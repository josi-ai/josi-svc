# PRD Review Tracker

Interactive review of all 95 PRDs across phases P0–P6 (76 original + 13 GAP_CLOSURE + 1 E-SLM + 5 payment). Every PRD gets checked off here — nothing skipped.

- **Reviewer:** @cpselvam
- **Started:** 2026-04-19
- **Total PRDs:** 95 (76 original + 13 GAP_CLOSURE + 1 E-SLM from §0.4 + 5 payment from §0.11; see `GAP_CLOSURE.md` + `ARCHITECTURE_DECISIONS.md`)
- **Pass 1 (Astrologer — calculation correctness + decision capture):** ✅ **COMPLETE — 29 / 29 astrology-heavy PRDs locked** (all P1 MVP ✅ · all P2 astrology-heavy ✅ · GAP_CLOSURE: E19, E23, E20, E21, E22, E27, E24, E25, E26, E28, E29, E18, E1c, E6b ✅ · E17 ✅ final)
- **Pass 2 (Engineering — 3-layer rubric: 12-point structural + 7-lens design + cross-cutting compliance, plus task DAG generation):** 4 / 95 (F1 ✅ retrofitted · F2 ✅ · F3 ✅ · F4 ✅ all 2026-04-25)
- **Cross-cutting locks:** 43 decisions in `DECISIONS.md` apply across all PRDs

---

## Review Rubric

**Pass 1 (Astrologer — calculation correctness)** uses the 6-point astrologer rubric in `feedback_astrologer_review_workflow.md`. This section documents **Pass 2 (Engineering)**.

Pass 2 is a **3-layer rubric** — each PRD is evaluated against all three layers, and findings from all three are folded into a `§ 2.5 Engineering Review` section stamped on the PRD.

### Layer 1 — Structural Completeness (12-point, pass/fail)

Fast check that the PRD has the sections an implementer needs. Every item is binary.

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

### Layer 2 — Design Quality (7-lens, findings-based)

Qualitative lens applied to each PRD. Surfaces gaps Layer 1 can't catch. Each lens can be ✅ / ⚠️ finding / N/A.

1. **Futuristic** — Anticipates 5-yr shifts (multimodal AI, agentic workflows, regulatory, global markets). Absorbs GPT-6 / Claude 5 / Gemini 3 without refactor.
2. **Future-proof** — Data model doesn't lock today's assumptions. Classical rules data-driven (YAML), not code. Calc versioning thought through.
3. **Extendible** — New tradition / yoga / dasa / dosha / kuta added without touching existing code. Plugin / registry pattern applied.
4. **Audit-ready** — Every calc has source-trace (which rule, which inputs, which code path). Immutable event log. Versioned rule registry. Reproducible from inputs + version.
5. **Performant** — Chart calc <500ms P95. Cache hit ratio targeted. Lazy compute for heavy ops. DB query budgets. Tenant isolation doesn't cost perf.
6. **User-friendly** — B2C complexity hidden; astrologer complexity exposed. Humane errors. Thoughtful loading states. Offline-first panchangam. Accessibility.
7. **AI-first** — Tool-use clean for LLMs. Structured outputs not free text. Context packaging for RAG. Qdrant vector hooks. Chart data AI-queryable natively.

### Layer 3 — Cross-cutting Compliance (architectural locks)

Checks the PRD against every lock in `ARCHITECTURE_DECISIONS.md` + `DECISIONS.md`. Each lock: ✅ / ⚠️ / N/A (with justification).

- **§0.5 liability posture** — crisis flow + wellness framing (applies to any AI-facing PRD)
- **§0.8 eval harness** — golden dataset + LLM-as-judge rubric + CI gate (applies to any AI-affecting PRD)
- **§0.9 audit architecture** — 5-layer reconstructability; fact tables store row_ids pinning rule versions (applies to any data-writing PRD)
- **§0.10 agent-team orchestration** — task DAG entry (acceptance_criteria / affected_paths / test_command / max_turns / model_tier / retry_budget) + path-overlap declaration (applies to all PRDs)
- **§0.12 naming conventions** — full English identifiers, no abbreviations, enum `id` column exception documented
- **§0.13 config-based versioning** — SCD Type 2 or equivalent DB-native versioning; no git SHA refs in schema
- **§0.14 PK conventions** — UUIDv7 PKs; enum tables add integer `id` + text code; FKs always UUID
- **Additional cross-cuts from DECISIONS.md** — e.g., §1.5 multilingual `classical_names`, §1.x node type / ayanamsa / house system (applies when PRD computes classical data)

