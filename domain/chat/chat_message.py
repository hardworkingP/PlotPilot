"""Chat Message Entity"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List
import uuid


@dataclass
class ToolCall:
    """工具调用记录"""
    name: str
    ok: bool
    detail: str


@dataclass
class MessageMeta:
    """消息元数据"""
    tools: Optional[List[ToolCall]] = None

    def to_dict(self) -> Optional[Dict[str, Any]]:
        """转换为字典"""
        if self.tools is None:
            return None
        return {
            "tools": [
                {"name": t.name, "ok": t.ok, "detail": t.detail}
                for t in self.tools
            ]
        }

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> Optional["MessageMeta"]:
        """从字典创建"""
        if data is None:
            return None
        tools_data = data.get("tools")
        if tools_data:
            tools = [
                ToolCall(name=t["name"], ok=t["ok"], detail=t["detail"])
                for t in tools_data
            ]
            return cls(tools=tools)
        return cls(tools=None)


@dataclass
class ChatMessage:
    """聊天消息实体

    表示一条聊天消息，包含角色、内容、时间戳和元数据。
    """
    id: str
    role: str  # user, assistant, system
    content: str
    ts: datetime
    meta: Optional[MessageMeta] = None

    def __post_init__(self):
        """验证消息数据"""
        if self.role not in ["user", "assistant", "system"]:
            raise ValueError(f"Invalid role: {self.role}")
        if not self.content:
            raise ValueError("Message content cannot be empty")

    @staticmethod
    def create_user_message(content: str) -> "ChatMessage":
        """创建用户消息"""
        return ChatMessage(
            id=str(uuid.uuid4()),
            role="user",
            content=content,
            ts=datetime.utcnow(),
            meta=None
        )

    @staticmethod
    def create_assistant_message(
        content: str,
        tools: Optional[List[ToolCall]] = None
    ) -> "ChatMessage":
        """创建助手消息"""
        meta = MessageMeta(tools=tools) if tools else None
        return ChatMessage(
            id=str(uuid.uuid4()),
            role="assistant",
            content=content,
            ts=datetime.utcnow(),
            meta=meta
        )

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "role": self.role,
            "content": self.content,
            "ts": self.ts.isoformat() + "Z",
            "meta": self.meta.to_dict() if self.meta else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatMessage":
        """从字典创建"""
        ts_str = data["ts"]
        if ts_str.endswith("Z"):
            ts_str = ts_str[:-1]
        ts = datetime.fromisoformat(ts_str)

        return cls(
            id=data["id"],
            role=data["role"],
            content=data["content"],
            ts=ts,
            meta=MessageMeta.from_dict(data.get("meta"))
        )
