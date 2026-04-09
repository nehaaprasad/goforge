"use client";

import {
  Activity,
  ArrowLeft,
  ChevronRight,
  Play,
  Terminal,
} from "lucide-react";
import Link from "next/link";
import { useCallback, useState } from "react";

import { Button } from "@/components/ui/button";
import { RunStatusBadge } from "@/components/landing/run-status-badge";
import { useRunSse } from "@/hooks/use-run-sse";
import { getPublicApiBaseUrl } from "@/lib/api-base";
import { createRun } from "@/lib/goforge-api";
import { cn } from "@/lib/utils";
import {
  apiRunStatusToBadgeStatus,
  apiStepStatusToDotStatus,
} from "@/types/run";

import { UnifiedDiffView } from "./unified-diff-view";

function basenamePath(p: string): string {
  const norm = p.replace(/\\/g, "/");
  const parts = norm.split("/").filter(Boolean);
  return parts[parts.length - 1] ?? p;
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

export function LiveWorkbench() {
  const apiBase = getPublicApiBaseUrl();
  const [task, setTask] = useState(
    "Add structured logging to the HTTP middleware"
  );
  const [runId, setRunId] = useState<string | null>(null);
  const [postError, setPostError] = useState<string | null>(null);
  const [isStarting, setIsStarting] = useState(false);

  const { snapshot, streamError } = useRunSse({
    apiBase,
    runId,
  });

  const startRun = useCallback(async () => {
    const trimmed = task.trim();
    if (!trimmed) {
      return;
    }
    setPostError(null);
    setIsStarting(true);
    setRunId(null);
    try {
      const { run_id } = await createRun(apiBase, trimmed);
      setRunId(run_id);
    } catch (e) {
      setPostError(e instanceof Error ? e.message : "Failed to start run");
    } finally {
      setIsStarting(false);
    }
  }, [apiBase, task]);

  const combinedError = postError ?? streamError;
  const repoLabel = snapshot ? basenamePath(snapshot.repo_root) : "sandbox-repo";

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
            PatchFlow · Run
          </h1>
        </div>
        <p className="max-w-md text-xs text-zinc-500">
          Live view of the goforge API (
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
          "flex flex-col overflow-hidden rounded-xl border border-white/[0.08] bg-[#0d1219]/95 shadow-[0_24px_80px_-24px_rgb(0_0_0_/_0.75),0_0_0_1px_rgb(255_255_255_/_0.04)_inset]"
        )}
      >
        <header className="flex flex-wrap items-center gap-2 border-b border-white/[0.06] bg-[#0a0e14]/95 px-3 py-3 sm:px-4">
          <div className="flex min-w-0 flex-1 flex-col gap-2 sm:flex-row sm:items-center">
            <div className="flex min-w-0 flex-1 items-center gap-2 text-[0.7rem] text-zinc-400 sm:text-xs">
              <span className="truncate rounded-md bg-white/[0.06] px-2 py-1 font-mono text-zinc-300">
                {repoLabel}
              </span>
              <ChevronRight className="size-4 shrink-0 text-zinc-600" aria-hidden />
              <span className="truncate text-zinc-500">local</span>
            </div>
            <label className="sr-only" htmlFor="patchflow-task">
              Task
            </label>
            <input
              id="patchflow-task"
              type="text"
              value={task}
              onChange={(e) => setTask(e.target.value)}
              placeholder="Describe the change…"
              className="w-full min-w-0 rounded-md border border-white/10 bg-black/30 px-3 py-2 text-sm text-zinc-100 outline-none ring-indigo-500/40 placeholder:text-zinc-600 focus:border-indigo-500/50 focus:ring-2 sm:max-w-xl"
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
            className="border-b border-red-500/20 bg-red-500/10 px-4 py-2 text-sm text-red-200"
          >
            {combinedError}
          </div>
        ) : null}

        {snapshot?.error ? (
          <div
            role="status"
            className="border-b border-amber-500/20 bg-amber-500/10 px-4 py-2 text-sm text-amber-100"
          >
            {snapshot.error}
          </div>
        ) : null}

        <div className="flex min-h-0 flex-1 flex-col gap-0 lg:flex-row">
          <aside className="border-white/[0.06] bg-[#080c14]/80 px-3 py-3 lg:w-52 lg:shrink-0 lg:border-r">
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

          <div className="min-h-0 min-w-0 flex-1 border-white/[0.06] bg-[#06080d]/90 p-3 lg:border-r">
            <p className="mb-2 text-[0.65rem] font-medium uppercase tracking-wider text-zinc-500">
              Diff
            </p>
            {snapshot?.diff ? (
              <UnifiedDiffView text={snapshot.diff} />
            ) : (
              <p className="rounded-lg border border-dashed border-white/10 bg-white/[0.02] px-3 py-8 text-center text-sm text-zinc-500">
                No diff yet — start a run or wait for the code stage.
              </p>
            )}
          </div>

          <div className="border-white/[0.06] bg-[#080c14]/80 px-3 py-3 lg:w-64 lg:shrink-0">
            <p className="mb-2 flex items-center gap-1.5 text-[0.65rem] font-medium uppercase tracking-wider text-zinc-500">
              <Terminal className="size-3" aria-hidden />
              Log
            </p>
            <ul className="max-h-[min(360px,50vh)] space-y-2 overflow-y-auto pr-1">
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
        </div>
      </div>
    </div>
  );
}
