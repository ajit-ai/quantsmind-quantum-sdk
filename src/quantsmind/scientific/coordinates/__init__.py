"""
Coordinates Package

This package provides coordinate system management for the Scientific package.

Purpose
-------
Provide comprehensive coordinate system definitions and transformations.

Modules
-------
- cartesian: Cartesian coordinates
- polar: Polar coordinates
- cylindrical: Cylindrical coordinates
- spherical: Spherical coordinates
- galactic: Galactic coordinates
- equatorial: Equatorial coordinates
"""

from __future__ import annotations

from quantsmind.scientific.coordinates.cartesian import CartesianCoordinate
from quantsmind.scientific.coordinates.cylindrical import CylindricalCoordinate
from quantsmind.scientific.coordinates.equatorial import EquatorialCoordinate
from quantsmind.scientific.coordinates.galactic import GalacticCoordinate
from quantsmind.scientific.coordinates.polar import PolarCoordinate
from quantsmind.scientific.coordinates.spherical import SphericalCoordinate

__all__ = [
    "CartesianCoordinate",
    "PolarCoordinate",
    "CylindricalCoordinate",
    "SphericalCoordinate",
    "GalacticCoordinate",
    "EquatorialCoordinate",
]
