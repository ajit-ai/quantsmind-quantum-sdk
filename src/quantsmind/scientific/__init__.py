"""
Scientific Package — Universal Scientific Abstraction Layer for QuantsMind SDK

This package provides the foundation for all scientific domain packages including
Quantum Computing, Physics, Chemistry, Biology, Astronomy, AI, Finance,
Simulation, and Optimization.

This package is part of the QuantsMind SDK (R0.6.0).

Purpose
-------
Provide a unified scientific abstraction layer for all QuantsMind domain packages.

Scientific Philosophy
---------------------
Everything observable follows the same lifecycle:
Entity → Property → Quantity → Measurement → Observation → Knowledge → Prediction

Modules
-------
- exceptions: Scientific exception hierarchy
- enums: Scientific enumerations
- types: Type definitions for scientific objects
- interfaces: Abstract interfaces for scientific components
- protocols: Structural subtyping protocols
- units: Unit management (base_unit, si_units, derived_units, custom_units)
- dimensions: Dimension management (dimension, dimensional_analysis)
- quantities: Quantity management (quantity, scalar, vector_quantity, tensor_quantity)
- measurements: Measurement management (measurement, uncertainty, tolerance, precision, accuracy)
- observables: Observable management (observable, observation, observer)
- coordinates: Coordinate systems (cartesian, polar, cylindrical, spherical, galactic, equatorial)
- reference_frames: Reference frames (reference_frame, inertial, rotating, quantum_frame)
- time: Time management (timestamp, duration, epoch, simulation_time, logical_time)
- constants: Constants (physical_constants, astronomical_constants, mathematical_constants)
- scales: Scale management (scale, logarithmic, linear)
- metadata: Metadata management
- validation: Validation functions
- serialization: Serialization functions
- factories: Factory methods
"""

from __future__ import annotations

# Foundational modules
from quantsmind.scientific import exceptions
from quantsmind.scientific import enums
from quantsmind.scientific import interfaces
from quantsmind.scientific import protocols
from quantsmind.scientific import types

# Units
from quantsmind.scientific.units import (
    BaseUnit,
    CustomUnit,
    CustomUnitsRegistry,
    DerivedUnit,
    DerivedUnitsRegistry,
    SIUnits,
)

# Dimensions
from quantsmind.scientific.dimensions import Dimension, DimensionalAnalysis

# Quantities
from quantsmind.scientific.quantities import Quantity, ScalarQuantity, TensorQuantity, VectorQuantity

# Measurements
from quantsmind.scientific.measurements import Accuracy, Measurement, Precision, Tolerance, Uncertainty

# Observables
from quantsmind.scientific.observables import Observable, Observation, ObservationRecord, Observer

# Coordinates
from quantsmind.scientific.coordinates import (
    CartesianCoordinate,
    CylindricalCoordinate,
    EquatorialCoordinate,
    GalacticCoordinate,
    PolarCoordinate,
    SphericalCoordinate,
)

# Reference frames
from quantsmind.scientific.reference_frames import (
    InertialFrame,
    QuantumReferenceFrame,
    ReferenceFrame,
    RotatingFrame,
)

# Time
from quantsmind.scientific.time import Duration, Epoch, LogicalTime, SimulationTime, Timestamp

# Constants
from quantsmind.scientific.constants import (
    AstronomicalConstants,
    ConstantDefinition,
    MathematicalConstants,
    PhysicalConstants,
)

# Scales
from quantsmind.scientific.scales import LinearScale, LogarithmicScale, Scale

# Support modules
from quantsmind.scientific.factories import ScientificFactory
from quantsmind.scientific.metadata import ScientificMetadata
from quantsmind.scientific.serialization import JsonSerializer, Serializer
from quantsmind.scientific.validation import ScientificValidator

__version__ = "R0.6.0"

__all__ = [
    # Foundational modules
    "exceptions",
    "enums",
    "types",
    "interfaces",
    "protocols",
    # Units
    "BaseUnit",
    "SIUnits",
    "DerivedUnit",
    "DerivedUnitsRegistry",
    "CustomUnit",
    "CustomUnitsRegistry",
    # Dimensions
    "Dimension",
    "DimensionalAnalysis",
    # Quantities
    "Quantity",
    "ScalarQuantity",
    "VectorQuantity",
    "TensorQuantity",
    # Measurements
    "Measurement",
    "Uncertainty",
    "Tolerance",
    "Precision",
    "Accuracy",
    # Observables
    "Observable",
    "Observation",
    "ObservationRecord",
    "Observer",
    # Coordinates
    "CartesianCoordinate",
    "PolarCoordinate",
    "CylindricalCoordinate",
    "SphericalCoordinate",
    "GalacticCoordinate",
    "EquatorialCoordinate",
    # Reference frames
    "ReferenceFrame",
    "InertialFrame",
    "RotatingFrame",
    "QuantumReferenceFrame",
    # Time
    "Timestamp",
    "Duration",
    "Epoch",
    "SimulationTime",
    "LogicalTime",
    # Constants
    "PhysicalConstants",
    "AstronomicalConstants",
    "MathematicalConstants",
    "ConstantDefinition",
    # Scales
    "Scale",
    "LinearScale",
    "LogarithmicScale",
    # Support modules
    "ScientificMetadata",
    "ScientificValidator",
    "JsonSerializer",
    "Serializer",
    "ScientificFactory",
    "__version__",
]
