"""
Decoherence Module

This module provides decoherence definitions for the Quantum package.

Purpose
-------
Provide decoherence management for quantum computing operations.

Responsibilities
----------------
- Define decoherence structure
- Support decoherence operations
- Support decoherence validation
- Support decoherence metadata

Dependencies
------------
typing (standard library)
quantsmind.quantum.algorithms.exceptions (quantum exceptions)
quantsmind.quantum.algorithms.types (quantum types)
quantsmind.quantum.noise.noise_model (noise model module)
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from quantsmind.quantum.algorithms.exceptions import NoiseError
from quantsmind.quantum.algorithms.types import ValidationResult
from quantsmind.quantum.noise.noise_model import NoiseModel


class Decoherence(NoiseModel):
    """Concrete implementation of a decoherence model.

    This class provides decoherence functionality for quantum computing.
    Decoherence models the loss of quantum coherence over time.

    Attributes:
        _name: Decoherence model name
        _t1: T1 relaxation time
        _t2: T2 dephasing time
        _metadata: Decoherence metadata

    Example:
        >>> decoherence = Decoherence("amplitude_damping", t1=100e-6, t2=50e-6)
    """

    def __init__(
        self,
        name: str,
        t1: float = 100e-6,
        t2: float = 50e-6,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a Decoherence.

        Args:
            name: Decoherence model name
            t1: T1 relaxation time (seconds)
            t2: T2 dephasing time (seconds)
            metadata: Decoherence metadata

        Example:
            >>> decoherence = Decoherence("amplitude_damping", t1=100e-6, t2=50e-6)
        """
        super().__init__(name, "decoherence", metadata=metadata)
        self._t1 = t1
        self._t2 = t2

    @property
    def t1(self) -> float:
        """Get the T1 relaxation time.

        Returns:
            T1 time

        Example:
            >>> t1 = decoherence.t1
        """
        return self._t1

    @property
    def t2(self) -> float:
        """Get the T2 dephasing time.

        Returns:
            T2 time

        Example:
            >>> t2 = decoherence.t2
        """
        return self._t2

    def set_t1(self, t1: float) -> None:
        """Set the T1 relaxation time.

        Args:
            t1: T1 time

        Example:
            >>> decoherence.set_t1(100e-6)
        """
        if t1 <= 0:
            raise NoiseError("T1 must be positive", {"t1": t1})

        self._t1 = t1

    def set_t2(self, t2: float) -> None:
        """Set the T2 dephasing time.

        Args:
            t2: T2 time

        Example:
            >>> decoherence.set_t2(50e-6)
        """
        if t2 <= 0:
            raise NoiseError("T2 must be positive", {"t2": t2})

        self._t2 = t2

    def get_relaxation_rate(self) -> float:
        """Get the relaxation rate (1/T1).

        Returns:
            Relaxation rate

        Example:
            >>> rate = decoherence.get_relaxation_rate()
        """
        return 1.0 / self._t1 if self._t1 > 0 else 0.0

    def get_dephasing_rate(self) -> float:
        """Get the dephasing rate (1/T2).

        Returns:
            Dephasing rate

        Example:
            >>> rate = decoherence.get_dephasing_rate()
        """
        return 1.0 / self._t2 if self._t2 > 0 else 0.0

    def validate(self) -> ValidationResult:
        """Validate the decoherence model.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = decoherence.validate()
        """
        errors = []

        # Validate base noise model
        is_valid, base_errors = super().validate()
        errors.extend(base_errors)

        if self._t1 <= 0:
            errors.append("T1 must be positive")

        if self._t2 <= 0:
            errors.append("T2 must be positive")

        if self._t2 > 2 * self._t1:
            errors.append("T2 cannot exceed 2*T1 (physical constraint)")

        return (len(errors) == 0, errors)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Decoherence definition

        Example:
            >>> data = decoherence.to_dict()
        """
        data = super().to_dict()
        data["t1"] = self._t1
        data["t2"] = self._t2
        data["relaxation_rate"] = self.get_relaxation_rate()
        data["dephasing_rate"] = self.get_dephasing_rate()
        return data

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(decoherence)
        """
        return f"Decoherence(name={self._name}, t1={self._t1:.2e}, t2={self._t2:.2e})"


# Export
__all__ = [
    "Decoherence",
]
