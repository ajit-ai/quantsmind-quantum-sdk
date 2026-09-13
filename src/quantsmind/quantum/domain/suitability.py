"""Quantum suitability assessment (QMQ-11 §5).

:Sclass:`QuantumSuitabilityAssessor` decides, deterministically and with
full evidence, whether a problem can or should run on the quantum path.
The assessment never claims quantum advantage or quantum execution: it only
records whether a QUBO path exists, whether a quantum algorithm was
selected, whether the runtime + algorithm are available, and why.

Suitability levels:

* ``SUITABLE`` — the problem is QUBO-amenable, a quantum algorithm was
  selected, and the environment can execute it.
* ``CONDITIONALLY_SUITABLE`` — a quantum path exists but cannot run here
  (missing runtime/algorithm), or was intentionally not selected (AUTO size
  policy).
* ``UNSUITABLE`` — no usable quantum path exists for the problem.
* ``UNKNOWN`` — no plan was available to assess.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Self

from quantsmind.quantum.intelligence.capabilities import CapabilityModel
from quantsmind.quantum.intelligence.plan import ComputationPlan

__all__ = ["QuantumSuitability", "SuitabilityAssessment", "QuantumSuitabilityAssessor"]


class QuantumSuitability(Enum):
    """Suitability of a problem for the quantum path (QMQ-11 §5)."""

    SUITABLE = "suitable"
    CONDITIONALLY_SUITABLE = "conditionally_suitable"
    UNSUITABLE = "unsuitable"
    UNKNOWN = "unknown"

    @classmethod
    def parse(cls, value: Any) -> QuantumSuitability:
        """Coerce a label or member to a :class:`QuantumSuitability`."""
        if isinstance(value, cls):
            return value
        text = str(value).strip().lower()
        for member in cls:
            if member.value == text or member.name.lower() == text:
                return member
        return QuantumSuitability.UNKNOWN


@dataclass
class SuitabilityAssessment:
    """Evidence-backed suitability of one problem (QMQ-11 §5).

    Args:
        problem_name: Names the assessed problem.
        suitability: The assigned :class:`QuantumSuitability` level.
        reason: Human-readable justification of the assignment.
        signals: Structural signals driving the decision (strategy,
            algorithm, formulation, capability flags, ...).
        evidence: Exact facts that produced the decision.
        limitations: Honest list of conditions that are NOT satisfied.
        quantum_available: Whether a quantum execution runtime was
            available (MicroQuantum installed and enabled).
        algorithm_available: Whether the selected quantum algorithm was
            executable in this environment.
        formulation_amenable: Whether a QUBO formulation path exists.
        provenance: Where-and-how metadata for the assessment.
        metadata: Free-form metadata.
    """

    problem_name: str
    suitability: QuantumSuitability
    reason: str
    signals: dict[str, Any] = field(default_factory=dict)
    evidence: dict[str, Any] = field(default_factory=dict)
    limitations: list[str] = field(default_factory=list)
    quantum_available: bool = False
    algorithm_available: bool = False
    formulation_amenable: bool = False
    provenance: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def label(self) -> str:
        """Serialized suitability label (e.g. ``"suitable"``)."""
        return self.suitability.value

    @property
    def is_suitable(self) -> bool:
        """True for ``SUITABLE`` or ``CONDITIONALLY_SUITABLE``.

        ``is_suitable`` answers "is there a viable quantum path for this
        problem" — never "quantum was executed".  Use
        :attr:`quantum_available` / :attr:`algorithm_available` for the
        execution readiness facts.
        """
        return self.suitability in (
            QuantumSuitability.SUITABLE,
            QuantumSuitability.CONDITIONALLY_SUITABLE,
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "problem_name": self.problem_name,
            "suitability": self.label,
            "reason": self.reason,
            "signals": dict(self.signals),
            "evidence": dict(self.evidence),
            "limitations": list(self.limitations),
            "quantum_available": bool(self.quantum_available),
            "algorithm_available": bool(self.algorithm_available),
            "formulation_amenable": bool(self.formulation_amenable),
            "provenance": dict(self.provenance),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Rebuild an assessment from :meth:`to_dict` output."""
        return cls(
            problem_name=str(data.get("problem_name", "")),
            suitability=QuantumSuitability.parse(data.get("suitability", "unknown")),
            reason=str(data.get("reason", "")),
            signals=dict(data.get("signals", {})),
            evidence=dict(data.get("evidence", {})),
            limitations=[str(x) for x in data.get("limitations", [])],
            quantum_available=bool(data.get("quantum_available", False)),
            algorithm_available=bool(data.get("algorithm_available", False)),
            formulation_amenable=bool(data.get("formulation_amenable", False)),
            provenance=dict(data.get("provenance", {})),
            metadata=dict(data.get("metadata", {})),
        )

    def __repr__(self) -> str:
        return (
            f"SuitabilityAssessment({self.problem_name!r} -> "
            f"{self.label}, quantum={self.quantum_available}, "
            f"algorithm={self.algorithm_available})"
        )


