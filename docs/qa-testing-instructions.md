# QA Testing Instructions for Josi

> **For AI QA agents:** Follow these instructions to test the Josi astrology platform end-to-end. Test each section sequentially. Report PASS/FAIL for each test case with screenshots where applicable.

## Prerequisites

### Start the services
```bash
cd /path/to/josi-svc
josi redock up dev --local
```
This starts: API (localhost:1954), Frontend (localhost:1989), PostgreSQL (localhost:1961), Redis (localhost:6399).

### Verify services are running
```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:1954/docs  # Should return 200
curl -s -o /dev/null -w "%{http_code}" http://localhost:1989        # Should return 200
```

### Test credentials
- Email: `imgovind@live.com`
- Password: `Test@123`
- Note: First login on a new browser triggers Clerk device verification (email code required)

---

## 1. Landing Page

| # | Test | Steps | Expected |
|---|------|-------|----------|
| 1.1 | Page loads | Navigate to `http://localhost:1989` | Landing page with "Ancient eyes on an infinite sky" heading, constellation sky background, chart calculator form |
| 1.2 | No console errors | Open DevTools Console | Zero errors (favicon 404 is acceptable) |
| 1.3 | Sign In link | Click "Sign In" in top nav | Redirects to `/auth/login` with Clerk sign-in form |
| 1.4 | Chart calculator form | Form has: name, date, time, place inputs + "Reveal Your Cosmic Story" button | All inputs rendered, button clickable |
| 1.5 | Scroll sections | Scroll down the page | "What you'll discover", AI Astrologer chat demo, "Six traditions" section, footer all render |

---

## 2. Authentication

| # | Test | Steps | Expected |
|---|------|-------|----------|
| 2.1 | Sign in page | Navigate to `/auth/login` | Clerk sign-in form with Apple/Google/X social login + email/password |
| 2.2 | Login flow | Enter credentials, click Continue | Redirects to `/dashboard` after auth |
| 2.3 | Stale session handling | Clear cookies, navigate to `/auth/login` | Sign-in form renders (no blank page) |
| 2.4 | Protected route redirect | Log out, navigate to `/dashboard` | Redirects to `/auth/login` |

---

## 3. Dashboard

| # | Test | Steps | Expected |
|---|------|-------|----------|
| 3.1 | Dashboard loads | Navigate to `/dashboard` (logged in) | Greeting with user name, date, "Add Widget" button, widget grid |
| 3.2 | No crash errors | Check console | No "Application error", no `TypeError`, no crash overlay |
| 3.3 | Today's Sky widget | Check the panchang widget | Shows tithi name, nakshatra, yoga, karana, vara with live data (not hardcoded) |
| 3.4 | Muhurta Timeline widget | Check the muhurta widget | Horizontal color-coded bar (6AM-6PM), hour dividers, Rahu Kaal/Abhijit time cards, "View full Muhurta" link |
| 3.5 | AI Chat widget | Check AI chat | Input field with "What would you like to explore?", suggestion chips (Career outlook, Current transits, Relationship insights) |
| 3.6 | Chart Quick View widget | Check chart widget | Either shows chart data OR "No charts calculated yet" with "Calculate your first chart" link |
| 3.7 | Widget error boundary | If any widget fails | Shows "Widget failed to load" with Remove button, NOT a full page crash |
| 3.8 | Add Widget button | Click "Add Widget" | Modal opens with widget catalog, categories, search |
| 3.9 | No hardcoded counter badges | Check sidebar nav items | No fake "12", "7", "1" badges next to nav items |

---

## 4. Sidebar Navigation

