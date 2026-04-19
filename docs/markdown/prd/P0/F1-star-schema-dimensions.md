---
prd_id: F1
epic_id: F1
title: "Star-schema dimension tables (source_authority, technique_family, aggregation_strategy, experiment, experiment_arm, output_shape)"
phase: P0-foundation
tags: [#correctness, #extensibility]
priority: must
depends_on: []
enables: [F2, F3, F4, F6, F7, F8, E1a, E2a, E4a, E6a, E14a]
classical_sources: []
estimated_effort: 2 days
status: approved
author: Govind
last_updated: 2026-04-19
---

# F1 — Star-Schema Dimension Tables

## 1. Purpose & Rationale

Every downstream classical technique, every aggregation strategy, every experiment references the same small set of curated vocabularies: *which source authority* (BPHS, Saravali, JH…), *which technique family* (yoga, dasa, tajaka…), *which aggregation strategy* (A/B/C/D), *which experiment*. Without normalization, these appear as free text, drift silently (`"bphs"` vs `"BPHS"` vs `"B.P.H.S."`), and cannot carry metadata (display names, default weights, era, language).

This PRD introduces 6 dimension tables as foreign-key targets for the entire fact hierarchy (F2). It's the single table-family that everything else references.

Seeding is from YAML at deploy time. Rows are stable. Changes are rare and backwards-compatible (additive).

## 2. Scope

### 2.1 In scope
- 6 new tables: `source_authority`, `technique_family`, `aggregation_strategy`, `experiment`, `experiment_arm`, `output_shape`
- YAML seed files at `src/josi/db/seeds/classical/*.yaml`
- Alembic migration generating tables
- Seed loader run on application startup (idempotent)
- Pydantic schemas for each dim
- Strawberry GraphQL types (read-only)

### 2.2 Out of scope
- Fact tables (handled in F2)
- JSON Schema for `output_shape.json_schema` content (handled in F7)
- Experiment lifecycle management UI (P3/P4)

### 2.3 Dependencies
- None. This is the foundation for everything else.

## 3. Technical Research

### 3.1 Why star schema

This is OLAP-style dimension modeling. Dim tables are:
- Small (< 100 rows each)
- Cached entirely in Postgres shared_buffers
- Referenced by FK from the high-volume fact tables

Joins against dim tables are hash broadcasts (near-zero cost). Dim metadata appears once, not per-fact-row. This pattern is battle-tested in data warehousing (Kimball's *The Data Warehouse Toolkit*, Ch. 2–3).

### 3.2 Why text primary keys (not integer surrogates)

We use text PKs (`source_id TEXT = 'bphs'`) rather than integer surrogate keys because:
- Self-documenting in fact rows and logs
- No performance difference for dim tables at this cardinality
- Simpler to reason about when debugging
- Migrations across environments preserve IDs

Storage difference: ~1-2 bytes per fact row × 200M rows = ~300MB — immaterial.

### 3.3 Alternatives considered

| Alternative | Rejected because |
|---|---|
| Postgres ENUMs for all 6 vocabularies | Can't attach metadata (display_name, era, default_weight) |
| Single generic `vocabulary` table with `vocab_type` column | Collapses type safety; cross-table FK targets unclear |
| No normalization (free text) | Silent drift, no metadata attachment |

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| Text vs integer PKs | Text | Self-documenting, zero perf penalty at this cardinality |
| Seed via YAML vs SQL migrations | YAML | Non-engineers can edit; easier to review in PRs |
| Seed on startup vs migration | Startup (idempotent upsert) | Survives env recreation; always reflects current YAML |
| Timestamps on dim tables | `created_at`, `updated_at`, `deprecated_at` | Supports audit + deprecation lifecycle |
| Multi-tenancy | Dim tables are global (no `organization_id`) | Classical vocabularies are shared across tenants |

## 5. Component Design

### 5.1 New modules

```
src/josi/models/classical/
├── __init__.py
├── source_authority.py
├── technique_family.py
├── aggregation_strategy.py
├── experiment.py
├── experiment_arm.py
└── output_shape.py

src/josi/db/seeds/classical/
├── source_authorities.yaml
├── technique_families.yaml
├── aggregation_strategies.yaml
├── output_shapes.yaml
└── experiments.yaml            # initially empty; populated in E14a

src/josi/services/classical/
└── dim_loader.py              # upserts dims from YAML on startup
```

### 5.2 Data model

```sql
CREATE TABLE source_authority (
    source_id           TEXT PRIMARY KEY,
    display_name        TEXT NOT NULL,
    tradition           TEXT NOT NULL CHECK (tradition IN
                          ('parashari','jaimini','tajaka','kp','western','hellenistic',
                           'chinese','mayan','celtic','modern_commentary')),
    era                 TEXT,                          -- "~100 BCE", "modern", ...
    citation_system     TEXT,                          -- "chapter_verse" | "sutra" | "karika"
    default_weight      NUMERIC(3,2) NOT NULL DEFAULT 1.00 CHECK (default_weight BETWEEN 0 AND 1),
    language            TEXT,                          -- "sanskrit" | "tamil" | "english"
    notes               TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    deprecated_at       TIMESTAMPTZ
);

CREATE TABLE technique_family (
    family_id                    TEXT PRIMARY KEY,
    display_name                 TEXT NOT NULL,
    default_output_shape_id      TEXT NOT NULL,          -- FK added after output_shape creation
    default_aggregation_hint     TEXT,                   -- "A"|"B"|"C"|"D" — which tends to work a priori
    parent_category              TEXT CHECK (parent_category IN
                                   ('vedic_classical','western','cross_tradition','chinese','other')),
    created_at                   TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at                   TIMESTAMPTZ NOT NULL DEFAULT now(),
    deprecated_at                TIMESTAMPTZ
);

CREATE TABLE output_shape (
    shape_id       TEXT PRIMARY KEY,
    display_name   TEXT NOT NULL,
    json_schema    JSONB NOT NULL,                       -- validates result payloads
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE technique_family
    ADD CONSTRAINT fk_technique_family_output_shape
    FOREIGN KEY (default_output_shape_id) REFERENCES output_shape(shape_id);

CREATE TABLE aggregation_strategy (
    strategy_id             TEXT PRIMARY KEY,
    display_name            TEXT NOT NULL,
    description             TEXT,
    implementation_version  TEXT NOT NULL,
    is_active               BOOLEAN NOT NULL DEFAULT true,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    deprecated_at           TIMESTAMPTZ
);

CREATE TABLE experiment (
    experiment_id   TEXT PRIMARY KEY,
    hypothesis      TEXT NOT NULL,
    primary_metric  TEXT NOT NULL,              -- 'astrologer_override_rate' | 'user_thumbs' | ...
    started_at      TIMESTAMPTZ,
    ended_at        TIMESTAMPTZ,
    status          TEXT NOT NULL CHECK (status IN ('planned','running','concluded','aborted')),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE experiment_arm (
    experiment_id     TEXT REFERENCES experiment(experiment_id) ON DELETE CASCADE,
    arm_id            TEXT NOT NULL,
    strategy_id       TEXT REFERENCES aggregation_strategy(strategy_id),
    allocation_pct    NUMERIC(5,2) NOT NULL CHECK (allocation_pct BETWEEN 0 AND 100),
    PRIMARY KEY (experiment_id, arm_id)
);
```

### 5.3 Seed YAML format

**`source_authorities.yaml`** (initial seed):

```yaml
- source_id: bphs
  display_name: "Brihat Parashara Hora Shastra"
  tradition: parashari
  era: "~100 BCE (traditional)"
  citation_system: chapter_verse
  default_weight: 1.00
  language: sanskrit
  notes: "Foundational Parashari text; primary authority for most Vedic techniques."

- source_id: saravali
  display_name: "Saravali (by Kalyanavarma)"
  tradition: parashari
  era: "~8th century CE"
  citation_system: chapter_verse
  default_weight: 0.85
  language: sanskrit

- source_id: phaladeepika
  display_name: "Phaladeepika (by Mantreswara)"
  tradition: parashari
  era: "~14th century CE"
  citation_system: chapter_verse
  default_weight: 0.80
  language: sanskrit

- source_id: jataka_parijata
  display_name: "Jataka Parijata (by Vaidyanatha Dikshita)"
  tradition: parashari
  era: "~16th century CE"
  citation_system: chapter_verse
  default_weight: 0.75
  language: sanskrit

- source_id: jaimini_sutras
  display_name: "Jaimini Upadesha Sutras"
  tradition: jaimini
  era: "~300 BCE (traditional)"
  citation_system: sutra
  default_weight: 1.00
  language: sanskrit

- source_id: tajaka_neelakanthi
  display_name: "Tajaka Neelakanthi (by Neelakantha)"
  tradition: tajaka
  era: "~16th century CE"
  citation_system: chapter_verse
  default_weight: 1.00
  language: sanskrit

- source_id: kp_reader
  display_name: "KP Reader Vols 1–6 (by K.S. Krishnamurti)"
  tradition: kp
  era: "~1960s CE"
  citation_system: chapter_verse
  default_weight: 1.00
  language: english

- source_id: jh
  display_name: "Jagannatha Hora 7.x (reference implementation)"
  tradition: parashari
  era: "modern"
  citation_system: software_reference
  default_weight: 0.95
  language: english

- source_id: maitreya
  display_name: "Maitreya9 (reference implementation)"
  tradition: parashari
  era: "modern"
  citation_system: software_reference
  default_weight: 0.85
  language: english
```

**`technique_families.yaml`**:

```yaml
- family_id: yoga
  display_name: "Classical Yogas"
  default_output_shape_id: boolean_with_strength
  default_aggregation_hint: D
  parent_category: vedic_classical

- family_id: dasa
  display_name: "Dasa Systems"
  default_output_shape_id: temporal_hierarchy
  default_aggregation_hint: D
  parent_category: vedic_classical

- family_id: ashtakavarga
  display_name: "Ashtakavarga"
  default_output_shape_id: numeric_matrix
  default_aggregation_hint: D
  parent_category: vedic_classical

- family_id: jaimini
  display_name: "Jaimini System"
  default_output_shape_id: structured_positions
  default_aggregation_hint: D
  parent_category: vedic_classical

- family_id: tajaka
  display_name: "Varshaphala / Tajaka"
  default_output_shape_id: annual_chart_summary
  default_aggregation_hint: D
  parent_category: vedic_classical

- family_id: transit_event
  display_name: "Transit Events (Sade Sati, Dhaiya, major transits)"
  default_output_shape_id: temporal_event
  default_aggregation_hint: D
  parent_category: vedic_classical

- family_id: kp
  display_name: "KP System"
  default_output_shape_id: structured_positions
  default_aggregation_hint: D
  parent_category: vedic_classical

- family_id: prasna
  display_name: "Prasna / Horary"
  default_output_shape_id: structured_positions
  default_aggregation_hint: D
  parent_category: vedic_classical

- family_id: varga_extended
  display_name: "Extended Vargas (D61–D144), Sarvatobhadra, Upagrahas"
  default_output_shape_id: structured_positions
  default_aggregation_hint: D
  parent_category: vedic_classical

- family_id: western_lot
  display_name: "Arabic Parts / Lots"
  default_output_shape_id: structured_positions
  default_aggregation_hint: D
  parent_category: western

- family_id: western_fixed_star
  display_name: "Fixed Stars"
  default_output_shape_id: structured_positions
  default_aggregation_hint: D
  parent_category: western

- family_id: western_harmonic
  display_name: "Harmonic Charts"
  default_output_shape_id: structured_positions
  default_aggregation_hint: D
  parent_category: western

- family_id: western_eclipse
  display_name: "Eclipse Calculations"
  default_output_shape_id: temporal_event
  default_aggregation_hint: D
  parent_category: western

- family_id: western_uranian
  display_name: "Uranian Sensitive Points"
  default_output_shape_id: structured_positions
  default_aggregation_hint: D
  parent_category: western

- family_id: synastry
  display_name: "Synastry (cross-chart)"
  default_output_shape_id: cross_chart_relations
  default_aggregation_hint: D
  parent_category: cross_tradition
```

**`aggregation_strategies.yaml`**:

```yaml
- strategy_id: A_majority
  display_name: "Simple Majority"
  description: "Majority vote for boolean, arithmetic mean for numeric, span-union for temporal."
  implementation_version: "1.0.0"
  is_active: true

- strategy_id: B_confidence
  display_name: "Confidence-Weighted"
  description: "Same shapes as A; every output carries confidence = agreement fraction."
  implementation_version: "1.0.0"
  is_active: true

- strategy_id: C_weighted
  display_name: "Source-Weighted"
  description: "Weighted by astrologer-set or Josi-default source weights."
  implementation_version: "1.0.0"
  is_active: true

- strategy_id: D_hybrid
  display_name: "Hybrid (default)"
  description: "Engine computes per-source (B internals); end-user surfaces see flattened (B); astrologers see C with their weights."
  implementation_version: "1.0.0"
  is_active: true
```

**`output_shapes.yaml`** (shape names only; actual JSON schemas live in F7):

```yaml
- shape_id: boolean_with_strength
  display_name: "Boolean with strength (e.g., yogas)"
  json_schema: {}  # populated in F7

- shape_id: numeric
  display_name: "Single numeric value"
  json_schema: {}

- shape_id: numeric_matrix
  display_name: "Grid of numeric values (e.g., ashtakavarga bindu matrix)"
  json_schema: {}

- shape_id: temporal_range
  display_name: "Time range"
  json_schema: {}

- shape_id: temporal_event
  display_name: "Point-in-time event"
  json_schema: {}

- shape_id: temporal_hierarchy
  display_name: "Nested time periods (dasa/antar/pratyantar)"
  json_schema: {}

- shape_id: structured_positions
  display_name: "Set of named zodiacal positions"
  json_schema: {}

- shape_id: annual_chart_summary
  display_name: "Tajaka / solar-return summary"
  json_schema: {}

- shape_id: cross_chart_relations
  display_name: "Cross-chart relationships (synastry, composite)"
  json_schema: {}

- shape_id: categorical
  display_name: "One-of-many category assignment"
  json_schema: {}
```

### 5.4 Dim loader service

```python
# src/josi/services/classical/dim_loader.py

class DimensionLoader:
    """Idempotently upserts dimension tables from YAML on startup."""

    SEEDS: dict[type[SQLModel], Path] = {
        SourceAuthority: Path("src/josi/db/seeds/classical/source_authorities.yaml"),
        TechniqueFamily: Path("src/josi/db/seeds/classical/technique_families.yaml"),
        OutputShape: Path("src/josi/db/seeds/classical/output_shapes.yaml"),
        AggregationStrategy: Path("src/josi/db/seeds/classical/aggregation_strategies.yaml"),
    }

    async def load_all(self, session: AsyncSession) -> LoadReport:
        """Returns counts of inserted / updated / unchanged rows per table."""
        ...

    async def _upsert(self, session: AsyncSession, model: type[SQLModel],
                     yaml_path: Path) -> UpsertCounts:
        ...
```

Called from FastAPI lifespan event. Failure aborts startup (fail-fast).

## 6. User Stories

### US-F1.1: As an engineer, I want FK constraints to prevent free-text drift
**Acceptance:** attempting to insert a technique_compute row with `source_id = 'BPHS'` (uppercase) fails with FK violation. Only canonical `'bphs'` is accepted.

### US-F1.2: As a classical advisor, I want to edit source metadata via YAML and PR
**Acceptance:** editing `source_authorities.yaml`, opening PR, merging, and redeploying results in updated `source_authority` table rows without migration or SQL.

### US-F1.3: As an analytics user, I want to group compute results by source era
**Acceptance:** running `SELECT sa.era, COUNT(*) FROM technique_compute tc JOIN source_authority sa ON tc.source_id = sa.source_id GROUP BY sa.era` returns correct counts grouped by classical era.

## 7. Tasks

### T-F1.1: Create SQLModel classes for 6 dim tables
- **Definition:** One SQLModel per dim with columns per schema above. Include `TableMeta` for table names. No `TenantBaseModel` inheritance (dims are global).
- **Acceptance:** Classes exist in `src/josi/models/classical/`. `mypy` passes.
- **Effort:** 3 hours
- **Depends on:** nothing

### T-F1.2: Generate Alembic migration
- **Definition:** `docker-compose exec web alembic revision --autogenerate -m "F1: classical dimension tables"`
- **Acceptance:** Migration generated, reviewed, creates all 6 tables + FKs + check constraints + indexes.
- **Effort:** 2 hours
- **Depends on:** T-F1.1

### T-F1.3: Write seed YAML files
- **Definition:** Author the 4 seed YAMLs (source_authorities, technique_families, aggregation_strategies, output_shapes) with the content above.
- **Acceptance:** YAMLs parse cleanly; each row has required fields; cross-references (technique_family → output_shape) are valid.
- **Effort:** 3 hours
- **Depends on:** T-F1.1

### T-F1.4: Build DimensionLoader service
- **Definition:** `DimensionLoader` class with `load_all()` method; idempotent upsert per row.
- **Acceptance:** Unit tests pass; running twice produces no changes the second time; missing row is inserted; changed fields are updated; rows present in DB but absent from YAML are NOT deleted (soft-deprecate with `deprecated_at`).
- **Effort:** 4 hours
- **Depends on:** T-F1.2, T-F1.3

### T-F1.5: Wire to FastAPI lifespan
- **Definition:** On startup, run `DimensionLoader.load_all()`. Fail startup on error.
- **Acceptance:** Fresh DB starts up with dims populated; startup fails cleanly on missing YAML.
- **Effort:** 1 hour
- **Depends on:** T-F1.4

### T-F1.6: Strawberry GraphQL types (read-only)
- **Definition:** Expose 6 dims as read-only GraphQL types under `/graphql`. No mutations in P0.
- **Acceptance:** GraphQL query `{ sourceAuthorities { sourceId displayName tradition } }` returns seeded rows.
- **Effort:** 2 hours
- **Depends on:** T-F1.1

## 8. Unit Tests

### 8.1 SQLModel classes

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_source_authority_model_roundtrip` | `SourceAuthority(source_id='bphs', display_name='BPHS', tradition='parashari', default_weight=1.0)` | insert + select returns equal obj | basic ORM sanity |
| `test_tradition_constraint_enforces_enum` | `tradition='madeup'` | `IntegrityError` on insert | CHECK constraint active |
| `test_default_weight_range_constraint` | `default_weight=1.5` | `IntegrityError` on insert | CHECK 0..1 active |

### 8.2 DimensionLoader

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_loader_inserts_on_empty_db` | empty DB + full YAMLs | all seed rows present | idempotency base case |
| `test_loader_second_run_is_noop` | already-populated DB + same YAMLs | 0 inserts, 0 updates | idempotency |
| `test_loader_updates_changed_fields` | YAML row with new `default_weight` | row UPDATE with new value | config evolves via YAML |
| `test_loader_does_not_delete_missing_rows` | DB has `source_id='bphs'`, YAML missing it | row stays, `deprecated_at` set | safety: no data loss |
| `test_loader_fk_validation_fails_fast` | technique_family references unknown output_shape | raises `IntegrityError` | catch seed bugs |

### 8.3 GraphQL read

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_source_authorities_query` | `{ sourceAuthorities { sourceId } }` | list of seeded source_ids | GraphQL surface works |
| `test_deprecated_sources_filtered` | deprecated row + live row | only live returned by default | UX default |

## 9. EPIC-Level Acceptance Criteria

- [ ] All 6 tables exist in DB after `alembic upgrade head`
- [ ] Seeding runs on startup idempotently
- [ ] Attempting to insert a `technique_compute` row with invalid `source_id` fails at DB level (FK constraint)
- [ ] Seed YAMLs are reviewable in git PRs by non-engineers
- [ ] GraphQL read queries return seeded data
- [ ] Unit test coverage ≥ 95% for loader + models
- [ ] Docs: `CLAUDE.md` updated with "classical dimensions are seeded from YAML; to add a source, edit `src/josi/db/seeds/classical/source_authorities.yaml` and open a PR"

## 10. Rollout Plan

- **Feature flag:** none — P0 foundation, unconditionally required.
- **Shadow compute:** N/A.
- **Backfill:** N/A (empty on first deploy).
- **Rollback:** `alembic downgrade -1` drops tables. Safe because no data depends on dims at P0 start.

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Typo in seed YAML breaks startup | Medium | High (blocks deploy) | CI test that loads seeds into test DB before merge |
| FK target missing on fact table migration | Low | High | Run dim seed before fact migration in Alembic ordering |
| Dim table bloat over time | Low | Low | Monitor row count; alert at >1000 rows per dim |
| YAML files become unwieldy | Low | Medium | If rows > 50, shard into multiple YAMLs in same dir |

## 12. References

- Master spec: [`docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`](../../../superpowers/specs/2026-04-19-classical-techniques-expansion-design.md)
- Related PRDs: F2 (fact tables FK into these), F4 (rule versioning uses source_id), F7 (output_shape.json_schema populated here)
- Kimball, *The Data Warehouse Toolkit*, Ch. 2–3 (star schema rationale)
