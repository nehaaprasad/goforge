from typing import Literal

from pydantic import BaseModel, Field

StepName = Literal[
    "Planner",
    "Context Retrieval",
    "Code Generation",
    "Test Generation",
    "Validation",
    "PR Creation",
]

StepStatus = Literal["pending", "running", "done", "failed"]

RunStatus = Literal["queued", "running", "completed", "failed"]


class StepState(BaseModel):
    name: StepName
    status: StepStatus = "pending"


class RunCreateRequest(BaseModel):
    task: str = Field(min_length=1, max_length=32_000)
    """Optional public HTTPS git URL; when set, the pipeline runs against a cached clone."""
    repo_url: str | None = Field(default=None, max_length=2048)


class RunCreateResponse(BaseModel):
    run_id: str


class RunSnapshot(BaseModel):
    run_id: str
    task: str
    status: RunStatus
    repo_root: str
    steps: list[StepState]
    logs: list[str]
    diff: str | None = None
    pr_url: str | None = None
    error: str | None = None
    # Structured agent outputs (PDF contracts: code notes; test paths + coverage focus)
    code_notes: list[str] = Field(default_factory=list)
    test_paths: list[str] = Field(default_factory=list)
    coverage_focus: list[str] = Field(default_factory=list)


class PlannerOutput(BaseModel):
    """Strict planner contract (matches PatchFlow agent JSON shape)."""

    tasks: list[str] = Field(default_factory=list)
    files: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)


class CodeAgentOutput(BaseModel):
    """Code agent JSON contract (unified diff + reviewer notes)."""

    unified_diff: str = Field(min_length=1)
    notes: list[str] = Field(default_factory=list)


class TestAgentOutput(BaseModel):
    """Test agent JSON contract (paths to test files + scenarios)."""

    tests: list[str] = Field(default_factory=list)
    coverage_focus: list[str] = Field(default_factory=list)


class HealthResponse(BaseModel):
    ok: bool = True
    repo_root: str
    repo_exists: bool
    remote_clone_enabled: bool = True
    go_available: bool = False
    git_available: bool = False
    go_version_line: str | None = None
    git_version_line: str | None = None
    persistence_enabled: bool = True
    persistence: Literal["sqlite", "memory"] = "sqlite"
    database_path: str | None = None
    openai_key_configured: bool = False


class PRDetailsResponse(BaseModel):
    run_id: str
    status: RunStatus
    pr_url: str | None = None
    error: str | None = None
