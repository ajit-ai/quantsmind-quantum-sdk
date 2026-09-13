"""QMQ-08 Portfolio Optimization tests.

Covers optimization configuration, the PortfolioOptimizationProblem model
(binary/continuous/integer allocation), validation (including impossible
portfolios), objectives/constraints/budget materialization, deterministic
serialization, asset mapping and QMQ-02 formulation reuse, portfolio
metrics, classical solving with known optima, benchmarking against the
classical baseline, QMQ-06 interpretation, honest failure semantics
(MappingError for continuous, FinanceValidationError for integer,
WorkflowError for QUANTUM_INSPIRED), deterministic repeated runs, the
MicroQuantum-blocked subprocess path and the canonical synthetic examples.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

from quantsmind.quantum import (
    AllocationKind,
    FinanceValidationError,
    MappingError,
    OptimizationModel,
    PortfolioAssetMapper,
    PortfolioFormulationAdapter,
    PortfolioOptimizationProblem,
    PortfolioOptimizationResult,
    PortfolioOptimizer,
    PortfolioSolution,
    QUBOMapper,
    WorkflowError,
)
from quantsmind.quantum.finance import (
    Budget,
    CardinalityConstraint,
    ExpectedReturnObjective,
    GroupAllocationConstraint,
    OptimizationConfiguration,
    PositionLimitConstraint,
    RiskAdjustedObjective,
    RiskMatrix,
    RiskObjective,
    compute_portfolio_metrics,
    example_budget_portfolio,
    example_group_constraints_portfolio,
    example_maximize_return_portfolio,
    example_minimize_risk_portfolio,
    example_portfolio_problem,
    example_portfolio_risk_matrix,
    example_portfolio_universe,
    example_risk_adjusted_portfolio,
    expected_return_of,
    portfolio_variance,
    portfolio_volatility,
    risk_contributions,
)

_SRC = str(Path(__file__).parents[3] / "src")


# ----------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------


def _universe():
    return example_portfolio_universe()


def _risk():
    return example_portfolio_risk_matrix()


def _config(preferred_strategy: str = "classical") -> OptimizationConfiguration:
    return OptimizationConfiguration(preferred_strategy=preferred_strategy)


# ----------------------------------------------------------------------
# configuration
# ----------------------------------------------------------------------


class TestOptimizationConfiguration:
    def test_defaults(self) -> None:
        config = PortfolioOptimizationProblem(name="p", universe=_universe()).optimization_config
        assert config.preferred_strategy == ""
        assert config.shots == 1024
        assert config.seed is None
        assert config.solver_max_variables == 20
        assert config.optimization_level == 0

    def test_strategy_normalization(self) -> None:
        assert OptimizationConfiguration(preferred_strategy=None).preferred_strategy == ""
        assert OptimizationConfiguration(preferred_strategy="").preferred_strategy == ""
        assert (
            OptimizationConfiguration(preferred_strategy=" classical ").preferred_strategy
            == "classical"
        )
        assert OptimizationConfiguration(preferred_strategy="HYBRID").preferred_strategy == "hybrid"

    def test_unknown_strategy_raises(self) -> None:
        with pytest.raises(FinanceValidationError):
            OptimizationConfiguration(preferred_strategy="teleportation")

    def test_invalid_values_raise(self) -> None:
        with pytest.raises(FinanceValidationError):
            OptimizationConfiguration(shots=0)
        with pytest.raises(FinanceValidationError):
            OptimizationConfiguration(seed=-1)
        with pytest.raises(FinanceValidationError):
            OptimizationConfiguration(solver_max_variables=0)
        with pytest.raises(FinanceValidationError):
            OptimizationConfiguration(optimization_level=9)

    def test_serialization_round_trip(self) -> None:
        config = OptimizationConfiguration(
            preferred_strategy="hybrid",
            algorithm="qaoa",
            shots=64,
            seed=3,
            solver_max_variables=30,
            optimization_level=1,
            metadata={"tag": "x"},
        )
        assert OptimizationConfiguration.from_dict(config.to_dict()).to_dict() == config.to_dict()


# ----------------------------------------------------------------------
# problem model
# ----------------------------------------------------------------------


class TestPortfolioProblem:
    def test_construction_and_size(self) -> None:
        problem = PortfolioOptimizationProblem(
            name="p",
            universe=_universe(),
            objectives=[ExpectedReturnObjective("expected_return")],
            allocation_kind="binary",
        )
        assert problem.size == 4
        assert problem.allocation_kind is AllocationKind.BINARY
        assert problem.validate() == []

    def test_default_allocation_kind_is_binary(self) -> None:
        problem = PortfolioOptimizationProblem(name="p", universe=_universe())
        assert problem.allocation_kind is AllocationKind.BINARY

    def test_empty_name_raises(self) -> None:
        with pytest.raises(FinanceValidationError):
            PortfolioOptimizationProblem(name="", universe=_universe())

    def test_duplicate_objective_names_raise(self) -> None:
        with pytest.raises(FinanceValidationError):
            PortfolioOptimizationProblem(
                name="p",
                universe=_universe(),
                objectives=[
                    ExpectedReturnObjective("same"),
                    RiskObjective("same"),
                ],
            )

    def test_duplicate_constraint_names_raise(self) -> None:
        with pytest.raises(FinanceValidationError):
            PortfolioOptimizationProblem(
                name="p",
                universe=_universe(),
                constraints=[
                    CardinalityConstraint(name="cardinality", min_assets=1, max_assets=2),
                    CardinalityConstraint(name="cardinality", min_assets=2, max_assets=4),
                ],
            )

    def test_binary_decision_variables(self) -> None:
        variables = PortfolioOptimizationProblem(
            name="p",
            universe=_universe(),
            allocation_kind="binary",
        ).decision_variables
        assert [v.name for v in variables] == ["x0", "x1", "x2", "x3"]
        from quantsmind.quantum import VariableType

        assert all(v.type is VariableType.BINARY for v in variables)
        assert variables[0].metadata["asset_id"] == "TECH-A"

    def test_continuous_decision_variables(self) -> None:
        variables = PortfolioOptimizationProblem(
            name="p",
            universe=_universe(),
            allocation_kind="continuous",
        ).decision_variables
        from quantsmind.quantum import VariableType

        assert all(v.type is VariableType.CONTINUOUS for v in variables)
        assert all(v.lower_bound == 0.0 for v in variables)
        assert all(v.upper_bound is None for v in variables)

    def test_integer_decision_variables_raise(self) -> None:
        problem = PortfolioOptimizationProblem(
            name="p",
            universe=_universe(),
            allocation_kind="integer",
        )
        with pytest.raises(FinanceValidationError) as exc:
            _ = problem.decision_variables
        assert "integer" in str(exc.value).lower()

    def test_invalid_allocation_kind_raises(self) -> None:
        with pytest.raises(FinanceValidationError):
            PortfolioOptimizationProblem(name="p", universe=_universe(), allocation_kind="int")


# ----------------------------------------------------------------------
# validation
# ----------------------------------------------------------------------


class TestValidation:
    def test_valid_example(self) -> None:
        assert example_risk_adjusted_portfolio().validate() == []

    def test_no_objectives(self) -> None:
        problem = PortfolioOptimizationProblem(name="p", universe=_universe())
        assert any("objective" in issue for issue in problem.validate())

    def test_empty_universe(self) -> None:
        from quantsmind.quantum import AssetUniverse

        problem = PortfolioOptimizationProblem(name="p", universe=AssetUniverse(assets=[]))
        assert any("assets" in issue for issue in problem.validate())

    def test_integer_reported_as_issue(self) -> None:
        problem = PortfolioOptimizationProblem(
            name="p",
            universe=_universe(),
            allocation_kind="integer",
        )
        issues = problem.validate()
        assert any("integer" in issue for issue in issues)
        with pytest.raises(FinanceValidationError):
            problem.raise_if_invalid()

    def test_risk_alignment(self) -> None:
        risk = RiskMatrix(
            asset_order=["TECH-A", "TECH-B"],
            matrix=[[0.0625, 0.0], [0.0, 0.0324]],
        )
        problem = PortfolioOptimizationProblem(name="p", universe=_universe(), risk=risk)
        assert any("risk matrix" in issue for issue in problem.validate())

    def test_impossible_minimum_allocation_vs_budget(self) -> None:
        problem = example_budget_portfolio()
        assert problem.validate() == []
        impossible = PortfolioOptimizationProblem(
            name="p",
            universe=_universe(),
            objectives=[ExpectedReturnObjective("expected_return")],
            constraints=[CardinalityConstraint(name="cardinality", min_assets=5, max_assets=5)],
            allocation_kind="continuous",
            budget=Budget(total=1.0),
        )
        issues = impossible.validate()
        assert any("exceeds the available budget" in issue for issue in issues)

    def test_cardinality_exceeds_assets(self) -> None:
        problem = PortfolioOptimizationProblem(
            name="p",
            universe=_universe(),
            objectives=[ExpectedReturnObjective("expected_return")],
            constraints=[CardinalityConstraint(name="cardinality", min_assets=9)],
        )
        assert any("exceeds the universe size" in issue for issue in problem.validate())

    def test_budget_name_conflict(self) -> None:
        problem = PortfolioOptimizationProblem(
            name="p",
            universe=_universe(),
            constraints=[CardinalityConstraint(name="budget", min_assets=1)],
            budget=Budget(total=1.0),
        )
        issues = problem.validate()
        assert any("budget" in issue and "conflict" in issue for issue in issues)

    def test_position_limit_unknown_asset(self) -> None:
        problem = PortfolioOptimizationProblem(
            name="p",
            universe=_universe(),
            constraints=[PositionLimitConstraint(name="limits", asset_ids=["MISSING"], upper=1.0)],
        )
        assert any("unknown assets" in issue for issue in problem.validate())

    def test_group_with_no_members(self) -> None:
        problem = PortfolioOptimizationProblem(
            name="p",
            universe=_universe(),
            constraints=[GroupAllocationConstraint(name="fx", group="fx", upper=1.0)],
        )
        assert any("no assets" in issue for issue in problem.validate())

    def test_raise_if_invalid_raises(self) -> None:
        with pytest.raises(FinanceValidationError):
            PortfolioOptimizationProblem(name="p", universe=_universe()).raise_if_invalid()


# ----------------------------------------------------------------------
# objectives & constraints & budget
# ----------------------------------------------------------------------


class TestObjectivesAndConstraints:
    def test_expected_return_expression(self) -> None:
        problem = example_maximize_return_portfolio()
        quantum = PortfolioFormulationAdapter().to_quantum_problem(problem)
        objective = quantum.objectives[0]
        assert objective.sense.name == "MAXIMIZE"
        assert "0.12*x0" in objective.expression
        assert "0.01*x3" in objective.expression

    def test_risk_objective_requires_matrix(self) -> None:
        problem = PortfolioOptimizationProblem(
            name="p",
            universe=_universe(),
            objectives=[RiskObjective("risk")],
        )
        assert any("risk matrix" in issue for issue in problem.validate())

    def test_risk_adjusted_expression(self) -> None:
        problem = example_risk_adjusted_portfolio()
        quantum = PortfolioFormulationAdapter().to_quantum_problem(problem)
        expression = quantum.objectives[0].expression
        assert "2.0*(" in expression
        assert "0.12*x0" in expression

    def test_zero_aversion_degrades_to_return(self) -> None:
        problem = PortfolioOptimizationProblem(
            name="p",
            universe=_universe(),
            objectives=[RiskAdjustedObjective("utility", risk_aversion=0.0)],
        )
        assert problem.validate() == []
        quantum = PortfolioFormulationAdapter().to_quantum_problem(problem)
        expression = quantum.objectives[0].expression
        assert "0.12*x0" in expression
        assert "*(" not in expression

    def test_budget_materializes_constraints(self) -> None:
        financial = example_budget_portfolio().to_financial_problem()
        names = [constraint.name for constraint in financial.constraints]
        assert "budget" in names
        assert "budget_allocation" in names

    def test_explicit_constraints_precede_budget(self) -> None:
        financial = example_budget_portfolio().to_financial_problem()
        names = [constraint.name for constraint in financial.constraints]
        assert names.index("positions") < names.index("budget")
        assert names.index("cash_floor") < names.index("budget")

    def test_budget_with_only_total_adds_budget_constraint(self) -> None:
        problem = PortfolioOptimizationProblem(
            name="p",
            universe=_universe(),
            budget=Budget(total=2.0),
        )
        financial = problem.to_financial_problem()
        assert [c.name for c in financial.constraints] == ["budget"]


# ----------------------------------------------------------------------
# serialization
# ----------------------------------------------------------------------


class TestSerialization:
    def test_problem_round_trip(self) -> None:
        problem = example_risk_adjusted_portfolio()
        rebuilt = PortfolioOptimizationProblem.from_dict(problem.to_dict())
        assert rebuilt.to_dict() == problem.to_dict()
        assert [c.name for c in rebuilt.constraints] == [c.name for c in problem.constraints]

    def test_problem_round_trip_with_budget(self) -> None:
        rebuilt = PortfolioOptimizationProblem.from_dict(example_budget_portfolio().to_dict())
        assert rebuilt.budget is not None
        assert rebuilt.allocation_kind.name.lower() == "continuous"
        assert rebuilt.optimization_config.to_dict() == {
            "preferred_strategy": "classical",
            "algorithm": "",
            "shots": 1024,
            "seed": None,
            "solver_max_variables": 20,
            "optimization_level": 0,
            "metadata": {},
        }

    def test_deterministic_serialization(self) -> None:
        first = example_maximize_return_portfolio().to_dict()
        second = example_maximize_return_portfolio().to_dict()
        assert first == second


# ----------------------------------------------------------------------
# mapping & formulation reuse
# ----------------------------------------------------------------------


class TestMappingAndFormulation:
    def test_deterministic_mapping(self) -> None:
        mapper = PortfolioAssetMapper()
        problem = example_maximize_return_portfolio()
        assert mapper.variable(problem, "TECH-A") == "x0"
        assert mapper.variable(problem, "CASH-A") == "x3"
        assert mapper.asset(problem, "x2") == "BOND-A"
        assert [m.variable_name for m in mapper.decode(problem, {})] == ["x0", "x1", "x2", "x3"]

    def test_decode_ignores_slack_and_sets_selected(self) -> None:
        mapper = PortfolioAssetMapper()
        decoded = mapper.decode(
            example_maximize_return_portfolio(),
            {"x0": 1, "x1": 0, "x2": 1, "x3": 0, "s0": 1, "s1": 5},
            selected_threshold=0.5,
        )
        selected = [d.asset_id for d in decoded if d.selected]
        assert selected == ["TECH-A", "BOND-A"]
        assert all(d.value != 5 for d in decoded)

    def test_formulation_reuses_qmq_pipeline(self) -> None:
        model = PortfolioFormulationAdapter().formulate(example_maximize_return_portfolio())
        assert isinstance(model, OptimizationModel)
        assert [v for v in model.variables] == ["x0", "x1", "x2", "x3"]

    def test_qubo_mapping_is_reused(self) -> None:
        quantum = PortfolioFormulationAdapter().to_quantum_problem(
            example_maximize_return_portfolio()
        )
        mapping = QUBOMapper().map(quantum)
        assert mapping.payload.name.endswith("_qubo")

    def test_portfolio_metadata(self) -> None:
        problem = example_maximize_return_portfolio()
        quantum = PortfolioFormulationAdapter().to_quantum_problem(problem)
        assert quantum.metadata["domain_sublayer"] == "portfolio"
        assert quantum.metadata["portfolio"] == "qmq08_maximize_return"
        assert quantum.metadata["optimization_config"]["preferred_strategy"] == "classical"
        assert quantum.metadata["domain_layer"] == "finance"
        assert quantum.provenance["domain_sublayer"] == "portfolio"

    def test_budget_in_metadata(self) -> None:
        quantum = PortfolioFormulationAdapter().to_quantum_problem(example_budget_portfolio())
        assert quantum.metadata["budget"]["total"] == 1.0


# ----------------------------------------------------------------------
# metrics
# ----------------------------------------------------------------------


class TestMetrics:
    def test_expected_return_of(self) -> None:
        universe = _universe()
        weights = {"TECH-A": 1.0}
        assert expected_return_of(universe, weights) == pytest.approx(0.12)
        assert expected_return_of(universe, {"TECH-A": 0.5, "BOND-A": 0.5}) == pytest.approx(0.075)

    def test_portfolio_variance_known_value(self) -> None:
        risk = _risk()
        assert portfolio_variance(risk, {"TECH-A": 1.0}) == pytest.approx(0.0625)
        assert portfolio_variance(risk, {"TECH-B": 1.0, "BOND-A": 1.0}) == pytest.approx(0.036)

    def test_portfolio_volatility(self) -> None:
        risk = _risk()
        assert portfolio_volatility(risk, {"TECH-A": 1.0}) == pytest.approx(0.25)

    def test_risk_contributions(self) -> None:
        risk = _risk()
        contributions = risk_contributions(risk, {"TECH-A": 1.0})
        assert contributions["TECH-A"] == pytest.approx(0.0625)
        assert contributions["CASH-A"] == pytest.approx(0.0)

    def test_compute_portfolio_metrics(self) -> None:
        weights = {"TECH-A": 1.0, "TECH-B": 1.0, "BOND-A": 0.0, "CASH-A": 0.0}
        metrics = compute_portfolio_metrics(
            _universe(),
            weights,
            _risk(),
            selected_threshold=0.5,
            violation_count=1,
            violation_magnitude=0.3,
        )
        assert metrics.expected_return == pytest.approx(0.2)
        assert metrics.variance == pytest.approx(0.0625 + 0.0324 + 2 * 0.03)
        assert metrics.selected_count == 2
        assert metrics.allocation_sum == pytest.approx(2.0)
        assert metrics.constraint_violations == 1
        assert metrics.constraint_violation_magnitude == pytest.approx(0.3)

    def test_metrics_serialization_round_trip(self) -> None:
        metrics = compute_portfolio_metrics(_universe(), {"TECH-A": 1.0}, _risk())
        from quantsmind.quantum import PortfolioMetrics

        assert PortfolioMetrics.from_dict(metrics.to_dict()).to_dict() == metrics.to_dict()


# ----------------------------------------------------------------------
# classical solution
# ----------------------------------------------------------------------


class TestClassicalSolution:
    def test_example_a_optimum(self) -> None:
        optimizer = PortfolioOptimizer(default_seed=7)
        result = optimizer.solve(example_maximize_return_portfolio(), strategy="classical")
        solution = result.solution
        assert solution is not None
        assert solution.objective_value == pytest.approx(0.2)
        assert solution.weights() == {
            "TECH-A": 1.0,
            "TECH-B": 1.0,
            "BOND-A": 0.0,
            "CASH-A": 0.0,
        }
        assert solution.selected_assets() == ["TECH-A", "TECH-B"]
        assert solution.metrics.expected_return == pytest.approx(0.2)
        assert solution.metrics.selected_count == 2
        assert solution.feasible is True
        assert solution.strategy == "classical"
        assert solution.solver == "classical/exhaustive"
        assert solution.num_variables == 4

    def test_objective_values_and_constraint_status(self) -> None:
        solution = (
            PortfolioOptimizer(default_seed=7)
            .solve(example_maximize_return_portfolio(), strategy="classical")
            .solution
        )
        assert solution is not None
        assert solution.objective_values["expected_return"] == pytest.approx(0.2)
        assert all(
            status == "satisfied"
            for name, status in solution.constraint_status.items()
            if "cardinality" in name
        )
        assert solution.num_constraints == 2

    def test_determinism_across_runs(self) -> None:
        optimizer = PortfolioOptimizer(default_seed=11)
        first = optimizer.solve(example_maximize_return_portfolio(), strategy="classical").solution
        second = optimizer.solve(example_maximize_return_portfolio(), strategy="classical").solution
        assert first is not None and second is not None
        assert first.weights() == second.weights()
        assert first.objective_value == second.objective_value
        assert first.selected_assets() == second.selected_assets()
        assert first.metrics.to_dict() == second.metrics.to_dict()

    def test_solution_serialization_round_trip(self) -> None:
        solution = (
            PortfolioOptimizer(default_seed=7)
            .solve(example_maximize_return_portfolio(), strategy="classical")
            .solution
        )
        assert solution is not None
        assert PortfolioSolution.from_dict(solution.to_dict()).to_dict() == solution.to_dict()

    def test_report_attached(self) -> None:
        result = PortfolioOptimizer(default_seed=7).solve(
            example_maximize_return_portfolio(), strategy="classical"
        )
        assert result.report is not None
        assert result.interpretation is not None


# ----------------------------------------------------------------------
# benchmark
# ----------------------------------------------------------------------


class TestBenchmark:
    def test_benchmark_classical_executed(self) -> None:
        result = PortfolioOptimizer(default_seed=7).benchmark(
            example_maximize_return_portfolio(), strategy="classical"
        )
        assert result.benchmark is not None
        assert result.benchmark.status == "executed"
        assert result.solution is not None
        assert result.interpretation is not None
        assert result.benchmark.metrics is not None

    def test_benchmark_known_optimum_gives_unit_ratio(self) -> None:
        result = PortfolioOptimizer(default_seed=7).benchmark(
            example_maximize_return_portfolio(),
            strategy="classical",
            known_optimum=0.2,
        )
        assert result.benchmark is not None
        assert result.benchmark.metrics is not None
        assert result.benchmark.metrics.approximation_ratio == pytest.approx(1.0)
        assert result.benchmark.metrics.optimality_gap == pytest.approx(0.0)

    def test_benchmark_ties_classical_baseline(self) -> None:
        result = PortfolioOptimizer(default_seed=7).benchmark(
            example_maximize_return_portfolio(), strategy="classical"
        )
        assert result.benchmark is not None
        assert result.benchmark.comparison is not None
        assert result.benchmark.comparison.winner is not None
        assert result.benchmark.comparison.winner.value in {"tie", "classical_win"}

    def test_benchmark_repeated_runs_summary(self) -> None:
        result = PortfolioOptimizer(default_seed=7).benchmark(
            example_maximize_return_portfolio(), strategy="classical", runs=2
        )
        assert result.benchmark is not None
        assert result.benchmark.summary is not None
        assert result.benchmark.summary.runs == 2

    def test_result_serialization_round_trip(self) -> None:
        result = PortfolioOptimizer(default_seed=7).benchmark(
            example_maximize_return_portfolio(),
            strategy="classical",
            known_optimum=0.2,
        )
        rebuilt = PortfolioOptimizationResult.from_dict(result.to_dict())
        assert rebuilt.solution is not None
        assert rebuilt.solution.to_dict()["objective_value"] == pytest.approx(0.2)
        assert rebuilt.benchmark is not None
        assert rebuilt.benchmark.status == result.benchmark.status
        assert rebuilt.benchmark.metrics.to_dict() == result.benchmark.metrics.to_dict()


# ----------------------------------------------------------------------
# honest failure semantics
# ----------------------------------------------------------------------


class TestHonestFailures:
    def test_continuous_solve_raises_mapping_error(self) -> None:
        with pytest.raises(MappingError):
            PortfolioOptimizer().solve(example_budget_portfolio(), strategy="classical")

    def test_continuous_benchmark_records_failed(self) -> None:
        result = PortfolioOptimizer().benchmark(example_budget_portfolio(), strategy="classical")
        assert result.benchmark is not None
        assert result.benchmark.status == "failed"
        assert "MappingError" in result.benchmark.error

    def test_continuous_validation_is_clean(self) -> None:
        assert example_budget_portfolio().validate() == []

    def test_continuous_formulation_is_clean(self) -> None:
        model = PortfolioFormulationAdapter().formulate(example_budget_portfolio())
        assert isinstance(model, OptimizationModel)

    def test_integer_solve_raises(self) -> None:
        problem = PortfolioOptimizationProblem(
            name="p",
            universe=_universe(),
            allocation_kind="integer",
        )
        with pytest.raises(FinanceValidationError):
            PortfolioOptimizer().solve(problem, strategy="classical")

    def test_quantum_inspired_raises_workflow_error(self) -> None:
        with pytest.raises(WorkflowError):
            PortfolioOptimizer().solve(
                example_maximize_return_portfolio(), strategy="quantum_inspired"
            )

    def test_continuous_metrics_without_risk_are_none(self) -> None:
        metrics = compute_portfolio_metrics(_universe(), {"TECH-A": 1.0}, None)
        assert metrics.variance is None
        assert metrics.volatility is None
        assert metrics.expected_return == pytest.approx(0.12)


# ----------------------------------------------------------------------
# examples
# ----------------------------------------------------------------------


class TestExamples:
    def test_all_examples_validate(self) -> None:
        for problem in (
            example_maximize_return_portfolio(),
            example_minimize_risk_portfolio(),
            example_risk_adjusted_portfolio(),
            example_budget_portfolio(),
            example_group_constraints_portfolio(),
            example_portfolio_problem(),
        ):
            assert problem.validate() == [], problem.name

    def test_example_kinds(self) -> None:
        assert example_budget_portfolio().allocation_kind.name.lower() == "continuous"
        assert example_portfolio_problem().allocation_kind.name.lower() == "binary"
        assert example_risk_adjusted_portfolio().risk is not None
        assert example_minimize_risk_portfolio().constraints[0].name == "cardinality"

    def test_canonical_problem_is_risk_adjusted(self) -> None:
        assert example_portfolio_problem().name == "qmq08_risk_adjusted"
        assert example_portfolio_problem().objectives[0].name == "return_minus_risk"

    def test_budget_example_has_position_limits(self) -> None:
        assert any(c.name == "positions" for c in example_budget_portfolio().constraints)
        assert any(c.name == "cash_floor" for c in example_budget_portfolio().constraints)

    def test_examples_solve_classically(self) -> None:
        optimizer = PortfolioOptimizer(default_seed=5)
        for problem in (
            example_maximize_return_portfolio(),
            example_minimize_risk_portfolio(),
            example_risk_adjusted_portfolio(),
            example_group_constraints_portfolio(),
        ):
            solution = optimizer.solve(problem, strategy="classical").solution
            assert solution is not None
            assert solution.feasible is True, problem.name


# ----------------------------------------------------------------------
# public API
# ----------------------------------------------------------------------


class TestPublicAPI:
    def test_root_exports(self) -> None:
        import quantsmind.quantum as qq

        for name in (
            "OptimizationConfiguration",
            "PortfolioOptimizationProblem",
            "PortfolioFormulationAdapter",
            "PortfolioAssetMapper",
            "PortfolioOptimizer",
            "PortfolioMetrics",
            "PortfolioComponent",
            "PortfolioSolution",
            "PortfolioOptimizationResult",
            "example_portfolio_problem",
        ):
            assert hasattr(qq, name), name

    def test_finance_exports(self) -> None:
        import quantsmind.quantum.finance as finance

        for name in (
            "PortfolioOptimizationProblem",
            "PortfolioOptimizer",
            "PortfolioSolution",
            "example_risk_adjusted_portfolio",
        ):
            assert hasattr(finance, name), name


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
            timeout=180,
        )
        return run.returncode, run.stdout

    def test_import_and_construction_blocked(self) -> None:
        rc, out = self._blocked_rc(
            """
