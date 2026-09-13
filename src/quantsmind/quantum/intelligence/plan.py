"""QMQ-03 declarative computation plan.

A :class:`ComputationPlan` records, for one domain problem, every decision
the intelligence layer made: classification, formulation, strategy,
algorithm recommendation (with fallbacks), mapping, executor and the
capability snapshot that justified them.  It is declarative and serializable,
ready for QMQ-04 to execute without re-deriving any decision.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, Self

from quantsmind.quantum.intelligence.algorithms import AlgorithmRecommendation
from quantsmind.quantum.intelligence.classification import ClassificationResult
from quantsmind.quantum.intelligence.recommender import FormulationRecommendation
from quantsmind.quantum.strategy.strategy import ComputationStrategy

if TYPE_CHECKING:
    from quantsmind.quantum.strategy.selector import StrategyDecision


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


@dataclass
class ComputationPlan:
    """Declarative execution plan for one problem (QMQ-03 §13).

    Args:
        problem_name: Name of the domain problem.
        problem_class: Classification label (e.g. ``"binary_optimization"``).
        formulation: Formulation kind to execute (e.g. ``"qubo"``).
        strategy: Chosen :class:`ComputationStrategy`.
        algorithm: Recommended primary algorithm id, or ``None``.
        recommendation: The full algorithm recommendation object.
        mapping: Mapping label needed for the chosen algorithm
            (e.g. ``"qubo"`` / ``"ising"`` / ``"none"``).
        executor: Executor that will run the plan (e.g.
            ``"microquantum/qaoa"`` / ``"classical/exhaustive"``).
        fallbacks: Executable fallback algorithm ids in preference order.
        capabilities: Capability snapshot justifying the recommendation.
        classification: The classification decision used.
        formulation_recommendation: The formulation recommendation used.
        strategy_decision: The strategy decision used.
        reason: Standing human-readable justification.
        provenance: Emergent provenance notes (module, rule path).
        created_at: ISO-8601 creation timestamp.
        metadata: Free-form metadata.
    """

    problem_name: str
    problem_class: str
    formulation: str
    strategy: ComputationStrategy
    algorithm: str | None
    recommendation: AlgorithmRecommendation
    mapping: str = "none"
    executor: str = ""
    fallbacks: list[str] = field(default_factory=list)
    capabilities: dict[str, bool] = field(default_factory=dict)
    classification: ClassificationResult | None = None
    formulation_recommendation: FormulationRecommendation | None = None
    strategy_decision: StrategyDecision | None = None
    reason: str = ""
    provenance: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=_utc_now)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def strategy_label(self) -> str:
        """Serialized strategy label (e.g. ``"hybrid"``)."""
        return self.strategy.value

    def is_quantum(self) -> bool:
        """True when the plan executes a quantum algorithm."""
        return self.executor == "microquantum/qaoa" or (
            self.strategy.uses_quantum_runtime and self.algorithm not in ("exhaustive", None)
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "problem_name": self.problem_name,
            "problem_class": self.problem_class,
            "formulation": self.formulation,
            "strategy": self.strategy.value,
            "algorithm": self.algorithm,
            "mapping": self.mapping,
            "executor": self.executor,
            "fallbacks": list(self.fallbacks),
            "capabilities": dict(self.capabilities),
            "recommendation": self.recommendation.to_dict(),
            "classification": (self.classification.to_dict() if self.classification else None),
            "formulation_recommendation": (
                self.formulation_recommendation.to_dict()
                if self.formulation_recommendation
                else None
            ),
            "strategy_decision": (
                self.strategy_decision.to_dict() if self.strategy_decision else None
            ),
            "reason": self.reason,
            "provenance": dict(self.provenance),
            "created_at": self.created_at,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Rebuild a plan from :meth:`to_dict` output."""
        strategy_decision_data = data.get("strategy_decision")
        strategy_decision = None
        if strategy_decision_data:
            from quantsmind.quantum.strategy.selector import StrategyDecision

            strategy_decision = StrategyDecision.from_dict(strategy_decision_data)
        return cls(
            problem_name=str(data.get("problem_name", "")),
            problem_class=str(data.get("problem_class", "unknown")),
            formulation=str(data.get("formulation", "optimization")),
            strategy=ComputationStrategy.parse(data.get("strategy", "classical")),
            algorithm=data.get("algorithm"),
            recommendation=AlgorithmRecommendation.from_dict(data.get("recommendation") or {}),
            mapping=str(data.get("mapping", "none")),
            executor=str(data.get("executor", "")),
            fallbacks=[str(f) for f in data.get("fallbacks", [])],
            capabilities={str(k): bool(v) for k, v in data.get("capabilities", {}).items()},
            classification=(
                ClassificationResult.from_dict(data["classification"])
                if data.get("classification")
                else None
            ),
            formulation_recommendation=(
                FormulationRecommendation.from_dict(data["formulation_recommendation"])
                if data.get("formulation_recommendation")
                else None
            ),
            strategy_decision=strategy_decision,
            reason=str(data.get("reason", "")),
            provenance=dict(data.get("provenance", {})),
            created_at=str(data.get("created_at", _utc_now())),
            metadata=dict(data.get("metadata", {})),
        )

    def __repr__(self) -> str:
        return (
            f"ComputationPlan({self.problem_name!r}: {self.problem_class} / "
            f"{self.formulation} / {self.strategy_label} / "
            f"{self.algorithm!r} -> {self.executor!r})"
        )


__all__ = ["ComputationPlan"]
