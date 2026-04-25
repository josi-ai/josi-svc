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
last_updated: 2026-04-25
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

## 2.5 Engineering Review (Pass 2 — Locked 2026-04-25)

**Reviewer:** cpselvam + Govind (pair) · **Rubric:** 3-layer (12-point structural + 7-lens design + cross-cutting compliance) · **Conforms to:** ARCHITECTURE_DECISIONS §0.9, §0.10, §0.12, §0.13, §0.14, §1.5 · **Cascades from:** F1 Pass 2

### Summary

F2 builds on F1's dim tables; F1's Pass 2 revisions (UUID PKs, SCD Type 2, `experiment`/`experiment_arm` moved to E14a, multilingual JSONB) cascade through F2. Pass 2 locks 5 decisions and revises the schema to a shape that is simultaneously §0.14-compliant (UUID PKs + composite UNIQUE business keys), §0.12-compliant (no bare `id`), §0.9-compliant (row_id pins for SCD reconstructability), and ergonomic (text-code FKs preserve readable logs/analytics).

### Layer 1 — Structural Completeness (12-point)

| # | Item | Status | Note |
|:-:|---|:-:|---|
| 1 | Frontmatter complete | ✅ | `last_updated` bumped to 2026-04-25 on Pass 2 lock |
| 2 | Purpose clear | ✅ | §1 articulates idempotency / composite FK / append-only invariants |
| 3 | Scope precise | ✅ | §2.1/§2.2 in+out; §2.3 deps on F1 + existing models |
| 4 | Research substantive | ✅ | §3 covers composite FK rationale, append-only aggregation, index strategy, 4 rejected alternatives |
| 5 | Open questions resolved | ✅ | §4 (6 original) + §2.5 Pass 2 Decisions (F2-Q1–F2-Q5) |
| 6 | Component design executable | ✅ | §5 full SQL + Pydantic + Protocol; revised schema below |
| 7 | User stories testable | ✅ | §6 US-F2.1–F2.4 |
| 8 | Tasks decomposed | ✅ | §7 T-F2.1–F2.6 + §2.5 Task DAG |
| 9 | Unit tests enumerated | ✅ | §8.1–§8.6 full tables (models / trigger / integration) |
| 10 | Acceptance criteria binary | ✅ | §9 + expanded §2.5 list |
| 11 | Rollout plan credible | ✅ | §10 — flag N/A justified; rollback via downgrade |
| 12 | Risks identified | ✅ | §11 — 5 risks with likelihood+impact+mitigation |

**Layer 1 verdict:** 12 / 12 pass.

### Layer 2 — Design Quality (7-lens)

| # | Lens | Finding | Status |
|:-:|---|---|:-:|
| 1 | Futuristic | Partition-ready (F3 LIST+HASH), experiment hooks deferred cleanly to E14a, signal log ready for learning loop | ✅ |
| 2 | Future-proof | Text-code FKs + row_id UUID pins give stable business identity + SCD versioning in one shape. F1 revisions absorbed cleanly via F2-Q1/Q2/Q5. | ✅ (resolved by Pass 2) |
| 3 | Extendible | New techniques plug in via YAML classical_rule rows (F6); no F2 schema changes needed | ✅ |
| 4 | Audit-ready | `input_fingerprint` + `output_hash` (F13) + `{dim}_row_id` SCD pins → full §0.9 reconstructability. F2-Q5 applied. | ✅ (resolved by Pass 2) |
| 5 | Performant | 3 tuned indexes; denormalized `technique_family_code` avoids joins for family-scoped reads | ✅ |
| 6 | User-friendly | N/A — data layer | N/A |
| 7 | AI-first | `result JSONB` typed by Pydantic per output_shape; typed tool-use contract deferred to F10 | ✅ |

**Layer 2 verdict:** 6 / 6 applicable lenses green after Pass 2 Decisions; 1 N/A.

