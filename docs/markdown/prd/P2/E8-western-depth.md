---
prd_id: E8
epic_id: E8
title: "Western Depth — Arabic Parts, Fixed Stars, Harmonics, Eclipses, Uranian"
phase: P2-breadth
tags: [#correctness, #extensibility, #ai-chat, #astrologer-ux]
priority: should
depends_on: [F1, F2, F6, F7, F8, F13, E1a]
enables: [E14a, P2-UI-western]
classical_sources: [dorotheus, valens, ptolemy, paulus_alexandrinus, addey, witte_hamburg]
estimated_effort: 4-5 weeks
status: draft
author: "@agent"
last_updated: 2026-04-19
---

# E8 — Western Depth: Arabic Parts, Fixed Stars, Harmonics, Eclipses, Uranian Points

## 1. Purpose & Rationale

Josi's Western module currently handles tropical placements, standard aspects, and basic house systems. Five deeper traditions of Western classical and modern astrology remain unimplemented and are routinely cited by serious Western practitioners:

1. **Arabic Parts / Hellenistic Lots** (Dorotheus, Paulus, Valens) — sect-aware computed points like Part of Fortune, Part of Spirit, Part of Eros. Core to Hellenistic practice; also used in medieval Arabic astrology (hence "Arabic Parts").
2. **Fixed Stars** (Ptolemy → Brady) — 60+ bright stars with classical interpretations. Conjunctions with natal points within 1° orb. Parans (simultaneous rising/culminating/setting) for mundane work.
3. **Harmonic Charts** (Addey, Harding) — mathematical transforms of the natal chart revealing latent patterns. 5th (talent), 7th (spiritual), 9th (marriage — philosophically parallel to Navamsa), 12th (karmic), etc.
4. **Eclipses** (NASA catalog-anchored) — solar/lunar eclipses 200 years past and 50 years future; conjunction with natal points; Saros cycle membership for eclipse-family interpretation.
5. **Uranian Sensitive Points / Midpoints** (Witte, Hamburg School) — midpoints, reflection points, planetary pictures. Uranian astrology is a distinct mid-20th-century methodology; its midpoint arithmetic is reused widely even outside Uranian strict practice.

Without these, Josi cannot credibly serve Western professional astrologers or feed a Western-depth AI chat. With them, we achieve parity with Solar Fire and exceed most open-source Python astrology libraries.

This PRD delivers all five as first-class engines, each conforming to the classical-techniques architecture (F1–F8), each emitting F7-typed output shapes, each source-attributed to its classical authority.

## 2. Scope

### 2.1 In scope

- **Arabic Parts / Lots (50 ranked Lots, sect-aware)**:
  - 7 Hermetic Lots (Fortune, Spirit, Eros, Necessity, Courage, Victory, Nemesis)
  - Sect-variant formulas per Paulus / Dorotheus / Valens for each Lot
  - 43 additional commonly-cited Lots (Marriage, Death, Sickness, Children, Father, Mother, etc.)
  - Lot activation (when a Lot's sign lord is strong/aspected)
- **Fixed Stars (60 ranked)**:
  - Royal Stars (Regulus, Spica, Antares, Aldebaran) — full treatment
  - 56 additional: Algol, Sirius, Fomalhaut, Alphard, Arcturus, Procyon, Betelgeuse, Rigel, Vega, Altair, Deneb, Capella, Pollux, Castor, etc.
  - Epoch-adjusted sidereal positions via Swiss Ephemeris `swe.fixstar`
  - Conjunction detection with natal points within 1° orb
  - **Parans** — rising/culminating/setting within a specified time window at chart's latitude
- **Harmonic Charts** (7 key harmonics):
  - H5 (talent), H7 (spiritual), H9 (marriage), H10 (career-fulfillment), H11 (friendship/group), H12 (karmic), H16 (tests/crises)
  - Harmonic aspect interpretation (same as natal aspects applied to harmonic chart)
- **Eclipses**:
  - NASA Five Millennium Canon dataset (local static file, Saros-indexed) covering 200y past + 50y future
  - Conjunctions of eclipse points with natal planets/angles within 3° orb
  - Saros cycle membership and family identification
- **Uranian Sensitive Points**:
  - Midpoints (half-sums) for all pairwise planetary combos → 78 midpoints for 10 planets + 3 angles
  - Reflection points (2B − A)
  - Sum points (A + B)
  - Planetary pictures: match natal planet within 2° of a midpoint
  - 8 Uranian hypothetical planets (Cupido, Hades, Zeus, Kronos, Apollon, Admetos, Vulkanus, Poseidon) — positional support via Witte's ephemeris tables
- **Output shape emission**:
  - Lots, fixed stars, Uranian points → `structured_positions`
  - Harmonic charts → reuse existing chart shape (`structured_positions` with details.harmonic_number)
  - Eclipses → `temporal_event`
- **Rule YAMLs** registered by tradition:
  - Hellenistic Lots → `source_id='dorotheus'`, `'paulus_alexandrinus'`, `'valens'`
  - Fixed stars → `source_id='ptolemy'`, `'brady'` (for modern parans)
  - Harmonics → `source_id='addey'`
  - Uranian → `source_id='witte_hamburg'`
- **API surface**:
  - `GET /api/v1/charts/{chart_id}/western/lots` (with `?tradition=hellenistic|medieval|all`)
  - `GET /api/v1/charts/{chart_id}/western/fixed-stars?orb=1.0`
  - `GET /api/v1/charts/{chart_id}/western/harmonics/{H}` (H ∈ {5,7,9,10,11,12,16})
  - `GET /api/v1/charts/{chart_id}/western/eclipses?from=YYYY-MM-DD&to=YYYY-MM-DD`
  - `GET /api/v1/charts/{chart_id}/western/uranian` → midpoints + planetary pictures

### 2.2 Out of scope

- **Primary directions** — separate classical technique; P3.
- **Profections** (Hellenistic annual profections) — scoped to a future Western-annual EPIC (parallel to E5 Varshaphala).
- **Solar arc directions** — deferred.
- **Horary "Urdha Lagna" equivalents for Western horary** — E10 handles horary under Vedic/KP; Western horary separate.
- **Uranian Transneptunians' exact ephemeris** beyond Witte tables — we ship Witte's positions as static data, not compute from gravitational models.
- **Eclipse shadow paths / visibility maps** — geographic projection out of scope; only point-in-time.
- **Bernadette Brady's star-phase lifecycle analysis** — modern Brady treatment beyond parans; phase-cycle deferred.
- **Translation of medieval Arabic Lots beyond Hermetic 7 + 43 top-ranked** — long tail in Holden / Hand inventories.

### 2.3 Dependencies

- F1 — add `source_id`: `dorotheus`, `paulus_alexandrinus`, `valens`, `ptolemy`, `brady`, `addey`, `witte_hamburg`
- F2 — fact tables
- F6 — DSL loader (Lot formulas as rules; fixed-star identification as rules)
- F7 — `structured_positions`, `temporal_event`
- F8 — aggregation protocol
- E1a — natal chart primitives (including sect determination)
- `pyswisseph` — `swe.fixstar` for fixed-star ephemeris; `swe.sol_eclipse_when_glob`, `swe.lun_eclipse_when_glob` for eclipse dates
- NASA Five Millennium Canon of Solar/Lunar Eclipses — static data file (public domain, Goddard)
- Witte Transneptunian table — static data (published in Witte & Lefeldt)

## 3. Classical Research

### 3.1 Arabic Parts / Hellenistic Lots

**Primary sources:**
- Dorotheus of Sidon, *Carmen Astrologicum* (~75 CE; Pingree Greek-to-English ed.) — Book I-V; sect-aware Lot formulas.
- Paulus Alexandrinus, *Introductory Matters* (378 CE; Greenbaum trans. 2001) — Ch. 23 on Lots.
- Vettius Valens, *Anthology* (~170 CE; Riley trans.) — Books II-IV scattered Lot references.
- Al-Biruni, *Elements of Astrology* (~1029 CE; Wright trans.) — medieval codification.
- Robert Hand, *Night & Day: Planetary Sect in Astrology* (1995) — modern synthesis.

**The sect rule:** in diurnal (day) charts, the formula uses `A − B + Ascendant`; in nocturnal (night) charts, the formula reverses to `B − A + Ascendant` for "reversing Lots." Not all Lots reverse — only those tied to sect-variable significators.

**Determining sect:**
- Day chart: Sun above horizon (in houses 7–12).
- Night chart: Sun below horizon (in houses 1–6).

This is E1a's existing sect determination; E8 consumes it.

**The 7 Hermetic Lots (Paulus Ch. 23):**

| # | Lot | Day formula | Night formula | Citation |
|---|---|---|---|---|
| 1 | Fortune | Moon − Sun + Asc | Sun − Moon + Asc | Paulus 23.1; Dorotheus I.26 |
| 2 | Spirit | Sun − Moon + Asc | Moon − Sun + Asc | Paulus 23.2 |
| 3 | Eros | Venus − Spirit + Asc | Spirit − Venus + Asc | Paulus 23.3 |
| 4 | Necessity | Fortune − Mercury + Asc | Mercury − Fortune + Asc | Paulus 23.4 |
| 5 | Courage | Mars − Fortune + Asc | Fortune − Mars + Asc | Paulus 23.5 |
| 6 | Victory | Jupiter − Spirit + Asc | Spirit − Jupiter + Asc | Paulus 23.6 |
| 7 | Nemesis | Fortune − Saturn + Asc | Saturn − Fortune + Asc | Paulus 23.7 |

**Additional 43 commonly-cited Lots** — listed with primary citation:

| # | Lot | Day formula | Reversed? | Citation |
|---|---|---|---|---|
| 8 | Marriage (men) | Venus − Saturn + Asc | No | Dorotheus II.3 |
| 9 | Marriage (women) | Saturn − Venus + Asc | No | Dorotheus II.3 |
| 10 | Children | Jupiter − Saturn + Asc | Yes | Dorotheus II.10 |
| 11 | Father | Sun − Saturn + Asc | Yes | Valens II.36 |
| 12 | Mother | Moon − Venus + Asc | Yes | Valens II.36 |
| 13 | Siblings | Jupiter − Saturn + Asc | No (shares formula w/ Children; context) | Al-Biruni 476 |
| 14 | Death | Saturn − Moon + Asc (8H of Fortune) | No | Valens II.37 |
| 15 | Sickness | Mars − Saturn + Asc | No | Dorotheus IV.1 |
| 16 | Imprisonment | Saturn − Fortune + Asc | No | Valens IV.11 |
| 17 | Exaltation | 19° Aries − Sun + Asc (day); 3° Taurus − Moon + Asc (night) | Custom | Paulus 23.8 |
| 18 | Commerce | Fortune − Spirit + Asc | Yes | Al-Biruni 477 |
| 19 | Treachery | Mars − Saturn + Asc | No | Dorotheus IV.1 |
| 20 | Travel | 9th cusp − 9H lord + Asc | No | Al-Biruni 478 |
| 21 | Friendship | Mercury − Moon + Asc | No | Al-Biruni 478 |
| 22 | Enemies | 12th cusp − 12L + Asc | No | Al-Biruni 478 |
| 23 | Reputation | Jupiter − Sun + Asc | Yes | Valens II.36 |
| 24 | Knowledge | Sun − Saturn + Asc | Yes | Al-Biruni 478 |
| 25 | Honor | Sun − Saturn + Asc (alias of Knowledge — flagged) | Yes | Al-Biruni 478 |
| 26-50 | ... (additional Medieval Arabic Parts) | per Al-Biruni §467-510 | per citation | Al-Biruni |

Full list of 50 in `src/josi/data/western_lots.json`. We load them as DSL rules (F6) so astrologers can add custom Lots.

### 3.2 Fixed Stars

**Primary sources:**
- Ptolemy, *Tetrabiblos* Book I Ch. 9 (Robbins trans.) — foundational fixed-star nature-per-planet table.
- Anonymous of 379 CE, *On the Fixed Stars* (Greek; Greenbaum commentary) — star list with interpretations.
- Bernadette Brady, *Star and Planet Combinations* (2008) + *Brady's Book of Fixed Stars* (1998) — modern canonical treatment; paran methodology.
- Robson, Vivian E., *The Fixed Stars and Constellations in Astrology* (1923) — 180+ star catalog.

**60 ranked stars** (E8 ships):

Royal Stars (4): Regulus, Spica, Antares, Aldebaran.
Other major: Algol, Sirius, Fomalhaut, Arcturus, Procyon, Betelgeuse, Rigel, Vega, Altair, Deneb, Capella, Pollux, Castor, Alphard, Denebola, Zosma, Dubhe, Alkaid, Alcor, Mizar, Mirach, Alpheratz, Markab, Scheat, Algenib, Hamal, Menkar, Mira, Algol-family (Algol is specifically included), Mirfak, Pleiades-midpoint (Alcyone), Zuben-al-ghenubi, Zuben-al-schemali, Unukalhai, Ras Alhague, Ras Algethi, Acumen, Facies, Polis, Vindemiatrix, Spiculum, etc.

Full list with Swiss Ephemeris star codes in `src/josi/data/fixed_stars.json`.

**Computation:**
- `swe.fixstar_ut(star_name, t_jd)` returns `(lon, lat, dist, lon_speed)` in the chart's coordinate system.
- Tropical longitude for Western work (sidereal offset not applied).
- Conjunction with natal point: `|lon_star − lon_planet| < orb`, default orb 1.0° (Brady default; Robson uses 1°–2°; E8 allows 1.0° default, configurable).

**Parans** (Brady §3):
A paran is the condition where two celestial bodies cross the **angles** (rising ASC, culminating MC, setting DSC, anticulminating IC) at the same time but **not necessarily in the same geographic location**. The traditional test: given natal latitude φ, compute rising time of star S1 and rising/culminating/setting time of star S2 on the natal day; paran if times match within 15 minutes.

**Algorithm:**
1. For each pair (natal planet P, fixed star S):
2. At natal latitude, for natal date ± 1 day:
3. Compute when P crosses each of the four angles (ASC/MC/DSC/IC).
4. Compute when S crosses each of the four angles.
5. For each (angle_P, angle_S) combination (16 combos), check if |time_P − time_S| < 15 min.
6. If yes, paran exists; record (P, S, angle_P, angle_S, time_diff).

E8 computes parans for the ~60 stars × 10 natal points = 600 pair evaluations per chart. Cached.

### 3.3 Harmonic Charts

**Primary sources:**
- John Addey, *Harmonics in Astrology* (1976) — founding text; mathematical basis.
- Michael Harding, *Hymns to the Ancient Gods* (1992) — harmonic interpretation.
- David Hamblin, *Harmonic Charts* (1983) — practical interpretation.

**Formula** (Addey Ch. 2):
For harmonic number H, each planet's longitude λ is transformed:
```
λ_H = (λ × H) mod 360
```

Houses are conceptually re-cast from the transformed Ascendant; in practice, most harmonic-chart analysts keep natal houses ("harmonic positions in natal houses") — we offer both modes via `?include_houses=true` flag. Default: harmonic longitudes only (no re-cast houses).

**7 harmonics shipped:**

| H | Name | Interpretive focus | Citation |
|---|---|---|---|
| 5 | Talent / creativity | Artistic, athletic latent gifts | Addey Ch. 4 |
| 7 | Spiritual | Inspiration, mysticism | Addey Ch. 5 |
| 9 | Joy / marriage | Philosophically parallel to Navamsa | Addey Ch. 6; Harding Ch. 7 |
| 10 | Career fulfillment | Vocation, worldly completion | Hamblin Ch. 9 |
| 11 | Friendship / group | Collective energies | Addey Ch. 7 |
| 12 | Karmic / discipline | Sacrifice, karmic closure | Hamblin Ch. 10 |
| 16 | Tests / crises | Structural challenges | Harding Ch. 11 |

E8 emits harmonic charts as `structured_positions` with planet positions in `positions[]` and `details.harmonic_number = H`.

### 3.4 Eclipses

**Primary source:**
- NASA Five Millennium Canon of Solar Eclipses (−1999 to +3000) — Espenak & Meeus, 2006.
- NASA Five Millennium Canon of Lunar Eclipses — Espenak & Meeus, 2009.
- Ptolemy, *Tetrabiblos* II Ch. 4 — classical eclipse interpretation (mundane).
- Richard Tarnas, *Cosmos and Psyche* — modern archetypal eclipse interpretation.

**Data format:**
NASA catalog has one row per eclipse: (datetime_UTC, type, saros_cycle, saros_member, magnitude, gamma, lat_max, lon_max). We ship a subset: **200 years back, 50 years forward from current date**, rolling window regenerated at deploy.

Data file: `src/josi/data/nasa_eclipses.json` — JSON array, ~2000 entries, ~500 KB.

**Compute** (for a given natal chart):
1. For each eclipse in window:
2. Compute Sun longitude at eclipse moment (solar eclipse) OR Sun/Moon midpoint (lunar eclipse).
3. Check conjunction with each natal point within 3° orb.
4. Emit `temporal_event` with `event_type ∈ {'solar_eclipse_conj_natal_X', 'lunar_eclipse_conj_natal_X'}` and `details.saros_cycle`, `details.eclipse_type`.

**Saros cycle family:** each eclipse belongs to a 18-year-11-day Saros series. Family identification surfaces in `details.saros_series_name` (e.g., "Saros 145") — useful for eclipse-family interpretation (Tarnas).

### 3.5 Uranian / Hamburg School

**Primary sources:**
- Alfred Witte, *Rules for Planetary Pictures* (1928/1946, Hamburg School) — primary; midpoints and hypothetical planets.
- Ruth Brummund, *Uranian Systems* (1985).
- Michael Munkasey, *The Astrological Thesaurus* (1992) — midpoint interpretations.

**Midpoint (half-sum) formula:**
```
midpoint(A, B) = ((λ_A + λ_B) / 2) mod 360
# But: Uranian tradition uses the SHORTER arc midpoint
if |λ_A − λ_B| > 180:
    shift one side by 360 before averaging, then mod 360
```

For 10 classical planets + 3 angles (Asc, MC, Vertex), there are C(13, 2) = 78 unique midpoints. Plus 8 Uranian hypotheticals → expand to C(18, 2) = 153 if all are included.

E8 offers `?include_hypotheticals=false|true` — default false (traditional 10 planets + 3 angles only).

**Reflection point** (`reflection(A, axis B) = (2 × λ_B − λ_A) mod 360`): the point symmetric to A around axis B. Used in planetary pictures.

**Sum point** (`sum(A, B) = (λ_A + λ_B) mod 360`): less commonly used; included for Uranian-strict practitioners.

**Planetary pictures:** a Witte "planetary picture" is the condition where some natal planet N falls on the midpoint of two other planets A and B (orb 2°). Written as `N = A/B` in Uranian notation. E.g., `Sun = Moon/Jupiter` means Sun lies on the Moon-Jupiter midpoint axis.

**Algorithm:**
1. Compute all 78 (or 153) midpoints.
2. For each natal planet N:
3. For each midpoint M_{A,B}:
4. If |λ_N − λ_M| < 2°: record planetary picture (N, A, B, orb).

Per-chart picture count typically 15–40.

**Uranian hypotheticals** (Witte TNP table):
Cupido, Hades, Zeus, Kronos, Apollon, Admetos, Vulkanus, Poseidon — no astronomical basis; Witte's calculated positions based on patterns. Static table reproduced from Witte's *Rules for Planetary Pictures* Appendix.

We ship positions at 100-year resolution (Witte's granularity); interpolate linearly for arbitrary dates. Acknowledged as approximate; Witte's strict followers compute differently, but the linear interpolation matches Hamburg School software practice.

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| Which Lot formulas (Paulus vs Dorotheus vs Valens disagree) | Ship each as distinct source_id; Paulus = default | Honors each lineage; astrologer chooses |
| Sect determination | Use E1a existing (Sun house 7-12 = day; 1-6 = night) | Classical; already implemented |
| Reversing vs non-reversing Lots | Per-Lot flag in YAML | Varies; must be explicit per formula |
| Fixed-star orb default | 1.0° (Brady) | Standard modern orb; configurable |
| Parans latitude | Natal latitude | Classical Brady |
| Paran time tolerance | 15 minutes | Brady §3 |
| Harmonics house treatment | Optional (`include_houses` flag); default longitudes only | Matches majority practice; computable either way |
| Eclipse window | 200y back / 50y forward, rolling | Balance data volume + practical relevance |
| Eclipse orb | 3° for natal conjunction | Modern Western convention (Tarnas uses ~5°; we're stricter) |
| Midpoint arc direction | Shorter arc | Uranian standard |
| Uranian hypotheticals default | Excluded unless requested | Avoids confusing Western-traditional users |
| Uranian TNP interpolation | Linear at 100y granularity | Matches Hamburg School software |
| Parans in output shape | `structured_positions` with `details.type='paran'` | Avoids 11th shape |
| Storage of NASA data | Static JSON file regenerated at deploy | 500 KB; public domain |

## 5. Component Design

### 5.1 New modules

```
src/josi/services/classical/
├── western/
│   ├── __init__.py
│   ├── lots/
│   │   ├── __init__.py
│   │   ├── lot_calculator.py              # LotCalculator
│   │   └── sect.py                         # (uses E1a)
│   ├── fixed_stars/
│   │   ├── __init__.py
│   │   ├── star_calculator.py              # conjunctions
│   │   └── parans.py                       # paran detection
│   ├── harmonics/
│   │   ├── __init__.py
│   │   └── harmonic_calculator.py
│   ├── eclipses/
│   │   ├── __init__.py
│   │   ├── eclipse_loader.py               # loads NASA JSON
│   │   └── eclipse_matcher.py              # matches to natal
│   └── uranian/
│       ├── __init__.py
│       ├── midpoints.py
│       ├── pictures.py
│       └── hypothetical_tnp.py             # Witte TNP ephemeris

src/josi/data/
├── western_lots.json                       # 50 lots
├── fixed_stars.json                        # 60 stars with swe codes
├── nasa_eclipses.json                      # rolling 250y window
└── witte_tnp_table.json                    # hypothetical positions

src/josi/rules/
├── western/
│   ├── lots/
│   │   ├── paulus_alexandrinus/             # 7 Hermetic
│   │   ├── dorotheus/                        # Dorotheus variants + his Lots
│   │   ├── valens/
│   │   └── al_biruni/                        # medieval Arabic 43
│   ├── fixed_stars/
│   │   ├── ptolemy/                          # classical 15 stars
│   │   └── brady/                            # 60 with modern interp
│   ├── harmonics/
│   │   └── addey/
│   └── uranian/
│       └── witte_hamburg/

src/josi/api/v1/controllers/
└── western_depth_controller.py
```

### 5.2 Data model additions

No new tables. All compute lands in `technique_compute` with:
- `technique_family_id = 'western_lot'` (Lots)
- `technique_family_id = 'western_fixed_star'` (stars + parans)
- `technique_family_id = 'western_harmonic'` (harmonics)
- `technique_family_id = 'western_eclipse'` (eclipses)
- `technique_family_id = 'western_uranian'` (midpoints + pictures)

All five families seeded in F1.

Index:
```sql
CREATE INDEX idx_western_compute_family_chart
  ON technique_compute (technique_family_id, chart_id, computed_at DESC)
  WHERE technique_family_id LIKE 'western_%';
```

### 5.3 API contract

```
GET /api/v1/charts/{chart_id}/western/lots?tradition=hellenistic
Response: TechniqueResult[StructuredPositions] with 7 Hermetic Lots
    ?tradition=all returns 50

GET /api/v1/charts/{chart_id}/western/fixed-stars?orb=1.0&include_parans=true
Response: TechniqueResult[StructuredPositions] with natal conjunctions + parans in details

GET /api/v1/charts/{chart_id}/western/harmonics/9
Response: TechniqueResult[StructuredPositions] with H9 transformed positions
    Optional: ?include_houses=true

GET /api/v1/charts/{chart_id}/western/eclipses?from=2020-01-01&to=2030-01-01
Response: TechniqueResult[TemporalEvent] list; each eclipse with natal conjunctions

GET /api/v1/charts/{chart_id}/western/uranian?include_hypotheticals=false
Response: TechniqueResult[StructuredPositions] with midpoints + planetary pictures
```

### 5.4 Internal interfaces

```python
# src/josi/services/classical/western/lots/lot_calculator.py

class LotCalculator(ClassicalEngineBase):
    technique_family_id: str = "western_lot"
    default_output_shape_id: str = "structured_positions"

    async def compute_for_source(
        self, session, chart_id, source_id,
        rule_ids: list[str] | None = None,
    ) -> list[TechniqueComputeRow]:
        # Load lot YAMLs matching source_id
        # For each lot, apply day/night formula
        # Emit Position per lot
        ...

# src/josi/services/classical/western/fixed_stars/star_calculator.py

class FixedStarCalculator(ClassicalEngineBase):
    technique_family_id: str = "western_fixed_star"

    async def conjunctions(self, chart_id: UUID, orb_deg: float = 1.0) -> list[Conjunction]: ...
    async def parans(self, chart_id: UUID, time_tolerance_min: int = 15) -> list[Paran]: ...

# src/josi/services/classical/western/harmonics/harmonic_calculator.py

class HarmonicCalculator(ClassicalEngineBase):
    technique_family_id: str = "western_harmonic"

    async def compute_harmonic(self, chart_id: UUID, H: int,
                               include_houses: bool = False) -> StructuredPositions: ...

# src/josi/services/classical/western/eclipses/eclipse_matcher.py

class EclipseMatcher(ClassicalEngineBase):
    technique_family_id: str = "western_eclipse"

    async def eclipses_in_window(self, chart_id: UUID,
                                  from_dt: datetime, to_dt: datetime,
                                  orb_deg: float = 3.0) -> list[EclipseEvent]: ...

# src/josi/services/classical/western/uranian/pictures.py

class UranianEngine(ClassicalEngineBase):
    technique_family_id: str = "western_uranian"

    async def midpoints(self, chart_id: UUID, include_tnp: bool = False) -> dict[str, float]: ...
    async def planetary_pictures(self, chart_id: UUID, orb_deg: float = 2.0,
                                 include_tnp: bool = False) -> list[Picture]: ...
```

## 6. User Stories

### US-E8.1: As a Hellenistic astrologer, I can see all 7 Hermetic Lots sect-reversed correctly
**Acceptance:** night chart returns Fortune computed as `Sun − Moon + Asc`; day chart returns `Moon − Sun + Asc`. Positions match Chris Brennan's *Hellenistic Astrology* (2017) worked examples within 0.01°.

### US-E8.2: As a Brady-trained astrologer, I receive parans for my chart
**Acceptance:** `GET /api/v1/charts/{chart_id}/western/fixed-stars?include_parans=true` returns list of (planet, star, angle_planet, angle_star, time_diff_min) with time_diff < 15 min.

### US-E8.3: As a harmonics practitioner, I can request H9 (marriage harmonic)
**Acceptance:** all natal planet longitudes × 9 mod 360; aspects in H9 computed via existing aspect engine. Matches Hamblin's published example (1983) within 0.001°.

### US-E8.4: As a mundane astrologer, I can see eclipses conjunct my chart in the past decade
**Acceptance:** `GET /api/v1/charts/{chart_id}/western/eclipses?from=2015-01-01&to=2026-01-01` returns TemporalEvent list with Saros cycle identified.

### US-E8.5: As a Uranian astrologer, I can see all planetary pictures in my chart
**Acceptance:** `GET /api/v1/charts/{chart_id}/western/uranian` returns midpoint dict + list of pictures like `"Sun = Moon/Jupiter (orb 1.2°)"`.

### US-E8.6: As an AI chat surface, every Western-depth output validates against its F7 shape
**Acceptance:** every engine output passes `fastjsonschema.compile(shape_schema)(output)`.

### US-E8.7: As an astrologer, I can choose Paulus vs Dorotheus Lot definitions
**Acceptance:** `astrologer_source_preference.source_weights = {"paulus_alexandrinus": 1.0}` produces Paulus Lots; `{"dorotheus": 1.0}` produces Dorotheus variants where they differ (e.g., Lot of Marriage).

## 7. Tasks

### T-E8.1: Lot calculator + 50 Lot YAMLs
- **Definition:** `LotCalculator`; Lot formulas as DSL rules under `src/josi/rules/western/lots/`; sect-reversal flag per Lot.
- **Acceptance:** 50 Lots load; 7 Hermetic match Paulus exactly; 43 Arabic match Al-Biruni within 0.01°.
- **Effort:** 18 hours (data entry dominates)
- **Depends on:** F6, E1a sect determination

### T-E8.2: Fixed-star catalog + conjunction engine
- **Definition:** `fixed_stars.json` with 60 stars and swe codes; `star_calculator.py` uses `swe.fixstar_ut`; conjunction detection within configurable orb.
- **Acceptance:** 60 stars return non-null longitudes; 10 conjunction fixtures match Brady published examples.
- **Effort:** 12 hours

### T-E8.3: Paran engine
- **Definition:** `parans.py` iterating planet × star × angle combos at natal latitude; 15-min tolerance.
- **Acceptance:** 5-chart fixture against Brady *Fixed Stars* Ch. 7 parans list; all parans identified.
- **Effort:** 14 hours

### T-E8.4: Harmonic calculator
- **Definition:** `harmonic_calculator.py` applies λ × H mod 360 per planet; optional house recast.
- **Acceptance:** 7 harmonics × 3 fixtures = 21 test points match Hamblin within 0.001°.
- **Effort:** 6 hours

### T-E8.5: Eclipse data loader
- **Definition:** script to generate `nasa_eclipses.json` from NASA's canonical catalog (1806–2076 window); `eclipse_loader.py` at startup.
- **Acceptance:** ~2000 entries loaded; Saros cycle sanity (gaps of 18y+11d between same-saros members).
- **Effort:** 10 hours

### T-E8.6: Eclipse matcher
- **Definition:** `eclipse_matcher.py` matches eclipses to natal points within orb; emits TemporalEvent list.
- **Acceptance:** historical fixture (1999 total solar eclipse 11°08' Leo) conjunct a natal Leo planet: emitted correctly.
- **Effort:** 8 hours

### T-E8.7: Midpoint engine
- **Definition:** `midpoints.py` computes all pairwise midpoints (shorter arc); 78 base + 153 with TNP.
- **Acceptance:** hand-computed fixture across 0°/360° wrap boundary: correct shorter-arc result.
- **Effort:** 6 hours

### T-E8.8: Planetary pictures
- **Definition:** `pictures.py` finds N on midpoint A/B within 2° orb; emits structured picture list.
- **Acceptance:** known fixture (Uranian standard: Kennedy's chart has Sun = Mars/Saturn picture) identified.
- **Effort:** 8 hours

### T-E8.9: Uranian TNP table
- **Definition:** Witte hypothetical planet positions as static JSON; linear interpolation for arbitrary date.
- **Acceptance:** 100-year endpoints match published Witte positions; midpoint evaluation at 2020 returns interpolated value.
- **Effort:** 10 hours (data entry + interpolation)

### T-E8.10: Rule YAMLs
- **Definition:** Write lot rules (50), star-conjunction rule template (applies to all 60 stars), harmonic-transform rule (parametric), eclipse-match rule, midpoint rule. Full set under `src/josi/rules/western/`.
- **Acceptance:** All load via `poetry run validate-rules`.
- **Effort:** 14 hours

### T-E8.11: API controllers
- **Definition:** `western_depth_controller.py` implementing all listed endpoints.
- **Acceptance:** OpenAPI complete; integration tests for each endpoint.
- **Effort:** 10 hours

### T-E8.12: Golden fixtures
- **Definition:** 5 natal charts. Per chart: 7 Hermetic Lots; top 10 star conjunctions; parans list; H9 chart; eclipses in ±10y; Uranian pictures.
- **Acceptance:** all assertions green.
- **Effort:** 18 hours

### T-E8.13: Performance
- **Definition:** Benchmark: lots < 10 ms; stars + conjunctions < 100 ms; parans < 300 ms; harmonic < 20 ms; eclipses < 50 ms; uranian < 100 ms.
- **Acceptance:** pytest-benchmark under thresholds.
- **Effort:** 4 hours

### T-E8.14: Documentation
- **Definition:** CLAUDE.md: "Western-depth engines live under `src/josi/services/classical/western/`". Docs explain sect, Lots, parans.
- **Acceptance:** merged.
- **Effort:** 4 hours

## 8. Unit Tests

### 8.1 Lots

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_fortune_day_formula` | day chart, Sun 10° Moon 60° Asc 100° | Fortune = 60-10+100 = 150° | Paulus 23.1 |
| `test_fortune_night_reverses` | night chart, same | Fortune = 10-60+100 = 50° | sect reversal |
| `test_spirit_opposite_fortune_day` | day chart | Spirit = Sun-Moon+Asc; Fortune = Moon-Sun+Asc; they sum to 2*Asc (mod 360) | algebra |
| `test_eros_depends_on_spirit` | same | Eros formula uses computed Spirit | chained formulas |
| `test_all_50_lots_compute_non_null` | full fixture | 50 longitudes in [0,360) | completeness |
| `test_lot_sect_aware_difference` | day vs night, Fortune | different by 2*(Sun-Moon) | sect visible in diff |
| `test_lot_source_selection_paulus_vs_dorotheus_marriage` | men's Marriage | Paulus: Venus-Saturn+Asc; Dorotheus same per II.3 | source parity |
| `test_lot_exaltation_special_formula` | day | uses 19°Aries-Sun+Asc | Paulus 23.8 special case |
| `test_lot_activation_lord_aspects` | Fortune lord aspects year lord | lot marked active | activation rule |

### 8.2 Fixed stars

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_regulus_longitude_2026` | current | Regulus ≈ 0° Virgo tropical | precession verification |
| `test_algol_conjunction_1_deg` | natal Venus at 26° Taurus | Algol (26°08' Taurus) in conjunction within 1° | Brady fixture |
| `test_spica_conjunction_1_deg` | natal Moon at 24° Libra | Spica (23°50' Libra) conjunct | Royal Star check |
| `test_orb_configurable` | orb=2° | captures pairs at 1.5° distance | configurability |
| `test_60_stars_all_resolve` | all | 60 non-null longitudes | data integrity |

### 8.3 Parans

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_paran_same_angle_same_time` | Sun and Regulus both rising within 10 min at natal lat | paran identified | Brady §3 |
| `test_paran_different_angles` | Sun rising + Spica culminating within 15 min | paran identified | cross-angle |
| `test_paran_time_threshold_exceeded` | 20 min apart | NOT identified | threshold |
| `test_paran_brady_book_example` | Brady *Fixed Stars* Ch.7 published chart | identified parans match list | classical canonical |
| `test_paran_count_reasonable` | typical chart | 5-25 parans (not hundreds; not zero) | sanity |

### 8.4 Harmonics

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_h5_longitude_math` | planet at 72° | H5 = 72*5 mod 360 = 0° | basic |
| `test_h9_wraps_correctly` | planet at 40° | H9 = 40*9 mod 360 = 0° | wrap |
| `test_h7_hamblin_example` | Hamblin ch. published chart | H7 positions match | classical |
| `test_harmonic_aspects_preserved_under_transform` | exact natal trine | still trine in H1 | identity |
| `test_h12_conjunction_natal_square` | natal square (90°) | H12: 90*12=1080 mod 360=0 → conjunction | expected semantic |

### 8.5 Eclipses

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_eclipse_catalog_loads` | app startup | ~2000 entries loaded | data infra |
| `test_solar_eclipse_1999_08_11_data` | catalog | exact (datetime, saros 145) | catalog fidelity |
| `test_eclipse_conj_natal_within_orb` | natal Sun 18° Leo, 1999-08-11 eclipse 18°21' Leo | match within 3° | matching |
| `test_eclipse_outside_window_excluded` | query 1500 CE | empty result | window bounds |
| `test_saros_family_identified` | 2024-04-08 eclipse | saros 139 | NASA fidelity |

### 8.6 Uranian

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_midpoint_simple` | A=10°, B=50° | 30° | arithmetic |
| `test_midpoint_shorter_arc_wrap` | A=350°, B=10° | 0° (not 180°) | shorter-arc invariant |
| `test_reflection_point` | A=30°, B=60° | reflection = 90° | 2B-A math |
| `test_picture_identification_within_orb` | N at midpoint ± 1.5° | picture emitted with orb 1.5° | identification |
| `test_picture_excluded_beyond_orb` | N at midpoint + 3° | NOT identified | orb boundary |
| `test_tnp_interpolation_midpoint` | date between 2000 and 2100 TNP positions | linearly interpolated | interpolation |
| `test_uranian_no_tnp_default` | default request | 78 midpoints, no TNPs | default config |
| `test_uranian_with_tnp` | include_hypotheticals=true | 153 midpoints | expansion |

### 8.7 Integration

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_western_lot_output_validates_structured_positions` | output | passes F7 schema | parity |
| `test_western_fixed_star_output_validates` | output | passes F7 schema | parity |
| `test_western_harmonic_output_validates` | output | passes F7 schema | parity |
| `test_western_eclipse_output_validates_temporal_event` | output | passes F7 temporal_event | parity |
| `test_western_uranian_output_validates` | output | passes F7 schema | parity |
| `test_all_western_engines_idempotent` | 5 families × 2 calls | 5 technique_compute rows; 10 aggregation_event rows | F2 contract |

## 9. EPIC-Level Acceptance Criteria

- [ ] 50 Arabic Parts / Lots implemented with sect-aware formulas; 7 Hermetic match Paulus exactly
- [ ] 60 fixed stars with Swiss Ephemeris-based positions; conjunction engine with configurable orb
- [ ] Paran engine detects rising/culminating/setting co-angular events within 15-min tolerance at natal latitude
- [ ] 7 harmonics (H5, H7, H9, H10, H11, H12, H16) implemented as λ×H mod 360 transforms
- [ ] NASA eclipse catalog (200y past + 50y future rolling window) loaded; eclipses matched to natal within 3° orb
- [ ] Saros cycle identification for every eclipse event
- [ ] Midpoint engine with shorter-arc convention; 78 midpoints (default) or 153 with TNPs
- [ ] Planetary pictures within 2° orb emitted as structured records
- [ ] Uranian hypothetical planet positions (Witte table) with linear interpolation
- [ ] All outputs conform to F7 `structured_positions` or `temporal_event` schemas
- [ ] API endpoints live for all 5 subdomains; documented in OpenAPI
- [ ] Golden chart suite: 5 charts × 5 subdomains × ~10 assertions = ~250 assertions green
- [ ] Rule YAMLs under `src/josi/rules/western/` for Paulus, Dorotheus, Valens, Al-Biruni, Ptolemy, Brady, Addey, Witte
- [ ] Unit test coverage ≥ 90% across `western/` package
- [ ] Integration tests hit full path (compute → persist → aggregate → API read) for all 5 families
- [ ] Performance per §7 T-E8.13 under budget
- [ ] CLAUDE.md updated with Western-depth section
- [ ] Sect reversal correctness validated with 2 day-night pairs

## 10. Rollout Plan

- **Feature flags:** `enable_western_lots`, `enable_fixed_stars`, `enable_harmonics`, `enable_eclipses`, `enable_uranian` — five independent flags. Default off until QA.
- **Shadow compute:** 2-week shadow on Lots and fixed stars (compare outputs to Astro-Databank / Solar Fire published examples); harmonics/eclipses/uranian ship with direct testing.
- **Backfill:** lazy (compute on first request); eclipses precomputed at deploy for all active users' charts during off-peak (low-cost: just natal-to-eclipse matching).
- **Rollback:** disable feature flags; endpoints return 501; redeploy old code.

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Lot sect reversal incorrectly applied to non-reversing Lots | High | High | Per-Lot explicit `reverses` flag in YAML; unit tests every day/night pair |
| Fixed-star Swiss Ephemeris star name mismatch | Medium | Medium | Use canonical swe codes; validate via swe_fixstar_nut |
| Paran time window (15 min) disputed | Low | Low | Configurable; 15 min per Brady default |
| Harmonic house recast inconsistent across practitioners | Medium | Low | Default longitudes only; optional recast behind flag |
| NASA catalog file size growth | Low | Low | Rolling 250y window; JSON ~500 KB; consider binary format if >5 MB |
| Eclipse orb disputed (3° vs 5°) | Medium | Low | Configurable; document default |
| Midpoint shorter-arc bug at 180° boundary | Medium | High | Explicit test at 0°-180° and 180°-360° |
| Uranian TNP linear interpolation too crude | Low | Low | Document approximation; strict Uranian practitioners have own software |
| Data file tampering invalidates hashes | Low | Medium | Cover static JSON files by content-hash; warn if modified post-deploy |
| Lot data entry errors (50 Lots × formulas) | High | Medium | Cross-reference against Holden's *Classical Astrology*; review PR with classical advisor |
| Al-Biruni medieval vs Hellenistic Lot formula drift | Medium | Medium | Each gets own source_id; YAML cites verse |

## 12. References

- Master spec: [`docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`](../../../superpowers/specs/2026-04-19-classical-techniques-expansion-design.md) §2.2 (western_lot, western_fixed_star, western_harmonic, western_eclipse, western_uranian in technique_families)
- F1 dims: [`../P0/F1-star-schema-dimensions.md`](../P0/F1-star-schema-dimensions.md) — add `dorotheus`, `paulus_alexandrinus`, `valens`, `ptolemy`, `brady`, `addey`, `witte_hamburg`
- F2 fact tables: [`../P0/F2-fact-tables.md`](../P0/F2-fact-tables.md)
- F6 Rule DSL: [`../P0/F6-rule-dsl-yaml-loader.md`](../P0/F6-rule-dsl-yaml-loader.md)
- F7 Output shapes: [`../P0/F7-output-shape-system.md`](../P0/F7-output-shape-system.md) §5.3.5 (temporal_event), §5.3.7 (structured_positions)
- F8 Aggregation: [`../P0/F8-technique-result-aggregation-protocol.md`](../P0/F8-technique-result-aggregation-protocol.md)
- E1a Multi-Dasa v1 — sect determination primitive
- **Classical sources (Lots):**
  - Dorotheus of Sidon, *Carmen Astrologicum* — Pingree ed. 1976; Books I-V
  - Paulus Alexandrinus, *Introductory Matters* — Greenbaum trans., 2001; Ch. 23
  - Vettius Valens, *Anthology* — Riley trans.; Books II-IV
  - Al-Biruni, *Elements of Astrology* — Wright trans., 1934; §467-510 (Arabic Parts)
  - Robert Hand, *Night & Day: Planetary Sect in Astrology*, 1995 — sect rules
  - Chris Brennan, *Hellenistic Astrology*, 2017 — modern codification
- **Classical sources (Fixed Stars):**
  - Ptolemy, *Tetrabiblos* — Robbins trans., Loeb 1940; Book I Ch. 9
  - Anonymous of 379 CE, *On the Fixed Stars* — Greenbaum commentary
  - Vivian E. Robson, *The Fixed Stars and Constellations in Astrology*, 1923
  - Bernadette Brady, *Brady's Book of Fixed Stars*, 1998
  - Bernadette Brady, *Star and Planet Combinations*, 2008 — parans
- **Classical sources (Harmonics):**
  - John Addey, *Harmonics in Astrology*, 1976
  - Michael Harding, *Hymns to the Ancient Gods*, 1992
  - David Hamblin, *Harmonic Charts*, 1983
- **Classical sources (Eclipses):**
  - F. Espenak & J. Meeus, *Five Millennium Canon of Solar Eclipses (−1999 to +3000)*, NASA/TP-2006-214141
  - F. Espenak & J. Meeus, *Five Millennium Canon of Lunar Eclipses*, NASA/TP-2009-214172
  - Richard Tarnas, *Cosmos and Psyche*, 2006
- **Classical sources (Uranian):**
  - Alfred Witte, *Rules for Planetary Pictures*, 1928/1946 — Hamburg School
  - Ruth Brummund, *Uranian Systems*, 1985
  - Michael Munkasey, *The Astrological Thesaurus*, 1992 — midpoint interpretations
- **Reference implementations:**
  - Solar Fire (commercial) — fixed stars, harmonics, Arabic parts, midpoints
  - Astro.com (Swiss Ephemeris) — fixed stars
  - Cosmic Patterns Kepler — Uranian and harmonics
