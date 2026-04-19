---
prd_id: S6
epic_id: S6
title: "Lazy compute for non-critical technique families (eager for D1/Vimshottari/active-transit, lazy otherwise)"
phase: P3-scale-10m
tags: [#performance]
priority: must
depends_on: [S5, S3]
enables: []
classical_sources: []
estimated_effort: 2 weeks
status: draft
author: Govind
last_updated: 2026-04-19
---

# S6 — Lazy Compute Strategy

## 1. Purpose & Rationale

By P3 we support 16+ technique families (yoga, multi-dasa systems, ashtakavarga, jaimini, tajaka, transit events, vargas D1–D144, western harmonics, KP, prasna, …). Computing every family eagerly on chart creation is wasteful: 90%+ of charts will never be queried for `prasna` or D144 vargas. Eager compute of all families would take 30–60s per chart and dominate our compute budget at 10M users.

**Policy:**

- **Eager** on chart creation (happens inside S5 `create_chart_workflow`, completes in ~200ms):
  - **D1 / Rasi chart** (positions, houses, lordships).
  - **Vimshottari dasa** (active MD/AD/PD at now).
  - **Active-transit ashtakavarga** (just the currently-transiting planets' bindus — not the full matrix).

- **Lazy** (computed on first access):
  - All other technique families (yoga, full ashtakavarga, jaimini, tajaka, all other dasas, D2–D144, western harmonics, KP, prasna, transit event streams, etc.).

Lazy compute is triggered by any of:
1. API query (`GET /api/v1/charts/{id}/yogas`).
2. AI chat tool-use call (`get_yoga_summary`).
3. UI widget request (Astrologer Workbench tab).

If the family isn't yet computed, the caller gets a `202 Accepted` + a compute job_id. The caller either polls (`GET /charts/{id}/compute-status`) or receives a webhook. AI chat auto-retries after 2 seconds transparently.

Additionally, **priority queue based on user engagement**: active users' charts (opened in last 7d) compute ahead of inactive. This keeps UX snappy for the users who care.

Freshness SLO: user sees fresh data within **2s of first access** for **99%** of lazy queries.

## 2. Scope

### 2.1 In scope
- Policy table: which families are eager, which lazy.
- Compute tracker: `chart_compute_status` table — per-(chart, family) status.
- Lazy trigger: API middleware and AI tool-use handler that enqueue compute when data missing.
- Priority queue routing: procrastinate (S5) queue selection based on user engagement score.
- User engagement score computation: `user_engagement_score` derived from last-login recency, session count.
- Status API: `GET /api/v1/charts/{id}/compute-status` returns per-family state.
- Webhook: `POST` to registered URL when lazy compute completes.
- AI chat integration: tool handler polls internally (1s, 2s) before returning `compute_pending` to LLM.
- Backfill: one-off workflow to pre-compute lazy families for top 1% most-active charts.

### 2.2 Out of scope
- Materialized subsets within a family (e.g., "compute only yoga X.Y") — compute at family granularity.
- Per-strategy laziness — all 4 strategies compute together per family.
- Speculative prefetch based on predicted access — future enhancement.
- Cross-family dependency resolution (e.g., "computing yoga requires D9 varga first") — handled internally by engine, transparent to S6.
- Compute prioritization based on subscription tier — not in P3.

### 2.3 Dependencies
- S5 — durable workflow orchestration; lazy compute enqueues procrastinate tasks.
- S3 — serving cache; lazy compute populates L1/L2 after completion.
- F9 — `chart_reading_view` records per-family freshness.

## 3. Technical Research

### 3.1 Why "eager D1 + Vimshottari + active-transit ashtakavarga"

These three are the floor of any useful reading:
- **D1 / Rasi**: positions are table stakes; almost every downstream calc depends on them.
- **Vimshottari active period**: "which dasa am I in right now?" is the #1 B2C question; computing MD/AD/PD is cheap (~20ms) and bounded.
- **Active-transit ashtakavarga**: tells us whether current transits are benefic or malefic; ~80ms to compute the 7 transiting planets' bindus for the birth ashtakavarga.

Total eager budget: **~200ms**. Fits inside the synchronous chart-creation request (user sees chart immediately).

Everything else can wait until actually requested.

### 3.2 Lazy trigger points

The trigger is the read path. Three entry points:

1. **REST API**: middleware inspects the route; if it maps to a lazy family and data is absent, enqueue + 202.
2. **AI tool-use**: tool handler checks freshness; if absent, enqueue, poll twice with 1s delay, then return `{"status": "computing", "eta_seconds": 2}` if still pending.
3. **GraphQL**: field-level resolver checks freshness; returns `pending` union type if absent.

Trigger is idempotent: enqueueing same compute twice is a no-op (lock strings from S5).

### 3.3 Priority queue routing

Procrastinate supports multiple queues with dedicated workers. We define:

- `compute_hi` — high-priority; 20 worker concurrency; target 2s P99.
- `compute_med` — medium; 10 concurrency; target 10s P99.
- `compute_lo` — backfill / infrequent; 5 concurrency; target <5min.

Routing rule based on `user_engagement_score`:
- Score ≥ 0.7 (active in last 7 days): `compute_hi`.
- Score 0.3–0.7 (active in last 30 days): `compute_med`.
- Score < 0.3 (inactive >30d) or no user associated (B2B API): `compute_lo`.

### 3.4 AI chat transparent retry

```python
# tool handler for get_yoga_summary
async def get_yoga_summary(chart_id: str, strategy: str = "D_hybrid"):
    value = await serving_cache.get(chart_id, "yoga", strategy, session)
    if value is not None:
        return value

    # trigger lazy compute
    await trigger_lazy_compute(chart_id, family_id="yoga")

    # poll twice with 1s delay (total 2s budget)
    for _ in range(2):
        await asyncio.sleep(1.0)
        value = await serving_cache.get(chart_id, "yoga", strategy, session)
        if value is not None:
            return value

    # still pending — return structured pending marker
    return YogaSummary(
        status="computing",
        eta_seconds=10,
        active_yogas=[],
        note="This chart's yoga analysis is being computed. Please ask again in a moment.",
    )
```

LLM is trained via prompt to handle `status=computing` gracefully ("I'm still computing that; give me a moment"). The user sees a natural "hold on, computing…" message, and a follow-up question 5 seconds later succeeds.

### 3.5 Status API

```
GET /api/v1/charts/{id}/compute-status
Response:
{
  "chart_id": "...",
  "status_by_family": {
    "yoga":          { "status": "fresh",     "last_computed_at": "..." },
    "dasa":          { "status": "fresh",     "last_computed_at": "..." },
    "transit_event": { "status": "computing", "enqueued_at": "...", "eta_seconds": 3 },
    "tajaka":        { "status": "stale",     "last_computed_at": "...", "reason": "rule_version_bumped" },
    "jaimini":       { "status": "never_computed" },
    ...
  }
}
```

### 3.6 Backfill strategy for top-active charts

Nightly job: identify top 1% most-active charts (1M charts if 100M total users — at P3 ceiling). For each, enqueue `compute_lazy_families` on `compute_lo` queue. Ensures next-day access is warm.

Engagement source: `user_sessions` table (last 30 days) + chart ownership mapping.

### 3.7 Alternatives considered

| Alternative | Rejected because |
|---|---|
| Fully lazy (no eager compute) | Worse UX — user sees blank dashboard for seconds after chart creation |
| Fully eager | 30–60s per chart; compute cost untenable at 10M users |
| Tiered by subscription (paid tiers get eager) | Business model decision; complicates tech; revisit in P4 |
| Speculative prefetch based on predicted queries | Premature optimization; need access data first |
| Cache TTL–only (no explicit lazy) | Doesn't solve "never computed" case; still need compute trigger |

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| Which families are eager? | D1, Vimshottari, active-transit ashtakavarga | Minimal floor for useful reading |
| Granularity of lazy | Per-family | Matches cache key + user-visible unit |
| Trigger point | API middleware + AI tool handler + GraphQL resolver | Every read path |
| Compute priority | Engagement score → 3 queues | Active users' experience matters most |
| AI chat handling | Transparent 2s poll then "computing" marker | Natural UX; no hard error |
| 202 semantics | Return compute_job_id + polling URL | Standard REST pattern |
| Webhook support | Yes, optional registration | Integrations / astrologer tooling |
| Engagement score source | Last-login + session count (last 30d) | Existing data, simple |
| Status values | fresh, stale, computing, never_computed | 4-way covers all cases |

## 5. Component Design

### 5.1 New modules

```
src/josi/services/lazy_compute/
├── __init__.py
├── policy.py                 # NEW: eager_families / lazy_families / routing
├── trigger.py                # NEW: trigger_lazy_compute() idempotent enqueue
├── status_tracker.py         # NEW: per-family status queries
├── engagement_score.py       # NEW: compute score, cache in Redis
└── backfill.py               # NEW: top-1% backfill job

src/josi/api/v1/
├── middleware/
│   └── lazy_compute_middleware.py  # NEW: intercepts read routes
└── controllers/
    └── compute_status_controller.py  # NEW: GET /charts/{id}/compute-status
```

### 5.2 Data model additions

```sql
-- Per-(chart, family) compute status
CREATE TABLE chart_compute_status (
    chart_id            UUID NOT NULL REFERENCES astrology_chart(chart_id) ON DELETE CASCADE,
    technique_family_id TEXT NOT NULL REFERENCES technique_family(family_id),
    status              TEXT NOT NULL CHECK (status IN
                          ('fresh','stale','computing','never_computed')),
    last_computed_at    TIMESTAMPTZ,
    enqueued_at         TIMESTAMPTZ,
    last_rule_version   TEXT,                  -- bump → stale
    job_id              BIGINT,                 -- procrastinate job id
    eta_seconds         INT,
    PRIMARY KEY (chart_id, technique_family_id)
);

CREATE INDEX idx_compute_status_computing
    ON chart_compute_status(enqueued_at)
    WHERE status = 'computing';

-- Webhooks (optional per user)
CREATE TABLE compute_completion_webhook (
    id             BIGSERIAL PRIMARY KEY,
    user_id        UUID NOT NULL REFERENCES "user"(user_id) ON DELETE CASCADE,
    url            TEXT NOT NULL,
    secret         TEXT NOT NULL,          -- HMAC signing key
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_success_at TIMESTAMPTZ,
    last_failure_at TIMESTAMPTZ,
    failure_count  INT NOT NULL DEFAULT 0
);

-- Engagement score materialized view (refreshed hourly)
CREATE MATERIALIZED VIEW user_engagement_score AS
SELECT
    u.user_id,
    CASE
        WHEN MAX(s.created_at) > now() - INTERVAL '7 days'  THEN 1.0
        WHEN MAX(s.created_at) > now() - INTERVAL '30 days' THEN 0.5
        ELSE 0.0
    END                                                 AS recency_score,
    COUNT(s.session_id) FILTER (WHERE s.created_at > now() - INTERVAL '30 days')
        / 30.0                                          AS frequency_score,
    CURRENT_TIMESTAMP                                   AS computed_at
FROM "user" u
LEFT JOIN user_session s ON s.user_id = u.user_id
GROUP BY u.user_id;

CREATE UNIQUE INDEX idx_engagement_user
    ON user_engagement_score(user_id);
```

### 5.3 Policy table

```python
# src/josi/services/lazy_compute/policy.py

EAGER_FAMILIES: set[str] = {
    "rasi_d1",
    "vimshottari_active",
    "transit_ashtakavarga_active",
}

LAZY_FAMILIES: set[str] = {
    "yoga",
    "dasa_full",
    "ashtakavarga_full",
    "jaimini",
    "tajaka",
    "transit_event",
    "kp",
    "prasna",
    "vargas_extended",
    "western_lot",
    "western_fixed_star",
    "western_harmonic",
    "western_eclipse",
    "synastry",
}

def is_lazy(family_id: str) -> bool:
    return family_id in LAZY_FAMILIES

def priority_queue_for(score: float) -> str:
    if score >= 0.7:
        return "compute_hi"
    if score >= 0.3:
        return "compute_med"
    return "compute_lo"
```

### 5.4 Trigger interface

```python
# src/josi/services/lazy_compute/trigger.py

async def trigger_lazy_compute(
    session: AsyncSession,
    chart_id: UUID,
    family_id: str,
    *,
    user_id: UUID | None = None,
    source_ids: list[str] | None = None,
) -> ComputeTriggerResult:
    """
    Enqueue compute for (chart, family) if not already fresh/computing.
    Returns the current status + job_id.
    """
    current = await _load_status(session, chart_id, family_id)
    if current.status == "fresh":
        return ComputeTriggerResult(status="fresh", job_id=None)
    if current.status == "computing":
        return ComputeTriggerResult(
            status="computing", job_id=current.job_id, eta_seconds=current.eta_seconds
        )

    # Enqueue on appropriate queue
    score = await _get_engagement_score(user_id) if user_id else 0.0
    queue = priority_queue_for(score)

    job_id = await compute_family_workflow.defer_async(
        lock=f"compute:{chart_id}:{family_id}",
        queue=queue,
        chart_id=str(chart_id),
        family_id=family_id,
        source_ids=source_ids,
    )

    # Update status row
    await _set_computing(session, chart_id, family_id, job_id=job_id, eta_seconds=_eta_for(queue))
    return ComputeTriggerResult(status="computing", job_id=job_id, eta_seconds=_eta_for(queue))


def _eta_for(queue: str) -> int:
    return {"compute_hi": 2, "compute_med": 10, "compute_lo": 120}[queue]
```

### 5.5 AI tool handler wrapper

```python
# src/josi/services/ai/tool_handlers/yoga_tool.py

async def get_yoga_summary(
    chart_id: str, strategy: str = "D_hybrid", min_confidence: float = 0.0,
) -> YogaSummary:
    session = await get_read_db_session()
    cache = get_serving_cache()

    value = await cache.get(UUID(chart_id), "yoga", strategy, session)
    if value is not None:
        return _filter_confidence(value, min_confidence)

    user_id = current_user_ctx.get().user_id
    trigger = await trigger_lazy_compute(
        session, UUID(chart_id), "yoga", user_id=user_id
    )

    # Poll twice, 1s apart
    for _ in range(2):
        await asyncio.sleep(1.0)
        value = await cache.get(UUID(chart_id), "yoga", strategy, session)
        if value is not None:
            return _filter_confidence(value, min_confidence)

    return YogaSummary(
        status="computing",
        active_yogas=[],
        eta_seconds=trigger.eta_seconds or 10,
        message="Yoga analysis is being computed; please ask again shortly.",
    )
```

### 5.6 Status API

```python
# src/josi/api/v1/controllers/compute_status_controller.py

@router.get("/charts/{chart_id}/compute-status")
async def get_compute_status(
    chart_id: UUID,
    session: ReadDbDep,
    current_user: CurrentUserDep,
) -> ComputeStatusResponse:
    # Authorize: user must own chart or be admin
    ...
    rows = await session.execute(
        select(ChartComputeStatus).where(ChartComputeStatus.chart_id == chart_id)
    )
    return ComputeStatusResponse(
        chart_id=chart_id,
        status_by_family={r.technique_family_id: r.to_response() for r in rows.scalars()},
    )
```

### 5.7 Webhook delivery

On compute completion (end of `compute_family_workflow` task), enqueue `deliver_webhook` task. Fetch user's registered webhook(s); POST with HMAC-signed body:

```json
{
  "event": "compute.completed",
  "chart_id": "...",
  "family_id": "yoga",
  "completed_at": "...",
  "user_id": "..."
}
```

Retry on non-2xx: 30s, 5min, 1hr. Disable webhook after 10 consecutive failures; notify user via email.

### 5.8 Backfill job

```python
# src/josi/services/lazy_compute/backfill.py

async def backfill_top_active_charts(k: int = 10000) -> None:
    """Enqueue lazy family compute for top-k most-active users' charts."""
    async with get_analytical_db_session() as s:
        rows = await s.execute(
            text(
                """
                SELECT c.chart_id
                FROM astrology_chart c
                JOIN user_engagement_score e ON e.user_id = c.owner_user_id
                WHERE e.recency_score >= 0.7
                ORDER BY e.frequency_score DESC
                LIMIT :k
                """
            ),
            {"k": k},
        )
        chart_ids = [r.chart_id for r in rows]

    for chart_id in chart_ids:
        for family in LAZY_FAMILIES:
            await trigger_lazy_compute(
                session=None, chart_id=chart_id, family_id=family,
                user_id=None,  # force compute_lo queue
            )
```

Scheduled daily via procrastinate periodic task.

## 6. User Stories

### US-S6.1: As a new user creating a chart, I see my D1 chart and current dasa within 1 second of POSTing
**Acceptance:** p95 `POST /charts` → response containing D1 + active Vimshottari + active-transit ashtakavarga ≤ 1s.

### US-S6.2: As an active user opening the Yogas tab, I see results within 2 seconds on first visit
**Acceptance:** p99 time from `GET /charts/{id}/yogas` (first access) → 200 with data ≤ 2s.

### US-S6.3: As an AI chat user, my question "what yogas are active in my chart?" works even if yogas haven't been computed
**Acceptance:** chat response arrives within 3s; if compute takes longer, user sees "I'm computing that; ask in a moment" and follow-up succeeds within 10s.

### US-S6.4: As an inactive user (no login in 60d) opening a chart, I can still see yogas but may wait longer
**Acceptance:** compute queued on `compute_lo`; P99 latency ≤ 2 min.

### US-S6.5: As a developer, I can see per-family compute state for any chart via an API
**Acceptance:** `GET /charts/{id}/compute-status` returns full breakdown.

### US-S6.6: As an integrator, I can register a webhook and receive notifications when compute completes
**Acceptance:** webhook POSTed with HMAC-signed body within 10s of compute completion.

### US-S6.7: As a product manager, top-active users see instant results for all lazy families thanks to nightly backfill
**Acceptance:** after backfill, 99% of top 1% users have all lazy families marked `fresh`.

## 7. Tasks

### T-S6.1: `chart_compute_status` table + tracker
- **Definition:** Migration per 5.2. `StatusTracker` helper class with `load`, `set_computing`, `set_fresh`, `set_stale`.
- **Acceptance:** CRUD works; idempotent upsert; composite PK enforced.
- **Effort:** 2 days
- **Depends on:** F9 complete

### T-S6.2: Policy module
- **Definition:** `policy.py` with EAGER/LAZY sets and `priority_queue_for`.
- **Acceptance:** unit tests cover all 3 queue bands and family classification.
- **Effort:** 0.5 day
- **Depends on:** nothing

### T-S6.3: `user_engagement_score` materialized view
- **Definition:** Migration; scheduled refresh every hour via procrastinate periodic task; cached in Redis (`engagement:{user_id}`, 1h TTL).
- **Acceptance:** view refreshes; Redis cached; synthetic low/med/high-engagement users produce correct scores.
- **Effort:** 1 day
- **Depends on:** nothing

### T-S6.4: `trigger_lazy_compute` function
- **Definition:** Idempotent enqueue per 5.4. Integrates with S5 tasks.
- **Acceptance:** calling twice with same (chart, family) enqueues once. Returns correct status + eta. Routes to correct queue.
- **Effort:** 2 days
- **Depends on:** T-S6.1, T-S6.2, T-S6.3, S5 complete

### T-S6.5: Modify S5 tasks to update status_tracker
- **Definition:** `compute_family_workflow` updates `chart_compute_status` before start (computing), after success (fresh), after failure (stale + keep last_computed_at).
- **Acceptance:** status transitions observable; after failure, next trigger re-enqueues.
- **Effort:** 1 day
- **Depends on:** T-S6.4

### T-S6.6: API middleware for REST routes
- **Definition:** Lightweight middleware: if route path matches lazy pattern (`/charts/{id}/(yogas|dasa|...)`), check status; if not fresh, call trigger + return 202 with `Location: /charts/{id}/compute-status`.
- **Acceptance:** first GET returns 202; subsequent GET after compute returns 200.
- **Effort:** 2 days
- **Depends on:** T-S6.4

### T-S6.7: AI tool-use integration
- **Definition:** Wrap tool handlers per 5.5. Add "status=computing" branch to all 6 tool shape Pydantic models.
- **Acceptance:** LLM sees `status=computing` when data not ready; tool returns value within 2s when data is ready.
- **Effort:** 3 days
- **Depends on:** T-S6.4, S3 complete

### T-S6.8: `GET /charts/{id}/compute-status` endpoint
- **Definition:** Controller per 5.6.
- **Acceptance:** returns all families' statuses; auth enforced; integration test passes.
- **Effort:** 1 day
- **Depends on:** T-S6.5

### T-S6.9: Webhook registration + delivery
- **Definition:** CRUD for `compute_completion_webhook`. `deliver_webhook` task (procrastinate). HMAC signing. Retry policy. Disable after 10 failures.
- **Acceptance:** webhook delivered within 10s of completion; signature verifiable; disable-on-failure works.
- **Effort:** 3 days
- **Depends on:** T-S6.5

### T-S6.10: Backfill job
- **Definition:** `backfill_top_active_charts` per 5.8. Scheduled nightly at 02:00 UTC.
- **Acceptance:** synthetic 10k-user dataset → nightly run enqueues correct count; completes within 4 hours.
- **Effort:** 2 days
- **Depends on:** T-S6.4

### T-S6.11: Prometheus metrics + Grafana panels
- **Definition:** Metrics: `lazy_compute_triggers_total{family,queue}`, `lazy_compute_latency_seconds`, `compute_status_gauge{status}`. Panels per family.
- **Acceptance:** dashboards live; alert: P99 `compute_hi` > 3s sustained 15 min.
- **Effort:** 1 day
- **Depends on:** T-S6.5

### T-S6.12: Documentation
- **Definition:** CLAUDE.md section on lazy-compute policy. Runbook `docs/markdown/runbooks/lazy-compute-lag.md`.
- **Acceptance:** merged; team walk-through.
- **Effort:** 0.5 day
- **Depends on:** T-S6.11

## 8. Unit Tests

### 8.1 Policy

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_d1_is_eager` | `is_lazy("rasi_d1")` | False | eager list |
| `test_yoga_is_lazy` | `is_lazy("yoga")` | True | lazy list |
| `test_unknown_family_defaults_to_lazy` | `is_lazy("made_up")` | True | safe default |
| `test_queue_for_active_user` | `priority_queue_for(0.8)` | `"compute_hi"` | routing |
| `test_queue_for_medium_user` | `priority_queue_for(0.5)` | `"compute_med"` | routing |
| `test_queue_for_inactive_user` | `priority_queue_for(0.1)` | `"compute_lo"` | routing |

### 8.2 Trigger

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_trigger_enqueues_when_never_computed` | status=never_computed | procrastinate job enqueued; status→computing | trigger works |
| `test_trigger_noop_when_fresh` | status=fresh | no enqueue; returns fresh | no wasted work |
| `test_trigger_returns_existing_job_when_computing` | status=computing | returns existing job_id | dedup |
| `test_trigger_respects_engagement_queue` | high-engagement user | enqueued on compute_hi | priority routing |
| `test_trigger_inactive_user_lo_queue` | low-engagement user | compute_lo queue | priority routing |
| `test_trigger_idempotent_concurrent` | 2 concurrent calls | exactly 1 enqueue | race safety |

### 8.3 Status transitions

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_status_set_computing` | tracker.set_computing(chart, family, job_id=123) | row status=computing, job_id=123 | state |
| `test_status_set_fresh` | tracker.set_fresh after computing | status=fresh, last_computed_at set | state |
| `test_status_set_stale_on_rule_bump` | rule version bump | existing rows → stale | F4 integration |
| `test_status_fresh_after_rule_bump_and_recompute` | stale → trigger → compute → set_fresh | status=fresh, last_rule_version updated | recovery |

### 8.4 AI tool handler

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_tool_returns_cached_value_fast` | cache hit | returns value; no trigger, no sleep | fast path |
| `test_tool_triggers_then_polls` | cache miss; compute completes at 1.2s | returns value after 1 sleep cycle | polling works |
| `test_tool_returns_pending_after_timeout` | compute takes >3s | returns status=computing | graceful fallback |
| `test_tool_second_call_gets_value` | after pending marker, compute completes, retry | returns value | eventual consistency |

### 8.5 API middleware

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_middleware_returns_202_on_first_access` | GET /charts/{id}/yogas with status=never_computed | 202 + Location header | lazy 202 |
| `test_middleware_returns_200_when_fresh` | GET /charts/{id}/yogas with status=fresh | 200 + data | hot path |
| `test_middleware_ignores_eager_routes` | GET /charts/{id}/rasi | 200 directly (no status check) | eager skip |

### 8.6 Webhook delivery

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_webhook_signed_body` | delivery | X-Josi-Signature header with HMAC | security |
| `test_webhook_retries_on_500` | first POST fails 500 | retries with backoff; succeeds on 2nd | resilience |
| `test_webhook_disabled_after_10_failures` | 10 consecutive failures | webhook row `failure_count=10`, disabled flag set | safety |
| `test_webhook_only_on_success` | compute fails | no delivery | correctness |

### 8.7 Backfill

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_backfill_picks_top_k_active` | 1000 users with varying scores | top 100 picked | correctness |
| `test_backfill_enqueues_on_lo_queue` | backfill run | all tasks on compute_lo | priority |
| `test_backfill_skips_already_fresh` | chart with all families fresh | no enqueues | efficiency |

### 8.8 Engagement score

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_engagement_recent_login_gives_high_score` | login today | score ≥ 0.7 | recency |
| `test_engagement_no_login_30d_gives_low_score` | no logins in 60d | score < 0.3 | decay |
| `test_engagement_cached_in_redis` | first call computes, second reads cache | 1 DB query, 1 Redis hit | perf |

## 9. EPIC-Level Acceptance Criteria

- [ ] Policy table defines eager and lazy families; tests enforce list stability
- [ ] `chart_compute_status` table migrated; transitions covered by unit tests
- [ ] `trigger_lazy_compute` idempotent + engagement-aware
- [ ] S5 tasks update status on start/success/failure
- [ ] AI tool handlers implement 2s poll + "computing" marker
- [ ] API middleware returns 202 for lazy first access
- [ ] `GET /charts/{id}/compute-status` live
- [ ] Webhook registration + HMAC-signed delivery + retry + disable-on-failure
- [ ] Nightly backfill enqueues top 1% active charts
- [ ] P95 eager compute (D1 + Vim + active ashtakavarga) ≤ 200ms in chart creation path
- [ ] P99 lazy compute on `compute_hi` ≤ 2s end-to-end (trigger → result available)
- [ ] 99% of lazy queries resolve within 2s for active users
- [ ] Unit test coverage ≥ 90% for new modules
- [ ] Runbook merged; CLAUDE.md updated with policy

## 10. Rollout Plan

- **Feature flag:** `FEATURE_LAZY_COMPUTE` (default off) — when off, everything is eager (fallback to P1/P2 behavior).
- **Shadow compute:** N — this changes the production behavior; shadow doesn't fit. Instead, canary:
  1. Enable flag for 1% of users (hash-based bucketing).
  2. Monitor: eager compute latency, lazy queue depth, user-visible errors, AI chat satisfaction.
  3. If metrics green for 7 days: promote to 10%, then 50%, then 100%.
- **Backfill strategy:**
  - Existing charts have status=`never_computed` for all lazy families.
  - On first access, trigger fires.
  - Alternative: one-off full-backfill of top 10% charts to pre-warm (optional; reassess after week 1).
- **Rollback plan:**
  1. Set `FEATURE_LAZY_COMPUTE=false`. API middleware skips; tool handlers compute synchronously.
  2. Workers keep draining queues; no data corruption.
  3. If chart_compute_status breaks, truncating it resets to `never_computed` safely (triggers will re-enqueue).

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| First-access latency spikes from thundering herd on popular charts | Medium | Medium | Stampede guard in trigger (idempotent enqueue); worker concurrency scales with queue depth |
| Inactive user has bad UX because of `compute_lo` queue | Medium | Low | If user is active enough to hit the API, they get re-scored; long-term they migrate to `compute_med` |
| AI chat "computing" fallback feels awkward to users | Medium | Low | Product copy tested; natural phrasing; data returns on next turn |
| Status table bloat (10M charts × 16 families = 160M rows) | Medium | Medium | Prune rows for soft-deleted charts via cascade; partition by chart_id hash if > 500M rows |
| Engagement score mv refresh slow | Low | Medium | Concurrent refresh (`REFRESH MATERIALIZED VIEW CONCURRENTLY`); alert on refresh > 10min |
| Webhook endpoint abuse / SSRF | Medium | High | URL validation (no private IPs); HMAC-only; timeout 5s; rate-limit per user |
| Compute queue starvation (lo never runs when hi always full) | Low | Medium | Each queue has dedicated workers; lo can't be starved by hi |
| User confused by 202 response | Medium | Low | Doc clearly; frontend handles via polling |
| Backfill storm overwhelms replicas | Low | Medium | Compute_lo worker concurrency capped; rate-limited via semaphore |

## 12. References

- Master spec: [`docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`](../../../superpowers/specs/2026-04-19-classical-techniques-expansion-design.md)
- Depends on: [S5](./S5-durable-workflow-orchestration.md), [S3](./S3-three-layer-serving-cache.md), [F9](../P0/F9-chart-reading-view-table.md)
- Laziness patterns: classical OS virtual memory paging — compute on page fault
- HTTP 202 semantics: RFC 7231 §6.3.3
