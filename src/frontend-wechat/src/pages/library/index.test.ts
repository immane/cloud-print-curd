import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import LibraryPage from "./index.vue";

describe("LibraryPage", () => {
  it("renders category tags and resource cards", () => {
    const wrapper = mount(LibraryPage, {
      props: {
        categories: [{ id: 1, name: "Exam" }],
        resources: [{ id: 10, title: "Physics", page_count: 12, is_public: true }],
        selectedCategoryId: 1,
        placeholderImage: "x"
      }
    });

    expect(wrapper.text()).toContain("Exam");
    expect(wrapper.text()).toContain("Physics");
    expect(wrapper.text()).toContain("Order");
  });

  it("shows empty state when no resources", () => {
    const wrapper = mount(LibraryPage, {
      props: {
        categories: [],
        resources: [],
        selectedCategoryId: undefined,
        placeholderImage: "x"
      }
    });

    expect(wrapper.text()).toContain("No resources in this category");
  });
});
