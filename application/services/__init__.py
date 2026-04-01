"""应用层服务"""
from application.services.novel_service import NovelService
from application.services.indexing_service import IndexingService
from application.services.character_indexer import CharacterIndexer

__all__ = ["NovelService", "IndexingService", "CharacterIndexer"]
