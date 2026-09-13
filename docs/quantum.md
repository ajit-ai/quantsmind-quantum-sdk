# QuantsMind Quantum SDK — User Guide

**QuantsMind Quantum 1.0.0** is a domain-oriented quantum intelligence SDK. It transforms supported real-world optimization problems — finance / portfolio, data, and ML — into mathematical computational workflows, and executes them through **classical**, **quantum**, or **hybrid** strategies, with benchmarking, interpretation, and provenance.

!!! abstract "One first-principle model"

    A System is composed of Entities. Every Entity has Identity, Properties, State,
    Behaviour, Relationships, Constraints, and History. Entities evolve through
    Interactions. Interactions change State. State evolves over Space and Time.
    Observation of evolution produces Knowledge. Knowledge enables Prediction.
    Prediction enables Decision. The quantum layer specializes this model — it does
    not reinvent it.

## Installation

```bash
pip install "quantsmind[quantum]"
```

The optional `microquantum` package (v0.4.x) provides the quantum execution engine.
The core SDK installs and works without it; the quantum layer reports its honest
availability and degrades gracefully when the engine is absent.

## Quick Start

```python
from quantsmind.quantum import formulate, run_workflow, DomainType, Strategy

# 1) Formulate a supported problem (here: portfolio optimization)
problem = formulate(
    domain=DomainType.FINANCE,
    data={...},                        # assets, returns, risk matrix, budget...
)

# 2) Execute as classical, quantum, or hybrid
report = run_workflow(
    problem,
    strategy=Strategy.AUTO,
    backend=None,                      # let the engine pick its default
    shots=1024,
)

# 3) Inspect the solution, interpretation, and provenance
print(report.objective_value)
print(report.interpretation.summary)
print(report.provenance.strategy)
```

## Supported Domains

- **Finance / Portfolio** — allocation optimization over a risk matrix, with
  volatility, budget, and return constraints.
- **Data** — clustering, matching, and feature-selection problems transformed into
  QUBO form.
- **ML** — integer / mixed models and assignment problems over learned matrices.

The framework is extensible: a domain registers its problem types, suitability
assessment, formulation adapter, and interpretation into the
`DomainIntelligence` registry.

## Honest Limitations

- The engine is optional and second-party; when unavailable, availability flags
  report `False` and workflows honesty-downgrade to the classical leg (never
  silently fake a quantum result).
- Hybrid execution interleaves a classical leg with a supported quantum leg only
  when the configured strategy requires it.
- Not every problem shape is representable by the built-in quantum formulations;
  `DomainIntelligence.assess` reports suitability and explains why.

## Key Concepts

| Concept | Purpose |
| --- | --- |
| `QuantumProgram` | A problem transformed into variables, objectives, and constraints. |
| `QuantumCircuitMapper` | Builds the circuit / Ising representation for a program. |
| `Executor` / `ExecutionOptions` | Classical, quantum, and hybrid execution legs. |
| `QuantumWorkflow` | Full pipeline: strategy selection, execution, decode, provenance. |
| `QuantumResult` / `ResultInterpretation` | Execution outcome plus a human-oriented interpretation. |
| `AlgorithmSelector` | Scored recommendation of algorithm families for a problem. |

## API Reference

Browse the complete public API of the quantum layer in the
[API Reference](reference/quantum.md). It is generated directly from the source
docstrings and matches the frozen public surface in `api_manifest.json`.