"""CLI: ``python -m rivet.agent.run --scenario NAME``.

Argument parsing is owned here. Scenario PRs must only add to ``REGISTRY``.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from rivet.agent.llm import StubLLM
from rivet.agent.runner import run_scenario
from rivet.agent.scenarios import REGISTRY


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m rivet.agent.run",
        description="Run a registered Rivet target-agent scenario.",
    )
    parser.add_argument(
        "--scenario",
        required=True,
        help="Scenario name registered in rivet.agent.scenarios.REGISTRY",
    )
    parser.add_argument(
        "--seed",
        default="1",
        help="Seed used in default run_id (scenario-seed)",
    )
    parser.add_argument(
        "--traces-dir",
        type=Path,
        default=None,
        help="Directory for Trace JSON (default: ./traces)",
    )
    args = parser.parse_args(argv)

    if args.scenario not in REGISTRY:
        known = sorted(REGISTRY) or ["(none)"]
        print(
            f"Unknown scenario {args.scenario!r}. Known: {', '.join(known)}",
            file=sys.stderr,
        )
        return 1

    scenario = REGISTRY[args.scenario]
    llm = StubLLM(list(scenario.stub_plan))
    kwargs: dict = {"seed": args.seed}
    if args.traces_dir is not None:
        kwargs["traces_dir"] = args.traces_dir
    trace = run_scenario(scenario, llm, **kwargs)
    print(f"Wrote Trace run_id={trace.run_id!r} label={trace.label!r} steps={len(trace.steps)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
