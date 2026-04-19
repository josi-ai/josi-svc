---
title: Classical Techniques Expansion — Master Design
date: 2026-04-19
status: approved
owner: Govind
phase_coverage: P0 through P6
related_prds: docs/markdown/prd/
---

# Classical Techniques Expansion — Master Design

## 0. Summary

This spec establishes the architecture, phasing, and governance for expanding Josi's astrology calculation engine from its current state (Vedic basics + Western basics + BaZi) to the most comprehensive multi-tradition classical astrology platform in existence.

**Scope:** 76 planned PRDs across 7 phases. Detailed PRDs for P0–P4 (commitments, including gap-closing PRDs E5b, E8b, E17 for full Maitreya parity); strategic PRDs for P5–P6 (vision).

**Timeline:** P0 in 2 weeks. First shippable increment (P1) in 3 months. Full classical breadth (P2) in 6 months. Scale to 10M users (P3) in 12 months. Scale to 100M (P4) in 18–24 months. P5–P6 thereafter.

**North star:** the only astrology platform where classical source authority is an explicit, configurable, and statistically-measured axis. Astrologers choose their lineage; end-users get AI-synthesized readings citing specific verses with confidence scores; an experimentation framework makes classical-technique accuracy empirically measurable for the first time.

---

## 1. Decisions locked in (from brainstorming session, 2026-04-19)

These are the six decisions that anchor all downstream PRDs. They do NOT get re-litigated in individual PRDs.

### 1.1 Sequencing (Decision 1)
**All calculation engines first → then UIs → then decide on follow-on strategy.**
Rationale: engines are the differentiator; UIs can follow rapidly once engines are correct. Keeps scope disciplined.

### 1.2 Source authority policy (Decision 2)
**Hybrid per-technique + astrologer-configurable + Ultra AI ensemble.**
- End-user AI chat (Auto mode): Josi picks one source per technique, invisible to user.
- Astrologer Pro mode: astrologer selects source per technique-family; saved as profile.
- Ultra AI mode: all configured sources computed, aggregated via experimental strategies, confidence surfaced.

### 1.3 Aggregation strategies (Decision 3)
**Build all 4 strategies; let statistics decide which wins per context.**
- **Strategy A — Simple majority:** boolean majority vote, arithmetic mean for numeric, span-union for temporal.
- **Strategy B — Confidence-weighted:** same shapes as A, but every output carries a confidence score = agreement fraction.
- **Strategy C — Source-weighted:** weighted by source-authority rank (astrologer-set weights or Josi defaults).
- **Strategy D — Hybrid (default):** engine always computes per-source + confidence (B internals); end-user surfaces see flattened best-guess (B output); astrologers see C with their weights.

### 1.4 Measurement signals (Decision 4)
**All three signals collected, weighted by decision context.**
- **Primary (fast):** astrologer override rate (both implicit and explicit). Dominant for astrologer-facing readings.
- **Primary (scale):** end-user thumbs up/down on AI chat responses. Dominant for B2C chat.
- **Gold-standard (slow):** predicted-vs-actual event correlation. Instrumented from day 1, decisive after 6+ months of data.

### 1.5 Yoga coverage depth (Decision 5)
**Comprehensive core (~250 yogas) shipped via P1 MVP (60) + P2 breadth (190 more); 1000-yoga reference set via additive rule registry in P4+.**

### 1.6 Override tracking (Decision 6)
**Implicit + explicit both.**
- Implicit: if astrologer uses the auto-computed value in their rendered reading, tracked as "accepted."
- Explicit: thumbs up/down button per computed element, tracked as "affirmed/rejected."

---

## 2. Architecture

### 2.1 Core principle: separate compute from aggregation

Every classical technique is split into two layers. The lower layer is expensive and runs once per (chart, source). The upper layer is cheap and runs N times per chart (once per aggregation strategy).

