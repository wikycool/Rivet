"""Registry loader seam — plugins optional until scenario PRs land."""

from __future__ import annotations

from rivet.agent.llm import StubToolCall
from rivet.agent.runner import Scenario
from rivet.agent.scenarios import REGISTRY, register


def test_register_is_additive() -> None:
    name = "__test_only_scenario__"
    REGISTRY.pop(name, None)
    sc = Scenario(
        name=name,
        label="benign",
        stub_plan=(StubToolCall(tool="read_file", inputs={"path": "trusted_doc"}),),
    )
    register(sc)
    assert REGISTRY[name] is sc
    REGISTRY.pop(name, None)
