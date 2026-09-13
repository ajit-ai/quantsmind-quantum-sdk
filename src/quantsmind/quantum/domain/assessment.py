"""Cross-domain problem assessment (QMQ-11 §4, §7).

:func:`assess_problem` walks one domain problem through the registered
binding and the existing QMQ-03 intelligence pipeline — classify, formulate,
choose strategy, recommend algorithm, build the computation plan, assess
suitability — and returns a :class:`ProblemAssessment` that is fully
inspectable and serializable.  No execution happens during assessment.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, Self

from quantsmind.quantum.domain.errors import DomainValidationError
from quantsmind.quantum.domain.registry import DomainKind, DomainRegistry
from quantsmind.quantum.domain.suitability import (
    QuantumSuitabilityAssessor,
    SuitabilityAssessment,
)
from quantsmind.quantum.intelligence.capabilities import CapabilityModel
from quantsmind.quantum.intelligence.classification import (
    ClassificationResult,
    ProblemClassifier,
)
from quantsmind.quantum.intelligence.plan import ComputationPlan
from quantsmind.quantum.intelligence.recommender import (
    AlgorithmSelector,
    FormulationRecommendation,
    FormulationRecommender,
)
from quantsmind.quantum.strategy.selector import StrategyDecision, StrategySelector

if TYPE_CHECKING:
    pass

__all__ = ["ProblemAssessment", "assess_problem"]


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


@dataclass
class ProblemAssessment:
    """Full, inspectable assessment of one domain problem (QMQ-11 §7).

    Args:
        problem_name: Name of the assessed problem.
        domain: The dispatched :class:`DomainKind`.
        problem_type: Class name of the assessed problem.
        classification: QMQ-03 classification decision.
        formulation: QMQ-03 formulation-kind recommendation.
        strategy_decision: QMQ-03 strategy decision (with rationale).
        algorithm_recommendation: QMQ-03 algorithm recommendation (with
            executable fallbacks).
        capabilities: Capability snapshot the decisions used.
        suitability: :class:`SuitabilityAssessment` of the plan.
        computation_plan: The QMQ-03 :class:`ComputationPlan` built.
        reasons: Rolled-up human-readable justification.
        provenance: Where-and-how metadata.
        created_at: ISO-8601 creation timestamp.
        metadata: Free-form metadata.
    """

    problem_name: str
    domain: DomainKind | None = None
    problem_type: str = ""
    classification: ClassificationResult | None = None
    formulation: FormulationRecommendation | None = None
    strategy_decision: StrategyDecision | None = None
    algorithm_recommendation: Any | None = None
    capabilities: CapabilityModel | None = None
    suitability: SuitabilityAssessment | None = None
    computation_plan: ComputationPlan | None = None
    reasons: list[str] = field(default_factory=list)
    provenance: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=_utc_now)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def domain_label(self) -> str:
        """Serialized domain label (e.g. ``"ml"``)."""
        return self.domain.value if self.domain is not None else ""

    @property
    def strategy_label(self) -> str:
        """Serialized selected strategy label."""
        if self.strategy_decision is not None:
            return self.strategy_decision.label
        if self.computation_plan is not None:
            return self.computation_plan.strategy_label
        return ""

    @property
    def algorithm(self) -> str:
        """Selected primary algorithm id (``""`` when none)."""
        if self.algorithm_recommendation is not None:
            return str(self.algorithm_recommendation.algorithm)
        if self.computation_plan is not None and self.computation_plan.algorithm:
            return str(self.computation_plan.algorithm)
        return ""

    @property
    def formulation_kind(self) -> str:
        """Recommended formulation kind (e.g. ``"qubo"``)."""
        if self.formulation is not None:
            return str(self.formulation.primary)
        if self.computation_plan is not None:
            return self.computation_plan.formulation
        return ""

    @property
    def suitability_label(self) -> str:
        """Serialized suitability label (``""`` when unassessed)."""
        return self.suitability.label if self.suitability is not None else ""

    @property
    def is_implementable(self) -> bool:
        """True when a computation plan was built (ready to run)."""
        return self.computation_plan is not None

    def summary(self) -> str:
        """One-line human summary of the assessment."""
        return (
            f"{self.problem_name!r} [{self.domain_label}/{self.problem_type}] "
            f"-> {self.classification.label if self.classification else '?'} / "
            f"{self.formulation_kind} / strategy={self.strategy_label or '?'} / "
            f"algorithm={self.algorithm or 'none'} / "
            f"suitability={self.suitability_label or 'unassessed'}"
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "problem_name": self.problem_name,
            "domain": self.domain_label,
            "problem_type": self.problem_type,
            "classification": (
                self.classification.to_dict() if self.classification is not None else None
            ),
            "formulation": (self.formulation.to_dict() if self.formulation is not None else None),
            "strategy_decision": (
                self.strategy_decision.to_dict() if self.strategy_decision is not None else None
            ),
            "algorithm_recommendation": (
                self.algorithm_recommendation.to_dict()
                if self.algorithm_recommendation is not None
                else None
            ),
            "capabilities": (
                self.capabilities.to_dict() if self.capabilities is not None else None
            ),
            "suitability": (self.suitability.to_dict() if self.suitability is not None else None),
            "computation_plan": (
                self.computation_plan.to_dict() if self.computation_plan is not None else None
            ),
            "reasons": list(self.reasons),
            "provenance": dict(self.provenance),
            "created_at": self.created_at,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Rebuild an assessment from :meth:`to_dict` output."""
        domain_label = str(data.get("domain", ""))
        domain = None
        if domain_label:
            domain = DomainKind.parse(domain_label)
        classification = data.get("classification")
        formulation = data.get("formulation")
        strategy_decision = data.get("strategy_decision")
        algorithm_recommendation = data.get("algorithm_recommendation")
        capabilities = data.get("capabilities")
        suitability = data.get("suitability")
        computation_plan = data.get("computation_plan")
        return cls(
            problem_name=str(data.get("problem_name", "")),
            domain=domain,
            problem_type=str(data.get("problem_type", "")),
            classification=(
                ClassificationResult.from_dict(dict(classification))
                if classification is not None
                else None
            ),
            formulation=(
                FormulationRecommendation.from_dict(dict(formulation))
                if formulation is not None
                else None
            ),
            strategy_decision=(
                StrategyDecision.from_dict(dict(strategy_decision))
                if strategy_decision is not None
                else None
            ),
            algorithm_recommendation=(
                _algorithm_recommendation_from_dict(algorithm_recommendation)
                if algorithm_recommendation is not None
                else None
            ),
            capabilities=(
                CapabilityModel.from_dict(dict(capabilities)) if capabilities is not None else None
            ),
            suitability=(
                SuitabilityAssessment.from_dict(dict(suitability))
                if suitability is not None
                else None
            ),
            computation_plan=(
                ComputationPlan.from_dict(dict(computation_plan))
                if computation_plan is not None
                else None
            ),
            reasons=[str(r) for r in data.get("reasons", [])],
            provenance=dict(data.get("provenance", {})),
            created_at=str(data.get("created_at", _utc_now())),
            metadata=dict(data.get("metadata", {})),
        )

    def __repr__(self) -> str:
        return (
            f"ProblemAssessment({self.problem_name!r} / {self.domain_label} / "
            f"{self.suitability_label or 'unassessed'})"
        )


