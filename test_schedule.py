import asyncio
import re
from playwright.async_api import Playwright, async_playwright, expect


async def run(playwright: Playwright) -> None:
    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context()
    page = await context.new_page()
    await page.goto("http://infosite.klt2u.oneback.net/info_backend/")
    await page.get_by_role("textbox", name="Username").click()
    await page.get_by_role("textbox", name="Username").fill("E2SRobot")
    await page.get_by_role("textbox", name="Username").press("Tab")
    await page.get_by_role("textbox", name="Password").fill("1111")
    await page.get_by_role("button", name="Login ").click()
    async with page.expect_popup() as page1_info:
        await page.get_by_role("link", name="Event Schedule(Lite)").click()
    page1 = await page1_info.value
    await page1.locator("#gameDateFromTo").click()
    await page1.get_by_role("cell", name="23").nth(1).click()
    await page1.get_by_role("cell", name="24").first.click()
    await page1.get_by_role("button", name="Apply").click()
    await page1.get_by_role("button", name="28 selected").click()
    await page1.get_by_role("checkbox", name="All", exact=True).check()
    await page1.get_by_role("checkbox", name="Soccerway", exact=True).check()
    await page1.get_by_role("button", name="Soccer", exact=True).click()
    await page1.get_by_text("Clear", exact=True).click()
    await page1.get_by_role("checkbox", name="Soccer", exact=True).check()
    await page1.get_by_role("button", name="Find").click()

    # ---------------------
    await context.close()
    await browser.close()


async def main() -> None:
    async with async_playwright() as playwright:
        await run(playwright)


asyncio.run(main())
