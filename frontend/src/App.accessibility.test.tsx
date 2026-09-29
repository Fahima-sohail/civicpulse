import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";
import App from "./App";


describe("application accessibility", () => {
  it("offers a skip link and marks the current view for assistive technology", () => {
    render(<App />);

    expect(screen.getByRole("link", { name: "Skip to main content" })).toHaveAttribute("href", "#main-content");
    expect(screen.getByRole("button", { name: "Submit" })).toHaveAttribute("aria-current", "page");
    expect(screen.getByRole("main")).toHaveAttribute("id", "main-content");
  });

  it("exposes the dark-mode state as a pressed toggle", async () => {
    const user = userEvent.setup();
    render(<App />);

    const toggle = screen.getByRole("button", { name: "Toggle dark mode" });
    expect(toggle).toHaveAttribute("aria-pressed", "false");
    await user.click(toggle);
    expect(toggle).toHaveAttribute("aria-pressed", "true");
  });

  it("updates the current view announcement when navigation changes", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({ items: [], total: 0, page: 1, page_size: 8 }), { headers: { "Content-Type": "application/json" } })));
    const user = userEvent.setup();
    render(<App />);

    await user.click(screen.getByRole("button", { name: "Dashboard" }));

    expect(screen.getByRole("button", { name: "Dashboard" })).toHaveAttribute("aria-current", "page");
    expect(await screen.findByText(/no reports match/i)).toBeInTheDocument();
  });
});
