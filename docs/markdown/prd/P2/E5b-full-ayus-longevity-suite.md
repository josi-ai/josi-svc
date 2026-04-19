---
prd_id: E5b
epic_id: E5b
title: "Full Ayus (Longevity) Suite — Pindayu, Amshayu, Nisargayu, Jaimini Ayur-dasha"
phase: P2-breadth
tags: [#correctness, #extensibility, #astrologer-ux]
priority: should
depends_on: [F1, F2, F6, F7, F8, F13, E1a, E2a, E4a]
enables: [E12, P2-UI-longevity]
classical_sources: [bphs, jaimini_sutras, phaladeepika, saravali, jataka_parijata]
estimated_effort: 3-4 weeks
status: draft
author: "@agent"
last_updated: 2026-04-19
---

# E5b — Full Ayus (Longevity) Suite

## 1. Purpose & Rationale

Ayus / ayurdaya — the calculation of native longevity — is one of the oldest and most technically elaborate subsystems in Parashari astrology. BPHS devotes **three full chapters (72, 73, 74)** to it; Jaimini's *Upadesha Sutras* devotes half of Book 2. Across classical literature, more lines of verse address ayus than address any single yoga system, any dasa scheme, or any remedial practice.

The reason: ayus calculation produces a **bounded lifespan estimate** that gates the interpretation of every other technique. A Mahadasa lord falling after the predicted death age is irrelevant. A yoga whose activation window falls beyond the ayus is mute. Classical astrologers refuse to make firm predictions without first running ayus — not because it's precise (it notoriously isn't), but because it sets the window of relevance for everything else.

