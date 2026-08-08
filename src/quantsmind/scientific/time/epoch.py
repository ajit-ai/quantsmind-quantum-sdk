"""
Epoch Module

This module provides epoch definitions for the Scientific package.

Purpose
-------
Provide epoch management and operations.

Responsibilities
----------------
- Define epoch structure
- Support epoch operations
- Support epoch conversions
- Support epoch validation

Dependencies
------------
typing (standard library)
datetime (standard library)
quantsmind.scientific.interfaces (scientific interfaces)
quantsmind.scientific.exceptions (scientific exceptions)
quantsmind.scientific.types (scientific types)
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from quantsmind.scientific.exceptions import TimeError
from quantsmind.scientific.interfaces import ITime
from quantsmind.scientific.types import EpochValue


class Epoch(ITime):
    """Concrete implementation of an epoch.

    This class provides epoch functionality.

    Attributes:
        _name: Epoch name
        _reference_time: Reference time
        _description: Epoch description
        _metadata: Epoch metadata

    Example:
        >>> epoch = Epoch("J2000", datetime(2000, 1, 1, 12, 0, 0))
        >>> epoch.value()
    """

    def __init__(
        self,
        name: str,
        reference_time: datetime,
        description: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize an Epoch.

        Args:
            name: Epoch name
            reference_time: Reference time
            description: Epoch description
            metadata: Epoch metadata

        Example:
            >>> epoch = Epoch("J2000", datetime(2000, 1, 1, 12, 0, 0))
        """
        self._name = name
        self._reference_time = reference_time
        self._description = description
        self._metadata = metadata or {}

    @property
    def name(self) -> str:
        """Get the epoch name.

        Returns:
            Epoch name

        Example:
            >>> print(f"Name: {epoch.name}")
        """
        return self._name

    @property
    def reference_time(self) -> datetime:
        """Get the reference time.

        Returns:
            Reference time

        Example:
            >>> print(f"Reference time: {epoch.reference_time}")
        """
        return self._reference_time

    @property
    def description(self) -> str:
        """Get the epoch description.

        Returns:
            Epoch description

        Example:
            >>> print(f"Description: {epoch.description}")
        """
        return self._description

    @property
    def metadata(self) -> Dict[str, Any]:
        """Get the epoch metadata.

        Returns:
            Epoch metadata

        Example:
            >>> print(f"Metadata: {epoch.metadata}")
        """
        return self._metadata.copy()

    def value(self) -> float:
        """Get the epoch value.

        Returns:
            Epoch value as Unix timestamp

        Example:
            >>> print(f"Value: {epoch.value}")
        """
        return self._reference_time.timestamp()

    def time_type(self) -> str:
        """Get the time type.

        Returns:
            Time type

        Example:
            >>> print(f"Type: {epoch.time_type()}")
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
            >>> converted = epoch.convert_to("simulation")
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

    def time_since(self, timestamp: datetime) -> float:
        """Calculate time since a timestamp.

        Args:
            timestamp: Timestamp to compare

        Returns:
            Time difference in seconds

        Example:
            >>> delta = epoch.time_since(datetime.utcnow())
        """
        return (timestamp - self._reference_time).total_seconds()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Epoch definition

        Example:
            >>> data = epoch.to_dict()
        """
        return {
            "name": self._name,
            "reference_time": self._reference_time.isoformat(),
            "description": self._description,
            "time_type": self.time_type(),
            "metadata": self._metadata.copy(),
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(epoch)
        """
        return f"Epoch(name={self._name}, reference_time={self._reference_time.isoformat()})"


# Export
__all__ = [
    "Epoch",
]
