import { test, expect, type Page } from "@playwright/test";

async function installApiMocks(page: Page) {
  const addresses = [
    {
      id: 1,
      title: "Dorm",
      recipient_name: "Alice",
      phone: "13800000000",
      address_line1: "No.1 Campus Road"
    }
  ];

  const files = [
    {
      id: 10,
      filename: "starter.pdf",
      page_count: 6,
      size_bytes: 2048,
      status: "ready"
    }
  ];

  await page.route("**/v1/**", async (route) => {
    const url = route.request().url();
    const method = route.request().method();

    if (url.includes("/v1/home/slider")) return route.fulfill({ json: [] });
    if (url.includes("/v1/home/tutorial")) {
      return route.fulfill({ json: { title: "How to print", updated_at: "2026-05-12", image_url: "" } });
    }
    if (url.includes("/v1/prices/tip")) return route.fulfill({ json: { text: "Prices are per page" } });
    if (url.includes("/v1/prices")) {
      return route.fulfill({
        json: [
          { size: "A4", paper_type: "standard", description: "A4 B/W single", unit_price_cents: 20 },
          { size: "A3", paper_type: "premium", description: "A3 color duplex", unit_price_cents: 120 }
        ]
      });
    }
    if (url.includes("/v1/library/categories")) return route.fulfill({ json: [{ id: 1, name: "Exam" }] });
    if (url.includes("/v1/library/resources")) {
      return route.fulfill({
        json: {
          items: [{ id: 201, title: "Math Notes", page_count: 30, is_public: true, thumbnail_url: "" }]
        }
      });
    }
    if (url.includes("/v1/users/me")) {
      return route.fulfill({
        json: { id: 7, display_name: "Tester", balance_cents: 5000, avatar_url: "" }
      });
    }
    if (url.includes("/v1/files") && method === "GET") return route.fulfill({ json: { items: files } });
    if (url.includes("/v1/orders") && method === "GET") return route.fulfill({ json: { items: [] } });
    if (url.includes("/v1/addresses") && method === "GET") return route.fulfill({ json: addresses });

    if (url.includes("/v1/files/create-upload") && method === "POST") {
      return route.fulfill({
        json: {
          upload_id: "up-1",
          upload_url: "http://localhost:5174/mock-upload",
          fields: { key: "files/up-1" }
        }
      });
    }
    if (url.includes("/v1/files/complete") && method === "POST") {
      files.push({
        id: 11,
        filename: "new-upload.pdf",
        page_count: 12,
        size_bytes: 4096,
        status: "ready"
      });
      return route.fulfill({ json: { ok: true } });
    }

    if (url.includes("/v1/orders/create") && method === "POST") {
      return route.fulfill({ json: { order_id: "order-123" } });
    }

    if (url.includes("/v1/addresses") && method === "POST") {
      const body = route.request().postDataJSON() as Record<string, string>;
      addresses.push({ id: 2, ...body });
      return route.fulfill({ json: { id: 2 } });
    }

    return route.fulfill({ status: 200, json: {} });
  });

  await page.route("**/mock-upload", async (route) => {
    if (route.request().method() === "POST") {
      return route.fulfill({ status: 204, body: "" });
    }
    return route.continue();
  });
}

test.beforeEach(async ({ page }) => {
  await installApiMocks(page);
  await page.goto("/");
});

test("renders three tabs", async ({ page }) => {
  await expect(page.getByRole("button", { name: "Home", exact: true })).toBeVisible();
  await expect(page.getByRole("button", { name: "Library", exact: true })).toBeVisible();
  await expect(page.getByRole("button", { name: "Me", exact: true })).toBeVisible();
});

test("price filter flow works", async ({ page }) => {
  await page.getByRole("button", { name: "Price List" }).first().click();
  await expect(page.getByRole("heading", { name: "Price List" })).toBeVisible();

  const paperTypeInput = page.getByPlaceholder("Filter paper type");
  await paperTypeInput.fill("premium");
  await expect(page.getByText("A3 / premium")).toBeVisible();
  await expect(page.getByText("A4 / standard")).toHaveCount(0);
});

test("upload file flow shows progress and refreshed list", async ({ page }) => {
  await page.getByRole("button", { name: "Me", exact: true }).click();
  const fileInput = page.locator("input[type='file']");
  await fileInput.setInputFiles({
    name: "new-upload.pdf",
    mimeType: "application/pdf",
    buffer: Buffer.from("fake pdf bytes")
  });

  await expect(page.getByText("Progress: 100%")).toBeVisible();
  await expect(page.getByText("new-upload.pdf")).toBeVisible();
});

test("create order and pay flow works", async ({ page }) => {
  await page.getByRole("button", { name: "Me", exact: true }).click();
  page.once("dialog", async (dialog) => {
    expect(dialog.message()).toContain("order-123");
    await dialog.accept();
  });

  await page.getByRole("button", { name: "Create Order" }).first().click();
  await expect(page.getByRole("heading", { name: "Checkout: starter.pdf" })).toBeVisible();
  await page.getByRole("button", { name: "Pay Now" }).click();
  await expect(page.getByText("Payment success")).toBeVisible();
});

test("address management add flow works", async ({ page }) => {
  await page.getByRole("button", { name: "Me", exact: true }).click();
  await page.getByRole("button", { name: "Address Management" }).click();
  await expect(page.getByRole("heading", { name: "Address Management" })).toBeVisible();

  await page.getByPlaceholder("Title").fill("Office");
  await page.getByPlaceholder("Recipient").fill("Bob");
  await page.getByPlaceholder("Phone").fill("13900000000");
  await page.getByPlaceholder("Address").fill("88 River Street");
  await page.getByRole("button", { name: "Add", exact: true }).click();

  await expect(page.getByText("Office")).toBeVisible();
  await expect(page.getByText("Bob · 13900000000")).toBeVisible();
});