from quantsmind.quantum.finance import (
    PortfolioOptimizationProblem,
    OptimizationConfiguration,
    example_portfolio_universe,
)
from quantsmind.quantum.finance.objectives import ExpectedReturnObjective
problem = PortfolioOptimizationProblem(
    name="blocked",
    universe=example_portfolio_universe(),
    objectives=[ExpectedReturnObjective("expected_return")],
    optimization_config=OptimizationConfiguration(preferred_strategy="classical"),
)
assert problem.validate() == []
assert problem.decision_variables[0].name == "x0"
print("PORTFOLIO_OK")
"""
        )
        assert rc == 0, out
        assert "PORTFOLIO_OK" in out

    def test_classical_solve_blocked(self) -> None:
        rc, out = self._blocked_rc(
            """
from quantsmind.quantum.finance.portfolio import PortfolioOptimizer
from quantsmind.quantum.finance.portfolio_examples import example_maximize_return_portfolio
result = PortfolioOptimizer(default_seed=7).solve(
    example_maximize_return_portfolio(), strategy="classical"
)
solution = result.solution
assert solution is not None
assert solution.feasible is True
assert solution.objective_value == 0.2
assert result.interpretation is not None
print("PORTFOLIO_OK")
"""
        )
        assert rc == 0, out
        assert "PORTFOLIO_OK" in out

    def test_classical_benchmark_blocked(self) -> None:
        rc, out = self._blocked_rc(
            """
