import pandas as pd
import asyncio
from pathlib import Path
from utils.logger import logger
import pandas as pd
import shutil
from datetime import datetime, timedelta, timezone


## IPTV 数据处理
async def processing_iptv(filename: str, start_date: str, end_date: str):
    """异步处理调度数据"""
    logger.info(f"Starting async processing of {filename}")

    try:
        # 异步读取CSV文件
        df = await asyncio.to_thread(
            pd.read_csv,
            f"./data/iptv/original/{filename}",
            engine="python",
            quotechar='"',
            on_bad_lines="skip",
            encoding="cp1258",
            encoding_errors="replace",
        )
        logger.debug(f"Loaded {len(df)} records from {filename}")

        # 异步处理数据
        df = await asyncio.to_thread(_process_dataframe, df, start_date, end_date)

        # 确保输出目录存在
        output_dir = Path("./data/iptv/")
        output_dir.mkdir(parents=True, exist_ok=True)

        # 异步保存处理后的文件
        output_filename = f"./data/iptv/processed/processed_{filename}"
        await asyncio.to_thread(
            df.to_csv, output_filename, index=False, encoding="utf-8-sig"
        )

        logger.info(f"Successfully processed {filename}, output: {output_filename}")
        return df

    except Exception as e:
        logger.error(f"Error processing schedule {filename}: {str(e)}", exc_info=True)
        raise


def _process_dataframe(
    df: pd.DataFrame, start_date: str, end_date: str
) -> pd.DataFrame:
    """同步的数据处理逻辑，在线程池中执行"""
    # 删除EventId列
    df.drop(columns=["EventId"], inplace=True)

    # 只保留足球数据
    df = df[df["Sport"] == "Soccer"]

    # 处理日期过滤
    df["StartDate"] = pd.to_datetime(df["Start Date"]) + pd.Timedelta(hours=7)
    df = df[
        df["StartDate"]
        >= pd.to_datetime(f"{start_date} 12:00PM", format="%d/%m/%Y %I:%M%p")
    ]
    df = df[
        df["StartDate"]
        <= pd.to_datetime(f"{end_date} 11:59AM", format="%d/%m/%Y %I:%M%p")
    ]
    df["Start Date"] = df["StartDate"].dt.strftime("%m/%d/%Y %I:%M %p")

    # 删除临时的StartDate列
    df.drop(columns=["StartDate"], inplace=True)
    df = df.drop_duplicates()
    return df


async def process_multiple_schedules(filenames: list, start_date: str, end_date: str):
    """并发处理多个调度文件"""
    logger.info(f"Starting concurrent processing of {len(filenames)} files")

    tasks = []
    for filename in filenames:
        task = processing_iptv(filename, start_date, end_date)
        tasks.append(task)

    try:
        results = await asyncio.gather(*tasks, return_exceptions=True)

        successful = 0
        failed = 0

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Failed to process {filenames[i]}: {result}")
                failed += 1
            else:
                successful += 1

        logger.info(f"Processing completed: {successful} successful, {failed} failed")
        return results

    except Exception as e:
        logger.error(f"Error in concurrent processing: {str(e)}", exc_info=True)
        raise


async def processing_iptv_json(df: pd.DataFrame, start_date: str, end_date: str):
    """异步处理调度数据"""
    df = df.rename(
        columns={
            "Competition": "leagueName",
            "Home Team": "homeTeamName",
            "Away Team": "awayTeamName",
            "Channel": "channel",
        }
    )
    df["StartDate"] = pd.to_datetime(df["Start Date"]) + pd.Timedelta(hours=7)
    df = df[
        df["StartDate"]
        >= pd.to_datetime(f"{start_date} 12:00PM", format="%Y-%m-%d %I:%M%p")
    ]
    df = df[
        df["StartDate"]
        <= pd.to_datetime(f"{end_date} 11:59AM", format="%Y-%m-%d  %I:%M%p")
    ]
    df.drop(columns=["StartDate"], inplace=True)
    df = df.drop_duplicates(["homeTeamName", "awayTeamName", "Start Date"])
    df["kickoffTime"] = pd.to_datetime(df["Start Date"], errors="coerce").dt.strftime(
        "%Y-%m-%dT%H:%M:%S.000Z"
    )
    df["alive"] = df["Watch"].apply(lambda x: str(x).strip().lower() == "verified")
    now = datetime.now()
    df["status"] = pd.to_datetime(df["Start Date"], errors="coerce").apply(
        lambda t: timedelta(0) <= (now - t) < timedelta(hours=2)
    )
    df = df.drop(columns=["Start Date", "Watch", "Information", "Sport"])
    return df.to_dict(orient="records")


## MERGE IPTV and InfoSite into  formula


# import pandas as pd
# import shutil

