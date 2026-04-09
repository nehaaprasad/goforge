"use client";

import {
  Activity,
  ArrowLeft,
  CheckCircle2,
  ChevronRight,
  GitPullRequest,
  ListChecks,
  Loader2,
  Play,
  Terminal,
  XCircle,
} from "lucide-react";
import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";

import { Button } from "@/components/ui/button";
import { RunStatusBadge } from "@/components/landing/run-status-badge";
import { useRunSse } from "@/hooks/use-run-sse";
import { getPublicApiBaseUrl } from "@/lib/api-base";
import { createRun } from "@/lib/goforge-api";
import { parseUnifiedDiffByFile } from "@/lib/parse-unified-diff";
import { cn } from "@/lib/utils";
import {
  type ApiRunStatus,
  type ApiStepState,
  apiRunStatusToBadgeStatus,
  apiStepStatusToDotStatus,
} from "@/types/run";

import { UnifiedDiffView } from "./unified-diff-view";

function basenamePath(p: string): string {
  const norm = p.replace(/\\/g, "/");
  const parts = norm.split("/").filter(Boolean);
  return parts[parts.length - 1] ?? p;
}

/** Backend caches remote clones under a .../clones/<id>/ directory. */
function isRemoteClonePath(p: string): boolean {
  return /[/\\]clones[/\\]/.test(p);
}

function stepDotClass(
  state: "idle" | "running" | "done" | "failed"
): string {
  switch (state) {
    case "done":
      return "bg-emerald-400/90 shadow-[0_0_10px_rgb(52_211_153_/_0.45)]";
    case "running":
      return "animate-pulse bg-indigo-400 shadow-[0_0_12px_rgb(129_140_248_/_0.55)]";
    case "failed":
      return "bg-red-400";
    default:
      return "bg-zinc-600";
  }
}

function validationCaption(
  steps: ApiStepState[] | undefined,
  runStatus: ApiRunStatus | undefined
): { tone: "muted" | "ok" | "bad" | "run"; text: string } {
  const v = steps?.find((s) => s.name === "Validation");
  if (!v) {
    return { tone: "muted", text: "Validation: waiting…" };
  }
  if (v.status === "running") {
    return {
      tone: "run",
      text: "Validation: running go build ./... and go test ./...",
    };
  }
  if (v.status === "failed") {
    return {
      tone: "bad",
      text: "Validation: failed — see banner above and logs →",
    };
  }
  if (v.status === "done" && runStatus === "completed") {
    return {
      tone: "ok",
      text: "Validation: go build ./... and go test ./... passed.",
    };
  }
  if (v.status === "done") {
    return { tone: "ok", text: "Validation: checks finished." };
  }
  return { tone: "muted", text: "Validation: pending…" };
}

