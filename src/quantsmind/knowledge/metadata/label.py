"""
Label Module

This module provides label definitions for the Knowledge package.

Purpose
-------
Provide label management for knowledge items.

Responsibilities
----------------
- Define label structure
- Support label operations
- Support label validation
- Support label metadata

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
from quantsmind.knowledge.types import Label


class Label:
    """Concrete implementation of a label.

    This class provides label functionality.

    Attributes:
        _name: Label name
        _value: Label value
        _confidence: Label confidence
        _labeler: Labeler
        _timestamp: Label timestamp
        _metadata: Label metadata

    Example:
        >>> label = Label("category", "science", 0.95, "user_001")
        >>> label.name
    """

    def __init__(
        self,
        name: str,
        value: str,
        confidence: float = 1.0,
        labeler: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a Label.

        Args:
            name: Label name
            value: Label value
            confidence: Label confidence (0.0 to 1.0)
            labeler: Labeler ID or name
            metadata: Label metadata

        Example:
            >>> label = Label("category", "science", 0.95, "user_001")
        """
        if not name:
            raise MetadataError("Label name cannot be empty")

        if not value:
            raise MetadataError("Label value cannot be empty")

        if confidence < 0.0 or confidence > 1.0:
            raise MetadataError("Label confidence must be between 0.0 and 1.0")

        self._name = name
        self._value = value
        self._confidence = confidence
        self._labeler = labeler
        self._timestamp = datetime.now(UTC).replace(tzinfo=None)
        self._metadata = metadata or {}

    @property
    def name(self) -> str:
        """Get the label name.

        Returns:
            Label name

        Example:
            >>> name = label.name
        """
        return self._name

    @property
    def value(self) -> str:
        """Get the label value.

        Returns:
            Label value

        Example:
            >>> value = label.value
        """
        return self._value

    @property
    def confidence(self) -> float:
        """Get the label confidence.

        Returns:
            Label confidence

        Example:
            >>> confidence = label.confidence
        """
        return self._confidence

    @property
    def labeler(self) -> str | None:
        """Get the labeler.

        Returns:
            Labeler ID or name

        Example:
            >>> labeler = label.labeler
        """
        return self._labeler

    @property
    def timestamp(self) -> datetime:
        """Get the label timestamp.

        Returns:
            Timestamp

        Example:
            >>> timestamp = label.timestamp
        """
        return self._timestamp

    @property
    def metadata(self) -> dict[str, Any]:
        """Get the label metadata.

        Returns:
            Label metadata

        Example:
            >>> metadata = label.metadata
        """
        return self._metadata.copy()

    def set_value(self, value: str) -> None:
        """Set the label value.

        Args:
            value: Label value

        Example:
            >>> label.set_value("physics")
        """
        if not value:
            raise MetadataError("Label value cannot be empty")
        self._value = value

    def set_confidence(self, confidence: float) -> None:
        """Set the label confidence.

        Args:
            confidence: Label confidence

        Example:
            >>> label.set_confidence(0.99)
        """
        if confidence < 0.0 or confidence > 1.0:
            raise MetadataError("Label confidence must be between 0.0 and 1.0")
        self._confidence = confidence

    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to the label.

        Args:
            key: Metadata key
            value: Metadata value

        Example:
            >>> label.add_metadata("source", "manual")
        """
        self._metadata[key] = value

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Label definition

        Example:
            >>> data = label.to_dict()
        """
        return {
            "name": self._name,
            "value": self._value,
            "confidence": self._confidence,
            "labeler": self._labeler,
            "timestamp": self._timestamp.isoformat(),
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(label)
        """
        return f"Label(name={self._name}, value={self._value}, confidence={self._confidence})"


class LabelSet:
    """Set of labels for a knowledge item.

    This class provides label set functionality.

    Attributes:
        _labels: Labels in the set

    Example:
        >>> labelset = LabelSet()
        >>> labelset.add_label(Label("category", "science"))
    """

    def __init__(self, labels: list[Label] | None = None) -> None:
        """Initialize a LabelSet.

        Args:
            labels: Initial labels

        Example:
            >>> labelset = LabelSet()
        """
        self._labels: dict[str, Label] = {}
        if labels:
            for label in labels:
                self.add_label(label)

    def add_label(self, label: Label) -> None:
        """Add a label to the set.

        Args:
            label: Label to add

        Example:
            >>> labelset.add_label(Label("category", "science"))
        """
        self._labels[label.name] = label

    def remove_label(self, name: str) -> bool:
        """Remove a label from the set.

        Args:
            name: Label name

        Returns:
            True if removed

        Example:
            >>> removed = labelset.remove_label("category")
        """
        if name in self._labels:
            del self._labels[name]
            return True
        return False

    def get_label(self, name: str) -> Label | None:
        """Get a label by name.

        Args:
            name: Label name

        Returns:
            Label or None

        Example:
            >>> label = labelset.get_label("category")
        """
        return self._labels.get(name)

    def get_high_confidence_labels(self, threshold: float = 0.8) -> list[Label]:
        """Get high confidence labels.

        Args:
            threshold: Confidence threshold

        Returns:
            List of labels

        Example:
            >>> labels = labelset.get_high_confidence_labels(0.9)
        """
        return [label for label in self._labels.values() if label.confidence >= threshold]

    def list_all(self) -> list[Label]:
        """List all labels.

        Returns:
            List of labels

        Example:
            >>> labels = labelset.list_all()
        """
        return list(self._labels.values())

    def count(self) -> int:
        """Get the number of labels.

        Returns:
            Number of labels

        Example:
            >>> count = labelset.count()
        """
        return len(self._labels)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Label set definition

        Example:
            >>> data = labelset.to_dict()
        """
        return {
            "labels": [label.to_dict() for label in self._labels.values()],
            "count": len(self._labels),
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(labelset)
        """
        return f"LabelSet(count={len(self._labels)})"


# Export
__all__ = [
    "Label",
    "LabelSet",
]
