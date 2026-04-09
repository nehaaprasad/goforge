"""Split Go source into bounded text chunks for embedding (RAG)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TextChunk:
    path: str
    text: str
    start_line: int
    end_line: int


def chunk_go_file(path: str, content: str, *, max_chars: int) -> list[TextChunk]:
    """
    Line-oriented chunking: pack lines until max_chars, then flush.
    Prefer not splitting mid-line; each chunk stays contiguous in the file.
    """
    if not content.strip():
        return []

    lines = content.splitlines(keepends=True)
    out: list[TextChunk] = []
    buf: list[str] = []
    buf_len = 0
    start_line = 1
    cur_line = 1

    def flush() -> None:
        nonlocal buf, buf_len, start_line, cur_line
        if not buf:
            return
        text = "".join(buf)
        end_line = start_line + len(buf) - 1
        out.append(TextChunk(path=path, text=text, start_line=start_line, end_line=end_line))
        buf = []
        buf_len = 0
        start_line = cur_line

    for line in lines:
        line_len = len(line)
        if line_len > max_chars:
            flush()
            for start in range(0, len(line), max_chars):
                piece = line[start : start + max_chars]
                ln = cur_line
                out.append(
                    TextChunk(path=path, text=piece, start_line=ln, end_line=ln)
                )
            cur_line += 1
            continue
        if buf and buf_len + line_len > max_chars:
            flush()
            start_line = cur_line
        buf.append(line)
        buf_len += line_len
        cur_line += 1

    flush()
    return out
