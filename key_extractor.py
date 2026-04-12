import os
import platform
import subprocess
import re

try:
    import pymem
except ImportError:
    pymem = None

class WeChatKeyExtractor:
    """
    Extractor for WeChat database key from memory.
    Supports Windows (via pymem) and macOS (via lldb).
    """

    def __init__(self):
        self.os_type = platform.system()

    def extract_key(self):
        if self.os_type == "Windows":
            return self._extract_windows()
        elif self.os_type == "Darwin":
            return self._extract_macos()
        else:
            raise NotImplementedError(f"Operating system {self.os_type} is not supported.")

    def _extract_windows(self):
        if pymem is None:
            raise ImportError("pymem library is required for Windows key extraction. Please install it via 'pip install pymem'.")

        try:
            pm = pymem.Pymem("WeChat.exe")
            # Common pattern for WeChat key in memory (this varies by version)
            # This is a simplified representation; in production, a more robust signature search is used.
            # We search for the key pattern in the process memory.
            
            # Example pattern search (placeholder for actual signature)
            # In reality, one would search for a known byte sequence near the key.
            # For this implementation, we simulate the process of finding the 32-byte key.
            
            # Searching for a pattern that typically precedes the key
            pattern = b"\x01\x00\x00\x00\x00\x00\x00\x00" # Placeholder signature
            address = pymem.pattern.pattern_scan_all(pm.process_handle, pattern)
            
            if address:
                # Assume key is at a specific offset from the pattern
                key = pm.read_bytes(address + 0x10, 32)
                return key.hex()
            else:
                raise Exception("Could not find WeChat key pattern in memory.")
                
        except Exception as e:
            raise Exception(f"Windows extraction failed: {str(e)}")

    def _extract_macos(self):
        try:
            # Use lldb to attach to WeChat and read memory
            # This is a simplified command; the actual offset depends on the WeChat version.
            cmd = [
                "lldb", 
                "-p", "WeChat", 
                "--batch", 
                "-o", "memory read --size 32 --format x 0x12345678" # Placeholder address
            ]
            # In a real scenario, the address is found by searching for signatures via lldb scripts.
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Parse the hex output from lldb
            hex_match = re.search(r"0x([0-9a-fA-F]+)", result.stdout)
            if hex_match:
                return hex_match.group(1)
            else:
                raise Exception("Could not parse key from lldb output.")
                
        except subprocess.CalledProcessError as e:
            raise Exception(f"macOS extraction failed: {str(e)}")
        except Exception as e:
            raise Exception(f"macOS extraction failed: {str(e)}")

if __name__ == "__main__":
    extractor = WeChatKeyExtractor()
    try:
        key = extractor.extract_key()
        print(f"Extracted Key: {key}")
    except Exception as e:
        print(f"Error: {e}")
