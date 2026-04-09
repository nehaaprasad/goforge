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


class HealthResponse(BaseModel):
    ok: bool = True
    repo_root: str
    repo_exists: bool
