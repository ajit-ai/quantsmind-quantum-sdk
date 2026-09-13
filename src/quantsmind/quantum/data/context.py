"""QMQ-09 data context and domain-context mapping.

:class:`DataContext` captures the domain intent behind a Data problem
(purpose, subdomain, the distance metric and feature weights used for
similarity, and an optional preferred computation strategy).  It maps onto
the QMQ-01 :class:`DomainContext` used by the formulation and workflow
layers through :meth:`DataContext.to_domain_context`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from quantsmind.quantum.data.errors import DataValidationError

if TYPE_CHECKING:
    from quantsmind.quantum.core.domain_context import DomainContext

__all__ = ["DataContext", "DISTANCE_METRICS"]

DISTANCE_METRICS = frozenset({"euclidean", "squared_euclidean", "weighted_euclidean"})


@dataclass
class DataContext:
    """Data-domain context of a Data problem.

    Args:
        purpose: Free-form purpose label (e.g. ``"feature_selection"``,
            ``"clustering"``, ``"analysis"``).
        subdomain: Domain subdomain (e.g. ``"tabular"``).
        distance_metric: One of :data:`DISTANCE_METRICS` used for pairwise
            relationships, similarity and clustering distance objectives.
        feature_weights: Optional per-feature weights for the weighted
            Euclidean distance (feature name -> non-negative weight).
        similarity_sigma: Kernel width of the Gaussian similarity transform.
        preferred_strategy: Optional preferred computation strategy label;
            validated against the existing strategy vocabulary when not empty.
        assumptions: Free-form modelling assumptions (JSON-safe).
        metadata: Free-form metadata (JSON-safe).
    """

    purpose: str = ""
    subdomain: str = ""
    distance_metric: str = "euclidean"
    feature_weights: dict[str, float] = field(default_factory=dict)
    similarity_sigma: float = 1.0
    preferred_strategy: str = ""
    assumptions: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.distance_metric not in DISTANCE_METRICS:
            raise DataValidationError(
                f"unknown distance metric {self.distance_metric!r}; "
                f"expected one of {sorted(DISTANCE_METRICS)}"
            )
        sigma = float(self.similarity_sigma)
        if not _finite(sigma) or sigma <= 0.0:
            raise DataValidationError("similarity_sigma must be a finite positive number")
        for feature, weight in self.feature_weights.items():
            if not feature:
                raise DataValidationError("feature weight names cannot be empty")
            if not _finite(float(weight)) or float(weight) < 0.0:
                raise DataValidationError(
                    f"feature weight for {feature!r} must be finite and non-negative"
                )
        if self.preferred_strategy:
            try:
                from quantsmind.quantum.strategy.strategy import ComputationStrategy

                ComputationStrategy.parse(self.preferred_strategy)
            except Exception as exc:  # pragma: no cover - defensive
                raise DataValidationError(
                    f"unknown preferred strategy {self.preferred_strategy!r}"
                ) from exc

    def to_domain_context(self) -> DomainContext:
        """Return the QMQ-01 domain context used by the formulation layers."""
        from quantsmind.quantum.core.domain_context import DomainContext

        return DomainContext(
            domain="data",
            subdomain=self.subdomain or "tabular",
            use_case="optimization",
            context_metadata={
                "purpose": self.purpose,
                "distance_metric": self.distance_metric,
                "similarity_sigma": float(self.similarity_sigma),
                "preferred_strategy": self.preferred_strategy,
            },
            units=[],
            metadata={
                "data": {
                    "feature_weights": dict(self.feature_weights),
                    "assumptions": dict(self.assumptions),
                }
            },
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "purpose": self.purpose,
            "subdomain": self.subdomain,
            "distance_metric": self.distance_metric,
            "feature_weights": {name: float(w) for name, w in self.feature_weights.items()},
            "similarity_sigma": float(self.similarity_sigma),
            "preferred_strategy": self.preferred_strategy,
            "assumptions": dict(self.assumptions),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DataContext:
        """Rebuild a context from :meth:`to_dict` output."""
        return cls(
            purpose=str(data.get("purpose", "")),
            subdomain=str(data.get("subdomain", "")),
            distance_metric=str(data.get("distance_metric", "euclidean")),
            feature_weights={
                name: float(weight) for name, weight in data.get("feature_weights", {}).items()
            },
            similarity_sigma=float(data.get("similarity_sigma", 1.0)),
            preferred_strategy=str(data.get("preferred_strategy", "")),
            assumptions=dict(data.get("assumptions", {})),
            metadata=dict(data.get("metadata", {})),
        )


def _finite(value: float) -> bool:
    import math

    return math.isfinite(value)
