---
prd_id: I6
epic_id: I6
title: "Digital Lifetime Companion — Longitudinal Chart-Aware AI"
phase: P6-institution
tags: [#end-user-ux, #ai-chat, #experimentation]
priority: should
depends_on: [I5, D6, D7, D5, I2]
enables: [I2, I7]
classical_sources: []
estimated_effort: 4+ quarters (Year 4 through Year 5)
status: draft
author: "@claude"
last_updated: 2026-04-19
---

# I6 — Digital Lifetime Companion

## 1. Purpose & Rationale

The default AI astrology experience is stateless: ask a question, receive a reading, close tab. I6 inverts this into a **longitudinal companion**: a chart-aware AI that accompanies a user over years or decades, tracking their decisions, their outcomes, their subjective reports, and refining its guidance against lived-life feedback.

Over time, a user's archive becomes a uniquely personal record of prediction vs. outcome — the first at-scale, structured longitudinal astrology dataset of its kind. With strong consent and encryption, aggregated signals feed I2 research (improving classical-technique accuracy empirically) and personalize the companion itself (what style of guidance this user finds most actionable).

**Strategic value:**
- Deep retention: users who start a lifetime journal at 25 have a 50-year relationship with Josi.
- Unique data asset: no competitor has longitudinal prediction-vs-outcome data. This is the gold-standard signal (master spec §1.4).
- Product moat: emotional switching cost (your life archive) is the strongest moat available.
- Research generator: empirical validation of classical techniques at scale — category-creation-level contribution.
- Enables I2 (papers on observed accuracy), I7 (institutional longitudinal studies).

## 2. Scope

### 2.1 In scope
- Personal journal: timeline of life events, decisions, emotions, tagged to chart placements and current dasa/transit state.
- AI check-ins: weekly or monthly prompts asking about key life domains (career, health, relationships, mental state).
- Prediction/retrospective tracking: AI makes explicit short- and long-term calls ("this Saturn transit could create career friction for 9 months"); user later reports what actually happened.
- Self-reflection prompts building on prior responses ("last quarter you described feeling stuck in work — three months on, what shifted?"). Builds on existing Neural Pathway Questions concept.
- Memory architecture: vector store of user responses + structured tags for retrieval.
- Strong privacy: end-to-end encryption options; fine-grained consent per data type.
- Export: full data portability (open format).
- Aggregate research contribution: opt-in, k-anonymized, feeds I2.
- Integration with biometrics (D5) for corroborative signals where user opts in.

### 2.2 Out of scope
- Medical record integration (regulated; separate legal track).
- Therapy replacement (explicitly not a therapeutic product; referral pathways only).
- Social features (sharing feeds, friend comparisons) — intentionally intimate, solo product.
- Predictions sold as tradeable signals (no financial advisor framing).
- Deceased-user "legacy" features in Year 4 launch (considered for Year 5+).

### 2.3 Dependencies
- **I5 (Cross-tradition unified reasoning)** — the voice of the companion.
- **D6 (Longitudinal dashboard)** — UI primitives; I6 is the AI layer on top.
- **D7 (Research data API)** — opt-in research export.
- **D5 (Biometric integration)** — optional corroborative signals.
- **I2 (Research Press)** — publication pathway.
- **Privacy/legal** — per-jurisdiction data retention, GDPR, CCPA, plus mental-health safeguarding laws.
- **Crisis response infrastructure** — if user expresses self-harm ideation, clear escalation pathway.

## 3. Technical Research

### 3.1 Memory architecture

Three memory layers:

1. **Structured memory** (Postgres tables): life events, decisions, outcomes, tagged to chart context (current dasa, active transits, relevant yogas) at the moment of capture.
2. **Semantic memory** (Qdrant): embeddings of user's free-text responses for similarity retrieval ("what did I say last year about career direction?").
3. **Rolling summary** (LLM-generated, stored per user): monthly condensed narrative so companion doesn't need full history in context.

For each interaction, the companion retrieves: (a) current chart state, (b) top-k semantically similar prior entries, (c) latest rolling summary. Fed to I5 orchestrator with companion-specific system prompt.

### 3.2 Privacy-first design

- **End-to-end encryption option**: user-controlled key; Josi servers store ciphertext only; AI processing requires user session + ephemeral key unsealing. Trade-off: no server-side analytics or research contribution unless user explicitly shares aggregated derivatives.
- **Default mode** (standard): server-side encryption at rest; Josi can process for personalization; research contribution opt-in.
- **Fine-grained consent**: per data type (health, relationships, financial, etc.); consent deltas logged immutably.
- **Right to deletion**: full erasure within 30 days; audit trail of deletion.
- **Data portability**: JSON/Markdown export including vector-store embeddings in standard format (e.g., OpenAI-compatible JSON Lines).

### 3.3 Prediction tracking

Explicit predictions are stored as structured objects:

```yaml
prediction:
  id: pred_123
  made_at: 2027-03-01
  horizon_start: 2027-04-01
  horizon_end: 2027-12-31
  statement: "Transit of Saturn over natal Mercury may create communication friction at work."
  tradition: vedic
  source_rules: [rule_id_x, rule_id_y]
  confidence: 0.72
  resolution:
    user_report: "Yes, had a tough quarter with my manager."
    reported_at: 2028-01-15
    classification: confirmed | partial | not_observed
    user_confidence: 0.9
```

Over time, these prediction-outcome pairs compose per-user and (with opt-in) population-level validation signal for the engine.

### 3.4 Ethical safeguards

- Never advise on acute medical, legal, or financial matters; direct to licensed professional.
- Self-harm detection (standard LLM safety layer + heuristics) triggers crisis-resource hand-off.
- No amplification of fatalistic framings ("you're doomed in 2030"); companion reframes as "tendencies, choices, and agency."
- Regular "consent refresh" prompts (e.g., yearly) confirming user still wants the companion active.
- Withdrawal / pause mode: user can hibernate the companion without deleting history.

### 3.5 Alternatives considered

| Alternative | Rejected because |
|---|---|
| No memory — stateless chat only | Defeats core thesis. |
| Memory but no explicit prediction tracking | Misses the research + retention upside. |
| Social / shared journal | Misaligned with intimate product; privacy risks. |
| Therapist-partnered product | Regulatory minefield; out of scope. |

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| End-to-end encryption default | Opt-in for E2E; standard = server-side encryption | E2E blocks research + personalization; user choice. |
| Prediction horizon length | Short (weeks), medium (months), long (years) — tiered | Meaningful signals at different time scales. |
| Check-in cadence | Weekly default; user-configurable | Balance between engagement and fatigue. |
| Crisis detection | Anthropic/Claude safety + custom heuristics + clinician-reviewed response templates | Safety non-negotiable. |
| Deletion vs archival | Full erasure option + reversible hibernation option | Both serve different user needs. |
| Research contribution threshold | k ≥ 100 for any published aggregate | Standard anonymization; alignment with I2. |
| Multi-device sync | Yes, via Josi auth + encrypted sync | Life companion must be available everywhere. |
| Inheritance / legacy access | Out of scope Year 4; revisit Year 5+ | Legal complexity. |

## 5. Component Design

### 5.1 New services / modules

```
src/josi/companion/
├── memory/
│   ├── structured_memory.py
│   ├── semantic_memory.py      # Qdrant interface
│   └── rolling_summary.py
├── predictions/
│   ├── tracking.py
│   └── resolution.py
├── checkins/
│   ├── scheduler.py
│   └── prompts.py
├── consent/
│   ├── policy.py
│   └── audit.py
├── safety/
│   ├── crisis_detection.py
│   └── escalation.py
└── export/
    └── portability.py

src/josi/api/v1/controllers/companion_controller.py
```

### 5.2 Data model additions

```sql
CREATE TABLE companion_consent (
  user_id FK, data_category TEXT,
  consent_state TEXT,  -- 'granted'|'denied'|'revoked'
  changed_at TIMESTAMPTZ,
  audit_hash TEXT,
  PRIMARY KEY (user_id, data_category)
);

CREATE TABLE companion_life_event (
  event_id UUID PK, user_id FK, occurred_at TIMESTAMPTZ NULL,
  recorded_at TIMESTAMPTZ, category TEXT, body TEXT,
  tags JSONB, chart_context JSONB,
  encryption_mode TEXT  -- 'server'|'e2e'
);

CREATE TABLE companion_prediction (
  prediction_id UUID PK, user_id FK,
  made_at TIMESTAMPTZ, horizon_start TIMESTAMPTZ, horizon_end TIMESTAMPTZ,
  statement TEXT, tradition TEXT, source_rule_refs JSONB,
  confidence NUMERIC(3,2),
  resolution JSONB NULL,
  resolved_at TIMESTAMPTZ NULL
);

CREATE TABLE companion_checkin (
  checkin_id UUID PK, user_id FK, scheduled_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ NULL, response_body TEXT NULL
);

CREATE TABLE companion_rolling_summary (
  user_id FK, period_month TEXT,  -- YYYY-MM
  summary TEXT, generated_at TIMESTAMPTZ,
  PRIMARY KEY (user_id, period_month)
);
```

### 5.3 API contract

```
POST /api/v1/companion/events
GET  /api/v1/companion/events
POST /api/v1/companion/predictions
POST /api/v1/companion/predictions/{id}/resolve
GET  /api/v1/companion/checkins/upcoming
POST /api/v1/companion/checkins/{id}/respond
POST /api/v1/companion/ask             # chat with memory context
GET  /api/v1/companion/export           # full portable archive
POST /api/v1/companion/hibernate
POST /api/v1/companion/delete           # full erasure request
GET  /api/v1/companion/consent
PUT  /api/v1/companion/consent
```

## 6. User Stories

### US-I6.1: As a 28-year-old user, I want a journal that correlates my life events with chart placements
**Acceptance:** add event → AI tags it with current dasa/transit context → retrievable 5 years later with full context.

### US-I6.2: As a privacy-conscious user, I want end-to-end encryption for sensitive entries
**Acceptance:** opt-in E2E; Josi cannot read content; recovery-phrase-based key; loss of phrase = loss of data (clearly explained).

### US-I6.3: As a long-term user, I want to see accuracy stats on past predictions
**Acceptance:** "Accuracy Dashboard" shows predictions made, resolved, confirmed/partial/not observed; per-tradition breakdown.

### US-I6.4: As a PhD researcher, I want anonymized longitudinal prediction-outcome data
**Acceptance:** D7 exposes aggregate stats; opt-in share rate visible; k ≥ 100; no PII.

### US-I6.5: As a user in a rough life period, I want the companion to recognize distress and surface resources
**Acceptance:** self-harm indicators → immediate hand-off to crisis resources (per jurisdiction); companion does not give astrological "fate" framing.

### US-I6.6: As a user who decides to leave Josi, I want to take my data with me
**Acceptance:** one-click export; receives JSON archive with events, predictions, embeddings; can be re-imported elsewhere.

### US-I6.7: As a Pro astrologer (with client consent), I want to reference a client's prediction archive
**Acceptance:** client-initiated share; read-only, time-scoped token; audit trail.

## 7. Tasks

### T-I6.1: Memory architecture
- **Definition:** Structured + semantic + rolling-summary layers wired; ingestion pipeline.
- **Acceptance:** End-to-end: add event → retrievable in 3 modalities within 5s.
- **Effort:** Q1.

### T-I6.2: Consent + encryption
- **Definition:** Fine-grained consent model; E2E mode with client-side key management.
- **Acceptance:** E2E verified by security audit; consent audit trail immutable.
- **Effort:** Q1–Q2.

### T-I6.3: Prediction tracking + resolution UX
- **Definition:** Data model + UX for making predictions + resolution prompts at horizon end.
- **Acceptance:** Resolution prompt delivered within 48h of horizon end; user can resolve asynchronously.
- **Effort:** Q2.

### T-I6.4: Check-in scheduler + prompts
- **Definition:** Cron-like scheduler per user; prompt library; personalization hooks (use rolling summary).
- **Acceptance:** User receives weekly prompt at configured time; prompt references a real recent chart event or prior entry.
- **Effort:** Q2.

### T-I6.5: Safety layer
- **Definition:** Crisis detection; escalation playbook; localized crisis resources.
- **Acceptance:** Clinician-reviewed playbook; 100% of simulated crisis inputs trigger correct escalation.
- **Effort:** Q2–Q3.

### T-I6.6: Companion conversational UX
- **Definition:** Chat integrated with memory retrieval; I5 orchestrator underneath.
- **Acceptance:** Memory-aware conversation passes 30 scripted user scenarios.
- **Effort:** Q3.

### T-I6.7: Accuracy dashboard
- **Definition:** Per-user dashboard summarizing predictions made, resolved, confirmed; tradition breakdown.
- **Acceptance:** Dashboard loads < 500ms; accurate; exportable.
- **Effort:** Q3.

### T-I6.8: Export + deletion + hibernation
- **Definition:** Data portability JSON format; deletion workflow; hibernation pause.
- **Acceptance:** Full export ≤ 2 min; deletion fully complete ≤ 30 days with audit confirmation.
- **Effort:** Q3.

### T-I6.9: Research-pipeline integration
- **Definition:** D7 aggregated export; consent-gated; k-anonymity enforced.
- **Acceptance:** Research export for N=1000 users (opt-in synthetic set) produces non-PII dataset.
- **Effort:** Q4.

### T-I6.10: Public launch + crisis-response SLAs
- **Definition:** Marketing + SLAs + 24/7 crisis-escalation monitoring for first 6 months.
- **Acceptance:** Launched with SLA dashboard; 100% crisis response within defined time window.
- **Effort:** Q4.

## 8. Unit Tests

### 8.1 Memory retrieval tests
| Test category | Representative names | Success target |
|---|---|---|
| Semantic retrieval relevance | `test_top_k_retrieval_relevance_on_gold_set` | Recall@5 ≥ 0.75 on held-out Q&A set |
| Rolling summary accuracy | `test_rolling_summary_captures_key_themes` | Panel rating ≥ 4/5 on 50 sampled summaries |
| Temporal ordering | `test_retrieval_respects_temporal_bounds` | 100% correctness on temporal-scoped queries |

### 8.2 Prediction lifecycle tests
| Test category | Representative names | Success target |
|---|---|---|
| Horizon-end prompt delivery | `test_resolution_prompt_on_horizon_end` | ≥ 95% delivery within 48h |
| Classification integrity | `test_resolution_classification_enum` | 100% of resolutions have valid classification |
| Per-user accuracy computation | `test_accuracy_dashboard_math` | Unit math verified on synthetic data |

### 8.3 Consent + privacy tests
| Test category | Representative names | Success target |
|---|---|---|
| E2E encryption | `test_e2e_entries_unreadable_server_side` | Server DB dump contains no plaintext |
| Consent audit immutability | `test_consent_change_logged_append_only` | 100% immutability verified |
| Deletion completeness | `test_full_deletion_clears_all_tables_within_30d` | 100% verified via end-to-end test |
| Data portability format | `test_export_roundtrip_reimport` | 100% of exported archive re-importable |

### 8.4 Safety tests
| Test category | Representative names | Success target |
|---|---|---|
| Crisis-indicator detection | `test_self_harm_keywords_trigger_escalation` | ≥ 99% recall on clinician-curated red-team set |
| Crisis-resource localization | `test_crisis_resources_per_jurisdiction` | 100% jurisdictional coverage where launched |
| Fatalism reframing | `test_fatalistic_prediction_reframed` | ≥ 95% of fatalistic phrasings reframed to agency |

### 8.5 Research pipeline tests
| Test category | Representative names | Success target |
|---|---|---|
| k-anonymity enforcement | `test_aggregate_export_k_ge_100` | 100% |
| Consent-gated inclusion | `test_non_consenters_excluded_from_export` | 100% |

### 8.6 Longitudinal / cohort tests
| Test category | Representative names | Success target |
|---|---|---|
| 1-year retention | `test_companion_1_year_active_rate` | ≥ 40% of cohort still active at 12 months |
| Prediction-resolution rate | `test_prediction_resolution_completion` | ≥ 60% of predictions resolved by users |

## 9. EPIC-Level Acceptance Criteria

- [ ] Memory architecture (structured + semantic + rolling) operational.
- [ ] E2E encryption option available and security-audited.
- [ ] Consent + audit + deletion complete and legal-reviewed (GDPR/CCPA).
- [ ] Prediction tracking + resolution + accuracy dashboard shipped.
- [ ] Weekly check-in scheduler running for all opted-in users.
- [ ] Crisis-detection + escalation playbook clinician-reviewed and operational.
- [ ] Data portability export tested end-to-end.
- [ ] Research pipeline delivering k ≥ 100 aggregate exports to D7 (opt-in).
- [ ] 12-month retention ≥ 40% in launch cohort.
- [ ] First I2 paper on longitudinal prediction-outcome correlation drafted.

## 10. Rollout Plan

**Gate 0 — Closed alpha (Year 4 Q1):**
- Feature flag: `companion_alpha`; 100 invited users.
- **Gate to proceed:** memory retrieval relevance ≥ 0.75; crisis simulations pass.

**Gate 1 — Ultra tier beta (Year 4 Q2):**
- Ultra subscribers opt-in.
- **Gate to proceed:** NPS ≥ 50; 0 unmitigated crisis-handling failures; privacy audit clean.

**Gate 2 — Public launch (Year 4 Q3):**
- Available to all users as premium feature.
- **Gate to proceed to research contribution:** consent flows stable; k-anonymity verified.

**Gate 3 — Research publication (Year 5):**
- First longitudinal paper with opt-in data submitted to I2.
- **Gate to I7:** 12-month retention and crisis-SLA maintained.

**Rollback plan:** disable new companion features; existing archives remain accessible in read-only mode; users can still export. No data deletion on rollback.

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| User in crisis receives inadequate support, leading to harm | Low | Catastrophic | Clinician-designed detection + escalation; 24/7 monitoring first 6 months; legal review per jurisdiction. |
| Data breach of sensitive long-term journals | Low | Catastrophic | E2E option; encryption at rest; SOC 2 controls; bug-bounty. |
| User becomes overly dependent / parasocial | Medium | Medium | Framing, limits on check-in frequency, clinician-reviewed prompts avoiding dependency language. |
| Astrology-based "life predictions" harm decision-making | Medium | High | Disclaimers; agency-centering prompts; never medical/legal/financial advice. |
| Retention collapses after novelty phase | High | Medium | Personalization, meaningful reflection, low-friction journaling UI; D6 dashboard engagement. |
| Regulatory classification as medical device in EU (AI Act) | Medium | High | Legal review; conspicuous non-medical framing; EU-specific adaptation if needed. |
| Inheritance / legacy access after user death | Medium | Low | Documented terms: hibernation on inactivity; family-access process deferred to Year 5+. |
| Research contribution exposes individuals via re-identification attack | Low | High | k ≥ 100 floor; external privacy audit; differential privacy added in Year 5. |
| Prediction tracking evolves into gambling / fatalism | Low | Medium | Classification emphasizes "tendencies"; partial/ambiguous categories; no "points". |
| Scale of data (billions of entries) overwhelms infra | Medium | Medium | Partitioning per user; hot/cold tiering; archival storage for 5+ year-old entries. |
| Consent revocation creates reconciliation complexity with ongoing research datasets | Medium | Medium | Immutable "publication cut" snapshots + prospective consent; deletion only affects future. |
| Localization of crisis resources expensive and error-prone | Medium | High | Partnership with international mental-health orgs; launch-country gating until resources verified. |

## 12. References

- Master spec: `docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md` — §1.4 gold-standard signal.
- Related PRDs: I5, D6, D7, D5, I2, I7
- GDPR Article 17 (right to erasure), CCPA right to delete.
- Clinical guidance: WHO suicide-prevention resources; crisis-response best practices.
- Longitudinal research ethics: Belmont Report; IRB standards.
- Vector memory patterns: LangChain memory, Mem0, Letta frameworks.
