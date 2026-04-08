import { GitBranch } from "lucide-react";

import { cn } from "@/lib/utils";

type LogoProps = {
  className?: string;
  iconClassName?: string;
};

export function Logo({ className, iconClassName }: LogoProps) {
  return (
    <div className={cn("flex items-center gap-2", className)}>
      <span
        className={cn(
          "flex size-9 items-center justify-center rounded-lg bg-gradient-to-br from-indigo-500/25 to-cyan-500/20 ring-1 ring-white/10 shadow-[0_0_24px_-4px_rgb(99_102_241_/_0.45)]",
          iconClassName
        )}
      >
        <GitBranch className="size-4 text-indigo-200" aria-hidden />
      </span>
      <span className="text-lg font-semibold tracking-tight text-white">
        PatchFlow
      </span>
    </div>
  );
}
