import argparse
import os
import sys
from key_extractor import WeChatKeyExtractor
from decrypter import WeChatDecrypter

def main():
    parser = argparse.ArgumentParser(description="WeChat Chat Record Export Tool - Core Modules")
    
    parser.add_argument("--extract", action="store_true", help="Extract the WeChat database key from memory")
    parser.add_argument("--decrypt", action="store_true", help="Decrypt the WeChat database")
    parser.add_argument("--db-path", type=str, help="Path to the encrypted .db file")
    parser.add_argument("--out-path", type=str, help="Path to save the decrypted .db file")
    parser.add_argument("--key", type=str, help="Manually provide the database key (hex)")

    args = parser.parse_args()

    if not args.extract and not args.decrypt:
        parser.print_help()
        sys.exit(1)

    key = args.key

    # 1. Key Extraction
    if args.extract:
        print("[*] Attempting to extract WeChat key from memory...")
        try:
            extractor = WeChatKeyExtractor()
            key = extractor.extract_key()
            print(f"[+] Successfully extracted key: {key}")
        except Exception as e:
            print(f"[-] Extraction failed: {e}")
            if not args.key:
                print("[-] No manual key provided. Cannot proceed with decryption.")
                sys.exit(1)

    # 2. Decryption
    if args.decrypt:
        if not key:
            print("[-] No key available for decryption. Use --extract or --key.")
            sys.exit(1)
        
        if not args.db_path or not args.out_path:
            print("[-] Please provide --db-path and --out-path for decryption.")
            sys.exit(1)

        print(f"[*] Decrypting database {args.db_path}...")
        try:
            decrypter = WeChatDecrypter(key)
            decrypter.decrypt_database(args.db_path, args.out_path)
            print(f"[+] Database decrypted and saved to: {args.out_path}")
        except Exception as e:
            print(f"[-] Decryption failed: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
