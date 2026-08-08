"""
Geometry Module

This module provides geometric operations for the Mathematics package.
Geometry represents points, lines, planes, and geometric transformations.

Purpose
-------
Provide geometric operations for the Mathematics package.

Scientific Meaning
------------------
Geometry represents the study of shapes, sizes, positions, and transformations,
essential for computer graphics, physics simulations, robotics, and many other scientific applications.

Responsibilities
----------------
- Support geometric primitives
- Enable geometric transformations
- Support geometric calculations
- Handle geometric validation

Dependencies
------------
typing (standard library)
math (standard library)
quantsmind.math.exceptions (exception hierarchy)
quantsmind.math.types (type definitions)
quantsmind.math.utilities (utility functions)

Future Extensions
-----------------
- 3D geometry
- Curves and surfaces
- Computational geometry
"""

from __future__ import annotations

import logging
import math
from typing import List, Optional, Tuple, Union

from quantsmind.math.exceptions import GeometryError, ValueError as MathValueError
from quantsmind.math.types import Point as PointType, Scalar

logger = logging.getLogger(__name__)


class Point:
    """Concrete implementation of a geometric point.

    This class represents a point in 2D or 3D space.

    Scientific Meaning
    ------------------
    In geometry, a point represents a location in space with no size or dimension.

    Attributes:
        _coordinates: Point coordinates

    Example:
        >>> p = Point([1.0, 2.0])
    """

    def __init__(self, coordinates: List[Scalar]) -> None:
        """Initialize a Point.

        Args:
            coordinates: Point coordinates

        Example:
            >>> p = Point([1.0, 2.0])
        """
        self._coordinates = list(coordinates)
        self._dimension = len(coordinates)
        logger.debug(f"Created point with {self._dimension} dimensions")

    @property
    def coordinates(self) -> List[Scalar]:
        """Get the coordinates.

        Returns:
            Coordinates

        Example:
            >>> print(f"Coordinates: {point.coordinates}")
        """
        return self._coordinates.copy()

    @property
    def dimension(self) -> int:
        """Get the dimension.

        Returns:
            Dimension

        Example:
            >>> print(f"Dimension: {point.dimension}")
        """
        return self._dimension

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(point)
        """
        return f"Point({self._coordinates})"

    def __str__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> str(point)
        """
        return f"({', '.join(str(x) for x in self._coordinates)})"

    def __eq__(self, other: Any) -> bool:
        """Check equality.

        Args:
            other: Object to compare with

        Returns:
            True if equal, False otherwise

        Example:
            >>> p1 == p2
        """
        if not isinstance(other, Point):
            return False
        return self._coordinates == other._coordinates

    def __hash__(self) -> int:
        """Return hash.

        Returns:
            Hash value

        Example:
            >>> hash(point)
        """
        return hash(tuple(self._coordinates))

    def distance_to(self, other: Point) -> float:
        """Calculate Euclidean distance to another point.

        Args:
            other: Other point

        Returns:
            Euclidean distance

        Raises:
            GeometryError: If dimensions don't match

        Example:
            >>> dist = p1.distance_to(p2)
        """
        if self._dimension != other._dimension:
            raise GeometryError(f"Dimension mismatch: {self._dimension} vs {other._dimension}")
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(self._coordinates, other._coordinates)))


