"""
Scientific Protocols Module

This module provides protocols for the Scientific package.

Purpose
-------
Define structural subtyping protocols for scientific operations.

Responsibilities
----------------
- Define unit conversion protocol
- Define dimensional analysis protocol
- Define coordinate transformation protocol
- Define time conversion protocol

Dependencies
------------
typing (standard library)
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from quantsmind.scientific.types import (
    ConversionFactor,
    CoordinateTriple,
    DimensionVector,
    MeasurementValue,
    QuantityValue,
)


@runtime_checkable
class UnitConvertible(Protocol):
    """Protocol for unit convertible objects.

    This protocol defines the contract for objects that can be converted between units.

    Example:
        >>> class MyUnit(UnitConvertible):
        ...     def to_base(self):
        ...         return 1.0
    """

    def to_base(self) -> ConversionFactor:
        """Convert to base unit.

        Returns:
            Conversion factor to base unit

        Example:
            >>> obj.to_base()
        """
        ...

    def from_base(self, factor: ConversionFactor) -> QuantityValue:
        """Convert from base unit.

        Args:
            factor: Conversion factor from base unit

        Returns:
            Converted value

        Example:
            >>> obj.from_base(1.0)
        """
        ...


@runtime_checkable
class Dimensional(Protocol):
    """Protocol for dimensional objects.

    This protocol defines the contract for objects with dimensional properties.

    Example:
        >>> class MyQuantity(Dimensional):
        ...     def get_dimension(self):
        ...         return (1, 0, 0, 0, 0, 0, 0)
    """

    def get_dimension(self) -> DimensionVector:
        """Get the dimension vector.

        Returns:
            Dimension vector (L, M, T, Θ, I, N, J)

        Example:
            >>> obj.get_dimension()
        """
        ...

    def is_dimensionless(self) -> bool:
        """Check if dimensionless.

        Returns:
            True if dimensionless, False otherwise

        Example:
            >>> obj.is_dimensionless()
        """
        ...


@runtime_checkable
class Measurable(Protocol):
    """Protocol for measurable objects.

    This protocol defines the contract for objects that can be measured.

    Example:
        >>> class MyMeasurement(Measurable):
        ...     def get_value(self):
        ...         return 1.0
    """

    def get_value(self) -> MeasurementValue:
        """Get the measured value.

        Returns:
            Measured value

        Example:
            >>> obj.get_value()
        """
        ...

    def get_uncertainty(self) -> MeasurementValue:
        """Get the measurement uncertainty.

        Returns:
            Measurement uncertainty

        Example:
            >>> obj.get_uncertainty()
        """
        ...


@runtime_checkable
class Transformable(Protocol):
    """Protocol for transformable coordinates.

    This protocol defines the contract for coordinate transformations.

    Example:
        >>> class MyCoordinate(Transformable):
        ...     def to_cartesian(self):
        ...         return (0.0, 0.0, 0.0)
    """

    def to_cartesian(self) -> CoordinateTriple:
        """Transform to Cartesian coordinates.

        Returns:
            Cartesian coordinates (x, y, z)

        Example:
            >>> obj.to_cartesian()
        """
        ...

    def from_cartesian(self, coords: CoordinateTriple) -> Transformable:
        """Transform from Cartesian coordinates.

        Args:
            coords: Cartesian coordinates

        Returns:
            Transformed coordinate

        Example:
            >>> obj.from_cartesian((0.0, 0.0, 0.0))
        """
        ...


@runtime_checkable
class Serializable(Protocol):
    """Protocol for serializable objects.

    This protocol defines the contract for objects that can be serialized.

    Example:
        >>> class MyObject(Serializable):
        ...     def to_dict(self):
        ...         return {"value": 1.0}
    """

    def to_dict(self) -> dict:
        """Convert to dictionary.

        Returns:
            Dictionary representation

        Example:
            >>> obj.to_dict()
        """
        ...

    @classmethod
    def from_dict(cls, data: dict) -> Serializable:
        """Create from dictionary.

        Args:
            data: Dictionary data

        Returns:
            Deserialized object

        Example:
            >>> MyObject.from_dict({"value": 1.0})
        """
        ...


@runtime_checkable
class Validatable(Protocol):
    """Protocol for validatable objects.

    This protocol defines the contract for objects that can be validated.

    Example:
        >>> class MyObject(Validatable):
        ...     def validate(self):
        ...         return True, []
    """

    def validate(self) -> tuple[bool, list[str]]:
        """Validate the object.

        Returns:
            Tuple of (is_valid, errors)

        Example:
            >>> obj.validate()
        """
        ...


@runtime_checkable
class Observable(Protocol):
    """Protocol for observable objects.

    This protocol defines the contract for objects that can be observed.

    Example:
        >>> class MyObservable(Observable):
        ...     def observe(self):
        ...         return {"value": 1.0}
    """

    def observe(self) -> dict:
        """Perform observation.

        Returns:
            Observation data

        Example:
            >>> obj.observe()
        """
        ...


# Export
__all__ = [
    "UnitConvertible",
    "Dimensional",
    "Measurable",
    "Transformable",
    "Serializable",
    "Validatable",
    "Observable",
]
