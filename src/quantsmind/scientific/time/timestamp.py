"""
Timestamp Module

This module provides timestamp definitions for the Scientific package.

Purpose
-------
Provide timestamp management and operations.

Responsibilities
----------------
- Define timestamp structure
- Support timestamp operations
- Support timestamp conversions
- Support timestamp validation

Dependencies
------------
typing (standard library)
datetime (standard library)
quantsmind.scientific.interfaces (scientific interfaces)
quantsmind.scientific.exceptions (scientific exceptions)
quantsmind.scientific.types (scientific types)
"""

from __future__ import annotations

from datetime import UTC, datetime, timezone
from typing import Any

from quantsmind.scientific.exceptions import TimeError
from quantsmind.scientific.interfaces import ITime


class Timestamp(ITime):
    """Concrete implementation of a timestamp.

    This class provides timestamp functionality.

    Attributes:
        _value: Timestamp value
        _timezone: Timezone
        _metadata: Timestamp metadata

    Example:
        >>> ts = Timestamp(datetime.now(UTC).replace(tzinfo=None))
        >>> ts.value()
    """

    def __init__(
        self,
        value: datetime,
        tz: timezone | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a Timestamp.

        Args:
            value: Timestamp value
            tz: Timezone
            metadata: Timestamp metadata

        Example:
            >>> ts = Timestamp(datetime.now(UTC).replace(tzinfo=None))
        """
        self._value = value
        self._timezone = tz or UTC
        self._metadata = metadata or {}

    @property
    def value(self) -> float:
        """Get the timestamp value.

        Returns:
            Timestamp value as Unix timestamp

        Example:
            >>> print(f"Value: {timestamp.value}")
        """
        return self._value.timestamp()

    @property
    def datetime_value(self) -> datetime:
        """Get the datetime value.

        Returns:
            Datetime value

        Example:
            >>> print(f"Datetime: {timestamp.datetime_value}")
        """
        return self._value

    @property
    def timezone(self) -> timezone:
        """Get the timezone.

        Returns:
            Timezone

        Example:
            >>> print(f"Timezone: {timestamp.timezone}")
        """
        return self._timezone

    @property
    def metadata(self) -> dict[str, Any]:
        """Get the timestamp metadata.

        Returns:
            Timestamp metadata

        Example:
            >>> print(f"Metadata: {timestamp.metadata}")
        """
        return self._metadata.copy()

    def time_type(self) -> str:
        """Get the time type.

        Returns:
            Time type

        Example:
            >>> print(f"Type: {timestamp.time_type()}")
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
            >>> converted = timestamp.convert_to("simulation")
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

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Timestamp definition

        Example:
            >>> data = timestamp.to_dict()
        """
        return {
            "value": self.value,
            "datetime": self._value.isoformat(),
            "timezone": str(self._timezone),
            "time_type": self.time_type(),
            "metadata": self._metadata.copy(),
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(timestamp)
        """
        return f"Timestamp(value={self.value}, datetime={self._value.isoformat()})"


# Export
__all__ = [
    "Timestamp",
]
