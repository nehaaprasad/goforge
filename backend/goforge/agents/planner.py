from __future__ import annotations

import json
from typing import Any

import httpx
from pydantic import ValidationError

from goforge.config import settings
from goforge.repo.scan import list_go_source_paths
from goforge.schemas import PlannerOutput

_SYSTEM = (
    "You are a senior Go engineer planning a minimal change for a monorepo. "
    "Return JSON only with keys: tasks (array of short strings), files (array of "
    "repo-relative paths), risks (array of short strings). "
    "Paths must use forward slashes. No markdown, no code fences."
)


def _mock_planner(task: str, repo_root: str) -> PlannerOutput:
    paths = list_go_source_paths(repo_root, limit=20)
    return PlannerOutput(
        tasks=[
            "Locate relevant packages for the request",
            "Implement the smallest safe change",
            "Update or add tests",
            "Run go test ./...",
        ],
        files=(paths[:8] if paths else ["internal/greet/greet.go"]),
        risks=[
            "Planner running in mock mode (set GOFORGE_OPENAI_API_KEY for LLM)",
            f"Task preview: {task[:120]}{'…' if len(task) > 120 else ''}",
        ],
    )


def _parse_llm_json(raw: str) -> PlannerOutput:
    try:
        data: Any = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"planner returned non-JSON: {exc}") from exc
    try:
        return PlannerOutput.model_validate(data)
    except ValidationError as exc:
        raise ValueError(f"planner JSON does not match schema: {exc}") from exc


async def _llm_planner(task: str, repo_root: str) -> PlannerOutput:
    key = settings.openai_api_key
    if not key or not str(key).strip():
        return _mock_planner(task, repo_root)

    files = list_go_source_paths(repo_root, limit=35)
    file_block = "\n".join(f"- {p}" for p in files) or "(no .go files found)"
    user = f"Task:\n{task}\n\nGo files (subset):\n{file_block}\n"

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
        "temperature": 0.2,
    }

    timeout = httpx.Timeout(settings.planner_timeout_s)
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(url, headers=headers, json=body)
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            detail = response.text[:800]
            raise RuntimeError(
                f"planner HTTP {response.status_code}: {detail}"
            ) from exc

        payload = response.json()
        try:
            content = payload["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(f"planner: unexpected API response shape: {payload!r}") from exc

    return _parse_llm_json(content)


async def run_planner(task: str, repo_root: str) -> PlannerOutput:
    """
    Produce a structured plan. Uses OpenAI-compatible Chat Completions when
    GOFORGE_OPENAI_API_KEY is set; otherwise returns deterministic mock output.
    On LLM/network/API errors, falls back to mock output and appends a risk line.
    """
    if not settings.openai_api_key or not str(settings.openai_api_key).strip():
        return _mock_planner(task, repo_root)
    try:
        return await _llm_planner(task, repo_root)
    except Exception as exc:
        mock = _mock_planner(task, repo_root)
        return PlannerOutput(
            tasks=mock.tasks,
            files=mock.files,
            risks=list(mock.risks) + [f"LLM planner failed: {exc}"],
        )
