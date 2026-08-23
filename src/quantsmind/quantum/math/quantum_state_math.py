"""
Quantum State Math Module

This module provides quantum state mathematics for the QuantsMind SDK.

Purpose
-------
Provide mathematical operations on quantum states, integrating with classical mathematics.

Classes
-------
QuantumStateMath: Quantum state mathematical operations

Responsibilities
----------------
- Convert quantum states to classical vectors
- Perform state operations
- Compute state overlaps
- Support state normalization

Dependencies
------------
typing (standard library)
quantsmind.algebra.linear_algebra (Vector)
"""

from __future__ import annotations

import math
from typing import Any

from quantsmind.algebra.linear_algebra import Vector


class QuantumStateMath:
    """Quantum state mathematical operations.

    This class provides functionality for mathematical operations on quantum states,
    bridging quantum computing with classical linear algebra.

    Attributes:
        _name: State name
        _amplitudes: State amplitudes (complex numbers)
        _metadata: Additional metadata

    Example:
        >>> qsm = QuantumStateMath("bell", [1/math.sqrt(2), 0, 0, 1/math.sqrt(2)])
        >>> classical = qsm.to_classical_vector()
    """

    def __init__(
        self,
        name: str,
        amplitudes: list[complex],
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a QuantumStateMath.

        Args:
            name: State name
            amplitudes: State amplitudes (complex numbers)
            metadata: Additional metadata

        Example:
            >>> qsm = QuantumStateMath("bell", [1/math.sqrt(2), 0, 0, 1/math.sqrt(2)])
        """
        self._name = name
        self._amplitudes = amplitudes
        self._metadata = metadata or {}

    @property
    def name(self) -> str:
        """Get the state name.

        Returns:
            State name

        Example:
            >>> name = qsm.name
        """
        return self._name

    @property
    def amplitudes(self) -> list[complex]:
        """Get the state amplitudes.

        Returns:
            State amplitudes

        Example:
            >>> amps = qsm.amplitudes
        """
        return self._amplitudes.copy()

    @property
    def dimension(self) -> int:
        """Get the state dimension.

        Returns:
            State dimension

        Example:
            >>> dim = qsm.dimension
        """
        return len(self._amplitudes)

    def to_classical_vector(self) -> Vector:
        """Convert to classical vector (real part only).

        Returns:
            Classical vector

        Example:
            >>> classical = qsm.to_classical_vector()
        """
        real_data = [complex(amp).real for amp in self._amplitudes]
        return Vector(f"{self._name}_classical", real_data)

    def normalize(self) -> QuantumStateMath:
        """Normalize the state.

        Returns:
            Normalized state

        Example:
            >>> normalized = qsm.normalize()
        """
        norm = math.sqrt(sum(abs(amp) ** 2 for amp in self._amplitudes))
        if norm == 0:
            raise ValueError("Cannot normalize zero state")

        normalized_amplitudes = [amp / norm for amp in self._amplitudes]
        return QuantumStateMath(f"{self._name}_normalized", normalized_amplitudes)

    def is_normalized(self, tolerance: float = 1e-10) -> bool:
        """Check if the state is normalized.

        Args:
            tolerance: Numerical tolerance

        Returns:
            True if normalized

        Example:
            >>> is_norm = qsm.is_normalized()
        """
        norm_squared = sum(abs(amp) ** 2 for amp in self._amplitudes)
        return abs(norm_squared - 1.0) < tolerance

    def inner_product(self, other: QuantumStateMath) -> complex:
        """Compute inner product with another state.

        Args:
            other: Other state

        Returns:
            Inner product

        Example:
            >>> overlap = qsm.inner_product(other)
        """
        if self.dimension != other.dimension:
            raise ValueError("States must have same dimension")

        return sum(self._amplitudes[i].conjugate() * other.amplitudes[i] for i in range(self.dimension))

    def overlap(self, other: QuantumStateMath) -> float:
        """Compute overlap (absolute value of inner product).

        Args:
            other: Other state

        Returns:
            Overlap value

        Example:
            >>> overlap = qsm.overlap(other)
        """
        return abs(self.inner_product(other))

    def fidelity(self, other: QuantumStateMath) -> float:
        """Compute fidelity with another state.

        Args:
            other: Other state

        Returns:
            Fidelity value

        Example:
            >>> fidelity = qsm.fidelity(other)
        """
        overlap = self.inner_product(other)
        return abs(overlap) ** 2

    def tensor_product(self, other: QuantumStateMath) -> QuantumStateMath:
        """Compute tensor product with another state.

        Args:
            other: Other state

        Returns:
            Tensor product state

        Example:
            >>> product = qsm.tensor_product(other)
        """
        product_amplitudes = []
        for amp1 in self._amplitudes:
            for amp2 in other.amplitudes:
                product_amplitudes.append(amp1 * amp2)

        return QuantumStateMath(f"{self._name}_tensor_{other._name}", product_amplitudes)

    def density_matrix(self) -> list[list[complex]]:
        """Compute the density matrix.

        Returns:
            Density matrix

        Example:
            >>> rho = qsm.density_matrix()
        """
        rho = [[0j] * self.dimension for _ in range(self.dimension)]
        for i in range(self.dimension):
            for j in range(self.dimension):
                rho[i][j] = self._amplitudes[i] * self._amplitudes[j].conjugate()
        return rho

    def expectation_value(self, observable: list[list[complex]]) -> complex:
        """Compute expectation value of an observable.

        Args:
            observable: Observable matrix

        Returns:
            Expectation value

        Example:
            >>> exp_val = qsm.expectation_value(observable)
        """
        if len(observable) != self.dimension or len(observable[0]) != self.dimension:
            raise ValueError("Observable must have same dimension as state")

        # Compute ⟨ψ|O|ψ⟩
        result = 0j
        for i in range(self.dimension):
            for j in range(self.dimension):
                result += self._amplitudes[i].conjugate() * observable[i][j] * self._amplitudes[j]

        return result

    def partial_trace(self, subsystem_dimensions: list[int], trace_over: list[int]) -> QuantumStateMath:
        """Compute partial trace over specified subsystems.

        Args:
            subsystem_dimensions: Dimensions of subsystems
            trace_over: Subsystems to trace over

        Returns:
            Reduced density matrix state

        Example:
            >>> reduced = qsm.partial_trace([2, 2], [1])
        """
        # Placeholder - real implementation would compute partial trace
        return self

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(qsm)
        """
        return f"QuantumStateMath(name={self._name}, dimension={self.dimension})"


__all__ = [
    "QuantumStateMath",
]
