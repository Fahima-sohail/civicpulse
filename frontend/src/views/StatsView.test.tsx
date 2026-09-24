import { render, screen } from "@testing-library/react";
import { vi } from "vitest";
import { StatsView } from "./StatsView";
it("displays the API cache header", async () => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({ by_category: { water: 4, electricity: 1, sanitation: 0, roads: 0, streetlights: 0, other: 0 }, by_priority: { high: 2, normal: 2, low: 1 } }), { headers: { "Content-Type": "application/json", "X-Cache": "HIT" } })));
  render(<StatsView />);
  expect(await screen.findByText("Cache HIT")).toBeInTheDocument(); expect(screen.getByText("Reports by category")).toBeInTheDocument();
});
