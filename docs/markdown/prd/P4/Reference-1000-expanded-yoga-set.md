---
prd_id: Reference-1000
epic_id: Reference-1000
title: "Expanded 1000-yoga reference set (editorial + community ingestion)"
phase: P4-scale-100m
tags: [#correctness, #i18n, #extensibility]
priority: should
depends_on: [E4a, E4b, F6, F16, P3-E2-console, S8]
enables: [I10, D3, Research]
classical_sources: [bphs, saravali, phaladeepika, jataka_parijata, jataka_bharanam, modern_commentaries]
estimated_effort: 12-16 weeks (editorial-limited, parallelizable)
status: draft
author: "@agent"
last_updated: 2026-04-19
---

# Reference-1000 — Expanded 1000-Yoga Reference Set

## 1. Purpose & Rationale

P2's E4b delivered 250 yogas — the "comprehensive core" — drawn from the most-cited subsets of BPHS, Saravali, Phaladeepika, and modern reference implementations (Jagannatha Hora, Maitreya9). This is already competitive with every commercial and open astrology tool in existence.

The long tail is larger. Full BPHS alone catalogs ~300 yogas; Saravali adds ~200 not in BPHS; Phaladeepika adds ~150; Jataka Parijata and Jataka Bharanam add another ~350 between them; modern commentaries contain thousands of identified variants. A reasonable target for the first extended wave is **1000+ yogas** — enough to cover every yoga a practicing Vedic astrologer will reference, while remaining editorially tractable.

This is not primarily an engineering challenge (F6's rule DSL is already expressive; S8 already handles safe rollouts). It is an **editorial and community-content challenge**: classical advisors reading primary sources, drafting rule YAMLs, dual-reviewing with engineers, authoring golden-chart tests, and shipping in controlled waves.

The outcome, at 100M users scale: the most comprehensive computational yoga catalogue in existence. Marketing positioning writes itself.

## 2. Scope

### 2.1 In scope

- Additional 750+ yogas on top of P2's 250, across the six classical sources listed above
- Per-yoga deliverables: rule YAML (F6), verse citation, classical names (English / Sanskrit IAST / Devanagari / Tamil where applicable), golden-chart test fixtures
- Editorial workflow tooling (extending P3-E2-console) for classical advisors who are not engineers
- Community contribution path: external advisors with limited authoring rights, gated approvals
- Shipping model: 0% flag at merge, promoted on demand via S8, typically activated for astrologer pro-mode first, then B2C
- Taxonomy: categorize yogas by type (raja, dhana, daridra, sanyasa, arishta, parivartana, …), by classical source, by required planets
- Search + discovery UI in astrologer workbench (E12) scoped for pro-mode consumption
- Quality gates: editor review, classical advisor sign-off, engineer code review, golden-chart suite green
- Localization layer: canonical Sanskrit names in Devanagari, IAST romanization, Tamil for Tamil user base, English display names
- Classical-source attribution fidelity: every yoga cites exact chapter:verse; advisors sign off on citation accuracy
- Observability: per-yoga activation rate, cross-source agreement (which yogas with the same name differ between sources), marketing-facing dashboard of catalog size

### 2.2 Out of scope

- The 10,000-yoga reference set (I10, P6) — this is its foundation but not its scope
- Interpretation templates per yoga — separate from rules; handled by E12 and AI chat
- Non-Vedic yogas (Western aspect patterns, Chinese-astrology star combinations) — different epistemic traditions, not yoga in the classical sense
- Commercial licensing of rule YAML — all rules ship open (explicit non-goal in master spec §7)
- Algorithmic yoga discovery from historical texts via NLP — research direction; not editorial
- Classical commentary translation services — curated by advisors
- End-user (B2C) surfacing of long-tail yogas by default — complexity overwhelm; gated behind tier / pro mode

### 2.3 Dependencies

- **E4a / E4b** — the yoga engine and 250-yoga baseline
- **F6** — rule DSL and YAML loader (every yoga ships through this)
- **F16** — golden-chart suite scaffolding (every yoga needs a fixture)
- **P3-E2-console** — rule authoring console; must support bulk authoring and classical-advisor UX
- **S8** — shadow-compute promotion infrastructure (every activation gated)
- **Language data** — Sanskrit Unicode corpus, Tamil transliteration
- Editorial team: at least 3 classical advisors under contract, reading native-language primary sources

## 3. Classical & Technical Research

### 3.1 Source coverage inventory

| Source | Approx. yoga count | Coverage in P2 | Target added in P4 |
|---|---:|---:|---:|
| Brihat Parashara Hora Shastra (BPHS) | ~300 | ~120 | +180 |
| Saravali (Kalyanavarma) | ~200 | ~60 | +140 |
| Phaladeepika (Mantreswara) | ~150 | ~40 | +110 |
| Jataka Parijata (Vaidyanatha) | ~200 | ~20 | +180 |
| Jataka Bharanam (Dhundiraja) | ~150 | ~10 | +140 |
| Modern commentaries (Raman, Rao, Sharma, …) | ~200 | ~0 | ~100 |
| **Total** | **~1200** | **~250** | **+~750 → ≥1000** |

Modern commentaries contain many reformulations and hybrids; we include only those with clear classical grounding cited by the commentator. Speculative yogas from contemporary authors are deferred to I10.

### 3.2 Per-yoga content contract

Every yoga ships as one YAML file under `src/josi/db/rules/yogas/{source}/{yoga_slug}.{version}.yaml`:

```yaml
rule_id: saravali/amsavatara
source_id: saravali
version: 1.0.0
content_hash: <sha256-filled-by-loader>
technique_family_id: yoga
output_shape_id: boolean_with_strength

citation: "Saravali Ch.39 v.21-23"

classical_names:
  en: "Amsavatara Yoga"
  sa_iast: "aṃśāvatāra yoga"
  sa_devanagari: "अंशावतार योग"
  ta: "அம்சாவதார யோகம்"

taxonomy:
  type: [raja]                   # raja, dhana, daridra, arishta, sanyasa, parivartana, nabhasa, …
  source_chapter: "Ch.39"
  classical_variants: ["saravali_ch39_v21_v23"]

prerequisites:
  planets_needed: [jupiter, venus, mercury]

rule_body:
  description: "Three or more benefics in kendras from Lagna, with at least one in the 10th."
  expression:
    AND:
      - count:
          source: { planets: [jupiter, venus, mercury, moon_if_waxing] }
          where: { house_from: "lagna", house_in: [1,4,7,10] }
          at_least: 3
      - any:
          source: { planets: [jupiter, venus, mercury] }
          where: { house_from: "lagna", house_in: [10] }

strength_calculation:
  method: "benefic_count_weighted_by_dig_bala"
  formula: "min(1.0, 0.25 * benefic_count + 0.15 * dig_bala_bonus)"

expected_rate:                   # steady-state activation rate; guides shadow thresholds
  min: 0.03
  max: 0.12

golden_charts:                   # references to fixtures; MUST include at least 2 positive + 1 negative
  positive:
    - tests/golden/charts/amsavatara_positive_01.yaml
    - tests/golden/charts/amsavatara_positive_02.yaml
  negative:
    - tests/golden/charts/amsavatara_negative_01.yaml

editor_notes: |
  Rechecked Kalyanavarma v.21-23 in Santhanam translation 1983 ed. pp.218-220.
  Modern commentators (Raman) sometimes include Moon regardless of waxing;
  we opt for stricter reading per primary source. See discussion thread #721.

reviewed_by:
  classical_advisor: "Dr. K. Venkatesan"
  engineer: "@agent"
  reviewed_at: 2026-05-12
```

### 3.3 Editorial workflow

Five-stage workflow, enforced in P3-E2-console:

1. **Draft** — classical advisor selects yoga from a "todo inventory" of missing yogas per source, reads primary source verse(s), authors rule YAML in console (with DSL form assistance).
2. **Self-review** — advisor writes ≥2 positive + ≥1 negative golden charts. Console runs rule, confirms expected classifications.
3. **Engineer review** — engineer checks DSL correctness, structural validity (F6), JSON Schema pass (F5), code style.
4. **Advisor dual-review** — a second classical advisor independently reviews citation accuracy and interpretation fidelity. Disagreements escalate to lead advisor.
5. **Merge + 0% flag** — rule enters `classical_rule` at merge but with 0% rollout flag. Activation is separate.

Target throughput: 4 advisors × 5 yogas/week sustainable = ~20 yogas/week. To reach +750 yogas: 38 weeks realistic, 16 weeks aggressive if a second advisor cohort onboards.

### 3.4 Activation waves

Activations happen in **waves** grouped by source + category, not individually, for operational sanity:

- **Wave 1** (month 1): +100 yogas (BPHS long tail — raja / dhana / arishta variants)
- **Wave 2** (month 2): +150 yogas (Saravali)
- **Wave 3** (month 3): +120 yogas (Phaladeepika)
- **Wave 4** (month 4): +180 yogas (Jataka Parijata)
- **Wave 5** (month 5): +140 yogas (Jataka Bharanam)
- **Wave 6** (month 6): +100 yogas (modern commentary-grounded)

Each wave: 0% → astrologer-pro-mode only (10%) → full pro-mode (100%) → B2C (100%). Each stage reuses S8 gates and monitors astrologer override rate as the primary signal.

### 3.5 Community contribution path

Beyond the core editorial team, selected external classical advisors can contribute via:

- Signed CLA (classical advisors' version)
- Draft authoring in console with `external_contributor` role
- Submissions go to a queue visible to the lead advisor for triage
- Contributor is credited in `reviewed_by.external_contributors` when merged

At most 20% of a wave's yogas come from external contributors — maintains editorial quality.

### 3.6 Classical-source attribution fidelity

Concrete anti-cases we reject:

- Citing "BPHS Ch.36" without verse numbers
- Citing "as per Raman" when Raman himself is a secondary source — cite Raman's source
- Paraphrased rules without the original verse's native-language text (at least IAST transliteration)

Every citation must survive "open the named translation edition, find the verse, verify it says what we claim." Advisor dual-review enforces this.

### 3.7 Long-tail yogas at 0% flag

Many of these yogas activate on < 0.5% of charts. Keeping them at 0% until explicit activation protects dashboards from noise. Activation triggers:

- Astrologer demand ("I need Pushkala yoga for a client reading")
- B2B tenant request (for tenants whose lineage emphasizes specific yogas)
- Editorial completion of a category (e.g., "all Saravali dhana yogas ready — activate as a group")

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| Target count | 1000+ (stretch 1200) | Editorially tractable in 4–6 months; clear marketing round number |
| Include modern-commentary yogas | Only when commentator cites a classical source; not Raman-original yogas | Purity of classical attribution |
| Localization scope | English, Sanskrit IAST, Devanagari always; Tamil when audience justifies | Aligns with Indian diaspora focus in product vision |
| Authoring access | Console only (no direct YAML PR from advisors) | UX + validation; engineers PR final YAMLs |
| Golden chart count per yoga | ≥2 positive + ≥1 negative, minimum | Baseline coverage; more encouraged |
| Dual-review required | Yes, second advisor | Non-negotiable for trust |
| Versioning | Every yoga starts at 1.0.0 on first merge | Consistent across catalog |
| Default activation | 0% at merge | Safety; explicit activation via S8 |
| Wave cadence | Monthly | Matches advisor throughput |
| External contributor limit | 20% per wave | Editorial quality control |
| Overlap handling (same yoga in multiple sources) | Separate rule_id per source | Preserves source-authority distinction; aggregation layer handles consensus |
| Dashboards | Catalog size, per-source coverage, per-category coverage | Marketing-facing and internal |
| i18n target set | Begin with 100 highest-utility yogas for Tamil/Devanagari; full set later | Tractability |
| Search indexing | Postgres full-text on `classical_names` + taxonomy | Simple; upgrades to vector later |

## 5. Component Design

### 5.1 New services / modules

```
src/josi/services/yoga_catalog/
├── __init__.py
├── catalog_inventory.py            # tracks "todo" list of missing yogas per source
├── editorial_workflow.py           # state machine: draft → self_reviewed → eng_reviewed → adv_reviewed → merged
├── wave_activator.py               # batch activation via S8 for a category/source
├── taxonomy_service.py             # type, source_chapter, category filtering
├── name_localization.py            # script conversion IAST ↔ Devanagari; Tamil lookups
└── search_indexer.py               # maintains Postgres FTS index on names

src/josi/db/rules/yogas/             # the growing rule repository
├── bphs/
├── saravali/
├── phaladeepika/
├── jataka_parijata/
├── jataka_bharanam/
└── modern/

src/josi/api/v1/controllers/
└── yoga_catalog_controller.py

web/app/(admin)/console/yogas/
├── page.tsx                        # catalog dashboard
├── inventory/page.tsx              # todo list per advisor
├── author/[yoga_id]/page.tsx       # authoring form
├── wave/[wave_id]/page.tsx         # wave activation view
└── components/
    ├── YogaEditor.tsx
    ├── GoldenChartTester.tsx
    ├── CitationValidator.tsx
    └── DualReviewDialog.tsx

tests/golden/charts/                # fixture repository, grows with catalog
```

### 5.2 Data model additions

Most model extensions are in existing tables:

```sql
-- Extend classical_rule metadata (F4 already has rule_id, version; we add metadata)
ALTER TABLE classical_rule
  ADD COLUMN editorial_status TEXT NOT NULL DEFAULT 'merged'
    CHECK (editorial_status IN ('draft','self_reviewed','eng_reviewed','adv_reviewed','merged')),
  ADD COLUMN primary_advisor_id UUID REFERENCES "user"(user_id),
  ADD COLUMN secondary_advisor_id UUID REFERENCES "user"(user_id),
  ADD COLUMN engineer_reviewer_id UUID REFERENCES "user"(user_id),
  ADD COLUMN activation_wave_id UUID;

-- Wave tracking
CREATE TABLE yoga_activation_wave (
    id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    wave_number           INTEGER NOT NULL,
    source_id             TEXT REFERENCES source_authority(source_id),
    name                  TEXT NOT NULL,
    target_yoga_count     INTEGER NOT NULL,
    activated_yoga_count  INTEGER NOT NULL DEFAULT 0,
    status                TEXT NOT NULL CHECK (status IN ('planned','in_review','activating_pro','activating_full','closed')),
    notes                 TEXT,
    created_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
    closed_at             TIMESTAMPTZ
);

-- Yoga taxonomy (multi-valued, searchable)
CREATE TABLE yoga_taxonomy (
    rule_id               TEXT NOT NULL,
    source_id             TEXT NOT NULL,
    version               TEXT NOT NULL,
    taxonomy_key          TEXT NOT NULL,          -- 'type' | 'source_chapter' | 'category' | …
    taxonomy_value        TEXT NOT NULL,
    PRIMARY KEY (rule_id, source_id, version, taxonomy_key, taxonomy_value),
    FOREIGN KEY (rule_id, source_id, version)
        REFERENCES classical_rule(rule_id, source_id, version)
);

CREATE INDEX idx_yoga_taxonomy_value ON yoga_taxonomy(taxonomy_key, taxonomy_value);

-- Editorial todo inventory
CREATE TABLE yoga_catalog_inventory (
    id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id            TEXT NOT NULL REFERENCES source_authority(source_id),
    yoga_slug            TEXT NOT NULL,
    citation             TEXT NOT NULL,
    status               TEXT NOT NULL CHECK (status IN ('todo','in_progress','drafted','merged','deferred')),
    assigned_to          UUID REFERENCES "user"(user_id),
    priority             INTEGER DEFAULT 100,
    notes                TEXT,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (source_id, yoga_slug)
);

-- External contributor attribution
CREATE TABLE yoga_external_contributor (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_id           TEXT NOT NULL,
    source_id         TEXT NOT NULL,
    version           TEXT NOT NULL,
    contributor_name  TEXT NOT NULL,
    contributor_affiliation TEXT,
    cla_signed_at     TIMESTAMPTZ NOT NULL,
    FOREIGN KEY (rule_id, source_id, version)
        REFERENCES classical_rule(rule_id, source_id, version)
);
```

### 5.3 API contract

**Public:**

```
GET /api/v1/yogas                      # list (paginated, filterable)
Query: source_id?, type?, category?, q? (free-text), language?=en
Response: { items: [...], total, page, per_page }

GET /api/v1/yogas/{rule_id}
Response: full yoga detail incl. classical_names, taxonomy, citation

GET /api/v1/yogas/{rule_id}/chart/{chart_id}
Response: activation state + strength for the specified chart, respecting flag
```

**Internal/admin:**

```
POST /api/v1/admin/yoga-catalog/inventory/seed
Body: YAML inventory file
Response: created entries, errors

GET /api/v1/admin/yoga-catalog/inventory
Query: source_id?, status?, assigned_to?
Response: todo list for dashboard

POST /api/v1/admin/yoga-catalog/inventory/{id}/claim
Response: assigned_to = caller

POST /api/v1/admin/yoga-catalog/drafts
Body: draft YAML
Response: draft_id; runs F5 validation + golden-chart preflight

POST /api/v1/admin/yoga-catalog/drafts/{id}/submit-for-review
Response: status = 'eng_reviewed' pending

POST /api/v1/admin/yoga-catalog/drafts/{id}/approve
Body: role = 'engineer' | 'classical_advisor' | 'secondary_advisor'
Response: updated editorial_status

POST /api/v1/admin/yoga-catalog/waves
Body: wave spec (source, target count, category)
Response: wave_id, eligible rule ids

POST /api/v1/admin/yoga-catalog/waves/{id}/activate-pro
POST /api/v1/admin/yoga-catalog/waves/{id}/activate-full
POST /api/v1/admin/yoga-catalog/waves/{id}/close

GET /api/v1/admin/yoga-catalog/coverage
Response: { total, by_source: {bphs: n, …}, by_type: {raja: n, …} }
```

**Internal Python:**

```python
# src/josi/services/yoga_catalog/editorial_workflow.py

class EditorialWorkflow:
    async def claim_inventory_item(self, inventory_id: UUID, user_id: UUID) -> None: ...
    async def submit_draft(self, yaml_body: str, author_id: UUID) -> DraftResult: ...
    async def approve(self, rule_id: str, version: str, approver_id: UUID, role: ReviewRole) -> None: ...
    async def merge(self, rule_id: str, version: str) -> None:
        """Writes to classical_rule with editorial_status='merged', flag at 0%."""

# src/josi/services/yoga_catalog/wave_activator.py

class WaveActivator:
    async def create_wave(self, source_id: str, target_count: int, name: str) -> Wave: ...
    async def activate_pro_mode(self, wave_id: UUID) -> list[PromotionId]:
        """Creates per-yoga S8 promotions scoped to astrologer pro mode."""
    async def activate_full(self, wave_id: UUID) -> list[PromotionId]: ...
```

## 6. User Stories

### US-R1000.1: As a classical advisor, I want a todo list of missing yogas grouped by source
**Acceptance:** inventory endpoint returns prioritized list; advisor can claim items; claimed items show in personal queue.

### US-R1000.2: As a classical advisor, I want to author a yoga rule without writing Python
**Acceptance:** P3-E2-console yoga authoring form accepts DSL via structured UI; validator runs on save; golden-chart test runner integrated in UI.

### US-R1000.3: As a product manager, I want to see catalog size grow in real time
**Acceptance:** `/admin/yoga-catalog/coverage` returns counts by source and type; public marketing page auto-updates monthly.

### US-R1000.4: As a pro-mode astrologer, I want to search the catalog by type and source
**Acceptance:** astrologer workbench search for "Saravali raja yogas" returns matching yogas with citation and expected activation rate.

### US-R1000.5: As an end user speaking Tamil, I want yoga names in my language
**Acceptance:** when locale is `ta`, yoga display uses `classical_names.ta` (falling back to Devanagari, then IAST, then English).

### US-R1000.6: As engineering, I want to activate an entire wave with a single action
**Acceptance:** wave activator creates S8 promotions for all yogas in the wave; admin UI shows progress; per-yoga auto-halt via gates applies normally.

### US-R1000.7: As an external classical advisor, I want to contribute a yoga draft
**Acceptance:** contributor with signed CLA and `external_contributor` role can author drafts; drafts route to lead advisor for triage; credited in metadata on merge.

### US-R1000.8: As research / Research PRD, I want to analyze cross-source agreement for the full catalog
**Acceptance:** OLAP mart (S4) computes per-yoga activation rate per source and pairwise source agreement; feeds `Research-cross-source-agreement-dataset.md`.

## 7. Tasks

### T-R1000.1: Seed inventory
- **Definition:** Advisors (or interim LLM-assisted draft pass reviewed by advisors) produce inventory rows for ~1200 candidate yogas across the six sources with citations and short descriptions. Load into `yoga_catalog_inventory`.
- **Acceptance:** Inventory table has ≥ 1200 rows; each has citation; coverage stats dashboard reports counts.
- **Effort:** 2 weeks editorial + 1 week tooling

### T-R1000.2: Extend P3-E2-console for yoga authoring
- **Definition:** Authoring form with DSL builder (and raw JSON fallback), localization fields, taxonomy multi-select, golden-chart test runner, citation validator. Integrates with drafts endpoint.
- **Acceptance:** Advisor walkthrough: author, test, submit a yoga end-to-end without engineer assistance.
- **Effort:** 3 weeks
- **Depends on:** P3-E2-console

### T-R1000.3: Editorial workflow state machine
- **Definition:** `EditorialWorkflow` enforces draft → self_reviewed → eng_reviewed → adv_reviewed → merged with role gates. Rejection bounces to prior state with notes.
- **Acceptance:** State transitions tested; illegal transitions rejected; notifications sent on status change.
- **Effort:** 1 week
- **Depends on:** T-R1000.2

### T-R1000.4: Wave activator with S8 integration
- **Definition:** Creates S8 promotions for each yoga in a wave, scoped first to pro-mode users, then full. Aggregates progress at wave level. Auto-halts entire wave if > 3 yogas hit their individual gate fails.
- **Acceptance:** Wave activation end-to-end in staging with 20 dummy yogas completes within 72 h; any simulated gate fail correctly halts.
- **Effort:** 2 weeks
- **Depends on:** S8, T-R1000.3

### T-R1000.5: Localization layer
- **Definition:** `NameLocalization` service for IAST ↔ Devanagari conversion (Aksharamukha or equivalent) and Tamil via curated lookup table. API responses respect `Accept-Language`.
- **Acceptance:** Conversion round-trips on 100 test strings; Tamil fallback works; CI test on catalog coverage.
- **Effort:** 1 week

### T-R1000.6: Search + discovery surface
- **Definition:** Postgres FTS index on `classical_names` + taxonomy values; `/api/v1/yogas` with query parameters; admin search UI in catalog dashboard.
- **Acceptance:** "raja saravali" returns expected Saravali raja yogas; search latency < 100 ms P95 at 2k yogas.
- **Effort:** 1 week
- **Depends on:** T-R1000.3

### T-R1000.7: External contributor path
- **Definition:** `external_contributor` role; CLA tracking table; draft queue view for lead advisor; attribution on merge.
- **Acceptance:** External contributor demo user signs CLA, submits draft, advisor accepts; merged rule shows contributor attribution.
- **Effort:** 1 week
- **Depends on:** T-R1000.3

### T-R1000.8: Golden-chart authoring helpers
- **Definition:** Chart generator for common patterns ("put Moon in Pisces, Jupiter in Cancer"); asserts positive/negative expectation; bulk validator.
- **Acceptance:** Advisor can produce 3 fixtures per yoga in < 15 minutes using tool.
- **Effort:** 1 week
- **Depends on:** F16

### T-R1000.9: Author 750 yogas (editorial campaign)
- **Definition:** The work itself — 4 advisors × 5 yogas/week. Per yoga: read primary source, draft in console, write fixtures, submit for review, address feedback, merge.
- **Acceptance:** 750 yoga YAMLs merged; all pass CI + golden chart suite; editorial_status = 'merged' for all.
- **Effort:** 38 weeks steady-state (16 weeks stretch with larger team)
- **Depends on:** T-R1000.2 through T-R1000.8

### T-R1000.10: Wave rollouts
- **Definition:** 6 waves × (pro-mode activation → full activation), each 2 weeks. Interleaved with authoring.
- **Acceptance:** All 6 waves closed; catalog at ≥ 1000 activated yogas.
- **Effort:** 24 weeks overlapping
- **Depends on:** T-R1000.4, T-R1000.9

### T-R1000.11: Public catalog + marketing page
- **Definition:** `/yogas` public page listing all activated yogas with search, source filter, category filter. Shareable per-yoga pages.
- **Acceptance:** SEO-friendly URLs; catalog count visible on landing page; shareable.
- **Effort:** 1 week

### T-R1000.12: Research dataset integration
- **Definition:** Ensure S4 OLAP marts include per-yoga activation statistics feeding `Research-cross-source-agreement-dataset.md`. Reviewed with research stakeholders.
- **Acceptance:** Sample dataset query runs; numbers consistent with OLTP sampling.
- **Effort:** 3 days
- **Depends on:** S4

## 8. Unit Tests

### 8.1 catalog_inventory

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_seed_inventory_idempotent` | seed file run twice | no duplicates | seed safety |
| `test_claim_inventory_transition` | claim todo item | status='in_progress', assigned_to=user | workflow |
| `test_cannot_claim_merged_item` | claim already-merged item | 409 | state guard |
| `test_priority_ordering` | list with priorities 1,50,100 | returns in ascending order | UX |

### 8.2 editorial_workflow

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_draft_submission_runs_validator` | malformed YAML | draft creation fails with F5/F6 error | validation gate |
| `test_draft_requires_golden_charts` | draft with 0 positive fixtures | submission rejected | content contract |
| `test_eng_review_approval_advances_state` | approve with role=engineer | status='eng_reviewed' | transition |
| `test_adv_review_must_be_different_user` | primary advisor approves as secondary | 409 | dual-control |
| `test_external_contributor_cannot_approve` | external approver | 403 | permission |
| `test_merge_writes_classical_rule_row` | full approval chain | new row in `classical_rule` with editorial_status='merged' | integration |

### 8.3 wave_activator

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_wave_creation_groups_eligible_rules` | wave for saravali raja | rules matching filter included | grouping |
| `test_activate_pro_creates_s8_promotion_per_yoga` | 10-yoga wave | 10 S8 promotions at pro-mode scope | integration |
| `test_wave_auto_halt_on_threshold_gate_fails` | 4 yogas fail individual gate | wave halted with reason | safety |
| `test_activate_full_after_pro_stable` | pro-stable for 72h | full activation allowed | staged rollout |

### 8.4 name_localization

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_iast_to_devanagari_roundtrip` | "aṃśāvatāra yoga" | "अंशावतार योग" | script conversion |
| `test_tamil_fallback_to_devanagari` | locale=ta, ta name missing | returns Devanagari | graceful degradation |
| `test_english_always_present` | any yoga | en key non-empty | invariant |

### 8.5 taxonomy_service + search

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_taxonomy_filter_by_type` | type=raja | only raja yogas | filtering |
| `test_fts_search_sanskrit_name` | q="gajakesari" | Gaja Kesari match | FTS correctness |
| `test_fts_search_taxonomy` | q="saravali" | rule_id prefix saravali/ matches | cross-field |
| `test_paginated_results` | page 2, per_page 20 | items 21-40 | API contract |

### 8.6 Integration

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_e2e_author_to_activation` | full advisor flow | yoga visible at `/api/v1/yogas/{id}` and active in computes | end-to-end |
| `test_overlap_yoga_same_name_different_source` | two rule_ids under different sources | both distinct; search returns both | cross-source correctness |
| `test_activation_respects_output_shape_validation` | malformed rule_body slipping through | activation blocked at F5 gate | defense-in-depth |

## 9. EPIC-Level Acceptance Criteria

- [ ] At least 1000 yogas with `editorial_status = 'merged'` in `classical_rule`
- [ ] At least 1000 yogas activated (rollout flag ≥ pro-mode 100%)
- [ ] Every yoga has: citation (chapter:verse), classical_names (en + sa_iast + sa_devanagari at minimum), golden charts (≥ 2 positive + ≥ 1 negative), editorial_status = 'merged', review attribution
- [ ] Golden chart suite green at every wave close
- [ ] CI test asserts no yoga ships without citation + fixtures
- [ ] Console workflow supports end-to-end authoring for non-engineers
- [ ] Dual-review enforced; same-user primary + secondary prevented
- [ ] 6 activation waves completed
- [ ] Public catalog page at `/yogas` live with search + filter
- [ ] At least 3 external contributors credited on merged yogas (proves open contribution path works)
- [ ] S4 OLAP marts export per-yoga activation rate and cross-source agreement
- [ ] Astrologer pro-mode workbench surfaces new yogas via search
- [ ] Documentation merged: `docs/markdown/classical/yoga-catalog.md` with authoring guide
- [ ] Marketing post published: "Josi now supports 1000 classical yogas"

## 10. Rollout Plan

- **Feature flag:** No global flag; each yoga has its own activation flag managed by S8. A wave is a tag over many per-yoga flags.
- **Shadow compute:** YES — each yoga goes through S8 shadow at wave activation. Because most long-tail yogas activate on < 1% of charts, statistical signal takes longer; extend shadow window to 7–14 days per wave.
- **Backfill strategy:** newly activated yogas do not auto-recompute historical charts. Activation affects forward computes and lazily re-evaluates when a chart is next read (F13 dependency trigger). Explicit bulk backfill available via admin tool if a wave wants to ensure historical coverage.
- **Rollback plan:** individual yoga rollback via S8 rollback; wave-level rollback deactivates all wave yogas in one admin call; data rows remain in `classical_rule` for audit.

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Editorial throughput falls short of plan | High | Medium | Recruit external contributors earlier; reduce target if needed (500 acceptable floor) |
| Citation errors slip past dual-review | Medium | High | Periodic audit by lead advisor; public catalog invites correction reports |
| DSL insufficient for exotic yoga formulations | Medium | Medium | Escalate to F6 DSL extensions (tracked separately); provisional "manual_rule" escape hatch with engineer review |
| Golden chart generation slow | Medium | Medium | Chart generator helpers (T-R1000.8); shared fixtures across variants |
| Wave auto-halt keeps halting on genuinely rare yogas | Medium | Low | Gate thresholds parameterized per yoga; low-activation yogas use looser `expected_rate_min` |
| Long-tail yogas confuse B2C users | Medium | Medium | Default B2C surface shows only Wave 1-2 (core ~250 + 100); pro mode sees all |
| Translation quality (Tamil, Devanagari) uneven | Medium | Low | Native-speaker editorial review for localized names |
| CLA disputes with external contributors | Low | Medium | Standard open-content CLA; lead advisor vets before acceptance |
| Catalog size stat becomes vanity metric | Low | Low | Coverage reports also show per-yoga activation rate and cross-source agreement so "1000" is not gamed |
| Storage growth from rule rows | Low | Low | 1000 rules × ~8 KB JSONB = 8 MB; trivial |
| Advisor burnout | Medium | High | Rotation, pace guardrails, recognition program; credit on public catalog page |

## 12. References

- Master spec: [`docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`](../../../superpowers/specs/2026-04-19-classical-techniques-expansion-design.md)
- E4a Yoga Engine MVP: [`E4a-yoga-engine-mvp.md`](../P1/E4a-yoga-engine-mvp.md)
- E4b Full 250 Yoga Engine: [`E4b-yoga-engine-full-250.md`](../P2/E4b-yoga-engine-full-250.md)
- F6 rule DSL: [`F6-rule-dsl-yaml-loader.md`](../P0/F6-rule-dsl-yaml-loader.md)
- F16 golden chart suite: [`F16-golden-chart-suite.md`](../P0/F16-golden-chart-suite.md)
- P3-E2-console rule authoring: [`P3-E2-console-rule-authoring-console.md`](../P3/P3-E2-console-rule-authoring-console.md)
- S8 shadow-compute rule migrations: [`S8-shadow-compute-rule-migrations.md`](./S8-shadow-compute-rule-migrations.md)
- I10 10,000-yoga reference set (P6): [`I10-ten-thousand-yoga-reference.md`](../P6/I10-ten-thousand-yoga-reference.md)
- Primary sources:
  - Brihat Parashara Hora Shastra, R. Santhanam trans., Ranjan Publications 1984
  - Saravali, R. Santhanam trans., Ranjan Publications 1983
  - Phaladeepika, G.S. Kapoor trans., Sagar Publications 2005
  - Jataka Parijata, V. Subrahmanya Sastri trans., Ranjan Publications 1993
  - Jataka Bharanam, S.S. Sareen trans., Sagar Publications 2000
- Aksharamukha transliteration — https://aksharamukha.appspot.com/
