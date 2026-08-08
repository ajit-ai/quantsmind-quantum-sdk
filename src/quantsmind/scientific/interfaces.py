"""
Scientific Interfaces Module

This module provides interfaces for the Scientific package.

Purpose
-------
Define abstract interfaces for scientific operations.

Responsibilities
----------------
- Define unit interface
- Define dimension interface
- Define quantity interface
- Define measurement interface
- Define coordinate interface
- Define reference frame interface
- Define time interface

Dependencies
------------
abc (standard library)
typing (standard library)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple

from quantsmind.scientific.types import (
    ConversionFactor,
    CoordinateTriple,
    DimensionVector,
    MeasurementValue,
    QuantityValue,
    UncertaintyValue,
)


class IUnit(ABC):
    """Interface for unit definitions.

    This interface defines the contract for unit implementations.

    Example:
        >>> class Meter(IUnit):
        ...     def name(self):
        ...         return "meter"
    """

    @abstractmethod
    def name(self) -> str:
        """Get the unit name.

        Returns:
            Unit name

        Example:
            >>> unit.name()
        """
        pass

    @abstractmethod
    def symbol(self) -> str:
        """Get the unit symbol.

        Returns:
            Unit symbol

        Example:
            >>> unit.symbol()
        """
        pass

    @abstractmethod
    def conversion_factor(self) -> ConversionFactor:
        """Get the conversion factor to base unit.

        Returns:
            Conversion factor

        Example:
            >>> unit.conversion_factor()
        """
        pass

    @abstractmethod
    def is_compatible(self, other: "IUnit") -> bool:
        """Check if units are compatible.

        Args:
            other: Other unit

        Returns:
            True if compatible, False otherwise

        Example:
            >>> unit.is_compatible(other_unit)
        """
        pass


class IDimension(ABC):
    """Interface for dimension definitions.

    This interface defines the contract for dimension implementations.

    Example:
        >>> class LengthDimension(IDimension):
        ...     def vector(self):
        ...         return (1, 0, 0, 0, 0, 0, 0)
    """

    @abstractmethod
    def name(self) -> str:
        """Get the dimension name.

        Returns:
            Dimension name

        Example:
            >>> dimension.name()
        """
        pass

    @abstractmethod
    def vector(self) -> DimensionVector:
        """Get the dimension vector.

        Returns:
            Dimension vector (L, M, T, Θ, I, N, J)

        Example:
            >>> dimension.vector()
        """
        pass

    @abstractmethod
    def is_compatible(self, other: "IDimension") -> bool:
        """Check if dimensions are compatible.

        Args:
            other: Other dimension

        Returns:
            True if compatible, False otherwise

        Example:
            >>> dimension.is_compatible(other_dimension)
        """
        pass


class IQuantity(ABC):
    """Interface for quantity definitions.

    This interface defines the contract for quantity implementations.

    Example:
        >>> class Length(IQuantity):
        ...     def value(self):
        ...         return 1.0
    """

    @abstractmethod
    def value(self) -> QuantityValue:
        """Get the quantity value.

        Returns:
            Quantity value

        Example:
            >>> quantity.value()
        """
        pass

    @abstractmethod
    def unit(self) -> IUnit:
        """Get the quantity unit.

        Returns:
            Quantity unit

        Example:
            >>> quantity.unit()
        """
        pass

    @abstractmethod
    def dimension(self) -> IDimension:
        """Get the quantity dimension.

        Returns:
            Quantity dimension

        Example:
            >>> quantity.dimension()
        """
        pass

    @abstractmethod
    def convert_to(self, unit: IUnit) -> "IQuantity":
        """Convert to a different unit.

        Args:
            unit: Target unit

        Returns:
            Converted quantity

        Example:
            >>> quantity.convert_to(new_unit)
        """
        pass


class IMeasurement(ABC):
    """Interface for measurement definitions.

    This interface defines the contract for measurement implementations.

    Example:
        >>> class LengthMeasurement(IMeasurement):
        ...     def value(self):
        ...         return 1.0
    """

    @abstractmethod
    def value(self) -> MeasurementValue:
        """Get the measurement value.

        Returns:
            Measurement value

        Example:
            >>> measurement.value()
        """
        pass

    @abstractmethod
    def uncertainty(self) -> UncertaintyValue:
        """Get the measurement uncertainty.

        Returns:
            Measurement uncertainty

        Example:
            >>> measurement.uncertainty()
        """
        pass

    @abstractmethod
    def unit(self) -> IUnit:
        """Get the measurement unit.

        Returns:
            Measurement unit

        Example:
            >>> measurement.unit()
        """
        pass

    @abstractmethod
    def confidence(self) -> float:
        """Get the confidence level.

        Returns:
            Confidence level (0.0 to 1.0)

        Example:
            >>> measurement.confidence()
        """
        pass


class ICoordinate(ABC):
    """Interface for coordinate definitions.

    This interface defines the contract for coordinate implementations.

    Example:
        >>> class CartesianCoordinate(ICoordinate):
        ...     def coordinates(self):
        ...         return (0.0, 0.0, 0.0)
    """

    @abstractmethod
    def coordinates(self) -> CoordinateTriple:
        """Get the coordinate values.

        Returns:
            Coordinate values (x, y, z)

        Example:
            >>> coordinate.coordinates()
        """
        pass

    @abstractmethod
    def system(self) -> str:
        """Get the coordinate system.

        Returns:
            Coordinate system name

        Example:
            >>> coordinate.system()
        """
        pass

    @abstractmethod
    def transform_to(self, target_system: str) -> "ICoordinate":
        """Transform to a different coordinate system.

        Args:
            target_system: Target coordinate system

        Returns:
            Transformed coordinate

        Example:
            >>> coordinate.transform_to("spherical")
        """
        pass


class IReferenceFrame(ABC):
    """Interface for reference frame definitions.

    This interface defines the contract for reference frame implementations.

    Example:
        >>> class InertialFrame(IReferenceFrame):
        ...     def frame_id(self):
        ...         return "inertial_001"
    """

    @abstractmethod
    def frame_id(self) -> str:
        """Get the frame identifier.

        Returns:
            Frame identifier

        Example:
            >>> frame.frame_id()
        """
        pass

    @abstractmethod
    def frame_type(self) -> str:
        """Get the frame type.

        Returns:
            Frame type

        Example:
            >>> frame.frame_type()
        """
        pass

    @abstractmethod
    def transform_to(self, target_frame: "IReferenceFrame") -> Dict[str, Any]:
        """Get transformation to another frame.

        Args:
            target_frame: Target reference frame

        Returns:
            Transformation matrix

        Example:
            >>> frame.transform_to(other_frame)
        """
        pass


class ITime(ABC):
    """Interface for time definitions.

    This interface defines the contract for time implementations.

    Example:
        >>> class PhysicalTime(ITime):
        ...     def value(self):
        ...         return 0.0
    """

    @abstractmethod
    def value(self) -> float:
        """Get the time value.

        Returns:
            Time value

        Example:
            >>> time.value()
        """
        pass

    @abstractmethod
    def time_type(self) -> str:
        """Get the time type.

        Returns:
            Time type

        Example:
            >>> time.time_type()
        """
        pass

    @abstractmethod
    def convert_to(self, target_type: str) -> "ITime":
        """Convert to a different time type.

        Args:
            target_type: Target time type

        Returns:
            Converted time

        Example:
            >>> time.convert_to("simulation")
        """
        pass


class IObservable(ABC):
    """Interface for observable definitions.

    This interface defines the contract for observable implementations.

    Example:
        >>> class Temperature(IObservable):
        ...     def observable_id(self):
        ...         return "temp_001"
    """

    @abstractmethod
    def observable_id(self) -> str:
        """Get the observable identifier.

        Returns:
            Observable identifier

        Example:
            >>> observable.observable_id()
        """
        pass

    @abstractmethod
    def observe(self) -> IMeasurement:
        """Perform an observation.

        Returns:
            Measurement result

        Example:
            >>> observable.observe()
        """
        pass


class IObserver(ABC):
    """Interface for observer definitions.

    This interface defines the contract for observer implementations.

    Example:
        >>> class Sensor(IObserver):
        ...     def observer_id(self):
        ...         return "sensor_001"
    """

    @abstractmethod
    def observer_id(self) -> str:
        """Get the observer identifier.

        Returns:
            Observer identifier

        Example:
            >>> observer.observer_id()
        """
        pass

    @abstractmethod
    def observe(self, observable: IObservable) -> IMeasurement:
        """Observe an observable.

        Args:
            observable: Observable to observe

        Returns:
            Measurement result

        Example:
            >>> observer.observe(observable)
        """
        pass


# Export
__all__ = [
    "IUnit",
    "IDimension",
    "IQuantity",
    "IMeasurement",
    "ICoordinate",
    "IReferenceFrame",
    "ITime",
    "IObservable",
    "IObserver",
]
