---
prd_id: F16
epic_id: F16
title: "Golden chart suite scaffolding"
phase: P0-foundation
tags: [#correctness]
priority: must
depends_on: [F8]
enables: [E1a, E1b, E2a, E3, E4a, E4b, E5, E6a, E7, E8, E9, E10, E15a, C5]
classical_sources: [bphs, saravali, phaladeepika, jataka_parijata, jaimini_sutras, tajaka_neelakanthi]
estimated_effort: 5 days
status: draft
author: Govind
last_updated: 2026-04-19
---

# F16 — Golden Chart Suite Scaffolding

## 1. Purpose & Rationale

Classical astrology correctness is hard to assert in the abstract. "This chart has Gaja Kesari Yoga" is only meaningful against a named authority who agrees. Unit tests for individual rules verify DSL correctness; **golden charts verify end-to-end classical correctness against curated, source-documented expected outcomes.**

This PRD delivers:
- A **YAML schema** for golden chart cases: birth data + expected outputs + provenance.
- A **test runner** that loads every YAML, runs every relevant engine, and asserts expected matches computed.
- **CI integration** that blocks merge on golden-suite failure.
- A **tolerance framework** for the kinds of tests where exact equality doesn't make sense (±0.1 strength, ±1 day period boundaries).
- **20 curated initial charts** (5 Indian historical, 5 Indian celebrities, 5 Western historical, 5 synthetic edge cases) to prove the framework.
- A **curation workflow** so the suite grows with each EPIC.

Without this, E4a (yoga engine) cannot meaningfully assert "Gaja Kesari is correctly activated" — only that the DSL evaluates the rule as written. Golden charts close the loop by saying: *according to the authors of BPHS, this chart has Gaja Kesari, and our engine agrees*.

## 2. Scope

### 2.1 In scope
- `tests/golden/charts/*.yaml` directory + schema.
- `GoldenChartCase` Pydantic model validating each YAML on load.
- `tests/test_golden.py` pytest entrypoint that parametrizes over all golden charts × every relevant engine.
- Tolerance framework: `exact | float ± X | temporal ± X days`.
- Expected-output declaration format per technique family (yogas, dasas, ashtakavarga, jaimini, tajaka).
- Initial 20 charts with documented provenance.
- CI integration: golden suite runs on every PR as a blocking check.
- Curation process doc (`tests/golden/CONTRIBUTING.md`): how to add a chart, what reviews are required.
- Growth hooks: each downstream EPIC's acceptance criteria reference the golden suite.

### 2.2 Out of scope
- Automated chart harvesting from external databases (Astrodienst, AstroDatabank). All initial charts are manually curated.
- Full 500-chart set — this PRD scaffolds for ~20; growth to ~500 happens incrementally across P1 and P2 EPICs.
- Differential testing against Jagannatha Hora / Maitreya9 — that's C5 in P3.
- UI for browsing golden cases — CLI + file read is enough for P0.
- Kid-gloves for charts where classical interpretations disagree — in those cases we record EACH source's expected separately, not a consensus.

### 2.3 Dependencies
- F8: `TechniqueResult` and `AggregationStrategy` protocols exist so the test runner knows how to invoke engines.
- F2: fact tables exist; test runner needs to insert rules + charts + read results.
- Existing chart creation path (`ChartService.create_chart`).

## 3. Classical / Technical Research

### 3.1 Design principle: per-source expected outputs

A golden chart's expected outputs are declared **per source** — never as a single "correct answer" that pretends all sources agree. Example:

```yaml
expected:
  yogas:
    bphs:
      - rule_id: yoga.raja.gaja_kesari
        active: true
        strength: { min: 0.7 }
    saravali:
      - rule_id: yoga.raja.gaja_kesari
        active: true
        strength: { min: 0.6 }   # Saravali's definition slightly differs
    phaladeepika:
      - rule_id: yoga.raja.gaja_kesari
        active: false            # Phaladeepika has stricter criteria
        strength: 0.0
```

This reflects the master spec's source-authority pluralism and prevents the golden suite from fossilizing one source's opinion as truth.

### 3.2 YAML case schema (full, annotated)

```yaml
# tests/golden/charts/golden.c001-ramana.yaml
chart_id: golden.c001
name: "Sri Ramana Maharshi"
description: "Indian spiritual teacher, 1879–1950"

birth:
  date: "1879-12-30"
  time: "01:00:00"
  tz: "Asia/Kolkata"
  place: "Tiruchuli, Tamil Nadu, India"
  lat: 9.6833
  lon: 78.3833
  time_certainty: rectified        # one of: precise | rectified | approximate

ayanamsa: lahiri                    # matches source_authority.source_id style

provenance:
  sources:
    - "Ramana Maharshi: His Life, A.R. Natarajan, chart rectification in appendix A"
    - "Sri Ramanasramam, official records"
  reviewed_by:
    - engineer: "Govind"
      date: "2026-04-19"
    # classical_advisor slot left open for P2+

expected:
  yogas:
    bphs:
      - rule_id: yoga.raja.gaja_kesari
        active: true
        strength: { min: 0.7 }
      - rule_id: yoga.pancha_mahapurusha.hamsa
        active: true
        strength: { min: 0.7 }
      - rule_id: yoga.spiritual.parivrajaka
        active: true
    saravali:
      - rule_id: yoga.raja.gaja_kesari
        active: true

  dasas:
    vimshottari:
      birth_mahadasha:
        lord: "venus"
        start: { date: "1879-11-14", tolerance_days: 1 }
        end:   { date: "1899-11-13", tolerance_days: 1 }

  ashtakavarga:
    bphs:
      sarvashtaka_total: { value: 337, tolerance: 0 }   # exact — property-invariant

  jaimini:
    jaimini_sutras:
      chara_karakas:
        AK: "venus"      # Atmakaraka
        AmK: "jupiter"   # Amatyakaraka
        # ... 8 total

  tajaka:
    tajaka_neelakanthi:
      year_2025:
        muntha_sign: "pisces"
        year_lord: "jupiter"

# Per-technique-family overrides allow marking a family as NOT YET TESTED for
# this chart (used heavily in initial scaffolding):
not_tested:
  - varga_extended
  - western_harmonic
```

### 3.3 Tolerance semantics

Three tolerance families:

1. **Boolean exact** — `active: true` or `active: false`. No tolerance.
2. **Float with bound** — `{ value: 0.75, tolerance: 0.1 }` OR `{ min: 0.7 }` OR `{ max: 0.3 }` OR `{ range: [0.7, 0.9] }`. Used for strengths (classical interpretation has natural variance).
3. **Temporal with day-window** — `{ date: "1899-11-13", tolerance_days: 1 }`. Used for dasa period boundaries (birth-time precision of ~1 minute causes period boundaries to drift by up to ~1 day over a human lifetime).

Exact / strict comparisons (`tolerance: 0` or no tolerance key) must match exactly.

### 3.4 Initial 20 charts — composition

| # | Chart | Category | Why selected |
|---|---|---|---|
| 1 | Ramana Maharshi | Indian historical | Rectified chart, high-confidence Gaja Kesari + Hamsa |
| 2 | Paramahansa Yogananda | Indian historical | Documented by Sri Yukteswar, rich yoga pattern |
| 3 | Bal Gangadhar Tilak | Indian historical | Astronomer himself; chart well-documented |
| 4 | Mahatma Gandhi | Indian historical | Widely published in astrology literature |
| 5 | Sri Aurobindo | Indian historical | Documented in his own writings |
| 6 | A.R. Rahman | Indian celebrity | Published birth data; strong dasa fit |
| 7 | Sachin Tendulkar | Indian celebrity | Published birth data; classical yoga showcase |
| 8 | Aishwarya Rai | Indian celebrity | Published birth data; classical manglik-related example |
| 9 | Rajinikanth | Indian celebrity | Tamil-speaking community relevance |
| 10 | Mukesh Ambani | Indian celebrity | Classical wealth yoga showcase |
| 11 | Albert Einstein | Western historical | Universal reference in Western astrology |
| 12 | Carl Jung | Western historical | Astrology-engaged himself; chart well-studied |
| 13 | Marilyn Monroe | Western historical | Exhaustively analyzed in Western sources |
| 14 | Princess Diana | Western historical | Well-rectified modern chart |
| 15 | John F. Kennedy | Western historical | Well-documented, classical Western reference |
| 16 | `golden.edge.cusp` | Synthetic edge case | Planet exactly on house cusp (tests cusp inclusion logic) |
| 17 | `golden.edge.antimeridian` | Synthetic | Birth near 180° E/W (coord boundary) |
| 18 | `golden.edge.polar_winter` | Synthetic | Birth at high lat in December (sun-below-horizon edge) |
| 19 | `golden.edge.leap_second` | Synthetic | Birth time during a leap second addition (IERS edge) |
| 20 | `golden.edge.retrograde_station` | Synthetic | Birth within 1 second of a planet station (direct ↔ retrograde) |

Synthetic cases have no `expected` sections for classical yogas (they're not real people) but verify the engine doesn't crash and produces plausible numeric outputs. They serve the *property* side of testing: structure, not specific authority.

### 3.5 Test runner architecture

```
pytest tests/test_golden.py

  ├─ discovers *.yaml files in tests/golden/charts/
  ├─ for each case → generates N parametrized tests, one per (family, source) pair
  │   where `expected[family][source]` exists
  ├─ setUp: creates a temporary chart in test DB with case birth data
  ├─ invokes engine registered for family (from F8's ClassicalEngine registry)
  ├─ compares actual vs expected via appropriate tolerance function
  └─ tearDown: rollback transaction
```

Parametrization pattern means pytest output looks like:

```
tests/test_golden.py::test_case[golden.c001-yogas-bphs-gaja_kesari] PASSED
tests/test_golden.py::test_case[golden.c001-dasas-vimshottari-birth_mahadasha] PASSED
tests/test_golden.py::test_case[golden.c002-yogas-bphs-hamsa] FAILED
```

Individual test failures are precisely scoped; engineers see which chart × which rule × which source drifted.

### 3.6 Growth mechanics

Each downstream EPIC's acceptance criteria include: "Add golden-chart expected outputs for this technique family to at least 10 existing golden charts." This keeps the suite growing in lockstep with engine coverage.

Charts are also added for:
- Any chart that produces a visible bug report (regression protection).
- Any chart where two engines disagree and we've picked a winner (lock the answer).

Target trajectory:
- P0 end: 20 charts.
- P1 end: 50 charts (each P1 EPIC adds ~10).
- P2 end: 200 charts.
- P3 end: 500 charts.

### 3.7 Alternatives considered

| Alternative | Rejected because |
|---|---|
| Store expected outputs in DB, not YAML | YAML is grep-able, PR-reviewable, version-controlled with engine code |
| Generate expected outputs by "running the engine and snapshotting" | Tautological; asserts nothing about classical correctness |
| Use an existing chart database like AstroDatabank | Licensing; data quality varies; cross-source expected outputs not present |
| One YAML per (chart, technique) | Thousands of files; fragments provenance |
| Single giant YAML file | Merge conflicts; poor PR reviewability |
| Generate expected from reference software (JH/Maitreya) and call that "truth" | That's C5 in P3 — different purpose; these goldens are classically-documented, not software-documented |

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| Per-chart file or one giant file | Per-chart file | PR reviewability; localized diffs |
| YAML vs JSON | YAML | Comments; multi-line strings for provenance; community norm |
| Initial chart count | 20 | Proves framework without blocking P0 timeline |
| Include classical advisor in review at P0 | No, engineer-only | Advisor role comes online in P2 |
| Tolerance default | Strict (exact match) unless specified | Catch drift; classical interpretations are usually crisp |
| Failure mode on unknown rule_id in expected | Test fails with clear error | Guardrail against typos |
| Expected format for rule IDs | Use F6 rule_id exactly | Consistency with production |
| Who can add charts | Anyone via PR; requires engineer review | Growth without bottleneck |
| Frequency of suite run in CI | Every PR | Blocking check |

## 5. Component Design

### 5.1 New modules and files

```
tests/golden/
├── CONTRIBUTING.md                     # how to add a chart
├── schema.py                           # Pydantic GoldenChartCase model
├── tolerance.py                        # tolerance comparison helpers
├── loader.py                           # YAML → GoldenChartCase
├── runner.py                           # orchestration: chart → engines → compare
└── charts/
    ├── golden.c001-ramana.yaml
    ├── golden.c002-yogananda.yaml
    ├── … (18 more)

tests/
└── test_golden.py                      # pytest entrypoint (parametrized)

.github/workflows/   (or equivalent Cloud Build trigger)
└── golden-suite.yml                    # blocking CI check
```

### 5.2 Data model

No production-DB changes. Golden suite uses test DB (ephemeral per test run).

### 5.3 Pydantic schema (GoldenChartCase)

```python
# tests/golden/schema.py

from datetime import date, time
from typing import Literal
from pydantic import BaseModel, Field, field_validator


class BirthData(BaseModel):
    date: date
    time: time
    tz: str
    place: str
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)
    time_certainty: Literal["precise", "rectified", "approximate"] = "precise"


class FloatTolerance(BaseModel):
    """One of: {value,tolerance}, {min}, {max}, {range}."""
    value: float | None = None
    tolerance: float | None = None
    min: float | None = None
    max: float | None = None
    range: tuple[float, float] | None = None


class TemporalExpected(BaseModel):
    date: date
    tolerance_days: int = 0


class YogaExpectation(BaseModel):
    rule_id: str
    active: bool
    strength: FloatTolerance | None = None


class DasaPeriodExpected(BaseModel):
    lord: str
    start: TemporalExpected
    end: TemporalExpected


class DasaSystemExpected(BaseModel):
    birth_mahadasha: DasaPeriodExpected | None = None
    # extend as needed


class AshtakavargaExpected(BaseModel):
    sarvashtaka_total: FloatTolerance | None = None
    # per-sign matrix optional; kept minimal at P0


class JaiminiExpected(BaseModel):
    chara_karakas: dict[str, str] | None = None  # {"AK":"venus", ...}


class TajakaYearExpected(BaseModel):
    muntha_sign: str | None = None
    year_lord: str | None = None


class ExpectedOutputs(BaseModel):
    """Keyed by technique_family, then by source_id."""
    yogas: dict[str, list[YogaExpectation]] = Field(default_factory=dict)
    dasas: dict[str, DasaSystemExpected] = Field(default_factory=dict)
    ashtakavarga: dict[str, AshtakavargaExpected] = Field(default_factory=dict)
    jaimini: dict[str, JaiminiExpected] = Field(default_factory=dict)
    tajaka: dict[str, dict[str, TajakaYearExpected]] = Field(default_factory=dict)
    # Extensible: new families added as siblings.


class Provenance(BaseModel):
    sources: list[str]
    reviewed_by: list[dict[str, str]]  # free-form per-reviewer record


class GoldenChartCase(BaseModel):
    chart_id: str
    name: str
    description: str | None = None
    birth: BirthData
    ayanamsa: str
    provenance: Provenance
    expected: ExpectedOutputs = Field(default_factory=ExpectedOutputs)
    not_tested: list[str] = Field(default_factory=list)

    @field_validator("chart_id")
    @classmethod
    def _id_shape(cls, v: str) -> str:
        if not v.startswith("golden."):
            raise ValueError("chart_id must start with 'golden.'")
        return v
```

### 5.4 Tolerance helpers

```python
# tests/golden/tolerance.py

def compare_bool(actual: bool, expected: bool) -> bool:
    return actual == expected


def compare_float(actual: float, expected: FloatTolerance) -> bool:
    if expected.value is not None and expected.tolerance is not None:
        return abs(actual - expected.value) <= expected.tolerance
    if expected.min is not None and actual >= expected.min:
        if expected.max is None or actual <= expected.max:
            return True
    if expected.max is not None and actual <= expected.max and expected.min is None:
        return True
    if expected.range is not None:
        return expected.range[0] <= actual <= expected.range[1]
    if expected.value is not None:
        return actual == expected.value
    raise ValueError("FloatTolerance has no constraint fields set")


def compare_temporal(actual: date, expected: TemporalExpected) -> bool:
    return abs((actual - expected.date).days) <= expected.tolerance_days
```

### 5.5 Test runner

```python
# tests/test_golden.py

import pytest
from pathlib import Path
from tests.golden.loader import load_all_cases
from tests.golden.runner import run_case_assertion

CASES = load_all_cases(Path("tests/golden/charts"))

# Flattened parameter list: (case, family, source, item_key)
def _flatten():
    params = []
    for case in CASES:
        for family, per_source in case.expected.model_dump().items():
            for source, items in per_source.items():
                # items may be dict or list; normalize to iterable of keys
                if isinstance(items, list):
                    for i, _ in enumerate(items):
                        params.append((case, family, source, i))
                else:
                    params.append((case, family, source, None))
    return params


@pytest.mark.parametrize("case,family,source,item_key", _flatten(),
                         ids=lambda p: f"{p[0].chart_id}-{p[1]}-{p[2]}-{p[3]}")
@pytest.mark.golden
def test_case(case, family, source, item_key, db_session, engine_registry):
    """
    Run one assertion:
    - Create chart in test DB from case.birth, case.ayanamsa.
    - Invoke engine for `family` using source `source`.
    - Fetch expected item at item_key.
    - Compare via appropriate tolerance.
    """
    run_case_assertion(case, family, source, item_key, db_session, engine_registry)
```

### 5.6 CI integration

Golden suite is a pytest marker `@pytest.mark.golden`. Runs as a dedicated CI job named `golden-chart-suite` that must pass for PR merge. Tuned for speed: uses a shared test DB, parallelized via `pytest-xdist` across cases.

Expected runtime at 20 cases × ~10 assertions/case = ~200 tests, should complete in < 60 seconds once all engines exist. At 500 cases in P3, target < 5 minutes.

## 6. User Stories

### US-F16.1: As an engineer, when I open a PR that breaks yoga activation on a historical chart, CI blocks merge
**Acceptance:** Modifying `yoga.raja.gaja_kesari` DSL such that Ramana's chart no longer activates → `test_case[golden.c001-yogas-bphs-0]` fails → CI red → merge blocked.

### US-F16.2: As a classical advisor, I want to contribute a new golden chart via PR without touching Python code
**Acceptance:** Creating a new YAML at `tests/golden/charts/golden.c021-newperson.yaml` + opening PR triggers CI, and if YAML is valid and expected outputs match engine output, CI passes. No Python edits required.

### US-F16.3: As an engineer, I want the golden suite to grow automatically as each EPIC ships
**Acceptance:** E4a's PR includes YAML edits that add `expected.yogas.bphs` fields to ≥10 existing golden charts. Golden suite has concrete E4a-specific assertions.

### US-F16.4: As a debug engineer, when a golden assertion fails, I want the output to tell me exactly what diverged
**Acceptance:** Test failure output includes: chart_id, family, source, rule_id, expected value, actual value, tolerance applied. No cryptic pytest assertions.

### US-F16.5: As a product owner, I want to see source-disagreement documented in golden cases
**Acceptance:** Chart `golden.c001` has different `expected.yogas.bphs` vs `expected.yogas.phaladeepika` for Gaja Kesari; both are tested separately; neither is privileged.

## 7. Tasks

### T-F16.1: GoldenChartCase Pydantic schema
- **Definition:** Per §5.3. Covers yogas, dasas, ashtakavarga, jaimini, tajaka expected shapes. Extensible.
- **Acceptance:** Schema validates all 20 initial YAMLs; invalid YAML (typo in tolerance) raises `ValidationError` with clear field path.
- **Effort:** 4 hours
- **Depends on:** nothing

### T-F16.2: YAML loader
- **Definition:** `loader.load_all_cases(dir)` reads all `*.yaml` under `tests/golden/charts/`, parses into `GoldenChartCase` list, validates uniqueness of `chart_id`.
- **Acceptance:** Returns 20 cases for the initial set; raises on duplicate `chart_id`.
- **Effort:** 2 hours
- **Depends on:** T-F16.1

### T-F16.3: Tolerance helpers
- **Definition:** Per §5.4. Full coverage of tolerance shapes.
- **Acceptance:** Unit tests for each comparator; covers `min/max/range/value±tolerance/temporal±days`.
- **Effort:** 3 hours
- **Depends on:** T-F16.1

### T-F16.4: Runner
- **Definition:** `runner.run_case_assertion(case, family, source, item_key, db, engines)`. Creates temp chart, invokes engine, fetches `technique_compute` rows filtered by source, compares via tolerance, raises with detailed diff.
- **Acceptance:** Mock engine returning known values produces PASS; returning wrong values produces helpful diff.
- **Effort:** 6 hours
- **Depends on:** T-F16.3, F8 engine protocol

### T-F16.5: pytest entrypoint
- **Definition:** `tests/test_golden.py` with parametrized `test_case`. Uses `@pytest.mark.golden`.
- **Acceptance:** `pytest -m golden` runs only golden tests; `-k "golden.c001"` filters to one chart; failure IDs are readable.
- **Effort:** 2 hours
- **Depends on:** T-F16.4

### T-F16.6: Author initial 20 YAML files
- **Definition:** Fill in YAMLs for all 20 charts per §3.4. For synthetic edge cases, no classical `expected` — just provenance + birth.
- **Acceptance:** All 20 YAMLs validate; `not_tested` lists are populated for technique families without P0 engine coverage; provenance populated for all.
- **Effort:** 2 days
- **Depends on:** T-F16.1

### T-F16.7: CI integration
- **Definition:** Add `golden-chart-suite` job to CI that runs `pytest -m golden` with xdist parallelism; blocks PR merge on failure.
- **Acceptance:** PR with deliberate YAML expected-value break fails the check; green PR passes.
- **Effort:** 3 hours
- **Depends on:** T-F16.5

### T-F16.8: CONTRIBUTING.md for golden suite
- **Definition:** Write `tests/golden/CONTRIBUTING.md` per §3.6. Include: file naming convention, required fields, review expectations, tolerance guidance, and growth-per-EPIC policy.
- **Acceptance:** Doc reviewed; used in every downstream EPIC's acceptance criteria.
- **Effort:** 3 hours
- **Depends on:** T-F16.1

### T-F16.9: Assertion-diff enhancer
- **Definition:** Custom pytest formatter that, on golden assertion failure, renders a structured diff: expected block, actual block, tolerance, field path.
- **Acceptance:** Demo failure produces a diff that a new engineer can act on without reading the test source.
- **Effort:** 3 hours
- **Depends on:** T-F16.4

### T-F16.10: Documentation
- **Definition:** Update `CLAUDE.md` with "golden suite is blocking; see tests/golden/CONTRIBUTING.md to add charts."
- **Acceptance:** Doc committed.
- **Effort:** 1 hour
- **Depends on:** T-F16.8

## 8. Unit Tests

### 8.1 GoldenChartCase schema

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_valid_case_parses` | all 20 initial YAMLs | all validate | real-world coverage |
| `test_bad_chart_id_prefix_rejected` | chart_id="c001" (missing `golden.` prefix) | ValidationError | convention |
| `test_duplicate_chart_id_detected` | two cases with same id | loader raises | uniqueness |
| `test_unknown_tolerance_shape_rejected` | `strength: {foo: bar}` | ValidationError | typo guard |
| `test_nonexistent_source_in_expected_flagged` | `expected.yogas.not_a_source: [...]` | warning at load time | source_authority parity |

### 8.2 Tolerance helpers

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_compare_bool_exact` | (true, true) | True | basic |
| `test_compare_float_value_tolerance_hit` | actual=0.72, expected={value:0.75, tolerance:0.1} | True | within band |
| `test_compare_float_value_tolerance_miss` | actual=0.50, expected={value:0.75, tolerance:0.1} | False | outside band |
| `test_compare_float_min_pass` | actual=0.8, expected={min:0.7} | True | lower-bound |
| `test_compare_float_range_pass` | actual=0.8, expected={range:[0.7,0.9]} | True | range |
| `test_compare_float_range_fail_high` | actual=0.95, expected={range:[0.7,0.9]} | False | upper bound |
| `test_compare_temporal_within_window` | actual=2026-04-20, expected={date:2026-04-19, tolerance_days:1} | True | day window |
| `test_compare_temporal_exactly_at_window_edge` | diff = tolerance_days | True | inclusive |
| `test_compare_temporal_outside_window` | diff = tolerance_days + 1 | False | strict |
| `test_compare_float_no_constraints_raises` | expected={} | ValueError | schema guard |

### 8.3 Loader

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_load_all_cases_count` | 20 YAML files | 20 cases returned | completeness |
| `test_load_skips_non_yaml` | directory with *.md noise | only .yaml parsed | robustness |
| `test_load_reports_parse_errors_with_filename` | one malformed YAML | exception message contains filename | debuggability |

### 8.4 Runner

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_runner_invokes_engine_with_right_source` | case expects bphs yoga | engine called with source_id='bphs' | source isolation |
| `test_runner_reads_technique_compute_rows_filtered_by_source` | two sources computed | assertion compares only bphs | filter correctness |
| `test_runner_reports_missing_rule_id` | expected rule_id not in DB | clear error: "rule X not loaded" | ops clarity |
| `test_runner_diff_format` | mismatch between actual/expected | diff includes all 5 fields: chart_id, family, source, rule_id, actual vs expected | debuggability |
| `test_runner_tolerates_float_within_bound` | actual=0.73, expected={value:0.75, tolerance:0.1} | PASS | tolerance integration |
| `test_runner_strict_on_boolean` | actual=false, expected=true | FAIL | strictness |

### 8.5 Pytest entrypoint

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_suite_discovers_all_cases` | run `pytest -m golden --collect-only` | 20 cases × avg-3 assertions = ~60 test IDs | discovery works |
| `test_suite_id_format` | any test | ID matches `{chart_id}-{family}-{source}-{item_key}` | readability |
| `test_suite_runs_in_under_60s_at_20_charts` | `pytest -m golden -n auto` | < 60s wall time | perf sanity |

### 8.6 CI integration (meta)

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_ci_config_has_golden_job` | CI YAML | job named `golden-chart-suite` present | infra invariant |
| `test_ci_blocks_merge_on_golden_fail` | deliberate break | PR shows blocking red check | governance |

## 9. EPIC-Level Acceptance Criteria

- [ ] `tests/golden/charts/` contains 20 YAML files, all validate against `GoldenChartCase`
- [ ] 15 are historical (10 Indian, 5 Western), 5 are synthetic edge cases
- [ ] All 20 have complete `provenance` blocks
- [ ] Tolerance framework implemented with unit tests covering every tolerance shape
- [ ] Runner correctly invokes engines and compares outputs; clear diff on failure
- [ ] `pytest -m golden` runs the full suite in < 60s at 20 cases
- [ ] CI job `golden-chart-suite` exists and blocks PR merge on failure
- [ ] `tests/golden/CONTRIBUTING.md` documents growth workflow
- [ ] `CLAUDE.md` updated
- [ ] Every downstream EPIC PRD (E4a, E1a, etc.) includes "add golden-chart expected outputs" in its acceptance criteria
- [ ] Unit test coverage ≥ 90% on `tests/golden/{schema,tolerance,loader,runner}.py`

## 10. Rollout Plan

- **Feature flag:** none — test-suite infrastructure.
- **Shadow compute:** N/A.
- **Backfill:** N/A.
- **Rollback plan:** Delete `tests/golden/` and the CI job. Zero production impact.

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Initial expected values are wrong due to engineer-only review | High | Medium | Acknowledged limitation at P0; P2 adds classical advisor review; mark `reviewed_by` to track who signed off |
| Flaky tests due to floating-point drift in engines | Medium | High | Tolerance framework exists; require PR reviewer to justify any `tolerance: 0` on floats |
| Suite runtime grows unbounded | Medium | Medium | Parallelization (`pytest-xdist`); if > 5 min at 500 charts, split into blocking (core) + non-blocking (nightly) |
| YAMLs diverge from actual rule_ids in F6 | Medium | Medium | Runner validates rule_id exists in DB at test time; clear error |
| Engineers skip adding golden expected in downstream EPICs | Medium | High | EPIC acceptance criteria enforce; PR template includes checkbox; periodic audit |
| Legal concern using real people's birth data | Low | Medium | Use only publicly-published birth data; document source in `provenance.sources` |
| Classical sources disagree and we force one "expected" | Medium | High | Schema design allows per-source expected outputs; never force consensus |
| Edge-case YAMLs (synthetic) asserting plausibility drift over time | Low | Low | Synthetic cases document their invariant in `description`; reviewer checks |
| Re-running suite on minor rule tweaks produces large diffs | Medium | Medium | Diff format is structured; reviewers can triage fast |

## 12. References

- Master spec: [`docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`](../../../superpowers/specs/2026-04-19-classical-techniques-expansion-design.md) §6.4
- F8 engine protocol: [`F8-technique-result-aggregation-protocol.md`](./F8-technique-result-aggregation-protocol.md)
- F17 property-based tests: [`F17-property-based-test-harness.md`](./F17-property-based-test-harness.md) (complementary test strategy)
- Classical sources: BPHS, Saravali, Phaladeepika, Jaimini Sutras, Tajaka Neelakanthi
- Chart provenance references: Ramana biography (A.R. Natarajan); Paramahansa Yogananda "Autobiography of a Yogi"; Sri Aurobindo Ashram records; public celebrity chart databases (Astrodienst)
- pytest-xdist for parallel runs
