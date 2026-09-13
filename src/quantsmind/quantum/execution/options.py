"""Controlled execution configuration (QMQ-04 §14).

:class:`ExecutionOptions` is the single, traceable configuration object an
execution consumes.  Quantum-specific options (shots, seed, backend, layers,
optimizer) are delegated straight to MicroQuantum's public QAOA API; there is
no second complete execution-configuration model here.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from quantsmind.quantum.strategy.strategy import ComputationStrategy


@dataclass(frozen=True)
class ExecutionOptions:
    """Controlled execution configuration for one workflow run.

    Args:
        strategy: Strategy to execute.  ``None`` defers to the
            :class:`ComputationPlan` (QMQ-03 decision).
        algorithm: Optional algorithm override (echoed into metadata; the
            plan's recommended algorithm drives execution unless
            ``requested_algorithm`` is set on the workflow).
        shots: Shot count for the quantum leg.
        seed: Optional RNG seed for reproducible quantum sampling.
        backend: Backend name (e.g. ``"statevector"``) or instance.
        num_layers: QAOA layers (``p``) for the quantum leg.
        penalty: Optional QUBO constraint penalty multiplier.
        qaoa_optimizer: Optional MicroQuantum optimizer for the QAOA
            variational loop (delegated unchanged).
        optimization_level: 0..3 optimization hint; recorded in metadata
            (the QAOA path does not consume it).
        run_classical_baseline: For HYBRID, whether to run the classical
            baseline.  ``None`` means automatic (always run).
        allow_fallback: Whether an unavailable requested algorithm may fall
            back to an executable replacement (never silent).
        metadata: Free-form execution metadata.
    """

    strategy: ComputationStrategy | str | None = None
    algorithm: str | None = None
    shots: int = 1024
    seed: int | None = None
    backend: str | None = None
    num_layers: int = 1
    penalty: float | None = None
    qaoa_optimizer: Any | None = None
    optimization_level: int = 0
    run_classical_baseline: bool | None = None
    allow_fallback: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def resolved_strategy(self) -> ComputationStrategy | None:
        """Strategy parsed to a :class:`ComputationStrategy` (or ``None``)."""
        if self.strategy is None:
            return None
        return (
            self.strategy
            if isinstance(self.strategy, ComputationStrategy)
            else ComputationStrategy.parse(self.strategy)
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "strategy": (
                self.strategy.name.lower()
                if isinstance(self.strategy, ComputationStrategy)
                else self.strategy
            ),
            "algorithm": self.algorithm,
            "shots": self.shots,
            "seed": self.seed,
            "backend": self.backend,
            "num_layers": self.num_layers,
            "penalty": self.penalty,
            "optimization_level": self.optimization_level,
            "run_classical_baseline": self.run_classical_baseline,
            "allow_fallback": self.allow_fallback,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ExecutionOptions:
        """Rebuild options from :meth:`to_dict` output."""
        strategy = data.get("strategy")
        parsed: ComputationStrategy | str | None = None
        if strategy is not None:
            parsed = ComputationStrategy.parse(strategy)
        return cls(
            strategy=parsed,
            algorithm=data.get("algorithm"),
            shots=int(data.get("shots", 1024)),
            seed=(int(data["seed"]) if data.get("seed") is not None else None),
            backend=data.get("backend"),
            num_layers=int(data.get("num_layers", 1)),
            penalty=(float(data["penalty"]) if data.get("penalty") is not None else None),
            optimization_level=int(data.get("optimization_level", 0)),
            run_classical_baseline=(
                bool(data["run_classical_baseline"])
                if data.get("run_classical_baseline") is not None
                else None
            ),
            allow_fallback=bool(data.get("allow_fallback", False)),
            metadata=dict(data.get("metadata", {})),
        )


__all__ = ["ExecutionOptions"]
