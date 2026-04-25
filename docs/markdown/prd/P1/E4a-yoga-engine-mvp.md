---
prd_id: E4a
epic_id: E4
title: "Classical Yoga Engine MVP (60 core yogas)"
phase: P1-mvp
tags: [#correctness, #extensibility, #experimentation]
priority: must
depends_on: [F1, F2, F4, F6, F7, F8, F13, F16, F17]
enables: [E4b, E11a, E14a, E12]
classical_sources: [bphs, saravali, phaladeepika, jataka_parijata]
estimated_effort: 4 weeks
status: approved
author: @agent-claude-opus-4-7
last_updated: 2026-04-22
---

# E4a — Classical Yoga Engine MVP (60 Core Yogas)

## 1. Purpose & Rationale

Yogas (*yoga* = "union," a specific planetary configuration producing a definite effect) are the **single largest classical content area** in Vedic astrology. Classical texts catalogue them across four major families — **Raja** (royalty/power), **Dhana** (wealth), **Chandra/Surya** (Moon-/Sun-centered), **Dushta** (afflicting) — with **Pancha Mahapurusha** (five "great person" yogas) as a fifth structural group and **Neecha Bhanga** (debility-cancellation) as a sixth.

An astrology platform that cannot identify active yogas in a chart is a fundamentally shallow platform. The reading experience for most end users is "what's special about my chart?" — and the answer is named yogas.

Josi currently has **no classical yoga engine**. Chart analysis is limited to planet positions, houses, and basic aspect listings. This PRD closes the gap with **60 core yogas**, each encoded as a declarative rule (F6 DSL), content-hashed (F4), activation-checked via predicates, and evaluated via the `ClassicalEngine` Protocol (F8).

The 60 chosen here are the *highest-cited* across BPHS, Saravali, and Phaladeepika — the yogas an astrologer *would mention first*. Full 250-yoga expansion lands in E4b (P2). The 1000-yoga reference set lands in P4 via the rule authoring console (P3-E2).

**Why rules not code:** every yoga ships as a YAML file in `src/josi/db/rules/yoga/`. Adding yoga 61 requires zero engineering change — just author YAML, PR, merge, deploy. Rule authors need not know Python. The engine interprets predicates declaratively (predicate vocabulary defined in F6; extended here as needed).

**Why strength scores not just boolean:** classical tradition differentiates "yoga present nominally" from "yoga at full strength." A yoga with a debilitated planet is weaker than one with an exalted planet; a yoga with aspect support is stronger than one without. Every yoga rule defines both an activation predicate (boolean) and a strength formula (0..1). End-user responses surface both; "you have Raja Yoga at 0.82 strength" reads more accurately than "you have Raja Yoga."

## 2. Scope

### 2.1 In scope

- **60 yoga rules** across 6 categories (Pancha Mahapurusha 5, Raja 15, Dhana 10, Chandra 10, Surya 5, Dushta 15).
- **Full YAML authoring for all 60**, each with:
  - `rule_id`, `source_id`, `version`, `content_hash`
  - `citation` (chapter + verse)
  - `classical_names` (en, sa_iast, sa_devanagari, ta)
  - Activation predicate using predicate vocabulary
  - Strength formula
- **Full expanded YAML** shown in this PRD for 5 representative yogas (one per category for engineering clarity); the other 55 listed with brief predicate summaries.
- **Predicate vocabulary** extension (if needed beyond F6 base): planet-in-kendra, planet-in-trikona, planet-in-own-sign, planet-exalted, planet-debilitated, mutual-aspect, conjunction, dispositor-of, lord-of-house, etc.
- **Cross-source variants** for yogas where BPHS and Saravali disagree (explicitly noted per yoga).
- **Engine implementation** as `YogaEngine(BaseClassicalEngine)` that evaluates all active rules against a chart, produces one compute row per yoga rule with `BooleanWithStrengthResult` shape.
- **Per-yoga test fixtures**: known charts with confirmed activation (famous charts from B.V. Raman's *Notable Horoscopes* catalogue where applicable).
- **REST + AI tool-use** endpoints.

### 2.2 Out of scope

- **Yogas 61–250** (full set): E4b.
- **Yoga interpretation/prediction text generation** (what the yoga *means* in natural language): E11a via AI LLM layer.
- **Yogas that require Jaimini system** (Chara Karakas, Arudhas): E3 in P2.
- **Tajaka yogas** (annual-chart yogas): E5.
- **Divisional-chart-specific yogas** (e.g., yogas in D-9 Navamsa): E4b.
- **Ashtakavarga-based yoga variants** (bindu thresholds): E4b.

### 2.3 Dependencies

- F1 (source_authority: `bphs`, `saravali`, `phaladeepika`, `jataka_parijata`; technique family `yoga`; output shape `boolean_with_strength`).
- F2 (fact tables).
- F4 (temporal rule versioning).
- F6 (rule DSL + predicate vocabulary; this PRD extends the vocabulary).
- F7 (JSON Schema for `boolean_with_strength`).
- F8 (`ClassicalEngine` Protocol + aggregation strategies).
- F13 (content-hash provenance).
- F16 (golden chart suite — adds yoga fixtures).
- F17 (property harness — ensures deterministic activation).
- Existing: `src/josi/services/astrology_service.py` supplies chart state (planet positions, houses, aspects, dispositors).

## 2.4 Design Decisions (Pass 1 Astrologer Review — Locked 2026-04-21)

All open questions from E4a Pass 1 astrologer review are resolved. Cross-cutting decisions reference `DECISIONS.md`; E4a-specific decisions documented here.

### Cross-cutting decisions (applied via `DECISIONS.md`)

| Decision | Value | Ref |
|---|---|---|
| Ayanamsa default | Lahiri B2C + 9-shortlist astrologer | 1.2 |
| Rahu/Ketu node type | Both Mean + True computed; **Mean default B2C** (revised 2026-04-22) | 1.1 |
| House system | Whole Sign B2C rasi chart + Bhava Chalit/Sripati parallel | 1.3 |
| Natchathiram count | 27 for all yoga predicates | 3.7 |
| Language display | Sanskrit-IAST canonical + Tamil phonetic for UI | 1.5 |
| Divisional chart purpose | BPHS Ch.6 canonical metadata per varga | 1.9/1.10 |

### E4a-specific decisions (locked this review)

| Decision | Value | Source |
|---|---|---|
| **Neecha Bhanga cancellation** (Q1) | **Approach A — separate yoga only.** Neecha Bhanga Raja Yoga emitted as one of 60 MVP yogas; does NOT affect other yoga activations. Pancha Mahapurusha and other predicates check own-sign/exaltation strictly. Matches BPHS/Phaladeepika/Saravali + Raman/Rao/Rath/Narasimha Rao + JH/PyJHora/Parashara's Light. Post-research (unanimous classical + modern authority consensus). | Q1 post-research |
| **Strength formula source** (Q2) | **Source D — Modern synthesis with Shadbalam dependency.** Each yoga strength incorporates participating planets' Shadbalam fractions per BPHS qualitative + Phaladeepika numerical + modern synthesis. **Engineering sequencing flag:** E4a depends on E19 Shadbalam Engine (new P2 PRD per GAP_CLOSURE). Options: bump E19 P2→P1 OR E4a v1 ships with Source E (dignity-weighted average) temporarily and upgrades when E19 lands. | Q2 |
| **Cross-source yoga variants** (Q3) | **Approach D — per-yoga curation by modern Parashari consensus.** For each of ~5-8 disputed yogas (Gajakesari, Sunapha, Vasi, Adhi, etc.), pick whichever variant Raman/Rath/Narasimha Rao endorses (typically matches Jagannatha Hora). Per-yoga decisions documented inline in YAML rule files with citation. | Q3 |
| **Active-yoga threshold** (Q4) | **Approach D — no threshold; rank-based display.** All activated yogas shown sorted by strength descending. B2C UI shows top 5-7; astrologer sees full list with strength column. Matches Jagannatha Hora behavior. | Q4 |
| **Graha Drishti in yoga predicates** (Q5) | **Composite approach** post-research: **Predicate:** V1 boolean with special-aspect promotion — 7th for all grahas + 3/10 for Sani (full) + 5/9 for Guru (full) + 4/8 for Sevvai (full). Matches BPHS Ch.26 "sambandha requires full drishti". **Strength formula:** V2 graded per BPHS Ch.28 Sphuta drishti (handled via Source D synthesis in Q2). **Rahu/Ketu default:** 7th only (matches JH/PyJHora/PL/AstroSage). **Astrologer profile toggle:** 4-option Node Aspect Rule selector — None (BPHS literal) / 7th only (default) / 5/7/9 Jupiter-like (Sanjay Rath) / 3/7/11 Tamil folk variant. | Q5 post-research |
| **Predicate vocabulary scope** (Q6) | **Option B — BPHS-comprehensive (~30 predicates).** Covers Ch.36-44 yoga descriptions comprehensively. Forward-compatible with E4b's 250-yoga extension. Matches Jagannatha Hora's implemented predicate set. Includes: planet-in-kendra, -trikona, -upachaya, -own-sign, -exalted, -debilitated, -moolatrikona, -vargottama, parivartana, conjunction, aspect (boolean V1+promotion), mutual-aspect, lord-of-house, dispositor-of, planet-in-Nth-from, same-nakshatra, bhava-has-benefic/malefic, planet-not-combust, planet-is-yoga-karaka-for-lagna, aspect-strength (V2 for strength), neecha-bhanga-conditions, and related. | Q6 |
| **Golden chart fixture architecture** (Q7) | **3-tier fixture architecture** post-research: **Tier 1 synthesized (60 files)** — minimal-activation isolated charts per yoga, classical-śloka-cited, deterministic. **Tier 2 public-figure (~15 AA-rated astrodatabank charts)** — Gandhi, Einstein, Nehru, Ramakrishna, Indira Gandhi, Queen Elizabeth II, Ramana Maharshi, Sri Aurobindo, Helen Keller, et al. — integration-level multi-yoga validation. **Tier 3 classical-text** — verified Raman 300C chart transcriptions, populated as physical book is consulted. **Sourcing stack:** Raman *Three Hundred Important Combinations* (58/60 coverage) + K.N. Rao *Yogas in Astrology* (Kala Sarpa + Vipareeta) + PVR Narasimha Rao *Integrated Approach* (cross-validation). **13 single-source yogas** (Parvata, Dhwaja, Kahala, Pushkala, Chamara, Kuladeepa, Vasi-from-Moon, Vesi/Vosi-from-Moon, Surya sect triad, Pisacha, Jadatva, Bhiru, Vesha-afflicting, Nirbhagya) resolved via Tier 1 synthesized. | Q7 post-research |
| **Yoga Karaka per-ascendant table** (Q8) | **Canonical 12-row table.** 6 Lagnas with dedicated Yoga Karaka: Rishabam (Sani), Kadagam (Sevvai), Simmam (Sevvai), Thulam (Sani), Magaram (Sukkiran), Kumbham (Sukkiran). 6 Lagnas with Lagna-lord-only: Mesham, Mithunam, Kanni, Viruchigam, Dhanusu, Meenam. Rahu/Ketu excluded from Yoga Karaka eligibility. Matches JH/PL/all modern software. | Q8 |

### Yoga Karaka canonical table (BPHS Ch.40 v.1-3)

| Lagna | Yoga Karaka | Rules kendra | Rules trikona |
|---|---|:-:|:-:|
| Mesham | Lagna lord (Sevvai) only | 1 | 1 |
| Rishabam | **Sani** | 10 | 9 |
| Mithunam | Lagna lord (Budhan) only | 1, 4 | 1 |
| Kadagam | **Sevvai** | 10 | 5 |
| Simmam | **Sevvai** | 4 | 9 |
| Kanni | Lagna lord (Budhan) only | 1, 10 | 1 |
| Thulam | **Sani** | 4 | 5 |
| Viruchigam | Lagna lord (Sevvai) only | 1 | 1 |
| Dhanusu | Lagna lord (Guru) only | 1, 4 | 1 |
| Magaram | **Sukkiran** | 10 | 5 |
| Kumbham | **Sukkiran** | 4 | 9 |
| Meenam | Lagna lord (Guru) only | 1, 10 | 1 |

### Engineering action items (not astrologer-review scope)

- [ ] Resolve E19 Shadbalam Engine sequencing (P2→P1 bump vs staged E4a v1 upgrade path)
- [ ] Implement ~30-predicate BPHS-comprehensive DSL in `src/josi/services/classical/yoga/predicates.py`
- [ ] Author 60 YAML rule files under `src/josi/db/rules/yoga/` (Pancha Mahapurusha 5, Raja 15, Dhana 10, Chandra 10, Surya 5, Dushta 15)
- [ ] Implement 3-tier fixture architecture at `tests/fixtures/yogas/{tier1_synthesized,tier2_public_figures,tier3_classical_text}/`
- [ ] Node Aspect Rule astrologer-profile toggle (4 options) via F2 `astrologer_source_preference`
- [ ] Yoga Karaka table encoded as shared reference data for predicate evaluation
- [ ] Per-yoga curation documentation for the ~5-8 BPHS-vs-Saravali disputed yogas with classical citation per decision
- [ ] Neecha Bhanga Raja Yoga as standalone predicate (classical cancellation conditions from BPHS Ch.40 v.19-25)

---

## 3. Classical / Technical Research

### 3.1 Yoga catalog — 60 yogas with category, source, and brief definition

All 60 are listed here. Full YAML for 5 representative examples appears in §3.2. Remaining 55 are specified as predicate summaries in §3.3.

#### 3.1.1 Pancha Mahapurusha Yogas (5) — BPHS Ch. 36

Five yogas, one per non-luminary-non-node classical planet (Mars, Mercury, Jupiter, Venus, Saturn), activating when the planet is **in its own sign or exalted** AND **in a kendra (1/4/7/10) from Lagna**.

| # | Yoga | Planet | Sign conditions | Houses (kendra) | Source |
|---|---|---|---|---|---|
| 1 | Ruchaka | Mars | Own (Aries/Scorpio) or exalted (Capricorn) | 1/4/7/10 | BPHS 36.2-4 |
| 2 | Bhadra | Mercury | Own (Gemini/Virgo) or exalted (Virgo) | 1/4/7/10 | BPHS 36.5-6 |
| 3 | Hamsa | Jupiter | Own (Sagittarius/Pisces) or exalted (Cancer) | 1/4/7/10 | BPHS 36.7-9 |
| 4 | Malavya | Venus | Own (Taurus/Libra) or exalted (Pisces) | 1/4/7/10 | BPHS 36.10-12 |
| 5 | Sasa | Saturn | Own (Capricorn/Aquarius) or exalted (Libra) | 1/4/7/10 | BPHS 36.13-16 |

#### 3.1.2 Raja Yogas (15) — BPHS Ch. 37 + Phaladeepika Ch. 6

Yogas producing power, status, governance. Most depend on combinations of lords of kendras (1/4/7/10) and trikonas (1/5/9), the two classical "auspicious" house-groups.

| # | Yoga | Short rule | Source |
|---|---|---|---|
| 6 | Gaja Kesari | Moon in kendra (1/4/7/10) from Jupiter | BPHS 37.5-6 |
| 7 | Amala | Natural benefic alone in 10th from Moon (OR from Lagna; variant) | BPHS 37.14 |
| 8 | Adhi | Natural benefics in 6/7/8 from Moon | BPHS 37.15-17 |
| 9 | Chamara | Lagna lord exalted in kendra with Jupiter aspect | Phaladeepika 6.12 |
| 10 | Dhenu | 2nd lord in kendra from Lagna | Phaladeepika 6.14 (variant) |
| 11 | Shankha | Benefics in 5 and 6 from Lagna AND 10th lord in 6/8/12 | Phaladeepika 6.32 |
| 12 | Bheri | Jupiter in 1/4/10 from Lagna OR from 7th lord | Phaladeepika 6.29 |
| 13 | Viparita Raja Yoga — Harsha | 6th lord in 6 OR 8 OR 12, no benefic association | BPHS 37.28 |
| 14 | Viparita Raja Yoga — Sarala | 8th lord in 6 OR 8 OR 12, no benefic association | BPHS 37.29 |
| 15 | Viparita Raja Yoga — Vimala | 12th lord in 6 OR 8 OR 12, no benefic association | BPHS 37.30 |
| 16 | Dharma-Karmadhipati Yoga | 9th lord + 10th lord in conjunction or mutual exchange | BPHS 37.9-10 |
| 17 | Kendra-Trikona Raja Yoga (generic) | Lord of kendra + lord of trikona in same house, mutual aspect, or exchange | BPHS 37.6-8 |
| 18 | Lagna-5 Raja Yoga | Lagna lord and 5th lord in mutual aspect, exchange, or conjunction | BPHS 37.8 (sub-case) |
| 19 | Lagna-9 Raja Yoga | Lagna lord and 9th lord in mutual aspect, exchange, or conjunction | BPHS 37.8 (sub-case) |
| 20 | Kahala | 4th lord + 9th lord in kendra AND Lagna lord strong | Phaladeepika 6.10 |

#### 3.1.3 Dhana Yogas (10) — Phaladeepika Ch. 15 + BPHS Ch. 43

Yogas producing wealth. Most involve the 2nd (family wealth), 5th (fortune), 9th (destiny), 11th (gains) lords.

| # | Yoga | Short rule | Source |
|---|---|---|---|
| 21 | Dhana Yoga (classical) | 2nd lord + 11th lord in conjunction OR mutual aspect OR exchange | Phaladeepika 15.2 |
| 22 | Lakshmi Yoga | 9th lord in own/exalted sign in a kendra AND Venus strong | Phaladeepika 15.4 |
| 23 | Kubera Yoga | 11th lord in 2nd OR 2nd lord in 11th, with benefic association | BPHS 43.6 |
| 24 | Dhana Yoga (Lagna-2) | Lagna lord + 2nd lord in conjunction | Phaladeepika 15.2 (sub-case) |
| 25 | Dhana Yoga (Lagna-11) | Lagna lord + 11th lord in conjunction/aspect | Phaladeepika 15.2 (sub-case) |
| 26 | Dhana Yoga (5-9) | 5th lord + 9th lord in conjunction/aspect (classical wealth + fortune) | BPHS 43.3 |
| 27 | Dhana Yoga (5-11) | 5th lord + 11th lord in conjunction/aspect | Phaladeepika 15.3 |
| 28 | Dhana Yoga (2-9) | 2nd lord + 9th lord in conjunction/aspect | BPHS 43.4 |
| 29 | Mahalakshmi Yoga | Venus + Moon in kendra from Lagna AND both unafflicted | Phaladeepika 15.6 (regional) |
| 30 | Guru-Mangala Yoga | Jupiter + Mars in conjunction/aspect, both dignified | Saravali 42.5 |

#### 3.1.4 Chandra Yogas (10) — BPHS Ch. 38

Moon-centered yogas; most classical texts cite the four core (Sunapha, Anapha, Durudhara, Kemadruma) first, then supplementary.

| # | Yoga | Short rule | Source |
|---|---|---|---|
| 31 | Sunapha | Any planet (except Sun, Rahu, Ketu) in 2nd from Moon | BPHS 38.2 |
| 32 | Anapha | Any planet (except Sun, Rahu, Ketu) in 12th from Moon | BPHS 38.3 |
| 33 | Durudhara | Planets in both 2nd AND 12th from Moon (excluding Sun) | BPHS 38.4 |
| 34 | Kemadruma | No planet in 1st, 2nd, or 12th from Moon (excluding Sun), and Moon not in kendra from Lagna | BPHS 38.5 (with cancellations) |
| 35 | Adhi Chandra (Chandra Adhi) | Benefics in 6/7/8 from Moon | BPHS 38.7-8 |
| 36 | Vasumati Yoga | Benefics in upachaya (3/6/10/11) from Moon | Saravali 13.4 |
| 37 | Pushkala Yoga | Moon's dispositor + Lagna lord in mutual aspect OR kendra with Moon | Saravali 13.11 |
| 38 | Shakata Yoga | Moon in 6/8/12 from Jupiter (affliction, dushta per some texts) | Saravali 13.9 |
| 39 | Chandra Mangala Yoga | Moon + Mars in conjunction or mutual aspect | Phaladeepika 6.22 |
| 40 | Gaja Kesari (noted in both Raja and Chandra) | Moon in kendra from Jupiter (same rule as #6; referenced both categories) | BPHS 37.5-6 (cross-category) |

Note: Gaja Kesari appears in both Raja and Chandra categories in classical texts; we dedupe by the rule_id and retain a single compute row.

#### 3.1.5 Surya Yogas (5) — BPHS Ch. 38 v.12-17

Sun-centered yogas parallel to Chandra family.

| # | Yoga | Short rule | Source |
|---|---|---|---|
| 41 | Vesi | Planet (other than Moon, Rahu, Ketu) in 2nd from Sun | BPHS 38.12 |
| 42 | Vosi | Planet (other than Moon, Rahu, Ketu) in 12th from Sun | BPHS 38.13 |
| 43 | Ubhayachari | Planets in both 2nd AND 12th from Sun | BPHS 38.14 |
| 44 | Budha-Aditya | Sun + Mercury conjunct within 10° | BPHS 38.20 (variant); Phaladeepika 6.27 |
| 45 | Surya Kemadruma | No planets in 2nd, 12th, 1st from Sun (Sun-equivalent of Kemadruma) | Saravali 14.6 (rare name variant) |

#### 3.1.6 Dushta / Arishta Yogas (15) — BPHS Ch. 42 + Phaladeepika Ch. 14

Afflicting / inauspicious combinations. Some cancel each other (cancellation rules cited inline).

| # | Yoga | Short rule | Source |
|---|---|---|---|
| 46 | Kemadruma (afflictive) | Same as #34 Kemadruma; category-classified dushta when uncanceled | BPHS 38.5 |
| 47 | Shakata (afflictive) | Same as #38 | Saravali 13.9 |
| 48 | Angaraka Yoga | Mars + Rahu conjunction OR Mars + Ketu conjunction | Saravali 38.11 (regional) |
| 49 | Pitra Dosha | Sun + Rahu conjunction OR Sun + Ketu conjunction OR Sun in 9th with malefic aspect | BPHS 42.6 (regional naming) |
| 50 | Kaal Sarp Yoga | All 7 classical planets between Rahu-Ketu axis (8 named subtypes by axis: Ananta, Kulika, Vasuki, Shankapala, Padma, Mahapadma, Takshaka, Karkotaka, Shankhachuda — classical regional enumeration) | Phaladeepika 14.18-21 (derivative; named subtypes are modern consolidation) |
| 51 | Daridra Yoga | 11th lord in 12th house (loss-of-gains) | BPHS 42.9 |
| 52 | Guru Chandala Yoga | Jupiter + Rahu OR Jupiter + Ketu conjunction | Saravali 38.13 |
| 53 | Vish Yoga | Moon + Saturn conjunction or 7th-aspect relationship | Saravali 13.21 |
| 54 | Graha Yuddha (Planetary War) | Two planets within 1° of each other (excluding Sun-Moon, Rahu-Ketu) — classical "war" rule identifies winner and loser | BPHS Ch. 27 |
| 55 | Balarishta | Moon in 6/8/12 with malefic aspect AND no benefic relief (birth-time affliction for infant) | BPHS 42.3-5 |
| 56 | Arishta Yoga (Chandra-weak) | Moon in 6/8/12 AND hemmed by malefics with no benefic aspect | BPHS 42.5 |
| 57 | Kuja Dosha (Mangal Dosha) | **B2C default (per DECISIONS §6.5 E25 Q2, revised 2026-04-22):** Sevvai in 2/4/7/8/12 from Lagna (5 houses, Lagna-only single-reference). **Astrologer toggle:** add 1st-house inclusion + Chandran-reference + Sukran-reference for lineages that require them. Classical Phaladeepika 14.12 lists Moon + Venus reference; not in current Tamil Parashari practice. | Phaladeepika 14.12 + DECISIONS §6.5 E25 Q2 |
| 58 | Kuja Dosha Cancellation | Kuja Dosha canceled when: Mars in own/exalted OR Mars aspected by Jupiter OR both partners have Kuja Dosha | Classical synthesis (B.V. Raman) |
| 59 | Sakata Cancellation (Sakata Bhanga) | Shakata canceled when Moon in own/exalted sign OR aspected by benefics | Classical synthesis |
| 60 | Neecha Bhanga Raja Yoga | Debilitated planet's debilitation canceled (see §3.4); produces Raja Yoga | BPHS 39.1-10 |

### 3.2 Five representative yogas — full YAML

These five demonstrate the full rule DSL across categories. All other 55 yoga YAMLs follow the same structure.

#### 3.2.1 Ruchaka Yoga (Pancha Mahapurusha) — full YAML

**`src/josi/db/rules/yoga/pancha_mahapurusha/ruchaka_bphs.yaml`:**

```yaml
rule_id: yoga.pancha_mahapurusha.ruchaka.bphs
source_id: bphs
version: "1.0.0"
technique_family_id: yoga
output_shape_id: boolean_with_strength
citation: "BPHS Ch.36 v.2-4"
classical_names:
  en: "Ruchaka Yoga"
  sa_iast: "Rucaka Yoga"
  sa_devanagari: "रुचक योग"
  ta: "ருசக யோகம்"
  hi: "रुचक योग"
effective_from: "2026-01-01T00:00:00Z"
effective_to: null

activation:
  predicate:
    op: all_of
    clauses:
      - op: planet_sign_status
        planet: mars
        status_any_of: [own_sign, exalted]
      - op: planet_in_house_group
        planet: mars
        houses: [1, 4, 7, 10]          # kendra from Lagna
        reference: lagna

strength:
  formula: weighted_sum
  terms:
    - weight: 0.5
      factor:
        op: planet_sign_status_score
        planet: mars
        scores:
          exalted: 1.0
          own_sign: 0.85
    - weight: 0.2
      factor:
        op: house_strength_score
        planet: mars
        scores:
          "1": 1.0
          "10": 0.95
          "7": 0.85
          "4": 0.75
    - weight: 0.2
      factor:
        op: aspects_received_score
        planet: mars
        benefic_aspect_bonus: 0.2
        malefic_aspect_penalty: 0.15
        base_score: 0.7
    - weight: 0.1
      factor:
        op: combustion_penalty
        planet: mars
        combust_within_degrees: 17
        penalty_if_combust: 0.5
  clamp: [0.0, 1.0]

metadata:
  category: pancha_mahapurusha
  classical_effects_tag: "commanding_personality, military_valor, physical_strength"
  variants:
    saravali_variant_notes: "Saravali Ch.35 v.8 allows aspect in kendra as alternative to occupancy; variant rule_id yoga.pancha_mahapurusha.ruchaka.saravali.variant handles this."
```

#### 3.2.2 Gaja Kesari Yoga (Raja/Chandra hybrid) — full YAML

**`src/josi/db/rules/yoga/raja/gaja_kesari_bphs.yaml`:**

```yaml
rule_id: yoga.raja.gaja_kesari.bphs
source_id: bphs
version: "1.0.0"
technique_family_id: yoga
output_shape_id: boolean_with_strength
citation: "BPHS Ch.37 v.5-6"
classical_names:
  en: "Gaja Kesari Yoga"
  sa_iast: "Gajakesarī Yoga"
  sa_devanagari: "गजकेसरी योग"
  ta: "கஜ கேசரி யோகம்"
  hi: "गजकेसरी योग"
effective_from: "2026-01-01T00:00:00Z"
effective_to: null

activation:
  predicate:
    op: angular_distance
    from: moon
    to: jupiter
    unit: sign_houses
    allowed_distances: [0, 3, 6, 9]      # Jupiter in kendra from Moon (0=conjunct, 3=4th, 6=7th, 9=10th)
    # Note: BPHS verse 5 specifies kendra from Moon; some commentators accept from Lagna as alternate.

strength:
  formula: weighted_sum
  terms:
    - weight: 0.3
      factor:
        op: planet_dignity_score
        planet: jupiter
        scores:
          exalted: 1.0
          own_sign: 0.85
          friendly_sign: 0.7
          neutral_sign: 0.55
          enemy_sign: 0.35
          debilitated: 0.1
    - weight: 0.25
      factor:
        op: planet_dignity_score
        planet: moon
        scores:
          exalted: 1.0
          own_sign: 0.85
          friendly_sign: 0.7
          neutral_sign: 0.55
          enemy_sign: 0.35
          debilitated: 0.1
    - weight: 0.25
      factor:
        op: lookup
        table:
          conjunction: 1.0      # Jupiter + Moon conjunct
          opposition: 0.75      # 7th from each other
          quadrant_trine: 0.9   # 4th/10th
        key:
          op: angular_distance_name
          from: moon
          to: jupiter
    - weight: 0.2
      factor:
        op: afflictions_penalty
        planets: [jupiter, moon]
        penalty_per_malefic_conjunction: 0.15
        penalty_per_malefic_aspect: 0.1
        base_score: 1.0
  clamp: [0.0, 1.0]

metadata:
  category: raja
  also_category: chandra
  classical_effects_tag: "fame, intelligence, respect_from_peers, longevity"
  variants:
    phaladeepika_note: "Phaladeepika 6.11 additionally requires Jupiter and Moon unafflicted; encoded as strength penalty, not activation gate."
```

#### 3.2.3 Lakshmi Yoga (Dhana) — full YAML

**`src/josi/db/rules/yoga/dhana/lakshmi_phaladeepika.yaml`:**

```yaml
rule_id: yoga.dhana.lakshmi.phaladeepika
source_id: phaladeepika
version: "1.0.0"
technique_family_id: yoga
output_shape_id: boolean_with_strength
citation: "Phaladeepika Ch.15 v.4"
classical_names:
  en: "Lakshmi Yoga"
  sa_iast: "Lakṣmī Yoga"
  sa_devanagari: "लक्ष्मी योग"
  ta: "லக்ஷ்மி யோகம்"

activation:
  predicate:
    op: all_of
    clauses:
      - op: house_lord_sign_status
        house: 9
        reference: lagna
        status_any_of: [own_sign, exalted]
      - op: house_lord_in_house_group
        house: 9
        reference: lagna
        houses: [1, 4, 7, 10]    # kendra
      - op: planet_strength
        planet: venus
        strength_metric: shadbala
        minimum: 0.55             # "Venus strong" — operationalized via existing Shadbala

strength:
  formula: weighted_sum
  terms:
    - weight: 0.4
      factor:
        op: house_lord_dignity_score
        house: 9
        reference: lagna
        scores:
          exalted: 1.0
          own_sign: 0.85
    - weight: 0.25
      factor:
        op: house_lord_house_strength
        house: 9
        reference: lagna
        placement_in: [1, 4, 7, 10]
        scores:
          "1": 1.0
          "10": 0.95
          "7": 0.85
          "4": 0.75
    - weight: 0.25
      factor:
        op: planet_strength
        planet: venus
        strength_metric: shadbala_normalized
    - weight: 0.1
      factor:
        op: afflictions_penalty
        planets: [venus]
        penalty_per_malefic_conjunction: 0.1
        base_score: 1.0
  clamp: [0.0, 1.0]

metadata:
  category: dhana
  classical_effects_tag: "wealth, fortune, marital_happiness, progeny"
  variants:
    bphs_variant_notes: "BPHS 43.5 has a narrower form requiring Venus specifically in a kendra. Encoded as a separate rule yoga.dhana.lakshmi.bphs if/when author prefers that lineage."
```

#### 3.2.4 Kemadruma Yoga (Dushta/Chandra) — full YAML

**`src/josi/db/rules/yoga/dushta/kemadruma_bphs.yaml`:**

```yaml
rule_id: yoga.dushta.kemadruma.bphs
source_id: bphs
version: "1.0.0"
technique_family_id: yoga
output_shape_id: boolean_with_strength
citation: "BPHS Ch.38 v.5 (definition); BPHS Ch.38 v.6 (cancellations)"
classical_names:
  en: "Kemadruma Yoga"
  sa_iast: "Kemadruma Yoga"
  sa_devanagari: "केमद्रुम योग"
  ta: "கேமத்ரும யோகம்"

activation:
  predicate:
    op: all_of
    clauses:
      # Definition (BPHS 38.5): no planet in 2nd or 12th from Moon, excluding Sun, Rahu, Ketu.
      - op: no_planet_in_house_from
        excluded_planets: [sun, rahu, ketu]
        houses: [2, 12]
        reference: moon
      # Strict form also requires Moon alone in its own sign (no conjunction).
      - op: no_planet_conjunct
        planet: moon
        excluded_planets: [sun, rahu, ketu]
      # BPHS 38.6 cancellations (encoded as NEGATED clauses):
      - op: not
        clause:
          op: any_of
          clauses:
            - op: planet_in_kendra
              planet: moon
              reference: lagna
            - op: planet_receives_aspect
              planet: moon
              from_any_of: [jupiter]      # benefic aspect on Moon
            - op: planet_sign_status
              planet: moon
              status_any_of: [exalted, own_sign]
            - op: all_planets_in_kendra_from_lagna:
                count_minimum: 3           # classical "many planets in kendra" variant cancellation

strength:
  formula: weighted_sum
  terms:
    - weight: 0.5
      factor:
        op: lookup
        key:
          op: moon_sign_status
        table:
          debilitated: 1.0
          enemy_sign: 0.8
          neutral_sign: 0.6
          friendly_sign: 0.4
          own_sign: 0.0      # cancellation — rule shouldn't activate anyway; defensive
          exalted: 0.0
    - weight: 0.3
      factor:
        op: afflictions_on_moon_penalty_inverted
        base_score: 0.5
        per_malefic_aspect_bonus: 0.2       # for a dushta yoga, more affliction = more strength
    - weight: 0.2
      factor:
        op: lookup
        key:
          op: birth_nakshatra_pada
        table:
          # Classical cross-reference: certain nakshatras intensify Kemadruma (regional tradition; weak).
          "default": 0.5
  clamp: [0.0, 1.0]

metadata:
  category: dushta
  classical_effects_tag: "isolation, financial_instability, emotional_distress"
  cancellation_rule_inline: true
  note: "Activation predicate already encodes cancellation clauses per BPHS 38.6. If canceled, active=false."
```

#### 3.2.5 Neecha Bhanga Raja Yoga — full YAML

**`src/josi/db/rules/yoga/raja/neecha_bhanga_rajayoga_bphs.yaml`:**

```yaml
rule_id: yoga.raja.neecha_bhanga.bphs
source_id: bphs
version: "1.0.0"
technique_family_id: yoga
output_shape_id: boolean_with_strength
citation: "BPHS Ch.39 v.1-10"
classical_names:
  en: "Neecha Bhanga Raja Yoga"
  sa_iast: "Nīcabhaṅga Rājayoga"
  sa_devanagari: "नीचभङ्ग राजयोग"
  ta: "நீசபங்க ராஜ யோகம்"

activation:
  # Applies per-debilitated planet. Emits one compute row per (chart, debilitated planet) where conditions met.
  iterate_over:
    source: debilitated_planets       # all planets currently debilitated in the chart
    as: P
  predicate:
    op: all_of
    clauses:
      - op: any_of                    # at least ONE of the 4 classical cancellation conditions
        clauses:
          # Condition 1 (BPHS 39.2): lord of debilitation sign is in a kendra from Lagna or Moon.
          - op: planet_in_kendra
            planet:
              op: lord_of_sign
              sign:
                op: debilitation_sign_of
                planet: "{P}"
            reference_any_of: [lagna, moon]
          # Condition 2 (BPHS 39.3): lord of exaltation sign of P is in a kendra from Lagna or Moon.
          - op: planet_in_kendra
            planet:
              op: lord_of_sign
              sign:
                op: exaltation_sign_of
                planet: "{P}"
            reference_any_of: [lagna, moon]
          # Condition 3 (BPHS 39.4): planet in debilitation is aspected by its own dispositor or the exalted-sign lord.
          - op: planet_receives_aspect
            planet: "{P}"
            from_any_of:
              - { op: lord_of_sign, sign: { op: sign_of_planet, planet: "{P}" } }
              - { op: lord_of_sign, sign: { op: exaltation_sign_of, planet: "{P}" } }
          # Condition 4 (BPHS 39.5): planet in debilitation is exchanging signs with another debilitated planet.
          - op: parivartana
            planet: "{P}"
            partner_status: debilitated

strength:
  formula: weighted_sum
  terms:
    - weight: 0.4
      factor:
        op: cancellation_count
        source: active_cancellation_conditions_for_P
        base_score: 0.5
        per_additional_condition_bonus: 0.2
    - weight: 0.3
      factor:
        op: planet_in_house_group_score
        planet: "{P}"
        scores:
          kendra: 1.0
          trikona: 0.9
          upachaya: 0.75
          dusthana: 0.3
    - weight: 0.3
      factor:
        op: planet_strength
        planet: "{P}"
        strength_metric: shadbala_normalized
  clamp: [0.0, 1.0]

metadata:
  category: raja
  also_category: cancellation
  classical_effects_tag: "rags_to_riches, late_blooming_success, triumph_over_adversity"
  per_planet_emission: true           # one row per debilitated planet meeting conditions
```

### 3.3 Remaining 55 yogas — predicate summaries

For each, the brief predicate structure as it will appear in the YAML. Complete files authored during T-E4a.3.

**Pancha Mahapurusha (4 remaining):**
- **Bhadra** (`yoga.pancha_mahapurusha.bhadra.bphs`): Mercury in {own_sign: gemini, virgo; exalted: virgo} AND in kendra. Citation BPHS 36.5-6.
- **Hamsa** (`yoga.pancha_mahapurusha.hamsa.bphs`): Jupiter in {own: sag, pisces; exalted: cancer} AND kendra. BPHS 36.7-9.
- **Malavya** (`yoga.pancha_mahapurusha.malavya.bphs`): Venus in {own: taurus, libra; exalted: pisces} AND kendra. BPHS 36.10-12.
- **Sasa** (`yoga.pancha_mahapurusha.sasa.bphs`): Saturn in {own: capricorn, aquarius; exalted: libra} AND kendra. BPHS 36.13-16.

**Raja (14 remaining; see §3.1.2 for full list):**
- **Amala** (`yoga.raja.amala.bphs`): at least one natural benefic (Jupiter, Venus, unafflicted Mercury, waxing Moon) in 10th from Moon AND no malefic in 10th from Moon. BPHS 37.14.
- **Adhi** (`yoga.raja.adhi.bphs`): benefics (Jupiter, Venus, Mercury) in 6, 7, AND 8 from Moon (all three positions covered; classical strict). BPHS 37.15-17.
- **Chamara** (`yoga.raja.chamara.phaladeepika`): Lagna lord exalted in a kendra AND aspected by Jupiter. Phaladeepika 6.12.
- **Dhenu** (`yoga.raja.dhenu.phaladeepika`): 2nd lord in kendra from Lagna; planets in 2nd house. Phaladeepika 6.14.
- **Shankha** (`yoga.raja.shankha.phaladeepika`): benefics in 5 AND 6 from Lagna AND 10th lord in 6/8/12. Phaladeepika 6.32.
- **Bheri** (`yoga.raja.bheri.phaladeepika`): Jupiter in {1,4,10} from Lagna OR from 7th lord, AND Venus strong. Phaladeepika 6.29.
- **Viparita Raja — Harsha** (`yoga.raja.viparita_harsha.bphs`): 6th lord in {6,8,12}, no conjunction with benefic. BPHS 37.28.
- **Viparita Raja — Sarala** (`yoga.raja.viparita_sarala.bphs`): 8th lord in {6,8,12}, no conjunction with benefic. BPHS 37.29.
- **Viparita Raja — Vimala** (`yoga.raja.viparita_vimala.bphs`): 12th lord in {6,8,12}, no conjunction with benefic. BPHS 37.30.
- **Dharma-Karmadhipati** (`yoga.raja.dharma_karmadhipati.bphs`): 9th lord + 10th lord in conjunction OR mutual aspect OR parivartana (sign exchange). BPHS 37.9-10.
- **Kendra-Trikona Raja (generic)** (`yoga.raja.kendra_trikona.bphs`): lord of any kendra (4,7,10 — Lagna itself is both) + lord of any trikona (5,9) in conjunction OR mutual aspect OR parivartana. Emitted per (kendra_house, trikona_house) pair. BPHS 37.6-8.
- **Lagna-5 Raja** (`yoga.raja.lagna_5.bphs`): Lagna lord + 5th lord in conjunction/aspect/parivartana. BPHS 37.8.
- **Lagna-9 Raja** (`yoga.raja.lagna_9.bphs`): Lagna lord + 9th lord in conjunction/aspect/parivartana. BPHS 37.8.
- **Kahala** (`yoga.raja.kahala.phaladeepika`): 4th lord + 9th lord in kendra (each or combined) AND Lagna lord shadbala ≥ 0.5. Phaladeepika 6.10.

**Dhana (10):**
- **Dhana Yoga classical** (`yoga.dhana.classical_2_11.phaladeepika`): 2nd lord + 11th lord in conjunction/aspect/exchange. Phaladeepika 15.2.
- **Kubera** (`yoga.dhana.kubera.bphs`): (11th lord in 2nd) OR (2nd lord in 11th) AND benefic association (conjunction or aspect by benefic). BPHS 43.6.
- **Dhana Lagna-2** (`yoga.dhana.lagna_2.phaladeepika`): Lagna lord + 2nd lord in conjunction. Phaladeepika 15.2 sub-case.
- **Dhana Lagna-11** (`yoga.dhana.lagna_11.phaladeepika`): Lagna lord + 11th lord in conjunction/aspect. Phaladeepika 15.2 sub-case.
- **Dhana 5-9** (`yoga.dhana.5_9.bphs`): 5th + 9th lords in conjunction/aspect. BPHS 43.3.
- **Dhana 5-11** (`yoga.dhana.5_11.phaladeepika`): 5th + 11th lords in conjunction/aspect. Phaladeepika 15.3.
- **Dhana 2-9** (`yoga.dhana.2_9.bphs`): 2nd + 9th lords in conjunction/aspect. BPHS 43.4.
- **Mahalakshmi** (`yoga.dhana.mahalakshmi.phaladeepika`): Venus AND Moon in kendra from Lagna AND both unafflicted. Phaladeepika 15.6.
- **Guru-Mangala** (`yoga.dhana.guru_mangala.saravali`): Jupiter + Mars in conjunction/aspect, both dignified (in own/exalted/friendly sign). Saravali 42.5.

**Chandra (9 remaining; #40 Gaja Kesari cross-referenced from Raja):**
- **Sunapha** (`yoga.chandra.sunapha.bphs`): any planet in 2nd from Moon, excluding Sun, Rahu, Ketu. BPHS 38.2.
- **Anapha** (`yoga.chandra.anapha.bphs`): any planet in 12th from Moon, excluding Sun, Rahu, Ketu. BPHS 38.3.
- **Durudhara** (`yoga.chandra.durudhara.bphs`): planets in 2nd AND 12th from Moon (excluding Sun). BPHS 38.4.
- **Kemadruma** (`yoga.chandra.kemadruma.bphs`): cross-ref to #46 in dushta — same rule_id. Classification tag `category: [chandra, dushta]`.
- **Adhi Chandra** (`yoga.chandra.adhi.bphs`): benefics in all three of {6,7,8} from Moon. BPHS 38.7-8.
- **Vasumati** (`yoga.chandra.vasumati.saravali`): benefics in upachaya {3,6,10,11} from Moon. Saravali 13.4.
- **Pushkala** (`yoga.chandra.pushkala.saravali`): (dispositor of Moon) + Lagna lord in mutual aspect OR conjunction in kendra with Moon. Saravali 13.11.
- **Shakata** (`yoga.chandra.shakata.saravali`): Moon in {6,8,12} from Jupiter. Saravali 13.9. Variant: cancellation if Moon is in own/exalted sign (see #59).
- **Chandra-Mangala** (`yoga.chandra.chandra_mangala.phaladeepika`): Moon + Mars in conjunction OR mutual aspect. Phaladeepika 6.22.

**Surya (5):**
- **Vesi** (`yoga.surya.vesi.bphs`): any planet in 2nd from Sun, excluding Moon, Rahu, Ketu. BPHS 38.12.
- **Vosi** (`yoga.surya.vosi.bphs`): any planet in 12th from Sun, excluding Moon, Rahu, Ketu. BPHS 38.13.
- **Ubhayachari** (`yoga.surya.ubhayachari.bphs`): planets in 2nd AND 12th from Sun. BPHS 38.14.
- **Budha-Aditya** (`yoga.surya.budha_aditya.bphs`): Sun + Mercury conjunct within 10° (classical orb). BPHS 38.20 + Phaladeepika 6.27 variant. Strength penalty if Mercury is combust (within 14°).
- **Surya Kemadruma** (`yoga.surya.surya_kemadruma.saravali`): no planet in 1st, 2nd, or 12th from Sun. Saravali 14.6 regional variant.

**Dushta (15; several cross-referenced):**
- **Kemadruma** → same rule as #34. `category: [chandra, dushta]`.
- **Shakata** → same as #38. `category: [chandra, dushta]`.
- **Angaraka** (`yoga.dushta.angaraka.saravali`): Mars + Rahu OR Mars + Ketu conjunction. Saravali 38.11.
- **Pitra Dosha** (`yoga.dushta.pitra_dosha.classical`): (Sun + Rahu conjunction) OR (Sun + Ketu conjunction) OR (Sun in 9th house AND afflicted by malefic aspect). BPHS 42.6.
- **Kaal Sarp** (`yoga.dushta.kaal_sarp.phaladeepika`): all 7 classical planets (Sun through Saturn) strictly between Rahu and Ketu in zodiacal order. Emits subtype name based on axis (Ananta if Rahu in 1st and Ketu in 7th, etc. — full 8-subtype lookup table). Phaladeepika 14.18-21.
- **Daridra** (`yoga.dushta.daridra.bphs`): 11th lord in 12th house. BPHS 42.9.
- **Guru Chandala** (`yoga.dushta.guru_chandala.saravali`): Jupiter + Rahu OR Jupiter + Ketu conjunction. Saravali 38.13.
- **Vish** (`yoga.dushta.vish.saravali`): Moon + Saturn conjunction OR mutual 7th aspect. Saravali 13.21.
- **Graha Yuddha** (`yoga.dushta.graha_yuddha.bphs`): two planets within 1° longitude, excluding Sun-Moon and Rahu-Ketu pairs. Emit per-pair, with winner/loser per BPHS 27 rules (northern planet wins if latitude differs; otherwise brighter wins). BPHS Ch. 27.
- **Balarishta** (`yoga.dushta.balarishta.bphs`): Moon in {6,8,12} AND hemmed by malefics AND no benefic aspect. BPHS 42.3-5.
- **Arishta (chandra-weak)** (`yoga.dushta.arishta_chandra.bphs`): Moon in {6,8,12} AND aspected by malefic AND no benefic aspect. BPHS 42.5.
- **Kuja Dosha** (`yoga.dushta.kuja_dosha.phaladeepika`): **B2C default (per DECISIONS §6.5 E25 Q2 revised 2026-04-22):** Sevvai in {2,4,7,8,12} from Lagna (5 houses, Lagna-only single-reference). **Astrologer toggles (off by default):** add 1st-house inclusion + Chandran-reference + Sukran-reference for lineages that require them. Phaladeepika 14.12 canonical 3-reference list retained as astrologer-enable but not active by default (not in current Tamil Parashari practice). Phaladeepika 14.12.
- **Kuja Dosha Cancellation** (`yoga.cancellation.kuja_dosha_bhanga.classical_synthesis`): Kuja Dosha canceled when Mars in own/exalted OR aspected by Jupiter OR Mars in Pisces/Cancer with Moon. Classical synthesis after B.V. Raman.
- **Sakata Bhanga** (`yoga.cancellation.sakata_bhanga.classical_synthesis`): Shakata canceled when Moon in own/exalted sign OR aspected by benefic (Jupiter, Venus, unafflicted Mercury). Classical synthesis.
- **Neecha Bhanga Raja Yoga** → full YAML in §3.2.5 above.

### 3.4 Predicate vocabulary extensions

The F6 base predicate vocabulary (`op: planet_in_house`, `op: conjunction`, etc.) is assumed. This PRD **extends** the vocabulary with the following, all implemented in `src/josi/services/classical/yoga/predicates.py`:

| Predicate `op` | Signature | Notes |
|---|---|---|
| `planet_sign_status` | `planet, status_any_of: [own_sign, exalted, debilitated, enemy_sign, friendly_sign, neutral_sign]` | Requires sign dignity table |
| `planet_in_house_group` | `planet, houses: [int], reference: lagna | moon | sun` | Membership test |
| `planet_in_kendra` | `planet, reference, reference_any_of?` | Sugar for houses=[1,4,7,10] |
| `planet_in_trikona` | `planet, reference` | Sugar for houses=[1,5,9] |
| `angular_distance` | `from, to, unit: sign_houses | degrees, allowed_distances` | Sign-based is modular 12 |
| `angular_distance_name` | `from, to` | Returns string like "conjunction", "opposition", "quadrant_trine" |
| `no_planet_in_house_from` | `houses, reference, excluded_planets?` | Negative spatial check |
| `no_planet_conjunct` | `planet, excluded_planets?` | |
| `all_planets_in_kendra_from_lagna` | `count_minimum` | Occupancy count |
| `planet_receives_aspect` | `planet, from_any_of: [planet | dynamic_expr]` | Drishti rules (classical sign-based + special) |
| `house_lord_sign_status` | `house, reference, status_any_of` | |
| `house_lord_in_house_group` | `house, reference, houses` | |
| `planet_strength` | `planet, strength_metric: shadbala | shadbala_normalized, minimum?` | Integrates existing StrengthCalculator |
| `parivartana` | `planet, partner_status?, partner_house?` | Sign exchange check |
| `lord_of_sign` / `lord_of_house` | `sign` or `house, reference` | Expressions returning a planet (nested usable) |
| `debilitation_sign_of` / `exaltation_sign_of` / `sign_of_planet` | `planet` | Returns sign |
| `iterate_over` | `source: debilitated_planets | all_planets | benefic_planets, as: var_name` | Rule-level iteration (emits one row per iteration) |
| `cancellation_count` | `source: active_cancellation_conditions_for_P` | Counts which cancellation clauses evaluated true for this iteration |
| `moon_sign_status` | — | Computed: returns current Moon sign dignity |
| `any_of`, `all_of`, `not` | Logical combinators | F6 base |
| `lookup` | `key: expression, table: {...}` | Map-based lookup |

### 3.5 Strength formula primitives

Strength formulas are built from:

- `weighted_sum` with list of `terms` (each a weight + factor expression)
- `product` (multiplies factors)
- `conditional` (if-then-else)
- `lookup` (table-based)
- `clamp` (pin to range)
- Raw scalar constants

Factor expressions reuse the predicate vocabulary above for lookups (e.g., `planet_dignity_score`, `house_strength_score`, `afflictions_penalty`, `combustion_penalty`).

### 3.6 Engine architecture

```
YogaEngine(BaseClassicalEngine)
  ├─ load_rules(family='yoga') → list[YogaRule]
  ├─ evaluate_rule(rule, chart_state) → BooleanWithStrengthResult
  │     ├─ predicate_evaluator.evaluate(rule.activation.predicate, chart_state)
  │     └─ if active: strength_evaluator.evaluate(rule.strength, chart_state)
  ├─ handle iterate_over → emit multiple rows (per-planet instances)
  └─ emit one technique_compute row per (chart, rule_id, source_id, rule_version)
```

Predicate evaluator is a dispatch table keyed by `op`, implemented in `predicates.py` with pure functions. Strength evaluator similar in `strength_formulas.py`.

Chart state provided once to the engine via a `ChartState` dataclass containing:
- Planet positions (sidereal + tropical)
- Sign dignity per planet
- House positions (from Lagna, Moon, Sun)
- Aspect matrix (7×9 classical sign-based drishti + Mars/Jupiter/Saturn special)
- Dispositor graph
- Shadbala values (if computed)
- Nakshatra + pada
- Tithi + paksha
- Lord-of-house map for each reference point

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| Boolean only or boolean + strength? | Both | Classical practice; strength enables UX nuance |
| Kemadruma cancellation: inline in predicate or separate cancellation rule? | Inline for #34/#46; separate for #58 (Kuja Dosha Bhanga) and #59 (Sakata Bhanga) | Kemadruma cancellations are definitional (BPHS 38.6); Kuja/Sakata cancellations are frequently applied independently in readings |
| When BPHS and Saravali disagree, which ships as default? | BPHS | Primary Parashari canon |
| Yoga cross-categorization (Gaja Kesari is Raja + Chandra) — dedupe or duplicate rule_ids? | Dedupe: one rule, multiple `category` tags | Single compute row per rule; UI/AI layer handles categorization |
| Per-planet iteration (Neecha Bhanga): one row or many? | Many — one per qualifying debilitated planet | Classical practice names "Neecha Bhanga for Mars," "Neecha Bhanga for Saturn" etc. |
| Strength threshold for "significant" yoga | 0.5 | Default mid-point; UX can expose threshold config |
| Combust planet affects strength of yoga involving it? | Yes, penalty in strength formula where relevant | Classical mention in BPHS Ch.36 (Pancha Mahapurusha strength is reduced by combustion) |
| Debilitated planet participating in a yoga — still active? | Active flag yes; strength penalty applies | Classical: presence still counts, strength differs |
| How to handle Kaal Sarp's 8 subtypes? | Single rule; subtype emitted in `details.subtype` | Rule is one check; subtype is metadata |
| Aspect rules: classical sign-based only, or include Jaimini argala / rashi drishti? | Classical sign-based only in v1 (graha drishti: Mars 4/8, Jupiter 5/9, Saturn 3/10; all planets 7th) | Scope; Jaimini in E3 |
| Mercury "benefic" classification (ambiguous by classical) | Benefic when unafflicted; malefic when conjunct/aspected by malefic | BPHS 2.21 |
| Moon "benefic" classification | Benefic when waxing (shukla paksha, 5 tithis from full Moon); neutral otherwise | BPHS 2.20 |

## 5. Component Design

### 5.1 New modules

```
src/josi/services/classical/yoga/
├── __init__.py
├── yoga_engine.py                  # main ClassicalEngine implementation
├── predicates.py                   # predicate evaluator (dispatch table)
├── strength_formulas.py            # strength evaluator
├── chart_state.py                  # ChartState dataclass + builder
├── dignity_tables.py               # exaltation/debilitation, ownership, mooltrikona
└── aspects.py                      # classical drishti computation (7×12 matrix)

src/josi/db/rules/yoga/
├── pancha_mahapurusha/
│   ├── ruchaka_bphs.yaml
│   ├── bhadra_bphs.yaml
│   ├── hamsa_bphs.yaml
│   ├── malavya_bphs.yaml
│   └── sasa_bphs.yaml
├── raja/
│   ├── gaja_kesari_bphs.yaml
│   ├── amala_bphs.yaml
│   ├── adhi_bphs.yaml
│   ├── chamara_phaladeepika.yaml
│   ├── dhenu_phaladeepika.yaml
│   ├── shankha_phaladeepika.yaml
│   ├── bheri_phaladeepika.yaml
│   ├── viparita_harsha_bphs.yaml
│   ├── viparita_sarala_bphs.yaml
│   ├── viparita_vimala_bphs.yaml
│   ├── dharma_karmadhipati_bphs.yaml
│   ├── kendra_trikona_bphs.yaml
│   ├── lagna_5_bphs.yaml
│   ├── lagna_9_bphs.yaml
│   ├── kahala_phaladeepika.yaml
│   └── neecha_bhanga_rajayoga_bphs.yaml
├── dhana/
│   ├── classical_2_11_phaladeepika.yaml
│   ├── lakshmi_phaladeepika.yaml
│   ├── kubera_bphs.yaml
│   ├── lagna_2_phaladeepika.yaml
│   ├── lagna_11_phaladeepika.yaml
│   ├── 5_9_bphs.yaml
│   ├── 5_11_phaladeepika.yaml
│   ├── 2_9_bphs.yaml
│   ├── mahalakshmi_phaladeepika.yaml
│   └── guru_mangala_saravali.yaml
├── chandra/
│   ├── sunapha_bphs.yaml
│   ├── anapha_bphs.yaml
│   ├── durudhara_bphs.yaml
│   ├── kemadruma_bphs.yaml         # referenced by dushta too
│   ├── adhi_chandra_bphs.yaml
│   ├── vasumati_saravali.yaml
│   ├── pushkala_saravali.yaml
│   ├── shakata_saravali.yaml       # referenced by dushta too
│   └── chandra_mangala_phaladeepika.yaml
├── surya/
│   ├── vesi_bphs.yaml
│   ├── vosi_bphs.yaml
│   ├── ubhayachari_bphs.yaml
│   ├── budha_aditya_bphs.yaml
│   └── surya_kemadruma_saravali.yaml
├── dushta/
│   ├── angaraka_saravali.yaml
│   ├── pitra_dosha_classical.yaml
│   ├── kaal_sarp_phaladeepika.yaml
│   ├── daridra_bphs.yaml
│   ├── guru_chandala_saravali.yaml
│   ├── vish_saravali.yaml
│   ├── graha_yuddha_bphs.yaml
│   ├── balarishta_bphs.yaml
│   ├── arishta_chandra_bphs.yaml
│   └── kuja_dosha_phaladeepika.yaml
└── cancellation/
    ├── kuja_dosha_bhanga_classical_synthesis.yaml
    └── sakata_bhanga_classical_synthesis.yaml

tests/golden/charts/yoga/
├── chart_01_famous_person_a.yaml
├── ...
├── chart_20_famous_person_t.yaml     # 20 charts covering all 60 yogas
```

### 5.2 Data model additions

No new tables. 60 new rows in `classical_rule` loaded by F6.

### 5.3 Engine interface

```python
# src/josi/services/classical/yoga/yoga_engine.py

class YogaActivationResult(BaseModel):
    rule_id: str
    active: bool
    strength: float             # 0..1
    details: dict = Field(default_factory=dict)
    citation: str
    iteration_key: str | None = None    # for iterate_over rules (e.g., "mars" for per-debilitated-planet)

class YogaEngine(BaseClassicalEngine):
    technique_family_id = "yoga"

    async def compute_for_source(
        self, session: AsyncSession, chart_id: UUID, source_id: str,
        rule_ids: list[str] | None = None,
    ) -> list[TechniqueComputeRow]:
        chart_state = await self._build_chart_state(chart_id)
        rules = await self._load_rules(source_id, rule_ids)
        rows = []
        for rule in rules:
            results = self._evaluate_rule(rule, chart_state)   # 0..N results (iteration)
            for result in results:
                rows.append(TechniqueComputeRow(
                    rule_id=rule.rule_id,
                    source_id=rule.source_id,
                    rule_version=rule.version,
                    result=BooleanWithStrengthResult(
                        active=result.active,
                        strength=result.strength,
                        details=result.details,
                        reason=self._explain(rule, result),
                    ),
                ))
        return rows

    def _evaluate_rule(self, rule, chart_state) -> list[YogaActivationResult]: ...
    def _explain(self, rule, result) -> str: ...
```

### 5.4 REST API

```
GET /api/v1/yogas/{chart_id}?category=raja&strength_min=0.5
GET /api/v1/yogas/{chart_id}?active_only=true

Response:
{
  "success": true,
  "data": {
    "yogas": [
      {
        "rule_id": "yoga.raja.gaja_kesari.bphs",
        "name_en": "Gaja Kesari Yoga",
        "name_sa_iast": "Gajakesarī Yoga",
        "category": ["raja", "chandra"],
        "active": true,
        "strength": 0.82,
        "citation": "BPHS Ch.37 v.5-6",
        "reason": "Jupiter in 10th from Moon (kendra); Jupiter in Taurus (neutral); Moon in Leo (friendly); no major afflictions."
      },
      ...
    ],
    "summary": { "total_active": 7, "by_category": { "raja": 3, "dhana": 2, ... } }
  },
  "errors": null
}
```

### 5.5 AI tool-use

```python
@tool
def get_yoga_summary(
    chart_id: str,
    strategy: StrategyId = "D_hybrid",
    min_confidence: float = 0.0,
    min_strength: float = 0.5,
    categories: list[Literal["pancha_mahapurusha", "raja", "dhana", "chandra", "surya", "dushta", "cancellation"]] | None = None,
) -> YogaSummary:
    """Returns list of active yogas meeting confidence + strength thresholds,
       aggregated per the requested strategy. Each yoga includes citation, category,
       strength, and classical-name translations."""
```

## 6. User Stories

### US-E4a.1: As an end user, I want to see "my active yogas" on my dashboard
**Acceptance:** Dashboard widget queries `/api/v1/yogas/{chart_id}?active_only=true&strength_min=0.5` and displays up to 5 strongest, with Sanskrit + English names and one-line descriptions.

### US-E4a.2: As an end user asking "what makes me wealthy in my chart?", I get dhana yogas with citations
**Acceptance:** AI chat tool `get_yoga_summary(categories=['dhana'])` returns named yogas with per-yoga citation; LLM wrapper synthesizes natural text.

### US-E4a.3: As an astrologer, I want to see "all active yogas including weak ones"
**Acceptance:** `?strength_min=0.0` returns full list; default `0.5` hides weak.

### US-E4a.4: As a classical scholar, I can review a yoga's source citation and verify against the text
**Acceptance:** Each yoga response contains `citation` field referencing specific chapter and verse; YAML rule has the same citation.

### US-E4a.5: As an engineer, adding a new yoga requires only authoring YAML
**Acceptance:** New rule YAML file added → F6 loader picks it up → engine evaluates it on next compute → appears in API response. Zero Python change.

### US-E4a.6: As a classical advisor, I can ship a Saravali variant of Ruchaka
**Acceptance:** Second rule YAML `yoga.pancha_mahapurusha.ruchaka.saravali.variant` with `source_id: saravali` coexists; both evaluated; aggregation strategy combines per user preference.

### US-E4a.7: As an engineer, I want to verify a famous chart (e.g., Gandhi per B.V. Raman *Notable Horoscopes* Ch.5) shows the classical-cited yogas
**Acceptance:** Golden fixture for Gandhi lists expected active yogas (Raj Yoga, Dhan Yoga, Pancha Mahapurusha X); test verifies all listed yogas show `active=true`.

### US-E4a.8: As an AI chat user asking "do I have Kaal Sarp Yoga", I get a clear yes/no + subtype if yes
**Acceptance:** Response includes `active` and `details.subtype` (e.g., "Ananta"); citation Phaladeepika 14.18-21.

## 7. Tasks

### T-E4a.1: Build chart-state builder
- **Definition:** `ChartState` dataclass + async builder that gathers planet positions, dignities, house placements, aspect matrix, dispositor graph, Shadbala, nakshatra, paksha from existing Josi services.
- **Acceptance:** Unit tests: for a known chart, all fields populate correctly; performance < 50 ms per chart.
- **Effort:** 3 days
- **Depends on:** existing `astrology_service.py`, `strength_calculator.py`

### T-E4a.2: Build predicate evaluator
- **Definition:** Dispatch-table evaluator for all ~20 predicate `op`s listed in §3.4. Pure functions returning booleans. Supports `iterate_over` with `{P}` variable substitution.
- **Acceptance:** Each `op` has ≥3 unit tests (typical, edge, empty); dispatch is extensible.
- **Effort:** 5 days
- **Depends on:** T-E4a.1

### T-E4a.3: Author all 60 yoga YAMLs
- **Definition:** Write 60 rule files across 7 subdirectories per §3.1–3.3. Each file includes citation, classical_names (en, sa_iast, sa_devanagari, ta), activation predicate, strength formula, category metadata.
- **Acceptance:** All 60 YAML parse via F6 loader; classical advisor PR review sign-off; content hashes stable; cross-referenced rules (Gaja Kesari, Kemadruma, Shakata) have single canonical file.
- **Effort:** 7 days (the content core)
- **Depends on:** F6 + T-E4a.2 (to know which predicate ops are available)

### T-E4a.4: Build strength evaluator
- **Definition:** Evaluator for `weighted_sum`, `product`, `conditional`, `lookup`, `clamp` with factor sub-expressions.
- **Acceptance:** Unit tests: Ruchaka-like formula produces expected scores for sample inputs; clamp behavior correct; edge cases (zero weights, empty terms).
- **Effort:** 2 days
- **Depends on:** T-E4a.2

### T-E4a.5: Implement `YogaEngine`
- **Definition:** Full engine per §5.3. Loads rules, builds chart state once, evaluates each rule, handles iterate_over, emits compute rows idempotently.
- **Acceptance:** Integration test: for a known chart, all 60 yogas evaluate; results match golden fixture.
- **Effort:** 3 days
- **Depends on:** T-E4a.2, T-E4a.3, T-E4a.4

### T-E4a.6: Author 20 golden chart fixtures
- **Definition:** 20 charts covering all 60 yogas at least once (some yogas share charts; famous charts from B.V. Raman *Notable Horoscopes* preferred, supplemented with synthetic charts for rare yogas). Each fixture lists expected active yogas with expected strength ranges.
- **Acceptance:** Fixtures parse; every yoga appears `active=true` in ≥1 fixture and `active=false` in ≥1 fixture; 100% of 60 yogas covered; classical-advisor signed.
- **Effort:** 5 days (chart selection + verification is intensive)
- **Depends on:** T-E4a.5

### T-E4a.7: Property tests (F17)
- **Definition:** Invariants: (a) deterministic — same chart → same output_hash, (b) all `active=true` results have `strength > 0`, (c) `strength ∈ [0, 1]` always, (d) `iterate_over` rules emit ≤ 9 rows (max planets), (e) cross-source variants of same yoga have overlapping activation on ≥80% of test charts.
- **Acceptance:** 1000 Hypothesis examples per invariant.
- **Effort:** 2 days
- **Depends on:** T-E4a.5

### T-E4a.8: REST endpoint + controller
- **Definition:** `GET /api/v1/yogas/{chart_id}` with `category`, `active_only`, `strength_min`, `source` query params.
- **Acceptance:** Shape validated; 4xx on bad params.
- **Effort:** 1 day
- **Depends on:** T-E4a.5

### T-E4a.9: AI tool `get_yoga_summary`
- **Definition:** Typed tool per §5.5; threads `strategy` through F8 aggregation layer.
- **Acceptance:** Integration test.
- **Effort:** 1 day
- **Depends on:** T-E4a.8

### T-E4a.10: Differential test vs Jagannatha Hora
- **Definition:** For 10 famous charts from *Notable Horoscopes*, compare Josi yoga list to JH yoga list. Acceptable divergence: classical variants + cross-source disagreement; flagged per yoga.
- **Acceptance:** Agreement ≥ 80% on activation (some JH yogas are outside our 60; some of ours JH doesn't report); strength within ±0.15 on agreed yogas.
- **Effort:** 3 days
- **Depends on:** T-E4a.6

### T-E4a.11: Documentation
- **Definition:** Add per-yoga Sanskrit names, English names, citation, and "what this means" one-liner to API docs. Update `CLAUDE.md` with yoga-engine architecture.
- **Acceptance:** API docs show all 60 yogas; classical advisor reviews English descriptions.
- **Effort:** 2 days
- **Depends on:** T-E4a.3

## 8. Unit Tests

### 8.1 Predicate evaluator (per `op`)

Sample; full suite covers all ~20 ops with ≥3 tests each.

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_planet_sign_status_own` | Mars in Aries | true for `{status_any_of: [own_sign]}` | Own sign |
| `test_planet_sign_status_exalted` | Mars in Capricorn | true for `{status_any_of: [exalted]}` | Exaltation |
| `test_planet_in_kendra_lagna` | Jupiter in 10th from Lagna | true | Kendra sugar |
| `test_planet_in_kendra_moon_reference` | Jupiter in 4th from Moon | true for `reference: moon` | Alternate reference |
| `test_angular_distance_conjunction` | Moon + Jupiter same sign | allowed_distances=[0] → true | Conjunction |
| `test_angular_distance_opposition` | Moon and Jupiter 180° apart in sign terms | allowed_distances=[6] → true | 7th |
| `test_no_planet_in_house_from` | empty 2nd-from-Moon excluding Sun/Rahu/Ketu | true for Kemadruma predicate | Absence |
| `test_parivartana_detected` | Mars in Gemini, Mercury in Aries | true | Sign exchange |
| `test_planet_receives_aspect_from_jupiter` | Moon in house 4, Jupiter in house 12 (9th aspect from Jupiter) | true (Jupiter's special 9th aspect) | Aspect rules |
| `test_iterate_over_debilitated_planets` | chart with Sun debilitated AND Mars debilitated | iteration emits 2 evaluations | Iteration |
| `test_house_lord_in_kendra` | 9th lord Jupiter in 10th (kendra) | true | Sugar |
| `test_nested_expression_lord_of_debilitation_sign_of` | Mars debilitated (sign Cancer), Cancer lord Moon in 4th | true for Moon in kendra check | Expression composition |

### 8.2 Strength evaluator

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_weighted_sum_basic` | weights [0.5, 0.5], factors [1.0, 0.5] | 0.75 | Formula |
| `test_weighted_sum_clamp_to_1` | sum computes to 1.3 | clamped 1.0 | Clamp |
| `test_lookup_default_branch` | key='unknown', table has 'default: 0.5' | 0.5 | Fallback |
| `test_conditional_branch` | condition true → value A else B | A | If-then |
| `test_combustion_penalty` | Mars within 17° of Sun | multiplier 0.5 applied | Combustion |

### 8.3 Per-yoga unit tests (5 representative; identical pattern for all 60)

#### Ruchaka
| Test name | Chart | Expected | Rationale |
|---|---|---|---|
| `test_ruchaka_active_mars_exalted_1st` | Mars in Capricorn 1st | active=true, strength > 0.9 | Exalted in Lagna (kendra) |
| `test_ruchaka_active_mars_own_4th` | Mars in Aries 4th | active=true, strength > 0.8 | Own + kendra |
| `test_ruchaka_inactive_mars_own_3rd` | Mars in Aries 3rd | active=false | Not kendra |
| `test_ruchaka_inactive_mars_debilitated_1st` | Mars in Cancer 1st | active=false | Debilitated — fails dignity clause |

#### Gaja Kesari
| Test name | Chart | Expected | Rationale |
|---|---|---|---|
| `test_gajakesari_moon_conjunct_jupiter` | Moon and Jupiter in Cancer | active=true | Conjunction = kendra-distance 0 |
| `test_gajakesari_7th_apart` | Moon in Aries, Jupiter in Libra | active=true | 7th apart = kendra |
| `test_gajakesari_5th_apart_inactive` | Moon in Aries, Jupiter in Leo | active=false | 5th not a kendra |
| `test_gajakesari_strength_reduced_by_debilitation` | Jupiter in Capricorn (debilitated), still in kendra from Moon | active=true, strength < 0.4 | Dignity penalty |

#### Lakshmi
| Test name | Chart | Expected | Rationale |
|---|---|---|---|
| `test_lakshmi_9thlord_exalted_in_kendra_strong_venus` | 9L Jupiter exalted in 4th (kendra), Venus shadbala=0.7 | active=true | All 3 clauses met |
| `test_lakshmi_weak_venus_inactive` | Same but Venus shadbala=0.4 | active=false | Clause 3 fails |
| `test_lakshmi_9thlord_not_in_kendra` | 9L Jupiter in 3rd | active=false | Clause 2 fails |

#### Kemadruma
| Test name | Chart | Expected | Rationale |
|---|---|---|---|
| `test_kemadruma_moon_isolated` | Moon in Aries; 2nd (Taurus), 12th (Pisces), and same sign: no planets except Sun/Rahu/Ketu allowed | active=true | Isolation |
| `test_kemadruma_canceled_by_jupiter_aspect` | same, but Jupiter aspects Moon (5th/9th) | active=false | Cancellation clause triggers |
| `test_kemadruma_canceled_by_moon_in_kendra` | Moon in 10th house | active=false | Kendra cancellation |
| `test_kemadruma_canceled_by_moon_exalted` | Moon in Taurus (exalted) and isolated | active=false | Exaltation cancellation |

#### Neecha Bhanga Raja Yoga
| Test name | Chart | Expected | Rationale |
|---|---|---|---|
| `test_nbry_mars_debilitated_cancer_lord_moon_in_kendra` | Mars in Cancer (debilitated), Moon (Cancer lord) in 1st or 10th | active=true for Mars | Condition 1 |
| `test_nbry_mars_debilitated_no_conditions_met` | Mars in Cancer, Moon in 3rd, no exch, no aspects | active=false for Mars | No cancellation |
| `test_nbry_iteration_emits_per_planet` | Sun debilitated AND Mars debilitated, both cancellations met | 2 compute rows | Iteration |
| `test_nbry_strength_increases_with_cancellation_count` | 3 cancellation conditions met | strength > single-condition case | Bonus formula |

### 8.4 Engine integration

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_engine_evaluates_all_60_rules` | Any chart | 60+ compute rows (iteration may add more) | Completeness |
| `test_engine_idempotent` | 2 runs | row count stable via ON CONFLICT | Idempotency |
| `test_engine_rule_version_pinned` | Inspect rows | All have matching rule_version | F4 consistency |
| `test_engine_cross_source_variants_coexist` | chart where Ruchaka BPHS + Saravali variant both apply | 2 rows, different source_id | Cross-source |
| `test_engine_performance` | 1 chart, 60 rules | P99 < 250 ms | Perf budget |

### 8.5 Rule loading

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_all_60_yamls_parse` | F6 loader | 60 rows in `classical_rule` | Content authoring |
| `test_yaml_citations_present` | Inspect rows | Every row has non-null `citation` | Citation coverage |
| `test_yaml_classical_names_multilingual` | Inspect rows | Every row has `en`, `sa_iast`, `sa_devanagari` | i18n baseline |

### 8.6 Golden suite

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_golden_gandhi_yogas` | B.V. Raman Notable Horoscopes #1 | Expected list of active yogas present; strength within ±0.15 | Classical case study |
| `test_golden_einstein_yogas` | BVR #12 | ditto | |
| ... (×20 charts) | | | |

### 8.7 Property tests

| Test name | Invariant | Rationale |
|---|---|---|
| `test_yoga_deterministic` | same chart → same output_hash | Content provenance |
| `test_active_implies_strength_positive` | active=true → strength > 0 | Consistency |
| `test_strength_in_range` | strength ∈ [0, 1] always | Bounds |
| `test_cancellation_terminates_activation` | For yoga with cancellation clause met, active=false | Correctness of cancellation |
| `test_iterate_over_bounded` | iterate_over rules emit ≤ 9 rows (max 7 planets + 2 nodes) | Scale |

### 8.8 Differential vs JH

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_differential_gandhi` | Gandhi chart vs JH yogas panel | ≥80% overlap of active yogas present in both Josi's 60 and JH | Cross-tool |
| ... (×10) | | | |

## 9. EPIC-Level Acceptance Criteria

- [ ] 60 yoga rules authored in YAML, loaded into `classical_rule` via F6
- [ ] Every rule has: `source_id`, `version`, `citation`, `classical_names` (en + sa_iast + sa_devanagari + ta), activation predicate, strength formula
- [ ] Predicate evaluator supports all ~20 `op`s listed in §3.4; each has unit tests
- [ ] Strength evaluator supports weighted_sum, product, conditional, lookup, clamp
- [ ] `YogaEngine` implements `ClassicalEngine` Protocol; idempotent compute via ON CONFLICT DO NOTHING
- [ ] REST endpoint `/api/v1/yogas/{chart_id}` with category/strength/active filters works
- [ ] AI tool `get_yoga_summary` works end-to-end; aggregates via F8 strategies
- [ ] Golden suite: 20 charts; every yoga activates in ≥1 chart and does NOT activate in ≥1 chart
- [ ] Property tests with ≥1000 examples per invariant all pass
- [ ] Unit test coverage ≥ 92% for predicates, strength formulas, engine
- [ ] Differential vs JH 7.x: ≥80% activation agreement on 10 famous charts
- [ ] Per-chart compute P99 < 250 ms (60 rules)
- [ ] `chart_reading_view.active_yogas` JSONB populated with top-N (configurable, default 10) strongest yogas
- [ ] Docs: `CLAUDE.md` + `docs/markdown/YOGA_ENGINE.md` describing rule DSL usage for yoga authors
- [ ] Classical advisor sign-off on YAML content (6 subdirs × ~10 files each)

## 10. Rollout Plan

- **Feature flag:** `ENABLE_YOGA_ENGINE` (default `true` on P1 deploy). Per-category flags (`ENABLE_YOGA_DUSHTA` etc.) available for partial rollout if needed.
- **Shadow compute:** on staging, run for 1000 charts; spot-check 20 against JH 7.x; review 5 famous-person charts vs *Notable Horoscopes*.
- **Backfill:** on-demand via AI chat; background worker seeds `chart_reading_view.active_yogas` over 2 weeks.
- **Rollback:** flag off → endpoint returns 503; `chart_reading_view.active_yogas` retains last-computed values; rules soft-deprecated via `effective_to`.

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Predicate vocabulary insufficient for some yoga → YAML cannot express | Medium | High | Predicate ops extensible; new op requires engineering change only on first use; 20 ops shipped cover ~95% of classical patterns |
| Classical advisor disagreement on yoga authoring | Medium | High | Dual-reviewer policy; BPHS takes precedence in disputes; alternate lineages ship as separate `source_id` rules |
| Aspect rules nuances (Mars's special 4th/8th, Jupiter's 5th/9th, Saturn's 3rd/10th) subtle | Medium | High | Classical sign-based only in v1; explicit aspect table; test matrix per planet-pair |
| Strength formula calibration feels arbitrary | High | Medium | Initial calibration is approximate; E14a experimentation refines weights over time with user/astrologer feedback |
| Per-chart performance at 60 rules × complex predicates | Medium | Medium | Chart state built once per chart; predicates pure; target < 250 ms; profiling in T-E4a.5 |
| Kaal Sarp 8-subtype enumeration disputed (regional invention) | Medium | Low | Phaladeepika reference documented; subtype is metadata, not a separate rule_id |
| Cross-source variants multiply complexity | Medium | Medium | P1 ships primary BPHS variant only per yoga; cross-source defers to P2 except where explicitly called out |
| Famous-chart fixtures may reveal engine bugs late | High | High | Author fixtures incrementally; failures block merge; classical-advisor signs off |
| Mercury/Moon benefic/malefic classification dynamic | Medium | Medium | Explicit predicate for classification; test coverage for waxing/waning and affliction thresholds |
| LLM prompt length with 60 yogas inflates cost | Medium | Medium | F11 citation shape is terse; F12 prompt caching amortizes; `min_strength` filter reduces payload |
| Rule YAML becomes unwieldy for rule authors | Low | Medium | 5-example style guide; future P3 rule authoring console |

## 12. References

- Master spec: [`docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`](../../../superpowers/specs/2026-04-19-classical-techniques-expansion-design.md)
- F1, F2, F4, F6, F7, F8, F13, F16, F17 (dependencies)
- Classical primary sources:
  - Brihat Parashara Hora Shastra, Santhanam translation (Ranjan 2004): Ch. 36 (Pancha Mahapurusha), Ch. 37 (Raja Yogas), Ch. 38 (Chandra + Surya), Ch. 39 (Neecha Bhanga), Ch. 42 (Arishta), Ch. 43 (Dhana)
  - Saravali by Kalyanavarma (R. Santhanam translation, Ranjan 1983): Ch. 13–14 (Chandra yogas), Ch. 35 (Pancha Mahapurusha variant), Ch. 38 (Dushta yogas), Ch. 42 (Dhana)
  - Phaladeepika by Mantreswara (G.S. Kapoor translation): Ch. 6 (Raja yogas), Ch. 14 (Dushta), Ch. 15 (Dhana)
  - Jataka Parijata by Vaidyanatha Dikshita: cross-references Ch. 4 + 7
- Modern commentary:
  - B.V. Raman, *Three Hundred Important Combinations* — comprehensive yoga catalog
  - B.V. Raman, *Notable Horoscopes* — worked examples (source for golden fixtures)
- Existing Josi: `src/josi/services/astrology_service.py`, `src/josi/services/strength_calculator.py`
- Reference implementation: Jagannatha Hora 7.x (Yogas panel: "Classical Yogas")
