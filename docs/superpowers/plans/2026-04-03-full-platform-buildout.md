# Full Platform Buildout Plan

**Date**: 2026-04-03
**Status**: Ready for execution
**Scope**: Wire up all backend APIs to frontend, replace all "Coming Soon" placeholders, build missing features

---

## Current State Summary

### Backend (mostly complete)
- **Working APIs**: Panchang, Dasha (Vimshottari/Yogini/Chara), Compatibility (Ashtakoota + Synastry), Transits (current + forecast), Predictions (daily/monthly/yearly), Remedies (full + gemstones + color therapy + numerology), Muhurta (find + rahu kaal + monthly calendar + best times today + activities), AI (interpret + neural pathway + styles + providers), Astrologers (register + search + profile + reviews + specializations), Consultations (book + list + detail + respond + messages + cancel + types + pending)
- **Missing APIs**: `GET/PUT /api/v1/me/preferences`, predictions weekly/quarterly/half-yearly, prediction 10-category structure

### Frontend (placeholders everywhere)
- **Working pages**: Dashboard (widget grid with mock data), Charts listing, Chart detail (Overview/Planets tabs work, Houses partial, Aspects "coming soon"), Profiles, Chart calculator, Login/Sign-up, Pricing, Developer portal
- **Coming Soon placeholders**: Panchang, Dasha, Predictions, Remedies, Compatibility, Transits, AI Insights, Settings, Consultations
- **Missing pages (404)**: Muhurta, Astrologers
- **Dashboard widgets**: All 9 widgets exist but show hardcoded mock data

### Bugs
1. Dashboard `page.tsx` line 58: `data.data.chart_id` assumes object but API returns array
2. Chart detail Aspects tab: shows "coming soon" placeholder
3. Sidebar links for `/muhurta` and `/astrologers` point to pages that don't exist

---

## Task Inventory

### Section N: Bug Fixes
- **T1**: Fix chart creation redirect in dashboard (array vs object) — `web/app/(dashboard)/dashboard/page.tsx` line 58
- **T2**: Fix Aspects tab in chart detail — replace ComingSoonCard with actual aspects table — `web/app/(dashboard)/charts/[chartId]/page.tsx` line 750
- **T3**: Create Muhurta page route (currently 404) — `web/app/(dashboard)/muhurta/page.tsx`
- **T4**: Create Astrologers page route (currently 404) — `web/app/(dashboard)/astrologers/page.tsx`

### Section A: Dashboard Widgets — Connect to Real APIs
- **T5**: Today's Sky widget — wire to `GET /api/v1/panchang/` with user's location
- **T6**: Current Dasha widget — wire to `GET /api/v1/dasha/vimshottari/{person_id}` using default profile
- **T7**: Chart Quick View widget — wire to `GET /api/v1/charts/person/{person_id}` for latest chart
- **T8**: Muhurta Timeline widget — wire to `POST /api/v1/panchang/muhurta` or `GET /api/v1/muhurta/best-times-today`
- **T9**: Western Transit widget — wire to `GET /api/v1/transits/current/{person_id}`
- **T10**: BaZi Summary widget — wire to chart data with `chart_type=chinese`
- **T11**: AI Chat Access widget — wire navigation to /ai page + show last interpretation if available
- **T12**: Available Astrologers widget — wire to `GET /api/v1/astrologers/search`

### Section B: Widget Library System
- **T13**: Add `react-grid-layout` for drag-and-drop widget repositioning
- **T14**: Backend: Add `GET/PUT /api/v1/me/preferences` endpoint for persisting widget layout and user preferences
- **T15**: Extend AddWidgetModal with full catalog, preview thumbnails, tradition-based smart defaults
- **T16**: Persist widget layout to backend via preferences API (replace localStorage)

### Section C: Panchang Page
- **T17**: Build daily Panchang view — full 5-element display with timing windows
- **T18**: Build weekly Panchang strip — 7-day horizontal view with key elements per day
- **T19**: Build monthly Panchang calendar — grid with color-coded quality indicators
- **T20**: Location selector component — use user's birth location or current location via browser geolocation

### Section D: Dasha Timeline Page
- **T21**: Build Dasha timeline visualization — Mahadasha > Antardasha > Pratyantardasha hierarchy
- **T22**: Current period highlight with progress bar and upcoming transitions
- **T23**: Click-to-expand interpretation panel for any dasha period

### Section E: Predictions System
- **T24**: Backend: Add `GET /api/v1/predictions/weekly/{person_id}` endpoint
- **T25**: Backend: Add `GET /api/v1/predictions/quarterly/{person_id}` endpoint
- **T26**: Backend: Add `GET /api/v1/predictions/half-yearly/{person_id}` endpoint
- **T27**: Backend: Refactor all prediction endpoints to return 10 life categories (Career, Finance, Love, Family, Health, Education, Spirituality, Travel, Social, Legal)
- **T28**: Backend: Fix bug in daily predictions — `astrology_astrology_calculator` typo on line 89 of prediction_controller.py
- **T29**: Frontend: Build predictions page with timeframe tabs (Daily/Weekly/Monthly/Quarterly/Half-yearly/Yearly)
- **T30**: Frontend: Build prediction detail view — per-category cards with AI chat integration

