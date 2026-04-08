import { cn } from "@/lib/utils";

type PageShellProps = {
  children: React.ReactNode;
  className?: string;
};

export function PageShell({ children, className }: PageShellProps) {
  return (
    <div
      className={cn(
        "relative min-h-screen overflow-x-hidden bg-[#0B0F19] text-zinc-100",
        className
      )}
    >
      <div
        aria-hidden
        className="pointer-events-none fixed inset-0 bg-mesh-glow opacity-90"
      />
      <div
        aria-hidden
        className="pointer-events-none fixed inset-0 opacity-[0.35]"
        style={{
          backgroundImage: `linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px)`,
          backgroundSize: "64px 64px",
        }}
      />
      <div
        aria-hidden
        className="pointer-events-none fixed -left-32 top-1/4 h-96 w-96 rounded-full bg-indigo-600/20 blur-[100px]"
      />
      <div
        aria-hidden
        className="pointer-events-none fixed -right-24 bottom-1/4 h-80 w-80 rounded-full bg-cyan-500/15 blur-[90px]"
      />
      <div className="relative z-10">{children}</div>
    </div>
  );
}
