"""Tool definition, registry, and dispatch.

Tools wrap plain callables with a name, description, and required
argument names; the registry dispatches validated calls and reports
unknown tools and missing arguments as typed errors.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "Tool",
    "ToolCall",
    "ToolRegistry",
    "UnknownToolError",
]


class UnknownToolError(KeyError):
    """Raised when no tool is registered under the requested name."""


@dataclass(frozen=True)
class Tool:
    """A callable capability an agent can invoke.

    Args:
        name: Unique tool name.
        description: Human/model-readable purpose.
        parameters: Required argument names.
        func: The underlying callable.
    """

    name: str
    description: str
    parameters: tuple[str, ...]
    func: Callable[..., Any]

    def call(self, arguments: dict[str, Any]) -> Any:
        """Validate required arguments and invoke the callable.

        Raises:
            ValueError: If a required argument is missing.
        """
        missing = [name for name in self.parameters if name not in arguments]
        if missing:
            raise ValueError(f"tool {self.name!r} missing arguments: {missing}")
        return self.func(**{name: arguments[name] for name in self.parameters})


@dataclass(frozen=True)
class ToolCall:
    """A request to invoke a tool with arguments."""

    name: str
    arguments: dict[str, Any] = field(default_factory=dict)


class ToolRegistry:
    """Name -> tool registry with dispatch."""

    def __init__(self) -> None:
        """Initialize an empty registry."""
        self._tools: dict[str, Tool] = {}

    @property
    def tool_count(self) -> int:
        """Number of registered tools."""
        return len(self._tools)

    def register(self, tool: Tool) -> None:
        """Register a tool (names must be unique and non-empty).

        Raises:
            ValueError: For empty names or duplicates.
        """
        if not tool.name:
            raise ValueError("tool name must not be empty")
        if tool.name in self._tools:
            raise ValueError(f"tool already registered: {tool.name!r}")
        self._tools[tool.name] = tool

    def names(self) -> list[str]:
        """Sorted registered tool names."""
        return sorted(self._tools)

    def dispatch(self, call: ToolCall) -> Any:
        """Validate and run a tool call.

        Raises:
            UnknownToolError: If the tool is not registered.
            ValueError: If required arguments are missing.
        """
        try:
            tool = self._tools[call.name]
        except KeyError:
            raise UnknownToolError(f"unknown tool: {call.name!r}") from None
        return tool.call(call.arguments)
