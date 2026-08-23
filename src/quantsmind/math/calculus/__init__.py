"""
Calculus Module

This module provides calculus operations for the Mathematics package.
Calculus represents differentiation, integration, and differential equations.

Purpose
-------
Provide calculus operations for the Mathematics package.

Scientific Meaning
------------------
Calculus represents the mathematical study of continuous change, essential for
physics, engineering, economics, and many other scientific applications.

Responsibilities
----------------
- Support derivative calculations
- Enable integration operations
- Support differential equations
- Handle calculus validation

Dependencies
------------
typing (standard library)
math (standard library)
quantsmind.math.exceptions (exception hierarchy)
quantsmind.math.types (type definitions)

Future Extensions
-----------------
- Symbolic differentiation
- Numerical integration
- Differential equation solvers
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import List, Optional, Tuple, Union

from quantsmind.math.exceptions import ConvergenceError
from quantsmind.math.exceptions import ValueError as MathValueError
from quantsmind.math.types import Scalar, Vector

logger = logging.getLogger(__name__)


class Derivative:
    """Concrete implementation of derivative calculation.

    This class provides numerical derivative calculation using finite differences.

    Scientific Meaning
    ------------------
    In calculus, the derivative represents the rate of change of a function with respect to its variable.

    Example:
        >>> def f(x): return x ** 2
        >>> derivative = Derivative.numerical(f, 2.0)
    """

    @staticmethod
    def numerical(
        func: Callable[[Scalar], Scalar],
        x: Scalar,
        h: float = 1e-6,
        method: str = "central"
    ) -> float:
        """Calculate numerical derivative.

        Args:
            func: Function to differentiate
            x: Point at which to calculate derivative
            h: Step size
            method: Method ("forward", "backward", "central")

        Returns:
            Derivative value

        Example:
            >>> derivative = Derivative.numerical(lambda x: x**2, 2.0)
        """
        if method == "forward":
            return (func(x + h) - func(x)) / h
        elif method == "backward":
            return (func(x) - func(x - h)) / h
        elif method == "central":
            return (func(x + h) - func(x - h)) / (2 * h)
        else:
            raise MathValueError(f"Unknown method: {method}")

    @staticmethod
    def partial(
        func: Callable[[Vector], Scalar],
        x: Vector,
        index: int,
        h: float = 1e-6
    ) -> float:
        """Calculate partial derivative.

        Args:
            func: Function to differentiate
            x: Point at which to calculate derivative
            index: Index of variable to differentiate
            h: Step size

        Returns:
            Partial derivative value

        Example:
            >>> partial = Derivative.partial(lambda x: x[0]**2 + x[1]**2, [1.0, 2.0], 0)
        """
        x_plus = x.copy()
        x_plus[index] += h
        x_minus = x.copy()
        x_minus[index] -= h
        return (func(x_plus) - func(x_minus)) / (2 * h)


class Integral:
    """Concrete implementation of integral calculation.

    This class provides numerical integration using various methods.

    Scientific Meaning
    ------------------
    In calculus, the integral represents the accumulation of quantities, such as area under a curve.

    Example:
        >>> def f(x): return x ** 2
        >>> integral = Integral.riemann(f, 0.0, 1.0, n=100)
    """

    @staticmethod
    def riemann(
        func: Callable[[Scalar], Scalar],
        a: float,
        b: float,
        n: int = 100,
        method: str = "midpoint"
    ) -> float:
        """Calculate Riemann sum approximation.

        Args:
            func: Function to integrate
            a: Lower bound
            b: Upper bound
            n: Number of intervals
            method: Method ("left", "right", "midpoint")

        Returns:
            Integral approximation

        Example:
            >>> integral = Integral.riemann(lambda x: x**2, 0.0, 1.0, n=100)
        """
        if n <= 0:
            raise MathValueError("Number of intervals must be positive")

        dx = (b - a) / n
        total = 0.0

        for i in range(n):
            if method == "left":
                x = a + i * dx
            elif method == "right":
                x = a + (i + 1) * dx
            elif method == "midpoint":
                x = a + (i + 0.5) * dx
            else:
                raise MathValueError(f"Unknown method: {method}")
            total += func(x) * dx

        return total

    @staticmethod
    def trapezoidal(
        func: Callable[[Scalar], Scalar],
        a: float,
        b: float,
        n: int = 100
    ) -> float:
        """Calculate trapezoidal rule approximation.

        Args:
            func: Function to integrate
            a: Lower bound
            b: Upper bound
            n: Number of intervals

        Returns:
            Integral approximation

        Example:
            >>> integral = Integral.trapezoidal(lambda x: x**2, 0.0, 1.0, n=100)
        """
        if n <= 0:
            raise MathValueError("Number of intervals must be positive")

        dx = (b - a) / n
        total = 0.5 * (func(a) + func(b))

        for i in range(1, n):
            x = a + i * dx
            total += func(x)

        return total * dx

    @staticmethod
    def simpson(
        func: Callable[[Scalar], Scalar],
        a: float,
        b: float,
        n: int = 100
    ) -> float:
        """Calculate Simpson's rule approximation.

        Args:
            func: Function to integrate
            a: Lower bound
            b: Upper bound
            n: Number of intervals (must be even)

        Returns:
            Integral approximation

        Raises:
            ValueError: If n is not even

        Example:
            >>> integral = Integral.simpson(lambda x: x**2, 0.0, 1.0, n=100)
        """
        if n <= 0:
            raise MathValueError("Number of intervals must be positive")
        if n % 2 != 0:
            raise MathValueError("Number of intervals must be even")

        dx = (b - a) / n
        total = func(a) + func(b)

        for i in range(1, n):
            x = a + i * dx
            if i % 2 == 0:
                total += 2 * func(x)
            else:
                total += 4 * func(x)

        return total * dx / 3.0


class Gradient:
    """Concrete implementation of gradient calculation.

    This class provides gradient calculation for multivariate functions.

    Scientific Meaning
    ------------------
    In calculus, the gradient represents the vector of partial derivatives,
    pointing in the direction of steepest ascent.

    Example:
        >>> def f(x): return x[0]**2 + x[1]**2
        >>> grad = Gradient.calculate(f, [1.0, 2.0])
    """

    @staticmethod
    def calculate(
        func: Callable[[Vector], Scalar],
        x: Vector,
        h: float = 1e-6
    ) -> Vector:
        """Calculate gradient.

        Args:
            func: Function to differentiate
            x: Point at which to calculate gradient
            h: Step size

        Returns:
            Gradient vector

        Example:
            >>> grad = Gradient.calculate(lambda x: x[0]**2 + x[1]**2, [1.0, 2.0])
        """
        gradient = []
        for i in range(len(x)):
            partial = Derivative.partial(func, x, i, h)
            gradient.append(partial)
        return gradient


class Jacobian:
    """Concrete implementation of Jacobian matrix calculation.

    This class provides Jacobian matrix calculation for vector-valued functions.

    Scientific Meaning
    ------------------
    In calculus, the Jacobian matrix represents the matrix of all first-order partial derivatives
    of a vector-valued function.

    Example:
        >>> def f(x): return [x[0]**2, x[0] * x[1]]
        >>> jacobian = Jacobian.calculate(f, [1.0, 2.0])
    """

    @staticmethod
    def calculate(
        func: Callable[[Vector], Vector],
        x: Vector,
        h: float = 1e-6
    ) -> list[list[float]]:
        """Calculate Jacobian matrix.

        Args:
            func: Vector-valued function
            x: Point at which to calculate Jacobian
            h: Step size

        Returns:
            Jacobian matrix

        Example:
            >>> jacobian = Jacobian.calculate(lambda x: [x[0]**2, x[0]*x[1]], [1.0, 2.0])
        """
        jacobian = []
        f_x = func(x)

        for i in range(len(f_x)):
            row = []
            for j in range(len(x)):
                x_plus = x.copy()
                x_plus[j] += h
                f_x_plus = func(x_plus)
                partial = (f_x_plus[i] - f_x[i]) / h
                row.append(partial)
            jacobian.append(row)

        return jacobian


class Hessian:
    """Concrete implementation of Hessian matrix calculation.

    This class provides Hessian matrix calculation for scalar-valued functions.

    Scientific Meaning
    ------------------
    In calculus, the Hessian matrix represents the matrix of second-order partial derivatives,
    used in optimization and analyzing curvature.

    Example:
        >>> def f(x): return x[0]**2 + x[1]**2
        >>> hessian = Hessian.calculate(f, [1.0, 2.0])
    """

    @staticmethod
    def calculate(
        func: Callable[[Vector], Scalar],
        x: Vector,
        h: float = 1e-6
    ) -> list[list[float]]:
        """Calculate Hessian matrix.

        Args:
            func: Scalar-valued function
            x: Point at which to calculate Hessian
            h: Step size

        Returns:
            Hessian matrix

        Example:
            >>> hessian = Hessian.calculate(lambda x: x[0]**2 + x[1]**2, [1.0, 2.0])
        """
        n = len(x)
        hessian = [[0.0] * n for _ in range(n)]

        for i in range(n):
            for j in range(n):
                # Calculate second partial derivative
                x_pp = x.copy()
                x_pp[i] += h
                x_pp[j] += h
                f_pp = func(x_pp)

                x_pm = x.copy()
                x_pm[i] += h
                x_pm[j] -= h
                f_pm = func(x_pm)

                x_mp = x.copy()
                x_mp[i] -= h
                x_mp[j] += h
                f_mp = func(x_mp)

                x_mm = x.copy()
                x_mm[i] -= h
                x_mm[j] -= h
                f_mm = func(x_mm)

                second_partial = (f_pp - f_pm - f_mp + f_mm) / (4 * h ** 2)
                hessian[i][j] = second_partial

        return hessian


# Export
__all__ = [
    "Derivative",
    "Integral",
    "Gradient",
    "Jacobian",
    "Hessian",
]

