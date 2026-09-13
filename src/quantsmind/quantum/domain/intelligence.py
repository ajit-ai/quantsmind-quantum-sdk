"""Domain intelligence orchestrator (QMQ-11 §9).

:class:`DomainIntelligence` is the public, domain-agnostic entry point.  It
dispatches a problem to its registered :class:`DomainBinding`, then walks it
through the existing QMQ-03 pipeline (assess) or executes it through the
per-domain optimizer (solve / benchmark).  All decisions and execution facts
are inspectable and serializable.
"""

from __future__ import annotations

from typing import Any

from quantsmind.quantum.domain.assessment import ProblemAssessment, assess_problem
from quantsmind.quantum.domain.errors import DomainDispatchError
from quantsmind.quantum.domain.plan import ExecutionPlan
from quantsmind.quantum.domain.registry import DomainRegistry
from quantsmind.quantum.domain.result import DomainRunResult, result_from_domain_result
from quantsmind.quantum.domain.suitability import QuantumSuitabilityAssessor
from quantsmind.quantum.intelligence.capabilities import CapabilityModel

__all__ = ["DomainIntelligence"]


class DomainIntelligence:
    """Cross-domain assessment, planning, solving and benchmarking.

    Args:
        registry: Dispatch registry; defaults to a fresh
            :class:`DomainRegistry` with the four built-in domains.
        assessor: :class:`QuantumSuitabilityAssessor`; defaulted when omitted.
        interpreter: Interpreter used by :meth:`interpret`; defaulted lazily.
    """

    def __init__(
        self,
        *,
        registry: DomainRegistry | None = None,
        assessor: QuantumSuitabilityAssessor | None = None,
        interpreter: Any | None = None,
    ) -> None:
        self.registry = registry or DomainRegistry()
        self.assessor = assessor or QuantumSuitabilityAssessor()
        self.interpreter = interpreter

    # ------------------------------------------------------------------
    # assessment & planning (no execution)
    # ------------------------------------------------------------------

    def assess(
        self,
        problem: Any,
        *,
        strategy: str | None = None,
        capabilities: CapabilityModel | None = None,
    ) -> ProblemAssessment:
        """Assess a domain problem (classify/formulate/strategy/algorithm/
        suitability) without executing anything."""
        return assess_problem(
            problem,
            self.registry,
            strategy=strategy,
            capabilities=capabilities,
        )

    def plan(
        self,
        problem: Any,
        *,
        strategy: str | None = None,
        capabilities: CapabilityModel | None = None,
    ) -> ExecutionPlan:
        """Build an inspectable :class:`ExecutionPlan` for a problem.

        The plan can be inspected before any execution happens; no quantum
        work is performed by planning itself.
        """
        assessment = self.assess(problem, strategy=strategy, capabilities=capabilities)
        plan = assessment.computation_plan
        if plan is None:
            raise DomainDispatchError(
                f"cannot plan {type(problem).__name__} problem "
                f"{getattr(problem, 'name', type(problem).__name__)!r}: "
                "no computation plan could be built",
                problem=problem,
            )
        suitability = assessment.suitability or self.assessor.assess_unknown(
            problem_name=getattr(problem, "name", type(problem).__name__)
        )
        return ExecutionPlan(
            plan=plan,
            domain=assessment.domain or (self.registry.resolve(problem).kind),
            problem_type=assessment.problem_type,
            strategy_requested=strategy or "",
            suitability=suitability,
            classification=plan.problem_class,
            formulation_kind=assessment.formulation_kind or plan.formulation,
            reasons=list(assessment.reasons),
            provenance={
                "module": "quantsmind.quantum.domain.intelligence",
                "method": "plan",
            },
            metadata={"requested_strategy": strategy or ""},
        )

    # ------------------------------------------------------------------
    # execution (solve / benchmark)
    # ------------------------------------------------------------------

    def solve(
        self,
        problem: Any,
        *,
        strategy: str | None = None,
        config: Any | None = None,
    ) -> DomainRunResult:
        """Solve a domain problem through its registered optimizer.

        The result is wrapped in a :class:`DomainRunResult` with the honest
        strategy/algorithm/backend/execution-mode facts and the QMQ-06
        interpretation.

        Raises:
            UnsupportedDomainError: When no domain binding matches.
        """
        binding = self.registry.resolve(problem)
        strategy_requested = strategy
        provenance = {
            "module": "quantsmind.quantum.domain.intelligence",
            "method": "solve",
        }
        metadata: dict[str, Any] = {}
        if config is not None and hasattr(config, "to_dict"):
            metadata["config"] = config.to_dict()
        domain_result = binding.solve(problem, strategy=strategy_requested, config=config)
        return result_from_domain_result(
            domain_result,
            problem,
            binding,
            kind="solve",
            strategy_requested=strategy_requested,
            provenance=provenance,
            metadata=metadata,
        )

    def benchmark(
        self,
        problem: Any,
        *,
        strategy: str | None = None,
        known_optimum: float | None = None,
        runs: int = 1,
        raise_on_error: bool = False,
        config: Any | None = None,
    ) -> DomainRunResult:
        """Benchmark a domain problem against the classical baseline (QMQ-05)."""
        binding = self.registry.resolve(problem)
        provenance = {
            "module": "quantsmind.quantum.domain.intelligence",
            "method": "benchmark",
        }
        metadata: dict[str, Any] = {
            "known_optimum": known_optimum,
            "runs": int(runs),
        }
        if config is not None and hasattr(config, "to_dict"):
            metadata["config"] = config.to_dict()
        domain_result = binding.benchmark(
            problem,
            strategy=strategy,
            known_optimum=known_optimum,
            runs=runs,
            raise_on_error=raise_on_error,
            config=config,
        )
        return result_from_domain_result(
            domain_result,
            problem,
            binding,
            kind="benchmark",
            strategy_requested=strategy,
            provenance=provenance,
            metadata=metadata,
        )

    # ------------------------------------------------------------------
    # interpretation
    # ------------------------------------------------------------------

    def interpret(self, result: DomainRunResult) -> Any:
        """Return the QMQ-06 interpretation carried by a run result.

        Returns:
            The :class:`ResultInterpretation` (QMQ-06) of the run, or raises
            :class:`DomainDispatchError` when no interpretation exists.
        """
        interpretation = getattr(result, "interpretation", None)
        if interpretation is None:
            report = getattr(result, "report", None)
            benchmark = getattr(result, "benchmark", None)
            if self.interpreter is not None and report is not None:
                interpretation = self.interpreter.interpret(report=report, benchmark=benchmark)
        if interpretation is None:
            raise DomainDispatchError(
                f"no QMQ-06 interpretation available for {result.problem_name!r}",
            )
        return interpretation

    def solve_and_interpret(
        self,
        problem: Any,
        *,
        strategy: str | None = None,
        config: Any | None = None,
    ) -> DomainRunResult:
        """Solve and attach the interpretation in a single call.

        The interpretation is already carried by the wrapped result from
        QMQ-06; this method only validates that it is present.
        """
        result = self.solve(problem, strategy=strategy, config=config)
        self.interpret(result)
        return result

    # ------------------------------------------------------------------
    # introspection
    # ------------------------------------------------------------------

    def supported_domains(self) -> list[str]:
        """Serialized labels of the registered domains."""
        return [domain.value for domain in self.registry.domains()]

    def is_supported(self, problem: Any) -> bool:
        """True when a domain binding matches the problem."""
        return self.registry.is_registered(problem)
