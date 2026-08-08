"""
Serializers Module

This module provides serializer definitions for the Knowledge package.

Purpose
-------
Provide serializer management for knowledge serialization.

Responsibilities
----------------
- Define serializer structure
- Support serializer operations
- Support serializer validation
- Support serializer metadata

Dependencies
------------
typing (standard library)
json (standard library)
quantsmind.knowledge.enums (knowledge enumerations)
quantsmind.knowledge.exceptions (knowledge exceptions)
quantsmind.knowledge.types (knowledge types)
"""

from __future__ import annotations

import json
from typing import Any, Callable, Dict, List, Optional

from quantsmind.knowledge.enums import SerializationType
from quantsmind.knowledge.exceptions import SerializationError
from quantsmind.knowledge.types import ValidationResult


class Serializer:
    """Concrete implementation of a serializer.

    This class provides serializer functionality for knowledge serialization.

    Attributes:
        _id: Serializer ID
        _name: Serializer name
        _serialization_type: Serialization type
        _serialize_function: Serialize function
        _deserialize_function: Deserialize function
        _parameters: Serializer parameters
        _metadata: Serializer metadata

    Example:
        >>> serializer = Serializer("ser_001", "JSON Serializer", SerializationType.JSON)
        >>> serializer.serialize({"value": 42})
    """

    def __init__(
        self,
        serializer_id: str,
        name: str,
        serialization_type: SerializationType,
        serialize_function: Optional[Callable[[Any], str]] = None,
        deserialize_function: Optional[Callable[[str], Any]] = None,
        parameters: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a Serializer.

        Args:
            serializer_id: Serializer ID
            name: Serializer name
            serialization_type: Serialization type
            serialize_function: Serialize function
            deserialize_function: Deserialize function
            parameters: Serializer parameters
            metadata: Serializer metadata

        Example:
            >>> serializer = Serializer("ser_001", "JSON Serializer", SerializationType.JSON)
        """
        if not serializer_id:
            raise SerializationError("Serializer ID cannot be empty", {"serializer_id": serializer_id})

        if not name:
            raise SerializationError("Serializer name cannot be empty", {"name": name})

        self._id = serializer_id
        self._name = name
        self._serialization_type = serialization_type
        self._serialize_function = serialize_function
        self._deserialize_function = deserialize_function
        self._parameters = parameters or {}
        self._metadata = metadata or {}

    @property
    def id(self) -> str:
        """Get the serializer ID.

        Returns:
            Serializer ID

        Example:
            >>> sid = serializer.id
        """
        return self._id

    @property
    def name(self) -> str:
        """Get the serializer name.

        Returns:
            Serializer name

        Example:
            >>> name = serializer.name
        """
        return self._name

    @property
    def serialization_type(self) -> SerializationType:
        """Get the serialization type.

        Returns:
            Serialization type

        Example:
            >>> stype = serializer.serialization_type
        """
        return self._serialization_type

    @property
    def parameters(self) -> Dict[str, Any]:
        """Get the serializer parameters.

        Returns:
            Serializer parameters

        Example:
            >>> parameters = serializer.parameters
        """
        return self._parameters.copy()

    @property
    def metadata(self) -> Dict[str, Any]:
        """Get the serializer metadata.

        Returns:
            Serializer metadata

        Example:
            >>> metadata = serializer.metadata
        """
        return self._metadata.copy()

    def set_serialize_function(self, serialize_function: Callable[[Any], str]) -> None:
        """Set the serialize function.

        Args:
            serialize_function: Serialize function

        Example:
            >>> serializer.set_serialize_function(json.dumps)
        """
        self._serialize_function = serialize_function

    def set_deserialize_function(self, deserialize_function: Callable[[str], Any]) -> None:
        """Set the deserialize function.

        Args:
            deserialize_function: Deserialize function

        Example:
            >>> serializer.set_deserialize_function(json.loads)
        """
        self._deserialize_function = deserialize_function

    def set_parameter(self, key: str, value: Any) -> None:
        """Set a parameter.

        Args:
            key: Parameter key
            value: Parameter value

        Example:
            >>> serializer.set_parameter("indent", 2)
        """
        self._parameters[key] = value

    def serialize(self, data: Any) -> str:
        """Serialize data.

        Args:
            data: Data to serialize

        Returns:
            Serialized string

        Example:
            >>> serialized = serializer.serialize({"value": 42})
        """
        if self._serialize_function:
            try:
                return self._serialize_function(data)
            except Exception as e:
                raise SerializationError(f"Serialization failed: {str(e)}", {"serializer_id": self._id})

        # Default JSON serialization
        try:
            return json.dumps(data, **self._parameters)
        except Exception as e:
            raise SerializationError(f"JSON serialization failed: {str(e)}", {"serializer_id": self._id})

    def deserialize(self, serialized: str) -> Any:
        """Deserialize data.

        Args:
            serialized: Serialized string

        Returns:
            Deserialized data

        Example:
            >>> data = serializer.deserialize('{"value": 42}')
        """
        if self._deserialize_function:
            try:
                return self._deserialize_function(serialized)
            except Exception as e:
                raise SerializationError(f"Deserialization failed: {str(e)}", {"serializer_id": self._id})

        # Default JSON deserialization
        try:
            return json.loads(serialized)
        except Exception as e:
            raise SerializationError(f"JSON deserialization failed: {str(e)}", {"serializer_id": self._id})

    def serialize_all(self, data_list: List[Any]) -> List[str]:
        """Serialize multiple data items.

        Args:
            data_list: List of data to serialize

        Returns:
            List of serialized strings

        Example:
            >>> serialized = serializer.serialize_all([{"value": 42}, {"value": 43}])
        """
        return [self.serialize(data) for data in data_list]

    def deserialize_all(self, serialized_list: List[str]) -> List[Any]:
        """Deserialize multiple data items.

        Args:
            serialized_list: List of serialized strings

        Returns:
            List of deserialized data

        Example:
            >>> data = serializer.deserialize_all(['{"value": 42}', '{"value": 43}'])
        """
        return [self.deserialize(serialized) for serialized in serialized_list]

    def validate(self) -> ValidationResult:
        """Validate the serializer.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = serializer.validate()
        """
        errors = []

        if not self._id:
            errors.append("Serializer ID cannot be empty")

        if not self._name:
            errors.append("Serializer name cannot be empty")

        return (len(errors) == 0, errors)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Serializer definition

        Example:
            >>> data = serializer.to_dict()
        """
        return {
            "id": self._id,
            "name": self._name,
            "serialization_type": self._serialization_type.value,
            "parameters": self._parameters,
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(serializer)
        """
        return f"Serializer(id={self._id}, name={self._name}, type={self._serialization_type.value})"


class SerializerRegistry:
    """Registry for serializers.

    This class provides serializer registry functionality.

    Attributes:
        _serializers: Registered serializers

    Example:
        >>> registry = SerializerRegistry()
        >>> registry.register(Serializer("ser_001", "JSON Serializer", SerializationType.JSON))
    """

    def __init__(self) -> None:
        """Initialize a SerializerRegistry.

        Example:
            >>> registry = SerializerRegistry()
        """
        self._serializers: Dict[str, Serializer] = {}

    def register(self, serializer: Serializer) -> None:
        """Register a serializer.

        Args:
            serializer: Serializer to register

        Example:
            >>> registry.register(Serializer("ser_001", "JSON Serializer", SerializationType.JSON))
        """
        self._serializers[serializer.id] = serializer

    def unregister(self, serializer_id: str) -> bool:
        """Unregister a serializer.

        Args:
            serializer_id: Serializer ID

        Returns:
            True if unregistered

        Example:
            >>> unregistered = registry.unregister("ser_001")
        """
        if serializer_id in self._serializers:
            del self._serializers[serializer_id]
            return True
        return False

    def get(self, serializer_id: str) -> Optional[Serializer]:
        """Get a serializer by ID.

        Args:
            serializer_id: Serializer ID

        Returns:
            Serializer or None

        Example:
            >>> serializer = registry.get("ser_001")
        """
        return self._serializers.get(serializer_id)

    def get_by_type(self, serialization_type: SerializationType) -> List[Serializer]:
        """Get serializers by type.

        Args:
            serialization_type: Serialization type

        Returns:
            List of serializers

        Example:
            >>> serializers = registry.get_by_type(SerializationType.JSON)
        """
        return [s for s in self._serializers.values() if s.serialization_type == serialization_type]

    def list_all(self) -> List[Serializer]:
        """List all registered serializers.

        Returns:
            List of serializers

        Example:
            >>> serializers = registry.list_all()
        """
        return list(self._serializers.values())

    def count(self) -> int:
        """Get the number of registered serializers.

        Returns:
            Number of serializers

        Example:
            >>> count = registry.count()
        """
        return len(self._serializers)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Registry state

        Example:
            >>> data = registry.to_dict()
        """
        return {
            "serializers": [serializer.to_dict() for serializer in self._serializers.values()],
            "count": len(self._serializers),
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(registry)
        """
        return f"SerializerRegistry(serializers={len(self._serializers)})"


# Export
__all__ = [
    "Serializer",
    "SerializerRegistry",
]
