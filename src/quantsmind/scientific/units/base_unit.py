"""
Base Unit Module

This module provides the base unit class for the Scientific package.

Purpose
-------
Provide the foundation for unit definitions.

Responsibilities
----------------
- Define base unit structure
- Support unit conversion
- Support unit compatibility checks
- Support unit metadata

Dependencies
------------
typing (standard library)
quantsmind.scientific.exceptions (scientific exceptions)
quantsmind.scientific.interfaces (scientific interfaces)
quantsmind.scientific.types (scientific types)
"""

from __future__ import annotations

from typing import Any

from quantsmind.scientific.exceptions import UnitError
from quantsmind.scientific.interfaces import IUnit
from quantsmind.scientific.types import ConversionFactor, UnitDefinition


class BaseUnit(IUnit):
    """Concrete implementation of a base unit.

    This class provides the foundation for unit definitions.

    Attributes:
        _name: Unit name
        _symbol: Unit symbol
        _conversion_factor: Conversion factor to base unit
        _dimension: Unit dimension
        _metadata: Unit metadata

    Example:
        >>> meter = BaseUnit("meter", "m", 1.0, "length")
        >>> meter.name()
    """

    def __init__(
        self,
        name: str,
        symbol: str,
        conversion_factor: ConversionFactor,
        dimension: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a BaseUnit.

        Args:
            name: Unit name
            symbol: Unit symbol
            conversion_factor: Conversion factor to base unit
            dimension: Unit dimension
            metadata: Unit metadata

        Example:
            >>> meter = BaseUnit("meter", "m", 1.0, "length")
        """
        self._name = name
        self._symbol = symbol
        self._conversion_factor = conversion_factor
        self._dimension = dimension
        self._metadata = metadata or {}

    @property
    def name(self) -> str:
        """Get the unit name.

        Returns:
            Unit name

        Example:
            >>> print(f"Name: {unit.name}")
        """
        return self._name

    @property
    def symbol(self) -> str:
        """Get the unit symbol.

        Returns:
            Unit symbol

        Example:
            >>> print(f"Symbol: {unit.symbol}")
        """
        return self._symbol

    @property
    def conversion_factor(self) -> ConversionFactor:
        """Get the conversion factor.

        Returns:
            Conversion factor to base unit

        Example:
            >>> print(f"Conversion factor: {unit.conversion_factor}")
        """
        return self._conversion_factor

    @property
    def dimension(self) -> str:
        """Get the unit dimension.

        Returns:
            Unit dimension

        Example:
            >>> print(f"Dimension: {unit.dimension}")
        """
        return self._dimension

    @property
    def metadata(self) -> dict[str, Any]:
        """Get the unit metadata.

        Returns:
            Unit metadata

        Example:
            >>> print(f"Metadata: {unit.metadata}")
        """
        return self._metadata.copy()

    def is_compatible(self, other: IUnit) -> bool:
        """Check if units are compatible.

        Args:
            other: Other unit

        Returns:
            True if compatible, False otherwise

        Example:
            >>> if unit.is_compatible(other_unit):
            ...     print("Compatible")
        """
        return self._dimension == other.dimension

    def convert_value(self, value: float, target_unit: IUnit) -> float:
        """Convert a value to a target unit.

        Args:
            value: Value to convert
            target_unit: Target unit

        Returns:
            Converted value

        Raises:
            UnitError: If units are not compatible

        Example:
            >>> converted = unit.convert_value(1.0, target_unit)
        """
        if not self.is_compatible(target_unit):
            raise UnitError(
                f"Cannot convert {self._name} to {target_unit.name()}",
                from_unit=self._name,
                to_unit=target_unit.name(),
            )

        # Convert to base unit, then to target unit
        base_value = value * self._conversion_factor
        target_value = base_value / target_unit.conversion_factor()
        return target_value

    def to_dict(self) -> UnitDefinition:
        """Convert to dictionary.

        Returns:
            Unit definition

        Example:
            >>> data = unit.to_dict()
        """
        return {
            "name": self._name,
            "symbol": self._symbol,
            "conversion_factor": self._conversion_factor,
            "dimension": self._dimension,
            "metadata": self._metadata.copy(),
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(unit)
        """
        return f"BaseUnit(name={self._name}, symbol={self._symbol})"


# Export
__all__ = [
    "BaseUnit",
]
