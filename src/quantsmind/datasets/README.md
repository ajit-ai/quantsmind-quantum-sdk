# Datasets Package

## Purpose
Defines contracts for discovering, loading, and versioning scientific datasets used across domains.

## Responsibility
Own Dataset/DataSource/Catalog interfaces. No loaders implemented.

## Dependencies
- `quantsmind.io`
- `quantsmind.foundation`

## Future Interfaces
- Dataset versioning and provenance contracts
- Streaming dataset interfaces

## Status
Architecture-only (R0.1.0). No scientific, numerical, or algorithmic
implementations exist in this package yet. All classes are interfaces,
abstract base classes, or empty skeletons documenting intended shape.

## Testing
See `tests/unit/datasets`, `tests/integration/datasets`
(placeholders only, no test logic yet).
