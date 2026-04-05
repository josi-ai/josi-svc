# Frontend Architecture Remediation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix all 7 structural issues identified in the April 2026 frontend architecture review — type safety, god components, duplicate types, localStorage validation, Turbopack/HMR fragility, styling inconsistencies, and missing service layer.

**Architecture:** Bottom-up remediation. First establish the type foundation (centralized types from backend API shapes). Then split god components using those types. Then consolidate styling, fix widget system, remove dead code, and add response validation.

**Tech Stack:** Next.js 16, React 19, TypeScript strict, TanStack React Query, Tailwind CSS v4, Clerk Auth, zod for validation

---

## Dependency DAG

```
Wave 0 (parallel — no dependencies):
  T1: Centralized types (web/types/api.ts)
  T2: Dead code removal (SubscriptionContext, GraphQL client)
  T3: Hardcoded colors → CSS variables

Wave 1 (depends on T1):
  T4: API client response validation
  T5: Split charts/page.tsx (1627 lines)
  T6: Split charts/[chartId]/page.tsx (1083 lines)
  T7: Split persons/page.tsx (1112 lines)

Wave 2 (depends on T1, T4):
  T8: Widget system — typed queryFns, dynamic import loading states
  T9: localStorage validation with zod
  T10: Split remaining large pages (transits, panchang, settings, compatibility, dasha)

Wave 3 (depends on all above):
  T11: Final audit — remove all remaining <any>, verify strict mode, test
```

---

## Task 1: Centralized Type Definitions

**Files:**
- Create: `web/types/api.ts` — all API response types
- Create: `web/types/index.ts` — barrel export
- Delete duplicate types from: all page files that redefine Person, Chart, PlanetData, etc.

**Goal:** Single source of truth for all TypeScript types. Generated from backend model/controller analysis.

The complete `api.ts` file content is provided by the backend API analysis (see agent output). Contains ~500 lines covering: ResponseModel, Person, AstrologyChart, PlanetPosition, TransitData, DashaPeriod, PredictionCategory, AstrologerResponse, ConsultationResponse, CulturalEvent, and endpoint type aliases.

---

## Task 2: Dead Code Removal

**Files:**
- Delete: `web/contexts/SubscriptionContext.tsx` (defined but never imported anywhere)
- Delete: `web/lib/graphql-client.ts` (GraphQL client exists but unused — no GraphQL queries in frontend)
- Modify: `web/components/providers.tsx` — remove SubscriptionProvider if imported there

---

## Task 3: Hardcoded Colors → CSS Variables

**Files:**
- Modify: `web/app/(dashboard)/consultations/page.tsx` — TYPE_GRAD hardcoded gradients
- Modify: `web/components/charts/chart-visualizations.tsx` — SIGN_ELEMENT_COLORS hardcoded hex
- Modify: `web/app/(dashboard)/astrologers/page.tsx` — hardcoded gradient colors for avatar backgrounds
- Modify: `web/app/globals.css` — add missing CSS variables for consultation type colors, element colors

Audit: `grep -rn '#[0-9A-Fa-f]\{6\}' web/app web/components --include="*.tsx" | grep -v node_modules | grep -v .next`

---

## Task 4: API Client Response Validation

**Files:**
- Modify: `web/lib/api-client.ts` — add generic response validation
- Create: `web/lib/api-helpers.ts` — typed helper functions for common API patterns (extracting nested arrays, etc.)

Key changes:
- `apiClient.get<T>()` should validate that response has `{ success, data }` shape
- Add `extractArray<T>(response, key)` helper for nested array responses like `{ astrologers: [] }`
- Add `extractData<T>(response)` helper that handles the `ResponseModel` unwrapping

---

## Task 5: Split charts/page.tsx (1627 lines → ~5 files)

**Files:**
- Keep: `web/app/(dashboard)/charts/page.tsx` — page shell, state, query (< 150 lines)
- Create: `web/app/(dashboard)/charts/_components/chart-grid-card.tsx` — grid view card
- Create: `web/app/(dashboard)/charts/_components/chart-list-view.tsx` — list/table view
- Create: `web/app/(dashboard)/charts/_components/chart-filters.tsx` — filter bar + view mode toggle
- Create: `web/app/(dashboard)/charts/_components/chart-empty.tsx` — empty/loading states
- Create: `web/app/(dashboard)/charts/_components/mini-chart.tsx` — mini chart visualization (if exists inline)

---

## Task 6: Split charts/[chartId]/page.tsx (1083 lines → ~5 files)

**Files:**
- Keep: `web/app/(dashboard)/charts/[chartId]/page.tsx` — page shell, queries (< 150 lines)
- Create: `web/app/(dashboard)/charts/[chartId]/_components/overview-tab.tsx`
- Create: `web/app/(dashboard)/charts/[chartId]/_components/planets-tab.tsx`
- Create: `web/app/(dashboard)/charts/[chartId]/_components/houses-tab.tsx`
- Create: `web/app/(dashboard)/charts/[chartId]/_components/aspects-tab.tsx`
- Create: `web/app/(dashboard)/charts/[chartId]/_components/chart-header.tsx` — title, dropdowns, delete button

---

## Task 7: Split persons/page.tsx (1112 lines → ~4 files)

**Files:**
- Keep: `web/app/(dashboard)/persons/page.tsx` — page shell (< 150 lines)
- Create: `web/app/(dashboard)/persons/_components/person-card.tsx`
- Create: `web/app/(dashboard)/persons/_components/person-form-modal.tsx`
- Create: `web/app/(dashboard)/persons/_components/person-list.tsx`

---

## Task 8: Widget System — Typed queryFns + Dynamic Import Loading

**Files:**
- Modify: `web/components/dashboard/widget-grid.tsx` — add `loading` component to all `dynamic()` calls
- Modify: all widget files in `web/components/dashboard/widgets/` — replace `<any>` with proper types from `web/types/api.ts`, ensure all data transformation happens in queryFn

---

## Task 9: localStorage Validation with zod

**Files:**
- Modify: `web/hooks/use-widget-layout.ts` — validate localStorage data with zod schema before using
- Create: `web/lib/storage.ts` — typed localStorage helpers with zod validation

---

## Task 10: Split Remaining Large Pages

**Files over 500 lines to split:**
- `web/app/(dashboard)/transits/page.tsx` (893 lines)
- `web/app/(dashboard)/panchang/page.tsx` (839 lines)
- `web/app/(dashboard)/settings/page.tsx` (721 lines)
- `web/app/(dashboard)/compatibility/page.tsx` (669 lines)
- `web/app/(dashboard)/dasha/page.tsx` (601 lines)
- `web/app/(dashboard)/charts/new/page.tsx` (559 lines)
- `web/app/(dashboard)/ai/page.tsx` (538 lines)

Each split into page shell (< 200 lines) + co-located `_components/` directory.

---

## Task 11: Final Audit

- Run `grep -rn '<any>' web/app web/components web/hooks --include="*.tsx" --include="*.ts"` — should return 0 results
- Run `npx tsc --noEmit --strict` — should pass with 0 errors
- Verify all pages load without console errors
- Verify HMR works on widget changes without restart
- Commit and push
