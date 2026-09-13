"""Canonical synthetic portfolio examples (QMQ-08 §21).

Each example builds a deterministic, tiny :class:`PortfolioOptimizationProblem`
entirely from supplied data — no market data, no estimation.  They are
**synthetic examples**, not market recommendations, and not investment advice.
"""

from __future__ import annotations

from quantsmind.quantum.finance.budget import Budget
from quantsmind.quantum.finance.constraints import (
    CardinalityConstraint,
    GroupAllocationConstraint,
    PositionLimitConstraint,
    WeightBoundsConstraint,
)
from quantsmind.quantum.finance.context import FinancialContext
from quantsmind.quantum.finance.examples import synthetic_asset
from quantsmind.quantum.finance.models import AssetUniverse
from quantsmind.quantum.finance.objectives import (
    ExpectedReturnObjective,
    RiskAdjustedObjective,
    RiskObjective,
)
from quantsmind.quantum.finance.portfolio import (
    OptimizationConfiguration,
    PortfolioOptimizationProblem,
)
from quantsmind.quantum.finance.risk import RiskMatrix
from quantsmind.quantum.finance.weights import AllocationKind

__all__ = [
    "example_portfolio_universe",
    "example_portfolio_risk_matrix",
    "example_maximize_return_portfolio",
    "example_minimize_risk_portfolio",
    "example_risk_adjusted_portfolio",
    "example_budget_portfolio",
    "example_group_constraints_portfolio",
    "example_portfolio_problem",
]


def example_portfolio_universe() -> AssetUniverse:
    """Universe A — two equity assets, one bond and one cash asset."""
    return AssetUniverse(
        name="qmq08_universe",
        assets=[
            synthetic_asset("TECH-A", 0.12, 0.25, symbol="TECH-A", asset_class="equity"),
            synthetic_asset("TECH-B", 0.08, 0.18, symbol="TECH-B", asset_class="equity"),
            synthetic_asset("BOND-A", 0.03, 0.06, symbol="BOND-A", asset_class="bond"),
            synthetic_asset("CASH-A", 0.01, 0.0, symbol="CASH-A", asset_class="cash"),
        ],
    )


def example_portfolio_risk_matrix() -> RiskMatrix:
    """Risk matrix over the portfolio universe (same supplied data as QMQ-07)."""
    return _portfolio_risk()


def _portfolio_risk() -> RiskMatrix:
    ids = ["TECH-A", "TECH-B", "BOND-A", "CASH-A"]
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
    n = len(ids)
    matrix: list[list[float]] = [[0.0] * n for _ in range(n)]
    for i, left in enumerate(ids):
        for j, right in enumerate(ids):
            if i == j:
                matrix[i][j] = variances[left]
            else:
                pair = covariances.get((left, right), covariances.get((right, left), 0.0))
                matrix[i][j] = pair
    return RiskMatrix(
        asset_order=list(ids), matrix=matrix, volatilities=[volatilities[t] for t in ids]
    )


def _context() -> FinancialContext:
    return FinancialContext(
        currency="USD",
        subdomain="portfolio",
        investment_horizon="1Y",
        risk_free_rate=0.02,
        transaction_cost_rate=0.001,
        assumptions={"data_source": "synthetic-supplied", "estimation": "none"},
    )


def _config(preferred_strategy: str = "classical") -> OptimizationConfiguration:
    return OptimizationConfiguration(preferred_strategy=preferred_strategy)


def example_maximize_return_portfolio() -> PortfolioOptimizationProblem:
    """Example A — maximize expected return under a cardinality bound."""
    return PortfolioOptimizationProblem(
        name="qmq08_maximize_return",
        universe=example_portfolio_universe(),
        objectives=[ExpectedReturnObjective("expected_return")],
        constraints=[CardinalityConstraint(name="cardinality", min_assets=2, max_assets=2)],
        allocation_kind=AllocationKind.BINARY,
        context=_context(),
        optimization_config=_config(),
        description="maximize expected return with exactly two assets selected",
    )


def example_minimize_risk_portfolio() -> PortfolioOptimizationProblem:
    """Example B — minimize portfolio variance under a cardinality bound."""
    return PortfolioOptimizationProblem(
        name="qmq08_minimize_risk",
        universe=example_portfolio_universe(),
        objectives=[RiskObjective("risk")],
        constraints=[CardinalityConstraint(name="cardinality", min_assets=2, max_assets=2)],
        allocation_kind=AllocationKind.BINARY,
        context=_context(),
        risk=example_portfolio_risk_matrix(),
        optimization_config=_config(),
        description="minimize portfolio variance with exactly two assets selected",
    )


def example_risk_adjusted_portfolio() -> PortfolioOptimizationProblem:
    """Example C — maximize risk-adjusted return (mean-variance utility)."""
    return PortfolioOptimizationProblem(
        name="qmq08_risk_adjusted",
        universe=example_portfolio_universe(),
        objectives=[RiskAdjustedObjective("return_minus_risk", risk_aversion=2.0)],
        constraints=[CardinalityConstraint(name="cardinality", min_assets=2, max_assets=2)],
        allocation_kind=AllocationKind.BINARY,
        context=_context(),
        risk=example_portfolio_risk_matrix(),
        optimization_config=_config(),
        description="maximize return - 2.0 * variance with exactly two assets selected",
    )


def example_budget_portfolio() -> PortfolioOptimizationProblem:
    """Example D — continuous allocation under a budget with position limits."""
    return PortfolioOptimizationProblem(
        name="qmq08_budget_allocation",
        universe=example_portfolio_universe(),
        objectives=[ExpectedReturnObjective("expected_return")],
        constraints=[
            PositionLimitConstraint(
                name="positions",
                asset_ids=["TECH-A", "TECH-B", "BOND-A", "CASH-A"],
                lower=0.0,
                upper=0.6,
            ),
            WeightBoundsConstraint(
                name="cash_floor",
                bounds={"CASH-A": (0.05, 1.0)},
            ),
        ],
        allocation_kind=AllocationKind.CONTINUOUS,
        budget=Budget(total=1.0, currency="USD", min_allocation=0.5, max_allocation=1.0),
        context=_context(),
        optimization_config=_config(),
        description="continuous weights under a budget with position limits",
    )


def example_group_constraints_portfolio() -> PortfolioOptimizationProblem:
    """Example E — binary selection with group allocation constraints."""
    return PortfolioOptimizationProblem(
        name="qmq08_group_allocation",
        universe=example_portfolio_universe(),
        objectives=[ExpectedReturnObjective("expected_return")],
        constraints=[
            GroupAllocationConstraint(name="equity", group="equity", upper=2.0),
            GroupAllocationConstraint(name="bond", group="bond", lower=1.0),
            CardinalityConstraint(name="cardinality", min_assets=2, max_assets=3),
        ],
        allocation_kind=AllocationKind.BINARY,
        context=_context(),
        optimization_config=_config(),
        description="at most two equity and at least one bond asset selected",
    )


def example_portfolio_problem() -> PortfolioOptimizationProblem:
    """The canonical QMQ-08 example problem (risk-adjusted, binary)."""
    return example_risk_adjusted_portfolio()
