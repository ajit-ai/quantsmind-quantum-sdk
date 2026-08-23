"""
Expectation Value Module

This module provides expectation value definitions for the Quantum package.

Purpose
-------
Provide expectation value management for quantum computing operations.

Responsibilities
----------------
- Define expectation value structure
- Support expectation value operations
- Support expectation value validation
- Support expectation value metadata

Dependencies
------------
typing (standard library)
quantsmind.quantum.algorithms.exceptions (quantum exceptions)
quantsmind.quantum.algorithms.types (quantum types)
quantsmind.quantum.operator.observable (observable module)
"""

from __future__ import annotations

from typing import Any

from quantsmind.quantum.algorithms.exceptions import MeasurementError
from quantsmind.quantum.algorithms.types import ValidationResult
from quantsmind.quantum.operator.observable import Observable


class ExpectationValue:
    """Concrete implementation of an expectation value.

    This class provides expectation value functionality for quantum computing.

    Attributes:
        _observable: Observable to measure
        _value: Expectation value
        _variance: Variance
        _shots: Number of shots
        _metadata: Expectation metadata

    Example:
        >>> exp_val = ExpectationValue(observable, 0.5)
    """

    def __init__(
        self,
        observable: Observable,
        value: float,
        variance: float = 0.0,
        shots: int = 0,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize an ExpectationValue.

        Args:
            observable: Observable to measure
            value: Expectation value
            variance: Variance
            shots: Number of shots
            metadata: Expectation metadata

        Example:
            >>> exp_val = ExpectationValue(observable, 0.5)
        """
        if observable is None:
            raise MeasurementError("Observable cannot be None", {"observable": None})

        self._observable = observable
        self._value = value
        self._variance = variance
        self._shots = shots
        self._metadata = metadata or {}

    @property
    def observable(self) -> Observable:
        """Get the observable.

        Returns:
            Observable

        Example:
            >>> obs = exp_val.observable
        """
        return self._observable

    @property
    def value(self) -> float:
        """Get the expectation value.

        Returns:
            Expectation value

        Example:
            >>> val = exp_val.value
        """
        return self._value

    @property
    def variance(self) -> float:
        """Get the variance.

        Returns:
            Variance

        Example:
            >>> var = exp_val.variance
        """
        return self._variance

    @property
    def shots(self) -> int:
        """Get the number of shots.

        Returns:
            Number of shots

        Example:
            >>> shots = exp_val.shots
        """
        return self._shots

    @property
    def metadata(self) -> dict[str, Any]:
        """Get the expectation metadata.

        Returns:
            Expectation metadata

        Example:
            >>> metadata = exp_val.metadata
        """
        return self._metadata.copy()

    def set_value(self, value: float) -> None:
        """Set the expectation value.

        Args:
            value: Expectation value

        Example:
            >>> exp_val.set_value(0.75)
        """
        self._value = value

    def set_variance(self, variance: float) -> None:
        """Set the variance.

        Args:
            variance: Variance

        Example:
            >>> exp_val.set_variance(0.1)
        """
        self._variance = variance

    def set_shots(self, shots: int) -> None:
        """Set the number of shots.

        Args:
            shots: Number of shots

        Example:
            >>> exp_val.set_shots(1024)
        """
        if shots < 0:
            raise MeasurementError("Shots cannot be negative", {"shots": shots})

        self._shots = shots

    def get_standard_deviation(self) -> float:
        """Get the standard deviation.

        Returns:
            Standard deviation

        Example:
            >>> std = exp_val.get_standard_deviation()
        """
        return self._variance ** 0.5

    def get_error(self) -> float:
        """Get the measurement error.

        Returns:
            Measurement error

        Example:
            >>> error = exp_val.get_error()
        """
        if self._shots > 0:
            return self.get_standard_deviation() / (self._shots ** 0.5)
        return 0.0

    def validate(self) -> ValidationResult:
        """Validate the expectation value.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = exp_val.validate()
        """
        errors = []

        if self._observable is None:
            errors.append("Observable cannot be None")

        if self._variance < 0:
            errors.append("Variance cannot be negative")

        if self._shots < 0:
            errors.append("Shots cannot be negative")

        return (len(errors) == 0, errors)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Expectation value definition

        Example:
            >>> data = exp_val.to_dict()
        """
        return {
            "observable": self._observable.name,
            "value": self._value,
            "variance": self._variance,
            "standard_deviation": self.get_standard_deviation(),
            "shots": self._shots,
            "error": self.get_error(),
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(exp_val)
        """
        return f"ExpectationValue(observable={self._observable.name}, value={self._value:.4f}, variance={self._variance:.4f})"


# Export
__all__ = [
    "ExpectationValue",
]
