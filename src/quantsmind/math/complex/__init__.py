"""
Complex Numbers Module

This module provides complex number operations for the Mathematics package.
ComplexNumber represents a mathematical complex number with support for common operations.

Purpose
-------
Provide complex number operations for the Mathematics package.

Scientific Meaning
------------------
Complex numbers represent numbers with real and imaginary parts, essential for
quantum mechanics, signal processing, control theory, and many other scientific applications.

Responsibilities
----------------
- Support complex number creation
- Enable complex number operations
- Support complex number transformations
- Handle complex number validation

Dependencies
------------
math (standard library)
typing (standard library)
quantsmind.math.constants (mathematical constants)
quantsmind.math.types (type definitions)

Future Extensions
-----------------
- Complex matrix operations
- Complex tensor operations
- Quaternion support
"""

from __future__ import annotations

import logging
import math
from typing import Any, List, Tuple, Union

from quantsmind.math.constants import PI
from quantsmind.math.types import Complex, Float, Scalar

logger = logging.getLogger(__name__)


class ComplexNumber:
    """Concrete implementation of a complex number.

    This class provides a comprehensive complex number representation with support for
    common complex number operations including addition, subtraction, multiplication,
    division, conjugation, and conversion between polar and Cartesian forms.

    Scientific Meaning
    ------------------
    In scientific computing, complex numbers are essential for quantum mechanics
    (wave functions), signal processing (Fourier transforms), control theory,
    and many other applications.

    Attributes:
        _real: Real part
        _imag: Imaginary part

    Example:
        >>> z = ComplexNumber(1.0, 2.0)
        >>> print(f"Magnitude: {z.magnitude()}")
    """

    def __init__(self, real: Float = 0.0, imag: Float = 0.0) -> None:
        """Initialize a ComplexNumber.

        Args:
            real: Real part
            imag: Imaginary part

        Example:
            >>> z = ComplexNumber(1.0, 2.0)
        """
        self._real: Float = float(real)
        self._imag: Float = float(imag)
        logger.debug(f"Created complex number: {self._real} + {self._imag}i")

    @property
    def real(self) -> Float:
        """Get the real part.

        Returns:
            Real part

        Example:
            >>> print(f"Real: {complex_number.real}")
        """
        return self._real

    @property
    def imag(self) -> Float:
        """Get the imaginary part.

        Returns:
            Imaginary part

        Example:
            >>> print(f"Imaginary: {complex_number.imag}")
        """
        return self._imag

    @property
    def magnitude(self) -> Float:
        """Get the magnitude (absolute value).

        Returns:
            Magnitude

        Example:
            >>> print(f"Magnitude: {complex_number.magnitude}")
        """
        return math.sqrt(self._real ** 2 + self._imag ** 2)

    @property
    def phase(self) -> Float:
        """Get the phase (argument) in radians.

        Returns:
            Phase in radians

        Example:
            >>> print(f"Phase: {complex_number.phase}")
        """
        return math.atan2(self._imag, self._real)

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(complex_number)
        """
        return f"ComplexNumber({self._real}, {self._imag})"

    def __str__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> str(complex_number)
        """
        if self._imag >= 0:
            return f"{self._real} + {self._imag}i"
        else:
            return f"{self._real} - {abs(self._imag)}i"

    def __eq__(self, other: Any) -> bool:
        """Check equality.

        Args:
            other: Object to compare with

        Returns:
            True if equal, False otherwise

        Example:
            >>> z1 == z2
        """
        if isinstance(other, ComplexNumber):
            return self._real == other._real and self._imag == other._imag
        if isinstance(other, complex):
            return self._real == other.real and self._imag == other.imag
        return False

    def __hash__(self) -> int:
        """Return hash.

        Returns:
            Hash value

        Example:
            >>> hash(complex_number)
        """
        return hash((self._real, self._imag))

    def __add__(self, other: ComplexNumber | Scalar) -> ComplexNumber:
        """Add complex number or scalar.

        Args:
            other: Complex number or scalar

        Returns:
            Sum

        Example:
            >>> result = z1 + z2
        """
        if isinstance(other, ComplexNumber):
            return ComplexNumber(self._real + other._real, self._imag + other._imag)
        else:
            return ComplexNumber(self._real + other, self._imag)

    def __radd__(self, other: Scalar) -> ComplexNumber:
        """Add scalar to complex number.

        Args:
            other: Scalar

        Returns:
            Sum

        Example:
            >>> result = 5.0 + z
        """
        return self.__add__(other)

    def __sub__(self, other: ComplexNumber | Scalar) -> ComplexNumber:
        """Subtract complex number or scalar.

        Args:
            other: Complex number or scalar

        Returns:
            Difference

        Example:
            >>> result = z1 - z2
        """
        if isinstance(other, ComplexNumber):
            return ComplexNumber(self._real - other._real, self._imag - other._imag)
        else:
            return ComplexNumber(self._real - other, self._imag)

    def __rsub__(self, other: Scalar) -> ComplexNumber:
        """Subtract complex number from scalar.

        Args:
            other: Scalar

        Returns:
            Difference

        Example:
            >>> result = 5.0 - z
        """
        return ComplexNumber(other - self._real, -self._imag)

    def __mul__(self, other: ComplexNumber | Scalar) -> ComplexNumber:
        """Multiply by complex number or scalar.

        Args:
            other: Complex number or scalar

        Returns:
            Product

        Example:
            >>> result = z1 * z2
        """
        if isinstance(other, ComplexNumber):
            real = self._real * other._real - self._imag * other._imag
            imag = self._real * other._imag + self._imag * other._real
            return ComplexNumber(real, imag)
        else:
            return ComplexNumber(self._real * other, self._imag * other)

    def __rmul__(self, other: Scalar) -> ComplexNumber:
        """Multiply scalar by complex number.

        Args:
            other: Scalar

        Returns:
            Product

        Example:
            >>> result = 5.0 * z
        """
        return self.__mul__(other)

    def __truediv__(self, other: ComplexNumber | Scalar) -> ComplexNumber:
        """Divide by complex number or scalar.

        Args:
            other: Complex number or scalar

        Returns:
            Quotient

        Example:
            >>> result = z1 / z2
        """
        if isinstance(other, ComplexNumber):
            denom = other._real ** 2 + other._imag ** 2
            if denom == 0:
                raise ZeroDivisionError("Cannot divide by zero complex number")
            real = (self._real * other._real + self._imag * other._imag) / denom
            imag = (self._imag * other._real - self._real * other._imag) / denom
            return ComplexNumber(real, imag)
        else:
            if other == 0:
                raise ZeroDivisionError("Cannot divide by zero")
            return ComplexNumber(self._real / other, self._imag / other)

    def __rtruediv__(self, other: Scalar) -> ComplexNumber:
        """Divide scalar by complex number.

        Args:
            other: Scalar

        Returns:
            Quotient

        Example:
            >>> result = 5.0 / z
        """
        denom = self._real ** 2 + self._imag ** 2
        if denom == 0:
            raise ZeroDivisionError("Cannot divide by zero complex number")
        real = (other * self._real) / denom
        imag = -(other * self._imag) / denom
        return ComplexNumber(real, imag)

    def __pow__(self, exponent: Scalar) -> ComplexNumber:
        """Raise to a power.

        Args:
            exponent: Exponent

        Returns:
            Result

        Example:
            >>> result = z ** 2
        """
        r = self.magnitude
        theta = self.phase
        new_r = r ** exponent
        new_theta = theta * exponent
        return ComplexNumber(new_r * math.cos(new_theta), new_r * math.sin(new_theta))

    def conjugate(self) -> ComplexNumber:
        """Get the complex conjugate.

        Returns:
            Complex conjugate

        Example:
            >>> conj = z.conjugate()
        """
        return ComplexNumber(self._real, -self._imag)

    def to_polar(self) -> tuple[Float, Float]:
        """Convert to polar form.

        Returns:
            Tuple of (magnitude, phase) in radians

        Example:
            >>> r, theta = z.to_polar()
        """
        return (self.magnitude, self.phase)

    @classmethod
    def from_polar(cls, magnitude: Float, phase: Float) -> ComplexNumber:
        """Create from polar form.

        Args:
            magnitude: Magnitude
            phase: Phase in radians

        Returns:
            Complex number

        Example:
            >>> z = ComplexNumber.from_polar(5.0, math.pi/4)
        """
        real = magnitude * math.cos(phase)
        imag = magnitude * math.sin(phase)
        return cls(real, imag)

    def to_tuple(self) -> tuple[Float, Float]:
        """Convert to tuple.

        Returns:
            Tuple of (real, imaginary)

        Example:
            >>> real, imag = z.to_tuple()
        """
        return (self._real, self._imag)

    def copy(self) -> ComplexNumber:
        """Create a copy.

        Returns:
            Copy of complex number

        Example:
            >>> copy = z.copy()
        """
        return ComplexNumber(self._real, self._imag)


