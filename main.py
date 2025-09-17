from fastapi import FastAPI, HTTPException
from datetime import datetime, date
from script.iptv import download_schedule  # 假设你有这个函数
from schema.schema import IptvRequest, IptvResponse
from utils.logger import logger
from utils.processing import process_schedule, process_multiple_schedules

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
        await process_schedule(filename, start_date, end_date)

        logger.info(f"Schedule downloaded successfully: {filename}")

        return IptvResponse(
            success=True,
            message="IPTV downloaded successfully",
            filename=f"/iptv/processed/{filename}",
            download_time=datetime.now(),
        )
    except Exception as e:
        logger.error(f"Error downloading schedule: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/schedules")
async def list_schedules():
    """列出所有已下载的调度文件"""
    logger.info("Listing all schedule files")
    try:
        import glob

        csv_files = glob.glob("schedule*.csv")
        logger.debug(f"Found {len(csv_files)} schedule files")
        return {"schedules": csv_files}
    except Exception as e:
        logger.error(f"Error listing schedules: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/schedule/{filename}")
async def get_schedule(filename: str):
    """获取特定调度文件的内容"""
    logger.info(f"Retrieving schedule file: {filename}")
    try:
        import pandas as pd

        df = pd.read_csv(filename)
        logger.debug(f"Successfully loaded {len(df)} records from {filename}")
        return {"data": df.to_dict("records")}
    except FileNotFoundError:
        logger.warning(f"Schedule file not found: {filename}")
        raise HTTPException(status_code=404, detail="Schedule file not found")
    except Exception as e:
        logger.error(f"Error reading schedule file {filename}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting IPTV API server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
