"""
Custom Units Module

This module provides custom unit definitions for the Scientific package.

Purpose
-------
Provide custom unit definition capabilities.

Responsibilities
----------------
- Define custom units
- Support custom unit registration
- Support custom unit conversions
- Provide custom unit registry

Dependencies
------------
typing (standard library)
quantsmind.scientific.units.base_unit (base unit)
quantsmind.scientific.units.derived_units (derived units)
quantsmind.scientific.exceptions (scientific exceptions)
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from quantsmind.scientific.exceptions import UnitError
from quantsmind.scientific.units.base_unit import BaseUnit
from quantsmind.scientific.units.derived_units import DerivedUnit


class CustomUnit(BaseUnit):
    """Concrete implementation of a custom unit.

    This class provides custom unit functionality.

    Attributes:
        _definition: Custom unit definition
        _aliases: Unit aliases

    Example:
        >>> custom = CustomUnit("myunit", "mu", 1.0, "length", definition={"description": "Custom length unit"})
    """

    def __init__(
        self,
        name: str,
        symbol: str,
        conversion_factor: float,
        dimension: str,
        definition: Optional[Dict[str, any]] = None,
        aliases: Optional[List[str]] = None,
        metadata: Optional[Dict[str, any]] = None,
    ) -> None:
        """Initialize a CustomUnit.

        Args:
            name: Unit name
            symbol: Unit symbol
            conversion_factor: Conversion factor to base unit
            dimension: Unit dimension
            definition: Custom unit definition
            aliases: Unit aliases
            metadata: Unit metadata

        Example:
            >>> custom = CustomUnit("myunit", "mu", 1.0, "length", definition={"description": "Custom length unit"})
        """
        super().__init__(name, symbol, conversion_factor, dimension, metadata)
        self._definition = definition or {}
        self._aliases = aliases or []

    @property
    def definition(self) -> Dict[str, any]:
        """Get the unit definition.

        Returns:
            Unit definition

        Example:
            >>> print(f"Definition: {unit.definition}")
        """
        return self._definition.copy()

    @property
    def aliases(self) -> List[str]:
        """Get the unit aliases.

        Returns:
            List of aliases

        Example:
            >>> print(f"Aliases: {unit.aliases}")
        """
        return self._aliases.copy()

    def add_alias(self, alias: str) -> None:
        """Add an alias for the unit.

        Args:
            alias: Alias to add

        Example:
            >>> unit.add_alias("mu")
        """
        if alias not in self._aliases:
            self._aliases.append(alias)

    def remove_alias(self, alias: str) -> bool:
        """Remove an alias from the unit.

        Args:
            alias: Alias to remove

        Returns:
            True if removed, False otherwise

        Example:
            >>> removed = unit.remove_alias("mu")
        """
        if alias in self._aliases:
            self._aliases.remove(alias)
            return True
        return False

    def to_dict(self) -> Dict[str, any]:
        """Convert to dictionary.

        Returns:
            Unit definition

        Example:
            >>> data = unit.to_dict()
        """
        data = super().to_dict()
        data["definition"] = self._definition.copy()
        data["aliases"] = self._aliases.copy()
        return data

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(unit)
        """
        return f"CustomUnit(name={self._name}, symbol={self._symbol}, aliases={self._aliases})"


class CustomUnitsRegistry:
    """Registry for custom units.

    This class provides a registry of custom units.

    Attributes:
        _units: Registered units
        _aliases: Alias mapping

    Example:
        >>> registry = CustomUnitsRegistry()
        >>> custom = registry.get_unit("myunit")
    """

    def __init__(self) -> None:
        """Initialize CustomUnitsRegistry.

        Example:
            >>> registry = CustomUnitsRegistry()
        """
        self._units: Dict[str, CustomUnit] = {}
        self._aliases: Dict[str, str] = {}

    def register_unit(self, unit: CustomUnit) -> None:
        """Register a custom unit.

        Args:
            unit: Unit to register

        Example:
            >>> registry.register_unit(custom_unit)
        """
        self._units[unit.name] = unit
        for alias in unit.aliases:
            self._aliases[alias] = unit.name

    def get_unit(self, name: str) -> Optional[CustomUnit]:
        """Get a unit by name or alias.

        Args:
            name: Unit name or alias

        Returns:
            Unit or None

        Example:
            >>> custom = registry.get_unit("myunit")
        """
        # Check direct name
        if name in self._units:
            return self._units[name]
        
        # Check aliases
        if name in self._aliases:
            return self._units[self._aliases[name]]
        
        return None

    def get_all_units(self) -> Dict[str, CustomUnit]:
        """Get all registered units.

        Returns:
            Dictionary of units

        Example:
            >>> units = registry.get_all_units()
        """
        return self._units.copy()

    def remove_unit(self, name: str) -> bool:
        """Remove a unit from the registry.

        Args:
            name: Unit name

        Returns:
            True if removed, False otherwise

        Example:
            >>> removed = registry.remove_unit("myunit")
        """
        if name in self._units:
            unit = self._units[name]
            # Remove aliases
            for alias in unit.aliases:
                if alias in self._aliases:
                    del self._aliases[alias]
            del self._units[name]
            return True
        return False

    def create_unit(
        self,
        name: str,
        symbol: str,
        conversion_factor: float,
        dimension: str,
        definition: Optional[Dict[str, any]] = None,
        aliases: Optional[List[str]] = None,
        metadata: Optional[Dict[str, any]] = None,
    ) -> CustomUnit:
        """Create and register a custom unit.

        Args:
            name: Unit name
            symbol: Unit symbol
            conversion_factor: Conversion factor to base unit
            dimension: Unit dimension
            definition: Custom unit definition
            aliases: Unit aliases
            metadata: Unit metadata

        Returns:
            Created unit

        Example:
            >>> custom = registry.create_unit("myunit", "mu", 1.0, "length")
        """
        unit = CustomUnit(name, symbol, conversion_factor, dimension, definition, aliases, metadata)
        self.register_unit(unit)
        return unit


# Export
__all__ = [
    "CustomUnit",
    "CustomUnitsRegistry",
]
