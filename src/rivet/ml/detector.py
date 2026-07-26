"""Layer 2 (patterns) v1 — threshold detector. No GNN / sklearn."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

VerdictLabel = Literal["benign", "attack", "suspicious"]


@dataclass(frozen=True)
class Verdict:
    label: VerdictLabel
    score: float
    reasons: list[str]


def detect(features: dict[str, float]) -> Verdict:
    """Classify a feature vector with deterministic thresholds.

    Rule (v1):
    - attack if crosses_trust_boundary and external_sinks > 0
    - suspicious if exactly one of those holds
    - else benign

    ``tool_combo_rarity`` is intentionally ignored until more Traces exist.
    """
    crosses = float(features.get("crosses_trust_boundary", 0.0)) > 0.0
    external = float(features.get("external_sinks", 0.0)) > 0.0
    reasons: list[str] = []

    if crosses:
        reasons.append("effective untrusted data reaches a sensitive/external sink")
    if external:
        reasons.append(f"external_sinks={features.get('external_sinks', 0.0)}")

    if crosses and external:
        return Verdict(label="attack", score=1.0, reasons=reasons)
    if crosses or external:
        return Verdict(label="suspicious", score=0.5, reasons=reasons)
    return Verdict(label="benign", score=0.0, reasons=["no trust-boundary exfiltration pattern"])