### Output format per PRD

A `§ 2.5 Engineering Review` section stamped on the PRD with:
1. **Summary** — 2–4 sentences on overall shape
2. **Layer 1 scorecard** — 12-point table (pass/fail + note)
3. **Layer 2 findings** — 7-lens table (status + finding)
4. **Layer 3 compliance** — lock-by-lock table (status + evidence)
5. **Pass 2 Decisions** — anything locked during review (numbered `{PRD}-Q{n}`)
6. **Task DAG entries** — JSON for §0.10 agent orchestration
7. **Cross-references** — back-links to ARCHITECTURE_DECISIONS + DECISIONS sections touched

**Status legend:** ⬜ not started · 🟡 in review · 🟢 approved · ✏️ needs revision · 🚧 blocked

---

## Phase P0 — Foundation (17 PRDs)

| # | ID | Title | Status | Notes |
|:-:|---|---|:-:|---|
| 1 | [F1](./P0/F1-star-schema-dimensions.md) | Star-schema dimension tables | 🟢 | Pass 2 ✅ 2026-04-23 — 4 F1-Q decisions locked + schema revised to 7 tables (3 enum lookup + 4 SCD Type 2). UUID PK universal + integer `id` for IntEnum mapping. `classical_names` JSONB multilingual. `experiment`/`experiment_arm` moved to E14a. 5-task DAG entry generated. See F1 §2.5. |
| 2 | [F2](./P0/F2-fact-tables.md) | Fact tables with composite FKs | 🟢 | Pass 2 ✅ 2026-04-25 — 5 F2-Q decisions locked. UUID PK + composite UNIQUE (§0.14). Text-code FKs + SCD row_id pins (F2-Q2+Q5 hybrid for §0.9). `experiment`/`experiment_arm` removed (deferred to E14a per F1-Q4 cascade). `id` → `aggregation_{event,signal}_id` (§0.12). 6-task DAG. See F2 §2.5. |
| 3 | [F3](./P0/F3-partitioning-from-day-one.md) | HASH(chart_id, 16) + monthly RANGE partitioning | 🟢 | Pass 2 ✅ 2026-04-25 — 5 F3-Q decisions locked. Simplified from LIST+HASH (65 partitions) to HASH-only (16 partitions) on technique_compute; chart-scoped reads are 99% of traffic. Dropped pg_partman in favor of ~80 LOC custom PartitionManager (cloud-portable). Composite PKs include partition keys per PG rule. F1+F2 cascade fully absorbed. Effort 3d→1.5d. See F3 §2.5. |
| 4 | [F4](./P0/F4-temporal-rule-versioning.md) | Temporal rule versioning (RFC 8785, semver, overlap trigger) | 🟢 | Pass 2 ✅ 2026-04-25 — 3 F4-Q decisions locked. **F4-Q1: RFC 8785 (JCS) replaces custom JCJ** — internet standard, byte-identical for our inputs, unblocks multi-language SDK + cryptographic signing futures. F4-Q2: trigger SQL renamed `rule_id`→`rule_code`, `source_id`→`source_authority_code` per F2 Pass 2. F4-Q3: F2's `idx_classical_rule_active` dropped; replaced by UNIQUE `idx_classical_rule_one_active`. 6-task DAG. Effort 3d→2d. See F4 §2.5. |
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

## Phase P1 — MVP Engines + Launch-blocking Payments (12 PRDs; 7 original + 5 payment)