### Section F: Remedies Page
- **T31**: Build remedies page — tiered display (Free/Low/Medium/High) with remedy cards
- **T32**: Build remedy detail view — instructions, timing, rationale, difficulty, cost estimate
- **T33**: Build remedy progress tracker — start/complete/skip actions per remedy
- **T34**: Backend: Add remedy progress tracking model and endpoints (`POST /api/v1/remedies/{person_id}/track`)

### Section G: Compatibility Page
- **T35**: Build profile pair selector — pick two profiles from user's person list
- **T36**: Build Ashtakoota score display — X/36 gauge with 8 guna breakdown cards
- **T37**: Build Manglik Dosha indicator and detailed per-guna interpretation
- **T38**: Build synastry chart overlay visualization

### Section H: Transits Page
- **T39**: Build current planetary positions table/wheel
- **T40**: Build active transit aspects list — natal chart overlay
- **T41**: Build upcoming transits calendar — month view with transit events
- **T42**: Build transit forecast timeline — significant events over next 30/90/180/365 days

### Section I: Muhurta Page (Full Build)
- **T43**: Build activity selector with supported activities from `GET /api/v1/muhurta/activities`
- **T44**: Build date range picker and muhurta search results display
- **T45**: Build monthly auspicious calendar view (using `POST /api/v1/muhurta/monthly-calendar`)
- **T46**: Build today's muhurta summary panel (using `GET /api/v1/muhurta/best-times-today`)

### Section J: Consultations and Astrologers Pages (Full Build)
- **T47**: Build astrologer directory — search, filter by specialization/language/tradition, profile cards
- **T48**: Build astrologer profile detail page — reviews, availability, specializations
- **T49**: Build booking flow — select astrologer, pick consultation type, choose time, confirm
- **T50**: Build consultation history page — past/upcoming consultations with status
- **T51**: Build in-consultation messaging interface

### Section K: Settings Page
- **T52**: Build account details section — display/edit from `/me` endpoint
- **T53**: Build subscription management section — current tier, usage, upgrade CTA
- **T54**: Build notification preferences section
- **T55**: Build default chart settings — tradition, house system, ayanamsa selection
- **T56**: Build widget layout reset and theme preference toggle

### Section L: Cultural Events and Ethnicity
- **T57**: Backend: Add `ethnicity` field (JSON array) to User model + migration
- **T58**: Frontend: Add ethnicity capture in settings/onboarding profile section
- **T59**: Backend: Build cultural events calendar endpoint based on ethnicity + location
- **T60**: Frontend: Build cultural events calendar page/widget

### Section M: AI Chat Page
- **T61**: Build chat interface — message input, conversation history, streaming responses
- **T62**: Build chart context sidebar — shows user's active chart data, current dasha, transits
- **T63**: Wire to `POST /api/v1/ai/interpret` with conversation threading
- **T64**: Build interpretation style selector (5 styles from `GET /api/v1/ai/styles`)

### Section Shared: Shared Components
- **T65**: Build ProfileSelector component — reusable dropdown to select a person from user's profiles (needed by Dasha, Transits, Predictions, Remedies, Compatibility)
- **T66**: Build LocationPicker component — reusable location input with geocoding (needed by Panchang, Muhurta)
- **T67**: Build TimeframeSelector component — reusable tab bar for daily/weekly/monthly/etc. (needed by Predictions, Panchang)

---

## Dependency Graph and Execution Waves

### Wave 0: Critical Bug Fixes and Shared Infrastructure (parallel)
All items have no prerequisites. Mix of quick fixes and foundational components.

| Task | Description | Size | Agent | Prereqs |
|------|-------------|------|-------|---------|
| T1 | Fix chart creation redirect bug (dashboard `data.data.chart_id` — API returns array) | S | frontend | none |
| T2 | Fix Aspects tab in chart detail (replace "coming soon" with aspects table) | M | frontend | none |
| T3 | Create Muhurta page route stub (eliminate 404) | S | frontend | none |
| T4 | Create Astrologers page route stub (eliminate 404) | S | frontend | none |
| T28 | Fix `astrology_astrology_calculator` typo in prediction_controller.py | S | backend | none |
| T14 | Backend: Add `GET/PUT /api/v1/me/preferences` endpoint | M | backend | none |
| T65 | Build ProfileSelector shared component | M | frontend | none |
| T66 | Build LocationPicker shared component | M | frontend | none |
| T67 | Build TimeframeSelector shared component | S | frontend | none |
| T20 | Build location selector component (browser geolocation + saved locations) | M | frontend | none |

**Parallelism**: All 10 tasks run simultaneously. 5 frontend agents, 2 backend agents.

---

### Wave 1: Dashboard Widgets + Backend Extensions (parallel)
Wire existing widgets to real APIs. Also begin backend work for missing endpoints.

