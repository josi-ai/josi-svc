---
prd_id: F17
epic_id: F17
title: "Property-based test harness (Hypothesis)"
phase: P0-foundation
tags: [#correctness]
priority: must
depends_on: [F8]
enables: [E1a, E1b, E2a, E3, E4a, E4b, E5, E6a, E7, E15a, C5]
classical_sources: []
estimated_effort: 4 days
status: draft
author: Govind
last_updated: 2026-04-19
---

# F17 — Property-Based Test Harness (Hypothesis)

## 1. Purpose & Rationale

Golden chart tests (F16) verify known classical facts against ~20–500 curated cases. That's example-based testing: it says "given these inputs, this result is correct." But classical astrology has **invariants** — mathematical and classical identities that should hold for *every* valid chart, not just the curated ones:

- Ashtakavarga: every planet contributes 0–8 bindus per sign, so `sum(bindus_for_planet_across_12_signs) ≤ 56 always`.
- Sarvashtakavarga: `sarva_total ≤ 337` (sum over 7 planets + ascendant each capped at their max).
- Vimshottari: `sum(all_mahadasha_lengths) == exactly 120 years`.
- Antardasha levels: `sum(antardasha_periods_under_a_mahadasha) == parent_mahadasha_duration ± 1 day` (floating-point tolerance).
- Shadbala: `virupa_total == 60 × rupa_total within 0.001`.
- Any planet position: `0 ≤ longitude < 360` and `-90 ≤ declination ≤ 90` always.
- Any house assignment: `1 ≤ house_number ≤ 12` always.

Example-based tests cannot express "for every valid chart." Hypothesis's property-based approach generates thousands of randomized-but-valid charts per CI run, checks each invariant, and auto-shrinks failing cases to minimal reproducers. This catches off-by-one errors, edge cases (leap years, antimeridian, pole-adjacent latitudes), and arithmetic bugs that curated tests would miss for decades.

F17 delivers the harness: Hypothesis integration, reusable strategy builders, an invariant registration decorator, and the initial catalog of classical invariants.

## 2. Scope

### 2.1 In scope
- `hypothesis` dependency pinned in `pyproject.toml`.
- Strategy builders in `tests/property/strategies/`:
  - `valid_chart()` — generates `GoldenChartCase`-compatible random charts with realistic inputs.
  - `valid_date()`, `valid_latitude()`, `valid_longitude()`, `valid_tz()`.
- Invariant registration: `@property_test(family="ashtakavarga", name="bindus_bounded")` decorator that auto-registers tests.
- Initial invariant catalog:
  - Ashtakavarga: 4 invariants (bindus per planet, sarva total, trikona/ekadhipatya shodhana monotonicity, per-sign sum).
  - Vimshottari: 3 invariants (total 120 years, nesting, ordering).
  - Yogini: 2 invariants (total 36 years, lord ordering).
  - Shadbala: 2 invariants (virupa↔rupa conversion, non-negativity).
  - Planet positions: 3 invariants (longitude range, latitude range, declination range).
  - House positions: 2 invariants (range 1–12, all planets assigned).
- Pytest integration: invariants run under `@pytest.mark.property` marker.
- Hypothesis config: `max_examples=200` in PR CI (fast), `max_examples=5000` in nightly.
- Fixed-seed mode (`HYPOTHESIS_SEED=...`) for deterministic CI.
- Shrinking configured to produce minimal failing examples.

### 2.2 Out of scope
- Invariants that require a full engine implementation (E1a, E2a, etc.) — those PRDs add their own property tests using this harness. F17 provides the harness AND the invariants for properties already satisfiable by foundation + basic existing engines (planet positions, house assignments) plus the "invariant registry" for everything that will come later.
- Fuzzing of I/O layer (HTTP endpoints, DB queries) — Hypothesis is engine-layer only here.
- Cross-engine consistency tests (E1a dasa vs E3 jaimini dasa agreement) — that's C5 differential testing.
- UI/frontend property tests — separate concern.

### 2.3 Dependencies
- F8: Engine Protocol exists so tests can invoke engines generically.
- Existing `AstrologyCalculator` (pyswisseph-based) — used as the source of truth for planet position and house invariants, which are true regardless of classical source.

## 3. Technical Research

### 3.1 Why Hypothesis

- Mature Python library (10+ years), widely used at scale.
- **Shrinking**: when a property fails, Hypothesis automatically reduces the counterexample toward minimal form. Given a failure at lat=73.214, it will shrink toward lat=0 or lat=90 (the "boundary" candidates).
- **Strategy composition**: `valid_chart()` can be built from `valid_date() | valid_lat() | valid_lon() | ...`.
- **Deterministic reproduction**: failing cases can be replayed via `@reproduce_failure` decorator.
- **Pytest integration**: first-class via `@given(...)` decorator.

### 3.2 Strategy: `valid_chart()`

```python
@st.composite
def valid_chart(draw, *, min_year=1800, max_year=2100,
                min_lat=-66.0, max_lat=66.0,
                min_lon=-180.0, max_lon=180.0):
    """
    Generate a chart with birth data in realistic ranges.

    Defaults:
      - Year range [1800, 2100] — covers 99% of real chart requests
      - Lat range [-66, 66] — excludes polar regions where classical
        astrology is undefined (no house computation works at poles)
      - TZ: draws from the IANA database of VALID timezones at the
        chosen date (no 'America/Indiana/Indianapolis' before 2007, etc.)
    """
    date = draw(st.dates(
        min_value=datetime(min_year, 1, 1).date(),
        max_value=datetime(max_year, 12, 31).date()
    ))
    time = draw(st.times())
    lat = draw(st.floats(min_value=min_lat, max_value=max_lat,
                         allow_nan=False, allow_infinity=False, width=32))
    lon = draw(st.floats(min_value=min_lon, max_value=max_lon,
                         allow_nan=False, allow_infinity=False, width=32))
    tz_name = draw(st.sampled_from(_valid_tz_names_for_date(date)))
    ayanamsa = draw(st.sampled_from(["lahiri", "kp", "raman", "fagan_bradley"]))
    return ChartBirthInputs(
        date=date, time=time, tz=tz_name,
        lat=lat, lon=lon, ayanamsa=ayanamsa,
    )
```

Key points:
- `width=32` for floats: produces well-behaved floats that round-trip through JSON without precision drift.
- `_valid_tz_names_for_date(date)`: custom helper filtering IANA list to timezones valid at that date (some TZs don't exist before a given date; skipping this causes `zoneinfo` errors).
- Ranges chosen to avoid undefined classical regions (poles, distant future/past beyond swiss ephemeris coverage).

### 3.3 Invariant registration

```python
# tests/property/registry.py

from typing import Callable

@dataclass(frozen=True)
class PropertyInvariant:
    family: str           # technique_family_id this invariant belongs to
    name: str             # short name
    description: str      # human-readable description
    fn: Callable          # the hypothesis @given-decorated test function

_REGISTRY: list[PropertyInvariant] = []

def property_test(family: str, name: str, description: str):
    """Decorator that registers an invariant and marks it pytest-collectable."""
    def decorator(fn):
        _REGISTRY.append(PropertyInvariant(family=family, name=name,
                                          description=description, fn=fn))
        return pytest.mark.property(fn)
    return decorator

def all_invariants() -> list[PropertyInvariant]:
    return list(_REGISTRY)
```

Invariants declared via:

```python
@property_test(
    family="ashtakavarga",
    name="bindus_per_planet_bounded",
    description="Each planet's total bindus across 12 signs is ≤ 56",
)
@given(chart=valid_chart())
@settings(max_examples=200, deadline=5000)
def test_ashtakavarga_bindus_per_planet_bounded(chart, engine_registry):
    result = engine_registry["ashtakavarga"].compute(chart)
    for planet, per_sign in result.bhinnashtaka.items():
        assert 0 <= sum(per_sign) <= 56, f"planet {planet}: sum={sum(per_sign)}"
```

### 3.4 Initial invariant catalog

#### 3.4.1 Ashtakavarga family (4 invariants)

| Name | Invariant | Tolerance |
|---|---|---|
| `bindus_per_planet_bounded` | Each planet's `sum_across_signs(bindus) ≤ 56` | exact |
| `bindus_per_sign_non_negative` | Every bindu count `≥ 0` | exact |
| `sarvashtaka_total_bounded` | `sarvashtaka_total ≤ 337` | exact |
| `shodhana_reduces_bindus` | After trikona + ekadhipatya shodhana, total bindus ≤ pre-shodhana total | exact |

#### 3.4.2 Vimshottari dasa (3 invariants)

| Name | Invariant | Tolerance |
|---|---|---|
| `mahadasha_total_is_120_years` | `sum(mahadasha_durations) == 120 years` | exact (365.25 days × 120) |
| `antardasha_sum_equals_parent` | `sum(antardasha_durations_under_parent) == parent_duration` | ±1 day |
| `dasa_lord_sequence_canonical` | Mahadasha lords in order: Ketu, Venus, Sun, Moon, Mars, Rahu, Jupiter, Saturn, Mercury | exact |

#### 3.4.3 Yogini dasa (2 invariants)

| Name | Invariant | Tolerance |
|---|---|---|
| `yogini_total_is_36_years` | `sum(yogini_mahadasha_durations) == 36 years` | exact |
| `yogini_lord_sequence` | Ordering follows Mangala, Pingala, Dhanya, Bhramari, Bhadrika, Ulka, Siddhi, Sankata | exact |

#### 3.4.4 Shadbala (2 invariants)

| Name | Invariant | Tolerance |
|---|---|---|
| `virupa_rupa_conversion` | `virupa_total == 60.0 × rupa_total` | ±0.001 |
| `shadbala_non_negative` | All 6 bala components ≥ 0 | exact |

#### 3.4.5 Planet positions (3 invariants)

| Name | Invariant | Tolerance |
|---|---|---|
| `longitude_in_range` | `0 ≤ longitude < 360` for every planet | exact |
| `latitude_in_range` | `-90 ≤ latitude ≤ 90` | exact |
| `ketu_is_rahu_plus_180` | `ketu_longitude == (rahu_longitude + 180) mod 360` | ±0.0001° |

#### 3.4.6 House positions (2 invariants)

| Name | Invariant | Tolerance |
|---|---|---|
| `house_in_range` | Every planet's house ∈ {1..12} | exact |
| `all_seven_planets_assigned_to_houses` | The 7 classical planets each have a house assignment | exact |

Total at P0 scaffold: **16 invariants**.

Each downstream engine EPIC adds its own invariants using the same decorator.

### 3.5 Config: PR vs nightly

```python
# tests/property/conftest.py

import os
from hypothesis import settings, Verbosity

PR_PROFILE = settings(
    max_examples=200,
    deadline=5000,               # 5s per example
    derandomize=True,            # fixed seed in CI for reproducibility
    verbosity=Verbosity.normal,
)

NIGHTLY_PROFILE = settings(
    max_examples=5000,
    deadline=30_000,
    derandomize=False,           # random exploration
    verbosity=Verbosity.verbose,
)

if os.getenv("CI_PROFILE") == "nightly":
    settings.register_profile("default", parent=NIGHTLY_PROFILE)
else:
    settings.register_profile("default", parent=PR_PROFILE)
settings.load_profile("default")
```

### 3.6 Shrinking and reproduction

When an invariant fails, Hypothesis auto-shrinks the input toward minimal form. The failing example is printed and can be replayed:

```
Falsifying example: test_vimshottari_total_120_years(
    chart=ChartBirthInputs(date=date(2000, 3, 1), time=time(12,0,0),
                           tz='UTC', lat=0.0, lon=0.0, ayanamsa='lahiri'),
)
You can reproduce this example by temporarily adding
@reproduce_failure('6.131.0', b'AXicY2BAA...')
```

The `@reproduce_failure` snippet is added to a TEMPORARY test to replay and debug. Once fixed, the snippet is removed and the generic test continues guarding the property.

### 3.7 Alternatives considered

| Alternative | Rejected because |
|---|---|
| Only example-based golden tests (F16) | Cannot assert "for every valid chart"; misses edge cases |
| QuickCheck-style via a different library (e.g., `pytest-quickcheck`) | Less mature in Python; Hypothesis is the de facto standard |
| Random fuzzing without shrinking | Counterexamples remain complex; debug costs high |
| Run all invariants on 100M+ generated charts offline | Compute-prohibitive and low marginal value |
| Write property tests without registry | No discoverability; downstream EPICs' additions invisible |

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| Library choice | Hypothesis | de facto Python PBT standard; mature shrinking |
| max_examples in PR CI | 200 | Balances signal vs runtime; upgrades in nightly |
| max_examples in nightly | 5000 | Deep exploration; OK with longer runtime |
| Polar lat range | Exclude beyond ±66° | Classical astrology undefined at poles |
| Year range | 1800–2100 | 99%+ of real chart requests; swiss ephemeris reliable |
| Ayanamsa values to draw | {lahiri, kp, raman, fagan_bradley} | Covers all currently-supported systems |
| Non-deterministic in nightly? | Yes (derandomize=False) | Find novel failures |
| Registry global vs per-module | Global list, auto-populated by decorator import | Discoverability |
| Handle time zone changes (DST) | `_valid_tz_names_for_date` filters invalid TZ/date combos | Robustness |
| Failing case retention | `.hypothesis/` cache committed to git? | No — keep in CI artifact; gitignore the cache dir |

## 5. Component Design

### 5.1 New modules

```
tests/property/
├── __init__.py
├── conftest.py                      # Hypothesis profile config
├── registry.py                      # PropertyInvariant + decorator
├── strategies/
│   ├── __init__.py
│   ├── chart.py                     # valid_chart, ChartBirthInputs
│   ├── primitives.py                # valid_date, valid_lat, etc.
│   └── timezones.py                 # _valid_tz_names_for_date helper
├── invariants/
│   ├── __init__.py                  # imports all modules so decorators fire
│   ├── planet_positions.py
│   ├── house_positions.py
│   ├── ashtakavarga.py              # scaffold; full tests activate with E2a
│   ├── vimshottari.py               # scaffold; activate with E1a
│   ├── yogini.py                    # scaffold; activate with E1a
│   └── shadbala.py                  # scaffold; activate with E2a/E7
└── test_property_suite.py           # pytest entrypoint
```

### 5.2 Data model

No DB changes.

### 5.3 Python API

```python
# tests/property/registry.py

from dataclasses import dataclass
from typing import Callable
import pytest

@dataclass(frozen=True)
class PropertyInvariant:
    family: str
    name: str
    description: str
    fn: Callable

_REGISTRY: list[PropertyInvariant] = []

def property_test(*, family: str, name: str, description: str):
    def decorator(fn):
        _REGISTRY.append(PropertyInvariant(
            family=family, name=name, description=description, fn=fn
        ))
        return pytest.mark.property(fn)
    return decorator

def all_invariants() -> list[PropertyInvariant]:
    return list(_REGISTRY)
```

### 5.4 Example invariant (planet positions)

```python
# tests/property/invariants/planet_positions.py

from hypothesis import given, settings
from tests.property.strategies.chart import valid_chart
from tests.property.registry import property_test
from josi.services.astrology_service import AstrologyCalculator


@property_test(
    family="planet_positions",
    name="longitude_in_range",
    description="Every planet's ecliptic longitude is in [0, 360)",
)
@given(chart=valid_chart())
@settings(max_examples=200, deadline=5000)
def test_planet_longitude_in_range(chart):
    calc = AstrologyCalculator()
    positions = calc.compute_positions(
        date=chart.date, time=chart.time, tz=chart.tz,
        lat=chart.lat, lon=chart.lon, ayanamsa=chart.ayanamsa,
    )
    for planet, pos in positions.items():
        assert 0.0 <= pos.longitude < 360.0, \
            f"{planet} longitude={pos.longitude} out of range"
```

### 5.5 Pytest entrypoint

```python
# tests/property/test_property_suite.py

# Importing invariants/ package side-effect-registers all invariants.
from tests.property import invariants   # noqa: F401
from tests.property.registry import all_invariants


def test_invariant_catalog_non_empty():
    """Smoke test: registry has invariants."""
    assert len(all_invariants()) >= 16


def test_invariant_catalog_has_no_duplicates():
    seen = set()
    for inv in all_invariants():
        key = (inv.family, inv.name)
        assert key not in seen, f"duplicate invariant {key}"
        seen.add(key)

# Individual invariants are pytest-collected via their @property_test
# decorator, which also marks them with @pytest.mark.property.
# Run: pytest -m property
```

### 5.6 CI integration

- **Per-PR job** `property-tests-fast`: runs `pytest -m property` under PR_PROFILE (200 examples each). Blocking. Target runtime ~2 min at 16 invariants × 200 examples.
- **Nightly job** `property-tests-deep`: runs under NIGHTLY_PROFILE (5000 examples). Non-blocking. Runtime budget 30 min.
- Both jobs upload `.hypothesis/` cache as a CI artifact for post-mortem.

## 6. User Stories

### US-F17.1: As an engineer, I want invariants to catch math bugs before production
**Acceptance:** introducing a deliberate off-by-one in the vimshottari sum (e.g., total = 119 years) fails `test_vimshottari_total_is_120_years` in CI, with a minimal counterexample chart printed.

### US-F17.2: As a reviewer, I want the set of invariants to be discoverable at a glance
**Acceptance:** `pytest --collect-only -m property` lists all 16 invariants with their family and name in the test ID.

### US-F17.3: As an engineer, when a nightly property test fails, I want to reproduce it locally
**Acceptance:** nightly CI failure message includes a `@reproduce_failure('6.x', b'...')` snippet that, pasted locally, reproduces the exact failing chart.

### US-F17.4: As an engineer implementing E2a, I want to add ashtakavarga invariants without changing the harness
**Acceptance:** `@property_test(family="ashtakavarga", name="shodhana_monotonic", …)` in a new file under `tests/property/invariants/` is automatically picked up on next CI run.

### US-F17.5: As a release manager, I want nightly property tests to find edge cases example tests missed
**Acceptance:** at least one real bug (over the first 6 months of platform life) is caught first by nightly property tests, not by example tests or production incidents.

## 7. Tasks

### T-F17.1: Add Hypothesis dependency
- **Definition:** Add `hypothesis = "^6.131"` to `pyproject.toml` `[tool.poetry.group.dev.dependencies]`. Run `poetry lock` and `poetry install`.
- **Acceptance:** `from hypothesis import given` works in the test env.
- **Effort:** 30 minutes
- **Depends on:** nothing

### T-F17.2: Strategy builders
- **Definition:** Implement `valid_chart`, `valid_date`, `valid_lat`, `valid_lon`, `valid_tz`, `_valid_tz_names_for_date`. Cover edge cases (DST transitions, leap years).
- **Acceptance:** `valid_chart().example()` returns a structurally-valid chart; 1000 draws produce no exceptions.
- **Effort:** 5 hours
- **Depends on:** T-F17.1

### T-F17.3: Registry and decorator
- **Definition:** `tests/property/registry.py` with `PropertyInvariant`, `property_test`, `all_invariants`.
- **Acceptance:** Registering 3 test invariants in a fixture and calling `all_invariants()` returns all 3.
- **Effort:** 2 hours
- **Depends on:** T-F17.1

### T-F17.4: Conftest + profile config
- **Definition:** `tests/property/conftest.py` with PR and nightly profiles; `CI_PROFILE` env var selects.
- **Acceptance:** `CI_PROFILE=nightly pytest -m property` uses max_examples=5000; default uses 200.
- **Effort:** 2 hours
- **Depends on:** T-F17.3

### T-F17.5: Planet-position + house-position invariants
- **Definition:** Implement all 5 invariants in §3.4.5 and §3.4.6. These work against the existing `AstrologyCalculator`.
- **Acceptance:** All 5 pass at max_examples=200 in CI.
- **Effort:** 4 hours
- **Depends on:** T-F17.2, T-F17.3

### T-F17.6: Scaffolded invariants for engines yet to ship
- **Definition:** Write invariant *skeletons* for ashtakavarga, vimshottari, yogini, shadbala. Skeletons are decorated and registered but marked `@pytest.mark.skip(reason="engine not yet implemented; activated by E1a/E2a/E7")`.
- **Acceptance:** Catalog shows all 16 invariants; skipped ones correctly collected but skipped in CI output.
- **Effort:** 4 hours
- **Depends on:** T-F17.3

### T-F17.7: Pytest entrypoint + catalog smoke tests
- **Definition:** `tests/property/test_property_suite.py` per §5.5.
- **Acceptance:** `pytest -m property --collect-only` lists 16 invariants; catalog-integrity tests pass.
- **Effort:** 1 hour
- **Depends on:** T-F17.5, T-F17.6

### T-F17.8: CI integration
- **Definition:** Add `property-tests-fast` blocking job + `property-tests-deep` non-blocking nightly job; upload `.hypothesis/` cache artifacts on failure.
- **Acceptance:** PR CI runs ~2 min; nightly CI runs ≤ 30 min; deliberate invariant break fails PR job.
- **Effort:** 3 hours
- **Depends on:** T-F17.7

### T-F17.9: Documentation
- **Definition:** Author `tests/property/README.md`: what property testing is, how to add a new invariant, how to reproduce a failure, how to interpret shrink output. Update `CLAUDE.md`.
- **Acceptance:** Doc reviewed; a new engineer can add an invariant without reading source.
- **Effort:** 2 hours
- **Depends on:** T-F17.6

### T-F17.10: Bridge with F16 expected outputs (optional nicety)
- **Definition:** For any golden chart, the subset of its `expected` outputs that assert bounds (e.g., `sarvashtaka_total: {value: 337, tolerance: 0}`) should also be reconcilable as property instances. Scaffold a cross-check utility that warns if a golden chart case directly contradicts a property invariant.
- **Acceptance:** Running the cross-check prints a warning if such contradiction exists; no false positives on initial 20 charts.
- **Effort:** 3 hours
- **Depends on:** T-F17.6, F16 complete

## 8. Unit Tests

### 8.1 Strategies

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_valid_chart_produces_valid_types` | 100 draws | each draw has `ChartBirthInputs` with correct types | type safety |
| `test_valid_chart_lat_range` | 1000 draws | all lat in [-66, 66] | configured bounds |
| `test_valid_chart_lon_range` | 1000 draws | all lon in [-180, 180] | configured bounds |
| `test_valid_chart_tz_valid_at_date` | 1000 draws | each tz valid at corresponding date | DST / TZ history correctness |
| `test_valid_chart_ayanamsa_from_set` | 1000 draws | ayanamsa ∈ {lahiri, kp, raman, fagan_bradley} | constrained |
| `test_valid_chart_deterministic_with_seed` | seed=42, two calls | identical sequences | repro |

### 8.2 Registry

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_decorator_registers_invariant` | decorate 1 function | appears in `all_invariants()` | registration |
| `test_decorator_adds_pytest_mark_property` | decorated test | has `@pytest.mark.property` | CI filtering works |
| `test_duplicate_family_name_flagged` | 2 invariants with same (family, name) | catalog-integrity test fails in CI | dup guard |

### 8.3 Invariant correctness (meta-tests)

Each invariant has a *meta-test* that a deliberately-broken engine fails the invariant, and a fixed (correct) engine passes.

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `meta_longitude_in_range_catches_bad_engine` | mock engine returning `-1.0` | invariant fails | sensitivity |
| `meta_vimshottari_total_catches_119_year_bug` | mock engine with off-by-one | invariant fails | sensitivity |
| `meta_sarva_total_catches_overbound` | mock engine returning 400 | invariant fails | sensitivity |
| `meta_virupa_rupa_catches_drift` | mock engine with 0.01 drift | invariant passes (within tolerance) | tolerance correctness |
| `meta_virupa_rupa_catches_larger_drift` | mock engine with 0.1 drift | invariant fails | tolerance correctness |

### 8.4 Profile handling

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_pr_profile_uses_200_examples` | CI_PROFILE unset | `settings().max_examples == 200` | default |
| `test_nightly_profile_uses_5000_examples` | `CI_PROFILE=nightly` | `max_examples == 5000` | config |

### 8.5 CI smoke tests

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_ci_config_has_property_jobs` | CI config | `property-tests-fast` and `property-tests-deep` jobs exist | infra invariant |
| `test_ci_fast_job_is_blocking` | CI config | fast job is blocking | governance |
| `test_ci_deep_job_is_non_blocking` | CI config | deep job non-blocking | governance |

## 9. EPIC-Level Acceptance Criteria

- [ ] Hypothesis library added; `poetry install` works
- [ ] `valid_chart` strategy implemented with configurable ranges
- [ ] `@property_test` decorator registers invariants into a global catalog
- [ ] 16 invariants registered (5 active + 11 scaffolded-as-skipped for engines yet to ship)
- [ ] All 5 active invariants pass at max_examples=200 in CI
- [ ] Meta-tests verify each invariant actually detects the bug it's meant to catch
- [ ] PR CI blocking job `property-tests-fast` runs in < 3 min
- [ ] Nightly non-blocking job `property-tests-deep` configured
- [ ] `.hypothesis/` cache uploaded as CI artifact on failure
- [ ] `tests/property/README.md` documents how to add invariants
- [ ] `CLAUDE.md` updated
- [ ] Downstream EPIC PRDs (E1a, E2a, E4a, etc.) explicitly cite F17 as the mechanism for their property tests
- [ ] Unit test coverage ≥ 90% on `tests/property/{registry,strategies}.py`

## 10. Rollout Plan

- **Feature flag:** none — test-only infrastructure.
- **Shadow compute:** N/A.
- **Backfill:** N/A.
- **Rollback plan:** Delete `tests/property/` and the two CI jobs. Remove Hypothesis from `pyproject.toml`. Zero production impact.

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Flaky test failures due to edge-of-range floats | Medium | Medium | Use `width=32` for floats; explicit bounds; `allow_nan=False`; pin Hypothesis version |
| TZ strategies produce invalid (date, tz) combos | Medium | Medium | `_valid_tz_names_for_date` filters explicitly; unit-tested |
| Nightly runtime explodes as invariants grow | Medium | Low | max_examples adjustable per invariant; profile tuning; parallelism via `pytest-xdist` |
| Engineers add invariants without meta-tests → false positives or false negatives | Medium | Medium | README requires meta-test; PR reviewer enforces |
| Shrinking gets stuck on a complex chart | Low | Low | Hypothesis has its own shrinking timeout; we can set `max_shrinking_time` |
| Property tests supersede classical authority and produce "correct" outputs that contradict classical sources | Low | High | Property tests only verify mathematical/structural invariants, never semantic classical claims. That's what golden charts (F16) are for. Documented in README. |
| Hypothesis upgrade changes reproduction format | Low | Medium | Pin to ^6.131; upgrade consciously |
| `.hypothesis/` cache not gitignored | Low | Low | Add to `.gitignore` as part of T-F17.4 |
| Property tests test the engine *on* the test harness's own chart fixture, which may differ from production chart fixture | Low | Medium | Use the same `ChartService` / `AstrologyCalculator` as production |

## 12. References

- Master spec: [`docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`](../../../superpowers/specs/2026-04-19-classical-techniques-expansion-design.md)
- Hypothesis docs: https://hypothesis.readthedocs.io/
- F8 engine protocol: [`F8-technique-result-aggregation-protocol.md`](./F8-technique-result-aggregation-protocol.md)
- F16 golden chart suite: [`F16-golden-chart-suite.md`](./F16-golden-chart-suite.md) (complementary: example-based to F17's property-based)
- Downstream engines that add invariants: E1a (dasa), E2a (ashtakavarga), E4a (yogas), E7 (vargas)
- Classical invariants sourced from: BPHS Ch.45 (ashtakavarga), BPHS Ch.46 (vimshottari), Saravali (shadbala)
