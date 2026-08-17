import type { SseEvent } from "./types";

export interface SseCallbacks {
  onEvent: (event: SseEvent) => void;
  onDone?: () => void;
  onClose?: () => void;
  signal?: AbortSignal;
}

/**
 * POST a body and consume the response as Server-Sent Events over fetch.
 * The backend (FastAPI StreamingResponse) emits `event:` / `data:` frames.
 */
export async function streamAnalysis(
  url: string,
  body: unknown,
  { onEvent, onClose, signal }: SseCallbacks,
): Promise<void> {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    signal,
  });

  if (!res.ok || !res.body) {
    const detail = await res.text().catch(() => "");
    throw new Error(`HTTP ${res.status}: ${detail || res.statusText}`);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let eventType = "";
  let dataLines: string[] = [];

  const flush = () => {
    if (eventType) {
      const payload = dataLines.join("\n");
      let data: unknown = null;
      try {
        data = payload ? JSON.parse(payload) : {};
      } catch {
        data = { raw: payload };
      }
      const ev = { type: eventType, ...(data as object) } as SseEvent;
      onEvent(ev);
    }
    eventType = "";
    dataLines = [];
  };

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });

      let idx: number;
      while ((idx = buffer.indexOf("\n\n")) !== -1) {
        const frame = buffer.slice(0, idx);
        buffer = buffer.slice(idx + 2);
        for (const line of frame.split("\n")) {
          if (line.startsWith("event:")) {
            eventType = line.slice(6).trim();
          } else if (line.startsWith("data:")) {
            dataLines.push(line.slice(5).trim());
          }
        }
        flush();
      }
    }
    // final frame without trailing blank line
    if (eventType || dataLines.length) flush();
  } finally {
    onClose?.();
  }
}
