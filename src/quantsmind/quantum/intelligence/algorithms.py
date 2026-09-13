"""QMQ-03 algorithm domain model.

An :class:`AlgorithmDescriptor` is a *description* of an algorithm that
QuantsMind Quantum knows how to talk about.  Describing an algorithm does
**not** mean QuantsMind implements it: computation is always delegated to
MicroQuantum (or to the QMQ-02 classical baseline).  The descriptor records
which problem classes, formulations and strategies an algorithm suits, and
what capability the environment must provide for it to be executable.

:class:`AlgorithmAvailability` keeps the three-level availability contract
explicit:

* ``architecture_supported`` — QuantsMind Quantum has a descriptor for it.
* ``available_in_microquantum`` — the installed MicroQuantum exposes it.
* ``currently_executable`` — it can run in this environment right now.

An :class:`AlgorithmRecommendation` is a scored, rule-based suggestion
(never a measured confidence) together with executable fallbacks.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any, Self

from quantsmind.quantum.strategy.strategy import ComputationStrategy

if TYPE_CHECKING:
    from quantsmind.quantum.intelligence.capabilities import CapabilityModel


class AlgorithmCategory(Enum):
    """High-level family an algorithm belongs to."""

    OPTIMIZATION = "optimization"
    VARIATIONAL = "variational"
    SEARCH = "search"
    SIMULATION = "simulation"
    MACHINE_LEARNING = "machine_learning"
    LINEAR_ALGEBRA = "linear_algebra"
    SAMPLING = "sampling"
    GRAPH = "graph"
    CLASSICAL = "classical"

    @classmethod
    def parse(cls, value: Any) -> AlgorithmCategory:
        """Coerce a label or member to an :class:`AlgorithmCategory`."""
        if isinstance(value, cls):
            return value
        text = str(value).strip().lower().replace("-", "_").replace(" ", "_")
        for member in cls:
            if member.name.lower() == text or member.value == text:
                return member
        raise ValueError(f"unknown algorithm category {value!r}")


@dataclass(frozen=True)
class AlgorithmDescriptor:
    """Structural description of an algorithm known to QuantsMind Quantum.

    Args:
        name: Canonical id (e.g. ``"qaoa"``).
        label: Human-readable label (e.g. ``"QAOA"``).
        category: High-level algorithm family.
        description: What the algorithm does.
        problem_classes: Problem-class labels the algorithm suits.
        formulations: Formulation kinds the algorithm consumes.
        strategies: Strategies the algorithm participates in.
        execution_modes: How the algorithm is executed (e.g. ``"vqe_loop"``).
        microquantum_identifier: Public MicroQuantum class name, or ``None``
            for non-quantum algorithms (e.g. the classical baseline).
        required_capabilities: Capability names that must be available for
            the algorithm to run (e.g. ``"qaoa_available"``).
        min_variables: Minimum useful problem size (inclusive).
        max_variables: Maximum useful problem size (inclusive).
        metadata: Free-form metadata.
    """

    name: str
    label: str
    category: AlgorithmCategory
    description: str
    problem_classes: tuple[str, ...] = ()
    formulations: tuple[str, ...] = ()
    strategies: tuple[ComputationStrategy, ...] = ()
    execution_modes: tuple[str, ...] = ()
    microquantum_identifier: str | None = None
    required_capabilities: tuple[str, ...] = ()
    min_variables: int | None = None
    max_variables: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("algorithm name must be a non-empty string")
        if isinstance(self.category, str):
            object.__setattr__(self, "category", AlgorithmCategory.parse(self.category))

    @property
    def category_label(self) -> str:
        """Serialized category label (e.g. ``"optimization"``)."""
        return self.category.value

    def matches(
        self,
        *,
        problem_class: str | None = None,
        formulation: str | None = None,
        strategy: ComputationStrategy | None = None,
    ) -> bool:
        """Return whether this descriptor is applicable to the given signals.

        Only constraints that are provided are checked; unknown signals are
        not grounds for exclusion.
        """
        return not (
            (problem_class is not None and problem_class not in self.problem_classes)
            or (formulation is not None and formulation not in self.formulations)
            or (strategy is not None and strategy not in self.strategies)
        )

    def availability(self, capabilities: CapabilityModel) -> AlgorithmAvailability:
        """Compute executive availability against a :class:`CapabilityModel`.

        Classical algorithms are executable when their (classical)
        capabilities are met; quantum algorithms require the corresponding
        MicroQuantum probe to have succeeded.
        """
        available_in_microquantum = self.microquantum_identifier is not None and (
            capabilities.microquantum_installed
            and capabilities.required_caps_met(self.required_capabilities)
        )
        if self.microquantum_identifier is None:
            currently_executable = capabilities.required_caps_met(self.required_capabilities)
        else:
            currently_executable = available_in_microquantum
        return AlgorithmAvailability(
            algorithm=self.name,
            architecture_supported=True,
            available_in_microquantum=available_in_microquantum,
            currently_executable=currently_executable,
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "name": self.name,
            "label": self.label,
            "category": self.category.value,
            "description": self.description,
            "problem_classes": list(self.problem_classes),
            "formulations": list(self.formulations),
            "strategies": [s.name.lower() for s in self.strategies],
            "execution_modes": list(self.execution_modes),
            "microquantum_identifier": self.microquantum_identifier,
            "required_capabilities": list(self.required_capabilities),
            "min_variables": self.min_variables,
            "max_variables": self.max_variables,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Rebuild a descriptor from :meth:`to_dict` output."""
        return cls(
            name=str(data["name"]),
            label=str(data.get("label", data["name"])),
            category=AlgorithmCategory.parse(data.get("category", "optimization")),
            description=str(data.get("description", "")),
            problem_classes=tuple(str(p) for p in data.get("problem_classes", [])),
            formulations=tuple(str(f) for f in data.get("formulations", [])),
            strategies=tuple(ComputationStrategy.parse(s) for s in data.get("strategies", [])),
            execution_modes=tuple(str(m) for m in data.get("execution_modes", [])),
            microquantum_identifier=data.get("microquantum_identifier"),
            required_capabilities=tuple(str(c) for c in data.get("required_capabilities", [])),
            min_variables=data.get("min_variables"),
            max_variables=data.get("max_variables"),
            metadata=dict(data.get("metadata", {})),
        )

    def __repr__(self) -> str:
        return f"AlgorithmDescriptor({self.name!r}, category={self.category.value})"


