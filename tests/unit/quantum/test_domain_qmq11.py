"""QMQ-11 Advanced Quantum & Domain Intelligence tests.

Covers the cross-domain layer: explicit registered dispatch through
:class:`DomainRegistry` (Finance, Portfolio, Data, ML), the inspectable
assessment (:class:`ProblemAssessment` / ``assess_problem``), the
domain-aware execution plan (:class:`ExecutionPlan`), deterministic quantum
suitability (:class:`QuantumSuitabilityAssessor`), the honest
:class:`DomainRunResult` wrapper (strategy/execution facts, no invented
quantum claims), deterministic classical solves and benchmarks across the
four domains, JSON-safe serialization round-trips, the canonical end-to-end
examples and the MicroQuantum-blocked subprocess path (import/assess/solve and
honest quantum-request degradation).
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

from quantsmind.quantum import (
    DomainIntelligence,
    QuantumProblem,
    example_portfolio_problem,
    qaoa_available,
)
from quantsmind.quantum.data.examples import feature_selection_example
from quantsmind.quantum.domain.assessment import ProblemAssessment, assess_problem
from quantsmind.quantum.domain.errors import (
    DomainDispatchError,
    DomainValidationError,
    UnsupportedDomainError,
)
from quantsmind.quantum.domain.plan import ExecutionPlan
from quantsmind.quantum.domain.registry import DomainBinding, DomainKind, DomainRegistry
from quantsmind.quantum.domain.result import DomainRunResult
from quantsmind.quantum.domain.suitability import (
    QuantumSuitability,
    QuantumSuitabilityAssessor,
    SuitabilityAssessment,
)
from quantsmind.quantum.finance.models import AssetUniverse, FinancialProblem
from quantsmind.quantum.intelligence.algorithms import AlgorithmRecommendation
from quantsmind.quantum.intelligence.capabilities import CapabilityModel
from quantsmind.quantum.intelligence.plan import ComputationPlan
from quantsmind.quantum.ml.examples import ml_classification_example
from quantsmind.quantum.strategy.strategy import ComputationStrategy

_SRC = str(Path(__file__).parents[3] / "src")

_CLASSICAL = "classical"


# ----------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------


def _finance() -> FinancialProblem:
    # Canonical QMQ-08 risk-adjusted portfolio -> financial problem.  Its
    # QUBO maps losslessly (cardinality-only, binary), so the end-to-end
    # classical solve is well-defined and reproducible.
    return example_portfolio_problem().to_financial_problem()


def _data() -> object:
    return feature_selection_example()


def _ml() -> object:
    return ml_classification_example()


def _intelligence() -> DomainIntelligence:
    return DomainIntelligence()


def _capabilities(*, quantum_ready: bool, qaoa_ready: bool) -> CapabilityModel:
    return CapabilityModel(
        microquantum_installed=quantum_ready,
        quantum_enabled=True,
        simulator_available=quantum_ready,
        backend_available=quantum_ready,
        qml_available=quantum_ready,
        quantum_execution_enabled=quantum_ready,
        classical_baseline_available=True,
        algorithm_available={"qaoa": qaoa_ready, "qaoa_available": qaoa_ready},
    )


def _plan(
    *,
    strategy: ComputationStrategy,
    formulation: str = "qubo",
    algorithm: str | None = "qaoa",
    executor: str = "",
) -> ComputationPlan:
    return ComputationPlan(
        problem_name="fake_problem",
        problem_class="binary_optimization",
        formulation=formulation,
        strategy=strategy,
        algorithm=algorithm,
        recommendation=AlgorithmRecommendation(
            algorithm=algorithm,
            suitability_score=0.8,
            reason="test",
        ),
        mapping="qubo" if formulation == "qubo" else "none",
        executor=executor,
        fallbacks=["qaoa", "qaoa_available"] if executor else [],
        capabilities={},
    )


# ----------------------------------------------------------------------
# explicit registered dispatch (QMQ-11 §10)
# ----------------------------------------------------------------------


class TestDomainRegistry:
    def test_default_registry_registers_four_domains(self) -> None:
        registry = DomainRegistry()
        assert len(registry) == 4
        assert registry.domains() == [
            DomainKind.FINANCE,
            DomainKind.PORTFOLIO,
            DomainKind.DATA,
            DomainKind.ML,
        ]

    def test_supported_domains_labels(self) -> None:
        assert DomainIntelligence().supported_domains() == [
            "finance",
            "portfolio",
            "data",
            "ml",
        ]

    def test_resolve_each_domain(self) -> None:
        registry = DomainRegistry()
        assert registry.kind_of(_finance()) is DomainKind.FINANCE
        assert registry.kind_of(example_portfolio_problem()) is DomainKind.PORTFOLIO
        assert registry.kind_of(_data()) is DomainKind.DATA
        assert registry.kind_of(_ml()) is DomainKind.ML

    def test_is_supported(self) -> None:
        intelligence = _intelligence()
        assert intelligence.is_supported(_finance())
        assert intelligence.is_supported(_ml())
        assert not intelligence.is_supported(object())

    def test_resolve_unsupported_raises(self) -> None:
        with pytest.raises(UnsupportedDomainError):
            DomainRegistry().resolve(object())
        with pytest.raises(UnsupportedDomainError):
            DomainRegistry().kind_of(object())
        with pytest.raises(UnsupportedDomainError):
            DomainRegistry().resolve_kind("crypto")  # unknown kind not registered

    def test_empty_registry(self) -> None:
        assert len(DomainRegistry(defaults=False)) == 0

    def test_register_requires_binding(self) -> None:
        with pytest.raises(TypeError):
            DomainRegistry().register("not-a-binding")  # type: ignore[arg-type]

    def test_duplicate_kind_raises(self) -> None:
        registry = DomainRegistry()
        with pytest.raises(ValueError):
            registry.register(registry.bindings()[0])

    def test_contains(self) -> None:
        registry = DomainRegistry()
        assert "data" in registry
        assert DomainKind.ML in registry
        assert "crypto" not in registry

    def test_domain_kind_parse(self) -> None:
        assert DomainKind.parse("finance") is DomainKind.FINANCE
        assert DomainKind.parse("ML") is DomainKind.ML
        assert DomainKind.parse(DomainKind.DATA) is DomainKind.DATA
        with pytest.raises(ValueError):
            DomainKind.parse("nope")

    def test_binding_accepts_and_top_quantum_problem(self) -> None:
        registry = DomainRegistry()
        finance = registry.resolve_kind(DomainKind.FINANCE)
        assert isinstance(finance, DomainBinding)
        assert finance.accepts(_finance())
        assert not finance.accepts(_ml())
        assert finance.validate(_finance()) == []
        quantum = finance.to_quantum_problem(_finance())
        assert isinstance(quantum, QuantumProblem)

    def test_assess_invalid_problem_raises_domain_validation_error(self) -> None:
        invalid = FinancialProblem(
            name="broken",
            universe=AssetUniverse([]),
            objectives=[],
            constraints=[],
            allocation_kind=example_portfolio_problem().to_financial_problem().allocation_kind,
        )
        with pytest.raises(DomainValidationError):
            _intelligence().assess(invalid)


# ----------------------------------------------------------------------
# assessment & plan (QMQ-11 §4, §7)
# ----------------------------------------------------------------------


class TestAssessmentAndPlan:
    def test_assess_finance(self) -> None:
        assessment = _intelligence().assess(_finance(), strategy=_CLASSICAL)
        assert isinstance(assessment, ProblemAssessment)
        assert assessment.problem_name == "qmq08_risk_adjusted"
        assert assessment.domain_label == "finance"
        assert assessment.classification.label == "binary_optimization"
        assert assessment.formulation_kind == "qubo"
        assert assessment.strategy_label == "classical"
        assert assessment.is_implementable
        assert assessment.computation_plan is not None
        assert assessment.suitability_label == "conditionally_suitable"

    def test_assess_data_and_ml_formulation(self) -> None:
        for problem, expected_kind in ((_data(), "data"), (_ml(), "ml")):
            assessment = assess_problem(problem, strategy=_CLASSICAL)
            assert assessment.domain_label == expected_kind
            assert assessment.formulation_kind == "qubo"
            assert assessment.classification.label == "binary_optimization"

    def test_assessment_dict_round_trip(self) -> None:
        original = _intelligence().assess(_finance(), strategy=_CLASSICAL)
        restored = ProblemAssessment.from_dict(original.to_dict())
        assert restored.problem_name == original.problem_name
        assert restored.domain_label == original.domain_label
        assert restored.classification.label == original.classification.label
        assert restored.formulation_kind == original.formulation_kind
        assert restored.strategy_label == original.strategy_label
        assert restored.suitability_label == original.suitability_label
        assert restored.is_implementable
        assert restored.computation_plan is not None
        assert restored.computation_plan.strategy_label == "classical"

    def test_plan(self) -> None:
        plan = _intelligence().plan(_finance(), strategy=_CLASSICAL)
        assert isinstance(plan, ExecutionPlan)
        assert plan.problem_name == "qmq08_risk_adjusted"
        assert plan.domain_label == "finance"
        assert plan.strategy == "classical"
        assert plan.executor == "classical/exhaustive"
        assert not plan.is_quantum
        assert plan.suitability.label == "conditionally_suitable"
        assert "qmq08_risk_adjusted" in plan.summary()

    def test_plan_dict_round_trip(self) -> None:
        original = _intelligence().plan(_finance(), strategy=_CLASSICAL)
        restored = ExecutionPlan.from_dict(original.to_dict())
        assert restored.problem_name == original.problem_name
        assert restored.domain_label == original.domain_label
        assert restored.strategy == original.strategy
        assert restored.executor == original.executor
        assert restored.suitability.label == original.suitability.label
        assert restored.classification == original.classification

    def test_plan_unknown_problem_raises_dispatch_error(self) -> None:
        with pytest.raises(DomainDispatchError):
            _intelligence().plan(object())


# ----------------------------------------------------------------------
# deterministic suitability (QMQ-11 §5)
# ----------------------------------------------------------------------


class TestQuantumSuitability:
    def test_suitable_when_quantum_path_runnable(self) -> None:
        plan = _plan(
            strategy=ComputationStrategy.HYBRID,
            executor="microquantum/qaoa",
        )
        assessment = QuantumSuitabilityAssessor().assess(
            plan=plan, capabilities=_capabilities(quantum_ready=True, qaoa_ready=True)
        )
        assert assessment.suitability is QuantumSuitability.SUITABLE
        assert assessment.is_suitable
        assert assessment.quantum_available and assessment.algorithm_available
        assert assessment.limitations == []

    def test_conditionally_suitable_when_runtime_missing(self) -> None:
        plan = _plan(
            strategy=ComputationStrategy.HYBRID,
            executor="microquantum/qaoa",
        )
        assessment = QuantumSuitabilityAssessor().assess(
            plan=plan, capabilities=_capabilities(quantum_ready=False, qaoa_ready=True)
        )
        assert assessment.suitability is QuantumSuitability.CONDITIONALLY_SUITABLE
        assert assessment.is_suitable
        assert any(
            "no quantum execution runtime" in limitation for limitation in assessment.limitations
        )

    def test_conditionally_suitable_when_algorithm_missing(self) -> None:
        plan = _plan(
            strategy=ComputationStrategy.HYBRID,
            executor="microquantum/qaoa",
        )
        assessment = QuantumSuitabilityAssessor().assess(
            plan=plan, capabilities=_capabilities(quantum_ready=True, qaoa_ready=False)
        )
        assert assessment.suitability is QuantumSuitability.CONDITIONALLY_SUITABLE
        assert any("not executable" in limitation for limitation in assessment.limitations)

    def test_conditionally_suitable_when_classical_selected(self) -> None:
        plan = _plan(
            strategy=ComputationStrategy.CLASSICAL,
            algorithm="exhaustive",
        )
        assessment = QuantumSuitabilityAssessor().assess(
            plan=plan, capabilities=_capabilities(quantum_ready=True, qaoa_ready=True)
        )
        assert assessment.suitability is QuantumSuitability.CONDITIONALLY_SUITABLE
        assert any("CLASSICAL here" in limitation for limitation in assessment.limitations)

    def test_unsuitable_when_not_qubo_amenable(self) -> None:
        plan = _plan(
            strategy=ComputationStrategy.QUANTUM,
            formulation="ising",
            algorithm="qaoa",
        )
        assessment = QuantumSuitabilityAssessor().assess(
            plan=plan, capabilities=_capabilities(quantum_ready=True, qaoa_ready=True)
        )
        assert assessment.suitability is QuantumSuitability.UNSUITABLE
        assert not assessment.is_suitable
        assert not assessment.formulation_amenable

    def test_unknown_when_no_plan(self) -> None:
        assessment = QuantumSuitabilityAssessor().assess_unknown(problem_name="x")
        assert assessment.suitability is QuantumSuitability.UNKNOWN
        assert not assessment.is_suitable

    def test_suitability_assessment_dict_round_trip(self) -> None:
        original = QuantumSuitabilityAssessor().assess(
            plan=_plan(strategy=ComputationStrategy.HYBRID, executor="microquantum/qaoa"),
            capabilities=_capabilities(quantum_ready=True, qaoa_ready=True),
        )
        restored = SuitabilityAssessment.from_dict(original.to_dict())
        assert restored.label == original.label
        assert restored.is_suitable
        assert restored.quantum_available == original.quantum_available
        assert restored.formulation_amenable == original.formulation_amenable
        assert restored.reason == original.reason

    @pytest.mark.skipif(not qaoa_available(), reason="microquantum missing")
    def test_assess_reports_suitable_on_default_plan_when_runtime_exists(self) -> None:
        # Installed runtime: the auto plan selects a quantum path and the
        # assessor must record SUITABLE — never UNKNOWN, never UNSUITABLE.
        assessment = _intelligence().assess(_finance())
        assert assessment.suitability_label == "suitable"
        assert assessment.is_implementable


# ----------------------------------------------------------------------
# execution: solve / benchmark / interpretation (QMQ-11 §8, §9)
# ----------------------------------------------------------------------


class TestDomainExecution:
    def test_solve_finance(self) -> None:
        result = _intelligence().solve(_finance(), strategy=_CLASSICAL)
        assert isinstance(result, DomainRunResult)
        assert result.problem_name == "qmq08_risk_adjusted"
        assert result.domain_label == "finance"
        assert result.strategy_requested == "classical"
        assert result.strategy_executed == "classical"
        assert result.execution_mode == "classical"
        assert result.fallback_used is False
        assert result.feasible is True
        assert result.algorithm == "exhaustive"
        assert result.backend == ""
        assert result.interpretation is not None
        assert result.interpretation_status() == "InterpretationStatus.EXECUTED"
        assert result.report is not None

    def test_solve_finance_objective_is_known_optimum(self) -> None:
        result = _intelligence().solve(_finance(), strategy=_CLASSICAL)
        assert result.objective_value is not None
        assert abs(result.objective_value - 0.038) < 1e-9

    def test_solve_finance_reproducible(self) -> None:
        first = _intelligence().solve(_finance(), strategy=_CLASSICAL)
        second = _intelligence().solve(_finance(), strategy=_CLASSICAL)
        assert first.objective_value == second.objective_value
        assert first.feasible == second.feasible

    def test_solve_data_and_ml(self) -> None:
        data = _intelligence().solve(_data(), strategy=_CLASSICAL)
        assert data.domain_label == "data"
        assert data.feasible is True
        assert data.objective_value == 9.0
        assert data.execution_mode == "classical"
        ml = _intelligence().solve(_ml(), strategy=_CLASSICAL)
        assert ml.domain_label == "ml"
        assert ml.feasible is True
        assert ml.objective_value == 3.0
        assert ml.execution_mode == "classical"

    def test_solve_data_returns_assets(self) -> None:
        data = _intelligence().solve(_data(), strategy=_CLASSICAL)
        solution = data.domain_result.solution
        assert solution.selected_features == ["height", "depth"]

    def test_benchmark(self) -> None:
        result = _intelligence().benchmark(_data(), strategy=_CLASSICAL)
        assert isinstance(result, DomainRunResult)
        assert result.domain_label == "data"
        assert result.benchmark is not None
        assert result.benchmark.status == "executed"
        assert result.interpretation is not None

    def test_solve_and_interpret(self) -> None:
        result = _intelligence().solve_and_interpret(_ml(), strategy=_CLASSICAL)
        assert _intelligence().interpret(result) is result.interpretation

    def test_domain_run_result_dict_round_trip(self) -> None:
        original = _intelligence().solve(_finance(), strategy=_CLASSICAL)
        restored = DomainRunResult.from_dict(original.to_dict())
        assert restored.problem_name == original.problem_name
        assert restored.domain_label == original.domain_label
        assert restored.strategy_requested == original.strategy_requested
        assert restored.strategy_executed == original.strategy_executed
        assert restored.execution_mode == original.execution_mode
        assert restored.feasible == original.feasible
        assert restored.objective_value == original.objective_value
        assert restored.fallback_used == original.fallback_used
        assert restored.interpretation is not None

    def test_no_false_quantum_claim_on_classical(self) -> None:
        result = _intelligence().solve(_finance(), strategy=_CLASSICAL)
        assert result.execution_mode == "classical"
        assert result.backend == ""
        assert any("no quantum execution" in limitation for limitation in result.limitations)


# ----------------------------------------------------------------------
# canonical end-to-end examples (QMQ-11 §16)
# ----------------------------------------------------------------------


class TestDomainExamples:
    def test_finance_example(self) -> None:
        from quantsmind.quantum.domain.examples import domain_finance_example

        artifacts = domain_finance_example()
        assessment = artifacts["assessment"]
        assert assessment.classification.label == "binary_optimization"
        assert assessment.formulation_kind == "qubo"
        assert assessment.suitability.is_suitable
        assert assessment.suitability_label in ("suitable", "conditionally_suitable")
        assert artifacts["plan"].domain_label == "finance"
        assert artifacts["plan"].problem_name == "qmq08_risk_adjusted"
        solve = artifacts["solve"]
        assert solve.feasible is True
        assert solve.strategy_executed == "classical"
        assert solve.execution_mode == "classical"
        assert artifacts["benchmark"].benchmark is not None
        assert artifacts["interpretation"].status.value == "executed"

    def test_data_and_ml_examples(self) -> None:
        from quantsmind.quantum.domain.examples import (
            domain_data_example,
            domain_ml_example,
        )

        data = domain_data_example()
        assert data["solve"].objective_value == 9.0
        assert data["solve"].execution_mode == "classical"
        ml = domain_ml_example()
        assert ml["solve"].objective_value == 3.0
        assert ml["solve"].execution_mode == "classical"

    def test_pipeline_example_supports_three_domains(self) -> None:
        from quantsmind.quantum.domain.examples import domain_pipeline_example

        pipeline = domain_pipeline_example()
        assert set(pipeline) == {"finance", "data", "ml"}
        assert all(pipeline[name]["solve"].feasible for name in pipeline)


# ----------------------------------------------------------------------
# no microquantum dependency (blocked subprocess)
# ----------------------------------------------------------------------


class TestNoMicroQuantum:
    @staticmethod
    def _blocked_rc(source: str) -> tuple[int, str]:
        code = (
            "import sys\n"
            "class _Blocker:\n"
            "    def find_spec(self, fullname, path=None, target=None):\n"
            "        if fullname == 'microquantum' or fullname.startswith('microquantum.'):\n"
            "            raise ModuleNotFoundError('blocked')\n"
            "        return None\n"
            "sys.meta_path.insert(0, _Blocker())\n" + source
        )
        env = {**os.environ, "PYTHONPATH": _SRC}
        run = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            env=env,
            timeout=240,
        )
        return run.returncode, run.stdout

    def test_import_and_assess_blocked(self) -> None:
        rc, out = self._blocked_rc(
            """
