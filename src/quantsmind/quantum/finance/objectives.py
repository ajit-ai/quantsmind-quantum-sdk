"""Financial objectives of the Finance domain layer.

Each :class:`FinancialObjective` is a validated, serializable domain
objective that materializes into the existing QMQ
:class:`~quantsmind.quantum.core.objective.Objective` (reusing the existing
:class:`~quantsmind.quantum.core.objective.ObjectiveSense`) with a symbolic
expression understood by the QMQ-02 formulation layer.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, ClassVar

from quantsmind.quantum.core.objective import Objective, ObjectiveSense
from quantsmind.quantum.finance._expr import (
    fmt_number,
    linear_string,
    quadratic_string,
    variable_names,
)
from quantsmind.quantum.finance.errors import FinanceValidationError

if TYPE_CHECKING:
    from quantsmind.quantum.finance.context import FinancialContext
    from quantsmind.quantum.finance.models import AssetUniverse
    from quantsmind.quantum.finance.risk import RiskMatrix

__all__ = [
    "FinancialObjective",
    "ExpectedReturnObjective",
    "RiskObjective",
    "RiskAdjustedObjective",
    "objective_from_dict",
]


@dataclass
class FinancialObjective:
    """Base class of financial objectives.

    Args:
        name: Unique objective name.
        description: Optional human-readable description.

    Raises:
        FinanceValidationError: If the name is empty.
    """

    name: str
    description: str = ""

    kind: ClassVar[str] = "financial"

    def __post_init__(self) -> None:
        if not self.name:
            raise FinanceValidationError("objective name must be a non-empty string")

    def validate(self, assets: AssetUniverse, risk: RiskMatrix | None) -> list[str]:
        """Return validation issues against an asset universe (empty = valid)."""
        return []

    def to_quantum_objective(
        self,
        assets: AssetUniverse,
        context: FinancialContext | None = None,
        risk: RiskMatrix | None = None,
    ) -> Objective:
        """Materialize into an existing QMQ objective.

        Raises:
            NotImplementedError: On the base class.
        """
        raise NotImplementedError(f"{type(self).__name__} must implement to_quantum_objective()")

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary (kind included)."""
        return {
            "kind": self.kind,
            "name": self.name,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FinancialObjective:
        """Rebuild an objective from :meth:`to_dict` output (name + description).

        Subclasses with extra fields override ``from_dict``.
        """
        return cls(
            name=str(data["name"]),
            description=str(data.get("description", "")),
        )

    def __repr__(self) -> str:
        return f"{type(self).__name__}(name={self.name!r})"


@dataclass
class ExpectedReturnObjective(FinancialObjective):
    """Maximize expected return: ``maximize sum(expected_return_i * x_i)``."""

    kind: ClassVar[str] = "expected_return"

    def to_quantum_objective(
        self,
        assets: AssetUniverse,
        context: FinancialContext | None = None,
        risk: RiskMatrix | None = None,
    ) -> Objective:
        coefficients = [asset.expected_return for asset in assets]
        expression = linear_string(coefficients, variable_names(len(assets)))
        return Objective(
            self.name,
            ObjectiveSense.MAXIMIZE,
            expression=expression,
            metadata={"finance_kind": self.kind},
        )


@dataclass
class RiskObjective(FinancialObjective):
    """Minimize total variance: ``minimize w^T Cov w``.

    Requires a positive-semidefinite :class:`RiskMatrix` aligned with the
    asset universe.
    """

    kind: ClassVar[str] = "risk"

    def validate(self, assets: AssetUniverse, risk: RiskMatrix | None) -> list[str]:
        if risk is None:
            return [f"risk objective {self.name!r} requires a risk matrix"]
        if not risk.psd:
            return [
                f"risk objective {self.name!r} requires a risk matrix that is positive semidefinite"
            ]
        return []

    @staticmethod
    def _risk_terms(assets: AssetUniverse, risk: RiskMatrix) -> list[tuple[str, str, float]]:
        variables = variable_names(len(assets))
        terms: list[tuple[str, str, float]] = []
        for i, left in enumerate(assets):
            for j, _right in enumerate(assets):
                terms.append(
                    (
                        variables[i],
                        variables[j],
                        risk.covariance(left.identifier, _right.identifier),
                    )
                )
        return terms

    def to_quantum_objective(
        self,
        assets: AssetUniverse,
        context: FinancialContext | None = None,
        risk: RiskMatrix | None = None,
    ) -> Objective:
        if risk is None:
            raise FinanceValidationError(f"risk objective {self.name!r} requires a risk matrix")
        risk.require_psd()
        expression = quadratic_string(self._risk_terms(assets, risk))
        return Objective(
            self.name,
            ObjectiveSense.MINIMIZE,
            expression=expression,
            metadata={"finance_kind": self.kind},
        )


@dataclass
class RiskAdjustedObjective(FinancialObjective):
    """Maximize risk-adjusted return: ``maximize return - lambda * risk``.

    A mean-variance utility objective combining the expected-return terms
    with a risk penalty scaled by ``risk_aversion >= 0``.  A zero aversion
    degenerates to the pure expected-return objective.
    """

    risk_aversion: float = 1.0

    kind: ClassVar[str] = "risk_adjusted"

    def __post_init__(self) -> None:
        super().__post_init__()
        if not math.isfinite(self.risk_aversion) or self.risk_aversion < 0.0:
            raise FinanceValidationError(
                f"risk_adjusted objective {self.name!r} risk_aversion must be a "
                f"finite value >= 0, got {self.risk_aversion!r}"
            )

    def validate(self, assets: AssetUniverse, risk: RiskMatrix | None) -> list[str]:
        if self.risk_aversion == 0.0:
            return []
        if risk is None:
            return [
                f"risk_adjusted objective {self.name!r} requires a risk matrix "
                "when risk_aversion > 0"
            ]
        if not risk.psd:
            return [
                f"risk_adjusted objective {self.name!r} requires a risk matrix "
                "that is positive semidefinite"
            ]
        return []

    def to_quantum_objective(
        self,
        assets: AssetUniverse,
        context: FinancialContext | None = None,
        risk: RiskMatrix | None = None,
    ) -> Objective:
        variables = variable_names(len(assets))
        return_coefficients = [asset.expected_return for asset in assets]
        return_expression = linear_string(return_coefficients, variables)
        if self.risk_aversion == 0.0:
            return Objective(
                self.name,
                ObjectiveSense.MAXIMIZE,
                expression=return_expression,
                metadata={"finance_kind": self.kind, "risk_aversion": float(self.risk_aversion)},
            )
        if risk is None:
            raise FinanceValidationError(
                f"risk_adjusted objective {self.name!r} requires a risk matrix "
                "when risk_aversion > 0"
            )
        risk.require_psd()
        risk_terms = RiskObjective._risk_terms(assets, risk)
        risk_expression = quadratic_string(risk_terms)
        expression = f"{return_expression} - {fmt_number(self.risk_aversion)}*({risk_expression})"
        return Objective(
            self.name,
            ObjectiveSense.MAXIMIZE,
            expression=expression,
            metadata={"finance_kind": self.kind, "risk_aversion": float(self.risk_aversion)},
        )

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data["risk_aversion"] = float(self.risk_aversion)
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RiskAdjustedObjective:
        return cls(
            name=str(data["name"]),
            description=str(data.get("description", "")),
            risk_aversion=float(data.get("risk_aversion", 1.0)),
        )


_OBJECTIVE_KINDS: dict[str, type[FinancialObjective]] = {
    ExpectedReturnObjective.kind: ExpectedReturnObjective,
    RiskObjective.kind: RiskObjective,
    RiskAdjustedObjective.kind: RiskAdjustedObjective,
}


def objective_from_dict(data: dict[str, Any]) -> FinancialObjective:
    """Rebuild a financial objective from its serialized ``kind``.

    Raises:
        FinanceValidationError: If the kind is unknown.
    """
    kind = data.get("kind")
    cls = _OBJECTIVE_KINDS.get(str(kind)) if kind is not None else None
    if cls is None:
        raise FinanceValidationError(f"unknown financial objective kind {kind!r}")
    return cls.from_dict(data)
