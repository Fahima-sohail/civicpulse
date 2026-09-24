import type { ApiError, Category, Complaint, ComplaintInput, ComplaintPage, Priority, Providers, Stats, Status } from "./types";

async function request<T>(path: string, init?: RequestInit): Promise<{ data: T; response: Response }> {
  const response = await fetch(path, { headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) }, ...init });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    const error = new Error(typeof body.detail === "string" ? body.detail : "The request could not be completed.") as ApiError;
    error.status = response.status;
    error.detail = error.message;
    error.retryAfter = response.headers.get("Retry-After");
    throw error;
  }
  return { data: await response.json() as T, response };
}

export const api = {
  createComplaint: (input: ComplaintInput) => request<Complaint>("/api/complaints", { method: "POST", body: JSON.stringify(input) }).then(({ data }) => data),
  getComplaints: (filters: { category?: Category; priority?: Priority; status?: Status; page: number; pageSize: number }) => {
    const params = new URLSearchParams({ page: String(filters.page), page_size: String(filters.pageSize) });
    if (filters.category) params.set("category", filters.category);
    if (filters.priority) params.set("priority", filters.priority);
    if (filters.status) params.set("status", filters.status);
    return request<ComplaintPage>(`/api/complaints?${params}`).then(({ data }) => data);
  },
  updateStatus: (id: string, status: Status) => request<Complaint>(`/api/complaints/${id}/status`, { method: "PATCH", body: JSON.stringify({ status }) }).then(({ data }) => data),
  getStats: () => request<Stats>("/api/stats").then(({ data, response }) => ({ data, cache: response.headers.get("X-Cache") ?? "MISS" })),
  getProviders: () => request<Providers>("/api/meta/providers").then(({ data }) => data),
};
