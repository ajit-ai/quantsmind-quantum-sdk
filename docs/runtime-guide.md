# Runtime Guide

How task execution works in the SDK: lifecycles, deterministic replay,
and the error model. This guide describes behavior that exists today;
it introduces no new API.

## Roles

| Component | Role |
|---|---|
| `Task` | One callable with args, timeout/retry metadata, and state |
| `Executor` | Runs tasks inline (`execute`) or on threads (`execute_async`) |
| `ExecutionEngine` | Coordinates executor, scheduler, and dispatcher |
| `Job` / `Workflow` / `Pipeline` | Group tasks into larger lifecycles |

Circuit execution is **not** part of this runtime — quantum circuits run
in MicroQuantum's runtime via `QuantumExperiment` (see the
Bell-State Example).

## Lifecycle

```text
CREATED → RUNNING → COMPLETED
                ↘ FAILED
CREATED / QUEUED / RUNNING → CANCELLED (via cancel())
```

A finished task never runs again: re-executing raises `TaskError`.

## Deterministic replay

`Executor.execute()` runs the callable inline, in call order. With
`max_workers=1` and deterministic callables, sequential submission is an
exact replay:

```python
from quantsmind.runtime.executor import Executor
from quantsmind.runtime.task import Task

executor = Executor(max_workers=1)
results = [executor.execute(Task(f"t{i}", lambda i=i: i * i)) for i in range(5)]
assert results == [0, 1, 4, 9, 16]
```

Pinned by `tests/unit/runtime/test_executor.py::TestDeterministicReplay`.

## Error model

- Task failure sets state `FAILED`, preserves the original exception on
  `task.error`, and raises `TaskError` carrying `task_id` with the
  original as `__cause__` (`raise ... from e`).
- The executor records failed tasks (`failed_count`, `get_task_status`)
  and re-raises; `execute_async` logs instead of raising.
- Validation (`validate()`) checks name, callability, and positive
  timeout / non-negative retry fields before execution.
- Queue-full rejection raises `TaskError("Maximum workers reached")`.

## Honest scope note

`Task` stores `timeout`, `retry_policy`, `retry_count`, and
`retry_delay`, and `validate()` checks them — but execution itself is
single-shot: no automatic retries and no timeout enforcement happen
today. Depend on the stored values at your own layer until a retry
framework lands (explicitly future work, not this guide).
