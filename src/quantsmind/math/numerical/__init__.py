"""
Numerical Methods Module

This module provides numerical methods for the Mathematics package.
Numerical methods represent algorithms for solving mathematical problems numerically.

Purpose
-------
Provide numerical methods for the Mathematics package.

Scientific Meaning
------------------
Numerical methods represent algorithms for solving mathematical problems that cannot be
solved analytically, essential for scientific computing, engineering, and applied mathematics.

Responsibilities
----------------
- Support numerical solvers
- Enable interpolation
- Support approximation
- Handle root finding

Dependencies
------------
typing (standard library)
quantsmind.math.exceptions (exception hierarchy)
quantsmind.math.types (type definitions)

Future Extensions
-----------------
- Advanced root finding
- Numerical integration
- Differential equation solvers
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import List, Optional, Tuple, Union

from quantsmind.math.exceptions import ConvergenceError
from quantsmind.math.types import Scalar, Vector

logger = logging.getLogger(__name__)


class NumericalSolver:
    """Concrete implementation of a numerical solver.

    This class provides numerical methods for solving equations.

    Scientific Meaning
    ------------------
    In numerical analysis, numerical solvers represent algorithms for finding approximate
    solutions to mathematical problems.

    Example:
        >>> solver = NumericalSolver()
        >>> root = solver.find_root(lambda x: x**2 - 4, 1.0)
    """

    def __init__(self, max_iterations: int = 1000, tolerance: float = 1e-10) -> None:
        """Initialize a NumericalSolver.

        Args:
            max_iterations: Maximum number of iterations
            tolerance: Convergence tolerance

        Example:
            >>> solver = NumericalSolver(max_iterations=1000, tolerance=1e-10)
        """
        self._max_iterations = max_iterations
        self._tolerance = tolerance
        logger.debug(f"Created numerical solver with max_iterations={max_iterations}")

    def find_root(
        self,
        func: Callable[[Scalar], Scalar],
        initial_guess: Scalar,
        method: str = "newton"
    ) -> Scalar:
        """Find a root of a function.

        Args:
            func: Function to find root of
            initial_guess: Initial guess
            method: Method ("newton", "bisection")

        Returns:
            Root value

        Raises:
            ConvergenceError: If method fails to converge

        Example:
            >>> root = solver.find_root(lambda x: x**2 - 4, 1.0)
        """
        if method == "newton":
            return self._newton_raphson(func, initial_guess)
        elif method == "bisection":
            return self._bisection(func, initial_guess)
        else:
            raise ValueError(f"Unknown method: {method}")

    def _newton_raphson(self, func: Callable[[Scalar], Scalar], x0: Scalar) -> Scalar:
        """Newton-Raphson method for root finding.

        Args:
            func: Function to find root of
            x0: Initial guess

        Returns:
            Root value

        Raises:
            ConvergenceError: If method fails to converge
        """
        x = x0
        for iteration in range(self._max_iterations):
            f_x = func(x)
            if abs(f_x) < self._tolerance:
                logger.info(f"Newton-Raphson converged at iteration {iteration}")
                return x

            # Numerical derivative
            h = 1e-6
            f_prime = (func(x + h) - func(x)) / h

            if abs(f_prime) < self._tolerance:
                raise ConvergenceError("Derivative too small, cannot continue")

            x_new = x - f_x / f_prime

            if abs(x_new - x) < self._tolerance:
                logger.info(f"Newton-Raphson converged at iteration {iteration}")
                return x_new

            x = x_new

        raise ConvergenceError("Newton-Raphson failed to converge")

    def _bisection(self, func: Callable[[Scalar], Scalar], x0: Scalar) -> Scalar:
        """Bisection method for root finding.

        Args:
            func: Function to find root of
            x0: Initial guess

        Returns:
            Root value

        Raises:
            ConvergenceError: If method fails to converge
        """
        # Find interval containing root
        a = x0 - 1.0
        b = x0 + 1.0

        # Expand interval until sign change
        while func(a) * func(b) > 0:
            a -= 1.0
            b += 1.0
            if abs(a - b) > 1000:
                raise ConvergenceError("Could not find interval containing root")

        for iteration in range(self._max_iterations):
            c = (a + b) / 2
            f_c = func(c)

            if abs(f_c) < self._tolerance:
                logger.info(f"Bisection converged at iteration {iteration}")
                return c

            if func(a) * f_c < 0:
                b = c
            else:
                a = c

            if abs(b - a) < self._tolerance:
                logger.info(f"Bisection converged at iteration {iteration}")
                return c

        raise ConvergenceError("Bisection failed to converge")


class Interpolation:
    """Concrete implementation of interpolation methods.

    This class provides interpolation for approximating functions.

    Scientific Meaning
    ------------------
    In numerical analysis, interpolation represents constructing new data points within
    the range of a discrete set of known data points.

    Example:
        >>> interp = Interpolation()
        >>> value = interp.linear([1, 2, 3], [1, 4, 9], 2.5)
    """

    @staticmethod
    def linear(x_data: list[Scalar], y_data: list[Scalar], x: Scalar) -> Scalar:
        """Linear interpolation.

        Args:
            x_data: X values
            y_data: Y values
            x: Point to interpolate

        Returns:
            Interpolated value

        Raises:
            ValueError: If data is insufficient

        Example:
            >>> value = Interpolation.linear([1, 2, 3], [1, 4, 9], 2.5)
        """
        if len(x_data) != len(y_data):
            raise ValueError("x_data and y_data must have same length")
        if len(x_data) < 2:
            raise ValueError("Need at least 2 data points")

        # Find interval
        for i in range(len(x_data) - 1):
            if x_data[i] <= x <= x_data[i + 1]:
                x0, x1 = x_data[i], x_data[i + 1]
                y0, y1 = y_data[i], y_data[i + 1]
                return y0 + (y1 - y0) * (x - x0) / (x1 - x0)

        # Extrapolate
        if x < x_data[0]:
            x0, x1 = x_data[0], x_data[1]
            y0, y1 = y_data[0], y_data[1]
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
        else:
            x0, x1 = x_data[-2], x_data[-1]
            y0, y1 = y_data[-2], y_data[-1]
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)

    @staticmethod
    def polynomial(x_data: list[Scalar], y_data: list[Scalar], x: Scalar, degree: int = 2) -> Scalar:
        """Polynomial interpolation.

        Args:
            x_data: X values
            y_data: Y values
            x: Point to interpolate
            degree: Polynomial degree

        Returns:
            Interpolated value

        Raises:
            ValueError: If data is insufficient

        Example:
            >>> value = Interpolation.polynomial([1, 2, 3], [1, 4, 9], 2.5, degree=2)
        """
        if len(x_data) != len(y_data):
            raise ValueError("x_data and y_data must have same length")
        if len(x_data) < degree + 1:
            raise ValueError(f"Need at least {degree + 1} data points")

        # Lagrange interpolation
        result = 0.0
        for i in range(degree + 1):
            term = y_data[i]
            for j in range(degree + 1):
                if i != j:
                    term *= (x - x_data[j]) / (x_data[i] - x_data[j])
            result += term

        return result


class Approximation:
    """Concrete implementation of approximation methods.

    This class provides approximation for complex functions.

    Scientific Meaning
    ------------------
    In numerical analysis, approximation represents representing complex functions
    with simpler functions for easier computation.

    Example:
        >>> approx = Approximation()
        >>> value = approx.taylor(lambda x: math.sin(x), 0.0, 1.0, 3)
    """

    @staticmethod
    def taylor(
        func: Callable[[Scalar], Scalar],
        center: Scalar,
        x: Scalar,
        degree: int,
        h: float = 1e-6
    ) -> Scalar:
        """Taylor series approximation.

        Args:
            func: Function to approximate
            center: Center point
            x: Point to evaluate
            degree: Degree of approximation
            h: Step size for numerical derivatives

        Returns:
            Approximated value

        Example:
            >>> value = Approximation.taylor(lambda x: math.sin(x), 0.0, 1.0, 3)
        """
        result = func(center)
        factorial = 1

        for n in range(1, degree + 1):
            factorial *= n

            # Numerical derivative
            if n == 1:
                derivative = (func(center + h) - func(center - h)) / (2 * h)
            else:
                # Simplified: use finite difference
                derivative = (func(center + h) - func(center)) / h

            result += derivative * (x - center) ** n / factorial

        return result


class RootFinding:
    """Concrete implementation of root finding methods.

    This class provides algorithms for finding roots of equations.

    Scientific Meaning
    ------------------
    In numerical analysis, root finding represents algorithms for solving equations
    of the form f(x) = 0.

    Example:
        >>> rf = RootFinding()
        >>> root = rf.bisection(lambda x: x**2 - 4, 0.0, 3.0)
    """

    @staticmethod
    def bisection(
        func: Callable[[Scalar], Scalar],
        a: Scalar,
        b: Scalar,
        tolerance: float = 1e-10,
        max_iterations: int = 1000
    ) -> Scalar:
        """Bisection method for root finding.

        Args:
            func: Function to find root of
            a: Lower bound
            b: Upper bound
            tolerance: Convergence tolerance
            max_iterations: Maximum iterations

        Returns:
            Root value

        Raises:
            ValueError: If no sign change in interval
            ConvergenceError: If method fails to converge

        Example:
            >>> root = RootFinding.bisection(lambda x: x**2 - 4, 0.0, 3.0)
        """
        if func(a) * func(b) > 0:
            raise ValueError("Function must have different signs at interval endpoints")

        for _iteration in range(max_iterations):
            c = (a + b) / 2
            f_c = func(c)

            if abs(f_c) < tolerance or abs(b - a) < tolerance:
                return c

            if func(a) * f_c < 0:
                b = c
            else:
                a = c

        raise ConvergenceError("Bisection failed to converge")

    @staticmethod
    def secant(
        func: Callable[[Scalar], Scalar],
        x0: Scalar,
        x1: Scalar,
        tolerance: float = 1e-10,
        max_iterations: int = 1000
    ) -> Scalar:
        """Secant method for root finding.

        Args:
            func: Function to find root of
            x0: First initial guess
            x1: Second initial guess
            tolerance: Convergence tolerance
            max_iterations: Maximum iterations

        Returns:
            Root value

        Raises:
            ConvergenceError: If method fails to converge

        Example:
            >>> root = RootFinding.secant(lambda x: x**2 - 4, 1.0, 2.0)
        """
        for _iteration in range(max_iterations):
            f_x0 = func(x0)
            f_x1 = func(x1)

            if abs(f_x1) < tolerance:
                return x1

            if abs(f_x1 - f_x0) < tolerance:
                raise ConvergenceError("Function values too close, cannot continue")

            x_new = x1 - f_x1 * (x1 - x0) / (f_x1 - f_x0)

            if abs(x_new - x1) < tolerance:
                return x_new

            x0, x1 = x1, x_new

        raise ConvergenceError("Secant method failed to converge")


# Export
__all__ = [
    "NumericalSolver",
    "Interpolation",
    "Approximation",
    "RootFinding",
]
