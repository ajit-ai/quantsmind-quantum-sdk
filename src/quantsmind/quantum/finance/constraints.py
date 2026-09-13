"""Financial constraints of the Finance domain layer.

Each :class:`FinancialConstraint` is a validated, serializable domain
constraint that materializes into the existing QMQ
:class:`~quantsmind.quantum.core.constraint.Constraint` objects used by the
formulation layer.  Every constraint carries an identifier, a description,
validation, a documented mathematical meaning and serialization.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, ClassVar

from quantsmind.quantum.core.constraint import Constraint
from quantsmind.quantum.finance._expr import linear_string, variable_name, variable_names
from quantsmind.quantum.finance.errors import FinanceValidationError

if TYPE_CHECKING:
    from quantsmind.quantum.finance.models import AssetUniverse

__all__ = [
    "FinancialConstraint",
    "BudgetConstraint",
    "WeightBoundsConstraint",
    "CardinalityConstraint",
    "PositionLimitConstraint",
    "GroupAllocationConstraint",
    "constraint_from_dict",
]


@dataclass
class FinancialConstraint:
    """Base class of financial constraints.

    Args:
        name: Unique constraint name.
        description: Optional human-readable description.

    Raises:
        FinanceValidationError: If the name is empty.
    """

    name: str
    description: str = ""

    kind: ClassVar[str] = "financial"

    def __post_init__(self) -> None:
        if not self.name:
            raise FinanceValidationError("constraint name must be a non-empty string")

    def validate(self, assets: AssetUniverse) -> list[str]:
        """Return validation issues against an asset universe (empty = valid)."""
        return []

    def to_quantum_constraints(self, assets: AssetUniverse) -> list[Constraint]:
        """Materialize into existing QMQ constraints.

        Raises:
            NotImplementedError: On the base class.
        """
        raise NotImplementedError(f"{type(self).__name__} must implement to_quantum_constraints()")

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary (kind included)."""
        return {
            "kind": self.kind,
            "name": self.name,
            "description": self.description,
        }

    def _variables(self, assets: AssetUniverse) -> list[str]:
        return variable_names(len(assets))

    def _names(self, assets: AssetUniverse) -> list[int]:
        return list(range(len(assets)))

    def __repr__(self) -> str:
        return f"{type(self).__name__}(name={self.name!r})"


@dataclass
class BudgetConstraint(FinancialConstraint):
    """Budget limit: ``sum(cost_i * x_i) <= total``.

    Without costs the aggregate allocation is bounded: ``sum(x_i) <= total``.
    ``costs`` maps asset identifier -> cost per unit of allocation; missing
    assets use a unit cost of 1.
    """

    total: float = 1.0
    currency: str = ""
    costs: dict[str, float] | None = None

    kind: ClassVar[str] = "budget"

    def __post_init__(self) -> None:
        super().__post_init__()
        if not math.isfinite(self.total) or self.total <= 0.0:
            raise FinanceValidationError(
                f"budget constraint {self.name!r} total must be a finite value "
                f"> 0, got {self.total!r}"
            )
        if self.costs is not None:
            for identifier, cost in self.costs.items():
                if not math.isfinite(cost):
                    raise FinanceValidationError(
                        f"cost of asset {identifier!r} must be finite, got {cost!r}"
                    )

    def validate(self, assets: AssetUniverse) -> list[str]:
        issues: list[str] = []
        if self.costs is not None:
            missing = sorted(set(self.costs) - {a.identifier for a in assets})
            if missing:
                issues.append(
                    f"budget constraint {self.name!r} references unknown assets: {missing}"
                )
        return issues

    def to_quantum_constraints(self, assets: AssetUniverse) -> list[Constraint]:
        variables = self._variables(assets)
        coefficients = [float((self.costs or {}).get(asset.identifier, 1.0)) for asset in assets]
        expression = linear_string(coefficients, variables)
        return [Constraint.le(self.name, expression=expression, value=float(self.total))]

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data["total"] = float(self.total)
        data["currency"] = self.currency
        data["costs"] = (
            {k: float(v) for k, v in self.costs.items()} if self.costs is not None else None
        )
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BudgetConstraint:
        costs = data.get("costs")
        return cls(
            name=str(data["name"]),
            description=str(data.get("description", "")),
            total=float(data.get("total", 1.0)),
            currency=str(data.get("currency", "")),
            costs={str(k): float(v) for k, v in costs.items()} if costs is not None else None,
        )


