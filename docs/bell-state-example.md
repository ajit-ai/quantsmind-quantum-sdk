# Bell-State Example

The smallest end-to-end run through the SDK: a declarative 2-qubit
program executed on the local statevector backend. It exercises the core
seam of QuantsMind Quantum — **declare → validate → translate → delegate
→ enriched result** — without any domain machinery.

## Run it

```bash
pip install "quantsmind[quantum]"
python examples/bell_state.py
```

Expected output (counts vary by seed; only `00`/`11` appear):

```text
program: bell (2 qubits, 2 gates)
validation: OK
circuit: QuantumCircuit
success: True
backend: statevector
counts: {'11': 509, '00': 515}
```

## What it demonstrates

| Step | API | Role |
|---|---|---|
| Declare | `QuantumProgram.bell_state()` | H + CNOT as data, no execution logic |
| Validate | `validate_program(program)` | Error list; empty means valid |
| Translate | `build_circuit(program)` | MicroQuantum `QuantumCircuit` |
| Delegate | `QuantumExperiment(...).run()` | Execution via MicroQuantum runtime |
| Result | `QuantumResult` | `counts`, `success`, `backend_name`, `provenance`, `to_dict()` |

## Compatibility canary

`tests/unit/quantum/test_bell_state_example.py` runs the same flow
seeded (`seed=42`) and asserts the entanglement signature structurally
(keys ⊆ {`00`, `11`}, totals, provenance). It guards the
`microquantum>=0.4,<0.5` pin: engine drift that changes gate handling,
backend names, or result shape fails fast here.
