"""Hybrid executor: real classical + real quantum legs, honest comparison.

QMQ-04 §10-§12: a hybrid run performs **both** computations.  The quantum
leg that cannot run (MicroQuantum absent or broken) is recorded as
``skipped``/``failed`` — never invented.  The comparison then picks the
deterministic winner; when only one leg executed, that leg wins by default
and the reason says so explicitly.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from quantsmind.quantum.core.objective import ObjectiveSense
from quantsmind.quantum.execution.classical import (
    ClassicalExecutionResult,
    ClassicalExecutor,
)
from quantsmind.quantum.execution.comparison import (
    ExecutionComparison,
    ExecutionComparisonEntry,
)
from quantsmind.quantum.execution.errors import (
    ClassicalExecutionError,
    ExecutionError,
    HybridExecutionError,
    MicroQuantumUnavailableError,
    QuantumExecutionError,
)
from quantsmind.quantum.execution.executor import Executor, ExecutorContext
from quantsmind.quantum.execution.quantum import (
    QuantumExecutionResult,
    QuantumExecutor,
)
from quantsmind.quantum.integration.microquantum import qaoa_available
from quantsmind.quantum.strategy.strategy import ComputationStrategy


@dataclass
class HybridExecutionResult:
    """Composite result of a hybrid execution.

    Args:
        classical: Classical leg result (or ``None`` when skipped/failed).
        quantum: Quantum leg result (or ``None`` when skipped/failed).
        comparison: Explicit comparison + deterministic selection.
        selected: Selected leg id (``"classical"`` / ``"quantum"``).
        selected_assignment: Assignment chosen by selection.
        metadata: Free-form metadata.
    """

    leg: str = "hybrid"
    executor: str = "hybrid"
    algorithm: str = "qaoa"
    classical: ClassicalExecutionResult | None = None
    quantum: QuantumExecutionResult | None = None
    comparison: ExecutionComparison | None = None
    selected: str | None = None
    selected_assignment: dict[str, int] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def assignment(self) -> dict[str, int]:
        """Selected assignment (existing ``build_solution`` compatibility)."""
        return self.selected_assignment

    @property
    def quantum_unavailable(self) -> bool:
        """True when the quantum leg produced no execution result."""
        return self.quantum is None

    @property
    def solver(self) -> str:
        """Selected leg's executor label (provenance compatibility)."""
        resolved = self._selected_result()
        return getattr(resolved, "solver", "") or getattr(resolved, "executor", "")

    @property
    def energy(self) -> float | None:
        """Selected leg's QUBO energy (provenance compatibility)."""
        resolved = self._selected_result()
        return getattr(resolved, "energy", None)

    @property
    def shots(self) -> int:
        """Selected leg's shot count."""
        resolved = self._selected_result()
        return int(getattr(resolved, "shots", 0))

    def _selected_result(self) -> Any | None:
        if self.selected == "quantum":
            return self.quantum
        if self.selected == "classical":
            return self.classical
        return None

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "leg": self.leg,
            "executor": self.executor,
            "algorithm": self.algorithm,
            "classical": self.classical.to_dict() if self.classical is not None else None,
            "quantum": self.quantum.to_dict() if self.quantum is not None else None,
            "comparison": self.comparison.to_dict() if self.comparison is not None else None,
            "selected": self.selected,
            "selected_assignment": {k: int(v) for k, v in self.selected_assignment.items()},
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> HybridExecutionResult:
        """Rebuild a result from :meth:`to_dict` output."""
        classical_data = data.get("classical")
        quantum_data = data.get("quantum")
        comparison_data = data.get("comparison")
        return cls(
            leg=str(data.get("leg", "hybrid")),
            executor=str(data.get("executor", "hybrid")),
            algorithm=str(data.get("algorithm", "qaoa")),
            classical=(
                ClassicalExecutionResult.from_dict(classical_data)
                if classical_data is not None
                else None
            ),
            quantum=(
                QuantumExecutionResult.from_dict(quantum_data) if quantum_data is not None else None
            ),
            comparison=(
                ExecutionComparison.from_dict(comparison_data)
                if comparison_data is not None
                else None
            ),
            selected=data.get("selected"),
            selected_assignment={
                str(k): int(v) for k, v in data.get("selected_assignment", {}).items()
            },
            metadata=dict(data.get("metadata", {})),
        )

    def __repr__(self) -> str:
        return (
            f"HybridExecutionResult(classical={self.classical is not None}, "
            f"quantum={self.quantum is not None}, selected={self.selected!r})"
        )


