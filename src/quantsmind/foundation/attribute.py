"""
Attribute Module

This module provides typed values for properties within the QuantsMind SDK.
Attributes represent concrete values with types (scalars, vectors, tensors, complex numbers).

Purpose
-------
Provide type-safe value representation for properties in the Foundation package.

Scientific Meaning
------------------
Attributes represent concrete values with types (scalars, vectors, tensors, complex numbers)
that characterize entities in scientific computing.

Responsibilities
----------------
- Manage attribute typing
- Support attribute validation
- Enable attribute serialization
- Handle attribute conversion
- Support attribute comparison

Dependencies
------------
typing (standard library)
logging (standard library)
quantsmind.foundation.exceptions (exception hierarchy)
quantsmind.foundation.constants (constant values)
quantsmind.foundation.types (type definitions)
quantsmind.foundation.interfaces (abstract interfaces)

Future Extensions
-----------------
- Attribute units and dimensions
- Attribute precision control
- Attribute lazy evaluation
- Attribute streaming
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Union

from quantsmind.foundation.constants import (
    DEFAULT_ATTRIBUTE_TYPE,
    ERROR_INVALID_PROPERTY,
)
from quantsmind.foundation.exceptions import (
    AttributeError,
    ConversionError,
    TypeError as FoundationTypeError,
)
from quantsmind.foundation.interfaces import (
    Comparable,
    Serializable,
    Validatable,
)
from quantsmind.foundation.types import (
    AttributeValue,
    ComparisonResult,
    ScalarValue,
    SerializedData,
    ValidationResult,
    VectorValue,
)

logger = logging.getLogger(__name__)


class Attribute(Comparable, Serializable, Validatable):
    """Concrete implementation of typed values for properties.

    This class provides type-safe value representation with support for
    scalars, vectors, and complex numbers.

    Scientific Meaning
    ------------------
    In scientific computing, attributes represent concrete values like mass,
    charge, position, momentum, or any other measurable quantity.

    Attributes:
        _value: The attribute value
        _type: The attribute type
        _precision: Optional precision for numeric values
        _unit: Optional unit for the value

    Example:
        >>> attr = Attribute(value=42.0, type="scalar", unit="kg")
        >>> print(f"Value: {attr.value}")
    """

    def __init__(
        self,
        value: AttributeValue,
        attribute_type: str = DEFAULT_ATTRIBUTE_TYPE,
        precision: Optional[int] = None,
        unit: Optional[str] = None,
    ) -> None:
        """Initialize an Attribute.

        Args:
            value: The attribute value
            attribute_type: The attribute type (scalar, vector, tensor, complex, string, bool)
            precision: Optional precision for numeric values
            unit: Optional unit for the value

        Raises:
            FoundationTypeError: If value type doesn't match attribute_type

        Example:
            >>> attr = Attribute(value=42.0, type="scalar", unit="kg")
            >>> attr = Attribute(value=[1.0, 2.0, 3.0], type="vector")
        """
        self._value: AttributeValue = value
        self._type: str = attribute_type
        self._precision: Optional[int] = precision
        self._unit: Optional[str] = unit

        self._validate_type()
        logger.debug(f"Created attribute: type={self._type}, unit={self._unit}")

    def _validate_type(self) -> None:
        """Validate that value matches the declared type.

        Raises:
            FoundationTypeError: If type mismatch
        """
        if self._type == "scalar":
            if not isinstance(self._value, (int, float, complex)):
                raise FoundationTypeError(
                    f"Scalar attribute must be numeric, got {type(self._value)}",
                    error_code=ERROR_INVALID_PROPERTY,
                )
        elif self._type == "vector":
            if not isinstance(self._value, list):
                raise FoundationTypeError(
                    f"Vector attribute must be a list, got {type(self._value)}",
                    error_code=ERROR_INVALID_PROPERTY,
                )
            if not all(isinstance(v, (int, float, complex)) for v in self._value):
                raise FoundationTypeError(
                    "Vector attribute must contain numeric values",
                    error_code=ERROR_INVALID_PROPERTY,
                )
        elif self._type == "string":
            if not isinstance(self._value, str):
                raise FoundationTypeError(
                    f"String attribute must be a string, got {type(self._value)}",
                    error_code=ERROR_INVALID_PROPERTY,
                )
        elif self._type == "bool":
            if not isinstance(self._value, bool):
                raise FoundationTypeError(
                    f"Boolean attribute must be a bool, got {type(self._value)}",
                    error_code=ERROR_INVALID_PROPERTY,
                )

    @property
    def value(self) -> AttributeValue:
        """Get the attribute value.

        Returns:
            The attribute value

        Example:
            >>> print(f"Value: {attribute.value}")
        """
        return self._value

    @property
    def attribute_type(self) -> str:
        """Get the attribute type.

        Returns:
            The attribute type

        Example:
            >>> print(f"Type: {attribute.attribute_type}")
        """
        return self._type

    @property
    def precision(self) -> Optional[int]:
        """Get the precision.

        Returns:
            Precision value or None

        Example:
            >>> print(f"Precision: {attribute.precision}")
        """
        return self._precision

    @property
    def unit(self) -> Optional[str]:
        """Get the unit.

        Returns:
            Unit string or None

        Example:
            >>> print(f"Unit: {attribute.unit}")
        """
        return self._unit

    @property
    def is_scalar(self) -> bool:
        """Check if attribute is a scalar.

        Returns:
            True if scalar, False otherwise

        Example:
            >>> if attribute.is_scalar:
            ...     print("Scalar attribute")
        """
        return self._type == "scalar"

    @property
    def is_vector(self) -> bool:
        """Check if attribute is a vector.

        Returns:
            True if vector, False otherwise

        Example:
            >>> if attribute.is_vector:
            ...     print("Vector attribute")
        """
        return self._type == "vector"

    def set_value(self, value: AttributeValue) -> None:
        """Set the attribute value.

        Args:
            value: New value

        Raises:
            FoundationTypeError: If value type doesn't match attribute_type

        Example:
            >>> attribute.set_value(43.0)
        """
        old_value = self._value
        self._value = value
        try:
            self._validate_type()
            logger.debug(f"Updated attribute value: {old_value} -> {value}")
        except FoundationTypeError:
            self._value = old_value
            raise

    def set_unit(self, unit: str) -> None:
        """Set the unit.

        Args:
            unit: New unit

        Example:
            >>> attribute.set_unit("m")
        """
        self._unit = unit
        logger.debug(f"Updated attribute unit: {unit}")

    # Comparable interface implementation
    def compare(self, other: Any) -> ComparisonResult:
        """Compare with another attribute.

        Args:
            other: Object to compare with

        Returns:
            Tuple of (are_equal, similarity_score, differences_dict)

        Raises:
            TypeError: If other is not an Attribute

        Example:
            >>> are_equal, similarity, differences = attr1.compare(attr2)
        """
        if not isinstance(other, Attribute):
            raise TypeError(f"Cannot compare Attribute with {type(other)}")

        are_equal = self._value == other._value and self._type == other._type
        similarity = 1.0 if are_equal else 0.0

        differences: Dict[str, Any] = {}
        if self._value != other._value:
            differences["value"] = (self._value, other._value)
        if self._type != other._type:
            differences["type"] = (self._type, other._type)
        if self._unit != other._unit:
            differences["unit"] = (self._unit, other._unit)

        return (are_equal, similarity, differences)

    def equals(self, other: Any) -> bool:
        """Check equality with another attribute.

        Args:
            other: Object to compare with

        Returns:
            True if equal, False otherwise

        Example:
            >>> if attr1.equals(attr2):
            ...     print("Attributes are equal")
        """
        if not isinstance(other, Attribute):
            return False
        return self._value == other._value and self._type == other._type

    def is_less_than(self, other: Any) -> bool:
        """Check if this attribute is less than another.

        Args:
            other: Object to compare with

        Returns:
            True if less than, False otherwise

        Raises:
            TypeError: If comparison not supported

        Example:
            >>> if attr1.is_less_than(attr2):
            ...     print("attr1 < attr2")
        """
        if not isinstance(other, Attribute):
            raise TypeError(f"Cannot compare Attribute with {type(other)}")
        if not isinstance(self._value, (int, float)) or not isinstance(
            other._value, (int, float)
        ):
            raise TypeError("Comparison only supported for numeric scalar attributes")
        return self._value < other._value  # type: ignore

    def is_greater_than(self, other: Any) -> bool:
        """Check if this attribute is greater than another.

        Args:
            other: Object to compare with

        Returns:
            True if greater than, False otherwise

        Raises:
            TypeError: If comparison not supported

        Example:
            >>> if attr1.is_greater_than(attr2):
            ...     print("attr1 > attr2")
        """
        if not isinstance(other, Attribute):
            raise TypeError(f"Cannot compare Attribute with {type(other)}")
        if not isinstance(self._value, (int, float)) or not isinstance(
            other._value, (int, float)
        ):
            raise TypeError("Comparison only supported for numeric scalar attributes")
        return self._value > other._value  # type: ignore

    @property
    def comparison_key(self) -> Any:
        """Get the comparison key.

        Returns:
            Comparison key (value)

        Example:
            >>> key = attribute.comparison_key
        """
        return self._value

    # Serializable interface implementation
    def serialize(self, format: str = "json") -> bytes:
        """Serialize the attribute to bytes.

        Args:
            format: Serialization format (currently only "json" supported)

        Returns:
            Serialized data as bytes

        Raises:
            NotImplementedError: If format is not supported

        Example:
            >>> data = attribute.serialize(format="json")
        """
        if format != "json":
            raise NotImplementedError(f"Serialization format '{format}' not yet implemented")

        import json

        data = {
            "value": self._value,
            "type": self._type,
            "precision": self._precision,
            "unit": self._unit,
        }
        return json.dumps(data).encode("utf-8")

    @classmethod
    def deserialize(cls, data: bytes, format: str = "json") -> "Attribute":
        """Deserialize the attribute from bytes.

        Args:
            data: Serialized data as bytes
            format: Serialization format (currently only "json" supported)

        Returns:
            Deserialized Attribute instance

        Raises:
            NotImplementedError: If format is not supported
            FoundationTypeError: If data is invalid

        Example:
            >>> attribute = Attribute.deserialize(data, format="json")
        """
        if format != "json":
            raise NotImplementedError(f"Serialization format '{format}' not yet implemented")

        import json

        try:
            obj = json.loads(data.decode("utf-8"))
            return cls(
                value=obj["value"],
                attribute_type=obj["type"],
                precision=obj.get("precision"),
                unit=obj.get("unit"),
            )
        except (json.JSONDecodeError, KeyError) as e:
            raise FoundationTypeError(
                f"Failed to deserialize attribute: {e}",
                error_code=ERROR_INVALID_PROPERTY,
            ) from e

    def is_serializable(self) -> bool:
        """Check if the attribute is serializable.

        Returns:
            True (attributes are always serializable)

        Example:
            >>> if attribute.is_serializable():
            ...     data = attribute.serialize()
        """
        return True

    @classmethod
    def get_supported_formats(cls) -> list[str]:
        """Get supported serialization formats.

        Returns:
            List of supported formats

        Example:
            >>> formats = Attribute.get_supported_formats()
        """
        return ["json"]

    # Validatable interface implementation
    def validate(self) -> ValidationResult:
        """Validate the attribute.

        Returns:
            Tuple of (is_valid, error_messages)

        Example:
            >>> is_valid, errors = attribute.validate()
        """
        errors: list[str] = []

        try:
            self._validate_type()
        except FoundationTypeError as e:
            errors.append(str(e))

        if self._precision is not None and self._precision < 0:
            errors.append("Precision must be non-negative")

        return (len(errors) == 0, errors)

    @property
    def validation_errors(self) -> list[str]:
        """Get validation errors.

        Returns:
            List of error messages

        Example:
            >>> errors = attribute.validation_errors
        """
        is_valid, errors = self.validate()
        return errors if not is_valid else []

    @property
    def validation_warnings(self) -> list[str]:
        """Get validation warnings.

        Returns:
            List of warning messages (currently empty)

        Example:
            >>> warnings = attribute.validation_warnings
        """
        return []

    # Conversion methods
    def convert_to(self, target_type: str) -> "Attribute":
        """Convert attribute to a different type.

        Args:
            target_type: Target type to convert to

        Returns:
            New Attribute with converted value

        Raises:
            ConversionError: If conversion fails

        Example:
            >>> vector_attr = Attribute(value=[1.0, 2.0], type="vector")
            >>> scalar_attr = vector_attr.convert_to("scalar")  # May fail
        """
        if target_type == self._type:
            return self

        try:
            if target_type == "scalar" and self._type == "vector":
                # Convert vector to scalar (take first element or sum)
                if isinstance(self._value, list) and len(self._value) > 0:
                    new_value = self._value[0]
                else:
                    raise ConversionError("Cannot convert empty vector to scalar")
            elif target_type == "vector" and self._type == "scalar":
                # Convert scalar to vector (single element)
                new_value = [self._value]  # type: ignore
            else:
                raise ConversionError(
                    f"Conversion from {self._type} to {target_type} not supported"
                )

            return Attribute(
                value=new_value,
                attribute_type=target_type,
                precision=self._precision,
                unit=self._unit,
            )
        except Exception as e:
            raise ConversionError(f"Failed to convert attribute: {e}") from e

    # Object protocol methods
    def __repr__(self) -> str:
        """Return string representation of the attribute.

        Returns:
            String representation

        Example:
            >>> repr(attribute)
        """
        return f"Attribute(value={self._value}, type='{self._type}', unit='{self._unit}')"

    def __str__(self) -> str:
        """Return string representation of the attribute.

        Returns:
            String representation

        Example:
            >>> str(attribute)
        """
        if self._unit:
            return f"{self._value} {self._unit}"
        return str(self._value)

    def __eq__(self, other: Any) -> bool:
        """Check equality.

        Args:
            other: Object to compare with

        Returns:
            True if equal, False otherwise

        Example:
            >>> attr1 == attr2
        """
        if not isinstance(other, Attribute):
            return False
        return self._value == other._value and self._type == other._type

    def __hash__(self) -> int:
        """Return hash of the attribute.

        Returns:
            Hash value

        Example:
            >>> hash(attribute)
        """
        return hash((self._value, self._type, self._unit))


# Export
__all__ = ["Attribute"]
