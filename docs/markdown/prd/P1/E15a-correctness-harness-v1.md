---
prd_id: E15a
epic_id: E15
title: "Correctness Harness v1 (golden suite + property tests in CI)"
phase: P1-mvp
tags: [#correctness]
priority: must
depends_on: [F8, F13, F16, F17, E1a, E2a, E4a, E6a]
enables: [E11a, E14a, C5, P3-E8-obs]
classical_sources: [bphs, saravali, phaladeepika, jataka_parijata, jaimini_sutras, tajaka_neelakanthi]
estimated_effort: 3-4 weeks
status: draft
author: @agent
last_updated: 2026-04-19
---

# E15a — Correctness Harness v1

## 1. Purpose & Rationale

Classical astrology calculation is only as valuable as its correctness. The master spec commits to a **golden chart suite green rate ≥ 99.5% per deploy** (spec §8.1). F16 ships the scaffolding — directory layout, loader, 20 seed charts — and F17 ships the property-based test harness. E15a makes correctness a **non-negotiable CI gate** for all P1 engines.

Three concrete deliverables:

1. **Grow the golden chart suite from 20 to 100 curated charts.** Famous historical figures with public birth data and published classical commentary provide both the inputs and the expected outputs. Each added chart cites the commentary book and page range for its expected outputs.
2. **Extend expected outputs to every P1 engine.** E1a adds Yogini + Ashtottari dasa periods. E2a adds Ashtakavarga shodhana values. E4a adds per-yoga activation status. E6a adds transit event windows.
3. **CI gate.** Golden suite runs on every PR; any regression below 99% (fail-fast threshold) blocks merge. Property tests run at `max_examples=500` per commit, `max_examples=10000` nightly. A **deploy gate** rolls back automatically if post-deploy pass rate drops below 99%.

E15a is the safety net that lets E11a (AI chat) cite accurate classical values and E14a (experiments) measure real differences between strategies instead of noise from bugs.

## 2. Scope

### 2.1 In scope

- Grow golden chart suite from 20 (F16) to **100 curated charts**
- Source charts: famous historical figures with public birth data + published commentary
- Expected outputs added per chart for every P1 technique:
  - Yogini dasa: all 8 mahadashas (lord, span)
  - Ashtottari dasa: all 8 mahadashas
  - Ashtakavarga: per-planet `sarvashtakavarga`, `bhinnashtakavarga`, `trikona_shodhit`, `ekadhipatya_shodhit`
  - Yogas: activation status + strength for all 60 MVP yogas
  - Transits: Sade Sati phase boundaries; major transit event windows
- CI integration: GitHub Actions job `golden-suite` runs on every PR
- Failed-chart annotations surfaced as GitHub PR comments via `::error file=...` directives
- Property tests from F17 wired to CI at `max_examples=500`
- Nightly CI job running property tests at `max_examples=10000`
- New invariants for P1:
  - Yogini: sum of 8 mahadashas == 36 years (exact)
  - Ashtottari: sum == 108 years (exact)
  - Ashtakavarga: trikona shodhit ≤ pre-shodhit cellwise
  - Yoga active count per chart ∈ [0, 60]
  - All dasa periods: monotonic non-overlapping temporal order
  - All engines: idempotent compute (same inputs → same output hash)
- Fail-fast threshold: deploy rolls back if post-deploy golden suite < 99%
- Weekly correctness report: pass rate, property-test discoveries, top flaky tests
- Tooling for adding a new golden chart (CLI scaffold)
- Documentation for classical advisors authoring expected outputs

### 2.2 Out of scope

- **Differential testing against JH / Maitreya** — C5 (P3)
- **UI for inspecting golden-suite results** — out of scope for v1; CI annotations suffice
- **Expected outputs for P2 techniques** (Jaimini, Tajaka, extended vargas) — E15a v2 / per-engine PRDs
- **Classical advisor onboarding program** — operational / org concern, not in this PRD
- **Chaos / fault-injection tests** — P3
- **Mutation testing** — maybe P3
- **Perf regression tests** — separate concern; handled under S2/S3
- **Full 1000-chart suite** — Reference-1000 (P4)

### 2.3 Dependencies

- F8 aggregation Protocol (property tests exercise strategy invariants)
- F13 content-hash provenance (idempotency assertion)
- F16 golden chart suite scaffolding (loader, directory, 20 seed charts)
- F17 property-based test harness (Hypothesis, shrinking, DB fixtures)
- E1a (Yogini + Ashtottari engines producing dasa outputs)
- E2a (Ashtakavarga with shodhana)
- E4a (60 MVP yogas)
- E6a (Transit intelligence)
- GitHub Actions (existing CI provider)
- Cloud Build (post-deploy verification runs here; see deploy folder)

## 3. Technical Research

### 3.1 Why 100 charts

- 20 is enough to catch gross bugs but misses combinatorial coverage (e.g., water-sign ascendants with retrograde Mars).
- 100 gives ≥ 8 examples per zodiac ascendant, ≥ 10 per dominant dasa lord at birth, and at least 1 chart triggering each of the 60 MVP yogas.
- 100 is hand-curatable in 3 weeks; 1000 is not (that's Reference-1000 territory).
- Statistics: at 99% pass-rate gate, one failure in 100 is exactly 1%, which equals the fail-fast threshold of < 99%. So the threshold is directly interpretable.

### 3.2 Source material

Priority criteria: (1) birth data in public record, (2) published classical commentary with numeric claims, (3) stylistic diversity.

Candidates (non-exhaustive; final list curated in T-E15a.2):

| Figure | Classical Commentary Source | Notes |
|---|---|---|
| Ramana Maharshi | K.N. Rao's *Predicting through Jaimini* (incl. Parashari cross-ref) | Spiritual luminary; Jaimini diagnostic |
| Jiddu Krishnamurti | B.V. Raman's *Notable Horoscopes* | Philosopher; strong yoga chart |
| Paramahansa Yogananda | Raman's *Notable Horoscopes* | Guru, solar Cancer ascendant |
| Ramakrishna Paramahansa | Traditional commentaries (multiple) | Mystic, specific yogas cited |
| Mahatma Gandhi | Raman; Dr. B.V. Raman's *Three Hundred Important Combinations* | Statesman; Rahu-Ketu emphasis |
| Jawaharlal Nehru | Raman | Politician; classic raja yogas |
| Indira Gandhi | Raman | Similar raja yoga set |
| Albert Einstein | Raman (Western + Vedic cross) | Western-recorded birth; validates sidereal conversion |
| C.G. Jung | Western commentators + Liz Greene | Western-dominant; tests cross-tradition |
| Queen Elizabeth II | British Records + Raman | Long-life chart; Vimshottari span validation |
| Steve Jobs | Public (8:15pm Feb 24 1955 San Francisco) | Modern; AK dasa transitions documented publicly |
| APJ Abdul Kalam | Raman + Hindu astrologer publications | Technology-leader chart; multi-yoga |
| Rabindranath Tagore | Traditional commentaries | Poet-laureate |
| Sri Aurobindo | Raman + ashram publications | Sage; very dense yoga chart |
| Swami Vivekananda | Raman | Spiritual; specific Neecha-bhanga references |
| B.V. Raman | autobiography | Meta-chart; self-commentary |
| Winston Churchill | Western records | Western-dominant, long-life |
| Abraham Lincoln | Public record | Western-tested; eclipses around assassination |
| Nelson Mandela | Public records + interviews with astrologers | Sade Sati analysis well-documented |
| … (another 80 to reach 100) | Mix of historical + public-figure charts with verifiable birth data | |

Each golden chart YAML cites specific commentary (book, edition, page) justifying each expected value.

### 3.3 Golden chart YAML format (extends F16)

```yaml
# tests/golden/charts/krishnamurti.yaml
chart_id: "golden-krishnamurti"
meta:
  name: "Jiddu Krishnamurti"
  source_book: "Raman, B.V. — Notable Horoscopes (Motilal Banarsidass, 1991 ed.), pp. 128-132"
  license_note: "Birth data public record"

birth:
  date: "1895-05-12"
  time: "00:30:00"
  tz: "+05:21:10"
  place: "Madanapalle, Andhra Pradesh, India"
  lat: 13.5500
  lon: 78.5000

ayanamsa: "lahiri"
house_system: "whole_sign"

expected:
  lagna_sign: "scorpio"

  vimshottari_md_sequence:
    - { lord: "venus", start: "1895-05-12", end: "1913-05-20", citation: "Raman p.128" }
    - { lord: "sun",   start: "1913-05-20", end: "1919-05-20", citation: "Raman p.128" }
    # ... full 9-lord cycle

  yogini_md_sequence:
    - { lord: "mangala",  start: "1895-05-12", end: "1896-05-12" }
    - { lord: "pingala",  start: "1896-05-12", end: "1898-05-12" }
    # ... sum to 36 years

  ashtottari_md_sequence:
    - { lord: "sun",      start: "...", end: "..." }
    # ... sum to 108 years

  ashtakavarga:
    sarvashtakavarga:
      by_sign: [30, 28, 34, 25, 26, 31, 30, 29, 33, 27, 31, 28]   # 12 signs
    bhinnashtakavarga:
      sun:     [4, 3, 5, 4, 3, 4, 3, 5, 3, 4, 4, 2]
      # ... per planet
    trikona_shodhit:
      sun:     [0, 3, 5, 0, 3, 4, 0, 5, 3, 0, 4, 2]
    ekadhipatya_shodhit:
      sun:     [0, 3, 5, 0, 3, 4, 0, 5, 3, 0, 4, 2]

  yogas_active:
    - { yoga_id: "gaja_kesari", active: true,  strength_range: [0.6, 0.9],
        citation: "Raman p.129: Moon in Cancer, Jupiter in kendra" }
    - { yoga_id: "neecha_bhanga_raja_yoga", active: true, strength_range: [0.5, 0.8] }
    - { yoga_id: "budha_aditya_yoga", active: false }
    # ... all 60 with active/inactive

  transit_sade_sati:
    - { phase: "rising", start: "1944-03-02", end: "1946-07-15" }
    - { phase: "peak",   start: "1946-07-15", end: "1949-01-03" }
    - { phase: "setting",start: "1949-01-03", end: "1951-06-20" }
```

Strength ranges accommodate aggregation-strategy variance (§1.3 master spec); exact point values only where classical source fixes them.

### 3.4 Tolerance model

- **Temporal values** — ±24h for dasa boundaries, ±3 days for transit events (accounts for ephemeris variance).
- **Numeric values** — exact match for ashtakavarga bindu counts; ±2% for derived strengths.
- **Boolean values** — exact match for yoga activation.
- **Range values** — observed value must be within declared `strength_range`.

Tolerances configurable per expected field; default policy documented.

### 3.5 Property-test invariants (v1 additions over F17)

```python
# Yogini
@given(chart=valid_chart_strategy())
def test_yogini_sum_36_years(chart):
    periods = yogini_engine.compute(chart)
    total = sum((p.end - p.start).total_seconds() for p in periods)
    assert abs(total / (365.25 * 86400) - 36.0) < 1e-6

# Ashtottari
@given(chart=valid_chart_strategy())
def test_ashtottari_sum_108_years(chart):
    periods = ashtottari_engine.compute(chart)
    total = sum((p.end - p.start).total_seconds() for p in periods)
    assert abs(total / (365.25 * 86400) - 108.0) < 1e-6

# Ashtakavarga shodhana monotonicity
@given(chart=valid_chart_strategy())
def test_trikona_shodhana_monotonic(chart):
    av = ashtakavarga_engine.compute(chart)
    for planet, cells in av.bhinnashtakavarga.items():
        for i, pre in enumerate(cells):
            assert av.trikona_shodhit[planet][i] <= pre

# Yoga count bounded
@given(chart=valid_chart_strategy())
def test_yoga_active_count_bounded(chart):
    yogas = yoga_engine.compute(chart)
    assert 0 <= sum(1 for y in yogas if y.active) <= 60

# Dasa temporal order
@given(chart=valid_chart_strategy(), system=dasa_system_strategy())
def test_dasa_periods_monotonic_non_overlapping(chart, system):
    periods = dasa_engine.compute(chart, system=system)
    for a, b in pairwise(periods):
        assert a.end == b.start   # contiguous, no gap or overlap

# Idempotency (F13)
@given(chart=valid_chart_strategy())
def test_compute_idempotent(chart):
    r1 = engine.compute(chart)
    r2 = engine.compute(chart)
    assert output_hash(r1) == output_hash(r2)
```

### 3.6 CI architecture

```
GitHub PR opened / updated
  ↓
GitHub Actions workflow: .github/workflows/correctness.yml
  ├── lint + type-check (existing)
  ├── unit tests (existing)
  ├── golden-suite (NEW): poetry run pytest tests/golden -v --json-report
  │       → parse report → emit ::error file=... annotations
  │       → fail job if pass_rate < 99%
  └── property-tests-quick (NEW): HYPOTHESIS_MAX_EXAMPLES=500
          → fail on any discovery

Nightly cron (02:00 UTC):
  └── property-tests-full: HYPOTHESIS_MAX_EXAMPLES=10000
          → file GitHub issue on discovery

Cloud Build post-deploy hook (deploy/api.cloudbuild.*.yaml):
  └── run golden-suite against deployed env
          if pass_rate < 99%: trigger rollback of Cloud Run revision
```

### 3.7 Alternatives considered

| Alternative | Rejected because |
|---|---|
| Allow classical-advisor expected outputs to be approximate prose | Can't assert mechanically; defeats CI gate |
| Run golden suite only on main merges | Catches issues too late; PR gate required |
| Skip property tests in PR CI for speed | Cheap variants (500 examples) add < 2 min; too valuable to skip |
| Store expected outputs in DB rather than YAML | YAML is reviewable in PRs; DB hides provenance |
| Use pytest-xdist to parallelize | Adds flakiness in DB-bound tests; serial is acceptable at 100 charts |

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| How many charts | 100 | Sweet spot between coverage and curatability |
| Fail-fast threshold | 99% (≤ 1 failure in 100) | Interpretable; matches pass-rate target |
| Tolerance model | Per-field configurable with documented defaults | Accommodates ephemeris/strategy variance |
| Property-test cadence | 500 per PR, 10,000 nightly | Good cost/coverage balance |
| Where do classical advisors edit | YAML files in PRs, reviewed by engineer + advisor | Two-eyes rule (spec §6.1) |
| CI provider | GitHub Actions for PRs, Cloud Build for post-deploy | Matches existing stack (CLAUDE.md memory) |
| Rollback trigger | < 99% post-deploy golden pass rate | Automated safety |
| Nightly property discovery workflow | File GitHub issue with shrink-minimized counterexample | Tracks as bug; auto-assigns to module owner |
| Birth-time precision policy | Record-quoted precision; lower confidence on rectified times | Prevents false failures on unrectified births |
| What when commentary disagrees with computed value | Tag expected with `commentary_disagreement=true`, use `computed` as canonical, file docs note | We validate engine, not the book |
| Expected outputs versioning | Each YAML carries `expected_schema_version`; bumped when format changes | Forward/back compat |
| Flakiness threshold | Test flagged if it fails ≥ 2× in trailing 20 runs | Weekly report highlights |

## 5. Component Design

### 5.1 New modules

```
tests/golden/
├── charts/                              # 100 curated chart YAMLs
│   ├── krishnamurti.yaml
│   ├── ramana.yaml
│   ├── einstein.yaml
│   └── ... (100 total)
├── loader.py                            # extended from F16
├── comparators/
│   ├── __init__.py
│   ├── temporal.py                      # ±24h dasa, ±3d transit
│   ├── numeric.py                       # exact + ±2% variants
│   ├── boolean.py
│   └── range.py
├── runner.py                            # orchestrates per-chart validation
├── report.py                            # JSON report + GitHub annotations
└── test_golden_suite.py                 # pytest entry point

tests/property/
├── engines/
│   ├── test_yogini_invariants.py
│   ├── test_ashtottari_invariants.py
│   ├── test_ashtakavarga_invariants.py
│   ├── test_yoga_engine_invariants.py
│   ├── test_transit_invariants.py
│   └── test_idempotency.py              # all engines
└── strategies.py                        # Hypothesis strategies (extends F17)

scripts/
├── golden_add_chart.py                  # CLI: scaffold new golden chart
└── correctness_weekly_report.py         # computes + emails weekly report

.github/workflows/
└── correctness.yml                      # PR + nightly CI jobs

deploy/
├── api.cloudbuild.dev.yaml              # extend with post-deploy golden check
└── api.cloudbuild.prod.yaml             # extend with post-deploy golden check + rollback
```

### 5.2 No data model additions

E15a is test infrastructure only. No production DB changes. (A `golden_run` table for history is optional and deferred to P3-E8-obs observability.)

### 5.3 Comparator interfaces

```python
# tests/golden/comparators/base.py

class Comparator(Protocol):
    name: str
    def compare(self, expected: Any, actual: Any, tolerance: dict | None = None) -> ComparisonResult: ...

@dataclass
class ComparisonResult:
    passed: bool
    message: str
    delta: Any | None = None
```

```python
# tests/golden/comparators/temporal.py

class TemporalRangeComparator:
    name = "temporal_range"

    def compare(self, expected: dict, actual: dict, tolerance: dict | None = None) -> ComparisonResult:
        tol = tolerance or {"boundary_seconds": 86400}  # ±24h default for dasa
        start_ok = abs((expected["start"] - actual["start"]).total_seconds()) <= tol["boundary_seconds"]
        end_ok   = abs((expected["end"]   - actual["end"]).total_seconds())   <= tol["boundary_seconds"]
        return ComparisonResult(
            passed=start_ok and end_ok,
            message=f"start_delta={...}, end_delta={...}",
        )
```

### 5.4 Runner

```python
# tests/golden/runner.py

class GoldenSuiteRunner:
    async def run(self, chart_filter: str | None = None) -> GoldenSuiteReport:
        charts = self.loader.load_all(filter=chart_filter)
        results = []
        for chart in charts:
            result = await self._run_one(chart)
            results.append(result)
        return GoldenSuiteReport(
            total=len(results),
            passed=sum(1 for r in results if r.passed),
            results=results,
        )

    async def _run_one(self, chart: GoldenChart) -> GoldenChartResult:
        actual = await compute_all_p1_engines(chart.birth)
        checks = []
        for field, expected in chart.expected.items():
            comparator = COMPARATOR_REGISTRY[schema_of(field)]
            checks.append((field, comparator.compare(expected, actual[field])))
        return GoldenChartResult(chart_id=chart.id, checks=checks,
                                 passed=all(c[1].passed for c in checks))
```

### 5.5 CI workflow

```yaml
# .github/workflows/correctness.yml
name: correctness

on:
  pull_request:
  schedule:
    - cron: "0 2 * * *"   # 02:00 UTC nightly

jobs:
  golden-suite:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install Poetry + deps
        run: |
          pipx install poetry
          poetry install --no-interaction
      - name: Run golden suite
        run: poetry run pytest tests/golden -v --json-report --json-report-file=report.json
      - name: Emit GitHub annotations
        if: always()
        run: poetry run python scripts/emit_golden_annotations.py report.json
      - name: Enforce 99% pass rate
        run: poetry run python scripts/enforce_pass_rate.py report.json 0.99

  property-tests-quick:
    if: github.event_name == 'pull_request'
    runs-on: ubuntu-latest
    env:
      HYPOTHESIS_MAX_EXAMPLES: "500"
    steps:
      - uses: actions/checkout@v4
      - run: |
          pipx install poetry
          poetry install --no-interaction
          poetry run pytest tests/property -v

  property-tests-full:
    if: github.event_name == 'schedule'
    runs-on: ubuntu-latest
    env:
      HYPOTHESIS_MAX_EXAMPLES: "10000"
    steps:
      - uses: actions/checkout@v4
      - run: |
          pipx install poetry
          poetry install --no-interaction
          poetry run pytest tests/property -v --tb=short
      - name: File issue on failure
        if: failure()
        uses: JasonEtco/create-an-issue@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### 5.6 Post-deploy rollback hook

Cloud Build step appended to `deploy/api.cloudbuild.{dev,prod}.yaml`:

```yaml
- name: gcr.io/cloud-builders/gcloud
  id: post-deploy-golden-check
  entrypoint: bash
  args:
    - -c
    - |
      TARGET_URL=$(gcloud run services describe josi-api-$_ENV --region=us-central1 --format='value(status.url)')
      poetry run python scripts/remote_golden_check.py --target "$TARGET_URL" --threshold 0.99 || {
        gcloud run services update-traffic josi-api-$_ENV --to-revisions=PREV=100 --region=us-central1
        exit 1
      }
```

## 6. User Stories

### US-E15a.1: As an engineer opening a PR, I immediately see which golden charts regressed
**Acceptance:** PR status check `golden-suite` shows pass/fail; failing charts annotated inline via `::error file=tests/golden/charts/X.yaml,line=42::...`; PR comment summarizes `N/100 charts passed`.

### US-E15a.2: As an engineer, I cannot merge a PR that fails 2+ golden charts
**Acceptance:** Branch protection rule on `main` requires `golden-suite` success; 2/100 failures → job fails (< 99%) → merge blocked.

### US-E15a.3: As a classical advisor, I can add a new golden chart via CLI and YAML
**Acceptance:** Running `poetry run python scripts/golden_add_chart.py --name "C.G. Jung"` scaffolds a YAML with placeholders; advisor fills expected values; PR review passes.

### US-E15a.4: As the on-call engineer, a bad deploy auto-rolls back when golden regression detected
**Acceptance:** Staging deploy with a deliberately broken engine rolls back Cloud Run revision within 2 min; Slack alert posted.

### US-E15a.5: As the product team, I receive a weekly correctness report
**Acceptance:** Every Monday 09:00 IST, email with: current golden-suite pass rate, property-test discoveries past week, top 5 flaky tests, trend chart.

### US-E15a.6: As an engineer, Yogini mahadasha periods in my P1 engine must sum to exactly 36 years
**Acceptance:** Property test `test_yogini_sum_36_years` fails if any synthetic chart produces wrong total.

### US-E15a.7: As an engineer, I can run the full golden suite locally in under 3 minutes
**Acceptance:** `poetry run pytest tests/golden -v` completes in < 3 min on reference laptop.

### US-E15a.8: As a maintainer, flaky tests are automatically surfaced in the weekly report
**Acceptance:** Test that fails ≥ 2 times in trailing 20 runs appears in the report's "flaky" section.

## 7. Tasks

### T-E15a.1: Define tolerance model + comparator registry
- **Definition:** Implement 4 comparators (temporal, numeric, boolean, range). Default tolerances documented.
- **Acceptance:** Unit tests green; docstrings describe defaults.
- **Effort:** 1 day
- **Depends on:** F16

### T-E15a.2: Curate 80 new golden chart YAMLs (beyond F16's 20)
- **Definition:** Research + draft 80 additional charts from the candidates in §3.2 and similar. Each with classical commentary citations.
- **Acceptance:** 100 total YAMLs pass schema validation; spot-check of 10 yields correct birth data.
- **Effort:** 10 working days (parallel with engineers via advisor)
- **Depends on:** T-E15a.1

### T-E15a.3: Expected outputs per P1 engine
- **Definition:** For each of 100 charts, fill in:
  - Yogini and Ashtottari period tables
  - Ashtakavarga bindu + shodhana tables
  - All 60 yogas with active flags + strength ranges
  - Sade Sati phase boundaries and major transit events
- **Acceptance:** Every YAML has all P1 fields; schema validation passes.
- **Effort:** 8 days (automated pre-fill by engines + human verification)
- **Depends on:** T-E15a.2 and E1a, E2a, E4a, E6a all complete

### T-E15a.4: Runner + report
- **Definition:** `GoldenSuiteRunner`, `GoldenSuiteReport`, JSON emit for CI.
- **Acceptance:** `poetry run pytest tests/golden` runs end-to-end; JSON report parseable.
- **Effort:** 3 days
- **Depends on:** T-E15a.1

### T-E15a.5: GitHub annotation emitter + pass-rate enforcer
- **Definition:** Scripts to convert JSON report into GH `::error` directives and to exit non-zero if pass rate < 99%.
- **Acceptance:** Faked failure in a branch produces annotations; PR blocked.
- **Effort:** 1 day
- **Depends on:** T-E15a.4

### T-E15a.6: Property-test invariants (Yogini, Ashtottari, Ashtakavarga shodhana, Yoga bound, dasa temporal order, idempotency)
- **Definition:** 6 new property test modules built on F17 harness.
- **Acceptance:** Each test runs at `HYPOTHESIS_MAX_EXAMPLES=500` in < 30s; each has a fixed-seed regression case.
- **Effort:** 4 days
- **Depends on:** F17, engines complete

### T-E15a.7: CI workflow
- **Definition:** `.github/workflows/correctness.yml` with `golden-suite`, `property-tests-quick`, `property-tests-full` jobs.
- **Acceptance:** Dry-run on fork passes; ToPR shows all 3 checks.
- **Effort:** 1 day
- **Depends on:** T-E15a.4, T-E15a.6

### T-E15a.8: Post-deploy verify + rollback
- **Definition:** Cloud Build steps appended to `deploy/api.cloudbuild.dev.yaml` and `deploy/api.cloudbuild.prod.yaml`; `scripts/remote_golden_check.py` probes a remote endpoint `/internal/golden-check` (new; staff-auth).
- **Acceptance:** In dev, simulated bad deploy rolls back; good deploy completes. Rollback event logged to Slack.
- **Effort:** 2 days
- **Depends on:** T-E15a.4

### T-E15a.9: `golden_add_chart.py` CLI + docs
- **Definition:** Command to scaffold a new golden YAML; doc for classical advisors under `docs/markdown/correctness/authoring-golden-charts.md`.
- **Acceptance:** Classical advisor unfamiliar with code can add a chart given the doc.
- **Effort:** 1 day

### T-E15a.10: Weekly report
- **Definition:** `scripts/correctness_weekly_report.py` reads CI history + flaky detection; emits HTML email. Scheduled via GitHub Actions cron Monday 03:30 UTC.
- **Acceptance:** Sample email reviewed and approved; email delivered to `eng-weekly@josiam.com`.
- **Effort:** 2 days

### T-E15a.11: Internal `/internal/golden-check` endpoint
- **Definition:** Staff-only endpoint that runs the golden suite against the live process's compute engines and returns pass rate; used by the post-deploy rollback step.
- **Acceptance:** Returns `{total, passed, pass_rate, failures: [...]}`; requires staff token.
- **Effort:** 1 day

### T-E15a.12: Docs + CLAUDE.md updates
- **Definition:** Add `docs/markdown/correctness/v1.md`; update CLAUDE.md to note the golden suite is a merge gate and how to run it locally.
- **Acceptance:** Docs reviewed and linked from INDEX.
- **Effort:** 0.5 day

## 8. Unit Tests

### 8.1 Comparators

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_temporal_within_tolerance` | expected/actual differ by 12h, tol 24h | pass | tolerance applied |
| `test_temporal_outside_tolerance` | differ by 30h | fail | boundary enforced |
| `test_numeric_exact_match` | 5 == 5 | pass | integer equality |
| `test_numeric_percent_tolerance` | expected 100, actual 101.5, tol ±2% | pass | pct tolerance |
| `test_boolean_strict_match` | True vs False | fail | no slack |
| `test_range_value_in_bounds` | actual 0.7, range [0.6, 0.9] | pass | range comparator |
| `test_range_value_below_bounds` | actual 0.5, range [0.6, 0.9] | fail | range boundary |

### 8.2 Runner

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_runner_loads_all_charts` | 100 YAMLs | report.total == 100 | loader integration |
| `test_runner_filters_by_chart_id` | filter="krishnamurti" | only 1 chart run | developer workflow |
| `test_runner_handles_missing_expected_fields_gracefully` | YAML missing `yogini_md_sequence` | check skipped with warning, not failure | forward compat |
| `test_runner_json_report_shape` | report | has `total, passed, results[]` | CI contract |

### 8.3 Annotation emitter

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_emit_no_failures_no_output` | all-pass report | 0 annotations | silent success |
| `test_emit_format_is_github_compatible` | 1 failure | one `::error file=...::` line | GH annotation spec |
| `test_enforce_pass_rate_blocks_below_threshold` | 98% pass | exit code 1 | gate enforcement |
| `test_enforce_pass_rate_allows_at_threshold` | 99% pass | exit code 0 | boundary |

### 8.4 Property invariants

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_yogini_sum_36_years` | 500 random charts | all return 36 year total | lifetime invariant |
| `test_ashtottari_sum_108_years` | 500 random charts | all return 108 year total | lifetime invariant |
| `test_ashtakavarga_trikona_shodhana_monotonic` | 500 random charts | trikona ≤ pre cellwise | shodhana correctness |
| `test_yoga_active_count_in_bounds` | 500 random charts | count ∈ [0, 60] | bounded output |
| `test_dasa_periods_contiguous` | 500 random charts, 2 systems | adjacent period a.end == b.start | temporal invariant |
| `test_compute_idempotent_engine_X` | 500 charts × 4 engines | output hash equal on re-run | F13 alignment |

### 8.5 Post-deploy check

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_remote_golden_check_success` | mock endpoint returns 99.5% | script exits 0 | happy path |
| `test_remote_golden_check_triggers_rollback` | mock endpoint returns 95% | script exits non-zero | triggers rollback |
| `test_remote_golden_check_network_error` | endpoint returns 500 | script retries 3x then fails | resilience |

### 8.6 CLI scaffold

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_golden_add_chart_creates_yaml` | `--name "Test"` | file created with valid schema | scaffold works |
| `test_golden_add_chart_rejects_duplicate` | existing chart id | error | prevents collision |

### 8.7 Weekly report

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_weekly_report_computes_pass_rate_trend` | 7 days history | trend matches | report math |
| `test_weekly_report_flags_flaky` | test fails 2x in 20 | appears in flaky list | flakiness detection |
| `test_weekly_report_html_renders` | sample data | valid HTML | email deliverability |

## 9. EPIC-Level Acceptance Criteria

- [ ] 100 curated golden charts in `tests/golden/charts/`
- [ ] Every chart YAML has expected outputs for Yogini, Ashtottari, Ashtakavarga (full shodhana), 60 MVP yogas, Sade Sati, and major transits
- [ ] Comparator registry handles temporal, numeric, boolean, range with documented defaults
- [ ] `GoldenSuiteRunner` runs locally in < 3 minutes and produces a JSON report
- [ ] GitHub Actions `correctness` workflow runs on every PR and nightly
- [ ] PR cannot merge if golden suite pass rate < 99%
- [ ] Property tests run at 500 examples per PR and 10,000 nightly
- [ ] All 6 new invariants implemented and green on current engines
- [ ] Post-deploy Cloud Build step rolls back on < 99% remote golden check
- [ ] `scripts/golden_add_chart.py` CLI scaffold works; classical-advisor doc published
- [ ] Weekly correctness report emails sent every Monday to eng-weekly@josiam.com
- [ ] Weekly report flags flaky tests (≥ 2 failures in trailing 20 runs)
- [ ] Unit test coverage ≥ 90% for new harness modules (comparators, runner, scripts)
- [ ] CLAUDE.md updated: "golden suite is a merge gate; run locally via `poetry run pytest tests/golden`"
- [ ] `docs/markdown/correctness/v1.md` published

## 10. Rollout Plan

- **Feature flag:** none — harness is pure test infrastructure; always-on once landed
- **Shadow compute:** N/A
- **Backfill:** N/A (no production data)
- **Rollback plan:** If CI gate is too noisy in first week, temporarily lower threshold via `scripts/enforce_pass_rate.py 0.97` on a branch; fix underlying issues; restore 0.99 within 7 days. Post-deploy auto-rollback can be disabled via Cloud Build variable `DISABLE_GOLDEN_ROLLBACK=1` for emergency operation.

Rollout sequence:

1. Week 1: land harness + all 20 existing F16 charts wired to CI at 95% threshold (informational only)
2. Week 2: add 40 more charts; threshold to 99% but non-blocking (warning)
3. Week 3: add remaining 40 charts; enable blocking PR gate
4. Week 4: enable post-deploy rollback; start weekly reports

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Classical commentary values disagree with engine (book wrong vs engine wrong) | High | Medium | Dual review; `commentary_disagreement=true` flag; prefer engine when ephemeris-justified and document |
| Golden suite becomes slow as it grows | Medium | Medium | Precompute ephemeris per chart once per CI run and cache; split by tag for selective runs |
| Over-tight tolerances cause false failures on minor ephemeris updates | Medium | Medium | Default tolerances generous; per-field override; reviewed in PR |
| Property tests discover real bugs during PR surge | Medium | Low | File issue with seed; don't block PR if pre-existing; fix within 7 days |
| Nightly property-test flaky (Hypothesis discovery drift) | Medium | Low | Seeded Hypothesis runs; shrink-minimize in report; maintain `hypothesis-settings.yaml` |
| Auto-rollback misfires (golden-check false negative) | Low | High | Threshold 99% chosen conservative; manual override via env var; 3× retry on network error |
| Classical advisor onboarding slow | High | Medium | CLI scaffold + doc; partner with Raman/similar publications for initial batch |
| Expected outputs outdated after engine bugfix | Medium | Medium | When an engine bugfix changes expected outputs, PR must update YAMLs with explicit justification in commit message; reviewer checks |
| Birth data recorded imprecisely for historical figures | Medium | Medium | Include `birth_time_precision_minutes` field; loosen tolerances for ≥ 15 min precision charts |
| CI runner infrastructure failure | Low | Medium | Retry once; alert in #eng-alerts |
| Nightly job silently failing | Medium | Medium | Heartbeat check: if nightly job hasn't run in 48h, PagerDuty alert |

## 12. References

- Master spec: [`docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`](../../../superpowers/specs/2026-04-19-classical-techniques-expansion-design.md) §6.4 (golden chart suite ownership), §8.1 (engine correctness)
- F16 Golden chart suite scaffolding: `../P0/F16-golden-chart-suite.md`
- F17 Property-based test harness: `../P0/F17-property-based-test-harness.md`
- F13 Content-hash provenance: [`../P0/F13-content-hash-provenance.md`](../P0/F13-content-hash-provenance.md)
- E1a Multi-Dasa v1: `./E1a-multi-dasa-v1.md`
- E2a Ashtakavarga v2: `./E2a-ashtakavarga-v2.md`
- E4a Yoga Engine MVP: `./E4a-yoga-engine-mvp.md`
- E6a Transit Intelligence v1: `./E6a-transit-intelligence-v1.md`
- C5 Differential testing vs reference (future): `../P3/C5-differential-testing-vs-reference.md`
- Classical references: B.V. Raman, *Notable Horoscopes* (Motilal Banarsidass); *Three Hundred Important Combinations*; K.N. Rao, *Predicting through Jaimini*
- Hypothesis (property testing): https://hypothesis.readthedocs.io
- GitHub Actions workflow commands: `::error file=...` annotations
