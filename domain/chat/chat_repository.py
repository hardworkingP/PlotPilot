"""Chat Repository Interface"""
from abc import ABC, abstractmethod
from typing import Optional

from domain.chat.chat_thread import ChatThread


class ChatRepository(ABC):
    """聊天仓储接口

    定义聊天数据的持久化操作。
    """

    @abstractmethod
    def save(self, thread: ChatThread) -> None:
        """保存聊天线程

        Args:
            thread: 聊天线程
        """
        pass

    @abstractmethod
    def get_by_novel_id(self, novel_id: str) -> Optional[ChatThread]:
        """根据小说 ID 获取聊天线程

        Args:
            novel_id: 小说 ID

        Returns:
            聊天线程，如果不存在则返回 None
        """
        pass

    @abstractmethod
    def delete(self, novel_id: str) -> None:
        """删除聊天线程

        Args:
            novel_id: 小说 ID
        """
        pass

    @abstractmethod
    def exists(self, novel_id: str) -> bool:
        """检查聊天线程是否存在

        Args:
            novel_id: 小说 ID

        Returns:
            是否存在
        """
        pass
