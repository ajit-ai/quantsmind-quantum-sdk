"""
Repository Module

This module provides repository definitions for the Knowledge package.

Purpose
-------
Provide repository management for knowledge storage and retrieval.

Responsibilities
----------------
- Define repository structure
- Support repository operations
- Support repository validation
- Support repository metadata

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
from quantsmind.knowledge.interfaces import IRepository
from quantsmind.knowledge.types import ValidationResult


class Repository(IRepository):
    """Concrete implementation of a repository.

    This class provides repository functionality for knowledge storage.

    Attributes:
        _id: Repository ID
        _name: Repository name
        _repository_type: Repository type
        _items: Stored items
        _metadata: Repository metadata

    Example:
        >>> repository = Repository("repo_001", "Knowledge Repository", RepositoryType.MEMORY)
        >>> repository.add("item_001", {"data": "value"})
    """

    def __init__(
        self,
        repository_id: str,
        name: str,
        repository_type: RepositoryType,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a Repository.

        Args:
            repository_id: Repository ID
            name: Repository name
            repository_type: Repository type
            metadata: Repository metadata

        Example:
            >>> repository = Repository("repo_001", "Knowledge Repository", RepositoryType.MEMORY)
        """
        self._id = repository_id
        self._name = name
        self._repository_type = repository_type
        self._items: dict[str, Any] = {}
        self._metadata = metadata or {}

    @property
    def id(self) -> str:
        """Get the repository ID.

        Returns:
            Repository ID

        Example:
            >>> rid = repository.id
        """
        return self._id

    @property
    def name(self) -> str:
        """Get the repository name.

        Returns:
            Repository name

        Example:
            >>> name = repository.name
        """
        return self._name

    @property
    def repository_type(self) -> RepositoryType:
        """Get the repository type.

        Returns:
            Repository type

        Example:
            >>> rtype = repository.repository_type
        """
        return self._repository_type

    @property
    def metadata(self) -> dict[str, Any]:
        """Get the repository metadata.

        Returns:
            Repository metadata

        Example:
            >>> metadata = repository.metadata
        """
        return self._metadata.copy()

    def add(self, item_id: str, item: Any) -> None:
        """Add an item to the repository.

        Args:
            item_id: Item ID
            item: Item to add

        Example:
            >>> repository.add("item_001", {"data": "value"})
        """
        self._items[item_id] = item

    def remove(self, item_id: str) -> bool:
        """Remove an item from the repository.

        Args:
            item_id: Item ID

        Returns:
            True if removed

        Example:
            >>> removed = repository.remove("item_001")
        """
        if item_id in self._items:
            del self._items[item_id]
            return True
        return False

    def get(self, item_id: str) -> Any | None:
        """Get an item from the repository.

        Args:
            item_id: Item ID

        Returns:
            Item or None

        Example:
            >>> item = repository.get("item_001")
        """
        return self._items.get(item_id)

    def list_all(self) -> list[str]:
        """List all item IDs.

        Returns:
            List of item IDs

        Example:
            >>> items = repository.list_all()
        """
        return list(self._items.keys())

    def count(self) -> int:
        """Get the number of items.

        Returns:
            Number of items

        Example:
            >>> count = repository.count()
        """
        return len(self._items)

    def clear(self) -> None:
        """Clear all items from the repository.

        Example:
            >>> repository.clear()
        """
        self._items.clear()

    def validate(self) -> ValidationResult:
        """Validate the repository.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = repository.validate()
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
            >>> data = repository.to_dict()
        """
        return {
            "id": self._id,
            "name": self._name,
            "repository_type": self._repository_type.value,
            "item_count": len(self._items),
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(repository)
        """
        return f"Repository(id={self._id}, name={self._name}, type={self._repository_type.value}, items={len(self._items)})"


# Export
__all__ = [
    "Repository",
]