| Task | Description | Size | Agent | Prereqs |
|------|-------------|------|-------|---------|
| T5 | Today's Sky widget — wire to Panchang API | M | frontend | T66 |
| T6 | Current Dasha widget — wire to Vimshottari API | M | frontend | T65 |
| T7 | Chart Quick View widget — wire to charts API | M | frontend | T65 |
| T8 | Muhurta Timeline widget — wire to muhurta best-times-today API | M | frontend | T66 |
| T9 | Western Transit widget — wire to transits API | M | frontend | T65 |
| T10 | BaZi Summary widget — wire to Chinese chart data | S | frontend | T65 |
| T11 | AI Chat Access widget — wire navigation + last reading preview | S | frontend | none |
| T12 | Available Astrologers widget — wire to astrologer search API | S | frontend | none |
| T24 | Backend: Add weekly predictions endpoint | M | backend | T28 |
| T25 | Backend: Add quarterly predictions endpoint | M | backend | T28 |
| T26 | Backend: Add half-yearly predictions endpoint | M | backend | T28 |
| T27 | Backend: Refactor predictions to 10 life categories | L | backend | T28 |
| T34 | Backend: Remedy progress tracking model + endpoints | M | backend | none |
| T57 | Backend: Add ethnicity field to User model + migration | S | backend | none |
| T59 | Backend: Cultural events calendar endpoint | L | backend | T57 |

**Parallelism**: Up to 8 frontend agents + 4 backend agents. Frontend agents need Wave 0 shared components. Backend work is independent.

---

### Wave 2: Feature Pages — Tier 1 (parallel, high-value pages)
Build the most impactful feature pages. Each agent owns one full page.

| Task | Description | Size | Agent | Prereqs |
|------|-------------|------|-------|---------|
| T17 | Panchang daily view | L | frontend | T66, T20 |
| T21+T22 | Dasha timeline visualization + progress bar | L | frontend | T65 |
| T29 | Predictions page with timeframe tabs | L | frontend | T65, T67, T24-T27 |
| T35+T36 | Compatibility page: pair selector + Ashtakoota score | L | frontend | T65 |
| T39+T40 | Transits page: positions table + active aspects | L | frontend | T65 |
| T43+T44+T46 | Muhurta page: activity selector + search + today panel | L | frontend | T3, T66 |
| T31+T32 | Remedies page: tiered display + detail view | L | frontend | T65 |
| T52+T53 | Settings page: account + subscription sections | M | frontend | T14 |
| T61+T63 | AI Chat page: chat interface + interpret API wiring | L | frontend | none |

**Parallelism**: 9 frontend agents, each building one complete page. Backend work from Wave 1 must be done for Predictions.

---

### Wave 3: Feature Pages — Tier 2 (parallel, secondary pages)
Complete remaining page sections and more complex features.

| Task | Description | Size | Agent | Prereqs |
|------|-------------|------|-------|---------|
| T18 | Panchang weekly strip view | M | frontend | T17 |
| T19 | Panchang monthly calendar view | M | frontend | T17 |
| T23 | Dasha click-to-expand interpretation panel | M | frontend | T21+T22 |
| T30 | Prediction detail view with per-category cards | M | frontend | T29 |
| T33 | Remedy progress tracker UI | M | frontend | T31, T34 |
| T37 | Compatibility: Manglik dosha + per-guna interpretation | M | frontend | T35+T36 |
| T38 | Compatibility: Synastry chart overlay | L | frontend | T35+T36 |
| T41 | Transits calendar (month view) | M | frontend | T39+T40 |
| T42 | Transit forecast timeline | M | frontend | T39+T40 |
| T45 | Muhurta monthly auspicious calendar | M | frontend | T43 |
| T47 | Astrologer directory page — search + filter + cards | L | frontend | T4 |
| T50 | Consultation history page | M | frontend | none |
| T54+T55+T56 | Settings: notifications + chart defaults + widget reset + theme | M | frontend | T52 |
| T62 | AI Chat: chart context sidebar | M | frontend | T61 |
| T64 | AI Chat: interpretation style selector | S | frontend | T61 |

**Parallelism**: Up to 15 frontend agents.

---

### Wave 4: Advanced Features + Polish (parallel)
Remaining complex features and integration work.

| Task | Description | Size | Agent | Prereqs |
|------|-------------|------|-------|---------|
| T13 | Add react-grid-layout for drag-and-drop widgets | L | frontend | T5-T12 |
| T15 | Extend AddWidgetModal with full catalog + previews | M | frontend | T13 |
| T16 | Persist widget layout to backend preferences API | M | frontend | T13, T14 |
| T48 | Astrologer profile detail page | M | frontend | T47 |
| T49 | Booking flow — select astrologer + pick time + confirm | L | frontend | T48 |
| T51 | In-consultation messaging interface | L | frontend | T50 |
| T58 | Frontend: ethnicity capture in settings | S | frontend | T52, T57 |
| T60 | Frontend: cultural events calendar | M | frontend | T59, T58 |

