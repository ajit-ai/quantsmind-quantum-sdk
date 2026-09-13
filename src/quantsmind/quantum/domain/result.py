"""Domain-level run result (QMQ-11 §8).

:class:`DomainRunResult` bundles a domain solve/benchmark outcome with the
honest execution facts: the requested strategy, the strategy that was actually
selected and executed, the algorithm, the backend, the execution mode
(``classical`` / ``quantum``), whether a fallback was used, and the QMQ-06
interpretation (which records ``DEGRADED`` when a quantum-capable strategy had
to execute classically).

Composition references (``report``, ``domain_result``) are kept in memory and
serialized only as lightweight references, mirroring QMQ-05.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, Self

from quantsmind.quantum.domain.registry import DomainBinding, DomainKind

if TYPE_CHECKING:
    pass

__all__ = ["DomainRunResult"]


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


@dataclass
class DomainRunResult:
    """Honest, provenance-rich result of a domain solve or benchmark.

    Args:
        problem_name: Name of the solved problem.
        domain: The dispatched :class:`DomainKind`.
        problem_type: Class name of the source domain problem.
        strategy_requested: Strategy the caller requested (``""`` = auto).
        strategy_selected: Strategy selected by QMQ-03 for execution.
        strategy_executed: Strategy that actually produced the outcome (may
            differ from selected after a fallback/degradation).
        algorithm: Algorithm id that ran (``""`` when classical).
        backend: Backend that executed the quantum leg (``""`` otherwise).
        execution_mode: ``"quantum"`` / ``"classical"`` / ``"classical"
            "quantum-inspired"``.
        fallback_used: True when the executed path differed from the
            requested/selected path (honest degradation).
        feasible: Feasibility of the produced solution or ``None``.
        objective_value: Leading objective value or ``None``.
        limitations: Honest list of what did NOT happen (e.g. quantum
            runtime missing).
        interpretation: QMQ-06 structured interpretation (optional).
        report: The QMQ-04 :class:`SolutionReport` (in-memory reference).
        benchmark: QMQ-05 :class:`BenchmarkResult` (in-memory reference).
        domain_result: The per-domain result object (in-memory reference).
        provenance: Where-and-how metadata.
        created_at: ISO-8601 creation timestamp.
        metadata: Free-form metadata.
    """

    problem_name: str
    domain: DomainKind | None = None
    problem_type: str = ""
    strategy_requested: str = ""
    strategy_selected: str = ""
    strategy_executed: str = ""
    algorithm: str = ""
    backend: str = ""
    execution_mode: str = "classical"
    fallback_used: bool = False
    feasible: bool | None = None
    objective_value: float | None = None
    limitations: list[str] = field(default_factory=list)
    interpretation: Any | None = None
    report: Any | None = None
    benchmark: Any | None = None
    domain_result: Any | None = None
    provenance: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=_utc_now)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def domain_label(self) -> str:
        return self.domain.value if self.domain is not None else ""

    def interpretation_status(self) -> str:
        """Serialized QMQ-06 interpretation status (``""`` when absent)."""
        if self.interpretation is not None:
            return str(getattr(self.interpretation, "status", "") or "")
        return ""

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary (reports as references)."""
        report_ref = None
        if self.report is not None:
            report_ref = {
                "problem": str(getattr(self.report, "problem", None) or ""),
                "strategy": (
                    self.report.strategy.name.lower()
                    if getattr(self.report, "strategy", None) is not None
                    else ""
                ),
                "feasible": (
                    self.report.solution.feasible
                    if getattr(getattr(self.report, "solution", None), "feasible", None) is not None
                    else None
                ),
                "selected_leg": getattr(self.report, "selected_leg", None),
                "created_at": getattr(self.report, "created_at", ""),
            }
        benchmark_ref = self.benchmark.to_dict() if self.benchmark is not None else None
        interpretation_ref = (
            self.interpretation.to_dict() if self.interpretation is not None else None
        )
        return {
            "problem_name": self.problem_name,
            "domain": self.domain_label,
            "problem_type": self.problem_type,
            "strategy_requested": self.strategy_requested,
            "strategy_selected": self.strategy_selected,
            "strategy_executed": self.strategy_executed,
            "algorithm": self.algorithm,
            "backend": self.backend,
            "execution_mode": self.execution_mode,
            "fallback_used": bool(self.fallback_used),
            "feasible": self.feasible,
            "objective_value": self.objective_value,
            "limitations": list(self.limitations),
            "report_ref": report_ref,
            "benchmark": benchmark_ref,
            "interpretation": interpretation_ref,
            "provenance": dict(self.provenance),
            "created_at": self.created_at,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Rebuild a result from :meth:`to_dict` output.

        Composition references (``report``, ``domain_result``) are not
        rebuilt; measured facts round-trip exactly.
        """
        from quantsmind.quantum.result.result_interpretation import (
            ResultInterpretation,
        )

        benchmark = data.get("benchmark")
        if benchmark is not None:
            from quantsmind.quantum.benchmark.models import BenchmarkResult

            benchmark = BenchmarkResult.from_dict(dict(benchmark))
        interpretation = data.get("interpretation")
        return cls(
            problem_name=str(data.get("problem_name", "")),
            domain=(DomainKind.parse(str(data["domain"])) if data.get("domain") else None),
            problem_type=str(data.get("problem_type", "")),
            strategy_requested=str(data.get("strategy_requested", "")),
            strategy_selected=str(data.get("strategy_selected", "")),
            strategy_executed=str(data.get("strategy_executed", "")),
            algorithm=str(data.get("algorithm", "")),
            backend=str(data.get("backend", "")),
            execution_mode=str(data.get("execution_mode", "classical")),
            fallback_used=bool(data.get("fallback_used", False)),
            feasible=data.get("feasible"),
            objective_value=data.get("objective_value"),
            limitations=[str(x) for x in data.get("limitations", [])],
            interpretation=(
                ResultInterpretation.from_dict(dict(interpretation))
                if interpretation is not None
                else None
            ),
            report=None,
            benchmark=benchmark,
            domain_result=None,
            provenance=dict(data.get("provenance", {})),
            created_at=str(data.get("created_at", _utc_now())),
            metadata=dict(data.get("metadata", {})),
        )

    def __repr__(self) -> str:
        return (
            f"DomainRunResult({self.problem_name!r} [{self.domain_label}] "
            f"requested={self.strategy_requested or 'auto'} -> "
            f"executed={self.strategy_executed or '?'}/{self.execution_mode}, "
            f"fallback={self.fallback_used})"
        )


def result_from_domain_result(
    domain_result: Any,
    problem: Any,
    binding: DomainBinding | None,
    *,
    kind: str,
    strategy_requested: str | None,
    provenance: dict[str, Any] | None = None,
    metadata: dict[str, Any] | None = None,
) -> DomainRunResult:
    """Wrap a per-domain optimizer result into a :class:`DomainRunResult`.

    Args:
        domain_result: Finance/Portfolio/Data/ML optimizer result.
        problem: The solved domain problem.
        binding: The dispatched :class:`DomainBinding` (for the domain).
        kind: ``"solve"`` or ``"benchmark"``.
        strategy_requested: Explicit requested strategy (``None`` = auto).
        provenance: Optional provenance to attach.
        metadata: Optional free-form metadata.

    The wrapper reads the honest execution facts from the underlying
    :class:`SolutionReport` and the QMQ-06 :class:`ResultInterpretation`, so
    it never invents a quantum claim.
    """
    report = getattr(domain_result, "report", None)
    benchmark = getattr(domain_result, "benchmark", None)
    interpretation = getattr(domain_result, "interpretation", None)
    solution = getattr(domain_result, "solution", None)

    strategy_selected = _report_strategy(report)
    strategy_executed, execution_mode = _executed_facts(interpretation, report)
    algorithm = _interpretation_algorithm(interpretation)
    backend = _interpretation_backend(interpretation)
    status = str(getattr(interpretation, "status", "") or "")
    fallback_used = _fallback_used(strategy_requested, strategy_executed, status)
    limitations = _limitations(strategy_requested, strategy_executed, execution_mode, status)

    problem_name = getattr(problem, "name", type(problem).__name__)
    provenance = dict(provenance or {})
    provenance.setdefault("module", "quantsmind.quantum.domain.result")
    provenance.setdefault("kind", kind)
    if binding is not None:
        provenance.setdefault("domain_binding", binding.label)

    return DomainRunResult(
        problem_name=problem_name,
        domain=binding.kind if binding is not None else None,
        problem_type=type(problem).__name__,
        strategy_requested=strategy_requested or "",
        strategy_selected=strategy_selected,
        strategy_executed=strategy_executed or strategy_selected,
        algorithm=algorithm,
        backend=backend,
        execution_mode=execution_mode,
        fallback_used=fallback_used,
        feasible=_solution_feasible(solution, report),
        objective_value=_solution_value(solution),
        limitations=limitations,
        interpretation=interpretation,
        report=report,
        benchmark=benchmark,
        domain_result=domain_result,
        provenance=provenance,
        metadata=dict(metadata or {}),
    )


def _report_strategy(report: Any) -> str:
    strategy = getattr(report, "strategy", None)
    if strategy is None:
        return ""
    return strategy.name.lower() if hasattr(strategy, "name") else str(strategy).strip().lower()


def _executed_facts(interpretation: Any, report: Any) -> tuple[str, str]:
    """Extract executed strategy and execution mode honestly.

    Prefers the QMQ-06 strategy section; falls back to the report's selected
    leg when no interpretation is available.
    """
    selected_leg = None
    strategy_section = getattr(interpretation, "strategy", None)
    if strategy_section is not None:
        selected_leg = getattr(strategy_section, "selected_leg", None)
        actual = getattr(strategy_section, "actual_strategy", None)
        if actual:
            return str(actual), _mode_for_leg(str(selected_leg) if selected_leg else actual)
    selected_leg = selected_leg or getattr(report, "selected_leg", None)
    mode = _mode_for_leg(selected_leg) if selected_leg else "classical"
    return "", mode


def _mode_for_leg(leg: str) -> str:
    text = str(leg).strip().lower()
    if text == "quantum":
        return "quantum"
    if "quantum_inspired" in text or "inspired" in text:
        return "classical/quantum-inspired"
    return "classical"


def _interpretation_algorithm(interpretation: Any) -> str:
    algorithm = getattr(getattr(interpretation, "algorithm", None), "algorithm", "")
    return str(algorithm or "").strip()


def _interpretation_backend(interpretation: Any) -> str:
    backend = getattr(getattr(interpretation, "algorithm", None), "backend", "")
    return str(backend or "").strip()


def _fallback_used(strategy_requested: str | None, executed: str, status: str) -> bool:
    if status.lower() == "degraded":
        return True
    requested = (strategy_requested or "").strip().lower()
    executed = (executed or "").strip().lower()
    if not (requested and executed):
        return False
    return requested != "auto" and requested != executed


def _limitations(
    strategy_requested: str | None,
    executed: str,
    execution_mode: str,
    status: str,
) -> list[str]:
    limitations: list[str] = []
    requested = (strategy_requested or "").strip().lower()
    if requested and requested not in ("", "auto", executed.strip().lower()):
        limitations.append(
            f"requested strategy {requested!r} did not execute; ran {executed or 'classical'}"
        )
    if status.lower() == "degraded":
        limitations.append(
            "QMQ-06 reports the run DEGRADED (quantum-capable strategy executed on a fallback path)"
        )
    if execution_mode in ("classical", "classical/quantum-inspired"):
        limitations.append(f"no quantum execution happened in this run (mode={execution_mode})")
    return limitations


def _solution_feasible(solution: Any, report: Any) -> bool | None:
    if solution is not None and getattr(solution, "feasible", None) is not None:
        return bool(solution.feasible)
    solution_report = getattr(report, "solution", None)
    if solution_report is not None and getattr(solution_report, "feasible", None) is not None:
        return bool(solution_report.feasible)
    return None


def _solution_value(solution: Any) -> float | None:
    if solution is None:
        return None
    value = getattr(solution, "objective_value", None)
    if value is None:
        value = getattr(solution, "score", None)
    return float(value) if value is not None else None
