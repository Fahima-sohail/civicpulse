import { render, screen } from "@testing-library/react";
import { vi } from "vitest";
import { StatsView } from "./StatsView";
it("displays the API cache header and active provider", async () => {
  vi.stubGlobal("fetch", vi.fn()
    .mockResolvedValueOnce(new Response(JSON.stringify({ by_category: { water: 4, electricity: 1, sanitation: 0, roads: 0, streetlights: 0, other: 0 }, by_priority: { high: 2, normal: 2, low: 1 } }), { headers: { "Content-Type": "application/json", "X-Cache": "HIT" } }))
    .mockResolvedValueOnce(new Response(JSON.stringify({ active_provider: "llm:ollama", outcomes: [{ provider: "llm:ollama", latency_ms: 43, fallback: false }] }), { headers: { "Content-Type": "application/json" } })));
  render(<StatsView />);
  expect(await screen.findByText("Cache HIT")).toBeInTheDocument(); expect(screen.getByText("Reports by category")).toBeInTheDocument(); expect(screen.getByText("Active provider: llm:ollama")).toBeInTheDocument();
});
