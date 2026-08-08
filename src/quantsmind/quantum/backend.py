"""
Quantum / Backend
=================

Purpose: Quantum-specific specialization of quantsmind.providers.Backend.

Architecture-only (R0.1.0): interface definition only, no quantum
algorithms, simulators, or gate decompositions implemented.

Dependencies (conceptual): quantsmind.foundation, quantsmind.math,
quantsmind.runtime, quantsmind.providers, quantsmind.compiler
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Backend(ABC):
    """Abstract contract for backend within the QuantsMind quantum domain."""

    @abstractmethod
    def describe(self) -> dict[str, Any]:
        """Return a structured description of this backend."""
        raise NotImplementedError
