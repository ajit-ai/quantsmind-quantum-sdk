"""
Portfolio Math Module

This module provides portfolio mathematics functionality for the QuantsMind SDK.

Purpose
-------
Provide portfolio analysis and optimization capabilities.

Classes
-------
PortfolioMath: Portfolio mathematics engine

Responsibilities
----------------
- Compute portfolio returns
- Compute portfolio risk metrics
- Compute Sharpe ratio
- Compute alpha and beta
- Portfolio optimization

Dependencies
------------
typing (standard library)
"""

from __future__ import annotations

import math
from typing import Any


class PortfolioMath:
    """Portfolio mathematics engine.

    This class provides functionality for portfolio analysis and optimization.

    Attributes:
        _name: Engine name
        _weights: Portfolio weights
        _returns: Asset returns
        _metadata: Additional metadata

    Example:
        >>> pm = PortfolioMath()
        >>> returns = pm.portfolio_return([0.5, 0.5], [0.1, 0.15])
    """

    def __init__(
        self,
        name: str = "default",
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a PortfolioMath.

        Args:
            name: Engine name
            metadata: Additional metadata

        Example:
            >>> pm = PortfolioMath()
        """
        self._name = name
        self._weights: list[float] = []
        self._returns: list[list[float]] = []
        self._metadata = metadata or {}

    @property
    def name(self) -> str:
        """Get the engine name.

        Returns:
            Engine name

        Example:
            >>> name = pm.name
        """
        return self._name

    def portfolio_return(
        self,
        weights: list[float],
        asset_returns: list[float],
    ) -> float:
        """Compute portfolio return.

        Args:
            weights: Portfolio weights
            asset_returns: Asset returns

        Returns:
            Portfolio return

        Example:
            >>> returns = pm.portfolio_return([0.5, 0.5], [0.1, 0.15])
        """
        if len(weights) != len(asset_returns):
            raise ValueError("Weights and returns must have same length")

        if abs(sum(weights) - 1.0) > 1e-6:
            raise ValueError("Weights must sum to 1")

        return sum(w * r for w, r in zip(weights, asset_returns, strict=False))

    def annualized_return(
        self,
        returns: list[float],
        periods_per_year: int = 252,
    ) -> float:
        """Compute annualized return.

        Args:
            returns: Period returns
            periods_per_year: Number of periods per year

        Returns:
            Annualized return

        Example:
            >>> ann_return = pm.annualized_return([0.01, 0.02, 0.015])
        """
        if not returns:
            raise ValueError("Returns cannot be empty")

        total_return = 1.0
        for r in returns:
            total_return *= (1 + r)

        return (total_return ** (periods_per_year / len(returns))) - 1

    def volatility(
        self,
        returns: list[float],
        periods_per_year: int = 252,
    ) -> float:
        """Compute portfolio volatility (standard deviation).

        Args:
            returns: Period returns
            periods_per_year: Number of periods per year

        Returns:
            Annualized volatility

        Example:
            >>> vol = pm.volatility([0.01, 0.02, 0.015])
        """
        if not returns:
            raise ValueError("Returns cannot be empty")

        mean_return = sum(returns) / len(returns)
        variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
        std_dev = math.sqrt(variance)

        return std_dev * math.sqrt(periods_per_year)

    def sharpe_ratio(
        self,
        returns: list[float],
        risk_free_rate: float = 0.02,
        periods_per_year: int = 252,
    ) -> float:
        """Compute Sharpe ratio.

        Args:
            returns: Period returns
            risk_free_rate: Risk-free rate (annualized)
            periods_per_year: Number of periods per year

        Returns:
            Sharpe ratio

        Example:
            >>> sharpe = pm.sharpe_ratio([0.01, 0.02, 0.015])
        """
        ann_return = self.annualized_return(returns, periods_per_year)
        ann_vol = self.volatility(returns, periods_per_year)

        if ann_vol == 0:
            return 0.0

        return (ann_return - risk_free_rate) / ann_vol

    def alpha(
        self,
        portfolio_returns: list[float],
        benchmark_returns: list[float],
        risk_free_rate: float = 0.02,
    ) -> float:
        """Compute Jensen's alpha.

        Args:
            portfolio_returns: Portfolio returns
            benchmark_returns: Benchmark returns
            risk_free_rate: Risk-free rate

        Returns:
            Alpha value

        Example:
            >>> alpha = pm.alpha([0.01, 0.02], [0.008, 0.015])
        """
        if len(portfolio_returns) != len(benchmark_returns):
            raise ValueError("Portfolio and benchmark returns must have same length")

        # Simple linear regression to get beta
        beta = self.beta(portfolio_returns, benchmark_returns)

        # Compute expected return
        avg_portfolio = sum(portfolio_returns) / len(portfolio_returns)
        avg_benchmark = sum(benchmark_returns) / len(benchmark_returns)

        expected_return = risk_free_rate + beta * (avg_benchmark - risk_free_rate)
        alpha = avg_portfolio - expected_return

        return alpha

    def beta(
        self,
        portfolio_returns: list[float],
        benchmark_returns: list[float],
    ) -> float:
        """Compute beta.

        Args:
            portfolio_returns: Portfolio returns
            benchmark_returns: Benchmark returns

        Returns:
            Beta value

        Example:
            >>> beta = pm.beta([0.01, 0.02], [0.008, 0.015])
        """
        if len(portfolio_returns) != len(benchmark_returns):
            raise ValueError("Portfolio and benchmark returns must have same length")

        n = len(portfolio_returns)

        # Compute covariance and variance
        avg_portfolio = sum(portfolio_returns) / n
        avg_benchmark = sum(benchmark_returns) / n

        covariance = sum(
            (p - avg_portfolio) * (b - avg_benchmark)
            for p, b in zip(portfolio_returns, benchmark_returns, strict=False)
        ) / n

        variance = sum((b - avg_benchmark) ** 2 for b in benchmark_returns) / n

        if variance == 0:
            return 0.0

        return covariance / variance

    def value_at_risk(
        self,
        returns: list[float],
        confidence_level: float = 0.95,
    ) -> float:
        """Compute Value at Risk (VaR).

        Args:
            returns: Historical returns
            confidence_level: Confidence level (0-1)

        Returns:
            VaR value

        Example:
            >>> var = pm.value_at_risk([0.01, 0.02, -0.01], 0.95)
        """
        if not returns:
            raise ValueError("Returns cannot be empty")

        sorted_returns = sorted(returns)
        index = int((1 - confidence_level) * len(sorted_returns))
        return sorted_returns[index]

    def conditional_var(
        self,
        returns: list[float],
        confidence_level: float = 0.95,
    ) -> float:
        """Compute Conditional Value at Risk (CVaR).

        Args:
            returns: Historical returns
            confidence_level: Confidence level (0-1)

        Returns:
            CVaR value

        Example:
            >>> cvar = pm.conditional_var([0.01, 0.02, -0.01], 0.95)
        """
        if not returns:
            raise ValueError("Returns cannot be empty")

        var = self.value_at_risk(returns, confidence_level)
        tail_losses = [r for r in returns if r <= var]

        if not tail_losses:
            return var

        return sum(tail_losses) / len(tail_losses)

    def portfolio_optimization(
        self,
        expected_returns: list[float],
        covariance_matrix: list[list[float]],
        risk_aversion: float = 1.0,
    ) -> list[float]:
        """Optimize portfolio weights (simplified mean-variance optimization).

        Args:
            expected_returns: Expected asset returns
            covariance_matrix: Covariance matrix
            risk_aversion: Risk aversion parameter

        Returns:
            Optimal weights

        Example:
            >>> weights = pm.portfolio_optimization([0.1, 0.15], [[0.01, 0.005], [0.005, 0.02]])
        """
        n = len(expected_returns)

        # Simplified optimization - equal weights for now
        # Real implementation would use quadratic programming
        weights = [1.0 / n] * n

        return weights

    def tracking_error(
        self,
        portfolio_returns: list[float],
        benchmark_returns: list[float],
    ) -> float:
        """Compute tracking error.

        Args:
            portfolio_returns: Portfolio returns
            benchmark_returns: Benchmark returns

        Returns:
            Tracking error

        Example:
            >>> te = pm.tracking_error([0.01, 0.02], [0.008, 0.015])
        """
        if len(portfolio_returns) != len(benchmark_returns):
            raise ValueError("Portfolio and benchmark returns must have same length")

        excess_returns = [p - b for p, b in zip(portfolio_returns, benchmark_returns, strict=False)]
        return math.sqrt(sum(e ** 2 for e in excess_returns) / len(excess_returns))

    def information_ratio(
        self,
        portfolio_returns: list[float],
        benchmark_returns: list[float],
    ) -> float:
        """Compute information ratio.

        Args:
            portfolio_returns: Portfolio returns
            benchmark_returns: Benchmark returns

        Returns:
            Information ratio

        Example:
            >>> ir = pm.information_ratio([0.01, 0.02], [0.008, 0.015])
        """
        excess_returns = [p - b for p, b in zip(portfolio_returns, benchmark_returns, strict=False)]
        avg_excess = sum(excess_returns) / len(excess_returns)
        te = self.tracking_error(portfolio_returns, benchmark_returns)

        if te == 0:
            return 0.0

        return avg_excess / te

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(pm)
        """
        return f"PortfolioMath(name={self._name})"


__all__ = [
    "PortfolioMath",
]
