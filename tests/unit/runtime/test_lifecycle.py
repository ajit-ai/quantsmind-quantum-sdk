"""Unit tests for runtime job/task/pipeline/workflow lifecycles."""

from __future__ import annotations

from quantsmind.runtime.job import Job
from quantsmind.runtime.pipeline import Pipeline
from quantsmind.runtime.task import Task
from quantsmind.runtime.workflow import Workflow


class TestTaskExecution:
    def test_execute_returns_func_value(self) -> None:
        task = Task("t1", lambda: 42)
        assert task.execute() == 42
        assert task.result == 42


class TestJobLifecycle:
    def test_empty_job_is_invalid(self) -> None:
        valid, errors = Job("j1").validate()
        assert valid is False
        assert errors

    def test_job_with_task_validates_and_executes(self) -> None:
        job = Job("j1")
        job.add_task(Task("t1", lambda: 42))
        assert job.validate() == (True, [])
        results = job.execute()
        assert list(results.values()) == [42]


class TestPipelineLifecycle:
    def test_empty_pipeline_is_invalid(self) -> None:
        valid, errors = Pipeline("p1").validate()
        assert valid is False
        assert errors

    def test_full_chain_validates(self) -> None:
        job = Job("j1")
        job.add_task(Task("t1", lambda: 1))
        workflow = Workflow("w1")
        workflow.add_job(job)
        pipeline = Pipeline("p1")
        pipeline.add_stage(workflow)
        assert pipeline.validate() == (True, [])