from quantsmind.quantum.domain import DomainIntelligence, DomainRegistry
from quantsmind.quantum.finance.portfolio_examples import example_portfolio_problem
problem = example_portfolio_problem().to_financial_problem()
registry = DomainRegistry()
assert len(registry) == 4
assessment = DomainIntelligence().assess(problem, strategy="classical")
assert assessment.domain_label == "finance"
assert assessment.strategy_label == "classical"
assert assessment.suitability.label == "conditionally_suitable"
print("QMQ11_OK")
"""
        )
        assert rc == 0, out
        assert "QMQ11_OK" in out

    def test_classical_solve_blocked(self) -> None:
        rc, out = self._blocked_rc(
            """
from quantsmind.quantum.domain import DomainIntelligence
from quantsmind.quantum.finance.portfolio_examples import example_portfolio_problem
result = DomainIntelligence().solve(
    example_portfolio_problem().to_financial_problem(), strategy="classical"
)
assert result.feasible is True
assert result.execution_mode == "classical"
assert result.backend == ""
print("QMQ11_OK")
"""
        )
        assert rc == 0, out
        assert "QMQ11_OK" in out

    def test_quantum_request_honest_downgrade_blocked(self) -> None:
        rc, out = self._blocked_rc(
            """
from quantsmind.quantum.domain import DomainIntelligence
from quantsmind.quantum.ml.examples import ml_classification_example
result = DomainIntelligence().solve(ml_classification_example(), strategy="quantum")
assert result.report is not None
assert result.report.strategy.name.lower() == "classical"
assert result.strategy_executed == "classical"
assert result.fallback_used is True
assert result.feasible is True
print("QMQ11_OK")
"""
        )
        assert rc == 0, out
        assert "QMQ11_OK" in out
