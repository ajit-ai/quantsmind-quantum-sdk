# AI Foundations

## Overview

Provider-independent AI orchestration in `quantsmind.ai`: messages,
model-backend interface, conversation memory, tools, evaluation metrics,
structured-output helpers, and a minimal agent loop. Model weights and
provider integrations live outside this package by design.

## Purpose

Let users build model-agnostic agents, wire tools, and evaluate outputs
without depending on any commercial AI provider.

## Concept

`ModelBackend.complete()` is the single seam to any language model.
Everything else — `ConversationMemory` windowing, `ToolRegistry`
dispatch, `Agent` plan-act-observe loop, `exact_match`/`token_f1`
metrics, JSON output parsing — is deterministic SDK logic.

## API

`Message` (+ role constants), `ModelBackend`, `ModelCapabilities`,
`ConversationMemory`, `Tool`, `ToolCall`, `ToolRegistry`,
`UnknownToolError`, `exact_match()`, `token_f1()`,
`parse_json_output()`, `Agent`, `AgentResult`, `TOOL_CALL_KEY`.

## Input / Processing / Output

Input: task strings and tool calls. Processing: bounded loop with
memory recall. Output: `AgentResult(answer, steps, tool_calls,
finished)`.

## Example

`python examples/ai/tool_loop.py` answers `(2+3)*4` through two
dispatched tool calls with a labeled scripted backend.

## Limitations

No model weights, no provider integrations, no streaming, no
embeddings; the scripted backends in examples/tests are scaffolding,
not inference.
