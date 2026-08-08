"""
Linear Scale Module

This module provides linear scale definitions for the Scientific package.

Purpose
-------
Provide linear scale implementation.

Responsibilities
----------------
- Define linear scale structure
- Support linear scale operations
- Support linear scale conversions
- Support linear scale validation

Dependencies
------------
typing (standard library)
quantsmind.scientific.scales.scale (scale)
quantsmind.scientific.enums (scientific enumerations)
quantsmind.scientific.exceptions (scientific exceptions)
quantsmind.scientific.types (scientific types)
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from quantsmind.scientific.enums import ScaleType
from quantsmind.scientific.scales.scale import Scale
from quantsmind.scientific.types import ScaleRange, ScaleValue


class LinearScale(Scale):
    """Concrete implementation of a linear scale.

    This class provides linear scale functionality.

    Attributes:
        _range: Scale range
        _metadata: Scale metadata

    Example:
        >>> scale = LinearScale(range=(0.0, 100.0))
        >>> scale.scale(50.0)
    """

    def __init__(
        self,
        range: Optional[ScaleRange] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a LinearScale.

        Args:
            range: Scale range (min, max)
            metadata: Scale metadata

        Example:
            >>> scale = LinearScale(range=(0.0, 100.0))
        """
        super().__init__(ScaleType.LINEAR, range, metadata)

    def scale(self, value: ScaleValue) -> ScaleValue:
        """Scale a value linearly.

        Args:
            value: Value to scale

        Returns:
            Scaled value

        Example:
            >>> scaled = scale.scale(50.0)
        """
        min_val, max_val = self._range
        
        if max_val == min_val:
            return 0.0
        
        return (value - min_val) / (max_val - min_val)

    def unscale(self, scaled_value: ScaleValue) -> ScaleValue:
        """Unscale a value linearly.

        Args:
            scaled_value: Scaled value

        Returns:
            Unscaled value

        Example:
            >>> unscaled = scale.unscale(0.5)
        """
        min_val, max_val = self._range
        
        return min_val + scaled_value * (max_val - min_val)

    def to_dict(self) -> Dict[str, Any]:
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
        return f"LinearScale(range={self._range})"


# Export
__all__ = [
    "LinearScale",
]
