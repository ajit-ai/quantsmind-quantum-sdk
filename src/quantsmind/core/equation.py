"""
Equation Module

This module provides the Equation class for mathematical equations.

Purpose
-------
Provide a class for representing and solving mathematical equations.

Classes
-------
Equation: Mathematical equation representation

Responsibilities
----------------
- Represent mathematical equations
- Support equation solving
- Support equation validation
- Support equation manipulation

Dependencies
------------
typing (standard library)
quantsmind.core.math_object (MathObject)
quantsmind.core.expression (Expression)
"""

from __future__ import annotations

from typing import Any

from quantsmind.core.expression import Expression
from quantsmind.core.math_object import MathObject


class Equation(MathObject):
    """Mathematical equation representation.

    This class provides functionality for representing and manipulating
    mathematical equations of the form left_hand = right_hand.

    Attributes:
        _name: Equation name
        _left_hand: Left-hand side expression
        _right_hand: Right-hand side expression
        _solutions: Known solutions
        _metadata: Additional metadata

    Example:
        >>> lhs = Expression("lhs", ["x", "2"], ["+", "*"])
        >>> rhs = Expression("rhs", ["8"], [])
        >>> eq = Equation("linear_eq", lhs, rhs)
        >>> solutions = eq.solve()
    """

    def __init__(
        self,
        name: str,
        left_hand: Expression,
        right_hand: Expression,
        solutions: list[float] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize an Equation.

        Args:
            name: Equation name
            left_hand: Left-hand side expression
            right_hand: Right-hand side expression
            solutions: Known solutions (if pre-computed)
            metadata: Additional metadata

        Example:
            >>> eq = Equation("linear_eq", lhs, rhs)
        """
        super().__init__(name, metadata)
        self._left_hand = left_hand
        self._right_hand = right_hand
        self._solutions = solutions or []

    @property
    def left_hand(self) -> Expression:
        """Get the left-hand side expression.

        Returns:
            Left-hand expression

        Example:
            >>> lhs = eq.left_hand
        """
        return self._left_hand

    @property
    def right_hand(self) -> Expression:
        """Get the right-hand side expression.

        Returns:
            Right-hand expression

        Example:
            >>> rhs = eq.right_hand
        """
        return self._right_hand

    @property
    def solutions(self) -> list[float]:
        """Get the known solutions.

        Returns:
            List of solutions

        Example:
            >>> sols = eq.solutions
        """
        return self._solutions.copy()

    def evaluate(self, **kwargs: Any) -> tuple[float, float]:
        """Evaluate both sides of the equation.

        Args:
            **kwargs: Variable assignments

        Returns:
            Tuple of (left_value, right_value)

        Example:
            >>> lhs_val, rhs_val = eq.evaluate(x=3)
        """
        left_value = self._left_hand.evaluate(**kwargs)
        right_value = self._right_hand.evaluate(**kwargs)
        return (left_value, right_value)

    def check_solution(self, **kwargs: Any) -> bool:
        """Check if given values satisfy the equation.

        Args:
            **kwargs: Variable assignments

        Returns:
            True if equation is satisfied

        Example:
            >>> is_valid = eq.check_solution(x=3)
        """
        left_value, right_value = self.evaluate(**kwargs)
        return abs(left_value - right_value) < 1e-9

    def solve(self, variable: str, **kwargs: Any) -> list[float]:
        """Solve the equation for a variable.

        Args:
            variable: Variable to solve for
            **kwargs: Known variable values

        Returns:
            List of solutions

        Example:
            >>> solutions = eq.solve("x")
        """
        # Placeholder - actual solving requires symbolic/numerical methods
        # For now, return pre-computed solutions if available
        if self._solutions:
            return self._solutions.copy()

        # Simple numerical approach for linear equations
        if variable in self._left_hand.variables or variable in self._right_hand.variables:
            # This is a placeholder - real implementation would use root finding
            return [0.0]

        return []

    def add_solution(self, solution: float) -> None:
        """Add a solution to the equation.

        Args:
            solution: Solution value

        Example:
            >>> eq.add_solution(3.0)
        """
        self._solutions.append(solution)

    def validate(self) -> tuple[bool, list[str]]:
        """Validate the equation.

        Returns:
            Tuple of (is_valid, error_messages)

        Example:
            >>> is_valid, errors = eq.validate()
        """
        errors = []

        # Validate base object
        is_valid, base_errors = super().validate()
        errors.extend(base_errors)

        # Validate expressions
        if self._left_hand is None:
            errors.append("Left-hand side cannot be None")
        else:
            is_valid, lhs_errors = self._left_hand.validate()
            errors.extend(lhs_errors)

        if self._right_hand is None:
            errors.append("Right-hand side cannot be None")
        else:
            is_valid, rhs_errors = self._right_hand.validate()
            errors.extend(rhs_errors)

        return (len(errors) == 0, errors)

    def serialize(self) -> dict[str, Any]:
        """Serialize the equation.

        Returns:
            Serialized representation

        Example:
            >>> data = eq.serialize()
        """
        data = super().serialize()
        data["left_hand"] = self._left_hand.serialize()
        data["right_hand"] = self._right_hand.serialize()
        data["solutions"] = self._solutions
        return data

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(eq)
        """
        return f"Equation(name={self._name}, solutions={len(self._solutions)})"


__all__ = [
    "Equation",
]
