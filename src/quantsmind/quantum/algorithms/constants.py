"""
Quantum Constants Module

This module provides constant definitions for the Quantum package.

Purpose
-------
Provide comprehensive constant definitions for quantum computing operations.

Responsibilities
----------------
- Define quantum-specific constants
- Provide physical constants
- Define default values

Dependencies
------------
math (standard library)
"""

from __future__ import annotations

import math

# SDK Version
QUANTUM_SDK_VERSION = "R0.8.0"

# Physical Constants
H_BAR = 1.054571817e-34  # Reduced Planck constant (J·s)
PLANCK_CONSTANT = 6.62607015e-23  # Planck constant (J·s)
BOLTZMANN_CONSTANT = 1.380649e-23  # Boltzmann constant (J/K)

# Quantum Constants
SQRT_2 = math.sqrt(2)
SQRT_2_INV = 1 / math.sqrt(2)
PI = math.pi
PI_2 = math.pi / 2
PI_4 = math.pi / 4

# Gate Constants
IDENTITY_MATRIX = [[1, 0], [0, 1]]
PAULI_X_MATRIX = [[0, 1], [1, 0]]
PAULI_Y_MATRIX = [[0, -1j], [1j, 0]]
PAULI_Z_MATRIX = [[1, 0], [0, -1]]
HADAMARD_MATRIX = [[SQRT_2_INV, SQRT_2_INV], [SQRT_2_INV, -SQRT_2_INV]]
S_GATE_MATRIX = [[1, 0], [0, 1j]]
T_GATE_MATRIX = [[1, 0], [0, math.exp(1j * PI_4)]]
SX_GATE_MATRIX = [[0.5 + 0.5j, 0.5 - 0.5j], [0.5 - 0.5j, 0.5 + 0.5j]]

# State Constants
ZERO_STATE = [1, 0]
ONE_STATE = [0, 1]
PLUS_STATE = [SQRT_2_INV, SQRT_2_INV]
MINUS_STATE = [SQRT_2_INV, -SQRT_2_INV]

# Default Values
DEFAULT_NUM_QUBITS = 1
DEFAULT_NUM_SHOTS = 1024
DEFAULT_OPTIMIZATION_LEVEL = 2
DEFAULT_CIRCUIT_DEPTH = 0
DEFAULT_GATE_COUNT = 0

# Backend Constants
DEFAULT_SIMULATOR_NAME = "statevector_simulator"
DEFAULT_PROVIDER_NAME = "local"
DEFAULT_BACKEND_TIMEOUT = 300  # seconds

# Compiler Constants
DEFAULT_TRANSPILATION_TARGET = "full"
DEFAULT_OPTIMIZATION_TARGET = "depth"

# Measurement Constants
DEFAULT_MEASUREMENT_BASIS = "computational"
DEFAULT_MEASUREMENT_TYPE = "projective"

# Noise Constants
DEFAULT_NOISE_MODEL = "ideal"
DEFAULT_ERROR_RATE = 0.0
DEFAULT_T1 = 100e-6  # 100 microseconds
DEFAULT_T2 = 50e-6  # 50 microseconds

# Algorithm Constants
DEFAULT_MAX_ITERATIONS = 1000
DEFAULT_CONVERGENCE_TOLERANCE = 1e-6
DEFAULT_LEARNING_RATE = 0.01

# Serialization Constants
DEFAULT_SERIALIZATION_FORMAT = "qasm"
SUPPORTED_SERIALIZATION_FORMATS = ["qasm", "qasm2", "qasm3", "quil", "json"]

# Validation Constants
MIN_QUBITS = 1
MAX_QUBITS = 128
MIN_SHOTS = 1
MAX_SHOTS = 100000
MIN_GATE_COUNT = 0
MAX_GATE_COUNT = 10000

# Gate Names
GATE_IDENTITY = "I"
GATE_X = "X"
GATE_Y = "Y"
GATE_Z = "Z"
GATE_H = "H"
GATE_S = "S"
GATE_T = "T"
GATE_SX = "SX"
GATE_RX = "RX"
GATE_RY = "RY"
GATE_RZ = "RZ"
GATE_PHASE = "PHASE"
GATE_U = "U"
GATE_CX = "CX"
GATE_CY = "CY"
GATE_CZ = "CZ"
GATE_SWAP = "SWAP"
GATE_ISWAP = "ISWAP"
GATE_CCX = "CCX"
GATE_MEASURE = "MEASURE"
GATE_RESET = "RESET"
GATE_BARRIER = "BARRIER"

# Standard Gate Sets
SINGLE_QUBIT_GATES = [
    GATE_IDENTITY,
    GATE_X,
    GATE_Y,
    GATE_Z,
    GATE_H,
    GATE_S,
    GATE_T,
    GATE_SX,
    GATE_RX,
    GATE_RY,
    GATE_RZ,
    GATE_PHASE,
    GATE_U,
]

