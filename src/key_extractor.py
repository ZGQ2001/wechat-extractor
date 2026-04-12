import subprocess
import platform
import os
import logging
from typing import Optional

try:
    import pymem
except ImportError:
    pymem = None

logger = logging.getLogger(\"KeyExtractor\")

class KeyExtractor:
    WIN_OFFSETS = {
        \"3.9.11\": 0x123456, 
        \"3.9.12\": 0x654321,
    }

    @staticmethod
    def check_mac_sip() -> bool:
        try:
            result = subprocess.run(['csrutil', 'status'], capture_output=True, text=True)
            return \"enabled\" not in result.stdout.lower()
        except Exception:
            return False

    @classmethod
    def get_key_mac(cls) -> Optional[str]:
        if not cls.check_mac_sip():
            logger.error(\"SIP is enabled. Please disable SIP to extract key via lldb.\")
            return None

        try:
            pgrep = subprocess.run(['pgrep', '-x', 'WeChat'], capture_output=True, text=True)
            if not pgrep.stdout:
                logger.error(\"WeChat is not running.\")
                return None
            pid = pgrep.stdout.strip()

            arch = platform.machine()
            reg = \"$x1\" if \"arm\" in arch.lower() else \"$rsi\"

            commands = [
                f\"process attach -p {pid}\",
                \"breakpoint set -n sqlite3_key\",
                \"continue\",
                f\"memory read --size 1 --format x --count 32 {reg}\",
                \"detach\",
                \"quit\"
            ]
            
            input_str = \"\\n\".join(commands) + \"\\n\"
            process = subprocess.Popen(
                ['sudo', 'lldb'], 
                stdin=subprocess.PIPE, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True
            )
            stdout, stderr = process.communicate(input=input_str)

            for line in stdout.splitlines():
                if \"0x\" in line and len(line.strip()) > 40:
                    bytes_part = line.split(':')[-1].strip()
                    hex_key = \"\".join(bytes_part.split()).replace(\"0x\", \"\")
                    if len(hex_key) == 64:
                        return hex_key
        except Exception as e:
            logger.exception(f\"Mac key extraction failed: {e}\")
        return None

    @classmethod
    def get_key_windows(cls) -> Optional[str]:
        if pymem is None:
            logger.error(\"pymem library not installed.\")
            return None

        try:
            pm = pymem.Pymem(\"WeChat.exe\")
            module = pymem.process.module_from_name(pm.process_handle, \"WeChatWin.dll\")
            base_addr = module.lpBaseOfDll
            version = cls._get_wechat_version()
            offset = cls.WIN_OFFSETS.get(version)
            if not offset:
                logger.error(f\"No offset found for WeChat version {version}.\")
                return None
            key_addr = base_addr + offset
            key_bytes = pm.read_bytes(key_addr, 32)
            return key_bytes.hex()
        except Exception as e:
            logger.exception(f\"Windows key extraction failed: {e}\")
        return None

    @staticmethod
    def _get_wechat_version() -> str:
        return \"3.9.11\" 

def extract_key(platform: str) -> Optional[str]:
    if platform == 'mac':
        return KeyExtractor.get_key_mac()
    elif platform == 'windows':
        return KeyExtractor.get_key_windows()
    return None
