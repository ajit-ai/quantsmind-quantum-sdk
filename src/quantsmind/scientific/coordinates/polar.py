"""
Polar Coordinate Module

This module provides polar coordinate definitions for the Scientific package.

Purpose
-------
Provide polar coordinate system implementation.

Responsibilities
----------------
- Define polar coordinates
- Support coordinate transformations
- Support coordinate operations
- Support coordinate validation

Dependencies
------------
typing (standard library)
math (standard library)
quantsmind.scientific.interfaces (scientific interfaces)
quantsmind.scientific.exceptions (scientific exceptions)
quantsmind.scientific.types (scientific types)
"""

from __future__ import annotations

import math
from typing import Any, Dict, Optional, Tuple

from quantsmind.scientific.exceptions import CoordinateError
from quantsmind.scientific.interfaces import ICoordinate
from quantsmind.scientific.types import CoordinateTriple, CoordinateValue


class PolarCoordinate(ICoordinate):
    """Concrete implementation of polar coordinates.

    This class provides polar coordinate functionality.

    Attributes:
        _r: Radial distance
        _theta: Angular coordinate (radians)
        _metadata: Coordinate metadata

    Example:
        >>> coord = PolarCoordinate(1.0, math.pi/4)
        >>> coord.coordinates()
    """

    def __init__(
        self,
        r: CoordinateValue,
        theta: CoordinateValue,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a PolarCoordinate.

        Args:
            r: Radial distance
            theta: Angular coordinate (radians)
            metadata: Coordinate metadata

        Example:
            >>> coord = PolarCoordinate(1.0, math.pi/4)
        """
        if r < 0:
            raise CoordinateError("Radial distance cannot be negative", coordinate="r")

        self._r = r
        self._theta = theta
        self._metadata = metadata or {}

    @property
    def r(self) -> CoordinateValue:
        """Get the radial distance.

        Returns:
            Radial distance

        Example:
            >>> print(f"R: {coord.r}")
        """
        return self._r

    @property
    def theta(self) -> CoordinateValue:
        """Get the angular coordinate.

        Returns:
            Angular coordinate (radians)

        Example:
            >>> print(f"Theta: {coord.theta}")
        """
        return self._theta

    @property
    def metadata(self) -> Dict[str, Any]:
        """Get the coordinate metadata.

        Returns:
            Coordinate metadata

        Example:
            >>> print(f"Metadata: {coord.metadata}")
        """
        return self._metadata.copy()

    def coordinates(self) -> CoordinateTriple:
        """Get the coordinate values.

        Returns:
            Coordinate values (r, theta, 0)

        Example:
            >>> coords = coord.coordinates()
        """
        return (self._r, self._theta, 0.0)

    def system(self) -> str:
        """Get the coordinate system.

        Returns:
            Coordinate system name

        Example:
            >>> print(f"System: {coord.system()}")
        """
        return "polar"

    def magnitude(self) -> float:
        """Calculate the magnitude.

        Returns:
            Magnitude (radial distance)

        Example:
            >>> mag = coord.magnitude()
        """
        return self._r

    def to_cartesian(self) -> Tuple[float, float]:
        """Convert to Cartesian coordinates (2D).

        Returns:
            Cartesian coordinates (x, y)

        Example:
            >>> x, y = coord.to_cartesian()
        """
        x = self._r * math.cos(self._theta)
        y = self._r * math.sin(self._theta)
        return (x, y)

    def transform_to(self, target_system: str) -> ICoordinate:
        """Transform to a different coordinate system.

        Args:
            target_system: Target coordinate system

        Returns:
            Transformed coordinate

        Raises:
            CoordinateError: If transformation not supported

        Example:
            >>> transformed = coord.transform_to("cartesian")
        """
        if target_system == "polar":
            return self
        elif target_system == "cartesian":
            from quantsmind.scientific.coordinates.cartesian import CartesianCoordinate
            x, y = self.to_cartesian()
            return CartesianCoordinate(x, y)
        elif target_system == "cylindrical":
            from quantsmind.scientific.coordinates.cylindrical import CylindricalCoordinate
            x, y = self.to_cartesian()
            return CylindricalCoordinate(self._r, self._theta, 0.0)
        else:
            raise CoordinateError(f"Transformation to {target_system} not supported")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Coordinate definition

        Example:
            >>> data = coord.to_dict()
        """
        return {
            "system": self.system(),
            "r": self._r,
            "theta": self._theta,
            "metadata": self._metadata.copy(),
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(coord)
        """
        return f"PolarCoordinate(r={self._r}, theta={self._theta})"


# Export
__all__ = [
    "PolarCoordinate",
]