class ComplexVector:
    """A vector of complex numbers.

    This class represents a vector where each element is a complex number.

    Example:
        >>> cv = ComplexVector([ComplexNumber(1.0, 2.0), ComplexNumber(3.0, 4.0)])
    """

    def __init__(self, elements: list[ComplexNumber]) -> None:
        """Initialize a ComplexVector.

        Args:
            elements: List of complex numbers

        Example:
            >>> cv = ComplexVector([ComplexNumber(1.0, 2.0), ComplexNumber(3.0, 4.0)])
        """
        self._elements = elements.copy()
        self._dimension = len(elements)

    @property
    def dimension(self) -> int:
        """Get the dimension.

        Returns:
            Vector dimension

        Example:
            >>> print(f"Dimension: {cv.dimension}")
        """
        return self._dimension

    def __getitem__(self, index: int) -> ComplexNumber:
        """Get element by index.

        Args:
            index: Element index

        Returns:
            Complex number

        Example:
            >>> element = cv[0]
        """
        return self._elements[index]

    def __len__(self) -> int:
        """Get length.

        Returns:
            Dimension

        Example:
            >>> len(cv)
        """
        return self._dimension

    def conjugate(self) -> ComplexVector:
        """Get the complex conjugate vector.

        Returns:
            Conjugated vector

        Example:
            >>> conj = cv.conjugate()
        """
        return ComplexVector([e.conjugate() for e in self._elements])


