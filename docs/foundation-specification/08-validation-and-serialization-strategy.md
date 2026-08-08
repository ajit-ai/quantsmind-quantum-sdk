# Validation & Serialization Strategy

This file states the cross-cutting rules that every class-level
"Validation Rules" / "Serialization" section (in `classes/*.md` and
`03-supporting-classes.md`) specializes. Individual classes never
contradict this file; they only add class-specific detail.

## Validation Strategy

### Layers of validation

1. **Type-level** — `TypeValidator` (from `validators.py`) checks a
   `Property`/`Attribute` value against its declared `value_type`.
   Always runs first; failure short-circuits further validation.
2. **Rule-level** — `RangeValidator`, `RegexValidator`,
   `RequiredValidator`, `PredicateValidator`, composed via
   `ValidatorChain`, run after type-level passes.
3. **Constraint-level** — `Constraint.evaluate(state)` checks a
   candidate `State` as a whole (may reference multiple
   Attributes/Properties jointly, e.g. "sum of portfolio weights ==
   1.0" — something no single-field Validator can express).
4. **Cross-Entity / System-level** — `System`-level `Constraint`s
   evaluated against the aggregate `state`, invoked from
   `System.validate()` and before `System.run_interaction()` commits.

### When validation runs

| Trigger | Layer(s) invoked |
|---|---|
| `Property`/`Attribute` construction | Type-level, Rule-level |
| `Attribute.set_value()` | Type-level, Rule-level |
| `Entity.update_state()` | Constraint-level (against the candidate `State`) |
| `Entity.validate()` / `System.validate()` (explicit call) | All layers, full re-check |
| `Interaction.commit()` | Constraint-level, per participant, before each `update_state()` |
| `System.run_interaction()` | Constraint-level, System-wide, after all participant commits |

### Fail-fast vs. collect-all

Every `Validatable.validate()` and `Constraint.evaluate()` call
defaults to **collect-all** (`ValidatorChain(mode=COLLECT_ALL)`) so
callers see every problem in one pass — except the *mutation-path*
checks (`Attribute.set_value()`, `Entity.update_state()`), which are
**fail-fast**, since a mutation must be atomically accepted or
rejected, not partially explained after the fact.

### Severity

`ConstraintSeverity.HARD` violations always raise
`ConstraintViolationError` and block the mutation. `SOFT` violations
never raise; they are recorded (via `ConstraintViolated` Event) and
surfaced in the `ValidationResult`/`ConstraintResult`, letting
higher-level domain code decide policy (e.g. warn-only during
exploratory simulation, hard-block in production finance pipelines).

## Serialization Strategy

### Guiding rule

**No class in `foundation` implements serialization logic itself.**
Every `Serializable.serialize()`/`deserialize()` delegates to a
`Serializer` instance resolved by `SerializationFormat` from
`serializers.py`'s (future) `SerializerRegistry`. This keeps format
concerns (JSON quirks, MessagePack binary framing, Protobuf schema
compilation) entirely out of the ontology classes.

### Envelope

Every serialized document — regardless of format — wraps the payload
in a common envelope:

```
{
  "sdk_version": "R0.2.0",
  "type": "<fully-qualified class name>",
  "format": "<SerializationFormat value>",
  "payload": { ... class-specific fields ... }
}
```

This is what allows `deserialize()` to be a single dispatching
classmethod on `Entity`/`System`/etc. rather than requiring the caller
to already know the concrete type.

### Reference resolution

Two serialization shapes exist across the ontology:

- **Value objects** (`State`, `Property`, `Attribute` value,
  `Observation`, `Event`, `Time`, `Space`) — serialize fully inline;
  no reference resolution needed.
- **Graph objects** (`Entity`, `System`, `Relationship`,
  `Interaction`) — reference each other by id. A `System`'s serialized
  document is the only place a full object *graph* (Entities +
  Relationships) is expected to serialize together as one connected
  document, specifically to avoid duplicating Entity payloads when the
  same Entity participates in many Relationships.

### Schema evolution

`sdk_version` in the envelope is the compatibility signal.
`Serializer.supports_schema_evolution` (see `06-exceptions-and-utilities.md`)
tells callers whether a given format can tolerate additive field
changes across versions without a full migration step. Protocol
Buffers is the format expected to carry strict, generated-schema
guarantees once the SDK ships multi-language bindings; JSON/YAML/
MessagePack are expected to tolerate additive changes only
(unrecognized fields ignored on read, missing optional fields
defaulted).

### What is never serialized

- Live callables (`Behaviour.pre_hooks`/`post_hooks`,
  `Validator.PredicateValidator`'s predicate) — these are
  re-attached programmatically by the owning domain package after
  deserialization, not embedded in the wire format.
- Full `Attribute.history` by default (opt-in via serializer
  parameter) — reconstructable from `Entity.history` if needed,
  avoiding duplicated storage.