### Layer 3 — Cross-cutting Compliance

| Lock | Requirement | Status | Evidence |
|---|---|:-:|---|
| §0.5 liability | Crisis flow for AI surfaces | N/A | Data layer; no user-facing AI |
| §0.8 eval harness | Golden dataset + LLM-as-judge | N/A | No AI surface; Eval cases section confirms |
| §0.9 reconstructability | Fact tables pin exact rule + SCD versions at compute time | ✅ | F2-Q5: `source_authority_row_id`, `technique_family_row_id`, `output_shape_row_id` on `technique_compute`; `aggregation_strategy_row_id` on `aggregation_event`; existing `input_fingerprint` + `output_hash` (F13) retained |
| §0.10 task DAG + path overlap | DAG entry + path overlap declared | ✅ | 6-task DAG in §2.5; path overlap declared (models/classical, schemas/classical, services/classical) |
| §0.12 naming | No bare `id`; full English identifiers | ✅ | F2-Q4: `id` → `aggregation_event_id` / `aggregation_signal_id`. `rule_id TEXT` → `rule_code TEXT`; `source_id TEXT` → `source_authority_code TEXT`; `strategy_id` → `aggregation_strategy_code`; `family_id` → `technique_family_code`; `shape_id` → `output_shape_code` (F1 already renamed). Trigger `validate_source_weights_keys` OK. |
| §0.13 config-based versioning | SCD row_id pins replace git SHA or TEXT version snapshots | ✅ | F2-Q5: `strategy_version TEXT` removed; `aggregation_strategy_row_id UUID` pins the SCD row. `classical_rule.version` retained (rule registry is its own immutable-append versioning per §3.2). |
| §0.14 PK conventions | UUIDv7 PK + composite UNIQUE business key on real-entity tables | ✅ | F2-Q1: `classical_rule_id UUID PK` + `UNIQUE(rule_code, source_authority_code, version)`; `technique_compute_id UUID PK` + `UNIQUE(chart_id, classical_rule_id)`; `aggregation_event_id UUID PK`; `aggregation_signal_id UUID PK`; `astrologer_source_preference` keeps composite PK (config table, genuinely identified by `(user_id, technique_family_code)`) — documented exception |
| §1.5 multilingual | `classical_names` JSONB on rule registry rows | ✅ | Present on `classical_rule` (existing); inherited FK dims carry own JSONB per F1 |
| F1 cascade | F2 FKs align with F1 revised dim shape | ✅ | F2-Q2: text-code FKs against F1 `{dim}_code` UNIQUE columns. F2-Q3: `experiment` / `experiment_arm` removed from F2 — E14a re-adds. |

**Layer 3 verdict:** 7 applicable locks ✅; 2 N/A (justified); 0 ⚠️/❌.

### Pass 2 Decisions

| # | Gap | Decision |
|---|---|---|
| F2-Q1 | Composite PKs violate §0.14 (UUID PK convention) | **UUID PK + composite UNIQUE** on real-entity tables. `classical_rule_id UUID PK DEFAULT uuidv7()` + `UNIQUE(rule_code, source_authority_code, version)`. `technique_compute_id UUID PK DEFAULT uuidv7()` + `UNIQUE(chart_id, classical_rule_id)`. `astrologer_source_preference` keeps composite PK as a config-table exception (documented). |
| F2-Q2 | FK column types (F1 cascade) | **Text-code FKs** — `{dim}_code TEXT REFERENCES {dim}({dim}_code)` for stable, readable business identity in fact rows and logs. Combined with F2-Q5 row_id pins where SCD reconstructability is needed. |
| F2-Q3 | `experiment` / `experiment_arm` FK (F1-Q4 cascade) | **Removed from F2.** Both columns + composite FK + `idx_aggregation_experiment` index deleted. E14a re-adds via `ALTER TABLE aggregation_event ADD COLUMN experiment_row_id UUID REFERENCES experiment(experiment_row_id)` when it ships. |
| F2-Q4 | `id` column naming (§0.12) | **Renamed.** `aggregation_event.id` → `aggregation_event_id`; `aggregation_signal.id` → `aggregation_signal_id`. |
| F2-Q5 | SCD version pinning (§0.9) | **Added row_id UUID columns** alongside text-code FKs. On `technique_compute`: `source_authority_row_id UUID NOT NULL REFERENCES source_authority(source_authority_row_id)`, `technique_family_row_id UUID NOT NULL REFERENCES technique_family(technique_family_row_id)`, `output_shape_row_id UUID NOT NULL REFERENCES output_shape(output_shape_row_id)`. On `aggregation_event`: `aggregation_strategy_row_id UUID NOT NULL REFERENCES aggregation_strategy(aggregation_strategy_row_id)` (replaces `strategy_version TEXT` snapshot). |

