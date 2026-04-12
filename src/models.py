from dataclasses import dataclass
from typing import Optional

@dataclass
class Message:
    \"\"\"聊天消息数据模型\"\"\"
    local_id: str
    svr_id: str
    create_time: int
    content: str
    msg_type: int
    sender: str
    is_revoked: bool = False
    extra_data: Optional[dict] = None

    def to_dict(self):
        return {
            \"local_id\": self.local_id,
            \"svr_id\": self.svr_id,
            \"create_time\": self.create_time,
            \"content\": self.content,
            \"msg_type\": self.msg_type,
            \"sender\": self.sender,
            \"is_revoked\": self.is_revoked,
            \"extra_data\": self.extra_data
        }
