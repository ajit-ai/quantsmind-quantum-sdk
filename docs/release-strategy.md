# Release Strategy

- Releases are cut from `main` after CI (lint, type-check, tests) passes.
- Each release updates `CHANGELOG.md` under "Keep a Changelog" format.
- R0.x releases are architecture/foundation releases; no numerical
  correctness guarantees are made until 1.0.
- Tags: `vR0.1.0`, `vR0.2.0`, ... pre-1.0; `v1.0.0`, ... post-1.0.
