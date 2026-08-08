"""
Index Module

This module provides index definitions for the Knowledge package.

Purpose
-------
Provide index management for efficient data retrieval.

Responsibilities
----------------
- Define index structure
- Support index operations
- Support index validation
- Support index metadata

Dependencies
------------
typing (standard library)
quantsmind.knowledge.enums (knowledge enumerations)
quantsmind.knowledge.exceptions (knowledge exceptions)
quantsmind.knowledge.types (knowledge types)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from quantsmind.knowledge.enums import IndexType
from quantsmind.knowledge.exceptions import IndexError
from quantsmind.knowledge.types import ValidationResult


class Index:
    """Concrete implementation of an index.

    This class provides index functionality for efficient data retrieval.

    Attributes:
        _id: Index ID
        _name: Index name
        _index_type: Index type
        _field: Indexed field
        _index_data: Index data structure
        _metadata: Index metadata

    Example:
        >>> index = Index("index_001", "name_index", IndexType.HASH, "name")
        >>> index.add("entity_001", {"name": "test"})
    """

    def __init__(
        self,
        index_id: str,
        name: str,
        index_type: IndexType,
        field: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize an Index.

        Args:
            index_id: Index ID
            name: Index name
            index_type: Index type
            field: Indexed field
            metadata: Index metadata

        Example:
            >>> index = Index("index_001", "name_index", IndexType.HASH, "name")
        """
        if not index_id:
            raise IndexError("Index ID cannot be empty", {"index_id": index_id})

        if not name:
            raise IndexError("Index name cannot be empty", {"name": name})

        if not field:
            raise IndexError("Field cannot be empty", {"field": field})

        self._id = index_id
        self._name = name
        self._index_type = index_type
        self._field = field
        self._index_data: Dict[str, List[str]] = {}
        self._metadata = metadata or {}

    @property
    def id(self) -> str:
        """Get the index ID.

        Returns:
            Index ID

        Example:
            >>> iid = index.id
        """
        return self._id

    @property
    def name(self) -> str:
        """Get the index name.

        Returns:
            Index name

        Example:
            >>> name = index.name
        """
        return self._name

    @property
    def index_type(self) -> IndexType:
        """Get the index type.

        Returns:
            Index type

        Example:
            >>> itype = index.index_type
        """
        return self._index_type

    @property
    def field(self) -> str:
        """Get the indexed field.

        Returns:
            Indexed field

        Example:
            >>> field = index.field
        """
        return self._field

    @property
    def metadata(self) -> Dict[str, Any]:
        """Get the index metadata.

        Returns:
            Index metadata

        Example:
            >>> metadata = index.metadata
        """
        return self._metadata.copy()

    def add(self, entity_id: str, data: Dict[str, Any]) -> None:
        """Add an entity to the index.

        Args:
            entity_id: Entity ID
            data: Entity data

        Example:
            >>> index.add("entity_001", {"name": "test"})
        """
        if self._field not in data:
            return

        key = str(data[self._field])
        if key not in self._index_data:
            self._index_data[key] = []
        if entity_id not in self._index_data[key]:
            self._index_data[key].append(entity_id)

    def remove(self, entity_id: str, data: Dict[str, Any]) -> None:
        """Remove an entity from the index.

        Args:
            entity_id: Entity ID
            data: Entity data

        Example:
            >>> index.remove("entity_001", {"name": "test"})
        """
        if self._field not in data:
            return

        key = str(data[self._field])
        if key in self._index_data and entity_id in self._index_data[key]:
            self._index_data[key].remove(entity_id)
            if not self._index_data[key]:
                del self._index_data[key]

    def search(self, value: Any) -> List[str]:
        """Search for entities by value.

        Args:
            value: Value to search for

        Returns:
            List of entity IDs

        Example:
            >>> results = index.search("test")
        """
        key = str(value)
        return self._index_data.get(key, []).copy()

    def get_all_keys(self) -> List[str]:
        """Get all indexed keys.

        Returns:
            List of keys

        Example:
            >>> keys = index.get_all_keys()
        """
        return list(self._index_data.keys())

    def count(self) -> int:
        """Get the number of indexed entries.

        Returns:
            Number of entries

        Example:
            >>> count = index.count()
        """
        return len(self._index_data)

    def validate(self) -> ValidationResult:
        """Validate the index.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = index.validate()
        """
        errors = []

        if not self._id:
            errors.append("Index ID cannot be empty")

        if not self._name:
            errors.append("Index name cannot be empty")

        if not self._field:
            errors.append("Field cannot be empty")

        return (len(errors) == 0, errors)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Index definition

        Example:
            >>> data = index.to_dict()
        """
        return {
            "id": self._id,
            "name": self._name,
            "index_type": self._index_type.value,
            "field": self._field,
            "entry_count": len(self._index_data),
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(index)
        """
        return f"Index(id={self._id}, name={self._name}, type={self._index_type.value}, field={self._field}, entries={len(self._index_data)})"


# Export
__all__ = [
    "Index",
]
