"""
Physical Constants Module

This module provides physical constant definitions for the Scientific package.

Purpose
-------
Provide fundamental physical constants.

Responsibilities
----------------
- Define physical constants
- Support constant access
- Support constant metadata
- Support constant validation

Dependencies
------------
typing (standard library)
quantsmind.scientific.types (scientific types)
"""

from __future__ import annotations

from typing import Any, Dict

from quantsmind.scientific.types import ConstantName, ConstantValue


class PhysicalConstants:
    """Physical constants registry.

    This class provides fundamental physical constants.

    Attributes:
        _constants: Registered constants

    Example:
        >>> constants = PhysicalConstants()
        >>> c = constants.get_constant("speed_of_light")
    """

    def __init__(self) -> None:
        """Initialize PhysicalConstants.

        Example:
            >>> constants = PhysicalConstants()
        """
        self._constants: Dict[ConstantName, ConstantDefinition] = {}
        self._initialize_constants()

    def _initialize_constants(self) -> None:
        """Initialize physical constants.

        Example:
            >>> constants._initialize_constants()
        """
        # Fundamental constants
        self._constants["speed_of_light"] = ConstantDefinition(
            "speed_of_light",
            299792458.0,
            "m/s",
            "Speed of light in vacuum"
        )
        self._constants["planck_constant"] = ConstantDefinition(
            "planck_constant",
            6.62607015e-34,
            "J·s",
            "Planck constant"
        )
        self._constants["reduced_planck_constant"] = ConstantDefinition(
            "reduced_planck_constant",
            1.054571817e-34,
            "J·s",
            "Reduced Planck constant (h-bar)"
        )
        self._constants["boltzmann_constant"] = ConstantDefinition(
            "boltzmann_constant",
            1.380649e-23,
            "J/K",
            "Boltzmann constant"
        )
        self._constants["gravitational_constant"] = ConstantDefinition(
            "gravitational_constant",
            6.67430e-11,
            "m³/(kg·s²)",
            "Gravitational constant"
        )
        self._constants["elementary_charge"] = ConstantDefinition(
            "elementary_charge",
            1.602176634e-19,
            "C",
            "Elementary charge"
        )
        self._constants["electron_mass"] = ConstantDefinition(
            "electron_mass",
            9.1093837015e-31,
            "kg",
            "Electron rest mass"
        )
        self._constants["proton_mass"] = ConstantDefinition(
            "proton_mass",
            1.67262192369e-27,
            "kg",
            "Proton rest mass"
        )
        self._constants["neutron_mass"] = ConstantDefinition(
            "neutron_mass",
            1.67492749804e-27,
            "kg",
            "Neutron rest mass"
        )
        self._constants["avogadro_constant"] = ConstantDefinition(
            "avogadro_constant",
            6.02214076e23,
            "mol⁻¹",
            "Avogadro constant"
        )
        self._constants["fine_structure_constant"] = ConstantDefinition(
            "fine_structure_constant",
            7.2973525693e-3,
            "dimensionless",
            "Fine-structure constant"
        )
        self._constants["rydberg_constant"] = ConstantDefinition(
            "rydberg_constant",
            10973731.568160,
            "m⁻¹",
            "Rydberg constant"
        )
        self._constants["stefan_boltzmann_constant"] = ConstantDefinition(
            "stefan_boltzmann_constant",
            5.670374419e-8,
            "W/(m²·K⁴)",
            "Stefan-Boltzmann constant"
        )
        self._constants["vacuum_permittivity"] = ConstantDefinition(
            "vacuum_permittivity",
            8.8541878128e-12,
            "F/m",
            "Vacuum permittivity"
        )
        self._constants["vacuum_permeability"] = ConstantDefinition(
            "vacuum_permeability",
            1.25663706212e-6,
            "N/A²",
            "Vacuum permeability"
        )

    def get_constant(self, name: ConstantName) -> Optional[ConstantDefinition]:
        """Get a constant by name.

        Args:
            name: Constant name

        Returns:
            Constant definition or None

        Example:
            >>> c = constants.get_constant("speed_of_light")
        """
        return self._constants.get(name)

    def get_all_constants(self) -> Dict[ConstantName, ConstantDefinition]:
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


class ConstantDefinition:
    """Constant definition.

    This class provides constant definition functionality.

    Attributes:
        _name: Constant name
        _value: Constant value
        _unit: Constant unit
        _description: Constant description

    Example:
        >>> c = ConstantDefinition("speed_of_light", 299792458.0, "m/s", "Speed of light")
    """

    def __init__(
        self,
        name: ConstantName,
        value: ConstantValue,
        unit: str,
        description: str = "",
    ) -> None:
        """Initialize a ConstantDefinition.

        Args:
            name: Constant name
            value: Constant value
            unit: Constant unit
            description: Constant description

        Example:
            >>> c = ConstantDefinition("speed_of_light", 299792458.0, "m/s", "Speed of light")
        """
        self._name = name
        self._value = value
        self._unit = unit
        self._description = description

    @property
    def name(self) -> ConstantName:
        """Get the constant name.

        Returns:
            Constant name

        Example:
            >>> print(f"Name: {constant.name}")
        """
        return self._name

    @property
    def value(self) -> ConstantValue:
        """Get the constant value.

        Returns:
            Constant value

        Example:
            >>> print(f"Value: {constant.value}")
        """
        return self._value

    @property
    def unit(self) -> str:
        """Get the constant unit.

        Returns:
            Constant unit

        Example:
            >>> print(f"Unit: {constant.unit}")
        """
        return self._unit

    @property
    def description(self) -> str:
        """Get the constant description.

        Returns:
            Constant description

        Example:
            >>> print(f"Description: {constant.description}")
        """
        return self._description

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Constant definition

        Example:
            >>> data = constant.to_dict()
        """
        return {
            "name": self._name,
            "value": self._value,
            "unit": self._unit,
            "description": self._description,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(constant)
        """
        return f"ConstantDefinition(name={self._name}, value={self._value}, unit={self._unit})"


# Export
__all__ = [
    "PhysicalConstants",
    "ConstantDefinition",
]