def _algorithm_recommendation_from_dict(data: dict[str, Any]) -> Any:
    from quantsmind.quantum.intelligence.algorithms import AlgorithmRecommendation

    return AlgorithmRecommendation.from_dict(data)


def assess_problem(
    problem: Any,
    registry: DomainRegistry | None = None,
    *,
    strategy: str | None = None,
    capabilities: CapabilityModel | None = None,
) -> ProblemAssessment:
    """Assess one domain problem through the QMQ-03 pipeline (no execution).

    Args:
        problem: The domain problem to assess.
        registry: Dispatch registry; defaults to a fresh
            :class:`DomainRegistry` with the built-in domains.
        strategy: Optional requested strategy label (forwarded to
            :meth:`StrategySelector.select_reasoned` through the binding).
        capabilities: Capability snapshot; detected when omitted.

    Raises:
        UnsupportedDomainError: When no registered binding supports the
            problem.
        DomainValidationError: When the problem fails its validation.
    """
    registry = registry or DomainRegistry()
    binding = registry.resolve(problem)
    problem_name = getattr(problem, "name", type(problem).__name__)
    issues = binding.validate(problem)
    if issues:
        raise DomainValidationError(
            f"cannot assess invalid {type(problem).__name__} problem "
            f"{problem_name!r}: " + "; ".join(issues),
            problem=problem,
        )
    capabilities = capabilities or CapabilityModel.detect()
    quantum_problem = binding.to_quantum_problem(problem, preferred_strategy=strategy)

    classification = ProblemClassifier().classify(quantum_problem)
    formulation_recommendation = FormulationRecommender().recommend(
        quantum_problem, classification=classification
    )
    strategy_decision = StrategySelector().select_reasoned(
        quantum_problem,
        classification=classification,
        formulation=quantum_problem.formulation,
        capabilities=capabilities,
    )
    algorithm_recommendation = AlgorithmSelector().select(
        quantum_problem,
        strategy=strategy_decision.strategy,
        classification=classification,
        capabilities=capabilities,
        allow_fallback=True,
    )
    plan = _build_computation_plan(
        quantum_problem,
        classification=classification,
        formulation_recommendation=formulation_recommendation,
        strategy_decision=strategy_decision,
        algorithm_recommendation=algorithm_recommendation,
    )
    suitability = QuantumSuitabilityAssessor().assess(plan=plan, capabilities=capabilities)
    reasons = list(strategy_decision.reasons)
    if plan.reason:
        reasons.append(plan.reason)
    reasons.append(suitability.reason)
    return ProblemAssessment(
        problem_name=problem_name,
        domain=binding.kind,
        problem_type=type(problem).__name__,
        classification=classification,
        formulation=formulation_recommendation,
        strategy_decision=strategy_decision,
        algorithm_recommendation=algorithm_recommendation,
        capabilities=capabilities,
        suitability=suitability,
        computation_plan=plan,
        reasons=reasons,
        provenance={
            "module": "quantsmind.quantum.domain.assessment",
            "domain_binding": binding.label,
            "pipeline": "classify->formulate->strategy->algorithm->plan->suitability",
        },
        metadata={"requested_strategy": strategy or ""},
    )


