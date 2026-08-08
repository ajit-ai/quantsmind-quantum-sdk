# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| R0.1.x  | :white_check_mark: (current, architecture-only) |

Formal long-term support windows will be published once the SDK
reaches 1.0.0 (see `docs/versioning-policy.md`).

## Reporting a Vulnerability

Please **do not** open a public GitHub issue for security
vulnerabilities.

Instead, report privately via your repository host's private security
advisory feature (e.g. GitHub Security Advisories), or contact the
maintainers directly through the channel listed in the project's
GitHub repository page.

Include:
- A description of the vulnerability and potential impact
- Steps to reproduce
- Affected version(s)

We aim to acknowledge reports within 5 business days.

## Scope Note (R0.1.0)

This release is architecture-only: no network calls, credential
handling, or execution logic is implemented yet (`security`,
`providers`, and `io` packages are interface skeletons only). Security
review will intensify starting with the R0.4.0 (`providers`) and
R0.10.0 (`security` hardening) milestones in `ROADMAP.md`.
