"""
Formula Module

This module provides the Formula class for mathematical formulas.

Purpose
-------
Provide a class for representing and manipulating mathematical formulas.

Classes
-------
Formula: Mathematical formula representation

Responsibilities
----------------
- Represent mathematical formulas
- Support formula operations
- Support formula evaluation
- Support formula validation

Dependencies
------------
typing (standard library)
quantsmind.core.math_object (MathObject)
quantsmind.core.expression (Expression)
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from quantsmind.core.expression import Expression
from quantsmind.core.math_object import MathObject


class Formula(MathObject):
    """Mathematical formula representation.

    This class provides functionality for representing and manipulating
    mathematical formulas, which are named expressions with specific semantics.

    Attributes:
        _name: Formula name
        _expression: Underlying expression
        _description: Formula description
        _parameters: Formula parameters
        _metadata: Additional metadata

    Example:
        >>> expr = Expression("area", ["pi", "r", "r"], ["*", "*"])
        >>> formula = Formula("circle_area", expr, "Area of a circle")
        >>> result = formula.evaluate(r=5, pi=3.14159)
    """

    def __init__(
        self,
        name: str,
        expression: Expression,
        description: str = "",
        parameters: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a Formula.

        Args:
            name: Formula name
            expression: Underlying expression
            description: Formula description
            parameters: Formula parameters with default values
            metadata: Additional metadata

        Example:
            >>> formula = Formula("circle_area", expr, "Area of a circle")
        """
        super().__init__(name, metadata)
        self._expression = expression
        self._description = description
        self._parameters = parameters or {}

    @property
    def expression(self) -> Expression:
        """Get the underlying expression.

        Returns:
            Expression

        Example:
            >>> expr = formula.expression
        """
        return self._expression

    @property
    def description(self) -> str:
        """Get the formula description.

        Returns:
            Description

        Example:
            >>> desc = formula.description
        """
        return self._description

    @property
    def parameters(self) -> Dict[str, Any]:
        """Get the formula parameters.

        Returns:
            Parameters dictionary

        Example:
            >>> params = formula.parameters
        """
        return self._parameters.copy()

    def evaluate(self, **kwargs: Any) -> float:
        """Evaluate the formula with given variable values.

        Args:
            **kwargs: Variable assignments

        Returns:
            Evaluated result

        Example:
            >>> result = formula.evaluate(r=5, pi=3.14159)
        """
        # Merge default parameters with provided values
        context = self._parameters.copy()
        context.update(kwargs)
        return self._expression.evaluate(**context)

    def set_expression(self, expression: Expression) -> None:
        """Set the underlying expression.

        Args:
            expression: New expression

        Example:
            >>> formula.set_expression(new_expr)
        """
        self._expression = expression

    def set_parameter(self, name: str, value: Any) -> None:
        """Set a parameter value.

        Args:
            name: Parameter name
            value: Parameter value

        Example:
            >>> formula.set_parameter("pi", 3.14159)
        """
        self._parameters[name] = value

    def validate(self) -> tuple[bool, list[str]]:
        """Validate the formula.

        Returns:
            Tuple of (is_valid, error_messages)

        Example:
            >>> is_valid, errors = formula.validate()
        """
        errors = []

        # Validate base object
        is_valid, base_errors = super().validate()
        errors.extend(base_errors)

        # Validate expression
        if self._expression is None:
            errors.append("Expression cannot be None")
        else:
            is_valid, expr_errors = self._expression.validate()
            errors.extend(expr_errors)

        return (len(errors) == 0, errors)

    def serialize(self) -> Dict[str, Any]:
        """Serialize the formula.

        Returns:
            Serialized representation

        Example:
            >>> data = formula.serialize()
        """
        data = super().serialize()
        data["expression"] = self._expression.serialize()
        data["description"] = self._description
        data["parameters"] = self._parameters
        return data

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(formula)
        """
        return f"Formula(name={self._name}, description={self._description})"


__all__ = [
    "Formula",
]
