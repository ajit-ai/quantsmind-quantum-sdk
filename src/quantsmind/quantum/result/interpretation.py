"""Data-derived interpretation of quantum domain solutions.

An :class:`Interpretation` summarizes *what the data says* about a
solution (feasibility, objective values, constraint status, score).  QMQ-01
deliberately does **not** fabricate domain or business meaning — that is
the task of later domain-specific interpretation modules.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from quantsmind.quantum.core.constraint import ConstraintStatus
from quantsmind.quantum.core.solution import ProblemSolution
from quantsmind.quantum.strategy.strategy import ComputationStrategy


class InterpretationQuality(Enum):
    """Overall confidence in a solution interpretation.

    Attributes:
        HIGH: Fully evaluated and feasible.
        MEDIUM: Partially evaluated (some constraints unknown).
        LOW: Infeasible (one or more constraints violated).
        UNKNOWN: Nothing could be evaluated.
    """

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


@dataclass
class Interpretation:
    """A structured, data-derived explanation of a solution.

    Args:
        summary: One-line human-readable summary.
        quality: Feasibility/evidence quality level.
        confidence: Optional numeric confidence in [0, 1].
        details: Free-form facts (feasible, objective values, statuses).
        metadata: Free-form metadata (e.g. strategy used).
    """

    summary: str = ""
    quality: InterpretationQuality = InterpretationQuality.UNKNOWN
    confidence: float | None = None
    details: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "summary": self.summary,
            "quality": self.quality.value,
            "confidence": self.confidence,
            "details": dict(self.details),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Interpretation:
        """Rebuild an Interpretation from :meth:`to_dict` output."""
        quality = str(data.get("quality", "unknown")).lower()
        try:
            parsed = InterpretationQuality(quality)
        except ValueError:
            parsed = InterpretationQuality.UNKNOWN
        return cls(
            summary=str(data.get("summary", "")),
            quality=parsed,
            confidence=(float(data["confidence"]) if data.get("confidence") is not None else None),
            details=dict(data.get("details", {})),
            metadata=dict(data.get("metadata", {})),
        )

    def __repr__(self) -> str:
        return f"Interpretation(quality={self.quality.value}, summary={self.summary!r})"


class SolutionInterpreter:
    """Produces conservative, data-derived interpretations of solutions.

    The interpreter derives its statements only from the solution itself
    (feasibility, objective values, constraint statuses, score) and the
    strategy that produced it.  No domain meaning is invented.
    """

    def interpret(
        self,
        solution: ProblemSolution,
        *,
        strategy: ComputationStrategy | str | None = None,
    ) -> Interpretation:
        """Interpret a solution using only its own data.

        Args:
            solution: The domain solution to interpret.
            strategy: Optional computation strategy used (recorded as
                metadata only).

        Returns:
            An :class:`Interpretation` constructed from solution facts.
        """
        statuses = list(solution.constraint_status.values())
        satisfied = sum(s is ConstraintStatus.SATISFIED for s in statuses)
        violated = sum(s is ConstraintStatus.VIOLATED for s in statuses)
        unknown = sum(s is ConstraintStatus.UNKNOWN for s in statuses)

        if violated:
            quality = InterpretationQuality.LOW
            summary = (
                f"solution for problem {solution.problem_name!r} is infeasible: "
                f"{violated} of {len(statuses)} constraints violated"
            )
        elif not statuses:
            quality = InterpretationQuality.UNKNOWN
            summary = (
                f"solution for problem {solution.problem_name!r} could not be "
                "judged (problem declares no evaluable constraints)"
            )
        elif statuses and unknown == len(statuses):
            quality = InterpretationQuality.UNKNOWN
            summary = (
                f"solution for problem {solution.problem_name!r} could not be "
                "evaluated (no evaluable constraints)"
            )
        elif statuses and satisfied < len(statuses):
            quality = InterpretationQuality.MEDIUM
            summary = (
                f"solution for problem {solution.problem_name!r}: {satisfied} of "
                f"{len(statuses)} constraints satisfied, {unknown} unknown"
            )
        else:
            quality = InterpretationQuality.HIGH
            summary = (
                f"feasible solution for problem {solution.problem_name!r} "
                f"({satisfied} of {len(statuses)} constraints satisfied)"
            )

        strategy_label = (
            strategy.name.lower()
            if isinstance(strategy, ComputationStrategy)
            else (strategy.lower() if strategy else None)
        )
        details: dict[str, Any] = {
            "feasible": solution.feasible,
            "objective_values": dict(solution.objective_values),
            "constraints": {
                "satisfied": satisfied,
                "violated": violated,
                "unknown": unknown,
            },
            "score": solution.score,
            "strategy": strategy_label,
        }
        return Interpretation(
            summary=summary,
            quality=quality,
            details=details,
            metadata={"interpreter": self.__class__.__name__},
        )

    def __call__(
        self,
        solution: ProblemSolution,
        *,
        strategy: ComputationStrategy | str | None = None,
    ) -> Interpretation:
        """Convenience alias for :meth:`interpret`."""
        return self.interpret(solution, strategy=strategy)


__all__ = ["Interpretation", "InterpretationQuality", "SolutionInterpreter"]
