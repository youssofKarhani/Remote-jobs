# Release Security Checklist

Run before every production release and during the quarterly re-audit. Each item has a way to
check it. Record the result in the release notes or the quarterly audit.

## Configuration

- [ ] Backend runs with `ENVIRONMENT=production` and `DEBUG=false` (`GET /api/health` reports `production`).
- [ ] `SECRET_KEY` is random, at least 32 characters, unique to production, and rotated within 90 days.
- [ ] `/docs`, `/redoc` and `/openapi.json` return 404 in production.
- [ ] `CORS_ORIGINS` lists only production origins.
- [ ] Database has no public TCP proxy; it's reachable only on the private network.
- [ ] No secrets in the repository or its history since the last release (gitleaks clean).

## HTTP and browser

- [ ] Security headers present: CSP, HSTS, X-Content-Type-Options, X-Frame-Options,
      Referrer-Policy, Permissions-Policy (`curl -sI https://findjobfit.de`).
- [ ] Mozilla Observatory and securityheaders.com grade A or better.
- [ ] `www` and `http://` permanently redirect to `https://findjobfit.de`.
- [ ] No CSP violations in the browser console on public pages.

## Authentication and access

- [ ] Sign-in and sign-up are rate limited (repeated failures return 429).
- [ ] Password rule enforced for new accounts.
- [ ] Every data endpoint requires authentication; admin endpoints require a superuser.
- [ ] Tenant-isolation tests pass for every endpoint.
- [ ] Tokens are never placed in URLs, logs or analytics.

## Data protection

- [ ] Account export contains every table holding the user's data.
- [ ] Account deletion removes all rows and generated files.
- [ ] Logs contain no CV text, tokens or passwords.
- [ ] Privacy policy matches the product: features, subprocessors, retention periods.
- [ ] Retention purge job ran successfully since the last release.

## Dependencies and supply chain

- [ ] No unresolved critical or high advisories (pip-audit, npm audit, Dependabot).
- [ ] GitHub Actions pinned to major versions; Dependabot updates them.

## Dynamic testing

- [ ] OWASP ZAP baseline scan against staging: no high-risk alerts.
- [ ] Playwright journeys and axe checks pass on staging.

## Operations

- [ ] Error tracking and uptime alerts working (trigger a test alert).
- [ ] Last backup restore drill succeeded within the past month.
