# Trace features (Layer 2 inputs)

`extract_features(trace)` returns a `dict[str, float]` with keys in `FEATURE_ORDER`.

## path_length

Number of tool-call steps in the Trace. Longer paths are not automatically malicious, but short trusted reads are the common benign shape in v1 demos.

## crosses_trust_boundary

`1.0` if any step has **effective trust** untrusted **and** `sink_type` in `{sensitive, external}`; else `0.0`. Effective trust is untrusted if the step itself is tagged untrusted **or** any transitive ancestor via `provenance.from_steps` is untrusted. This is reachability — not “untrusted appears earlier in the list.”

## sensitive_nodes_touched

Count of steps with `sink_type == "sensitive"` (e.g. password DB reads).

## external_sinks

Count of steps with `sink_type == "external"` (e.g. outbound email).

## untrusted_sources

Count of steps whose own `source_trust == "untrusted"` (not the effective/transitive label).

## tool_combo_rarity

v1: `0.0` if the ordered tool tuple is on a hardcoded known-benign allowlist (currently only `("read_file",)`); otherwise `1.0`. Do **not** fit frequencies on the two demos. The Layer 2 v1 detector must not use this feature.
