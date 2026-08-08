"""
Option Pricer Module

This module provides option pricing functionality for the QuantsMind SDK.

Purpose
-------
Provide option pricing models including Black-Scholes and Monte Carlo methods.

Classes
-------
OptionPricer: Option pricing engine

Responsibilities
----------------
- Price European options
- Price American options
- Compute Greeks
- Support various option types

Dependencies
------------
typing (standard library)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
import math


class OptionPricer:
    """Option pricing engine.

    This class provides functionality for pricing financial options.

    Attributes:
        _name: Pricer name
        _risk_free_rate: Risk-free rate
        _metadata: Additional metadata

    Example:
        >>> pricer = OptionPricer(risk_free_rate=0.05)
        >>> price = pricer.black_scholes_call(S=100, K=100, T=1, sigma=0.2)
    """

    def __init__(
        self,
        risk_free_rate: float = 0.05,
        name: str = "default",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize an OptionPricer.

        Args:
            risk_free_rate: Risk-free rate
            name: Pricer name
            metadata: Additional metadata

        Example:
            >>> pricer = OptionPricer(risk_free_rate=0.05)
        """
        self._name = name
        self._risk_free_rate = risk_free_rate
        self._metadata = metadata or {}

    @property
    def name(self) -> str:
        """Get the pricer name.

        Returns:
            Pricer name

        Example:
            >>> name = pricer.name
        """
        return self._name

    @property
    def risk_free_rate(self) -> float:
        """Get the risk-free rate.

        Returns:
            Risk-free rate

        Example:
            >>> r = pricer.risk_free_rate
        """
        return self._risk_free_rate

    def black_scholes_call(
        self,
        S: float,
        K: float,
        T: float,
        sigma: float,
    ) -> float:
        """Price a European call option using Black-Scholes.

        Args:
            S: Current stock price
            K: Strike price
            T: Time to maturity (years)
            sigma: Volatility

        Returns:
            Call option price

        Example:
            >>> price = pricer.black_scholes_call(S=100, K=100, T=1, sigma=0.2)
        """
        d1 = self._d1(S, K, T, sigma)
        d2 = self._d2(d1, sigma, T)

        return S * self._cdf(d1) - K * math.exp(-self._risk_free_rate * T) * self._cdf(d2)

    def black_scholes_put(
        self,
        S: float,
        K: float,
        T: float,
        sigma: float,
    ) -> float:
        """Price a European put option using Black-Scholes.

        Args:
            S: Current stock price
            K: Strike price
            T: Time to maturity (years)
            sigma: Volatility

        Returns:
            Put option price

        Example:
            >>> price = pricer.black_scholes_put(S=100, K=100, T=1, sigma=0.2)
        """
        d1 = self._d1(S, K, T, sigma)
        d2 = self._d2(d1, sigma, T)

        return K * math.exp(-self._risk_free_rate * T) * self._cdf(-d2) - S * self._cdf(-d1)

    def _d1(self, S: float, K: float, T: float, sigma: float) -> float:
        """Compute d1 parameter.

        Args:
            S: Current stock price
            K: Strike price
            T: Time to maturity
            sigma: Volatility

        Returns:
            d1 value
        """
        return (math.log(S / K) + (self._risk_free_rate + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))

    def _d2(self, d1: float, sigma: float, T: float) -> float:
        """Compute d2 parameter.

        Args:
            d1: d1 value
            sigma: Volatility
            T: Time to maturity

        Returns:
            d2 value
        """
        return d1 - sigma * math.sqrt(T)

    def _cdf(self, x: float) -> float:
        """Compute cumulative distribution function of standard normal.

        Args:
            x: Value

        Returns:
            CDF value
        """
        return 0.5 * (1 + math.erf(x / math.sqrt(2)))

    def delta(
        self,
        S: float,
        K: float,
        T: float,
        sigma: float,
        option_type: str = "call",
    ) -> float:
        """Compute delta (sensitivity to underlying price).

        Args:
            S: Current stock price
            K: Strike price
            T: Time to maturity
            sigma: Volatility
            option_type: Option type (call or put)

        Returns:
            Delta value

        Example:
            >>> delta = pricer.delta(S=100, K=100, T=1, sigma=0.2)
        """
        d1 = self._d1(S, K, T, sigma)

        if option_type == "call":
            return self._cdf(d1)
        else:
            return self._cdf(d1) - 1

    def gamma(
        self,
        S: float,
        K: float,
        T: float,
        sigma: float,
    ) -> float:
        """Compute gamma (second derivative with respect to underlying price).

        Args:
            S: Current stock price
            K: Strike price
            T: Time to maturity
            sigma: Volatility

        Returns:
            Gamma value

        Example:
            >>> gamma = pricer.gamma(S=100, K=100, T=1, sigma=0.2)
        """
        d1 = self._d1(S, K, T, sigma)
        return self._pdf(d1) / (S * sigma * math.sqrt(T))

    def _pdf(self, x: float) -> float:
        """Compute probability density function of standard normal.

        Args:
            x: Value

        Returns:
            PDF value
        """
        return math.exp(-0.5 * x ** 2) / math.sqrt(2 * math.pi)

    def vega(
        self,
        S: float,
        K: float,
        T: float,
        sigma: float,
    ) -> float:
        """Compute vega (sensitivity to volatility).

        Args:
            S: Current stock price
            K: Strike price
            T: Time to maturity
            sigma: Volatility

        Returns:
            Vega value

        Example:
            >>> vega = pricer.vega(S=100, K=100, T=1, sigma=0.2)
        """
        d1 = self._d1(S, K, T, sigma)
        return S * self._pdf(d1) * math.sqrt(T)

    def theta(
        self,
        S: float,
        K: float,
        T: float,
        sigma: float,
        option_type: str = "call",
    ) -> float:
        """Compute theta (sensitivity to time).

        Args:
            S: Current stock price
            K: Strike price
            T: Time to maturity
            sigma: Volatility
            option_type: Option type (call or put)

        Returns:
            Theta value

        Example:
            >>> theta = pricer.theta(S=100, K=100, T=1, sigma=0.2)
        """
        d1 = self._d1(S, K, T, sigma)
        d2 = self._d2(d1, sigma, T)

        term1 = -(S * self._pdf(d1) * sigma) / (2 * math.sqrt(T))

        if option_type == "call":
            term2 = -self._risk_free_rate * K * math.exp(-self._risk_free_rate * T) * self._cdf(d2)
        else:
            term2 = self._risk_free_rate * K * math.exp(-self._risk_free_rate * T) * self._cdf(-d2)

        return term1 + term2

    def rho(
        self,
        S: float,
        K: float,
        T: float,
        sigma: float,
        option_type: str = "call",
    ) -> float:
        """Compute rho (sensitivity to interest rate).

        Args:
            S: Current stock price
            K: Strike price
            T: Time to maturity
            sigma: Volatility
            option_type: Option type (call or put)

        Returns:
            Rho value

        Example:
            >>> rho = pricer.rho(S=100, K=100, T=1, sigma=0.2)
        """
        d2 = self._d2(self._d1(S, K, T, sigma), sigma, T)

        if option_type == "call":
            return K * T * math.exp(-self._risk_free_rate * T) * self._cdf(d2)
        else:
            return -K * T * math.exp(-self._risk_free_rate * T) * self._cdf(-d2)

    def implied_volatility(
        self,
        S: float,
        K: float,
        T: float,
        market_price: float,
        option_type: str = "call",
        max_iterations: int = 100,
        tolerance: float = 1e-6,
    ) -> float:
        """Compute implied volatility using Newton-Raphson.

        Args:
            S: Current stock price
            K: Strike price
            T: Time to maturity
            market_price: Market price of option
            option_type: Option type (call or put)
            max_iterations: Maximum iterations
            tolerance: Convergence tolerance

        Returns:
            Implied volatility

        Example:
            >>> iv = pricer.implied_volatility(S=100, K=100, T=1, market_price=10)
        """
        sigma = 0.2  # Initial guess

        for _ in range(max_iterations):
            if option_type == "call":
                model_price = self.black_scholes_call(S, K, T, sigma)
            else:
                model_price = self.black_scholes_put(S, K, T, sigma)

            diff = model_price - market_price

            if abs(diff) < tolerance:
                break

            # Vega as derivative of price with respect to volatility
            vega = self.vega(S, K, T, sigma)

            if vega == 0:
                break

            sigma = sigma - diff / vega

            if sigma < 0:
                sigma = 0.01

        return sigma

    def binomial_tree(
        self,
        S: float,
        K: float,
        T: float,
        sigma: float,
        steps: int = 100,
        option_type: str = "call",
        american: bool = False,
    ) -> float:
        """Price option using binomial tree method.

        Args:
            S: Current stock price
            K: Strike price
            T: Time to maturity
            sigma: Volatility
            steps: Number of time steps
            option_type: Option type (call or put)
            american: Whether option is American

        Returns:
            Option price

        Example:
            >>> price = pricer.binomial_tree(S=100, K=100, T=1, sigma=0.2)
        """
        dt = T / steps
        u = math.exp(sigma * math.sqrt(dt))
        d = 1 / u
        p = (math.exp(self._risk_free_rate * dt) - d) / (u - d)

        # Initialize stock price tree
        stock_prices = [[0.0] * (i + 1) for i in range(steps + 1)]
        for i in range(steps + 1):
            for j in range(i + 1):
                stock_prices[i][j] = S * (u ** (i - j)) * (d ** j)

        # Initialize option values at maturity
        option_values = [[0.0] * (i + 1) for i in range(steps + 1)]
        for j in range(steps + 1):
            if option_type == "call":
                option_values[steps][j] = max(0, stock_prices[steps][j] - K)
            else:
                option_values[steps][j] = max(0, K - stock_prices[steps][j])

        # Backward induction
        for i in range(steps - 1, -1, -1):
            for j in range(i + 1):
                option_values[i][j] = math.exp(-self._risk_free_rate * dt) * (
                    p * option_values[i + 1][j] + (1 - p) * option_values[i + 1][j + 1]
                )

                # Early exercise for American options
                if american:
                    if option_type == "call":
                        exercise_value = max(0, stock_prices[i][j] - K)
                    else:
                        exercise_value = max(0, K - stock_prices[i][j])
                    option_values[i][j] = max(option_values[i][j], exercise_value)

        return option_values[0][0]

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(pricer)
        """
        return f"OptionPricer(name={self._name}, r={self._risk_free_rate})"


__all__ = [
    "OptionPricer",
]
