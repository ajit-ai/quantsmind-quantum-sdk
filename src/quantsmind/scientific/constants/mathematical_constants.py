"""
Mathematical Constants Module

This module provides mathematical constant definitions for the Scientific package.

Purpose
-------
Provide fundamental mathematical constants.

Responsibilities
----------------
- Define mathematical constants
- Support constant access
- Support constant metadata
- Support constant validation

Dependencies
------------
typing (standard library)
math (standard library)
quantsmind.scientific.types (scientific types)
quantsmind.scientific.constants.physical_constants (physical constants)
"""

from __future__ import annotations

import math

from quantsmind.scientific.constants.physical_constants import ConstantDefinition
from quantsmind.scientific.types import ConstantName


class MathematicalConstants:
    """Mathematical constants registry.

    This class provides fundamental mathematical constants.

    Attributes:
        _constants: Registered constants

    Example:
        >>> constants = MathematicalConstants()
        >>> pi = constants.get_constant("pi")
    """

    def __init__(self) -> None:
        """Initialize MathematicalConstants.

        Example:
            >>> constants = MathematicalConstants()
        """
        self._constants: dict[ConstantName, ConstantDefinition] = {}
        self._initialize_constants()

    def _initialize_constants(self) -> None:
        """Initialize mathematical constants.

        Example:
            >>> constants._initialize_constants()
        """
        # Mathematical constants
        self._constants["pi"] = ConstantDefinition(
            "pi",
            math.pi,
            "dimensionless",
            "Pi (π)"
        )
        self._constants["e"] = ConstantDefinition(
            "e",
            math.e,
            "dimensionless",
            "Euler's number"
        )
        self._constants["golden_ratio"] = ConstantDefinition(
            "golden_ratio",
            (1 + math.sqrt(5)) / 2,
            "dimensionless",
            "Golden ratio (φ)"
        )
        self._constants["sqrt2"] = ConstantDefinition(
            "sqrt2",
            math.sqrt(2),
            "dimensionless",
            "Square root of 2"
        )
        self._constants["sqrt3"] = ConstantDefinition(
            "sqrt3",
            math.sqrt(3),
            "dimensionless",
            "Square root of 3"
        )
        self._constants["ln2"] = ConstantDefinition(
            "ln2",
            math.log(2),
            "dimensionless",
            "Natural logarithm of 2"
        )
        self._constants["ln10"] = ConstantDefinition(
            "ln10",
            math.log(10),
            "dimensionless",
            "Natural logarithm of 10"
        )
        self._constants["log10_e"] = ConstantDefinition(
            "log10_e",
            math.log10(math.e),
            "dimensionless",
            "Base-10 logarithm of e"
        )
        self._constants["log2_e"] = ConstantDefinition(
            "log2_e",
            math.log2(math.e),
            "dimensionless",
            "Base-2 logarithm of e"
        )
        self._constants["euler_gamma"] = ConstantDefinition(
            "euler_gamma",
            0.57721566490153286060651209008240243104215933593992,
            "dimensionless",
            "Euler-Mascheroni constant (γ)"
        )
        self._constants["catalan_constant"] = ConstantDefinition(
            "catalan_constant",
            0.915965594177219015054603514932384110774,
            "dimensionless",
            "Catalan's constant (G)"
        )
        self._constants["apery_constant"] = ConstantDefinition(
            "apery_constant",
            1.202056903159594285399738161511449990764,
            "dimensionless",
            "Apéry's constant (ζ(3))"
        )
        self._constants["feigenbaum_alpha"] = ConstantDefinition(
            "feigenbaum_alpha",
            2.50290787509589282228390287321821599624,
            "dimensionless",
            "Feigenbaum constant α"
        )
        self._constants["feigenbaum_delta"] = ConstantDefinition(
            "feigenbaum_delta",
            4.669201609102990671853203820466201617258,
            "dimensionless",
            "Feigenbaum constant δ"
        )

    def get_constant(self, name: ConstantName) -> ConstantDefinition | None:
        """Get a constant by name.

        Args:
            name: Constant name

        Returns:
            Constant definition or None

        Example:
            >>> pi = constants.get_constant("pi")
        """
        return self._constants.get(name)

    def get_all_constants(self) -> dict[ConstantName, ConstantDefinition]:
        """Get all constants.

        Returns:
            Dictionary of constants

        Example:
            >>> all_constants = constants.get_all_constants()
        """
        return self._constants.copy()

    def register_constant(self, definition: ConstantDefinition) -> None:
        """Register a custom constant.

        Args:
            definition: Constant definition

        Example:
            >>> constants.register_constant(custom_constant)
        """
        self._constants[definition.name] = definition


# Export
__all__ = [
    "MathematicalConstants",
]
