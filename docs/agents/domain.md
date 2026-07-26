# Domain Docs

How the engineering skills should consume this repo's domain documentation when exploring the codebase.

## Before exploring, read these

- **`CONTEXT.md`** at the repo root
- **`docs/adr/`** — read ADRs that touch the area you're about to work in

## File structure

```
/
├── CONTEXT.md
├── docs/adr/
├── plans/
└── src/rivet/
    ├── agent/    # Target agent (LLM + tools) — AI team
    ├── ml/       # Graph features, Layer 2 detector — AI team
    ├── attacks/  # Injection scenarios — AI team
    ├── proxy/    # MCP tap — infra team (future)
    └── policy/   # Layer 1 rules — infra team (future)
```

Package imports use the `rivet` namespace (e.g. `import rivet`, `from rivet.agent import ...`). Do not use bare top-level packages named `agent` or `ml` — they collide with PyPI distributions.

## Use the glossary's vocabulary

When naming domain concepts (issues, tests, modules), use terms from `CONTEXT.md`. See **Trace**, **Provenance graph**, **Taint**, **Sink**, **Layer 1**, **Layer 2**.
