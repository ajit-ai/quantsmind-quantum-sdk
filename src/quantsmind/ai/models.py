"""Model abstractions.

:class:`ModelBackend` is the single seam between the SDK's orchestration
(memory, tools, agents) and any language model. Backends are provided by
integrations, never by this package: there is intentionally no built-in
model, fake or otherwise.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from quantsmind.ai.messages import Message

__all__ = [
    "ModelCapabilities",
    "ModelBackend",
]


@dataclass(frozen=True)
class ModelCapabilities:
    """What a model backend declares about itself.

    Attributes:
        name: Backend identity.
        context_window: Maximum input messages, if declared.
        supports_tools: Whether the backend can request tool calls.
        supports_structured_output: Whether JSON-mode output is available.
        metadata: Free-form extra details.
    """

    name: str
    context_window: int | None = None
    supports_tools: bool = False
    supports_structured_output: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


class ModelBackend(ABC):
    """Interface every model integration must implement."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Backend identity."""
        raise NotImplementedError

    @abstractmethod
    def capabilities(self) -> ModelCapabilities:
        """Describe this backend."""
        raise NotImplementedError

    @abstractmethod
    def complete(self, messages: list[Message]) -> Message:
        """Produce the next assistant message for a conversation.

        Args:
            messages: Conversation history (oldest first).

        Returns:
            The assistant reply (possibly carrying a tool request in
            ``metadata`` following the ``tool_call`` convention).
        """
        raise NotImplementedError
