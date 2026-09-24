import { useEffect, useState } from "react";
import { ErrorBoundary } from "./components/ErrorBoundary";
import { DashboardView } from "./views/DashboardView";
import { StatsView } from "./views/StatsView";
import { SubmitView } from "./views/SubmitView";

type View = "submit" | "dashboard" | "stats";
const labels: Record<View, string> = { submit: "Submit", dashboard: "Dashboard", stats: "Stats" };
function Shell() {
  const [view, setView] = useState<View>("submit");
  const [dark, setDark] = useState(() => localStorage.getItem("civicpulse-theme") === "dark");
  useEffect(() => { document.documentElement.dataset.theme = dark ? "dark" : "light"; localStorage.setItem("civicpulse-theme", dark ? "dark" : "light"); }, [dark]);
  return <div className="app-shell"><header><button className="brand" onClick={() => setView("submit")}><span className="brand-mark">C</span><span>CivicPulse<small>municipal response</small></span></button><nav aria-label="Main navigation">{(Object.keys(labels) as View[]).map((item) => <button className={view === item ? "active" : ""} key={item} onClick={() => setView(item)}>{labels[item]}</button>)}</nav><button className="theme-toggle" onClick={() => setDark((current) => !current)} aria-label="Toggle dark mode">{dark ? "☀ Light" : "◐ Dark"}</button></header><main>{view === "submit" && <SubmitView />}{view === "dashboard" && <DashboardView />}{view === "stats" && <StatsView />}</main><footer>Made for clearer, kinder municipal response.</footer></div>;
}
export default function App() { return <ErrorBoundary><Shell /></ErrorBoundary>; }
