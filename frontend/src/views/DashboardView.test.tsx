import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";
import { DashboardView } from "./DashboardView";

const complaint = { id: "a1", text: "Road has large pothole near school", location: "Street 4", reporter_contact: null, category: "roads", priority: "high", status: "open", ai_summary: "Large pothole near school.", triaged_by: "rules", triage_latency_ms: 1, created_at: "2026-01-01", updated_at: "2026-01-01" };
describe("DashboardView", () => {
  it("surfaces the exact 409 detail from the backend", async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(new Response(JSON.stringify({ items: [complaint], total: 1, page: 1, page_size: 8 }), { headers: { "Content-Type": "application/json" } }))
      .mockResolvedValueOnce(new Response(JSON.stringify({ detail: "Invalid transition: open -> resolved" }), { status: 409, headers: { "Content-Type": "application/json" } }));
    vi.stubGlobal("fetch", fetchMock);
    const user = userEvent.setup(); render(<DashboardView />); await screen.findByText("Large pothole near school.");
    await user.selectOptions(screen.getByLabelText("Update status for a1"), "resolved");
    expect(await screen.findByRole("alert")).toHaveTextContent("Invalid transition: open -> resolved");
  });
  it("sends filter choices to the typed list request", async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify({ items: [], total: 0, page: 1, page_size: 8 }), { headers: { "Content-Type": "application/json" } })); vi.stubGlobal("fetch", fetchMock);
    const user = userEvent.setup(); render(<DashboardView />); await screen.findByText(/no reports match/i); await user.selectOptions(screen.getByLabelText("Category"), "water");
    expect(await screen.findByText(/no reports match/i)).toBeInTheDocument(); expect(fetchMock).toHaveBeenLastCalledWith(expect.stringContaining("category=water"), expect.any(Object));
  });
});
