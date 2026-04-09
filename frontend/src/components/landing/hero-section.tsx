import Link from "next/link";

import { buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";

import { ProductWorkbench } from "./product-workbench";

export function HeroSection() {
  return (
    <section
      id="hero"
      className="mx-auto w-full max-w-6xl px-4 pb-20 pt-10 sm:px-6 sm:pb-28 sm:pt-14"
    >
      <div className="grid items-center gap-12 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.05fr)] lg:gap-10 xl:gap-14">
        <div className="max-w-xl animate-fade-up">
          <p className="mb-4 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.04] px-3 py-1 text-xs font-medium text-indigo-200/90 shadow-[0_0_40px_-12px_rgb(99_102_241_/_0.5)]">
            <span className="size-1.5 rounded-full bg-emerald-400 shadow-[0_0_8px_rgb(52_211_153_/_0.8)]" />
            Go monorepos · validation-first
          </p>
          <h1 className="text-balance text-4xl font-semibold tracking-tight text-white sm:text-5xl lg:text-[2.75rem] lg:leading-[1.1]">
            Turn engineering tickets into validated pull requests.
          </h1>
          <p className="mt-5 max-w-lg text-pretty text-base leading-relaxed text-zinc-400 sm:text-lg">
            PatchFlow uses multi-agent orchestration to plan, code, test, validate,
            and prepare PRs for Go monorepos—so your team ships with confidence.
          </p>
          <div className="mt-8 flex flex-wrap items-center gap-3">
            <Link
              href="/workflow"
              className={cn(
                buttonVariants({ size: "lg" }),
                "h-10 bg-gradient-to-r from-indigo-500 via-violet-500 to-cyan-500 px-6 text-sm font-semibold text-white shadow-xl shadow-indigo-500/25 hover:from-indigo-400 hover:via-violet-400 hover:to-cyan-400"
              )}
            >
              Start Free Demo
            </Link>
            <Link
              href="#how"
              className={cn(
                buttonVariants({ variant: "outline", size: "lg" }),
                "h-10 border-white/15 bg-white/[0.04] px-6 text-sm font-medium text-zinc-100 hover:bg-white/[0.08]"
              )}
            >
              See How It Works
            </Link>
          </div>
        </div>

        <div className="relative mx-auto w-full max-w-xl lg:mx-0 lg:max-w-none">
          <div
            aria-hidden
            className="pointer-events-none absolute -inset-4 rounded-3xl bg-gradient-to-br from-indigo-500/20 via-transparent to-cyan-500/15 opacity-80 blur-2xl"
          />
          <div className="relative transition-transform duration-500 hover:scale-[1.01]">
            <ProductWorkbench variant="hero" className="w-full" />
          </div>
        </div>
      </div>
    </section>
  );
}
