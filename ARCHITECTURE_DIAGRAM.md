# QuantsMind SDK Architecture Diagram

## Overview

QuantsMind SDK is a universal scientific computing framework built on a single first-principle model: **A System is composed of Entities**. The current version (R0.1.0) is architecture-only, defining interfaces without implementations.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         QuantsMind SDK (R0.1.0)                            │
│                    Architecture-Only Foundation Layer                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Package Dependency Layers

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                           LAYER 10: Cross-Cutting                           │
│  visualization │ datasets │ plugins │ telemetry                            │
│  (depend on lower layers only, never on domain packages)                    │
└──────────────────────────────────────────────────────────────────────────────┘
                                        │
┌──────────────────────────────────────────────────────────────────────────────┐
│                           LAYER 9: Domain Packages                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │ quantum  │  │ physics  │  │ chemistry│  │ biology  │  │ astronomy│      │
│  │ (+runtime│  │          │  │   →      │  │   →      │  │   →      │      │
│  │  compiler│  │          │  │ physics) │  │ chemistry│  │ physics) │      │
│  │  providers│ │          │  │          │  │          │  │          │      │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘      │
│  ┌──────────┐  ┌──────────┐                                                   │
│  │cosmology │  │   ai     │                                                   │
│  │   →      │  │          │                                                   │
│  │astronomy │  │          │                                                   │
│  │   physics│  │          │                                                   │
│  └──────────┘  └──────────┘                                                   │
│  ┌──────────┐                                                              │
│  │ finance  │                                                              │
│  │   →      │                                                              │
│  │ math,    │                                                              │
│  │optimiz., │                                                              │
│  │   ai     │                                                              │
│  └──────────┘                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
                                        │
┌──────────────────────────────────────────────────────────────────────────────┐
│                           LAYER 8: Simulation                               │
│  simulation (depends on foundation, core, math)                              │
└──────────────────────────────────────────────────────────────────────────────┘
                                        │
┌──────────────────────────────────────────────────────────────────────────────┐
│                           LAYER 7: Optimization                              │
│  optimization (depends on math, foundation, exceptions)                       │
└──────────────────────────────────────────────────────────────────────────────┘
                                        │
┌──────────────────────────────────────────────────────────────────────────────┐
│                    LAYER 6: Execution Model                                  │
│  runtime │ compiler │ providers                                              │
│  (depend on core, foundation, exceptions)                                    │
└──────────────────────────────────────────────────────────────────────────────┘
                                        │
┌──────────────────────────────────────────────────────────────────────────────┐
│                           LAYER 5: Mathematics                               │
│  math (linear algebra, tensors, geometry, probability, statistics,           │
│       calculus, optimization primitives, graph theory, complex numbers,      │
│       numerical methods)                                                     │
│  (depends on foundation, exceptions)                                         │
└──────────────────────────────────────────────────────────────────────────────┘
                                        │
┌──────────────────────────────────────────────────────────────────────────────┐
│                           LAYER 4: Core                                      │
│  core (shared abstractions: registries, contexts, base containers)           │
│  (depends on foundation, exceptions)                                        │
└──────────────────────────────────────────────────────────────────────────────┘
                                        │
┌──────────────────────────────────────────────────────────────────────────────┐
│                           LAYER 3: Foundation                                │
│  foundation (universal ontology: Entity, System, State, Interaction, ...)   │
│  (depends only on exceptions)                                                │
└──────────────────────────────────────────────────────────────────────────────┘
                                        │
┌──────────────────────────────────────────────────────────────────────────────┐
│                    LAYER 2: Infrastructure                                  │
│  config │ io │ security                                                      │
│  (depend only on layer 1)                                                    │
└──────────────────────────────────────────────────────────────────────────────┘
                                        │