**Parallelism**: 8 frontend agents.

---

## Wave Summary

| Wave | Name | Tasks | Parallel Agents | Est. Time |
|------|------|-------|-----------------|-----------|
| 0 | Bug Fixes + Shared Infrastructure | T1, T2, T3, T4, T14, T20, T28, T65, T66, T67 | 7 | 1-3 hrs |
| 1 | Dashboard Widgets + Backend Extensions | T5-T12, T24-T27, T34, T57, T59 | 12 | 2-4 hrs |
| 2 | Feature Pages Tier 1 | T17, T21-T22, T29, T31-T32, T35-T36, T39-T40, T43-T44+T46, T52-T53, T61+T63 | 9 | 3-8 hrs |
| 3 | Feature Pages Tier 2 | T18-T19, T23, T30, T33, T37-T38, T41-T42, T45, T47, T50, T54-T56, T62, T64 | 15 | 2-6 hrs |
| 4 | Advanced Features + Polish | T13, T15-T16, T48-T49, T51, T58, T60 | 8 | 3-8 hrs |

**Total tasks**: 67
**Critical path**: Wave 0 (shared components) -> Wave 1 (widgets + backend) -> Wave 2 (pages) -> Wave 3 (enhancements) -> Wave 4 (advanced)
**Estimated total wall-clock time with max parallelism**: 11-29 hours across 5 waves

---

## Detailed Task Specifications

### T1: Fix Chart Creation Redirect Bug
**File**: `web/app/(dashboard)/dashboard/page.tsx` line 55-62
**Problem**: `data.data.chart_id` assumes the API returns a single chart object, but `/api/v1/charts/calculate` returns an array of charts.
**Fix**: Change to `const charts = Array.isArray(data.data) ? data.data : [data.data]; const chartId = charts[0]?.chart_id;`
**Size**: S | **Agent**: frontend

### T2: Fix Aspects Tab in Chart Detail
**File**: `web/app/(dashboard)/charts/[chartId]/page.tsx` ~line 750
**Problem**: Aspects tab shows "Aspects analysis coming soon" ComingSoonCard.
**Fix**: Build an aspects table component showing planet1, aspect type, planet2, orb, applying/separating. Data is already in `chart.aspects` or can be computed from planet longitudes.
**Size**: M | **Agent**: frontend

### T3: Create Muhurta Page Route
**File**: Create `web/app/(dashboard)/muhurta/page.tsx`
**Action**: Initially a stub page (not ComingSoon) that will be filled in T43-T46. For now, show a basic page layout with "Muhurta" heading and placeholder sections.
**Size**: S | **Agent**: frontend

### T4: Create Astrologers Page Route
**File**: Create `web/app/(dashboard)/astrologers/page.tsx`
**Action**: Initially a stub page that will be filled in T47. Basic layout with "Astrologers" heading.
**Size**: S | **Agent**: frontend

