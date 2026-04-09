from __future__ import annotations

import asyncio


async def _first_line(argv: list[str]) -> str | None:
    try:
        proc = await asyncio.create_subprocess_exec(
            *argv,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        out, _ = await proc.communicate()
        if proc.returncode != 0:
            return None
        line = out.decode("utf-8", errors="replace").strip().splitlines()
        if not line:
            return None
        return line[0][:300]
    except FileNotFoundError:
        return None


async def get_go_git_versions() -> tuple[str | None, str | None]:
    """Return first line of `go version` and `git --version`, or None if missing."""
    go_v = await _first_line(["go", "version"])
    git_v = await _first_line(["git", "--version"])
    return go_v, git_v
