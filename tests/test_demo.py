"""Demo seam: python -m rivet.demo runs benign + attack and prints verdicts."""

from __future__ import annotations

import subprocess
import sys


def test_demo_module_exits_zero_and_labels_both() -> None:
    proc = subprocess.run(
        [sys.executable, "-m", "rivet.demo"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    out = proc.stdout.lower()
    assert "benign" in out
    assert "attack" in out
    assert "verdict" in out