# filename = "schedule11"
# iptv = pd.read_csv("./data/iptv/processed/processed_schedule11.csv")
# infosite = pd.read_csv("./data/infosite/infosite.csv")
# shutil.copy("./data/formula.xlsx", f"./data/merge/{filename}.xlsx")

# # 寫入 Excel，不同的 sheet
# with pd.ExcelWriter(
#     f"./data/merge/{filename}.xlsx",
#     engine="openpyxl",
#     mode="a",
#     if_sheet_exists="replace",
# ) as writer:
#     iptv.to_excel(writer, sheet_name="IPTV", index=False)
#     infosite.to_excel(writer, sheet_name="infosite1", index=False)


async def merge_data_to_excel(iptv_path: str, infosite_path: str, output_filename: str):
    """异步合并IPTV和infosite数据到Excel文件"""
    logger.info(
        f"Starting merge data to Excel: IPTV={iptv_path}, infosite={infosite_path}"
    )

    try:
        # 异步读取CSV文件
        # iptv_path = f"./data/iptv/processed/processed_{filename}"
        # infosite_path = f"./data/infosite/{infosite_filename}"
        formula_path = "./data/formula.xlsx"

        logger.debug(f"Reading IPTV data from {iptv_path}")
        iptv = await asyncio.to_thread(pd.read_csv, iptv_path)

        logger.debug(f"Reading infosite data from {infosite_path}")
        infosite = await asyncio.to_thread(pd.read_excel, infosite_path)

        # 确保输出目录存在
        merge_dir = Path("./data/merge/")
        merge_dir.mkdir(parents=True, exist_ok=True)

        # # 生成输出文件名
        # if not output_filename:
        #     base_filename = filename.replace(".csv", "")
        #     output_filename = f"{base_filename}_merged.xlsx"

        output_path = f"./data/merge/{output_filename}.xlsx"

        # 异步复制模板文件
        logger.debug(f"Copying formula template to {output_path}")
        await asyncio.to_thread(shutil.copy, formula_path, output_path)

        # 异步写入Excel文件
        logger.debug(f"Writing data to Excel sheets")
        await asyncio.to_thread(_write_excel_sheets, output_path, iptv, infosite)

        logger.info(f"Successfully merged data to Excel: {output_path}")

        return {
            "success": True,
            "output_path": output_path,
            "iptv_source": iptv_path,
            "infosite_source": infosite_path,
        }

    except FileNotFoundError as e:
        logger.error(f"File not found: {str(e)}")
        raise ValueError(f"Required file not found: {str(e)}")
    except Exception as e:
        logger.error(f"Error merging data to Excel: {str(e)}", exc_info=True)
        raise


def _write_excel_sheets(output_path: str, iptv: pd.DataFrame, infosite: pd.DataFrame):
    """同步的Excel写入逻辑，在线程池中执行"""
    with pd.ExcelWriter(
        output_path,
        engine="openpyxl",
        mode="a",
        if_sheet_exists="replace",
    ) as writer:
        iptv.to_excel(writer, sheet_name="IPTV", index=False)
        infosite.to_excel(writer, sheet_name="infosite1", index=False)


async def process_and_merge_schedule(
    start_date: str, end_date: str, filename: str, infosite_filename: str
):
    """完整的处理流程：处理调度数据并合并到Excel"""
    logger.info(
        f"Starting complete processing and merge for IPTV={filename}, infosite={infosite_filename}"
    )

    try:
        # 先处理调度数据
        logger.info("Step 1: Processing schedule data")
        df = await processing_iptv(filename, start_date, end_date)

        # 再合并到Excel
        logger.info("Step 2: Merging data to Excel")
        result = await merge_data_to_excel(filename, infosite_filename)

        logger.info(f"Complete processing finished for {filename}")

        return {
            "success": True,
            "processed_records": len(df),
            "excel_path": result["output_path"],
            "iptv_records": result["iptv_records"],
            "infosite_records": result["infosite_records"],
        }

    except Exception as e:
        logger.error(f"Error in complete processing: {str(e)}", exc_info=True)
        raise


# 批量处理多个文件
async def batch_merge_to_excel(merge_configs: list):
    """批量异步合并多个文件到Excel

    Args:
        merge_configs: 包含 {'filename': str, 'infosite_filename': str} 的配置列表
    """
    logger.info(f"Starting batch merge for {len(merge_configs)} configurations")

    tasks = []
    for config in merge_configs:
        task = merge_data_to_excel(
            config["filename"],
            config["infosite_filename"],
            config.get("output_filename"),
        )
        tasks.append(task)

    try:
        results = await asyncio.gather(*tasks, return_exceptions=True)

        successful = 0
        failed = 0

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Failed to merge config {merge_configs[i]}: {result}")
                failed += 1
            else:
                successful += 1

        logger.info(f"Batch merge completed: {successful} successful, {failed} failed")
        return results

    except Exception as e:
        logger.error(f"Error in batch merge: {str(e)}", exc_info=True)
        raise
