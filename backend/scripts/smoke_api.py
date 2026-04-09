#!/usr/bin/env python3
"""In-process smoke: GET /health + POST /api/run (no open port). Run from repo: cd backend && .venv/bin/python scripts/smoke_api.py"""

from __future__ import annotations

import os
import sys
from pathlib import Path

_backend = Path(__file__).resolve().parent.parent
os.chdir(_backend)
if str(_backend) not in sys.path:
    sys.path.insert(0, str(_backend))

from fastapi.testclient import TestClient  # noqa: E402

from goforge.main import app  # noqa: E402


def main() -> None:
    c = TestClient(app)
    h = c.get("/health")
    h.raise_for_status()
    body = h.json()
    assert body.get("ok") is True
    r = c.post("/api/run", json={"task": "smoke_api.py verification"})
    r.raise_for_status()
    data = r.json()
    assert "run_id" in data
    print("smoke_api: OK", data["run_id"])


if __name__ == "__main__":
    main()
