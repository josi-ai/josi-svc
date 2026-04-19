---
prd_id: P3-E6-flag
epic_id: E6
title: "Feature-flagged rule rollouts (shadow → 10% → 50% → 100%)"
phase: P3-scale-10m
tags: [#correctness, #experimentation]
priority: must
depends_on: [F4, F13, F8]
enables: [S8]
classical_sources: []
estimated_effort: 2 weeks
status: draft
author: Govind
last_updated: 2026-04-19
---

# P3-E6-flag — Feature-Flagged Rule Rollouts

## 1. Purpose & Rationale

Classical rules evolve. A yoga's activation criteria may tighten (e.g., "Gaja Kesari requires Moon-Jupiter within 5 houses of each other, not arbitrary conjunction"). A dasa system's balance calculation may be corrected. When a rule version bumps (F4), naively promoting the new version everywhere causes:

- User-facing outputs flip overnight — "my Raja Yoga disappeared!" is a support nightmare.
- We have no idea whether the new version is actually better before it ships.
- No rollback path if a bug slips through.

This PRD adds a **staged rollout discipline** on top of F4's rule versioning: every rule bump goes through 4 stages — **shadow**, **10%**, **50%**, **100%** — with statistical quality gates between each.

- **Shadow**: new version computed alongside old version. Outputs diffed. Not shown to users. Used to measure divergence and confidence.
- **10% canary**: bucketed by `chart_id` hash. 10% of charts see new version. Metrics collected: override rate, user thumbs rate, latency.
- **50%**: expand bucket. Validate no regression.
- **100%**: new version is the default; old version deprecated.

Rollback: flip `effective_from` on new version to a future date. Old version resumes for all users instantly. No data loss (every compute row is preserved with its original rule_version; F2).

Each rule version has a **dashboard** showing its current stage, divergence metrics, and override/thumbs rates — so engineers and classical advisors can reason about promotion data, not vibes.

## 2. Scope

### 2.1 In scope
- `rule_rollout` table: per `(rule_id, source_id, version)` rollout stage + percentage.
- Rollout stage enum: `shadow | canary_10 | canary_50 | full_100 | rolled_back`.
- Bucketing: deterministic `chart_id` hash → percentage bucket.
- Shadow compute mode: on rule evaluation, compute both old and new; persist both; return old for user-facing; record divergence.
- Diff computation: per output_shape rules for "do these two outputs agree?" (boolean exact, strength ±0.05, temporal ±1 hr for starts, ±1 day for transits, numeric ±5%).
- Metrics per rule version at each stage: divergence rate, astrologer override rate, user thumbs rate, compute latency.
- Admin API: list rules in flight, promote stage, rollback, view metrics.
- Rollout dashboard (Grafana) per rule or aggregated.
- Promotion guardrails: cannot promote if divergence > threshold without explicit override.

### 2.2 Out of scope
- Automated promotion (human clicks promote button; automation is P4's S8 shadow-compute rule migrations).
- A/B testing framework (F14a + experimentation framework handles that; this PRD is for version rollouts specifically).
- Per-tenant rule overrides (P4).
- UI for non-admin users to toggle (admin-only; classical advisors get access).
- Rollback beyond one version back (must `effective_from`-flip; deep rollback is manual).

### 2.3 Dependencies
- F4 — temporal rule versioning.
- F13 — content-hash provenance.
- F8 — aggregation strategies (shadow divergence compared at aggregation_event level).
- S5 — procrastinate (shadow recompute tasks).

## 3. Technical Research

### 3.1 Staged rollout pattern

Classic progressive rollout. Informed by:
- GitHub's feature-flag patterns
- Google SRE Book Ch. 27 "Reliable Product Launches"
- Flagger / Argo Rollouts for k8s

Adapted to our domain: the "feature" is a rule version. The "metric" is divergence from previous version + override rate + thumbs rate.

### 3.2 Bucketing

Deterministic hash:

```python
def bucket(chart_id: UUID, salt: str) -> float:
    """Returns a deterministic value in [0, 1) for this chart under this rule rollout."""
    h = hashlib.sha256(f"{salt}:{chart_id}".encode()).digest()
    return int.from_bytes(h[:8], "big") / (2**64)
```

Salt per `(rule_id, source_id, version)` prevents correlation across rollouts (otherwise the same users would always be in "canary" across all rules).

Bucket assignment:
- Shadow stage: all charts see shadow; but only old version is surfaced.
- Canary 10: bucket < 0.10 sees new; others see old.
- Canary 50: bucket < 0.50 sees new.
- Full 100: all see new.
- Rolled back: all see old.

### 3.3 Shadow compute mechanics

When a new rule version enters shadow:

1. A shadow-recompute task is enqueued (S5) for every chart that has a `technique_compute` row for the old version.
2. For each chart: compute new version, write `technique_compute` row with new `rule_version`.
3. After compute, write a `rule_shadow_diff` row recording agreement between old and new outputs.

Shadow phase duration: minimum 48 hours. Longer for rare-activation rules (need enough samples).

### 3.4 Divergence metric per output shape

```python
def agrees(old: Any, new: Any, shape_id: str) -> bool:
    match shape_id:
        case "boolean_with_strength":
            return (old.active == new.active
                    and abs((old.strength or 0) - (new.strength or 0)) <= 0.05)
        case "numeric":
            return abs(old.value - new.value) <= max(0.05 * abs(old.value), 1e-9)
        case "numeric_matrix":
            return all(abs(a - b) <= 1 for ra, rb in zip(old.matrix, new.matrix)
                                      for a, b in zip(ra, rb))
        case "temporal_range":
            return (abs((old.start - new.start).total_seconds()) <= 3600 and
                    abs((old.end - new.end).total_seconds()) <= 3600)
        case "temporal_event":
            return abs((old.at - new.at).total_seconds()) <= 86400
        case "temporal_hierarchy":
            # all nested periods agree
            return all(agrees(a, b, "temporal_range")
                       for a, b in zip(old.periods, new.periods))
        case "structured_positions":
            return old.positions == new.positions
        case _:
            return old == new
```

### 3.5 Promotion quality gates

Cannot promote to next stage unless all hold:

1. **Divergence rate < 30%** for shadow (high divergence is fine *if* intentional — but requires explicit reason).
2. **Sample size sufficient** for stage: shadow needs ≥ 1000 charts with the rule activated; canary_10 needs ≥ 100 charts in bucket.
3. **No alerting regression**: compute latency P99 within 20% of baseline; zero increase in DLQ from this rule.
4. **Override rate stable**: astrologer override rate on new version within ±5 pp of old version's rate. (If override rate goes *up*, investigate. If *down*, great.)
5. **Thumbs rate stable**: user thumbs-down rate on AI responses using new version within ±5 pp of baseline.

Override logic: admins can force-promote with `force=true` + reason text. Audit-logged.

### 3.6 Alternatives considered

| Alternative | Rejected because |
|---|---|
| Instant promotion (effective_from = now) | No safety net; already the F4 default; too risky for any rule change |
| LaunchDarkly / split.io | External service; our rule bumps are infrequent; self-hosted is simpler |
| Random assignment (not chart-hashed) | User-visible flipping between versions across sessions; must be sticky |
| User-level bucketing | Some charts are shared or B2B-owned (no user); chart-level is more stable |
| Fully automated promotion | P3 is manual; P4's S8 will auto-promote |

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| Bucket unit | chart_id | Stable; owner-agnostic; works for B2B |
| Bucket salt | per-(rule_id, source_id, version) | Decorrelates rollouts |
| Stages | shadow → 10% → 50% → 100% → rolled_back | Standard progressive pattern |
| Shadow duration | Min 48h; extended by sample-size gate | Statistical minimum + rare-event allowance |
| Promotion authority | admin role; force option with audit | Operational safety |
| Rollback mechanism | Flip `effective_from` to far-future on new version | Uses existing F4; instant; reversible |
| Divergence tolerance | Per-shape (Section 3.4) | Numerical nuance per type |
| Quality gates | Divergence, sample size, latency, override delta, thumbs delta | Five independent signals |
| Metric storage | `rule_shadow_diff` + `aggregation_signal` (F2) | Reuse existing fact infra |
| Dashboard | Grafana | Aligns with P3-E8-obs |

## 5. Component Design

### 5.1 New modules

```
src/josi/services/rule_rollout/
├── __init__.py
├── bucketer.py                # NEW: deterministic chart_id → bucket
├── selector.py                # NEW: "which version does this chart see?"
├── shadow.py                  # NEW: shadow compute orchestration
├── diff.py                    # NEW: per-shape agreement calculator
├── promotion.py               # NEW: gate checks + transitions
└── metrics.py                 # NEW: rollout-specific Prometheus metrics

src/josi/workflows/tasks/
└── shadow_compute.py          # NEW: task that computes shadow version

src/josi/api/v1/controllers/
└── rule_rollout_controller.py # NEW: admin CRUD + promote/rollback
```

### 5.2 Data model additions

```sql
-- Rollout state per rule version
CREATE TABLE rule_rollout (
    rule_id          TEXT NOT NULL,
    source_id        TEXT NOT NULL REFERENCES source_authority(source_id),
    version          TEXT NOT NULL,
    stage            TEXT NOT NULL CHECK (stage IN
                       ('shadow','canary_10','canary_50','full_100','rolled_back')),
    stage_entered_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    bucket_salt      TEXT NOT NULL,
    notes            TEXT,
    promoted_by      UUID REFERENCES "user"(user_id),
    rolled_back_by   UUID REFERENCES "user"(user_id),
    rolled_back_reason TEXT,
    PRIMARY KEY (rule_id, source_id, version),
    FOREIGN KEY (rule_id, source_id, version)
        REFERENCES classical_rule(rule_id, source_id, version)
);

CREATE INDEX idx_rollout_stage ON rule_rollout(stage);

-- Shadow diff log: per-chart comparison of old vs new
CREATE TABLE rule_shadow_diff (
    id                BIGSERIAL PRIMARY KEY,
    chart_id          UUID NOT NULL REFERENCES astrology_chart(chart_id),
    rule_id           TEXT NOT NULL,
    source_id         TEXT NOT NULL,
    old_version       TEXT NOT NULL,
    new_version       TEXT NOT NULL,
    agrees            BOOLEAN NOT NULL,
    old_output_hash   CHAR(64) NOT NULL,
    new_output_hash   CHAR(64) NOT NULL,
    divergence_detail JSONB,
    computed_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    FOREIGN KEY (rule_id, source_id, old_version)
        REFERENCES classical_rule(rule_id, source_id, version),
    FOREIGN KEY (rule_id, source_id, new_version)
        REFERENCES classical_rule(rule_id, source_id, version)
);

CREATE INDEX idx_shadow_diff_rule
    ON rule_shadow_diff(rule_id, source_id, new_version, computed_at DESC);

CREATE INDEX idx_shadow_diff_disagree
    ON rule_shadow_diff(rule_id, source_id, new_version)
    WHERE agrees = false;

-- Aggregate rollup (refreshed hourly via periodic task)
CREATE MATERIALIZED VIEW rule_rollout_metrics AS
SELECT
    rr.rule_id,
    rr.source_id,
    rr.version,
    rr.stage,
    count(DISTINCT sd.chart_id)                              AS shadow_samples,
    count(DISTINCT sd.chart_id) FILTER (WHERE sd.agrees)     AS agreeing,
    count(DISTINCT sd.chart_id) FILTER (WHERE NOT sd.agrees) AS diverging,
    (count(sd.id) FILTER (WHERE NOT sd.agrees)::float
        / nullif(count(sd.id), 0))                           AS divergence_rate,
    -- override + thumbs joined from aggregation_signal
    COALESCE(sig.override_rate, 0)                           AS override_rate,
    COALESCE(sig.thumbs_down_rate, 0)                        AS thumbs_down_rate
FROM rule_rollout rr
LEFT JOIN rule_shadow_diff sd
    ON sd.rule_id = rr.rule_id
   AND sd.source_id = rr.source_id
   AND sd.new_version = rr.version
LEFT JOIN LATERAL (
    SELECT
        AVG(CASE WHEN s.signal_type LIKE 'astrologer_override%' THEN 1 ELSE 0 END) AS override_rate,
        AVG(CASE WHEN s.signal_type = 'user_thumbs_down' THEN 1 ELSE 0 END)        AS thumbs_down_rate
    FROM aggregation_signal s
    JOIN aggregation_event ae ON ae.id = s.aggregation_event_id
    WHERE ae.inputs_hash IN (
        SELECT input_fingerprint FROM technique_compute
        WHERE rule_id = rr.rule_id AND source_id = rr.source_id
          AND rule_version = rr.version
    )
) sig ON TRUE
GROUP BY rr.rule_id, rr.source_id, rr.version, rr.stage,
         sig.override_rate, sig.thumbs_down_rate;

CREATE UNIQUE INDEX idx_rollout_metrics_unique
    ON rule_rollout_metrics(rule_id, source_id, version);
```

### 5.3 Bucketing + selector

```python
# src/josi/services/rule_rollout/bucketer.py

def bucket_for(chart_id: UUID, salt: str) -> float:
    h = hashlib.sha256(f"{salt}:{chart_id}".encode()).digest()
    return int.from_bytes(h[:8], "big") / (2**64)

# src/josi/services/rule_rollout/selector.py

@dataclass(frozen=True)
class VersionSelection:
    version: str
    is_shadow_surface: bool  # True means "old version surfaced, new version computed behind scenes"

async def select_version(
    session: AsyncSession,
    chart_id: UUID,
    rule_id: str,
    source_id: str,
) -> VersionSelection:
    """Decides which rule_version this chart sees for a given (rule, source)."""
    versions = await _load_active_versions(session, rule_id, source_id)
    # versions: list ordered by effective_from desc
    # Each version has a rule_rollout row

    for ver in versions:
        rollout = ver.rollout
        if rollout.stage == "rolled_back":
            continue
        if rollout.stage == "shadow":
            # surface previous version; mark shadow
            return VersionSelection(versions[1].version, is_shadow_surface=True)
        b = bucket_for(chart_id, rollout.bucket_salt)
        match rollout.stage:
            case "canary_10" if b < 0.10:  return VersionSelection(ver.version, False)
            case "canary_50" if b < 0.50:  return VersionSelection(ver.version, False)
            case "full_100":               return VersionSelection(ver.version, False)
            case _:
                continue  # try next (older) version

    # Fallback: oldest active
    return VersionSelection(versions[-1].version, is_shadow_surface=False)
```

### 5.4 Shadow compute task

```python
# src/josi/workflows/tasks/shadow_compute.py

@app.task(queue="compute", retry=retry_5)
async def shadow_compute(
    chart_id: str, rule_id: str, source_id: str,
    old_version: str, new_version: str,
) -> None:
    async with get_session() as s:
        # Compute new version
        engine = get_engine_for_rule(rule_id, source_id)
        new_row = await engine.compute_for_source(
            s, UUID(chart_id), source_id, rule_ids=[rule_id],
            force_version=new_version,
        )
        # Load old row
        old_row = await _load_compute(s, chart_id, rule_id, source_id, old_version)

        # Diff
        shape = await _load_output_shape(s, rule_id, source_id)
        agrees = agrees_fn(old_row.result, new_row.result, shape)

        # Persist diff
        s.add(RuleShadowDiff(
            chart_id=UUID(chart_id),
            rule_id=rule_id, source_id=source_id,
            old_version=old_version, new_version=new_version,
            agrees=agrees,
            old_output_hash=old_row.output_hash,
            new_output_hash=new_row.output_hash,
            divergence_detail=(None if agrees else _detail(old_row.result, new_row.result)),
        ))
        await s.commit()
```

### 5.5 Promotion gates

```python
# src/josi/services/rule_rollout/promotion.py

class PromotionGate(BaseModel):
    divergence_rate: float
    min_samples: int
    override_delta_pp: float
    thumbs_delta_pp: float
    latency_p99_delta_pct: float

GATES: dict[str, PromotionGate] = {
    "shadow_to_10":  PromotionGate(divergence_rate=0.30, min_samples=1000,
                                   override_delta_pp=5, thumbs_delta_pp=5,
                                   latency_p99_delta_pct=20),
    "10_to_50":      PromotionGate(divergence_rate=0.30, min_samples=100,
                                   override_delta_pp=5, thumbs_delta_pp=5,
                                   latency_p99_delta_pct=20),
    "50_to_100":     PromotionGate(divergence_rate=0.30, min_samples=500,
                                   override_delta_pp=5, thumbs_delta_pp=5,
                                   latency_p99_delta_pct=20),
}

async def can_promote(
    session: AsyncSession, rule_id: str, source_id: str, version: str,
) -> PromotionCheckResult:
    rollout = await _load_rollout(session, rule_id, source_id, version)
    metrics = await _load_metrics(session, rule_id, source_id, version)
    gate_key = f"{rollout.stage}_to_{_next_stage(rollout.stage)}"
    gate = GATES[gate_key]

    checks = [
        ("divergence", metrics.divergence_rate <= gate.divergence_rate),
        ("samples", metrics.shadow_samples >= gate.min_samples),
        ("override_delta", abs(metrics.override_delta_pp) <= gate.override_delta_pp),
        ("thumbs_delta", abs(metrics.thumbs_delta_pp) <= gate.thumbs_delta_pp),
        ("latency", metrics.latency_p99_delta_pct <= gate.latency_p99_delta_pct),
    ]
    return PromotionCheckResult(
        can_promote=all(ok for _, ok in checks),
        failing_checks=[name for name, ok in checks if not ok],
        metrics=metrics,
    )
```

### 5.6 Admin API

```
GET  /api/v1/admin/rules/rollouts                    # list in-flight rollouts
GET  /api/v1/admin/rules/{rule_id}/{source_id}/{version}/rollout
GET  /api/v1/admin/rules/{rule_id}/{source_id}/{version}/metrics
POST /api/v1/admin/rules/{rule_id}/{source_id}/{version}/promote
     Body: { "force": false, "reason": "..." }
POST /api/v1/admin/rules/{rule_id}/{source_id}/{version}/rollback
     Body: { "reason": "..." }
POST /api/v1/admin/rules/{rule_id}/{source_id}/{version}/recompute-shadow
```

All require `role=admin`.

### 5.7 Dashboard per rule

Grafana panels (auto-generated from rule metadata; aligns with P3-E8-obs):

1. Stage + time-in-stage
2. Divergence rate (shadow only)
3. Sample count (cumulative)
4. Override rate: this version vs previous
5. Thumbs-down rate: this version vs previous
6. Compute latency P99: this version vs previous
7. Alert state summary

## 6. User Stories

### US-P3-E6-flag.1: As an engineer bumping a rule version, I can put it in shadow mode without affecting users
**Acceptance:** deploying a new `classical_rule` row with `effective_from = now()` + inserting `rule_rollout(stage='shadow')` results in all users seeing the old version while new version is computed in the background.

### US-P3-E6-flag.2: As a classical advisor, I can see divergence between old and new versions of a rule
**Acceptance:** dashboard shows divergence rate within 24h of shadow start.

### US-P3-E6-flag.3: As an admin, I can promote a rule from shadow to 10% canary via API
**Acceptance:** `POST /admin/rules/.../promote` transitions stage; gates checked; audit log entry written.

### US-P3-E6-flag.4: As an admin, if I see a regression, I can rollback instantly
**Acceptance:** `POST .../rollback` sets stage to `rolled_back`; old version surfaces for 100% within 10s (cache invalidated via S3).

### US-P3-E6-flag.5: As an SRE, I cannot accidentally promote a rule that fails quality gates without explicit `force`
**Acceptance:** unforced promote returns 409 with failing check list. `force=true` + reason succeeds and audit-logs.

### US-P3-E6-flag.6: As a user in the 10% canary bucket, my reading is consistent across sessions
**Acceptance:** same chart_id always buckets to same value; rollout promoting 10→50 only moves me if bucket < 0.50.

## 7. Tasks

### T-P3-E6-flag.1: Data model migration
- **Definition:** `rule_rollout`, `rule_shadow_diff`, `rule_rollout_metrics` mv per 5.2.
- **Acceptance:** migration applies; FKs enforced; mv refreshes.
- **Effort:** 1 day
- **Depends on:** F2, F4

### T-P3-E6-flag.2: Bucketer + selector
- **Definition:** Implement `bucket_for`, `select_version` per 5.3.
- **Acceptance:** deterministic under same inputs; distribution uniform (χ² test); correct stage resolution.
- **Effort:** 2 days
- **Depends on:** T-P3-E6-flag.1

### T-P3-E6-flag.3: Diff function per output_shape
- **Definition:** `agrees_fn(old, new, shape_id)` per 3.4; exhaustive coverage of 10 shapes.
- **Acceptance:** unit tests pass; edge cases (None, empty, unicode) handled.
- **Effort:** 2 days
- **Depends on:** F7 complete

### T-P3-E6-flag.4: `shadow_compute` task
- **Definition:** procrastinate task per 5.4; computes new version, writes shadow diff row.
- **Acceptance:** integration test: insert new rule version in shadow → enqueue task for chart → diff row present.
- **Effort:** 2 days
- **Depends on:** T-P3-E6-flag.3, S5 complete

### T-P3-E6-flag.5: Integration with compute path
- **Definition:** Modify `compute_for_source` to call `select_version` before evaluating. When in shadow, both old (surfaced) and new (shadowed) compute paths run.
- **Acceptance:** shadow mode: old result surfaced; new result persisted; diff recorded.
- **Effort:** 2 days
- **Depends on:** T-P3-E6-flag.2, T-P3-E6-flag.4

### T-P3-E6-flag.6: Promotion gates
- **Definition:** `can_promote` per 5.5; `promote` state transition; atomic with audit trail.
- **Acceptance:** gate failures blocked; force override works with reason; audit log row created.
- **Effort:** 2 days
- **Depends on:** T-P3-E6-flag.1

### T-P3-E6-flag.7: Admin API
- **Definition:** Controllers per 5.6. Auth (admin-only). Pydantic schemas.
- **Acceptance:** all 6 endpoints functional; covered by integration tests; openapi docs generated.
- **Effort:** 2 days
- **Depends on:** T-P3-E6-flag.6

### T-P3-E6-flag.8: Cache invalidation on rollback
- **Definition:** On rollback, emit invalidation for all charts that had seen new version. Integrates with S3.
- **Acceptance:** after rollback, cache keys for affected charts invalidated within 30s.
- **Effort:** 1 day
- **Depends on:** T-P3-E6-flag.6, S3 complete

### T-P3-E6-flag.9: Metrics mv refresh job
- **Definition:** procrastinate periodic task refreshing `rule_rollout_metrics` mv hourly.
- **Acceptance:** mv stays within 1 hour of ground truth; refresh takes < 60s at 10M charts.
- **Effort:** 1 day
- **Depends on:** T-P3-E6-flag.1

### T-P3-E6-flag.10: Grafana dashboards
- **Definition:** Dashboards-as-code: per-rule panel set + aggregate panel.
- **Acceptance:** in-flight rollouts visible; stage + metrics panels live.
- **Effort:** 2 days
- **Depends on:** T-P3-E6-flag.9

### T-P3-E6-flag.11: Documentation + runbook
- **Definition:** `docs/markdown/runbooks/rule-rollout.md`. CLAUDE.md section "Rolling out a rule change".
- **Acceptance:** doc merged; dry-run of rollout by author follows runbook successfully.
- **Effort:** 1 day
- **Depends on:** T-P3-E6-flag.10

## 8. Unit Tests

### 8.1 Bucketer

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_bucket_deterministic` | same chart_id + salt, 100 calls | identical value | determinism |
| `test_bucket_range` | 10000 random ids | all values in [0,1) | math correct |
| `test_bucket_uniform` | 10000 random ids | χ² test passes (p > 0.05) | no hotspot |
| `test_different_salts_decorrelate` | same id, 2 salts | buckets uncorrelated (|corr| < 0.05) | independence |

### 8.2 Selector

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_shadow_surfaces_previous_version` | new version in shadow, old version full_100 | returns old version, is_shadow=True | shadow UX |
| `test_canary_10_below_bucket` | bucket=0.05, canary_10 | new version | canary logic |
| `test_canary_10_above_bucket` | bucket=0.15, canary_10 | old version | canary logic |
| `test_full_100_returns_new` | full_100 | new version | final stage |
| `test_rolled_back_returns_older` | new rolled_back, old full_100 | old version | rollback |
| `test_missing_rollout_treated_as_full_100` | classical_rule without rollout row | that version returned | back-compat |

### 8.3 Diff (per shape)

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_boolean_same_active_small_strength_delta` | active=True, str=0.7 vs active=True, str=0.73 | agrees | tolerance |
| `test_boolean_different_active` | active=True vs active=False | disagrees | strict boolean |
| `test_numeric_within_5pct` | 100 vs 103 | agrees | numeric tol |
| `test_numeric_outside_5pct` | 100 vs 110 | disagrees | |
| `test_temporal_range_within_1hr` | start±30min, end±30min | agrees | temporal tol |
| `test_temporal_event_within_1day` | at±12h | agrees | event tol |
| `test_temporal_event_over_1day` | at±26h | disagrees | |
| `test_numeric_matrix_within_1_bindu` | matrix differs by 1 in each cell | agrees | ashtakavarga tol |
| `test_structured_positions_exact_required` | house=3 vs house=4 | disagrees | positions strict |

### 8.4 Shadow compute

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_shadow_writes_diff_row` | new version in shadow, chart with old compute | diff row present | orchestration |
| `test_shadow_respects_idempotency` | run shadow twice | 1 diff row | dedup |
| `test_shadow_does_not_surface_new` | shadow_compute then user read | user sees old | surface invariant |
| `test_shadow_records_output_hashes` | shadow diff row | both hashes non-empty | provenance |

### 8.5 Promotion gates

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_promote_denied_on_high_divergence` | divergence=40% | can_promote=False; reason='divergence' | safety |
| `test_promote_denied_on_low_samples` | samples=500, need 1000 | can_promote=False; reason='samples' | statistical |
| `test_promote_allowed_all_green` | all metrics pass | can_promote=True | happy path |
| `test_force_override_allowed` | force=True + reason | promote succeeds; audit row | override |
| `test_force_without_reason_denied` | force=True, reason="" | 422 | require reason |

### 8.6 Admin API

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_list_rollouts_filter_by_stage` | GET ?stage=shadow | only shadow rollouts | filter |
| `test_rollback_invalidates_cache` | POST rollback | cache invalidation enqueued | integration |
| `test_non_admin_forbidden` | non-admin JWT | 403 | authz |
| `test_rollback_to_already_rolled_back_idempotent` | rollback twice | second call 200 no-op | idempotency |

### 8.7 Integration

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_full_shadow_to_canary_to_full` | shadow → canary_10 → canary_50 → full_100 | each transition applies; bucketed reads correct | end-to-end |
| `test_rollback_after_full_reverts_surface` | full_100 → rollback | 100% see old version within 10s | recovery |

## 9. EPIC-Level Acceptance Criteria

- [ ] `rule_rollout`, `rule_shadow_diff`, `rule_rollout_metrics` tables live
- [ ] Deterministic bucketer (uniform distribution, decorrelated salts)
- [ ] `select_version` correctly resolves stage to version
- [ ] Shadow compute task writes diff rows; old surfaces; new persists
- [ ] Promotion gates block unsafe transitions; force+reason override works
- [ ] Rollback restores previous version within 10s (cache invalidation proven)
- [ ] Admin API functional with audit logging
- [ ] Metrics mv refreshes hourly
- [ ] Grafana dashboards render per-rule stage + metrics
- [ ] Runbook merged with dry-run verified
- [ ] Unit test coverage ≥ 90% for new modules
- [ ] CLAUDE.md updated: "every rule bump must enter shadow; see runbook"

## 10. Rollout Plan

- **Feature flag:** `FEATURE_STAGED_ROLLOUT` (default on from day 1 of this PRD — not opt-in, mandatory for new rule versions once built).
- **Shadow compute:** meta-shadow — for the first rule version bump post-deploy, we run the entire staged flow in staging before prod.
- **Backfill strategy:** Existing rule versions are implicitly `full_100`; creating rollout rows with `stage=full_100` for all current versions (idempotent insert).
- **Rollback plan (for this PRD itself):**
  1. Set `FEATURE_STAGED_ROLLOUT=false`.
  2. `select_version` returns `effective_from`-latest (F4 default behavior).
  3. Shadow tasks still run but cease to affect user-facing surfaces.
  4. Cleanly removable; no data corruption.

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Shadow compute doubles compute cost during rollout | High (certain) | Medium | Scoped to rules in shadow; typical concurrent shadows < 5; cost bounded |
| Bucketer hotspotting (bad hash distribution) | Low | High | Property test on distribution; SHA-256 is uniform |
| User flip between versions across sessions | Low | Medium | Bucketing is chart-id deterministic and stage-salted; stable |
| Diff function has bug for an output shape | Medium | High | Exhaustive unit tests per shape; shape-specific review before deploy |
| Admin force-promote abused | Low | High | Audit log; weekly review; alert on force count > 3/week |
| Cache invalidation on rollback incomplete | Medium | High | Use S3 invalidation cascade; monitor via cache hit rate during rollback |
| mv refresh lag during high-rollout periods | Medium | Medium | Refresh every 10 min (not hourly) during active rollouts |
| Divergence alert noise on rare rules | Medium | Low | Minimum sample size gate; rare-rule shadow duration extended |
| Promotion gate too strict → nothing ever ships | Medium | Medium | Gates tuned based on first 10 rollouts; revisit quarterly |

## 12. References

- Master spec: [`docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`](../../../superpowers/specs/2026-04-19-classical-techniques-expansion-design.md)
- Depends on: [F4](../P0/F4-temporal-rule-versioning.md), [F13](../P0/F13-content-hash-provenance.md), [F8](../P0/F8-technique-result-aggregation-protocol.md)
- Enables: [S8](../P4/S8-shadow-compute-rule-migrations.md)
- Google SRE Book, Ch. 27: https://sre.google/sre-book/reliable-product-launches/
- Flagger (progressive delivery): https://flagger.app/
