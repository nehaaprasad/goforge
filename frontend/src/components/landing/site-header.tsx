"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";

import { Logo } from "./logo";

const nav = [
  { href: "#demo", label: "Product" },
  { href: "#how", label: "How it Works" },
  { href: "#features", label: "Features" },
  { href: "#demo", label: "Demo" },
  { href: "#faq", label: "FAQ" },
] as const;

export function SiteHeader() {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 12);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <header
      className={cn(
        "sticky top-0 z-50 border-b border-transparent transition-colors duration-300",
        scrolled &&
          "border-white/[0.06] bg-[#0B0F19]/80 backdrop-blur-xl supports-[backdrop-filter]:bg-[#0B0F19]/65"
      )}
    >
      <div className="mx-auto flex w-full max-w-6xl items-center justify-between gap-4 px-4 py-4 sm:px-6">
        <Link href="#hero" className="shrink-0 rounded-md outline-offset-4">
          <Logo />
        </Link>

        <nav
          aria-label="Primary"
          className="hidden items-center gap-1 md:flex lg:gap-2"
        >
          {nav.map((item) => (
            <Link
              key={item.label}
              href={item.href}
              className="rounded-md px-2.5 py-2 text-sm text-zinc-400 transition-colors hover:text-white"
            >
              {item.label}
            </Link>
          ))}
        </nav>

        <div className="flex shrink-0 items-center gap-2">
          <Link
            href="#demo"
            className={cn(
              buttonVariants({ variant: "outline", size: "sm" }),
              "hidden border-white/10 bg-white/[0.03] text-zinc-200 hover:bg-white/[0.06] sm:inline-flex"
            )}
          >
            View Workflow
          </Link>
          <Link
            href="#demo"
            className={cn(
              buttonVariants({ size: "sm" }),
              "h-8 bg-gradient-to-r from-indigo-500 to-violet-600 px-3 text-xs font-medium text-white shadow-lg shadow-indigo-500/20 hover:from-indigo-400 hover:to-violet-500"
            )}
          >
            Try Demo
          </Link>
        </div>
      </div>
    </header>
  );
}
