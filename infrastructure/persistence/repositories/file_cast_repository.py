"""File-based Cast repository implementation"""
import logging
from typing import Optional
from pathlib import Path
from domain.cast.aggregates.cast_graph import CastGraph
from domain.cast.repositories.cast_repository import CastRepository
from domain.novel.value_objects.novel_id import NovelId
from infrastructure.persistence.storage.backend import StorageBackend
from infrastructure.persistence.mappers.cast_mapper import CastMapper

logger = logging.getLogger(__name__)


class FileCastRepository(CastRepository):
    """File-based Cast repository implementation

    Stores cast graphs as JSON files in output/novels/{slug}/cast_graph.json
    """

    def __init__(self, storage: StorageBackend):
        """Initialize repository

        Args:
            storage: Storage backend
        """
        self.storage = storage

    def _get_path(self, novel_id: NovelId) -> str:
        """Get cast graph file path

        Args:
            novel_id: Novel ID

        Returns:
            File path
        """
        return f"novels/{novel_id.value}/cast_graph.json"

    def save(self, cast_graph: CastGraph) -> None:
        """Save cast graph

        Args:
            cast_graph: Cast graph to save
        """
        path = self._get_path(cast_graph.novel_id)
        data = CastMapper.to_dict(cast_graph)
        self.storage.write_json(path, data)
        logger.info(f"Saved cast graph for novel {cast_graph.novel_id.value}")

    def get_by_novel_id(self, novel_id: NovelId) -> Optional[CastGraph]:
        """Get cast graph by novel ID

        Args:
            novel_id: Novel ID

        Returns:
            Cast graph if found, None otherwise
        """
        path = self._get_path(novel_id)

        if not self.storage.exists(path):
            logger.debug(f"Cast graph not found for novel {novel_id.value}")
            return None

        try:
            data = self.storage.read_json(path)
            cast_graph = CastMapper.from_dict(data, novel_id.value)
            logger.info(f"Loaded cast graph for novel {novel_id.value}")
            return cast_graph
        except Exception as e:
            logger.warning(f"Failed to load cast graph from {path}: {str(e)}")
            return None

    def delete(self, novel_id: NovelId) -> None:
        """Delete cast graph by novel ID

        Args:
            novel_id: Novel ID
        """
        path = self._get_path(novel_id)
        self.storage.delete(path)
        logger.info(f"Deleted cast graph for novel {novel_id.value}")

    def exists(self, novel_id: NovelId) -> bool:
        """Check if cast graph exists for novel

        Args:
            novel_id: Novel ID

        Returns:
            True if exists, False otherwise
        """
        path = self._get_path(novel_id)
        return self.storage.exists(path)
