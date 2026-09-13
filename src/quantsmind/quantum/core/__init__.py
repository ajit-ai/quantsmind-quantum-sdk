"""Core domain problem model of QuantsMind Quantum.

The core layer defines the vocabulary of a domain problem: variables,
objectives, constraints, domain context, the problem itself and domain
solutions.  It contains no execution logic — that lives in the workflow
layer and in MicroQuantum.
"""

from __future__ import annotations

from quantsmind.quantum.core.constraint import (
    Constraint,
    ConstraintOperator,
    ConstraintPriority,
    ConstraintStatus,
)
from quantsmind.quantum.core.domain_context import DomainContext
from quantsmind.quantum.core.objective import Objective, ObjectiveSense
from quantsmind.quantum.core.problem import QuantumProblem
from quantsmind.quantum.core.solution import ProblemSolution
from quantsmind.quantum.core.variable import Variable, VariableType

__all__ = [
    "QuantumProblem",
    "Variable",
    "VariableType",
    "Objective",
    "ObjectiveSense",
    "Constraint",
    "ConstraintOperator",
    "ConstraintPriority",
    "ConstraintStatus",
    "DomainContext",
    "ProblemSolution",
]
