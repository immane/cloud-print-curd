import { test, expect } from "@playwright/test";

test("redirects to login without token", async ({ page }) => {
  await page.goto("/");
  await expect(page).toHaveURL(/login/);
});
