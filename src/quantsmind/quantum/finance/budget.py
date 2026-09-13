"""Capital / budget representation of the Finance domain layer.

A :class:`Budget` captures the available capital in nullable currency
metadata plus optional minimum/maximum aggregate-allocation constraints.  It
is a domain concept only — currency conversion and live FX are out of scope.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from quantsmind.quantum.finance.errors import FinanceValidationError

__all__ = ["Budget"]


@dataclass
class Budget:
    """Validated capital / budget representation.

    Args:
        total: Total available budget (allocation units).
        currency: Optional currency code (metadata only).
        min_allocation: Optional minimum aggregate allocation.
        max_allocation: Optional maximum aggregate allocation.

    Raises:
        FinanceValidationError: If totals are invalid or bounds inconsistent.
    """

    total: float
    currency: str = ""
    min_allocation: float | None = None
    max_allocation: float | None = None

    def __post_init__(self) -> None:
        if not math.isfinite(self.total) or self.total <= 0.0:
            raise FinanceValidationError(
                f"budget total must be a finite value > 0, got {self.total!r}"
            )
        for name, value in (
            ("min_allocation", self.min_allocation),
            ("max_allocation", self.max_allocation),
        ):
            if value is not None and not math.isfinite(value):
                raise FinanceValidationError(f"{name} must be finite, got {value!r}")
        if self.min_allocation is not None and self.min_allocation < 0.0:
            raise FinanceValidationError(
                f"min_allocation must be >= 0, got {self.min_allocation!r}"
            )
        if (
            self.min_allocation is not None
            and self.max_allocation is not None
            and self.min_allocation > self.max_allocation
        ):
            raise FinanceValidationError(
                f"min_allocation {self.min_allocation} > max_allocation {self.max_allocation}"
            )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "total": float(self.total),
            "currency": self.currency,
            "min_allocation": self.min_allocation,
            "max_allocation": self.max_allocation,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Budget:
        """Rebuild a Budget from :meth:`to_dict` output."""
        return cls(
            total=float(data["total"]),
            currency=str(data.get("currency", "")),
            min_allocation=(
                float(data["min_allocation"]) if data.get("min_allocation") is not None else None
            ),
            max_allocation=(
                float(data["max_allocation"]) if data.get("max_allocation") is not None else None
            ),
        )
