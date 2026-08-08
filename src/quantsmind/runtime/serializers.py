"""
Runtime Serializers Module

This module provides serialization functions for the Runtime package.

Purpose
-------
Provide serialization functions for the QuantsMind SDK.

Responsibilities
----------------
- Serialize to JSON
- Serialize to YAML
- Serialize to TOML
- Support custom serializers

Dependencies
------------
typing (standard library)
logging (standard library)
json (standard library)
quantsmind.runtime.constants (runtime constants)
quantsmind.runtime.types (runtime types)
quantsmind.runtime.exceptions (runtime exceptions)
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, Optional

from quantsmind.runtime.exceptions import ConfigurationError
from quantsmind.runtime.types import SerializationFormat

logger = logging.getLogger(__name__)


class JsonSerializer:
    """Concrete implementation of a JSON serializer.

    This class provides JSON serialization capabilities.

    Example:
        >>> serializer = JsonSerializer()
        >>> data = serializer.serialize({"key": "value"})
    """

    def serialize(self, data: Any, indent: int = 2) -> str:
        """Serialize data to JSON.

        Args:
            data: Data to serialize
            indent: Indentation level

        Returns:
            JSON string

        Raises:
            ConfigurationError: If serialization fails

        Example:
            >>> data = serializer.serialize({"key": "value"})
        """
        try:
            return json.dumps(data, indent=indent, default=str)
        except Exception as e:
            raise ConfigurationError(f"JSON serialization failed: {str(e)}") from e

    def deserialize(self, data: str) -> Any:
        """Deserialize data from JSON.

        Args:
            data: JSON string

        Returns:
            Deserialized data

        Raises:
            ConfigurationError: If deserialization fails

        Example:
            >>> data = serializer.deserialize('{"key": "value"}')
        """
        try:
            return json.loads(data)
        except Exception as e:
            raise ConfigurationError(f"JSON deserialization failed: {str(e)}") from e


class Serializer:
    """Concrete implementation of a serializer.

    This class provides serialization capabilities for multiple formats.

    Attributes:
        _json_serializer: JSON serializer
        _format: Default format

    Example:
        >>> serializer = Serializer()
        >>> data = serializer.serialize({"key": "value"}, format="json")
    """

    def __init__(self, default_format: SerializationFormat = "json") -> None:
        """Initialize a Serializer.

        Args:
            default_format: Default serialization format

        Example:
            >>> serializer = Serializer()
        """
        self._json_serializer = JsonSerializer()
        self._format = default_format
        logger.debug("Created serializer")

    def serialize(
        self,
        data: Any,
        format: Optional[SerializationFormat] = None,
        **kwargs: Any
    ) -> str:
        """Serialize data to specified format.

        Args:
            data: Data to serialize
            format: Serialization format
            **kwargs: Additional arguments

        Returns:
            Serialized string

        Raises:
            ConfigurationError: If format is not supported

        Example:
            >>> data = serializer.serialize({"key": "value"}, format="json")
        """
        fmt = format or self._format

        if fmt == "json":
            return self._json_serializer.serialize(data, **kwargs)
        else:
            raise ConfigurationError(f"Unsupported format: {fmt}")

    def deserialize(
        self,
        data: str,
        format: Optional[SerializationFormat] = None,
        **kwargs: Any
    ) -> Any:
        """Deserialize data from specified format.

        Args:
            data: Serialized string
            format: Serialization format
            **kwargs: Additional arguments

        Returns:
            Deserialized data

        Raises:
            ConfigurationError: If format is not supported

        Example:
            >>> data = serializer.deserialize('{"key": "value"}', format="json")
        """
        fmt = format or self._format

        if fmt == "json":
            return self._json_serializer.deserialize(data, **kwargs)
        else:
            raise ConfigurationError(f"Unsupported format: {fmt}")


# Export
__all__ = [
    "JsonSerializer",
    "Serializer",
]
