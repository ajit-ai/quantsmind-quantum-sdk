"""QMQ-02 optimization representations (expression, QUBO, Ising, baseline).

The optimization package provides the computational representations that the
QMQ-01 domain foundation plugs into::

    QuantumProblem
        -> OptimizationModel
        -> QUBOModel          (binary quadratic minimization)
        -> IsingModel         (spin form, energy-equivalent to the QUBO)
        -> quantum program / MicroQuantum
    and, independently::

    QUBOModel -> ExhaustiveSolver (classical baseline)

Nothing in this package imports ``microquantum``; engine access stays in the
integration layer.
"""

from __future__ import annotations

from quantsmind.quantum.optimization.classical import (
    ClassicalSolverResult,
    ExhaustiveLimitError,
    ExhaustiveSolver,
    NoFeasibleSolutionError,
)
from quantsmind.quantum.optimization.expression import (
    Constant,
    Expression,
    ExpressionError,
    ExpressionParseError,
    Product,
    Scale,
    Sum,
    VariableExpression,
    coerce_expression,
    const,
    evaluate_expression,
    parse_expression,
    var,
)
from quantsmind.quantum.optimization.ising import IsingError, IsingModel
from quantsmind.quantum.optimization.penalties import (
    ConstraintPenalizer,
    PenaltyTerm,
    UnsupportedConstraintError,
)
from quantsmind.quantum.optimization.qubo import (
    QUBOError,
    QUBOModel,
    qubo_from_expression,
)

__all__ = [
    "Expression",
    "ExpressionError",
    "ExpressionParseError",
    "Constant",
    "VariableExpression",
    "Scale",
    "Sum",
    "Product",
    "var",
    "const",
    "coerce_expression",
    "parse_expression",
    "evaluate_expression",
    "QUBOError",
    "QUBOModel",
    "qubo_from_expression",
    "IsingError",
    "IsingModel",
    "ConstraintPenalizer",
    "PenaltyTerm",
    "UnsupportedConstraintError",
    "ClassicalSolverResult",
    "ExhaustiveSolver",
    "ExhaustiveLimitError",
    "NoFeasibleSolutionError",
]
