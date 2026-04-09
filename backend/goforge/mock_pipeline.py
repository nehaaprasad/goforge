from __future__ import annotations

import asyncio

from goforge.run_store import RunRecord, store
from goforge.schemas import StepStatus


async def _delay(seconds: float) -> None:
    await asyncio.sleep(seconds)


def _set_step_status(
    rec: RunRecord, name: str, status: StepStatus
) -> None:
    for s in rec.steps:
        if s.name == name:
            s.status = status
            return


async def _append_log(rec: RunRecord, line: str) -> None:
    rec.logs.append(line)
    await store.emit(rec.run_id, rec.snapshot())


async def run_mock_pipeline(rec: RunRecord) -> None:
    try:
        rec.status = "running"
        await store.emit(rec.run_id, rec.snapshot())

        await _append_log(rec, "Run started against local sandbox repository.")

        stages: list[tuple[str, list[str]]] = [
            (
                "Planner",
                [
                    "Planner: decomposing ticket into scoped steps.",
                    "Planner: candidate files — cmd/, internal/ (mock).",
                ],
            ),
            (
                "Context Retrieval",
                [
                    "Retriever: loading relevant packages (mock).",
                    "Retriever: ranked chunks ready for code agent.",
                ],
            ),
            (
                "Code Generation",
                [
                    "Code agent: proposing minimal unified diff (mock).",
                ],
            ),
            (
                "Test Generation",
                [
                    "Test agent: aligning tests with changed behavior (mock).",
                ],
            ),
            (
                "Validation",
                [
                    "Validation: go test ./... (not executed in mock slice).",
                ],
            ),
            (
                "PR Creation",
                [
                    "PR: branch/PR creation deferred until validation is real.",
                ],
            ),
        ]

        mock_diff = (
            "--- a/internal/example.go\n"
            "+++ b/internal/example.go\n"
            "@@ -1,3 +1,4 @@\n"
            " package internal\n"
            " \n"
            "+// PatchFlow mock diff — replace with agent output.\n"
            " const Example = 1\n"
        )

        for step_name, log_lines in stages:
            _set_step_status(rec, step_name, "running")
            await store.emit(rec.run_id, rec.snapshot())
            await _delay(0.15)

            for line in log_lines:
                await _append_log(rec, line)
                await _delay(0.08)

            _set_step_status(rec, step_name, "done")
            await store.emit(rec.run_id, rec.snapshot())
            await _delay(0.05)

        rec.diff = mock_diff
        rec.pr_url = None
        rec.status = "completed"
        await _append_log(rec, "Mock pipeline completed. Wire agents + go test next.")
        await store.emit(rec.run_id, rec.snapshot())

    except asyncio.CancelledError:
        rec.status = "failed"
        rec.error = "Run cancelled."
        await store.emit(rec.run_id, rec.snapshot())
        raise
    except Exception as exc:
        rec.status = "failed"
        rec.error = str(exc)
        await store.emit(rec.run_id, rec.snapshot())
