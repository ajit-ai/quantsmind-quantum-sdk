# Documentation Structure

Every class specified in this document must ship, at implementation
time, with documentation following this exact template — consistent
with `docs/documentation-standards.md` at the repo root, specialized
here for class-level API docs.

## Per-class documentation template

```markdown
# <ClassName>

## Overview
One paragraph: what it is, why it exists, what it composes/is composed by.

## Responsibilities
Bullet list, matching the "General" + "Relationships" sections of
this specification.

## API Reference
Auto-generated from docstrings once implemented (e.g. via mkdocstrings
or Sphinx autodoc), but must render:
- Attributes (name, type, description)
- Properties
- Public methods (signature, params, return, exceptions)
- Events emitted
- Exceptions raised

## Examples
At least one minimal, runnable example per major behavior category
(construction, mutation, observation, serialization).

## Developer Notes
Design rationale, non-obvious invariants, common pitfalls (e.g. "State
is immutable — don't try to mutate `.values` in place").

## Extension Guidelines
How a domain package should subclass or compose this class. Explicit
"do not do X" guidance where relevant (e.g. "do not add scientific
computation logic to Behaviour hooks; delegate to Transformation").
```

## Documentation toolchain (architecture only)

- **Source of truth:** docstrings in the eventual implementation,
  written to the format specified in
  `docs/documentation-standards.md` (Purpose / Responsibility /
  Dependencies / Future Interfaces for modules; the template above for
  classes).
- **Generation:** a static-site generator (candidate: MkDocs +
  mkdocstrings, chosen for parity with the Markdown-first repo
  structure already in place) renders `docs/` and inline docstrings
  into a browsable API reference — selection and CI wiring deferred to
  a DevOps-focused roadmap item, not decided in this specification.
- **Cross-linking:** every class's generated doc page links to (a) its
  entry in this specification (`docs/foundation-specification/`), (b)
  its module's entry in `01-module-descriptions.md`, and (c) any ADR
  in `architecture/decisions/` that motivated its design.

## Documentation completeness gate

A class is not considered "documentation complete" until:

1. Every public method has a docstring covering signature, params,
   return, preconditions, postconditions, and exceptions (mirroring
   this specification's "Methods" sections exactly — the spec **is**
   the docstring content plan).
2. Every emitted `Event` and raised `Exception` is cross-linked to its
   entry in `07-events.md` / `06-exceptions-and-utilities.md`.
3. At least one example exists per interface the class implements
   (e.g. a class implementing `Cloneable` has a `clone()` example).

This gate is enforced manually via PR review in R0.2.0; a future
roadmap item (see `12-roadmap.md`) proposes a docstring-coverage CI
check once implementation begins.
