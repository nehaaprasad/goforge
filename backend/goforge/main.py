from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from goforge.config import settings
from goforge.mock_pipeline import run_mock_pipeline
from goforge.run_store import store
from goforge.schemas import HealthResponse, RunCreateRequest, RunCreateResponse, RunSnapshot
from goforge.toolchain import get_go_git_versions

app = FastAPI(
    title="goforge API",
    description="PatchFlow orchestration backend (vertical slice).",
    version="0.1.0",
)

_origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins or ["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    root = settings.repo_root.resolve()
    go_v, git_v = await get_go_git_versions()
    return HealthResponse(
        repo_root=str(root),
        repo_exists=root.is_dir(),
        go_available=go_v is not None,
        git_available=git_v is not None,
        go_version_line=go_v,
        git_version_line=git_v,
    )


@app.post("/api/run", response_model=RunCreateResponse)
async def create_run(body: RunCreateRequest) -> RunCreateResponse:
    root = settings.repo_root.resolve()
    if not root.is_dir():
        raise HTTPException(
            status_code=400,
            detail=(
                f"Local repo path does not exist or is not a directory: {root}. "
                "Create ./sandbox-repo or set GOFORGE_REPO_ROOT."
            ),
        )

    rec = await store.create(body.task, repo_root=str(root))
    rec.pipeline_task = asyncio.create_task(run_mock_pipeline(rec))
    return RunCreateResponse(run_id=rec.run_id)


@app.get("/api/run/{run_id}", response_model=RunSnapshot)
async def get_run(run_id: str) -> RunSnapshot:
    rec = await store.get(run_id)
    if rec is None:
        raise HTTPException(status_code=404, detail="Run not found.")
    return rec.snapshot()


@app.get("/api/run/{run_id}/stream")
async def stream_run(run_id: str) -> StreamingResponse:
    rec = await store.get(run_id)
    if rec is None:
        raise HTTPException(status_code=404, detail="Run not found.")

    async def event_stream() -> AsyncIterator[bytes]:
        current = await store.get(run_id)
        if current is None:
            return
        snap = current.snapshot()
        yield _sse_encode(snap)
        if snap.status in ("completed", "failed"):
            return
        while True:
            try:
                next_snap = await asyncio.wait_for(
                    current.event_queue.get(), timeout=25.0
                )
                yield _sse_encode(next_snap)
                if next_snap.status in ("completed", "failed"):
                    return
            except TimeoutError:
                yield b": keepalive\n\n"
                latest = await store.get(run_id)
                if latest is None:
                    return
                if latest.status in ("completed", "failed"):
                    yield _sse_encode(latest.snapshot())
                    return

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


def _sse_encode(snapshot: RunSnapshot) -> bytes:
    payload = json.dumps(snapshot.model_dump(mode="json"), ensure_ascii=False)
    return f"data: {payload}\n\n".encode("utf-8")


@app.get("/api/pr/{run_id}")
async def pr_details(run_id: str):
    _ = run_id
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="PR details endpoint not implemented yet (GitHub integration pending).",
    )
