"""CLI seam: python -m rivet.agent.run --scenario NAME."""

from __future__ import annotations

import subprocess
import sys


def test_unknown_scenario_exits_nonzero() -> None:
    proc = subprocess.run(
        [sys.executable, "-m", "rivet.agent.run", "--scenario", "does-not-exist"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode != 0
    combined = (proc.stdout + proc.stderr).lower()
    assert "unknown" in combined or "does-not-exist" in combined
    assert "known" in combined


def test_registry_importable_and_empty() -> None:
    from rivet.agent.scenarios import REGISTRY

    assert isinstance(REGISTRY, dict)
    assert REGISTRY == {}
