"""
Accuracy Module

This module provides accuracy definitions for the Scientific package.

Purpose
-------
Provide accuracy specifications for measurements.

Responsibilities
----------------
- Define accuracy structure
- Support accuracy calculations
- Support accuracy validation
- Support error analysis

Dependencies
------------
typing (standard library)
quantsmind.scientific.exceptions (scientific exceptions)
quantsmind.scientific.types (scientific types)
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from quantsmind.scientific.exceptions import MeasurementError
from quantsmind.scientific.types import MeasurementValue


class Accuracy:
    """Concrete implementation of accuracy.

    This class provides accuracy functionality.

    Attributes:
        _value: Accuracy value
        _reference: Reference value
        _metadata: Accuracy metadata

    Example:
        >>> accuracy = Accuracy(0.01, 1.0)
        >>> accuracy.calculate_error(1.005)
    """

    def __init__(
        self,
        value: MeasurementValue,
        reference: MeasurementValue,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize an Accuracy.

        Args:
            value: Accuracy value (maximum acceptable error)
            reference: Reference value (true value)
            metadata: Accuracy metadata

        Example:
            >>> accuracy = Accuracy(0.01, 1.0)
        """
        if value < 0:
            raise MeasurementError("Accuracy value cannot be negative", measurement="accuracy")

        self._value = value
        self._reference = reference
        self._metadata = metadata or {}

    @property
    def value(self) -> MeasurementValue:
        """Get the accuracy value.

        Returns:
            Accuracy value

        Example:
            >>> print(f"Value: {accuracy.value}")
        """
        return self._value

    @property
    def reference(self) -> MeasurementValue:
        """Get the reference value.

        Returns:
            Reference value

        Example:
            >>> print(f"Reference: {accuracy.reference}")
        """
        return self._reference

    @property
    def metadata(self) -> Dict[str, Any]:
        """Get the accuracy metadata.

        Returns:
            Accuracy metadata

        Example:
            >>> print(f"Metadata: {accuracy.metadata}")
        """
        return self._metadata.copy()

    def absolute_error(self, measured: MeasurementValue) -> MeasurementValue:
        """Calculate absolute error.

        Args:
            measured: Measured value

        Returns:
            Absolute error

        Example:
            >>> error = accuracy.absolute_error(1.005)
        """
        return abs(measured - self._reference)

    def relative_error(self, measured: MeasurementValue) -> float:
        """Calculate relative error.

        Args:
            measured: Measured value

        Returns:
            Relative error

        Raises:
            MeasurementError: If reference value is zero

        Example:
            >>> error = accuracy.relative_error(1.005)
        """
        if self._reference == 0:
            raise MeasurementError("Cannot calculate relative error with zero reference", measurement="relative_error")
        return abs(measured - self._reference) / abs(self._reference)

    def percentage_error(self, measured: MeasurementValue) -> float:
        """Calculate percentage error.

        Args:
            measured: Measured value

        Returns:
            Percentage error

        Example:
            >>> error = accuracy.percentage_error(1.005)
        """
        return self.relative_error(measured) * 100.0

    def is_accurate(self, measured: MeasurementValue) -> bool:
        """Check if a measured value is within accuracy.

        Args:
            measured: Measured value

        Returns:
            True if accurate, False otherwise

        Example:
            >>> if accuracy.is_accurate(1.005):
            ...     print("Accurate")
        """
        return self.absolute_error(measured) <= self._value

    def accuracy_score(self, measured: MeasurementValue) -> float:
        """Calculate accuracy score (0.0 to 1.0).

        Args:
            measured: Measured value

        Returns:
            Accuracy score

        Example:
            >>> score = accuracy.accuracy_score(1.005)
        """
        error = self.absolute_error(measured)
        if self._value == 0:
            return 1.0 if error == 0 else 0.0
        return max(0.0, 1.0 - (error / self._value))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Accuracy definition

        Example:
            >>> data = accuracy.to_dict()
        """
        return {
            "value": self._value,
            "reference": self._reference,
            "metadata": self._metadata.copy(),
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(accuracy)
        """
        return f"Accuracy(value={self._value}, reference={self._reference})"


# Export
__all__ = [
    "Accuracy",
]
