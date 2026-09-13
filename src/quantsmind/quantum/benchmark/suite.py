"""Canonical QMQ-05 benchmark suite: five small, deterministic problems.

The suite is deliberately small and exact (QMQ-05 §18):

* every benchmark is solvable exhaustively in milliseconds, so a classical
  baseline of known optimum can be computed and cross-checked;
* the variety covers linear and QUBO objectives, bound/inequality and
  equality-free constraints, both senses, and classical vs quantum-capable
  strategies;
* ``known_optimum`` values are stated explicitly and independently of the
  run (they are verified by tests, never derived from the benchmark itself).

No Finance, no sub-question novelty: the members reuse the QMQ-02/04
problem patterns exactly.
"""

from __future__ import annotations

from quantsmind.quantum.benchmark.models import BaselineConfig, Benchmark, BenchmarkSuite
from quantsmind.quantum.core.constraint import Constraint
from quantsmind.quantum.core.objective import Objective, ObjectiveSense
from quantsmind.quantum.core.problem import QuantumProblem
from quantsmind.quantum.core.variable import Variable
from quantsmind.quantum.execution.options import ExecutionOptions
from quantsmind.quantum.strategy.strategy import ComputationStrategy


def _classification_blob() -> dict[str, object]:
    return {"suite": "qmq05", "deterministic": True}


def b1_knapsack() -> QuantumProblem:
    """3-var knapsack: maximize value under one capacity constraint.

    Optimum: ``x0=1, x1=1, x2=0`` -> objective ``7`` (classical, exact).
    """
    problem = QuantumProblem("qmq05_b1_knapsack", domain="optimization")
    for index in range(3):
        problem.add_variable(Variable.binary(f"b1_x{index}"))
    problem.add_objective(
        Objective(
            "value",
            ObjectiveSense.MAXIMIZE,
            expression="3*b1_x0 + 4*b1_x1 + 5*b1_x2",
        )
    )
    problem.add_constraint(
        Constraint.le("capacity", expression="2*b1_x0 + 3*b1_x1 + 4*b1_x2", value=5.0)
    )
    problem.preferred_strategy = ComputationStrategy.CLASSICAL
    return problem


def b2_linear_max() -> QuantumProblem:
    """3-var unconstrained maximize linear objective.

    Optimum: all ones -> objective ``12`` (classical, exact).
    """
    problem = QuantumProblem("qmq05_b2_linear_max", domain="optimization")
    for index in range(3):
        problem.add_variable(Variable.binary(f"b2_x{index}"))
    problem.add_objective(
        Objective(
            "sum",
            ObjectiveSense.MAXIMIZE,
            expression="3*b2_x0 + 4*b2_x1 + 5*b2_x2",
        )
    )
    problem.preferred_strategy = ComputationStrategy.CLASSICAL
    return problem


def b3_qubo_min() -> QuantumProblem:
    """2-var QUBO minimize: ``x0 + x1 - 2*x0*x1``.

    Optimum: ``x0=x1=1`` -> objective ``0`` (a zero-optimum case exercising
    the ``optimality_gap``/``approximation_ratio`` division handling).
    """
    problem = QuantumProblem("qmq05_b3_qubo_min", domain="optimization")
    problem.add_variable(Variable.binary("a"))
    problem.add_variable(Variable.binary("b"))
    problem.add_objective(
        Objective(
            "pair",
            ObjectiveSense.MINIMIZE,
            expression="a + b - 2*a*b",
        )
    )
    problem.preferred_strategy = ComputationStrategy.HYBRID
    return problem


def b4_maxcut_triangle() -> QuantumProblem:
    """Max-Cut on the triangle (QMQ-04 canonical example, reused unchanged).

    Optimum cut: ``2`` (any single-edge separation is max for the triangle);
    a genuinely quantum-capable HYBRID run compares against the exact
    classical cut value.
    """
    problem = QuantumProblem("qmq05_b4_maxcut_triangle", domain="optimization")
    for variable in ("a", "b", "c"):
        problem.add_variable(Variable.binary(variable))
    problem.add_objective(
        Objective(
            "cut",
            ObjectiveSense.MAXIMIZE,
            expression=("1*(a+b-2*a*b) + 1*(b+c-2*b*c) + 1*(a+c-2*a*c)"),
        )
    )
    problem.preferred_strategy = ComputationStrategy.HYBRID
    return problem


