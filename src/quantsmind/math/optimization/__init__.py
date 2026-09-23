"""
Optimization Module

This module provides optimization operations for the Mathematics package.
Optimization represents finding optimal solutions to mathematical problems.

Purpose
-------
Provide optimization operations for the Mathematics package.

Scientific Meaning
------------------
Optimization represents the process of finding the best solution from all feasible solutions,
essential for machine learning, operations research, engineering design, and many other scientific applications.

Responsibilities
----------------
- Support objective functions
- Enable optimization algorithms
- Support constraint handling
- Handle optimization validation

Dependencies
------------
typing (standard library)
quantsmind.math.exceptions (exception hierarchy)
quantsmind.math.types (type definitions)

Future Extensions
-----------------
- Gradient descent
- Newton's method
- Constrained optimization
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import List, Optional, Tuple, Union

from quantsmind.math.exceptions import ConvergenceError, OptimizationError
from quantsmind.math.types import Scalar, Vector

logger = logging.getLogger(__name__)


class ObjectiveFunction:
    """Concrete implementation of an objective function.

    This class represents a function to be optimized.

    Scientific Meaning
    ------------------
    In optimization, the objective function represents the function to be minimized or maximized.

    Example:
        >>> obj = ObjectiveFunction(lambda x: x[0]**2 + x[1]**2)
    """

    def __init__(self, func: Callable[[Vector], Scalar]) -> None:
        """Initialize an ObjectiveFunction.

        Args:
            func: Function to optimize

        Example:
            >>> obj = ObjectiveFunction(lambda x: x[0]**2 + x[1]**2)
        """
        self._func = func
        logger.debug("Created objective function")

    def evaluate(self, x: Vector) -> Scalar:
        """Evaluate the objective function.

        Args:
            x: Point to evaluate

        Returns:
            Function value

        Example:
            >>> value = obj.evaluate([1.0, 2.0])
        """
        return self._func(x)

    def __call__(self, x: Vector) -> Scalar:
        """Make the objective function callable.

        Args:
            x: Point to evaluate

        Returns:
            Function value

        Example:
            >>> value = obj([1.0, 2.0])
        """
        return self.evaluate(x)


class Constraint:
    """Concrete implementation of an optimization constraint.

    This class represents a constraint on the optimization problem.

    Scientific Meaning
    ------------------
    In optimization, constraints represent restrictions on the feasible region.

    Example:
        >>> constraint = Constraint(lambda x: x[0] >= 0)
    """

    def __init__(self, func: Callable[[Vector], bool]) -> None:
        """Initialize a Constraint.

        Args:
            func: Constraint function (returns True if satisfied)

        Example:
            >>> constraint = Constraint(lambda x: x[0] >= 0)
        """
        self._func = func
        logger.debug("Created constraint")

    def is_satisfied(self, x: Vector) -> bool:
        """Check if constraint is satisfied.

        Args:
            x: Point to check

        Returns:
            True if satisfied, False otherwise

        Example:
            >>> if constraint.is_satisfied([1.0, 2.0]):
            ...     print("Constraint satisfied")
        """
        return self._func(x)


class SearchSpace:
    """Concrete implementation of a search space.

    This class represents the domain over which optimization is performed.

    Scientific Meaning
    ------------------
    In optimization, the search space represents the set of all possible solutions.

    Example:
        >>> space = SearchSpace([(-10.0, 10.0), (-10.0, 10.0)])
    """

    def __init__(self, bounds: list[tuple[float, float]]) -> None:
        """Initialize a SearchSpace.

        Args:
            bounds: List of (lower, upper) bounds for each dimension

        Example:
            >>> space = SearchSpace([(-10.0, 10.0), (-10.0, 10.0)])
        """
        self._bounds = bounds
        self._dimension = len(bounds)
        logger.debug(f"Created search space with {self._dimension} dimensions")

    @property
    def bounds(self) -> list[tuple[float, float]]:
        """Get the bounds.

        Returns:
            List of bounds

        Example:
            >>> print(f"Bounds: {space.bounds}")
        """
        return self._bounds.copy()

    @property
    def dimension(self) -> int:
        """Get the dimension.

        Returns:
            Dimension

        Example:
            >>> print(f"Dimension: {space.dimension}")
        """
        return self._dimension

    def is_within_bounds(self, x: Vector) -> bool:
        """Check if a point is within bounds.

        Args:
            x: Point to check

        Returns:
            True if within bounds, False otherwise

        Example:
            >>> if space.is_within_bounds([5.0, 5.0]):
            ...     print("Within bounds")
        """
        if len(x) != self._dimension:
            return False
        for i, (lower, upper) in enumerate(self._bounds):
            if x[i] < lower or x[i] > upper:
                return False
        return True

    def random_point(self) -> Vector:
        """Generate a random point within bounds.

        Returns:
            Random point

        Example:
            >>> point = space.random_point()
        """
        import random
        return [random.uniform(lower, upper) for lower, upper in self._bounds]


class Optimizer:
    """Concrete implementation of an optimizer.

    This class provides optimization algorithms for finding optimal solutions.

    Scientific Meaning
    ------------------
    In optimization, an optimizer represents an algorithm that finds the optimal solution
    to an optimization problem.

    Example:
        >>> optimizer = Optimizer()
        >>> result = optimizer.minimize(obj, space)
    """

    def __init__(self, max_iterations: int = 1000, tolerance: float = 1e-6) -> None:
        """Initialize an Optimizer.

        Args:
            max_iterations: Maximum number of iterations
            tolerance: Convergence tolerance

        Example:
            >>> optimizer = Optimizer(max_iterations=1000, tolerance=1e-6)
        """
        self._max_iterations = max_iterations
        self._tolerance = tolerance
        logger.debug(f"Created optimizer with max_iterations={max_iterations}")

    def minimize(
        self,
        objective: ObjectiveFunction,
        search_space: SearchSpace,
        initial_point: Vector | None = None,
        constraints: list[Constraint] | None = None
    ) -> tuple[Vector, Scalar]:
        """Minimize an objective function using gradient descent.

        Args:
            objective: Objective function to minimize
            search_space: Search space
            initial_point: Optional initial point
            constraints: Optional constraints

        Returns:
            Tuple of (optimal point, optimal value)

        Raises:
            OptimizationError: If optimization fails

        Example:
            >>> optimizer = Optimizer()
            >>> result = optimizer.minimize(obj, space)
        """
        x = search_space.random_point() if initial_point is None else initial_point.copy()

        if constraints is None:
            constraints = []

        # Simplified gradient descent implementation
        learning_rate = 0.01
        for iteration in range(self._max_iterations):
            # Calculate gradient (numerical)
            gradient = self._numerical_gradient(objective, x)

            # Update point
            x_new = [x[i] - learning_rate * gradient[i] for i in range(len(x))]

            # Check constraints
            if all(c.is_satisfied(x_new) for c in constraints) and search_space.is_within_bounds(x_new):
                x = x_new

            # Check convergence
            if self._check_convergence(objective, x, x_new):
                logger.info(f"Converged at iteration {iteration}")
                break

        return (x, objective.evaluate(x))

    def _numerical_gradient(self, objective: ObjectiveFunction, x: Vector, h: float = 1e-6) -> Vector:
        """Calculate numerical gradient.

        Args:
            objective: Objective function
            x: Point
            h: Step size

        Returns:
            Gradient vector
        """
        gradient = []
        for i in range(len(x)):
            x_plus = x.copy()
            x_plus[i] += h
            x_minus = x.copy()
            x_minus[i] -= h
            partial = (objective.evaluate(x_plus) - objective.evaluate(x_minus)) / (2 * h)
            gradient.append(partial)
        return gradient

    def _check_convergence(self, objective: ObjectiveFunction, x_old: Vector, x_new: Vector) -> bool:
        """Check for convergence.

        Args:
            objective: Objective function
            x_old: Old point
            x_new: New point

        Returns:
            True if converged, False otherwise
        """
        f_old = objective.evaluate(x_old)
        f_new = objective.evaluate(x_new)
        return abs(f_new - f_old) < self._tolerance


class CostFunction(ObjectiveFunction):
    """Concrete implementation of a cost function.

    This class represents a cost function to be minimized.

    Scientific Meaning
    ------------------
    In optimization, a cost function represents the cost to be minimized,
    commonly used in machine learning and control theory.

    Example:
        >>> cost = CostFunction(lambda x: sum(x_i**2 for x_i in x))
    """

    def __init__(self, func: Callable[[Vector], Scalar]) -> None:
        """Initialize a CostFunction.

        Args:
            func: Cost function

        Example:
            >>> cost = CostFunction(lambda x: sum(x_i**2 for x_i in x))
        """
        super().__init__(func)


# Export
__all__ = [
    "ObjectiveFunction",
    "Constraint",
    "SearchSpace",
    "Optimizer",
    "CostFunction",
]

