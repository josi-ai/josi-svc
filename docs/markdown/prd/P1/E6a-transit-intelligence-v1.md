---
prd_id: E6a
epic_id: E6
title: "Transit Intelligence v1 (Sade Sati, Dhaiya, major transits, eclipses)"
phase: P1-mvp
tags: [#correctness, #end-user-ux]
priority: must
depends_on: [F1, F2, F4, F6, F7, F8, F13, F16, F17]
enables: [E6b, E11a, E13, E14a]
classical_sources: [bphs, phaladeepika, saravali, jataka_parijata]
estimated_effort: 3 weeks
status: approved
author: @agent-claude-opus-4-7
last_updated: 2026-04-19
---

# E6a — Transit Intelligence v1 (Sade Sati, Dhaiya, Major Transits, Eclipses)

## 1. Purpose & Rationale

Transits (*gochara*, "the moving sky") are what end users *actually* ask AI chat for: "When does my Sade Sati end?", "Is this a good year?", "What's my current Saturn phase?". Classical Vedic timing is transit-heavy in popular practice — even more than dasa — because transits produce the *emotional* experience dasa provides the *framework* for.

Josi today has `src/josi/services/transit_monitor.py` that computes raw planetary positions at arbitrary datetimes, but no classical transit *patterns*. This PRD adds the four most-cited classical transit constructs:

1. **Sade Sati** ("seven-and-a-half of Saturn") — BPHS Ch. 40, Phaladeepika Ch. 26. Saturn's ~7.5-year span crossing 12th → 1st → 2nd from natal Moon.
2. **Dhaiya** (Kantaka Shani, Ashtama Shani) — Saturn in 4th or 8th from Moon, ~2.5 years each. Parallel afflicting transits that modern practice treats as "mini Sade-Satis."
3. **Major outer-planet transits** — Jupiter's 12-year circuit ingresses (guru peyarchi in Tamil tradition), Rahu/Ketu's 18-month-per-sign reverse march, Saturn's sign-by-sign ingresses (shani peyarchi).
4. **Eclipse events** — solar and lunar eclipses with their conjunction status to natal points.

All four produce **temporal event streams** (`temporal_event` and `temporal_range` output shapes from F7) that:
- The AI chat can query for "what's active right now" or "what's coming up."
- The end-user UI can render as a timeline.
- The astrologer workbench can overlay on natal chart.
- Aggregation strategies can compare across sources (e.g., different classical definitions of the exact Sade Sati start).

Core engine approach: **event stream, not date-by-date scan.** For each classical pattern, the engine precomputes *boundary* events (ingress, peak, exit) from Swiss Ephemeris positions, not a day-by-day evaluation. This keeps compute under 100 ms per chart for a 30-year horizon.

## 2. Scope

### 2.1 In scope

- **Sade Sati computation** with 3 phases (rising dhaiya / peak / setting dhaiya), start/end dates, retrograde re-entry handling.
- **Kantaka Shani** (Saturn in 4th from Moon) and **Ashtama Shani** (Saturn in 8th from Moon) as 2.5-year temporal ranges, including retrograde re-entry.
- **Jupiter sign ingresses** (Jupiter changing sign) for the next 30 years from any reference date.
- **Saturn sign ingresses** (Saturn changing sign) for the next 30 years — including retrograde back-and-forth within a sign boundary.
- **Rahu / Ketu sign ingresses** (~1.5 years per sign; reverse order through signs).
- **Solar eclipse events** and **lunar eclipse events** from Swiss Ephemeris, annotated with natal-point conjunctions (orb ≤ 3°).
- `ClassicalEngine` Protocol conformance for each pattern as a distinct rule.
- Rule YAML files per F6 DSL.
- REST endpoints + AI tool-use.
- 10 golden charts with known Sade Sati / Dhaiya / ingress dates verified against JH 7.x.

### 2.2 Out of scope

- **Ashtakavarga transit predictions** (gochara + bindu) — deferred to E6b.
- **Vedha chakra** (classical obstruction rules during transit) — E6b.
- **Personalized daily horoscope generation** — deferred; we produce events, not text.
- **Muhurta** (electional astrology for upcoming dates) — E6c.
- **Dasa-transit synthesis** (e.g., "Jupiter MD + Saturn transit to Jupiter natal") — covered at aggregation layer, not here.
- **Graha-dristi transit effects** — deferred. v1 focuses on ingress events and Saturn-Moon relative position; aspect-based transit effects in E6b.

### 2.3 Dependencies

- F1 (source_authority, `transit_event` family, `temporal_event` output shape).
- F2 (fact tables).
- F4, F6 (rule versioning, YAML loader).
- F7, F8 (JSON Schema for `temporal_event`; `ClassicalEngine` Protocol).
- F13, F16, F17 (content-hash provenance, golden suite, property harness).
- Existing `src/josi/services/transit_monitor.py` (raw transit computation — retained and wrapped).
- Existing `src/josi/services/astrology_service.py` AstrologyCalculator (for natal position retrieval).
- `pyswisseph` (Swiss Ephemeris) for high-precision planetary longitudes and eclipse events.

## 3. Classical / Technical Research

### 3.1 Sade Sati — BPHS Ch. 40, Phaladeepika Ch. 26

**Citation:** BPHS Ch. 40 v.8–15 (transit effects of Saturn), Phaladeepika Ch. 26 v.1–12 (*Śanīcara-gocara*).

**Definition:** Sade Sati is the period during which transiting Saturn occupies the 12th, 1st, and 2nd houses from the natal **Moon sign** (janma rashi). Saturn spends ~2.5 years in each sign; three consecutive signs = 7.5 years. Hence "Sade Sati" = *sāḍhe sātī* ("seven-and-a-half").

**Three phases** (classical nomenclature varies; modern commentary after B.V. Raman crystallizes):
- **Rising Dhaiya** / First Quarter (*prathama dhaiya*): Saturn in 12th from Moon. Affects physical health, expenditure, losses.
- **Peak** / Middle Quarter (*madhya dhaiya*): Saturn in 1st from Moon (same sign as Moon). Affects mind, marriage, profession.
- **Setting Dhaiya** / Last Quarter (*antya dhaiya*): Saturn in 2nd from Moon. Affects family, speech, wealth.

**Retrograde complication:** Saturn retrogrades ~4.5 months per year. In any multi-year window, Saturn typically enters sign N, retrogrades back to sign N-1, re-enters sign N. This means the "first moment Saturn enters 12th from Moon" is not always the clean "start date" of Sade Sati. Josi must emit **all boundary events** (entries, exits, re-entries), not just the nominal start.

**Canonical computation:**

```
Let M = natal Moon sidereal longitude (fixed for the chart)
Let M_sign = sign containing M (1..12)

Phase signs:
  phase_1_sign = (M_sign - 1 - 1) mod 12 + 1      # 12th from Moon
  phase_2_sign = M_sign                           # 1st from Moon
  phase_3_sign = M_sign mod 12 + 1                # 2nd from Moon

For a date range [T_start, T_end], scan Saturn's sidereal longitude:
  - Detect every sign-boundary crossing (ingress / egress).
  - Classify each crossing: entering phase_1 / exiting phase_1 / entering phase_2 / ... / exiting phase_3.
  - Emit an event per crossing with metadata: direction (direct/retrograde), sign, phase.
  - Reconcile sequences into "phase windows" (first-entry-to-last-exit ranges).
```

**Output shape (`temporal_range` for the overall Sade Sati and for each phase; `temporal_event` for individual ingress/egress):**

```json
{
  "sade_sati": {
    "active_now": true,
    "start": "2020-01-24T12:00:00Z",
    "end": "2027-06-03T18:00:00Z",
    "phases": [
      {"phase": "rising_dhaiya", "start": "2020-01-24", "end": "2022-07-12"},
      {"phase": "peak", "start": "2022-07-13", "end": "2025-02-11"},
      {"phase": "setting_dhaiya", "start": "2025-02-12", "end": "2027-06-03"}
    ],
    "saturn_retrograde_events": [
      {"type": "retrograde_entry_phase_1", "date": "2021-10-10"},
      {"type": "direct_reentry_phase_1", "date": "2022-02-23"}
    ],
    "citation": "BPHS Ch.40 v.8-15; Phaladeepika Ch.26"
  }
}
```

### 3.2 Kantaka Shani (Dhaiya) — Phaladeepika Ch. 26 v.14

**Citation:** Phaladeepika Ch. 26 v.14–16 (*kaṇṭaka-śanīcara*).

**Definition:** Saturn in 4th from natal Moon for ~2.5 years. "Kantaka" = thorn. Afflicts domestic life, property, emotional peace.

**Computation:** Same algorithm as Sade Sati but with a single phase sign = (M_sign + 3) mod 12 + 1 (4th from Moon).

### 3.3 Ashtama Shani (Dhaiya) — Phaladeepika Ch. 26 v.18

**Citation:** Phaladeepika Ch. 26 v.18 (*aṣṭama-śanīcara*).

**Definition:** Saturn in 8th from natal Moon for ~2.5 years. Afflicts longevity, chronic health, accidents.

**Computation:** Phase sign = (M_sign + 7 - 1) mod 12 + 1 (8th from Moon).

### 3.4 Jupiter sign ingresses

**Rationale:** Jupiter's 12-year return and sign-by-sign ingresses are major timing events in Vedic practice. In Tamil tradition this is *guru peyarchi*; in North India, *guru rashi parivartana*. Books and temples announce each Jupiter sign change. The list of ingresses for the next 30 years is a high-demand artifact.

**Computation:** Track Jupiter's sidereal longitude continuously over a date range; emit a `temporal_event` at each sign boundary crossing. Include retrograde re-entries (rare for Jupiter but possible near boundaries).

```
Let T_start, T_end = range (default: now, now + 30 years)
For each day t in [T_start, T_end]:
  lon_t = swe.calc_ut(julday(t), JUPITER, sidereal_flag)
  if sign(lon_t) != sign(lon_{t-1}):
    emit event {type: jupiter_ingress, from_sign: ..., to_sign: ..., direction: direct|retrograde, date: t}
```

In practice we bisect on sign changes rather than scanning daily for precision.

**Output:** List of `temporal_event`s with citation "Classical tradition; no single verse."

### 3.5 Saturn sign ingresses (shani peyarchi)

**Rationale:** Same as Jupiter but for Saturn. Used alongside Sade Sati determination.

**Computation:** Identical to §3.4 but for Saturn.

### 3.6 Rahu / Ketu sign ingresses

**Rationale:** Rahu and Ketu transit in **retrograde** through signs at ~18 months per sign. Ingress events are widely announced. Ketu is always exactly 180° from Rahu.

**Computation:** Same as Jupiter but use mean node longitude (classical) or true node (modern). Josi default: **mean node** (matches JH 7.x default and classical intention — the "averaged" node is what 19th-century almanacs used).

### 3.7 Eclipse events

**Source:** Swiss Ephemeris `swe_sol_eclipse_when_glob` and `swe_lun_eclipse_when_glob` APIs.

**Events emitted:** Each eclipse gets a `temporal_event` with:
- `eclipse_type`: solar (total / annular / partial / hybrid) or lunar (total / partial / penumbral)
- `peak_datetime` (UTC)
- `eclipse_longitude` (sidereal)
- `eclipse_sign`
- `visibility_region` (from Swiss Ephemeris; optional)
- `natal_conjunctions`: list of natal planets / angles within 3° orb of the eclipse longitude
- `citation`: "Computed from Swiss Ephemeris"

**Natal conjunction highlighting** is the differentiator: we don't just emit eclipses, we tag which eclipses hit the user's natal points, since that's what classical practice cares about (eclipses on natal Moon/Sun/ascendant are classical malefic timers, BPHS Ch. 98).

### 3.8 Engine architecture

Five engines under a shared `BaseTransitEngine`:

```
BaseTransitEngine
  ├─ natal_moon_sign(chart) → int
  ├─ natal_point_longitudes(chart) → dict[str, float]
  ├─ scan_planet_longitude(planet, T_start, T_end) → list[(date, longitude)]
  └─ detect_sign_crossings(series) → list[event]

SadeSatiEngine(BaseTransitEngine)
  – 3-phase window + individual retrograde events

DhaiyaEngine(BaseTransitEngine)
  – 1-phase window (instantiated as KantakaShani and AshtamaShani)

PlanetaryIngressEngine(BaseTransitEngine)
  – generic for Jupiter, Saturn, Rahu/Ketu

EclipseEngine(BaseTransitEngine)
  – Swiss Ephemeris eclipse calls + natal conjunction annotation
```

### 3.9 Precision model

- All dates emitted at UTC, datetime-precision.
- Sign-boundary crossings bisected to 1-minute precision in UTC.
- Retrograde direction detected by sign of (lon_t - lon_{t-1}).
- Acceptance target: ±1 day vs JH 7.x for Sade Sati boundaries; ±6 hours for individual ingress events.

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| Mean node vs true node for Rahu/Ketu | Mean node (default) | Matches JH 7.x + classical almanacs; configurable per astrologer later |
| Emit individual retrograde events within a Sade Sati, or only phase boundaries? | Both | AI chat can explain "you're in re-entry"; UI can collapse |
| What date range default for Jupiter/Saturn/Rahu ingresses? | 30 years from today, minimum | Covers typical user's remaining life-horizon |
| Eclipse orb for natal conjunction | 3° (sidereal) | BPHS implicit; most classical texts reference 3-5°; 3° chosen as conservative/specific |
| Eclipse visibility — regional highlighting? | Optional; include in response but not required for activation | Classical texts emphasize eclipse in birth chart, not visibility |
| Sade Sati start date: first 12th-from-Moon entry, or first *direct* 12th-from-Moon entry that sticks? | First entry (including retrograde); metadata flags retrograde subsequences | Most classical reference is "when Saturn first enters" without direction qualifier |
| Output shape: single `temporal_range` per Sade Sati or event stream? | Both — parent `temporal_range` + nested events | AI chat usage drives structured; UI renders timeline |
| Support past Sade Satis? | Yes; emit all within a configurable window [birth, now+30y] | Astrological reading often references past Sade Sati outcomes |
| Configurable orbs for natal conjunctions beyond eclipses | Deferred to E6b | Scope control |
| Time zone handling — return UTC only? | UTC in JSON; frontend converts to user TZ | API convention |

## 5. Component Design

### 5.1 New modules

```
src/josi/services/classical/transit/
├── __init__.py
├── base_transit_engine.py           # shared scan + crossing detection
├── sade_sati_engine.py
├── dhaiya_engine.py                 # shared for Kantaka + Ashtama
├── planetary_ingress_engine.py      # Jupiter / Saturn / Rahu / Ketu
├── eclipse_engine.py
└── natal_conjunction_util.py        # orb-based natal point matching

src/josi/db/rules/transit/
├── sade_sati_bphs.yaml
├── kantaka_shani_phaladeepika.yaml
├── ashtama_shani_phaladeepika.yaml
├── jupiter_ingress.yaml
├── saturn_ingress.yaml
├── rahu_ketu_ingress.yaml
└── eclipse_events.yaml

tests/golden/charts/transit/
├── chart_01_sade_sati_expected.yaml
├── ...
└── chart_10_sade_sati_expected.yaml
```

### 5.2 Rule YAML examples

**`sade_sati_bphs.yaml`:**

```yaml
rule_id: transit.sade_sati.bphs
source_id: bphs
version: "1.0.0"
technique_family_id: transit_event
output_shape_id: temporal_range
citation: "BPHS Ch.40 v.8-15; Phaladeepika Ch.26"
classical_names:
  en: "Sade Sati"
  sa_iast: "Sāḍhe Sātī"
  sa_devanagari: "साढ़े साती"
  hi: "साढ़े साती"
  ta: "சாடே சாதி"
effective_from: "2026-01-01T00:00:00Z"
effective_to: null

activation:
  predicate:
    op: always_true       # computed whenever a chart exists

compute:
  engine: sade_sati
  parameters:
    affecting_planet: saturn
    reference_point: natal_moon_sign
    phase_offsets_from_reference: [-1, 0, 1]   # 12th, 1st, 2nd
    phase_names: [rising_dhaiya, peak, setting_dhaiya]
    detect_retrograde_subevents: true
    scan_window_years_past: 80     # full life horizon back
    scan_window_years_future: 30
    boundary_precision_minutes: 1
  output:
    shape: temporal_range_with_sub_phases
```

**`kantaka_shani_phaladeepika.yaml`:**

```yaml
rule_id: transit.kantaka_shani.phaladeepika
source_id: phaladeepika
version: "1.0.0"
technique_family_id: transit_event
output_shape_id: temporal_range
citation: "Phaladeepika Ch.26 v.14-16"
classical_names:
  en: "Kantaka Shani"
  sa_iast: "Kaṇṭaka Śanīcara"

activation:
  predicate:
    op: always_true

compute:
  engine: dhaiya
  parameters:
    affecting_planet: saturn
    reference_point: natal_moon_sign
    phase_offset_from_reference: 3      # 4th from Moon
    phase_name: kantaka_shani
    detect_retrograde_subevents: true
```

**`ashtama_shani_phaladeepika.yaml`:** similar, `phase_offset_from_reference: 7`.

**`jupiter_ingress.yaml`:**

```yaml
rule_id: transit.jupiter_ingress.classical
source_id: bphs
version: "1.0.0"
technique_family_id: transit_event
output_shape_id: temporal_event
citation: "Classical tradition (guru peyarchi)"

activation:
  predicate:
    op: always_true

compute:
  engine: planetary_ingress
  parameters:
    planet: jupiter
    scan_window_years_future: 30
    emit_retrograde_reentries: true
```

**`eclipse_events.yaml`:**

```yaml
rule_id: transit.eclipses.swiss_ephemeris
source_id: bphs       # annotated per BPHS eclipse rules for natal impact
version: "1.0.0"
technique_family_id: transit_event
output_shape_id: temporal_event
citation: "BPHS Ch.98 (eclipse effects); computation via Swiss Ephemeris"

activation:
  predicate:
    op: always_true

compute:
  engine: eclipse
  parameters:
    include_solar: true
    include_lunar: true
    scan_window_years_past: 5
    scan_window_years_future: 30
    natal_conjunction_orb_degrees: 3.0
    natal_points_to_check: [sun, moon, mars, mercury, jupiter, venus, saturn, rahu, ketu, ascendant, midheaven]
```

### 5.3 Engine interface

```python
# src/josi/services/classical/transit/base_transit_engine.py

class TransitEvent(BaseModel):
    event_type: str                    # e.g., "sade_sati_start", "jupiter_ingress"
    date: datetime                     # UTC
    metadata: dict = Field(default_factory=dict)
    citation: str | None = None

class TransitRange(BaseModel):
    range_type: str                    # e.g., "sade_sati", "kantaka_shani"
    start: datetime
    end: datetime
    phases: list["TransitRange"] = Field(default_factory=list)   # nested sub-ranges
    events: list[TransitEvent] = Field(default_factory=list)     # retrograde re-entries etc
    metadata: dict = Field(default_factory=dict)
    citation: str | None = None

class BaseTransitEngine:
    technique_family_id = "transit_event"

    async def compute_for_source(
        self, session: AsyncSession, chart_id: UUID, source_id: str,
        rule_ids: list[str] | None = None,
    ) -> list[TechniqueComputeRow]: ...

    def scan_longitude(
        self, planet: str, t_start: datetime, t_end: datetime, step_days: float = 1.0,
    ) -> list[tuple[datetime, float]]:
        """Dense longitude samples via pyswisseph."""

    def find_sign_crossings(
        self, series: list[tuple[datetime, float]], precision_minutes: int = 1,
    ) -> list[tuple[datetime, int, int, str]]:
        """Bisects to precision. Returns (when, from_sign, to_sign, direction)."""
```

### 5.4 REST API contract

```
GET /api/v1/transits/{chart_id}/sade-sati
GET /api/v1/transits/{chart_id}/dhaiya          # returns both Kantaka + Ashtama
GET /api/v1/transits/{chart_id}/ingresses?planet=jupiter&from=2026-01-01&to=2056-01-01
GET /api/v1/transits/{chart_id}/eclipses?from=...&to=...

Response (sade-sati):
{
  "success": true,
  "data": {
    "is_active": true,
    "current_phase": "peak",
    "history": [ /* past Sade Satis within configured horizon */ ],
    "current": {
      "start": "2020-01-24T12:00:00Z",
      "end": "2027-06-03T18:00:00Z",
      "phases": [ ... ],
      "saturn_retrograde_subevents": [ ... ],
      "citation": "BPHS Ch.40 v.8-15; Phaladeepika Ch.26"
    },
    "upcoming": []
  },
  "errors": null
}
```

### 5.5 AI tool-use extension

```python
@tool
def get_transit_events(
    chart_id: str,
    date_range: DateRange,
    importance: Literal["major", "minor", "all"] = "major",
    event_types: list[Literal["sade_sati", "dhaiya", "jupiter_ingress", "saturn_ingress",
                              "rahu_ketu_ingress", "eclipse"]] | None = None,
) -> list[TransitEvent]:
    """Returns transit events overlapping the given date range. `major` = Sade Sati, Dhaiya,
       ingresses of Jupiter/Saturn/Rahu-Ketu, and eclipses with natal conjunction.
       Response includes citations and natal-point interactions where applicable."""
```

## 6. User Stories

### US-E6a.1: As an end user, I want to ask "Am I in Sade Sati?" and get a precise answer
**Acceptance:** AI tool `get_transit_events` with `event_types=['sade_sati']` returns current phase, start, end, and retrograde subevents, cited to BPHS 40 + Phaladeepika 26.

### US-E6a.2: As an end user, I want to see Jupiter's next sign change
**Acceptance:** `/api/v1/transits/{chart_id}/ingresses?planet=jupiter` returns the next ingress with date, from_sign, to_sign.

### US-E6a.3: As an astrologer, I want to see all eclipses that hit my client's natal Moon within a 5-year window
**Acceptance:** `/api/v1/transits/{chart_id}/eclipses?from=2026-01-01&to=2031-01-01` returns eclipses; each lists `natal_conjunctions` with orb details; those conjunct natal Moon are flagged.

### US-E6a.4: As an AI chat user asking "when does my Sade Sati end", I get a date, the phase transitions, and the citation
**Acceptance:** Response includes end date, 3 phases breakdown, citation "BPHS Ch.40 v.8-15; Phaladeepika Ch.26".

### US-E6a.5: As an engineer, I want golden tests that match JH 7.x Sade Sati dates
**Acceptance:** 10 golden charts; each has manually-JH-verified Sade Sati ranges; tests pass within ±1 day tolerance for phase boundaries.

### US-E6a.6: As a classical advisor, I can switch the Kantaka Shani source from Phaladeepika to BPHS (if a variant emerges)
**Acceptance:** Adding a `kantaka_shani_bphs.yaml` rule with alternate citation is additive; existing compute rows retain their source_id.

## 7. Tasks

### T-E6a.1: Build `BaseTransitEngine` with scan + crossing detection
- **Definition:** Shared class with `scan_longitude()` and `find_sign_crossings()` using `pyswisseph`. 1-minute precision via bisection.
- **Acceptance:** Unit tests: known Jupiter ingress date matches expected ±1 minute.
- **Effort:** 2 days
- **Depends on:** F8

### T-E6a.2: Implement `SadeSatiEngine`
- **Definition:** Subclass computes 3-phase windows, classifies events as rising_dhaiya / peak / setting_dhaiya, records retrograde re-entries.
- **Acceptance:** For Moon-in-Sagittarius test chart, current Sade Sati (2020–2027) matches JH 7.x ±1 day.
- **Effort:** 3 days
- **Depends on:** T-E6a.1

### T-E6a.3: Implement `DhaiyaEngine` (Kantaka + Ashtama)
- **Definition:** Parameterized engine for 4th-from-Moon and 8th-from-Moon. Same retrograde logic as Sade Sati.
- **Acceptance:** Unit tests for 5 sample charts; JH 7.x match ±1 day.
- **Effort:** 1 day
- **Depends on:** T-E6a.2

### T-E6a.4: Implement `PlanetaryIngressEngine`
- **Definition:** Generic engine for Jupiter, Saturn, Rahu, Ketu. Configurable via rule YAML (planet name, retrograde emission).
- **Acceptance:** Unit tests verify Jupiter ingress into current+next 3 signs; Saturn similar; Rahu/Ketu retrograde direction correct.
- **Effort:** 2 days
- **Depends on:** T-E6a.1

### T-E6a.5: Implement `EclipseEngine`
- **Definition:** Use `swe_sol_eclipse_when_glob` and `swe_lun_eclipse_when_glob`. For each, compute sidereal longitude, sign, natal conjunctions (orb ≤ 3°) via natal chart lookup.
- **Acceptance:** Unit tests: solar eclipse April 8, 2024 computed correctly; natal conjunction annotation for a test chart with Sun at that longitude picks it up.
- **Effort:** 2 days
- **Depends on:** T-E6a.1

### T-E6a.6: Author all 7 rule YAML files
- **Definition:** Write rules per §5.2; load via F6.
- **Acceptance:** 7 new rows in `classical_rule`; content hashes stable.
- **Effort:** 1 day
- **Depends on:** F6

### T-E6a.7: Wire `ClassicalEngine` Protocol conformance + idempotent compute
- **Definition:** Each engine emits `technique_compute` rows; idempotent; output hash stable.
- **Acceptance:** Integration test inserts rows; second run is no-op.
- **Effort:** 1 day
- **Depends on:** T-E6a.2, T-E6a.3, T-E6a.4, T-E6a.5

### T-E6a.8: REST endpoints (4)
- **Definition:** `/sade-sati`, `/dhaiya`, `/ingresses`, `/eclipses` on `/api/v1/transits/{chart_id}/`.
- **Acceptance:** All 4 endpoints return valid shapes; query params validated; 4xx on bad input.
- **Effort:** 1 day
- **Depends on:** T-E6a.7

### T-E6a.9: AI tool `get_transit_events`
- **Definition:** Typed tool per §5.5. Queries all 4 sub-engines based on requested `event_types`.
- **Acceptance:** Integration test with chat agent.
- **Effort:** 0.5 day
- **Depends on:** T-E6a.8

### T-E6a.10: Golden chart fixtures
- **Definition:** 10 birth charts with expected Sade Sati ranges (including retrograde subevents), Kantaka/Ashtama windows, Jupiter ingress dates for next 12 years, eclipses hitting natal points within a 10-year window. All verified manually against JH 7.x.
- **Acceptance:** Fixtures complete; classical-advisor signed.
- **Effort:** 3 days (JH verification is the bottleneck)
- **Depends on:** T-E6a.7

### T-E6a.11: Property tests (F17)
- **Definition:** Invariants: (a) Sade Sati total ≈ 7.5 years ± 6 months (varies due to retrograde), (b) 3 phases sum ≈ total, (c) phase order preserved, (d) Kantaka + Ashtama never overlap Sade Sati peak (they can overlap rising/setting dhaiyas at edges — document), (e) Jupiter ingress count over N years ≈ N (Jupiter ~1 year per sign), (f) Saturn ingress count ≈ N / 2.5, (g) eclipse count ≈ 4/year average over long windows.
- **Acceptance:** 1000 Hypothesis examples per invariant; all pass.
- **Effort:** 1 day
- **Depends on:** T-E6a.7

### T-E6a.12: Performance testing
- **Definition:** Measure end-to-end compute for one chart: all 7 transit rules, 30-year future horizon. Target < 500 ms on dev machine.
- **Acceptance:** Benchmark script reports < 500 ms median over 100 runs.
- **Effort:** 0.5 day
- **Depends on:** T-E6a.7

### T-E6a.13: Differential test vs JH 7.x
- **Definition:** For 10 golden charts, compare Sade Sati phase boundaries, Kantaka/Ashtama boundaries, next 5 Jupiter ingresses, next 5 Saturn ingresses, and all eclipses in a 10-year window to JH output.
- **Acceptance:** Phase boundaries within ±1 day; ingresses within ±6 hours; eclipses within ±1 minute.
- **Effort:** 2 days
- **Depends on:** T-E6a.10

## 8. Unit Tests

### 8.1 BaseTransitEngine

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_scan_longitude_monotonic_direct` | Jupiter, 1-year window | Longitude increases monotonically (or decreases during retrograde) | Sanity |
| `test_find_crossing_precision` | Jupiter near Aries→Taurus | Bisection finds boundary to 1-minute precision | Precision target |
| `test_find_retrograde_reentry` | Saturn near sign boundary in known retrograde | Emits 2 crossings (exit + re-entry) | Retrograde handling |

### 8.2 SadeSatiEngine

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_sadesati_moon_in_sagittarius_2020_2027` | chart with Moon 258° (Sag) | Current Sade Sati: 2020-01-24 start, 2027-06-03 end ±1 day | JH-verified |
| `test_sadesati_three_phases_in_order` | any chart | rising_dhaiya → peak → setting_dhaiya in time order | Ordering invariant |
| `test_sadesati_retrograde_subevents_emitted` | chart with known Saturn retrograde during active SS | Retrograde event list non-empty | Completeness |
| `test_sadesati_inactive_when_saturn_far_from_moon` | chart with Moon-to-Saturn-sign distance > 2 | `is_active = false` | Negative |
| `test_sadesati_past_satis_listed` | 50-year-old chart | History list non-empty | Full horizon |

### 8.3 DhaiyaEngine

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_kantaka_saturn_in_4th_from_moon` | chart with Saturn transiting 4th from Moon today | `active=true`, range spans ~2.5y | Classical |
| `test_ashtama_saturn_in_8th_from_moon` | similar for 8th | `active=true`, range spans ~2.5y | |
| `test_kantaka_ashtama_do_not_overlap_sadesati_peak` | synthetic chart | No temporal overlap with peak phase | Phase exclusivity (peak is 1st-from-Moon, not 4th or 8th) |

### 8.4 PlanetaryIngressEngine

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_jupiter_ingress_2026_aries_to_taurus` | Jupiter, Apr 2026 | Ingress date matches JH ±6h | Differential |
| `test_saturn_ingress_retrograde_reentry` | Saturn 2025-2026 Aquarius-Pisces boundary | 3 ingresses: direct entry, retrograde exit, direct re-entry | Retrograde correctness |
| `test_rahu_ketu_retrograde_direction` | Rahu, any window | sign changes in reverse zodiacal order | Rahu's natural retrograde motion |
| `test_ingress_count_over_12_years_for_jupiter` | 12-year window | ~12 ingresses | Expected cadence |

### 8.5 EclipseEngine

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_solar_eclipse_2024_04_08` | scan window includes Apr 2024 | Solar eclipse total, peak ≈ 18:17 UTC, longitude ~19° Pisces sidereal | Known event |
| `test_natal_conjunction_within_3deg` | test chart with Sun at 19.5° Pisces sidereal | Eclipse flags natal Sun conjunction with orb ~0.5° | Conjunction detection |
| `test_natal_conjunction_not_within_3deg` | test chart with Sun at 23° Pisces | No flag on this eclipse | Orb boundary |
| `test_lunar_eclipse_counted` | 10-year window | Lunar eclipses ≈ 2/year | Cadence sanity |

### 8.6 Integration / API

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_rest_sade_sati_returns_shape` | `/api/v1/transits/{id}/sade-sati` | 200 with `is_active`, `current_phase`, `citation` | API shape |
| `test_rest_ingresses_filter_by_date_range` | `?from=2026-01-01&to=2028-01-01` | Events within range only | Filter correctness |
| `test_ai_tool_get_transit_events` | date_range, event_types=['sade_sati','jupiter_ingress'] | Combined list | Tool call |
| `test_compute_rows_idempotent` | Compute twice | Same row count | Idempotency |
| `test_compute_rows_cited` | Inspect result JSONB | `citation` present | Citation embedding |

### 8.7 Property tests (Hypothesis)

| Test name | Invariant | Rationale |
|---|---|---|
| `test_sadesati_total_duration_bound` | 6.5y ≤ (end - start) ≤ 8.0y for any chart | Saturn retrograde variance |
| `test_sadesati_phases_sum_eq_total` | sum of 3 phase durations = total (allow ±1 day for edge) | Composition |
| `test_ingress_monotonic_time` | emitted events in increasing time order | Temporal |
| `test_eclipse_peak_in_window` | for each emitted eclipse, scan_start ≤ peak ≤ scan_end | Filtering correctness |
| `test_natal_conjunction_orb_bound` | for each flagged conjunction, orb ≤ configured value | Conjunction |

### 8.8 Golden suite

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_golden_chart_01_sadesati` | fixture 01 | Phase boundaries ±1 day vs JH | Differential |
| ... (×10 charts) | | | |
| `test_golden_chart_jupiter_next_5_ingresses` | fixture | 5 upcoming ingresses ±6h vs JH | |
| `test_golden_chart_eclipses_10y` | fixture | Eclipse list matches JH 1:1; natal conjunctions match | |

## 9. EPIC-Level Acceptance Criteria

- [ ] 5 transit engines (SadeSati, Dhaiya, PlanetaryIngress, Eclipse, Base shared) implement `ClassicalEngine` Protocol
- [ ] 7 rule YAMLs loaded into `classical_rule` via F6
- [ ] REST endpoints `/sade-sati`, `/dhaiya`, `/ingresses`, `/eclipses` functional
- [ ] AI tool `get_transit_events` works end-to-end
- [ ] Golden suite: 10 charts × ~6 patterns each = ~60 assertions; Sade Sati phase boundaries within ±1 day vs JH 7.x
- [ ] Jupiter/Saturn ingresses within ±6 hours vs JH
- [ ] Eclipses within ±1 minute vs Swiss Ephemeris canonical
- [ ] Natal conjunction annotation working with configurable orb
- [ ] Property tests pass with ≥1000 Hypothesis examples per invariant
- [ ] Unit test coverage ≥ 90% for new code
- [ ] `chart_reading_view.transit_highlights` JSONB populated for every chart
- [ ] End-to-end compute for a single chart (all 7 rules, 30-year horizon) < 500 ms P99
- [ ] Docs: `CLAUDE.md` notes transit intelligence capability; API docs show all 4 endpoints with examples

## 10. Rollout Plan

- **Feature flag:** `ENABLE_TRANSIT_INTELLIGENCE` (default `true` on P1).
- **Shadow compute:** on staging, run for 1000 charts; spot-check 20 Sade Satis manually against JH 7.x; verify 5 known eclipses.
- **Backfill strategy:** on-demand (no pre-compute). `chart_reading_view.transit_highlights` populated lazily on first API read, then TTL-refreshed via background worker (see S3).
- **Rollback plan:** flip flag off → endpoints return 503; AI tool returns empty list. Rules soft-deprecated via `effective_to`.

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Swiss Ephemeris ayanamsa drift between versions | Low | Medium | Pin `pyswisseph` version; golden tests catch regressions |
| Sade Sati definition (12th-1st-2nd from Moon) vs lineage using ascendant instead | Low | Medium | Classical default is Moon (BPHS); alternate rule can be added |
| Retrograde re-entry classification ambiguous near boundary | Medium | Medium | Document: re-entry counts as "still active" span; phase doesn't restart |
| Eclipse orb convention variance | Medium | Low | 3° is conservative; configurable per astrologer in pro-mode |
| Performance on 30-year scans (dense) | Medium | Medium | Coarse daily scan + bisection for boundaries; cache intermediate series per chart |
| JH 7.x as reference is itself a black box (no source) | Medium | Medium | Augment with B.V. Raman hand-computed examples for cross-verification |
| Time zone off-by-one for boundaries reported in UTC | Medium | Low | All API timestamps ISO 8601 UTC; frontend converts |
| Rahu/Ketu mean vs true node user expectation mismatch | Medium | Low | Document default; config surface in astrologer preferences |
| Eclipse visibility regionalization deferred; users may expect local visibility | Medium | Low | Clarify in docs: events are astrological (sidereal), not regional visual |

## 12. References

- Master spec: [`docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`](../../../superpowers/specs/2026-04-19-classical-techniques-expansion-design.md)
- F1, F2, F6, F7, F8, F13, F16, F17 (dependencies)
- Classical sources:
  - Brihat Parashara Hora Shastra Ch. 40 (Saturn transit effects), Ch. 98 (eclipse effects).
  - Phaladeepika by Mantreswara, Ch. 26 (*Śanīcara-gocara*, Kantaka Shani, Ashtama Shani).
  - Saravali Ch. 39–40 (transit cross-references).
  - Jataka Parijata Ch. 16 (supplementary).
  - B.V. Raman, *Notable Horoscopes* (Sade Sati case studies).
- Existing Josi: `src/josi/services/transit_monitor.py`, `src/josi/services/astrology_service.py`
- External: `pyswisseph` (eclipse + longitude computations), Jagannatha Hora 7.x (reference)
