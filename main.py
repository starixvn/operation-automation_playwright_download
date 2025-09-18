from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from datetime import datetime, date
from script.iptv import download_schedule  # 假设你有这个函数
from script.infosite import download_infosite_data, download_infosite_with_filters
from schema.schema import (
    IptvRequest,
    IptvResponse,
    InfositeRequest,
    InfositeResponse,
    MergeRequest,
)
from utils.logger import logger
from utils.processing import (
    processing_iptv,
    merge_data_to_excel,
)
from pathlib import Path
import asyncio
import shutil

app = FastAPI(title="IPTV Schedule API", version="1.0.0")


@app.on_event("startup")
async def startup_event():
    logger.info("IPTV Schedule API starting up...")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("IPTV Schedule API shutting down...")


@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "IPTV Schedule API"}


@app.post("/download-iptv", response_model=IptvResponse)
async def download_iptv_endpoint(request: IptvRequest):
    logger.info(
        f"Download schedule request received: start_date={request.start_date}, end_date={request.end_date}"
    )

    try:
        # 验证日期格式
        start_date = request.start_date
        end_date = request.end_date

        logger.debug(f"Processing dates: {start_date} to {end_date}")

        # 生成文件名（如果没有提供）
        if not request.filename:
            filename = f"schedule_{start_date.replace('/', '')}_to_{end_date.replace('/', '')}.csv"
        else:
            filename = request.filename

        logger.info(f"Starting download for file: {filename}")

        # 调用下载函数
        await download_schedule(start_date, end_date, filename)
        await processing_iptv(filename, start_date, end_date)

        logger.info(f"Schedule downloaded successfully: {filename}")

        return IptvResponse(
            success=True,
            message="IPTV downloaded successfully",
            filename=f"./data/iptv/processed/{filename}",
            download_time=datetime.now(),
        )
    except Exception as e:
        logger.error(f"Error downloading schedule: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/merge-to-excel")
async def merge_to_excel_endpoint(request: MergeRequest):
    """将处理后的数据合并到Excel文件"""
    logger.info(
        f"Merge to Excel request: IPTV={request.iptv_path}, infosite={request.infosite_path}"
    )

    try:
        result = await merge_data_to_excel(
            request.iptv_path, request.infosite_path, request.output_filename
        )

        return {
            "success": True,
            "message": "Data merged to Excel successfully",
            "iptv_filename": request.iptv_path,
            "infosite_filename": request.infosite_path,
            "output_path": result["output_path"],
            "merge_time": datetime.now(),
        }

    except Exception as e:
        logger.error(f"Error merging to Excel: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/download-infosite", response_model=InfositeResponse)
async def download_infosite_endpoint(request: InfositeRequest):
    """下载infosite数据"""
    logger.info(f"Infosite download request: {request}")

    try:
        if request.competitions:
            file_path = await download_infosite_with_filters(
                request.start_time,
                request.end_time,
                request.competitions,
            )
        else:
            file_path = await download_infosite_data(
                request.start_time, request.end_time
            )

        return InfositeResponse(
            success=True,
            message="Infosite data downloaded successfully",
            filename=Path(file_path).name,
            file_path=file_path,
            download_time=datetime.now(),
        )

    except Exception as e:
        logger.error(f"Error downloading infosite data: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# @app.get("/schedules")
# async def list_schedules():
#     """列出所有已下载的调度文件"""
#     logger.info("Listing all schedule files")
#     try:
#         import glob

#         csv_files = glob.glob("schedule*.csv")
#         logger.debug(f"Found {len(csv_files)} schedule files")
#         return {"schedules": csv_files}
#     except Exception as e:
#         logger.error(f"Error listing schedules: {str(e)}", exc_info=True)
#         raise HTTPException(status_code=500, detail=str(e))


# @app.get("/schedule/{filename}")
# async def get_schedule(filename: str):
#     """获取特定调度文件的内容"""
#     logger.info(f"Retrieving schedule file: {filename}")
#     try:
#         import pandas as pd

#         df = pd.read_csv(filename)
#         logger.debug(f"Successfully loaded {len(df)} records from {filename}")
#         return {"data": df.to_dict("records")}
#     except FileNotFoundError:
#         logger.warning(f"Schedule file not found: {filename}")
#         raise HTTPException(status_code=404, detail="Schedule file not found")
#     except Exception as e:
#         logger.error(f"Error reading schedule file {filename}: {str(e)}", exc_info=True)
#         raise HTTPException(status_code=500, detail=str(e))


@app.get("/infosite-files")
async def list_infosite_files():
    """列出所有可用的infosite文件"""
    logger.info("Listing infosite files")
    try:
        import glob

        infosite_dir = "./data/infosite/"
        Path(infosite_dir).mkdir(parents=True, exist_ok=True)

        csv_files = glob.glob(f"{infosite_dir}*.csv")
        # 只返回文件名，不包含路径
        filenames = [Path(f).name for f in csv_files]

        logger.debug(f"Found {len(filenames)} infosite files")
        return {"infosite_files": filenames}
    except Exception as e:
        logger.error(f"Error listing infosite files: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/download-excel/{filename}")
async def download_excel_file(filename: str):
    """下载合并后的Excel文件"""
    logger.info(f"Excel file download request: {filename}")

    try:
        # 构建文件路径
        excel_dir = Path("./data/merge/")

        # 如果没有扩展名，添加.xlsx
        if not filename.endswith(".xlsx"):
            filename = f"{filename}.xlsx"

        file_path = excel_dir / filename

        # 检查文件是否存在
        if not file_path.exists():
            logger.warning(f"Excel file not found: {file_path}")
            raise HTTPException(
                status_code=404, detail=f"Excel file '{filename}' not found"
            )

        logger.info(f"Serving Excel file: {file_path}")

        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading Excel file: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/excel-files")
async def list_excel_files():
    """列出所有可用的Excel文件"""
    logger.info("Listing Excel files")
    try:
        import glob

        excel_dir = "./data/merge/"
        Path(excel_dir).mkdir(parents=True, exist_ok=True)

        excel_files = glob.glob(f"{excel_dir}*.xlsx")
        files_info = []

        for file_path in excel_files:
            file_obj = Path(file_path)
            stat = file_obj.stat()

            files_info.append(
                {
                    "filename": file_obj.name,
                    "size_bytes": stat.st_size,
                    "size_mb": round(stat.st_size / (1024 * 1024), 2),
                    "created_time": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                }
            )

        # 按修改时间排序，最新的在前面
        files_info.sort(key=lambda x: x["modified_time"], reverse=True)

        logger.debug(f"Found {len(files_info)} Excel files")
        return {"excel_files": files_info, "total_count": len(files_info)}

    except Exception as e:
        logger.error(f"Error listing Excel files: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting IPTV API server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
