import {
  Activity,
  ChevronRight,
  CircleDot,
  Play,
  Terminal,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

import { DiffSnippet } from "./diff-snippet";
import { RunStatusBadge } from "./run-status-badge";

type StepState = "idle" | "running" | "done" | "failed";

const steps: { id: string; label: string; state: StepState; hint?: string }[] = [
  { id: "planner", label: "Planner", state: "done", hint: "3 files" },
  { id: "context", label: "Context", state: "done", hint: "12 chunks" },
  { id: "code", label: "Code", state: "running", hint: "diff" },
  { id: "test", label: "Tests", state: "idle" },
  { id: "validation", label: "Validation", state: "idle" },
  { id: "pr", label: "PR", state: "idle" },
];

const logLines = [
  { t: "14:02:01", agent: "Planner", text: "Scoped auth/rate_limit.go and middleware." },
  { t: "14:02:04", agent: "Context", text: "Loaded 4 packages, 2 test files." },
  { t: "14:02:09", agent: "Code", text: "Applying minimal diff; preserving public API." },
];

function stepDot(state: StepState) {
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

type ProductWorkbenchProps = {
  variant?: "hero" | "showcase";
  className?: string;
};

export function ProductWorkbench({
  variant = "hero",
  className,
}: ProductWorkbenchProps) {
  const isHero = variant === "hero";

  return (
    <div
      className={cn(
        "flex flex-col overflow-hidden rounded-xl border border-white/[0.08] bg-[#0d1219]/95 shadow-[0_24px_80px_-24px_rgb(0_0_0_/_0.75),0_0_0_1px_rgb(255_255_255_/_0.04)_inset]",
        isHero ? "w-full max-w-4xl" : "w-full max-w-5xl",
        className
      )}
    >
      <header className="flex flex-wrap items-center gap-2 border-b border-white/[0.06] bg-[#0a0e14]/95 px-3 py-2.5 sm:px-4">
        <div className="flex min-w-0 flex-1 items-center gap-2 text-[0.7rem] text-zinc-400 sm:text-xs">
          <span className="truncate rounded-md bg-white/[0.06] px-2 py-1 font-mono text-zinc-300">
            sandbox-repo
          </span>
          <ChevronRight className="size-4 shrink-0 text-zinc-600" aria-hidden />
          <span className="truncate text-zinc-500">main</span>
        </div>
        <div className="flex items-center gap-2">
          <RunStatusBadge status="running" />
          <Button
            size="sm"
            className="h-7 gap-1.5 rounded-md bg-gradient-to-r from-indigo-500 to-violet-600 px-3 text-xs font-medium text-white shadow-lg shadow-indigo-500/25 hover:from-indigo-400 hover:to-violet-500"
          >
            <Play className="size-3 fill-current" aria-hidden />
            Run
          </Button>
        </div>
      </header>

      <div
        className={cn(
          "min-h-0 flex-1 gap-0",
          isHero
            ? "flex flex-col lg:flex-row"
            : "grid grid-cols-1 lg:grid-cols-[220px_1fr_280px]"
        )}
      >
        {/* Workflow */}
        <aside
          className={cn(
            "border-white/[0.06] bg-[#080c14]/80 px-3 py-3 sm:px-3",
            isHero ? "lg:w-52 lg:shrink-0 lg:border-r" : "lg:border-r"
          )}
        >
          <p className="mb-2 flex items-center gap-1.5 text-[0.65rem] font-medium uppercase tracking-wider text-zinc-500">
            <Activity className="size-3" aria-hidden />
            Workflow
          </p>
          <ul className="space-y-1">
            {steps.map((s) => (
              <li key={s.id}>
                <div
                  className={cn(
                    "flex items-center gap-2 rounded-lg px-2 py-1.5 text-[0.65rem] sm:text-xs",
                    s.state === "running" &&
                      "bg-indigo-500/10 ring-1 ring-indigo-500/25",
                    s.state === "done" && "opacity-90"
                  )}
                >
                  <span
                    className={cn(
                      "size-1.5 shrink-0 rounded-full",
                      stepDot(s.state)
                    )}
                  />
                  <span
                    className={cn(
                      "flex-1 font-medium",
                      s.state === "running" ? "text-indigo-100" : "text-zinc-300"
                    )}
                  >
                    {s.label}
                  </span>
                  {s.hint ? (
                    <span className="text-[0.6rem] text-zinc-500">{s.hint}</span>
                  ) : null}
                </div>
              </li>
            ))}
          </ul>
        </aside>

        {/* Diff */}
        <div
          className={cn(
            "min-h-0 min-w-0 flex-1 border-white/[0.06] bg-[#06080d]/90 p-3",
            isHero ? "lg:border-r" : "lg:border-r"
          )}
        >
          <div className="mb-2 flex items-center gap-2 border-b border-white/[0.05] pb-2">
            <div className="flex gap-1">
              <span className="rounded-t-md border border-b-0 border-white/10 bg-white/[0.06] px-2 py-1 text-[0.65rem] text-zinc-200">
                rate_limit.go
              </span>
              <span className="rounded-t-md px-2 py-1 text-[0.65rem] text-zinc-500">
                handler_test.go
              </span>
            </div>
            <span className="ml-auto text-[0.6rem] text-zinc-500">{`go test ./...`}</span>
          </div>
          <DiffSnippet compact={isHero} />
          {!isHero ? (
            <p className="mt-2 text-[0.65rem] text-zinc-500">
              Validation: pending — tests will run after patch application.
            </p>
          ) : null}
        </div>

        {/* Logs — full width row on hero sm layout second column spans; on hero we use 2 cols so logs go below */}
        <div
          className={cn(
            "border-white/[0.06] bg-[#080c14]/80 px-3 py-3",
            isHero ? "lg:w-64 lg:shrink-0 lg:border-l-0" : ""
          )}
        >
          <p className="mb-2 flex items-center gap-1.5 text-[0.65rem] font-medium uppercase tracking-wider text-zinc-500">
            <Terminal className="size-3" aria-hidden />
            Agent log
          </p>
          <ul className="space-y-2">
            {logLines.slice(0, isHero ? 2 : 3).map((l) => (
              <li
                key={`${l.t}-${l.agent}`}
                className="rounded-lg border border-white/[0.05] bg-black/20 px-2 py-1.5"
              >
                <div className="flex flex-wrap items-center gap-2 text-[0.6rem] text-zinc-500">
                  <span className="font-mono">{l.t}</span>
                  <span className="rounded bg-indigo-500/15 px-1.5 py-0.5 text-[0.55rem] font-medium uppercase tracking-wide text-indigo-200">
                    {l.agent}
                  </span>
                </div>
                <p className="mt-1 text-[0.65rem] leading-snug text-zinc-300">
                  {l.text}
                </p>
              </li>
            ))}
          </ul>
          {!isHero ? (
            <div className="mt-3 flex items-center gap-2 rounded-md border border-dashed border-white/10 bg-white/[0.02] px-2 py-2 text-[0.65rem] text-zinc-500">
              <CircleDot className="size-4 shrink-0 text-cyan-400/80" aria-hidden />
              Streaming output from validation will appear here.
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}
