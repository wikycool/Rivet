"""Graph-style features extracted from a Trace for Layer 2 (patterns).

Taint uses **reachability** over ``provenance.from_steps``, not step order.
"""

from __future__ import annotations

from functools import lru_cache

from rivet.trace import Trace

FEATURE_ORDER: tuple[str, ...] = (
    "path_length",
    "crosses_trust_boundary",
    "sensitive_nodes_touched",
    "external_sinks",
    "untrusted_sources",
    "tool_combo_rarity",
)

# Known-benign tool sequences (tuple of tool names). Others score rarity 1.0.
_BENIGN_TOOL_COMBOS: frozenset[tuple[str, ...]] = frozenset(
    {
        ("read_file",),
    }
)


def _effective_trust_untrusted(trace: Trace) -> dict[int, bool]:
    """Map step number → whether effective trust is untrusted (transitive)."""
    by_num = {s.step: s for s in trace.steps}

    @lru_cache(maxsize=None)
    def untrusted(step_no: int) -> bool:
        step = by_num[step_no]
        if step.tags.source_trust == "untrusted":
            return True
        return any(untrusted(parent) for parent in step.provenance.from_steps)

    return {n: untrusted(n) for n in by_num}


def extract_features(trace: Trace) -> dict[str, float]:
    """Return a named feature map keyed in ``FEATURE_ORDER``."""
    eff = _effective_trust_untrusted(trace)
    path_length = float(len(trace.steps))
    sensitive = float(sum(1 for s in trace.steps if s.tags.sink_type == "sensitive"))
    external = float(sum(1 for s in trace.steps if s.tags.sink_type == "external"))
    untrusted_sources = float(
        sum(1 for s in trace.steps if s.tags.source_trust == "untrusted")
    )
    crosses = 0.0
    for s in trace.steps:
        if eff[s.step] and s.tags.sink_type in ("sensitive", "external"):
            crosses = 1.0
            break
    combo = tuple(s.tool for s in trace.steps)
    rarity = 0.0 if combo in _BENIGN_TOOL_COMBOS else 1.0

    features = {
        "path_length": path_length,
        "crosses_trust_boundary": crosses,
        "sensitive_nodes_touched": sensitive,
        "external_sinks": external,
        "untrusted_sources": untrusted_sources,
        "tool_combo_rarity": rarity,
    }
    return {key: features[key] for key in FEATURE_ORDER}
