from __future__ import annotations

import asyncio

from goforge.agents.planner import run_planner
from goforge.config import settings
from goforge.repo.workspace import ensure_git_repo, git_apply_unified, git_reset_clean
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


async def _run_planner_step(rec: RunRecord) -> None:
    _set_step_status(rec, "Planner", "running")
    await store.emit(rec.run_id, rec.snapshot())
    await _delay(0.12)

    mode = (
        "llm"
        if settings.openai_api_key and str(settings.openai_api_key).strip()
        else "mock"
    )
    await _append_log(rec, f"Planner: mode={mode}")

    plan = await run_planner(rec.task, rec.repo_root)
    for item in plan.tasks:
        await _append_log(rec, f"Planner task: {item}")
    if plan.files:
        shown = plan.files[:14]
        await _append_log(rec, "Planner files: " + ", ".join(shown))
        if len(plan.files) > 14:
            await _append_log(
                rec, f"Planner: ({len(plan.files) - 14} additional path(s) omitted)"
            )
    for risk in plan.risks:
        await _append_log(rec, f"Planner risk: {risk}")

    _set_step_status(rec, "Planner", "done")
    await store.emit(rec.run_id, rec.snapshot())
    await _delay(0.05)


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


# Must apply cleanly to the committed baseline in sandbox-repo (see internal/greet).
MOCK_DIFF = (
    "--- a/internal/greet/greet.go\n"
    "+++ b/internal/greet/greet.go\n"
    "@@ -3,5 +3,6 @@\n"
    " \n"
    " // Hello returns a fixed string for tests and demos.\n"
    " func Hello() string {\n"
    "+\t// PatchFlow: applied mock diff (sandbox).\n"
    " \treturn \"hello\"\n"
    " }\n"
)


async def run_mock_pipeline(rec: RunRecord) -> None:
    try:
        ok, err = await ensure_git_repo(rec.repo_root)
        if not ok:
            rec.status = "failed"
            rec.error = err
            await store.emit(rec.run_id, rec.snapshot())
            return

        code, rout = await git_reset_clean(rec.repo_root)
        if code != 0:
            rec.status = "failed"
            rec.error = f"git reset failed:\n{rout}"
            await store.emit(rec.run_id, rec.snapshot())
            return

        rec.status = "running"
        await store.emit(rec.run_id, rec.snapshot())

        await _append_log(rec, "Run started against local sandbox repository.")
        await _append_log(
            rec,
            "Workspace: git baseline ready (reset to HEAD before patch).",
        )

        await _run_planner_step(rec)

        later_stages: list[tuple[str, list[str]]] = [
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

        for step_name, lines in later_stages:
            await _run_mock_step(rec, step_name, lines)

        rec.diff = MOCK_DIFF
        await store.emit(rec.run_id, rec.snapshot())

        try:
            _set_step_status(rec, "Validation", "running")
            await store.emit(rec.run_id, rec.snapshot())

            await _append_log(rec, "Validation: applying unified diff (git apply)")

            acode, aout = await git_apply_unified(rec.repo_root, MOCK_DIFF)
            for line in aout.splitlines() if aout.strip() else ["(git apply: no output)"]:
                await _append_log(rec, line)

            if acode != 0:
                _set_step_status(rec, "Validation", "failed")
                rec.status = "failed"
                rec.error = f"git apply failed with exit code {acode}"
                rec.pr_url = None
                await store.emit(rec.run_id, rec.snapshot())
                return

            await _append_log(rec, "Validation: running go test ./...")

            tcode, output = await run_go_test(rec.repo_root)
            for line in output.splitlines() if output.strip() else ["(no output)"]:
                await _append_log(rec, line)

            if tcode != 0:
                _set_step_status(rec, "Validation", "failed")
                rec.status = "failed"
                rec.error = f"go test ./... exited with code {tcode}"
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
                "Pipeline completed: patch applied, go test passed; PR automation is next.",
            )
            await store.emit(rec.run_id, rec.snapshot())

        finally:
            rcode, _ = await git_reset_clean(rec.repo_root)
            if rcode != 0:
                await _append_log(
                    rec,
                    f"Warning: post-run git reset returned {rcode} (sandbox may need manual cleanup).",
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
