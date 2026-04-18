# QA Screenshots

Throwaway Playwright / manual verification screenshots captured during feature work. **Gitignored** by the project-wide `*.png` rule in `.gitignore` — these live on disk for visual inspection but are not committed.

For curated, committed design assets (landing page, auth, pricing mockups), see `docs/mockups/screenshots/` instead.

## Folders

| Folder | What goes here |
|---|---|
| `onboarding/` | 3-step onboarding wizard flow captures (`onboarding-test-01-login.png` … `-09-after-fix.png`) |
| `dasha/` | Dasha widget + full dasha page (Mahadasha through Prana, 5-level rendering, label/layout iterations) |
| `dashboard/` | Dashboard shell, widget grid, error boundaries, layout fixes, post-login states |
| `muhurta/` | Muhurta widget + page (blocks, bar, contrast, legibility, widget closeups) |
| `astrologers/` | Astrologer marketplace / listing / verified flows |
| `chart/` | Chart calculator + chart detail page (inputs, calculated output, detail views) |
| `consultations/` | Consultation booking / management flows |
| `landing/` | Public landing page verification shots (for finalized versions, use `docs/mockups/screenshots/`) |
| `login/` | Login / post-login state captures (Clerk flows, redirects) |
| `misc/` | One-off screenshots that don't fit a feature bucket |

## Drop-in guide for new screenshots

When running Playwright (or `mcp__playwright__browser_take_screenshot`) during feature work:

1. Save to the matching folder above, not the project root.
2. Name descriptively: `<feature>-<state>.png` — e.g. `dashboard-widget-empty.png`, `dasha-level-5-expanded.png`. Avoid generic names like `test.png` or `current.png`.
3. If the feature is new and no folder fits, create a new subfolder rather than using `misc/`.
4. Intermediate debug captures are fine to keep — they're gitignored and cost nothing. Prune when they stop being useful.
