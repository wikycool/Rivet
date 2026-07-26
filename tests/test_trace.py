"""Tests for rivet.trace public API (load_trace / dump_trace)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from rivet.trace import dump_trace, load_trace

VALID_TRACE = {
    "schema_version": "1",
    "run_id": "benign-stub-1",
    "label": "benign",
    "steps": [
        {
            "step": 1,
            "tool": "read_file",
            "inputs": {},
            "outputs": {},
            "provenance": {"from_steps": []},
            "tags": {"source_trust": "trusted", "sink_type": "none"},
        }
    ],
}


def test_load_dump_round_trip_preserves_fields(tmp_path: Path) -> None:
    path = tmp_path / "trace.json"
    path.write_text(json.dumps(VALID_TRACE), encoding="utf-8")

    loaded = load_trace(path)
    dumped = dump_trace(loaded)

    assert json.loads(dumped) == VALID_TRACE

    from_dict = load_trace(VALID_TRACE)
    assert from_dict.run_id == "benign-stub-1"
    assert from_dict.label == "benign"
    assert from_dict.schema_version == "1"
    assert len(from_dict.steps) == 1
    assert from_dict.steps[0].tool == "read_file"
    assert from_dict.steps[0].provenance.from_steps == []
    assert from_dict.steps[0].tags.source_trust == "trusted"
    assert from_dict.steps[0].tags.sink_type == "none"


def test_dump_trace_is_byte_identical_across_two_dumps() -> None:
    trace = load_trace(VALID_TRACE)
    first = dump_trace(trace)
    second = dump_trace(trace)
    assert first == second


def test_dump_trace_writes_dest_file(tmp_path: Path) -> None:
    dest = tmp_path / "out.json"
    trace = load_trace(VALID_TRACE)
    dumped = dump_trace(trace, dest=dest)
    assert dest.read_text(encoding="utf-8") == dumped
    assert json.loads(dumped) == VALID_TRACE


def test_invalid_label_rejected() -> None:
    bad = {**VALID_TRACE, "label": "suspicious"}
    with pytest.raises(ValidationError):
        load_trace(bad)


def test_invalid_source_trust_rejected() -> None:
    bad = json.loads(json.dumps(VALID_TRACE))
    bad["steps"][0]["tags"]["source_trust"] = "maybe"
    with pytest.raises(ValidationError):
        load_trace(bad)


def test_missing_steps_rejected() -> None:
    bad = {
        "schema_version": "1",
        "run_id": "x",
        "label": "benign",
    }
    with pytest.raises(ValidationError):
        load_trace(bad)
