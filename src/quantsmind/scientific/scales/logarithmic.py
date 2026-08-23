"""
Logarithmic Scale Module

This module provides logarithmic scale definitions for the Scientific package.

Purpose
-------
Provide logarithmic scale implementation.

Responsibilities
----------------
- Define logarithmic scale structure
- Support logarithmic scale operations
- Support logarithmic scale conversions
- Support logarithmic scale validation

Dependencies
------------
typing (standard library)
math (standard library)
quantsmind.scientific.scales.scale (scale)
quantsmind.scientific.exceptions (scientific exceptions)
quantsmind.scientific.types (scientific types)
"""

from __future__ import annotations

import math
from typing import Any

from quantsmind.scientific.enums import ScaleType
from quantsmind.scientific.exceptions import MeasurementError
from quantsmind.scientific.scales.scale import Scale
from quantsmind.scientific.types import ScaleRange, ScaleValue


class LogarithmicScale(Scale):
    """Concrete implementation of a logarithmic scale.

    This class provides logarithmic scale functionality.

    Attributes:
        _base: Logarithm base
        _range: Scale range
        _metadata: Scale metadata

    Example:
        >>> scale = LogarithmicScale(base=10, range=(1.0, 1000.0))
        >>> scale.scale(10.0)
    """

    def __init__(
        self,
        base: float = 10.0,
        range: ScaleRange | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a LogarithmicScale.

        Args:
            base: Logarithm base
            range: Scale range (min, max)
            metadata: Scale metadata

        Example:
            >>> scale = LogarithmicScale(base=10, range=(1.0, 1000.0))
        """
        if base <= 0 or base == 1:
            raise MeasurementError("Logarithm base must be positive and not equal to 1", measurement="scale")

        super().__init__(ScaleType.LOGARITHMIC, range, metadata)
        self._base = base

    @property
    def base(self) -> float:
        """Get the logarithm base.

        Returns:
            Logarithm base

        Example:
            >>> print(f"Base: {scale.base}")
        """
        return self._base

    def scale(self, value: ScaleValue) -> ScaleValue:
        """Scale a value logarithmically.

        Args:
            value: Value to scale

        Returns:
            Scaled value

        Raises:
            MeasurementError: If value is non-positive

        Example:
            >>> scaled = scale.scale(10.0)
        """
        if value <= 0:
            raise MeasurementError("Value must be positive for logarithmic scaling", measurement="scale")

        min_val, max_val = self._range
        
        if min_val <= 0:
            raise MeasurementError("Minimum value must be positive for logarithmic scaling", measurement="scale")

        log_value = math.log(value, self._base)
        log_min = math.log(min_val, self._base)
        log_max = math.log(max_val, self._base)
        
        if log_max == log_min:
            return 0.0
        
        return (log_value - log_min) / (log_max - log_min)

    def unscale(self, scaled_value: ScaleValue) -> ScaleValue:
        """Unscale a value logarithmically.

        Args:
            scaled_value: Scaled value

        Returns:
            Unscaled value

        Example:
            >>> unscaled = scale.unscale(0.5)
        """
        min_val, max_val = self._range
        
        log_min = math.log(min_val, self._base)
        log_max = math.log(max_val, self._base)
        
        log_value = log_min + scaled_value * (log_max - log_min)
        return self._base ** log_value

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Scale definition

        Example:
            >>> data = scale.to_dict()
        """
        data = super().to_dict()
        data["base"] = self._base
        return data

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(scale)
        """
        return f"LogarithmicScale(base={self._base}, range={self._range})"


# Export
__all__ = [
    "LogarithmicScale",
]
