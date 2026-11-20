import fs from "node:fs";
import path from "node:path";
import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

const PUBLIC_PAGES = ["/", "/onboarding", "/cv-upload", "/privacy", "/impressum", "/terms", "/ethics"];

// Serious/critical axe findings that already existed when this suite was added, as "rule@path".
// The test fails only on violations NOT in this list, so the baseline can only shrink.
// Regenerate after fixing issues:  UPDATE_A11Y_BASELINE=1 npm run e2e -- public-pages
const BASELINE_FILE = path.join(__dirname, "a11y-baseline.json");
const UPDATE = !!process.env.UPDATE_A11Y_BASELINE;

function readBaseline(): string[] {
  return fs.existsSync(BASELINE_FILE) ? JSON.parse(fs.readFileSync(BASELINE_FILE, "utf-8")) : [];
}

// Written per test: Playwright restarts its worker after a failure, so in-memory state is lost.
function recordBaseline(pagePath: string, keys: string[]) {
  const kept = readBaseline().filter((k) => !k.endsWith(`@${pagePath}`));
  fs.writeFileSync(BASELINE_FILE, JSON.stringify([...kept, ...keys].sort(), null, 2) + "\n");
}

const baseline = readBaseline();

// Errors from the dev server's own tooling, not from the app.
const IGNORED_CONSOLE = [/\[HMR\]/, /Fast Refresh/, /React DevTools/, /webpack-hmr|_next\/hmr/];

for (const pagePath of PUBLIC_PAGES) {
  test(`${pagePath} loads without console errors and has no new accessibility violations`, async ({ page }) => {
    const errors: string[] = [];
    page.on("console", (msg) => {
      if (msg.type() === "error" && !IGNORED_CONSOLE.some((re) => re.test(msg.text()))) errors.push(msg.text());
    });
    page.on("pageerror", (err) => errors.push(err.message));

    const response = await page.goto(pagePath);
    expect(response?.status()).toBeLessThan(400);
    await page.waitForLoadState("networkidle");

    expect(errors, "console errors").toEqual([]);

    const results = await new AxeBuilder({ page })
      .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"])
      .analyze();
    const serious = results.violations
      .filter((v) => v.impact === "serious" || v.impact === "critical")
      .map((v) => `${v.id}@${pagePath}`);
    if (UPDATE) {
      recordBaseline(pagePath, serious);
      return;
    }

    const newViolations = serious.filter((k) => !baseline.includes(k));
    const details = results.violations
      .filter((v) => newViolations.includes(`${v.id}@${pagePath}`))
      .map((v) => `${v.id}: ${v.help} (${v.nodes.length} elements, e.g. ${v.nodes[0]?.target.join(" ")})`);
    expect(details, "new serious/critical accessibility violations").toEqual([]);
  });
}
