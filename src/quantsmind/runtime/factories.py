"""
Runtime Factories Module

This module provides factory methods for the Runtime package.

Purpose
-------
Provide factory methods for creating runtime objects.

Responsibilities
----------------
- Create runtime objects
- Support object initialization
- Handle object configuration
- Support object customization

Dependencies
------------
typing (standard library)
logging (standard library)
quantsmind.runtime.constants (runtime constants)
quantsmind.runtime.types (runtime types)
quantsmind.runtime.context (context)
quantsmind.runtime.session (session)
quantsmind.runtime.task (task)
quantsmind.runtime.job (job)
quantsmind.runtime.workflow (workflow)
quantsmind.runtime.pipeline (pipeline)
"""

from __future__ import annotations

import logging
from typing import Any, Callable, Dict, Optional

from quantsmind.runtime.context import ExecutionContext
from quantsmind.runtime.job import Job
from quantsmind.runtime.pipeline import Pipeline
from quantsmind.runtime.session import RuntimeSession
from quantsmind.runtime.task import Task
from quantsmind.runtime.types import ConfigDict
from quantsmind.runtime.workflow import Workflow

logger = logging.getLogger(__name__)


class RuntimeFactory:
    """Concrete implementation of a runtime factory.

    This class provides factory methods for creating runtime objects.

    Example:
        >>> factory = RuntimeFactory()
        >>> session = factory.create_session()
    """

    def create_session(self, config: Optional[ConfigDict] = None) -> RuntimeSession:
        """Create a runtime session.

        Args:
            config: Optional configuration

        Returns:
            Runtime session

        Example:
            >>> session = factory.create_session()
        """
        session = RuntimeSession()
        if config:
            for key, value in config.items():
                session.set_metadata(key, value)
        logger.debug("Created runtime session")
        return session

    def create_context(self, config: Optional[ConfigDict] = None) -> ExecutionContext:
        """Create an execution context.

        Args:
            config: Optional configuration

        Returns:
            Execution context

        Example:
            >>> context = factory.create_context()
        """
        context = ExecutionContext()
        if config:
            context.update(config)
        logger.debug("Created execution context")
        return context

    def create_task(
        self,
        name: str,
        func: Callable,
        args: Optional[list] = None,
        kwargs: Optional[dict] = None,
        config: Optional[ConfigDict] = None,
    ) -> Task:
        """Create a task.

        Args:
            name: Task name
            func: Task function
            args: Task arguments
            kwargs: Task keyword arguments
            config: Optional configuration

        Returns:
            Task

        Example:
            >>> task = factory.create_task("my_task", lambda x: x * 2, args=[5])
        """
        task = Task(name=name, func=func, args=args, kwargs=kwargs)
        if config:
            for key, value in config.items():
                task.set_metadata(key, value)
        logger.debug(f"Created task: {name}")
        return task

    def create_job(
        self,
        name: str,
        tasks: Optional[list] = None,
        config: Optional[ConfigDict] = None,
    ) -> Job:
        """Create a job.

        Args:
            name: Job name
            tasks: Job tasks
            config: Optional configuration

        Returns:
            Job

        Example:
            >>> job = factory.create_job("my_job", tasks=[task])
        """
        job = Job(name=name)
        if tasks:
            for task in tasks:
                job.add_task(task)
        if config:
            for key, value in config.items():
                job.set_metadata(key, value)
        logger.debug(f"Created job: {name}")
        return job

    def create_workflow(
        self,
        name: str,
        jobs: Optional[list] = None,
        config: Optional[ConfigDict] = None,
    ) -> Workflow:
        """Create a workflow.

        Args:
            name: Workflow name
            jobs: Workflow jobs
            config: Optional configuration

        Returns:
            Workflow

        Example:
            >>> workflow = factory.create_workflow("my_workflow", jobs=[job])
        """
        workflow = Workflow(name=name)
        if jobs:
            for job in jobs:
                workflow.add_job(job)
        if config:
            for key, value in config.items():
                workflow.set_metadata(key, value)
        logger.debug(f"Created workflow: {name}")
        return workflow

    def create_pipeline(
        self,
        name: str,
        workflows: Optional[list] = None,
        config: Optional[ConfigDict] = None,
    ) -> Pipeline:
        """Create a pipeline.

        Args:
            name: Pipeline name
            workflows: Pipeline workflows
            config: Optional configuration

        Returns:
            Pipeline

        Example:
            >>> pipeline = factory.create_pipeline("my_pipeline", workflows=[workflow])
        """
        pipeline = Pipeline(name=name)
        if workflows:
            for workflow in workflows:
                pipeline.add_stage(workflow)
        if config:
            for key, value in config.items():
                pipeline.set_metadata(key, value)
        logger.debug(f"Created pipeline: {name}")
        return pipeline


# Export
__all__ = [
    "RuntimeFactory",
]
