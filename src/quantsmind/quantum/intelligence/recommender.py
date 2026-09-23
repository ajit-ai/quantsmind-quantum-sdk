"""QMQ-03 formulation recommendation and rule-based algorithm selection.

Two responsibilities live here:

* :class:`FormulationRecommender` — decides *which formulation kind* a
  problem should use.  It deliberately does **not** force everything into
  QUBO (QMQ-03 §6): QUBO is recommended only for binary problems, Ising is
  offered as an alternative, graph/simulation/ML/statistical problems keep
  their native formulations.

* :class:`AlgorithmSelector` — turns a classified problem, an accepted
  formulation and a strategy into an :class:`AlgorithmRecommendation` using
  **deterministic rule-based heuristics**.  Scores are documented suitability
  scores, not ML confidence, and the selector never presents an unavailable
  algorithm as the only path: an executable fallback is always attached when
  a quantum recommendation cannot run.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Self

from quantsmind.quantum.intelligence.algorithms import AlgorithmDescriptor, AlgorithmRecommendation
from quantsmind.quantum.intelligence.capabilities import CapabilityModel
from quantsmind.quantum.intelligence.classification import (
    ClassificationResult,
    ProblemClass,
)
from quantsmind.quantum.intelligence.registry import AlgorithmRegistry
from quantsmind.quantum.strategy.strategy import ComputationStrategy

if TYPE_CHECKING:
    from quantsmind.quantum.core.problem import QuantumProblem
    from quantsmind.quantum.formulation.mathematical_model import MathematicalModel

# ---------------------------------------------------------------- formulations

_OPTIMIZATION_CLASSES = {
    "binary_optimization",
    "integer_optimization",
    "continuous_optimization",
    "graph_optimization",
    "constraint_optimization",
}


@dataclass
class FormulationAlternative:
    """One alternative formulation the recommender may offer.

    Args:
        kind: Formulation kind label (e.g. ``"ising"``, ``"qubo"``).
        reason: Why this alternative exists and when it should be preferred.
        appropriateness: 0.0–1.0 rule-based fit for this problem.
    """

    kind: str
    reason: str
    appropriateness: float

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "kind": self.kind,
            "reason": self.reason,
            "appropriateness": self.appropriateness,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Rebuild from :meth:`to_dict` output."""
        return cls(
            kind=str(data["kind"]),
            reason=str(data.get("reason", "")),
            appropriateness=float(data.get("appropriateness", 0.0)),
        )

    def __repr__(self) -> str:
        return f"FormulationAlternative({self.kind!r}, fit={self.appropriateness})"


