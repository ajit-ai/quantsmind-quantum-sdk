"""
Measurement Module

This module provides measurement definitions for the Scientific package.

Purpose
-------
Provide measurement definitions and operations.

Responsibilities
----------------
- Define measurement structure
- Support measurement uncertainty
- Support measurement validation
- Support measurement metadata

Dependencies
------------
typing (standard library)
quantsmind.scientific.exceptions (scientific exceptions)
quantsmind.scientific.interfaces (scientific interfaces)
quantsmind.scientific.types (scientific types)
quantsmind.scientific.units.base_unit (base unit)
"""

from __future__ import annotations

from typing import Any

from quantsmind.scientific.exceptions import MeasurementError
from quantsmind.scientific.interfaces import IMeasurement, IUnit
from quantsmind.scientific.types import ConfidenceLevel, MeasurementValue, UncertaintyValue


class Measurement(IMeasurement):
    """Concrete implementation of a measurement.

    This class provides measurement functionality.

    Attributes:
        _value: Measurement value
        _uncertainty: Measurement uncertainty
        _unit: Measurement unit
        _confidence: Confidence level
        _metadata: Measurement metadata

    Example:
        >>> length = Measurement(1.0, 0.01, meter_unit, 0.95)
        >>> length.value()
    """

    def __init__(
        self,
        value: MeasurementValue,
        uncertainty: UncertaintyValue,
        unit: IUnit,
        confidence: ConfidenceLevel = 0.95,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a Measurement.

        Args:
            value: Measurement value
            uncertainty: Measurement uncertainty
            unit: Measurement unit
            confidence: Confidence level (0.0 to 1.0)
            metadata: Measurement metadata

        Example:
            >>> length = Measurement(1.0, 0.01, meter_unit, 0.95)
        """
        if uncertainty < 0:
            raise MeasurementError("Uncertainty cannot be negative", measurement="uncertainty")
        
        if not 0.0 <= confidence <= 1.0:
            raise MeasurementError("Confidence must be between 0.0 and 1.0", measurement="confidence")

        self._value = value
        self._uncertainty = uncertainty
        self._unit = unit
        self._confidence = confidence
        self._metadata = metadata or {}

    @property
    def value(self) -> MeasurementValue:
        """Get the measurement value.

        Returns:
            Measurement value

        Example:
            >>> print(f"Value: {measurement.value}")
        """
        return self._value

    @property
    def uncertainty(self) -> UncertaintyValue:
        """Get the measurement uncertainty.

        Returns:
            Measurement uncertainty

        Example:
            >>> print(f"Uncertainty: {measurement.uncertainty}")
        """
        return self._uncertainty

    @property
    def unit(self) -> IUnit:
        """Get the measurement unit.

        Returns:
            Measurement unit

        Example:
            >>> print(f"Unit: {measurement.unit}")
        """
        return self._unit

    @property
    def confidence(self) -> ConfidenceLevel:
        """Get the confidence level.

        Returns:
            Confidence level

        Example:
            >>> print(f"Confidence: {measurement.confidence}")
        """
        return self._confidence

    @property
    def metadata(self) -> dict[str, Any]:
        """Get the measurement metadata.

        Returns:
            Measurement metadata

        Example:
            >>> print(f"Metadata: {measurement.metadata}")
        """
        return self._metadata.copy()

    @property
    def relative_uncertainty(self) -> float:
        """Get the relative uncertainty.

        Returns:
            Relative uncertainty (uncertainty / value)

        Example:
            >>> print(f"Relative uncertainty: {measurement.relative_uncertainty}")
        """
        if self._value == 0:
            return float('inf')
        return self._uncertainty / abs(self._value)

    @property
    def range(self) -> tuple[MeasurementValue, MeasurementValue]:
        """Get the measurement range.

        Returns:
            Tuple of (lower_bound, upper_bound)

        Example:
            >>> lower, upper = measurement.range
        """
        return (self._value - self._uncertainty, self._value + self._uncertainty)

    def is_within_range(self, value: MeasurementValue) -> bool:
        """Check if a value is within the measurement range.

        Args:
            value: Value to check

        Returns:
            True if within range, False otherwise

        Example:
            >>> if measurement.is_within_range(1.01):
            ...     print("Within range")
        """
        lower, upper = self.range
        return lower <= value <= upper

    def convert_to(self, target_unit: IUnit) -> Measurement:
        """Convert to a different unit.

        Args:
            target_unit: Target unit

        Returns:
            Converted measurement

        Raises:
            MeasurementError: If units are not compatible

        Example:
            >>> converted = measurement.convert_to(kilometer_unit)
        """
        if not self._unit.is_compatible(target_unit):
            raise MeasurementError(
                f"Cannot convert {self._unit.name()} to {target_unit.name()}",
                measurement="conversion"
            )

        # Convert value and uncertainty
        if hasattr(self._unit, 'convert_value'):
            converted_value = self._unit.convert_value(self._value, target_unit)
            converted_uncertainty = self._unit.convert_value(self._uncertainty, target_unit)
        else:
            # Generic conversion using conversion factors
            base_value = self._value * self._unit.conversion_factor()
            base_uncertainty = self._uncertainty * self._unit.conversion_factor()
            converted_value = base_value / target_unit.conversion_factor()
            converted_uncertainty = base_uncertainty / target_unit.conversion_factor()

        return Measurement(converted_value, converted_uncertainty, target_unit, self._confidence, self._metadata)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Measurement definition

        Example:
            >>> data = measurement.to_dict()
        """
        return {
            "value": self._value,
            "uncertainty": self._uncertainty,
            "unit": self._unit.name(),
            "confidence": self._confidence,
            "metadata": self._metadata.copy(),
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(measurement)
        """
        return f"Measurement(value={self._value} ± {self._uncertainty}, unit={self._unit.name()}, confidence={self._confidence})"


# Export
__all__ = [
    "Measurement",
]