### T5: Today's Sky Widget — Wire to Panchang API
**File**: `web/components/dashboard/widgets/todays-sky.tsx`
**Current**: Hardcoded "Shukla Chaturthi in Rohini" text
**Target**: Call `GET /api/v1/panchang/?date={now}&latitude={lat}&longitude={lng}&timezone={tz}` using user's location. Display actual tithi, nakshatra, yoga, karana, vara from response.
**Dependencies**: T66 (LocationPicker — need user's location)
**Size**: M | **Agent**: frontend

### T6: Current Dasha Widget
**File**: `web/components/dashboard/widgets/current-dasha.tsx`
**Target**: Call `GET /api/v1/dasha/vimshottari/{person_id}` using the user's default profile. Show current Mahadasha planet, Antardasha planet, progress percentage, and end date.
**Dependencies**: T65 (ProfileSelector — need default person_id)
**Size**: M | **Agent**: frontend

### T7: Chart Quick View Widget
**File**: `web/components/dashboard/widgets/chart-quick-view.tsx`
**Target**: Fetch user's most recent chart. Show Sun sign, Moon sign, Ascendant, and a mini South Indian chart diagram.
**Dependencies**: T65
**Size**: M | **Agent**: frontend

### T8: Muhurta Timeline Widget
**File**: `web/components/dashboard/widgets/muhurta-timeline.tsx`
**Target**: Call `GET /api/v1/muhurta/best-times-today?latitude={lat}&longitude={lng}&timezone={tz}`. Show today's auspicious/inauspicious periods as a horizontal timeline.
**Dependencies**: T66
**Size**: M | **Agent**: frontend

### T9: Western Transit Widget
**File**: `web/components/dashboard/widgets/western-transit.tsx`
**Target**: Call `GET /api/v1/transits/current/{person_id}`. Show active major transits with planet, aspect, and intensity.
**Dependencies**: T65
**Size**: M | **Agent**: frontend

### T10: BaZi Summary Widget
**File**: `web/components/dashboard/widgets/bazi-summary.tsx`
**Target**: If user has a Chinese chart, display Four Pillars summary. Otherwise show "Create a Chinese chart to see your BaZi".
**Dependencies**: T65
**Size**: S | **Agent**: frontend

### T11: AI Chat Access Widget
**File**: `web/components/dashboard/widgets/ai-chat-access.tsx`
**Target**: Quick-ask input that navigates to /ai with pre-filled question. Show the last AI reading snippet if available.
**Size**: S | **Agent**: frontend

### T12: Available Astrologers Widget
**File**: `web/components/dashboard/widgets/available-astrologers.tsx`
**Target**: Call `GET /api/v1/astrologers/search?limit=3`. Show 3 astrologer cards with name, specialization, rating. Link to /astrologers.
**Size**: S | **Agent**: frontend

### T13: Drag-and-Drop Widget Grid
**File**: `web/components/dashboard/widget-grid.tsx`
**Action**: Replace CSS grid with `react-grid-layout`. Each widget becomes a resizable, draggable grid item. Maintain size mapping (full/half/third to grid columns).
**Size**: L | **Agent**: frontend

### T14: Backend: User Preferences Endpoint
**Files**: `src/josi/api/v1/controllers/me_controller.py`
**Action**: Add `GET /api/v1/me/preferences` and `PUT /api/v1/me/preferences`. Uses existing `User.preferences` JSON field. Support nested keys like `dashboard.widget_layout`, `chart.default_tradition`, `chart.default_ayanamsa`, `chart.default_house_system`, `theme`.
**Size**: M | **Agent**: backend

### T15: Extended AddWidgetModal
**File**: `web/components/dashboard/add-widget-modal.tsx`
**Action**: Add widget previews/thumbnails, better categorization, search/filter. Show which widgets are compatible with user's chart traditions.
**Dependencies**: T13
**Size**: M | **Agent**: frontend

### T16: Persist Widget Layout to Backend
**File**: `web/components/dashboard/widget-grid.tsx`
**Action**: Replace localStorage persistence with API calls to `PUT /api/v1/me/preferences` for layout data. Load on mount from `GET /api/v1/me/preferences`.
**Dependencies**: T13, T14
**Size**: M | **Agent**: frontend

### T17: Panchang Daily View
**File**: Replace content in `web/app/(dashboard)/panchang/page.tsx`
**Action**: Build full daily panchang display. Show all 5 elements (Tithi, Nakshatra, Yoga, Karana, Vara) with end times, percentages, deities. Include sunrise/sunset, Rahu Kaal, auspicious periods. Use `GET /api/v1/panchang/` endpoint.
**Dependencies**: T66, T20
**Size**: L | **Agent**: frontend

### T18: Panchang Weekly Strip
**File**: Add component within panchang page
**Action**: 7-day horizontal strip showing key panchang elements per day. Each day shows tithi name + nakshatra + general quality. Clicking a day loads full daily view.
**Dependencies**: T17
**Size**: M | **Agent**: frontend

### T19: Panchang Monthly Calendar
**File**: Add component within panchang page
**Action**: Calendar grid where each day cell shows color-coded quality (green=auspicious, yellow=mixed, red=inauspicious). Click opens daily detail. Uses batch panchang calls or muhurta monthly calendar.
**Dependencies**: T17
**Size**: M | **Agent**: frontend

### T20: Location Selector Component
**File**: Create shared component
**Action**: Component that detects user's current location via browser geolocation, or allows selecting from saved locations (birth location from profile). Returns lat/lng/timezone. Used by Panchang, Muhurta, and widgets.
**Size**: M | **Agent**: frontend

### T21+T22: Dasha Timeline Visualization
**File**: Replace content in `web/app/(dashboard)/dasha/page.tsx`
**Action**: Build visual timeline. Mahadasha periods as colored horizontal bars spanning life duration. Antardasha shown as subdivisions within current Mahadasha. Pratyantardasha shown when expanded. Current period highlighted with a progress bar showing percentage elapsed + remaining days. Upcoming transitions listed with dates.
**Dependencies**: T65
**Size**: L | **Agent**: frontend

### T23: Dasha Interpretation Panel
**File**: Component within dasha page
**Action**: Clicking any dasha period opens a side panel or modal with interpretation. Shows: planet ruling the period, life areas affected, general theme, do/don't advice. Could use AI interpretation if available, otherwise static content from backend.
**Dependencies**: T21+T22
**Size**: M | **Agent**: frontend

### T24: Backend: Weekly Predictions Endpoint
**File**: `src/josi/api/v1/controllers/prediction_controller.py`
**Action**: Add `GET /api/v1/predictions/weekly/{person_id}?week_start={date}`. Aggregate daily predictions + planet sign changes during the week. Return 10 life categories.
**Dependencies**: T28
**Size**: M | **Agent**: backend

### T25: Backend: Quarterly Predictions Endpoint
**File**: `src/josi/api/v1/controllers/prediction_controller.py`
**Action**: Add `GET /api/v1/predictions/quarterly/{person_id}?quarter={1-4}&year={year}`. Analyze Saturn/Jupiter/Rahu movements + dasha context.
**Dependencies**: T28
**Size**: M | **Agent**: backend

### T26: Backend: Half-Yearly Predictions Endpoint
**File**: `src/josi/api/v1/controllers/prediction_controller.py`
**Action**: Add `GET /api/v1/predictions/half-yearly/{person_id}?half={1-2}&year={year}`. Major planetary period shifts.
**Dependencies**: T28
**Size**: M | **Agent**: backend

### T27: Backend: Refactor Predictions to 10 Categories
**File**: `src/josi/api/v1/controllers/prediction_controller.py`
**Action**: Refactor `_generate_daily_predictions` and monthly/yearly to return predictions across 10 life categories: Career (houses 10,6), Finance (2,11), Love (7,5), Family (4), Health (6,1), Education (5,4), Spirituality (12,9), Travel (3,9,12), Social (11,1), Legal (6,8). Each category has a score (1-10), summary, and detailed text.
**Dependencies**: T28
**Size**: L | **Agent**: backend

### T28: Fix Prediction Controller Typo
**File**: `src/josi/api/v1/controllers/prediction_controller.py` line 89
**Problem**: `astrology_astrology_calculator` should be `astrology_calculator`
**Fix**: Simple find-replace
**Size**: S | **Agent**: backend

### T29: Predictions Page Frontend
**File**: Replace content in `web/app/(dashboard)/predictions/page.tsx`
**Action**: Build tabbed interface: Daily | Weekly | Monthly | Quarterly | Half-yearly | Yearly. Each tab calls the corresponding prediction API. Show person selector at top. Daily tab is default. Each prediction shows 10 category cards with scores and summaries.
**Dependencies**: T65, T67, T24-T27
**Size**: L | **Agent**: frontend

### T30: Prediction Detail View
**File**: Component within predictions page
**Action**: Clicking a category card expands to show full prediction text + "Ask AI" button that opens chat with context pre-loaded.
**Dependencies**: T29
**Size**: M | **Agent**: frontend

### T31+T32: Remedies Page
**File**: Replace content in `web/app/(dashboard)/remedies/page.tsx`
**Action**: Build tiered remedy display. Call `GET /api/v1/remedies/{person_id}`. Group remedies into tiers: Free (mantras, meditation), Low (temple visits, donations), Medium (home pujas, yantras), High (gemstones, elaborate rituals). Each remedy card shows: name, description, when to do, why it helps, difficulty badge, cost estimate.
**Dependencies**: T65
**Size**: L | **Agent**: frontend

### T33: Remedy Progress Tracker UI
**File**: Component within remedies page
**Action**: Each remedy has Start/Complete/Skip buttons. Track state locally + persist to backend via `POST /api/v1/remedies/{person_id}/track`. Show completion percentage per tier.
**Dependencies**: T31, T34
**Size**: M | **Agent**: frontend

### T34: Backend: Remedy Progress Tracking
**Files**: New model + controller endpoints
**Action**: Create `remedy_progress` table (user_id, person_id, remedy_type, remedy_name, status [not_started/in_progress/completed/skipped], started_at, completed_at). Add `POST /api/v1/remedies/{person_id}/track` and `GET /api/v1/remedies/{person_id}/progress`.
**Size**: M | **Agent**: backend

### T35+T36: Compatibility Page — Pair Selector + Score
**File**: Replace content in `web/app/(dashboard)/compatibility/page.tsx`
**Action**: Build two-person selector (dropdowns from user's profiles list). "Calculate" button calls `POST /api/v1/compatibility/calculate`. Display: large circular gauge showing X/36 score, color-coded (green >24, yellow 18-24, red <18). Below: 8 guna cards each showing individual score, max possible, and a brief description.
**Dependencies**: T65
**Size**: L | **Agent**: frontend

### T37: Compatibility — Manglik + Per-Guna Detail
**File**: Component within compatibility page
**Action**: Manglik Dosha section showing both partners' status with explanation. Each guna card expandable to show detailed interpretation.
**Dependencies**: T35+T36
**Size**: M | **Agent**: frontend

### T38: Compatibility — Synastry Chart Overlay
**File**: Component within compatibility page
**Action**: Call `POST /api/v1/compatibility/synastry`. Display dual-chart overlay showing inter-chart aspects. Table of aspects with planet1, aspect type, planet2, orb, and harmonious/challenging indicator.
**Dependencies**: T35+T36
**Size**: L | **Agent**: frontend

### T39+T40: Transits Page — Positions + Active Aspects
**File**: Replace content in `web/app/(dashboard)/transits/page.tsx`
**Action**: Call `GET /api/v1/transits/current/{person_id}`. Display: (1) Current planetary positions table — planet, sign, degree, retrograde indicator. (2) Active transit aspects — transiting planet, aspect type, natal planet, orb, intensity, interpretation.
**Dependencies**: T65
**Size**: L | **Agent**: frontend

### T41: Transits Calendar
**File**: Component within transits page
**Action**: Month calendar view where each day shows significant transit events. Color-coded by type (sign change, exact aspect, retrograde station). Uses forecast API data.
**Dependencies**: T39+T40
**Size**: M | **Agent**: frontend

### T42: Transit Forecast Timeline
**File**: Component within transits page
**Action**: Call `GET /api/v1/transits/forecast/{person_id}?days=90`. Vertical timeline showing upcoming events: exact transits, sign changes, retrograde periods. Filterable by planet and timeframe.
**Dependencies**: T39+T40
**Size**: M | **Agent**: frontend

### T43+T44+T46: Muhurta Page — Full Build
**File**: Expand `web/app/(dashboard)/muhurta/page.tsx` (created in T3)
**Action**: (1) Activity type selector from `GET /api/v1/muhurta/activities`. (2) Date range picker. (3) Search button calls `POST /api/v1/muhurta/find-muhurta`. (4) Results list with quality score, time window, panchang details. (5) Today's summary panel from `GET /api/v1/muhurta/best-times-today` showing Rahu Kaal and good periods.
**Dependencies**: T3, T66
**Size**: L | **Agent**: frontend

### T45: Muhurta Monthly Calendar
**File**: Component within muhurta page
**Action**: Call `POST /api/v1/muhurta/monthly-calendar`. Calendar grid with each day showing auspicious/inauspicious status and total auspicious days count.
**Dependencies**: T43
**Size**: M | **Agent**: frontend

### T47: Astrologer Directory Page
**File**: Expand `web/app/(dashboard)/astrologers/page.tsx` (created in T4)
**Action**: Call `GET /api/v1/astrologers/search`. Build: search bar, filter sidebar (specialization, tradition, language, rating, availability), astrologer cards showing photo, name, specializations, rating, rate, "Book" button. Pagination.
**Dependencies**: T4
**Size**: L | **Agent**: frontend

### T48: Astrologer Profile Detail Page
**File**: Create `web/app/(dashboard)/astrologers/[astrologerId]/page.tsx`
**Action**: Call `GET /api/v1/astrologers/{astrologer_id}`. Show full profile: bio, specializations, languages, years of experience, verification status, reviews list, availability calendar, consultation types offered, rates. "Book Consultation" CTA.
**Dependencies**: T47
**Size**: M | **Agent**: frontend

### T49: Booking Flow
**File**: New components within astrologers/consultations
**Action**: Multi-step booking: (1) Select consultation type (video/chat/email/voice). (2) Pick available time slot. (3) Confirm and pay (Stripe checkout integration). Calls `POST /api/v1/consultations/book`.
**Dependencies**: T48
**Size**: L | **Agent**: frontend

### T50: Consultation History Page
**File**: Replace content in `web/app/(dashboard)/consultations/page.tsx`
**Action**: Call `GET /api/v1/consultations/my-consultations`. Show upcoming and past consultations. Each card shows: astrologer name, type, date/time, status badge (upcoming/completed/cancelled). Click to view detail.
**Dependencies**: none
**Size**: M | **Agent**: frontend

### T51: In-Consultation Messaging
**File**: New component for consultation detail
**Action**: Call `GET /api/v1/consultations/{id}` and `POST /api/v1/consultations/{id}/messages`. Build threaded message interface for active consultations. Real-time polling or WebSocket for new messages.
**Dependencies**: T50
**Size**: L | **Agent**: frontend

### T52+T53: Settings — Account + Subscription
**File**: Replace content in `web/app/(dashboard)/settings/page.tsx`
**Action**: Tab layout: Account | Subscription | Notifications | Chart Defaults | Display. Account tab: show/edit profile from `GET/PUT /api/v1/me` (name, email, avatar, date of birth, birth location). Subscription tab: show current tier from `GET /api/v1/me/subscription`, usage stats from `GET /api/v1/me/usage`, upgrade buttons linking to pricing page.
**Dependencies**: T14
**Size**: M | **Agent**: frontend

### T54+T55+T56: Settings — Notifications + Chart Defaults + Display
**File**: Components within settings page
**Action**: Notifications tab: toggle switches for email/push/in-app notifications for predictions, transits, dasha changes, consultations. Chart defaults tab: dropdowns for default tradition, house system, ayanamsa. Display tab: theme toggle (already exists elsewhere, add here), widget layout reset button. All persisted via `PUT /api/v1/me/preferences`.
**Dependencies**: T52
**Size**: M | **Agent**: frontend

### T57: Backend: Add Ethnicity to User Model
**File**: `src/josi/models/user_model.py`
**Action**: Add `ethnicity: List[str] = Field(default=[], sa_column=Column(JSON))` to User model. Generate Alembic migration. Update `UserUpdate` schema to include ethnicity.
**Size**: S | **Agent**: backend

### T58: Frontend: Ethnicity Capture
**File**: Component within settings page
**Action**: Multi-select dropdown in the Account tab for ethnicity. Options: Tamil Hindu, North Indian Hindu, Bengali Hindu, South Indian Christian, Muslim, Buddhist, Sikh, Jain, etc. Saved via `PUT /api/v1/me`.
**Dependencies**: T52, T57
**Size**: S | **Agent**: frontend

### T59: Backend: Cultural Events Calendar
**File**: New controller + service
**Action**: Create `GET /api/v1/events/cultural?ethnicity={list}&year={year}&month={month}`. Returns cultural festivals and events relevant to the user's ethnicity and location. Data-driven from a static calendar dataset (not real-time computed).
**Dependencies**: T57
**Size**: L | **Agent**: backend

### T60: Frontend: Cultural Events Calendar
**File**: New page or section within dashboard
**Action**: Calendar widget/page showing cultural events. Color-coded by tradition. Links to relevant panchang data for each date.
**Dependencies**: T59, T58
**Size**: M | **Agent**: frontend

### T61+T63: AI Chat Page — Interface + API Wiring
**File**: Replace content in `web/app/(dashboard)/ai/page.tsx`
**Action**: Build full chat interface. Message input at bottom, conversation history scrolling up. User sends question, frontend calls `POST /api/v1/ai/interpret` with `chart_id`, `question`, `style`. Show AI response in chat bubble. Support for selecting which chart to discuss. Conversation state managed in React state (not persisted to backend initially).
**Size**: L | **Agent**: frontend

### T62: AI Chat — Chart Context Sidebar
**File**: Component within AI page
**Action**: Right sidebar showing: selected chart's key placements (Sun/Moon/Asc), current dasha period, active transits. Provides at-a-glance context while chatting. Collapsible on mobile.
**Dependencies**: T61
**Size**: M | **Agent**: frontend

### T64: AI Chat — Style Selector
**File**: Component within AI page
**Action**: Dropdown or toggle bar above chat input to select interpretation style. Loads options from `GET /api/v1/ai/styles`. Default: Balanced.
**Dependencies**: T61
**Size**: S | **Agent**: frontend

### T65: ProfileSelector Shared Component
**File**: Create `web/components/ui/profile-selector.tsx`
**Action**: Reusable dropdown component that fetches user's persons from `GET /api/v1/persons/` and lets them pick one. Supports "default profile" concept. Emits `onChange(personId)`. Used across Dasha, Transits, Predictions, Remedies, Compatibility pages and dashboard widgets. Caches the person list.
**Size**: M | **Agent**: frontend

### T66: LocationPicker Shared Component
**File**: Create `web/components/ui/location-picker.tsx`
**Action**: Reusable component for location input. Options: (1) Use current location (browser geolocation), (2) Use profile birth location, (3) Manual city search using `GET /api/v1/location/search`. Returns `{latitude, longitude, timezone, displayName}`. Used by Panchang, Muhurta, and widgets.
**Size**: M | **Agent**: frontend

### T67: TimeframeSelector Shared Component
**File**: Create `web/components/ui/timeframe-selector.tsx`
**Action**: Reusable tab bar component with configurable timeframe options (Daily/Weekly/Monthly/Quarterly/Half-yearly/Yearly). Emits `onChange(timeframe)`. Styled consistently with app design system.
**Size**: S | **Agent**: frontend

---

## Agent Assignment Strategy

Each agent should receive:
1. The specific task ID(s) and full specification from this document
2. The relevant file paths to read and modify
3. The API endpoint documentation (from backend controller docstrings)
4. The design system reference (existing component styles)

### Context Budget Per Agent
- **S tasks**: ~15K tokens context needed
- **M tasks**: ~25K tokens context needed
- **L tasks**: ~40K tokens context needed
- **XL tasks**: ~60K tokens context needed (split if possible)

### Agent Types
- **Frontend agent**: Needs access to `web/` directory, existing component patterns, API client, design tokens
- **Backend agent**: Needs access to `src/josi/`, existing controller patterns, service layer, models
- **Fullstack agent**: Needs both — only use when a task requires creating a backend endpoint AND its frontend consumer in a single unit

---

## Risk Register

| Risk | Impact | Mitigation |
|------|--------|------------|
| Prediction controller has a typo bug (`astrology_astrology_calculator`) that prevents it from working | Blocks all prediction features | T28 is Wave 0, fix first |
| `data.data.chart_id` bug causes broken chart creation flow | Users can't create charts from dashboard | T1 is Wave 0 |
| react-grid-layout may conflict with existing CSS grid | Widget grid breaks | T13 is Wave 4, test thoroughly |
| AI interpretation service may not be fully functional | AI Chat page shows errors | T61 should handle API errors gracefully with fallback UI |
| Cultural events calendar requires curated data | Empty results if no data seeded | T59 should include a seed dataset for major Indian festivals |
| Consultation booking needs Stripe integration | Payment flow incomplete | T49 can stub payment step initially |

---

## Success Criteria

1. Zero "Coming Soon" placeholders remain on any page
2. Zero 404 errors from sidebar navigation
3. All 9 dashboard widgets show real data (with graceful loading/error states)
4. Chart creation redirect works correctly
5. Aspects tab in chart detail shows actual aspect data
6. All prediction timeframes return structured 10-category data
7. Widget layout persists across sessions via backend API
8. Settings page allows managing all user preferences
