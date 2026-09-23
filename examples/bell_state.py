"""Bell-state example: the SDK's core promise in ~30 lines.

Build a declarative :class:`QuantumProgram` (H + CNOT), validate it,
translate it to a MicroQuantum circuit, execute it on the local
statevector backend, and read back the enriched
:class:`QuantumResult`.

Run from the repository root::

    python examples/bell_state.py

Requires the optional quantum engine::

    pip install "quantsmind[quantum]"
"""

from __future__ import annotations

from quantsmind.quantum import QuantumExperiment, QuantumProgram
from quantsmind.quantum.bridge import build_circuit, validate_program


def main() -> None:
    program = QuantumProgram.bell_state()
    print(f"program: {program.name} "
          f"({program.num_qubits} qubits, {program.num_operations} gates)")

    issues = validate_program(program)
    if issues:
        raise SystemExit(f"invalid program: {issues}")
    print("validation: OK")

    circuit = build_circuit(program)
    print(f"circuit: {type(circuit).__name__}")

    experiment = QuantumExperiment(
        program, backend="statevector", shots=1024, seed=42
    )
    result = experiment.run()

    print(f"success: {result.success}")
    print(f"backend: {result.backend_name}")
    print(f"counts: {result.counts}")
    print(f"provenance: {result.provenance}")


if __name__ == "__main__":
    main()
