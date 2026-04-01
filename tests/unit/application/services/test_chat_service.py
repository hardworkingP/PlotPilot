"""ChatService 单元测试"""
import pytest
from unittest.mock import Mock, AsyncMock, MagicMock
from datetime import datetime

from application.services.chat_service import ChatService
from domain.chat.chat_thread import ChatThread
from domain.chat.chat_message import ChatMessage
from domain.novel.entities.novel import Novel, NovelStage
from domain.novel.value_objects.novel_id import NovelId
from domain.bible.entities.bible import Bible
from domain.ai.services.llm_service import GenerationResult
from domain.ai.value_objects.token_usage import TokenUsage
from domain.shared.exceptions import EntityNotFoundError


class TestChatService:
    """ChatService 单元测试"""

    @pytest.fixture
    def mock_chat_repository(self):
        """Mock ChatRepository"""
        return Mock()

    @pytest.fixture
    def mock_llm_service(self):
        """Mock LLMService"""
        mock = Mock()
        mock.generate = AsyncMock()
        mock.generate_stream = AsyncMock()
        return mock

    @pytest.fixture
    def mock_novel_repository(self):
        """Mock NovelRepository"""
        return Mock()

    @pytest.fixture
    def mock_bible_repository(self):
        """Mock BibleRepository"""
        return Mock()

    @pytest.fixture
    def mock_cast_repository(self):
        """Mock CastRepository"""
        return Mock()

    @pytest.fixture
    def mock_knowledge_repository(self):
        """Mock KnowledgeRepository"""
        return Mock()

    @pytest.fixture
    def service(
        self,
        mock_chat_repository,
        mock_llm_service,
        mock_novel_repository,
        mock_bible_repository,
        mock_cast_repository,
        mock_knowledge_repository
    ):
        """创建 ChatService 实例"""
        return ChatService(
            mock_chat_repository,
            mock_llm_service,
            mock_novel_repository,
            mock_bible_repository,
            mock_cast_repository,
            mock_knowledge_repository
        )

    def test_get_messages_empty(self, service, mock_chat_repository):
        """测试获取空消息列表"""
        mock_chat_repository.get_by_novel_id.return_value = None

        result = service.get_messages("test-novel")

        assert result == {"messages": []}
        mock_chat_repository.get_by_novel_id.assert_called_once_with("test-novel")

    def test_get_messages_with_data(self, service, mock_chat_repository):
        """测试获取消息列表"""
        thread = ChatThread.create("test-novel")
        msg = ChatMessage.create_user_message("Hello")
        thread.add_message(msg)

        mock_chat_repository.get_by_novel_id.return_value = thread

        result = service.get_messages("test-novel")

        assert len(result["messages"]) == 1
        assert result["messages"][0]["content"] == "Hello"

    @pytest.mark.asyncio
    async def test_send_message_novel_not_found(
        self,
        service,
        mock_novel_repository
    ):
        """测试发送消息时小说不存在"""
        mock_novel_repository.get_by_id.return_value = None

        with pytest.raises(EntityNotFoundError):
            await service.send_message("nonexistent", "Hello")

    @pytest.mark.asyncio
    async def test_send_message_success(
        self,
        service,
        mock_chat_repository,
        mock_llm_service,
        mock_novel_repository,
        mock_bible_repository
    ):
        """测试成功发送消息"""
        # Setup mocks
        novel = Novel(
            id=NovelId("test-novel"),
            title="测试小说",
            author="作者",
            target_chapters=10
        )
        mock_novel_repository.get_by_id.return_value = novel
        mock_bible_repository.get_by_novel_id.return_value = None
        mock_chat_repository.get_by_novel_id.return_value = None

        mock_llm_service.generate.return_value = GenerationResult(
            content="AI 回复",
            token_usage=TokenUsage(input_tokens=10, output_tokens=20)
        )

        # Execute
        result = await service.send_message("test-novel", "Hello")

        # Verify
        assert result["ok"] is True
        assert result["reply"] == "AI 回复"
        mock_chat_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_message_with_clear_thread(
        self,
        service,
        mock_chat_repository,
        mock_llm_service,
        mock_novel_repository,
        mock_bible_repository
    ):
        """测试发送消息时清空线程"""
        # Setup mocks
        novel = Novel(
            id=NovelId("test-novel"),
            title="测试小说",
            author="作者",
            target_chapters=10
        )
        mock_novel_repository.get_by_id.return_value = novel
        mock_bible_repository.get_by_novel_id.return_value = None

        # 创建已有消息的线程
        thread = ChatThread.create("test-novel")
        thread.add_message(ChatMessage.create_user_message("Old message"))
        mock_chat_repository.get_by_novel_id.return_value = thread

        mock_llm_service.generate.return_value = GenerationResult(
            content="AI 回复",
            token_usage=TokenUsage(input_tokens=10, output_tokens=20)
        )

        # Execute with clear_thread=True
        result = await service.send_message(
            "test-novel",
            "New message",
            clear_thread=True
        )

        # Verify thread was cleared and new message added
        assert result["ok"] is True
        saved_thread = mock_chat_repository.save.call_args[0][0]
        # Should have 2 messages: new user message + assistant reply
        assert len(saved_thread.messages) == 2

    @pytest.mark.asyncio
    async def test_clear_thread_success(
        self,
        service,
        mock_chat_repository,
        mock_novel_repository
    ):
        """测试清空线程"""
        novel = Novel(
            id=NovelId("test-novel"),
            title="测试小说",
            author="作者",
            target_chapters=10
        )
        mock_novel_repository.get_by_id.return_value = novel

        thread = ChatThread.create("test-novel")
        thread.add_message(ChatMessage.create_user_message("Message"))
        mock_chat_repository.get_by_novel_id.return_value = thread

        await service.clear_thread("test-novel")

        mock_chat_repository.save.assert_called_once()
        saved_thread = mock_chat_repository.save.call_args[0][0]
        assert len(saved_thread.messages) == 0

    @pytest.mark.asyncio
    async def test_clear_thread_novel_not_found(
        self,
        service,
        mock_novel_repository
    ):
        """测试清空线程时小说不存在"""
        mock_novel_repository.get_by_id.return_value = None

        with pytest.raises(EntityNotFoundError):
            await service.clear_thread("nonexistent")
