"""
Time Package

This package provides time management for the Scientific package.

Purpose
-------
Provide comprehensive time definitions and operations.

Modules
-------
- timestamp: Timestamp management
- duration: Duration management
- epoch: Epoch management
- simulation_time: Simulation time management
- logical_time: Logical time management
"""

from __future__ import annotations

from quantsmind.scientific.time.duration import Duration
from quantsmind.scientific.time.epoch import Epoch
from quantsmind.scientific.time.logical_time import LogicalTime
from quantsmind.scientific.time.simulation_time import SimulationTime
from quantsmind.scientific.time.timestamp import Timestamp

__all__ = [
    "Timestamp",
    "Duration",
    "Epoch",
    "SimulationTime",
    "LogicalTime",
]