class QuantumSuitabilityAssessor:
    """Deterministic, evidence-backed suitability assessment (QMQ-11 §5).

    Rules (in evaluation order):

    1. No usable plan -> ``UNKNOWN``.
    2. Not QUBO-amenable (``plan.formulation != "qubo"``) -> ``UNSUITABLE``.
    3. Quantum algorithm selected AND runtime + algorithm available ->
       ``SUITABLE``.
    4. Quantum path exists (quantum/classical-hybrid strategy or quantum
       algorithm) but is not executable here -> ``CONDITIONALLY_SUITABLE``
       with the missing prerequisites listed as limitations.
    5. Otherwise (AUTO selected CLASSICAL for a QUBO-amenable problem) ->
       ``CONDITIONALLY_SUITABLE`` with the size policy stated.
    """

    def assess(
        self,
        *,
        plan: ComputationPlan,
        capabilities: CapabilityModel | None = None,
        problem_name: str | None = None,
    ) -> SuitabilityAssessment:
        """Assess a :class:`ComputationPlan` against an environment snapshot.

        Args:
            plan: The QMQ-03 :class:`ComputationPlan` to assess.
            capabilities: Capability snapshot; re-detected when omitted.
            problem_name: Optional override of the assessed problem name.

        Returns:
            SuitabilityAssessment: Level, reasons, limitations and evidence.
        """
        capabilities = capabilities or CapabilityModel.detect()
        name = problem_name or plan.problem_name
        quantum_ready = capabilities.quantum_execution_enabled
        algorithm = (plan.algorithm or "").strip()
        algorithm_ready = (
            capabilities.is_available(algorithm)
            if algorithm and algorithm not in ("exhaustive", "classical")
            else False
        )
        uses_quantum_strategy = plan.strategy.uses_quantum_runtime or plan.is_quantum()
        quantum_algorithm_selected = (
            bool(algorithm) and algorithm not in ("exhaustive", "classical") and plan.is_quantum()
        )

        signals: dict[str, Any] = {
            "strategy_selected": plan.strategy_label,
            "algorithm_selected": algorithm,
            "formulation_selected": plan.formulation,
            "quantum_ready": bool(quantum_ready),
            "quantum_algorithm_selected": bool(quantum_algorithm_selected),
        }
        evidence: dict[str, Any] = {
            "quantum_enabled": bool(capabilities.quantum_enabled),
            "microquantum_installed": bool(capabilities.microquantum_installed),
            "algorithm_available": bool(algorithm_ready),
            "formulation_amenable": plan.formulation == "qubo",
            "capability_probe": str(capabilities.metadata.get("probe", "")),
        }

        if plan.formulation != "qubo":
            return self._assessment(
                name,
                QuantumSuitability.UNSUITABLE,
                reason=(
                    f"problem {name!r} is not QUBO-amenable "
                    f"(formulation {plan.formulation!r}); classical path only"
                ),
                signals=signals,
                evidence=evidence,
                limitations=[
                    f"formulation {plan.formulation!r} does not map to the QUBO pipeline",
                ],
                quantum_available=quantum_ready,
                algorithm_available=algorithm_ready,
                formulation_amenable=False,
            )

        if quantum_algorithm_selected and quantum_ready and algorithm_ready:
            return self._assessment(
                name,
                QuantumSuitability.SUITABLE,
                reason=(
                    f"QUBO path exists; quantum algorithm {algorithm!r} was "
                    "selected and this environment can execute it"
                ),
                signals=signals,
                evidence=evidence,
                limitations=[],
                quantum_available=True,
                algorithm_available=True,
                formulation_amenable=True,
            )

        limitations: list[str] = []
        if uses_quantum_strategy and not quantum_ready:
            limitations.append(
                "a quantum strategy was selected but no quantum execution "
                "runtime is available here (MicroQuantum not installed/enabled)"
            )
        if uses_quantum_strategy and quantum_ready and not algorithm_ready:
            limitations.append(
                f"quantum algorithm {algorithm!r} is not executable in this environment"
            )
        if not uses_quantum_strategy:
            limitations.append(
                f"strategy {plan.strategy_label!r} is CLASSICAL here "
                "(automatic size policy or runtime absence)"
            )
        if not limitations:
            limitations.append("quantum path not executed in this environment")
        return self._assessment(
            name,
            QuantumSuitability.CONDITIONALLY_SUITABLE,
            reason=(
                f"QUBO path exists for {name!r} but the quantum path did not "
                "and/or could not run in this environment"
            ),
            signals=signals,
            evidence=evidence,
            limitations=limitations,
            quantum_available=quantum_ready,
            algorithm_available=algorithm_ready,
            formulation_amenable=True,
        )

    def assess_unknown(self, *, problem_name: str) -> SuitabilityAssessment:
        """Return an ``UNKNOWN`` assessment when no plan could be built."""
        return self._assessment(
            problem_name,
            QuantumSuitability.UNKNOWN,
            reason=f"no computation plan could be built for {problem_name!r}",
            signals={},
            evidence={},
            limitations=["no plan was produced to assess"],
            quantum_available=False,
            algorithm_available=False,
            formulation_amenable=False,
        )

    @staticmethod
    def _assessment(
        problem_name: str,
        suitability: QuantumSuitability,
        *,
        reason: str,
        signals: dict[str, Any],
        evidence: dict[str, Any],
        limitations: list[str],
        quantum_available: bool,
        algorithm_available: bool,
        formulation_amenable: bool,
    ) -> SuitabilityAssessment:
        return SuitabilityAssessment(
            problem_name=problem_name,
            suitability=suitability,
            reason=reason,
            signals=dict(signals),
            evidence=dict(evidence),
            limitations=list(limitations),
            quantum_available=quantum_available,
            algorithm_available=algorithm_available,
            formulation_amenable=formulation_amenable,
            provenance={
                "module": "quantsmind.quantum.domain.suitability",
                "rule_path": ["deterministic-suitability-rules"],
            },
        )
