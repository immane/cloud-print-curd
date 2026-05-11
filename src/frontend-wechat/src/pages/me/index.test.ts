import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import MePage from "./index.vue";

describe("MePage", () => {
  it("shows profile and files", () => {
    const wrapper = mount(MePage, {
      props: {
        profile: { display_name: "u", balance_cents: 1200 },
        files: [{ id: 1, filename: "a.pdf", page_count: 1, size_bytes: 12, status: "ready" }],
        orderStatusCards: [{ key: "k", label: "Pending", count: 1 }],
        uploadProgress: 0,
        placeholderImage: "x"
      }
    });
    expect(wrapper.text()).toContain("u");
    expect(wrapper.text()).toContain("a.pdf");
  });

  it("emits filter-orders when status card clicked", async () => {
    const wrapper = mount(MePage, {
      props: {
        profile: { display_name: "u", balance_cents: 1200 },
        files: [],
        orderStatusCards: [{ key: "PENDING_PAYMENT", label: "Pending", count: 1 }],
        uploadProgress: 0,
        placeholderImage: "x"
      }
    });

    await wrapper.find(".status-grid button").trigger("click");
    expect(wrapper.emitted("filter-orders")?.[0]).toEqual(["PENDING_PAYMENT"]);
  });
});