@dataclass
class WeightBoundsConstraint(FinancialConstraint):
    """Per-asset allocation bounds: ``lower_i <= x_i <= upper_i``."""

    bounds: dict[str, tuple[float, float]] = field(default_factory=dict)

    kind: ClassVar[str] = "weight_bounds"

    def __post_init__(self) -> None:
        super().__post_init__()
        for identifier, (lower, upper) in self.bounds.items():
            if not math.isfinite(lower) or not math.isfinite(upper):
                raise FinanceValidationError(
                    f"weight bounds of asset {identifier!r} must be finite"
                )
            if lower > upper:
                raise FinanceValidationError(
                    f"weight bounds of asset {identifier!r} have lower {lower} > upper {upper}"
                )

    def validate(self, assets: AssetUniverse) -> list[str]:
        missing = sorted(set(self.bounds) - {a.identifier for a in assets})
        if missing:
            return [f"weight bound constraint {self.name!r} references unknown assets: {missing}"]
        return []

    def to_quantum_constraints(self, assets: AssetUniverse) -> list[Constraint]:
        constraints: list[Constraint] = []
        for identifier, (lower, upper) in self.bounds.items():
            if not assets.has(identifier):
                raise FinanceValidationError(
                    f"weight bound constraint {self.name!r} references unknown asset {identifier!r}"
                )
            variable = variable_name(assets.index_of(identifier))
            lower_expr = linear_string([1.0], [variable])
            upper_expr = linear_string([1.0], [variable])
            constraints.append(
                Constraint.ge(f"{self.name}_{identifier}_lower", expression=lower_expr, value=lower)
            )
            constraints.append(
                Constraint.le(f"{self.name}_{identifier}_upper", expression=upper_expr, value=upper)
            )
        return constraints

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data["bounds"] = {
            identifier: [float(lower), float(upper)]
            for identifier, (lower, upper) in self.bounds.items()
        }
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> WeightBoundsConstraint:
        raw = data.get("bounds", {})
        bounds: dict[str, tuple[float, float]] = {}
        for identifier, pair in raw.items():
            bounds[str(identifier)] = (float(pair[0]), float(pair[1]))
        return cls(
            name=str(data["name"]),
            description=str(data.get("description", "")),
            bounds=bounds,
        )


@dataclass
class CardinalityConstraint(FinancialConstraint):
    """Bounded cardinality / aggregate allocation: ``min <= sum(x_i) <= max``.

    Under a binary allocation the sum is the number of selected assets (a
    cardinality bound); under a continuous allocation it bounds the aggregate
    allocation.  Bounds are real values; whole-valued bounds additionally
    participate in a cardinality sanity check against the universe size.
    """

    min_assets: float = 1.0
    max_assets: float | None = None

    kind: ClassVar[str] = "cardinality"

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.min_assets < 0:
            raise FinanceValidationError(
                f"cardinality constraint {self.name!r} min_assets must be >= 0, "
                f"got {self.min_assets}"
            )
        if self.max_assets is not None:
            if not math.isfinite(self.max_assets):
                raise FinanceValidationError(
                    f"cardinality constraint {self.name!r} max_assets must be finite"
                )
            if self.min_assets > self.max_assets:
                raise FinanceValidationError(
                    f"cardinality constraint {self.name!r} has min_assets "
                    f"{self.min_assets} > max_assets {self.max_assets}"
                )

    def validate(self, assets: AssetUniverse) -> list[str]:
        issues: list[str] = []
        count = len(assets)
        if self.min_assets.is_integer() and int(self.min_assets) > count:
            issues.append(
                f"cardinality constraint {self.name!r} min_assets={self.min_assets} "
                f"exceeds the universe size {count}"
            )
        if (
            self.max_assets is not None
            and self.max_assets.is_integer()
            and int(self.max_assets) > count
        ):
            issues.append(
                f"cardinality constraint {self.name!r} max_assets={self.max_assets} "
                f"exceeds the universe size {count}"
            )
        return issues

    def to_quantum_constraints(self, assets: AssetUniverse) -> list[Constraint]:
        constraints: list[Constraint] = []
        variables = self._variables(assets)
        coefficients = [1.0] * len(assets)
        expression = linear_string(coefficients, variables)
        if self.max_assets is not None:
            constraints.append(
                Constraint.le(
                    f"{self.name}_max", expression=expression, value=float(self.max_assets)
                )
            )
        constraints.append(
            Constraint.ge(f"{self.name}_min", expression=expression, value=float(self.min_assets))
        )
        return constraints

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data["min_assets"] = float(self.min_assets)
        data["max_assets"] = self.max_assets
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CardinalityConstraint:
        return cls(
            name=str(data["name"]),
            description=str(data.get("description", "")),
            min_assets=float(data.get("min_assets", 1.0)),
            max_assets=(float(data["max_assets"]) if data.get("max_assets") is not None else None),
        )


