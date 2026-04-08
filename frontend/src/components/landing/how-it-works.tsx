import {
  CheckCircle2,
  GitPullRequest,
  LayoutList,
  Sparkles,
} from "lucide-react";

import { Card, CardContent } from "@/components/ui/card";

const steps = [
  {
    title: "Planner Agent",
    description:
      "Breaks your ticket into concrete steps and scopes the smallest set of packages and files to touch.",
    icon: LayoutList,
  },
  {
    title: "Code Agent",
    description:
      "Produces minimal, reviewable diffs grounded in your repo—no drive-by rewrites.",
    icon: Sparkles,
  },
  {
    title: "Test Agent",
    description:
      "Adds or updates tests that match the new behavior and protect regressions.",
    icon: CheckCircle2,
  },
  {
    title: "Validation + PR",
    description:
      "Runs Go builds and tests as the gate; only then opens a branch and pull request.",
    icon: GitPullRequest,
  },
] as const;

export function HowItWorks() {
  return (
    <section id="how" className="mx-auto w-full max-w-6xl px-4 py-20 sm:px-6">
      <div className="mx-auto max-w-2xl text-center">
        <h2 className="text-3xl font-semibold tracking-tight text-white sm:text-4xl">
          How it works
        </h2>
        <p className="mt-3 text-pretty text-zinc-400">
          A single pipeline from ticket to merge-ready PR—each stage visible and
          verifiable.
        </p>
      </div>

      <div className="relative mt-14">
        <div
          aria-hidden
          className="absolute left-0 right-0 top-10 hidden h-px bg-gradient-to-r from-transparent via-indigo-500/40 to-transparent lg:block"
        />
        <ul className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4 lg:gap-4">
          {steps.map((step, i) => (
            <li key={step.title} className="relative">
              <Card className="h-full border-white/10 bg-[#0d1219]/80 shadow-[0_0_0_1px_rgb(255_255_255_/_0.04)_inset] backdrop-blur-sm transition-shadow hover:shadow-[0_0_40px_-20px_rgb(99_102_241_/_0.35)]">
                <CardContent className="flex flex-col gap-3 pt-6">
                  <div className="flex items-center gap-3">
                    <span className="flex size-10 items-center justify-center rounded-lg bg-gradient-to-br from-indigo-500/20 to-cyan-500/15 ring-1 ring-white/10">
                      <step.icon
                        className="size-5 text-indigo-200"
                        aria-hidden
                      />
                    </span>
                    <span className="text-xs font-medium uppercase tracking-wider text-zinc-500">
                      Step {i + 1}
                    </span>
                  </div>
                  <h3 className="text-base font-semibold text-white">
                    {step.title}
                  </h3>
                  <p className="text-sm leading-relaxed text-zinc-400">
                    {step.description}
                  </p>
                </CardContent>
              </Card>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
