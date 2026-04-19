# PRD Master Index

Canonical registry of all 76 PRDs across Phases P0–P6. Filter by phase, priority, or tag by grepping frontmatter.

**Master design:** [`docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`](../../superpowers/specs/2026-04-19-classical-techniques-expansion-design.md)
**PRD template:** [`_TEMPLATE.md`](./_TEMPLATE.md)

---

## Phase 0 — Foundation (Week 1–2, 17 PRDs)

Architectural primitives. Nothing user-visible. Must all land before P1 starts.

| ID | Title | Tags | Priority | Depends |
|---|---|---|:---:|---|
| [F1](./P0/F1-star-schema-dimensions.md) | Star-schema dimension tables | `#correctness` `#extensibility` | **must** | — |
| [F2](./P0/F2-fact-tables.md) | Fact tables with composite FKs | `#correctness` | **must** | F1 |
| [F3](./P0/F3-partitioning-from-day-one.md) | LIST + HASH partitioning scheme | `#performance` | **must** | F2 |
| [F4](./P0/F4-temporal-rule-versioning.md) | Temporal rule versioning (effective_from/to, content_hash) | `#correctness` `#extensibility` | **must** | F1 |
| [F5](./P0/F5-json-schema-validation.md) | JSON Schema validation at insert time | `#correctness` | **must** | F2 |
| [F6](./P0/F6-rule-dsl-yaml-loader.md) | Rule DSL: YAML format, loader, content-hash | `#extensibility` | **must** | F4 |
| [F7](./P0/F7-output-shape-system.md) | Output shapes with JSON schemas | `#extensibility` | **must** | F5 |
| [F8](./P0/F8-technique-result-aggregation-protocol.md) | TechniqueResult + AggregationStrategy Protocol | `#extensibility` `#experimentation` | **must** | F7 |
| [F9](./P0/F9-chart-reading-view-table.md) | chart_reading_view incrementally-updated table | `#performance` `#ai-chat` | **must** | F2, F8 |
| [F10](./P0/F10-typed-ai-tool-use-contract.md) | Typed AI tool-use contract (Pydantic + Claude) | `#ai-chat` | **must** | F8 |
| [F11](./P0/F11-citation-embedded-responses.md) | Citation-embedded response shape | `#ai-chat` `#correctness` | **must** | F10 |
| [F12](./P0/F12-prompt-caching-claude.md) | Prompt caching via Claude cache_control | `#ai-chat` `#performance` | **must** | F10 |
| [F13](./P0/F13-content-hash-provenance.md) | Content-hash provenance chain | `#correctness` | **must** | F2, F6 |
| [F14](./P0/F14-deterministic-seeding.md) | Deterministic seeding for stochastic ops | `#correctness` | **should** | — |
| [F15](./P0/F15-chart-canonical-fingerprint.md) | Chart canonical fingerprinting | `#performance` | **should** | F13 |
| [F16](./P0/F16-golden-chart-suite.md) | Golden chart suite scaffolding | `#correctness` | **must** | F8 |
| [F17](./P0/F17-property-based-test-harness.md) | Property-based test harness (Hypothesis) | `#correctness` | **must** | F8 |

---

## Phase 1 — MVP Engines (Month 1–3, 7 PRDs)

Shippable engine increments. Each ships independently via API. Target: 10k users.

| ID | Title | Tags | Priority | Depends |
|---|---|---|:---:|---|
| [E1a](./P1/E1a-multi-dasa-v1.md) | Multi-Dasa Engine v1 (Yogini + Ashtottari) | `#correctness` | **must** | F1–F17 |
| [E2a](./P1/E2a-ashtakavarga-v2.md) | Ashtakavarga v2 (Trikona + Ekadhipatya shodhana) | `#correctness` | **must** | F1–F17 |
| [E4a](./P1/E4a-yoga-engine-mvp.md) | Classical Yoga Engine MVP (60 core yogas) | `#correctness` `#extensibility` | **must** | F1–F17 |
| [E6a](./P1/E6a-transit-intelligence-v1.md) | Transit Intelligence v1 (Sade Sati, Dhaiya, major transits) | `#correctness` | **must** | F1–F17 |
| [E11a](./P1/E11a-ai-chat-orchestration-v1.md) | AI Chat Orchestration v1 (tool-use + citations) | `#ai-chat` `#end-user-ux` | **must** | F10, F11, F12 |
| [E14a](./P1/E14a-experimentation-framework-v1.md) | Experimentation Framework v1 | `#experimentation` | **must** | F8 |
| [E15a](./P1/E15a-correctness-harness-v1.md) | Correctness Harness v1 (golden suite + property tests in CI) | `#correctness` | **must** | F16, F17 |

---

## Phase 2 — Breadth & UIs (Month 3–6, 14 PRDs)

Full classical coverage + dedicated UIs. Target: 10k → 100k users.

