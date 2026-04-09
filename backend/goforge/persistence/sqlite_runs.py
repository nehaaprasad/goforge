"""SQLite persistence for run snapshots (production durability)."""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import TYPE_CHECKING

import aiosqlite

if TYPE_CHECKING:
    from goforge.schemas import RunSnapshot

logger = logging.getLogger("goforge.persistence")

SCHEMA = """
CREATE TABLE IF NOT EXISTS run_snapshots (
  run_id TEXT PRIMARY KEY,
  payload TEXT NOT NULL,
  updated_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_run_snapshots_updated ON run_snapshots(updated_at);
"""


async def init_db(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(db_path) as db:
        await db.executescript(SCHEMA)
        await db.commit()


async def save_snapshot(snap: "RunSnapshot", db_path: Path) -> None:
    payload = snap.model_dump_json()
    t = time.time()
    try:
        async with aiosqlite.connect(db_path) as db:
            await db.execute(
                "INSERT OR REPLACE INTO run_snapshots (run_id, payload, updated_at) VALUES (?, ?, ?)",
                (snap.run_id, payload, t),
            )
            await db.commit()
    except OSError as exc:
        logger.exception("SQLite save failed: %s", exc)
        raise


async def load_snapshot(run_id: str, db_path: Path) -> "RunSnapshot | None":
    from goforge.schemas import RunSnapshot

    try:
        async with aiosqlite.connect(db_path) as db:
            db.row_factory = aiosqlite.Row
            cur = await db.execute(
                "SELECT payload FROM run_snapshots WHERE run_id = ?", (run_id,)
            )
            row = await cur.fetchone()
            if row is None:
                return None
            return RunSnapshot.model_validate_json(row["payload"])
    except OSError as exc:
        logger.warning("SQLite load failed: %s", exc)
        return None


async def mark_stale_runs_failed(db_path: Path) -> int:
    """
    After a crash/restart, runs that were queued or running cannot continue.
    Mark them failed so clients do not poll forever.
    """
    from goforge.schemas import RunSnapshot

    try:
        async with aiosqlite.connect(db_path) as db:
            db.row_factory = aiosqlite.Row
            cur = await db.execute("SELECT run_id, payload FROM run_snapshots")
            rows = await cur.fetchall()
    except OSError:
        return 0

    count = 0
    try:
        async with aiosqlite.connect(db_path) as db:
            for row in rows:
                snap = RunSnapshot.model_validate_json(row["payload"])
                if snap.status not in ("queued", "running"):
                    continue
                updated = snap.model_copy(
                    update={
                        "status": "failed",
                        "error": "Run interrupted by server restart.",
                    }
                )
                await db.execute(
                    "INSERT OR REPLACE INTO run_snapshots (run_id, payload, updated_at) VALUES (?, ?, ?)",
                    (updated.run_id, updated.model_dump_json(), time.time()),
                )
                count += 1
            await db.commit()
    except OSError as exc:
        logger.warning("mark_stale_runs_failed: %s", exc)
        return count
    if count:
        logger.info("Marked %d interrupted run(s) as failed after restart.", count)
    return count
