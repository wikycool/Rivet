"""Target agent runner: scenario + LLMClient -> Trace."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

from rivet.agent.llm import FinalAction, LLMClient, StubToolCall, ToolCallAction
from rivet.agent.tools import TOOLS, ToolResult
from rivet.trace import Provenance, Step, Tags, Trace, dump_trace

Label = Literal["benign", "attack"]


@dataclass(frozen=True)
class Scenario:
    name: str
    label: Label
    # Optional StubLLM plan for CLI runs (Steps 4/5 fill this in).
    stub_plan: tuple[StubToolCall, ...] = field(default_factory=tuple)


def _invoke_tool(name: str, inputs: dict[str, Any]) -> ToolResult:
    if name not in TOOLS:
        known = ", ".join(sorted(TOOLS))
        raise KeyError(f"Unknown tool {name!r}; known: {known}")
    fn = TOOLS[name]
    if name == "read_file":
        path = inputs.get("path", inputs.get("path_or_key"))
        if path is None:
            raise ValueError("read_file requires 'path' (or 'path_or_key') in inputs")
        return fn(path)
    return fn(**inputs)


def run_scenario(
    scenario: Scenario,
    llm: LLMClient,
    *,
    run_id: str | None = None,
    seed: str = "1",
    traces_dir: Path | str | None = None,
) -> Trace:
    """Execute tool calls from ``llm`` and return a schema-valid Trace.

    Provenance is copied from each tool-call action's ``from_steps`` —
    never inferred from sequential order.
    """
    resolved_id = run_id if run_id is not None else f"{scenario.name}-{seed}"
    messages: list[Any] = [{"role": "user", "content": f"run scenario {scenario.name}"}]
    steps: list[Step] = []
    step_no = 0

    while True:
        action = llm.next_action(
            messages=messages,
            available_tools=list(TOOLS.keys()),
        )
        if isinstance(action, FinalAction):
            messages.append({"role": "assistant", "content": action.text})
            break

        if not isinstance(action, ToolCallAction):
            raise TypeError(f"Unexpected action type: {type(action)!r}")

        result = _invoke_tool(action.tool, action.inputs)
        step_no += 1
        step = Step(
            step=step_no,
            tool=action.tool,
            inputs=dict(action.inputs),
            outputs=dict(result.outputs),
            provenance=Provenance(from_steps=list(action.from_steps)),
            tags=Tags(
                source_trust=result.source_trust,
                sink_type=result.sink_type,
            ),
        )
        steps.append(step)
        messages.append(
            {
                "role": "tool",
                "tool": action.tool,
                "outputs": result.outputs,
            }
        )

    trace = Trace(
        schema_version="1",
        run_id=resolved_id,
        label=scenario.label,
        steps=steps,
    )

    root = Path(traces_dir) if traces_dir is not None else Path("traces")
    dest_dir = root / scenario.label
    dest_dir.mkdir(parents=True, exist_ok=True)
    dump_trace(trace, dest_dir / f"{resolved_id}.json")
    return trace
