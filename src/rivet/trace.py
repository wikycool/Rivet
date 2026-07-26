"""Trace schema v1 — serialize/deserialize agent-run provenance graphs.

A Trace is one agent run: ordered tool-call steps with taint tags
(``source_trust``) and sink tags (``sink_type``), plus declared provenance
edges (``from_steps``).

Schema (``schema_version`` ``"1"``)::

    {
      "schema_version": "1",
      "run_id": "benign-stub-1",
      "label": "benign",
      "steps": [{
        "step": 1,
        "tool": "read_file",
        "inputs": {},
        "outputs": {},
        "provenance": {"from_steps": []},
        "tags": {"source_trust": "trusted", "sink_type": "none"}
      }]
    }

Enums:
- ``label`` ∈ {benign, attack}
- ``source_trust`` ∈ {trusted, untrusted}
- ``sink_type`` ∈ {none, sensitive, external}
- ``provenance.from_steps``: list[int] (empty = root)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

Label = Literal["benign", "attack"]
SourceTrust = Literal["trusted", "untrusted"]
SinkType = Literal["none", "sensitive", "external"]


class Provenance(BaseModel):
    """Declared data-flow parents; empty list means a root step."""

    model_config = ConfigDict(extra="forbid")

    from_steps: list[int] = Field(default_factory=list)


class Tags(BaseModel):
    """Taint and sink classification for a step."""

    model_config = ConfigDict(extra="forbid")

    source_trust: SourceTrust
    sink_type: SinkType


class Step(BaseModel):
    """One tool call within a Trace."""

    model_config = ConfigDict(extra="forbid")

    step: int
    tool: str
    inputs: dict[str, Any] = Field(default_factory=dict)
    outputs: dict[str, Any] = Field(default_factory=dict)
    provenance: Provenance
    tags: Tags


class Trace(BaseModel):
    """One agent run as ordered steps with tags and provenance."""

    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["1"]
    run_id: str
    label: Label
    steps: list[Step]


def load_trace(src: str | Path | dict) -> Trace:
    """Load and validate a Trace from a path, JSON string, or dict."""
    if isinstance(src, dict):
        data: Any = src
    else:
        path = Path(src)
        if path.exists() and path.is_file():
            text = path.read_text(encoding="utf-8")
        else:
            text = str(src)
        data = json.loads(text)
    return Trace.model_validate(data)


def dump_trace(trace: Trace, dest: Path | None = None) -> str:
    """Serialize a Trace to stable JSON; optionally write to ``dest``."""
    # model_dump(mode="json") + separators keep dumps byte-identical
    # for a fixed Trace (no uuid / timestamps).
    payload = trace.model_dump(mode="json")
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if dest is not None:
        dest.write_text(text, encoding="utf-8")
    return text
