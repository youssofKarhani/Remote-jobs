# Testing Strategy

A test pyramid: many fast checks at the bottom, a few slow end-to-end journeys at the top. Every
layer below runs in CI or at release; each has a pass bar that blocks the merge or release.

**Test data rule:** synthetic CVs or consented, anonymised ones only. Never commit a real CV or
real personal data, in fixtures, snapshots or screenshots.

## Layers

| Layer | Tools | What it proves | Pass bar |
|---|---|---|---|
| Static | eslint, `tsc`, gitleaks, pip-audit, npm audit (ruff, mypy and bandit to add) | Code compiles, follows rules, has no committed secrets or known-vulnerable deps | No errors; no secrets |
| Unit | `pytest`; Vitest + Testing Library (frontend) | Pure logic: extraction heuristics, normalisation, API client, hooks | 80% line coverage on `backend/app/services` and `frontend/src/lib` |
| API and contract | `pytest` + FastAPI `TestClient`; schemathesis against the OpenAPI schema | Every route enforces auth; user A can never read or change user B's data; inputs are validated; no 500s on fuzzed input | All pass; zero 500s |
| Extraction quality | CV benchmark suite (`tests/test_phase9_cv_benchmark_suite.py`) | Field-level accuracy across CV layouts (EN/DE, one to three columns, scanned) | Precision and recall don't drop versus `master` |
| Scenario | `tests/e2e` | Multi-step API workflows | All pass |
| Browser end-to-end | Playwright | Real user journeys in a real browser | All pass on the local stack and on staging |
| Accessibility | `@axe-core/playwright` on every E2E page; manual keyboard + screen-reader pass per release | WCAG 2.2 AA | No serious or critical violations |
| Performance | Lighthouse CI; k6 for API load | Core Web Vitals and API behaviour under load | LCP < 2.5 s, CLS < 0.1, INP < 200 ms; rate limits hold |
| Security, dynamic | OWASP ZAP baseline scan on staging; Mozilla Observatory | Headers, cookies, common web vulnerabilities | No high alerts; headers grade A |
| Privacy | API tests | Export contains all user data; deletion removes every row and file; retention purge works | All pass |

## Critical journeys (Playwright)

1. Signed out: paste or upload a CV → see the preview → sign-in prompt → register → CV saved.
2. Register, sign out, sign in; wrong password shows a readable error; repeated failures are throttled.
3. Upload PDF and DOCX CVs; edit an extracted record on the profile page.
4. Set preferences → open a job → match → tailor a CV → download the document.
5. Download my data; delete account (wrong password refused, right password deletes and signs out).
6. Every public page loads with no console errors and no CSP violations.

## Running tests locally

Backend (from `backend/`):

```bash
uv sync
uv run pytest -q                 # unit + API tests
uv run pytest -q ../tests/e2e    # API scenario tests
```

The benchmark's average-latency assertion depends on machine speed; CI deselects it and gates on
quality metrics instead.

Frontend (from `frontend/`):

```bash
npm ci
npm run lint && npm run typecheck
npm test            # unit tests (Vitest), once added
npm run e2e         # Playwright, starts backend + frontend, once added
```

Security headers on a production build:

```bash
npm run build && npm run start
curl -sI http://localhost:3000/
```

## Writing good tests here

- Test behaviour, not implementation: assert on HTTP status, response body and database state.
- **Every new endpoint gets a tenant-isolation test:** create two users, prove one can't read or
  modify the other's records.
- **Every new table holding personal data** must appear in the account export and be removed by
  account deletion; the generic tests in `test_account_security_and_rights.py` (from PR #2) catch this.
- Use fixtures from `backend/tests/conftest.py` (`client`, `db_session`, `sample_user`,
  `auth_headers`, and `superuser_headers` for admin-only routes); don't call external services.
  Mock the AI gateway.
- A flaky test is a bug: fix it or quarantine it with an issue link, never retry blindly.
