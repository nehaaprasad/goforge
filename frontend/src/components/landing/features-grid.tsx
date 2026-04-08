import { Boxes, FileDiff, GitPullRequest, Layers, Workflow } from "lucide-react";

import { Card, CardContent } from "@/components/ui/card";

const features = [
  {
    title: "Multi-agent orchestration",
    body: "Planner, code, and test agents run in sequence with strict handoffs—no silent overlap.",
    icon: Workflow,
    accentClass:
      "bg-gradient-to-br from-indigo-500/30 to-violet-600/10",
  },
  {
    title: "Go repo understanding",
    body: "Targets modules, packages, and tests so changes stay local and reviewable.",
    icon: Boxes,
    accentClass:
      "bg-gradient-to-br from-violet-500/25 to-fuchsia-600/10",
  },
  {
    title: "Diff-based code generation",
    body: "Outputs unified diffs you can read in review—aligned with how your team already ships.",
    icon: FileDiff,
    accentClass:
      "bg-gradient-to-br from-cyan-500/20 to-indigo-600/10",
  },
  {
    title: "Test creation and validation",
    body: "Adds tests that track behavior, then runs the same checks your CI would.",
    icon: Layers,
    accentClass:
      "bg-gradient-to-br from-emerald-500/15 to-cyan-600/10",
  },
  {
    title: "GitHub PR automation",
    body: "Opens a pull request only after validation passes—publish, don’t guess.",
    icon: GitPullRequest,
    accentClass:
      "bg-gradient-to-br from-indigo-500/20 to-emerald-600/10",
  },
] as const;

export function FeaturesGrid() {
  return (
    <section id="features" className="mx-auto w-full max-w-6xl px-4 py-20 sm:px-6">
      <div className="mx-auto max-w-2xl text-center">
        <h2 className="text-3xl font-semibold tracking-tight text-white sm:text-4xl">
          Everything you need to go from ticket to PR
        </h2>
        <p className="mt-3 text-pretty text-zinc-400">
          Opinionated where safety matters, flexible where your monorepo is unique.
        </p>
      </div>

      <div className="mt-12 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {features.map((f) => (
          <Card
            key={f.title}
            className="group border-white/10 bg-[#0d1219]/70 shadow-[0_0_0_1px_rgb(255_255_255_/_0.04)_inset] transition-all hover:border-indigo-500/25 hover:shadow-[0_0_48px_-24px_rgb(99_102_241_/_0.45)]"
          >
            <CardContent className="relative overflow-hidden pt-6">
              <div
                aria-hidden
                className={`pointer-events-none absolute -right-8 -top-8 h-32 w-32 rounded-full opacity-80 blur-2xl transition-opacity group-hover:opacity-100 ${f.accentClass}`}
              />
              <div className="relative flex flex-col gap-3">
                <span className="flex size-10 items-center justify-center rounded-lg bg-white/[0.06] ring-1 ring-white/10">
                  <f.icon className="size-5 text-indigo-200" aria-hidden />
                </span>
                <h3 className="text-lg font-semibold text-white">{f.title}</h3>
                <p className="text-sm leading-relaxed text-zinc-400">{f.body}</p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </section>
  );
}
