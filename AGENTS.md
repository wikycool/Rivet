# Rivet — Agent Instructions

## Agent skills

This repo uses [Matt Pocock's engineering skills](https://github.com/mattpocock/skills). Skills live in `.agents/skills/` (installed via `npx skills@latest add mattpocock/skills`).

**Run once per clone:** `/setup-matt-pocock-skills` (already configured — see `docs/agents/`).

**Common flows:**

| Skill | When to use |
|---|---|
| `/grill-with-docs` | Sharpen a design; builds `CONTEXT.md` and ADRs |
| `/to-spec` | Turn a conversation into a GitHub issue spec |
| `/to-tickets` | Break a spec into tracer-bullet tickets |
| `/prototype` | Throwaway agent harness or graph viz |
| `/tdd` | Build features test-first (agent runner, ML features) |
| `/implement` | Implement from spec/tickets with TDD + code review |
| `/research` | Background research (AgentDojo, MCP, taint tracking) |

Read `CONTEXT.md` before exploring the codebase. Issue tracker: GitHub (`wikycool/Rivet`).
