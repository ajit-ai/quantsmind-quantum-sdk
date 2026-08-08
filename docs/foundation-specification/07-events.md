# Event Hierarchy (`event.py` + cross-module event catalog)

All Events share the `Event` envelope defined in
`03-supporting-classes.md`. This file is the single source of truth
for the complete `EventType` enumeration referenced by every class
spec in this document.

## `EventType` enumeration

| Event | Emitted by | Payload (key fields) |
|---|---|---|
| `EntityCreated` | `Entity.create()` via `Lifecycle` | `entity_id`, `type` |
| `EntityInitialized` | `Entity.initialize()` | `entity_id`, `properties`, `attributes` |
| `EntityActivated` | `Entity.activate()` | `entity_id` |
| `EntityDeactivated` | `Entity.deactivate()` | `entity_id` |
| `EntitySuspended` | `Entity.suspend()` | `entity_id`, `reason` |
| `EntityDestroyed` | `Entity.destroy()` | `entity_id` |
| `SystemCreated` / `SystemInitialized` / `SystemActivated` / `SystemDeactivated` / `SystemDestroyed` | `System` lifecycle methods | `system_id` |
| `EntityAddedToSystem` | `System.add_entity()` | `system_id`, `entity_id` |
| `EntityRemovedFromSystem` | `System.remove_entity()` | `system_id`, `entity_id` |
| `RelationshipAdded` | `System.add_relationship()` | `system_id`, `relationship_id`, `participants` |
| `RelationshipRemoved` | `System.remove_relationship()` | `system_id`, `relationship_id` |
| `StateChanged` | `Entity.update_state()` / `System` aggregate update | `owner_id`, `old_state_id`, `new_state_id`, `cause_interaction_id` |
| `StateCreated` | `State.create()` | `state_id`, `owner_id` |
| `StateMerged` | `State.merge()` | `state_id`, `merged_from` |
| `PropertyAdded` / `PropertyRemoved` | `Entity.add_property()` / `remove_property()` | `entity_id`, `property_name` |
| `AttributeAdded` / `AttributeRemoved` | `Entity.add_attribute()` / `remove_attribute()` | `entity_id`, `attribute_name` |
| `AttributeChanged` | `Attribute.set_value()` | `entity_id`, `attribute_name`, `old_value`, `new_value` |
| `ConstraintAdded` | `Entity.add_constraint()` / `System.add_constraint()` | `owner_id`, `constraint_id` |
| `ConstraintViolated` | `Entity.update_state()` / `Constraint.evaluate()` caller | `owner_id`, `constraint_id`, `detail` |
| `ValidationSucceeded` / `ValidationFailed` | any `Validatable.validate()` caller | `owner_id`, `errors` (if failed) |
| `InteractionCreated` | `Interaction.create()` | `interaction_id`, `type`, `participants` |
| `InteractionStarted` | `Interaction.apply()` | `interaction_id` |
| `InteractionCompleted` | `Interaction.commit()` | `interaction_id`, `duration` |
| `InteractionFailed` | `Interaction.fail()` | `interaction_id`, `reason` |
| `InteractionCancelled` | `Interaction.cancel()` | `interaction_id`, `reason` |
| `ObservationRecorded` | `Entity.observe()` / `System.observe()` / `Interaction.observe()` | `observation_id`, `subject_id` |
| `KnowledgeGenerated` | `Knowledge.create()` | `knowledge_id`, `subject_type`, `contributing_observations` |

**Extension policy.** Domain packages append new `EventType` values
through a documented registry-merge mechanism (`EventType` becomes an
open enumeration backed by a registry rather than a closed Python
`Enum` at implementation time, or — if the target language requires a
closed enum — domain packages define their own `DomainEventType` enum
and wrap it in a generic `Event` whose `type` field carries a
namespaced string, e.g. `"quantum.circuit_compiled"`). This decision is
deferred to R0.3.0 language-binding work; both options are compatible
with the `Event` class shape already specified.

## `EventBus` contract

```
EventBus.publish(event: Event) -> None
EventBus.subscribe(event_type: EventType, handler: EventHandler) -> SubscriptionId
EventBus.unsubscribe(subscription_id: SubscriptionId) -> None
EventBus.subscribe_all(handler: EventHandler) -> SubscriptionId   # wildcard subscription
```

**Delivery guarantees (architecture-level, to be honored by whatever
concrete `EventBus` `runtime` provides):**
- At-least-once delivery to each subscriber within a single process.
- Publish never blocks the producer beyond enqueueing (bounded queue,
  default depth `constants.EVENT_BUS_DEFAULT_QUEUE_DEPTH`); a full
  queue raises `EventBusUnavailableError` rather than blocking
  indefinitely, and callers are expected to treat event publication as
  best-effort, never load-bearing for correctness of the operation
  that triggered it.
- Ordering is guaranteed per-source (`source_id`), not globally, across
  concurrent producers.

## Cross-Reference

Every event listed above appears in the "Events" section of its owning
class spec (`classes/entity.md`, `classes/system.md`,
`classes/state.md`, `classes/interaction.md`,
`03-supporting-classes.md`). This file exists so implementers have one
place to generate the actual `EventType` enum from, rather than
collating it from twenty files by hand.
