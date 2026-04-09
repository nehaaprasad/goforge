import Link from "next/link";

import { Logo } from "./logo";

const links = [
  { href: "#features", label: "Product" },
  { href: "#how", label: "How it Works" },
  { href: "#demo", label: "Demo" },
  { href: "#faq", label: "FAQ" },
] as const;

export function SiteFooter() {
  return (
    <footer className="border-t border-white/[0.06] bg-[#0a0e14]/80">
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-8 px-4 py-12 sm:flex-row sm:items-start sm:justify-between sm:px-6">
        <div>
          <Logo />
          <p className="mt-3 max-w-xs text-sm leading-relaxed text-zinc-500">
            From ticket to validated pull request—multi-agent orchestration for Go
            monorepos.
          </p>
        </div>
        <nav aria-label="Footer" className="flex flex-wrap gap-x-8 gap-y-3">
          {links.map((l) => (
            <Link
              key={l.href}
              href={l.href}
              className="text-sm text-zinc-400 transition-colors hover:text-white"
            >
              {l.label}
            </Link>
          ))}
        </nav>
      </div>
      <div className="border-t border-white/[0.04] py-6 text-center text-xs text-zinc-600">
        © {new Date().getFullYear()} GoForage. All rights reserved.
      </div>
    </footer>
  );
}
