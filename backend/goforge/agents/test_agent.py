"""Test agent: structured JSON — paths to tests + coverage focus (PDF contract)."""

from __future__ import annotations

import json
import re
from typing import Any

import httpx
from pydantic import ValidationError

from goforge.config import settings
from goforge.schemas import PlannerOutput, TestAgentOutput

_SYSTEM = (
    "You are a senior Go test engineer. Given a task and a proposed unified diff, "
    "return JSON only with keys: tests (array of repo-relative paths to *_test.go files "
    "that should be created or updated for this change), coverage_focus (array of short "
    "strings describing scenarios to cover—e.g. happy path, edge cases, regressions). "
    "Use forward slashes in paths. If no test file is needed, tests may be empty."
)


def _extract_test_paths_from_diff(diff: str) -> list[str]:
    seen: list[str] = []
    for m in re.finditer(r"^\+\+\+ b/(.+)$", diff, re.MULTILINE):
        p = m.group(1).strip().split("\t")[0].strip()
        if p.endswith("_test.go") and p not in seen:
            seen.append(p)
    return seen


def _mock_test_agent(task: str, plan: PlannerOutput, diff: str) -> TestAgentOutput:
    paths = _extract_test_paths_from_diff(diff)
    if not paths:
        for f in plan.files:
            if f.endswith(".go") and "_test" not in f:
                candidate = f.replace(".go", "_test.go")
                paths.append(candidate)
                break
    if not paths:
        paths = ["internal/greet/greet_test.go"]  # sandbox default
    return TestAgentOutput(
        tests=paths,
        coverage_focus=[
            "Regression: existing package exports and behavior",
            f"Task alignment: {task[:120]}{'…' if len(task) > 120 else ''}",
        ],
    )


def _strip_json_fences(raw: str) -> str:
    s = raw.strip()
    m = re.match(r"^```(?:json)?\s*\n?([\s\S]*?)\n?```\s*$", s)
    if m:
        return m.group(1).strip()
    return s


def _parse_test_json(raw: str) -> TestAgentOutput:
    s = _strip_json_fences(raw)
    try:
        data: Any = json.loads(s)
    except json.JSONDecodeError as exc:
        raise ValueError(f"test agent returned non-JSON: {exc}") from exc
    try:
        return TestAgentOutput.model_validate(data)
    except ValidationError as exc:
        raise ValueError(f"test agent JSON invalid: {exc}") from exc


async def _llm_test_agent(
    task: str, plan: PlannerOutput, diff: str
) -> TestAgentOutput:
    key = settings.openai_api_key
    if not key or not str(key).strip():
        return _mock_test_agent(task, plan, diff)

    tasks = "\n".join(f"- {t}" for t in plan.tasks) or "(none)"
    files = "\n".join(f"- {p}" for p in plan.files) or "(none)"
    diff_excerpt = diff[:14_000] if len(diff) > 14_000 else diff
    if len(diff) > 14_000:
        diff_excerpt += "\n… [diff truncated for prompt]\n"

    user = (
        f"Task:\n{task}\n\n"
        f"Planner tasks:\n{tasks}\n"
        f"Planner files:\n{files}\n\n"
        f"Unified diff:\n{diff_excerpt}\n"
    )

    url = f"{settings.openai_base_url.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {key.strip()}",
        "Content-Type": "application/json",
    }
    body = {
        "model": settings.openai_model,
        "messages": [
            {"role": "system", "content": _SYSTEM},
            {"role": "user", "content": user},
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.15,
    }

    timeout = httpx.Timeout(settings.planner_timeout_s)
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(url, headers=headers, json=body)
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            detail = response.text[:800]
            raise RuntimeError(
                f"test agent HTTP {response.status_code}: {detail}"
            ) from exc

        payload = response.json()
        try:
            content = payload["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(f"test agent: unexpected API response: {payload!r}") from exc

    return _parse_test_json(content)


async def run_test_agent(
    task: str, plan: PlannerOutput, diff: str
) -> tuple[TestAgentOutput, str | None]:
    """
    Produce structured test suggestions. LLM when API key; otherwise deterministic mock.
    Returns (output, warning).
    """
    if not settings.openai_api_key or not str(settings.openai_api_key).strip():
        return _mock_test_agent(task, plan, diff), None

    try:
        return await _llm_test_agent(task, plan, diff), None
    except Exception as exc:
        return _mock_test_agent(task, plan, diff), f"LLM test agent failed; using mock: {exc}"
