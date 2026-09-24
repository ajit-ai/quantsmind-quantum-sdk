"""Unit tests for quantsmind.ai primitives.

The scripted backend below is test-only scaffolding with fixed,
inspectable behavior — it exercises the orchestration logic, not
inference. No model weights are involved anywhere in this file.
"""

from __future__ import annotations

import pytest

from quantsmind.ai import (
    Agent,
    ConversationMemory,
    Message,
    ModelBackend,
    ModelCapabilities,
    Tool,
    ToolCall,
    ToolRegistry,
    UnknownToolError,
    exact_match,
    parse_json_output,
    token_f1,
)
from quantsmind.ai.structured import StructuredOutputError


class ScriptedBackend(ModelBackend):
    """Deterministic test double: requests one tool call, then answers."""

    def __init__(self) -> None:
        """Initialize."""
        self.calls = 0

    @property
    def name(self) -> str:
        return "scripted-test-backend"

    def capabilities(self) -> ModelCapabilities:
        return ModelCapabilities(name=self.name, supports_tools=True)

    def complete(self, messages: list[Message]) -> Message:
        self.calls += 1
        if self.calls == 1:
            return Message(
                role="assistant",
                content="computing",
                metadata={"tool_call": {"name": "add", "arguments": {"a": 2, "b": 3}}},
            )
        return Message(role="assistant", content="5")


class TestMessages:
    def test_roundtrip(self) -> None:
        message = Message(role="user", content="hi", metadata={"k": "v"})
        assert Message.from_dict(message.to_dict()) == message

    def test_bad_role(self) -> None:
        with pytest.raises(ValueError):
            Message(role="robot", content="hi")


class TestMemory:
    def test_window_pins_system(self) -> None:
        memory = ConversationMemory(max_messages=2)
        memory.store(Message(role="system", content="sys"))
        memory.store(Message(role="user", content="one"))
        memory.store(Message(role="user", content="two"))
        recalled = memory.recall()
        assert [m.content for m in recalled] == ["sys", "two"]
        assert memory.size == 3

    def test_bad_window(self) -> None:
        with pytest.raises(ValueError):
            ConversationMemory(max_messages=0)


class TestTools:
    def test_dispatch(self) -> None:
        registry = ToolRegistry()
        registry.register(
            Tool(name="add", description="add", parameters=("a", "b"), func=lambda a, b: a + b)
        )
        assert registry.dispatch(ToolCall(name="add", arguments={"a": 2, "b": 3})) == 5
        assert registry.names() == ["add"]

    def test_unknown_and_missing(self) -> None:
        registry = ToolRegistry()
        with pytest.raises(UnknownToolError):
            registry.dispatch(ToolCall(name="nope", arguments={}))
        registry.register(Tool(name="f", description="f", parameters=("x",), func=lambda x: x))
        with pytest.raises(ValueError):
            registry.dispatch(ToolCall(name="f", arguments={}))
        with pytest.raises(ValueError):
            registry.register(Tool(name="f", description="dup", parameters=(), func=lambda: 1))


class TestEvaluation:
    def test_exact(self) -> None:
        assert exact_match(" hi ", "hi") == 1.0
        assert exact_match("a", "b") == 0.0

    def test_f1(self) -> None:
        assert token_f1("the cat sat", "the cat sat") == 1.0
        assert token_f1("", "") == 1.0
        assert token_f1("a", "b") == 0.0


class TestStructured:
    def test_parse_and_require(self) -> None:
        assert parse_json_output('{"a": 1}', ["a"]) == {"a": 1}
        with pytest.raises(StructuredOutputError):
            parse_json_output("nope", ["a"])
        with pytest.raises(StructuredOutputError):
            parse_json_output("[1, 2]", ["a"])
        with pytest.raises(StructuredOutputError):
            parse_json_output('{"b": 1}', ["a"])


class TestAgent:
    def test_tool_loop_finishes(self) -> None:
        tools = ToolRegistry()
        tools.register(
            Tool(name="add", description="add", parameters=("a", "b"), func=lambda a, b: a + b)
        )
        result = Agent(ScriptedBackend(), tools).run("add 2 and 3")
        assert result.finished is True
        assert result.answer == "5"
        assert result.tool_calls == ["add"]

    def test_step_budget(self) -> None:
        class Chatty(ScriptedBackend):
            def complete(self, messages: list[Message]) -> Message:  # type: ignore[override]
                self.calls += 1
                return Message(
                    role="assistant",
                    content="more",
                    metadata={"tool_call": {"name": "add", "arguments": {"a": 1, "b": 1}}},
                )

        tools = ToolRegistry()
        tools.register(
            Tool(name="add", description="add", parameters=("a", "b"), func=lambda a, b: a + b)
        )
        result = Agent(Chatty(), tools, max_steps=2).run("go")
        assert result.finished is False
        assert result.steps == 2

    def test_bad_budget(self) -> None:
        with pytest.raises(ValueError):
            Agent(ScriptedBackend(), max_steps=0)
