"""
Parameter Module

This module provides the Parameter class for mathematical parameters.

Purpose
-------
Provide a class for representing mathematical parameters.

Classes
-------
Parameter: Mathematical parameter representation

Responsibilities
----------------
- Represent mathematical parameters
- Support parameter constraints
- Support parameter operations
- Support parameter validation

Dependencies
------------
typing (standard library)
quantsmind.core.variable (Variable)
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Union


class Parameter:
    """Mathematical parameter representation.

    This class provides functionality for representing mathematical parameters
    with optional constraints, default values, and metadata. Parameters are similar
    to variables but typically represent fixed or tunable constants in formulas.

    Attributes:
        _name: Parameter name
        _value: Parameter value
        _default_value: Default value
        _type: Parameter type
        _constraints: Parameter constraints
        _metadata: Additional metadata

    Example:
        >>> param = Parameter("pi", 3.14159, "float", description="Pi constant")
        >>> value = param.get_value()
    """

    def __init__(
        self,
        name: str,
        value: Optional[Union[float, int, str]] = None,
        param_type: str = "float",
        default_value: Optional[Union[float, int, str]] = None,
        constraints: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a Parameter.

        Args:
            name: Parameter name
            value: Initial value
            param_type: Parameter type (float, int, str, bool)
            default_value: Default value for reset
            constraints: Parameter constraints (min_value, max_value, allowed_values)
            metadata: Additional metadata

        Example:
            >>> param = Parameter("pi", 3.14159, "float", description="Pi constant")
        """
        if not name:
            raise ValueError("Parameter name cannot be empty")

        self._name = name
        self._value = value if value is not None else default_value
        self._default_value = default_value
        self._type = param_type
        self._constraints = constraints or {}
        self._metadata = metadata or {}

    @property
    def name(self) -> str:
        """Get the parameter name.

        Returns:
            Parameter name

        Example:
            >>> name = param.name
        """
        return self._name

    @property
    def value(self) -> Optional[Union[float, int, str]]:
        """Get the parameter value.

        Returns:
            Parameter value

        Example:
            >>> value = param.value
        """
        return self._value

    @property
    def default_value(self) -> Optional[Union[float, int, str]]:
        """Get the default value.

        Returns:
            Default value

        Example:
            >>> default = param.default_value
        """
        return self._default_value

    @property
    def type(self) -> str:
        """Get the parameter type.

        Returns:
            Parameter type

        Example:
            >>> ptype = param.type
        """
        return self._type

    @property
    def constraints(self) -> Dict[str, Any]:
        """Get the parameter constraints.

        Returns:
            Constraints dictionary

        Example:
            >>> constraints = param.constraints
        """
        return self._constraints.copy()

    @property
    def metadata(self) -> Dict[str, Any]:
        """Get the metadata.

        Returns:
            Metadata dictionary

        Example:
            >>> metadata = param.metadata
        """
        return self._metadata.copy()

    def set_value(self, value: Union[float, int, str]) -> None:
        """Set the parameter value.

        Args:
            value: New value

        Example:
            >>> param.set_value(3.14159)
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

    def get_value(self) -> Optional[Union[float, int, str]]:
        """Get the parameter value.

        Returns:
            Parameter value

        Example:
            >>> value = param.get_value()
        """
        return self._value

    def reset_to_default(self) -> None:
        """Reset the parameter to its default value.

        Example:
            >>> param.reset_to_default()
        """
        if self._default_value is not None:
            self._value = self._default_value

    def is_set(self) -> bool:
        """Check if the parameter has a value.

        Returns:
            True if value is set

        Example:
            >>> is_set = param.is_set()
        """
        return self._value is not None

    def validate(self) -> tuple[bool, list[str]]:
        """Validate the parameter.

        Returns:
            Tuple of (is_valid, error_messages)

        Example:
            >>> is_valid, errors = param.validate()
        """
        errors = []

        if not self._name:
            errors.append("Parameter name cannot be empty")

        if self._value is not None:
            # Re-use set_value validation logic
            try:
                original_value = self._value
                self._value = None
                self.set_value(original_value)
            except (TypeError, ValueError) as e:
                errors.append(str(e))

        return (len(errors) == 0, errors)

    def serialize(self) -> Dict[str, Any]:
        """Serialize the parameter.

        Returns:
            Serialized representation

        Example:
            >>> data = param.serialize()
        """
        return {
            "name": self._name,
            "value": self._value,
            "default_value": self._default_value,
            "type": self._type,
            "constraints": self._constraints,
            "metadata": self._metadata,
        }

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> "Parameter":
        """Deserialize a dictionary to a parameter.

        Args:
            data: Serialized data

        Returns:
            Parameter

        Example:
            >>> param = Parameter.deserialize(data)
        """
        return cls(
            data["name"],
            data.get("value"),
            data.get("type", "float"),
            data.get("default_value"),
            data.get("constraints"),
            data.get("metadata"),
        )

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(param)
        """
        return f"Parameter(name={self._name}, value={self._value}, type={self._type})"


__all__ = [
    "Parameter",
]
