import logging
import sys
from datetime import datetime
from pathlib import Path
import os

def setup_logger(name: str = "iptv_api", log_level: str = "INFO"):
    """设置日志配置"""

    # 创建logs目录
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # 获取日志级别
    level = getattr(logging, log_level.upper(), logging.INFO)

    # 创建logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 避免重复添加handler
    if logger.handlers:
        return logger

    # 创建格式器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 控制台handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 文件handler - 按日期分割
    today = datetime.now().strftime('%Y-%m-%d')
    file_handler = logging.FileHandler(
        log_dir / f"iptv_api_{today}.log",
        encoding='utf-8'
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # 错误文件handler
    error_handler = logging.FileHandler(
        log_dir / f"iptv_api_error_{today}.log",
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)

    return logger

# 创建全局logger实例
logger = setup_logger()