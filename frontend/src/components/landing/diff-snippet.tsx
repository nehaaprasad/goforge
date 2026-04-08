import { cn } from "@/lib/utils";

type Line = { line: string; type: "context" | "remove" | "add" };

const lines: Line[] = [
  { line: "package auth", type: "context" },
  { line: "", type: "context" },
  { line: "func NewLimiter() *Limiter {", type: "context" },
  { line: "  return &Limiter{", type: "remove" },
  { line: "    max: 100,", type: "remove" },
  { line: "  return &Limiter{", type: "add" },
  { line: "    max: 60,", type: "add" },
  { line: "    window: time.Minute,", type: "add" },
  { line: "  }", type: "context" },
  { line: "}", type: "context" },
];

function lineClass(t: Line["type"]) {
  switch (t) {
    case "remove":
      return "bg-red-500/15 text-red-200/95";
    case "add":
      return "bg-emerald-500/20 text-emerald-200/95";
    default:
      return "text-zinc-500/90";
  }
}

function prefix(t: Line["type"]) {
  switch (t) {
    case "remove":
      return "−";
    case "add":
      return "+";
    default:
      return " ";
  }
}

type DiffSnippetProps = {
  className?: string;
  fileName?: string;
  compact?: boolean;
};

export function DiffSnippet({
  className,
  fileName = "internal/auth/rate_limit.go",
  compact = false,
}: DiffSnippetProps) {
  const visible = compact ? lines.slice(0, 5) : lines;

  return (
    <div
      className={cn(
        "overflow-hidden rounded-lg border border-white/[0.08] bg-[#070a12]/90 font-mono text-[11px] leading-relaxed shadow-inner sm:text-xs",
        className
      )}
    >
      <div className="flex items-center justify-between border-b border-white/[0.06] bg-white/[0.03] px-3 py-2">
        <span className="truncate text-[0.7rem] text-zinc-400">{fileName}</span>
        <span className="shrink-0 text-[0.65rem] font-medium uppercase tracking-wide text-emerald-400/90">
          modified
        </span>
      </div>
      <div className="max-h-[min(280px,42vh)] overflow-auto px-0 py-2">
        {visible.map((row, i) => (
          <div
            key={`${row.line}-${i}`}
            className={cn(
              "grid grid-cols-[1.5rem_1fr] gap-x-2 px-2 py-px",
              lineClass(row.type)
            )}
          >
            <span className="select-none text-right text-zinc-600/80">
              {i + 12}
            </span>
            <span>
              <span className="inline-block w-3 text-center opacity-70">
                {prefix(row.type)}
              </span>
              <span className="inline text-zinc-200/95">
                {row.line || "\u00a0"}
              </span>
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
