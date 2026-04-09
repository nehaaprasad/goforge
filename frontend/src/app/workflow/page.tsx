import type { Metadata } from "next";

import { PageShell } from "@/components/landing/page-shell";
import { LiveWorkbench } from "@/components/run/live-workbench";

export const metadata: Metadata = {
  title: "GoForage · Run | GoForge",
  description:
    "Live workflow view connected to the goforge orchestration API.",
};

export default function WorkflowPage() {
  return (
    <PageShell>
      <LiveWorkbench />
    </PageShell>
  );
}
