# Blueprint: Rivet AI Slice — Target Agent Harness + Layer 2 v1

**Objective:** Implement the AI team’s first vertical: Trace contract → fake tools → target agent runner → benign/attack demos → graph features → simple Layer 2 detector.

**Parent spec:** https://github.com/wikycool/Rivet/issues/1  
**Repo:** `wikycool/Rivet` · default branch `main` · mode: **branch/PR** (git + `gh` available)  
**Owner:** AI team  
**Out of scope for this plan:** MCP Tap, Layer 1 rules, GNN, AgentDojo, real email/DB, sklearn

**Review status:** Adversarial review APPROVE WITH FIXES applied (2026-07-26).

---

## Glossary (use these terms)

| Term | Meaning |
|---|---|
| Trace | One agent run as ordered tool-call steps + tags |
| Target agent | The AI under test (tools + LLM client) |
| Taint | Trust origin of data (`trusted` / `untrusted`) |
| Sink | Where data can leave (`none` / `sensitive` / `external`) |
| Layer 2 (patterns) | Anomaly detection on Trace features (not GNN yet) |

Read `CONTEXT.md` before every step.

---

## Frozen public API (do not deviate; changes require a plan amendment)

| Module | Symbol | Signature |
|---|---|---|
| `rivet.trace` | `Trace`, `Step`, `Tags`, `Provenance` | Pydantic v2 models |
| `rivet.trace` | `load_trace` | `(src: str \| Path \| dict) -> Trace` |
| `rivet.trace` | `dump_trace` | `(trace: Trace, dest: Path \| None = None) -> str` |
| `rivet.agent.tools` | `ToolResult` | `@dataclass(frozen=True)` with `outputs: dict`, `source_trust: Literal["trusted","untrusted"]`, `sink_type: Literal["none","sensitive","external"]` |
| `rivet.agent.tools` | `TOOLS` | `dict[str, Callable[..., ToolResult]]` |
| `rivet.agent.llm` | `LLMClient` | Protocol: next action → tool call or final text |
| `rivet.agent.llm` | `StubLLM` | Scripted plan; each entry may include `from_steps: list[int]` |
| `rivet.agent.runner` | `run_scenario` | `(scenario: Scenario, llm: LLMClient, *, run_id: str \| None = None) -> Trace` |
| `rivet.agent.scenarios` | `REGISTRY` | `dict[str, Scenario]` |
| `rivet.agent.run` | `__main__` | CLI: `python -m rivet.agent.run --scenario {name}` |
| `rivet.ml.features` | `extract_features` | `(trace: Trace) -> dict[str, float]` |
| `rivet.ml.features` | `FEATURE_ORDER` | `tuple[str, ...]` fixed key order |
| `rivet.ml.detector` | `detect` | `(features: dict[str, float]) -> Verdict` |
| `rivet.ml.detector` | `Verdict` | `label: Literal["benign","attack","suspicious"]`, `score: float`, `reasons: list[str]` |

**Enum literals (copy exactly):**

- `Trace.label` ∈ {`benign`, `attack`}
- `source_trust` ∈ {`trusted`, `untrusted`}
- `sink_type` ∈ {`none`, `sensitive`, `external`}
- `Verdict.label` ∈ {`benign`, `attack`, `suspicious`}

**Trace schema v1 shape:**

```json
{
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
      "tags": {"source_trust": "trusted", "sink_type": "none"}
    }
  ]
}
```

**Widening vs issue #1:** `provenance.from_step` → `provenance.from_steps: list[int]` (joins). Comment on #1 when merging Step 1. StubLLM is CI default (Ollama optional) — note in PR for #4.

**`run_id`:** Caller-supplied. Runner default: `f"{scenario_name}-{seed}"`. Never `uuid4()` or wall-clock. For fixed scenario + stub plan, `dump_trace` output is **byte-identical** across runs.

---

## Issue ↔ step map

| Step | GitHub issue | Title |
|---|---|---|
| 0 | #9 (create if missing) | Python bootstrap + layout |
| 1 | #2 | Trace schema |
| 2 | #3 | Fake tools |
| 3a | #4 (partial) | Runner + StubLLM |
| 3b | #4 (closes) | Ollama + CLI registry |
| 4 | #5 | Benign scenario |
| 5 | #6 | Attack scenario |
| 6 | #7 | Graph features |
| 7 | #8 | Layer 2 detector |
| 8 | comment on #1 | Demo polish |

---

## Dependency graph

