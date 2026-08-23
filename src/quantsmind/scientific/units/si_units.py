"""
SI Units Module

This module provides SI unit definitions for the Scientific package.

Purpose
-------
Provide standard SI unit definitions.

Responsibilities
----------------
- Define SI base units
- Define SI derived units
- Support SI unit conversions
- Provide SI unit registry

Dependencies
------------
typing (standard library)
quantsmind.scientific.units.base_unit (base unit)
"""

from __future__ import annotations

from quantsmind.scientific.units.base_unit import BaseUnit


class SIUnits:
    """SI Units registry.

    This class provides a registry of standard SI units.

    Attributes:
        _units: Registered units

    Example:
        >>> si = SIUnits()
        >>> meter = si.get_unit("meter")
    """

    def __init__(self) -> None:
        """Initialize SIUnits registry.

        Example:
            >>> si = SIUnits()
        """
        self._units: dict[str, BaseUnit] = {}
        self._initialize_base_units()
        self._initialize_derived_units()

    def _initialize_base_units(self) -> None:
        """Initialize SI base units.

        Example:
            >>> si._initialize_base_units()
        """
        # Length
        self._units["meter"] = BaseUnit("meter", "m", 1.0, "length")
        self._units["kilometer"] = BaseUnit("kilometer", "km", 1000.0, "length")
        self._units["centimeter"] = BaseUnit("centimeter", "cm", 0.01, "length")

        # Mass
        self._units["kilogram"] = BaseUnit("kilogram", "kg", 1.0, "mass")
        self._units["gram"] = BaseUnit("gram", "g", 0.001, "mass")

        # Time
        self._units["second"] = BaseUnit("second", "s", 1.0, "time")
        self._units["minute"] = BaseUnit("minute", "min", 60.0, "time")
        self._units["hour"] = BaseUnit("hour", "h", 3600.0, "time")

        # Temperature
        self._units["kelvin"] = BaseUnit("kelvin", "K", 1.0, "temperature")
        self._units["celsius"] = BaseUnit("celsius", "°C", 1.0, "temperature")

        # Electric current
        self._units["ampere"] = BaseUnit("ampere", "A", 1.0, "charge")

        # Information
        self._units["byte"] = BaseUnit("byte", "B", 1.0, "information")
        self._units["bit"] = BaseUnit("bit", "b", 0.125, "information")

    def _initialize_derived_units(self) -> None:
        """Initialize SI derived units.

        Example:
            >>> si._initialize_derived_units()
        """
        # Energy
        self._units["joule"] = BaseUnit("joule", "J", 1.0, "energy")
        self._units["electronvolt"] = BaseUnit("electronvolt", "eV", 1.602176634e-19, "energy")

        # Force
        self._units["newton"] = BaseUnit("newton", "N", 1.0, "force")

        # Power
        self._units["watt"] = BaseUnit("watt", "W", 1.0, "power")

        # Pressure
        self._units["pascal"] = BaseUnit("pascal", "Pa", 1.0, "force")

        # Voltage
        self._units["volt"] = BaseUnit("volt", "V", 1.0, "energy")

        # Magnetic field
        self._units["tesla"] = BaseUnit("tesla", "T", 1.0, "force")

        # Frequency
        self._units["hertz"] = BaseUnit("hertz", "Hz", 1.0, "frequency")

    def get_unit(self, name: str) -> BaseUnit | None:
        """Get a unit by name.

        Args:
            name: Unit name

        Returns:
            Unit or None

        Example:
            >>> meter = si.get_unit("meter")
        """
        return self._units.get(name)

    def get_all_units(self) -> dict[str, BaseUnit]:
        """Get all registered units.

        Returns:
            Dictionary of units

        Example:
            >>> units = si.get_all_units()
        """
        return self._units.copy()

    def register_unit(self, unit: BaseUnit) -> None:
        """Register a custom unit.

        Args:
            unit: Unit to register

        Example:
            >>> si.register_unit(custom_unit)
        """
        self._units[unit.name] = unit


# Export
__all__ = [
    "SIUnits",
]
