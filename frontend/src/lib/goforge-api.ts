import type { RunCreateResponse, RunSnapshot } from "@/types/run";

async function readHttpError(res: Response): Promise<string> {
  try {
    const body = (await res.json()) as { detail?: unknown };
    const d = body.detail;
    if (typeof d === "string") {
      return d;
    }
    if (Array.isArray(d)) {
      return d
        .map((x) =>
          typeof x === "object" && x !== null && "msg" in x
            ? String((x as { msg: string }).msg)
            : String(x)
        )
        .join(" ");
    }
  } catch {
    /* ignore */
  }
  return res.statusText || `HTTP ${res.status}`;
}

export async function createRun(
  apiBase: string,
  task: string,
  options?: { repoUrl?: string | null }
): Promise<RunCreateResponse> {
  const base = apiBase.replace(/\/$/, "");
  const repo_url = (options?.repoUrl ?? "").trim();
  const body: { task: string; repo_url?: string } = { task };
  if (repo_url) {
    body.repo_url = repo_url;
  }
  const res = await fetch(`${base}/api/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    throw new Error(await readHttpError(res));
  }
  return res.json() as Promise<RunCreateResponse>;
}

export async function fetchRunSnapshot(
  apiBase: string,
  runId: string
): Promise<RunSnapshot> {
  const base = apiBase.replace(/\/$/, "");
  const res = await fetch(`${base}/api/run/${encodeURIComponent(runId)}`);
  if (!res.ok) {
    throw new Error(await readHttpError(res));
  }
  return res.json() as Promise<RunSnapshot>;
}
