"""
Variable Module

This module provides the Variable class for mathematical variables.

Purpose
-------
Provide a class for representing mathematical variables.

Classes
-------
Variable: Mathematical variable representation

Responsibilities
----------------
- Represent mathematical variables
- Support variable constraints
- Support variable operations
- Support variable validation

Dependencies
------------
typing (standard library)
quantsmind.core.math_object (MathObject)
"""

from __future__ import annotations

from typing import Any


class Variable:
    """Mathematical variable representation.

    This class provides functionality for representing mathematical variables
    with optional constraints and metadata.

    Attributes:
        _name: Variable name
        _value: Variable value
        _type: Variable type
        _constraints: Variable constraints
        _metadata: Additional metadata

    Example:
        >>> var = Variable("x", 0.0, "float", min_value=0.0, max_value=10.0)
        >>> var.set_value(5.0)
    """

    def __init__(
        self,
        name: str,
        value: float | int | str | None = None,
        var_type: str = "float",
        constraints: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a Variable.

        Args:
            name: Variable name
            value: Initial value
            var_type: Variable type (float, int, str, bool)
            constraints: Variable constraints (min_value, max_value, allowed_values)
            metadata: Additional metadata

        Example:
            >>> var = Variable("x", 0.0, "float", min_value=0.0, max_value=10.0)
        """
        if not name:
            raise ValueError("Variable name cannot be empty")

        self._name = name
        self._value = value
        self._type = var_type
        self._constraints = constraints or {}
        self._metadata = metadata or {}

    @property
    def name(self) -> str:
        """Get the variable name.

        Returns:
            Variable name

        Example:
            >>> name = var.name
        """
        return self._name

    @property
    def value(self) -> float | int | str | None:
        """Get the variable value.

        Returns:
            Variable value

        Example:
            >>> value = var.value
        """
        return self._value

    @property
    def type(self) -> str:
        """Get the variable type.

        Returns:
            Variable type

        Example:
            >>> vtype = var.type
        """
        return self._type

    @property
    def constraints(self) -> dict[str, Any]:
        """Get the variable constraints.

        Returns:
            Constraints dictionary

        Example:
            >>> constraints = var.constraints
        """
        return self._constraints.copy()

    @property
    def metadata(self) -> dict[str, Any]:
        """Get the metadata.

        Returns:
            Metadata dictionary

        Example:
            >>> metadata = var.metadata
        """
        return self._metadata.copy()

    def set_value(self, value: float | int | str) -> None:
        """Set the variable value.

        Args:
            value: New value

        Example:
            >>> var.set_value(5.0)
        """
        # Type check
        if self._type == "float":
            if not isinstance(value, (int, float)):
                raise TypeError(f"Expected float, got {type(value)}")
            value = float(value)
        elif self._type == "int":
            if not isinstance(value, (int, float)):
                raise TypeError(f"Expected int, got {type(value)}")
            value = int(value)
        elif self._type == "str":
            if not isinstance(value, str):
                raise TypeError(f"Expected str, got {type(value)}")
        elif self._type == "bool":
            if not isinstance(value, bool):
                raise TypeError(f"Expected bool, got {type(value)}")

        # Constraint check
        if "min_value" in self._constraints and isinstance(value, (int, float)):
            if value < self._constraints["min_value"]:
                raise ValueError(f"Value {value} below minimum {self._constraints['min_value']}")

        if "max_value" in self._constraints and isinstance(value, (int, float)):
            if value > self._constraints["max_value"]:
                raise ValueError(f"Value {value} above maximum {self._constraints['max_value']}")

        if "allowed_values" in self._constraints:
            if value not in self._constraints["allowed_values"]:
                raise ValueError(f"Value {value} not in allowed values {self._constraints['allowed_values']}")

        self._value = value

    def get_value(self) -> float | int | str | None:
        """Get the variable value.

        Returns:
            Variable value

        Example:
            >>> value = var.get_value()
        """
        return self._value

    def is_set(self) -> bool:
        """Check if the variable has a value.

        Returns:
            True if value is set

        Example:
            >>> is_set = var.is_set()
        """
        return self._value is not None

    def reset(self) -> None:
        """Reset the variable to None.

        Example:
            >>> var.reset()
        """
        self._value = None

    def validate(self) -> tuple[bool, list[str]]:
        """Validate the variable.

        Returns:
            Tuple of (is_valid, error_messages)

        Example:
            >>> is_valid, errors = var.validate()
        """
        errors = []

        if not self._name:
            errors.append("Variable name cannot be empty")

        if self._value is not None:
            # Re-use set_value validation logic
            try:
                original_value = self._value
                self._value = None
                self.set_value(original_value)
            except (TypeError, ValueError) as e:
                errors.append(str(e))

        return (len(errors) == 0, errors)

    def serialize(self) -> dict[str, Any]:
        """Serialize the variable.

        Returns:
            Serialized representation

        Example:
            >>> data = var.serialize()
        """
        return {
            "name": self._name,
            "value": self._value,
            "type": self._type,
            "constraints": self._constraints,
            "metadata": self._metadata,
        }

    @classmethod
    def deserialize(cls, data: dict[str, Any]) -> Variable:
        """Deserialize a dictionary to a variable.

        Args:
            data: Serialized data

        Returns:
            Variable

        Example:
            >>> var = Variable.deserialize(data)
        """
        return cls(
            data["name"],
            data.get("value"),
            data.get("type", "float"),
            data.get("constraints"),
            data.get("metadata"),
        )

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(var)
        """
        return f"Variable(name={self._name}, value={self._value}, type={self._type})"


__all__ = [
    "Variable",
]
