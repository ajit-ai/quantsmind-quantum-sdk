# Visualization Package

## Purpose
Defines rendering-agnostic contracts for visualizing Entities, State, and simulation trajectories across every domain.

## Responsibility
Own Renderer/Figure/Scene interfaces. No rendering backends implemented.

## Dependencies
- `quantsmind.foundation`

## Future Interfaces
- 2D/3D scene graph contracts
- Interactive and static renderer adapters

## Status
Architecture-only (R0.1.0). No scientific, numerical, or algorithmic
implementations exist in this package yet. All classes are interfaces,
abstract base classes, or empty skeletons documenting intended shape.

## Testing
See `tests/unit/visualization`, `tests/integration/visualization`
(placeholders only, no test logic yet).
