"""
Tolerance Module

This module provides tolerance definitions for the Scientific package.

Purpose
-------
Provide tolerance specifications for measurements.

Responsibilities
----------------
- Define tolerance structure
- Support tolerance checks
- Support tolerance ranges
- Support tolerance validation

Dependencies
------------
typing (standard library)
quantsmind.scientific.exceptions (scientific exceptions)
quantsmind.scientific.types (scientific types)
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from quantsmind.scientific.exceptions import MeasurementError
from quantsmind.scientific.types import ToleranceValue


class Tolerance:
    """Concrete implementation of a tolerance.

    This class provides tolerance functionality.

    Attributes:
        _value: Tolerance value
        _type: Tolerance type (absolute or relative)
        _metadata: Tolerance metadata

    Example:
        >>> tolerance = Tolerance(0.01, "absolute")
        >>> tolerance.check(1.0, 1.005)
    """

    def __init__(
        self,
        value: ToleranceValue,
        tolerance_type: str = "absolute",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a Tolerance.

        Args:
            value: Tolerance value
            tolerance_type: Type of tolerance ("absolute" or "relative")
            metadata: Tolerance metadata

        Example:
            >>> tolerance = Tolerance(0.01, "absolute")
        """
        if value < 0:
            raise MeasurementError("Tolerance value cannot be negative", measurement="tolerance")
        
        if tolerance_type not in ["absolute", "relative"]:
            raise MeasurementError("Tolerance type must be 'absolute' or 'relative'", measurement="tolerance")

        self._value = value
        self._type = tolerance_type
        self._metadata = metadata or {}

    @property
    def value(self) -> ToleranceValue:
        """Get the tolerance value.

        Returns:
            Tolerance value

        Example:
            >>> print(f"Value: {tolerance.value}")
        """
        return self._value

    @property
    def tolerance_type(self) -> str:
        """Get the tolerance type.

        Returns:
            Tolerance type

        Example:
            >>> print(f"Type: {tolerance.tolerance_type}")
        """
        return self._type

    @property
    def metadata(self) -> Dict[str, Any]:
        """Get the tolerance metadata.

        Returns:
            Tolerance metadata

        Example:
            >>> print(f"Metadata: {tolerance.metadata}")
        """
        return self._metadata.copy()

    def get_range(self, nominal: float) -> Tuple[float, float]:
        """Get the tolerance range for a nominal value.

        Args:
            nominal: Nominal value

        Returns:
            Tuple of (lower_bound, upper_bound)

        Example:
            >>> lower, upper = tolerance.get_range(1.0)
        """
        if self._type == "absolute":
            lower = nominal - self._value
            upper = nominal + self._value
        else:  # relative
            lower = nominal * (1 - self._value)
            upper = nominal * (1 + self._value)
        
        return (lower, upper)

    def check(self, nominal: float, measured: float) -> bool:
        """Check if a measured value is within tolerance.

        Args:
            nominal: Nominal value
            measured: Measured value

        Returns:
            True if within tolerance, False otherwise

        Example:
            >>> if tolerance.check(1.0, 1.005):
            ...     print("Within tolerance")
        """
        lower, upper = self.get_range(nominal)
        return lower <= measured <= upper

    def deviation(self, nominal: float, measured: float) -> float:
        """Calculate the deviation from nominal.

        Args:
            nominal: Nominal value
            measured: Measured value

        Returns:
            Deviation from nominal

        Example:
            >>> dev = tolerance.deviation(1.0, 1.005)
        """
        if self._type == "absolute":
            return measured - nominal
        else:  # relative
            if nominal == 0:
                return 0.0
            return (measured - nominal) / nominal

    def is_within_tolerance(self, deviation: float) -> bool:
        """Check if a deviation is within tolerance.

        Args:
            deviation: Deviation value

        Returns:
            True if within tolerance, False otherwise

        Example:
            >>> if tolerance.is_within_tolerance(0.005):
            ...     print("Within tolerance")
        """
        if self._type == "absolute":
            return abs(deviation) <= self._value
        else:  # relative
            return abs(deviation) <= self._value

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Tolerance definition

        Example:
            >>> data = tolerance.to_dict()
        """
        return {
            "value": self._value,
            "type": self._type,
            "metadata": self._metadata.copy(),
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(tolerance)
        """
        return f"Tolerance(value={self._value}, type={self._type})"


# Export
__all__ = [
    "Tolerance",
]
