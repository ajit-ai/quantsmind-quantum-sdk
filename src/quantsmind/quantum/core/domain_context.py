"""Domain context for quantum domain problems.

A :class:`DomainContext` describes the environment a problem lives in
(``finance``, ``fraud``, ``manufacturing``, ``energy``, ...).  QMQ-01
provides the foundation only; concrete domain modules extend it later.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DomainContext:
    """Context in which a quantum domain problem exists.

    Args:
        domain: Top-level domain (e.g. ``"finance"``, ``"fraud"``, ``"energy"``).
        subdomain: Optional subdomain (e.g. ``"portfolio"``).
        use_case: Optional business/scientific use case.
        context_metadata: Domain-specific business/scientific metadata.
        units: Applicable measurement units (e.g. ``["USD", "days"]``).
        metadata: Free-form custom metadata.

    Raises:
        ValueError: If ``domain`` is empty.
    """

    domain: str
    subdomain: str = ""
    use_case: str = ""
    context_metadata: dict[str, Any] = field(default_factory=dict)
    units: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.domain.strip():
            raise ValueError("domain must be a non-empty string")

    def qualified(self) -> str:
        """Return ``"domain"`` or ``"domain/subdomain"``."""
        if self.subdomain:
            return f"{self.domain}/{self.subdomain}"
        return self.domain

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "domain": self.domain,
            "subdomain": self.subdomain,
            "use_case": self.use_case,
            "context_metadata": dict(self.context_metadata),
            "units": list(self.units),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DomainContext:
        """Rebuild a DomainContext from :meth:`to_dict` output."""
        return cls(
            domain=str(data["domain"]),
            subdomain=str(data.get("subdomain", "")),
            use_case=str(data.get("use_case", "")),
            context_metadata=dict(data.get("context_metadata", {})),
            units=list(data.get("units", [])),
            metadata=dict(data.get("metadata", {})),
        )

    def __repr__(self) -> str:
        return f"DomainContext(domain={self.qualified()!r})"


__all__ = ["DomainContext"]
