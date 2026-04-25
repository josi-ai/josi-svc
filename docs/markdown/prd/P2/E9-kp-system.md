---
prd_id: E9
epic_id: E9
title: "KP System — Sub-Lord, Significators, Ruling Planets, KP Horary"
phase: P2-breadth
tags: [#correctness, #extensibility, #ai-chat, #astrologer-ux]
priority: must
depends_on: [F1, F2, F6, F7, F8, F13, E1a]
enables: [E10, E14a, E12]  # 2026-04-23: P2-UI-kp resolved to E12 Astrologer Workbench UI (dedicated KP tab)
classical_sources: [kp_reader]
estimated_effort: 5-6 weeks
status: draft
author: "@agent"
last_updated: 2026-04-22
---

# E9 — KP System: Sub-Lord, Significators, Ruling Planets, KP Horary

## 1. Purpose & Rationale

The Krishnamurti Paddhati (KP) system, developed by K.S. Krishnamurti (1908–1972) and published across six "KP Readers" (1971–1983), is the **single classical system with single-source authority**: there is no BPHS fallback, no inter-text disagreement to adjudicate. Krishnamurti himself specified every rule, and his son and students (through the KP journal and later societies) preserved it as a closed system.

KP is the **dominant horary methodology in South India and Sri Lanka**, with millions of practicing astrologers worldwide. Its distinguishing features:

1. **Sub-lord division** — each of the 27 nakshatras is subdivided into 9 **sub-divisions** proportional to the Vimshottari dasa lord periods, producing 243 "subs" across the zodiac. Planets and cusps each have a unique sub-lord.
2. **Multi-level significator hierarchy** — every house has 5 levels of significators (planets signifying the house), with strict ordering that enables clean event-outcome prediction.
3. **Ruling Planets (RP)** — at any moment, a set of 4-5 "ruling planets" is derivable from the day, Lagna, and Moon. Events manifest when transits + RPs + significators align.
4. **KP Horary number method** — uniquely, KP assigns each of 249 numbers to a specific zodiacal longitude (Aries 0°0' to Pisces 29°41'). The querent picks a number 1-249; the horary chart casts with that number as Ascendant-proxy.
5. **Cuspal sub-lord analysis** — the sub-lord of each house cusp, read by what that sub-lord signifies, determines outcomes for that house's matters. This is the core predictive engine.

Without E9, Josi cannot serve KP astrologers (a large market) and cannot power E10's unified Prasna/Horary EPIC (which requires KP as one of two first-class horary methods).

This PRD delivers KP as a **full engine family** with its own compute module, predicate vocabulary, rule set (sourced exclusively from K.S. Krishnamurti's *KP Reader Vols 1-6*), API surface, and a dedicated output shape.

## 2. Scope

### 2.1 In scope

- **Sub-lord computation** — precise 243-sub zodiac table; API to query sub-lord for any longitude.
- **Sub-sub-lord (and deeper)** — KP practice uses up to 5 levels (Sub, Sub-Sub, ..., 5th-level). Engine supports all 5.
- **Cuspal sub-lords** — for each of 12 house cusps, resolve sub/sub-sub lords. Placidus house system default (KP-standard); allow override.
- **Multi-level significator hierarchy** — for each house 1..12, compute 5-level significator set per KP Reader Vol. 2 Ch. 4:
  1. Planets in the house.
  2. Planets in nakshatras of planets in the house (level 1's nakshatra-disposers).
  3. Lord of the house.
  4. Planets in nakshatras of the lord.
  5. Planets conjunct the house lord or its nakshatra lord.
- **Ruling Planets (RP)** for arbitrary moment: day lord, ascendant sign lord, ascendant nakshatra lord, Moon sign lord, Moon nakshatra lord (and some variants include ascendant sub-lord).
- **KP Horary number method** — 249-number mapping table; given (number, moment, location), cast horary chart.
- **Cuspal sub-lord analysis** — for each house, determine if the cuspal sub-lord is a significator of that house's matter (positive) or of contrary houses (negative). Emit outcome per house.
- **Output shape proposal: `kp_analysis`** — a new 11th output shape. Propose to F7 team; if rejected, fall back to `structured_positions` with rich `details`. **This PRD's primary recommendation: propose `kp_analysis` as a new shape.**
- **Rule YAMLs** registered under `source_id='kp_reader'`.
- **API surface**:
  - `GET /api/v1/charts/{chart_id}/kp/sub-lords` — per-planet and per-cusp sub-lords
  - `GET /api/v1/charts/{chart_id}/kp/significators` — full 5-level map for 12 houses
  - `GET /api/v1/charts/{chart_id}/kp/ruling-planets?at={iso}` — RPs for given moment (default: now)
  - `POST /api/v1/charts/{chart_id}/kp/cuspal-analysis?house={1..12}&matter={marriage|...}` — targeted analysis
  - `POST /api/v1/kp/horary` — KP horary by number method

### 2.2 Out of scope

- **KP Stellar Horoscopy** (Book 1-2 older methodology pre-dating number method) — covered by implication in sub-lord rules; standalone surfacing deferred.
- **KP yearly dasa for marital/child timing** — standard Vimshottari is shared with E1a; KP-specific refinements deferred to E9b.
- **KP financial astrology** specialized rules — niche; P3+.
- **Stellar sub-lord theory extensions** from KP derivative literature (K.P. Hariharan, Kanak Bosmia) — stick to primary Krishnamurti texts.
- **The 7th-level sub** and beyond — practical KP stops at 5 levels.
- **Regional KP variations** (Tamil KP vs Telugu KP) — uniform Krishnamurti corpus only.

### 2.3 Dependencies

- F1 — add `source_id='kp_reader'`; add `technique_family_id='kp'`
- F2 — fact tables
- F6 — rule DSL loader
- F7 — add `kp_analysis` output shape; if deferred, use `structured_positions`
- F8 — aggregation protocol
- E1a — natal chart primitives; Vimshottari dasa proportions (reused for sub boundaries)
- `pyswisseph` for Placidus house cusps (existing in Josi for Western calc)

## 2.4 Design Decisions (Pass 1 Astrologer Review — Locked 2026-04-22)

All open questions from E9 Pass 1 astrologer review are resolved. KP is **single-source canon** (KS Krishnamurti KP Reader Vols 1-6, 1971-1983) — no commentary variants unlike Parashari/Jaimini/Tajaka PRDs.

### Cross-cutting decisions

| Decision | Value | Ref |
|---|---|---|
| Krishnamurti ayanamsa | Required for KP chart (in astrologer 9-shortlist) | DECISIONS 1.2 |
| Placidus house system | Required for KP chart (in astrologer 6-shortlist) | DECISIONS 1.3 |
| Rahu/Ketu node type | Both Mean + True | DECISIONS 1.1 |
| Natchathiram count | 27 | DECISIONS 3.7 |
| Sub-lord proportions | Vimshottari dasa lord-years (shared with E1a) | E1a inheritance |
| Language display | Sanskrit-IAST + Tamil phonetic | DECISIONS 1.5 |

### E9-specific decisions (locked this review)

| Decision | Value | Source |
|---|---|---|
| **KP ayanamsa + house system binding** (Q1) | **Separate KP chart — don't modify natal.** Natal chart stays with Lahiri ayanamsa + Whole Sign house system. KP engine generates its OWN chart with Krishnamurti ayanamsa + Placidus houses for KP-specific analysis. Astrologer workbench shows both side-by-side (Parashari natal + KP chart). Cleanest separation. Matches JH convention. | Q1 |
| **Significator hierarchy source** (Q2) | **KP Reader Vol.2 Ch.4 canonical 5-level hierarchy.** Strict single-source (KS Krishnamurti's own text). Levels (strongest → weakest): (1) natchathiram-lords of house occupants, (2) house occupants themselves, (3) natchathiram-lord of house-cusp lord, (4) house-cusp lord, (5) modifier planets (conjunct Level 1-4 OR Rahu/Ketu OR aspecting cusp/lord). Matches all KP software. | Q2 |
| **Ruling Planets variant** (Q3) | **5-element standard** (KP Reader Vol.3 canonical): (1) day lord, (2) ascendant sign lord, (3) ascendant natchathiram lord, (4) Moon sign lord, (5) Moon natchathiram lord. Computed at query moment. Matches JH + PL + Astrosage. | Q3 |
| **Sub-level depth** (Q4) | **5 levels** full KP Reader canonical: Natchathiram lord → Sub-lord → Sub-sub-lord → 4th-level → 5th-level. Each level subdivides by Vimshottari proportions (27 × 9 = 243 subs; 243 × 9 = 2187 sub-subs; etc. through 5 levels). Matches KPStar + JH. | Q4 |
| **KP cross-tradition activation** (Q5) | **Practice-type profile preset.** Astrologer selects at profile creation: Vedic-Parashari only (KP hidden) / Vedic-KP practitioner (KP primary + Parashari cross-reference) / Mixed (both visible) / Western (Vedic+KP hidden, Western Depth per E8/E8b). Matches E8b Q4 convention. | Q5 |
| **KP canon scope** (Q6) | **Strict KP Reader Vols 1-6 only** (KS Krishnamurti 1971-1983). Single-source canonical. No modern extensions (Hariharan 6-element RP, Bosale regional variants, etc.). Matches JH + KPStar + PL + Astrosage. KP's defining feature is single-authority canon — preserving that. Same for both user types. | Q6 |

### KP engine output shape

```python
kp_analysis = {
    "chart_id": str,
    "kp_chart": {  # Separate KP chart per Q1
        "ayanamsa": "krishnamurti",
        "house_system": "placidus",
        "planetary_positions": {planet: {rasi, longitude, natchathiram, sub, sub_sub, ...}},
        "cusps": [12_cusps_with_sub_lords]
    },
    "significators": {  # 5-level hierarchy per Q2
        house_num: {
            level_1: list[graha],  # natchathiram-lords of occupants
            level_2: list[graha],  # occupants
            level_3: list[graha],  # natchathiram-lord of house-cusp lord
            level_4: graha,        # house-cusp lord
            level_5: list[graha]   # modifier planets
        }
    },
    "ruling_planets": {  # 5-element per Q3 at specified moment
        "day_lord": graha,
        "asc_sign_lord": graha,
        "asc_natchathiram_lord": graha,
        "moon_sign_lord": graha,
        "moon_natchathiram_lord": graha,
        "computed_at": datetime
    },
    "sub_depth_levels": 5,  # per Q4
    "source": "kp_reader_vols_1_6"  # strict canon
}
```

### 249-number horary mapping

Static lookup table mapping each number 1-249 to specific zodiacal longitude from Mesham 0°00' at #1 to Meenam 29°41' at #249. KP Reader Vol.3 canonical table. Used in `POST /api/v1/kp/horary` endpoint.

### Engineering action items (not astrologer-review scope)

- [ ] Sub-lord computation engine: 243-sub zodiac table + per-longitude sub-lord lookup
- [ ] 5-level significator computation per KP Reader Vol.2 Ch.4
- [ ] Ruling Planets real-time computation at query moment (5-element)
- [ ] 249-number horary table + horary chart cast endpoint
- [ ] Cuspal sub-lord analysis logic per house + matter mapping
- [ ] Separate KP chart generation (Krishnamurti ayanamsa + Placidus) alongside natal
- [ ] Practice-type profile preset (6 options per Q5) + KP tab visibility logic
- [ ] `kp_analysis` output shape — propose as new F7 shape; fallback to `structured_positions` with rich `details`
- [ ] Golden chart fixtures: 10 KP Reader example charts cross-verified at ±0 exact sub-lord match vs KP Reader Vol.2-4 published cases

---

## 3. Classical Research

**Primary source:** K.S. Krishnamurti, *KP Reader Vols 1-6* (1971–1983), Krishnamurti Publications. These are the **single authority** for the entire KP system. Chapter citations below use the format `KPR-V.Ch.v`.

**Secondary (cited for worked examples only):**
- K.P. Hariharan, *KP Sub Theory* (1990s)
- Kanak Bosmia, *KP Reader Companion* (2010s)
- K.S.K. Haran, *KP — Beyond Basic* (2000s)

We use **only** Krishnamurti's own text for rule authority; secondary sources provide example-verification only.

### 3.1 Sub-Lord Division (KPR-II.Ch.1)

**Foundation:** The 27 nakshatras partition the 360° zodiac into 13°20' segments. Krishnamurti subdivides each nakshatra into **9 sub-divisions** whose widths are proportional to the Vimshottari dasa-lord periods (in years):

| Lord | Years | Sub arc (of nakshatra = 13°20') |
|---|---|---|
| Ketu | 7 | 7/120 × 13°20' = 46'40" |
| Venus | 20 | 20/120 × 13°20' = 2°13'20" |
| Sun | 6 | 6/120 × 13°20' = 40'0" |
| Moon | 10 | 10/120 × 13°20' = 1°6'40" |
| Mars | 7 | 7/120 × 13°20' = 46'40" |
| Rahu | 18 | 18/120 × 13°20' = 2°0'0" |
| Jupiter | 16 | 16/120 × 13°20' = 1°46'40" |
| Saturn | 19 | 19/120 × 13°20' = 2°6'40" |
| Mercury | 17 | 17/120 × 13°20' = 1°53'20" |
| **Total** | **120** | **13°20'0"** |

**Order of subs within a nakshatra:** starts with the nakshatra's OWN lord, then proceeds in Vimshottari order. Example — Krittika (lord Sun) subs in order: Sun, Moon, Mars, Rahu, Jupiter, Saturn, Mercury, Ketu, Venus.

**Resulting 243-sub table:** 27 nakshatras × 9 subs = 243 subs. Each sub is a unique (nakshatra_lord, sub_lord) pair plus a longitude range. Table constant; precompute at application startup.

**Citation:** KPR-II.Ch.1 v.1-12 gives the foundational table. Krishnamurti uses minutes+seconds (archaic); we use floating-point degrees internally.

### 3.2 Sub-Sub-Lord and Deeper (KPR-III.Ch.4)

Same algorithm recurses. Within each sub, divide into 9 sub-subs **proportional to Vimshottari periods**, starting with the sub's own lord.

Formula: `sub_sub_arc(lord) = sub_arc × (lord_years / 120)`.

For a longitude λ: find nakshatra (level 1 lord), then sub (level 2 lord), then sub-sub (level 3 lord), etc. KPR-III.Ch.4 v.5 notes "the 5th level yields a precision of seconds of arc suitable for sub-second timing of events" — practical KP horary uses levels 2-4 actively; 5th level for pinpoint event timing.

E9 ships 5 levels. Each longitude resolves to (L1, L2, L3, L4, L5).

### 3.3 Cuspal Sub-Lord (KPR-II.Ch.2)

For each of 12 Placidus house cusps, compute the sub-lord of the cusp's longitude. This is the **cuspal sub-lord (CSL)**.

KPR-II.Ch.2 v.14: *"The sub-lord of a cusp rules that house's affairs. No matter how many planets reside in or aspect the house, the cuspal sub-lord is decisive."*

E9 computes CSL for all 12 cusps at every compute cycle.

**Placidus is mandatory for KP.** KPR-I.Ch.3 v.7-9 explicitly specifies Placidus houses. Other systems (Koch, equal, whole-sign) **do not** work with KP analysis. E9 hard-codes Placidus unless astrologer overrides (with a warning flag).

### 3.4 Multi-Level Significators (KPR-II.Ch.4)

For any house H (1..12), the set of planets "signifying" H is the union of:

**Level 1 (Occupants):** Planets physically located in house H.

**Level 2 (Occupants' Nakshatra Disposers):** For each planet in level 1, add the lord of its nakshatra.

**Level 3 (Owner):** The sign lord of the sign on cusp H (per Placidus).

**Level 4 (Owner's Nakshatra Disposers):** The nakshatra lord of the house owner.

**Level 5 (Conjunctions/Dispositions):** Planets conjunct with level-3 or level-4 members (orb 5° per KP), or planets in their nakshatra ("stellar subservients").

**Ordering within the set:** KPR-II.Ch.4 v.23 specifies a **strength ordering** within the set — level-2 planets are stronger significators than level-1 (because nakshatra lords override occupants). Ordering for cuspal analysis:
1. Level 2 (strongest — nakshatra of occupant)
2. Level 4 (second — nakshatra of owner)
3. Level 1 (occupants themselves)
4. Level 3 (owner itself)
5. Level 5 (conjunctions)

This **inverted order** is non-obvious but essential for KP prediction accuracy. E9 surfaces significators ranked by level-strength.

### 3.5 Ruling Planets (KPR-III.Ch.7)

At any moment M, Ruling Planets are:

1. **Day Lord (Vaara)** — weekday's planetary lord (Sun=Sunday, Moon=Monday, …).
2. **Ascendant sign lord** at M.
3. **Ascendant nakshatra lord** at M.
4. **Ascendant sub-lord** at M (optional 5th RP in later Krishnamurti writings; KPR-V.Ch.3 adds this).
5. **Moon sign lord** at M.
6. **Moon nakshatra lord** at M.

Traditional list: 4 RPs (day + Asc sign + Asc nakshatra + Moon nakshatra). Extended list: 6 RPs (adds Moon sign lord + Asc sub-lord). E9 supports both via `?extended=false|true`; default extended=true (more common in practice since KPR-V).

**Deduplication:** if Asc sign lord = Moon sign lord, they're counted once. RP list length is typically 3-5 distinct planets.

**Usage in prediction (KPR-III.Ch.8):** an event happens when the significator set of the relevant house overlaps with the Ruling Planets at the moment of prediction or at the moment of manifestation. Strong overlap → high confidence.

### 3.6 KP Horary Number Method (KPR-IV.Ch.1-3)

**The 249-number mapping.** Krishnamurti divided the zodiac not into degrees but into **249 sub-ranges** — specifically the 243 subs plus 6 "padas" derived from deeper-level splits to yield exactly 249 meaningful divisions for horary. Each number 1-249 maps to a specific longitude.

**Actual mapping (KPR-IV Appendix):**
- Number 1 = Aries 0°00' to Aries 0°46'40" (Ketu's sub within Ashwini)
- Number 2 = Aries 0°46'40" to Aries 3°0'0" (Venus's sub within Ashwini)
- ... (follows sub sequence)
- Number 249 = Pisces 29°13'20" to Pisces 30°00'

**Krishnamurti's 249-number table** is reproduced in KPR-IV Appendix B. E9 ships this as `src/josi/data/kp_249_number_table.json` — a static immutable mapping.

**Horary chart casting** (KPR-IV.Ch.2):
1. Querent picks a number N ∈ [1, 249].
2. Astrologer records moment M (time of query) and location L.
3. At time M, compute **all planet positions** as usual.
4. Instead of the **astronomical** ascendant, use the longitude for number N as the **horary Ascendant**.
5. Compute Placidus houses from this horary Ascendant + L.
6. Apply all standard KP analysis: CSL, significators, RPs, sub-lords.

The number-picked-Ascendant replaces the astronomical one. All other planet positions remain real-sky.

### 3.7 Cuspal Sub-Lord Analysis for Outcome Prediction (KPR-II.Ch.6)

For a given question about house H (e.g., marriage → 7th house), the CSL's signification pattern determines outcome:

**Step 1:** Identify CSL of house H.

**Step 2:** Check what houses CSL signifies (via significator levels 1-5, applied to CSL as if querying "what does this planet signify?").

**Step 3:**
- If CSL signifies H AND supporting houses (e.g., for 7H-marriage: 2, 7, 11 are primary; 5 is supporting) → **YES / positive outcome**.
- If CSL signifies contradicting houses (e.g., for marriage: 1, 6, 10 are contra) → **NO / negative outcome**.
- Mixed: further analysis via RPs + current dasha sub-lord.

**House signification map for common queries** (KPR-II.Ch.6 and scattered in Vols 3-5):

| Query | Primary houses | Supporting | Contra |
|---|---|---|---|
| Marriage | 2, 7, 11 | 5 | 1, 6, 10 |
| Children | 2, 5, 11 | — | 1, 4, 10, 12 |
| Career/job | 2, 6, 10, 11 | — | 5, 9 |
| Foreign travel | 3, 9, 12 | — | 4, 8 |
| Education | 4, 9, 11 | — | 8, 12 |
| Health recovery | 1, 5, 11 | — | 6, 8, 12 |
| Litigation win | 6, 11 | — | 12, 8 |
| Lost article recovery | 2, 11 | — | 8, 12 |
| Property acquisition | 4, 11 | — | 3, 12 |
| Financial gain | 2, 11 | — | 8, 12 |

E9 ships this table as `src/josi/data/kp_query_house_map.json` — editable DSL data referenced by horary rules.

### 3.8 Alternatives considered

| Alternative | Rejected because |
|---|---|
| Treat KP as a variant of Parashara (single source_id='parashara_kp') | Loses KP's distinct single-authority branding; astrologers want explicit KP |
| Skip sub-sub-sub (only Sub) | Limits to basic horary; deep KP horary needs level-5 |
| Use existing panchang engine for RPs | RP calculation is simple but has KP-specific conventions (deduplication, extended list); cleaner in own module |
| Store 249-number table in DB | Static data; JSON file avoids migration overhead; immutable per Krishnamurti |
| Allow non-Placidus houses for KP | KPR-I.Ch.3 is explicit; non-Placidus breaks rule semantics; we hard-require Placidus |
| Compute sub-lord on the fly | 243-sub table tiny (~10 KB); precompute at startup |

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| New output_shape `kp_analysis` or reuse | Propose `kp_analysis`; fallback to structured_positions with rich details | F7 catalog is closed; addition is additive non-breaking per F7 §3.4 policy (new shape_id) |
| Default RP list length | 6 (extended) | Matches KPR-V; most modern KP practitioners |
| Sub-levels supported | 5 | Practical ceiling per KPR-III |
| Placidus mandatory | Yes, hard-required for KP | KPR-I.Ch.3 explicit; override produces warning |
| 249-number table source | KPR-IV Appendix B | Single authoritative table |
| Ayanamsa for KP | KP Ayanamsa (K.S. Krishnamurti's own, ≈ Lahiri + small delta) | KPR-I.Ch.2 specifies; E9 supports it as separate ayanamsa option |
| Query classification | Table of ~20 common queries; AI fallback for novel queries | Covers 95% of horary practice; AI handles edge cases |
| Sub-sub computation orb | No orb — discrete sub boundaries | Sub boundaries are exact in KP; no fuzzy matching |
| Level-5 conjunction orb | 5° | KPR-II.Ch.4 v.30 specifies "close conjunction, within 5 degrees" |
| Ordering of significators | Level 2 > 4 > 1 > 3 > 5 | KPR-II.Ch.4 v.23 explicit |
| Horary number range validation | 1-249 inclusive | Krishnamurti specified range |
| Time used for horary | User-provided OR server-now | User override matters for remote queries |

## 5. Component Design

### 5.1 New modules

```
src/josi/services/classical/
└── kp/
    ├── __init__.py
    ├── engine.py                        # KPEngine : ClassicalEngine
    ├── sub_lord.py                      # 243-sub table + deep levels
    ├── cuspal.py                        # cuspal sub-lord for 12 houses
    ├── significators.py                 # 5-level significator hierarchy
    ├── ruling_planets.py                # RP computation
    ├── horary_249.py                    # 249-number mapping + horary chart
    ├── query_analyzer.py                # CSL analysis for outcome prediction
    └── kp_ayanamsa.py                   # KP Ayanamsa (wrapper on swe)

src/josi/data/
├── kp_249_number_table.json             # 249 → longitude range
├── kp_query_house_map.json              # query-category → house map
└── kp_sub_table.json                    # 243-sub precomputed (optional cache)

src/josi/rules/kp/kp_reader/
├── significator_levels.yaml             # 5-level DSL rule
├── cuspal_sub_lord_analysis.yaml        # per-house outcome rule
├── horary_249_map.yaml                  # 249-number mapping as rule
└── ruling_planets_composition.yaml      # RP list assembly

src/josi/schemas/classical/output_shapes/
└── kp_analysis.py                       # NEW SHAPE (if accepted by F7 team)

src/josi/api/v1/controllers/
└── kp_controller.py
```

### 5.2 Proposed new output_shape: `kp_analysis`

```python
class KPCusp(BaseModel):
    model_config = ConfigDict(extra="forbid")
    house:      int = Field(..., ge=1, le=12)
    longitude:  float = Field(..., ge=0.0, lt=360.0)
    sign:       int = Field(..., ge=0, le=11)
    nakshatra_lord: str
    sub_lord:       str
    sub_sub_lord:   str | None = None

class KPSignificatorSet(BaseModel):
    model_config = ConfigDict(extra="forbid")
    house:    int = Field(..., ge=1, le=12)
    level_1:  list[str]                        # occupants
    level_2:  list[str]                        # occupants' nakshatra disposers
    level_3:  list[str]                        # owner
    level_4:  list[str]                        # owner's nakshatra disposers
    level_5:  list[str]                        # conjuncts
    ranked:   list[str]                        # by strength 2>4>1>3>5

class KPRulingPlanets(BaseModel):
    model_config = ConfigDict(extra="forbid")
    at:        datetime
    day_lord:  str
    asc_sign_lord:     str
    asc_nakshatra_lord: str
    asc_sub_lord:      str | None = None       # only in extended
    moon_sign_lord:    str
    moon_nakshatra_lord: str
    unique_rps:        list[str]               # deduplicated

class KPCuspalAnalysis(BaseModel):
    model_config = ConfigDict(extra="forbid")
    house:       int
    matter:      str                            # e.g., "marriage"
    csl:         str                            # the cuspal sub-lord planet
    signifies_primary:   list[int]              # which primary houses CSL signifies
    signifies_supporting: list[int]
    signifies_contra:    list[int]
    verdict:             str                    # "yes" | "no" | "mixed"
    confidence:          float = Field(..., ge=0.0, le=1.0)
    rationale:           str                    # narrative line

class KPAnalysis(BaseModel):
    model_config = ConfigDict(extra="forbid")

    chart_kind:     str                         # "natal" | "horary"
    ayanamsa:       str                         # "kp" | "lahiri" | other override
    cusps:          list[KPCusp]                # 12 entries
    planet_sub_lords: dict[str, str]            # planet -> sub-lord
    significators:  list[KPSignificatorSet]     # 12 entries (1 per house)
    ruling_planets: KPRulingPlanets
    cuspal_analyses: list[KPCuspalAnalysis]     # populated per-query
    details:        dict[str, Any] = Field(default_factory=dict)
```

**Why a new shape:** KP analysis combines structured positions (cusps, planet subs) + multi-level indexed sets (significators) + RPs + per-query analyses. Cramming into `structured_positions` means all structure goes into `details`, defeating the purpose of F7 typing.

**If F7 review rejects the new shape:** fall back to `structured_positions` with full KPAnalysis in `details`. All downstream code treats `details` as a typed dict (via Pydantic); UI loses shape validation but functionality preserved. **Recommendation: accept the new shape.**

### 5.3 Data model additions

No new tables. Compute rows in `technique_compute` with `technique_family_id='kp'`.

Index addition:
```sql
CREATE INDEX idx_kp_compute_chart
  ON technique_compute (chart_id, computed_at DESC)
  WHERE technique_family_id = 'kp';
```

### 5.4 API contract

```
GET /api/v1/charts/{chart_id}/kp/sub-lords
Response: TechniqueResult[KPAnalysis]  — with significators + cusps + RPs populated; cuspal_analyses empty until queried

GET /api/v1/charts/{chart_id}/kp/significators
Response: TechniqueResult[KPAnalysis] — focused on significators list

GET /api/v1/charts/{chart_id}/kp/ruling-planets?at=2026-04-20T10:00:00Z
Response: TechniqueResult[KPAnalysis] — RPs + time

POST /api/v1/charts/{chart_id}/kp/cuspal-analysis
Body: { "house": 7, "matter": "marriage" }
Response: TechniqueResult[KPAnalysis] with `cuspal_analyses` populated for that house

POST /api/v1/kp/horary
Body: {
  "number": 147,
  "at": "2026-04-20T14:30:00+05:30",
  "location": {"lat": 13.08, "lon": 80.27},
  "querent_question": "Will the marriage proposal succeed?",
  "matter": "marriage"
}
Response: TechniqueResult[KPAnalysis]
  with chart_kind="horary", ayanamsa="kp", and full cuspal analysis for matter
```

### 5.5 Internal Python interface

```python
# src/josi/services/classical/kp/engine.py

class KPEngine(ClassicalEngineBase):
    technique_family_id: str = "kp"
    default_output_shape_id: str = "kp_analysis"

    def __init__(self, calc: AstrologyCalculator, sub_table: KPSubTable,
                 number_table: KP249Table, query_map: KPQueryMap):
        ...

    async def compute_for_source(
        self, session, chart_id, source_id, rule_ids=None,
        *, analysis_scope: Literal["full","sub_lords_only","rps_only"] = "full",
    ) -> list[TechniqueComputeRow]: ...

    async def compute_horary(
        self, session, number: int, at: datetime, location: GeoLocation,
        matter: str | None = None,
    ) -> TechniqueResult[KPAnalysis]: ...

    async def analyze_cuspal(
        self, session, chart_id: UUID, house: int, matter: str,
    ) -> KPCuspalAnalysis: ...
```

## 6. User Stories

### US-E9.1: As a KP astrologer, I can see the sub-lord of every planet and cusp in my natal chart
**Acceptance:** `GET /api/v1/charts/{chart_id}/kp/sub-lords` returns KPAnalysis with 12 cusps + 9 planet subs; each matches JH KP-module output.

### US-E9.2: As a KP astrologer, I see the 5-level significator set for each house, ranked by strength
**Acceptance:** `GET /api/v1/charts/{chart_id}/kp/significators` returns 12 KPSignificatorSet entries. Ordering for house 7 on a published chart matches KPR-II Ch.4 Appendix Example 3.

### US-E9.3: As a KP astrologer, I can get Ruling Planets for the current moment or a specific moment
**Acceptance:** `?at=...` returns deduplicated RP list; default (no `at`) uses server now. RP composition matches KPR-III Ch.7 formula.

### US-E9.4: As a KP horary astrologer, I can cast a number-based horary chart
**Acceptance:** `POST /api/v1/kp/horary` with number 147 + moment + location returns full KPAnalysis with horary Ascendant at number 147's longitude; cuspal analysis for specified matter computed.

### US-E9.5: As a classical advisor, CSL analysis for marriage on a known published example matches
**Acceptance:** KPR-IV.Ch.5 Example 2 (horary chart "will the marriage happen") input reproduces verdict="yes", confidence ≥ 0.7.

### US-E9.6: As an engineer adding a 21st query category, I can add a YAML entry without engine code changes
**Acceptance:** editing `src/josi/data/kp_query_house_map.json` (adding `"litigation_outcome"` with house map) and reloading results in support for the new query type via POST body.

### US-E9.7: As an AI chat surface, KP outputs validate against `kp_analysis` JSON Schema (or fallback shape)
**Acceptance:** every engine output passes `fastjsonschema.compile(kp_analysis_schema)(output)`.

## 7. Tasks

### T-E9.1: 243-sub lord table
- **Definition:** `sub_lord.py` — precompute 243-sub zodiac table at startup; provide `sub_lord_at(longitude, level=2..5)`.
- **Acceptance:** 243 subs sum to 360.0° exactly (floating-point tolerance 1e-6); 10 longitude fixtures match KPR-II tables.
- **Effort:** 8 hours

### T-E9.2: Deep sub levels (3-5)
- **Definition:** Recursive sub-sub-sub computation; `sub_lord_at(lon, level=5)` returns full 5-tuple.
- **Acceptance:** 5-tuple for canonical longitude (e.g., Aries 2°13'20") = (ashwini, venus, venus, ketu, ketu) per KPR-III Ch.4 worked example.
- **Effort:** 4 hours

### T-E9.3: Cuspal sub-lord
- **Definition:** `cuspal.py` — Placidus cusps (from existing Swiss Ephemeris call); resolve sub-lord per cusp.
- **Acceptance:** 3 natal fixtures: CSLs match JH KP module exactly.
- **Effort:** 6 hours

### T-E9.4: 5-level significator hierarchy
- **Definition:** `significators.py` — compute L1-L5 sets; rank per §3.4.
- **Acceptance:** KPR-II Ch.4 Appendix Example 3: 5-level significator for house 7 matches published answer including ordering.
- **Effort:** 12 hours

### T-E9.5: Ruling Planets
- **Definition:** `ruling_planets.py` — day lord + Asc/Moon components; dedupe; extended toggle.
- **Acceptance:** 3 moment fixtures against KPR-III Ch.7 worked examples.
- **Effort:** 4 hours

### T-E9.6: 249-number table + horary casting
- **Definition:** `horary_249.py` — load number table JSON; given (number, moment, location), cast horary chart (real-sky planets + horary Ascendant).
- **Acceptance:** 10 numbers × 3 moments: horary Ascendant longitudes match KPR-IV Appendix table (verified by number boundaries).
- **Effort:** 10 hours

### T-E9.7: Query-category → house map
- **Definition:** `kp_query_house_map.json` with ~20 categories; loader module.
- **Acceptance:** All 20 categories load; primary/supporting/contra sets non-empty; no overlaps.
- **Effort:** 4 hours

### T-E9.8: Cuspal sub-lord analysis engine
- **Definition:** `query_analyzer.py` — given CSL and query-category, compute signify-primary/supporting/contra; derive verdict + confidence.
- **Acceptance:** KPR-IV Ch.5 Example 2 (marriage horary): verdict matches; confidence in [0.7, 1.0].
- **Effort:** 10 hours

### T-E9.9: KP Ayanamsa support
- **Definition:** Expose `kp_ayanamsa` as a selectable ayanamsa option; wire through AstrologyCalculator.
- **Acceptance:** computed positions with KP Ayanamsa differ from Lahiri by ~6'–8' (the Krishnamurti offset).
- **Effort:** 4 hours

### T-E9.10: KPAnalysis output shape
- **Definition:** Add `KPAnalysis` to `SHAPE_REGISTRY`; update F1 `output_shapes.yaml`; update F7 PRD as AMENDMENT; Pydantic model per §5.2.
- **Acceptance:** Shape registered; F7 test suite passes with 11 shapes; `kp_analysis` returns valid schema from F7 endpoint.
- **Effort:** 4 hours (+ F7 amendment coordination)
- **Depends on:** F7 owner acceptance

### T-E9.11: Rule YAMLs
- **Definition:** Significator, cuspal analysis, horary mapping, RP composition as rule YAMLs under `src/josi/rules/kp/kp_reader/`. Each cites KPR volume/chapter/verse.
- **Acceptance:** All load via `poetry run validate-rules`.
- **Effort:** 10 hours

### T-E9.12: KPEngine assembly
- **Definition:** `engine.py` ties all modules; implements `compute_for_source` + `compute_horary` + `analyze_cuspal`.
- **Acceptance:** Integration test: natal KP analysis for 5 charts → 5 technique_compute rows; horary for 3 example numbers → 3 rows.
- **Effort:** 14 hours

### T-E9.13: API controllers + routing
- **Definition:** `kp_controller.py` with all listed endpoints; register in `api/v1/__init__.py`.
- **Acceptance:** OpenAPI documents all endpoints; 5 curl tests pass.
- **Effort:** 10 hours

### T-E9.14: Golden fixtures
- **Definition:** 5 natal charts: full KPAnalysis including all cusps, significators, RPs. 5 horary charts: full KPAnalysis + cuspal analysis for specified matter.
- **Acceptance:** All assertions green; every element hand-verified against KP Reader examples.
- **Effort:** 24 hours

### T-E9.15: Performance + caching
- **Definition:** Full KP analysis P95 < 800 ms uncached; < 200 ms cached. Horary chart P95 < 1.5 s.
- **Acceptance:** Locust benchmark passes.
- **Effort:** 6 hours

### T-E9.16: Documentation
- **Definition:** CLAUDE.md KP section; KP quickstart doc for new engineers.
- **Acceptance:** Merged.
- **Effort:** 4 hours

## 8. Unit Tests

### 8.1 Sub-lord table

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_sub_lord_table_sums_to_360` | 243 subs | sum of arcs = 360.0 ± 1e-9 | mathematical invariant |
| `test_sub_lord_aries_0deg_0min` | 0.0 | nakshatra=ashwini, sub=ketu | Ashwini starts with ketu (own lord) |
| `test_sub_lord_aries_46min_40sec_boundary` | 0°46'40" exact | transitions from ketu sub to venus sub | boundary |
| `test_sub_lord_pisces_end` | 359.999 | nakshatra=revati, sub=mercury | end of zodiac |
| `test_sub_lord_krittika_own_lord_sun` | first point of krittika | sub=sun | own-lord-first ordering |
| `test_sub_lord_cached_247_subs_tested` | 243 random longitudes | all return valid (nak_lord, sub_lord) pair | stress |

### 8.2 Deep sub levels

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_level_5_tuple_returned` | any longitude | 5-tuple (L1..L5) | depth |
| `test_level_5_kpr_example` | KPR-III example longitude | 5-tuple matches Krishnamurti published | classical |
| `test_sub_sub_arc_proportional` | Venus sub within Ashwini, sub-sub Venus | sub_sub_arc = 2°13'20" × (20/120) = 22'13.33" | proportion |
| `test_level_5_performance` | 1000 lookups | total < 50 ms | speed |

### 8.3 Cuspal sub-lord

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_csl_12_cusps_computed` | natal chart | 12 CSLs (all non-null) | completeness |
| `test_csl_placidus_hard_required` | chart with koch=true | warning emitted; still uses placidus | mandatory |
| `test_csl_matches_jh_fixture` | 3 charts | CSLs match JH KP output | cross-tool |
| `test_csl_on_sign_boundary` | cusp exactly at sign boundary | resolves to later sign's first nakshatra | edge case |

### 8.4 Significators

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_level_1_occupants_of_house` | planets in house 7 | L1 = those planets | basic |
| `test_level_2_nakshatra_disposers` | L1 planets' nakshatra lords | L2 correct | §3.4 |
| `test_level_3_house_owner` | 7th cusp sign Leo | L3 = sun | simple |
| `test_level_4_owner_nakshatra_lord` | Sun in Ashwini | L4 = ketu | basic |
| `test_level_5_conjuncts_within_5_deg` | planets within 5° of L3 or L4 | L5 correct | KPR-II 4.30 orb |
| `test_significator_ranking_order` | any house | ranked list order = [L2+L4+L1+L3+L5] | KPR-II 4.23 |
| `test_kpr_appendix_example_3_house_7` | KPR-II Ch.4 App Ex 3 | matches published | canonical |
| `test_12_houses_all_have_sig_sets` | any chart | 12 KPSignificatorSet in output | completeness |

### 8.5 Ruling Planets

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_rp_sunday_includes_sun` | Sunday moment | day_lord = sun; sun in unique_rps | basic |
| `test_rp_extended_adds_asc_sub_lord` | extended=true | 6 entries before dedupe | KPR-V |
| `test_rp_deduplicated` | chart where Asc sign lord = Moon sign lord | unique_rps shorter than raw 6 | dedup |
| `test_rp_moment_now_vs_explicit` | no `at` vs `at=now()` | identical outputs | defaulting |
| `test_rp_kpr_example` | KPR-III Ch.7 example moment | RPs match | canonical |

### 8.6 Horary (249-number)

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_number_1_is_aries_0_0_to_0_46_40` | table lookup | correct range | table integrity |
| `test_number_249_is_pisces_end` | table lookup | 359°13'20" to 360° | table integrity |
| `test_number_147_longitude_specific` | lookup | a specific mid-zodiac value | random check |
| `test_horary_ascendant_replaces_astronomical` | number=100, moment M | horary Asc = number-100 longitude; planet positions = real at M | core algorithm |
| `test_horary_invalid_number_0_rejects` | number=0 | 400 error | validation |
| `test_horary_invalid_number_250_rejects` | number=250 | 400 error | validation |
| `test_horary_number_boundary_exact` | number at boundary | resolves deterministically to lower-bound range | determinism |

### 8.7 Cuspal analysis for outcome

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_marriage_csl_signifies_2_7_11` | CSL signifies {2,7,11} | verdict="yes", confidence ≥ 0.8 | primary houses |
| `test_marriage_csl_signifies_1_6_10` | CSL signifies contra | verdict="no", confidence ≥ 0.7 | contra houses |
| `test_marriage_csl_mixed` | CSL signifies {7, 6} | verdict="mixed", confidence ~ 0.5 | mixed |
| `test_kpr_iv_ch5_ex2_marriage` | KPR-IV Ch.5 Ex 2 input | verdict="yes" | canonical |
| `test_career_query_different_houses` | career query | uses {2,6,10,11} primary | query map |
| `test_all_20_queries_computable` | loop all | each returns KPCuspalAnalysis | completeness |

### 8.8 Integration

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_kp_analysis_output_validates_schema` | output | passes kp_analysis JSON Schema | F7 parity |
| `test_kp_engine_idempotent` | call twice | 1 technique_compute row (ON CONFLICT) | F2 |
| `test_kp_horary_end_to_end` | POST /kp/horary | full KPAnalysis returned with verdict | E2E |
| `test_kp_ayanamsa_differs_from_lahiri` | same chart | positions diverge by ~6'-8' | ayanamsa wiring |
| `test_kp_natal_vs_horary_distinguishable` | chart_kind field | correctly set | distinction |
| `test_kp_source_id_exclusively_kp_reader` | audit | all KP rules source_id='kp_reader' | single-source policy |

## 9. EPIC-Level Acceptance Criteria

- [ ] 243-sub zodiac table precomputed and tested; sums to 360° exact
- [ ] Deep sub levels (2-5) computable for any longitude
- [ ] Cuspal sub-lord for all 12 Placidus cusps; Placidus hard-required with override warning
- [ ] 5-level significator hierarchy per house with correct ranking (2>4>1>3>5)
- [ ] Ruling Planets composition (standard 4 + extended 6) with deduplication
- [ ] 249-number horary table loaded as immutable static JSON
- [ ] Horary chart casting: number → horary Ascendant + real-sky planets
- [ ] Cuspal sub-lord analysis for 20 common query categories
- [ ] KP Ayanamsa supported as selectable option
- [ ] New output shape `kp_analysis` proposed to F7; accepted OR fallback to `structured_positions` with typed details
- [ ] All output validates against chosen shape's JSON Schema
- [ ] API endpoints live: `/kp/sub-lords`, `/kp/significators`, `/kp/ruling-planets`, `/kp/cuspal-analysis`, `/kp/horary`
- [ ] Golden chart suite: 5 natal + 5 horary charts with full KPAnalysis hand-verified; ~300 assertions green
- [ ] Rule YAMLs under `src/josi/rules/kp/kp_reader/` — all cite KPR volume/chapter/verse
- [ ] Unit test coverage ≥ 90% across `kp/` package
- [ ] Integration tests cover full path (compute → persist → aggregate → API)
- [ ] Performance per §7 T-E9.15 under budget
- [ ] CLAUDE.md updated with KP section
- [ ] Single-source policy audit: every KP rule's `source_id = 'kp_reader'`

## 10. Rollout Plan

- **Feature flag:** `enable_kp_engine` — off at merge, on in P2 after internal QA with 2 KP-trained advisors verifying 20 charts.
- **Shadow compute:** 2 weeks compute-and-log for every natal chart; compare against JH KP module on 100 random charts; < 5% divergence required.
- **Backfill strategy:** lazy on request; backfill top 10k active charts during off-peak 24 hours before public launch.
- **Rollback plan:** disable feature flag; endpoints return 501; redeploy old code. Data in `technique_compute` retained.

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| 243-sub table transcription error | Medium | Critical (corrupts all KP output) | Mathematical invariants (sums, boundaries) tested; compare against JH numeric output on 100 longitudes |
| 249-number table transcription error | Medium | High | Cross-reference KPR-IV Appendix with Hariharan reproduction; unit test each boundary |
| Placidus house computation divergence vs JH | Medium | High | Use Swiss Ephemeris Placidus (same as JH); verify on 10 charts |
| Significator ranking disputed by KP sub-schools | Low | Medium | Ship KPR-II.Ch.4.v23 ordering; allow override flag `?sig_order=standard\|alternative` in E9b |
| KP Ayanamsa deviation from Lahiri misunderstood | Medium | Medium | UI shows ayanamsa label; document in response `details.ayanamsa` |
| Query category expansion requires code change | Low | Low | Category map is editable JSON; loader reloads without deploy in dev mode |
| Horary number edge cases at sub boundaries | Low | Medium | Deterministic lower-bound rule; explicit unit tests at boundaries |
| Extended RP list breaks legacy users expecting 4 | Low | Low | Query param `?extended=false` preserves legacy |
| F7 shape addition rejected | Medium | Medium | Fallback to `structured_positions` with typed details; no functionality loss |
| Level-5 conjunction orb (5°) disagrees with some practitioners | Low | Low | Configurable; document |
| Krishnamurti's own later writings (Vol V, VI) contradict Vol II | Medium | Medium | Treat as single corpus; use later volume where explicit contradiction; document in YAML `notes` |
| Performance degradation at level-5 lookups across chart+query load | Medium | Medium | Precompute per-chart significator set; cache KPAnalysis with invalidation on source-pref change |

## 12. References

- Master spec: [`docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`](../../../superpowers/specs/2026-04-19-classical-techniques-expansion-design.md) §2.2 (kp technique_family)
- F1 dims: [`../P0/F1-star-schema-dimensions.md`](../P0/F1-star-schema-dimensions.md) — `source_id='kp_reader'`, `technique_family_id='kp'`
- F2 fact tables: [`../P0/F2-fact-tables.md`](../P0/F2-fact-tables.md)
- F6 Rule DSL: [`../P0/F6-rule-dsl-yaml-loader.md`](../P0/F6-rule-dsl-yaml-loader.md)
- F7 Output shapes: [`../P0/F7-output-shape-system.md`](../P0/F7-output-shape-system.md) — proposal to add `kp_analysis` as 11th shape
- F8 Aggregation: [`../P0/F8-technique-result-aggregation-protocol.md`](../P0/F8-technique-result-aggregation-protocol.md)
- E1a Multi-Dasa v1 — Vimshottari proportions reused
- E10 Prasna/Horary — consumes KP engine for one of two first-class horary methods
- **Classical source (single authority):**
  - K.S. Krishnamurti, *KP Reader Vol I: Krishnamurti Paddhati — Introduction*, 1971, Krishnamurti Publications — Ch. 1-3 (foundations, Placidus, KP Ayanamsa)
  - K.S. Krishnamurti, *KP Reader Vol II: Krishnamurti Paddhati — Fundamental Principles of Astrology*, 1972 — Ch. 1 (sub-lord table), Ch. 2 (cuspal sub-lord), Ch. 4 (5-level significators), Ch. 6 (cuspal analysis for outcome)
  - K.S. Krishnamurti, *KP Reader Vol III: Krishnamurti Paddhati — The Significators and the Stellar System*, 1974 — Ch. 4 (deep sub levels), Ch. 7-8 (Ruling Planets)
  - K.S. Krishnamurti, *KP Reader Vol IV: Krishnamurti Paddhati — Horary Astrology*, 1977 — Ch. 1-3 (249-number method), Ch. 5 (worked examples), Appendix B (249-number table)
  - K.S. Krishnamurti, *KP Reader Vol V: Krishnamurti Paddhati — Case Studies*, 1979 — Ch. 3 (extended RPs including Asc sub-lord)
  - K.S. Krishnamurti, *KP Reader Vol VI: Krishnamurti Paddhati — Advanced Technique*, 1983 — commentary and synthesis
- **Secondary (verification only):**
  - K.P. Hariharan, *KP Sub Theory*, ~1995
  - Kanak Bosmia, *KP Reader Companion*, ~2010
- **Reference implementations:**
  - Jagannatha Hora 7.41 — "KP" tab
  - KP Astro (commercial software; primary India-market KP tool)
  - Janmakundali Pro (KP module)