### Revised schema (applied — supersedes §5.2 below)

**`classical_rule` — immutable rule registry, UUID PK + composite business key**

```sql
CREATE TABLE classical_rule (
    classical_rule_id        UUID PRIMARY KEY DEFAULT uuidv7(),
    rule_code                TEXT NOT NULL,                          -- e.g., 'yoga.raja.gaja_kesari'
    source_authority_code    TEXT NOT NULL REFERENCES source_authority(source_authority_code),
    source_authority_row_id  UUID NOT NULL REFERENCES source_authority(source_authority_row_id),
    version                  TEXT NOT NULL,                          -- semver for this rule's own evolution
    content_hash             CHAR(64) NOT NULL,                      -- F13: sha256 of canonical rule body JSON
    technique_family_code    TEXT NOT NULL REFERENCES technique_family(technique_family_code),
    technique_family_row_id  UUID NOT NULL REFERENCES technique_family(technique_family_row_id),
    output_shape_code        TEXT NOT NULL REFERENCES output_shape(output_shape_code),
    output_shape_row_id      UUID NOT NULL REFERENCES output_shape(output_shape_row_id),
    rule_body                JSONB NOT NULL,                         -- DSL payload (F6)
    citation                 TEXT,                                   -- "BPHS 36.14-16"
    classical_names          JSONB NOT NULL DEFAULT '{}'::jsonb,     -- §1.5 multilingual
    effective_from           TIMESTAMPTZ NOT NULL DEFAULT now(),
    effective_to             TIMESTAMPTZ,                            -- null = active
    created_at               TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT unique_classical_rule_business_key
        UNIQUE (rule_code, source_authority_code, version)
);

CREATE INDEX idx_classical_rule_family ON classical_rule(technique_family_code);
CREATE INDEX idx_classical_rule_active
    ON classical_rule(rule_code, source_authority_code)
    WHERE effective_to IS NULL;
```

**`technique_compute` — UUID PK + composite UNIQUE + SCD row_id pins**

```sql
CREATE TABLE technique_compute (
    technique_compute_id     UUID PRIMARY KEY DEFAULT uuidv7(),
    organization_id          UUID NOT NULL REFERENCES organization(organization_id),
    chart_id                 UUID NOT NULL REFERENCES astrology_chart(chart_id),

    classical_rule_id        UUID NOT NULL REFERENCES classical_rule(classical_rule_id),
    rule_code                TEXT NOT NULL,                          -- denormalized for fast filters + readable logs
    source_authority_code    TEXT NOT NULL REFERENCES source_authority(source_authority_code),
    source_authority_row_id  UUID NOT NULL REFERENCES source_authority(source_authority_row_id),
    rule_version             TEXT NOT NULL,

    technique_family_code    TEXT NOT NULL REFERENCES technique_family(technique_family_code),
    technique_family_row_id  UUID NOT NULL REFERENCES technique_family(technique_family_row_id),
    output_shape_code        TEXT NOT NULL REFERENCES output_shape(output_shape_code),
    output_shape_row_id      UUID NOT NULL REFERENCES output_shape(output_shape_row_id),

    result                   JSONB NOT NULL,
    input_fingerprint        CHAR(64) NOT NULL,                      -- F13
    output_hash              CHAR(64) NOT NULL,                      -- F13
    computed_at              TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT unique_technique_compute_chart_rule
        UNIQUE (chart_id, classical_rule_id)
);

CREATE INDEX idx_compute_family
    ON technique_compute(chart_id, technique_family_code);
CREATE INDEX idx_compute_org_family
    ON technique_compute(organization_id, technique_family_code, computed_at DESC);
```

