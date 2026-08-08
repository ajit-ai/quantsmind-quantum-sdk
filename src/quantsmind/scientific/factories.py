"""
Factories Module

This module provides factory methods for the Scientific package.

Purpose
-------
Provide factory methods for creating scientific objects.

Responsibilities
----------------
- Create units
- Create dimensions
- Create quantities
- Create measurements
- Create coordinates

Dependencies
------------
typing (standard library)
quantsmind.scientific.units (units)
quantsmind.scientific.dimensions (dimensions)
quantsmind.scientific.quantities (quantities)
quantsmind.scientific.measurements (measurements)
quantsmind.scientific.coordinates (coordinates)
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from quantsmind.scientific.coordinates import CartesianCoordinate
from quantsmind.scientific.dimensions import Dimension, DimensionalAnalysis
from quantsmind.scientific.measurements import Measurement
from quantsmind.scientific.quantities import Quantity, ScalarQuantity, VectorQuantity
from quantsmind.scientific.units import BaseUnit, SIUnits


class ScientificFactory:
    """Concrete implementation of a scientific factory.

    This class provides factory functionality for creating scientific objects.

    Example:
        >>> factory = ScientificFactory()
        >>> meter = factory.create_unit("meter", "m", 1.0, "length")
    """

    def __init__(self) -> None:
        """Initialize a ScientificFactory.

        Example:
            >>> factory = ScientificFactory()
        """
        self._si_units = SIUnits()
        self._dimensional_analysis = DimensionalAnalysis()

    def create_unit(
        self,
        name: str,
        symbol: str,
        conversion_factor: float,
        dimension: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> BaseUnit:
        """Create a unit.

        Args:
            name: Unit name
            symbol: Unit symbol
            conversion_factor: Conversion factor
            dimension: Unit dimension
            metadata: Unit metadata

        Returns:
            Created unit

        Example:
            >>> meter = factory.create_unit("meter", "m", 1.0, "length")
        """
        return BaseUnit(name, symbol, conversion_factor, dimension, metadata)

    def get_si_unit(self, name: str) -> Optional[BaseUnit]:
        """Get an SI unit.

        Args:
            name: Unit name

        Returns:
            BaseUnit or None

        Example:
            >>> meter = factory.get_si_unit("meter")
        """
        return self._si_units.get_unit(name)

    def create_dimension(
        self,
        name: str,
        vector: tuple[int, int, int, int, int, int, int],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dimension:
        """Create a dimension.

        Args:
            name: Dimension name
            vector: Dimension vector (L, M, T, Θ, I, N, J)
            metadata: Dimension metadata

        Returns:
            Created dimension

        Example:
            >>> length = factory.create_dimension("length", (1, 0, 0, 0, 0, 0, 0))
        """
        return Dimension(name, vector, metadata)

    def get_dimension(self, name: str) -> Optional[Dimension]:
        """Get a dimension.

        Args:
            name: Dimension name

        Returns:
            Dimension or None

        Example:
            >>> length = factory.get_dimension("length")
        """
        return self._dimensional_analysis.get_dimension(name)

    def create_quantity(
        self,
        value: float,
        unit: BaseUnit,
        dimension: Dimension,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Quantity:
        """Create a quantity.

        Args:
            value: Quantity value
            unit: Quantity unit
            dimension: Quantity dimension
            metadata: Quantity metadata

        Returns:
            Created quantity

        Example:
            >>> length = factory.create_quantity(1.0, meter_unit, length_dim)
        """
        return Quantity(value, unit, dimension, metadata)

    def create_scalar_quantity(
        self,
        value: float,
        unit: BaseUnit,
        dimension: Dimension,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ScalarQuantity:
        """Create a scalar quantity.

        Args:
            value: Quantity value
            unit: Quantity unit
            dimension: Quantity dimension
            metadata: Quantity metadata

        Returns:
            Created scalar quantity

        Example:
            >>> length = factory.create_scalar_quantity(1.0, meter_unit, length_dim)
        """
        return ScalarQuantity(value, unit, dimension, metadata)

    def create_vector_quantity(
        self,
        value: list[float],
        unit: BaseUnit,
        dimension: Dimension,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> VectorQuantity:
        """Create a vector quantity.

        Args:
            value: Vector values
            unit: Quantity unit
            dimension: Quantity dimension
            metadata: Quantity metadata

        Returns:
            Created vector quantity

        Example:
            >>> position = factory.create_vector_quantity([1.0, 2.0, 3.0], meter_unit, length_dim)
        """
        return VectorQuantity(value, unit, dimension, metadata)

    def create_measurement(
        self,
        value: float,
        uncertainty: float,
        unit: BaseUnit,
        confidence: float = 0.95,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Measurement:
        """Create a measurement.

        Args:
            value: Measurement value
            uncertainty: Measurement uncertainty
            unit: Measurement unit
            confidence: Confidence level
            metadata: Measurement metadata

        Returns:
            Created measurement

        Example:
            >>> length = factory.create_measurement(1.0, 0.01, meter_unit)
        """
        return Measurement(value, uncertainty, unit, confidence, metadata)

    def create_cartesian_coordinate(
        self,
        x: float,
        y: float,
        z: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> CartesianCoordinate:
        """Create a Cartesian coordinate.

        Args:
            x: X coordinate
            y: Y coordinate
            z: Z coordinate
            metadata: Coordinate metadata

        Returns:
            Created coordinate

        Example:
            >>> coord = factory.create_cartesian_coordinate(1.0, 2.0, 3.0)
        """
        return CartesianCoordinate(x, y, z, metadata)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Factory state

        Example:
            >>> data = factory.to_dict()
        """
        return {
            "si_units_count": len(self._si_units.get_all_units()),
            "dimensions_count": len(self._dimensional_analysis.get_all_dimensions()),
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(factory)
        """
        return f"ScientificFactory(si_units={len(self._si_units.get_all_units())}, dimensions={len(self._dimensional_analysis.get_all_dimensions())})"


# Export
__all__ = [
    "ScientificFactory",
]
