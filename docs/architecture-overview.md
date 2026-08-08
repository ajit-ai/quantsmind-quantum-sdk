# Architecture Overview

QuantsMind SDK is built on a single first-principle model: **a System is
composed of Entities**. Every Entity has Identity, Properties, State,
Behaviour, Relationships, Constraints, and History. Entities evolve
through Interactions, which change State over Space and Time.
Observation of that evolution produces Knowledge, which enables
Prediction, which enables Decision.

## Layering

```
foundation        <- universal ontology (Entity, System, State, ...)
core, exceptions, utils, logging, config, io, security
math               <- mathematical vocabulary
runtime, compiler, providers   <- execution model
simulation         <- generic evolution-over-time engine contracts
domains: quantum, physics, chemistry, biology, astronomy,
         cosmology, finance, ai
visualization, datasets, plugins, telemetry
```

Lower layers never depend on higher layers. Domain packages (quantum,
physics, ...) depend on foundation, core, math, runtime, compiler, and
providers, but never on each other except where explicitly documented
(e.g. chemistry -> physics, cosmology -> astronomy -> physics).

## Why this shape

- **Composition over inheritance**: Systems are composed of Entities and
  Relationships rather than deep class hierarchies.
- **Vendor independence**: `providers` isolates all hardware/cloud vendor
  specifics behind a stable contract.
- **Interfaces before implementations**: R0.1.0 ships only abstract
  contracts; concrete numerical/algorithmic implementations are future
  releases (see ROADMAP.md).