```
┌────────────────────────────────────────────────────────────────────┐
│  Technique Invocation: compute_technique(chart_id, family)         │
├────────────────────────────────────────────────────────────────────┤
│  Layer 4 — Serving mart (chart_reading_view, flat table)           │
│     ↑ incrementally updated by worker on aggregation_event insert  │
├────────────────────────────────────────────────────────────────────┤
│  Layer 3 — Aggregation strategies (pure functions on per-source)   │
│     Strategy A, B, C, D → aggregation_event (append-only log)      │
├────────────────────────────────────────────────────────────────────┤
│  Layer 2 — Per-source compute (idempotent by construction)         │
│     RuleEngine(chart, source, rule_version) → technique_compute    │
├────────────────────────────────────────────────────────────────────┤
│  Layer 1 — Immutable rule registry (content-addressable)           │
│     YAML files → classical_rule table at deploy time               │
└────────────────────────────────────────────────────────────────────┘
```

### 2.2 Data model (star schema)

**Dimension tables (normalized, seeded from YAML at deploy, ~100 rows total):**

```sql
source_authority(source_id PK, display_name, tradition, era, citation_system,
                 default_weight, language, notes)

technique_family(family_id PK, display_name, default_output_shape,
                 default_aggregation_hint, parent_category)

aggregation_strategy(strategy_id PK, display_name, description,
                     implementation_version, is_active, created_at, deprecated_at)

experiment(experiment_id PK, hypothesis, primary_metric,
           started_at, ended_at, status)

experiment_arm(experiment_id, arm_id, strategy_id, allocation_pct,
               PK(experiment_id, arm_id))

output_shape(shape_id PK, json_schema)
```

**Fact tables (composite FKs, JSONB for polymorphic content):**

```sql
classical_rule(
  rule_id, source_id FK, version, content_hash,
  technique_family_id FK, output_shape_id FK,
  rule_body JSONB, citation, classical_names JSONB,
  effective_from, effective_to,
  PK(rule_id, source_id, version)
)

technique_compute(
  chart_id FK, rule_id, source_id FK, rule_version,
  result JSONB, computed_at,
  PK(chart_id, rule_id, source_id, rule_version),
  FK(rule_id, source_id, rule_version) → classical_rule
)
-- Partitioned LIST BY technique_family_id, HASH sub-partition on chart_id

aggregation_event(
  id PK, chart_id FK, technique_family_id FK,
  strategy_id FK, experiment_id FK, experiment_arm_id,
  inputs_hash, output JSONB, surface, user_mode, computed_at
)

aggregation_signal(
  id PK, aggregation_event_id FK, signal_type, signal_value JSONB,
  recorded_by_user_id FK, recorded_at
)

astrologer_source_preference(
  user_id FK, technique_family_id FK,
  source_weights JSONB, preferred_strategy_id FK,
  PK(user_id, technique_family_id)
)
```

**Serving mart (denormalized on purpose, regular table updated by worker):**

```sql
chart_reading_view(
  chart_id PK,
  active_yogas JSONB,        -- from strategy D aggregation
  current_dasas JSONB,       -- active MD/AD/PD across all dasa systems
  transit_highlights JSONB,  -- Sade Sati, major transits
  tajaka_summary JSONB,      -- current year's Varshaphala
  jaimini_summary JSONB,     -- Chara karakas, Arudhas, Jaimini dasa context
  ashtakavarga_summary JSONB,
  astrologer_preference_key, -- which preference profile was applied
  last_computed_at
)
```

### 2.3 Multi-tenancy

Every fact table carries `organization_id` (inherited from `TenantBaseModel`). All queries filter on it. Sharding-readiness follows naturally.

### 2.4 Versioning everything

- **Rules** versioned with `effective_from`/`effective_to`. Old compute rows retain old version forever.
- **Strategies** versioned via `implementation_version`; events carry version at compute time.
- **Dimension vocabularies** versioned; deprecations are additive (`deprecated_at` flag).
- **Rule changes roll out via shadow → 10% → 50% → 100%** (P3 feature).

### 2.5 Content-hash provenance

Every `technique_compute` row stores `input_fingerprint` (hash of chart data + rule version + content hash) and `output_hash`. Enables:
- Full audit trail for any user-visible result
- Deterministic recompute triggers when any input changes
- Tamper detection

---

## 3. AI chat integration

### 3.1 Tool-use contract

Chat backend gains typed tool-use:

