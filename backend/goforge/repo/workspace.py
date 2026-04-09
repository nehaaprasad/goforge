from __future__ import annotations

import asyncio
import os
from pathlib import Path

_GIT_IDENTITY = (
    "-c",
    "user.email=goforge@local",
    "-c",
    "user.name=goforge sandbox",
)


async def _run(
    cwd: Path,
    argv: list[str],
    *,
    stdin: bytes | None = None,
) -> tuple[int, str]:
    proc = await asyncio.create_subprocess_exec(
        *argv,
        cwd=str(cwd),
        stdin=asyncio.subprocess.PIPE if stdin is not None else None,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
        env=os.environ.copy(),
    )
    out, _ = await proc.communicate(stdin)
    text = (out or b"").decode("utf-8", errors="replace")
    code = proc.returncode
    if code is None:
        return 1, text + "\n(exit code unknown)"
    return code, text


async def ensure_git_repo(repo_root: str) -> tuple[bool, str]:
    """
    Ensure repo_root is a git worktree with at least one commit (sandbox baseline).
    Safe to call on every run.
    """
    root = Path(repo_root).resolve()
    if not root.is_dir():
        return False, f"not a directory: {root}"

    git_dir = root / ".git"
    if git_dir.exists():
        return True, ""

    code, out = await _run(root, ["git", "init"])
    if code != 0:
        return False, f"git init failed:\n{out}"

    code, out = await _run(
        root,
        ["git", *_GIT_IDENTITY, "add", "-A"],
    )
    if code != 0:
        return False, f"git add failed:\n{out}"

    code, out = await _run(
        root,
        ["git", *_GIT_IDENTITY, "commit", "-m", "chore: sandbox baseline"],
    )
    if code != 0:
        return False, f"git commit failed:\n{out}"

    return True, ""


async def git_reset_clean(repo_root: str) -> tuple[int, str]:
    """Restore tracked files and remove untracked artifacts (best-effort)."""
    root = Path(repo_root).resolve()
    if not (root / ".git").is_dir():
        return 0, ""

    code1, o1 = await _run(root, ["git", "reset", "--hard", "HEAD"])
    code2, o2 = await _run(root, ["git", "clean", "-fd"])
    combined = (o1 + "\n" + o2).strip()
    return (code1 if code1 != 0 else code2), combined


async def git_apply_unified(repo_root: str, diff_text: str) -> tuple[int, str]:
    """
    Apply a unified diff with `git apply`. Runs `--check` first so the worktree
    is not modified when the patch does not apply cleanly.
    """
    root = Path(repo_root).resolve()
    if not (root / ".git").is_dir():
        return 1, "git apply: .git missing (call ensure_git_repo first)"

    data = diff_text.encode("utf-8")
    code, out = await _run(root, ["git", "apply", "--check", "-"], stdin=data)
    if code != 0:
        return code, out

    return await _run(root, ["git", "apply", "-"], stdin=data)
