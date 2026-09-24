# Release Strategy

- Releases are cut from `main` after CI (lint, type-check, tests) passes.
- Each release updates `CHANGELOG.md` under "Keep a Changelog" format.
- R0.x releases are architecture/foundation releases; no numerical
  correctness guarantees are made until 1.0.
- Tags: `vR0.1.0`, `vR0.2.0`, ... pre-1.0; `v1.0.0`, ... post-1.0.

## Package publishing (Trusted Publishing)

Version tags (`v*`) trigger `.github/workflows/release.yml`, which runs
`build` → `testpypi` → `pypi`: the build job produces the wheel/sdist
once, checks the tag against the package version, creates the GitHub
Release, and both publishing jobs consume that exact artifact. PyPI
never publishes if TestPyPI publishing failed. All authentication uses
GitHub OIDC Trusted Publishing — no API tokens or passwords exist
anywhere in the pipeline.

Before publishing jobs can authenticate, an administrator must register
each Trusted Publisher on the corresponding index (pending actions, not
yet performed):

- TestPyPI: owner `ajit-ai`, repository `quantsmind-quantum-sdk`,
  workflow `release.yml`, environment `testpypi`.
- PyPI: owner `ajit-ai`, repository `quantsmind-quantum-sdk`,
  workflow `release.yml`, environment `pypi`.

Released index versions are immutable: a published version is never
overwritten by re-running the workflow.
