---
description: End-to-end testing of all Josi frontend pages after login
---
// turbo-all

# E2E Testing Workflow for Josi Platform

## Overview
This workflow tests all frontend pages of the Josi astrology platform (localhost:1989) after logging in. It covers navigation, data loading, UI rendering, and error detection for every dashboard page.

## Prerequisites
- The API backend must be running (Docker: `redock` or `docker-compose up -d`)
- The frontend dev server must be running on port 1989 (`npm run dev` from `web/`)
- Test credentials: `imgovind@live.com` / `Test@123`
- A verification code will be needed during login — ask the user for it

## Step 1: Login

1. Open browser to `http://localhost:1989`
2. It should redirect to `http://localhost:1989/auth/login` or show the landing page
3. Enter email: `imgovind@live.com`
4. Enter password: `Test@123`
5. A 6-digit verification code screen will appear — **ASK THE USER** for the code
6. Enter the verification code and submit
7. Should redirect to `/dashboard`
8. **Verify**: Sidebar shows "Josi" logo with "MYSTIC" badge, greeting shows user name "Govindarajan Panneerselvam"

## Step 2: Dashboard Page (`/dashboard`)

The dashboard has a configurable widget grid. Default widgets:

**Expected Widgets (in order):**
1. **Today's Sky** (full width) — Shows tithi, nakshatra, yoga, karana, vara, Rahu Kaal
2. **Chart Quick View** (1/3 width) — Shows mini birth chart or "Calculate your first chart" CTA
3. **Current Dasha** (1/3 width) — Active planetary period or "Unable to load" message
4. **AI Chat** (1/3 width) — "Ask Josi AI" with quick-action buttons
5. **Today's Muhurta** (1/2 width) — Color-coded timeline bar with Rahu Kaal, Abhijit times
6. **Western Transit** (1/2 width) — Western transit alert or "Unable to load" message
7. **Latest Reading** (1/3 width) — Latest AI reading or empty state
8. **BaZi Summary** (1/3 width) — Chinese four pillars or empty state

**Checks:**
- [ ] Page loads without JS errors (no white screen)
- [ ] All widget cards render with proper backgrounds (dark cards with borders)
- [ ] WidgetErrorBoundary doesn't show (no "Something went wrong" in any widget)
- [ ] "+ Add Widget" button visible in top right
- [ ] Sidebar navigation is functional
- [ ] User dropdown at bottom of sidebar works

## Step 3: Charts Page (`/charts`)

**Navigation:** Click "Charts" in sidebar

**Expected UI:**
- Page title "Charts" or "Birth Charts"
- Filter controls (tradition filter, search)
- Grid or list view toggle
- Either chart cards or an empty state "No charts yet" with CTA

**Checks:**
- [ ] Page loads without errors
- [ ] Filter/search UI renders
- [ ] View toggle (grid/list) works
- [ ] If charts exist, cards show chart name, tradition badge, date

### Sub-page: New Chart (`/charts/new`)
- Click "New Chart" or "+" button
- Birth details form should render: Name, Date, Time, Location fields
- Location picker should load (uses geocoding API)
- **Don't submit** — just verify form renders

### Sub-page: Chart Detail (`/charts/[chartId]`)
- If charts exist, click on one
- Should show: chart visualization, tabs (Overview, Planets, Houses, Aspects)
- Quick info panel on the side
- Each tab should load without errors

## Step 4: Profiles Page (`/persons`)

**Navigation:** Click "Profiles" in sidebar

**Expected UI:**
- Page title "Profiles" or "People"
- Person cards with name, birth info
- "Add Profile" button
- Each person card may show mini chart

**Checks:**
- [ ] Page loads, person list renders
- [ ] Person cards display correctly
- [ ] Add/edit modal opens when clicking add button

## Step 5: AI Insights Page (`/ai`)

**Navigation:** Click "AI Insights" in sidebar

**Expected UI:**
- Chat interface with message input
- Chart context sidebar (if charts exist)
- Style selector for interpretation types
- Previous conversation history (if any)

**Checks:**
- [ ] Page loads without errors
- [ ] Chat input is functional
- [ ] Chart context sidebar renders (or shows empty state)
- [ ] **Don't send messages** — just verify UI renders

## Step 6: Compatibility Page (`/compatibility`)

**Navigation:** Click "Compatibility" in sidebar

**Expected UI:**
- Two person selector dropdowns
- If persons selected: Guna Milan score gauge, Manglik section, detailed analysis
- If no persons: empty state prompting to select two profiles

