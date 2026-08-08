# Core Package

## Purpose
Provides the shared abstractions (registries, contexts, base container types) that concrete domain packages build on top of the foundation ontology.

## Responsibility
Translate foundation concepts into reusable engineering primitives: base System containers, component registries, dependency-injection style contexts, and package bootstrap hooks.

## Dependencies
- `quantsmind.foundation`
- `quantsmind.exceptions`

## Future Interfaces
- Plugin discovery and registration protocol
- Context-scoped configuration resolution
- Domain-agnostic System composition helpers

## Status
Architecture-only (R0.1.0). No scientific, numerical, or algorithmic
implementations exist in this package yet. All classes are interfaces,
abstract base classes, or empty skeletons documenting intended shape.

## Testing
See `tests/unit/core`, `tests/integration/core`
(placeholders only, no test logic yet).
