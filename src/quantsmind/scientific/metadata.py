"""
Metadata Module

This module provides metadata management for the Scientific package.

Purpose
-------
Provide metadata definitions and operations.

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
quantsmind.scientific.types (scientific types)
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from quantsmind.scientific.types import MetadataDict, MetadataKey, MetadataValue


class ScientificMetadata:
    """Concrete implementation of scientific metadata.

    This class provides metadata functionality.

    Attributes:
        _data: Metadata data
        _created_at: Creation timestamp
        _updated_at: Update timestamp

    Example:
        >>> metadata = ScientificMetadata()
        >>> metadata.set("author", "John Doe")
    """

    def __init__(self, data: MetadataDict | None = None) -> None:
        """Initialize a ScientificMetadata.

        Args:
            data: Initial metadata data

        Example:
            >>> metadata = ScientificMetadata()
        """
        self._data: MetadataDict = data or {}
        self._created_at = datetime.now(UTC).replace(tzinfo=None)
        self._updated_at = datetime.now(UTC).replace(tzinfo=None)

    @property
    def data(self) -> MetadataDict:
        """Get the metadata data.

        Returns:
            Metadata data

        Example:
            >>> print(f"Data: {metadata.data}")
        """
        return self._data.copy()

    @property
    def created_at(self) -> datetime:
        """Get the creation timestamp.

        Returns:
            Creation timestamp

        Example:
            >>> print(f"Created: {metadata.created_at}")
        """
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        """Get the update timestamp.

        Returns:
            Update timestamp

        Example:
            >>> print(f"Updated: {metadata.updated_at}")
        """
        return self._updated_at

    def get(self, key: MetadataKey, default: MetadataValue | None = None) -> MetadataValue | None:
        """Get a metadata value.

        Args:
            key: Metadata key
            default: Default value if key not found

        Returns:
            Metadata value or default

        Example:
            >>> value = metadata.get("author")
        """
        return self._data.get(key, default)

    def set(self, key: MetadataKey, value: MetadataValue) -> None:
        """Set a metadata value.

        Args:
            key: Metadata key
            value: Metadata value

        Example:
            >>> metadata.set("author", "John Doe")
        """
        self._data[key] = value
        self._updated_at = datetime.now(UTC).replace(tzinfo=None)

    def update(self, data: MetadataDict) -> None:
        """Update metadata with new data.

        Args:
            data: New metadata data

        Example:
            >>> metadata.update({"author": "John Doe", "date": "2024-01-01"})
        """
        self._data.update(data)
        self._updated_at = datetime.now(UTC).replace(tzinfo=None)

    def delete(self, key: MetadataKey) -> bool:
        """Delete a metadata key.

        Args:
            key: Metadata key

        Returns:
            True if deleted, False otherwise

        Example:
            >>> deleted = metadata.delete("author")
        """
        if key in self._data:
            del self._data[key]
            self._updated_at = datetime.now(UTC).replace(tzinfo=None)
            return True
        return False

    def has(self, key: MetadataKey) -> bool:
        """Check if metadata has a key.

        Args:
            key: Metadata key

        Returns:
            True if key exists, False otherwise

        Example:
            >>> if metadata.has("author"):
            ...     print("Has author")
        """
        return key in self._data

    def keys(self) -> list[MetadataKey]:
        """Get all metadata keys.

        Returns:
            List of keys

        Example:
            >>> keys = metadata.keys()
        """
        return list(self._data.keys())

    def values(self) -> list[MetadataValue]:
        """Get all metadata values.

        Returns:
            List of values

        Example:
            >>> values = metadata.values()
        """
        return list(self._data.values())

    def items(self) -> list[tuple[MetadataKey, MetadataValue]]:
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
        self._updated_at = datetime.now(UTC).replace(tzinfo=None)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Metadata dictionary

        Example:
            >>> data = metadata.to_dict()
        """
        return {
            "data": self._data.copy(),
            "created_at": self._created_at.isoformat(),
            "updated_at": self._updated_at.isoformat(),
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(metadata)
        """
        return f"ScientificMetadata(keys={len(self._data)}, created={self._created_at.isoformat()})"


# Export
__all__ = [
    "ScientificMetadata",
]
