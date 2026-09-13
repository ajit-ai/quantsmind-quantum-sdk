"""Classical/quantum comparison for hybrid execution (QMQ-04 §10/§11).

:class:`ExecutionComparison` is the explicit comparison artifact of a
hybrid run: one entry per executed/skipped/failed leg plus a deterministic
winner and the reasons that produced it.  No advantage, speedup or
superiority claim is ever fabricated here — only the recorded objective
value, energy, feasibility and status of each leg are compared.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from quantsmind.quantum.core.objective import ObjectiveSense

if TYPE_CHECKING:
    from quantsmind.quantum.execution.classical import ClassicalExecutionResult
    from quantsmind.quantum.execution.quantum import QuantumExecutionResult

_LEG_PRIORITY = {"classical": 2, "quantum": 1}

_EXECUTED = "executed"
_SKIPPED = "skipped"
_FAILED = "failed"


@dataclass
class ExecutionComparisonEntry:
    """One leg of a hybrid execution, ready for comparison.

    Args:
        leg: ``"classical"`` or ``"quantum"``.
        algorithm: Algorithm id that produced the result.
        executor: Executor label (e.g. ``"classical/exhaustive"``).
        status: ``"executed"`` / ``"skipped"`` / ``"failed"``.
        objective_value: Domain objective value of the returned assignment.
        energy: QUBO energy of the returned assignment (minimization form).
        feasible: Whether the assignment satisfies the domain constraints.
        message: Free-form note (skip/failure reason, ...).
        metadata: Free-form metadata.
    """

    leg: str
    algorithm: str = ""
    executor: str = ""
    status: str = _EXECUTED
    objective_value: float | None = None
    energy: float | None = None
    feasible: bool | None = None
    message: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "leg": self.leg,
            "algorithm": self.algorithm,
            "executor": self.executor,
            "status": self.status,
            "objective_value": self.objective_value,
            "energy": self.energy,
            "feasible": self.feasible,
            "message": self.message,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ExecutionComparisonEntry:
        """Rebuild an entry from :meth:`to_dict` output."""
        return cls(
            leg=str(data.get("leg", "")),
            algorithm=str(data.get("algorithm", "")),
            executor=str(data.get("executor", "")),
            status=str(data.get("status", _EXECUTED)),
            objective_value=(
                float(data["objective_value"]) if data.get("objective_value") is not None else None
            ),
            energy=(float(data["energy"]) if data.get("energy") is not None else None),
            feasible=(bool(data["feasible"]) if data.get("feasible") is not None else None),
            message=str(data.get("message", "")),
            metadata=dict(data.get("metadata", {})),
        )

    @classmethod
    def from_execution(
        cls,
        *,
        leg: str,
        execution: ClassicalExecutionResult | QuantumExecutionResult | None,
        status: str = _EXECUTED,
        message: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> ExecutionComparisonEntry:
        """Build an entry from a normalized execution result."""
        if execution is None:
            return cls(
                leg=leg,
                status=status,
                message=message,
                metadata=dict(metadata or {}),
            )
        return cls(
            leg=leg,
            algorithm=execution.algorithm,
            executor=execution.executor,
            status=status,
            objective_value=execution.objective_value,
            energy=execution.energy,
            feasible=execution.feasible,
            message=message,
            metadata=dict(metadata or {}),
        )


@dataclass
class ExecutionComparison:
    """Explicit comparison of the legs of a hybrid execution.

    Args:
        entries: Comparison entries, one per leg.
        winner: Leg id that won selection (``"classical"`` / ``"quantum"`` /
            ``None`` when nothing executed).
        selected_reason: Human-readable justification for the winner.
        tie_break: Tie-break rule description when selection needed one.
        sense: Objective sense used for ranking (``"minimize"``/``"maximize"``).
        metadata: Free-form metadata.
    """

    entries: list[ExecutionComparisonEntry] = field(default_factory=list)
    winner: str | None = None
    selected_reason: str = ""
    tie_break: str = ""
    sense: str = "minimize"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "entries": [entry.to_dict() for entry in self.entries],
            "winner": self.winner,
            "selected_reason": self.selected_reason,
            "tie_break": self.tie_break,
            "sense": self.sense,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ExecutionComparison:
        """Rebuild a comparison from :meth:`to_dict` output."""
        return cls(
            entries=[ExecutionComparisonEntry.from_dict(e) for e in data.get("entries", [])],
            winner=data.get("winner"),
            selected_reason=str(data.get("selected_reason", "")),
            tie_break=str(data.get("tie_break", "")),
            sense=str(data.get("sense", "minimize")),
            metadata=dict(data.get("metadata", {})),
        )

    @classmethod
    def build(
        cls,
        entries: list[ExecutionComparisonEntry],
        *,
        sense: ObjectiveSense | str = ObjectiveSense.MINIMIZE,
    ) -> ExecutionComparison:
        """Rank executed legs and pick a deterministic winner.

        Ranking (QMQ-04 §11):
        1. feasible beats infeasible,
        2. better objective per the problem's sense (fallback: QUBO energy,
           lower is better),
        3. ties are broken deterministically in favour of the classical
           exact baseline.

        No quantum-advantage/speedup claim is ever derived from this ranking.
        """
        parsed_sense = sense if isinstance(sense, ObjectiveSense) else ObjectiveSense.parse(sense)
        rank_key = "maximize" if parsed_sense is ObjectiveSense.MAXIMIZE else "minimize"
        executed = [entry for entry in entries if entry.status == _EXECUTED]
        if not executed:
            return cls(
                entries=list(entries),
                winner=None,
                selected_reason="no executable leg produced a result",
                sense=rank_key,
            )

        def score(entry: ExecutionComparisonEntry) -> float | None:
            if entry.objective_value is not None:
                objective = float(entry.objective_value)
                return objective if parsed_sense is ObjectiveSense.MAXIMIZE else -objective
            if entry.energy is not None:
                return -float(entry.energy)
            return None

        scored: list[tuple[ExecutionComparisonEntry, bool, float, int]] = []
        for entry in executed:
            entry_score = score(entry)
            scored.append(
                (
                    entry,
                    bool(entry.feasible),
                    entry_score if entry_score is not None else float("-inf"),
                    _LEG_PRIORITY.get(entry.leg, 0),
                )
            )

        winner_entry, winner_feasible, winner_score, _ = max(
            scored, key=lambda item: (item[1], item[2], item[3])
        )

        tie_break = ""
        if len(scored) > 1:
            peers = [
                item for item in scored if item[1] == winner_feasible and item[2] == winner_score
            ]
            if len(peers) > 1:
                tie_break = (
                    "equal objective and feasibility; deterministic tie-break "
                    "prefers the classical exact baseline"
                )

        reason_parts = [
            f"winner: {winner_entry.leg}",
            f"feasible={winner_feasible}",
            (
                f"objective={winner_score}"
                if winner_entry.objective_value is not None
                else f"energy={winner_entry.energy}"
            ),
        ]
        if tie_break:
            reason_parts.append(tie_break)
        return cls(
            entries=list(entries),
            winner=winner_entry.leg,
            selected_reason="; ".join(reason_parts),
            tie_break=tie_break,
            sense=rank_key,
        )

    def __repr__(self) -> str:
        return (
            f"ExecutionComparison(winner={self.winner!r}, "
            f"entries={[e.leg for e in self.entries]}, sense={self.sense})"
        )


__all__ = ["ExecutionComparison", "ExecutionComparisonEntry"]
