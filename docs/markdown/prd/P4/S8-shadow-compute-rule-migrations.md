---
prd_id: S8
epic_id: S8
title: "Shadow-compute rule migrations (1% shadow → promoted rollout)"
phase: P4-scale-100m
tags: [#correctness, #experimentation]
priority: must
depends_on: [F4, F6, F13, P3-E6-flag, S4]
enables: [P4-E4-tenant, Reference-1000]
classical_sources: []
estimated_effort: 3-4 weeks
status: draft
author: "@agent"
last_updated: 2026-04-19
---

# S8 — Shadow-Compute Rule Migrations

## 1. Purpose & Rationale

At 100M users a rule change — even a trivial-looking bug fix bumping `bphs/gaja_kesari@1.0.0` to `1.0.1` — touches tens of millions of chart-reading-views, drives AI responses, and influences astrologer override rates. Rolling it out naively is unacceptable for three reasons:

1. **Silent correctness regressions.** A "bug fix" can introduce a new bug; we need to see the output diff before committing.
2. **Unexpected blast radius.** A fix to one yoga can affect 30M charts if the yoga is common, or 30 charts if rare — we do not know until we measure.
3. **Astrologer trust.** Pro-mode astrologers configure preferences per source; changing what a source "means" without telling them erodes confidence.

P3-E6-flag introduced shadow → 10% → 50% → 100% flag-controlled rollouts. That works for *enabling* a rule. This PRD extends it to *version migrations*: when v1.0.1 supersedes v1.0.0, both run in parallel in shadow, outputs are compared row-by-row, divergence is classified, and only then does the new version progress.

The end state: every rule migration produces a public audit record like:

> *"Rule `bphs/gaja_kesari` promoted from v1.0.0 to v1.0.1 on 2026-07-15 14:22 UTC. Shadow window: 7 days. Charts affected by behavior change: 2,341,567 of 87,210,988 shadowed (2.7%). Divergence classification: 100% 'expected' (matches bug report #4521: kendra check incorrectly excluded 4th house). 0% 'unexpected'. Rollout: 1% → 10% (2026-07-16) → 50% (2026-07-18) → 100% (2026-07-22)."*

This PRD makes that audit and the control plane that produces it.

## 2. Scope

### 2.1 In scope

- Shadow execution mode for rule versions: v_new computes alongside v_old, results stored in `technique_compute_shadow`
- 1% sampling strategy for shadow (deterministic, org-id hashed; not random)
- Automated output comparison and divergence classification
- Expected vs unexpected divergence taxonomy (bug-report-matched vs surprise)
- Admin UI for reviewing shadow diffs and approving / aborting rollouts
- Promotion pipeline: shadow → 1% → 10% → 50% → 100% with gates at each step (extends P3-E6-flag)
- Chart-level audit trail tying every user-visible change to a promotion event
- Rollback: revert promotion and re-compute affected charts with v_old
- Integration with S4 so shadow comparisons run in BigQuery (scale)
- Integration with P3-E8-obs so divergence metrics live on dashboards
- Alerts: unexpected divergence exceeding threshold halts rollout automatically

### 2.2 Out of scope

- Shadow for **new** rules (no v_old to compare against) — handled by P3-E6-flag directly
- Shadow for schema migrations of `technique_compute` itself — handled by Alembic + CDC backfill (S4)
- Cross-source comparisons (BPHS yoga output vs Saravali equivalent) — that is C5 differential testing
- Manual rule editing at rollout time — console authoring is P3-E2-console; S8 consumes the output
- Full "AI quality" regression testing of downstream interpretation — covered by E15a
- Rule deprecation / retirement — handled via `effective_to` in F4; S8 only handles version bumps

### 2.3 Dependencies

- **F4** — temporal rule versioning, `effective_from` / `effective_to`, content-hash identifiers
- **F6** — YAML rule loader, so shadow receives rule bodies from the same registry
- **F13** — content-hash provenance for stable diff keys
- **P3-E6-flag** — feature-flag plumbing reused; S8 is a specialization
- **S4** — shadow comparison runs in BigQuery at scale; diff storage may exceed OLTP capacity
- **P3-E8-obs** — dashboards surface divergence metrics

## 3. Technical Research

### 3.1 Shadow vs canary vs blue-green — why shadow?

- **Canary**: users see different results. Unacceptable before we understand divergence.
- **Blue-green**: same — a subset of traffic gets new version. Same objection.
- **Shadow**: new version computes; output is recorded but not served. Users see old version until promotion. This is the only mode compatible with "measure blast radius before exposing users."

We only adopt canary *after* shadow has cleared divergence gates (then it becomes the 1% → 10% → … stages).

### 3.2 Determining what to shadow

Not every compute event shadows: that would double the write load during rollout. Strategy:

- **Sampling:** `org_id` hash mod 100 == N → shadow. Start N=1 (1%); ramp after gates pass.
- **Freshness:** only NEW computes shadow. A chart whose result for `rule_id` is already in cache from v_old is not recomputed for shadow until the chart is naturally invalidated (e.g., chart edited, dependency change per F13).
- **Replay mode** (for completeness): admin-triggered re-computation of historical charts against v_new without affecting user-facing results. Used when a bug fix needs coverage on existing data.

### 3.3 Output diff classification

For every chart in the shadow sample, diff is `(output_hash_old, output_hash_new)`:

- `EQUAL` — no behavioral change for this chart.
- `DIFFERENT — expected` — the diff matches the bug-report description (see §3.4).
- `DIFFERENT — unexpected` — the diff does not match any declared expectation.
- `ERROR` — v_new raised on this chart while v_old succeeded (or vice versa).

Only `EQUAL` and `DIFFERENT — expected` are acceptable at gate time. Any `DIFFERENT — unexpected` halts rollout.

### 3.4 Declared expected-diff predicates

Every rule version bump ships with a YAML `expected_diff` predicate. The predicate must match every `DIFFERENT` row or the gate fails.

**Example:** fixing Gaja Kesari kendra check to include 4th house:

```yaml
# src/josi/db/rules/bphs/gaja_kesari.1.0.1.yaml
rule_id: bphs/gaja_kesari
version: 1.0.1
content_hash: "<sha256>"
supersedes: 1.0.0
migration:
  bug_report: "Issue #4521: Gaja Kesari incorrectly excluded 4th house from kendra check"
  expected_diff:
    # A row is 'expected divergent' iff ALL predicates match.
    - path: "$.active"
      change: "false → true"
      condition: |
        # Moon in 4th from Jupiter OR Jupiter in 4th from Moon,
        # other kendra conditions not met in v_old.
        chart.planet_house[moon] == (chart.planet_house[jupiter] + 3) % 12
        OR chart.planet_house[jupiter] == (chart.planet_house[moon] + 3) % 12
    - path: "$.reason"
      change: "contains '4th house kendra' only in v_new"
  expected_rate_min: 0.01
  expected_rate_max: 0.15
```

The `expected_rate_min/max` bounds let us halt rollout if the real divergence rate is outside the hypothesis range — either the bug was bigger than thought, or something else changed too.

### 3.5 Storage scale

At 1% shadow over 100M charts × 5000 rules = 5B shadow rows per week during active rollouts. OLTP cannot absorb this, so shadow rows go to a dedicated lightweight table that is aggressively TTL-cleaned after promotion closes:

```
technique_compute_shadow (PK (chart_id, rule_id, source_id, rule_version), TTL = promotion_ttl_days)
```

Diff computation runs against BigQuery (S4 replicates `technique_compute` + `technique_compute_shadow`). Diff summaries come back to OLTP as `rule_promotion_divergence_summary` (small aggregate rows per promotion).

### 3.6 Where does v_new code live?

Rule bodies are YAML in `src/josi/db/rules/` (F6) and loaded into `classical_rule`. At rollout time, both v1.0.0 and v1.0.1 coexist in the registry with different versions. The rule engine picks the version based on the active promotion flag — not based on "latest." Every compute row records its `rule_version`, so audit is exact.

### 3.7 Alternatives considered

| Alternative | Rejected because |
|---|---|
| Direct promotion without shadow | Silent correctness regression risk unacceptable at 100M users |
| Shadow always at 100% | Doubles compute cost; unnecessary — 1% is statistically sufficient for common rules |
| Manual diff review only | Does not scale beyond 10–20 rule migrations/month; we expect hundreds at Reference-1000 scale |
| Auto-promote on EQUAL-only | Disallows any intentional behavior change (a real bug fix changes outputs!) |
| Blue-green flip with fast rollback | User-facing; even 5-min exposure to a regression is unacceptable for astrologer surfaces |

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| Sampling method | Deterministic `org_id hash mod 100` | Reproducible; no RNG drift; same orgs sampled across restarts |
| Initial shadow rate | 1% for first 24 h, 10% next 48 h, then re-sample at promotion stages | Balance signal vs cost |
| Shadow storage location | OLTP table with aggressive TTL + S4 replication | Primary diff compute in BQ |
| Diff keys | Content hash `(output_hash_old, output_hash_new)` | Stable, cheap, language-agnostic |
| Expected-diff schema | YAML predicate with JSONPath + condition DSL | Co-located with rule; reviewable in PR |
| Predicate DSL | Subset of rule DSL from F6 | Reuse; one language to learn |
| Gate thresholds | Unexpected divergence > 0.1% halts; expected outside declared range halts | Tight but not zero — we allow tiny non-determinism from `NOW()` etc. |
| Chart-level audit | Retained forever via `rule_promotion_event` + `chart_change_log` | Regulatory / trust requirement |
| Who can abort rollout | Any platform engineer + any classical advisor with `rule_promoter` role | Two-key safety; dual control |
| Roll-forward cooldown after abort | 7 days minimum | Forces reflection on root cause |
| How long shadow table retained | 30 days past final promotion decision | Post-mortem window |
| Re-shadow when code changes behavior mid-rollout | Invalidate current promotion, restart shadow | Correctness over speed |

## 5. Component Design

### 5.1 New services / modules

```
src/josi/services/rule_promotion/
├── __init__.py
├── promotion_controller.py       # state machine: draft → shadow → 1% → 10% → 50% → 100% → closed
├── shadow_runner.py               # compute v_new in shadow on sampled charts
├── diff_classifier.py             # compares v_old output_hash to v_new; applies expected_diff predicate
├── expected_diff_parser.py        # parses migration.expected_diff YAML into evaluable predicates
├── divergence_aggregator.py       # rolls up per-promotion stats from BQ
├── gate_evaluator.py              # go/no-go per stage based on divergence stats
└── audit_writer.py                # writes immutable rule_promotion_event rows

src/josi/api/v1/controllers/
└── rule_promotion_controller.py  # REST + GraphQL surface for admin UI

web/app/(admin)/rule-promotions/
├── page.tsx                      # list active / recent promotions
├── [promotion_id]/page.tsx       # detail: divergence stats, diff samples, gate state
└── components/
    ├── PromotionTimeline.tsx
    ├── DivergenceChart.tsx
    ├── DiffSampleTable.tsx
    └── GateApprovalDialog.tsx
```

### 5.2 Data model additions

```sql
-- ============================================================
-- rule_promotion: one row per version migration event
-- ============================================================
CREATE TABLE rule_promotion (
    promotion_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_id               TEXT NOT NULL,
    source_id             TEXT NOT NULL REFERENCES source_authority(source_id),
    from_version          TEXT NOT NULL,    -- e.g., '1.0.0'
    to_version            TEXT NOT NULL,    -- e.g., '1.0.1'
    bug_report_url        TEXT,             -- e.g., GitHub issue link
    expected_diff_spec    JSONB NOT NULL,   -- parsed migration.expected_diff
    current_stage         TEXT NOT NULL CHECK (current_stage IN
                            ('draft','shadow','canary_1','canary_10','canary_50','full','closed','aborted','rolled_back')),
    stage_started_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by            UUID NOT NULL REFERENCES "user"(user_id),
    approved_by           UUID REFERENCES "user"(user_id),     -- second approver per stage
    notes                 TEXT,
    created_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
    closed_at             TIMESTAMPTZ,
    FOREIGN KEY (rule_id, source_id, from_version)
        REFERENCES classical_rule(rule_id, source_id, version),
    FOREIGN KEY (rule_id, source_id, to_version)
        REFERENCES classical_rule(rule_id, source_id, version)
);

CREATE INDEX idx_promotion_active ON rule_promotion(current_stage) WHERE current_stage NOT IN ('closed','aborted','rolled_back');

-- ============================================================
-- rule_promotion_stage_event: history of stage transitions
-- ============================================================
CREATE TABLE rule_promotion_stage_event (
    id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    promotion_id          UUID NOT NULL REFERENCES rule_promotion(promotion_id) ON DELETE CASCADE,
    from_stage            TEXT,                         -- null on initial
    to_stage              TEXT NOT NULL,
    transitioned_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    transitioned_by       UUID REFERENCES "user"(user_id),
    reason                TEXT,                         -- 'automatic_gate_pass' | 'manual_approval' | 'auto_halt_unexpected_diff' | …
    gate_stats_snapshot   JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX idx_promotion_stage_history ON rule_promotion_stage_event(promotion_id, transitioned_at);

-- ============================================================
-- technique_compute_shadow: short-lived sibling of technique_compute
-- ============================================================
CREATE TABLE technique_compute_shadow (
    organization_id      UUID NOT NULL,
    chart_id             UUID NOT NULL,
    rule_id              TEXT NOT NULL,
    source_id            TEXT NOT NULL,
    rule_version         TEXT NOT NULL,
    promotion_id         UUID NOT NULL REFERENCES rule_promotion(promotion_id) ON DELETE CASCADE,
    result               JSONB NOT NULL,
    output_hash          CHAR(64) NOT NULL,
    computed_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (chart_id, rule_id, source_id, rule_version, promotion_id)
);

CREATE INDEX idx_shadow_promotion ON technique_compute_shadow(promotion_id, computed_at DESC);

-- Partitioned by promotion_id for cheap TTL drop.

-- ============================================================
-- rule_promotion_divergence_summary: aggregate diff stats
-- ============================================================
CREATE TABLE rule_promotion_divergence_summary (
    id                       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    promotion_id             UUID NOT NULL REFERENCES rule_promotion(promotion_id) ON DELETE CASCADE,
    window_started_at        TIMESTAMPTZ NOT NULL,
    window_ended_at          TIMESTAMPTZ NOT NULL,
    charts_sampled           BIGINT NOT NULL,
    equal_count              BIGINT NOT NULL,
    different_expected       BIGINT NOT NULL,
    different_unexpected     BIGINT NOT NULL,
    error_count              BIGINT NOT NULL,
    divergence_rate          NUMERIC(5,4) NOT NULL,    -- different_* / sampled
    unexpected_rate          NUMERIC(5,4) NOT NULL,
    created_at               TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_divergence_promotion ON rule_promotion_divergence_summary(promotion_id, window_ended_at DESC);

-- ============================================================
-- chart_change_log: audit of user-visible rule-driven changes
-- ============================================================
CREATE TABLE chart_change_log (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id     UUID NOT NULL,
    chart_id            UUID NOT NULL,
    promotion_id        UUID NOT NULL REFERENCES rule_promotion(promotion_id),
    rule_id             TEXT NOT NULL,
    source_id           TEXT NOT NULL,
    from_output_hash    CHAR(64) NOT NULL,
    to_output_hash      CHAR(64) NOT NULL,
    changed_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_change_log_chart ON chart_change_log(chart_id, changed_at DESC);
CREATE INDEX idx_change_log_promotion ON chart_change_log(promotion_id);
```

**YAML rule migration schema extension** (add to F6):

```yaml
migration:                          # required when supersedes is set
  bug_report: "<free text or URL>"
  supersedes: "<version>"
  expected_diff:
    - path: "<JSONPath into result>"
      change: "<from → to, or predicate>"
      condition: "<rule DSL expression>"  # optional; bounds which charts should see this diff
  expected_rate_min: <float 0..1>
  expected_rate_max: <float 0..1>
  notes: "<free text>"
```

### 5.3 API contract

**Admin REST endpoints:**

```
POST /api/v1/admin/rule-promotions
Body: { rule_id, source_id, to_version, bug_report_url?, notes? }
-> { promotion_id, stage: 'draft' }

POST /api/v1/admin/rule-promotions/{promotion_id}/start-shadow
-> advances to stage 'shadow'; spawns shadow_runner

POST /api/v1/admin/rule-promotions/{promotion_id}/approve-next-stage
Body: { approver_notes: str }
-> advances stage (if gate passes) or returns 409 with reason

POST /api/v1/admin/rule-promotions/{promotion_id}/abort
Body: { reason: str }
-> stage = 'aborted'; rolls back shadow

POST /api/v1/admin/rule-promotions/{promotion_id}/rollback
Body: { reason: str }
-> stage = 'rolled_back'; forces all charts back to from_version; recomputes

GET /api/v1/admin/rule-promotions/{promotion_id}
-> full state + current divergence summary + recent sample diffs

GET /api/v1/admin/rule-promotions?status=active
-> list of in-flight promotions

GET /api/v1/audit/chart/{chart_id}/changes?since=<ts>
-> chart-level change log for user-visible results
```

All admin endpoints require `rule_promoter` role.

**Internal Python:**

```python
# src/josi/services/rule_promotion/promotion_controller.py

class PromotionController:
    async def create(self, rule_id: str, source_id: str, to_version: str,
                     created_by: UUID, bug_report_url: str | None = None) -> Promotion: ...

    async def start_shadow(self, promotion_id: UUID) -> None: ...

    async def evaluate_gate(self, promotion_id: UUID) -> GateDecision:
        """Pulls latest divergence summary; returns PASS | WARN | FAIL with reason."""

    async def advance(self, promotion_id: UUID, approver: UUID) -> Promotion: ...

    async def abort(self, promotion_id: UUID, reason: str) -> None: ...

    async def rollback(self, promotion_id: UUID, reason: str) -> None: ...

# src/josi/services/rule_promotion/diff_classifier.py

@dataclass
class DiffRow:
    chart_id: UUID
    output_hash_old: str
    output_hash_new: str
    classification: Literal['EQUAL','DIFFERENT_EXPECTED','DIFFERENT_UNEXPECTED','ERROR']
    reason: str | None

class DiffClassifier:
    def __init__(self, expected_diff_spec: ExpectedDiffSpec): ...

    async def classify_batch(self, rows: list[tuple[UUID, dict, dict]]) -> list[DiffRow]: ...
```

**BigQuery query (runs via scheduled query every 5 min during promotion):**

```sql
-- computes divergence summary for a single promotion
INSERT INTO `josi_olap.rule_promotion_divergence_summary` ...
SELECT
  @promotion_id, @window_start, @window_end,
  COUNT(*) as charts_sampled,
  COUNTIF(s.output_hash = p.output_hash) AS equal,
  COUNTIF(s.output_hash != p.output_hash
          AND classify_expected(s.result, p.result) = 'expected') AS different_expected,
  COUNTIF(s.output_hash != p.output_hash
          AND classify_expected(s.result, p.result) = 'unexpected') AS different_unexpected,
  ...
FROM `josi_olap.fct_technique_compute_shadow` s
JOIN `josi_olap.v_technique_compute` p USING (chart_id, rule_id, source_id)
WHERE s.promotion_id = @promotion_id
  AND p.rule_version = (SELECT from_version FROM rule_promotion WHERE promotion_id = @promotion_id)
  AND s.computed_at BETWEEN @window_start AND @window_end;
```

## 6. User Stories

### US-S8.1: As a classical advisor, I want to migrate a rule from v1.0.0 to v1.0.1 and see the blast radius before any user sees it
**Acceptance:** after PRing the v1.0.1 YAML and opening a promotion, the admin UI shows divergence stats after ~1 hour of shadow; I can inspect 10 sample diffs; I see a PASS/FAIL verdict with specific counts.

### US-S8.2: As a platform engineer, I want rollouts to auto-halt on unexpected divergence
**Acceptance:** if `different_unexpected / charts_sampled > 0.001`, the promotion controller emits PagerDuty alert and halts stage advancement. No manual intervention needed to stop; manual intervention needed to resume.

### US-S8.3: As a user, I want to know when a chart result changed and why
**Acceptance:** `/api/v1/audit/chart/{chart_id}/changes` returns every rule-driven change to my chart along with promotion URL and bug-report link.

### US-S8.4: As an SRE, I want shadow compute cost bounded
**Acceptance:** during any active rollout, shadow write load is ≤ 1% of production write load (measured in Cloud SQL insert throughput); shadow table grows then drops to zero within 30 days of closure.

### US-S8.5: As product management, I want to roll back a promotion that looked good in shadow but caused astrologer backlash
**Acceptance:** triggering rollback recomputes affected charts back to `from_version`; within 1 hour all `chart_reading_view` rows reflect the pre-promotion state; change log records the rollback event.

### US-S8.6: As QA, I want to replay shadow on historical charts, not just new ones
**Acceptance:** admin CLI `josi promotion replay --promotion-id <uuid> --limit 1M` computes v_new against 1M archived charts and feeds results into divergence summary.

## 7. Tasks

### T-S8.1: Data model migration
- **Definition:** Alembic migration creating `rule_promotion`, `rule_promotion_stage_event`, `technique_compute_shadow` (partitioned by promotion_id), `rule_promotion_divergence_summary`, `chart_change_log`. Includes constraints + indexes.
- **Acceptance:** Migration applies cleanly; downgrade cleanly reverts. FKs to `classical_rule` work.
- **Effort:** 3 days
- **Depends on:** F4

### T-S8.2: Expected-diff YAML schema + parser
- **Definition:** JSON Schema for `migration.expected_diff`; parser that converts it to an evaluable `ExpectedDiffSpec` object; validator run at rule PR time (CI).
- **Acceptance:** CI fails on malformed `migration` blocks; parser unit tests cover path, change, and condition variants; predicate evaluator returns `expected | unexpected` for synthetic inputs.
- **Effort:** 1 week
- **Depends on:** F6

### T-S8.3: PromotionController state machine
- **Definition:** Implements draft → shadow → canary_1 → canary_10 → canary_50 → full → closed transitions. Every transition writes a stage_event row. Abort and rollback paths explicit.
- **Acceptance:** Unit tests cover every transition and every illegal transition; race conditions on double-advance produce clear errors; state machine is fully observable via `/api/v1/admin/rule-promotions/{id}`.
- **Effort:** 1 week
- **Depends on:** T-S8.1

### T-S8.4: ShadowRunner
- **Definition:** Worker that samples computes at 1% rate (hash-based by org_id), runs v_new, writes to `technique_compute_shadow`. Reuses rule engine from F6; no user-facing side effects. Triggered when a promotion enters `shadow` stage; stops when it advances past `canary_50` (by that point canary rollout itself is generating diff signals).
- **Acceptance:** Sampling is deterministic; shadow writes do not interfere with production computes; shadow throughput scales to 200k shadow computes/s.
- **Effort:** 1 week
- **Depends on:** T-S8.3

### T-S8.5: DiffClassifier
- **Definition:** Given two result JSONs and an `ExpectedDiffSpec`, returns classification. Handles boolean, numeric, temporal, structured shapes.
- **Acceptance:** Unit tests per output shape (F7). Edge cases: missing keys, null values, floating-point near-equality. Predicate engine evaluates in < 1 ms per row.
- **Effort:** 1 week
- **Depends on:** T-S8.2

### T-S8.6: BigQuery divergence aggregator scheduled query
- **Definition:** BQ scheduled query (every 5 min during active promotion) writes rows into `rule_promotion_divergence_summary` via reverse-sync to OLTP. Uses UDF for `classify_expected`.
- **Acceptance:** End-to-end latency from shadow write → divergence row visible < 10 minutes. Handles 5B shadow rows / week at steady state.
- **Effort:** 1 week
- **Depends on:** T-S8.4, S4

### T-S8.7: GateEvaluator + auto-halt
- **Definition:** Reads latest divergence summary; emits PASS / WARN / FAIL. Thresholds: unexpected > 0.1% = FAIL; expected outside declared range = FAIL; sample too small = WARN (wait). Triggers PagerDuty + auto-abort on FAIL.
- **Acceptance:** Synthetic divergence data drives correct verdicts; auto-halt kicks in within 60 s of a stage-breaching threshold.
- **Effort:** 4 days
- **Depends on:** T-S8.6

### T-S8.8: Chart change log writer
- **Definition:** On stage advancement (1% → 10% etc.), for every chart whose output_hash changed, insert row into `chart_change_log`. Runs as BQ-to-OLTP reverse sync.
- **Acceptance:** After promoting v1.0.1 to full, every affected chart has a log row; `/api/v1/audit/chart/{id}/changes` returns log.
- **Effort:** 4 days
- **Depends on:** T-S8.3

### T-S8.9: Rollback implementation
- **Definition:** `rollback()` sets stage to `rolled_back`, forces `effective_to=NOW()` on to_version rows in `classical_rule`, triggers recomputation of all affected charts via F13 dependency graph.
- **Acceptance:** Rollback test in staging: promote, rollback within 1 h; all chart_reading_view rows match pre-promotion state within 1 h.
- **Effort:** 1 week
- **Depends on:** T-S8.3, F13

### T-S8.10: Admin UI
- **Definition:** Next.js pages at `web/app/(admin)/rule-promotions/`. Lists active promotions, detail page with timeline, divergence chart, sample diffs, approve-next / abort / rollback buttons. Uses typed TypeScript interfaces in `web/types/`.
- **Acceptance:** Product walkthrough with classical advisor: can create promotion, start shadow, review diffs, approve, observe rollout progress, abort.
- **Effort:** 2 weeks
- **Depends on:** T-S8.3, T-S8.5

### T-S8.11: Admin CLI
- **Definition:** `josi promotion create | start | status | advance | abort | rollback | replay`. Wraps REST endpoints.
- **Acceptance:** CLI commands map to REST endpoints; operational runbook uses CLI only.
- **Effort:** 3 days
- **Depends on:** T-S8.3

### T-S8.12: Extend P3-E6-flag for promotion-aware rollout
- **Definition:** Flag system understands promotion stages: "100% on v1.0.1 for shard hash bucket 0..9" maps to canary_10. Reuses P3-E6-flag as substrate; S8 becomes the decision plane.
- **Acceptance:** Stage advancement in S8 updates P3-E6-flag in real time; rule engine reads flag to pick version.
- **Effort:** 1 week
- **Depends on:** P3-E6-flag, T-S8.3

### T-S8.13: Integration tests + staging dry-run
- **Definition:** End-to-end staging test: load 1M shadow charts, migrate a rule from v1.0.0 → v1.0.1 with a synthetic expected_diff that captures some but not all diffs, observe auto-halt on unexpected fraction.
- **Acceptance:** Test passes; documented in runbook.
- **Effort:** 1 week
- **Depends on:** T-S8.4 through T-S8.10

## 8. Unit Tests

### 8.1 expected_diff_parser

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_parse_simple_bool_diff` | YAML with `path: "$.active", change: "false → true"` | evaluable spec | baseline |
| `test_parse_condition_dsl` | YAML with `condition` expression | parses & evaluates | reuse of F6 DSL |
| `test_reject_malformed_yaml` | missing `expected_rate_min` | ValueError | strict validation |
| `test_reject_unknown_path` | path into field not in output_shape | ValueError | schema-aware |
| `test_evaluate_matching_diff` | two result dicts, spec | returns "expected" | correctness |
| `test_evaluate_non_matching_diff` | diff not covered | returns "unexpected" | safety |

### 8.2 diff_classifier

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_equal_outputs` | same hash | classification EQUAL | base case |
| `test_boolean_flip_matches_expected` | active false → true, spec predicate matches | DIFFERENT_EXPECTED | core path |
| `test_boolean_flip_unexpected` | active flipped on chart outside condition | DIFFERENT_UNEXPECTED | safety |
| `test_error_on_new_raises` | v_new raised, v_old did not | ERROR | robust classification |
| `test_numeric_near_equal_is_equal` | 0.3000001 vs 0.3 on numeric shape | EQUAL within epsilon | float tolerance |
| `test_temporal_diff_matches_range_condition` | date shift within declared range | DIFFERENT_EXPECTED | temporal shape |

### 8.3 promotion_controller state machine

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_create_promotion_starts_in_draft` | new promotion | stage='draft' | initial state |
| `test_draft_to_shadow_only` | draft → canary_10 directly | IllegalTransition | enforces order |
| `test_shadow_to_canary_1_requires_gate_pass` | advance with unexpected diff | 409 error | safety gate |
| `test_canary_advance_records_stage_event` | approve next stage | new stage_event row | auditability |
| `test_abort_from_any_active_stage` | abort during canary_50 | stage='aborted'; shadow data retained | rollback-friendly |
| `test_rollback_only_after_promotion_reached_full` | rollback from canary_10 | IllegalTransition (use abort) | semantic clarity |

### 8.4 gate_evaluator

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_gate_pass_below_thresholds` | unexpected 0.05%, expected in range | PASS | happy path |
| `test_gate_fail_unexpected_above_threshold` | unexpected 0.5% | FAIL + reason | safety |
| `test_gate_fail_expected_below_range` | expected 0.2% with declared min 1% | FAIL + reason | hypothesis check |
| `test_gate_warn_insufficient_sample` | 500 charts sampled | WARN | don't promote on small N |
| `test_auto_halt_emits_pagerduty` | simulated FAIL | event in alerting system | oncall contract |

### 8.5 shadow_runner

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_hash_sampling_is_deterministic` | same org twice | same sampled/not | reproducibility |
| `test_sampling_rate_1pct` | 10k orgs | ~100 sampled (Poisson tolerance) | rate correctness |
| `test_shadow_write_does_not_touch_production_compute` | shadow run | `technique_compute` unchanged | isolation |
| `test_shadow_respects_abort` | abort mid-run | stops within 10s | operational safety |
| `test_replay_mode_on_historical_charts` | explicit chart list | writes shadow rows | replay path |

### 8.6 chart_change_log writer

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_log_written_on_stage_advance` | 10% stage with 1k divergent charts | 1k log rows | audit |
| `test_no_log_on_equal_outputs` | EQUAL chart | no log row | no-noise |
| `test_log_idempotent_on_retry` | stage advance retried | 1k unique rows | retry safety |

### 8.7 End-to-end integration

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_full_promotion_flow` | create → shadow → advance to full → close | terminal state correct; all stage_events present | happy path end-to-end |
| `test_full_rollback_flow` | full → rollback | all chart_reading_view reverted within 1h | rollback works |
| `test_auto_halt_on_unexpected` | synthetic unexpected diffs | stage auto-aborts | integration of gate + controller |

## 9. EPIC-Level Acceptance Criteria

- [ ] Alembic migration applies cleanly; rollback drops tables cleanly
- [ ] Every rule version YAML with `supersedes` set requires `migration.expected_diff`; CI enforces
- [ ] 1% shadow sampling is deterministic and produces statistically meaningful diffs within 1 h at steady state
- [ ] Diff classification runs in BigQuery within 10 min of shadow write
- [ ] Gate evaluator correctly halts on unexpected divergence > 0.1%
- [ ] Admin UI allows full promotion lifecycle (create, start shadow, inspect diffs, advance, abort, rollback)
- [ ] Chart change log accessible via `/api/v1/audit/chart/{id}/changes` and survives partition drops
- [ ] Rollback recomputes all affected charts back to from_version within 1 h on 10M-chart corpus
- [ ] P3-E6-flag integration: promotion stage controls rule version served in real time
- [ ] Staging dry-run of a realistic rule migration succeeds
- [ ] Runbook merged: "Rule promotion went wrong — triage and roll back"
- [ ] Unit test coverage ≥ 90% on all new modules
- [ ] Cost during active promotion ≤ 5% of baseline OLTP write spend

## 10. Rollout Plan

- **Feature flag:** `RULE_PROMOTION_MODE` with states `disabled` | `shadow_only` | `full`. Default `disabled` until first staging dry-run passes.
- **Shadow compute:** this PRD IS the shadow-compute infrastructure. It shadows itself metaphorically — first real use is a no-op migration (v1.0.0 → v1.0.1 with bytewise-identical rule body) to verify the machinery.
- **Backfill strategy:** not applicable; all promotions happen from day of enablement forward.
- **Rollback plan:** `RULE_PROMOTION_MODE=disabled` stops all active promotions; existing `technique_compute_shadow` rows retained per TTL; in-flight promotions frozen at current stage until re-enabled. Data model changes are fully reversible via Alembic downgrade.

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| False positives in `unexpected` classification halt legitimate rollouts | Medium | Medium | Authoring tool for expected_diff includes "test this predicate against recent production" preview |
| Shadow compute doubles OLTP write load inadvertently | Medium | High | 1% sampling cap enforced at shadow_runner; monitoring; kill switch |
| BQ divergence query lags past 10 min SLO | Medium | Medium | Fallback to OLTP computation for small sample (< 10k rows) during BQ issue; runbook |
| Rollback compute storm when reverting widely-used rule | High | High | Priority queue: interactive charts first, batch later; throttle to 10% OLTP capacity |
| Admin user approves without reviewing diffs | Medium | High | UI requires scrolling through at least 5 sample diffs + typing rule ID to confirm |
| Rule author writes overly-loose `condition` that matches unexpected diffs | Medium | Medium | PR-time lint: `condition` cannot be `true` or missing; classical advisor review required |
| Promotion lives forever in `shadow` stage (forgotten) | Medium | Low | Weekly "stale promotions" report auto-posted to engineering channel |
| State machine race condition on concurrent approvals | Low | Medium | Optimistic locking via `stage_version` column + single-writer advisory lock |
| Chart change log grows unbounded | Medium | Low | Log is per-event; partition by month; retention policy 3 years for audit |
| Shadow table TTL drop removes data a rollback still needs | Low | High | Rollback path copies relevant shadow rows to archival table before TTL hits; promotion close confirms copy |

## 12. References

- Master spec: [`docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`](../../../superpowers/specs/2026-04-19-classical-techniques-expansion-design.md)
- F4 temporal rule versioning: [`F4-temporal-rule-versioning.md`](../P0/F4-temporal-rule-versioning.md)
- F6 rule DSL + YAML loader: [`F6-rule-dsl-yaml-loader.md`](../P0/F6-rule-dsl-yaml-loader.md)
- F13 content-hash provenance: [`F13-content-hash-provenance.md`](../P0/F13-content-hash-provenance.md)
- P3-E6-flag feature-flag rollouts: [`P3-E6-flag-feature-flagged-rule-rollouts.md`](../P3/P3-E6-flag-feature-flagged-rule-rollouts.md)
- S4 OLAP replication: [`S4-olap-replication-clickhouse.md`](./S4-olap-replication-clickhouse.md)
- P3-E8-obs per-rule observability: [`P3-E8-obs-per-rule-observability.md`](../P3/P3-E8-obs-per-rule-observability.md)
- GitHub progressive delivery patterns — Humble & Farley, *Continuous Delivery*
