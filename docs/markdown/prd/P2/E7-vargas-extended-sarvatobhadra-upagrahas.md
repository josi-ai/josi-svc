---
prd_id: E7
epic_id: E7
title: "Extended Vargas (D61–D144), Sarvatobhadra Chakra, Upagrahas"
phase: P2-breadth
tags: [#correctness, #extensibility, #astrologer-ux]
priority: should
depends_on: [F1, F2, F6, F7, F8, E1a]
enables: [E14a, P2-UI-vargas]
classical_sources: [bphs, uttara_kalamrita, jaimini_sutras, kerala_commentaries, saravali]
estimated_effort: 3-4 weeks
status: draft
author: "@agent"
last_updated: 2026-04-22
---

# E7 — Extended Vargas (D61–D144), Sarvatobhadra Chakra, Upagrahas

## 1. Purpose & Rationale

Josi's existing `DivisionalChartsCalculator` covers the standard 16 Shodashavargas (D1–D60 excluding D61+). Classical Parashari literature, Uttara Kalamrita, and Jaimini sources collectively reference at least seven additional divisional charts above D60 — and three specific classical instruments are systematically *absent* from most commercial software: the full Upagraha (sub-planet) set beyond Gulika/Mandi, and the Sarvatobhadra Chakra (SBC) — the 9×9 grid used for muhurta, prasna, and omen analysis across North Indian and Kerala practice.

This PRD closes those gaps:

1. **Extended Vargas D61–D144** — Akshavedamsa (D45, already in D-series), Shashtiamsa (D60, already present), Ashtottari Amsa (D108 = D12 × D9), Dwadashottari (D72), Chaturashittiyamsa (D84 — "ashta-dashamsa" family), Shatamsa (D100 — rare; mentioned in UK), Dwadashamsa sub-variants, and D144 ("Nadi Amsa extended" — used by some Nadi systems). Specify exact division algorithm per varga.
2. **Sarvatobhadra Chakra (SBC)** — 9×9 grid encoding 28 nakshatras (incl. Abhijit), 12 rashis, 8 weekdays, vowels, and tithi categories. Used to evaluate fitness of names, moments, letters. Critical for muhurta selection, horary (prasna), and daily-choice consulting.
3. **Upagrahas (sub-planets)** — beyond already-implemented Gulika/Mandi, add Dhuma, Vyatipata (Pata), Parivesha, Chapa, Upaketu, Kala, Yamakantaka, Ardhaprahara. Two computation schools (Kerala vs North Indian) differ markedly — we support both as distinct `source_id`.

These additions bring Josi to parity with Jagannatha Hora on the "full classical instrument inventory" axis and unlock dedicated UIs (P2-UI-vargas) and downstream EPICs (E10 uses SBC for Prasna omen analysis; E14a uses them in aggregation experiments).

## 2. Scope

### 2.1 In scope

- **Extended Vargas** (seven new charts):
  - D72 — Dwadashottari
  - D84 — Chaturashittiyamsa
  - D100 — Shatamsa
  - D108 — Ashtottari Amsa (composite of D12 × D9)
  - D144 — Nadi Amsa Extended
  - Plus two less-cited but canonical: D150 (Nadi Amsa strict) and D300 (deferred — out of scope; documented)
- Per-varga algorithmic specification with citations.
- **Sarvatobhadra Chakra** construction:
  - 9×9 grid with 28 nakshatras (incl. Abhijit), 12 rashis, 8 directions × compass letters, weekdays, tithis, vowels
  - Grid rendering emit suitable for UI consumption (structured_positions with nested grid in `details`)
  - Auspiciousness query: given (natal Moon nakshatra, current Moon nakshatra, query letter) → fitness score
- **Upagrahas** — 8 new sub-planets (6 per Kerala school, 8 per North Indian; support both):
  - Dhuma, Vyatipata, Parivesha, Chapa (Indrachapa), Upaketu — computed from Sun (day-duration fractions)
  - Kala, Mrityu, Ardhaprahara, Yamakantaka — computed from day/night duration fractions (North Indian school)
  - Per-school algorithms documented and implemented as separate `source_id` values
- **Output shape emission**: `structured_positions` for upagrahas and extended varga positions; `structured_positions` with nested `details.grid` for SBC
- **Rule/predicate definitions**: extended-varga rules registered under `source_id='bphs'` + `source_id='uttara_kalamrita'`; SBC rules register for muhurta/prasna use; upagrahas split into `kerala_upagraha` and `north_indian_upagraha` source variants
- **API surface**:
  - `GET /api/v1/charts/{chart_id}/vargas/extended` → all extended-varga positions
  - `GET /api/v1/charts/{chart_id}/sarvatobhadra` → SBC grid + active cells for this chart
  - `POST /api/v1/charts/{chart_id}/sarvatobhadra/query` with `{letter|nakshatra|weekday}` → fitness score
  - `GET /api/v1/charts/{chart_id}/upagrahas?school={kerala|north_indian}` → 8 upagraha positions

### 2.2 Out of scope

- **D300 (Ardha-Nadi Amsa)** — only rarely cited in Nadi astrology; divisions of 0.1° are beyond practical accuracy of natal birth times; documented but not implemented.
- **Vedha analysis on SBC** — "vedha" is the blocking-aspect analysis on the SBC grid; non-trivial classical predicate system; deferred to E7b.
- **Astrocartography / locational astrology** — different infrastructure.
- **Nadi-reading text lookups** — Nadi palm-leaf readings use the extended vargas; integrating Nadi text lookups is a P5+ content partnership problem, not calculation.
- **D-chart strength computation beyond D30** — Shadvarga / Saptavarga / Shodashavarga strength tables already exist; extending those scores to D60+ follows naturally from compute but is tracked in separate PRD (E2b).

### 2.3 Dependencies

- F1 — `source_id` additions: `kerala_upagraha`, `north_indian_upagraha`, `uttara_kalamrita`
- F2 — fact tables
- F6 — DSL loader for rule YAMLs
- F7 — `structured_positions` shape (suitable for upagraha + SBC)
- F8 — aggregation protocol
- E1a — natal ascendant, planet positions, sunrise/sunset (for day-fraction upagrahas)
- Existing `DivisionalChartsCalculator` — extended here
- Existing `AstrologyCalculator` — for sunrise/sunset/tithi

## 2.4 Design Decisions (Pass 1 Astrologer Review — Locked 2026-04-22)

All open questions from E7 Pass 1 astrologer review are resolved. Cross-cutting decisions reference `DECISIONS.md`; GAP_CLOSURE Sphuta extension applied. E7-specific decisions documented here.

### Cross-cutting decisions

| Decision | Value | Ref |
|---|---|---|
| Ayanamsa | Lahiri | DECISIONS 1.2 |
| Rahu/Ketu node type | Both Mean + True | DECISIONS 1.1 |
| Natchathiram count | 27 for all general use; **28 for SBC only** (scoped exception) | DECISIONS 3.7 |
| Language display | Sanskrit-IAST + Tamil phonetic | DECISIONS 1.5 |
| Varga purpose metadata | BPHS Ch.6 canonical strings | DECISIONS 1.9/1.10 |
| 5 Sphutas in E7 scope | Per GAP_CLOSURE §1.B extension | GAP_CLOSURE |

### E7-specific decisions (locked this review)

| Decision | Value | Source |
|---|---|---|
| **Extended Varga division algorithms** (Q1) | **BPHS Ch.6 + Uttara Kalamrita Ch.2 synthesis** for D72 Dwadashottari, D84 Chaturashittiyamsa, D100 Shatamsa, D108 Ashtottari Amsa, D144 Nadi Amsa Extended. Matches JH + PL + Astrosage. | Q1 |
| **Sarvathobhadra Chakra (SBC) layout** (Q2) | **BPHS Ch.86 standard 9×9 grid** — 28 natchathirams (incl. Abhijit), 12 rasis, 8 weekdays, directions, letters, vowels, tithis. Matches JH + PL + Astrosage + Tamil Vakya. Same for both user types. | Q2 |
| **Upagrahas school default** (Q3) | **North Indian school default** (8 upagrahas: Dhuma, Vyatipata, Parivesha, Chapa/Indrachapa, Upaketu, Kala, Yamakantaka, Ardhaprahara) + **Kerala school (6 upagrahas) as astrologer-profile toggle**. Matches JH + Tamil Vakya default + uniform variant convention. | Q3 |
| **5 Sphutas classical source** (Q4) | **BPHS Ch.79-80 + UK Ch.2 synthesis** for all 5 Sphutas (Beeja, Kshetra, Deha, Mrityu, Pranapada). Modern standard. Matches JH + PL + Astrosage + Tamil Vakya. **Ethical gating:** Mrityu Sphuta astrologer-workbench-only (same convention as E5b Ayus); B2C AI chat declines Mrityu-specific queries. | Q4 |
| **SBC query API scope** (Q5) | **4 query types shipped:** (1) name-testing / varna fitness, (2) natchathiram compatibility, (3) weekday fitness for activity, (4) travel/direction auspiciousness. **Type 5 muhurta date-range search deferred** to E7-enhancement PRD. Matches JH scope. Same for both user types. | Q5 |
| **Cross-source aggregation for E7** (Q6) | **Variant-toggle pattern extended to all E7 techniques.** Extended Vargas: BPHS+UK default + Kerala Parahita variant (D84/D108 toggle). SBC: BPHS Ch.86 only (no variant — classical grid deterministic). Upagrahas: North Indian default + Kerala school toggle (already in Q3). Sphutas: BPHS+UK default + Phaladeepika/Kerala Prashnashastra variant toggle. Uniform with E1b/E3/E5/E5b. | Q6 |

### E7 engine output shapes

```python
extended_vargas = {
    "D72_dwadashottari": {planet: sign_position},
    "D84_chaturashittiyamsa": {planet: sign_position},
    "D100_shatamsa": {planet: sign_position},
    "D108_ashtottari_amsa": {planet: sign_position},
    "D144_nadi_amsa_extended": {planet: sign_position},
    "source": Literal["bphs_uk", "kerala_parahita"]  # D84/D108 variant
}

sarvathobhadra_chakra = {
    "grid_9x9": nested_grid_structure,
    "active_cells_for_chart": list[CellReference],
    "source": "bphs_ch86"
}

upagrahas = {
    "school": Literal["north_indian", "kerala"],  # 8 or 6 positions
    "positions": {name: longitude}
}

sphutas = {
    "beeja": float,        # longitude
    "kshetra": float,
    "deha": float,
    "mrityu": float,       # astrologer-workbench-only
    "pranapada": float,
    "source": Literal["bphs_uk", "phaladeepika", "kerala_prashnashastra"]
}
```

### Engineering action items (not astrologer-review scope)

- [ ] Extended Varga computation module (5 algorithms per BPHS+UK)
- [ ] Kerala Parahita variant for D84/D108 as sibling rules; astrologer toggle
- [ ] SBC 9×9 grid static data + query engine (4 query types per Q5)
- [ ] Upagraha North Indian + Kerala computation modules; astrologer school toggle via F2
- [ ] 5 Sphuta formulas per BPHS+UK + Phaladeepika/Kerala variant siblings
- [ ] Mrityu Sphuta role-gated API (astrologer-only; 403 for B2C)
- [ ] REST endpoints: `/api/v1/charts/{id}/vargas/extended`, `/api/v1/charts/{id}/sarvathobhadra`, `/api/v1/charts/{id}/upagrahas?school=...`, `/api/v1/charts/{id}/sphutas`
- [ ] SBC query endpoints: `POST /api/v1/sarvathobhadra/query` with `{query_type, params}` for name/compat/weekday/direction queries

---

## 3. Classical Research

Abbreviations used:
- **BPHS** = *Brihat Parashara Hora Shastra*, Santhanam trans., Ranjan Publications
- **UK** = *Uttara Kalamrita* by Kalidasa, G.K. Ojha trans., Motilal Banarsidas
- **JS** = *Jaimini Upadesha Sutras*, Sanjay Rath trans.
- **BrihatSBC** = *Muhurta Martanda* + Kerala commentaries on Sarvatobhadra Chakra

### 3.1 Extended Vargas — Division Algorithms

**General principle:** a D-N chart divides each 30° sign into N equal parts, each part assigned to a sign per a rule specific to N.

#### 3.1.1 D72 — Dwadashottari (UK Ch. 4 v. 3-5)

Each sign has 72 parts of 30°/72 = 25' each. "Dwadashottari" = 12 + (cycles of 72). Assignment rule:

```
For planet at longitude λ in sign S (1..12), degree-in-sign δ (0..30):
part_index = floor(δ / (30/72))          # 0..71
d72_sign = ((S - 1) * 72 + part_index) mod 12 + 1
```

Citation: UK Ch. 4 v. 3-5 attributes this to Nadi tradition; BPHS Ch. 7 v. 32 references the name but gives no worked example. We use UK's cycle-12 assignment.

#### 3.1.2 D84 — Chaturashittiyamsa (UK Ch. 4 v. 6-8)

84 parts of 30°/84 ≈ 21.43' each. Used for longevity refinement in some Nadi schools.

```
part_index = floor(δ / (30/84))           # 0..83
d84_sign = ((S - 1) * 84 + part_index) mod 12 + 1
```

#### 3.1.3 D100 — Shatamsa (UK Ch. 4 v. 9-11)

100 parts of 18' each. Classically referenced as "Nadi Amsa" but distinct from D150 Nadi.

```
part_index = floor(δ / (30/100))          # 0..99
d100_sign = ((S - 1) * 100 + part_index) mod 12 + 1
```

#### 3.1.4 D108 — Ashtottari Amsa (BPHS Ch. 7 v. 34 commentary + UK)

D108 is conceptually D12 × D9 — used classically for Ashtottari Dasha analysis. Two variants exist in commentaries:

**Variant A (composite):** compute D12 sign → further divide that sign into 9 navamsa parts → the D108 sign is the navamsa-of-dwadashamsa.
```
d12_sign = dwadashamsa(λ)
offset_in_d12 = (λ - sign_start(S)) mod (30/12)
navamsa_within_d12 = floor(offset_in_d12 / ((30/12)/9))
d108_sign_composite = navamsa_sign_of(d12_sign, navamsa_within_d12)
```

**Variant B (direct 108 parts):** divide each sign into 108 direct parts.
```
part_index = floor(δ / (30/108))
d108_sign_direct = ((S - 1) * 108 + part_index) mod 12 + 1
```

BPHS is silent on which is canonical. UK Ch. 4 v. 12 favors Variant A ("composite"). Commentaries by B.V. Raman favor Variant B. **E7 ships both as distinct `source_id` variants**:
- `source_id = 'bphs'` → Variant A (composite)
- `source_id = 'uttara_kalamrita'` → Variant A (matches BPHS, per UK's explicit statement)
- `source_id = 'raman_commentary'` → Variant B

Astrologer picks via source preference (F1/F2 astrologer_source_preference).

#### 3.1.5 D144 — Nadi Amsa Extended (UK Ch. 4 v. 13)

Used by certain Nadi schools. 144 parts per sign.
```
part_index = floor(δ / (30/144))          # 0..143
d144_sign = ((S - 1) * 144 + part_index) mod 12 + 1
```

#### 3.1.6 D150 — Nadi Amsa (strict) (UK Ch. 4 v. 14-16)

Classical Nadi Amsa — 150 parts per sign × 12 = 1800 total (matches 1800 nadi amsas of the zodiac). Assignment is **NOT cyclic in the simple sense**; UK v. 15 specifies a movable/fixed/dual rotation pattern per sign, with each of the 1800 positions named (Vasudha, Vaishnavi, Brahmi, etc.).

```
part_index = floor(δ / (30/150))          # 0..149
# Name lookup from D150_NAMES[sign_class][part_index]
# Sign for chart: name's dispositor sign (per UK table)
```

Full Vasudha→Indumukhi name table has 1800 entries (UK Appendix; reproduced in Sanjay Rath's *Nadi Astrology*). We encode the table as a static data file `src/josi/data/d150_nadi_amsa_names.json`.

#### 3.1.7 Sign class rotations (all D>30 vargas)

Sign class (movable=chara, fixed=sthira, dual=dwisvabhava) affects direction of counting for vargas of certain orders. BPHS Ch. 7 v. 10-12 gives the rule:
- Movable signs: count forward from sign itself
- Fixed signs: count forward from the 9th from sign
- Dual signs: count forward from the 5th from sign

This rule applies to D9, D12 (partially), and by convention to D108 composite and D150 Nadi. Extended vargas D72, D84, D100, D144 follow the **simple cyclic rule** per UK — no sign-class rotation.

### 3.2 Sarvatobhadra Chakra (SBC)

Source: *Brihat Samhita* Ch. 86 (Varahamihira) + *Muhurta Martanda* + multiple Kerala muhurta manuscripts. Canonical modern treatment: J.N. Bhasin, *Sarvatobhadra Chakra* (1993); B.V. Raman, *Muhurtha* Ch. 18.

#### 3.2.1 Grid structure

A 9×9 matrix. Conceptually, the outer ring contains the movable content (nakshatras, weekdays, etc.); the inner 7×7 contains 12 rashis arranged in 4 arms and the center.

**Full layout** (Bhasin p. 14):

- **Row 0 (top, 9 cells)**: Nakshatras spanning from Krittika (east-start) across the top → Revati
- **Col 0 (left, 9 cells)**: Nakshatras descending (Magha zone)
- **Col 8 (right, 9 cells)**: Nakshatras ascending (Anuradha zone)
- **Row 8 (bottom, 9 cells)**: Nakshatras (Shravana zone)
- **Corners (4 cells)**: Vowel sets (a, i, u, e, ai, o, au, etc. — Devanagari vowels) — 16 total, 4 per corner
- **Inner 7×7**: 12 rashis in a cross-pattern:
  - Center cell (4,4): empty (points to the moment itself)
  - North arm (rows 1-3, col 4): 3 rashis (Meena, Kumbha, Makara) — fixed by tradition
  - East arm (row 4, cols 5-7): 3 rashis (Mesha, Vrisha, Mithuna)
  - South arm (rows 5-7, col 4): 3 rashis (Karka, Simha, Kanya)
  - West arm (row 4, cols 1-3): 3 rashis (Tula, Vrischika, Dhanus)
- **Remaining interior cells**: weekdays (8 including "intercalary"), tithi categories (nanda/bhadra/jaya/rikta/purna, mapped to cells)

The exact grid is canonicalized in `src/josi/data/sarvatobhadra_grid.json` — derived from Bhasin's published grid, cross-checked against Raman *Muhurtha*.

#### 3.2.2 Nakshatras — 28, not 27

SBC includes **Abhijit** as the 28th nakshatra, inserted between Uttara Ashadha and Shravana. Abhijit occupies sidereal longitude 276°40'–280°53' — overlapping the boundary of standard 27-nakshatra system (Uttara Ashadha 270°–283°20'; Shravana 283°20'–296°40'). The overlap is traditionally handled as "Abhijit is a 28th shared region; for muhurta it is a distinct auspicious nakshatra."

For SBC purposes, Abhijit is a distinct cell and a planet/Moon falling in its specific longitude range occupies the Abhijit cell.

#### 3.2.3 Auspiciousness query

Given:
- A natal Moon nakshatra (fixed for a given person)
- A current Moon nakshatra, weekday, tithi
- Optionally a query letter/name

The SBC is evaluated for:
1. **Vedha** — blockage on opposite row/col from natal Moon. Planets transiting the vedha-pada cells are inauspicious for that native on that day.
2. **Letter-auspiciousness** — for a chosen name/letter (in corner-vowel region), check distance to natal Moon's row/col/arm; closer = better.
3. **Weekday fitness** — weekday cell's arm-match with natal Moon's arm.

**E7 ships:**
- SBC grid construction (static, identical for all charts)
- Projection of chart's natal Moon onto grid → `natal_cell` coordinates
- Query endpoint that evaluates a candidate moment (date/time + optional letter) and returns `fitness_score` ∈ [0, 1] with breakdown

**E7 defers** (E7b):
- Full vedha analysis
- Adverse-yoga detection on SBC
- Integration with muhurta engine (E-muhurta, not yet scoped)

### 3.3 Upagrahas (Sub-Planets)

Upagrahas are shadow points, not astronomical bodies. They are computed from day/night duration fractions or sun-longitude arithmetic. Two schools differ on which are canonical and on exact formulas.

**Existing in Josi:** Gulika, Mandi (BPHS Ch. 7 v. 40).

**To add in E7:**

#### 3.3.1 Sun-longitude-derived Upagrahas (North Indian; BPHS Ch. 7 v. 58-65)

These are computed by adding fixed offsets to the Sun's longitude. Their formulas are the same across schools.

| Upagraha | Formula (λ = Sun longitude) | Citation |
|---|---|---|
| Dhuma | λ + 133°20' | BPHS 7.58 |
| Vyatipata (Pata) | 360° − Dhuma = 360° − (λ + 133°20') = 226°40' − λ | BPHS 7.59 |
| Parivesha | Vyatipata + 180° | BPHS 7.60 |
| Chapa (Indrachapa) | 360° − Parivesha | BPHS 7.61 |
| Upaketu | Chapa + 16°40' | BPHS 7.62 |

All modulo 360°. These five are the "Pancha Upagrahas" cited by most North Indian commentators.

#### 3.3.2 Day/night-duration-derived Upagrahas (Kerala school; BPHS Ch. 7 v. 40-57; Kerala commentaries)

These are based on dividing the day (sunrise→sunset) or night (sunset→sunrise) into 8 parts and assigning each part to a planet by a weekday-based scheme. The longitude computed is the ascendant at the start of the "assigned slot."

| Upagraha | Day/Night | Slot assignment | Citation |
|---|---|---|---|
| Kala | Day | 1st slot on Sunday; rotates | BPHS 7.41 |
| Mrityu | Day | 5th slot on Sunday; rotates | BPHS 7.43 |
| Ardhaprahara | Day | 6th slot on Sunday; rotates | BPHS 7.45 |
| Yamakantaka | Day | 4th slot on Sunday; rotates | BPHS 7.47 |

**Weekday slot rotation rule** (BPHS 7.41): For Sunday, Kala occupies slot 1 (Sun's slot). Each subsequent weekday shifts the slot assignments by +1 in the weekday lord sequence (Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn). Thus on Monday, Kala occupies the slot that was Moon's on Sunday, etc.

**E7 provides both schools:**
- `source_id = 'north_indian_upagraha'` → Dhuma, Vyatipata, Parivesha, Chapa, Upaketu, Kala, Mrityu, Ardhaprahara, Yamakantaka (9 upagrahas)
- `source_id = 'kerala_upagraha'` → same 9, but Kerala commentaries differ on Mrityu and Ardhaprahara slot numbers. Kerala convention per *Hora Deepika*: Mrityu = 5th slot, Ardhaprahara = 7th slot (not 6th).

Both schools are simultaneously computable; astrologer preference determines which surfaces.

### 3.4 Alternatives considered

| Alternative | Rejected because |
|---|---|
| Only implement BPHS; ignore UK-only vargas | Loses ≥ 2 commonly cited vargas (D108, D150 Nadi); Nadi astrologers explicitly use these |
| Only the "high confidence" upagrahas (5) | Kerala astrologers rely on 8 including Kala/Mrityu; losing them blocks muhurta accuracy |
| Represent SBC as plain matrix JSON | UI and query-engine need structure; we emit structured_positions with explicit cell typing |
| Separate output_shape for SBC | Adds a 12th shape to the F7 closed catalog; F7's 10-shape closure is non-negotiable. SBC fits `structured_positions` (cells as positions) with grid in details. |
| Dynamic SBC construction per chart | SBC grid is static (culturally fixed); only the chart's Moon-projection varies |

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| Which D108 variant is canonical | Both; variant per source_id | Literature disagreement; let astrologer choose |
| D150 name-table storage | Static JSON data file | 1800-entry immutable table; version with rule bumps |
| Sign-class rotation for D>30 vargas | Simple cyclic per UK | Extends natural pattern; no cited exception |
| Abhijit inclusion in SBC | Yes, as distinct cell | Canonical per Bhasin; 28-cell nakshatra ring |
| SBC grid static or per-chart | Static; projection varies | Matches classical understanding |
| Upagraha schools | Ship both Kerala + North Indian as source_ids | Real disagreement; both valid |
| Day/night boundary for Kerala upagrahas | Swiss ephemeris civil sunrise/sunset | Standard; documented in details |
| Computing Upagraha ascendant vs longitude | Ascendant-at-slot-start (classical) | BPHS explicit; not longitude of Sun + offset |
| Shape for SBC | `structured_positions` with `details.grid` | F7 closed catalog; grid is engine-internal detail |
| D300 ship at this EPIC | No | Low citation frequency; birth-time precision insufficient |
| Vedha analysis ship | No (E7b) | Non-trivial; sit alongside muhurta engine |
| Integration with Panchang engine | Loose — SBC reads current Moon nakshatra from Panchang; doesn't modify Panchang | Unchanged contract |
| Reference implementation for cross-check | JH 7.41 (upagrahas), Parashara's Light (vargas), Kala (SBC) | Standard tri-source validation |

## 5. Component Design

### 5.1 New modules

```
src/josi/services/classical/
├── vargas_extended/
│   ├── __init__.py
│   ├── extended_calculator.py            # ExtendedVargaCalculator
│   ├── d72_dwadashottari.py
│   ├── d84_chaturashittiyamsa.py
│   ├── d100_shatamsa.py
│   ├── d108_ashtottari.py                # variants A/B selectable by source
│   ├── d144_nadi_extended.py
│   └── d150_nadi_strict.py
├── sarvatobhadra/
│   ├── __init__.py
│   ├── grid.py                           # static grid loader
│   ├── projector.py                      # project natal Moon + query into grid
│   └── fitness.py                        # compute fitness_score for a query
└── upagrahas_extended/
    ├── __init__.py
    ├── sun_derived.py                    # Dhuma, Vyatipata, Parivesha, Chapa, Upaketu
    └── daylight_derived.py                # Kala, Mrityu, Ardhaprahara, Yamakantaka

src/josi/data/
├── d150_nadi_amsa_names.json             # 1800 entries
└── sarvatobhadra_grid.json               # static 9×9 grid definition

src/josi/rules/
├── vargas_extended/
│   └── bphs/ + uttara_kalamrita/ + raman_commentary/
├── sarvatobhadra/
│   └── bphs/ + kerala_muhurta/
└── upagrahas/
    ├── kerala_upagraha/
    └── north_indian_upagraha/

src/josi/api/v1/controllers/
├── vargas_extended_controller.py
├── sarvatobhadra_controller.py
└── upagrahas_extended_controller.py
```

### 5.2 Data model additions

No new tables. Results flow to `technique_compute` with:
- `technique_family_id = 'varga_extended'` for D72–D150
- `technique_family_id = 'varga_extended'` for SBC (reuse family; shape-carried distinction)
- `technique_family_id = 'varga_extended'` for upagrahas (Gulika/Mandi remain in existing panchang family; new 9 go here)

Index:
```sql
CREATE INDEX idx_varga_ext_chart_varga
  ON technique_compute (chart_id, (result->>'varga_code'))
  WHERE technique_family_id = 'varga_extended';
```

### 5.3 API contract

```
GET /api/v1/charts/{chart_id}/vargas/extended
Response 200:
{
  "success": true,
  "data": {
    "positions": [
      {"name":"d72.sun","sign":5,"house":null,"degree":14.2,"details":{"varga_code":"D72"}},
      {"name":"d108.sun","sign":2,"degree":3.1,"details":{"varga_code":"D108","variant":"composite"}},
      ...
    ]
  }
}

GET /api/v1/charts/{chart_id}/sarvatobhadra
Response 200 (structured_positions + grid in details):
{
  "success": true,
  "data": {
    "positions": [
      {"name":"natal_moon_cell","details":{"row":3,"col":7}}
    ],
    "details": {
      "grid": [ [ {"type":"nakshatra","value":"krittika"}, ...], ... ],
      "natal_cell": {"row":3,"col":7}
    }
  }
}

POST /api/v1/charts/{chart_id}/sarvatobhadra/query
Body: {"at":"2026-04-20T10:00:00Z","letter":"ra","weekday":"monday"}
Response 200:
{
  "success": true,
  "data": {
    "fitness_score": 0.78,
    "breakdown": {
      "nakshatra_match": 0.80,
      "letter_distance": 0.75,
      "weekday_arm_match": 1.00,
      "vedha_block": false
    }
  }
}

GET /api/v1/charts/{chart_id}/upagrahas?school=kerala
Response 200: TechniqueResult[StructuredPositions]
```

### 5.4 Internal Python interface

```python
# src/josi/services/classical/vargas_extended/extended_calculator.py

class ExtendedVargaCalculator:
    SUPPORTED_VARGAS: set[str] = {"D72","D84","D100","D108","D144","D150"}

    def compute_varga(self, planet_longitudes: dict[str, float],
                      varga_code: str, source_id: str) -> dict[str, PlanetPosition]:
        ...

# src/josi/services/classical/sarvatobhadra/fitness.py

class SBCFitnessEvaluator:
    def evaluate(self, natal_moon_nakshatra: str,
                 current_moon_nakshatra: str,
                 weekday: str,
                 letter: str | None = None,
                 tithi: int | None = None) -> SBCFitnessResult:
        ...

# src/josi/services/classical/upagrahas_extended/daylight_derived.py

class DaylightUpagrahaCalculator:
    def compute(self, date_utc: datetime, location: GeoLocation,
                school: Literal["kerala","north_indian"]) -> dict[str, UpagrahaPosition]:
        ...
```

## 6. User Stories

### US-E7.1: As a Nadi astrologer, I need D150 chart with classical name lookup
**Acceptance:** `GET /api/v1/charts/{chart_id}/vargas/extended` returns D150 positions with `details.nadi_name` = "Vasudha" (or whichever) for each planet, matching the UK table.

### US-E7.2: As an astrologer, I can switch between D108 composite vs direct via source preference
**Acceptance:** setting `astrologer_source_preference.source_weights = {"bphs": 1.0}` yields composite; `{"raman_commentary": 1.0}` yields direct; outputs differ for the same chart.

### US-E7.3: As a muhurta astrologer, I can evaluate a candidate moment against the SBC
**Acceptance:** `POST /api/v1/charts/{chart_id}/sarvatobhadra/query` with a datetime + letter returns fitness score with breakdown; fits classical Bhasin examples within ±0.05.

### US-E7.4: As an astrologer consulting Kerala school, I receive 9 upagrahas per Kerala formulas
**Acceptance:** `GET /api/v1/charts/{chart_id}/upagrahas?school=kerala` returns 9 positions including Mrityu at slot-5, Ardhaprahara at slot-7 (Kerala convention).

### US-E7.5: As the AI chat surface, all extended-varga and upagraha outputs validate against F7 `structured_positions`
**Acceptance:** every engine output passes `fastjsonschema.compile(structured_positions_schema)(output)`.

### US-E7.6: As a chart reader, SBC grid is consistent across all charts
**Acceptance:** `details.grid` for chart A equals `details.grid` for chart B (same 9×9); only `natal_cell` differs.

### US-E7.7: As an engineer, adding D300 in the future requires zero architecture changes
**Acceptance:** adding a new D300 module + YAML under `src/josi/rules/vargas_extended/` + registering the varga code in `ExtendedVargaCalculator.SUPPORTED_VARGAS` is the full diff.

## 7. Tasks

### T-E7.1: Extended Varga calculator (D72/D84/D100/D144)
- **Definition:** One module per varga with `compute(longitudes, source_id)`; 4 modules.
- **Acceptance:** 4 vargas × 5 chart fixtures = 20 test points match JH output.
- **Effort:** 10 hours
- **Depends on:** existing DivisionalChartsCalculator

### T-E7.2: D108 composite + direct variants
- **Definition:** Single module with `variant` parameter: `composite` (navamsa-of-dwadashamsa) or `direct` (108-fold).
- **Acceptance:** composite matches JH (BPHS mode); direct matches Raman worked example.
- **Effort:** 6 hours

### T-E7.3: D150 Nadi Amsa + name table
- **Definition:** JSON data file with 1800 Vasudha→Indumukhi entries (from UK Appendix); compute module returns sign + name.
- **Acceptance:** 10 longitude fixtures return correct name + sign per UK table.
- **Effort:** 14 hours (data entry dominates)

### T-E7.4: Sign-class rotation helper
- **Definition:** Utility function `rotate_for_sign_class(sign, amount_by_class)` usable by any varga that needs it (composite D108, Navamsa-style).
- **Acceptance:** 6 rotation cases (2 per class) verified.
- **Effort:** 2 hours

### T-E7.5: Sun-derived upagraha module
- **Definition:** `sun_derived.py` with 5 functions + orchestrator; formulas §3.3.1.
- **Acceptance:** 5 upagrahas × 5 fixtures = 25 test points match JH; modular arithmetic correct at 360° boundary.
- **Effort:** 6 hours

### T-E7.6: Daylight-derived upagraha module (both schools)
- **Definition:** `daylight_derived.py` implementing Kala/Mrityu/Ardhaprahara/Yamakantaka slot computation; branches on school.
- **Acceptance:** Kerala and North Indian variants produce different Mrityu/Ardhaprahara on Sunday fixture; ascending-sign computation validated.
- **Effort:** 10 hours

### T-E7.7: SBC grid data + loader
- **Definition:** `sarvatobhadra_grid.json` encoding Bhasin's 9×9 layout (281 cell entries: 9 × 9 + metadata on cells); `grid.py` exposes typed structure.
- **Acceptance:** Grid loads; Bhasin's published diagram (p. 14) byte-for-byte matches rendered grid.
- **Effort:** 10 hours (data entry + validation)

### T-E7.8: SBC projector + fitness evaluator
- **Definition:** `projector.py` maps natal Moon nakshatra to grid coordinates; `fitness.py` implements `evaluate` with nakshatra-match + letter-distance + weekday-arm-match + vedha-detect.
- **Acceptance:** 10 Bhasin worked examples pass within ±0.05 fitness.
- **Effort:** 12 hours

### T-E7.9: Rule YAMLs (extended vargas + upagrahas + SBC)
- **Definition:** YAMLs under `src/josi/rules/vargas_extended/` (bphs + UK + Raman sources), `src/josi/rules/upagrahas/` (kerala + north_indian), `src/josi/rules/sarvatobhadra/` (bphs). Each cites source verse.
- **Acceptance:** All YAMLs validate via `poetry run validate-rules`.
- **Effort:** 14 hours

### T-E7.10: API controllers + routing
- **Definition:** Three controllers with listed endpoints; register in `api/v1/__init__.py`.
- **Acceptance:** OpenAPI documents all endpoints; integration tests cover all routes.
- **Effort:** 8 hours

### T-E7.11: Golden fixtures
- **Definition:** 5 natal charts each with expected D72/D84/D100/D108/D144/D150 positions, 9 upagraha positions (both schools), SBC natal cell + 3 queries.
- **Acceptance:** All assertions green; fixtures stored under `tests/golden/charts/`.
- **Effort:** 16 hours

### T-E7.12: Performance benchmarks
- **Definition:** Benchmark extended-varga batch compute (all 6 vargas, 9 planets) < 50 ms per chart; SBC query < 20 ms.
- **Acceptance:** pytest-benchmark under thresholds.
- **Effort:** 4 hours

### T-E7.13: Documentation
- **Definition:** Docs note on how to pick school; SBC interpretation primer in docs/markdown/.
- **Acceptance:** CLAUDE.md + /docs updated.
- **Effort:** 3 hours

## 8. Unit Tests

### 8.1 Extended Vargas

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_d72_simple_cyclic_first_part` | λ=0.1° Aries | d72_sign=Aries (first part of 72) | boundary |
| `test_d72_last_part` | λ=29.99° Aries | d72_sign=Pisces ((0*72 + 71) mod 12 + 1 = 12) | last part |
| `test_d84_sign_progression` | λ=15° Leo | d84 matches hand-computed | basic |
| `test_d100_matches_jh_fixture` | 5-planet chart | matches JH D100 output | cross-tool parity |
| `test_d108_composite_matches_bphs` | chart | composite variant output | BPHS alignment |
| `test_d108_direct_matches_raman_example` | Raman's published example | direct variant output | alternative variant |
| `test_d108_variants_differ` | same chart | composite ≠ direct | distinct sources |
| `test_d144_simple_cyclic` | λ = 15.5° Virgo | d144 matches hand-computed | basic |
| `test_d150_nadi_name_lookup_vasudha` | λ = 0.2° Aries | name="vasudha", sign=Aries | UK table entry |
| `test_d150_nadi_name_lookup_indumukhi` | λ = 359.9° Pisces | name="indumukhi" (last entry) | UK table last entry |
| `test_d150_all_1800_positions_have_names` | all 1800 fixture positions | all have non-null name | data integrity |

### 8.2 Sun-derived upagrahas

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_dhuma_formula` | Sun at 10° Aries (10°) | Dhuma = 10 + 133°20' = 143°20' | BPHS 7.58 |
| `test_vyatipata_complement` | Sun at 10° Aries | Vyatipata = 360 − Dhuma = 216°40' | BPHS 7.59 |
| `test_parivesha_opposite_vyatipata` | same | Parivesha = Vyatipata + 180 = 36°40' | BPHS 7.60 |
| `test_chapa_complement_parivesha` | same | Chapa = 360 − Parivesha = 323°20' | BPHS 7.61 |
| `test_upaketu_offset_from_chapa` | same | Upaketu = Chapa + 16°40' = 340° | BPHS 7.62 |
| `test_upagraha_wrap_360` | Sun = 280° → Dhuma = 280 + 133°20' = 413°20' → 53°20' | wrap applied | modular arithmetic |

### 8.3 Daylight-derived upagrahas

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_kala_sunday_slot_1` | Sunday, known sunrise/sunset | Kala = ascending sign at 1st-slot start | BPHS 7.41 |
| `test_kala_monday_rotation` | Monday | Kala in slot-2 region (rotated) | weekday rotation |
| `test_mrityu_kerala_slot_5` | Sunday Kerala | Mrityu at 5th slot | Kerala convention |
| `test_mrityu_ni_same_slot_5` | Sunday NI | Mrityu also 5th (schools agree on Mrityu in BPHS) | baseline |
| `test_ardhaprahara_kerala_slot_7` | Kerala | 7th slot | Kerala convention |
| `test_ardhaprahara_ni_slot_6` | NI | 6th slot | North Indian convention |
| `test_yamakantaka_slot_4` | Sunday | slot-4 | BPHS 7.47 |
| `test_upagraha_schools_produce_different_outputs` | same chart | Mrityu Kerala ≠ Mrityu NI **on non-Sunday day** (rotation carries through differently) | school independence |

### 8.4 Sarvatobhadra Chakra

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_sbc_grid_is_9x9` | static grid | 81 cells | structure |
| `test_sbc_contains_28_nakshatras` | grid | 28 distinct nakshatra cells (including Abhijit) | completeness |
| `test_sbc_contains_12_rashis_inner_cross` | grid | 12 rashi cells arranged 3+3+3+3 around center | layout |
| `test_sbc_natal_moon_projection` | natal Moon in Rohini | natal_cell = (Bhasin row/col for Rohini) | projection |
| `test_sbc_fitness_nakshatra_exact_match` | natal Rohini, query Rohini | fitness ≥ 0.9 | nakshatra-match max |
| `test_sbc_fitness_vedha_block` | query position is 180° from natal | vedha_block=true, fitness < 0.3 | vedha logic |
| `test_sbc_fitness_letter_auspicious` | letter in natal arm | letter_distance=0 | letter subscore |
| `test_sbc_bhasin_example_1` | Bhasin p.42 worked example | fitness matches within 0.05 | classical canonical |
| `test_sbc_bhasin_example_2` | Bhasin p.51 worked example | same | second canonical |
| `test_sbc_grid_byte_identical_across_charts` | 10 charts | `details.grid` equal across all | static grid invariant |

### 8.5 API integration

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_extended_vargas_endpoint_all_six` | GET .../vargas/extended | 6 varga codes present in positions | completeness |
| `test_upagrahas_endpoint_both_schools` | GET .../upagrahas?school=kerala vs ?school=north_indian | 9 positions each; Mrityu/Ardhaprahara differ | school wiring |
| `test_sarvatobhadra_get_returns_grid` | GET .../sarvatobhadra | response has details.grid[9][9] | shape contract |
| `test_sarvatobhadra_query_fitness_in_range` | POST .../query | fitness_score ∈ [0,1] | boundary |
| `test_vargas_output_structured_positions_schema` | output | passes F7 fastjsonschema | parity |
| `test_upagrahas_output_structured_positions_schema` | output | passes F7 schema | parity |
| `test_sarvatobhadra_output_structured_positions_with_grid_detail` | output | base shape valid; details.grid 9×9 | shape-within-shape |

### 8.6 Determinism & idempotency

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_extended_varga_idempotent_recompute` | call twice | 1 technique_compute row | F2 contract |
| `test_sbc_query_deterministic` | same query twice | identical fitness_score | determinism |
| `test_d150_name_lookup_stable_across_runs` | 10 longitudes | same names 100× | data immutability |

## 9. EPIC-Level Acceptance Criteria

- [ ] 6 extended vargas (D72, D84, D100, D108 both variants, D144, D150) implemented and tested
- [ ] D150 Nadi Amsa name table (1800 entries) loaded from static JSON; lookups work
- [ ] 9 upagrahas per school (Kerala, North Indian) implemented; both schools selectable via source_id
- [ ] Sarvatobhadra Chakra 9×9 grid construction matches Bhasin's published diagram
- [ ] SBC projector correctly maps natal Moon nakshatra to grid cell
- [ ] SBC fitness evaluator with 4 sub-scores (nakshatra, letter, weekday-arm, vedha) matches 2 classical worked examples
- [ ] Output validates against F7 `structured_positions` schema for all three families
- [ ] API endpoints for all three families live and documented in OpenAPI
- [ ] Golden chart suite: 5 charts × 6 vargas + 9 upagrahas × 2 schools + 3 SBC queries = ~220 assertions all green
- [ ] Unit test coverage ≥ 90% across new packages
- [ ] Integration tests cover full path (compute → persist → aggregate → API read)
- [ ] Performance: extended-varga batch < 50 ms; SBC query < 20 ms
- [ ] CLAUDE.md updated: "extended vargas live under `src/josi/rules/vargas_extended/`; to add a new varga, implement module + rule YAML"
- [ ] Both D108 variants selectable and distinctly computable

## 10. Rollout Plan

- **Feature flag:** `enable_extended_vargas`, `enable_sarvatobhadra`, `enable_extended_upagrahas` — three independent flags. Default off until QA; on in P2 after validation.
- **Shadow compute:** 1 week shadow on extended vargas (log outputs, compare to JH where possible); SBC + upagrahas ship with direct testing.
- **Backfill strategy:** lazy (compute on first request); no bulk backfill needed (vargas are cheap).
- **Rollback plan:** set feature flag false; endpoints return 501; no data destruction; redeploy old code.

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| D150 name-table transcription errors | Medium | High | Cross-check against two published sources (UK + Rath); unit tests on edge entries |
| D108 variant selection confuses users | Medium | Medium | UI shows variant label; astrologer source preference is explicit |
| SBC Abhijit longitude overlap creates edge-case bug | Medium | Medium | Explicit test at 276°40' boundary |
| Kerala vs NI upagraha slot numbers contested by regional practitioners | Medium | Low | Documented per-school; allow override |
| Daylight-fraction upagrahas sensitive to sunrise/sunset source | Low | Medium | Use consistent Swiss Ephemeris civil sunrise; document in details |
| Large D150 name-table JSON bloats bundle | Low | Low | Load lazily; total size ~150 KB |
| SBC grid layout published variants differ (Bhasin vs Raman vs South Indian) | Medium | Medium | Ship Bhasin (most cited) as source_id='bphs'; E7b adds Raman variant |
| Upagraha computation duplicates existing Gulika/Mandi | Certain | Low | Keep Gulika/Mandi in existing `PanchangCalculator`; new 9 live in `upagrahas_extended/` |
| Sign-class rotation for D108 composite subtle bugs | Medium | High | Fuzz with Hypothesis; unit test per sign-class |

## 12. References

- Master spec: [`docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`](../../../superpowers/specs/2026-04-19-classical-techniques-expansion-design.md) §2.2 (varga coverage), §5.2 (tagging)
- F1 dims: [`../P0/F1-star-schema-dimensions.md`](../P0/F1-star-schema-dimensions.md) — add `kerala_upagraha`, `north_indian_upagraha`, `raman_commentary` source_ids
- F2 fact tables: [`../P0/F2-fact-tables.md`](../P0/F2-fact-tables.md)
- F6 Rule DSL: [`../P0/F6-rule-dsl-yaml-loader.md`](../P0/F6-rule-dsl-yaml-loader.md)
- F7 Output shapes: [`../P0/F7-output-shape-system.md`](../P0/F7-output-shape-system.md) §5.3.7 `structured_positions`
- F8 Aggregation: [`../P0/F8-technique-result-aggregation-protocol.md`](../P0/F8-technique-result-aggregation-protocol.md)
- E1a Multi-Dasa v1
- E10 Prasna (consumer of SBC for omen analysis)
- **Classical sources:**
  - Maharshi Parashara, *Brihat Parashara Hora Shastra* — Santhanam trans., Ranjan Publications — Ch. 7 v. 32-34 (extended vargas), v. 40-65 (upagrahas)
  - Kalidasa, *Uttara Kalamrita* — G.K. Ojha trans., Motilal Banarsidas — Ch. 4 v. 3-16 (D72-D150 vargas)
  - Varahamihira, *Brihat Samhita* — M. Ramakrishna Bhat trans. — Ch. 86 (Sarvatobhadra foundations)
  - J.N. Bhasin, *Sarvatobhadra Chakra*, 1993, Sagar Publications — primary modern treatment
  - B.V. Raman, *Muhurtha*, UBSPD — Ch. 18 (SBC applications)
  - Sanjay Rath, *Nadi Astrology* — D150 name table cross-reference
  - Kerala *Hora Deepika* (manuscript tradition; selectively cited for Kerala upagraha slot numbers)
- **Reference implementations:**
  - Jagannatha Hora 7.41 — "Divisional Charts" tab (extended vargas), "Upagrahas" tab
  - Parashara's Light 9.0 — divisional charts (commercial)
  - Kala software — SBC rendering (Indian-market commercial)
