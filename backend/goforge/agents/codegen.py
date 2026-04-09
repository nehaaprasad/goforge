from __future__ import annotations

import json
import re
from typing import Any

import httpx
from pydantic import BaseModel, Field, ValidationError

from goforge.config import settings
from goforge.default_diff import MOCK_DIFF
from goforge.schemas import PlannerOutput

_SYSTEM = (
    "You are an expert Go engineer. Produce a single unified diff (git format) "
    "that applies cleanly to the repository. Paths in the diff must be repo-relative "
    "(e.g. internal/foo/bar.go). Do not include markdown fences. "
    "Prefer minimal changes. If tests need updates, include *_test.go hunks in the same diff. "
    "Return JSON only with key unified_diff (string). The diff must be valid unified diff text."
)


class _CodegenOutput(BaseModel):
    unified_diff: str = Field(min_length=1)


def _strip_json_fences(raw: str) -> str:
    s = raw.strip()
    m = re.match(r"^```(?:json)?\s*\n?([\s\S]*?)\n?```\s*$", s)
    if m:
        return m.group(1).strip()
    return s


def _parse_codegen_json(raw: str) -> str:
    s = _strip_json_fences(raw)
    try:
        data: Any = json.loads(s)
    except json.JSONDecodeError as exc:
        raise ValueError(f"codegen returned non-JSON: {exc}") from exc
    try:
        out = _CodegenOutput.model_validate(data)
    except ValidationError as exc:
        raise ValueError(f"codegen JSON invalid: {exc}") from exc
    return out.unified_diff.strip()


def _mock_codegen(task: str, repo_root: str, plan: PlannerOutput) -> str:
    _ = (task, repo_root, plan)
    return MOCK_DIFF


async def _llm_codegen(
    task: str,
    repo_root: str,
    plan: PlannerOutput,
    context_bundle: str,
    previous_failure: str | None,
) -> str:
    key = settings.openai_api_key
    if not key or not str(key).strip():
        return _mock_codegen(task, repo_root, plan)

    risks = "\n".join(f"- {r}" for r in plan.risks) or "(none)"
    tasks = "\n".join(f"- {t}" for t in plan.tasks) or "(none)"
    plan_files = "\n".join(f"- {p}" for p in plan.files) or "(none)"

    fail_block = ""
    if previous_failure:
        fail_block = (
            "\n\nPrevious attempt failed. Fix the patch or tests.\n"
            f"<failure>\n{previous_failure[:12_000]}\n</failure>\n"
        )

    user = (
        f"Task:\n{task}\n\n"
        f"Planner tasks:\n{tasks}\n"
        f"Planner files:\n{plan_files}\n"
        f"Planner risks:\n{risks}\n\n"
        f"Repository root: {repo_root}\n\n"
        f"Source context:\n{context_bundle}\n"
        f"{fail_block}"
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
        "temperature": 0.1,
    }

    timeout = httpx.Timeout(settings.codegen_timeout_s)
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(url, headers=headers, json=body)
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            detail = response.text[:800]
            raise RuntimeError(
                f"codegen HTTP {response.status_code}: {detail}"
            ) from exc

        payload = response.json()
        try:
            content = payload["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(f"codegen: unexpected API response: {payload!r}") from exc

    return _parse_codegen_json(content)


async def generate_unified_diff(
    task: str,
    repo_root: str,
    plan: PlannerOutput,
    context_bundle: str,
    *,
    previous_failure: str | None = None,
) -> tuple[str, str | None]:
    """
    Produce a unified diff. Uses OpenAI-compatible Chat Completions when
    GOFORGE_OPENAI_API_KEY is set; otherwise returns the sandbox mock diff.

    Returns (diff, warning). Warning is set when an LLM was requested but
    generation failed and the sandbox mock diff was used instead.
    """
    if not settings.openai_api_key or not str(settings.openai_api_key).strip():
        return _mock_codegen(task, repo_root, plan), None

    try:
        return (
            await _llm_codegen(
                task, repo_root, plan, context_bundle, previous_failure
            ),
            None,
        )
    except Exception as exc:
        return _mock_codegen(task, repo_root, plan), (
            f"LLM codegen failed; using sandbox mock diff: {exc}"
        )
