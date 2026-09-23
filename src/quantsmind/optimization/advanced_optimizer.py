"""
Advanced Optimizer Module

This module provides advanced optimization algorithms for the QuantsMind SDK.

Purpose
-------
Provide LBFGS, Bayesian optimization, and simulated annealing algorithms.

Classes
-------
LBFGSOptimizer: Limited-memory BFGS optimizer
BayesianOptimizer: Bayesian optimization
SimulatedAnnealing: Simulated annealing optimizer

Responsibilities
----------------
- Optimize functions using advanced methods
- Support quasi-Newton methods
- Support probabilistic optimization
- Support global optimization

Dependencies
------------
typing (standard library)
quantsmind.core.math_object (MathObject)
"""

from __future__ import annotations

import math
import random
from collections.abc import Callable
from typing import Any


class LBFGSOptimizer:
    """Limited-memory BFGS optimizer.

    This class implements the L-BFGS quasi-Newton optimization algorithm.

    Attributes:
        _memory_size: Number of corrections to store
        _max_iterations: Maximum iterations
        _tolerance: Convergence tolerance
        _metadata: Additional metadata

    Example:
        >>> optimizer = LBFGSOptimizer(memory_size=10)
        >>> result, history = optimizer.optimize(lambda x: x**2, lambda x: 2*x, 1.0)
    """

    def __init__(
        self,
        memory_size: int = 10,
        max_iterations: int = 1000,
        tolerance: float = 1e-6,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize an LBFGSOptimizer.

        Args:
            memory_size: Number of corrections to store
            max_iterations: Maximum iterations
            tolerance: Convergence tolerance
            metadata: Additional metadata

        Example:
            >>> optimizer = LBFGSOptimizer(memory_size=10)
        """
        self._memory_size = memory_size
        self._max_iterations = max_iterations
        self._tolerance = tolerance
        self._metadata = metadata or {}

    @property
    def memory_size(self) -> int:
        """Get the memory size.

        Returns:
            Memory size

        Example:
            >>> size = optimizer.memory_size
        """
        return self._memory_size

    def optimize(
        self,
        func: Callable[[float], float],
        gradient: Callable[[float], float],
        initial_x: float,
    ) -> tuple[float, list[float]]:
        """Optimize using L-BFGS.

        Args:
            func: Objective function
            gradient: Gradient function
            initial_x: Initial point

        Returns:
            Tuple of (optimal_x, history)

        Example:
            >>> result, history = optimizer.optimize(lambda x: x**2, lambda x: 2*x, 1.0)
        """
        x = initial_x
        history = [x]

        # L-BFGS state
        s_history: list[float] = []  # Position differences
        y_history: list[float] = []  # Gradient differences
        rho_history: list[float] = []  # 1 / (y^T s)

        grad = gradient(x)
        old_grad = grad
        old_x = x

        for _ in range(self._max_iterations):
            # Compute search direction using L-BFGS two-loop recursion
            q = grad
            alpha: list[float] = []

            # First loop
            for i in reversed(range(len(s_history))):
                alpha_i = rho_history[i] * s_history[i] * q
                alpha.append(alpha_i)
                q = q - alpha_i * y_history[i]

            # Scale
            if len(s_history) > 0:
                gamma = (s_history[-1] * y_history[-1]) / (y_history[-1] ** 2 + 1e-10)
                q = gamma * q
            else:
                q = q  # Initial step

            # Second loop
            for i in range(len(s_history)):
                beta = rho_history[i] * y_history[i] * q
                q = q + s_history[i] * (alpha[len(s_history) - 1 - i] - beta)

            # Line search (simplified - use fixed step size)
            step_size = 0.01
            x_new = x - step_size * q

            # Update history
            s = x_new - old_x
            new_grad = gradient(x_new)
            y = new_grad - old_grad

            rho = 1.0 / (y * s + 1e-10)

            s_history.append(s)
            y_history.append(y)
            rho_history.append(rho)

            # Maintain memory size
            if len(s_history) > self._memory_size:
                s_history.pop(0)
                y_history.pop(0)
                rho_history.pop(0)

            history.append(x_new)

            # Check convergence
            if abs(x_new - x) < self._tolerance:
                break

            x = x_new
            old_x = x
            old_grad = new_grad
            grad = new_grad

        return (x, history)

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(optimizer)
        """
        return f"LBFGSOptimizer(memory_size={self._memory_size})"


class BayesianOptimizer:
    """Bayesian optimization.

    This class implements Bayesian optimization for global optimization.

    Attributes:
        _n_init: Number of initial random samples
        _n_iter: Number of optimization iterations
        _acquisition: Acquisition function type

    Example:
        >>> optimizer = BayesianOptimizer(n_init=10, n_iter=50)
        >>> result, history = optimizer.optimize(lambda x: x**2, (-10, 10))
    """

    def __init__(
        self,
        n_init: int = 10,
        n_iter: int = 50,
        acquisition: str = "expected_improvement",
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a BayesianOptimizer.

        Args:
            n_init: Number of initial random samples
            n_iter: Number of optimization iterations
            acquisition: Acquisition function type
            metadata: Additional metadata

        Example:
            >>> optimizer = BayesianOptimizer(n_init=10, n_iter=50)
        """
        self._n_init = n_init
        self._n_iter = n_iter
        self._acquisition = acquisition
        self._metadata = metadata or {}

    @property
    def n_init(self) -> int:
        """Get the number of initial samples.

        Returns:
            Number of initial samples

        Example:
            >>> n = optimizer.n_init
        """
        return self._n_init

    def optimize(
        self,
        func: Callable[[float], float],
        bounds: tuple[float, float],
    ) -> tuple[float, list[float]]:
        """Optimize using Bayesian optimization.

        Args:
            func: Objective function
            bounds: Search bounds (lower, upper)

        Returns:
            Tuple of (optimal_x, history)

        Example:
            >>> result, history = optimizer.optimize(lambda x: x**2, (-10, 10))
        """
        lower, upper = bounds

        # Initial random sampling
        samples = [random.uniform(lower, upper) for _ in range(self._n_init)]
        y = [func(x) for x in samples]

        history = [samples[y.index(min(y))]]

        for _ in range(self._n_iter):
            # Find best current point
            best_idx = y.index(min(y))
            best_x = samples[best_idx]

            # Simple acquisition: sample around best point
            # Real implementation would use Gaussian Process and proper acquisition
            sigma = (upper - lower) * 0.1
            candidate_x = random.gauss(best_x, sigma)
            candidate_x = max(lower, min(upper, candidate_x))

            candidate_y = func(candidate_x)

            # Add to dataset
            samples.append(candidate_x)
            y.append(candidate_y)

            # Track best
            best_idx = y.index(min(y))
            best_x = samples[best_idx]
            history.append(best_x)

        best_idx = y.index(min(y))
        return (samples[best_idx], history)

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(optimizer)
        """
        return f"BayesianOptimizer(n_init={self._n_init}, n_iter={self._n_iter})"


class SimulatedAnnealing:
    """Simulated annealing optimizer.

    This class implements simulated annealing for global optimization.

    Attributes:
        _initial_temp: Initial temperature
        _cooling_rate: Cooling rate
        _min_temp: Minimum temperature

    Example:
        >>> optimizer = SimulatedAnnealing(initial_temp=1000, cooling_rate=0.95)
        >>> result, history = optimizer.optimize(lambda x: x**2, (-10, 10))
    """

    def __init__(
        self,
        initial_temp: float = 1000.0,
        cooling_rate: float = 0.95,
        min_temp: float = 1e-6,
        max_iterations: int = 10000,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a SimulatedAnnealing optimizer.

        Args:
            initial_temp: Initial temperature
            cooling_rate: Cooling rate (0 < rate < 1)
            min_temp: Minimum temperature
            max_iterations: Maximum iterations
            metadata: Additional metadata

        Example:
            >>> optimizer = SimulatedAnnealing(initial_temp=1000, cooling_rate=0.95)
        """
        self._initial_temp = initial_temp
        self._cooling_rate = cooling_rate
        self._min_temp = min_temp
        self._max_iterations = max_iterations
        self._metadata = metadata or {}

    @property
    def initial_temp(self) -> float:
        """Get the initial temperature.

        Returns:
            Initial temperature

        Example:
            >>> temp = optimizer.initial_temp
        """
        return self._initial_temp

    def optimize(
        self,
        func: Callable[[float], float],
        bounds: tuple[float, float],
    ) -> tuple[float, list[float]]:
        """Optimize using simulated annealing.

        Args:
            func: Objective function
            bounds: Search bounds (lower, upper)

        Returns:
            Tuple of (optimal_x, history)

        Example:
            >>> result, history = optimizer.optimize(lambda x: x**2, (-10, 10))
        """
        lower, upper = bounds

        # Initial solution
        current_x = random.uniform(lower, upper)
        current_value = func(current_x)

        best_x = current_x
        best_value = current_value

        temp = self._initial_temp
        history = [best_x]

        for _ in range(self._max_iterations):
            if temp < self._min_temp:
                break

            # Generate neighbor
            step_size = (upper - lower) * 0.1 * (temp / self._initial_temp)
            neighbor_x = current_x + random.uniform(-step_size, step_size)
            neighbor_x = max(lower, min(upper, neighbor_x))
            neighbor_value = func(neighbor_x)

            # Accept or reject
            delta = neighbor_value - current_value
            if delta < 0 or random.random() < math.exp(-delta / temp):
                current_x = neighbor_x
                current_value = neighbor_value

                # Update best
                if current_value < best_value:
                    best_x = current_x
                    best_value = current_value

            history.append(best_x)

            # Cool down
            temp *= self._cooling_rate

        return (best_x, history)

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(optimizer)
        """
        return f"SimulatedAnnealing(initial_temp={self._initial_temp}, cooling_rate={self._cooling_rate})"


__all__ = [
    "LBFGSOptimizer",
    "BayesianOptimizer",
    "SimulatedAnnealing",
]