```
Step 0 (bootstrap + CI + domain.md fix)
    │
    ├──────────────┐
    ▼              ▼
Step 1          Step 2
Trace schema    Fake tools
    │              │
    └──────┬───────┘
           ▼
        Step 3a
        Runner + StubLLM
           ▼
        Step 3b
        Ollama + CLI + REGISTRY shell
           │
     ┌─────┴─────┐
     ▼           ▼
  Step 4      Step 5
  Benign      Attack   (additive REGISTRY only)
     │           │
     └─────┬─────┘
           ▼
        Step 6
        Graph features
           ▼
        Step 7
        Layer 2 detector (thresholds only)
           ▼
        Step 8
        Demo polish + README
```

**Parallelism:** Step 1 ∥ Step 2 after Step 0. Step 4 ∥ Step 5 after Step 3b.

---

## Invariants (verify after every step)

1. `pytest` passes with **no Ollama required** (stub LLM / fixtures only). GitHub Actions CI enforces this after Step 0.
2. No real email, no production DB, no secrets in repo.
3. Domain terms from `CONTEXT.md` used in public APIs and issue comments.
4. Traces written under `traces/` (gitignored); fixtures under `tests/fixtures/`.
5. Each PR maps to exactly one GitHub issue (see map above).
6. Before opening each PR: re-read **Anti-patterns**; state in PR body that none are violated.
7. For a fixed scenario + stub plan, Trace JSON is byte-identical across runs.

---

## Plan mutation protocol

| Action | Rule |
|---|---|
| **Split** | If a step exceeds ~1 PR / one context window, insert `N.a` / `N.b` and update edges |
| **Insert** | New step gets an id, blockers, and a note in **Audit trail** |
| **Skip** | Mark `SKIPPED` with reason; rewire dependents |
| **Reorder** | Only if no broken edge; update graph |
| **Abandon** | Mark `ABANDONED`; leave issue comment on parent #1 |

---

## Step 0 — Python project bootstrap + CI

