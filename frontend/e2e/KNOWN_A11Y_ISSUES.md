# Known accessibility issues

Serious or critical axe findings (WCAG 2.2 AA) that existed when the E2E suite was added. They're
recorded in `a11y-baseline.json`, so tests fail only on **new** violations. Fix these, then
regenerate the baseline so it shrinks:

```bash
UPDATE_A11Y_BASELINE=1 npm run e2e -- public-pages
```

| Rule | Pages | What it means | Likely fix |
|---|---|---|---|
| `color-contrast` | `/`, `/onboarding`, `/cv-upload`, `/privacy`, `/impressum`, `/terms`, `/ethics` | Some text is below 4.5:1 contrast against its background, for example dim zinc text in bordered badges and footers on the near-black page. | Raise muted text from `text-zinc-500`/`600` to at least `text-zinc-400` on `bg-zinc-950`, and check badge text on tinted backgrounds. |
| `label-content-name-mismatch` | `/` | A control's accessible name (e.g. `aria-label`) doesn't contain its visible text, so voice-control users can't activate it by saying what they see. | Make the `aria-label` start with the visible label, or remove it and rely on the visible text. |

Not yet covered by automated checks (do these by hand each release):

- Keyboard-only use of the onboarding wizard, auth dialog and profile dialogs (focus order, visible focus, Escape closes).
- Screen-reader announcements while a CV is being extracted (status messages should be in a live region).
- `prefers-reduced-motion` for the Framer Motion animations.
