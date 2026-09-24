import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";
import { SubmitView } from "./SubmitView";

describe("SubmitView", () => {
  it("shows mirrored field validation before submission", async () => {
    const user = userEvent.setup(); render(<SubmitView />);
    await user.click(screen.getByRole("button", { name: "Submit report" }));
    expect(screen.getByText(/10 to 2,000 characters/i)).toBeInTheDocument();
    expect(screen.getByText(/3 to 200 characters/i)).toBeInTheDocument();
  });
  it("shows the returned triage result", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({ id: "one", text: "Water pipe burst near school", location: "Block A", reporter_contact: null, category: "water", priority: "high", status: "open", ai_summary: "Burst water pipe near school.", triaged_by: "simulated", triage_latency_ms: 22, created_at: "2026-01-01", updated_at: "2026-01-01" }), { status: 201, headers: { "Content-Type": "application/json" } })));
    const user = userEvent.setup(); render(<SubmitView />);
    await user.type(screen.getByLabelText("What is happening?"), "Water pipe burst near school, road is flooding."); await user.type(screen.getByLabelText("Location"), "Block A"); await user.click(screen.getByRole("button", { name: "Submit report" }));
    expect(await screen.findByText(/report has been sent/i)).toBeInTheDocument(); expect(screen.getByText("simulated")).toBeInTheDocument();
  });
  it("gives a kind retry message for a rate limit", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({ detail: "Rate limit exceeded" }), { status: 429, headers: { "Content-Type": "application/json", "Retry-After": "34" } })));
    const user = userEvent.setup(); render(<SubmitView />);
    await user.type(screen.getByLabelText("What is happening?"), "Water pipe burst near school, road is flooding."); await user.type(screen.getByLabelText("Location"), "Block A"); await user.click(screen.getByRole("button", { name: "Submit report" }));
    expect(await screen.findByText(/34 seconds/i)).toBeInTheDocument();
  });
});
