# Tests

QuantsMind uses a four-tier testing strategy:

| Tier | Purpose |
|------|---------|
| `unit/` | Fast, isolated tests per class/function contract |
| `integration/` | Cross-package interaction tests |
| `regression/` | Locks in previously fixed defects |
| `performance/` | Execution-time / memory budget assertions |

R0.1.0 is architecture-only: directories mirror `src/quantsmind` package
structure and are pre-created so future implementations always land in
the correct location, but no test bodies exist yet.

Run with:

```bash
pytest tests/unit
```
