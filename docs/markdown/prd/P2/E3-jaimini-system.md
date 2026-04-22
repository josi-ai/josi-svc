---
prd_id: E3
epic_id: E3
title: "Jaimini System (Chara Karakas, Arudhas, Rashi Drishti, Jaimini Yogas)"
phase: P2-breadth
tags: [#correctness, #extensibility, #i18n]
priority: must
depends_on: [F1, F2, F4, F6, F7, F8, F13, F16, F17, E1b]
enables: [E4b, E11b, E12, E14a]
classical_sources: [jaimini_sutras, bphs, saravali, jataka_parijata]
estimated_effort: 5-6 weeks
status: draft
author: @agent-claude-opus-4-7
last_updated: 2026-04-21
---

# E3 — Jaimini System (Chara Karakas, Arudhas, Rashi Drishti, Jaimini Yogas)

## 1. Purpose & Rationale

Jaimini astrology is a self-contained classical system, philosophically and computationally orthogonal to the predominantly planet-centric Parashari tradition. It is authoritatively rooted in the **Jaimini Upadesha Sutras** (attributed to sage Jaimini, ~300 BCE traditional) and elaborated through millennia of commentary (Somanatha's *Kalpalatha*, Nrisimha's *Vasantaraja*, Irangati Rangacharya's modern commentary).

The Jaimini system has four pillars that a calculation engine must produce:

1. **Chara Karakas** — *movable* significators. Unlike Parashari's fixed karakas (Sun=father, Moon=mother), Jaimini ranks the 7 (or 8) grahas by **sidereal longitude within sign** to assign a chart-specific hierarchy: Atmakaraka (soul), Amatyakaraka (career/counsel), Bhratrukaraka (siblings), Matrukaraka (mother), Putrakaraka (children), Gnatikaraka (relations/troubles), Darakaraka (spouse).
2. **Arudha Padas** — *reflection points*. For each house H (1 through 12), compute the Arudha A(H) = the sign the house "projects" into the world via its lord's placement. Arudha Lagna (AL = A1) represents the public image; Upapada (UL = A12) represents spouse/marriage. Classical calculation rules (Jaimini Sutras 1.2.39–1.2.45) have specific exceptions to prevent overlap with the house itself or its lord.
3. **Rashi Drishti** — *sign-based aspects*. A Jaimini aspect is cast **sign-to-sign**, not planet-to-planet. Movable signs aspect fixed signs (except adjacent); fixed signs aspect movable (except adjacent); dual signs aspect dual. This is qualitatively distinct from Parashari graha drishti (which is planet-centric with 3/7/10th special aspects for some planets).
4. **Jaimini Yogas** — a library of ~25 yogas that combine the above three pillars. Examples: Chara Karaka Raja Yoga (Atmakaraka + Amatyakaraka in mutual kendra); Karakamsa Yoga (planets in Karakamsa sign); Upapada-based marriage yogas; Arudha-based wealth yogas.

Without a dedicated Jaimini engine, Josi cannot serve Jaimini-practicing astrologers or produce the cross-tradition readings the master spec commits to (§1.5). Jaimini yogas are distinct from BPHS Parashari yogas (E4a/E4b) and must be computed against Chara Karakas + Arudhas + rashi drishti — which means E3 depends on its own foundational outputs (karakas and arudhas are produced first, then consumed by yogas).

This PRD establishes the full Jaimini calculation stack — the 4 pillars — and ships 15+ classical Jaimini yogas as its yoga library. It reuses the E1b Chara/Narayana Dasha outputs for context but does not re-implement them.

## 2. Scope

### 2.1 In scope

**Pillar 1 — Chara Karakas**
- Deterministic ranking of 7 grahas (Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn) by longitude-in-sign descending; assignment to AK, AmK, BK, MK, PK, GK, DK in that order.
- Alternate 8-karaka variant including Rahu (ranked by 30° − its longitude-in-sign, per Jaimini convention — Rahu's retrograde motion means "higher remaining" is equivalent to the other grahas' "higher elapsed").
- Tiebreak policy: when two grahas have longitudes within 1 arc-second, use lexicographic planet-id as deterministic fallback; log WARN.
- Output: `structured_positions` with 7 or 8 named positions.

**Pillar 2 — Arudha Padas**
- All 12 Arudhas: A1 (Arudha Lagna = AL), A2–A11, A12 (Upapada = UL).
- Calculation per Jaimini Sutras 1.2.39: count from house H to its lord's placement; project the same count forward from the lord's sign; the landed sign = Arudha.
- Exception rules per Jaimini Sutras 1.2.41–1.2.43: if the projected count lands in H itself (count=1) or in the 7th from H (count=7), project instead to the **10th from the lord** (preventing overlap with house/lord).
- Special arudhas: Bhava Pada (Arudha of each bhava), Pada Lagna (common alias for AL), Upapada (alias for UL). Document naming consistency.
- Output: `structured_positions` with 12 named positions.

**Pillar 3 — Rashi Drishti**
- Sign-to-sign aspect matrix per Jaimini Sutras 1.1.8–1.1.12.
- Per-sign aspect list: `aspects_cast_by(sign) → list[sign]`; `aspects_received_by(sign) → list[sign]`.
- Applied for yogas, dasa phalita (E11b), and astrologer UI overlays.
- Output: not a first-class technique; exposed as a predicate (`rashi_drishti_between(from, to)`) available to yoga rules.

**Pillar 4 — Jaimini Yogas (15+ shipped in E3)**
- Chara Karaka Raja Yoga (AK-AmK mutual kendra/trikona)
- Karakamsa Yoga (planets in Karakamsa = AK's Navamsha sign)
- Swamsha Yoga (planets in Swamsha = AK's Rashi)
- Upapada Yoga for marriage (Upapada lord placement)
- Ghati Arudha (A5) prosperity yoga
- Dara Karaka Kendra Yoga (DK in kendra from AL)
- Argala (obstruction) detection for AL — primary + secondary
- Virodha Argala (counter-obstruction)
- Chara Dasa Rashi-Drishti Phalita (conjunction of current dasa rasi + rashi-drishted planets)
- Atmakaraka-in-Lagna / Kendra / Trikona yogas
- Amatyakaraka-Atmakaraka conjunction
- Brahma Yoga (Jaimini variant)
- Maha Bhagya Yoga (Jaimini variant)
- Bandhana Yoga (bondage via Arudha)
- Niryana-Sthana Yoga (timing of death via 8th from AL)
- Additional 5+ from Jaimini Sutras Ch. 2–3.

Each yoga ships as a F6 DSL rule with explicit citation.

**REST API**
- `GET /api/v1/jaimini/{chart_id}/karakas`
- `GET /api/v1/jaimini/{chart_id}/arudhas`
- `GET /api/v1/jaimini/{chart_id}/rashi-drishti`
- `GET /api/v1/jaimini/{chart_id}/yogas`
- `GET /api/v1/jaimini/{chart_id}` — aggregated bundle

**AI tool-use**
- `get_chara_karakas(chart_id)` → 7 or 8 karakas
- `get_arudhas(chart_id)` → 12 arudhas
- `get_jaimini_yogas(chart_id)` → active yogas with citations
- `get_rashi_drishti(chart_id, from_sign)` → signs aspected
- Each tool response carries citations and confidence.

**Golden suite**
- 8 charts × 4 pillars = 32 fixture files, cross-verified against JH 7.x and secondary manual computation from Rangacharya examples.

### 2.2 Out of scope

- **Chara Dasha and Narayana Dasha** — produced by E1b; consumed here.
- **Padakrama Dasha variants beyond E1b** — deferred.
- **Additional ~50 Jaimini yogas** from obscure commentaries (Somanatha's 40+ yogas) — deferred to P4 reference-set expansion. E3 ships a focused 15+ high-usage set.
- **Phalita (outcome prediction) interpretation via Jaimini Rasi Drishti** — delegated to E11b (AI Chat debate mode).
- **Jaimini Bhava Pada chart visualization** — UI delegated to E12 (Astrologer Workbench).
- **Dasamsha or other vargas via Jaimini lens** — E7 owns extended vargas; E3 uses Navamsha only (for Karakamsa).
- **"Vedic Age" / "Dasa-Bhukti Phalita" narrative generation** — E11b.
- **Alternate Karakamsa definition (Swamsha = Atmakaraka's Rashi vs Karakamsa = Atmakaraka's Navamsha)** — both shipped but documented as distinct concepts, not alternate rules.

### 2.3 Dependencies

- F1 (source_authority with `jaimini_sutras`, `saravali`, `bphs`, `jataka_parijata` seeded)
- F2 (classical_rule, technique_compute tables)
- F4 (rule versioning)
- F6 (YAML rule loader + predicate library — adds Jaimini predicates)
- F7 (`structured_positions` + `boolean_with_strength` output shapes)
- F8 (engine Protocol + aggregation)
- F13 (content-hash provenance)
- F16 (golden chart suite)
- F17 (property tests)
- E1b (Chara/Narayana dasa outputs consumed by dasa-phalita yoga rules)
- Existing `AstrologyChart` schema: sidereal planet longitudes (already computed), Navamsha (D9) chart (already computed), house lords, planetary placements per sign.

## 2.4 Design Decisions (Pass 1 Astrologer Review — Locked 2026-04-21)

All open questions from E3 Pass 1 astrologer review are resolved. Cross-cutting decisions reference `DECISIONS.md`; E3-specific decisions documented here.

### Cross-cutting decisions (applied via `DECISIONS.md` + E1b)

| Decision | Value | Ref |
|---|---|---|
| 8-karaka Atmakaraka | Rahu included with `30°−long` rule | E1b Q1 / §2.4 |
| Ayanamsa default | Lahiri | 1.2 |
| Rahu/Ketu node type | Both Mean + True computed | 1.1 |
| Natchathiram count | 27 | 3.7 |
| Language display | Sanskrit-IAST + Tamil phonetic | 1.5 |
| Cross-source aggregation convention | Default + 1 variant per technique with astrologer toggle | E1b Q7 |

### E3-specific decisions (locked this review)

| Decision | Value | Source |
|---|---|---|
| **Chara Karaka tie-breaking** (Q1) | **Lexicographic planet-id fallback** (Sooriyan > Chandran > Sevvai > Budhan > Guru > Sukkiran > Sani > Rahu) + WARN log on sub-arcsecond tie. Matches JH + Astrosage. Same for both user types. | Q1 |
| **Arudha Pada exception rules source** (Q2) | **Jaimini Upadesha Sutras 1.2.39-45 canonical.** 2 exception rules only: (a) if Arudha = H itself → project to 10th from L; (b) if Arudha = 7th from H → project to 10th from L. Matches JH + PL + K.N. Rao + Astrosage + Rao. | Q2 |
| **Rashi Drishti matrix + node treatment** (Q3) | **Standard 12×12 matrix per JUS 1.1.8-12, node-agnostic.** Chara aspects 3 fixed (except adjacent); Sthira aspects 3 movable (except adjacent); Dwiswabhava aspects 3 other dual. Purely boolean (no graded strength). Rahu/Ketu occupy signs like any graha; no node-specific drishti modification. Exposed as astrologer-facing matrix view + internal `rashi_drishti_between(from, to)` predicate for yoga rules. | Q3 |
| **Jaimini yogas MVP list** (Q4) | **15 yogas balanced across 8 categories**, each cited to Jaimini Upadesha Sutras verse: (1) Chara Karaka Raja Yoga (JUS 1.2.11), (2) Karakamsa Yoga (JUS 1.3.1-3), (3) Swamsha Yoga (JUS 1.3.4-5), (4) Raja Sambandha Yoga (JUS 1.2.14), (5) Upapada Rahasya Yoga (JUS 2.1.10-15), (6) AL-Kendra Benefic Yoga (JUS 1.2.20-22), (7) AL-Upachaya Yoga (JUS 1.2.30), (8) Hara Yoga (commentary), (9) Karakamsa 5th Benefic Yoga (JUS 1.3.7), (10) Putra Karaka Yoga (JUS 1.2.19), (11) Argala to AL Yoga (JUS 1.2.35-38), (12) Virodha Argala Yoga (JUS 1.2.40), (13) AL-Drishti Rasi Raja Yoga (commentary), (14) Chara Karaka Dhana Yoga (commentary), (15) Mahapurusha Karaka Yoga (JUS 1.2.17). | Q4 |
| **Argala / Virodha Argala scope** (Q5) | **Generalized Argala from any reference bhava** (not AL-only as PRD original). Argala + Virodha Argala computable from Lagna, AL, any karaka position, any bhava. Astrologer UI has reference-point picker. Same for both user types. Matches GAP_CLOSURE lock + JH + Sanjay Rath SJVC. Classical Argala positions per JUS 1.2.35-38: Primary at 2/4/5/8/11, Subha at 3/12, Virodha Argala at counter positions. | Q5 |
| **Cross-source aggregation** (Q6) | **JUS canonical default + Rangacharya Kalpalatha variant per technique as astrologer-profile toggle.** Matches E1b Q7 convention. Per-technique application: Arudha (JUS default + Rangacharya extended exceptions toggle), Rashi Drishti (JUS deterministic — no variant), Argala (JUS generalized default + Rangacharya nuances toggle), Jaimini yogas (sibling rules where JUS + Rangacharya disagree; 2-option astrologer toggle). | Q6 |

### Engineering action items (not astrologer-review scope)

- [ ] 8-karaka AK ranking with lexicographic tie-break + WARN log (inherited from E1b)
- [ ] Arudha computation per JUS 1.2.39-45 with 2-exception rule
- [ ] Rashi Drishti 12×12 matrix as static lookup + `rashi_drishti_between(from, to)` predicate
- [ ] 15 Jaimini yoga rules as YAML under `src/josi/db/rules/jaimini_yoga/`
- [ ] Generalized Argala engine with reference-point parameter
- [ ] Rangacharya variant rules as sibling YAMLs per technique; astrologer profile toggle via F2
- [ ] Golden chart fixtures with known Jaimini yoga activations (from K.N. Rao / Rath published charts)

---

## 3. Classical / Technical Research

### 3.1 Chara Karakas — the movable significators

**Primary source:** Jaimini Upadesha Sutras, Book 1, Chapter 2, sutras 1.2.1–1.2.9. Canonical modern commentary: Rangacharya §2.1–§2.25.

#### 3.1.1 The 7-karaka list (Parashari school)

```
Atmakaraka   (AK)   → soul, self, chart "owner"
Amatyakaraka (AmK)  → career, minister, counsel
Bhratrukaraka (BK)  → siblings, co-borns
Matrukaraka  (MK)   → mother, nourishment
Putrakaraka  (PK)   → children, creativity
Gnatikaraka  (GK)   → kin, relations, troubles
Darakaraka   (DK)   → spouse, partner
```

7 grahas rank into 7 slots, in descending order of **longitude within their current sign** (i.e., degrees elapsed within the sign, from 0°00′ to 29°59′59″).

#### 3.1.2 Ranking rule

Per Jaimini Sutras 1.2.3:
> "atmadi-sapta-karakā uccatamā sphuṭānusāreṇa"
> "The seven karakas starting with Atmakaraka are [assigned] according to the highest [longitude in sign] downward."

Procedure:
1. For each of the 7 grahas (Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn), compute `lon_in_sign = sidereal_longitude mod 30°`.
2. Sort descending by `lon_in_sign`.
3. Assign top to AK, next to AmK, …, bottom to DK.

#### 3.1.3 The 8-karaka variant (with Rahu)

Per Jaimini Sutras 1.2.4 (disputed by some schools):
> "rāhu-sahitā aṣṭa-karakāḥ"
> "With Rahu [included], [there are] eight karakas."

Rahu moves retrograde in zodiacal order. Jaimini convention: compute Rahu's rank position by using **30° − Rahu's longitude-in-sign** (i.e., treating Rahu's elapsed retrograde motion as "ascending" degrees).

The 8-karaka list inserts **Pitrukaraka (PtK) = father** between MK and PK per some schools (Rangacharya §2.10); other schools retain the 7-name list but shift the 8th member to "Darakaraka" with roles of BK through DK re-assigned. Josi default: **7-karaka variant** (matches JH 7.x default, most commonly practiced). 8-karaka variant shipped as alternate rule `jaimini.karakas.eight_with_rahu.jaimini_sutras`.

#### 3.1.4 Tiebreaking

Two grahas with identical longitudes-in-sign to arc-second precision is vanishingly rare (~1 in 10^6 charts), but deterministically:

- **Classical tiebreak (Rangacharya §2.12):** the graha closer to the Lagna by aspectual proximity wins the higher slot.
- **Josi determinism (deterministic fallback):** if classical tiebreak still ties (extremely rare), use **lexicographic planet-id** (alphabetical: `jupiter < mars < mercury < moon < saturn < sun < venus`). WARN log on invocation.

#### 3.1.5 Output

```yaml
# Example output for a sample chart
positions:
  - name: atmakaraka
    planet: jupiter
    sign: 4            # Leo (0-indexed)
    degree: 29.45
    details:
      lon_in_sign: 29.45
      rank: 1
  - name: amatyakaraka
    planet: moon
    sign: 0
    degree: 27.12
    details: { lon_in_sign: 27.12, rank: 2 }
  - name: bhratrukaraka
    planet: venus
    ...
  # ... 7 or 8 entries
```

### 3.2 Arudha Padas — the reflection points

**Primary source:** Jaimini Upadesha Sutras, Book 1, Chapter 2, sutras 1.2.39–1.2.48. Commentary: Rangacharya §3.1–§3.30.

#### 3.2.1 Basic projection rule

Per Jaimini Sutras 1.2.39:
> "gṛha-svāmī-sthānād gaṇayet; tat padam iti"
> "Count from the lord's placement [back the same count from house to lord]; that is the [Arudha] Pada."

Procedure for Arudha of house H:
1. `lord_sign = sign occupied by the lord of H in the Rashi chart`.
2. `count = inclusive count from sign(H) forward to lord_sign` (both ends inclusive, per Jaimini convention).
3. `arudha_sign = lord_sign + (count − 1)` (walking forward `count` signs from `lord_sign`, equivalent to counting `count` inclusive from `lord_sign`).

Example:
- H = 1st house (Lagna sign = Aries).
- Aries's lord = Mars.
- Mars is in Leo. Count Aries → Leo inclusive = 5.
- Arudha Lagna = Leo + (5 − 1) = Sagittarius + 4 = **Sagittarius**. Wait — `Leo + 4 = Sagittarius` (Leo is the 5th sign; +4 = 9th = Sagittarius). Yes, AL = Sagittarius.

#### 3.2.2 The "1 or 7" exception

Per Jaimini Sutras 1.2.41–1.2.43:
> "sakāra-saptame tad-daśama-gṛhāc ca padam"
> "[If the count lands at] itself (1) or the 7th, [then project instead from the] 10th from the lord [as the pada]."

Rationale: if count=1, the lord is in H itself, and the naive projection returns H again — Arudha == house, no reflection information. If count=7, the lord is in the 7th from H, and naive projection returns the 7th from the 7th = H again. Both collapse; the exception redirects to the 10th from the lord.

Procedure:
- If `count ∈ {1, 7}`:
  - `arudha_sign = lord_sign + 9` (i.e., 10th from lord, 0-indexed shift)

Applies to **all 12 Arudhas** uniformly (not just AL).

#### 3.2.3 The 12 Arudhas — naming

| ID | Common name | Computed as |
|---|---|---|
| A1 | Arudha Lagna (AL) / Pada Lagna | Arudha of 1st |
| A2 | Dhana Pada | Arudha of 2nd |
| A3 | Bhratru Pada / Vikrama Pada | Arudha of 3rd |
| A4 | Matru Pada / Sukha Pada | Arudha of 4th |
| A5 | Putra Pada / Mantra Pada | Arudha of 5th |
| A6 | Shatru Pada / Roga Pada | Arudha of 6th |
| A7 | Dara Pada | Arudha of 7th |
| A8 | Ayu Pada / Randhra Pada | Arudha of 8th |
| A9 | Pitru Pada / Bhagya Pada | Arudha of 9th |
| A10 | Karma Pada | Arudha of 10th |
| A11 | Labha Pada | Arudha of 11th |
| A12 | Upapada Lagna (UL) | Arudha of 12th |

#### 3.2.4 Additional contextual Arudhas

- **Ghati Arudha** = Arudha of the 5th from Lagna (A5 alias). Associated with Ghatika Lagna philosophy.
- **Bhava Pada** = generic term for any Arudha of a bhava (same as A2–A11).
- **Karakamsa** = Atmakaraka's **Navamsha** sign (D9), used for yogas, not a classical Arudha but often grouped with Jaimini output.
- **Swamsha** = Atmakaraka's **Rashi** sign (D1); colloquial alias.

Josi emits A1–A12 under names `arudha_1` through `arudha_12` plus aliases; `karakamsa` and `swamsha` are emitted in the same `structured_positions` output with distinct names.

#### 3.2.5 Upapada (UL = A12) special significance

Per Jaimini Sutras 1.2.44:
> "dvādaśādeḥ padaṃ dārodveham; tad adhīśena darabhāvaḥ"
> "The pada of the 12th [= UL] is for marriage; [examine] the lord of [UL] for the spouse's condition."

Implemented as:
- UL sign = standard Arudha-of-12 computation.
- UL lord = ruling planet of UL sign.
- Spouse indicators: planets in UL, planets aspecting UL (via rashi drishti), UL lord's placement.

Used by multiple yoga rules shipped in this PRD.

### 3.3 Rashi Drishti — sign-based aspects

**Primary source:** Jaimini Upadesha Sutras, Book 1, Chapter 1, sutras 1.1.8–1.1.14. Rangacharya §1.10–§1.15.

#### 3.3.1 The rule

Per Jaimini Sutras 1.1.8:
> "carāḥ sthirān paśyanti"
> "Movable [signs] see fixed [signs]."

> "sthirāś carān"
> "Fixed [see] movable."

> "dvisvabhāvā dvisvabhāvān"
> "Dual [see] dual."

**Exception (Jaimini Sutras 1.1.10):** adjacent signs **do not** aspect (movable ↔ adjacent fixed is omitted).

Sign categories:

| Category | Signs |
|---|---|
| Movable (Chara) | Aries, Cancer, Libra, Capricorn |
| Fixed (Sthira) | Taurus, Leo, Scorpio, Aquarius |
| Dual (Dvisvabhava) | Gemini, Virgo, Sagittarius, Pisces |

#### 3.3.2 Aspect matrix (12 × 12)

Full rashi drishti matrix (X aspects Y):

| From | To |
|---|---|
| Aries (movable) | Leo, Scorpio, Aquarius (fixed except adjacent Taurus) |
| Taurus (fixed) | Cancer, Libra, Capricorn (movable except adjacent Aries & Gemini) — wait: adjacent-exclusion only applies to "the immediately next sign", not both sides. Rangacharya §1.12 clarifies: **exclude the sign immediately following in direct order**. So Taurus excludes only Aries if counting "previous adjacent"; and Gemini isn't fixed so irrelevant. Net: Taurus aspects Cancer, Libra, Capricorn. |
| Gemini (dual) | Virgo, Sagittarius, Pisces |
| Cancer (movable) | Scorpio, Aquarius, Taurus (excluding adjacent Leo) |
| Leo (fixed) | Libra, Capricorn, Aries (excluding adjacent Cancer/Virgo which are not fixed — irrelevant) |
| Virgo (dual) | Sagittarius, Pisces, Gemini |
| Libra (movable) | Aquarius, Taurus, Leo (excluding adjacent Scorpio) |
| Scorpio (fixed) | Capricorn, Aries, Cancer (excluding adjacent Libra) |
| Sagittarius (dual) | Pisces, Gemini, Virgo |
| Capricorn (movable) | Taurus, Leo, Scorpio (excluding adjacent Aquarius) |
| Aquarius (fixed) | Aries, Cancer, Libra (excluding adjacent Capricorn/Pisces — Pisces is dual, irrelevant) |
| Pisces (dual) | Gemini, Virgo, Sagittarius |

Pattern: each sign aspects **exactly 3** other signs (never 4, never 2). Symmetry: X aspects Y ⇔ Y aspects X (rashi drishti is bilateral).

**Computational form:** encode as a 12×12 boolean matrix `RASHI_DRISHTI[from_sign][to_sign]`. Stored as a constant in `jaimini_aspects.py`.

#### 3.3.3 Graha rashi drishti vs sign rashi drishti

Jaimini also defines **graha rashi drishti** (a planet aspects whatever signs its sign aspects). This is distinct from Parashari graha drishti (3/7/10th special aspects). Implementation:

```python
def graha_aspects_sign(planet: str, target_sign: int, chart) -> bool:
    planet_sign = chart.planet_sign(planet)
    return RASHI_DRISHTI[planet_sign][target_sign]
```

### 3.4 Jaimini Yogas — the shipped 15+

All yogas emit `boolean_with_strength` shape. Each has strength formula derived from constituent strength inputs (AK dignity, mutual kendra count, Arudha lord strength, etc.). Below each yoga lists:

- ID
- Classical name + citation
- Activation predicate
- Strength formula gist

(Full YAMLs authored in T-E3.5; gist here.)

#### 3.4.1 `jaimini.yoga.raja.ak_amk_kendra`

**Chara Karaka Raja Yoga (AK + AmK in mutual kendra)**. Citation: Jaimini Sutras 2.1.5; Rangacharya §5.1.

```yaml
activation:
  all_of:
    - predicate: chara_karaka_in_kendra_from
      of: atmakaraka
      target: amatyakaraka
    - predicate: chara_karaka_in_kendra_from
      of: amatyakaraka
      target: atmakaraka
strength_formula:
  type: weighted_average
  inputs:
    - { value: { call: planet_dignity_score, args: {planet: "{ak_planet}"} }, weight: 0.5 }
    - { value: { call: planet_dignity_score, args: {planet: "{amk_planet}"} }, weight: 0.5 }
```

Interpretive gist: AK and AmK in mutual kendra → ruler + counselor in productive alignment → power, recognition, smooth career.

#### 3.4.2 `jaimini.yoga.karakamsa.planets_in_karakamsa`

**Karakamsa Yoga — planets in Karakamsa indicate profession**. Citation: Jaimini Sutras 1.2.61–1.2.85.

Activation: at least one graha occupies the **Karakamsa sign** (AK's Navamsha sign). Per-planet-in-karakamsa interpretations (Jupiter→knowledge, Venus→arts, Mercury→commerce, etc.) covered narratively in E11b; the yoga merely marks activation.

Strength formula: count of planets in Karakamsa / 3 (normalized; clamped [0,1]).

#### 3.4.3 `jaimini.yoga.swamsha.planets_in_swamsha`

**Swamsha Yoga — planets in Swamsha (AK's Rashi sign)**. Citation: Rangacharya §5.20.

Similar to Karakamsa but operates on D1 instead of D9. Ships as separate rule; strength = count of planets in AK's rashi / 3.

#### 3.4.4 `jaimini.yoga.upapada.marriage`

**Upapada Marriage Yoga**. Citation: Jaimini Sutras 1.2.44–1.2.48.

Activation: UL lord is well-placed (not in 6th/8th/12th from UL) AND UL has no malefic in it AND UL is aspected (rashi drishti) by a benefic.

Strength formula: `(1 − malefic_influence_on_ul) × benefic_aspect_count / 3`.

#### 3.4.5 `jaimini.yoga.ghati_arudha.prosperity`

**Ghati Arudha (A5) Prosperity Yoga**. Citation: Rangacharya §3.25; Jataka Parijata 13.12.

Activation: benefic graha in or aspecting A5; A5 lord in kendra or trikona from Lagna.

Strength: `benefic_presence_score(A5) × lord_placement_score`.

#### 3.4.6 `jaimini.yoga.dara_karaka.kendra_from_al`

**Darakaraka in Kendra from Arudha Lagna — marriage prominence**. Citation: Jaimini Sutras 2.3.11.

Activation: DK planet is in 1st, 4th, 7th, or 10th from AL.

Strength: `dk_dignity × (1 if in AL-kendra else 0)` (binary kendra check).

#### 3.4.7 `jaimini.yoga.argala.primary_al`

**Argala (Obstruction) on AL — 2nd, 4th, 11th from AL**. Citation: Jaimini Sutras 1.2.15.

Activation: planets exist in 2nd, 4th, or 11th from AL → they exert Argala (influence) on AL. Primary argala vs Virodha (counter-obstruction from 12th, 10th, 3rd from AL) decides net result.

Strength: `(benefic_argala_count − malefic_argala_count) / total_argala_planets` (clamped).

#### 3.4.8 `jaimini.yoga.argala.virodha`

**Virodha Argala — counter-obstruction**. Citation: Jaimini Sutras 1.2.18.

Activation: planets in 12th, 10th, or 3rd from AL cancel the corresponding argala from 2nd, 4th, 11th.

Ships as companion rule with `jaimini.yoga.argala.primary_al`; both active → net argala computed by yoga consumer.

#### 3.4.9 `jaimini.yoga.ak_in_lagna`

**Atmakaraka in Lagna — soul-self alignment**. Citation: Rangacharya §5.5.

Activation: AK planet occupies Lagna sign.

Strength: `ak_dignity_score`.

#### 3.4.10 `jaimini.yoga.ak_in_kendra`

**Atmakaraka in Kendra (1,4,7,10)**. Citation: Rangacharya §5.7.

Activation: AK in 4th, 7th, or 10th (1st covered by the narrower §3.4.9 rule — shipped as separate rule to allow aggregation).

Strength: `ak_dignity × (1 if in kendra else 0)`.

#### 3.4.11 `jaimini.yoga.ak_in_trikona`

**Atmakaraka in Trikona (5, 9)**. Citation: Rangacharya §5.8.

Activation: AK in 5th or 9th.

#### 3.4.12 `jaimini.yoga.amk_ak_conjunct`

**Amatyakaraka conjoined with Atmakaraka**. Citation: Jaimini Sutras 2.1.8.

Activation: AK planet and AmK planet occupy the same sign (any orb).

Strength: `(30° − abs(ak_lon − amk_lon)) / 30°` (closer = stronger).

#### 3.4.13 `jaimini.yoga.brahma.jaimini`

**Brahma Yoga (Jaimini variant)**. Citation: Jaimini Sutras 2.2.15; Rangacharya §5.30.

Activation: all three — AL lord, UL lord, and 5th-from-AL lord — mutually aspect each other via rashi drishti OR occupy a single sign.

Strength: `mutual_aspect_count / 3`.

#### 3.4.14 `jaimini.yoga.maha_bhagya.jaimini`

**Maha Bhagya Yoga (Jaimini variant)**. Citation: Rangacharya §5.35 (distinct from Parashari Maha Bhagya shipped in E4a/E4b).

Activation: day birth + AL in odd sign + Moon in odd sign; OR night birth + AL in even sign + Moon in even sign. (Jaimini: uses AL instead of Lagna.)

Strength: binary 1.0 if active else 0.0.

#### 3.4.15 `jaimini.yoga.bandhana.al_8th_malefic`

**Bandhana Yoga — bondage indication**. Citation: Jaimini Sutras 2.3.7; Rangacharya §5.40.

Activation: malefic in 8th from AL OR 12th from AL + 2nd from AL has no benefic.

Strength: `malefic_count / 2`.

#### 3.4.16 `jaimini.yoga.niryana.eighth_from_al`

**Niryana-Sthana Yoga — timing indicator for major transitions (classical: death)**. Citation: Jaimini Sutras 2.3.20.

Activation: specific planetary placements in 8th from AL. Informational — E11b narrative generation treats this with appropriate disclaimers per master spec §7 (not a prediction of death; a classical timing *indicator* only).

Strength: `1.0` if pattern active.

#### 3.4.17 (optional) 5 more yogas

Shipped if calendar permits in T-E3.5:
- `jaimini.yoga.pushkara_pada` (Pushkara Pada benefic transit)
- `jaimini.yoga.pushkara_navamsha` (Pushkara Navamsha)
- `jaimini.yoga.dwidwadasha_yoga` (Dwi-Dwadasha AK-lord pattern)
- `jaimini.yoga.sankhya_yoga` (count-based Jaimini Sankhya)
- `jaimini.yoga.karaka_kartari` (karaka scissors pattern)

Target: ship 15 yogas minimum, 20 as stretch.

### 3.5 Predicate library additions (F6)

E3 registers the following Jaimini-specific predicates in a new file `src/josi/rules/predicates/jaimini_core.yaml` (consumed by F6 loader):

```yaml
predicates:
  - name: chara_karaka_in_kendra_from
    signature:
      of: { type: string, enum: [atmakaraka, amatyakaraka, bhratrukaraka, matrukaraka, putrakaraka, gnatikaraka, darakaraka] }
      target: { type: string, enum: [atmakaraka, amatyakaraka, bhratrukaraka, matrukaraka, putrakaraka, gnatikaraka, darakaraka] }
    returns: boolean
    impl: josi.services.classical.jaimini.predicates:chara_karaka_in_kendra_from

  - name: rashi_drishti_between
    signature:
      from_sign: { type: sign }
      to_sign: { type: sign }
    returns: boolean
    impl: josi.services.classical.jaimini.predicates:rashi_drishti_between

  - name: planet_in_arudha
    signature:
      planet: { type: planet }
      arudha: { type: string, enum: [al, a2, a3, a4, a5, a6, a7, a8, a9, a10, a11, ul] }
    returns: boolean
    impl: josi.services.classical.jaimini.predicates:planet_in_arudha

  - name: planet_in_karakamsa
    signature:
      planet: { type: planet }
    returns: boolean
    impl: josi.services.classical.jaimini.predicates:planet_in_karakamsa

  - name: planet_in_swamsha
    signature:
      planet: { type: planet }
    returns: boolean
    impl: josi.services.classical.jaimini.predicates:planet_in_swamsha

  - name: arudha_in_sign
    signature:
      arudha: { type: string }
      sign: { type: sign }
    returns: boolean
    impl: josi.services.classical.jaimini.predicates:arudha_in_sign

  - name: upapada_lord_well_placed
    signature: {}
    returns: boolean
    impl: josi.services.classical.jaimini.predicates:upapada_lord_well_placed

  - name: argala_from_al
    signature:
      house: { type: house, enum: [2, 4, 11, 12, 10, 3] }
      polarity: { type: string, enum: [primary, virodha] }
    returns: boolean
    impl: josi.services.classical.jaimini.predicates:argala_from_al

functions:
  - name: karaka_planet_id
    signature:
      karaka: { type: string }
    returns: string  # planet name
    impl: josi.services.classical.jaimini.functions:karaka_planet_id

  - name: arudha_sign_id
    signature:
      arudha: { type: string }
    returns: number  # 0-11
    impl: josi.services.classical.jaimini.functions:arudha_sign_id

  - name: rashi_drishti_count_to_sign
    signature:
      target_sign: { type: sign }
    returns: number
    impl: josi.services.classical.jaimini.functions:rashi_drishti_count_to_sign
```

### 3.6 Engine architecture

Three engines for the three non-yoga pillars; one engine for yogas (consumes the other three):

```
CharaKarakasEngine(ClassicalEngine)
  ├─ technique_family_id = "jaimini"
  ├─ output_shape_id = "structured_positions"
  ├─ rule_id = "jaimini.karakas.seven.jaimini_sutras"
  └─ compute_for_source() → ranks 7 grahas, emits 7-position payload

ArudhasEngine(ClassicalEngine)
  ├─ technique_family_id = "jaimini"
  ├─ output_shape_id = "structured_positions"
  ├─ rule_id = "jaimini.arudhas.twelve.jaimini_sutras"
  └─ compute_for_source() → computes A1..A12 + Karakamsa + Swamsha

RashiDrishtiEngine(ClassicalEngine)
  ├─ technique_family_id = "jaimini"
  ├─ output_shape_id = "structured_positions"  (aspecting-signs list per sign)
  ├─ rule_id = "jaimini.rashi_drishti.base.jaimini_sutras"
  └─ compute_for_source() → 12 signs × {aspects: [signs], aspected_by: [signs]}

JaiminiYogaEngine(ClassicalEngine)
  ├─ technique_family_id = "yoga"  (NOT "jaimini" — yogas are their own family)
  ├─ output_shape_id = "boolean_with_strength"
  ├─ consumes: karakas + arudhas + rashi_drishti computes
  └─ evaluates 15+ yoga rules via F6 DSL
```

JaiminiYogaEngine has its own `technique_family_id = "yoga"` (unifies with E4a/E4b yoga queries). Rule IDs namespace Jaimini yogas under `jaimini.yoga.*` while Parashari yogas are `yoga.raja.*` etc.

Dependency: JaiminiYogaEngine depends on CharaKarakasEngine and ArudhasEngine results being present in `technique_compute`. Orchestrator ensures compute order: karakas → arudhas → rashi_drishti → yogas.

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| 7 or 8 karakas default | **7 (no Rahu)** — matches JH 7.x default | Differential testing precedence; 8-karaka as alternate rule |
| Tiebreak at identical longitudes | **Lexicographic planet-id + WARN** (after classical tiebreak fails) | Determinism; rare case |
| Karakamsa = D9 Navamsha vs Swamsha = D1 | **Both shipped as distinct outputs** in `structured_positions` | Naming consistency matters in astrologer UI |
| Arudha exception handling for count=1 or 7 | **Project to 10th from lord** | Jaimini Sutras 1.2.41–43 explicit |
| Arudhas beyond A1–A12 (e.g., Bhava Pada duplicates) | **Only 12 Arudhas + Karakamsa + Swamsha** — Bhava Pada is alias | Clean namespace |
| Rashi Drishti bidirectionality | **Confirmed bilateral** (X→Y ⇔ Y→X) | Classical invariant |
| Rashi Drishti adjacent-exclusion precise form | **Exclude sign immediately next in direct order, per Rangacharya §1.12** | Disambiguates |
| Graha rashi drishti vs graha drishti (Parashari) | **Both shipped as distinct predicates** | Used by different yoga families |
| Yoga count: 15, 20, or 25 | **15 hard minimum, 20 stretch** | P4 reference-set expands to 50+ |
| JaiminiYogaEngine's technique_family_id | **`"yoga"`** (unifies with Parashari) | User query "show my yogas" returns both traditions |
| Bandhana/Niryana yogas with legal/outcome disclaimers | **Ship with explicit `disclaimer` field in YAML notes** | Master spec §7 compliance |
| 4-karaka variant (AK, AmK, BK, MK only, per some schools) | **Not shipped** | Not an accepted modern variant |
| AK computation for Mercury retrograde | **Use actual sidereal longitude** (Mercury treated like other grahas) | Classical interpretation |

## 5. Component Design

### 5.1 New modules

```
src/josi/services/classical/jaimini/
├── __init__.py
├── chara_karakas_engine.py
├── arudhas_engine.py
├── rashi_drishti_engine.py
├── jaimini_yoga_engine.py
├── predicates.py                # F6 predicate implementations
├── functions.py                 # F6 function implementations
└── constants.py                 # RASHI_DRISHTI[12][12] matrix, sign categories

src/josi/rules/predicates/
└── jaimini_core.yaml            # Jaimini predicate library (F6)

src/josi/rules/jaimini/
├── karakas/
│   ├── seven.jaimini_sutras.yaml
│   └── eight_with_rahu.jaimini_sutras.yaml   # alternate
├── arudhas/
│   └── twelve.jaimini_sutras.yaml
├── rashi_drishti/
│   └── base.jaimini_sutras.yaml
└── yogas/
    ├── raja_ak_amk_kendra.jaimini_sutras.yaml
    ├── karakamsa_planets.jaimini_sutras.yaml
    ├── swamsha_planets.jaimini_sutras.yaml
    ├── upapada_marriage.jaimini_sutras.yaml
    ├── ghati_arudha_prosperity.rangacharya.yaml
    ├── dara_karaka_kendra_al.jaimini_sutras.yaml
    ├── argala_primary_al.jaimini_sutras.yaml
    ├── argala_virodha.jaimini_sutras.yaml
    ├── ak_in_lagna.rangacharya.yaml
    ├── ak_in_kendra.rangacharya.yaml
    ├── ak_in_trikona.rangacharya.yaml
    ├── amk_ak_conjunct.jaimini_sutras.yaml
    ├── brahma.jaimini_sutras.yaml
    ├── maha_bhagya.rangacharya.yaml
    ├── bandhana_al_8th.jaimini_sutras.yaml
    └── niryana_eighth_al.jaimini_sutras.yaml

tests/golden/charts/jaimini/
├── chart_01/{karakas,arudhas,rashi_drishti,yogas}.yaml
├── ... (8 charts)

tests/classical/jaimini/
├── test_chara_karakas.py
├── test_arudhas.py
├── test_rashi_drishti.py
├── test_jaimini_yogas.py
├── test_jaimini_predicates.py
└── test_e3_properties.py
```

### 5.2 Data model additions

No new tables. 19 new rows in `classical_rule`:
- 2 karakas rules (7 default, 8 alternate)
- 1 arudhas rule
- 1 rashi drishti rule
- 15+ yoga rules

All flow into `technique_compute` with existing `technique_family_id ∈ {jaimini, yoga}`.

### 5.3 API contract

```
GET /api/v1/jaimini/{chart_id}/karakas?variant=seven
  Response.data:
    positions: [
      { name: "atmakaraka", planet: "jupiter", sign: 4, degree: 29.45, details: {...} },
      ...7 or 8 entries
    ]

GET /api/v1/jaimini/{chart_id}/arudhas
  Response.data:
    positions: [
      { name: "arudha_1", sign: 8, degree: null, lord: "saturn", details: {count_used: 5, exception_applied: false} },
      { name: "arudha_lagna", sign: 8, ... },   # alias of arudha_1
      ...
      { name: "karakamsa", sign: 3, details: { source: "D9" } },
      { name: "swamsha", sign: 4, details: { source: "D1" } }
    ]

GET /api/v1/jaimini/{chart_id}/rashi-drishti?from_sign=0
  Response.data:
    from_sign: 0,
    aspects: [4, 7, 10],    # Leo, Scorpio, Aquarius (0-indexed Aries)
    aspected_by: [4, 7, 10]  # bilateral

GET /api/v1/jaimini/{chart_id}/yogas
  Response.data:
    active_yogas: [
      {
        rule_id: "jaimini.yoga.raja.ak_amk_kendra",
        name: "Chara Karaka Raja Yoga",
        active: true,
        strength: 0.82,
        details: {...},
        citation: "Jaimini Sutras 2.1.5"
      },
      ...
    ]

GET /api/v1/jaimini/{chart_id}
  Response.data: { karakas: {...}, arudhas: {...}, rashi_drishti_summary: {...}, yogas: [...] }
```

### 5.4 AI tool-use extension

```python
@tool
def get_chara_karakas(chart_id: str, variant: Literal["seven", "eight"] = "seven") -> list[Karaka]:
    """Returns the 7 or 8 Chara Karakas ranked by sidereal longitude within sign.
       Each karaka has name ('atmakaraka', ...), assigned planet, sign, and degree.
       Citation: Jaimini Sutras 1.2.1-9."""

@tool
def get_arudhas(chart_id: str) -> list[Arudha]:
    """Returns the 12 Arudha Padas + Karakamsa + Swamsha.
       Citation: Jaimini Sutras 1.2.39-48."""

@tool
def get_jaimini_yogas(chart_id: str, min_confidence: float = 0.0) -> list[Yoga]:
    """Returns active Jaimini yogas with strength, details, and citations.
       Classical sources: Jaimini Upadesha Sutras, Rangacharya commentary, Saravali."""

@tool
def get_rashi_drishti(chart_id: str, from_sign: int) -> RashiDrishtiInfo:
    """Returns signs aspected by and aspecting from_sign via Jaimini rashi drishti.
       Citation: Jaimini Sutras 1.1.8-12."""
```

## 6. User Stories

### US-E3.1: As a Jaimini practitioner, I want to see my 7 Chara Karakas ordered by longitude-in-sign
**Acceptance:** `/api/v1/jaimini/{chart_id}/karakas` returns 7 positions with `rank: 1..7`, ordered by `lon_in_sign` descending, AK at rank 1, DK at rank 7.

### US-E3.2: As an astrologer, I want to see my client's Arudha Lagna and Upapada prominently
**Acceptance:** `/api/v1/jaimini/{chart_id}/arudhas` returns 12 Arudhas; `details.exception_applied` flag is correctly set for Arudhas where count ∈ {1, 7} triggered the 10th-from-lord projection.

### US-E3.3: As an engineer, I want to verify Arudhas against manual Rangacharya examples
**Acceptance:** 8 golden charts each have their 12 Arudhas manually computed per Rangacharya examples; test asserts computed values match.

### US-E3.4: As an AI agent, I want `get_jaimini_yogas` to return active yogas with citations
**Acceptance:** Tool returns list of `{rule_id, name, active, strength, citation}`; every active yoga has a classical citation.

### US-E3.5: As a classical advisor, I want to add a new Jaimini yoga via YAML PR
**Acceptance:** Create `src/josi/rules/jaimini/yogas/new_yoga.yaml`; merge PR; next deploy loads it; next compute invocation for any chart evaluates the new yoga; no engine code change.

### US-E3.6: As an engineer, I want Jaimini yoga queries to unify with Parashari yoga queries
**Acceptance:** `GET /api/v1/yogas/{chart_id}` (E4a endpoint) returns both Parashari and Jaimini yogas because both share `technique_family_id = 'yoga'`.

### US-E3.7: As a tiebreak victim, I want deterministic karaka assignment even with near-identical longitudes
**Acceptance:** Two runs on same chart always produce same karaka assignment; WARN log on lexicographic fallback invocation.

### US-E3.8: As an astrologer, I want to select the 8-karaka variant for a Jaimini-Rahu school client
**Acceptance:** Set `astrologer_source_preference.source_weights = {...}` to prefer alternate rule; aggregation (F8) picks 8-karaka variant; UI surfaces "8-karaka view".

### US-E3.9: As a product owner, I want Bandhana and Niryana yogas to carry appropriate disclaimers
**Acceptance:** Classical YAML for `jaimini.yoga.bandhana.al_8th_malefic` and `jaimini.yoga.niryana.eighth_from_al` include `notes` field with disclaimer text; E11b surfaces them with classical framing.

### US-E3.10: As an AI agent, I want rashi drishti predicates available for narrative composition
**Acceptance:** `get_rashi_drishti(chart_id, from_sign=7)` returns the 3 signs aspected by Libra; AI uses them in yoga explanations.

## 7. Tasks

### T-E3.1: Author Jaimini predicate library YAML
- **Definition:** `src/josi/rules/predicates/jaimini_core.yaml` with 8+ predicates and 3+ functions per §3.5. Implement Python stubs in `predicates.py` and `functions.py`.
- **Acceptance:** F6 `PredicateRegistry` loads library; signature-check passes; `poetry run validate-rules` exits 0.
- **Effort:** 2 days
- **Depends on:** F6

### T-E3.2: Implement constants — rashi drishti matrix + sign categories
- **Definition:** `src/josi/services/classical/jaimini/constants.py` with `SIGN_CATEGORY = {Aries: "movable", ...}` and `RASHI_DRISHTI: list[list[bool]]` 12×12 matrix per §3.3.2.
- **Acceptance:** Matrix is symmetric (X→Y ⇔ Y→X); each sign aspects exactly 3 others; unit tests validate.
- **Effort:** 1 day
- **Depends on:** none

### T-E3.3: Implement `CharaKarakasEngine`
- **Definition:** Implements `ClassicalEngine` Protocol per §3.1. Ranks 7 grahas by `lon_in_sign` desc, assigns names. Alternate 8-karaka variant with Rahu using `30° − lon_in_sign`. Tiebreak per §3.1.4. Emits `structured_positions`.
- **Acceptance:** Unit tests pass for 10+ charts with hand-computed karakas; tiebreak WARN logged when invoked; 8-karaka variant produces different output when active.
- **Effort:** 2 days
- **Depends on:** T-E3.1, T-E3.2

### T-E3.4: Implement `ArudhasEngine`
- **Definition:** Implements `ClassicalEngine` per §3.2. Computes A1–A12 per projection rule with 1-or-7 exception. Also emits Karakamsa (AK's D9 sign) and Swamsha (AK's D1 sign). `details.exception_applied: bool` per position.
- **Acceptance:** Unit tests pass for 20 hand-computed Arudha cases (both normal and exception branches); golden tests pass.
- **Effort:** 2 days
- **Depends on:** T-E3.1, T-E3.3 (consumes AK for Karakamsa/Swamsha)

### T-E3.5: Implement `RashiDrishtiEngine`
- **Definition:** Implements `ClassicalEngine` per §3.3. Trivial — precomputed matrix lookup. Emits 12-entry `structured_positions` where each entry = `{name: "rashi_N", aspects: [...], aspected_by: [...]}`.
- **Acceptance:** Unit tests assert matrix symmetry; API test passes.
- **Effort:** 0.5 day
- **Depends on:** T-E3.2

### T-E3.6: Author 15+ yoga rule YAMLs
- **Definition:** Author YAMLs per §3.4 (15 required + 5 stretch). Each YAML: full activation predicate composition + strength formula + classical citation + disclaimer where appropriate.
- **Acceptance:** F6 loader parses all; `poetry run validate-rules` passes; classical-advisor review recorded in PR.
- **Effort:** 4 days (heaviest YAML authoring task in E3)
- **Depends on:** T-E3.1

### T-E3.7: Implement `JaiminiYogaEngine`
- **Definition:** Engine that loads Jaimini yoga rules (filter: `source_id ∈ {jaimini_sutras, saravali, jataka_parijata}` OR `rule_id LIKE 'jaimini.yoga.%'`). Evaluates each rule against chart state using F6 DSL interpreter. Emits `boolean_with_strength` per yoga.
- **Acceptance:** Unit tests: 5 hand-crafted charts trigger expected yoga activations; strength formulas produce expected outputs.
- **Effort:** 3 days
- **Depends on:** T-E3.3, T-E3.4, T-E3.5, T-E3.6, F8

### T-E3.8: REST + GraphQL endpoints
- **Definition:** Implement `/api/v1/jaimini/{chart_id}/{karakas,arudhas,rashi-drishti,yogas}` and aggregated `/api/v1/jaimini/{chart_id}`. Existing `/api/v1/yogas/{chart_id}` unified to include Jaimini yogas.
- **Acceptance:** Curl tests pass for all endpoints; OpenAPI doc generated; response shapes conform to schemas.
- **Effort:** 1.5 days
- **Depends on:** T-E3.3, T-E3.4, T-E3.5, T-E3.7

### T-E3.9: AI tool-use extension
- **Definition:** Implement `get_chara_karakas`, `get_arudhas`, `get_jaimini_yogas`, `get_rashi_drishti` tools. Update prompt docs.
- **Acceptance:** Tool schemas validate; integration tests with mock LLM invocations return correct payloads.
- **Effort:** 1 day
- **Depends on:** T-E3.8

### T-E3.10: Author 8 golden chart fixtures × 4 pillars = 32 fixture files
- **Definition:** 8 charts. Per chart, fixtures for karakas, arudhas, rashi_drishti (trivial — matrix is chart-independent, one fixture file shared), and yogas. Karakas + arudhas manually computed using Rangacharya examples + JH 7.x cross-check; yogas by inspection.
- **Acceptance:** Fixtures parse; recorded `verified_by` field; classical-advisor sign-off.
- **Effort:** 4 days
- **Depends on:** F16

### T-E3.11: Golden + property tests
- **Definition:**
  - Golden tests: karakas match JH for 8 charts; arudhas match Rangacharya examples; yogas' active set matches expected.
  - Property tests (F17, ≥1000 examples per pillar):
    - Karakas: ranking produces 7 distinct names; lon_in_sign descending monotonic; invariance under alternate planet ordering at same longitudes.
    - Arudhas: each Arudha's sign is deterministic from chart state; exception flag correctly set when count ∈ {1, 7}.
    - Rashi Drishti: matrix is bilaterally symmetric; each sign aspects exactly 3; movable/fixed/dual partition respected.
    - Yogas: strength ∈ [0, 1]; active yogas have non-null citation; `output_hash` stable across reruns.
- **Acceptance:** All tests green in CI; ≥1000 Hypothesis examples per pillar with 0 failures.
- **Effort:** 2 days
- **Depends on:** T-E3.7, T-E3.10, F17

### T-E3.12: Unified yoga endpoint integration (E4a consolidation)
- **Definition:** `/api/v1/yogas/{chart_id}` (E4a) must surface both Parashari and Jaimini yogas. If E4a hasn't shipped at E3 start, stub the endpoint for Jaimini-only; merge with Parashari when E4a lands.
- **Acceptance:** Query returns combined list with `tradition: "parashari" | "jaimini"` field; sort/filter by tradition works.
- **Effort:** 1 day
- **Depends on:** T-E3.8 (and optionally E4a endpoint if available)

### T-E3.13: Integration test + documentation
- **Definition:** End-to-end test: YAML → F6 loader → F8 engine compute → aggregation → chart_reading_view.jaimini_summary → REST → AI tool. CLAUDE.md updated with Jaimini engine overview.
- **Acceptance:** Round-trip passes CI; docs merged.
- **Effort:** 1 day
- **Depends on:** T-E3.11

## 8. Unit Tests

### 8.1 Constants — rashi drishti matrix

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_rashi_drishti_symmetric` | for each (i, j) | matrix[i][j] == matrix[j][i] | Classical bilateral |
| `test_each_sign_aspects_exactly_3` | per sign | sum of row = 3 | Classical count |
| `test_movable_aspects_fixed_except_adjacent` | Aries (movable) | aspects = {Leo, Scorpio, Aquarius} | Jaimini 1.1.8 |
| `test_fixed_aspects_movable_except_adjacent` | Taurus (fixed) | aspects = {Cancer, Libra, Capricorn} | Jaimini 1.1.8 |
| `test_dual_aspects_dual` | Gemini (dual) | aspects = {Virgo, Sagittarius, Pisces} | Jaimini 1.1.8 |
| `test_sign_does_not_aspect_self` | any sign | matrix[i][i] == False | Invariant |
| `test_adjacent_exclusion_aries_taurus` | Aries | does NOT aspect Taurus | Adjacent exclusion |

### 8.2 Chara Karakas — ranking

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_karaka_rank_highest_lon_is_ak` | 7 grahas with distinct lons | highest-lon = AK | Jaimini 1.2.3 |
| `test_karaka_assignment_canonical` | chart: {sun: 15°, moon: 27°, mars: 5°, merc: 12°, jup: 29.5°, ven: 22°, sat: 3°} | AK=jupiter, AmK=moon, BK=venus, MK=sun, PK=mercury, GK=mars, DK=saturn | Known chart |
| `test_karaka_lon_in_sign_computation` | planet at absolute 125° (Leo 5°) | lon_in_sign = 5.0 | Modular math |
| `test_karaka_tiebreak_classical` | 2 planets at 27.000° and 27.000° — closer-to-Lagna wins | classical rule applied | Rangacharya §2.12 |
| `test_karaka_tiebreak_lexicographic_fallback` | 2 planets at 27.000° and 27.000° with equal Lagna distance | lexicographic by name; WARN logged | Determinism |
| `test_karaka_8_variant_includes_rahu` | chart with Rahu at lon_in_sign 28° | 8-karaka output lists Rahu; Rahu's effective rank-value = 30−28 = 2 | Alternate rule |
| `test_karaka_7_variant_excludes_rahu` | default | 7 output positions; Rahu not named | Default rule |
| `test_karaka_output_shape_structured_positions` | any chart | emits `structured_positions` per F7 | Shape conformance |

### 8.3 Arudhas — projection + exception

| Test name | Input (H, lord_sign) | Expected arudha_sign | Rationale |
|---|---|---|---|
| `test_arudha_normal_projection` | H=1 (Aries), lord=Mars in Leo | sign = Sagittarius (count=5, +4 from Leo = Sag) | Jaimini 1.2.39 |
| `test_arudha_count_1_exception_10th_from_lord` | H=1, lord in Aries itself (count=1) | sign = 10th from Aries = Capricorn | Exception |
| `test_arudha_count_7_exception_10th_from_lord` | H=1, lord in Libra (count=7 from Aries) | sign = 10th from Libra = Cancer | Exception |
| `test_arudha_count_2_normal` | H=2 (Taurus), lord=Venus in Gemini (count=2) | sign = 10th from Gemini...wait no, count=2 is normal → from Gemini count 2 = Cancer | Normal projection |
| `test_arudha_bilateral_consistency` | various | projection formula applied consistently | Invariant |
| `test_arudha_lagna_is_a1` | any chart | arudha_lagna == arudha_1 alias | Naming |
| `test_upapada_is_a12` | any chart | upapada == arudha_12 alias | Naming |
| `test_arudha_exception_flag_set` | chart with count=1 for A5 | positions[4].details.exception_applied = true | Disclosure |
| `test_karakamsa_is_ak_navamsha` | chart with AK=jupiter in D9 Leo | karakamsa position sign = Leo | Definition |
| `test_swamsha_is_ak_rashi` | chart with AK=jupiter in D1 Cancer | swamsha position sign = Cancer | Definition |
| `test_arudhas_all_12_present` | any chart | positions contains names arudha_1..arudha_12 | Completeness |

### 8.4 Jaimini predicates

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_chara_karaka_in_kendra_from` | AK in sign 4, AmK in sign 7 (7−4=3, kendra? No, kendra = 1,4,7,10 counted; +1 = 4th from AK) | True | kendra means 1/4/7/10 count inclusive |
| `test_rashi_drishti_between_true` | from=0 (Aries), to=4 (Leo) | True | Matrix lookup |
| `test_rashi_drishti_between_false_adjacent` | from=0 (Aries), to=1 (Taurus) | False | Adjacent exclusion |
| `test_planet_in_arudha` | jupiter in sign=AL sign | True | Position check |
| `test_planet_in_karakamsa` | jupiter in AK's D9 sign | True | Definition |
| `test_argala_from_al_primary` | planets in 2nd/4th/11th from AL | True for each | Primary argala |
| `test_argala_virodha` | planets in 12th/10th/3rd from AL | True for virodha | Virodha rule |
| `test_upapada_lord_well_placed` | UL lord in 1/4/5/7/9/10 from UL | True | Well-placed definition |

### 8.5 Jaimini yogas — activation

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_raja_ak_amk_kendra_active` | chart with AK in sign X, AmK in sign X+3 (kendra) | active=True | Yoga definition |
| `test_raja_ak_amk_kendra_inactive` | AK+AmK in non-kendra positions | active=False | Yoga definition |
| `test_karakamsa_yoga_with_3_planets` | 3 planets in Karakamsa | active=True, strength=1.0 | count/3 normalized |
| `test_swamsha_yoga_with_1_planet` | 1 planet in Swamsha | active=True, strength≈0.33 | count/3 |
| `test_upapada_marriage_active` | UL lord well-placed, no malefic in UL, benefic aspects | active=True, strength > 0.5 | Full pattern |
| `test_ghati_arudha_prosperity_active` | benefic in A5, A5 lord in kendra from Lagna | active=True | Yoga rule |
| `test_dara_karaka_kendra_from_al_active` | DK in 7th from AL | active=True | Kendra check |
| `test_argala_primary_al_active` | benefic in 2nd from AL | active=True with benefic strength | Primary argala |
| `test_argala_virodha_active` | malefic in 12th from AL | active=True (virodha form) | Virodha rule |
| `test_ak_in_lagna_active` | AK planet in Lagna sign | active=True, strength=ak_dignity | Definition |
| `test_amk_ak_conjunct_same_sign_active` | AK+AmK same sign, lon diff 5° | active=True, strength=(30−5)/30 | Conjunction |
| `test_brahma_jaimini_active` | AL_lord, UL_lord, 5th_AL_lord mutually aspect via rashi drishti | active=True | Brahma definition |
| `test_maha_bhagya_jaimini_day_odd_active` | day birth + AL odd + Moon odd | active=True, strength=1.0 | Definition |
| `test_maha_bhagya_jaimini_night_even_active` | night birth + AL even + Moon even | active=True | Night variant |
| `test_bandhana_al_8th_malefic_active` | malefic in 8th from AL | active=True | Bondage indicator |
| `test_niryana_eighth_from_al_pattern` | specific 8th-from-AL pattern | active=True | Timing indicator |

### 8.6 Jaimini yogas — strength formulas

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_raja_strength_weighted_average` | AK dignity=0.8, AmK dignity=0.6 | strength = 0.7 (avg) | Formula |
| `test_karakamsa_strength_count_div_3` | 2 planets in karakamsa | strength = 0.667 | Formula |
| `test_karakamsa_strength_clamped_at_1` | 5 planets in karakamsa | strength = 1.0 (clamped) | Clamp |
| `test_amk_ak_conjunct_strength_by_orb` | orb=1° | strength = 29/30 ≈ 0.967 | Formula |

### 8.7 Rule registry integration

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_e3_rules_loaded_from_yaml` | F6 loader | 19+ new rows in `classical_rule` | Wiring |
| `test_e3_content_hash_stable` | 3 reloads | identical hashes | Determinism |
| `test_e3_jaimini_predicate_library_loaded` | F6 predicate registry | 8+ Jaimini predicates available | F6 integration |
| `test_e3_unified_yoga_endpoint_returns_both_traditions` | `GET /api/v1/yogas/{chart_id}` | list contains `tradition: "parashari"` AND `tradition: "jaimini"` entries | Unification |

### 8.8 Golden suite (Rangacharya + JH)

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_golden_chart_01_karakas_match_rangacharya` | fixture | 7 karakas match Rangacharya Ch.2 example | Classical fidelity |
| `test_golden_chart_01_arudhas_match_rangacharya` | fixture | 12 Arudhas match Rangacharya Ch.3 | Classical fidelity |
| `test_golden_chart_01_yogas_match_expected` | fixture | active_yogas set matches expected | Hand-verified |
| `test_golden_chart_02_to_08_karakas` | 7 charts | all karakas match JH 7.x | Differential testing |
| `test_golden_chart_02_to_08_arudhas` | 7 charts | all arudhas match JH (±sign boundary tolerance) | Differential testing |
| `test_golden_chart_02_to_08_yogas_overlap_90pct` | 7 charts | >90% overlap of active_yogas with JH Jaimini yoga list | Differential testing |

### 8.9 Property tests (Hypothesis, F17, ≥1000 examples)

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_karaka_ranking_produces_7_distinct_names` | random chart | |set(names)| = 7 | Invariant |
| `test_karaka_longitudes_monotonic_descending` | random | lon_in_sign[rank_i] ≥ lon_in_sign[rank_i+1] | Ranking invariant |
| `test_arudha_always_in_0_to_11` | random | all arudha signs ∈ 0..11 | Domain |
| `test_arudha_exception_flag_iff_count_1_or_7` | random | flag set iff count ∈ {1,7} | Rule consistency |
| `test_rashi_drishti_matrix_symmetric_property` | (1000 random sign pairs) | matrix[i][j] == matrix[j][i] | Classical invariant |
| `test_yoga_strength_in_0_1` | random charts × all yogas | strength ∈ [0, 1] | Shape invariant |
| `test_yoga_active_yogas_have_citation` | random | every active yoga has non-null citation | F11 requirement |
| `test_recompute_deterministic` | same chart 2 runs | same output_hash | F13 contract |

## 9. EPIC-Level Acceptance Criteria

- [ ] 19+ Jaimini rule YAMLs (karakas × 2, arudhas × 1, rashi drishti × 1, yogas × 15+) loaded into `classical_rule` via F6 loader
- [ ] Jaimini predicate library registered in F6 PredicateRegistry with 8+ predicates and 3+ functions
- [ ] `CharaKarakasEngine`, `ArudhasEngine`, `RashiDrishtiEngine`, `JaiminiYogaEngine` implement `ClassicalEngine` Protocol
- [ ] REST endpoints live: `/api/v1/jaimini/{chart_id}/{karakas,arudhas,rashi-drishti,yogas}` and aggregated
- [ ] `/api/v1/yogas/{chart_id}` unifies Parashari + Jaimini yogas with `tradition` field
- [ ] AI tool-use extensions (`get_chara_karakas`, `get_arudhas`, `get_jaimini_yogas`, `get_rashi_drishti`) live and integration-tested
- [ ] 8 golden charts × 4 pillars = 32 fixtures all pass; karakas + arudhas cross-verified against Rangacharya examples and JH 7.x
- [ ] Property tests pass with ≥1000 Hypothesis examples per pillar
- [ ] Unit test coverage ≥ 90% for all new code
- [ ] `chart_reading_view.jaimini_summary` JSONB populated with karakas, arudhas, active_jaimini_yogas
- [ ] Documentation: CLAUDE.md + user docs updated; classical-advisor sign-off recorded
- [ ] Performance: full Jaimini compute bundle (karakas + arudhas + yogas) per chart P99 < 150 ms
- [ ] Content integrity: every active yoga surface carries citation per F11 contract

## 10. Rollout Plan

- **Feature flags:** `ENABLE_JAIMINI_KARAKAS`, `ENABLE_JAIMINI_ARUDHAS`, `ENABLE_JAIMINI_YOGAS` (rashi drishti always on — trivial compute). Defaults `false` on first P2 deploy.
- **Shadow compute:** 7 days. Compute rows written for all existing charts in staging. Spot-check 20 charts vs JH 7.x before production flip.
- **Astrologer preview:** 2-week early-access tier; astrologers can enable via pro-mode toggle. Feedback feeds override-rate signals (F2 `aggregation_signal`) for E14a.
- **Backfill:** opportunistic on chart view. Background `compute_missing_jaimini` job seeds 10M+ charts over 6 weeks (karakas are cheap; yogas are the long pole).
- **Rollback:** flip flags off → Jaimini endpoints return 404; Parashari-only endpoints unaffected. `effective_to = now()` on new rules soft-deprecates; compute rows retained.
- **Classical advisor review gate:** production rollout requires external classical advisor (non-employee, Jaimini-school practitioner) sign-off on golden chart karakas + arudhas + yogas for at least 3 of the 8 fixtures. Tracked as a separate GitHub issue; blocks flag flip.

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Arudha projection formula encoded incorrectly (off-by-one in inclusive count) | Medium | High | Dedicated unit tests for count=1,2,3,7,8,12 cases; property test asserts `arudha_sign = (lord_sign + count − 1) mod 12` for non-exception; exception branch explicitly tested |
| Rashi drishti matrix adjacency rule ambiguity across commentaries | Medium | Medium | Rangacharya §1.12 authoritative interpretation cited; test_rashi_drishti_symmetric property catches asymmetric encoding bugs; classical-advisor review |
| Chara Karaka 7 vs 8 variant selection ambiguity in UI | Low | Medium | Default 7 matches JH; 8-karaka alternate behind astrologer preference; API response includes variant field |
| Bandhana / Niryana yoga disclaimers misinterpreted by users | Medium | High (reputational) | `notes` field in YAML carries disclaimer text; E11b narrative generator wraps these yogas with classical framing; UI shows "classical indicator — not a prediction" label |
| Jaimini yoga strength formulas underspecified in classical sources | High | Medium | Josi formulates pragmatic strength formulas, flagged in YAML notes as Josi interpretation of classical constraints; avoid claiming classical authority for strength numbers |
| Karakamsa (D9) depends on D9 chart being computed — integration gap | Low | High | T-E3.4 asserts D9 chart available; fallback error clearly identifies missing D9 input |
| Unified yoga endpoint (E3 + E4a) collision on same rule_id namespace | Low | Medium | `jaimini.yoga.*` vs `yoga.*` prefix enforced in F6 rule_id regex; CI check prevents collision |
| 8-karaka variant (with Rahu) produces divergent output from JH under edge lon values | Medium | Low | 8-variant shipped as non-default; flagged for advisor review; not critical for v1 |
| Tiebreak rule (classical → lexicographic) surfaces WARN in production for >1% of charts | Low | Low | Alerting at >0.5% rate; if exceeded, investigate Rahu/node longitude precision |
| Argala yoga activation overlaps with Virodha argala producing contradictory user messages | Medium | Medium | Both yogas ship; E11b narrative logic resolves contradiction by net argala count; not E3's concern beyond flagging both |
| Jaimini Sutras textual edition differences (Sagar vs Motilal Banarsidass) | Low | Low | Author citations reference Sagar/Rangacharya edition; alternate editions documented |

## 12. References

- Master spec: [`docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`](../../../superpowers/specs/2026-04-19-classical-techniques-expansion-design.md) §2.2, §2.3
- F1 dimensions: [`../P0/F1-star-schema-dimensions.md`](../P0/F1-star-schema-dimensions.md)
- F2 fact tables: [`../P0/F2-fact-tables.md`](../P0/F2-fact-tables.md)
- F6 rule DSL + predicate library: [`../P0/F6-rule-dsl-yaml-loader.md`](../P0/F6-rule-dsl-yaml-loader.md)
- F7 output shapes (`structured_positions`, `boolean_with_strength`): [`../P0/F7-output-shape-system.md`](../P0/F7-output-shape-system.md)
- F8 engine + strategy Protocol: [`../P0/F8-technique-result-aggregation-protocol.md`](../P0/F8-technique-result-aggregation-protocol.md)
- F13 content-hash provenance: [`../P0/F13-content-hash-provenance.md`](../P0/F13-content-hash-provenance.md)
- F16 golden chart suite: [`../P0/F16-golden-chart-suite.md`](../P0/F16-golden-chart-suite.md)
- F17 property-based test harness: [`../P0/F17-property-based-test-harness.md`](../P0/F17-property-based-test-harness.md)
- E1b Chara/Narayana dasa (consumed for dasa-phalita yogas): [`./E1b-multi-dasa-v2.md`](./E1b-multi-dasa-v2.md)
- E4a/E4b yoga engines (unified yoga endpoint): [`../P1/E4a-yoga-engine-mvp.md`](../P1/E4a-yoga-engine-mvp.md), [`./E4b-yoga-engine-full-250.md`](./E4b-yoga-engine-full-250.md)
- Classical primary sources:
  - **Jaimini Upadesha Sutras**, Book 1 Chapters 1–4 (rashi drishti, chara karakas, arudhas, dasa)
  - **Jaimini Upadesha Sutras**, Book 2 Chapters 1–3 (yogas, raja yogas, bandhana, niryana)
  - **Brihat Parashara Hora Shastra** Ch. 34 (karaka cross-references), Ch. 50 (Chara Dasha foundation)
  - **Saravali** (Kalyanavarma) — supplementary Jaimini references
  - **Jataka Parijata** (Vaidyanatha Dikshita), Ch. 13 (Ghati Arudha), Ch. 18 (Jaimini dasas cross-reference)
  - **Jaimini Sutras commentary** by Irangati Rangacharya (Sagar Publications), §1.1–§5.50
  - **Kalpalatha** (Somanatha) — advanced Jaimini yogas (not shipped in v1; referenced for P4 expansion)
- Reference implementations: Jagannatha Hora 7.x (primary); Maitreya9 (secondary for karaka/arudha cross-check)