**Status:** done (PR https://github.com/wikycool/Rivet/pull/10 — merge to close #9)  
**GitHub issue:** https://github.com/wikycool/Rivet/issues/9  
**Branch:** `feat/ai-python-bootstrap`  
**Blocked by:** none  
**Parallel with:** —  
**Model tier:** default  
**Rollback:** delete branch; no production impact

### Context brief (cold start)

Rivet is an empty scaffold. Freeze layout under `src/rivet/` (not bare `src/agent/`). Update `docs/agents/domain.md` to match. Commit agent-skills docs if still untracked. Add GitHub Actions CI. Do **not** implement Trace/agent yet.

### Tasks

- [ ] First commit on branch (or tiny prior commit): `AGENTS.md`, `CONTEXT.md`, `.agents/`, `docs/agents/`, `skills-lock.json`, `.gitignore`, `plans/` — keep packaging PR reviewable
- [ ] Layout FROZEN: `src/rivet/{agent,ml,attacks}/` each with `__init__.py`. Future infra: `src/rivet/{proxy,policy}/`
- [ ] Update tree in `docs/agents/domain.md` to show `src/rivet/...` (reject generic top-level `agent`/`ml` package names — PyPI collisions)
- [ ] Delete `src/.gitkeep` once `src/rivet/` exists
- [ ] `pyproject.toml`: package `rivet`, Python ≥3.11; deps `pydantic`; optional-dependencies `dev = ["pytest"]`, `ollama = ["ollama"]`
- [ ] Trivial smoke test so pytest exit code is 0 (not 5)
- [ ] Verify `.gitignore` already has `.venv/`, `traces/`, `.scratch/`
- [ ] `.github/workflows/ci.yml`: ubuntu-latest, Python 3.11, `pip install -e ".[dev]"`, `pytest -q` — no Ollama, no secrets
- [ ] `gh issue create` for bootstrap if #9 missing; PR closes #9

### Verification

```powershell
# From repo root. Use interpreter path (activation does not persist across tool calls).
# On this machine prefer py -3.11 if `py` defaults to 3.13.
py -3.11 -m venv .venv
.venv\Scripts\python.exe -m pip install -e ".[dev]"
.venv\Scripts\python.exe -m pytest -q
# expect exit code 0, >=1 test passed
```

### Exit criteria

- `import rivet` works after editable install.
- CI workflow exists and is green on the PR.
- `docs/agents/domain.md` shows `src/rivet/` layout.
- Issue #9 closed by merge.

---

## Step 1 — Trace schema + JSON validation

**Status:** done (merged PR https://github.com/wikycool/Rivet/pull/11)  
**GitHub issue:** https://github.com/wikycool/Rivet/issues/2  
**Branch:** `feat/ai-trace-schema`  
**Blocked by:** Step 0  
**Parallel with:** Step 2  
**Model tier:** strongest (contract freezes for Tap + ML)  
**Rollback:** Before Step 3a merges: revert PR. After: **roll forward only** — optional fields + `schema_version` bump; comment on #1 for Tap owner.

### Context brief (cold start)

Implement Frozen public API for `rivet.trace` exactly. Models: `Trace`, `Step`, `Tags`, `Provenance` with `from_steps: list[int]` (empty = root). Required `schema_version: Literal["1"]`. `run_id` is a plain string (caller-owned).

Comment on issue #1 recording `from_step` → `from_steps` widening before merge.

Glossary: **Trace**, **Taint**, **Sink**.

### Tasks

- [ ] Implement `src/rivet/trace.py` (or `src/rivet/trace/__init__.py`) exporting Frozen API symbols
- [ ] `load_trace` / `dump_trace` with clear validation errors
- [ ] Short schema doc in module docstring or `docs/trace-schema.md`
- [ ] Tests in `tests/test_trace.py`: happy path + ≥2 invalid cases
- [ ] Comment on #1 about `from_steps` + `schema_version`
- [ ] PR: `Closes #2`; anti-patterns checklist in body

### Verification

```powershell
.venv\Scripts\python.exe -m pytest tests/test_trace.py -q
# expect exit 0, >=3 tests
```

### Exit criteria

- Round-trip preserves fields; byte-stable when same model instance dumped twice.
- Invalid label / missing steps / bad tag enum fail loudly.
- Issue #2 acceptance criteria checked in PR body.

---

## Step 2 — Fake tools

**Status:** done (merged PR https://github.com/wikycool/Rivet/pull/12)  
**GitHub issue:** https://github.com/wikycool/Rivet/issues/3  
**Branch:** `feat/ai-fake-tools`  
**Blocked by:** Step 0  
**Parallel with:** Step 1  
**Model tier:** default  
**Rollback:** revert PR

### Context brief (cold start)

Implement `rivet.agent.tools`: `ToolResult` + `TOOLS` with `read_file`, `query_db`, `send_email`. Fixture-backed only.

**Shared contract with Step 1 (parallel-safe):** Copy tag literals and `ToolResult` fields from **Frozen public API** verbatim. Step 2 defines `ToolResult` in `rivet.agent.tools` and does **NOT** import from `rivet.trace`. Step 3a maps `ToolResult` → `Step.tags` — that adapter is the only bridge.

### Tasks

- [ ] `TOOLS` registry + three callables returning `ToolResult`
- [ ] Fixtures: trusted doc, poisoned/untrusted doc, sensitive password rows
- [ ] Tests in `tests/test_tools.py` — happy path + tag assertions
- [ ] PR: `Closes #3`

### Verification

```powershell
.venv\Scripts\python.exe -m pytest tests/test_tools.py -q
# expect exit 0, >=3 tests
```

### Exit criteria

- `read_file` supports trusted vs untrusted by key/path.
- `query_db` → `sink_type=sensitive`; `send_email` → `sink_type=external`.
- No network I/O.

---

## Step 3a — Runner + StubLLM + Trace assembly

**Status:** done (merged PR https://github.com/wikycool/Rivet/pull/13)  
**GitHub issue:** https://github.com/wikycool/Rivet/issues/4 (partial — still open for 3b)  
**Branch:** `feat/ai-agent-runner`  
**Blocked by:** Step 1, Step 2  
**Parallel with:** —  
**Model tier:** strongest  
**Rollback:** revert PR if 3b not merged

### Context brief (cold start)

Primary seam: `run_scenario(scenario, llm) -> Trace`.

- `LLMClient` protocol + `StubLLM` with scripted tool calls.
- **Provenance is DECLARED, never inferred.** Each StubLLM plan entry carries `from_steps: list[int]`; runner copies verbatim. Sequential adjacency is NOT an edge. No upstream → `from_steps: []`.
- Map each `ToolResult` → `Step.tags`.
- Write under `traces/<label>/` using `dump_trace`.
- Default `run_id` = `f"{scenario_name}-{seed}"`.

Note in PR: StubLLM is default for CI; issue #1 said Ollama-first — intentional deviation.

### Tasks

- [ ] `rivet.agent.llm`: protocol + StubLLM
- [ ] `rivet.agent.runner`: `run_scenario`
- [ ] Integration test `tests/test_runner.py` with multi-step stub plan + provenance joins
- [ ] PR comments on #4 (does not close)

### Verification

```powershell
.venv\Scripts\python.exe -m pytest tests/test_runner.py -q
# expect exit 0, >=1 test; no Ollama
```

### Exit criteria

- Stub-driven run produces schema-valid Trace without Ollama.
- Join provenance (`from_steps` with 2 parents) covered by a test.
- Byte-identical dump for fixed seed.

---

## Step 3b — Ollama client + CLI + empty REGISTRY

**Status:** pending  
**GitHub issue:** https://github.com/wikycool/Rivet/issues/4 (closes)  
**Branch:** `feat/ai-agent-cli`  
**Blocked by:** Step 3a  
**Parallel with:** —  
**Model tier:** default  
**Rollback:** revert PR

### Context brief (cold start)

Own the CLI so Step 4 ∥ Step 5 stay additive-only.

- `OllamaClient` optional; live test skip if unavailable.
- `rivet.agent.scenarios.REGISTRY: dict[str, Scenario]` — empty but importable.
- `python -m rivet.agent.run --scenario NAME` — unknown name → non-zero exit + list known names.
- Steps 4/5 only register scenarios; they must not change argparse.

### Tasks

- [ ] `OllamaClient` + skip-marked smoke test
- [ ] `REGISTRY` + `run.py` CLI
- [ ] Test: unknown scenario exits non-zero
- [ ] PR: `Closes #4`

### Verification

```powershell
.venv\Scripts\python.exe -m pytest tests/test_cli.py tests/test_ollama.py -q
# ollama tests may skip; CLI test must pass
```

### Exit criteria

- CLI importable; empty registry; unknown scenario fails clearly.
- Issue #4 closed.

---

## Step 4 — Benign scenario

**Status:** pending  
**GitHub issue:** https://github.com/wikycool/Rivet/issues/5  
**Branch:** `feat/ai-scenario-benign`  
**Blocked by:** Step 3b  
**Parallel with:** Step 5  
**Model tier:** default  
**Rollback:** revert PR

### Context brief (cold start)

**Additive only:** register `benign` in `REGISTRY` + fixture + stub plan. Do not modify `run.py` argparse.

Path: trusted `read_file` only; no `query_db` / `send_email`. Label `benign`.

### Tasks

- [ ] Scenario + trusted fixture + stub plan (`from_steps` as needed)
- [ ] `tests/test_scenario_benign.py`
- [ ] PR: `Closes #5`

### Verification

```powershell
.venv\Scripts\python.exe -m pytest tests/test_scenario_benign.py -q
.venv\Scripts\python.exe -m rivet.agent.run --scenario benign
```

### Exit criteria

- Issue #5 acceptance criteria met.
- Demo works with stub (no Ollama).

---

## Step 5 — Attack scenario

**Status:** pending  
**GitHub issue:** https://github.com/wikycool/Rivet/issues/6  
**Branch:** `feat/ai-scenario-attack`  
**Blocked by:** Step 3b  
**Parallel with:** Step 4  
**Model tier:** default  
**Rollback:** revert PR

### Context brief (cold start)

**Additive only:** register `attack` in `REGISTRY`. Stub plan forces: untrusted `read_file` → sensitive `query_db` → external `send_email`. Prefer `from_steps` joining doc + DB into email step.

### Tasks

- [ ] Poisoned fixture + stub plan with join provenance
- [ ] `tests/test_scenario_attack.py`
- [ ] PR: `Closes #6`

### Verification

```powershell
.venv\Scripts\python.exe -m pytest tests/test_scenario_attack.py -q
.venv\Scripts\python.exe -m rivet.agent.run --scenario attack
```

### Exit criteria

- Trace path + tags match classic exfiltration.
- Issue #6 criteria met.

---

## Step 6 — Graph features from Trace

**Status:** pending  
**GitHub issue:** https://github.com/wikycool/Rivet/issues/7  
**Branch:** `feat/ai-graph-features`  
**Blocked by:** Step 4, Step 5  
**Parallel with:** —  
**Model tier:** default  
**Rollback:** revert PR

### Context brief (cold start)

`extract_features(trace) -> dict[str, float]` with keys in `FEATURE_ORDER`.

**Taint propagation (required):**

```
effective_trust(step) = untrusted if step.tags.source_trust == "untrusted"
  OR any transitive ancestor via provenance.from_steps is untrusted;
  else trusted.

crosses_trust_boundary = 1.0 if ∃ step with effective_trust == untrusted
  AND sink_type ∈ {sensitive, external}; else 0.0.
```

This is **reachability**, not positional ordering.

| Feature | Definition |
|---|---|
| `path_length` | step count |
| `crosses_trust_boundary` | as above |
| `sensitive_nodes_touched` | count sink_type=sensitive |
| `external_sinks` | count sink_type=external |
| `untrusted_sources` | count source_trust=untrusted |
| `tool_combo_rarity` | v1: hardcoded allowlist of known-benign tool combos → 0.0/1.0. **Do not** fit a frequency table on the two demos. Detector v1 must not read this feature. |

### Tasks

- [ ] `rivet.ml.features` + docs paragraph per feature
- [ ] Fixture Traces (frozen JSON) in `tests/fixtures/`
- [ ] `tests/test_features.py`
- [ ] PR: `Closes #7`

### Verification

```powershell
.venv\Scripts\python.exe -m pytest tests/test_features.py -q
```

### Exit criteria

- Benign: no boundary cross, external_sinks=0.
- Attack: boundary cross + external_sinks ≥ 1.
- Issue #7 criteria met.

---

## Step 7 — Simple Layer 2 detector (thresholds only)

**Status:** pending  
**GitHub issue:** https://github.com/wikycool/Rivet/issues/8  
**Branch:** `feat/ai-layer2-detector`  
**Blocked by:** Step 6  
**Parallel with:** —  
**Model tier:** default  
**Rollback:** revert PR

### Context brief (cold start)

**v1 is thresholds ONLY.** sklearn / IsolationForest / GNN out of scope until ≥50 traces.

Rule:

```
if crosses_trust_boundary and external_sinks > 0 → attack
elif crosses_trust_boundary or external_sinks > 0 → suspicious
else → benign
```

Do not use `tool_combo_rarity` in v1.

### Tasks

- [ ] `detect(features) -> Verdict`
- [ ] `tests/test_detector.py` — attack flagged, benign clean
- [ ] README note: Layer 2 v1 = thresholds; GNN later
- [ ] PR: `Closes #8`

### Verification

```powershell
.venv\Scripts\python.exe -m pytest tests/test_detector.py -q
```

### Exit criteria

- Deterministic on two demo feature vectors.
- Issue #8 criteria met.

---

## Step 8 — Demo polish + README

**Status:** pending  
**GitHub issue:** comment + close #1 when done  
**Branch:** `feat/ai-demo-polish`  
**Blocked by:** Step 7  
**Parallel with:** —  
**Model tier:** default  
**Rollback:** revert PR

### Context brief (cold start)

One documented command runs benign + attack and prints Trace summary + detector verdict. Update root README. Close parent #1.

### Tasks

- [ ] Demo script or CLI flag covering both scenarios + detect
- [ ] README: install, test, demo, link to this plan
- [ ] Comment on #1; close #1
- [ ] Mark steps done in this plan file

### Verification

```powershell
.venv\Scripts\python.exe -m pytest -q
# documented demo command succeeds with stub backend
```

### Exit criteria

- Fresh clone + venv + demo works without Ollama.
- Parent #1 closed.

---

## Anti-patterns to avoid

1. **Testing the LLM’s personality** — always StubLLM for CI.
2. **Second Trace schema** — one Pydantic model; tools use `ToolResult` only; runner is the sole adapter.
3. **Real sinks** — no SMTP, no cloud DB.
4. **GNN / sklearn in v1** — explicitly deferred.
5. **Horizontal slices** — don’t merge “all tools + all ML” in one PR.
6. **Blocking AI on MCP Tap** — runner produces Traces independently.
7. **GitHub Models** — do not depend.
8. **Skipping Step 0** — later PRs will fight imports/pytest.
9. **Inferring provenance from step order** — only declared `from_steps`.
10. **Editing CLI argparse in scenario PRs** — REGISTRY additive only.

---

## How to execute a step

```text
1. Read CONTEXT.md + Frozen public API + this step's section only.
2. Read the linked GitHub issue.
3. Branch from latest main.
4. Implement with /tdd (red-green-refactor).
5. Run this step's verification commands (expect exit 0).
6. Open PR with Closes #N (except 3a).
7. In PR body: confirm Anti-patterns 1–10 not violated.
8. Merge; update Status: done in this file.
```

---

## Audit trail

| Date | Change |
|---|---|
| 2026-07-26 | Initial blueprint from spec #1 and tickets #2–#8 |
| 2026-07-26 | Adversarial review (APPROVE WITH FIXES): frozen API; `src/rivet/` layout; split 3a/3b; CLI ownership; declared provenance; `from_steps` + `schema_version`; thresholds-only detector; CI + pytest path fixes; issue↔step map |
