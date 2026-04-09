from __future__ import annotations

import asyncio

from goforge.run_store import RunRecord, store
from goforge.schemas import StepStatus
from goforge.validation.go_checks import run_go_test


async def _delay(seconds: float) -> None:
    await asyncio.sleep(seconds)


def _set_step_status(rec: RunRecord, name: str, status: StepStatus) -> None:
    for s in rec.steps:
        if s.name == name:
            s.status = status
            return


async def _append_log(rec: RunRecord, line: str) -> None:
    rec.logs.append(line)
    await store.emit(rec.run_id, rec.snapshot())


async def _run_mock_step(
    rec: RunRecord, step_name: str, log_lines: list[str]
) -> None:
    _set_step_status(rec, step_name, "running")
    await store.emit(rec.run_id, rec.snapshot())
    await _delay(0.15)

    for line in log_lines:
        await _append_log(rec, line)
        await _delay(0.08)

    _set_step_status(rec, step_name, "done")
    await store.emit(rec.run_id, rec.snapshot())
    await _delay(0.05)


MOCK_DIFF = (
    "--- a/internal/greet/greet.go\n"
    "+++ b/internal/greet/greet.go\n"
    "@@ -1,6 +1,7 @@\n"
    " package greet\n"
    " \n"
    " // Hello returns a fixed string for tests and demos.\n"
    " func Hello() string {\n"
    "+\t// PatchFlow: mock diff — replace with agent output.\n"
    "\treturn \"hello\"\n"
    " }\n"
)


async def run_mock_pipeline(rec: RunRecord) -> None:
    try:
        rec.status = "running"
        await store.emit(rec.run_id, rec.snapshot())

        await _append_log(rec, "Run started against local sandbox repository.")

        early_stages: list[tuple[str, list[str]]] = [
            (
                "Planner",
                [
                    "Planner: decomposing ticket into scoped steps.",
                    "Planner: candidate files — internal/greet (mock).",
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
        ]

        for step_name, lines in early_stages:
            await _run_mock_step(rec, step_name, lines)

        rec.diff = MOCK_DIFF
        await store.emit(rec.run_id, rec.snapshot())

        _set_step_status(rec, "Validation", "running")
        await store.emit(rec.run_id, rec.snapshot())
        await _append_log(rec, "Validation: running go test ./...")

        code, output = await run_go_test(rec.repo_root)
        for line in (output.splitlines() if output.strip() else ["(no output)"]):
            await _append_log(rec, line)

        if code != 0:
            _set_step_status(rec, "Validation", "failed")
            rec.status = "failed"
            rec.error = f"go test ./... exited with code {code}"
            rec.pr_url = None
            await store.emit(rec.run_id, rec.snapshot())
            return

        _set_step_status(rec, "Validation", "done")
        await store.emit(rec.run_id, rec.snapshot())

        _set_step_status(rec, "PR Creation", "running")
        await store.emit(rec.run_id, rec.snapshot())
        await _delay(0.12)
        await _append_log(
            rec,
            "PR: skipped — GitHub integration not enabled (validation passed).",
        )
        await _delay(0.05)
        _set_step_status(rec, "PR Creation", "done")

        rec.status = "completed"
        rec.pr_url = None
        await _append_log(
            rec,
            "Pipeline completed: go test passed; PR automation is the next integration step.",
        )
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
