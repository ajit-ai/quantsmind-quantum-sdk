# Foundation Package

## Purpose
Defines the universal ontology that every other package in QuantsMind is built on: Entity, System, State, Interaction, and the primitives that describe how anything in the SDK exists, changes, and is observed.

## Responsibility
Own the first-principle model: Systems are composed of Entities; Entities have Identity, Properties, State, Behaviour, Relationships, Constraints, and History; Interactions evolve State over Space and Time; Observation produces Knowledge; Knowledge enables Prediction.

## Dependencies
- *(none — leaf package)*

## Future Interfaces
- Formal typed Property/Attribute descriptors with units and domains
- Event-sourced State history and replay
- Constraint solver integration points
- Cross-domain Relationship graph

## Status
Architecture-only (R0.1.0). No scientific, numerical, or algorithmic
implementations exist in this package yet. All classes are interfaces,
abstract base classes, or empty skeletons documenting intended shape.

## Testing
See `tests/unit/foundation`, `tests/integration/foundation`
(placeholders only, no test logic yet).
