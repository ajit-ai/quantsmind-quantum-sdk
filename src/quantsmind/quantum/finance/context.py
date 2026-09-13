"""Financial problem context of the Finance domain layer.

A :class:`FinancialContext` is the metadata/model configuration of a
financial problem: currency, horizon, assumptions and model settings.  It is
**not** an external data-ingestion framework — QMQ-07 works entirely from
supplied data.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

from quantsmind.quantum.core.domain_context import DomainContext
from quantsmind.quantum.finance.errors import FinanceValidationError

__all__ = ["FinancialContext"]


@dataclass
class FinancialContext:
    """Financial metadata and model configuration.

    Args:
        currency: Optional currency code (metadata only; no conversion).
        subdomain: Finance subdomain (e.g. ``"portfolio"``).
        investment_horizon: Optional horizon label (e.g. ``"1Y"``).
        risk_free_rate: Optional risk-free rate used by risk-adjusted models.
        transaction_cost_rate: Assumed proportional transaction-cost rate.
        assumptions: Named model assumptions (JSON-safe values).
        metadata: Free-form metadata.

    Raises:
        FinanceValidationError: If a numeric field is invalid.
    """

    currency: str = ""
    subdomain: str = ""
    investment_horizon: str = ""
    risk_free_rate: float | None = None
    transaction_cost_rate: float = 0.0
    assumptions: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.risk_free_rate is not None and not math.isfinite(self.risk_free_rate):
            raise FinanceValidationError(
                f"risk_free_rate must be finite, got {self.risk_free_rate!r}"
            )
        if not math.isfinite(self.transaction_cost_rate) or self.transaction_cost_rate < 0.0:
            raise FinanceValidationError(
                "transaction_cost_rate must be a finite value >= 0, got "
                f"{self.transaction_cost_rate!r}"
            )

    def to_domain_context(self) -> DomainContext:
        """Derive the generic QMQ :class:`DomainContext` for this finance."""
        context_metadata: dict[str, Any] = {
            "currency": self.currency,
            "investment_horizon": self.investment_horizon,
            "risk_free_rate": self.risk_free_rate,
            "transaction_cost_rate": self.transaction_cost_rate,
        }
        return DomainContext(
            domain="finance",
            subdomain=self.subdomain,
            use_case="optimization",
            context_metadata=context_metadata,
            units=[self.currency] if self.currency else [],
            metadata={"assumptions": dict(self.assumptions)},
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "currency": self.currency,
            "subdomain": self.subdomain,
            "investment_horizon": self.investment_horizon,
            "risk_free_rate": self.risk_free_rate,
            "transaction_cost_rate": float(self.transaction_cost_rate),
            "assumptions": dict(self.assumptions),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FinancialContext:
        """Rebuild a FinancialContext from :meth:`to_dict` output."""
        risk_free_rate = data.get("risk_free_rate")
        return cls(
            currency=str(data.get("currency", "")),
            subdomain=str(data.get("subdomain", "")),
            investment_horizon=str(data.get("investment_horizon", "")),
            risk_free_rate=float(risk_free_rate) if risk_free_rate is not None else None,
            transaction_cost_rate=float(data.get("transaction_cost_rate", 0.0)),
            assumptions=dict(data.get("assumptions", {})),
            metadata=dict(data.get("metadata", {})),
        )
