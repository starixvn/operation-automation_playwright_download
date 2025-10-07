from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class IptvRequest(BaseModel):
    start_date: str  # 格式: "16/09/2025"
    end_date: str  # 格式: "17/09/2025"
    filename: Optional[str] = None  # 可选的文件名


class IptvResponse(BaseModel):
    success: bool
    message: str
    filename: Optional[str] = None
    download_time: datetime


class InfositeRequest(BaseModel):
    start_time: str  # 格式: "2025-09-16"
    end_time: str  # 格式: "2025-09-17"
    filename: str  # 可选的文件名
    leagues: Optional[List[str]] = None  # 比赛类型列表
    league_groups: Optional[List[str]] = None  # 比赛类型列表
    sports: Optional[List[str]] = None  # 比赛类型列表
    save_features: Optional[List[str]] = None  # 比赛类型列表
    batch_size: Optional[int] = 100  # 比赛类型列表


class InfositeResponse(BaseModel):
    success: bool
    message: str
    filename: str
    file_path: str
    download_time: datetime


class MergeRequest(BaseModel):
    iptv_path: str  # IPTV处理后的文件名
    infosite_path: str  # infosite CSV文件名
    output_filename: str  # 输出Excel文件名

class CheckLeaguesRequest(BaseModel):
    start_time: str  # 格式: "2025-09-16"
    end_time: str  # 格式: "2025-09-17"
    league_groups: list[str]  # 比赛类型列表

class CheckLeaguesResponse(BaseModel):
    success: bool
    count: int
    leagues: list[str]