TWO_QUBIT_GATES = [
    GATE_CX,
    GATE_CY,
    GATE_CZ,
    GATE_SWAP,
    GATE_ISWAP,
]

THREE_QUBIT_GATES = [
    GATE_CCX,
]

# Provider Names
PROVIDER_IBM = "ibm"
PROVIDER_GOOGLE = "google"
PROVIDER_AWS_BRAKET = "aws_braket"
PROVIDER_AZURE_QUANTUM = "azure_quantum"
PROVIDER_IONQ = "ionq"
PROVIDER_RIGETTI = "rigetti"
PROVIDER_QUANTINUUM = "quantinuum"
PROVIDER_XANADU = "xanadu"
PROVIDER_LOCAL = "local"

# Backend Names
BACKEND_STATEVECTOR = "statevector_simulator"
BACKEND_UNITARY = "unitary_simulator"
BACKEND_MATRIX_PRODUCT_STATE = "matrix_product_state_simulator"
BACKEND_NOISY = "noisy_simulator"

# Export
__all__ = [
    # Version
    "QUANTUM_SDK_VERSION",
    # Physical Constants
    "H_BAR",
    "PLANCK_CONSTANT",
    "BOLTZMANN_CONSTANT",
    # Quantum Constants
    "SQRT_2",
    "SQRT_2_INV",
    "PI",
    "PI_2",
    "PI_4",
    # Gate Constants
    "IDENTITY_MATRIX",
    "PAULI_X_MATRIX",
    "PAULI_Y_MATRIX",
    "PAULI_Z_MATRIX",
    "HADAMARD_MATRIX",
    "S_GATE_MATRIX",
    "T_GATE_MATRIX",
    "SX_GATE_MATRIX",
    # State Constants
    "ZERO_STATE",
    "ONE_STATE",
    "PLUS_STATE",
    "MINUS_STATE",
    # Default Values
    "DEFAULT_NUM_QUBITS",
    "DEFAULT_NUM_SHOTS",
    "DEFAULT_OPTIMIZATION_LEVEL",
    "DEFAULT_CIRCUIT_DEPTH",
    "DEFAULT_GATE_COUNT",
    # Backend Constants
    "DEFAULT_SIMULATOR_NAME",
    "DEFAULT_PROVIDER_NAME",
    "DEFAULT_BACKEND_TIMEOUT",
    # Compiler Constants
    "DEFAULT_TRANSPILATION_TARGET",
    "DEFAULT_OPTIMIZATION_TARGET",
    # Measurement Constants
    "DEFAULT_MEASUREMENT_BASIS",
    "DEFAULT_MEASUREMENT_TYPE",
    # Noise Constants
    "DEFAULT_NOISE_MODEL",
    "DEFAULT_ERROR_RATE",
    "DEFAULT_T1",
    "DEFAULT_T2",
    # Algorithm Constants
    "DEFAULT_MAX_ITERATIONS",
    "DEFAULT_CONVERGENCE_TOLERANCE",
    "DEFAULT_LEARNING_RATE",
    # Serialization Constants
    "DEFAULT_SERIALIZATION_FORMAT",
    "SUPPORTED_SERIALIZATION_FORMATS",
    # Validation Constants
    "MIN_QUBITS",
    "MAX_QUBITS",
    "MIN_SHOTS",
    "MAX_SHOTS",
    "MIN_GATE_COUNT",
    "MAX_GATE_COUNT",
    # Gate Names
    "GATE_IDENTITY",
    "GATE_X",
    "GATE_Y",
    "GATE_Z",
    "GATE_H",
    "GATE_S",
    "GATE_T",
    "GATE_SX",
    "GATE_RX",
    "GATE_RY",
    "GATE_RZ",
    "GATE_PHASE",
    "GATE_U",
    "GATE_CX",
    "GATE_CY",
    "GATE_CZ",
    "GATE_SWAP",
    "GATE_ISWAP",
    "GATE_CCX",
    "GATE_MEASURE",
    "GATE_RESET",
    "GATE_BARRIER",
    # Standard Gate Sets
    "SINGLE_QUBIT_GATES",
    "TWO_QUBIT_GATES",
    "THREE_QUBIT_GATES",
    # Provider Names
    "PROVIDER_IBM",
    "PROVIDER_GOOGLE",
    "PROVIDER_AWS_BRAKET",
    "PROVIDER_AZURE_QUANTUM",
    "PROVIDER_IONQ",
    "PROVIDER_RIGETTI",
    "PROVIDER_QUANTINUUM",
    "PROVIDER_XANADU",
    "PROVIDER_LOCAL",
    # Backend Names
    "BACKEND_STATEVECTOR",
    "BACKEND_UNITARY",
    "BACKEND_MATRIX_PRODUCT_STATE",
    "BACKEND_NOISY",
]
