---
prd_id: D3
epic_id: D3
title: "Localization to 20+ languages × native astrological traditions"
phase: P5-dominance
tags: [#i18n, #extensibility, #correctness, #multi-tenant]
priority: must
depends_on: [F1, F4, F6, F7, F8, P3-E2-console, P4-E4-tenant]
enables: [D1, D4, D9, D11, I10]
classical_sources: [tibetan_tsi, sufi_ilm_al_nujum, west_african_ifa, native_american_medicine_wheel, mayan_tzolkin, hellenistic]
estimated_effort: 16-24 weeks (multi-tradition)
status: draft
author: "@agent"
last_updated: 2026-04-19
---

# D3 — Localization to 20+ Languages × Native Traditions

## 1. Purpose & Rationale

Most "international" astrology apps translate English horoscopes. That misses the point. Every culture has its own divinatory tradition — often with classical texts, specialized language, and practitioners. Josi's extensibility architecture (F1 source_authority dim + F6 YAML rule DSL + F8 aggregation) was designed precisely so that new traditions are **content, not code**.

This PRD operationalizes that extensibility payoff. For each new tradition, the engineering work is: seed new `source_authority` rows, author YAML rules, wire output_shapes if novel, run golden charts. No schema changes, no aggregation changes.

The moat is two-fold:
1. **Breadth** — no competitor offers Tibetan Tsi + Sufi Ilm al-Nujum + West African Ifa + Native American Medicine Wheel + Mayan Tzolkin + Celtic Ogham + Chinese BaZi + Vedic + Western in one platform.
2. **Respect** — each tradition is authored *with* community advisors, cited, attributed, and the UI respects the source context (not just "exotic content").

## 2. Scope

### 2.1 In scope
- New traditions at launch (priority order, each ships independently):
  1. Tibetan Tsi (Tibetan astrology — elements, mewas, parkhas, birth animals)
  2. Sufi / Islamic Ilm al-Nujum (lunar mansions / *al-manazil*, hour rulership, *ruhaniyyat*)
  3. West African Ifa divination (256 odus, binary-casting, consultant framing)
  4. Native American Medicine Wheel (directions, animal totems, seasonal alignment — with tribal-specific variants respected, not collapsed)
  5. Mayan Tzolkin (20 day-signs × 13 numbers, already partially supported — extending to full classical system)
  6. Celtic Ogham tree calendar (13 tree-months + divination)
  7. Hellenistic depth (whole-sign, triplicities, bounds — expanding existing Western)
- Language expansion to 20+ at launch: ta, hi, en, te, bn, mr, kn, ml, pa, gu, ur, ne, si, zh, ja, ko, ar, fa, id, vi, es, pt, fr, de, ru, sw
- Content localization for all existing techniques (yoga names, dasha descriptions, panchang elements) — not just translation but **cultural-appropriate phrasing** per native speakers
- Tradition-picker UX: user (or astrologer) picks which traditions are active for their reading
- Per-tradition source_authority default weights maintained separately from existing dims
- Advisor partnership protocol: every new tradition requires named advisor(s) with written sign-off

### 2.2 Out of scope
- AI-generated interpretations in native-tradition content without advisor oversight (all launch content is advisor-authored)
- Full calendrical systems for every tradition (e.g., we do Tibetan lunar months, but not Tibetan Phugpa vs Tsurphu calendar debate yet — that's P6)
- Voice (D1) in all 20+ languages at the *same* launch — D3 ships text first; D1 catches up per-language later
- Commercial claims about efficacy of any tradition

### 2.3 Dependencies
- F1 source_authority dim must accept new traditions via YAML PR (already supported)
- F6 rule DSL must support new output shapes (e.g., binary casting for Ifa)
- F7 output_shape JSON schemas — may need new shapes for some traditions
- P3-E2-console for non-engineer classical authors (especially advisors without coding background)
- P4-E4-tenant rule overrides for institutional users who want their tradition-variant

## 3. Classical / Technical Research

### 3.1 Tradition inventory and sources

| Tradition | Key source(s) | Output shapes | Advisor type |
|---|---|---|---|
| Tibetan Tsi | *rTsis gzhung gyi mdzes rgyan* (Tsi Treatises); *Kalachakra Tantra* derivatives | structured_positions, categorical (mewas, parkhas) | Tibetan Buddhist lineage holders |
| Sufi Ilm al-Nujum | *Kitab al-Bari' fi ahkam al-nujum* (al-Biruni); *Al-Madkhal al-Kabir* (Abu Ma'shar) | structured_positions, temporal_event | Sufi scholars; Islamic studies academics |
| West African Ifa | Odu Ifa corpus (256 odus, oral tradition + 20th-century codifications) | boolean_with_strength (per odu activation), categorical | Babalawo lineage practitioners |
| Native American Medicine Wheel | Tribe-specific; no single classical text; oral tradition + contemporary teachings | categorical, structured_positions | Tribal-specific knowledge holders; respect sovereignty |
| Mayan Tzolkin (full) | *Popol Vuh* astronomy sections; Dresden/Madrid codices | categorical, temporal_hierarchy | Maya academics; Daykeepers (Ajq'ij) |
| Celtic Ogham | *Auraicept na nÉces*; medieval tree-calendar compilations | categorical, temporal_range | Celtic studies academics |
| Hellenistic depth | Vettius Valens *Anthology*; Ptolemy *Tetrabiblos*; Firmicus Maternus | structured_positions, temporal_hierarchy | Existing Western advisors + classicists |

### 3.2 Why these first, not others

Chinese BaZi is already core (covered in P1/P2). Jewish kabbalistic numerology, runic systems (Futhark), I-Ching are deferred to P6 (I8). The launch 7 are chosen because:
- Major living tradition with practitioners requesting inclusion
- Documented classical/oral source corpus to cite
- Named advisors identified or identifiable
- Distinct technique_family that adds non-redundant signal

### 3.3 Language matrix

20+ languages × (existing content + new tradition content) = large. Strategy:
- **Tier-1 languages** (ta, hi, en, zh, ar, es) — fully localized UX, content, advisor-reviewed interpretations
- **Tier-2 languages** (te, bn, mr, kn, ml, pa, gu, ur, ja, ko) — UX + content; advisor review where possible
- **Tier-3 languages** (ne, si, fa, id, vi, pt, fr, de, ru, sw) — UX + machine-translated content with native-speaker spot check; advisor review expansion path

Each tier has a gate for promotion.

### 3.4 Technical approach

Extensibility architecture means per-tradition work is:
1. YAML PR adding `source_authority` rows
2. YAML PRs adding rules under the appropriate `technique_family` (or new family if needed)
3. Optional: new `output_shape` + JSON schema if data shape is novel (e.g., Ifa binary casting)
4. Translation files in standard i18n format (e.g., ICU MessageFormat)
5. Golden chart additions per tradition
6. Feature flag per tradition for gradual rollout

No Python code change for a new tradition unless a new output shape is required. Even then, the change is small (register shape in F7).

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| Machine translation vs human | Human for tier-1/2 tradition content; MT + spot-check for tier-3 UX strings | Classical content mistranslation damages trust; UX strings tolerate MT |
| Collapse Medicine Wheel across tribes | No — respect tribal-specific variants; offer as separate source_ids | Sovereignty; accuracy |
| Include contested sources | Only with advisor sign-off and explicit provenance note | Trust via transparency |
| Ship all 7 traditions at once | No — ship per-tradition as ready | Velocity + per-tradition gates |
| Allow users to mix traditions in one reading | Yes (per Decision 2 in master spec — Ultra AI ensemble) | Core product thesis |
| How to handle tradition-specific birth data | Per-tradition birth-data supplement fields via `technique_family` metadata | Some traditions need extra inputs (e.g., Tibetan element of birth year) |

## 5. Component Design

### 5.1 New modules

```
src/josi/content/traditions/
├── tibetan_tsi/
│   ├── source_authority.yaml
│   ├── rules/
│   └── advisor_signoff.md
├── sufi_ilm_al_nujum/
├── west_african_ifa/
├── native_american_medicine_wheel/
│   ├── dine/        # tribe-specific subdirs
│   ├── lakota/
│   └── ...
├── mayan_tzolkin/
├── celtic_ogham/
└── hellenistic_depth/

src/josi/i18n/
├── locales/
│   ├── hi/
│   ├── ta/
│   ├── ... (20+ locales)
└── translator.py                # ICU MessageFormat loader

src/josi/services/classical/
└── tradition_registry.py        # enumerates active traditions + their families
```

### 5.2 Data model additions

No schema changes. Only:
- Additional rows in `source_authority` (YAML-seeded via F1 loader)
- Additional rows in `technique_family` if a tradition needs a new family (e.g., `ifa_casting`)
- Additional rows in `output_shape` + JSON schema in F7 if data shape is novel
- New golden charts per tradition

User preference extension:

```sql
-- Reusing existing astrologer_source_preference, adding:
ALTER TABLE astrologer_source_preference
    ADD COLUMN IF NOT EXISTS active_traditions TEXT[] DEFAULT NULL;
-- NULL = all traditions active; array = filter
```

Per-user locale already exists in `user_account`.

### 5.3 API contract

```
GET /api/v1/traditions
Response: list of active traditions with source_ids, supported languages,
          required_birth_data_extras

POST /api/v1/charts/{id}/read?traditions=vedic,tibetan_tsi&locale=hi
Response: citation-embedded reading in Hindi with both Vedic and Tibetan Tsi
          source attributions
```

## 6. User Stories

### US-D3.1: As a Tibetan Buddhist user, I want my reading to include Tsi-tradition interpretation
**Acceptance:** toggling Tibetan Tsi in my preferences adds Tsi-authored segments to my reading; citations reference classical texts; UX labels correct in Tibetan or English-transliterated Tsi terminology.

### US-D3.2: As a Bengali speaker, I want my reading entirely in Bengali including yoga names
**Acceptance:** yoga names, nakshatra names, dasa names rendered in Bengali script with proper transliteration; advisor sign-off on translations.

### US-D3.3: As a Babalawo practitioner, I want Ifa odu activations for my birth moment alongside my Vedic chart
**Acceptance:** Ifa casting algorithm (based on birth moment as casting event) returns activated odus with verse references from Odu Ifa corpus; visible alongside Vedic analysis.

### US-D3.4: As a non-English speaker at launch, I get tier-3 UX with machine-translated strings but accurate classical content
**Acceptance:** UX strings MT with spot-check; classical content (yoga descriptions, dasa interpretations) either human-reviewed or clearly marked "MT — advisor review pending."

### US-D3.5: As an astrologer, I want to filter my workbench to only the traditions I practice
**Acceptance:** preference saved; workbench UI (E12) respects filter; API calls with `traditions=` param return only selected.

### US-D3.6: As a tradition advisor, I can submit a new rule as a YAML PR without touching Python
**Acceptance:** P3-E2-console allows advisors to author rules; preview + golden chart validation in console before PR merge.

### US-D3.7: As a user, I want to opt out of a tradition I don't want to see
**Acceptance:** preference toggle per tradition; default off for culturally specific traditions (Medicine Wheel); default on for cross-cultural (Hellenistic, Mayan Tzolkin).

## 7. Tasks

### T-D3.1: Advisor partnerships + MOUs per tradition
- **Definition:** Identify, approach, contract with at least 2 advisors per tradition; sign-off protocol.
- **Acceptance:** signed MOUs; named advisors listed in `advisor_signoff.md` per tradition.
- **Effort:** 4-8 weeks (ops, not engineering; ongoing)

### T-D3.2: Tibetan Tsi YAML + rules + golden charts
- **Definition:** Author YAML rules for elements, mewas, parkhas, birth-animal system; 20 golden charts.
- **Acceptance:** advisor sign-off; all golden charts pass.
- **Effort:** 3 weeks

### T-D3.3: Sufi Ilm al-Nujum YAML + rules + golden charts
- **Definition:** Al-manazil (28 lunar mansions), hour rulership, *ruhaniyyat* correspondences.
- **Acceptance:** advisor sign-off; 20 golden charts pass.
- **Effort:** 3 weeks

### T-D3.4: West African Ifa casting engine + odu catalog
- **Definition:** Birth-moment-based casting algorithm; 256 odu registry; verse references.
- **Acceptance:** advisor sign-off; casting deterministic and reproducible.
- **Effort:** 4 weeks (new output shape + algorithm)

### T-D3.5: Native American Medicine Wheel (per-tribe subdirs)
- **Definition:** Start with Dine, Lakota, Ojibwe variants; tribal-specific advisor sign-off REQUIRED; no cross-tribal aggregation.
- **Acceptance:** each subdir has independent advisor sign-off; UX never conflates tribes.
- **Effort:** 4-6 weeks

### T-D3.6: Mayan Tzolkin full depth
- **Definition:** Beyond day-sign/number: trecena positions, venus-table cross-reference, classical Maya cosmology links.
- **Acceptance:** advisor sign-off; 20 golden charts.
- **Effort:** 3 weeks

### T-D3.7: Celtic Ogham tree calendar
- **Definition:** 13 tree-months, ogham-letter correspondences, divination rules.
- **Acceptance:** advisor sign-off; 20 golden charts.
- **Effort:** 2 weeks

### T-D3.8: Hellenistic depth
- **Definition:** Triplicities, bounds (Egyptian/Ptolemaic/Porphyry), whole-sign house system, Valens-style timing.
- **Acceptance:** cross-reference with existing Western; 20 golden charts.
- **Effort:** 3 weeks

### T-D3.9: Language expansion (20+) — UX strings
- **Definition:** ICU MessageFormat catalog; tier-1/2/3 strategy above.
- **Acceptance:** tier-1 100% human-reviewed; tier-3 MT + spot-check; language-switch UX complete.
- **Effort:** 6 weeks (parallelizable)

### T-D3.10: Classical content localization per tradition per tier-1 language
- **Definition:** Yoga names, dasa descriptions, per-tradition interpretations in tier-1 languages.
- **Acceptance:** advisor review per language.
- **Effort:** 8 weeks (parallelizable)

### T-D3.11: Tradition registry + API
- **Definition:** `/api/v1/traditions` endpoint; tradition preference storage; filter in reading APIs.
- **Acceptance:** unit + integration tests green; tested across all 7 launch traditions.
- **Effort:** 1 week

### T-D3.12: Tradition picker UX
- **Definition:** Settings + onboarding surface for traditions; tribal-sovereignty defaults respected.
- **Acceptance:** UX tested with users from each tradition community.
- **Effort:** 2 weeks

### T-D3.13: Rollout flags + golden-suite CI
- **Definition:** One flag per tradition; CI runs all golden charts per tradition on every PR.
- **Acceptance:** flag-off → tradition invisible in UX and APIs.
- **Effort:** 1 week

## 8. Unit Tests

### 8.1 Tradition-specific rule activation
- Category: golden charts per tradition produce expected activations.
- Target: ≥ 99% golden-chart pass rate per tradition.
- Representative: `test_tibetan_tsi_mewa_9_activation`, `test_ifa_odu_iwori_meji_casting`, `test_mayan_tzolkin_trecena_boundary`.

### 8.2 Extensibility regression
- Category: adding a new source_authority via YAML does NOT require code change.
- Target: CI job that adds a synthetic source, runs migration path, verifies queryable.
- Representative: `test_synthetic_source_yaml_load_end_to_end`, `test_new_output_shape_validates`.

### 8.3 Localization
- Category: ICU strings render correctly per locale, including plurals, gender, script.
- Target: 100% of strings have translations in tier-1; placeholder-match CI check.
- Representative: `test_hindi_plural_forms`, `test_arabic_rtl_rendering`, `test_tamil_script_preserved`.

### 8.4 Translation accuracy of classical content
- Category: spot-check sampled translations against advisor reference.
- Target: tier-1 ≥ 98% match; tier-3 ≥ 85%.
- Representative: `test_yoga_name_bengali_matches_reference`, `test_dasa_name_kannada_transliteration`.

### 8.5 Advisor-sovereignty constraints
- Category: Medicine Wheel tribes never aggregated; per-tribe filters honored.
- Target: 100% isolation.
- Representative: `test_medicine_wheel_tribes_not_aggregated`, `test_tribe_filter_excludes_others`.

### 8.6 Cross-tradition ensemble
- Category: user with multiple traditions active gets fused reading via F8.
- Target: aggregation result cites each tradition with its own source.
- Representative: `test_vedic_plus_tibetan_fusion_citation`, `test_disagreement_surfaced_across_traditions`.

### 8.7 Per-tradition feature flag
- Category: flag off → tradition invisible end-to-end.
- Target: 100% isolation on flag off.
- Representative: `test_flag_off_hides_from_api`, `test_flag_off_hides_from_ui`.

## 9. EPIC-Level Acceptance Criteria

- [ ] 7 launch traditions shipped with named advisor sign-off
- [ ] 20+ languages with tier-appropriate coverage
- [ ] Golden-chart suite per tradition ≥ 99% pass
- [ ] Zero code changes required to add the 8th tradition (demonstrated via synthetic addition)
- [ ] Tradition picker UX validated with community users
- [ ] Tribal sovereignty preserved for Medicine Wheel variants
- [ ] Extensibility CI job proves YAML-only addition works end-to-end
- [ ] Documentation: each tradition dir contains advisor sign-off, source citations, and UX guidance

## 10. Rollout Plan

- **Feature flags:** `tradition_{tibetan_tsi|sufi_ilm|ifa|medicine_wheel|mayan_full|ogham|hellenistic_depth}_enabled`.
- **Language flags:** `locale_{xx}_enabled` tier-by-tier.
- **Sequence:**
  1. Hellenistic depth first (safest; existing Western audience)
  2. Mayan Tzolkin full (builds on existing)
  3. Tibetan Tsi (high demand, low controversy)
  4. Sufi Ilm al-Nujum (requires careful framing)
  5. Celtic Ogham (niche, simple)
  6. Ifa (novel output shape; longest engineering tail)
  7. Medicine Wheel (sovereignty care; longest advisor tail)
- **Per tradition gate:** advisor sign-off complete, golden charts 99%, community preview of 100 users with NPS ≥ 40.
- **Language rollout:** tier-1 at launch; tier-2 within 3 months; tier-3 within 6 months of tier-2.
- **Rollback:** flag off per tradition / per language.

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Cultural appropriation accusations | Medium | High | Named advisors; transparent attribution; opt-out defaults for culturally specific content |
| Tribal-sovereignty violations | Medium | Very High | Tribe-specific subdirs; no cross-tribe aggregation; tribal advisor veto |
| Translation errors in classical content | High | Medium | Tier-1 requires advisor review; tier-3 marked pending |
| Advisor MOU delays block launch | High | Medium | Stagger launches; don't couple tradition flag releases |
| Content drift between language versions | Medium | Medium | Source-of-truth in advisor language; translation is derivation |
| Political sensitivities (e.g., Tibetan, Kurdish) | Medium | Medium | Cultural review; neutral framing; no political content |
| Regulatory bans on divinatory content in some countries | Low | Medium | Geo-fence capability; disclaimer per jurisdiction |

## 12. References

- Master spec: `docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`
- Related PRDs: F1 (source_authority), F6 (rule DSL), F8 (aggregation), P3-E2-console (rule authoring console), P4-E4-tenant (per-tenant overrides), I10 (10k-yoga reference), I5 (cross-tradition reasoning)
- Classical sources: cited per tradition subdir
