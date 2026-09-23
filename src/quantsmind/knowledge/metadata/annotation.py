"""
Annotation Module

This module provides annotation definitions for the Knowledge package.

Purpose
-------
Provide annotation management for knowledge items.

Responsibilities
----------------
- Define annotation structure
- Support annotation operations
- Support annotation validation
- Support annotation metadata

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

from quantsmind.knowledge.types import Annotation


class Annotation:
    """Concrete implementation of an annotation.

    This class provides annotation functionality.

    Attributes:
        _id: Annotation ID
        _text: Annotation text
        _annotator: Annotator
        _timestamp: Annotation timestamp
        _metadata: Annotation metadata

    Example:
        >>> annotation = Annotation("This is a note", "user_001")
        >>> annotation.text
    """

    def __init__(
        self,
        text: str,
        annotator: str,
        annotation_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize an Annotation.

        Args:
            text: Annotation text
            annotator: Annotator ID or name
            annotation_id: Annotation ID
            metadata: Annotation metadata

        Example:
            >>> annotation = Annotation("This is a note", "user_001")
        """
        self._id = annotation_id or f"annotation_{datetime.now(UTC).replace(tzinfo=None).timestamp()}"
        self._text = text
        self._annotator = annotator
        self._timestamp = datetime.now(UTC).replace(tzinfo=None)
        self._metadata = metadata or {}

    @property
    def id(self) -> str:
        """Get the annotation ID.

        Returns:
            Annotation ID

        Example:
            >>> annotation_id = annotation.id
        """
        return self._id

    @property
    def text(self) -> str:
        """Get the annotation text.

        Returns:
            Annotation text

        Example:
            >>> text = annotation.text
        """
        return self._text

    @property
    def annotator(self) -> str:
        """Get the annotator.

        Returns:
            Annotator ID or name

        Example:
            >>> annotator = annotation.annotator
        """
        return self._annotator

    @property
    def timestamp(self) -> datetime:
        """Get the annotation timestamp.

        Returns:
            Timestamp

        Example:
            >>> timestamp = annotation.timestamp
        """
        return self._timestamp

    @property
    def metadata(self) -> dict[str, Any]:
        """Get the annotation metadata.

        Returns:
            Annotation metadata

        Example:
            >>> metadata = annotation.metadata
        """
        return self._metadata.copy()

    def update_text(self, text: str) -> None:
        """Update the annotation text.

        Args:
            text: New annotation text

        Example:
            >>> annotation.update_text("Updated note")
        """
        self._text = text

    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to the annotation.

        Args:
            key: Metadata key
            value: Metadata value

        Example:
            >>> annotation.add_metadata("priority", "high")
        """
        self._metadata[key] = value

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Annotation definition

        Example:
            >>> data = annotation.to_dict()
        """
        return {
            "id": self._id,
            "text": self._text,
            "annotator": self._annotator,
            "timestamp": self._timestamp.isoformat(),
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(annotation)
        """
        return f"Annotation(id={self._id}, text={self._text[:50]}, annotator={self._annotator})"


# Export
__all__ = [
    "Annotation",
]
