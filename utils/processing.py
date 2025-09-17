import pandas as pd
import asyncio
from pathlib import Path
from utils.logger import logger


async def process_schedule(filename: str, start_date: str, end_date: str):
    """异步处理调度数据"""
    logger.info(f"Starting async processing of {filename}")

    try:
        # 异步读取CSV文件
        df = await asyncio.to_thread(pd.read_csv, f"./data/iptv/original/{filename}")
        logger.debug(f"Loaded {len(df)} records from {filename}")

        # 异步处理数据
        df = await asyncio.to_thread(_process_dataframe, df, start_date, end_date)

        # 确保输出目录存在
        output_dir = Path("./data/iptv/")
        output_dir.mkdir(parents=True, exist_ok=True)

        # 异步保存处理后的文件
        output_filename = f"./data/iptv/processed/processed_{filename}"
        await asyncio.to_thread(df.to_csv, output_filename, index=False)

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
    df["StartDate"] = pd.to_datetime(df["Start Date"])
    df = df[df["StartDate"] >= pd.to_datetime(f"{start_date} 12:00PM")]
    df = df[df["StartDate"] <= pd.to_datetime(f"{end_date} 11:59AM")]

    # 删除临时的StartDate列
    df.drop(columns=["StartDate"], inplace=True)

    return df


async def process_multiple_schedules(filenames: list, start_date: str, end_date: str):
    """并发处理多个调度文件"""
    logger.info(f"Starting concurrent processing of {len(filenames)} files")

    tasks = []
    for filename in filenames:
        task = process_schedule(filename, start_date, end_date)
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
