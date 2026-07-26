"""Scenario registry — Steps 4/5 register additively via plugin modules.

Do not change CLI argparse in ``rivet.agent.run``. Scenario PRs only add
``scenario_<name>.py`` modules that call ``register(...)``.
"""

from __future__ import annotations

import importlib
from typing import Iterable

from rivet.agent.runner import Scenario

REGISTRY: dict[str, Scenario] = {}

# Discovered modules (optional — ImportError ignored so PRs can land independently).
_PLUGIN_MODULES: tuple[str, ...] = (
    "rivet.agent.scenario_benign",
    "rivet.agent.scenario_attack",
)


def register(scenario: Scenario) -> None:
    """Add a scenario to REGISTRY. Idempotent if the same object/name is re-registered."""
    existing = REGISTRY.get(scenario.name)
    if existing is not None and existing != scenario:
        raise ValueError(f"Scenario {scenario.name!r} already registered")
    REGISTRY[scenario.name] = scenario


def _load_plugins(modules: Iterable[str] | None = None) -> None:
    for name in modules if modules is not None else _PLUGIN_MODULES:
        try:
            importlib.import_module(name)
        except ImportError:
            continue


_load_plugins()
