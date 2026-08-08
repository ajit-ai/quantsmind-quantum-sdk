"""
Serializers Module

This module provides serialization functions for the Scientific package.

Purpose
-------
Provide serialization and deserialization for scientific objects.

Responsibilities
----------------
- Serialize to JSON
- Serialize to YAML
- Serialize to TOML
- Deserialize from JSON
- Deserialize from YAML
- Deserialize from TOML

Dependencies
------------
typing (standard library)
json (standard library)
quantsmind.scientific.exceptions (scientific exceptions)
quantsmind.scientific.types (scientific types)
"""

from __future__ import annotations

import json
from typing import Any, Dict, Optional

from quantsmind.scientific.exceptions import MeasurementError
from quantsmind.scientific.types import SerializedData, SerializationFormat


class JsonSerializer:
    """Concrete implementation of JSON serialization.

    This class provides JSON serialization functionality.

    Example:
        >>> serializer = JsonSerializer()
        >>> data = serializer.serialize({"key": "value"})
    """

    def __init__(self, indent: Optional[int] = None) -> None:
        """Initialize a JsonSerializer.

        Args:
            indent: JSON indentation level

        Example:
            >>> serializer = JsonSerializer(indent=2)
        """
        self._indent = indent

    def serialize(self, data: Dict[str, Any]) -> str:
        """Serialize data to JSON.

        Args:
            data: Data to serialize

        Returns:
            JSON string

        Example:
            >>> json_str = serializer.serialize({"key": "value"})
        """
        return json.dumps(data, indent=self._indent, default=str)

    def deserialize(self, data: str) -> Dict[str, Any]:
        """Deserialize data from JSON.

        Args:
            data: JSON string

        Returns:
            Deserialized data

        Raises:
            MeasurementError: If deserialization fails

        Example:
            >>> data = serializer.deserialize('{"key": "value"}')
        """
        try:
            return json.loads(data)
        except json.JSONDecodeError as e:
            raise MeasurementError(f"Failed to deserialize JSON: {e}", measurement="serialization")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Serializer configuration

        Example:
            >>> data = serializer.to_dict()
        """
        return {
            "format": "json",
            "indent": self._indent,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(serializer)
        """
        return f"JsonSerializer(indent={self._indent})"


class Serializer:
    """Concrete implementation of a general serializer.

    This class provides serialization functionality for multiple formats.

    Attributes:
        _format: Serialization format
        _json_serializer: JSON serializer

    Example:
        >>> serializer = Serializer("json")
        >>> data = serializer.serialize({"key": "value"})
    """

    def __init__(self, format: SerializationFormat = "json") -> None:
        """Initialize a Serializer.

        Args:
            format: Serialization format

        Example:
            >>> serializer = Serializer("json")
        """
        self._format = format
        self._json_serializer = JsonSerializer()

    @property
    def format(self) -> SerializationFormat:
        """Get the serialization format.

        Returns:
            Serialization format

        Example:
            >>> print(f"Format: {serializer.format}")
        """
        return self._format

    def serialize(self, data: Dict[str, Any]) -> SerializedData:
        """Serialize data.

        Args:
            data: Data to serialize

        Returns:
            Serialized data

        Raises:
            MeasurementError: If format not supported

        Example:
            >>> serialized = serializer.serialize({"key": "value"})
        """
        if self._format == "json":
            return self._json_serializer.serialize(data)
        else:
            raise MeasurementError(f"Format {self._format} not supported", measurement="serialization")

    def deserialize(self, data: SerializedData) -> Dict[str, Any]:
        """Deserialize data.

        Args:
            data: Data to deserialize

        Returns:
            Deserialized data

        Raises:
            MeasurementError: If format not supported

        Example:
            >>> deserialized = serializer.deserialize('{"key": "value"}')
        """
        if self._format == "json":
            if isinstance(data, str):
                return self._json_serializer.deserialize(data)
            else:
                raise MeasurementError("Data must be a string for JSON deserialization", measurement="serialization")
        else:
            raise MeasurementError(f"Format {self._format} not supported", measurement="serialization")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Serializer configuration

        Example:
            >>> data = serializer.to_dict()
        """
        return {
            "format": self._format,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(serializer)
        """
        return f"Serializer(format={self._format})"


# Export
__all__ = [
    "JsonSerializer",
    "Serializer",
]