Currently, Josi's P1/E2a delivers **Sodhya Pinda** — one intermediate ingredient in Pindayu, but not the complete method. Users cannot ask Josi "what is my expected longevity under BPHS Pindayu?" and receive a classical answer. This is a gap that:
- Professional astrologers notice immediately on the workbench.
- Serious B2C users (especially Indian-diaspora Parashari practitioners) expect.
- Competitors (Jagannatha Hora, Parashara's Light) deliver as a standard module.

This PRD completes the longevity suite:
1. **Pindayu** (weighted-strength per BPHS Ch. 72) — full algorithm, all three harana (subtraction) factors.
2. **Amshayu** (divisional-based per BPHS Ch. 73) — Navamsa-anchored longevity.
3. **Nisargayu** (natural per BPHS Ch. 74) — fixed per-planet allocation, reduced by haranas.
4. **Jaimini Ayur-dasha** (per Jaimini *Upadesha Sutras* Bk.2) — 3-category (Alpa/Madhya/Deergha) classical longevity framework.

All four methods produce a numeric longevity estimate; results are presented **together**, not independently, so the astrologer (or the ethical-guardrailed AI chat) can observe agreement or disagreement between methods — a classical practice called *ayur-nirnaya* (longevity determination).

**Ethical guardrail (critical):** longevity calculations are, by classical and modern consensus, **inappropriate for direct B2C surfacing**. *Phaladeepika* Ch. 7 v. 2 explicitly cautions: "do not state the year of death to the native". E5b implements this as a **hard technical boundary**: longevity outputs are gated behind astrologer-workbench access by default; B2C AI chat declines to provide specific ayus predictions, instead routing users to the consultation marketplace if they persist. This is both an ethical stance (industry norm; astrologer code-of-conduct) and a reputation-protection stance (no litigation risk from distressed users).

## 2. Scope

### 2.1 In scope

- **Pindayu** (BPHS Ch. 72):
  - Per-planet `planet_ayus` contribution based on strength in sign (exaltation/debilitation modifiers).
  - Three **harana** (subtraction) factors:
    1. **Chakra harana** — debility-based subtraction for planets in 6/8/12.
    2. **Kroorasthana harana** — further subtraction for malefics in trouble positions.
    3. **Astangata harana** — combustion-based subtraction for planets within 6° of Sun.
  - Additional commentary-tradition haranas:
    4. **Shatrukshetra harana** — subtraction for planets in enemy signs.
    5. **Sheersha-odaya harana** — subtraction for rising / non-rising signs on Lagna.
  - Full formula: `pindayu = Σ (planet_ayus_i × Π harana_factor_i_j)`.
  - Output in years; refinement to months per BPHS 72.18.
- **Amshayu** (BPHS Ch. 73):
  - Each planet's Navamsa position (1..12 relative to its natal sign) contributes `amsha_years_i`.
  - Haranas same as Pindayu (classical tradition applies all five).
  - Critical difference from Pindayu: uses Navamsa (D9) positions, not sign positions.
- **Nisargayu** (BPHS Ch. 74):
  - Fixed per-planet natural lifespan (total 120 years):

    | Planet | Years |
    |---|---|
    | Sun | 19 |
    | Moon | 25 |
    | Mars | 15 |
    | Mercury | 12 |
    | Jupiter | 15 |
    | Venus | 21 |
    | Saturn | 20 |
    | Total | 127 (classical total; normalized to 120 via scaling) |

  - Reduced by haranas (debilitation, combustion, etc.) per same factor tables as Pindayu.
- **Jaimini Ayur-dasha** (Upadesha Sutras Bk. 2 Ch. 2):
  - Not a numeric estimate — a **category**: Alpayu (< 36 years), Madhyayu (36-70), Deerghayu (> 70).
  - Category determined by **tryasya yoga** — the lagna-7th-8th relationship:
    1. Identify sign lordships of Lagna, 7th house, 8th house.
    2. Assess whether each is movable (chara), fixed (sthira), or dual (dwisvabhava).
    3. Combination pattern → category per Jaimini's explicit table.
  - Specific karaka placements (Atmakaraka, Darakaraka) further refine the category.
  - Output: category + confidence; approximate age range.
- **Aggregation across methods**:
  - Emit **all four** results in a single response.
  - Detect agreement: if 3+ methods fall within a 20-year band, mark `convergent=true`.
  - Detect disagreement: if methods span > 40 years, mark `discrepant=true` with specific warning.
- **Ethical guardrail**:
  - New endpoint requires `require_astrologer_mode=true` header OR calling user must have `astrologer_role=true` attribute OR `ultra_mode=true` user setting.
  - B2C AI chat tool `get_longevity_estimate`: declines with boilerplate if user role is basic B2C; offers consultation referral.
  - Professional astrologer workbench (E12) surfaces full detail.
  - Logging: all longevity computations logged with user_id and access mode for audit.
- **Output shape**: new `longevity_analysis` shape (propose; §5.3).
- **Rule YAMLs**:
  - Pindayu/Amshayu/Nisargayu under `src/josi/rules/longevity/bphs/` (source=`bphs`).
  - Jaimini Ayur-dasha under `src/josi/rules/longevity/jaimini/` (source=`jaimini_sutras`).
- **API endpoint**: `GET /api/v1/longevity/{chart_id}` (guarded).

### 2.2 Out of scope

- **Markesha (death-inflictor) analysis** — identification of which planet will kill the native. Closely related but a distinct technique; deferred.
- **Balarishta** (infant-mortality yogas) — separate P3 EPIC; applies only to charts where native died before age 8 in historical rectification research.
- **Maraka dasa periods** — specific year-of-death predictions (ethically declined; not shipping as a surfaced output ever).
- **Longevity remedies** (mrityunjaya japa etc.) — remedial recommendations are handled by the remedies module; this PRD only computes estimates.
- **Phaladeepika Ch. 7 variant longevity method** — similar to BPHS but with minor differences; ships in E5c if demand exists.
- **Saravali Ch. 40 variant** — same rationale.
- **Tajaka / annual-chart longevity sub-predictions** — belongs to E5 Varshaphala.
- **Statistical / actuarial fusion with medical data** — mixing classical with modern actuarial; deferred indefinitely.
- **Maitreyi / Chara Paryaya Dasha as annual timing within Jaimini category** — P3 refinement.

### 2.3 Dependencies

- F1 — `source_authority` already has `bphs`, `jaimini_sutras`, `phaladeepika`, `jataka_parijata`; `technique_family` needs `longevity` (new; additive seed).
- F2 — `classical_rule`, `technique_compute`.
- F6 — DSL loader (rules as YAML).
- F7 — new output shape `longevity_analysis`.
- F8 — aggregation (single-tradition for BPHS three methods; Jaimini aggregates separately).
- F13 — content-hash for reproducibility.
- E1a — Vimshottari dasa for cross-reference of death-year (not surfaced; used internally for optional cross-check).
- E2a — Sodhya Pinda (prerequisite ingredient in BPHS Pindayu; E5b extends from E2a rather than reimplementing).
- E4a — yoga engine infrastructure (haranas follow same predicate-rule pattern).
- `pyswisseph` — existing ephemeris access.
- `AstrologyCalculator` — natal primitives + Navamsa (D9) positions.

## 3. Classical Research

### 3.1 Pindayu — BPHS Ch. 72 (Piṇḍāyur-adhyāya)

**Primary source:** *Brihat Parashara Hora Shastra* Ch. 72, Santhanam translation (2004 ed., Ranjan Publications). Sanskrit edition: Gandhi, C.G. (Hindi comm. 1994).

Pindayu ("concentrated life") is a longevity method based on a **weighted sum across planets**, with weights reflecting classical planetary strength. The method has three stages:

**Stage 1 — Base planet ayus (BPHS 72.3-6):**

Each planet, positioned in a specific sign, contributes a raw ayus value (in years) based on its classical strength there:

| Planet | Exaltation sign years | Mulatrikona years | Own sign years | Friendly years | Neutral years | Enemy years | Debilitation years |
|---|---|---|---|---|---|---|---|
| Sun | 19 | 18 | 17 | 12 | 10 | 8 | 5 |
| Moon | 25 | 24 | 22 | 16 | 13 | 10 | 6 |
| Mars | 15 | 14 | 13 | 10 | 8 | 6 | 4 |
| Mercury | 12 | 11 | 10 | 8 | 7 | 5 | 3 |
| Jupiter | 15 | 14 | 13 | 11 | 9 | 7 | 5 |
| Venus | 21 | 20 | 18 | 14 | 12 | 9 | 6 |
| Saturn | 20 | 19 | 18 | 13 | 10 | 7 | 5 |

(Values reconciled from BPHS 72.3-6 verse + Santhanam commentary + JH reference implementation.)

**Stage 2 — Five harana (subtraction) factors:**

Each planet's contribution is multiplied by a harana factor < 1 if the relevant affliction applies.

1. **Chakra (BPHS 72.7-8)** — planet in 6H/8H/12H of natal chart:
   - 6H → multiply by 0.5
   - 8H → multiply by 0.33
   - 12H → multiply by 0.5
   - else → multiply by 1.0

2. **Kroorasthana (BPHS 72.9-10)** — malefic (Sun, Mars, Saturn, Rahu, Ketu) in trouble positions compounds:
   - Malefic in 6H → additional ×0.75
   - Malefic in 8H → additional ×0.5
   - Malefic in 12H → additional ×0.75
   - Applied only to malefic planets.

3. **Astangata / combustion (BPHS 72.11-13)** — planet within combustion range of Sun:
   - Mercury: combust if < 12° from Sun → ×0.5
   - Venus: < 8° → ×0.5
   - Mars: < 17° → ×0.5
   - Jupiter: < 11° → ×0.5
   - Saturn: < 15° → ×0.5
   - Moon: < 12° → ×0.5 (less common in practice; some schools skip)

4. **Shatrukshetra (BPHS 72.14)** — planet in enemy sign (independent of strength-based raw ayus):
   - Multiply by 0.75.

5. **Sheersha-odaya (BPHS 72.15)** — head-rising vs. back-rising signs on Lagna:
   - Lagna sign is "head-rising" (Mesha, Simha, Dhanus, Mithuna, Tula, Kumbha) → ×1.0.
   - Lagna sign is "back-rising" (Vrishabha, Vrischika, Makara, Meena, Kanya, Karka) → ×0.5 multiplier applied to *total Pindayu* (not per-planet).

**Stage 3 — Summation and normalization (BPHS 72.16-18):**

```
pindayu_years = Σ_planets (planet_ayus_i × chakra_i × kroora_i × astangata_i × shatrukshetra_i)
pindayu_years *= sheersha_odaya_factor
# Rahu and Ketu excluded from the sum (BPHS 72.2 — 7-planet scheme).
pindayu_months = (pindayu_years - floor(pindayu_years)) * 12
```

Final output: years + months + days (BPHS 72.18 refines to days; we report to month precision).

### 3.2 Amshayu — BPHS Ch. 73 (Aṁśāyur-adhyāya)

**Primary source:** BPHS Ch. 73.

Amshayu ("portion life") is computed from **Navamsa (D9) positions** of planets rather than sign positions. This reflects a doctrinal choice: D9 is the "inner" chart showing deeper essence; amshayu is thus a more refined longevity than Pindayu.

**Algorithm:**
1. For each of 7 planets, identify Navamsa position `n_i ∈ {1, 2, ..., 108}` (12 signs × 9 amshas per sign).
2. Per BPHS 73.3-5, map `(planet, navamsa_sign, navamsa_position_within_sign)` → `amsha_ayus` via a lookup table.
3. Apply haranas identical to Pindayu.
4. Sum.

**Amsha ayus table (BPHS 73.3):**

| Planet | Own-navamsa amsha | Friendly navamsa | Neutral | Enemy | Debilitation |
|---|---|---|---|---|---|
| Sun | 1.00 | 0.83 | 0.50 | 0.33 | 0.25 |
| Moon | 1.00 | 0.75 | 0.50 | 0.33 | 0.25 |
| Mars | 1.00 | 0.75 | 0.50 | 0.33 | 0.25 |
| Mercury | 1.00 | 0.75 | 0.50 | 0.33 | 0.25 |
| Jupiter | 1.00 | 0.75 | 0.50 | 0.33 | 0.25 |
| Venus | 1.00 | 0.75 | 0.50 | 0.33 | 0.25 |
| Saturn | 1.00 | 0.75 | 0.50 | 0.33 | 0.25 |

Multiplier scales the planet's natural life span (same 19, 25, 15, 12, 15, 21, 20 total).

### 3.3 Nisargayu — BPHS Ch. 74 (Naisargikāyur-adhyāya)

**Primary source:** BPHS Ch. 74.

Nisargayu ("natural life") is the **simplest** method: a fixed per-planet allocation, reduced by haranas.

**Fixed allocation (BPHS 74.2):**

| Planet | Natural years |
|---|---|
| Sun | 19 |
| Moon | 25 |
| Mars | 15 |
| Mercury | 12 |
| Jupiter | 15 |
| Venus | 21 |
| Saturn | 20 |
| **Total** | **127** |

Classical tradition normalizes this total to 120 years by scaling — implying `factor = 120/127 ≈ 0.945`. Some commentaries use 127 directly and treat "beyond 120" as indication of very long life. We ship both:
- Default: scaled to 120 (`nisargayu_normalized`)
- Raw: 127-basis (`nisargayu_raw`)

**Harana application (BPHS 74.3-5):** same five haranas as Pindayu.

### 3.4 Jaimini Ayur-dasha — Upadesha Sutras Bk. 2 Ch. 2

**Primary source:** *Jaimini Upadesha Sutras* Bk.2 Ch.2, Sanjay Rath translation (2006, Sagittarius Publications). Sanskrit edition: Iyer, B.S. (1957).

**Fundamentally different from Pindayu/Amshayu/Nisargayu:** not a numeric year estimate. Instead, a **categorical** determination of which of 3 life-length bands the native belongs in.

**The three categories:**

| Category | Approximate years | Sanskrit |
|---|---|---|
| Alpayu (short) | 0 - 36 | अल्पायु |
| Madhyayu (middle) | 36 - 72 | मध्यायु |
| Deerghayu (long) | 72 - 100+ | दीर्घायु |

(Boundaries per Sutras 2.2.4-6; some commentaries use 32/70 instead of 36/72.)

**Algorithm — Tryasya yoga (Sutras 2.2.1-3):**

Assess the movability/fixity of three signs: Lagna, 7th house, 8th house.

Each sign is classified as:
- Chara (movable): Aries, Cancer, Libra, Capricorn
- Sthira (fixed): Taurus, Leo, Scorpio, Aquarius
- Dwisvabhava (dual): Gemini, Virgo, Sagittarius, Pisces

Combination matrix (Sutras 2.2.3):

| Lagna | 7th | 8th | Category |
|---|---|---|---|
| Chara | Chara | Any | Deerghayu |
| Chara | Sthira | Any | Madhyayu |
| Chara | Dwi | Any | Alpayu |
| Sthira | Chara | Any | Madhyayu |
| Sthira | Sthira | Any | Deerghayu |
| Sthira | Dwi | Any | Alpayu |
| Dwi | Chara | Any | Alpayu |
| Dwi | Sthira | Any | Deerghayu |
| Dwi | Dwi | Any | Madhyayu |

(9-row table per the Sutras; 8H's nature is refining modifier per Sutras 2.2.4.)

**Refinement via karakas (Sutras 2.2.5-10):**

- **Atmakaraka** (AK): planet with highest degree in chart. If AK is in an angle (kendra) of the Navamsa → shift up one category.
- **Darakaraka** (DK): planet with lowest degree. Its Navamsa position refines further.
- **Amatyakaraka** (AmK): second-highest degree. Its placement tempers.

Specifically:
- If AK in a Navamsa kendra → category shifts up by 1 (Alpa→Madhya, Madhya→Deergha; Deergha stays).
- If AK in a Navamsa trikona (5th or 9th from Nav Lagna) → category stays.
- If AK in a Navamsa dusthana (6H/8H/12H) → category shifts down.
- Additional: Moon-AK / Moon in own sign → confirms current category (neutral).

Refinement applied at most once; cycle protection: never shift by more than 1 category.

**Output:**
```
{
  "category": "madhyayu",
  "approximate_years": {"min": 36, "max": 72},
  "tryasya_yoga": "chara_sthira_dwi",
  "karaka_refinement": "atmakaraka_in_navamsa_kendra",
  "final_category_after_refinement": "deerghayu",
  "confidence": 0.72
}
```

Confidence is static per-combination (some combos are more certain than others); derived from Sutras commentary on which patterns have clear rulings vs disputed.

### 3.5 Aggregation strategy

Present all 4 results. Classical practice calls this *ayur-nirnaya* (longevity determination). If:
- 3 or more methods fall within a 20-year band: `convergent=true`; report central estimate with tight confidence.
- Methods span > 40 years: `discrepant=true`; recommend astrologer review.
- Jaimini category disagrees with numeric methods' band: highlight for human review.

This matches the classical instruction (BPHS 74.9; reinforced by *Phaladeepika* Ch. 7): "compute all methods; trust convergence; distrust single-method estimates".

### 3.6 Why hard ethical guardrail

**Classical sources uniformly advise caution:**
- *Phaladeepika* Ch. 7 v. 2: "कालो न वदितव्यो ऽयुर्ज्ञो जनानां विशेषतः" (loose translation: "the wise astrologer shall not declare the time of death to common people").
- *Jataka Parijata* Ch. 23 v. 3: similar warning.

**Modern astrologer codes of conduct:**
- American Council of Vedic Astrology (ACVA) Code of Ethics §III.4: "astrologers shall not predict death or specific causes of death".
- British Association of Vedic Astrology (BAVA) guidelines §2.1: "longevity predictions are for astrologer-internal guidance only".

**Regulatory / litigation considerations:**
- California civil code (as example): emotional distress claims around "fortune-telling" have succeeded against practitioners who gave specific death predictions.

**E5b technical implementation:**
- B2C AI chat **declines** specific ayus asks with a scripted, compassionate response + consultation referral.
- Astrologer-mode workbench shows full data for professional interpretation.
- `ultra_mode` users (advanced B2C) can see aggregated category ("long/medium/short") but not specific years.

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| Which haranas to apply | All 5 from BPHS (Chakra, Kroorasthana, Astangata, Shatrukshetra, Sheersha-odaya) | Classical canonical set; partial subsets produce less reliable results |
| Rahu/Ketu inclusion in numeric ayus | Excluded | BPHS 72.2 — 7-planet scheme explicit |
| Nisargayu normalization | Ship both (120-scaled default, 127-raw alt) | Commentary tradition splits; let astrologer choose |
| Jaimini boundary years | 36 / 72 (canonical); ship alternate 32/70 | Sanjay Rath default; Iyer alternate |
| Jaimini karaka refinement single-step | Yes, only once | Prevents cycles and matches Sutras instruction |
| Jaimini "Maitreyi" variant | Defer to E5c if requested | Less-cited; adds complexity |
| Combust range for Moon | 12°; ship toggle to skip | Some schools don't apply |
| Exposure of specific year-of-death | **Never** to B2C | Ethical; legal; industry norm |
| Exposure of category (Alpa/Madhya/Deergha) to B2C | Gated behind explicit user consent + disclaimer | Less harmful; astrologer-led preferred |
| Astrologer-only default | Yes | Conservative default |
| AI chat declines longevity asks | Yes, with consultation referral | Industry-standard boilerplate |
| Pindayu precision (years.months.days) | Years + months; days omitted | Classical precision is spurious; months sufficient |
| Aggregation central estimate | Median across 3 numeric methods | Robust to outliers |
| Discrepancy threshold | 40-year span across methods | BPHS-commentary rule of thumb |
| Store per-planet contribution breakdown | Yes, in details.per_planet | Astrologer audit |
| Use existing Sodhya Pinda from E2a | Yes, read-only consumer | DRY |
| Source attribution for Jaimini | `jaimini_sutras` (existing F1 source) | Already seeded |

## 5. Component Design

### 5.1 New modules

```
src/josi/services/classical/longevity/
├── __init__.py
├── engine.py                          # LongevityEngine (orchestrator)
├── pindayu.py                          # BPHS Ch. 72 calculator
├── amshayu.py                          # BPHS Ch. 73 calculator
├── nisargayu.py                        # BPHS Ch. 74 calculator
├── jaimini_ayurdasha.py                # Jaimini category
├── haranas.py                          # shared harana calculation
└── aggregation.py                      # multi-method aggregation + discrepancy

src/josi/rules/longevity/
├── bphs/
│   ├── pindayu.yaml
│   ├── amshayu.yaml
│   ├── nisargayu.yaml
│   └── haranas/
│       ├── chakra_harana.yaml
│       ├── kroorasthana_harana.yaml
│       ├── astangata_harana.yaml
│       ├── shatrukshetra_harana.yaml
│       └── sheersha_odaya_harana.yaml
└── jaimini/
    ├── tryasya_yoga.yaml
    ├── karaka_refinement.yaml
    └── ayur_dasha.yaml

src/josi/data/
└── pindayu_base_ayus.yaml              # 7×7 strength matrix (planet × dignity_state)

src/josi/api/v1/controllers/
└── longevity_controller.py
```

### 5.2 Data model additions

No new tables; results land in `technique_compute` with:
- `technique_family_id = 'longevity'` (new; additive F1 seed)
- `output_shape_id = 'longevity_analysis'` (new; §5.3)
- `source_id ∈ {'bphs', 'jaimini_sutras'}` (both existing)

Index:
```sql
CREATE INDEX idx_longevity_compute_chart
  ON technique_compute (chart_id, rule_id, computed_at DESC)
  WHERE technique_family_id = 'longevity';
```

F1 additive seed:
```yaml
# technique_families.yaml additions
- family_id: longevity
  display_name: "Longevity (Ayus) — Pindayu, Amshayu, Nisargayu, Jaimini"
  default_output_shape_id: longevity_analysis
  default_aggregation_hint: D
  parent_category: vedic_classical
```

### 5.3 New output shape: `longevity_analysis`

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["methods", "aggregate"],
  "properties": {
    "methods": {
      "type": "object",
      "properties": {
        "pindayu": {
          "type": "object",
          "required": ["estimate_years", "haranas_applied", "per_planet"],
          "properties": {
            "estimate_years": {"type": "number"},
            "estimate_months": {"type": "number"},
            "haranas_applied": {
              "type": "object",
              "properties": {
                "chakra": {"type": "object"},
                "kroorasthana": {"type": "object"},
                "astangata": {"type": "object"},
                "shatrukshetra": {"type": "object"},
                "sheersha_odaya": {"type": "number"}
              }
            },
            "per_planet": {
              "type": "array",
              "items": {
                "type": "object",
                "required": ["planet", "base_ayus", "contribution"],
                "properties": {
                  "planet": {"type": "string"},
                  "base_ayus": {"type": "number"},
                  "dignity_state": {"type": "string"},
                  "chakra_factor": {"type": "number"},
                  "kroora_factor": {"type": "number"},
                  "astangata_factor": {"type": "number"},
                  "shatru_factor": {"type": "number"},
                  "contribution": {"type": "number"}
                }
              }
            },
            "citation": {"type": "string"}
          }
        },
        "amshayu": {
          "type": "object",
          "required": ["estimate_years", "per_planet"],
          "properties": {
            "estimate_years": {"type": "number"},
            "per_planet": {"type": "array"},
            "citation": {"type": "string"}
          }
        },
        "nisargayu": {
          "type": "object",
          "required": ["estimate_years_scaled", "estimate_years_raw"],
          "properties": {
            "estimate_years_scaled": {"type": "number"},
            "estimate_years_raw": {"type": "number"},
            "per_planet": {"type": "array"},
            "citation": {"type": "string"}
          }
        },
        "jaimini": {
          "type": "object",
          "required": ["category", "approximate_years"],
          "properties": {
            "category": {"type": "string", "enum": ["alpayu","madhyayu","deerghayu"]},
            "approximate_years": {
              "type": "object",
              "properties": {"min": {"type": "number"}, "max": {"type": "number"}}
            },
            "tryasya_yoga": {"type": "string"},
            "karaka_refinement": {"type": "string"},
            "final_category_after_refinement": {"type": "string"},
            "confidence": {"type": "number", "minimum": 0, "maximum": 1},
            "citation": {"type": "string"}
          }
        }
      }
    },
    "aggregate": {
      "type": "object",
      "required": ["convergent", "central_estimate_years"],
      "properties": {
        "convergent": {"type": "boolean"},
        "discrepant": {"type": "boolean"},
        "central_estimate_years": {"type": "number"},
        "range_years": {
          "type": "object",
          "properties": {"min": {"type": "number"}, "max": {"type": "number"}}
        },
        "astrologer_note": {"type": "string"}
      }
    },
    "access_mode": {
      "type": "string",
      "enum": ["astrologer_workbench", "ultra_mode_b2c", "internal_audit"]
    },
    "ethical_disclaimer": {"type": "string"}
  }
}
```

### 5.4 API contract

```
GET /api/v1/longevity/{chart_id}
Headers:
  X-API-Key: <key> OR Authorization: Bearer <jwt>
  X-Access-Mode: astrologer_workbench | ultra_mode_b2c  (default: astrologer_workbench;
                                                         403 if user lacks role)

Optional query params:
  methods        (default: all; comma-separated subset of pindayu,amshayu,nisargayu,jaimini)
  include_raw    (default: false; if true, returns raw 127-basis Nisargayu too)

Response 200 (astrologer mode — full detail):
{
  "success": true,
  "message": "Longevity analysis computed",
  "data": {
    "metadata": { TechniqueResultMetadata },
    "per_source": { ... bphs, jaimini_sutras ... },
    "aggregates": {
      "D_hybrid": {
        "result": { ... longevity_analysis shape with full detail ... }
      }
    }
  }
}

Response 200 (ultra_mode_b2c — category only):
{
  "success": true,
  "message": "...",
  "data": {
    "longevity_category": "deerghayu",
    "approximate_range_years": {"min": 72, "max": 100},
    "disclaimer": "This is a classical categorical estimate; for detailed analysis please consult a professional astrologer.",
    "consultation_offer": {"consultation_url": "/consultations/book"}
  }
}

Response 403 (B2C user without ultra_mode):
{
  "success": false,
  "message": "Longevity analysis requires astrologer access or ultra_mode consent.",
  "errors": ["access_restricted"],
  "data": {"consultation_offer": {"consultation_url": "/consultations/book"}}
}
```

### 5.5 Internal Python interface

```python
# src/josi/services/classical/longevity/engine.py

class LongevityEngine(ClassicalEngineBase):
    technique_family_id: str = "longevity"
    default_output_shape_id: str = "longevity_analysis"

    def __init__(
        self,
        calc: AstrologyCalculator,
        pindayu: PindayuCalculator,
        amshayu: AmshayuCalculator,
        nisargayu: NisargayuCalculator,
        jaimini: JaiminiAyurDasha,
        harana_calculator: HaranaCalculator,
    ):
        ...

    async def compute_longevity(
        self,
        chart_id: UUID,
        methods: list[str] | None = None,
        access_mode: str = "astrologer_workbench",
    ) -> LongevityAnalysis:
        """
        Run 4 methods; aggregate; respect access_mode gating.
        """

    async def _aggregate(
        self,
        pindayu: float,
        amshayu: float,
        nisargayu: float,
        jaimini_category: str,
    ) -> AggregateSummary:
        """
        Detect convergence, compute central estimate (median), flag discrepancy.
        """


# src/josi/services/classical/longevity/pindayu.py

class PindayuCalculator:
    def __init__(self, calc: AstrologyCalculator, harana: HaranaCalculator):
        ...

    def compute(self, chart: NatalChart) -> PindayuResult:
        """
        Per BPHS Ch. 72:
          1. For each of 7 planets, look up base_ayus from strength table.
          2. Apply 5 harana factors via HaranaCalculator.
          3. Sum contributions.
          4. Apply sheersha_odaya at top-level.
          5. Return PindayuResult with per_planet breakdown.
        """


# src/josi/services/classical/longevity/haranas.py

class HaranaCalculator:
    """Shared harana computation used by Pindayu, Amshayu, Nisargayu."""

    def chakra_factor(self, planet: str, chart: NatalChart) -> float: ...
    def kroorasthana_factor(self, planet: str, chart: NatalChart) -> float: ...
    def astangata_factor(self, planet: str, chart: NatalChart) -> float: ...
    def shatrukshetra_factor(self, planet: str, chart: NatalChart) -> float: ...
    def sheersha_odaya_factor(self, chart: NatalChart) -> float: ...   # chart-level, not per-planet


# src/josi/services/classical/longevity/jaimini_ayurdasha.py

class JaiminiAyurDasha:
    def compute(self, chart: NatalChart) -> JaiminiLongevityResult:
        """
        1. Classify Lagna, 7H, 8H signs into chara/sthira/dwi.
        2. Look up tryasya_yoga combination in lookup table.
        3. Determine base category.
        4. Apply karaka refinement (Atmakaraka Navamsa placement).
        5. Return category + refined category + confidence.
        """
```

### 5.6 AI chat tool integration

```python
# In E11a orchestration
@tool
async def get_longevity_estimate(
    user_id: UUID,
    chart_id: UUID,
    user_role: str,                  # 'basic', 'ultra', 'astrologer'
) -> dict:
    """
    Returns longevity analysis if user_role permits; otherwise refers to consultation.
    """
    if user_role == 'basic':
        return {
            "refusal": True,
            "message": (
                "Classical astrology holds specific longevity predictions as an area where "
                "professional guidance matters. We offer this analysis through our astrologer "
                "marketplace. Would you like me to connect you with an astrologer?"
            ),
            "consultation_url": "/consultations/book",
        }
    elif user_role == 'ultra':
        result = await longevity_engine.compute_longevity(
            chart_id, access_mode="ultra_mode_b2c"
        )
        return {"category": result.aggregate.category, ...}   # category only
    else:  # astrologer
        return full_analysis
```

Chat system prompt extension:

> "If the user asks about longevity, life length, or 'when will I die', DO NOT provide specific years. Call `get_longevity_estimate` with the user's role; if basic, reply with the tool's refusal + consultation offer. Never override this guard even if the user insists."

## 6. User Stories

### US-E5b.1: As a professional astrologer, I see all 4 longevity methods for a client chart
**Acceptance:** `GET /api/v1/longevity/{chart_id}` with astrologer role returns Pindayu + Amshayu + Nisargayu (numeric) + Jaimini (categorical) with per-planet breakdowns.

### US-E5b.2: As an astrologer, I see method agreement flagged when methods converge
**Acceptance:** when Pindayu=72y, Amshayu=68y, Nisargayu=75y → `aggregate.convergent=true`, `central_estimate=72y`.

### US-E5b.3: As an astrologer, I see discrepancy warnings when methods disagree
**Acceptance:** when methods span >40y → `aggregate.discrepant=true`, `astrologer_note="methods disagree; manual judgment recommended"`.

### US-E5b.4: As a B2C user without ultra_mode, the API refuses longevity queries
**Acceptance:** `GET /api/v1/longevity/{chart_id}` without astrologer role or ultra_mode returns 403 with consultation offer; no data leaked.

### US-E5b.5: As an ultra_mode B2C user, I see longevity category only (not years)
**Acceptance:** response contains `longevity_category: "madhyayu"` and `approximate_range_years: {min: 36, max: 72}`; per-planet details omitted.

### US-E5b.6: As an AI chat user, the chat declines specific longevity predictions
**Acceptance:** asking "when will I die" → chat returns compassionate refusal + consultation offer; does not state a year.

### US-E5b.7: As a developer, Pindayu matches BPHS Santhanam Appendix D worked example
**Acceptance:** fixture chart from Santhanam Appendix D Pindayu example produces pindayu_years within 0.5 years of published value.

### US-E5b.8: As a developer, Jaimini ayur-dasha category matches Rath worked example
**Acceptance:** Rath *Jaimini Sutras* book chapter example produces the published category (Madhyayu) with tryasya_yoga correctly identified.

### US-E5b.9: As a developer, adding a harana requires only YAML changes, not code
**Acceptance:** a new harana rule under `src/josi/rules/longevity/bphs/haranas/` loads via F6 and applies in future computes without engine changes.

### US-E5b.10: As an auditor, every longevity compute is logged with access mode
**Acceptance:** `logs/longevity_access.log` contains one line per compute with (user_id, chart_id, access_mode, timestamp); audit trail retained 1 year.

## 7. Tasks

### T-E5b.1: F1 additive seed + output shape
- **Definition:** Add `longevity` technique_family; add `longevity_analysis` output_shape with JSON Schema per §5.3.
- **Acceptance:** DimensionLoader picks up both; `SELECT * FROM technique_family WHERE family_id='longevity'` returns 1 row; `fastjsonschema.compile(longevity_analysis_schema)(sample)` passes.
- **Effort:** 4 hours

### T-E5b.2: HaranaCalculator
- **Definition:** 5 harana methods in `haranas.py` with per-planet and chart-level returns.
- **Acceptance:** Unit tests: planet in 8H → chakra_factor=0.33; malefic in 6H → kroora_factor=0.75; Mercury within 12° of Sun → astangata_factor=0.5; etc.
- **Effort:** 10 hours

### T-E5b.3: Pindayu calculator + base ayus data
- **Definition:** `PindayuCalculator` per §3.1; `pindayu_base_ayus.yaml` with 7×7 strength table.
- **Acceptance:** 5 fixtures match BPHS Santhanam Appendix D worked examples within 0.5y.
- **Effort:** 14 hours
- **Depends on:** T-E5b.2

### T-E5b.4: Amshayu calculator
- **Definition:** `AmshayuCalculator` per §3.2; consumes D9 positions from existing AstrologyCalculator.
- **Acceptance:** Navamsa-anchored fixture matches hand-computed value.
- **Effort:** 10 hours
- **Depends on:** T-E5b.2

### T-E5b.5: Nisargayu calculator
- **Definition:** `NisargayuCalculator` per §3.3; emits both raw (127) and scaled (120).
- **Acceptance:** Undisturbed chart returns scaled=~120y; harana-afflicted returns reduced.
- **Effort:** 6 hours
- **Depends on:** T-E5b.2

### T-E5b.6: Jaimini Ayur-dasha
- **Definition:** `JaiminiAyurDasha` per §3.4; tryasya_yoga table lookup + karaka refinement.
- **Acceptance:** Rath worked example matches (chara-sthira-dwi → Madhyayu); refinement via AK in Nav kendra shifts to Deerghayu.
- **Effort:** 16 hours

### T-E5b.7: LongevityEngine aggregator
- **Definition:** `LongevityEngine.compute_longevity` orchestrates 4 methods; `_aggregate` computes median + convergence/discrepancy.
- **Acceptance:** Integration test: 3 fixture charts, each with known published values, engine produces matching outputs + correct convergence flag.
- **Effort:** 8 hours

### T-E5b.8: Rule YAMLs (BPHS + Jaimini)
- **Definition:** Author rule YAMLs under `src/josi/rules/longevity/` for Pindayu, Amshayu, Nisargayu, Jaimini (4 method rules) + 5 harana rules + tryasya_yoga + karaka_refinement YAMLs.
- **Acceptance:** All load via `poetry run validate-rules`; content_hashes stable.
- **Effort:** 12 hours
- **Depends on:** F6

### T-E5b.9: Ethical guardrail + access modes
- **Definition:** API controller checks `X-Access-Mode` header + user role; rejects or shapes response per §5.4.
- **Acceptance:** B2C without ultra_mode → 403; ultra_mode → category only; astrologer → full.
- **Effort:** 6 hours

### T-E5b.10: AI chat tool + refusal system
- **Definition:** Register `get_longevity_estimate` tool in E11a; add system prompt guidance to decline for basic users.
- **Acceptance:** Chat refuses with compassionate message + consultation link on "when will I die" with basic user; responds with category only for ultra_mode.
- **Effort:** 8 hours
- **Depends on:** E11a, T-E5b.7

### T-E5b.11: Audit logging
- **Definition:** Log every longevity compute to `logs/longevity_access.log` with (user_id, chart_id, access_mode, content_hash, timestamp); 1-year retention.
- **Acceptance:** Logs written; log rotation configured; unit test asserts log entry per compute.
- **Effort:** 3 hours

### T-E5b.12: API controller + routing
- **Definition:** `longevity_controller.py` with endpoints per §5.4. Register in `api/v1/__init__.py`.
- **Acceptance:** OpenAPI docs show endpoints; integration tests for all 3 access modes.
- **Effort:** 6 hours

### T-E5b.13: Golden fixtures
- **Definition:** 5 natal charts: each with published Pindayu (BPHS / JH), Amshayu (JH), Nisargayu (trivially computable), Jaimini category (Rath/Iyer worked examples). Per-planet contributions too.
- **Acceptance:** All engine outputs match fixtures within 0.5y / matching category; 60+ assertions green.
- **Effort:** 16 hours

### T-E5b.14: Performance + caching
- **Definition:** Benchmark: single-chart longevity < 300ms; cached lookup < 20ms.
- **Acceptance:** pytest-benchmark passes.
- **Effort:** 4 hours

### T-E5b.15: Documentation + ethical posture
- **Definition:** CLAUDE.md: "longevity engine under `src/josi/services/classical/longevity/`". User-facing docs explicitly explain ethical guardrail. Astrologer workbench help text.
- **Acceptance:** Merged; ethical stance clearly articulated.
- **Effort:** 4 hours

## 8. Unit Tests

### 8.1 HaranaCalculator

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_chakra_factor_planet_in_8th` | planet in 8H | 0.33 | BPHS 72.7 |
| `test_chakra_factor_planet_in_6th` | planet in 6H | 0.5 | BPHS 72.7 |
| `test_chakra_factor_planet_elsewhere` | planet in 5H | 1.0 | BPHS 72.7 |
| `test_kroora_malefic_in_8h` | Mars in 8H | 0.5 (compounded with chakra 0.33 → net 0.165) | BPHS 72.9 |
| `test_kroora_benefic_unaffected` | Jupiter in 8H | kroora_factor=1.0 (only chakra applies) | malefic-only |
| `test_astangata_mercury_6deg_from_sun` | Mercury 6° from Sun (< 12°) | 0.5 | combustion |
| `test_astangata_mercury_15deg` | Mercury 15° | 1.0 | outside range |
| `test_shatrukshetra_planet_in_enemy_sign` | Sun in Libra (enemy) | 0.75 | BPHS 72.14 |
| `test_sheersha_odaya_head_rising_lagna` | Lagna Aries (head-rising) | 1.0 | chart-level |
| `test_sheersha_odaya_back_rising_lagna` | Lagna Taurus (back-rising) | 0.5 | BPHS 72.15 |

### 8.2 Pindayu calculator

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_pindayu_santhanam_app_d_fixture_1` | BPHS worked chart 1 | pindayu_years matches published value ±0.5y | classical canonical |
| `test_pindayu_santhanam_app_d_fixture_2` | BPHS worked chart 2 | within ±0.5y | canonical |
| `test_pindayu_excludes_rahu_ketu` | chart with Rahu/Ketu | their contribution=0 | BPHS 72.2 |
| `test_pindayu_sheersha_odaya_halving` | same chart with back-rising Lagna vs head-rising | back-rising result = head-rising result / 2 | factor application |
| `test_pindayu_per_planet_breakdown` | any fixture | 7 entries in per_planet, sum equals estimate | audit |
| `test_pindayu_no_planets_afflicted` | strongest chart (all exalted/own) | years close to sum(19+25+15+12+15+21+20)=127 | no-harana upper bound |
| `test_pindayu_all_planets_in_8h` | contrived fixture | years reduced significantly | harana compounding |

### 8.3 Amshayu calculator

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_amshayu_uses_navamsa_positions` | planet in own sign natal but debilitated Navamsa | contribution reduced | D9-anchored |
| `test_amshayu_jh_reference_fixture` | reference chart | match JH ±0.5y | cross-check |
| `test_amshayu_differs_from_pindayu_when_d9_differs` | chart with strong sign but weak Navamsa | Amshayu < Pindayu | doctrine verified |

### 8.4 Nisargayu calculator

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_nisargayu_unafflicted_scaled_120` | chart with no haranas | ~120y | normalization |
| `test_nisargayu_raw_127` | same chart, include_raw=true | ~127y | raw basis |
| `test_nisargayu_heavy_affliction_reduces` | all planets in 8H | years < 60 | haranas work |

### 8.5 Jaimini Ayur-dasha

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_jaimini_chara_sthira_dwi_madhyayu` | Lagna chara, 7th sthira, 8th dwi | category=madhyayu | tryasya_yoga table |
| `test_jaimini_chara_chara_deerghayu` | Lagna chara, 7th chara, 8th any | deerghayu | tryasya_yoga table |
| `test_jaimini_sthira_dwi_alpayu` | Lagna sthira, 7th dwi, 8th any | alpayu | tryasya_yoga table |
| `test_jaimini_atmakaraka_nav_kendra_shifts_up` | base madhyayu + AK in Nav 4H | final=deerghayu | karaka refinement |
| `test_jaimini_atmakaraka_nav_dusthana_shifts_down` | base madhyayu + AK in Nav 8H | final=alpayu | karaka refinement |
| `test_jaimini_single_step_refinement` | Deerghayu + AK in kendra | stays deerghayu (can't shift above) | bound |
| `test_jaimini_rath_example_chart` | Rath worked example | published category | canonical |

### 8.6 LongevityEngine aggregation

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_aggregate_convergent_methods` | Pindayu=72, Amshayu=68, Nisargayu=75 | convergent=true, central=72 | convergence |
| `test_aggregate_discrepant_methods` | Pindayu=45, Amshayu=85, Nisargayu=65 | discrepant=true (span 40y) | flagging |
| `test_aggregate_jaimini_agreement_with_numeric` | numeric central=60, Jaimini=madhyayu (36-72) | agreement flag | cross-method |
| `test_aggregate_jaimini_disagreement` | numeric central=90, Jaimini=alpayu | disagreement flag | cross-method |
| `test_median_robust_to_outlier` | 60, 62, 58, 120 | median=61 | robust central |

### 8.7 Ethical guardrail

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_b2c_basic_returns_403` | basic user GET /longevity | 403 + consultation offer | gate |
| `test_b2c_ultra_returns_category_only` | ultra_mode user | data has category, not years | scoped response |
| `test_astrologer_returns_full` | astrologer role | full longevity_analysis | unrestricted |
| `test_ai_chat_basic_refuses_specific_years` | basic user asks "when will I die" | refusal + consultation_url | tool guard |
| `test_ai_chat_ultra_returns_category_only` | ultra_mode user same question | category only (no years) | scoped tool |
| `test_audit_log_entry_per_compute` | any compute | log line written | audit |
| `test_audit_log_no_plaintext_years_for_b2c` | basic user refusal | log records access_mode=basic, no years computed | privacy |

### 8.8 Rule YAMLs

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_all_longevity_rules_load` | validate-rules | passes | F6 integration |
| `test_longevity_rule_citations_present` | each rule | citation field non-empty | provenance |
| `test_harana_rule_content_hash_stable` | same YAML re-loaded | hash unchanged | reproducibility |

### 8.9 Integration

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_longevity_full_path_astrologer` | 5 charts × astrologer mode | 5 technique_compute rows; all longevity_analysis valid | E2E |
| `test_longevity_idempotent` | same chart twice | 1 compute row + 2 aggregation events | F2 contract |
| `test_longevity_output_schema_strict` | any output | passes F7 longevity_analysis schema | parity |
| `test_longevity_respects_access_mode_end_to_end` | basic → 403, ultra → category, astrologer → full | all correct | auth wiring |
| `test_longevity_consults_e2a_sodhya_pinda` | chart with precomputed Sodhya Pinda | Pindayu uses existing E2a results | DRY |

## 9. EPIC-Level Acceptance Criteria

- [ ] `LongevityEngine` implements 4 methods (Pindayu, Amshayu, Nisargayu, Jaimini)
- [ ] All 5 BPHS haranas implemented in shared `HaranaCalculator`
- [ ] Pindayu matches BPHS Santhanam Appendix D worked examples within 0.5 year on 5 fixtures
- [ ] Amshayu uses Navamsa positions; differs from Pindayu on charts where D9 differs from Rashi
- [ ] Nisargayu ships both 120-scaled and 127-raw variants
- [ ] Jaimini Ayur-dasha categorizes charts into alpayu/madhyayu/deerghayu with karaka refinement
- [ ] Aggregation detects convergence (3+ methods within 20y) and discrepancy (>40y span)
- [ ] Ethical guardrail: B2C without ultra_mode → 403; ultra_mode → category only; astrologer → full
- [ ] AI chat declines specific longevity predictions with compassionate refusal + consultation offer
- [ ] Audit log written for every longevity compute with access mode
- [ ] New F1 rows: `longevity` technique_family, `longevity_analysis` output_shape
- [ ] Rule YAMLs (4 methods + 5 haranas + 2 Jaimini rules) load via F6 and have stable content_hashes
- [ ] API endpoint `GET /api/v1/longevity/{chart_id}` live with role-based response shaping
- [ ] Integration test hits full path (compute → persist → aggregate → API read) for all 3 access modes
- [ ] Golden fixture suite: 5 charts × ~12 assertions = 60+ assertions green
- [ ] Unit test coverage ≥ 90% across `longevity/` package
- [ ] Performance: full longevity compute < 300ms; cached < 20ms
- [ ] CLAUDE.md updated with longevity section + ethical posture articulation

## 10. Rollout Plan

- **Feature flag:** `enable_longevity_engine` — off in P1, on in P2 for astrologer-pro tier first. B2C access remains 403 until `enable_longevity_b2c_ultra` flag (separate) is turned on after 4-week QA period.
- **Shadow compute:** 2 weeks — compute all 4 methods on all charts with astrologer accounts; compare to JH reference for charts where astrologer provides their JH computation; log to `logs/longevity_shadow.log`.
- **Backfill:** lazy (compute on first request per chart); no bulk backfill (longevity is on-demand).
- **Rollback:** disable feature flag; API returns 501; `technique_compute` rows remain for future re-enable. Any cached results retained.

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Pindayu base-ayus table transcription error | Medium | High | Dual review (engineer + classical advisor); differential test vs JH |
| Harana formulas disputed across commentaries | High | Medium | Ship BPHS canonical; Phaladeepika variant as source_id variant in E5c |
| Ethical guardrail bypassed by API misuse | Medium | **Very High** (legal + reputation) | Multi-layer: role check + access_mode header + AI tool-level refusal; audit log; integration test asserts 403 for basic |
| AI chat system prompt drift allows longevity leak | Medium | High | System prompt version-pinned; adversarial red-team test asking "when will I die" 20 ways; must all refuse |
| B2C ultra_mode category disclosure still upsets user | Low | Medium | Category is soft (range); category itself is disclaimered; consultation offer always present |
| Method disagreement confuses astrologer | Medium | Low | Discrepancy flag + astrologer_note explicitly call it out |
| Jaimini karaka refinement disputed across commentators | Medium | Low | Ship Sanjay Rath default; document alternates |
| Nisargayu 120 vs 127 scaling debate | Low | Low | Ship both; let astrologer choose |
| Performance regression if all 4 methods run every time | Low | Low | Each method < 100ms; total < 300ms; cache results |
| Audit log contains sensitive data | Low | Medium | Log only (user_id, chart_id, access_mode, content_hash); never log estimate_years for basic users |
| Litigation from distressed user | Low | Very High | Disclaimer in all responses; consultation referral; no specific years to B2C ever |
| Classical source disagreement on Pindayu method (planet weights) | Medium | Medium | Per-planet source attribution in per_planet; astrologer can trace each value |
| Content_hash instability across haranas evolutions | Low | Medium | F13 ensures hash only over semantic fields; harana version bumps explicitly |
| Cross-method aggregation masks single-method failures | Medium | Low | Each method's result surfaced individually; aggregate is an additional signal |

## 12. References

- Master spec: [`docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`](../../../superpowers/specs/2026-04-19-classical-techniques-expansion-design.md)
- F1 dims: [`../P0/F1-star-schema-dimensions.md`](../P0/F1-star-schema-dimensions.md)
- F2 fact tables: [`../P0/F2-fact-tables.md`](../P0/F2-fact-tables.md)
- F6 Rule DSL: [`../P0/F6-rule-dsl-yaml-loader.md`](../P0/F6-rule-dsl-yaml-loader.md)
- F7 Output shapes: [`../P0/F7-output-shape-system.md`](../P0/F7-output-shape-system.md) — adds `longevity_analysis`
- F8 Aggregation: [`../P0/F8-technique-result-aggregation-protocol.md`](../P0/F8-technique-result-aggregation-protocol.md)
- F13 Content-hash provenance: [`../P0/F13-content-hash-provenance.md`](../P0/F13-content-hash-provenance.md)
- E1a Multi-Dasa v1: [`../P1/E1a-multi-dasa-v1.md`](../P1/E1a-multi-dasa-v1.md)
- E2a Ashtakavarga v2 (Sodhya Pinda prerequisite): [`../P1/E2a-ashtakavarga-v2.md`](../P1/E2a-ashtakavarga-v2.md)
- E4a Yoga Engine MVP: [`../P1/E4a-yoga-engine-mvp.md`](../P1/E4a-yoga-engine-mvp.md)
- E11a AI Chat Orchestration (for tool integration): [`../P1/E11a-ai-chat-orchestration-v1.md`](../P1/E11a-ai-chat-orchestration-v1.md)
- E12 Astrologer Workbench (surfacing): [`./E12-astrologer-workbench-ui.md`](./E12-astrologer-workbench-ui.md)
- **Classical sources:**
  - *Brihat Parashara Hora Shastra* Ch. 72 (Piṇḍāyur-adhyāya), Ch. 73 (Aṁśāyur-adhyāya), Ch. 74 (Naisargikāyur-adhyāya) — Santhanam translation (2004 ed., Ranjan Publications)
  - *Brihat Parashara Hora Shastra* — Gandhi, C.G., Hindi commentary edition, 1994
  - *Jaimini Upadesha Sutras* Bk.2 Ch.2 — Sanjay Rath translation (2006, Sagittarius Publications)
  - *Jaimini Sutras* — Iyer, B.S., edition, 1957
  - *Phaladeepika* by Mantreswara, Ch. 7 — ethical caution on death prediction
  - *Jataka Parijata* by Vaidyanatha Dikshita, Ch. 23 — cross-reference on longevity
  - *Saravali* by Kalyanavarma, Ch. 40 — variant longevity method (deferred)
- **Modern reference:**
  - K.N. Rao, *Ups and Downs in Career* (includes longevity case studies), Vani Publications
  - B.V. Raman, *Three Hundred Important Combinations* — longevity-related yogas
- **Ethical codes:**
  - American Council of Vedic Astrology (ACVA) Code of Ethics §III.4
  - British Association of Vedic Astrology (BAVA) Guidelines §2.1
  - International Society of Astrological Research (ISAR) Ethics Code, 2019
- Reference implementations:
  - Jagannatha Hora 7.41 — "Ayurdaya" panel (used as numeric baseline for 5 golden fixtures)
  - Parashara's Light 9.0 — longevity module (commercial)
