---
prd_id: C5
epic_id: C5
title: "Differential testing vs Jagannatha Hora (JH) + Maitreya9"
phase: P3-scale-10m
tags: [#correctness]
priority: should
depends_on: [E15a, F16, F17]
enables: []
classical_sources: [jh, maitreya]
estimated_effort: 3 weeks
status: draft
author: Govind
last_updated: 2026-04-19
---

# C5 — Differential Testing vs Reference Implementations

## 1. Purpose & Rationale

Josi computes classical astrology from first principles using Swiss Ephemeris + our rule engine. The two most respected reference implementations in the Vedic community are:

- **Jagannatha Hora (JH) 7.x** — Windows desktop app, closed source but widely trusted; supports exports to XML.
- **Maitreya9** — open-source C++ (portable); supports a CLI (`maitreya-console`) or we pre-compute reference tables for a golden-chart set.

Ad-hoc spot-checking against these gives us confidence but no systematic assurance. This PRD ships a **nightly differential testing job**: pick a random sample of 100 charts (50 golden-suite + 50 recent production charts), compute across all three engines (Josi, JH, Maitreya9), diff the outputs per technique, and file GitHub issues for disagreements.

Success target: **< 1% disagreement per technique at P2 end**. Disagreements that survive investigation get classified as:

- **Josi bug** — we fix.
- **JH / Maitreya bug** — we document in known-disagreements.
- **Justifiable divergence** — e.g., different varga-scheme interpretation from the same source; documented via BPHS verse citation.

Tolerances differ by output shape: booleans exact; strengths ±0.05; temporal ±1 hour for dasa starts, ±1 day for transits; numeric ±5%.

Output: a **known-disagreements budget** — each entry has rule_id, source reference, justification, and tolerance. Everything outside the budget is a regression.

## 2. Scope

### 2.1 In scope
- Nightly differential-test job (Cloud Run Job scheduled at 03:00 UTC).
- Chart sampler: 50 from `tests/golden/charts/` + 50 recent prod charts (anonymized PII).
- JH integration: via XML export (pre-computed from JH for the 50 golden charts + nightly export for recent charts via RDP-controlled Windows runner — details below).
- Maitreya9 integration: via `maitreya-console` CLI run inside a Linux container (we ship the container with Maitreya9 built).
- Josi compute: invokes our engine via `ClassicalEngine` Protocol for each (chart, family).
- Comparator: per-shape tolerance logic (reuses P3-E6-flag's `agrees` function with tightened tolerances).
- Disagreement report: JSON file uploaded to GCS; GitHub issues auto-filed per cluster.
- Known-disagreements budget: YAML file `tests/differential/known_disagreements.yaml` — entries grant waivers for documented cases.
- Dashboard: disagreement rate per technique over time.
- Integration into CI: per-PR differential run on the 50 golden charts only (fast; ~2 min).

### 2.2 Out of scope
- Western-astrology references (there's no dominant Western equivalent of JH; we rely on `ephemeris + kerykeion` cross-checks separately).
- Real-time differential testing (too slow; nightly only).
- Automatic patching / self-healing on disagreements.
- Proving bug in JH or Maitreya (we document, don't fight).

### 2.3 Dependencies
- E15a — correctness harness v1 (golden suite infrastructure).
- F16 — golden chart suite (50 charts for baseline).
- F17 — property-based test harness (some tolerances reused).

## 3. Technical Research

### 3.1 JH integration

Jagannatha Hora is Windows-only and closed. Options:

- **Option A (rejected):** Wine-on-Linux. Poor fidelity; JH uses Windows-specific API paths.
- **Option B (chosen):** Pre-computed XML exports for golden charts (50 charts; one-time human effort). For recent prod charts: a dedicated Windows Cloud VM running JH + AutoHotkey scripts to drive export.
- **Option C (rejected):** Reverse-engineer JH's logic. Legally questionable + brittle.

**Decision: Option B.**

- Golden-chart exports: human runs JH with each golden chart; exports *Complete Data XML*. Stored in `tests/differential/jh_exports/{chart_id}.xml`. Committed to repo. Re-exported only when golden charts change (rare).
- Prod-chart exports: nightly, `josiam-jh-runner` GCE Windows instance runs for 10 minutes: `AutoHotkey` script reads chart list from GCS, loads each in JH, exports XML, uploads back to GCS. 50 charts × ~5s/chart = ~5 min.
- Not a hard dependency on the Windows runner — if unavailable, job still runs against golden set + Maitreya only, flagged as partial.

### 3.2 Maitreya9 integration

Maitreya9 is open-source C++. Ship in our differential-test container:

```dockerfile
FROM debian:12 AS maitreya-build
RUN apt-get update && apt-get install -y git build-essential wx-common libwxgtk3.2-dev
RUN git clone https://github.com/martin-pe/maitreya9.git /maitreya
WORKDIR /maitreya
RUN cd src && make console   # CLI binary

FROM python:3.12-slim
COPY --from=maitreya-build /maitreya/bin/maitreya-console /usr/local/bin/
COPY --from=maitreya-build /maitreya/data /usr/local/share/maitreya-data
```

Maitreya CLI invocation:

```bash
maitreya-console --chart birth.ini --output json --techniques yoga,dasa,ashtakavarga
```

Output parsed via our `MaitreyaParser` into a canonical dict.

### 3.3 JH XML parser

JH XML is structured but verbose. Example fragment:

```xml
<Chart>
  <NativeData>
    <DateOfBirth>1973-04-24</DateOfBirth>
    <TimeOfBirth>14:10:00</TimeOfBirth>
    ...
  </NativeData>
  <D1Planets>
    <Planet name="Sun"     sign="Aries"   degree="10.25"  ... />
    ...
  </D1Planets>
  <Yogas>
    <Yoga name="Gaja Kesari" active="Yes" source="BPHS" />
    ...
  </Yogas>
  <VimshottariDasa>
    <MD lord="Jupiter" start="1973-04-24" end="1989-04-23">
      <AD lord="Jupiter" start="1973-04-24" end="1975-06-11"> ... </AD>
      ...
    </MD>
  </VimshottariDasa>
</Chart>
```

Parser maps to canonical intermediate dict with same keys as Josi's outputs.

### 3.4 Per-technique tolerance table

| Technique family | Shape | Tolerance |
|---|---|---|
| Yoga activation | boolean | exact match on `active` |
| Yoga strength | numeric | ±0.05 |
| Vimshottari MD/AD starts | temporal_range | ±1 hour on start/end |
| Yogini / Kalachakra dasa starts | temporal_range | ±1 hour |
| Transit events (Sade Sati) | temporal_event | ±1 day |
| Ashtakavarga bindu matrix | numeric_matrix | ±1 bindu per cell |
| Ashtakavarga totals | numeric | ±2 total |
| Tajaka Muntha sign | structured_positions | exact |
| Jaimini karakas | structured_positions | exact |
| Varga position (D9 sign) | structured_positions | exact |
| House position of planet | structured_positions | exact (whole-sign mode) |
| Planet longitude | numeric | ±0.01° |
| KP sub-lord | structured_positions | exact |

### 3.5 GitHub issue filing

Cluster disagreements by `(technique_family, rule_id)`. One issue per cluster, even if 20 charts disagree. Body:

```markdown
## Differential test disagreement: yoga.raja.gaja_kesari

**Disagreement rate**: 8 of 50 charts (16%)
**Tolerance**: boolean exact

### Sample disagreements

| Chart | Josi | JH | Maitreya |
|---|---|---|---|
| alice-1990 | active | inactive | inactive |
| bob-1975 | active | inactive | active |

### Next steps

- [ ] Review BPHS 36.14-16 activation criteria
- [ ] Check Josi rule body `yoga.raja.gaja_kesari` version 1.2.0
- [ ] Confirm JH's source attribution

Auto-filed by differential test on 2026-04-19.
```

Issues labeled `differential-testing`, assigned to the rule's owner (from `classical_rule.owner_email`, P3-E8-obs).

### 3.6 Known-disagreements budget

`tests/differential/known_disagreements.yaml`:

```yaml
- rule_id: yoga.dhana.lakshmi
  source_id: bphs
  reason: "JH's Lakshmi Yoga uses Raghava Bhatta's activation criteria; Josi uses BPHS 43.5-7."
  references:
    - "BPHS Ch.43 v.5-7"
    - "Raghava Bhatta commentary on BPHS"
  tolerance_override:
    chart_ids: [all]
    outcome: documented_disagreement
  last_reviewed: 2026-03-15

- rule_id: dasa.vimshottari.md_start
  source_id: bphs
  reason: "JH rounds dasa start to midnight; Josi computes exact sub-second."
  tolerance_override:
    field: start_datetime
    tolerance_seconds: 86400   # 1 day
  last_reviewed: 2026-02-20
```

Comparator reads this file before reporting; budgeted disagreements are logged but not filed as issues.

### 3.7 Alternatives considered

| Alternative | Rejected because |
|---|---|
| Only golden-chart diff (no prod sample) | Misses regressions on chart patterns not in golden set |
| Live diff on every chart creation | Too slow; unnecessary given nightly cadence |
| Human review of all disagreements | Doesn't scale; GitHub issues + budget lets humans filter |
| Diff against Parashara's Light, AstroSage, others | Too many tools; JH + Maitreya covers 95% of practitioner community |
| Property-based "all three produce same shape" | Schema agreement ≠ semantic agreement; want values |

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| How to access JH? | Pre-computed XML + nightly Windows runner for fresh charts | Closed-source + Windows-only |
| How to access Maitreya? | Build from source in container; CLI | Open-source + portable |
| Sample size | 50 golden + 50 prod | Fast (~5 min) nightly; statistically meaningful |
| Tolerances | Per-shape, tight but realistic | Matches human-reviewable precision |
| Reporting | GitHub issues per (family, rule) cluster | Groups noise; one ticket per real problem |
| Budget | YAML-committed; reviewed quarterly | Transparent; waivers have justification |
| CI per-PR | Yes, golden only (no Windows) | Fast; catches obvious regressions |
| Anonymization of prod charts | Strip owner, name, location (coord→offset only) | Privacy |
| Auto-fix on disagreement | No | Humans decide which engine is right |

## 5. Component Design

### 5.1 New modules

```
tests/differential/
├── __init__.py
├── run_differential.py              # NEW: main entrypoint
├── jh_parser.py                     # NEW: parse JH XML
├── maitreya_parser.py               # NEW: parse Maitreya CLI output
├── comparator.py                    # NEW: per-shape diff
├── known_disagreements.yaml         # NEW: budget
├── jh_exports/                      # checked-in XML files (50 golden)
│   └── *.xml
├── reports/                         # runtime: generated reports
└── chart_sampler.py                 # NEW: samples golden + recent prod

src/josi/services/differential/
├── __init__.py
├── issue_filer.py                   # NEW: GitHub API integration
├── anonymizer.py                    # NEW: PII stripping for prod charts
└── runner.py                        # NEW: invokes all three engines

docker/
└── Dockerfile.differential          # NEW: container with Josi + Maitreya + parsers

deploy/
└── differential.cloudbuild.yaml     # NEW: nightly cloudbuild trigger

infra/pulumi/
└── jh_runner.py                     # NEW: Windows GCE instance (prod only)
```

### 5.2 Data model additions

```sql
-- Track disagreements over time
CREATE TABLE differential_run (
    id                 BIGSERIAL PRIMARY KEY,
    run_started_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    run_ended_at       TIMESTAMPTZ,
    chart_count        INT NOT NULL,
    total_comparisons  INT NOT NULL,
    disagreements      INT NOT NULL,
    budgeted           INT NOT NULL,              -- within known_disagreements
    unbudgeted         INT NOT NULL,
    jh_available       BOOLEAN NOT NULL DEFAULT true,
    maitreya_available BOOLEAN NOT NULL DEFAULT true,
    report_gcs_uri     TEXT
);

CREATE TABLE differential_disagreement (
    id                 BIGSERIAL PRIMARY KEY,
    run_id             BIGINT NOT NULL REFERENCES differential_run(id),
    chart_id           UUID NOT NULL,
    technique_family   TEXT NOT NULL,
    rule_id            TEXT,
    josi_output        JSONB,
    jh_output          JSONB,
    maitreya_output    JSONB,
    disagreement_type  TEXT CHECK (disagreement_type IN
                         ('josi_vs_jh','josi_vs_maitreya','three_way',
                          'jh_vs_maitreya_only')),
    tolerance_exceeded JSONB,
    is_budgeted        BOOLEAN NOT NULL,
    issue_number       INT,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_disagreement_family_recent
    ON differential_disagreement(technique_family, created_at DESC);
```

### 5.3 Runner skeleton

```python
# tests/differential/run_differential.py

async def run() -> DifferentialReport:
    charts = await sample_charts(n_golden=50, n_prod=50)
    jh_available = await check_jh_xml_availability(charts)
    maitreya_ready = await check_maitreya_build()

    report = DifferentialReport()

    for chart in charts:
        josi_results = await compute_josi(chart)
        jh_results = (await load_jh_xml(chart) if jh_available
                      else None)
        maitreya_results = (await compute_maitreya(chart) if maitreya_ready
                            else None)

        for family in TECHNIQUE_FAMILIES:
            for rule_id in rules_for(family):
                j = josi_results.get((family, rule_id))
                h = jh_results.get((family, rule_id)) if jh_results else None
                m = maitreya_results.get((family, rule_id)) if maitreya_results else None

                disagree = compare(j, h, m, shape_of(family, rule_id))
                if disagree and not is_budgeted(rule_id, chart.chart_id, disagree):
                    report.add(chart.chart_id, family, rule_id, j, h, m, disagree)

    await persist_report(report)
    await file_issues(report.clustered())
    return report
```

### 5.4 Comparator

```python
# tests/differential/comparator.py

TOLERANCES_BY_SHAPE = {
    "boolean_with_strength": {"active": "exact", "strength": 0.05},
    "numeric": 0.05,               # relative 5%
    "numeric_matrix": 1,           # abs 1 per cell
    "temporal_range": {"start": 3600, "end": 3600},
    "temporal_event": 86400,
    "temporal_hierarchy": {"period_start": 3600, "period_end": 3600},
    "structured_positions": "exact",
}

def compare(
    josi: Any, jh: Any, maitreya: Any, shape_id: str,
) -> Disagreement | None:
    if josi is None:
        return Disagreement(type="josi_missing")

    # compare pairs
    jh_match = jh is None or within_tolerance(josi, jh, shape_id)
    m_match = maitreya is None or within_tolerance(josi, maitreya, shape_id)
    if jh_match and m_match:
        return None

    return Disagreement(
        type=_classify(jh, maitreya, jh_match, m_match),
        josi=josi, jh=jh, maitreya=maitreya,
        delta=_delta(josi, jh, maitreya, shape_id),
    )
```

### 5.5 Issue filer

```python
# src/josi/services/differential/issue_filer.py

async def file_issues(
    clusters: list[DisagreementCluster],
    gh_token: str = settings.GITHUB_TOKEN,
) -> list[int]:
    gh = GithubClient(token=gh_token)
    existing = await gh.search_open_issues(label="differential-testing")
    filed = []

    for cluster in clusters:
        title = f"Differential disagreement: {cluster.rule_id} ({cluster.disagreement_rate:.0%})"
        if _already_filed(title, existing):
            continue

        body = render_cluster_markdown(cluster)
        assignee = await _resolve_owner(cluster.rule_id)

        issue = await gh.create_issue(
            repo="josi/josi-svc",
            title=title, body=body, labels=["differential-testing"],
            assignee=assignee,
        )
        filed.append(issue.number)

    return filed
```

### 5.6 Anonymizer

```python
# src/josi/services/differential/anonymizer.py

def anonymize_for_diff(chart: AstrologyChart) -> AnonymizedChart:
    """Strip PII while preserving astrologically relevant inputs."""
    return AnonymizedChart(
        chart_id=chart.chart_id,                 # UUID, not personal
        birth_utc=chart.birth_utc,               # astrologically required
        latitude=_round(chart.latitude, 2),      # ~1km precision (enough)
        longitude=_round(chart.longitude, 2),
        timezone=chart.timezone,
        # owner_user_id, name, location_name: REMOVED
    )
```

### 5.7 CI integration

```yaml
# .github/workflows/differential.yml (added)
name: differential-golden
on: [pull_request]
jobs:
  golden-diff:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run golden differential
        run: |
          docker build -f docker/Dockerfile.differential -t diff .
          docker run --rm -v $PWD:/code diff \
            python tests/differential/run_differential.py --golden-only
      - name: Fail on unbudgeted disagreements
        run: test "${UNBUDGETED_COUNT}" = "0"
```

Runs in < 3 min (no Windows runner available in PR CI; JH data from committed XML).

### 5.8 Cloud Build nightly job

```yaml
# deploy/differential.cloudbuild.yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-f', 'docker/Dockerfile.differential', '-t', 'diff:latest', '.']
  - name: 'diff:latest'
    entrypoint: 'python'
    args: ['tests/differential/run_differential.py', '--prod-sample', '50']
    env:
      - 'GITHUB_TOKEN=$$GITHUB_TOKEN'
      - 'GCS_BUCKET=josiam-diff-reports-prod'
    secretEnv: ['GITHUB_TOKEN']
availableSecrets:
  secretManager:
    - versionName: projects/josiam/secrets/github-differential-token/versions/latest
      env: 'GITHUB_TOKEN'
timeout: '1800s'
```

Triggered by Cloud Scheduler at 03:00 UTC.

## 6. User Stories

### US-C5.1: As an engineer, every night I see whether Josi agrees with JH + Maitreya within tolerance
**Acceptance:** nightly run produces report; summary posted to Slack with disagreement counts per family.

### US-C5.2: As a classical advisor, disagreements on yoga activation are auto-filed as GitHub issues and assigned to me
**Acceptance:** test: inject disagreement → issue created within 30 min of nightly run; assignee matches `owner_email`.

### US-C5.3: As a rule owner, I can waive a known documented disagreement so it stops firing
**Acceptance:** adding YAML entry to `known_disagreements.yaml` suppresses issue; suppression shown in report as "budgeted".

### US-C5.4: As a reviewer on a PR, I see whether my change introduces differential disagreements on golden charts
**Acceptance:** PR CI runs golden-diff; fails if unbudgeted disagreement introduced.

### US-C5.5: As a product owner, I can track disagreement rate per technique over time in a dashboard
**Acceptance:** Grafana dashboard shows `disagreement_rate{family}` trend; target < 1% after P2.

### US-C5.6: As an SRE, if the JH Windows runner is down, the nightly job still runs (partial) and alerts me
**Acceptance:** runner unavailable → Maitreya-only diff runs; Slack alert: "differential: JH runner unavailable"; run marked `partial`.

## 7. Tasks

### T-C5.1: Build Maitreya in Docker
- **Definition:** `docker/Dockerfile.differential` per 3.2. Tests: CLI invokable with test chart.
- **Acceptance:** `docker run diff maitreya-console --version` succeeds.
- **Effort:** 2 days
- **Depends on:** nothing

### T-C5.2: `MaitreyaParser`
- **Definition:** Parses Maitreya CLI JSON output into canonical dict; covers yoga/dasa/ashtakavarga/jaimini.
- **Acceptance:** unit tests against captured CLI outputs for 10 test charts.
- **Effort:** 3 days
- **Depends on:** T-C5.1

### T-C5.3: JH XML parser
- **Definition:** `jh_parser.py` per 3.3; maps XML to canonical dict.
- **Acceptance:** unit tests against committed JH XML for 10 golden charts.
- **Effort:** 3 days
- **Depends on:** JH XML captures available (one-time human task)

### T-C5.4: Comparator + tolerance logic
- **Definition:** `comparator.py` per 5.4. Per-shape tolerances.
- **Acceptance:** exhaustive unit tests per shape + tolerance edge cases.
- **Effort:** 3 days
- **Depends on:** T-C5.2, T-C5.3

### T-C5.5: Chart sampler
- **Definition:** Samples 50 golden + 50 anonymized prod charts; caches to avoid re-sampling same charts.
- **Acceptance:** returns 100 chart objects; anonymized fields absent from prod charts.
- **Effort:** 2 days
- **Depends on:** F16 complete

### T-C5.6: Runner (orchestrator)
- **Definition:** `run_differential.py` per 5.3; runs the three engines in parallel; populates `differential_run` + `differential_disagreement`.
- **Acceptance:** 100-chart run completes in < 20 min; persists rows correctly.
- **Effort:** 3 days
- **Depends on:** T-C5.4, T-C5.5

### T-C5.7: Known-disagreements budget loader
- **Definition:** YAML loader + `is_budgeted()` check; validates every entry has required fields.
- **Acceptance:** malformed YAML fails CI; valid waiver suppresses issue.
- **Effort:** 1 day
- **Depends on:** T-C5.6

### T-C5.8: GitHub issue filer
- **Definition:** `issue_filer.py` per 5.5; uses `GITHUB_TOKEN` from Secret Manager.
- **Acceptance:** synthetic disagreement → issue created; re-run doesn't duplicate.
- **Effort:** 2 days
- **Depends on:** T-C5.6

### T-C5.9: JH Windows runner (prod-only, Pulumi)
- **Definition:** Windows Server 2022 GCE instance with JH pre-installed; AutoHotkey script drives nightly exports; GCS integration for I/O.
- **Acceptance:** instance provisioned; nightly trigger invokes script; XMLs produced in GCS.
- **Effort:** 5 days
- **Depends on:** nothing

### T-C5.10: Cloud Build nightly job
- **Definition:** `deploy/differential.cloudbuild.yaml` per 5.8; Cloud Scheduler trigger.
- **Acceptance:** schedule triggers build; run completes with report uploaded to GCS.
- **Effort:** 1 day
- **Depends on:** T-C5.6, T-C5.8

### T-C5.11: CI integration (PR golden-diff)
- **Definition:** `.github/workflows/differential.yml` per 5.7.
- **Acceptance:** opening a PR runs golden diff in < 3 min; fails on unbudgeted disagreement.
- **Effort:** 1 day
- **Depends on:** T-C5.6

### T-C5.12: Grafana dashboard + Slack alert
- **Definition:** Dashboard: disagreement rate per family over time. Slack: nightly summary to `#josi-differential`.
- **Acceptance:** dashboard live; Slack message posted on each run.
- **Effort:** 1 day
- **Depends on:** T-C5.10

### T-C5.13: Documentation + initial budget
- **Definition:** `docs/markdown/runbooks/differential-testing.md`. Initial `known_disagreements.yaml` with ~5 documented cases per classical advisor input.
- **Acceptance:** doc merged; budget PR merged by classical advisor.
- **Effort:** 2 days
- **Depends on:** T-C5.12

### T-C5.14: Anonymizer for prod charts
- **Definition:** `anonymizer.py` per 5.6. Unit tests.
- **Acceptance:** anonymized chart has no PII fields but retains astrological inputs.
- **Effort:** 1 day
- **Depends on:** nothing

## 8. Unit Tests

### 8.1 JH parser

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_jh_parser_extracts_d1_positions` | sample XML | dict of planet→(sign, degree) | core |
| `test_jh_parser_extracts_yogas` | XML with 5 yogas | list of 5 dicts | list parsing |
| `test_jh_parser_extracts_vimshottari` | XML with nested MD/AD/PD | nested structure | nesting |
| `test_jh_parser_handles_empty_dasa` | XML with no dasa | empty list, no crash | robustness |
| `test_jh_parser_malformed_xml_raises` | garbage input | raises ParseError | safety |

### 8.2 Maitreya parser

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_maitreya_parser_basic` | JSON output | canonical dict | core |
| `test_maitreya_parser_numeric_precision` | CLI float output | preserves to 4 decimals | precision |
| `test_maitreya_cli_timeout_handled` | runner mocks 60s hang | raises CliTimeoutError | safety |

### 8.3 Comparator

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_bool_exact_match_no_disagree` | active=True, True, True | None | happy |
| `test_bool_disagreement` | active=True, False, True | Disagreement(josi_vs_jh) | basic |
| `test_strength_within_tolerance` | 0.70, 0.72, 0.73 | None | ±0.05 respected |
| `test_strength_outside_tolerance` | 0.70, 0.80, 0.70 | Disagreement | ±0.05 enforced |
| `test_temporal_within_1hr` | starts differ by 30min | None | ±1hr |
| `test_temporal_event_outside_1day` | events differ 30hr | Disagreement | ±1day |
| `test_numeric_matrix_1_bindu_per_cell` | matrices differ 1 each | None | ashtakavarga |
| `test_missing_maitreya_only_vs_jh` | josi ok, jh ok, maitreya None | None | partial |
| `test_jh_maitreya_agree_josi_wrong` | josi=A, jh=B, maitreya=B | Disagreement | both-outnumber-one |

### 8.4 Known-disagreements budget

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_budget_suppresses_matching_rule` | disagreement on budgeted rule | is_budgeted=True | waiver |
| `test_budget_scoped_to_chart_ids` | rule has `chart_ids: [specific]` | only specific chart suppressed | precision |
| `test_budget_invalid_yaml_fails` | malformed YAML | raises at load | CI guard |
| `test_budget_missing_reason_rejected` | entry without reason | validation error | accountability |

### 8.5 Issue filer

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_filer_creates_one_issue_per_cluster` | 8 disagreements all same rule | 1 issue | deduplication |
| `test_filer_skips_existing_open_issue` | re-run with same cluster | no new issue | idempotency |
| `test_filer_assigns_owner_from_metadata` | rule with owner=foo | issue assignee=foo | routing |
| `test_filer_skips_when_gh_token_missing` | no token | logs + skips (no crash) | resilience |

### 8.6 Anonymizer

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_anonymize_removes_name` | chart with owner_name=Alice | result has no `owner_name` | privacy |
| `test_anonymize_rounds_coords` | lat=37.7749281 | lat=37.77 | granularity |
| `test_anonymize_preserves_birth_utc` | birth_utc set | unchanged | astrological correctness |

### 8.7 Runner integration

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_runner_golden_only_mode` | --golden-only flag | only 50 charts processed | fast CI path |
| `test_runner_handles_jh_unavailable` | JH XMLs missing | runs Maitreya-only; marks run partial | resilience |
| `test_runner_persists_report_to_db` | complete run | differential_run row with counts | audit |
| `test_runner_exit_code_on_unbudgeted` | 1 unbudgeted disagreement | exit 1 | CI integration |
| `test_runner_exit_code_zero_when_budgeted` | all disagreements budgeted | exit 0 | budget works |

### 8.8 CI integration

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_pr_fails_on_unbudgeted_golden_disagreement` | PR breaks a golden rule | workflow fails | gate |
| `test_pr_passes_on_budgeted_disagreement` | PR introduces doc'd waiver | workflow passes | waiver respected |
| `test_pr_completes_in_under_3_minutes` | 50-chart golden diff | ≤ 180s wall time | dev ergonomics |

## 9. EPIC-Level Acceptance Criteria

- [ ] Maitreya9 built in container; CLI invocation works
- [ ] JH XML parser handles golden chart files
- [ ] Comparator implements per-shape tolerances
- [ ] Chart sampler returns 50 golden + 50 anonymized prod charts
- [ ] Runner orchestrates three-way diff; persists report
- [ ] `known_disagreements.yaml` loader + `is_budgeted` check
- [ ] GitHub issue filer: one issue per cluster; assigns rule owner
- [ ] JH Windows runner provisioned (prod); nightly exports to GCS
- [ ] Cloud Build nightly job scheduled at 03:00 UTC
- [ ] CI per-PR golden-diff workflow live; runs in < 3 min
- [ ] Grafana dashboard: disagreement rate per family over time
- [ ] Slack summary posted nightly
- [ ] Target: < 1% disagreement rate per technique at end of P2 (measured)
- [ ] Unit test coverage ≥ 90% for new modules
- [ ] Runbook merged; initial budget ~5 entries merged by classical advisor

## 10. Rollout Plan

- **Feature flag:** none at runtime — this is a CI + nightly job, off-path from users.
- **Shadow compute:** N/A.
- **Backfill strategy:**
  - Week 1: build infra (Maitreya container, parsers, comparator).
  - Week 2: run golden diff only; bootstrap budget with documented disagreements.
  - Week 3: enable prod sample (after JH runner provisioned); run 7 nights; fix real bugs.
- **Rollback plan:**
  1. Disable Cloud Scheduler trigger for nightly.
  2. Remove CI workflow file (PRs continue without golden diff).
  3. Keep infra in place for re-enabling.

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| JH Windows runner unreliable | Medium | Medium | Graceful degradation to Maitreya-only; Slack alert on failure |
| Maitreya build breaks on upgrade | Low | Medium | Pinned git commit in Dockerfile; upgrade intentionally |
| High initial disagreement rate (> 20%) | High (certain) | Medium | Budget + prioritize fixes; classical advisor weekly triage |
| False-positive disagreements from parser bugs | Medium | High | Unit tests against captured golden outputs; 2-engineer review of parsers |
| GitHub issue spam | Medium | Low | Cluster by (family, rule); skip if open issue exists |
| PII leaks via anonymized prod charts | Low | High | Anonymizer unit-tested; 2-day review of output samples before enabling prod sampling |
| CI duration > 3 min blocks developer workflow | Medium | Low | Profile; parallelize charts; skip expensive diffs in CI |
| Legal concerns about JH XML sharing | Low | High | Golden charts are synthetic; prod-chart JH exports stored in private GCS; no public distribution |
| Maitreya9 project abandoned | Low | Medium | Fork at pinned commit; consider adding Swiss Ephemeris Python direct diff as backup |

## 12. References

- Master spec: [`docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`](../../../superpowers/specs/2026-04-19-classical-techniques-expansion-design.md)
- Depends on: [E15a](../P1/E15a-correctness-harness-v1.md), [F16](../P0/F16-golden-chart-suite.md), [F17](../P0/F17-property-based-test-harness.md)
- Jagannatha Hora: http://www.vedicastrologer.org/jh/
- Maitreya9: https://github.com/martin-pe/maitreya9
- Differential testing literature: McKeeman (1998), "Differential Testing for Software"
- Success metric (spec §8.1): "Differential testing against JH/Maitreya: disagreement rate < 1% per technique after P2"
