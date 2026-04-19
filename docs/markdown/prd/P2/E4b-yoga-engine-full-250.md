---
prd_id: E4b
epic_id: E4
title: "Classical Yoga Engine — Full 250-Yoga Catalog"
phase: P2-breadth
tags: [#correctness, #extensibility, #experimentation, #i18n]
priority: must
depends_on: [E4a, F1, F2, F4, F6, F7, F8, F13, F16, F17]
enables: [E11a, E11b, E12, E13, P3-E2-console, P4-yoga-reference-1000]
classical_sources: [bphs, saravali, phaladeepika, jataka_parijata, jaimini_sutras, tajaka_neelakanthi]
estimated_effort: 8 weeks
status: draft
author: @agent-claude-opus-4-7
last_updated: 2026-04-19
---

# E4b — Classical Yoga Engine, Full 250-Yoga Catalog

## 1. Purpose & Rationale

E4a shipped the **engine** (`YogaEngine`, predicate evaluator, strength evaluator, DSL loader integration) plus the **60 highest-cited yogas** across six categories. E4b is the **content-breadth release**: 190 additional yoga rules that bring Josi's coverage to ~250 yogas, matching what a working astrologer would recognize from Jagannatha Hora or Maitreya9.

Three observations drive this PRD:

1. **The engine is already built.** E4b is purely **additive** — no changes to `YogaEngine` or its evaluators. The rule-registry pattern matured in E4a is now cashing its promise: adding a yoga is a pure content change (1 YAML + 1 test fixture + a PR).
2. **The DSL needs ~10 new predicates** (Nabhasa Sankhya counts, Parivartana mutual-exchange, Tajaka applying/separating aspect, Kaal-Sarp axis lookups). Small, bounded, shared across many yogas.
3. **We will NOT write 250 full YAMLs.** This PRD lists all 250 yogas by rule_id + category + source + one-line gist; provides **full YAML for 20 representative yogas** chosen to exercise every new predicate; and specifies the **authoring workflow** for the remaining ~230.

"What's special about my chart?" — the question every AI chat session converges to — is answered by named yogas. More yogas = more specific, more classically-grounded answers.

## 2. Scope

### 2.1 In scope

- **190 additional yoga rules** across 11 categories (§3.1).
- **Full YAML for 20 representative yogas** chosen to exercise every new DSL predicate (§3.2).
- **Brief rule summaries for the remaining ~170** — same format as E4a §3.3 (§3.3–§3.12).
- **~10 new DSL predicates** added to F6 vocabulary, implemented in `src/josi/services/classical/yoga/predicates.py` (§3.14).
- **Cross-source variant handling** — BPHS/Saravali/Phaladeepika disagreements ship as sibling rules (distinct `rule_id`, shared `technique_family_id`), consumed by F8 aggregation strategies (§3.13).
- **Golden-chart fixtures** — ≥1 activating chart per new yoga (190 new fixtures minimum).
- **Tajaka yogas** — 16 authored here but gated behind E5 (Varshaphala): engine short-circuits them unless a Varshaphala chart is supplied. Flagged via `metadata.requires_chart_context: varshaphala`.
- **Ship-wave feature flagging** — 4 waves of ~50 yogas, each wave golden-green before promotion.
- **Rule-authoring workflow** — who authors, how reviewed, how tested, SLA for yoga-61 → production (§5.4).

### 2.2 Out of scope

- **Engine changes.** `YogaEngine` surface is frozen at E4a.
- **Yogas 251–1000** — deferred to P4 via the rule-authoring console (P3-E2).
- **Natural-language interpretation generation** — owned by E11a.
- **Divisional-chart-specific yogas** (D-9 Navamsa, D-10 Dasamsa) — deferred to E7 + future E4c.
- **Ashtakavarga-threshold variants** — deferred; needs cross-technique state.
- **KP-sublord-based yogas** — owned by E9.
- **New aggregation strategies.** Per-yoga nuance rides on F8's existing A/B/C/D.

### 2.3 Dependencies

- **E4a** completed and in production — engine, dispatch tables, DSL loader, 60 base rules, golden fixtures.
- **F6** rule DSL + loader; extended here. **F16** golden chart suite; +190 fixtures. **F17** property-test harness.
- **E5 (Varshaphala)** — *soft* dep for Tajaka; YAMLs ship here, become evaluable when E5 provides Varshaphala chart state. Feature-flagged.
- Classical-advisor network (Sanskritist + working astrologer) — operational.

## 3. Classical Research — The 250-Yoga Catalog

Organizing principle: **breadth-first**. Every one of the 250 yogas appears at least as a one-liner. Twenty appear as full YAML. The rest are authored during T-E4b.3+ using the same grammar.

Category counts:

| Category | E4a | E4b adds | Total |
|---|---:|---:|---:|
| Pancha Mahapurusha | 5 | 0 | 5 |
| Raja Yogas | 15 | 25 | 40 |
| Dhana Yogas | 10 | 30 | 40 |
| Nabhasa Yogas | 0 | 32 | 32 |
| Chandra Yogas | 10 | 20 | 30 |
| Surya Yogas | 5 | 5 | 10 |
| Parivartana Yogas | 0 | 30 | 30 |
| Viparita Raja variants | 3 | 3 | 6 |
| Dushta / Arishta | 15 | 19 | 34 |
| Named Miscellaneous | 0 | 18 | 18 |
| Tajaka (Varshaphala-gated) | 0 | 16 | 16 |
| **Totals** | **63** | **198** | **261** |

De-duplication between "Named Misc" and regional Raja lists brings the shipped count to exactly 250 at freeze.

### 3.1 Category structure reference

- **Pancha Mahapurusha** (E4a-only): see E4a §3.1.1.
- **Raja / Dhana:** Kendra-Trikona and 2/5/9/11 lord combinations from BPHS, Phaladeepika, Saravali, Jataka Parijata.
- **Nabhasa** (BPHS Ch.39): Asraya (3), Dala (10), Sankhya (19).
- **Chandra / Surya:** Moon-/Sun-family extensions.
- **Parivartana** (BPHS Ch.40): six type-families × kendra-trikona categories = 30 canonical combos.
- **Viparita Raja variants:** Harsha, Sarala, Vimala plus strict strength variants.
- **Dushta / Arishta:** Kaal-Sarp axis types, Shrapit, Pitra Dosha sub-types, Daridra variants.
- **Named Miscellaneous:** Hari, Hara, Brahma — Saravali Ch.18–30 + Phaladeepika + Jataka Parijata.
- **Tajaka:** Annual-chart yogas from Tajaka Neelakanthi. Gated on E5.

### 3.2 The 20 representative yogas — full YAML

These 20 exercise every DSL capability not fully demonstrated in E4a. They are the engineering acceptance set — if they parse, load, evaluate, and test green, the remaining ~170 follow the same patterns. YAMLs below use compressed indentation (the loader accepts both styles).

#### 3.2.1 Ruchaka (Pancha Mahapurusha)

Already authored in E4a §3.2.1 as `yoga.pancha_mahapurusha.ruchaka.bphs`. Reproduced by reference.

#### 3.2.2 Rajju (Nabhasa Asraya)

`src/josi/rules/yogas/bphs/nabhasa/rajju_bphs.yaml`:

```yaml
rule_id: yoga.nabhasa.asraya.rajju.bphs
source_id: bphs
version: "1.0.0"
technique_family_id: yoga
output_shape_id: boolean_with_strength
citation: "BPHS Ch.39 v.2"
classical_names: {en: "Rajju Yoga", sa_iast: "Rajju Yoga", sa_devanagari: "रज्जु योग", ta: "ரஜ்ஜு யோகம்"}
effective_from: "2026-06-01T00:00:00Z"
activation:
  predicate:
    op: all_planets_in_sign_group
    planets: [sun, moon, mars, mercury, jupiter, venus, saturn]
    sign_group: chara              # movable: Aries, Cancer, Libra, Capricorn
    require_all: true
strength:
  formula: weighted_sum
  terms:
    - {weight: 0.5, factor: {op: count_distinct_signs_with_planets, planets: [sun, moon, mars, mercury, jupiter, venus, saturn], scores_by_count: {"1": 0.4, "2": 0.65, "3": 0.85, "4": 1.0}}}
    - {weight: 0.3, factor: {op: planet_dignity_average, planets: [sun, moon, mars, mercury, jupiter, venus, saturn]}}
    - {weight: 0.2, factor: {op: afflictions_penalty_chart_wide, base_score: 0.8, penalty_per_combust: 0.05}}
  clamp: [0.0, 1.0]
metadata: {category: nabhasa_asraya, classical_effects_tag: "wanderer, travel_career, restless_nature", requires_chart_context: natal}
```

#### 3.2.3 Musala (Nabhasa Asraya)

`src/josi/rules/yogas/bphs/nabhasa/musala_bphs.yaml`:

```yaml
rule_id: yoga.nabhasa.asraya.musala.bphs
source_id: bphs
version: "1.0.0"
technique_family_id: yoga
output_shape_id: boolean_with_strength
citation: "BPHS Ch.39 v.3"
classical_names: {en: "Musala Yoga", sa_iast: "Musala Yoga", sa_devanagari: "मुसल योग", ta: "முசல யோகம்"}
effective_from: "2026-06-01T00:00:00Z"
activation:
  predicate:
    op: all_planets_in_sign_group
    planets: [sun, moon, mars, mercury, jupiter, venus, saturn]
    sign_group: sthira             # fixed: Taurus, Leo, Scorpio, Aquarius
    require_all: true
strength:
  formula: weighted_sum
  terms:
    - {weight: 0.55, factor: {op: count_distinct_signs_with_planets, planets: [sun, moon, mars, mercury, jupiter, venus, saturn], scores_by_count: {"1": 0.4, "2": 0.7, "3": 0.9, "4": 1.0}}}
    - {weight: 0.45, factor: {op: planet_dignity_average, planets: [sun, moon, mars, mercury, jupiter, venus, saturn]}}
  clamp: [0.0, 1.0]
metadata: {category: nabhasa_asraya, classical_effects_tag: "stability, fixed_principles, persistent_wealth"}
```

#### 3.2.4 Kamala (Nabhasa Dala)

```yaml
rule_id: yoga.nabhasa.dala.kamala.bphs
source_id: bphs
version: "1.0.0"
technique_family_id: yoga
output_shape_id: boolean_with_strength
citation: "BPHS Ch.39 v.11"
classical_names: {en: "Kamala Yoga", sa_iast: "Kamala Yoga", sa_devanagari: "कमल योग"}
effective_from: "2026-06-01T00:00:00Z"
activation:
  predicate:
    op: planets_occupy_houses_exactly
    planets: [sun, moon, mars, mercury, jupiter, venus, saturn]
    required_houses: [1, 4, 7, 10]
    mode: all_kendras_occupied
    reference: lagna
strength:
  formula: weighted_sum
  terms:
    - {weight: 0.4, factor: {op: planet_dignity_average, planets: [sun, moon, mars, mercury, jupiter, venus, saturn]}}
    - {weight: 0.3, factor: {op: benefic_occupancy_ratio, houses: [1, 4, 7, 10]}}
    - {weight: 0.3, factor: {op: afflictions_penalty_chart_wide, base_score: 0.8}}
  clamp: [0.0, 1.0]
metadata: {category: nabhasa_dala, classical_effects_tag: "lotus_like_beauty, spiritual_authority, sustained_prosperity"}
```

#### 3.2.5 Shakti (Nabhasa Dala)

```yaml
rule_id: yoga.nabhasa.dala.shakti.bphs
source_id: bphs
version: "1.0.0"
technique_family_id: yoga
output_shape_id: boolean_with_strength
citation: "BPHS Ch.39 v.17"
classical_names: {en: "Shakti Yoga", sa_iast: "Śakti Yoga"}
effective_from: "2026-06-01T00:00:00Z"
activation:
  predicate:
    op: all_of
    clauses:
      - {op: benefics_in_house_group, benefics: [jupiter, venus, mercury_if_unafflicted, moon_if_waxing], houses: [7, 8, 9], reference: lagna, minimum_benefics: 2}
      - {op: malefics_in_house_group, malefics: [sun, mars, saturn, rahu, ketu], houses: [7, 8, 9], reference: lagna, minimum_malefics: 1}
strength:
  formula: weighted_sum
  terms:
    - {weight: 0.5, factor: {op: dignity_balance_score, benefics_in_houses: [7, 8, 9], malefics_in_houses: [7, 8, 9]}}
    - {weight: 0.3, factor: {op: planet_dignity_average, planets_scope: benefics_in_houses, houses: [7, 8, 9]}}
    - {weight: 0.2, factor: {op: afflictions_penalty_chart_wide, base_score: 0.8}}
  clamp: [0.0, 1.0]
metadata: {category: nabhasa_dala, classical_effects_tag: "warrior_spirit, victory_against_odds, martial_valor"}
```

#### 3.2.6 Gada (Nabhasa Sankhya)

```yaml
rule_id: yoga.nabhasa.sankhya.gada.bphs
source_id: bphs
version: "1.0.0"
technique_family_id: yoga
output_shape_id: boolean_with_strength
citation: "BPHS Ch.39 v.23"
classical_names: {en: "Gada Yoga", sa_iast: "Gadā Yoga"}
effective_from: "2026-06-01T00:00:00Z"
activation:
  predicate:
    op: all_of
    clauses:
      - {op: all_planets_in_adjacent_kendra_pair, planets: [sun, moon, mars, mercury, jupiter, venus, saturn], reference: lagna}
      - {op: count_distinct_signs_with_planets, planets: [sun, moon, mars, mercury, jupiter, venus, saturn], equals: 2}
strength:
  formula: weighted_sum
  terms:
    - {weight: 0.6, factor: {op: planet_dignity_average, planets: [sun, moon, mars, mercury, jupiter, venus, saturn]}}
    - {weight: 0.4, factor: {op: house_strength_average, houses_occupied_by: [sun, moon, mars, mercury, jupiter, venus, saturn]}}
  clamp: [0.0, 1.0]
metadata: {category: nabhasa_sankhya, classical_effects_tag: "mace_wielder, forceful_nature, martial_profession"}
```

#### 3.2.7 Maha Parivartana — Lagna ↔ 10th

```yaml
rule_id: yoga.parivartana.maha.lagna_10.bphs
source_id: bphs
version: "1.0.0"
technique_family_id: yoga
output_shape_id: boolean_with_strength
citation: "BPHS Ch.40 v.4-6"
classical_names: {en: "Maha Parivartana (Lagna–10th)", sa_iast: "Mahā Parivartana Yoga"}
effective_from: "2026-06-01T00:00:00Z"
activation:
  predicate: {op: mutual_exchange, lord_of_house_a: 1, lord_of_house_b: 10, reference: lagna}
strength:
  formula: weighted_sum
  terms:
    - {weight: 0.35, factor: {op: planet_dignity_score, planet: {op: lord_of_house, house: 1, reference: lagna}}}
    - {weight: 0.35, factor: {op: planet_dignity_score, planet: {op: lord_of_house, house: 10, reference: lagna}}}
    - {weight: 0.2, factor: {op: afflictions_penalty, planets: [{op: lord_of_house, house: 1, reference: lagna}, {op: lord_of_house, house: 10, reference: lagna}], base_score: 1.0}}
    - {weight: 0.1, factor: {op: aspects_received_score, planets_scope: [lord_1, lord_10], benefic_aspect_bonus: 0.15, base_score: 0.7}}
  clamp: [0.0, 1.0]
metadata: {category: parivartana_maha, classical_effects_tag: "career_and_self_alignment, executive_success", parivartana_type: maha}
```

#### 3.2.8 Khala Parivartana — 6th ↔ 8th

Strength here reflects severity of affliction (higher strength = stronger dushta effect).

```yaml
rule_id: yoga.parivartana.khala.6_8.bphs
source_id: bphs
version: "1.0.0"
technique_family_id: yoga
output_shape_id: boolean_with_strength
citation: "BPHS Ch.40 v.10-12"
classical_names: {en: "Khala Parivartana (6th–8th)", sa_iast: "Khala Parivartana Yoga"}
effective_from: "2026-06-01T00:00:00Z"
activation:
  predicate: {op: mutual_exchange, lord_of_house_a: 6, lord_of_house_b: 8, reference: lagna}
strength:
  formula: weighted_sum
  terms:
    - {weight: 0.5, factor: {op: afflictions_amplifier, planets: [{op: lord_of_house, house: 6, reference: lagna}, {op: lord_of_house, house: 8, reference: lagna}], base_score: 0.5, per_malefic_aspect_bonus: 0.15}}
    - {weight: 0.3, factor: {op: inverse_planet_dignity, planets: [{op: lord_of_house, house: 6, reference: lagna}, {op: lord_of_house, house: 8, reference: lagna}]}}
    - {weight: 0.2, factor: {op: lookup, key: {op: paksha}, table: {shukla: 0.4, krishna: 0.7}}}
  clamp: [0.0, 1.0]
metadata: {category: parivartana_khala, classical_effects_tag: "sudden_losses, chronic_enemies, health_setbacks", parivartana_type: khala}
```

#### 3.2.9 Viparita Raja — Harsha (strict sibling of E4a)

```yaml
rule_id: yoga.raja.viparita_harsha.bphs.strict
source_id: bphs
version: "1.0.0"
technique_family_id: yoga
output_shape_id: boolean_with_strength
citation: "BPHS Ch.37 v.28 (strict-reading per Govindacharya commentary)"
classical_names: {en: "Viparita Raja — Harsha (strict)", sa_iast: "Viparīta Rājayoga — Harṣa"}
effective_from: "2026-06-01T00:00:00Z"
activation:
  predicate:
    op: all_of
    clauses:
      - {op: house_lord_in_house_group, house: 6, reference: lagna, houses: [6, 8, 12]}
      - {op: not, clause: {op: planet_conjunct_or_aspected_by, planet: {op: lord_of_house, house: 6, reference: lagna}, partners: [jupiter, venus]}}
      - {op: not, clause: {op: planet_conjunct, planet: {op: lord_of_house, house: 6, reference: lagna}, partners: [sun, moon]}}
      - {op: house_lord_not_debilitated, house: 6, reference: lagna}
strength:
  formula: weighted_sum
  terms:
    - {weight: 0.45, factor: {op: planet_dignity_score, planet: {op: lord_of_house, house: 6, reference: lagna}}}
    - {weight: 0.3, factor: {op: lookup, key: {op: house_of_planet, planet: {op: lord_of_house, house: 6, reference: lagna}, reference: lagna}, table: {"6": 1.0, "8": 0.85, "12": 0.75}}}
    - {weight: 0.25, factor: {op: afflictions_penalty, planets: [{op: lord_of_house, house: 6, reference: lagna}], base_score: 0.85}}
  clamp: [0.0, 1.0]
metadata: {category: raja_viparita, variant_of: yoga.raja.viparita_harsha.bphs, classical_effects_tag: "triumph_over_enemies, health_recovery"}
```

#### 3.2.10 Viparita Raja — Sarala (expanded sibling)

```yaml
rule_id: yoga.raja.viparita_sarala.bphs.expanded
source_id: bphs
version: "1.0.0"
technique_family_id: yoga
output_shape_id: boolean_with_strength
citation: "BPHS Ch.37 v.29 + Phaladeepika 6.36 cross-reading"
classical_names: {en: "Viparita Raja — Sarala (expanded)", sa_iast: "Viparīta Rājayoga — Sarala"}
effective_from: "2026-06-01T00:00:00Z"
activation:
  predicate:
    op: all_of
    clauses:
      - {op: house_lord_in_house_group, house: 8, reference: lagna, houses: [6, 8, 12]}
      - {op: not, clause: {op: planet_conjunct_or_aspected_by, planet: {op: lord_of_house, house: 8, reference: lagna}, partners: [jupiter, venus, mercury_if_unafflicted]}}
strength:
  formula: weighted_sum
  terms:
    - {weight: 0.4, factor: {op: planet_dignity_score, planet: {op: lord_of_house, house: 8, reference: lagna}}}
    - {weight: 0.3, factor: {op: lookup, key: {op: house_of_planet, planet: {op: lord_of_house, house: 8, reference: lagna}, reference: lagna}, table: {"6": 0.85, "8": 1.0, "12": 0.8}}}
    - {weight: 0.3, factor: {op: planet_strength, planet: {op: lord_of_house, house: 8, reference: lagna}, strength_metric: shadbala_normalized}}
  clamp: [0.0, 1.0]
metadata: {category: raja_viparita, variant_of: yoga.raja.viparita_sarala.bphs, classical_effects_tag: "resilience, unexpected_longevity"}
```

#### 3.2.11 Adhi Yoga (Chandra — from-Moon reference)

```yaml
rule_id: yoga.chandra.adhi.bphs
source_id: bphs
version: "1.0.0"
technique_family_id: yoga
output_shape_id: boolean_with_strength
citation: "BPHS Ch.38 v.7-8"
classical_names: {en: "Adhi Yoga (Chandra)", sa_iast: "Ādhi Yoga"}
effective_from: "2026-06-01T00:00:00Z"
activation:
  predicate:
    op: all_of
    clauses:
      - {op: benefics_in_house_group, benefics: [jupiter, venus, mercury_if_unafflicted], houses: [6, 7, 8], reference: moon, minimum_benefics: 2}
      - {op: none_of, clauses: [{op: malefic_in_house, house: 6, reference: moon}, {op: malefic_in_house, house: 7, reference: moon}, {op: malefic_in_house, house: 8, reference: moon}]}
strength:
  formula: weighted_sum
  terms:
    - {weight: 0.45, factor: {op: benefic_count_in_houses, houses: [6, 7, 8], reference: moon, scores_by_count: {"2": 0.7, "3": 1.0}}}
    - {weight: 0.3, factor: {op: planet_dignity_average, planets_scope: benefics_in_houses, houses: [6, 7, 8], reference: moon}}
    - {weight: 0.25, factor: {op: planet_dignity_score, planet: moon}}
  clamp: [0.0, 1.0]
metadata: {category: chandra, also_category: raja, classical_effects_tag: "leadership, respectable_position, followers"}
```

#### 3.2.12 Amala Yoga

```yaml
rule_id: yoga.raja.amala.bphs
source_id: bphs
version: "1.0.0"
technique_family_id: yoga
output_shape_id: boolean_with_strength
citation: "BPHS Ch.37 v.14"
classical_names: {en: "Amala Yoga", sa_iast: "Amala Yoga", sa_devanagari: "अमल योग"}
effective_from: "2026-06-01T00:00:00Z"
activation:
  predicate:
    op: any_of
    clauses:
      - {op: all_of, clauses: [{op: benefic_in_house, house: 10, reference: moon}, {op: no_malefic_in_house, house: 10, reference: moon}]}
      - {op: all_of, clauses: [{op: benefic_in_house, house: 10, reference: lagna}, {op: no_malefic_in_house, house: 10, reference: lagna}]}
strength:
  formula: weighted_sum
  terms:
    - {weight: 0.45, factor: {op: planet_dignity_score, planet: {op: strongest_benefic_in_house, house: 10, reference: moon_or_lagna}}}
    - {weight: 0.3, factor: {op: house_strength_score, planet: {op: strongest_benefic_in_house, house: 10}}}
    - {weight: 0.25, factor: {op: afflictions_penalty, planets: [{op: strongest_benefic_in_house, house: 10}], base_score: 0.9}}
  clamp: [0.0, 1.0]
metadata: {category: raja, classical_effects_tag: "unblemished_reputation, pure_livelihood, ethical_fame"}
```

#### 3.2.13 Lakshmi Yoga (Dhana)

Already authored in E4a §3.2.3 as `yoga.dhana.lakshmi.phaladeepika`.

#### 3.2.14 Kubera Yoga (Dhana)

```yaml
rule_id: yoga.dhana.kubera.bphs
source_id: bphs
version: "1.0.0"
technique_family_id: yoga
output_shape_id: boolean_with_strength
citation: "BPHS Ch.43 v.6"
classical_names: {en: "Kubera Yoga", sa_iast: "Kubera Yoga", sa_devanagari: "कुबेर योग"}
effective_from: "2026-06-01T00:00:00Z"
activation:
  predicate:
    op: all_of
    clauses:
      - {op: any_of, clauses: [{op: house_lord_in_house, house: 11, target_house: 2, reference: lagna}, {op: house_lord_in_house, house: 2, target_house: 11, reference: lagna}]}
      - {op: any_of, clauses: [{op: house_lord_conjunct_with_benefic, house: 2, reference: lagna}, {op: house_lord_conjunct_with_benefic, house: 11, reference: lagna}, {op: house_lord_aspected_by_benefic, house: 2, reference: lagna}, {op: house_lord_aspected_by_benefic, house: 11, reference: lagna}]}
strength:
  formula: weighted_sum
  terms:
    - {weight: 0.3, factor: {op: planet_dignity_score, planet: {op: lord_of_house, house: 2, reference: lagna}}}
    - {weight: 0.3, factor: {op: planet_dignity_score, planet: {op: lord_of_house, house: 11, reference: lagna}}}
    - {weight: 0.2, factor: {op: benefic_association_score, planets: [{op: lord_of_house, house: 2, reference: lagna}, {op: lord_of_house, house: 11, reference: lagna}]}}
    - {weight: 0.2, factor: {op: afflictions_penalty, planets: [{op: lord_of_house, house: 2, reference: lagna}, {op: lord_of_house, house: 11, reference: lagna}], base_score: 1.0}}
  clamp: [0.0, 1.0]
metadata: {category: dhana, classical_effects_tag: "accumulated_wealth, treasury, inheritance"}
```

#### 3.2.15 Kaal Sarp — Anant (Axis 1–7)

```yaml
rule_id: yoga.dushta.kaal_sarp.anant.phaladeepika
source_id: phaladeepika
version: "1.0.0"
technique_family_id: yoga
output_shape_id: boolean_with_strength
citation: "Phaladeepika Ch.14 v.18 (Anant: Rahu in 1st / Ketu in 7th)"
classical_names: {en: "Kaal Sarp — Anant", sa_iast: "Kāla Sarpa — Ananta"}
effective_from: "2026-06-01T00:00:00Z"
activation:
  predicate:
    op: all_of
    clauses:
      - {op: all_planets_between_nodes, planets: [sun, moon, mars, mercury, jupiter, venus, saturn], from_node: rahu, to_node: ketu, direction: zodiacal}
      - {op: planet_in_house, planet: rahu, house: 1, reference: lagna}
      - {op: planet_in_house, planet: ketu, house: 7, reference: lagna}
strength:
  formula: weighted_sum
  terms:
    - {weight: 0.4, factor: {op: afflictions_amplifier, planets: [rahu, ketu], base_score: 0.6, per_malefic_aspect_bonus: 0.1}}
    - {weight: 0.3, factor: {op: count_distinct_signs_with_planets, planets: [sun, moon, mars, mercury, jupiter, venus, saturn], inverted: true, scores_by_count: {"1": 1.0, "2": 0.9, "3": 0.8, "4": 0.7, "5": 0.6, "6": 0.5, "7": 0.4}}}
    - {weight: 0.3, factor: {op: afflictions_penalty_chart_wide, base_score: 0.7, penalty_per_combust: 0.05}}
  clamp: [0.0, 1.0]
metadata: {category: dushta_kaal_sarp, subtype: anant, axis: "1-7", classical_effects_tag: "karmic_struggles, relationship_challenges"}
```

#### 3.2.16 Kaal Sarp — Padma (Axis 2–8)

```yaml
rule_id: yoga.dushta.kaal_sarp.padma.phaladeepika
source_id: phaladeepika
version: "1.0.0"
technique_family_id: yoga
output_shape_id: boolean_with_strength
citation: "Phaladeepika Ch.14 v.19 (Padma: Rahu in 2nd / Ketu in 8th)"
classical_names: {en: "Kaal Sarp — Padma", sa_iast: "Kāla Sarpa — Padma"}
effective_from: "2026-06-01T00:00:00Z"
activation:
  predicate:
    op: all_of
    clauses:
      - {op: all_planets_between_nodes, planets: [sun, moon, mars, mercury, jupiter, venus, saturn], from_node: rahu, to_node: ketu, direction: zodiacal}
      - {op: planet_in_house, planet: rahu, house: 2, reference: lagna}
      - {op: planet_in_house, planet: ketu, house: 8, reference: lagna}
strength:
  formula: weighted_sum
  terms:
    - {weight: 0.5, factor: {op: afflictions_amplifier, planets: [rahu, ketu], base_score: 0.6}}
    - {weight: 0.3, factor: {op: planet_dignity_average, planets: [sun, moon, mars, mercury, jupiter, venus, saturn], inverted: true}}
    - {weight: 0.2, factor: {op: lookup, key: {op: house_of_planet, planet: moon, reference: lagna}, table: {"2": 1.0, "8": 1.0, "6": 0.85, "12": 0.85, "default": 0.5}}}
  clamp: [0.0, 1.0]
metadata: {category: dushta_kaal_sarp, subtype: padma, axis: "2-8", classical_effects_tag: "wealth_obstacles, speech_issues, family_friction"}
```

#### 3.2.17 Shakata Yoga (Chandra/Dushta)

```yaml
rule_id: yoga.dushta.shakata.saravali
source_id: saravali
version: "1.0.0"
technique_family_id: yoga
output_shape_id: boolean_with_strength
citation: "Saravali Ch.13 v.9"
classical_names: {en: "Shakata Yoga", sa_iast: "Śakaṭa Yoga"}
effective_from: "2026-06-01T00:00:00Z"
activation:
  predicate:
    op: all_of
    clauses:
      - {op: angular_distance, from: jupiter, to: moon, unit: sign_houses, allowed_distances: [5, 7, 11]}
      - op: not
        clause:
          op: any_of
          clauses:
            - {op: planet_sign_status, planet: moon, status_any_of: [own_sign, exalted]}
            - {op: planet_receives_aspect, planet: moon, from_any_of: [jupiter, venus, mercury_if_unafflicted]}
strength:
  formula: weighted_sum
  terms:
    - {weight: 0.5, factor: {op: afflictions_amplifier, planets: [moon], base_score: 0.5}}
    - {weight: 0.3, factor: {op: inverse_planet_dignity, planets: [moon]}}
    - {weight: 0.2, factor: {op: lookup, key: {op: paksha}, table: {shukla: 0.35, krishna: 0.65}}}
  clamp: [0.0, 1.0]
metadata: {category: chandra_dushta, classical_effects_tag: "reversals_of_fortune, up_and_down_life"}
```

#### 3.2.18 Angaraka Yoga

```yaml
rule_id: yoga.dushta.angaraka.saravali
source_id: saravali
version: "1.0.0"
technique_family_id: yoga
output_shape_id: boolean_with_strength
citation: "Saravali Ch.38 v.11"
classical_names: {en: "Angaraka Yoga", sa_iast: "Aṅgāraka Yoga"}
effective_from: "2026-06-01T00:00:00Z"
activation:
  predicate:
    op: any_of
    clauses:
      - {op: planet_conjunct, planet: mars, partners: [rahu], orb_degrees: 8}
      - {op: planet_conjunct, planet: mars, partners: [ketu], orb_degrees: 8}
strength:
  formula: weighted_sum
  terms:
    - {weight: 0.55, factor: {op: conjunction_tightness_score, planet_a: mars, planet_b_any_of: [rahu, ketu], max_orb: 8}}
    - {weight: 0.25, factor: {op: afflictions_amplifier, planets: [mars], base_score: 0.5}}
    - {weight: 0.2, factor: {op: lookup, key: {op: house_of_planet, planet: mars, reference: lagna}, table: {"1": 0.9, "4": 0.9, "7": 0.9, "8": 1.0, "12": 0.95, "default": 0.6}}}
  clamp: [0.0, 1.0]
metadata: {category: dushta, classical_effects_tag: "anger, conflict, accidents, surgical_risk"}
```

#### 3.2.19 Ithasala Yoga (Tajaka — applying aspect)

```yaml
rule_id: yoga.tajaka.ithasala.neelakanthi
source_id: tajaka_neelakanthi
version: "1.0.0"
technique_family_id: yoga
output_shape_id: boolean_with_strength
citation: "Tajaka Neelakanthi Ch.2 v.8-12"
classical_names: {en: "Ithasala Yoga", sa_iast: "Ithaśāla Yoga"}
effective_from: "2026-06-01T00:00:00Z"
activation:
  predicate:
    op: all_of
    clauses:
      - {op: chart_context_is, context: varshaphala}
      - {op: applying_aspect, planet_faster: {op: muntha_lord}, planet_slower: {op: varsha_lord}, orb_degrees: 7, aspect_type: any_classical}
strength:
  formula: weighted_sum
  terms:
    - {weight: 0.5, factor: {op: applying_tightness_score, faster: {op: muntha_lord}, slower: {op: varsha_lord}}}
    - {weight: 0.3, factor: {op: planet_dignity_average, planets: [{op: muntha_lord}, {op: varsha_lord}]}}
    - {weight: 0.2, factor: {op: afflictions_penalty, planets: [{op: muntha_lord}, {op: varsha_lord}], base_score: 0.85}}
  clamp: [0.0, 1.0]
metadata: {category: tajaka, requires_chart_context: varshaphala, engine_short_circuit_unless_context_matches: true, classical_effects_tag: "year_completion, successful_undertakings"}
```

#### 3.2.20 Isharaaph Yoga (Tajaka — separating aspect)

```yaml
rule_id: yoga.tajaka.isharaaph.neelakanthi
source_id: tajaka_neelakanthi
version: "1.0.0"
technique_family_id: yoga
output_shape_id: boolean_with_strength
citation: "Tajaka Neelakanthi Ch.2 v.13-16"
classical_names: {en: "Isharaaph Yoga", sa_iast: "Īśarāpha Yoga"}
effective_from: "2026-06-01T00:00:00Z"
activation:
  predicate:
    op: all_of
    clauses:
      - {op: chart_context_is, context: varshaphala}
      - {op: separating_aspect, planet_faster: {op: muntha_lord}, planet_slower: {op: varsha_lord}, orb_degrees: 7, aspect_type: any_classical}
strength:
  formula: weighted_sum
  terms:
    - {weight: 0.6, factor: {op: separating_recency_score, faster: {op: muntha_lord}, slower: {op: varsha_lord}}}
    - {weight: 0.4, factor: {op: planet_dignity_average, planets: [{op: muntha_lord}, {op: varsha_lord}]}}
  clamp: [0.0, 1.0]
metadata: {category: tajaka, requires_chart_context: varshaphala, classical_effects_tag: "fading_opportunity, recently_passed_favorable_moment"}
```

### 3.3 Raja Yogas — 25 new rule summaries

One-liners; authored in T-E4b.5 per §5.4.

- `yoga.raja.parijata.phaladeepika` — Lagna lord's dispositor in own/exalted sign in a kendra. Phaladeepika 6.13.
- `yoga.raja.uttama.jataka_parijata` — Lagna lord + 10th lord in Vargottama (same sign in D-1 and D-9). Jataka Parijata 10.14.
- `yoga.raja.kulavardhanam.saravali` — 5th lord in own/exalted in kendra (strengthens family succession). Saravali 41.6.
- `yoga.raja.mahabhagya.bphs` — Daytime: Lagna + Sun + Moon in odd signs. Nighttime: all in even signs. BPHS 37.22.
- `yoga.raja.saraswati.phaladeepika` — Jupiter, Venus, Mercury in kendras/trikonas AND Jupiter in own/friendly/exalted. Phaladeepika 6.9.
- `yoga.raja.srinatha.jataka_parijata` — 10th lord in 7th + 7th lord exalted + aspect from 2nd lord. Jataka Parijata 10.16.
- `yoga.raja.budhaditya.phaladeepika` — Sun + Mercury conjunction in a kendra (kendra-extension of Budha-Aditya). Phaladeepika 6.27 variant.
- `yoga.raja.kalpadruma.saravali` — 4-step dispositor chain (L1 → dispositor → D's dispositor → Navamsha lord) all strong. Saravali 42.3.
- `yoga.raja.satya.jataka_parijata` — 9th lord exalted in kendra from Lagna + Jupiter aspect. Jataka Parijata 10.19.
- `yoga.raja.akhanda_samrajya.phaladeepika` — Lagna lord + 10th lord + 11th lord in mutual trinal relationship. Phaladeepika 6.40.
- `yoga.raja.amsavatara.saravali` — Lagna + 3 benefics in own/exalted Navamsha. Saravali 35.12.
- `yoga.raja.kahala_alt.saravali` — Saravali sibling of Kahala (less strict than Phaladeepika form). Saravali 35.24.
- `yoga.raja.gaja_kesari.saravali_permissive` — sibling of E4a's BPHS form: Saravali accepts aspect in addition to kendra occupancy. Saravali 13.3.
- `yoga.raja.rajasambandhi.phaladeepika` — Lagna lord conjoined with any kendra lord AND any trikona lord. Phaladeepika 6.7.
- `yoga.raja.mridang.jataka_parijata` — Lagna lord in 10th, 10th lord in Lagna, Jupiter in either kendra. Jataka Parijata 10.22.
- `yoga.raja.karta_ripu.saravali` — Lagna lord + 6th lord in mutual exchange (kartari-ripu type). Saravali 38.6.
- `yoga.raja.kalanidhi.phaladeepika` — Jupiter in 2nd/5th aspected by Mercury + Venus. Phaladeepika 6.33.
- `yoga.raja.yuva_raj.jataka_parijata` — 9th lord in Lagna, Lagna lord in 9th. Jataka Parijata 10.25.
- `yoga.raja.kalpa_druma_alt.jataka_parijata` — Jataka Parijata sibling of Kalpadruma (differs in Navamsha step). Jataka Parijata 10.27.
- `yoga.raja.vipareeta_trikona.saravali` — Two trikona lords in mutual 6/8 AND benefic joins one. Saravali 42.9.
- `yoga.raja.subha_kartari.phaladeepika` — benefics in both 12th and 2nd from Lagna. Phaladeepika 6.42.
- `yoga.raja.papa_kartari.phaladeepika` — malefics in both 12th and 2nd from Lagna (reluctant power). Phaladeepika 6.43.
- `yoga.raja.sankha.jataka_parijata` — 5th lord + 6th lord combination (JP variant). Jataka Parijata 10.29.
- `yoga.raja.bheri.saravali_permissive` — Saravali Bheri: Jupiter OR Venus (not Jupiter only). Saravali 35.28.
- `yoga.raja.kahala.jataka_parijata` — 4th+9th lords in kendra + strong Lagna lord + benefic aspect (JP sibling). Jataka Parijata 10.31.

### 3.4 Dhana Yogas — 30 new rule summaries

- `yoga.dhana.lakshmi.bphs` — BPHS sibling of E4a's Phaladeepika Lakshmi. BPHS 43.5.
- `yoga.dhana.kubera.phaladeepika` — Phaladeepika sibling of Kubera. Phaladeepika 15.5.
- `yoga.dhana.srinatha.jataka_parijata` — 10th lord in 7th + 7th lord exalted (dhana reading). Jataka Parijata 10.16.
- `yoga.dhana.parijata.phaladeepika` — 2nd lord in own sign in a kendra. Phaladeepika 15.8.
- `yoga.dhana.subha_vasi.saravali` — benefic in 2nd from Sun (dhana reading of Vesi). Saravali 14.2.
- `yoga.dhana.vasumati.phaladeepika` — Phaladeepika variant of Vasumati. Phaladeepika 6.25.
- `yoga.dhana.chamara.saravali` — Exalted Lagna lord in kendra + Venus aspect (wealth reading). Saravali 35.14.
- `yoga.dhana.saraswati.phaladeepika` — Mercury/Jupiter/Venus in 2/5/7/9/10/11 (wealth-axis reading). Phaladeepika 6.9 (dhana).
- `yoga.dhana.budha_dhana.jataka_parijata` — Mercury in 2nd aspected by Jupiter. Jataka Parijata 15.4.
- `yoga.dhana.guru_dhana.jataka_parijata` — Jupiter in 2nd aspected by Mercury. Jataka Parijata 15.5.
- `yoga.dhana.sukha_dhana.phaladeepika` — 4th lord + 2nd lord in mutual kendra. Phaladeepika 15.11.
- `yoga.dhana.poorna_dhana.bphs` — Lagna lord in 2nd, 2nd lord in 11th, 11th lord in Lagna (3-cycle). BPHS 43.10.
- `yoga.dhana.akrura.saravali` — all benefics in 2/5/11, no malefic aspect. Saravali 42.16.
- `yoga.dhana.chandra_venus_conj.jataka_parijata` — Moon + Venus conjunction in 2/4/11. Jataka Parijata 15.9.
- `yoga.dhana.sun_jupiter_conj.phaladeepika` — Sun + Jupiter in 2nd/5th aspected by Venus. Phaladeepika 15.13.
- `yoga.dhana.2_10.bphs` — 2nd + 10th lords in conjunction/aspect. BPHS 43.7.
- `yoga.dhana.11_4.phaladeepika` — 11th + 4th lords conjunction (property wealth). Phaladeepika 15.14.
- `yoga.dhana.11_10.phaladeepika` — 11th + 10th lords conjunction (career wealth). Phaladeepika 15.15.
- `yoga.dhana.5_10.saravali` — 5th + 10th lords conjunction (creative wealth). Saravali 42.11.
- `yoga.dhana.9_10.bphs` — Dharma-Karmadhipati as dhana reading. BPHS 43.9.
- `yoga.dhana.2_5.phaladeepika` — 2nd + 5th lords conjunction (fortune wealth). Phaladeepika 15.16.
- `yoga.dhana.2_11_mutual_aspect.bphs` — 2nd + 11th lords in 7th-aspect. BPHS 43.12.
- `yoga.dhana.2_11_parivartana.bphs` — 2nd + 11th lords in sign exchange. BPHS 43.13.
- `yoga.dhana.kubera_alt.jataka_parijata` — 11th in 2nd with Jupiter aspect. Jataka Parijata 15.20.
- `yoga.dhana.madhu.saravali` — Venus + Mercury conjunction in 4th/5th. Saravali 42.19.
- `yoga.dhana.manas.saravali` — 4th lord exalted + Moon in own sign (mental wealth). Saravali 42.21.
- `yoga.dhana.dhanvantari.phaladeepika` — 8th lord + Jupiter in 1st/10th (physician's wealth). Phaladeepika 15.20.
- `yoga.dhana.indra.jataka_parijata` — Lagna lord in 11th, 11th lord in 5th, 5th lord in Lagna. Jataka Parijata 15.24.
- `yoga.dhana.bharati.saravali` — Venus in 5th with Mercury aspect (artistic wealth). Saravali 42.23.
- `yoga.dhana.shakuni.jataka_parijata` — Rahu in 2nd + exalted malefic dispositor (dark-Dhana). Jataka Parijata 15.27.

### 3.5 Nabhasa Yogas — 32 total

BPHS Ch.39. Three sub-families.

**Asraya (3):** full YAMLs for Rajju (§3.2.2), Musala (§3.2.3). Remaining:
- `yoga.nabhasa.asraya.nala.bphs` — all planets in dual (dvisvabhava) signs: Gemini, Virgo, Sagittarius, Pisces. BPHS 39.4.

**Dala (10):** full YAMLs for Kamala (§3.2.4), Shakti (§3.2.5). Remaining:
- `yoga.nabhasa.dala.vapi.bphs` — all planets in 2/5/8/11 from Lagna. BPHS 39.12.
- `yoga.nabhasa.dala.yupa.bphs` — all in 1/2/3/4. BPHS 39.13.
- `yoga.nabhasa.dala.shara.bphs` — all in 4/5/6/7. BPHS 39.14.
- `yoga.nabhasa.dala.danda.bphs` — all in 7/8/9/10. BPHS 39.16.
- `yoga.nabhasa.dala.naukam.bphs` — all in 1st seven houses. BPHS 39.18.
- `yoga.nabhasa.dala.kuta.bphs` — all in 4th–10th arc. BPHS 39.19.
- `yoga.nabhasa.dala.chhatra.bphs` — all in 7th–Lagna arc. BPHS 39.20.
- `yoga.nabhasa.dala.chapa.bphs` — all in 10th–4th arc (bow). BPHS 39.21.
- `yoga.nabhasa.dala.ardha_chandra.bphs` — all in 6 consecutive houses. BPHS 39.22.

**Sankhya (19):** full YAML for Gada (§3.2.6). Remaining:
- `yoga.nabhasa.sankhya.shakata.bphs` — all 7 in 2 opposing kendra pairs (1+7 or 4+10). BPHS 39.24.
- `yoga.nabhasa.sankhya.vihaga.bphs` — all in 2 opposing non-kendra pairs. BPHS 39.25.
- `yoga.nabhasa.sankhya.shringataka.bphs` — all in 3 signs (1/5/9 pattern). BPHS 39.26.
- `yoga.nabhasa.sankhya.hala.bphs` — all in 3 non-trine signs at even intervals. BPHS 39.27.
- `yoga.nabhasa.sankhya.vajra.bphs` — planets distributed 1/7 only. BPHS 39.28.
- `yoga.nabhasa.sankhya.yava.bphs` — planets in 1/4/7/10 with specific mass distribution. BPHS 39.29.
- `yoga.nabhasa.sankhya.kamala_sankhya.bphs` — all in 4 kendras (distinct from Dala Kamala by occupancy pattern). BPHS 39.30.
- `yoga.nabhasa.sankhya.vapi_sankhya.bphs` — sibling of Dala Vapi, 5-sign dispersion. BPHS 39.31.
- `yoga.nabhasa.sankhya.yupa_sankhya.bphs` — sibling of Yupa Dala. BPHS 39.32.
- `yoga.nabhasa.sankhya.ishu.bphs` — 6 consecutive signs anchored in 3rd. BPHS 39.33.
- `yoga.nabhasa.sankhya.shakti_sankhya.bphs` — 6 signs with Mars anchoring. BPHS 39.34.
- `yoga.nabhasa.sankhya.danda_sankhya.bphs` — planets in 7 signs (each in its own). BPHS 39.35.
- `yoga.nabhasa.sankhya.naukam_sankhya.bphs` — full 7-planet spread in 8 sign arcs. BPHS 39.36.
- `yoga.nabhasa.sankhya.kutara.bphs` — asymmetric sign spread. BPHS 39.37.
- `yoga.nabhasa.sankhya.chhatra_sankhya.bphs` — sibling of Chhatra Dala counted by sign-occupancy. BPHS 39.38.
- `yoga.nabhasa.sankhya.chapa_sankhya.bphs` — sibling of Chapa Dala counted by sign-occupancy. BPHS 39.39.
- `yoga.nabhasa.sankhya.ardhachandra_sankhya.bphs` — sibling of Ardhachandra Dala. BPHS 39.40.
- `yoga.nabhasa.sankhya.samudra.bphs` — all 7 in 7 different signs. BPHS 39.41.

Note: Nabhasa Sankhya depends on **count of distinct signs occupied by the 7 classical planets**, not house positions alone. The new DSL predicate `count_distinct_signs_with_planets` (§3.14) supports this.

### 3.6 Chandra Yogas — 20 new rule summaries

- `yoga.chandra.pushkala_alt.bphs` — BPHS sibling of E4a's Saravali Pushkala. BPHS 38.10.
- `yoga.chandra.soubhagya.saravali` — Moon in Taurus/Cancer in kendra + benefic aspect. Saravali 13.14.
- `yoga.chandra.chamara.saravali` — Moon's dispositor exalted in kendra. Saravali 13.16.
- `yoga.chandra.dhana_chandra.phaladeepika` — Moon in 2nd/11th + benefic conjunction. Phaladeepika 6.23.
- `yoga.chandra.srinatha_chandra.phaladeepika` — Moon in 7th aspected by 10th lord. Phaladeepika 6.26.
- `yoga.chandra.adhama.saravali` — Moon in 12th from Lagna, no benefic aspect. Saravali 13.18.
- `yoga.chandra.sama.saravali` — Moon in 4th/8th from Lagna, neutral. Saravali 13.19.
- `yoga.chandra.varishta.saravali` — Moon in 1/7/10 from Lagna + benefic aspect. Saravali 13.20.
- `yoga.chandra.amala_chandra.bphs` — Moon-reference Amala sibling (benefic alone in 10th from Moon). BPHS 37.14 variant.
- `yoga.chandra.chandra_adhama.phaladeepika` — Moon in enemy sign aspected by malefic. Phaladeepika 6.24.
- `yoga.chandra.chandra_kendra.bphs` — Moon in kendra + kendra lord strong. BPHS 38.15.
- `yoga.chandra.chandra_trikona.bphs` — Moon in trikona + trikona lord strong. BPHS 38.16.
- `yoga.chandra.chandra_malavya.phaladeepika` — Moon + Venus in kendra (Malavya-like). Phaladeepika 6.28.
- `yoga.chandra.chandra_hamsa.phaladeepika` — Moon + Jupiter in kendra (Hamsa-like). Phaladeepika 6.29 variant.
- `yoga.chandra.purna_chandra.saravali` — Full Moon (tithi 14/15 shukla) in kendra. Saravali 13.25.
- `yoga.chandra.subha_chandra.jataka_parijata` — Moon between two benefics (benefic kartari). Jataka Parijata 10.33.
- `yoga.chandra.papa_chandra.jataka_parijata` — Moon between two malefics (papa kartari). Jataka Parijata 10.34.
- `yoga.chandra.chandra_yuti.phaladeepika` — Moon conjoined with Jupiter AND Venus. Phaladeepika 6.30.
- `yoga.chandra.rajya_chandra.saravali` — Moon exalted + in 10th + benefic aspect. Saravali 13.27.
- `yoga.chandra.bandhu_chandra.saravali` — Moon in 4th with 4th lord in kendra. Saravali 13.29.

### 3.7 Surya Yogas — 5 new rule summaries

- `yoga.surya.vargottama_sun.bphs` — Sun in same sign in Rasi and Navamsha. BPHS 38.25.
- `yoga.surya.pushkala_surya.saravali` — Sun in kendra with dispositor exalted. Saravali 14.8.
- `yoga.surya.surya_adhama.saravali` — Sun in 12th from Lagna unafflicted. Saravali 14.10.
- `yoga.surya.surya_sama.saravali` — Sun in 4th/8th from Lagna, neutral. Saravali 14.11.
- `yoga.surya.surya_varishta.saravali` — Sun in kendra/trikona + benefic aspect. Saravali 14.12.

### 3.8 Parivartana Yogas — 30 total

BPHS Ch.40. Mutual exchange (sign swap). Classified in six type-families.

**Maha (10) — Kendra↔Trikona:** full YAML for Lagna–10 (§3.2.7). Remaining: `lagna_5`, `lagna_9`, `4_5`, `4_9`, `4_10`, `7_5`, `7_9`, `10_5`, `10_9` — all `yoga.parivartana.maha.{a}_{b}.bphs`, citations BPHS 40.4–12.

**Khala (10) — Trika/Dusthana with Upachaya or adjacent:** full YAML for 6–8 (§3.2.8). Remaining: `3_6`, `3_8`, `3_12`, `6_11`, `8_11`, `12_11`, `6_3`, `8_3`, `6_12` — all `yoga.parivartana.khala.{a}_{b}.bphs`, citations BPHS 40.16–24.

**Dainya (10) — Pure dusthana-dusthana (afflictive):** `6_8`, `6_12`, `8_12`, `6_3`, `8_3`, `12_3`, `8_1`, `12_1`, `6_1`, `8_4` — all `yoga.parivartana.dainya.{a}_{b}.bphs`, citations BPHS 40.28–37.

All 30 use the new `mutual_exchange(lord_of_house_a, lord_of_house_b)` DSL predicate (§3.14).

### 3.9 Viparita Raja variants — 3 new rule summaries

Full YAMLs above for Harsha-strict (§3.2.9) and Sarala-expanded (§3.2.10). Remaining:
- `yoga.raja.viparita_vimala.bphs.strict` — 12th lord in dusthana, no benefic association, not debilitated. BPHS 37.30 strict.

### 3.10 Dushta / Arishta Yogas — 19 new rule summaries

Full YAMLs above for Kaal Sarp Anant (§3.2.15), Padma (§3.2.16), Shakata (§3.2.17), Angaraka (§3.2.18). Remaining 6 Kaal Sarp axis types + 9 other dushta:

**Remaining Kaal Sarp axes** (all `yoga.dushta.kaal_sarp.*.phaladeepika`): `kulika` (3–9, Phaladeepika 14.20), `vasuki` (4–10, 14.21), `shankapala` (5–11, 14.22), `mahapadma` (6–12, 14.23), `takshaka` (7–1, 14.24), `karkotaka` (8–2, 14.25).

**Other dushta:**
- `yoga.dushta.shrapit.regional_synthesis` — Saturn + Rahu conjunction involving 1/4/8/10 (curse yoga). Regional synthesis.
- `yoga.dushta.bhagavat_sesha.saravali` — all malefics in 8/12, unafflicted by benefics. Saravali 42.25.
- `yoga.dushta.chandal.jataka_parijata` — Jupiter + Rahu conjunction in any house (expanded Guru Chandala). Jataka Parijata 10.40.
- `yoga.dushta.pitra_dosha.sun_9th.bphs` — Sun in 9th afflicted by Saturn or Rahu. BPHS 42.7.
- `yoga.dushta.pitra_dosha.rahu_9th.saravali` — Rahu in 9th, no benefic aspect. Saravali 38.18.
- `yoga.dushta.matru_dosha.saravali` — Rahu/Ketu in 4th afflicting Moon or 4th lord. Saravali 38.20.
- `yoga.dushta.bhratru_dosha.saravali` — Mars in 3rd afflicted by Saturn + 3rd lord weak. Saravali 38.22.
- `yoga.dushta.kalatra_dosha.phaladeepika` — Venus afflicted + 7th lord in dusthana + Mars in 7th. Phaladeepika 14.14.
- `yoga.dushta.santan_dosha.phaladeepika` — 5th lord + Jupiter afflicted by Saturn/Rahu (progeny-line). Phaladeepika 14.15.

### 3.11 Named Miscellaneous Yogas — 18 new rule summaries

From Saravali Ch.18–30 + Jataka Parijata Ch.10:
- `yoga.named.hari.saravali` — Venus in kendra + Moon exalted + Lagna lord in trikona. Saravali 25.4.
- `yoga.named.hara.saravali` — Mars in 10th + Sun/Saturn in kendra. Saravali 25.5.
- `yoga.named.brahma.saravali` — Jupiter in kendra from 7th lord + benefic association. Saravali 25.7.
- `yoga.named.vishnu.saravali` — Jupiter in 9th + Moon in 5th + Venus in Lagna. Saravali 25.8.
- `yoga.named.shiva.saravali` — 9th lord in 5th + 5th lord in 9th + 10th lord in kendra. Saravali 25.10.
- `yoga.named.karta_ripu.saravali` — Lagna lord + 6th lord in mutual exchange (dark-type power). Saravali 38.6.
- `yoga.named.amsavatara.saravali` — Lagna + 3 benefics in own/exalted Navamsha. Saravali 35.12.
- `yoga.named.ganesha.jataka_parijata` — Jupiter in Lagna + Mercury in 2nd + Ketu in 5th. Jataka Parijata 10.45.
- `yoga.named.lakshmi_narayana.jataka_parijata` — Venus + Jupiter in 2nd + Moon in 11th. Jataka Parijata 10.46.
- `yoga.named.parijata_named.saravali` — Lagna lord's dispositor's dispositor exalted in kendra. Saravali 42.31.
- `yoga.named.kalpa_druma_named.saravali` — 4-step dispositor chain (L1 → D1 → D2 → Navamsha lord) all strong. Saravali 42.3.
- `yoga.named.matsya.jataka_parijata` — benefic in Lagna + malefic in 9th + mixed in 5th. Jataka Parijata 10.48.
- `yoga.named.kurma.jataka_parijata` — benefics in 5/6/7 + malefics in 1/3/11. Jataka Parijata 10.49.
- `yoga.named.varaha.jataka_parijata` — benefics in 2/9/12 + Sun + Mercury in Lagna. Jataka Parijata 10.50.
- `yoga.named.narasimha.jataka_parijata` — Mars in Leo in Lagna + Sun in 5th + Jupiter aspecting. Jataka Parijata 10.51.
- `yoga.named.vamana.jataka_parijata` — 3 benefics in Lagna + Mercury exalted. Jataka Parijata 10.52.
- `yoga.named.parasu_rama.jataka_parijata` — Mars in 10th + Saturn in 7th + Jupiter in 3rd. Jataka Parijata 10.53.
- `yoga.named.rama.jataka_parijata` — exalted Sun in Lagna + Jupiter in kendra + 9th lord in 9th. Jataka Parijata 10.54.

### 3.12 Tajaka Yogas — 16 new rule summaries (Varshaphala-gated)

All Tajaka yogas have `metadata.requires_chart_context: varshaphala`; short-circuited unless a Varshaphala chart is supplied (E5 dep). Full YAMLs above for Ithasala (§3.2.19) and Isharaaph (§3.2.20). Remaining 14 (all `yoga.tajaka.*.neelakanthi`, citations Tajaka Neelakanthi Ch.2 v.18–46):

- `nakta` — third planet mediates between two that can't form direct aspect.
- `yamya` — planet in its own house in Varshaphala.
- `mama` — a planet returning to aspect a significator.
- `manau` — "mutual respect" aspect between Varsha lord and Muntha lord.
- `kamboola` — Moon applying aspect with year lord.
- `gairi_kamboola` — Moon applying aspect but with intermediate malefic interference.
- `khallasara` — separating aspect between Muntha lord and 10th lord of Varshaphala.
- `radda` — "rejection" (applying aspect refused due to retrograde motion).
- `duphali_kuttha` — two-side rejection by both significators.
- `dutthotha_davira` — chain of applying aspects.
- `tambira` — applying aspect by retrograde.
- `kuttha` — neutralization via combustion in Varshaphala.
- `ikkabala` — single-planet domination of the year.
- `induvara` — Moon in own house of Varshaphala + year lord aspected.

### 3.13 Cross-source variant handling

Several yogas have competing classical readings. Per F8 design, each variant ships as a **sibling rule** with a distinct `rule_id` suffix identifying the source variant. Aggregation (Strategy A/B/C/D) consumes all siblings and produces either a majority verdict (A), confidence-weighted (B), source-weighted per astrologer preference (C), or hybrid (D).

Sibling examples authored or summarized:
- `yoga.raja.gaja_kesari.bphs` (E4a) + `yoga.raja.gaja_kesari.saravali_permissive` (§3.3) — Saravali permits aspect in addition to kendra occupancy.
- `yoga.raja.viparita_harsha.bphs` (E4a) + `.strict` (§3.2.9).
- `yoga.dhana.lakshmi.phaladeepika` (E4a) + `.bphs` (§3.4).
- `yoga.dhana.kubera.bphs` (§3.2.14) + `.phaladeepika` (§3.4).
- `yoga.raja.bheri.phaladeepika` (E4a) + `.saravali_permissive` (§3.3).
- `yoga.raja.kahala.phaladeepika` (E4a) + `.saravali` + `.jataka_parijata` (3-way).

All siblings share `technique_family_id: yoga` and are indistinguishable to F8 except by their per-source `source_authority` rank.

### 3.14 New DSL predicates — ~10 additions for F6

All implemented in `src/josi/services/classical/yoga/predicates.py` as pure functions; declarations in `src/josi/rules/predicates/vedic_core_e4b.yaml`.

| `op` | Signature | Used by |
|---|---|---|
| `all_planets_in_sign_group` | `planets, sign_group: chara \| sthira \| dvisvabhava, require_all` | Rajju, Musala, Nala |
| `count_distinct_signs_with_planets` | `planets, equals? \| inverted? \| scores_by_count?` | All Nabhasa Sankhya |
| `all_planets_in_adjacent_kendra_pair` | `planets, reference` | Gada, Shakata (Nabhasa) |
| `planets_occupy_houses_exactly` | `planets, required_houses, mode` | Kamala, Sankhya Kamala |
| `mutual_exchange` | `lord_of_house_a, lord_of_house_b, reference` | All 30 Parivartana |
| `all_planets_between_nodes` | `planets, from_node, to_node, direction` | All 8 Kaal Sarp subtypes |
| `applying_aspect` | `planet_faster, planet_slower, orb_degrees, aspect_type` | Ithasala, Kamboola, Nakta |
| `separating_aspect` | same signature | Isharaaph, Khallasara |
| `chart_context_is` | `context: natal \| varshaphala \| prasna` | All 16 Tajaka yogas (gate) |
| `benefics_in_house_group` / `malefics_in_house_group` | `houses, reference, minimum_*` | Shakti, Adhi, Subha Kartari |
| `house_lord_conjunct_with_benefic` / `house_lord_aspected_by_benefic` | `house, reference` | Kubera, Dhana yogas |
| `planet_conjunct_or_aspected_by` | `planet, partners` | Viparita Raja strict variants |
| `house_lord_not_debilitated` | `house, reference` | Viparita Raja strict variants |
| `applying_tightness_score` / `separating_recency_score` | `faster, slower` → 0..1 | Tajaka strength formulas |

Helper expressions for strength formulas (dispatch-table-resolved, not predicates):
- `muntha_lord`, `varsha_lord` — resolve to planet in Varshaphala context.
- `conjunction_tightness_score` — 1.0 at exact conjunction, 0 at orb limit.
- `afflictions_amplifier` — inverse of `afflictions_penalty`; for dushta yogas more affliction = higher strength.
- `inverse_planet_dignity` — for dushta yogas.
- `dignity_balance_score` — measures coexistence of benefic/malefic in a house group.

### 3.15 Engine reuse — no engine changes

`YogaEngine` from E4a is reused as-is. The only touches:
1. `predicate_registry.py` gains the ~10 new `op` entries via registration.
2. `strength_formulas.py` gains the 5 helper expressions.
3. `rule_registry_loader.py` discovers 190 additional YAMLs — loader is glob-based, no code change.
4. `chart_state.py` gains a `context: Literal["natal", "varshaphala", "prasna"]` field; Tajaka rules short-circuit when context mismatches. Default `"natal"` so E4a behavior is unchanged.

This PRD is additive across the stack. No migration needed; `classical_rule` table absorbs new rows on next app startup via the idempotent loader.

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| Can a rule require context beyond natal chart? | Yes via `chart_context_is`; engine short-circuits on mismatch | Tajaka yogas need Varshaphala; short-circuiting avoids false-inactive records |
| Cross-source disagreement (BPHS vs Saravali)? | Sibling rules with distinct `rule_id`, shared `technique_family_id`; F8 aggregation handles consensus | Classical practice recognizes both; surfacing both is more accurate than collapsing |
| Nabhasa Sankhya needs "count of distinct signs occupied" — unsupported today | Add `count_distinct_signs_with_planets` predicate | Pure function of planet-sign map already in `ChartState` |
| Parivartana needs mutual-exchange detection | Add `mutual_exchange(lord_a, lord_b)` predicate | One predicate serves all 30 Parivartana yogas |
| Viparita Raja "in dusthana" definition | 6, 8, or 12 explicit; strict variant also requires not debilitated | Classical texts vary; strict captures canonical alternate reading |
| Tajaka rules require Varshaphala but E5 isn't live | Ship YAMLs; engine short-circuits until E5 lands | Decouples content from engine; when E5 ships, Tajaka activates instantly |
| Multiple Nabhasa yogas simultaneously? | Yes; emit all that match | Classical texts: a chart can carry multiple; strongest dominates but all present |
| Kaal Sarp: 1 rule with subtype field, or 8 rules? | **8 separate rules** | Each subtype has distinct classical effects; separate rules preserve per-subtype tests + AI citations |
| Strength semantics for dushta yogas | `[0, 1]` always means "how strongly the rule applies"; UX flips to "how afflictive" | Consistency across engines; UX knows the category |
| Kuja Dosha Moon/Venus refs — 3 separate rules or 1 with OR? | 1 rule, 3 OR clauses (E4a choice preserved) | Matches classical "Kuja Dosha" as single doctrinal concept |
| Where do Tajaka "Muntha" / "Varsha lord" come from? | Resolved by `chart_state.varshaphala_context` when present | Added to ChartState optional fields by E5 |
| Dainya vs Khala Parivartana disambiguation | Ship both rule_ids; Dainya is stricter (pure dusthana); Khala is broader | BPHS Ch.40 differentiates by emphasis |
| Engine emit "Nabhasa-Absent" negative rules? | No | Activation is always positive; UX infers absence from lack of rows |
| Yoga naming conflicts across regional traditions | `classical_names.en` primary; regional synonyms in free-text array (non-hashed) | Regional searchability |
| Parivartana when both lords also aspect each other | One rule; activation = exchange; aspect rewarded via strength | Cleaner separation of activation vs. strength |

## 5. Component Design

### 5.1 Files added

```
src/josi/rules/yogas/
├── bphs/{nabhasa,parivartana,raja,dhana,chandra,surya}/ ...
├── saravali/{raja,dhana,chandra,surya,dushta,named}/ ...
├── phaladeepika/{raja,dhana,dushta,chandra}/ ...
├── jataka_parijata/{named,raja,dhana}/ ...
└── tajaka_neelakanthi/*.yaml (16 files)

src/josi/rules/predicates/
└── vedic_core_e4b.yaml               # new predicate declarations

src/josi/services/classical/yoga/
├── predicates.py                      # +10 new predicates registered
├── strength_formulas.py               # +5 helper expressions
└── chart_state.py                     # +context field; +optional varshaphala_context

tests/golden/charts/yoga/e4b/         # 190+ new golden test charts
tests/unit/services/classical/yoga/
├── test_predicates_e4b.py
├── test_nabhasa_yogas.py
├── test_parivartana_yogas.py
├── test_tajaka_yogas.py
├── test_kaal_sarp_yogas.py
└── test_cross_source_variants.py
```

### 5.2 Data model — no schema changes

`classical_rule` table (F2) absorbs 190 additional rows. No DDL.

### 5.3 API contract

No new endpoints. Existing `GET /api/v1/charts/{chart_id}/yogas` returns the superset. New query params:

```
GET /api/v1/charts/{chart_id}/yogas
  ?category=nabhasa|parivartana|tajaka|...
  ?subcategory=asraya|dala|sankhya|maha|khala|dainya
  ?min_strength=0.5
  ?source=bphs|saravali|phaladeepika|jataka_parijata|tajaka_neelakanthi
  ?include_inactive=false
  ?context=natal|varshaphala    # defaults to natal
```

Response payload shape unchanged from E4a.

### 5.4 Rule-authoring workflow

For each of the ~170 yogas authored post-PRD-merge:

1. **Source selection.** Classical advisor identifies primary verse citation. If sources disagree, sibling rules.
2. **Draft authoring.** Engineer (P2) or advisor (P3+, post P3-E2-console) composes YAML in a PR.
3. **Structural review.** CI validates against DSL grammar (F6) + predicate signatures (§3.14).
4. **Content review.** Dual review: advisor approves citation + Sanskrit names; engineer approves predicate choice + strength formula.
5. **Golden fixture.** ≥1 activating chart (famous-chart from B.V. Raman's catalogue preferred). If none, property-tested synthetic chart with a one-line justification.
6. **Cancellation variant.** If text specifies cancellations, encode inline (E4a Kemadruma pattern) or as sibling cancellation rule (E4a Kuja Dosha Bhanga pattern).
7. **Merge + deploy.** Rule loads on next app start. Compute rows backfill via F3 worker (async, non-blocking).

SLA: yoga-N → production in **< 10 business days** from the moment the verse citation is received, assuming no cross-source research.

## 6. User Stories

### US-E4b.1: Astrologer queries Nabhasa yogas

**Role:** Pro-mode astrologer. **Want:** query Josi for Nabhasa yogas with confidence scores per source.
**Acceptance:** `GET /charts/{id}/yogas?category=nabhasa` returns all matching yogas across sub-categories (Asraya/Dala/Sankhya) with strength, source, citation; Strategy C is default in Pro mode.

### US-E4b.2: End user sees Kaal Sarp subtype correctly named

**Role:** B2C end user. **Want:** "You have Kaal Sarp Padma Yoga (Phaladeepika tradition)" not "You have Kaal Sarp."
**Acceptance:** AI chat tool `get_yoga_summary` surfaces the subtype name; 8 distinct Kaal Sarp axis types return correct subtype when axis matches; only one Kaal Sarp subtype active at a time per chart.

### US-E4b.3: Astrologer sees cross-source disagreement

**Role:** Pro-mode astrologer. **Want:** when BPHS and Saravali disagree on Gaja Kesari, see both readings with citations.
**Acceptance:** chart shows `yoga.raja.gaja_kesari.bphs` (active) and `yoga.raja.gaja_kesari.saravali_permissive` (active, different strength); Strategy D (default) surfaces consensus + per-source breakdown on expand.

### US-E4b.4: Developer adds yoga #261

**Role:** backend engineer. **Want:** add a yoga outside the 250 set.
**Acceptance:** author YAML, run `poetry run validate-rules`, add golden test, open PR; dual-review closes within 48h; rule ships in next deploy without engine code changes.

### US-E4b.5: Ultra AI user consults all sources for Parivartana

**Role:** Ultra-AI-mode premium user. **Want:** 3-way BPHS vs Saravali vs Phaladeepika take on Maha Parivartana.
**Acceptance:** AI chat synthesizes all sibling rules and presents the synthesis as an internal "debate" with verse citations.

## 7. Tasks

### T-E4b.1: DSL predicate additions

- **Def:** Implement ~10 new predicates in `predicates.py` + declarations in `rules/predicates/vedic_core_e4b.yaml`.
- **Accept:** each predicate has ≥3 unit tests; `validate-rules` CLI rejects malformed predicate calls; predicate YAMLs round-trip through loader.
- **Effort:** 4 days. **Depends on:** E4a, F6.

### T-E4b.2: Strength formula helper expressions

- **Def:** Implement 5 new helpers in `strength_formulas.py`.
- **Accept:** each has unit tests; integration test verifies end-to-end rule load + evaluation.
- **Effort:** 2 days. **Depends on:** T-E4b.1.

### T-E4b.3: Author Wave 0 — 20 full-YAML rules

- **Def:** Author the 20 full YAMLs from §3.2 and check them into `src/josi/rules/yogas/...`.
- **Accept:** all 20 load; `technique_compute` rows produced for each against sample chart; golden fixtures exist.
- **Effort:** 5 days. **Depends on:** T-E4b.1, T-E4b.2.

### T-E4b.4: Wave 1 — Nabhasa (32) + Parivartana (30)

- **Def:** Remaining 62 YAMLs using §3.14 predicates.
- **Accept:** all 62 load; golden fixtures green; differential vs JH < 2%.
- **Effort:** 10 days. **Depends on:** T-E4b.3.

### T-E4b.5: Wave 2 — Raja (25) + Dhana (30)

- **Accept:** 55 YAMLs load; golden green; cross-source sibling correctness verified. **Effort:** 9 days. **Depends on:** T-E4b.3.

### T-E4b.6: Wave 3 — Chandra (20) + Surya (5) + Viparita (3) + Named (18)

- **Accept:** 46 YAMLs load; golden green. **Effort:** 8 days. **Depends on:** T-E4b.3.

### T-E4b.7: Wave 4 — Tajaka (16) + Dushta (19)

- **Accept:** 35 YAMLs load; Tajaka short-circuits on natal; dushta golden green. **Effort:** 7 days. **Depends on:** T-E4b.3.

### T-E4b.8: Cross-source variant correctness test suite

- **Def:** Tests targeting sibling pairs (Gaja Kesari bphs vs saravali, Lakshmi pairs, etc.). Verify F8 aggregation.
- **Accept:** 15+ sibling-pair tests across A/B/C/D strategies; all green. **Effort:** 3 days.

### T-E4b.9: Golden chart fixture expansion

- **Def:** 190 golden charts in `tests/golden/charts/yoga/e4b/`.
- **Accept:** 100% of 190 new rule_ids have ≥1 activating fixture; golden suite green. **Effort:** 6 days (parallelizable).

### T-E4b.10: Property tests

- **Def:** Hypothesis-based invariant tests (§8.3).
- **Accept:** 12+ property tests green; ≥3 previously-latent bugs found + fixed. **Effort:** 3 days. **Depends on:** F17.

### T-E4b.11: API + AI tool-use updates

- **Def:** Extend `get_yoga_summary` AI tool to accept `category` filter; update OpenAPI for `/yogas` query params.
- **Accept:** AI chat can query per-category; contract tests green. **Effort:** 1 day.

### T-E4b.12: Observability

- **Def:** Extend P3-E8-obs dashboards for per-rule activation rates; alert on rules that never activate across 1000+ charts.
- **Accept:** dashboard shows per-rule rate; alert fires on 0% rules after 48h. **Effort:** 2 days.

### T-E4b.13: Rollout & feature flags

- **Def:** Gate each wave behind a flag; ship waves sequentially over 4 sprints.
- **Accept:** all 4 waves in production; all flags removed after 100% rollout. **Effort:** 1 day per wave.

### T-E4b.14: Documentation

- **Def:** Update CLAUDE.md, API docs, authoring guide (§5.4).
- **Accept:** new reviewer can onboard + author a yoga in < 1 hour. **Effort:** 1 day.

### T-E4b.15: Differential testing vs Jagannatha Hora

- **Def:** 500 random charts; compute via both Josi E4b and JH; log + investigate disagreements.
- **Accept:** per-rule disagreement rate < 2%; disagreements classified (bug / variant / JH-bug / orb difference). **Effort:** 4 days.

## 8. Unit Tests

Coverage model: 250 × 5 hand-written tests each is infeasible. Strategy:

- **80% of yogas (~200)** have a direct fixture-based test: known-activating chart → assert `active=true`, `strength > 0`.
- **20% (~50)** covered exclusively by property tests (mutual-exclusion, count-cardinality invariants).
- **All ~10 new predicates** have direct unit tests (≥3 input cases each).
- **All ~5 new strength helpers** have direct unit tests (≥2 cases each).
- **Cross-source sibling pairs** get dedicated tests (~15+ pairs × 1–2 tests each).

### 8.1 Predicate unit tests (`test_predicates_e4b.py`)

| Test | Input | Expected | Rationale |
|---|---|---|---|
| all_planets_in_sign_group_chara_true | 7 planets in Aries/Cancer/Libra/Cap | `True` | Rajju baseline |
| all_planets_in_sign_group_false_one_fixed | 6 chara + 1 fixed | `False` | Strictness |
| count_distinct_signs_equals_2 | Planets in Aries + Libra only | `2` | Shakata/Gada support |
| count_distinct_signs_equals_7 | 7 planets in 7 signs | `7` | Samudra support |
| mutual_exchange_1_10 | L1 in sign-of-L10 AND L10 in sign-of-L1 | `True` | Maha Parivartana core |
| mutual_exchange_single_ended_false | Only L1 swapped, L10 elsewhere | `False` | Must be mutual |
| all_planets_between_nodes_true | Rahu 1st, Ketu 7th, 7 planets in 2–6 | `True` | Kaal Sarp |
| chart_context_varshaphala_pass | `ctx='varshaphala'` | `True` | Tajaka gate |
| chart_context_varshaphala_fail | `ctx='natal'` | `False` | Tajaka short-circuit |
| applying_aspect_true | Fast planet approaching slow within orb | `True` | Ithasala |
| separating_aspect_true | Fast planet past slow within orb | `True` | Isharaaph |
| planets_occupy_houses_kendra | All 7 in {1,4,7,10} | `True` | Kamala (Dala) |
| house_lord_not_debilitated | 6th lord in own sign | `True` | Viparita strict guard |
| applying_tightness_score_exact | 0° separation | `1.0` | Strength boundary |
| applying_tightness_score_at_orb | 7° at max orb | `0.0` | Strength boundary |

### 8.2 Yoga-level integration tests

| Category | # Tests | Strategy |
|---|---:|---|
| Raja (25 new) | 25 | 1 activating chart per yoga |
| Dhana (30 new) | 30 | 1 per yoga |
| Nabhasa Asraya (3) | 3 | All-chara/sthira/dual charts |
| Nabhasa Dala (10) | 10 | Representative distributions |
| Nabhasa Sankhya (19) | 15 | 15 direct; 4 by property |
| Chandra (20 new) | 20 | 1 per yoga |
| Surya (5 new) | 5 | 1 per yoga |
| Parivartana (30) | 30 | 1 per lord-pair |
| Viparita (3 new) | 3 | 1 per variant |
| Dushta (19 new) | 19 | 1 per yoga; 8 Kaal Sarp each |
| Named Misc (18) | 18 | 1 per yoga |
| Tajaka (16) | 16 | 1 per yoga, synthetic Varshaphala |
| **Total (new)** | **~194** | |

### 8.3 Property tests (`test_yoga_properties.py`)

| Test | Property | Rationale |
|---|---|---|
| no_yoga_on_empty_chart | Empty ChartState → no rule activates | Defensive |
| at_most_one_kaal_sarp_subtype | ≤1 of 8 Kaal Sarp rules activates per chart | Subtype exclusivity |
| nabhasa_asraya_mutually_exclusive | ≤1 of Rajju/Musala/Nala activates | Sign-group exclusivity |
| gada_and_samudra_disjoint | Gada (2 signs) and Samudra (7 signs) can't both activate | Cardinality |
| parivartana_mutual | `mutual_exchange(a,b) ⇔ mutual_exchange(b,a)` | Symmetry |
| tajaka_never_on_natal | All Tajaka inactive when `ctx='natal'` | Short-circuit |
| tajaka_activates_on_varshaphala | Hypothesis-generated VP contexts → ≥1 Tajaka rule | Engine wiring |
| strength_in_bounds | Every active rule: `0 ≤ strength ≤ 1` | Clamp correctness |
| viparita_strict_implies_base | Strict active ⇒ base active | Strict ⊆ base |
| gaja_kesari_sibling_not_equivalent | Saravali form activates when BPHS doesn't (not vice-versa) | Sibling semantics |
| kaal_sarp_requires_between_nodes | Any Kaal Sarp activation ⇒ all-between-nodes true | Invariant |
| parivartana_maha_non_dusthana | Maha ⇒ neither lord owns a dusthana | Category integrity |

### 8.4 Cross-source variant tests (`test_cross_source_variants.py`)

| Test | Scenario | Expected |
|---|---|---|
| gaja_kesari_bphs_vs_saravali | Jupiter aspecting Moon, not in kendra | Saravali active, BPHS inactive |
| kubera_bphs_vs_phaladeepika_concur | Chart satisfies both | Both active |
| lakshmi_phaladeepika_vs_bphs | Only Phaladeepika form satisfied | Phaladeepika active, BPHS inactive |
| kahala_triple_sibling | Chart activates all 3 Kahala siblings | 3 compute rows |
| viparita_harsha_strict_vs_base | 6th lord combust | Base active, strict inactive |
| aggregation_A_simple_majority | 2/3 siblings active | Strategy A: `active=true` |
| aggregation_B_confidence | 2/3 active | Confidence = 0.67 |
| aggregation_C_source_weighted | Astrologer weights BPHS > Saravali | Active iff BPHS active |
| aggregation_D_hybrid | End-user sees B flat; astrologer sees C | Shape validated |

## 9. EPIC-Level Acceptance Criteria

PRD is "done" when ALL pass:

- [ ] 190 new yoga YAMLs authored + loaded via `RuleRegistryLoader` (total 250 incl. E4a).
- [ ] 20 full YAMLs from §3.2 shipped as authored.
- [ ] Remaining ~170 yogas follow the §3.3–§3.12 summaries; each has a golden fixture.
- [ ] F6 DSL extended with 10 new predicates; declarations in `src/josi/rules/predicates/vedic_core_e4b.yaml`.
- [ ] `predicates.py` implements all 10; each ≥3 unit tests.
- [ ] `strength_formulas.py` implements 5 helpers; each ≥2 unit tests.
- [ ] `ChartState.context: Literal["natal","varshaphala","prasna"]` added, default `"natal"`.
- [ ] Tajaka yogas (16) short-circuit to `active=false` on `context="natal"`; verified by property test.
- [ ] Golden suite grows with ≥1 activating chart per yoga (190 new fixtures).
- [ ] 15+ cross-source sibling pair tests green.
- [ ] 12+ property tests green.
- [ ] Differential vs Jagannatha Hora: per-rule disagreement < 2%.
- [ ] Yoga activation rates surfaced per rule on P3-E8-obs dashboards.
- [ ] Zero "rule-never-activates" alerts after 48h.
- [ ] API `/yogas` query params (`category`, `subcategory`, `source`, `min_strength`, `include_inactive`, `context`) contract-tested.
- [ ] AI tool `get_yoga_summary` supports category filter + F8 strategy-based aggregation.
- [ ] Unit-test coverage for new code ≥ 90%.
- [ ] CLAUDE.md + authoring guide updated; reviewer onboards + authors a yoga in < 1 hour.
- [ ] No engine-code changes needed for hypothetical yoga #261 (smoke-test authored).

## 10. Rollout Plan

- **Feature flags:** `yoga_e4b_wave_0` (20 representative) → `wave_1` (Nabhasa+Parivartana) → `wave_2` (Raja+Dhana) → `wave_3` (Chandra+Surya+Viparita+Named) → `wave_4` (Tajaka+Dushta). Default off; promoted per wave after golden green.

- **Wave cadence (6 sprints):**
  - Wave 0: Sprint 1 (foundation + DSL extensions + 20 representative).
  - Wave 1: Sprints 2–3 (62 yogas; highest DSL-novelty).
  - Wave 2: Sprints 3–4 (55 yogas; sibling-rule-heavy).
  - Wave 3: Sprints 4–5 (46 yogas).
  - Wave 4: Sprints 5–6 (35 yogas; Tajaka gated on E5).

- **Shadow compute:** Y — 24h before each wave's flag flip, `technique_compute` rows produced but not surfaced via API. Verifies no regression; measures compute cost.

- **Backfill:** F3 worker backfills `technique_compute` for existing charts when new rules activate. Per master-spec §8.3: full backfill < 24h at 10M charts. Gate: pause wave promotion if queue exceeds 100k.

- **Rollback:** flip flag off → UI surfaces revert; `technique_compute` rows retained (append-only). For authoring errors post-rollout: bump `effective_to` on affected rows; engine stops evaluating at next compute; re-author ships with new `effective_from`.

- **Tajaka gating:** if E5 is not live at Wave 4 flip time, Tajaka rules remain short-circuited (always `active=false` for natal). When E5 ships, no re-deploy needed — short-circuit naturally lifts.

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---:|---:|---|
| Classical disagreement exceeds 30 sibling pairs | Medium | Medium | Sibling pattern built (E4a + here); absorbs more siblings without engine changes |
| Scale: 250 × 5 sources × N charts = 5×-growth in compute | Medium | High | F3 partitioning + content-hashed caching (F13); compute idempotent; monitor Wave 2 |
| Rule-authoring bottleneck with 2–3 trained authors | High | Medium | P3-E2 console unblocks advisors; documented workflow (§5.4) lets engineers author with advisor review in 48h |
| New predicate bug (`mutual_exchange` mis-handles nodes) mis-activates 30+ yogas | Medium | High | Predicate unit tests on critical path; property tests catch class-wide bugs; feature flag per wave allows rollback |
| Nabhasa DSL predicates (count-distinct-signs) fragile | Low | Medium | Dedicated test file; property test for Asraya exclusivity |
| Yoga naming conflicts across regional traditions | Low | Low | `classical_names` supports 4+ languages; regional synonyms in free-text array |
| Tajaka lands before E5 | Medium | Low | Short-circuit via `chart_context_is`; natal returns `active=false` cleanly |
| Differential vs JH > 2% | Medium | High | Investigate each disagreement class (bug/variant/JH-bug/orb); if variant, add sibling with `source_id: jagannatha_hora`; recompute target |
| Golden fixture maintenance burden grows | High | Medium | Reuse famous-chart library across similar yogas; "1 chart per yoga" as minimum, not max |
| AI chat token budget blown by 50+ active yogas | Medium | Medium | `get_yoga_summary` respects `min_confidence` + `min_strength`; surface top-N with "X more" affordance |
| 190 new YAMLs create noisy PRs | Medium | Low | One-yoga-per-PR convention; CI threshold |

## 12. References

- Master spec: `docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`
- Predecessor PRD: `docs/markdown/prd/P1/E4a-yoga-engine-mvp.md`
- Foundation PRDs: `docs/markdown/prd/P0/F1-star-schema-dimensions.md`, `F6-rule-dsl-yaml-loader.md`, `F8-aggregation-strategies.md`, `F13-content-hash-provenance.md`, `F16-golden-chart-suite.md`, `F17-property-test-harness.md`
- Related: `docs/markdown/prd/P2/E5-varshaphala-tajaka.md` (Tajaka chart-context source)
- Classical primary sources: *BPHS* Ch.27, 36–43 (esp. Ch.39 Nabhasa, Ch.40 Parivartana); *Saravali* (Kalyana Varma) Ch.13, 14, 18–30, 35, 38, 42; *Phaladeepika* (Mantreshwara) Ch.6 (Raja), 14 (dushta + Kaal Sarp), 15 (Dhana); *Jataka Parijata* (Vaidyanatha Dikshita) Ch.10 (Raja, Misc), 15 (Dhana); *Tajaka Neelakanthi* (Neelakantha) Ch.2.
- Secondary: B.V. Raman, *Notable Horoscopes* (fixtures), *Three Hundred Important Combinations*; K.N. Rao, *Yogas in Astrology*.
- Reference implementations: Jagannatha Hora 7.x (differential target), Maitreya 9.
