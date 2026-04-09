from __future__ import annotations

import asyncio
import os
from pathlib import Path


async def run_go_test(repo_root: str) -> tuple[int, str]:
    """
    Run `go test ./...` in repo_root.

    Returns (exit_code, combined stdout+stderr). Exit code is non-zero on failure
    or if `go` is missing from PATH.
    """
    root = Path(repo_root).resolve()
    if not root.is_dir():
        return 1, f"not a directory: {root}"

    try:
        proc = await asyncio.create_subprocess_exec(
            "go",
            "test",
            "./...",
            cwd=str(root),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            env=os.environ.copy(),
        )
    except FileNotFoundError:
        return 127, "go: command not found (install Go or fix PATH)"

    out, _ = await proc.communicate()
    text = out.decode("utf-8", errors="replace")
    code = proc.returncode
    if code is None:
        return 1, text + "\n(process exit code unknown)"
    return code, text
