"""
Logical Time Module

This module provides logical time definitions for the Scientific package.

Purpose
-------
Provide logical time management and operations.

Responsibilities
----------------
- Define logical time structure
- Support logical time operations
- Support logical time conversions
- Support logical time validation

Dependencies
------------
typing (standard library)
quantsmind.scientific.interfaces (scientific interfaces)
quantsmind.scientific.exceptions (scientific exceptions)
quantsmind.scientific.types (scientific types)
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from quantsmind.scientific.exceptions import TimeError
from quantsmind.scientific.interfaces import ITime


class LogicalTime(ITime):
    """Concrete implementation of logical time.

    This class provides logical time functionality.

    Attributes:
        _value: Logical time value
        _metadata: Logical time metadata

    Example:
        >>> logical_time = LogicalTime(0)
        >>> logical_time.value()
    """

    def __init__(
        self,
        value: int,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a LogicalTime.

        Args:
            value: Logical time value (integer)
            metadata: Logical time metadata

        Example:
            >>> logical_time = LogicalTime(0)
        """
        if value < 0:
            raise TimeError("Logical time cannot be negative", time_value=str(value))

        self._value = value
        self._metadata = metadata or {}

    @property
    def value(self) -> float:
        """Get the logical time value.

        Returns:
            Logical time value

        Example:
            >>> print(f"Value: {logical_time.value}")
        """
        return float(self._value)

    @property
    def int_value(self) -> int:
        """Get the logical time value as integer.

        Returns:
            Logical time value as integer

        Example:
            >>> print(f"Int value: {logical_time.int_value}")
        """
        return self._value

    @property
    def metadata(self) -> Dict[str, Any]:
        """Get the logical time metadata.

        Returns:
            Logical time metadata

        Example:
            >>> print(f"Metadata: {logical_time.metadata}")
        """
        return self._metadata.copy()

    def time_type(self) -> str:
        """Get the time type.

        Returns:
            Time type

        Example:
            >>> print(f"Type: {logical_time.time_type()}")
        """
        return "logical"

    def convert_to(self, target_type: str) -> ITime:
        """Convert to a different time type.

        Args:
            target_type: Target time type

        Returns:
            Converted time

        Raises:
            TimeError: If conversion not supported

        Example:
            >>> converted = logical_time.convert_to("simulation")
        """
        if target_type == "logical":
            return self
        elif target_type == "simulation":
            from quantsmind.scientific.time.simulation_time import SimulationTime
            return SimulationTime(float(self._value))
        elif target_type == "physical":
            from quantsmind.scientific.time.timestamp import Timestamp
            from datetime import datetime, timezone
            return Timestamp(datetime.fromtimestamp(float(self._value), timezone.utc))
        else:
            raise TimeError(f"Conversion to {target_type} not supported", time_value=str(target_type))

    def increment(self, delta: int = 1) -> "LogicalTime":
        """Increment logical time.

        Args:
            delta: Increment amount

        Returns:
            Incremented logical time

        Example:
            >>> incremented = logical_time.increment(1)
        """
        new_value = self._value + delta
        return LogicalTime(new_value, self._metadata)

    def decrement(self, delta: int = 1) -> "LogicalTime":
        """Decrement logical time.

        Args:
            delta: Decrement amount

        Returns:
            Decremented logical time

        Raises:
            TimeError: If result is negative

        Example:
            >>> decremented = logical_time.decrement(1)
        """
        new_value = self._value - delta
        if new_value < 0:
            raise TimeError("Logical time cannot be negative", time_value=str(new_value))
        return LogicalTime(new_value, self._metadata)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Logical time definition

        Example:
            >>> data = logical_time.to_dict()
        """
        return {
            "value": self._value,
            "time_type": self.time_type(),
            "metadata": self._metadata.copy(),
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(logical_time)
        """
        return f"LogicalTime(value={self._value})"


# Export
__all__ = [
    "LogicalTime",
]