**`aggregation_event` — UUID PK (renamed), experiment FKs removed, strategy SCD pinned**

```sql
CREATE TABLE aggregation_event (
    aggregation_event_id         UUID PRIMARY KEY DEFAULT uuidv7(),
    organization_id              UUID NOT NULL REFERENCES organization(organization_id),
    chart_id                     UUID NOT NULL REFERENCES astrology_chart(chart_id),

    technique_family_code        TEXT NOT NULL REFERENCES technique_family(technique_family_code),
    technique_family_row_id      UUID NOT NULL REFERENCES technique_family(technique_family_row_id),
    technique_code               TEXT NOT NULL,                      -- e.g., 'yoga.raja.gaja_kesari'; nullable for family-level aggregation

    aggregation_strategy_code    TEXT NOT NULL REFERENCES aggregation_strategy(aggregation_strategy_code),
    aggregation_strategy_row_id  UUID NOT NULL REFERENCES aggregation_strategy(aggregation_strategy_row_id),
    -- NB: strategy_version TEXT removed — pinned via aggregation_strategy_row_id per F2-Q5

    inputs_hash                  CHAR(64) NOT NULL,                  -- hash of (classical_rule_id) tuples consumed
    output                       JSONB NOT NULL,
    surface                      TEXT NOT NULL CHECK (surface IN
                                   ('b2c_chat','astrologer_pro','ultra_ai','internal_experiment','api')),
    user_mode                    TEXT NOT NULL CHECK (user_mode IN ('auto','custom','ultra')),
    computed_at                  TIMESTAMPTZ NOT NULL DEFAULT now()
    -- NB: experiment_id / experiment_arm_id / composite FK removed per F2-Q3; E14a re-adds
);

CREATE INDEX idx_aggregation_chart
    ON aggregation_event(chart_id, technique_family_code, aggregation_strategy_code, computed_at DESC);
CREATE INDEX idx_aggregation_org_recent
    ON aggregation_event(organization_id, computed_at DESC);
-- NB: idx_aggregation_experiment dropped per F2-Q3; E14a re-creates
```

**`aggregation_signal` — UUID PK (renamed)**

```sql
CREATE TABLE aggregation_signal (
    aggregation_signal_id     UUID PRIMARY KEY DEFAULT uuidv7(),
    organization_id           UUID NOT NULL REFERENCES organization(organization_id),
    aggregation_event_id      UUID NOT NULL REFERENCES aggregation_event(aggregation_event_id),
    signal_type               TEXT NOT NULL CHECK (signal_type IN
                                ('astrologer_override_implicit','astrologer_override_explicit',
                                 'user_thumbs_up','user_thumbs_down',
                                 'outcome_positive','outcome_negative','outcome_neutral')),
    signal_value              JSONB NOT NULL DEFAULT '{}'::jsonb,
    recorded_by_user_id       UUID REFERENCES "user"(user_id),
    recorded_at               TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_signal_event    ON aggregation_signal(aggregation_event_id, signal_type);
CREATE INDEX idx_signal_org_recent ON aggregation_signal(organization_id, recorded_at DESC);
```

**`astrologer_source_preference` — composite PK retained (config table exception per §0.14)**

