"""
Gradient Optimizer Module

This module provides gradient-based optimization algorithms for the QuantsMind SDK.

Purpose
-------
Provide gradient descent and related optimization algorithms.

Classes
-------
GradientOptimizer: Base gradient optimizer
GradientDescent: Gradient descent algorithm
AdamOptimizer: Adam optimization algorithm
NewtonMethod: Newton's method optimizer

Responsibilities
----------------
- Optimize functions using gradient information
- Support various gradient-based algorithms
- Track optimization progress
- Check convergence

Dependencies
------------
typing (standard library)
quantsmind.core.math_object (MathObject)
"""

from __future__ import annotations

import math
from collections.abc import Callable
from typing import Any


class GradientOptimizer:
    """Base gradient optimizer.

    This class provides the base functionality for gradient-based optimization.

    Attributes:
        _name: Optimizer name
        _learning_rate: Learning rate
        _max_iterations: Maximum iterations
        _tolerance: Convergence tolerance
        _metadata: Additional metadata

    Example:
        >>> optimizer = GradientOptimizer("gd", learning_rate=0.01)
        >>> result = optimizer.optimize(lambda x: x**2, initial_x=1.0)
    """

    def __init__(
        self,
        name: str,
        learning_rate: float = 0.01,
        max_iterations: int = 1000,
        tolerance: float = 1e-6,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a GradientOptimizer.

        Args:
            name: Optimizer name
            learning_rate: Learning rate
            max_iterations: Maximum iterations
            tolerance: Convergence tolerance
            metadata: Additional metadata

        Example:
            >>> optimizer = GradientOptimizer("gd", learning_rate=0.01)
        """
        self._name = name
        self._learning_rate = learning_rate
        self._max_iterations = max_iterations
        self._tolerance = tolerance
        self._metadata = metadata or {}

    @property
    def name(self) -> str:
        """Get the optimizer name.

        Returns:
            Optimizer name

        Example:
            >>> name = optimizer.name
        """
        return self._name

    @property
    def learning_rate(self) -> float:
        """Get the learning rate.

        Returns:
            Learning rate

        Example:
            >>> lr = optimizer.learning_rate
        """
        return self._learning_rate

    def set_learning_rate(self, learning_rate: float) -> None:
        """Set the learning rate.

        Args:
            learning_rate: Learning rate

        Example:
            >>> optimizer.set_learning_rate(0.001)
        """
        if learning_rate <= 0:
            raise ValueError("Learning rate must be positive")
        self._learning_rate = learning_rate

    def optimize(
        self,
        func: Callable[[float], float],
        gradient: Callable[[float], float],
        initial_x: float,
    ) -> tuple[float, list[float]]:
        """Optimize a function.

        Args:
            func: Objective function
            gradient: Gradient function
            initial_x: Initial point

        Returns:
            Tuple of (optimal_x, history)

        Example:
            >>> result, history = optimizer.optimize(lambda x: x**2, lambda x: 2*x, 1.0)
        """
        raise NotImplementedError("Subclasses must implement optimize")

    def convergence_check(self, x_new: float, x_old: float) -> bool:
        """Check convergence.

        Args:
            x_new: New value
            x_old: Old value

        Returns:
            True if converged

        Example:
            >>> converged = optimizer.convergence_check(x_new, x_old)
        """
        return abs(x_new - x_old) < self._tolerance

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(optimizer)
        """
        return f"GradientOptimizer(name={self._name}, lr={self._learning_rate})"


class GradientDescent(GradientOptimizer):
    """Gradient descent optimizer.

    This class implements the gradient descent optimization algorithm.

    Example:
        >>> optimizer = GradientDescent(learning_rate=0.01)
        >>> result, history = optimizer.optimize(lambda x: x**2, lambda x: 2*x, 1.0)
    """

    def __init__(
        self,
        learning_rate: float = 0.01,
        max_iterations: int = 1000,
        tolerance: float = 1e-6,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a GradientDescent optimizer.

        Args:
            learning_rate: Learning rate
            max_iterations: Maximum iterations
            tolerance: Convergence tolerance
            metadata: Additional metadata

        Example:
            >>> optimizer = GradientDescent(learning_rate=0.01)
        """
        super().__init__("gradient_descent", learning_rate, max_iterations, tolerance, metadata)

    def optimize(
        self,
        func: Callable[[float], float],
        gradient: Callable[[float], float],
        initial_x: float,
    ) -> tuple[float, list[float]]:
        """Optimize using gradient descent.

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

        for _ in range(self._max_iterations):
            grad = gradient(x)
            x_new = x - self._learning_rate * grad

            history.append(x_new)

            if self.convergence_check(x_new, x):
                break

            x = x_new

        return (x, history)


class AdamOptimizer(GradientOptimizer):
    """Adam optimizer.

    This class implements the Adam optimization algorithm with adaptive learning rates.

    Attributes:
        _beta1: Exponential decay rate for first moment
        _beta2: Exponential decay rate for second moment
        _epsilon: Small constant for numerical stability

    Example:
        >>> optimizer = AdamOptimizer(learning_rate=0.001)
        >>> result, history = optimizer.optimize(lambda x: x**2, lambda x: 2*x, 1.0)
    """

    def __init__(
        self,
        learning_rate: float = 0.001,
        beta1: float = 0.9,
        beta2: float = 0.999,
        epsilon: float = 1e-8,
        max_iterations: int = 1000,
        tolerance: float = 1e-6,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize an AdamOptimizer.

        Args:
            learning_rate: Learning rate
            beta1: Exponential decay rate for first moment
            beta2: Exponential decay rate for second moment
            epsilon: Small constant for numerical stability
            max_iterations: Maximum iterations
            tolerance: Convergence tolerance
            metadata: Additional metadata

        Example:
            >>> optimizer = AdamOptimizer(learning_rate=0.001)
        """
        super().__init__("adam", learning_rate, max_iterations, tolerance, metadata)
        self._beta1 = beta1
        self._beta2 = beta2
        self._epsilon = epsilon

    def optimize(
        self,
        func: Callable[[float], float],
        gradient: Callable[[float], float],
        initial_x: float,
    ) -> tuple[float, list[float]]:
        """Optimize using Adam.

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

        m = 0.0  # First moment
        v = 0.0  # Second moment

        for t in range(1, self._max_iterations + 1):
            grad = gradient(x)

            m = self._beta1 * m + (1 - self._beta1) * grad
            v = self._beta2 * v + (1 - self._beta2) * (grad ** 2)

            m_hat = m / (1 - self._beta1 ** t)
            v_hat = v / (1 - self._beta2 ** t)

            x_new = x - self._learning_rate * m_hat / (math.sqrt(v_hat) + self._epsilon)

            history.append(x_new)

            if self.convergence_check(x_new, x):
                break

            x = x_new

        return (x, history)


class NewtonMethod(GradientOptimizer):
    """Newton's method optimizer.

    This class implements Newton's method for optimization using second-order information.

    Attributes:
        _hessian: Hessian function

    Example:
        >>> optimizer = NewtonMethod(learning_rate=1.0)
        >>> result, history = optimizer.optimize(lambda x: x**2, lambda x: 2*x, lambda x: 2, 1.0)
    """

    def __init__(
        self,
        learning_rate: float = 1.0,
        max_iterations: int = 1000,
        tolerance: float = 1e-6,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a NewtonMethod optimizer.

        Args:
            learning_rate: Learning rate (typically 1.0 for Newton's method)
            max_iterations: Maximum iterations
            tolerance: Convergence tolerance
            metadata: Additional metadata

        Example:
            >>> optimizer = NewtonMethod(learning_rate=1.0)
        """
        super().__init__("newton", learning_rate, max_iterations, tolerance, metadata)

    def optimize(
        self,
        func: Callable[[float], float],
        gradient: Callable[[float], float],
        initial_x: float,
        hessian: Callable[[float], float] | None = None,
    ) -> tuple[float, list[float]]:
        """Optimize using Newton's method.

        Args:
            func: Objective function
            gradient: Gradient function
            initial_x: Initial point
            hessian: Hessian function (optional, will use finite differences if not provided)

        Returns:
            Tuple of (optimal_x, history)

        Example:
            >>> result, history = optimizer.optimize(lambda x: x**2, lambda x: 2*x, lambda x: 2, 1.0)
        """
        x = initial_x
        history = [x]

        for _ in range(self._max_iterations):
            grad = gradient(x)

            if hessian is not None:
                hess = hessian(x)
            else:
                # Finite difference approximation
                h = 1e-6
                hess = (gradient(x + h) - gradient(x - h)) / (2 * h)

            if abs(hess) < 1e-10:
                break

            x_new = x - self._learning_rate * grad / hess

            history.append(x_new)

            if self.convergence_check(x_new, x):
                break

            x = x_new

        return (x, history)


__all__ = [
    "GradientOptimizer",
    "GradientDescent",
    "AdamOptimizer",
    "NewtonMethod",
]
