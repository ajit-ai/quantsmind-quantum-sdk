"""
Scientific Exceptions Module

This module provides exception hierarchy for the Scientific package.

Purpose
-------
Provide comprehensive exception handling for scientific operations.

Responsibilities
----------------
- Define scientific-specific exceptions
- Support contextual error information
- Provide detailed error messages
- Support error chaining

Dependencies
------------
typing (standard library)
"""

from __future__ import annotations

from typing import Any, Dict, Optional


class ScientificError(Exception):
    """Base exception for all scientific errors.

    This class provides the foundation for all scientific exceptions.

    Attributes:
        message: Error message
        context: Additional context information

    Example:
        >>> raise ScientificError("Operation failed")
    """

    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Initialize a ScientificError.

        Args:
            message: Error message
            context: Additional context information

        Example:
            >>> raise ScientificError("Operation failed")
        """
        super().__init__(message)
        self.message = message
        self.context = context or {}

    def __str__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> str(error)
        """
        if self.context:
            return f"{self.message} | Context: {self.context}"
        return self.message


class UnitError(ScientificError):
    """Exception raised for unit-related errors.

    This class handles errors related to unit operations.

    Attributes:
        unit: Unit that caused the error

    Example:
        >>> raise UnitError("Invalid unit conversion", unit="meter")
    """

    def __init__(self, message: str, unit: Optional[str] = None, context: Optional[Dict[str, Any]] = None) -> None:
        """Initialize a UnitError.

        Args:
            message: Error message
            unit: Unit that caused the error
            context: Additional context information

        Example:
            >>> raise UnitError("Invalid unit conversion", unit="meter")
        """
        super().__init__(message, context)
        self.unit = unit


class DimensionError(ScientificError):
    """Exception raised for dimension-related errors.

    This class handles errors related to dimensional analysis.

    Attributes:
        dimension: Dimension that caused the error

    Example:
        >>> raise DimensionError("Incompatible dimensions", dimension="length")
    """

    def __init__(self, message: str, dimension: Optional[str] = None, context: Optional[Dict[str, Any]] = None) -> None:
        """Initialize a DimensionError.

        Args:
            message: Error message
            dimension: Dimension that caused the error
            context: Additional context information

        Example:
            >>> raise DimensionError("Incompatible dimensions", dimension="length")
        """
        super().__init__(message, context)
        self.dimension = dimension


class QuantityError(ScientificError):
    """Exception raised for quantity-related errors.

    This class handles errors related to quantity operations.

    Attributes:
        quantity: Quantity that caused the error

    Example:
        >>> raise QuantityError("Invalid quantity operation")
    """

    def __init__(self, message: str, quantity: Optional[str] = None, context: Optional[Dict[str, Any]] = None) -> None:
        """Initialize a QuantityError.

        Args:
            message: Error message
            quantity: Quantity that caused the error
            context: Additional context information

        Example:
            >>> raise QuantityError("Invalid quantity operation")
        """
        super().__init__(message, context)
        self.quantity = quantity


class MeasurementError(ScientificError):
    """Exception raised for measurement-related errors.

    This class handles errors related to measurement operations.

    Attributes:
        measurement: Measurement that caused the error

    Example:
        >>> raise MeasurementError("Invalid measurement")
    """

    def __init__(self, message: str, measurement: Optional[str] = None, context: Optional[Dict[str, Any]] = None) -> None:
        """Initialize a MeasurementError.

        Args:
            message: Error message
            measurement: Measurement that caused the error
            context: Additional context information

        Example:
            >>> raise MeasurementError("Invalid measurement")
        """
        super().__init__(message, context)
        self.measurement = measurement


class CoordinateError(ScientificError):
    """Exception raised for coordinate-related errors.

    This class handles errors related to coordinate operations.

    Attributes:
        coordinate: Coordinate that caused the error

    Example:
        >>> raise CoordinateError("Invalid coordinate transformation")
    """

    def __init__(self, message: str, coordinate: Optional[str] = None, context: Optional[Dict[str, Any]] = None) -> None:
        """Initialize a CoordinateError.

        Args:
            message: Error message
            coordinate: Coordinate that caused the error
            context: Additional context information

        Example:
            >>> raise CoordinateError("Invalid coordinate transformation")
        """
        super().__init__(message, context)
        self.coordinate = coordinate


class ReferenceFrameError(ScientificError):
    """Exception raised for reference frame-related errors.

    This class handles errors related to reference frame operations.

    Attributes:
        frame: Reference frame that caused the error

    Example:
        >>> raise ReferenceFrameError("Invalid reference frame")
    """

    def __init__(self, message: str, frame: Optional[str] = None, context: Optional[Dict[str, Any]] = None) -> None:
        """Initialize a ReferenceFrameError.

        Args:
            message: Error message
            frame: Reference frame that caused the error
            context: Additional context information

        Example:
            >>> raise ReferenceFrameError("Invalid reference frame")
        """
        super().__init__(message, context)
        self.frame = frame


class TimeError(ScientificError):
    """Exception raised for time-related errors.

    This class handles errors related to time operations.

    Attributes:
        time_value: Time value that caused the error

    Example:
        >>> raise TimeError("Invalid time operation")
    """

    def __init__(self, message: str, time_value: Optional[str] = None, context: Optional[Dict[str, Any]] = None) -> None:
        """Initialize a TimeError.

        Args:
            message: Error message
            time_value: Time value that caused the error
            context: Additional context information

        Example:
            >>> raise TimeError("Invalid time operation")
        """
        super().__init__(message, context)
        self.time_value = time_value


class ConversionError(ScientificError):
    """Exception raised for conversion errors.

    This class handles errors related to unit conversions.

    Attributes:
        from_unit: Source unit
        to_unit: Target unit

    Example:
        >>> raise ConversionError("Cannot convert meter to second", from_unit="meter", to_unit="second")
    """

    def __init__(self, message: str, from_unit: Optional[str] = None, to_unit: Optional[str] = None, context: Optional[Dict[str, Any]] = None) -> None:
        """Initialize a ConversionError.

        Args:
            message: Error message
            from_unit: Source unit
            to_unit: Target unit
            context: Additional context information

        Example:
            >>> raise ConversionError("Cannot convert meter to second", from_unit="meter", to_unit="second")
        """
        super().__init__(message, context)
        self.from_unit = from_unit
        self.to_unit = to_unit


class ValidationError(ScientificError):
    """Exception raised for validation errors.

    This class handles errors related to validation operations.

    Attributes:
        field: Field that failed validation
        value: Value that failed validation

    Example:
        >>> raise ValidationError("Invalid value", field="temperature", value=-300)
    """

    def __init__(self, message: str, field: Optional[str] = None, value: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> None:
        """Initialize a ValidationError.

        Args:
            message: Error message
            field: Field that failed validation
            value: Value that failed validation
            context: Additional context information

        Example:
            >>> raise ValidationError("Invalid value", field="temperature", value=-300)
        """
        super().__init__(message, context)
        self.field = field
        self.value = value


# Export
__all__ = [
    "ScientificError",
    "UnitError",
    "DimensionError",
    "QuantityError",
    "MeasurementError",
    "CoordinateError",
    "ReferenceFrameError",
    "TimeError",
    "ConversionError",
    "ValidationError",
]
