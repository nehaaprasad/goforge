from __future__ import annotations

from pathlib import Path


def list_go_source_paths(repo_root: str, *, limit: int = 40) -> list[str]:
    """
    Return repo-relative paths to .go files (excluding vendor and .git), sorted.
    """
    root = Path(repo_root).resolve()
    if not root.is_dir():
        return []

    out: list[str] = []
    for path in sorted(root.rglob("*.go")):
        parts = path.parts
        if "vendor" in parts or ".git" in parts:
            continue
        rel = path.relative_to(root).as_posix()
        out.append(rel)
        if len(out) >= limit:
            break
    return out
