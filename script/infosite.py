import asyncio
import os
from datetime import datetime
from playwright.async_api import Playwright, async_playwright, expect
from utils.logger import logger
from pathlib import Path

infosite_user = os.getenv("INFOSITE_USER", "E2SRobot")
infosite_password = os.getenv("INFOSITE_PASSWORD", "1111")


async def download_infosite_data(
    start_time: str,
    end_time: str,
) -> str:
    """下载infosite数据的核心函数"""
    logger.info(f"Starting infosite data download: {start_time} to {end_time}")

    if not infosite_user or not infosite_password:
        logger.error(
            "INFOSITE_USER and INFOSITE_PASSWORD environment variables are required"
        )
        raise ValueError("Missing infosite credentials")

    async def run(playwright: Playwright) -> str:
        try:
            logger.debug("Launching browser for infosite...")
            browser = await playwright.chromium.launch(headless=True)
            context = await browser.new_context(accept_downloads=True)
            page = await context.new_page()

            logger.debug("Navigating to infosite login page...")
            await page.goto("http://infosite.klt2u.oneback.net/info_backend/")
            await asyncio.sleep(10)
            logger.debug("Filling login credentials...")
            await page.get_by_role("textbox", name="Username").click()
            await page.get_by_role("textbox", name="Username").fill(infosite_user)
            await page.get_by_role("textbox", name="Password").click()
            await page.get_by_role("textbox", name="Password").fill(infosite_password)

            logger.debug("Logging in...")
            await page.get_by_role("button", name="Login ").click()
            await asyncio.sleep(3)

            logger.debug("Opening Event Schedule page...")
            async with page.expect_popup() as page1_info:
                await page.get_by_role("link", name="Event Schedule(Lite)").click()

            page1 = await page1_info.value
            await asyncio.sleep(2)

            logger.debug(f"Setting date range: {start_time} - {end_time}")
            await page1.locator("#gameDateFromTo").click()
            await asyncio.sleep(2)
            await page1.locator("#gameDateFromTo").fill(f"{start_time} - {end_time}")
            await page1.locator("#gameDateFromTo").press("Enter")
            await asyncio.sleep(2)

            logger.debug("Applying date filter...")
            await page1.get_by_role("button", name="Apply").click()
            await asyncio.sleep(3)

            logger.debug("Starting search...")
            await page1.get_by_role("button", name="Find").click()
            await asyncio.sleep(10)
            await page1.get_by_role("button", name="None").click()
            await asyncio.sleep(5)

            logger.debug("Selecting UEFA Champions League...")
            await page1.get_by_role(
                "checkbox", name="*UEFA CHAMPIONS LEAGUE", exact=True
            ).check()
            await page1.get_by_role("button", name="Query", exact=True).click()
            await asyncio.sleep(5)

            logger.debug("Selecting all matches for export...")
            await page1.locator("#exportCheckAll").check()
            await page1.get_by_role("button", name="Export match as file").click()
            await asyncio.sleep(2)

            logger.debug("Starting download...")
            async with page1.expect_download() as download_info:
                await page1.locator("#export-modal").get_by_text("Confirm").click()

            download = await download_info.value
            filename = download.suggested_filename
            # print("Suggested filename:", filename)
            # 确保输出目录存在
            # output_dir = Path("./data/infosite/")
            # output_dir.mkdir(parents=True, exist_ok=True)

            # 生成文件名
            # if not output_filename:
            #     output_filename = f"{start_time}-{end_time}.csv"
            await asyncio.sleep(5)
            download_path = f"./data/infosite/{filename}"
            await download.save_as(download_path)

            logger.info(f"Infosite data downloaded successfully: {download_path}")
            return str(download_path)

        except Exception as e:
            logger.error(
                f"Error during infosite download process: {str(e)}", exc_info=True
            )
            raise
        finally:
            if context:
                try:
                    await context.close()
                    logger.debug("Browser context closed")
                except Exception as e:
                    logger.warning(f"Error closing browser context: {e}")

            if browser:
                try:
                    await browser.close()
                    logger.debug("Browser closed")
                except Exception as e:
                    logger.warning(f"Error closing browser: {e}")

    try:
        async with async_playwright() as playwright:
            return await run(playwright)
    except Exception as e:
        logger.error(f"Failed to download infosite data: {str(e)}", exc_info=True)
        raise


