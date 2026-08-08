# Simulation Package

## Purpose
Defines generic contracts for simulating the evolution of Systems over Space and Time, independent of physical domain.

## Responsibility
Own SimulationEngine, Timestep, Trajectory, and Observer interfaces that domain packages (physics, chemistry, ...) specialize.

## Dependencies
- `quantsmind.foundation`
- `quantsmind.core`
- `quantsmind.math`

## Future Interfaces
- Deterministic vs stochastic simulation contracts
- Multi-scale / multi-resolution simulation interfaces
- Checkpointing and reproducibility contracts

## Status
Architecture-only (R0.1.0). No scientific, numerical, or algorithmic
implementations exist in this package yet. All classes are interfaces,
abstract base classes, or empty skeletons documenting intended shape.

## Testing
See `tests/unit/simulation`, `tests/integration/simulation`
(placeholders only, no test logic yet).
