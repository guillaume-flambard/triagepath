export type LlmProvider = "mock" | "ollama" | "groq";

export interface AnalysisRequest {
  name?: string;
  sector?: string;
  free_text?: string;
  preset?: string | null;
  url?: string;
  team_size?: number;
  hourly_rate?: number;
  weeks_per_month?: number;
  llm_provider?: LlmProvider;
  model?: string;
}

export interface ScoredTask {
  rank?: number;
  task?: string | { name?: string; [k: string]: unknown };
  name?: string;
  volume_per_week?: number;
  minutes_per_unit?: number;
  repetitiveness?: number;
  automatability?: number;
  evidence?: string;
  hours_per_month?: number;
  eur_per_month?: number;
  priority_score?: number;
}

export interface ReviewPayload {
  scored_tasks?: ScoredTask[];
  deep_dives?: unknown[];
  assumptions?: string;
}

export type SseEvent =
  | { type: "thread"; thread_id: string }
  | { type: "node"; node: string; message: string }
  | { type: "interrupt"; payload: ReviewPayload }
  | { type: "done"; final: Record<string, unknown>; thread_id: string }
  | { type: "error"; message: string };

export type ReviewAction = "approve" | "edit" | "reject";

export interface ReviewRequest {
  thread_id: string;
  action: ReviewAction;
  hourly_rate?: number;
  weeks_per_month?: number;
  tasks?: unknown[];
}

export interface ReviewResponse {
  thread_id: string;
  final: {
    action?: string;
    step?: string;
    events?: string[];
    report?: string;
    [key: string]: unknown;
  };
  events?: unknown[];
}
