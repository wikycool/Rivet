"""Feature extractor seam: extract_features(Trace) -> dict[str, float]."""

from __future__ import annotations

from pathlib import Path

from rivet.ml.features import FEATURE_ORDER, extract_features
from rivet.trace import load_trace

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def test_benign_fixture_has_no_boundary_or_external() -> None:
    features = extract_features(load_trace(FIXTURES / "benign_trace.json"))
    assert features["path_length"] == 1.0
    assert features["crosses_trust_boundary"] == 0.0
    assert features["external_sinks"] == 0.0
    assert features["sensitive_nodes_touched"] == 0.0
    assert features["untrusted_sources"] == 0.0
    assert features["tool_combo_rarity"] == 0.0  # known-benign allowlist


def test_attack_fixture_crosses_boundary_with_external_sink() -> None:
    features = extract_features(load_trace(FIXTURES / "attack_trace.json"))
    assert features["path_length"] == 3.0
    assert features["crosses_trust_boundary"] == 1.0
    assert features["external_sinks"] >= 1.0
    assert features["sensitive_nodes_touched"] >= 1.0
    assert features["untrusted_sources"] >= 1.0
    assert features["tool_combo_rarity"] == 1.0  # not on allowlist


def test_feature_order_is_complete_and_stable() -> None:
    features = extract_features(load_trace(FIXTURES / "benign_trace.json"))
    assert tuple(features.keys()) == FEATURE_ORDER
    assert set(FEATURE_ORDER) == set(features)


def test_reachability_not_positional_ordering() -> None:
    """Untrusted then unrelated sensitive without provenance edge is NOT a cross."""
    from rivet.trace import Provenance, Step, Tags, Trace

    trace = Trace(
        schema_version="1",
        run_id="positional-trap",
        label="benign",
        steps=[
            Step(
                step=1,
                tool="read_file",
                inputs={},
                outputs={},
                provenance=Provenance(from_steps=[]),
                tags=Tags(source_trust="untrusted", sink_type="none"),
            ),
            Step(
                step=2,
                tool="query_db",
                inputs={},
                outputs={},
                provenance=Provenance(from_steps=[]),  # no edge from step 1
                tags=Tags(source_trust="trusted", sink_type="sensitive"),
            ),
        ],
    )
    features = extract_features(trace)
    assert features["crosses_trust_boundary"] == 0.0
