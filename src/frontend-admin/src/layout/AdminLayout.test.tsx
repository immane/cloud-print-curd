import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import { describe, it, expect } from "vitest";
import AdminLayout from "./AdminLayout";

describe("AdminLayout", () => {
  it("renders sidebar menus", () => {
    const client = new QueryClient();
    render(
      <QueryClientProvider client={client}>
        <MemoryRouter>
          <AdminLayout />
        </MemoryRouter>
      </QueryClientProvider>
    );

    expect(screen.getByText("Cloud Print")).toBeTruthy();
    expect(screen.getByText("Orders")).toBeTruthy();
    expect(screen.getByText("Files")).toBeTruthy();
  });
});
