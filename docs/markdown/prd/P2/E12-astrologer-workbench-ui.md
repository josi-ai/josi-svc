---
prd_id: E12
epic_id: E12
title: "Astrologer Workbench UI — Professional-Grade Classical Computation Surface"
phase: P2-breadth
tags: [#astrologer-ux, #i18n, #extensibility, #correctness, #performance]
priority: must
depends_on: [E1a, E1b, E2a, E3, E4a, E4b, E5, E6a, E7, E8, E9, E10, E11a, E11b, F8, F9, F10, F11, E14a]
enables: [E14a, D4, D8, I1]
classical_sources: [bphs, saravali, phaladeepika, jataka_parijata, jaimini_sutras, tajaka_neelakanthi, kp_reader, jh, maitreya]
estimated_effort: 8-10 weeks
status: draft
author: @agent
last_updated: 2026-04-19
---

# E12 — Astrologer Workbench UI

## 1. Purpose & Rationale

Professional astrologers are the domain experts whose approval is the single strongest lever on Josi's correctness and cultural credibility. They are also the primary revenue driver of the marketplace (D4) and the source of the override signals (Decision 6 of master spec) that calibrate every aggregation strategy. Yet the current Josi UI was built for end-users: full-width dashboard widgets, simple summaries, no access to the classical depth underneath.

E12 is the pro-facing surface that exposes the full computation depth already built in P0–P2 engines. Every classical technique that the engines compute is exposed: divisional charts D1–D144, all dasa systems in tree + bar visualizations, full Ashtakavarga grids, all 250 yogas with citation panels, Jaimini karakas and arudhas, Tajaka year comparisons, KP sub-lord tables, Prasna, fixed stars, harmonics, eclipses. Every computed value is badged with its `source_authority`; clicking the badge reveals the classical verse that defined it. Astrologers pick their lineage in profile — per `technique_family` — and the UI reflects that preference end-to-end.

The commercial framing: E12 turns astrologers into *power users* of Josi. They onboard their consultation practice, compute readings 10× faster with better primary sources than JH or Maitreya (which are desktop-only, English-only), produce PDF-exported readings, and their edits feed the E14a experimentation loop. This is how Josi becomes the professional standard — not because we advertise it, but because the workbench is the best tool they've used.

## 2. Scope

### 2.1 In scope

**Information architecture**

- New Pro shell at `web/app/(pro)/workbench/*` (separate route group from `(dashboard)` for end-users).
- Left sidebar: Chart List, Clients, Saved Readings, Source Preferences, Usage. Collapsed to icon rail on small screens.
- Primary working surface: `/workbench/chart/[chartId]` with top-level tabs:
  - **Natal** — primary chart rendering (chosen style), planet + house + aspect tables.
  - **Divisional** — D1–D144 selector (D1/D2/D3/D4/D7/D9/D10/D12/D16/D20/D24/D27/D30/D40/D45/D60/D81/D108/D144) with overlay mode (compare two vargas side by side).
  - **Dashas** — tree view + bar timeline for all systems (Vimshottari / Yogini / Ashtottari / Chara / Narayana / Kalachakra).
  - **Ashtakavarga** — interactive 12×7 grid + Sarvashtakavarga + transit bindu overlay.
  - **Yogas** — sortable/filterable list (active, strength, source, era) + citation panel side-drawer.
  - **Jaimini** — Chara Karakas table, Arudha Lagna, Padas, Jaimini yogas, Jaimini dasa context.
  - **Tajaka** — Varshaphala year selector with Muntha, year-lord, Sahams, comparison with prior year.
  - **Transits** — current transits, upcoming events, Sade Sati / Dhaiya bands.
  - **KP** — sub-lord table, significators matrix, ruling planets.
  - **Prasna** — horary entry (new question with moment timestamp) → fresh sub-chart.

**Chart-style picker**

- North Indian, South Indian, East Indian, Bengali, Western wheel — all rendered from the same computed data. Stored per user preference + per-chart override.
- Each style implemented as an isolated component under `web/components/charts/styles/` reusing `web/types/chart.ts` data.

**Source-authority-aware display**

- Every computed value on every tab carries a small source badge (e.g., "BPHS" in pill form). Click → tooltip with verse citation and cross-source comparison popover.
- Computed values change visually when astrologer swaps source preference (no page reload — TanStack Query invalidation).

**Per-technique source preference**

- `/workbench/settings/sources` — for each `technique_family`, astrologer chooses a source or sets weights (slider UI). Saved to `astrologer_source_preference` (F2/F8).
- Preferences applied live on next tool response.

**Classical citations panel**

- Side-drawer component. Renders per-verse: IAST, Devanagari, Tamil, English translation, commentary (when available). Loaded lazily per citation id.
- Clickable from yogas list, drill-down chips from E11b, transit events.

**Dasa tree + bar diagrams**

- Tree view: expandable MD → AD → PD → SubSub → SubSubSub (5 levels). Mirrors Maitreya/JH convention of period durations in "years-months-days".
- Bar view: continuous timeline across visible window; current period highlighted; click span → drill-down panel with classical dasa-phala text.
- Both views driven by `get_current_dasa(system, level=5)` + `get_dasa_timeline(system, date_range)` tools.

**Editable reading export**

- `/workbench/chart/[chartId]/reading/new` — starts from an auto-generated template (classical structure: Lagna, Karakas, Yogas, Dasa-Phala, Transit, Remedies).
- Astrologer edits inline (ProseMirror-based editor, `web/components/editor/`).
- Export: HTML preview → PDF via server-side Playwright renderer (`/api/v1/readings/{id}/export.pdf`).
- Edit vs auto-generated diff tracked; **the diff is the implicit override signal** (E14a Decision 6): if astrologer deletes/replaces an auto-computed value, that's a rejection signal; kept verbatim is an acceptance signal.

**Pro-only features**

- **Bulk chart import** — CSV/JSON of client birth data, concurrent computation via batch API, progress UI.
- **Varshaphala year comparison** — stack 3–5 consecutive solar-return years side by side; diff highlighting.
- **Multi-chart synastry with overlay** — select 2 charts, render planets from chart B on chart A (and reverse), aspect table, composite chart sub-tab.
- **Live Ultra mode in AI chat** — when E11b chat is invoked from workbench, `ensemble=true` default; astrologer-configured weights applied.

**i18n**

- UI in English + Hindi + Tamil at launch (framework supports the full 10-language D3 set; 3 prioritized for astrologer audience).
- Sanskrit technical terms always shown with a hover tooltip giving plain-language meaning in the user's UI language.
- `web/lib/i18n/` set up with message catalogs; no hardcoded strings in components.

**Performance**

- `chart_reading_view` row hydrates the whole workbench within 300 ms P95 on re-visit.
- First-load per tab: lazy-chunked; non-visible panels do not block above-the-fold.
- Virtualization on yoga list (up to 250 rows) and dasa tree (up to ~5000 leaves).

### 2.2 Out of scope

- **Marketplace consultation flow** (video/chat/email/voice, booking, payments, reviews) — D4.
- **Astrologer certification program** — D8.
- **Real-time collaboration on a reading** (two astrologers editing the same doc) — deferred.
- **Offline mode / desktop installer** — desktop-equivalence via responsive web is sufficient at P2.
- **Bulk chart export to JH-compatible files** — later; import-only at launch.
- **AI rule-authoring console** — P3 (`P3-E2-console`).
- **Automated reading generation end-to-end (one click, no edits)** — workbench is the *editing* surface; auto-generated template is a starting point only.
- **Voice dictation into the reading editor** — P5.
- **Native mobile app** — responsive web hits desktop + tablet; phone is a read-only viewer in P2.

### 2.3 Dependencies

- All P1 engines (E1a, E2a, E4a, E6a) for the base computations.
- All P2 engines (E1b, E3, E4b, E5, E7, E8, E9, E10) for full depth.
- F8 aggregation + F9 reading view + F10 tool contract + F11 citations are the data spine.
- E11a/E11b for the embedded chat panel.
- E14a for experiment/signal attribution of astrologer edits.
- `astrologer_source_preference` table (defined in F2) must exist.
- Authentication: astrologer role on `User` model (already present per CLAUDE.md memory).
- PDF rendering: server-side Playwright; bundled in api container.

## 3. Technical Research

### 3.1 Separate route group for Pro surface

Why `(pro)` and not just new tabs inside `(dashboard)`:

- Different navigation shell — dashboard is widget-grid; workbench is tab-panel.
- Different auth gate — only users with `role='astrologer'` and active verification.
- Different telemetry — we measure workbench usage separately (time-on-chart, reading export rate) for product-mix decisions.
- Different SSR policy — dashboard is client-only per CLAUDE.md; workbench follows the same client-only rule (all data comes from typed tool calls), mounted via a `WorkbenchShell` analogous to `DashboardShell`.

Client-only rendering prevents Clerk/auth hydration mismatches that have already bitten us on `(dashboard)`.

### 3.2 Chart-style picker — clean abstraction

Every style component takes the same props: `{ chart: NatalChartData; highlights?: ChartHighlights; style: ChartStyle }`. Visual differences are purely rendering.

```
NatalChartData → StyleDispatcher → { NorthIndianChart | SouthIndianChart | ... }
```

`NatalChartData` is the same shape produced by `get_chart_data` — planets, houses, aspects — in ecliptic + whole-sign / placidus agnostic form. Whole-sign houses default (Vedic). Rasi-style picker switches between North/South/East/Bengali; Western wheel uses placidus houses (toggleable).

Reuse: existing `web/components/charts/north-indian-chart.tsx`, `south-indian-chart.tsx`, `western-wheel-chart.tsx` remain; add `east-indian-chart.tsx`, `bengali-chart.tsx`.

### 3.3 Dasa tree + bar: data shape and virtualization

The dasa tree can have up to 9 × 9 × 9 × 9 × 9 = ~59k nodes in full depth — but only 9 × 9 × 9 (729) are usually rendered because level 4–5 are lazy-loaded per F9's already-computed tree.

Data shape:

```ts
interface DasaNode {
  level: number;              // 1..5
  lord: string;
  start: string;              // ISO
  end: string;
  durationDays: number;
  source: CitedFact<string>;
  classicalPhala?: string;    // BPHS dasa-phala text (if available for this MD/AD pair)
  children?: DasaNode[];      // undefined = not loaded
}
```

Bar view uses a virtualized horizontal canvas. Zoom levels: year / decade / lifetime. Current period highlighted in `--accent-gold`. Clicking a span scrolls the tree to the matching node.

### 3.4 Ashtakavarga interactive grid

The Sarva matrix is 12 columns × 7 rows (planets + lagna) + 1 row of sign totals. Per-cell drill-down: click → popover shows the 8 contributors' individual bindu marks with source breakdown.

Transit overlay: toggle "Show transit bindu for today" overlays current-position markers on each sign column. Updates live as a user changes the date picker (via a debounced tool call).

### 3.5 Yogas list with citation panel

250-row virtualized list with columns: active, name (display + Sanskrit), strength, source, era. Filter chips: active-only, source-family, era, strength range.

Side-drawer citation panel (`ClassicalCitationPanel`) opens on row click. Loaded via `GET /api/v1/classical/verses/{rule_id}?source_id=...` (new endpoint, served from `classical_rule.rule_body`). Panel shows:

- Title + classical_names dict
- Verse in IAST, Devanagari, Tamil, English
- Cross-source comparison: "BPHS says X; Saravali says Y; Phaladeepika says Z" — with per-source confidence
- Related yogas (same lord, same house)

### 3.6 Source preference UI

Two modes per technique family:

1. **Single source** — radio-style: pick one. Weight = 1.0 for that, 0 for others.
2. **Weighted blend** — sliders per source (snap to 0 / 0.25 / 0.5 / 0.75 / 1.0). Sum visualization shows normalized weights.

A third "Ultra" toggle flags the family to use ensemble mode automatically in E11b chat. Saved preferences apply across all charts for this astrologer; per-chart override available via a small "override for this chart" affordance.

Preferences flow: UI → `PUT /api/v1/astrologer/source-preferences/{family_id}` → `astrologer_source_preference` table → TanStack Query invalidation on keys `['chart-reading-view', chartId]` → tool calls re-run with new preference on next open.

### 3.7 Editable reading export + implicit override signal

The auto-generated reading template is built server-side via `GET /api/v1/readings/template?chart_id=...` which returns a ProseMirror-compatible JSON document. Each block is tagged with its computed-fact provenance:

```jsonc
{
  "type": "paragraph",
  "attrs": {
    "fact_ref": "yoga.gaja_kesari.active",
    "computed_value": "active",
    "source": "bphs",
    "citation": "BPHS 36.14-16"
  },
  "content": [{ "type": "text", "text": "Gaja Kesari is strongly active..." }]
}
```

Astrologer edits the document. On save:

- Diff per block: if `content.text` unchanged → signal `accepted`.
- If changed → signal `modified` with diff payload.
- If block removed → signal `rejected`.
- Signals written to `aggregation_signal` (F2) keyed to the fact_ref's `aggregation_event_id`.

PDF export uses a headless Playwright renderer in the api container; reading HTML → A4 PDF. Download served via presigned URL from storage.

### 3.8 i18n strategy

- Next.js App Router + `next-intl` for message catalogs.
- `web/lib/i18n/messages/{en,hi,ta}/workbench.json` (and other components).
- Sanskrit terms passed through a `<SanskritTerm term="rāja-yoga">` component that renders devanagari + roman + tooltip in UI language.
- Date formatting: user-selected calendar (Gregorian / Shalivahana / Vikram).
- Number formatting: locale-aware (Tamil uses native digits where configured).

### 3.9 Performance budget

- `chart_reading_view` row fetched once per chart-open; hydrated into a typed `WorkbenchChartStore` (Zustand). All tabs read from the store.
- Non-visible tabs are route-split (`React.lazy` + Next dynamic import). First paint of Natal tab < 300 ms after data arrives.
- Yoga list virtualized via `@tanstack/react-virtual` (250 rows, window 20).
- Dasa bar view: canvas, not DOM (perf headroom for 5k spans).
- Dasa tree: DOM, virtualized, level-4+ lazy-expanded.
- Image assets: SVG-only. No raster images in the workbench primary surface.
- Lighthouse desktop performance score ≥ 90 for `/workbench/chart/[chartId]`.

### 3.10 Accessibility (pro tool but accessibility still required)

- Keyboard nav: `[` / `]` to cycle tabs, `n/p` next/prev chart in list, `?` help overlay.
- Every interactive element has focus ring via `--focus-ring`.
- Color palette is color-blind-safe (tested against deuteranopia + protanopia simulators).
- ARIA labels on charts describe the planet + house placements for screen readers.

### 3.11 Alternatives considered

| Alternative | Rejected because |
|---|---|
| Embed workbench as dashboard tabs | Conflicts with widget-grid mental model; different audience |
| Electron desktop app | Native packaging overhead; responsive web hits 95% of the value |
| Render every style in Canvas | Loses DOM accessibility; SVG is the right primitive for this complexity level |
| Rebuild from JH UI conventions exactly | Clunky; we have latitude for better design while preserving workflow idioms |
| Single mega-chart component switching styles internally | Violates CLAUDE.md max-300-line rule; isolated style components are clearer |
| Store source preferences in localStorage | Loses cross-device consistency; DB is right |
| PDF via client-side jsPDF | Fidelity loss for complex layouts; server-side Playwright is proven |

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| Where in the route tree | `web/app/(pro)/workbench/*` | Separate auth + navigation shell |
| Default chart style | North Indian for users with Indian locale; Western for others; user can override in settings | Cultural default + escape hatch |
| Varga depth | D1–D144 selectable; D81, D108, D144 opt-in (rarely used) | Respect E7 scope; don't overwhelm UI |
| Dasa level depth | 5 levels default, user-configurable 3–5 | Matches JH/Maitreya; beyond 5 is noise |
| Source preference granularity | Per technique_family only (not per-rule) | Per-rule is too granular; future work |
| Bulk import format | CSV + JSON; validated via Pydantic | Standard; schemas published |
| Reading export format | PDF primary; HTML + DOCX roadmap | PDF is the professional currency |
| Reading editor | ProseMirror via TipTap | Best-in-class; MIT license; typed |
| Implicit override signal granularity | Per-block diff | Lightweight; avoids char-level noise |
| Explicit override signal | Thumbs next to each computed block | Finer grained than per-reading |
| I18n at launch | en, hi, ta | Prioritized astrologer audience |
| SSR | No — client-only per dashboard convention | Hydration safety; tool-call data model |
| Route group auth | `role='astrologer'` + `is_verified=true` | Gates workbench from end-users cleanly |
| Zustand vs Context for store | Zustand | Lighter; selective subscriptions; typed |
| Chart-style components file count | One file per style | Max-300-line rule; isolated tests |
| Side-drawer vs modal for citation panel | Drawer (non-blocking) | Astrologer flips between chart + verse continuously |
| Dasa-phala text source | Per source_authority; fallback to classical BPHS if unavailable | Most sources have phala text |
| Tajaka comparison years count | 3 default, 5 max | Visual complexity cliff beyond 5 |
| Synastry composite chart | Midpoint composite; Davison roadmap | Midpoint is the Vedic/Western common baseline |
| Mobile viewport | Tablet-usable; phone is read-only view | Workbench is desktop-primary |

## 5. Component Design

### 5.1 Route tree

```
web/app/(pro)/
├── layout.tsx                              # WorkbenchShell mount (client-only)
├── workbench/
│   ├── page.tsx                            # chart list + recent
│   ├── clients/
│   │   └── page.tsx                        # clients list, search, tags
│   ├── chart/
│   │   └── [chartId]/
│   │       ├── layout.tsx                  # tab nav + chart header
│   │       ├── page.tsx                    # redirect → /natal
│   │       ├── natal/page.tsx
│   │       ├── divisional/page.tsx
│   │       ├── dashas/page.tsx
│   │       ├── ashtakavarga/page.tsx
│   │       ├── yogas/page.tsx
│   │       ├── jaimini/page.tsx
│   │       ├── tajaka/page.tsx
│   │       ├── transits/page.tsx
│   │       ├── kp/page.tsx
│   │       ├── prasna/page.tsx
│   │       └── reading/
│   │           ├── new/page.tsx
│   │           └── [readingId]/page.tsx
│   ├── synastry/[chartA]/[chartB]/page.tsx
│   ├── settings/
│   │   ├── sources/page.tsx
│   │   ├── preferences/page.tsx
│   │   └── usage/page.tsx
│   └── import/page.tsx                     # bulk import
```

### 5.2 Component library

```
web/components/workbench/
├── shell/
│   ├── workbench-shell.tsx                 # client-only mount wrapper
│   ├── sidebar.tsx
│   ├── chart-header.tsx
│   └── tab-nav.tsx
├── charts/
│   ├── style-picker.tsx
│   └── styles/
│       ├── north-indian-chart.tsx          # existing, moved
│       ├── south-indian-chart.tsx
│       ├── east-indian-chart.tsx           # NEW
│       ├── bengali-chart.tsx               # NEW
│       └── western-wheel-chart.tsx
├── divisional/
│   ├── varga-selector.tsx
│   └── varga-overlay.tsx
├── dashas/
│   ├── dasa-system-picker.tsx
│   ├── dasa-tree.tsx                       # virtualized
│   ├── dasa-node-row.tsx
│   ├── dasa-bar-timeline.tsx               # canvas
│   ├── dasa-phala-panel.tsx
│   └── dasa-detail-drawer.tsx
├── ashtakavarga/
│   ├── sarvashtakavarga-grid.tsx
│   ├── bhinna-matrix.tsx
│   ├── transit-bindu-overlay.tsx
│   └── ashtakavarga-cell-popover.tsx
├── yogas/
│   ├── yoga-list.tsx                       # virtualized
│   ├── yoga-row.tsx
│   ├── yoga-filter-chips.tsx
│   └── yoga-badge.tsx                      # active/strength
├── jaimini/
│   ├── chara-karaka-table.tsx
│   ├── arudha-board.tsx
│   ├── jaimini-yoga-list.tsx
│   └── jaimini-dasa-context.tsx
├── tajaka/
│   ├── year-picker.tsx
│   ├── varshaphala-overview.tsx
│   ├── year-comparison-panel.tsx
│   ├── sahams-list.tsx
│   └── muntha-marker.tsx
├── transits/
│   ├── current-transits.tsx
│   ├── upcoming-events.tsx
│   └── sade-sati-band.tsx
├── kp/
│   ├── sub-lord-table.tsx
│   ├── significators-matrix.tsx
│   └── ruling-planets.tsx
├── prasna/
│   ├── question-composer.tsx
│   └── prasna-chart-view.tsx
├── citation/
│   ├── classical-citation-panel.tsx        # side-drawer
│   ├── source-badge.tsx
│   ├── verse-block.tsx
│   └── cross-source-comparison.tsx
├── reading/
│   ├── reading-editor.tsx                  # TipTap wrapper
│   ├── reading-template-loader.tsx
│   ├── reading-block-menu.tsx
│   ├── reading-diff-signal.tsx             # tracks accept/modify/reject
│   └── reading-export-button.tsx
├── source-preferences/
│   ├── family-preference-card.tsx
│   ├── source-weight-slider.tsx
│   └── ultra-mode-toggle.tsx
├── synastry/
│   ├── synastry-overlay-chart.tsx
│   ├── aspect-table.tsx
│   └── composite-chart-panel.tsx
├── import/
│   ├── csv-uploader.tsx
│   ├── import-row-preview.tsx
│   └── import-progress.tsx
└── common/
    ├── sanskrit-term.tsx
    ├── confidence-bar.tsx
    ├── loading-skeleton.tsx
    └── error-state.tsx
```

Each file ≤ 300 lines. Where a panel exceeds that, it's broken into sub-components.

### 5.3 Types

```
web/types/
├── classical-chart.ts              # NatalChartData shared across styles
├── classical-dasa.ts               # DasaNode, DasaSystem, DasaTimeline
├── classical-varga.ts              # VargaId enum, VargaChart
├── classical-ashtakavarga.ts       # Matrix, CellDetail
├── classical-yoga.ts               # YogaEntry, YogaFilter
├── classical-jaimini.ts            # CharaKaraka, Arudha, JaiminiYoga
├── classical-tajaka.ts             # VarshaphalaSummary, Saham, Muntha
├── classical-transit.ts            # TransitEvent, SadeSatiBand
├── classical-kp.ts                 # SubLordRow, SignificatorCell
├── classical-prasna.ts             # PrasnaQuestion, PrasnaChart
├── classical-citation.ts           # VerseBlock, ClassicalCitation
├── workbench-reading.ts            # ReadingDoc, ReadingBlock, ReadingDiff
├── workbench-source-pref.ts        # SourcePreference, FamilyWeights
└── workbench-synastry.ts           # SynastryAspects, CompositeChart
```

All types imported in components; zero duplicate definitions (CLAUDE.md rule). Every apiClient call typed against these.

### 5.4 Data layer

```ts
// web/hooks/workbench/use-chart-reading-view.ts

interface ChartReadingView {
  chartId: string;
  activeYogas: YogaEntry[];
  currentDasas: Record<DasaSystem, DasaNode[]>;
  transitHighlights: TransitEvent[];
  tajakaSummary: VarshaphalaSummary | null;
  jaiminiSummary: JaiminiSummary;
  ashtakavargaSummary: AshtakavargaSummary;
  astrologerPreferenceKey: string;
  lastComputedAt: string;
}

export function useChartReadingView(chartId: string) {
  return useQuery<ChartReadingView>({
    queryKey: ['chart-reading-view', chartId],
    queryFn: async () => {
      const res = await apiClient.get<{ data: ChartReadingView }>(
        `/api/v1/charts/${chartId}/reading-view`,
      );
      return res.data.data;
    },
    staleTime: 30_000,
  });
}
```

Per-technique hooks (`useDasaTimeline`, `useAshtakavargaDetail`, `useYogaList`, `useCitation`) follow the same shape: transform happens in `queryFn`, component consumes typed data (CLAUDE.md rule).

### 5.5 API contract additions

**Chart reading view (workbench-optimized):**

```
GET /api/v1/charts/{chartId}/reading-view
Response: { success, data: ChartReadingView }
```

**Detailed technique endpoints (lazy):**

```
GET /api/v1/charts/{chartId}/dashas/{system}/timeline?from=...&to=...&levels=5
GET /api/v1/charts/{chartId}/divisional/{vargaId}
GET /api/v1/charts/{chartId}/ashtakavarga/detail?cell=...
GET /api/v1/charts/{chartId}/tajaka/{year}
GET /api/v1/charts/{chartId}/kp/significators
GET /api/v1/charts/{chartId}/synastry/{otherChartId}
```

**Source preferences:**

```
GET /api/v1/astrologer/source-preferences
PUT /api/v1/astrologer/source-preferences/{family_id}
Body: { mode: "single" | "weighted" | "ultra",
        source_weights: Record<source_id, number> }
```

**Reading:**

```
GET /api/v1/readings/template?chart_id=...              # ProseMirror JSON
POST /api/v1/readings                                   # create from template
PUT  /api/v1/readings/{id}                              # save edits; writes signals
POST /api/v1/readings/{id}/export.pdf                   # returns presigned URL
```

**Bulk import:**

```
POST /api/v1/charts/bulk-import        # multipart CSV/JSON
GET  /api/v1/charts/bulk-import/{job_id}/status
```

**Classical verses:**

```
GET /api/v1/classical/verses/{rule_id}?source_id=...&lang=en,sa_iast,sa_devanagari,ta
```

### 5.6 Backend services (delta vs existing)

```
src/josi/api/v1/controllers/
├── workbench_chart_controller.py
├── workbench_reading_controller.py
├── workbench_source_preference_controller.py
├── workbench_import_controller.py
└── classical_verse_controller.py

src/josi/services/workbench/
├── reading_template_service.py         # builds ProseMirror JSON from reading view
├── reading_diff_service.py             # computes accept/modify/reject per block
├── reading_export_service.py           # Playwright-based PDF
└── bulk_import_service.py

src/josi/services/classical/
└── verse_service.py                    # serves canonical verses per source

src/josi/workers/
└── reading_pdf_worker.py               # async PDF generation (optional)
```

### 5.7 Store

```ts
// web/stores/workbench-chart-store.ts
import { create } from 'zustand';

interface WorkbenchChartStore {
  chartId: string | null;
  activeTab: WorkbenchTab;
  chartStyle: ChartStyle;
  dasaSystem: DasaSystem;
  vargaId: VargaId;
  setChartId: (id: string) => void;
  setActiveTab: (tab: WorkbenchTab) => void;
  setChartStyle: (style: ChartStyle) => void;
  setDasaSystem: (s: DasaSystem) => void;
  setVargaId: (v: VargaId) => void;
}

export const useWorkbenchChartStore = create<WorkbenchChartStore>((set) => ({
  chartId: null,
  activeTab: 'natal',
  chartStyle: 'north_indian',
  dasaSystem: 'vimshottari',
  vargaId: 'D1',
  setChartId: (chartId) => set({ chartId }),
  setActiveTab: (activeTab) => set({ activeTab }),
  setChartStyle: (chartStyle) => set({ chartStyle }),
  setDasaSystem: (dasaSystem) => set({ dasaSystem }),
  setVargaId: (vargaId) => set({ vargaId }),
}));
```

## 6. User Stories

### US-E12.1: As an astrologer, I can open a client's chart and see Natal + all 5-level Vimshottari dasa within 1 second
**Acceptance:** Chart header loads; Natal tab renders within 300 ms of server response; dasa tree lazy-expands to level 5 under cursor.

### US-E12.2: As an astrologer, I can switch chart style between North/South/East/Bengali/Western without page reload
**Acceptance:** Style picker changes rendering; same planet data; preserved highlights.

### US-E12.3: As an astrologer, I can configure my preferred source per technique family and see the UI reflect my choice
**Acceptance:** Setting BPHS for yogas + Saravali for Tajaka → opening any chart shows source badges matching; cross-source popover highlights my chosen source.

### US-E12.4: As an astrologer, I can open a yoga row and see the defining verse in IAST + Devanagari + Tamil + English
**Acceptance:** Click yoga row → citation drawer opens within 200 ms; all 4 language renderings present when available.

### US-E12.5: As an astrologer, I can generate a reading template, edit it, and export to PDF
**Acceptance:** Template loaded from auto-compute; edits save via PUT; clicking Export triggers PDF download within 10 s.

### US-E12.6: As a researcher, my edits to the reading feed the override-signal loop
**Acceptance:** Modifying a yoga paragraph in the editor produces an `aggregation_signal` row of type `modified`; deleting a block produces `rejected`; keeping verbatim produces `accepted`.

### US-E12.7: As an astrologer, I can bulk-import 100 client charts via CSV and compute them in parallel
**Acceptance:** CSV upload → Pydantic validation report; progress UI shows completed/failed counts; all 100 charts accessible in list within 5 min.

### US-E12.8: As an astrologer, I can compare 3 consecutive Varshaphala years side by side
**Acceptance:** Year selector allows range; view renders 3 columns with diff highlighting on Muntha, year-lord, active Sahams.

### US-E12.9: As an astrologer, I can overlay chart B onto chart A for synastry
**Acceptance:** Synastry view shows chart A with chart B planets in outer ring; aspect table populates; composite sub-tab accessible.

### US-E12.10: As a Tamil-speaking astrologer, my UI is in Tamil with Sanskrit terms tooltipped in Tamil
**Acceptance:** `?lang=ta` or user-preference → all UI strings Tamil; hover "raja-yoga" → Tamil explanation.

### US-E12.11: As an astrologer, I can call the AI chat from within a chart and it runs in Ultra mode with my weights
**Acceptance:** Chat panel opens pre-scoped to the current chart; responses cite per-source; my configured weights guide the aggregated source ordering.

### US-E12.12: As an astrologer using a keyboard, I can navigate tabs and charts without a mouse
**Acceptance:** `[` / `]` cycle tabs; `n/p` next/prev chart; `?` opens shortcut help overlay.

### US-E12.13: As an astrologer with a color vision deficiency, the Ashtakavarga heatmap is legible
**Acceptance:** Color palette passes deuteranopia/protanopia simulators; alternative pattern markers optional.

## 7. Tasks

### T-E12.1: Route scaffold + WorkbenchShell
- **Definition:** `web/app/(pro)/*` tree; auth gate on `role='astrologer'`; `WorkbenchShell` client-only mount.
- **Acceptance:** `/workbench` returns 403 for end-users; astrologer sees sidebar.
- **Effort:** 3 days

### T-E12.2: Chart header + tab nav
- **Definition:** Top-level tab nav; chart header with birth summary, style picker, chart switcher.
- **Acceptance:** Tabs navigate; keyboard shortcuts work; style picker persists.
- **Effort:** 2 days

### T-E12.3: `GET /api/v1/charts/{id}/reading-view` endpoint
- **Definition:** Returns typed `ChartReadingView` shape assembled from `chart_reading_view` row.
- **Acceptance:** P95 < 100 ms server-side; shape matches TypeScript type exactly.
- **Effort:** 2 days

### T-E12.4: Natal tab (rendering + tables)
- **Definition:** Chart visualization (style-dispatched) + planet table + house table + aspect table.
- **Acceptance:** All 5 chart styles render from same data; tables virtualized where needed.
- **Effort:** 4 days

### T-E12.5: East Indian + Bengali chart styles
- **Definition:** Two new components following existing NorthIndian pattern.
- **Acceptance:** Visual parity with reference from JH/Maitreya; a11y labels.
- **Effort:** 4 days

### T-E12.6: Divisional tab + varga selector
- **Definition:** `VargaSelector` component; per-varga rendering via same style components.
- **Acceptance:** All 15 vargas selectable; overlay mode works (D1 + D9 side-by-side).
- **Effort:** 3 days

### T-E12.7: Dasa tab — tree view
- **Definition:** Virtualized tree; 5-level lazy expansion; dasa-phala drawer on node click.
- **Acceptance:** 5k-node tree renders smoothly at 60 fps on mid-tier laptop.
- **Effort:** 4 days

### T-E12.8: Dasa tab — bar timeline
- **Definition:** Canvas-based timeline; zoom levels; current period highlight; click → scroll tree to matching node.
- **Acceptance:** Timeline renders 500 spans at 60 fps; sync with tree works.
- **Effort:** 3 days

### T-E12.9: Ashtakavarga tab
- **Definition:** Sarva grid, Bhinna matrices, cell popover, transit bindu overlay.
- **Acceptance:** Correct values per source; hover reveals 8-contributor breakdown.
- **Effort:** 3 days

### T-E12.10: Yogas tab with citation drawer
- **Definition:** Virtualized yoga list; filter chips; `ClassicalCitationPanel` drawer.
- **Acceptance:** 250 yogas render instantly; filter latency < 50 ms; drawer opens in 200 ms.
- **Effort:** 4 days

### T-E12.11: Jaimini tab
- **Definition:** Chara karaka table, Arudha board, Jaimini yogas list.
- **Acceptance:** Karakas compute correctly; Arudha lagna displayed with source badge.
- **Effort:** 2 days

### T-E12.12: Tajaka tab + year comparison
- **Definition:** Year picker; Varshaphala overview; 3-5 year comparison grid.
- **Acceptance:** Muntha + year-lord + Sahams visible; diffs highlighted.
- **Effort:** 3 days

### T-E12.13: Transits tab
- **Definition:** Current transits table; Sade Sati band; upcoming events.
- **Acceptance:** Data matches `get_transit_events` tool; Sade Sati span accurate.
- **Effort:** 2 days

### T-E12.14: KP tab
- **Definition:** Sub-lord table, significators matrix, ruling planets.
- **Acceptance:** KP values agree with E9 engine golden suite.
- **Effort:** 2 days

### T-E12.15: Prasna tab + sub-chart flow
- **Definition:** Question composer (text + moment timestamp); spawns a prasna sub-chart; links back to main chart.
- **Acceptance:** Prasna sub-chart computed server-side via E10; renders in same workbench tabs.
- **Effort:** 3 days

### T-E12.16: Source preferences settings page
- **Definition:** `family-preference-card.tsx`, `source-weight-slider.tsx`, Ultra toggle.
- **Acceptance:** PUT persists; UI reflects on next chart open; tests cover all 9 technique families.
- **Effort:** 3 days

### T-E12.17: Reading editor + TipTap integration
- **Definition:** Block-aware editor; template loader; per-block provenance attrs; diff tracker.
- **Acceptance:** Template renders; edits persist; blocks keep `fact_ref` metadata.
- **Effort:** 5 days

### T-E12.18: Reading diff signal service
- **Definition:** Backend: diff per-block on PUT; write `aggregation_signal` rows.
- **Acceptance:** Unit tests for accept/modify/reject classification; signals appear in E14a dashboards.
- **Effort:** 2 days

### T-E12.19: Reading PDF export
- **Definition:** Playwright-based renderer; A4 paginated; presigned URL.
- **Acceptance:** PDF renders correctly with all classical scripts (Devanagari, Tamil).
- **Effort:** 3 days

### T-E12.20: Classical citation panel + verse endpoint
- **Definition:** `/api/v1/classical/verses/{rule_id}` + `ClassicalCitationPanel` component.
- **Acceptance:** All 4 languages shown where available; cross-source comparison works.
- **Effort:** 3 days

### T-E12.21: Bulk chart import
- **Definition:** CSV/JSON upload, validation, batch compute job, progress UI.
- **Acceptance:** 100-row CSV completes in 5 min; errors reported per row.
- **Effort:** 4 days

### T-E12.22: Synastry tab
- **Definition:** Overlay chart rendering, aspect table, composite midpoint chart.
- **Acceptance:** Synastry computation matches reference (JH synastry).
- **Effort:** 4 days

### T-E12.23: i18n setup (en, hi, ta)
- **Definition:** next-intl + message catalogs + `SanskritTerm` component.
- **Acceptance:** Language switcher; all workbench strings localized; tests prevent new hardcoded strings.
- **Effort:** 3 days

### T-E12.24: Accessibility pass
- **Definition:** Keyboard nav, focus rings, ARIA labels, color-blind palette check.
- **Acceptance:** axe-core in Playwright passes; manual screen-reader pass on Natal tab.
- **Effort:** 2 days

### T-E12.25: Performance budget + Lighthouse CI
- **Definition:** CI step running Lighthouse against staging; budget file; alerts.
- **Acceptance:** Desktop perf ≥ 90, a11y ≥ 95; regressions block merge.
- **Effort:** 1 day

### T-E12.26: Documentation + onboarding
- **Definition:** `docs/markdown/astrologer-workbench.md`; in-app onboarding tour; keyboard shortcut overlay.
- **Acceptance:** Docs merged; tour triggers on first workbench visit.
- **Effort:** 2 days

## 8. Unit Tests

### 8.1 Chart style components (RTL)

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_north_indian_renders_all_9_planets` | NatalChartData with 9 planets | 9 planet labels in DOM | coverage |
| `test_south_indian_renders_12_houses_in_fixed_layout` | NatalChartData | 12 house cells in 4×4 grid with center empty | layout correctness |
| `test_east_indian_uses_cross_layout` | NatalChartData | cross-layout CSS class applied | style fidelity |
| `test_bengali_renders_nakshatras` | NatalChartData with nakshatra info | nakshatra labels present | unique-to-bengali feature |
| `test_western_wheel_uses_placidus_houses` | NatalChartData | placidus cusp lines drawn | Western convention |
| `test_all_styles_same_data_source` | single NatalChartData | all 5 styles render without type errors | abstraction correctness |

### 8.2 DasaTree (RTL + virtualization)

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_dasa_tree_renders_1_mahadasa_default` | Vimshottari data, default level 1 | 1 MD row rendered, collapsed | default view |
| `test_dasa_tree_expands_on_click` | click MD row | AD children load | lazy-expansion |
| `test_dasa_tree_level_5_renders_leaf_nodes` | expand to level 5 | 5-level path visible | depth supported |
| `test_dasa_tree_virtualization_cap` | 5000-node tree | only ~50 DOM nodes in viewport | virtualization active |

### 8.3 DasaBarTimeline (canvas testing via jsdom + canvas mock)

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_bar_timeline_zoom_levels` | year/decade/lifetime | span count changes appropriately | zoom works |
| `test_bar_timeline_current_period_highlighted` | spans containing `now()` | highlighted with `--accent-gold` | current-state UX |
| `test_bar_timeline_click_scrolls_tree` | click span | `onSpanClick` fires with matching lord + start | sync with tree |

### 8.4 AshtakavargaGrid

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_sarva_grid_renders_12_columns` | Sarva matrix | 12 sign columns | correctness |
| `test_cell_popover_shows_8_contributors` | click cell | popover with 8 contributor rows | drill-down works |
| `test_transit_bindu_overlay_toggle` | toggle on | overlay markers render | feature |
| `test_bhinna_matrix_7_rows` | matrix | 7 planet rows + 1 totals | structure |

### 8.5 YogaList

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_yoga_list_filters_by_source` | filter BPHS | only BPHS-sourced rows | filtering |
| `test_yoga_list_filters_by_active` | active-only | inactive rows hidden | filter UX |
| `test_yoga_list_click_opens_drawer` | click row | `ClassicalCitationPanel` opens with matching rule_id | navigation |
| `test_yoga_list_virtualization` | 250 yogas | < 30 DOM rows at once | virtualization |

### 8.6 ClassicalCitationPanel

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_citation_panel_renders_4_languages` | verse with IAST, Devanagari, Tamil, English | 4 language blocks in DOM | breadth |
| `test_citation_panel_cross_source_comparison` | rule with 3 source variants | 3 comparison rows | comparison UX |
| `test_citation_panel_lazy_loads` | panel closed | no fetch | perf |
| `test_citation_panel_loads_on_open` | panel opens | GET /api/v1/classical/verses/... fires | lazy load |

### 8.7 SourcePreferencesForm

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_preferences_save_on_change` | slide BPHS to 0.8 | debounced PUT fires | persistence |
| `test_preferences_ultra_toggle` | flip toggle | family set to ultra mode | ultra flow |
| `test_preferences_weight_normalization` | weights sum > 1 | visualize normalized sum | clarity |

### 8.8 ReadingEditor

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_reading_editor_loads_template` | chart_id | template fetched and blocks rendered | initial load |
| `test_reading_editor_preserves_fact_ref_attrs_on_edit` | edit paragraph text | `fact_ref` attr retained | provenance |
| `test_reading_editor_save_triggers_diff_signal` | modify block, save | `aggregation_signal` POST with `kind='modified'` | signal loop |
| `test_reading_editor_delete_block_signals_rejected` | delete block, save | signal `kind='rejected'` | signal attribution |
| `test_reading_editor_verbatim_block_signals_accepted` | no change | signal `kind='accepted'` | signal attribution |

### 8.9 Reading backend (pytest)

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_template_service_includes_provenance` | chart with yogas, dasa | ProseMirror blocks tagged with `fact_ref` | correctness |
| `test_reading_diff_service_classifies_modified` | old vs new block text | `kind='modified'` signal | diff logic |
| `test_reading_diff_service_classifies_rejected` | removed block | `kind='rejected'` | diff logic |
| `test_reading_export_playwright_generates_pdf` | reading doc | PDF binary returned; > 1KB | export works |
| `test_reading_export_fonts_render_devanagari` | block with Sanskrit | PDF contains Devanagari glyphs (font embed) | fidelity |

### 8.10 SourcePreferenceService (pytest)

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_preference_persistence` | PUT for family | row in `astrologer_source_preference` | persistence |
| `test_preference_applies_to_subsequent_reading_view` | preference set, open chart | reading-view reflects weighted aggregation | live application |
| `test_preference_cross_astrologer_isolation` | astrologer A preferences | astrologer B sees own, not A's | multi-tenant |

### 8.11 BulkImport

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_csv_import_validates_schema` | CSV with missing column | 400 with per-row errors | UX |
| `test_csv_import_parallel_compute` | 100 valid rows | all charts in DB within 5 min | throughput |
| `test_csv_import_partial_failure` | 95 valid, 5 invalid | 95 succeed, 5 reported | resilience |

### 8.12 Synastry

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_synastry_overlay_renders_two_planet_sets` | two charts | inner + outer rings render | overlay UI |
| `test_synastry_aspect_table_populates` | two charts | aspect rows with orb | correctness |
| `test_composite_midpoint_computation` | two charts | composite matches hand-calculated midpoints | math |

### 8.13 i18n

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_workbench_renders_tamil` | lang=ta | tab labels in Tamil | localization |
| `test_sanskrit_term_tooltip_in_hindi` | lang=hi, "raja-yoga" term | tooltip in Hindi | Sanskrit terms localized |
| `test_no_hardcoded_strings_check` | CI grep on components | 0 hardcoded English in JSX | enforcement |

### 8.14 Accessibility

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_axe_natal_tab_no_violations` | Natal tab | 0 violations | a11y baseline |
| `test_keyboard_tab_cycle` | Tab key through controls | focus order matches visual order | a11y |
| `test_color_blind_palette_pass` | Ashtakavarga heatmap | passes deuteranopia/protanopia simulators | inclusion |

### 8.15 Playwright end-to-end

| Test name | Flow | Assertion | Rationale |
|---|---|---|---|
| `e2e_open_chart_and_hydrate` | login → /workbench → click chart | Natal tab visible within 1s | perf budget |
| `e2e_switch_style` | open chart → style picker → South Indian | chart re-renders in South Indian | style picker works |
| `e2e_yoga_drill_down` | Yogas tab → click row → citation drawer | 4 languages visible | citation panel works |
| `e2e_source_pref_flow` | Settings → set BPHS for yogas → open chart | yoga source badges show BPHS | end-to-end prefs |
| `e2e_reading_template_to_pdf` | Reading new → edit → Export | PDF downloads | export works |
| `e2e_bulk_import_csv` | Import → upload CSV → progress → charts appear | 10 rows imported | bulk flow |
| `e2e_synastry_overlay` | Chart A → Synastry with B | overlay visible | synastry works |
| `e2e_keyboard_nav_shortcuts` | `?` → shortcut overlay | overlay appears | a11y |
| `e2e_tamil_ui_switch` | lang=ta → UI in Tamil | tab labels Tamil | i18n works |

## 9. EPIC-Level Acceptance Criteria

- [ ] `(pro)/workbench/*` route group live with astrologer-role gate
- [ ] All 10 chart tabs (Natal/Divisional/Dashas/Ashtakavarga/Yogas/Jaimini/Tajaka/Transits/KP/Prasna) functional
- [ ] All 5 chart styles render identical data correctly (North/South/East/Bengali/Western)
- [ ] Chart-reading-view hydration P95 < 300 ms on re-visit
- [ ] Source preferences page functional; preferences applied live to reading-view
- [ ] Classical citation panel renders verse in en + hi + ta + IAST + Devanagari where available
- [ ] Dasa tree supports 5 levels; bar timeline supports year/decade/lifetime zoom
- [ ] Reading editor loads template, edits persist, PDF export works with Devanagari + Tamil fonts
- [ ] Reading edits produce `aggregation_signal` rows (accepted/modified/rejected) per block
- [ ] Bulk import processes 100-row CSV in < 5 min
- [ ] Synastry with overlay + composite chart functional
- [ ] i18n: en, hi, ta fully localized; no hardcoded strings in `web/app/(pro)/`
- [ ] All frontend files ≤ 300 lines; zero `any` in workbench path; all colors via CSS vars
- [ ] Accessibility: Lighthouse a11y ≥ 95; axe-core CI passes; keyboard shortcuts documented
- [ ] Performance: Lighthouse desktop perf ≥ 90 for `/workbench/chart/[chartId]`
- [ ] Playwright e2e suite green
- [ ] Unit test coverage ≥ 85% for workbench components and services
- [ ] Documentation: `docs/markdown/astrologer-workbench.md` + in-app onboarding tour

## 10. Rollout Plan

- **Feature flag:** `WORKBENCH_UI_ENABLED` (default OFF; gated to astrologer-role users with `is_verified=true` at launch).
- **Shadow rollout:** 10 invited astrologers → 50 → public-for-verified astrologers over 4 weeks.
- **Backfill:** None required (workbench reads existing `chart_reading_view`). Bulk-import feature uses existing compute pipeline.
- **Rollback plan:** Flip flag OFF; route redirects to legacy `/dashboard`. No data migration required. Source preferences remain persisted.
- **Monitoring:**
  - Per-tab time-to-first-paint histograms.
  - Reading export success/failure rate.
  - PDF rendering duration P95.
  - Source preference adoption rate (% astrologers with ≥ 1 configured family).
  - Reading edit signal volume per day.
- **Onboarding:** Guided tour on first workbench visit; "Set up your lineage" suggestion modal linking to source preferences.

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Astrologers reject the workbench if it feels like a toy vs JH/Maitreya | Medium | High | Dogfood with 5 senior astrologers in weeks 1–3; iterate on feedback before public rollout |
| Devanagari / Tamil font rendering in PDF breaks | Medium | High | Font embedding tested in CI; bundled Noto Sans Devanagari + Noto Sans Tamil |
| Dasa tree performance collapses on deep expansion | Medium | Medium | Virtualization + canvas fallback for bar; performance budget in CI |
| Reading editor loses user edits on network blip | Low | High | Debounced autosave + local draft in indexedDB |
| Source preference change causes incorrect re-aggregation | Low | High | F8 aggregation tests cover all strategies; integration test for preference-change round-trip |
| Bulk import overwhelms compute queue | Medium | Medium | Per-astrologer rate limit; queue-depth alerts |
| Synastry composite math disagrees with JH | Medium | Medium | Golden chart suite includes synastry pairs; diff against JH output |
| Localization regressions as new strings added | High | Low | CI check greps for English in JSX outside en.json |
| i18n RTL support (future Arabic tradition PRDs) | Low | Low | Design with logical CSS properties (margin-inline-start vs margin-left) |
| Accessibility regressions slip in | Medium | Medium | axe-core in Playwright; manual screen-reader pass per release |
| Workbench leaks end-user features / feature-parity confusion | Low | Medium | Clear nav separation; "Back to dashboard" link |
| Per-tenant chart isolation bug leaks across astrologers | Low | Very High | Repository-level org filter tests; penetration test |
| SSR/CSR hydration mismatch re-emerges | Low | Medium | Mirror dashboard pattern: client-only WorkbenchShell |
| PDF generator exhausts server memory | Medium | Medium | Queue-based worker; per-job 30s timeout; memory cap per render |
| Keyboard shortcut conflicts with browser shortcuts | Medium | Low | Shortcut overlay shows conflicts; configurable |
| Bundle size explosion (TipTap, virtualization, canvas libs) | Medium | Medium | Route-level code splitting; bundle-size budget in CI |

## 12. References

- Master spec: [`docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`](../../../superpowers/specs/2026-04-19-classical-techniques-expansion-design.md) §1.2, §1.4, §1.6
- Source preferences (data model): [`P0/F8-technique-result-aggregation-protocol.md`](../P0/F8-technique-result-aggregation-protocol.md)
- Reading view (data source): [`P0/F9-chart-reading-view-table.md`](../P0/F9-chart-reading-view-table.md)
- Citation envelope: [`P0/F11-citation-embedded-responses.md`](../P0/F11-citation-embedded-responses.md)
- Ultra AI (chat integration): [`P2/E11b-ai-chat-debate-mode.md`](./E11b-ai-chat-debate-mode.md)
- End-user sibling surface: [`P2/E13-end-user-simplification-ui.md`](./E13-end-user-simplification-ui.md)
- Experimentation (signal loop): [`P1/E14a-experimentation-framework-v1.md`](../P1/E14a-experimentation-framework-v1.md)
- Frontend conventions: [`CLAUDE.md`](../../../../CLAUDE.md) → "Frontend Conventions (MUST FOLLOW)"
- Reference implementations: Jagannatha Hora 7.x, Maitreya9 (visual parity targets)
- TipTap: https://tiptap.dev (reading editor)
- next-intl: https://next-intl-docs.vercel.app (i18n)
