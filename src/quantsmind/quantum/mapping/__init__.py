"""Mapping layer of QuantsMind Quantum.

Maps domain/computational descriptions into runtime representations.
QMQ-01 ships the quantum-circuit mapping.  QMQ-02 adds the automatic
problem -> optimization -> QUBO -> Ising pipeline:

* :class:`ProblemMapper`  problem -> :class:`OptimizationModel`
* :class:`QUBOMapper`     problem -> :class:`QUBOModel` (with penalties)
* :class:`IsingMapper`    QUBO -> :class:`IsingModel`
* :class:`QuantumCircuitMapper` program -> MicroQuantum circuit (QMQ-01)
"""

from __future__ import annotations

from quantsmind.quantum.mapping.ising import IsingMapper
from quantsmind.quantum.mapping.mapper import (
    DomainMapper,
    MappingError,
    MappingResult,
    QuantumCircuitMapper,
)
from quantsmind.quantum.mapping.qubo import ProblemMapper, QUBOMapper

__all__ = [
    "DomainMapper",
    "MappingError",
    "MappingResult",
    "QuantumCircuitMapper",
    "ProblemMapper",
    "QUBOMapper",
    "IsingMapper",
]
