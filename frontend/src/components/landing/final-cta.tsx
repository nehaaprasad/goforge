import Link from "next/link";

import { buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export function FinalCta() {
  return (
    <section className="mx-auto w-full max-w-6xl px-4 pb-24 pt-4 sm:px-6">
      <div className="relative overflow-hidden rounded-2xl border border-indigo-500/20 bg-gradient-to-br from-indigo-500/10 via-[#0d1219] to-cyan-500/10 px-6 py-14 text-center shadow-[0_0_80px_-30px_rgb(99_102_241_/_0.45)] sm:px-12">
        <div
          aria-hidden
          className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_top,_rgb(99_102_241_/_0.2),_transparent_55%)]"
        />
        <div className="relative mx-auto max-w-2xl">
          <h2 className="text-3xl font-semibold tracking-tight text-white sm:text-4xl">
            Ship faster without losing control.
          </h2>
          <p className="mt-3 text-pretty text-zinc-400">
            GoForage keeps your ticket-to-PR path visible, validated, and ready
            for review—starting with your local sandbox repo.
          </p>
          <Link
            href="/workflow"
            className={cn(
              buttonVariants({ size: "lg" }),
              "mt-8 inline-flex h-11 bg-gradient-to-r from-indigo-500 to-violet-600 px-8 text-sm font-semibold text-white shadow-xl shadow-indigo-500/30 hover:from-indigo-400 hover:to-violet-500"
            )}
          >
            Open the demo
          </Link>
        </div>
      </div>
    </section>
  );
}
