/**
 * Mirrors backend `goforge.schemas` — keep in sync when the API changes.
 */
export type ApiRunStatus = "queued" | "running" | "completed" | "failed";

export type ApiStepStatus = "pending" | "running" | "done" | "failed";

export type ApiStepName =
  | "Planner"
  | "Context Retrieval"
  | "Code Generation"
  | "Test Generation"
  | "Validation"
  | "PR Creation";

/** Step row from the API snapshot. */
export type ApiStepState = { name: ApiStepName; status: ApiStepStatus };

export type RunSnapshot = {
  run_id: string;
  task: string;
  status: ApiRunStatus;
  repo_root: string;
  steps: ApiStepState[];
  logs: string[];
  diff: string | null;
  pr_url: string | null;
  error: string | null;
};

export type RunCreateResponse = {
  run_id: string;
};

/** Badge variant names aligned with `RunStatusBadge` (live workflow). */
export type UiRunBadgeStatus = "queued" | "running" | "complete" | "failed";

export function apiRunStatusToBadgeStatus(s: ApiRunStatus): UiRunBadgeStatus {
  switch (s) {
    case "queued":
      return "queued";
    case "running":
      return "running";
    case "completed":
      return "complete";
    case "failed":
      return "failed";
  }
}

export type UiStepDotStatus = "idle" | "running" | "done" | "failed";

export function apiStepStatusToDotStatus(s: ApiStepStatus): UiStepDotStatus {
  switch (s) {
    case "pending":
      return "idle";
    case "running":
      return "running";
    case "done":
      return "done";
    case "failed":
      return "failed";
  }
}
