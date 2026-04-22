# PRD Review Tracker

Interactive review of all 76 PRDs across phases P0–P6. Every PRD gets checked off here — nothing skipped.

- **Reviewer:** @cpselvam
- **Started:** 2026-04-19
- **Total PRDs:** 89 (76 original + 13 added via gap-closure; see `GAP_CLOSURE.md`)
- **Pass 1 (Astrologer — calculation correctness + decision capture):** ✅ **COMPLETE — 29 / 29 astrology-heavy PRDs locked** (all P1 MVP ✅ · all P2 astrology-heavy ✅ · GAP_CLOSURE: E19, E23, E20, E21, E22, E27, E24, E25, E26, E28, E29, E18, E1c, E6b ✅ · E17 ✅ final)
- **Pass 2 (Engineering — 12-point rubric):** 0 / 89
- **Cross-cutting locks:** 43 decisions in `DECISIONS.md` apply across all PRDs

---

## Review Rubric

For each PRD, we check:

1. **Frontmatter complete** — id, phase, tags, priority, deps, enables, effort, status, author, date
2. **Purpose clear** — problem statement, who benefits, business/engineering impact articulated
3. **Scope precise** — in-scope bullets concrete; out-of-scope items justified; dependencies listed
4. **Research substantive** — classical citations *with verse refs* OR technical alternatives weighed
5. **Open questions resolved** — every non-trivial decision recorded with rationale
6. **Component design executable** — modules named, SQL concrete, API contract typed
7. **User stories testable** — `As … I want … so that …` + acceptance conditions
8. **Tasks decomposed** — each has definition, acceptance, effort estimate
9. **Unit tests enumerated** — name/input/expected/rationale per rule or module
10. **Acceptance criteria binary** — every item pass/fail checkable
11. **Rollout plan credible** — feature flag, shadow, backfill, rollback all addressed
12. **Risks identified** — likelihood/impact/mitigation filled in

**Status legend:** ⬜ not started · 🟡 in review · ✅ approved · ✏️ needs revision · 🚧 blocked

---

## Phase P0 — Foundation (17 PRDs)

| # | ID | Title | Status | Notes |
|:-:|---|---|:-:|---|
| 1 | [F1](./P0/F1-star-schema-dimensions.md) | Star-schema dimension tables | ⬜ | |
| 2 | [F2](./P0/F2-fact-tables.md) | Fact tables with composite FKs | ⬜ | |
| 3 | [F3](./P0/F3-partitioning-from-day-one.md) | LIST + HASH partitioning scheme | ⬜ | |
| 4 | [F4](./P0/F4-temporal-rule-versioning.md) | Temporal rule versioning | ⬜ | |
| 5 | [F5](./P0/F5-json-schema-validation.md) | JSON Schema validation at insert | ⬜ | |
| 6 | [F6](./P0/F6-rule-dsl-yaml-loader.md) | Rule DSL: YAML format + loader | ⬜ | |
| 7 | [F7](./P0/F7-output-shape-system.md) | Output shapes with JSON schemas | ⬜ | |
| 8 | [F8](./P0/F8-technique-result-aggregation-protocol.md) | TechniqueResult + Aggregation Protocol | ⬜ | |
| 9 | [F9](./P0/F9-chart-reading-view-table.md) | chart_reading_view table | ⬜ | |
| 10 | [F10](./P0/F10-typed-ai-tool-use-contract.md) | Typed AI tool-use contract | ⬜ | |
| 11 | [F11](./P0/F11-citation-embedded-responses.md) | Citation-embedded response shape | ⬜ | |
| 12 | [F12](./P0/F12-prompt-caching-claude.md) | Prompt caching via Claude cache_control | ⬜ | |
| 13 | [F13](./P0/F13-content-hash-provenance.md) | Content-hash provenance chain | ⬜ | |
| 14 | [F14](./P0/F14-deterministic-seeding.md) | Deterministic seeding | ⬜ | |
| 15 | [F15](./P0/F15-chart-canonical-fingerprint.md) | Chart canonical fingerprinting | ⬜ | |
| 16 | [F16](./P0/F16-golden-chart-suite.md) | Golden chart suite scaffolding | ⬜ | |
| 17 | [F17](./P0/F17-property-based-test-harness.md) | Property-based test harness | ⬜ | |

