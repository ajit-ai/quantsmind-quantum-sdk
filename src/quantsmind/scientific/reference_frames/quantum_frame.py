"""
Quantum Frame Module

This module provides quantum reference frame definitions for the Scientific package.

Purpose
-------
Provide quantum reference frame implementation.

Responsibilities
----------------
- Define quantum reference frame
- Support frame transformations
- Support frame operations
- Support frame validation

Dependencies
------------
typing (standard library)
quantsmind.scientific.reference_frames.reference_frame (reference frame)
quantsmind.scientific.interfaces (scientific interfaces)
quantsmind.scientific.exceptions (scientific exceptions)
quantsmind.scientific.types (scientific types)
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from quantsmind.scientific.interfaces import IReferenceFrame
from quantsmind.scientific.reference_frames.reference_frame import ReferenceFrame
from quantsmind.scientific.types import FrameID, FrameTransform


class QuantumReferenceFrame(ReferenceFrame):
    """Concrete implementation of a quantum reference frame.

    This class provides quantum reference frame functionality.

    Attributes:
        _frame_id: Frame identifier
        _name: Frame name
        _description: Frame description
        _basis_state: Basis state
        _metadata: Frame metadata

    Example:
        >>> frame = QuantumReferenceFrame("quantum_001", "Qubit Frame", "Quantum reference frame")
        >>> frame.frame_id()
    """

    def __init__(
        self,
        frame_id: FrameID,
        name: str,
        description: str = "",
        basis_state: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a QuantumReferenceFrame.

        Args:
            frame_id: Frame identifier
            name: Frame name
            description: Frame description
            basis_state: Basis state
            metadata: Frame metadata

        Example:
            >>> frame = QuantumReferenceFrame("quantum_001", "Qubit Frame", "Quantum reference frame")
        """
        super().__init__(frame_id, name, description, metadata)
        self._basis_state = basis_state or "|0⟩"

    @property
    def basis_state(self) -> str:
        """Get the basis state.

        Returns:
            Basis state

        Example:
            >>> print(f"Basis state: {frame.basis_state}")
        """
        return self._basis_state

    def frame_type(self) -> str:
        """Get the frame type.

        Returns:
            Frame type

        Example:
            >>> print(f"Type: {frame.frame_type()}")
        """
        return "quantum"

    def transform_to(self, target_frame: IReferenceFrame) -> FrameTransform:
        """Get transformation to another frame.

        Args:
            target_frame: Target reference frame

        Returns:
            Transformation matrix

        Note:
            This is a placeholder implementation. Real implementations would
            require proper quantum transformations (unitary operators).

        Example:
            >>> transform = frame.transform_to(other_frame)
        """
        # Simplified transformation (identity for same frame)
        if target_frame.frame_id() == self._frame_id:
            return {
                "type": "identity",
                "matrix": [[1, 0], [0, 1]],
                "basis_state": self._basis_state,
            }
        
        # Placeholder for actual transformation logic
        return {
            "type": "quantum_transform",
            "source_frame": self._frame_id,
            "target_frame": target_frame.frame_id(),
            "basis_state": self._basis_state,
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Frame definition

        Example:
            >>> data = frame.to_dict()
        """
        data = super().to_dict()
        data["basis_state"] = self._basis_state
        return data

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(frame)
        """
        return f"QuantumReferenceFrame(id={self._frame_id}, name={self._name}, basis_state={self._basis_state})"


# Export
__all__ = [
    "QuantumReferenceFrame",
]
