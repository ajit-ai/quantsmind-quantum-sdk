"""Pure QMQ-05 comparison and metric math.

All sense/energy normalization of the benchmark layer is centralized here
(QMQ-05 §10):

* QUBO/Ising **energy is always compared as "lower is better"** — this is
  the QMQ-04 energy-direction fix, kept as the single reference.
* Domain **objectives** follow the problem's own ``MINIMIZE`` / ``MAXIMIZE``
  sense.

The module imports nothing from :mod:`quantsmind.quantum.benchmark.models`,
so it stays circular-import free and reusable by any future consumer.
"""

from __future__ import annotations

from math import isfinite

from quantsmind.quantum.core.constraint import ConstraintOperator, ConstraintStatus
from quantsmind.quantum.core.objective import ObjectiveSense
from quantsmind.quantum.core.problem import QuantumProblem


def objective_sense(problem: QuantumProblem) -> ObjectiveSense:
    """Return the primary objective sense of a problem.

    The first objective is the scalar being optimised (matching the workflow
    and QMQ-04 executors); a problem without objectives defaults to
    ``MINIMIZE``.
    """
    if problem.objectives:
        return problem.objectives[0].sense
    return ObjectiveSense.MINIMIZE


def sense_label(sense: ObjectiveSense | str) -> str:
    """Serialized sense label (``"minimize"``/``"maximize"``)."""
    parsed = sense if isinstance(sense, ObjectiveSense) else ObjectiveSense.parse(sense)
    return parsed.name.lower()


def is_better(left: float | None, right: float | None, sense: ObjectiveSense) -> bool:
    """True when ``left`` strictly outperforms ``right`` under ``sense``."""
    if left is None or right is None:
        return False
    if sense is ObjectiveSense.MAXIMIZE:
        return float(left) > float(right)
    return float(left) < float(right)


def normalized_score(
    sense: ObjectiveSense | str,
    objective_value: float | None,
    energy: float | None,
) -> float | None:
    """Return a higher-is-better scalar for ranking or ``None``.

    The domain objective is normalized by its sense; when the objective is
    unavailable, the QUBO/Ising energy is used and **lower energy is always
    better** (the QMQ-04 energy-direction fix, centralized here).
    """
    parsed = sense if isinstance(sense, ObjectiveSense) else ObjectiveSense.parse(sense)
    if objective_value is not None:
        value = float(objective_value)
        return value if parsed is ObjectiveSense.MAXIMIZE else -value
    if energy is not None:
        return -float(energy)
    return None


def optimality_gap(achieved: float | None, optimum: float | None) -> float | None:
    """Relative distance from a known optimum (0.0 means exact).

    Formula (QMQ-05 §11, documented):

    * ``optimum != 0``: ``gap = |optimum - achieved| / |optimum|``
    * ``optimum == 0``: ``gap = |optimum - achieved|`` (absolute distance,
      avoiding division by zero).

    The gap is always non-negative and sense-independent: a result that
    exactly matches the known optimum gives ``0.0``, any other result gives
    a positive distance (a result *better* than the recorded optimum still
    yields a positive gap — the discrepancy is surfaced, never hidden).

    Returns ``None`` when either value is missing or non-finite.
    """
    if achieved is None or optimum is None:
        return None
    achieved_f = float(achieved)
    optimum_f = float(optimum)
    if not isfinite(achieved_f) or not isfinite(optimum_f):
        return None
    distance = abs(optimum_f - achieved_f)
    if optimum_f == 0.0:
        return distance
    return distance / abs(optimum_f)


def approximation_ratio(
    achieved: float | None,
    optimum: float | None,
    sense: ObjectiveSense | str,
) -> float | None:
    """Approximation ratio against a known optimum, where mathematically
    appropriate (QMQ-05 §6).

    Formula (documented):

    * ``MAXIMIZE``: ``ratio = achieved / optimum``
    * ``MINIMIZE``: ``ratio = optimum / achieved``

    The ratio is only reported (≤1 when the result is suboptimal) for
    positive optima and non-negative meaningful denominators.  Returns
    ``None`` whenever the ratio is not interpretable (zero optimum, missing
    values, conflicting signs) — no value is manufactured.
    """
    if achieved is None or optimum is None:
        return None
    achieved_f = float(achieved)
    optimum_f = float(optimum)
    if not isfinite(achieved_f) or not isfinite(optimum_f) or optimum_f == 0.0:
        return None
    parsed = sense if isinstance(sense, ObjectiveSense) else ObjectiveSense.parse(sense)
    if parsed is ObjectiveSense.MAXIMIZE:
        if optimum_f <= 0.0 or achieved_f < 0.0:
            return None
        return achieved_f / optimum_f
    if optimum_f < 0.0 or achieved_f <= 0.0:
        return None
    return optimum_f / achieved_f


def _lhs_value(expression: object, assignments: dict[str, int]) -> float | None:
    """Evaluate a constraint expression to a numeric left-hand side."""
    if expression is None:
        return None
    if isinstance(expression, str):
        from quantsmind.quantum.optimization.expression import parse_expression

        return float(parse_expression(expression).evaluate(assignments))
    evaluate = getattr(expression, "evaluate", None)
    if callable(evaluate):
        return float(evaluate(assignments))
    if callable(expression):
        return float(expression(assignments))
    return None


def constraint_violations(problem: QuantumProblem, assignment: dict[str, int]) -> tuple[int, float]:
    """Count and magnitude of constraint violations for an assignment.

    Uses the existing domain :class:`Constraint` abstraction (QMQ-05 §12):
    a constraint is violated iff its :meth:`Constraint.evaluate` status is
    ``VIOLATED``; the magnitude is the numeric excess over the RHS value
    (missing/unevaluable expressions contribute ``0``).

    Returns ``(count, magnitude)``.
    """
    count = 0
    magnitude = 0.0
    for constraint in problem.constraints:
        if constraint.evaluate(assignment) is not ConstraintStatus.VIOLATED:
            continue
        count += 1
        lhs = _lhs_value(constraint.expression, assignment)
        if lhs is None:
            continue
        if constraint.operator is ConstraintOperator.LE:
            magnitude += max(0.0, lhs - constraint.value)
        elif constraint.operator is ConstraintOperator.GE:
            magnitude += max(0.0, constraint.value - lhs)
        else:
            magnitude += abs(lhs - constraint.value)
    return count, magnitude


__all__ = [
    "objective_sense",
    "sense_label",
    "is_better",
    "normalized_score",
    "optimality_gap",
    "approximation_ratio",
    "constraint_violations",
]
