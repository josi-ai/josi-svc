---
prd_id: S5
epic_id: S5
title: "Durable workflow orchestration (procrastinate at P3, optional Temporal at P4)"
phase: P3-scale-10m
tags: [#performance, #correctness]
priority: must
depends_on: [F8, F2]
enables: [S6, S3, P3-E6-flag]
classical_sources: []
estimated_effort: 3 weeks
status: draft
author: Govind
last_updated: 2026-04-19
---

# S5 — Durable Workflow Orchestration

## 1. Purpose & Rationale

Chart creation triggers a fan-out of computations: per-family rule evaluation across multiple source_ids, then aggregation under 4 strategies, then `chart_reading_view` materialization. At P1 we ran this synchronously in the request handler with `asyncio.gather` — works up to a few hundred rules. By P3 we have 250+ rules × 10 sources × 4 strategies = **10,000+ fan-out tasks per chart**, with retries, idempotency, and partial failures to coordinate.

Synchronous fan-out breaks at scale:
- Request timeouts (Cloud Run 60-minute limit far exceeded).
- No retry on transient DB hiccup.
- No idempotency across retries.
- No visibility (which of the 10k tasks failed?).
- No backfill support (re-run task for 10M charts when rule changes).

This PRD adopts **procrastinate** (Postgres-backed task queue) as our durable workflow runtime at P3. Procrastinate is simple, ops-light, and runs inside our existing Postgres — no new infrastructure. We keep Temporal as the documented upgrade path at P4 if our orchestration needs grow beyond procrastinate's model (e.g., signals, child workflows, multi-day sagas).

Workflows at P3:
- `create_chart_workflow` — after chart persisted, fan out compute per source, aggregate per strategy, refresh reading view.
- `recompute_family_workflow` — triggered on rule version bump (F4).
- `backfill_source_workflow` — when a new source is added, compute its rules across all charts.
- `invalidation_workflow` — adjunct to S3 (cache invalidation cascade when rule version changes).

Idempotency is free: every task's PK is `(chart_id, rule_id, source_id, rule_version)` (F2). Retries are safe by construction.

## 2. Scope

### 2.1 In scope
- Procrastinate library integration (https://procrastinate.readthedocs.io/).
- Postgres tables: `procrastinate_jobs`, `procrastinate_events` (library-managed; added via Alembic).
- Core workflows:
  1. `create_chart_workflow(chart_id)` — invoked after `POST /charts`.
  2. `compute_all_sources(chart_id)` — child: fans out per-(family, source) compute tasks.
  3. `aggregate_all_strategies(chart_id, family_id)` — runs 4 strategies.
  4. `refresh_reading_view(chart_id)` — final step; writes F9 row.
  5. `recompute_family_workflow(technique_family_id, rule_version)` — rule-bump trigger.
  6. `backfill_source_workflow(source_id, rule_ids, chart_filter)` — admin-invoked.
- Retry policy: exponential backoff (1s, 4s, 16s, 64s, 256s), max 5 retries.
- Idempotency: every task identified by deterministic `lock` string. Duplicate enqueues are no-ops.
- Dead-letter queue (DLQ): tasks past max retries move to `procrastinate_jobs_failed`; oncall inspects.
- Workers: Cloud Run Jobs with `procrastinate worker` command, horizontally scaled.
- Observability: task queue depth, task latency histogram, failure rate, DLQ size.
- Admin API: trigger backfill, inspect running workflows, retry DLQ.
- Temporal decision matrix + migration sketch (for P4 doc; not implemented).

### 2.2 Out of scope
- Multi-day sagas, human-in-the-loop approval flows — procrastinate is sufficient at P3.
- Cross-service workflows (web, AI, astrologer consultation) — service-local workflows only.
- Temporal implementation — documented as P4 option; not adopted now.
- Celery — rejected in decision matrix below.
- Workflow definition DSL — we use plain Python decorators.

### 2.3 Dependencies
- F2 fact tables (idempotent upserts rely on composite PK).
- F8 aggregation protocol (strategies are stateless pure functions).
- Cloud Run Jobs (already in use via deploy YAMLs).

## 3. Technical Research

### 3.1 Decision matrix: Temporal vs procrastinate vs Celery

| Dimension | procrastinate | Celery | Temporal |
|---|---|---|---|
| Storage backend | **Postgres (existing)** | Redis / RabbitMQ | Temporal cluster (k8s) |
| Infra to add | **None** | Redis (have) + broker config | Temporal cluster (significant) |
| Operational complexity | **Low** | Medium | High |
| Python SDK maturity | Good (actively developed) | Very mature | Good (newer) |
| Async-native | **Yes** | Partial (acks-late workflows tricky) | Yes |
| Durability | Postgres WAL | Needs result backend config | Event-sourced, strong |
| Workflow primitives | Tasks + periodic + chains | Tasks + chord/group | **Full workflow-as-code** (signals, child WFs, timers) |
| Idempotency story | Lock strings | Manual | Built-in (determinism) |
| Cost | ~0 (uses existing PG) | Redis + broker | Temporal cluster (~$200/mo min) |
| Learning curve | Low | Medium | **High** |
| Failure visibility | `procrastinate shell` + DB views | Flower dashboard | Temporal Web UI |
| Right for P3 (10M) | **Yes** | Marginal | Overkill |
| Right for P4 (100M) | Borderline | No | **Yes** |

**Decision: procrastinate for P3. Revisit at P4.**

Rationale:
- Zero new infrastructure — fits our "one-repo Postgres-centric" philosophy.
- Idempotency via lock strings aligns perfectly with F2 composite PKs.
- Sufficient for our fan-out pattern (no multi-day sagas or human approvals needed).
- Temporal is the clear winner when we hit 100M users and need cross-service workflow coordination; its cost and complexity is unjustified now.

### 3.2 Idempotency construction

Each task takes a `lock` kwarg:

```python
await compute_for_source.defer_async(
    lock=f"compute:{chart_id}:{family_id}:{source_id}:{rule_version}",
    chart_id=str(chart_id),
    family_id=family_id,
    source_id=source_id,
    rule_version=rule_version,
)
```

Procrastinate guarantees only one job with a given `lock` runs at a time; duplicates queued while one runs are merged. The task body itself is idempotent via F2 `ON CONFLICT DO NOTHING`.

### 3.3 Retry backoff

Default: `RetryStrategy(max_attempts=5, exponential_wait=4, linear_wait=0)`.
Which means: 0s (first attempt), 4s, 16s, 64s, 256s between retries; total ~5.5 min.

Exceptions:
- `IntegrityError` — retry (transient FK conflicts during concurrent inserts).
- `ConnectionError`, `OperationalError` — retry.
- `JSONSchemaValidationError` — **do not retry** (data bug; DLQ immediately).
- `ValueError` from rule DSL — **do not retry** (rule bug; DLQ immediately).

### 3.4 Fan-out structure

```python
@app.task(queue="create_chart")
async def create_chart_workflow(chart_id: str) -> None:
    # 1. Fan out compute per (family, source)
    rules = await load_active_rules()
    for family_id, source_id, rule_version in _compute_matrix(rules):
        await compute_for_source.defer_async(
            lock=f"compute:{chart_id}:{family_id}:{source_id}:{rule_version}",
            chart_id=chart_id, family_id=family_id,
            source_id=source_id, rule_version=rule_version,
        )

    # 2. When all compute_for_source done, aggregate
    # Use a barrier task that waits on compute_for_source tasks
    await aggregation_barrier.defer_async(
        lock=f"barrier:{chart_id}",
        chart_id=chart_id,
    )

@app.task(queue="compute", retry=_retry_5)
async def compute_for_source(
    chart_id: str, family_id: str, source_id: str, rule_version: str,
) -> None:
    # Delegates to ClassicalEngine for that family
    ...

@app.task(queue="aggregate", retry=_retry_5)
async def aggregation_barrier(chart_id: str) -> None:
    # Poll: are all compute_for_source tasks for this chart done?
    pending = await count_pending_compute_tasks(chart_id)
    if pending > 0:
        raise TransientError(f"{pending} compute tasks still pending")
    # All done → aggregate
    for family_id in ACTIVE_FAMILIES:
        for strategy_id in ACTIVE_STRATEGIES:
            await aggregate_strategy.defer_async(
                lock=f"aggregate:{chart_id}:{family_id}:{strategy_id}",
                chart_id=chart_id, family_id=family_id, strategy_id=strategy_id,
            )
    # After aggregation, refresh view
    await refresh_reading_view.defer_async(
        lock=f"refresh:{chart_id}",
        chart_id=chart_id,
    )
```

The barrier pattern: `aggregation_barrier` raises a transient error if compute tasks are still pending, which schedules it for retry with backoff. By retry 3, compute tasks are almost certainly done.

Alternative (cleaner but more moving parts): Use procrastinate's `blocking_task` feature with a downstream task that waits. Rejected because `blocking_task` requires sync callbacks; the barrier-retry pattern keeps things async-friendly.

### 3.5 Queues and worker pools

| Queue | Purpose | Worker concurrency | Cloud Run instances |
|---|---|---|---|
| `create_chart` | orchestrator tasks | 10 | 2 (prod) |
| `compute` | per-source fan-out | 50 per worker | 4 (prod), auto-scale to 20 |
| `aggregate` | per-strategy fan-out | 20 per worker | 2 (prod), auto-scale to 8 |
| `refresh` | F9 view update | 5 | 1 |
| `backfill` | bulk backfill tasks | 20 per worker | 1-10 (scaled on demand) |
| `invalidation` | S3 cascade | 10 per worker | 1 |

### 3.6 Observability

Exposed metrics (via procrastinate's built-in + custom):

```
procrastinate_jobs_total{status="todo|doing|succeeded|failed"}
procrastinate_job_duration_seconds{task,queue}
procrastinate_queue_depth{queue}
procrastinate_retries_total{task}
procrastinate_dlq_size
josi_workflow_tasks_per_chart_histogram
```

Grafana panels:
- Queue depth per queue (time series)
- Task success/failure rates
- P50/P99 task duration per task name
- DLQ size + age of oldest failed task
- Workers alive count

Alerts:
- DLQ size > 50 for > 15 min → page
- Queue depth `compute` > 100,000 for > 30 min → page (worker pool saturated)
- P99 `compute_for_source` duration > 10s (sign of DB contention)

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| Temporal, procrastinate, or Celery? | procrastinate at P3, Temporal at P4 if needed | Decision matrix 3.1 |
| Backend | Postgres (primary cluster) | Zero new infra |
| Workflow definition style | Python decorators on async functions | Idiomatic; simple |
| Idempotency | `lock` strings + F2 composite PKs | Double defense |
| Retry policy | Exponential backoff, 5 attempts, ~5.5 min total | Balances transient vs DLQ |
| DLQ handling | Human-triggered retry from admin API | Avoid infinite-retry data bugs |
| Barrier pattern | Retry-based (transient error until deps complete) | Keeps tasks async-compatible |
| Workers | Cloud Run Jobs with `--always-on` | Fits existing deploy pattern |
| Separate queues | Yes, per workload | Isolation of backfill from hot path |
| Task timeout | 5 min per task (hard kill) | Prevents runaway |

## 5. Component Design

### 5.1 New modules

```
src/josi/workflows/
├── __init__.py
├── app.py                        # procrastinate App instance + config
├── tasks/
│   ├── __init__.py
│   ├── create_chart.py          # create_chart_workflow
│   ├── compute.py               # compute_for_source
│   ├── aggregate.py             # aggregation_barrier, aggregate_strategy
│   ├── refresh.py               # refresh_reading_view
│   ├── recompute.py             # recompute_family_workflow
│   ├── backfill.py              # backfill_source_workflow
│   └── invalidation.py          # invalidation cascade (S3 adjunct)
├── retry.py                      # RetryStrategy presets
├── errors.py                     # TransientError, PermanentError
└── admin_api.py                  # trigger/inspect/retry DLQ

src/josi/api/v1/controllers/
└── admin_workflow_controller.py  # NEW: POST /admin/workflows/...

deploy/
└── workflow-worker.cloudbuild.{dev,prod}.yaml   # NEW: worker Cloud Run Jobs

docker/
└── Dockerfile.worker             # NEW: worker image (uses same base + procrastinate CLI)
```

### 5.2 Data model additions

Procrastinate ships its own schema. We mount it via Alembic:

```python
# src/alembic/versions/{ts}_add_procrastinate.py
from procrastinate.schema import SchemaManager

def upgrade():
    schema = SchemaManager.get_schema()
    op.execute(schema)

def downgrade():
    op.execute("DROP SCHEMA procrastinate CASCADE")
```

Tables created (owned by procrastinate):
- `procrastinate_jobs` — the queue
- `procrastinate_events` — state transitions
- `procrastinate_periodic_defers` — scheduled recurring jobs

Our own additions:

```sql
-- DLQ inspection view
CREATE VIEW procrastinate_dlq AS
SELECT
    id, task_name, args, lock, status, scheduled_at, attempts,
    last_error, last_attempt_at
FROM procrastinate_jobs
WHERE status = 'failed';

-- Workflow audit log (beyond what procrastinate records)
CREATE TABLE workflow_audit (
    id              BIGSERIAL PRIMARY KEY,
    workflow_name   TEXT NOT NULL,
    chart_id        UUID,
    triggered_by    TEXT,         -- 'api' | 'worker' | 'admin' | 'backfill'
    input_args      JSONB,
    started_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    finished_at     TIMESTAMPTZ,
    status          TEXT CHECK (status IN ('started','succeeded','failed','partial')),
    task_count      INT
);

CREATE INDEX idx_workflow_audit_chart ON workflow_audit(chart_id, started_at DESC);
```

### 5.3 procrastinate app configuration

```python
# src/josi/workflows/app.py

from procrastinate import App, PsycopgConnector
from josi.config import settings

app = App(
    connector=PsycopgConnector(
        kwargs={
            "host": settings.DB_HOST_PRIMARY,
            "port": settings.DB_PORT,
            "user": settings.DB_USER,
            "password": settings.DB_PASSWORD,
            "dbname": settings.DB_NAME,
        }
    ),
    import_paths=[
        "josi.workflows.tasks.create_chart",
        "josi.workflows.tasks.compute",
        "josi.workflows.tasks.aggregate",
        "josi.workflows.tasks.refresh",
        "josi.workflows.tasks.recompute",
        "josi.workflows.tasks.backfill",
        "josi.workflows.tasks.invalidation",
    ],
)
```

### 5.4 Retry strategy presets

```python
# src/josi/workflows/retry.py

from procrastinate import RetryStrategy, BaseRetryStrategy
from josi.workflows.errors import TransientError, PermanentError

class ClassifiedRetry(BaseRetryStrategy):
    """Retries transient errors with exponential backoff.
    Does not retry permanent errors (→ DLQ immediately)."""

    def __init__(self, max_attempts: int = 5):
        self.max_attempts = max_attempts

    def get_retry_decision(self, *, exception, job) -> bool | float:
        if isinstance(exception, PermanentError):
            return False  # DLQ immediately
        if job.attempts >= self.max_attempts:
            return False
        wait_seconds = 4 ** job.attempts  # 4, 16, 64, 256, 1024 — cap in practice
        return wait_seconds

retry_5 = ClassifiedRetry(max_attempts=5)
retry_3 = ClassifiedRetry(max_attempts=3)
```

### 5.5 Core task signatures

```python
# src/josi/workflows/tasks/create_chart.py

@app.task(
    queue="create_chart",
    retry=retry_5,
    pass_context=True,
    timeout_seconds=300,
)
async def create_chart_workflow(
    context: JobContext,
    chart_id: str,
    source_ids: list[str] | None = None,
) -> None:
    ...

# src/josi/workflows/tasks/compute.py

@app.task(
    queue="compute",
    retry=retry_5,
    pass_context=True,
    timeout_seconds=300,
)
async def compute_for_source(
    context: JobContext,
    chart_id: str,
    family_id: str,
    source_id: str,
    rule_version: str,
) -> None:
    ...

# src/josi/workflows/tasks/aggregate.py

@app.task(queue="aggregate", retry=retry_5)
async def aggregation_barrier(chart_id: str) -> None:
    pending = await _count_pending_compute(chart_id)
    if pending > 0:
        raise TransientError(f"{pending} compute tasks pending")
    for family_id, strategy_id in _aggregation_matrix():
        await aggregate_strategy.defer_async(
            lock=f"aggregate:{chart_id}:{family_id}:{strategy_id}",
            chart_id=chart_id, family_id=family_id, strategy_id=strategy_id,
        )
    await refresh_reading_view.defer_async(
        lock=f"refresh:{chart_id}", chart_id=chart_id,
    )

@app.task(queue="aggregate", retry=retry_5)
async def aggregate_strategy(
    chart_id: str, family_id: str, strategy_id: str,
) -> None:
    ...

# src/josi/workflows/tasks/refresh.py

@app.task(queue="refresh", retry=retry_3)
async def refresh_reading_view(chart_id: str) -> None:
    ...

# src/josi/workflows/tasks/backfill.py

@app.task(queue="backfill", retry=retry_5, timeout_seconds=600)
async def backfill_source_workflow(
    source_id: str,
    rule_ids: list[str],
    chart_filter: dict,  # e.g., {"created_after": "2026-01-01"}
) -> None:
    ...
```

### 5.6 Admin API

```
POST /api/v1/admin/workflows/trigger
Body: { "workflow": "backfill_source", "args": {...} }
Response: { "job_id": "...", "lock": "..." }

GET /api/v1/admin/workflows/{job_id}
Response: { "status": "doing", "attempts": 2, ... }

POST /api/v1/admin/workflows/{job_id}/retry
Response: { "requeued": true, "new_scheduled_at": "..." }

GET /api/v1/admin/workflows/dlq
Response: { "items": [ { "id": ..., "task_name": ..., "last_error": ..., "age_seconds": ... } ] }

POST /api/v1/admin/workflows/dlq/purge
Body: { "older_than_seconds": 604800 }   # purge DLQ entries >7d
```

All admin endpoints require `role=admin` JWT claim.

## 6. User Stories

### US-S5.1: As an engineer, when a chart is POSTed, its computation happens in the background and completes within 10s for typical inputs
**Acceptance:** p95 time from `POST /charts` → `chart_reading_view` row populated ≤ 10s in prod at 10k-chart baseline load.

### US-S5.2: As the system, a transient DB hiccup during compute does not fail the chart creation
**Acceptance:** injected `OperationalError` on first 2 attempts; task succeeds on 3rd attempt; no user-visible failure.

### US-S5.3: As an ops engineer, I can list DLQ tasks and retry them from an admin endpoint
**Acceptance:** `GET /admin/workflows/dlq` returns failed jobs; `POST .../{id}/retry` requeues and succeeds (or re-DLQs with new error).

### US-S5.4: As a product owner, triggering a backfill for a new source processes 10k charts without affecting hot-path compute
**Acceptance:** `backfill` queue has dedicated workers; `compute` queue P99 latency unchanged during a 10k-chart backfill.

### US-S5.5: As an ops engineer, I can see queue depth, task latency, DLQ size in Grafana and get paged on anomalies
**Acceptance:** dashboards live; alert rules wired.

### US-S5.6: As an engineer, enqueueing the same `(chart_id, family, source, version)` twice results in exactly one execution
**Acceptance:** integration test: call `compute_for_source.defer_async` twice with same lock concurrently; exactly one row in `technique_compute`; one task in `succeeded` state, one in `cancelled` (merged).

## 7. Tasks

### T-S5.1: Install procrastinate + Alembic schema
- **Definition:** Add `procrastinate = "^2.9"` to `pyproject.toml`. Generate migration mounting procrastinate schema. Add `workflow_audit` + `procrastinate_dlq` view.
- **Acceptance:** `alembic upgrade head` applies; tables exist; `procrastinate shell` connects.
- **Effort:** 1 day
- **Depends on:** F2 complete

### T-S5.2: App factory + task scaffolding
- **Definition:** Implement `src/josi/workflows/app.py`, `retry.py`, `errors.py`. Empty task modules with signatures.
- **Acceptance:** `python -m procrastinate --app josi.workflows.app.app healthchecks all` passes.
- **Effort:** 1 day
- **Depends on:** T-S5.1

### T-S5.3: `compute_for_source` task
- **Definition:** Wire to per-family engines (existing ClassicalEngine Protocol from F2). Uses F2 `ON CONFLICT DO NOTHING` for idempotent inserts.
- **Acceptance:** task enqueue → run → `technique_compute` row present with correct payload. Re-enqueue same lock → no new row.
- **Effort:** 3 days
- **Depends on:** T-S5.2

### T-S5.4: `aggregate_strategy` task
- **Definition:** Invokes 4 strategies via F8 Protocol; writes `aggregation_event` rows.
- **Acceptance:** task produces 4 events per (chart, family); each event carries correct strategy_id + version.
- **Effort:** 2 days
- **Depends on:** T-S5.2

### T-S5.5: `aggregation_barrier` + `create_chart_workflow`
- **Definition:** Fan-out orchestrator + barrier retry pattern per 3.4.
- **Acceptance:** integration test: post chart → wait for reading_view row → asserts yoga/dasa/transit fields populated.
- **Effort:** 3 days
- **Depends on:** T-S5.3, T-S5.4

### T-S5.6: `refresh_reading_view` task
- **Definition:** Reads latest aggregation_events, writes `chart_reading_view` row.
- **Acceptance:** writes correct row; idempotent on re-run.
- **Effort:** 2 days
- **Depends on:** T-S5.4

### T-S5.7: `recompute_family_workflow` + `backfill_source_workflow`
- **Definition:** Bulk enqueuers; chunked to 1000 charts per batch to avoid exhausting queue.
- **Acceptance:** triggering backfill for 10k charts enqueues 10k tasks + completes in < 30 min on 2 workers.
- **Effort:** 3 days
- **Depends on:** T-S5.3

### T-S5.8: Worker Docker image + Cloud Run Jobs deploy
- **Definition:** `docker/Dockerfile.worker` runs `procrastinate worker --queues ...`. Cloud Run Job per queue class. Separate `create_chart` / `compute` / `aggregate` / `refresh` / `backfill` / `invalidation` pools.
- **Acceptance:** workers deployed; scale event triggers new instances; workers process tasks.
- **Effort:** 3 days
- **Depends on:** T-S5.2

### T-S5.9: Admin API controller
- **Definition:** `src/josi/api/v1/controllers/admin_workflow_controller.py` per 5.6.
- **Acceptance:** all 5 endpoints functional; require admin auth; covered by integration tests.
- **Effort:** 2 days
- **Depends on:** T-S5.2

### T-S5.10: Observability (metrics + dashboards + alerts)
- **Definition:** Export procrastinate metrics via OTel. Grafana dashboard YAML. Alert rules for queue depth, DLQ size, task duration.
- **Acceptance:** dashboard live; synthetic DLQ injection fires alert within 15 min.
- **Effort:** 2 days
- **Depends on:** T-S5.8

### T-S5.11: Integrate `POST /charts` with workflow trigger
- **Definition:** Replace inline `asyncio.gather` compute in chart controller with `create_chart_workflow.defer_async`.
- **Acceptance:** POST /charts returns 201 immediately with `workflow_job_id`; reading_view populates asynchronously.
- **Effort:** 1 day
- **Depends on:** T-S5.5

### T-S5.12: Documentation + runbook
- **Definition:** CLAUDE.md: workflow patterns. Runbook `docs/markdown/runbooks/workflow-ops.md`: how to inspect DLQ, re-enqueue, pause queue.
- **Acceptance:** merged; team walk-through.
- **Effort:** 1 day
- **Depends on:** T-S5.9, T-S5.10

### T-S5.13: Temporal migration design doc (non-implementation)
- **Definition:** 2-page `docs/markdown/design/temporal-migration-at-p4.md` — when we'd switch and what maps.
- **Acceptance:** merged; references in this PRD section 3.1.
- **Effort:** 1 day
- **Depends on:** nothing

## 8. Unit Tests

### 8.1 Idempotency

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_lock_prevents_concurrent_execution` | 2 concurrent defer_async with same lock | only 1 task runs; other merged | lock semantics |
| `test_repeated_compute_is_noop` | 3 sequential compute_for_source with same args | `technique_compute` has 1 row | F2 ON CONFLICT |
| `test_different_rule_version_produces_new_row` | same chart/family/source, different rule_version | 2 rows present | version segregation |
| `test_backfill_of_existing_compute_is_noop` | backfill task over already-computed charts | no new rows; tasks succeed | idempotent backfill |

### 8.2 Retry behavior

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_transient_error_retries` | task raises OperationalError on attempt 1; succeeds on 2 | job marked succeeded; 2 attempts recorded | retry works |
| `test_permanent_error_immediately_dlq` | task raises JSONSchemaValidationError | job marked failed after attempt 1 | no-retry policy |
| `test_max_attempts_respected` | task always raises OperationalError | job marked failed after 5 attempts | bounded retry |
| `test_exponential_backoff_timing` | observe `scheduled_at` across attempts | intervals roughly 4, 16, 64, 256s | backoff correct |

### 8.3 Barrier pattern

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_barrier_waits_for_compute_tasks` | 5 compute tasks pending; barrier runs | barrier raises TransientError → retry scheduled | waits for children |
| `test_barrier_proceeds_when_done` | 0 compute tasks pending; barrier runs | spawns aggregate tasks and refresh | proceeds |
| `test_barrier_does_not_run_aggregate_prematurely` | 1 compute pending, 4 done; barrier runs | aggregate tasks NOT enqueued | safety |

### 8.4 create_chart_workflow

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_create_chart_fans_out_per_matrix` | chart with 3 families × 3 sources | 9 compute tasks enqueued | fan-out correct |
| `test_create_chart_respects_source_filter` | call with source_ids=["bphs"] | tasks only for bphs enqueued | parameter works |
| `test_create_chart_triggers_barrier` | workflow run | barrier task enqueued after compute fan-out | pipeline complete |

### 8.5 Admin API

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_trigger_backfill_returns_job_id` | POST /admin/workflows/trigger | 200 with job_id | happy path |
| `test_trigger_requires_admin_auth` | non-admin JWT | 403 | authz |
| `test_dlq_lists_failed_jobs` | 2 DLQ entries | GET returns both | visibility |
| `test_retry_requeues_failed_job` | POST /retry on DLQ job | job status returns to todo | re-enqueue |
| `test_retry_idempotent_on_already_requeued` | call twice | second call no-op success | safety |

### 8.6 Observability

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_queue_depth_metric_exported` | 100 pending tasks | `procrastinate_queue_depth{queue="compute"}=100` | metric works |
| `test_task_duration_histogram_recorded` | task takes 250ms | histogram sample in bucket | latency |
| `test_dlq_size_metric` | 5 failed jobs | `procrastinate_dlq_size=5` | visibility |
| `test_alert_fires_on_dlq_over_50` | synthetic 51 failures for 15min | alert condition true | alerting |

### 8.7 Integration (full path)

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_full_create_chart_path` | POST /charts → wait 30s | chart_reading_view row present, all 6 families populated | end-to-end |
| `test_rule_version_bump_triggers_recompute` | change rule version in DB | recompute_family_workflow enqueues; affected charts re-aggregated | version flow |
| `test_worker_restart_resumes_pending_jobs` | enqueue jobs → kill worker → start new worker | jobs complete | durability |

## 9. EPIC-Level Acceptance Criteria

- [ ] procrastinate integrated; schema applied via Alembic
- [ ] 7 task types implemented: create_chart_workflow, compute_for_source, aggregation_barrier, aggregate_strategy, refresh_reading_view, recompute_family_workflow, backfill_source_workflow
- [ ] Idempotency via lock strings + F2 ON CONFLICT verified
- [ ] Retry strategy: transient retries, permanent → DLQ immediately
- [ ] Barrier pattern works: aggregation waits for compute
- [ ] Dedicated worker pools per queue; Cloud Run Jobs deployed
- [ ] Admin API: trigger / inspect / retry DLQ / purge
- [ ] Grafana dashboard + alert rules live
- [ ] p95 chart-creation workflow latency ≤ 10s at 10k-baseline load
- [ ] Unit test coverage ≥ 90% for workflow modules
- [ ] Runbook merged
- [ ] Temporal migration design doc merged
- [ ] CLAUDE.md updated: "background work uses procrastinate tasks in `src/josi/workflows/tasks/`"

## 10. Rollout Plan

- **Feature flag:** `FEATURE_ASYNC_CREATE_CHART` (default off) — when off, POST /charts still runs inline compute. When on, it defers.
- **Shadow compute:** Y — for first 48h with flag on, workflow runs alongside inline compute; outputs compared for equality; flag back off if divergence > 0.1%.
- **Backfill strategy:**
  - For charts already in DB: no backfill needed — create_chart_workflow only triggers on new charts. For existing charts lacking reading_view, use `backfill_source_workflow` one-off.
- **Rollback plan:**
  1. Set `FEATURE_ASYNC_CREATE_CHART=false`. POST /charts returns to inline compute.
  2. Workers keep draining queue; when empty, pause worker Cloud Run Jobs.
  3. No data corruption possible — idempotent inserts mean partial workflows are safely re-runnable.

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| procrastinate Postgres schema adds write load to primary | Medium | Medium | procrastinate is lightweight (~10 inserts/task); if it dominates, move to separate small PG instance |
| Worker OOM from large fan-out | Medium | Medium | `timeout_seconds` per task; worker memory limit in Cloud Run; chunked fan-out for backfill |
| Barrier retry storm when compute stuck | Medium | Medium | Barrier max_attempts=5 → DLQ; alert; manual intervention |
| Long backfill blocks hot path | Low | High | Separate queue + separate worker pool; compute queue workers untouched |
| Transient vs permanent misclassification | Medium | Medium | Explicit `TransientError`/`PermanentError` hierarchy; code review |
| procrastinate library breaking change | Low | Medium | Pin version; upgrade intentionally with tests |
| DLQ grows unbounded | Low | Medium | Alert at > 50; admin purge endpoint; weekly triage ritual |
| Cold start of worker Cloud Run Job | Medium | Low | Min instances = 1 for hot pools; warmup on boot |
| Idempotency footgun on non-F2 side effects | Medium | High | Task bodies must be idempotent; code review; checklist in CLAUDE.md |

## 12. References

- Master spec: [`docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`](../../../superpowers/specs/2026-04-19-classical-techniques-expansion-design.md)
- Depends on: [F2](../P0/F2-fact-tables.md), [F8](../P0/F8-technique-result-aggregation-protocol.md)
- Enables: [S3](./S3-three-layer-serving-cache.md), [S6](./S6-lazy-compute-strategy.md), [P3-E6-flag](./P3-E6-flag-feature-flagged-rule-rollouts.md)
- procrastinate: https://procrastinate.readthedocs.io/
- Temporal: https://temporal.io/ (P4 upgrade target)
- Transactional outbox / saga patterns: Richardson, *Microservices Patterns*, Ch. 4–6
