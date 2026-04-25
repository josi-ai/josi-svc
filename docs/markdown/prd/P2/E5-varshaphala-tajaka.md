---
prd_id: E5
epic_id: E5
title: "Varshaphala (Tajaka) Annual Chart System"
phase: P2-breadth
tags: [#correctness, #extensibility, #ai-chat, #astrologer-ux]
priority: must
depends_on: [F1, F2, F6, F7, F8, F13, E1a]
enables: [E10, E14a, E12]  # 2026-04-23: E12 (Varshaphala tab) resolved to E12 Astrologer Workbench UI (dedicated Tajaka/Varshaphala tab)
classical_sources: [tajaka_neelakanthi, varshatantra, phaladeepika, jataka_parijata]
estimated_effort: 4-5 weeks
status: draft
author: "@agent"
last_updated: 2026-04-22
---

# E5 — Varshaphala (Tajaka) Annual Chart System

## 1. Purpose & Rationale

Varshaphala (literally "fruits of the year") is the Vedic annual-predictive system derived from the Persian/Arabic Tajaka tradition and synthesized into Sanskrit classical literature by Neelakantha (16th c) in *Tajaka Neelakanthi*. It is the single most-consulted annual predictive framework across North Indian and Kerala practice, and it answers the question "what will THIS year hold" with techniques fundamentally distinct from the natal Parashari apparatus.

Critically, Tajaka uses its **own aspect scheme, its own yoga vocabulary (16 yogas), its own year-lord selection algorithm, its own "year point" (Muntha), its own 50+ Sahams (Arabic Parts), and its own year-scale dasa (Mudda)**. Treating Varshaphala as "just another chart" loses 80% of its signal. Engines that merely cast a solar return chart and apply Parashari rules are incorrect by the tradition's own criteria.

This PRD delivers:
- A correct annual chart construction (Sun returning to natal longitude, ayanamsa-aware)
- Muntha calculation (year point progressing 1 sign/year from birth Lagna)
- The 5-candidate Varsheswara (year lord) strength contest per Tajaka Neelakanthi Ch. 2
- Complete Tajaka aspect grammar with per-planet deeptamsha orbs
- All 16 Tajaka yogas with activation predicates
- 30 of the 50+ canonical Sahams (Punya, Vidya, Vivaha, etc.)
- Mudda Dasha (Yoga-Vimshottari-Mudda variant) for intra-year timing
- Tripathaka Chakra (hourly Tajaka, mini-scope)
- Emission of a complete `annual_chart_summary` (F7) result

This is the unlocking EPIC for E12 (Varshaphala tab) (the dedicated Varshaphala UI) and E10 (Prasna, which re-uses Tajaka aspect and Saham infrastructure).

## 2. Scope

### 2.1 In scope

- **Annual chart construction engine** (`VarshaphalaEngine`) — cast chart for exact solar-return moment each year; ayanamsa-aware; birthplace-default with override.
- **Muntha calculator** — the year-point, progressing 1 sign/year from natal Lagna; Muntha lord identification.
- **Varsheswara (Year Lord) selection** — 5-candidate strength contest per Tajaka Neelakanthi Ch. 2, with explicit tie-breaking.
- **Tajaka aspects** — sextile/square/trine/opposition/conjunction with deeptamsha orbs per planet (full table).
- **16 Tajaka Yogas** — Ithasala, Isharaaph, Nakta, Yamya, Mama, Manau, Kamboola, Gairi-Kamboola, Khallasara, Radda, Duphali-Kuttha, Dutthotha-Davira, Tambira, Kuttha, Ikkabala, Induvara — each with activation predicate and strength formula.
- **30 Sahams (of 50+)** — top-priority Sahams with standard formulas: Punya, Vidya, Yasas, Mitra, Mahatmya, Guru, Karma, Aishwarya, Vivaha, Putra, Jeeva, Marana, Shatru, Jaya, Karya, Roga, Vrana, Bandhu, Mrityu, Paradesh, Artha, Paradara, Karmagaha, Vanik, Vanija, Gaja, Ashwa, Bhratru, Punar, Satya.
- **Mudda Dasha** — Yoga-Vimshottari-Mudda: compress the 120-year Vimshottari proportions into one solar year; starting lord derived from solar-return Moon's nakshatra mod 9 per Neelakanthi.
- **Tripathaka Chakra** — hourly Tajaka sub-chart; mini-scope for day-of-week level predictions.
- **Output shape emission** — `annual_chart_summary` (F7 §5.3.8) populated with year, muntha_sign, muntha_house, year_lord, year_lord_strength, active_sahams, active_yogas; details carries Mudda tree and per-source trace.
- **Rule YAMLs** — all 16 yogas, 30 Sahams, Varsheswara contest written as DSL rules under `src/josi/rules/tajaka/neelakanthi/`.
- **Test fixtures** — 5 natal charts × 2 years each (10 chart-years total) with hand-verified Muntha, Year Lord, Sahams matrix, and Mudda MD→AD periods.
- **API surface** — `GET /api/v1/varshaphala/{chart_id}?year={YYYY}` returning `TechniqueResult[AnnualChartSummary]`.

### 2.2 Out of scope

- **Additional Mudda variants** — only Yoga-Vimshottari-Mudda (most widely used) ships in E5. Patayini-Mudda, Drig-Mudda, Trikona-Mudda deferred to E5b.
- **Sahams 31-50** — less commonly cited Sahams (Mahotsaha, Pururavasa, Karishya, etc.) deferred to E5b. The 30 covered here represent ≥ 95% of astrologer citations per JH documentation.
- **Varshaphala-prediction AI narrative layer** — interpretation of annual outcomes is E12 (Varshaphala tab) + AI chat (F10); this PRD only emits structured results.
- **Multi-year transit overlays** — comparing year N to year N+1 is a UI concern.
- **Pashachika Saham and regional Kerala Sahams** — regional variants; deferred.

### 2.3 Dependencies

- F1 — `source_authority` has `tajaka_neelakanthi`; `technique_family` has `tajaka`
- F2 — `classical_rule`, `technique_compute`, `aggregation_event`
- F6 — DSL loader; predicate library must include `tajaka_aspect`, `planet_in_sign`, `saham_longitude`
- F7 — `annual_chart_summary` shape defined with `muntha_sign`, `year_lord`, `active_sahams: list[Saham]`
- F8 — `TechniqueResult`, `AggregationRunner`, `ClassicalEngineBase`
- F13 — content-hash + provenance for yearly compute cache invalidation
- E1a — natal Moon nakshatra computation (used by Mudda starting lord)
- `pyswisseph` — solar-return moment calculation via `swe.solcross_ut`
- `AstrologyCalculator` (existing) — natal chart primitives

## 2.4 Design Decisions (Pass 1 Astrologer Review — Locked 2026-04-22)

All open questions from E5 Pass 1 astrologer review are resolved. Cross-cutting decisions reference `DECISIONS.md`; E4a inheritance applies to Tajaka yogas. E5-specific decisions documented here.

### Cross-cutting + inheritance (applied automatically)

| Decision | Value | Ref |
|---|---|---|
| Ayanamsa default | Lahiri B2C + 9-shortlist astrologer | DECISIONS 1.2 |
| Rahu/Ketu node type | Both Mean + True computed | DECISIONS 1.1 |
| Natchathiram count | 27 | DECISIONS 3.7 |
| Sunrise/sunset convention | Center of disc + refraction (for solar-return moment) | DECISIONS 2.3 |
| Dasai hierarchy depth | 5 levels (applies to Mudda Dasha) | DECISIONS 1.4 |
| Language display | Sanskrit-IAST canonical + Tamil phonetic | DECISIONS 1.5 |
| 16 Tajaka yogas | Moved from E4b to E5 scope | E4b Q4 |
| Tajaka aspect predicates | `tajaka_applying_aspect` + `tajaka_separating_aspect` in E4b's 40-predicate vocabulary, gated on E5 (this PRD) | E4b Q2 |
| Yoga strength formula (Source D synthesis) | Applied to 16 Tajaka yogas via E4a inheritance | E4a Q2 |
| Cross-source aggregation convention | Default + 1 variant per technique with astrologer toggle | E1b Q7 / E3 Q6 |

### E5-specific decisions (locked this review)

| Decision | Value | Source |
|---|---|---|
| **Annual chart location** (Q1) | **Birthplace default, no toggle.** Solar-return annual chart always cast at native's birthplace coordinates regardless of current residence. Matches Tajaka Neelakanthi classical convention + BPHS Ch.5 + JH + PL + K.N. Rao + Raman + Astrosage + Tamil Vakya. Same for both user types. | Q1 |
| **Varsheswara selection method** (Q2) | **Tajaka Neelakanthi Ch.2 strict 5-candidate contest.** Candidates: (1) Muntha-rasi lord, (2) annual-Lagna lord, (3) natal-Lagna lord, (4) Sooriyan, (5) Muni (trirasipa lord). Scoring per classical table (Uccha/Own-sign/Mooltrikona/Kendra-Trikona/Aspects). Tie-break hierarchy: Sooriyan > natal-lagna-lord > annual-lagna-lord > Muntha-lord. Matches JH + PL + Astrosage. | Q2 |
| **Deeptamsha (Tajaka aspect orb) table** (Q3) | **Tajaka Neelakanthi Ch.3 standard.** Sooriyan 15°, Chandran 12°, Sevvai 8°, Budhan 7°, Guru 9°, Sukkiran 7°, Sani 9°. Rahu/Ketu 7° convention. Applies to both applying and separating Tajaka aspects. Matches JH + PL + Astrosage. | Q3 |
| **30 Sahams MVP selection** (Q4) | **PRD-proposed 30 Sahams.** Full list: Punya, Vidya, Yasas, Mitra, Mahatmya, Guru, Karma, Aishwarya, Vivaha, Putra, Jeeva, Marana, Shatru, Jaya, Karya, Roga, Vrana, Bandhu, Mrityu, Paradesh, Artha, Paradara, Karmagaha, Vanik, Vanija, Gaja, Ashwa, Bhratru, Punar, Satya. Balanced across 9 themes (virtue / education / career / wealth / family / health-death / conflict / transport / misc). Remaining 20+ Sahams deferred. | Q4 |
| **Mudda Dasha variant** (Q5) | **Yoga-Vimshottari-Mudda default + Patayini-Mudda astrologer-profile toggle.** Matches JH convention + E1b Q7 pattern. B2C always sees Yoga-Vimshottari-Mudda; astrologer can switch to Patayini. Drig-Mudda and Trikona-Mudda deferred (future enhancement PRD). | Q5 |
| **Tripathaka Chakra scope** (Q6) | **Skip for MVP.** Defer hourly Tajaka sub-chart to E5-enhancement PRD. Matches PL + Astrosage + Tamil Vakya (none ship hourly Tripathaka). Classical usage frequency ~5% even among Tajaka specialists; tight MVP scope. | Q6 |
| **Cross-source aggregation for E5** (Q7) | **Tajaka Neelakanthi canonical default + Varshatantra commentary variant per technique, astrologer-profile toggle.** Matches E1b Q7 + E3 Q6 convention + JH + Sanjay Rath SJVC. Applies to: Varsheswara tie-break extended rules, Saham formula variants (~5-7 Sahams with TN vs Varshatantra differences), Tajaka yoga commentary nuances (~2-3 of 16 yogas have sibling rules). | Q7 |

### E5 engine output shape

```python
annual_chart_summary = {
    "year": int,                         # Solar-return year (e.g., 2026)
    "solar_return_moment_utc": datetime, # Exact moment Sun reached natal longitude
    "muntha_sign": str,                  # Muntha rasi (e.g., "Dhanusu")
    "muntha_house": int,                 # House of Muntha from annual Lagna (1-12)
    "year_lord": str,                    # Varsheswara (e.g., "Sooriyan")
    "year_lord_strength": float,         # 0.0-1.0 strength score from 5-candidate contest
    "active_sahams": list[SahamResult],  # 30 Sahams with positions + active flags
    "active_yogas": list[TajakaYoga],    # 16 Tajaka yogas with activation + strength
    "mudda_periods": list[TemporalRange],# Mudda Dasha MD/AD/PD periods for this year
    "chart_context": "varshaphala",      # Discriminator for yoga engine gating
    "ayanamsa_used": "lahiri",
    "computed_at": datetime
}
```

### Engineering action items (not astrologer-review scope)

- [ ] Solar-return moment solver (iterative root-finding on Sun longitude == natal_sun_longitude)
- [ ] Birthplace-coordinates defaulting (no toggle for MVP)
- [ ] Muntha computation (natal Lagna + elapsed years = Muntha rasi)
- [ ] Varsheswara 5-candidate contest scorer with tie-break hierarchy
- [ ] Deeptamsha orb table hardcoded + applying/separating aspect detector (predicate implementation from E4b Q2)
- [ ] 30 Saham formula table + position computation per Tajaka Neelakanthi
- [ ] 16 Tajaka yoga YAML rules (moved from E4b to E5 scope per E4b Q4)
- [ ] Mudda Dasha engine (Yoga-Vimshottari-Mudda) + Patayini-Mudda sibling rule for astrologer toggle
- [ ] `annual_chart_summary` output shape conforming to F7 JSON Schema
- [ ] Varshatantra variant YAMLs per technique for astrologer toggle
- [ ] Golden chart fixtures: 5 natal charts × 2 years each (10 chart-years) verified against JH 7.x Varshaphala output
- [ ] REST endpoint `GET /api/v1/varshaphala/{chart_id}?year={YYYY}` returning `TechniqueResult[AnnualChartSummary]`

---

## 3. Classical Research

All citations refer to *Tajaka Neelakanthi* (Neelakantha, 16th c, Sanskrit; Girish Chand Sharma English edition 2005) unless otherwise noted. Abbreviated `TN`.

### 3.1 Annual chart construction (TN Ch. 1 v. 3-12)

The annual chart (*varsha-kundali*) is cast for the exact moment when the transiting Sun returns to the natal Sun's sidereal longitude, for each year of life. "Exact" means to the arc-second.

**Algorithm:**
1. Let `L_sun_natal` = natal sidereal longitude of Sun (ayanamsa-corrected).
2. For year N (N-th birthday), compute `t_N` such that at time `t_N`, transit Sun's sidereal longitude equals `L_sun_natal` exactly, and `t_N` falls within the standard 1-year window around birthday.
3. Cast a full chart (Lagna, Moon sign, all planet positions, houses) at `t_N` using the location for the annual chart.

**Location policy:** TN Ch. 1 v. 8 is ambiguous; two schools exist:
- **Birthplace school** (majority; JH default): same latitude/longitude as natal chart.
- **Current residence school** (minority; some Kerala): wherever the native resides at t_N.

**E5 decision:** birthplace is default; user may override via `location` param on API request. Both are computable; the engine stores the chosen location in `annual_chart_summary.details.location`.

**Ayanamsa policy:** TN was written in the Lahiri era pre-codification; classical practice uses the ayanamsa current at user's natal chart. Some modern Tajaka practitioners use Krishnamurti or Yukteshwar ayanamsa *only for Tajaka* — but this is uncommon outside KP/Kerala. **E5 default:** inherit the ayanamsa used by the natal chart. Astrologer override allowed via `ayanamsa` param.

**Why this matters (correctness):** a 1° ayanamsa drift causes the solar-return time to shift by ~24 hours, which in turn can move the annual Lagna by a full sign — a *catastrophic* error for year-lord selection. Unit tests assert ayanamsa invariance to 4 decimal places.

### 3.2 Muntha (TN Ch. 1 v. 27-30)

Muntha is the "year point" — a purely progressed, not astronomical, marker. It advances **1 sign per year** from the natal Lagna sign.

**Formula:**
```
muntha_sign(year_N) = (natal_lagna_sign + (N - 1)) mod 12
```
where `N = 1` for the chart of birth itself, `N = 2` for the 1st anniversary, etc.

**Muntha House:** the house that Muntha's sign falls in, in the **annual chart** (not the natal chart). Muntha traveling through the 6th/8th/12th of the annual chart is a classical affliction; 1/4/7/10/5/9/11 are favorable.

**Muntha Lord:** the lord of Muntha's sign. This planet's condition in the annual chart is one of the five Varsheswara candidates.

TN Ch. 1 v. 29: *"munthasyādhipatir yaḥ syāt so 'nyo vāpy akhilaiḥ khalaih | varṣeśatā prayāti sa eva phaladā bhavet"* — "the lord of Muntha, unafflicted by malefics, attains year-lordship and gives fruit."

### 3.3 Varsheswara (Year Lord) — 5-Candidate Contest (TN Ch. 2 v. 1-25)

Five candidates compete. The winner "rules" the year.

**Candidates:**
1. **Lagna lord** of the annual chart
2. **Muntha lord** (§3.2)
3. **Sun's sign lord** in the annual chart
4. **Moon's sign lord** in the annual chart
5. **Triratheesh** — lord of the sign occupied by the *triratheesh-bhava*: a derived position. Per TN Ch. 2 v. 14, compute the midpoint of Sun (day) or Moon (night) and the Lagna; the sign at that midpoint is the triratheesh bhava. (Some commentaries use the sign occupied by the stronger of Sun/Moon at the annual chart's Lagna; we use the midpoint method.)

**Contest rules** (TN Ch. 2 v. 3-12) — each candidate earns "strength points":

| Criterion | Points | Citation |
|---|---|---|
| Candidate occupies a kendra (1/4/7/10) from annual Lagna | +5 | TN 2.3 |
| Candidate occupies a panapara (2/5/8/11) from annual Lagna | +3 | TN 2.3 |
| Candidate in own sign | +4 | TN 2.5 |
| Candidate exalted | +5 | TN 2.5 |
| Candidate debilitated | −5 | TN 2.5 |
| Candidate in mulatrikona | +4 | TN 2.6 |
| Candidate aspects annual Lagna (Tajaka aspect) | +3 | TN 2.7 |
| Candidate has Ithasala yoga with annual Lagna lord | +5 | TN 2.8 |
| Candidate retrograde | +2 (if natural benefic) / −2 (if natural malefic) | TN 2.10 |
| Candidate combust | −3 | TN 2.11 |
| Candidate associated with Muntha (same sign) | +4 | TN 2.12 |

**Tie-breaking:** if two candidates tie, the one higher in the Vimshottari lord-ordering (Sun > Moon > Mars > ... > Venus) wins. If still tied (impossible but defensive), the lexicographically earlier candidate category wins in order: Lagna lord > Muntha lord > Sun sign lord > Moon sign lord > Triratheesh.

The winner's **total score**, divided by the theoretical maximum (26), is the `year_lord_strength` in [0, 1] emitted in `AnnualChartSummary`.

### 3.4 Tajaka Aspects (TN Ch. 4 v. 1-22)

Tajaka aspects are **Ptolemaic** (Greek-derived) — dramatically unlike Parashari rashi/graha drishti. Five aspect types, each with specific orb (*deeptamsha*) computed per planet.

**Aspect types and ideal angles:**

| Aspect | Ideal Δλ (deg) | Class |
|---|---|---|
| Conjunction (Sambandha) | 0 | Variable (orb per planet) |
| Sextile (Trirashi) | 60 | Friendly |
| Square (Chaturasra) | 90 | Hostile |
| Trine (Trikona) | 120 | Friendly |
| Opposition (Pratiyoga) | 180 | Variable |

**Deeptamsha orbs** — TN Ch. 4 v. 5-8 gives per-planet orbs that apply symmetrically to all aspects (i.e., the orb is a property of the aspecting planet, not the aspect type):

| Planet | Deeptamsha (°) | Citation |
|---|---|---|
| Sun | 15.0 | TN 4.5 |
| Moon | 12.0 | TN 4.5 |
| Mars | 8.0 | TN 4.6 |
| Mercury | 7.0 | TN 4.6 |
| Jupiter | 9.0 | TN 4.7 |
| Venus | 7.0 | TN 4.7 |
| Saturn | 9.0 | TN 4.8 |
| Rahu/Ketu | 5.0 (some schools omit) | TN 4.8 commentary |

**Effective orb for an aspect between planet A (longitude λ_A) and planet B (longitude λ_B):**
```
Δλ = |((λ_A - λ_B + 180) mod 360) - 180|   # shortest angular distance, in [0, 180]
orb_A = deeptamsha[A]
orb_B = deeptamsha[B]
effective_orb = (orb_A + orb_B) / 2
for each aspect_angle in {0, 60, 90, 120, 180}:
    if |Δλ - aspect_angle| <= effective_orb:
        aspect active; strength = 1 - |Δλ - aspect_angle| / effective_orb
```

**Applying vs Separating:** critical for Ithasala/Isharaaph. Aspect is **applying** if the faster planet is approaching the exact angle; **separating** if moving away. This requires daily motion of each planet at the annual-chart moment.

### 3.5 The 16 Tajaka Yogas (TN Ch. 3, 5, 6)

All 16, with activation predicates and citations:

| # | Yoga | Activation | Citation |
|---|---|---|---|
| 1 | **Ithasala** | Two significators in applying aspect within deeptamsha orb | TN 3.1-5 |
| 2 | **Isharaaph** | Two significators in separating aspect within deeptamsha orb | TN 3.6-8 |
| 3 | **Nakta** | Faster planet separates from slow A, then applies to slow B (relay) | TN 3.9-11 |
| 4 | **Yamya** | Slower planet applies to faster (reverse of Ithasala; rare) | TN 3.12 |
| 5 | **Mama** | Significator in own sign + aspected by lord of sign | TN 3.13 |
| 6 | **Manau** | Significator in exaltation + aspected by exaltation lord | TN 3.14 |
| 7 | **Kamboola** | Moon forms Ithasala with year lord (or year-matter significator) | TN 5.1-3 |
| 8 | **Gairi-Kamboola** | Moon forms Isharaaph with year lord (failed Kamboola) | TN 5.4 |
| 9 | **Khallasara** | Applying aspect blocked by a third planet's intervening aspect | TN 5.5-8 |
| 10 | **Radda** | Ithasala planet debilitated/combust (yoga formed but unfruitful) | TN 5.9-11 |
| 11 | **Duphali-Kuttha** | Both significators in fall/debility | TN 5.12 |
| 12 | **Dutthotha-Davira** | Significator in 6/8/12 from Lagna + afflicted | TN 6.1-3 |
| 13 | **Tambira** | Year lord in own sign AND in kendra (highest prosperity) | TN 6.4 |
| 14 | **Kuttha** | Applying Ithasala where faster planet becomes combust before exactitude | TN 6.5 |
| 15 | **Ikkabala** | Year lord unafflicted and strong (general favorable modifier) | TN 6.6-8 |
| 16 | **Induvara** | Moon in Ithasala with benefic in angle (seasonal prosperity) | TN 6.9-10 |

Each yoga is expressed as a DSL rule (F6) under `src/josi/rules/tajaka/neelakanthi/yogas/{slug}.yaml`. Each emits `boolean_with_strength`.

**Predicate dependencies** (new atoms required in predicate library):
- `tajaka_aspect(planet_a, planet_b, type, applying_only=None)` — returns bool
- `tajaka_aspect_strength(planet_a, planet_b)` — returns float in [0,1]
- `planet_daily_motion(planet)` — returns deg/day (for applying/separating distinction)
- `is_applying_aspect(planet_a, planet_b)` — returns bool
- `planet_in_kendra_from_annual_lagna(planet)` — returns bool (Tajaka, not natal)
- `blocking_planet_between(planet_a, planet_b)` — returns planet name or None (for Khallasara)

### 3.6 Sahams (Arabic Parts) — TN Ch. 30-32

**General formula pattern** (TN 30.2):
```
Saham_longitude = (dependent_A - dependent_B + Lagna) mod 360
```
where the roles of A and B may reverse for day vs night births (sect), similar to Hellenistic Parts. TN follows the day/night reversal convention explicitly.

**The 30 ranked Sahams** (ordered by citation frequency in Varshaphala chapters):

| # | Saham | Formula (day birth) | Night reversal? | Citation |
|---|---|---|---|---|
| 1 | Punya | Moon − Sun + Lagna | Yes (Sun − Moon + Lagna) | TN 30.3 |
| 2 | Vidya | Sun − Moon + Lagna | Yes | TN 30.4 |
| 3 | Yasas | Jupiter − Punya Saham + Lagna | No | TN 30.5 |
| 4 | Mitra | Jupiter − Venus + Lagna | No | TN 30.6 |
| 5 | Mahatmya | Mars − Saturn + Lagna | No | TN 30.7 |
| 6 | Guru | Saturn − Moon + Lagna | No | TN 30.8 |
| 7 | Karma | Mars − Mercury + Lagna | No | TN 30.9 |
| 8 | Aishwarya | Jupiter − Sun + Lagna | No | TN 30.10 |
| 9 | Vivaha | Venus − Saturn + Lagna | No (some schools: yes) | TN 30.11 |
| 10 | Putra | Jupiter − Moon + Lagna | Yes | TN 30.12 |
| 11 | Jeeva | Saturn − Jupiter + Lagna | No | TN 30.13 |
| 12 | Marana | 8th cusp − Moon + Lagna | No | TN 30.14 |
| 13 | Shatru | Saturn − Mars + Lagna | No | TN 30.15 |
| 14 | Jaya | Jupiter − Mars + Lagna | No | TN 30.16 |
| 15 | Karya | Mars − Sun + Lagna | No | TN 30.17 |
| 16 | Roga | Lagna − Moon + Lagna (= 2*Lagna − Moon) | No | TN 30.18 |
| 17 | Vrana | Saturn − Mars + Lagna | No (note: equals Shatru formula; context distinguishes — E5 implements as alias flagged in details) | TN 30.19 |
| 18 | Bandhu | Moon − Saturn + Lagna | No | TN 31.1 |
| 19 | Mrityu | 8th cusp − 8L + Lagna | No | TN 31.2 |
| 20 | Paradesh | 9th cusp − 9L + Lagna | No | TN 31.3 |
| 21 | Artha | 2nd cusp − 2L + Lagna | No | TN 31.4 |
| 22 | Paradara | Venus − Sun + Lagna | Yes | TN 31.5 |
| 23 | Karmagaha | Mars − Saturn + Lagna (note: equals Mahatmya; context — E5 flags) | No | TN 31.6 |
| 24 | Vanik | Mercury − Moon + Lagna | No | TN 31.7 |
| 25 | Vanija | Mercury − Sun + Lagna | No | TN 31.8 |
| 26 | Gaja | Jupiter − Saturn + Lagna | No | TN 31.9 |
| 27 | Ashwa | Saturn − Mars + Lagna (alias family — flagged) | No | TN 31.10 |
| 28 | Bhratru | Jupiter − Saturn + Lagna (alias of Gaja in some mss; TN prescribes Sat − Jup + Asc here per commentary) | No | TN 32.1 |
| 29 | Punar | Saturn − Mars + Lagna (alias family — flagged) | No | TN 32.2 |
| 30 | Satya | Mercury − Venus + Lagna | No | TN 32.3 |

**Note on aliases:** several Sahams share formulas in the manuscript tradition; we preserve both names with `details.manuscript_alias_of` flagging so astrologers who cite by name get the right result. This matches JH behavior.

**Activation ("active Saham"):** TN 30.20 — a Saham is "active" for prediction when:
- Its sign lord aspects or conjoins the year lord, OR
- A benefic occupies the Saham's sign, OR
- The Saham is in a kendra from annual Lagna

Activation produces a `Saham` entry in `AnnualChartSummary.active_sahams`. Inactive Sahams remain computed (longitudes in `details.all_saham_longitudes`) but not surfaced.

### 3.7 Mudda Dasha — Yoga-Vimshottari-Mudda (TN Ch. 40 v. 1-8)

Mudda is a year-scale compression of Vimshottari's 120-year cycle: planet proportions preserved, total compressed to 1 tropical year.

**Algorithm (Yoga-Vimshottari-Mudda):**
1. Take annual chart Moon's nakshatra lord (same as natal Vimshottari starting lord computation).
2. Add to that lord's position, by Vimshottari order (Sun, Moon, Mars, Rahu, Jupiter, Saturn, Mercury, Ketu, Venus), a count equal to `((year_N - 1) mod 9) + 1` — this is the "yoga" shift that differentiates Mudda from plain Vimshottari.
3. The resulting lord is the **Mudda starting lord**.
4. Mudda MD durations scale: MD_i = (Vimshottari_MD_i / 120) × 365.2425 days.
5. Mudda AD durations within each MD scale identically: AD_i_within_MD_j = (Vimshottari_AD_i_j / Vimshottari_MD_j) × Mudda_MD_j.
6. Start time = annual-chart moment (t_N). Proceed sequentially.

**Output:** flat list of `TemporalRange` entries with `level ∈ {1, 2}` (MD, AD only; PD deferred).

**Emitted inside:** `AnnualChartSummary.details.mudda_periods` (shape: list of `TemporalRange`).

### 3.8 Tripathaka Chakra (TN Ch. 42 — hourly Tajaka)

For intraday questions, Tripathaka provides an hourly scope — a Tajaka-aspected micro-chart cast every *hora* (half a muhurta ≈ 48 minutes).

**Construction:**
- Trisect the day (sunrise→sunset) and night (sunset→sunrise) each into 12 parts (standard horas).
- For a query at time `t_q` within the year, identify the current hora.
- The hora's planetary lord (Sun-lord sequence) aspected against annual chart's Muntha yields hourly fortune signal.

Tripathaka is emitted on demand (not always) via a separate `/api/v1/varshaphala/{chart_id}/tripathaka?at={iso}` endpoint. Emits `structured_positions`.

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| Location for annual chart | Birthplace default; user override | TN Ch. 1 v. 8 is ambiguous; JH + majority of astrologers default birthplace |
| Ayanamsa for Tajaka | Inherit from natal unless override | Most astrologers don't switch ayanamsas mid-computation; 1° drift catastrophic |
| Year convention | Year 1 = birth chart; Year 2 = first return | Matches TN Ch. 1 v. 3 and Neelakanthi's worked examples |
| Tie-breaking for Varsheswara | Vimshottari lord order, then candidate category | TN is silent; JH's convention; documented in `details.tiebreak_rule` |
| Sahams day/night reversal | Per-Saham table (TN explicit for some, silent for others) | Match JH and Neelakanthi commentary |
| Saham alias names | Keep both, flag in details | Avoid losing citations from practitioners using the "other" name |
| Mudda variant at launch | Yoga-Vimshottari-Mudda only | Most widely used; other variants E5b |
| Rahu/Ketu deeptamsha | 5° (present in TN commentary tradition; included in orb averaging) | Some schools omit; expose as source_id variant |
| Ithasala orb uses average of two planets | Yes (`(orb_A + orb_B) / 2`) | TN 4.5 commentary; JH; standard Tajaka practice |
| Storage of inactive Sahams | Computed, stored in `details.all_saham_longitudes`; not surfaced | Astrologer may query any Saham later without recompute |
| Mudda start time granularity | To the second (matches solar-return moment) | Integer-day truncation loses AD precision |
| Tripathaka in same engine or separate | Separate endpoint, same engine class | Different cadence; shares primitives |

## 5. Component Design

### 5.1 New modules

```
src/josi/services/classical/
├── varshaphala/
│   ├── __init__.py
│   ├── engine.py                         # VarshaphalaEngine : ClassicalEngine
│   ├── solar_return.py                   # computes t_N via swe.solcross_ut
│   ├── muntha.py                         # muntha_sign, muntha_house, muntha_lord
│   ├── varsheswara.py                    # 5-candidate contest
│   ├── tajaka_aspects.py                 # aspect detection + deeptamsha
│   ├── sahams.py                         # Saham formulas + activation check
│   ├── mudda.py                          # Yoga-Vimshottari-Mudda tree
│   └── tripathaka.py                     # hourly chakra

src/josi/rules/tajaka/neelakanthi/
├── yogas/
│   ├── ithasala.yaml
│   ├── isharaaph.yaml
│   ├── nakta.yaml
│   ├── ...                               # all 16
├── sahams/
│   ├── punya.yaml
│   ├── vidya.yaml
│   ├── ...                               # all 30
└── varsheswara_contest.yaml              # 5-candidate scoring as a single composite rule

src/josi/api/v1/controllers/
└── varshaphala_controller.py

src/josi/rules/predicates/
└── tajaka_core.yaml                      # new predicates
```

### 5.2 Data model additions

No new tables. All results land in `technique_compute` with `technique_family_id = 'tajaka'` and `output_shape_id = 'annual_chart_summary'`. Rules registered under `source_id = 'tajaka_neelakanthi'` in `classical_rule`.

Index addition:
```sql
CREATE INDEX idx_tajaka_compute_chart_year
  ON technique_compute (chart_id, (result->>'year'))
  WHERE technique_family_id = 'tajaka';
```
(partial index; speeds "get Varshaphala for chart X, year Y" lookups.)

### 5.3 API contract

```
GET /api/v1/varshaphala/{chart_id}?year=2026
Headers:
  X-API-Key: <key> OR Authorization: Bearer <jwt>
Optional query params:
  ayanamsa      (override; default: inherit natal)
  location      (override; default: birthplace)
  sources       (comma-separated; default: tajaka_neelakanthi)
  strategy      (default: D_hybrid)

Response 200:
{
  "success": true,
  "message": "Varshaphala computed",
  "data": {
    "metadata": { ... TechniqueResultMetadata ... },
    "per_source": {
      "tajaka_neelakanthi": {
        "source_id": "tajaka_neelakanthi",
        "rule_version": "1.0.0",
        "content_hash": "…",
        "result": {
          "year": 2026,
          "muntha_sign": 3,
          "muntha_house": 7,
          "year_lord": "jupiter",
          "year_lord_strength": 0.73,
          "active_sahams": [
            {"name": "punya", "sign": 3, "house": 7, "degree": 14.22},
            ...
          ],
          "active_yogas": ["yoga.tajaka.ithasala.jupiter_sun", ...],
          "details": {
            "solar_return_utc": "2026-07-14T02:18:33Z",
            "location": {"lat": 13.08, "lon": 80.27},
            "ayanamsa": "lahiri",
            "varsheswara_scores": {"lagna_lord": 14, "muntha_lord": 11, ...},
            "all_saham_longitudes": { ... },
            "mudda_periods": [ TemporalRange, ... ],
            "tiebreak_rule": "vimshottari_lord_order"
          }
        },
        "computed_at": "…"
      }
    },
    "aggregates": { "D_hybrid": { ... AggregateEntry ... } }
  }
}

GET /api/v1/varshaphala/{chart_id}/tripathaka?at=2026-07-14T10:30:00Z
Response: TechniqueResult[StructuredPositions]
```

### 5.4 Internal Python interface

```python
# src/josi/services/classical/varshaphala/engine.py

class VarshaphalaEngine(ClassicalEngineBase):
    technique_family_id: str = "tajaka"
    default_output_shape_id: str = "annual_chart_summary"

    def __init__(self, calc: AstrologyCalculator, registry: PredicateRegistry):
        ...

    async def compute_for_source(
        self,
        session: AsyncSession,
        chart_id: UUID,
        source_id: str,
        rule_ids: list[str] | None = None,
        *,
        year: int,                            # required for tajaka; override method sig
        ayanamsa: str | None = None,
        location: GeoLocation | None = None,
    ) -> list[TechniqueComputeRow]:
        """
        1. Compute solar-return moment t_N.
        2. Cast annual chart.
        3. Compute Muntha.
        4. Run Varsheswara contest → year_lord + strength.
        5. Compute all Tajaka aspects.
        6. Evaluate 16 yogas via DSL rules.
        7. Compute 30 Sahams + activation.
        8. Compute Mudda tree.
        9. Assemble AnnualChartSummary.
        10. Persist to technique_compute.
        """

    async def compute_tripathaka(
        self,
        session: AsyncSession,
        chart_id: UUID,
        at: datetime,
    ) -> StructuredPositions: ...
```

## 6. User Stories

### US-E5.1: As an astrologer, I can request the Varshaphala for any year of any chart
**Acceptance:** `GET /api/v1/varshaphala/{chart_id}?year=2026` returns a complete `AnnualChartSummary` with muntha, year_lord, active_sahams, and active_yogas. Response P95 < 800 ms (cached); < 3 s (first compute).

### US-E5.2: As a classical advisor, I can verify the Year Lord by seeing the contest breakdown
**Acceptance:** `details.varsheswara_scores` lists all 5 candidates and their point totals. Winner matches TN Ch. 2 contest algorithm on 10 hand-computed fixtures.

### US-E5.3: As an astrologer using KP/Kerala ayanamsa, I can override Tajaka ayanamsa
**Acceptance:** `?ayanamsa=krishnamurti` computes the solar-return moment with KP ayanamsa and produces a different `solar_return_utc` than Lahiri (verified on golden chart with >1° ayanamsa delta).

### US-E5.4: As the AI chat surface, I receive `TechniqueResult[AnnualChartSummary]` that validates against the F7 JSON Schema
**Acceptance:** engine output passes `fastjsonschema.compile(annual_chart_summary_schema)(output)`; no extra keys; all required fields present.

### US-E5.5: As an engineer, identical inputs produce identical outputs year-over-year
**Acceptance:** `compute_for_source(chart_id=X, year=2026)` called twice in sequence inserts only one `technique_compute` row (ON CONFLICT DO NOTHING); recomputes validate content_hash stability.

### US-E5.6: As an astrologer, I can inspect all 50+ Saham longitudes even if only ~30 are reported "active"
**Acceptance:** `details.all_saham_longitudes` contains longitudes for all 30 computed Sahams; filter to `active_sahams` uses TN 30.20 criteria.

### US-E5.7: As a developer, I can add a 17th Tajaka yoga without engine code changes
**Acceptance:** new YAML under `src/josi/rules/tajaka/neelakanthi/yogas/` using existing predicates loads on next deploy; first request produces updated `active_yogas` list.

## 7. Tasks

### T-E5.1: Solar-return computation
- **Definition:** `solar_return.py` — given natal chart + year N, compute exact `t_N`. Wrap `swe.solcross_ut` with bracketing search; return UTC datetime with microsecond precision.
- **Acceptance:** 10 fixtures pass: computed `t_N` within ±0.1 seconds of JH reference.
- **Effort:** 10 hours
- **Depends on:** existing `AstrologyCalculator`

### T-E5.2: Muntha module
- **Definition:** `muntha.py` — compute muntha_sign, lookup in annual chart to get muntha_house, identify muntha_lord.
- **Acceptance:** 10 fixtures; muntha sign matches hand-computed progression.
- **Effort:** 4 hours

### T-E5.3: Varsheswara contest
- **Definition:** `varsheswara.py` — implement 11 scoring criteria; run contest; return (winner, score, per_candidate_scores).
- **Acceptance:** 10 fixtures pass with breakdown matching Sharma's English TN worked examples (Appendix B).
- **Effort:** 16 hours

### T-E5.4: Tajaka aspect engine
- **Definition:** `tajaka_aspects.py` — per-planet deeptamsha; applying/separating detection via daily motion; return list of active aspects with orb + strength.
- **Acceptance:** 20-aspect fixture (2 charts × 10 aspect pairs) matches hand-computed to within 0.01° orb.
- **Effort:** 14 hours

### T-E5.5: Predicate library additions (`tajaka_core.yaml`)
- **Definition:** register new predicates: `tajaka_aspect`, `tajaka_aspect_strength`, `is_applying_aspect`, `planet_daily_motion`, `planet_in_kendra_from_annual_lagna`, `blocking_planet_between`, `saham_longitude`.
- **Acceptance:** `poetry run validate-rules` passes; predicates resolve in registry.
- **Effort:** 8 hours
- **Depends on:** F6

### T-E5.6: 16 Tajaka yoga rule YAMLs
- **Definition:** One YAML per yoga under `src/josi/rules/tajaka/neelakanthi/yogas/`. Each cites TN chapter/verse.
- **Acceptance:** All 16 load via F6 loader; content_hashes stable across 3 runs.
- **Effort:** 20 hours
- **Depends on:** T-E5.5

### T-E5.7: Saham computation + 30 Saham YAMLs
- **Definition:** `sahams.py` generic formula engine; 30 YAMLs declaratively specifying formulas. Include day/night reversal per Saham.
- **Acceptance:** 30 Sahams computed for 5 fixtures match hand-computed longitudes to 0.001°.
- **Effort:** 24 hours

### T-E5.8: Mudda Dasha
- **Definition:** `mudda.py` — Yoga-Vimshottari-Mudda per §3.7. Emit MD + AD levels.
- **Acceptance:** 5 fixtures × 2 years: MD sequence + durations match JH reference.
- **Effort:** 12 hours

### T-E5.9: Tripathaka chakra
- **Definition:** `tripathaka.py` — hora lord sequence, map query time to hora, emit structured_positions.
- **Acceptance:** 10 hora-time fixtures match TN commentary worked examples.
- **Effort:** 8 hours

### T-E5.10: VarshaphalaEngine assembly
- **Definition:** Wire all modules in `engine.py`; implement `compute_for_source` + `assemble_result`.
- **Acceptance:** Full integration test: compute Varshaphala for 5 chart-years → 5 `technique_compute` rows + 5 `aggregation_event` rows; round-trip AnnualChartSummary.
- **Effort:** 16 hours
- **Depends on:** T-E5.1..T-E5.9

### T-E5.11: API controller + routing
- **Definition:** `varshaphala_controller.py` with `GET /api/v1/varshaphala/{chart_id}` and `/tripathaka` endpoints. Register in `api/v1/__init__.py`.
- **Acceptance:** OpenAPI docs show endpoints; manual curl against dev server returns shape-valid payload.
- **Effort:** 6 hours
- **Depends on:** T-E5.10

### T-E5.12: Golden fixture suite
- **Definition:** 5 natal charts × 2 years = 10 chart-years, each with fixture YAML listing expected muntha, year_lord, top 5 active Sahams, top 3 active yogas, Mudda MD→AD first 3 periods.
- **Acceptance:** Engine output matches fixture byte-equal across 3 runs.
- **Effort:** 20 hours

### T-E5.13: Performance + caching
- **Definition:** Cache `technique_compute` by (chart_id, year); implement cache invalidation on rule version bump; benchmark to 10 concurrent requests P95 < 1.5 s.
- **Acceptance:** Locust test passes.
- **Effort:** 6 hours

### T-E5.14: Documentation + CLAUDE.md update
- **Definition:** Add Varshaphala section to docs explaining Tajaka-vs-Parashari distinction; document solar-return ayanamsa policy.
- **Acceptance:** Docs merged.
- **Effort:** 3 hours

## 8. Unit Tests

### 8.1 Solar-return computation

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_solar_return_year_1_equals_birth` | natal chart, year=1 | t_N = birth moment | boundary |
| `test_solar_return_year_2_approx_365_days` | natal chart, year=2 | t_N − birth ≈ 365.25 days ± 12h | basic |
| `test_solar_return_subsecond_precision` | JH-matched fixture | computed matches to 0.1s | precision contract |
| `test_solar_return_ayanamsa_invariance` | same t_N recomputed with different ayanamsa on natal | solar-return t unchanged | Sun sidereal longitude depends on ayanamsa → test catches drift |
| `test_solar_return_leap_year_offset` | birth in leap year, year 5 | correct accumulated offset | calendar edge case |

### 8.2 Muntha

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_muntha_year_1_equals_natal_lagna` | natal Lagna Aries, year 1 | muntha_sign=0 | boundary (birth=year 1) |
| `test_muntha_year_13_full_cycle` | natal Lagna Aries, year 13 | muntha_sign=0 (full 12-sign cycle) | wrap-around |
| `test_muntha_house_in_annual_chart` | fixture | muntha_house from annual lagna | cross-chart math |
| `test_muntha_lord_identification` | muntha sign = Leo | muntha_lord = sun | lord lookup |

### 8.3 Varsheswara contest

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_varsheswara_all_candidates_scored` | any fixture | 5 entries in per_candidate_scores | completeness |
| `test_varsheswara_kendra_bonus_applied` | candidate in 4th house | +5 applied | TN 2.3 |
| `test_varsheswara_debilitation_penalty` | candidate in debilitation | −5 applied | TN 2.5 |
| `test_varsheswara_tiebreak_vimshottari_order` | two candidates tie at 14 | higher Vimshottari lord wins | decision §3.3 |
| `test_varsheswara_tn_appendix_b_example_1` | Sharma TN English App B fixture 1 | year_lord = Jupiter, score 17/26 | classical canonical |
| `test_varsheswara_tn_appendix_b_example_2` | fixture 2 | year_lord = Mars, score 19/26 | classical canonical |

### 8.4 Tajaka aspects

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_tajaka_conjunction_within_orb` | Sun 5°, Moon 10°, orb average 13.5° | conjunction active, strength 0.63 | basic orb calc |
| `test_tajaka_trine_exact` | Sun 0° Aries, Jupiter 0° Leo | trine active, strength 1.0 | exact aspect |
| `test_tajaka_square_outside_orb` | Sun 0°, Mars 100° (10° off 90°) | Sun-Mars orb avg = 11.5°; 10° inside → active; but test delta 95° from 90° = 5° inside | orb precision |
| `test_tajaka_applying_vs_separating` | faster planet behind slower | applying | direction semantics |
| `test_tajaka_deeptamsha_per_planet` | Sun-Saturn pair | orb = (15 + 9)/2 = 12° | per-planet orbs averaged |
| `test_tajaka_rahu_ketu_orb_5_deg` | Rahu-Venus pair | orb = (5 + 7)/2 = 6° | node orb policy |

### 8.5 Tajaka yogas (16 × ≥2 tests each — 32 minimum; critical 5 shown)

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_ithasala_applying_aspect_active` | two significators applying within orb | active, strength reflects closeness to exact | TN 3.1-5 |
| `test_ithasala_separating_not_active` | separating aspect | inactive; Isharaaph active instead | distinction |
| `test_isharaaph_separating_aspect_active` | separating within orb | active | TN 3.6-8 |
| `test_kamboola_moon_ithasala_year_lord` | Moon applying to year lord | Kamboola active | TN 5.1-3 |
| `test_khallasara_blocking_planet_intervenes` | third planet aspects both signif | Khallasara blocks Ithasala | TN 5.5-8 |
| `test_radda_debilitated_signif_kills_yoga` | Ithasala pair, one debilitated | Radda active, reduces Ithasala strength | TN 5.9-11 |
| `test_tambira_year_lord_own_sign_kendra` | year lord in own sign in kendra | Tambira active, max strength | TN 6.4 |
| `test_ikkabala_unafflicted_year_lord` | year lord clean | Ikkabala active | TN 6.6-8 |

### 8.6 Sahams

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_saham_punya_day_formula` | Sun 5°, Moon 40°, Lagna 100° | Punya = 40 − 5 + 100 = 135° | TN 30.3 |
| `test_saham_punya_night_reversal` | night birth, same | Punya = 5 − 40 + 100 = 65° | day/night |
| `test_saham_vidya_day_formula` | same | Vidya = 5 − 40 + 100 = 65° | TN 30.4 |
| `test_all_30_sahams_compute_without_error` | full fixture | 30 numeric longitudes in [0, 360) | completeness |
| `test_saham_active_when_lord_aspects_year_lord` | configured fixture | Saham in active_sahams list | activation §3.6 |
| `test_saham_inactive_not_surfaced` | Saham lord neutral | not in active_sahams; present in details.all_saham_longitudes | surfacing policy |
| `test_saham_alias_flagged` | Mahatmya and Karmagaha same formula | details.manuscript_alias_of set | alias handling |

### 8.7 Mudda Dasha

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_mudda_total_duration_equals_tropical_year` | sum of MD durations | 365.2425 days ± 0.01 | compression check |
| `test_mudda_md_proportions_preserved` | ratio of Jupiter MD to Saturn MD | 16/19 (Vimshottari proportion) | algorithm invariant |
| `test_mudda_starting_lord_yoga_shift` | annual Moon nakshatra = Rohini (Moon lord), year 3 | starting lord shifted by ((3-1) mod 9)+1 = 3 positions in Vimshottari order → shifts Moon → Mars → Rahu → Jupiter; starting lord = Jupiter | §3.7 algorithm |
| `test_mudda_ad_within_md_proportions` | first MD's 9 ADs | durations = Vimshottari_ADs × MD_frac | hierarchy |

### 8.8 Tripathaka

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_tripathaka_daytime_first_hora` | sunrise + 10 min | Sun's hora (weekday lord sequence) | basic |
| `test_tripathaka_night_sequence` | post-sunset | night-hora sequence differs from day | day/night |
| `test_tripathaka_muntha_aspect` | hora lord aspects muntha | favorable hour flag set | aspect linkage |

### 8.9 Integration + end-to-end

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_varshaphala_full_path` | 5 charts × 2 years | 10 technique_compute + 10 aggregation_event rows; all AnnualChartSummary valid against F7 schema | E2E |
| `test_varshaphala_idempotent_recompute` | call twice | 1 technique_compute row (ON CONFLICT), 2 aggregation_event rows (append-only) | F2 contract |
| `test_varshaphala_ayanamsa_override_changes_output` | same chart, Lahiri vs KP | different solar_return_utc; potentially different muntha_house | ayanamsa wiring |
| `test_varshaphala_location_override_changes_houses` | same chart, birthplace vs NYC | muntha_house differs; year_lord same | location wiring |
| `test_varshaphala_output_shape_strict` | output | passes fastjsonschema(annual_chart_summary) | F7 ↔ E5 parity |

## 9. EPIC-Level Acceptance Criteria

- [ ] `VarshaphalaEngine` implements `ClassicalEngine` Protocol; `isinstance` check passes
- [ ] Solar-return computation within ±0.1 s of JH reference on 10 fixtures
- [ ] Muntha calculation correct on 10 fixtures (year 1 through 24)
- [ ] Varsheswara contest matches TN Sharma Appendix B examples (2 canonical examples)
- [ ] Tajaka aspect engine handles all 5 aspect types with per-planet deeptamsha
- [ ] All 16 Tajaka yogas implemented as DSL rules; all load via F6; all pass activation fixtures
- [ ] 30 Sahams implemented with day/night reversal per TN table
- [ ] Mudda Dasha (Yoga-Vimshottari variant) produces correct MD+AD tree summing to 365.2425 d
- [ ] Tripathaka chakra computes for arbitrary intraday times
- [ ] `AnnualChartSummary` output validates against F7 JSON Schema for all fixtures
- [ ] API endpoint `GET /api/v1/varshaphala/{chart_id}?year=YYYY` live and documented
- [ ] Golden chart suite: 5 charts × 2 years × 6 asserted fields = 60 assertions all green
- [ ] Unit test coverage ≥ 90% across `varshaphala/` package
- [ ] Integration test hits full path (compute → persist → aggregate → read via TechniqueResult)
- [ ] Performance: P95 < 1.5 s uncached, < 400 ms cached at 10 rps
- [ ] CLAUDE.md updated with Varshaphala section
- [ ] Ayanamsa override + location override both functional and tested

## 10. Rollout Plan

- **Feature flag:** `enable_tajaka_engine` — off in P1, on in P2 behind astrologer Pro mode first, then B2C after 2-week soak.
- **Shadow compute:** for 2 weeks after deploy, compute Varshaphala on every chart-read but don't surface in AI tool-use; log to `logs/tajaka_shadow.log`; manually review 100 random outputs against JH.
- **Backfill strategy:** lazy (compute on first request per chart-year); background job backfills top 10k active charts for current + next year during off-peak.
- **Rollback plan:** set `enable_tajaka_engine=false`; API returns 501 Not Implemented; `technique_compute` rows stay; redeploy old code with no migration.

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Solar-return computation slow (iterative bracketing) | Medium | Medium | Cache `t_N` per (chart_id, year); swe.solcross_ut is fast (< 5 ms) in practice |
| Ayanamsa override produces subtly wrong charts | Medium | High | Test suite enforces 0.1-s invariance; user-visible UI shows "ayanamsa: lahiri" next to result |
| Saham manuscript aliases disagree | High | Medium | Expose both names; flag aliases in details; audit log when astrologer queries Saham by alias |
| Varsheswara tie-break rule disagreement | Low | Medium | Document clearly; expose `tiebreak_rule` in details; allow astrologer override in future |
| Tajaka aspect applying/separating calc fragile near aspect-exactness | Medium | Medium | Daily-motion from swe; test fixtures near exactitude; clamp direction when Δλ < 0.01° |
| Rule YAML count grows to 46 (16 + 30) — slow F6 load | Low | Low | F6 loader is O(N) at startup; 46 rules × 1 ms = 46 ms |
| Mudda starting-lord algorithm disputed across mss | Medium | Medium | Ship Yoga-Vimshottari-Mudda as default; document explicitly; E5b adds other variants as distinct rules |
| Historical chart data (pre-1900 births) has ephemeris edge cases | Low | Medium | Swiss Ephemeris handles 5400 BCE – 5400 CE; test one pre-1900 fixture |
| Annual chart at timezone-boundary births produces wrong year number | Medium | Medium | Always compute in UTC; test a fixture born 23:58 local |

## 12. References

- Master spec: [`docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`](../../../superpowers/specs/2026-04-19-classical-techniques-expansion-design.md) §2.2 (Tajaka summary in chart_reading_view), §5.2 (PRD tagging)
- F1 dims: [`../P0/F1-star-schema-dimensions.md`](../P0/F1-star-schema-dimensions.md) — `source_id: tajaka_neelakanthi`
- F2 fact tables: [`../P0/F2-fact-tables.md`](../P0/F2-fact-tables.md)
- F6 Rule DSL: [`../P0/F6-rule-dsl-yaml-loader.md`](../P0/F6-rule-dsl-yaml-loader.md)
- F7 Output shapes: [`../P0/F7-output-shape-system.md`](../P0/F7-output-shape-system.md) §5.3.8 `annual_chart_summary`
- F8 Aggregation Protocol: [`../P0/F8-technique-result-aggregation-protocol.md`](../P0/F8-technique-result-aggregation-protocol.md)
- E1a Multi-Dasa v1: (used for natal Vimshottari mapping Moon nakshatra → lord)
- E10 Prasna/Horary: reuses Tajaka aspect + Saham infrastructure
- **Classical sources**:
  - Neelakantha, *Tajaka Neelakanthi* — Sharma, G.C. (trans.), 2005, Sagar Publications — Ch. 1 (annual chart), Ch. 2 (Varsheswara), Ch. 3 (Ithasala/Isharaaph), Ch. 4 (aspects + deeptamsha), Ch. 5-6 (remaining 14 yogas), Ch. 30-32 (Sahams), Ch. 40 (Mudda), Ch. 42 (Tripathaka)
  - Mantreswara, *Phaladeepika* Ch. 20 — parallel treatment of annual predictions; secondary source
  - Vaidyanatha, *Jataka Parijata* Ch. 18 — Varshaphala cross-reference
  - *Varshatantra* (attribution disputed; medieval Sanskrit) — additional Saham formulas; consulted for aliases only
- Reference implementations:
  - Jagannatha Hora 7.41 — "Tajika" tab; used as numeric baseline
  - Parashara's Light 9.0 — Varshaphala module (commercial; not canonical)
