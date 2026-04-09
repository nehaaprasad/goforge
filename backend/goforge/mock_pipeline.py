from __future__ import annotations

import asyncio

from goforge.agents.codegen import generate_unified_diff
from goforge.agents.planner import run_planner
from goforge.agents.test_agent import run_test_agent
from goforge.config import settings
from goforge.context.bundle import build_context_bundle
from goforge.rag.pipeline import build_rag_context_section
from goforge.github.pr import try_create_github_pr
from goforge.repo.workspace import ensure_git_repo, git_apply_unified, git_reset_clean
from goforge.run_store import RunRecord, store
from goforge.schemas import PlannerOutput, StepStatus
from goforge.validation.go_checks import run_go_build, run_go_test


async def _delay(seconds: float) -> None:
    await asyncio.sleep(seconds)


def _is_remote_clone_path(repo_root: str) -> bool:
    return "/clones/" in repo_root.replace("\\", "/")


def _set_step_status(rec: RunRecord, name: str, status: StepStatus) -> None:
    for s in rec.steps:
        if s.name == name:
            s.status = status
            return


async def _append_log(rec: RunRecord, line: str) -> None:
    rec.logs.append(line)
    await store.emit(rec.run_id, rec.snapshot())


async def _run_planner_step(rec: RunRecord) -> PlannerOutput:
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
    return plan


async def _run_context_step(rec: RunRecord, plan: PlannerOutput) -> str:
    _set_step_status(rec, "Context Retrieval", "running")
    await store.emit(rec.run_id, rec.snapshot())
    await _delay(0.08)

    await _append_log(rec, "Context: loading planner-selected paths (bounded).")

    rag_section, rag_status = await build_rag_context_section(
        rec.repo_root, plan, rec.task
    )
    if rag_status == "rag":
        await _append_log(
            rec,
            f"RAG: retrieved top-{settings.rag_top_k} chunks (embedding similarity).",
        )
    elif rag_status == "skipped_no_key":
        await _append_log(
            rec,
            "RAG: skipped — set GOFORGE_OPENAI_API_KEY to enable embedding retrieval.",
        )
    elif rag_status == "skipped_disabled":
        await _append_log(rec, "RAG: disabled (GOFORGE_RAG_ENABLED=false).")
    elif rag_status == "skipped_no_chunks":
        await _append_log(rec, "RAG: no .go chunks to index.")
    elif rag_status.startswith("error"):
        await _append_log(rec, f"RAG: failed ({rag_status}) — using file bundle only.")

    bundle = build_context_bundle(rec.repo_root, plan)
    if rag_section:
        bundle = rag_section + "\n\n" + bundle
    await _append_log(rec, f"Context: bundle size ~{len(bundle)} characters (UTF-8).")

    _set_step_status(rec, "Context Retrieval", "done")
    await store.emit(rec.run_id, rec.snapshot())
    await _delay(0.05)
    return bundle


async def _run_codegen_step(
    rec: RunRecord,
    plan: PlannerOutput,
    context_bundle: str,
    *,
    previous_failure: str | None,
) -> tuple[str, str | None]:
    _set_step_status(rec, "Code Generation", "running")
    await store.emit(rec.run_id, rec.snapshot())
    await _delay(0.12)

    if previous_failure:
        await _append_log(
            rec,
            "Code agent: regenerating unified diff (validation feedback).",
        )

    diff, code_notes, warn = await generate_unified_diff(
        rec.task,
        rec.repo_root,
        plan,
        context_bundle,
        previous_failure=previous_failure,
    )
    if warn:
        await _append_log(rec, warn)

    rec.code_notes = list(code_notes)
    rec.diff = diff
    await store.emit(rec.run_id, rec.snapshot())
    await _append_log(rec, "Code agent: unified diff ready.")
    for note in code_notes:
        await _append_log(rec, f"Code note: {note}")
    _set_step_status(rec, "Code Generation", "done")
    await store.emit(rec.run_id, rec.snapshot())
    await _delay(0.05)
    return diff, warn