class ComplexMatrix:
    """A matrix of complex numbers.

    This class represents a matrix where each element is a complex number.

    Example:
        >>> cm = ComplexMatrix([[ComplexNumber(1.0, 0.0), ComplexNumber(0.0, 1.0)]])
    """

    def __init__(self, data: list[list[ComplexNumber]]) -> None:
        """Initialize a ComplexMatrix.

        Args:
            data: Matrix data as list of lists of complex numbers

        Example:
            >>> cm = ComplexMatrix([[ComplexNumber(1.0, 0.0), ComplexNumber(0.0, 1.0)]])
        """
        self._data = [row.copy() for row in data]
        self._rows = len(data)
        self._cols = len(data[0]) if data else 0

    @property
    def shape(self) -> tuple[int, int]:
        """Get the shape.

        Returns:
            Shape tuple (rows, cols)

        Example:
            >>> print(f"Shape: {cm.shape}")
        """
        return (self._rows, self._cols)

    def __getitem__(self, index: tuple[int, int]) -> ComplexNumber:
        """Get element by index.

        Args:
            index: (row, col) tuple

        Returns:
            Complex number

        Example:
            >>> element = cm[0, 0]
        """
        row_idx, col_idx = index
        return self._data[row_idx][col_idx]

    def conjugate_transpose(self) -> ComplexMatrix:
        """Get the conjugate transpose (Hermitian transpose).

        Returns:
            Conjugate transposed matrix

        Example:
            >>> hermitian = cm.conjugate_transpose()
        """
        transposed = [[self._data[j][i].conjugate() for j in range(self._rows)] for i in range(self._cols)]
        return ComplexMatrix(transposed)


# Export
__all__ = [
    "ComplexNumber",
    "ComplexVector",
    "ComplexMatrix",
]