export function LiveWorkbench() {
  const apiBase = getPublicApiBaseUrl();
  const [task, setTask] = useState(
    "Add structured logging to the HTTP middleware"
  );
  /** Optional public https:// git URL; empty = GOFORGE_REPO_ROOT / sandbox-repo. */
  const [repoUrl, setRepoUrl] = useState("");
  const [runId, setRunId] = useState<string | null>(null);
  const [postError, setPostError] = useState<string | null>(null);
  const [isStarting, setIsStarting] = useState(false);
  const [fileIdx, setFileIdx] = useState(0);

  const { snapshot, streamError } = useRunSse({
    apiBase,
    runId,
  });

  const diffChunks = useMemo(
    () => parseUnifiedDiffByFile(snapshot?.diff ?? ""),
    [snapshot?.diff]
  );

  useEffect(() => {
    setFileIdx(0);
  }, [snapshot?.run_id, snapshot?.diff]);

  const startRun = useCallback(async () => {
    const trimmed = task.trim();
    if (!trimmed) {
      return;
    }
    setPostError(null);
    setIsStarting(true);
    setRunId(null);
    try {
      const { run_id } = await createRun(apiBase, trimmed, {
        repoUrl: repoUrl.trim() || null,
      });
      setRunId(run_id);
    } catch (e) {
      setPostError(e instanceof Error ? e.message : "Failed to start run");
    } finally {
      setIsStarting(false);
    }
  }, [apiBase, task, repoUrl]);

  const combinedError = postError ?? streamError;
  const repoLabel = snapshot ? basenamePath(snapshot.repo_root) : "sandbox-repo";
  const repoSource =
    snapshot && isRemoteClonePath(snapshot.repo_root)
      ? "remote clone"
      : "local";
  const val = validationCaption(snapshot?.steps, snapshot?.status);

  const activeChunk = diffChunks[fileIdx] ?? diffChunks[0];

  const codeNotes = snapshot?.code_notes ?? [];
  const testPaths = snapshot?.test_paths ?? [];
  const coverageFocus = snapshot?.coverage_focus ?? [];
  const hasStructuredOutput =
    codeNotes.length > 0 ||
    testPaths.length > 0 ||
    coverageFocus.length > 0;

  return (
    <div className="mx-auto w-full max-w-6xl px-4 pb-16 pt-6 sm:px-6">
      <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <Link
            href="/"
            className="inline-flex items-center gap-1.5 text-sm text-zinc-400 transition-colors hover:text-white"
          >
            <ArrowLeft className="size-4" aria-hidden />
            Home
          </Link>
          <span className="text-zinc-600">/</span>
          <h1 className="text-lg font-semibold tracking-tight text-white">
            GoForage · Run
          </h1>
        </div>
        <p className="max-w-md text-xs text-zinc-500">
          Live view of the GoForage API (
          <span className="font-mono text-zinc-400">{apiBase}</span>). Start the
          backend with{" "}
          <code className="rounded bg-white/[0.06] px-1 py-0.5 text-[0.65rem]">
            uvicorn goforge.main:app
          </code>
          .
        </p>
      </div>

      <div
        className={cn(
          "flex max-h-[min(920px,calc(100vh-5rem))] flex-col overflow-hidden rounded-xl border border-white/[0.08] bg-[#0d1219]/95 shadow-[0_24px_80px_-24px_rgb(0_0_0_/_0.75),0_0_0_1px_rgb(255_255_255_/_0.04)_inset]"
        )}
      >
        <header className="flex shrink-0 flex-wrap items-center gap-2 border-b border-white/[0.06] bg-[#0a0e14]/95 px-3 py-3 backdrop-blur-sm supports-[backdrop-filter]:bg-[#0a0e14]/90 sm:px-4">
          <div className="flex min-w-0 flex-1 flex-col gap-2 sm:flex-row sm:items-center">
            <div className="flex min-w-0 flex-1 items-center gap-2 text-[0.7rem] text-zinc-400 sm:text-xs">
              <span className="truncate rounded-md bg-white/[0.06] px-2 py-1 font-mono text-zinc-300">
                {repoLabel}
              </span>
              <ChevronRight className="size-4 shrink-0 text-zinc-600" aria-hidden />
              <span className="truncate text-zinc-500">{repoSource}</span>
            </div>
            <label className="sr-only" htmlFor="goforage-task">
              Task
            </label>
            <input
              id="goforage-task"
              type="text"
              value={task}
              onChange={(e) => setTask(e.target.value)}
              placeholder="Describe the change…"
              className="w-full min-w-0 rounded-md border border-white/10 bg-black/30 px-3 py-2 text-sm text-zinc-100 outline-none ring-indigo-500/40 placeholder:text-zinc-600 focus:border-indigo-500/50 focus:ring-2 sm:max-w-xl"
            />
            <label className="sr-only" htmlFor="goforage-repo-url">
              Repository URL optional
            </label>
            <input
              id="goforage-repo-url"
              type="url"
              inputMode="url"
              autoComplete="off"
              value={repoUrl}
              onChange={(e) => setRepoUrl(e.target.value)}
              placeholder="Optional: https://github.com/org/repo (public HTTPS clone)"
              className="w-full min-w-0 rounded-md border border-white/10 bg-black/20 px-3 py-1.5 text-xs text-zinc-300 outline-none ring-indigo-500/40 placeholder:text-zinc-600 focus:border-indigo-500/50 focus:ring-2 sm:max-w-xl"
            />
          </div>
          <div className="flex items-center gap-2">
            {snapshot ? (
              <RunStatusBadge status={apiRunStatusToBadgeStatus(snapshot.status)} />
            ) : (
              <RunStatusBadge status="idle" />
            )}
            <Button
              size="sm"
              disabled={
                !task.trim() ||
                isStarting ||
                snapshot?.status === "queued" ||
                snapshot?.status === "running"
              }
              onClick={() => void startRun()}
              className="h-8 gap-1.5 rounded-md bg-gradient-to-r from-indigo-500 to-violet-600 px-3 text-xs font-medium text-white shadow-lg shadow-indigo-500/25 hover:from-indigo-400 hover:to-violet-500 disabled:opacity-50"
            >
              <Play className="size-3 fill-current" aria-hidden />
              {isStarting ? "Starting…" : "Run"}
            </Button>
          </div>
        </header>

        {combinedError ? (
          <div
            role="alert"
            className="shrink-0 border-b border-red-500/20 bg-red-500/10 px-4 py-2 text-sm text-red-200"
          >
            {combinedError}
          </div>
        ) : null}

        {snapshot?.error ? (
          <div
            role="status"
            className="shrink-0 border-b border-amber-500/20 bg-amber-500/10 px-4 py-2 text-sm text-amber-100"
          >
            {snapshot.error}
          </div>
        ) : null}

        <div className="flex min-h-0 flex-1 flex-col overflow-hidden lg:flex-row">
          <aside className="max-h-[40vh] shrink-0 overflow-y-auto border-white/[0.06] bg-[#080c14]/80 px-3 py-3 lg:max-h-none lg:w-52 lg:shrink-0 lg:border-r">
            <p className="mb-2 flex items-center gap-1.5 text-[0.65rem] font-medium uppercase tracking-wider text-zinc-500">
              <Activity className="size-3" aria-hidden />
              Workflow
            </p>
            <ul className="space-y-1">
              {(snapshot?.steps ?? []).map((s) => {
                const ui = apiStepStatusToDotStatus(s.status);
                return (
                  <li key={s.name}>
                    <div
                      className={cn(
                        "flex items-center gap-2 rounded-lg px-2 py-1.5 text-[0.65rem] sm:text-xs",
                        ui === "running" &&
                          "bg-indigo-500/10 ring-1 ring-indigo-500/25"
                      )}
                    >
                      <span
                        className={cn(
                          "size-1.5 shrink-0 rounded-full",
                          stepDotClass(ui)
                        )}
                      />
                      <span
                        className={cn(
                          "flex-1 font-medium",
                          ui === "running" ? "text-indigo-100" : "text-zinc-300"
                        )}
                      >
                        {s.name}
                      </span>
                    </div>
                  </li>
                );
              })}
            </ul>
          </aside>

          <div className="flex min-h-0 min-w-0 flex-1 flex-col overflow-hidden border-white/[0.06] bg-[#06080d]/90 lg:border-r">
            <div className="shrink-0 border-b border-white/[0.06] px-3 py-2">
              <p className="mb-1.5 text-[0.65rem] font-medium uppercase tracking-wider text-zinc-500">
                Diff
              </p>
              <div
                className={cn(
                  "flex items-start gap-2 rounded-lg border px-2.5 py-2 text-[0.7rem] leading-snug sm:text-xs",
                  val.tone === "ok" &&
                    "border-emerald-500/25 bg-emerald-500/10 text-emerald-100/95",
                  val.tone === "bad" &&
                    "border-red-500/25 bg-red-500/10 text-red-100/95",
                  val.tone === "run" &&
                    "border-indigo-500/25 bg-indigo-500/10 text-indigo-100/95",
                  val.tone === "muted" &&
                    "border-white/[0.06] bg-white/[0.03] text-zinc-400"
                )}
              >
                {val.tone === "ok" ? (
                  <CheckCircle2 className="mt-0.5 size-4 shrink-0 text-emerald-400/90" aria-hidden />
                ) : null}
                {val.tone === "bad" ? (
                  <XCircle className="mt-0.5 size-4 shrink-0 text-red-400/90" aria-hidden />
                ) : null}
                {val.tone === "run" ? (
                  <Loader2
                    className="mt-0.5 size-4 shrink-0 animate-spin text-indigo-400/90"
                    aria-hidden
                  />
                ) : null}
                {val.tone === "muted" ? (
                  <span className="mt-0.5 size-4 shrink-0 rounded-full bg-zinc-600" aria-hidden />
                ) : null}
                <span className="min-w-0 flex-1">{val.text}</span>
              </div>
            </div>

            {snapshot?.diff && diffChunks.length > 0 ? (
              <>
                {diffChunks.length > 1 ? (
                  <div className="shrink-0 border-b border-white/[0.06] px-2 py-2">
                    <div className="flex gap-1 overflow-x-auto pb-1">
                      {diffChunks.map((c, i) => (
                        <button
                          key={`${c.displayPath}-${i}`}
                          type="button"
                          onClick={() => setFileIdx(i)}
                          className={cn(
                            "shrink-0 rounded-md border px-2.5 py-1.5 text-left text-[0.65rem] font-medium transition-colors sm:text-xs",
                            i === fileIdx
                              ? "border-indigo-500/40 bg-indigo-500/15 text-indigo-100"
                              : "border-white/[0.06] bg-black/20 text-zinc-400 hover:border-white/15 hover:text-zinc-200"
                          )}
                        >
                          {basenamePath(c.displayPath)}
                        </button>
                      ))}
                    </div>
                  </div>
                ) : null}
                <div className="min-h-0 flex-1 p-3 pt-2">
                  <UnifiedDiffView
                    text={activeChunk?.raw ?? snapshot.diff}
                    label={activeChunk?.displayPath}
                  />
                </div>
              </>
            ) : (
              <div className="p-3">
                <p className="rounded-lg border border-dashed border-white/10 bg-white/[0.02] px-3 py-8 text-center text-sm text-zinc-500">
                  No diff yet — start a run or wait for the code stage.
                </p>
              </div>
            )}
          </div>

          <div className="flex max-h-[45vh] min-h-0 shrink-0 flex-col border-white/[0.06] bg-[#080c14]/80 lg:max-h-none lg:w-72 lg:shrink-0">
            <div className="min-h-0 flex-1 overflow-y-auto px-3 py-3">
              <p className="mb-2 flex items-center gap-1.5 text-[0.65rem] font-medium uppercase tracking-wider text-zinc-500">
                <Terminal className="size-3" aria-hidden />
                Log
              </p>
              <ul className="space-y-2 pr-1">
                {(snapshot?.logs ?? []).map((line, i) => (
                  <li
                    key={`${i}-${line.slice(0, 24)}`}
                    className="rounded-lg border border-white/[0.05] bg-black/20 px-2 py-1.5 text-[0.65rem] leading-snug text-zinc-300"
                  >
                    {line}
                  </li>
                ))}
              </ul>
              {!snapshot?.logs?.length ? (
                <p className="text-[0.65rem] text-zinc-600">Waiting for output…</p>
              ) : null}
            </div>

            {snapshot ? (
              <div className="max-h-48 shrink-0 overflow-y-auto border-t border-white/[0.06] px-3 py-3">
                <p className="mb-2 flex items-center gap-1.5 text-[0.65rem] font-medium uppercase tracking-wider text-zinc-500">
                  <ListChecks className="size-3" aria-hidden />
                  Agent outputs
                </p>
                {hasStructuredOutput ? (
                  <div className="space-y-3 text-[0.65rem] leading-relaxed">
                    {codeNotes.length > 0 ? (
                      <div>
                        <p className="mb-1 font-medium text-zinc-400">
                          Code notes
                        </p>
                        <ul className="list-disc space-y-1 pl-4 text-zinc-400">
                          {codeNotes.map((n, i) => (
                            <li key={`code-note-${i}`}>{n}</li>
                          ))}
                        </ul>
                      </div>
                    ) : null}
                    {testPaths.length > 0 ? (
                      <div>
                        <p className="mb-1 font-medium text-zinc-400">
                          Test files
                        </p>
                        <ul className="list-disc space-y-1 pl-4 font-mono text-[0.6rem] text-zinc-400">
                          {testPaths.map((p, i) => (
                            <li key={`tp-${i}`}>{p}</li>
                          ))}
                        </ul>
                      </div>
                    ) : null}
                    {coverageFocus.length > 0 ? (
                      <div>
                        <p className="mb-1 font-medium text-zinc-400">
                          Coverage focus
                        </p>
                        <ul className="list-disc space-y-1 pl-4 text-zinc-400">
                          {coverageFocus.map((c, i) => (
                            <li key={`cf-${i}`}>{c}</li>
                          ))}
                        </ul>
                      </div>
                    ) : null}
                  </div>
                ) : (
                  <p className="text-[0.65rem] text-zinc-600">
                    Structured fields from the Code and Test agents appear here
                    (same JSON contract as the PDF spec).
                  </p>
                )}
              </div>
            ) : null}

            <div className="shrink-0 border-t border-white/[0.06] px-3 py-3">
              <p className="mb-2 text-[0.65rem] font-medium uppercase tracking-wider text-zinc-500">
                Pull request
              </p>
              {snapshot?.pr_url ? (
                <a
                  href={snapshot.pr_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 rounded-lg border border-indigo-500/30 bg-indigo-500/10 px-3 py-2 text-[0.7rem] font-medium text-indigo-100 transition-colors hover:border-indigo-400/50 hover:bg-indigo-500/15 sm:text-xs"
                >
                  <GitPullRequest className="size-4 shrink-0" aria-hidden />
                  Open pull request
                </a>
              ) : snapshot?.status === "completed" ? (
                <p className="text-[0.65rem] leading-relaxed text-zinc-500">
                  No PR link — set{" "}
                  <code className="rounded bg-white/[0.06] px-1 py-0.5 font-mono text-[0.6rem] text-zinc-400">
                    GOFORGE_GITHUB_TOKEN
                  </code>{" "}
                  and{" "}
                  <code className="rounded bg-white/[0.06] px-1 py-0.5 font-mono text-[0.6rem] text-zinc-400">
                    GOFORGE_GITHUB_REPO
                  </code>{" "}
                  on the backend to open a PR automatically.
                </p>
              ) : (
                <p className="text-[0.65rem] text-zinc-600">
                  PR URL appears here after a successful run when GitHub is configured.
                </p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
