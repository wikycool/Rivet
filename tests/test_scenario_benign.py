"""Benign scenario: trusted read_file only; Trace label benign."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from rivet.agent.llm import StubLLM
from rivet.agent.runner import run_scenario
from rivet.agent.scenarios import REGISTRY


def test_benign_scenario_registered() -> None:
    assert "benign" in REGISTRY
    assert REGISTRY["benign"].label == "benign"


def test_benign_stub_run_produces_trusted_read_only_trace(tmp_path: Path) -> None:
    scenario = REGISTRY["benign"]
    llm = StubLLM(list(scenario.stub_plan))

    trace = run_scenario(scenario, llm, seed="1", traces_dir=tmp_path)

    assert trace.label == "benign"
    assert [s.tool for s in trace.steps] == ["read_file"]
    assert "query_db" not in {s.tool for s in trace.steps}
    assert "send_email" not in {s.tool for s in trace.steps}
    assert trace.steps[0].tags.source_trust == "trusted"
    assert trace.steps[0].inputs["path"] == "trusted_doc"

    out = tmp_path / "benign" / "benign-1.json"
    assert out.is_file()


def test_cli_benign_scenario_exits_zero() -> None:
    proc = subprocess.run(
        [sys.executable, "-m", "rivet.agent.run", "--scenario", "benign"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0
    combined = proc.stdout + proc.stderr
    assert "benign" in combined.lower()
