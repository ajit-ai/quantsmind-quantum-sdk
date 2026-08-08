"""
Quantum Result Module

This module provides quantum result definitions for the Quantum package.

Purpose
-------
Provide quantum result management for quantum computing operations.

Responsibilities
----------------
- Define quantum result structure
- Support quantum result operations
- Support quantum result validation
- Support quantum result metadata

Dependencies
------------
typing (standard library)
quantsmind.quantum.algorithms.exceptions (quantum exceptions)
quantsmind.quantum.algorithms.types (quantum types)
quantsmind.quantum.execution.execution_context (execution context module)
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from quantsmind.quantum.algorithms.exceptions import ExecutionError
from quantsmind.quantum.algorithms.types import ValidationResult
from quantsmind.quantum.execution.execution_context import ExecutionContext


class QuantumResult:
    """Concrete implementation of a quantum result.

    This class provides quantum result functionality for quantum computing.

    Attributes:
        _job_id: Job ID
        _context: Execution context
        _counts: Measurement counts
        _state: Final state
        _metadata: Result metadata

    Example:
        >>> result = QuantumResult("job_001", context, {"00": 512, "11": 512})
    """

    def __init__(
        self,
        job_id: str,
        context: ExecutionContext,
        counts: Dict[str, int],
        state: Optional[Any] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a QuantumResult.

        Args:
            job_id: Job ID
            context: Execution context
            counts: Measurement counts
            state: Final state
            metadata: Result metadata

        Example:
            >>> result = QuantumResult("job_001", context, {"00": 512, "11": 512})
        """
        if not job_id:
            raise ExecutionError("Job ID cannot be empty", {"job_id": job_id})

        if context is None:
            raise ExecutionError("Context cannot be None", {"context": None})

        if not counts:
            raise ExecutionError("Counts cannot be empty", {"counts": counts})

        self._job_id = job_id
        self._context = context
        self._counts = counts
        self._state = state
        self._metadata = metadata or {}

    @property
    def job_id(self) -> str:
        """Get the job ID.

        Returns:
            Job ID

        Example:
            >>> jid = result.job_id
        """
        return self._job_id

    @property
    def context(self) -> ExecutionContext:
        """Get the execution context.

        Returns:
            Execution context

        Example:
            >>> context = result.context
        """
        return self._context

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
    def state(self) -> Optional[Any]:
        """Get the final state.

        Returns:
            Final state

        Example:
            >>> state = result.state
        """
        return self._state

    @property
    def metadata(self) -> Dict[str, Any]:
        """Get the result metadata.

        Returns:
            Result metadata

        Example:
            >>> metadata = result.metadata
        """
        return self._metadata.copy()

    def get_shots(self) -> int:
        """Get the total number of shots.

        Returns:
            Total shots

        Example:
            >>> shots = result.get_shots()
        """
        return sum(self._counts.values())

    def get_probabilities(self) -> Dict[str, float]:
        """Get the measurement probabilities.

        Returns:
            Measurement probabilities

        Example:
            >>> probs = result.get_probabilities()
        """
        total = self.get_shots()
        if total == 0:
            return {}
        return {outcome: count / total for outcome, count in self._counts.items()}

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

    def get_outcome(self, outcome: str) -> int:
        """Get the count for a specific outcome.

        Args:
            outcome: Measurement outcome

        Returns:
            Count

        Example:
            >>> count = result.get_outcome("00")
        """
        return self._counts.get(outcome, 0)

    def validate(self) -> ValidationResult:
        """Validate the result.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = result.validate()
        """
        errors = []

        if not self._job_id:
            errors.append("Job ID cannot be empty")

        if self._context is None:
            errors.append("Context cannot be None")

        if not self._counts:
            errors.append("Counts cannot be empty")

        # Validate counts are non-negative
        for outcome, count in self._counts.items():
            if count < 0:
                errors.append(f"Count for outcome {outcome} is negative: {count}")

        return (len(errors) == 0, errors)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Result definition

        Example:
            >>> data = result.to_dict()
        """
        return {
            "job_id": self._job_id,
            "context": self._context.name,
            "shots": self.get_shots(),
            "counts": self._counts,
            "probabilities": self.get_probabilities(),
            "most_frequent": self.get_most_frequent(),
            "has_state": self._state is not None,
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(result)
        """
        return f"QuantumResult(job_id={self._job_id}, shots={self.get_shots()}, outcomes={len(self._counts)})"
