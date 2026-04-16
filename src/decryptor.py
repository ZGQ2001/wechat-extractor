import os
import hmac
import hashlib
import logging
from Cryptodome.Cipher import AES

logger = logging.getLogger("Decryptor")

def decrypt_db(input_path: str, output_path: str, key_hex: str, platform: str = "windows") -> bool:
    """
    纯 Python 实现的微信 SQLCipher 数据库解密
    
    参数:
        input_path: 加密的 .db 文件路径
        output_path: 解密后的标准 SQLite 输出路径
        key_hex: 64 字符十六进制密钥
        platform: "windows" (页大小4096) 或 "mac" (页大小1024)
    """
    if not os.path.exists(input_path):
        logger.error(f"❌ 文件不存在: {input_path}")
        return False

    # 微信不同平台的数据库页大小设定
    page_size = 4096 if platform.lower() == "windows" else 1024
    # SQLCipher 默认的保留区大小 (存放 IV 和 HMAC)
    reserve_size = 48 
    # HMAC 校验长度 (用于填充文件尾部以保证 SQLite 页对齐)
    mac_size = 32

    try:
        password = bytes.fromhex(key_hex.replace(" ", ""))
        with open(input_path, "rb") as f:
            blist = f.read()

        if len(blist) == 0:
            logger.warning(f"⚠️ 文件为空: {input_path}")
            return False

        # 检查是否已经是解密过的标准 SQLite 文件
        if blist[:16] == b"SQLite format 3\x00":
            logger.info(f"✅ 文件已经是解密状态，直接复制: {os.path.basename(input_path)}")
            with open(output_path, "wb") as out_f:
                out_f.write(blist)
            return True

        # SQLCipher 前 16 字节为 Salt（盐）
        salt = blist[:16]
        
        # 密钥派生：PBKDF2_HMAC_SHA1
        key_derivation = hashlib.pbkdf2_hmac('sha1', password, salt, 64000, 32)
        
        with open(output_path, "wb") as out_file:
            # 写入标准 SQLite 文件头
            out_file.write(b"SQLite format 3\x00")
            
            # 逐页进行 AES-256-CBC 解密
            for i in range(0, len(blist), page_size):
                page = blist[i : i + page_size]
                
                # 第 1 页结构特殊（包含了 Salt）
                if i == 0:
                    iv = page[16:32]
                    # 加密数据区域排除头部 salt+iv 以及尾部的 mac
                    enc_data = page[32 : page_size - mac_size]
                    cipher = AES.new(key_derivation, AES.MODE_CBC, iv)
                    decrypted = cipher.decrypt(enc_data)
                    
                    out_file.write(decrypted)
                    # 补齐尾部数据以维持 SQLite 严格的页对齐校验
                    out_file.write(page[page_size - mac_size :])
                # 第 N 页
                else:
                    iv = page[0:16]
                    enc_data = page[16 : page_size - mac_size]
                    cipher = AES.new(key_derivation, AES.MODE_CBC, iv)
                    decrypted = cipher.decrypt(enc_data)
                    
                    out_file.write(decrypted)
                    out_file.write(page[page_size - mac_size :])

        logger.debug(f"🔓 解密成功: {os.path.basename(input_path)}")
        return True

    except Exception as e:
        logger.error(f"❌ 解密失败 {os.path.basename(input_path)}: {e}")
        return False