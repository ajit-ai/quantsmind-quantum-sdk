# Physics Package

## Purpose
Defines the domain model for physical systems (particles, fields, forces, dynamics) built on the simulation and math layers.

## Responsibility
Own physics domain interfaces. No physics algorithms implemented.

## Dependencies
- `quantsmind.foundation`
- `quantsmind.math`
- `quantsmind.simulation`

## Future Interfaces
- Classical, statistical, and quantum-field sub-domain contracts
- Unit-aware physical quantity interfaces

## Status
Architecture-only (R0.1.0). No scientific, numerical, or algorithmic
implementations exist in this package yet. All classes are interfaces,
abstract base classes, or empty skeletons documenting intended shape.

## Testing
See `tests/unit/physics`, `tests/integration/physics`
(placeholders only, no test logic yet).