| ID | Title | Tags | Priority | Depends |
|---|---|---|:---:|---|
| [E1b](./P2/E1b-multi-dasa-v2.md) | Multi-Dasa Engine v2 (Chara + Narayana + Kalachakra) | `#correctness` | **must** | E1a |
| [E3](./P2/E3-jaimini-system.md) | Jaimini System (Chara Karakas, Arudhas, Jaimini yogas) | `#correctness` | **must** | F1–F17 |
| [E4b](./P2/E4b-yoga-engine-full-250.md) | Full Yoga Engine (complete 250 set) | `#correctness` | **must** | E4a |
| [E5](./P2/E5-varshaphala-tajaka.md) | Varshaphala (Tajaka): Muntha, Year Lord, Sahams | `#correctness` | **must** | F1–F17 |
| [E5b](./P2/E5b-full-ayus-longevity-suite.md) | Full Ayus (Longevity) Suite — Pindayu, Amshayu, Nisargayu, Jaimini Ayu | `#correctness` | **should** | E1a, E2a, E4a |
| [E7](./P2/E7-vargas-extended-sarvatobhadra-upagrahas.md) | Extended Vargas D61–D144, Sarvatobhadra, Upagrahas | `#correctness` | **should** | F1–F17 |
| [E8](./P2/E8-western-depth.md) | Western Depth (Arabic Parts, fixed stars, harmonics, eclipses, Uranian) | `#correctness` | **should** | F1–F17 |
| [E8b](./P2/E8b-asteroids-centaurs-planetoids.md) | Asteroids, Centaurs & Planetoids (Ceres, Pallas, Juno, Vesta, Chiron, Eris, …) | `#correctness` | **should** | E8 |
| [E9](./P2/E9-kp-system.md) | KP System (sub-lord, significators, KP horary) | `#correctness` | **should** | F1–F17 |
| [E10](./P2/E10-prasna-horary.md) | Prasna / Horary (Vedic + KP unified) | `#correctness` | **could** | E9 |
| [E11b](./P2/E11b-ai-chat-debate-mode.md) | AI Chat v2 (debate mode, Ultra AI ensemble, semantic similarity) | `#ai-chat` | **must** | E11a, E14a |
| [E12](./P2/E12-astrologer-workbench-ui.md) | Astrologer Workbench UI | `#astrologer-ux` `#i18n` | **must** | all engines |
| [E13](./P2/E13-end-user-simplification-ui.md) | End-User Simplification UI | `#end-user-ux` | **must** | E11a |
| [E17](./P2/E17-chart-rectification.md) | Chart Rectification (multi-technique triangulation) | `#correctness` `#astrologer-ux` | **should** | E1a, E6a, existing transit + progression |

---

## Phase 3 — Scale to 10M (Month 6–12, 9 PRDs)

Ops hardening. Target: 100k → 10M users. No new user-facing features.

| ID | Title | Tags | Priority | Depends |
|---|---|---|:---:|---|
| [S2](./P3/S2-read-replicas-routing.md) | Read replicas + PgBouncer routing | `#performance` | **must** | F2, F3 |
| [S3](./P3/S3-three-layer-serving-cache.md) | 3-layer serving cache (Redis L1 + table L2 + facts L3) | `#performance` | **must** | F9 |
| [S5](./P3/S5-durable-workflow-orchestration.md) | Durable workflow orchestration (Temporal or procrastinate) | `#performance` `#correctness` | **must** | F8 |
| [S6](./P3/S6-lazy-compute-strategy.md) | Lazy compute for non-critical technique families | `#performance` | **must** | S5 |
| [P3-E6-flag](./P3/P3-E6-flag-feature-flagged-rule-rollouts.md) | Feature-flagged rule rollouts (shadow → 10% → 50% → 100%) | `#correctness` `#experimentation` | **must** | F4, F13 |
| [P3-E8-obs](./P3/P3-E8-obs-per-rule-observability.md) | Per-rule observability dashboards | `#correctness` | **must** | F8, F13 |
| [C5](./P3/C5-differential-testing-vs-reference.md) | Differential testing vs JH + Maitreya | `#correctness` | **should** | E15a |
| [P3-E2-console](./P3/P3-E2-console-rule-authoring-console.md) | Rule authoring console for non-engineers | `#extensibility` `#i18n` | **should** | F6 |
| [AI5](./P3/AI5-debate-mode-ultra-ai.md) | Debate-mode Ultra AI (shows strategy disagreement) | `#ai-chat` | **could** | E11b |

---

## Phase 4 — Scale to 100M (Year 1–2, 6 PRDs)

Hyperscale. Target: 10M → 100M users.

