"""
Datatype Module

This module provides datatype definitions for the Knowledge package.

Purpose
-------
Provide datatype management for schemas.

Responsibilities
----------------
- Define datatype structure
- Support datatype operations
- Support datatype validation
- Support datatype conversion

Dependencies
------------
typing (standard library)
quantsmind.knowledge.exceptions (knowledge exceptions)
quantsmind.knowledge.types (knowledge types)
"""

from __future__ import annotations

from typing import Any

from quantsmind.knowledge.exceptions import ValidationError


class DataType:
    """Concrete implementation of a datatype.

    This class provides datatype functionality.

    Attributes:
        _name: Datatype name
        _base_type: Base type
        _constraints: Datatype constraints
        _description: Datatype description

    Example:
        >>> dtype = DataType("positive_int", "int", constraints={"min": 0})
        >>> dtype.name
    """

    def __init__(
        self,
        name: str,
        base_type: str = "string",
        constraints: dict[str, Any] | None = None,
        description: str | None = None,
    ) -> None:
        """Initialize a DataType.

        Args:
            name: Datatype name
            base_type: Base type
            constraints: Datatype constraints
            description: Datatype description

        Example:
            >>> dtype = DataType("positive_int", "int", constraints={"min": 0})
        """
        if not name:
            raise ValidationError("Datatype name cannot be empty")

        self._name = name
        self._base_type = base_type
        self._constraints = constraints or {}
        self._description = description

    @property
    def name(self) -> str:
        """Get the datatype name.

        Returns:
            Datatype name

        Example:
            >>> name = dtype.name
        """
        return self._name

    @property
    def base_type(self) -> str:
        """Get the base type.

        Returns:
            Base type

        Example:
            >>> base_type = dtype.base_type
        """
        return self._base_type

    @property
    def constraints(self) -> dict[str, Any]:
        """Get the datatype constraints.

        Returns:
            Datatype constraints

        Example:
            >>> constraints = dtype.constraints
        """
        return self._constraints.copy()

    @property
    def description(self) -> str | None:
        """Get the datatype description.

        Returns:
            Datatype description

        Example:
            >>> description = dtype.description
        """
        return self._description

    def set_constraint(self, key: str, value: Any) -> None:
        """Set a constraint.

        Args:
            key: Constraint key
            value: Constraint value

        Example:
            >>> dtype.set_constraint("min", 0)
        """
        self._constraints[key] = value

    def validate(self, value: Any) -> tuple[bool, list[str]]:
        """Validate a value against datatype constraints.

        Args:
            value: Value to validate

        Returns:
            (is_valid, errors)

        Example:
            >>> valid, errors = dtype.validate(42)
        """
        errors = []

        # Validate base type
        if not self._validate_type(value, self._base_type):
            errors.append(f"Value has invalid type, expected {self._base_type}")

        # Validate constraints
        if "min" in self._constraints and isinstance(value, (int, float)):
            if value < self._constraints["min"]:
                errors.append(f"Value is below minimum {self._constraints['min']}")

        if "max" in self._constraints and isinstance(value, (int, float)):
            if value > self._constraints["max"]:
                errors.append(f"Value is above maximum {self._constraints['max']}")

        if "min_length" in self._constraints and isinstance(value, (str, list)):
            if len(value) < self._constraints["min_length"]:
                errors.append(f"Value is below minimum length {self._constraints['min_length']}")

        if "max_length" in self._constraints and isinstance(value, (str, list)):
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
            >>> valid = dtype._validate_type("value", "string")
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

    def convert(self, value: Any) -> Any:
        """Convert value to this datatype.

        Args:
            value: Value to convert

        Returns:
            Converted value

        Raises:
            ValidationError: If conversion fails

        Example:
            >>> converted = dtype.convert("42")
        """
        try:
            if self._base_type == "string":
                return str(value)
            elif self._base_type == "int":
                return int(value)
            elif self._base_type == "float":
                return float(value)
            elif self._base_type == "bool":
                return bool(value)
            elif self._base_type == "list":
                return list(value)
            elif self._base_type == "dict":
                return dict(value)
            else:
                return value
        except (ValueError, TypeError) as e:
            raise ValidationError(f"Failed to convert value to {self._name}: {e}")

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Datatype definition

        Example:
            >>> data = dtype.to_dict()
        """
        return {
            "name": self._name,
            "base_type": self._base_type,
            "constraints": self._constraints,
            "description": self._description,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(dtype)
        """
        return f"DataType(name={self._name}, base_type={self._base_type})"


class DataTypeRegistry:
    """Registry for custom datatypes.

    This class provides datatype registry functionality.

    Attributes:
        _datatypes: Registered datatypes

    Example:
        >>> registry = DataTypeRegistry()
        >>> registry.register(DataType("positive_int", "int"))
    """

    def __init__(self) -> None:
        """Initialize a DataTypeRegistry.

        Example:
            >>> registry = DataTypeRegistry()
        """
        self._datatypes: dict[str, DataType] = {}

        # Register standard datatypes
        self._register_standard_datatypes()

    def _register_standard_datatypes(self) -> None:
        """Register standard datatypes.

        Example:
            >>> registry._register_standard_datatypes()
        """
        standard_types = [
            DataType("string", "string"),
            DataType("int", "int"),
            DataType("float", "float"),
            DataType("bool", "bool"),
            DataType("list", "list"),
            DataType("dict", "dict"),
            DataType("any", "any"),
        ]

        for dtype in standard_types:
            self._datatypes[dtype.name] = dtype

    def register(self, datatype: DataType) -> None:
        """Register a datatype.

        Args:
            datatype: Datatype to register

        Example:
            >>> registry.register(DataType("positive_int", "int"))
        """
        self._datatypes[datatype.name] = datatype

    def unregister(self, name: str) -> bool:
        """Unregister a datatype.

        Args:
            name: Datatype name

        Returns:
            True if unregistered

        Example:
            >>> unregistered = registry.unregister("positive_int")
        """
        if name in self._datatypes and name not in ["string", "int", "float", "bool", "list", "dict", "any"]:
            del self._datatypes[name]
            return True
        return False

    def get(self, name: str) -> DataType | None:
        """Get a datatype by name.

        Args:
            name: Datatype name

        Returns:
            Datatype or None

        Example:
            >>> dtype = registry.get("string")
        """
        return self._datatypes.get(name)

    def list_all(self) -> list[DataType]:
        """List all registered datatypes.

        Returns:
            List of datatypes

        Example:
            >>> datatypes = registry.list_all()
        """
        return list(self._datatypes.values())

    def count(self) -> int:
        """Get the number of registered datatypes.

        Returns:
            Number of datatypes

        Example:
            >>> count = registry.count()
        """
        return len(self._datatypes)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Registry state

        Example:
            >>> data = registry.to_dict()
        """
        return {
            "datatypes": [dtype.to_dict() for dtype in self._datatypes.values()],
            "count": len(self._datatypes),
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(registry)
        """
        return f"DataTypeRegistry(count={len(self._datatypes)})"


# Export
__all__ = [
    "DataType",
    "DataTypeRegistry",
]
