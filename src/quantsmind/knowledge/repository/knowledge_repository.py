"""
Knowledge Repository Module

This module provides knowledge repository definitions for the Knowledge package.

Purpose
-------
Provide knowledge repository management for comprehensive knowledge storage.

Responsibilities
----------------
- Define knowledge repository structure
- Support knowledge repository operations
- Support knowledge repository validation
- Support knowledge repository metadata

Dependencies
------------
typing (standard library)
quantsmind.knowledge.enums (knowledge enumerations)
quantsmind.knowledge.exceptions (knowledge exceptions)
quantsmind.knowledge.interfaces (knowledge interfaces)
quantsmind.knowledge.types (knowledge types)
"""

from __future__ import annotations

from typing import Any

from quantsmind.knowledge.enums import RepositoryType
from quantsmind.knowledge.exceptions import RepositoryError
from quantsmind.knowledge.interfaces import IRepository
from quantsmind.knowledge.types import ValidationResult


class KnowledgeRepository(IRepository):
    """Concrete implementation of a knowledge repository.

    This class provides knowledge repository functionality for comprehensive knowledge storage.

    Attributes:
        _id: Repository ID
        _name: Repository name
        _repository_type: Repository type
        _knowledge_items: Knowledge items
        _schemas: Schemas
        _ontologies: Ontologies
        _metadata: Repository metadata

    Example:
        >>> repo = KnowledgeRepository("krepo_001", "Knowledge Repository")
        >>> repo.add_knowledge("item_001", {"data": "value"})
    """

    def __init__(
        self,
        repository_id: str,
        name: str,
        repository_type: RepositoryType = RepositoryType.MEMORY,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a KnowledgeRepository.

        Args:
            repository_id: Repository ID
            name: Repository name
            repository_type: Repository type
            metadata: Repository metadata

        Example:
            >>> repo = KnowledgeRepository("krepo_001", "Knowledge Repository")
        """
        if not repository_id:
            raise RepositoryError("Repository ID cannot be empty", {"repository_id": repository_id})

        if not name:
            raise RepositoryError("Repository name cannot be empty", {"name": name})

        self._id = repository_id
        self._name = name
        self._repository_type = repository_type
        self._knowledge_items: dict[str, Any] = {}
        self._schemas: dict[str, Any] = {}
        self._ontologies: dict[str, Any] = {}
        self._metadata = metadata or {}

    @property
    def id(self) -> str:
        """Get the repository ID.

        Returns:
            Repository ID

        Example:
            >>> rid = repo.id
        """
        return self._id

    @property
    def name(self) -> str:
        """Get the repository name.

        Returns:
            Repository name

        Example:
            >>> name = repo.name
        """
        return self._name

    @property
    def repository_type(self) -> RepositoryType:
        """Get the repository type.

        Returns:
            Repository type

        Example:
            >>> rtype = repo.repository_type
        """
        return self._repository_type

    @property
    def metadata(self) -> dict[str, Any]:
        """Get the repository metadata.

        Returns:
            Repository metadata

        Example:
            >>> metadata = repo.metadata
        """
        return self._metadata.copy()

    def add_knowledge(self, item_id: str, item: Any) -> None:
        """Add a knowledge item to the repository.

        Args:
            item_id: Item ID
            item: Knowledge item

        Example:
            >>> repo.add_knowledge("item_001", {"data": "value"})
        """
        self._knowledge_items[item_id] = item

    def remove_knowledge(self, item_id: str) -> bool:
        """Remove a knowledge item from the repository.

        Args:
            item_id: Item ID

        Returns:
            True if removed

        Example:
            >>> removed = repo.remove_knowledge("item_001")
        """
        if item_id in self._knowledge_items:
            del self._knowledge_items[item_id]
            return True
        return False

    def get_knowledge(self, item_id: str) -> Any | None:
        """Get a knowledge item from the repository.

        Args:
            item_id: Item ID

        Returns:
            Knowledge item or None

        Example:
            >>> item = repo.get_knowledge("item_001")
        """
        return self._knowledge_items.get(item_id)

    def add_schema(self, schema_id: str, schema: Any) -> None:
        """Add a schema to the repository.

        Args:
            schema_id: Schema ID
            schema: Schema definition

        Example:
            >>> repo.add_schema("schema_001", {"fields": ["name", "value"]})
        """
        self._schemas[schema_id] = schema

    def remove_schema(self, schema_id: str) -> bool:
        """Remove a schema from the repository.

        Args:
            schema_id: Schema ID

        Returns:
            True if removed

        Example:
            >>> removed = repo.remove_schema("schema_001")
        """
        if schema_id in self._schemas:
            del self._schemas[schema_id]
            return True
        return False

    def get_schema(self, schema_id: str) -> Any | None:
        """Get a schema from the repository.

        Args:
            schema_id: Schema ID

        Returns:
            Schema or None

        Example:
            >>> schema = repo.get_schema("schema_001")
        """
        return self._schemas.get(schema_id)

    def add_ontology(self, ontology_id: str, ontology: Any) -> None:
        """Add an ontology to the repository.

        Args:
            ontology_id: Ontology ID
            ontology: Ontology definition

        Example:
            >>> repo.add_ontology("ontology_001", {"concepts": ["Person", "Organization"]})
        """
        self._ontologies[ontology_id] = ontology

    def remove_ontology(self, ontology_id: str) -> bool:
        """Remove an ontology from the repository.

        Args:
            ontology_id: Ontology ID

        Returns:
            True if removed

        Example:
            >>> removed = repo.remove_ontology("ontology_001")
        """
        if ontology_id in self._ontologies:
            del self._ontologies[ontology_id]
            return True
        return False

    def get_ontology(self, ontology_id: str) -> Any | None:
        """Get an ontology from the repository.

        Args:
            ontology_id: Ontology ID

        Returns:
            Ontology or None

        Example:
            >>> ontology = repo.get_ontology("ontology_001")
        """
        return self._ontologies.get(ontology_id)

    def add(self, item_id: str, item: Any) -> None:
        """Add an item to the repository (alias for add_knowledge).

        Args:
            item_id: Item ID
            item: Item to add

        Example:
            >>> repo.add("item_001", {"data": "value"})
        """
        self.add_knowledge(item_id, item)

    def remove(self, item_id: str) -> bool:
        """Remove an item from the repository.

        Args:
            item_id: Item ID

        Returns:
            True if removed

        Example:
            >>> removed = repo.remove("item_001")
        """
        return self.remove_knowledge(item_id)

    def get(self, item_id: str) -> Any | None:
        """Get an item from the repository.

        Args:
            item_id: Item ID

        Returns:
            Item or None

        Example:
            >>> item = repo.get("item_001")
        """
        return self.get_knowledge(item_id)

    def list_all(self) -> list[str]:
        """List all knowledge item IDs.

        Returns:
            List of item IDs

        Example:
            >>> items = repo.list_all()
        """
        return list(self._knowledge_items.keys())

    def count(self) -> int:
        """Get the number of knowledge items.

        Returns:
            Number of items

        Example:
            >>> count = repo.count()
        """
        return len(self._knowledge_items)

    def clear(self) -> None:
        """Clear all items from the repository.

        Example:
            >>> repo.clear()
        """
        self._knowledge_items.clear()
        self._schemas.clear()
        self._ontologies.clear()

    def validate(self) -> ValidationResult:
        """Validate the knowledge repository.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = repo.validate()
        """
        errors = []

        if not self._id:
            errors.append("Repository ID cannot be empty")

        if not self._name:
            errors.append("Repository name cannot be empty")

        return (len(errors) == 0, errors)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Repository definition

        Example:
            >>> data = repo.to_dict()
        """
        return {
            "id": self._id,
            "name": self._name,
            "repository_type": self._repository_type.value,
            "knowledge_count": len(self._knowledge_items),
            "schema_count": len(self._schemas),
            "ontology_count": len(self._ontologies),
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(repo)
        """
        return f"KnowledgeRepository(id={self._id}, name={self._name}, knowledge={len(self._knowledge_items)}, schemas={len(self._schemas)}, ontologies={len(self._ontologies)})"


# Export
__all__ = [
    "KnowledgeRepository",
]