@dataclass(frozen=True)
class AlgorithmAvailability:
    """Three-level availability of one algorithm.

    Args:
        algorithm: Canonical algorithm id.
        architecture_supported: QuantsMind Quantum has a descriptor for it.
        available_in_microquantum: The installed MicroQuantum exposes it.
        currently_executable: It can run in this environment right now.
    """

    algorithm: str
    architecture_supported: bool
    available_in_microquantum: bool
    currently_executable: bool

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "algorithm": self.algorithm,
            "architecture_supported": self.architecture_supported,
            "available_in_microquantum": self.available_in_microquantum,
            "currently_executable": self.currently_executable,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Rebuild from :meth:`to_dict` output."""
        return cls(
            algorithm=str(data["algorithm"]),
            architecture_supported=bool(data.get("architecture_supported", False)),
            available_in_microquantum=bool(data.get("available_in_microquantum", False)),
            currently_executable=bool(data.get("currently_executable", False)),
        )

    def __repr__(self) -> str:
        return (
            f"AlgorithmAvailability({self.algorithm!r}, "
            f"mq={self.available_in_microquantum}, "
            f"executable={self.currently_executable})"
        )


@dataclass
class AlgorithmRecommendation:
    """A scored, rule-based algorithm recommendation.

    Args:
        algorithm: Recommended canonical algorithm id, or ``None`` when no
            executable algorithm fits.
        suitability_score: Rule-based heuristic score in ``[0, 1]``.  This is
            **not** ML confidence; it reflects how well deterministic rules
            match this problem, formulation and strategy.
        reason: Human-readable, signal-based explanation.
        required_capabilities: Capabilities the recommendation needs.
        expected_input_representation: What the algorithm is handed
            (e.g. ``"IsingModel -> microquantum.OptimizationProblem"``).
        execution_mode: How the algorithm runs (e.g. ``"vqe_loop"``).
        fallbacks: Executable fallback recommendations (never the only path
            when a primary is unavailable).
        capabilities: Snapshot of the capability flags considered.
        user_requested: True when the algorithm was explicitly requested.
        metadata: Free-form metadata (e.g. ``requested_algorithm`` when a
            fallback was applied).
    """

    algorithm: str | None
    suitability_score: float
    reason: str
    required_capabilities: list[str] = field(default_factory=list)
    expected_input_representation: str = ""
    execution_mode: str = ""
    fallbacks: list[AlgorithmRecommendation] = field(default_factory=list)
    capabilities: dict[str, bool] = field(default_factory=dict)
    user_requested: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "algorithm": self.algorithm,
            "suitability_score": self.suitability_score,
            "reason": self.reason,
            "required_capabilities": list(self.required_capabilities),
            "expected_input_representation": self.expected_input_representation,
            "execution_mode": self.execution_mode,
            "fallbacks": [fallback.to_dict() for fallback in self.fallbacks],
            "capabilities": dict(self.capabilities),
            "user_requested": self.user_requested,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Rebuild a recommendation from :meth:`to_dict` output."""
        return cls(
            algorithm=data.get("algorithm"),
            suitability_score=float(data.get("suitability_score", 0.0)),
            reason=str(data.get("reason", "")),
            required_capabilities=[str(c) for c in data.get("required_capabilities", [])],
            expected_input_representation=str(data.get("expected_input_representation", "")),
            execution_mode=str(data.get("execution_mode", "")),
            fallbacks=[cls.from_dict(fallback) for fallback in data.get("fallbacks", [])],
            capabilities={str(k): bool(v) for k, v in data.get("capabilities", {}).items()},
            user_requested=bool(data.get("user_requested", False)),
            metadata=dict(data.get("metadata", {})),
        )

    def __repr__(self) -> str:
        return (
            f"AlgorithmRecommendation(algorithm={self.algorithm!r}, "
            f"score={self.suitability_score}, "
            f"fallbacks={[f.algorithm for f in self.fallbacks]})"
        )


__all__ = [
    "AlgorithmCategory",
    "AlgorithmDescriptor",
    "AlgorithmAvailability",
    "AlgorithmRecommendation",
]
