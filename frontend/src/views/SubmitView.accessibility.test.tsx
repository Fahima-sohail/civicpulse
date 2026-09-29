import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";
import { SubmitView } from "./SubmitView";


describe("SubmitView accessibility", () => {
  it("connects validation errors to their input fields", async () => {
    const user = userEvent.setup();
    render(<SubmitView />);

    await user.click(screen.getByRole("button", { name: "Submit report" }));

    expect(screen.getByLabelText("What is happening?")).toHaveAttribute("aria-describedby", "text-help text-error");
    expect(screen.getByLabelText("Location")).toHaveAttribute("aria-describedby", "location-error");
    expect(screen.getByText(/10 to 2,000 characters/i)).toHaveAttribute("id", "text-error");
    expect(screen.getByText(/3 to 200 characters/i)).toHaveAttribute("id", "location-error");
  });

  it("announces a successful triage result as one complete update", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({ id: "one", text: "Water pipe burst near school", location: "Block A", reporter_contact: null, category: "water", priority: "high", status: "open", ai_summary: "Burst water pipe near school.", triaged_by: "llm:ollama", triage_latency_ms: 22, created_at: "2026-01-01", updated_at: "2026-01-01" }), { status: 201, headers: { "Content-Type": "application/json" } })));
    const user = userEvent.setup();
    render(<SubmitView />);

    await user.type(screen.getByLabelText("What is happening?"), "Water pipe burst near school, road is flooding.");
    await user.type(screen.getByLabelText("Location"), "Block A");
    await user.click(screen.getByRole("button", { name: "Submit report" }));

    const heading = await screen.findByText(/report has been sent/i);
    const result = heading.closest("section");
    expect(result).toHaveAttribute("aria-live", "polite");
    expect(result).toHaveAttribute("aria-atomic", "true");
  });
});
