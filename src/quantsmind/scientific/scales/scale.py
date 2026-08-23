"""
Scale Module

This module provides scale definitions for the Scientific package.

Purpose
-------
Provide scale definitions and operations.

Responsibilities
----------------
- Define scale structure
- Support scale operations
- Support scale conversions
- Support scale validation

Dependencies
------------
typing (standard library)
quantsmind.scientific.enums (scientific enumerations)
quantsmind.scientific.exceptions (scientific exceptions)
quantsmind.scientific.types (scientific types)
"""

from __future__ import annotations

from typing import Any

from quantsmind.scientific.enums import ScaleType
from quantsmind.scientific.types import ScaleRange, ScaleValue


class Scale:
    """Concrete implementation of a scale.

    This class provides scale functionality.

    Attributes:
        _scale_type: Scale type
        _range: Scale range
        _metadata: Scale metadata

    Example:
        >>> scale = Scale(ScaleType.LINEAR, (0.0, 100.0))
        >>> scale.scale(50.0)
    """

    def __init__(
        self,
        scale_type: ScaleType = ScaleType.LINEAR,
        range: ScaleRange | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a Scale.

        Args:
            scale_type: Scale type
            range: Scale range (min, max)
            metadata: Scale metadata

        Example:
            >>> scale = Scale(ScaleType.LINEAR, (0.0, 100.0))
        """
        self._scale_type = scale_type
        self._range = range or (0.0, 1.0)
        self._metadata = metadata or {}

    @property
    def scale_type(self) -> ScaleType:
        """Get the scale type.

        Returns:
            Scale type

        Example:
            >>> print(f"Type: {scale.scale_type}")
        """
        return self._scale_type

    @property
    def range(self) -> ScaleRange:
        """Get the scale range.

        Returns:
            Scale range

        Example:
            >>> print(f"Range: {scale.range}")
        """
        return self._range

    @property
    def metadata(self) -> dict[str, Any]:
        """Get the scale metadata.

        Returns:
            Scale metadata

        Example:
            >>> print(f"Metadata: {scale.metadata}")
        """
        return self._metadata.copy()

    def scale(self, value: ScaleValue) -> ScaleValue:
        """Scale a value.

        Args:
            value: Value to scale

        Returns:
            Scaled value

        Example:
            >>> scaled = scale.scale(50.0)
        """
        min_val, max_val = self._range
        
        if self._scale_type == ScaleType.LINEAR:
            return self._scale_linear(value, min_val, max_val)
        elif self._scale_type == ScaleType.LOGARITHMIC:
            return self._scale_logarithmic(value, min_val, max_val)
        else:
            return value

    def _scale_linear(self, value: ScaleValue, min_val: ScaleValue, max_val: ScaleValue) -> ScaleValue:
        """Scale a value linearly.

        Args:
            value: Value to scale
            min_val: Minimum value
            max_val: Maximum value

        Returns:
            Scaled value

        Example:
            >>> scaled = scale._scale_linear(50.0, 0.0, 100.0)
        """
        if max_val == min_val:
            return 0.0
        return (value - min_val) / (max_val - min_val)

    def _scale_logarithmic(self, value: ScaleValue, min_val: ScaleValue, max_val: ScaleValue) -> ScaleValue:
        """Scale a value logarithmically.

        Args:
            value: Value to scale
            min_val: Minimum value
            max_val: Maximum value

        Returns:
            Scaled value

        Example:
            >>> scaled = scale._scale_logarithmic(50.0, 1.0, 100.0)
        """
        import math
        
        if value <= 0 or min_val <= 0:
            return 0.0
        
        log_value = math.log(value)
        log_min = math.log(min_val)
        log_max = math.log(max_val)
        
        if log_max == log_min:
            return 0.0
        
        return (log_value - log_min) / (log_max - log_min)

    def unscale(self, scaled_value: ScaleValue) -> ScaleValue:
        """Unscale a value.

        Args:
            scaled_value: Scaled value

        Returns:
            Unscaled value

        Example:
            >>> unscaled = scale.unscale(0.5)
        """
        min_val, max_val = self._range
        
        if self._scale_type == ScaleType.LINEAR:
            return self._unscale_linear(scaled_value, min_val, max_val)
        elif self._scale_type == ScaleType.LOGARITHMIC:
            return self._unscale_logarithmic(scaled_value, min_val, max_val)
        else:
            return scaled_value

    def _unscale_linear(self, scaled_value: ScaleValue, min_val: ScaleValue, max_val: ScaleValue) -> ScaleValue:
        """Unscale a value linearly.

        Args:
            scaled_value: Scaled value
            min_val: Minimum value
            max_val: Maximum value

        Returns:
            Unscaled value

        Example:
            >>> unscaled = scale._unscale_linear(0.5, 0.0, 100.0)
        """
        return min_val + scaled_value * (max_val - min_val)

    def _unscale_logarithmic(self, scaled_value: ScaleValue, min_val: ScaleValue, max_val: ScaleValue) -> ScaleValue:
        """Unscale a value logarithmically.

        Args:
            scaled_value: Scaled value
            min_val: Minimum value
            max_val: Maximum value

        Returns:
            Unscaled value

        Example:
            >>> unscaled = scale._unscale_logarithmic(0.5, 1.0, 100.0)
        """
        import math
        
        log_min = math.log(min_val)
        log_max = math.log(max_val)
        
        log_value = log_min + scaled_value * (log_max - log_min)
        return math.exp(log_value)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Scale definition

        Example:
            >>> data = scale.to_dict()
        """
        return {
            "scale_type": self._scale_type.value,
            "range": self._range,
            "metadata": self._metadata.copy(),
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(scale)
        """
        return f"Scale(type={self._scale_type.value}, range={self._range})"


# Export
__all__ = [
    "Scale",
]
