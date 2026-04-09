"""Structured code + test agent outputs (schemas + mock paths)."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from goforge.agents.codegen import generate_unified_diff
from goforge.agents.test_agent import run_test_agent
from goforge.default_diff import MOCK_DIFF
from goforge.schemas import CodeAgentOutput, PlannerOutput, TestAgentOutput


class TestStructuredAgents(unittest.IsolatedAsyncioTestCase):
    async def test_mock_codegen_includes_notes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "go.mod").write_text("module t\n\ngo 1.22\n", encoding="utf-8")
            plan = PlannerOutput(tasks=["x"], files=["a.go"], risks=[])
            diff, notes, warn = await generate_unified_diff(
                "task", str(root), plan, "ctx", previous_failure=None
            )
            self.assertEqual(diff, MOCK_DIFF)
            self.assertTrue(notes)
            self.assertIsNone(warn)

    def test_code_agent_output_schema(self) -> None:
        raw = '{"unified_diff": "--- a/f.go\\n+++ b/f.go\\n", "notes": ["n1"]}'
        out = CodeAgentOutput.model_validate_json(raw)
        self.assertIn("f.go", out.unified_diff)
        self.assertEqual(out.notes, ["n1"])

    async def test_test_agent_mock_extracts_paths(self) -> None:
        diff = """diff --git a/internal/greet/greet_test.go b/internal/greet/greet_test.go
--- a/internal/greet/greet_test.go
+++ b/internal/greet/greet_test.go
@@ -1 +1 @@
"""
        plan = PlannerOutput(files=[], tasks=[], risks=[])
        out, warn = await run_test_agent("t", plan, diff)
        self.assertIn("internal/greet/greet_test.go", out.tests)
        self.assertIsNone(warn)

    def test_test_agent_output_schema(self) -> None:
        raw = '{"tests": ["a_test.go"], "coverage_focus": ["happy path"]}'
        out = TestAgentOutput.model_validate_json(raw)
        self.assertEqual(out.tests, ["a_test.go"])
        self.assertEqual(out.coverage_focus, ["happy path"])


if __name__ == "__main__":
    unittest.main()
