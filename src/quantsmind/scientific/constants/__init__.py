"""
Constants Package

This package provides constant management for the Scientific package.

Purpose
-------
Provide comprehensive constant definitions and access.

Modules
-------
- physical_constants: Physical constants
- astronomical_constants: Astronomical constants
- mathematical_constants: Mathematical constants
"""

from __future__ import annotations

from quantsmind.scientific.constants.astronomical_constants import AstronomicalConstants
from quantsmind.scientific.constants.mathematical_constants import MathematicalConstants
from quantsmind.scientific.constants.physical_constants import ConstantDefinition, PhysicalConstants

__all__ = [
    "PhysicalConstants",
    "AstronomicalConstants",
    "MathematicalConstants",
    "ConstantDefinition",
]
