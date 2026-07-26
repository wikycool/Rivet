# Rivet

AI agent security platform: MCP proxy, provenance graph, two-layer defense (rules + behavioral patterns).

## Language

**Trace**:
A single agent run — ordered tool calls from one user task through completion.
_Avoid_: Session, log dump, conversation

**Provenance graph**:
The live map of nodes (tool calls, data artifacts) and edges (data flow between steps).
_Avoid_: Action log, dependency graph (generic)

**Tap**:
The MCP proxy that intercepts every tool call before it executes.
_Avoid_: Middleware, interceptor (generic)

**Guard**:
The enforcement layer that allows, blocks, or flags actions based on policy and patterns.
_Avoid_: Filter, firewall (generic)

**Taint**:
A trust label on data — where it originated (user, internal doc, untrusted web page, hidden injection).
_Avoid_: Tag, classification (generic)

**Sink**:
A destination where data can leave the system (external email, HTTP POST, file write outside sandbox).
_Avoid_: Output, endpoint (generic)

**Layer 1 (rules)**:
Deterministic information-flow policies — e.g. untrusted data must not reach an external sink.
_Avoid_: Rule engine, policy layer (without "Layer 1")

**Layer 2 (patterns)**:
Behavioral anomaly detection on provenance graphs — flags unusual action shapes rules miss.
_Avoid_: ML layer, AI detection (vague)

**Benign trace**:
A provenance graph from normal agent work (book flight, summarize doc).
_Avoid_: Good run, normal flow

**Attack trace**:
A provenance graph where prompt injection caused misuse (exfiltration, privilege abuse).
_Avoid_: Bad run, malicious session

**Target agent**:
The AI bot under test — uses tools and is the subject of attacks and monitoring.
_Avoid_: Victim bot, test LLM
