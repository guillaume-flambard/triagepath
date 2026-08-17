import type { AnalysisRequest, ReviewRequest, ReviewResponse, SseEvent } from "./types";
import { streamAnalysis } from "./sse";

const API_BASE = "/api";

export function startAnalysis(
  req: AnalysisRequest,
  callbacks: {
    onEvent: (e: SseEvent) => void;
    onClose?: () => void;
    signal?: AbortSignal;
  },
): Promise<void> {
  return streamAnalysis(`${API_BASE}/analyze/stream`, req, {
    onEvent: callbacks.onEvent,
    onClose: callbacks.onClose,
    signal: callbacks.signal,
  });
}

export async function submitReview(req: ReviewRequest): Promise<ReviewResponse> {
  const res = await fetch(`${API_BASE}/review`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
  if (!res.ok) {
    const detail = await res.text().catch(() => "");
    throw new Error(`HTTP ${res.status}: ${detail || res.statusText}`);
  }
  return res.json();
}
