from rivet.agent.llm import StubToolCall
from rivet.agent.runner import Scenario
from rivet.agent.scenarios import register

SCENARIO = Scenario(
    name="benign",
    label="benign",
    stub_plan=(
        StubToolCall(tool="read_file", inputs={"path": "trusted_doc"}, from_steps=[]),
    ),
)
register(SCENARIO)
