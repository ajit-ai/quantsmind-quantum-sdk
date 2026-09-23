"""
Property Module

This module provides named characteristics for entities within the QuantsMind SDK.
Properties represent qualitative or quantitative characteristics (mass, charge, spin, position, momentum).

Purpose
-------
Provide structured named characteristics for entities in the Foundation package.

Scientific Meaning
------------------
Properties represent qualitative or quantitative characteristics like mass, charge,
spin, position, momentum, or any other measurable or descriptive attribute of entities.

Responsibilities
----------------
- Manage property metadata
- Support property validation
- Enable property serialization
- Handle property inheritance
- Support property constraints

Dependencies
------------
typing (standard library)
logging (standard library)
quantsmind.foundation.exceptions (exception hierarchy)
quantsmind.foundation.constants (constant values)
quantsmind.foundation.types (type definitions)
quantsmind.foundation.interfaces (abstract interfaces)
quantsmind.foundation.attribute (attribute values)

Future Extensions
-----------------
- Property composition
- Property derivation
- Property caching
- Property optimization
"""

from __future__ import annotations

import logging
from typing import Any

from quantsmind.foundation.attribute import Attribute
from quantsmind.foundation.constants import (
    DEFAULT_PROPERTY_TYPE,
    ERROR_INVALID_PROPERTY,
    MAX_NAME_LENGTH,
    RESERVED_PROPERTY_NAMES,
)
from quantsmind.foundation.enums import SerializationFormat
from quantsmind.foundation.exceptions import (
    InvalidPropertyError,
)
from quantsmind.foundation.interfaces import (
    Serializable,
    Validatable,
)
from quantsmind.foundation.types import (
    MetadataDict,
    SerializedData,
    ValidationResult,
)

logger = logging.getLogger(__name__)


