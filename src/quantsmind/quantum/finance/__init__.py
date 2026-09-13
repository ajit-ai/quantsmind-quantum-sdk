"""Finance domain layer of QuantsMind Quantum (QMQ-07 / QMQ-08).

The Finance layer models financial optimization problems as validated,
domain-neutral-but-finance-specific objects and converts them into the
existing QMQ mathematical/optimization infrastructure (QMQ-02 formulation,
QUBO mapping, workflow, execution, benchmark, interpretation).  It works
entirely from supplied/synthetic data — no live market data, no trading
execution, no quantum algorithms.

QMQ-07 ships the Finance foundation (models, weights, context, risk, budget,
objectives, constraints, formulation and mapping).  QMQ-08 builds the
portfolio optimization layer on top of it: a :class:`PortfolioOptimizationProblem`,
portfolio metrics, portfolio solution and result models, and a
:class:`PortfolioOptimizer` that runs the existing QMQ pipeline (binary
selection supported; continuous allocation is validated/formulated but the
current binary-only QUBO pipeline surfaces honest errors rather than
silently approximating; integer allocation raises validation errors).

This is computational Finance domain infrastructure.  It is not investment
advice and does not provide live financial-data or trading services.

Importing this package never requires ``microquantum``.
"""

from __future__ import annotations

from quantsmind.quantum.finance.budget import Budget
from quantsmind.quantum.finance.constraints import (
    BudgetConstraint,
    CardinalityConstraint,
    FinancialConstraint,
    GroupAllocationConstraint,
    PositionLimitConstraint,
    WeightBoundsConstraint,
    constraint_from_dict,
)
from quantsmind.quantum.finance.context import FinancialContext
from quantsmind.quantum.finance.errors import FinanceError, FinanceValidationError
from quantsmind.quantum.finance.examples import (
    example_asset_universe,
    example_budget,
    example_combined_problem,
    example_financial_problem,
    example_return_problem,
    example_risk_matrix,
    example_risk_problem,
    synthetic_asset,
)
from quantsmind.quantum.finance.formulation import FinanceFormulationAdapter
from quantsmind.quantum.finance.mapping import (
    AssetMapping,
    DecodedAsset,
    FinanceAssetMapper,
)
from quantsmind.quantum.finance.models import (
    Asset,
    AssetUniverse,
    FinancialInstrument,
    FinancialProblem,
)
from quantsmind.quantum.finance.objectives import (
    ExpectedReturnObjective,
    FinancialObjective,
    RiskAdjustedObjective,
    RiskObjective,
    objective_from_dict,
)
from quantsmind.quantum.finance.optimizer import (
    FinanceOptimizationResult,
    FinanceOptimizer,
    FinancialSolution,
)
from quantsmind.quantum.finance.portfolio import (
    OptimizationConfiguration,
    PortfolioAssetMapper,
    PortfolioFormulationAdapter,
    PortfolioOptimizationProblem,
    PortfolioOptimizer,
)
from quantsmind.quantum.finance.portfolio_examples import (
    example_budget_portfolio,
    example_group_constraints_portfolio,
    example_maximize_return_portfolio,
    example_minimize_risk_portfolio,
    example_portfolio_problem,
    example_portfolio_risk_matrix,
    example_portfolio_universe,
    example_risk_adjusted_portfolio,
)
from quantsmind.quantum.finance.portfolio_metrics import (
    PortfolioMetrics,
    compute_portfolio_metrics,
    expected_return_of,
    portfolio_variance,
    portfolio_volatility,
    risk_contributions,
)
from quantsmind.quantum.finance.portfolio_solution import (
    PortfolioComponent,
    PortfolioOptimizationResult,
    PortfolioSolution,
)
from quantsmind.quantum.finance.risk import RiskMatrix
from quantsmind.quantum.finance.weights import Allocation, AllocationKind

__all__ = [
    "FinancialInstrument",
    "Asset",
    "AssetUniverse",
    "FinancialProblem",
    "FinancialContext",
    "RiskMatrix",
    "Budget",
    "AllocationKind",
    "Allocation",
    "FinancialConstraint",
    "BudgetConstraint",
    "WeightBoundsConstraint",
    "CardinalityConstraint",
    "PositionLimitConstraint",
    "GroupAllocationConstraint",
    "constraint_from_dict",
    "FinancialObjective",
    "ExpectedReturnObjective",
    "RiskObjective",
    "RiskAdjustedObjective",
    "objective_from_dict",
    "FinanceFormulationAdapter",
    "FinanceAssetMapper",
    "AssetMapping",
    "DecodedAsset",
    "OptimizationConfiguration",
    "PortfolioOptimizationProblem",
    "PortfolioFormulationAdapter",
    "PortfolioAssetMapper",
    "PortfolioOptimizer",
    "FinancialSolution",
    "FinanceOptimizationResult",
    "FinanceOptimizer",
    "PortfolioMetrics",
    "compute_portfolio_metrics",
    "expected_return_of",
    "portfolio_variance",
    "portfolio_volatility",
    "risk_contributions",
    "PortfolioComponent",
    "PortfolioSolution",
    "PortfolioOptimizationResult",
    "FinanceError",
    "FinanceValidationError",
    "synthetic_asset",
    "example_asset_universe",
    "example_budget",
    "example_risk_matrix",
    "example_return_problem",
    "example_risk_problem",
    "example_combined_problem",
    "example_financial_problem",
    "example_portfolio_universe",
    "example_portfolio_risk_matrix",
    "example_maximize_return_portfolio",
    "example_minimize_risk_portfolio",
    "example_risk_adjusted_portfolio",
    "example_budget_portfolio",
    "example_group_constraints_portfolio",
    "example_portfolio_problem",
]
