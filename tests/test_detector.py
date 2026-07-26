"""Layer 2 detector seam: detect(features) -> Verdict (thresholds only)."""

from __future__ import annotations

from pathlib import Path

from rivet.ml.detector import Verdict, detect
from rivet.ml.features import extract_features
from rivet.trace import load_trace

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def test_benign_fixture_is_benign() -> None:
    features = extract_features(load_trace(FIXTURES / "benign_trace.json"))
    verdict = detect(features)
    assert verdict.label == "benign"
    assert verdict.score == 0.0


def test_attack_fixture_is_attack() -> None:
    features = extract_features(load_trace(FIXTURES / "attack_trace.json"))
    verdict = detect(features)
    assert verdict.label == "attack"
    assert verdict.score == 1.0
    assert any("trust" in r.lower() or "external" in r.lower() for r in verdict.reasons)


def test_suspicious_when_only_boundary() -> None:
    verdict = detect(
        {
            "path_length": 2.0,
            "crosses_trust_boundary": 1.0,
            "sensitive_nodes_touched": 1.0,
            "external_sinks": 0.0,
            "untrusted_sources": 1.0,
            "tool_combo_rarity": 1.0,  # must be ignored in v1
        }
    )
    assert verdict.label == "suspicious"
    assert 0.0 < verdict.score < 1.0


def test_ignores_tool_combo_rarity() -> None:
    """Rarity alone must not flip a clean path to attack/suspicious."""
    verdict = detect(
        {
            "path_length": 1.0,
            "crosses_trust_boundary": 0.0,
            "sensitive_nodes_touched": 0.0,
            "external_sinks": 0.0,
            "untrusted_sources": 0.0,
            "tool_combo_rarity": 1.0,
        }
    )
    assert verdict.label == "benign"
    assert isinstance(verdict, Verdict)
