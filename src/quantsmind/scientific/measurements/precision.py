"""
Precision Module

This module provides precision definitions for the Scientific package.

Purpose
-------
Provide precision specifications for measurements.

Responsibilities
----------------
- Define precision structure
- Support precision calculations
- Support precision validation
- Support precision types

Dependencies
------------
typing (standard library)
quantsmind.scientific.enums (scientific enumerations)
quantsmind.scientific.exceptions (scientific exceptions)
quantsmind.scientific.types (scientific types)
"""

from __future__ import annotations

from typing import Any

from quantsmind.scientific.enums import PrecisionType
from quantsmind.scientific.exceptions import MeasurementError
from quantsmind.scientific.types import MeasurementValue


class Precision:
    """Concrete implementation of precision.

    This class provides precision functionality.

    Attributes:
        _value: Precision value (number of decimal places or significant figures)
        _type: Precision type
        _metadata: Precision metadata

    Example:
        >>> precision = Precision(3, PrecisionType.DECIMAL_PLACES)
        >>> precision.round(1.23456)
    """

    def __init__(
        self,
        value: int,
        precision_type: PrecisionType = PrecisionType.DOUBLE,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a Precision.

        Args:
            value: Precision value
            precision_type: Type of precision
            metadata: Precision metadata

        Example:
            >>> precision = Precision(3, PrecisionType.DECIMAL_PLACES)
        """
        if value < 0:
            raise MeasurementError("Precision value cannot be negative", measurement="precision")

        self._value = value
        self._type = precision_type
        self._metadata = metadata or {}

    @property
    def value(self) -> int:
        """Get the precision value.

        Returns:
            Precision value

        Example:
            >>> print(f"Value: {precision.value}")
        """
        return self._value

    @property
    def precision_type(self) -> PrecisionType:
        """Get the precision type.

        Returns:
            Precision type

        Example:
            >>> print(f"Type: {precision.precision_type}")
        """
        return self._type

    @property
    def metadata(self) -> dict[str, Any]:
        """Get the precision metadata.

        Returns:
            Precision metadata

        Example:
            >>> print(f"Metadata: {precision.metadata}")
        """
        return self._metadata.copy()

    def round(self, value: MeasurementValue) -> MeasurementValue:
        """Round a value to this precision.

        Args:
            value: Value to round

        Returns:
            Rounded value

        Example:
            >>> rounded = precision.round(1.23456)
        """
        if self._type == PrecisionType.DECIMAL_PLACES:
            return round(value, self._value)
        elif self._type == PrecisionType.SIGNIFICANT_FIGURES:
            return self._round_significant(value, self._value)
        else:  # SINGLE or DOUBLE precision
            if self._type == PrecisionType.SINGLE:
                return float(value)  # Single precision (32-bit)
            else:  # DOUBLE
                return float(value)  # Double precision (64-bit)

    def _round_significant(self, value: MeasurementValue, sig_figs: int) -> MeasurementValue:
        """Round to significant figures.

        Args:
            value: Value to round
            sig_figs: Number of significant figures

        Returns:
            Rounded value

        Example:
            >>> rounded = precision._round_significant(1.23456, 3)
        """
        if value == 0:
            return 0.0
        
        from math import floor, log10
        
        magnitude = floor(log10(abs(value)))
        scale = 10 ** (sig_figs - magnitude - 1)
        return round(value / scale) * scale

    def format(self, value: MeasurementValue) -> str:
        """Format a value to this precision.

        Args:
            value: Value to format

        Returns:
            Formatted string

        Example:
            >>> formatted = precision.format(1.23456)
        """
        if self._type == PrecisionType.DECIMAL_PLACES:
            return f"{value:.{self._value}f}"
        elif self._type == PrecisionType.SIGNIFICANT_FIGURES:
            rounded = self._round_significant(value, self._value)
            return f"{rounded:.{max(0, self._value - 1)}g}"
        else:
            return str(float(value))

    def check(self, value: MeasurementValue) -> bool:
        """Check if a value meets this precision.

        Args:
            value: Value to check

        Returns:
            True if meets precision, False otherwise

        Example:
            >>> if precision.check(1.234):
            ...     print("Meets precision")
        """
        formatted = self.format(value)
        return len(formatted.replace(".", "").replace("-", "").lstrip("0")) <= self._value

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Precision definition

        Example:
            >>> data = precision.to_dict()
        """
        return {
            "value": self._value,
            "type": self._type.value,
            "metadata": self._metadata.copy(),
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(precision)
        """
        return f"Precision(value={self._value}, type={self._type.value})"


# Export
__all__ = [
    "Precision",
]
