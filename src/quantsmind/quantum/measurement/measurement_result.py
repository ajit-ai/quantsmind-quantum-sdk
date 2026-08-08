"""
Measurement Result Module

This module provides measurement result definitions for the Quantum package.

Purpose
-------
Provide measurement result management for quantum computing operations.

Responsibilities
----------------
- Define measurement result structure
- Support measurement result operations
- Support measurement result validation
- Support measurement result metadata

Dependencies
------------
typing (standard library)
quantsmind.quantum.algorithms.exceptions (quantum exceptions)
quantsmind.quantum.algorithms.types (quantum types)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from quantsmind.quantum.algorithms.exceptions import MeasurementError
from quantsmind.quantum.algorithms.types import ValidationResult


class MeasurementResult:
    """Concrete implementation of a measurement result.

    This class provides measurement result functionality for quantum computing.

    Attributes:
        _shots: Number of shots
        _counts: Measurement counts
        _probabilities: Measurement probabilities
        _metadata: Result metadata

    Example:
        >>> result = MeasurementResult(1024)
        >>> result.add_count("00", 512)
    """

    def __init__(
        self,
        shots: int,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a MeasurementResult.

        Args:
            shots: Number of shots
            metadata: Result metadata

        Example:
            >>> result = MeasurementResult(1024)
        """
        if shots <= 0:
            raise MeasurementError("Number of shots must be positive", {"shots": shots})

        self._shots = shots
        self._counts: Dict[str, int] = {}
        self._probabilities: Dict[str, float] = {}
        self._metadata = metadata or {}

    @property
    def shots(self) -> int:
        """Get the number of shots.

        Returns:
            Number of shots

        Example:
            >>> shots = result.shots
        """
        return self._shots

    @property
    def counts(self) -> Dict[str, int]:
        """Get the measurement counts.

        Returns:
            Measurement counts

        Example:
            >>> counts = result.counts
        """
        return self._counts.copy()

    @property
    def probabilities(self) -> Dict[str, float]:
        """Get the measurement probabilities.

        Returns:
            Measurement probabilities

        Example:
            >>> probs = result.probabilities
        """
        return self._probabilities.copy()

    @property
    def metadata(self) -> Dict[str, Any]:
        """Get the result metadata.

        Returns:
            Result metadata

        Example:
            >>> metadata = result.metadata
        """
        return self._metadata.copy()

    def add_count(self, outcome: str, count: int) -> None:
        """Add a measurement count.

        Args:
            outcome: Measurement outcome
            count: Count

        Example:
            >>> result.add_count("00", 512)
        """
        if count < 0:
            raise MeasurementError("Count cannot be negative", {"count": count})

        self._counts[outcome] = count
        self._probabilities[outcome] = count / self._shots

    def get_count(self, outcome: str) -> int:
        """Get the count for a specific outcome.

        Args:
            outcome: Measurement outcome

        Returns:
            Count

        Example:
            >>> count = result.get_count("00")
        """
        return self._counts.get(outcome, 0)

    def get_probability(self, outcome: str) -> float:
        """Get the probability for a specific outcome.

        Args:
            outcome: Measurement outcome

        Returns:
            Probability

        Example:
            >>> prob = result.get_probability("00")
        """
        return self._probabilities.get(outcome, 0.0)

    def get_most_frequent(self) -> str:
        """Get the most frequent outcome.

        Returns:
            Most frequent outcome

        Example:
            >>> outcome = result.get_most_frequent()
        """
        if not self._counts:
            return ""

        return max(self._counts, key=self._counts.get)

    def get_outcomes(self) -> List[str]:
        """Get all possible outcomes.

        Returns:
            List of outcomes

        Example:
            >>> outcomes = result.get_outcomes()
        """
        return list(self._counts.keys())

    def validate(self) -> ValidationResult:
        """Validate the measurement result.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = result.validate()
        """
        errors = []

        if self._shots <= 0:
            errors.append("Number of shots must be positive")

        total_count = sum(self._counts.values())
        if total_count > self._shots:
            errors.append(f"Total count {total_count} exceeds shots {self._shots}")

        # Check probabilities sum to 1
        total_prob = sum(self._probabilities.values())
        if abs(total_prob - 1.0) > 1e-6 and self._probabilities:
            errors.append(f"Probabilities sum to {total_prob}, expected 1.0")

        return (len(errors) == 0, errors)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Measurement result definition

        Example:
            >>> data = result.to_dict()
        """
        return {
            "shots": self._shots,
            "counts": self._counts,
            "probabilities": self._probabilities,
            "outcome_count": len(self._counts),
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(result)
        """
        return f"MeasurementResult(shots={self._shots}, outcomes={len(self._counts)})"
