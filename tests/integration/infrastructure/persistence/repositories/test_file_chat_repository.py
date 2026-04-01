"""FileChatRepository 集成测试"""
import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from domain.chat.chat_thread import ChatThread
from domain.chat.chat_message import ChatMessage, ToolCall, MessageMeta
from infrastructure.persistence.storage.file_storage import FileStorage
from infrastructure.persistence.repositories.file_chat_repository import FileChatRepository


class TestFileChatRepository:
    """FileChatRepository 集成测试"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp_path = tempfile.mkdtemp()
        yield Path(temp_path)
        shutil.rmtree(temp_path)

    @pytest.fixture
    def storage(self, temp_dir):
        """创建 FileStorage 实例"""
        return FileStorage(temp_dir)

    @pytest.fixture
    def repository(self, storage):
        """创建 FileChatRepository 实例"""
        return FileChatRepository(storage)

    def test_save_and_get(self, repository):
        """测试保存和获取聊天线程"""
        thread = ChatThread.create("test-novel")
        user_msg = ChatMessage.create_user_message("Hello")
        thread.add_message(user_msg)

        repository.save(thread)
        retrieved = repository.get_by_novel_id("test-novel")

        assert retrieved is not None
        assert retrieved.novel_id == "test-novel"
        assert len(retrieved.messages) == 1
        assert retrieved.messages[0].content == "Hello"
        assert retrieved.messages[0].role == "user"

    def test_get_nonexistent(self, repository):
        """测试获取不存在的聊天线程"""
        result = repository.get_by_novel_id("nonexistent")
        assert result is None

    def test_save_with_multiple_messages(self, repository):
        """测试保存包含多条消息的线程"""
        thread = ChatThread.create("test-novel")

        user_msg = ChatMessage.create_user_message("Hello")
        thread.add_message(user_msg)

        assistant_msg = ChatMessage.create_assistant_message("Hi there!")
        thread.add_message(assistant_msg)

        repository.save(thread)
        retrieved = repository.get_by_novel_id("test-novel")

        assert len(retrieved.messages) == 2
        assert retrieved.messages[0].role == "user"
        assert retrieved.messages[1].role == "assistant"
        assert retrieved.messages[1].content == "Hi there!"

    def test_save_with_tool_calls(self, repository):
        """测试保存包含工具调用的消息"""
        thread = ChatThread.create("test-novel")

        tools = [
            ToolCall(name="cast_get_snapshot", ok=True, detail="获取快照成功"),
            ToolCall(name="story_upsert", ok=True, detail="更新故事成功")
        ]
        assistant_msg = ChatMessage.create_assistant_message("完成操作", tools)
        thread.add_message(assistant_msg)

        repository.save(thread)
        retrieved = repository.get_by_novel_id("test-novel")

        assert len(retrieved.messages) == 1
        assert retrieved.messages[0].meta is not None
        assert retrieved.messages[0].meta.tools is not None
        assert len(retrieved.messages[0].meta.tools) == 2
        assert retrieved.messages[0].meta.tools[0].name == "cast_get_snapshot"
        assert retrieved.messages[0].meta.tools[0].ok is True

    def test_delete(self, repository):
        """测试删除聊天线程"""
        thread = ChatThread.create("test-novel")
        repository.save(thread)

        assert repository.exists("test-novel")

        repository.delete("test-novel")
        assert not repository.exists("test-novel")

    def test_exists(self, repository):
        """测试检查聊天线程是否存在"""
        assert not repository.exists("test-novel")

        thread = ChatThread.create("test-novel")
        repository.save(thread)

        assert repository.exists("test-novel")

    def test_update_existing_thread(self, repository):
        """测试更新已存在的线程"""
        thread = ChatThread.create("test-novel")
        user_msg1 = ChatMessage.create_user_message("First message")
        thread.add_message(user_msg1)
        repository.save(thread)

        # 获取并添加新消息
        retrieved = repository.get_by_novel_id("test-novel")
        user_msg2 = ChatMessage.create_user_message("Second message")
        retrieved.add_message(user_msg2)
        repository.save(retrieved)

        # 验证更新
        final = repository.get_by_novel_id("test-novel")
        assert len(final.messages) == 2
        assert final.messages[1].content == "Second message"

    def test_clear_messages(self, repository):
        """测试清空消息"""
        thread = ChatThread.create("test-novel")
        thread.add_message(ChatMessage.create_user_message("Message 1"))
        thread.add_message(ChatMessage.create_user_message("Message 2"))
        repository.save(thread)

        # 清空消息
        retrieved = repository.get_by_novel_id("test-novel")
        retrieved.clear_messages()
        repository.save(retrieved)

        # 验证清空
        final = repository.get_by_novel_id("test-novel")
        assert len(final.messages) == 0

    def test_message_timestamp_persistence(self, repository):
        """测试消息时间戳持久化"""
        thread = ChatThread.create("test-novel")
        msg = ChatMessage.create_user_message("Test")
        original_ts = msg.ts
        thread.add_message(msg)

        repository.save(thread)
        retrieved = repository.get_by_novel_id("test-novel")

        # 时间戳应该保持一致（允许微小差异）
        retrieved_ts = retrieved.messages[0].ts
        assert abs((retrieved_ts - original_ts).total_seconds()) < 1
