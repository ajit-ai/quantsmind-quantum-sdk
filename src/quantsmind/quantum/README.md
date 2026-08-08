# Quantum Computing Package

## Purpose
Defines the vendor-independent quantum computing domain model: qubits, circuits, gates, operators, state vectors, Hamiltonians, measurement, and noise, on top of the runtime/provider/compiler layers.

## Responsibility
Own quantum domain interfaces only. No quantum algorithms, gate decompositions, or simulators implemented.

## Dependencies
- `quantsmind.foundation`
- `quantsmind.core`
- `quantsmind.math`
- `quantsmind.runtime`
- `quantsmind.providers`
- `quantsmind.compiler`

## Future Interfaces
- Circuit IR lowering to provider-specific backends
- Noise model and error-mitigation contracts
- Hybrid quantum-classical execution interfaces

## Status
Architecture-only (R0.1.0). No scientific, numerical, or algorithmic
implementations exist in this package yet. All classes are interfaces,
abstract base classes, or empty skeletons documenting intended shape.

## Testing
See `tests/unit/quantum`, `tests/integration/quantum`
(placeholders only, no test logic yet).
