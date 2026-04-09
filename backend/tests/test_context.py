"""Context bundle loading."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from goforge.context.bundle import build_context_bundle
from goforge.schemas import PlannerOutput


class TestContextBundle(unittest.TestCase):
    def test_loads_planner_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "go.mod").write_text("module t\n\ngo 1.22\n", encoding="utf-8")
            (root / "internal" / "x").mkdir(parents=True)
            (root / "internal" / "x" / "a.go").write_text("package x\n", encoding="utf-8")

            plan = PlannerOutput(files=["internal/x/a.go"], tasks=[], risks=[])
            text = build_context_bundle(str(root), plan)
            self.assertIn("internal/x/a.go", text)
            self.assertIn("package x", text)

    def test_fallback_when_no_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "go.mod").write_text("module t\n\ngo 1.22\n", encoding="utf-8")
            (root / "b.go").write_text("package main\n", encoding="utf-8")
            plan = PlannerOutput(files=[], tasks=[], risks=[])
            text = build_context_bundle(str(root), plan)
            self.assertIn("b.go", text)


if __name__ == "__main__":
    unittest.main()
