"""
Reference Frame Module

This module provides reference frame definitions for the Scientific package.

Purpose
-------
Provide reference frame definitions and operations.

Responsibilities
----------------
- Define reference frame structure
- Support frame transformations
- Support frame metadata
- Support frame validation

Dependencies
------------
typing (standard library)
quantsmind.scientific.interfaces (scientific interfaces)
quantsmind.scientific.exceptions (scientific exceptions)
quantsmind.scientific.types (scientific types)
"""

from __future__ import annotations

from typing import Any

from quantsmind.scientific.interfaces import IReferenceFrame
from quantsmind.scientific.types import FrameID, FrameTransform


class ReferenceFrame(IReferenceFrame):
    """Concrete implementation of a reference frame.

    This class provides reference frame functionality.

    Attributes:
        _frame_id: Frame identifier
        _name: Frame name
        _description: Frame description
        _metadata: Frame metadata

    Example:
        >>> frame = ReferenceFrame("frame_001", "Lab Frame", "Laboratory reference frame")
        >>> frame.frame_id()
    """

    def __init__(
        self,
        frame_id: FrameID,
        name: str,
        description: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a ReferenceFrame.

        Args:
            frame_id: Frame identifier
            name: Frame name
            description: Frame description
            metadata: Frame metadata

        Example:
            >>> frame = ReferenceFrame("frame_001", "Lab Frame", "Laboratory reference frame")
        """
        self._frame_id = frame_id
        self._name = name
        self._description = description
        self._metadata = metadata or {}

    @property
    def frame_id(self) -> FrameID:
        """Get the frame identifier.

        Returns:
            Frame identifier

        Example:
            >>> print(f"ID: {frame.frame_id}")
        """
        return self._frame_id

    @property
    def name(self) -> str:
        """Get the frame name.

        Returns:
            Frame name

        Example:
            >>> print(f"Name: {frame.name}")
        """
        return self._name

    @property
    def description(self) -> str:
        """Get the frame description.

        Returns:
            Frame description

        Example:
            >>> print(f"Description: {frame.description}")
        """
        return self._description

    @property
    def metadata(self) -> dict[str, Any]:
        """Get the frame metadata.

        Returns:
            Frame metadata

        Example:
            >>> print(f"Metadata: {frame.metadata}")
        """
        return self._metadata.copy()

    def frame_type(self) -> str:
        """Get the frame type.

        Returns:
            Frame type

        Example:
            >>> print(f"Type: {frame.frame_type()}")
        """
        return "reference"

    def transform_to(self, target_frame: IReferenceFrame) -> FrameTransform:
        """Get transformation to another frame.

        Args:
            target_frame: Target reference frame

        Returns:
            Transformation matrix

        Note:
            This is a placeholder implementation. Subclasses should override.

        Example:
            >>> transform = frame.transform_to(other_frame)
        """
        raise NotImplementedError("Subclasses must implement transform_to()")

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Frame definition

        Example:
            >>> data = frame.to_dict()
        """
        return {
            "frame_id": self._frame_id,
            "name": self._name,
            "description": self._description,
            "frame_type": self.frame_type(),
            "metadata": self._metadata.copy(),
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(frame)
        """
        return f"ReferenceFrame(id={self._frame_id}, name={self._name})"


# Export
__all__ = [
    "ReferenceFrame",
]
