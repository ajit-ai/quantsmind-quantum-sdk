"""
Scalar Quantity Module

This module provides scalar quantity definitions for the Scientific package.

Purpose
-------
Provide scalar quantity definitions and operations.

Responsibilities
----------------
- Define scalar quantity structure
- Support scalar arithmetic
- Support scalar conversion
- Support scalar validation

Dependencies
------------
typing (standard library)
quantsmind.scientific.quantities.quantity (quantity)
quantsmind.scientific.interfaces (scientific interfaces)
quantsmind.scientific.types (scientific types)
"""

from __future__ import annotations

from typing import Any

from quantsmind.scientific.interfaces import IDimension, IUnit
from quantsmind.scientific.quantities.quantity import Quantity
from quantsmind.scientific.types import QuantityValue


class ScalarQuantity(Quantity):
    """Concrete implementation of a scalar quantity.

    This class provides scalar quantity functionality.

    Attributes:
        _value: Scalar value
        _unit: Scalar unit
        _dimension: Scalar dimension
        _metadata: Scalar metadata

    Example:
        >>> length = ScalarQuantity(1.0, meter_unit, length_dimension)
        >>> length.value()
    """

    def __init__(
        self,
        value: QuantityValue,
        unit: IUnit,
        dimension: IDimension,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a ScalarQuantity.

        Args:
            value: Scalar value
            unit: Scalar unit
            dimension: Scalar dimension
            metadata: Scalar metadata

        Example:
            >>> length = ScalarQuantity(1.0, meter_unit, length_dimension)
        """
        super().__init__(value, unit, dimension, metadata)

    def abs(self) -> ScalarQuantity:
        """Get absolute value.

        Returns:
            Absolute value

        Example:
            >>> absolute = scalar.abs()
        """
        return ScalarQuantity(abs(self._value), self._unit, self._dimension, self._metadata)

    def negate(self) -> ScalarQuantity:
        """Negate the scalar.

        Returns:
            Negated scalar

        Example:
            >>> negated = scalar.negate()
        """
        return ScalarQuantity(-self._value, self._unit, self._dimension, self._metadata)

    def power(self, exponent: float) -> ScalarQuantity:
        """Raise scalar to a power.

        Args:
            exponent: Power to raise to

        Returns:
            Resulting scalar

        Example:
            >>> result = scalar.power(2)
        """
        result_value = self._value ** exponent
        result_dimension = self._dimension.power(int(exponent))
        return ScalarQuantity(result_value, self._unit, result_dimension, self._metadata)

    def sqrt(self) -> ScalarQuantity:
        """Calculate square root.

        Returns:
            Square root

        Example:
            >>> root = scalar.sqrt()
        """
        return self.power(0.5)

    def __add__(self, other: ScalarQuantity) -> ScalarQuantity:
        """Add scalars.

        Args:
            other: Other scalar

        Returns:
            Resulting scalar

        Example:
            >>> result = scalar1 + scalar2
        """
        return self.add(other)

    def __sub__(self, other: ScalarQuantity) -> ScalarQuantity:
        """Subtract scalars.

        Args:
            other: Other scalar

        Returns:
            Resulting scalar

        Example:
            >>> result = scalar1 - scalar2
        """
        return self.subtract(other)

    def __mul__(self, other: ScalarQuantity) -> ScalarQuantity:
        """Multiply scalars.

        Args:
            other: Other scalar

        Returns:
            Resulting scalar

        Example:
            >>> result = scalar1 * scalar2
        """
        return self.multiply(other)

    def __truediv__(self, other: ScalarQuantity) -> ScalarQuantity:
        """Divide scalars.

        Args:
            other: Other scalar

        Returns:
            Resulting scalar

        Example:
            >>> result = scalar1 / scalar2
        """
        return self.divide(other)

    def __neg__(self) -> ScalarQuantity:
        """Negate scalar.

        Returns:
            Negated scalar

        Example:
            >>> result = -scalar
        """
        return self.negate()

    def __abs__(self) -> ScalarQuantity:
        """Absolute value.

        Returns:
            Absolute value

        Example:
            >>> result = abs(scalar)
        """
        return self.abs()

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(scalar)
        """
        return f"ScalarQuantity(value={self._value}, unit={self._unit.name()}, dimension={self._dimension.name()})"


# Export
__all__ = [
    "ScalarQuantity",
]
