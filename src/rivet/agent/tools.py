"""Fixture-backed fake tools for the target agent harness.

Returns ToolResult with taint/sink tag literals copied from the frozen Trace
contract. Does not import rivet.trace — Step 3 maps ToolResult → Step.tags.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

_FIXTURES = Path(__file__).resolve().parent / "fixtures"

# Known fixture keys → (relative path under fixtures/, source_trust).
_FILE_FIXTURES: dict[str, tuple[str, Literal["trusted", "untrusted"]]] = {
    "trusted_doc": ("trusted_doc.txt", "trusted"),
    "poisoned_doc": ("poisoned_doc.txt", "untrusted"),
    # Path-style aliases (same fixtures).
    "fixtures/trusted_doc.txt": ("trusted_doc.txt", "trusted"),
    "fixtures/poisoned_doc.txt": ("poisoned_doc.txt", "untrusted"),
}


@dataclass(frozen=True)
class ToolResult:
    outputs: dict
    source_trust: Literal["trusted", "untrusted"]
    sink_type: Literal["none", "sensitive", "external"]


def read_file(path_or_key: str) -> ToolResult:
    """Return fixture document content with source_trust from the fixture map."""
    key = path_or_key.strip().replace("\\", "/")
    if key not in _FILE_FIXTURES:
        known = ", ".join(sorted(_FILE_FIXTURES))
        raise KeyError(f"Unknown file fixture {path_or_key!r}; known: {known}")
    rel, trust = _FILE_FIXTURES[key]
    content = (_FIXTURES / rel).read_text(encoding="utf-8")
    return ToolResult(
        outputs={"content": content, "path": key},
        source_trust=trust,
        sink_type="none",
    )


def query_db(*, table: str = "users", **_: Any) -> ToolResult:
    """Return sensitive password-style rows from a local JSON fixture."""
    rows_raw = json.loads((_FIXTURES / "passwords.json").read_text(encoding="utf-8"))
    if table != "users":
        raise KeyError(f"Unknown table {table!r}; only 'users' is fixture-backed")
    # Flatten to dicts that include a 'password' key for tests/scenarios.
    rows: list[dict[str, str]] = [dict(row) for row in rows_raw]
    return ToolResult(
        outputs={"table": table, "rows": rows},
        source_trust="trusted",
        sink_type="sensitive",
    )


def send_email(*, to: str, subject: str, body: str, **_: Any) -> ToolResult:
    """Record an outbound email payload; no SMTP or network I/O."""
    return ToolResult(
        outputs={"to": to, "subject": subject, "body": body},
        source_trust="trusted",
        sink_type="external",
    )


TOOLS: dict[str, Callable[..., ToolResult]] = {
    "read_file": read_file,
    "query_db": query_db,
    "send_email": send_email,
}
