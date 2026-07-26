"""Attack scenario: untrusted read → sensitive DB → external email."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from rivet.agent.llm import StubLLM
from rivet.agent.runner import run_scenario
from rivet.agent.scenarios import REGISTRY


def test_attack_scenario_registered() -> None:
    assert "attack" in REGISTRY
    assert REGISTRY["attack"].label == "attack"


def test_attack_stub_run_exfiltration_path_and_tags(tmp_path: Path) -> None:
    scenario = REGISTRY["attack"]
    llm = StubLLM(list(scenario.stub_plan))

    trace = run_scenario(scenario, llm, seed="1", traces_dir=tmp_path)

    assert trace.label == "attack"
    assert [s.tool for s in trace.steps] == ["read_file", "query_db", "send_email"]
    assert trace.steps[0].tags.source_trust == "untrusted"
    assert trace.steps[0].tags.sink_type == "none"
    assert trace.steps[0].inputs["path"] == "poisoned_doc"
    assert trace.steps[1].tags.sink_type == "sensitive"
    assert trace.steps[1].inputs["table"] == "users"
    assert trace.steps[2].tags.sink_type == "external"
    assert trace.steps[2].provenance.from_steps == [1, 2]

    out = tmp_path / "attack" / "attack-1.json"
    assert out.is_file()


def test_cli_attack_scenario_exits_zero() -> None:
    proc = subprocess.run(
        [sys.executable, "-m", "rivet.agent.run", "--scenario", "attack"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0
    combined = proc.stdout + proc.stderr
    assert "attack" in combined.lower()
