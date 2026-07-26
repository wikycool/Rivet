"""End-to-end AI-slice demo: run benign + attack Traces and Layer 2 verdicts.

Usage::

    python -m rivet.demo
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from rivet.agent.llm import StubLLM
from rivet.agent.runner import run_scenario
from rivet.agent.scenarios import REGISTRY
from rivet.ml.detector import detect
from rivet.ml.features import extract_features


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m rivet.demo",
        description="Run benign and attack scenarios; print Trace summaries + Layer 2 verdicts.",
    )
    parser.add_argument(
        "--traces-dir",
        type=Path,
        default=Path("traces"),
        help="Directory for Trace JSON (default: ./traces)",
    )
    parser.add_argument("--seed", default="demo", help="Seed for run_id")
    args = parser.parse_args(argv)

    for name in ("benign", "attack"):
        if name not in REGISTRY:
            print(f"Missing scenario {name!r} in REGISTRY", file=sys.stderr)
            return 1
        scenario = REGISTRY[name]
        trace = run_scenario(
            scenario,
            StubLLM(list(scenario.stub_plan)),
            seed=args.seed,
            traces_dir=args.traces_dir,
        )
        features = extract_features(trace)
        verdict = detect(features)
        tools = " → ".join(s.tool for s in trace.steps) or "(none)"
        print(f"=== {name} ===")
        print(f"  run_id:  {trace.run_id}")
        print(f"  tools:   {tools}")
        print(
            f"  features: boundary={features['crosses_trust_boundary']:.0f} "
            f"external={features['external_sinks']:.0f} "
            f"sensitive={features['sensitive_nodes_touched']:.0f}"
        )
        print(f"  verdict: {verdict.label} (score={verdict.score})")
        for reason in verdict.reasons:
            print(f"    - {reason}")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
