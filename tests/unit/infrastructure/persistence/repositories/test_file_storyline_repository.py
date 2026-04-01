import pytest
from unittest.mock import Mock
from domain.novel.entities.storyline import Storyline
from domain.novel.value_objects.novel_id import NovelId
from domain.novel.value_objects.storyline_type import StorylineType
from domain.novel.value_objects.storyline_status import StorylineStatus
from domain.novel.value_objects.storyline_milestone import StorylineMilestone
from infrastructure.persistence.repositories.file_storyline_repository import FileStorylineRepository
from infrastructure.persistence.storage.backend import StorageBackend


class TestFileStorylineRepository:
    """FileStorylineRepository 测试"""

    def test_save_storyline(self):
        """测试保存故事线"""
        mock_storage = Mock(spec=StorageBackend)
        repo = FileStorylineRepository(mock_storage)

        novel_id = NovelId("novel-123")
        storyline = Storyline(
            id="storyline-1",
            novel_id=novel_id,
            storyline_type=StorylineType.ROMANCE,
            status=StorylineStatus.ACTIVE,
            estimated_chapter_start=5,
            estimated_chapter_end=20
        )

        repo.save(storyline)

        mock_storage.write_json.assert_called_once()
        call_args = mock_storage.write_json.call_args
        assert call_args[0][0] == "storylines/novel-123_storyline-1.json"
        assert call_args[0][1]["id"] == "storyline-1"
        assert call_args[0][1]["novel_id"] == "novel-123"

    def test_get_by_id_exists(self):
        """测试根据 ID 获取故事线 - 存在"""
        mock_storage = Mock(spec=StorageBackend)
        repo = FileStorylineRepository(mock_storage)

        mock_storage.list_files.return_value = ["storylines/novel-123_storyline-1.json"]
        mock_storage.read_json.return_value = {
            "id": "storyline-1",
            "novel_id": "novel-123",
            "storyline_type": "romance",
            "status": "active",
            "estimated_chapter_start": 5,
            "estimated_chapter_end": 20,
            "current_milestone_index": 0,
            "milestones": []
        }

        storyline = repo.get_by_id("storyline-1")

        assert storyline is not None
        assert storyline.id == "storyline-1"
        assert storyline.novel_id == NovelId("novel-123")
        assert storyline.storyline_type == StorylineType.ROMANCE

    def test_get_by_id_not_exists(self):
        """测试根据 ID 获取故事线 - 不存在"""
        mock_storage = Mock(spec=StorageBackend)
        repo = FileStorylineRepository(mock_storage)

        mock_storage.list_files.return_value = []

        storyline = repo.get_by_id("storyline-1")

        assert storyline is None

    def test_get_by_novel_id(self):
        """测试根据小说 ID 获取所有故事线"""
        mock_storage = Mock(spec=StorageBackend)
        repo = FileStorylineRepository(mock_storage)

        mock_storage.list_files.return_value = [
            "storylines/novel-123_storyline-1.json",
            "storylines/novel-123_storyline-2.json"
        ]
        mock_storage.read_json.side_effect = [
            {
                "id": "storyline-1",
                "novel_id": "novel-123",
                "storyline_type": "romance",
                "status": "active",
                "estimated_chapter_start": 5,
                "estimated_chapter_end": 20,
                "current_milestone_index": 0,
                "milestones": []
            },
            {
                "id": "storyline-2",
                "novel_id": "novel-123",
                "storyline_type": "mystery",
                "status": "active",
                "estimated_chapter_start": 1,
                "estimated_chapter_end": 30,
                "current_milestone_index": 0,
                "milestones": []
            }
        ]

        novel_id = NovelId("novel-123")
        storylines = repo.get_by_novel_id(novel_id)

        assert len(storylines) == 2
        assert storylines[0].id == "storyline-1"
        assert storylines[1].id == "storyline-2"
        mock_storage.list_files.assert_called_once_with("storylines/novel-123_*.json")

    def test_get_by_novel_id_empty(self):
        """测试根据小说 ID 获取所有故事线 - 空列表"""
        mock_storage = Mock(spec=StorageBackend)
        repo = FileStorylineRepository(mock_storage)

        mock_storage.list_files.return_value = []

        novel_id = NovelId("novel-123")
        storylines = repo.get_by_novel_id(novel_id)

        assert len(storylines) == 0

    def test_delete_storyline(self):
        """测试删除故事线"""
        mock_storage = Mock(spec=StorageBackend)
        repo = FileStorylineRepository(mock_storage)

        mock_storage.list_files.return_value = [
            "storylines/novel-123_storyline-1.json"
        ]

        repo.delete("storyline-1")

        mock_storage.delete.assert_called_once_with("storylines/novel-123_storyline-1.json")

    def test_delete_storyline_not_found(self):
        """测试删除不存在的故事线"""
        mock_storage = Mock(spec=StorageBackend)
        repo = FileStorylineRepository(mock_storage)

        mock_storage.list_files.return_value = []

        # Should not raise an error
        repo.delete("storyline-1")

        mock_storage.delete.assert_not_called()

    def test_save_storyline_with_milestones(self):
        """测试保存带有里程碑的故事线"""
        mock_storage = Mock(spec=StorageBackend)
        repo = FileStorylineRepository(mock_storage)

        novel_id = NovelId("novel-123")
        milestone = StorylineMilestone(
            order=0,
            title="First Meeting",
            description="Hero meets love interest",
            target_chapter_start=5,
            target_chapter_end=6,
            prerequisites=["intro"],
            triggers=["meet"]
        )

        storyline = Storyline(
            id="storyline-1",
            novel_id=novel_id,
            storyline_type=StorylineType.ROMANCE,
            status=StorylineStatus.ACTIVE,
            estimated_chapter_start=5,
            estimated_chapter_end=20,
            milestones=[milestone],
            current_milestone_index=0
        )

        repo.save(storyline)

        mock_storage.write_json.assert_called_once()
        call_args = mock_storage.write_json.call_args
        assert len(call_args[0][1]["milestones"]) == 1
        assert call_args[0][1]["milestones"][0]["title"] == "First Meeting"
