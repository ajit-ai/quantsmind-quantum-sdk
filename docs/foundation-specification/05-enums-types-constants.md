# Enums, Types & Constants (`enums.py`, `types.py`, `constants.py`)

These three modules are leaf modules (no internal dependencies) that
every other `foundation` module depends on. They exist to eliminate
duplicated vocabulary and magic values across the package.

## `enums.py`

| Enum | Values | Used by |
|---|---|---|
| `LifecycleStage` | `CREATED`, `INITIALIZED`, `ACTIVE`, `INACTIVE`, `SUSPENDED`, `DESTROYED` | `Lifecycle`, `Entity`, `System` |
| `InteractionStatus` | `PENDING`, `RUNNING`, `COMPLETED`, `FAILED`, `CANCELLED` | `Interaction` |
| `EventType` | See `07-events.md` for the full enumerated list | `Event`, `EventBus` |
| `RelationshipDirection` | `DIRECTED`, `UNDIRECTED` | `Relationship` |
| `RelationshipCardinality` | `ONE_TO_ONE`, `ONE_TO_MANY`, `MANY_TO_MANY` | `Relationship` |
| `ConstraintSeverity` | `HARD`, `SOFT` | `Constraint` |
| `SerializationFormat` | `JSON`, `YAML`, `MSGPACK`, `BINARY`, `PROTOBUF` | `serializers.py`, every `Serializable` |
| `ObservationMethod` | `DIRECT`, `DERIVED`, `SIMULATED` | `Observation` |
| `TimeMode` | `WALL_CLOCK`, `DISCRETE_STEP`, `LOGICAL` | `Time` |

**Extension policy.** Domain packages must not edit `enums.py`
directly. `EventType` and `ObservationMethod` are the two enums
expected to grow with new domains; they provide a documented
extension-point pattern (a reserved sub-range of values, or a
companion `DomainEventType` registry merged at runtime) rather than
requiring `foundation` to be modified for every new domain package —
finalized in `07-events.md`.

## `types.py`

Type aliases and generics with no runtime behavior, used to keep
signatures across `foundation` consistent:

| Alias | Definition (conceptual) | Purpose |
|---|---|---|
| `EntityId` | `str` (validated against `constants.ID_PATTERN`) | Entity/System identifier type |
| `SystemId` | `EntityId` | Alias for readability at System call sites |
| `RelationshipId`, `ConstraintId`, `InteractionId`, `EventId`, `ObservationId`, `KnowledgeId`, `StateId`, `SubscriptionId` | `str` | Per-class id aliases, all validated the same way |
| `Timestamp` | `float` (Unix epoch seconds) | Raw numeric time value backing `Time` |
| `PropertyValue` | `Union[str, int, float, bool, complex, None]` | Allowed immutable Property value types (numeric-plus-string closure; structured values wrap in a nested `Property` set instead) |
| `AttributeValue` | `Union[str, int, float, bool, complex, None]` | Same closure as `PropertyValue`, kept as a separate alias since the two evolve independently |
| `StatePayload` | `Mapping[str, AttributeValue]` | The frozen `values` mapping inside `State` |
| `TypeSchema` | `Mapping[str, type]` | Declared shape for `Transformation.input_schema`/`output_schema` |
| `ConstraintExpression` | structured data type (e.g. nested dict AST: `{"op": "<=", "left": ..., "right": ...}`) | Data-only predicate representation for `Constraint.expression` |
| `T`, `TState`, `TEntity` | `TypeVar`s | Generic bounds for factory/collection signatures (e.g. `EntityFactory[TEntity]`) |

**Design note on `PropertyValue`/`AttributeValue`.** Restricting these
to a closed set of primitive types (rather than `Any`) is intentional:
it keeps every `Serializer` implementation tractable across every
target format and every future language port. Structured/composite
values are represented as *multiple* named `Property`/`Attribute`
entries, or as a nested `Entity`, never as an opaque blob inside a
single value slot.

## `constants.py`

| Constant | Value (indicative) | Purpose |
|---|---|---|
| `ID_PATTERN` | regex, e.g. `^[a-zA-Z][a-zA-Z0-9_\-\.]{0,127}$` | Identifier grammar shared by `Identity`, `Property`, `Attribute`, `Relationship`, `Constraint` names |
| `MAX_HISTORY_LENGTH` | `1000` | Default cap on `Entity.history`/`System.history` before oldest entries are evicted |
| `MAX_ATTRIBUTE_HISTORY_LENGTH` | `1000` | Default cap on `Attribute.history` |
| `DEFAULT_SERIALIZATION_FORMAT` | `SerializationFormat.JSON` | Default used when a `Serializable` method omits `format` |
| `MAX_SYSTEM_NESTING_DEPTH` | `16` | Guardrail for System-of-Systems composition (Future Extension) to prevent unbounded recursion |
| `SDK_VERSION` | `"R0.2.0"` | Embedded in every serialized document's envelope for schema-evolution purposes |
| `EVENT_BUS_DEFAULT_QUEUE_DEPTH` | `10000` | Default bounded-queue size for the `EventBus` reference contract |
| `RESERVED_ATTRIBUTE_NAMES` | `{"id", "type", "version"}` | Names disallowed as user-defined `Property`/`Attribute` names to prevent collision with core `Entity` fields |

**Overridability.** All of the above are compile-time/package-level
defaults in `foundation`. Runtime overriding (e.g. per-deployment
`MAX_HISTORY_LENGTH`) is intentionally out of scope for `foundation`
and is a documented Future Extension wired through the `config`
package instead — `foundation` must remain usable with zero
configuration.
