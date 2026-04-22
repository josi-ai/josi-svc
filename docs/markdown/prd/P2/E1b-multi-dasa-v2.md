---
prd_id: E1b
epic_id: E1
title: "Multi-Dasa Engine v2 (Chara + Narayana + Kalachakra)"
phase: P2-breadth
tags: [#correctness, #extensibility]
priority: must
depends_on: [E1a, F1, F2, F4, F6, F7, F8, F13, F16, F17]
enables: [E3, E11b, E14a]
classical_sources: [bphs, jaimini_sutras, jataka_parijata, saravali]
estimated_effort: 4-5 weeks
status: draft
author: @agent-claude-opus-4-7
last_updated: 2026-04-21
---

# E1b — Multi-Dasa Engine v2 (Chara + Narayana + Kalachakra)

## 1. Purpose & Rationale

E1a shipped **Vimshottari + Yogini + Ashtottari** — three nakshatra-anchored, lord-based Parashari dasa systems. E1b completes Josi's dasa breadth with three advanced, structurally different systems:

1. **Chara Dasha (Jaimini)** — a *sign*-based dasa where each mahadasha equals a rasi. Direction and period per rasi are determined by Atmakaraka placement and a count-to-lord formula. Total cycle ~144 years. Introduced in Jaimini Upadesha Sutras; elaborated in BPHS Ch. 50 and Irangati Rangacharya's commentary. Indispensable for timing career and life-sphere transitions in Jaimini readings.
2. **Narayana Dasha (Jaimini)** — another sign-based dasa with different starting rasi rules (based on 7th from Lagna or Karakamsa) and different direction logic. Total cycle matches Chara (~144 years, 12 padakramas). Used for "what event manifests when" macro-timing.
3. **Kalachakra Dasha** — the most computationally intricate classical dasa. 9 periods per nakshatra pada. Based on Moon's pada, resolves to "Savya" (forward) or "Apasavya" (reverse) paryaya, selects one of four rasi sequences with per-rasi year allotments (Mesha=7, Vrishabha=16, …). Total cycle varies by starting pada (~83 to ~100 years). Source: BPHS Ch. 53; expanded in Jataka Parijata.

All three systems emit the same `temporal_hierarchy` output shape defined in F7 and reuse the per-source compute + aggregation infrastructure from F8. Unlike E1a's nakshatra-lord systems, Chara and Narayana are **sign-anchored** (the "lord" field of each period is a rasi name rather than a planetary lord), and Kalachakra is **pada-anchored** (a paryaya × rasi combination). The F7 `TemporalRange.lord` field is repurposed to hold whichever abstraction is appropriate; an additional `details.system_kind ∈ {nakshatra_lord, sign, paryaya}` carries the discriminator for downstream consumers.

**Correctness bar:** every period boundary must match Jagannatha Hora 7.x within ±1 day across a cross-verified golden suite of at least 5 charts per system.

## 2. Scope

### 2.1 In scope
- Three new engines: `CharaDasaEngine`, `NarayanaDasaEngine`, `KalachakraDasaEngine`, each implementing the `ClassicalEngine` Protocol from F8.
- Three rule YAML documents per F6 DSL (one per system). The rule body is **declarative metadata** (cycle kind, starting-point method, per-rasi year tables, paryaya lookups) rather than pure predicate composition; the engine interprets the metadata block and executes the algorithm in Python. Rationale: dasa-sequence construction is fundamentally procedural (walk a sign order with direction flips) and is not reasonable to express in pure boolean predicates.
- 3-level temporal hierarchy (mahadasha → antardasha → pratyantardasa) for all three systems.
- Sidereal astronomical inputs shared with Vimshottari: Moon longitude, Moon nakshatra+pada, Atmakaraka planet/sign, Lagna sign, Karakamsa sign.
- Golden chart fixtures: 5 charts × 3 systems × 3 levels, all boundaries cross-verified against JH 7.x (primary reference) and Maitreya9 (secondary).
- Property tests (F17): sum invariants, no gaps, no overlaps, monotonic time, direction consistency, recompute determinism.
- REST endpoint extension: `GET /api/v1/dasha/{chart_id}?system={chara|narayana|kalachakra}`.
- AI tool-use extension: `get_current_dasa(chart_id, system, level)` accepts the three new systems.
- Documentation of divergences across classical commentaries, with Josi's chosen lineage flagged per rule YAML.

### 2.2 Out of scope
- **Tribhagi, Brahma, Trikona, Shatabdika and other rare Jaimini variants** — deferred to P4 reference-set expansion. Only Chara and Narayana cover 95% of Jaimini practice.
- **Sookshma (4th level) and Prana (5th level) subdivisions** — like E1a, E1b stops at pratyantardasa. 4+ levels deferred to P3+ as usage data warrants.
- **Chara Dasha rashi drishti overlays during dasa windows** — delegated to E3 (Jaimini System), which consumes Chara Dasha periods and applies rashi drishti on top.
- **Kalachakra "Mandook Dasha" leaping variants** — deferred; the standard Savya/Apasavya covers the common case.
- **Phalita (prediction) interpretation layer** — E11a / E11b owns this; E1b only emits temporal periods.
- **Cross-source reconciliation when BPHS Ch.50 disagrees with Jaimini Sutras Ch.4 on Chara direction edge cases** — ship BPHS default + Jaimini-Rangacharya-commentary variant as alternate rule; astrologer preference selects.

### 2.3 Dependencies
- E1a (base `BaseDasaEngine` extracted; this PRD extends it).
- F1 (source authorities `bphs`, `jaimini_sutras`, `jataka_parijata`, `saravali` seeded).
- F2 (classical_rule, technique_compute tables).
- F4 (effective_from/to, content_hash).
- F6 (rule YAML loader).
- F7 (`temporal_hierarchy` output shape with JSON Schema).
- F8 (engine Protocol + aggregation strategies).
- F13 (content-hash provenance).
- F16 (golden chart suite scaffolding).
- F17 (property-based test harness).
- Existing chart data: Atmakaraka (ranking by sidereal longitude of the 7 graha excluding Ketu by the Parashari school; Rahu optional per Jaimini variant), Lagna sign, Karakamsa sign (Atmakaraka's Navamsha sign), Moon nakshatra and pada.

## 2.4 Design Decisions (Pass 1 Astrologer Review — Locked 2026-04-21)

All open questions from E1b Pass 1 astrologer review are resolved. Cross-cutting decisions reference `DECISIONS.md`; E1b-specific decisions documented here.

### Cross-cutting decisions (applied via `DECISIONS.md`)

| Decision | Value | Ref |
|---|---|---|
| Ayanamsa default | Lahiri B2C + 9-shortlist astrologer | 1.2 |
| Rahu/Ketu node type | Both Mean + True computed (affects AK candidacy for Rahu, Rahu-MD periods) | 1.1 |
| Natchathiram count | 27 (affects Kalachakra pada→paryaya selection) | 3.7 |
| Dasai hierarchy depth | 5 levels (MD→AD→PD→Sookshma→Prana) for both user types | 1.4 |
| Dasai matching bar vs JH | ±1 day (inherited from E1a Q9) | E1a §2.4 |
| Language display | Sanskrit-IAST + Tamil phonetic | 1.5 |

### E1b-specific decisions (locked this review)

| Decision | Value | Source |
|---|---|---|
| **Atmakaraka determination** (Q1) | **8-karaka (include Rahu)** — Rahu's AK candidacy = `30° − longitude_within_sign`. Traditional Jaimini per Upadesha Sutras + Rangacharya + Rath + Rao + JH/PL. Same for both user types. | Q1 |
| **Chara Dasai direction rule** (Q2) | **BPHS Ch.50 parity rule** — odd starting rasi → forward direction; even starting rasi → backward direction. Matches JH + PL + Astrosage + Tamil Vakya default. | Q2 |
| **Chara Dasai period-length formula** (Q3) | **BPHS Ch.50 count-to-lord**, traditional rulers only (Sevvai for Viruchigam, Sani for Kumbham — NOT Ketu/Rahu co-rulership). Period = count−1 years (forward/backward per Q2 direction); 12 years if lord in rasi itself. Total cycle ~144 years. | Q3 |
| **Narayana Dasai starting rule** (Q4) | **Karakamsa rasi (Variant B) default + astrologer toggle to 7th-from-Lagna (Variant A)**. Matches JH convention. Classical foundation: Jaimini Upadesha Sutras + Rangacharya + Rath + Rao. | Q4 |
| **Kalachakra paryaya selection** (Q5) | **BPHS Ch.53 standard paryaya table** — canonical 108-pada × 4-paryaya mapping (Savya-1 / Savya-2 / Apasavya-1 / Apasavya-2). Savya year table: Mesham=7, Rishabam=16, Mithunam=9, Kadagam=21, Simmam=5, Kanni=9, Thulam=16, Viruchigam=7, Dhanusu=10. Apasavya per BPHS Ch.53 corresponding table. | Q5 |
| **Kalachakra rasi-year table** (Q6 covered by Q5) | BPHS Ch.53 canonical. Both Savya and Apasavya tables from same source. | covered via Q5 |
| **Cross-source aggregation** (Q7) | **Option C — BPHS canonical default + 1 Rangacharya commentary variant per Jaimini dasai, 2-option astrologer-profile toggle.** Chara: BPHS parity rule (default) + Rangacharya lord-placement variant (toggle). Narayana: Karakamsa (default, locked Q4) + 7th-from-Lagna (toggle). Kalachakra: BPHS Ch.53 standard only (no variant; Mandook/Gatika deferred as research curiosities). No full F8 aggregation for MVP. Matches JH convention + PRD §2.2 intention. | Q7 |

### Engineering action items (not astrologer-review scope)

- [ ] CharaDasaEngine: implement BPHS Ch.50 parity direction + count-to-lord period; Rangacharya variant as sibling rule via F6 YAML DSL
- [ ] NarayanaDasaEngine: Karakamsa-based starting (AK's Navamsa position); 7th-from-Lagna as sibling rule
- [ ] KalachakraDasaEngine: BPHS Ch.53 pada→paryaya lookup table + Savya/Apasavya year tables; handle natchathiram-pada edge cases per boundary-inclusive lower convention (DECISIONS 3.7)
- [ ] 8-karaka AK computation with Rahu's `30° − longitude` rule; expose 7-karaka mode as optional astrologer toggle
- [ ] Golden chart suite: 5 charts × 3 dasai systems × 3 levels at ±1 day bar vs JH 7.x
- [ ] Property tests: sum invariants, no gaps, no overlaps, direction consistency, paryaya selection determinism

---

## 3. Classical / Technical Research

### 3.1 Chara Dasha (Jaimini)

**Primary source:** Jaimini Upadesha Sutras, Book 1, Chapter 4 (*daśā-adhyāya*). Elaborated in BPHS Ch. 50 (Parashari adoption). Canonical modern commentary: Irangati Rangacharya, *Jaimini Sutras* (Sagar Publications), §4.1–§4.42.

**System kind:** sign-based. Each mahadasha = one rasi; the "lord" displayed is the rasi name (e.g., "mesha"), and the ruling planet of that rasi governs interpretation. Total cycle = sum of 12 rasi durations ≈ 144 years.

#### 3.1.1 Starting rasi

The starting mahadasha rasi is **Lagna rasi** (the rising sign at birth). This is the standard BPHS + Parashari-Jaimini rule.

*Alternate schools* (shipped as separate rule YAMLs, not defaults):
- "Karaka Lagna school" (Rangacharya §4.3): start from **Karakamsa Lagna** (Atmakaraka's Navamsha sign projected as Lagna).
- "Atma Lagna school" (rare): start from **Atmakaraka's rasi** in Rashi.

Josi default is **BPHS / Lagna-start**, matching JH 7.x default, which enables differential testing.

#### 3.1.2 Direction (Savya / Apasavya)

Direction is determined by whether the Lagna rasi is odd (Aries=1, Gemini=3, …) or even (Taurus, Cancer, …), and whether the Atmakaraka is in the Lagna rasi or not.

Per BPHS 50.4-6 and Rangacharya §4.7:

| Lagna rasi parity | Atmakaraka relationship | Direction |
|---|---|---|
| Odd (1,3,5,7,9,11) | AK not in Lagna sign | **Savya** (forward: zodiacal order) |
| Even (2,4,6,8,10,12) | AK not in Lagna sign | **Apasavya** (reverse: anti-zodiacal) |
| Any | AK in Lagna sign itself | Direction based on **7th from Lagna** parity instead (odd → Savya, even → Apasavya) |

Computationally: `rasi_order = 1..12` in zodiacal sequence (Aries=1). Savya walks `[L, L+1, L+2, …]` modulo 12. Apasavya walks `[L, L-1, L-2, …]` modulo 12.

#### 3.1.3 Period per rasi (the "12 minus count-to-lord" rule)

The central formula of Chara Dasha, per BPHS 50.7 and Rangacharya §4.10:

```
period(R) years = 12 − count_from_rasi_to_its_lord(R)
```

Where `count_from_rasi_to_its_lord(R)` counts signs starting at R (inclusive of R=1) walking forward to the sign occupied by R's ruling planet, again inclusive — i.e., *inclusive-both-ends* counting, which is the Jaimini convention.

Exception per BPHS 50.8 and Rangacharya §4.12: if the lord of R is in R itself (i.e., count = 1), the period is **12 years** (treat "12 − 1 = 11" as the exception → bumped to 12). Some commentators apply additional bumps for exaltation; Josi does not apply those in v1 (flagged as lineage variant).

Worked example (chart dependent — the lord of a sign depends on where the lord-planet sits in the *birth chart*, not the zodiac):

Suppose in a chart:
- Mars (lord of Aries) sits in Leo. Count Aries → Leo inclusive both ends = 5. Period of Aries = 12 − 5 = 7 years.
- Venus (lord of Taurus) sits in Taurus itself. Count = 1. Period of Taurus = 12 (exception).
- Mercury (lord of Gemini) sits in Sagittarius. Count Gemini → Sagittarius inclusive = 7. Period of Gemini = 12 − 7 = 5 years.

Sum of all 12 periods is chart-specific; typically 120–144 years.

#### 3.1.4 Antardasha within Chara mahadasha

Per BPHS 50.11 and Rangacharya §4.18: within each mahadasha rasi M, the 12 antardasha rasis appear in the same direction (Savya/Apasavya) as the mahadasha sequence, starting from M itself. The antardasha duration for sub-rasi A inside mahadasha M is:

```
antardasha_duration(A, inside M) = M_mahadasha_duration × A_mahadasha_duration / sum_of_all_12_mahadasha_durations
```

i.e., proportional to A's own mahadasha duration. Sum of all 12 antardashas inside M equals M_mahadasha_duration.

#### 3.1.5 Pratyantardasa

Same proportional recursive formula:

```
pratyantar(P, inside A, inside M) = antardasha_duration(A, M) × P_mahadasha_duration / sum_of_all_12_mahadasha_durations
```

#### 3.1.6 Special case: Ketu and the "8th rasi" rule

Per Rangacharya §4.15: some commentators include **Ketu's rasi** (Ketu does not rule any zodiacal sign in the standard Parashari scheme; in Jaimini, Ketu co-rules Scorpio with Mars in some schools). Josi v1 does **not** apply Ketu co-lordship; only the classical 7 grahas rule (Sun=Leo, Moon=Cancer, Mars=Aries+Scorpio, Mercury=Gemini+Virgo, Jupiter=Sagittarius+Pisces, Venus=Taurus+Libra, Saturn=Capricorn+Aquarius). This matches JH default.

### 3.2 Narayana Dasha (Jaimini)

**Primary source:** Jaimini Sutras Ch. 4 (continued). Rangacharya commentary §4.50–§4.75. Also called "Padakrama Dasha" in some lineages.

**System kind:** sign-based, 12 padakramas. Total cycle similarly chart-dependent ≈ 144 years.

#### 3.2.1 Starting rasi

Per Jaimini Sutras 4.50 and Rangacharya §4.52:

- Find **which is stronger**: the **Lagna rasi** or the **7th from Lagna**. Strength is determined by a ranked set of criteria (Jaimini Sutras 4.51–4.55; summarized):
  1. The sign containing **more planets** is stronger.
  2. Tiebreak: the sign whose **lord is stronger** (lord closer to Atmakaraka by sign count, Atmakaraka itself being the strongest reference).
  3. Tiebreak: the sign whose **natural lord** (planet ruling it) has **higher longitude**.
  4. Further tiebreakers per Rangacharya §4.54–§4.55.
- The stronger of Lagna or 7th-from-Lagna is the **starting rasi**.

Josi implements a deterministic strength function in Python matching JH 7.x's documented ordering. Edge-case ties at >3 levels are broken by lexicographic rasi-id as a deterministic fallback (flagged in logs).

#### 3.2.2 Direction

Per Jaimini Sutras 4.57 and Rangacharya §4.60:

- If the **starting rasi is odd** (movable or fixed-odd: Aries, Gemini, Leo, Libra, Sagittarius, Aquarius) → **Savya** (forward).
- If the **starting rasi is even** → **Apasavya** (reverse).

(Note: this parity rule differs slightly across lineages; the above matches BPHS + JH. Some Saravali-influenced schools use movable/fixed/dual directly. Flagged in rule YAML as BPHS lineage.)

#### 3.2.3 Period per rasi

Narayana Dasha uses the **same "12 minus count-to-lord" formula** as Chara Dasha (§3.1.3), with the **same exception for count=1** → 12 years. The difference from Chara is:

- **Counting direction**: for Narayana, the count from rasi R to its lord's occupied sign is done in the *dasa direction* (Savya or Apasavya), not always forward. Per Rangacharya §4.63.
- Practical consequence: a chart will produce different period values for the same 12 rasis under Chara vs Narayana because the count direction flips for half of them in Apasavya Narayana.

#### 3.2.4 Antardasha and Pratyantardasa

**Same proportional subdivision** as Chara (§3.1.4–5). Narayana's antardasha starting rasi within a mahadasha M is also **M itself**; direction follows the mahadasha direction.

#### 3.2.5 Variants shipped

- `dasa.narayana.bphs` — BPHS / JH default, starting rasi = stronger of Lagna vs 7th from Lagna, parity rule per §3.2.2.
- `dasa.narayana.karakamsa.jaimini` — alternate starting rasi = Karakamsa Lagna, still with parity-based direction. Shipped as an alternate rule, not default.

### 3.3 Kalachakra Dasha

**Primary source:** BPHS Ch. 53 (*Kālacakra-daśā adhyāya*). Extensive elaboration in Jataka Parijata Ch. 19 and Kalidasa's *Uttara Kalamrita*. Most computationally intricate classical dasa system.

**System kind:** pada-based → paryaya-sequence-based. Total cycle varies by starting pada, typically 83–100 years (full paryaya covers 9 rasis).

#### 3.3.1 Moon's nakshatra and pada

The starting paryaya + rasi + duration are determined by **Moon's nakshatra pada** (quarter). Each nakshatra = 13°20′ = 4 padas of 3°20′ each. The 27 nakshatras × 4 padas = 108 distinct starting points. The Kalachakra scheme groups these 108 into 4 paryaya types:

| Nakshatra group (by nakshatra #) | Paryaya |
|---|---|
| 1, 5, 9, 13, 17, 21, 25 (Ashwini, Mrigashira, Ashlesha, Hasta, Anuradha, U. Ashadha, P. Bhadrapada) | **Savya-Paryaya 1** |
| 2, 6, 10, 14, 18, 22, 26 (Bharani, Ardra, Magha, Chitra, Jyeshtha, Shravana, U. Bhadrapada) | **Apasavya-Paryaya 1** |
| 3, 7, 11, 15, 19, 23, 27 (Krittika, Punarvasu, P. Phalguni, Swati, Mula, Dhanishta, Revati) | **Savya-Paryaya 2** |
| 4, 8, 12, 16, 20, 24 (Rohini, Pushya, U. Phalguni, Vishakha, P. Ashadha, Shatabhisha) | **Apasavya-Paryaya 2** |

Per pada (1/2/3/4) within the nakshatra, a specific index into the paryaya's rasi sequence is selected.

#### 3.3.2 Paryaya rasi sequences

Per BPHS 53.4–53.16, each paryaya has **9 rasis** in a specific, memorized order with **fixed year allotments per rasi**:

**Rasi → years table (BPHS 53.11, the foundational memorized table):**

| Rasi | Years |
|---|---|
| Aries (Mesha) | 7 |
| Taurus (Vrishabha) | 16 |
| Gemini (Mithuna) | 9 |
| Cancer (Karka) | 21 |
| Leo (Simha) | 5 |
| Virgo (Kanya) | 9 |
| Libra (Tula) | 16 |
| Scorpio (Vrischika) | 7 |
| Sagittarius (Dhanus) | 10 |
| Capricorn (Makara) | 4 |
| Aquarius (Kumbha) | 4 |
| Pisces (Meena) | 10 |

Total of all 12 = 118 years. But any single paryaya uses only **9 of these 12 rasis**, not all. The paryaya sequences (per BPHS 53.7–53.10) are:

**Savya-Paryaya 1** (starts from Aries, traverses odd-numbered cluster of rasis):
`[Aries, Taurus, Gemini, Cancer, Leo, Virgo, Libra, Scorpio, Sagittarius]` for **pada 1**.
Sum = 7+16+9+21+5+9+16+7+10 = 100 years.

For pada 2 within a Savya-Paryaya-1 nakshatra, the sequence shifts (starts from the 2nd rasi of the paryaya and cycles): `[Taurus, Gemini, Cancer, Leo, Virgo, Libra, Scorpio, Sagittarius, Capricorn]`. Pada 3 starts from Gemini; pada 4 starts from Cancer; each time a different 9-of-12 window is selected.

**Apasavya-Paryaya 1** uses reverse traversal from a different starting rasi:
pada 1 → `[Cancer, Gemini, Taurus, Aries, Pisces, Aquarius, Capricorn, Sagittarius, Scorpio]`.
Subsequent padas shift analogously in reverse.

**Savya-Paryaya 2** (BPHS 53.9) starts from Leo for pada 1:
`[Leo, Virgo, Libra, Scorpio, Sagittarius, Capricorn, Aquarius, Pisces, Aries]`.
Subsequent padas shift forward.

**Apasavya-Paryaya 2** (BPHS 53.10) starts from Scorpio for pada 1, reversing:
`[Scorpio, Libra, Virgo, Leo, Cancer, Gemini, Taurus, Aries, Pisces]`.
Subsequent padas shift backward.

**Implementation form:** encode the four paryaya tables × 4 pada windows = 16 possible 9-rasi sequences explicitly in the rule YAML (as a `paryaya_table`), rather than deriving by arithmetic. Like Yogini's 27-row nakshatra lookup, arithmetic derivation here is where modern tools most frequently err; BPHS verses are unambiguous when encoded verbatim.

#### 3.3.3 Balance of starting rasi

Per BPHS 53.18–53.20:

The fraction of the starting pada's nakshatra-span already traversed at birth determines the balance of the first (starting) rasi in the paryaya. The pada span is 3°20′ = 200 arc-minutes.

```
pada_offset_arcmin = (moon_longitude mod 13°20') mod 3°20'     // position within current pada
pada_fraction_elapsed = pada_offset_arcmin / 200_arcmin
balance_of_first_rasi = first_rasi_years × (1 − pada_fraction_elapsed)
```

#### 3.3.4 Antardasha within Kalachakra mahadasha

Per BPHS 53.25–53.28: antardashas within a mahadasha rasi M are the **same 9 paryaya rasis** (not all 12), proportional to their own year durations:

```
antardasha_duration(A, inside M) = M_duration × A_mahadasha_duration / paryaya_total_years
```

where `paryaya_total_years` is the sum of the 9 rasis in M's paryaya (e.g., 100 for Savya-Paryaya 1 pada 1).

Sum of 9 antardashas inside M = M_duration. ✓

#### 3.3.5 Pratyantardasa

Same proportional formula, nested one level.

#### 3.3.6 "Mandook Dasha" leaps

Per BPHS 53.30–53.32, at specific transitions (e.g., from the 5th to the 6th rasi in a paryaya), a **leap** ("Mandook") occurs where the dasa sequence jumps non-adjacently. Josi v1 **does not implement Mandook** — its application is disputed (some commentators apply it, others don't; JH 7.x does not by default). Flagged as a `dasa.kalachakra.mandook.bphs` future variant rule, explicitly out of scope for E1b.

### 3.4 Engine architecture

All three systems extend `BaseDasaEngine` (from E1a) but override `_find_starting` and add new helper methods:

```
BaseDasaEngine (from E1a)
  ├─ _find_starting() [abstract]
  ├─ _build_mahadasha_sequence()
  ├─ _build_antardasha()
  ├─ _build_pratyantar()
  └─ emit TemporalHierarchyResult

CharaDasaEngine(BaseDasaEngine)  — NEW
  ├─ system_kind = "sign"
  ├─ _find_starting() → starting_rasi (Lagna sign), direction (Savya/Apasavya)
  ├─ _compute_rasi_period(rasi, chart) → years via "12 − count_to_lord" + exception
  └─ override _build_mahadasha_sequence to walk signs in direction, no nakshatra logic

NarayanaDasaEngine(BaseDasaEngine)  — NEW
  ├─ system_kind = "sign"
  ├─ _find_starting() → stronger of (Lagna, 7th from Lagna), direction by parity
  ├─ _compute_rasi_period(rasi, chart, direction) → same formula, count in direction
  └─ override _build_mahadasha_sequence analogously

KalachakraDasaEngine(BaseDasaEngine)  — NEW
  ├─ system_kind = "paryaya"
  ├─ _find_starting() → paryaya + pada → 9-rasi sequence, balance of first rasi
  ├─ _rasi_duration_for_paryaya(rasi) → lookup from BPHS 53.11 table
  └─ override _build_mahadasha_sequence to walk 9-rasi paryaya, not 12
```

All three emit `TemporalHierarchyResult` with `root_system ∈ {chara, narayana, kalachakra}`. The `DasaPeriod.lord` field holds `"mesha"`, `"vrishabha"`, etc. (rasi names) for Chara/Narayana, and the paryaya rasi for Kalachakra. `DasaPeriod.details.system_kind` holds `"sign"` or `"paryaya"` for consumer disambiguation.

### 3.5 Rule YAML shape (F6 DSL)

The rule body, while F6 DSL compatible, is *mostly declarative metadata* interpreted by the engine — **not** a pure predicate composition. This is a conscious DSL extension for dasa rules: they need `compute.engine: <engine_id>` to dispatch to Python logic. Activation remains pure predicate-DSL.

**`src/josi/rules/dasas/chara_bphs.yaml`**:

```yaml
rule_id: dasa.chara.bphs
source_id: bphs
version: "1.0.0"
technique_family_id: dasa
output_shape_id: temporal_hierarchy
citation: "BPHS Ch.50 v.1-28; Jaimini Sutras Bk.1 Ch.4"
classical_names:
  en: "Chara Dasha"
  sa_iast: "Cara Daśā"
  sa_devanagari: "चर दशा"
  ta: "சர தசை"
effective_from: "2026-06-01T00:00:00Z"
effective_to: null

rule_body:
  activation:
    predicate: always_true
  compute:
    engine: chara_dasa
    system_kind: sign
    cycle_kind: variable_sum_twelve_rasis
    starting_rasi_rule:
      method: lagna_rasi               # 'lagna_rasi' | 'karakamsa' | 'atmakaraka_rasi'
      atmakaraka_in_lagna_fallback: seventh_from_lagna_parity
    direction_rule:
      method: parity_of_starting_with_ak_exception
    period_formula:
      name: twelve_minus_count_to_lord
      count_direction: forward_only    # Chara uses forward count always
      exception_when_count_is_one: set_to_twelve
    levels: 3
    antardasha_formula: proportional_to_own_mahadasha_over_sum
    pratyantar_formula: recursive_proportional
```

**`src/josi/rules/dasas/narayana_bphs.yaml`**:

```yaml
rule_id: dasa.narayana.bphs
source_id: bphs
version: "1.0.0"
technique_family_id: dasa
output_shape_id: temporal_hierarchy
citation: "Jaimini Sutras Bk.1 Ch.4 v.50-75; BPHS Ch.51"
classical_names:
  en: "Narayana Dasha"
  sa_iast: "Nārāyaṇa Daśā"
  sa_devanagari: "नारायण दशा"
  ta: "நாராயண தசை"
effective_from: "2026-06-01T00:00:00Z"
effective_to: null

rule_body:
  activation:
    predicate: always_true
  compute:
    engine: narayana_dasa
    system_kind: sign
    cycle_kind: variable_sum_twelve_rasis
    starting_rasi_rule:
      method: stronger_of_lagna_or_seventh
      strength_ranking:
        - more_planets_in_sign
        - lord_stronger_by_ak_proximity
        - lord_higher_longitude
        - rangacharya_fourth_tiebreak
        - lexicographic_rasi_id_fallback
    direction_rule:
      method: parity_of_starting_rasi
    period_formula:
      name: twelve_minus_count_to_lord
      count_direction: dasa_direction   # counts in Savya/Apasavya, not always forward
      exception_when_count_is_one: set_to_twelve
    levels: 3
    antardasha_formula: proportional_to_own_mahadasha_over_sum
    pratyantar_formula: recursive_proportional
```

**`src/josi/rules/dasas/kalachakra_bphs.yaml`**:

```yaml
rule_id: dasa.kalachakra.bphs
source_id: bphs
version: "1.0.0"
technique_family_id: dasa
output_shape_id: temporal_hierarchy
citation: "BPHS Ch.53 v.1-32; Jataka Parijata Ch.19"
classical_names:
  en: "Kalachakra Dasha"
  sa_iast: "Kālacakra Daśā"
  sa_devanagari: "कालचक्र दशा"
  ta: "காலசக்ர தசை"
effective_from: "2026-06-01T00:00:00Z"
effective_to: null

rule_body:
  activation:
    predicate: always_true
  compute:
    engine: kalachakra_dasa
    system_kind: paryaya
    cycle_kind: paryaya_nine_rasis

    rasi_to_years:      # BPHS 53.11, standard table
      mesha:         7
      vrishabha:    16
      mithuna:       9
      karka:        21
      simha:         5
      kanya:         9
      tula:         16
      vrischika:     7
      dhanus:       10
      makara:        4
      kumbha:        4
      meena:        10

    paryaya_assignment:
      # nakshatra_number (1-27) → paryaya_id
      1:  savya_paryaya_1
      2:  apasavya_paryaya_1
      3:  savya_paryaya_2
      4:  apasavya_paryaya_2
      5:  savya_paryaya_1
      6:  apasavya_paryaya_1
      7:  savya_paryaya_2
      8:  apasavya_paryaya_2
      9:  savya_paryaya_1
      10: apasavya_paryaya_1
      11: savya_paryaya_2
      12: apasavya_paryaya_2
      13: savya_paryaya_1
      14: apasavya_paryaya_1
      15: savya_paryaya_2
      16: apasavya_paryaya_2
      17: savya_paryaya_1
      18: apasavya_paryaya_1
      19: savya_paryaya_2
      20: apasavya_paryaya_2
      21: savya_paryaya_1
      22: apasavya_paryaya_1
      23: savya_paryaya_2
      24: apasavya_paryaya_2
      25: savya_paryaya_1
      26: apasavya_paryaya_1
      27: savya_paryaya_2

    paryaya_tables:
      # Each paryaya × pada → 9-rasi sequence. 16 rows total.
      savya_paryaya_1:
        pada_1: [mesha, vrishabha, mithuna, karka, simha, kanya, tula, vrischika, dhanus]
        pada_2: [vrishabha, mithuna, karka, simha, kanya, tula, vrischika, dhanus, makara]
        pada_3: [mithuna, karka, simha, kanya, tula, vrischika, dhanus, makara, kumbha]
        pada_4: [karka, simha, kanya, tula, vrischika, dhanus, makara, kumbha, meena]
      apasavya_paryaya_1:
        pada_1: [karka, mithuna, vrishabha, mesha, meena, kumbha, makara, dhanus, vrischika]
        pada_2: [mithuna, vrishabha, mesha, meena, kumbha, makara, dhanus, vrischika, tula]
        pada_3: [vrishabha, mesha, meena, kumbha, makara, dhanus, vrischika, tula, kanya]
        pada_4: [mesha, meena, kumbha, makara, dhanus, vrischika, tula, kanya, simha]
      savya_paryaya_2:
        pada_1: [simha, kanya, tula, vrischika, dhanus, makara, kumbha, meena, mesha]
        pada_2: [kanya, tula, vrischika, dhanus, makara, kumbha, meena, mesha, vrishabha]
        pada_3: [tula, vrischika, dhanus, makara, kumbha, meena, mesha, vrishabha, mithuna]
        pada_4: [vrischika, dhanus, makara, kumbha, meena, mesha, vrishabha, mithuna, karka]
      apasavya_paryaya_2:
        pada_1: [vrischika, tula, kanya, simha, karka, mithuna, vrishabha, mesha, meena]
        pada_2: [tula, kanya, simha, karka, mithuna, vrishabha, mesha, meena, kumbha]
        pada_3: [kanya, simha, karka, mithuna, vrishabha, mesha, meena, kumbha, makara]
        pada_4: [simha, karka, mithuna, vrishabha, mesha, meena, kumbha, makara, dhanus]

    balance_formula:
      pada_span_arcmin: 200
      formula: "first_rasi_years * (1 - (moon_longitude_mod_13_20 mod 3_20) / 200)"

    levels: 3
    antardasha_formula: proportional_over_paryaya_total_years
    pratyantar_formula: recursive_proportional
```

**Note on paryaya tables**: the exact 16-row mapping above is the author's best reading of BPHS 53.7–53.10 cross-referenced with JH 7.x generated output. These tables **MUST be verified cell-by-cell against JH 7.x** during T-E1b.5 golden-fixture authorship before shipping. Any discrepancy becomes a flagged classical-advisor review item. This is the single highest-risk fidelity item in the PRD.

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| Dasa rule YAML: pure predicate DSL or procedural metadata? | **Metadata-driven** (engine dispatches from `compute.engine` + tables). Activation remains predicate-based. | Dasa construction is fundamentally procedural; forcing pure-predicate DSL would either require hundreds of atomic predicates or collapse readability. F6 DSL supports `compute.*` as engine-interpreted metadata. |
| Chara default starting rasi | **Lagna rasi** (BPHS default, matches JH) | Differential testing precedence; alternate schools shipped as variant rules |
| Narayana strength tiebreak at >3 deep | **Lexicographic rasi-id fallback with WARN log** | Determinism required; log allows investigation |
| Kalachakra Mandook leaps | **Not implemented in v1** (flagged future) | Lineage-dependent; JH 7.x default does not apply |
| Ketu co-lordship for Chara sign-period formula | **Not applied in v1** (classical 7-graha lordship only) | Matches JH default |
| Paryaya tables: encode explicitly vs derive | **Encoded explicitly** (16 × 9 rasi sequences in YAML) | Arithmetic derivation is error-prone; verses are unambiguous when encoded verbatim |
| Levels: 2 or 3? | **3** (MD, AD, PD) | Classical minimum; F9 view can collapse to 2 |
| Float precision for 3-level nested arithmetic | **`Decimal` internally, convert to datetime on emission** | Avoids boundary drift over ~100 years × 9 rasis × 9 AD × 9 PD |
| Atmakaraka ranking: include Rahu or not? | **Exclude Rahu in v1 (Parashari school)** | JH default; Jaimini-with-Rahu shipped as alternate in E3 (not E1b) |
| 5-chart minimum for golden fixtures (vs 10 in E1a) | **5 per system × 3 systems = 15 fixtures** | Kalachakra manual JH cross-check is labor-intensive; 5 is minimum statistically useful; expand in C5 (differential testing) |
| Narayana "karakamsa start" variant | **Shipped as alternate rule `dasa.narayana.karakamsa.jaimini`** | Enables astrologer-preference selection without engine fork |
| Effective_from: aligned with E1a (2026-01-01) or later (2026-06-01)? | **2026-06-01** | Signals P2 rollout phase; allows astrologer-preview tier |

## 5. Component Design

### 5.1 New modules

```
src/josi/services/classical/dasa/
├── chara_engine.py
├── narayana_engine.py
├── kalachakra_engine.py
├── jaimini_common.py             # shared: inclusive-count-to-lord, AK resolution, strength ranking
└── paryaya_tables.py             # in-memory constants loaded from YAML — the 16 × 9 arrays

src/josi/rules/dasas/
├── chara_bphs.yaml
├── narayana_bphs.yaml
├── narayana_karakamsa_jaimini.yaml         # alternate starting-rasi variant
└── kalachakra_bphs.yaml

src/josi/schemas/classical/dasa/
└── temporal_hierarchy_schemas.py           # extended from E1a — adds system_kind enum

tests/golden/charts/dasa/
├── chart_01_expected_chara.yaml
├── chart_01_expected_narayana.yaml
├── chart_01_expected_kalachakra.yaml
├── ... (5 charts × 3 systems = 15 fixtures)

tests/classical/dasa/
├── test_chara_engine.py
├── test_narayana_engine.py
├── test_kalachakra_engine.py
└── test_e1b_properties.py
```

### 5.2 Data model additions

No new tables. Four new rows inserted into `classical_rule` (Chara BPHS, Narayana BPHS, Narayana-Karakamsa, Kalachakra BPHS) by the F6 loader. Compute rows land in existing `technique_compute` partition for `technique_family_id = 'dasa'`.

### 5.3 API contract

```
GET /api/v1/dasha/{chart_id}?system=chara
GET /api/v1/dasha/{chart_id}?system=narayana
GET /api/v1/dasha/{chart_id}?system=kalachakra

Query params (additions beyond E1a):
  - direction: [auto|savya|apasavya]   // advanced: override computed direction (for astrologer pro mode)
  - starting_rasi: [auto|<rasi_name>]   // advanced: override
  - source: [bphs|jaimini_sutras]       // default bphs

Response (200):
{
  "success": true,
  "message": "Dasa computed",
  "data": {
    "system": "chara",
    "rule_id": "dasa.chara.bphs",
    "source_id": "bphs",
    "rule_version": "1.0.0",
    "citation": "BPHS Ch.50 v.1-28",
    "root_system": "chara",
    "direction": "savya",
    "starting_rasi": "karka",
    "periods": [
      {
        "lord": "karka",
        "level": 1,
        "start": "1987-03-15T00:00:00Z",
        "end": "1994-03-15T00:00:00Z",
        "details": {
          "system_kind": "sign",
          "period_years_raw": 7.0,
          "period_formula_input": { "count_to_lord": 5, "lord": "moon", "lord_sign": "vrischika" }
        },
        "children": [...]
      },
      ...
    ]
  }
}
```

### 5.4 Internal Python interface

```python
# src/josi/services/classical/dasa/chara_engine.py

class CharaDasaEngine(BaseDasaEngine):
    technique_family_id = "dasa"
    default_output_shape_id = "temporal_hierarchy"
    system_kind = "sign"
    rule_id = "dasa.chara.bphs"

    async def compute_for_source(
        self, session: AsyncSession, chart_id: UUID, source_id: str,
        rule_ids: list[str] | None = None,
    ) -> list[TechniqueComputeRow]: ...

    def _find_starting(self, chart: AstrologyChart) -> tuple[str, Direction]:
        """Returns (starting_rasi_name, direction ∈ {Savya, Apasavya})."""

    def _compute_rasi_period(self, rasi: str, chart: AstrologyChart, direction: Direction) -> Decimal:
        """Returns years for mahadasha of `rasi` via 12 − count_to_lord with exception."""

    def _inclusive_count(self, from_rasi: str, to_rasi: str, direction: Direction) -> int:
        """Inclusive-both-ends sign count; Jaimini convention."""
```

```python
# src/josi/services/classical/dasa/narayana_engine.py

class NarayanaDasaEngine(BaseDasaEngine):
    system_kind = "sign"
    rule_id = "dasa.narayana.bphs"

    def _find_starting(self, chart: AstrologyChart) -> tuple[str, Direction]:
        """Returns (stronger of Lagna vs 7th from Lagna, direction by parity)."""

    def _compare_rasi_strength(self, rasi_a: str, rasi_b: str, chart: AstrologyChart) -> int:
        """Returns -1/0/1 per Rangacharya 5-level tiebreak ladder."""

    def _compute_rasi_period(self, rasi: str, chart: AstrologyChart, direction: Direction) -> Decimal:
        """Counts in direction, not always forward."""
```

```python
# src/josi/services/classical/dasa/kalachakra_engine.py

class KalachakraDasaEngine(BaseDasaEngine):
    system_kind = "paryaya"
    rule_id = "dasa.kalachakra.bphs"

    def _find_starting(self, chart: AstrologyChart) -> tuple[Paryaya, list[str], Decimal]:
        """Returns (paryaya, 9-rasi sequence, balance_years)."""

    def _rasi_duration(self, rasi: str) -> int:
        """Lookup from BPHS 53.11 table."""

    def _resolve_paryaya_and_pada(self, moon_nakshatra: int, moon_pada: int) -> tuple[str, int]:
        """(paryaya_id, pada_1_4) for the 16-row lookup."""
```

### 5.5 AI tool-use extension (F10)

```python
@tool
def get_current_dasa(
    chart_id: str,
    system: Literal["vimshottari", "yogini", "ashtottari", "chara", "narayana", "kalachakra"] = "vimshottari",
    level: int = 2,
    at_date: date | None = None,
) -> DasaPeriod:
    """Returns the dasa period(s) active at at_date for the named system.

    For sign-based systems (chara, narayana), the `lord` field holds the rasi name
    ('mesha', 'vrishabha', …); `details.ruling_planet` has the natural planetary ruler.
    For paryaya-based (kalachakra), `lord` is the current rasi in the paryaya.
    Citation is always embedded."""
```

## 6. User Stories

### US-E1b.1: As a Jaimini practitioner, I want to see my Chara Dasha mahadasha rasi and its period in years
**Acceptance:** `/api/v1/dasha/{chart_id}?system=chara` returns a 12-period hierarchy where each mahadasha period's `lord` is a rasi name and `details.period_formula_input` exposes the count-to-lord reasoning.

### US-E1b.2: As an astrologer in Pro mode, I want to select between BPHS Narayana vs Karakamsa-start Narayana per client
**Acceptance:** Setting `astrologer_source_preference.source_weights = {"jaimini_sutras": 1.0}` causes the Narayana-Karakamsa rule to be selected in aggregation; UI shows a "Narayana Dasha (Karakamsa start)" tag.

### US-E1b.3: As an engineer, I want to verify Kalachakra periods against Jagannatha Hora to within ±1 day
**Acceptance:** `tests/golden/charts/dasa/chart_01_expected_kalachakra.yaml` contains 9 mahadasha boundaries verified manually against JH 7.x; golden test passes.

### US-E1b.4: As a classical advisor, I want direction flip at "AK-in-Lagna" exception to match BPHS 50.6
**Acceptance:** `test_chara_ak_in_lagna_direction_fallback_to_seventh_parity` passes; classical advisor sign-off recorded in PR.

### US-E1b.5: As an AI agent calling `get_current_dasa(chart, system='narayana', level=3)`, I receive a 3-deep hierarchy with sign-based lords
**Acceptance:** Response is `DasaPeriod` tree depth 3; all `lord` fields are rasi names; `details.system_kind = "sign"`; citation embedded.

### US-E1b.6: As a research user, I want to compare Vimshottari and Chara predictions for the same transit window
**Acceptance:** `/api/v1/dasha/{chart_id}?system=all` (extension) returns both systems side-by-side; UI overlay works.

### US-E1b.7: As an engineer regenerating dasa for a chart, I want idempotent recomputes
**Acceptance:** Running compute twice on same chart × same rule version produces one `technique_compute` row; `output_hash` identical.

### US-E1b.8: As an astrologer running pro mode, I want to override the computed Chara direction
**Acceptance:** `GET /api/v1/dasha/{chart_id}?system=chara&direction=apasavya` returns the apasavya variant without touching persistent compute; `metadata.override_reason = "user_override"` in response.

## 7. Tasks

### T-E1b.1: Author three rule YAML files + one variant
- **Definition:** `chara_bphs.yaml`, `narayana_bphs.yaml`, `narayana_karakamsa_jaimini.yaml`, `kalachakra_bphs.yaml`. Include all tables (Kalachakra's 16 × 9 paryaya table, rasi→years table). Validate against F6 DSL schema via `poetry run validate-rules`.
- **Acceptance:** F6 loader parses all 4; 4 rows in `classical_rule`; content_hash stable across three reloads; Kalachakra paryaya tables classical-advisor-reviewed.
- **Effort:** 3 days (includes classical cross-reference)
- **Depends on:** F6, E1a

### T-E1b.2: Build `jaimini_common.py` helper module
- **Definition:** Shared helpers: `inclusive_count(from_rasi, to_rasi, direction)`, `resolve_atmakaraka(chart)`, `rank_rasi_strength(rasi_a, rasi_b, chart)` with 5-level tiebreak, `parity_of_rasi`, `rasi_lord`, `rasi_from_name`.
- **Acceptance:** Unit tests for each helper pass; mypy clean; lookup tables (rasi → lord, rasi → parity) are explicit.
- **Effort:** 2 days
- **Depends on:** E1a (access to chart data accessors)

### T-E1b.3: Implement `CharaDasaEngine`
- **Definition:** Subclass of `BaseDasaEngine` per §5.4. Uses `jaimini_common` helpers. Implements `_find_starting` (Lagna rasi + parity + AK-in-Lagna exception), `_compute_rasi_period` (12-minus-count, exception at count=1), `_build_mahadasha_sequence` (walk signs in direction), `_build_antardasha`/`_build_pratyantar` (proportional recursive).
- **Acceptance:** Unit tests pass: 6 starting-rasi cases (odd/even Lagna × AK-in vs AK-out); 10 period-formula cases; invariants (sum ≈ ~144, no gaps, no overlaps) hold on 1000 random charts.
- **Effort:** 3 days
- **Depends on:** T-E1b.1, T-E1b.2

### T-E1b.4: Implement `NarayanaDasaEngine`
- **Definition:** Subclass of `BaseDasaEngine`. Implements `_find_starting` using `rank_rasi_strength` for stronger-of-Lagna-vs-7th. Direction = parity of starting rasi. `_compute_rasi_period` counts in dasa direction (not forward). Antar/pratyantar proportional.
- **Acceptance:** Unit tests pass: 8 strength-ranking cases (including 4-way tie → lexicographic fallback + WARN log); 10 period cases; alternate karakamsa-start variant triggered by alternate rule_id.
- **Effort:** 3.5 days
- **Depends on:** T-E1b.1, T-E1b.2

### T-E1b.5: Implement `KalachakraDasaEngine`
- **Definition:** Subclass of `BaseDasaEngine`. Implements `_resolve_paryaya_and_pada`, `_find_starting` (paryaya + 9-rasi sequence + balance), `_rasi_duration` (BPHS 53.11 lookup), `_build_mahadasha_sequence` (walk 9 rasis of paryaya, not 12), antar/pratyantar over paryaya-total-years. Uses `Decimal` internally.
- **Acceptance:** Unit tests pass: 16 paryaya+pada resolution cases (one per row of `paryaya_tables`); 9 rasi-duration cases; sum-of-9-mahadashas equals paryaya_total_years; 3-level invariants hold.
- **Effort:** 4 days (highest complexity)
- **Depends on:** T-E1b.1, T-E1b.2

### T-E1b.6: Author 5 × 3 = 15 golden chart fixtures
- **Definition:** 5 canonical charts. For each, manually verify **all mahadasha and all first-level antardasha boundaries** for Chara, Narayana, Kalachakra against JH 7.x (primary) and Maitreya9 (secondary, where supported). Encode as F16 golden fixtures. Kalachakra paryaya tables must be cross-verified cell-by-cell during this process.
- **Acceptance:** Fixtures parse; cross-verification recorded in each YAML's `verified_by` field; at least 1 chart flags a known JH ↔ Maitreya divergence (expected for edge cases) with both values recorded.
- **Effort:** 5 days (bulk of manual verification)
- **Depends on:** F16

### T-E1b.7: Golden + property tests
- **Definition:** Golden-suite tests assert boundaries match JH fixtures to ±1 day. Property tests (F17, ≥1000 examples per system):
  - **Chara**: sum of 12 rasi periods in 115–145 range; no gaps/overlaps; direction consistent; exception-at-count-one triggers correctly.
  - **Narayana**: strength ranking deterministic with same chart; direction = parity of computed starting rasi.
  - **Kalachakra**: sum of 9 rasi MDs = paryaya_total_years ∈ {83, 86, 91, 100, ...}; balance ≤ first_rasi_years; monotonic time.
  - All 3 systems: `technique_compute` row idempotent; `output_hash` stable across runs.
- **Acceptance:** Tests pass in CI; Hypothesis reports no failures; golden suite tolerance honored.
- **Effort:** 2.5 days
- **Depends on:** T-E1b.3, T-E1b.4, T-E1b.5, T-E1b.6, F17

### T-E1b.8: REST endpoint extension + controller wiring
- **Definition:** Extend `GET /api/v1/dasha/{chart_id}` to accept `?system ∈ {chara, narayana, kalachakra}` and the advanced override params (`direction`, `starting_rasi`). Controller dispatches to correct engine.
- **Acceptance:** Curl tests for all 3 systems + 2 override params return valid responses; 4xx for invalid combos (e.g., `direction=savya` + `starting_rasi=karka` + override fails strength ranking → warn but accept).
- **Effort:** 1 day
- **Depends on:** T-E1b.3, T-E1b.4, T-E1b.5

### T-E1b.9: AI tool-use extension (F10)
- **Definition:** Update `get_current_dasa` tool signature to include new systems. Update prompt docs to describe sign-based vs paryaya-based `lord` semantics.
- **Acceptance:** Tool schema validates; integration test invoking chat tool with `system='kalachakra'` returns correct period with citation.
- **Effort:** 0.5 day
- **Depends on:** T-E1b.8

### T-E1b.10: F9 `chart_reading_view.current_dasas` extension
- **Definition:** Update the worker that populates `chart_reading_view.current_dasas` JSONB to include `chara`, `narayana`, `kalachakra` alongside Vimshottari/Yogini/Ashtottari. Shape: `{"<system>": {"current_md": {...}, "current_ad": {...}, "current_pd": {...}}}`.
- **Acceptance:** After compute, `SELECT current_dasas FROM chart_reading_view WHERE chart_id=?` returns all 6 systems for charts that have them all computed; missing systems are absent (not null).
- **Effort:** 1 day
- **Depends on:** T-E1b.3, T-E1b.4, T-E1b.5, F9

### T-E1b.11: Integration test (full path)
- **Definition:** Test creates chart, triggers compute for all 3 systems, verifies rule+compute+aggregation rows in DB, queries via REST, verifies F9 view populated, asserts AI tool returns correct period for each system.
- **Acceptance:** Full round-trip passes in CI.
- **Effort:** 1 day
- **Depends on:** T-E1b.7, T-E1b.8, T-E1b.9, T-E1b.10

### T-E1b.12: Documentation + CLAUDE.md
- **Definition:** Add Chara/Narayana/Kalachakra overview to user-facing docs. CLAUDE.md updated: "Josi supports six dasa systems: Vimshottari, Yogini, Ashtottari, Chara, Narayana, Kalachakra. Sign-based and paryaya-based systems encode `lord` as rasi name; `details.system_kind` disambiguates."
- **Acceptance:** Docs merged; classical-advisor review recorded on paryaya tables.
- **Effort:** 0.5 day
- **Depends on:** T-E1b.11

## 8. Unit Tests

### 8.1 jaimini_common — helpers

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_inclusive_count_forward_same_sign` | from=aries, to=aries, dir=savya | 1 | Count=1 means same sign |
| `test_inclusive_count_forward_adjacent` | from=aries, to=taurus, savya | 2 | Aries→Taurus inclusive-both-ends |
| `test_inclusive_count_forward_full_cycle` | from=aries, to=pisces, savya | 12 | Full zodiacal distance |
| `test_inclusive_count_reverse_adjacent` | from=taurus, to=aries, apasavya | 2 | Reverse direction |
| `test_inclusive_count_reverse_wrap` | from=aries, to=taurus, apasavya | 12 | Aries→Taurus reverse = 11 signs back |
| `test_atmakaraka_ranking_excludes_rahu_default` | chart with 7 grahas + Rahu | top = highest-lon of 7 non-Rahu | Parashari school default |
| `test_atmakaraka_includes_rahu_alternate_school` | same chart + `include_rahu=True` | Rahu compared via 30°−lon trick | Jaimini-with-Rahu alternate |
| `test_rank_rasi_strength_more_planets_wins` | A has 3 planets, B has 2 | A > B | Criterion 1 |
| `test_rank_rasi_strength_tiebreak_by_lord_ak_proximity` | equal planet counts; A's lord closer to AK | A > B | Criterion 2 |
| `test_rank_rasi_strength_deep_tie_lexicographic_fallback` | 5-way tie through classical rules | lexicographic by rasi-id + WARN log | Determinism |

### 8.2 Chara — starting + direction

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_chara_lagna_aries_no_ak_in_lagna_savya` | Lagna=Aries, AK=Jupiter in Sag | starting=Aries, direction=Savya | Odd Lagna, no exception |
| `test_chara_lagna_taurus_no_ak_in_lagna_apasavya` | Lagna=Taurus, AK=Jupiter in Sag | starting=Taurus, direction=Apasavya | Even Lagna |
| `test_chara_ak_in_lagna_falls_back_to_seventh_parity` | Lagna=Aries (odd), AK in Aries → check 7th=Libra (odd) → Savya | Savya | BPHS 50.6 exception |
| `test_chara_ak_in_lagna_seventh_even_apasavya` | Lagna=Taurus (even), AK in Taurus → 7th=Scorpio (even) → Apasavya | Apasavya | Exception branch |
| `test_chara_direction_consistency_for_1000_charts` | 1000 random charts | direction is deterministic; matches expected parity rule | Hypothesis invariant |

### 8.3 Chara — period formula

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_chara_period_count_5_yields_7_years` | rasi=Aries, lord=Mars in Leo (count=5) | 7 years | Normal case |
| `test_chara_period_count_1_exception_yields_12_years` | rasi=Taurus, lord=Venus in Taurus (count=1) | 12 years | BPHS 50.8 exception |
| `test_chara_period_count_7_yields_5_years` | rasi=Gemini, lord=Mercury in Sag (count=7) | 5 years | Normal |
| `test_chara_period_count_11_yields_1_year` | rasi=Cancer, lord=Moon in Taurus (count=11) | 1 year | Edge near minimum |
| `test_chara_period_count_12_yields_0_years_forbidden` | rasi=R, lord opposite R (count=12) | 0 years triggers error OR floor-to-1 per convention | Edge case; Rangacharya §4.13 says "0 years" is never emitted; treat as 1 year |
| `test_chara_period_invariant_sum_115_145` | 1000 random charts | sum of 12 periods ∈ [115, 145] | Empirical range |

### 8.4 Chara — hierarchy + arithmetic

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_chara_antardasha_sum_eq_parent_md` | any MD | sum of 12 AD durations = MD duration | Subdivision invariant |
| `test_chara_pratyantar_sum_eq_parent_ad` | any AD | sum of 12 PD durations = AD duration | Recursive invariant |
| `test_chara_no_gap_no_overlap` | 10 charts × 3 levels | end[i] == start[i+1] ± 1 µs | Temporal consistency |
| `test_chara_direction_consistent_through_levels` | savya MD → savya AD → savya PD | all levels same direction | Classical rule |

### 8.5 Narayana — starting + strength

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_narayana_lagna_stronger_becomes_start` | Lagna has 3 planets, 7th has 1 | starting = Lagna | Criterion 1 |
| `test_narayana_seventh_stronger_becomes_start` | 7th has 4 planets, Lagna has 2 | starting = 7th | Criterion 1 |
| `test_narayana_tiebreak_by_lord_ak_proximity` | equal planets; Lagna's lord 2 signs from AK, 7th's lord 5 | starting = Lagna | Criterion 2 |
| `test_narayana_direction_parity_of_starting` | starting = Gemini (odd) | Savya | Criterion |
| `test_narayana_direction_apasavya_if_even_start` | starting = Scorpio (even) | Apasavya | Criterion |

### 8.6 Narayana — period formula (count in direction)

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_narayana_savya_count_forward` | rasi=Aries, lord in Leo, savya | count=5, period=7 | Forward count |
| `test_narayana_apasavya_count_reverse` | rasi=Taurus, lord in Leo, apasavya | count=Taurus→Leo reverse=10, period=2 | Reverse count |
| `test_narayana_apasavya_count_one_exception` | lord in same rasi, apasavya | period=12 | Exception holds in either direction |
| `test_narayana_period_differs_from_chara_same_chart` | same chart | periods differ for half the rasis | Distinguishes Narayana from Chara |

### 8.7 Narayana — variants

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_narayana_bphs_variant_lagna_or_seventh` | default rule_id | uses `stronger_of_lagna_or_seventh` | Default |
| `test_narayana_karakamsa_variant_starts_karakamsa` | alternate rule_id | uses Karakamsa Lagna | Alternate school |
| `test_narayana_variant_selected_by_astrologer_preference` | pref.source_weights = {"jaimini_sutras": 1.0} | aggregation picks karakamsa variant | Astrologer config |

### 8.8 Kalachakra — paryaya resolution

| Test name | Input (nakshatra, pada) | Expected (paryaya, starting_rasi) | Rationale |
|---|---|---|---|
| `test_kalachakra_ashwini_pada_1` | (1, 1) | (savya_paryaya_1, mesha) | BPHS 53.7 pada 1 |
| `test_kalachakra_ashwini_pada_2` | (1, 2) | (savya_paryaya_1, vrishabha) | BPHS 53.7 pada 2 |
| `test_kalachakra_bharani_pada_1` | (2, 1) | (apasavya_paryaya_1, karka) | BPHS 53.8 |
| `test_kalachakra_krittika_pada_1` | (3, 1) | (savya_paryaya_2, simha) | BPHS 53.9 |
| `test_kalachakra_rohini_pada_1` | (4, 1) | (apasavya_paryaya_2, vrischika) | BPHS 53.10 |
| `test_kalachakra_all_16_paryaya_pada_combos` | all (naksh%4, pada) | matches paryaya_tables | Table integrity |
| `test_kalachakra_revati_pada_4_wraps` | (27, 4) | savya_paryaya_2, karka | End-of-zodiac boundary |

### 8.9 Kalachakra — rasi duration lookup

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_kalachakra_mesha_7` | rasi=mesha | 7 years | BPHS 53.11 |
| `test_kalachakra_vrishabha_16` | rasi=vrishabha | 16 | BPHS 53.11 |
| `test_kalachakra_karka_21` | rasi=karka | 21 | BPHS 53.11 |
| `test_kalachakra_sum_of_all_12_eq_118` | all rasis | 118 | Standard total |

### 8.10 Kalachakra — balance + hierarchy

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_kalachakra_balance_at_pada_start` | moon at pada boundary | balance = first_rasi_years | Full period |
| `test_kalachakra_balance_mid_pada` | moon at 50% of pada | balance = first_rasi_years × 0.5 | Proportional |
| `test_kalachakra_9_md_sum_eq_paryaya_total` | any chart | sum of 9 MDs = paryaya_total (83/86/91/100/...) | Subdivision |
| `test_kalachakra_antardasha_sum_eq_parent` | any MD | sum of 9 ADs = MD duration | Subdivision |
| `test_kalachakra_pratyantar_sum_eq_parent` | any AD | sum of 9 PDs = AD duration | Recursive |
| `test_kalachakra_9_not_12_md_count` | any chart | length of MD list = 9 | Paryaya uses 9 of 12 rasis |

### 8.11 Rule registry integration

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_e1b_rules_loaded_from_yaml` | F6 loader | 4 new rows in `classical_rule` | Wiring |
| `test_e1b_content_hash_stable` | 3 reloads | identical hashes | Determinism |
| `test_e1b_rule_yaml_cosmetic_edit_no_hash_change` | edit `notes` | same hash | F6 contract |
| `test_e1b_compute_references_rule_version` | Inspect compute row | rule_version='1.0.0' | Version-lock |
| `test_e1b_compute_row_idempotent` | 2 computes | 1 row | ON CONFLICT DO NOTHING |

### 8.12 Golden suite (Jagannatha Hora cross-verified)

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_golden_chart_01_chara_md_boundaries` | chart_01 fixture | 12 MD boundaries match JH ±1 day | Correctness |
| `test_golden_chart_01_chara_ad_boundaries` | chart_01 fixture | first MD's 12 AD boundaries match JH ±1 day | Correctness |
| `test_golden_chart_01_narayana_md` | chart_01 | 12 MD boundaries match JH ±1 day | Correctness |
| `test_golden_chart_01_kalachakra_md` | chart_01 | 9 MD boundaries match JH ±1 day; starting rasi + paryaya matches | Correctness |
| `test_golden_chart_02_through_05_all_systems` | charts 02–05 × 3 systems | all match JH ±1 day | Systemic correctness |
| `test_golden_jh_maitreya_known_divergence_recorded` | chart with known edge | both values recorded; test XFAIL with message | Documented divergence |

### 8.13 Property tests (Hypothesis, F17, ≥1000 examples each)

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_chara_hierarchy_sum_invariant` | random chart | sum of 12 MDs ∈ [115, 145]; AD sums = parent; PD sums = parent | Arithmetic |
| `test_chara_monotonic_time` | random | end[i] ≤ start[i+1] | Temporal |
| `test_chara_direction_rule_invariant` | random | computed direction matches parity rule including AK-in-Lagna fallback | Classical rule |
| `test_narayana_strength_deterministic` | same chart | ranking same on every call | Determinism |
| `test_narayana_period_differs_from_chara_half_time` | random | at least 50% of rasi periods differ between Chara and Narayana | Distinguishing invariant |
| `test_kalachakra_paryaya_assignment_by_nakshatra_mod_4` | all 27 × 4 pada combos | paryaya = assignment_table[(nakshatra-1) % 4] | Table integrity |
| `test_kalachakra_balance_le_first_rasi` | random | balance ≤ first_rasi_years | Invariant |
| `test_kalachakra_9_md_count` | random | exactly 9 mahadashas | Paryaya structure |
| `test_recompute_deterministic_all_systems` | same inputs 2 times | same output_hash | Provenance |
| `test_e1b_no_gaps_no_overlaps` | all 3 systems, random | end[i]==start[i+1] at every level | Consistency |

## 9. EPIC-Level Acceptance Criteria

- [ ] Chara, Narayana, Kalachakra YAML rules + Narayana-Karakamsa variant loaded into `classical_rule` via F6 loader
- [ ] `CharaDasaEngine`, `NarayanaDasaEngine`, `KalachakraDasaEngine` implement `ClassicalEngine` Protocol and pass compliance test
- [ ] `jaimini_common` helpers (inclusive count, AK resolution, rasi strength ranking) unit-tested
- [ ] REST endpoint `GET /api/v1/dasha/{chart_id}?system={chara|narayana|kalachakra}` returns all three systems with citations
- [ ] AI tool `get_current_dasa(system=...)` works end-to-end for all three new systems
- [ ] 15 golden fixtures (5 charts × 3 systems) all pass ±1 day vs JH 7.x
- [ ] Property tests pass with ≥1000 Hypothesis examples per system
- [ ] Unit test coverage ≥ 90% for all new code
- [ ] `chart_reading_view.current_dasas` JSONB populated for all 6 systems (Vim + Yog + Asht + Chara + Nar + Kala)
- [ ] Documentation: CLAUDE.md + user docs updated; classical-advisor sign-off recorded on Kalachakra paryaya tables
- [ ] Performance: compute per chart per system P99 < 80 ms (Kalachakra slowest due to paryaya resolution; Chara fastest)
- [ ] Golden chart suite green for technique_family=dasa (overall E1a + E1b)
- [ ] Integration test hits full path: YAML → classical_rule → compute → aggregation → chart_reading_view → REST → AI tool

## 10. Rollout Plan

- **Feature flag:** `ENABLE_DASA_CHARA`, `ENABLE_DASA_NARAYANA`, `ENABLE_DASA_KALACHAKRA` — all default `false` on P2 deploy, flipped `true` after golden-suite green for 7 consecutive days in staging.
- **Shadow compute:** for 7 days, engines write `technique_compute` rows in staging only; production endpoints gate on flag. Spot-check 20 charts' output against JH 7.x before promoting.
- **Backfill strategy:** opportunistic — compute on next chart view. Background job `compute_missing_dasas_v2` seeds pre-existing charts over 4 weeks (larger cycle than E1a given Kalachakra cost).
- **Rollback plan:** flip flag off → endpoint returns 404 for new systems; Vimshottari/Yogini/Ashtottari unaffected. `effective_to = now()` on new rules soft-deprecates; existing compute rows retained for audit.
- **Astrologer preview:** 2-week early-access tier before general rollout. Astrologers file override-rate signals that feed into E14a experimentation.

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Kalachakra paryaya tables transcription error (16 × 9 = 144 rasi entries) | **High** | **Critical** (wrong dasas for ~25% of charts) | Cell-by-cell classical-advisor review in T-E1b.1; golden fixtures cross-verified against JH; property test asserts paryaya_assignment matches nakshatra mod 4 rule |
| Narayana strength-ranking deep-tie lexicographic fallback differs from JH tiebreak | Medium | Medium | Log WARN every time lexicographic fallback triggers; accept classical-advisor convention in v1; track diverges via C5 differential testing |
| Chara AK-in-Lagna 7th-parity exception encoded incorrectly | Medium | High | Dedicated unit test per parity × AK-in-Lagna combo (4 cases); property test 1000 charts matches rule table |
| Float precision drift over 3 levels × 9 rasis × 9 AD × 9 PD (Kalachakra) | Medium | Medium | `Decimal` internally with 28-digit precision; datetime conversion only on emission; property test asserts boundary continuity to microsecond |
| Rasi lord lookup conflicts across Ketu-co-lord variants | Low | Low | Default excludes Ketu co-lordship; alternate variant rule shipped as lineage option in E3 (not E1b) |
| BPHS vs Jaimini Sutras vs Rangacharya disagree on edge cases | Medium | Low | Ship default (BPHS) + alternate variants as separate rules; astrologer preference selects; per-source compute preserves all |
| "12 − count" formula yielding 0 years at count=12 | Medium | Medium | Rangacharya §4.13 guidance: floor to 1 year; logged when triggered; documented in classical_names.notes |
| JH 7.x closed-source → cross-verification is manual | Certain | Medium | T-E1b.6 allocates 5 days for verification; 5-chart minimum (vs 10 in E1a); C5 differential testing at P3 catches drift |
| Atmakaraka computation depends on Rahu-inclusion convention; drift breaks Chara direction | Medium | High | Explicit `include_rahu` parameter in `resolve_atmakaraka`; default False (Parashari); dedicated test for both modes |
| Kalachakra Mandook leaps never shipped; practitioners demand it | Low | Medium | Explicit out-of-scope in §2.2; `dasa.kalachakra.mandook.bphs` future rule stub mentioned in docs |
| Narayana-Karakamsa variant rarely selected → insufficient override signal for E14a | Medium | Low | Expected; rely on astrologer Pro-mode explicit preference rather than auto-experimentation |

## 12. References

- Master spec: [`docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`](../../../superpowers/specs/2026-04-19-classical-techniques-expansion-design.md)
- F1 dimensions: [`../P0/F1-star-schema-dimensions.md`](../P0/F1-star-schema-dimensions.md)
- F2 fact tables: [`../P0/F2-fact-tables.md`](../P0/F2-fact-tables.md)
- F6 rule DSL: [`../P0/F6-rule-dsl-yaml-loader.md`](../P0/F6-rule-dsl-yaml-loader.md)
- F7 output shapes: [`../P0/F7-output-shape-system.md`](../P0/F7-output-shape-system.md)
- F8 engine + strategy protocol: [`../P0/F8-technique-result-aggregation-protocol.md`](../P0/F8-technique-result-aggregation-protocol.md)
- F13 content-hash provenance: [`../P0/F13-content-hash-provenance.md`](../P0/F13-content-hash-provenance.md)
- F16 golden chart suite: [`../P0/F16-golden-chart-suite.md`](../P0/F16-golden-chart-suite.md)
- F17 property-based test harness: [`../P0/F17-property-based-test-harness.md`](../P0/F17-property-based-test-harness.md)
- E1a predecessor PRD: [`../P1/E1a-multi-dasa-v1.md`](../P1/E1a-multi-dasa-v1.md)
- E3 downstream (consumes Chara periods + rashi drishti): [`./E3-jaimini-system.md`](./E3-jaimini-system.md)
- Classical primary sources:
  - **Brihat Parashara Hora Shastra** Ch. 50 (Chara Dasha), Ch. 51 (Narayana references), Ch. 53 (Kalachakra Dasha)
  - **Jaimini Upadesha Sutras** Book 1, Chapter 4 (dasa-adhyaya: verses 1–75)
  - **Jataka Parijata** Ch. 18 (dasa comparisons), Ch. 19 (Kalachakra elaboration)
  - **Uttara Kalamrita** by Kalidasa (Kalachakra supplement)
  - **Jaimini Sutras** commentary by Irangati Rangacharya (Sagar Publications) §4.1–§4.75
- Reference implementations: Jagannatha Hora 7.x (VedicAstrology.com, free download); Maitreya9 (open-source, maitreya.info)
