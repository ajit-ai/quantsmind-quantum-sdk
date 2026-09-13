"""Core financial models of the Finance domain layer.

This module owns the strongly typed, validated financial domain objects:
:class:`FinancialInstrument`, :class:`Asset`, :class:`AssetUniverse` and the
:class:`FinancialProblem` that connects universe, context, objectives,
constraints and risk information.  Building these objects never invokes a
quantum engine.
"""

from __future__ import annotations

import math
from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from quantsmind.quantum.core.variable import Variable, VariableType
from quantsmind.quantum.finance.errors import FinanceValidationError
from quantsmind.quantum.finance.weights import AllocationKind

if TYPE_CHECKING:
    from quantsmind.quantum.finance.budget import Budget
    from quantsmind.quantum.finance.constraints import FinancialConstraint
    from quantsmind.quantum.finance.context import FinancialContext
    from quantsmind.quantum.finance.objectives import FinancialObjective
    from quantsmind.quantum.finance.risk import RiskMatrix

__all__ = [
    "FinancialInstrument",
    "Asset",
    "AssetUniverse",
    "FinancialProblem",
]


@dataclass
class FinancialInstrument:
    """Identity of a financial instrument.

    Args:
        identifier: Unique, non-empty instrument identifier (e.g. ``"USD"``).
        symbol: Optional ticker/symbol; defaults to the identifier.
        name: Optional human-readable name; defaults to the identifier.
        description: Optional description.
        metadata: Free-form metadata.

    Raises:
        FinanceValidationError: If the identifier is empty.
    """

    identifier: str
    symbol: str = ""
    name: str = ""
    description: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.identifier or not self.identifier.strip():
            raise FinanceValidationError("instrument identifier must be a non-empty string")
        self.symbol = self.symbol or self.identifier
        self.name = self.name or self.identifier

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "identifier": self.identifier,
            "symbol": self.symbol,
            "name": self.name,
            "description": self.description,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FinancialInstrument:
        """Rebuild a FinancialInstrument from :meth:`to_dict` output."""
        return cls(
            identifier=str(data["identifier"]),
            symbol=str(data.get("symbol", "")),
            name=str(data.get("name", "")),
            description=str(data.get("description", "")),
            metadata=dict(data.get("metadata", {})),
        )


@dataclass
class Asset(FinancialInstrument):
    """An instrument extended with optimization-relevant financial data.

    Args:
        expected_return: Supplied expected return (may be negative).
        price: Optional unit price/value (must be positive when set).
        volatility: Optional annualized volatility (``>= 0`` when set).
        asset_class: Optional group label (e.g. ``"equity"``, ``"bond"``),
            used by :class:`~quantsmind.quantum.finance.constraints
            .GroupAllocationConstraint`.

    Raises:
        FinanceValidationError: If a numeric field is not finite or violates
            its documented domain.
    """

    expected_return: float = 0.0
    price: float | None = None
    volatility: float | None = None
    asset_class: str = ""

    def __post_init__(self) -> None:
        super().__post_init__()
        if not math.isfinite(self.expected_return):
            raise FinanceValidationError(
                f"expected_return of asset {self.identifier!r} must be finite, "
                f"got {self.expected_return!r}"
            )
        if self.price is not None and (not math.isfinite(self.price) or self.price <= 0.0):
            raise FinanceValidationError(
                f"price of asset {self.identifier!r} must be a finite value > 0, got {self.price!r}"
            )
        if self.volatility is not None and (
            not math.isfinite(self.volatility) or self.volatility < 0.0
        ):
            raise FinanceValidationError(
                f"volatility of asset {self.identifier!r} must be a finite "
                f"value >= 0, got {self.volatility!r}"
            )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        data = super().to_dict()
        data["expected_return"] = float(self.expected_return)
        data["price"] = self.price
        data["volatility"] = self.volatility
        data["asset_class"] = self.asset_class
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Asset:
        """Rebuild an Asset from :meth:`to_dict` output."""
        return cls(
            identifier=str(data["identifier"]),
            symbol=str(data.get("symbol", "")),
            name=str(data.get("name", "")),
            description=str(data.get("description", "")),
            metadata=dict(data.get("metadata", {})),
            expected_return=float(data.get("expected_return", 0.0)),
            price=float(data["price"]) if data.get("price") is not None else None,
            volatility=(float(data["volatility"]) if data.get("volatility") is not None else None),
            asset_class=str(data.get("asset_class", "")),
        )


