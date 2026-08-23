"""
Integration Module

This module provides integration functionality for the QuantsMind SDK.

Purpose
-------
Provide numerical integration capabilities.

Classes
-------
Integrator: Integration engine

Responsibilities
----------------
- Compute definite integrals
- Compute indefinite integrals
- Compute numerical integrals
- Compute Monte Carlo integrals

Dependencies
------------
typing (standard library)
quantsmind.algebra.polynomial (Polynomial)
"""

from __future__ import annotations

import random
from collections.abc import Callable
from typing import Any

from quantsmind.algebra.polynomial import Polynomial


class Integrator:
    """Integration engine.

    This class provides functionality for computing integrals of functions,
    including numerical integration methods.

    Attributes:
        _method: Integration method (trapezoidal, simpson, monte_carlo)
        _n: Number of subdivisions for numerical integration
        _metadata: Additional metadata

    Example:
        >>> integrator = Integrator(method="simpson", n=1000)
        >>> result = integrator.definite_integral(lambda x: x**2, 0, 1)
    """

    def __init__(
        self,
        method: str = "simpson",
        n: int = 1000,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize an Integrator.

        Args:
            method: Integration method (trapezoidal, simpson, monte_carlo)
            n: Number of subdivisions
            metadata: Additional metadata

        Example:
            >>> integrator = Integrator(method="simpson", n=1000)
        """
        self._method = method
        self._n = n
        self._metadata = metadata or {}

    @property
    def method(self) -> str:
        """Get the integration method.

        Returns:
            Integration method

        Example:
            >>> method = integrator.method
        """
        return self._method

    @property
    def n(self) -> int:
        """Get the number of subdivisions.

        Returns:
            Number of subdivisions

        Example:
            >>> n = integrator.n
        """
        return self._n

    def set_n(self, n: int) -> None:
        """Set the number of subdivisions.

        Args:
            n: Number of subdivisions

        Example:
            >>> integrator.set_n(2000)
        """
        if n <= 0:
            raise ValueError("Number of subdivisions must be positive")
        self._n = n

    def definite_integral(
        self,
        func: Callable[[float], float],
        a: float,
        b: float,
    ) -> float:
        """Compute a definite integral.

        Args:
            func: Function to integrate
            a: Lower bound
            b: Upper bound

        Returns:
            Integral value

        Example:
            >>> result = integrator.definite_integral(lambda x: x**2, 0, 1)
        """
        if self._method == "trapezoidal":
            return self._trapezoidal(func, a, b)
        elif self._method == "simpson":
            return self._simpson(func, a, b)
        elif self._method == "monte_carlo":
            return self._monte_carlo(func, a, b)
        else:
            raise NotImplementedError(f"Method {self._method} not implemented")

    def _trapezoidal(
        self,
        func: Callable[[float], float],
        a: float,
        b: float,
    ) -> float:
        """Trapezoidal rule integration.

        Args:
            func: Function to integrate
            a: Lower bound
            b: Upper bound

        Returns:
            Integral value
        """
        h = (b - a) / self._n
        result = 0.5 * (func(a) + func(b))

        for i in range(1, self._n):
            x = a + i * h
            result += func(x)

        return result * h

    def _simpson(
        self,
        func: Callable[[float], float],
        a: float,
        b: float,
    ) -> float:
        """Simpson's rule integration.

        Args:
            func: Function to integrate
            a: Lower bound
            b: Upper bound

        Returns:
            Integral value
        """
        if self._n % 2 != 0:
            self._n += 1  # Simpson's rule requires even number of intervals

        h = (b - a) / self._n
        result = func(a) + func(b)

        for i in range(1, self._n):
            x = a + i * h
            if i % 2 == 0:
                result += 2 * func(x)
            else:
                result += 4 * func(x)

        return result * h / 3

    def _monte_carlo(
        self,
        func: Callable[[float], float],
        a: float,
        b: float,
    ) -> float:
        """Monte Carlo integration.

        Args:
            func: Function to integrate
            a: Lower bound
            b: Upper bound

        Returns:
            Integral value
        """
        total = 0.0
        for _ in range(self._n):
            x = random.uniform(a, b)
            total += func(x)

        return (b - a) * total / self._n

    def indefinite_integral(self, poly: Polynomial) -> Polynomial:
        """Compute indefinite integral of a polynomial.

        Args:
            poly: Polynomial to integrate

        Returns:
            Integral polynomial

        Example:
            >>> integral = integrator.indefinite_integral(poly)
        """
        return poly.integral()

    def numerical_integral(
        self,
        func: Callable[[float], float],
        a: float,
        b: float,
        method: str = "simpson",
    ) -> float:
        """Compute numerical integral with specified method.

        Args:
            func: Function to integrate
            a: Lower bound
            b: Upper bound
            method: Integration method

        Returns:
            Integral value

        Example:
            >>> result = integrator.numerical_integral(lambda x: x**2, 0, 1, "trapezoidal")
        """
        original_method = self._method
        self._method = method
        result = self.definite_integral(func, a, b)
        self._method = original_method
        return result

    def monte_carlo_integral(
        self,
        func: Callable[[list[float]], float],
        bounds: list[tuple[float, float]],
        n_samples: int | None = None,
    ) -> float:
        """Compute Monte Carlo integral for multivariate function.

        Args:
            func: Multivariate function
            bounds: List of (lower, upper) bounds for each dimension
            n_samples: Number of samples (uses default if not provided)

        Returns:
            Integral value

        Example:
            >>> result = integrator.monte_carlo_integral(lambda x: x[0]**2 + x[1]**2, [(0, 1), (0, 1)])
        """
        n = n_samples if n_samples is not None else self._n
        len(bounds)
        volume = 1.0
        for a, b in bounds:
            volume *= (b - a)

        total = 0.0
        for _ in range(n):
            x = [random.uniform(a, b) for a, b in bounds]
            total += func(x)

        return volume * total / n

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(integrator)
        """
        return f"Integrator(method={self._method}, n={self._n})"


__all__ = [
    "Integrator",
]
