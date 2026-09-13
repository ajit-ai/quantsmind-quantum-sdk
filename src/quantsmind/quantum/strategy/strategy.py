"""Computation strategies for QuantsMind Quantum.

The strategy enumerates how a domain problem should be computed.
QMQ-01 ships a deterministic, rule-based :class:`StrategySelector`.
A future learned or advice-based selector can replace the ``select``
implementation without callers changing.
"""

from __future__ import annotations

from enum import Enum
from typing import Any


class ComputationStrategy(Enum):
    """How a domain problem should be computed.

    Attributes:
        CLASSICAL: Classical computation on CPUs/GPUs.
        QUANTUM: End-to-end quantum computation (MicroQuantum runtime).
        HYBRID: Classical domain pre/post-processing with a quantum kernel.
        QUANTUM_INSPIRED: Classical algorithms inspired by quantum mechanics.
        AUTO: Deterministic rule-based selection (see :class:`StrategySelector`).
    """

    CLASSICAL = "classical"
    QUANTUM = "quantum"
    HYBRID = "hybrid"
    QUANTUM_INSPIRED = "quantum_inspired"
    AUTO = "auto"

    @classmethod
    def parse(cls, value: Any) -> ComputationStrategy:
        """Coerce a name or member to a :class:`ComputationStrategy`."""
        if isinstance(value, cls):
            return value
        text = str(value).strip().lower().replace("-", "_").replace(" ", "_")
        for member in cls:
            if member.name.lower() == text or member.value == text:
                return member
        names = ", ".join(m.name for m in cls)
        raise ValueError(f"unknown computation strategy {value!r}; expected one of: {names}")

    @property
    def uses_quantum_runtime(self) -> bool:
        """True for strategies that require MicroQuantum execution."""
        return self in {ComputationStrategy.QUANTUM, ComputationStrategy.HYBRID}


__all__ = ["ComputationStrategy"]
