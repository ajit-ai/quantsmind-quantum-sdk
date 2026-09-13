"""Allocation-weight representation of the Finance domain layer.

QMQ-07 introduces the domain concepts required to express allocation
weights and cleanly distinguishes the three representations QMQ-08 will pick
between for the portfolio model: continuous weights, binary selection and
integer quantities.  QMQ-07 ships the concepts; QMQ-08 decides the specific
portfolio representation.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING, Any

from quantsmind.quantum.finance.errors import FinanceValidationError

if TYPE_CHECKING:
    from quantsmind.quantum.finance.models import AssetUniverse

__all__ = ["AllocationKind", "Allocation"]


class AllocationKind(Enum):
    """Representation of an allocation decision.

    Attributes:
        CONTINUOUS: Real-valued weights (e.g. fractions of capital).
        BINARY: 0/1 selection of whether an asset is held.
        INTEGER: Integer quantities (e.g. number of units).
    """

    CONTINUOUS = auto()
    BINARY = auto()
    INTEGER = auto()

    @classmethod
    def parse(cls, value: Any) -> AllocationKind:
        """Coerce a name or member to an :class:`AllocationKind`."""
        if isinstance(value, cls):
            return value
        text = str(value).strip().lower()
        for member in cls:
            if member.name.lower() == text:
                return member
        names = ", ".join(m.name.lower() for m in cls)
        raise FinanceValidationError(f"unknown allocation kind {value!r}; expected one of: {names}")


@dataclass
class Allocation:
    """A validated ``asset -> weight`` allocation over a fixed asset order.

    Args:
        asset_order: Deterministic order of asset identifiers (must match the
            asset universe ordering that formulation relies on).
        weights: Asset identifier -> weight value.  Only identifiers present
            in ``asset_order`` are allowed; missing entries default to 0.
        kind: Reported allocation representation.

    Raises:
        FinanceValidationError: If an identifier is unknown, repeated, or a
            weight is not finite.
    """

    asset_order: list[str]
    weights: dict[str, float] = field(default_factory=dict)
    kind: AllocationKind = AllocationKind.CONTINUOUS

    def __post_init__(self) -> None:
        self.kind = AllocationKind.parse(self.kind)
        seen: set[str] = set()
        for identifier in self.asset_order:
            if not identifier:
                raise FinanceValidationError("asset identifiers must be non-empty")
            if identifier in seen:
                raise FinanceValidationError(
                    f"duplicate asset identifier {identifier!r} in allocation order"
                )
            seen.add(identifier)
        for identifier, value in self.weights.items():
            if identifier not in seen:
                raise FinanceValidationError(f"weight references unknown asset {identifier!r}")
            if not math.isfinite(float(value)):
                raise FinanceValidationError(
                    f"weight of asset {identifier!r} must be finite, got {value!r}"
                )

    def weight(self, identifier: str) -> float:
        """Return the weight of an asset (0 when unset)."""
        return float(self.weights.get(identifier, 0.0))

    def total(self) -> float:
        """Return the sum of all weights in ``asset_order``."""
        return sum(self.weight(identifier) for identifier in self.asset_order)

    @classmethod
    def from_universe(
        cls,
        universe: AssetUniverse,
        weights: dict[str, float],
        *,
        kind: AllocationKind | str = AllocationKind.CONTINUOUS,
    ) -> Allocation:
        """Build an allocation aligned with an asset universe order."""
        order = [asset.identifier for asset in universe.assets]
        known = set(order)
        unknown = sorted(set(weights) - known)
        if unknown:
            raise FinanceValidationError(
                f"weights reference assets outside the universe: {unknown}"
            )
        return cls(asset_order=order, weights=dict(weights), kind=AllocationKind.parse(kind))

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "asset_order": list(self.asset_order),
            "weights": {k: float(v) for k, v in self.weights.items()},
            "kind": self.kind.name.lower(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Allocation:
        """Rebuild an Allocation from :meth:`to_dict` output."""
        return cls(
            asset_order=[str(x) for x in data.get("asset_order", [])],
            weights={str(k): float(v) for k, v in data.get("weights", {}).items()},
            kind=AllocationKind.parse(data.get("kind", "continuous")),
        )
