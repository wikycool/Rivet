# Rivet

AI agent security platform with an MCP proxy and provenance graph.

Rivet provides **two-layer defense** for agent workflows:

1. **Rules layer** — declarative policies that gate tool calls, data access, and side effects before they execute.
2. **Behavioral patterns layer** — runtime signals and graph-backed provenance to detect anomalous or unsafe agent behavior over time.

## Project layout

```
src/     Application code (MCP proxy, policy engine, provenance graph)
docs/    Architecture notes, threat models, and design docs
tests/   Unit and integration tests
```

## Status

Early scaffold — implementation in progress.
