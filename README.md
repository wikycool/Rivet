# Rivet

AI agent security platform — **MCP tap**, **provenance graph**, and **two-layer defense** for tool-using agents.

1. **Layer 1 (rules)** — deterministic information-flow policies *(infra — not built yet)*.
2. **Layer 2 (patterns)** — graph features + threshold detector on agent Traces.

**Layer 2 v1** uses thresholds only (trust-boundary reachability + external sinks). **GNN / sklearn are later.**

## Quickstart

Requires Python 3.11+. No Ollama required for demos or CI.

```powershell
py -3.11 -m venv .venv
.venv\Scripts\python.exe -m pip install -e ".[dev]"
.venv\Scripts\python.exe -m pytest -q
```

## Demo (benign + attack + Layer 2 verdicts)

```powershell
.venv\Scripts\python.exe -m rivet.demo
```

Expected: benign → `verdict: benign`; attack → `verdict: attack`.

Single scenarios:

```powershell
.venv\Scripts\python.exe -m rivet.agent.run --scenario benign
.venv\Scripts\python.exe -m rivet.agent.run --scenario attack
```

## Layout

```
src/rivet/agent/   Target agent, tools, scenarios, StubLLM runner
src/rivet/ml/      Trace features + Layer 2 detector
src/rivet/trace.py Trace schema v1
docs/              Schema, features, agent config
plans/             Construction blueprint
tests/             Unit + integration (StubLLM only)
```

## Docs

- Blueprint: [`plans/rivet-ai-slice-agent-harness.md`](plans/rivet-ai-slice-agent-harness.md)
- Trace schema: [`docs/trace-schema.md`](docs/trace-schema.md)
- Features: [`docs/features.md`](docs/features.md)
- Glossary: [`CONTEXT.md`](CONTEXT.md)

Optional live LLM: `pip install -e ".[ollama]"` (not used by demos/CI).
