"""
Tag Module

This module provides tag definitions for the Knowledge package.

Purpose
-------
Provide tag management for knowledge items.

Responsibilities
----------------
- Define tag structure
- Support tag operations
- Support tag validation
- Support tag metadata

Dependencies
------------
typing (standard library)
datetime (standard library)
quantsmind.knowledge.enums (knowledge enumerations)
quantsmind.knowledge.exceptions (knowledge exceptions)
quantsmind.knowledge.types (knowledge types)
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from quantsmind.knowledge.exceptions import MetadataError
from quantsmind.knowledge.types import Tag


class Tag:
    """Concrete implementation of a tag.

    This class provides tag functionality.

    Attributes:
        _name: Tag name
        _value: Tag value
        _category: Tag category
        _created_at: Creation timestamp
        _metadata: Tag metadata

    Example:
        >>> tag = Tag("important", "high", "priority")
        >>> tag.name
    """

    def __init__(
        self,
        name: str,
        value: str | None = None,
        category: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a Tag.

        Args:
            name: Tag name
            value: Tag value
            category: Tag category
            metadata: Tag metadata

        Example:
            >>> tag = Tag("important", "high", "priority")
        """
        if not name:
            raise MetadataError("Tag name cannot be empty")

        self._name = name
        self._value = value
        self._category = category
        self._created_at = datetime.now(UTC).replace(tzinfo=None)
        self._metadata = metadata or {}

    @property
    def name(self) -> str:
        """Get the tag name.

        Returns:
            Tag name

        Example:
            >>> name = tag.name
        """
        return self._name

    @property
    def value(self) -> str | None:
        """Get the tag value.

        Returns:
            Tag value

        Example:
            >>> value = tag.value
        """
        return self._value

    @property
    def category(self) -> str | None:
        """Get the tag category.

        Returns:
            Tag category

        Example:
            >>> category = tag.category
        """
        return self._category

    @property
    def created_at(self) -> datetime:
        """Get the creation timestamp.

        Returns:
            Creation timestamp

        Example:
            >>> created = tag.created_at
        """
        return self._created_at

    @property
    def metadata(self) -> dict[str, Any]:
        """Get the tag metadata.

        Returns:
            Tag metadata

        Example:
            >>> metadata = tag.metadata
        """
        return self._metadata.copy()

    def set_value(self, value: str) -> None:
        """Set the tag value.

        Args:
            value: Tag value

        Example:
            >>> tag.set_value("medium")
        """
        self._value = value

    def set_category(self, category: str) -> None:
        """Set the tag category.

        Args:
            category: Tag category

        Example:
            >>> tag.set_category("priority")
        """
        self._category = category

    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to the tag.

        Args:
            key: Metadata key
            value: Metadata value

        Example:
            >>> tag.add_metadata("color", "red")
        """
        self._metadata[key] = value

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Tag definition

        Example:
            >>> data = tag.to_dict()
        """
        return {
            "name": self._name,
            "value": self._value,
            "category": self._category,
            "created_at": self._created_at.isoformat(),
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(tag)
        """
        return f"Tag(name={self._name}, value={self._value}, category={self._category})"


class TagSet:
    """Set of tags for a knowledge item.

    This class provides tag set functionality.

    Attributes:
        _tags: Tags in the set

    Example:
        >>> tagset = TagSet()
        >>> tagset.add_tag(Tag("important"))
    """

    def __init__(self, tags: list[Tag] | None = None) -> None:
        """Initialize a TagSet.

        Args:
            tags: Initial tags

        Example:
            >>> tagset = TagSet()
        """
        self._tags: dict[str, Tag] = {}
        if tags:
            for tag in tags:
                self.add_tag(tag)

    def add_tag(self, tag: Tag) -> None:
        """Add a tag to the set.

        Args:
            tag: Tag to add

        Example:
            >>> tagset.add_tag(Tag("important"))
        """
        self._tags[tag.name] = tag

    def remove_tag(self, name: str) -> bool:
        """Remove a tag from the set.

        Args:
            name: Tag name

        Returns:
            True if removed

        Example:
            >>> removed = tagset.remove_tag("important")
        """
        if name in self._tags:
            del self._tags[name]
            return True
        return False

    def get_tag(self, name: str) -> Tag | None:
        """Get a tag by name.

        Args:
            name: Tag name

        Returns:
            Tag or None

        Example:
            >>> tag = tagset.get_tag("important")
        """
        return self._tags.get(name)

    def get_tags_by_category(self, category: str) -> list[Tag]:
        """Get tags by category.

        Args:
            category: Tag category

        Returns:
            List of tags

        Example:
            >>> tags = tagset.get_tags_by_category("priority")
        """
        return [tag for tag in self._tags.values() if tag.category == category]

    def list_all(self) -> list[Tag]:
        """List all tags.

        Returns:
            List of tags

        Example:
            >>> tags = tagset.list_all()
        """
        return list(self._tags.values())

    def count(self) -> int:
        """Get the number of tags.

        Returns:
            Number of tags

        Example:
            >>> count = tagset.count()
        """
        return len(self._tags)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Tag set definition

        Example:
            >>> data = tagset.to_dict()
        """
        return {
            "tags": [tag.to_dict() for tag in self._tags.values()],
            "count": len(self._tags),
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(tagset)
        """
        return f"TagSet(count={len(self._tags)})"


# Export
__all__ = [
    "Tag",
    "TagSet",
]
