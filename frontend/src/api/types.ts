export type Category = "water" | "electricity" | "sanitation" | "roads" | "streetlights" | "other";
export type Priority = "high" | "normal" | "low";
export type Status = "open" | "in_progress" | "resolved" | "rejected";

export interface Complaint {
  id: string;
  text: string;
  location: string;
  reporter_contact: string | null;
  category: Category;
  priority: Priority;
  status: Status;
  ai_summary: string | null;
  triaged_by: string;
  triage_latency_ms: number;
  created_at: string;
  updated_at: string;
}

export interface ComplaintInput { text: string; location: string; reporter_contact?: string; }
export interface ComplaintPage { items: Complaint[]; total: number; page: number; page_size: number; }
export interface Stats { by_category: Record<Category, number>; by_priority: Record<Priority, number>; }
export interface ProviderOutcome { provider: string; latency_ms: number; fallback: boolean; }
export interface Providers { active_provider: string; outcomes: ProviderOutcome[]; }
export interface ApiError extends Error { status: number; detail: string; retryAfter?: string | null; }
