import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import HomePage from "./index.vue";

describe("HomePage", () => {
  it("renders tutorial and price buttons", () => {
    const wrapper = mount(HomePage, {
      props: { slider: [], tutorial: { title: "t" } }
    });
    expect(wrapper.text()).toContain("Printing Tutorial");
    expect(wrapper.text()).toContain("Price List");
  });

  it("emits slide-click when banner is tapped", async () => {
    const wrapper = mount(HomePage, {
      props: {
        slider: [{ id: 1, image_url: "https://example.com/1.png" }],
        tutorial: { title: "Guide" }
      }
    });

    await wrapper.find(".slide").trigger("click");
    expect(wrapper.emitted("slide-click")?.length).toBe(1);
  });
});
