import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./tests/e2e",
  use: {
    baseURL: "http://localhost:5174"
  },
  webServer: {
    command: "npm run dev -- --host 127.0.0.1 --port 5174",
    port: 5174,
    reuseExistingServer: true,
    timeout: 120000
  }
});
