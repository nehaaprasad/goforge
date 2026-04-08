import { ArrowRight } from "lucide-react";

const stages = [
  "Ticket",
  "Planner",
  "Context retrieval",
  "Code agent",
  "Test agent",
  "Validation",
  "PR",
] as const;

export function ArchitectureSection() {
  return (
    <section
      id="architecture"
      className="mx-auto w-full max-w-6xl px-4 py-20 sm:px-6"
    >
      <div className="mx-auto max-w-2xl text-center">
        <h2 className="text-3xl font-semibold tracking-tight text-white sm:text-4xl">
          Architecture
        </h2>
        <p className="mt-3 text-pretty text-zinc-400">
          A straight-line pipeline with a hard validation gate before anything
          reaches GitHub.
        </p>
      </div>

      <div className="mt-12 overflow-x-auto rounded-xl border border-white/10 bg-[#080c14]/80 p-6 shadow-[0_0_0_1px_rgb(255_255_255_/_0.04)_inset]">
        <ol className="flex min-w-[640px] items-center justify-between gap-2">
          {stages.map((label, i) => (
            <li key={label} className="flex flex-1 items-center gap-2">
              <span className="flex min-w-0 flex-1 items-center justify-center rounded-lg border border-white/10 bg-white/[0.04] px-3 py-2 text-center text-xs font-medium text-zinc-200 sm:text-sm">
                {label}
              </span>
              {i < stages.length - 1 ? (
                <ArrowRight
                  className="size-4 shrink-0 text-zinc-600"
                  aria-hidden
                />
              ) : null}
            </li>
          ))}
        </ol>
      </div>
    </section>
  );
}