class HybridExecutor(Executor):
    """Runs the classical baseline and the QAOA leg, then selects a winner.

    Args:
        classical_executor: Optional :class:`ClassicalExecutor` override.
        quantum_executor: Optional :class:`QuantumExecutor` override.
    """

    name = "hybrid-executor"
    executor_id = "hybrid"
    strategies = (ComputationStrategy.HYBRID,)

    def __init__(
        self,
        *,
        classical_executor: ClassicalExecutor | None = None,
        quantum_executor: QuantumExecutor | None = None,
    ) -> None:
        self.classical_executor = classical_executor or ClassicalExecutor()
        self.quantum_executor = quantum_executor or QuantumExecutor()

    def is_available(self, capabilities: Any | None = None) -> bool:
        # The classical leg is always available, so a hybrid run can proceed
        # even without MicroQuantum (documented fallback in QMQ-04 §8).
        return True

    def execute(self, context: ExecutorContext) -> HybridExecutionResult:
        problem = context.problem
        sense = problem.objectives[0].sense if problem.objectives else ObjectiveSense.MINIMIZE

        classical: ClassicalExecutionResult | None = None
        quantum: QuantumExecutionResult | None = None
        classical_message = ""
        quantum_message = ""
        classical_metadata: dict[str, Any] = {}
        quantum_metadata: dict[str, Any] = {}

        run_classical = (
            True
            if context.options.run_classical_baseline is None
            else context.options.run_classical_baseline
        )
        if run_classical:
            try:
                classical = self.classical_executor.execute(context)
                classical = self.classical_executor.validate(classical, context)
            except ClassicalExecutionError as exc:
                classical_message = str(exc)
            except ExecutionError as exc:
                classical_message = str(exc)
        elif not run_classical:
            classical_message = "classical baseline disabled via run_classical_baseline=False"

        if qaoa_available():
            try:
                raw_quantum = self.quantum_executor.execute(context)
                quantum = self.quantum_executor.validate(raw_quantum, context)
            except MicroQuantumUnavailableError as exc:
                quantum_message = str(exc)
            except QuantumExecutionError as exc:
                quantum_message = str(exc)
            except ExecutionError as exc:
                quantum_message = str(exc)
        else:
            quantum_message = (
                "quantum leg skipped: the optional 'microquantum' dependency is "
                "not available; qaoa_available() returned False (documented "
                "hybrid fallback, never faked)"
            )

        entries: list[ExecutionComparisonEntry] = []
        if classical is not None:
            entries.append(
                ExecutionComparisonEntry.from_execution(leg="classical", execution=classical)
            )
        elif classical_message:
            entries.append(
                ExecutionComparisonEntry.from_execution(
                    leg="classical",
                    execution=None,
                    status="failed",
                    message=classical_message,
                    metadata=classical_metadata,
                )
            )
        if quantum is not None:
            entries.append(
                ExecutionComparisonEntry.from_execution(leg="quantum", execution=quantum)
            )
        elif quantum_message:
            entries.append(
                ExecutionComparisonEntry.from_execution(
                    leg="quantum",
                    execution=None,
                    status="skipped",
                    message=quantum_message,
                    metadata=quantum_metadata,
                )
            )

        if classical is None and quantum is None:
            reason = (
                f"classical: {classical_message}"
                if classical_message
                else ("classical: unavailable")
            )
            reason += "; quantum: "
            reason += quantum_message if quantum_message else "unavailable"
            raise HybridExecutionError(f"hybrid execution produced no executable leg ({reason})")

        comparison = ExecutionComparison.build(entries, sense=sense)
        selected = comparison.winner
        selected_result = quantum if selected == "quantum" else classical
        assert selected is not None
        assert selected_result is not None
        return HybridExecutionResult(
            classical=classical,
            quantum=quantum,
            comparison=comparison,
            selected=selected,
            selected_assignment=dict(getattr(selected_result, "assignment", {})),
            algorithm=("qaoa" if selected == "quantum" and quantum is not None else "exhaustive"),
            executor="hybrid",
            metadata={
                "quantum_leg": ("executed" if quantum is not None else "skipped"),
                "classical_leg": ("executed" if classical is not None else "failed"),
                "fallback_used": quantum is None,
            },
        )


__all__ = ["HybridExecutor", "HybridExecutionResult"]
