---
prd_id: P3-E8-obs
epic_id: E8
title: "Per-rule observability dashboards (auto-generated from rule metadata)"
phase: P3-scale-10m
tags: [#correctness, #experimentation]
priority: must
depends_on: [F8, F13, P3-E6-flag]
enables: []
classical_sources: []
estimated_effort: 2 weeks
status: draft
author: Govind
last_updated: 2026-04-19
---

# P3-E8-obs — Per-Rule Observability Dashboards

## 1. Purpose & Rationale

At P2 end, we have ~250 classical rules in production. At P4 / Reference-1000, we have ~1000. Each rule has its own behavioral fingerprint: activation rate, confidence distribution, cross-source agreement, latency. Without per-rule observability:

- A rule silently changes behavior after an engine refactor — we don't notice for weeks.
- Astrologer override rate spikes on one specific yoga — we don't see it.
- A rule's compute latency starts dominating — we blame the "engine" generically.

**Manually** building 250+ Grafana dashboards is untenable. This PRD ships **programmatic dashboard generation** from rule metadata. Every `classical_rule` row triggers automatic creation / refresh of a standard 6-panel dashboard in Grafana, folder-organized by `technique_family_id`. Alert rules follow the same pattern.

Integration with existing observability: Josi runs on GCP Cloud Run. Current stack uses Google Cloud Monitoring for infra metrics and Grafana Cloud for application dashboards (new at P3). This PRD formalizes Grafana Cloud as the app-metrics home and ships the auto-generation pipeline.

Output: 250 rules → 250 dashboards, auto-refreshed nightly. Alerts: "rule X activation rate changed > 2σ from 30-day baseline" pages the rule's owner.

## 2. Scope

### 2.1 In scope
- Metric definitions per rule (6 standard metrics):
  1. **Activation rate** — % of charts where rule activates (per output_shape semantics of "activated").
  2. **Confidence distribution** — histogram of confidence scores (for strategy B/C/D).
  3. **Cross-source agreement score** — % of sources agreeing on this rule's output.
  4. **Strategy divergence** — disagreement % across strategies A/B/C/D for same rule.
  5. **Compute latency** — P50 / P99 per rule, in ms.
  6. **Override / thumbs signals** — astrologer override rate, user thumbs rate.
- Metric emission: Prometheus-style labels `{rule_id, source_id, version, family_id, strategy_id}`.
- Metric aggregation: Grafana Cloud (Mimir-backed).
- Dashboard generator: Python script that walks `classical_rule` + rule metadata → POSTs to Grafana API → creates / updates dashboard.
- Folder organization: `Rules / {technique_family_id} / {rule_id}` in Grafana.
- Alert rules: auto-generated per rule; default thresholds + per-rule overrides in rule YAML.
- Dashboard-as-code storage: generated JSON committed to repo (`ops/grafana/dashboards/`) for PR review.
- CI job: nightly run regenerates; drift detection.

### 2.2 Out of scope
- Log aggregation — handled separately (GCP Cloud Logging).
- Tracing per-rule — OpenTelemetry instrumentation of compute already exists; this PRD focuses on metrics.
- User-facing stats UI — Astrologer Workbench has its own rule-quality view (E12); this is ops-only.
- Custom alert channels per rule owner — single default channel; owner encoded in alert labels.
- Anomaly detection beyond 2σ — later ML-based detection is P4+.

### 2.3 Dependencies
- F8 — aggregation protocol emits `aggregation_event` rows that feed metrics.
- F13 — content-hash provenance for tagging metrics with rule version.
- P3-E6-flag — rollout stage appears on dashboard panels.

## 3. Technical Research

### 3.1 Metric emission path

Every `aggregation_event` insert triggers metric updates (OpenTelemetry counter + histogram). Hot path instrumentation is already cheap (~µs). Metrics also computed in batch from Postgres (nightly) for activation rate and cross-source agreement, since per-event emission is too granular for these.

Hybrid:

- **Real-time counters** (per event): latency histogram, activation toggle.
- **Batch-derived** (nightly SQL queries against `technique_compute` / `aggregation_event`): activation rate, cross-source agreement, strategy divergence.

Batch metrics stored as Prometheus `gauge` pushed to Grafana Cloud Mimir via a simple Cloud Run Job.

### 3.2 Grafana dashboards-as-code

Grafana dashboards are JSON objects. Two approaches:

1. **Grafonnet / Jsonnet**: Grafana Labs' canonical DSL; declarative; powerful. High learning curve.
2. **Python + grafanalib**: simpler; Pythonic; slightly less ergonomic for complex dashboards.

**Decision: grafanalib** — fits our Python-heavy codebase; dashboards are simple (6 panels, templated); contributors don't need to learn Jsonnet.

### 3.3 Dashboard template (per rule)

```
┌───────────────────────────────────────────────────────────────────────┐
│ Rule: yoga.raja.gaja_kesari | Source: bphs | Version: 1.2.0           │
│ Family: yoga | Stage: full_100 | Owner: classical-advisors@josi.com  │
├─────────────────────────┬─────────────────────────────────────────────┤
│ Panel 1: Activation     │ Panel 2: Confidence distribution            │
│ (time series; %)        │ (heatmap or histogram panel)                │
├─────────────────────────┼─────────────────────────────────────────────┤
│ Panel 3: Cross-source   │ Panel 4: Strategy divergence                │
│ agreement (%)           │ (A/B/C/D; disagreement %)                   │
├─────────────────────────┼─────────────────────────────────────────────┤
│ Panel 5: Compute        │ Panel 6: Signals                            │
│ latency P50/P99         │ (override rate, thumbs up/down)             │
└─────────────────────────┴─────────────────────────────────────────────┘
```

### 3.4 Alert thresholds

Default alert rules per rule:

- **Activation rate changed > 2σ** from 30-day baseline (alert: owner).
- **Cross-source agreement dropped below 0.5** for > 1 hour (alert: rule-owner).
- **Compute P99 latency > 500ms** for > 15 minutes (alert: engineering-oncall).
- **Thumbs-down rate > 30%** for > 1 hour (alert: product-oncall).
- **Override rate > 40%** for > 1 day (alert: classical-advisors).

Per-rule YAML overrides:

```yaml
# classical/rules/yoga/raja/gaja_kesari.yaml
# (existing rule DSL from F6)
alerts:
  activation_rate_sigma: 3.0   # wider tolerance for this rule
  override_rate_max: 0.5        # specifically allow higher override
```

### 3.5 Cardinality management

250 rules × 4 strategies × 10 sources × many labels ≈ 10k time series. Manageable on Grafana Cloud starter tier (10M active series). At 1000 rules = 40k time series, still comfortable.

Labels pruned where cardinality adds no insight (e.g., don't emit per-chart_id).

### 3.6 Folder layout

```
Rules
├── yoga
│   ├── raja
│   │   ├── gaja_kesari [dashboard]
│   │   ├── shasha [dashboard]
│   │   └── ...
│   ├── dhana
│   └── ...
├── dasa
│   ├── vimshottari [dashboard]
│   ├── yogini [dashboard]
│   └── ...
├── ashtakavarga
├── tajaka
├── jaimini
└── transit_event
```

Top-level "Rules overview" dashboard lists all rules with stage + alert state.

### 3.7 Drift detection

CI job compares live Grafana dashboard JSON to committed `ops/grafana/dashboards/*.json`. Drift → PR comment / alert.

### 3.8 Alternatives considered

| Alternative | Rejected because |
|---|---|
| Hand-authored dashboards | Doesn't scale to 250+ rules |
| Grafonnet / Jsonnet | Learning curve; team is Python-native |
| Terraform provider for Grafana | Works but Terraform-centric; we use Pulumi for infra |
| Datadog dashboards | Cost; we're already moving to Grafana Cloud |
| Cloud Monitoring only | Limited dashboard flexibility |

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| Dashboard-as-code lib | grafanalib (Python) | Native Python codebase |
| Grafana Cloud vs self-hosted | Grafana Cloud (managed Mimir) | Ops simplicity |
| Metric emission | Hybrid: real-time hot path + nightly batch | Granularity vs cost |
| Folder structure | `Rules/{family}/{rule_id}` | Aligns with technique_family_id dimension |
| Alert channels | Single default (rule_owner email / slack); override per rule | Simple; evolves if needed |
| Threshold defaults | 2σ activation, 0.5 agreement, 500ms P99, 30% thumbs-down | Calibrated against P2 data |
| Dashboard commit policy | Generated JSON committed; regenerated in CI | PR review + drift detection |
| Rule owner field | Added to classical_rule YAML frontmatter | Ownership accountability |

## 5. Component Design

### 5.1 New modules

```
src/josi/services/observability/
├── __init__.py
├── rule_metrics.py             # NEW: metric emission helpers
├── batch_metrics.py            # NEW: nightly batch metric computation
└── baseline_tracker.py         # NEW: 30-day rolling baseline per rule

ops/grafana/
├── dashboard_generator.py      # NEW: generates dashboards from rule registry
├── alert_generator.py          # NEW: generates alerts
├── dashboards/                 # committed generated JSON
│   └── rules/
│       └── yoga/
│           ├── raja/
│           │   ├── gaja_kesari.json
│           │   └── shasha.json
│           └── ...
├── alerts/                     # committed generated YAML (Grafana alert rules)
└── drift_check.py              # NEW: CI drift detector

src/josi/workflows/tasks/
├── batch_rule_metrics.py       # NEW: nightly task
└── regenerate_dashboards.py    # NEW: nightly task

deploy/
└── grafana-sync.cloudbuild.yaml   # NEW: CI job that POSTs dashboards to Grafana
```

### 5.2 Data model additions

```sql
-- Rolling baseline for activation rate per rule, 30-day window
CREATE TABLE rule_baseline (
    rule_id           TEXT NOT NULL,
    source_id         TEXT NOT NULL,
    metric_name       TEXT NOT NULL,       -- 'activation_rate','override_rate',...
    window_days       INT NOT NULL DEFAULT 30,
    mean              DOUBLE PRECISION NOT NULL,
    stddev            DOUBLE PRECISION NOT NULL,
    samples           BIGINT NOT NULL,
    computed_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (rule_id, source_id, metric_name)
);

-- Rule owner (extracted from YAML frontmatter on rule load)
ALTER TABLE classical_rule
    ADD COLUMN owner_email TEXT,
    ADD COLUMN alert_overrides JSONB NOT NULL DEFAULT '{}'::jsonb;
```

### 5.3 Metric emission (hot path)

```python
# src/josi/services/observability/rule_metrics.py

from opentelemetry import metrics

meter = metrics.get_meter("josi.rules")

_compute_latency_hist = meter.create_histogram(
    "josi_rule_compute_latency_seconds",
    description="Rule compute latency",
    unit="s",
)

_activation_counter = meter.create_counter(
    "josi_rule_activation_total",
    description="Rule activated or not",
)

_aggregation_counter = meter.create_counter(
    "josi_rule_aggregation_total",
    description="Aggregation event per rule",
)

def record_compute(
    rule_id: str, source_id: str, version: str, family_id: str,
    duration_seconds: float,
) -> None:
    _compute_latency_hist.record(
        duration_seconds,
        attributes={
            "rule_id": rule_id, "source_id": source_id,
            "version": version, "family_id": family_id,
        },
    )

def record_activation(
    rule_id: str, source_id: str, version: str, family_id: str,
    activated: bool,
) -> None:
    _activation_counter.add(1, attributes={
        "rule_id": rule_id, "source_id": source_id,
        "version": version, "family_id": family_id,
        "activated": str(activated).lower(),
    })
```

### 5.4 Batch metrics (nightly)

```python
# src/josi/workflows/tasks/batch_rule_metrics.py

@app.task(queue="compute_lo", retry=retry_3)
async def batch_rule_metrics() -> None:
    async with get_analytical_db_session() as s:
        # For each (rule_id, source_id, version), compute last-24h metrics
        results = await s.execute(text("""
            SELECT
                tc.rule_id,
                tc.source_id,
                tc.rule_version,
                tc.technique_family_id,
                count(*) FILTER (WHERE (tc.result->>'active')::bool) AS n_active,
                count(*)                                              AS n_total,
                percentile_cont(0.5) WITHIN GROUP (ORDER BY
                    extract(epoch FROM (tc.computed_at - astrology_chart.created_at)))
                                                                      AS p50_compute_s
            FROM technique_compute tc
            JOIN astrology_chart ON astrology_chart.chart_id = tc.chart_id
            WHERE tc.computed_at >= now() - INTERVAL '1 day'
            GROUP BY tc.rule_id, tc.source_id, tc.rule_version, tc.technique_family_id
        """))
        # Push to Mimir as gauges
        for row in results:
            _push_gauge(
                "josi_rule_activation_rate",
                value=row.n_active / max(row.n_total, 1),
                labels={
                    "rule_id": row.rule_id,
                    "source_id": row.source_id,
                    "version": row.rule_version,
                    "family_id": row.technique_family_id,
                },
            )

    # Update rolling baseline
    await _refresh_baselines()
```

### 5.5 Dashboard generator

```python
# ops/grafana/dashboard_generator.py

from grafanalib.core import (
    Dashboard, Graph, Heatmap, Target, Row, Time, YAxes, YAxis,
    RowPanel, TimeSeries, Stat,
)

def build_rule_dashboard(rule: ClassicalRuleRow) -> Dashboard:
    title = f"Rule: {rule.rule_id} ({rule.source_id} v{rule.version})"
    tags = ["rule", rule.technique_family_id, rule.source_id]
    owner = rule.owner_email or "unknown"
    folder = f"Rules / {rule.technique_family_id}"

    panels = [
        TimeSeries(
            title="Activation rate",
            dataSource="mimir",
            targets=[Target(
                expr=(
                    f'josi_rule_activation_rate'
                    f'{{rule_id="{rule.rule_id}",source_id="{rule.source_id}",version="{rule.version}"}}'
                ),
            )],
            unit="percentunit",
        ),
        Heatmap(
            title="Confidence distribution",
            dataSource="mimir",
            targets=[Target(
                expr=(
                    f'rate(josi_rule_confidence_bucket'
                    f'{{rule_id="{rule.rule_id}"}}[5m])'
                ),
            )],
        ),
        TimeSeries(
            title="Cross-source agreement",
            dataSource="mimir",
            targets=[Target(
                expr=(
                    f'josi_rule_cross_source_agreement'
                    f'{{rule_id="{rule.rule_id}"}}'
                ),
            )],
        ),
        TimeSeries(
            title="Strategy divergence",
            dataSource="mimir",
            targets=[Target(
                expr=(
                    f'josi_rule_strategy_disagreement'
                    f'{{rule_id="{rule.rule_id}"}}'
                ),
            )],
        ),
        TimeSeries(
            title="Compute latency P50/P99",
            dataSource="mimir",
            targets=[
                Target(expr=f'histogram_quantile(0.50, rate(josi_rule_compute_latency_seconds_bucket{{rule_id="{rule.rule_id}"}}[5m]))'),
                Target(expr=f'histogram_quantile(0.99, rate(josi_rule_compute_latency_seconds_bucket{{rule_id="{rule.rule_id}"}}[5m]))'),
            ],
        ),
        TimeSeries(
            title="Override & thumbs signals",
            dataSource="mimir",
            targets=[
                Target(expr=f'josi_rule_override_rate{{rule_id="{rule.rule_id}"}}'),
                Target(expr=f'josi_rule_thumbs_down_rate{{rule_id="{rule.rule_id}"}}'),
            ],
        ),
    ]

    return Dashboard(
        title=title,
        tags=tags,
        panels=panels,
        annotations=[_owner_annotation(owner), _rollout_stage_annotation(rule)],
        time=Time("now-7d", "now"),
        refresh="5m",
        uid=f"rule-{rule.rule_id}-{rule.source_id}-{rule.version}"[:40],
    ).auto_panel_ids()
```

### 5.6 Alert generator

```python
# ops/grafana/alert_generator.py

def build_rule_alerts(rule: ClassicalRuleRow) -> list[AlertRule]:
    overrides = rule.alert_overrides
    alerts = [
        AlertRule(
            name=f"rule_activation_sigma_{rule.rule_id}",
            expr=(
                f'abs(josi_rule_activation_rate{{rule_id="{rule.rule_id}"}} - '
                f'avg_over_time(josi_rule_activation_rate{{rule_id="{rule.rule_id}"}}[30d])) > '
                f'{overrides.get("activation_rate_sigma", 2)} * '
                f'stddev_over_time(josi_rule_activation_rate{{rule_id="{rule.rule_id}"}}[30d])'
            ),
            for_="1h",
            labels={"owner": rule.owner_email, "severity": "warning"},
            annotations={
                "summary": f"{rule.rule_id}: activation rate drifted > {overrides.get('activation_rate_sigma', 2)}σ",
            },
        ),
        AlertRule(
            name=f"rule_latency_p99_{rule.rule_id}",
            expr=f'histogram_quantile(0.99, rate(josi_rule_compute_latency_seconds_bucket{{rule_id="{rule.rule_id}"}}[5m])) > 0.5',
            for_="15m",
            labels={"owner": "eng-oncall", "severity": "warning"},
            annotations={"summary": f"{rule.rule_id}: P99 compute > 500ms"},
        ),
        AlertRule(
            name=f"rule_thumbs_down_{rule.rule_id}",
            expr=f'josi_rule_thumbs_down_rate{{rule_id="{rule.rule_id}"}} > {overrides.get("thumbs_down_rate_max", 0.3)}',
            for_="1h",
            labels={"owner": "product-oncall", "severity": "warning"},
        ),
        AlertRule(
            name=f"rule_override_rate_{rule.rule_id}",
            expr=f'josi_rule_override_rate{{rule_id="{rule.rule_id}"}} > {overrides.get("override_rate_max", 0.4)}',
            for_="1d",
            labels={"owner": rule.owner_email or "classical-advisors"},
        ),
    ]
    return alerts
```

### 5.7 Sync pipeline

```
nightly (02:30 UTC):
  1. batch_rule_metrics task runs; pushes gauges to Mimir
  2. regenerate_dashboards task runs:
     a. Load all classical_rule rows
     b. For each, build_rule_dashboard → JSON
     c. Write to ops/grafana/dashboards/{family}/{rule_id}.json
     d. Open PR if git diff detected; or, if running in CI, fail with diff
  3. grafana-sync.cloudbuild.yaml (triggered on merge to main):
     a. Walk ops/grafana/dashboards/
     b. POST each JSON to Grafana API
     c. Walk ops/grafana/alerts/
     d. Apply alert rules
```

## 6. User Stories

### US-P3-E8-obs.1: As a rule owner, I can see my rule's dashboard in Grafana within 24h of it being added
**Acceptance:** author commits new rule YAML → nightly sync runs → dashboard present in Grafana under `Rules/{family}/{rule_id}`.

### US-P3-E8-obs.2: As an SRE, when a rule's activation rate drifts > 2σ, I get paged with the rule owner in the alert
**Acceptance:** synthetic test: inject activation drift → alert fires to owner channel within 1 hour; message includes `rule_id`, `owner_email`.

### US-P3-E8-obs.3: As a classical advisor, I see all yoga rules' dashboards in one folder
**Acceptance:** `Rules / yoga / ...` folder contains all yoga rule dashboards.

### US-P3-E8-obs.4: As a developer, adding a new rule doesn't require me to hand-write a dashboard
**Acceptance:** YAML rule merged → dashboard auto-generated on next nightly run.

### US-P3-E8-obs.5: As an ops engineer, I see the rollout stage on every rule's dashboard
**Acceptance:** dashboards display annotation: `Stage: canary_10` (from P3-E6-flag).

### US-P3-E8-obs.6: As a reviewer, I can PR-review dashboard JSON drift before it lands in prod
**Acceptance:** CI job flags dashboards whose live JSON differs from committed; PR comment lists diffs.

## 7. Tasks

### T-P3-E8-obs.1: Set up Grafana Cloud + Mimir data source
- **Definition:** Grafana Cloud org provisioned; Mimir endpoint configured; API token in Secret Manager (`josiam-grafana-api-token-{env}`).
- **Acceptance:** `grafana-cli --url ... get dashboards` returns empty set; Mimir accepts metric writes.
- **Effort:** 1 day
- **Depends on:** nothing

### T-P3-E8-obs.2: Hot-path metric emission
- **Definition:** `rule_metrics.py` per 5.3. Instrument `compute_for_source` and aggregation tasks.
- **Acceptance:** compute a test chart → metrics visible in Mimir with correct labels.
- **Effort:** 2 days
- **Depends on:** T-P3-E8-obs.1

### T-P3-E8-obs.3: Batch metrics task
- **Definition:** `batch_rule_metrics` procrastinate periodic task per 5.4. Pushes gauges to Mimir.
- **Acceptance:** nightly run completes < 10 min at 10M charts; gauges visible.
- **Effort:** 2 days
- **Depends on:** T-P3-E8-obs.2

### T-P3-E8-obs.4: `rule_baseline` table + rolling baseline refresh
- **Definition:** Migration per 5.2. Refresh logic in `batch_metrics.py` computes 30-day mean/stddev.
- **Acceptance:** synthetic data → baselines correct; refresh idempotent.
- **Effort:** 1 day
- **Depends on:** T-P3-E8-obs.3

### T-P3-E8-obs.5: `owner_email` + `alert_overrides` on classical_rule
- **Definition:** Migration + update rule YAML loader (F6) to extract these fields.
- **Acceptance:** rule YAML with `owner_email: ...` → column populated on reload.
- **Effort:** 1 day
- **Depends on:** F6 complete

### T-P3-E8-obs.6: Dashboard generator
- **Definition:** `dashboard_generator.py` with `build_rule_dashboard` per 5.5.
- **Acceptance:** running `python -m ops.grafana.dashboard_generator` on 10 test rules produces 10 JSON files; each validates against Grafana schema.
- **Effort:** 3 days
- **Depends on:** T-P3-E8-obs.2

### T-P3-E8-obs.7: Alert generator
- **Definition:** `alert_generator.py` with `build_rule_alerts` per 5.6.
- **Acceptance:** running generator produces Grafana alert rule YAML; validates.
- **Effort:** 2 days
- **Depends on:** T-P3-E8-obs.6

### T-P3-E8-obs.8: Nightly regenerate task + commit script
- **Definition:** `regenerate_dashboards` procrastinate task. Writes JSON into repo; opens PR via GitHub API if diff. Alternative in CI: fail build if drift.
- **Acceptance:** scheduled; synthetic rule addition → PR opened with new JSON.
- **Effort:** 2 days
- **Depends on:** T-P3-E8-obs.6

### T-P3-E8-obs.9: Cloud Build sync pipeline
- **Definition:** `deploy/grafana-sync.cloudbuild.yaml` — on merge to main, walks `ops/grafana/dashboards/` + `alerts/` and applies via Grafana API.
- **Acceptance:** merging a dashboard change triggers pipeline; dashboard appears in Grafana within 5 min.
- **Effort:** 2 days
- **Depends on:** T-P3-E8-obs.8

### T-P3-E8-obs.10: Drift detection CI
- **Definition:** `drift_check.py`: fetches live dashboard JSON from Grafana; compares to committed. Runs in daily CI.
- **Acceptance:** manual edit in Grafana UI → next CI run flags drift.
- **Effort:** 1 day
- **Depends on:** T-P3-E8-obs.9

### T-P3-E8-obs.11: Top-level "Rules overview" dashboard
- **Definition:** Aggregated dashboard: list of all rules, stage, alert state, owner.
- **Acceptance:** clicking a rule row drills into per-rule dashboard.
- **Effort:** 1 day
- **Depends on:** T-P3-E8-obs.6

### T-P3-E8-obs.12: Documentation
- **Definition:** `docs/markdown/runbooks/rule-observability.md` — how to read dashboards, respond to alerts. CLAUDE.md update: "every rule YAML must include `owner_email`".
- **Acceptance:** merged; team training held.
- **Effort:** 1 day
- **Depends on:** T-P3-E8-obs.11

## 8. Unit Tests

### 8.1 Metric emission

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_compute_latency_recorded` | 250ms compute | histogram sample with expected labels | hot path |
| `test_activation_counter_increments_on_true` | activated=True | counter +1 with labels | counter |
| `test_activation_counter_separate_label_on_false` | activated=False | separate counter bucket | label separation |
| `test_labels_exclude_chart_id` | emit metric | chart_id not present in labels | cardinality guard |

### 8.2 Batch metrics

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_batch_computes_activation_rate` | 10 charts with rule: 3 active | gauge = 0.3 | correctness |
| `test_batch_handles_zero_activations` | all inactive | gauge = 0 | division by zero |
| `test_batch_pushes_to_mimir` | run task | POST to Mimir remote_write endpoint observed | integration |
| `test_batch_incremental_idempotent` | run twice in 24h | overwrites gauges; no stale values | idempotency |

### 8.3 Rolling baseline

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_baseline_computes_mean_stddev` | 30 days of samples: [0.1,0.2,...,0.1] | stats computed | math |
| `test_baseline_warns_on_insufficient_samples` | < 7 days of data | row has samples=N; stddev flagged low | guard |
| `test_baseline_refresh_idempotent` | run twice | single row with latest values | idempotency |

### 8.4 Dashboard generator

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_dashboard_has_6_panels` | synthetic rule | generated Dashboard.panels has 6 | template |
| `test_dashboard_uid_stable` | same rule twice | same uid | no churn |
| `test_dashboard_folder_matches_family` | rule family=yoga | folder `Rules / yoga` | org |
| `test_dashboard_tags_include_family_and_source` | rule | tags include both | searchability |
| `test_dashboard_promql_queries_quoted_correctly` | rule with special chars | queries escape `"` | injection safety |

### 8.5 Alert generator

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_default_alert_thresholds` | rule with no overrides | default 2σ, 500ms P99, 0.3 thumbs, 0.4 override | defaults applied |
| `test_alert_overrides_applied` | rule with `activation_rate_sigma: 3.0` | alert expr uses 3.0 | override |
| `test_alert_owner_label` | rule with owner=foo@josi.com | label `owner=foo@josi.com` | routing |
| `test_alert_for_duration` | generated | `for: 1h` on activation; `for: 15m` on latency | alert hygiene |

### 8.6 Drift check

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_drift_detects_panel_added` | live has 7 panels, committed 6 | drift reported | detection |
| `test_drift_no_false_positive_on_auto_fields` | live has different `version` field | ignored | stability |
| `test_drift_reports_exact_diff_path` | drift in panels[2].targets[0].expr | diff path clear | debug |

### 8.7 Integration

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_new_rule_gets_dashboard_next_run` | add rule YAML → run generator | dashboard JSON present in repo | e2e |
| `test_regenerate_no_op_on_unchanged` | re-run without rule changes | git status clean | idempotency |
| `test_alert_fires_on_synthetic_drift` | push synthetic metrics that trigger 2σ | alert rule evaluates true in Grafana | alerting |

## 9. EPIC-Level Acceptance Criteria

- [ ] Grafana Cloud + Mimir configured; API token in Secret Manager
- [ ] Hot-path metrics emitted with correct labels; verified in Mimir
- [ ] Batch metrics nightly task runs in < 10 min at 10M-chart scale
- [ ] `rule_baseline` table + rolling refresh implemented
- [ ] `classical_rule` has `owner_email` + `alert_overrides` columns
- [ ] Dashboard generator produces valid Grafana dashboards per rule
- [ ] Alert generator produces valid Grafana alert rules
- [ ] Nightly regenerate + Cloud Build sync pipeline operational
- [ ] Drift detection in CI; PR comment on drift
- [ ] Folder hierarchy `Rules / {family} / {rule_id}` populated in Grafana
- [ ] Top-level "Rules overview" dashboard lists all rules
- [ ] Synthetic drift test: alert fires within 1 hour; owner labeled
- [ ] Unit test coverage ≥ 90% for generator + alert modules
- [ ] Runbook + CLAUDE.md update merged
- [ ] All existing rules populated with `owner_email` in YAML

## 10. Rollout Plan

- **Feature flag:** `FEATURE_RULE_OBSERVABILITY` (default off until T-P3-E8-obs.9 green).
- **Shadow compute:** N/A — additive only.
- **Backfill strategy:**
  - Step 1: emit metrics (hot path active immediately — no-op until dashboards exist).
  - Step 2: Bulk-add `owner_email` to all existing rule YAMLs in a single PR; defaults to `classical-advisors@josi.com` where unknown.
  - Step 3: Run generator once; open single PR with all dashboards.
  - Step 4: Merge → sync pipeline applies.
  - Step 5: Rolling baseline needs 7 days of data before alerts are meaningful; alert rules active but expected to stay silent for 7 days.
- **Rollback plan:**
  1. Disable `FEATURE_RULE_OBSERVABILITY`. Hot-path metrics still emitted (harmless).
  2. Pause sync pipeline.
  3. Dashboards remain in Grafana but stop updating. Alerts silenced.
  4. No data corruption.

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Metric cardinality explosion (10k+ series) | Medium | Medium | Labels pruned; chart_id excluded; review labels per new metric |
| Grafana Cloud cost exceeds budget | Medium | Medium | Starter tier = 10M active series (ample at 10k); monitor monthly bill |
| Nightly regenerate breaks on malformed rule | Medium | Low | Per-rule try/except; skip bad rule, log error, continue |
| Drift from manual UI edits | High (certain some engineers will edit) | Low | Daily CI detects; Slack notification; education |
| Alert fatigue from too many per-rule alerts | High | Medium | Default thresholds tuned; owner labels route correctly; weekly review of noisy alerts |
| Sync pipeline fails silently | Low | High | CI step checks dashboard count matches expected; alert on mismatch |
| Baseline contaminated by rollout stage changes | Medium | Medium | Baseline keyed per version; rolls fresh per new version |
| Rule YAML owner field not filled | Medium | Low | Default to `classical-advisors@josi.com`; lint rule enforces field on new YAMLs |

## 12. References

- Master spec: [`docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`](../../../superpowers/specs/2026-04-19-classical-techniques-expansion-design.md)
- Depends on: [F8](../P0/F8-technique-result-aggregation-protocol.md), [F13](../P0/F13-content-hash-provenance.md), [P3-E6-flag](./P3-E6-flag-feature-flagged-rule-rollouts.md)
- grafanalib: https://github.com/weaveworks/grafanalib
- Grafana HTTP API: https://grafana.com/docs/grafana/latest/developers/http_api/
- Grafana Cloud Mimir: https://grafana.com/docs/mimir/latest/
- Google SRE Book Ch. 6 "Monitoring Distributed Systems"
