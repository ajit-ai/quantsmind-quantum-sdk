"""
Dimension Module

This module provides dimension definitions for the Scientific package.

Purpose
-------
Provide dimension definitions and operations.

Responsibilities
----------------
- Define dimension structure
- Support dimension vectors
- Support dimension compatibility checks
- Support dimension operations

Dependencies
------------
typing (standard library)
quantsmind.scientific.exceptions (scientific exceptions)
quantsmind.scientific.interfaces (scientific interfaces)
quantsmind.scientific.types (scientific types)
"""

from __future__ import annotations

from typing import Any

from quantsmind.scientific.interfaces import IDimension
from quantsmind.scientific.types import DimensionPower, DimensionVector


class Dimension(IDimension):
    """Concrete implementation of a dimension.

    This class provides dimension functionality.

    Attributes:
        _name: Dimension name
        _vector: Dimension vector (L, M, T, Θ, I, N, J)
        _metadata: Dimension metadata

    Example:
        >>> length = Dimension("length", (1, 0, 0, 0, 0, 0, 0))
        >>> length.name()
    """

    def __init__(
        self,
        name: str,
        vector: DimensionVector,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a Dimension.

        Args:
            name: Dimension name
            vector: Dimension vector (L, M, T, Θ, I, N, J)
            metadata: Dimension metadata

        Example:
            >>> length = Dimension("length", (1, 0, 0, 0, 0, 0, 0))
        """
        self._name = name
        self._vector = vector
        self._metadata = metadata or {}

    @property
    def name(self) -> str:
        """Get the dimension name.

        Returns:
            Dimension name

        Example:
            >>> print(f"Name: {dimension.name}")
        """
        return self._name

    @property
    def vector(self) -> DimensionVector:
        """Get the dimension vector.

        Returns:
            Dimension vector (L, M, T, Θ, I, N, J)

        Example:
            >>> print(f"Vector: {dimension.vector}")
        """
        return self._vector

    @property
    def metadata(self) -> dict[str, Any]:
        """Get the dimension metadata.

        Returns:
            Dimension metadata

        Example:
            >>> print(f"Metadata: {dimension.metadata}")
        """
        return self._metadata.copy()

    def is_compatible(self, other: IDimension) -> bool:
        """Check if dimensions are compatible.

        Args:
            other: Other dimension

        Returns:
            True if compatible, False otherwise

        Example:
            >>> if dimension.is_compatible(other_dimension):
            ...     print("Compatible")
        """
        return self._vector == other.vector()

    def is_dimensionless(self) -> bool:
        """Check if dimensionless.

        Returns:
            True if dimensionless, False otherwise

        Example:
            >>> if dimension.is_dimensionless():
            ...     print("Dimensionless")
        """
        return all(power == 0 for power in self._vector)

    def multiply(self, other: IDimension) -> Dimension:
        """Multiply dimensions.

        Args:
            other: Other dimension

        Returns:
            Resulting dimension

        Example:
            >>> result = dimension.multiply(other_dimension)
        """
        new_vector = tuple(
            self._vector[i] + other.vector()[i]
            for i in range(7)
        )
        return Dimension(f"{self._name}*{other.name()}", new_vector)

    def divide(self, other: IDimension) -> Dimension:
        """Divide dimensions.

        Args:
            other: Other dimension

        Returns:
            Resulting dimension

        Example:
            >>> result = dimension.divide(other_dimension)
        """
        new_vector = tuple(
            self._vector[i] - other.vector()[i]
            for i in range(7)
        )
        return Dimension(f"{self._name}/{other.name()}", new_vector)

    def power(self, exponent: DimensionPower) -> Dimension:
        """Raise dimension to a power.

        Args:
            exponent: Power to raise to

        Returns:
            Resulting dimension

        Example:
            >>> result = dimension.power(2)
        """
        new_vector = tuple(power * exponent for power in self._vector)
        return Dimension(f"{self._name}^{exponent}", new_vector)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dimension definition

        Example:
            >>> data = dimension.to_dict()
        """
        return {
            "name": self._name,
            "vector": self._vector,
            "metadata": self._metadata.copy(),
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(dimension)
        """
        return f"Dimension(name={self._name}, vector={self._vector})"


# Export
__all__ = [
    "Dimension",
]
