---
prd_id: E14a
epic_id: E14
title: "Experimentation Framework v1"
phase: P1-mvp
tags: [#experimentation, #correctness, #extensibility]
priority: must
depends_on: [F1, F2, F8, F9, E11a]
enables: [E11b, P3-E8-obs, AI5, Research]
classical_sources: []
estimated_effort: 3 weeks
status: draft
author: @agent
last_updated: 2026-04-19
---

# E14a — Experimentation Framework v1

## 1. Purpose & Rationale

Josi's **north star** is making classical-technique accuracy empirically measurable. The master spec locks in four aggregation strategies (A_majority, B_confidence, C_weighted, D_hybrid) and three signal types (astrologer override, user thumbs, outcome correlation). All four strategies must run in parallel on every chart, every signal must be attributable back to a specific `(strategy, technique_family)`, and a scoreboard must make winners visible.

P0 (F8) ships the `AggregationStrategy` Protocol and the four strategy stubs. E14a **implements** those stubs for every output_shape, builds the post-compute worker that fans out to all strategies, collects the three signal types, and computes the scoreboard.

Without E14a, the star-schema carries no aggregation rows; AI chat has no `aggregation_event_id` to cite (F11 breaks); signals have nothing to attach to; we never learn which strategy wins.

With E14a, every `technique_compute` insert produces four `aggregation_event` rows (one per strategy), the `chart_reading_view` is hydrated from the default strategy's output, signals are captured from three distinct surfaces, and a scoreboard view answers "which strategy is winning for yogas?" out of the box.

## 2. Scope

### 2.1 In scope

- Four strategy implementations in `src/josi/services/classical/aggregation/`:
  - `strategy_a_majority.py`
  - `strategy_b_confidence.py`
  - `strategy_c_weighted.py`
  - `strategy_d_hybrid.py`
- Per-output_shape aggregation logic for all 10 shapes from F7
- Aggregation worker: triggered on any `technique_compute` insert for `(chart_id, rule_id, source_id, rule_version)`; computes all 4 strategies for the `(chart_id, technique_family)`; appends 4 `aggregation_event` rows
- Chart_reading_view updater: on D_hybrid event, upsert the corresponding slice of `chart_reading_view`
- Experiment assignment: `hash(chart_id + experiment_id) % 100` maps to arm via `experiment_arm.allocation_pct` intervals; default 100% D_hybrid (the "control" experiment)
- Signal collection:
  - Implicit astrologer override detector (Python heuristic over rendered text)
  - Explicit `POST /api/v1/ai/signal` for thumbs and outcome reports
  - Chat thumbs plumbing from E11a (delegated signal writes)
- Outcome logging API + model for user-reported outcomes
- Scoreboard view: materialized view grouping signals per `(strategy_id, technique_family_id)`
- Admin read-only endpoints: `GET /api/v1/admin/experiments`, `GET /api/v1/admin/scoreboard`
- Unit + integration tests covering all 4 strategies × all 10 shapes + worker + signal wiring

### 2.2 Out of scope

- **UI for scoreboard dashboard** — P3-E8-obs delivers that; v1 ships a JSON endpoint only
- **Bandit / Bayesian auto-winner** — v1 reports; humans decide
- **Experiment configuration UI** — experiments created via seed YAML / SQL in v1; UI in P3
- **Cross-strategy rollup statistics beyond counts/rates** — p-values, CIs come in P3-E8-obs
- **Statistical significance testing** — v1 surfaces raw rates; significance gating is a P3 concern
- **Real-time websocket updates of scoreboard** — daily refresh is sufficient
- **Astrologer-weights UI** — astrologer-set source_weights are already stored (F2); the UI to set them is E12 (P2)
- **ML-learned weights** — future; v1 only handles fixed-weight strategies

### 2.3 Dependencies

- F1 (strategy and experiment dim tables)
- F2 (`aggregation_event`, `aggregation_signal` fact tables)
- F7 (output_shape JSON schemas)
- F8 (`AggregationStrategy` Protocol)
- F9 (`chart_reading_view` is the downstream consumer of D_hybrid)
- E11a (chat surface generates primary user-signals)
- `usage_service.py` (for per-user signal rate-limiting)

## 3. Technical Research

### 3.1 Aggregation rules per output_shape

The four strategies need concrete reductions for each F7 shape. Below is the canonical semantics table.

| Shape | A_majority | B_confidence | C_weighted | D_hybrid |
|---|---|---|---|---|
| `boolean_with_strength` | majority vote on `active`; arithmetic mean of `strength` | A output + `confidence = agreement_fraction` | weighted vote using `source_weights` | B internals; surface B flattened for end-user; C for astrologer pro |
| `numeric` | arithmetic mean | B output + `confidence = 1 - stddev/mean` (bounded) | weighted mean | B |
| `numeric_matrix` | cell-wise arithmetic mean | B + per-cell confidence | cell-wise weighted mean | B |
| `temporal_range` | span-intersection if >50% overlap; else span-union | B + overlap ratio as confidence | weighted midpoint + span | B |
| `temporal_event` | mode of dates (round to day); mean if continuous | B + `confidence = (count of agreeing sources) / total` | weighted modal date | B |
| `temporal_hierarchy` | level-wise `temporal_range` merge | B per level | C per level | B |
| `structured_positions` | union of positions with majority support | B + per-position confidence | union with weighted significance | B |
| `annual_chart_summary` | field-wise reduction (booleans → majority, numerics → mean) | B + per-field confidence | C per field | B |
| `cross_chart_relations` | intersection of relations present in majority | B + confidence per relation | C per relation | B |
| `categorical` | modal category | B + `confidence = count/total` | weighted vote | B |

All reductions are pure functions of `list[TechniqueResult]` → `AggregatedResult`.

### 3.2 Worker trigger strategy

Three options considered:

1. **DB trigger on technique_compute INSERT** — atomic but binds DB to business logic; hard to unit test; cross-partition triggers are fragile.
2. **Outbox pattern with polling worker** — transactional outbox written in the same txn as compute; worker polls and fans out.
3. **Notify/listen** — low-latency but tied to single worker process.

**Decision:** Outbox + poller. Writes a `technique_compute_outbox` row in the same txn as `technique_compute`. Background worker (asyncio task launched from FastAPI lifespan, with an opt-out to a dedicated process) claims batches, computes all 4 strategies per `(chart_id, technique_family)`, inserts events, updates `chart_reading_view`, deletes outbox row. Idempotent via `UNIQUE (chart_id, technique_family, strategy_id, inputs_hash)` on `aggregation_event`.

P3 may migrate to Temporal / procrastinate (see S5); the outbox row shape is chosen so S5 migration is a pure move-the-consumer change.

### 3.3 Why hash-based assignment (not random)

Hash-based `hash(chart_id + experiment_id)` guarantees:

- Same chart lands in same arm across restarts
- Reproducible for debugging
- No need to persist per-chart assignment rows

Trade-off: cannot hot-swap allocations without re-hashing. Acceptable at P1.

### 3.4 Implicit override detector (heuristic)

"Did the astrologer's rendered text use the auto-computed value?" Detector:

```
given: rendered_text: str, expected_token: str (from auto-compute)
return token_appears(rendered_text, expected_token, fuzz=0.85)
```

Fuzz allows typographic/locale variance. For:

- **Yogas** (`boolean_with_strength`): check if yoga name appears at all in rendered text, and whether positive/negative framing matches expected activation state.
- **Dasa periods**: check if lord + level + within-1-day date window appears.
- **Transits**: check if event name + date window appears.

False positives/negatives tracked; we accept 10-20% noise at v1. The primary-signal weight (astrologer override) is calibrated accordingly.

### 3.5 Alternatives considered

| Alternative | Rejected because |
|---|---|
| Run only D_hybrid, skip A/B/C | Can't measure relative strategy performance → defeats the spec's core thesis |
| Implicit-override detector that parses AST of rendered text | Over-engineered for v1; NLP will be P3 |
| Eager per-request aggregation (no worker) | Doubles chat-path latency; blocks on strategy compute |
| Materialized view refreshed on every insert | Concurrent refresh overhead; scoreboard accuracy to the day is fine |

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| Worker technology | asyncio task from lifespan + outbox table | Simplest; P3 migrates to Temporal via S5 |
| Run all 4 strategies always | Yes | Needed for scoreboard even when 100% D_hybrid is served |
| Default experiment allocation | 100% D_hybrid (`control_experiment`) | Matches master spec decision 1.3 |
| Idempotency key on aggregation_event | `(chart_id, technique_family_id, strategy_id, inputs_hash)` | Composite unique; safe retries |
| Hash or persisted assignment | Hash | Reproducible; no storage overhead |
| Scoreboard refresh cadence | Daily materialized view | Good enough for v1; sub-hour is P3 |
| Outcome signal timing | User-initiated via explicit API | P1 does not actively prompt; E11b may |
| Signal rate-limit per user | 100 signals/day | Stops abuse without hindering legitimate use |
| Override detector language scope | English only | Tamil + others added when E12 astrologer UI ships |
| How does D_hybrid pick which of B/C to flatten for an end-user surface | Surface-level flag on event | Serving layer picks based on `surface` and astrologer preference |
| What happens if only 1 source computed | Emit event with confidence=1.0 and `single_source=true` | Don't block; surface transparency |
| Experiment lifecycle | Seed YAML `experiments.yaml` + Alembic-like migration | Non-engineers can review experiment changes in PRs |

## 5. Component Design

### 5.1 New modules

```
src/josi/services/classical/aggregation/
├── __init__.py
├── base.py                          # AggregationStrategy Protocol re-export from F8
├── strategy_a_majority.py
├── strategy_b_confidence.py
├── strategy_c_weighted.py
├── strategy_d_hybrid.py
├── shapes/                          # per-shape reducers used by strategies
│   ├── __init__.py
│   ├── boolean_with_strength.py
│   ├── numeric.py
│   ├── numeric_matrix.py
│   ├── temporal_range.py
│   ├── temporal_event.py
│   ├── temporal_hierarchy.py
│   ├── structured_positions.py
│   ├── annual_chart_summary.py
│   ├── cross_chart_relations.py
│   └── categorical.py
├── worker.py                        # outbox-polling aggregation worker
├── view_updater.py                  # upserts chart_reading_view from D_hybrid events
└── assignment.py                    # hash-based arm assignment

src/josi/services/classical/signals/
├── __init__.py
├── implicit_override_detector.py
├── signal_writer.py                 # shared by chat + astrologer UIs
└── outcome_service.py

src/josi/services/classical/scoreboard/
├── __init__.py
├── scoreboard_service.py
└── sql/
    └── scoreboard_view.sql

src/josi/models/classical/
└── technique_compute_outbox.py      # new outbox row

src/josi/api/v1/controllers/
├── ai_signal_controller.py          # /api/v1/ai/signal
├── outcome_controller.py            # /api/v1/outcomes
└── admin_experiments_controller.py  # /api/v1/admin/*

src/josi/db/seeds/classical/
└── experiments.yaml                 # seed with `control_experiment`
```

### 5.2 Data model additions

```sql
-- ============================================================
-- technique_compute_outbox: fan-out queue written in same txn as compute
-- ============================================================
CREATE TABLE technique_compute_outbox (
    id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id       UUID NOT NULL REFERENCES organization(organization_id),
    chart_id              UUID NOT NULL REFERENCES astrology_chart(chart_id),
    technique_family_id   TEXT NOT NULL REFERENCES technique_family(family_id),
    enqueued_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    claimed_at            TIMESTAMPTZ,
    claimed_by            TEXT,                                  -- worker id
    attempts              INTEGER NOT NULL DEFAULT 0,
    UNIQUE (chart_id, technique_family_id, claimed_at)           -- one unclaimed per (chart, family)
);

CREATE INDEX idx_outbox_claim
    ON technique_compute_outbox(enqueued_at)
    WHERE claimed_at IS NULL;

-- ============================================================
-- aggregation_event: add uniqueness for idempotent worker retries
-- ============================================================
ALTER TABLE aggregation_event
    ADD CONSTRAINT uq_aggregation_event_idempotent
    UNIQUE (chart_id, technique_family_id, strategy_id, inputs_hash);

-- ============================================================
-- user_outcome_report: user-reported outcome of a past prediction
-- ============================================================
CREATE TABLE user_outcome_report (
    report_id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id        UUID NOT NULL REFERENCES organization(organization_id),
    user_id                UUID NOT NULL REFERENCES "user"(user_id),
    chart_id               UUID NOT NULL REFERENCES astrology_chart(chart_id),
    aggregation_event_id   UUID NOT NULL REFERENCES aggregation_event(id),
    outcome                TEXT NOT NULL CHECK (outcome IN ('positive','negative','neutral')),
    note                   TEXT,
    occurred_on            DATE,
    reported_at            TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_outcome_event ON user_outcome_report(aggregation_event_id);

-- ============================================================
-- scoreboard_view: materialized view for strategy × family rollups
-- ============================================================
CREATE MATERIALIZED VIEW scoreboard_view AS
SELECT
    ae.strategy_id,
    ae.technique_family_id,
    COUNT(*)                                           AS event_count,
    COUNT(DISTINCT ae.chart_id)                        AS distinct_charts,
    COUNT(s.id) FILTER (WHERE s.signal_type = 'user_thumbs_up')                AS thumbs_up,
    COUNT(s.id) FILTER (WHERE s.signal_type = 'user_thumbs_down')              AS thumbs_down,
    COUNT(s.id) FILTER (WHERE s.signal_type = 'astrologer_override_implicit')  AS implicit_override,
    COUNT(s.id) FILTER (WHERE s.signal_type = 'astrologer_override_explicit')  AS explicit_override,
    COUNT(s.id) FILTER (WHERE s.signal_type = 'outcome_positive')              AS outcome_positive,
    COUNT(s.id) FILTER (WHERE s.signal_type = 'outcome_negative')              AS outcome_negative,
    CASE WHEN COUNT(s.id) FILTER (WHERE s.signal_type IN ('user_thumbs_up','user_thumbs_down')) > 0
         THEN COUNT(s.id) FILTER (WHERE s.signal_type = 'user_thumbs_up')::numeric
              / NULLIF(COUNT(s.id) FILTER (WHERE s.signal_type IN ('user_thumbs_up','user_thumbs_down')), 0)
    END                                                AS thumbs_up_rate,
    MAX(ae.computed_at)                                AS last_event_at,
    now()                                              AS refreshed_at
FROM aggregation_event ae
LEFT JOIN aggregation_signal s ON s.aggregation_event_id = ae.id
GROUP BY ae.strategy_id, ae.technique_family_id;

CREATE UNIQUE INDEX idx_scoreboard_key
    ON scoreboard_view(strategy_id, technique_family_id);
```

Refresh: `REFRESH MATERIALIZED VIEW CONCURRENTLY scoreboard_view` every 24h via scheduled job.

### 5.3 Seed experiments

```yaml
# src/josi/db/seeds/classical/experiments.yaml
- experiment_id: control_experiment
  hypothesis: "D_hybrid is a sensible default; measure baseline signals."
  primary_metric: user_thumbs
  status: running
  started_at: 2026-04-20T00:00:00Z
  arms:
    - arm_id: d_hybrid
      strategy_id: D_hybrid
      allocation_pct: 100.00
```

### 5.4 API contract

**Explicit signal (thumbs or override):**

```
POST /api/v1/ai/signal
Body: {
  aggregation_event_id: UUID,
  kind: "thumbs_up" | "thumbs_down" | "astrologer_override_explicit",
  note?: string
}
Response: { success: true, message: "signal recorded", data: { signal_id: UUID } }
```

**Outcome report:**

```
POST /api/v1/outcomes
Body: {
  chart_id: UUID,
  aggregation_event_id: UUID,
  outcome: "positive" | "negative" | "neutral",
  occurred_on?: "YYYY-MM-DD",
  note?: string
}
Response: { success: true, message: "outcome recorded", data: { report_id, signal_id } }
```

The handler writes both a `user_outcome_report` row and a corresponding `aggregation_signal` with `signal_type` `outcome_{positive|negative|neutral}`.

**Admin scoreboard:**

```
GET /api/v1/admin/scoreboard
Query params: technique_family_id?, strategy_id?, since?
Response: {
  success: true,
  data: {
    rows: [
      { strategy_id, technique_family_id, event_count, thumbs_up, thumbs_down,
        thumbs_up_rate, implicit_override, explicit_override,
        outcome_positive, outcome_negative, distinct_charts, last_event_at }
    ],
    refreshed_at: ISO8601
  }
}
```

**Admin experiments:**

```
GET /api/v1/admin/experiments
Response: { success, data: { experiments: [{experiment_id, hypothesis, status, arms: [...]}] } }
```

Both admin endpoints require `current_user.is_staff == true`.

### 5.5 Internal interfaces

```python
# src/josi/services/classical/aggregation/base.py (re-exported from F8)

class AggregationStrategy(Protocol):
    strategy_id: str
    version: str

    def aggregate(
        self,
        results: list[TechniqueComputeRow],
        output_shape: str,
        source_weights: dict[str, float] | None = None,
    ) -> AggregatedResult: ...
```

```python
# src/josi/services/classical/aggregation/worker.py

class AggregationWorker:
    STRATEGIES: list[AggregationStrategy] = [
        StrategyA(), StrategyB(), StrategyC(), StrategyD(),
    ]

    async def run_forever(self) -> None:
        while True:
            batch = await self._claim_batch(limit=50)
            if not batch:
                await asyncio.sleep(0.5)
                continue
            for job in batch:
                await self._process(job)

    async def _process(self, job: OutboxRow) -> None:
        results = await compute_repo.fetch_all_sources(
            job.chart_id, job.technique_family_id,
        )
        assignment = Assignment.for_chart(job.chart_id, experiment="control_experiment")
        for strategy in self.STRATEGIES:
            out = strategy.aggregate(results, shape_of(job.technique_family_id))
            await event_repo.upsert(
                chart_id=job.chart_id,
                technique_family_id=job.technique_family_id,
                strategy_id=strategy.strategy_id,
                experiment_id=assignment.experiment_id,
                experiment_arm_id=assignment.arm_id,
                inputs_hash=hash_inputs(results),
                output=out.to_json(),
            )
        await view_updater.update_from_d_hybrid(job.chart_id, job.technique_family_id)
        await outbox_repo.mark_done(job.id)
```

```python
# src/josi/services/classical/aggregation/assignment.py

class Assignment(NamedTuple):
    experiment_id: str
    arm_id: str

    @classmethod
    def for_chart(cls, chart_id: UUID, experiment: str = "control_experiment") -> "Assignment":
        arms = experiment_arm_repo.for_experiment(experiment)
        bucket = int.from_bytes(
            hashlib.sha256(f"{chart_id}:{experiment}".encode()).digest()[:4],
            "big",
        ) % 10000
        cumulative = 0
        for arm in sorted(arms, key=lambda a: a.arm_id):
            cumulative += int(arm.allocation_pct * 100)
            if bucket < cumulative:
                return cls(experiment, arm.arm_id)
        return cls(experiment, arms[-1].arm_id)  # defensive
```

```python
# src/josi/services/classical/signals/implicit_override_detector.py

class ImplicitOverrideDetector:
    def detect(
        self,
        rendered_text: str,
        aggregation_event: AggregationEvent,
    ) -> OverrideVerdict:
        """
        Returns OverrideVerdict(
          is_override: bool,  # True if auto-value not found in text
          confidence: float,  # detector's self-confidence
          evidence: str,      # matched/missed substrings for debug
        )
        """
```

```python
# src/josi/services/classical/signals/signal_writer.py

class SignalWriter:
    async def record(
        self,
        aggregation_event_id: UUID,
        signal_type: SignalType,
        value: dict | None = None,
        user_id: UUID | None = None,
    ) -> UUID: ...
```

## 6. User Stories

### US-E14a.1: As an engineer, each technique_compute insert triggers all 4 strategies
**Acceptance:** Inserting a `technique_compute` row for `(chart_id_X, technique_family='yoga')` with 3 source rows eventually produces 4 `aggregation_event` rows (one per strategy) and updates the `yoga` slice of `chart_reading_view`.

### US-E14a.2: As a product owner, I can see the scoreboard per strategy × family
**Acceptance:** `GET /api/v1/admin/scoreboard` returns rows for all active `(strategy_id, technique_family_id)` pairs with counts and rates.

### US-E14a.3: As a user, I can thumbs-up a chat response and my signal shows up in the scoreboard the next day
**Acceptance:** After thumbs-up on an assistant message whose citation references `agg_event_X`, the scoreboard row for that `(strategy, family)` shows `thumbs_up += 1` after the next refresh.

### US-E14a.4: As a user, I can report an outcome of a past prediction
**Acceptance:** `POST /api/v1/outcomes` persists a `user_outcome_report` row and a corresponding `aggregation_signal` row with the right `signal_type`.

### US-E14a.5: As an engineer, re-enqueueing the same outbox row twice does not produce duplicate events
**Acceptance:** The `UNIQUE (chart_id, technique_family_id, strategy_id, inputs_hash)` constraint prevents duplicates; worker logs idempotent skip.

### US-E14a.6: As an engineer, when only one source exists for a rule the strategies do not crash
**Acceptance:** All 4 strategies return a valid `AggregatedResult` with `single_source=true` and `confidence=1.0`; no exceptions.

### US-E14a.7: As a product owner, I can launch a new experiment via YAML + migration
**Acceptance:** Adding an entry to `experiments.yaml` with two arms (50/50 A_majority vs D_hybrid) and redeploying routes charts to arms reproducibly.

### US-E14a.8: As an engineer, the implicit override detector flags when an astrologer's rendered text does not reference the auto-computed value
**Acceptance:** Given rendered text that omits the auto-suggested yoga, detector returns `is_override=true`; an `astrologer_override_implicit` signal is written.

## 7. Tasks

### T-E14a.1: Implement 10 shape reducers
- **Definition:** Pure functions per shape, covering A_majority and B_confidence semantics. Type-safe with Pydantic.
- **Acceptance:** Unit tests for every shape with 3 representative multi-source input sets each.
- **Effort:** 4 days
- **Depends on:** F7

### T-E14a.2: Implement strategies A, B, C, D using shape reducers
- **Definition:** Four strategy classes obeying the F8 Protocol. C handles source_weights fallback to Josi defaults when astrologer has no preference. D composes B for end-user and C for astrologer surfaces.
- **Acceptance:** Contract tests: feeding same inputs, A == majority, B carries confidence, C respects weights, D matches B for end-user mode.
- **Effort:** 3 days
- **Depends on:** T-E14a.1, F8

### T-E14a.3: Outbox table + migration
- **Definition:** `technique_compute_outbox` SQLModel + autogenerate migration; `user_outcome_report` + migration; `uq_aggregation_event_idempotent` constraint.
- **Acceptance:** `alembic upgrade head` applies and reverts.
- **Effort:** 0.5 day

### T-E14a.4: Wire outbox write into technique_compute insert
- **Definition:** Extend `BaseEngine.persist()` from F2 scaffolding to also insert outbox row in same txn.
- **Acceptance:** Unit test: inserting a compute row creates exactly one unclaimed outbox row; rolling back txn removes both.
- **Effort:** 0.5 day
- **Depends on:** T-E14a.3

### T-E14a.5: AggregationWorker
- **Definition:** Async worker claiming outbox batches; runs 4 strategies; writes events; delegates to view_updater; marks outbox done; idempotent on retries.
- **Acceptance:** Integration test: 100 outbox rows processed in < 10 s; replay of same batch writes 0 new events.
- **Effort:** 3 days
- **Depends on:** T-E14a.2, T-E14a.4

### T-E14a.6: view_updater
- **Definition:** On D_hybrid event, upserts the slice (yoga / dasa / transits / tajaka / ashtakavarga) in `chart_reading_view`.
- **Acceptance:** Unit tests: each slice updates independently; no cross-slice interference.
- **Effort:** 2 days
- **Depends on:** T-E14a.5, F9

### T-E14a.7: Experiment assignment
- **Definition:** Hash-based allocator honoring `experiment_arm.allocation_pct`. Seed `control_experiment` in `experiments.yaml`.
- **Acceptance:** Property test: for 1000 random chart_ids across 50/50 allocation, split is 50% ± 3%.
- **Effort:** 1 day
- **Depends on:** F1 experiment dim

### T-E14a.8: Signal writer + thumbs handler
- **Definition:** Shared `SignalWriter` used by chat (E11a) and signal controller. `/api/v1/ai/signal` endpoint.
- **Acceptance:** Unit + integration: thumbs-up writes one `aggregation_signal`; rate-limited at 100/user/day.
- **Effort:** 1 day

### T-E14a.9: Outcome controller
- **Definition:** `/api/v1/outcomes` writes `user_outcome_report` + `aggregation_signal` atomically.
- **Acceptance:** Integration test covers positive/negative/neutral.
- **Effort:** 1 day

### T-E14a.10: Implicit override detector
- **Definition:** Python class with per-shape detection rules (English only in v1).
- **Acceptance:** Unit tests on 20 hand-curated (text, event, expected_verdict) tuples; precision > 80%, recall > 70%.
- **Effort:** 2 days

### T-E14a.11: Scoreboard materialized view + refresh job
- **Definition:** Materialized view per schema above; scheduled daily refresh via FastAPI startup-registered `asyncio.create_task` loop.
- **Acceptance:** Unit test asserts view columns; integration test refreshes and checks delta.
- **Effort:** 1 day

### T-E14a.12: Admin scoreboard + experiments endpoints
- **Definition:** Read-only endpoints with `is_staff` guard.
- **Acceptance:** E2E: staff token returns 200 with expected payload; non-staff 403.
- **Effort:** 1 day

### T-E14a.13: Observability + alerts
- **Definition:** Prometheus metrics: `aggregation_worker_batch_latency_seconds`, `aggregation_worker_queue_depth`, `aggregation_events_written_total{strategy, family}`, `signal_write_total{type}`, `scoreboard_refresh_duration_seconds`. Alert on queue depth > 10k for > 5 min.
- **Acceptance:** Metrics exposed and alert rules defined in `deploy/alerts.yml`.
- **Effort:** 1 day

### T-E14a.14: Docs
- **Definition:** `docs/markdown/experimentation/v1.md` covering architecture, strategy semantics, signal wiring, and scoreboard usage.
- **Acceptance:** Reviewed and linked from INDEX.
- **Effort:** 0.5 day

## 8. Unit Tests

### 8.1 Shape reducers (representative)

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_boolean_with_strength_majority_true` | 3 sources: [T,T,F] with strengths [0.8,0.6,0.9] | `active=True, strength=0.77` | majority math |
| `test_numeric_majority_mean` | [10, 12, 14] | 12.0 | arithmetic mean |
| `test_temporal_range_span_intersect` | [(10,20),(12,22),(11,21)] | (12,20) intersection | span-intersection when overlap |
| `test_temporal_range_span_union_on_low_overlap` | [(0,5),(10,15)] | (0,15) | fallback to union |
| `test_numeric_matrix_cellwise_mean` | two 3x3 matrices | cell-wise mean | grid math |
| `test_categorical_modal` | ['a','a','b'] | 'a' | mode |
| `test_temporal_hierarchy_level_wise` | nested periods across 2 sources | merged hierarchy | level recursion |
| `test_structured_positions_union_with_majority` | 3 sources with overlapping positions | union with majority support flag | position semantics |
| `test_annual_chart_summary_field_wise` | 2 tajaka summaries | field-wise reduction | mixed-type reducer |
| `test_cross_chart_relations_intersection` | 3 synastry maps | intersection retained | relation reducer |

### 8.2 Strategies

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_strategy_a_boolean` | 3 yoga results | majority vote | A contract |
| `test_strategy_b_confidence_equals_agreement_fraction` | 3 yogas, 2 agreeing | confidence=0.67 | B contract |
| `test_strategy_c_weighted_overrides_majority` | [T×w0.2, T×w0.3, F×w0.6] | `active=False` (weighted) | C contract |
| `test_strategy_c_uses_astrologer_weights_when_present` | preference with `bphs:1.0, saravali:0.1` | weights applied | astrologer override |
| `test_strategy_c_falls_back_to_source_defaults` | no preference | uses `source_authority.default_weight` | fallback |
| `test_strategy_d_matches_b_for_end_user_surface` | same inputs, surface='b2c_chat' | D output == B output | D contract |
| `test_strategy_d_matches_c_for_astrologer_surface` | same inputs, surface='astrologer_pro' | D output == C output | D contract |
| `test_strategy_single_source_no_crash` | 1 source only | confidence=1.0, single_source=true | edge case |
| `test_strategy_empty_inputs_returns_null_result` | 0 sources | `AggregatedResult(empty=true)` | safety |

### 8.3 AggregationWorker

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_worker_processes_outbox_row` | 1 row, 3 source computes | 4 aggregation_event rows; view slice updated | happy path |
| `test_worker_idempotent_on_retry` | same row re-enqueued | 0 new events (unique constraint) | idempotency |
| `test_worker_advances_on_strategy_error` | B crashes on one row | A,C,D still written; B failure logged with metric | resilience |
| `test_worker_skips_until_batch_ready` | empty outbox | sleeps; no events | control loop |
| `test_worker_honors_experiment_assignment` | chart in 50/50 arm | event rows carry correct arm_id | experiment plumbing |
| `test_worker_persists_single_source_events` | rule with one source computed | 4 events with single_source flag | edge case |

### 8.4 Assignment

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_assignment_deterministic` | same chart_id called twice | same arm both times | reproducibility |
| `test_assignment_distribution_50_50` | 1000 random chart_ids over 50/50 | split 500±30 each | allocation correctness |
| `test_assignment_multi_arm_uneven` | 70/20/10 allocation | splits within ±3% | multi-arm math |
| `test_assignment_all_to_one_arm` | 100/0 allocation | all to the 100% arm | edge case |

### 8.5 Signal path

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_signal_writer_writes_row` | thumbs_up + event_id | one `aggregation_signal` row | basic |
| `test_signal_rate_limit_per_user` | 101st signal same day | 429 | abuse prevention |
| `test_signal_endpoint_requires_auth` | no token | 401 | auth |
| `test_outcome_endpoint_writes_two_rows` | outcome=positive | outcome report + signal row both present | compound write |
| `test_outcome_invalid_chart_mismatch` | aggregation_event's chart != body chart | 400 | consistency |

### 8.6 Implicit override detector

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_detector_yoga_present_in_text` | text mentions yoga + activation consistent | `is_override=false` | accept |
| `test_detector_yoga_missing` | text omits yoga entirely | `is_override=true` | detect |
| `test_detector_dasa_date_within_window` | text mentions "Jupiter Mahadasa" with matching dates | `is_override=false` | acceptable match |
| `test_detector_polarity_flip` | auto says active, text says not active | `is_override=true` | polarity check |
| `test_detector_fuzz_tolerates_typo` | typo in yoga name | match accepted at fuzz ≥ 0.85 | tolerant match |

### 8.7 Scoreboard

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_scoreboard_aggregates_counts` | seed 10 events + 5 signals | row counts match expected | view correctness |
| `test_scoreboard_thumbs_rate` | 3 up, 1 down | thumbs_up_rate == 0.75 | rate math |
| `test_scoreboard_refresh_concurrent` | refresh while reads in-flight | no error; reads still work | concurrency |
| `test_admin_endpoint_staff_gate` | non-staff token | 403 | authZ |

### 8.8 Integration

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_full_path_insert_to_scoreboard` | insert compute → outbox → worker → events → user thumbs → scoreboard refresh | correct rollup row | end-to-end |
| `test_chat_signal_path` | E11a thumbs triggers signal rows | count matches citation count | chat integration |

## 9. EPIC-Level Acceptance Criteria

- [ ] Four strategy implementations pass unit tests for all 10 output_shapes
- [ ] Every `technique_compute` insert produces 4 `aggregation_event` rows via the worker
- [ ] `chart_reading_view` slices update correctly from D_hybrid events
- [ ] `control_experiment` seeded and assignment returns `D_hybrid` for 100% of charts
- [ ] Thumbs + override + outcome signals written via the shared `SignalWriter`
- [ ] Implicit override detector precision > 80%, recall > 70% on fixture set
- [ ] Scoreboard materialized view refreshes daily and queryable via admin endpoint
- [ ] All unit tests green; coverage ≥ 90% on aggregation + signal modules
- [ ] Integration test covers full path compute → aggregation → view → signal → scoreboard
- [ ] Prometheus metrics + queue-depth alert in place
- [ ] Docs published (`docs/markdown/experimentation/v1.md`)
- [ ] CLAUDE.md updated with experimentation surface + admin endpoints

## 10. Rollout Plan

- **Feature flag:** `EXPERIMENTATION_V1_ENABLED` — when off, outbox rows still accumulate but worker does not claim; allows deploying schema before enabling processing. Default on in P1.
- **Shadow compute:** N/A (first version)
- **Backfill:** On enable, seed outbox with one row per existing `(chart_id, technique_family_id)` that has compute data. Backfill job caps at 1000 rows/batch with 1s sleep between batches; tracked via `backfill_run` table (optional; skipped if data volume low).
- **Rollback plan:** Disable flag → worker drains existing outbox, stops claiming new rows. Downgrade migration drops outbox + outcome table; events and signals remain (read-only). `chart_reading_view` remains last-populated (stale but functional).

Rollout sequence:

1. Deploy schema + seed (flag off).
2. Enable worker with 10% of outbox throughput (config cap).
3. Ramp to 100% after 24h of stable metrics.
4. Enable signal endpoints.
5. Enable scoreboard endpoint (staff only).

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Worker backlog under load | Medium | High | Batch size tunable; queue-depth alert; P3 migrates to Temporal (S5) |
| Strategy bug writes bad data into chart_reading_view | Medium | High | view_updater reads only D_hybrid events; event-level idempotency; feature flag to revert to prior view state |
| Implicit override detector has high FP rate | High | Medium | Signal rows tagged with detector version; analytics excludes noisy rows; detector tuned in month 2 |
| Materialized view refresh blocks reads | Low | Medium | `REFRESH ... CONCURRENTLY`; daily off-peak schedule |
| Hash-based assignment skews with small samples | Low | Low | SHA-256 produces uniform distribution empirically; property test catches regressions |
| Strategy C weights sum to zero (astrologer error) | Low | Medium | Normalize; if all zero, fall back to equal weights and log |
| Outbox row leaks on crashed worker | Medium | Medium | `claimed_at` + timeout reaper reclaims after 10 min |
| Scoreboard becomes expensive at 100M events | Low (P1) | Low (P1) | Handled in S4 (OLAP replication) |
| Outcome reports spammed | Low | Low | Signal rate limit + per-chart cap |

## 12. References

- Master spec: [`docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`](../../../superpowers/specs/2026-04-19-classical-techniques-expansion-design.md) §1.3, §1.4
- F1 dims: [`../P0/F1-star-schema-dimensions.md`](../P0/F1-star-schema-dimensions.md)
- F2 facts: [`../P0/F2-fact-tables.md`](../P0/F2-fact-tables.md)
- F7 output shapes: `../P0/F7-output-shape-system.md`
- F8 aggregation Protocol: `../P0/F8-technique-result-aggregation-protocol.md`
- F9 chart_reading_view: [`../P0/F9-chart-reading-view-table.md`](../P0/F9-chart-reading-view-table.md)
- E11a AI chat orchestration: `./E11a-ai-chat-orchestration-v1.md`
- S5 durable workflows (future): `../P3/S5-durable-workflow-orchestration.md`
- Kimball, *The Data Warehouse Toolkit*, Ch. 6 (fact-table aggregations)
