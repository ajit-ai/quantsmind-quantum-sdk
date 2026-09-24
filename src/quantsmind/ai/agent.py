"""Minimal plan-act-observe agent loop.

The loop itself is real orchestration logic: it stores history in
memory, asks the injected :class:`ModelBackend` for the next step,
dispatches ``tool_call`` requests from reply metadata, and stops on a
final answer or the step budget. The model is always injected — this
module contains no model weights and no fake inference.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from quantsmind.ai.memory import ConversationMemory
from quantsmind.ai.messages import TOOL, USER, Message
from quantsmind.ai.models import ModelBackend
from quantsmind.ai.tools import ToolCall, ToolRegistry, UnknownToolError

__all__ = [
    "AgentResult",
    "Agent",
]

#: Metadata key carrying a tool request: ``{"name": ..., "arguments": {...}}``.
TOOL_CALL_KEY = "tool_call"


@dataclass
class AgentResult:
    """Outcome of an agent run."""

    answer: str
    steps: int
    tool_calls: list[str] = field(default_factory=list)
    finished: bool = False


class Agent:
    """Runs a bounded plan-act-observe loop over tools.

    Args:
        backend: The model integration (injected).
        tools: Available tools (may be empty).
        memory: Conversation memory (created if omitted).
        max_steps: Step budget before stopping unfinished.
    """

    def __init__(
        self,
        backend: ModelBackend,
        tools: ToolRegistry | None = None,
        memory: ConversationMemory | None = None,
        max_steps: int = 5,
    ) -> None:
        """Initialize the agent."""
        if max_steps < 1:
            raise ValueError(f"max_steps must be >= 1, got {max_steps!r}")
        self._backend = backend
        self._tools = tools or ToolRegistry()
        self._memory = memory or ConversationMemory()
        self._max_steps = max_steps

    def run(self, task: str) -> AgentResult:
        """Run the task through the loop and return the result."""
        self._memory.store(Message(role=USER, content=task))
        calls: list[str] = []
        for _ in range(self._max_steps):
            reply = self._backend.complete(self._memory.recall())
            self._memory.store(reply)
            request = reply.metadata.get(TOOL_CALL_KEY)
            if not isinstance(request, dict):
                return AgentResult(
                    answer=reply.content, steps=len(calls) + 1, tool_calls=calls, finished=True
                )
            try:
                outcome = self._tools.dispatch(
                    ToolCall(
                        name=str(request.get("name", "")),
                        arguments=dict(request.get("arguments", {})),
                    )
                )
            except UnknownToolError as exc:
                observation = f"tool error: {exc}"
            else:
                observation = f"tool result: {outcome}"
                calls.append(str(request.get("name", "")))
            self._memory.store(Message(role=TOOL, content=observation))
        return AgentResult(answer="", steps=self._max_steps, tool_calls=calls, finished=False)
