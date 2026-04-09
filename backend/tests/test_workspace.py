"""Smoke tests for git workspace helpers (isolated temp repos)."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from goforge.default_diff import MOCK_DIFF
from goforge.repo.workspace import ensure_git_repo, git_apply_unified, git_reset_clean
from goforge.validation.go_checks import run_go_build, run_go_test

_GO_MOD = """module example.com/sandbox

go 1.22
"""

_GREET = """// Package greet is a tiny package used to exercise go test in the sandbox repo.
package greet

// Hello returns a fixed string for tests and demos.
func Hello() string {
	return "hello"
}
"""

_GREET_TEST = """package greet

import "testing"

func TestHello(t *testing.T) {
	if Hello() != "hello" {
		t.Fatalf("Hello() = %q, want %q", Hello(), "hello")
	}
}
"""


def _write_minimal_module(root: Path) -> None:
    (root / "go.mod").write_text(_GO_MOD, encoding="utf-8")
    greet_dir = root / "internal" / "greet"
    greet_dir.mkdir(parents=True)
    (greet_dir / "greet.go").write_text(_GREET, encoding="utf-8")
    (greet_dir / "greet_test.go").write_text(_GREET_TEST, encoding="utf-8")


class TestWorkspace(unittest.IsolatedAsyncioTestCase):
    async def test_apply_patch_go_test_reset_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_module(root)

            ok, err = await ensure_git_repo(str(root))
            self.assertTrue(ok, msg=err)

            code, out = await git_reset_clean(str(root))
            self.assertEqual(code, 0, msg=out)

            acode, aout = await git_apply_unified(str(root), MOCK_DIFF)
            self.assertEqual(acode, 0, msg=aout)

            bcode, bout = await run_go_build(str(root))
            self.assertEqual(bcode, 0, msg=bout)

            tcode, tout = await run_go_test(str(root))
            self.assertEqual(tcode, 0, msg=tout)

            rcode, _ = await git_reset_clean(str(root))
            self.assertEqual(rcode, 0)

            text = (root / "internal" / "greet" / "greet.go").read_text(encoding="utf-8")
            self.assertNotIn("GoForage: applied mock diff", text)

    async def test_git_apply_rejects_bad_patch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_module(root)

            ok, err = await ensure_git_repo(str(root))
            self.assertTrue(ok, msg=err)

            bad = "this is not a valid patch\n"
            code, _ = await git_apply_unified(str(root), bad)
            self.assertNotEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
