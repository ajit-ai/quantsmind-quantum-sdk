"""
Theory Module

This module provides theory definitions for the Knowledge package.

Purpose
-------
Provide theory management for knowledge organization.

Responsibilities
----------------
- Define theory structure
- Support theory operations
- Support theory validation
- Support theory metadata

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
from typing import Any, Dict, List, Optional

from quantsmind.knowledge.enums import EvidenceType
from quantsmind.knowledge.exceptions import EvidenceError
from quantsmind.knowledge.types import ValidationResult


class Theory:
    """Concrete implementation of a theory.

    This class provides theory functionality for knowledge organization.

    Attributes:
        _id: Theory ID
        _name: Theory name
        _description: Theory description
        _principles: Theory principles
        _hypotheses: Supporting hypotheses
        _evidence: Supporting evidence
        _status: Theory status
        _timestamp: Timestamp
        _metadata: Theory metadata

    Example:
        >>> theory = Theory("theory_001", "Test Theory", "Description", ["principle1"])
    """

    def __init__(
        self,
        theory_id: str,
        name: str,
        description: str,
        principles: List[str],
        status: str = "proposed",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a Theory.

        Args:
            theory_id: Theory ID
            name: Theory name
            description: Theory description
            principles: Theory principles
            status: Theory status
            metadata: Theory metadata

        Example:
            >>> theory = Theory("theory_001", "Test Theory", "Description", ["principle1"])
        """
        if not theory_id:
            raise EvidenceError("Theory ID cannot be empty", {"theory_id": theory_id})

        if not name:
            raise EvidenceError("Theory name cannot be empty", {"name": name})

        if not description:
            raise EvidenceError("Description cannot be empty", {"description": description})

        if not principles:
            raise EvidenceError("Principles cannot be empty", {"principles": principles})

        self._id = theory_id
        self._name = name
        self._description = description
        self._principles = principles
        self._hypotheses: List[str] = []
        self._evidence: List[str] = []
        self._status = status
        self._timestamp = datetime.utcnow()
        self._metadata = metadata or {}

    @property
    def id(self) -> str:
        """Get the theory ID.

        Returns:
            Theory ID

        Example:
            >>> tid = theory.id
        """
        return self._id

    @property
    def name(self) -> str:
        """Get the theory name.

        Returns:
            Theory name

        Example:
            >>> name = theory.name
        """
        return self._name

    @property
    def description(self) -> str:
        """Get the theory description.

        Returns:
            Theory description

        Example:
            >>> description = theory.description
        """
        return self._description

    @property
    def principles(self) -> List[str]:
        """Get the theory principles.

        Returns:
            List of principles

        Example:
            >>> principles = theory.principles
        """
        return self._principles.copy()

    @property
    def hypotheses(self) -> List[str]:
        """Get the supporting hypotheses.

        Returns:
            List of hypothesis IDs

        Example:
            >>> hypotheses = theory.hypotheses
        """
        return self._hypotheses.copy()

    @property
    def evidence(self) -> List[str]:
        """Get the supporting evidence.

        Returns:
            List of evidence IDs

        Example:
            >>> evidence = theory.evidence
        """
        return self._evidence.copy()

    @property
    def status(self) -> str:
        """Get the theory status.

        Returns:
            Theory status

        Example:
            >>> status = theory.status
        """
        return self._status

    @property
    def timestamp(self) -> datetime:
        """Get the timestamp.

        Returns:
            Timestamp

        Example:
            >>> timestamp = theory.timestamp
        """
        return self._timestamp

    @property
    def metadata(self) -> Dict[str, Any]:
        """Get the theory metadata.

        Returns:
            Theory metadata

        Example:
            >>> metadata = theory.metadata
        """
        return self._metadata.copy()

    def set_status(self, status: str) -> None:
        """Set the theory status.

        Args:
            status: Theory status

        Example:
            >>> theory.set_status("established")
        """
        self._status = status

    def add_principle(self, principle: str) -> None:
        """Add a principle to the theory.

        Args:
            principle: Principle to add

        Example:
            >>> theory.add_principle("new_principle")
        """
        self._principles.append(principle)

    def remove_principle(self, principle: str) -> bool:
        """Remove a principle from the theory.

        Args:
            principle: Principle to remove

        Returns:
            True if removed

        Example:
            >>> removed = theory.remove_principle("principle1")
        """
        if principle in self._principles:
            self._principles.remove(principle)
            return True
        return False

    def add_hypothesis(self, hypothesis_id: str) -> None:
        """Add a supporting hypothesis.

        Args:
            hypothesis_id: Hypothesis ID

        Example:
            >>> theory.add_hypothesis("hyp_001")
        """
        self._hypotheses.append(hypothesis_id)

    def remove_hypothesis(self, hypothesis_id: str) -> bool:
        """Remove a supporting hypothesis.

        Args:
            hypothesis_id: Hypothesis ID

        Returns:
            True if removed

        Example:
            >>> removed = theory.remove_hypothesis("hyp_001")
        """
        if hypothesis_id in self._hypotheses:
            self._hypotheses.remove(hypothesis_id)
            return True
        return False

    def add_evidence(self, evidence_id: str) -> None:
        """Add supporting evidence.

        Args:
            evidence_id: Evidence ID

        Example:
            >>> theory.add_evidence("ev_001")
        """
        self._evidence.append(evidence_id)

    def remove_evidence(self, evidence_id: str) -> bool:
        """Remove supporting evidence.

        Args:
            evidence_id: Evidence ID

        Returns:
            True if removed

        Example:
            >>> removed = theory.remove_evidence("ev_001")
        """
        if evidence_id in self._evidence:
            self._evidence.remove(evidence_id)
            return True
        return False

    def validate(self) -> ValidationResult:
        """Validate the theory.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = theory.validate()
        """
        errors = []

        if not self._id:
            errors.append("Theory ID cannot be empty")

        if not self._name:
            errors.append("Theory name cannot be empty")

        if not self._description:
            errors.append("Description cannot be empty")

        if not self._principles:
            errors.append("Principles cannot be empty")

        return (len(errors) == 0, errors)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Theory definition

        Example:
            >>> data = theory.to_dict()
        """
        return {
            "id": self._id,
            "name": self._name,
            "description": self._description,
            "principles": self._principles,
            "hypothesis_count": len(self._hypotheses),
            "hypotheses": self._hypotheses,
            "evidence_count": len(self._evidence),
            "evidence": self._evidence,
            "status": self._status,
            "timestamp": self._timestamp.isoformat(),
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(theory)
        """
        return f"Theory(id={self._id}, name={self._name}, status={self._status}, principles={len(self._principles)}, hypotheses={len(self._hypotheses)}, evidence={len(self._evidence)})"


# Export
__all__ = [
    "Theory",
]
