"""
Law Module

This module provides law definitions for the Knowledge package.

Purpose
-------
Provide law management for knowledge principles.

Responsibilities
----------------
- Define law structure
- Support law operations
- Support law validation
- Support law metadata

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


class Law:
    """Concrete implementation of a law.

    This class provides law functionality for knowledge principles.

    Attributes:
        _id: Law ID
        _name: Law name
        _description: Law description
        _statement: Law statement
        _domain: Domain of application
        _conditions: Applicable conditions
        _evidence: Supporting evidence
        _timestamp: Timestamp
        _metadata: Law metadata

    Example:
        >>> law = Law("law_001", "Newton's First Law", "Description", "Statement", "Physics")
    """

    def __init__(
        self,
        law_id: str,
        name: str,
        description: str,
        statement: str,
        domain: str,
        conditions: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a Law.

        Args:
            law_id: Law ID
            name: Law name
            description: Law description
            statement: Law statement
            domain: Domain of application
            conditions: Applicable conditions
            metadata: Law metadata

        Example:
            >>> law = Law("law_001", "Newton's First Law", "Description", "Statement", "Physics")
        """
        if not law_id:
            raise EvidenceError("Law ID cannot be empty", {"law_id": law_id})

        if not name:
            raise EvidenceError("Law name cannot be empty", {"name": name})

        if not description:
            raise EvidenceError("Description cannot be empty", {"description": description})

        if not statement:
            raise EvidenceError("Statement cannot be empty", {"statement": statement})

        if not domain:
            raise EvidenceError("Domain cannot be empty", {"domain": domain})

        self._id = law_id
        self._name = name
        self._description = description
        self._statement = statement
        self._domain = domain
        self._conditions = conditions or []
        self._evidence: List[str] = []
        self._timestamp = datetime.utcnow()
        self._metadata = metadata or {}

    @property
    def id(self) -> str:
        """Get the law ID.

        Returns:
            Law ID

        Example:
            >>> lid = law.id
        """
        return self._id

    @property
    def name(self) -> str:
        """Get the law name.

        Returns:
            Law name

        Example:
            >>> name = law.name
        """
        return self._name

    @property
    def description(self) -> str:
        """Get the law description.

        Returns:
            Law description

        Example:
            >>> description = law.description
        """
        return self._description

    @property
    def statement(self) -> str:
        """Get the law statement.

        Returns:
            Law statement

        Example:
            >>> statement = law.statement
        """
        return self._statement

    @property
    def domain(self) -> str:
        """Get the domain of application.

        Returns:
            Domain

        Example:
            >>> domain = law.domain
        """
        return self._domain

    @property
    def conditions(self) -> List[str]:
        """Get the applicable conditions.

        Returns:
            List of conditions

        Example:
            >>> conditions = law.conditions
        """
        return self._conditions.copy()

    @property
    def evidence(self) -> List[str]:
        """Get the supporting evidence.

        Returns:
            List of evidence IDs

        Example:
            >>> evidence = law.evidence
        """
        return self._evidence.copy()

    @property
    def timestamp(self) -> datetime:
        """Get the timestamp.

        Returns:
            Timestamp

        Example:
            >>> timestamp = law.timestamp
        """
        return self._timestamp

    @property
    def metadata(self) -> Dict[str, Any]:
        """Get the law metadata.

        Returns:
            Law metadata

        Example:
            >>> metadata = law.metadata
        """
        return self._metadata.copy()

    def add_condition(self, condition: str) -> None:
        """Add an applicable condition.

        Args:
            condition: Condition to add

        Example:
            >>> law.add_condition("inertial_frame")
        """
        self._conditions.append(condition)

    def remove_condition(self, condition: str) -> bool:
        """Remove an applicable condition.

        Args:
            condition: Condition to remove

        Returns:
            True if removed

        Example:
            >>> removed = law.remove_condition("inertial_frame")
        """
        if condition in self._conditions:
            self._conditions.remove(condition)
            return True
        return False

    def add_evidence(self, evidence_id: str) -> None:
        """Add supporting evidence.

        Args:
            evidence_id: Evidence ID

        Example:
            >>> law.add_evidence("ev_001")
        """
        self._evidence.append(evidence_id)

    def remove_evidence(self, evidence_id: str) -> bool:
        """Remove supporting evidence.

        Args:
            evidence_id: Evidence ID

        Returns:
            True if removed

        Example:
            >>> removed = law.remove_evidence("ev_001")
        """
        if evidence_id in self._evidence:
            self._evidence.remove(evidence_id)
            return True
        return False

    def validate(self) -> ValidationResult:
        """Validate the law.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = law.validate()
        """
        errors = []

        if not self._id:
            errors.append("Law ID cannot be empty")

        if not self._name:
            errors.append("Law name cannot be empty")

        if not self._description:
            errors.append("Description cannot be empty")

        if not self._statement:
            errors.append("Statement cannot be empty")

        if not self._domain:
            errors.append("Domain cannot be empty")

        return (len(errors) == 0, errors)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Law definition

        Example:
            >>> data = law.to_dict()
        """
        return {
            "id": self._id,
            "name": self._name,
            "description": self._description,
            "statement": self._statement,
            "domain": self._domain,
            "conditions": self._conditions,
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
            >>> repr(law)
        """
        return f"Law(id={self._id}, name={self._name}, domain={self._domain}, conditions={len(self._conditions)}, evidence={len(self._evidence)})"


# Export
__all__ = [
    "Law",
]
