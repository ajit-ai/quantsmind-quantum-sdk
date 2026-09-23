"""
Serializers Module

This module provides common serialization utilities for the Foundation package.
Serializers provide reusable serialization logic for foundation objects.

Purpose
-------
Provide common serialization utilities for the Foundation package.

Scientific Meaning
------------------
Serializers enable data persistence and transmission in scientific computing applications,
ensuring data can be saved, loaded, and shared across systems.

Responsibilities
----------------
- Provide common serialization functions
- Support JSON serialization
- Enable format conversion
- Support custom serializers

Dependencies
------------
typing (standard library)
json (standard library)
quantsmind.foundation.exceptions (exception hierarchy)
quantsmind.foundation.types (type definitions)

Future Extensions
-----------------
- Binary serializers
- Compression support
- Streaming serializers
- Async serializers
"""

from __future__ import annotations

import json
import logging
from typing import Any

from quantsmind.foundation.enums import SerializationFormat
from quantsmind.foundation.exceptions import SerializationError
from quantsmind.foundation.interfaces import Serializable

logger = logging.getLogger(__name__)


def to_json(obj: Any, indent: int | None = None) -> str:
    """Convert an object to JSON string.

    Args:
        obj: Object to serialize
        indent: JSON indentation level

    Returns:
        JSON string

    Raises:
        SerializationError: If serialization fails

    Example:
        >>> json_str = to_json({"key": "value"}, indent=2)
    """
    try:
        return json.dumps(obj, indent=indent, default=str)
    except (TypeError, ValueError) as e:
        raise SerializationError(f"Failed to serialize to JSON: {e}") from e


def from_json(json_str: str) -> Any:
    """Convert a JSON string to an object.

    Args:
        json_str: JSON string to deserialize

    Returns:
        Deserialized object

    Raises:
        SerializationError: If deserialization fails

    Example:
        >>> obj = from_json('{"key": "value"}')
    """
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, ValueError) as e:
        raise SerializationError(f"Failed to deserialize from JSON: {e}") from e


def serialize_to_dict(obj: Serializable) -> dict[str, Any]:
    """Serialize a Serializable object to a dictionary.

    Args:
        obj: Serializable object

    Returns:
        Dictionary representation

    Raises:
        SerializationError: If serialization fails

    Example:
        >>> data_dict = serialize_to_dict(serializable_obj)
    """
    try:
        data = obj.serialize(format=SerializationFormat.JSON)
        result: dict[str, Any] = from_json(data.decode("utf-8"))
        return result
    except Exception as e:
        raise SerializationError(f"Failed to serialize to dict: {e}") from e


def deserialize_from_dict(cls: type[Serializable], data: dict[str, Any]) -> Any:
    """Deserialize an object from a dictionary.

    Args:
        cls: Class to deserialize to
        data: Dictionary data

    Returns:
        Deserialized object

    Raises:
        SerializationError: If deserialization fails

    Example:
        >>> obj = deserialize_from_dict(MyClass, {"key": "value"})
    """
    try:
        json_str = to_json(data)
        return cls.deserialize(json_str.encode("utf-8"), format=SerializationFormat.JSON)
    except Exception as e:
        raise SerializationError(f"Failed to deserialize from dict: {e}") from e


def serialize_to_file(
    obj: Serializable,
    filepath: str,
    format: SerializationFormat = SerializationFormat.JSON,
) -> None:
    """Serialize a Serializable object to a file.

    Args:
        obj: Serializable object
        filepath: File path to write to
        format: Serialization format

    Raises:
        SerializationError: If serialization fails

    Example:
        >>> serialize_to_file(serializable_obj, "data.json")
    """
    try:
        data = obj.serialize(format=format)
        with open(filepath, "wb") as f:
            f.write(data)
        logger.debug(f"Serialized object to {filepath}")
    except Exception as e:
        raise SerializationError(f"Failed to serialize to file: {e}") from e


def deserialize_from_file(
    cls: type[Serializable],
    filepath: str,
    format: SerializationFormat = SerializationFormat.JSON,
) -> Any:
    """Deserialize an object from a file.

    Args:
        cls: Class to deserialize to
        filepath: File path to read from
        format: Serialization format

    Returns:
        Deserialized object

    Raises:
        SerializationError: If deserialization fails

    Example:
        >>> obj = deserialize_from_file(MyClass, "data.json")
    """
    try:
        with open(filepath, "rb") as f:
            data = f.read()
        obj = cls.deserialize(data, format=format)
        logger.debug(f"Deserialized object from {filepath}")
        return obj
    except Exception as e:
        raise SerializationError(f"Failed to deserialize from file: {e}") from e


class Serializer:
    """Base class for custom serializers.

    This class provides a framework for creating reusable serializers
    with custom serialization logic.

    Example:
        >>> class CustomSerializer(Serializer):
        ...     def serialize(self, obj: Any) -> bytes:
        ...         return to_json(obj).encode("utf-8")
        ...     def deserialize(self, data: bytes) -> Any:
        ...         return from_json(data.decode("utf-8"))
    """

    def serialize(self, obj: Any) -> bytes:
        """Serialize an object to bytes.

        Args:
            obj: Object to serialize

        Returns:
            Serialized data as bytes

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement serialize method")

    def deserialize(self, data: bytes) -> Any:
        """Deserialize bytes to an object.

        Args:
            data: Serialized data

        Returns:
            Deserialized object

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement deserialize method")


class JSONSerializer(Serializer):
    """JSON serializer implementation.

    This class provides a standard JSON serializer for common use cases.

    Example:
        >>> serializer = JSONSerializer()
        >>> data = serializer.serialize({"key": "value"})
        >>> obj = serializer.deserialize(data)
    """

    def serialize(self, obj: Any) -> bytes:
        """Serialize an object to JSON bytes.

        Args:
            obj: Object to serialize

        Returns:
            Serialized data as bytes

        Example:
            >>> data = serializer.serialize({"key": "value"})
        """
        return to_json(obj).encode("utf-8")

    def deserialize(self, data: bytes) -> Any:
        """Deserialize JSON bytes to an object.

        Args:
            data: Serialized data

        Returns:
            Deserialized object

        Example:
            >>> obj = serializer.deserialize(data)
        """
        return from_json(data.decode("utf-8"))


# Export
__all__ = [
    "to_json",
    "from_json",
    "serialize_to_dict",
    "deserialize_from_dict",
    "serialize_to_file",
    "deserialize_from_file",
    "Serializer",
    "JSONSerializer",
]
