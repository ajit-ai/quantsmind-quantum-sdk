"""Finance -> QMQ formulation adapter.

:class:`FinanceFormulationAdapter` converts a validated
:class:`~quantsmind.quantum.finance.models.FinancialProblem` into the
existing QMQ pipeline: a :class:`QuantumProblem` (which the existing
:func:`~quantsmind.quantum.formulation.formulate` and QUBO mapper consume
unchanged).  It preserves objective senses, variables, constraints,
coefficients, the deterministic asset ordering and Finance provenance
metadata.  No Finance-specific QUBO exists — the existing QMQ-02
representations are reused.
"""

from __future__ import annotations

from typing import Any

from quantsmind.quantum.core.constraint import Constraint
from quantsmind.quantum.core.domain_context import DomainContext
from quantsmind.quantum.core.objective import Objective
from quantsmind.quantum.core.problem import QuantumProblem
from quantsmind.quantum.core.variable import Variable
from quantsmind.quantum.finance.context import FinancialContext
from quantsmind.quantum.finance.errors import FinanceValidationError
from quantsmind.quantum.finance.models import FinancialProblem

__all__ = ["FinanceFormulationAdapter"]


def _default_domain(context: FinancialContext | None) -> DomainContext:
    if context is not None:
        return context.to_domain_context()
    return DomainContext(domain="finance")


class FinanceFormulationAdapter:
    """Converts financial problems into the existing QMQ formulation.

    The conversion is deterministic: decision variables follow the ``x<i>``
    convention in universe order, objectives keep their senses, and every
    financial constraint materializes into QMQ constraints.
    """

    def validate(self, problem: FinancialProblem) -> list[str]:
        """Return the validation issues of a financial problem (empty = valid)."""
        return problem.validate()

    def raise_if_invalid(self, problem: FinancialProblem) -> None:
        """Raise :class:`FinanceValidationError` when the problem is invalid.

        Raises:
            FinanceValidationError: If the problem fails validation.
        """
        issues = problem.validate()
        if issues:
            raise FinanceValidationError(
                f"invalid financial problem {problem.name!r}: " + "; ".join(issues)
            )

    @staticmethod
    def finance_metadata(problem: FinancialProblem) -> dict[str, Any]:
        """JSON-safe Finance provenance metadata for the quantum problem."""
        meta: dict[str, Any] = {
            "domain_layer": "finance",
            "universe": problem.universe.name,
            "asset_order": problem.universe.identifier_order(),
            "allocation_kind": problem.allocation_kind.name.lower(),
            "objectives": [o.to_dict() for o in problem.objectives],
            "constraints": [c.to_dict() for c in problem.constraints],
        }
        if problem.context is not None:
            meta["context"] = problem.context.to_dict()
            meta["assumptions"] = dict(problem.context.assumptions)
        if problem.risk is not None:
            meta["risk"] = problem.risk.to_dict()
        return meta

    def to_quantum_problem(
        self,
        problem: FinancialProblem,
        *,
        preferred_strategy: Any = None,
    ) -> QuantumProblem:
        """Convert a financial problem into a QMQ :class:`QuantumProblem`.

        Args:
            problem: The validated financial problem.
            preferred_strategy: Optional preferred computation strategy.

        Raises:
            FinanceValidationError: If the financial problem is invalid.
        """
        self.raise_if_invalid(problem)
        variables: list[Variable] = problem.decision_variables
        objectives: list[Objective] = [
            objective.to_quantum_objective(problem.universe, problem.context, problem.risk)
            for objective in problem.objectives
        ]
        constraints: list[Constraint] = []
        for constraint in problem.constraints:
            constraints.extend(constraint.to_quantum_constraints(problem.universe))
        return QuantumProblem(
            name=problem.name,
            description=problem.description,
            domain=_default_domain(problem.context),
            variables=variables,
            objectives=objectives,
            constraints=constraints,
            metadata=FinanceFormulationAdapter.finance_metadata(problem),
            preferred_strategy=preferred_strategy,
            provenance={
                "domain_layer": "finance",
                "universe": problem.universe.name,
                "asset_order": problem.universe.identifier_order(),
                "allocation_kind": problem.allocation_kind.name.lower(),
            },
        )

    def formulate(self, problem: FinancialProblem) -> Any:
        """Return the existing QMQ formulation of a financial problem.

        Delegates to the existing :func:`quantsmind.quantum.formulation
        .formulate`, producing an :class:`OptimizationModel` (or another
        :class:`MathematicalModel` selected by the existing rules).
        """
        from quantsmind.quantum.formulation import formulate as qmq_formulate

        return qmq_formulate(self.to_quantum_problem(problem))