| # | ID | Title | Status | Notes |
|:-:|---|---|:-:|---|
| 18 | [E1a](./P1/E1a-multi-dasa-v1.md) | Multi-Dasa Engine v1 | 🟡 | Pass 1 ✅ 2026-04-21 — 11 locks (Q3/Q4/Q7/Q8/Q9/Q10/Q11 + 4 cross-cutting); see E1a §2.4 |
| 19 | [E2a](./P1/E2a-ashtakavarga-v2.md) | Ashtakavarga v2 | 🟡 | Pass 1 ✅ 2026-04-21 — 5 E2a locks (Q1/Q2/Q3/Q4/Q5) + 10 cross-cutting; see E2a §2.4; Q2 post-research correction (per-sign Rashi Pinda, not 3-fold) |
| 20 | [E4a](./P1/E4a-yoga-engine-mvp.md) | Classical Yoga Engine MVP (60) | 🟡 | Pass 1 ✅ 2026-04-21 — 8 E4a locks (Q1/Q2/Q3/Q4/Q5/Q6/Q7/Q8) + 6 cross-cutting; 4 research agents used (Neecha Bhanga, Graha Drishti, Tamil node-aspect variance, fixture coverage gap); see E4a §2.4 |
| 21 | [E6a](./P1/E6a-transit-intelligence-v1.md) | Transit Intelligence v1 | 🟡 | Pass 1 ✅ 2026-04-21 — 7 E6a locks (Q1-Q7) + 6 cross-cutting; see E6a §2.4 |
| 22 | [E11a](./P1/E11a-ai-chat-orchestration-v1.md) | AI Chat Orchestration v1 | ⬜ | |
| 23 | [E14a](./P1/E14a-experimentation-framework-v1.md) | Experimentation Framework v1 | ⬜ | |
| 24 | [E15a](./P1/E15a-correctness-harness-v1.md) | Correctness Harness v1 | ⬜ | |
| 25 | E-BILLING *(file pending)* | B2C subscription billing (Flows 1+2) | 🚧 | Architecture locked 2026-04-23 in ARCHITECTURE_DECISIONS §0.11. Razorpay India + Stripe rest-of-world. Subscription lifecycle + tier transitions + consultation purchases. Launch blocker per §0.2. PRD file to be authored in Pass 2. |
| 26 | E-PAYOUT *(file pending)* | Astrologer marketplace payouts (Flow 3) | 🚧 | Architecture locked 2026-04-23 in ARCHITECTURE_DECISIONS §0.11. RazorpayX Route (India) + Stripe Connect (US/UK/EU). Weekly cadence. Cross-border FX via LRS corridor. KYC at onboarding. Launch blocker. PRD file to be authored in Pass 2. |
| 27 | E-METER *(file pending)* | B2B API metered billing (Flow 4) | 🚧 | Architecture locked 2026-04-23 in ARCHITECTURE_DECISIONS §0.11. Stripe Meters usage-based pricing. Per-tenant spend caps. Tier + overage model. Tenant portal. Enterprise contracts. Launch blocker for B2B. PRD file to be authored in Pass 2. |
| 28 | E-TRUST *(file pending)* | Trust & Safety (disputes / refunds / fraud / sanctions) | 🚧 | Architecture locked 2026-04-23 in ARCHITECTURE_DECISIONS §0.11. Dispute 48h SLA. Fraud detection on top of Stripe Radar. Sanctions screening (OFAC/UN/EU/UK). Consultation dispute workflow. Launch blocker. PRD file to be authored in Pass 2. |
| 29 | E-TAX *(file pending)* | Tax compliance automation | 🚧 | Architecture locked 2026-04-23 in ARCHITECTURE_DECISIONS §0.11. GST India + Stripe Tax (US state + EU VAT-OSS + UK VAT) + 1099-K/1042-S generation. Automated invoice per transaction. Launch blocker. PRD file to be authored in Pass 2. |

