"""
Attribute Module

This module provides attribute definitions for the Knowledge package.

Purpose
-------
Provide attribute management for knowledge items.

Responsibilities
----------------
- Define attribute structure
- Support attribute operations
- Support attribute validation
- Support attribute metadata

Dependencies
------------
typing (standard library)
datetime (standard library)
quantsmind.knowledge.enums (knowledge enumerations)
quantsmind.knowledge.exceptions (knowledge exceptions)
quantsmind.knowledge.types (knowledge types)
"""

from __future__ import annotations

from typing import Any

from quantsmind.knowledge.exceptions import MetadataError


class Attribute:
    """Concrete implementation of an attribute.

    This class provides attribute functionality.

    Attributes:
        _name: Attribute name
        _value: Attribute value
        _attribute_type: Attribute type
        _default_value: Default value
        _metadata: Attribute metadata

    Example:
        >>> attr = Attribute("color", "red", "string", default="blue")
        >>> attr.name
    """

    def __init__(
        self,
        name: str,
        value: Any,
        attribute_type: str = "string",
        default: Any | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize an Attribute.

        Args:
            name: Attribute name
            value: Attribute value
            attribute_type: Attribute type
            default: Default value
            metadata: Attribute metadata

        Example:
            >>> attr = Attribute("color", "red", "string", default="blue")
        """
        if not name:
            raise MetadataError("Attribute name cannot be empty")

        self._name = name
        self._value = value
        self._attribute_type = attribute_type
        self._default_value = default
        self._metadata = metadata or {}

    @property
    def name(self) -> str:
        """Get the attribute name.

        Returns:
            Attribute name

        Example:
            >>> name = attr.name
        """
        return self._name

    @property
    def value(self) -> Any:
        """Get the attribute value.

        Returns:
            Attribute value

        Example:
            >>> value = attr.value
        """
        return self._value

    @property
    def attribute_type(self) -> str:
        """Get the attribute type.

        Returns:
            Attribute type

        Example:
            >>> atype = attr.attribute_type
        """
        return self._attribute_type

    @property
    def default_value(self) -> Any | None:
        """Get the default value.

        Returns:
            Default value

        Example:
            >>> default = attr.default_value
        """
        return self._default_value

    @property
    def metadata(self) -> dict[str, Any]:
        """Get the attribute metadata.

        Returns:
            Attribute metadata

        Example:
            >>> metadata = attr.metadata
        """
        return self._metadata.copy()

    def set_value(self, value: Any) -> None:
        """Set the attribute value.

        Args:
            value: Attribute value

        Example:
            >>> attr.set_value("green")
        """
        self._value = value

    def reset_to_default(self) -> None:
        """Reset attribute to default value.

        Example:
            >>> attr.reset_to_default()
        """
        if self._default_value is not None:
            self._value = self._default_value

    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to the attribute.

        Args:
            key: Metadata key
            value: Metadata value

        Example:
            >>> attr.add_metadata("description", "Color attribute")
        """
        self._metadata[key] = value

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Attribute definition

        Example:
            >>> data = attr.to_dict()
        """
        return {
            "name": self._name,
            "value": self._value,
            "attribute_type": self._attribute_type,
            "default_value": self._default_value,
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(attr)
        """
        return f"Attribute(name={self._name}, value={self._value}, type={self._attribute_type})"


class AttributeSet:
    """Set of attributes for a knowledge item.

    This class provides attribute set functionality.

    Attributes:
        _attributes: Attributes in the set

    Example:
        >>> attrset = AttributeSet()
        >>> attrset.add_attribute(Attribute("color", "red"))
    """

    def __init__(self, attributes: list[Attribute] | None = None) -> None:
        """Initialize an AttributeSet.

        Args:
            attributes: Initial attributes

        Example:
            >>> attrset = AttributeSet()
        """
        self._attributes: dict[str, Attribute] = {}
        if attributes:
            for attr in attributes:
                self.add_attribute(attr)

    def add_attribute(self, attribute: Attribute) -> None:
        """Add an attribute to the set.

        Args:
            attribute: Attribute to add

        Example:
            >>> attrset.add_attribute(Attribute("color", "red"))
        """
        self._attributes[attribute.name] = attribute

    def remove_attribute(self, name: str) -> bool:
        """Remove an attribute from the set.

        Args:
            name: Attribute name

        Returns:
            True if removed

        Example:
            >>> removed = attrset.remove_attribute("color")
        """
        if name in self._attributes:
            del self._attributes[name]
            return True
        return False

    def get_attribute(self, name: str) -> Attribute | None:
        """Get an attribute by name.

        Args:
            name: Attribute name

        Returns:
            Attribute or None

        Example:
            >>> attr = attrset.get_attribute("color")
        """
        return self._attributes.get(name)

    def get_attributes_by_type(self, attribute_type: str) -> list[Attribute]:
        """Get attributes by type.

        Args:
            attribute_type: Attribute type

        Returns:
            List of attributes

        Example:
            >>> attrs = attrset.get_attributes_by_type("string")
        """
        return [attr for attr in self._attributes.values() if attr.attribute_type == attribute_type]

    def reset_all_to_defaults(self) -> None:
        """Reset all attributes to default values.

        Example:
            >>> attrset.reset_all_to_defaults()
        """
        for attr in self._attributes.values():
            attr.reset_to_default()

    def list_all(self) -> list[Attribute]:
        """List all attributes.

        Returns:
            List of attributes

        Example:
            >>> attrs = attrset.list_all()
        """
        return list(self._attributes.values())

    def count(self) -> int:
        """Get the number of attributes.

        Returns:
            Number of attributes

        Example:
            >>> count = attrset.count()
        """
        return len(self._attributes)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Attribute set definition

        Example:
            >>> data = attrset.to_dict()
        """
        return {
            "attributes": [attr.to_dict() for attr in self._attributes.values()],
            "count": len(self._attributes),
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(attrset)
        """
        return f"AttributeSet(count={len(self._attributes)})"


# Export
__all__ = [
    "Attribute",
    "AttributeSet",
]