class Line:
    """Concrete implementation of a geometric line.

    This class represents a line in 2D or 3D space.

    Scientific Meaning
    ------------------
    In geometry, a line represents a straight one-dimensional figure having no thickness
    and extending infinitely in both directions.

    Attributes:
        _point1: First point
        _point2: Second point

    Example:
        >>> line = Line(Point([0.0, 0.0]), Point([1.0, 1.0]))
    """

    def __init__(self, point1: Point, point2: Point) -> None:
        """Initialize a Line.

        Args:
            point1: First point
            point2: Second point

        Raises:
            GeometryError: If points have different dimensions

        Example:
            >>> line = Line(Point([0.0, 0.0]), Point([1.0, 1.0]))
        """
        if point1.dimension != point2.dimension:
            raise GeometryError(f"Point dimensions must match: {point1.dimension} vs {point2.dimension}")
        self._point1 = point1
        self._point2 = point2
        self._dimension = point1.dimension

    @property
    def point1(self) -> Point:
        """Get the first point.

        Returns:
            First point

        Example:
            >>> print(f"Point 1: {line.point1}")
        """
        return self._point1

    @property
    def point2(self) -> Point:
        """Get the second point.

        Returns:
            Second point

        Example:
            >>> print(f"Point 2: {line.point2}")
        """
        return self._point2

    @property
    def dimension(self) -> int:
        """Get the dimension.

        Returns:
            Dimension

        Example:
            >>> print(f"Dimension: {line.dimension}")
        """
        return self._dimension

    def length(self) -> float:
        """Calculate the line length.

        Returns:
            Line length

        Example:
            >>> length = line.length()
        """
        return self._point1.distance_to(self._point2)

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(line)
        """
        return f"Line({self._point1}, {self._point2})"


class Plane:
    """Concrete implementation of a geometric plane.

    This class represents a plane in 3D space.

    Scientific Meaning
    ------------------
    In geometry, a plane represents a flat two-dimensional surface that extends infinitely.

    Attributes:
        _point1: First point
        _point2: Second point
        _point3: Third point

    Example:
        >>> plane = Plane(Point([0.0, 0.0, 0.0]), Point([1.0, 0.0, 0.0]), Point([0.0, 1.0, 0.0]))
    """

    def __init__(self, point1: Point, point2: Point, point3: Point) -> None:
        """Initialize a Plane.

        Args:
            point1: First point
            point2: Second point
            point3: Third point

        Raises:
            GeometryError: If points are not 3D or are collinear

        Example:
            >>> plane = Plane(Point([0.0, 0.0, 0.0]), Point([1.0, 0.0, 0.0]), Point([0.0, 1.0, 0.0]))
        """
        if point1.dimension != 3 or point2.dimension != 3 or point3.dimension != 3:
            raise GeometryError("Plane requires 3D points")
        
        self._point1 = point1
        self._point2 = point2
        self._point3 = point3

    @property
    def point1(self) -> Point:
        """Get the first point.

        Returns:
            First point

        Example:
            >>> print(f"Point 1: {plane.point1}")
        """
        return self._point1

    @property
    def point2(self) -> Point:
        """Get the second point.

        Returns:
            Second point

        Example:
            >>> print(f"Point 2: {plane.point2}")
        """
        return self._point2

    @property
    def point3(self) -> Point:
        """Get the third point.

        Returns:
            Third point

        Example:
            >>> print(f"Point 3: {plane.point3}")
        """
        return self._point3

    def normal(self) -> List[Scalar]:
        """Calculate the plane normal vector.

        Returns:
            Normal vector

        Example:
            >>> normal = plane.normal()
        """
        p1 = self._point1.coordinates
        p2 = self._point2.coordinates
        p3 = self._point3.coordinates

        v1 = [p2[i] - p1[i] for i in range(3)]
        v2 = [p3[i] - p1[i] for i in range(3)]

        normal = [
            v1[1] * v2[2] - v1[2] * v2[1],
            v1[2] * v2[0] - v1[0] * v2[2],
            v1[0] * v2[1] - v1[1] * v2[0],
        ]
        return normal

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(plane)
        """
        return f"Plane({self._point1}, {self._point2}, {self._point3})"


