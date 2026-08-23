"""
Consistency Module

This module provides consistency definitions for the Knowledge package.

Purpose
-------
Provide consistency checks for data quality.

Responsibilities
----------------
- Define consistency structure
- Support consistency operations
- Support consistency validation
- Support consistency metadata

Dependencies
------------
typing (standard library)
quantsmind.knowledge.enums (knowledge enumerations)
quantsmind.knowledge.exceptions (knowledge exceptions)
quantsmind.knowledge.types (knowledge types)
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from quantsmind.knowledge.exceptions import QualityError
from quantsmind.knowledge.types import ValidationResult


class Consistency:
    """Concrete implementation of a consistency check.

    This class provides consistency functionality for checking data consistency.

    Attributes:
        _id: Check ID
        _rules: Consistency rules
        _metadata: Check metadata

    Example:
        >>> consistency = Consistency("cons_001")
        >>> consistency.add_rule("age >= 0")
    """

    def __init__(
        self,
        check_id: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a Consistency.

        Args:
            check_id: Check ID
            metadata: Check metadata

        Example:
            >>> consistency = Consistency("cons_001")
        """
        if not check_id:
            raise QualityError("Check ID cannot be empty", {"check_id": check_id})

        self._id = check_id
        self._rules: list[tuple[str, Callable[[dict[str, Any]], bool]]] = []
        self._metadata = metadata or {}

    @property
    def id(self) -> str:
        """Get the check ID.

        Returns:
            Check ID

        Example:
            >>> cid = consistency.id
        """
        return self._id

    @property
    def rules(self) -> list[str]:
        """Get the rule descriptions.

        Returns:
            Rule descriptions

        Example:
            >>> rules = consistency.rules
        """
        return [rule[0] for rule in self._rules]

    @property
    def metadata(self) -> dict[str, Any]:
        """Get the check metadata.

        Returns:
            Check metadata

        Example:
            >>> metadata = consistency.metadata
        """
        return self._metadata.copy()

    def add_rule(self, description: str, check_function: Callable[[dict[str, Any]], bool]) -> None:
        """Add a consistency rule.

        Args:
            description: Rule description
            check_function: Check function

        Example:
            >>> consistency.add_rule("age >= 0", lambda d: d.get("age", 0) >= 0)
        """
        self._rules.append((description, check_function))

    def remove_rule(self, description: str) -> bool:
        """Remove a consistency rule.

        Args:
            description: Rule description

        Returns:
            True if removed

        Example:
            >>> removed = consistency.remove_rule("age >= 0")
        """
        for i, (desc, _) in enumerate(self._rules):
            if desc == description:
                del self._rules[i]
                return True
        return False

    def check(self, data: dict[str, Any]) -> ValidationResult:
        """Check data consistency.

        Args:
            data: Data to check

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = consistency.check({"age": 25})
        """
        errors = []

        for description, check_function in self._rules:
            try:
                if not check_function(data):
                    errors.append(f"Consistency rule failed: {description}")
            except Exception as e:
                errors.append(f"Consistency rule error '{description}': {str(e)}")

        return (len(errors) == 0, errors)

    def get_consistency_score(self, data: dict[str, Any]) -> float:
        """Get consistency score.

        Args:
            data: Data to check

        Returns:
            Consistency score (0.0 to 1.0)

        Example:
            >>> score = consistency.get_consistency_score({"age": 25})
        """
        if not self._rules:
            return 1.0

        passed_count = 0
        for _description, check_function in self._rules:
            try:
                if check_function(data):
                    passed_count += 1
            except Exception:
                pass

        return passed_count / len(self._rules)

    def validate(self) -> ValidationResult:
        """Validate the consistency check.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = consistency.validate()
        """
        errors = []

        if not self._id:
            errors.append("Check ID cannot be empty")

        return (len(errors) == 0, errors)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Check definition

        Example:
            >>> data = consistency.to_dict()
        """
        return {
            "id": self._id,
            "rules": [rule[0] for rule in self._rules],
            "rule_count": len(self._rules),
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(consistency)
        """
        return f"Consistency(id={self._id}, rules={len(self._rules)})"


# Export
__all__ = [
    "Consistency",
]
