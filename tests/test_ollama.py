"""Optional OllamaClient smoke — skipped when Ollama is unavailable."""

from __future__ import annotations

import pytest

from rivet.agent.llm import FinalAction, OllamaClient, ToolCallAction, ollama_available


@pytest.mark.skipif(not ollama_available(), reason="Ollama not available")
def test_ollama_client_returns_action() -> None:
    client = OllamaClient(model="llama3")
    action = client.next_action(
        messages=[{"role": "user", "content": "Reply with the single word: ok"}],
        available_tools=[],
    )
    assert isinstance(action, (FinalAction, ToolCallAction))
