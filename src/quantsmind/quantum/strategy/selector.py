"""Deterministic, rule-based strategy selection (QMQ-01).

The :class:`StrategySelector` uses a clear, testable, stateless decision
function to choose a :class:`ComputationStrategy` for a domain problem.
The class is a stable seam: a future learned or advisor-based selector can
replace the ``select`` implementation without callers changing.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, cast

from quantsmind.quantum._mq import microquantum_available
from quantsmind.quantum.intelligence.classification import (
    ClassificationResult,
    ProblemClass,
)
from quantsmind.quantum.strategy.strategy import ComputationStrategy

if TYPE_CHECKING:
    from quantsmind.quantum.core.problem import QuantumProblem
    from quantsmind.quantum.formulation.mathematical_model import MathematicalModel
    from quantsmind.quantum.intelligence.capabilities import CapabilityModel


@dataclass
class StrategyDecision:
    """A strategy selection together with its full rationale (QMQ-03 §7).

    Args:
        strategy: The selected :class:`ComputationStrategy`.
        reasons: Ordered list of human-readable reasons for the decision.
        signals: Structural signals that drove the decision (problem size,
            variable types, formulation kind, capability flags, ...).
        metadata: Free-form metadata (rule path, overrides, ...).
    """

    strategy: ComputationStrategy
    reasons: list[str] = field(default_factory=list)
    signals: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def label(self) -> str:
        """Serialized strategy label (e.g. ``"hybrid"``)."""
        return self.strategy.value

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "strategy": self.label,
            "reasons": list(self.reasons),
            "signals": dict(self.signals),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> StrategyDecision:
        """Rebuild a decision from :meth:`to_dict` output."""
        return cls(
            strategy=ComputationStrategy.parse(data.get("strategy", "classical")),
            reasons=[str(r) for r in data.get("reasons", [])],
            signals=dict(data.get("signals", {})),
            metadata=dict(data.get("metadata", {})),
        )

    def __repr__(self) -> str:
        return f"StrategyDecision({self.label!r})"


class StrategySelector:
    """Selects a :class:`ComputationStrategy` for a domain problem.

    Selection rules (QMQ-01, fully deterministic):

    1. An explicit ``preferred_strategy`` is honoured; if it requires a
       quantum runtime that is unavailable it is downgraded to CLASSICAL.
    2. If no quantum backend is available, the strategy is CLASSICAL.
    3. Otherwise a size-based heuristic applies:

       * ``n <= quantum_attempt_threshold``  ->  HYBRID
         (small problems can run a quantum kernel with classical
         pre/post-processing).
       * ``quantum_attempt_threshold < n <= quantum_inspired_threshold``
         ->  QUANTUM_INSPIRED (too large for a variational circuit with
         a reasonable shot budget, but suitable for classical algorithms
         inspired by quantum mechanics).
       * ``n > quantum_inspired_threshold``
         ->  CLASSICAL (domain pre-processing only).

    A problem can override rule 3 by setting
    ``problem.metadata["quantum_suitable"] = False`` (then CLASSICAL is
    returned).

    Args:
        quantum_attempt_threshold: Problem size at or below which a quantum
            kernel is attempted.
        quantum_inspired_threshold: Problem size at or below which
            QUANTUM_INSPIRED is used.
        quantum_enabled: Master switch allowing quantum-family strategies.
    """

    def __init__(
        self,
        *,
        quantum_attempt_threshold: int = 25,
        quantum_inspired_threshold: int = 500,
        quantum_enabled: bool = True,
    ) -> None:
        if quantum_attempt_threshold < 1:
            raise ValueError("quantum_attempt_threshold must be >= 1")
        if quantum_inspired_threshold < quantum_attempt_threshold:
            raise ValueError("quantum_inspired_threshold must be >= quantum_attempt_threshold")
        self.quantum_attempt_threshold = quantum_attempt_threshold
        self.quantum_inspired_threshold = quantum_inspired_threshold
        self.quantum_enabled = quantum_enabled

    # ------------------------------------------------------------------
    # internal helpers
    # ------------------------------------------------------------------

    def _quantum_possible(
        self,
        *,
        backend_available: bool | None = None,
        available_algorithms: set[str] | None = None,
    ) -> bool:
        """Return True when a quantum strategy can theoretically execute."""
        if not self.quantum_enabled:
            return False
        if backend_available is not None:
            return backend_available
        if available_algorithms is not None and not available_algorithms:
            return False
        return microquantum_available()

    def _quantum_ok(
        self,
        *,
        backend_available: bool | None,
        available_algorithms: set[str] | None,
        capabilities: CapabilityModel | None,
    ) -> bool:
        """Quantum-runtime availability respecting an explicit capability
        snapshot when one is supplied (QMQ-03 path)."""
        if capabilities is not None and backend_available is None and available_algorithms is None:
            return capabilities.quantum_execution_enabled and capabilities.backend_available
        return self._quantum_possible(
            backend_available=backend_available,
            available_algorithms=available_algorithms,
        )

    # ------------------------------------------------------------------
    # public API
    # ------------------------------------------------------------------

    def select(
        self,
        problem: QuantumProblem,
        *,
        backend_available: bool | None = None,
        available_algorithms: set[str] | None = None,
    ) -> ComputationStrategy:
        """Choose a strategy deterministically.

        Args:
            problem: The problem to classify.
            backend_available: If given, overrides the global MicroQuantum
                availability check.
            available_algorithms: If given and empty, forces CLASSICAL.
        """
        preference = problem.preferred_strategy
        if preference is not None and preference is not ComputationStrategy.AUTO:
            if preference.uses_quantum_runtime and not self._quantum_possible(
                backend_available=backend_available,
                available_algorithms=available_algorithms,
            ):
                return ComputationStrategy.CLASSICAL
            return cast(ComputationStrategy, preference)

        if not self._quantum_possible(
            backend_available=backend_available,
            available_algorithms=available_algorithms,
        ):
            return ComputationStrategy.CLASSICAL

        quantum_suitable = bool(problem.metadata.get("quantum_suitable", problem.size > 0))
        if not quantum_suitable:
            return ComputationStrategy.CLASSICAL

        n = problem.size
        if n <= self.quantum_attempt_threshold:
            return ComputationStrategy.HYBRID
        if n <= self.quantum_inspired_threshold:
            return ComputationStrategy.QUANTUM_INSPIRED
        return ComputationStrategy.CLASSICAL

    def select_reasoned(
        self,
        problem: QuantumProblem,
        *,
        backend_available: bool | None = None,
        available_algorithms: set[str] | None = None,
        classification: ClassificationResult | ProblemClass | None = None,
        formulation: MathematicalModel | None = None,
        capabilities: CapabilityModel | None = None,
    ) -> StrategyDecision:
        """Select a strategy with a full, explainable rationale (QMQ-03 §7).

        The decision is made by the same deterministic rules as
        :meth:`select`, but the AUTO path may additionally consider the
        problem class, formulation kind and capability flags when they are
        provided — instead of size alone.  Without those signals the result
        is identical to :meth:`select` (backward compatible).

        Returns:
            StrategyDecision: The selected strategy plus reasons and signals.
        """
        preference = problem.preferred_strategy
        reasons: list[str] = []
        signals: dict[str, Any] = {
            "problem_size": problem.size,
            "n_variables": len(problem.variables),
            "n_constraints": len(problem.constraints),
            "n_objectives": len(problem.objectives),
            "quantum_enabled": self.quantum_enabled,
            "quantum_suitable": bool(problem.metadata.get("quantum_suitable", problem.size > 0)),
            "preferred_strategy": (preference.name.lower() if preference is not None else "auto"),
        }
        if formulation is not None:
            signals["formulation_kind"] = formulation.kind
        if classification is not None:
            signals["problem_class"] = (
                classification.label
                if isinstance(classification, ClassificationResult)
                else classification.value
            )
        if backend_available is not None:
            signals["backend_available"] = backend_available
        if available_algorithms is not None:
            signals["available_algorithms"] = sorted(available_algorithms)

        # Rule 1: an explicit, non-AUTO preference.
        if preference is not None and preference is not ComputationStrategy.AUTO:
            quantum_ok = self._quantum_ok(
                backend_available=backend_available,
                available_algorithms=available_algorithms,
                capabilities=capabilities,
            )
            if preference.uses_quantum_runtime and not quantum_ok:
                reasons.append(
                    f"preferred strategy {preference.value!r} requires a "
                    "quantum runtime, which is unavailable here; "
                    "downgraded to CLASSICAL"
                )
                return StrategyDecision(
                    strategy=ComputationStrategy.CLASSICAL,
                    reasons=reasons,
                    signals=signals,
                    metadata={"rule_path": ["explicit-preference-downgrade"]},
                )
            reasons.append(f"honouring explicit preferred_strategy={preference.value!r}")
            return StrategyDecision(
                strategy=preference,
                reasons=reasons,
                signals=signals,
                metadata={"rule_path": ["explicit-preference"]},
            )

        # Rule 2: no quantum runtime -> CLASSICAL.
        quantum_possible = self._quantum_ok(
            backend_available=backend_available,
            available_algorithms=available_algorithms,
            capabilities=capabilities,
        )
        if not quantum_possible:
            reasons.append(
                "no quantum runtime available (microquantum absent or "
                "quantum disabled); strategy is CLASSICAL"
            )
            return StrategyDecision(
                strategy=ComputationStrategy.CLASSICAL,
                reasons=reasons,
                signals=signals,
                metadata={"rule_path": ["no-quantum-runtime"]},
            )
        reasons.append("quantum runtime available")

        # Rule 3: problem declared unsuitable for quantum -> CLASSICAL.
        quantum_suitable = bool(problem.metadata.get("quantum_suitable", problem.size > 0))
        if not quantum_suitable:
            reasons.append("problem metadata marks quantum_suitable=False; strategy is CLASSICAL")
            return StrategyDecision(
                strategy=ComputationStrategy.CLASSICAL,
                reasons=reasons,
                signals=signals,
                metadata={"rule_path": ["metadata-not-quantum-suitable"]},
            )

        # Rule 4: structural refinement when a class/formulation is known.
        label: str | None = None
        if classification is not None:
            label = (
                classification.label
                if isinstance(classification, ClassificationResult)
                else classification.value
            )

        n = problem.size
        reasoning_path: list[str]
        if label is None or not capabilities:
            strategy, reasoning_path = self._size_strategy(n, quantum_suitable, reasons)
        else:
            strategy, reasoning_path = self._reasoned_auto(
                label=label,
                n=n,
                reasons=reasons,
                signals=signals,
                formulation=formulation,
                capabilities=capabilities,
            )
        return StrategyDecision(
            strategy=strategy,
            reasons=reasons,
            signals=signals,
            metadata={"rule_path": reasoning_path},
        )

    def _size_strategy(
        self,
        n: int,
        quantum_suitable: bool,
        reasons: list[str],
    ) -> tuple[ComputationStrategy, list[str]]:
        """Legacy-compatible size-only AUTO decision (QMQ-01 rules)."""
        if not quantum_suitable:
            return ComputationStrategy.CLASSICAL, ["size:not-quantum-suitable"]
        reasons.append(f"problem_size={n}")
        if n <= self.quantum_attempt_threshold:
            reasons.append(
                f"size {n} <= attempt threshold "
                f"{self.quantum_attempt_threshold}; strategy is HYBRID"
            )
            return ComputationStrategy.HYBRID, ["size:hybrid"]
        if n <= self.quantum_inspired_threshold:
            reasons.append(
                f"size {n} <= inspired threshold "
                f"{self.quantum_inspired_threshold}; strategy is "
                "QUANTUM_INSPIRED (no executor yet: representation only)"
            )
            return ComputationStrategy.QUANTUM_INSPIRED, ["size:quantum-inspired"]
        reasons.append(
            f"size {n} above inspired threshold "
            f"{self.quantum_inspired_threshold}; strategy is CLASSICAL"
        )
        return ComputationStrategy.CLASSICAL, ["size:classical"]

    def _reasoned_auto(
        self,
        *,
        label: str,
        n: int,
        reasons: list[str],
        signals: dict[str, Any],
        formulation: MathematicalModel | None,
        capabilities: CapabilityModel,
    ) -> tuple[ComputationStrategy, list[str]]:
        """Structural AUTO decision (QMQ-03 §7), richer than pure size.

        Keeps legacy size outcomes wherever there is no structure-specific
        reason to diverge, and honours the classical-baseline-first policy:
        a small quantum-compatible problem is routed to HYBRID (classical
        baseline plus quantum comparison), never to bare QUANTUM.
        """
        form_kind = formulation.kind if formulation is not None else None
        signals["formulation_kind"] = form_kind if form_kind is not None else "unknown"

        quantum_capable = capabilities.quantum_execution_enabled and capabilities.backend_available
        size_path: list[str]

        strategy, size_path = self._size_strategy(n, True, reasons)

        # Structure-specific refinements.
        if label == "simulation":
            signals["native_quantum"] = True
            if quantum_capable:
                reasons.append(
                    "simulation problems are naturally quantum; "
                    "strategy is QUANTUM (algorithm: hamiltonian_simulation)"
                )
                return (
                    ComputationStrategy.QUANTUM,
                    ["structure:simulation->quantum"] + size_path,
                )
            reasons.append(
                "simulation has no lossless classical-encoding shortcut; "
                "without a quantum runtime it is not executable"
            )
            return (
                ComputationStrategy.CLASSICAL,
                ["structure:simulation->classical-no-runtime"] + size_path,
            )
        if label == "search":
            reasons.append("search problems map to Grover; strategy is QUANTUM")
            return (
                ComputationStrategy.QUANTUM,
                ["structure:search->quantum"] + size_path,
            )
        if label == "sampling":
            reasons.append("sampling problems map to amplitude estimation; strategy is QUANTUM")
            return (
                ComputationStrategy.QUANTUM,
                ["structure:sampling->quantum"] + size_path,
            )
        if label == "linear_algebra":
            reasons.append("linear-algebra problems map to HHL/QFT; strategy is QUANTUM")
            return (
                ComputationStrategy.QUANTUM,
                ["structure:linear_algebra->quantum"] + size_path,
            )
        if label in ("machine_learning", "statistical"):
            reasons.append(
                f"{label} typically combines classical and quantum steps; strategy is HYBRID"
            )
            return (
                ComputationStrategy.HYBRID,
                [f"structure:{label}->hybrid"] + size_path,
            )
        if label == "continuous_optimization":
            reasons.append(
                "continuous variables have no lossless QUBO encoding; prefer the classical baseline"
            )
            return (
                ComputationStrategy.CLASSICAL,
                ["structure:continuous->classical"] + size_path,
            )
        if label == "integer_optimization":
            reasons.append(
                "integer variables need quantization before QUBO; not a "
                "natural quantum target, prefer classical"
            )
            return (
                ComputationStrategy.CLASSICAL,
                ["structure:integer->classical"] + size_path,
            )
        if label in ("binary_optimization", "graph_optimization", "constraint_optimization"):
            if quantum_capable and n <= self.quantum_attempt_threshold:
                reasons.append(
                    f"{label} is quantum-compatible and a classical baseline "
                    "is available at this size; use HYBRID so the QAOA "
                    "result can be compared against exhaustive search "
                    "(hybrid comparison)"
                )
                return (
                    ComputationStrategy.HYBRID,
                    ["structure:optimization->hybrid"] + size_path,
                )
            if not quantum_capable:
                reasons.append(
                    f"{label} is quantum-compatible but no quantum runtime "
                    "can execute it; strategy is CLASSICAL"
                )
                return (
                    ComputationStrategy.CLASSICAL,
                    ["structure:optimization->classical-no-runtime"] + size_path,
                )
        reasons.append(
            "no structure-specific signal; falling back to size-based "
            f"AUTO decision ({strategy.value})"
        )
        return strategy, ["structure:none"] + size_path

    def explain(
        self,
        problem: QuantumProblem,
        *,
        backend_available: bool | None = None,
        available_algorithms: set[str] | None = None,
    ) -> dict[str, Any]:
        """Return the selected strategy and a human-readable rationale.

        Useful for logging and testing but never consumed by the workflow
        itself.
        """
        strategy = self.select(
            problem,
            backend_available=backend_available,
            available_algorithms=available_algorithms,
        )
        reasons: list[str] = [
            "preferred_strategy="
            f"{problem.preferred_strategy.name if problem.preferred_strategy else 'AUTO'}",
            f"microquantum_available={microquantum_available()}",
            f"quantum_enabled={self.quantum_enabled}",
            f"problem_size={problem.size}",
            f"n_constraints={len(problem.constraints)}",
            f"quantum_suitable={bool(problem.metadata.get('quantum_suitable', problem.size > 0))}",
        ]
        if backend_available is not None:
            reasons.append(f"backend_available={backend_available}")
        if available_algorithms is not None:
            reasons.append(f"available_algorithms={len(available_algorithms)}")
        return {"strategy": strategy, "reason": "; ".join(reasons)}


__all__ = ["StrategySelector", "StrategyDecision"]