| # | Test | Steps | Expected |
|---|------|-------|----------|
| 4.1 | All nav items present | Check sidebar | Overview (Dashboard, Charts, Profiles, AI Insights), Explore (Compatibility, Transits, Panchang, Dasha, Muhurta, Cultural Events), Connect (Astrologers, Consultations) |
| 4.2 | No Settings in sidebar | Check sidebar | "Settings" is NOT a nav item (accessible via user dropdown at bottom) |
| 4.3 | No 404 pages | Click every nav item | All pages load without 404 errors |
| 4.4 | User dropdown | Click user name at bottom of sidebar | Shows Edit Profile, Subscription, Settings links |
| 4.5 | Sidebar collapse | Click collapse button (top right of sidebar) | Sidebar collapses to icon-only mode |

---

## 5. Profiles (Persons)

| # | Test | Steps | Expected |
|---|------|-------|----------|
| 5.1 | Profiles page loads | Navigate to `/persons` | Page with profile list or empty state |
| 5.2 | Create profile | Click "Add Profile", fill name + DOB + time + place, save | Profile created, appears in list |
| 5.3 | Edit profile | Click edit on a profile, change a field, save | Profile updated |
| 5.4 | Default profile | One profile should have a default badge/star | Default profile used by widgets |
| 5.5 | Delete profile | Click delete, confirm in modal | Profile removed (soft delete) |

---

## 6. Chart Calculation & Detail

| # | Test | Steps | Expected |
|---|------|-------|----------|
| 6.1 | Calculate chart page | Navigate to `/charts/new` | Profile selector, tradition/house system/ayanamsa dropdowns, "Calculate Chart" button |
| 6.2 | Calculate a chart | Select a profile with complete birth data, click Calculate | Chart calculated, redirects to chart detail page (NOT `/charts/undefined`) |
| 6.3 | Chart detail — Overview tab | Check Overview tab | Rasi chart + Navamsa chart side-by-side, birth panchang section, dasha balance at birth, technical details (ayanamsa) |
| 6.4 | Chart format selector | Click the format dropdown (South Indian/North Indian/Western Wheel) | Chart visualization changes format |
| 6.5 | Planets tab | Click Planets tab | Table with all 9 planets: sign, degree, nakshatra, pada, dignity, retrograde indicator |
| 6.6 | Houses tab | Click Houses tab | House cusps table OR "data not available" message |
| 6.7 | Aspects tab | Click Aspects tab | Aspects table with planet pairs, aspect type, orb, applying/separating |
| 6.8 | Divisional Charts tab | Click Divisional Charts tab | Table showing D1-D60 positions per planet, D1/D9 columns highlighted |
| 6.9 | Strength tab | Click Strength tab | Shadbala table, Ashtakavarga table, Bhava Bala table — OR "not available" message |
| 6.10 | Export Text | Click "Export Text" button in header | Downloads .txt file in 1991 ASCII format with planet positions, chart grids, dasha details |
| 6.11 | Export PDF | Click "Print / PDF" button | Opens new window with formatted chart for printing |
| 6.12 | Delete chart | Click Delete, confirm in modal | Chart deleted, redirects to `/charts` |

---

## 7. Charts Listing

| # | Test | Steps | Expected |
|---|------|-------|----------|
| 7.1 | Charts page | Navigate to `/charts` | Grid or list view of calculated charts |
| 7.2 | View modes | Toggle between Grid and List views | Both render correctly |
| 7.3 | Filter by tradition | Use filter dropdown | Charts filtered by selected tradition |
| 7.4 | Delete from listing | Click trash icon on a chart, confirm | Chart removed from list |

---

## 8. Feature Pages

### 8.1 Panchang (`/panchang`)

| # | Test | Steps | Expected |
|---|------|-------|----------|
| 8.1.1 | Daily view | Default tab | Full panchang with 5 elements, timing windows, quality summary |
| 8.1.2 | Date navigation | Click prev/next arrows | Panchang updates for selected date |
| 8.1.3 | Weekly view | Click Weekly tab | 7-day strip with quality indicators per day |
| 8.1.4 | Monthly view | Click Monthly tab | Calendar grid with color-coded days |

### 8.2 Dasha (`/dasha`)

