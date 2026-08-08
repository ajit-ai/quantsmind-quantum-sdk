"""
Quantum / Hamiltonian
=====================

Purpose: A contract describing the energy operator governing time evolution.

Architecture-only (R0.1.0): interface definition only, no quantum
algorithms, simulators, or gate decompositions implemented.

Dependencies (conceptual): quantsmind.foundation, quantsmind.math,
quantsmind.runtime, quantsmind.providers, quantsmind.compiler
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Hamiltonian(ABC):
    """Abstract contract for hamiltonian within the QuantsMind quantum domain."""

    @abstractmethod
    def describe(self) -> dict[str, Any]:
        """Return a structured description of this hamiltonian."""
        raise NotImplementedError
