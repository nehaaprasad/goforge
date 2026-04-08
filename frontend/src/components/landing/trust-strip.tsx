const items = [
  "Built for Go teams",
  "Ticket to PR workflow",
  "Validation-first automation",
  "Designed for monorepos",
] as const;

export function TrustStrip() {
  return (
    <section
      aria-label="Trust indicators"
      className="border-y border-white/[0.06] bg-white/[0.02]"
    >
      <div className="mx-auto flex w-full max-w-6xl flex-wrap items-center justify-center gap-x-10 gap-y-3 px-4 py-8 sm:px-6">
        {items.map((text) => (
          <p
            key={text}
            className="text-center text-sm font-medium tracking-tight text-zinc-400"
          >
            {text}
          </p>
        ))}
      </div>
    </section>
  );
}
