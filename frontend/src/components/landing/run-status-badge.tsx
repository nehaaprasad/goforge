import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";

type RunStatus =
  | "idle"
  | "queued"
  | "running"
  | "done"
  | "complete"
  | "failed";

const styles: Record<
  RunStatus,
  { label: string; className: string }
> = {
  idle: {
    label: "Idle",
    className:
      "border-zinc-600/80 bg-zinc-800/80 text-zinc-300 shadow-none",
  },
  queued: {
    label: "Queued",
    className:
      "border-zinc-600/80 bg-zinc-800/80 text-zinc-300 shadow-none",
  },
  running: {
    label: "Running",
    className:
      "border-indigo-500/40 bg-indigo-500/15 text-indigo-200 shadow-[0_0_20px_-6px_rgb(99_102_241_/_0.6)]",
  },
  done: {
    label: "Done",
    className:
      "border-emerald-500/35 bg-emerald-500/10 text-emerald-200",
  },
  complete: {
    label: "Complete",
    className:
      "border-emerald-500/35 bg-emerald-500/10 text-emerald-200",
  },
  failed: {
    label: "Failed",
    className: "border-red-500/40 bg-red-500/10 text-red-200",
  },
};

type RunStatusBadgeProps = {
  status: RunStatus;
  className?: string;
};

export function RunStatusBadge({ status, className }: RunStatusBadgeProps) {
  const s = styles[status];
  return (
    <Badge
      variant="outline"
      className={cn(
        "rounded-md px-2 py-0.5 text-[0.65rem] font-medium uppercase tracking-wide",
        s.className,
        className
      )}
    >
      {s.label}
    </Badge>
  );
}
