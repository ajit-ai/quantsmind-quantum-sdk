"""Domain-level results of a QuantsMind quantum workflow.

A :class:`SolutionReport` bundles a problem with every artifact produced
during a workflow run: the formulation, the selected strategy, the mapping
record, the execution result (a
:class:`~quantsmind.quantum.circuit_result.QuantumResult`), the domain
solution, its interpretation and provenance.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from quantsmind.quantum.core.problem import QuantumProblem
from quantsmind.quantum.core.solution import ProblemSolution
from quantsmind.quantum.formulation.mathematical_model import MathematicalModel
from quantsmind.quantum.mapping.mapper import MappingResult
from quantsmind.quantum.result.interpretation import Interpretation
from quantsmind.quantum.result.provenance import Provenance
from quantsmind.quantum.strategy.strategy import ComputationStrategy

if TYPE_CHECKING:
    from quantsmind.quantum.benchmark.models import BenchmarkResult
    from quantsmind.quantum.execution.classical import ClassicalExecutionResult
    from quantsmind.quantum.execution.comparison import ExecutionComparison
    from quantsmind.quantum.execution.quantum import QuantumExecutionResult
    from quantsmind.quantum.intelligence.algorithms import AlgorithmRecommendation
    from quantsmind.quantum.intelligence.classification import ClassificationResult
    from quantsmind.quantum.intelligence.plan import ComputationPlan
    from quantsmind.quantum.result.result_interpretation import ResultInterpretation


@dataclass
class SolutionReport:
    """Complete record of one workflow run for a domain problem.

    Args:
        problem: The problem that was solved.
        formulation: The formulation model built for the problem.
        strategy: The strategy selected and used.
        mapping: The mapping record from program to runtime object.
        execution: The execution result (QuantumResult or raw engine result).
        solution: The domain-level solution.
        interpretation: Data-derived interpretation of the solution.
        provenance: Where-and-how metadata for the run.
        classification: QMQ-03 problem classification (optional).
        recommendation: QMQ-03 algorithm recommendation (optional).
        plan: QMQ-03 computation plan (optional).
        classical_execution: QMQ-04 classical leg result (classical/hybrid runs).
        quantum_execution: QMQ-04 quantum leg result (quantum/hybrid runs).
        comparison: QMQ-04 hybrid comparison + selection (hybrid runs).
        selected_leg: QMQ-04 selected leg (``"classical"``/``"quantum"``).
        result_interpretation: QMQ-06 structured interpretation (optional).
        benchmark: QMQ-05 benchmark result this report belongs to (optional).
        created_at: UTC ISO timestamp of report creation.
    """

    problem: QuantumProblem | None = None
    formulation: MathematicalModel | None = None
    strategy: ComputationStrategy | None = None
    mapping: MappingResult | None = None
    execution: Any | None = None
    solution: ProblemSolution | None = None
    interpretation: Interpretation | None = None
    provenance: Provenance | None = None
    classification: ClassificationResult | None = None
    recommendation: AlgorithmRecommendation | None = None
    plan: ComputationPlan | None = None
    classical_execution: ClassicalExecutionResult | None = None
    quantum_execution: QuantumExecutionResult | None = None
    comparison: ExecutionComparison | None = None
    selected_leg: str | None = None
    result_interpretation: ResultInterpretation | None = None
    benchmark: BenchmarkResult | None = None
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def to_dict(self) -> dict[str, Any]:
        """Serialize the report to a JSON-safe dictionary."""
        return {
            "problem": self.problem.to_dict() if self.problem is not None else None,
            "formulation": (self.formulation.to_dict() if self.formulation is not None else None),
            "strategy": (self.strategy.name.lower() if self.strategy is not None else None),
            "mapping": self.mapping.to_dict() if self.mapping is not None else None,
            "execution": (
                self.execution.to_dict()
                if self.execution is not None and hasattr(self.execution, "to_dict")
                else (repr(self.execution) if self.execution is not None else None)
            ),
            "solution": self.solution.to_dict() if self.solution is not None else None,
            "interpretation": (
                self.interpretation.to_dict() if self.interpretation is not None else None
            ),
            "provenance": (self.provenance.to_dict() if self.provenance is not None else None),
            "classification": (
                self.classification.to_dict() if self.classification is not None else None
            ),
            "recommendation": (
                self.recommendation.to_dict() if self.recommendation is not None else None
            ),
            "plan": self.plan.to_dict() if self.plan is not None else None,
            "classical_execution": (
                self.classical_execution.to_dict() if self.classical_execution is not None else None
            ),
            "quantum_execution": (
                self.quantum_execution.to_dict() if self.quantum_execution is not None else None
            ),
            "comparison": (self.comparison.to_dict() if self.comparison is not None else None),
            "selected_leg": self.selected_leg,
            "result_interpretation": (
                self.result_interpretation.to_dict()
                if self.result_interpretation is not None
                else None
            ),
            "benchmark": (self.benchmark.to_dict() if self.benchmark is not None else None),
            "created_at": self.created_at,
        }

    def __repr__(self) -> str:
        return (
            f"SolutionReport(problem={self.problem.name if self.problem else None!r}, "
            f"strategy={self.strategy.name.lower() if self.strategy else None}, "
            f"feasible={self.solution.feasible if self.solution else None})"
        )


__all__ = ["SolutionReport"]
