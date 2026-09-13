"""QMQ-07 Finance Domain Foundation tests.

Covers asset/instrument models, the asset universe, risk matrices, budget,
allocation weights, financial constraints and objectives, the
FinancialProblem model, the finance -> QMQ formulation adapter, the
deterministic asset <-> variable mapping with solution decoding, provenance
integration, the canonical synthetic examples and a MicroQuantum-free
end-to-end run through the existing QUBO infrastructure.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

from quantsmind.quantum import (
    Allocation,
    AllocationKind,
    Asset,
    AssetMapping,
    AssetUniverse,
    Budget,
    BudgetConstraint,
    CardinalityConstraint,
    Constraint,
    DecodedAsset,
    DomainContext,
    ExhaustiveSolver,
    ExpectedReturnObjective,
    FinanceAssetMapper,
    FinanceError,
    FinanceFormulationAdapter,
    FinanceValidationError,
    FinancialContext,
    FinancialInstrument,
    FinancialProblem,
    GroupAllocationConstraint,
    Objective,
    ObjectiveSense,
    OptimizationModel,
    PositionLimitConstraint,
    ProblemMapper,
    QuantumProblem,
    QUBOMapper,
    RiskAdjustedObjective,
    RiskMatrix,
    RiskObjective,
    VariableType,
    WeightBoundsConstraint,
    constraint_from_dict,
    objective_from_dict,
    synthetic_asset,
)

_SRC = str(Path(__file__).parents[3] / "src")


# ----------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------


def _asset(
    identifier: str,
    expected_return: float = 0.05,
    *,
    volatility: float | None = 0.1,
    asset_class: str = "equity",
) -> Asset:
    return synthetic_asset(identifier, expected_return, volatility, asset_class=asset_class)


def _universe(identifiers: list[str] | None = None) -> AssetUniverse:
    if identifiers is None:
        identifiers = ["A", "B", "C"]
    return AssetUniverse(assets=[_asset(identifier) for identifier in identifiers])


def _risk3() -> RiskMatrix:
    return RiskMatrix(
        asset_order=["A", "B", "C"],
        matrix=[
            [0.04, 0.01, 0.0],
            [0.01, 0.0225, 0.0],
            [0.0, 0.0, 0.09],
        ],
        volatilities=[0.2, 0.15, 0.3],
    )


def _binary_problem() -> FinancialProblem:
    """A 2-asset binary problem: maximize return minus risk, exactly-one."""
    universe = AssetUniverse(
        assets=[_asset("A", 0.1, volatility=0.2), _asset("B", 0.05, volatility=0.1)]
    )
    risk = RiskMatrix(
        asset_order=["A", "B"],
        matrix=[[0.04, 0.0], [0.0, 0.01]],
        volatilities=[0.2, 0.1],
    )
    return FinancialProblem(
        name="qmq07_e2e",
        universe=universe,
        objectives=[RiskAdjustedObjective("return_minus_risk", risk_aversion=1.0)],
        constraints=[
            BudgetConstraint(name="budget", total=1.0),
            CardinalityConstraint(name="cardinality", min_assets=1, max_assets=1),
        ],
        risk=risk,
        allocation_kind=AllocationKind.BINARY,
    )


# ----------------------------------------------------------------------
# assets / instruments
# ----------------------------------------------------------------------


class TestFinancialInstrument:
    def test_valid_instrument(self) -> None:
        instrument = FinancialInstrument(identifier="AAPL", symbol="AAPL")
        assert instrument.identifier == "AAPL"
        assert instrument.symbol == "AAPL"
        assert instrument.name == "AAPL"

    def test_symbol_and_name_default_to_identifier(self) -> None:
        instrument = FinancialInstrument(identifier="ID-1")
        assert instrument.symbol == "ID-1"
        assert instrument.name == "ID-1"

    def test_empty_identifier_rejected(self) -> None:
        with pytest.raises(FinanceValidationError):
            FinancialInstrument(identifier="")
        with pytest.raises(FinanceValidationError):
            FinancialInstrument(identifier="   ")

    def test_round_trip(self) -> None:
        original = FinancialInstrument(
            identifier="ID", symbol="S", name="Name", description="d", metadata={"k": 1}
        )
        rebuilt = FinancialInstrument.from_dict(original.to_dict())
        assert rebuilt == original


class TestAsset:
    def test_valid_asset(self) -> None:
        asset = Asset(
            identifier="A",
            expected_return=0.1,
            price=10.0,
            volatility=0.2,
            asset_class="equity",
        )
        assert asset.expected_return == 0.1
        assert asset.price == 10.0

    def test_negative_return_allowed(self) -> None:
        asset = Asset(identifier="A", expected_return=-0.03)
        assert asset.expected_return == -0.03

    def test_non_finite_return_rejected(self) -> None:
        with pytest.raises(FinanceValidationError):
            Asset(identifier="A", expected_return=float("nan"))
        with pytest.raises(FinanceValidationError):
            Asset(identifier="A", expected_return=float("inf"))

    def test_price_validated(self) -> None:
        with pytest.raises(FinanceValidationError):
            Asset(identifier="A", price=0.0)
        with pytest.raises(FinanceValidationError):
            Asset(identifier="A", price=-5.0)
        with pytest.raises(FinanceValidationError):
            Asset(identifier="A", price=float("nan"))
        assert Asset(identifier="A", price=7.5).price == 7.5

    def test_volatility_validated(self) -> None:
        with pytest.raises(FinanceValidationError):
            Asset(identifier="A", volatility=-0.1)
        with pytest.raises(FinanceValidationError):
            Asset(identifier="A", volatility=float("inf"))
        assert Asset(identifier="A", volatility=0.0).volatility == 0.0

    def test_round_trip(self) -> None:
        original = Asset(
            identifier="A",
            expected_return=0.12,
            price=10.0,
            volatility=0.2,
            asset_class="equity",
            metadata={"k": "v"},
        )
        rebuilt = Asset.from_dict(original.to_dict())
        assert rebuilt == original


# ----------------------------------------------------------------------
# asset universe
# ----------------------------------------------------------------------


class TestAssetUniverse:
    def test_deterministic_ordering_preserved(self) -> None:
        universe = _universe(["C", "A", "B"])
        assert universe.identifier_order() == ["C", "A", "B"]
        assert [asset.identifier for asset in universe] == ["C", "A", "B"]

    def test_lookup_and_index(self) -> None:
        universe = _universe(["A", "B"])
        assert universe.asset("B").identifier == "B"
        assert universe.index_of("A") == 0
        assert universe.index_of("B") == 1
        assert "A" in universe
        assert universe.has("A")
        assert not universe.has("ZZZ")
        assert len(universe) == 2

    def test_missing_lookup_raises(self) -> None:
        universe = _universe(["A"])
        with pytest.raises(KeyError):
            universe.asset("ZZZ")
        with pytest.raises(KeyError):
            universe.index_of("ZZZ")

    def test_duplicate_detection(self) -> None:
        with pytest.raises(FinanceValidationError):
            AssetUniverse(assets=[_asset("A"), _asset("A")])

    def test_iteration(self) -> None:
        universe = _universe(["A", "B"])
        assert [a.identifier for a in universe] == ["A", "B"]
        assert universe[0].identifier == "A"

    def test_round_trip(self) -> None:
        original = AssetUniverse(name="u", assets=[_asset("A"), _asset("B")])
        rebuilt = AssetUniverse.from_dict(original.to_dict())
        assert rebuilt == original
        assert rebuilt.identifier_order() == ["A", "B"]


# ----------------------------------------------------------------------
# risk
# ----------------------------------------------------------------------


class TestRisk:
    def test_valid_matrix(self) -> None:
        risk = _risk3()
        assert risk.psd is True
        assert risk.psd_validated is True
        assert risk.variance("A") == pytest.approx(0.04)
        assert risk.covariance("A", "B") == pytest.approx(0.01)
        assert risk.covariance("B", "A") == pytest.approx(0.01)

    def test_dimension_mismatch(self) -> None:
        with pytest.raises(FinanceValidationError):
            RiskMatrix(
                asset_order=["A", "B"],
                matrix=[[0.04, 0.01, 0.0], [0.01, 0.02, 0.0], [0.0, 0.0, 0.1]],
            )

    def test_non_square(self) -> None:
        with pytest.raises(FinanceValidationError):
            RiskMatrix(
                asset_order=["A", "B"],
                matrix=[[0.04, 0.01], [0.01, 0.02], [0.0, 0.0]],
            )

    def test_non_finite_entry(self) -> None:
        with pytest.raises(FinanceValidationError):
            RiskMatrix(asset_order=["A", "B"], matrix=[[0.04, float("inf")], [float("inf"), 0.02]])

    def test_asymmetric_beyond_tolerance_rejected(self) -> None:
        with pytest.raises(FinanceValidationError):
            RiskMatrix(asset_order=["A", "B"], matrix=[[0.04, 0.5], [0.0, 0.02]])

    def test_correlations_truth(self) -> None:
        risk = RiskMatrix(
            asset_order=["A", "B"],
            matrix=[[0.04, 0.02], [0.02, 0.01]],
            volatilities=[0.2, 0.1],
        )
        correlation = risk.correlation()
        assert correlation[0][0] == pytest.approx(1.0)
        assert correlation[1][1] == pytest.approx(1.0)
        assert correlation[0][1] == pytest.approx(0.02 / (0.2 * 0.1))

    def test_correlation_requires_volatilities(self) -> None:
        risk = RiskMatrix(asset_order=["A", "B"], matrix=[[0.04, 0.0], [0.0, 0.01]])
        with pytest.raises(FinanceError):
            risk.correlation()

    def test_non_psd_raises(self) -> None:
        with pytest.raises(FinanceValidationError):
            RiskMatrix(asset_order=["A", "B"], matrix=[[1.0, 2.0], [2.0, 1.0]])

    def test_psd_accepted(self) -> None:
        risk = RiskMatrix(asset_order=["A", "B"], matrix=[[2.0, 1.0], [1.0, 2.0]])
        assert risk.psd is True

    def test_round_trip(self) -> None:
        original = _risk3()
        rebuilt = RiskMatrix.from_dict(original.to_dict())
        assert rebuilt.matrix == original.matrix
        assert rebuilt.asset_order == original.asset_order
        assert rebuilt.volatilities == original.volatilities


# ----------------------------------------------------------------------
# context / budget / allocation
# ----------------------------------------------------------------------


class TestFinancialContext:
    def test_defaults(self) -> None:
        context = FinancialContext()
        assert context.currency == ""
        assert context.transaction_cost_rate == 0.0

    def test_validation(self) -> None:
        with pytest.raises(FinanceValidationError):
            FinancialContext(risk_free_rate=float("nan"))
        with pytest.raises(FinanceValidationError):
            FinancialContext(transaction_cost_rate=-0.01)
        with pytest.raises(FinanceValidationError):
            FinancialContext(transaction_cost_rate=float("inf"))

    def test_to_domain_context(self) -> None:
        context = FinancialContext(currency="USD", subdomain="portfolio", risk_free_rate=0.02)
        domain = context.to_domain_context()
        assert isinstance(domain, DomainContext)
        assert domain.domain == "finance"
        assert domain.subdomain == "portfolio"
        assert domain.qualified() == "finance/portfolio"

    def test_round_trip(self) -> None:
        original = FinancialContext(
            currency="USD",
            subdomain="portfolio",
            risk_free_rate=0.02,
            transaction_cost_rate=0.001,
            assumptions={"a": 1},
        )
        rebuilt = FinancialContext.from_dict(original.to_dict())
        assert rebuilt == original


class TestBudget:
    def test_valid(self) -> None:
        budget = Budget(total=1.0, currency="USD", min_allocation=0.0, max_allocation=1.0)
        assert budget.total == 1.0

    def test_invalid_total(self) -> None:
        with pytest.raises(FinanceValidationError):
            Budget(total=0.0)
        with pytest.raises(FinanceValidationError):
            Budget(total=-1.0)
        with pytest.raises(FinanceValidationError):
            Budget(total=float("nan"))

    def test_inconsistent_bounds(self) -> None:
        with pytest.raises(FinanceValidationError):
            Budget(total=1.0, min_allocation=0.8, max_allocation=0.2)

    def test_round_trip(self) -> None:
        original = Budget(total=1.0, currency="USD")
        rebuilt = Budget.from_dict(original.to_dict())
        assert rebuilt == original


class TestAllocation:
    def test_kind_parse(self) -> None:
        assert AllocationKind.parse("binary") is AllocationKind.BINARY
        assert AllocationKind.parse(AllocationKind.CONTINUOUS) is AllocationKind.CONTINUOUS
        with pytest.raises(FinanceValidationError):
            AllocationKind.parse("bogus")

    def test_kinds_are_distinct(self) -> None:
        assert AllocationKind.CONTINUOUS is not AllocationKind.BINARY
        assert AllocationKind.CONTINUOUS is not AllocationKind.INTEGER

    def test_valid_allocation(self) -> None:
        allocation = Allocation(asset_order=["A", "B"], weights={"A": 0.4}, kind="continuous")
        assert allocation.weight("A") == 0.4
        assert allocation.weight("B") == 0.0
        assert allocation.total() == pytest.approx(0.4)

    def test_unknown_asset_rejected(self) -> None:
        with pytest.raises(FinanceValidationError):
            Allocation(asset_order=["A"], weights={"ZZZ": 1.0})

    def test_duplicate_order_rejected(self) -> None:
        with pytest.raises(FinanceValidationError):
            Allocation(asset_order=["A", "A"], weights={"A": 1.0})

    def test_non_finite_rejected(self) -> None:
        with pytest.raises(FinanceValidationError):
            Allocation(asset_order=["A"], weights={"A": float("nan")})

    def test_round_trip(self) -> None:
        original = Allocation(asset_order=["A", "B"], weights={"A": 0.4}, kind="binary")
        rebuilt = Allocation.from_dict(original.to_dict())
        assert rebuilt == original
        assert rebuilt.kind is AllocationKind.BINARY


# ----------------------------------------------------------------------
# constraints
# ----------------------------------------------------------------------


class TestBudgetConstraint:
    def test_materializes_le(self) -> None:
        constraint = BudgetConstraint(name="budget", total=0.8)
        [qc] = constraint.to_quantum_constraints(_universe())
        assert isinstance(qc, Constraint)
        assert qc.operator.value == "<="
        assert qc.value == 0.8
        assert qc.expression == "1.0*x0 + 1.0*x1 + 1.0*x2"

    def test_costs_used(self) -> None:
        constraint = BudgetConstraint(name="budget", total=10.0, costs={"A": 2.0, "B": 3.0})
        [qc] = constraint.to_quantum_constraints(_universe())
        assert qc.expression == "2.0*x0 + 3.0*x1 + 1.0*x2"

    def test_invalid_total(self) -> None:
        with pytest.raises(FinanceValidationError):
            BudgetConstraint(name="budget", total=0.0)

    def test_unknown_cost_asset_reported(self) -> None:
        constraint = BudgetConstraint(name="budget", total=1.0, costs={"ZZZ": 1.0})
        assert any("ZZZ" in issue for issue in constraint.validate(_universe()))

    def test_round_trip(self) -> None:
        original = BudgetConstraint(name="budget", total=1.0, currency="USD")
        rebuilt = BudgetConstraint.from_dict(original.to_dict())
        assert rebuilt == original


class TestWeightBounds:
    def test_materializes_lower_and_upper(self) -> None:
        constraint = WeightBoundsConstraint(name="w", bounds={"A": (0.1, 0.5)})
        constraints = constraint.to_quantum_constraints(_universe())
        assert [c.expression for c in constraints] == ["1.0*x0", "1.0*x0"]
        assert [c.value for c in constraints] == [0.1, 0.5]

    def test_invalid_bounds(self) -> None:
        with pytest.raises(FinanceValidationError):
            WeightBoundsConstraint(name="w", bounds={"A": (0.5, 0.1)})

    def test_missing_reference(self) -> None:
        constraint = WeightBoundsConstraint(name="w", bounds={"ZZZ": (0.0, 1.0)})
        assert any("ZZZ" in issue for issue in constraint.validate(_universe()))

    def test_round_trip(self) -> None:
        original = WeightBoundsConstraint(name="w", bounds={"A": (0.1, 0.5)})
        rebuilt = WeightBoundsConstraint.from_dict(original.to_dict())
        assert rebuilt == original


class TestCardinality:
    def test_materializes_both_sides(self) -> None:
        constraint = CardinalityConstraint(name="card", min_assets=2, max_assets=3)
        constraints = constraint.to_quantum_constraints(_universe(["A", "B", "C", "D"]))
        assert len(constraints) == 2
        bodies = {(c.operator.value, c.value): c.expression for c in constraints}
        assert bodies[("<=", 3.0)] == "1.0*x0 + 1.0*x1 + 1.0*x2 + 1.0*x3"
        assert bodies[(">=", 2.0)] == "1.0*x0 + 1.0*x1 + 1.0*x2 + 1.0*x3"

    def test_invalid_bounds(self) -> None:
        with pytest.raises(FinanceValidationError):
            CardinalityConstraint(name="card", min_assets=3, max_assets=1)

    def test_exceeds_universe_reported(self) -> None:
        constraint = CardinalityConstraint(name="card", min_assets=5)
        assert any("universe" in issue for issue in constraint.validate(_universe(["A", "B"])))

    def test_round_trip(self) -> None:
        original = CardinalityConstraint(name="card", min_assets=1, max_assets=3)
        rebuilt = CardinalityConstraint.from_dict(original.to_dict())
        assert rebuilt == original


class TestPositionLimit:
    def test_materializes_limits(self) -> None:
        constraint = PositionLimitConstraint(name="pos", asset_ids=["A"], lower=0.0, upper=0.5)
        constraints = constraint.to_quantum_constraints(_universe())
        assert len(constraints) == 2
        assert constraints[0].value == 0.0
        assert constraints[1].value == 0.5

    def test_requires_assets(self) -> None:
        with pytest.raises(FinanceValidationError):
            PositionLimitConstraint(name="pos", asset_ids=[])

    def test_inconsistent_limits(self) -> None:
        with pytest.raises(FinanceValidationError):
            PositionLimitConstraint(name="pos", asset_ids=["A"], lower=0.5, upper=0.1)

    def test_missing_reference(self) -> None:
        constraint = PositionLimitConstraint(name="pos", asset_ids=["ZZZ"])
        assert any("ZZZ" in issue for issue in constraint.validate(_universe()))

    def test_round_trip(self) -> None:
        original = PositionLimitConstraint(name="pos", asset_ids=["A"], lower=0.0, upper=0.4)
        rebuilt = PositionLimitConstraint.from_dict(original.to_dict())
        assert rebuilt == original


class TestGroupAllocation:
    def test_materializes_group_sum(self) -> None:
        universe = AssetUniverse(
            assets=[
                _asset("A", asset_class="equity"),
                _asset("B", asset_class="equity"),
                _asset("C", asset_class="bond"),
            ]
        )
        constraint = GroupAllocationConstraint(name="equity_cap", group="equity", upper=0.7)
        [qc] = constraint.to_quantum_constraints(universe)
        assert qc.expression == "1.0*x0 + 1.0*x1"
        assert qc.value == 0.7

    def test_group_with_no_assets_reported(self) -> None:
        constraint = GroupAllocationConstraint(name="g", group="crypto")
        assert "no assets" in constraint.validate(_universe())[0]

    def test_requires_group(self) -> None:
        with pytest.raises(FinanceValidationError):
            GroupAllocationConstraint(name="g", group="")

    def test_round_trip(self) -> None:
        original = GroupAllocationConstraint(name="g", group="equity", upper=0.8)
        rebuilt = GroupAllocationConstraint.from_dict(original.to_dict())
        assert rebuilt == original


class TestConstraintDispatch:
    def test_from_dict_dispatch(self) -> None:
        for constraint in (
            BudgetConstraint(name="b", total=1.0),
            WeightBoundsConstraint(name="w", bounds={"A": (0.0, 1.0)}),
            CardinalityConstraint(name="c", min_assets=1),
            PositionLimitConstraint(name="p", asset_ids=["A"]),
            GroupAllocationConstraint(name="g", group="equity"),
        ):
            rebuilt = constraint_from_dict(constraint.to_dict())
            assert type(rebuilt) is type(constraint)
            assert rebuilt == constraint

    def test_unknown_kind(self) -> None:
        with pytest.raises(FinanceValidationError):
            constraint_from_dict({"kind": "bogus", "name": "x"})


# ----------------------------------------------------------------------
# objectives
# ----------------------------------------------------------------------


class TestObjectives:
    def test_expected_return_maximizes(self) -> None:
        objective = ExpectedReturnObjective("expected_return")
        qc = objective.to_quantum_objective(_universe())
        assert isinstance(qc, Objective)
        assert qc.sense is ObjectiveSense.MAXIMIZE
        assert qc.expression == "0.05*x0 + 0.05*x1 + 0.05*x2"

    def test_expected_return_uses_asset_data(self) -> None:
        universe = AssetUniverse(assets=[_asset("A", 0.12), _asset("B", -0.03)])
        qc = ExpectedReturnObjective("expected_return").to_quantum_objective(universe)
        assert qc.expression == "0.12*x0 + -0.03*x1"

    def test_risk_minimizes(self) -> None:
        risk = _risk3()
        qc = RiskObjective("risk").to_quantum_objective(_universe(), risk=risk)
        assert qc.sense is ObjectiveSense.MINIMIZE
        assert "x0*x0" in qc.expression or "x0*x0" in str(qc.expression)
        assert "x0*x1" in str(qc.expression)

    def test_risk_requires_matrix(self) -> None:
        with pytest.raises(FinanceValidationError):
            RiskObjective("risk").to_quantum_objective(_universe())
        objective = RiskObjective("risk")
        assert "requires a risk matrix" in objective.validate(_universe(), None)[0]

    def test_risk_adjusted_maximizes_combined(self) -> None:
        objective = RiskAdjustedObjective("ret_minus_risk", risk_aversion=2.0)
        qc = objective.to_quantum_objective(_universe(), risk=_risk3())
        assert qc.sense is ObjectiveSense.MAXIMIZE
        assert "0.05*x0 + 0.05*x1 + 0.05*x2 - 2.0*(" in qc.expression

    def test_risk_adjusted_zero_aversion_is_linear(self) -> None:
        objective = RiskAdjustedObjective("ret", risk_aversion=0.0)
        qc = objective.to_quantum_objective(_universe(), risk=_risk3())
        assert qc.expression == "0.05*x0 + 0.05*x1 + 0.05*x2"

    def test_risk_adjusted_requires_risk(self) -> None:
        objective = RiskAdjustedObjective("ret_minus_risk", risk_aversion=1.0)
        with pytest.raises(FinanceValidationError):
            objective.to_quantum_objective(_universe())

    def test_negative_risk_aversion_rejected(self) -> None:
        with pytest.raises(FinanceValidationError):
            RiskAdjustedObjective("o", risk_aversion=-1.0)

    def test_sense_enum_reused(self) -> None:
        assert (
            ExpectedReturnObjective("o").to_quantum_objective(_universe()).sense
            is ObjectiveSense.MAXIMIZE
        )
        assert (
            RiskObjective("o").to_quantum_objective(_universe(), risk=_risk3()).sense
            is ObjectiveSense.MINIMIZE
        )

    def test_dispatch_round_trip(self) -> None:
        for objective in (
            ExpectedReturnObjective("r"),
            RiskObjective("risk"),
            RiskAdjustedObjective("adj", risk_aversion=3.0),
        ):
            rebuilt = objective_from_dict(objective.to_dict())
            assert type(rebuilt) is type(objective)
            assert rebuilt == objective

    def test_unknown_kind(self) -> None:
        with pytest.raises(FinanceValidationError):
            objective_from_dict({"kind": "bogus", "name": "x"})


# ----------------------------------------------------------------------
# financial problem
# ----------------------------------------------------------------------


class TestFinancialProblem:
    def test_valid_problem(self) -> None:
        problem = FinancialProblem(
            name="p",
            universe=_universe(),
            objectives=[ExpectedReturnObjective("r")],
        )
        assert problem.validate() == []
        assert len(problem.decision_variables) == 3
        assert [v.name for v in problem.decision_variables] == ["x0", "x1", "x2"]

    def test_empty_universe_reported(self) -> None:
        problem = FinancialProblem(
            name="p",
            universe=AssetUniverse(assets=[]),
            objectives=[ExpectedReturnObjective("r")],
        )
        assert any("no assets" in issue for issue in problem.validate())

    def test_no_objectives_reported(self) -> None:
        problem = FinancialProblem(name="p", universe=_universe(), objectives=[])
        assert any("no objectives" in issue for issue in problem.validate())

    def test_duplicate_objective_names(self) -> None:
        with pytest.raises(FinanceValidationError):
            FinancialProblem(
                name="p",
                universe=_universe(),
                objectives=[ExpectedReturnObjective("r"), ExpectedReturnObjective("r")],
            )

    def test_duplicate_constraint_names(self) -> None:
        with pytest.raises(FinanceValidationError):
            FinancialProblem(
                name="p",
                universe=_universe(),
                objectives=[ExpectedReturnObjective("r")],
                constraints=[
                    BudgetConstraint(name="b", total=1.0),
                    CardinalityConstraint(name="b", min_assets=1),
                ],
            )

    def test_risk_dimension_mismatch_reported(self) -> None:
        risk = RiskMatrix(asset_order=["A", "B"], matrix=[[0.04, 0.0], [0.0, 0.01]])
        problem = FinancialProblem(
            name="p",
            universe=_universe(["A", "B", "C"]),
            objectives=[RiskObjective("risk")],
            risk=risk,
        )
        assert any("asset_order" in issue for issue in problem.validate())

    def test_risk_objective_without_risk_reported(self) -> None:
        problem = FinancialProblem(
            name="p",
            universe=_universe(),
            objectives=[RiskObjective("risk")],
        )
        assert any("risk matrix" in issue for issue in problem.validate())

    def test_raise_if_invalid(self) -> None:
        problem = FinancialProblem(name="p", universe=_universe(), objectives=[])
        with pytest.raises(FinanceValidationError):
            problem.raise_if_invalid()

    def test_decision_variables_binary(self) -> None:
        problem = FinancialProblem(
            name="p",
            universe=_universe(["A", "B"]),
            objectives=[ExpectedReturnObjective("r")],
            allocation_kind="binary",
        )
        variables = problem.decision_variables
        assert [v.type for v in variables] == [VariableType.BINARY, VariableType.BINARY]
        assert [v.name for v in variables] == ["x0", "x1"]
        assert variables[0].metadata["asset_id"] == "A"

    def test_decision_variables_continuous(self) -> None:
        problem = FinancialProblem(
            name="p",
            universe=_universe(["A"]),
            objectives=[ExpectedReturnObjective("r")],
            allocation_kind="continuous",
        )
        [variable] = problem.decision_variables
        assert variable.type is VariableType.CONTINUOUS
        assert variable.lower_bound == 0.0

    def test_integer_representation_deferred(self) -> None:
        problem = FinancialProblem(
            name="p",
            universe=_universe(["A"]),
            objectives=[ExpectedReturnObjective("r")],
            allocation_kind="integer",
        )
        with pytest.raises(FinanceValidationError):
            _ = problem.decision_variables

    def test_round_trip(self) -> None:
        problem = FinancialProblem(
            name="p",
            universe=_universe(["A", "B"]),
            objectives=[
                ExpectedReturnObjective("r"),
                RiskAdjustedObjective("adj", risk_aversion=1.0),
            ],
            constraints=[
                BudgetConstraint(name="b", total=1.0),
                CardinalityConstraint(name="c", min_assets=1, max_assets=2),
                WeightBoundsConstraint(name="w", bounds={"A": (0.0, 0.8)}),
                PositionLimitConstraint(name="p", asset_ids=["B"], upper=0.9),
                GroupAllocationConstraint(name="g", group="equity", upper=1.0),
            ],
            context=FinancialContext(currency="USD"),
            risk=_risk3(),
            allocation_kind="binary",
            metadata={"tag": "t"},
        )
        rebuilt = FinancialProblem.from_dict(problem.to_dict())
        assert rebuilt.name == problem.name
        assert [o.name for o in rebuilt.objectives] == [o.name for o in problem.objectives]
        assert [c.name for c in rebuilt.constraints] == [c.name for c in problem.constraints]
        assert rebuilt.allocation_kind is AllocationKind.BINARY
        assert (
            rebuilt.risk is not None and rebuilt.risk.matrix == problem.risk.matrix
            if problem.risk
            else True
        )

    def test_to_budget_constraint(self) -> None:
        problem = FinancialProblem(
            name="p",
            universe=_universe(),
            objectives=[ExpectedReturnObjective("r")],
            allocation_kind="binary",
        )
        problem.to_budget_constraint(Budget(total=1.0, currency="USD"))
        assert problem.constraint_exists("budget")
        constraint = problem.constraints[0]
        assert isinstance(constraint, BudgetConstraint)
        assert constraint.total == 1.0


# ----------------------------------------------------------------------
# formulation adapter
# ----------------------------------------------------------------------


class TestFormulationAdapter:
    def test_to_quantum_problem(self) -> None:
        problem = _binary_problem()
        adapter = FinanceFormulationAdapter()
        quantum = adapter.to_quantum_problem(problem)
        assert isinstance(quantum, QuantumProblem)
        assert quantum.name == "qmq07_e2e"
        assert isinstance(quantum.domain, DomainContext)
        assert quantum.domain.domain == "finance"
        assert [v.name for v in quantum.variables] == ["x0", "x1"]
        assert [v.type for v in quantum.variables] == [VariableType.BINARY, VariableType.BINARY]

    def test_objective_preserved(self) -> None:
        quantum = FinanceFormulationAdapter().to_quantum_problem(_binary_problem())
        [objective] = quantum.objectives
        assert objective.name == "return_minus_risk"
        assert objective.sense is ObjectiveSense.MAXIMIZE

    def test_constraints_preserved(self) -> None:
        quantum = FinanceFormulationAdapter().to_quantum_problem(_binary_problem())
        names = {c.name for c in quantum.constraints}
        assert {"budget", "cardinality_min", "cardinality_max"} <= names

    def test_deterministic_variable_ordering(self) -> None:
        adapter = FinanceFormulationAdapter()
        first = adapter.to_quantum_problem(_binary_problem())
        second = adapter.to_quantum_problem(_binary_problem())
        assert [v.name for v in first.variables] == [v.name for v in second.variables]
        assert [o.expression for o in first.objectives] == [o.expression for o in second.objectives]

    def test_domain_context_from_financial_context(self) -> None:
        problem = FinancialProblem(
            name="p",
            universe=_universe(["A"]),
            objectives=[ExpectedReturnObjective("r")],
            context=FinancialContext(currency="USD", subdomain="portfolio"),
            allocation_kind="binary",
        )
        quantum = FinanceFormulationAdapter().to_quantum_problem(problem)
        assert quantum.domain.qualified() == "finance/portfolio"
        assert quantum.domain.context_metadata["currency"] == "USD"

    def test_preferred_strategy_passthrough(self) -> None:
        quantum = FinanceFormulationAdapter().to_quantum_problem(
            _binary_problem(), preferred_strategy="classical"
        )
        assert quantum.preferred_strategy is not None

    def test_formulate_uses_existing_infrastructure(self) -> None:
        model = ProblemMapper().map(
            FinanceFormulationAdapter().to_quantum_problem(_binary_problem())
        )
        assert isinstance(model, OptimizationModel)
        assert model.problem_name == "qmq07_e2e"

    def test_invalid_problem_rejected(self) -> None:
        problem = FinancialProblem(name="p", universe=_universe(), objectives=[])
        with pytest.raises(FinanceValidationError):
            FinanceFormulationAdapter().to_quantum_problem(problem)


# ----------------------------------------------------------------------
# mapping / decoding
# ----------------------------------------------------------------------


class TestMappingAndDecoding:
    def test_asset_to_variable(self) -> None:
        mapping = FinanceAssetMapper().map(_binary_problem())
        assert mapping.asset_order == ["A", "B"]
        assert mapping.variable_names == ["x0", "x1"]
        assert mapping.variable("A") == "x0"
        assert mapping.variable("B") == "x1"
        assert mapping.index("B") == 1
        assert mapping.asset("x0") == "A"

    def test_unknown_asset_raises(self) -> None:
        mapping = FinanceAssetMapper().map(_binary_problem())
        with pytest.raises(KeyError):
            mapping.variable("ZZZ")
        with pytest.raises(KeyError):
            mapping.asset("x9")

    def test_decode_assignments(self) -> None:
        problem = FinancialProblem(
            name="p",
            universe=_universe(["A", "B", "C"]),
            objectives=[ExpectedReturnObjective("r")],
            allocation_kind="binary",
        )
        mapping = FinanceAssetMapper().map(problem)
        decoded = mapping.decode_assignments({"x0": 1, "x1": 0, "x2": 1})
        assert isinstance(decoded, list)
        assert isinstance(decoded[0], DecodedAsset)
        assert [(d.asset_id, d.selected) for d in decoded] == [
            ("A", True),
            ("B", False),
            ("C", True),
        ]
        assert [d.value for d in decoded] == [1.0, 0.0, 1.0]

    def test_decode_ignores_unknown_keys(self) -> None:
        problem = FinancialProblem(
            name="p",
            universe=_universe(["A"]),
            objectives=[ExpectedReturnObjective("r")],
            allocation_kind="binary",
        )
        mapping = FinanceAssetMapper().map(problem)
        decoded = mapping.decode_assignments({"x0": 1, "x_slack": 1, "ZZZ": 1})
        assert [(d.asset_id, d.value) for d in decoded] == [("A", 1.0)]

    def test_round_trip(self) -> None:
        mapping = FinanceAssetMapper().map(_binary_problem())
        rebuilt = AssetMapping.from_dict(mapping.to_dict())
        assert rebuilt == mapping


# ----------------------------------------------------------------------
# provenance integration
# ----------------------------------------------------------------------


class TestProvenanceIntegration:
    def test_finance_metadata_present(self) -> None:
        adapter = FinanceFormulationAdapter()
        problem = _binary_problem()
        quantum = adapter.to_quantum_problem(problem)
        meta = quantum.metadata
        assert meta["domain_layer"] == "finance"
        assert meta["asset_order"] == ["A", "B"]
        assert meta["allocation_kind"] == "binary"
        assert meta["universe"] == ""

    def test_asset_ordering_and_assumptions_preserved(self) -> None:
        problem = FinancialProblem(
            name="p",
            universe=_universe(["C", "A", "B"]),
            objectives=[ExpectedReturnObjective("r")],
            context=FinancialContext(assumptions={"estimation": "none"}),
            allocation_kind="binary",
        )
        quantum = FinanceFormulationAdapter().to_quantum_problem(problem)
        assert quantum.metadata["asset_order"] == ["C", "A", "B"]
        assert quantum.metadata["assumptions"] == {"estimation": "none"}
        assert quantum.provenance["domain_layer"] == "finance"
        assert quantum.provenance["asset_order"] == ["C", "A", "B"]

    def test_formulation_metadata_flows(self) -> None:
        model = FinanceFormulationAdapter().formulate(_binary_problem())
        assert model.metadata["domain_layer"] == "finance"
        assert model.metadata["asset_order"] == ["A", "B"]

    def test_metadata_json_safe(self) -> None:
        quantum = FinanceFormulationAdapter().to_quantum_problem(_binary_problem())
        serialized = quantum.metadata
        import json

        json.dumps(serialized)


# ----------------------------------------------------------------------
# examples
# ----------------------------------------------------------------------


class TestExamples:
    def test_asset_universe_example(self) -> None:
        universe = __import__(
            "quantsmind.quantum", fromlist=["example_asset_universe"]
        ).example_asset_universe()
        assert len(universe) == 4
        assert universe.identifier_order()[0] == "TECH-A"

    def test_budget_example(self) -> None:
        budget = __import__("quantsmind.quantum", fromlist=["example_budget"]).example_budget()
        assert budget.total == 1.0
        assert budget.max_allocation == 1.0

    def test_risk_matrix_example(self) -> None:
        risk = __import__(
            "quantsmind.quantum", fromlist=["example_risk_matrix"]
        ).example_risk_matrix()
        assert risk.psd is True
        assert len(risk.asset_order) == 3

    @pytest.mark.parametrize(
        "factory",
        ["example_return_problem", "example_risk_problem", "example_combined_problem"],
    )
    def test_problem_examples_valid(self, factory: str) -> None:
        problem = getattr(__import__("quantsmind.quantum", fromlist=[factory]), factory)()
        assert isinstance(problem, FinancialProblem)
        assert problem.validate() == []

    def test_synthetic_asset_helper(self) -> None:
        asset = synthetic_asset("X", 0.02, asset_class="cash")
        assert asset.asset_class == "cash"
        assert asset.symbol == "X"


# ----------------------------------------------------------------------
# end-to-end across the existing QMQ pipeline (no MicroQuantum)
# ----------------------------------------------------------------------


class TestIntegrationEndToEnd:
    def test_binary_problem_through_existing_qubo(self) -> None:
        problem = _binary_problem()
        adapter = FinanceFormulationAdapter()
        problem.raise_if_invalid()
        quantum = adapter.to_quantum_problem(problem)
        assert isinstance(quantum, QuantumProblem)

        mapping_result = QUBOMapper().map(quantum, strategy="classical")
        qubo = mapping_result.payload
        assert qubo is not None

        solved = ExhaustiveSolver(max_variables=12).solve(qubo)
        assert solved.feasible

        mapping = FinanceAssetMapper().map(problem)
        decoded = mapping.decode_assignments(solved.assignment)
        selected = [d.asset_id for d in decoded if d.selected]
        assert len(selected) == 1

    def test_existing_formulation_consumed_unchanged(self) -> None:
        quantum = FinanceFormulationAdapter().to_quantum_problem(_binary_problem())
        model = ProblemMapper().map(quantum)
        assert model.problem_name == "qmq07_e2e"
        assert [v for v in model.variables] == ["x0", "x1"]


# ----------------------------------------------------------------------
# no microquantum dependency
# ----------------------------------------------------------------------


class TestNoMicroQuantumDependency:
    @staticmethod
    def _block_all_microquantum_imports(source: str) -> int:
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
            timeout=120,
        )
        if run.returncode != 0:
            print(run.stderr)
        return run.returncode

    def test_domain_construction_without_microquantum(self) -> None:
        assert (
            self._block_all_microquantum_imports(
                """