async def download_infosite_with_filters(
    start_time: str,
    end_time: str,
    competitions: list = None,
) -> str:
    """带过滤条件的infosite数据下载"""
    if competitions is None:
        competitions = ["*UEFA CHAMPIONS LEAGUE"]

    logger.info(
        f"Starting filtered infosite download: {start_time} to {end_time}, competitions={competitions}"
    )

    if not infosite_user or not infosite_password:
        logger.error(
            "INFOSITE_USER and INFOSITE_PASSWORD environment variables are required"
        )
        raise ValueError("Missing infosite credentials")

    async def run(playwright: Playwright) -> str:
        browser = None
        context = None
        try:
            logger.debug("Launching browser for filtered infosite download...")
            browser = await playwright.chromium.launch(headless=True)
            context = await browser.new_context(accept_downloads=True)
            page = await context.new_page()

            # 登录流程
            logger.debug("Performing login...")
            await page.goto("http://infosite.klt2u.oneback.net/info_backend/")
            await asyncio.sleep(3)

            await page.get_by_role("textbox", name="Username").fill(infosite_user)
            await page.get_by_role("textbox", name="Password").fill(infosite_password)
            await page.get_by_role("button", name="Login ").click()
            await asyncio.sleep(3)

            # 打开Event Schedule页面
            logger.debug("Opening Event Schedule page...")
            async with page.expect_popup() as page1_info:
                await page.get_by_role("link", name="Event Schedule(Lite)").click()

            page1 = await page1_info.value
            await asyncio.sleep(2)

            # 设置日期范围
            logger.debug(f"Setting date range: {start_time} - {end_time}")
            await page1.locator("#gameDateFromTo").click()
            await asyncio.sleep(2)
            await page1.locator("#gameDateFromTo").fill(f"{start_time} - {end_time}")
            await page1.locator("#gameDateFromTo").press("Enter")
            await asyncio.sleep(2)
            await page1.get_by_role("button", name="Apply").click()
            await asyncio.sleep(3)

            # 搜索操作
            logger.debug("Performing search...")
            await page1.get_by_role("button", name="Find").click()
            await asyncio.sleep(5)
            await page1.get_by_role("button", name="None").click()
            await asyncio.sleep(3)

            # 选择比赛
            for competition in competitions:
                try:
                    logger.debug(f"Selecting competition: {competition}")
                    await page1.get_by_role(
                        "checkbox", name=competition, exact=True
                    ).check()
                    await asyncio.sleep(1)
                except Exception as e:
                    logger.warning(f"Could not select competition '{competition}': {e}")

            await page1.get_by_role("button", name="Query", exact=True).click()
            await asyncio.sleep(5)

            # 导出
            logger.debug("Exporting data...")
            await page1.locator("#exportCheckAll").check()
            await page1.get_by_role("button", name="Export match as file").click()
            await asyncio.sleep(2)

            async with page1.expect_download() as download_info:
                await page1.locator("#export-modal").get_by_text("Confirm").click()

            download = await download_info.value
            filename = download.suggested_filename

            download_path = f"./data/infosite/{filename}"
            await download.save_as(download_path)

            logger.info(
                f"Filtered infosite data downloaded successfully: {download_path}"
            )
            return str(download_path)

        except Exception as e:
            logger.error(
                f"Error in filtered infosite download: {str(e)}", exc_info=True
            )
            raise
        finally:
            if context:
                try:
                    await context.close()
                    logger.debug("Browser context closed")
                except Exception as e:
                    logger.warning(f"Error closing browser context: {e}")

            if browser:
                try:
                    await browser.close()
                    logger.debug("Browser closed")
                except Exception as e:
                    logger.warning(f"Error closing browser: {e}")

    try:
        async with async_playwright() as playwright:
            return await run(playwright)
    except Exception as e:
        logger.error(
            f"Failed to download filtered infosite data: {str(e)}", exc_info=True
        )
        raise
