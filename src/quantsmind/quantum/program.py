"""Declarative, vendor-neutral quantum programs.

``QuantumProgram`` is the QuantsMind-facing description of a quantum
program: an ordered list of :class:`GateSpec` operations on a fixed
number of qubits.  It deliberately contains **no execution logic** — it
is a translation input.  The actual circuit construction, simulation and
execution are delegated to MicroQuantum by :mod:`quantsmind.quantum.bridge`.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class GateSpec:
    """A single gate operation on named qubits.

    Args:
        name: Gate name (``"h"``, ``"x"``, ``"cx"``, ``"rx"``, ...).
        qubits: Qubit indices the gate acts on (1 or 2 entries).
        params: Optional numeric rotation parameters (``(theta,)`` for ``rx``).
    """

    name: str
    qubits: tuple[int, ...]
    params: tuple[float, ...] = ()

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("gate name must be a non-empty string")
        if not self.qubits:
            raise ValueError(f"gate {self.name!r} must act on at least one qubit")
        if any(not isinstance(q, int) or q < 0 for q in self.qubits):
            raise ValueError(f"gate {self.name!r} has invalid qubit indices: {self.qubits}")

    @classmethod
    def from_tuple(cls, name: str, qubits: Sequence[int], *params: float) -> GateSpec:
        """Build a GateSpec from positional parts."""
        return cls(name=name, qubits=tuple(qubits), params=tuple(params))

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {"name": self.name, "qubits": list(self.qubits), "params": list(self.params)}


@dataclass
class QuantumProgram:
    """A declarative quantum program for translation to MicroQuantum.

    Args:
        num_qubits: Fixed number of qubits.
        operations: Ordered gate operations.
        name: Optional program label (used for provenance).
        metadata: Optional domain metadata attached to the program.
    """

    num_qubits: int
    operations: list[GateSpec] = field(default_factory=list)
    name: str = "program"
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.num_qubits < 1:
            raise ValueError(f"num_qubits must be >= 1, got {self.num_qubits}")
        for spec in self.operations:
            if any(q >= self.num_qubits for q in spec.qubits):
                raise ValueError(
                    f"gate {spec.name!r} references qubit index out of range: {spec.qubits}"
                )

    def add(self, name: str, qubits: Sequence[int], *params: float) -> QuantumProgram:
        """Append a gate operation and return self (fluent)."""
        self.operations.append(GateSpec.from_tuple(name, qubits, *params))
        return self

    def add_gate(self, spec: GateSpec) -> QuantumProgram:
        """Append a pre-built GateSpec and return self."""
        self.operations.append(spec)
        self._check_range()
        return self

    def _check_range(self) -> None:
        for spec in self.operations:
            if any(q >= self.num_qubits for q in spec.qubits):
                raise ValueError(
                    f"gate {spec.name!r} references qubit index out of range: {spec.qubits}"
                )

    @property
    def num_operations(self) -> int:
        """Number of gate operations in the program."""
        return len(self.operations)

    @property
    def gate_names(self) -> list[str]:
        """Ordered gate names, for quick inspection."""
        return [op.name for op in self.operations]

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "num_qubits": self.num_qubits,
            "name": self.name,
            "metadata": dict(self.metadata),
            "operations": [op.to_dict() for op in self.operations],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> QuantumProgram:
        """Rebuild a QuantumProgram from :meth:`to_dict` output."""
        return cls(
            num_qubits=int(data["num_qubits"]),
            name=str(data.get("name", "program")),
            metadata=dict(data.get("metadata", {})),
            operations=[
                GateSpec(
                    name=str(op["name"]),
                    qubits=tuple(op["qubits"]),
                    params=tuple(op["params"]),
                )
                for op in data.get("operations", [])
            ],
        )

    @classmethod
    def bell_state(cls) -> QuantumProgram:
        """Convenience constructor for a 2-qubit Bell state program."""
        return cls(
            num_qubits=2,
            name="bell",
            operations=[GateSpec("h", (0,)), GateSpec("cx", (0, 1))],
        )


__all__ = ["GateSpec", "QuantumProgram"]
