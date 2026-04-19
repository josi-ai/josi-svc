---
prd_id: F9
epic_id: F9
title: "chart_reading_view — regular table, incrementally maintained serving mart for AI tool-use"
phase: P0-foundation
tags: [#performance, #ai-chat, #correctness]
priority: must
depends_on: [F2, F8]
enables: [F10, F11, E11a, E12, E13]
classical_sources: []
estimated_effort: 4-5 days
status: draft
author: @agent
last_updated: 2026-04-19
---

# F9 — chart_reading_view (Regular Table, Worker-Maintained Serving Mart)

## 1. Purpose & Rationale

The AI chat backend needs a **single-query, sub-20ms read** that returns the complete current-state picture of a chart: active yogas, current dasa periods across all systems, transit highlights, tajaka summary, jaimini summary, ashtakavarga summary, western summary, chinese summary. Fetching these by joining raw `technique_compute` and `aggregation_event` per turn would cost 5–15 queries and hundreds of milliseconds — unacceptable for the tool-use loop in F10, and devastating when an LLM issues 3–8 tool calls per user turn.

The obvious solution — a PostgreSQL `MATERIALIZED VIEW` — **does not scale**:
- `REFRESH MATERIALIZED VIEW CONCURRENTLY` rebuilds the entire MV, which at 10M+ charts is minute-to-hour scale.
- Partial refresh requires `REFRESH ... CONCURRENTLY` per-chart workarounds that Postgres doesn't natively support.
- Freshness window becomes coupled to refresh cadence.

Instead, we model the view as a **regular table** updated **incrementally** by a background worker (`ReadingViewWorker`) that listens to `aggregation_event` inserts (the append-only log from F8) and upserts the affected JSONB key on the affected chart's row. This yields:

- **O(1) per-event update cost** regardless of total chart count.
- **Freshness SLA ≤ 30s** (target ≤ 10s) from aggregation_event insert to chart_reading_view row update.
- **Linear storage** (one row per chart, 2–5 KB each).

This PRD specifies the table, the worker, idempotency, freshness guarantees, multi-tenancy, schema-versioning strategy, and lazy initialization.

## 2. Scope

### 2.1 In scope
- `chart_reading_view` table (regular table, not MATERIALIZED VIEW)
- `ReadingViewWorker` service that consumes `aggregation_event` inserts
- LISTEN/NOTIFY pathway (preferred) + periodic-poll fallback
- Per-technique-family JSONB key writers (active_yogas, current_dasas, transit_highlights, tajaka_summary, jaimini_summary, ashtakavarga_summary, western_summary, chinese_summary)
- Idempotency via `last_aggregation_event_id` watermark
- Lazy init: row created on first aggregation_event per chart
- Schema `version` column + backfill script when bumped
- GIN index on `active_yogas` for "find charts with yoga X" analytics
- Multi-tenant isolation via `organization_id`
- Alembic migration
- Unit tests + integration tests for worker behavior

### 2.2 Out of scope
- Redis L1 cache on top of this table (S3)
- Cross-region replication of this table (S7)
- GraphQL surface for this table (consumed only by F10 tools)
- Full-text search over JSONB content (D6)

### 2.3 Dependencies
- F2 (`aggregation_event` table exists and is append-only)
- F8 (`AggregationStrategy` Protocol produces aggregation events)
- `AstrologyChart` model with `chart_id` UUID PK
- `Organization` model for tenant FK
- Postgres 14+ (for `NOTIFY` payloads up to 8000 bytes; we use only small payloads)

## 3. Technical Research

### 3.1 Why not MATERIALIZED VIEW

| Property | MATERIALIZED VIEW | chart_reading_view (this PRD) |
|---|---|---|
| Partial refresh | Not natively supported | Per-row upsert |
| Refresh cost at 100M rows | Minutes to hours | Constant per event |
| Freshness coupling | To refresh cadence | To event arrival (≤ 10–30s) |
| Concurrent reads during refresh | Requires `CONCURRENTLY` (full rebuild still) | Plain MVCC; no downtime |
| Schema migration | Drop + rebuild | Standard ALTER + lazy recompute |

### 3.2 Update mechanism: LISTEN/NOTIFY vs polling

**Preferred: LISTEN/NOTIFY.** On `aggregation_event` insert, a `BEFORE INSERT` trigger calls `pg_notify('aggregation_event_inserted', event_id::text)`. The worker holds a persistent asyncpg connection issuing `LISTEN aggregation_event_inserted`, then processes events one-by-one.

**Fallback: periodic poll.** The worker keeps a watermark (max `aggregation_event.id` last processed, stored in `reading_view_worker_state`) and polls every 2s for rows with `id > watermark`. This fires if NOTIFY misses (connection drop, payload overflow, crash recovery).

We run **both simultaneously**: NOTIFY for latency; poll for correctness. This is the "belt and suspenders" pattern adopted by listen_notify + workers in production systems (procrastinate, PgQ, Hasura event triggers).

### 3.3 Idempotency model

Every chart_reading_view row carries `last_aggregation_event_id` (UUID). Before applying an event, worker asserts:

```sql
UPDATE chart_reading_view
SET active_yogas = $new_yogas,
    last_aggregation_event_id = $event_id,
    last_computed_at = now()
WHERE chart_id = $chart_id
  AND (last_aggregation_event_id IS NULL
       OR last_aggregation_event_id < $event_id)  -- UUID v7 timestamp-ordered
```

(We use **UUID v7** for `aggregation_event.id` so that IDs are monotonic-ish by time, making `<` ordering meaningful.)

If an event has already been applied (UUID < watermark), the UPDATE is a no-op. This means **re-delivery is safe**; restarts and dual-worker runs are also safe.

### 3.4 Lazy init

The view row does **not** exist until the first `aggregation_event` fires for a chart. On first event, worker issues:

```sql
INSERT INTO chart_reading_view (chart_id, organization_id, last_aggregation_event_id, last_computed_at)
VALUES ($chart_id, $organization_id, $event_id, now())
ON CONFLICT (chart_id) DO UPDATE SET ... ;
```

Benefit: no backfill needed on first deploy. The view builds itself as charts are computed.

### 3.5 Per-family writer design

The `aggregation_event.technique_family_id` determines **which JSONB column** gets updated. Mapping:

| technique_family_id | JSONB column |
|---|---|
| `yoga` | `active_yogas` |
| `dasa` | `current_dasas` |
| `transit_event` | `transit_highlights` |
| `tajaka` | `tajaka_summary` |
| `jaimini` | `jaimini_summary` |
| `ashtakavarga` | `ashtakavarga_summary` |
| `western_lot`, `western_fixed_star`, `western_harmonic`, `western_eclipse`, `western_uranian` | `western_summary` (merged; sub-keys by sub-family) |
| `bazi`, `chinese_qimen` (future) | `chinese_summary` |

Each writer is a pure function `(chart_id, event_id) -> JSONB`. It queries the **most recent `aggregation_event`** for that chart+family where `strategy_id = chart_strategy` and writes the event's `output` JSONB directly (or a compressed projection — see 3.6).

### 3.6 JSONB payload shape per column

**`active_yogas`** (array):
```json
[
  {
    "yoga_id": "raja.gaja_kesari",
    "display_name": "Gaja Kesari Yoga",
    "active": true,
    "strength": 0.82,
    "source_id": "bphs",
    "citation": "BPHS Ch.36 v.14-16",
    "confidence": 0.9,
    "cross_source_agreement": "4/5"
  }
]
```

**`current_dasas`** (object keyed by system):
```json
{
  "vimshottari": {
    "mahadasa": {"lord": "jupiter", "start": "2020-03-14", "end": "2036-03-14"},
    "antardasa": {"lord": "saturn", "start": "2025-11-02", "end": "2028-05-14"},
    "pratyantardasa": {"lord": "mercury", "start": "2026-03-01", "end": "2026-07-20"}
  },
  "yogini": { ... },
  "ashtottari": { ... }
}
```

**`transit_highlights`**:
```json
{
  "sade_sati": {"active": true, "phase": "peak", "ends": "2027-05-10"},
  "major_transits": [
    {"planet": "jupiter", "event": "sign_change", "to_sign": "taurus", "at": "2026-05-14"}
  ]
}
```

Each of the remaining summaries (`tajaka_summary`, `jaimini_summary`, `ashtakavarga_summary`, `western_summary`, `chinese_summary`) follows its family's `output_shape` (F7), projected for read efficiency.

### 3.7 Freshness SLA

- **Target:** P50 < 5s, P95 < 10s, P99 < 30s from `aggregation_event INSERT` → `chart_reading_view` row reflects the new data.
- **SLO alert:** P99 > 60s for > 5 min = page on-call.
- **Measurement:** worker emits `reading_view.apply_latency_ms` histogram; computed as `now() - aggregation_event.computed_at` at apply time.

### 3.8 Alternatives considered

| Alternative | Rejected because |
|---|---|
| MATERIALIZED VIEW with periodic REFRESH | Can't scale past ~1M charts without minutes-long refresh |
| Per-chart triggers writing directly to reading_view | Adds write-path latency to compute engines; couples compute and serving |
| Redis-only serving cache (no table) | Loses durability; rebuilding cache on cold-start requires re-aggregation of 10M charts |
| Kafka/event-stream topology | Overkill at P0; requires separate infra; revisit at P4 (S4) |
| Per-technique-family tables (split reading view) | AI tool-use needs joined picture; single-row read is the point |

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| MATERIALIZED VIEW vs regular table | Regular table | Incremental update; unbounded scale |
| NOTIFY-only vs poll-only vs both | Both | NOTIFY for latency, poll for correctness/crash-recovery |
| Watermark granularity: per-chart or global | Per-chart (`last_aggregation_event_id`) | Allows out-of-order events per chart to be handled correctly |
| UUID version for aggregation_event.id | UUID v7 (time-ordered) | Enables `<` comparison for idempotency watermark |
| Where does strategy selection come from | Derived from `chart_reading_view.strategy_applied` (default `D_hybrid`) | View stores which strategy was applied so updates are consistent |
| Soft-delete semantics | Not applicable — when chart is soft-deleted, view row is deleted via CASCADE | No need to preserve reading view for deleted charts |
| Multi-tenancy | `organization_id` column + filter in every query | Same as all tenant tables (matches F2 convention) |
| Backfill on schema version bump | Background job processes all charts in batches of 1000 | Versioning is rare; one-off cost acceptable |
| Concurrency between multiple workers | Allowed; idempotency via watermark ensures correctness | Supports horizontal scale |

## 5. Component Design

### 5.1 New modules

```
src/josi/models/classical/
└── chart_reading_view.py           # SQLModel class

src/josi/services/classical/
├── reading_view_worker.py          # ReadingViewWorker (LISTEN + poll)
├── reading_view_writers.py         # per-family JSONB projections
└── reading_view_state.py           # worker state persistence

src/josi/repositories/
└── chart_reading_view_repo.py      # tenant-aware reads

src/josi/db/seeds/classical/
└── reading_view_writers.yaml       # family_id → writer_class map (optional)
```

### 5.2 Data model

```sql
CREATE TABLE chart_reading_view (
    chart_id                    UUID PRIMARY KEY REFERENCES astrology_chart(chart_id) ON DELETE CASCADE,
    organization_id             UUID NOT NULL REFERENCES organization(organization_id),
    active_yogas                JSONB NOT NULL DEFAULT '[]'::jsonb,
    current_dasas               JSONB NOT NULL DEFAULT '{}'::jsonb,
    transit_highlights          JSONB NOT NULL DEFAULT '{}'::jsonb,
    tajaka_summary              JSONB,
    jaimini_summary             JSONB,
    ashtakavarga_summary        JSONB,
    western_summary             JSONB,
    chinese_summary             JSONB,
    astrologer_preference_key   TEXT,                                -- FK-ish to astrologer_source_preference
    strategy_applied            TEXT NOT NULL DEFAULT 'D_hybrid'
                                REFERENCES aggregation_strategy(strategy_id),
    last_computed_at            TIMESTAMPTZ,
    last_aggregation_event_id   UUID,
    version                     INTEGER NOT NULL DEFAULT 1,          -- schema-version; bumped → triggers backfill
    created_at                  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at                  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_reading_view_org ON chart_reading_view(organization_id);
CREATE INDEX idx_reading_view_last_computed ON chart_reading_view(last_computed_at DESC NULLS LAST);
CREATE INDEX idx_reading_view_version ON chart_reading_view(version);

-- GIN index for "find charts with yoga X" analytics / similarity
CREATE INDEX idx_reading_view_active_yogas_gin
    ON chart_reading_view USING GIN (active_yogas jsonb_path_ops);

-- Worker state table
CREATE TABLE reading_view_worker_state (
    worker_id        TEXT PRIMARY KEY,         -- 'reading_view_worker' singleton, or per-shard id
    last_processed_event_id UUID,
    last_processed_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    heartbeat_at            TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Trigger on aggregation_event to NOTIFY
CREATE OR REPLACE FUNCTION notify_aggregation_event() RETURNS trigger AS $$
BEGIN
    PERFORM pg_notify('aggregation_event_inserted',
        json_build_object(
            'event_id', NEW.id,
            'chart_id', NEW.chart_id,
            'technique_family_id', NEW.technique_family_id,
            'organization_id', NEW.organization_id
        )::text);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_notify_aggregation_event
    AFTER INSERT ON aggregation_event
    FOR EACH ROW EXECUTE FUNCTION notify_aggregation_event();
```

### 5.3 Worker interface

```python
# src/josi/services/classical/reading_view_worker.py

from asyncio import Queue, create_task, gather
from uuid import UUID
from josi.db.async_db import EngineManager

class ReadingViewWorker:
    """
    Listens on Postgres NOTIFY and (concurrently) polls aggregation_event for
    new rows. For each event, updates the relevant JSONB key of the affected
    chart's chart_reading_view row. Idempotent via last_aggregation_event_id.
    """

    def __init__(
        self,
        engine_mgr: EngineManager,
        worker_id: str = "reading_view_worker",
        poll_interval_sec: float = 2.0,
        batch_size: int = 100,
    ): ...

    async def start(self) -> None:
        """Launch NOTIFY listener + poll loop as background tasks."""
        await gather(self._listen_loop(), self._poll_loop(), self._heartbeat_loop())

    async def _listen_loop(self) -> None:
        """LISTEN on aggregation_event_inserted; enqueue events."""
        ...

    async def _poll_loop(self) -> None:
        """Every poll_interval_sec, SELECT events where id > watermark."""
        ...

    async def _apply_event(self, event: AggregationEvent) -> None:
        """
        1. Look up writer for event.technique_family_id.
        2. Compute new JSONB projection.
        3. Upsert chart_reading_view row with idempotency guard.
        """
        ...

    async def stop(self) -> None: ...
```

### 5.4 Per-family writer interface

```python
# src/josi/services/classical/reading_view_writers.py

from typing import Protocol
from sqlalchemy.ext.asyncio import AsyncSession

class ReadingViewWriter(Protocol):
    """Produces a JSONB projection for a single (chart, technique_family) pair."""

    technique_family_id: str
    target_column: str  # e.g., 'active_yogas'

    async def project(
        self,
        session: AsyncSession,
        chart_id: UUID,
        strategy_id: str,
    ) -> dict | list | None: ...


class YogaReadingViewWriter:
    technique_family_id = "yoga"
    target_column = "active_yogas"

    async def project(self, session, chart_id, strategy_id):
        # Query latest aggregation_event per yoga rule for this chart
        # Filter to active=True; project to compact array shape.
        ...

# Similar for Dasa, TransitEvent, Tajaka, Jaimini, Ashtakavarga, Western*, Chinese.

WRITER_REGISTRY: dict[str, ReadingViewWriter] = {
    "yoga": YogaReadingViewWriter(),
    "dasa": DasaReadingViewWriter(),
    "transit_event": TransitEventReadingViewWriter(),
    "tajaka": TajakaReadingViewWriter(),
    "jaimini": JaiminiReadingViewWriter(),
    "ashtakavarga": AshtakavargaReadingViewWriter(),
    # Western families collapsed into one writer that keys into western_summary
    "western_lot": WesternReadingViewWriter(sub_key="lots"),
    "western_fixed_star": WesternReadingViewWriter(sub_key="fixed_stars"),
    "western_harmonic": WesternReadingViewWriter(sub_key="harmonics"),
    "western_eclipse": WesternReadingViewWriter(sub_key="eclipses"),
    "western_uranian": WesternReadingViewWriter(sub_key="uranian"),
}
```

### 5.5 Tenant-aware repository read path

```python
# src/josi/repositories/chart_reading_view_repo.py

class ChartReadingViewRepository:
    async def get_by_chart_id(
        self,
        chart_id: UUID,
        organization_id: UUID,
    ) -> ChartReadingView | None:
        """PK lookup + tenant guard. Returns None if row not yet initialized."""
        ...

    async def find_charts_with_yoga(
        self,
        organization_id: UUID,
        yoga_id: str,
        limit: int = 100,
    ) -> list[UUID]:
        """Uses GIN index on active_yogas."""
        ...
```

## 6. User Stories

### US-F9.1: As the AI chat backend, I want a single-row read that returns the complete reading context for a chart
**Acceptance:** `SELECT * FROM chart_reading_view WHERE chart_id = $1 AND organization_id = $2` returns in P99 < 5ms.

### US-F9.2: As a classical engine, I can insert an aggregation_event and trust that the reading view reflects it within 30 seconds
**Acceptance:** given an `aggregation_event` insert at time T, the corresponding `chart_reading_view` column reflects the new output by T+30s in all test runs (P99).

### US-F9.3: As an operator, duplicate or replayed aggregation_event inserts do not corrupt the reading view
**Acceptance:** re-inserting the same event (same id) leaves the view row unchanged; applying an older event (lower UUID v7) does not overwrite a newer one.

### US-F9.4: As an analyst, I can find all charts that have a given yoga active
**Acceptance:** `SELECT chart_id FROM chart_reading_view WHERE active_yogas @> '[{"yoga_id":"raja.gaja_kesari"}]'` uses the GIN index and returns in P99 < 200ms at 10M rows.

### US-F9.5: As the system, a chart with no aggregation events yet has no reading view row (not an all-nulls row)
**Acceptance:** querying `chart_reading_view` for an uncomputed chart returns 0 rows; API layer interprets this as "computing".

### US-F9.6: As an engineer, bumping `version` triggers a controlled backfill of all existing rows without downtime
**Acceptance:** a script reads all rows with `version < CURRENT_VERSION`, re-runs writers, upserts; serving reads remain unaffected.

## 7. Tasks

### T-F9.1: SQLModel class + migration
- **Definition:** `ChartReadingView` SQLModel; Alembic migration for table, indexes, worker-state table, trigger.
- **Acceptance:** `alembic upgrade head` creates objects; `alembic downgrade -1` cleanly reverts; GIN index confirmed via `\di+` in psql.
- **Effort:** 4 hours
- **Depends on:** F2 complete

### T-F9.2: NOTIFY trigger + asyncpg LISTEN integration
- **Definition:** Postgres trigger on `aggregation_event` emitting `pg_notify`. asyncpg connection with `add_listener()` in worker.
- **Acceptance:** inserting an aggregation_event causes the worker's listener callback to fire within 1s.
- **Effort:** 4 hours
- **Depends on:** T-F9.1

### T-F9.3: Poll loop
- **Definition:** Async loop that every 2s `SELECT * FROM aggregation_event WHERE id > $watermark ORDER BY id LIMIT 100`.
- **Acceptance:** worker catches events even if NOTIFY is disabled; watermark advances monotonically in `reading_view_worker_state`.
- **Effort:** 4 hours
- **Depends on:** T-F9.1

### T-F9.4: Writer registry + initial writers (yoga, dasa, transit_event)
- **Definition:** `ReadingViewWriter` protocol + 3 concrete writers producing compact JSONB projections.
- **Acceptance:** Each writer takes `(chart_id, strategy_id)` and returns the expected JSON shape given fixture `aggregation_event` rows.
- **Effort:** 1 day
- **Depends on:** T-F9.1

### T-F9.5: Remaining writers (tajaka, jaimini, ashtakavarga, western family, chinese)
- **Definition:** 5 more writers completing the registry.
- **Acceptance:** Fixture-driven tests pass for each.
- **Effort:** 1 day
- **Depends on:** T-F9.4

### T-F9.6: Idempotent upsert with watermark guard
- **Definition:** `_apply_event` issues UPDATE with `WHERE last_aggregation_event_id IS NULL OR last_aggregation_event_id < $new_id`; lazy INSERT on first event.
- **Acceptance:** re-delivering event is a no-op; old events do not clobber newer state.
- **Effort:** 3 hours
- **Depends on:** T-F9.4

### T-F9.7: Repository + freshness metric
- **Definition:** `ChartReadingViewRepository.get_by_chart_id` + `find_charts_with_yoga` + Prometheus histogram `reading_view_apply_latency_seconds`.
- **Acceptance:** metric visible on `/metrics`; tenant filter applied by default.
- **Effort:** 4 hours
- **Depends on:** T-F9.1, T-F9.6

### T-F9.8: Backfill CLI (schema-version bump)
- **Definition:** `python -m josi.cli backfill-reading-view --target-version 2` script processes rows with `version < target` in batches.
- **Acceptance:** runs against dev DB; progress logged; idempotent on retry.
- **Effort:** 4 hours
- **Depends on:** T-F9.6

### T-F9.9: Integration tests (end-to-end)
- **Definition:** Full path: compute engine → aggregation_event → NOTIFY → worker → reading view row.
- **Acceptance:** freshness P99 < 1s in test env; tenant isolation confirmed; idempotency confirmed.
- **Effort:** 1 day
- **Depends on:** T-F9.2, T-F9.3, T-F9.6

### T-F9.10: Lifespan wiring + healthcheck
- **Definition:** Worker launched from FastAPI lifespan; `/health` reports worker heartbeat age.
- **Acceptance:** stale heartbeat (> 30s) surfaces in `/health` as degraded.
- **Effort:** 2 hours
- **Depends on:** T-F9.9

## 8. Unit Tests

### 8.1 ChartReadingView model

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_pk_is_chart_id` | insert two rows with same `chart_id` | second raises `IntegrityError` | PK contract |
| `test_cascade_delete_from_chart` | delete parent `astrology_chart` row | reading view row deleted | ON DELETE CASCADE correct |
| `test_default_active_yogas_empty_array` | insert without `active_yogas` | value is `[]::jsonb` | default applied |
| `test_strategy_applied_fk_enforced` | insert with `strategy_applied='made_up'` | `IntegrityError` | FK to aggregation_strategy |
| `test_gin_index_usable` | `EXPLAIN` on `active_yogas @> '[{"yoga_id":"x"}]'` | uses `idx_reading_view_active_yogas_gin` | index tuning |

### 8.2 ReadingViewWorker — NOTIFY path

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_notify_fires_on_insert` | insert aggregation_event | worker's listener invoked within 1s | trigger + LISTEN wired correctly |
| `test_notify_payload_contains_event_id` | insert event with id=X | listener callback receives payload JSON with `event_id=X` | payload shape correct |
| `test_notify_listener_reconnects_on_drop` | kill connection, reinsert event | worker reconnects and processes missed event (via poll catch-up) | resilience |

### 8.3 ReadingViewWorker — poll path

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_poll_catches_up_from_watermark` | insert 5 events while worker offline; start worker | worker processes all 5 within first poll cycle | poll correctness |
| `test_poll_advances_watermark` | process 3 events | `reading_view_worker_state.last_processed_event_id` = highest event id | watermark progress |
| `test_poll_respects_batch_size` | insert 500 events with batch_size=100 | processes in 5 batches, no loss | batching correctness |

### 8.4 Idempotency

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_apply_same_event_twice_is_noop` | apply event E to chart C; apply E again | row unchanged after second apply | idempotency contract |
| `test_older_event_does_not_overwrite_newer` | apply event E2 (newer), then deliver E1 (older) | row reflects E2; E1 apply is no-op | out-of-order safety |
| `test_lazy_insert_on_first_event` | no existing row; apply event | row created with event's projection | lazy init |
| `test_concurrent_workers_idempotent` | 2 workers processing overlapping events | final state consistent, no double-apply artifacts | horizontal scale safety |

### 8.5 Per-family writers

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_yoga_writer_projects_active_only` | 5 yoga events (3 active, 2 inactive) | `active_yogas` contains only 3 | writer filters inactive |
| `test_yoga_writer_includes_citation` | event with `source_id='bphs'` and citation | projected row includes citation string | citation carried through |
| `test_dasa_writer_nests_by_system` | vimshottari + yogini events | `current_dasas` has keys `vimshottari`, `yogini` | multi-system nesting |
| `test_transit_writer_projects_sade_sati` | sade_sati event with phase='peak' | `transit_highlights.sade_sati.phase == 'peak'` | transit shape |
| `test_western_writer_keys_by_sub_family` | western_lot event + western_fixed_star event | `western_summary.lots` and `western_summary.fixed_stars` populated | western sub-keying |

### 8.6 Multi-tenant isolation

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_get_by_chart_wrong_org_returns_none` | chart in org A; query with org B | returns None | tenant guard |
| `test_find_charts_with_yoga_filters_by_org` | matching chart in org A, matching chart in org B, query with org A | only org A chart returned | tenant filter on analytics |

### 8.7 Freshness SLA

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_freshness_under_1s_in_test_env` | insert 100 events, measure apply latency | P99 < 1s (NOTIFY fast path) | SLA baseline |
| `test_freshness_under_30s_poll_only` | disable NOTIFY; insert 100 events | P99 < 30s | fallback path honors SLA |

### 8.8 Schema version backfill

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_backfill_processes_only_stale_version` | 100 rows with v=1 and v=2; run with target v=2 | only v=1 rows updated | targeted backfill |
| `test_backfill_idempotent_on_retry` | run twice | second run is no-op | retry safety |

## 9. EPIC-Level Acceptance Criteria

- [ ] `chart_reading_view` table exists with exact schema, indexes (including GIN), FKs, and defaults
- [ ] Worker starts on FastAPI lifespan; visible in `/health` with heartbeat
- [ ] LISTEN/NOTIFY trigger fires on every `aggregation_event` insert
- [ ] Poll loop advances watermark monotonically and catches events missed by NOTIFY
- [ ] All 8 JSONB columns have a registered writer
- [ ] Idempotency watermark prevents duplicate/out-of-order event corruption
- [ ] Lazy init: uncomputed charts have no view row
- [ ] Multi-tenant isolation enforced in all repository reads
- [ ] Freshness SLA: P99 < 30s from aggregation_event insert → view row update, measured over 24h soak test
- [ ] Integration test hits the full path (compute → event → NOTIFY → worker → view row → API read)
- [ ] Unit test coverage ≥ 90% for worker, writers, repository
- [ ] Golden chart suite green for this module (no regressions from F8)
- [ ] Documentation updated in `CLAUDE.md` (new section: "Reading View Worker") and `docs/markdown/prd/INDEX.md`
- [ ] Backfill CLI tested on at least 10k rows in staging

## 10. Rollout Plan

- **Feature flag:** `READING_VIEW_WORKER_ENABLED` (default ON in P0 since no data exists yet; flag primarily protects against runaway worker in incidents).
- **Shadow compute:** N/A — view is the only source of truth for F10; no shadow comparison possible at P0.
- **Backfill strategy:** N/A at P0 (zero existing charts). Future version bumps use T-F9.8 CLI, batched 1000/txn, run as K8s job.
- **Rollback plan:** Disable feature flag (worker stops consuming events; no write). Existing view rows remain valid and readable; staleness accumulates until worker re-enabled. For schema-level rollback, `alembic downgrade -1` drops the table; tool-use path in F10 must gracefully degrade to direct-query fallback (documented in F10).

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| NOTIFY payload exceeds 8000-byte limit | Low | Medium | Payload only carries ids, not full event; poll path catches dropped NOTIFYs |
| Worker falls behind under event burst | Medium | High | Horizontal scale: multiple workers with partitioned event consumption (chart_id % N); alert when lag > 60s |
| JSONB row size grows > 16KB TOAST threshold for heavy charts | Medium | Medium | Projections are compact; periodic audit of row size P99; cap number of stored active yogas at 150 per chart |
| Watermark race on concurrent workers | Low | High | UUID v7 monotonicity + `last_aggregation_event_id <` guard; tested in `test_concurrent_workers_idempotent` |
| NOTIFY storm on bulk compute jobs (backfill) | Medium | Medium | Bulk jobs insert aggregation_event without triggering NOTIFY (use session variable `SET LOCAL josi.suppress_notify=true` checked in trigger); workers catch up via poll |
| Schema-version backfill runs out of DB connections | Low | Medium | Backfill CLI uses a dedicated connection pool with `max_connections=5` |
| GIN index bloat over time | Medium | Low | Monitor index size; `REINDEX CONCURRENTLY` monthly via maintenance job |
| Worker process dies silently | Medium | High | Heartbeat row in `reading_view_worker_state`; `/health` flags stale; systemd/K8s restart policy |

## 12. References

- Master spec: [`docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`](../../../superpowers/specs/2026-04-19-classical-techniques-expansion-design.md), §2.2 (serving mart), §3 (AI chat integration)
- F2 fact tables: [`F2-fact-tables.md`](./F2-fact-tables.md) — `aggregation_event` definition
- F8 aggregation protocol: [`F8-technique-result-aggregation-protocol.md`](./F8-technique-result-aggregation-protocol.md) — events are emitted here
- F10 tool-use contract: [`F10-typed-ai-tool-use-contract.md`](./F10-typed-ai-tool-use-contract.md) — primary consumer of this table
- Postgres LISTEN/NOTIFY reference: https://www.postgresql.org/docs/current/sql-notify.html
- UUID v7 spec: RFC 9562 §5.7
- Kimball, *The Data Warehouse Toolkit* Ch. 19 (real-time partitioning & drip-feed patterns)
