"""
Hypothesis Module

This module provides hypothesis definitions for the Knowledge package.

Purpose
-------
Provide hypothesis management for knowledge formulation.

Responsibilities
----------------
- Define hypothesis structure
- Support hypothesis operations
- Support hypothesis validation
- Support hypothesis metadata

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


class Hypothesis:
    """Concrete implementation of a hypothesis.

    This class provides hypothesis functionality for knowledge formulation.

    Attributes:
        _id: Hypothesis ID
        _name: Hypothesis name
        _description: Hypothesis description
        _premises: Supporting premises
        _conclusion: Hypothesis conclusion
        _status: Hypothesis status
        _evidence: Supporting evidence
        _timestamp: Timestamp
        _metadata: Hypothesis metadata

    Example:
        >>> hypothesis = Hypothesis("hyp_001", "Test Hypothesis", "Description", ["premise1"], "conclusion")
    """

    def __init__(
        self,
        hypothesis_id: str,
        name: str,
        description: str,
        premises: list[str],
        conclusion: str,
        status: str = "proposed",
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a Hypothesis.

        Args:
            hypothesis_id: Hypothesis ID
            name: Hypothesis name
            description: Hypothesis description
            premises: Supporting premises
            conclusion: Hypothesis conclusion
            status: Hypothesis status
            metadata: Hypothesis metadata

        Example:
            >>> hypothesis = Hypothesis("hyp_001", "Test Hypothesis", "Description", ["premise1"], "conclusion")
        """
        if not hypothesis_id:
            raise EvidenceError("Hypothesis ID cannot be empty", {"hypothesis_id": hypothesis_id})

        if not name:
            raise EvidenceError("Hypothesis name cannot be empty", {"name": name})

        if not description:
            raise EvidenceError("Description cannot be empty", {"description": description})

        if not premises:
            raise EvidenceError("Premises cannot be empty", {"premises": premises})

        if not conclusion:
            raise EvidenceError("Conclusion cannot be empty", {"conclusion": conclusion})

        self._id = hypothesis_id
        self._name = name
        self._description = description
        self._premises = premises
        self._conclusion = conclusion
        self._status = status
        self._evidence: list[str] = []
        self._timestamp = datetime.utcnow()
        self._metadata = metadata or {}

    @property
    def id(self) -> str:
        """Get the hypothesis ID.

        Returns:
            Hypothesis ID

        Example:
            >>> hid = hypothesis.id
        """
        return self._id

    @property
    def name(self) -> str:
        """Get the hypothesis name.

        Returns:
            Hypothesis name

        Example:
            >>> name = hypothesis.name
        """
        return self._name

    @property
    def description(self) -> str:
        """Get the hypothesis description.

        Returns:
            Hypothesis description

        Example:
            >>> description = hypothesis.description
        """
        return self._description

    @property
    def premises(self) -> list[str]:
        """Get the supporting premises.

        Returns:
            List of premises

        Example:
            >>> premises = hypothesis.premises
        """
        return self._premises.copy()

    @property
    def conclusion(self) -> str:
        """Get the hypothesis conclusion.

        Returns:
            Hypothesis conclusion

        Example:
            >>> conclusion = hypothesis.conclusion
        """
        return self._conclusion

    @property
    def status(self) -> str:
        """Get the hypothesis status.

        Returns:
            Hypothesis status

        Example:
            >>> status = hypothesis.status
        """
        return self._status

    @property
    def evidence(self) -> list[str]:
        """Get the supporting evidence IDs.

        Returns:
            List of evidence IDs

        Example:
            >>> evidence = hypothesis.evidence
        """
        return self._evidence.copy()

    @property
    def timestamp(self) -> datetime:
        """Get the timestamp.

        Returns:
            Timestamp

        Example:
            >>> timestamp = hypothesis.timestamp
        """
        return self._timestamp

    @property
    def metadata(self) -> dict[str, Any]:
        """Get the hypothesis metadata.

        Returns:
            Hypothesis metadata

        Example:
            >>> metadata = hypothesis.metadata
        """
        return self._metadata.copy()

    def set_status(self, status: str) -> None:
        """Set the hypothesis status.

        Args:
            status: Hypothesis status

        Example:
            >>> hypothesis.set_status("confirmed")
        """
        self._status = status

    def add_premise(self, premise: str) -> None:
        """Add a premise to the hypothesis.

        Args:
            premise: Premise to add

        Example:
            >>> hypothesis.add_premise("new_premise")
        """
        self._premises.append(premise)

    def remove_premise(self, premise: str) -> bool:
        """Remove a premise from the hypothesis.

        Args:
            premise: Premise to remove

        Returns:
            True if removed

        Example:
            >>> removed = hypothesis.remove_premise("premise1")
        """
        if premise in self._premises:
            self._premises.remove(premise)
            return True
        return False

    def add_evidence(self, evidence_id: str) -> None:
        """Add supporting evidence.

        Args:
            evidence_id: Evidence ID

        Example:
            >>> hypothesis.add_evidence("ev_001")
        """
        self._evidence.append(evidence_id)

    def remove_evidence(self, evidence_id: str) -> bool:
        """Remove supporting evidence.

        Args:
            evidence_id: Evidence ID

        Returns:
            True if removed

        Example:
            >>> removed = hypothesis.remove_evidence("ev_001")
        """
        if evidence_id in self._evidence:
            self._evidence.remove(evidence_id)
            return True
        return False

    def validate(self) -> ValidationResult:
        """Validate the hypothesis.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = hypothesis.validate()
        """
        errors = []

        if not self._id:
            errors.append("Hypothesis ID cannot be empty")

        if not self._name:
            errors.append("Hypothesis name cannot be empty")

        if not self._description:
            errors.append("Description cannot be empty")

        if not self._premises:
            errors.append("Premises cannot be empty")

        if not self._conclusion:
            errors.append("Conclusion cannot be empty")

        return (len(errors) == 0, errors)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Hypothesis definition

        Example:
            >>> data = hypothesis.to_dict()
        """
        return {
            "id": self._id,
            "name": self._name,
            "description": self._description,
            "premises": self._premises,
            "conclusion": self._conclusion,
            "status": self._status,
            "evidence_count": len(self._evidence),
            "evidence": self._evidence,
            "timestamp": self._timestamp.isoformat(),
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(hypothesis)
        """
        return f"Hypothesis(id={self._id}, name={self._name}, status={self._status}, premises={len(self._premises)}, evidence={len(self._evidence)})"


# Export
__all__ = [
    "Hypothesis",
]
