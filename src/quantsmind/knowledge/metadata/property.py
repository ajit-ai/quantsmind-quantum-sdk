"""
Property Module

This module provides property definitions for the Knowledge package.

Purpose
-------
Provide property management for knowledge items.

Responsibilities
----------------
- Define property structure
- Support property operations
- Support property validation
- Support property metadata

Dependencies
------------
typing (standard library)
datetime (standard library)
quantsmind.knowledge.enums (knowledge enumerations)
quantsmind.knowledge.exceptions (knowledge exceptions)
quantsmind.knowledge.types (knowledge types)
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from quantsmind.knowledge.enums import MetadataType
from quantsmind.knowledge.exceptions import MetadataError
from quantsmind.knowledge.types import Property


class Property:
    """Concrete implementation of a property.

    This class provides property functionality.

    Attributes:
        _name: Property name
        _value: Property value
        _data_type: Property data type
        _required: Whether property is required
        _read_only: Whether property is read-only
        _metadata: Property metadata

    Example:
        >>> prop = Property("length", 42.0, "float", required=True)
        >>> prop.name
    """

    def __init__(
        self,
        name: str,
        value: Any,
        data_type: str = "string",
        required: bool = False,
        read_only: bool = False,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a Property.

        Args:
            name: Property name
            value: Property value
            data_type: Property data type
            required: Whether property is required
            read_only: Whether property is read-only
            metadata: Property metadata

        Example:
            >>> prop = Property("length", 42.0, "float", required=True)
        """
        if not name:
            raise MetadataError("Property name cannot be empty")

        self._name = name
        self._value = value
        self._data_type = data_type
        self._required = required
        self._read_only = read_only
        self._metadata = metadata or {}

    @property
    def name(self) -> str:
        """Get the property name.

        Returns:
            Property name

        Example:
            >>> name = prop.name
        """
        return self._name

    @property
    def value(self) -> Any:
        """Get the property value.

        Returns:
            Property value

        Example:
            >>> value = prop.value
        """
        return self._value

    @property
    def data_type(self) -> str:
        """Get the property data type.

        Returns:
            Property data type

        Example:
            >>> dtype = prop.data_type
        """
        return self._data_type

    @property
    def required(self) -> bool:
        """Get whether property is required.

        Returns:
            True if required

        Example:
            >>> required = prop.required
        """
        return self._required

    @property
    def read_only(self) -> bool:
        """Get whether property is read-only.

        Returns:
            True if read-only

        Example:
            >>> read_only = prop.read_only
        """
        return self._read_only

    @property
    def metadata(self) -> Dict[str, Any]:
        """Get the property metadata.

        Returns:
            Property metadata

        Example:
            >>> metadata = prop.metadata
        """
        return self._metadata.copy()

    def set_value(self, value: Any) -> None:
        """Set the property value.

        Args:
            value: Property value

        Raises:
            MetadataError: If property is read-only

        Example:
            >>> prop.set_value(43.0)
        """
        if self._read_only:
            raise MetadataError("Property is read-only", {"property": self._name})
        self._value = value

    def validate_type(self, value: Any) -> bool:
        """Validate value against data type.

        Args:
            value: Value to validate

        Returns:
            True if valid

        Example:
            >>> valid = prop.validate_type(42.0)
        """
        type_map = {
            "string": str,
            "int": int,
            "float": float,
            "bool": bool,
            "list": list,
            "dict": dict,
        }

        expected_type = type_map.get(self._data_type, str)
        return isinstance(value, expected_type)

    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to the property.

        Args:
            key: Metadata key
            value: Metadata value

        Example:
            >>> prop.add_metadata("unit", "m")
        """
        self._metadata[key] = value

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Property definition

        Example:
            >>> data = prop.to_dict()
        """
        return {
            "name": self._name,
            "value": self._value,
            "data_type": self._data_type,
            "required": self._required,
            "read_only": self._read_only,
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(prop)
        """
        return f"Property(name={self._name}, value={self._value}, type={self._data_type})"


class PropertySet:
    """Set of properties for a knowledge item.

    This class provides property set functionality.

    Attributes:
        _properties: Properties in the set

    Example:
        >>> propset = PropertySet()
        >>> propset.add_property(Property("length", 42.0))
    """

    def __init__(self, properties: Optional[list[Property]] = None) -> None:
        """Initialize a PropertySet.

        Args:
            properties: Initial properties

        Example:
            >>> propset = PropertySet()
        """
        self._properties: Dict[str, Property] = {}
        if properties:
            for prop in properties:
                self.add_property(prop)

    def add_property(self, property: Property) -> None:
        """Add a property to the set.

        Args:
            property: Property to add

        Example:
            >>> propset.add_property(Property("length", 42.0))
        """
        self._properties[property.name] = property

    def remove_property(self, name: str) -> bool:
        """Remove a property from the set.

        Args:
            name: Property name

        Returns:
            True if removed

        Example:
            >>> removed = propset.remove_property("length")
        """
        if name in self._properties:
            del self._properties[name]
            return True
        return False

    def get_property(self, name: str) -> Optional[Property]:
        """Get a property by name.

        Args:
            name: Property name

        Returns:
            Property or None

        Example:
            >>> prop = propset.get_property("length")
        """
        return self._properties.get(name)

    def get_required_properties(self) -> list[Property]:
        """Get required properties.

        Returns:
            List of required properties

        Example:
            >>> props = propset.get_required_properties()
        """
        return [prop for prop in self._properties.values() if prop.required]

    def validate_all(self) -> tuple[bool, list[str]]:
        """Validate all properties.

        Returns:
            (is_valid, errors)

        Example:
            >>> valid, errors = propset.validate_all()
        """
        errors = []

        for prop in self._properties.values():
            if prop.required and prop.value is None:
                errors.append(f"Required property '{prop.name}' is missing")

            if prop.value is not None and not prop.validate_type(prop.value):
                errors.append(f"Property '{prop.name}' has invalid type")

        return (len(errors) == 0, errors)

    def list_all(self) -> list[Property]:
        """List all properties.

        Returns:
            List of properties

        Example:
            >>> props = propset.list_all()
        """
        return list(self._properties.values())

    def count(self) -> int:
        """Get the number of properties.

        Returns:
            Number of properties

        Example:
            >>> count = propset.count()
        """
        return len(self._properties)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Property set definition

        Example:
            >>> data = propset.to_dict()
        """
        return {
            "properties": [prop.to_dict() for prop in self._properties.values()],
            "count": len(self._properties),
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(propset)
        """
        return f"PropertySet(count={len(self._properties)})"


# Export
__all__ = [
    "Property",
    "PropertySet",
]
