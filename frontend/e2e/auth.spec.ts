import { expect, test } from "@playwright/test";

// Long enough for current and stricter future password rules; local test value only.
const PASSWORD = "e2e Local Test 7731 pass";

function uniqueEmail() {
  return `e2e-${Date.now()}-${Math.floor(Math.random() * 1e6)}@example.com`;
}

test.describe("authentication", () => {
  test("register, see signed-in state, sign out", async ({ page }) => {
    const email = uniqueEmail();
    await page.goto("/");

    await page.getByRole("button", { name: /^sign in$/i }).first().click();
    const dialog = page.getByRole("dialog");
    await dialog.getByRole("tab", { name: "Register" }).click();
    await dialog.getByPlaceholder("e.g. Alex Morgan").fill("E2E Tester");
    await dialog.getByPlaceholder("alex@example.com").fill(email);
    await dialog.getByPlaceholder("••••••••").fill(PASSWORD);
    await dialog.getByRole("button", { name: "Create Account" }).click();

    await expect(dialog).toBeHidden();
    await expect(page.getByText("E2E Tester").first()).toBeVisible();
    await expect.poll(() => page.evaluate(() => !!localStorage.getItem("auth_token"))).toBe(true);

    await page.getByTitle("Sign out").click();
    await page.getByRole("dialog").getByRole("button", { name: "Yes, Sign Out" }).click();

    await expect.poll(() => page.evaluate(() => localStorage.getItem("auth_token"))).toBeNull();
    await expect(page.getByRole("button", { name: /^sign in$/i }).first()).toBeVisible();
  });

  test("wrong password shows a readable error", async ({ page, request }) => {
    const email = uniqueEmail();
    const reg = await request.post("http://localhost:8000/api/v1/auth/register", {
      data: { email, password: PASSWORD, full_name: "E2E Wrong Password" },
    });
    expect(reg.status()).toBe(201);

    await page.goto("/");
    await page.getByRole("button", { name: /^sign in$/i }).first().click();
    const dialog = page.getByRole("dialog");
    await dialog.getByPlaceholder("candidate@example.com").fill(email);
    await dialog.getByPlaceholder("••••••••").fill("definitely-not-it");
    await dialog.getByRole("button", { name: /^sign in$/i }).click();

    await expect(dialog.getByText(/Incorrect email or password/)).toBeVisible();
    await expect(dialog.getByText("[object Object]")).toHaveCount(0);
  });
});