from quantsmind.quantum.finance.portfolio import PortfolioOptimizer
from quantsmind.quantum.finance.portfolio_examples import example_risk_adjusted_portfolio
result = PortfolioOptimizer(default_seed=7).benchmark(
    example_risk_adjusted_portfolio(), strategy="classical"
)
assert result.benchmark is not None
assert result.benchmark.status == "executed"
assert result.interpretation is not None
print("PORTFOLIO_OK")
"""
        )
        assert rc == 0, out
        assert "PORTFOLIO_OK" in out

    def test_quantum_request_honest_downgrade_blocked(self) -> None:
        rc, out = self._blocked_rc(
            """
from quantsmind.quantum.finance.portfolio import PortfolioOptimizer
from quantsmind.quantum.finance.portfolio_examples import example_maximize_return_portfolio
result = PortfolioOptimizer(default_seed=7).solve(
    example_maximize_return_portfolio(), strategy="quantum"
)
solution = result.solution
assert solution is not None
assert result.report is not None
assert result.report.strategy.name.lower() == "classical"
assert solution.feasible is True
print("PORTFOLIO_OK")
"""
        )
        assert rc == 0, out
        assert "PORTFOLIO_OK" in out

    def test_interpretation_blocked(self) -> None:
        rc, out = self._blocked_rc(
            """
from quantsmind.quantum.finance.portfolio_examples import example_risk_adjusted_portfolio
from quantsmind.quantum.finance.portfolio import (
    PortfolioFormulationAdapter,
    PortfolioOptimizer,
)
from quantsmind.quantum.result.result_interpretation import ResultInterpreter
result = PortfolioOptimizer(default_seed=7).solve(
    example_risk_adjusted_portfolio(), strategy="classical"
)
assert result.interpretation.status.value == "executed"
assert result.interpretation.solution_quality.value == "feasible"
print("PORTFOLIO_OK")
"""
        )
        assert rc == 0, out
        assert "PORTFOLIO_OK" in out
