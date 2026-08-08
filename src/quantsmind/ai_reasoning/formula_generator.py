"""
Formula Generator Module

This module provides AI-assisted formula generation functionality for the QuantsMind SDK.

Purpose
-------
Provide AI-powered formula generation capabilities.

Classes
-------
FormulaGenerator: Formula generation engine

Responsibilities
----------------
- Generate mathematical formulas
- Suggest formula patterns
- Validate formula syntax
- Convert between formula formats

Dependencies
------------
typing (standard library)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


class FormulaGenerator:
    """Formula generation engine.

    This class provides AI-assisted generation of mathematical formulas.

    Attributes:
        _name: Generator name
        _formula_templates: Formula template library
        _generation_history: History of generated formulas
        _metadata: Additional metadata

    Example:
        >>> generator = FormulaGenerator()
        >>> formula = generator.generate_formula("quadratic", {"a": 1, "b": -2, "c": 1})
    """

    def __init__(
        self,
        name: str = "default",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a FormulaGenerator.

        Args:
            name: Generator name
            metadata: Additional metadata

        Example:
            >>> generator = FormulaGenerator()
        """
        self._name = name
        self._formula_templates: Dict[str, str] = {}
        self._generation_history: List[Dict[str, Any]] = []
        self._metadata = metadata or {}

    @property
    def name(self) -> str:
        """Get the generator name.

        Returns:
            Generator name

        Example:
            >>> name = generator.name
        """
        return self._name

    def generate_formula(
        self,
        formula_type: str,
        parameters: Dict[str, Any],
    ) -> str:
        """Generate a mathematical formula.

        Args:
            formula_type: Type of formula to generate
            parameters: Formula parameters

        Returns:
            Generated formula string

        Example:
            >>> formula = generator.generate_formula("quadratic", {"a": 1, "b": -2, "c": 1})
        """
        formula = self._build_formula(formula_type, parameters)

        result = {
            "formula_type": formula_type,
            "parameters": parameters,
            "formula": formula,
        }

        self._generation_history.append(result)
        return formula

    def _build_formula(
        self,
        formula_type: str,
        parameters: Dict[str, Any],
    ) -> str:
        """Build a formula from type and parameters.

        Args:
            formula_type: Type of formula
            parameters: Formula parameters

        Returns:
            Formula string

        Example:
            >>> formula = generator._build_formula("quadratic", {"a": 1, "b": -2, "c": 1})
        """
        formulas = {
            "quadratic": self._quadratic_formula(parameters),
            "linear": self._linear_formula(parameters),
            "circle": self._circle_formula(parameters),
            "sphere": self._sphere_formula(parameters),
            "gaussian": self._gaussian_formula(parameters),
        }

        return formulas.get(formula_type, "Unknown formula type")

    def _quadratic_formula(self, params: Dict[str, Any]) -> str:
        """Build quadratic formula.

        Args:
            params: Parameters (a, b, c)

        Returns:
            Quadratic formula string

        Example:
            >>> formula = generator._quadratic_formula({"a": 1, "b": -2, "c": 1})
        """
        a = params.get("a", 1)
        b = params.get("b", 0)
        c = params.get("c", 0)

        return f"{a}*x^2 + {b}*x + {c} = 0"

    def _linear_formula(self, params: Dict[str, Any]) -> str:
        """Build linear formula.

        Args:
            params: Parameters (m, b)

        Returns:
            Linear formula string

        Example:
            >>> formula = generator._linear_formula({"m": 2, "b": 3})
        """
        m = params.get("m", 1)
        b = params.get("b", 0)

        return f"y = {m}*x + {b}"

    def _circle_formula(self, params: Dict[str, Any]) -> str:
        """Build circle formula.

        Args:
            params: Parameters (h, k, r)

        Returns:
            Circle formula string

        Example:
            >>> formula = generator._circle_formula({"h": 0, "k": 0, "r": 5})
        """
        h = params.get("h", 0)
        k = params.get("k", 0)
        r = params.get("r", 1)

        return f"(x - {h})^2 + (y - {k})^2 = {r}^2"

    def _sphere_formula(self, params: Dict[str, Any]) -> str:
        """Build sphere formula.

        Args:
            params: Parameters (h, k, l, r)

        Returns:
            Sphere formula string

        Example:
            >>> formula = generator._sphere_formula({"h": 0, "k": 0, "l": 0, "r": 5})
        """
        h = params.get("h", 0)
        k = params.get("k", 0)
        l = params.get("l", 0)
        r = params.get("r", 1)

        return f"(x - {h})^2 + (y - {k})^2 + (z - {l})^2 = {r}^2"

    def _gaussian_formula(self, params: Dict[str, Any]) -> str:
        """Build Gaussian formula.

        Args:
            params: Parameters (mu, sigma)

        Returns:
            Gaussian formula string

        Example:
            >>> formula = generator._gaussian_formula({"mu": 0, "sigma": 1})
        """
        mu = params.get("mu", 0)
        sigma = params.get("sigma", 1)

        return f"(1/({sigma}*sqrt(2*pi))) * exp(-((x - {mu})^2)/(2*{sigma}^2))"

    def suggest_formula_pattern(self, problem: str) -> List[str]:
        """Suggest formula patterns for a problem.

        Args:
            problem: Problem description

        Returns:
            List of suggested patterns

        Example:
            >>> patterns = generator.suggest_formula_pattern("Find the roots of x^2 - 4 = 0")
        """
        problem_lower = problem.lower()

        if "quadratic" in problem_lower or "x^2" in problem_lower or "x**2" in problem_lower:
            return ["quadratic", "parabola"]
        elif "linear" in problem_lower or "x" in problem_lower:
            return ["linear", "line"]
        elif "circle" in problem_lower:
            return ["circle"]
        elif "sphere" in problem_lower:
            return ["sphere"]
        elif "gaussian" in problem_lower or "normal" in problem_lower:
            return ["gaussian", "normal_distribution"]

        return ["general"]

    def validate_formula(self, formula: str) -> Dict[str, Any]:
        """Validate a formula.

        Args:
            formula: Formula string

        Returns:
            Validation result

        Example:
            >>> validation = generator.validate_formula("x^2 + 2x + 1 = 0")
        """
        validation = {
            "is_valid": True,
            "issues": [],
            "suggestions": [],
        }

        # Basic validation checks
        if "=" not in formula:
            validation["is_valid"] = False
            validation["issues"].append("Missing equals sign")

        if not any(c in formula for c in ["x", "y", "z"]):
            validation["suggestions"].append("Consider adding variables")

        return validation

    def convert_to_latex(self, formula: str) -> str:
        """Convert formula to LaTeX format.

        Args:
            formula: Formula string

        Returns:
            LaTeX formatted formula

        Example:
            >>> latex = generator.convert_to_latex("x^2 + 2x + 1 = 0")
        """
        latex = formula

        # Simple conversions
        latex = latex.replace("^2", "^2")
        latex = latex.replace("^3", "^3")
        latex = latex.replace("sqrt", "\\sqrt")
        latex = latex.replace("pi", "\\pi")
        latex = latex.replace("exp", "e^")

        return latex

    def get_generation_history(self) -> List[Dict[str, Any]]:
        """Get the generation history.

        Returns:
            List of past generated formulas

        Example:
            >>> history = generator.get_generation_history()
        """
        return self._generation_history.copy()

    def clear_history(self) -> None:
        """Clear the generation history.

        Example:
            >>> generator.clear_history()
        """
        self._generation_history = []

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(generator)
        """
        return f"FormulaGenerator(name={self._name}, history_entries={len(self._generation_history)})"


__all__ = [
    "FormulaGenerator",
]
