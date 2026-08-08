"""
Metadata Module

This module provides metadata definitions for the Knowledge package.

Purpose
-------
Provide metadata management and operations.

Responsibilities
----------------
- Define metadata structure
- Support metadata operations
- Support metadata validation
- Support metadata serialization

Dependencies
------------
typing (standard library)
datetime (standard library)
quantsmind.knowledge.enums (knowledge enumerations)
quantsmind.knowledge.exceptions (knowledge exceptions)
quantsmind.knowledge.interfaces (knowledge interfaces)
quantsmind.knowledge.types (knowledge types)
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from quantsmind.knowledge.enums import MetadataType
from quantsmind.knowledge.exceptions import MetadataError
from quantsmind.knowledge.interfaces import IMetadata
from quantsmind.knowledge.types import (
    MetadataDict,
    MetadataKey,
    MetadataValue,
)


class KnowledgeMetadata(IMetadata):
    """Concrete implementation of knowledge metadata.

    This class provides metadata functionality.

    Attributes:
        _data: Metadata data
        _metadata_type: Metadata type
        _created_at: Creation timestamp
        _updated_at: Update timestamp

    Example:
        >>> metadata = KnowledgeMetadata({"key": "value"})
        >>> metadata.get("key")
    """

    def __init__(
        self,
        data: Optional[MetadataDict] = None,
        metadata_type: MetadataType = MetadataType.CUSTOM,
    ) -> None:
        """Initialize KnowledgeMetadata.

        Args:
            data: Metadata data
            metadata_type: Metadata type

        Example:
            >>> metadata = KnowledgeMetadata({"key": "value"})
        """
        self._data: MetadataDict = data or {}
        self._metadata_type = metadata_type
        self._created_at = datetime.utcnow()
        self._updated_at = datetime.utcnow()

    @property
    def metadata_type(self) -> MetadataType:
        """Get the metadata type.

        Returns:
            Metadata type

        Example:
            >>> mtype = metadata.metadata_type
        """
        return self._metadata_type

    @property
    def created_at(self) -> datetime:
        """Get the creation timestamp.

        Returns:
            Creation timestamp

        Example:
            >>> created = metadata.created_at
        """
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        """Get the update timestamp.

        Returns:
            Update timestamp

        Example:
            >>> updated = metadata.updated_at
        """
        return self._updated_at

    def get(self, key: MetadataKey, default: Any = None) -> Any:
        """Get a metadata value.

        Args:
            key: Metadata key
            default: Default value

        Returns:
            Metadata value or default

        Example:
            >>> value = metadata.get("key")
        """
        return self._data.get(key, default)

    def set(self, key: MetadataKey, value: MetadataValue) -> None:
        """Set a metadata value.

        Args:
            key: Metadata key
            value: Metadata value

        Example:
            >>> metadata.set("key", "value")
        """
        self._data[key] = value
        self._updated_at = datetime.utcnow()

    def update(self, data: MetadataDict) -> None:
        """Update metadata.

        Args:
            data: Metadata data

        Example:
            >>> metadata.update({"key": "value"})
        """
        self._data.update(data)
        self._updated_at = datetime.utcnow()

    def delete(self, key: MetadataKey) -> bool:
        """Delete a metadata value.

        Args:
            key: Metadata key

        Returns:
            True if deleted

        Example:
            >>> deleted = metadata.delete("key")
        """
        if key in self._data:
            del self._data[key]
            self._updated_at = datetime.utcnow()
            return True
        return False

    def has(self, key: MetadataKey) -> bool:
        """Check if metadata key exists.

        Args:
            key: Metadata key

        Returns:
            True if key exists

        Example:
            >>> if metadata.has("key"):
            ...     print("Key exists")
        """
        return key in self._data

    def keys(self) -> List[MetadataKey]:
        """Get all metadata keys.

        Returns:
            List of keys

        Example:
            >>> keys = metadata.keys()
        """
        return list(self._data.keys())

    def values(self) -> List[MetadataValue]:
        """Get all metadata values.

        Returns:
            List of values

        Example:
            >>> values = metadata.values()
        """
        return list(self._data.values())

    def items(self) -> List[tuple[MetadataKey, MetadataValue]]:
        """Get all metadata items.

        Returns:
            List of (key, value) tuples

        Example:
            >>> items = metadata.items()
        """
        return list(self._data.items())

    def clear(self) -> None:
        """Clear all metadata.

        Example:
            >>> metadata.clear()
        """
        self._data.clear()
        self._updated_at = datetime.utcnow()

    def merge(self, other: IMetadata) -> None:
        """Merge with another metadata.

        Args:
            other: Other metadata

        Example:
            >>> metadata.merge(other_metadata)
        """
        self.update(other.to_dict())

    def copy(self) -> "KnowledgeMetadata":
        """Create a copy of the metadata.

        Returns:
            Copy of metadata

        Example:
            >>> copy = metadata.copy()
        """
        return KnowledgeMetadata(self._data.copy(), self._metadata_type)

    def to_dict(self) -> MetadataDict:
        """Convert to dictionary.

        Returns:
            Metadata dictionary

        Example:
            >>> data = metadata.to_dict()
        """
        return self._data.copy()

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(metadata)
        """
        return f"KnowledgeMetadata(type={self._metadata_type.value}, keys={len(self._data)}, created={self._created_at.isoformat()})"


# Export
__all__ = [
    "KnowledgeMetadata",
]
