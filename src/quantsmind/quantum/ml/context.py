"""QMQ-10 ML context and domain-context mapping.

:class:`MLContext` captures the domain intent behind an ML problem (purpose,
subdomain, an optional preferred computation strategy and modelling
assumptions).  It maps onto the QMQ-01 :class:`DomainContext` used by the
formulation and workflow layers through :meth:`MLContext.to_domain_context`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from quantsmind.quantum.ml.errors import MLValidationError

if TYPE_CHECKING:
    from quantsmind.quantum.core.domain_context import DomainContext

__all__ = ["MLContext"]


@dataclass
class MLContext:
    """ML-domain context of an ML problem.

    Args:
        purpose: Free-form purpose label (e.g. ``"classification"``,
            ``"model_selection"``, ``"hyperparameter_optimization"``).
        subdomain: Domain subdomain (e.g. ``"tabular"``).
        preferred_strategy: Optional preferred computation strategy label;
            validated against the existing strategy vocabulary when not empty.
        assumptions: Free-form modelling assumptions (JSON-safe).
        metadata: Free-form metadata (JSON-safe).
    """

    purpose: str = ""
    subdomain: str = "tabular"
    preferred_strategy: str = ""
    assumptions: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.preferred_strategy:
            text = str(self.preferred_strategy).strip().lower()
            try:
                from quantsmind.quantum.strategy.strategy import ComputationStrategy

                ComputationStrategy.parse(text)
            except Exception as exc:  # pragma: no cover - defensive
                raise MLValidationError(
                    f"unknown preferred strategy {self.preferred_strategy!r}"
                ) from exc
            self.preferred_strategy = text

    def to_domain_context(self) -> DomainContext:
        """Return the QMQ-01 domain context used by the formulation layers."""
        from quantsmind.quantum.core.domain_context import DomainContext

        return DomainContext(
            domain="ml",
            subdomain=self.subdomain or "tabular",
            use_case="optimization",
            context_metadata={
                "purpose": self.purpose,
                "preferred_strategy": self.preferred_strategy,
            },
            units=[],
            metadata={
                "ml": {
                    "assumptions": dict(self.assumptions),
                }
            },
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "purpose": self.purpose,
            "subdomain": self.subdomain,
            "preferred_strategy": self.preferred_strategy,
            "assumptions": dict(self.assumptions),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MLContext:
        """Rebuild a context from :meth:`to_dict` output."""
        return cls(
            purpose=str(data.get("purpose", "")),
            subdomain=str(data.get("subdomain", "tabular")),
            preferred_strategy=str(data.get("preferred_strategy", "")),
            assumptions=dict(data.get("assumptions", {})),
            metadata=dict(data.get("metadata", {})),
        )
