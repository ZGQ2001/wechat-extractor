import csv
import json
import logging
from typing import List
from pathlib import Path
from .models import Message
from .utils import format_timestamp

logger = logging.getLogger(\"Exporter\")

class Exporter:
    @staticmethod
    def to_csv(messages: List[Message], output_path: str):
        with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([\"时间\", \"发送者\", \"类型\", \"内容\"])
            for m in messages:
                writer.writerow([format_timestamp(m.create_time), m.sender, m.msg_type, m.content])

    @staticmethod
    def to_json(messages: List[Message], output_path: str):
        data = [m.to_dict() for m in messages]
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @staticmethod
    def to_html(messages: List[Message], output_path: str):
        html_start = \"<html><body style='font-family:sans-serif; background:#f5f5f5;'>\"
        html_end = \"</body></html>\"
        body = \"\"
        for m in messages:
            align = \"right\" if \"me\" in m.sender.lower() else \"left\"
            color = \"#95ec69\" if align == \"right\" else \"#ffffff\"
            body += f\"<div style='text-align:{align}; margin:10px;'><span style='background:{color}; padding:5px; border-radius:5px;'>{m.content}</span><br><small>{format_timestamp(m.create_time)}</small></div>\"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_start + body + html_end)
