"""Inspectable, domain-aware execution plan (QMQ-11 §7).

:mod:`quantsmind.quantum.domain.plan` wraps a :class:`ComputationPlan` with
the domain dimension (:class:`DomainKind`) and the full
:class:`SuitabilityAssessment`, so the caller can inspect *what* will run,
*why* it was selected, and *whether* the quantum path is available in this
environment, before any execution happens.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, Self

from quantsmind.quantum.domain.registry import DomainKind
from quantsmind.quantum.domain.suitability import SuitabilityAssessment
from quantsmind.quantum.intelligence.plan import ComputationPlan

if TYPE_CHECKING:
    pass

__all__ = ["ExecutionPlan"]


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


@dataclass
class ExecutionPlan:
    """Domain-aware, inspectable execution plan (QMQ-11 §7).

    Args:
        plan: The QMQ-03 :class:`ComputationPlan` (classification,
            formulation, strategy, algorithm, mapping, executor, fallbacks).
        domain: The dispatched :class:`DomainKind`.
        problem_type: Class name of the source domain problem.
        strategy_requested: Explicit strategy the caller requested
            (``""`` for automatic).
        suitability: Suitability assessment of the plan.
        classification: Serialized classification label.
        formulation_kind: Serialized formulation kind.
        reasons: Rolled-up reasons from the plan and suitability.
        provenance: Where-and-how metadata.
        created_at: ISO-8601 creation timestamp.
        metadata: Free-form metadata.
    """

    plan: ComputationPlan
    domain: DomainKind
    problem_type: str
    strategy_requested: str
    suitability: SuitabilityAssessment
    classification: str = ""
    formulation_kind: str = ""
    reasons: list[str] = field(default_factory=list)
    provenance: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=_utc_now)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def problem_name(self) -> str:
        return self.plan.problem_name

    @property
    def domain_label(self) -> str:
        return self.domain.value

    @property
    def strategy(self) -> str:
        return self.plan.strategy_label

    @property
    def algorithm(self) -> str | None:
        return self.plan.algorithm

    @property
    def executor(self) -> str:
        return self.plan.executor

    @property
    def mapping(self) -> str:
        return self.plan.mapping

    @property
    def fallbacks(self) -> list[str]:
        return list(self.plan.fallbacks)

    @property
    def is_quantum(self) -> bool:
        return self.plan.is_quantum()

    def summary(self) -> str:
        """One-line human summary of the plan."""
        return (
            f"{self.problem_name!r} [{self.domain_label}/{self.problem_type}] "
            f"-> {self.classification} / {self.formulation_kind} / "
            f"strategy={self.strategy} / executor={self.executor!r} / "
            f"suitability={self.suitability.label}"
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "problem_name": self.problem_name,
            "domain": self.domain_label,
            "problem_type": self.problem_type,
            "strategy_requested": self.strategy_requested,
            "classification": self.classification,
            "formulation_kind": self.formulation_kind,
            "strategy": self.strategy,
            "algorithm": self.algorithm,
            "executor": self.executor,
            "mapping": self.mapping,
            "fallbacks": self.fallbacks,
            "is_quantum": self.is_quantum,
            "suitability": self.suitability.to_dict(),
            "plan": self.plan.to_dict(),
            "reasons": list(self.reasons),
            "provenance": dict(self.provenance),
            "created_at": self.created_at,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Rebuild a plan from :meth:`to_dict` output."""
        return cls(
            plan=ComputationPlan.from_dict(data["plan"]),
            domain=DomainKind.parse(data.get("domain", "")),
            problem_type=str(data.get("problem_type", "")),
            strategy_requested=str(data.get("strategy_requested", "")),
            suitability=SuitabilityAssessment.from_dict(data.get("suitability", {})),
            classification=str(data.get("classification", "")),
            formulation_kind=str(data.get("formulation_kind", "")),
            reasons=[str(r) for r in data.get("reasons", [])],
            provenance=dict(data.get("provenance", {})),
            created_at=str(data.get("created_at", _utc_now())),
            metadata=dict(data.get("metadata", {})),
        )

    def __repr__(self) -> str:
        return (
            f"ExecutionPlan({self.problem_name!r} [{self.domain_label}] -> "
            f"{self.strategy}/{self.executor!r}, "
            f"suitability={self.suitability.label})"
        )
