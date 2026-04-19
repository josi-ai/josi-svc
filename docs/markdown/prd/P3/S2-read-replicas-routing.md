---
prd_id: S2
epic_id: S2
title: "Read replicas + PgBouncer routing (read/write aware pool)"
phase: P3-scale-10m
tags: [#performance, #correctness]
priority: must
depends_on: [F2, F3]
enables: [S3, S4, S7]
classical_sources: []
estimated_effort: 2 weeks
status: draft
author: Govind
last_updated: 2026-04-19
---

# S2 — Read Replicas + PgBouncer Routing

## 1. Purpose & Rationale

At 100k users we run on a single Cloud SQL Postgres primary. At 10M users the read load on `chart_reading_view`, `technique_compute`, and `aggregation_event` (driven by AI tool-use and astrologer-workbench reads) will saturate primary CPU and IOPS. Writes cannot coexist with that read burden — chart creation and aggregation workflows will queue behind reads, and lock contention on high-volume fact tables will spike tail latency.

This PRD introduces a **read/write-aware connection pool** in front of Postgres:

- **Primary**: all writes. All reads inside a write-transaction.
- **Read replicas** (streaming replication): chart-context reads, `chart_reading_view` lookups, rule registry lookups, any B2C read path.
- **Analytical replica** (`hot_standby_feedback=off`): long-running experiment analytics, Ultra-AI-mode fan-out reads, admin dashboards.

Connection multiplexing via **PgBouncer** in **transaction pooling** mode. Workload routing via a lightweight Python-side dispatcher on top of the existing `EngineManager`, so controllers and services can opt-in to replica reads with a context manager.

Target: lift primary CPU from ~80% steady to ~35%, enable horizontal read scale, keep replication-lag-aware writes so we don't surface stale data after a user's own write.

## 2. Scope

### 2.1 In scope
- Cloud SQL read replicas: **dev = 1**, **prod = 3** (2 hot-serving + 1 analytical).
- PgBouncer deployment on Cloud Run (sidecar-less; dedicated service) in **transaction pooling** mode.
- Pool manager change: `EngineManager` gains a `role` axis (`primary | replica | analytical`) alongside existing tenant axis.
- FastAPI dependency: `get_read_db()` (replica) and `get_async_db()` (primary, existing name preserved).
- Replica-aware decorator: `@reads_from_replica` on controllers/services.
- Post-write read pinning: after a write on a session, subsequent reads within the same request go to primary (avoid read-after-write stale data).
- Replication lag monitoring: Cloud Monitoring metric + Grafana panel + alert.
- Failover handling: if primary fails over, PgBouncer reloads; in-flight transactions fail cleanly with a retriable error class.
- Routing table (documented matrix): which queries / endpoints go to which role.

### 2.2 Out of scope
- Sharding (deferred to S7 / P4).
- Logical replication to ClickHouse (S4 / P4).
- Cross-region replicas (cost/complexity; single-region at P3).
- PgBouncer TLS termination (relies on Cloud SQL Auth Proxy already providing TLS).
- Automatic replica promotion in application layer (Cloud SQL handles failover; we just reconnect).

### 2.3 Dependencies
- F2 (fact tables) — defines the tables whose reads we are offloading.
- F3 (partitioning) — partition pruning reduces replica scan cost.
- Cloud SQL IAM role `cloudsql.client` on the replica SA.
- `josiam-{env}` Pulumi stacks to provision replicas.

## 3. Technical Research

### 3.1 Why PgBouncer in transaction pooling

Cloud Run containers are ephemeral and horizontally scale to hundreds of instances. Without a pooler, each instance opens its own pool to Postgres, and PG hits `max_connections` (default 400 on `db-custom-1-3840`). PgBouncer multiplexes thousands of short client connections onto a small server-connection pool.

**Transaction pooling** (not session pooling) is chosen because:
- asyncpg / SQLAlchemy async sessions are transaction-scoped.
- Prepared statements across reuse boundaries are handled via `server_reset_query = DISCARD ALL` + `statement_cache_size = 0` on asyncpg client side.
- Transaction pooling gets ~4× the multiplexing of session pooling.

Session pooling is used *only* for the analytical pool where long-running analytical queries need advisory locks / temp tables / prepared plan reuse.

### 3.2 Why three replicas in prod

- 2 hot-serving replicas behind a round-robin DNS or PgBouncer multi-host — redundancy for one falling behind or being upgraded.
- 1 analytical replica with `hot_standby_feedback=off`. This prevents long-running analytical queries from blocking vacuum on primary (which is the classical "replica kills primary" footgun). The trade-off: queries on the analytical replica may be cancelled due to conflict with primary vacuums; we handle this via retry-with-backoff in the analytical client.

Dev keeps 1 replica because dev doesn't need analytical isolation and cost matters.

### 3.3 Replication lag budget

Postgres streaming replication with sufficient network bandwidth holds lag under ~50ms at steady state. We budget **P99 500ms** as SLO. Breach triggers:

1. Alert rule owner (oncall).
2. Temporary re-route of that replica's traffic to primary via PgBouncer server_check_query.
3. Investigation: commonly long-running replica query (analytical leakage) or a write burst.

### 3.4 Read-after-write correctness

Common pitfall: user POSTs `/charts`, gets 201, then GETs `/charts/{id}` on next request; GET hits replica, which hasn't caught up; user sees 404. Two mitigations combined:

1. **Session-level write tracking**. A FastAPI middleware sets `request.state.wrote = True` if any write executed. Subsequent reads in same request use primary.
2. **Cross-request pinning via a signed cookie / header** (`X-Read-Consistency: read-your-writes`). After a write, client receives a short-TTL token containing the primary LSN; subsequent reads pass token; dispatcher compares `pg_last_wal_replay_lsn()` on replica — if behind, falls back to primary.

Mitigation 1 is mandatory. Mitigation 2 is optional per-endpoint (decorator-based opt-in for user-facing mutable flows).

### 3.5 Alternatives considered

| Alternative | Rejected because |
|---|---|
| pgpool-II | More features, more ops burden; PgBouncer is simpler and Cloud Run-friendly |
| Cloud SQL read pool (GCP beta) | Limited control over routing and lag observability; revisit at P4 if GA improves |
| Application-side primary-only with vertical scale | Caps at db-custom-96-614400; expensive and single-point-of-failure |
| Proxysql | Postgres support is weak; used primarily for MySQL |
| Pgcat (rust rewrite) | Promising but less battle-tested for our scale; reconsider at P4 |

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| Where does PgBouncer run? | Dedicated Cloud Run service `josi-pgbouncer-{env}` behind internal LB | Scales independently from API; easy to upgrade |
| How many replicas? | dev=1, prod=3 (2 hot + 1 analytical) | Redundancy + analytical isolation |
| Pooling mode | Transaction for hot replicas + primary; Session for analytical | asyncpg transaction scope; analytical needs prepared plans |
| Prepared statements | Disabled (`statement_cache_size=0`) | Transaction pooling mandates |
| How to route? | Python-side dispatcher; `get_read_db()` and `get_async_db()` FastAPI deps | Minimal intrusion; typed opt-in |
| Read-after-write guarantee | Mandatory per-request; optional cross-request via LSN token | Correctness without global primary routing |
| Replication-lag SLO | P99 500ms | Balances correctness vs offload |
| Analytical replica isolation | `hot_standby_feedback=off` + `max_standby_streaming_delay=-1` | Long queries allowed; may be cancelled on vacuum |
| Failover behavior | Retriable `DatabaseReconnectRequired` exception | Explicit contract; caller retries once |

## 5. Component Design

### 5.1 New / modified modules

```
src/josi/db/
├── async_db.py             # modified: add role-aware engines
├── pool_router.py          # NEW: PoolRouter chooses primary/replica/analytical
├── lsn_tracker.py          # NEW: tracks last-write LSN per request
└── retry.py                # NEW: DatabaseReconnectRequired exception + retry decorator

src/josi/api/v1/
├── dependencies.py         # modified: add get_read_db, get_analytical_db
└── middleware/
    └── read_write_tracker.py  # NEW: ASGI middleware, sets request.state.wrote

infra/
├── pgbouncer/
│   ├── Dockerfile
│   ├── pgbouncer.ini.j2    # jinja: template per env
│   └── userlist.txt.j2
└── pulumi/
    ├── cloud_sql.py        # modified: add replicas
    └── pgbouncer.py        # NEW: Cloud Run service for PgBouncer

deploy/
├── pgbouncer.cloudbuild.dev.yaml   # NEW
└── pgbouncer.cloudbuild.prod.yaml  # NEW
```

### 5.2 Data model additions

No new tables. Role-resolution is config-only. One observability view:

```sql
-- Monitoring: replication lag as a queryable view on primary
CREATE OR REPLACE VIEW replication_status AS
SELECT
    application_name             AS replica_name,
    client_addr,
    state,
    pg_wal_lsn_diff(pg_current_wal_lsn(), sent_lsn)    AS send_lag_bytes,
    pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn)  AS replay_lag_bytes,
    extract(epoch FROM replay_lag)                     AS replay_lag_seconds,
    sync_state
FROM pg_stat_replication;
```

### 5.3 Pool router interface

```python
# src/josi/db/pool_router.py

from enum import Enum
from contextvars import ContextVar

class DbRole(str, Enum):
    PRIMARY = "primary"
    REPLICA = "replica"
    ANALYTICAL = "analytical"

_role_ctx: ContextVar[DbRole] = ContextVar("db_role", default=DbRole.REPLICA)
_wrote_ctx: ContextVar[bool] = ContextVar("db_wrote", default=False)

class PoolRouter:
    """Owns one AsyncEngine per role. FastAPI deps pick via context var."""

    def __init__(self, primary_dsn: str, replica_dsn: str, analytical_dsn: str):
        self._engines: dict[DbRole, AsyncEngine] = {
            DbRole.PRIMARY: create_async_engine(primary_dsn, **_primary_opts()),
            DbRole.REPLICA: create_async_engine(replica_dsn, **_replica_opts()),
            DbRole.ANALYTICAL: create_async_engine(analytical_dsn, **_analytical_opts()),
        }

    def engine(self, role: DbRole) -> AsyncEngine:
        # if writes happened this request, force primary
        if _wrote_ctx.get():
            return self._engines[DbRole.PRIMARY]
        return self._engines[role]

    async def session(self, role: DbRole) -> AsyncIterator[AsyncSession]:
        eng = self.engine(role)
        async with AsyncSession(eng, expire_on_commit=False) as s:
            yield s
```

### 5.4 FastAPI dependencies

```python
# src/josi/api/v1/dependencies.py

async def get_async_db() -> AsyncIterator[AsyncSession]:
    """Primary. All writes. Existing name preserved for back-compat."""
    async for s in router.session(DbRole.PRIMARY):
        yield s

async def get_read_db() -> AsyncIterator[AsyncSession]:
    """Replica. Safe for read-only handlers."""
    async for s in router.session(DbRole.REPLICA):
        yield s

async def get_analytical_db() -> AsyncIterator[AsyncSession]:
    """Analytical replica. Long-running or heavy scans."""
    async for s in router.session(DbRole.ANALYTICAL):
        yield s

ReadDbDep = Annotated[AsyncSession, Depends(get_read_db)]
AnalyticalDbDep = Annotated[AsyncSession, Depends(get_analytical_db)]
```

### 5.5 Read-write tracker middleware

```python
# src/josi/api/v1/middleware/read_write_tracker.py

class ReadWriteTrackerMiddleware:
    """Watches SQL statements; on first write, flips context var so
    subsequent reads in same request go to primary."""

    async def __call__(self, scope, receive, send):
        token = _wrote_ctx.set(False)
        try:
            await self.app(scope, receive, send)
        finally:
            _wrote_ctx.reset(token)

# SQLAlchemy event listener
@event.listens_for(Engine, "before_cursor_execute")
def _mark_wrote(conn, cursor, statement, *_):
    if statement.strip().upper().startswith(("INSERT","UPDATE","DELETE","MERGE","CALL")):
        _wrote_ctx.set(True)
```

### 5.6 Routing matrix

| Endpoint / operation | Default role | Reason |
|---|---|---|
| `POST /api/v1/charts` | primary | Write |
| `GET /api/v1/charts/{id}` | replica (primary after own write) | Hot read path |
| `GET /api/v1/charts/{id}/reading` | replica | Reads `chart_reading_view` |
| AI tool-use `get_yoga_summary` | replica | Read-only tool |
| AI tool-use `get_current_dasa` | replica | Read-only tool |
| Chart creation fan-out compute inserts | primary | Writes to `technique_compute` |
| Aggregation worker inserts | primary | Writes to `aggregation_event` |
| `GET /api/v1/admin/experiments/*/metrics` | analytical | Heavy aggregation |
| Ultra AI fan-out reads (all 4 strategies) | analytical | Many reads per request |
| `GET /api/v1/me` | replica | Hot B2C read |
| `GET /api/v1/astrologers/search` | replica | Hot B2C read |
| GraphQL queries (read) | replica | Read-only |
| GraphQL mutations | primary | Writes |
| Alembic migration | primary | DDL |
| Golden-chart nightly diff job | analytical | Long-running scan |

### 5.7 PgBouncer config (per env, rendered from Jinja)

```ini
[databases]
josi_primary     = host=/cloudsql/josiam:us-central1:josiam-{env}    pool_mode=transaction
josi_replica     = host=/cloudsql/josiam:us-central1:josiam-{env}-r1 pool_mode=transaction
josi_replica_alt = host=/cloudsql/josiam:us-central1:josiam-{env}-r2 pool_mode=transaction
josi_analytical  = host=/cloudsql/josiam:us-central1:josiam-{env}-r3 pool_mode=session

[pgbouncer]
listen_addr      = 0.0.0.0
listen_port      = 6432
auth_type        = scram-sha-256
auth_file        = /etc/pgbouncer/userlist.txt

max_client_conn  = 2000      ; clients (Cloud Run workers) may connect
default_pool_size = 50       ; server conns per (db,user) pair
reserve_pool_size = 10
reserve_pool_timeout = 3
server_reset_query = DISCARD ALL
server_idle_timeout = 300
query_timeout    = 30        ; drop queries >30s on hot pools
; analytical pool overrides via [pgbouncer] per-db settings:
; josi_analytical.query_timeout = 600
```

### 5.8 Pulumi additions (sketch)

```python
# infra/pulumi/cloud_sql.py (delta)

replica_1 = gcp.sql.DatabaseInstance(
    f"josiam-{env}-r1",
    master_instance_name=primary.name,
    database_version="POSTGRES_17",
    region="us-central1",
    replica_configuration=gcp.sql.DatabaseInstanceReplicaConfigurationArgs(
        failover_target=False,
    ),
    settings=gcp.sql.DatabaseInstanceSettingsArgs(
        tier="db-custom-1-3840" if env=="dev" else "db-custom-2-7680",
        database_flags=[{"name": "hot_standby_feedback", "value": "on"}],
    ),
)

replica_analytical = gcp.sql.DatabaseInstance(
    f"josiam-{env}-r3",
    master_instance_name=primary.name,
    settings=gcp.sql.DatabaseInstanceSettingsArgs(
        tier="db-custom-2-7680",
        database_flags=[
            {"name": "hot_standby_feedback", "value": "off"},
            {"name": "max_standby_streaming_delay", "value": "-1"},
            {"name": "max_standby_archive_delay", "value": "-1"},
        ],
    ),
)
```

## 6. User Stories

### US-S2.1: As an API consumer, my read is served from a replica while my concurrent chart creation goes to primary
**Acceptance:** p99 AI-tool-use read latency at 10M charts ≤ 200ms; primary write throughput unaffected under concurrent read load.

### US-S2.2: As a user who just POSTed my chart, my next GET returns the chart (no stale 404)
**Acceptance:** 100% of GETs issued in the same request after a write hit primary. Cross-request test: POST /charts then GET /charts/{id} returns 200 with < 1s SLA.

### US-S2.3: As an oncall engineer, I can see replication lag in Grafana and get paged when P99 > 500ms for 5 min
**Acceptance:** Grafana panel `replication_status` live; alert rule `replica_lag_p99_breached` fires to PagerDuty.

### US-S2.4: As an analytics engineer, my long-running query against `aggregation_event` does not affect hot-path reads
**Acceptance:** a 120-second analytical query runs on analytical replica without raising primary CPU above baseline by > 5%; hot replicas' P99 read latency unaffected.

### US-S2.5: As a developer, I opt a new controller into replica reads with a single-line dependency change
**Acceptance:** replacing `AsyncDbDep` with `ReadDbDep` on a read-only controller routes traffic to a replica.

## 7. Tasks

### T-S2.1: Provision read replicas via Pulumi
- **Definition:** Extend `infra/pulumi/cloud_sql.py` to create `r1`, `r2` (hot), `r3` (analytical). Configure flags per 5.8.
- **Acceptance:** `pulumi up` on dev creates 1 replica; on prod creates 3. Replicas stream WAL; `replication_status` view shows `state = streaming`.
- **Effort:** 2 days
- **Depends on:** nothing

### T-S2.2: Build PgBouncer Docker image + Cloud Run deployment
- **Definition:** Dockerfile based on `edoburu/pgbouncer`. Jinja template for `pgbouncer.ini`. Secret Manager integration for `userlist.txt`. Cloud Run service with internal LB; min instances = 2 for prod, 1 for dev.
- **Acceptance:** PgBouncer reachable from `josi-api-{env}` at `josi-pgbouncer-{env}:6432`; `SHOW POOLS` returns expected pools.
- **Effort:** 3 days
- **Depends on:** T-S2.1

### T-S2.3: Implement `PoolRouter` + context vars
- **Definition:** `src/josi/db/pool_router.py` per 5.3. Three engines per process, lazy-initialised. Env vars `DATABASE_URL_PRIMARY`, `DATABASE_URL_REPLICA`, `DATABASE_URL_ANALYTICAL`.
- **Acceptance:** Unit test: acquiring a session under each role returns an engine with matching `bind.url`. Write flips context var.
- **Effort:** 2 days
- **Depends on:** T-S2.2

### T-S2.4: FastAPI dependencies `get_read_db`, `get_analytical_db`
- **Definition:** `src/josi/api/v1/dependencies.py` additions per 5.4. Update docstrings.
- **Acceptance:** mypy passes; existing `get_async_db` still routes to primary.
- **Effort:** 2 hours
- **Depends on:** T-S2.3

### T-S2.5: Read-write tracker middleware
- **Definition:** ASGI middleware + SQLAlchemy event listener per 5.5. Registered in `app_factory`.
- **Acceptance:** Integration test: handler writes then reads; both queries land on primary. Separate request reads: replica.
- **Effort:** 1 day
- **Depends on:** T-S2.3

### T-S2.6: Route audit — update controllers to use correct DB dep
- **Definition:** Audit all controllers under `src/josi/api/v1/controllers/`. Apply routing matrix (5.6). Update dependency imports.
- **Acceptance:** Routing matrix implemented; integration tests confirm expected role per endpoint.
- **Effort:** 3 days
- **Depends on:** T-S2.5

### T-S2.7: Replication-lag monitoring + alert
- **Definition:** Create `replication_status` view (migration). Export lag to Cloud Monitoring via scheduled Cloud Run job polling `pg_stat_replication` every 30s. Grafana dashboard panel. Alert: P99 > 500ms for 5 min.
- **Acceptance:** Dashboard live; synthetic test: kill a replica's recovery for 10s; alert fires within 5 min.
- **Effort:** 2 days
- **Depends on:** T-S2.1

### T-S2.8: Failover handling
- **Definition:** Raise `DatabaseReconnectRequired` (subclass of `OperationalError`) when asyncpg reports `ConnectionDoesNotExistError` or `AdminShutdownError`. Retry decorator catches and retries once with a 100ms delay.
- **Acceptance:** Chaos test: trigger Cloud SQL failover in dev; ongoing API requests either succeed or return retriable 503 with `Retry-After`.
- **Effort:** 2 days
- **Depends on:** T-S2.3

### T-S2.9: Documentation updates
- **Definition:** CLAUDE.md: "use `ReadDbDep` for read-only handlers, `AsyncDbDep` for writes". Add runbook `docs/markdown/runbooks/replica-failover.md`.
- **Acceptance:** Docs merged; PRs referencing wrong dep flagged by reviewers.
- **Effort:** 0.5 day
- **Depends on:** T-S2.6

## 8. Unit Tests

### 8.1 PoolRouter

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_router_returns_primary_engine_for_primary_role` | `router.engine(DbRole.PRIMARY)` in fresh ctx | engine bound to primary DSN | role routing |
| `test_router_returns_replica_for_replica_role_when_no_writes` | `engine(REPLICA)` with `_wrote_ctx=False` | replica engine | happy-path read |
| `test_router_returns_primary_for_replica_role_after_write` | `engine(REPLICA)` with `_wrote_ctx=True` | primary engine | read-after-write |
| `test_analytical_role_unaffected_by_wrote_ctx` | `engine(ANALYTICAL)` with `_wrote_ctx=True` | analytical engine | analytical is explicit caller opt-in |
| `test_router_session_closes_on_exit` | enter+exit `router.session()` | underlying connection returned to pool | no leak |

### 8.2 ReadWriteTrackerMiddleware

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_ctx_starts_false` | new request | `_wrote_ctx.get() is False` | default is read |
| `test_ctx_flips_on_insert` | INSERT statement intercepted by event listener | `_wrote_ctx.get() is True` | flag detection |
| `test_ctx_flips_on_update` | UPDATE | True | same |
| `test_select_does_not_flip` | SELECT | False | read safe |
| `test_ctx_reset_between_requests` | request A writes, request B reads | B sees `False` | isolation |

### 8.3 Replication-lag tracker

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_lag_tracker_reports_ms_behind` | mock `pg_stat_replication` with replay_lag=0.3s | metric `replica_replay_lag_seconds=0.3` | correct parsing |
| `test_lag_tracker_aggregates_multi_replicas` | 2 replicas, lags 0.1s & 0.7s | metric labeled per replica_name | cardinality correct |
| `test_lag_alert_fires_above_threshold` | synthetic 600ms sustained for 5 min | alert condition evaluates true | alerting |
| `test_lag_tracker_survives_replica_down` | `pg_stat_replication` empty for one replica | no crash; emits `replica_unavailable=1` gauge | resilience |

### 8.4 Retry & failover

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_reconnect_raises_retriable_error` | simulated `AdminShutdownError` on execute | raises `DatabaseReconnectRequired` | typed exception |
| `test_decorator_retries_once_on_reconnect` | first call raises DRR, second succeeds | final result returned | auto-retry semantics |
| `test_decorator_does_not_retry_twice` | both attempts raise DRR | raises to caller | bounded retries |
| `test_non_retriable_error_propagates` | generic `IntegrityError` | not retried, raises immediately | scope of retry |

### 8.5 Routing matrix (integration)

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_get_chart_reads_from_replica` | GET `/charts/{id}` | engine used has DSN containing `-r1` or `-r2` | matrix enforcement |
| `test_post_chart_writes_to_primary` | POST `/charts` | primary DSN used | write role |
| `test_ai_toolcall_uses_replica` | `get_yoga_summary` tool invocation | replica DSN | AI tool role |
| `test_admin_metrics_uses_analytical` | GET `/admin/experiments/{id}/metrics` | analytical DSN | analytical opt-in |
| `test_post_then_get_same_request_uses_primary` | handler that writes + reads | both on primary | read-after-write in-request |

## 9. EPIC-Level Acceptance Criteria

- [ ] 3 replicas provisioned in prod, 1 in dev, via Pulumi
- [ ] PgBouncer running on Cloud Run with transaction pooling for hot pools, session pooling for analytical
- [ ] Routing matrix implemented and covered by integration tests
- [ ] Read-after-write correctness proven by integration test
- [ ] Replication lag dashboard live; alert configured
- [ ] Primary CPU utilization at 100k-user synthetic load ≤ 50% (baseline was 80%)
- [ ] AI tool-use read P99 ≤ 200ms at 1M-chart synthetic dataset
- [ ] Failover chaos test: one failed hot replica causes ≤ 1% request errors for ≤ 60s
- [ ] Unit test coverage ≥ 90% for `PoolRouter`, middleware, retry
- [ ] Runbook `docs/markdown/runbooks/replica-failover.md` merged
- [ ] CLAUDE.md updated with `ReadDbDep` usage guideline

## 10. Rollout Plan

- **Feature flag:** `FEATURE_REPLICA_ROUTING` (default off in dev until T-S2.5 green; on in prod after 1 week of shadow).
- **Shadow compute:** Y — for first 48h, dispatcher logs the intended role but still sends all queries to primary; compare logged lag vs observed. Promote to real routing after 99% of logged would-be-replica queries show lag < 500ms.
- **Backfill strategy:** N/A — no data changes.
- **Rollback plan:**
  1. Set `FEATURE_REPLICA_ROUTING=false` — `PoolRouter.engine()` returns primary for all roles.
  2. Redeploy PgBouncer pointing all `[databases]` entries at primary.
  3. Replicas kept streaming; reactivated when issue resolved.

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Read-after-write bug surfaces stale data | Medium | High | Mandatory in-request write-tracker; LSN token for cross-request endpoints; strong integration tests |
| Transaction pooling breaks prepared statements | High (first time) | Medium | `statement_cache_size=0` on asyncpg; doc'd in CLAUDE.md |
| Analytical replica query cancelled during vacuum storm | Medium | Low | Retry-with-backoff in analytical client; alert if cancel rate > 5%/hr |
| PgBouncer becomes SPOF | Medium | High | Min 2 instances in prod; Cloud Run auto-heals; request queue < 30s timeout |
| Replica falls behind > 500ms sustained | Medium | Medium | Alert + auto-drain replica from hot pool via health check |
| Cost: 3 extra Cloud SQL instances | High (certain) | Medium | Dev = 1 replica only; analytical = dev-tier `db-custom-2-7680`; budget review at P3 midpoint |
| Developer forgets to use `ReadDbDep` | High | Low (correctness preserved) | PR template checkbox; lint rule flags read-only controllers that use primary |

## 12. References

- Master spec: [`docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`](../../../superpowers/specs/2026-04-19-classical-techniques-expansion-design.md)
- Depends on: [F2](../P0/F2-fact-tables.md), [F3](../P0/F3-partitioning-from-day-one.md)
- Enables: [S3](./S3-three-layer-serving-cache.md), [S4](../P4/S4-olap-replication-clickhouse.md), [S7](../P4/S7-sharding-citus-or-splitting.md)
- PgBouncer docs: https://www.pgbouncer.org/config.html
- Cloud SQL read replicas: https://cloud.google.com/sql/docs/postgres/replication
- Postgres streaming replication: https://www.postgresql.org/docs/current/warm-standby.html
