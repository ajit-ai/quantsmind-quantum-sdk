"""
Noise Package

This package provides noise management for the Quantum package.

Purpose
-------
Provide comprehensive noise definitions and operations.

Modules
-------
- noise_model: Noise model management
- decoherence: Decoherence management
- error_channel: Error channel management
"""

from __future__ import annotations

from quantsmind.quantum.noise.decoherence import Decoherence
from quantsmind.quantum.noise.error_channel import (
    AmplitudeDampingChannel,
    BitFlipChannel,
    DepolarizingChannel,
    ErrorChannel,
    PhaseFlipChannel,
)
from quantsmind.quantum.noise.noise_model import NoiseModel

__all__ = [
    "NoiseModel",
    "Decoherence",
    "ErrorChannel",
    "BitFlipChannel",
    "PhaseFlipChannel",
    "AmplitudeDampingChannel",
    "DepolarizingChannel",
]
