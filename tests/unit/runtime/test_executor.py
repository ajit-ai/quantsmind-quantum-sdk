"""Unit tests for Executor determinism and Task error paths (9-B).

The executor runs tasks inline and in order: with ``max_workers=1``,
sequential submission is an exact deterministic replay. These tests pin
that contract plus the failure, validation, and cancellation paths.
"""

from __future__ import annotations

import pytest

from quantsmind.runtime.enums import ExecutionState
from quantsmind.runtime.exceptions import TaskError
from quantsmind.runtime.executor import Executor
from quantsmind.runtime.task import Task


def _recorder(log: list[str], label: str) -> str:
    log.append(label)
    return label


class TestDeterministicReplay:
    def test_sequential_order_is_exact(self) -> None:
        executor = Executor(max_workers=1)
        log: list[str] = []
        first = executor.execute(Task("t1", _recorder, args=[log, "a"]))
        second = executor.execute(Task("t2", _recorder, args=[log, "b"]))
        assert (first, second) == ("a", "b")
        assert log == ["a", "b"]
        assert executor.completed_count == 2
        assert executor.failed_count == 0

    def test_replay_twice_matches(self) -> None:
        def run_once() -> list[int]:
            executor = Executor(max_workers=1)
            return [executor.execute(Task(f"t{i}", lambda i=i: i * i)) for i in range(5)]

        assert run_once() == run_once() == [0, 1, 4, 9, 16]


class TestExecutorErrors:
    def test_max_workers_rejection(self) -> None:
        executor = Executor(max_workers=1)
        blocker = Task("blocker", lambda: 1)
        executor._active_tasks[blocker.task_id] = blocker
        with pytest.raises(TaskError, match="Maximum workers"):
            executor.execute(Task("t2", lambda: 2))

    def test_failure_bookkeeping(self) -> None:
        def boom() -> None:
            raise RuntimeError("nope")

        executor = Executor(max_workers=1)
        task = Task("bad", boom)
        with pytest.raises(TaskError):
            executor.execute(task)
        assert executor.failed_count == 1
        assert executor.completed_count == 0
        assert task.state == ExecutionState.FAILED
        assert isinstance(task.error, RuntimeError)

    def test_status_lookup(self) -> None:
        executor = Executor(max_workers=1)
        task = Task("t1", lambda: 1)
        assert executor.get_task_status(task.task_id) is None
        executor.execute(task)
        assert executor.get_task_status(task.task_id) == ExecutionState.COMPLETED

    def test_shutdown_clears_active(self) -> None:
        executor = Executor(max_workers=1)
        task = Task("t1", lambda: 1)
        executor._active_tasks[task.task_id] = task
        executor.shutdown()
        assert executor.active_count == 0


class TestTaskErrors:
    def test_double_execute_rejected(self) -> None:
        task = Task("t1", lambda: 1)
        task.execute()
        with pytest.raises(TaskError, match="Cannot execute"):
            task.execute()

    def test_cancel_then_execute_rejected(self) -> None:
        task = Task("t1", lambda: 1)
        task.cancel()
        assert task.state == ExecutionState.CANCELLED
        with pytest.raises(TaskError, match="Cannot execute"):
            task.execute()

    def test_failure_state_and_cause(self) -> None:
        def boom() -> None:
            raise ValueError("bad input")

        task = Task("bad", boom)
        with pytest.raises(TaskError) as exc_info:
            task.execute()
        assert task.state == ExecutionState.FAILED
        assert isinstance(task.error, ValueError)
        assert exc_info.value.task_id == task.task_id
        assert isinstance(exc_info.value.__cause__, ValueError)

    def test_validation_errors(self) -> None:
        valid, errors = Task("", lambda: 1).validate()
        assert valid is False and errors
        valid, errors = Task("t", "not-callable").validate()  # type: ignore[arg-type]
        assert valid is False and errors
        valid, errors = Task("t", lambda: 1, timeout=0).validate()
        assert valid is False and errors
        valid, errors = Task("t", lambda: 1, retry_count=-1).validate()
        assert valid is False and errors
        assert Task("t", lambda: 1).validate() == (True, [])
