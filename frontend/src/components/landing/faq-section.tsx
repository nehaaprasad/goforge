"use client";

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";

const faqs = [
  {
    q: "Does GoForage replace developers?",
    a: "No. It automates the repetitive path from ticket to validated diff and PR. Engineers stay in control of architecture, review, and merge—GoForage reduces toil, not judgment.",
  },
  {
    q: "Does it support large Go monorepos?",
    a: "Yes—that’s the focus. The workflow is built around scoped changes, package-aware context, and the same build and test commands you already run—so growth doesn’t mean guesswork.",
  },
  {
    q: "How safe is the code generation?",
    a: "Nothing ships without passing your Go checks. Diffs are reviewable, tests are part of the loop, and pull requests are only created after validation succeeds—so safety is enforced, not promised.",
  },
  {
    q: "Can it be extended to other languages?",
    a: "The orchestration model is general, but GoForage is optimized for Go first—modules, tests, and tooling match what teams already trust. Other languages may come later as separate tracks.",
  },
] as const;

export function FaqSection() {
  return (
    <section id="faq" className="mx-auto w-full max-w-6xl scroll-mt-24 px-4 py-20 sm:px-6">
      <div className="mx-auto max-w-2xl text-center">
        <h2 className="text-3xl font-semibold tracking-tight text-white sm:text-4xl">
          Frequently asked questions
        </h2>
        <p className="mt-3 text-pretty text-zinc-400">
          Straight answers about how GoForage fits into real engineering teams.
        </p>
      </div>

      <Accordion className="mx-auto mt-10 w-full max-w-3xl rounded-xl border border-white/10 bg-[#0d1219]/60 px-2 shadow-[0_0_0_1px_rgb(255_255_255_/_0.04)_inset]">
        {faqs.map((item, i) => (
          <AccordionItem
            key={item.q}
            value={`faq-${i}`}
            className="border-white/10 px-3 last:border-b-0"
          >
            <AccordionTrigger className="py-4 text-left text-base text-white hover:no-underline">
              {item.q}
            </AccordionTrigger>
            <AccordionContent className="pb-4 text-zinc-400">
              {item.a}
            </AccordionContent>
          </AccordionItem>
        ))}
      </Accordion>
    </section>
  );
}