## Phase P2 — Breadth & UIs (27 PRDs; 14 original + 13 GAP_CLOSURE)

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
| 39 | E18 *(file pending)* | Sudarshana Chakra + Triple-Affirmation Analysis | 🚧 | Pass 1 ✅ 2026-04-22 — locks in DECISIONS §6.5 E18. Jataka Parijata Ch.11 + Sarvartha Chintamani. PRD file to be authored in Pass 2. |
| 40 | E19 *(file pending)* | Shadbalam Engine | 🚧 | Pass 1 ✅ 2026-04-22 — locks in DECISIONS §6.5 E19. 6 balas + Budhan dual-classification. Inherits §1.7 Shadbalam + thresholds. PRD file to be authored in Pass 2. |
| 41 | E20 *(file pending)* | Bhava Bala Engine | 🚧 | Pass 1 ✅ 2026-04-22 — locks in DECISIONS §6.5 E20. Bhavadhipati + Digbala-Bhavasya + Bhava Drishti decomposition. PRD file to be authored in Pass 2. |
| 42 | E21 *(file pending)* | Vimshopaka Bala | 🚧 | Pass 1 ✅ 2026-04-22 — locks in DECISIONS §6.5 E21. 20-point divisional synthesis. PRD file to be authored in Pass 2. |
| 43 | E22 *(file pending)* | Avastha Suite | 🚧 | Pass 1 ✅ 2026-04-22 — locks in DECISIONS §6.5 E22. All 5 classical schemes (Baladi / Jagrat-Swapna-Sushupti / 9-fold / Lajjitadi / Arohana-Avarohana). PRD file to be authored in Pass 2. |
| 44 | E23 *(file pending)* | Panchadha Maitri | 🚧 | Pass 1 ✅ 2026-04-22 — locks in DECISIONS §6.5 E23. 5-fold composite friendship. Feeds E19 Sthana Bala. PRD file to be authored in Pass 2. |
| 45 | E24 *(file pending)* | Janma-Tara 9-Cycle | 🚧 | Pass 1 ✅ 2026-04-22 — locks in DECISIONS §6.5 E24. Tara cycle per Muhurta Chintamani Ch.3. Feeds E25 + muhurtam. PRD file to be authored in Pass 2. |
| 46 | E25 *(file pending)* | Ashtakoota Milan + Manglik | 🚧 | Pass 1 ✅ 2026-04-22 (Q2 revised 5-house Lagna-only 2026-04-22) — locks in DECISIONS §6.5 E25. 8-koota + Manglik + Rajju/Vedha. PRD file to be authored in Pass 2. |
| 47 | E26 *(file pending)* | Special Lagnas Suite | 🚧 | Pass 1 ✅ 2026-04-22 — locks in DECISIONS §6.5 E26. 10 Special Lagnas (Bhava/Hora Lagna/Ghati/Vighati/Sri/Indu/Pranapada/Varnada/Nisheka/Vakra-Shoola). PRD file to be authored in Pass 2. |
| 48 | E27 *(file pending)* | Maraka-Badhaka Engine | 🚧 | Pass 1 ✅ 2026-04-22 (Q6 KP Maraka deferred 2026-04-23) — locks in DECISIONS §6.5 E27. Parashari-only v1. Inherits E5b ethical gating. PRD file to be authored in Pass 2. |
| 49 | E28 *(file pending)* | Upaya / Remedies Engine | 🚧 | Pass 1 ✅ 2026-04-22 — locks in DECISIONS §6.5 E28. Rule-registry dosha→upaya mapping with regional auto-adapt. PRD file to be authored in Pass 2. |
| 50 | E29 *(file pending)* | Thirumana Porutham (Tamil 10-porutham) | 🚧 | Pass 1 ✅ 2026-04-22 — locks in DECISIONS §6.5 E29. Tamil-specific wedding matching. PRD file to be authored in Pass 2. |
| 51 | E1c *(file pending)* | Extended Dasa Pack | 🚧 | Pass 1 ✅ 2026-04-22 — locks in DECISIONS §6.5 E1c. 5 minor kalpas (Chathurseethi-sama 84yr, Dwisaptati-sama 72yr, Panchottari, Shodashottari, Shatabdika). Eligibility predicates per-dasa (not inherited from Ashtottari §1.6). PRD file to be authored in Pass 2. |

**Note on 🚧 rows:** These 13 GAP_CLOSURE PRDs have Pass 1 decisions locked in `DECISIONS.md §6.5`; their PRD files will be authored during Engineering Pass 2 per the engineering action items listed in each §6.5 entry. The `🚧` status distinguishes "PRD file pending but Pass 1 locks exist" from `⬜` ("no Pass 1 decisions yet").

## Phase P3 — Scale to 10M (10 PRDs; 9 original + 1 GAP_CLOSURE)

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
| 48 | E6b *(file pending)* | Transit Intelligence v2 | 🚧 | Pass 1 ✅ 2026-04-22 — locks in DECISIONS §6.5 E6b. Transit Ashtakavargam + Vedha + Lattha + Tara/Chandra Bala + Graha-Karaka transit + Kal Sarpa transit. PRD file to be authored in Pass 2 under P3. |
| 49 | E-SLM *(file pending)* | Proprietary Astrology SLM (fine-tuned OSS) | 🚧 | Architecture locked 2026-04-23 in ARCHITECTURE_DECISIONS §0.4. Fine-tuned 7B-13B model (Llama-3 / Qwen-2.5) on Josi proprietary data (interpretations + consultation transcripts + NPQ + user feedback). Prerequisites: 100K+ interpretations + 1K+ consultations + opt-in consent framework. Target: 60-70% of B2C interpretation volume at ~10% frontier API cost. Defensive moat. PRD file to be authored when prerequisites hit. |

## Phase P4 — Scale to 100M (7 PRDs; 6 original + 1 SLM-adjacent if promoted from P3)

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
