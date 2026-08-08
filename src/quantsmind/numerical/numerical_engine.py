"""
Numerical Engine Module

This module provides numerical computing functionality for the QuantsMind SDK.

Purpose
-------
Provide numerical methods including root finding, interpolation, curve fitting,
approximation, and error analysis.

Functions
-------
root_finding: Find roots of equations
interpolation: Interpolate data points
extrapolation: Extrapolate beyond data range
curve_fit: Fit curves to data
approximation: Approximate functions
error_analysis: Analyze numerical errors

Dependencies
------------
typing (standard library)
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Tuple
import math


def root_finding(
    func: Callable[[float], float],
    a: float,
    b: float,
    method: str = "bisection",
    tolerance: float = 1e-6,
    max_iterations: int = 1000,
) -> float:
    """Find a root of a function in the interval [a, b].

    Args:
        func: Function to find root of
        a: Lower bound
        b: Upper bound
        method: Root finding method (bisection, newton, secant)
        tolerance: Convergence tolerance
        max_iterations: Maximum iterations

    Returns:
        Root value

    Example:
        >>> root = root_finding(lambda x: x**2 - 4, 0, 3)
    """
    if method == "bisection":
        return _bisection(func, a, b, tolerance, max_iterations)
    elif method == "newton":
        return _newton_root(func, a, tolerance, max_iterations)
    elif method == "secant":
        return _secant(func, a, b, tolerance, max_iterations)
    else:
        raise ValueError(f"Unknown method: {method}")


def _bisection(
    func: Callable[[float], float],
    a: float,
    b: float,
    tolerance: float,
    max_iterations: int,
) -> float:
    """Bisection method for root finding.

    Args:
        func: Function to find root of
        a: Lower bound
        b: Upper bound
        tolerance: Convergence tolerance
        max_iterations: Maximum iterations

    Returns:
        Root value
    """
    fa = func(a)
    fb = func(b)

    if fa * fb > 0:
        raise ValueError("Function must have opposite signs at endpoints")

    for _ in range(max_iterations):
        c = (a + b) / 2
        fc = func(c)

        if abs(fc) < tolerance or (b - a) / 2 < tolerance:
            return c

        if fa * fc < 0:
            b = c
            fb = fc
        else:
            a = c
            fa = fc

    return (a + b) / 2


def _newton_root(
    func: Callable[[float], float],
    x0: float,
    tolerance: float,
    max_iterations: int,
) -> float:
    """Newton's method for root finding.

    Args:
        func: Function to find root of
        x0: Initial guess
        tolerance: Convergence tolerance
        max_iterations: Maximum iterations

    Returns:
        Root value
    """
    x = x0
    h = 1e-6

    for _ in range(max_iterations):
        fx = func(x)
        if abs(fx) < tolerance:
            return x

        # Numerical derivative
        fpx = (func(x + h) - func(x - h)) / (2 * h)

        if abs(fpx) < 1e-10:
            break

        x_new = x - fx / fpx

        if abs(x_new - x) < tolerance:
            return x_new

        x = x_new

    return x


def _secant(
    func: Callable[[float], float],
    x0: float,
    x1: float,
    tolerance: float,
    max_iterations: int,
) -> float:
    """Secant method for root finding.

    Args:
        func: Function to find root of
        x0: First initial guess
        x1: Second initial guess
        tolerance: Convergence tolerance
        max_iterations: Maximum iterations

    Returns:
        Root value
    """
    for _ in range(max_iterations):
        f0 = func(x0)
        f1 = func(x1)

        if abs(f1) < tolerance:
            return x1

        if abs(f1 - f0) < 1e-10:
            break

        x2 = x1 - f1 * (x1 - x0) / (f1 - f0)

        if abs(x2 - x1) < tolerance:
            return x2

        x0, x1 = x1, x2

    return x1


def interpolation(
    x_data: List[float],
    y_data: List[float],
    x: float,
    method: str = "linear",
) -> float:
    """Interpolate value at point x.

    Args:
        x_data: X data points
        y_data: Y data points
        x: Point to interpolate at
        method: Interpolation method (linear, polynomial, spline)

    Returns:
        Interpolated value

    Example:
        >>> y = interpolation([0, 1, 2], [0, 1, 4], 1.5)
    """
    if len(x_data) != len(y_data):
        raise ValueError("x_data and y_data must have same length")

    if method == "linear":
        return _linear_interpolation(x_data, y_data, x)
    elif method == "polynomial":
        return _polynomial_interpolation(x_data, y_data, x)
    elif method == "spline":
        return _spline_interpolation(x_data, y_data, x)
    else:
        raise ValueError(f"Unknown method: {method}")


def _linear_interpolation(
    x_data: List[float],
    y_data: List[float],
    x: float,
) -> float:
    """Linear interpolation.

    Args:
        x_data: X data points
        y_data: Y data points
        x: Point to interpolate at

    Returns:
        Interpolated value
    """
    # Find interval
    for i in range(len(x_data) - 1):
        if x_data[i] <= x <= x_data[i + 1]:
            x0, x1 = x_data[i], x_data[i + 1]
            y0, y1 = y_data[i], y_data[i + 1]
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)

    # Extrapolate using nearest interval
    if x < x_data[0]:
        return y_data[0]
    else:
        return y_data[-1]


def _polynomial_interpolation(
    x_data: List[float],
    y_data: List[float],
    x: float,
) -> float:
    """Lagrange polynomial interpolation.

    Args:
        x_data: X data points
        y_data: Y data points
        x: Point to interpolate at

    Returns:
        Interpolated value
    """
    n = len(x_data)
    result = 0.0

    for i in range(n):
        term = y_data[i]
        for j in range(n):
            if i != j:
                term *= (x - x_data[j]) / (x_data[i] - x_data[j])
        result += term

    return result


def _spline_interpolation(
    x_data: List[float],
    y_data: List[float],
    x: float,
) -> float:
    """Cubic spline interpolation (simplified).

    Args:
        x_data: X data points
        y_data: Y data points
        x: Point to interpolate at

    Returns:
        Interpolated value
    """
    # Placeholder - real implementation would compute cubic spline coefficients
    # For now, fall back to linear interpolation
    return _linear_interpolation(x_data, y_data, x)


def extrapolation(
    x_data: List[float],
    y_data: List[float],
    x: float,
    method: str = "linear",
) -> float:
    """Extrapolate value at point x beyond data range.

    Args:
        x_data: X data points
        y_data: Y data points
        x: Point to extrapolate at
        method: Extrapolation method (linear, polynomial)

    Returns:
        Extrapolated value

    Example:
        >>> y = extrapolation([0, 1, 2], [0, 1, 4], 3)
    """
    if method == "linear":
        # Use last two points for linear extrapolation
        x0, x1 = x_data[-2], x_data[-1]
        y0, y1 = y_data[-2], y_data[-1]
        return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    elif method == "polynomial":
        # Use polynomial extrapolation
        return _polynomial_interpolation(x_data, y_data, x)
    else:
        raise ValueError(f"Unknown method: {method}")


def curve_fit(
    x_data: List[float],
    y_data: List[float],
    model: Callable[[float, List[float]], float],
    initial_params: List[float],
    tolerance: float = 1e-6,
    max_iterations: int = 1000,
) -> Tuple[List[float], List[float]]:
    """Fit a model to data using least squares.

    Args:
        x_data: X data points
        y_data: Y data points
        model: Model function f(x, params)
        initial_params: Initial parameter values
        tolerance: Convergence tolerance
        max_iterations: Maximum iterations

    Returns:
        Tuple of (optimized_params, residuals)

    Example:
        >>> def linear_model(x, params):
        ...     return params[0] + params[1] * x
        >>> params, residuals = curve_fit(x, y, linear_model, [0, 1])
    """
    params = initial_params.copy()

    for _ in range(max_iterations):
        # Compute residuals
        residuals = [y_data[i] - model(x_data[i], params) for i in range(len(x_data))]

        # Simple gradient descent (placeholder - real implementation would use Levenberg-Marquardt)
        h = 1e-6
        gradient = []
        for j in range(len(params)):
            params_plus = params.copy()
            params_plus[j] += h
            residuals_plus = [y_data[i] - model(x_data[i], params_plus) for i in range(len(x_data))]
            grad_j = sum((rp - r) ** 2 for rp, r in zip(residuals_plus, residuals)) / h
            gradient.append(grad_j)

        # Update parameters
        learning_rate = 0.01
        new_params = [params[j] - learning_rate * gradient[j] for j in range(len(params))]

        # Check convergence
        if max(abs(np - p) for np, p in zip(new_params, params)) < tolerance:
            params = new_params
            break

        params = new_params

    final_residuals = [y_data[i] - model(x_data[i], params) for i in range(len(x_data))]
    return (params, final_residuals)


def approximation(
    func: Callable[[float], float],
    degree: int,
    bounds: Tuple[float, float],
    method: str = "polynomial",
) -> Callable[[float], float]:
    """Create an approximation of a function.

    Args:
        func: Function to approximate
        degree: Approximation degree
        bounds: Approximation bounds
        method: Approximation method (polynomial, chebyshev)

    Returns:
        Approximating function

    Example:
        >>> approx = approximation(lambda x: math.sin(x), degree=5, bounds=(0, math.pi))
        >>> y = approx(1.0)
    """
    if method == "polynomial":
        return _polynomial_approximation(func, degree, bounds)
    elif method == "chebyshev":
        return _chebyshev_approximation(func, degree, bounds)
    else:
        raise ValueError(f"Unknown method: {method}")


def _polynomial_approximation(
    func: Callable[[float], float],
    degree: int,
    bounds: Tuple[float, float],
) -> Callable[[float], float]:
    """Polynomial approximation using least squares.

    Args:
        func: Function to approximate
        degree: Polynomial degree
        bounds: Approximation bounds

    Returns:
        Approximating function
    """
    a, b = bounds

    # Sample points
    n_samples = degree + 10
    x_samples = [a + (b - a) * i / (n_samples - 1) for i in range(n_samples)]
    y_samples = [func(x) for x in x_samples]

    # Solve least squares (simplified - real implementation would use numpy.linalg.lstsq)
    # For now, return original function as placeholder
    return func


def _chebyshev_approximation(
    func: Callable[[float], float],
    degree: int,
    bounds: Tuple[float, float],
) -> Callable[[float], float]:
    """Chebyshev polynomial approximation.

    Args:
        func: Function to approximate
        degree: Approximation degree
        bounds: Approximation bounds

    Returns:
        Approximating function
    """
    # Placeholder - real implementation would compute Chebyshev coefficients
    return func


def error_analysis(
    exact: List[float],
    approximate: List[float],
) -> Dict[str, float]:
    """Analyze numerical errors.

    Args:
        exact: Exact values
        approximate: Approximate values

    Returns:
        Dictionary of error metrics

    Example:
        >>> errors = error_analysis(exact_values, approx_values)
    """
    if len(exact) != len(approximate):
        raise ValueError("Exact and approximate must have same length")

    n = len(exact)

    # Absolute errors
    abs_errors = [abs(e - a) for e, a in zip(exact, approximate)]

    # Relative errors
    rel_errors = [abs(e - a) / (abs(e) + 1e-10) for e, a in zip(exact, approximate)]

    # Mean absolute error
    mae = sum(abs_errors) / n

    # Root mean square error
    rmse = math.sqrt(sum(e**2 for e in abs_errors) / n)

    # Max absolute error
    max_abs_error = max(abs_errors)

    # Mean relative error
    mre = sum(rel_errors) / n

    return {
        "mae": mae,
        "rmse": rmse,
        "max_abs_error": max_abs_error,
        "mre": mre,
        "abs_errors": abs_errors,
        "rel_errors": rel_errors,
    }


__all__ = [
    "root_finding",
    "interpolation",
    "extrapolation",
    "curve_fit",
    "approximation",
    "error_analysis",
]
