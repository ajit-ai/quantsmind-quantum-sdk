"""Automatic problem -> optimization -> QUBO mapping (QMQ-02).

The QMQ-01 foundation left this stage as ``NotImplementedError``.  QMQ-02
implements it for the supported binary-optimization path::

    QuantumProblem
        -> OptimizationModel      (ProblemMapper)
        -> QUBOModel              (QUBOMapper, incl. constraint penalties)

Unsupported problems fail loudly with :class:`MappingError` — never with a
fake or empty mapping.
"""

from __future__ import annotations

from typing import Any

from quantsmind.quantum.core.variable import VariableType
from quantsmind.quantum.formulation import formulate
from quantsmind.quantum.formulation.optimization_model import OptimizationModel
from quantsmind.quantum.mapping.mapper import MappingError, MappingResult
from quantsmind.quantum.optimization.expression import (
    ExpressionError,
    coerce_expression,
)
from quantsmind.quantum.optimization.penalties import (
    ConstraintPenalizer,
    UnsupportedConstraintError,
)
from quantsmind.quantum.optimization.qubo import QUBOError, QUBOModel
from quantsmind.quantum.strategy.strategy import ComputationStrategy


class ProblemMapper:
    """Maps a :class:`QuantumProblem` to an :class:`OptimizationModel`."""

    name = "problem_formulation"

    def map(self, problem: Any) -> OptimizationModel:
        """Return the optimization formulation of a problem.

        Raises:
            MappingError: If the problem has no optimization formulation
                (no objective / unsupported model kind).
        """
        model = (
            problem.formulation
            if isinstance(problem.formulation, OptimizationModel)
            else formulate(problem)
        )
        if not isinstance(model, OptimizationModel):
            raise MappingError(
                f"problem {getattr(problem, 'name', '?')!r} is not an "
                "optimization problem; QUBO formulation requires an "
                "optimization formulation"
            )
        return model


class QUBOMapper:
    """Maps a binary :class:`QuantumProblem` to a :class:`QUBOModel`.

    The objective expression (symbolic string or expression node) becomes
    the quadratic polynomial; a MAXIMIZE objective is negated so the QUBO is
    always a minimization; supported constraints are folded in as exact
    penalty terms.  The mapping record keeps the original sense and the
    penalty detail so reports can restore objective and feasibility.
    """

    name = "qubo"

    def map(
        self,
        problem: Any,
        *,
        strategy: ComputationStrategy = ComputationStrategy.HYBRID,
        penalty: float | None = None,
    ) -> MappingResult:
        """Build the QUBO model and record the mapping.

        Raises:
            MappingError: If the problem cannot be mapped (no objective,
                non-binary variables, non-symbolic objective, non-quadratic
                terms, or an unsupported constraint).
        """
        model = ProblemMapper().map(problem)
        variables = [v.name for v in problem.variables]
        if not variables:
            raise MappingError("QUBO mapping requires at least one decision variable")

        if not problem.objectives:
            raise MappingError("QUBO mapping requires at least one objective")
        objective = problem.objectives[0]

        non_binary = [v.name for v in problem.variables if v.type is not VariableType.BINARY]
        if non_binary:
            raise MappingError(
                "QUBO mapping supports binary variables only; the following "
                f"are not binary: {non_binary}"
            )

        try:
            expression = coerce_expression(objective.expression)
        except ExpressionError as exc:
            raise MappingError(
                f"objective {objective.name!r} cannot be mapped to a QUBO: {exc}"
            ) from exc

        unknown = set(expression.variables) - set(variables)
        if unknown:
            raise MappingError(
                f"objective expression references variables outside the problem: {sorted(unknown)}"
            )

        linear: dict[str, float] = {}
        quadratic: dict[tuple[str, str], float] = {}
        constant = 0.0
        for monomial, coefficient in expression.expand().items():
            degree = len(monomial)
            if degree > 2:
                raise MappingError(
                    f"objective {objective.name!r} has a term of degree "
                    f"{degree} (monomial {'*'.join(monomial)}); QUBO "
                    "requires terms of degree at most 2"
                )
            if degree == 0:
                constant += coefficient
            elif degree == 1 or monomial[0] == monomial[1]:
                linear[monomial[0]] = linear.get(monomial[0], 0.0) + coefficient
            else:
                key = (
                    (monomial[0], monomial[1])
                    if monomial[0] < monomial[1]
                    else (monomial[1], monomial[0])
                )
                quadratic[key] = quadratic.get(key, 0.0) + coefficient

        sense = objective.sense.name.lower()
        inverted = sense == "maximize"
        if inverted:
            linear = {n: -c for n, c in linear.items()}
            quadratic = {k: -c for k, c in quadratic.items()}
            constant = -constant

        objective_scale = 1.0
        candidates = [abs(c) for c in linear.values()]
        candidates += [abs(c) for c in quadratic.values()]
        objective_scale = max(candidates + [1.0])
        penalty_value = (1.0 + objective_scale) * 10.0 if penalty is None else float(penalty)
        if penalty_value <= 0.0:
            raise MappingError(f"penalty must be positive, got {penalty_value!r}")

        penalizer = ConstraintPenalizer(penalty=penalty_value)
        penalty_records: list[dict[str, Any]] = []
        slack_variables: list[str] = []
        for constraint in problem.constraints:
            try:
                term = penalizer.penalize(constraint)
            except UnsupportedConstraintError as exc:
                raise MappingError(
                    f"constraint {constraint.name!r} cannot be mapped to a QUBO penalty: {exc}"
                ) from exc
            for name, coefficient in term.linear.items():
                linear[name] = linear.get(name, 0.0) + coefficient
            for key, coefficient in term.quadratic.items():
                quadratic[key] = quadratic.get(key, 0.0) + coefficient
            constant += term.constant
            penalty_records.append(term.to_dict())
            for slack in term.slack_variables:
                if slack not in slack_variables:
                    slack_variables.append(slack)

        all_variables = variables + slack_variables
        try:
            qubo = QUBOModel(
                variables=all_variables,
                linear=linear,
                quadratic=quadratic,
                constant=constant,
                name=f"{model.problem_name}_qubo",
                metadata={
                    "problem": model.problem_name,
                    "formulation": model.name,
                },
            )
        except QUBOError as exc:
            raise MappingError(f"QUBO construction failed: {exc}") from exc

        metadata: dict[str, Any] = {
            "problem": model.problem_name,
            "objective": objective.name,
            "sense": sense,
            "sense_inverted": inverted,
            "objective_scale": objective_scale,
            "penalty": penalty_value,
            "penalties": penalty_records,
            "slack_variables": slack_variables,
            "decision_variables": variables,
        }
        steps = [
            "validated binary optimization problem",
            f"expanded objective {objective.name!r} into quadratic monomials",
            f"sense={sense}{' (negated for minimization)' if inverted else ''}",
            f"folded {len(problem.constraints)} constraints into penalties",
            (
                f"introduced {len(slack_variables)} slack variable(s)"
                if slack_variables
                else "no slack variables required"
            ),
            f"target: QUBOModel over {len(all_variables)} variables",
        ]
        return MappingResult(
            mapper=self.name,
            strategy=strategy,
            source="QuantumProblem/optimization",
            target="QUBOModel",
            steps=steps,
            metadata=metadata,
            payload=qubo,
        )


__all__ = ["ProblemMapper", "QUBOMapper"]
