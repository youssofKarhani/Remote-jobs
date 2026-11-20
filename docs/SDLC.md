# Software Development Lifecycle

How FindJobFit is planned, built, shipped and run. It's sized for a solo developer or a small
team, with security and privacy built into each stage (in the spirit of NIST SSDF and OWASP SAMM),
because the product processes CVs, which are personal data.

```
Plan → Design → Build → Verify → Release → Operate → Respond → Improve
```

## 1. Plan

- Every piece of work is a GitHub issue on the project board.
- A feature gets a one-page spec in the issue:
  - **Problem** and who has it
  - **Acceptance criteria**, written so they can be tested
  - **Data touched**: does it create, read or share personal data? Which fields?
  - **Abuse cases**: how could someone misuse it (scraping, brute force, cost abuse, injection)?
  - **Out of scope**
- Bugs include steps to reproduce, expected vs actual, and environment.

## 2. Design

Needed only for changes touching personal data, authentication, AI/LLM calls, or infrastructure.

- **Threat model (short STRIDE pass):** spoofing, tampering, repudiation, information
  disclosure, denial of service, elevation of privilege. One line each; "n/a" is a valid answer.
- **Privacy note:** lawful basis, retention, whether the new data appears in the account export
  and is removed by account deletion, and any new subprocessor.
- **Architecture decision record (ADR)** in `docs/adr/NNNN-title.md` for decisions that are
  hard to reverse (new datastore, auth model, external provider).
- Keep `ARCHITECTURE.md` the source of truth for structure.

## 3. Build

- **Trunk-based:** short-lived branches off `master`, named `feat/…`, `fix/…`, `chore/…`, `docs/…`.
  Aim to merge within a few days.
- **Conventional Commits** (`feat:`, `fix:`, `chore:`, `docs:`, `test:`, `refactor:`).
- **Pre-commit hooks:** `uvx pre-commit install` once. They run whitespace fixes, a private-key
  check, gitleaks and ruff.
- **Feature flags** for risky or partial work (see `backend/app/config.py`). Ship dark and
  enable deliberately.
- **Secrets never go in the repository.** It's public. Read them from Railway at runtime.
- **Respect boundaries** in `AGENTS.md`: frontend work in `frontend/`, backend work in `backend/`.

## 4. Verify

Every pull request runs CI (`.github/workflows/ci.yml`); a red check blocks the merge.

| Stage | What runs |
|---|---|
| Static | eslint, TypeScript, gitleaks, dependency audit |
| Unit and API | `pytest` (backend), `npm test` (frontend) |
| Scenario | `tests/e2e` API scenarios |
| Build | `next build` |
| Browser | Playwright journeys with axe accessibility checks (see `docs/TESTING.md`) |

Review: one approving review, or the self-review checklist in the PR template when working solo.
The **Definition of Done** is in `.github/pull_request_template.md`.

Repository settings to enable: branch protection on `master` (require CI, no force-push),
GitHub private vulnerability reporting, Dependabot alerts and secret scanning.

## 5. Release

```
local  →  staging (Railway environment)  →  production
```

- Merging to `master` deploys to **staging** automatically.
- Production gets a **tagged release** (`vMAJOR.MINOR.PATCH`) once staging passes:
  Playwright smoke tests, an OWASP ZAP baseline scan and Lighthouse budgets.
- **Database changes** ship as Alembic migrations, run as a pre-deploy step
  (`uv run alembic upgrade head`). Never rely on `create_all` in production.
- **Production config is validated at startup:** the backend refuses to start with
  `ENVIRONMENT=production` and an unsafe `SECRET_KEY` or `DEBUG=true`.
- Release notes are generated from Conventional Commit messages.
- **Rollback:** redeploy the previous tag. Migrations must be backward compatible for one
  release, so the previous version can run against the new schema.

## 6. Operate

- **Errors:** Sentry (or similar) on frontend and backend, with personal data scrubbed.
- **Logs:** structured, no CV text, no tokens, no passwords. `DEBUG` stays off in production.
- **Uptime:** an external check on `/api/health` and the homepage every minute, alerting within
  5 minutes.
- **Backups:** nightly Postgres backups; a restore drill into a scratch database every month.
- **Secrets:** rotated every 90 days, and immediately after any suspected exposure.
- **Dependencies:** Dependabot weekly; critical vulnerabilities patched within 7 days.
- **Data retention:** scheduled purge as defined in the privacy policy.

## 7. Respond

Incident runbook:

1. **Detect:** alert, report or anomaly. Open a private incident note with a timeline.
2. **Contain:** close the exposure (revoke access, disable the feature flag, block traffic).
3. **Eradicate:** rotate affected secrets and fix the root cause.
4. **Assess:** was personal data accessed? Whose, which fields, for how long?
5. **Notify:** if personal data is likely affected, notify the supervisory authority within
   **72 hours** of becoming aware (GDPR Art. 33), and the people affected when the risk is high
   (Art. 34).
6. **Postmortem:** blameless write-up within a week, with follow-up issues.

Security reports from outside come in via `SECURITY.md`.

## 8. Improve

- **Monthly:** extraction benchmark trend, Lighthouse trend, open security and dependency items.
- **Quarterly:** full re-audit with `docs/SECURITY_CHECKLIST.md` and `docs/TESTING.md`; review
  this document.
