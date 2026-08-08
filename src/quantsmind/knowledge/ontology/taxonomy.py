"""
Taxonomy Module

This module provides taxonomy definitions for the Knowledge package.

Purpose
-------
Provide taxonomy management for ontologies.

Responsibilities
----------------
- Define taxonomy structure
- Support taxonomy operations
- Support taxonomy validation
- Support taxonomy hierarchy

Dependencies
------------
typing (standard library)
quantsmind.knowledge.enums (knowledge enumerations)
quantsmind.knowledge.exceptions (knowledge exceptions)
quantsmind.knowledge.types (knowledge types)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from quantsmind.knowledge.enums import OntologyType
from quantsmind.knowledge.exceptions import OntologyError
from quantsmind.knowledge.types import TaxonomyID, ValidationResult


class Taxonomy:
    """Concrete implementation of a taxonomy.

    This class provides taxonomy functionality.

    Attributes:
        _id: Taxonomy ID
        _name: Taxonomy name
        _root: Root concept ID
        _levels: Taxonomy levels
        _description: Taxonomy description
        _metadata: Taxonomy metadata

    Example:
        >>> taxonomy = Taxonomy("taxonomy_001", "Biological Classification")
        >>> taxonomy.name
    """

    def __init__(
        self,
        taxonomy_id: TaxonomyID,
        name: str,
        root: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a Taxonomy.

        Args:
            taxonomy_id: Taxonomy ID
            name: Taxonomy name
            root: Root concept ID
            description: Taxonomy description
            metadata: Taxonomy metadata

        Example:
            >>> taxonomy = Taxonomy("taxonomy_001", "Biological Classification")
        """
        if not taxonomy_id:
            raise OntologyError("Taxonomy ID cannot be empty")

        if not name:
            raise OntologyError("Taxonomy name cannot be empty")

        self._id = taxonomy_id
        self._name = name
        self._root = root
        self._levels: List[List[str]] = []
        self._description = description
        self._metadata = metadata or {}

    @property
    def id(self) -> TaxonomyID:
        """Get the taxonomy ID.

        Returns:
            Taxonomy ID

        Example:
            >>> tid = taxonomy.id
        """
        return self._id

    @property
    def name(self) -> str:
        """Get the taxonomy name.

        Returns:
            Taxonomy name

        Example:
            >>> name = taxonomy.name
        """
        return self._name

    @property
    def root(self) -> Optional[str]:
        """Get the root concept ID.

        Returns:
            Root concept ID

        Example:
            >>> root = taxonomy.root
        """
        return self._root

    @property
    def levels(self) -> List[List[str]]:
        """Get the taxonomy levels.

        Returns:
            List of levels, each containing concept IDs

        Example:
            >>> levels = taxonomy.levels
        """
        return [level.copy() for level in self._levels]

    @property
    def description(self) -> Optional[str]:
        """Get the taxonomy description.

        Returns:
            Taxonomy description

        Example:
            >>> description = taxonomy.description
        """
        return self._description

    @property
    def metadata(self) -> Dict[str, Any]:
        """Get the taxonomy metadata.

        Returns:
            Taxonomy metadata

        Example:
            >>> metadata = taxonomy.metadata
        """
        return self._metadata.copy()

    def set_root(self, root: str) -> None:
        """Set the root concept.

        Args:
            root: Root concept ID

        Example:
            >>> taxonomy.set_root("root_001")
        """
        self._root = root

    def add_level(self, level: List[str]) -> None:
        """Add a level to the taxonomy.

        Args:
            level: List of concept IDs at this level

        Example:
            >>> taxonomy.add_level(["kingdom_001", "kingdom_002"])
        """
        self._levels.append(level)

    def get_level(self, level_index: int) -> Optional[List[str]]:
        """Get a specific level.

        Args:
            level_index: Level index

        Returns:
            List of concept IDs or None

        Example:
            >>> level = taxonomy.get_level(0)
        """
        if 0 <= level_index < len(self._levels):
            return self._levels[level_index].copy()
        return None

    def get_depth(self) -> int:
        """Get the depth of the taxonomy.

        Returns:
            Number of levels

        Example:
            >>> depth = taxonomy.get_depth()
        """
        return len(self._levels)

    def get_concept_level(self, concept_id: str) -> Optional[int]:
        """Get the level of a concept.

        Args:
            concept_id: Concept ID

        Returns:
            Level index or None

        Example:
            >>> level = taxonomy.get_concept_level("concept_001")
        """
        for i, level in enumerate(self._levels):
            if concept_id in level:
                return i
        return None

    def get_parent(self, concept_id: str) -> Optional[str]:
        """Get the parent of a concept.

        Args:
            concept_id: Concept ID

        Returns:
            Parent concept ID or None

        Example:
            >>> parent = taxonomy.get_parent("concept_001")
        """
        level = self.get_concept_level(concept_id)
        if level is None or level == 0:
            return None

        # Find parent in previous level
        parent_level = self._levels[level - 1]
        # This is a simplified implementation - real implementation would track parent-child relationships
        return parent_level[0] if parent_level else None

    def get_children(self, concept_id: str) -> List[str]:
        """Get the children of a concept.

        Args:
            concept_id: Concept ID

        Returns:
            List of child concept IDs

        Example:
            >>> children = taxonomy.get_children("concept_001")
        """
        level = self.get_concept_level(concept_id)
        if level is None or level >= len(self._levels) - 1:
            return []

        # Return next level as children (simplified)
        return self._levels[level + 1].copy()

    def validate(self) -> ValidationResult:
        """Validate the taxonomy.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = taxonomy.validate()
        """
        errors = []

        if not self._id:
            errors.append("Taxonomy ID cannot be empty")

        if not self._name:
            errors.append("Taxonomy name cannot be empty")

        if not self._root and self._levels:
            errors.append("Taxonomy with levels must have a root")

        return (len(errors) == 0, errors)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Taxonomy definition

        Example:
            >>> data = taxonomy.to_dict()
        """
        return {
            "id": self._id,
            "name": self._name,
            "root": self._root,
            "levels": self._levels,
            "depth": len(self._levels),
            "description": self._description,
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(taxonomy)
        """
        return f"Taxonomy(id={self._id}, name={self._name}, depth={len(self._levels)})"


# Export
__all__ = [
    "Taxonomy",
]