class Property(Serializable, Validatable):
    """Concrete implementation of named characteristics for entities.

    This class provides structured named characteristics with support for
    typed values, units, and constraints.

    Scientific Meaning
    ------------------
    In scientific computing, properties represent characteristics like mass,
    charge, spin, position, momentum, or any other measurable quantity.

    Attributes:
        _name: Property name
        _value: Property value (Attribute)
        _property_type: Property type
        _unit: Optional unit for the property
        _description: Optional description
        _metadata: Additional metadata
        _constraints: List of constraints

    Example:
        >>> prop = Property(name="mass", value=Attribute(value=42.0, type="scalar"), unit="kg")
        >>> print(f"Property: {prop.name} = {prop.value}")
    """

    def __init__(
        self,
        name: str,
        value: Attribute,
        property_type: str = DEFAULT_PROPERTY_TYPE,
        unit: str | None = None,
        description: str | None = None,
        metadata: MetadataDict | None = None,
    ) -> None:
        """Initialize a Property.

        Args:
            name: Property name
            value: Property value as Attribute
            property_type: Property type
            unit: Optional unit for the property
            description: Optional description
            metadata: Optional metadata dictionary

        Raises:
            InvalidPropertyError: If name is invalid or reserved
            ValueError: If name exceeds maximum length

        Example:
            >>> prop = Property(
            ...     name="mass",
            ...     value=Attribute(value=42.0, type="scalar"),
            ...     unit="kg"
            ... )
        """
        self._name: str = name
        self._value: Attribute = value
        self._property_type: str = property_type
        self._unit: str | None = unit
        self._description: str | None = description
        self._metadata: MetadataDict = metadata or {}

        self._validate_name()
        logger.debug(f"Created property: {name}")

    def _validate_name(self) -> None:
        """Validate the property name.

        Raises:
            InvalidPropertyError: If name is invalid or reserved
            ValueError: If name exceeds maximum length
        """
        if not self._name or not isinstance(self._name, str):
            raise InvalidPropertyError(
                "Property name must be a non-empty string",
                error_code=ERROR_INVALID_PROPERTY,
            )

        if len(self._name) > MAX_NAME_LENGTH:
            raise ValueError(f"Property name exceeds maximum length of {MAX_NAME_LENGTH}")

        if self._name in RESERVED_PROPERTY_NAMES:
            raise InvalidPropertyError(
                f"Property name '{self._name}' is reserved",
                error_code=ERROR_INVALID_PROPERTY,
            )

    @property
    def name(self) -> str:
        """Get the property name.

        Returns:
            Property name

        Example:
            >>> print(f"Property: {property.name}")
        """
        return self._name

    @property
    def value(self) -> Attribute:
        """Get the property value.

        Returns:
            Property value as Attribute

        Example:
            >>> print(f"Value: {property.value}")
        """
        return self._value

    @property
    def property_type(self) -> str:
        """Get the property type.

        Returns:
            Property type

        Example:
            >>> print(f"Type: {property.property_type}")
        """
        return self._property_type

    @property
    def unit(self) -> str | None:
        """Get the property unit.

        Returns:
            Unit string or None

        Example:
            >>> print(f"Unit: {property.unit}")
        """
        return self._unit

    @property
    def description(self) -> str | None:
        """Get the property description.

        Returns:
            Description string or None

        Example:
            >>> print(f"Description: {property.description}")
        """
        return self._description

    @property
    def metadata(self) -> MetadataDict:
        """Get the property metadata.

        Returns:
            Metadata dictionary

        Example:
            >>> print(f"Metadata: {property.metadata}")
        """
        return self._metadata.copy()

    @property
    def has_unit(self) -> bool:
        """Check if property has a unit.

        Returns:
            True if has unit, False otherwise

        Example:
            >>> if property.has_unit:
            ...     print(f"Unit: {property.unit}")
        """
        return self._unit is not None

    def set_value(self, value: Attribute) -> None:
        """Set the property value.

        Args:
            value: New value as Attribute

        Example:
            >>> property.set_value(Attribute(value=43.0, type="scalar"))
        """
        old_value = self._value
        self._value = value
        logger.debug(f"Updated property {self._name} value: {old_value} -> {value}")

    def set_unit(self, unit: str) -> None:
        """Set the property unit.

        Args:
            unit: New unit

        Example:
            >>> property.set_unit("m")
        """
        self._unit = unit
        logger.debug(f"Updated property {self._name} unit: {unit}")

    def set_description(self, description: str) -> None:
        """Set the property description.

        Args:
            description: New description

        Example:
            >>> property.set_description("Particle mass")
        """
        self._description = description
        logger.debug(f"Updated property {self._name} description")

    def update_metadata(self, metadata: MetadataDict) -> None:
        """Update the property metadata.

        Args:
            metadata: New metadata dictionary (will be merged with existing)

        Example:
            >>> property.update_metadata({"source": "measurement"})
        """
        self._metadata.update(metadata)
        logger.debug(f"Updated property {self._name} metadata")

    # Serializable interface implementation
    def serialize(
        self, format: SerializationFormat | str = SerializationFormat.JSON
    ) -> SerializedData:
        """Serialize the property to bytes.

        Args:
            format: Serialization format (currently only "json" supported)

        Returns:
            Serialized data as bytes

        Raises:
            NotImplementedError: If format is not supported

        Example:
            >>> data = property.serialize(format=SerializationFormat.JSON)
        """
        is_json = format is SerializationFormat.JSON or (
            isinstance(format, str) and format.lower() == "json"
        )
        if not is_json:
            raise NotImplementedError(f"Serialization format '{format}' not yet implemented")

        import json

        data = {
            "name": self._name,
            "value": self._value.serialize(format="json").decode("utf-8"),
            "type": self._property_type,
            "unit": self._unit,
            "description": self._description,
            "metadata": self._metadata,
        }
        return json.dumps(data).encode("utf-8")

    @classmethod
    def deserialize(
        cls, data: SerializedData, format: SerializationFormat | str = SerializationFormat.JSON
    ) -> Property:
        """Deserialize the property from bytes.

        Args:
            data: Serialized data as bytes
            format: Serialization format (currently only "json" supported)

        Returns:
            Deserialized Property instance

        Raises:
            NotImplementedError: If format is not supported
            InvalidPropertyError: If data is invalid

        Example:
            >>> property = Property.deserialize(data, format=SerializationFormat.JSON)
        """
        is_json = format is SerializationFormat.JSON or (
            isinstance(format, str) and format.lower() == "json"
        )
        if not is_json:
            raise NotImplementedError(f"Serialization format '{format}' not yet implemented")

        import json

        try:
            obj = json.loads(data.decode("utf-8"))
            value = Attribute.deserialize(
                obj["value"].encode("utf-8"), format="json"
            )
            return cls(
                name=obj["name"],
                value=value,
                property_type=obj["type"],
                unit=obj.get("unit"),
                description=obj.get("description"),
                metadata=obj.get("metadata"),
            )
        except (json.JSONDecodeError, KeyError) as e:
            raise InvalidPropertyError(
                f"Failed to deserialize property: {e}",
                error_code=ERROR_INVALID_PROPERTY,
            ) from e

    def is_serializable(self) -> bool:
        """Check if the property is serializable.

        Returns:
            True (properties are always serializable)

        Example:
            >>> if property.is_serializable():
            ...     data = property.serialize()
        """
        return True

    @classmethod
    def get_supported_formats(cls) -> list[SerializationFormat]:
        """Get supported serialization formats.

        Returns:
            List of supported formats

        Example:
            >>> formats = Property.get_supported_formats()
        """
        return [SerializationFormat.JSON]

    # Validatable interface implementation
    def validate(self) -> ValidationResult:
        """Validate the property.

        Returns:
            Tuple of (is_valid, error_messages)

        Example:
            >>> is_valid, errors = property.validate()
        """
        errors: list[str] = []

        try:
            self._validate_name()
        except (InvalidPropertyError, ValueError) as e:
            errors.append(str(e))

        # Validate the attribute value
        is_value_valid, value_errors = self._value.validate()
        if not is_value_valid:
            errors.extend([f"Value error: {err}" for err in value_errors])

        return (len(errors) == 0, errors)

    @property
    def validation_errors(self) -> list[str]:
        """Get validation errors.

        Returns:
            List of error messages

        Example:
            >>> errors = property.validation_errors
        """
        is_valid, errors = self.validate()
        return errors if not is_valid else []

    @property
    def validation_warnings(self) -> list[str]:
        """Get validation warnings.

        Returns:
            List of warning messages (currently empty)

        Example:
            >>> warnings = property.validation_warnings
        """
        return []

    # Object protocol methods
    def __repr__(self) -> str:
        """Return string representation of the property.

        Returns:
            String representation

        Example:
            >>> repr(property)
        """
        return f"Property(name='{self._name}', value={self._value}, unit='{self._unit}')"

    def __str__(self) -> str:
        """Return string representation of the property.

        Returns:
            String representation

        Example:
            >>> str(property)
        """
        if self._unit:
            return f"{self._name}: {self._value} {self._unit}"
        return f"{self._name}: {self._value}"

    def __eq__(self, other: Any) -> bool:
        """Check equality.

        Args:
            other: Object to compare with

        Returns:
            True if equal, False otherwise

        Example:
            >>> prop1 == prop2
        """
        if not isinstance(other, Property):
            return False
        return self._name == other._name and self._value == other._value

    def __hash__(self) -> int:
        """Return hash of the property.

        Returns:
            Hash value

        Example:
            >>> hash(property)
        """
        return hash((self._name, self._value))


# Export
__all__ = ["Property"]
