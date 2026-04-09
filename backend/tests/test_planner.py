"""Planner agent: mock path and repo scanning."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

import httpx

from goforge.agents.planner import run_planner
from goforge.config import settings
from goforge.repo.scan import list_go_source_paths


class TestPlanner(unittest.IsolatedAsyncioTestCase):
    async def test_mock_planner_returns_schema(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "go.mod").write_text("module t\n\ngo 1.22\n", encoding="utf-8")
            (root / "p").mkdir()
            (root / "p" / "x.go").write_text("package p\n", encoding="utf-8")

            plan = await run_planner("add logging", str(root))
            self.assertTrue(plan.tasks)
            self.assertTrue(plan.files)
            self.assertTrue(plan.risks)

    def test_list_go_respects_limit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for i in range(5):
                (root / f"f{i}.go").write_text("package x\n", encoding="utf-8")
            paths = list_go_source_paths(str(root), limit=3)
            self.assertEqual(len(paths), 3)

    async def test_llm_failure_falls_back_with_risk(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "go.mod").write_text("module t\n\ngo 1.22\n", encoding="utf-8")
            (root / "a.go").write_text("package a\n", encoding="utf-8")

            mock_client = AsyncMock()
            mock_client.post = AsyncMock(
                side_effect=httpx.ConnectError("no network in test")
            )
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)

            with (
                patch.object(settings, "openai_api_key", "sk-test"),
                patch(
                    "goforge.agents.planner.httpx.AsyncClient",
                    return_value=mock_client,
                ),
            ):
                plan = await run_planner("task", str(root))

            self.assertTrue(any("LLM planner failed" in r for r in plan.risks))
            self.assertTrue(plan.tasks)


if __name__ == "__main__":
    unittest.main()
