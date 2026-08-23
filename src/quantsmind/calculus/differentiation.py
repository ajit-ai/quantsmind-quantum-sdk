"""
Differentiation Module

This module provides differentiation functionality for the QuantsMind SDK.

Purpose
-------
Provide numerical and symbolic differentiation capabilities.

Classes
-------
Differentiator: Differentiation engine

Responsibilities
----------------
- Compute first derivatives
- Compute second derivatives
- Compute partial derivatives
- Compute gradients
- Compute Jacobians
- Compute Hessians

Dependencies
------------
typing (standard library)
quantsmind.core.math_object (MathObject)
quantsmind.algebra.polynomial (Polynomial)
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from quantsmind.algebra.polynomial import Polynomial


class Differentiator:
    """Differentiation engine.

    This class provides functionality for computing derivatives of functions,
    including numerical differentiation for arbitrary functions and symbolic
    differentiation for polynomials.

    Attributes:
        _method: Differentiation method (numerical, symbolic)
        _h: Step size for numerical differentiation
        _metadata: Additional metadata

    Example:
        >>> diff = Differentiator(method="numerical", h=1e-6)
        >>> derivative = diff.first_derivative(lambda x: x**2, x=2.0)
    """

    def __init__(
        self,
        method: str = "numerical",
        h: float = 1e-6,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a Differentiator.

        Args:
            method: Differentiation method (numerical, symbolic)
            h: Step size for numerical differentiation
            metadata: Additional metadata

        Example:
            >>> diff = Differentiator(method="numerical", h=1e-6)
        """
        self._method = method
        self._h = h
        self._metadata = metadata or {}

    @property
    def method(self) -> str:
        """Get the differentiation method.

        Returns:
            Differentiation method

        Example:
            >>> method = diff.method
        """
        return self._method

    @property
    def h(self) -> float:
        """Get the step size.

        Returns:
            Step size

        Example:
            >>> h = diff.h
        """
        return self._h

    def set_h(self, h: float) -> None:
        """Set the step size.

        Args:
            h: Step size

        Example:
            >>> diff.set_h(1e-8)
        """
        if h <= 0:
            raise ValueError("Step size must be positive")
        self._h = h

    def first_derivative(self, func: Callable[[float], float], x: float) -> float:
        """Compute the first derivative using central difference.

        Args:
            func: Function to differentiate
            x: Point to evaluate at

        Returns:
            First derivative value

        Example:
            >>> derivative = diff.first_derivative(lambda x: x**2, x=2.0)
        """
        if self._method == "numerical":
            return (func(x + self._h) - func(x - self._h)) / (2 * self._h)
        else:
            raise NotImplementedError(f"Method {self._method} not implemented")

    def second_derivative(self, func: Callable[[float], float], x: float) -> float:
        """Compute the second derivative using central difference.

        Args:
            func: Function to differentiate
            x: Point to evaluate at

        Returns:
            Second derivative value

        Example:
            >>> derivative = diff.second_derivative(lambda x: x**2, x=2.0)
        """
        if self._method == "numerical":
            return (func(x + self._h) - 2 * func(x) + func(x - self._h)) / (self._h ** 2)
        else:
            raise NotImplementedError(f"Method {self._method} not implemented")

    def partial_derivative(
        self,
        func: Callable[[list[float]], float],
        x: list[float],
        var_index: int,
    ) -> float:
        """Compute a partial derivative.

        Args:
            func: Multivariate function
            x: Point to evaluate at
            var_index: Index of variable to differentiate with respect to

        Returns:
            Partial derivative value

        Example:
            >>> derivative = diff.partial_derivative(lambda x: x[0]**2 + x[1]**2, [1.0, 2.0], 0)
        """
        if var_index < 0 or var_index >= len(x):
            raise ValueError(f"Variable index {var_index} out of range")

        x_plus = x.copy()
        x_minus = x.copy()
        x_plus[var_index] += self._h
        x_minus[var_index] -= self._h

        return (func(x_plus) - func(x_minus)) / (2 * self._h)

    def gradient(
        self,
        func: Callable[[list[float]], float],
        x: list[float],
    ) -> list[float]:
        """Compute the gradient vector.

        Args:
            func: Multivariate function
            x: Point to evaluate at

        Returns:
            Gradient vector

        Example:
            >>> grad = diff.gradient(lambda x: x[0]**2 + x[1]**2, [1.0, 2.0])
        """
        return [self.partial_derivative(func, x, i) for i in range(len(x))]

    def jacobian(
        self,
        func: Callable[[list[float]], list[float]],
        x: list[float],
    ) -> list[list[float]]:
        """Compute the Jacobian matrix.

        Args:
            func: Vector-valued function
            x: Point to evaluate at

        Returns:
            Jacobian matrix

        Example:
            >>> jac = diff.jacobian(lambda x: [x[0]**2, x[0]*x[1]], [1.0, 2.0])
        """
        # Evaluate function to get output dimension
        f_x = func(x)
        output_dim = len(f_x)
        len(x)

        jacobian = []
        for i in range(output_dim):
            # Compute gradient of i-th component function
            def component_func(x_vals: list[float]) -> float:
                return func(x_vals)[i]

            grad = self.gradient(component_func, x)
            jacobian.append(grad)

        return jacobian

    def hessian(
        self,
        func: Callable[[list[float]], float],
        x: list[float],
    ) -> list[list[float]]:
        """Compute the Hessian matrix.

        Args:
            func: Multivariate function
            x: Point to evaluate at

        Returns:
            Hessian matrix

        Example:
            >>> hess = diff.hessian(lambda x: x[0]**2 + x[1]**2, [1.0, 2.0])
        """
        n = len(x)
        hessian = [[0.0] * n for _ in range(n)]

        for i in range(n):
            for j in range(n):
                # Compute second partial derivative
                def partial_func(x_vals: list[float]) -> float:
                    return self.partial_derivative(func, x_vals, i)

                hessian[i][j] = self.partial_derivative(partial_func, x, j)

        return hessian

    def differentiate_polynomial(self, poly: Polynomial) -> Polynomial:
        """Differentiate a polynomial symbolically.

        Args:
            poly: Polynomial to differentiate

        Returns:
            Derivative polynomial

        Example:
            >>> deriv = diff.differentiate_polynomial(poly)
        """
        return poly.derivative()

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(diff)
        """
        return f"Differentiator(method={self._method}, h={self._h})"


__all__ = [
    "Differentiator",
]
