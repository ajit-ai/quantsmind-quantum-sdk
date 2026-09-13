"""Bridge between QuantsMind domain descriptions and MicroQuantum.

The bridge is the **only** place where QuantsMind constructs MicroQuantum
objects.  It translates a :class:`~quantsmind.quantum.program.QuantumProgram`
into a ``microquantum.core.circuit.QuantumCircuit`` using MicroQuantum's
public ``Operator`` factory API and ``QuantumCircuit.append``.

It does **not** reimplement gates, circuits, states, measurement,
simulation, transpilation, algorithms or providers.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from quantsmind.quantum._mq import require_microquantum
from quantsmind.quantum.program import GateSpec, QuantumProgram

# Lower-case gate name -> matching MicroQuantum Operator factory.
# Entry is (factory_name, expected_param_count).
_GATE_FACTORIES: dict[str, tuple[str, int]] = {
    "i": ("I", 0),
    "x": ("X", 0),
    "y": ("Y", 0),
    "z": ("Z", 0),
    "h": ("H", 0),
    "s": ("S", 0),
    "sdg": ("Sdg", 0),
    "t": ("T", 0),
    "tdg": ("Tdg", 0),
    "rx": ("Rx", 1),
    "ry": ("Ry", 1),
    "rz": ("Rz", 1),
    "cx": ("CNOT", 0),
    "cnot": ("CNOT", 0),
    "cz": ("CZ", 0),
    "swap": ("SWAP", 0),
}


class UnknownGateError(ValueError):
    """Raised when a program references a gate MicroQuantum cannot build."""

    def __init__(self, name: str) -> None:
        super().__init__(
            f"unknown gate {name!r}; supported: {', '.join(sorted(set(_GATE_FACTORIES)))}"
        )


class GateParamError(ValueError):
    """Raised when a gate receives an unexpected number of parameters."""

    def __init__(self, name: str, expected: int, got: int) -> None:
        super().__init__(f"gate {name!r} expects {expected} parameter(s), got {got}")


def validate_program(program: QuantumProgram) -> list[str]:
    """Return a list of translation errors for a program (empty means valid)."""
    errors: list[str] = []
    for spec in program.operations:
        key = spec.name.lower()
        if key not in _GATE_FACTORIES:
            errors.append(f"unknown gate {spec.name!r}")
            continue
        _, expected = _GATE_FACTORIES[key]
        if len(spec.params) != expected:
            errors.append(
                f"gate {spec.name!r} expects {expected} parameter(s), got {len(spec.params)}"
            )
        if key in ("cx", "cnot", "cz", "swap"):
            if len(spec.qubits) != 2:
                errors.append(f"gate {spec.name!r} expects exactly 2 qubits")
        elif len(spec.qubits) != 1:
            errors.append(f"gate {spec.name!r} expects exactly 1 qubit")
    return errors


def build_circuit(program: QuantumProgram) -> Any:
    """Translate a :class:`QuantumProgram` into a MicroQuantum circuit."""
    mq = require_microquantum()

    circuit = mq.QuantumCircuit(program.num_qubits)
    for spec in program.operations:
        key = spec.name.lower()
        if key not in _GATE_FACTORIES:
            raise UnknownGateError(spec.name)
        _append_gate(circuit, spec)
    return circuit


def _append_gate(circuit: Any, spec: GateSpec) -> None:
    mq = require_microquantum()
    factory_name, expected = _GATE_FACTORIES[spec.name.lower()]
    if len(spec.params) != expected:
        raise GateParamError(spec.name, expected, len(spec.params))
    if spec.name.lower() in ("cx", "cnot", "cz", "swap"):
        if len(spec.qubits) != 2:
            raise ValueError(f"gate {spec.name!r} expects exactly 2 qubits")
    else:
        if len(spec.qubits) != 1:
            raise ValueError(f"gate {spec.name!r} expects exactly 1 qubit")
    factory: Callable[..., object] = getattr(mq.Operator, factory_name)
    operator = factory(*spec.params)
    circuit.append(operator, list(spec.qubits))


__all__ = [
    "UnknownGateError",
    "GateParamError",
    "validate_program",
    "build_circuit",
]
