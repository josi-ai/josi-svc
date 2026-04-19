---
prd_id: F3
epic_id: F3
title: "LIST + HASH partitioning scheme for technique_compute; monthly RANGE partitioning for aggregation_event"
phase: P0-foundation
tags: [#performance, #correctness]
priority: must
depends_on: [F1, F2]
enables: [F9, S2, S4, S7, all engine EPICs at scale]
classical_sources: []
estimated_effort: 3 days
status: draft
author: Govind
last_updated: 2026-04-19
---

# F3 — Partitioning from Day One

## 1. Purpose & Rationale

At 10M users with ~250 yogas × 10 sources × 1 dasa system × 6 dasa levels × 12 ashtakavarga entries × 1 tajaka = ~15–30 rows/chart in `technique_compute`, we are looking at 150M–300M rows within 24 months. `aggregation_event` scales similarly: every chart read that engages the aggregation layer appends a row; at 10M DAU with 5 reads/day average, that is 50M events/day, 1.5B/month.

Partitioning an existing 300M-row table is a multi-day operation that requires either `pg_partman`'s online partitioning (table rewrite + batched data move) or a full dump/restore. Both require serious downtime engineering and carry real risk. Partitioning an **empty** table — the moment we ship F2 — is free: `CREATE TABLE ... PARTITION BY` + empty child partitions + attach.

This PRD establishes the partitioned physical layout at the moment the tables first ship. Even at 10k users (pre-launch scale) where data fits on a laptop, the structure is in place so we never pay the migration cost later.

**Invariants set here:**
- `technique_compute` is `PARTITION BY LIST (technique_family_id)` with one partition per technique family, and each family is `PARTITION BY HASH (chart_id)` into 4 sub-partitions.
- `aggregation_event` is `PARTITION BY RANGE (computed_at)` with one partition per calendar month, auto-created by a scheduled job 60 days ahead.
- All queries filter on `chart_id` **and** `technique_family_id` to enable partition pruning.
- Indexes are created per-partition (PG14+ propagates from parent automatically for partitioned indexes).

## 2. Scope

### 2.1 In scope
- Rewrite the `technique_compute` DDL from F2 as `PARTITION BY LIST (technique_family_id)` + child `PARTITION BY HASH (chart_id)`
- 16 LIST partitions matching the 16 technique families seeded in F1
- 4 HASH sub-partitions per LIST partition = 64 leaf partitions total
- Rewrite the `aggregation_event` DDL from F2 as `PARTITION BY RANGE (computed_at)` with one partition per month
- Initial seed of monthly partitions: 12 months (current month ± 6)
- Partition-management service (`PartitionManager`) that creates forward partitions on a schedule
- Assessment of `pg_partman` availability on Cloud SQL PostgreSQL 17 and fallback if unavailable
- Foreign key behavior on partitioned tables (PG14+)
- Alembic migration strategy for partitioned DDL
- Partition-pruning verification via `EXPLAIN (ANALYZE, BUFFERS)` tests

### 2.2 Out of scope
- Sharding across physical databases (that is P4 — S7)
- Automated old-partition archival to ClickHouse (P4 — S4)
- Sub-hash rebalancing beyond 4 buckets (handled at P3 when row counts warrant; doc includes sizing curve)
- Per-tenant partitioning (P4 — S7)
- `chart_reading_view` partitioning (F9 — single table per chart, not fact-scale)

### 2.3 Dependencies
- F1 (technique_family seeded — partition names derived from `family_id`)
- F2 (table column definitions — this PRD amends the DDL)
- Cloud SQL PostgreSQL 17 (confirmed) — supports LIST + HASH multi-level partitioning and FKs on partitioned tables
- `AstrologyChart` model (FK target for `chart_id`)

## 3. Technical Research

### 3.1 Why partition empty tables now

Postgres cannot retroactively partition a populated table via DDL. Options for migrating a large table to partitioned form:

1. **`pg_partman`'s `create_parent()` + `partition_data_time`/`partition_data_id`** — batched online move, but requires the parent table already exists as a regular table with matching structure, then rename-swap. Row-by-row INSERT of 300M rows into partitions, even batched with `COMMIT` per batch, takes 12–48 hours and doubles disk usage during migration.
2. **Full dump/restore with new schema** — simplest but requires full downtime proportional to data size.
3. **Online rewrite via logical replication** — build a partitioned shadow, replicate, cut over. 1–2 weeks of engineering, shared RDS upgrade window semantics.

All three cost engineering time + operational risk. Doing it on the empty table at F2 ship costs nothing: `CREATE TABLE ... PARTITION BY` is the same DDL cost as an unpartitioned `CREATE TABLE`, and every insert henceforth goes to the right partition automatically.

This is a tax paid entirely in developer complexity (partition-aware queries, partition management), not in runtime, migration cost, or downtime. That trade is favorable only if we believe the data will ever grow — which, per the business plan, it will.

### 3.2 Why LIST on `technique_family_id`

Technique families are the natural coarse-grained isolation. Yoga rows and ashtakavarga rows have:
- Different read workloads (yoga queried by chart overview; ashtakavarga queried by detailed chart view or transit analysis)
- Different write cadences (yoga computed once per chart at creation + once per rule-change; ashtakavarga recomputed when transit context changes)
- Different row sizes (yoga result JSONB ~400 bytes; ashtakavarga numeric_matrix ~2.5KB)
- Different retention needs in the future (yogas are forever; ashtakavarga transit snapshots may be archivable)

LIST partitioning lets us:
- Drop an entire family's data in one `DROP TABLE partition_name` (O(1), not O(N) `DELETE`)
- VACUUM / REINDEX each family independently on different schedules
- Apply per-family row-level security policies if needed (not in P0, but cheap later)
- Write per-family backfill jobs that only scan the relevant partition

16 families × 1 LIST partition each = 16 LIST partitions.

### 3.3 Why HASH sub-partitioning on `chart_id`

Within a family, the dominant read path is "all rows for chart X". That filter must be an equality predicate on a partitioning key to prune. HASH partitioning on `chart_id` gives:
- Even data distribution (any hash function will approximately evenly distribute UUID v4 values)
- Constant-time partition lookup for `WHERE chart_id = ?` queries
- Natural foundation for future sharding: HASH partition n goes to physical shard n mod num_shards

**Initial bucket count: 4.** Rationale:
- At 10k users × 30 rows each / 16 families = ~1875 rows per family partition → 470 rows/bucket. Vacuous at this scale.
- At 10M users × 30 rows each / 16 = ~18.75M rows per family → 4.7M rows/bucket. Still fits in memory-class queries.
- At 100M users × 30 rows each / 16 = 187M rows per family → 47M rows/bucket. Starts to warrant more buckets.

**Migration path to more buckets:** at P3/P4 scale we can re-hash by detaching one hash partition, creating two hash partitions covering its key range (requires custom hash function wrappers; Postgres's built-in hash has fixed modulus semantics), and re-inserting. This is planned but not in F3. For now, 4 buckets is adequate up to 100M users.

### 3.4 Why RANGE by month on `aggregation_event`

`aggregation_event` is time-series: rows are written continuously, read recently (last day for user-visible UI, last 30 days for astrologer-facing analytics, last 90 days for experiment readouts), and eventually archived. Monthly RANGE partitioning:
- Makes "events this month" queries prune to one partition
- Makes "events older than 90 days" archival a `DETACH PARTITION` + move — O(1) at the planner level
- Keeps each partition size bounded (1.5B events/month at 10M DAU is the eventual peak; partitions hold one month each)
- Indexes per partition stay under 100GB-ish, keeping VACUUM tractable

### 3.5 pg_partman availability on Cloud SQL PostgreSQL 17

As of 2026-04 Cloud SQL for PostgreSQL 17 **supports `pg_partman` 5.x** as an extension (confirmed: the `cloudsql.enable_pg_partman` flag and the extension list both show it). We will use `pg_partman` for the `aggregation_event` monthly partition rotation because:
- Battle-tested, less code than rolling our own
- Handles edge cases (DST boundaries, partition name collisions, retention)
- Emits structured events we can log

For `technique_compute` (LIST + HASH), we do **not** use `pg_partman` — LIST partitioning is static (16 families = 16 partitions for all time) and HASH partitioning is also static (4 buckets, created once at migration). These partitions are declared in the migration file and never change.

**Fallback plan if `pg_partman` becomes unavailable** (e.g., enterprise Cloud SQL variant or self-hosted PG without extension access):
- A `PartitionManager` service (below) implements minimum viable monthly rotation via plain SQL in a Celery/procrastinate beat task running daily.
- Cost: ~200 lines of Python; parity with `pg_partman` for our narrow use case.

### 3.6 Partition pruning: query requirements

Partition pruning only activates when the planner can statically or dynamically determine which partitions a query must touch. Required predicates:

- `technique_compute`:
  - For LIST pruning: `WHERE technique_family_id = ?` (literal or parameterized value known at plan time)
  - For HASH pruning (within a family): `WHERE chart_id = ?` (also planner-known)
  - Ideal query pattern: `WHERE technique_family_id = ? AND chart_id = ?` → prunes to a single leaf partition
  - Queries with only `WHERE chart_id = ?` still prune HASH within **every** LIST partition — 16 partitions touched instead of 1, but pruning still cuts cost by 4× within each family. The app layer should always supply `technique_family_id` when known.
- `aggregation_event`:
  - For RANGE pruning: `WHERE computed_at >= ? AND computed_at < ?` (explicit half-open range)
  - Or point query on `computed_at` equality (rare, but supported)
  - Queries without `computed_at` in the predicate scan all partitions — this is fine for rare cross-time analytics but must be avoided in user-facing read paths.

We will add an ADR (`docs/markdown/adr/partitioning-query-requirements.md`) documenting these predicate requirements and update the `ChartService` / `AggregationService` query builders to always supply `technique_family_id` and time ranges where possible.

### 3.7 Indexes on partitioned tables (PG14+)

Creating an index on the parent partitioned table in PG14+ creates the index on every existing and future partition automatically. We declare indexes once at the parent level; Postgres handles propagation.

Exception: creating a UNIQUE index requires the unique key to include the partition key. The `technique_compute` composite PK `(chart_id, rule_id, source_id, rule_version)` includes `chart_id` (HASH key) but does NOT include `technique_family_id` (LIST key). Therefore PG cannot enforce the PK uniquely across all LIST partitions via a single top-level index.

**Resolution:** the PK must include `technique_family_id`. Since `(rule_id, source_id, rule_version)` already uniquely identifies a rule and a rule belongs to exactly one `technique_family_id` (classical_rule enforces this), adding `technique_family_id` to the PK is a no-op logically — it is functionally dependent on `rule_id`. We add it explicitly to the PK: `PRIMARY KEY (chart_id, technique_family_id, rule_id, source_id, rule_version)`.

This is a minor amendment to F2 captured in this PRD's migration. F2's SQLModel class will gain `technique_family_id` in its PK tuple.

### 3.8 Foreign keys on partitioned tables (PG14+)

PG14 introduced FK support on partitioned tables (both outgoing FKs from partitioned table and incoming FKs targeting a partitioned table). PG16 broadened this. We are on PG17 → full FK support.

- `technique_compute` (partitioned) has outgoing composite FK to `classical_rule` (not partitioned) — supported.
- No table currently has a FK **targeting** `technique_compute` or `aggregation_event`, so the "incoming FK to partitioned table" case does not arise.

### 3.9 Alembic migration challenges

Alembic's autogenerate does NOT detect partitioning directives (`PARTITION BY`, `ATTACH PARTITION`). We must hand-craft the partitioning DDL using `op.execute()` inside an otherwise-autogenerated migration:

1. Run `alembic revision --autogenerate -m "F3: partitioned technique_compute and aggregation_event"`.
2. The autogenerated output will attempt to `op.create_table()` both tables as regular (non-partitioned) tables — this is wrong.
3. Replace the autogenerated `op.create_table()` calls with `op.execute()` blocks containing the correct `CREATE TABLE ... PARTITION BY ...` SQL and per-partition `CREATE TABLE ... PARTITION OF ...` SQL.
4. Keep the autogenerated CHECK constraint and index blocks (those work against partitioned tables transparently in PG14+).
5. Document this pattern in a comment at the top of the migration for future reference.

This is an acceptable divergence from the project rule "never hand-write migrations" because Alembic autogenerate does not support partitioning directives at all as of 2026-04 — the hand-written portion is unavoidable, but it is strictly limited to the partitioning DDL.

### 3.10 Alternatives considered

| Alternative | Rejected because |
|---|---|
| Single unpartitioned table, partition later | Migration cost at scale is non-trivial; doing it empty is free |
| Hash-only partitioning on chart_id across all families | Loses per-family operational isolation; one yoga rule change invalidates the whole table's cache |
| LIST-only on family (no HASH sub-partitioning) | Single-family partitions grow too large at 100M users (187M rows); VACUUM struggles |
| Range on computed_at for technique_compute | technique_compute is recomputed irregularly; computed_at is poor sharding key; chart_id is the natural access key |
| Declarative partitioning via `pg_pathman` (3rd-party) | Not available on Cloud SQL; declarative partitioning is native since PG10 |
| Inheritance-based partitioning (pre-PG10) | Deprecated; trigger complexity; no use case |

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| HASH bucket count for technique_compute | 4 | Adequate through 100M users; migration to 8/16/64 is planned for P3/P4 |
| pg_partman usage | Use for aggregation_event; do not use for technique_compute | aggregation_event needs monthly rotation; technique_compute partitions are static |
| Fallback if pg_partman unavailable | Custom PartitionManager service (~200 LOC) | Narrow scope; keeps option open |
| Amend PK on technique_compute to include technique_family_id | Yes | Required for PG to enforce uniqueness across LIST partitions |
| Number of forward partitions pre-created for aggregation_event | 6 months forward at all times | pg_partman default `premake=4` is too short for operational safety; 6 gives a cushion |
| How to apply partitioning DDL via Alembic | op.execute() blocks inside autogenerated migration | Autogenerate can't emit PARTITION BY; hand-crafted SQL unavoidable |
| Partition naming convention | `technique_compute_{family}_h{hash_bucket}` and `aggregation_event_y{year}m{month}` | Self-documenting; sorts naturally |
| VACUUM strategy | Autovacuum per partition with scaled thresholds | Default works at current scale; revisit at P3 |
| Drop or archive old aggregation_event partitions? | Default retention: keep all; archival policy in S4 | P0 keeps data; P4 moves cold data to ClickHouse |

## 5. Component Design

### 5.1 New modules

```
src/josi/services/classical/
└── partition_manager.py        # monthly partition rotation for aggregation_event

src/josi/db/
└── partition_helpers.py        # pure functions: format partition names, compute month boundaries

src/alembic/versions/
└── <hash>_f3_partitioned_fact_tables.py
```

### 5.2 Data model DDL (amending F2)

```sql
-- ============================================================
-- technique_compute: LIST by technique_family_id, HASH sub-partition on chart_id
-- ============================================================

-- First, drop the F2 non-partitioned table (F3 migration runs after F2; in practice
-- F2 ships without actual rows so this is an empty-table swap).
DROP TABLE IF EXISTS technique_compute;

CREATE TABLE technique_compute (
    organization_id          UUID NOT NULL REFERENCES organization(organization_id),
    chart_id                 UUID NOT NULL REFERENCES astrology_chart(chart_id),
    rule_id                  TEXT NOT NULL,
    source_id                TEXT NOT NULL REFERENCES source_authority(source_id),
    rule_version             TEXT NOT NULL,
    technique_family_id      TEXT NOT NULL REFERENCES technique_family(family_id),
    output_shape_id          TEXT NOT NULL REFERENCES output_shape(shape_id),
    result                   JSONB NOT NULL,
    input_fingerprint        CHAR(64) NOT NULL,
    output_hash              CHAR(64) NOT NULL,
    computed_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (chart_id, technique_family_id, rule_id, source_id, rule_version),  -- amended from F2
    FOREIGN KEY (rule_id, source_id, rule_version)
        REFERENCES classical_rule(rule_id, source_id, version)
) PARTITION BY LIST (technique_family_id);

-- One LIST partition per family, each itself partitioned by HASH(chart_id, 4)
-- Repeat for all 16 families seeded in F1.

-- Example for 'yoga':
CREATE TABLE technique_compute_yoga
    PARTITION OF technique_compute
    FOR VALUES IN ('yoga')
    PARTITION BY HASH (chart_id);

CREATE TABLE technique_compute_yoga_h0 PARTITION OF technique_compute_yoga
    FOR VALUES WITH (MODULUS 4, REMAINDER 0);
CREATE TABLE technique_compute_yoga_h1 PARTITION OF technique_compute_yoga
    FOR VALUES WITH (MODULUS 4, REMAINDER 1);
CREATE TABLE technique_compute_yoga_h2 PARTITION OF technique_compute_yoga
    FOR VALUES WITH (MODULUS 4, REMAINDER 2);
CREATE TABLE technique_compute_yoga_h3 PARTITION OF technique_compute_yoga
    FOR VALUES WITH (MODULUS 4, REMAINDER 3);

-- Repeat for: dasa, ashtakavarga, jaimini, tajaka, transit_event, kp, prasna,
-- varga_extended, western_lot, western_fixed_star, western_harmonic, western_eclipse,
-- western_uranian, synastry, and one DEFAULT partition for any family added later:

CREATE TABLE technique_compute_default
    PARTITION OF technique_compute
    DEFAULT
    PARTITION BY HASH (chart_id);

CREATE TABLE technique_compute_default_h0 PARTITION OF technique_compute_default
    FOR VALUES WITH (MODULUS 4, REMAINDER 0);
-- ... h1, h2, h3

-- Indexes declared on parent; PG14+ propagates to all partitions.
CREATE INDEX idx_compute_family
    ON technique_compute(chart_id, technique_family_id);

CREATE INDEX idx_compute_org_family
    ON technique_compute(organization_id, technique_family_id, computed_at DESC);

-- ============================================================
-- aggregation_event: RANGE by month on computed_at
-- ============================================================

DROP TABLE IF EXISTS aggregation_event;

CREATE TABLE aggregation_event (
    id                       UUID NOT NULL DEFAULT gen_random_uuid(),
    organization_id          UUID NOT NULL REFERENCES organization(organization_id),
    chart_id                 UUID NOT NULL REFERENCES astrology_chart(chart_id),
    technique_family_id      TEXT NOT NULL REFERENCES technique_family(family_id),
    technique_id             TEXT NOT NULL,
    strategy_id              TEXT NOT NULL REFERENCES aggregation_strategy(strategy_id),
    strategy_version         TEXT NOT NULL,
    experiment_id            TEXT REFERENCES experiment(experiment_id),
    experiment_arm_id        TEXT,
    inputs_hash              CHAR(64) NOT NULL,
    output                   JSONB NOT NULL,
    surface                  TEXT CHECK (surface IN ('b2c_chat','astrologer_pro','ultra_ai','internal_experiment','api')),
    user_mode                TEXT CHECK (user_mode IN ('auto','custom','ultra')),
    computed_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (id, computed_at),   -- amended from F2: PK must include partition key
    FOREIGN KEY (experiment_id, experiment_arm_id)
        REFERENCES experiment_arm(experiment_id, arm_id)
) PARTITION BY RANGE (computed_at);

-- Seed 12 months of partitions (current month ± 6) at migration time.
-- Named aggregation_event_y2026m04, etc.
CREATE TABLE aggregation_event_y2026m04 PARTITION OF aggregation_event
    FOR VALUES FROM ('2026-04-01') TO ('2026-05-01');
CREATE TABLE aggregation_event_y2026m05 PARTITION OF aggregation_event
    FOR VALUES FROM ('2026-05-01') TO ('2026-06-01');
-- ... through 2026-10 (6 months forward) and back through 2025-11 (5 months prior)

-- Default partition catches any row outside planned range (should be zero; alerting on non-empty).
CREATE TABLE aggregation_event_default PARTITION OF aggregation_event DEFAULT;

CREATE INDEX idx_aggregation_chart
    ON aggregation_event(chart_id, technique_family_id, strategy_id, computed_at DESC);

CREATE INDEX idx_aggregation_experiment
    ON aggregation_event(experiment_id, experiment_arm_id, computed_at DESC)
    WHERE experiment_id IS NOT NULL;

CREATE INDEX idx_aggregation_org_recent
    ON aggregation_event(organization_id, computed_at DESC);

-- ============================================================
-- pg_partman registration for aggregation_event monthly rotation
-- ============================================================
CREATE EXTENSION IF NOT EXISTS pg_partman;

SELECT partman.create_parent(
    p_parent_table    => 'public.aggregation_event',
    p_control         => 'computed_at',
    p_type            => 'range',
    p_interval        => '1 month',
    p_premake         => 6,                 -- 6 months of forward partitions at all times
    p_start_partition => (date_trunc('month', now() - interval '6 months'))::text
);

-- Retention: default unlimited at P0. S4 will set retention=36 months and enable archival.
UPDATE partman.part_config
   SET retention_keep_table = true, retention_keep_index = true
 WHERE parent_table = 'public.aggregation_event';
```

### 5.3 PartitionManager service

Used if `pg_partman` becomes unavailable OR to provide app-layer observability on top of `pg_partman`. In P0 it runs as a daily procrastinate/Celery beat task invoked for monitoring only; creation is delegated to `pg_partman.run_maintenance_proc()`.

```python
# src/josi/services/classical/partition_manager.py

from dataclasses import dataclass
from datetime import date, datetime, timezone
from uuid import UUID
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class PartitionStatus:
    parent_table: str
    partition_name: str
    from_bound: str
    to_bound: str
    row_estimate: int
    size_mb: float


class PartitionManager:
    """Monthly partition rotation + observability for aggregation_event.

    In P0, partition creation is handled by pg_partman via cron
    (pg_partman.run_maintenance_proc()). This service:
      1. Verifies forward partitions exist (alerts if fewer than 3 months ahead).
      2. Enumerates current partitions for Prometheus / health reporting.
      3. Offers a pure-SQL fallback `ensure_forward_partitions()` for environments
         without pg_partman.
    """

    FORWARD_MONTHS_REQUIRED = 3
    PREMAKE_MONTHS = 6

    async def status(self, session: AsyncSession) -> list[PartitionStatus]: ...

    async def verify_forward_coverage(self, session: AsyncSession) -> bool:
        """Returns True if partitions exist for at least FORWARD_MONTHS_REQUIRED months ahead."""
        ...

    async def ensure_forward_partitions(
        self, session: AsyncSession, months_ahead: int = PREMAKE_MONTHS
    ) -> list[str]:
        """Fallback: idempotently CREATEs monthly partitions via plain SQL.
        Used only when pg_partman is unavailable."""
        ...

    async def run_pg_partman_maintenance(self, session: AsyncSession) -> None:
        """Invokes pg_partman.run_maintenance_proc() for aggregation_event."""
        await session.execute(
            text("CALL partman.run_maintenance_proc(p_analyze := true)")
        )
```

### 5.4 Partition-aware query helpers

```python
# src/josi/db/partition_helpers.py

from datetime import datetime


def aggregation_partition_name(computed_at: datetime) -> str:
    """Returns the partition name expected to hold a row with given computed_at."""
    return f"aggregation_event_y{computed_at:%Y}m{computed_at:%m}"


def month_bounds(dt: datetime) -> tuple[datetime, datetime]:
    """Returns (start_of_month, start_of_next_month) for partition boundary construction."""
    ...
```

### 5.5 Lifespan wiring

Add to FastAPI `lifespan`:
```python
# On startup: log partition status, verify forward coverage, fail startup if coverage is missing.
async with get_async_db() as session:
    status = await partition_manager.verify_forward_coverage(session)
    if not status:
        raise RuntimeError("aggregation_event forward partition coverage < 3 months")
```

## 6. User Stories

### US-F3.1: As an engineer, I want a `WHERE chart_id = ? AND technique_family_id = ?` query to scan exactly one leaf partition
**Acceptance:** `EXPLAIN` on the query shows `Append` over exactly 1 leaf partition (not 64). Scan cost in the plan is constant regardless of data size in other partitions.

### US-F3.2: As an engineer, I want the monthly partition for `aggregation_event` to exist at least 3 months ahead of the current date at all times
**Acceptance:** on startup, the `PartitionManager.verify_forward_coverage()` check passes. If it fails, the app refuses to start with a clear message. `pg_partman`'s daily maintenance job keeps 6 months ahead.

### US-F3.3: As a DBA, I want to drop a full technique family's data in O(1) when a classical source is retired
**Acceptance:** `DROP TABLE technique_compute_yoga_h0, technique_compute_yoga_h1, technique_compute_yoga_h2, technique_compute_yoga_h3` (or `DETACH PARTITION`) succeeds in <1 second regardless of row count.

### US-F3.4: As an engineer, I want inserting to a non-existent partition to hit the default partition (visible + alertable), not fail
**Acceptance:** Inserting a row with `technique_family_id = 'not_yet_seeded'` lands in `technique_compute_default`. A monitoring metric on default partition row count alerts when non-zero.

### US-F3.5: As an engineer, I want composite FKs to work on the partitioned `technique_compute`
**Acceptance:** Inserting a row with `(rule_id, source_id, rule_version)` not in `classical_rule` raises `IntegrityError` just as it did on the unpartitioned table.

## 7. Tasks

### T-F3.1: Author migration file with partitioning DDL
- **Definition:** Create `src/alembic/versions/<hash>_f3_partitioned_fact_tables.py`. Autogenerate then hand-edit: DROP + CREATE partitioned parents for both tables; CREATE LIST partitions for all 16 families + default; CREATE HASH sub-partitions (4 each) under every LIST partition; CREATE 12 monthly RANGE partitions for aggregation_event + default; re-declare indexes; re-declare composite FK; amend PKs.
- **Acceptance:** `alembic upgrade head` from a state with F2 applied succeeds. `alembic downgrade -1` drops partitioned tables and recreates F2's unpartitioned versions. `psql \d+ technique_compute` shows `Partition key: LIST (technique_family_id)`. `psql \d+ technique_compute_yoga` shows `Partition key: HASH (chart_id)`.
- **Effort:** 6 hours
- **Depends on:** F1, F2 complete

### T-F3.2: pg_partman setup and configuration
- **Definition:** Within the migration: `CREATE EXTENSION pg_partman`; call `partman.create_parent()` on `aggregation_event`; set `premake=6`, `retention_keep_table=true`. Verify via `SELECT * FROM partman.part_config`.
- **Acceptance:** `partman.part_config` has a row for `public.aggregation_event` with `premake=6` and the correct interval. Calling `partman.run_maintenance_proc()` creates any missing forward partitions.
- **Effort:** 2 hours
- **Depends on:** T-F3.1

### T-F3.3: PartitionManager service with fallback
- **Definition:** Implement `PartitionManager` with `status()`, `verify_forward_coverage()`, `ensure_forward_partitions()` (pure SQL fallback), `run_pg_partman_maintenance()`. All methods are async, accept an `AsyncSession`, and are testable without pg_partman present (fallback path).
- **Acceptance:** Unit tests pass for all four methods. Fallback `ensure_forward_partitions()` creates correctly-named partitions with correct bounds. `status()` returns accurate row estimates via `pg_class.reltuples`.
- **Effort:** 6 hours
- **Depends on:** T-F3.1

### T-F3.4: Partition-helper utilities
- **Definition:** `aggregation_partition_name()` and `month_bounds()` pure functions in `src/josi/db/partition_helpers.py`. Used by PartitionManager and by tests.
- **Acceptance:** Hypothesis property tests: for any datetime in 2020–2040, `aggregation_partition_name` matches pattern `aggregation_event_yYYYYmMM`; `month_bounds` returns UTC midnight-aligned bounds.
- **Effort:** 2 hours
- **Depends on:** none

### T-F3.5: Schedule daily `pg_partman.run_maintenance_proc()`
- **Definition:** Add a Celery/procrastinate beat task (or PG scheduled job via pg_cron if available) running at 03:00 UTC daily. Task calls `PartitionManager.run_pg_partman_maintenance()`.
- **Acceptance:** Beat schedule registered; task logs a structured line on each run including partitions created and retention actions. Monitoring alert fires if the task does not run for 48 hours.
- **Effort:** 3 hours
- **Depends on:** T-F3.3

### T-F3.6: Lifespan verification hook
- **Definition:** On FastAPI startup, call `PartitionManager.verify_forward_coverage()`. Abort startup with clear message if coverage < 3 months.
- **Acceptance:** Startup logs coverage status. Test: forcibly detach 3 months of forward partitions and verify startup fails.
- **Effort:** 1 hour
- **Depends on:** T-F3.3

### T-F3.7: Partition pruning EXPLAIN tests
- **Definition:** Tests that issue representative queries and assert `EXPLAIN` plans show pruning. Representative queries:
  - `SELECT * FROM technique_compute WHERE chart_id = ? AND technique_family_id = 'yoga'` → 1 leaf partition
  - `SELECT * FROM technique_compute WHERE chart_id = ?` → 16 leaf partitions (HASH pruning within each LIST)
  - `SELECT * FROM aggregation_event WHERE computed_at >= '2026-04-01' AND computed_at < '2026-05-01' AND chart_id = ?` → 1 monthly partition
- **Acceptance:** Parsing `EXPLAIN (FORMAT JSON)` output confirms partition counts per query. Tests run in CI on seed data.
- **Effort:** 4 hours
- **Depends on:** T-F3.1

### T-F3.8: Update F2 SQLModel classes for amended PKs
- **Definition:** `technique_compute` gains `technique_family_id` in composite PK; `aggregation_event` gains `computed_at` in composite PK. Update SQLModel field metadata.
- **Acceptance:** Type hints are correct; inserts via ORM succeed with amended PKs; unit tests from F2 continue to pass.
- **Effort:** 2 hours
- **Depends on:** T-F3.1

### T-F3.9: Cloud SQL pg_partman availability verification
- **Definition:** Verify `pg_partman` extension is whitelisted on Cloud SQL PG17 for both `josiam-dev` and `josiam-prod` instances. Document enablement flag (`cloudsql.enable_pg_partman` if applicable). If not enabled, file a Cloud Build or gcloud task.
- **Acceptance:** `SELECT * FROM pg_available_extensions WHERE name = 'pg_partman'` returns a row in both environments. Extension creates successfully in dev.
- **Effort:** 2 hours
- **Depends on:** none (pre-work)

## 8. Unit Tests

### 8.1 Partition helpers

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_aggregation_partition_name_format` | `datetime(2026, 4, 19, 12, 0, tzinfo=UTC)` | `"aggregation_event_y2026m04"` | naming convention stable |
| `test_aggregation_partition_name_single_digit_month` | `datetime(2026, 1, 5)` | `"aggregation_event_y2026m01"` | zero-padding correct |
| `test_month_bounds_utc` | `datetime(2026, 4, 19, 23, 59, tzinfo=UTC)` | `(2026-04-01T00Z, 2026-05-01T00Z)` | UTC-aligned boundaries |
| `test_month_bounds_dec_to_jan` | `datetime(2026, 12, 15)` | `(2026-12-01, 2027-01-01)` | year rollover |
| `test_partition_name_hypothesis` | Hypothesis: any datetime in [2000, 2050] | matches `^aggregation_event_y\d{4}m(0[1-9]\|1[0-2])$` | no off-by-one |

### 8.2 PartitionManager

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_status_lists_all_partitions` | fresh DB after migration | 16 families × 4 hash buckets + defaults + 12 monthly partitions | full inventory |
| `test_verify_forward_coverage_passes_on_migrated_db` | DB with 6 months forward | returns True | happy path |
| `test_verify_forward_coverage_fails_on_stripped_partitions` | drop 4 months of forward partitions | returns False | degraded state detected |
| `test_ensure_forward_partitions_creates_missing` | drop next-month partition; call ensure | partition recreated with correct bounds | fallback works |
| `test_ensure_forward_partitions_is_idempotent` | call twice | no errors, no duplicate partitions | safe to re-run |
| `test_run_pg_partman_maintenance_calls_proc` | mock pg_partman proc | SQL `CALL partman.run_maintenance_proc(...)` executed | delegation verified |

### 8.3 Partition pruning

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_prune_single_leaf_on_chart_and_family` | `WHERE chart_id=? AND technique_family_id='yoga'` | `EXPLAIN` shows 1 leaf partition scanned | full LIST+HASH pruning |
| `test_prune_hash_only_when_family_missing` | `WHERE chart_id=?` | `EXPLAIN` shows 17 partitions (16 families × 1 hash each + default) | HASH prunes within each LIST |
| `test_prune_monthly_range` | `WHERE computed_at >= '2026-04-01' AND computed_at < '2026-05-01'` | `EXPLAIN` shows 1 monthly partition scanned | RANGE pruning |
| `test_prune_disabled_when_function_on_partition_key` | `WHERE date_trunc('month', computed_at) = '2026-04-01'` | `EXPLAIN` shows all partitions scanned | documents anti-pattern |

### 8.4 Composite FK on partitioned table

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_compute_fk_enforced_on_partitioned_table` | insert compute row with (rule_id, source_id, rule_version) not in classical_rule | IntegrityError | PG14+ FK on partitioned table works |
| `test_compute_insert_routes_to_correct_partition` | insert yoga row | row visible in `technique_compute_yoga_hN` for the chart_id's hash | routing correct |
| `test_compute_insert_unknown_family_goes_to_default` | insert with family 'unknown' (seeded) | row lands in `technique_compute_default_hN` | default catches surprises |

### 8.5 Aggregation event range partitioning

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_event_insert_current_month` | insert with `computed_at = now()` | row in current-month partition | routing works |
| `test_event_insert_past_month_partition_exists` | insert 3 months ago | row in correct historical partition | retention / back-dated data |
| `test_event_insert_outside_range_hits_default` | insert 10 years in future (no partition) | row in `aggregation_event_default` | no data loss |
| `test_event_pk_includes_computed_at` | attempt PK = (id only) via ORM | rejected at schema validation | PK amendment enforced |

### 8.6 Migration roundtrip

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_migration_upgrade_from_f2` | DB at F2 revision | upgrade head succeeds; partitioned tables replace unpartitioned | forward migration works |
| `test_migration_downgrade_to_f2` | DB at F3 revision | downgrade -1 drops partitioned tables and recreates F2 shape | rollback works |
| `test_migration_idempotent_no_data_loss_empty_db` | apply F3 on empty DB | no errors; 0 rows in all partitions | empty-table swap safe |

## 9. EPIC-Level Acceptance Criteria

- [ ] `technique_compute` is partitioned: `PARTITION BY LIST (technique_family_id)` with 16 LIST partitions + 1 DEFAULT, each HASH-subpartitioned into 4 buckets (65 leaf partitions total)
- [ ] `aggregation_event` is partitioned: `PARTITION BY RANGE (computed_at)` with 12 monthly partitions seeded + 1 DEFAULT
- [ ] `pg_partman` extension installed in Cloud SQL PG17 (dev + prod) and configured with `premake=6` for `aggregation_event`
- [ ] Daily `run_maintenance_proc()` scheduled and observable (logs + alert on failure)
- [ ] Startup lifespan check verifies ≥3 months forward coverage; aborts startup on failure
- [ ] Representative queries show partition pruning in `EXPLAIN`:
  - `(chart_id, technique_family_id)` → 1 leaf partition
  - Monthly range on `computed_at` → 1 monthly partition
- [ ] Composite FK from `technique_compute` → `classical_rule` works on the partitioned table (PG14+)
- [ ] Amended PKs include partition keys (`technique_family_id` in `technique_compute` PK; `computed_at` in `aggregation_event` PK)
- [ ] Alembic migration upgrades from F2 and downgrades cleanly on an empty DB
- [ ] Integration test hits the full path (insert routes correctly, FK enforced, pruning verified)
- [ ] Unit test coverage ≥ 90% for `PartitionManager` and partition helpers
- [ ] Documentation updated: `CLAUDE.md` adds "Always filter by `technique_family_id` and `chart_id` on `technique_compute`; always filter by `computed_at` range on `aggregation_event`"
- [ ] ADR authored at `docs/markdown/adr/partitioning-query-requirements.md`

## 10. Rollout Plan

- **Feature flag:** none — P0 foundation; tables are empty on first deploy so partitioning is free to apply unconditionally.
- **Shadow compute:** N/A.
- **Backfill strategy:** N/A (empty tables). If rollout slips past the point where rows exist, backfill becomes a 24-hour migration via `pg_partman.partition_data_time`.
- **Rollback plan:** `alembic downgrade -1` drops partitioned structure and recreates F2 tables. Safe at P0 (empty). In production with data, rollback is NOT supported — we would roll forward with a fix rather than downgrade.

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| `pg_partman` unavailable in production Cloud SQL after all | Low | Medium | T-F3.9 verifies availability early; PartitionManager fallback path tested |
| Engineer writes query without `technique_family_id` and scans all 64 partitions | Medium | Medium | ADR + lint rule + query-builder helper that requires the predicate |
| Default partition accumulates rows silently (bug) | Medium | Medium | Alert on `row_count(technique_compute_default) > 0` |
| Forward partition coverage lapses (pg_partman job fails) | Medium | High | Startup lifespan check + monitoring + alert at 48 hours stale |
| HASH bucket count of 4 becomes inadequate at P4 scale | High (at scale) | Medium | Documented migration path to 8/16; SLA: revisit when any family partition > 50M rows |
| Alembic hand-crafted DDL diverges from SQLModel expectations | Medium | Medium | T-F3.8 keeps ORM models in sync; migration roundtrip test in CI |
| Index propagation from parent to partitions fails on PG version mismatch | Low | High | CI matrix includes PG17; fail fast if PG version < 14 |
| `DETACH PARTITION` during live traffic takes ACCESS EXCLUSIVE lock | Medium | Medium | Use `DETACH PARTITION CONCURRENTLY` (PG14+); never run during peak |
| pg_cron unavailable; beat scheduler down drops partition creation | Low | High | Dual schedule: pg_partman maintenance also invoked on startup; two independent failure paths |

## 12. References

- Master spec: [`docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`](../../../superpowers/specs/2026-04-19-classical-techniques-expansion-design.md)
- Related PRDs: [F1](./F1-star-schema-dimensions.md), [F2](./F2-fact-tables.md), F9 (chart_reading_view), S2/S4/S7 (later scaling)
- PostgreSQL declarative partitioning: https://www.postgresql.org/docs/17/ddl-partitioning.html
- pg_partman: https://github.com/pgpartman/pg_partman
- Cloud SQL for PostgreSQL extensions: https://cloud.google.com/sql/docs/postgres/extensions
- ADR to author: `docs/markdown/adr/partitioning-query-requirements.md`
