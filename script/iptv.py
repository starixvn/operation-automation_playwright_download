import re
from playwright.sync_api import Page, expect
import os

email = os.getenv("EMAIL")
password = os.getenv("PASSWORD")


def test_example(page: Page) -> None:
    page.goto("https://inplayip.tv/login?redirectUrl=/schedule")
    page.get_by_role("textbox", name="Email").click()
    page.get_by_role("textbox", name="Email").fill(email)
    page.get_by_role("textbox", name="Password").click()
    page.get_by_role("textbox", name="Password").fill(password)
    page.get_by_role("button", name="Sign in", exact=True).click()
    page.get_by_role("button", name="").nth(1).click()
    page.get_by_role("button", name="").nth(1).click()
    page.get_by_text("Select period").click()
    page.get_by_role("textbox", name="Start Date").click()
    page.get_by_role("button", name="Choose Tuesday, September 9,").click()
    page.get_by_role(
        "button",
        name="Choose Wednesday, September 17, 2025 as your check-out date. It's available.",
    ).click()
    with page.expect_download() as download_info:
        page.get_by_text("Download CSV").click()
    download = download_info.value
    download.save_as("schedule.csv")
