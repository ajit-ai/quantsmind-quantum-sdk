"""Result layer of QuantsMind Quantum.

Contains the domain-level :class:`SolutionReport`, data-derived
:class:`Interpretation` and :class:`Provenance` models, and the QMQ-06
structured result interpretation (:class:`ResultInterpreter` /
:class:`ResultInterpretation`).  The low-level enriched circuit result
(:class:`QuantumResult`) lives in :mod:`quantsmind.quantum.circuit_result`.
"""

from __future__ import annotations

from quantsmind.quantum.result.interpretation import (
    Interpretation,
    InterpretationQuality,
    SolutionInterpreter,
)
from quantsmind.quantum.result.provenance import Provenance
from quantsmind.quantum.result.result import SolutionReport
from quantsmind.quantum.result.result_interpretation import (
    AlgorithmInterpretation,
    BenchmarkInterpretation,
    ExecutionInterpretation,
    FeasibilityInterpretation,
    FeasibilityStatus,
    InterpretationStatus,
    Limitation,
    ObjectiveInterpretation,
    ProvenanceOverview,
    Qualification,
    ResultInterpretation,
    ResultInterpreter,
    SolutionQuality,
    StrategyInterpretation,
)

__all__ = [
    "SolutionReport",
    "Interpretation",
    "InterpretationQuality",
    "SolutionInterpreter",
    "Provenance",
    "AlgorithmInterpretation",
    "BenchmarkInterpretation",
    "ExecutionInterpretation",
    "FeasibilityInterpretation",
    "FeasibilityStatus",
    "InterpretationStatus",
    "Limitation",
    "ObjectiveInterpretation",
    "ProvenanceOverview",
    "Qualification",
    "ResultInterpretation",
    "ResultInterpreter",
    "SolutionQuality",
    "StrategyInterpretation",
]