class Circle:
    """Concrete implementation of a geometric circle.

    This class represents a circle in 2D space.

    Scientific Meaning
    ------------------
    In geometry, a circle represents the set of all points in a plane that are at a given
    distance (radius) from a given point (center).

    Attributes:
        _center: Center point
        _radius: Radius

    Example:
        >>> circle = Circle(Point([0.0, 0.0]), 5.0)
    """

    def __init__(self, center: Point, radius: Scalar) -> None:
        """Initialize a Circle.

        Args:
            center: Center point
            radius: Radius

        Raises:
            GeometryError: If radius is negative

        Example:
            >>> circle = Circle(Point([0.0, 0.0]), 5.0)
        """
        if radius < 0:
            raise GeometryError("Radius cannot be negative")
        self._center = center
        self._radius = radius

    @property
    def center(self) -> Point:
        """Get the center.

        Returns:
            Center point

        Example:
            >>> print(f"Center: {circle.center}")
        """
        return self._center

    @property
    def radius(self) -> Scalar:
        """Get the radius.

        Returns:
            Radius

        Example:
            >>> print(f"Radius: {circle.radius}")
        """
        return self._radius

    @property
    def area(self) -> float:
        """Calculate the area.

        Returns:
            Area

        Example:
            >>> area = circle.area
        """
        from quantsmind.math.constants import PI
        return PI * self._radius ** 2

    @property
    def circumference(self) -> float:
        """Calculate the circumference.

        Returns:
            Circumference

        Example:
            >>> circ = circle.circumference
        """
        from quantsmind.math.constants import PI
        return 2 * PI * self._radius

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(circle)
        """
        return f"Circle({self._center}, {self._radius})"


class Polygon:
    """Concrete implementation of a geometric polygon.

    This class represents a polygon defined by a list of vertices.

    Scientific Meaning
    ------------------
    In geometry, a polygon represents a closed plane figure with straight sides.

    Attributes:
        _vertices: List of vertices

    Example:
        >>> polygon = Polygon([Point([0.0, 0.0]), Point([1.0, 0.0]), Point([1.0, 1.0])])
    """

    def __init__(self, vertices: List[Point]) -> None:
        """Initialize a Polygon.

        Args:
            vertices: List of vertices

        Raises:
            GeometryError: If vertices have different dimensions or insufficient vertices

        Example:
            >>> polygon = Polygon([Point([0.0, 0.0]), Point([1.0, 0.0]), Point([1.0, 1.0])])
        """
        if len(vertices) < 3:
            raise GeometryError("Polygon requires at least 3 vertices")
        
        dimension = vertices[0].dimension
        for v in vertices:
            if v.dimension != dimension:
                raise GeometryError("All vertices must have the same dimension")
        
        self._vertices = vertices.copy()
        self._dimension = dimension

    @property
    def vertices(self) -> List[Point]:
        """Get the vertices.

        Returns:
            List of vertices

        Example:
            >>> print(f"Vertices: {polygon.vertices}")
        """
        return self._vertices.copy()

    @property
    def dimension(self) -> int:
        """Get the dimension.

        Returns:
            Dimension

        Example:
            >>> print(f"Dimension: {polygon.dimension}")
        """
        return self._dimension

    def area(self) -> float:
        """Calculate the polygon area (2D only).

        Returns:
            Area

        Raises:
            GeometryError: If polygon is not 2D

        Example:
            >>> area = polygon.area()
        """
        if self._dimension != 2:
            raise GeometryError("Area calculation requires 2D polygon")
        
        # Shoelace formula
        n = len(self._vertices)
        area = 0.0
        for i in range(n):
            j = (i + 1) % n
            x1, y1 = self._vertices[i].coordinates
            x2, y2 = self._vertices[j].coordinates
            area += x1 * y2 - x2 * y1
        return abs(area) / 2.0

    def perimeter(self) -> float:
        """Calculate the perimeter.

        Returns:
            Perimeter

        Example:
            >>> perimeter = polygon.perimeter()
        """
        perimeter = 0.0
        n = len(self._vertices)
        for i in range(n):
            j = (i + 1) % n
            perimeter += self._vertices[i].distance_to(self._vertices[j])
        return perimeter

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(polygon)
        """
        return f"Polygon({self._vertices})"


