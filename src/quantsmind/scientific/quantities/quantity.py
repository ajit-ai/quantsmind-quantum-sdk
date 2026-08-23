"""
Quantity Module

This module provides quantity definitions for the Scientific package.

Purpose
-------
Provide quantity definitions and operations.

Responsibilities
----------------
- Define quantity structure
- Support quantity arithmetic
- Support quantity conversion
- Support quantity validation

Dependencies
------------
typing (standard library)
quantsmind.scientific.exceptions (scientific exceptions)
quantsmind.scientific.interfaces (scientific interfaces)
quantsmind.scientific.types (scientific types)
quantsmind.scientific.units.base_unit (base unit)
quantsmind.scientific.dimensions.dimension (dimension)
"""

from __future__ import annotations

from typing import Any

from quantsmind.scientific.exceptions import ConversionError, QuantityError
from quantsmind.scientific.interfaces import IDimension, IQuantity, IUnit
from quantsmind.scientific.types import QuantityValue
from quantsmind.scientific.units.base_unit import BaseUnit


class Quantity(IQuantity):
    """Concrete implementation of a quantity.

    This class provides quantity functionality.

    Attributes:
        _value: Quantity value
        _unit: Quantity unit
        _dimension: Quantity dimension
        _metadata: Quantity metadata

    Example:
        >>> length = Quantity(1.0, meter_unit, length_dimension)
        >>> length.value()
    """

    def __init__(
        self,
        value: QuantityValue,
        unit: IUnit,
        dimension: IDimension,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a Quantity.

        Args:
            value: Quantity value
            unit: Quantity unit
            dimension: Quantity dimension
            metadata: Quantity metadata

        Example:
            >>> length = Quantity(1.0, meter_unit, length_dimension)
        """
        self._value = value
        self._unit = unit
        self._dimension = dimension
        self._metadata = metadata or {}

    @property
    def value(self) -> QuantityValue:
        """Get the quantity value.

        Returns:
            Quantity value

        Example:
            >>> print(f"Value: {quantity.value}")
        """
        return self._value

    @property
    def unit(self) -> IUnit:
        """Get the quantity unit.

        Returns:
            Quantity unit

        Example:
            >>> print(f"Unit: {quantity.unit}")
        """
        return self._unit

    @property
    def dimension(self) -> IDimension:
        """Get the quantity dimension.

        Returns:
            Quantity dimension

        Example:
            >>> print(f"Dimension: {quantity.dimension}")
        """
        return self._dimension

    @property
    def metadata(self) -> dict[str, Any]:
        """Get the quantity metadata.

        Returns:
            Quantity metadata

        Example:
            >>> print(f"Metadata: {quantity.metadata}")
        """
        return self._metadata.copy()

    def convert_to(self, target_unit: IUnit) -> Quantity:
        """Convert to a different unit.

        Args:
            target_unit: Target unit

        Returns:
            Converted quantity

        Raises:
            ConversionError: If units are not compatible

        Example:
            >>> converted = quantity.convert_to(kilometer_unit)
        """
        if not self._unit.is_compatible(target_unit):
            raise ConversionError(
                f"Cannot convert {self._unit.name()} to {target_unit.name()}",
                from_unit=self._unit.name(),
                to_unit=target_unit.name(),
            )

        if isinstance(self._unit, BaseUnit):
            converted_value = self._unit.convert_value(self._value, target_unit)
        else:
            # Generic conversion using conversion factors
            base_value = self._value * self._unit.conversion_factor()
            converted_value = base_value / target_unit.conversion_factor()

        return Quantity(converted_value, target_unit, self._dimension, self._metadata)

    def add(self, other: IQuantity) -> Quantity:
        """Add quantities.

        Args:
            other: Other quantity

        Returns:
            Resulting quantity

        Raises:
            QuantityError: If quantities are not compatible

        Example:
            >>> result = quantity.add(other_quantity)
        """
        if not self._dimension.is_compatible(other.dimension()):
            raise QuantityError(
                "Cannot add quantities with different dimensions",
                quantity=f"{self._dimension.name()} + {other.dimension().name()}",
            )

        if not self._unit.is_compatible(other.unit()):
            # Convert to same unit
            other_converted = other.convert_to(self._unit)
            result_value = self._value + other_converted.value()
        else:
            result_value = self._value + other.value()

        return Quantity(result_value, self._unit, self._dimension, self._metadata)

    def subtract(self, other: IQuantity) -> Quantity:
        """Subtract quantities.

        Args:
            other: Other quantity

        Returns:
            Resulting quantity

        Raises:
            QuantityError: If quantities are not compatible

        Example:
            >>> result = quantity.subtract(other_quantity)
        """
        if not self._dimension.is_compatible(other.dimension()):
            raise QuantityError(
                "Cannot subtract quantities with different dimensions",
                quantity=f"{self._dimension.name()} - {other.dimension().name()}",
            )

        if not self._unit.is_compatible(other.unit()):
            # Convert to same unit
            other_converted = other.convert_to(self._unit)
            result_value = self._value - other_converted.value()
        else:
            result_value = self._value - other.value()

        return Quantity(result_value, self._unit, self._dimension, self._metadata)

    def multiply(self, other: IQuantity) -> Quantity:
        """Multiply quantities.

        Args:
            other: Other quantity

        Returns:
            Resulting quantity

        Example:
            >>> result = quantity.multiply(other_quantity)
        """
        result_value = self._value * other.value()
        result_dimension = self._dimension.multiply(other.dimension())
        
        # For simplicity, use the first unit (real implementation would handle unit multiplication)
        return Quantity(result_value, self._unit, result_dimension, self._metadata)

    def divide(self, other: IQuantity) -> Quantity:
        """Divide quantities.

        Args:
            other: Other quantity

        Returns:
            Resulting quantity

        Raises:
            QuantityError: If dividing by zero

        Example:
            >>> result = quantity.divide(other_quantity)
        """
        if other.value() == 0:
            raise QuantityError("Cannot divide by zero", quantity="division")

        result_value = self._value / other.value()
        result_dimension = self._dimension.divide(other.dimension())
        
        # For simplicity, use the first unit (real implementation would handle unit division)
        return Quantity(result_value, self._unit, result_dimension, self._metadata)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Quantity definition

        Example:
            >>> data = quantity.to_dict()
        """
        return {
            "value": self._value,
            "unit": self._unit.name(),
            "dimension": self._dimension.name(),
            "metadata": self._metadata.copy(),
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(quantity)
        """
        return f"Quantity(value={self._value}, unit={self._unit.name()}, dimension={self._dimension.name()})"


# Export
__all__ = [
    "Quantity",
]
