---
prd_id: E1a
epic_id: E1
title: "Multi-Dasa Engine v1 (Yogini + Ashtottari)"
phase: P1-mvp
tags: [#correctness, #extensibility]
priority: must
depends_on: [F1, F2, F4, F6, F7, F8, F13, F16, F17]
enables: [E1b, E11a, E4a, E14a]
classical_sources: [bphs, jataka_parijata, saravali]
estimated_effort: 2.5 weeks
status: approved
author: @agent-claude-opus-4-7
last_updated: 2026-04-21
---

# E1a — Multi-Dasa Engine v1 (Yogini + Ashtottari)

## 1. Purpose & Rationale

Josi today computes only **Vimshottari Dasa** (120-year cycle, Moon-nakshatra-anchored), implemented in `src/josi/services/dasa_calculator.py`. This single-system approach is a correctness gap for two reasons:

1. **Classical practitioners rarely use Vimshottari alone.** Parashari tradition prescribes at least three systems to be cross-read for timing: Vimshottari (primary), Ashtottari (Moon in krishna paksha, per BPHS Ch. 47), and Yogini (for short-term transitional windows, per BPHS Ch. 48). A reading that names "your current dasa" as just Vimshottari is incomplete.
2. **Astrologer marketplace requires multi-system.** Pro-mode astrologers will filter candidate Josi astrologers by what systems they practice; if Josi only outputs Vimshottari, the marketplace API is narrower than the tradition it serves.

This PRD adds the two shortest-to-correct-classically dasa systems beyond Vimshottari:

- **Yogini Dasa** (BPHS Ch. 48): 8 mahadashas, total 36 years. Anchored to Moon's nakshatra. Ships as always-applicable (short enough to fully cycle ~3× per lifetime).
- **Ashtottari Dasa** (BPHS Ch. 47): 8 mahadashas, total 108 years. Anchored to Moon's nakshatra. Ships with a configurable activation predicate (Moon in krishna paksha — classical restriction) vs universal application (some schools).

Both systems share structure: nakshatra-based starting dasha, proportional antardashas and pratyantardashas (3 levels), same JSONB output shape (`temporal_hierarchy`) as Vimshottari, and the same `ClassicalEngine` Protocol from F8.

Implementation expectation: engine matches Jagannatha Hora 7.x (JH) period boundaries within ±1 day across a golden suite of 10 charts.

## 2. Scope

### 2.1 In scope

- Two new dasa engines: **Yogini** and **Ashtottari**, each implementing the `ClassicalEngine` Protocol.
- Rule YAML files per F6 DSL with full activation + calculation specified declaratively.
- Content-hashed rule registry entries in `classical_rule` table (via F6 loader).
- 3-level temporal hierarchy output (mahadasha → antardasha → pratyantardasa) conforming to `temporal_hierarchy` shape.
- Classical source citations embedded in rule YAML (`citation`, `classical_names`).
- Golden chart fixtures: 10 known charts with expected dasa periods verified against JH.
- Unit tests per rule; integration test for full compute path (rule → compute → aggregation → API).
- REST endpoint surfaces extended: `GET /api/v1/dasha/{chart_id}?system={vimshottari|yogini|ashtottari}`.
- AI tool-use extension: `get_current_dasa(chart_id, system, level)` supports new systems.

### 2.2 Out of scope

- **Chara Dasa, Narayana Dasa, Kalachakra Dasa** — deferred to E1b (P2).
- **Sub-sub-sub levels** (4-deep: sookshma, prana) — deferred to E1b; v1 stops at pratyantardasa.
- **Dasa-bhukti-antar transit overlays** — deferred to E6a/E6b.
- **Yogini Dasa fractional-day edge-case divergences** between Saravali and BPHS variants — v1 uses BPHS Ch. 48; cross-source variants deferred to P2.
- **Phalita (prediction) interpretation layer** — covered separately in E11a.

### 2.3 Dependencies

- F1 (source_authority has `bphs`, `jataka_parijata`, `saravali` seeded).
- F2 (classical_rule, technique_compute tables exist).
- F4 (rule versioning — `effective_from`/`effective_to`, `content_hash`).
- F6 (YAML rule loader populates `classical_rule`).
- F7 (`temporal_hierarchy` JSON Schema defined).
- F8 (`ClassicalEngine` Protocol + aggregation strategies available).
- F13 (content-hash provenance chain).
- F16 (golden chart suite scaffolding — adds fixtures for dasa tests).
- F17 (property-based test harness — enforces invariants: sum of periods = system cycle, no gaps, no overlaps).

## 2.4 Design Decisions (Pass 1 Astrologer Review — Locked 2026-04-21)

All open questions from E1a Pass 1 astrologer review are resolved. Cross-cutting decisions reference `DECISIONS.md`; E1a-specific decisions documented here.

### Cross-cutting decisions (applied via `DECISIONS.md`)

| Decision | Value | Ref |
|---|---|---|
| Ayanamsa default | Lahiri (Chitrapaksha Official) for B2C; 9-shortlist for astrologer profile (Lahiri, Raman, Krishnamurti, True Chithirai, Yukteshwar, J.N. Bhasin, Suryasiddhantha, True Poosam, Fagan-Bradley) | DECISIONS 1.2 |
| Ashtottari eligibility | Permissive default (always compute); astrologer can toggle BPHS strict via F2 `astrologer_source_preference` | DECISIONS 1.6 |
| Dasai hierarchy depth | 5 levels (MD → AD → PD → Sookshma → Prana) for both user types | DECISIONS 1.4 |
| Rahu/Ketu node type | Both Mean Node + True Node computed always; B2C default True Node; astrologer prompted | DECISIONS 1.1 |
| Natchathiram count | 27 for everything (including dasai starting-lord mapping); SBC exception only (28 in SBC) | DECISIONS 3.7 |
| Language display | Sanskrit-IAST canonical + Tamil phonetic for UI; entity names use Tamil phonetic primary | DECISIONS 1.5 |

### E1a-specific decisions (locked this review)

| Decision | Value | Source |
|---|---|---|
| Yogini starting-natchathiram lookup | BPHS Ch.48 table only (27-row mapping in §3.1); no Saravali variant | Pass 1 Q3 |
| Ashtottari starting-lord algorithm | Continuous longitude-based: `cumulative_years = moon_sidereal_long / 360 × 108` — matches JH 7.x exactly | Pass 1 Q4 |
| Paksham method (strict-mode Ashtottari only) | Tithi-based lookup reused from panchangam layer; zero recomputation | Pass 1 Q7 |
| Natchathiram-boundary edge case | Boundary-inclusive lower (`floor(moon_long / 13°20') + 1`); silent (no warning) | Pass 1 Q8 |
| Matching bar vs JH 7.x | ±1 day across 10-chart golden suite | Pass 1 Q9 |
| Dasai balance rendering | Y/M/D/H/M classical breakdown for both user types; internal float for arithmetic | Pass 1 Q10 |
| Timezone for dasai boundary dates | Birthplace timezone with historical awareness via `pytz` (handles pre-1947 Madras Time LMT variations, pre-DST-change transitions, Indian IST fixed +5:30 post-1947) | Pass 1 Q11 |

### Implementation implications

1. **Dual-node computation** per chart → both Mean Node and True Node stored with discriminator. Starting-lord selection uses Chandran's natchathiram (independent of node type). Period lengths unchanged; only active-moment Rahu position differs between node types.
2. **5-level depth computation** → extend proportional formula naturally: `sookshma = antardasa × sookshma_lord_years / cycle_total`; `prana = sookshma × prana_lord_years / cycle_total`. For Yogini, `cycle_total = 36`; Ashtottari `= 108`; Vimshottari `= 120`.
3. **Historical timezone awareness** → use `pytz` (not fixed UTC offset) for rendering dasai boundary dates. Pre-1947 Indian births use Madras Time LMT; post-1947 use IST (+5:30 fixed). Western births need full DST transition history.
4. **Tithi dependency** → dasai engine strict-mode Ashtottari check reads tithi from panchangam layer output. Engine-ordering constraint: panchangam computes before dasai engine.

### Engineering action items (not astrologer-review scope)

- [ ] Extend existing `dasa_calculator.py` Vimshottari to compute 5 levels (currently ships 3); behavior-preserving refactor alongside new Yogini/Ashtottari engines.
- [ ] Implement dual Mean + True node computation at chart creation; store both with discriminator.
- [ ] Add `pytz`-based historical timezone rendering to dasai boundary date output layer.
- [ ] Golden chart suite: 10 charts × 3 dasai systems × 5 levels, cross-verified against JH 7.x at ±1 day.
- [ ] Rule YAMLs for both Yogini and Ashtottari encode classical variants as sibling rules; permissive/BPHS-strict Ashtottari selected via `effective_from`.
- [ ] Engineering decision on Vimshottari refactor risk (behavior-preserving refactor vs duplicate base logic vs feature-flag gate) — out of astrologer review scope, engineering team owns.

---

## 3. Classical / Technical Research

### 3.1 Yogini Dasa — BPHS Chapter 48

**Source:** Brihat Parashara Hora Shastra, Chapter 48 (*Yogini Dasa adhyaya*). Variant references in Jataka Parijata Ch. 18.

**System:**
- 8 mahadashas (yoginis) with years summing to 36: 1+2+3+4+5+6+7+8 = 36.
- Cycle repeats; a 90-year-old person has experienced 2.5 full cycles.

| # | Yogini (Sanskrit) | Planetary lord | Years |
|---|---|---|---|
| 1 | Mangala | Moon | 1 |
| 2 | Pingala | Sun | 2 |
| 3 | Dhanya | Jupiter | 3 |
| 4 | Bhramari | Mars | 4 |
| 5 | Bhadrika | Mercury | 5 |
| 6 | Ulka | Saturn | 6 |
| 7 | Siddha | Venus | 7 |
| 8 | Sankata | Rahu | 8 |

**Starting yogini determined by Moon's nakshatra at birth** (BPHS 48.4–6). Offset: `(nakshatra_number) mod 8`, with mapping starting from Ashwini→Sankata (the "tail" yogini):

| Nakshatra # | Name | Starting Yogini |
|---|---|---|
| 1 | Ashwini | Sankata |
| 2 | Bharani | Mangala |
| 3 | Krittika | Pingala |
| 4 | Rohini | Dhanya |
| 5 | Mrigashira | Bhramari |
| 6 | Ardra | Bhadrika |
| 7 | Punarvasu | Ulka |
| 8 | Pushya | Siddha |
| 9 | Ashlesha | Sankata |
| 10 | Magha | Mangala |
| 11 | P. Phalguni | Pingala |
| 12 | U. Phalguni | Dhanya |
| 13 | Hasta | Bhramari |
| 14 | Chitra | Bhadrika |
| 15 | Swati | Ulka |
| 16 | Vishakha | Siddha |
| 17 | Anuradha | Sankata |
| 18 | Jyeshtha | Mangala |
| 19 | Mula | Pingala |
| 20 | P. Ashadha | Dhanya |
| 21 | U. Ashadha | Bhramari |
| 22 | Shravana | Bhadrika |
| 23 | Dhanishta | Ulka |
| 24 | Shatabhisha | Siddha |
| 25 | P. Bhadrapada | Sankata |
| 26 | U. Bhadrapada | Mangala |
| 27 | Revati | Pingala |

Computationally: `starting_yogini_index = ((nakshatra_number - 1) mod 8) + 1` if we re-index (Sankata=1, Mangala=2, …) — **but the classical pattern is offset by Sankata being 8**. Implementation form: use an explicit lookup table (the 27-row table above); do not derive by arithmetic — variants exist in Saravali and mistakes propagate.

**Balance calculation (BPHS 48.7–8):**

The proportion of the starting nakshatra already traversed at birth is also the proportion of the starting yogini already elapsed. Formula:

```
elapsed_fraction = (moon_longitude_in_nakshatra) / (nakshatra_span_degrees)
                 = (moon_longitude mod 13°20') / 13°20'
balance_of_starting_yogini = starting_yogini_years × (1 - elapsed_fraction)
```

The first mahadasha runs from birth for `balance_of_starting_yogini` years; subsequent mahadashas run full duration in sequence.

**Antardasha subdivision (BPHS 48.9):**

Within each mahadasha, the 8 yoginis appear again in cyclic order starting from the current lord, with periods in ratio to their mahadasha durations:

```
antardasha_duration(yogini_A, inside_mahadasha_of_Y)
  = (Y_mahadasha_duration × A_mahadasha_duration) / 36
```

Example: within the Bhramari (4-year) mahadasha, antardashas are:
- Bhramari: 4 × 4 / 36 = 0.444 yr
- Bhadrika: 4 × 5 / 36 = 0.556 yr
- Ulka: 4 × 6 / 36 = 0.667 yr
- Siddha: 4 × 7 / 36 = 0.778 yr
- Sankata: 4 × 8 / 36 = 0.889 yr
- Mangala: 4 × 1 / 36 = 0.111 yr
- Pingala: 4 × 2 / 36 = 0.222 yr
- Dhanya: 4 × 3 / 36 = 0.333 yr

Sum = 4.000 yr ✓

**Pratyantardasha subdivision:** same ratio principle, nested one level deeper:

```
pratyantar_duration(C, inside_antar_A, inside_mahadasha_Y)
  = (antardasha_duration(A, Y) × C_mahadasha_duration) / 36
```

### 3.2 Ashtottari Dasa — BPHS Chapter 47

**Source:** BPHS Ch. 47 (*Ashtottari Dasa adhyaya*); also referenced in Jataka Parijata 18.

**System:**
- 8 mahadashas totaling 108 years.

| # | Lord | Years |
|---|---|---|
| 1 | Sun | 6 |
| 2 | Moon | 15 |
| 3 | Mars | 8 |
| 4 | Mercury | 17 |
| 5 | Saturn | 10 |
| 6 | Jupiter | 19 |
| 7 | Rahu | 12 |
| 8 | Venus | 21 |

Sum = 108 ✓

**Starting dasha by Moon's nakshatra (BPHS 47.4–7):**

Grouped into 8 clusters of 3+ nakshatras each. Classical verse enumerates:

| Starting Lord | Nakshatras |
|---|---|
| Sun | Krittika, Rohini, Mrigashira (partial), Ardra (partial) |
| Moon | remaining Ardra, Punarvasu, Pushya, Ashlesha (partial) |
| Mars | remaining Ashlesha, Magha, P. Phalguni, U. Phalguni (partial) |
| Mercury | remaining U. Phalguni, Hasta, Chitra, Swati (partial) |
| Saturn | remaining Swati, Vishakha, Anuradha, Jyeshtha (partial) |
| Jupiter | remaining Jyeshtha, Mula, P. Ashadha, U. Ashadha (partial) |
| Rahu | remaining U. Ashadha, Shravana, Dhanishta, Shatabhisha (partial) |
| Venus | remaining Shatabhisha, P. Bhadrapada, U. Bhadrapada, Revati, Ashwini (partial), Bharani (partial), Krittika (partial — loops) |

The classical computation is in **aayanamsa-adjusted sidereal longitude**: the 108-year cycle maps to 360° such that each year covers 360°/108 = 3.333°. Moon's sidereal longitude determines entry point. Implementation (canonical algorithm per JH and Saravali confirmations):

```
longitude_fraction = moon_sidereal_longitude / 360.0
cumulative_years = longitude_fraction × 108

# Walk the dasha sequence to find which dasha cumulative_years falls into:
running_total = 0
for (lord, years) in DASHA_SEQUENCE:
    if cumulative_years < running_total + years:
        starting_lord = lord
        elapsed_in_starting = cumulative_years - running_total
        balance = years - elapsed_in_starting
        break
    running_total += years
```

**Activation predicate (classical rule — divergent schools):**

Two classical positions exist:

- **Strict school (BPHS 47.2):** Ashtottari applies *only* when Moon is in **krishna paksha** (waning phase) **and** Lagna is occupied or aspected by a benefic **and** night birth. Some commentators add "when Rahu is not in Lagna."
- **Permissive school (Jataka Parijata + modern JH default):** Ashtottari applies universally; the classical restriction is treated as a lineage preference, not a bar.

**Josi default: permissive** (always compute). Rationale: (a) aligns with JH 7.x default, enabling differential testing; (b) B2C users expect the period to be shown without lineage-specific gating; (c) astrologer pro-mode can set a per-astrologer preference (via F2's `astrologer_source_preference`) to filter to strict activation. The rule YAML encodes both variants; the default is chosen via `effective_from` on the permissive variant.

**Antardasha / Pratyantardasa:** same proportional formula as Yogini (`parent × child / 108`).

### 3.3 Engine architecture

Each system is an instance of a shared `DasaEngine` base class conforming to the `ClassicalEngine` Protocol (F8):

```
BaseDasaEngine (shared)
  ├─ nakshatra_lookup() → starting lord + balance
  ├─ build_mahadasha_sequence(birth_dt) → List[TemporalRange]
  ├─ build_antardasha(mahadasha) → List[TemporalRange]
  ├─ build_pratyantar(antardasha) → List[TemporalRange]
  └─ emit TemporalHierarchyResult (3 levels)

YoginiDasaEngine(BaseDasaEngine)
  – cycle_years = 36
  – sequence = [('mangala',1,'moon'), ...]
  – nakshatra → lord via BPHS Ch.48 lookup

AshtottariDasaEngine(BaseDasaEngine)
  – cycle_years = 108
  – sequence = [('sun',6), ('moon',15), ...]
  – starting lord via sidereal-longitude bucket
  – activation predicate: moon_paksha_check (see 3.2)
```

Existing Vimshottari in `dasa_calculator.py` will be refactored in T-E1a.7 to share `BaseDasaEngine` — behavior-preserving.

### 3.4 Rule YAML shape (F6 DSL)

**`src/josi/db/rules/dasa/yogini_bphs.yaml`**:

```yaml
rule_id: dasa.yogini.bphs
source_id: bphs
version: "1.0.0"
technique_family_id: dasa
output_shape_id: temporal_hierarchy
citation: "BPHS Ch.48 v.1-9"
classical_names:
  en: "Yogini Dasa"
  sa_iast: "Yoginī Daśā"
  sa_devanagari: "योगिनी दशा"
  ta: "யோகினி தசை"
effective_from: "2026-01-01T00:00:00Z"
effective_to: null

activation:
  predicate:
    op: always_true            # Yogini always applies

compute:
  engine: yogini_dasa
  cycle_years: 36
  sequence:
    - { yogini: mangala, lord: moon,    years: 1 }
    - { yogini: pingala, lord: sun,     years: 2 }
    - { yogini: dhanya,  lord: jupiter, years: 3 }
    - { yogini: bhramari, lord: mars,   years: 4 }
    - { yogini: bhadrika, lord: mercury, years: 5 }
    - { yogini: ulka,    lord: saturn,  years: 6 }
    - { yogini: siddha,  lord: venus,   years: 7 }
    - { yogini: sankata, lord: rahu,    years: 8 }
  nakshatra_to_starting_yogini:
    1: sankata      # Ashwini
    2: mangala      # Bharani
    3: pingala      # Krittika
    4: dhanya       # Rohini
    5: bhramari     # Mrigashira
    6: bhadrika     # Ardra
    7: ulka         # Punarvasu
    8: siddha       # Pushya
    9: sankata      # Ashlesha
    10: mangala     # Magha
    11: pingala     # P.Phalguni
    12: dhanya      # U.Phalguni
    13: bhramari    # Hasta
    14: bhadrika    # Chitra
    15: ulka        # Swati
    16: siddha      # Vishakha
    17: sankata     # Anuradha
    18: mangala     # Jyeshtha
    19: pingala     # Mula
    20: dhanya      # P.Ashadha
    21: bhramari    # U.Ashadha
    22: bhadrika    # Shravana
    23: ulka        # Dhanishta
    24: siddha      # Shatabhisha
    25: sankata     # P.Bhadrapada
    26: mangala     # U.Bhadrapada
    27: pingala     # Revati
  levels: 3                  # mahadasha, antardasha, pratyantar
  balance_formula: proportional_to_nakshatra_remainder
  subdivision_formula: "parent_years * child_years / cycle_years"
```

**`src/josi/db/rules/dasa/ashtottari_bphs.yaml`**:

```yaml
rule_id: dasa.ashtottari.bphs
source_id: bphs
version: "1.0.0"
technique_family_id: dasa
output_shape_id: temporal_hierarchy
citation: "BPHS Ch.47 v.1-8"
classical_names:
  en: "Ashtottari Dasa"
  sa_iast: "Aṣṭottarī Daśā"
  sa_devanagari: "अष्टोत्तरी दशा"
  ta: "அஷ்டோத்தரி தசை"
effective_from: "2026-01-01T00:00:00Z"
effective_to: null

activation:
  predicate:
    op: always_true            # Josi default: permissive school

compute:
  engine: ashtottari_dasa
  cycle_years: 108
  sequence:
    - { lord: sun,     years: 6 }
    - { lord: moon,    years: 15 }
    - { lord: mars,    years: 8 }
    - { lord: mercury, years: 17 }
    - { lord: saturn,  years: 10 }
    - { lord: jupiter, years: 19 }
    - { lord: rahu,    years: 12 }
    - { lord: venus,   years: 21 }
  starting_dasha:
    method: sidereal_longitude_bucket
    cumulative_years_formula: "(moon_sidereal_longitude / 360.0) * 108"
  levels: 3
  subdivision_formula: "parent_years * child_years / cycle_years"
```

**`src/josi/db/rules/dasa/ashtottari_strict_bphs.yaml`** (variant, same `rule_id`, different `source_id` not appropriate since both are BPHS; instead use a sibling rule_id):

```yaml
rule_id: dasa.ashtottari.strict.bphs
source_id: bphs
version: "1.0.0"
technique_family_id: dasa
output_shape_id: temporal_hierarchy
citation: "BPHS Ch.47 v.2 (strict school)"
classical_names:
  en: "Ashtottari Dasa (strict paksha-gated)"
effective_from: "2026-01-01T00:00:00Z"
effective_to: null

activation:
  predicate:
    op: all_of
    clauses:
      - { op: moon_in_paksha, paksha: krishna }
      # Optionally: { op: benefic_in_or_aspecting_lagna }
      # Optionally: { op: birth_at_night }

compute:
  engine: ashtottari_dasa
  # (compute block identical to permissive version — reuse via YAML anchor in final authored file)
```

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| Apply Ashtottari universally or only per krishna-paksha restriction? | **Both**: ship permissive as default, strict as alternate rule | Matches JH default for differential testing; astrologer pro-mode can override |
| Levels: 2 (MD-AD) or 3 (MD-AD-PD)? | 3 | Three is classical minimum cited in BPHS 48.9; UI can collapse to 2 visually |
| Store computed periods in DB or compute on-demand? | Compute on write, cache in `technique_compute` via `ClassicalEngine` | Keeps AI tool-use P50 < 20 ms |
| Yogini: which nakshatra-to-yogini mapping (mod 8 formulas differ across texts)? | Explicit 27-row table from BPHS Ch.48 verse | Verses specify explicitly; arithmetic derivation is where modern tools most often err |
| Refactor existing Vimshottari dasa into shared base? | Yes, in T-E1a.7, behavior-preserving | Enables single AggregationStrategy code path for multi-system cross-reads |
| What if Moon's longitude is on a nakshatra boundary (discrete ambiguity)? | Tiebreak: round-down (assign to earlier nakshatra) + property test asserts continuity | Standard convention; Hypothesis test catches regressions |
| Cross-source reconciliation when BPHS and Saravali differ on Yogini ordering? | Ship BPHS only in v1; Saravali variant deferred to P2 | Scope control; classical precedence is BPHS |

## 5. Component Design

### 5.1 New modules

```
src/josi/services/classical/dasa/
├── __init__.py
├── base_dasa_engine.py         # BaseDasaEngine (shared skeleton)
├── yogini_engine.py            # YoginiDasaEngine
├── ashtottari_engine.py        # AshtottariDasaEngine
└── vimshottari_engine.py       # refactor of existing dasa_calculator (behavior-preserving)

src/josi/db/rules/dasa/
├── vimshottari_bphs.yaml
├── yogini_bphs.yaml
├── ashtottari_bphs.yaml
└── ashtottari_strict_bphs.yaml

src/josi/schemas/classical/dasa/
└── temporal_hierarchy_schemas.py   # Pydantic models for output

tests/golden/charts/dasa/
├── chart_01_expected_yogini.yaml
├── chart_01_expected_ashtottari.yaml
├── ... (10 charts)
```

### 5.2 Data model additions

No new tables. Two new rows in `classical_rule` (inserted by F6 loader from the two YAML files). Output rows flow into `technique_compute` with existing schema.

### 5.3 Engine interface

```python
# src/josi/services/classical/dasa/base_dasa_engine.py

from typing import Protocol
from datetime import datetime
from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession


class DasaPeriod(BaseModel):
    lord: str                     # e.g. "jupiter", "mangala" (yogini name)
    level: int                    # 1=mahadasha, 2=antardasha, 3=pratyantar
    start: datetime
    end: datetime
    children: list["DasaPeriod"] = Field(default_factory=list)


class TemporalHierarchyResult(BaseModel):
    root_system: str              # "vimshottari" | "yogini" | "ashtottari"
    periods: list[DasaPeriod]     # root-level (mahadashas), each with nested children


class BaseDasaEngine:
    technique_family_id = "dasa"
    cycle_years: float
    sequence: list[tuple[str, int]]     # (lord, years)

    async def compute_for_source(
        self,
        session: AsyncSession,
        chart_id: UUID,
        source_id: str,
        rule_ids: list[str] | None = None,
    ) -> list[TechniqueComputeRow]: ...

    def _find_starting(self, moon_longitude: float, birth_dt: datetime) -> tuple[str, float]:
        """Returns (starting_lord, balance_years). Overridden per system."""
        raise NotImplementedError

    def _build_mahadasha_sequence(
        self, starting_lord: str, balance_years: float, birth_dt: datetime
    ) -> list[DasaPeriod]: ...

    def _build_antardasha(self, mahadasha: DasaPeriod) -> list[DasaPeriod]: ...

    def _build_pratyantar(self, antardasha: DasaPeriod) -> list[DasaPeriod]: ...
```

### 5.4 REST API contract

```
GET /api/v1/dasha/{chart_id}?system=yogini
GET /api/v1/dasha/{chart_id}?system=ashtottari
GET /api/v1/dasha/{chart_id}?system=vimshottari    # existing, unchanged shape

Response (200):
{
  "success": true,
  "message": "Dasa computed",
  "data": {
    "system": "yogini",
    "rule_id": "dasa.yogini.bphs",
    "source_id": "bphs",
    "rule_version": "1.0.0",
    "citation": "BPHS Ch.48 v.1-9",
    "root_system": "yogini",
    "periods": [
      {
        "lord": "dhanya",
        "planet_lord": "jupiter",
        "level": 1,
        "start": "1987-03-15T00:00:00Z",
        "end": "1989-08-20T00:00:00Z",
        "children": [
          { "lord": "dhanya", "level": 2, "start": "...", "end": "...", "children": [...] },
          ...
        ]
      },
      ...
    ]
  },
  "errors": null
}
```

Query parameters:
- `system` (required): `vimshottari` | `yogini` | `ashtottari`
- `levels` (optional, default 3): 1 | 2 | 3
- `from_date`, `to_date` (optional): filter hierarchy to overlapping periods
- `source` (optional, default `bphs`): source of rule to apply

### 5.5 AI tool-use extension (F10)

```python
@tool
def get_current_dasa(
    chart_id: str,
    system: Literal["vimshottari", "yogini", "ashtottari"] = "vimshottari",
    level: int = 2,                    # 1=MD only; 2=MD+AD; 3=MD+AD+PD
    at_date: date | None = None,       # default: today
) -> DasaPeriod:
    """Returns the dasa period(s) active at `at_date` (default today) for the named system,
       drilling down to `level` nesting depth. Response includes citation."""
    ...
```

## 6. User Stories

### US-E1a.1: As an end user, I want to see my current Yogini dasa alongside Vimshottari
**Acceptance:** Dashboard dasa widget shows both systems stacked; both pull from the same F9 `chart_reading_view.current_dasas` JSONB with systems keyed by name.

### US-E1a.2: As an astrologer, I want to pick which dasa systems to show for my client reading
**Acceptance:** Pro-mode UI reads `astrologer_source_preference` with `technique_family_id = 'dasa'`, `source_weights = {"bphs": 1.0}`, `preferred_strategy_id` set; rendered chart shows only selected systems.

### US-E1a.3: As an engineer, I want to verify Yogini periods against Jagannatha Hora
**Acceptance:** `tests/golden/charts/dasa/chart_01_expected_yogini.yaml` contains 10 MD boundaries verified manually against JH 7.x. Golden-suite test passes within ±1 day tolerance.

### US-E1a.4: As a classical advisor, I want to adjust the Ashtottari activation rule without a code change
**Acceptance:** Editing `activation.predicate` in `ashtottari_strict_bphs.yaml`, merging the PR, and redeploying causes the strict rule to become active; old compute rows retain old rule version via `classical_rule.effective_to` timestamp.

### US-E1a.5: As an AI agent calling `get_current_dasa(chart, system='ashtottari', level=3)`, I receive a nested 3-deep hierarchy with citation
**Acceptance:** Response is `DasaPeriod` tree depth 3; citation `"BPHS Ch.47 v.1-8"` embedded; confidence 1.0 (single-source).

## 7. Tasks

### T-E1a.1: Author rule YAML files
- **Definition:** Write `yogini_bphs.yaml`, `ashtottari_bphs.yaml`, `ashtottari_strict_bphs.yaml` per Section 3.4. Include all 27-row nakshatra lookup for Yogini. Validate against F6 DSL schema.
- **Acceptance:** F6 loader parses all three; inserts 3 rows into `classical_rule`; content_hash stable on re-load.
- **Effort:** 1 day
- **Depends on:** F6 complete

### T-E1a.2: Build `BaseDasaEngine` base class
- **Definition:** Shared skeleton with `_find_starting`, `_build_mahadasha_sequence`, `_build_antardasha`, `_build_pratyantar`, and `compute_for_source` implementing the `ClassicalEngine` Protocol. Emits `technique_compute` rows via idempotent upsert.
- **Acceptance:** Protocol conformance verified; unit tests for subdivision arithmetic (sum invariants) pass.
- **Effort:** 2 days
- **Depends on:** F8

### T-E1a.3: Implement `YoginiDasaEngine`
- **Definition:** Subclass of `BaseDasaEngine`. Overrides `_find_starting` using explicit 27-row lookup. Cycle=36, sequence per Section 3.1.
- **Acceptance:** Unit tests: `(nakshatra=1, moon_lon_in_naksh=0%) → Sankata, balance=8.0 years`; `(nakshatra=27, moon_lon_in_naksh=50%) → Pingala, balance=1.0 year`; sum-of-periods invariant holds for 1000 random moon longitudes.
- **Effort:** 1.5 days
- **Depends on:** T-E1a.2

### T-E1a.4: Implement `AshtottariDasaEngine`
- **Definition:** Subclass of `BaseDasaEngine`. Overrides `_find_starting` using sidereal-longitude bucket (Section 3.2). Cycle=108. Activation predicate evaluation for strict variant.
- **Acceptance:** Unit tests: canonical test cases match JH 7.x output for 5 sample longitudes; strict variant gated by paksha predicate.
- **Effort:** 1.5 days
- **Depends on:** T-E1a.2

### T-E1a.5: Author golden chart fixtures
- **Definition:** 10 birth charts with birth data, Moon longitude, and expected Yogini + Ashtottari mahadasha boundaries to ±1 day (verified manually against JH 7.x). YAML format consumable by F16 golden suite.
- **Acceptance:** Fixtures parse; expected values cross-checked by classical advisor review.
- **Effort:** 2 days (includes manual JH verification)
- **Depends on:** F16

### T-E1a.6: Golden + property tests
- **Definition:** Golden-suite test asserts computed mahadasha boundaries match fixtures ±1 day. Property tests: for N random moon longitudes, (a) sum of mahadashas = cycle_years, (b) no gaps, (c) no overlaps, (d) monotonic time, (e) re-computing is idempotent.
- **Acceptance:** Tests pass in CI; property tests with 1000 examples pass.
- **Effort:** 1 day
- **Depends on:** T-E1a.3, T-E1a.4, T-E1a.5, F17

### T-E1a.7: Refactor existing Vimshottari to share `BaseDasaEngine`
- **Definition:** Move `src/josi/services/dasa_calculator.py` logic into `VimshottariDasaEngine(BaseDasaEngine)`. Keep public surface; internal restructure only. Old tests still pass.
- **Acceptance:** All existing dasa tests green; diff is additive or neutral; no change to existing API response shapes.
- **Effort:** 1.5 days
- **Depends on:** T-E1a.2

### T-E1a.8: REST endpoint + controller wiring
- **Definition:** Extend `GET /api/v1/dasha/{chart_id}` to accept `?system=yogini|ashtottari`. Controller delegates to appropriate engine.
- **Acceptance:** Curl tests for all 3 systems return valid responses; 4xx for unknown `system`.
- **Effort:** 0.5 day
- **Depends on:** T-E1a.3, T-E1a.4

### T-E1a.9: AI tool-use extension
- **Definition:** Update `get_current_dasa` tool (F10) to accept `system` param; update prompt docs.
- **Acceptance:** Tool schema validates; integration test invoking chat tool with `system='yogini'` returns correct period.
- **Effort:** 0.5 day
- **Depends on:** T-E1a.8

### T-E1a.10: Integration test (full path)
- **Definition:** Test creates chart, triggers compute, verifies rule+compute rows in DB, queries via REST and GraphQL, and asserts AI tool returns correct period.
- **Acceptance:** Full round-trip passes in CI.
- **Effort:** 0.5 day
- **Depends on:** T-E1a.6, T-E1a.8, T-E1a.9

## 8. Unit Tests

### 8.1 Yogini — starting yogini lookup

| Test name | Input (nakshatra, moon_lon_in_naksh_deg) | Expected (starting_yogini, balance_yr) | Rationale |
|---|---|---|---|
| `test_yogini_ashwini_start` | (1, 0.0) | (sankata, 8.0) | Canonical: Ashwini→Sankata; 0% traversed → full 8y balance |
| `test_yogini_ashwini_mid` | (1, 6.667) | (sankata, 4.0) | 50% traversed → half balance |
| `test_yogini_bharani_end` | (2, 13.333) | (mangala, ~0.0) | End of nakshatra → ~0 balance, next yogini about to start |
| `test_yogini_revati_start` | (27, 0.0) | (pingala, 2.0) | Revati→Pingala; BPHS mapping |
| `test_yogini_mula_mid` | (19, 6.667) | (pingala, 1.0) | Mula→Pingala, 50% remaining of 2y |
| `test_yogini_invariant_balance_le_full` | 1000 random inputs | balance ≤ starting_yogini_years always | invariant |

### 8.2 Yogini — sequence arithmetic

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_yogini_md_sum_eq_cycle` | any start + full sequence | sum of 8 MD durations = 36 yr | Sum invariant |
| `test_yogini_antardasha_sum_eq_parent` | Bhramari (4y) MD | sum of 8 antar durations = 4.0 yr | Subdivision formula |
| `test_yogini_pratyantar_sum_eq_parent` | any AD | sum of 8 PD durations = AD duration | Recursive invariant |
| `test_yogini_period_order_preserved` | starting=bhramari | next MD is bhadrika, then ulka, ..., wraps at sankata→mangala→dhanya | Ordering |
| `test_yogini_no_overlap_or_gap` | 10 charts, full 36-yr hierarchy | end[i] == start[i+1] (modulo float tolerance) | Temporal consistency |

### 8.3 Ashtottari — starting lord lookup

| Test name | Input (moon_sidereal_lon_deg) | Expected (lord, balance_yr) | Rationale |
|---|---|---|---|
| `test_ashtottari_lon_0` | 0.0 | (sun, 6.0) | Sidereal 0° → start of cycle, full Sun |
| `test_ashtottari_lon_20` | 20.0 | (sun, 0.0) | Sun exhausted at cumulative_years=6 → lon=360*6/108=20° |
| `test_ashtottari_lon_25` | 25.0 | (moon, ~13.5) | 25° → cumulative=7.5y → Moon (next), balance=15-1.5=13.5 |
| `test_ashtottari_lon_358` | 358.0 | (venus, ~0.67) | Near end of cycle |
| `test_ashtottari_balance_le_full` | 1000 random lons | balance ≤ lord_years always | Invariant |

### 8.4 Ashtottari — activation

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_ashtottari_permissive_always_active` | any chart | active=true | Default permissive |
| `test_ashtottari_strict_krishna_paksha_active` | chart with Moon in krishna paksha | strict variant active | BPHS 47.2 |
| `test_ashtottari_strict_shukla_paksha_inactive` | chart with Moon in shukla paksha | strict variant inactive | BPHS 47.2 |

### 8.5 Ashtottari — arithmetic

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_ashtottari_md_sum_eq_108` | full sequence | 108.0 | Sum invariant |
| `test_ashtottari_antardasha_sum` | Jupiter (19y) MD | sum of 8 antar durations = 19.0 | Subdivision |
| `test_ashtottari_pratyantar_sum` | any AD | sum of 8 PD = AD duration | Recursive |

### 8.6 Rule registry integration

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_rule_loaded_from_yaml` | Run F6 loader | 3 new rows in `classical_rule` | YAML wiring |
| `test_rule_content_hash_stable` | Load twice | same content_hash | Determinism |
| `test_compute_row_written_idempotently` | Run compute twice | 1 row in `technique_compute` | Idempotency via ON CONFLICT |
| `test_compute_references_rule_version` | Inspect compute row | `rule_version='1.0.0'` | Version-lock |

### 8.7 Golden suite (Jagannatha Hora differential)

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_golden_chart_01_yogini` | `tests/golden/charts/dasa/chart_01.yaml` | All MD boundaries match JH ±1 day | Correctness vs reference |
| ... (×10 charts per system) | | | |
| `test_golden_chart_01_ashtottari` | same | All MD boundaries match JH ±1 day | |

### 8.8 Property tests (Hypothesis, F17)

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_yogini_hierarchy_total_duration_invariant` | random (lat, lon, tz, dt, moon_lon) | sum of 8 MDs = 36y; sum of 8 ADs inside each MD = MD duration; sum of 8 PDs inside each AD = AD duration | Arithmetic invariant |
| `test_ashtottari_monotonic_time` | random | for all adjacent periods, end[i] ≤ start[i+1] | Temporal |
| `test_recompute_deterministic` | same inputs | same `output_hash` | Content-hash determinism |
| `test_period_covers_entire_cycle_from_birth` | random birth_dt | earliest period starts at birth_dt; latest period ends at birth_dt + cycle_years × N cycles | Coverage |

## 9. EPIC-Level Acceptance Criteria

- [ ] Yogini + Ashtottari YAML rules loaded into `classical_rule` table via F6 loader
- [ ] `YoginiDasaEngine` and `AshtottariDasaEngine` implement `ClassicalEngine` Protocol
- [ ] Existing Vimshottari refactored to share `BaseDasaEngine`; no behavior regression
- [ ] REST endpoint `GET /api/v1/dasha/{chart_id}?system=...` returns all three systems
- [ ] AI tool `get_current_dasa(system=...)` works end-to-end
- [ ] Golden suite: 10 charts × 2 new systems (20 fixtures) all pass ±1 day vs JH 7.x
- [ ] Property tests pass with ≥1000 Hypothesis examples per system
- [ ] Unit test coverage ≥ 90% for all new code
- [ ] `chart_reading_view.current_dasas` JSONB shape documented and populated for new systems
- [ ] Documentation updated: `CLAUDE.md` notes three dasa systems available; user-facing docs show examples
- [ ] Performance: compute for a single chart for one system completes in < 50 ms P99

## 10. Rollout Plan

- **Feature flag:** `ENABLE_DASA_YOGINI`, `ENABLE_DASA_ASHTOTTARI` (both default `true` on P1 deploy; removable in P2 once stable).
- **Shadow compute:** on staging, run computations for 1000 existing charts; spot-check 10 against JH 7.x manually before promoting to prod.
- **Backfill strategy:** opportunistic — compute on next chart view. A background job (`compute_missing_dasas`) can seed over 2 weeks.
- **Rollback plan:** flip flag off → endpoint returns 404 for new systems; existing Vimshottari unaffected. `effective_to = now()` on new rules soft-deprecates them without data loss.

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Yogini nakshatra→yogini mapping mis-encoded | Medium | High | 27-row explicit lookup (not arithmetic); classical-advisor PR review on YAML |
| Ashtottari sidereal-longitude bucket off-by-one at boundaries | Medium | High | Property test: for lon=k × (360/108), starting changes exactly at boundary |
| Float precision drift over 3 nested levels → period boundary drift | Low | Medium | Use `Decimal` for duration arithmetic; convert to `datetime` only at emission |
| BPHS activation-predicate ambiguity (strict Ashtottari) disputed by lineage | Medium | Low | Ship both rules side-by-side; astrologer preference decides |
| Vimshottari refactor introduces regression | Medium | High | Behavior-preserving refactor; old test suite must pass unchanged before T-E1a.7 merges |
| `technique_compute` row count grows fast (3 systems × chart × rule) | Low | Low | F3 partitioning handles it; row size bounded (JSONB depth ≤ 3 levels × 8 × 8 × 8 = 512 periods max) |
| Krishna-paksha predicate depends on astronomical Moon/Sun longitudes; existing chart data must expose them | Low | Medium | Verify `AstrologyChart` schema exposes `moon.sign_longitude`, `sun.sign_longitude`; paksha derived from difference |

## 12. References

- Master spec: [`docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`](../../../superpowers/specs/2026-04-19-classical-techniques-expansion-design.md)
- F1 dimensions: [`../P0/F1-star-schema-dimensions.md`](../P0/F1-star-schema-dimensions.md)
- F2 fact tables: [`../P0/F2-fact-tables.md`](../P0/F2-fact-tables.md)
- F6 rule DSL: [`../P0/F6-rule-dsl-yaml-loader.md`](../P0/F6-rule-dsl-yaml-loader.md)
- F8 engine protocol: [`../P0/F8-technique-result-aggregation-protocol.md`](../P0/F8-technique-result-aggregation-protocol.md)
- Existing Vimshottari: `src/josi/services/dasa_calculator.py`
- Classical primary sources:
  - Brihat Parashara Hora Shastra, Ch. 47 (Ashtottari Dasa), Ch. 48 (Yogini Dasa)
  - Jataka Parijata, Ch. 18 (dasa cross-references)
  - Saravali (supplementary, deferred to P2 for variant rules)
- Reference implementation: Jagannatha Hora 7.x (free download, VedicAstrology.com)
