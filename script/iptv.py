from playwright.async_api import Playwright, async_playwright, expect
from config.env_config import config
from utils.logger import logger
import pandas as pd
import io
import json

# Load configuration
email = config.get("EMAIL")
password = config.get("PASSWORD")
headless = config.get_bool("HEADLESS", False)

# Proxy configuration
http_proxy = config.get("HTTP_PROXY")
https_proxy = config.get("HTTPS_PROXY")


async def download_schedule_backup(start_date: str, end_date: str):
    """下载调度数据的核心函数"""
    logger.info(f"Starting download_schedule: {start_date} to {end_date}")

    async def run(playwright: Playwright) -> None:
        # browser = None
        # context = None
        try:
            logger.debug("Launching browser...")

            # Configure proxy if available
            launch_options = {"headless": headless}
            context_options = {}

            if http_proxy or https_proxy:
                proxy_config = {}
                if http_proxy:
                    proxy_config["server"] = http_proxy
                    logger.info(f"Using HTTP proxy: {http_proxy}")
                elif https_proxy:
                    proxy_config["server"] = https_proxy
                    logger.info(f"Using HTTPS proxy: {https_proxy}")

                context_options["proxy"] = proxy_config

            browser = await playwright.chromium.launch(**launch_options)
            context = await browser.new_context(**context_options)
            page = await context.new_page()

            logger.debug("Navigating to login page...")
            await page.goto("https://inplayip.tv/login?redirectUrl=/schedule")

            logger.debug("Filling login credentials...")
            await page.get_by_role("textbox", name="Email").click()
            await page.get_by_role("textbox", name="Email").fill(email)
            await page.get_by_role("textbox", name="Password").click()
            await page.get_by_role("textbox", name="Password").fill(password)

            logger.debug("Signing in...")
            await page.get_by_role("button", name="Sign in", exact=True).click()

            await page.get_by_role("button", name="").nth(1).click()
            await page.get_by_text("Select period").click()
            await page.get_by_role("textbox", name="Start Date").click()
            await page.get_by_role("textbox", name="Start Date").fill(start_date)
            await page.get_by_role("button", name="").nth(1).click()
            await page.get_by_role("button", name="").nth(1).click()
            await page.get_by_role("textbox", name="End Date").fill(end_date)

            logger.debug("Starting download...")
            async with page.expect_download() as download_info:
                await page.get_by_text("Download CSV").click()
            download = await download_info.value
            await download.save_as("./data/iptv/original/" + filename)
            if not download_bytes:
                raise ValueError(
                    "Empty download content — file may be corrupted or not a CSV."
                )
            try:
                df = pd.read_csv(io.BytesIO(download_bytes), encoding="utf-8")
                print(df.head())
            except UnicodeDecodeError:
                logger.warning(
                    "Encoding issue detected, retrying with fallback encoding..."
                )
                df = pd.read_csv(io.BytesIO(download_bytes), encoding="latin1")
            except pd.errors.ParserError:
                raise ValueError("Downloaded file is not a valid CSV format.")

            # logger.info(f"Download completed successfully: {filename}")

        except Exception as e:
            logger.error(f"Error during download process: {str(e)}", exc_info=True)
            raise
        finally:
            if context:
                await context.close()
                logger.debug("Browser context closed")
            if browser:
                await browser.close()
                logger.debug("Browser closed")

    async with async_playwright() as playwright:
        await run(playwright)


# start_date = "16/10/2025"
# end_date = "17/10/2025"
# filename = "schedule.csv"

# asyncio.run(download_schedule(start_date, end_date, filename))


async def login_and_get_token():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)

        context_options = {}
        if http_proxy or https_proxy:
            proxy_config = {}
            if http_proxy:
                proxy_config["server"] = http_proxy
                logger.info(f"Using HTTP proxy: {http_proxy}")
            elif https_proxy:
                proxy_config["server"] = https_proxy
                logger.info(f"Using HTTPS proxy: {https_proxy}")
            context_options["proxy"] = proxy_config

        context = await browser.new_context(**context_options)
        page = await context.new_page()

        print("🔐 Navigating to login page...")
        await page.goto(
            "https://inplayip.tv/login?redirectUrl=/schedule", timeout=120000
        )

        # 填寫登入表單
        await page.get_by_role("textbox", name="Email").fill(email)
        await page.get_by_role("textbox", name="Password").fill(password)
        await page.get_by_role("button", name="Sign in", exact=True).click()

        # 等待登入完成（可以依實際情況調整）
        await page.wait_for_load_state("networkidle")

        # 1️⃣ 從 localStorage 抓 access_token
        token = await page.evaluate(
            "localStorage.getItem('accessToken')"
        ) or await page.evaluate("localStorage.getItem('token')")

        # 2️⃣ 抓 deviceUuid
        device_uuid = await page.evaluate("localStorage.getItem('deviceUuid')")

        if not token or not device_uuid:
            print("⚠️ 沒抓到 token 或 deviceUuid，嘗試列出所有 localStorage 內容：")
            items = await page.evaluate("Object.entries(localStorage)")
            for k, v in items:
                print(f"{k}: {v}")

        print(f"✅ Token: {token[:50]}...")
        print(f"✅ DeviceUUID: {device_uuid}")

        await browser.close()
        return token, device_uuid


