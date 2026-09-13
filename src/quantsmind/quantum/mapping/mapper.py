"""Domain-to-computation mapping foundation.

A mapping takes a :class:`~quantsmind.quantum.program.QuantumProgram`
(a computational representation of a domain problem) and produces a
:class:`MappingResult` describing the mapping steps.  Building the
actual runtime object is deferred to :meth:`DomainMapper.build`.

QMQ-01 ships one real mapping:
:class:`QuantumCircuitMapper` -> MicroQuantum circuit (via the bridge).
QMQ-02 adds QUBO / Ising / Hamiltonian / classical mappings.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, ClassVar

from quantsmind.quantum.bridge import build_circuit, validate_program
from quantsmind.quantum.strategy.strategy import ComputationStrategy


class MappingError(ValueError):
    """Raised when a domain description cannot be mapped to a computation."""


@dataclass
class MappingResult:
    """Record of a domain -> computation mapping.

    Args:
        mapper: Name of the mapper that produced the record.
        strategy: Strategy the mapping was produced for.
        source: A short description of the input representation.
        target: A short description of the output representation.
        steps: Human-readable mapping steps taken.
        metadata: Free-form mapping metadata.
        payload: Optional non-serializable mapped object.
    """

    mapper: str
    strategy: ComputationStrategy
    source: str
    target: str
    steps: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    payload: Any = field(default=None, repr=False)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary (payload excluded)."""
        return {
            "mapper": self.mapper,
            "strategy": self.strategy.name.lower(),
            "source": self.source,
            "target": self.target,
            "steps": list(self.steps),
            "metadata": dict(self.metadata),
        }


class DomainMapper(ABC):
    """Maps a computational description into a runtime representation.

    Subclasses implement one directed mapping.  ``map()`` validates the
    input and records the mapping steps; ``build()`` materializes the
    runtime object (a MicroQuantum circuit, a QUBO, ...).
    """

    name: ClassVar[str] = "domain_mapper"
    source: ClassVar[str] = "domain"
    target: ClassVar[str] = "computation"

    @abstractmethod
    def map(
        self,
        program: Any,
        *,
        strategy: ComputationStrategy,
    ) -> MappingResult:
        """Validate the input and record the mapping steps."""

    @abstractmethod
    def build(self, result: MappingResult) -> Any:
        """Materialize the mapped computational representation."""


class QuantumCircuitMapper(DomainMapper):
    """Real mapping: declarative :class:`QuantumProgram` -> MicroQuantum circuit.

    Validation is performed via :func:`validate_program`; the actual
    MicroQuantum circuit is built lazily by :func:`build_circuit` when
    :meth:`build` is called.

    Raises:
        MappingError: If the program is invalid or the strategy is
            incompatible with quantum execution.
    """

    name = "quantum_circuit"
    source = "quantsmind.quantum.QuantumProgram"
    target = "microquantum.QuantumCircuit"

    def __init__(self) -> None:
        self._program: Any = None

    def map(
        self,
        program: Any,
        *,
        strategy: ComputationStrategy = ComputationStrategy.HYBRID,
    ) -> MappingResult:
        """Validate the program and record the mapping steps.

        Args:
            program: A :class:`~quantsmind.quantum.program.QuantumProgram`.
            strategy: The chosen computation strategy.

        Raises:
            MappingError: If the strategy is incompatible with quantum
                execution or the program is not translatable.
        """
        if not strategy.uses_quantum_runtime:
            raise MappingError(
                f"quantum circuit mapping requires a quantum strategy, got {strategy.name.lower()}"
            )
        errors = validate_program(program)
        if errors:
            raise MappingError(
                f"program {program.name!r} is not translatable: " + "; ".join(errors)
            )
        self._program = program
        steps = [
            f"validated program {program.name!r} ({program.num_operations} operations)",
            "resolved gate operators through MicroQuantum public API",
            f"target: {self.target}",
        ]
        return MappingResult(
            mapper=self.name,
            strategy=strategy,
            source=self.source,
            target=self.target,
            steps=steps,
            metadata={
                "num_qubits": program.num_qubits,
                "num_operations": program.num_operations,
                "gates": list(program.gate_names),
            },
        )

    def build(self, result: MappingResult) -> Any:
        """Materialize the MicroQuantum circuit.

        Delegates to :func:`quantsmind.quantum.bridge.build_circuit`,
        which in turn calls MicroQuantum's public ``Operator`` factories.
        """
        if result.mapper != self.name:
            raise MappingError(
                f"MappingResult was produced by {result.mapper!r}, expected {self.name!r}"
            )
        if self._program is None:
            raise MappingError("map() must be called before build()")
        return build_circuit(self._program)


__all__ = [
    "DomainMapper",
    "MappingError",
    "MappingResult",
    "QuantumCircuitMapper",
]