```python
@tool
def get_yoga_summary(chart_id: str, strategy: StrategyId = "D_hybrid",
                    min_confidence: float = 0.0) -> YogaSummary: ...

@tool
def get_current_dasa(chart_id: str, system: DasaSystem = "vimshottari",
                    level: int = 2) -> DasaPeriod: ...

@tool
def get_transit_events(chart_id: str, date_range: DateRange,
                      importance: TransitImportance = "major") -> list[TransitEvent]: ...

@tool
def get_tajaka_summary(chart_id: str, year: int) -> TajakaSummary: ...

@tool
def find_similar_charts(chart_id: str, technique_family: str,
                       limit: int = 10) -> list[SimilarChart]: ...
```

Tool responses are Pydantic models with stable shapes across rule versions.

### 3.2 Response shape always carries citations and confidence

Every fact the LLM sees includes:
- `source`: e.g., `"bphs"` or `"consensus"` (if from aggregation)
- `citation`: e.g., `"BPHS Ch.36 v.14-16"`
- `confidence`: 0.0–1.0 (from strategy B/C/D aggregation)
- `cross_source_agreement`: optional, "4/5 sources agree"

This drives natural epistemic tone: "strongly active" vs "some traditions see this."

### 3.3 Prompt caching

Chart-specific context (active yogas, current dasas, transit state) cached via Claude `cache_control` per session. First AI call: full context. Subsequent calls within 5 min: cache hit, 5× cheaper.

### 3.4 Ultra AI mode (P2+)

Premium users can enable "debate mode": LLM consults all 4 strategies separately, presents disagreement as internal debate, synthesizes.

---

## 4. Phasing

| Phase | Timeline | User scale | Theme | PRD count |
|---|---|---|---|---|
| **P0 Foundation** | Week 1–2 | pre-launch | Architectural primitives | 17 |
| **P1 MVP Engines** | Month 1–3 | 0 → 10k | Shippable engine increments | 7 |
| **P2 Breadth & UIs** | Month 3–6 | 10k → 100k | Full classical coverage + dedicated UIs + Maitreya-parity gap-closing | 14 |
| **P3 Scale to 10M** | Month 6–12 | 100k → 10M | Ops hardening | 9 |
| **P4 Scale to 100M** | Year 1–2 | 10M → 100M | Hyperscale, multi-tenant overrides | 6 |
| **P5 Category Dominance** | Year 2–3 | 100M+ | Multi-modal, network effects | 12 |
| **P6 Category Creation** | Year 3–5 | established | Institution, research, open-source | 11 |
| **Total** | — | — | — | **76** |

Phase-by-phase EPIC inventory is canonical in `docs/markdown/prd/INDEX.md`.

---

## 5. PRD organization

### 5.1 Directory layout

```
docs/markdown/prd/
├── INDEX.md                       # master index with all 73 PRDs, filterable by tag
├── _TEMPLATE.md                    # canonical PRD format
├── P0/                             # 17 foundation PRDs
│   ├── F1-star-schema-dimensions.md
│   ├── F2-fact-tables.md
│   ├── ...
├── P1/                             # 7 MVP PRDs
│   ├── E1a-multi-dasa-v1.md
│   ├── E2a-ashtakavarga-v2.md
│   ├── ...
├── P2/                             # 11 breadth PRDs
├── P3/                             # 9 scale-10M PRDs
├── P4/                             # 6 scale-100M PRDs
├── P5/                             # 12 dominance PRDs
└── P6/                             # 11 institution PRDs
```

### 5.2 Tagging scheme (enforced in YAML frontmatter)

Every PRD must declare:

```yaml
---
prd_id: E4a
epic_id: E4
title: "Classical Yoga Engine MVP (60 yogas)"
phase: P1-mvp
tags: [#correctness, #extensibility, #experimentation]
priority: must
depends_on: [F1, F2, F4, F6, F7, F8, F13, F17]
enables: [E4b, E11a, E14a]
classical_sources: [bphs, saravali, phaladeepika]
estimated_effort: 3-4 weeks
status: approved | in_progress | completed
---
```

### 5.3 PRD content structure