```sql
CREATE TABLE astrologer_source_preference (
    organization_id                   UUID NOT NULL REFERENCES organization(organization_id),
    user_id                           UUID NOT NULL REFERENCES "user"(user_id),
    technique_family_code             TEXT NOT NULL REFERENCES technique_family(technique_family_code),
    source_weights                    JSONB NOT NULL DEFAULT '{}'::jsonb,
                                      -- keys validated against source_authority_code by trigger
    preferred_aggregation_strategy_code  TEXT REFERENCES aggregation_strategy(aggregation_strategy_code),
    preference_mode                   TEXT NOT NULL DEFAULT 'auto'
                                      CHECK (preference_mode IN ('auto','custom','ultra')),
    created_at                        TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at                        TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (user_id, technique_family_code)
);

-- Trigger renamed source_id → source_authority_code to match F1
CREATE OR REPLACE FUNCTION validate_source_weights_keys()
RETURNS trigger AS $$
DECLARE
    invalid_key TEXT;
BEGIN
    SELECT key INTO invalid_key
    FROM jsonb_object_keys(NEW.source_weights) AS key
    WHERE key NOT IN (
        SELECT source_authority_code FROM source_authority
        WHERE is_current = true AND deprecated_at IS NULL
    )
    LIMIT 1;
    IF invalid_key IS NOT NULL THEN
        RAISE EXCEPTION 'Invalid source_authority_code in source_weights: %', invalid_key;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_validate_source_weights
    BEFORE INSERT OR UPDATE ON astrologer_source_preference
    FOR EACH ROW EXECUTE FUNCTION validate_source_weights_keys();
```

### Naming rule (§0.12) compliance — delta from original §5.2

| Original identifier | Revised identifier | Reason |
|---|---|---|
| `classical_rule(rule_id, source_id, version)` composite PK | `classical_rule_id UUID PK` + `UNIQUE(rule_code, source_authority_code, version)` | §0.14 + F2-Q1 |
| `aggregation_event.id UUID` | `aggregation_event_id UUID` | §0.12 + F2-Q4 |
| `aggregation_signal.id UUID` | `aggregation_signal_id UUID` | §0.12 + F2-Q4 |
| `rule_id TEXT` (on compute) | `rule_code TEXT` + `classical_rule_id UUID FK` | §0.12 no bare `id` + F2-Q1 |
| `source_id TEXT` | `source_authority_code TEXT` + `source_authority_row_id UUID` | F1 rename + F2-Q2 + F2-Q5 |
| `family_id TEXT` (on compute) | `technique_family_code TEXT` + `technique_family_row_id UUID` | F1 rename + F2-Q2 + F2-Q5 |
| `shape_id TEXT` | `output_shape_code TEXT` + `output_shape_row_id UUID` | F1 rename + F2-Q2 + F2-Q5 |
| `strategy_id TEXT` | `aggregation_strategy_code TEXT` + `aggregation_strategy_row_id UUID` | F1 rename + F2-Q2 + F2-Q5 |
| `strategy_version TEXT` | *removed* | Replaced by `aggregation_strategy_row_id` per F2-Q5 |
| `experiment_id TEXT` / `experiment_arm_id TEXT` | *removed* | Moved to E14a per F2-Q3 |

### Path overlap declaration

F2 tasks reserve these paths (no other P0 PRD may write here):

```
src/josi/models/classical/classical_rule.py
src/josi/models/classical/technique_compute.py
src/josi/models/classical/aggregation_event.py
src/josi/models/classical/aggregation_signal.py
src/josi/models/classical/astrologer_source_preference.py
src/josi/schemas/classical/result_payloads.py
src/josi/schemas/classical/aggregation_outputs.py
src/josi/schemas/classical/signal_payloads.py
src/josi/services/classical/base_engine.py
src/alembic/versions/                   # One migration file (sequenced after F1)
tests/unit/models/classical/test_classical_rule.py
tests/unit/models/classical/test_technique_compute.py
tests/unit/models/classical/test_aggregation_event.py
tests/unit/models/classical/test_aggregation_signal.py
tests/unit/models/classical/test_astrologer_source_preference.py
tests/integration/classical/test_f2_round_trip.py
```

