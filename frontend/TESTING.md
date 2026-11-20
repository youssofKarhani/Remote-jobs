# Frontend tests

The overall strategy is in [`docs/TESTING.md`](../docs/TESTING.md). This file covers how to run
the frontend layers.

## Unit and component tests (Vitest)

```bash
npm test            # run once
npm run test:watch  # watch mode
```

- Config: `vitest.config.ts` (jsdom, the `@/` alias), setup in `vitest.setup.ts`.
- Tests live next to the code as `*.test.ts(x)`, e.g. `src/lib/api.test.ts`.
- Mock `fetch` and `@/lib/auth-context` rather than calling the real API.

## Browser end-to-end tests (Playwright)

```bash
npx playwright install chromium   # once per machine
npm run e2e                       # headless
npm run e2e:ui                    # interactive runner
```

`playwright.config.ts` starts both servers for you:

- **Backend** on port 8000 via `uv run --directory ../backend uvicorn …`, using a throwaway
  SQLite file `backend/e2e.db` (git-ignored). It never touches a shared database.
- **Frontend** on port 3000 via `npm run dev`, pointed at that backend.

If you already have both running locally, they're reused.

Journeys covered so far (`e2e/`):

- `auth.spec.ts`: register → signed in → sign out; a wrong password shows a readable error.
- `public-pages.spec.ts`: every public page loads without console errors and has no **new**
  serious or critical accessibility violations (axe, WCAG 2.2 AA). Existing issues are listed in
  `e2e/KNOWN_A11Y_ISSUES.md` and `e2e/a11y-baseline.json`.

Test accounts use unique `@example.com` addresses and exist only in the throwaway database.
