"""QMQ-03 deterministic problem classification.

The classifier decides what kind of problem a
:class:`~quantsmind.quantum.core.problem.QuantumProblem` is (``binary_optimization``,
``graph_optimization``, ``simulation``, ...).  It is **synthetic and rule
based**, never an AI/LLM model: every decision is derived from structural
signals (variable types, formulation kind, explicit metadata) and is fully
deterministic and explainable.

Rules are ordered by specificity:

1. An explicit ``problem.metadata["problem_class"]`` override wins.
2. Otherwise the formulation ``kind`` drives the decision
   (``graph`` -> ``graph_optimization``, ``ml`` -> ``machine_learning``, ...).
3. ``optimization`` formulations are refined by the variable types
   (all binary -> ``binary_optimization``, any continuous -> ``continuous_optimization``,
   any integer -> ``integer_optimization``, otherwise ``constraint_optimization``).

The classifier is extensible: subclasses can override :meth:`_classify` or
custom rules can be layered in front of :meth:`classify`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any, Self

from quantsmind.quantum.core.variable import VariableType

if TYPE_CHECKING:
    from quantsmind.quantum.core.problem import QuantumProblem
    from quantsmind.quantum.formulation.mathematical_model import MathematicalModel

_OPTIMIZATION_CLASSES = (
    "binary_optimization",
    "integer_optimization",
    "continuous_optimization",
    "constraint_optimization",
)


class ProblemClass(Enum):
    """Machine-readable problem category (QMQ-03).

    Labels are snake_case so they survive JSON round trips.
    """

    BINARY_OPTIMIZATION = "binary_optimization"
    INTEGER_OPTIMIZATION = "integer_optimization"
    CONTINUOUS_OPTIMIZATION = "continuous_optimization"
    GRAPH_OPTIMIZATION = "graph_optimization"
    CONSTRAINT_OPTIMIZATION = "constraint_optimization"
    SIMULATION = "simulation"
    MACHINE_LEARNING = "machine_learning"
    STATISTICAL = "statistical"
    SEARCH = "search"
    SAMPLING = "sampling"
    LINEAR_ALGEBRA = "linear_algebra"
    UNKNOWN = "unknown"

    @classmethod
    def parse(cls, value: Any) -> ProblemClass:
        """Coerce a snake_case label or member to a :class:`ProblemClass`."""
        if isinstance(value, cls):
            return value
        text = str(value).strip().lower().replace("-", "_").replace(" ", "_")
        for member in cls:
            if member.name.lower() == text or member.value == text:
                return member
        raise ValueError(f"unknown problem class {value!r}")

    @classmethod
    def known_labels(cls) -> tuple[str, ...]:
        """All serialized labels of the supported problem classes."""
        return tuple(member.value for member in cls)


@dataclass
class ClassificationResult:
    """Result of a deterministic problem classification.

    Args:
        problem_name: Name of the classified problem.
        problem_class: The assigned :class:`ProblemClass`.
        reason: Human-readable explanation of the assignment.
        signals: Structural signals used by the classifier (variable types,
            formulation kind, counts, ...).
        metadata: Free-form classification metadata (e.g. the rule path).
    """

    problem_name: str
    problem_class: ProblemClass
    reason: str
    signals: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def label(self) -> str:
        """Serialized label of the problem class (e.g. ``"binary_optimization"``)."""
        return self.problem_class.value

    @property
    def is_optimization(self) -> bool:
        """True for the optimization family of classes."""
        return self.label in _OPTIMIZATION_CLASSES

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "problem_name": self.problem_name,
            "problem_class": self.label,
            "reason": self.reason,
            "signals": dict(self.signals),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Rebuild a ClassificationResult from :meth:`to_dict` output."""
        return cls(
            problem_name=str(data.get("problem_name", "")),
            problem_class=ProblemClass.parse(data.get("problem_class", "unknown")),
            reason=str(data.get("reason", "")),
            signals=dict(data.get("signals", {})),
            metadata=dict(data.get("metadata", {})),
        )

    def __repr__(self) -> str:
        return f"ClassificationResult({self.problem_name!r} -> {self.label})"


