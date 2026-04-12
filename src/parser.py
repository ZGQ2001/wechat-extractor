import sqlite3
import logging
from typing import List, Optional
from .models import Message

logger = logging.getLogger(\"Parser\")

class WeChatParser:
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def get_all_chat_tables(self) -> List[str]:
        self.cursor.execute(\"SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'Chat_%';\")
        return [row[0] for row in self.cursor.fetchall()]

    def parse_chat(self, table_name: str, contact_id: str = None) -> List[Message]:
        query = f\"SELECT localId, svrId, createTime, content, type FROM {table_name} ORDER BY createTime ASC\"
        self.cursor.execute(query)
        messages = []
        for row in self.cursor.fetchall():
            messages.append(Message(
                local_id=str(row[0]),
                svr_id=str(row[1]),
                create_time=row[2],
                content=row[3],
                msg_type=row[4],
                sender=contact_id or table_name,
                is_revoked=False
            ))
        return messages

    def close(self):
        self.conn.close()
