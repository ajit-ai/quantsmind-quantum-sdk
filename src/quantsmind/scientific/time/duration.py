"""
Duration Module

This module provides duration definitions for the Scientific package.

Purpose
-------
Provide duration management and operations.

Responsibilities
----------------
- Define duration structure
- Support duration operations
- Support duration conversions
- Support duration validation

Dependencies
------------
typing (standard library)
quantsmind.scientific.interfaces (scientific interfaces)
quantsmind.scientific.exceptions (scientific exceptions)
quantsmind.scientific.types (scientific types)
"""

from __future__ import annotations

from typing import Any

from quantsmind.scientific.exceptions import TimeError
from quantsmind.scientific.interfaces import ITime
from quantsmind.scientific.types import DurationValue


class Duration(ITime):
    """Concrete implementation of a duration.

    This class provides duration functionality.

    Attributes:
        _value: Duration value
        _unit: Duration unit
        _metadata: Duration metadata

    Example:
        >>> dur = Duration(60.0, "second")
        >>> dur.value()
    """

    def __init__(
        self,
        value: DurationValue,
        unit: str = "second",
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a Duration.

        Args:
            value: Duration value
            unit: Duration unit (second, minute, hour, day)
            metadata: Duration metadata

        Example:
            >>> dur = Duration(60.0, "second")
        """
        if value < 0:
            raise TimeError("Duration cannot be negative", time_value=str(value))

        self._value = value
        self._unit = unit
        self._metadata = metadata or {}

    @property
    def value(self) -> float:
        """Get the duration value.

        Returns:
            Duration value in seconds

        Example:
            >>> print(f"Value: {duration.value}")
        """
        return self._to_seconds()

    @property
    def original_value(self) -> DurationValue:
        """Get the original duration value.

        Returns:
            Original duration value

        Example:
            >>> print(f"Original value: {duration.original_value}")
        """
        return self._value

    @property
    def unit(self) -> str:
        """Get the duration unit.

        Returns:
            Duration unit

        Example:
            >>> print(f"Unit: {duration.unit}")
        """
        return self._unit

    @property
    def metadata(self) -> dict[str, Any]:
        """Get the duration metadata.

        Returns:
            Duration metadata

        Example:
            >>> print(f"Metadata: {duration.metadata}")
        """
        return self._metadata.copy()

    def _to_seconds(self) -> float:
        """Convert to seconds.

        Returns:
            Duration in seconds

        Example:
            >>> seconds = duration._to_seconds()
        """
        conversion_factors = {
            "second": 1.0,
            "minute": 60.0,
            "hour": 3600.0,
            "day": 86400.0,
        }
        return self._value * conversion_factors.get(self._unit, 1.0)

    def time_type(self) -> str:
        """Get the time type.

        Returns:
            Time type

        Example:
            >>> print(f"Type: {duration.time_type()}")
        """
        return "physical"

    def convert_to(self, target_type: str) -> ITime:
        """Convert to a different time type.

        Args:
            target_type: Target time type

        Returns:
            Converted time

        Raises:
            TimeError: If conversion not supported

        Example:
            >>> converted = duration.convert_to("simulation")
        """
        if target_type == "physical":
            return self
        elif target_type == "simulation":
            from quantsmind.scientific.time.simulation_time import SimulationTime
            return SimulationTime(self.value)
        elif target_type == "logical":
            from quantsmind.scientific.time.logical_time import LogicalTime
            return LogicalTime(int(self.value))
        else:
            raise TimeError(f"Conversion to {target_type} not supported", time_value=str(target_type))

    def to_unit(self, target_unit: str) -> Duration:
        """Convert to a different unit.

        Args:
            target_unit: Target unit

        Returns:
            Converted duration

        Raises:
            TimeError: If unit not supported

        Example:
            >>> converted = duration.to_unit("minute")
        """
        conversion_factors = {
            "second": 1.0,
            "minute": 60.0,
            "hour": 3600.0,
            "day": 86400.0,
        }

        if target_unit not in conversion_factors:
            raise TimeError(f"Unit {target_unit} not supported", time_value=str(target_unit))

        seconds = self._to_seconds()
        converted_value = seconds / conversion_factors[target_unit]
        return Duration(converted_value, target_unit, self._metadata)

    def add(self, other: Duration) -> Duration:
        """Add durations.

        Args:
            other: Other duration

        Returns:
            Resulting duration

        Example:
            >>> result = duration.add(other_duration)
        """
        total_seconds = self._to_seconds() + other._to_seconds()
        return Duration(total_seconds, "second", self._metadata)

    def subtract(self, other: Duration) -> Duration:
        """Subtract durations.

        Args:
            other: Other duration

        Returns:
            Resulting duration

        Raises:
            TimeError: If result is negative

        Example:
            >>> result = duration.subtract(other_duration)
        """
        total_seconds = self._to_seconds() - other._to_seconds()
        if total_seconds < 0:
            raise TimeError("Duration cannot be negative", time_value=str(total_seconds))
        return Duration(total_seconds, "second", self._metadata)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Duration definition

        Example:
            >>> data = duration.to_dict()
        """
        return {
            "value": self._value,
            "unit": self._unit,
            "seconds": self.value,
            "time_type": self.time_type(),
            "metadata": self._metadata.copy(),
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(duration)
        """
        return f"Duration(value={self._value}, unit={self._unit})"


# Export
__all__ = [
    "Duration",
]
