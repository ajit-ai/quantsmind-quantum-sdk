"""
Scientific Types Module

This module provides type definitions for the Scientific package.

Purpose
-------
Provide type aliases and type hints for scientific operations.

Responsibilities
----------------
- Define type aliases for units
- Define type aliases for dimensions
- Define type aliases for quantities
- Define type aliases for measurements
- Define type aliases for coordinates
- Define type aliases for time

Dependencies
------------
typing (standard library)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple, Union

# Unit types
UnitName = str
UnitSymbol = str
ConversionFactor = float
UnitDefinition = Dict[str, Union[str, float]]

# Dimension types
DimensionName = str
DimensionPower = int
DimensionVector = Tuple[int, int, int, int, int, int, int]  # L, M, T, Θ, I, N, J

# Quantity types
QuantityValue = Union[int, float]
QuantityVector = List[QuantityValue]
QuantityTensor = List[List[QuantityValue]]

# Measurement types
MeasurementValue = Union[int, float]
UncertaintyValue = Union[int, float]
ConfidenceLevel = float
ToleranceValue = Union[int, float]

# Coordinate types
CoordinateValue = Union[int, float]
CoordinateTuple = Tuple[CoordinateValue, CoordinateValue]
CoordinateTriple = Tuple[CoordinateValue, CoordinateValue, CoordinateValue]

# Time types
TimestampValue = Union[int, float]
DurationValue = Union[int, float]
EpochValue = Union[int, float]

# Scale types
ScaleValue = Union[int, float]
ScaleRange = Tuple[ScaleValue, ScaleValue]

# Constant types
ConstantName = str
ConstantValue = Union[int, float]
ConstantDefinition = Dict[str, Union[str, float, List[str]]]

# Metadata types
MetadataKey = str
MetadataValue = Any
MetadataDict = Dict[MetadataKey, MetadataValue]

# Validation types
ValidationResult = Tuple[bool, List[str]]
ValidationError = str

# Serialization types
SerializationFormat = str
SerializedData = Union[str, bytes, Dict[str, Any]]

# Observer types
ObserverID = str
ObservableID = str
ObservationID = str

# Reference frame types
FrameID = str
FrameTransform = Dict[str, Any]

# Export
__all__ = [
    # Unit types
    "UnitName",
    "UnitSymbol",
    "ConversionFactor",
    "UnitDefinition",
    # Dimension types
    "DimensionName",
    "DimensionPower",
    "DimensionVector",
    # Quantity types
    "QuantityValue",
    "QuantityVector",
    "QuantityTensor",
    # Measurement types
    "MeasurementValue",
    "UncertaintyValue",
    "ConfidenceLevel",
    "ToleranceValue",
    # Coordinate types
    "CoordinateValue",
    "CoordinateTuple",
    "CoordinateTriple",
    # Time types
    "TimestampValue",
    "DurationValue",
    "EpochValue",
    # Scale types
    "ScaleValue",
    "ScaleRange",
    # Constant types
    "ConstantName",
    "ConstantValue",
    "ConstantDefinition",
    # Metadata types
    "MetadataKey",
    "MetadataValue",
    "MetadataDict",
    # Validation types
    "ValidationResult",
    "ValidationError",
    # Serialization types
    "SerializationFormat",
    "SerializedData",
    # Observer types
    "ObserverID",
    "ObservableID",
    "ObservationID",
    # Reference frame types
    "FrameID",
    "FrameTransform",
]