## Phase P1 — MVP Engines (7 PRDs)

| # | ID | Title | Status | Notes |
|:-:|---|---|:-:|---|
| 18 | [E1a](./P1/E1a-multi-dasa-v1.md) | Multi-Dasa Engine v1 | 🟡 | Pass 1 ✅ 2026-04-21 — 11 locks (Q3/Q4/Q7/Q8/Q9/Q10/Q11 + 4 cross-cutting); see E1a §2.4 |
| 19 | [E2a](./P1/E2a-ashtakavarga-v2.md) | Ashtakavarga v2 | 🟡 | Pass 1 ✅ 2026-04-21 — 5 E2a locks (Q1/Q2/Q3/Q4/Q5) + 10 cross-cutting; see E2a §2.4; Q2 post-research correction (per-sign Rashi Pinda, not 3-fold) |
| 20 | [E4a](./P1/E4a-yoga-engine-mvp.md) | Classical Yoga Engine MVP (60) | 🟡 | Pass 1 ✅ 2026-04-21 — 8 E4a locks (Q1/Q2/Q3/Q4/Q5/Q6/Q7/Q8) + 6 cross-cutting; 4 research agents used (Neecha Bhanga, Graha Drishti, Tamil node-aspect variance, fixture coverage gap); see E4a §2.4 |
| 21 | [E6a](./P1/E6a-transit-intelligence-v1.md) | Transit Intelligence v1 | 🟡 | Pass 1 ✅ 2026-04-21 — 7 E6a locks (Q1-Q7) + 6 cross-cutting; see E6a §2.4 |
| 22 | [E11a](./P1/E11a-ai-chat-orchestration-v1.md) | AI Chat Orchestration v1 | ⬜ | |
| 23 | [E14a](./P1/E14a-experimentation-framework-v1.md) | Experimentation Framework v1 | ⬜ | |
| 24 | [E15a](./P1/E15a-correctness-harness-v1.md) | Correctness Harness v1 | ⬜ | |

## Phase P2 — Breadth & UIs (14 PRDs)

