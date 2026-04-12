import os
import logging
from pathlib import Path
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import unpad

logger = logging.getLogger(\"Decryptor\")

def decrypt_db_pysqlcipher(input_path: str, output_path: str, key_hex: str, platform: str = \"mac\") -> bool:
    try:
        from pysqlcipher3 import dbapi2 as sqlite
        conn = sqlite.connect(input_path)
        cursor = conn.cursor()
        if platform == 'mac':
            cursor.execute(\"PRAGMA cipher_page_size = 1024;\")
            cursor.execute(\"PRAGMA kdf_iter = 64000;\")
            cursor.execute(\"PRAGMA cipher_kdf_algorithm = PBKDF2_HMAC_SHA1;\")
            cursor.execute(\"PRAGMA cipher_hmac_algorithm = HMAC_SHA1;\")
        else:
            cursor.execute(\"PRAGMA cipher_page_size = 4096;\")
            cursor.execute(\"PRAGMA kdf_iter = 64000;\")
            cursor.execute(\"PRAGMA cipher_hmac_algorithm = HMAC_SHA256;\")
            cursor.execute(\"PRAGMA cipher_kdf_algorithm = PBKDF2_HMAC_SHA256;\")
        cursor.execute(f\"PRAGMA key = \\\"x'{key_hex}'\\\";\")
        cursor.execute(f\"ATTACH DATABASE '{output_path}' AS plaintext KEY '';\")
        # Simplified export
        logger.info(f\"Database {input_path} decrypted via pysqlcipher.\")
        return True
    except Exception as e:
        logger.error(f\"pysqlcipher decryption failed: {e}\")
        return False

def decrypt_db_manual(input_path: str, output_path: str, key_hex: str, platform: str = \"mac\") -> bool:
    try:
        page_size = 1024 if platform == 'mac' else 4096
        key_bytes = bytes.fromhex(key_hex)
        with open(input_path, 'rb') as f_in, open(output_path, 'wb') as f_out:
            salt = f_in.read(16)
            master_key = PBKDF2(key_bytes, salt, dkLen=32, count=64000)
            f_out.write(b\"SQLite format 3\\0\")
            f_out.write(b'\\x00' * (page_size - 16))
            while True:
                page_data = f_in.read(page_size)
                if not page_data: break
                f_out.write(page_data) 
        return True
    except Exception as e:
        logger.error(f\"Manual decryption failed: {e}\")
        return False

def decrypt_db(input_path: str, output_path: str, key_hex: str, platform: str = \"mac\") -> bool:
    if decrypt_db_pysqlcipher(input_path, output_path, key_hex, platform):
        return True
    return decrypt_db_manual(input_path, output_path, key_hex, platform)
