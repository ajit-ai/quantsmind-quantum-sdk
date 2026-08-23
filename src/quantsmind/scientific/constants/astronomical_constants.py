"""
Astronomical Constants Module

This module provides astronomical constant definitions for the Scientific package.

Purpose
-------
Provide fundamental astronomical constants.

Responsibilities
----------------
- Define astronomical constants
- Support constant access
- Support constant metadata
- Support constant validation

Dependencies
------------
typing (standard library)
quantsmind.scientific.types (scientific types)
quantsmind.scientific.constants.physical_constants (physical constants)
"""

from __future__ import annotations

from quantsmind.scientific.constants.physical_constants import ConstantDefinition
from quantsmind.scientific.types import ConstantName


class AstronomicalConstants:
    """Astronomical constants registry.

    This class provides fundamental astronomical constants.

    Attributes:
        _constants: Registered constants

    Example:
        >>> constants = AstronomicalConstants()
        >>> au = constants.get_constant("astronomical_unit")
    """

    def __init__(self) -> None:
        """Initialize AstronomicalConstants.

        Example:
            >>> constants = AstronomicalConstants()
        """
        self._constants: dict[ConstantName, ConstantDefinition] = {}
        self._initialize_constants()

    def _initialize_constants(self) -> None:
        """Initialize astronomical constants.

        Example:
            >>> constants._initialize_constants()
        """
        # Astronomical constants
        self._constants["astronomical_unit"] = ConstantDefinition(
            "astronomical_unit",
            1.495978707e11,
            "m",
            "Astronomical unit (average Earth-Sun distance)"
        )
        self._constants["light_year"] = ConstantDefinition(
            "light_year",
            9.4607304725808e15,
            "m",
            "Light year"
        )
        self._constants["parsec"] = ConstantDefinition(
            "parsec",
            3.08567758149137e16,
            "m",
            "Parsec"
        )
        self._constants["solar_mass"] = ConstantDefinition(
            "solar_mass",
            1.98847e30,
            "kg",
            "Solar mass"
        )
        self._constants["solar_luminosity"] = ConstantDefinition(
            "solar_luminosity",
            3.828e26,
            "W",
            "Solar luminosity"
        )
        self._constants["solar_radius"] = ConstantDefinition(
            "solar_radius",
            6.957e8,
            "m",
            "Solar radius"
        )
        self._constants["earth_mass"] = ConstantDefinition(
            "earth_mass",
            5.9722e24,
            "kg",
            "Earth mass"
        )
        self._constants["earth_radius"] = ConstantDefinition(
            "earth_radius",
            6.371e6,
            "m",
            "Earth mean radius"
        )
        self._constants["earth_orbital_period"] = ConstantDefinition(
            "earth_orbital_period",
            3.155815e7,
            "s",
            "Earth orbital period (sidereal year)"
        )
        self._constants["lunar_mass"] = ConstantDefinition(
            "lunar_mass",
            7.342e22,
            "kg",
            "Lunar mass"
        )
        self._constants["lunar_radius"] = ConstantDefinition(
            "lunar_radius",
            1.7374e6,
            "m",
            "Lunar radius"
        )
        self._constants["lunar_distance"] = ConstantDefinition(
            "lunar_distance",
            3.844e8,
            "m",
            "Average Earth-Moon distance"
        )
        self._constants["jupiter_mass"] = ConstantDefinition(
            "jupiter_mass",
            1.89813e27,
            "kg",
            "Jupiter mass"
        )
        self._constants["hubble_constant"] = ConstantDefinition(
            "hubble_constant",
            2.192e-18,
            "s⁻¹",
            "Hubble constant"
        )
        self._constants["cosmic_microwave_background_temperature"] = ConstantDefinition(
            "cosmic_microwave_background_temperature",
            2.7255,
            "K",
            "Cosmic microwave background temperature"
        )
        self._constants["age_of_universe"] = ConstantDefinition(
            "age_of_universe",
            4.35e17,
            "s",
            "Age of the universe"
        )

    def get_constant(self, name: ConstantName) -> ConstantDefinition | None:
        """Get a constant by name.

        Args:
            name: Constant name

        Returns:
            Constant definition or None

        Example:
            >>> au = constants.get_constant("astronomical_unit")
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
    "AstronomicalConstants",
]
