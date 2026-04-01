"""基于文件的 Chat 仓储实现"""
import logging
from typing import Optional
from pathlib import Path

from domain.chat.chat_thread import ChatThread
from domain.chat.chat_message import ChatMessage
from domain.chat.chat_repository import ChatRepository
from infrastructure.persistence.storage.backend import StorageBackend

logger = logging.getLogger(__name__)


class FileChatRepository(ChatRepository):
    """基于文件系统的 Chat 仓储实现

    使用 JSON 文件存储聊天数据，路径为 novels/{novel_id}/chat/thread.json
    """

    def __init__(self, storage: StorageBackend):
        """初始化仓储

        Args:
            storage: 存储后端
        """
        self.storage = storage

    def _get_path(self, novel_id: str) -> str:
        """获取聊天线程文件路径

        Args:
            novel_id: 小说 ID

        Returns:
            文件路径
        """
        return f"novels/{novel_id}/chat/thread.json"

    def save(self, thread: ChatThread) -> None:
        """保存聊天线程"""
        path = self._get_path(thread.novel_id)
        data = {
            "thread_id": thread.thread_id,
            "updated_at": thread.updated_at.isoformat() + "Z",
            "messages": [msg.to_dict() for msg in thread.messages]
        }
        self.storage.write_json(path, data)

    def get_by_novel_id(self, novel_id: str) -> Optional[ChatThread]:
        """根据小说 ID 获取聊天线程"""
        path = self._get_path(novel_id)

        if not self.storage.exists(path):
            return None

        try:
            data = self.storage.read_json(path)

            # Parse timestamp
            updated_at_str = data.get("updated_at", "")
            if updated_at_str.endswith("Z"):
                updated_at_str = updated_at_str[:-1]
            from datetime import datetime
            updated_at = datetime.fromisoformat(updated_at_str)

            # Parse messages
            messages = [
                ChatMessage.from_dict(msg_data)
                for msg_data in data.get("messages", [])
            ]

            return ChatThread(
                thread_id=data["thread_id"],
                novel_id=novel_id,
                messages=messages,
                updated_at=updated_at
            )
        except Exception as e:
            logger.error(f"Failed to load chat thread from {path}: {str(e)}")
            return None

    def delete(self, novel_id: str) -> None:
        """删除聊天线程"""
        path = self._get_path(novel_id)
        if self.storage.exists(path):
            self.storage.delete(path)

    def exists(self, novel_id: str) -> bool:
        """检查聊天线程是否存在"""
        path = self._get_path(novel_id)
        return self.storage.exists(path)