| # | ID | Title | Status | Notes |
|:-:|---|---|:-:|---|
| 25 | [E1b](./P2/E1b-multi-dasa-v2.md) | Multi-Dasa Engine v2 | 🟡 | Pass 1 ✅ 2026-04-21 — 7 E1b locks (Q1-Q7) + 6 cross-cutting; see E1b §2.4 |
| 26 | [E3](./P2/E3-jaimini-system.md) | Jaimini System | 🟡 | Pass 1 ✅ 2026-04-21 — 6 E3 locks (Q1-Q6) + 6 cross-cutting; Argala generalized per GAP_CLOSURE; see E3 §2.4 |
| 27 | [E4b](./P2/E4b-yoga-engine-full-250.md) | Full Yoga Engine (250) | 🟡 | Pass 1 ✅ 2026-04-21 — 6 E4b locks (Q1-Q6) + E4a inheritance + 6 cross-cutting; Tajaka moved to E5; Kaal Sarpa 12 per GAP_CLOSURE; see E4b §2.4 |
| 28 | [E5](./P2/E5-varshaphala-tajaka.md) | Varshaphala (Tajaka) | 🟡 | Pass 1 ✅ 2026-04-22 — 7 E5 locks (Q1-Q7) + E4a inheritance for Tajaka yogas + 7 cross-cutting; 16 Tajaka yogas now in E5 scope; see E5 §2.4 |
| 29 | [E5b](./P2/E5b-full-ayus-longevity-suite.md) | Full Ayus Longevity Suite | 🟡 | Pass 1 ✅ 2026-04-22 — 7 E5b locks (Q1-Q7) + E2a Sodhya Pinda inheritance + 8 cross-cutting; ethical gating Hard Refusal B2C; see E5b §2.4 |
| 30 | [E7](./P2/E7-vargas-extended-sarvatobhadra-upagrahas.md) | Extended Vargas + Sarvatobhadra + Upagrahas | 🟡 | Pass 1 ✅ 2026-04-22 — 6 E7 locks (Q1-Q6) + GAP_CLOSURE Sphuta extension + 6 cross-cutting; see E7 §2.4 |
| 31 | [E8](./P2/E8-western-depth.md) | Western Depth | 🟡 | Pass 1 ✅ 2026-04-22 — 7 E8 locks (Q1-Q7); Western tradition isolated from Vedic; per-technique zodiac hybrid; see E8 §2.4 |
| 32 | [E8b](./P2/E8b-asteroids-centaurs-planetoids.md) | Asteroids, Centaurs, Planetoids | 🟡 | Pass 1 ✅ 2026-04-22 — 4 E8b locks (Q1-Q4) + E8 Western inheritance; 15-body tiered feature flags; see E8b §2.4 |
| 33 | [E9](./P2/E9-kp-system.md) | KP System | 🟡 | Pass 1 ✅ 2026-04-22 — 6 E9 locks (Q1-Q6); single-source KS Krishnamurti canon (no variants); separate KP chart; see E9 §2.4 |
| 34 | [E10](./P2/E10-prasna-horary.md) | Prasna / Horary | 🟡 | Pass 1 ✅ 2026-04-22 — 6 E10 locks (Q1-Q6); orchestrates E5+E7+E9+E1a+E4a; dual-method always; see E10 §2.4 |
| 35 | [E11b](./P2/E11b-ai-chat-debate-mode.md) | AI Chat v2 (debate mode) | ⬜ | |
| 36 | [E12](./P2/E12-astrologer-workbench-ui.md) | Astrologer Workbench UI | ⬜ | |
| 37 | [E13](./P2/E13-end-user-simplification-ui.md) | End-User Simplification UI | ⬜ | |
| 38 | [E17](./P2/E17-chart-rectification.md) | Chart Rectification | 🟡 | Pass 1 ✅ 2026-04-22 — 5 E17 locks (Q1-Q5 all Option B); Parashari-weighted scoring, ±4h window, Mode 3 astrologer-gated, ≥70% threshold, BPHS canonical + Jaimini/KP toggles; see E17 §2.4 |

## Phase P3 — Scale to 10M (9 PRDs)

| # | ID | Title | Status | Notes |
|:-:|---|---|:-:|---|
| 39 | [S2](./P3/S2-read-replicas-routing.md) | Read replicas + PgBouncer | ⬜ | |
| 40 | [S3](./P3/S3-three-layer-serving-cache.md) | 3-layer serving cache | ⬜ | |
| 41 | [S5](./P3/S5-durable-workflow-orchestration.md) | Durable workflow orchestration | ⬜ | |
| 42 | [S6](./P3/S6-lazy-compute-strategy.md) | Lazy compute strategy | ⬜ | |
| 43 | [P3-E6-flag](./P3/P3-E6-flag-feature-flagged-rule-rollouts.md) | Feature-flagged rule rollouts | ⬜ | |
| 44 | [P3-E8-obs](./P3/P3-E8-obs-per-rule-observability.md) | Per-rule observability | ⬜ | |
| 45 | [C5](./P3/C5-differential-testing-vs-reference.md) | Differential testing vs reference | ⬜ | |
| 46 | [P3-E2-console](./P3/P3-E2-console-rule-authoring-console.md) | Rule authoring console | ⬜ | |
| 47 | [AI5](./P3/AI5-debate-mode-ultra-ai.md) | Debate-mode Ultra AI | ⬜ | |

## Phase P4 — Scale to 100M (6 PRDs)

