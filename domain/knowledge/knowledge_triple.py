"""Knowledge Triple entity"""
from typing import Optional
from domain.shared.base_entity import BaseEntity


class KnowledgeTriple(BaseEntity):
    """知识三元组实体

    表示一个知识事实：主语-谓词-宾语
    """

    def __init__(
        self,
        id: str,
        subject: str,
        predicate: str,
        object: str,
        chapter_id: Optional[int] = None,
        note: str = ""
    ):
        """初始化知识三元组

        Args:
            id: 三元组唯一标识
            subject: 主语
            predicate: 谓词/关系
            object: 宾语
            chapter_id: 关联章节号
            note: 备注说明
        """
        super().__init__(id)
        self.subject = subject
        self.predicate = predicate
        self.object = object
        self.chapter_id = chapter_id
        self.note = note

    def __repr__(self) -> str:
        return f"<KnowledgeTriple {self.id}: {self.subject} -> {self.predicate} -> {self.object}>"