@dataclass
class FormulationRecommendation:
    """Recommended formulation for a problem.

    Args:
        problem_name: Classified problem name.
        classification: Label of the problem class driving the decision.
        primary: Recommended formulation kind (e.g. ``"qubo"``).
        alternatives: Additional executables, with reasons.
        reason: Human-readable explanation of the primary choice.
        metadata: Free-form metadata (rule path, forced flag, ...).
    """

    problem_name: str
    classification: str
    primary: str
    alternatives: list[FormulationAlternative] = field(default_factory=list)
    reason: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_qubo(self) -> bool:
        """True when the primary recommendation is a QUBO formulation."""
        return self.primary == "qubo"

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "problem_name": self.problem_name,
            "classification": self.classification,
            "primary": self.primary,
            "alternatives": [alt.to_dict() for alt in self.alternatives],
            "reason": self.reason,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Rebuild from :meth:`to_dict` output."""
        return cls(
            problem_name=str(data.get("problem_name", "")),
            classification=str(data.get("classification", "unknown")),
            primary=str(data.get("primary", "optimization")),
            alternatives=[
                FormulationAlternative.from_dict(alt) for alt in data.get("alternatives", [])
            ],
            reason=str(data.get("reason", "")),
            metadata=dict(data.get("metadata", {})),
        )

    def __repr__(self) -> str:
        return (
            f"FormulationRecommendation({self.problem_name!r} -> "
            f"{self.primary} for {self.classification})"
        )


class FormulationRecommender:
    """Rule-based formulation-kind recommender (QMQ-03 §6).

    The evaluator is purely structural: it reads the problem class and the
    current formulation, never the mathematical content.

    Args:
        registries: Bundled, unused (kept for extensibility); pass the
            algorithm registry when available.
    """

    def __init__(self, registries: AlgorithmRegistry | None = None) -> None:
        self.registries = registries

    # ------------------------------------------------------------------
    # public API
    # ------------------------------------------------------------------

    def recommend(
        self,
        problem: QuantumProblem,
        formulation: MathematicalModel | None = None,
        strategy: ComputationStrategy | None = None,
        classification: ClassificationResult | ProblemClass | None = None,
        *,
        force_qubo: bool = False,
    ) -> FormulationRecommendation:
        """Recommend a formulation kind for ``problem``.

        Args:
            problem: The domain problem.
            formulation: Optional prebuilt formulation (built on demand).
            strategy: Optional strategy; informs which formulations can be
                consumed.
            classification: Classification result (or just a class) to avoid
                re-classification.
            force_qubo: When True, QUBO is recommended even for
                non-binary problems (recorded in metadata; the caller decides
                whether the problem is actually quantizable).

        Returns:
            FormulationRecommendation: The recommended primary kind and
            alternatives.
        """
        classified = _coerce_classification(classification, problem, formulation)
        label = (
            classified.label if isinstance(classified, ClassificationResult) else classified.value
        )
        reason_parts: list[str] = []
        alternatives: list[FormulationAlternative] = []
        primary = "optimization"
        rule_path: list[str] = []

        could_consume = {strategy} if strategy is not None else set(ComputationStrategy)

        if label == "binary_optimization" or force_qubo:
            primary = "qubo"
            rule_path.append("force_qubo" if force_qubo else "binary->qubo")
            reason_parts.append(
                "binary variables map losslessly to a QUBO; recommend QUBO as the primary encoding"
            )
            alternatives.append(
                FormulationAlternative(
                    kind="ising",
                    reason="Ising (spin ±1) is equivalent to QUBO after a "
                    "linear substitution and may ease annealing on "
                    "certain backends.",
                    appropriateness=0.8,
                )
            )
        elif label == "integer_optimization":
            primary = "optimization"
            rule_path.append("integer->optimization")
            reason_parts.append(
                "integer variables cannot be encoded losslessly in QUBO; "
                "keep the direct optimization formulation"
            )
            alternatives.append(
                FormulationAlternative(
                    kind="qubo",
                    reason="A QUBO is only viable if integers are quantized "
                    "into binary bits; the caller must enable that "
                    "explicitly.",
                    appropriateness=0.4,
                )
            )
        elif label == "continuous_optimization":
            primary = "optimization"
            rule_path.append("continuous->optimization")
            reason_parts.append(
                "continuous problems cannot be mapped losslessly to QUBO; QUBO would lose precision"
            )
        elif label == "graph_optimization":
            primary = "graph"
            rule_path.append("graph->graph")
            reason_parts.append(
                "the formulation already uses a graph model; keep it, and "
                "translate to QUBO only when an optimizer requires it"
            )
            alternatives.append(
                FormulationAlternative(
                    kind="qubo",
                    reason="Graph problems admit a QUBO via edge penalties "
                    "when required by a QUBO-only optimizer.",
                    appropriateness=0.7,
                )
            )
        elif label == "constraint_optimization":
            primary = "optimization"
            rule_path.append("constraint->optimization")
            reason_parts.append(
                "constraints are native to the optimization formulation; QUBO is optional"
            )
            alternatives.append(
                FormulationAlternative(
                    kind="qubo",
                    reason="Feasible only after constraints are encoded as quadratic penalties.",
                    appropriateness=0.5,
                )
            )
        elif label == "simulation":
            primary = "simulation"
            rule_path.append("simulation->simulation")
            reason_parts.append("simulation keeps its Hamiltonian representation")
        elif label == "machine_learning":
            primary = "ml"
            rule_path.append("ml->ml")
            reason_parts.append("machine-learning problems use the ML formulation")
        elif label == "statistical":
            primary = "statistical"
            rule_path.append("statistical->statistical")
            reason_parts.append("statistical problems use the statistical formulation")
        elif label == "search":
            primary = "mathematical"
            rule_path.append("search->mathematical")
            reason_parts.append(
                "search problems are statements over a declared structure, not objectives to encode"
            )
        elif label == "sampling":
            primary = "mathematical"
            rule_path.append("sampling->mathematical")
            reason_parts.append(
                "sampling is a distribution-harvesting problem; use the mathematical formulation"
            )
        elif label == "linear_algebra":
            primary = "mathematical"
            rule_path.append("linear_algebra->mathematical")
            reason_parts.append("linear-algebra problems stay in the mathematical formulation")
        elif label == "unknown":
            primary = formulation.kind if formulation is not None else "mathematical"
            rule_path.append("unknown->default")
            reason_parts.append("no structural signal; kept the current formulation")

        return FormulationRecommendation(
            problem_name=problem.name,
            classification=label,
            primary=primary,
            alternatives=alternatives,
            reason="; ".join(reason_parts),
            metadata={
                "rule_path": rule_path,
                "could_consume": sorted(c.value for c in could_consume),
                "strategy": strategy.value if strategy is not None else None,
                "original_formulation": (formulation.kind if formulation is not None else None),
            },
        )


# ---------------------------------------------------------------- selection


class AlgorithmSelectionError(ValueError):
    """Raised when no rule can select an algorithm for the inputs."""

    def __init__(self, message: str, *, signals: dict[str, Any] | None = None) -> None:
        self.signals = signals or {}
        super().__init__(message)


def _coerce_classification(
    classification: ClassificationResult | ProblemClass | None,
    problem: QuantumProblem,
    formulation: MathematicalModel | None = None,
) -> ClassificationResult | ProblemClass:
    if classification is not None:
        return classification
    from quantsmind.quantum.intelligence.classification import ProblemClassifier

    return ProblemClassifier().classify(problem, formulation=formulation)


def _coerce_class_label(
    classification: ClassificationResult | ProblemClass,
) -> str:
    if isinstance(classification, ClassificationResult):
        return classification.label
    return classification.value


def _formulation_kind(
    formulation: MathematicalModel | None,
    classification_label: str,
) -> str:
    """Resolve the formulation kind to match against.

    Uses the given formulation, else the kind the class implies (so a binary
    problem without an explicit QUBO still matches QUBO-consuming
    algorithms).
    """
    if formulation is not None:
        return formulation.kind
    implied = {
        "binary_optimization": "qubo",
        "integer_optimization": "optimization",
        "continuous_optimization": "optimization",
        "constraint_optimization": "optimization",
        "graph_optimization": "graph",
        "simulation": "simulation",
        "machine_learning": "ml",
        "statistical": "statistical",
        "search": "mathematical",
        "sampling": "mathematical",
        "linear_algebra": "mathematical",
    }
    return implied.get(classification_label, "unknown")


# Candidate chains: ordered preference per problem class, at most two levels
# of fallback, the last always the classical baseline for optimization.
# The first tuple is the quantum-leaning chain; the optional second is the
# hybrid chain (classical comparison follows the quantum step).
_CANDIDATE_CHAINS: dict[str, tuple[tuple[str, ...], ...]] = {
    "binary_optimization": (
        ("qaoa", "vqe", "vqd", "adapt_vqe", "exhaustive"),
        ("qaoa", "vqe", "exhaustive"),
    ),
    "integer_optimization": (("qaoa", "vqe", "vqd", "adapt_vqe", "exhaustive"),),
    "continuous_optimization": (("qaoa", "vqe", "vqd", "adapt_vqe", "exhaustive"),),
    "graph_optimization": (("qaoa", "vqe", "vqd", "adapt_vqe", "exhaustive"),),
    "constraint_optimization": (("qaoa", "vqe", "vqd", "adapt_vqe", "exhaustive"),),
    "search": (("grover", "deutsch_jozsa", "bernstein_vazirani", "qft"),),
    "sampling": (("amplitude_estimation", "qft", "grover"),),
    "simulation": (
        (
            "hamiltonian_simulation",
            "vqe",
            "continuous_quantum_walk",
            "discrete_quantum_walk",
        ),
    ),
    "machine_learning": (("qml",),),
    "statistical": (("amplitude_estimation",),),
    "linear_algebra": (("hhl", "qft"),),
    "unknown": (),
}

_DEFAULT_SCORES = {
    "qaoa": 0.9,
    "vqe": 0.7,
    "vqd": 0.6,
    "adapt_vqe": 0.6,
    "grover": 0.9,
    "deutsch_jozsa": 0.65,
    "bernstein_vazirani": 0.6,
    "qft": 0.6,
    "hhl": 0.8,
    "phase_estimation": 0.7,
    "hamiltonian_simulation": 0.8,
    "continuous_quantum_walk": 0.7,
    "discrete_quantum_walk": 0.6,
    "amplitude_estimation": 0.8,
    "qml": 0.8,
    "shor": 0.7,
    "exhaustive": 0.9,
}

_QUANTUM_STRATEGIES = (ComputationStrategy.QUANTUM, ComputationStrategy.HYBRID)


class AlgorithmSelector:
    """Deterministic rule-based algorithm selector (QMQ-03 §8–§10).

    Args:
        registry: Algorithm registry (defaults to the standard catalog).
    """

    def __init__(
        self,
        registry: AlgorithmRegistry | None = None,
        formulation_recommender: FormulationRecommender | None = None,
    ) -> None:
        self.registry = registry or AlgorithmRegistry()
        self.formulation_recommender = formulation_recommender or FormulationRecommender(
            registries=registry
        )
        # The most recent formulation recommendation produced by select().
        self.formulation_recommendation: FormulationRecommendation | None = None

    # ------------------------------------------------------------------
    # public API
    # ------------------------------------------------------------------

    def select(
        self,
        problem: QuantumProblem,
        formulation: MathematicalModel | None = None,
        strategy: ComputationStrategy | str | None = None,
        classification: ClassificationResult | ProblemClass | None = None,
        capabilities: CapabilityModel | None = None,
        requested_algorithm: str | None = None,
        *,
        allow_fallback: bool = False,
    ) -> AlgorithmRecommendation:
        """Select an algorithm, or raise when no rule applies.

        Args:
            problem: The domain problem.
            formulation: The chosen formulation (defaults to the problem's).
            strategy: The chosen :class:`ComputationStrategy`.
            classification: Classification result; re-classified if omitted.
            capabilities: Capability snapshot; auto-detected if omitted.
            requested_algorithm: Optional explicit algorithm id.
            allow_fallback: If True and the requested algorithm is not
                executable, an executable replacement is selected and
                recorded.  A requested algorithm is never silently replaced:
                the fallback is always marked in ``metadata``.

        Returns:
            AlgorithmRecommendation: A scored recommendation with an
            executable fallback chain.

        Raises:
            AlgorithmSelectionError: When the request is impossible (unknown
                requested algorithm, or - without ``allow_fallback`` - an
                unavailable requested algorithm).
        """
        model = formulation or problem.formulation
        classified = _coerce_classification(classification, problem, model)
        label = _coerce_class_label(classified)
        capabilities = capabilities or CapabilityModel.detect()
        resolved_strategy = self._resolve_strategy(strategy)
        if resolved_strategy is ComputationStrategy.AUTO:
            # AUTO means "choose for me": prefer the quantum path when the
            # environment can execute it, otherwise stay classical (QMQ-03
            # §17, and identical to the QMQ-01 legacy AUTO policy).
            resolved_strategy = (
                ComputationStrategy.QUANTUM
                if capabilities.quantum_execution_enabled
                else ComputationStrategy.CLASSICAL
            )

        recommended = self.formulation_recommender.recommend(
            problem,
            model,
            strategy=resolved_strategy,
            classification=classified,
        )
        self.formulation_recommendation = recommended

        # Match algorithms against the formulation the pipeline will
        # actually hand them: use the provided qubo/ising model when present,
        # otherwise the formulation the recommender picked for this class.
        if model is not None and model.kind in ("qubo", "ising"):
            matching_kind = model.kind
        else:
            matching_kind = recommended.primary
        formulation_kind = _formulation_kind(model, label)

        if requested_algorithm is not None:
            return self._select_requested(
                requested_algorithm,
                problem=problem,
                label=label,
                formulation_kind=formulation_kind,
                strategy=resolved_strategy,
                capabilities=capabilities,
                allow_fallback=allow_fallback,
            )

        chain = _candidate_chain_for(label, resolved_strategy)
        if not chain:
            reason = (
                f"no algorithm rule applies to problem {problem.name!r} "
                f"(class={label!r}, strategy={resolved_strategy.value!r}); "
                f"problem cannot be routed to an algorithm"
            )
            return AlgorithmRecommendation(
                algorithm=None,
                suitability_score=0.0,
                reason=reason,
                capabilities=capabilities.capability_flags(),
                metadata={"rule_path": ["no-candidate-chain"]},
            )

        recommendation = self._best_executable(
            candidates=chain,
            problem=problem,
            label=label,
            formulation_kind=matching_kind,
            strategy=resolved_strategy,
            capabilities=capabilities,
            requested_algorithm=None,
        )
        recommendation.metadata["matching_kind"] = matching_kind
        return recommendation

    # ------------------------------------------------------------------
    # internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _resolve_strategy(
        strategy: ComputationStrategy | str | None,
    ) -> ComputationStrategy:
        if strategy is None:
            return ComputationStrategy.AUTO
        if isinstance(strategy, ComputationStrategy):
            return strategy
        return ComputationStrategy.parse(strategy)

    @staticmethod
    def _matches_descriptor(
        descriptor: AlgorithmDescriptor,
        *,
        label: str,
        formulation_kind: str,
        strategy: ComputationStrategy,
    ) -> bool:
        """Descriptor compatibility under a (possibly quantum) strategy.

        The classical baseline is allowed to match a QUANTUM/HYBRID strategy:
        an executable classical fallback is exactly the point of QMQ-03 §10.
        """
        if not descriptor.matches(problem_class=label, formulation=formulation_kind):
            return False
        if strategy in _QUANTUM_STRATEGIES:
            return True
        return descriptor.matches(strategy=strategy)

    def _known_matching_algorithms(
        self,
        label: str,
        formulation_kind: str,
        chain: tuple[str, ...],
        strategy: ComputationStrategy,
    ) -> list[AlgorithmDescriptor]:
        """Known descriptors in ``chain`` matching the problem, formulation
        and strategy.

        Primary selection is strict about the strategy: under QUANTUM/HYBRID
        the classical baseline is *not* a primary candidate (a quantum
        recommendation must never silently become a classical one); it only
        appears as an executable fallback.
        """
        result = []
        for algorithm_id in chain:
            if algorithm_id in self.registry:
                descriptor = self.registry.get(algorithm_id)
                if descriptor.matches(
                    problem_class=label,
                    formulation=formulation_kind,
                    strategy=strategy,
                ):
                    result.append(descriptor)
        return result

    def _best_executable(
        self,
        *,
        candidates: tuple[str, ...],
        problem: QuantumProblem,
        label: str,
        formulation_kind: str,
        strategy: ComputationStrategy,
        capabilities: CapabilityModel,
        requested_algorithm: str | None,
    ) -> AlgorithmRecommendation:
        matching = self._known_matching_algorithms(label, formulation_kind, candidates, strategy)
        executable = [
            descriptor
            for descriptor in matching
            if descriptor.availability(capabilities).currently_executable
        ]
        fallbacks = self._build_fallbacks(
            chain=candidates,
            label=label,
            formulation_kind=formulation_kind,
            strategy=strategy,
            capabilities=capabilities,
            exclude=None,
            depth=0,
        )
        known_unavailable = [
            descriptor
            for descriptor in matching
            if not descriptor.availability(capabilities).currently_executable
        ]

        if not executable:
            if known_unavailable:
                primary_id = known_unavailable[0].name
                return AlgorithmRecommendation(
                    algorithm=None,
                    suitability_score=0.0,
                    reason=(
                        f"{primary_id!r} is the right kind of algorithm for "
                        f"{label} with a {formulation_kind} formulation and "
                        f"strategy {strategy.value!r}, but it is not "
                        f"executable here.  Execution must stay classical."
                    ),
                    capabilities=capabilities.capability_flags(),
                    metadata={
                        "recommended_but_unavailable": primary_id,
                        "rule_path": ["recommended-but-unavailable"],
                    },
                    fallbacks=fallbacks,
                )
            return AlgorithmRecommendation(
                algorithm=None,
                suitability_score=0.0,
                reason=(
                    f"no executable algorithm matches {label} with a "
                    f"{formulation_kind} formulation under strategy "
                    f"{strategy.value!r}"
                ),
                capabilities=capabilities.capability_flags(),
                metadata={"rule_path": ["no-executable-algorithm"]},
                fallbacks=fallbacks,
            )

        descriptor = executable[0]
        fallbacks = [fallback for fallback in fallbacks if fallback.algorithm != descriptor.name]
        return AlgorithmRecommendation(
            algorithm=descriptor.name,
            suitability_score=_DEFAULT_SCORES.get(descriptor.name, 0.5),
            reason=self._reason(
                descriptor=descriptor,
                label=label,
                formulation_kind=formulation_kind,
                strategy=strategy,
                capabilities=capabilities,
                user_requested=requested_algorithm is not None,
            ),
            required_capabilities=list(descriptor.required_capabilities),
            expected_input_representation=_expected_input(descriptor.name),
            execution_mode=(descriptor.execution_modes[0] if descriptor.execution_modes else ""),
            fallbacks=fallbacks,
            capabilities=capabilities.capability_flags(),
            user_requested=requested_algorithm is not None,
            metadata={
                "rule_path": ["rule-based-selection"],
                "formulation_kind": formulation_kind,
            },
        )

    def _build_fallbacks(
        self,
        *,
        chain: tuple[str, ...],
        label: str,
        formulation_kind: str,
        strategy: ComputationStrategy,
        capabilities: CapabilityModel,
        exclude: set[str] | None,
        depth: int,
    ) -> list[AlgorithmRecommendation]:
        """Build an executable fallback chain (QMQ-03 §10)."""
        if depth > 2:
            return []
        exclude = set(exclude or set())
        fallbacks: list[AlgorithmRecommendation] = []
        for algorithm_id in chain:
            if algorithm_id in exclude:
                continue
            descriptor = self.registry.get(algorithm_id) if algorithm_id in self.registry else None
            if descriptor is None:
                continue
            if not self._matches_descriptor(
                descriptor,
                label=label,
                formulation_kind=formulation_kind,
                strategy=strategy,
            ):
                continue
            if not descriptor.availability(capabilities).currently_executable:
                continue
            fallbacks.append(
                AlgorithmRecommendation(
                    algorithm=descriptor.name,
                    suitability_score=max(0.4, _DEFAULT_SCORES.get(descriptor.name, 0.5) - 0.2),
                    reason=f"fallback: {descriptor.label} is executable and matches {label}",
                    required_capabilities=list(descriptor.required_capabilities),
                    expected_input_representation=_expected_input(descriptor.name),
                    execution_mode=(
                        descriptor.execution_modes[0] if descriptor.execution_modes else ""
                    ),
                    fallbacks=self._build_fallbacks(
                        chain=chain,
                        label=label,
                        formulation_kind=formulation_kind,
                        strategy=strategy,
                        capabilities=capabilities,
                        exclude=exclude | {descriptor.name},
                        depth=depth + 1,
                    ),
                    capabilities=capabilities.capability_flags(),
                    metadata={"fallback_depth": depth + 1},
                )
            )
        return fallbacks

    def _select_requested(
        self,
        algorithm_id: str,
        *,
        problem: QuantumProblem,
        label: str,
        formulation_kind: str,
        strategy: ComputationStrategy,
        capabilities: CapabilityModel,
        allow_fallback: bool,
    ) -> AlgorithmRecommendation:
        if algorithm_id not in self.registry:
            raise AlgorithmSelectionError(
                f"requested algorithm {algorithm_id!r} is not known to QuantsMind Quantum"
            )
        descriptor = self.registry.get(algorithm_id)
        executable = descriptor.availability(capabilities).currently_executable
        if not executable:
            if not allow_fallback:
                raise AlgorithmSelectionError(
                    f"requested algorithm {algorithm_id!r} is not currently "
                    f"executable (missing capability: "
                    f"{descriptor.required_capabilities or 'unknown'})"
                )
            recommended = self._best_executable(
                candidates=_fallback_chain_for(label, strategy),
                problem=problem,
                label=label,
                formulation_kind=formulation_kind,
                strategy=strategy,
                capabilities=capabilities,
                requested_algorithm=algorithm_id,
            )
            recommended.metadata["requested_algorithm"] = algorithm_id
            recommended.metadata["fallback_applied"] = True
            recommended.reason = (
                f"requested {algorithm_id!r} cannot run here; fell back to "
                f"executable {recommended.algorithm!r}"
            )
            return recommended

        return AlgorithmRecommendation(
            algorithm=descriptor.name,
            suitability_score=0.95,
            reason=(
                f"algorithm {algorithm_id!r} was explicitly requested for "
                f"{problem.name!r} ({label}, {formulation_kind}) and is "
                f"currently executable"
            ),
            required_capabilities=list(descriptor.required_capabilities),
            expected_input_representation=_expected_input(descriptor.name),
            execution_mode=(descriptor.execution_modes[0] if descriptor.execution_modes else ""),
            fallbacks=self._build_fallbacks(
                chain=(algorithm_id,),
                label=label,
                formulation_kind=formulation_kind,
                strategy=strategy,
                capabilities=capabilities,
                exclude=set(),
                depth=0,
            ),
            capabilities=capabilities.capability_flags(),
            user_requested=True,
            metadata={
                "rule_path": ["user-requested"],
                "formulation_kind": formulation_kind,
            },
        )

    @staticmethod
    def _reason(
        *,
        descriptor: AlgorithmDescriptor,
        label: str,
        formulation_kind: str,
        strategy: ComputationStrategy,
        capabilities: CapabilityModel,
        user_requested: bool,
    ) -> str:
        prefix = "explicitly requested" if user_requested else "rule-based selection"
        if descriptor.name == "exhaustive":
            return (
                f"{prefix}: {descriptor.label} is the classical baseline for "
                f"{label}; strategy {strategy.value!r} routes optimization "
                f"jobs to exhaustive search when quantum execution is not "
                f"engaged"
            )
        available = capabilities.is_available(f"{descriptor.name}_available")
        return (
            f"{prefix}: problem {label} with {formulation_kind} formulation "
            f"under strategy {strategy.value!r} maps to {descriptor.label} "
            f"(microquantum={descriptor.microquantum_identifier!r}, "
            f"available={available})"
        )


def _candidate_chain_for(label: str, strategy: ComputationStrategy) -> tuple[str, ...]:
    chains = _CANDIDATE_CHAINS.get(label, ())
    if not chains:
        return ()
    if strategy is ComputationStrategy.CLASSICAL:
        return ("exhaustive",)
    if strategy is ComputationStrategy.HYBRID and len(chains) > 1:
        return chains[1]
    return chains[0]


def _fallback_chain_for(label: str, strategy: ComputationStrategy) -> tuple[str, ...]:
    """Conservative, classical-leaning chain for permitted fallbacks."""
    if strategy in _QUANTUM_STRATEGIES and label in _OPTIMIZATION_CLASSES:
        return ("exhaustive",) + _CANDIDATE_CHAINS.get(label, ())[0]
    chains = _CANDIDATE_CHAINS.get(label, ())
    return chains[0] if chains else ()


def _expected_input(algorithm_id: str) -> str:
    mapping = {
        "qaoa": "IsingModel -> microquantum.OptimizationProblem (QMQ-02 mapper)",
        "vqe": "IsingModel/Hamiltonian -> microquantum.OptimizationProblem (QMQ-02 mapper)",
        "vqd": "IsingModel/Hamiltonian -> microquantum.OptimizationProblem (QMQ-02 mapper)",
        "adapt_vqe": "IsingModel/Hamiltonian -> microquantum.OptimizationProblem (QMQ-02 mapper)",
        "grover": "domain oracles -> microquantum.GroverSearch",
        "deutsch_jozsa": "domain oracles -> microquantum.DeutschJozsa",
        "bernstein_vazirani": "domain oracles -> microquantum.BernsteinVazirani",
        "qft": "state preparation -> microquantum.QFT",
        "phase_estimation": "unitary + state -> microquantum.PhaseEstimation",
        "hhl": "linear system -> microquantum.HHL",
        "shor": "k = n-qubit integer -> microquantum.ShorsAlgorithm",
        "amplitude_estimation": "oracle -> microquantum.AmplitudeEstimation",
        "hamiltonian_simulation": "Hamiltonian -> microquantum.HamiltonianSimulation",
        "continuous_quantum_walk": "Hamiltonian -> microquantum.ContinuousQuantumWalk",
        "discrete_quantum_walk": "Hamiltonian -> microquantum.DiscreteQuantumWalk",
        "qml": "ML problem -> microquantum.QuantumKernel",
        "exhaustive": "OptimizationModel -> classical exhaustive executor (QMQ-02)",
    }
    return mapping.get(algorithm_id, f"{algorithm_id} model -> microquantum")


__all__ = [
    "FormulationAlternative",
    "FormulationRecommendation",
    "FormulationRecommender",
    "AlgorithmSelector",
    "AlgorithmSelectionError",
]
