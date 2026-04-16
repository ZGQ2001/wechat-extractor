import os
import sys
import subprocess
import logging
from pathlib import Path
import re

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("KeyScanner_Manual")

def manual_bloodhound_scan() -> dict:
    try:
        import pymem
    except ImportError:
        logger.error("❌ 缺少 pymem")
        sys.exit(1)

    print("===" * 15)
    print("🎯 微信 4.1.x 猎犬定点爆破模式")
    print("===" * 15)

    # 1. 手动获取本地 Salt
    db_path_str = input("👉 请输入你的 msg.db 或 contact.db 的绝对路径 (不要带双引号):\n> ").strip().strip('"').strip("'")
    db_path = Path(db_path_str)
    
    if not db_path.exists():
        logger.error(f"❌ 找不到该文件，请检查路径是否正确: {db_path}")
        sys.exit(1)

    try:
        with open(db_path, "rb") as f:
            salt_bytes = f.read(16)
            if b"SQLite format 3" in salt_bytes:
                logger.error("❌ 这个文件没有加密！它是普通的 SQLite 数据库。")
                sys.exit(1)
            salt_hex = salt_bytes.hex().lower()
            logger.info(f"✅ 成功提取目标文件的物理特征 (Salt): {salt_hex}")
    except Exception as e:
        logger.error(f"❌ 读取文件失败: {e}")
        sys.exit(1)

    # 2. 寻找微信进程组
    target_exes = ["weixin.exe", "WeChat.exe"]
    pids = []
    for exe in target_exes:
        try:
            output = subprocess.check_output(f'tasklist /FI "IMAGENAME eq {exe}" /NH', shell=True).decode('gbk', errors='ignore')
            lines = [line for line in output.split('\n') if exe.lower() in line.lower()]
            pids.extend([int(line.split()[1]) for line in lines if len(line.split()) > 1])
        except Exception:
            continue

    if not pids:
        logger.error("❌ 未找到微信进程，请确保微信已登录。")
        sys.exit(1)

    # 3. 编译精准正则扫描器
    # 寻找：64位十六进制Key + 我们刚刚提取到的32位Salt
    pattern_exact = re.compile(b"([0-9a-fA-F]{64})" + salt_hex.encode(), re.IGNORECASE)
    # 备用寻找：带 x'' 壳的格式
    pattern_shell = re.compile(b"x'([0-9a-fA-F]{64})" + salt_hex.encode() + b"'", re.IGNORECASE)

    all_keys = set()
    
    logger.info(f"🧬 [步骤 3] 仪器已就绪，正在对 {len(pids)} 个进程的内存进行深度穿透... (约 15-30 秒)")
    
    for pid in pids:
        try:
            pm = pymem.Pymem(pid)
            for memory_region in pm.iter_region():
                # 仅筛选已提交并有读取权限的活动内存块
                if not memory_region.State == 0x1000:
                    continue
                if memory_region.Protect not in [0x02, 0x04, 0x20, 0x40]: 
                    continue
                    
                try:
                    data = pm.read_bytes(memory_region.BaseAddress, memory_region.RegionSize)
                    
                    # 精准匹配
                    for match in pattern_exact.finditer(data):
                        key = match.group(1).decode('ascii').lower()
                        if key != "0"*64:
                            all_keys.add(key)
                            
                    for match in pattern_shell.finditer(data):
                        key = match.group(1).decode('ascii').lower()
                        if key != "0"*64:
                            all_keys.add(key)

                except Exception:
                    pass 
        except Exception:
            pass 

    if all_keys:
        print("\n" + "="*50)
        print("🎉 爆破成功！我们在内存深处抓取到了以下可能的解密密钥：")
        for idx, key in enumerate(all_keys):
            print(f"🔑 Key [{idx+1}]: {key}")
        print("="*50)
        print("👉 下一步：你可以拿着这把钥匙，去运行我们之前的 decryptor.py 进行解密了！")
    else:
        print("\n❌ 定点爆破失败。内存中未发现该 Salt 的相关记录。")
        print("💡 请确认：1. 你是否在微信里点开了几个群聊（让程序把这个数据库读进内存）？")
        print("         2. 这个数据库是否属于当前正在登录的账号？")

if __name__ == "__main__":
    manual_bloodhound_scan()