"""Canonical synthetic Finance examples (QMQ-07 §23).

Every example is deterministic, tiny and built entirely from supplied data.
They are **synthetic examples**, not market recommendations, and not
investment advice.
"""

from __future__ import annotations

from quantsmind.quantum.finance.budget import Budget
from quantsmind.quantum.finance.constraints import (
    BudgetConstraint,
    CardinalityConstraint,
    WeightBoundsConstraint,
)
from quantsmind.quantum.finance.context import FinancialContext
from quantsmind.quantum.finance.models import Asset, AssetUniverse, FinancialProblem
from quantsmind.quantum.finance.objectives import (
    ExpectedReturnObjective,
    RiskAdjustedObjective,
    RiskObjective,
)
from quantsmind.quantum.finance.risk import RiskMatrix
from quantsmind.quantum.finance.weights import AllocationKind

__all__ = [
    "synthetic_asset",
    "example_asset_universe",
    "example_budget",
    "example_risk_matrix",
    "example_return_problem",
    "example_risk_problem",
    "example_combined_problem",
    "example_financial_problem",
]


def synthetic_asset(
    identifier: str,
    expected_return: float,
    volatility: float | None = None,
    *,
    symbol: str = "",
    asset_class: str = "equity",
    price: float | None = None,
) -> Asset:
    """Build one deterministic synthetic asset."""
    return Asset(
        identifier=identifier,
        symbol=symbol or identifier,
        expected_return=expected_return,
        volatility=volatility,
        asset_class=asset_class,
        price=price,
    )


def _universe() -> AssetUniverse:
    return AssetUniverse(
        name="qmq07_synthetic",
        assets=[
            synthetic_asset("TECH-A", 0.12, 0.25, symbol="TECH-A", asset_class="equity"),
            synthetic_asset("TECH-B", 0.08, 0.18, symbol="TECH-B", asset_class="equity"),
            synthetic_asset("BOND-A", 0.03, 0.06, symbol="BOND-A", asset_class="bond"),
            synthetic_asset("CASH-A", 0.01, 0.0, symbol="CASH-A", asset_class="cash"),
        ],
    )


def _risk(ticker_ids: list[str]) -> RiskMatrix:
    variances = {
        "TECH-A": 0.25 * 0.25,
        "TECH-B": 0.18 * 0.18,
        "BOND-A": 0.06 * 0.06,
        "CASH-A": 0.0,
    }
    volatilities = {
        "TECH-A": 0.25,
        "TECH-B": 0.18,
        "BOND-A": 0.06,
        "CASH-A": 0.0,
    }
    covariances = {("TECH-A", "TECH-B"): 0.03, ("TECH-B", "BOND-A"): 0.0}
    n = len(ticker_ids)
    matrix: list[list[float]] = [[0.0] * n for _ in range(n)]
    for i, left in enumerate(ticker_ids):
        for j, right in enumerate(ticker_ids):
            if i == j:
                matrix[i][j] = variances[left]
            else:
                pair = covariances.get((left, right), covariances.get((right, left), 0.0))
                matrix[i][j] = pair
    return RiskMatrix(
        asset_order=list(ticker_ids),
        matrix=matrix,
        volatilities=[volatilities[ticker] for ticker in ticker_ids],
    )


def example_asset_universe() -> AssetUniverse:
    """Example 1 — a four-asset universe with supplied expected returns."""
    return _universe()


def example_budget(capital: float = 1.0, name: str = "qmq07_budget") -> Budget:
    """Example 2 — a capital/budget with allocation bounds."""
    return Budget(total=capital, currency="USD", min_allocation=0.0, max_allocation=1.0)


def example_risk_matrix() -> RiskMatrix:
    """Example 3 — a deterministic covariance/risk matrix."""
    return _risk(["TECH-A", "TECH-B", "BOND-A"])


def _context() -> FinancialContext:
    return FinancialContext(
        currency="USD",
        subdomain="portfolio",
        investment_horizon="1Y",
        risk_free_rate=0.02,
        transaction_cost_rate=0.001,
        assumptions={"data_source": "synthetic-supplied", "estimation": "none"},
    )


def example_return_problem() -> FinancialProblem:
    """Example 4 — maximize expected return under a budget."""
    return FinancialProblem(
        name="qmq07_max_return",
        universe=_universe(),
        objectives=[ExpectedReturnObjective("expected_return")],
        constraints=[
            BudgetConstraint(name="budget", total=1.0, currency="USD"),
            CardinalityConstraint(name="cardinality", min_assets=2, max_assets=4),
            WeightBoundsConstraint(
                name="weights", bounds={"TECH-A": (0.0, 0.5), "CASH-A": (0.05, 1.0)}
            ),
        ],
        context=_context(),
        allocation_kind=AllocationKind.BINARY,
    )


def example_risk_problem() -> FinancialProblem:
    """Example 5 — minimize portfolio variance under a budget."""
    return FinancialProblem(
        name="qmq07_min_risk",
        universe=_universe(),
        objectives=[RiskObjective("risk")],
        constraints=[
            BudgetConstraint(name="budget", total=1.0, currency="USD"),
            CardinalityConstraint(name="cardinality", min_assets=2, max_assets=4),
        ],
        context=_context(),
        risk=_risk(["TECH-A", "TECH-B", "BOND-A", "CASH-A"]),
        allocation_kind=AllocationKind.BINARY,
    )


def example_combined_problem() -> FinancialProblem:
    """Example 6 — maximize return minus a risk penalty (mean-variance)."""
    return FinancialProblem(
        name="qmq07_return_minus_risk",
        universe=_universe(),
        objectives=[RiskAdjustedObjective("return_minus_risk", risk_aversion=2.0)],
        constraints=[
            BudgetConstraint(name="budget", total=1.0, currency="USD"),
            CardinalityConstraint(name="cardinality", min_assets=2, max_assets=4),
        ],
        context=_context(),
        risk=_risk(["TECH-A", "TECH-B", "BOND-A", "CASH-A"]),
        allocation_kind=AllocationKind.BINARY,
    )


def example_financial_problem() -> FinancialProblem:
    """The canonical QMQ-07 example problem (combined objective, binary)."""
    return example_combined_problem()
