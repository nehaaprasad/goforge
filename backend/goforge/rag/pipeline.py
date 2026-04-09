"""
RAG: chunk repo .go files, embed, retrieve top-k by cosine similarity vs query.

Falls back to empty section when no API key or on error (caller keeps file bundle).
"""

from __future__ import annotations

from pathlib import Path

from goforge.config import settings
from goforge.rag.chunk import TextChunk, chunk_go_file
from goforge.rag.embed import embed_query, embed_texts
from goforge.rag.similarity import cosine_similarity
from goforge.repo.scan import list_go_source_paths
from goforge.schemas import PlannerOutput


def _candidate_paths(repo_root: str, plan: PlannerOutput) -> list[str]:
    root = Path(repo_root).resolve()
    seen: set[str] = set()
    out: list[str] = []
    for rel in plan.files:
        rel = rel.strip().replace("\\", "/")
        if rel and rel not in seen:
            seen.add(rel)
            out.append(rel)
    if not out:
        out = list_go_source_paths(str(root), limit=20)
    return out


def _collect_chunks(repo_root: str, paths: list[str], max_chars: int, max_chunks: int) -> list[TextChunk]:
    root = Path(repo_root).resolve()
    all_chunks: list[TextChunk] = []
    for rel in paths:
        if len(all_chunks) >= max_chunks:
            break
        path = root / rel
        if not path.is_file():
            continue
        raw = path.read_bytes()
        if len(raw) > 512_000:
            raw = raw[:512_000]
        text = raw.decode("utf-8", errors="replace")
        for c in chunk_go_file(rel, text, max_chars=max_chars):
            all_chunks.append(c)
            if len(all_chunks) >= max_chunks:
                break
    return all_chunks


def _format_rag_section(chunks: list[TextChunk], scores: list[float]) -> str:
    lines: list[str] = [
        "=== RAG: top relevant code chunks (embedding similarity) ===",
        "",
    ]
    for rank, (ch, score) in enumerate(zip(chunks, scores, strict=True), start=1):
        header = f"--- [{rank}] {ch.path}:{ch.start_line}-{ch.end_line} (score≈{score:.4f}) ---"
        lines.append(header)
        lines.append(ch.text.rstrip())
        lines.append("")
    return "\n".join(lines)


async def build_rag_context_section(
    repo_root: str,
    plan: PlannerOutput,
    task: str,
) -> tuple[str, str]:
    """
    Returns (context_prefix, status).

    status:
      - "rag" — section contains top-k chunks
      - "skipped_no_key"
      - "skipped_disabled"
      - "skipped_no_chunks"
      - "error: ..." — embedding/HTTP failure (empty section)
    """
    if not settings.rag_enabled:
        return "", "skipped_disabled"

    if not settings.openai_api_key or not str(settings.openai_api_key).strip():
        return "", "skipped_no_key"

    paths = _candidate_paths(repo_root, plan)
    chunks = _collect_chunks(
        repo_root,
        paths,
        max_chars=settings.rag_chunk_chars,
        max_chunks=settings.rag_max_chunks_embed,
    )
    if not chunks:
        return "", "skipped_no_chunks"

    texts = [c.text for c in chunks]

    try:
        chunk_embs = await embed_texts(texts)
        query_text = (
            f"{task.strip()}\n\nPlanner tasks:\n"
            + "\n".join(f"- {t}" for t in plan.tasks[:12])
            + "\n\nPlanner files:\n"
            + "\n".join(f"- {f}" for f in plan.files[:24])
        )
        q_emb = await embed_query(query_text[:12_000])
    except Exception as exc:
        return "", f"error: {exc}"

    scores = [cosine_similarity(q_emb, e) for e in chunk_embs]
    ranked = sorted(
        range(len(chunks)),
        key=lambda i: scores[i],
        reverse=True,
    )
    k = min(settings.rag_top_k, len(ranked))
    top_idx = ranked[:k]
    top_chunks = [chunks[i] for i in top_idx]
    top_scores = [scores[i] for i in top_idx]

    return _format_rag_section(top_chunks, top_scores), "rag"
