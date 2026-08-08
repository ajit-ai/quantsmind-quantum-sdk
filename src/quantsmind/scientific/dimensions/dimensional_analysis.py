"""
Dimensional Analysis Module

This module provides dimensional analysis capabilities for the Scientific package.

Purpose
-------
Provide dimensional analysis operations.

Responsibilities
----------------
- Perform dimensional consistency checks
- Support dimensional calculations
- Support dimensional simplification
- Provide dimensional analysis tools

Dependencies
------------
typing (standard library)
quantsmind.scientific.dimensions.dimension (dimension)
quantsmind.scientific.exceptions (scientific exceptions)
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from quantsmind.scientific.dimensions.dimension import Dimension
from quantsmind.scientific.exceptions import DimensionError
from quantsmind.scientific.types import DimensionVector


class DimensionalAnalysis:
    """Concrete implementation of dimensional analysis.

    This class provides dimensional analysis capabilities.

    Attributes:
        _dimensions: Registered dimensions

    Example:
        >>> analysis = DimensionalAnalysis()
        >>> analysis.register_dimension("length", (1, 0, 0, 0, 0, 0, 0))
    """

    def __init__(self) -> None:
        """Initialize a DimensionalAnalysis.

        Example:
            >>> analysis = DimensionalAnalysis()
        """
        self._dimensions: Dict[str, Dimension] = {}
        self._initialize_base_dimensions()

    def _initialize_base_dimensions(self) -> None:
        """Initialize base dimensions.

        Example:
            >>> analysis._initialize_base_dimensions()
        """
        # Base dimensions (L, M, T, Θ, I, N, J)
        self._dimensions["length"] = Dimension("length", (1, 0, 0, 0, 0, 0, 0))
        self._dimensions["mass"] = Dimension("mass", (0, 1, 0, 0, 0, 0, 0))
        self._dimensions["time"] = Dimension("time", (0, 0, 1, 0, 0, 0, 0))
        self._dimensions["temperature"] = Dimension("temperature", (0, 0, 0, 1, 0, 0, 0))
        self._dimensions["charge"] = Dimension("charge", (0, 0, 0, 0, 1, 0, 0))
        self._dimensions["information"] = Dimension("information", (0, 0, 0, 0, 0, 1, 0))
        self._dimensions["probability"] = Dimension("probability", (0, 0, 0, 0, 0, 0, 1))

        # Derived dimensions
        self._dimensions["energy"] = Dimension("energy", (2, 1, -2, 0, 0, 0, 0))
        self._dimensions["force"] = Dimension("force", (1, 1, -2, 0, 0, 0, 0))
        self._dimensions["power"] = Dimension("power", (2, 1, -3, 0, 0, 0, 0))
        self._dimensions["frequency"] = Dimension("frequency", (0, 0, -1, 0, 0, 0, 0))
        self._dimensions["dimensionless"] = Dimension("dimensionless", (0, 0, 0, 0, 0, 0, 0))

    def register_dimension(self, name: str, vector: DimensionVector) -> Dimension:
        """Register a custom dimension.

        Args:
            name: Dimension name
            vector: Dimension vector

        Returns:
            Registered dimension

        Example:
            >>> analysis.register_dimension("custom", (1, 0, 0, 0, 0, 0, 0))
        """
        dimension = Dimension(name, vector)
        self._dimensions[name] = dimension
        return dimension

    def get_dimension(self, name: str) -> Optional[Dimension]:
        """Get a dimension by name.

        Args:
            name: Dimension name

        Returns:
            Dimension or None

        Example:
            >>> dimension = analysis.get_dimension("length")
        """
        return self._dimensions.get(name)

    def check_consistency(self, left: Dimension, right: Dimension) -> bool:
        """Check dimensional consistency.

        Args:
            left: Left dimension
            right: Right dimension

        Returns:
            True if consistent, False otherwise

        Example:
            >>> consistent = analysis.check_consistency(length_dim, length_dim)
        """
        return left.is_compatible(right)

    def multiply_dimensions(self, *dimensions: Dimension) -> Dimension:
        """Multiply multiple dimensions.

        Args:
            *dimensions: Dimensions to multiply

        Returns:
            Resulting dimension

        Raises:
            DimensionError: If no dimensions provided

        Example:
            >>> result = analysis.multiply_dimensions(length_dim, mass_dim)
        """
        if not dimensions:
            raise DimensionError("No dimensions provided for multiplication")

        result = dimensions[0]
        for dim in dimensions[1:]:
            result = result.multiply(dim)
        return result

    def divide_dimensions(self, numerator: Dimension, denominator: Dimension) -> Dimension:
        """Divide dimensions.

        Args:
            numerator: Numerator dimension
            denominator: Denominator dimension

        Returns:
            Resulting dimension

        Example:
            >>> result = analysis.divide_dimensions(energy_dim, time_dim)
        """
        return numerator.divide(denominator)

    def power_dimension(self, dimension: Dimension, exponent: int) -> Dimension:
        """Raise dimension to a power.

        Args:
            dimension: Dimension to raise
            exponent: Power to raise to

        Returns:
            Resulting dimension

        Example:
            >>> result = analysis.power_dimension(length_dim, 2)
        """
        return dimension.power(exponent)

    def simplify_dimension(self, vector: DimensionVector) -> Dimension:
        """Simplify a dimension vector to a known dimension.

        Args:
            vector: Dimension vector to simplify

        Returns:
            Simplified dimension

        Example:
            >>> simplified = analysis.simplify_dimension((2, 1, -2, 0, 0, 0, 0))
        """
        for name, dimension in self._dimensions.items():
            if dimension.vector == vector:
                return dimension
        
        # If no match, create a custom dimension
        return Dimension("custom", vector)

    def get_dimensional_formula(self, dimension: Dimension) -> str:
        """Get dimensional formula string.

        Args:
            dimension: Dimension to analyze

        Returns:
            Dimensional formula string

        Example:
            >>> formula = analysis.get_dimensional_formula(length_dim)
        """
        vector = dimension.vector
        symbols = ["L", "M", "T", "Θ", "I", "N", "J"]
        parts = []
        
        for i, (symbol, power) in enumerate(zip(symbols, vector)):
            if power != 0:
                if power == 1:
                    parts.append(symbol)
                else:
                    parts.append(f"{symbol}^{power}")
        
        return "·".join(parts) if parts else "dimensionless"

    def analyze_equation(self, left: Dimension, right: Dimension) -> Tuple[bool, str]:
        """Analyze dimensional consistency of an equation.

        Args:
            left: Left side dimension
            right: Right side dimension

        Returns:
            Tuple of (is_consistent, message)

        Example:
            >>> consistent, message = analysis.analyze_equation(length_dim, length_dim)
        """
        if self.check_consistency(left, right):
            return True, "Dimensions are consistent"
        else:
            left_formula = self.get_dimensional_formula(left)
            right_formula = self.get_dimensional_formula(right)
            return False, f"Dimensions inconsistent: {left_formula} ≠ {right_formula}"

    def get_all_dimensions(self) -> Dict[str, Dimension]:
        """Get all registered dimensions.

        Returns:
            Dictionary of dimensions

        Example:
            >>> dimensions = analysis.get_all_dimensions()
        """
        return self._dimensions.copy()


# Export
__all__ = [
    "DimensionalAnalysis",
]
