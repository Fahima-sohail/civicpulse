import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { ApiError, Stats } from "../api/types";
import { Loading } from "../components/Loading";

const friendly: Record<string, string> = { water: "Water", electricity: "Electricity", sanitation: "Sanitation", roads: "Roads", streetlights: "Streetlights", other: "Other", high: "High", normal: "Normal", low: "Low" };
function Bars({ title, values, kind }: { title: string; values: Record<string, number>; kind: "category" | "priority" }) {
  const max = Math.max(...Object.values(values), 1);
  return <section className="chart-card"><h2>{title}</h2><div className="bars">{Object.entries(values).map(([key, value]) => <div className="bar-row" key={key}><span>{friendly[key] ?? key}</span><div className="bar-track"><div className={`bar-fill ${kind} ${key}`} style={{ width: `${(value / max) * 100}%` }} /></div><strong>{value}</strong></div>)}</div></section>;
}
export function StatsView() {
  const [stats, setStats] = useState<Stats | null>(null); const [cache, setCache] = useState("MISS"); const [error, setError] = useState<string | null>(null);
  const load = async () => { try { const result = await api.getStats(); setStats(result.data); setCache(result.cache); } catch (caught) { setError((caught as ApiError).detail); } };
  useEffect(() => { void load(); }, []);
  return <section className="view stats-view"><div className="view-intro compact"><p className="eyebrow">Service overview</p><h1>Where attention is needed.</h1><p>Current report volumes, grouped by service area and urgency.</p></div><div className="stats-toolbar"><span className={`cache-indicator ${cache.toLowerCase()}`}>Cache {cache}</span><button onClick={() => void load()}>Refresh data</button></div>{error && <p className="form-message" role="alert">{error}</p>}{stats ? <div className="chart-grid"><Bars title="Reports by category" values={stats.by_category} kind="category" /><Bars title="Reports by priority" values={stats.by_priority} kind="priority" /></div> : <div className="center-loading"><Loading label="Gathering service data…" /></div>}</section>;
}
