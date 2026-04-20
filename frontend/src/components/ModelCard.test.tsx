import { render, screen } from "@testing-library/react";
import { BrowserRouter } from "react-router";
import { describe, it, expect } from "vitest";
import ModelCard from "./ModelCard";
import type { LLMModelListItem } from "@/types";

const mockModel: LLMModelListItem = {
  id: 1,
  provider: { id: 1, name: "Anthropic", website: "https://anthropic.com" },
  name: "Claude Sonnet 4",
  context_window: 200000,
  input_price_per_1m: "3.0000",
  output_price_per_1m: "15.0000",
  arena_elo_score: 1320,
  release_date: "2025-05-22",
  is_open_source: false,
};

function renderWithRouter(ui: React.ReactElement) {
  return render(<BrowserRouter>{ui}</BrowserRouter>);
}

describe("ModelCard", () => {
  it("renders model name and provider", () => {
    renderWithRouter(<ModelCard model={mockModel} />);
    expect(screen.getByText("Claude Sonnet 4")).toBeDefined();
    expect(screen.getByText("Anthropic")).toBeDefined();
  });

  it("renders ELO score badge", () => {
    renderWithRouter(<ModelCard model={mockModel} />);
    expect(screen.getByText("ELO 1320")).toBeDefined();
  });

  it("renders pricing", () => {
    renderWithRouter(<ModelCard model={mockModel} />);
    expect(screen.getByText("$3/1M")).toBeDefined();
    expect(screen.getByText("$15/1M")).toBeDefined();
  });

  it("renders context window", () => {
    renderWithRouter(<ModelCard model={mockModel} />);
    expect(screen.getByText("200K")).toBeDefined();
  });

  it("renders open source badge when applicable", () => {
    const openSourceModel: LLMModelListItem = {
      ...mockModel,
      is_open_source: true,
    };
    renderWithRouter(<ModelCard model={openSourceModel} />);
    expect(screen.getByText("Open Source")).toBeDefined();
  });

  it("links to model detail page", () => {
    renderWithRouter(<ModelCard model={mockModel} />);
    const link = screen.getByRole("link");
    expect(link.getAttribute("href")).toBe("/models/1");
  });
});
