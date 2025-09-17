from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class IptvRequest(BaseModel):
    start_date: str  # 格式: "16/09/2025"
    end_date: str  # 格式: "17/09/2025"
    filename: Optional[str] = None  # 可选的文件名


class IptvResponse(BaseModel):
    success: bool
    message: str
    filename: Optional[str] = None
    download_time: datetime
