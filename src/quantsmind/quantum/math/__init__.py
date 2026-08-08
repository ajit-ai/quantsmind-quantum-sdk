"""
Quantum Math Package

This package provides quantum mathematics integration for the QuantsMind SDK.

Purpose
-------
Provide mathematical interfaces between quantum computing and classical mathematics.

Modules
-------
- quantum_matrix: Quantum matrix operations
- quantum_state_math: Quantum state mathematics
- quantum_operator_math: Quantum operator mathematics
"""

from __future__ import annotations

from quantsmind.quantum.math.quantum_matrix import QuantumMatrix
from quantsmind.quantum.math.quantum_operator_math import QuantumOperatorMath
from quantsmind.quantum.math.quantum_state_math import QuantumStateMath

__all__: list[str] = [
    "QuantumMatrix",
    "QuantumStateMath",
    "QuantumOperatorMath",
]
