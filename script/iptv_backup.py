import asyncio
import re
from playwright.async_api import Playwright, async_playwright, expect
import os
from utils.logger import logger

email = os.environ.get("EMAIL")
password = os.environ.get("PASSWORD")


async def download_schedule(
    start_date: str, end_date: str, filename: str = "schedule.csv"
):
    """下载调度数据的核心函数"""
    logger.info(
        f"Starting download_schedule: {start_date} to {end_date}, file: {filename}"
    )

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

            logger.info(f"Download completed successfully: {filename}")

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


# start_date = "16/09/2025"
# end_date = "17/09/2025"
# filename = "schedule.csv"

# asyncio.run(download_schedule(start_date, end_date, filename))