async def download_schedule(date: str, token: str, device_uuid: str):

    async with async_playwright() as p:
        print(f"[INFO] Downloading IPTV schedule table: {date}")

        browser = await p.chromium.launch(headless=True)
        context_options = {}
        if http_proxy or https_proxy:
            proxy_config = {}
            if http_proxy:
                proxy_config["server"] = http_proxy
                logger.info(f"Using HTTP proxy: {http_proxy}")
            elif https_proxy:
                proxy_config["server"] = https_proxy
                logger.info(f"Using HTTPS proxy: {https_proxy}")
            context_options["proxy"] = proxy_config
        context = await browser.new_context(**context_options)
        page = await context.new_page()

        url = "https://api.inplayip.tv/api/schedule/table"

        # POST Payload（由你提供）
        payload = {
            "filters": {
                "searchDate": date,  # ← 你傳入的 date
                "searchWord": "",
                "onlyNew": False,
                "showVOD": False,
                "showLive": False,
                "sportsCriteria": ["Soccer"],
                "countriesCriteria": [],
                "servicesCriteria": [],
            },
            "timezoneOffset": 0,  # ← 你要求固定 0
        }

        # 正確的瀏覽器 Header（避免 401 / 403）
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/142.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "Content-Type": "application/json; charset=UTF-8",
            "Origin": "https://inplayip.tv",
            "Referer": "https://inplayip.tv/",
            "DeviceUUID": device_uuid,
            "Authorization": f"Bearer {token}",
        }

        # ⚠️ 重點：Playwright 舊版不支援 json=payload
        # 所以用 data=json.dumps(payload)（最保險，100% work）
        response = await page.request.post(
            url, headers=headers, data=json.dumps(payload)
        )

        if response.status != 200:
            raise RuntimeError(f"[ERROR] HTTP {response.status}")

        data = await response.json()
        data = pd.DataFrame(data)
        columns = [
            "eventId",
            "region",
            "sport",
            "competition",
            "competitor1",
            "competitor2",
            "startTime",
            "endTime",
            "channel",
            "cancelled",
            "verified",
        ]
        data = data[columns]
        print(data["sport"].unique())
        # print(f"[INFO] Loaded schedule table, items={len(data.get('items', []))}")

        await browser.close()
        return data


# import requests
# import pandas as pd

# token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy9lbWFpbGFkZHJlc3MiOiJib3duYkBlbnBpbmUuY29tIiwiaHR0cDovL3NjaGVtYXMubWljcm9zb2Z0LmNvbS93cy8yMDA4LzA2L2lkZW50aXR5L2NsYWltcy9yb2xlIjoiQ2xpZW50IEFkbWluIiwiaWQiOiIyNzEwIiwiZ3JvdXBJZCI6Ijk1IiwicmVzdHJpY3Rpb25JZCI6IjQ3MCIsImdyb3VwTmFtZSI6IklCQyIsImRldmljZVVpZCI6IjI5M2JiZWU3ZGM3MmMyZGJiYjhhNTVkYTk1MjRkNWUyIiwibmJmIjoxNzYzNzAxMTY1LCJleHAiOjE3NjM3ODc1NjUsImlzcyI6IkluUGxheSBBUEkiLCJhdWQiOiJJblBsYXkgVUkifQ.Ny1dfSM7fsOcxGBUlzoqTvokVbTQR7wzd6aPZZwIOvM"
# device_uuid = "6836d8999e9c211e04d50a14d11bdde3"
# url = "https://api.inplayip.tv/api/schedule/table"

# headers = {
#     "Accept": "application/json, text/plain, */*",
#     "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
#     "Content-Type": "application/json; charset=UTF-8",
#     "Origin": "https://inplayip.tv",
#     "Referer": "https://inplayip.tv/",
#     "Sec-Fetch-Site": "same-site",
#     "Sec-Fetch-Mode": "cors",
#     "DeviceUUID": "6836d8999e9c211e04d50a14d11bdde3",
#     "Authorization": f"Bearer {token}",
# }

# # 這裡是你要 POST 的 body（format 依 API 要求調整）
# payload = {
#     "filters": {
#         "searchDate": "2025-11-21T04:59:26.517Z",
#         "searchWord": "",
#         "onlyNew": False,
#         "showVOD": False,
#         "showLive": False,
#         "sportsCriteria": ["Soccer"],
#         "countriesCriteria": [],
#         "servicesCriteria": [],
#     },
#     "timezoneOffset": 0,
# }

# response = requests.post(url, headers=headers, json=payload)

# print("Status:", response.status_code)
# print(response.text)

# data = response.json()
# data2 = pd.DataFrame(data)

# columns = [
#     "eventId",
#     "region",
#     "sport",
#     "competition",
#     "competitor1",
#     "competitor2",
#     "startTime",
#     "endTime",
#     "cancelled",
#     "verified",
# ]
# data3 = data2[columns]

# print(data2)


# data3.to_csv("iptv_schedule_table.csv", index=False)
