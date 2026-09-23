"""
Rule Module

This module provides rule definitions for the Knowledge package.

Purpose
-------
Provide rule management for knowledge inference.

Responsibilities
----------------
- Define rule structure
- Support rule operations
- Support rule validation
- Support rule metadata

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

from quantsmind.knowledge.exceptions import EvidenceError
from quantsmind.knowledge.types import ValidationResult


class Rule:
    """Concrete implementation of a rule.

    This class provides rule functionality for knowledge inference.

    Attributes:
        _id: Rule ID
        _name: Rule name
        _description: Rule description
        _conditions: Rule conditions
        _consequences: Rule consequences
        _priority: Rule priority
        _evidence: Supporting evidence
        _timestamp: Timestamp
        _metadata: Rule metadata

    Example:
        >>> rule = Rule("rule_001", "Inference Rule", "Description", ["condition1"], ["consequence1"])
    """

    def __init__(
        self,
        rule_id: str,
        name: str,
        description: str,
        conditions: list[str],
        consequences: list[str],
        priority: int = 0,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a Rule.

        Args:
            rule_id: Rule ID
            name: Rule name
            description: Rule description
            conditions: Rule conditions
            consequences: Rule consequences
            priority: Rule priority
            metadata: Rule metadata

        Example:
            >>> rule = Rule("rule_001", "Inference Rule", "Description", ["condition1"], ["consequence1"])
        """
        if not rule_id:
            raise EvidenceError("Rule ID cannot be empty", {"rule_id": rule_id})

        if not name:
            raise EvidenceError("Rule name cannot be empty", {"name": name})

        if not description:
            raise EvidenceError("Description cannot be empty", {"description": description})

        if not conditions:
            raise EvidenceError("Conditions cannot be empty", {"conditions": conditions})

        if not consequences:
            raise EvidenceError("Consequences cannot be empty", {"consequences": consequences})

        self._id = rule_id
        self._name = name
        self._description = description
        self._conditions = conditions
        self._consequences = consequences
        self._priority = priority
        self._evidence: list[str] = []
        self._timestamp = datetime.now(UTC).replace(tzinfo=None)
        self._metadata = metadata or {}

    @property
    def id(self) -> str:
        """Get the rule ID.

        Returns:
            Rule ID

        Example:
            >>> rid = rule.id
        """
        return self._id

    @property
    def name(self) -> str:
        """Get the rule name.

        Returns:
            Rule name

        Example:
            >>> name = rule.name
        """
        return self._name

    @property
    def description(self) -> str:
        """Get the rule description.

        Returns:
            Rule description

        Example:
            >>> description = rule.description
        """
        return self._description

    @property
    def conditions(self) -> list[str]:
        """Get the rule conditions.

        Returns:
            List of conditions

        Example:
            >>> conditions = rule.conditions
        """
        return self._conditions.copy()

    @property
    def consequences(self) -> list[str]:
        """Get the rule consequences.

        Returns:
            List of consequences

        Example:
            >>> consequences = rule.consequences
        """
        return self._consequences.copy()

    @property
    def priority(self) -> int:
        """Get the rule priority.

        Returns:
            Rule priority

        Example:
            >>> priority = rule.priority
        """
        return self._priority

    @property
    def evidence(self) -> list[str]:
        """Get the supporting evidence.

        Returns:
            List of evidence IDs

        Example:
            >>> evidence = rule.evidence
        """
        return self._evidence.copy()

    @property
    def timestamp(self) -> datetime:
        """Get the timestamp.

        Returns:
            Timestamp

        Example:
            >>> timestamp = rule.timestamp
        """
        return self._timestamp

    @property
    def metadata(self) -> dict[str, Any]:
        """Get the rule metadata.

        Returns:
            Rule metadata

        Example:
            >>> metadata = rule.metadata
        """
        return self._metadata.copy()

    def set_priority(self, priority: int) -> None:
        """Set the rule priority.

        Args:
            priority: Rule priority

        Example:
            >>> rule.set_priority(10)
        """
        self._priority = priority

    def add_condition(self, condition: str) -> None:
        """Add a condition to the rule.

        Args:
            condition: Condition to add

        Example:
            >>> rule.add_condition("new_condition")
        """
        self._conditions.append(condition)

    def remove_condition(self, condition: str) -> bool:
        """Remove a condition from the rule.

        Args:
            condition: Condition to remove

        Returns:
            True if removed

        Example:
            >>> removed = rule.remove_condition("condition1")
        """
        if condition in self._conditions:
            self._conditions.remove(condition)
            return True
        return False

    def add_consequence(self, consequence: str) -> None:
        """Add a consequence to the rule.

        Args:
            consequence: Consequence to add

        Example:
            >>> rule.add_consequence("new_consequence")
        """
        self._consequences.append(consequence)

    def remove_consequence(self, consequence: str) -> bool:
        """Remove a consequence from the rule.

        Args:
            consequence: Consequence to remove

        Returns:
            True if removed

        Example:
            >>> removed = rule.remove_consequence("consequence1")
        """
        if consequence in self._consequences:
            self._consequences.remove(consequence)
            return True
        return False

    def add_evidence(self, evidence_id: str) -> None:
        """Add supporting evidence.

        Args:
            evidence_id: Evidence ID

        Example:
            >>> rule.add_evidence("ev_001")
        """
        self._evidence.append(evidence_id)

    def remove_evidence(self, evidence_id: str) -> bool:
        """Remove supporting evidence.

        Args:
            evidence_id: Evidence ID

        Returns:
            True if removed

        Example:
            >>> removed = rule.remove_evidence("ev_001")
        """
        if evidence_id in self._evidence:
            self._evidence.remove(evidence_id)
            return True
        return False

    def validate(self) -> ValidationResult:
        """Validate the rule.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = rule.validate()
        """
        errors = []

        if not self._id:
            errors.append("Rule ID cannot be empty")

        if not self._name:
            errors.append("Rule name cannot be empty")

        if not self._description:
            errors.append("Description cannot be empty")

        if not self._conditions:
            errors.append("Conditions cannot be empty")

        if not self._consequences:
            errors.append("Consequences cannot be empty")

        return (len(errors) == 0, errors)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Rule definition

        Example:
            >>> data = rule.to_dict()
        """
        return {
            "id": self._id,
            "name": self._name,
            "description": self._description,
            "conditions": self._conditions,
            "consequences": self._consequences,
            "priority": self._priority,
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
            >>> repr(rule)
        """
        return f"Rule(id={self._id}, name={self._name}, priority={self._priority}, conditions={len(self._conditions)}, consequences={len(self._consequences)}, evidence={len(self._evidence)})"


# Export
__all__ = [
    "Rule",
]