**Checks:**
- [ ] Page loads without errors
- [ ] Person selectors render
- [ ] If profiles exist, selecting two should trigger analysis
- [ ] Score gauge and Guna card components render

## Step 7: Transits Page (`/transits`)

**Navigation:** Click "Transits" in sidebar

**Expected UI:**
- Person selector (needs a chart/person)
- Positions table showing current planetary positions
- Transit aspects section
- Transit calendar
- Transit forecast
- Summary cards

**Checks:**
- [ ] Page loads without errors
- [ ] If a person with chart exists, transit data loads
- [ ] Positions table renders with planet rows
- [ ] Transit calendar shows current month
- [ ] Forecast section renders

## Step 8: Panchang Page (`/panchang`)

**Navigation:** Click "Panchang" in sidebar

**Expected UI:**
- Date navigation (prev/next day arrows)
- Five Elements Card (Tithi, Nakshatra, Yoga, Karana, Vara)
- Sun & Moon Card (rise/set/transit times)
- Quality Summary Card
- Timing Windows Card (Rahu Kaal, etc.)
- Weekly strip at bottom
- Monthly calendar view option

**Checks:**
- [ ] Page loads, panchang data fetches for today
- [ ] Five elements display with correct data
- [ ] Date navigation works (prev/next)
- [ ] Weekly strip shows 7 days
- [ ] Monthly calendar renders when toggled

## Step 9: Dasha Page (`/dasha`)

**Navigation:** Click "Dasha" in sidebar

**Expected UI:**
- Person selector
- Dasha timeline/tree visualization
- Current period highlighted
- Dasha interpretation panel
- Sub-period details

**Checks:**
- [ ] Page loads without errors
- [ ] If a person with chart exists, dasha data loads
- [ ] Dasha components render (tree, interpretation panel)
- [ ] Period navigation/expansion works

## Step 10: Muhurta Page (`/muhurta`) ⚠️ RECENTLY CHANGED

**Navigation:** Click "Muhurta" in sidebar

**Expected UI:**
- Hero section with "Muhurta" title and description
- Timeframe selector: Daily / Weekly / Monthly tabs
- Date navigation arrows with date label
- Daily view (default): period cards with color-coded quality
- Activity search section at bottom

**Daily View Checks:**
- [ ] Periods load from API (`/api/v1/panchang/` endpoint)
- [ ] Color-coded cards (green=auspicious, red=inauspicious, neutral)
- [ ] Each period shows name, time range, quality badge, ruling planet
- [ ] Date navigation works

**Weekly View Checks:**
- [ ] Switch to "Weekly" tab
- [ ] Shows 7-day grid with quality indicators per day
- [ ] Week navigation arrows work

**Monthly View Checks:**
- [ ] Switch to "Monthly" tab
- [ ] Calendar grid with quality dots per day
- [ ] Clicking a day switches to Daily view for that date
- [ ] Month navigation works

**Activity Search Checks:**
- [ ] Activity search section renders below the view
- [ ] Dropdown loads activities from `/api/v1/muhurta/activities`
- [ ] Selecting an activity and searching shows muhurta windows

## Step 11: Cultural Events Page (`/events`)

**Navigation:** Click "Cultural Events" in sidebar

**Expected UI:**
- "Cultural Events & Festivals" title
- Monthly calendar with event dots (color-coded by tradition)
- Category filter pills: Hindu, Sikh, Jain, Christian
- Event count summary (e.g., "8 EVENTS THIS MONTH")
- Event detail cards with: name, date, description, Significance section, Rituals & Observances tags, auspicious marker
- Month navigation arrows

**Checks:**
- [ ] Page loads without errors
- [ ] Calendar renders current month with event indicator dots
- [ ] Category filters are visible and clickable
- [ ] Event detail cards show below calendar
- [ ] Month navigation works

## Step 12: Astrologers Page (`/astrologers`)

**Navigation:** Click "Astrologers" in sidebar

**Expected UI:**
- Search astrologers interface (or empty state)
- Astrologer cards with name, specialties, rating

