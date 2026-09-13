"""Portfolio metrics of the QMQ-08 portfolio layer.

Metrics are computed entirely from supplied financial data (expected returns
and an optional :class:`~quantsmind.quantum.finance.risk.RiskMatrix`) — no
statistical estimation, no market data.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from quantsmind.quantum.finance.risk import RiskMatrix

if TYPE_CHECKING:
    from quantsmind.quantum.finance.models import AssetUniverse

__all__ = [
    "expected_return_of",
    "portfolio_variance",
    "portfolio_volatility",
    "risk_contributions",
    "PortfolioMetrics",
    "compute_portfolio_metrics",
]


def expected_return_of(universe: AssetUniverse, weights: Mapping[str, float]) -> float:
    """Expected portfolio return ``sum(expected_return_i * w_i)`` over the universe.

    Missing weights default to 0; identifiers outside the universe are
    ignored (unknown identifiers are a validation concern, not a metric).
    """
    return sum(
        asset.expected_return * float(weights.get(asset.identifier, 0.0)) for asset in universe
    )


def portfolio_variance(risk: RiskMatrix, weights: Mapping[str, float]) -> float:
    """Portfolio variance ``w^T Cov w`` from a supplied risk matrix.

    The matrix owns the deterministic asset order; entries for assets without
    a weight default to 0.
    """
    order = risk.asset_order
    n = len(order)
    column = [float(weights.get(identifier, 0.0)) for identifier in order]
    total = 0.0
    for i in range(n):
        row_dot = sum(risk.matrix[i][j] * column[j] for j in range(n))
        total += column[i] * row_dot
    return total


def portfolio_volatility(risk: RiskMatrix, weights: Mapping[str, float]) -> float:
    """Portfolio volatility (standard deviation) ``sqrt(w^T Cov w)``.

    Round-off may produce a value marginally below zero for an empty
    allocation; the reported volatility is clamped at 0.
    """
    variance = portfolio_variance(risk, weights)
    return math.sqrt(max(0.0, variance))


def risk_contributions(risk: RiskMatrix, weights: Mapping[str, float]) -> dict[str, float]:
    """Marginal variance contribution ``w_i * (Cov w)_i`` per asset identifier."""
    order = risk.asset_order
    n = len(order)
    column = [float(weights.get(identifier, 0.0)) for identifier in order]
    contributions: dict[str, float] = {}
    for i, identifier in enumerate(order):
        row_dot = sum(risk.matrix[i][j] * column[j] for j in range(n))
        contributions[identifier] = float(column[i] * row_dot)
    return contributions


@dataclass
class PortfolioMetrics:
    """Measured metrics of a portfolio selection (QMQ-08).

    ``expected_return`` / ``variance`` / ``volatility`` are ``None`` whenever
    the underlying data (e.g. a risk matrix) was not supplied; counts default
    to 0.  Nothing is invented beyond the supplied financial data.

    Args:
        expected_return: Expected portfolio return (supplied returns only).
        variance: ``w^T Cov w`` over the supplied risk matrix.
        volatility: Square root of the (clamped) variance.
        selected_count: Number of assets selected (weight > threshold).
        allocation_sum: Sum of all weights in universe order.
        constraint_violations: Number of violated constraints.
        constraint_violation_magnitude: Total excess magnitude of violations.
    """

    expected_return: float | None = None
    variance: float | None = None
    volatility: float | None = None
    selected_count: int = 0
    allocation_sum: float = 0.0
    constraint_violations: int = 0
    constraint_violation_magnitude: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def compute(
        cls,
        universe: AssetUniverse,
        weights: Mapping[str, float],
        risk: RiskMatrix | None = None,
        *,
        selected_threshold: float = 0.5,
        violation_count: int = 0,
        violation_magnitude: float = 0.0,
    ) -> PortfolioMetrics:
        """Compute portfolio metrics from supplied allocations.

        Args:
            universe: The asset universe (owns the deterministic order).
            weights: Asset identifier -> weight mapping.
            risk: Optional risk matrix for variance/volatility.
            selected_threshold: Weight strictly above this counts as selected.
            violation_count: Number of violated constraints (from the existing
                constraint evaluation infrastructure; ``0`` when unused).
            violation_magnitude: Total excess magnitude (``0.0`` when unused).
        """
        order = universe.identifier_order()
        allocation_sum = sum(float(weights.get(identifier, 0.0)) for identifier in order)
        selected = sum(
            1
            for identifier in order
            if float(weights.get(identifier, 0.0)) > float(selected_threshold)
        )
        return cls(
            expected_return=expected_return_of(universe, weights),
            variance=portfolio_variance(risk, weights) if risk is not None else None,
            volatility=portfolio_volatility(risk, weights) if risk is not None else None,
            selected_count=selected,
            allocation_sum=allocation_sum,
            constraint_violations=int(violation_count),
            constraint_violation_magnitude=float(violation_magnitude),
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "expected_return": self.expected_return,
            "variance": self.variance,
            "volatility": self.volatility,
            "selected_count": self.selected_count,
            "allocation_sum": float(self.allocation_sum),
            "constraint_violations": self.constraint_violations,
            "constraint_violation_magnitude": float(self.constraint_violation_magnitude),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PortfolioMetrics:
        """Rebuild :class:`PortfolioMetrics` from :meth:`to_dict` output."""
        return cls(
            expected_return=(
                float(data["expected_return"]) if data.get("expected_return") is not None else None
            ),
            variance=(float(data["variance"]) if data.get("variance") is not None else None),
            volatility=(float(data["volatility"]) if data.get("volatility") is not None else None),
            selected_count=int(data.get("selected_count", 0)),
            allocation_sum=float(data.get("allocation_sum", 0.0)),
            constraint_violations=int(data.get("constraint_violations", 0)),
            constraint_violation_magnitude=float(data.get("constraint_violation_magnitude", 0.0)),
            metadata=dict(data.get("metadata", {})),
        )

    def __repr__(self) -> str:
        return (
            f"PortfolioMetrics(expected_return={self.expected_return}, "
            f"variance={self.variance}, selected={self.selected_count})"
        )


def compute_portfolio_metrics(
    universe: AssetUniverse,
    weights: Mapping[str, float],
    risk: RiskMatrix | None = None,
    *,
    selected_threshold: float = 0.5,
    violation_count: int = 0,
    violation_magnitude: float = 0.0,
) -> PortfolioMetrics:
    """Convenience wrapper around :meth:`PortfolioMetrics.compute`."""
    return PortfolioMetrics.compute(
        universe,
        weights,
        risk,
        selected_threshold=selected_threshold,
        violation_count=violation_count,
        violation_magnitude=violation_magnitude,
    )
