---
prd_id: I8
epic_id: I8
title: "Cross-Modal Divination — Tarot, I-Ching, Runes, Numerology, Lo Shu"
phase: P6-institution
tags: [#extensibility, #correctness, #end-user-ux]
priority: should
depends_on: [F1, F4, F6, F7, F8, I3, D3]
enables: [I5, I10]
classical_sources: []
estimated_effort: 4-5 quarters (Year 4)
status: draft
author: "@claude"
last_updated: 2026-04-19
---

# I8 — Cross-Modal Divination (Tarot, I-Ching, Runes, Numerology, Lo Shu)

## 1. Purpose & Rationale

Astrology is one of many classical divination / reflection systems. Each has its own classical corpus, its own rules, its own source authorities, its own traditions. Josi's substrate — dimension tables (F1), rule DSL (F6), aggregation protocol (F8), source authority (master spec §1.2) — is *modality-agnostic*. Rules about tarot card meanings, hexagram interpretations, rune spreads, numerology reductions, and Lo Shu square computations fit the same shape.

I8 expands Josi beyond astrology into a **multi-modal classical divination platform**. Each modality is its own `technique_family` + `source_authority` set. The same engines, the same aggregation strategies, the same AI tool-use contract apply. Cross-tradition synthesis (I5) can now span astrology AND tarot AND I-Ching.

Existing code: `src/josi/services/numerology_service.py` already implements numerology; I8 formalizes it into the rule-registry pattern and builds out the other modalities.

**Strategic value:**
- Massive TAM expansion: tarot market alone dwarfs astrology app market.
- Validates the architecture: if the same infrastructure handles 5+ modalities, it's genuinely a "classical knowledge substrate", not just an astrology system.
- Combinatorial richness: "your Sun in Pisces + The Moon card drawn + Hexagram 29 (Abyss) all point to emotional depth".
- Further reinforces I3 (open-source substrate attracts modality-specific contributors).
- Unlocks consultations across modalities in D4 marketplace.

## 2. Scope

### 2.1 In scope
- **Tarot engine**: 78-card deck (22 Major + 56 Minor); multiple deck variants (Rider-Waite-Smith, Thoth, Marseille); spreads (Celtic Cross, Three-Card, Horseshoe, etc.); card meanings as rule-registry entries per source authority (Waite, Pollack, Pictorial Key, etc.).
- **I-Ching engine**: 64 hexagrams; yarrow-stalk and three-coin methods; moving lines; trigram interpretation; Richard Wilhelm + Legge + Cleary translations as source authorities.
- **Rune engine**: Elder Futhark (24 runes) + optional Younger Futhark; spreads; historical source authorities.
- **Numerology**: formalize existing `numerology_service.py` into registry pattern; Pythagorean + Chaldean systems as source authorities; life path, expression, soul urge numbers; Chinese numerology (Lo Shu).
- **Lo Shu Square**: 3×3 magic square method; birth-date derived; Chinese tradition source authorities.
- UX surface: each modality gets reading UI, history, sharing; single "oracle" dashboard unifies them.
- AI interpretation: same tool-use + RAG pattern; per-modality corpora.
- Integration into I5 (cross-modal synthesis as extension of cross-tradition synthesis).
- D3 localization: modality-native languages preferred (Chinese for I-Ching, Old Norse/English for runes, etc.).

### 2.2 Out of scope
- Scrying / mediumship modalities (not rule-formalizable).
- Palmistry / physiognomy (deferred to D2 — vision AI track, not I8).
- Random word / open-text "oracle" apps.
- Tarot card art licensing (use public-domain art: Rider-Waite-Smith 1909 is public domain; purchase or commission others).
- Deck-creation UGC (Year 5+).

### 2.3 Dependencies
- **F1 (dim tables)** — add new `technique_family` + `source_authority` rows.
- **F4 (rule versioning)** — same mechanism for tarot card meanings.
- **F6 (rule DSL YAML loader)** — same format, different content.
- **F7 (output shapes)** — possibly add new shapes (e.g., "card_spread", "hexagram_with_moving_lines").
- **F8 (aggregation protocol)** — same A/B/C/D strategies.
- **I3 (open-source engine)** — modalities ship in the OSS repo too.
- **D3 (localization)** — strongly needed.
- **Art assets** — card / rune illustrations; licensing.
- **Classical advisors per modality** (tarot, I-Ching, runic traditions).

## 3. Classical / Technical Research

### 3.1 Modality-to-substrate mapping

Each modality maps onto the F1/F6/F7/F8 substrate:

| Modality | technique_family additions | source_authority examples | Output shapes |
|---|---|---|---|
| Tarot | `tarot_card`, `tarot_spread` | `rws_waite`, `thoth_crowley`, `marseille`, `pollack_78_degrees` | `card_spread`, `card_meaning` (boolean+strength) |
| I-Ching | `iching_hexagram`, `iching_trigram`, `iching_moving_line` | `wilhelm_baynes`, `legge`, `cleary_taoist`, `huang` | `hexagram_reading` |
| Rune | `rune_symbol`, `rune_spread` | `thorsson_futhark`, `pennick_runelore` | `rune_spread`, `rune_meaning` |
| Numerology (Pyth) | `numerology_life_path`, `numerology_expression`, `numerology_soul_urge` | `pythagorean_classical`, `modern_numerology_javane` | `numeric`, `categorical` |
| Numerology (Chald) | same families; different source | `chaldean_classical` | same |
| Lo Shu | `loshu_square` | `chinese_classical` | `numeric_matrix` |

### 3.2 Randomness / draw mechanics

Divination modalities involve random draws. We make draws **deterministic given seeds** (per F14) so readings are reproducible and auditable:

```python
# Tarot draw: seeded by user_intent_text + timestamp + user_id
seed = hash(f"{user_intent}|{iso_timestamp}|{user_id}")
rng = random.Random(seed)
cards = rng.sample(deck, k=spread_size)
```

User can re-draw (new seed) or save (persist the drawn reading).

For I-Ching, three-coin method: 6 tosses with 3 coins each; yin/yang per toss; produces hexagram + moving lines. Same seeding.

### 3.3 Tarot spread semantics

Each spread (Celtic Cross, Three-Card, etc.) is a `technique` whose rule takes a set of (position, card) tuples and emits:
- Per-position meaning (rule: card_meaning_at_position[pos])
- Pattern-level observations (e.g., "majority Major Arcana — significant life themes")
- Overall synthesis (LLM over the per-position emissions)

### 3.4 I-Ching moving lines

The unique complexity in I-Ching: moving lines transform one hexagram into another. Rule engine must handle:

```
original_hex → [moving_lines: 3, 5] → transformed_hex
```

Both hexagrams' readings feed the output (present situation + trajectory). Rule YAML must express this; we model a single reading as `{original: ..., transformed: ..., transition_meaning: ...}`.

### 3.5 Numerology — refactor from existing service

Existing `numerology_service.py` already computes. Refactor path:
1. Extract numerology rules into YAML registry.
2. Tag source authority per rule.
3. Delete imperative code; keep only the rule engine path.
4. Re-test with existing test cases.

No user-visible regression should occur.

### 3.6 Alternatives considered

| Alternative | Rejected because |
|---|---|
| Separate microservice per modality | Fragments architecture; defeats "classical substrate" story. |
| Embed modality logic in ad-hoc services like existing numerology_service | Inconsistent with F6/F8 conventions; regresses to imperative code. |
| Skip modalities Josi isn't already doing | Misses the thesis validation + TAM expansion. |
| Fully random draws (no seeding) | Loses reproducibility; makes debugging / audit impossible. |

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| Which modalities in launch | Tarot, I-Ching, Rune, Numerology, Lo Shu | Covers major Western + Chinese traditions; validates breadth. |
| Deterministic seeded draws | Yes | Reproducibility + auditability; users can still re-seed. |
| Deck art | RWS (public domain) at launch; others licensed later | Legal simplicity. |
| Moving lines in I-Ching | Full support at launch | Without moving lines, I-Ching is truncated. |
| Unified "Oracle" dashboard | Yes | Discoverability; cross-modal UX. |
| Cross-modal synthesis | Join I5 extension | Natural fit; adds value. |
| Refactor numerology now vs later | Now, as part of I8 | Avoids permanent technical debt. |
| UGC custom decks | Out of scope Year 4 | Moderation + quality complexity. |

## 5. Component Design

### 5.1 New services / modules

```
src/josi/divination/
├── common/
│   ├── draw.py                 # Seeded RNG primitives
│   └── spread_engine.py
├── tarot/
│   ├── deck.py                 # Card catalog
│   ├── spreads.py
│   └── interpreter.py
├── iching/
│   ├── hexagrams.py
│   ├── toss.py                 # Three-coin / yarrow-stalk
│   └── moving_lines.py
├── rune/
│   ├── staves.py
│   └── spreads.py
├── numerology/
│   └── (refactor existing numerology_service.py into this + rule YAMLs)
└── loshu/
    └── square.py

src/josi/models/divination/
└── ... (modality tables if needed; mostly metadata on existing classical_rule)

src/josi/api/v1/controllers/divination_controller.py

src/josi/db/seeds/classical/
├── tarot/                       # card meaning YAMLs per source
├── iching/                      # hexagram meaning YAMLs per source
├── rune/
├── numerology/
└── loshu/
```

### 5.2 Data model additions

Most modalities fit existing `classical_rule` table with new `technique_family_id` values. Additional:

```sql
CREATE TABLE divination_reading (
  reading_id UUID PK, user_id FK, chart_id FK NULL,
  modality TEXT, spread_or_method TEXT,
  seed TEXT, draw_payload JSONB,
  interpreted_at TIMESTAMPTZ, interpretation TEXT,
  source_authorities JSONB,
  shared_token TEXT NULL
);

-- For recurring modality-specific UX
CREATE TABLE divination_user_pref (
  user_id FK, modality TEXT, preferred_deck_or_source TEXT,
  preferred_language TEXT,
  PRIMARY KEY (user_id, modality)
);
```

### 5.3 API contract

```
POST /api/v1/divination/tarot/draw
  body: {spread, intent, seed?}
  response: {reading_id, cards: [...], interpretation: ...}

POST /api/v1/divination/iching/cast
  body: {method: 'coin'|'yarrow', intent}
  response: {reading_id, hexagram, moving_lines, transformed_hexagram, interpretation}

POST /api/v1/divination/rune/draw
POST /api/v1/divination/numerology/compute
POST /api/v1/divination/loshu/compute

GET  /api/v1/divination/readings/me
GET  /api/v1/divination/readings/{id}
```

## 6. User Stories

### US-I8.1: As a tarot-preferring user, I want a seeded Celtic Cross reading I can save and revisit
**Acceptance:** draw reading; saved with seed; re-open shows same cards; interpretation consistent.

### US-I8.2: As an I-Ching user, I want moving lines handled correctly
**Acceptance:** cast hexagram; moving lines identified; transformed hexagram shown; meanings for both render.

### US-I8.3: As a classical-content contributor, I want to add a new tarot source authority via PR
**Acceptance:** submit YAML rules citing source; dual review; merged; readings option to select new source.

### US-I8.4: As a Chinese-heritage user, I want my Lo Shu Square computed from birthdate with native terminology
**Acceptance:** compute from DOB; display with Chinese character labels (simplified + traditional options); fully localized in Mandarin.

### US-I8.5: As an Ultra AI user, I want a unified reading that synthesizes my chart + drawn tarot card + current I-Ching cast
**Acceptance:** single synthesis (via I5) weaves all three with citations; divergence flagged.

### US-I8.6: As a Josi maintainer, I want existing numerology code to behave identically after refactor
**Acceptance:** pre/post test suite passes with 100% output parity on 1000 test inputs.

### US-I8.7: As a Pro astrologer in the marketplace, I want to offer combined astrology+tarot consultations
**Acceptance:** listing surfaces multi-modal tag; client chart + drawn reading both present in consultation context.

## 7. Tasks

### T-I8.1: Dimension seed expansion
- **Definition:** Add `technique_family` rows (tarot_card, tarot_spread, iching_hexagram, ...); add `source_authority` rows per modality.
- **Acceptance:** Seeds merge; idempotent.
- **Effort:** Q1.

### T-I8.2: Tarot engine + RWS source YAMLs
- **Definition:** Draw mechanics, deck model, Celtic Cross + Three-Card + Horseshoe spreads; RWS meanings as YAML.
- **Acceptance:** End-to-end API returns valid reading; determinism tests pass.
- **Effort:** Q1–Q2.

### T-I8.3: I-Ching engine (three-coin, moving lines, Wilhelm-Baynes source)
- **Definition:** Coin toss / yarrow option; hexagram computation; moving lines + transformation; Wilhelm-Baynes meaning YAMLs.
- **Acceptance:** Hexagram generation reproduces published test cases.
- **Effort:** Q2.

### T-I8.4: Rune engine (Elder Futhark + Thorsson source)
- **Definition:** 24 runes; spread mechanics; Thorsson source YAML.
- **Acceptance:** End-to-end API.
- **Effort:** Q2.

### T-I8.5: Numerology refactor
- **Definition:** Extract existing `numerology_service.py` logic into rule YAMLs; delete imperative service; thin service wraps rule engine.
- **Acceptance:** 100% output parity on 1000-case regression test.
- **Effort:** Q2.

### T-I8.6: Lo Shu Square
- **Definition:** Implement compute; source YAML for Chinese-classical interpretations.
- **Acceptance:** Correct outputs on published reference cases.
- **Effort:** Q3.

### T-I8.7: Unified "Oracle" dashboard UI
- **Definition:** Next.js dashboard unifying all modalities; recent readings; quick-draw UI.
- **Acceptance:** Playwright passes for all 5 modalities.
- **Effort:** Q3.

### T-I8.8: I5 cross-modal synthesis extension
- **Definition:** Extend theme-mapping to include tarot / I-Ching / etc. indicators; synthesis agent handles modalities.
- **Acceptance:** 20-case gold-set synthesis evaluated; panel rating ≥ 4/5.
- **Effort:** Q3–Q4.

### T-I8.9: Localization
- **Definition:** D3-scope modality-native languages for each reading.
- **Acceptance:** Mandarin I-Ching; German/English rune; etc.
- **Effort:** Q4.

### T-I8.10: I3 OSS sync
- **Definition:** Modality code + rule YAMLs merged to OSS repo.
- **Acceptance:** Published in major release of josi-classical-engine.
- **Effort:** Q4.

## 8. Unit Tests

### 8.1 Draw determinism tests
| Test category | Representative names | Success target |
|---|---|---|
| Seed → identical draw | `test_same_seed_same_tarot_draw` | 100% across 10k trials |
| Seed → identical hexagram | `test_same_seed_same_iching_cast` | 100% |
| Moving-line correctness | `test_moving_lines_transform_to_correct_hexagram` | 100% on 64 test cases |

### 8.2 Rule-registry coverage tests
| Test category | Representative names | Success target |
|---|---|---|
| Tarot coverage | `test_all_78_cards_have_meaning_rules_per_source` | 100% per source authority |
| I-Ching coverage | `test_all_64_hexagrams_and_384_lines_covered` | 100% |
| Rune coverage | `test_all_24_elder_futhark_covered` | 100% |
| Numerology parity | `test_numerology_output_matches_preexisting_service` | 100% on 1000 inputs |

### 8.3 Aggregation tests
| Test category | Representative names | Success target |
|---|---|---|
| Multi-source tarot (Waite vs Pollack) | `test_tarot_aggregation_strategy_D_produces_expected_output` | Known expected output |
| Cross-source confidence | `test_iching_cross_source_confidence` | Confidence scores in [0,1] range |

### 8.4 I5 synthesis tests
| Test category | Representative names | Success target |
|---|---|---|
| Cross-modal synthesis | `test_synthesis_across_chart_tarot_iching` | Panel ≥ 4/5 on 20 gold cases |
| Citation integrity | `test_every_modality_claim_cited` | 100% |

### 8.5 Localization tests
| Test category | Representative names | Success target |
|---|---|---|
| Mandarin I-Ching | `test_iching_mandarin_hexagram_names` | 100% match published set |
| English/German runes | `test_rune_language_parity` | No missing strings per locale |

### 8.6 Historical-reading persistence tests
| Test category | Representative names | Success target |
|---|---|---|
| Reproducibility | `test_saved_reading_reproduces_on_reopen` | 100% |
| User privacy | `test_private_reading_not_visible_without_share_token` | 100% |

## 9. EPIC-Level Acceptance Criteria

- [ ] All 5 modalities live (Tarot, I-Ching, Rune, Numerology, Lo Shu).
- [ ] Existing numerology behavior preserved after refactor (regression suite 100%).
- [ ] Moving-line support in I-Ching operational.
- [ ] Seeded-draw determinism verified.
- [ ] Unified Oracle dashboard shipped.
- [ ] I5 synthesis extended to modalities with ≥ 4/5 panel rating.
- [ ] Localization for at least 2 languages per modality live.
- [ ] All modality code + rule YAMLs merged into I3 OSS.
- [ ] Golden test suite green for each modality.
- [ ] Coverage: Tarot (78 cards × ≥ 2 sources), I-Ching (64 hexagrams × ≥ 2 sources), Rune (24), Numerology (Pythagorean + Chaldean), Lo Shu.

## 10. Rollout Plan

**Gate 0 — Internal alpha (Year 4 Q2):**
- Feature flag: `divination_modalities`; Josi employees + 20 tarot/I-Ching advisors.
- **Gate to proceed:** golden suite green; determinism tests pass.

**Gate 1 — Ultra subscriber beta (Year 4 Q3):**
- All Ultra subscribers get Tarot + I-Ching; others staged.
- **Gate to proceed:** NPS ≥ 50; no draw-reproducibility bugs.

**Gate 2 — Public launch (Year 4 Q4):**
- All 5 modalities available to all users.
- **Gate to cross-modal synthesis (I5 extension):** core modality stability over 30 days.

**Gate 3 — Advanced features (Year 5):**
- Additional deck variants, rune Younger Futhark, UGC decks evaluated.

**Rollback plan:** feature flag per modality; can disable individually. Existing saved readings remain accessible.

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Numerology refactor regressions | Medium | High | Aggressive regression suite; shadow compute vs old service during transition. |
| Tarot card art licensing disputes | Medium | Medium | RWS public domain at launch; license others with clear chains of title. |
| Moving-line edge cases wrong in I-Ching | Medium | Medium | 64-case regression suite; expert review pre-launch. |
| "Divination" perceived as lower-tier than astrology in Josi's brand | Low | Low | Framing: classical knowledge traditions of comparable depth. |
| Modality flood dilutes AI synthesis quality | Medium | Medium | User-controllable: which modalities factor into Ultra synthesis. |
| Random-seed leakage exposes intent text | Low | Medium | Hash with salt; don't expose raw seed. |
| Cultural-appropriation critique (Norse runes, Chinese I-Ching) | Medium | Medium | Classical-advisor consultation per tradition; respectful framing. |
| UGC deck moderation burden (if pursued later) | Medium | Medium | Out of scope Year 4; defer with explicit gate. |
| Legal: some jurisdictions restrict "fortune telling" | Medium | High | Jurisdictional legal check; framing as reflection/classical-study. |
| Users substitute divination for astrology unexpectedly, affecting monetization | Low | Low | Both premium in Ultra tier; cross-sell. |
| Hexagram-meaning source variation is larger than anticipated; aggregation uncertainty | Medium | Medium | Surface confidence; educate user on source differences (matches existing source-authority pattern). |

## 12. References

- Master spec: `docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md` — §1.2 (source authority, applies to all modalities).
- Related PRDs: F1, F4, F6, F7, F8, F14, I3, I5, D3
- Waite, A. E. (1910). *The Pictorial Key to the Tarot.*
- Pollack, R. (1980). *Seventy-Eight Degrees of Wisdom.*
- Wilhelm, R., & Baynes, C. (1950). *The I Ching or Book of Changes.*
- Thorsson, E. (1984). *Futhark: A Handbook of Rune Magic.*
- Cheiro (1926). *Book of Numbers.*
- Existing code: `src/josi/services/numerology_service.py`.
