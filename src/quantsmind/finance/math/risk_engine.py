"""
Risk Engine Module

This module provides risk analysis functionality for the QuantsMind SDK.

Purpose
-------
Provide comprehensive risk analysis capabilities for financial instruments.

Classes
-------
RiskEngine: Risk analysis engine

Responsibilities
----------------
- Compute risk metrics
- Analyze portfolio risk
- Compute risk exposures
- Risk factor analysis

Dependencies
------------
typing (standard library)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
import math


class RiskEngine:
    """Risk analysis engine.

    This class provides functionality for analyzing financial risk.

    Attributes:
        _name: Engine name
        _risk_factors: Risk factors
        _metadata: Additional metadata

    Example:
        >>> engine = RiskEngine()
        >>> metrics = engine.compute_risk_metrics([0.01, 0.02, -0.01])
    """

    def __init__(
        self,
        name: str = "default",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a RiskEngine.

        Args:
            name: Engine name
            metadata: Additional metadata

        Example:
            >>> engine = RiskEngine()
        """
        self._name = name
        self._risk_factors: Dict[str, float] = {}
        self._metadata = metadata or {}

    @property
    def name(self) -> str:
        """Get the engine name.

        Returns:
            Engine name

        Example:
            >>> name = engine.name
        """
        return self._name

    def compute_risk_metrics(
        self,
        returns: List[float],
        confidence_levels: Optional[List[float]] = None,
    ) -> Dict[str, float]:
        """Compute comprehensive risk metrics.

        Args:
            returns: Historical returns
            confidence_levels: Confidence levels for VaR

        Returns:
            Dictionary of risk metrics

        Example:
            >>> metrics = engine.compute_risk_metrics([0.01, 0.02, -0.01])
        """
        if confidence_levels is None:
            confidence_levels = [0.95, 0.99]

        metrics = {}

        # Basic statistics
        metrics["mean"] = sum(returns) / len(returns) if returns else 0.0
        metrics["std"] = math.sqrt(sum((r - metrics["mean"]) ** 2 for r in returns) / len(returns)) if returns else 0.0

        # Downside risk
        negative_returns = [r for r in returns if r < 0]
        metrics["downside_deviation"] = math.sqrt(sum(r ** 2 for r in negative_returns) / len(negative_returns)) if negative_returns else 0.0

        # Skewness
        if metrics["std"] > 0:
            skew = sum((r - metrics["mean"]) ** 3 for r in returns) / (len(returns) * metrics["std"] ** 3)
            metrics["skewness"] = skew
        else:
            metrics["skewness"] = 0.0

        # Kurtosis
        if metrics["std"] > 0:
            kurt = sum((r - metrics["mean"]) ** 4 for r in returns) / (len(returns) * metrics["std"] ** 4) - 3
            metrics["kurtosis"] = kurt
        else:
            metrics["kurtosis"] = 0.0

        # VaR and CVaR
        for cl in confidence_levels:
            metrics[f"var_{int(cl*100)}"] = self._var(returns, cl)
            metrics[f"cvar_{int(cl*100)}"] = self._cvar(returns, cl)

        # Maximum drawdown
        metrics["max_drawdown"] = self._max_drawdown(returns)

        return metrics

    def _var(self, returns: List[float], confidence_level: float) -> float:
        """Compute Value at Risk.

        Args:
            returns: Historical returns
            confidence_level: Confidence level

        Returns:
            VaR value
        """
        if not returns:
            return 0.0

        sorted_returns = sorted(returns)
        index = int((1 - confidence_level) * len(sorted_returns))
        return sorted_returns[index]

    def _cvar(self, returns: List[float], confidence_level: float) -> float:
        """Compute Conditional Value at Risk.

        Args:
            returns: Historical returns
            confidence_level: Confidence level

        Returns:
            CVaR value
        """
        if not returns:
            return 0.0

        var = self._var(returns, confidence_level)
        tail_losses = [r for r in returns if r <= var]

        if not tail_losses:
            return var

        return sum(tail_losses) / len(tail_losses)

    def _max_drawdown(self, returns: List[float]) -> float:
        """Compute maximum drawdown.

        Args:
            returns: Historical returns

        Returns:
            Maximum drawdown
        """
        if not returns:
            return 0.0

        cumulative = 1.0
        peak = cumulative
        max_dd = 0.0

        for r in returns:
            cumulative *= (1 + r)
            if cumulative > peak:
                peak = cumulative

            dd = (peak - cumulative) / peak
            if dd > max_dd:
                max_dd = dd

        return max_dd

    def beta_exposure(
        self,
        portfolio_returns: List[float],
        factor_returns: List[float],
    ) -> float:
        """Compute beta exposure to a factor.

        Args:
            portfolio_returns: Portfolio returns
            factor_returns: Factor returns

        Returns:
            Beta exposure

        Example:
            >>> beta = engine.beta_exposure([0.01, 0.02], [0.008, 0.015])
        """
        if len(portfolio_returns) != len(factor_returns):
            raise ValueError("Returns must have same length")

        n = len(portfolio_returns)

        avg_portfolio = sum(portfolio_returns) / n
        avg_factor = sum(factor_returns) / n

        covariance = sum(
            (p - avg_portfolio) * (f - avg_factor)
            for p, f in zip(portfolio_returns, factor_returns)
        ) / n

        variance = sum((f - avg_factor) ** 2 for f in factor_returns) / n

        if variance == 0:
            return 0.0

        return covariance / variance

    def stress_test(
        self,
        portfolio_value: float,
        scenarios: List[Dict[str, float]],
    ) -> Dict[str, float]:
        """Perform stress testing on portfolio.

        Args:
            portfolio_value: Current portfolio value
            scenarios: Stress scenarios with factor shocks

        Returns:
            Portfolio values under scenarios

        Example:
            >>> results = engine.stress_test(1000000, [{"market": -0.2}, {"market": -0.3}])
        """
        results = {}

        for i, scenario in enumerate(scenarios):
            # Simplified stress test - apply shocks linearly
            shock = sum(scenario.values())
            stressed_value = portfolio_value * (1 + shock)
            results[f"scenario_{i+1}"] = stressed_value

        return results

    def scenario_analysis(
        self,
        base_value: float,
        factor_sensitivities: Dict[str, float],
        factor_shocks: Dict[str, float],
    ) -> float:
        """Perform scenario analysis.

        Args:
            base_value: Base portfolio value
            factor_sensitivities: Factor sensitivities
            factor_shocks: Factor shocks

        Returns:
            Stressed portfolio value

        Example:
            >>> value = engine.scenario_analysis(1000000, {"equity": 0.6}, {"equity": -0.2})
        """
        total_shock = 0.0

        for factor, sensitivity in factor_sensitivities.items():
            if factor in factor_shocks:
                total_shock += sensitivity * factor_shocks[factor]

        return base_value * (1 + total_shock)

    def risk_budget(
        self,
        total_risk: float,
        risk_contributions: List[float],
    ) -> List[float]:
        """Allocate risk budget.

        Args:
            total_risk: Total portfolio risk
            risk_contributions: Individual risk contributions

        Returns:
            Risk budget allocation

        Example:
            >>> budget = engine.risk_budget(0.15, [0.05, 0.07, 0.03])
        """
        total_contribution = sum(risk_contributions)

        if total_contribution == 0:
            return [0.0] * len(risk_contributions)

        return [rc / total_contribution * total_risk for rc in risk_contributions]

    def concentration_risk(
        self,
        weights: List[float],
        herfindahl_index: bool = True,
    ) -> float:
        """Compute concentration risk.

        Args:
            weights: Portfolio weights
            herfindahl_index: Use Herfindahl index

        Returns:
            Concentration risk measure

        Example:
            >>> risk = engine.concentration_risk([0.5, 0.3, 0.2])
        """
        if herfindahl_index:
            return sum(w ** 2 for w in weights)
        else:
            # Gini coefficient (simplified)
            sorted_weights = sorted(weights)
            n = len(sorted_weights)
            cum_sum = sum((i + 1) * w for i, w in enumerate(sorted_weights))
            return (2 * cum_sum) / (n * sum(sorted_weights)) - (n + 1) / n

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(engine)
        """
        return f"RiskEngine(name={self._name})"


__all__ = [
    "RiskEngine",
]