def b5_geq_max() -> QuantumProblem:
    """4-var maximize with a >= constraint.

    Optimum: all ones -> objective ``8`` (constraint exactly relaxed,
    classical).  Non-trivially constrained so the exhaustive baseline walks a
    larger space than the unconstrained members.
    """
    problem = QuantumProblem("qmq05_b5_geq_max", domain="optimization")
    for index in range(4):
        problem.add_variable(Variable.binary(f"b5_x{index}"))
    problem.add_objective(
        Objective(
            "value",
            ObjectiveSense.MAXIMIZE,
            expression="2*b5_x0 + 3*b5_x1 + 1*b5_x2 + 2*b5_x3",
        )
    )
    problem.add_constraint(
        Constraint.ge("minimum", expression="b5_x0 + b5_x1 + b5_x2 + b5_x3", value=2.0)
    )
    problem.preferred_strategy = ComputationStrategy.CLASSICAL
    return problem


def default_suite(
    *,
    shots: int = 512,
    seed: int = 7,
    max_variables: int = 20,
) -> BenchmarkSuite:
    """Build the canonical QMQ-05 suite of five deterministic benchmarks.

    Args:
        shots: Quantum-leg shot count for HYBRID members.
        seed: Reproducibility seed for HYBRID members.
        max_variables: Classical baseline exhaustive limit.
    """
    suite = BenchmarkSuite(
        name="qmq05_default",
        description=(
            "Five small, deterministic benchmark problems with known optima; "
            "classical baselines are exact exhaustive runs (QMQ-02/04)."
        ),
    )
    hybrid_options = ExecutionOptions(shots=shots, seed=seed)

    suite.add(
        Benchmark(
            benchmark_id="b1_knapsack",
            name="Canonical knapsack (3 vars, capacity)",
            problem=b1_knapsack(),
            strategy="classical",
            algorithm="exhaustive",
            formulation="optimization",
            baseline=BaselineConfig(max_variables=max_variables),
            known_optimum=7.0,
            metadata=_classification_blob(),
        )
    )
    suite.add(
        Benchmark(
            benchmark_id="b2_linear_max",
            name="Canonical unconstrained linear max (3 vars)",
            problem=b2_linear_max(),
            strategy="classical",
            algorithm="exhaustive",
            formulation="optimization",
            baseline=BaselineConfig(max_variables=max_variables),
            known_optimum=12.0,
            metadata=_classification_blob(),
        )
    )
    suite.add(
        Benchmark(
            benchmark_id="b3_qubo_min",
            name="Canonical QUBO minimize (2 vars, zero optimum)",
            problem=b3_qubo_min(),
            strategy="hybrid",
            algorithm="qaoa",
            formulation="optimization",
            options=hybrid_options,
            baseline=BaselineConfig(max_variables=max_variables),
            known_optimum=0.0,
            metadata=_classification_blob(),
        )
    )
    suite.add(
        Benchmark(
            benchmark_id="b4_maxcut_triangle",
            name="Canonical Max-Cut triangle (3 vars, QMQ-04 reuse)",
            problem=b4_maxcut_triangle(),
            strategy="hybrid",
            algorithm="qaoa",
            formulation="optimization",
            options=hybrid_options,
            baseline=BaselineConfig(max_variables=max_variables),
            known_optimum=2.0,
            metadata=_classification_blob(),
        )
    )
    suite.add(
        Benchmark(
            benchmark_id="b5_geq_max",
            name="Canonical constrained maximize (4 vars, >=)",
            problem=b5_geq_max(),
            strategy="classical",
            algorithm="exhaustive",
            formulation="optimization",
            baseline=BaselineConfig(max_variables=max_variables),
            known_optimum=8.0,
            metadata=_classification_blob(),
        )
    )
    return suite


def default_suite_examples() -> list[Benchmark]:
    """Return the members of :func:`default_suite` (convenience for tooling)."""
    return list(default_suite().benchmarks.values())


__all__ = [
    "b1_knapsack",
    "b2_linear_max",
    "b3_qubo_min",
    "b4_maxcut_triangle",
    "b5_geq_max",
    "default_suite",
    "default_suite_examples",
]
