"""QuantsMind-facing quantum result enrichment.

``QuantumResult`` wraps a MicroQuantum ``BackendResult`` and adds
QuantsMind-specific context: experiment identity, domain metadata and
provenance.  The MicroQuantum result remains directly accessible via
``primitives.native`` — QuantsMind does not re-implement Quantum result
semantics.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from quantsmind.quantum._mq import require_microquantum


@dataclass
class QuantumResult:
    """Enriched result of a QuantsMind quantum experiment.

    Args:
        native: The underlying MicroQuantum ``BackendResult``.
        experiment_id: QuantsMind experiment identity.
        program_name: Name of the originating QuantumProgram.
        domain_metadata: Domain metadata attached by the caller.
        provenance: Execution provenance details.
        created_at: UTC ISO timestamp when this enrichment was created.
    """

    native: Any
    experiment_id: str = ""
    program_name: str = ""
    domain_metadata: dict[str, Any] = field(default_factory=dict)
    provenance: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    @classmethod
    def from_backend_result(
        cls,
        result: Any,
        *,
        experiment_id: str = "",
        program_name: str = "",
        domain_metadata: dict[str, Any] | None = None,
        provenance: dict[str, Any] | None = None,
    ) -> QuantumResult:
        """Wrap a MicroQuantum BackendResult with QuantsMind context."""
        return cls(
            native=result,
            experiment_id=experiment_id,
            program_name=program_name,
            domain_metadata=dict(domain_metadata or {}),
            provenance=dict(provenance or {}),
        )

    # -- MicroQuantum surface passthrough ---------------------------------
    # Read-only access to the underlying result without re-implementing it.

    @property
    def counts(self) -> dict[str, int]:
        """Measurement counts from the backend result."""
        return getattr(self.native, "counts", {})

    @property
    def statevector(self) -> Any:
        """State vector from the backend result (when provided)."""
        return getattr(self.native, "statevector", None)

    @property
    def samples(self) -> list[Any]:
        """Raw samples from the backend result (when provided)."""
        return getattr(self.native, "samples", [])

    @property
    def shots(self) -> int:
        """Number of shots executed."""
        return getattr(self.native, "shots", 0)

    @property
    def backend_name(self) -> str:
        """Name of the backend that produced the result."""
        return getattr(self.native, "backend_name", "")

    @property
    def num_qubits(self) -> int:
        """Number of qubits in the executed circuit."""
        return getattr(self.native, "num_qubits", 0)

    @property
    def success(self) -> bool:
        """Whether the backend reported success."""
        return bool(getattr(self.native, "success", True))

    def to_dict(self) -> dict[str, Any]:
        """Serialize enrichment and underlying result to a JSON-safe dict."""
        native = getattr(self.native, "to_dict", None)
        native_data = native() if callable(native) else repr(self.native)
        return {
            "experiment_id": self.experiment_id,
            "program_name": self.program_name,
            "domain_metadata": dict(self.domain_metadata),
            "provenance": dict(self.provenance),
            "created_at": self.created_at,
            "backend_name": self.backend_name,
            "shots": self.shots,
            "counts": dict(self.counts),
            "native": native_data,
        }


def to_microquantum_result(result: QuantumResult) -> Any:
    """Return the underlying MicroQuantum result from a QuantumResult."""
    require_microquantum()
    return result.native


__all__ = ["QuantumResult", "to_microquantum_result"]