Every PRD contains:
1. Purpose & rationale
2. Scope (in/out)
3. Classical/technical research (rules with citations, or architecture with alternatives)
4. Open questions (all resolved in this spec; any reopened at implementation time flagged back to brainstorming)
5. Component design (services, data model delta, API contract)
6. User stories
7. Tasks (work breakdown with per-task acceptance criteria)
8. Unit tests (per module, per rule for classical engines)
9. EPIC-level acceptance criteria
10. Rollout plan
11. Risks & mitigations

---

## 6. Governance

### 6.1 PRD lifecycle
- **Draft** → author writes, submits PR
- **Under review** → classical-content reviewers (for yoga/dasa/jaimini/tajaka PRDs) + engineering reviewers
- **Approved** → merged, linked in INDEX, ready for implementation
- **In progress** → engineering execution
- **Completed** → all acceptance criteria passed, golden chart suite green, merged to main

### 6.2 Changes to master spec
This document is the anchor. Changes require brainstorming-skill cycle (new session) not inline edits. Individual PRD scope changes are allowed.

### 6.3 Rule authoring
- P0–P1: engineers author YAML rules
- P2: engineers + classical advisors author, engineers review structure
- P3: rule authoring console (E2-console) allows non-engineer classical authors

### 6.4 Golden chart suite ownership
Maintained in `tests/golden/charts/*.yaml`. Each chart has:
- Birth data
- Expected active yogas (per source)
- Expected dasa periods
- Classical-verse references justifying expected outputs

Additions require dual review (engineer + classical advisor).

---

## 7. Non-goals (explicitly out of scope)

- **Commercial astrology predictions for legal/medical/financial advice** — Josi provides classical calculations and interpretations as entertainment/spiritual-guidance only. All UI surfaces carry disclaimers.
- **Real-time horoscope auto-generation** — we compute on chart state; we do not generate "today's horoscope for all Aries" bulk content in P1–P4.
- **Astrology school accreditation** — until P6, Josi does not issue certifications.
- **Proprietary vs. classical interpretation mixing** — we never blend Josi-originated rules with classical rules in the same TechniqueResult; if we ever originate rules, they get their own `source_id = "josi_original"`.
- **Closed-source classical rules** — the rule registry YAML is considered open content; if we publish, it publishes. Commercial moat is the AI layer + data, not the rule definitions.

---

## 8. Success metrics (spec-level)

### 8.1 Engine correctness
- Golden chart suite green rate ≥ 99.5% per deploy
- Cross-source agreement measured and tracked per rule
- Differential testing against JH/Maitreya: disagreement rate < 1% per technique after P2

### 8.2 Product velocity
- From P0 complete: average 2 weeks from "new classical rule defined" → "shipped in production with tests"
- Astrologer onboarding to pro-mode configuration: < 10 minutes

### 8.3 Scale
- AI tool-use read latency P50 < 20 ms, P99 < 200 ms at 10M users
- Engine backfill for a new classical source (across all existing charts) completes in < 24 hours at 10M charts

### 8.4 AI quality
- End-user thumbs-up rate on AI chat responses ≥ 75%
- Astrologer override rate on computed elements ≤ 15% at steady state

---

## 9. Open questions (to resolve in writing-plans or later brainstorming)

These are intentionally deferred to implementation planning:

1. **Celery vs procrastinate vs Temporal for P1 workflows** — decide at P1 start based on ops preference.
2. **pg_jsonschema vs app-level JSON Schema validation** — decide at P0 based on extension availability in Cloud SQL.
3. **Qdrant embedding dimensionality and model** — decide at E11a start based on Claude embedding capabilities.
4. **Specific classical scholar/advisor partnerships** — operational, not technical.
5. **Pricing for Ultra AI mode** — product/business decision, not in this spec.

---

## 10. References

- `docs/markdown/PRODUCT_VISION.md` — product-level context
- `CLAUDE.md` — codebase conventions
- `docs/markdown/prd/INDEX.md` — full PRD index
- `docs/markdown/prd/_TEMPLATE.md` — PRD format
- Classical texts (primary sources): BPHS, Saravali, Phaladeepika, Jataka Parijata, Jaimini Sutras, Tajaka Neelakanthi, KP Reader Vols 1–6
- Reference implementations: Jagannatha Hora 7.x, Maitreya9
