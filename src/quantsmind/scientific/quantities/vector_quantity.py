"""
Vector Quantity Module

This module provides vector quantity definitions for the Scientific package.

Purpose
-------
Provide vector quantity definitions and operations.

Responsibilities
----------------
- Define vector quantity structure
- Support vector arithmetic
- Support vector operations
- Support vector validation

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
from quantsmind.scientific.types import QuantityVector


class VectorQuantity(Quantity):
    """Concrete implementation of a vector quantity.

    This class provides vector quantity functionality.

    Attributes:
        _value: Vector values
        _unit: Vector unit
        _dimension: Vector dimension
        _metadata: Vector metadata

    Example:
        >>> position = VectorQuantity([1.0, 2.0, 3.0], meter_unit, length_dimension)
        >>> position.value()
    """

    def __init__(
        self,
        value: QuantityVector,
        unit: IUnit,
        dimension: IDimension,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a VectorQuantity.

        Args:
            value: Vector values
            unit: Vector unit
            dimension: Vector dimension
            metadata: Vector metadata

        Example:
            >>> position = VectorQuantity([1.0, 2.0, 3.0], meter_unit, length_dimension)
        """
        super().__init(value, unit, dimension, metadata)

    @property
    def value(self) -> QuantityVector:
        """Get the vector values.

        Returns:
            Vector values

        Example:
            >>> print(f"Value: {vector.value}")
        """
        return self._value

    @property
    def magnitude(self) -> float:
        """Get the vector magnitude.

        Returns:
            Vector magnitude

        Example:
            >>> print(f"Magnitude: {vector.magnitude}")
        """
        return sum(v ** 2 for v in self._value) ** 0.5

    @property
    def dimension(self) -> int:
        """Get the vector dimension.

        Returns:
            Vector dimension (number of components)

        Example:
            >>> print(f"Dimension: {vector.dimension}")
        """
        return len(self._value)

    def normalize(self) -> VectorQuantity:
        """Normalize the vector.

        Returns:
            Normalized vector

        Raises:
            ValueError: If vector magnitude is zero

        Example:
            >>> normalized = vector.normalize()
        """
        mag = self.magnitude
        if mag == 0:
            raise ValueError("Cannot normalize zero vector")
        
        normalized_value = [v / mag for v in self._value]
        return VectorQuantity(normalized_value, self._unit, self._dimension, self._metadata)

    def dot(self, other: VectorQuantity) -> float:
        """Calculate dot product.

        Args:
            other: Other vector

        Returns:
            Dot product

        Raises:
            ValueError: If vectors have different dimensions

        Example:
            >>> result = vector1.dot(vector2)
        """
        if self.dimension != other.dimension:
            raise ValueError("Vectors must have the same dimension")
        
        return sum(a * b for a, b in zip(self._value, other.value(), strict=False))

    def add(self, other: VectorQuantity) -> VectorQuantity:
        """Add vectors.

        Args:
            other: Other vector

        Returns:
            Resulting vector

        Raises:
            ValueError: If vectors have different dimensions

        Example:
            >>> result = vector1.add(vector2)
        """
        if self.dimension != other.dimension:
            raise ValueError("Vectors must have the same dimension")
        
        result_value = [a + b for a, b in zip(self._value, other.value(), strict=False)]
        return VectorQuantity(result_value, self._unit, self._dimension, self._metadata)

    def subtract(self, other: VectorQuantity) -> VectorQuantity:
        """Subtract vectors.

        Args:
            other: Other vector

        Returns:
            Resulting vector

        Raises:
            ValueError: If vectors have different dimensions

        Example:
            >>> result = vector1.subtract(vector2)
        """
        if self.dimension != other.dimension:
            raise ValueError("Vectors must have the same dimension")
        
        result_value = [a - b for a, b in zip(self._value, other.value(), strict=False)]
        return VectorQuantity(result_value, self._unit, self._dimension, self._metadata)

    def scale(self, scalar: float) -> VectorQuantity:
        """Scale the vector.

        Args:
            scalar: Scale factor

        Returns:
            Scaled vector

        Example:
            >>> scaled = vector.scale(2.0)
        """
        result_value = [v * scalar for v in self._value]
        return VectorQuantity(result_value, self._unit, self._dimension, self._metadata)

    def __add__(self, other: VectorQuantity) -> VectorQuantity:
        """Add vectors.

        Args:
            other: Other vector

        Returns:
            Resulting vector

        Example:
            >>> result = vector1 + vector2
        """
        return self.add(other)

    def __sub__(self, other: VectorQuantity) -> VectorQuantity:
        """Subtract vectors.

        Args:
            other: Other vector

        Returns:
            Resulting vector

        Example:
            >>> result = vector1 - vector2
        """
        return self.subtract(other)

    def __mul__(self, scalar: float) -> VectorQuantity:
        """Multiply by scalar.

        Args:
            scalar: Scalar multiplier

        Returns:
            Scaled vector

        Example:
            >>> result = vector * 2.0
        """
        return self.scale(scalar)

    def __rmul__(self, scalar: float) -> VectorQuantity:
        """Multiply by scalar (right side).

        Args:
            scalar: Scalar multiplier

        Returns:
            Scaled vector

        Example:
            >>> result = 2.0 * vector
        """
        return self.scale(scalar)

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(vector)
        """
        return f"VectorQuantity(value={self._value}, unit={self._unit.name()}, dimension={self._dimension.name()})"


# Export
__all__ = [
    "VectorQuantity",
]