| # | Test | Steps | Expected |
|---|------|-------|----------|
| 8.2.1 | Timeline | Select a profile | Colored timeline bar spanning 120 years, current period highlighted |
| 8.2.2 | Current period detail | Check detail card | Mahadasha + Antardasha with dates, progress bar, remaining time |
| 8.2.3 | Interpretation panel | Click on a dasha period | Interpretation panel with planet theme, life areas, do/don't advice |

### 8.3 Predictions (`/predictions`)

| # | Test | Steps | Expected |
|---|------|-------|----------|
| 8.3.1 | Timeframe tabs | Click Daily/Weekly/Monthly/Quarterly/Half-yearly/Yearly | Each tab loads predictions for that timeframe |
| 8.3.2 | Category cards | Check the 10 category cards | Score bar, summary, advice/caution for each life area |
| 8.3.3 | Period navigation | Click prev/next arrows | Navigates to previous/next period |

### 8.4 Compatibility (`/compatibility`)

| # | Test | Steps | Expected |
|---|------|-------|----------|
| 8.4.1 | Profile pair selector | Select two profiles | "Calculate Compatibility" button enables |
| 8.4.2 | Calculate | Click Calculate | Score gauge (X/36), 8 guna breakdown cards, Manglik section |

### 8.5 Transits (`/transits`)

| # | Test | Steps | Expected |
|---|------|-------|----------|
| 8.5.1 | Current positions | Select a profile | Planetary positions table + active transit aspects |
| 8.5.2 | Transit calendar | Scroll to calendar section | Month calendar with transit events |

### 8.6 Muhurta (`/muhurta`)

| # | Test | Steps | Expected |
|---|------|-------|----------|
| 8.6.1 | Daily view | Default | Quality badge, timeline bar with segments, period detail cards |
| 8.6.2 | Weekly view | Click Weekly | 7-day card grid with quality dots |
| 8.6.3 | Activity search | Select activity, date range, location, click "Find Auspicious Times" | Results ranked by quality score |

### 8.7 Remedies (`/remedies`)

| # | Test | Steps | Expected |
|---|------|-------|----------|
| 8.7.1 | Remedy tiers | Check tier tabs | Free / Low Cost / Medium / Premium tiers |
| 8.7.2 | Remedy cards | Expand a remedy | Instructions, timing, difficulty, cost estimate |
| 8.7.3 | Progress tracking | Click Start/Complete on a remedy | Progress updates, completed shows checkmark |

### 8.8 AI Chat (`/ai`)

| # | Test | Steps | Expected |
|---|------|-------|----------|
| 8.8.1 | Chat interface | Navigate to `/ai` | Chat input at bottom, suggestion chips if no messages |
| 8.8.2 | Send message | Type a question, press Enter | User message appears, AI responds (or error message if AI service not configured) |
| 8.8.3 | Style selector | Change interpretation style dropdown | Style changes for next message |

### 8.9 Astrologers (`/astrologers`)

| # | Test | Steps | Expected |
|---|------|-------|----------|
| 8.9.1 | Marketplace page | Navigate to `/astrologers` | "Find Your Guide" hero, search/filter bar, featured astrologer cards |
| 8.9.2 | Demo profiles | Check the astrologer cards | 6 demo profiles with gold-filled stars, tradition pills, pricing, "View Profile" buttons |
| 8.9.3 | Search/filter | Search by name or filter by tradition | Cards filter in real-time |

### 8.10 Consultations (`/consultations`)

| # | Test | Steps | Expected |
|---|------|-------|----------|
| 8.10.1 | Consultations page | Navigate to `/consultations` | "Your Sessions" with tabs, empty state with "Begin Your Journey" |
| 8.10.2 | Feature cards | Check empty state | Video Session, Live Chat, Voice Call cards with pricing |
| 8.10.3 | Browse Astrologers CTA | Click "Browse Astrologers" | Navigates to `/astrologers` |