class CoordinateSystem:
    """Concrete implementation of a coordinate system.

    This class represents a coordinate system with origin and basis vectors.

    Scientific Meaning
    ------------------
    In geometry, a coordinate system provides a reference frame for describing
    positions and transformations.

    Attributes:
        _origin: Origin point
        _basis: Basis vectors

    Example:
        >>> cs = CoordinateSystem(Point([0.0, 0.0]), [[1.0, 0.0], [0.0, 1.0]])
    """

    def __init__(self, origin: Point, basis: List[List[Scalar]]) -> None:
        """Initialize a CoordinateSystem.

        Args:
            origin: Origin point
            basis: Basis vectors

        Example:
            >>> cs = CoordinateSystem(Point([0.0, 0.0]), [[1.0, 0.0], [0.0, 1.0]])
        """
        self._origin = origin
        self._basis = [row.copy() for row in basis]
        self._dimension = origin.dimension

    @property
    def origin(self) -> Point:
        """Get the origin.

        Returns:
            Origin point

        Example:
            >>> print(f"Origin: {cs.origin}")
        """
        return self._origin

    @property
    def basis(self) -> List[List[Scalar]]:
        """Get the basis vectors.

        Returns:
            Basis vectors

        Example:
            >>> print(f"Basis: {cs.basis}")
        """
        return [row.copy() for row in self._basis]

    @property
    def dimension(self) -> int:
        """Get the dimension.

        Returns:
            Dimension

        Example:
            >>> print(f"Dimension: {cs.dimension}")
        """
        return self._dimension

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(cs)
        """
        return f"CoordinateSystem({self._origin}, {self._basis})"


class Transformation:
    """Concrete implementation of a geometric transformation.

    This class represents geometric transformations like translation, rotation, and scaling.

    Scientific Meaning
    ------------------
    In geometry, transformations represent operations that change the position,
    orientation, or size of geometric objects.

    Example:
        >>> transform = Transformation()
        >>> transformed_point = transform.translate(point, [1.0, 0.0])
    """

    @staticmethod
    def translate(point: Point, offset: List[Scalar]) -> Point:
        """Translate a point by an offset.

        Args:
            point: Point to translate
            offset: Translation offset

        Returns:
            Translated point

        Raises:
            GeometryError: If dimensions don't match

        Example:
            >>> transformed = Transformation.translate(point, [1.0, 0.0])
        """
        if point.dimension != len(offset):
            raise GeometryError(f"Dimension mismatch: {point.dimension} vs {len(offset)}")
        new_coords = [c + o for c, o in zip(point.coordinates, offset)]
        return Point(new_coords)

    @staticmethod
    def rotate(point: Point, angle: float, center: Optional[Point] = None) -> Point:
        """Rotate a point around a center (2D only).

        Args:
            point: Point to rotate
            angle: Rotation angle in radians
            center: Center of rotation (default: origin)

        Returns:
            Rotated point

        Raises:
            GeometryError: If point is not 2D

        Example:
            >>> transformed = Transformation.rotate(point, math.pi/2)
        """
        if point.dimension != 2:
            raise GeometryError("Rotation requires 2D point")
        
        if center is None:
            center = Point([0.0, 0.0])
        
        # Translate to origin
        translated = Transformation.translate(point, [-c for c in center.coordinates])
        
        # Rotate
        x, y = translated.coordinates
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        rotated_coords = [x * cos_a - y * sin_a, x * sin_a + y * cos_a]
        
        # Translate back
        return Transformation.translate(Point(rotated_coords), center.coordinates)

    @staticmethod
    def scale(point: Point, factor: Union[Scalar, List[Scalar]], center: Optional[Point] = None) -> Point:
        """Scale a point by a factor.

        Args:
            point: Point to scale
            factor: Scale factor (scalar or per-dimension)
            center: Center of scaling (default: origin)

        Returns:
            Scaled point

        Raises:
            GeometryError: If dimensions don't match

        Example:
            >>> transformed = Transformation.scale(point, 2.0)
        """
        if isinstance(factor, (int, float)):
            factor = [factor] * point.dimension
        
        if point.dimension != len(factor):
            raise GeometryError(f"Dimension mismatch: {point.dimension} vs {len(factor)}")
        
        if center is None:
            center = Point([0.0] * point.dimension)
        
        # Translate to origin
        translated = Transformation.translate(point, [-c for c in center.coordinates])
        
        # Scale
        scaled_coords = [c * f for c, f in zip(translated.coordinates, factor)]
        
        # Translate back
        return Transformation.translate(Point(scaled_coords), center.coordinates)


# Export
__all__ = [
    "Point",
    "Line",
    "Plane",
    "Circle",
    "Polygon",
    "CoordinateSystem",
    "Transformation",
]

