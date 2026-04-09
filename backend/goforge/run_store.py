from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass, field

from goforge.schemas import RunSnapshot, RunStatus, StepName, StepState, StepStatus


def _initial_steps() -> list[StepState]:
    names: list[StepName] = [
        "Planner",
        "Context Retrieval",
        "Code Generation",
        "Test Generation",
        "Validation",
        "PR Creation",
    ]
    return [StepState(name=n, status="pending") for n in names]


@dataclass
class RunRecord:
    run_id: str
    task: str
    repo_root: str
    status: RunStatus = "queued"
    steps: list[StepState] = field(default_factory=_initial_steps)
    logs: list[str] = field(default_factory=list)
    diff: str | None = None
    pr_url: str | None = None
    error: str | None = None
    event_queue: asyncio.Queue[RunSnapshot] = field(default_factory=asyncio.Queue)
    pipeline_task: asyncio.Task[None] | None = None

    def snapshot(self) -> RunSnapshot:
        return RunSnapshot(
            run_id=self.run_id,
            task=self.task,
            status=self.status,
            repo_root=self.repo_root,
            steps=list(self.steps),
            logs=list(self.logs),
            diff=self.diff,
            pr_url=self.pr_url,
            error=self.error,
        )


class RunStore:
    def __init__(self) -> None:
        self._runs: dict[str, RunRecord] = {}
        self._lock = asyncio.Lock()

    async def create(self, task: str, repo_root: str) -> RunRecord:
        run_id = str(uuid.uuid4())
        rec = RunRecord(run_id=run_id, task=task.strip(), repo_root=repo_root)
        async with self._lock:
            self._runs[run_id] = rec
        return rec

    async def get(self, run_id: str) -> RunRecord | None:
        async with self._lock:
            return self._runs.get(run_id)

    async def emit(self, run_id: str, snapshot: RunSnapshot) -> None:
        rec = await self.get(run_id)
        if rec is None:
            return
        await rec.event_queue.put(snapshot)


store = RunStore()
