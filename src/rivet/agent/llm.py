"""LLM client protocol and StubLLM for CI (no live model required)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, Union


@dataclass(frozen=True)
class StubToolCall:
    """One scripted tool call; provenance is declared, never inferred."""

    tool: str
    inputs: dict[str, Any] = field(default_factory=dict)
    from_steps: list[int] = field(default_factory=list)


@dataclass(frozen=True)
class ToolCallAction:
    tool: str
    inputs: dict[str, Any]
    from_steps: list[int] = field(default_factory=list)


@dataclass(frozen=True)
class FinalAction:
    text: str


Action = Union[ToolCallAction, FinalAction]


class LLMClient(Protocol):
    """Next action: tool call or final text."""

    def next_action(
        self,
        *,
        messages: list[Any],
        available_tools: list[str],
    ) -> Action: ...


class StubLLM:
    """Scripted plan for tests/CI. Exhausted plan yields FinalAction."""

    def __init__(self, plan: list[StubToolCall]) -> None:
        self._plan = list(plan)
        self._index = 0

    def next_action(
        self,
        *,
        messages: list[Any],
        available_tools: list[str],
    ) -> Action:
        del messages, available_tools  # unused — plan is authoritative
        if self._index >= len(self._plan):
            return FinalAction(text="done")
        call = self._plan[self._index]
        self._index += 1
        return ToolCallAction(
            tool=call.tool,
            inputs=dict(call.inputs),
            from_steps=list(call.from_steps),
        )
