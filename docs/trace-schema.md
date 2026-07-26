# Trace schema v1

A **Trace** is one agent run: ordered tool-call steps with taint (`source_trust`) and sink (`sink_type`) tags, plus declared provenance (`from_steps`).

Public API: `rivet.trace` — `load_trace`, `dump_trace`, models `Trace`, `Step`, `Tags`, `Provenance`.

## Shape

```json
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
```

## Enums

| Field | Values |
|---|---|
| `schema_version` | `"1"` (required) |
| `label` | `benign`, `attack` |
| `tags.source_trust` | `trusted`, `untrusted` |
| `tags.sink_type` | `none`, `sensitive`, `external` |

- `run_id`: plain string, caller-owned (no uuid/timestamps in the schema).
- `provenance.from_steps`: `list[int]`; empty means root (no parents). Widened from singular `from_step` in issue #1.
