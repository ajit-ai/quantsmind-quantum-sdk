"""Tool-use loop: answer (2+3)*4 with a calculator tool and memory.

Feature: Agent + ToolRegistry + ConversationMemory from ``quantsmind.ai``.
Purpose: show real plan-act-observe orchestration with an injected model.
Input: the task string "compute (2+3)*4".
Processing: the scripted backend (clearly labeled test-style stand-in,
NOT a model) requests add/multiply calls; the agent dispatches them.
Output: final answer "20" with the tool-call trail.
Meaning: orchestration is real SDK logic; only weights are external.

Run from the repository root::

    python examples/ai/tool_loop.py
"""

from __future__ import annotations

from quantsmind.ai import (
    Agent,
    ConversationMemory,
    Message,
    ModelBackend,
    ModelCapabilities,
    Tool,
    ToolRegistry,
)


class ScriptedBackend(ModelBackend):
    """Deterministic stand-in backend for this example (not a model)."""

    def __init__(self) -> None:
        """Initialize."""
        self.calls = 0

    @property
    def name(self) -> str:
        return "example-scripted-backend"

    def capabilities(self) -> ModelCapabilities:
        return ModelCapabilities(name=self.name, supports_tools=True)

    def complete(self, messages: list[Message]) -> Message:
        self.calls += 1
        if self.calls == 1:
            request = {"name": "add", "arguments": {"a": 2, "b": 3}}
            return Message(role="assistant", content="adding", metadata={"tool_call": request})
        if self.calls == 2:
            request = {"name": "multiply", "arguments": {"x": 5, "y": 4}}
            return Message(role="assistant", content="multiplying", metadata={"tool_call": request})
        return Message(role="assistant", content="20")


def main() -> None:
    tools = ToolRegistry()
    tools.register(
        Tool(name="add", description="add", parameters=("a", "b"), func=lambda a, b: a + b)
    )
    tools.register(
        Tool(
            name="multiply",
            description="multiply",
            parameters=("x", "y"),
            func=lambda x, y: x * y,
        )
    )
    agent = Agent(ScriptedBackend(), tools, ConversationMemory())
    result = agent.run("compute (2+3)*4")
    print(f"answer: {result.answer}")
    print(f"tool calls: {result.tool_calls}")
    print(f"finished: {result.finished}")


if __name__ == "__main__":
    main()
