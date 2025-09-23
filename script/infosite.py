import asyncio
import os
from playwright.async_api import Playwright, async_playwright, expect
from utils.logger import logger
from pathlib import Path
import pandas as pd
import math
import time
import json

infosite_user = os.getenv("INFOSITE_USER")
infosite_password = os.getenv("INFOSITE_PASSWORD")
features = json.load(open("config/export.json"))


async def get_league_names(
    start_time: str,
    end_time: str,
    leagues_groups: list = None,
) -> list:
    logger.info(f"Starting infosite check league: {start_time} to {end_time}")

    async def run(playwright: Playwright) -> list:
        browser = None
        context = None
        try:
            logger.debug("Launching browser for infosite check league...")
            browser = await playwright.chromium.launch(headless=False)
            context = await browser.new_context(accept_downloads=True)
            page = await context.new_page()

            logger.debug("Navigating to infosite login page...")
            await page.goto("http://infosite.klt2p.oneback.net/info_backend/")
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
            await page1.get_by_role("button", name="27 selected").click()
            await page1.get_by_role("checkbox", name="All", exact=True).check()
            for leagues_group in leagues_groups:
                await page1.get_by_role(
                    "checkbox", name=leagues_group, exact=True
                ).check()
            await page1.get_by_role("button", name="Find").click()
            await asyncio.sleep(10)
            await page1.get_by_role("button", name="None").click()
            checkboxes = page1.locator(
                "#leagueId_luluselect_modal input[type=checkbox]"
            )
            count = await checkboxes.count()
            leagues = []
            for i in range(count):
                # 找出對應的 label
                label = await checkboxes.nth(i).evaluate(
                    "el => el.parentElement.innerText"
                )
                leagues.append(label)
            print(leagues)
            return leagues
        except Exception as e:
            logger.error(f"Error during infosite check league: {str(e)}", exc_info=True)
            raise
        finally:
            if context:
                await context.close()
            if browser:
                await browser.close()

    try:
        async with async_playwright() as playwright:
            return await run(playwright)
    except Exception as e:
        logger.error(f"Failed to download infosite data: {str(e)}", exc_info=True)
        raise
        # await page1.get_by_role("button", name="Select All").click()


async def download_infosite_data(
    start_time: str,
    end_time: str,
    filename: str = None,
    leagues: list = None,
    league_groups: list = None,
    sports: list = None,
    save_features: list = None,
    batch_size: int = 5,
) -> str:
    """下载infosite数据的核心函数"""
    logger.info(f"Starting infosite data download: {start_time} to {end_time}")

    if not infosite_user or not infosite_password:
        logger.error(
            "INFOSITE_USER and INFOSITE_PASSWORD environment variables are required"
        )
        raise ValueError("Missing infosite credentials")
    output_dir = Path("./data/infosite")
    tmp_dir = output_dir / "tmp"
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    async def run(playwright: Playwright) -> str:
        try:
            logger.debug("Launching browser for infosite...")
            browser = await playwright.chromium.launch(headless=False)
            context = await browser.new_context(accept_downloads=True)
            page = await context.new_page()

            logger.debug("Navigating to infosite login page...")
            await page.goto("http://infosite.klt2p.oneback.net/info_backend/")
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
            await page1.get_by_role("button", name="27 selected").click()
            await page1.get_by_role("checkbox", name="All", exact=True).check()
            for leagues_group in league_groups:
                await page1.get_by_role(
                    "checkbox", name=leagues_group, exact=True
                ).check()
            if sports:
                await page1.get_by_role("button", name="Soccer", exact=True).click()
                await page1.get_by_text("Clear", exact=True).click()
                for sport in sports:
                    await page1.get_by_role("checkbox", name=sport, exact=True).check()
            # await asyncio.sleep(10)
            # btn = await page1.get_by_role("button", name="None").click()
            # count = await checkboxes.count()
            num_batches = math.ceil(len(leagues) / batch_size)
            tmp_files = []
            for batch_index in range(num_batches):
                exec_start_time = time.time()
                logger.info(f"Downloading batch {batch_index+1} of {num_batches}")
                await asyncio.sleep(5)
                try:
                    await page1.get_by_role("button", name="None").click()
                except Exception:
                    await page1.get_by_role("button", name="Selected:").click()
                await asyncio.sleep(3)
                await page1.get_by_role("button", name="Clear All").click()
                start_index = batch_index * batch_size
                end_index = min(start_index + batch_size, len(leagues))
                current_batch = leagues[start_index:end_index]
                for league in current_batch:
                    checkbox = page1.get_by_role("checkbox", name=league, exact=True)
                    await checkbox.wait_for(state="visible", timeout=120000)
                    await checkbox.check()
                await page1.get_by_role("button", name="Query", exact=True).click()

                try:
                    await page1.locator("div.blockUI.blockOverlay").wait_for(
                        state="detached", timeout=120000
                    )
                except:
                    logger.warning("Overlay still present, force continuing...")

                logger.debug("Selecting all matches for export...")
                await page1.locator("#exportCheckAll").check()
                await page1.get_by_role("button", name="Export match as file").click()
                await asyncio.sleep(10)

                logger.debug("Starting download...")
                await page1.locator("#expUncheckAll").click()
                if save_features:
                    if "all" in save_features:
                        await page1.locator("#expCheckAll").click()
                    else:
                        for save_feature in save_features:
                            save_feature = features[save_feature]
                            await page1.locator(save_feature).check()
                async with page1.expect_download() as download_info:
                    await page1.locator("#export-modal").get_by_text("Confirm").click()

                download = await download_info.value
                batch_file = tmp_dir / f"{filename}_batch{batch_index+1}.xls"
                await download.save_as(str(batch_file))
                logger.info(
                    f"Saved batch file: {batch_file} in {time.time() - exec_start_time:.2f} seconds"
                )
                tmp_files.append(batch_file)
            dfs = [pd.read_excel(f) for f in tmp_files]
            merged_df = pd.concat(dfs, ignore_index=True)
            final_path = output_dir / f"{filename}.xls"
            merged_df.to_excel(final_path, index=False)
            for tmp_file in tmp_files:
                try:
                    os.remove(tmp_file)
                except Exception:
                    pass
            # filename = download.suggested_filename
            # print("Suggested filename:", filename)
            # 确保输出目录存在
            # output_dir = Path("./data/infosite/")
            # output_dir.mkdir(parents=True, exist_ok=True)

            # 生成文件名
            # if not output_filename:
            #     output_filename = f"{start_time}-{end_time}.csv"
            # await asyncio.sleep(5)
            # download_path = f"./data/infosite/{filename}"
            # await download.save_as(download_path)

            logger.info(f"Infosite data downloaded successfully: {final_path}")
            return str(final_path)
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
