---
prd_id: F2
epic_id: F2
title: "Fact tables with composite FKs (classical_rule, technique_compute, aggregation_event, aggregation_signal, astrologer_source_preference)"
phase: P0-foundation
tags: [#correctness]
priority: must
depends_on: [F1]
enables: [F3, F5, F9, F13, all engine EPICs]
classical_sources: []
estimated_effort: 3 days
status: approved
author: Govind
last_updated: 2026-04-19
---

# F2 — Fact Tables with Composite FKs

## 1. Purpose & Rationale

F1 establishes dimensions. F2 establishes the fact tables that *use* those dimensions: the immutable rule registry, the per-source compute results, the aggregation event log, the signal log, and astrologer source preferences.

Design invariants:
- **Idempotency by primary-key construction.** Given the same `(chart_id, rule_id, source_id, rule_version)`, at most one result exists. Duplicate computes become `ON CONFLICT DO NOTHING`.
- **Referential integrity via composite FKs.** `technique_compute` FKs to `classical_rule(rule_id, source_id, version)` so results cannot orphan from their rule.
- **Append-only aggregation log.** Every aggregation is a new row; updates are not allowed. Supports experiment replay, audit, and strategy rollout.
- **Multi-tenancy via `organization_id`.** Every fact row is tenant-isolated.

## 2. Scope

### 2.1 In scope
- 5 new tables:
  - `classical_rule` — immutable rule registry
  - `technique_compute` — per-source raw results
  - `aggregation_event` — append-only aggregation log
  - `aggregation_signal` — feedback collection
  - `astrologer_source_preference` — per-astrologer config
- Composite foreign keys where needed
- Indexes tuned for known read paths
- Pydantic schemas for result and signal payloads
- Alembic migration

### 2.2 Out of scope
- Partitioning scheme (F3 — applied to `technique_compute` and `aggregation_event`)
- JSON Schema content for `result`, `rule_body`, `output` (F5, F6, F7)
- `chart_reading_view` table (F9)
- Rule loader from YAML (F6)

### 2.3 Dependencies
- F1 (dimension tables are FK targets)
- `TenantBaseModel` (existing in codebase)
- `AstrologyChart` model (existing; PK `chart_id`)

## 3. Technical Research

### 3.1 Why composite FK on technique_compute

We could use a surrogate UUID PK and trust app code to keep `rule_id`, `source_id`, `rule_version` consistent. We don't, because:

- Silent drift is a real failure mode at scale
- Postgres's FK check is microseconds against a cached dim
- Makes the invariant "this result comes from this exact rule" enforceable

The primary key `(chart_id, rule_id, source_id, rule_version)` serves triple duty: identity, uniqueness, and composite FK target.

### 3.2 Why aggregation_event is append-only

Strategies will evolve (new implementation_version). We don't want to overwrite the output of strategy B v1.0.0 when B v1.1.0 ships — that breaks experiments mid-flight. Append-only lets us compare versions over time.

### 3.3 Index strategy

Known read paths:
- AI tool-use: `chart_reading_view` by `chart_id` (F9)
- Audit: `technique_compute` by `(chart_id, technique_family)` → requires join via `classical_rule` OR denormalized `technique_family_id` in compute
- Analytics: `aggregation_event` by `(experiment_id, experiment_arm_id, technique_family_id)`

Decision: **denormalize `technique_family_id` into `technique_compute`** as a FK column to enable fast family-scoped reads without join. Same for `aggregation_event`. This is tolerable duplication (1 text col, indexed).

### 3.4 Alternatives considered

| Alternative | Rejected because |
|---|---|
| Single `fact` table with polymorphic discriminator | Collapses type safety; JSONB-everywhere; no compile-time per-shape checks |
| Separate tables per output_shape (technique_compute_boolean, _numeric, _temporal) | Ugly joins for "all results for chart X"; 5× migration cost |
| Overwrite-on-change for aggregations | Loses strategy version history; breaks experiment replay |
| Ignore multi-tenancy at F2, add later | Retrofit requires rewriting every query; cheap to add now |

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| Surrogate vs composite PK on technique_compute | Composite | Enforces idempotency and referential integrity |
| Denormalize technique_family_id | Yes | Enables fast family-scoped reads without join |
| Mutable vs append-only aggregation | Append-only | Experiment replay + audit |
| Include organization_id | Yes on all fact tables | Multi-tenancy + sharding readiness |
| JSON Schema validation location | Insert-time via F5 | Fail fast; pg_jsonschema |
| Include `computed_at` | Yes, `TIMESTAMPTZ NOT NULL DEFAULT now()` | Audit + cache freshness |

## 5. Component Design

### 5.1 New modules

```
src/josi/models/classical/
├── classical_rule.py
├── technique_compute.py
├── aggregation_event.py
├── aggregation_signal.py
└── astrologer_source_preference.py

src/josi/schemas/classical/
├── result_payloads.py          # Pydantic for result JSONB
├── aggregation_outputs.py      # Pydantic for aggregation output JSONB
└── signal_payloads.py          # Pydantic for signal value JSONB
```

### 5.2 Data model

```sql
-- ============================================================
-- classical_rule: immutable rule registry, loaded from YAML (F6)
-- ============================================================
CREATE TABLE classical_rule (
    rule_id                  TEXT NOT NULL,
    source_id                TEXT NOT NULL REFERENCES source_authority(source_id),
    version                  TEXT NOT NULL,                         -- semver
    content_hash             CHAR(64) NOT NULL,                     -- sha256 of canonical JSON
    technique_family_id      TEXT NOT NULL REFERENCES technique_family(family_id),
    output_shape_id          TEXT NOT NULL REFERENCES output_shape(shape_id),
    rule_body                JSONB NOT NULL,                        -- DSL payload (F6)
    citation                 TEXT,                                  -- "BPHS 36.14-16"
    classical_names          JSONB NOT NULL DEFAULT '{}'::jsonb,    -- {en, sa_iast, sa_devanagari, ta}
    effective_from           TIMESTAMPTZ NOT NULL DEFAULT now(),
    effective_to             TIMESTAMPTZ,                           -- null = active
    created_at               TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (rule_id, source_id, version)
);

CREATE INDEX idx_classical_rule_family ON classical_rule(technique_family_id);
CREATE INDEX idx_classical_rule_effective
    ON classical_rule(rule_id, source_id)
    WHERE effective_to IS NULL;

-- ============================================================
-- technique_compute: per-source raw compute results
-- ============================================================
CREATE TABLE technique_compute (
    organization_id          UUID NOT NULL REFERENCES organization(organization_id),
    chart_id                 UUID NOT NULL REFERENCES astrology_chart(chart_id),
    rule_id                  TEXT NOT NULL,
    source_id                TEXT NOT NULL REFERENCES source_authority(source_id),
    rule_version             TEXT NOT NULL,
    technique_family_id      TEXT NOT NULL REFERENCES technique_family(family_id),  -- denormalized
    output_shape_id          TEXT NOT NULL REFERENCES output_shape(shape_id),       -- denormalized
    result                   JSONB NOT NULL,
    input_fingerprint        CHAR(64) NOT NULL,     -- F13: hash of (chart inputs, rule content)
    output_hash              CHAR(64) NOT NULL,     -- F13: hash of result
    computed_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (chart_id, rule_id, source_id, rule_version),
    FOREIGN KEY (rule_id, source_id, rule_version)
        REFERENCES classical_rule(rule_id, source_id, version)
);

CREATE INDEX idx_compute_family
    ON technique_compute(chart_id, technique_family_id);

CREATE INDEX idx_compute_org_family
    ON technique_compute(organization_id, technique_family_id, computed_at DESC);

-- Partitioned in F3; created here as PARTITION BY LIST (technique_family_id)
-- with default partition for initial simplicity, per-family partitions added in F3.

-- ============================================================
-- aggregation_event: append-only log of aggregated outputs
-- ============================================================
CREATE TABLE aggregation_event (
    id                       UUID NOT NULL DEFAULT gen_random_uuid(),
    organization_id          UUID NOT NULL REFERENCES organization(organization_id),
    chart_id                 UUID NOT NULL REFERENCES astrology_chart(chart_id),
    technique_family_id      TEXT NOT NULL REFERENCES technique_family(family_id),
    technique_id             TEXT NOT NULL,           -- e.g., 'yoga.raja.gaja_kesari'; nullable for family-level
    strategy_id              TEXT NOT NULL REFERENCES aggregation_strategy(strategy_id),
    strategy_version         TEXT NOT NULL,           -- snapshotted from aggregation_strategy at compute time
    experiment_id            TEXT REFERENCES experiment(experiment_id),
    experiment_arm_id        TEXT,
    inputs_hash              CHAR(64) NOT NULL,       -- hash of (rule_id, rule_version, source_id) tuples consumed
    output                   JSONB NOT NULL,
    surface                  TEXT CHECK (surface IN ('b2c_chat','astrologer_pro','ultra_ai','internal_experiment','api')),
    user_mode                TEXT CHECK (user_mode IN ('auto','custom','ultra')),
    computed_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (id),
    FOREIGN KEY (experiment_id, experiment_arm_id)
        REFERENCES experiment_arm(experiment_id, arm_id)
);

CREATE INDEX idx_aggregation_chart
    ON aggregation_event(chart_id, technique_family_id, strategy_id, computed_at DESC);

CREATE INDEX idx_aggregation_experiment
    ON aggregation_event(experiment_id, experiment_arm_id, computed_at DESC)
    WHERE experiment_id IS NOT NULL;

CREATE INDEX idx_aggregation_org_recent
    ON aggregation_event(organization_id, computed_at DESC);

-- Partitioned in F3 by computed_at monthly.

-- ============================================================
-- aggregation_signal: feedback (astrologer override, user thumbs, outcomes)
-- ============================================================
CREATE TABLE aggregation_signal (
    id                        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id           UUID NOT NULL REFERENCES organization(organization_id),
    aggregation_event_id      UUID NOT NULL REFERENCES aggregation_event(id),
    signal_type               TEXT NOT NULL CHECK (signal_type IN
                                ('astrologer_override_implicit','astrologer_override_explicit',
                                 'user_thumbs_up','user_thumbs_down',
                                 'outcome_positive','outcome_negative','outcome_neutral')),
    signal_value              JSONB NOT NULL DEFAULT '{}'::jsonb,   -- structured per signal_type
    recorded_by_user_id       UUID REFERENCES "user"(user_id),
    recorded_at               TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_signal_event
    ON aggregation_signal(aggregation_event_id, signal_type);

CREATE INDEX idx_signal_org_recent
    ON aggregation_signal(organization_id, recorded_at DESC);

-- ============================================================
-- astrologer_source_preference: per-astrologer config
-- ============================================================
CREATE TABLE astrologer_source_preference (
    organization_id              UUID NOT NULL REFERENCES organization(organization_id),
    user_id                      UUID NOT NULL REFERENCES "user"(user_id),
    technique_family_id          TEXT NOT NULL REFERENCES technique_family(family_id),
    source_weights               JSONB NOT NULL DEFAULT '{}'::jsonb,
                                 -- keys must be valid source_ids; trigger validates
    preferred_strategy_id        TEXT REFERENCES aggregation_strategy(strategy_id),
    preference_mode              TEXT NOT NULL DEFAULT 'auto'
                                 CHECK (preference_mode IN ('auto','custom','ultra')),
    created_at                   TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at                   TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (user_id, technique_family_id)
);

-- Trigger: validate source_weights keys against source_authority
CREATE OR REPLACE FUNCTION validate_source_weights_keys()
RETURNS trigger AS $$
DECLARE
    invalid_key TEXT;
BEGIN
    SELECT jsonb_object_keys(NEW.source_weights) INTO invalid_key
    WHERE jsonb_object_keys(NEW.source_weights)
      NOT IN (SELECT source_id FROM source_authority WHERE deprecated_at IS NULL)
    LIMIT 1;
    IF invalid_key IS NOT NULL THEN
        RAISE EXCEPTION 'Invalid source_id in source_weights: %', invalid_key;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_validate_source_weights
    BEFORE INSERT OR UPDATE ON astrologer_source_preference
    FOR EACH ROW EXECUTE FUNCTION validate_source_weights_keys();
```

### 5.3 Pydantic result payload schemas

```python
# src/josi/schemas/classical/result_payloads.py

from typing import Literal
from pydantic import BaseModel, Field, confloat

class BooleanWithStrengthResult(BaseModel):
    """Result shape for yoga activation, etc."""
    active: bool
    strength: confloat(ge=0, le=1) = 0.0
    details: dict = Field(default_factory=dict)
    reason: str | None = None  # why active or inactive

class NumericResult(BaseModel):
    value: float
    unit: str | None = None
    details: dict = Field(default_factory=dict)

class NumericMatrixResult(BaseModel):
    """e.g., ashtakavarga bindu matrix: 12 signs × 8 contributors."""
    matrix: list[list[int]]
    row_labels: list[str]
    col_labels: list[str]

class TemporalRangeResult(BaseModel):
    start: datetime
    end: datetime
    lord: str | None = None           # e.g., 'jupiter' for dasa periods
    level: int | None = None          # 1=mahadasa, 2=antardasa, 3=pratyantardasa

class TemporalHierarchyResult(BaseModel):
    periods: list[TemporalRangeResult]
    root_system: str                  # e.g., 'vimshottari', 'yogini'

# ... (other shapes: structured_positions, annual_chart_summary, etc.)
```

### 5.4 Internal service interface (scaffolded; implemented by per-technique engines)

```python
# src/josi/services/classical/base_engine.py

class ClassicalEngine(Protocol):
    """Contract implemented by every per-family engine (yoga, dasa, etc.)."""

    technique_family_id: str

    async def compute_for_source(
        self,
        session: AsyncSession,
        chart_id: UUID,
        source_id: str,
        rule_ids: list[str] | None = None,  # None = all rules from source
    ) -> list[TechniqueComputeRow]: ...

    async def load_cached(
        self,
        session: AsyncSession,
        chart_id: UUID,
        source_id: str | None = None,
    ) -> list[TechniqueComputeRow]: ...
```

Engines write rows via `ON CONFLICT DO NOTHING` to preserve idempotency.

## 6. User Stories

### US-F2.1: As an engineer, I want to insert a technique_compute row and have the PK prevent duplicates
**Acceptance:** running the same compute twice leaves exactly one row; no exception on second insert when using `ON CONFLICT DO NOTHING`.

### US-F2.2: As an engineer, I want FK constraints to prevent orphaned compute results
**Acceptance:** inserting a technique_compute row whose `(rule_id, source_id, rule_version)` is not in `classical_rule` raises `IntegrityError`.

### US-F2.3: As an analytics user, I want to query "all aggregation events for experiment X arm Y" without a full-table scan
**Acceptance:** query uses `idx_aggregation_experiment` (visible in `EXPLAIN`); response P99 < 100ms at 10M rows.

### US-F2.4: As an astrologer, my `source_weights` JSONB is validated to contain only valid source_ids
**Acceptance:** attempting to set `source_weights = {"made_up": 1.0}` raises trigger exception.

## 7. Tasks

### T-F2.1: SQLModel classes
- **Definition:** One SQLModel per fact table with exact columns above. Composite PKs specified. FKs declared. Inherit appropriately from `TenantBaseModel` (picks up `organization_id`, timestamps, soft-delete) except `classical_rule` which is global.
- **Acceptance:** Classes compile; mypy passes; FK relationships are declared and queryable via ORM.
- **Effort:** 4 hours
- **Depends on:** F1 complete

### T-F2.2: Alembic migration
- **Definition:** Autogenerate migration; manually add check constraints, composite FK, trigger, indexes.
- **Acceptance:** Migration applies on fresh DB and produces exact schema above; `alembic downgrade -1` cleanly reverts.
- **Effort:** 4 hours
- **Depends on:** T-F2.1

### T-F2.3: Pydantic result payload schemas
- **Definition:** Schemas for all 10 output_shapes in `schemas/classical/result_payloads.py`.
- **Acceptance:** Every shape has a `BaseModel`; JSON Schema can be derived via `.model_json_schema()`.
- **Effort:** 4 hours
- **Depends on:** F1 output_shapes seeded

### T-F2.4: ClassicalEngine Protocol scaffold
- **Definition:** Protocol declared; base helpers for loading/saving rows with idempotent upsert.
- **Acceptance:** A test subclass can implement `compute_for_source` and round-trip successfully.
- **Effort:** 3 hours
- **Depends on:** T-F2.1, T-F2.2

### T-F2.5: Integration test: full path insert + query
- **Definition:** Test that creates a rule, inserts compute row, inserts aggregation event, inserts signal, and queries each.
- **Acceptance:** All inserts succeed; all reads return expected shapes.
- **Effort:** 3 hours
- **Depends on:** T-F2.2, T-F2.3

### T-F2.6: source_weights trigger validation test
- **Definition:** Attempt inserts with valid and invalid `source_weights` and assert behavior.
- **Acceptance:** Valid accepted; invalid raises `IntegrityError` with clear message.
- **Effort:** 1 hour
- **Depends on:** T-F2.2

## 8. Unit Tests

### 8.1 classical_rule model

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_rule_composite_pk_enforced` | 2 inserts with same `(rule_id, source_id, version)` | IntegrityError on second | PK works |
| `test_rule_fk_to_source` | rule with unknown `source_id` | IntegrityError | dim FK enforced |
| `test_rule_effective_dates_nullable_to` | insert with `effective_to=NULL` | accepts; shows in `effective IS NULL` index | active-rule filtering |

### 8.2 technique_compute model

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_compute_idempotent_on_conflict` | 2 inserts same PK with `ON CONFLICT DO NOTHING` | 1 row | idempotency contract |
| `test_compute_fk_requires_rule_exists` | compute with no matching rule | IntegrityError | referential integrity |
| `test_compute_fk_requires_exact_version` | compute with mismatched rule_version | IntegrityError | version-lock enforced |
| `test_compute_orphan_prevented_on_rule_delete` | delete rule with compute rows | error or RESTRICT | safety |
| `test_compute_family_index_used` | `EXPLAIN` on query by (chart_id, technique_family_id) | uses idx_compute_family | index tuning |

### 8.3 aggregation_event model

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_event_append_only_semantics` | `UPDATE` on an event row | no semantic support; we enforce via app layer that only INSERTs happen | append-only contract (DB allows UPDATE but workflow forbids) |
| `test_event_experiment_composite_fk` | event with experiment_arm_id not in experiment_arm | IntegrityError | experiment integrity |
| `test_event_surface_check_constraint` | surface='junk' | CHECK violation | enum enforcement |

### 8.4 astrologer_source_preference

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_pref_valid_source_weights` | `{"bphs": 1.0, "saravali": 0.7}` | INSERT succeeds | happy path |
| `test_pref_invalid_source_key_rejected` | `{"made_up": 1.0}` | trigger raises | FK-by-trigger for JSONB keys |
| `test_pref_deprecated_source_rejected` | source marked `deprecated_at NOT NULL` | trigger raises | can't set weight on deprecated source |

### 8.5 aggregation_signal

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_signal_fk_to_event` | signal with unknown `aggregation_event_id` | IntegrityError | integrity |
| `test_signal_type_enum_enforced` | signal_type='made_up' | CHECK violation | enum enforcement |

### 8.6 Integration round-trip

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_full_path_insert_and_query` | rule → compute → aggregation → signal, each inserted and queried | all values round-trip correctly | end-to-end sanity |

## 9. EPIC-Level Acceptance Criteria

- [ ] All 5 tables exist post-migration with exact columns, constraints, indexes
- [ ] Composite FK on technique_compute → classical_rule active
- [ ] ON CONFLICT DO NOTHING works for idempotent inserts
- [ ] source_weights trigger validates against source_authority
- [ ] Pydantic result payload models cover all 10 output_shapes
- [ ] ClassicalEngine Protocol defined and usable
- [ ] Integration test passes: rule → compute → aggregation → signal path
- [ ] Unit test coverage ≥ 95% for models and trigger

## 10. Rollout Plan

- **Feature flag:** none — P0 foundation.
- **Shadow compute:** N/A.
- **Backfill:** N/A (empty on first deploy).
- **Rollback:** `alembic downgrade -1` drops tables. Safe at P0 because no production data.

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Composite FK performance degrades at 10M+ rows | Low | Medium | Indexes on FK columns; F3 partitioning caps per-partition size |
| JSONB `result` grows unbounded for some technique family | Medium | Medium | JSON Schema validation (F5) caps complexity; monitor row size percentiles |
| Trigger slows inserts on astrologer_source_preference | Low | Low | Low write volume (only when astrologer edits prefs) |
| Migration ordering bug: fact tables before dims | Medium | High | Alembic `down_revision` chain enforces F1 → F2; CI test on fresh DB |
| Soft-delete mixed with composite PK confusion | Medium | Medium | classical_rule does NOT soft-delete; uses `effective_to`. Document clearly. |

## 12. References

- Master spec: [`docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`](../../../superpowers/specs/2026-04-19-classical-techniques-expansion-design.md)
- F1 dim tables: [`F1-star-schema-dimensions.md`](./F1-star-schema-dimensions.md)
- Existing `TenantBaseModel`: `src/josi/models/base.py`
- Existing `AstrologyChart`: `src/josi/models/chart.py`
