"""RAG chunking and similarity (no network)."""

from __future__ import annotations

import math
import unittest

from goforge.rag.chunk import chunk_go_file
from goforge.rag.similarity import cosine_similarity


class TestRag(unittest.TestCase):
    def test_cosine_identical(self) -> None:
        a = [1.0, 2.0, 3.0]
        b = [1.0, 2.0, 3.0]
        self.assertAlmostEqual(cosine_similarity(a, b), 1.0, places=5)

    def test_cosine_orthogonal(self) -> None:
        a = [1.0, 0.0]
        b = [0.0, 1.0]
        self.assertAlmostEqual(cosine_similarity(a, b), 0.0, places=5)

    def test_chunk_packs_lines(self) -> None:
        content = "\n".join([f"line {i}" for i in range(50)])
        chunks = chunk_go_file("p.go", content, max_chars=80)
        self.assertTrue(len(chunks) >= 2)
        self.assertTrue(all(len(c.text) <= 120 for c in chunks))

    def test_chunk_oversized_line(self) -> None:
        long_line = "x" * 5000 + "\n"
        chunks = chunk_go_file("p.go", long_line, max_chars=100)
        self.assertTrue(len(chunks) >= 2)
        self.assertTrue(all(len(c.text) <= 100 for c in chunks))


if __name__ == "__main__":
    unittest.main()