@dataclass
class PositionLimitConstraint(FinancialConstraint):
    """Position limits on specific assets: ``lower <= x_i <= upper``."""

    asset_ids: list[str] = field(default_factory=list)
    lower: float | None = None
    upper: float | None = None

    kind: ClassVar[str] = "position_limit"

    def __post_init__(self) -> None:
        super().__post_init__()
        if not self.asset_ids:
            raise FinanceValidationError(
                f"position limit constraint {self.name!r} must name at least one asset"
            )
        if self.lower is not None and not math.isfinite(self.lower):
            raise FinanceValidationError(f"position limit {self.name!r} lower must be finite")
        if self.upper is not None and not math.isfinite(self.upper):
            raise FinanceValidationError(f"position limit {self.name!r} upper must be finite")
        if self.lower is not None and self.upper is not None and self.lower > self.upper:
            raise FinanceValidationError(
                f"position limit {self.name!r} has lower {self.lower} > upper {self.upper}"
            )

    def validate(self, assets: AssetUniverse) -> list[str]:
        missing = sorted(set(self.asset_ids) - {a.identifier for a in assets})
        if missing:
            return [f"position limit constraint {self.name!r} references unknown assets: {missing}"]
        return []

    def to_quantum_constraints(self, assets: AssetUniverse) -> list[Constraint]:
        constraints: list[Constraint] = []
        for identifier in self.asset_ids:
            if not assets.has(identifier):
                raise FinanceValidationError(
                    f"position limit constraint {self.name!r} references unknown asset "
                    f"{identifier!r}"
                )
            variable = variable_name(assets.index_of(identifier))
            expression = linear_string([1.0], [variable])
            if self.lower is not None:
                constraints.append(
                    Constraint.ge(
                        f"{self.name}_{identifier}_lower",
                        expression=expression,
                        value=float(self.lower),
                    )
                )
            if self.upper is not None:
                constraints.append(
                    Constraint.le(
                        f"{self.name}_{identifier}_upper",
                        expression=expression,
                        value=float(self.upper),
                    )
                )
        return constraints

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data["asset_ids"] = list(self.asset_ids)
        data["lower"] = self.lower
        data["upper"] = self.upper
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PositionLimitConstraint:
        return cls(
            name=str(data["name"]),
            description=str(data.get("description", "")),
            asset_ids=[str(x) for x in data.get("asset_ids", [])],
            lower=float(data["lower"]) if data.get("lower") is not None else None,
            upper=float(data["upper"]) if data.get("upper") is not None else None,
        )


@dataclass
class GroupAllocationConstraint(FinancialConstraint):
    """Group allocation limits: ``lower <= sum_{i in group} x_i <= upper``.

    A group is an :attr:`~quantsmind.quantum.finance.models.Asset.asset_class`
    value (e.g. ``"equity"``).
    """

    group: str = ""
    lower: float | None = None
    upper: float | None = None

    kind: ClassVar[str] = "group_allocation"

    def __post_init__(self) -> None:
        super().__post_init__()
        if not self.group:
            raise FinanceValidationError(
                f"group allocation constraint {self.name!r} must name a group"
            )
        if self.lower is not None and not math.isfinite(self.lower):
            raise FinanceValidationError(f"group allocation {self.name!r} lower must be finite")
        if self.upper is not None and not math.isfinite(self.upper):
            raise FinanceValidationError(f"group allocation {self.name!r} upper must be finite")
        if self.lower is not None and self.upper is not None and self.lower > self.upper:
            raise FinanceValidationError(
                f"group allocation {self.name!r} has lower {self.lower} > upper {self.upper}"
            )

    def validate(self, assets: AssetUniverse) -> list[str]:
        members = [asset for asset in assets if asset.asset_class == self.group]
        if not members:
            return [
                f"group allocation constraint {self.name!r} names group {self.group!r} "
                "which has no assets in the universe"
            ]
        return []

    @staticmethod
    def _group_members(assets: AssetUniverse, group: str) -> list[int]:
        indices = [index for index, asset in enumerate(assets) if asset.asset_class == group]
        return indices

    def to_quantum_constraints(self, assets: AssetUniverse) -> list[Constraint]:
        indices = self._group_members(assets, self.group)
        variables = [variable_name(index) for index in indices]
        coefficients = [1.0] * len(indices)
        expression = linear_string(coefficients, variables)
        constraints: list[Constraint] = []
        if self.upper is not None:
            constraints.append(
                Constraint.le(f"{self.name}_upper", expression=expression, value=float(self.upper))
            )
        if self.lower is not None:
            constraints.append(
                Constraint.ge(f"{self.name}_lower", expression=expression, value=float(self.lower))
            )
        return constraints

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data["group"] = self.group
        data["lower"] = self.lower
        data["upper"] = self.upper
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GroupAllocationConstraint:
        return cls(
            name=str(data["name"]),
            description=str(data.get("description", "")),
            group=str(data.get("group", "")),
            lower=float(data["lower"]) if data.get("lower") is not None else None,
            upper=float(data["upper"]) if data.get("upper") is not None else None,
        )


_CONSTRAINT_KINDS: dict[str, Any] = {
    BudgetConstraint.kind: BudgetConstraint,
    WeightBoundsConstraint.kind: WeightBoundsConstraint,
    CardinalityConstraint.kind: CardinalityConstraint,
    PositionLimitConstraint.kind: PositionLimitConstraint,
    GroupAllocationConstraint.kind: GroupAllocationConstraint,
}


def constraint_from_dict(data: dict[str, Any]) -> FinancialConstraint:
    """Rebuild a financial constraint from its serialized ``kind``.

    Raises:
        FinanceValidationError: If the kind is unknown.
    """
    kind = data.get("kind")
    cls = _CONSTRAINT_KINDS.get(str(kind)) if kind is not None else None
    if cls is None:
        raise FinanceValidationError(f"unknown financial constraint kind {kind!r}")
    rebuilt: FinancialConstraint = cls.from_dict(data)
    return rebuilt
