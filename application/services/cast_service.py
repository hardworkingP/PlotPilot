"""Cast application service"""
import logging
import re
from typing import Optional, List, Dict, Set
from pathlib import Path
from domain.cast.aggregates.cast_graph import CastGraph
from domain.cast.entities.character import Character
from domain.cast.entities.relationship import Relationship
from domain.cast.entities.story_event import StoryEvent
from domain.cast.value_objects.character_id import CharacterId
from domain.cast.value_objects.relationship_id import RelationshipId
from domain.cast.repositories.cast_repository import CastRepository
from domain.novel.value_objects.novel_id import NovelId
from domain.shared.exceptions import EntityNotFoundError
from application.dtos.cast_dto import (
    CastGraphDTO,
    CastSearchResultDTO,
    CastCoverageDTO,
    CharacterCoverageDTO,
    BibleCharacterDTO,
    QuotedTextDTO
)

logger = logging.getLogger(__name__)


class CastService:
    """Cast application service

    Handles cast graph operations including CRUD, search, and coverage analysis.
    """

    def __init__(self, cast_repository: CastRepository, storage_root: Path):
        """Initialize service

        Args:
            cast_repository: Cast repository
            storage_root: Root path for storage (e.g., ./data or ./output)
        """
        self.cast_repository = cast_repository
        self.storage_root = storage_root

    def get_cast_graph(self, novel_id: str) -> Optional[CastGraphDTO]:
        """Get cast graph for a novel

        Args:
            novel_id: Novel ID

        Returns:
            CastGraphDTO if found, None otherwise
        """
        cast_graph = self.cast_repository.get_by_novel_id(NovelId(novel_id))
        if cast_graph is None:
            return None
        return CastGraphDTO.from_domain(cast_graph)

    def update_cast_graph(self, novel_id: str, data: dict) -> CastGraphDTO:
        """Update cast graph for a novel

        Args:
            novel_id: Novel ID
            data: Cast graph data

        Returns:
            Updated CastGraphDTO

        Raises:
            ValueError: If data is invalid
        """
        # Parse and validate data
        version = data.get("version", 2)
        characters_data = data.get("characters", [])
        relationships_data = data.get("relationships", [])

        # Create domain objects
        characters = []
        for char_data in characters_data:
            story_events = [
                StoryEvent(
                    id=e["id"],
                    summary=e["summary"],
                    chapter_id=e.get("chapter_id"),
                    importance=e.get("importance", "normal")
                )
                for e in char_data.get("story_events", [])
            ]

            character = Character(
                id=CharacterId(char_data["id"]),
                name=char_data["name"],
                aliases=char_data.get("aliases", []),
                role=char_data.get("role", ""),
                traits=char_data.get("traits", ""),
                note=char_data.get("note", ""),
                story_events=story_events
            )
            characters.append(character)

        relationships = []
        for rel_data in relationships_data:
            story_events = [
                StoryEvent(
                    id=e["id"],
                    summary=e["summary"],
                    chapter_id=e.get("chapter_id"),
                    importance=e.get("importance", "normal")
                )
                for e in rel_data.get("story_events", [])
            ]

            relationship = Relationship(
                id=RelationshipId(rel_data["id"]),
                source_id=CharacterId(rel_data["source_id"]),
                target_id=CharacterId(rel_data["target_id"]),
                label=rel_data.get("label", ""),
                note=rel_data.get("note", ""),
                directed=rel_data.get("directed", True),
                story_events=story_events
            )
            relationships.append(relationship)

        # Create or update cast graph
        cast_graph = CastGraph(
            id=f"cast_{novel_id}",
            novel_id=NovelId(novel_id),
            version=version,
            characters=characters,
            relationships=relationships
        )

        # Save
        self.cast_repository.save(cast_graph)
        logger.info(f"Updated cast graph for novel {novel_id}")

        return CastGraphDTO.from_domain(cast_graph)

    def search_cast(self, novel_id: str, query: str) -> CastSearchResultDTO:
        """Search characters and relationships in cast graph

        Args:
            novel_id: Novel ID
            query: Search query

        Returns:
            CastSearchResultDTO with matching characters and relationships

        Raises:
            EntityNotFoundError: If cast graph not found
        """
        cast_graph = self.cast_repository.get_by_novel_id(NovelId(novel_id))
        if cast_graph is None:
            raise EntityNotFoundError("CastGraph", f"for novel {novel_id}")

        characters = cast_graph.search_characters(query)
        relationships = cast_graph.search_relationships(query)

        return CastSearchResultDTO.from_domain_lists(characters, relationships)

    def get_cast_coverage(self, novel_id: str) -> CastCoverageDTO:
        """Analyze cast coverage in novel chapters

        Scans chapter files to find character mentions and compares with cast graph.

        Args:
            novel_id: Novel ID

        Returns:
            CastCoverageDTO with coverage analysis

        Raises:
            EntityNotFoundError: If cast graph not found
        """
        cast_graph = self.cast_repository.get_by_novel_id(NovelId(novel_id))
        if cast_graph is None:
            raise EntityNotFoundError("CastGraph", f"for novel {novel_id}")

        # Find chapter files
        novel_path = self.storage_root / "novels" / novel_id
        chapter_files = list(novel_path.glob("chapter_*.md"))
        chapter_files_scanned = len(chapter_files)

        # Build character name index
        char_name_map: Dict[str, Character] = {}
        for char in cast_graph.characters:
            char_name_map[char.name] = char
            for alias in char.aliases:
                char_name_map[alias] = char

        # Scan chapters for character mentions
        char_mentions: Dict[str, Set[int]] = {char.id.value: set() for char in cast_graph.characters}

        for chapter_file in chapter_files:
            # Extract chapter number from filename
            match = re.search(r'chapter_(\d+)\.md', chapter_file.name)
            if not match:
                continue
            chapter_id = int(match.group(1))

            try:
                content = chapter_file.read_text(encoding='utf-8')

                # Check for character mentions
                for name, char in char_name_map.items():
                    if name in content:
                        char_mentions[char.id.value].add(chapter_id)
            except Exception as e:
                logger.warning(f"Failed to read chapter file {chapter_file}: {e}")

        # Build character coverage list
        characters_coverage = []
        for char in cast_graph.characters:
            chapter_ids = sorted(char_mentions.get(char.id.value, set()))
            characters_coverage.append(CharacterCoverageDTO(
                id=char.id.value,
                name=char.name,
                mentioned=len(chapter_ids) > 0,
                chapter_ids=chapter_ids
            ))

        # Load bible data for comparison
        bible_not_in_cast = self._analyze_bible_coverage(novel_id, cast_graph, chapter_files)

        # Find quoted text not in cast
        quoted_not_in_cast = self._analyze_quoted_text(cast_graph, chapter_files)

        return CastCoverageDTO(
            chapter_files_scanned=chapter_files_scanned,
            characters=characters_coverage,
            bible_not_in_cast=bible_not_in_cast,
            quoted_not_in_cast=quoted_not_in_cast
        )

    def _analyze_bible_coverage(
        self,
        novel_id: str,
        cast_graph: CastGraph,
        chapter_files: List[Path]
    ) -> List[BibleCharacterDTO]:
        """Analyze bible characters not in cast graph

        Args:
            novel_id: Novel ID
            cast_graph: Cast graph
            chapter_files: List of chapter files

        Returns:
            List of bible characters not in cast
        """
        bible_path = self.storage_root / "novels" / novel_id / "bible.json"
        if not bible_path.exists():
            return []

        try:
            import json
            bible_data = json.loads(bible_path.read_text(encoding='utf-8'))
            bible_characters = bible_data.get("characters", [])
        except Exception as e:
            logger.warning(f"Failed to load bible data: {e}")
            return []

        # Get cast character names
        cast_names = set()
        for char in cast_graph.characters:
            cast_names.add(char.name)
            cast_names.update(char.aliases)

        # Find bible characters not in cast
        result = []
        for bible_char in bible_characters:
            name = bible_char.get("name", "")
            if not name or name in cast_names:
                continue

            # Check if mentioned in chapters
            chapter_ids = set()
            for chapter_file in chapter_files:
                match = re.search(r'chapter_(\d+)\.md', chapter_file.name)
                if not match:
                    continue
                chapter_id = int(match.group(1))

                try:
                    content = chapter_file.read_text(encoding='utf-8')
                    if name in content:
                        chapter_ids.add(chapter_id)
                except Exception:
                    pass

            result.append(BibleCharacterDTO(
                name=name,
                role=bible_char.get("role", ""),
                in_novel_text=len(chapter_ids) > 0,
                chapter_ids=sorted(chapter_ids)
            ))

        return result

    def _analyze_quoted_text(
        self,
        cast_graph: CastGraph,
        chapter_files: List[Path]
    ) -> List[QuotedTextDTO]:
        """Analyze quoted text (「」) not matching cast characters

        Args:
            cast_graph: Cast graph
            chapter_files: List of chapter files

        Returns:
            List of quoted text not in cast
        """
        # Get cast character names
        cast_names = set()
        for char in cast_graph.characters:
            cast_names.add(char.name)
            cast_names.update(char.aliases)

        # Find quoted text in chapters
        quoted_pattern = re.compile(r'「([^」]+)」')
        quoted_mentions: Dict[str, Set[int]] = {}

        for chapter_file in chapter_files:
            match = re.search(r'chapter_(\d+)\.md', chapter_file.name)
            if not match:
                continue
            chapter_id = int(match.group(1))

            try:
                content = chapter_file.read_text(encoding='utf-8')
                for match in quoted_pattern.finditer(content):
                    text = match.group(1)
                    if text not in cast_names:
                        if text not in quoted_mentions:
                            quoted_mentions[text] = set()
                        quoted_mentions[text].add(chapter_id)
            except Exception:
                pass

        # Build result
        result = []
        for text, chapter_ids in quoted_mentions.items():
            result.append(QuotedTextDTO(
                text=text,
                count=len(chapter_ids),
                chapter_ids=sorted(chapter_ids)
            ))

        # Sort by count descending
        result.sort(key=lambda x: x.count, reverse=True)

        return result