| ID | Title | Tags | Priority | Depends |
|---|---|---|:---:|---|
| [S4](./P4/S4-olap-replication-clickhouse.md) | OLAP replication (pg_logical → Kafka → ClickHouse) | `#performance` `#experimentation` | **must** | S3 |
| [S7](./P4/S7-sharding-citus-or-splitting.md) | Sharding (Citus extension or org-based split) | `#performance` | **must** | S2 |
| [S8](./P4/S8-shadow-compute-rule-migrations.md) | Shadow-compute rule migrations (1% shadow before promotion) | `#correctness` | **must** | F4, P3-E6-flag |
| [P4-E4-tenant](./P4/P4-E4-tenant-per-tenant-rule-overrides.md) | Per-tenant rule overrides | `#multi-tenant` `#extensibility` | **must** | F6 |
| [Reference-1000](./P4/Reference-1000-expanded-yoga-set.md) | Expanded 1000-yoga reference set | `#correctness` `#i18n` | **should** | E4b, P3-E2-console |
| [Research](./P4/Research-cross-source-agreement-dataset.md) | Cross-source agreement research dataset | — | **could** | S4 |

---

## Phase 5 — Category Dominance (Year 2–3, 12 PRDs)

Multi-modal, marketplace network effects. Target: 100M+ users.

| ID | Title | Tags | Priority |
|---|---|---|:---:|
| [D1](./P5/D1-voice-native-ai-astrologer.md) | Voice-native AI astrologer | `#ai-chat` `#end-user-ux` | **must** |
| [D2](./P5/D2-vision-ai-palm-face-tarot.md) | Vision AI (palmistry, face, tarot via camera) | `#ai-chat` `#end-user-ux` | **should** |
| [D3](./P5/D3-localization-20-plus-traditions.md) | Localization to 20+ languages × native traditions | `#i18n` `#extensibility` | **must** |
| [D4](./P5/D4-marketplace-network-effects.md) | Marketplace network effects | `#astrologer-ux` `#multi-tenant` | **must** |
| [D5](./P5/D5-biometric-integration.md) | Biometric integration (Apple Health, Oura, WHOOP) | `#end-user-ux` | **should** |
| [D6](./P5/D6-longitudinal-dashboard.md) | Longitudinal personal dashboard | `#experimentation` `#end-user-ux` | **must** |
| [D7](./P5/D7-research-data-api.md) | Research data API (anonymized, opt-in) | — | **should** |
| [D8](./P5/D8-astrologer-certification-program.md) | Astrologer certification ("Josi Certified") | `#astrologer-ux` | **should** |
| [D9](./P5/D9-enterprise-tier.md) | Enterprise tier (temples, corporate, matchmaking) | `#multi-tenant` | **should** |
| [D10](./P5/D10-federated-inter-platform.md) | Federated inter-platform agreement | `#experimentation` | **could** |
| [D11](./P5/D11-temple-muhurta-api.md) | Hindu temple muhurta-as-a-service API | `#multi-tenant` | **could** |
| [D12](./P5/D12-real-time-cosmic-events.md) | Real-time cosmic event streams | `#end-user-ux` | **could** |

---

## Phase 6 — Category Creation (Year 3–5, 11 PRDs)

Research, education, open-source foundation. Institutional scope.

| ID | Title | Tags | Priority |
|---|---|---|:---:|
| [I1](./P6/I1-josi-academy.md) | Josi Academy (curriculum + AI tutor) | `#extensibility` | **must** |
| [I2](./P6/I2-josi-research-press.md) | Josi Research Press (peer-reviewed publications) | — | **must** |
| [I3](./P6/I3-open-source-rule-engine.md) | Open-source the rule engine (Apache 2.0) | `#extensibility` | **must** |
| [I4](./P6/I4-generative-chart-synthesis.md) | Generative chart synthesis | `#ai-chat` | **should** |
| [I5](./P6/I5-cross-tradition-unified-reasoning.md) | Cross-tradition unified reasoning AI | `#ai-chat` | **must** |
| [I6](./P6/I6-digital-lifetime-companion.md) | Digital lifetime companion | `#end-user-ux` `#ai-chat` | **should** |
| [I7](./P6/I7-institutions-b2g-b2ngo.md) | Astrology for institutions (B2G / B2NGO) | `#multi-tenant` | **could** |
| [I8](./P6/I8-cross-modal-divination.md) | Cross-modal divination (tarot, I-Ching, runes, numerology) | `#extensibility` | **should** |
| [I9](./P6/I9-regulatory-certification-body.md) | Regulatory / certification body | — | **could** |
| [I10](./P6/I10-ten-thousand-yoga-reference.md) | The 10,000-yoga reference set | `#correctness` `#i18n` | **should** |
| [I11](./P6/I11-strategic-optionality.md) | Strategic optionality (IPO / acquisition readiness) | — | **could** |

---

## Filtering cheat-sheet

**All `must` PRDs in P1:**
```
grep -l "phase: P1-mvp" docs/markdown/prd/P1/*.md | xargs grep -l "priority: must"
```

**All `#correctness` PRDs:**
```
grep -lE "tags:.*#correctness" docs/markdown/prd/**/*.md
```

**What P3 items depend on F4?**
```
grep -l "depends_on:.*F4" docs/markdown/prd/P3/*.md
```

**Count by phase:**
```
for p in P0 P1 P2 P3 P4 P5 P6; do echo "$p: $(ls docs/markdown/prd/$p/*.md 2>/dev/null | wc -l)"; done
```
