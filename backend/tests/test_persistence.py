"""SQLite run snapshot persistence."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from goforge.persistence.sqlite_runs import init_db, load_snapshot, save_snapshot
from goforge.schemas import RunSnapshot, StepState


def _sample_snapshot(run_id: str = "rid-1") -> RunSnapshot:
    return RunSnapshot(
        run_id=run_id,
        task="hello",
        status="completed",
        repo_root="/tmp/r",
        steps=[StepState(name="Planner", status="done")],
        logs=["a"],
        diff=None,
        pr_url=None,
        error=None,
        code_notes=[],
        test_paths=[],
        coverage_focus=[],
    )


class TestPersistence(unittest.IsolatedAsyncioTestCase):
    async def test_save_load_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "t.db"
            await init_db(db_path)
            snap = _sample_snapshot()
            await save_snapshot(snap, db_path)
            loaded = await load_snapshot(snap.run_id, db_path)
            self.assertIsNotNone(loaded)
            assert loaded is not None
            self.assertEqual(loaded.run_id, snap.run_id)
            self.assertEqual(loaded.status, "completed")


if __name__ == "__main__":
    unittest.main()
