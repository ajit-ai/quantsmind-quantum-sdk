"""
Derived Units Module

This module provides derived unit definitions for the Scientific package.

Purpose
-------
Provide derived unit definitions from base units.

Responsibilities
----------------
- Define derived units
- Support derived unit conversions
- Support derived unit composition
- Provide derived unit registry

Dependencies
------------
typing (standard library)
quantsmind.scientific.units.base_unit (base unit)
quantsmind.scientific.exceptions (scientific exceptions)
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from quantsmind.scientific.exceptions import UnitError
from quantsmind.scientific.units.base_unit import BaseUnit


class DerivedUnit(BaseUnit):
    """Concrete implementation of a derived unit.

    This class provides derived unit functionality.

    Attributes:
        _base_units: Base units composition
        _exponents: Exponents for base units

    Example:
        >>> newton = DerivedUnit("newton", "N", 1.0, "force", [("meter", 1), ("kilogram", 1), ("second", -2)])
    """

    def __init__(
        self,
        name: str,
        symbol: str,
        conversion_factor: float,
        dimension: str,
        base_units: Optional[List[Tuple[str, int]]] = None,
        metadata: Optional[Dict[str, any]] = None,
    ) -> None:
        """Initialize a DerivedUnit.

        Args:
            name: Unit name
            symbol: Unit symbol
            conversion_factor: Conversion factor to base unit
            dimension: Unit dimension
            base_units: List of (base_unit_name, exponent) tuples
            metadata: Unit metadata

        Example:
            >>> newton = DerivedUnit("newton", "N", 1.0, "force", [("meter", 1), ("kilogram", 1), ("second", -2)])
        """
        super().__init__(name, symbol, conversion_factor, dimension, metadata)
        self._base_units = base_units or []
        self._exponents: Dict[str, int] = {unit: exp for unit, exp in self._base_units}

    @property
    def base_units(self) -> List[Tuple[str, int]]:
        """Get the base units composition.

        Returns:
            List of (base_unit_name, exponent) tuples

        Example:
            >>> print(f"Base units: {unit.base_units}")
        """
        return self._base_units.copy()

    @property
    def exponents(self) -> Dict[str, int]:
        """Get the exponents for base units.

        Returns:
            Dictionary of base unit names to exponents

        Example:
            >>> print(f"Exponents: {unit.exponents}")
        """
        return self._exponents.copy()

    def compose_from(self, base_unit_instances: Dict[str, BaseUnit]) -> float:
        """Calculate conversion factor from base unit instances.

        Args:
            base_unit_instances: Dictionary of base unit names to instances

        Returns:
            Calculated conversion factor

        Raises:
            UnitError: If base units are missing

        Example:
            >>> factor = unit.compose_from({"meter": meter_unit, "kilogram": kg_unit, "second": sec_unit})
        """
        factor = 1.0
        for unit_name, exponent in self._base_units:
            if unit_name not in base_unit_instances:
                raise UnitError(f"Missing base unit: {unit_name}", unit=unit_name)
            base_unit = base_unit_instances[unit_name]
            factor *= base_unit.conversion_factor ** exponent
        return factor

    def to_dict(self) -> Dict[str, any]:
        """Convert to dictionary.

        Returns:
            Unit definition

        Example:
            >>> data = unit.to_dict()
        """
        data = super().to_dict()
        data["base_units"] = self._base_units.copy()
        data["exponents"] = self._exponents.copy()
        return data

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(unit)
        """
        return f"DerivedUnit(name={self._name}, symbol={self._symbol}, base_units={self._base_units})"


class DerivedUnitsRegistry:
    """Registry for derived units.

    This class provides a registry of derived units.

    Attributes:
        _units: Registered units

    Example:
        >>> registry = DerivedUnitsRegistry()
        >>> newton = registry.get_unit("newton")
    """

    def __init__(self) -> None:
        """Initialize DerivedUnitsRegistry.

        Example:
            >>> registry = DerivedUnitsRegistry()
        """
        self._units: Dict[str, DerivedUnit] = {}
        self._initialize_common_derived_units()

    def _initialize_common_derived_units(self) -> None:
        """Initialize common derived units.

        Example:
            >>> registry._initialize_common_derived_units()
        """
        # Force: kg·m/s²
        self._units["newton"] = DerivedUnit(
            "newton", "N", 1.0, "force",
            [("kilogram", 1), ("meter", 1), ("second", -2)]
        )

        # Energy: kg·m²/s²
        self._units["joule"] = DerivedUnit(
            "joule", "J", 1.0, "energy",
            [("kilogram", 1), ("meter", 2), ("second", -2)]
        )

        # Power: kg·m²/s³
        self._units["watt"] = DerivedUnit(
            "watt", "W", 1.0, "power",
            [("kilogram", 1), ("meter", 2), ("second", -3)]
        )

        # Pressure: kg/(m·s²)
        self._units["pascal"] = DerivedUnit(
            "pascal", "Pa", 1.0, "force",
            [("kilogram", 1), ("meter", -1), ("second", -2)]
        )

        # Frequency: 1/s
        self._units["hertz"] = DerivedUnit(
            "hertz", "Hz", 1.0, "frequency",
            [("second", -1)]
        )

    def get_unit(self, name: str) -> Optional[DerivedUnit]:
        """Get a unit by name.

        Args:
            name: Unit name

        Returns:
            Unit or None

        Example:
            >>> newton = registry.get_unit("newton")
        """
        return self._units.get(name)

    def get_all_units(self) -> Dict[str, DerivedUnit]:
        """Get all registered units.

        Returns:
            Dictionary of units

        Example:
            >>> units = registry.get_all_units()
        """
        return self._units.copy()

    def register_unit(self, unit: DerivedUnit) -> None:
        """Register a derived unit.

        Args:
            unit: Unit to register

        Example:
            >>> registry.register_unit(custom_unit)
        """
        self._units[unit.name] = unit


# Export
__all__ = [
    "DerivedUnit",
    "DerivedUnitsRegistry",
]
