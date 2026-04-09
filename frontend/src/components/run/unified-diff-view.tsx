import { cn } from "@/lib/utils";

function lineClass(line: string): string {
  if (line.startsWith("+++") || line.startsWith("---")) {
    return "text-zinc-400";
  }
  if (line.startsWith("@@")) {
    return "bg-white/[0.04] text-zinc-400";
  }
  if (line.startsWith("+")) {
    return "bg-emerald-500/15 text-emerald-100/95";
  }
  if (line.startsWith("-")) {
    return "bg-red-500/12 text-red-200/95";
  }
  return "text-zinc-400/90";
}

type UnifiedDiffViewProps = {
  text: string;
  /** Shown in the header row (e.g. current file path). */
  label?: string;
  className?: string;
};

export function UnifiedDiffView({ text, label, className }: UnifiedDiffViewProps) {
  const lines = text.split("\n");
  return (
    <div
      className={cn(
        "flex min-h-0 flex-1 flex-col overflow-hidden rounded-lg border border-white/[0.08] bg-[#070a12]/90 font-mono text-[11px] leading-relaxed sm:text-xs",
        className
      )}
    >
      <div className="shrink-0 border-b border-white/[0.06] bg-white/[0.03] px-3 py-2 text-[0.65rem] text-zinc-500">
        <span className="text-zinc-500">Unified diff</span>
        {label ? (
          <span className="ml-2 font-medium text-zinc-300">· {label}</span>
        ) : null}
      </div>
      <div className="min-h-0 flex-1 overflow-auto p-2">
        {lines.map((line, i) => (
          <div
            key={`${i}-${line.slice(0, 12)}`}
            className={cn(
              "grid grid-cols-[2rem_1fr] gap-x-2 px-1 py-px",
              lineClass(line)
            )}
          >
            <span className="select-none text-right text-zinc-600">{i + 1}</span>
            <span className="whitespace-pre-wrap break-all text-zinc-200/95">
              {line || "\u00a0"}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
