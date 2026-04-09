"""Load bounded text context from the repo for agent prompts."""

from __future__ import annotations

from pathlib import Path

from goforge.repo.scan import list_go_source_paths
from goforge.schemas import PlannerOutput

_MAX_FILE_BYTES = 256_000
_MAX_TOTAL_CHARS = 48_000


def build_context_bundle(repo_root: str, plan: PlannerOutput) -> str:
    """
    Read planner-selected paths (fallback: first Go files) with size limits.
    Returns a single string suitable for LLM prompts.
    """
    root = Path(repo_root).resolve()
    if not root.is_dir():
        return "(repo root missing)"

    candidates: list[str] = []
    seen: set[str] = set()
    for rel in plan.files:
        rel = rel.strip().replace("\\", "/")
        if not rel or rel in seen:
            continue
        seen.add(rel)
        candidates.append(rel)

    if not candidates:
        candidates = list_go_source_paths(str(root), limit=12)

    chunks: list[str] = []
    total = 0
    truncated_files = 0

    header = (
        f"Repository root: {root}\n"
        f"Context budget: ~{_MAX_TOTAL_CHARS} characters.\n\n"
    )
    total += len(header)

    for rel in candidates:
        path = root / rel
        if not path.is_file():
            line = f"=== {rel} (missing)\n\n"
            if total + len(line) > _MAX_TOTAL_CHARS:
                truncated_files += 1
                break
            chunks.append(line)
            total += len(line)
            continue

        raw = path.read_bytes()
        if len(raw) > _MAX_FILE_BYTES:
            text = raw[:_MAX_FILE_BYTES].decode("utf-8", errors="replace")
            text += "\n… [truncated: file too large]\n"
        else:
            text = raw.decode("utf-8", errors="replace")

        block = f"=== {rel}\n{text}\n"
        if total + len(block) > _MAX_TOTAL_CHARS:
            remain = _MAX_TOTAL_CHARS - total - 40
            if remain > 200:
                chunks.append(block[:remain] + "\n… [truncated: context budget]\n")
            truncated_files += 1
            break
        chunks.append(block)
        total += len(block)

    if truncated_files:
        chunks.append(
            f"\n… {truncated_files} file(s) omitted or truncated (context budget).\n"
        )

    return header + "".join(chunks)