**Checks:**
- [ ] Page loads without errors
- [ ] UI renders (may show "No astrologers found" — that's OK)
- [ ] No crashes from removed astrologer widget code

## Step 13: Consultations Page (`/consultations`)

**Navigation:** Click "Consultations" in sidebar

**Expected UI:**
- List of user's consultations (or empty state)
- Each consultation shows astrologer, status, date

**Checks:**
- [ ] Page loads without errors
- [ ] Consultations list or empty state renders

## Step 14: Settings Page (`/settings`)

**Navigation:** Navigate to `/settings`

> **NOTE:** The `/api/v1/me` endpoint must return `ResponseModel` format (`{success, message, data}`).
> A previous bug had it returning raw `UserResponse` which caused infinite "Loading settings..." state.

**Expected UI — Tabs:**
1. **Account** — Full Name, Email (managed by auth provider), Phone, Ethnicity/Background selector, Save Changes button
2. **Subscription** — Current plan name, active status, usage stats
3. **Notifications** — Toggles for Daily Predictions, Transit Alerts, Dasha Period Changes, Consultation Reminders
4. **Chart Defaults** — Default Tradition (Vedic/Western/Chinese), House System, Ayanamsa, Chart Format dropdowns, Save Changes button
5. **Display** — Dark/Light theme cards with Save Theme button, Dashboard Layout section with Reset Widget Layout button

**Checks:**
- [ ] Page loads with tab navigation (5 tabs visible)
- [ ] Account tab shows user data populated from API (not "Loading settings...")
- [ ] Each tab renders its form/info without errors when clicked
- [ ] Subscription tab loads subscription info and usage
- [ ] Chart Defaults shows current values in dropdowns
- [ ] Display tab shows theme selector and layout reset
- [ ] **Don't save changes** — just verify UI renders

## Step 15: Console Error Check

At the end of all navigation, open browser console and check for:
- [ ] No unhandled promise rejections
- [ ] No React errors (hydration mismatches shouldn't occur since dashboard is client-only)
- [ ] No 500-series API errors
- [ ] 404 API errors are acceptable for missing data (e.g., no charts yet)

## Reporting

After completing all checks, create a summary with:
1. **Pages that loaded successfully** (✅)
2. **Pages with issues** (❌) — describe the error
3. **Pages with warnings** (⚠️) — non-critical issues
4. **Screenshots** of any errors found

## Page Route Reference

| Sidebar Item      | Route                       | API Dependencies                                    |
|-------------------|-----------------------------|-----------------------------------------------------|
| Dashboard         | `/dashboard`                | `/panchang/`, `/persons/me`, `/ai/history`           |
| Charts            | `/charts`                   | `/charts/person/{id}`, `/persons/`                   |
| Chart Detail      | `/charts/[chartId]`         | `/charts/{id}`, `/persons/{id}`                      |
| New Chart         | `/charts/new`               | `/location/geocode` (on submit)                      |
| Profiles          | `/persons`                  | `/persons/`                                          |
| AI Insights       | `/ai`                       | `/ai/interpret`, `/ai/history`                       |
| Compatibility     | `/compatibility`            | `/persons/`, `/compatibility/calculate` (on submit)  |
| Transits          | `/transits`                 | `/transits/current/{id}`, `/transits/forecast/{id}`  |
| Panchang          | `/panchang`                 | `/panchang/?date=...`                                |
| Dasha             | `/dasha`                    | `/dasha/vimshottari/{id}`                            |
| Muhurta           | `/muhurta`                  | `/panchang/`, `/muhurta/find-muhurta`, `/muhurta/activities`, `/muhurta/monthly-calendar` |
| Cultural Events   | `/events`                   | TBD                                                  |
| Astrologers       | `/astrologers`              | `/astrologers/search`                                |
| Consultations     | `/consultations`            | `/consultations/my-consultations`                    |
| Settings          | `/settings`                 | `/me`, `/me/preferences`, `/me/subscription`, `/me/usage` |

## Widget Reference (Dashboard)

| Widget            | Type Key             | API Endpoint                           |
|-------------------|----------------------|----------------------------------------|
| Today's Sky       | `todays-sky`         | `/panchang/?date=...`                  |
| Muhurta Timeline  | `muhurta-timeline`   | `/panchang/?date=...`                  |
| Chart Quick View  | `chart-quick-view`   | `/persons/me`, `/charts/person/{id}`   |
| Current Dasha     | `current-dasha`      | `/persons/me`, `/dasha/vimshottari/{id}` |
| AI Chat           | `ai-chat-access`     | None (just UI)                         |
| Latest Reading    | `latest-reading`     | `/ai/history?limit=1`                  |
| BaZi Summary      | `bazi-summary`       | `/persons/me`, `/charts/person/{id}`   |
| Western Transit   | `western-transit`    | `/persons/me`, `/transits/current/{id}` |