class ProblemClassifier:
    """Deterministic structural problem classifier (QMQ-03).

    Args:
        default_class: Class assigned when no signal is available.
    """

    def __init__(self, *, default_class: ProblemClass | str = ProblemClass.UNKNOWN) -> None:
        self.default_class = ProblemClass.parse(default_class)

    # ------------------------------------------------------------------
    # public API
    # ------------------------------------------------------------------

    def classify(
        self,
        problem: QuantumProblem,
        formulation: MathematicalModel | None = None,
    ) -> ClassificationResult:
        """Classify a domain problem using structural rules only.

        Args:
            problem: The problem to classify.
            formulation: Optional prebuilt formulation (built on demand
                otherwise).

        Returns:
            ClassificationResult: The assigned class and its rationale.
        """
        variables = list(problem.variables)
        n_objectives = len(problem.objectives)
        n_constraints = len(problem.constraints)
        domain = None
        if problem.domain is not None:
            domain = (
                problem.domain if isinstance(problem.domain, str) else problem.domain.qualified()
            )
        signals: dict[str, Any] = {
            "n_variables": len(variables),
            "n_objectives": n_objectives,
            "n_constraints": n_constraints,
            "variable_types": [v.type.name.lower() for v in variables],
            "formulation_kind": (formulation.kind if formulation is not None else None),
            "domain": domain,
        }

        # Rule 1: an explicit, authoritative metadata override.
        override = problem.metadata.get("problem_class")
        if override is not None:
            try:
                problem_class = ProblemClass.parse(override)
            except ValueError:
                problem_class = self.default_class
            signals["rule"] = "metadata[problem_class] override"
            reason = (
                f"problem {problem.name!r} explicitly declares problem_class "
                f"{problem_class.value!r} in metadata"
            )
            return ClassificationResult(
                problem_name=problem.name,
                problem_class=problem_class,
                reason=reason,
                signals=signals,
                metadata={"rule_path": ["metadata_override"]},
            )

        # Rule 2: formulation kind drives non-optimization decisions.
        model = formulation or problem.formulation
        kind = model.kind if model is not None else None
        if kind is None:
            from quantsmind.quantum.formulation import formulate

            built = formulate(problem)
            kind = built.kind
            signals["formulation_kind"] = kind

        if kind == "graph":
            problem_class = ProblemClass.GRAPH_OPTIMIZATION
            rule_path = ["formulation_kind:graph"]
            reason = f"formulation kind 'graph' -> {problem_class.value}"
        elif kind == "ml":
            problem_class = ProblemClass.MACHINE_LEARNING
            rule_path = ["formulation_kind:ml"]
            reason = f"formulation kind 'ml' -> {problem_class.value}"
        elif kind == "simulation":
            problem_class = ProblemClass.SIMULATION
            rule_path = ["formulation_kind:simulation"]
            reason = f"formulation kind 'simulation' -> {problem_class.value}"
        elif kind == "statistical":
            problem_class = ProblemClass.STATISTICAL
            rule_path = ["formulation_kind:statistical"]
            reason = f"formulation kind 'statistical' -> {problem_class.value}"
        elif kind == "optimization":
            problem_class = self._optimization_subclass(variables)
            rule_path = ["formulation_kind:optimization", "variable_types"]
            reason = (
                f"optimization formulation with variable types "
                f"{signals['variable_types']} -> {problem_class.value}"
            )
        else:
            problem_class = self.default_class
            rule_path = ["formulation_kind:mathematical", "no_structural_signal"]
            reason = (
                f"no structural signal for problem {problem.name!r}; "
                f"assigned {self.default_class.value} by default"
            )

        signals["rule"] = "formulation kind + variable types"
        return ClassificationResult(
            problem_name=problem.name,
            problem_class=problem_class,
            reason=reason,
            signals=signals,
            metadata={"rule_path": rule_path},
        )

    # ------------------------------------------------------------------
    # internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _optimization_subclass(variables: list[Any]) -> ProblemClass:
        types = {v.type for v in variables}
        if types and types == {VariableType.BINARY}:
            return ProblemClass.BINARY_OPTIMIZATION
        if any(v.type is VariableType.CONTINUOUS for v in variables):
            return ProblemClass.CONTINUOUS_OPTIMIZATION
        if any(v.type is VariableType.INTEGER for v in variables):
            return ProblemClass.INTEGER_OPTIMIZATION
        return ProblemClass.CONSTRAINT_OPTIMIZATION


__all__ = [
    "ProblemClass",
    "ClassificationResult",
    "ProblemClassifier",
]
