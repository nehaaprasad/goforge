from __future__ import annotations

import asyncio
import logging
import uuid
from dataclasses import dataclass, field

from goforge.config import settings
from goforge.persistence.sqlite_runs import load_snapshot, save_snapshot
from goforge.schemas import RunSnapshot, RunStatus, StepName, StepState, StepStatus

logger = logging.getLogger("goforge.run_store")


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


def record_from_snapshot(snap: RunSnapshot) -> "RunRecord":
    """Rebuild an in-memory record from a persisted snapshot (no live pipeline)."""
    return RunRecord(
        run_id=snap.run_id,
        task=snap.task,
        repo_root=snap.repo_root,
        status=snap.status,
        steps=list(snap.steps),
        logs=list(snap.logs),
        diff=snap.diff,
        pr_url=snap.pr_url,
        error=snap.error,
        code_notes=list(snap.code_notes),
        test_paths=list(snap.test_paths),
        coverage_focus=list(snap.coverage_focus),
    )


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
    code_notes: list[str] = field(default_factory=list)
    test_paths: list[str] = field(default_factory=list)
    coverage_focus: list[str] = field(default_factory=list)
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
            code_notes=list(self.code_notes),
            test_paths=list(self.test_paths),
            coverage_focus=list(self.coverage_focus),
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
        await self._persist(rec.snapshot())
        return rec

    async def get(self, run_id: str) -> RunRecord | None:
        async with self._lock:
            rec = self._runs.get(run_id)
        if rec is not None:
            return rec
        if not settings.persistence_enabled:
            return None
        snap = await load_snapshot(run_id, settings.db_path)
        if snap is None:
            return None
        rec = record_from_snapshot(snap)
        async with self._lock:
            if run_id not in self._runs:
                self._runs[run_id] = rec
            return self._runs[run_id]

    async def emit(self, run_id: str, snapshot: RunSnapshot) -> None:
        # Active runs are always in memory; do not hit SQLite here (hot path).
        async with self._lock:
            rec = self._runs.get(run_id)
        if rec is None:
            return
        await rec.event_queue.put(snapshot)
        await self._persist(snapshot)

    async def _persist(self, snapshot: RunSnapshot) -> None:
        if not settings.persistence_enabled:
            return
        try:
            await save_snapshot(snapshot, settings.db_path)
        except Exception as exc:
            logger.warning("Snapshot persist failed (run continues in memory): %s", exc)

    async def cancel_all_pipeline_tasks(self) -> None:
        async with self._lock:
            recs = list(self._runs.values())
        for rec in recs:
            t = rec.pipeline_task
            if t is not None and not t.done():
                t.cancel()
                try:
                    await t
                except asyncio.CancelledError:
                    pass


store = RunStore()
