# API Design Principles

- Public APIs are defined by interfaces in `foundation`, `core`, and
  each domain package's top-level `__init__.py`.
- Prefer keyword-only arguments for anything beyond the first
  positional parameter.
- Every public class documents Purpose, Responsibility, Dependencies.
- Favor small Protocols/ABCs over large "god objects".
- Backward compatibility is preserved within a MAJOR version wherever
  possible (see `versioning-policy.md`).
