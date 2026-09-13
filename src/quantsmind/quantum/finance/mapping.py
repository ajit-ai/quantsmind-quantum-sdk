"""Deterministic asset <-> variable mapping and solution decoding.

QMQ-07 establishes the canonical mapping::

    asset identifier <-> decision variable (``x<i>``) <-> variable index

and the generic infrastructure to decode a future optimization result back
into financial asset decisions.  QMQ-08 builds the actual portfolio workflow
on top of this.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from quantsmind.quantum.finance.errors import FinanceValidationError
from quantsmind.quantum.finance.weights import AllocationKind

if TYPE_CHECKING:
    from quantsmind.quantum.finance.models import FinancialProblem

__all__ = ["FinanceAssetMapper", "AssetMapping", "DecodedAsset"]


@dataclass
class DecodedAsset:
    """A decoded asset decision from an assignment.

    Args:
        asset_id: The asset identifier.
        index: Deterministic variable index of the asset.
        variable_name: The decision-variable name (``x<i>``).
        symbol: Optional asset symbol.
        value: The assigned value in the solution.
        selected: Whether the value exceeds the selection threshold.
    """

    asset_id: str
    index: int
    variable_name: str
    symbol: str = ""
    value: float = 0.0
    selected: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "asset_id": self.asset_id,
            "index": self.index,
            "variable_name": self.variable_name,
            "symbol": self.symbol,
            "value": float(self.value),
            "selected": bool(self.selected),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DecodedAsset:
        """Rebuild a DecodedAsset from :meth:`to_dict` output."""
        return cls(
            asset_id=str(data["asset_id"]),
            index=int(data.get("index", -1)),
            variable_name=str(data.get("variable_name", "")),
            symbol=str(data.get("symbol", "")),
            value=float(data.get("value", 0.0)),
            selected=bool(data.get("selected", False)),
        )


@dataclass
class AssetMapping:
    """The deterministic asset <-> variable <-> index mapping of a problem.

    Args:
        problem_name: Name of the originating financial problem.
        asset_order: Ordered asset identifiers (universe order).
        allocation_kind: Allocation representation of the problem.
        symbols: Optional asset identifier -> symbol lookup.
    """

    problem_name: str
    asset_order: list[str]
    allocation_kind: AllocationKind
    symbols: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.allocation_kind = AllocationKind.parse(self.allocation_kind)
        seen: set[str] = set()
        for identifier in self.asset_order:
            if not identifier:
                raise FinanceValidationError("asset identifiers must be non-empty")
            if identifier in seen:
                raise FinanceValidationError(
                    f"duplicate asset identifier {identifier!r} in asset mapping"
                )
            seen.add(identifier)

    def __len__(self) -> int:
        return len(self.asset_order)

    @property
    def variable_names(self) -> list[str]:
        """Decision-variable names in asset order (``x0, x1, ...``)."""
        return [f"x{index}" for index in range(len(self.asset_order))]

    def index(self, identifier: str) -> int:
        """Return the variable index of an asset identifier."""
        if identifier not in self.asset_order:
            raise KeyError(f"asset {identifier!r} not in mapping for {self.problem_name!r}")
        return self.asset_order.index(identifier)

    def variable(self, identifier: str) -> str:
        """Return the decision-variable name of an asset identifier."""
        return f"x{self.index(identifier)}"

    def asset(self, variable_name: str) -> str:
        """Return the asset identifier for a decision-variable name.

        Raises:
            KeyError: If the variable name is outside the mapping.
        """
        if not variable_name.startswith("x"):
            raise KeyError(f"variable {variable_name!r} is not a mapped decision variable")
        try:
            index = int(variable_name[1:])
        except ValueError:
            raise KeyError(
                f"variable {variable_name!r} is not a mapped decision variable"
            ) from None
        if index < 0 or index >= len(self.asset_order):
            raise KeyError(f"variable {variable_name!r} is outside the mapping")
        return self.asset_order[index]

    def decode_assignments(
        self,
        assignments: dict[str, Any],
        *,
        selected_threshold: float = 0.5,
    ) -> list[DecodedAsset]:
        """Decode an assignment back into ordered asset decisions.

        Keys may be decision-variable names (``x0``) or asset identifiers;
        unknown keys (e.g. QUBO slack variables) are ignored.  ``selected``
        is ``value > selected_threshold``.
        """
        decoded: list[DecodedAsset] = []
        for index, identifier in enumerate(self.asset_order):
            variable = f"x{index}"
            value = assignments.get(variable, assignments.get(identifier, 0.0))
            decoded.append(
                DecodedAsset(
                    asset_id=identifier,
                    index=index,
                    variable_name=variable,
                    symbol=self.symbols.get(identifier, ""),
                    value=float(value),
                    selected=float(value) > float(selected_threshold),
                )
            )
        return decoded

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "problem_name": self.problem_name,
            "asset_order": list(self.asset_order),
            "allocation_kind": self.allocation_kind.name.lower(),
            "symbols": dict(self.symbols),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AssetMapping:
        """Rebuild an AssetMapping from :meth:`to_dict` output."""
        return cls(
            problem_name=str(data.get("problem_name", "")),
            asset_order=[str(x) for x in data.get("asset_order", [])],
            allocation_kind=AllocationKind.parse(data.get("allocation_kind", "continuous")),
            symbols={str(k): str(v) for k, v in data.get("symbols", {}).items()},
        )


class FinanceAssetMapper:
    """Builds the deterministic :class:`AssetMapping` of a financial problem."""

    def map(self, problem: FinancialProblem) -> AssetMapping:
        """Return the asset -> variable mapping of a financial problem.

        Raises:
            FinanceValidationError: If the problem is invalid.
        """
        issues = problem.validate()
        if issues:
            raise FinanceValidationError(
                f"invalid financial problem {problem.name!r}: " + "; ".join(issues)
            )
        symbols = {asset.identifier: asset.symbol for asset in problem.universe if asset.symbol}
        return AssetMapping(
            problem_name=problem.name,
            asset_order=problem.universe.identifier_order(),
            allocation_kind=problem.allocation_kind,
            symbols=symbols,
        )
