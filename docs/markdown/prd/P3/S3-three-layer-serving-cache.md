---
prd_id: S3
epic_id: S3
title: "Three-layer serving cache (Redis L1 + chart_reading_view L2 + fact tables L3)"
phase: P3-scale-10m
tags: [#performance, #ai-chat]
priority: must
depends_on: [F9, S2]
enables: [S6, AI5]
classical_sources: []
estimated_effort: 2 weeks
status: draft
author: Govind
last_updated: 2026-04-19
---

# S3 — Three-Layer Serving Cache

## 1. Purpose & Rationale

At 10M users, every AI chat turn fans out to 1–6 tool-use calls (`get_yoga_summary`, `get_current_dasa`, `get_transit_events`, `get_tajaka_summary`, `get_ashtakavarga_summary`, `find_similar_charts`). If each tool hits Postgres, we do 60M+ serving reads per day assuming 10M DAU × 1 chat session/day. Even with replicas (S2) and partitioned facts (F3), the point-query cost is 5–15ms at the 99th percentile; 6 tool calls per turn = 30–90ms of DB latency added to every LLM response, and 60M reads/day per replica stresses the hot path.

This PRD introduces a three-layer read hierarchy:

- **L1 — Redis** cache keyed by `(chart_id, technique_family_id, strategy_id)`. Target: sub-millisecond reads. 95%+ hit rate. 24h TTL.
- **L2 — `chart_reading_view`** table (already defined in F9). Denormalized JSONB per chart. Target: 2–5ms read. Covers L1 miss.
- **L3 — Fact tables** (`technique_compute`, `aggregation_event`). Target: 20–100ms. Covers L2 miss / compute trigger.

Read flow: **L1 → L2 → L3 → lazy compute** (S6). Write flow (invalidation): on `aggregation_event` insert, a Postgres `LISTEN/NOTIFY` channel triggers a worker that deletes affected L1 keys and bumps L2 `chart_reading_view` (F9 worker already does this).

## 2. Scope

### 2.1 In scope
- L1 Redis cache service: `ServingCache` with typed API per tool shape.
- Redis key schema (structured, versioned).
- Serialization: `orjson` + optional zstd for values > 2KB.
- TTL policy: 24h default, 15min for transit-event shapes (temporal freshness matters), 7d for yoga (stable).
- Invalidation worker: subscribes to `aggregation_event` NOTIFY channel, deletes matching L1 keys.
- Cache stampede protection via `SET NX` "in-flight" sentinel.
- Cloud Memorystore (Redis) sizing: **100 GB, Standard HA tier** for prod; **5 GB Basic** for dev.
- Eviction policy: `allkeys-lru`.
- Metrics: L1/L2/L3 hit rate, P50/P99 serving latency per layer, key count, memory used, eviction count.
- Cache warming hook: after a chart's lazy compute completes (S6), optionally pre-populate L1 for its top-6 families.
- Public cache headers on upstream API (`Cache-Control: private, max-age=60`) for CDN edge caching of the final tool-use response.

### 2.2 Out of scope
- CDN (Cloudflare/Fastly) configuration — Cloud Run already sits behind GCLB; L1 is our cache.
- Multi-region replication of Redis — P4 concern; single-region at P3.
- Vector search caching (Qdrant) — handled independently by Qdrant's own LRU.
- User-level caching (e.g., "`/me`" response) — separate PRD; not in serving hierarchy.
- Cache write-through semantics from compute path — compute path always writes to Postgres; L1 is populated on first read.

### 2.3 Dependencies
- F9 — `chart_reading_view` (the L2 layer) is the incrementally-updated table.
- S2 — read replicas route L2/L3 reads to replicas.
- Redis 7 on Cloud Memorystore; exists in dev via `docker-compose.yml` already.

## 3. Technical Research

### 3.1 Why three layers

A single cache (L1 → DB) is simpler but:
- L2 `chart_reading_view` is already precomputed per-chart for AI tool use (F9). It's a Postgres table, fast to read (2–5ms), and serves as a durable source of truth for L1.
- L1 Redis absorbs the hot set (active users' charts in the last 24h).
- L3 fact tables serve cold reads and anchor correctness.

This mirrors the classical pattern: L1 = RAM, L2 = SSD, L3 = disk — applied to data-serving.

### 3.2 Why Redis not in-process cache

Cloud Run autoscales to hundreds of instances. In-process caches duplicate per-instance and cold-start with zero hit rate. Redis is shared across instances; hit rate stays warm across deploys and scale events.

### 3.3 Size budget

Assumptions:
- 10M total charts, but only ~10% ("hot set") accessed in 24h = 1M charts.
- 6 technique families cached per chart (yoga, dasa, transit, tajaka, jaimini, ashtakavarga).
- Average serialized payload: ~5 KB per (chart, family). Some families larger (ashtakavarga matrix ~12 KB); others smaller (tajaka summary ~3 KB).
- 1M × 6 × 5 KB = **30 GB**, plus overhead and strategy fan-out = ~**50 GB**.

Cloud Memorystore **Standard 100 GB** tier gives headroom for growth + HA replica. LRU evicts cleanly at 90%+ utilization.

### 3.4 Hit-rate target: 95%+

Analysis:
- Chart re-read rate per session ~3× (chat turns reference same tool calls).
- Session frequency ~1/day for engaged users.
- 24h TTL aligns with session cadence.

If hit rate drops below 95% we investigate: too-short TTL, under-sized Redis, or invalidation storm.

### 3.5 Invalidation: NOTIFY/LISTEN vs polling vs outbox

| Approach | Pros | Cons | Decision |
|---|---|---|---|
| pg `LISTEN/NOTIFY` on `aggregation_event` insert | Sub-second latency; native; no extra infra | Delivered at-most-once; drops on listener reconnect | **Choose, with outbox fallback** |
| Outbox table + polling | Durable; survives worker restart | 1–5s latency; extra table | Use as **fallback** for missed NOTIFY |
| Debezium / CDC | Industrial-strength | Heavy infra; overkill at P3 | Reject |

Hybrid: NOTIFY for fast path + outbox for durability. Every `aggregation_event` insert writes a row to `cache_invalidation_outbox` and `pg_notify('cache_invalidate', ...)`. Worker processes NOTIFY events in real-time and additionally reads outbox every 30s to catch missed events. Outbox rows older than 5 min without processing are retried.

### 3.6 Stampede protection

When a popular chart's L1 key is evicted and 100 concurrent requests arrive, all 100 hit L2/L3. Mitigation: `SET key:lock NX EX 10` before compute; losers poll or fall through to L2 (which is only 2–5ms, acceptable).

### 3.7 Alternatives considered

| Alternative | Rejected because |
|---|---|
| Single Redis-only cache (skip L2) | F9 `chart_reading_view` already exists; 2nd-layer hits give correctness without recompute |
| Database `pg_prewarm` of `chart_reading_view` | Doesn't reduce per-query work; just keeps hot blocks in shared_buffers |
| Materialized views with triggers | Refresh storm on invalidation; `chart_reading_view` is a regular table for a reason |
| App-level per-process LRU (`functools.lru_cache`) | Per-instance, lost on scale events; no cross-instance sharing |

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| Key scheme | `jsc:v1:{chart_id}:{family}:{strategy}` | Versioned prefix for schema evolution |
| Value format | orjson → zstd when > 2 KB | Fast serialize; compress large payloads |
| TTL per family | 7d yoga, 24h dasa, 15min transit, 24h default | Aligned with volatility |
| Invalidation path | NOTIFY/LISTEN + outbox fallback | Sub-second + durable |
| Stampede handling | `SET NX` sentinel; fall through to L2 if contended | Simple, correct |
| Memory tier | prod = 100 GB Standard HA; dev = 5 GB Basic | 95th-percentile sizing |
| Eviction | `allkeys-lru` | Hot-set wins by access pattern |
| Cache-miss compute trigger | Caller responsibility (S6 lazy compute) | Cache has no opinion on how to fill |
| Redis connection limits | 1000 concurrent (Standard tier default) | PgBouncer-style pool not needed at this volume |
| Warming on lazy compute | Opt-in per family | Avoid warming for cold charts that never re-read |

## 5. Component Design

### 5.1 New modules

```
src/josi/services/cache/
├── __init__.py
├── serving_cache.py          # NEW: ServingCache with typed API
├── serialization.py          # NEW: orjson + zstd
├── invalidation.py           # NEW: InvalidationWorker (pg NOTIFY consumer)
├── stampede.py               # NEW: lock sentinel
└── metrics.py                # NEW: prometheus counters/histograms

src/josi/services/cache/handlers/
├── base.py                   # NEW: CacheHandler Protocol
├── yoga_handler.py
├── dasa_handler.py
├── transit_handler.py
├── tajaka_handler.py
├── jaimini_handler.py
└── ashtakavarga_handler.py

src/josi/workers/
└── cache_invalidation_worker.py  # NEW: long-running subscriber

src/alembic/versions/
└── {ts}_add_cache_invalidation_outbox.py
```

### 5.2 Data model additions

```sql
-- Outbox for durable invalidation fallback
CREATE TABLE cache_invalidation_outbox (
    id                  BIGSERIAL PRIMARY KEY,
    chart_id            UUID NOT NULL REFERENCES astrology_chart(chart_id),
    technique_family_id TEXT NOT NULL REFERENCES technique_family(family_id),
    strategy_id         TEXT,                    -- null = all strategies
    reason              TEXT NOT NULL,           -- 'aggregation_event' | 'rule_version_bump' | 'manual'
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    processed_at        TIMESTAMPTZ,
    retry_count         INT NOT NULL DEFAULT 0
);

CREATE INDEX idx_invalidation_unprocessed
    ON cache_invalidation_outbox(created_at)
    WHERE processed_at IS NULL;

-- Trigger: on aggregation_event insert, write outbox row + NOTIFY
CREATE OR REPLACE FUNCTION emit_cache_invalidation()
RETURNS trigger AS $$
BEGIN
    INSERT INTO cache_invalidation_outbox
        (chart_id, technique_family_id, strategy_id, reason)
    VALUES
        (NEW.chart_id, NEW.technique_family_id, NEW.strategy_id, 'aggregation_event');
    PERFORM pg_notify(
        'cache_invalidate',
        json_build_object(
            'chart_id',  NEW.chart_id,
            'family',    NEW.technique_family_id,
            'strategy',  NEW.strategy_id
        )::text
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_emit_cache_invalidation
    AFTER INSERT ON aggregation_event
    FOR EACH ROW EXECUTE FUNCTION emit_cache_invalidation();
```

### 5.3 ServingCache interface

```python
# src/josi/services/cache/serving_cache.py

from typing import Generic, TypeVar, Protocol
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

class CacheHandler(Protocol, Generic[T]):
    family_id: str
    ttl_seconds: int
    shape_cls: type[T]

    def serialize(self, value: T) -> bytes: ...
    def deserialize(self, raw: bytes) -> T: ...
    def l2_loader(
        self, session: AsyncSession, chart_id: UUID, strategy_id: str
    ) -> Awaitable[T | None]: ...

class ServingCache:
    """Three-layer cache: L1 Redis → L2 chart_reading_view → L3 compute."""

    def __init__(self, redis: Redis, handlers: dict[str, CacheHandler]):
        self._redis = redis
        self._handlers = handlers
        self._metrics = CacheMetrics()

    async def get(
        self,
        chart_id: UUID,
        family_id: str,
        strategy_id: str,
        session: AsyncSession,
    ) -> BaseModel | None:
        handler = self._handlers[family_id]
        key = self._key(chart_id, family_id, strategy_id)

        # L1
        raw = await self._redis.get(key)
        if raw is not None:
            self._metrics.hit("l1", family_id)
            return handler.deserialize(raw)
        self._metrics.miss("l1", family_id)

        # Stampede guard
        lock_key = f"{key}:lock"
        got_lock = await self._redis.set(lock_key, "1", nx=True, ex=10)
        if not got_lock:
            # another worker is populating; fall through to L2
            pass

        # L2
        value = await handler.l2_loader(session, chart_id, strategy_id)
        if value is not None:
            self._metrics.hit("l2", family_id)
            await self._redis.set(
                key, handler.serialize(value), ex=handler.ttl_seconds
            )
            if got_lock:
                await self._redis.delete(lock_key)
            return value
        self._metrics.miss("l2", family_id)

        # L3 compute trigger is caller's responsibility (S6 lazy compute)
        if got_lock:
            await self._redis.delete(lock_key)
        return None

    async def invalidate(
        self,
        chart_id: UUID,
        family_id: str | None = None,
        strategy_id: str | None = None,
    ) -> int:
        """Delete matching keys. None = wildcard."""
        pattern = self._pattern(chart_id, family_id, strategy_id)
        deleted = 0
        async for key in self._redis.scan_iter(match=pattern, count=500):
            await self._redis.delete(key)
            deleted += 1
        self._metrics.invalidated(family_id or "all", deleted)
        return deleted

    @staticmethod
    def _key(chart_id: UUID, family: str, strategy: str) -> str:
        return f"jsc:v1:{chart_id}:{family}:{strategy}"

    @staticmethod
    def _pattern(chart_id: UUID, family: str | None, strategy: str | None) -> str:
        return f"jsc:v1:{chart_id}:{family or '*'}:{strategy or '*'}"
```

### 5.4 TTL table (per family)

```python
# src/josi/services/cache/ttl_config.py
TTL_BY_FAMILY = {
    "yoga":          60 * 60 * 24 * 7,    # 7 days (stable)
    "dasa":          60 * 60 * 24,        # 24 h
    "transit_event": 60 * 15,             # 15 min (moving)
    "tajaka":        60 * 60 * 24,        # 24 h
    "jaimini":       60 * 60 * 24 * 7,
    "ashtakavarga":  60 * 60 * 24,
    "kp":            60 * 60 * 24,
    "prasna":        60 * 5,              # 5 min (question-time sensitive)
    "__default__":   60 * 60 * 24,
}
```

### 5.5 Serialization

```python
# src/josi/services/cache/serialization.py
import orjson, zstandard as zstd

_ZSTD_THRESHOLD = 2048
_MAGIC_ZSTD = b"\x28\xb5\x2f\xfd"
_compressor = zstd.ZstdCompressor(level=3)
_decompressor = zstd.ZstdDecompressor()

def serialize(value: BaseModel) -> bytes:
    raw = orjson.dumps(value.model_dump(mode="json"))
    if len(raw) > _ZSTD_THRESHOLD:
        return _compressor.compress(raw)
    return raw

def deserialize(raw: bytes, cls: type[T]) -> T:
    if raw[:4] == _MAGIC_ZSTD:
        raw = _decompressor.decompress(raw)
    return cls.model_validate_json(raw)
```

### 5.6 Invalidation worker

```python
# src/josi/workers/cache_invalidation_worker.py

class InvalidationWorker:
    """Two loops:
    - NOTIFY listener: sub-second; dequeues payloads and invalidates.
    - Outbox poller: 30-second interval; catches missed NOTIFYs.
    """

    async def run(self) -> None:
        await asyncio.gather(self._notify_loop(), self._outbox_loop())

    async def _notify_loop(self) -> None:
        async with asyncpg.connect(PRIMARY_DSN) as conn:
            await conn.add_listener("cache_invalidate", self._on_notify)
            while True:
                await asyncio.sleep(3600)  # keep connection alive

    async def _on_notify(self, conn, pid, channel, payload_json: str) -> None:
        payload = json.loads(payload_json)
        await self._cache.invalidate(
            UUID(payload["chart_id"]),
            family_id=payload.get("family"),
            strategy_id=payload.get("strategy"),
        )
        # mark outbox row processed
        await conn.execute(
            """
            UPDATE cache_invalidation_outbox
            SET processed_at = now()
            WHERE chart_id = $1 AND technique_family_id = $2
              AND processed_at IS NULL
            """,
            UUID(payload["chart_id"]), payload.get("family"),
        )

    async def _outbox_loop(self) -> None:
        while True:
            await asyncio.sleep(30)
            async with self._session_factory() as s:
                rows = await s.execute(
                    select(CacheInvalidationOutbox)
                    .where(CacheInvalidationOutbox.processed_at.is_(None))
                    .where(CacheInvalidationOutbox.created_at <
                           datetime.utcnow() - timedelta(seconds=60))
                    .limit(500)
                )
                for row in rows.scalars():
                    await self._cache.invalidate(
                        row.chart_id, row.technique_family_id, row.strategy_id
                    )
                    row.processed_at = datetime.utcnow()
                await s.commit()
```

### 5.7 Metrics

Exported via OpenTelemetry / Prometheus:

```
josi_cache_hits_total{layer="l1",family="yoga"}
josi_cache_misses_total{layer="l1",family="yoga"}
josi_cache_latency_seconds_bucket{layer="l1",family="yoga"}
josi_cache_invalidations_total{family="yoga",reason="aggregation_event"}
josi_cache_memory_used_bytes
josi_cache_keys_total
josi_cache_evictions_total
```

Grafana dashboard panels:
- Hit-rate stacked area (L1 / L2 / L3)
- P50/P99 latency per layer
- Keys + memory trend
- Eviction rate
- Invalidation backlog (outbox unprocessed count)

## 6. User Stories

### US-S3.1: As the AI chat backend, my `get_yoga_summary` tool call returns in <2ms on cache hit
**Acceptance:** p99 L1 read latency ≤ 2ms; hit rate ≥ 95% in steady state.

### US-S3.2: As the compute worker, my new aggregation event invalidates the stale L1 key within 1s
**Acceptance:** INSERT into `aggregation_event` → key absent from Redis within 1000ms at p99.

### US-S3.3: As an oncall engineer, I can see hit rate, key count, memory usage, invalidation backlog in Grafana
**Acceptance:** dashboard panels live; alert fires if hit rate < 90% for 15 min or if invalidation backlog > 10k rows.

### US-S3.4: As an engineer, a burst of 1000 concurrent requests for a cold key does not thunder through L2/L3
**Acceptance:** only one request triggers L2 load; remaining 999 read L1 after ≤ 10ms wait or hit L2 directly (not L3).

### US-S3.5: As a developer, adding a new technique family to the cache is a one-file change
**Acceptance:** implementing `CacheHandler` for new family_id and registering in the DI container makes it available via `ServingCache.get`.

## 7. Tasks

### T-S3.1: Provision Cloud Memorystore (Redis) tiers
- **Definition:** Pulumi: `josiam-redis-{env}`; dev = Basic 5 GB; prod = Standard HA 100 GB, `maxmemory-policy=allkeys-lru`.
- **Acceptance:** Redis reachable from Cloud Run via VPC connector; `redis-cli INFO memory` shows `maxmemory_policy:allkeys-lru`.
- **Effort:** 1 day
- **Depends on:** nothing

### T-S3.2: `ServingCache` skeleton + metrics
- **Definition:** Implement `ServingCache.get`, `.invalidate`, stampede guard, metrics per 5.3 & 5.7.
- **Acceptance:** Unit tests for get/invalidate pass; Prometheus metrics visible at `/metrics`.
- **Effort:** 3 days
- **Depends on:** T-S3.1

### T-S3.3: Serialization (orjson + zstd)
- **Definition:** `serialize/deserialize` helpers; threshold and magic-byte handling per 5.5.
- **Acceptance:** round-trip tests for small payloads (no compression) and large payloads (compression). Benchmark: serialize of 10 KB payload < 100µs.
- **Effort:** 1 day
- **Depends on:** nothing

### T-S3.4: Per-family cache handlers
- **Definition:** 6 `CacheHandler` implementations (yoga, dasa, transit, tajaka, jaimini, ashtakavarga) each wiring `l2_loader` to the corresponding `chart_reading_view` column.
- **Acceptance:** each handler loads from L2 given a chart_id with F9 data; returns `None` on absent.
- **Effort:** 3 days
- **Depends on:** T-S3.2, F9 complete

### T-S3.5: Invalidation infrastructure (outbox + trigger + NOTIFY)
- **Definition:** Alembic migration for `cache_invalidation_outbox`, trigger, NOTIFY channel.
- **Acceptance:** inserting into `aggregation_event` triggers both outbox row and NOTIFY event, observable via `psql` LISTEN.
- **Effort:** 1 day
- **Depends on:** F2 complete

### T-S3.6: `InvalidationWorker` Cloud Run job
- **Definition:** Long-running Cloud Run job (always-on) running both NOTIFY and outbox loops per 5.6.
- **Acceptance:** deploying worker → inserting test aggregation_event → key deleted within 1s; killing worker → restart → processes unprocessed outbox rows within 30s.
- **Effort:** 2 days
- **Depends on:** T-S3.5, T-S3.2

### T-S3.7: Integrate cache into AI tool-use handlers
- **Definition:** Replace direct `chart_reading_view` reads in `get_yoga_summary`, `get_current_dasa`, etc. with `ServingCache.get`. Fall-through on L2 miss triggers compute (via S6 hook; stub acceptable if S6 not yet landed).
- **Acceptance:** all 6 tool-use calls route through cache; benchmarks show < 5ms P99 on hits.
- **Effort:** 2 days
- **Depends on:** T-S3.4

### T-S3.8: Grafana dashboard + alerts
- **Definition:** Dashboards-as-code YAML; alerts: hit rate < 90% (15 min), invalidation backlog > 10k, memory > 90%.
- **Acceptance:** dashboards render in Grafana Cloud; alerts fire under synthetic failure injection.
- **Effort:** 1 day
- **Depends on:** T-S3.2, T-S3.6

### T-S3.9: Load test + capacity verification
- **Definition:** Locust scenario: 1000 concurrent users, each doing 1 AI turn / 5s for 10 min. Verify hit rate, Redis CPU, Cloud Run concurrency.
- **Acceptance:** hit rate ≥ 95%; Redis CPU ≤ 50%; no stampede events (stampede guard effective).
- **Effort:** 2 days
- **Depends on:** T-S3.7, T-S3.8

### T-S3.10: Documentation
- **Definition:** Update CLAUDE.md with cache layer overview; `docs/markdown/runbooks/cache-outage.md`.
- **Acceptance:** merged; team training session held.
- **Effort:** 0.5 day
- **Depends on:** T-S3.9

## 8. Unit Tests

### 8.1 ServingCache

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_l1_hit_returns_without_db` | key present in Redis | deserialized value; no L2 call | hit path |
| `test_l1_miss_triggers_l2_load` | key absent, L2 row present | value from L2; key written to Redis | miss → L2 |
| `test_l2_miss_returns_none` | key absent, L2 row absent | None; no L3 compute (caller handles) | contract |
| `test_invalidate_exact_key` | invalidate(chart_id, "yoga", "D_hybrid") | only that key deleted | precise delete |
| `test_invalidate_wildcard_family` | invalidate(chart_id, None, None) | all keys for chart_id deleted | wildcard scan |
| `test_ttl_applied_from_config` | L2 load for family=yoga | Redis EX = 604800 | per-family TTL |
| `test_stampede_only_one_l2_load` | 100 concurrent misses on same key | exactly 1 L2 SQL query observed | stampede guard |
| `test_stampede_lock_expires` | holder crashes; lock TTL 10s | other requester proceeds after 10s | no deadlock |

### 8.2 Serialization

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_small_payload_no_compression` | 500-byte dict | no zstd magic bytes | threshold respected |
| `test_large_payload_compressed` | 10 KB dict | starts with `0x28b52ffd` | compression activated |
| `test_roundtrip_equal` | value → serialize → deserialize | equal to original | correctness |
| `test_deserialize_handles_both_formats` | feed small raw and zstd raw | both decode to same dict | migration safe |

### 8.3 InvalidationWorker

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_notify_triggers_invalidate` | pg_notify with test payload | `cache.invalidate` called with parsed args | NOTIFY path |
| `test_outbox_picks_up_missed_row` | row with `processed_at IS NULL` older than 60s | invalidate called, row marked processed | durable fallback |
| `test_notify_loop_reconnects_on_drop` | connection dropped mid-loop | reconnects within 5s; resumes listening | resilience |
| `test_outbox_retry_backoff` | invalidate fails → retry_count++ | retry_count bounded at 5; then left for alert | bounded retries |

### 8.4 Trigger (DB integration)

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_trigger_writes_outbox_row` | INSERT aggregation_event | outbox row exists | trigger works |
| `test_trigger_emits_notify` | INSERT event; LISTEN in test | payload received | NOTIFY works |
| `test_trigger_payload_shape` | INSERT event | JSON has chart_id, family, strategy keys | schema stable |

### 8.5 Handlers

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_yoga_handler_ttl_7d` | YogaHandler.ttl_seconds | 604800 | config correct |
| `test_transit_handler_ttl_15min` | TransitHandler.ttl_seconds | 900 | freshness |
| `test_yoga_handler_l2_loader_reads_active_yogas` | chart with F9 data | returns active_yogas JSONB deserialized | integration |

### 8.6 Metrics

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_l1_hit_increments_counter` | `get()` on cached key | `josi_cache_hits_total{layer="l1"}` += 1 | observability |
| `test_invalidate_increments_counter` | `invalidate(...)` deletes 3 keys | `josi_cache_invalidations_total` += 3 | observability |
| `test_latency_histogram_recorded` | `get()` call | histogram sample recorded with labeled family | observability |

## 9. EPIC-Level Acceptance Criteria

- [ ] Redis Memorystore provisioned per env
- [ ] `ServingCache` implemented with 6 family handlers
- [ ] Outbox table + trigger + NOTIFY channel live
- [ ] Invalidation worker running; sub-1s invalidation verified
- [ ] Stampede guard prevents L2 thundering herd (load-test proven)
- [ ] L1 hit rate ≥ 95% at 10k-user synthetic load
- [ ] P99 serving latency (L1 hit): ≤ 2 ms
- [ ] P99 serving latency (L1 miss, L2 hit): ≤ 10 ms
- [ ] Grafana dashboard live with hit-rate, memory, invalidation-backlog panels
- [ ] Alerts configured: hit-rate < 90% (15m), invalidation backlog > 10k, memory > 90%
- [ ] Unit test coverage ≥ 90% for `ServingCache`, `InvalidationWorker`, serialization
- [ ] Runbook `docs/markdown/runbooks/cache-outage.md` merged
- [ ] CLAUDE.md updated: "for serving reads, use `ServingCache.get`; never read `chart_reading_view` directly from controllers"

## 10. Rollout Plan

- **Feature flag:** `FEATURE_SERVING_CACHE` (default off); when off, tool-use handlers read directly from `chart_reading_view`.
- **Shadow compute:** Y — for first 72h, cache is populated on reads but read path still serves from L2. Compare cache-path latency to direct-read; verify 95% match.
- **Backfill strategy:** N/A — cache warms naturally from traffic. Optional: one-time warm job for top 10k most-active charts (derived from `aggregation_event` recent inserts).
- **Rollback plan:**
  1. Set `FEATURE_SERVING_CACHE=false` — controllers revert to direct L2 reads.
  2. Invalidation worker keeps running (harmless; empties keys, no reads depend on them).
  3. Re-enable when issue resolved.
  4. Hard kill: `redis-cli FLUSHDB` safely resets (worst case: temporary latency spike as L2 re-serves).

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Invalidation misses → stale data served | Medium | High | NOTIFY + outbox dual path; outbox lag alert; TTL caps staleness at 24h |
| Redis outage | Low | Medium | Fall-through to L2 works; p99 degrades to ~10ms, still acceptable |
| Stampede on popular chart eviction | Medium | Medium | Stampede lock; L2 is fast enough to serve contended misses |
| Memory exhaustion from unexpected payload size | Medium | Medium | Per-family size cap (truncate at 100 KB + alert); memory alert at 90% |
| NOTIFY channel saturation at 10M+ daily events | Low | Medium | Each NOTIFY is small (~200B); postgres handles >100k/sec |
| Clock skew between nodes breaks TTL precision | Low | Low | Redis TTL is server-side; not affected |
| Developer reads `chart_reading_view` directly, bypassing cache | Medium | Low (correctness preserved) | Lint rule + code review + integration test on key endpoints |
| Cost: 100 GB Redis Standard HA | High (certain) | Medium | Review at P3 midpoint; consider Standard (non-HA) if SLA permits |

## 12. References

- Master spec: [`docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`](../../../superpowers/specs/2026-04-19-classical-techniques-expansion-design.md)
- Depends on: [F9](../P0/F9-chart-reading-view-table.md), [S2](./S2-read-replicas-routing.md)
- Enables: [S6](./S6-lazy-compute-strategy.md), [AI5](./AI5-debate-mode-ultra-ai.md)
- Redis LRU docs: https://redis.io/docs/latest/develop/reference/eviction/
- Postgres LISTEN/NOTIFY: https://www.postgresql.org/docs/current/sql-notify.html
- Transactional outbox pattern: Chris Richardson, *Microservices Patterns*, Ch. 3