| # | ID | Title | Status | Notes |
|:-:|---|---|:-:|---|
| 48 | [S4](./P4/S4-olap-replication-clickhouse.md) | OLAP replication (ClickHouse) | ⬜ | |
| 49 | [S7](./P4/S7-sharding-citus-or-splitting.md) | Sharding (Citus or split) | ⬜ | |
| 50 | [S8](./P4/S8-shadow-compute-rule-migrations.md) | Shadow-compute rule migrations | ⬜ | |
| 51 | [P4-E4-tenant](./P4/P4-E4-tenant-per-tenant-rule-overrides.md) | Per-tenant rule overrides | ⬜ | |
| 52 | [Reference-1000](./P4/Reference-1000-expanded-yoga-set.md) | Expanded 1000-yoga reference | ⬜ | |
| 53 | [Research](./P4/Research-cross-source-agreement-dataset.md) | Cross-source agreement dataset | ⬜ | |

## Phase P5 — Category Dominance (12 PRDs)

| # | ID | Title | Status | Notes |
|:-:|---|---|:-:|---|
| 54 | [D1](./P5/D1-voice-native-ai-astrologer.md) | Voice-native AI astrologer | ⬜ | |
| 55 | [D2](./P5/D2-vision-ai-palm-face-tarot.md) | Vision AI (palm/face/tarot) | ⬜ | |
| 56 | [D3](./P5/D3-localization-20-plus-traditions.md) | Localization 20+ languages | ⬜ | |
| 57 | [D4](./P5/D4-marketplace-network-effects.md) | Marketplace network effects | ⬜ | |
| 58 | [D5](./P5/D5-biometric-integration.md) | Biometric integration | ⬜ | |
| 59 | [D6](./P5/D6-longitudinal-dashboard.md) | Longitudinal dashboard | ⬜ | |
| 60 | [D7](./P5/D7-research-data-api.md) | Research data API | ⬜ | |
| 61 | [D8](./P5/D8-astrologer-certification-program.md) | Astrologer certification | ⬜ | |
| 62 | [D9](./P5/D9-enterprise-tier.md) | Enterprise tier | ⬜ | |
| 63 | [D10](./P5/D10-federated-inter-platform.md) | Federated inter-platform | ⬜ | |
| 64 | [D11](./P5/D11-temple-muhurta-api.md) | Temple muhurta API | ⬜ | |
| 65 | [D12](./P5/D12-real-time-cosmic-events.md) | Real-time cosmic events | ⬜ | |

## Phase P6 — Category Creation (11 PRDs)

| # | ID | Title | Status | Notes |
|:-:|---|---|:-:|---|
| 66 | [I1](./P6/I1-josi-academy.md) | Josi Academy | ⬜ | |
| 67 | [I2](./P6/I2-josi-research-press.md) | Josi Research Press | ⬜ | |
| 68 | [I3](./P6/I3-open-source-rule-engine.md) | Open-source rule engine | ⬜ | |
| 69 | [I4](./P6/I4-generative-chart-synthesis.md) | Generative chart synthesis | ⬜ | |
| 70 | [I5](./P6/I5-cross-tradition-unified-reasoning.md) | Cross-tradition unified reasoning | ⬜ | |
| 71 | [I6](./P6/I6-digital-lifetime-companion.md) | Digital lifetime companion | ⬜ | |
| 72 | [I7](./P6/I7-institutions-b2g-b2ngo.md) | Institutions (B2G/B2NGO) | ⬜ | |
| 73 | [I8](./P6/I8-cross-modal-divination.md) | Cross-modal divination | ⬜ | |
| 74 | [I9](./P6/I9-regulatory-certification-body.md) | Regulatory / certification body | ⬜ | |
| 75 | [I10](./P6/I10-ten-thousand-yoga-reference.md) | 10,000-yoga reference set | ⬜ | |
| 76 | [I11](./P6/I11-strategic-optionality.md) | Strategic optionality | ⬜ | |

---

## Review Notes

Per-PRD findings are appended below as we go. Each entry captures: rubric scorecard, strengths, gaps, required changes, and resolution.

<!-- Append new review entries below this line, newest at bottom -->