F2 extends F1's `src/josi/models/classical/` directory; no conflict because file names are disjoint.

### Task DAG entries (for §0.10 agent-team orchestration)

```json
[
  {
    "task_id": "F2-schema-migration",
    "prd_ref": "F2",
    "role": "coder + migration-writer",
    "depends_on": ["F1-schema-migration", "F1-seed-yaml-authoring"],
    "acceptance_criteria": "5 fact tables (classical_rule, technique_compute, aggregation_event, aggregation_signal, astrologer_source_preference) via Alembic migration sequenced after F1. UUIDv7 PKs on 4 real-entity tables; composite PK on astrologer_source_preference config table. All FKs resolve to F1 dim tables. source_weights trigger installed. Migration-lint passes. mypy passes on SQLModel classes.",
    "affected_paths": ["src/josi/models/classical/classical_rule.py", "src/josi/models/classical/technique_compute.py", "src/josi/models/classical/aggregation_event.py", "src/josi/models/classical/aggregation_signal.py", "src/josi/models/classical/astrologer_source_preference.py", "src/alembic/versions/"],
    "test_command": "poetry run alembic upgrade head && poetry run pytest tests/unit/models/classical/",
    "max_turns": 60,
    "model_tier": "mid",
    "retry_budget": 1
  },
  {
    "task_id": "F2-pydantic-result-payloads",
    "prd_ref": "F2",
    "role": "coder",
    "depends_on": ["F1-seed-yaml-authoring"],
    "acceptance_criteria": "Pydantic BaseModel per output_shape (10 shapes from F1). .model_json_schema() works. Every shape is discriminator-addressable. Unit tests validate round-trip from JSONB to typed model.",
    "affected_paths": ["src/josi/schemas/classical/result_payloads.py", "src/josi/schemas/classical/aggregation_outputs.py", "src/josi/schemas/classical/signal_payloads.py"],
    "test_command": "poetry run pytest tests/unit/schemas/classical/",
    "max_turns": 40,
    "model_tier": "mid",
    "retry_budget": 1
  },
  {
    "task_id": "F2-classical-engine-protocol",
    "prd_ref": "F2",
    "role": "coder",
    "depends_on": ["F2-schema-migration"],
    "acceptance_criteria": "ClassicalEngine Protocol in base_engine.py. Helper for idempotent upsert via ON CONFLICT on UNIQUE(chart_id, classical_rule_id). Test subclass round-trips successfully.",
    "affected_paths": ["src/josi/services/classical/base_engine.py", "tests/unit/services/classical/test_base_engine.py"],
    "test_command": "poetry run pytest tests/unit/services/classical/test_base_engine.py",
    "max_turns": 40,
    "model_tier": "mid",
    "retry_budget": 1
  },
  {
    "task_id": "F2-trigger-validation",
    "prd_ref": "F2",
    "role": "coder",
    "depends_on": ["F2-schema-migration"],
    "acceptance_criteria": "source_weights trigger validates JSONB keys against source_authority.source_authority_code WHERE is_current AND deprecated_at IS NULL. Rejects unknown + deprecated keys with clear error. 3+ test cases (valid / unknown / deprecated).",
    "affected_paths": ["tests/unit/models/classical/test_astrologer_source_preference.py"],
    "test_command": "poetry run pytest tests/unit/models/classical/test_astrologer_source_preference.py",
    "max_turns": 20,
    "model_tier": "cheap",
    "retry_budget": 1
  },
  {
    "task_id": "F2-integration-round-trip",
    "prd_ref": "F2",
    "role": "coder + qa",
    "depends_on": ["F2-schema-migration", "F2-pydantic-result-payloads", "F2-classical-engine-protocol"],
    "acceptance_criteria": "End-to-end test: seed dim rows (F1) → insert classical_rule → insert technique_compute with SCD row_id pins → insert aggregation_event → insert aggregation_signal → verify all reads return expected shapes. Reconstructability test: given technique_compute.source_authority_row_id, resolve to exact SCD version of source_authority at compute time.",
    "affected_paths": ["tests/integration/classical/test_f2_round_trip.py"],
    "test_command": "poetry run pytest tests/integration/classical/test_f2_round_trip.py",
    "max_turns": 40,
    "model_tier": "mid",
    "retry_budget": 1
  },
  {
    "task_id": "F2-index-explain-tests",
    "prd_ref": "F2",
    "role": "coder + qa",
    "depends_on": ["F2-schema-migration"],
    "acceptance_criteria": "EXPLAIN tests assert index usage: idx_compute_family used for (chart_id, technique_family_code) queries; idx_aggregation_chart used for strategy-scoped reads; idx_signal_event used for signal-by-event reads. Fails on seq scan.",
    "affected_paths": ["tests/integration/classical/test_f2_indexes.py"],
    "test_command": "poetry run pytest tests/integration/classical/test_f2_indexes.py",
    "max_turns": 30,
    "model_tier": "mid",
    "retry_budget": 1
  }
]
```

