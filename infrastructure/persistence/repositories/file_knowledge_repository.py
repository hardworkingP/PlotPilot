"""File-based Knowledge repository implementation"""
import logging
from typing import Optional
from domain.knowledge.story_knowledge import StoryKnowledge
from domain.knowledge.chapter_summary import ChapterSummary
from domain.knowledge.knowledge_triple import KnowledgeTriple
from domain.knowledge.repositories.knowledge_repository import KnowledgeRepository
from infrastructure.persistence.storage.backend import StorageBackend

logger = logging.getLogger(__name__)


class FileKnowledgeRepository(KnowledgeRepository):
    """基于文件系统的知识仓储实现

    使用 novel_knowledge.json 文件存储知识图谱数据
    """

    def __init__(self, storage: StorageBackend):
        """初始化仓储

        Args:
            storage: 存储后端
        """
        self.storage = storage

    def _get_path(self, novel_id: str) -> str:
        """获取知识文件路径

        Args:
            novel_id: 小说ID

        Returns:
            文件路径
        """
        return f"novels/{novel_id}/novel_knowledge.json"

    def get_by_novel_id(self, novel_id: str) -> Optional[StoryKnowledge]:
        """根据小说ID获取知识图谱"""
        path = self._get_path(novel_id)

        if not self.storage.exists(path):
            return None

        try:
            data = self.storage.read_json(path)
            return self._from_dict(novel_id, data)
        except Exception as e:
            logger.error(f"Failed to load knowledge for {novel_id}: {str(e)}")
            return None

    def save(self, knowledge: StoryKnowledge) -> None:
        """保存知识图谱"""
        path = self._get_path(knowledge.novel_id)
        data = self._to_dict(knowledge)
        self.storage.write_json(path, data)

    def exists(self, novel_id: str) -> bool:
        """检查知识图谱是否存在"""
        path = self._get_path(novel_id)
        return self.storage.exists(path)

    def delete(self, novel_id: str) -> None:
        """删除知识图谱"""
        path = self._get_path(novel_id)
        if self.storage.exists(path):
            self.storage.delete(path)

    def _to_dict(self, knowledge: StoryKnowledge) -> dict:
        """将领域对象转换为字典

        Args:
            knowledge: 故事知识

        Returns:
            字典表示
        """
        return {
            "version": knowledge.version,
            "premise_lock": knowledge.premise_lock,
            "chapters": [
                {
                    "chapter_id": ch.chapter_id,
                    "summary": ch.summary,
                    "key_events": ch.key_events,
                    "open_threads": ch.open_threads,
                    "consistency_note": ch.consistency_note,
                    "beat_sections": ch.beat_sections,
                    "sync_status": ch.sync_status
                }
                for ch in knowledge.chapters
            ],
            "facts": [
                {
                    "id": fact.id,
                    "subject": fact.subject,
                    "predicate": fact.predicate,
                    "object": fact.object,
                    "chapter_id": fact.chapter_id,
                    "note": fact.note
                }
                for fact in knowledge.facts
            ]
        }

    def _from_dict(self, novel_id: str, data: dict) -> StoryKnowledge:
        """从字典创建领域对象

        Args:
            novel_id: 小说ID
            data: 字典数据

        Returns:
            故事知识
        """
        chapters = [
            ChapterSummary(
                chapter_id=ch["chapter_id"],
                summary=ch.get("summary", ""),
                key_events=ch.get("key_events", ""),
                open_threads=ch.get("open_threads", ""),
                consistency_note=ch.get("consistency_note", ""),
                beat_sections=ch.get("beat_sections", []),
                sync_status=ch.get("sync_status", "draft")
            )
            for ch in data.get("chapters", [])
        ]

        facts = [
            KnowledgeTriple(
                id=fact["id"],
                subject=fact.get("subject", ""),
                predicate=fact.get("predicate", ""),
                object=fact.get("object", ""),
                chapter_id=fact.get("chapter_id"),
                note=fact.get("note", "")
            )
            for fact in data.get("facts", [])
        ]

        return StoryKnowledge(
            novel_id=novel_id,
            version=data.get("version", 1),
            premise_lock=data.get("premise_lock", ""),
            chapters=chapters,
            facts=facts
        )
