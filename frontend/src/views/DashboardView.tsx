import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { ApiError, Category, ComplaintPage, Priority, Status } from "../api/types";
import { CategoryLabel, PriorityBadge, StatusBadge } from "../components/Badge";
import { Loading } from "../components/Loading";
import { Toast } from "../components/Toast";

const categories: Category[] = ["water", "electricity", "sanitation", "roads", "streetlights", "other"];
const priorities: Priority[] = ["high", "normal", "low"];
const statuses: Status[] = ["open", "in_progress", "resolved", "rejected"];

export function DashboardView() {
  const [page, setPage] = useState(1);
  const [filters, setFilters] = useState<{ category?: Category; priority?: Priority; status?: Status }>({});
  const [data, setData] = useState<ComplaintPage | null>(null);
  const [loading, setLoading] = useState(true);
  const [notice, setNotice] = useState<string | null>(null);
  const pageSize = 8;
  const fetchPage = async () => { setLoading(true); try { setData(await api.getComplaints({ ...filters, page, pageSize })); } catch (error) { setNotice((error as ApiError).detail); } finally { setLoading(false); } };
  useEffect(() => { void fetchPage(); }, [page, filters.category, filters.priority, filters.status]);
  const setFilter = (key: "category" | "priority" | "status", value: string) => { setPage(1); setFilters((current) => ({ ...current, [key]: value || undefined })); };
  const update = async (id: string, status: Status) => { try { await api.updateStatus(id, status); await fetchPage(); } catch (error) { setNotice((error as ApiError).detail); } };
  const totalPages = Math.max(1, Math.ceil((data?.total ?? 0) / pageSize));
  return <section className="view dashboard-view">
    <div className="view-intro compact"><p className="eyebrow">Operations desk</p><h1>Today’s civic pulse.</h1><p>Review and update reports as they move through the municipal workflow.</p></div>
    <div className="filters card" aria-label="Complaint filters">
      <label>Category<select value={filters.category ?? ""} onChange={(e) => setFilter("category", e.target.value)}><option value="">All categories</option>{categories.map((item) => <option key={item}>{item}</option>)}</select></label>
      <label>Priority<select value={filters.priority ?? ""} onChange={(e) => setFilter("priority", e.target.value)}><option value="">All priorities</option>{priorities.map((item) => <option key={item}>{item}</option>)}</select></label>
      <label>Status<select value={filters.status ?? ""} onChange={(e) => setFilter("status", e.target.value)}><option value="">All statuses</option>{statuses.map((item) => <option key={item}>{item}</option>)}</select></label>
      <span className="result-count">{data?.total ?? 0} reports</span>
    </div>
    {loading ? <div className="center-loading"><Loading label="Loading reports…" /></div> : <div className="complaint-list">{data?.items.map((item) => <article className="complaint-card" key={item.id}>
      <div className="complaint-top"><div><CategoryLabel category={item.category} /><h2>{item.ai_summary || item.text}</h2></div><PriorityBadge priority={item.priority} /></div>
      <p className="complaint-location">⌖ {item.location}</p><p className="complaint-copy">{item.text}</p>
      <div className="complaint-bottom"><StatusBadge status={item.status} /><label className="status-control">Update status<select aria-label={`Update status for ${item.id}`} value={item.status} onChange={(e) => void update(item.id, e.target.value as Status)}>{statuses.map((status) => <option key={status} value={status}>{status.replace("_", " ")}</option>)}</select></label></div>
    </article>)}{data?.items.length === 0 && <div className="empty-state">No reports match these filters.</div>}</div>}
    <div className="pagination"><button disabled={page === 1} onClick={() => setPage((value) => value - 1)}>Previous</button><span>Page {page} of {totalPages}</span><button disabled={page >= totalPages} onClick={() => setPage((value) => value + 1)}>Next</button></div>
    {notice && <Toast message={notice} onDismiss={() => setNotice(null)} />}
  </section>;
}
