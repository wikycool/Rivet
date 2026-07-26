# Rivet

AI agent security platform with an MCP proxy and provenance graph.

Rivet provides **two-layer defense** for agent workflows:

1. **Layer 1 (rules)** — deterministic information-flow policies that gate tool calls before they execute *(infra — not built yet)*.
2. **Layer 2 (patterns)** — behavioral signals on provenance graphs to detect anomalous agent behavior.

**Layer 2 v1** is a **threshold** detector on Trace features (trust-boundary reachability + external sinks). **GNN / sklearn are explicitly later** — not used in v1.

## Project layout

```
src/rivet/   Application package (agent, ml, attacks; proxy/policy later)
docs/        Architecture notes, agent config, ADRs, feature docs
plans/       Construction blueprints
tests/       Unit and integration tests
```

## Setup (AI slice)

Requires Python 3.11+.

```powershell
py -3.11 -m venv .venv
.venv\Scripts\python.exe -m pip install -e ".[dev]"
.venv\Scripts\python.exe -m pytest -q
```

Optional live LLM (not required for tests):

```powershell
.venv\Scripts\python.exe -m pip install -e ".[ollama]"
```

## Demo scenarios (StubLLM — no Ollama)

```powershell
.venv\Scripts\python.exe -m rivet.agent.run --scenario benign
.venv\Scripts\python.exe -m rivet.agent.run --scenario attack
```

## Blueprint

AI harness construction plan: [`plans/rivet-ai-slice-agent-harness.md`](plans/rivet-ai-slice-agent-harness.md)

Feature docs: [`docs/features.md`](docs/features.md) · Trace schema: [`docs/trace-schema.md`](docs/trace-schema.md)