def _executor_for(strategy: Any, algorithm: str | None) -> str:
    """Deterministic executor label for a strategy/algorithm pair."""
    from quantsmind.quantum.strategy.strategy import ComputationStrategy

    if (
        strategy in (ComputationStrategy.QUANTUM, ComputationStrategy.HYBRID)
        and algorithm
        and algorithm not in ("exhaustive", "classical")
    ):
        return f"microquantum/{algorithm}"
    if strategy is ComputationStrategy.QUANTUM_INSPIRED:
        return "classical/quantum-inspired"
    return "classical/exhaustive"


def _build_computation_plan(
    quantum_problem: Any,
    *,
    classification: ClassificationResult,
    formulation_recommendation: FormulationRecommendation,
    strategy_decision: StrategyDecision,
    algorithm_recommendation: Any,
) -> ComputationPlan:
    """Build the QMQ-03 :class:`ComputationPlan` for an assessment.

    The plan's mapping label is taken from the formulation recommendation
    (``"qubo"`` when the QUBO path exists) and its executor from the chosen
    strategy and algorithm, mirroring how QMQ-04 runs the plan.
    """
    algorithm = algorithm_recommendation.algorithm if algorithm_recommendation is not None else None
    mapping = (
        "qubo"
        if formulation_recommendation.is_qubo
        else (str(formulation_recommendation.primary) or "none")
    )
    executor = _executor_for(strategy_decision.strategy, algorithm)
    fallbacks = (
        [str(f.algorithm) for f in algorithm_recommendation.fallbacks]
        if algorithm_recommendation is not None
        else []
    )
    strategy_why = (
        strategy_decision.reasons[0] if strategy_decision.reasons else "strategy selected"
    )
    algorithm_why = (
        algorithm_recommendation.reason if algorithm_recommendation is not None else "no algorithm"
    )
    reason = f"{classification.reason} | {strategy_why} | {algorithm_why}"
    return ComputationPlan(
        problem_name=quantum_problem.name,
        problem_class=classification.label,
        formulation=formulation_recommendation.primary,
        strategy=strategy_decision.strategy,
        algorithm=algorithm,
        recommendation=algorithm_recommendation,
        mapping=mapping,
        executor=executor,
        fallbacks=fallbacks,
        classification=classification,
        formulation_recommendation=formulation_recommendation,
        strategy_decision=strategy_decision,
        reason=reason,
        provenance={
            "module": "quantsmind.quantum.domain.assessment",
            "rule_path": ["domain-assessment-plan"],
        },
    )


__all__ = ["ProblemAssessment", "assess_problem"]
