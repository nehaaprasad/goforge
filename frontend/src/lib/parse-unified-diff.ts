/**
 * Split a unified diff string into per-file chunks for tabbed review (PDF layout spec).
 * Handles `diff --git` headers and fallback `--- a/` hunks.
 */

export type DiffFileChunk = {
  /** Repo-relative path for display */
  displayPath: string;
  raw: string;
};

function extractPathFromChunk(chunk: string): string | null {
  const git = chunk.match(/^diff --git a\/(.+?) b\/(.+?)$/m);
  if (git) {
    return (git[2] ?? git[1]).trim();
  }
  const plus = chunk.match(/^\+\+\+ b\/(.+)$/m);
  if (plus) {
    return plus[1].trim().replace(/\t.*$/, "");
  }
  const minus = chunk.match(/^--- a\/(.+)$/m);
  if (minus) {
    return minus[1].trim().replace(/\t.*$/, "");
  }
  return null;
}

export function parseUnifiedDiffByFile(text: string): DiffFileChunk[] {
  const normalized = text.replace(/\r\n/g, "\n").trim();
  if (!normalized) {
    return [];
  }

  if (normalized.includes("\ndiff --git ")) {
    const parts = normalized.split(/\n(?=diff --git )/);
    return parts.map((part) => {
      const raw = part.trim();
      return {
        displayPath: extractPathFromChunk(raw) ?? "file",
        raw,
      };
    });
  }

  if (normalized.startsWith("diff --git ")) {
    return [
      {
        displayPath: extractPathFromChunk(normalized) ?? "patch",
        raw: normalized,
      },
    ];
  }

  if (/^---\s+a\//m.test(normalized)) {
    const parts = normalized.split(/\n(?=---\s+a\/)/);
    return parts.map((part) => {
      const raw = part.trim();
      return {
        displayPath: extractPathFromChunk(raw) ?? "file",
        raw,
      };
    });
  }

  return [{ displayPath: "patch", raw: normalized }];
}
