"""
Rotating Frame Module

This module provides rotating reference frame definitions for the Scientific package.

Purpose
-------
Provide rotating reference frame implementation.

Responsibilities
----------------
- Define rotating reference frame
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


class RotatingFrame(ReferenceFrame):
    """Concrete implementation of a rotating reference frame.

    This class provides rotating reference frame functionality.

    Attributes:
        _frame_id: Frame identifier
        _name: Frame name
        _description: Frame description
        _angular_velocity: Angular velocity
        _rotation_axis: Rotation axis
        _metadata: Frame metadata

    Example:
        >>> frame = RotatingFrame("rotating_001", "Earth Frame", "Earth rotating frame")
        >>> frame.frame_id()
    """

    def __init__(
        self,
        frame_id: FrameID,
        name: str,
        description: str = "",
        angular_velocity: float = 0.0,
        rotation_axis: Optional[tuple[float, float, float]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a RotatingFrame.

        Args:
            frame_id: Frame identifier
            name: Frame name
            description: Frame description
            angular_velocity: Angular velocity (rad/s)
            rotation_axis: Rotation axis (x, y, z)
            metadata: Frame metadata

        Example:
            >>> frame = RotatingFrame("rotating_001", "Earth Frame", "Earth rotating frame")
        """
        super().__init__(frame_id, name, description, metadata)
        self._angular_velocity = angular_velocity
        self._rotation_axis = rotation_axis or (0.0, 0.0, 1.0)

    @property
    def angular_velocity(self) -> float:
        """Get the angular velocity.

        Returns:
            Angular velocity (rad/s)

        Example:
            >>> print(f"Angular velocity: {frame.angular_velocity}")
        """
        return self._angular_velocity

    @property
    def rotation_axis(self) -> tuple[float, float, float]:
        """Get the rotation axis.

        Returns:
            Rotation axis (x, y, z)

        Example:
            >>> print(f"Rotation axis: {frame.rotation_axis}")
        """
        return self._rotation_axis

    def frame_type(self) -> str:
        """Get the frame type.

        Returns:
            Frame type

        Example:
            >>> print(f"Type: {frame.frame_type()}")
        """
        return "rotating"

    def transform_to(self, target_frame: IReferenceFrame) -> FrameTransform:
        """Get transformation to another frame.

        Args:
            target_frame: Target reference frame

        Returns:
            Transformation matrix

        Note:
            This is a simplified implementation. Real implementations would
            require proper transformations including Coriolis and centrifugal effects.

        Example:
            >>> transform = frame.transform_to(other_frame)
        """
        # Simplified transformation (identity for same frame)
        if target_frame.frame_id() == self._frame_id:
            return {
                "type": "identity",
                "matrix": [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
                "translation": [0, 0, 0],
            }
        
        # Placeholder for actual transformation logic
        return {
            "type": "rotating_transform",
            "source_frame": self._frame_id,
            "target_frame": target_frame.frame_id(),
            "angular_velocity": self._angular_velocity,
            "rotation_axis": self._rotation_axis,
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Frame definition

        Example:
            >>> data = frame.to_dict()
        """
        data = super().to_dict()
        data["angular_velocity"] = self._angular_velocity
        data["rotation_axis"] = self._rotation_axis
        return data

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(frame)
        """
        return f"RotatingFrame(id={self._frame_id}, name={self._name}, angular_velocity={self._angular_velocity})"


# Export
__all__ = [
    "RotatingFrame",
]
