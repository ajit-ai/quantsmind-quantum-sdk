"""
Evidence Module

This module provides evidence definitions for the Knowledge package.

Purpose
-------
Provide evidence management for knowledge verification.

Responsibilities
----------------
- Define evidence structure
- Support evidence operations
- Support evidence validation
- Support evidence metadata

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

from quantsmind.knowledge.enums import EvidenceType
from quantsmind.knowledge.exceptions import EvidenceError
from quantsmind.knowledge.types import ValidationResult


class Evidence:
    """Concrete implementation of evidence.

    This class provides evidence functionality for knowledge verification.

    Attributes:
        _id: Evidence ID
        _evidence_type: Evidence type
        _source: Evidence source
        _data: Evidence data
        _confidence: Confidence level
        _timestamp: Timestamp
        _metadata: Evidence metadata

    Example:
        >>> evidence = Evidence("ev_001", EvidenceType.OBSERVATION, "source_001", {"value": 42})
    """

    def __init__(
        self,
        evidence_id: str,
        evidence_type: EvidenceType,
        source: str,
        data: dict[str, Any],
        confidence: float = 1.0,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize an Evidence.

        Args:
            evidence_id: Evidence ID
            evidence_type: Evidence type
            source: Evidence source
            data: Evidence data
            confidence: Confidence level (0.0 to 1.0)
            metadata: Evidence metadata

        Example:
            >>> evidence = Evidence("ev_001", EvidenceType.OBSERVATION, "source_001", {"value": 42})
        """
        if not evidence_id:
            raise EvidenceError("Evidence ID cannot be empty", {"evidence_id": evidence_id})

        if not source:
            raise EvidenceError("Source cannot be empty", {"source": source})

        if not 0.0 <= confidence <= 1.0:
            raise EvidenceError("Confidence must be between 0.0 and 1.0", {"confidence": confidence})

        self._id = evidence_id
        self._evidence_type = evidence_type
        self._source = source
        self._data = data
        self._confidence = confidence
        self._timestamp = datetime.now(UTC).replace(tzinfo=None)
        self._metadata = metadata or {}

    @property
    def id(self) -> str:
        """Get the evidence ID.

        Returns:
            Evidence ID

        Example:
            >>> eid = evidence.id
        """
        return self._id

    @property
    def evidence_type(self) -> EvidenceType:
        """Get the evidence type.

        Returns:
            Evidence type

        Example:
            >>> etype = evidence.evidence_type
        """
        return self._evidence_type

    @property
    def source(self) -> str:
        """Get the evidence source.

        Returns:
            Evidence source

        Example:
            >>> source = evidence.source
        """
        return self._source

    @property
    def data(self) -> dict[str, Any]:
        """Get the evidence data.

        Returns:
            Evidence data

        Example:
            >>> data = evidence.data
        """
        return self._data.copy()

    @property
    def confidence(self) -> float:
        """Get the confidence level.

        Returns:
            Confidence level

        Example:
            >>> confidence = evidence.confidence
        """
        return self._confidence

    @property
    def timestamp(self) -> datetime:
        """Get the timestamp.

        Returns:
            Timestamp

        Example:
            >>> timestamp = evidence.timestamp
        """
        return self._timestamp

    @property
    def metadata(self) -> dict[str, Any]:
        """Get the evidence metadata.

        Returns:
            Evidence metadata

        Example:
            >>> metadata = evidence.metadata
        """
        return self._metadata.copy()

    def set_confidence(self, confidence: float) -> None:
        """Set the confidence level.

        Args:
            confidence: Confidence level (0.0 to 1.0)

        Example:
            >>> evidence.set_confidence(0.9)
        """
        if not 0.0 <= confidence <= 1.0:
            raise EvidenceError("Confidence must be between 0.0 and 1.0", {"confidence": confidence})
        self._confidence = confidence

    def add_data(self, key: str, value: Any) -> None:
        """Add data to the evidence.

        Args:
            key: Data key
            value: Data value

        Example:
            >>> evidence.add_data("observation", "value")
        """
        self._data[key] = value

    def validate(self) -> ValidationResult:
        """Validate the evidence.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = evidence.validate()
        """
        errors = []

        if not self._id:
            errors.append("Evidence ID cannot be empty")

        if not self._source:
            errors.append("Source cannot be empty")

        if not 0.0 <= self._confidence <= 1.0:
            errors.append("Confidence must be between 0.0 and 1.0")

        return (len(errors) == 0, errors)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Evidence definition

        Example:
            >>> data = evidence.to_dict()
        """
        return {
            "id": self._id,
            "evidence_type": self._evidence_type.value,
            "source": self._source,
            "data": self._data,
            "confidence": self._confidence,
            "timestamp": self._timestamp.isoformat(),
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(evidence)
        """
        return f"Evidence(id={self._id}, type={self._evidence_type.value}, source={self._source}, confidence={self._confidence})"


# Export
__all__ = [
    "Evidence",
]
