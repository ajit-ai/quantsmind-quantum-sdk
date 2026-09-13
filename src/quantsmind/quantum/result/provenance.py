"""Provenance recording for quantum domain solutions.

A :class:`Provenance` records how a domain result was produced: the
strategy, formulation, algorithm, backend, execution metadata and the SDK
version.  It makes results auditable and reproducible without coupling to
any specific execution engine.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from importlib.metadata import PackageNotFoundError, version
from typing import Any

from quantsmind.quantum.strategy.strategy import ComputationStrategy


def _sdk_version() -> str:
    """Return the installed quantsmind SDK version (or ``"unknown"``)."""
    try:
        return version("quantsmind")
    except PackageNotFoundError:
        return "unknown"


@dataclass
class Provenance:
    """Where-and-how metadata attached to a domain result.

    Args:
        strategy: Computation strategy used.
        formulation: Formulation kind (e.g. ``"optimization"``).
        algorithm: Algorithm used (e.g. ``"vqe"``, ``"grover"``,
            ``"qaoa"``, ``"exhaustive"``) or ``""``.
        executor: Executor identity (e.g. ``"classical/exhaustive"``,
            ``"microquantum/qaoa"``) or ``""``.
        backend: Backend that executed the workflow or ``""``.
        execution_metadata: Metadata from the execution layer (experiment id,
            actual backend, shots, counts-derived summary).
        sdk_version: QuantsMind SDK version that produced the result.
        created_at: UTC ISO timestamp of record creation.
        metadata: Free-form provenance metadata.
    """

    strategy: ComputationStrategy | str | None = None
    formulation: str = ""
    algorithm: str = ""
    executor: str = ""
    backend: str = ""
    execution_metadata: dict[str, Any] = field(default_factory=dict)
    sdk_version: str = field(default_factory=_sdk_version)
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_execution(
        cls,
        *,
        strategy: ComputationStrategy | str | None = None,
        formulation: str = "",
        algorithm: str = "",
        executor: str = "",
        backend: str = "",
        execution: Any | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Provenance:
        """Build provenance, deriving execution metadata from a result.

        ``execution`` may be any object exposing ``experiment_id``,
        ``program_name``, ``backend_name``, ``shots`` and ``provenance``
        attributes (e.g. a
        :class:`~quantsmind.quantum.circuit_result.QuantumResult`), or a
        QMQ-02 executor result exposing ``solver``/``energy`` (e.g.
        :class:`~quantsmind.quantum.optimization.classical.ClassicalSolverResult`
        or
        :class:`~quantsmind.quantum.integration.microquantum.QaoaExecutionResult`).
        """
        execution_metadata: dict[str, Any] = {}
        if execution is not None:
            execution_metadata = {
                "experiment_id": getattr(execution, "experiment_id", ""),
                "program_name": getattr(execution, "program_name", ""),
                "actual_backend": getattr(execution, "backend_name", "")
                or getattr(execution, "backend", ""),
                "shots": getattr(execution, "shots", 0),
                "executor": getattr(execution, "solver", ""),
                "algorithm": getattr(execution, "algorithm", "")
                or getattr(execution, "solver", ""),
                "energy": getattr(execution, "energy", None),
                "provenance": dict(getattr(execution, "provenance", {})),
            }
        return cls(
            strategy=(strategy.name if isinstance(strategy, ComputationStrategy) else strategy),
            formulation=formulation,
            algorithm=algorithm,
            executor=executor or execution_metadata.get("executor", ""),
            backend=backend or execution_metadata.get("actual_backend", ""),
            execution_metadata=execution_metadata,
            metadata=dict(metadata or {}),
        )

    @property
    def strategy_label(self) -> str | None:
        """Serialized strategy label (e.g. ``"hybrid"``)."""
        if self.strategy is None:
            return None
        label = (
            self.strategy.name.lower()
            if isinstance(self.strategy, ComputationStrategy)
            else str(self.strategy).lower()
        )
        return label

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "strategy": self.strategy_label,
            "formulation": self.formulation,
            "algorithm": self.algorithm,
            "executor": self.executor,
            "backend": self.backend,
            "execution_metadata": dict(self.execution_metadata),
            "sdk_version": self.sdk_version,
            "created_at": self.created_at,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Provenance:
        """Rebuild a Provenance from :meth:`to_dict` output."""
        strategy = data.get("strategy")
        parsed: ComputationStrategy | str | None = None
        if strategy is not None:
            parsed = ComputationStrategy.parse(strategy)
        return cls(
            strategy=parsed,
            formulation=str(data.get("formulation", "")),
            algorithm=str(data.get("algorithm", "")),
            executor=str(data.get("executor", "")),
            backend=str(data.get("backend", "")),
            execution_metadata=dict(data.get("execution_metadata", {})),
            sdk_version=str(data.get("sdk_version", _sdk_version())),
            created_at=str(data.get("created_at", datetime.now(UTC).isoformat())),
            metadata=dict(data.get("metadata", {})),
        )

    def __repr__(self) -> str:
        return (
            f"Provenance(strategy={self.strategy_label}, formulation={self.formulation!r}, "
            f"executor={self.executor!r}, backend={self.backend!r})"
        )


__all__ = ["Provenance"]