@dataclass
class AssetUniverse:
    """An ordered, validated collection of financial assets.

    Deterministic ordering is preserved from construction (insertion order)
    because QUBO variable mapping depends on deterministic variable indices.
    Duplicate identifiers are rejected.

    Args:
        assets: Ordered list of assets.
        name: Optional universe name (may be empty).

    Raises:
        FinanceValidationError: If an identifier is empty or repeated.
    """

    assets: list[Asset]
    name: str = ""
    _index: dict[str, Asset] = field(default_factory=dict, init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        seen: set[str] = set()
        for asset in self.assets:
            if asset.identifier in seen:
                raise FinanceValidationError(
                    f"duplicate asset identifier {asset.identifier!r} in universe"
                )
            seen.add(asset.identifier)
        self._index = {asset.identifier: asset for asset in self.assets}

    def __len__(self) -> int:
        return len(self.assets)

    def __iter__(self) -> Iterator[Asset]:
        return iter(self.assets)

    def __getitem__(self, index: int) -> Asset:
        return self.assets[index]

    def __contains__(self, identifier: object) -> bool:
        return isinstance(identifier, str) and identifier in self._index

    def has(self, identifier: str) -> bool:
        """Return whether an asset identifier is in the universe."""
        return identifier in self._index

    def asset(self, identifier: str) -> Asset:
        """Return the asset with the given identifier.

        Raises:
            KeyError: If the identifier is not in the universe.
        """
        if identifier not in self._index:
            raise KeyError(f"asset {identifier!r} not in universe {self.name!r}")
        return self._index[identifier]

    def index_of(self, identifier: str) -> int:
        """Return the deterministic index of an asset identifier.

        Raises:
            KeyError: If the identifier is not in the universe.
        """
        for index, asset in enumerate(self.assets):
            if asset.identifier == identifier:
                return index
        raise KeyError(f"asset {identifier!r} not in universe {self.name!r}")

    def identifier_order(self) -> list[str]:
        """Return the deterministic ordered asset identifiers."""
        return [asset.identifier for asset in self.assets]

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "name": self.name,
            "assets": [asset.to_dict() for asset in self.assets],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AssetUniverse:
        """Rebuild an AssetUniverse from :meth:`to_dict` output."""
        return cls(
            assets=[Asset.from_dict(d) for d in data.get("assets", [])],
            name=str(data.get("name", "")),
        )


@dataclass
class FinancialProblem:
    """A complete financial optimization problem definition.

    Connects an :class:`AssetUniverse`, optional :class:`FinancialContext`
    and :class:`RiskMatrix`, financial objectives, financial constraints and
    an :class:`AllocationKind`.  Construction never invokes a quantum engine.

    Args:
        name: Unique problem name.
        universe: The available financial assets.
        objectives: Financial objectives (at least one).
        constraints: Financial constraints.
        context: Optional financial metadata/configuration.
        risk: Optional covariance/risk matrix over the universe.
        allocation_kind: How the allocation is represented
            (``continuous`` / ``binary`` / ``integer``).
        description: Optional description.
        metadata: Free-form metadata.

    Raises:
        FinanceValidationError: If the name is empty or objective/constraint
            names repeat.
    """

    name: str
    universe: AssetUniverse
    objectives: list[FinancialObjective] = field(default_factory=list)
    constraints: list[FinancialConstraint] = field(default_factory=list)
    context: FinancialContext | None = None
    risk: RiskMatrix | None = None
    allocation_kind: AllocationKind = AllocationKind.CONTINUOUS
    description: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.name:
            raise FinanceValidationError("problem name must be a non-empty string")
        self.allocation_kind = AllocationKind.parse(self.allocation_kind)
        self._assert_unique("objective", [o.name for o in self.objectives])
        self._assert_unique("constraint", [c.name for c in self.constraints])

    @staticmethod
    def _assert_unique(kind: str, names: list[str]) -> None:
        seen: set[str] = set()
        duplicates: list[str] = []
        for name in names:
            if name in seen:
                duplicates.append(name)
            seen.add(name)
        if duplicates:
            raise FinanceValidationError(
                f"duplicate {kind} name(s) in financial problem: {sorted(set(duplicates))}"
            )

    # -- decision variables ----------------------------------------------

    @property
    def size(self) -> int:
        """Number of assets (one decision variable per asset)."""
        return len(self.universe)

    @property
    def decision_variables(self) -> list[Variable]:
        """Deterministic decision variables following the ``x<i>`` convention.

        One variable per asset in universe order.  ``continuous`` yields
        long-only ``[0, inf)`` weights, ``binary`` yields 0/1 selection.
        ``integer`` is intentionally not defined here: the portfolio
        representation is a QMQ-08 decision.
        """
        variables: list[Variable] = []
        for index, asset in enumerate(self.universe):
            name = f"x{index}"
            description = f"allocation for {asset.identifier}"
            metadata = {"asset_id": asset.identifier}
            if asset.symbol:
                metadata["asset_symbol"] = asset.symbol
            if self.allocation_kind is AllocationKind.BINARY:
                variables.append(
                    Variable(
                        name,
                        VariableType.BINARY,
                        domain="asset",
                        description=description,
                        metadata=metadata,
                    )
                )
            elif self.allocation_kind is AllocationKind.CONTINUOUS:
                variables.append(
                    Variable(
                        name,
                        VariableType.CONTINUOUS,
                        lower_bound=0.0,
                        upper_bound=None,
                        domain="asset",
                        description=description,
                        metadata=metadata,
                    )
                )
            else:
                raise FinanceValidationError(
                    "integer allocation representation is not defined by QMQ-07; "
                    "the portfolio variable representation is a QMQ-08 decision"
                )
        return variables

    # -- validation ------------------------------------------------------

    def validate(self) -> list[str]:
        """Return a list of human-actionable validation issues.

        An empty list means the problem is a valid input to the formulation
        adapter.  Validation never raises; use :meth:`raise_if_invalid`.
        """
        issues: list[str] = []
        if not self.universe.assets:
            issues.append("financial problem has no assets in its universe")
        if not self.objectives:
            issues.append("financial problem has no objectives")
        if self.risk is not None:
            expected = self.universe.identifier_order()
            if self.risk.asset_order != expected:
                issues.append(f"risk matrix asset_order must match the universe order ({expected})")
        for objective in self.objectives:
            issues.extend(objective.validate(self.universe, self.risk))
        for constraint in self.constraints:
            issues.extend(constraint.validate(self.universe))
        return issues

    def raise_if_invalid(self) -> None:
        """Raise :class:`FinanceValidationError` listing all issues.

        Raises:
            FinanceValidationError: If :meth:`validate` returns any issue.
        """
        issues = self.validate()
        if issues:
            details = "; ".join(issues)
            raise FinanceValidationError(f"invalid financial problem {self.name!r}: {details}")

    def to_budget_constraint(self, budget: Budget, name: str = "budget") -> None:
        """Convenience: append a budget constraint derived from a :class:`Budget`.

        The aggregate allocation is bounded by ``budget.total``; when
        ``min_allocation`` / ``max_allocation`` are set they bound the sum
        as well (as minimum/maximum aggregate allocation constraints).
        """
        from quantsmind.quantum.finance.constraints import (
            BudgetConstraint,
            CardinalityConstraint,
        )

        if self.constraint_exists(name):
            raise FinanceValidationError(
                f"constraint {name!r} already exists in financial problem {self.name!r}"
            )
        self.constraints.append(
            BudgetConstraint(name=name, total=budget.total, currency=budget.currency)
        )
        lower = budget.min_allocation
        upper = budget.max_allocation
        if lower is not None and upper is None:
            self.constraints.append(
                CardinalityConstraint(
                    name=f"{name}_min_allocation", min_assets=lower, max_assets=None
                )
            )
        elif upper is not None and lower is None:
            self.constraints.append(
                CardinalityConstraint(name=f"{name}_max_allocation", min_assets=0, max_assets=upper)
            )
        elif lower is not None and upper is not None:
            self.constraints.append(
                CardinalityConstraint(name=f"{name}_allocation", min_assets=lower, max_assets=upper)
            )

    def constraint_exists(self, name: str) -> bool:
        """Return whether a constraint with the given name already exists."""
        return any(constraint.name == name for constraint in self.constraints)

    # -- serialization ---------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "universe": self.universe.to_dict(),
            "objectives": [o.to_dict() for o in self.objectives],
            "constraints": [c.to_dict() for c in self.constraints],
            "context": self.context.to_dict() if self.context is not None else None,
            "risk": self.risk.to_dict() if self.risk is not None else None,
            "allocation_kind": self.allocation_kind.name.lower(),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FinancialProblem:
        """Rebuild a FinancialProblem from :meth:`to_dict` output."""
        from quantsmind.quantum.finance.constraints import constraint_from_dict
        from quantsmind.quantum.finance.context import FinancialContext
        from quantsmind.quantum.finance.objectives import objective_from_dict
        from quantsmind.quantum.finance.risk import RiskMatrix

        return cls(
            name=str(data["name"]),
            description=str(data.get("description", "")),
            universe=AssetUniverse.from_dict(data["universe"]),
            objectives=[objective_from_dict(d) for d in data.get("objectives", [])],
            constraints=[constraint_from_dict(d) for d in data.get("constraints", [])],
            context=(
                FinancialContext.from_dict(data["context"])
                if data.get("context") is not None
                else None
            ),
            risk=(RiskMatrix.from_dict(data["risk"]) if data.get("risk") is not None else None),
            allocation_kind=AllocationKind.parse(data.get("allocation_kind", "continuous")),
            metadata=dict(data.get("metadata", {})),
        )

    def __repr__(self) -> str:
        return (
            f"FinancialProblem(name={self.name!r}, assets={self.size}, "
            f"objectives={len(self.objectives)}, constraints={len(self.constraints)}, "
            f"allocation_kind={self.allocation_kind.name.lower()})"
        )


__all__ = ["FinancialInstrument", "Asset", "AssetUniverse", "FinancialProblem"]
