"""基于文件的 Storyline 仓储实现"""
import logging
from typing import Optional, List
from domain.novel.entities.storyline import Storyline
from domain.novel.value_objects.novel_id import NovelId
from domain.novel.repositories.storyline_repository import StorylineRepository
from infrastructure.persistence.storage.backend import StorageBackend
from infrastructure.persistence.mappers.storyline_mapper import StorylineMapper

logger = logging.getLogger(__name__)


class FileStorylineRepository(StorylineRepository):
    """基于文件系统的 Storyline 仓储实现

    使用 JSON 文件存储故事线数据。
    文件路径格式: storylines/{novel_id}_{storyline_id}.json
    """

    def __init__(self, storage: StorageBackend):
        """初始化仓储

        Args:
            storage: 存储后端
        """
        self.storage = storage

    def _get_path(self, novel_id: str, storyline_id: str) -> str:
        """获取故事线文件路径

        Args:
            novel_id: 小说 ID
            storyline_id: 故事线 ID

        Returns:
            文件路径
        """
        return f"storylines/{novel_id}_{storyline_id}.json"

    def save(self, storyline: Storyline) -> None:
        """保存故事线"""
        path = self._get_path(storyline.novel_id.value, storyline.id)
        data = StorylineMapper.to_dict(storyline)
        self.storage.write_json(path, data)

    def get_by_id(self, storyline_id: str) -> Optional[Storyline]:
        """根据 ID 获取故事线

        由于文件名包含 novel_id，需要搜索所有匹配的文件
        """
        # Search for files matching the pattern *_{storyline_id}.json
        pattern = f"storylines/*_{storyline_id}.json"
        matching_files = self.storage.list_files(pattern)

        if not matching_files:
            return None

        # Read the first matching file
        data = self.storage.read_json(matching_files[0])
        return StorylineMapper.from_dict(data)

    def get_by_novel_id(self, novel_id: NovelId) -> List[Storyline]:
        """根据小说 ID 获取所有故事线"""
        pattern = f"storylines/{novel_id.value}_*.json"
        matching_files = self.storage.list_files(pattern)

        storylines = []
        for file_path in matching_files:
            data = self.storage.read_json(file_path)
            storyline = StorylineMapper.from_dict(data)
            storylines.append(storyline)

        return storylines

    def delete(self, storyline_id: str) -> None:
        """删除故事线"""
        # Search for files matching the pattern *_{storyline_id}.json
        pattern = f"storylines/*_{storyline_id}.json"
        matching_files = self.storage.list_files(pattern)

        for file_path in matching_files:
            self.storage.delete(file_path)