from quantsmind.quantum import (
    Asset,
    AssetUniverse,
    FinancialProblem,
    RiskMatrix,
    ExpectedReturnObjective,
    BudgetConstraint,
    FinanceFormulationAdapter,
    FinanceAssetMapper,
)

universe = AssetUniverse(
    assets=[Asset("A", expected_return=0.1, volatility=0.2),
            Asset("B", expected_return=0.05, volatility=0.1)]
)
problem = FinancialProblem(
    name="no-mq", universe=universe,
    objectives=[ExpectedReturnObjective("ret")],
    constraints=[BudgetConstraint(name="b", total=1.0)],
    risk=RiskMatrix(asset_order=["A", "B"],
                    matrix=[[0.04, 0.0], [0.0, 0.01]]),
    allocation_kind="binary",
)
assert problem.validate() == []
quantum = FinanceFormulationAdapter().to_quantum_problem(problem)
assert len(quantum.variables) == 2
mapping = FinanceAssetMapper().map(problem)
assert mapping.variable("A") == "x0"
print("FINANCE_OK")
"""
            )
            == 0
        )

    def test_generic_imports_still_work_without_microquantum(self) -> None:
        assert (
            self._block_all_microquantum_imports(
                """
import quantsmind.quantum
from quantsmind.quantum import QuantumProblem, Variable, Objective, ObjectiveSense
problem = QuantumProblem("plain")
problem.add_variable(Variable.binary("a"))
assert problem.size == 1
print("IMPORT_OK")
"""
            )
            == 0
        )
