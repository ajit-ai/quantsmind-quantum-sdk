"""
Fact Module

This module provides fact definitions for the Knowledge package.

Purpose
-------
Provide fact management for verified knowledge.

Responsibilities
----------------
- Define fact structure
- Support fact operations
- Support fact validation
- Support fact metadata

Dependencies
------------
typing (standard library)
datetime (standard library)
quantsmind.knowledge.enums (knowledge enumerations)
quantsmind.knowledge.exceptions (knowledge exceptions)
quantsmind.knowledge.types (knowledge types)
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from quantsmind.knowledge.exceptions import EvidenceError
from quantsmind.knowledge.types import ValidationResult


class Fact:
    """Concrete implementation of a fact.

    This class provides fact functionality for verified knowledge.

    Attributes:
        _id: Fact ID
        _statement: Fact statement
        _source: Fact source
        _verification_status: Verification status
        _evidence: Supporting evidence
        _confidence: Confidence level
        _timestamp: Timestamp
        _metadata: Fact metadata

    Example:
        >>> fact = Fact("fact_001", "Water boils at 100°C", "source_001")
    """

    def __init__(
        self,
        fact_id: str,
        statement: str,
        source: str,
        verification_status: str = "verified",
        confidence: float = 1.0,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a Fact.

        Args:
            fact_id: Fact ID
            statement: Fact statement
            source: Fact source
            verification_status: Verification status
            confidence: Confidence level (0.0 to 1.0)
            metadata: Fact metadata

        Example:
            >>> fact = Fact("fact_001", "Water boils at 100°C", "source_001")
        """
        if not fact_id:
            raise EvidenceError("Fact ID cannot be empty", {"fact_id": fact_id})

        if not statement:
            raise EvidenceError("Statement cannot be empty", {"statement": statement})

        if not source:
            raise EvidenceError("Source cannot be empty", {"source": source})

        if not 0.0 <= confidence <= 1.0:
            raise EvidenceError("Confidence must be between 0.0 and 1.0", {"confidence": confidence})

        self._id = fact_id
        self._statement = statement
        self._source = source
        self._verification_status = verification_status
        self._evidence: list[str] = []
        self._confidence = confidence
        self._timestamp = datetime.utcnow()
        self._metadata = metadata or {}

    @property
    def id(self) -> str:
        """Get the fact ID.

        Returns:
            Fact ID

        Example:
            >>> fid = fact.id
        """
        return self._id

    @property
    def statement(self) -> str:
        """Get the fact statement.

        Returns:
           Fact statement

        Example:
            >>> statement = fact.statement
        """
        return self._statement

    @property
    def source(self) -> str:
        """Get the fact source.

        Returns:
            Fact source

        Example:
            >>> source = fact.source
        """
        return self._source

    @property
    def verification_status(self) -> str:
        """Get the verification status.

        Returns:
            Verification status

        Example:
            >>> status = fact.verification_status
        """
        return self._verification_status

    @property
    def evidence(self) -> list[str]:
        """Get the supporting evidence.

        Returns:
            List of evidence IDs

        Example:
            >>> evidence = fact.evidence
        """
        return self._evidence.copy()

    @property
    def confidence(self) -> float:
        """Get the confidence level.

        Returns:
            Confidence level

        Example:
            >>> confidence = fact.confidence
        """
        return self._confidence

    @property
    def timestamp(self) -> datetime:
        """Get the timestamp.

        Returns:
            Timestamp

        Example:
            >>> timestamp = fact.timestamp
        """
        return self._timestamp

    @property
    def metadata(self) -> dict[str, Any]:
        """Get the fact metadata.

        Returns:
            Fact metadata

        Example:
            >>> metadata = fact.metadata
        """
        return self._metadata.copy()

    def set_verification_status(self, status: str) -> None:
        """Set the verification status.

        Args:
            status: Verification status

        Example:
            >>> fact.set_verification_status("verified")
        """
        self._verification_status = status

    def set_confidence(self, confidence: float) -> None:
        """Set the confidence level.

        Args:
            confidence: Confidence level (0.0 to 1.0)

        Example:
            >>> fact.set_confidence(0.95)
        """
        if not 0.0 <= confidence <= 1.0:
            raise EvidenceError("Confidence must be between 0.0 and 1.0", {"confidence": confidence})
        self._confidence = confidence

    def add_evidence(self, evidence_id: str) -> None:
        """Add supporting evidence.

        Args:
            evidence_id: Evidence ID

        Example:
            >>> fact.add_evidence("ev_001")
        """
        self._evidence.append(evidence_id)

    def remove_evidence(self, evidence_id: str) -> bool:
        """Remove supporting evidence.

        Args:
            evidence_id: Evidence ID

        Returns:
            True if removed

        Example:
            >>> removed = fact.remove_evidence("ev_001")
        """
        if evidence_id in self._evidence:
            self._evidence.remove(evidence_id)
            return True
        return False

    def validate(self) -> ValidationResult:
        """Validate the fact.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = fact.validate()
        """
        errors = []

        if not self._id:
            errors.append("Fact ID cannot be empty")

        if not self._statement:
            errors.append("Statement cannot be empty")

        if not self._source:
            errors.append("Source cannot be empty")

        if not 0.0 <= self._confidence <= 1.0:
            errors.append("Confidence must be between 0.0 and 1.0")

        return (len(errors) == 0, errors)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Fact definition

        Example:
            >>> data = fact.to_dict()
        """
        return {
            "id": self._id,
            "statement": self._statement,
            "source": self._source,
            "verification_status": self._verification_status,
            "evidence_count": len(self._evidence),
            "evidence": self._evidence,
            "confidence": self._confidence,
            "timestamp": self._timestamp.isoformat(),
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(fact)
        """
        return f"Fact(id={self._id}, statement={self._statement[:50]}..., status={self._verification_status}, confidence={self._confidence})"


# Export
__all__ = [
    "Fact",
]