┌──────────────────────────────────────────────────────────────────────────────┐
│                    LAYER 1: Base Utilities                                   │
│  exceptions │ utils │ logging                                               │
│  (no internal dependencies)                                                 │
└──────────────────────────────────────────────────────────────────────────────┘
```

## Foundation Ontology (The Core Model)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                        Foundation Ontology                                   │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │ Entity (atomic unit)                                                   │ │
│  │  ├── Identity (unique identifier)                                      │ │
│  │  ├── Property (named characteristics)                                  │ │
│  │  ├── Attribute (typed values)                                          │ │
│  │  ├── State (current condition)                                         │ │
│  │  ├── Behaviour (actions/responses)                                     │ │
│  │  ├── Relationship (connections to other entities)                     │ │
│  │  ├── Constraint (rules/limitations)                                    │ │
│  │  └── Lifecycle (creation/evolution/destruction)                        │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │ System (collection of entities)                                        │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │ Interaction (how entities affect each other)                          │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │ Space & Time (context for evolution)                                    │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │ Event (discrete occurrences)                                           │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │ Observation (capturing evolution)                                       │ │
│  │  └── Knowledge (derived from observations)                              │ │
│  │      └── Prediction (anticipating future states)                        │ │
│  │          └── Decision (choosing actions)                                │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │ Transformation (state changes)                                          │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────┘
```

## Key Design Principles

1. **Composition over Inheritance**: Systems are composed of Entities and Relationships rather than deep class hierarchies

2. **Vendor Independence**: `providers` package isolates all hardware/cloud vendor specifics behind stable contracts

3. **Interfaces before Implementations**: R0.1.0 ships only abstract contracts; concrete numerical/algorithmic implementations are future releases

4. **Universal Ontology**: All domain packages (quantum, physics, chemistry, biology, astronomy, cosmology, finance, AI) specialize the same foundation ontology instead of reinventing their own

## Domain Package Specialization

Each domain package specializes the foundation ontology:

- **quantum**: Thin integration layer over MicroQuantum (QuantumProgram, QuantumExperiment, QuantumResult, algorithm delegation); engine concepts (Qubit, Circuit, Gate, Operator, Hamiltonian, Measurement, Noise, Statevector) are owned by MicroQuantum
- **physics**: Physical systems domain model
- **chemistry**: Molecular/chemical systems domain model (depends on physics)
- **biology**: Biological systems domain model (depends on chemistry)
- **astronomy**: Astronomical systems domain model (depends on physics)
- **cosmology**: Universe-scale structure/evolution domain model (depends on astronomy, physics)
- **finance**: Quantitative finance domain model (depends on math, optimization, ai)
- **ai**: AI/ML domain model

## Repository Structure

```
quantsmind-sdk/
├── src/quantsmind/        # 23 installable packages (architecture-only)
├── docs/                  # Architecture, developer & contribution docs
├── architecture/          # Architecture Decision Records (ADRs)
├── research/              # Exploratory notes (not public API)
├── examples/              # Usage examples (shape-only in R0.1.0)
├── tutorials/             # Onboarding material
├── tests/                 # Unit / integration / regression / performance
├── benchmarks/            # Long-running performance tracking
├── scripts/               # Developer & CI utility scripts
├── configs/               # Default non-secret configuration
├── assets/                # Docs/branding static assets
├── tools/                 # Internal dev tooling (not shipped)
└── .github/               # CI workflows, issue/PR templates
```

## Current Status: R0.1.0

- **No scientific algorithms**: Contains no quantum, AI, optimization, or simulation algorithms
- **Architecture-only**: Defines complete package layout, public interface contracts, and documentation standards
- **All abstract**: Every symbol is an abstract interface (ABC with NotImplementedError)
- **Future implementations**: Concrete numerical/algorithmic implementations planned for future releases (see ROADMAP.md)

## Dependency Rules (Hard Constraints)

- No circular imports between packages, ever
- Domain packages never import each other except via explicit documented arrows
- Only `providers` may reference vendor-specific SDKs, and only behind optional extras in pyproject.toml
- Lower layers never depend on higher layers
