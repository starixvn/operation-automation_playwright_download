import asyncio
import re
from playwright.async_api import Playwright, async_playwright, expect
import os

email = os.getenv("EMAIL")
password = os.getenv("PASSWORD")


# async def run(playwright: Playwright) -> None:
#     browser = await playwright.chromium.launch(headless=True)
#     context = await browser.new_context()
#     page = await context.new_page()
#     await page.goto("https://inplayip.tv/schedule")
#     await page.get_by_role("textbox", name="Email").click()
#     await page.get_by_role("textbox", name="Email").fill(email)
#     await page.get_by_role("textbox", name="Password").click()
#     await page.get_by_role("textbox", name="Password").fill(password)
#     await page.get_by_role("button", name="Sign in", exact=True).click()
#     await page.wait_for_timeout(2000)
#     await page.get_by_role("button", name="").nth(1).click()
#     await page.get_by_text("Select period").click()
#     await page.get_by_role("textbox", name="Start Date").click()
#     await page.get_by_role("button", name="Choose Tuesday, September 9,").click()
#     await page.get_by_role("button", name="Choose Wednesday, September 17,").click()
#     async with page.expect_download() as download_info:
#         await page.get_by_text("Download CSV").click()
#     download = await download_info.value
#     await download.save_as("schedule.csv")
#     # ---------------------
#     await context.close()
#     await browser.close()
async def run(playwright: Playwright) -> None:
    browser = await playwright.chromium.launch(headless=True)
    context = await browser.new_context()
    page = await context.new_page()
    response = await page.goto("https://inplayip.tv/schedule")
    await page.get_by_role("textbox", name="Email").click()
    await page.get_by_role("textbox", name="Email").fill("bownb@enpine.com")
    await page.get_by_role("textbox", name="Password").click()
    await page.get_by_role("textbox", name="Password").fill("!QAZxdr5432")
    await page.get_by_role("button", name="Sign in", exact=True).click()
    await page.wait_for_timeout(2000)
    await page.get_by_role("button", name="").nth(1).click()
    await page.get_by_text("Select period").click()
    await page.get_by_role("textbox", name="Start Date").click()
    await page.get_by_role("button", name="Choose Tuesday, September 9,").click()
    await page.get_by_role("button", name="Choose Wednesday, September 17,").click()
    async with page.expect_download() as download_info:
        await page.get_by_text("Download CSV").click()
    download = await download_info.value
    await download.save_as("schedule.csv")
    # ---------------------
    await context.close()
    await browser.close()


async def main() -> None:
    async with async_playwright() as playwright:
        await run(playwright)


asyncio.run(main())
