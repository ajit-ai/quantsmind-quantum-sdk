"""
Quality Rule Module

This module provides quality rule definitions for the Knowledge package.

Purpose
-------
Provide quality rule management for data quality checks.

Responsibilities
----------------
- Define quality rule structure
- Support quality rule operations
- Support quality rule validation
- Support quality rule metadata

Dependencies
------------
typing (standard library)
quantsmind.knowledge.enums (knowledge enumerations)
quantsmind.knowledge.exceptions (knowledge exceptions)
quantsmind.knowledge.types (knowledge types)
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional

from quantsmind.knowledge.enums import QualityType
from quantsmind.knowledge.exceptions import QualityError
from quantsmind.knowledge.types import ValidationResult


class QualityRule:
    """Concrete implementation of a quality rule.

    This class provides quality rule functionality.

    Attributes:
        _id: Rule ID
        _name: Rule name
        _rule_type: Rule type
        _description: Rule description
        _check_function: Check function
        _parameters: Rule parameters
        _metadata: Rule metadata

    Example:
        >>> rule = QualityRule("rule_001", "non_null_check", "completeness")
        >>> rule.check({"value": 42})
    """

    def __init__(
        self,
        rule_id: str,
        name: str,
        rule_type: str,
        description: Optional[str] = None,
        check_function: Optional[Callable[[Any], bool]] = None,
        parameters: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a QualityRule.

        Args:
            rule_id: Rule ID
            name: Rule name
            rule_type: Rule type
            description: Rule description
            check_function: Check function
            parameters: Rule parameters
            metadata: Rule metadata

        Example:
            >>> rule = QualityRule("rule_001", "non_null_check", "completeness")
        """
        if not rule_id:
            raise QualityError("Rule ID cannot be empty", {"rule_id": rule_id})

        if not name:
            raise QualityError("Rule name cannot be empty", {"name": name})

        if not rule_type:
            raise QualityError("Rule type cannot be empty", {"rule_type": rule_type})

        self._id = rule_id
        self._name = name
        self._rule_type = rule_type
        self._description = description
        self._check_function = check_function
        self._parameters = parameters or {}
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
    def rule_type(self) -> str:
        """Get the rule type.

        Returns:
            Rule type

        Example:
            >>> rtype = rule.rule_type
        """
        return self._rule_type

    @property
    def description(self) -> Optional[str]:
        """Get the rule description.

        Returns:
            Rule description

        Example:
            >>> description = rule.description
        """
        return self._description

    @property
    def parameters(self) -> Dict[str, Any]:
        """Get the rule parameters.

        Returns:
            Rule parameters

        Example:
            >>> parameters = rule.parameters
        """
        return self._parameters.copy()

    @property
    def metadata(self) -> Dict[str, Any]:
        """Get the rule metadata.

        Returns:
            Rule metadata

        Example:
            >>> metadata = rule.metadata
        """
        return self._metadata.copy()

    def set_check_function(self, check_function: Callable[[Any], bool]) -> None:
        """Set the check function.

        Args:
            check_function: Check function

        Example:
            >>> rule.set_check_function(lambda x: x is not None)
        """
        self._check_function = check_function

    def set_parameter(self, key: str, value: Any) -> None:
        """Set a parameter.

        Args:
            key: Parameter key
            value: Parameter value

        Example:
            >>> rule.set_parameter("threshold", 0.5)
        """
        self._parameters[key] = value

    def check(self, data: Any) -> ValidationResult:
        """Check data against the rule.

        Args:
            data: Data to check

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = rule.check({"value": 42})
        """
        if self._check_function:
            try:
                result = self._check_function(data)
                return (result, [] if result else [f"Rule '{self._name}' failed"])
            except Exception as e:
                return (False, [f"Rule '{self._name}' error: {str(e)}"])

        return (True, [])

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

        if not self._rule_type:
            errors.append("Rule type cannot be empty")

        return (len(errors) == 0, errors)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Rule definition

        Example:
            >>> data = rule.to_dict()
        """
        return {
            "id": self._id,
            "name": self._name,
            "rule_type": self._rule_type,
            "description": self._description,
            "parameters": self._parameters,
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(rule)
        """
        return f"QualityRule(id={self._id}, name={self._name}, type={self._rule_type})"


# Export
__all__ = [
    "QualityRule",
]
