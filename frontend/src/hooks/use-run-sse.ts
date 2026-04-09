"use client";

import { useEffect, useRef, useState } from "react";

import { fetchRunSnapshot } from "@/lib/goforge-api";
import type { RunSnapshot } from "@/types/run";

type UseRunSseOptions = {
  apiBase: string;
  runId: string | null;
};

type UseRunSseResult = {
  snapshot: RunSnapshot | null;
  streamError: string | null;
  isStreaming: boolean;
};

function isTerminal(status: RunSnapshot["status"]): boolean {
  return status === "completed" || status === "failed";
}

/**
 * Loads the latest snapshot via GET, then subscribes to SSE until the run finishes.
 */
export function useRunSse({ apiBase, runId }: UseRunSseOptions): UseRunSseResult {
  const [snapshot, setSnapshot] = useState<RunSnapshot | null>(null);
  const [streamError, setStreamError] = useState<string | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const snapshotRef = useRef<RunSnapshot | null>(null);

  useEffect(() => {
    snapshotRef.current = snapshot;
  }, [snapshot]);

  useEffect(() => {
    if (!runId) {
      setSnapshot(null);
      setStreamError(null);
      setIsStreaming(false);
      return;
    }

    const base = apiBase.replace(/\/$/, "");
    let es: EventSource | null = null;
    let cancelled = false;

    setStreamError(null);
    setIsStreaming(true);

    void (async () => {
      try {
        const initial = await fetchRunSnapshot(base, runId);
        if (cancelled) {
          return;
        }
        setSnapshot(initial);
        if (isTerminal(initial.status)) {
          setIsStreaming(false);
          return;
        }

        if (cancelled) {
          return;
        }

        const url = `${base}/api/run/${encodeURIComponent(runId)}/stream`;
        es = new EventSource(url);

        if (cancelled) {
          es.close();
          es = null;
          return;
        }

        es.onmessage = (ev) => {
          try {
            const data = JSON.parse(ev.data) as RunSnapshot;
            setSnapshot(data);
            if (isTerminal(data.status)) {
              es?.close();
              es = null;
              setIsStreaming(false);
            }
          } catch {
            setStreamError("Invalid snapshot from stream");
          }
        };

        es.onerror = () => {
          es?.close();
          es = null;
          setIsStreaming(false);
          const last = snapshotRef.current;
          if (!last || !isTerminal(last.status)) {
            setStreamError((prev) => prev ?? "Stream disconnected");
          }
        };
      } catch (e) {
        if (!cancelled) {
          setStreamError(e instanceof Error ? e.message : "Failed to load run");
          setIsStreaming(false);
        }
      }
    })();

    return () => {
      cancelled = true;
      es?.close();
    };
  }, [apiBase, runId]);

  return { snapshot, streamError, isStreaming };
}
