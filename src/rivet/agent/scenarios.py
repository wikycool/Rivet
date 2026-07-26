"""Scenario registry — Steps 4/5 register additively; do not change CLI argparse."""

from __future__ import annotations

from rivet.agent.runner import Scenario

# Empty by design in Step 3b. Benign/attack scenarios register here later.
REGISTRY: dict[str, Scenario] = {}
