"""
Gate Package

This package provides gate management for the Quantum package.

Purpose
-------
Provide comprehensive gate definitions and operations.

Modules
-------
- gate: Gate management
- single_qubit_gate: Single qubit gate management
- multi_qubit_gate: Multi qubit gate management
- controlled_gate: Controlled gate management
- parameterized_gate: Parameterized gate management
"""

from __future__ import annotations

from quantsmind.quantum.gate.controlled_gate import (
    CCXGate,
    CNOTGate,
    ControlledGate,
    CYGate,
    CZGate,
)
from quantsmind.quantum.gate.gate import QuantumGate
from quantsmind.quantum.gate.multi_qubit_gate import ISwapGate, MultiQubitGate, SwapGate
from quantsmind.quantum.gate.parameterized_gate import (
    ParameterizedGate,
    PhaseGate,
    RXGate,
    RYGate,
    RZGate,
    UGate,
)
from quantsmind.quantum.gate.single_qubit_gate import (
    HadamardGate,
    IdentityGate,
    PauliXGate,
    PauliYGate,
    PauliZGate,
    SGate,
    SingleQubitGate,
    SXGate,
    TGate,
)

__all__ = [
    "QuantumGate",
    "SingleQubitGate",
    "IdentityGate",
    "PauliXGate",
    "PauliYGate",
    "PauliZGate",
    "HadamardGate",
    "SGate",
    "TGate",
    "SXGate",
    "MultiQubitGate",
    "SwapGate",
    "ISwapGate",
    "ControlledGate",
    "CNOTGate",
    "CYGate",
    "CZGate",
    "CCXGate",
    "ParameterizedGate",
    "RXGate",
    "RYGate",
    "RZGate",
    "PhaseGate",
    "UGate",
]
