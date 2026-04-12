import os
import sqlite3

try:
    from pysqlcipher3 import dbapi2 as sqlite3_cipher
except ImportError:
    sqlite3_cipher = None

class WeChatDecrypter:
    """
    Decrypter for WeChat SQLCipher databases.
    """

    def __init__(self, key_hex):
        if sqlite3_cipher is None:
            raise ImportError("pysqlcipher3 is required for decryption. Please install it.")
        
        # Convert hex key to bytes
        self.key = bytes.fromhex(key_hex)

    def decrypt_database(self, encrypted_db_path, decrypted_db_path):
        """
        Decrypts an encrypted WeChat .db file and saves it to a new file.
        """
        if not os.path.exists(encrypted_db_path):
            raise FileNotFoundError(f"Encrypted database not found: {encrypted_db_path}")

        try:
            # Connect to the encrypted database
            conn = sqlite3_cipher.connect(encrypted_db_path)
            cursor = conn.cursor()
            
            # Set the decryption key
            # The key is typically passed as a raw binary string or a hex string
            # For SQLCipher, we use PRAGMA key
            cursor.execute(f"PRAGMA key = \"x'{self.key.hex()}'\";")
            
            # Verify the key by attempting a simple query
            try:
                cursor.execute("SELECT count(*) FROM sqlite_master;")
            except sqlite3_cipher.DatabaseError:
                raise Exception("Invalid key or corrupted database. Decryption failed.")

            # Attach a new empty database to export the decrypted content
            cursor.execute(f"ATTACH DATABASE '{decrypted_db_path}' AS decrypted;")
            cursor.execute("SELECT sqlcipher_export('decrypted');")
            cursor.execute("DETACH DATABASE decrypted;")
            
            conn.close()
            return True
            
        except Exception as e:
            raise Exception(f"Decryption process failed: {str(e)}")

if __name__ == "__main__":
    # Example usage
    import sys
    if len(sys.argv) < 4:
        print("Usage: python decrypter.py <key_hex> <encrypted_db> <decrypted_db>")
    else:
        try:
            decrypter = WeChatDecrypter(sys.argv[1])
            decrypter.decrypt_database(sys.argv[2], sys.argv[3])
            print("Database decrypted successfully.")
        except Exception as e:
            print(f"Error: {e}")
