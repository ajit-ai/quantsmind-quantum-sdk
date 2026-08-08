"""
Reference Frames Package

This package provides reference frame management for the Scientific package.

Purpose
-------
Provide comprehensive reference frame definitions and transformations.

Modules
-------
- reference_frame: Base reference frame class
- inertial: Inertial reference frame
- rotating: Rotating reference frame
- quantum_frame: Quantum reference frame
"""

from __future__ import annotations

from quantsmind.scientific.reference_frames.inertial import InertialFrame
from quantsmind.scientific.reference_frames.quantum_frame import QuantumReferenceFrame
from quantsmind.scientific.reference_frames.reference_frame import ReferenceFrame
from quantsmind.scientific.reference_frames.rotating import RotatingFrame

__all__ = [
    "ReferenceFrame",
    "InertialFrame",
    "RotatingFrame",
    "QuantumReferenceFrame",
]
