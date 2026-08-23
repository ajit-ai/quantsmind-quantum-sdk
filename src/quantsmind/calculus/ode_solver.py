"""
ODE Solver Module

This module provides ODE solving functionality for the QuantsMind SDK.

Purpose
-------
Provide numerical methods for solving ordinary differential equations.

Classes
-------
ODESolver: ODE solving engine

Responsibilities
----------------
- Solve ODEs using Euler method
- Solve ODEs using Runge-Kutta method
- Solve ODEs using adaptive methods
- Solve systems of ODEs

Dependencies
------------
typing (standard library)
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any


class ODESolver:
    """ODE solving engine.

    This class provides functionality for solving ordinary differential equations
    using various numerical methods.

    Attributes:
        _method: Solving method (euler, runge_kutta, adaptive)
        _step_size: Step size for numerical methods
        _tolerance: Tolerance for adaptive methods
        _metadata: Additional metadata

    Example:
        >>> solver = ODESolver(method="runge_kutta", step_size=0.01)
        >>> solution = solver.solve(lambda t, y: -y, y0=1.0, t_span=(0, 1))
    """

    def __init__(
        self,
        method: str = "runge_kutta",
        step_size: float = 0.01,
        tolerance: float = 1e-6,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize an ODESolver.

        Args:
            method: Solving method (euler, runge_kutta, adaptive)
            step_size: Step size for numerical methods
            tolerance: Tolerance for adaptive methods
            metadata: Additional metadata

        Example:
            >>> solver = ODESolver(method="runge_kutta", step_size=0.01)
        """
        self._method = method
        self._step_size = step_size
        self._tolerance = tolerance
        self._metadata = metadata or {}

    @property
    def method(self) -> str:
        """Get the solving method.

        Returns:
            Solving method

        Example:
            >>> method = solver.method
        """
        return self._method

    @property
    def step_size(self) -> float:
        """Get the step size.

        Returns:
            Step size

        Example:
            >>> h = solver.step_size
        """
        return self._step_size

    def set_step_size(self, step_size: float) -> None:
        """Set the step size.

        Args:
            step_size: Step size

        Example:
            >>> solver.set_step_size(0.001)
        """
        if step_size <= 0:
            raise ValueError("Step size must be positive")
        self._step_size = step_size

    def solve(
        self,
        func: Callable[[float, float], float],
        y0: float,
        t_span: tuple[float, float],
    ) -> tuple[list[float], list[float]]:
        """Solve an ODE.

        Args:
            func: ODE function dy/dt = f(t, y)
            y0: Initial condition
            t_span: Time span (t_start, t_end)

        Returns:
            Tuple of (t_values, y_values)

        Example:
            >>> t, y = solver.solve(lambda t, y: -y, y0=1.0, t_span=(0, 1))
        """
        if self._method == "euler":
            return self._euler(func, y0, t_span)
        elif self._method == "runge_kutta":
            return self._runge_kutta(func, y0, t_span)
        elif self._method == "adaptive":
            return self._adaptive(func, y0, t_span)
        else:
            raise NotImplementedError(f"Method {self._method} not implemented")

    def _euler(
        self,
        func: Callable[[float, float], float],
        y0: float,
        t_span: tuple[float, float],
    ) -> tuple[list[float], list[float]]:
        """Euler method.

        Args:
            func: ODE function
            y0: Initial condition
            t_span: Time span

        Returns:
            Tuple of (t_values, y_values)
        """
        t_start, t_end = t_span
        t_values = [t_start]
        y_values = [y0]

        t = t_start
        y = y0

        while t < t_end:
            h = min(self._step_size, t_end - t)
            y += h * func(t, y)
            t += h

            t_values.append(t)
            y_values.append(y)

        return (t_values, y_values)

    def _runge_kutta(
        self,
        func: Callable[[float, float], float],
        y0: float,
        t_span: tuple[float, float],
    ) -> tuple[list[float], list[float]]:
        """Runge-Kutta 4th order method.

        Args:
            func: ODE function
            y0: Initial condition
            t_span: Time span

        Returns:
            Tuple of (t_values, y_values)
        """
        t_start, t_end = t_span
        t_values = [t_start]
        y_values = [y0]

        t = t_start
        y = y0

        while t < t_end:
            h = min(self._step_size, t_end - t)

            k1 = func(t, y)
            k2 = func(t + h / 2, y + h * k1 / 2)
            k3 = func(t + h / 2, y + h * k2 / 2)
            k4 = func(t + h, y + h * k3)

            y += h * (k1 + 2 * k2 + 2 * k3 + k4) / 6
            t += h

            t_values.append(t)
            y_values.append(y)

        return (t_values, y_values)

    def _adaptive(
        self,
        func: Callable[[float, float], float],
        y0: float,
        t_span: tuple[float, float],
    ) -> tuple[list[float], list[float]]:
        """Adaptive step size method.

        Args:
            func: ODE function
            y0: Initial condition
            t_span: Time span

        Returns:
            Tuple of (t_values, y_values)
        """
        t_start, t_end = t_span
        t_values = [t_start]
        y_values = [y0]

        t = t_start
        y = y0
        h = self._step_size

        while t < t_end:
            h = min(h, t_end - t)

            # Compute two steps with h
            y1 = self._rk4_step(func, t, y, h)

            # Compute one step with 2h
            y2 = self._rk4_step(func, t, y, 2 * h)

            # Estimate error
            error = abs(y1 - y2) / 15  # Error estimate for RK4

            if error < self._tolerance:
                # Accept step
                y = y1
                t += h
                t_values.append(t)
                y_values.append(y)

                # Increase step size
                h *= 1.2
            else:
                # Reject step, decrease step size
                h *= 0.5

        return (t_values, y_values)

    def _rk4_step(
        self,
        func: Callable[[float, float], float],
        t: float,
        y: float,
        h: float,
    ) -> float:
        """Single RK4 step.

        Args:
            func: ODE function
            t: Current time
            y: Current value
            h: Step size

        Returns:
            New value
        """
        k1 = func(t, y)
        k2 = func(t + h / 2, y + h * k1 / 2)
        k3 = func(t + h / 2, y + h * k2 / 2)
        k4 = func(t + h, y + h * k3)

        return y + h * (k1 + 2 * k2 + 2 * k3 + k4) / 6

    def solve_system(
        self,
        func: Callable[[float, list[float]], list[float]],
        y0: list[float],
        t_span: tuple[float, float],
    ) -> tuple[list[float], list[list[float]]]:
        """Solve a system of ODEs.

        Args:
            func: ODE system function dy/dt = f(t, y)
            y0: Initial conditions
            t_span: Time span

        Returns:
            Tuple of (t_values, y_values)

        Example:
            >>> t, y = solver.solve_system(lambda t, y: [-y[1], y[0]], [1, 0], (0, 10))
        """
        t_start, t_end = t_span
        t_values = [t_start]
        y_values = [y0.copy()]

        t = t_start
        y = y0.copy()

        while t < t_end:
            h = min(self._step_size, t_end - t)

            if self._method == "euler":
                dydt = func(t, y)
                y = [y[i] + h * dydt[i] for i in range(len(y))]
            elif self._method == "runge_kutta":
                k1 = func(t, y)
                k2 = func(t + h / 2, [y[i] + h * k1[i] / 2 for i in range(len(y))])
                k3 = func(t + h / 2, [y[i] + h * k2[i] / 2 for i in range(len(y))])
                k4 = func(t + h, [y[i] + h * k3[i] for i in range(len(y))])

                y = [
                    y[i] + h * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]) / 6
                    for i in range(len(y))
                ]
            else:
                raise NotImplementedError(f"Method {self._method} not implemented for systems")

            t += h
            t_values.append(t)
            y_values.append(y.copy())

        return (t_values, y_values)

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(solver)
        """
        return f"ODESolver(method={self._method}, step_size={self._step_size})"


__all__ = [
    "ODESolver",
]
