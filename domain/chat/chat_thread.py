"""Chat Thread Aggregate Root"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
import uuid

from domain.chat.chat_message import ChatMessage


@dataclass
class ChatThread:
    """聊天线程聚合根

    管理一个小说的聊天消息历史。
    """
    thread_id: str
    novel_id: str
    messages: List[ChatMessage] = field(default_factory=list)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    @staticmethod
    def create(novel_id: str) -> "ChatThread":
        """创建新的聊天线程"""
        return ChatThread(
            thread_id=str(uuid.uuid4()),
            novel_id=novel_id,
            messages=[],
            updated_at=datetime.utcnow()
        )

    def add_message(self, message: ChatMessage) -> None:
        """添加消息到线程"""
        self.messages.append(message)
        self.updated_at = datetime.utcnow()

    def clear_messages(self) -> None:
        """清空所有消息"""
        self.messages.clear()
        self.updated_at = datetime.utcnow()

    def get_messages(self, limit: Optional[int] = None) -> List[ChatMessage]:
        """获取消息列表

        Args:
            limit: 限制返回的消息数量，None 表示返回所有

        Returns:
            消息列表
        """
        if limit is None:
            return self.messages.copy()
        return self.messages[-limit:] if limit > 0 else []

    def get_message_count(self) -> int:
        """获取消息数量"""
        return len(self.messages)
