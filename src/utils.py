import datetime
import platform
from pathlib import Path
import logging

def format_timestamp(ts: int) -> str:
    \"\"\"将 Unix 时间戳转换为可读格式\"\"\"
    return datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

def get_platform() -> str:
    \"\"\"获取当前系统平台\"\"\"
    sys_name = platform.system().lower()
    if sys_name == 'darwin':
        return 'mac'
    elif sys_name == 'windows':
        return 'windows'
    raise OSError(f\"Unsupported platform: {sys_name}\")

def setup_logging(level=logging.INFO):
    logging.basicConfig(
        level=level,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
