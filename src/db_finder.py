import os
import glob
import logging
from pathlib import Path
from typing import List

# 导入刚才写的解密函数
from src.decryptor import decrypt_db

logger = logging.getLogger("DBFinder")

def get_default_db_dirs(platform: str) -> List[Path]:
    """尝试自动推断微信数据库存放的可能路径"""
    possible_paths = []
    user_home = Path.home()

    if platform == "windows":
        # 微信 PC 版默认路径
        possible_paths.append(user_home / "Documents" / "WeChat Files")
        # 有些人会放在公共文档下
        possible_paths.append(Path(os.environ.get("PUBLIC", "C:\\Users\\Public")) / "Documents" / "WeChat Files")
    elif platform == "mac":
        # Mac App Store 版路径
        possible_paths.append(user_home / "Library/Containers/com.tencent.xinWeChat/Data/Library/Application Support/com.tencent.xinWeChat")
    
    return [p for p in possible_paths if p.exists()]

def find_wechat_dbs(base_dir: Path, platform: str) -> List[Path]:
    """遍历目录寻找消息数据库(MSG.db)和联系人数据库"""
    found_dbs = []
    
    logger.info(f"🔍 正在扫描目录: {base_dir}")
    
    # 使用 glob 进行全量扫描
    for root, dirs, files in os.walk(base_dir):
        # 排除掉不相关的目录，加快扫描速度
        if any(exclude in root for exclude in ['Attachment', 'Image', 'Video', 'File', 'Temp']):
            continue

        for file in files:
            file_name = file.lower()
            # Windows 的 MSG0.db, MSG1.db... 或者 MicroMsg.db (联系人)
            # Mac 的 msg_0.db, msg_1.db... 或者 wccontact_new2.db (联系人)
            if file_name.startswith("msg") and file_name.endswith(".db"):
                found_dbs.append(Path(root) / file)
            elif file_name in ["micromsg.db", "wccontact_new2.db", "group_new.db"]:
                found_dbs.append(Path(root) / file)

    return found_dbs

def batch_decrypt(platform: str, key_hex: str, output_dir: Path, custom_db_path: str = None) -> List[Path]:
    """批量解密查找到的所有数据库"""
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)

    db_paths_to_decrypt = []

    # 如果用户指定了路径，则只扫指定路径；否则尝试自动寻找
    if custom_db_path and Path(custom_db_path).exists():
        db_paths_to_decrypt = find_wechat_dbs(Path(custom_db_path), platform)
    else:
        dirs = get_default_db_dirs(platform)
        if not dirs:
            logger.error("❌ 未能自动找到微信数据目录，请使用命令行参数 --db-path 手动指定！")
            return []
        for d in dirs:
            db_paths_to_decrypt.extend(find_wechat_dbs(d, platform))

    if not db_paths_to_decrypt:
        logger.warning("⚠️ 未在指定目录下找到任何相关的微信 .db 文件。")
        return []

    logger.info(f"📦 共找到 {len(db_paths_to_decrypt)} 个待处理数据库文件。开始批量解密...")
    
    from rich.progress import Progress
    decrypted_files = []

    # 使用 rich 库展示漂亮的进度条
    with Progress() as progress:
        task = progress.add_task("[cyan]正在解密数据库...", total=len(db_paths_to_decrypt))
        
        for db_path in db_paths_to_decrypt:
            # 保持一些子目录结构，防止重名 (比如账号 A 的 MSG0.db 和账号 B 的 MSG0.db)
            parent_name = db_path.parent.name
            safe_filename = f"{parent_name}_{db_path.name}"
            out_path = output_dir / safe_filename
            
            success = decrypt_db(str(db_path), str(out_path), key_hex, platform)
            if success:
                decrypted_files.append(out_path)
            
            progress.advance(task)

    logger.info(f"🎉 批量解密完成！成功: {len(decrypted_files)} 个。文件保存在 -> {output_dir.absolute()}")
    return decrypted_files