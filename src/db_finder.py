import os
import logging
from pathlib import Path
from typing import List, Optional
from .decryptor import decrypt_db

logger = logging.getLogger(\"DBFinder\")

class DBFinder:
    MAC_BASE_PATH = Path(\"~/Library/Containers/com.tencent.xinWeChat/Data/Library/Application Support/com.tencent.xinWeChat\").expanduser()
    WIN_BASE_PATH = Path(os.getenv(\"USERPROFILE\", \"\")) / \"Documents/WeChat Files\"

    @classmethod
    def find_all_db(cls, platform: str, custom_path: Optional[str] = None) -> List[Path]:
        base = Path(custom_path) if custom_path else (cls.MAC_BASE_PATH if platform == 'mac' else cls.WIN_BASE_PATH)
        if not base.exists():
            logger.error(f\"Base path {base} does not exist.\")
            return []
        return list(base.rglob(\"*.db\"))

def find_and_decrypt_all(platform: str, key_hex: str, output_dir: str, custom_path: Optional[str] = None) -> List[str]:
    finder = DBFinder()
    db_files = finder.find_all_db(platform, custom_path)
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    success_files = []
    for db_file in db_files:
        if \"msg\" not in db_file.name.lower() and \"MSG\" not in db_file.name:
            continue
        target_path = out_path / f\"decrypted_{db_file.name}\"
        if target_path.exists():
            with open(target_path, 'rb') as f:
                if f.read(15) == b\"SQLite format 3\":
                    success_files.append(str(target_path))
                    continue
        if decrypt_db(str(db_file), str(target_path), key_hex, platform):
            success_files.append(str(target_path))
    return success_files
