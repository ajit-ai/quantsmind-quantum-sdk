"""
Monte Carlo Finance Module

This module provides Monte Carlo simulation functionality for the QuantsMind SDK.

Purpose
-------
Provide Monte Carlo simulation capabilities for financial modeling.

Classes
-------
MonteCarloFinanceSimulator: Monte Carlo finance simulator

Responsibilities
----------------
- Simulate asset price paths
- Price options using Monte Carlo
- Simulate portfolio performance
- Risk analysis via simulation

Dependencies
------------
typing (standard library)
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Tuple
import math
import random


class MonteCarloFinanceSimulator:
    """Monte Carlo finance simulator.

    This class provides functionality for Monte Carlo simulation in finance.

    Attributes:
        _name: Simulator name
        _risk_free_rate: Risk-free rate
        _seed: Random seed
        _metadata: Additional metadata

    Example:
        >>> simulator = MonteCarloFinanceSimulator(risk_free_rate=0.05)
        >>> paths = simulator.simulate_geometric_brownian_motion(S0=100, mu=0.1, sigma=0.2, T=1, n_steps=252, n_paths=1000)
    """

    def __init__(
        self,
        risk_free_rate: float = 0.05,
        seed: Optional[int] = None,
        name: str = "default",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a MonteCarloFinanceSimulator.

        Args:
            risk_free_rate: Risk-free rate
            seed: Random seed for reproducibility
            name: Simulator name
            metadata: Additional metadata

        Example:
            >>> simulator = MonteCarloFinanceSimulator(risk_free_rate=0.05)
        """
        self._name = name
        self._risk_free_rate = risk_free_rate
        self._seed = seed
        if seed is not None:
            random.seed(seed)
        self._metadata = metadata or {}

    @property
    def name(self) -> str:
        """Get the simulator name.

        Returns:
            Simulator name

        Example:
            >>> name = simulator.name
        """
        return self._name

    @property
    def risk_free_rate(self) -> float:
        """Get the risk-free rate.

        Returns:
            Risk-free rate

        Example:
            >>> r = simulator.risk_free_rate
        """
        return self._risk_free_rate

    def simulate_geometric_brownian_motion(
        self,
        S0: float,
        mu: float,
        sigma: float,
        T: float,
        n_steps: int = 252,
        n_paths: int = 1000,
    ) -> List[List[float]]:
        """Simulate asset price paths using geometric Brownian motion.

        Args:
            S0: Initial stock price
            mu: Drift (expected return)
            sigma: Volatility
            T: Time horizon (years)
            n_steps: Number of time steps
            n_paths: Number of simulation paths

        Returns:
            List of price paths

        Example:
            >>> paths = simulator.simulate_geometric_brownian_motion(S0=100, mu=0.1, sigma=0.2, T=1, n_steps=252, n_paths=1000)
        """
        dt = T / n_steps
        paths = []

        for _ in range(n_paths):
            path = [S0]
            for _ in range(n_steps):
                # Generate random normal
                z = random.gauss(0, 1)
                # GBM formula: S_t = S_{t-1} * exp((mu - 0.5*sigma^2)*dt + sigma*sqrt(dt)*z)
                drift = (mu - 0.5 * sigma ** 2) * dt
                diffusion = sigma * math.sqrt(dt) * z
                new_price = path[-1] * math.exp(drift + diffusion)
                path.append(new_price)
            paths.append(path)

        return paths

    def monte_carlo_option_price(
        self,
        S0: float,
        K: float,
        T: float,
        sigma: float,
        option_type: str = "call",
        n_paths: int = 10000,
        n_steps: int = 100,
    ) -> float:
        """Price option using Monte Carlo simulation.

        Args:
            S0: Initial stock price
            K: Strike price
            T: Time to maturity
            sigma: Volatility
            option_type: Option type (call or put)
            n_paths: Number of simulation paths
            n_steps: Number of time steps

        Returns:
            Option price

        Example:
            >>> price = simulator.monte_carlo_option_price(S0=100, K=100, T=1, sigma=0.2)
        """
        paths = self.simulate_geometric_brownian_motion(S0, self._risk_free_rate, sigma, T, n_steps, n_paths)

        payoffs = []
        for path in paths:
            final_price = path[-1]
            if option_type == "call":
                payoff = max(0, final_price - K)
            else:
                payoff = max(0, K - final_price)
            payoffs.append(payoff)

        # Discount expected payoff
        expected_payoff = sum(payoffs) / len(payoffs)
        price = math.exp(-self._risk_free_rate * T) * expected_payoff

        return price

    def simulate_portfolio(
        self,
        initial_value: float,
        weights: List[float],
        expected_returns: List[float],
        cov_matrix: List[List[float]],
        T: float,
        n_steps: int = 252,
        n_paths: int = 1000,
    ) -> List[List[float]]:
        """Simulate portfolio value paths.

        Args:
            initial_value: Initial portfolio value
            weights: Asset weights
            expected_returns: Expected asset returns
            cov_matrix: Covariance matrix
            T: Time horizon
            n_steps: Number of time steps
            n_paths: Number of simulation paths

        Returns:
            List of portfolio value paths

        Example:
            >>> paths = simulator.simulate_portfolio(1000000, [0.6, 0.4], [0.1, 0.08], [[0.01, 0.005], [0.005, 0.02]])
        """
        dt = T / n_steps
        n_assets = len(weights)
        paths = []

        # Cholesky decomposition for correlated random variables (simplified)
        # Real implementation would use proper Cholesky decomposition
        for _ in range(n_paths):
            path = [initial_value]
            for _ in range(n_steps):
                # Generate correlated random variables (simplified - assuming independence)
                random_returns = [random.gauss(0, 1) for _ in range(n_assets)]

                # Apply expected returns and volatilities
                asset_returns = []
                for i in range(n_assets):
                    vol = math.sqrt(cov_matrix[i][i]) if cov_matrix[i][i] > 0 else 0
                    asset_return = expected_returns[i] * dt + vol * math.sqrt(dt) * random_returns[i]
                    asset_returns.append(asset_return)

                # Portfolio return
                portfolio_return = sum(w * (1 + r) for w, r in zip(weights, asset_returns)) - 1
                new_value = path[-1] * (1 + portfolio_return)
                path.append(new_value)

            paths.append(path)

        return paths

    def value_at_risk_simulation(
        self,
        portfolio_value: float,
        returns: List[float],
        confidence_level: float = 0.95,
        n_simulations: int = 10000,
    ) -> float:
        """Compute VaR using Monte Carlo simulation.

        Args:
            portfolio_value: Current portfolio value
            returns: Historical returns
            confidence_level: Confidence level
            n_simulations: Number of simulations

        Returns:
            VaR value

        Example:
            >>> var = simulator.value_at_risk_simulation(1000000, [0.01, 0.02, -0.01])
        """
        # Compute statistics from historical returns
        mean_return = sum(returns) / len(returns)
        std_return = math.sqrt(sum((r - mean_return) ** 2 for r in returns) / len(returns))

        # Simulate future returns
        simulated_returns = [random.gauss(mean_return, std_return) for _ in range(n_simulations)]

        # Compute simulated portfolio values
        simulated_values = [portfolio_value * (1 + r) for r in simulated_returns]

        # Compute VaR
        sorted_values = sorted(simulated_values)
        index = int((1 - confidence_level) * len(sorted_values))
        var_value = portfolio_value - sorted_values[index]

        return var_value

    def conditional_var_simulation(
        self,
        portfolio_value: float,
        returns: List[float],
        confidence_level: float = 0.95,
        n_simulations: int = 10000,
    ) -> float:
        """Compute CVaR using Monte Carlo simulation.

        Args:
            portfolio_value: Current portfolio value
            returns: Historical returns
            confidence_level: Confidence level
            n_simulations: Number of simulations

        Returns:
            CVaR value

        Example:
            >>> cvar = simulator.conditional_var_simulation(1000000, [0.01, 0.02, -0.01])
        """
        var = self.value_at_risk_simulation(portfolio_value, returns, confidence_level, n_simulations)

        # Compute statistics from historical returns
        mean_return = sum(returns) / len(returns)
        std_return = math.sqrt(sum((r - mean_return) ** 2 for r in returns) / len(returns))

        # Simulate future returns
        simulated_returns = [random.gauss(mean_return, std_return) for _ in range(n_simulations)]

        # Compute simulated portfolio values
        simulated_values = [portfolio_value * (1 + r) for r in simulated_returns]

        # Compute CVaR (average of worst losses beyond VaR)
        threshold = portfolio_value - var
        tail_losses = [portfolio_value - v for v in simulated_values if v <= threshold]

        if not tail_losses:
            return var

        cvar = sum(tail_losses) / len(tail_losses)
        return cvar

    def asian_option_price(
        self,
        S0: float,
        K: float,
        T: float,
        sigma: float,
        option_type: str = "call",
        n_paths: int = 10000,
        n_steps: int = 100,
    ) -> float:
        """Price Asian option using Monte Carlo simulation.

        Args:
            S0: Initial stock price
            K: Strike price
            T: Time to maturity
            sigma: Volatility
            option_type: Option type (call or put)
            n_paths: Number of simulation paths
            n_steps: Number of time steps

        Returns:
            Asian option price

        Example:
            >>> price = simulator.asian_option_price(S0=100, K=100, T=1, sigma=0.2)
        """
        paths = self.simulate_geometric_brownian_motion(S0, self._risk_free_rate, sigma, T, n_steps, n_paths)

        payoffs = []
        for path in paths:
            # Arithmetic average
            average_price = sum(path) / len(path)

            if option_type == "call":
                payoff = max(0, average_price - K)
            else:
                payoff = max(0, K - average_price)

            payoffs.append(payoff)

        # Discount expected payoff
        expected_payoff = sum(payoffs) / len(payoffs)
        price = math.exp(-self._risk_free_rate * T) * expected_payoff

        return price

    def barrier_option_price(
        self,
        S0: float,
        K: float,
        barrier: float,
        T: float,
        sigma: float,
        barrier_type: str = "knock-out",
        option_type: str = "call",
        n_paths: int = 10000,
        n_steps: int = 100,
    ) -> float:
        """Price barrier option using Monte Carlo simulation.

        Args:
            S0: Initial stock price
            K: Strike price
            barrier: Barrier level
            T: Time to maturity
            sigma: Volatility
            barrier_type: Barrier type (knock-out or knock-in)
            option_type: Option type (call or put)
            n_paths: Number of simulation paths
            n_steps: Number of time steps

        Returns:
            Barrier option price

        Example:
            >>> price = simulator.barrier_option_price(S0=100, K=100, barrier=120, T=1, sigma=0.2)
        """
        paths = self.simulate_geometric_brownian_motion(S0, self._risk_free_rate, sigma, T, n_steps, n_paths)

        payoffs = []
        for path in paths:
            # Check if barrier is crossed
            barrier_crossed = any(price >= barrier for price in path)

            if barrier_type == "knock-out":
                if barrier_crossed:
                    payoff = 0.0
                else:
                    final_price = path[-1]
                    if option_type == "call":
                        payoff = max(0, final_price - K)
                    else:
                        payoff = max(0, K - final_price)
            else:  # knock-in
                if barrier_crossed:
                    final_price = path[-1]
                    if option_type == "call":
                        payoff = max(0, final_price - K)
                    else:
                        payoff = max(0, K - final_price)
                else:
                    payoff = 0.0

            payoffs.append(payoff)

        # Discount expected payoff
        expected_payoff = sum(payoffs) / len(payoffs)
        price = math.exp(-self._risk_free_rate * T) * expected_payoff

        return price

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(simulator)
        """
        return f"MonteCarloFinanceSimulator(name={self._name}, r={self._risk_free_rate})"


__all__ = [
    "MonteCarloFinanceSimulator",
]
