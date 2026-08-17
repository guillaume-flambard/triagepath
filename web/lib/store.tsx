"use client";

import { createContext, useCallback, useContext, useRef, useState, ReactNode } from "react";
import type {
  AnalysisRequest,
  ReviewAction,
  ReviewPayload,
  ReviewResponse,
  SseEvent,
} from "./types";
import { startAnalysis, submitReview } from "./api";

export interface RunState {
  threadId: string | null;
  events: SseEvent[];
  interrupt: ReviewPayload | null;
  interruptNonce: number;
  review: ReviewResponse | null;
  error: string | null;
  running: boolean;
}

interface StoreValue {
  runs: Record<string, RunState>;
  start: (req: AnalysisRequest) => Promise<string>;
  review: (threadId: string, action: ReviewAction, overrides?: { hourly_rate?: number; weeks_per_month?: number }) => Promise<void>;
}

const StoreContext = createContext<StoreValue | null>(null);

function initialState(): RunState {
  return { threadId: null, events: [], interrupt: null, interruptNonce: 0, review: null, error: null, running: true };
}

export function AnalysisStoreProvider({ children }: { children: ReactNode }) {
  const [runs, setRuns] = useState<Record<string, RunState>>({});
  const runsRef = useRef(runs);
  runsRef.current = runs;

  const patch = useCallback((threadId: string, fn: (s: RunState) => RunState) => {
    setRuns((prev) => {
      const cur = prev[threadId] ?? initialState();
      return { ...prev, [threadId]: fn(cur) };
    });
  }, []);

  const start = useCallback(
    async (req: AnalysisRequest): Promise<string> => {
      const threadId = `run-${Date.now()}`;
      setRuns((prev) => ({ ...prev, [threadId]: initialState() }));

      try {
        await startAnalysis(req, {
          onEvent: (e) => {
            patch(threadId, (s) => {
              const next: RunState = {
                ...s,
                events: [...s.events, e],
                running: e.type !== "done" && e.type !== "error",
                error: e.type === "error" ? (e as { message: string }).message : s.error,
              };
              if (e.type === "thread") next.threadId = (e as { thread_id: string }).thread_id;
              if (e.type === "interrupt") {
                next.interrupt = (e as { payload: ReviewPayload }).payload;
                next.interruptNonce += 1;
              }
              return next;
            });
          },
        });
      } catch (err) {
        patch(threadId, (s) => ({ ...s, error: String(err), running: false }));
      }
      return threadId;
    },
    [patch],
  );

  const review = useCallback(
    async (localKey: string, action: ReviewAction, overrides?: { hourly_rate?: number; weeks_per_month?: number }) => {
      const run = runsRef.current[localKey];
      const backendId = run?.threadId ?? localKey;
      patch(localKey, (s) => ({ ...s, running: true }));
      try {
        const res = await submitReview({
          thread_id: backendId,
          action,
          ...overrides,
        });
        const final = res.final ?? {};
        // After an "edit" the graph re-scores and re-pauses at a new human-review
        // interrupt (final.step is "deep_dive", no report yet). Surface that as a
        // fresh review instead of a report.
        const reInterrupt = final.step && final.step !== "report";
        patch(localKey, (s) => ({
          ...s,
          review: reInterrupt ? null : res,
          interrupt: reInterrupt
            ? { scored_tasks: final.scored_tasks as ReviewPayload["scored_tasks"] }
            : s.interrupt,
          interruptNonce: reInterrupt ? s.interruptNonce + 1 : s.interruptNonce,
          running: false,
          error: null,
        }));
      } catch (err) {
        patch(localKey, (s) => ({ ...s, error: String(err), running: false }));
      }
    },
    [patch],
  );

  return (
    <StoreContext.Provider value={{ runs, start, review }}>
      {children}
    </StoreContext.Provider>
  );
}

export function useAnalysisStore(): StoreValue {
  const ctx = useContext(StoreContext);
  if (!ctx) throw new Error("useAnalysisStore must be used within AnalysisStoreProvider");
  return ctx;
}
