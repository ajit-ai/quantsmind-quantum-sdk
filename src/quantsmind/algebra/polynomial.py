"""
Polynomial Module

This module provides polynomial classes for the QuantsMind SDK.

Purpose
-------
Provide polynomial representation and manipulation functionality.

Classes
-------
Polynomial: Polynomial representation
PolynomialSolver: Polynomial equation solver

Responsibilities
----------------
- Represent polynomials
- Evaluate polynomials
- Find polynomial degree
- Find polynomial roots
- Factor polynomials
- Expand polynomials
- Differentiate polynomials
- Integrate polynomials

Dependencies
------------
typing (standard library)
quantsmind.core.math_object (MathObject)
"""

from __future__ import annotations

import math
from typing import Any

from quantsmind.core.math_object import MathObject


class Polynomial(MathObject):
    """Polynomial representation.

    This class provides functionality for representing and manipulating
    polynomials of the form: a_n*x^n + a_{n-1}*x^{n-1} + ... + a_1*x + a_0

    Attributes:
        _name: Polynomial name
        _coefficients: Coefficients [a_0, a_1, ..., a_n]
        _variable: Variable name (default 'x')
        _metadata: Additional metadata

    Example:
        >>> poly = Polynomial("quadratic", [1, 0, -2])  # x^2 - 2
        >>> result = poly.evaluate(3)  # 9 - 2 = 7
    """

    def __init__(
        self,
        name: str,
        coefficients: list[float],
        variable: str = "x",
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a Polynomial.

        Args:
            name: Polynomial name
            coefficients: Coefficients [a_0, a_1, ..., a_n] where a_i is coefficient of x^i
            variable: Variable name
            metadata: Additional metadata

        Example:
            >>> poly = Polynomial("quadratic", [1, 0, -2])  # x^2 - 2
        """
        super().__init__(name, metadata)
        self._coefficients = coefficients
        self._variable = variable

    @property
    def coefficients(self) -> list[float]:
        """Get the coefficients.

        Returns:
            List of coefficients

        Example:
            >>> coeffs = poly.coefficients
        """
        return self._coefficients.copy()

    @property
    def variable(self) -> str:
        """Get the variable name.

        Returns:
            Variable name

        Example:
            >>> var = poly.variable
        """
        return self._variable

    def degree(self) -> int:
        """Get the degree of the polynomial.

        Returns:
            Polynomial degree

        Example:
            >>> deg = poly.degree()
        """
        # Remove trailing zeros
        coeffs = self._coefficients.copy()
        while len(coeffs) > 1 and abs(coeffs[-1]) < 1e-10:
            coeffs.pop()
        return len(coeffs) - 1

    def evaluate(self, x: float) -> float:
        """Evaluate the polynomial at a point.

        Args:
            x: Value to evaluate at

        Returns:
            Evaluated value

        Example:
            >>> result = poly.evaluate(3)
        """
        result = 0.0
        for i, coeff in enumerate(self._coefficients):
            result += coeff * (x ** i)
        return result

    def derivative(self) -> Polynomial:
        """Compute the derivative of the polynomial.

        Returns:
            Derivative polynomial

        Example:
            >>> deriv = poly.derivative()
        """
        if len(self._coefficients) <= 1:
            return Polynomial(f"{self._name}_deriv", [0.0], self._variable)

        deriv_coeffs = [i * self._coefficients[i] for i in range(1, len(self._coefficients))]
        return Polynomial(f"{self._name}_deriv", deriv_coeffs, self._variable)

    def integral(self, constant: float = 0.0) -> Polynomial:
        """Compute the integral of the polynomial.

        Args:
            constant: Integration constant

        Returns:
            Integral polynomial

        Example:
            >>> integral = poly.integral(constant=1.0)
        """
        integral_coeffs = [constant] + [self._coefficients[i] / (i + 1) for i in range(len(self._coefficients))]
        return Polynomial(f"{self._name}_integral", integral_coeffs, self._variable)

    def add(self, other: Polynomial) -> Polynomial:
        """Add another polynomial.

        Args:
            other: Polynomial to add

        Returns:
            Sum polynomial

        Example:
            >>> result = poly.add(other)
        """
        max_len = max(len(self._coefficients), len(other.coefficients))
        result_coeffs = []
        for i in range(max_len):
            coeff = self._coefficients[i] if i < len(self._coefficients) else 0.0
            coeff += other.coefficients[i] if i < len(other.coefficients) else 0.0
            result_coeffs.append(coeff)
        return Polynomial(f"{self._name}_plus_{other._name}", result_coeffs, self._variable)

    def subtract(self, other: Polynomial) -> Polynomial:
        """Subtract another polynomial.

        Args:
            other: Polynomial to subtract

        Returns:
            Difference polynomial

        Example:
            >>> result = poly.subtract(other)
        """
        max_len = max(len(self._coefficients), len(other.coefficients))
        result_coeffs = []
        for i in range(max_len):
            coeff = self._coefficients[i] if i < len(self._coefficients) else 0.0
            coeff -= other.coefficients[i] if i < len(other.coefficients) else 0.0
            result_coeffs.append(coeff)
        return Polynomial(f"{self._name}_minus_{other._name}", result_coeffs, self._variable)

    def multiply(self, other: Polynomial) -> Polynomial:
        """Multiply by another polynomial.

        Args:
            other: Polynomial to multiply by

        Returns:
            Product polynomial

        Example:
            >>> result = poly.multiply(other)
        """
        result_len = len(self._coefficients) + len(other.coefficients) - 1
        result_coeffs = [0.0] * result_len
        for i, coeff1 in enumerate(self._coefficients):
            for j, coeff2 in enumerate(other.coefficients):
                result_coeffs[i + j] += coeff1 * coeff2
        return Polynomial(f"{self._name}_times_{other._name}", result_coeffs, self._variable)

    def scale(self, factor: float) -> Polynomial:
        """Scale the polynomial by a factor.

        Args:
            factor: Scaling factor

        Returns:
            Scaled polynomial

        Example:
            >>> result = poly.scale(2.0)
        """
        scaled_coeffs = [coeff * factor for coeff in self._coefficients]
        return Polynomial(f"{self._name}_scaled", scaled_coeffs, self._variable)

    def roots(self) -> list[complex]:
        """Find the roots of the polynomial.

        Returns:
            List of complex roots

        Example:
            >>> roots = poly.roots()
        """
        deg = self.degree()
        if deg == 0:
            return []
        elif deg == 1:
            # Linear: ax + b = 0 => x = -b/a
            a, b = self._coefficients[1], self._coefficients[0]
            return [-b / a] if a != 0 else []
        elif deg == 2:
            # Quadratic: ax^2 + bx + c = 0
            a, b, c = self._coefficients[2], self._coefficients[1], self._coefficients[0]
            if a == 0:
                return []
            discriminant = b**2 - 4*a*c
            if discriminant >= 0:
                sqrt_d = math.sqrt(discriminant)
                return [(-b + sqrt_d) / (2*a), (-b - sqrt_d) / (2*a)]
            else:
                sqrt_d = math.sqrt(-discriminant)
                return [complex(-b, sqrt_d) / (2*a), complex(-b, -sqrt_d) / (2*a)]
        else:
            # For higher degrees, use numerical methods (placeholder)
            # Real implementation would use numpy's roots or similar
            return []

    def factor(self) -> list[Polynomial]:
        """Factor the polynomial.

        Returns:
            List of factor polynomials

        Example:
            >>> factors = poly.factor()
        """
        # Placeholder - actual factoring requires symbolic computation
        return [self.clone()]

    def expand(self) -> Polynomial:
        """Expand the polynomial (already in expanded form).

        Returns:
            Expanded polynomial

        Example:
            >>> expanded = poly.expand()
        """
        return self.clone()

    def validate(self) -> tuple[bool, list[str]]:
        """Validate the polynomial.

        Returns:
            Tuple of (is_valid, error_messages)

        Example:
            >>> is_valid, errors = poly.validate()
        """
        errors = []

        # Validate base object
        is_valid, base_errors = super().validate()
        errors.extend(base_errors)

        if not self._coefficients:
            errors.append("Coefficients cannot be empty")

        return (len(errors) == 0, errors)

    def serialize(self) -> dict[str, Any]:
        """Serialize the polynomial.

        Returns:
            Serialized representation

        Example:
            >>> data = poly.serialize()
        """
        data = super().serialize()
        data["coefficients"] = self._coefficients
        data["variable"] = self._variable
        data["degree"] = self.degree()
        return data

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(poly)
        """
        return f"Polynomial(name={self._name}, degree={self.degree()})"


class PolynomialSolver:
    """Polynomial equation solver.

    This class provides functionality for solving polynomial equations.

    Attributes:
        _polynomial: Polynomial to solve
        _tolerance: Solution tolerance
        _max_iterations: Maximum iterations for numerical methods

    Example:
        >>> poly = Polynomial("quadratic", [1, 0, -2])
        >>> solver = PolynomialSolver(poly)
        >>> roots = solver.solve()
    """

    def __init__(
        self,
        polynomial: Polynomial,
        tolerance: float = 1e-10,
        max_iterations: int = 1000,
    ) -> None:
        """Initialize a PolynomialSolver.

        Args:
            polynomial: Polynomial to solve
            tolerance: Solution tolerance
            max_iterations: Maximum iterations

        Example:
            >>> solver = PolynomialSolver(poly)
        """
        self._polynomial = polynomial
        self._tolerance = tolerance
        self._max_iterations = max_iterations

    @property
    def polynomial(self) -> Polynomial:
        """Get the polynomial.

        Returns:
            Polynomial

        Example:
            >>> poly = solver.polynomial
        """
        return self._polynomial

    def solve(self) -> list[complex]:
        """Solve the polynomial equation.

        Returns:
            List of roots

        Example:
            >>> roots = solver.solve()
        """
        return self._polynomial.roots()

    def solve_newton(self, initial_guess: float) -> complex:
        """Solve using Newton's method.

        Args:
            initial_guess: Initial guess for the root

        Returns:
            Root

        Example:
            >>> root = solver.solve_newton(1.0)
        """
        x = initial_guess
        deriv = self._polynomial.derivative()

        for _ in range(self._max_iterations):
            fx = self._polynomial.evaluate(x)
            fpx = deriv.evaluate(x)

            if abs(fpx) < self._tolerance:
                break

            x_new = x - fx / fpx
            if abs(x_new - x) < self._tolerance:
                return x_new
            x = x_new

        return x

    def find_real_roots(self) -> list[float]:
        """Find only real roots.

        Returns:
            List of real roots

        Example:
            >>> real_roots = solver.find_real_roots()
        """
        all_roots = self.solve()
        real_roots = [root.real for root in all_roots if abs(root.imag) < self._tolerance]
        return real_roots

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(solver)
        """
        return f"PolynomialSolver(polynomial={self._polynomial.name})"


__all__ = [
    "Polynomial",
    "PolynomialSolver",
]
