import asyncio
import re
from playwright.async_api import Playwright, async_playwright, expect
import os
from datetime import datetime

email = os.getenv("EMAIL")
password = os.getenv("PASSWORD")


def format_date_for_button(date_str: str) -> str:
    """
    将 YYYY/MM/DD 格式的日期转换为网页按钮需要的格式
    例如: "2025/09/09" -> "Choose Monday, September 9,"
    """
    date_obj = datetime.strptime(date_str, "%Y/%m/%d")
    weekday = date_obj.strftime("%A")  # Monday, Tuesday, etc.
    month = date_obj.strftime("%B")  # January, February, etc.
    day = date_obj.day  # 9 (不带前导零)

    return f"Choose {weekday}, {month} {day},"


async def run(playwright: Playwright, start_date: str, end_date: str) -> None:
    browser = await playwright.chromium.launch(headless=True)  # 改回无头模Ｔ
    context = await browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )
    page = await context.new_page()

    # 设置更长的超时时间
    page.set_default_timeout(60000)  # 60秒

    try:
        print("正在访问网站...")
        await page.goto("https://inplayip.tv/schedule", wait_until="networkidle")

        print("正在填写邮箱...")
        await page.get_by_role("textbox", name="Email").click()
        await page.get_by_role("textbox", name="Email").fill(email)

        print("正在填写密码...")
        await page.get_by_role("textbox", name="Password").click()
        await page.get_by_role("textbox", name="Password").fill(password)

        print("正在登录...")
        await page.get_by_role("button", name="Sign in", exact=True).click()
        await page.wait_for_timeout(3000)  # 增加等待时间

        print("正在选择日期范围...")
        await page.get_by_role("button", name="").nth(1).click()
        await page.get_by_text("Select period").click()
        await page.get_by_role("textbox", name="Start Date").click()

        print(f"选择开始日期: {start_date}")
        await page.get_by_role("button", name=start_date).click()

        print(f"选择结束日期: {end_date}")
        await page.get_by_role("button", name=end_date).click()

        print("正在下载CSV文件...")
        async with page.expect_download() as download_info:
            await page.get_by_text("Download CSV").click()
        download = await download_info.value
        download.save_as("schedule.csv")
        print("CSV文件已保存为 schedule.csv")

    except Exception as e:
        print(f"发生错误: {e}")
        # 截图以便调试
        await page.screenshot(path="error_screenshot.png")
        raise
    finally:
        await context.close()
        await browser.close()


async def main() -> None:
    # 现在可以使用简单的日期格式
    start_date = format_date_for_button("2025/09/16")
    end_date = format_date_for_button("2025/09/17")

    print(f"开始日期格式: {start_date}")
    print(f"结束日期格式: {end_date}")

    async with async_playwright() as playwright:
        await run(playwright, start_date, end_date)


asyncio.run(main())