**Total F2 implementation estimate:** 6 parallel tasks; 2 (payloads + protocol) can start as soon as F1-seed-yaml-authoring lands. Estimated cost ~$20-30. Wall-clock ~3-4 days at full agent parallelism.

### Acceptance criteria (expanded beyond §9)

In addition to existing acceptance criteria:
- [ ] All 5 tables conform to §0.14 PK conventions (UUID PK on 4 real-entity tables; composite PK on astrologer_source_preference config-table exception documented)
- [ ] All FKs resolve: text-code FKs to F1 `{dim}_code` UNIQUE columns; row_id FKs to F1 SCD `{dim}_row_id` PK columns
- [ ] §0.9 reconstructability test passes: given a technique_compute row and its `{source_authority,technique_family,output_shape}_row_id` + `input_fingerprint`, the compute output can be regenerated bit-exact
- [ ] No bare `id` columns (§0.12) — verified by ruff rule N997+
- [ ] `experiment_id` / `experiment_arm_id` / `strategy_version` fields NOT present in F2 tables
- [ ] Trigger `validate_source_weights_keys` references `source_authority_code` column (not `source_id`) and filters by `is_current = true`
- [ ] ON CONFLICT DO NOTHING works against `UNIQUE(chart_id, classical_rule_id)` for technique_compute idempotency

### Eval cases

N/A — F2 is data-layer foundation; no AI surface. §0.8 eval harness does not apply.

### Cross-references

- `ARCHITECTURE_DECISIONS.md §0.9` — fact tables pin `{dim}_row_id UUID` for reconstructability (F2-Q5 applied)
- `ARCHITECTURE_DECISIONS.md §0.10` — task DAG + path overlap
- `ARCHITECTURE_DECISIONS.md §0.12` — no bare `id`; full English identifiers (F2-Q4 applied)
- `ARCHITECTURE_DECISIONS.md §0.13` — config-based versioning via SCD row_id, not TEXT snapshots (F2-Q5 removed `strategy_version`)
- `ARCHITECTURE_DECISIONS.md §0.14` — UUIDv7 PK + composite UNIQUE business key (F2-Q1 applied)
- `F1-star-schema-dimensions.md §2.5` — F1 revised shape that F2 FKs now align with (F2-Q2 applied)
- `DECISIONS.md §1.5` — multilingual `classical_names` on `classical_rule`
- **E14a** — re-adds `experiment_row_id UUID` column to `aggregation_event` when experiment framework ships (F2-Q3 defers)

---

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
