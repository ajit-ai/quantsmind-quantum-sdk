"""
Bloch State Module

This module provides Bloch sphere state definitions for the Quantum package.

Purpose
-------
Provide Bloch sphere state management for quantum computing operations.

Responsibilities
----------------
- Define Bloch sphere state structure
- Support Bloch sphere state operations
- Support Bloch sphere state validation
- Support Bloch sphere state metadata

Dependencies
------------
typing (standard library)
math (standard library)
quantsmind.quantum.algorithms.exceptions (quantum exceptions)
quantsmind.quantum.algorithms.enums (quantum enumerations)
quantsmind.quantum.algorithms.types (quantum types)
quantsmind.quantum.state.quantum_state (quantum state module)
"""

from __future__ import annotations

import math
from typing import Any

from quantsmind.quantum.algorithms.enums import StateType
from quantsmind.quantum.algorithms.exceptions import StateError
from quantsmind.quantum.algorithms.types import ValidationResult
from quantsmind.quantum.state.quantum_state import QuantumState


class BlochState(QuantumState):
    """Concrete implementation of a Bloch sphere state.

    This class provides Bloch sphere state functionality for quantum computing.
    Bloch sphere states represent single-qubit pure states.

    Attributes:
        _theta: Polar angle
        _phi: Azimuthal angle
        _metadata: State metadata

    Example:
        >>> bloch_state = BlochState(theta=0, phi=0)
    """

    def __init__(
        self,
        theta: float = 0.0,
        phi: float = 0.0,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a BlochState.

        Args:
            theta: Polar angle (0 to π)
            phi: Azimuthal angle (0 to 2π)
            metadata: State metadata

        Example:
            >>> bloch_state = BlochState(theta=0, phi=0)
        """
        super().__init__(1, metadata)  # Bloch sphere only for single qubit
        self._theta = theta
        self._phi = phi
        self._state_type = StateType.BLOCH

    @property
    def theta(self) -> float:
        """Get the polar angle.

        Returns:
            Polar angle

        Example:
            >>> theta = bloch_state.theta
        """
        return self._theta

    @property
    def phi(self) -> float:
        """Get the azimuthal angle.

        Returns:
            Azimuthal angle

        Example:
            >>> phi = bloch_state.phi
        """
        return self._phi

    @property
    def state_type(self) -> StateType:
        """Get the state type.

        Returns:
            State type

        Example:
            >>> stype = bloch_state.state_type
        """
        return self._state_type

    def set_angles(self, theta: float, phi: float) -> None:
        """Set the Bloch sphere angles.

        Args:
            theta: Polar angle (0 to π)
            phi: Azimuthal angle (0 to 2π)

        Example:
            >>> bloch_state.set_angles(math.pi/2, 0)
        """
        if theta < 0 or theta > math.pi:
            raise StateError(f"Theta must be between 0 and π, got {theta}", {"theta": theta})

        if phi < 0 or phi > 2 * math.pi:
            raise StateError(f"Phi must be between 0 and 2π, got {phi}", {"phi": phi})

        self._theta = theta
        self._phi = phi

    def get_state_vector(self) -> tuple[complex, complex]:
        """Get the state vector representation.

        Returns:
            Tuple of complex amplitudes (α, β)

        Example:
            >>> alpha, beta = bloch_state.get_state_vector()
        """
        cos_half_theta = math.cos(self._theta / 2)
        sin_half_theta = math.sin(self._theta / 2)

        alpha = cos_half_theta
        beta = sin_half_theta * math.exp(1j * self._phi)

        return (alpha, beta)

    def get_cartesian_coordinates(self) -> tuple[float, float, float]:
        """Get the Cartesian coordinates on the Bloch sphere.

        Returns:
            Tuple of (x, y, z) coordinates

        Example:
            >>> x, y, z = bloch_state.get_cartesian_coordinates()
        """
        x = math.sin(self._theta) * math.cos(self._phi)
        y = math.sin(self._theta) * math.sin(self._phi)
        z = math.cos(self._theta)

        return (x, y, z)

    def set_from_cartesian(self, x: float, y: float, z: float) -> None:
        """Set the state from Cartesian coordinates.

        Args:
            x: X coordinate
            y: Y coordinate
            z: Z coordinate

        Example:
            >>> bloch_state.set_from_cartesian(0, 0, 1)
        """
        # Normalize to unit sphere
        norm = math.sqrt(x**2 + y**2 + z**2)
        if norm > 1e-10:
            x /= norm
            y /= norm
            z /= norm

        self._theta = math.acos(z)
        self._phi = math.atan2(y, x)
        if self._phi < 0:
            self._phi += 2 * math.pi

    def initialize_zero(self) -> None:
        """Initialize to |0⟩ state (north pole).

        Example:
            >>> bloch_state.initialize_zero()
        """
        self._theta = 0.0
        self._phi = 0.0

    def initialize_one(self) -> None:
        """Initialize to |1⟩ state (south pole).

        Example:
            >>> bloch_state.initialize_one()
        """
        self._theta = math.pi
        self._phi = 0.0

    def initialize_plus(self) -> None:
        """Initialize to |+⟩ state (equator, phi=0).

        Example:
            >>> bloch_state.initialize_plus()
        """
        self._theta = math.pi / 2
        self._phi = 0.0

    def initialize_minus(self) -> None:
        """Initialize to |-⟩ state (equator, phi=π).

        Example:
            >>> bloch_state.initialize_minus()
        """
        self._theta = math.pi / 2
        self._phi = math.pi

    def initialize_y_plus(self) -> None:
        """Initialize to |+i⟩ state (equator, phi=π/2).

        Example:
            >>> bloch_state.initialize_y_plus()
        """
        self._theta = math.pi / 2
        self._phi = math.pi / 2

    def initialize_y_minus(self) -> None:
        """Initialize to |-i⟩ state (equator, phi=3π/2).

        Example:
            >>> bloch_state.initialize_y_minus()
        """
        self._theta = math.pi / 2
        self._phi = 3 * math.pi / 2

    def get_pauli_expectations(self) -> tuple[float, float, float]:
        """Get the expectation values of Pauli operators.

        Returns:
            Tuple of (⟨X⟩, ⟨Y⟩, ⟨Z⟩)

        Example:
            >>> x_exp, y_exp, z_exp = bloch_state.get_pauli_expectations()
        """
        x, y, z = self.get_cartesian_coordinates()
        return (x, y, z)

    def validate(self) -> ValidationResult:
        """Validate the Bloch state.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = bloch_state.validate()
        """
        errors = []

        # Validate base state
        is_valid, base_errors = super().validate()
        errors.extend(base_errors)

        if self._theta < 0 or self._theta > math.pi:
            errors.append(f"Theta must be between 0 and π, got {self._theta}")

        if self._phi < 0 or self._phi > 2 * math.pi:
            errors.append(f"Phi must be between 0 and 2π, got {self._phi}")

        return (len(errors) == 0, errors)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Bloch state definition

        Example:
            >>> data = bloch_state.to_dict()
        """
        data = super().to_dict()
        data["state_type"] = self._state_type.value
        data["theta"] = self._theta
        data["phi"] = self._phi
        data["cartesian"] = self.get_cartesian_coordinates()
        data["state_vector"] = self.get_state_vector()
        return data

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(bloch_state)
        """
        return f"BlochState(theta={self._theta:.4f}, phi={self._phi:.4f})"
