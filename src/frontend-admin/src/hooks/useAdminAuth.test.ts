import { describe, it, expect } from "vitest";
import { useAdminAuth } from "./useAdminAuth";

describe("useAdminAuth", () => {
  it("returns false without token", () => {
    localStorage.removeItem("admin_token");
    expect(useAdminAuth().isAuthed).toBe(false);
  });

  it("returns true with token", () => {
    localStorage.setItem("admin_token", "x");
    expect(useAdminAuth().isAuthed).toBe(true);
  });
});