### 8.11 Settings (`/settings` via user dropdown)

| # | Test | Steps | Expected |
|---|------|-------|----------|
| 8.11.1 | Settings page | Navigate via user dropdown | 5 tabs: Account, Subscription, Notifications, Chart Defaults, Display |
| 8.11.2 | Account tab | Check Account | Name, email, phone, ethnicity multi-select, language dropdown |
| 8.11.3 | Chart Defaults | Check Chart Defaults | Tradition, house system, ayanamsa, chart format dropdowns |
| 8.11.4 | Save preferences | Change a setting, click Save | Success feedback, preference persisted |

### 8.12 Cultural Events (`/events`)

| # | Test | Steps | Expected |
|---|------|-------|----------|
| 8.12.1 | Events page | Navigate to `/events` | Calendar with colored tradition dots, event list |
| 8.12.2 | Month navigation | Click prev/next arrows | Calendar updates |
| 8.12.3 | Ethnicity filter | If ethnicity set in settings | Events filtered to user's traditions |

---

## 9. Localization (i18n)

| # | Test | Steps | Expected |
|---|------|-------|----------|
| 9.1 | Language preference | Go to Settings > Account, select Tamil | Language saved |
| 9.2 | Today's Sky widget | Return to dashboard | Panchang terms show Tamil subscript (e.g., "Vishakha" with "விசாகம்" underneath) |
| 9.3 | Muhurta widget | Check muhurta widget | "Rahu Kaal" shows "ராகு காலம்" subscript |

---

## 10. Cross-Browser & Responsive

| # | Test | Steps | Expected |
|---|------|-------|----------|
| 10.1 | Desktop (1440px) | Full width browser | 3-column widget grid, sidebar visible |
| 10.2 | Tablet (768px) | Resize to tablet width | 2-column widget grid, sidebar may collapse |
| 10.3 | Mobile (375px) | Resize to mobile width | 1-column layout, sidebar hidden or overlay |

---

## 11. Performance & Stability

| # | Test | Steps | Expected |
|---|------|-------|----------|
| 11.1 | No hydration errors | Check console on any dashboard page | Zero "Hydration failed" errors |
| 11.2 | No reload loops | Navigate to dashboard after login | Page loads once, no repeated reloads |
| 11.3 | Widget crash isolation | If any widget API fails | Widget shows error state, dashboard stays functional |
| 11.4 | Turbopack stability | Make a code change to a widget file | HMR updates without crash (if error boundary works) |

---

## 12. API Health

| # | Test | Steps | Expected |
|---|------|-------|----------|
| 12.1 | API docs | Navigate to `http://localhost:1954/docs` | Swagger UI loads with all endpoints |
| 12.2 | Panchang endpoint | `curl http://localhost:1954/api/v1/panchang/?date=2026-04-08T06:00:00&latitude=13.08&longitude=80.27&timezone=Asia/Kolkata` | Returns panchang data with tithi, nakshatra, yoga, karana |
| 12.3 | CORS | Check browser console for CORS errors on authenticated API calls | No CORS blocking (regex allows localhost) |

---

## Known Limitations (Not Bugs)

- **Dasha/Transits widgets show "Unable to load"** when the user's default profile has no birth time/place — this is expected, the user needs to complete their profile
- **Astrologer marketplace shows demo profiles** — real astrologers have not been onboarded yet
- **Consultation history shows empty state** — no astrologers table migrated yet
- **AI Chat** requires OpenAI/Anthropic API key configured on the backend to generate responses
- **`/api/v1/me/preferences` may return 401** if Clerk JWT doesn't have `josi_user_id` yet (first login race condition) — widget system falls back to localStorage

---

## Reporting Format

For each test case, report:
```
| Test ID | Status | Notes |
|---------|--------|-------|
| 1.1     | PASS   |       |
| 1.2     | FAIL   | Console shows: [error message] |
```

Attach screenshots for any FAIL results.
