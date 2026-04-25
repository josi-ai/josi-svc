---
prd_id: E2a
epic_id: E2
title: "Ashtakavarga v2 (Trikona + Ekadhipatya shodhana, Sodhya Pinda)"
phase: P1-mvp
tags: [#correctness, #extensibility]
priority: must
depends_on: [F1, F2, F4, F6, F7, F8, F13, F16, F17]
enables: [E11a, E14a]  # E2b removed 2026-04-23 — orphaned reference, no E2b PRD exists or is planned
classical_sources: [bphs, phaladeepika, jataka_parijata]
estimated_effort: 2 weeks
status: approved
author: @agent-claude-opus-4-7
last_updated: 2026-04-22
---

# E2a — Ashtakavarga v2 (Trikona + Ekadhipatya Shodhana, Sodhya Pinda)

## 1. Purpose & Rationale

Josi currently computes **raw Bhinnashtakavarga** (BAV) and **Sarvashtakavarga** (SAV) in `src/josi/services/ashtakavarga_calculator.py` — bindu contribution matrices per classical rules. This is the shallow half of the technique. The classical workflow (BPHS Ch. 66, *Ashtakavargaadhyaya*) explicitly prescribes two **shodhana** ("purification") passes before any numeric can be interpreted:

1. **Trikona Shodhana** — removes redundant bindus across trinal sign groups.
2. **Ekadhipatya Shodhana** — resolves duplication from two signs owned by the same planet.

And then, for longevity and strength assessments (ayurdaya), the doubly-shodhit BAV feeds into a **Sodhya Pinda** computation: planet-factor × rashi-factor multipliers applied to the purified matrix.

Today Josi displays the raw BAV, which classical astrologers reject as incomplete. B.V. Raman in *A Catechism of Astrology* and all Parashari textbooks emphasize: **never judge a house by raw bindu counts; always judge by shodhit values.**

This PRD:
- Adds the two shodhana algorithms exactly per BPHS Ch. 66.
- Adds Sodhya Pinda (planet + rashi pinda) per BPHS Ch. 67.
- Versions all three outputs (raw, trikona-shodhit, ekadhipatya-shodhit, sodhya-pinda) as separate JSONB matrices under the same `numeric_matrix` output shape.
- Exposes them via REST and AI tool-use.
- Wires through the F8 `ClassicalEngine` Protocol and F6 rule DSL so future shodhana variants (there are regional differences) drop in additively.

## 2. Scope

### 2.1 In scope

- **Trikona Shodhana** algorithm (BPHS Ch. 66 v.1–5).
- **Ekadhipatya Shodhana** algorithm (BPHS Ch. 66 v.6–15).
- **Sodhya Pinda** computation: Graha Pinda (planet factor) × Rashi Pinda (sign factor) × Shodhit BAV (BPHS Ch. 67).
- Refactor of existing `AshtakavargaCalculator` into a `ClassicalEngine` conforming implementation.
- New rule YAML files per F6 DSL: one per algorithm, citing BPHS.
- Extended response payload: raw + trikona_shodhit + ekadhipatya_shodhit + sodhya_pinda matrices.
- 10 golden chart fixtures with JH 7.x verified expected values.
- Property tests: post-shodhana bindu counts ≤ pre-shodhana; sum invariants.

### 2.2 Out of scope

- **Transit-based ashtakavarga predictions** (Ayurdaya, Pinda Ayu) — deferred to E6b.
- **Kakshya-based finer subdivisions** (sub-sign strength, Kaksha Vibhaga) — P2.
- **Variant shodhana methods from Phaladeepika** (minor differences from BPHS) — deferred; BPHS canonical in v1.
- **Ashtakavarga-based varga charts** (D-3, D-7 ashtakavarga) — outside classical Ashtakavarga scope.

### 2.3 Dependencies

- F1 (source `bphs` seeded; `ashtakavarga` family seeded; `numeric_matrix` output shape seeded).
- F2 (fact tables including `technique_compute`).
- F4 (rule versioning).
- F6 (YAML rule loader).
- F7 (JSON Schema for `numeric_matrix` defines shape of `matrix: int[12][8]`).
- F8 (`ClassicalEngine` Protocol).
- F16, F17 (golden suite + property test harness).
- Existing `ashtakavarga_calculator.py` (to be refactored, not replaced).

## 2.4 Design Decisions (Pass 1 Astrologer Review — Locked 2026-04-21)

All open questions from E2a Pass 1 astrologer review are resolved. Cross-cutting decisions reference `DECISIONS.md`; E2a-specific decisions documented here.

### Cross-cutting decisions (applied via `DECISIONS.md`)

| Decision | Value | Ref |
|---|---|---|
| Ayanamsa default | Lahiri B2C + 9-shortlist astrologer | 1.2 |
| Rahu/Ketu node type | Both Mean + True computed; **Mean default B2C** (revised 2026-04-22); astrologer prompted per chart | 1.1 |
| Natchathiram count | 27 (affects contributor-from-Moon rules) | 3.7 |
| Ashtakavargam scope (B2C) | 3-tier bhava-strength summary from post-shodhanai SAV with BPHS Ch.6 purpose mapping | 1.8 |
| Ashtakavargam scope (Astrologer) | Full 5-tab view (Raw BAV, Trikona-Shodhit, Ekadhipatya-Shodhit, Shodhit SAV, Sodhya Pinda) + Kaksha Vibhaga panel + contributor-trace drill-down | 1.8 |
| Divisional scope | D1 (Rasi) + D9 (Navamsam) Ashtakavargam computed; D10+ deferred | 1.8 |
| Trikona Shodhanai variant | Phaladeepika 3-case rule: (1) if min=0 → zero all three; (2) if min is tied ≥2 members → zero all three; (3) else subtract min (revised 2026-04-22) | 1.8 |
| Kaksha Vibhaga | Promoted from "optional stage 7" to in-scope astrologer view | 1.8 |
| Sodhya Pinda downstream | Feeds E5b Ayurdaya (Pindayu computation); astrologer-gated for ethical reasons | 1.7 (references E5b) |
| Language display | Sanskrit-IAST canonical + Tamil phonetic for UI | 1.5 |

### E2a-specific decisions (locked this review)

| Decision | Value | Source |
|---|---|---|
| Ekadhipatya Shodhanai variant | BPHS strict (Variant 1) — zero-out based on ruler-position and lower-bindu rules. Matches JH + Parashara's Light + Tamil Vakya dominant practice. Mixes traditions with Phaladeepika Trikona; acceptable since separate reduction operations. | Pass 1 Q1 |
| Graha Pinda + Rashi Pinda source | **Chakra values** (not literal verse). Graha Pinda: Sooriyan 5, Chandran 5, Sevvai 8, Budhan 5, Guru 10, Sukkiran 7, Sani 5. Rashi Pinda per-sign: Mesham 7, Rishabam 10, Mithunam 8, Karkatam 4, Simmam 10, Kanni 6, Thulam 7, Viruchigam 8, Dhanusu 9, Magaram 5, Kumbham 11, Meenam 12. Matches JH + Parashara's Light + all modern software (chakra overrides literal verse per 500+ years working practice). | Pass 1 Q2 (post-research) |
| Per-graha max bindu totals | Classical 48/49/39/54/56/52/39 (Sooriyan/Chandran/Sevvai/Budhan/Guru/Sukkiran/Sani). SAV classical max = 337. Used as property-test invariant (assert computed BAV totals don't exceed maxes) + percentage-of-max rendering ("Budhan 42/54 = 78%") in astrologer view. | Pass 1 Q3 |
| Contributor-trace storage | Bindu-only storage (no bitmask or trace materialization). Drill-down recomputes contributor rules on demand (~10-50ms latency). Minimal storage (~1.3 KB/chart) — acceptable latency trade-off for rare astrologer drill-down usage. | Pass 1 Q4 |
| Matching bar vs JH 7.x | **Exact (±0) per-cell match** across 10 golden-chart fixtures. Covers Raw BAV + Trikona-Shodhit + Ekadhipatya-Shodhit + SAV + Sodhya Pinda. Any divergence is a bug; Ashtakavargam is integer math, deterministic. | Pass 1 Q5 |

### Sodhya Pinda worked computation (example)

For a chart with shodhit BAV totals per graha (hypothetical):

```
Graha       Shodhit BAV total    Graha Pinda    Sodhya (per-sign weighted)
─────────────────────────────────────────────────────────────────────────
Sooriyan    34                   5              1360
Chandran    36                   5              1260
Sevvai      28                   8              1568
Budhan      40                   5              1600
Guru        41                   10             2870
Sukkiran    38                   7              2128
Sani        26                   5              1040
─────────────────────────────────────────────────────────────────────────
Total                                           11826     → feeds E5b Pindayu
```

### Implementation implications

1. **Dual-node computation** (from DECISIONS 1.1) → BAV computed twice if node type affects Rahu/Ketu contributor tables. Store both computations with discriminator.
2. **D9 Navamsam Ashtakavargam** → second full Ashtakavargam pipeline computed alongside D1. 2× storage, 2× compute. Cached per chart.
3. **Kaksha Vibhaga** → additional 96-kaksha computation per graha per chart (7 grahas × 96 kakshas = 672 lookups). Tabulated; trivial compute.
4. **Percentage-of-max rendering** → requires classical-max table hardcoded; when astrologer views per-graha BAV, render "X/max (Y%)". Invariant assertion in property tests.
5. **Sodhya Pinda → E5b dependency** → Ashtakavargam pipeline must complete before E5b Pindayu can compute. Pipeline ordering: Panchangam → Chart positions → Ashtakavargam → E5b Ayurdaya.

### Engineering action items (not astrologer-review scope)

- [ ] Refactor existing `ashtakavarga_calculator.py` to `ClassicalEngine` Protocol conformance (per E2a §3).
- [ ] Add Trikona Shodhanai rule (Phaladeepika 3-case) as YAML rule: if trine min=0 → zero all; elif trine min tied ≥2 members → zero all; else subtract min. Reject any impl that only subtracts min without the two edge cases.
- [ ] Add Ekadhipatya Shodhanai rule (BPHS strict zero-out logic) as YAML rule.
- [ ] Add Sodhya Pinda computation with chakra Graha Pinda + per-sign Rashi Pinda constants.
- [ ] Build 10 golden chart fixtures cross-verified at ±0 tolerance against JH 7.x (BAV + SAV + Sodhya Pinda).
- [ ] Property tests: post-shodhanai bindu counts ≤ pre-shodhanai; per-graha totals ≤ classical max (48/49/39/54/56/52/39).
- [ ] D9 Navamsam Ashtakavargam pipeline parallel to D1 (same 6 stages applied to D9 planetary positions).
- [ ] Contributor-trace recompute API endpoint (on-demand; not stored).
- [ ] Kaksha Vibhaga per-graha 96-kaksha table + API surface for astrologer panel.

---

## 3. Classical / Technical Research

### 3.1 Raw Bhinnashtakavarga (BAV) — already implemented, included here for framing

**Source:** BPHS Ch. 65.

For each of 7 planets (Sun through Saturn; Rahu and Ketu excluded in classical BAV per BPHS Ch. 65 v.2), a 12-column bindu matrix is built by contributions from 8 reference points (Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, and Lagna). Each contributor "gives" a bindu to specific houses relative to itself, per classical tables.

Output (pre-shodhana):

```
BAV[planet][sign] ∈ {0, 1, 2, ..., 8}      # 8 = maximum possible
Σ_sign BAV[planet][sign] ≤ 56              # total per planet (upper bound)
```

**Sarvashtakavarga (SAV):** `SAV[sign] = Σ_planet BAV[planet][sign]`. Used as whole-chart strength map.

Existing Josi implementation at `src/josi/services/ashtakavarga_calculator.py` covers this accurately for all 7 planets. **Retain unchanged**; v2 consumes its output as input.

### 3.2 Trikona Shodhana — BPHS Ch. 66 v.1–5

**Citation:** BPHS Ch. 66 verses 1–5 (*triKoṇaśodhanaṁ*).

**Intuition:** A trikona is a trinal group of signs (1-5-9, 2-6-10, 3-7-11, 4-8-12). Within each trikona, there are three signs. Classical reasoning says bindus duplicated across the trikona are redundant "noise"; the *minimum* bindu count across the three signs is the common base that every trikona member shares, and can be subtracted to surface the differential.

**Algorithm (applied per planet's BAV):**

For each of the 4 trikona groups: `T1={1,5,9}`, `T2={2,6,10}`, `T3={3,7,11}`, `T4={4,8,12}`:

```
for trikona in [{1,5,9}, {2,6,10}, {3,7,11}, {4,8,12}]:
    values = [BAV[planet][sign] for sign in trikona]
    if 0 in values:
        # classical exception (BPHS 66.4): if any member has 0, skip subtraction
        continue
    m = min(values)
    for sign in trikona:
        BAV[planet][sign] -= m
```

Applied to all 7 planets' BAVs independently. The result is called **Trikona Shuddhi BAV**.

**Rationale for the "0 skip" exception:** Subtracting from a zero would go negative, which is meaningless in bindu arithmetic. BPHS v.4 explicitly instructs: *yasminn ekopi bindur na syāt tasya triKoṇaśodhanaṁ na syāt* ("if any [member] has even one bindu missing, its trikona is not purified").

**Worked example (classical test case, B.V. Raman, A Catechism of Astrology, Example 14):**

Sun's BAV:
```
Signs:   1  2  3  4  5  6  7  8  9  10 11 12
Binds:   4  5  3  6  5  4  2  3  6  4  3  5
```

Trikonas:
- T1 {1,5,9}: values=[4,5,6], min=4 → subtract 4 → [0,1,2]
- T2 {2,6,10}: [5,4,4], min=4 → [1,0,0]
- T3 {3,7,11}: [3,2,3], min=2 → [1,0,1]
- T4 {4,8,12}: [6,3,5], min=3 → [3,0,2]

Sun's Trikona-Shuddhi BAV: `[0,1,1,3,1,0,0,0,2,0,1,2]`.

### 3.3 Ekadhipatya Shodhana — BPHS Ch. 66 v.6–15

**Citation:** BPHS Ch. 66 verses 6–15 (*ekādhipatyaśodhanaṁ*).

**Intuition:** Five planets own two signs each (Mars: Aries+Scorpio; Mercury: Gemini+Virgo; Jupiter: Sagittarius+Pisces; Venus: Taurus+Libra; Saturn: Capricorn+Aquarius). Sun owns only Leo; Moon owns only Cancer — so they are exempt. Having bindus in both signs of the same lord is a form of "duplication of lordship" (ekādhipatya), and the classical rule sets one of the two to zero under specified conditions, allocating the bindu weight to the "stronger" sign.

**Algorithm (applied per planet's Trikona-Shuddhi BAV, after §3.2):**

For each pair of co-owned signs (signA, signB) belonging to the same lord L:

```
Let V_A = BAV[planet][signA]   (post-trikona value)
Let V_B = BAV[planet][signB]

Let occA = (L occupies signA? 1 : 0)              # does L itself sit in signA in the natal chart?
Let occB = (L occupies signB? 1 : 0)
# In BPHS "occupies" means a planet is in the sign; for this algorithm, L-occupancy is the critical case,
# but classical texts also consider any planet occupying the sign.

Let any_planet_in_A = (any natal planet in signA?)
Let any_planet_in_B = (any natal planet in signB?)
```

The classical ruleset from BPHS 66.7–13 (distilled into a deterministic decision table):

| Case | Condition | Rule |
|---|---|---|
| (1) | Both signs occupied by planets AND V_A = V_B | Both retain their bindus (no change) |
| (2) | Both signs occupied by planets AND V_A > V_B | Set V_B = 0; V_A unchanged |
| (3) | Both signs occupied by planets AND V_A < V_B | Set V_A = 0; V_B unchanged |
| (4) | Only signA occupied (V_B's sign empty) AND V_A ≥ V_B | Set V_B = 0; V_A unchanged |
| (5) | Only signA occupied AND V_A < V_B | Set V_A = 0; V_B unchanged (the non-occupied but higher-bindu sign retains) |
| (6) | Only signB occupied | Symmetric mirror of cases 4/5 |
| (7) | Neither sign occupied AND V_A > V_B | Set V_B = 0 |
| (8) | Neither sign occupied AND V_A < V_B | Set V_A = 0 |
| (9) | Neither sign occupied AND V_A = V_B | Both retain (or set both = 0 — see variant) |

**Variant for case (9):** BPHS verse 13 is terse; Phaladeepika (Ch.5) prescribes "both set to 0" for the neither-occupied-equal case, interpreting duplication-without-strength as pure noise. Saravali keeps both. Josi default: **Phaladeepika variant (both zero)** for neither-occupied-equal (rationale: conservative, matches JH 7.x). Configurable via rule variant in v2 if needed.

Iterate over all 5 co-owned-pair cases per planet (Mars/Mercury/Jupiter/Venus/Saturn). For Sun and Moon, single-sign owners, no Ekadhipatya applies — their BAVs pass through unchanged.

**Worked example (continuation from §3.2 Sun BAV Trikona-Shuddhi):**

`[0,1,1,3,1,0,0,0,2,0,1,2]` (signs 1–12)

Mars pair: sign 1 (Aries, V=0) and sign 8 (Scorpio, V=0). Both zero — no effect.
Mercury pair: sign 3 (Gemini, V=1) and sign 6 (Virgo, V=0). One side zero → classical rule: the zero stays zero, the nonzero stays. No change.
Jupiter pair: sign 9 (V=2) and sign 12 (V=2). Equal. Apply natal-occupancy check from chart; assume neither sign occupied → case (9) Phaladeepika variant → both zero.
Venus pair: sign 2 (V=1) and sign 7 (V=0). No change.
Saturn pair: sign 10 (V=0) and sign 11 (V=1). No change.

Result (Sun Ekadhipatya-Shuddhi BAV): `[0,1,1,3,1,0,0,0,0,0,1,0]`. Sum = 7.

### 3.4 Sodhya Pinda — BPHS Ch. 67

**Citation:** BPHS Ch. 67 (*Śodhyapiṇḍādhyāya*).

**Purpose:** Convert the doubly-shodhit BAV into a single numeric planet-pinda ("purified pile") value. Used downstream for ayurdaya (lifespan) estimation (deferred to E6b), and for relative planetary strength.

**Formula:**

```
sodhya_pinda[planet] = Σ_sign (shodhit_BAV[planet][sign] × rashi_pinda[sign] × graha_pinda[planet][sign])
```

Where:

**Rashi Pinda** (BPHS 67.2) — fixed weighting by sign:

| Sign | Weight |
|---|---|
| 1 Aries | 7 |
| 2 Taurus | 10 |
| 3 Gemini | 8 |
| 4 Cancer | 4 |
| 5 Leo | 10 |
| 6 Virgo | 6 |
| 7 Libra | 7 |
| 8 Scorpio | 8 |
| 9 Sagittarius | 9 |
| 10 Capricorn | 5 |
| 11 Aquarius | 11 |
| 12 Pisces | 12 |

(These numerical weights are classical tradition; BPHS gives them without derivation.)

**Graha Pinda** (BPHS 67.3–5) — weight that each planet gives *to each sign*, for that planet's own Sodhya Pinda. This is a 7×12 matrix. Values are classical and given in BPHS; reference table appears in `src/josi/db/rules/ashtakavarga/graha_pinda_bphs.yaml` (see §5.3).

**Example form (Sun Graha Pinda, BPHS 67.3):**

| Sign | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Sun's weight | 5 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

(Sun's Graha Pinda weights concentrate on its own sign Leo and exaltation Aries.)

Full 7×12 table loaded from YAML; see T-E2a.3.

### 3.5 Output shape

Reusing `numeric_matrix` output shape (F7):

```json
{
  "matrix": [ [int]*12 ]*7,       // 7 planets × 12 signs
  "row_labels": ["sun","moon","mars","mercury","jupiter","venus","saturn"],
  "col_labels": ["aries","taurus", ... ,"pisces"],
  "metadata": {
    "variant": "raw" | "trikona_shuddhi" | "ekadhipatya_shuddhi" | "sodhya_pinda",
    "citation": "BPHS Ch.66 v.1-5",
    "computed_at": "..."
  }
}
```

**Four rows in `technique_compute`** per chart per source:
- `rule_id = "ashtakavarga.bav.bphs"` → raw BAV
- `rule_id = "ashtakavarga.trikona_shuddhi.bphs"` → after trikona
- `rule_id = "ashtakavarga.ekadhipatya_shuddhi.bphs"` → after ekadhipatya
- `rule_id = "ashtakavarga.sodhya_pinda.bphs"` → sodhya pinda (7-element vector; encoded as 7×1 matrix for shape uniformity)

Stored separately so aggregation strategies and auditability can reference each stage.

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| Overwrite BAV in place or store separate variants? | Separate variants (4 compute rows) | Auditability; each stage can be independently cited in AI responses |
| Case (9) of Ekadhipatya (neither occupied, equal) — Phaladeepika (both zero) or Saravali (both retain)? | Phaladeepika (both zero) default | Matches JH 7.x; conservative; Saravali variant ships as alternate rule for P2 |
| Include Rahu/Ketu in BAV? | No (BPHS 65.2) | Classical Ashtakavarga is 7-planet |
| Sodhya Pinda — produce vector or scalar per planet? | Scalar per planet (7 values) | Classical definition; downstream consumers expect single number per planet |
| What counts as "planet occupying a sign" for Ekadhipatya? | Any of 7 planets (Sun–Saturn) per BPHS; Rahu/Ketu exclusion consistent with 7-planet framing | Ambiguity in verse; BPHS precedence |
| Float arithmetic anywhere? | No — all bindu and pinda math is integer | Classical texts use integers; avoids any rounding risk |
| Refactor existing `ashtakavarga_calculator.py`? | Wrap, don't replace | Minimize regression risk; new engine delegates raw BAV to existing module |

## 5. Component Design

### 5.1 New modules

```
src/josi/services/classical/ashtakavarga/
├── __init__.py
├── ashtakavarga_engine.py         # main ClassicalEngine implementation
├── trikona_shodhana.py            # pure function
├── ekadhipatya_shodhana.py        # pure function
└── sodhya_pinda.py                # pure function

src/josi/db/rules/ashtakavarga/
├── bav_bphs.yaml                  # raw BAV (wraps existing calculator)
├── trikona_shuddhi_bphs.yaml
├── ekadhipatya_shuddhi_bphs.yaml
├── sodhya_pinda_bphs.yaml
├── graha_pinda_bphs.yaml          # 7×12 data table, referenced by sodhya_pinda rule
└── rashi_pinda_bphs.yaml          # 12-element data table

tests/golden/charts/ashtakavarga/
├── chart_01_expected_shodhana.yaml     # all 4 variants for 10 charts
├── ...
└── chart_10_expected_shodhana.yaml
```

### 5.2 Data model additions

No new tables. Four new `classical_rule` rows; compute rows flow through existing `technique_compute` schema.

### 5.3 Rule YAML

**`trikona_shuddhi_bphs.yaml`:**

```yaml
rule_id: ashtakavarga.trikona_shuddhi.bphs
source_id: bphs
version: "1.0.0"
technique_family_id: ashtakavarga
output_shape_id: numeric_matrix
citation: "BPHS Ch.66 v.1-5"
classical_names:
  en: "Trikona Shodhana"
  sa_iast: "Trikoṇaśodhana"
  sa_devanagari: "त्रिकोणशोधन"
  ta: "திரிகோண சோதனை"
effective_from: "2026-01-01T00:00:00Z"
effective_to: null

activation:
  predicate:
    op: depends_on
    rule_id: ashtakavarga.bav.bphs       # needs raw BAV as input

compute:
  engine: ashtakavarga_trikona_shodhana
  input:
    from_rule: ashtakavarga.bav.bphs
  algorithm:
    trikonas:
      - [1, 5, 9]
      - [2, 6, 10]
      - [3, 7, 11]
      - [4, 8, 12]
    # Phaladeepika 3-case rule (Ch.26 v.12-18) — revised 2026-04-22
    reduction_rule: phaladeepika_3_case
    zero_all_if_any_member_is_zero: true      # edge case 1: any zero → zero all three
    zero_all_if_min_tied_2_or_more: true      # edge case 2: tie at min → zero all three
    else_subtract_minimum: true                # normal case
  output:
    matrix_dim: [7, 12]
    row_labels: [sun, moon, mars, mercury, jupiter, venus, saturn]
    col_labels: [aries, taurus, gemini, cancer, leo, virgo, libra, scorpio, sagittarius, capricorn, aquarius, pisces]
```

**`ekadhipatya_shuddhi_bphs.yaml`:**

```yaml
rule_id: ashtakavarga.ekadhipatya_shuddhi.bphs
source_id: bphs
version: "1.0.0"
technique_family_id: ashtakavarga
output_shape_id: numeric_matrix
citation: "BPHS Ch.66 v.6-15"
classical_names:
  en: "Ekadhipatya Shodhana"
  sa_iast: "Ekādhipatyaśodhana"
  sa_devanagari: "एकाधिपत्यशोधन"

activation:
  predicate:
    op: depends_on
    rule_id: ashtakavarga.trikona_shuddhi.bphs

compute:
  engine: ashtakavarga_ekadhipatya_shodhana
  input:
    from_rule: ashtakavarga.trikona_shuddhi.bphs
  algorithm:
    co_owned_pairs:
      - { lord: mars,    signs: [1, 8] }      # Aries + Scorpio
      - { lord: mercury, signs: [3, 6] }      # Gemini + Virgo
      - { lord: jupiter, signs: [9, 12] }     # Sagittarius + Pisces
      - { lord: venus,   signs: [2, 7] }      # Taurus + Libra
      - { lord: saturn,  signs: [10, 11] }    # Capricorn + Aquarius
    equal_neither_occupied_variant: phaladeepika   # "both_zero" | "both_retain"
  output:
    matrix_dim: [7, 12]
    row_labels: [sun, moon, mars, mercury, jupiter, venus, saturn]
    col_labels: [aries, taurus, gemini, cancer, leo, virgo, libra, scorpio, sagittarius, capricorn, aquarius, pisces]
```

**`rashi_pinda_bphs.yaml`:**

```yaml
rule_id: ashtakavarga.rashi_pinda.bphs
source_id: bphs
version: "1.0.0"
technique_family_id: ashtakavarga
output_shape_id: numeric_matrix
citation: "BPHS Ch.67 v.2"

compute:
  engine: data_table
  weights:
    - { sign: 1,  name: aries,       weight: 7 }
    - { sign: 2,  name: taurus,      weight: 10 }
    - { sign: 3,  name: gemini,      weight: 8 }
    - { sign: 4,  name: cancer,      weight: 4 }
    - { sign: 5,  name: leo,         weight: 10 }
    - { sign: 6,  name: virgo,       weight: 6 }
    - { sign: 7,  name: libra,       weight: 7 }
    - { sign: 8,  name: scorpio,     weight: 8 }
    - { sign: 9,  name: sagittarius, weight: 9 }
    - { sign: 10, name: capricorn,   weight: 5 }
    - { sign: 11, name: aquarius,    weight: 11 }
    - { sign: 12, name: pisces,      weight: 12 }
```

**`graha_pinda_bphs.yaml`:** (abbreviated; full values authored from BPHS 67.3–5)

```yaml
rule_id: ashtakavarga.graha_pinda.bphs
source_id: bphs
version: "1.0.0"
technique_family_id: ashtakavarga
output_shape_id: numeric_matrix
citation: "BPHS Ch.67 v.3-5"

compute:
  engine: data_table
  matrix:
    # rows: planets in order [sun, moon, mars, mercury, jupiter, venus, saturn]
    # cols: signs 1..12
    - [5,  0,  0,  0, 10,  0,  0,  0,  0,  0,  0,  0]      # Sun
    - [0,  0,  0, 10,  0,  0,  0,  0,  0,  0,  0,  0]      # Moon (concentrated on Cancer)
    - [5,  0,  0,  0,  0,  0,  0, 10,  0,  0,  0,  0]      # Mars (own: Aries+Scorpio)
    - [0,  0, 10,  0,  0, 10,  0,  0,  0,  0,  0,  0]      # Mercury (Gemini+Virgo own)
    - [0,  0,  0, 10,  0,  0,  0,  0, 10,  0,  0, 10]      # Jupiter (Sag+Pisces own, Cancer exalted; approx)
    - [0, 10,  0,  0,  0,  0, 10,  0,  0,  0,  0, 10]      # Venus (Taurus+Libra own, Pisces exalted)
    - [0,  0,  0,  0,  0,  0, 10,  0,  0, 10, 10,  0]      # Saturn (Capricorn+Aquarius own, Libra exalted)
# NOTE: exact classical values to be re-verified against BPHS Ch.67 v.3-5 during T-E2a.3 content authoring.
# These are illustrative and SHOULD NOT ship without cross-check against a print edition (Santhanam 2004).
```

**`sodhya_pinda_bphs.yaml`:**

```yaml
rule_id: ashtakavarga.sodhya_pinda.bphs
source_id: bphs
version: "1.0.0"
technique_family_id: ashtakavarga
output_shape_id: numeric_matrix
citation: "BPHS Ch.67 v.1-10"

activation:
  predicate:
    op: all_of
    clauses:
      - { op: depends_on, rule_id: ashtakavarga.ekadhipatya_shuddhi.bphs }
      - { op: depends_on, rule_id: ashtakavarga.rashi_pinda.bphs }
      - { op: depends_on, rule_id: ashtakavarga.graha_pinda.bphs }

compute:
  engine: ashtakavarga_sodhya_pinda
  formula: "sum over sign of (shodhit_BAV[planet][sign] * rashi_pinda[sign] * graha_pinda[planet][sign])"
  output:
    matrix_dim: [7, 1]
    row_labels: [sun, moon, mars, mercury, jupiter, venus, saturn]
    col_labels: [sodhya_pinda]
```

### 5.4 Engine interface

```python
# src/josi/services/classical/ashtakavarga/ashtakavarga_engine.py

class AshtakavargaEngine(BaseClassicalEngine):
    technique_family_id = "ashtakavarga"

    def __init__(self, raw_calculator: AshtakavargaCalculator):
        """Wraps existing raw-BAV calculator; adds shodhana stages."""
        self._raw = raw_calculator

    async def compute_for_source(
        self, session: AsyncSession, chart_id: UUID, source_id: str,
        rule_ids: list[str] | None = None,
    ) -> list[TechniqueComputeRow]:
        chart = await load_chart(session, chart_id)

        # Stage 1: raw BAV (delegates to existing calculator)
        raw_bav = self._raw.compute(chart)                  # 7×12 int matrix

        # Stage 2: trikona
        trikona = apply_trikona_shodhana(raw_bav)

        # Stage 3: ekadhipatya
        ekadhi = apply_ekadhipatya_shodhana(
            trikona, chart_planets=chart.planet_positions,
            equal_variant="phaladeepika",
        )

        # Stage 4: sodhya pinda
        sodhya = compute_sodhya_pinda(
            ekadhi, rashi_pinda=RASHI_PINDA, graha_pinda=GRAHA_PINDA,
        )

        # Emit 4 compute rows (one per rule_id)
        return [
            TechniqueComputeRow(rule_id="ashtakavarga.bav.bphs", result=NumericMatrixResult(matrix=raw_bav, ...)),
            TechniqueComputeRow(rule_id="ashtakavarga.trikona_shuddhi.bphs", result=NumericMatrixResult(matrix=trikona, ...)),
            TechniqueComputeRow(rule_id="ashtakavarga.ekadhipatya_shuddhi.bphs", result=NumericMatrixResult(matrix=ekadhi, ...)),
            TechniqueComputeRow(rule_id="ashtakavarga.sodhya_pinda.bphs", result=NumericMatrixResult(matrix=sodhya, ...)),
        ]
```

```python
# src/josi/services/classical/ashtakavarga/trikona_shodhana.py

def apply_trikona_shodhana(bav: list[list[int]]) -> list[list[int]]:
    """Pure function. Returns new matrix; does not mutate input."""
    TRIKONAS = [(0, 4, 8), (1, 5, 9), (2, 6, 10), (3, 7, 11)]   # 0-indexed
    result = [row[:] for row in bav]
    for planet_idx in range(7):
        for trikona in TRIKONAS:
            values = [result[planet_idx][s] for s in trikona]
            if 0 in values:
                continue                       # BPHS 66.4 exception
            m = min(values)
            for s in trikona:
                result[planet_idx][s] -= m
    return result
```

### 5.5 REST API contract

```
GET /api/v1/ashtakavarga/{chart_id}?variant=all
GET /api/v1/ashtakavarga/{chart_id}?variant=raw
GET /api/v1/ashtakavarga/{chart_id}?variant=trikona_shuddhi
GET /api/v1/ashtakavarga/{chart_id}?variant=ekadhipatya_shuddhi
GET /api/v1/ashtakavarga/{chart_id}?variant=sodhya_pinda

Response (variant=all):
{
  "success": true,
  "message": "Ashtakavarga computed",
  "data": {
    "raw": { "matrix": [[...]], "row_labels": [...], "col_labels": [...], "citation": "BPHS Ch.65" },
    "trikona_shuddhi": { "matrix": [[...]], ..., "citation": "BPHS Ch.66 v.1-5" },
    "ekadhipatya_shuddhi": { "matrix": [[...]], ..., "citation": "BPHS Ch.66 v.6-15" },
    "sodhya_pinda": { "values": {"sun": 274, "moon": 312, ...}, "citation": "BPHS Ch.67" },
    "sarvashtakavarga": { "per_sign": [int]*12, "total": int }
  },
  "errors": null
}
```

### 5.6 AI tool extension

```python
@tool
def get_ashtakavarga_summary(
    chart_id: str,
    variant: Literal["raw", "trikona_shuddhi", "ekadhipatya_shuddhi", "sodhya_pinda"] = "ekadhipatya_shuddhi",
    planet: Literal["sun", "moon", "mars", ...] | None = None,
) -> AshtakavargaSummary:
    """Returns post-shodhana BAV for the named variant; if planet given, returns only that row.
       Default variant is doubly-shodhit (classical practice)."""
```

## 6. User Stories

### US-E2a.1: As an astrologer, I want to see post-shodhana BAV (not raw) as the default
**Acceptance:** Astrologer UI default variant is `ekadhipatya_shuddhi`; raw is opt-in via toggle. AI chat default invocation returns `ekadhipatya_shuddhi`.

### US-E2a.2: As a classical scholar reviewing outputs, I want each shodhana stage cited separately
**Acceptance:** Every matrix returned carries a `citation` field; `raw` cites BPHS Ch.65, `trikona_shuddhi` cites BPHS 66.1-5, `ekadhipatya_shuddhi` cites BPHS 66.6-15, `sodhya_pinda` cites BPHS 67.

### US-E2a.3: As an engineer, I want to verify against JH 7.x
**Acceptance:** 10 golden charts compute all 4 variants; JH-verified expected matrices cross-checked within exact equality (integer arithmetic; no tolerance needed).

### US-E2a.4: As a classical advisor, I want to swap the Ekadhipatya equal-case variant from Phaladeepika to Saravali
**Acceptance:** Editing `equal_neither_occupied_variant: saravali` in the rule YAML and redeploying produces different compute rows; old compute rows retained under old rule version.

### US-E2a.5: As an AI chat agent, I can answer "What's my Jupiter Sodhya Pinda?"
**Acceptance:** `get_ashtakavarga_summary(variant='sodhya_pinda', planet='jupiter')` returns integer with citation.

## 7. Tasks

### T-E2a.1: Author trikona shodhana function and tests
- **Definition:** Pure function `apply_trikona_shodhana(bav: list[list[int]]) -> list[list[int]]`. Matches §3.2 worked example exactly.
- **Acceptance:** Unit tests on B.V. Raman Example 14 pass; zero-exception verified.
- **Effort:** 0.5 day
- **Depends on:** existing raw BAV calculator

### T-E2a.2: Author ekadhipatya shodhana function and tests
- **Definition:** Pure function `apply_ekadhipatya_shodhana(bav, chart_planets, equal_variant)`. Full 9-case table per §3.3.
- **Acceptance:** Unit tests cover all 9 cases; at least 2 tests per case (typical + edge).
- **Effort:** 1.5 days

### T-E2a.3: Author rashi_pinda + graha_pinda YAML and verify against BPHS
- **Definition:** Write YAML data tables for both. Cross-check each value against a print edition of BPHS Ch. 67 (Santhanam 2004 translation). Classical advisor PR review required.
- **Acceptance:** All 7×12 graha_pinda values verified; rashi_pinda 12 values verified.
- **Effort:** 1 day (includes manual verification)

### T-E2a.4: Sodhya Pinda computation
- **Definition:** Function `compute_sodhya_pinda(shodhit_bav, rashi_pinda, graha_pinda) -> dict[str, int]`. Applies formula §3.4.
- **Acceptance:** Unit tests with hand-computed values for 3 sample charts.
- **Effort:** 0.5 day
- **Depends on:** T-E2a.2, T-E2a.3

### T-E2a.5: Build `AshtakavargaEngine` and wire `ClassicalEngine` Protocol
- **Definition:** Engine that orchestrates the 4 stages, emits 4 compute rows with correct rule_ids, idempotent.
- **Acceptance:** Protocol conformance; integration test verifies rows land in DB.
- **Effort:** 1 day
- **Depends on:** T-E2a.1, T-E2a.2, T-E2a.4

### T-E2a.6: Author rule YAML files (4 rules)
- **Definition:** Write 4 rule YAMLs (trikona, ekadhipatya, rashi_pinda, graha_pinda, sodhya_pinda) per §5.3. F6 loader ingests.
- **Acceptance:** Loader inserts 5 rows (4 rules + 2 data-table rules); content hashes stable.
- **Effort:** 0.5 day
- **Depends on:** F6, T-E2a.3

### T-E2a.7: Golden chart fixtures (10 charts)
- **Definition:** 10 birth charts with expected raw, trikona, ekadhipatya, sodhya_pinda matrices. Verified against JH 7.x by exact integer equality.
- **Acceptance:** Fixtures parse; classical-advisor review-signed; 10 charts cross-checked.
- **Effort:** 3 days (JH verification is manual per chart)
- **Depends on:** T-E2a.5

### T-E2a.8: Property tests (F17)
- **Definition:** Hypothesis-driven: (a) post-trikona bindu ≤ pre-trikona for every (planet, sign), (b) post-ekadhipatya ≤ post-trikona, (c) total bindus across 12 signs per planet ≤ 56, (d) sodhya pinda values are non-negative, (e) re-applying trikona to already-trikona-shuddhi yields same result (idempotency of the shodhana function on already-purified input).
- **Acceptance:** 1000 Hypothesis examples per property all pass.
- **Effort:** 1 day
- **Depends on:** T-E2a.5

### T-E2a.9: REST endpoint extension
- **Definition:** Extend `/api/v1/ashtakavarga/{chart_id}` with `?variant=` query param. Default `all`.
- **Acceptance:** All 5 variant values return valid shapes; 4xx for unknown.
- **Effort:** 0.5 day
- **Depends on:** T-E2a.5

### T-E2a.10: AI tool `get_ashtakavarga_summary`
- **Definition:** Typed tool per §5.6; default variant is `ekadhipatya_shuddhi`; citation embedded.
- **Acceptance:** Integration test with chat agent.
- **Effort:** 0.5 day
- **Depends on:** T-E2a.9

### T-E2a.11: Differential test vs Jagannatha Hora
- **Definition:** For 10 golden charts, compare all 4 matrices element-wise to JH 7.x outputs.
- **Acceptance:** 100% exact match (integer equality) across 10 charts × 4 variants = 40 assertions.
- **Effort:** 1 day (JH runs + scripting)
- **Depends on:** T-E2a.7

## 8. Unit Tests

### 8.1 Trikona Shodhana

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_trikona_bvr_example14_sun` | B.V. Raman Example 14 Sun BAV | `[0,1,1,3,1,0,0,0,2,0,1,2]` | Canonical worked example |
| `test_trikona_zero_skip_rule` | `[0, 5, 3, ...]` in T1 | no subtraction in T1 | BPHS 66.4 exception |
| `test_trikona_all_equal_trikona` | `[4, 4, 4, ...]` in T1 | `[0, 0, 0, ...]` | Equal min case |
| `test_trikona_idempotent` | Run twice on same BAV | Second run = no-op | Shodhana applied to shodhit input |
| `test_trikona_does_not_mutate_input` | `input` after call | unchanged | Purity |
| `test_trikona_per_planet_independent` | Only Sun BAV modified | Moon BAV unchanged | Independence |

### 8.2 Ekadhipatya Shodhana (all 9 cases)

| Test name | Case | Input setup | Expected behavior | Rationale |
|---|---|---|---|---|
| `test_ekadhi_case_1_both_occupied_equal` | 1 | V_A=V_B=3, both occupied | Both retain (3,3) | BPHS 66.7 |
| `test_ekadhi_case_2_both_occupied_A_greater` | 2 | V_A=5, V_B=3, both occupied | V_B=0 | BPHS 66.8 |
| `test_ekadhi_case_3_both_occupied_B_greater` | 3 | V_A=2, V_B=6, both occupied | V_A=0 | BPHS 66.8 mirror |
| `test_ekadhi_case_4_only_A_occupied_A_ge_B` | 4 | V_A=4, V_B=3, only A occupied | V_B=0 | BPHS 66.10 |
| `test_ekadhi_case_5_only_A_occupied_A_lt_B` | 5 | V_A=2, V_B=6, only A occupied | V_A=0 | BPHS 66.11 |
| `test_ekadhi_case_6_only_B_occupied` | 6 | mirror of 4/5 | mirror behavior | Symmetry |
| `test_ekadhi_case_7_neither_A_greater` | 7 | V_A=5, V_B=3, neither occupied | V_B=0 | BPHS 66.12 |
| `test_ekadhi_case_8_neither_B_greater` | 8 | V_A=2, V_B=6, neither occupied | V_A=0 | BPHS 66.12 mirror |
| `test_ekadhi_case_9_phaladeepika` | 9 | V_A=V_B=4, neither occupied, variant=phaladeepika | Both zero | Phaladeepika rule |
| `test_ekadhi_case_9_saravali` | 9 | same, variant=saravali | Both retain | Saravali variant |
| `test_ekadhi_sun_moon_pass_through` | — | Any BAV for sun/moon | Unchanged by ekadhi | Single-sign owners exempt |
| `test_ekadhi_does_not_mutate_trikona_input` | — | trikona matrix unchanged | purity | Pure fn |

### 8.3 Sodhya Pinda

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_sodhya_pinda_formula_correct` | Known BAV + known pindas | Hand-computed value | Formula fidelity |
| `test_sodhya_pinda_zero_bav_zero_result` | All zeros | All zeros | Identity |
| `test_sodhya_pinda_non_negative` | Any valid input | All values ≥ 0 | Range invariant |

### 8.4 Engine integration

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_engine_emits_4_rows` | One chart | 4 `technique_compute` rows, one per rule_id | Multi-stage emission |
| `test_engine_idempotent` | Run twice | 4 rows total (ON CONFLICT DO NOTHING) | Idempotency |
| `test_engine_rule_version_pinned` | Inspect compute rows | All have `rule_version = '1.0.0'` | Version-lock |
| `test_engine_content_hash_in_provenance` | Inspect `input_fingerprint` | Matches F13 canonical hash | Provenance |

### 8.5 Rule registry

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_rules_loaded_from_yaml` | F6 loader run | 5 new rows (incl. data tables) | YAML wiring |
| `test_graha_pinda_values_match_bphs` | Table fixture vs Santhanam 2004 | Equal | Content authoring |

### 8.6 Golden suite

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_golden_chart_01_all_variants` | chart_01 fixture | All 4 matrices element-wise equal to JH 7.x | Differential |
| ... (×10 charts) | | | |

### 8.7 Property tests

| Test name | Invariant | Rationale |
|---|---|---|
| `test_trikona_monotonic` | post-trikona bindu ≤ pre-trikona always | Shodhana never adds bindus |
| `test_ekadhi_monotonic` | post-ekadhi bindu ≤ post-trikona always | Same |
| `test_bav_upper_bound` | Σ_sign BAV[planet][sign] ≤ 56 for any planet | Classical upper bound |
| `test_sodhya_pinda_non_negative` | All sodhya values ≥ 0 | Non-negativity |
| `test_engine_output_deterministic` | Same input → same `output_hash` | F13 provenance |

## 9. EPIC-Level Acceptance Criteria

- [ ] `AshtakavargaEngine` implements `ClassicalEngine` Protocol
- [ ] 4 rule rows + 2 data-table rows loaded into `classical_rule` via F6
- [ ] Trikona shodhana matches B.V. Raman Example 14 exactly
- [ ] Ekadhipatya shodhana 9-case table implemented; Phaladeepika variant default
- [ ] Sodhya Pinda produces non-negative 7-element vector
- [ ] REST endpoint `/api/v1/ashtakavarga/{chart_id}?variant=` returns all 4 variants
- [ ] AI tool `get_ashtakavarga_summary` works; default variant = `ekadhipatya_shuddhi`
- [ ] Golden suite: 10 charts × 4 variants = 40 assertions, 100% integer equality vs JH 7.x
- [ ] Property tests with ≥1000 examples per property all pass
- [ ] Unit test coverage ≥ 92% for new code
- [ ] Existing raw BAV behavior unchanged (regression tests green)
- [ ] Docs: `CLAUDE.md` notes 4-variant model; API docs show default is shodhit

## 10. Rollout Plan

- **Feature flag:** `ENABLE_ASHTAKAVARGA_SHODHANA` (default `true` on P1 deploy).
- **Shadow compute:** on staging, compute shodhana for 1000 charts; diff random sample against JH 7.x.
- **Backfill:** opportunistic. `chart_reading_view.ashtakavarga_summary` populated lazily.
- **Rollback:** flip flag → API `variant` falls back to `raw` only. Rules soft-deprecated via `effective_to`.

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Ekadhipatya case-9 variant choice disputed by a lineage | High | Low | Both variants shipped; astrologer preference flip |
| Graha Pinda values mis-transcribed from classical text | Medium | High | Dual review: engineer + classical advisor; JH differential test catches errors |
| "Planet occupying sign" interpretation ambiguity | Low | Medium | Explicit rule: "any of 7 planets in sign at birth"; documented |
| Raw BAV bug in existing calculator propagates to shodhana | Low | High | Retain existing tests; add assertion-tests that raw BAV row 0 (Sun) matches known chart |
| Integer overflow (Python handles; but Postgres column) | Low | Low | JSONB stores ints; max realistic sodhya pinda ~3000 → fits easily |
| Golden chart JH verification is manual, error-prone | Medium | High | 2-reviewer rule; screenshot JH output saved with fixtures |
| Documentation of "shodhit" as UI default confuses users expecting raw | Medium | Low | Tooltip + toggle; docs update |

## 12. References

- Master spec: [`docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`](../../../superpowers/specs/2026-04-19-classical-techniques-expansion-design.md)
- Classical sources:
  - Brihat Parashara Hora Shastra Ch. 65 (BAV), Ch. 66 (Shodhana), Ch. 67 (Sodhya Pinda). Santhanam translation (2004 ed., Ranjan Publications).
  - Phaladeepika by Mantreswara, Ch. 5 (Ekadhipatya equal-case variant).
  - Jataka Parijata Ch. 14 (cross-reference).
  - B.V. Raman, *A Catechism of Astrology*, Example 14 (worked trikona example).
- Existing Josi: `src/josi/services/ashtakavarga_calculator.py`
- Reference implementation: Jagannatha Hora 7.x (Ashtakavarga → Shodhya Pinda panel)
