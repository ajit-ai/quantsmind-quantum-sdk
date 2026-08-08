"""
Validators Module

This module provides validation functions for the Scientific package.

Purpose
-------
Provide validation logic for scientific objects.

Responsibilities
----------------
- Validate units
- Validate dimensions
- Validate quantities
- Validate measurements
- Validate coordinates

Dependencies
------------
typing (standard library)
quantsmind.scientific.exceptions (scientific exceptions)
quantsmind.scientific.types (scientific types)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from quantsmind.scientific.exceptions import (
    ConversionError,
    DimensionError,
    MeasurementError,
    QuantityError,
    ValidationError,
)
from quantsmind.scientific.types import ValidationResult


class ScientificValidator:
    """Concrete implementation of scientific validation.

    This class provides validation functionality.

    Attributes:
        _errors: Validation errors

    Example:
        >>> validator = ScientificValidator()
        >>> validator.validate_unit("meter")
    """

    def __init__(self) -> None:
        """Initialize a ScientificValidator.

        Example:
            >>> validator = ScientificValidator()
        """
        self._errors: List[str] = []

    @property
    def errors(self) -> List[str]:
        """Get the validation errors.

        Returns:
            List of errors

        Example:
            >>> print(f"Errors: {validator.errors}")
        """
        return self._errors.copy()

    def clear_errors(self) -> None:
        """Clear validation errors.

        Example:
            >>> validator.clear_errors()
        """
        self._errors.clear()

    def validate_unit(self, unit: str) -> ValidationResult:
        """Validate a unit.

        Args:
            unit: Unit name

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = validator.validate_unit("meter")
        """
        self.clear_errors()
        
        if not unit:
            self._errors.append("Unit cannot be empty")
            return False, self._errors
        
        if not isinstance(unit, str):
            self._errors.append("Unit must be a string")
            return False, self._errors
        
        return True, []

    def validate_dimension(self, dimension: str) -> ValidationResult:
        """Validate a dimension.

        Args:
            dimension: Dimension name

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = validator.validate_dimension("length")
        """
        self.clear_errors()
        
        if not dimension:
            self._errors.append("Dimension cannot be empty")
            return False, self._errors
        
        if not isinstance(dimension, str):
            self._errors.append("Dimension must be a string")
            return False, self._errors
        
        return True, []

    def validate_quantity(self, value: float, unit: str, dimension: str) -> ValidationResult:
        """Validate a quantity.

        Args:
            value: Quantity value
            unit: Unit name
            dimension: Dimension name

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = validator.validate_quantity(1.0, "meter", "length")
        """
        self.clear_errors()
        
        if not isinstance(value, (int, float)):
            self._errors.append("Quantity value must be numeric")
        
        unit_valid, unit_errors = self.validate_unit(unit)
        if not unit_valid:
            self._errors.extend(unit_errors)
        
        dimension_valid, dimension_errors = self.validate_dimension(dimension)
        if not dimension_valid:
            self._errors.extend(dimension_errors)
        
        return len(self._errors) == 0, self._errors

    def validate_measurement(
        self,
        value: float,
        uncertainty: float,
        unit: str,
        confidence: float,
    ) -> ValidationResult:
        """Validate a measurement.

        Args:
            value: Measurement value
            uncertainty: Measurement uncertainty
            unit: Unit name
            confidence: Confidence level

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = validator.validate_measurement(1.0, 0.01, "meter", 0.95)
        """
        self.clear_errors()
        
        if not isinstance(value, (int, float)):
            self._errors.append("Measurement value must be numeric")
        
        if uncertainty < 0:
            self._errors.append("Uncertainty cannot be negative")
        
        if not 0.0 <= confidence <= 1.0:
            self._errors.append("Confidence must be between 0.0 and 1.0")
        
        unit_valid, unit_errors = self.validate_unit(unit)
        if not unit_valid:
            self._errors.extend(unit_errors)
        
        return len(self._errors) == 0, self._errors

    def validate_coordinate(self, system: str, coordinates: tuple) -> ValidationResult:
        """Validate a coordinate.

        Args:
            system: Coordinate system
            coordinates: Coordinate values

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = validator.validate_coordinate("cartesian", (1.0, 2.0, 3.0))
        """
        self.clear_errors()
        
        valid_systems = ["cartesian", "polar", "cylindrical", "spherical", "galactic", "equatorial"]
        
        if system not in valid_systems:
            self._errors.append(f"Invalid coordinate system: {system}")
        
        if not isinstance(coordinates, (tuple, list)):
            self._errors.append("Coordinates must be a tuple or list")
            return False, self._errors
        
        if len(coordinates) < 2:
            self._errors.append("Coordinates must have at least 2 values")
        
        for coord in coordinates:
            if not isinstance(coord, (int, float)):
                self._errors.append("Coordinate values must be numeric")
        
        return len(self._errors) == 0, self._errors

    def validate_config(self, config: Dict[str, Any]) -> ValidationResult:
        """Validate a configuration.

        Args:
            config: Configuration dictionary

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = validator.validate_config({"key": "value"})
        """
        self.clear_errors()
        
        if not isinstance(config, dict):
            self._errors.append("Configuration must be a dictionary")
            return False, self._errors
        
        return True, []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Validator state

        Example:
            >>> data = validator.to_dict()
        """
        return {
            "errors": self._errors.copy(),
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(validator)
        """
        return f"ScientificValidator(errors={len(self._errors)})"


# Export
__all__ = [
    "ScientificValidator",
]
