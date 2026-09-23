"""
Converter Module

This module provides converter definitions for the Knowledge package.

Purpose
-------
Provide converter management for data type conversions.

Responsibilities
----------------
- Define converter structure
- Support converter operations
- Support converter validation
- Support converter metadata

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

from quantsmind.knowledge.exceptions import TransformationError
from quantsmind.knowledge.types import ValidationResult


class Converter:
    """Concrete implementation of a converter.

    This class provides converter functionality for converting data types.

    Attributes:
        _id: Converter ID
        _name: Converter name
        _source_type: Source data type
        _target_type: Target data type
        _convert_function: Convert function
        _metadata: Converter metadata

    Example:
        >>> converter = Converter("conv_001", "String to Int", "string", "int")
        >>> converter.convert("42")
    """

    def __init__(
        self,
        converter_id: str,
        name: str,
        source_type: str,
        target_type: str,
        convert_function: Callable[[Any], Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a Converter.

        Args:
            converter_id: Converter ID
            name: Converter name
            source_type: Source data type
            target_type: Target data type
            convert_function: Convert function
            metadata: Converter metadata

        Example:
            >>> converter = Converter("conv_001", "String to Int", "string", "int")
        """
        if not converter_id:
            raise TransformationError("Converter ID cannot be empty", {"converter_id": converter_id})

        if not name:
            raise TransformationError("Converter name cannot be empty", {"name": name})

        if not source_type:
            raise TransformationError("Source type cannot be empty", {"source_type": source_type})

        if not target_type:
            raise TransformationError("Target type cannot be empty", {"target_type": target_type})

        self._id = converter_id
        self._name = name
        self._source_type = source_type
        self._target_type = target_type
        self._convert_function = convert_function
        self._metadata = metadata or {}

    @property
    def id(self) -> str:
        """Get the converter ID.

        Returns:
            Converter ID

        Example:
            >>> cid = converter.id
        """
        return self._id

    @property
    def name(self) -> str:
        """Get the converter name.

        Returns:
            Converter name

        Example:
            >>> name = converter.name
        """
        return self._name

    @property
    def source_type(self) -> str:
        """Get the source type.

        Returns:
            Source data type

        Example:
            >>> source_type = converter.source_type
        """
        return self._source_type

    @property
    def target_type(self) -> str:
        """Get the target type.

        Returns:
            Target data type

        Example:
            >>> target_type = converter.target_type
        """
        return self._target_type

    @property
    def metadata(self) -> dict[str, Any]:
        """Get the converter metadata.

        Returns:
            Converter metadata

        Example:
            >>> metadata = converter.metadata
        """
        return self._metadata.copy()

    def set_convert_function(self, convert_function: Callable[[Any], Any]) -> None:
        """Set the convert function.

        Args:
            convert_function: Convert function

        Example:
            >>> converter.set_convert_function(int)
        """
        self._convert_function = convert_function

    def convert(self, data: Any) -> Any:
        """Convert data from source to target type.

        Args:
            data: Data to convert

        Returns:
            Converted data

        Example:
            >>> result = converter.convert("42")
        """
        if self._convert_function:
            try:
                return self._convert_function(data)
            except Exception as e:
                raise TransformationError(f"Conversion failed: {str(e)}", {"converter_id": self._id})

        # Default conversion attempts
        if self._target_type == "string":
            return str(data)
        elif self._target_type == "int":
            return int(data)
        elif self._target_type == "float":
            return float(data)
        elif self._target_type == "bool":
            return bool(data)
        else:
            return data

    def can_convert(self, data: Any) -> bool:
        """Check if data can be converted.

        Args:
            data: Data to check

        Returns:
            True if convertible

        Example:
            >>> can_convert = converter.can_convert("42")
        """
        try:
            self.convert(data)
            return True
        except Exception:
            return False

    def validate(self) -> ValidationResult:
        """Validate the converter.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = converter.validate()
        """
        errors = []

        if not self._id:
            errors.append("Converter ID cannot be empty")

        if not self._name:
            errors.append("Converter name cannot be empty")

        if not self._source_type:
            errors.append("Source type cannot be empty")

        if not self._target_type:
            errors.append("Target type cannot be empty")

        return (len(errors) == 0, errors)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Converter definition

        Example:
            >>> data = converter.to_dict()
        """
        return {
            "id": self._id,
            "name": self._name,
            "source_type": self._source_type,
            "target_type": self._target_type,
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(converter)
        """
        return f"Converter(id={self._id}, name={self._name}, source={self._source_type}, target={self._target_type})"


class ConverterRegistry:
    """Registry for converters.

    This class provides converter registry functionality.

    Attributes:
        _converters: Registered converters

    Example:
        >>> registry = ConverterRegistry()
        >>> registry.register(Converter("conv_001", "String to Int", "string", "int"))
    """

    def __init__(self) -> None:
        """Initialize a ConverterRegistry.

        Example:
            >>> registry = ConverterRegistry()
        """
        self._converters: dict[str, Converter] = {}

    def register(self, converter: Converter) -> None:
        """Register a converter.

        Args:
            converter: Converter to register

        Example:
            >>> registry.register(Converter("conv_001", "String to Int", "string", "int"))
        """
        self._converters[converter.id] = converter

    def unregister(self, converter_id: str) -> bool:
        """Unregister a converter.

        Args:
            converter_id: Converter ID

        Returns:
            True if unregistered

        Example:
            >>> unregistered = registry.unregister("conv_001")
        """
        if converter_id in self._converters:
            del self._converters[converter_id]
            return True
        return False

    def get(self, converter_id: str) -> Converter | None:
        """Get a converter by ID.

        Args:
            converter_id: Converter ID

        Returns:
            Converter or None

        Example:
            >>> converter = registry.get("conv_001")
        """
        return self._converters.get(converter_id)

    def get_by_types(self, source_type: str, target_type: str) -> Converter | None:
        """Get a converter by source and target types.

        Args:
            source_type: Source data type
            target_type: Target data type

        Returns:
            Converter or None

        Example:
            >>> converter = registry.get_by_types("string", "int")
        """
        for converter in self._converters.values():
            if converter.source_type == source_type and converter.target_type == target_type:
                return converter
        return None

    def list_all(self) -> list[Converter]:
        """List all registered converters.

        Returns:
            List of converters

        Example:
            >>> converters = registry.list_all()
        """
        return list(self._converters.values())

    def count(self) -> int:
        """Get the number of registered converters.

        Returns:
            Number of converters

        Example:
            >>> count = registry.count()
        """
        return len(self._converters)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Registry state

        Example:
            >>> data = registry.to_dict()
        """
        return {
            "converters": [converter.to_dict() for converter in self._converters.values()],
            "count": len(self._converters),
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(registry)
        """
        return f"ConverterRegistry(converters={len(self._converters)})"


# Export
__all__ = [
    "Converter",
    "ConverterRegistry",
]
