"""
Simulation Time Module

This module provides simulation time definitions for the Scientific package.

Purpose
-------
Provide simulation time management and operations.

Responsibilities
----------------
- Define simulation time structure
- Support simulation time operations
- Support simulation time conversions
- Support simulation time validation

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
from quantsmind.scientific.types import DurationValue


class SimulationTime(ITime):
    """Concrete implementation of simulation time.

    This class provides simulation time functionality.

    Attributes:
        _value: Simulation time value
        _time_step: Time step
        _metadata: Simulation time metadata

    Example:
        >>> sim_time = SimulationTime(0.0, 0.01)
        >>> sim_time.value()
    """

    def __init__(
        self,
        value: float,
        time_step: float = 0.01,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a SimulationTime.

        Args:
            value: Simulation time value
            time_step: Time step for simulation
            metadata: Simulation time metadata

        Example:
            >>> sim_time = SimulationTime(0.0, 0.01)
        """
        if value < 0:
            raise TimeError("Simulation time cannot be negative", time_value=str(value))

        if time_step <= 0:
            raise TimeError("Time step must be positive", time_value=str(time_step))

        self._value = value
        self._time_step = time_step
        self._metadata = metadata or {}

    @property
    def value(self) -> float:
        """Get the simulation time value.

        Returns:
            Simulation time value

        Example:
            >>> print(f"Value: {sim_time.value}")
        """
        return self._value

    @property
    def time_step(self) -> float:
        """Get the time step.

        Returns:
            Time step

        Example:
            >>> print(f"Time step: {sim_time.time_step}")
        """
        return self._time_step

    @property
    def metadata(self) -> Dict[str, Any]:
        """Get the simulation time metadata.

        Returns:
            Simulation time metadata

        Example:
            >>> print(f"Metadata: {sim_time.metadata}")
        """
        return self._metadata.copy()

    def time_type(self) -> str:
        """Get the time type.

        Returns:
            Time type

        Example:
            >>> print(f"Type: {sim_time.time_type()}")
        """
        return "simulation"

    def convert_to(self, target_type: str) -> ITime:
        """Convert to a different time type.

        Args:
            target_type: Target time type

        Returns:
            Converted time

        Raises:
            TimeError: If conversion not supported

        Example:
            >>> converted = sim_time.convert_to("physical")
        """
        if target_type == "simulation":
            return self
        elif target_type == "physical":
            from quantsmind.scientific.time.timestamp import Timestamp
            from datetime import datetime, timezone
            return Timestamp(datetime.fromtimestamp(self.value, timezone.utc))
        elif target_type == "logical":
            from quantsmind.scientific.time.logical_time import LogicalTime
            return LogicalTime(int(self.value))
        else:
            raise TimeError(f"Conversion to {target_type} not supported", time_value=str(target_type))

    def advance(self, steps: int = 1) -> "SimulationTime":
        """Advance simulation time.

        Args:
            steps: Number of steps to advance

        Returns:
            Advanced simulation time

        Example:
            >>> advanced = sim_time.advance(10)
        """
        new_value = self._value + (steps * self._time_step)
        return SimulationTime(new_value, self._time_step, self._metadata)

    def step_count(self) -> int:
        """Get the current step count.

        Returns:
            Step count

        Example:
            >>> steps = sim_time.step_count()
        """
        return int(self._value / self._time_step)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Simulation time definition

        Example:
            >>> data = sim_time.to_dict()
        """
        return {
            "value": self._value,
            "time_step": self._time_step,
            "step_count": self.step_count(),
            "time_type": self.time_type(),
            "metadata": self._metadata.copy(),
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(sim_time)
        """
        return f"SimulationTime(value={self._value}, time_step={self._time_step})"


# Export
__all__ = [
    "SimulationTime",
]