async def _run_testgen_step(rec: RunRecord, plan: PlannerOutput, diff: str) -> None:
    _set_step_status(rec, "Test Generation", "running")
    await store.emit(rec.run_id, rec.snapshot())
    await _delay(0.1)

    out, warn = await run_test_agent(rec.task, plan, diff)
    if warn:
        await _append_log(rec, warn)

    rec.test_paths = list(out.tests)
    rec.coverage_focus = list(out.coverage_focus)
    await store.emit(rec.run_id, rec.snapshot())

    if out.tests:
        for p in out.tests:
            await _append_log(rec, f"Test agent: suggested file — {p}")
    else:
        await _append_log(
            rec,
            "Test agent: no test file paths suggested (relying on existing tests).",
        )
    for c in out.coverage_focus:
        await _append_log(rec, f"Test agent: coverage — {c}")

    if "_test.go" in diff or "Test" in diff:
        await _append_log(
            rec,
            "Test agent: diff includes test-related hunks (review).",
        )

    _set_step_status(rec, "Test Generation", "done")
    await store.emit(rec.run_id, rec.snapshot())
    await _delay(0.05)


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

        await _append_log(
            rec,
            "Run started against cached remote clone."
            if _is_remote_clone_path(rec.repo_root)
            else "Run started against local sandbox repository.",
        )
        await _append_log(
            rec,
            "Workspace: git baseline ready (reset to HEAD before patch).",
        )

        plan = await _run_planner_step(rec)
        context_bundle = await _run_context_step(rec, plan)

        diff, _warn = await _run_codegen_step(
            rec, plan, context_bundle, previous_failure=None
        )
        await _run_testgen_step(rec, plan, diff)

        max_attempts = (
            settings.validation_max_attempts
            if settings.openai_api_key and str(settings.openai_api_key).strip()
            else 1
        )
        failure: str | None = None
        validated = False

        for attempt in range(max_attempts):
            await git_reset_clean(rec.repo_root)
            if attempt > 0:
                await _append_log(
                    rec,
                    f"Validation: attempt {attempt + 1}/{max_attempts} (regenerating patch).",
                )
                diff, _warn = await _run_codegen_step(
                    rec, plan, context_bundle, previous_failure=failure
                )
                await _run_testgen_step(rec, plan, diff)

            rec.diff = diff
            await store.emit(rec.run_id, rec.snapshot())

            _set_step_status(rec, "Validation", "running")
            await store.emit(rec.run_id, rec.snapshot())

            await _append_log(rec, "Validation: applying unified diff (git apply)")

            acode, aout = await git_apply_unified(rec.repo_root, diff)
            for line in aout.splitlines() if aout.strip() else ["(git apply: no output)"]:
                await _append_log(rec, line)

            if acode != 0:
                failure = f"git apply failed:\n{aout}"
                if attempt + 1 < max_attempts:
                    await _append_log(
                        rec,
                        "Validation: git apply failed — will retry with a new patch.",
                    )
                    continue
                _set_step_status(rec, "Validation", "failed")
                rec.status = "failed"
                rec.error = failure
                rec.pr_url = None
                await store.emit(rec.run_id, rec.snapshot())
                return

            await _append_log(rec, "Validation: running go build ./...")

            bcode, bout = await run_go_build(rec.repo_root)
            for line in bout.splitlines() if bout.strip() else ["(no output)"]:
                await _append_log(rec, line)

            if bcode != 0:
                failure = f"go build ./... exited with code {bcode}\n{bout}"
                if attempt + 1 < max_attempts:
                    await _append_log(
                        rec,
                        "Validation: go build failed — will retry with a new patch.",
                    )
                    continue
                _set_step_status(rec, "Validation", "failed")
                rec.status = "failed"
                rec.error = failure
                rec.pr_url = None
                await store.emit(rec.run_id, rec.snapshot())
                return

            await _append_log(rec, "Validation: running go test ./...")

            tcode, output = await run_go_test(rec.repo_root)
            for line in output.splitlines() if output.strip() else ["(no output)"]:
                await _append_log(rec, line)

            if tcode != 0:
                failure = f"go test ./... exited with code {tcode}\n{output}"
                if attempt + 1 < max_attempts:
                    await _append_log(
                        rec,
                        "Validation: go test failed — will retry with a new patch.",
                    )
                    continue
                _set_step_status(rec, "Validation", "failed")
                rec.status = "failed"
                rec.error = failure
                rec.pr_url = None
                await store.emit(rec.run_id, rec.snapshot())
                return

            validated = True
            break

        if not validated:
            rec.status = "failed"
            rec.error = rec.error or "Validation failed after retries."
            rec.pr_url = None
            await store.emit(rec.run_id, rec.snapshot())
            return

        _set_step_status(rec, "Validation", "done")
        await store.emit(rec.run_id, rec.snapshot())

        _set_step_status(rec, "PR Creation", "running")
        await store.emit(rec.run_id, rec.snapshot())
        await _delay(0.08)

        pr_url, pr_logs = await try_create_github_pr(
            repo_root=rec.repo_root,
            run_id=rec.run_id,
            task=rec.task,
        )
        for line in pr_logs:
            await _append_log(rec, line)

        rec.pr_url = pr_url
        _set_step_status(rec, "PR Creation", "done")

        rec.status = "completed"
        rec.error = None
        await _append_log(
            rec,
            "Pipeline completed: patch applied; go build and go test passed.",
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
    finally:
        rcode, _ = await git_reset_clean(rec.repo_root)
        if rcode != 0:
            await store.emit(rec.run_id, rec.snapshot())
