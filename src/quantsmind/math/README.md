# Mathematics Package

## Purpose
Provides the mathematical vocabulary (linear algebra, tensors, geometry, probability, statistics, calculus, optimization primitives, graph theory, complex numbers, numerical methods) shared by every scientific domain in the SDK.

## Responsibility
Own mathematical type and operation interfaces. No numerical algorithms are implemented — this package defines contracts that concrete numerical backends will satisfy in later versions.

## Dependencies
- `quantsmind.foundation`
- `quantsmind.exceptions`

## Future Interfaces
- Backend-agnostic tensor interface (NumPy/JAX/Torch adapters)
- Symbolic math interoperability
- Numerical precision and unit-safety contracts

## Status
Architecture-only (R0.1.0). No scientific, numerical, or algorithmic
implementations exist in this package yet. All classes are interfaces,
abstract base classes, or empty skeletons documenting intended shape.

## Testing
See `tests/unit/math`, `tests/integration/math`
(placeholders only, no test logic yet).
