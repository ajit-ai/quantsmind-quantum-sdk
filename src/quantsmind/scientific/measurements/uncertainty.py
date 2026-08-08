"""
Uncertainty Module

This module provides uncertainty definitions for the Scientific package.

Purpose
-------
Provide uncertainty calculation and propagation.

Responsibilities
----------------
- Define uncertainty types
- Support uncertainty propagation
- Support uncertainty combination
- Support statistical uncertainty

Dependencies
------------
typing (standard library)
math (standard library)
quantsmind.scientific.enums (scientific enumerations)
quantsmind.scientific.exceptions (scientific exceptions)
quantsmind.scientific.types (scientific types)
"""

from __future__ import annotations

import math
from typing import List, Optional, Tuple

from quantsmind.scientific.enums import UncertaintyType
from quantsmind.scientific.exceptions import MeasurementError
from quantsmind.scientific.types import UncertaintyValue


class Uncertainty:
    """Concrete implementation of uncertainty.

    This class provides uncertainty functionality.

    Attributes:
        _value: Uncertainty value
        _type: Uncertainty type
        _confidence: Confidence level

    Example:
        >>> uncertainty = Uncertainty(0.01, UncertaintyType.ABSOLUTE, 0.95)
        >>> uncertainty.value()
    """

    def __init__(
        self,
        value: UncertaintyValue,
        uncertainty_type: UncertaintyType = UncertaintyType.ABSOLUTE,
        confidence: float = 0.95,
    ) -> None:
        """Initialize an Uncertainty.

        Args:
            value: Uncertainty value
            uncertainty_type: Type of uncertainty
            confidence: Confidence level

        Example:
            >>> uncertainty = Uncertainty(0.01, UncertaintyType.ABSOLUTE, 0.95)
        """
        if value < 0:
            raise MeasurementError("Uncertainty value cannot be negative", measurement="uncertainty")
        
        if not 0.0 <= confidence <= 1.0:
            raise MeasurementError("Confidence must be between 0.0 and 1.0", measurement="confidence")

        self._value = value
        self._type = uncertainty_type
        self._confidence = confidence

    @property
    def value(self) -> UncertaintyValue:
        """Get the uncertainty value.

        Returns:
            Uncertainty value

        Example:
            >>> print(f"Value: {uncertainty.value}")
        """
        return self._value

    @property
    def uncertainty_type(self) -> UncertaintyType:
        """Get the uncertainty type.

        Returns:
            Uncertainty type

        Example:
            >>> print(f"Type: {uncertainty.uncertainty_type}")
        """
        return self._type

    @property
    def confidence(self) -> float:
        """Get the confidence level.

        Returns:
            Confidence level

        Example:
            >>> print(f"Confidence: {uncertainty.confidence}")
        """
        return self._confidence

    def to_absolute(self, measured_value: float) -> "Uncertainty":
        """Convert to absolute uncertainty.

        Args:
            measured_value: Measured value

        Returns:
            Absolute uncertainty

        Example:
            >>> absolute = uncertainty.to_absolute(1.0)
        """
        if self._type == UncertaintyType.ABSOLUTE:
            return self
        
        if self._type == UncertaintyType.RELATIVE:
            absolute_value = self._value * abs(measured_value)
            return Uncertainty(absolute_value, UncertaintyType.ABSOLUTE, self._confidence)
        
        return self

    def to_relative(self, measured_value: float) -> "Uncertainty":
        """Convert to relative uncertainty.

        Args:
            measured_value: Measured value

        Returns:
            Relative uncertainty

        Raises:
            MeasurementError: If measured value is zero

        Example:
            >>> relative = uncertainty.to_relative(1.0)
        """
        if measured_value == 0:
            raise MeasurementError("Cannot convert to relative uncertainty with zero value", measurement="conversion")
        
        if self._type == UncertaintyType.RELATIVE:
            return self
        
        if self._type == UncertaintyType.ABSOLUTE:
            relative_value = self._value / abs(measured_value)
            return Uncertainty(relative_value, UncertaintyType.RELATIVE, self._confidence)
        
        return self

    @staticmethod
    def combine_independent(uncertainties: List["Uncertainty"]) -> "Uncertainty":
        """Combine independent uncertainties (root sum of squares).

        Args:
            uncertainties: List of uncertainties to combine

        Returns:
            Combined uncertainty

        Example:
            >>> combined = Uncertainty.combine_independent([u1, u2])
        """
        if not uncertainties:
            return Uncertainty(0.0)
        
        # Convert all to absolute for combination
        absolute_values = [u.value for u in uncertainties]
        combined_value = math.sqrt(sum(u ** 2 for u in absolute_values))
        
        return Uncertainty(combined_value, UncertaintyType.ABSOLUTE, uncertainties[0].confidence)

    @staticmethod
    def combine_correlated(uncertainties: List["Uncertainty"]) -> "Uncertainty":
        """Combine correlated uncertainties (linear sum).

        Args:
            uncertainties: List of uncertainties to combine

        Returns:
            Combined uncertainty

        Example:
            >>> combined = Uncertainty.combine_correlated([u1, u2])
        """
        if not uncertainties:
            return Uncertainty(0.0)
        
        combined_value = sum(u.value for u in uncertainties)
        
        return Uncertainty(combined_value, UncertaintyType.ABSOLUTE, uncertainties[0].confidence)

    def propagate_addition(self, other: "Uncertainty") -> "Uncertainty":
        """Propagate uncertainty through addition.

        Args:
            other: Other uncertainty

        Returns:
            Propagated uncertainty

        Example:
            >>> propagated = uncertainty.propagate_addition(other_uncertainty)
        """
        return Uncertainty.combine_independent([self, other])

    def propagate_multiplication(self, other: "Uncertainty", value1: float, value2: float) -> "Uncertainty":
        """Propagate uncertainty through multiplication.

        Args:
            other: Other uncertainty
            value1: First value
            value2: Second value

        Returns:
            Propagated uncertainty

        Example:
            >>> propagated = uncertainty.propagate_multiplication(other_uncertainty, 1.0, 2.0)
        """
        # Convert to relative uncertainties
        rel1 = self.to_relative(value1)
        rel2 = other.to_relative(value2)
        
        # Combine relative uncertainties
        combined_rel = Uncertainty.combine_independent([rel1, rel2])
        
        # Convert back to absolute
        result_value = value1 * value2
        return combined_rel.to_absolute(result_value)

    def scale(self, factor: float) -> "Uncertainty":
        """Scale the uncertainty.

        Args:
            factor: Scale factor

        Returns:
            Scaled uncertainty

        Example:
            >>> scaled = uncertainty.scale(2.0)
        """
        return Uncertainty(self._value * factor, self._type, self._confidence)

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(uncertainty)
        """
        return f"Uncertainty(value={self._value}, type={self._type.value}, confidence={self._confidence})"


# Export
__all__ = [
    "Uncertainty",
]
