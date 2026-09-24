"""AI Package — Defines provider-independent AI/ML abstractions.

This package is part of the QuantsMind SDK (R0.1.0).
Foundational implementation (Phase 11): messages, model-backend
interface, conversation memory, tools, evaluation metrics,
structured-output helpers, and a minimal agent loop. Model weights and
provider integrations live outside this package by design.
"""

from __future__ import annotations

from quantsmind.ai.agent import TOOL_CALL_KEY, Agent, AgentResult
from quantsmind.ai.evaluation import exact_match, token_f1
from quantsmind.ai.memory import ConversationMemory
from quantsmind.ai.messages import ASSISTANT, SYSTEM, TOOL, USER, Message
from quantsmind.ai.models import ModelBackend, ModelCapabilities
from quantsmind.ai.structured import StructuredOutputError, parse_json_output
from quantsmind.ai.tools import Tool, ToolCall, ToolRegistry, UnknownToolError

__all__: list[str] = [
    "TOOL_CALL_KEY",
    "Agent",
    "AgentResult",
    "exact_match",
    "token_f1",
    "ConversationMemory",
    "ASSISTANT",
    "SYSTEM",
    "TOOL",
    "USER",
    "Message",
    "ModelBackend",
    "ModelCapabilities",
    "StructuredOutputError",
    "parse_json_output",
    "Tool",
    "ToolCall",
    "ToolRegistry",
    "UnknownToolError",
]
