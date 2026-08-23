"""
Field Module

This module provides field definitions for the Knowledge package.

Purpose
-------
Provide field management for schemas.

Responsibilities
----------------
- Define field structure
- Support field operations
- Support field validation
- Support field constraints

Dependencies
------------
typing (standard library)
quantsmind.knowledge.exceptions (knowledge exceptions)
quantsmind.knowledge.types (knowledge types)
"""

from __future__ import annotations

from typing import Any

from quantsmind.knowledge.exceptions import ValidationError


class Field:
    """Concrete implementation of a schema field.

    This class provides field functionality.

    Attributes:
        _name: Field name
        _field_type: Field type
        _required: Whether field is required
        _default: Default value
        _constraints: Field constraints
        _description: Field description

    Example:
        >>> field = Field("name", "string", required=True)
        >>> field.name
    """

    def __init__(
        self,
        name: str,
        field_type: str = "string",
        required: bool = False,
        default: Any | None = None,
        constraints: dict[str, Any] | None = None,
        description: str | None = None,
    ) -> None:
        """Initialize a Field.

        Args:
            name: Field name
            field_type: Field type
            required: Whether field is required
            default: Default value
            constraints: Field constraints
            description: Field description

        Example:
            >>> field = Field("name", "string", required=True)
        """
        if not name:
            raise ValidationError("Field name cannot be empty")

        self._name = name
        self._field_type = field_type
        self._required = required
        self._default = default
        self._constraints = constraints or {}
        self._description = description

    @property
    def name(self) -> str:
        """Get the field name.

        Returns:
            Field name

        Example:
            >>> name = field.name
        """
        return self._name

    @property
    def field_type(self) -> str:
        """Get the field type.

        Returns:
            Field type

        Example:
            >>> ftype = field.field_type
        """
        return self._field_type

    @property
    def required(self) -> bool:
        """Get whether field is required.

        Returns:
            True if required

        Example:
            >>> required = field.required
        """
        return self._required

    @property
    def default(self) -> Any | None:
        """Get the default value.

        Returns:
            Default value

        Example:
            >>> default = field.default
        """
        return self._default

    @property
    def constraints(self) -> dict[str, Any]:
        """Get the field constraints.

        Returns:
            Field constraints

        Example:
            >>> constraints = field.constraints
        """
        return self._constraints.copy()

    @property
    def description(self) -> str | None:
        """Get the field description.

        Returns:
            Field description

        Example:
            >>> description = field.description
        """
        return self._description

    def set_constraint(self, key: str, value: Any) -> None:
        """Set a constraint.

        Args:
            key: Constraint key
            value: Constraint value

        Example:
            >>> field.set_constraint("min", 0)
        """
        self._constraints[key] = value

    def remove_constraint(self, key: str) -> bool:
        """Remove a constraint.

        Args:
            key: Constraint key

        Returns:
            True if removed

        Example:
            >>> removed = field.remove_constraint("min")
        """
        if key in self._constraints:
            del self._constraints[key]
            return True
        return False

    def validate_value(self, value: Any) -> tuple[bool, list[str]]:
        """Validate a value against field constraints.

        Args:
            value: Value to validate

        Returns:
            (is_valid, errors)

        Example:
            >>> valid, errors = field.validate_value("test")
        """
        errors = []

        # Validate type
        if not self._validate_type(value, self._field_type):
            errors.append(f"Value has invalid type, expected {self._field_type}")

        # Validate constraints
        if "min" in self._constraints and isinstance(value, (int, float)):
            if value < self._constraints["min"]:
                errors.append(f"Value is below minimum {self._constraints['min']}")

        if "max" in self._constraints and isinstance(value, (int, float)):
            if value > self._constraints["max"]:
                errors.append(f"Value is above maximum {self._constraints['max']}")

        if "min_length" in self._constraints and isinstance(value, str):
            if len(value) < self._constraints["min_length"]:
                errors.append(f"Value is below minimum length {self._constraints['min_length']}")

        if "max_length" in self._constraints and isinstance(value, str):
            if len(value) > self._constraints["max_length"]:
                errors.append(f"Value is above maximum length {self._constraints['max_length']}")

        if "pattern" in self._constraints and isinstance(value, str):
            import re
            if not re.match(self._constraints["pattern"], value):
                errors.append(f"Value does not match pattern {self._constraints['pattern']}")

        if "enum" in self._constraints and value not in self._constraints["enum"]:
            errors.append(f"Value not in allowed values: {self._constraints['enum']}")

        return (len(errors) == 0, errors)

    def _validate_type(self, value: Any, expected_type: str) -> bool:
        """Validate value type.

        Args:
            value: Value to validate
            expected_type: Expected type

        Returns:
            True if valid

        Example:
            >>> valid = field._validate_type("value", "string")
        """
        type_map = {
            "string": str,
            "int": int,
            "float": float,
            "bool": bool,
            "list": list,
            "dict": dict,
            "any": object,
        }

        expected_python_type = type_map.get(expected_type, str)
        if expected_type == "any":
            return True

        return isinstance(value, expected_python_type)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Field definition

        Example:
            >>> data = field.to_dict()
        """
        return {
            "name": self._name,
            "type": self._field_type,
            "required": self._required,
            "default": self._default,
            "constraints": self._constraints,
            "description": self._description,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(field)
        """
        return f"Field(name={self._name}, type={self._field_type}, required={self._required})"


# Export
__all__ = [
    "Field",
]
