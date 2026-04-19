---
prd_id: I5
epic_id: I5
title: "Cross-Tradition Unified Reasoning AI"
phase: P6-institution
tags: [#ai-chat, #correctness, #extensibility, #end-user-ux]
priority: must
depends_on: [E11b, I3, D3, I8, I10]
enables: [I6, I7]
classical_sources: [bphs, jaimini_sutras, tajaka_neelakanthi, kp_reader, saravali]
estimated_effort: 4 quarters (Year 3 Q4 through Year 4 Q3)
status: draft
author: "@claude"
last_updated: 2026-04-19
---

# I5 — Cross-Tradition Unified Reasoning AI

## 1. Purpose & Rationale

By Year 3, Josi hosts the engines for six astrology traditions (Vedic/Parashari, Jaimini, Western, Hellenistic, Chinese/BaZi, KP) and several divination systems (I8). Each gives a different reading of the same person. No existing product (nor human astrologer, typically) synthesizes *across* traditions with the rigor of citing and weighting each.

I5 builds an LLM explicitly trained/retrieval-grounded for **cross-tradition synthesis**: a reasoning agent that can answer, for example:

> "Your BaZi Four Pillars show weak Wood element; your Vedic Lagna lord Mars is debilitated in the D1; your Hellenistic 6th-place Lot of Disease receives Saturn. All three traditions converge on a health theme around your liver / joints in this cycle."

This is the first AI that treats multi-tradition synthesis as a first-class capability rather than a tacked-on option. It is the cognitive layer above the calculation engines — Josi's central AI differentiator.

**Strategic value:**
- Unique capability: no competitor has all engines, classical corpora, *and* the synthesis infrastructure.
- Platform thesis validation: proves the multi-tradition bet. If this works, Josi's breadth becomes its core value.
- Drives premium tier (Ultra AI) adoption.
- Preconditions I6 (longitudinal companion) and I7 (institutions) which both require a unified reasoning voice.

## 2. Scope

### 2.1 In scope
- A fine-tuned or heavily retrieval-augmented LLM specialized in multi-tradition synthesis:
  - Fine-tuned Claude/Sonnet variant (or equivalent Anthropic-supported adapter) on a curated classical-synthesis corpus, OR
  - Advanced RAG over cross-tradition corpus with synthesis prompt templates and agent-loop chaining.
- A cross-tradition tool-use contract exposing every engine's results in a unified shape (extension of F10).
- A "convergence" primitive: given a theme (health, career, relationships, etc.), query each tradition's readings, compute convergence/divergence, render with citations.
- Training + evaluation corpus: curated synthesis examples by expert cross-tradition astrologers (rare; an asset class).
- Calibration: confidence scores per claim; explicit disagreement flags when traditions diverge.
- Localization hooks for each tradition's idiom (D3).
- Accessible in Ultra AI mode + Astrologer Workbench + end-user chat (with feature flagging).

### 2.2 Out of scope
- Replacing per-tradition readings (single-tradition readings remain canonical for users who prefer).
- Mixing tradition-specific claim into unified claim without citation (every synthesis sentence must be attributable).
- Theological / philosophical synthesis (e.g., resolving fundamental worldview differences between Vedic and Hellenistic cosmology) — respect the traditions' integrity.
- Prediction-quality absolute claims ("you will have a heart attack") — framed as tendencies/themes.

### 2.3 Dependencies
- **E11b (AI chat debate mode)** — substrate; I5 extends.
- **I3 (open-source engine)** — the calculation layer; I5 orchestrates across all engines.
- **D3 (localization)** — multilingual delivery.
- **I8 (cross-modal divination)** — optional extra modalities (tarot, I-Ching) can join the synthesis.
- **I10 (10,000-yoga reference)** — corpus for Vedic side.
- **Expert-annotated synthesis corpus** — must be curated; significant editorial cost.
- **Fine-tuning infrastructure** — if Anthropic offers Claude fine-tuning by Year 4; else heavy RAG.

## 3. Classical / Technical Research

### 3.1 Why cross-tradition synthesis is non-trivial

Each tradition uses different ontologies:
- **Vedic** — signs × houses × nakshatras × vargas × dasas × yogas.
- **Western** — signs × houses × aspects × transits.
- **BaZi** — four pillars (year/month/day/hour) × five elements × ten gods × luck pillars.
- **Hellenistic** — sects × lots × profections × ZR (zodiacal releasing).
- **KP** — sub-lords × significators.

A "health theme" in one is `6th house + Saturn aspecting lagna lord`; in another, it's `weak Wood relative to strong Metal`; in another, `Lot of Disease with malefic overlord`. These do not map 1:1. Cross-tradition synthesis requires **theme-level abstraction** where traditions are mapped to shared themes with explicit translation logic.

### 3.2 Theme-mapping layer

Introduce a "theme" dimension table keyed by life-domain (health, career, relationships, wealth, spiritual, family, travel, education, legal, mental, creative), with tradition-specific mappings:

```yaml
theme: health
vedic_indicators:
  - {family: lagna_lord, condition: weakness}
  - {family: house, num: 6, condition: malefic_influence}
  - {family: yoga, id: arishta_*}
western_indicators:
  - {aspect: saturn_hard_to_sun}
  - {lot: disease}
chinese_indicators:
  - {element: any, condition: severely_unbalanced}
  - {ten_gods: hurting_officer_dominant}
hellenistic_indicators:
  - {lot: disease}
  - {profection: 6th_house_year}
```

This mapping is classical-advisor-reviewed, versioned, and part of I3. Synthesis agents compute per-tradition indicator activation, then convergence/divergence.

### 3.3 Architecture: agent orchestration

```
User question:
  "What do the traditions say about my career for the next year?"
      ↓
Planner agent (Claude):
  - Identifies theme: career
  - Identifies temporal scope: next 12 months
  - Lists tools to call per tradition
      ↓
Parallel tool calls:
  - get_vedic_career_indicators(chart_id)
  - get_western_career_indicators(chart_id, year)
  - get_bazi_career_indicators(chart_id, year)
  - get_hellenistic_career_indicators(chart_id, year)
      ↓
Synthesis agent (Claude):
  - Receives structured per-tradition readings with citations
  - Computes convergence (shared themes) + divergence (contradictions)
  - Generates narrative with per-claim citations
  - Marks confidence per claim (from aggregation_strategy)
      ↓
Response:
  - Executive summary
  - Per-theme paragraphs
  - Divergence notes
  - Citations footer
```

### 3.4 Training / evaluation corpus

- Collect ~500 expert cross-tradition case studies (licensed from cross-tradition astrologers or produced in-house with I1 Master-level graduates).
- Gold evaluation set: 50 chart+question pairs with ideal answers validated by a panel.
- Calibration set: measure agreement between model output and panel; target ≥ 0.8 ordinal agreement.

### 3.5 Alternatives considered

| Alternative | Rejected because |
|---|---|
| Single-tradition-at-a-time, let user switch | Fails the synthesis thesis; no differentiator. |
| Train fully from scratch on classical corpus | Prohibitively expensive; data-sparse domain. |
| Pure prompt engineering, no fine-tune | Works partly; loses consistency; falls back to RAG+prompting if fine-tuning is unavailable. |
| Dedicated model per tradition, meta-LLM composes | Too many model endpoints; maintenance burden. |

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| Fine-tune vs RAG | RAG-primary; fine-tune adapter if Anthropic exposes it by Year 4 | Keep optionality; RAG gives us most of the win. |
| Per-tradition weighting in synthesis | Astrologer-configurable; Josi defaults exist | Respects pluralism; aligns with master spec §1.2. |
| Theme taxonomy | 11 canonical themes at launch; extensible | Start practical; grow. |
| Divergence rendering | Explicit flag: "Traditions disagree here: [details]" | Epistemic honesty core to product identity. |
| Output length | Scoped by question; default ~300–500 words | Readable, not overwhelming. |
| Caching | Per-chart synthesis cached for 24 hours | Compute-cost control. |
| User consent for cross-tradition synthesis on their chart | Always on (it's just synthesis of existing readings); transparency via settings | No new data collected. |

## 5. Component Design

### 5.1 New services / modules

```
src/josi/ai/unified_reasoning/
├── orchestrator.py          # Planner + synthesis agent orchestration
├── theme_mapping.py         # Theme → per-tradition indicators
├── convergence.py           # Compute convergence/divergence across readings
├── citation_router.py       # Ensure every claim in output is attributable
├── calibration.py           # Confidence scoring per claim
└── eval/
    ├── gold_set.py
    └── panel_agreement.py

src/josi/models/unified_reasoning/
└── theme_dimension.py       # Seed table + YAML

src/josi/api/v1/controllers/unified_chat_controller.py
```

### 5.2 Data model additions

```sql
CREATE TABLE theme (
  theme_id TEXT PK,
  display_name TEXT,
  category TEXT   -- life_domain | temporal | relational
);

CREATE TABLE theme_indicator (
  theme_id FK,
  tradition TEXT,
  indicator JSONB,        -- tradition-specific rule mapping
  version TEXT,
  PRIMARY KEY (theme_id, tradition, version)
);

CREATE TABLE unified_synthesis_event (
  event_id UUID PK, chart_id FK, user_id FK,
  question TEXT, themes_detected JSONB,
  per_tradition_inputs JSONB,
  synthesis_output TEXT,
  citations JSONB,
  divergence_flags JSONB,
  confidence_scores JSONB,
  model_version TEXT, rendered_at TIMESTAMPTZ,
  prompt_cache_hit BOOLEAN
);
```

### 5.3 API contract

```
POST /api/v1/unified/ask
  body: { chart_id, question, language, mode: 'auto'|'pro', traditions: [...] }
  response: streamed SSE with: summary, per-theme sections, citations, divergence flags

GET  /api/v1/unified/themes
POST /api/v1/unified/feedback       # thumbs + free text; feeds calibration
```

## 6. User Stories

### US-I5.1: As an end-user, I want a synthesis across traditions when asking about my health
**Acceptance:** response cites specific Vedic + Western + BaZi indicators; convergence statement present; divergence flagged if present; time to first token ≤ 3s; full response ≤ 15s.

### US-I5.2: As a Pro astrologer running Ultra AI, I want to configure which traditions synthesize
**Acceptance:** dropdown to toggle each tradition on/off; weight sliders per tradition; synthesis respects configuration.

### US-I5.3: As a research user, I want convergence metrics exported for my dataset
**Acceptance:** D7 exposes anonymized convergence distributions per theme; k ≥ 100.

### US-I5.4: As a Tamil-speaking end-user, I want synthesis in Tamil with tradition-native idioms
**Acceptance:** D3-localized response; BaZi terms transliterated appropriately; Vedic terms in Tamil; Western terms translated.

### US-I5.5: As a skeptic user, I want clear labeling when traditions disagree
**Acceptance:** "Traditions disagree here" banner; expandable detail; no false consensus.

### US-I5.6: As a researcher for I2, I want to measure whether tradition convergence correlates with observed outcomes
**Acceptance:** research dataset (opt-in) captures convergence score + user-reported outcomes; I2 paper publishable.

## 7. Tasks

### T-I5.1: Theme taxonomy + mapping YAML
- **Definition:** 11 themes × 5 traditions = 55 indicator mappings; classical-advisor reviewed.
- **Acceptance:** YAML merged into I3; every indicator references a real rule.
- **Effort:** Q1.

### T-I5.2: Orchestrator (planner + synthesis agents)
- **Definition:** Agent-loop with tool calls per tradition; citation routing; divergence computation.
- **Acceptance:** End-to-end flow on 10 test questions; no missing-citation claims.
- **Effort:** Q1–Q2.

### T-I5.3: Expert corpus collection
- **Definition:** 500 cross-tradition case studies licensed or authored; gold set of 50 for evaluation.
- **Acceptance:** Corpus delivered, stored, version-tagged.
- **Effort:** Q1–Q2 (parallel, external dependency).

### T-I5.4: Fine-tuning OR advanced RAG
- **Definition:** If Anthropic fine-tuning available: fine-tune adapter; else: build RAG with prompt caching + retrieval pipeline.
- **Acceptance:** Model achieves ≥ 0.8 ordinal agreement with panel on gold set.
- **Effort:** Q2–Q3.

### T-I5.5: Calibration + confidence layer
- **Definition:** Confidence score per claim; uses aggregation_strategy signals under the hood.
- **Acceptance:** Calibration plot shows confidence correlates with panel agreement.
- **Effort:** Q3.

### T-I5.6: Front-end integration
- **Definition:** Ultra chat UI in Next.js; divergence banners; citations expandable; localization.
- **Acceptance:** Playwright tests for EN/TA/HI happy paths + divergence case.
- **Effort:** Q3.

### T-I5.7: Public-launch gating
- **Definition:** Feature flags; gradual rollout; performance monitoring.
- **Acceptance:** Rollout executes per plan; p99 latency holds.
- **Effort:** Q4.

### T-I5.8: First I2 paper on synthesis quality
- **Definition:** Paper describing panel-agreement methodology + convergence ↔ outcome analysis.
- **Acceptance:** Submitted to I2; panel reviews.
- **Effort:** Q4.

## 8. Unit Tests

### 8.1 Theme-mapping tests
| Test category | Representative names | Success target |
|---|---|---|
| Mapping coverage | `test_every_theme_has_indicator_per_tradition` | 100% of themes × traditions covered |
| Indicator validity | `test_indicator_references_real_rule` | 100% FK resolution to classical_rule |

### 8.2 Orchestrator tests
| Test category | Representative names | Success target |
|---|---|---|
| Planner produces correct tool-call set | `test_planner_identifies_career_theme` | ≥ 95% correct theme-identification on gold set |
| Parallel tool execution | `test_tool_calls_run_concurrently` | Wallclock ≤ 1.3× slowest individual tool |
| Missing-tradition handling | `test_graceful_when_tradition_missing` | No crashes; degraded response labeled |

### 8.3 Citation-integrity tests
| Test category | Representative names | Success target |
|---|---|---|
| No uncited claim | `test_every_claim_has_citation` | 100% of output sentences map to a citation |
| No fabricated citation | `test_no_citation_references_missing_rule` | 100% citation FK resolution |

### 8.4 Panel-agreement tests (gold set)
| Test category | Representative names | Success target |
|---|---|---|
| Overall ordinal agreement | `test_model_vs_panel_ordinal_agreement` | ≥ 0.8 Spearman on gold set |
| Divergence detection | `test_model_flags_known_divergence_cases` | ≥ 90% recall on gold divergence cases |
| Tradition balance | `test_no_tradition_systematically_overweighted` | Each tradition cited ≥ 15% across outputs |

### 8.5 Latency / cost tests
| Test category | Representative names | Success target |
|---|---|---|
| Time to first token | `test_ttft_p50_under_3s` | p50 ≤ 3s; p99 ≤ 8s |
| Full response | `test_full_response_p99_under_15s` | p99 ≤ 15s |
| Prompt-cache hit rate | `test_cache_hit_rate_gte_60pct` | ≥ 60% on repeat queries within session |

### 8.6 Localization tests
| Test category | Representative names | Success target |
|---|---|---|
| Language fidelity | `test_ta_hi_response_quality` | Panel rates localized output ≥ 4/5 on fidelity |
| Tradition-native idiom | `test_bazi_terms_preserved` | 100% of canonical terms retained per style guide |

### 8.7 Safety / calibration tests
| Test category | Representative names | Success target |
|---|---|---|
| Medical-claim refusal | `test_refuses_definitive_medical_prediction` | ≥ 99% refusal on adversarial prompts |
| Confidence calibration | `test_confidence_correlates_with_panel_agreement` | Correlation ≥ 0.6 |

## 9. EPIC-Level Acceptance Criteria

- [ ] Theme taxonomy (11 themes × 5 traditions) merged and advisor-signed-off.
- [ ] Model achieves ≥ 0.8 ordinal agreement with expert panel on gold set.
- [ ] End-to-end synthesis flow delivers time-to-first-token ≤ 3s (p50).
- [ ] 100% of output claims are citation-attributable.
- [ ] Divergence detection recall ≥ 90% on gold divergence set.
- [ ] Ultra AI mode launched to all Ultra subscribers.
- [ ] Localization live in EN, TA, HI.
- [ ] First I2 synthesis-methodology paper submitted.
- [ ] User thumbs-up rate on synthesis responses ≥ 75% (aligns with master spec §8.4).

## 10. Rollout Plan

**Gate 0 — Dogfood (Year 3 Q4):**
- Feature flag: `unified_reasoning_internal` (Josi employees + 10 astrologer advisors only).
- **Gate to proceed:** panel agreement ≥ 0.8 on gold set; citation integrity 100%.

**Gate 1 — Ultra AI alpha (Year 4 Q1):**
- 500 Ultra subscribers opt-in.
- **Gate to proceed:** thumbs-up ≥ 70%; latency within SLO; no citation-fabrication incidents.

**Gate 2 — Astrologer Workbench (Year 4 Q2):**
- All Pro astrologers get access in Ultra mode.
- **Gate to proceed:** astrologer implicit-override rate ≤ 20% (master spec §8.4 target).

**Gate 3 — General Ultra AI public (Year 4 Q3):**
- All Ultra tier subscribers.
- **Gate to I6 unlock:** steady-state quality metrics hold for 90 days.

**Rollback plan:** feature flag disables unified reasoning; per-tradition chats remain available. Cached syntheses remain readable but new ones disabled.

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Cross-tradition hallucination fabricates convergence | Medium | High | Theme-mapping rigor; citation checks; divergence flags mandatory. |
| Model flattens genuine tradition differences into bland consensus | Medium | Medium | Explicit divergence rendering; panel evals focus on divergence detection. |
| Expert-corpus licensing fails | Medium | High | Produce corpus in-house via I1 Master graduates; budget reserved. |
| Fine-tuning unavailable from Anthropic | Medium | Medium | RAG-first architecture works without; fine-tune is upside. |
| Latency blows out due to 5 parallel tool calls | Medium | Medium | Concurrency + prompt caching; staged degradation if one tradition slow. |
| User confusion over which tradition "is right" | High | Medium | UI makes pluralism the model; transparency; no "winner" framing. |
| Per-tradition advocates accuse Josi of dilution | Medium | Medium | Single-tradition mode remains canonical; Ultra is additive. |
| Sensitive health/relationship claims cause harm | Low-Medium | High | Medical-claim refusal guardrails; disclaimers; opt-in consent for sensitive themes. |
| Regulatory scrutiny for AI-generated health commentary | Medium | High | Framing as "classical themes"; no diagnostic claims; legal review per jurisdiction. |
| Cost per synthesis query exceeds pricing model | Medium | Medium | Prompt caching (≥ 60% hit); per-query budget limits; Ultra tier priced to cover. |
| Localization quality uneven across languages | High | Medium | Native-speaker review; tradition-native style guides; D3 quality gates. |
| Dependency on I10 corpus completion slips | Medium | Medium | Launch with partial I10 (Reference-1000 baseline); expand iteratively. |

## 12. References

- Master spec: `docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md` — §3 (AI chat integration), §1.2 (source authority).
- Related PRDs: E11b, I3, D3, I8, I10, I2, I6, I7, D7
- Cross-tradition case-study literature (rare; see B.V. Raman's cross-writing, Hellenistic + Vedic comparative works).
- RAG + agent-loop patterns: ReAct, function-calling best practices.
- Calibration: Guo et al. (2017) *On Calibration of Modern Neural Networks*.
