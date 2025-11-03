import asyncio
import re
from playwright.async_api import Playwright, async_playwright, expect
import os
from utils.logger import logger
import pandas as pd
import io

email = os.environ.get("EMAIL")
password = os.environ.get("PASSWORD")


async def download_schedule_backup(start_date: str, end_date: str):
    """下载调度数据的核心函数"""
    logger.info(f"Starting download_schedule: {start_date} to {end_date}")

    async def run(playwright: Playwright) -> None:
        # browser = None
        # context = None
        try:
            logger.debug("Launching browser...")
            browser = await playwright.chromium.launch(headless=True)
            context = await browser.new_context()
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
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        print("🔐 Navigating to login page...")
        await page.goto("https://inplayip.tv/login?redirectUrl=/schedule")

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


async def download_schedule(
    start_date: str, end_date: str, token: str, device_uuid: str
):

    async def run(playwright: Playwright):
        logger.info(f"Downloading IPTV schedule: {start_date} to {end_date}")
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        url = "https://api.inplayip.tv/api/schedule/document/csv"
        params = {
            "startDate": start_date,
            "endDate": end_date,
            "timezoneOffset": "-480",
        }

        headers = {
            "Authorization": f"Bearer {token}",
            "DeviceUUID": device_uuid,
            "Origin": "https://inplayip.tv",
            "Referer": "https://inplayip.tv/",
        }

        # ✅ 呼叫 API 下載 CSV
        response = await page.request.get(url, headers=headers, params=params)
        if response.status != 200:
            raise RuntimeError(f"Download failed: HTTP {response.status}")

        csv_bytes = await response.body()

        # ✅ 解析 DataFrame
        df = pd.read_csv(io.BytesIO(csv_bytes))
        logger.info(f"✅ IPTV CSV loaded, rows={len(df)}")

        # ✅ 篩選運動類型
        df = df[df["Sport"] == "Soccer"]

        await browser.close()
        return df

    # ✅ 必須 return！
    async with async_playwright() as p:
        return await run(p)
