"""
Scientific Enums Module

This module provides enumerations for the Scientific package.

Purpose
-------
Provide type-safe enumerations for scientific operations.

Responsibilities
----------------
- Define unit system enumerations
- Define dimension enumerations
- Define quantity type enumerations
- Define coordinate system enumerations
- Define reference frame enumerations

Dependencies
------------
enum (standard library)
"""

from __future__ import annotations

from enum import Enum


class UnitSystem(Enum):
    """Enumeration of unit systems.

    This class defines supported unit systems.

    Attributes:
        SI: International System of Units
        CGS: Centimeter-Gram-Second system
        IMPERIAL: Imperial system
        CUSTOM: Custom unit system

    Example:
        >>> system = UnitSystem.SI
    """
    SI = "si"
    CGS = "cgs"
    IMPERIAL = "imperial"
    CUSTOM = "custom"


class DimensionType(Enum):
    """Enumeration of dimension types.

    This class defines supported dimension types.

    Attributes:
        LENGTH: Length dimension
        MASS: Mass dimension
        TIME: Time dimension
        TEMPERATURE: Temperature dimension
        CHARGE: Charge dimension
        ENERGY: Energy dimension
        FORCE: Force dimension
        POWER: Power dimension
        INFORMATION: Information dimension
        FREQUENCY: Frequency dimension
        PROBABILITY: Probability dimension
        DIMENSIONLESS: Dimensionless quantity

    Example:
        >>> dim = DimensionType.LENGTH
    """
    LENGTH = "length"
    MASS = "mass"
    TIME = "time"
    TEMPERATURE = "temperature"
    CHARGE = "charge"
    ENERGY = "energy"
    FORCE = "force"
    POWER = "power"
    INFORMATION = "information"
    FREQUENCY = "frequency"
    PROBABILITY = "probability"
    DIMENSIONLESS = "dimensionless"


class QuantityType(Enum):
    """Enumeration of quantity types.

    This class defines supported quantity types.

    Attributes:
        SCALAR: Scalar quantity
        VECTOR: Vector quantity
        TENSOR: Tensor quantity

    Example:
        >>> qtype = QuantityType.SCALAR
    """
    SCALAR = "scalar"
    VECTOR = "vector"
    TENSOR = "tensor"


class CoordinateSystem(Enum):
    """Enumeration of coordinate systems.

    This class defines supported coordinate systems.

    Attributes:
        CARTESIAN: Cartesian coordinates
        POLAR: Polar coordinates
        CYLINDRICAL: Cylindrical coordinates
        SPHERICAL: Spherical coordinates
        GALACTIC: Galactic coordinates
        EQUATORIAL: Equatorial coordinates

    Example:
        >>> coords = CoordinateSystem.CARTESIAN
    """
    CARTESIAN = "cartesian"
    POLAR = "polar"
    CYLINDRICAL = "cylindrical"
    SPHERICAL = "spherical"
    GALACTIC = "galactic"
    EQUATORIAL = "equatorial"


class ReferenceFrameType(Enum):
    """Enumeration of reference frame types.

    This class defines supported reference frame types.

    Attributes:
        INERTIAL: Inertial reference frame
        ROTATING: Rotating reference frame
        QUANTUM: Quantum reference frame

    Example:
        >>> frame = ReferenceFrameType.INERTIAL
    """
    INERTIAL = "inertial"
    ROTATING = "rotating"
    QUANTUM = "quantum"


class TimeType(Enum):
    """Enumeration of time types.

    This class defines supported time types.

    Attributes:
        PHYSICAL: Physical time
        SIMULATION: Simulation time
        LOGICAL: Logical time

    Example:
        >>> ttype = TimeType.PHYSICAL
    """
    PHYSICAL = "physical"
    SIMULATION = "simulation"
    LOGICAL = "logical"


class ScaleType(Enum):
    """Enumeration of scale types.

    This class defines supported scale types.

    Attributes:
        LINEAR: Linear scale
        LOGARITHMIC: Logarithmic scale
        EXPONENTIAL: Exponential scale

    Example:
        >>> scale = ScaleType.LINEAR
    """
    LINEAR = "linear"
    LOGARITHMIC = "logarithmic"
    EXPONENTIAL = "exponential"


class UncertaintyType(Enum):
    """Enumeration of uncertainty types.

    This class defines supported uncertainty types.

    Attributes:
        ABSOLUTE: Absolute uncertainty
        RELATIVE: Relative uncertainty
        STATISTICAL: Statistical uncertainty
        SYSTEMATIC: Systematic uncertainty

    Example:
        >>> utype = UncertaintyType.ABSOLUTE
    """
    ABSOLUTE = "absolute"
    RELATIVE = "relative"
    STATISTICAL = "statistical"
    SYSTEMATIC = "systematic"


class PrecisionType(Enum):
    """Enumeration of precision types.

    This class defines supported precision types.

    Attributes:
        SINGLE: Single precision
        DOUBLE: Double precision
        ARBITRARY: Arbitrary precision

    Example:
        >>> ptype = PrecisionType.DOUBLE
    """
    SINGLE = "single"
    DOUBLE = "double"
    ARBITRARY = "arbitrary"


class ConstantCategory(Enum):
    """Enumeration of constant categories.

    This class defines supported constant categories.

    Attributes:
        PHYSICAL: Physical constants
        ASTRONOMICAL: Astronomical constants
        MATHEMATICAL: Mathematical constants

    Example:
        >>> category = ConstantCategory.PHYSICAL
    """
    PHYSICAL = "physical"
    ASTRONOMICAL = "astronomical"
    MATHEMATICAL = "mathematicical"


# Export
__all__ = [
    "UnitSystem",
    "DimensionType",
    "QuantityType",
    "CoordinateSystem",
    "ReferenceFrameType",
    "TimeType",
    "ScaleType",
    "UncertaintyType",
    "PrecisionType",
    "ConstantCategory",
]
