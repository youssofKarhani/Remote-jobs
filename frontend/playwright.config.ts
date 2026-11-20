import { defineConfig, devices } from "@playwright/test";

const API_URL = "http://localhost:8000";
const APP_URL = "http://localhost:3000";

/**
 * Browser end-to-end tests against the real backend and frontend.
 * The backend uses a throwaway SQLite file (backend/e2e.db), never a shared database.
 */
export default defineConfig({
  testDir: "./e2e",
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  workers: 1,
  reporter: process.env.CI ? [["github"], ["html", { open: "never" }]] : "list",
  timeout: 60_000,
  use: {
    baseURL: APP_URL,
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: [
    {
      command: "uv run --directory ../backend uvicorn app.main:app --port 8000",
      url: `${API_URL}/api/health`,
      reuseExistingServer: !process.env.CI,
      timeout: 120_000,
      env: {
        DATABASE_URL: "sqlite:///./e2e.db",
        ENVIRONMENT: "development",
        DEBUG: "false",
        CORS_ORIGINS: APP_URL,
      },
    },
    {
      command: "npm run dev",
      url: APP_URL,
      reuseExistingServer: !process.env.CI,
      timeout: 180_000,
      env: {
        NEXT_PUBLIC_API_URL: API_URL,
        NEXT_TELEMETRY_DISABLED: "1",
      },
    },
  ],
});
