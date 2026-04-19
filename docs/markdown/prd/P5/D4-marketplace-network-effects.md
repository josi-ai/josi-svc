---
prd_id: D4
epic_id: D4
title: "Marketplace network effects (referrals, supervisor/apprentice, specialization matching, reputation graph)"
phase: P5-dominance
tags: [#astrologer-ux, #multi-tenant, #end-user-ux, #experimentation]
priority: must
depends_on: [E12, D3, D8]
enables: [D8, D9]
classical_sources: []
estimated_effort: 10-14 weeks
status: draft
author: "@agent"
last_updated: 2026-04-19
---

# D4 — Marketplace Network Effects

## 1. Purpose & Rationale

Josi's marketplace at P2/P3 is transactional — users book astrologers; astrologers take bookings. That's linear growth. At 100M+ users, marketplace value compounds when astrologers **network with each other** and the matching engine gets exponentially smarter.

Three network-effect layers:
1. **Astrologer-to-astrologer referrals** — a Vedic master receives a career question better answered by a KP specialist; with one tap, referral; revenue-share on closed consultations. Expands per-astrologer earnings without zero-sum competition.
2. **Supervisor/apprentice hierarchies** — senior astrologers mentor juniors; supervision visible in apprentice profiles ("trained under X"); apprentice early-work reviewed. Creates a reputation spine.
3. **Specialization matching** — users describe needs in natural language; matching engine combines chart-compatibility, tradition, language, specialization, price, availability, and reputation graph to rank. Matching gets better with data.

Together, these turn the marketplace from a flat directory into a **reputation graph**, strengthening per-marginal-astrologer value.

## 2. Scope

### 2.1 In scope
- Referral workflow: astrologer-A initiates referral to astrologer-B; revenue-share configurable per referral (default 15% to referrer); 30-day attribution window
- Supervisor/apprentice relationships: formal opt-in links; supervision agreements stored; public "trained under" badge; apprentice gating (first N consultations reviewed)
- Reputation graph data model: nodes = astrologers, edges = referrals/supervisions/endorsements, weighted by successful-outcome signals
- Specialization matcher service: NL query → ranked astrologer list with explainability
- Reputation surfacing in ranking (D8 certification level + graph score)
- Anti-gaming: detection of referral rings, self-referrals, fake endorsements
- Revenue-share accounting + Stripe Connect flows for split payouts
- Astrologer discovery API (v2) with ranking explanation

### 2.2 Out of scope
- Marketplace pricing optimization (dynamic pricing) — D4 includes display and filters; dynamic pricing is a separate algorithm PRD post-D4
- Astrologer chat/DM between astrologers — nice-to-have, deferred
- Consumer-side social graph ("friends who used X") — separate concept, not marketplace-side

### 2.3 Dependencies
- E12 Astrologer Workbench (exists for astrologer UX)
- D8 Certification (provides reputation anchor)
- D3 Localization (specialization matching needs language axis)
- Stripe Connect already integrated at P2
- F8 aggregation engine for signal fusion in matching

## 3. Technical Research

### 3.1 Reputation graph algorithms

Options for graph-based reputation:
- **Personalized PageRank** — proven, computable at scale; used by StackOverflow, Academia.edu
- **HITS (hubs and authorities)** — too symmetric for asymmetric trust
- **TrustRank** — targets spam resistance; good for anti-gaming
- **Bespoke weighted propagation** — custom blend

Decision: Personalized PageRank on a weighted DAG, with TrustRank-style seed-sets for abuse resistance. Recomputed nightly; incremental updates via delta.

### 3.2 Matching engine

Inputs:
- User chart features (via F9 `chart_reading_view`)
- User query text (natural language)
- User preferences (tradition, language, gender preference, price band)
- Availability (calendar)
- Astrologer features (certification, specializations, reputation graph score, recent NPS, historical outcome correlations from D6)

Approach: hybrid retrieval → learned ranker. Retrieval: inverted-index + semantic embedding on astrologer profile. Ranking: gradient-boosted trees or small transformer, features above.

Explainability required: every returned astrologer shows *why* ("matches because: Vedic + Tamil-speaking + 5 similar chart consultations in past year with 4.8/5 avg").

### 3.3 Anti-gaming

Adversarial scenarios:
1. Astrologer rings boost each other's graph scores
2. Fake apprentices created for "trained under" badge
3. Self-referrals with fake users
4. Review-bombing via sockpuppets

Defenses:
- Graph structure anomaly detection (clustering, reciprocity ratios)
- Consultation-based revenue attribution (no revenue → no graph weight)
- Identity verification gating for supervisor role
- Device/network fingerprint dedup for users
- Mandatory minimum consultation volume for supervisor eligibility

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| Referral revenue-share default | 15% to referrer for 30 days | Industry-standard; balances incentive + fairness |
| Supervisor eligibility | ≥ 500 consultations + Gold cert (D8) + 12+ months tenure | Prevents "instant mentors" gaming |
| Apprentice review depth | First 20 consultations — transcript audited by supervisor | Quality floor; not forever-review |
| Graph recompute cadence | Nightly full + streaming delta for new edges | Balance cost + freshness |
| Open the matching engine | No — internal for P5; possibly open research API later | Competitive; privacy |
| Include chart-compatibility in matching | Yes as optional boost — user toggle | Some users want astrological fit; some don't |

## 5. Component Design

### 5.1 New modules

```
src/josi/marketplace/
├── referrals/
│   ├── workflow.py
│   ├── revenue_share.py
│   └── stripe_split.py
├── mentorship/
│   ├── supervisor_apprentice.py
│   └── review_gate.py
├── reputation/
│   ├── graph_builder.py
│   ├── pagerank_engine.py
│   ├── trust_seeds.py
│   └── anomaly_detector.py
├── matching/
│   ├── retriever.py              # hybrid inverted-index + semantic
│   ├── ranker.py                 # GBDT model + features
│   ├── explainer.py              # human-readable why
│   └── query_understanding.py    # NL → structured intent
└── antigaming/
    └── detectors.py
```

### 5.2 Data model additions

```sql
CREATE TABLE astrologer_referral (
    referral_id          UUID PRIMARY KEY,
    referrer_id          UUID NOT NULL REFERENCES user_account(user_id),
    referred_to_id       UUID NOT NULL REFERENCES user_account(user_id),
    client_user_id       UUID NOT NULL REFERENCES user_account(user_id),
    initiated_at         TIMESTAMPTZ NOT NULL,
    expires_at           TIMESTAMPTZ NOT NULL,             -- +30 days
    revenue_share_pct    NUMERIC(5,2) NOT NULL DEFAULT 15.00,
    consultation_id      UUID,                              -- filled when closed
    payout_cents         INTEGER,
    status               TEXT CHECK (status IN ('open','fulfilled','expired','declined'))
);

CREATE TABLE mentorship (
    mentorship_id        UUID PRIMARY KEY,
    supervisor_id        UUID NOT NULL REFERENCES user_account(user_id),
    apprentice_id        UUID NOT NULL REFERENCES user_account(user_id),
    started_at           TIMESTAMPTZ NOT NULL,
    ended_at             TIMESTAMPTZ,
    agreement_uri        TEXT,
    apprentice_reviews_remaining INTEGER NOT NULL DEFAULT 20,
    status               TEXT CHECK (status IN ('active','completed','terminated'))
);

CREATE TABLE reputation_edge (
    edge_id              UUID PRIMARY KEY,
    from_user_id         UUID NOT NULL,
    to_user_id           UUID NOT NULL,
    edge_type            TEXT CHECK (edge_type IN
                           ('referral','mentorship','endorsement','co_authored_reading')),
    weight               NUMERIC(6,4) NOT NULL,
    computed_at          TIMESTAMPTZ NOT NULL
);

CREATE TABLE reputation_score (
    user_id              UUID PRIMARY KEY REFERENCES user_account(user_id),
    pagerank_score       NUMERIC(10,6),
    trust_score          NUMERIC(10,6),
    computed_at          TIMESTAMPTZ NOT NULL,
    is_abused            BOOLEAN NOT NULL DEFAULT false,
    abuse_details        JSONB
);

CREATE TABLE specialization_tag (
    tag_id               TEXT PRIMARY KEY,           -- 'career','relationships','health','tamil','vedic',...
    display_name         TEXT,
    category             TEXT
);

CREATE TABLE astrologer_specialization (
    user_id              UUID,
    tag_id               TEXT REFERENCES specialization_tag(tag_id),
    self_rated           INTEGER CHECK (self_rated BETWEEN 1 AND 5),
    PRIMARY KEY(user_id, tag_id)
);

CREATE INDEX idx_referral_referrer_status ON astrologer_referral(referrer_id, status);
CREATE INDEX idx_reputation_edge_to ON reputation_edge(to_user_id, edge_type);
```

### 5.3 API contract

```
POST /api/v1/marketplace/referrals
Body: { "client_user_id": "...", "referred_to_id": "...", "context": "career KP specialist" }
Response: { referral_id, expires_at, share_link }

GET /api/v1/marketplace/match?q="Tamil speaking Vedic career help under $50/30min"
Response: {
  results: [
    { astrologer_id, rank, why: ["Tamil native","Gold cert","5 similar charts 4.8/5"] },
    ...
  ],
  query_interpretation: { languages:["ta"], traditions:["vedic"], topics:["career"], price_max:50 }
}

GET /api/v1/marketplace/astrologer/{id}/reputation
Response: { pagerank_score, cert_level, supervised_by, apprentices_count,
            referrals_received_90d, referrals_given_90d }
```

## 6. User Stories

### US-D4.1: As astrologer-A I can refer a client to astrologer-B with revenue-share
**Acceptance:** one-tap referral creates row; client receives notification; if client books with B within 30 days, 15% to A on closed consultation; Stripe split payout on settlement.

### US-D4.2: As a senior astrologer I can formally supervise apprentices
**Acceptance:** eligibility checks pass; apprentice consents; mentorship row created; apprentice profile shows "trained under X"; supervisor reviews apprentice's first 20 consultations.

### US-D4.3: As a user I can describe my need in natural language and get ranked matches with reasons
**Acceptance:** NL query interpreted (structured output); top-10 ranked; each has "why" explanation; p95 < 500ms.

### US-D4.4: As a user I understand why astrologer X ranked above Y
**Acceptance:** explanation cites matching signals; user can click "show me more about X's reputation" → reputation detail page.

### US-D4.5: As the platform we prevent referral rings from gaming the graph
**Acceptance:** synthetic ring of 10 astrologers referring among themselves with no real consultations triggers anomaly detector; abuse flag set; reputation score frozen; manual review queue.

### US-D4.6: As an apprentice I can only take paid bookings after supervisor approval
**Acceptance:** during review window, bookings gated by supervisor approve; supervisor sees queue; SLA 48h.

### US-D4.7: As astrologer I can see my graph score, inputs, and how to improve
**Acceptance:** dashboard shows score, top contributing edges, suggested actions (e.g., "get cert to Gold for +0.15").

## 7. Tasks

### T-D4.1: Referral workflow + Stripe split payouts
- **Definition:** Data model, referral-creation API, notification, attribution tracker, Stripe Connect split on consultation close.
- **Acceptance:** E2E test: referral → booking → consultation → payout split correctly; accounting reconciles.
- **Effort:** 3 weeks

### T-D4.2: Mentorship + review-gate
- **Definition:** Eligibility checks, consent flow, mentorship row, apprentice-review queue, supervisor dashboard.
- **Acceptance:** eligibility rules enforced; apprentice review queue populated and clearable.
- **Effort:** 2 weeks

### T-D4.3: Reputation graph builder + PageRank engine
- **Definition:** Nightly batch builds graph from edges; Personalized PageRank; TrustRank seeds; delta update path.
- **Acceptance:** deterministic reruns; 100k-node graph computes in < 10 min; scores written to reputation_score.
- **Effort:** 3 weeks

### T-D4.4: Specialization tag taxonomy + migration
- **Definition:** Tag catalog; astrologer self-rating UI; seed top-200 tags.
- **Acceptance:** 200 tags seeded; astrologer onboarding prompts for 5+ tags; search indexable.
- **Effort:** 1.5 weeks

### T-D4.5: Matching engine (retriever + ranker)
- **Definition:** Hybrid inverted-index (Postgres FTS or Elasticsearch) + semantic embeddings; GBDT ranker trained on historical bookings + consultation outcomes.
- **Acceptance:** offline eval NDCG@10 ≥ 0.75 vs random baseline; online A/B uplift target ≥ +8% booking rate.
- **Effort:** 4 weeks

### T-D4.6: Explainer + NL query understanding
- **Definition:** LLM-based query parsing to structured intent; explanation generator.
- **Acceptance:** 95% correct parse on 500-query eval set; explanations rated clear by 4/5 reviewers.
- **Effort:** 2 weeks

### T-D4.7: Anti-gaming detectors
- **Definition:** Graph anomaly detection (reciprocity, cluster coefficient), device/identity dedup, revenue-attribution gate.
- **Acceptance:** red-team simulation of 3 attack types; ≥ 90% caught within 1 review cycle.
- **Effort:** 2 weeks

### T-D4.8: Astrologer reputation dashboard
- **Definition:** Graph score, edge contributors, improvement suggestions, referrals in/out.
- **Acceptance:** E12 workbench integration; astrologer qualitative feedback positive in preview.
- **Effort:** 1.5 weeks

## 8. Unit Tests

### 8.1 Referral lifecycle & accounting
- Category: creation, attribution window, fulfillment, expiration, decline, payout split.
- Target: zero accounting discrepancies in 10k simulated flows.
- Representative: `test_referral_30day_window_enforced`, `test_stripe_split_on_close`, `test_expired_referral_no_payout`.

### 8.2 Mentorship eligibility
- Category: eligibility rules, supervisor-approval gating.
- Target: 100% correct gating on edge cases.
- Representative: `test_eligibility_below_500_consultations_rejected`, `test_apprentice_booking_requires_supervisor_approval`, `test_review_counter_decrement`.

### 8.3 Graph engine
- Category: correctness, determinism, delta semantics, performance.
- Target: deterministic output; 100k nodes in < 10 min; delta produces same result as full rerun.
- Representative: `test_pagerank_deterministic_seed`, `test_trustrank_penalizes_sinks`, `test_delta_matches_full`.

### 8.4 Matching quality
- Category: retrieval recall, ranking relevance.
- Target: NDCG@10 ≥ 0.75 on holdout; recall@50 ≥ 0.95.
- Representative: `test_ndcg_10_on_holdout`, `test_multilingual_query_recall`, `test_specialization_filter_precision`.

### 8.5 Query understanding
- Category: NL → structured intent.
- Target: ≥ 95% correct parse on eval set.
- Representative: `test_parse_tamil_career_under_50`, `test_parse_hindi_relationships_gold_cert`, `test_parse_ambiguous_query_asks_clarification`.

### 8.6 Anti-gaming detection
- Category: simulated attack scenarios.
- Target: ≥ 90% caught within 1 review cycle; false positive rate < 2%.
- Representative: `test_detect_referral_ring_10_nodes`, `test_detect_fake_apprentice`, `test_low_fp_rate_on_legitimate_edges`.

### 8.7 Explainer quality
- Category: human-readable "why" output.
- Target: 4/5 rater clarity.
- Representative: `test_explainer_cites_language_match`, `test_explainer_cites_chart_similarity`.

## 9. EPIC-Level Acceptance Criteria

- [ ] Referral workflow end-to-end with correct Stripe split
- [ ] Mentorship formalized with review gate
- [ ] Reputation graph computed nightly; scores queryable
- [ ] Matching engine uplifts booking rate ≥ 8% in A/B vs current directory
- [ ] Anti-gaming red-team pass ≥ 90%
- [ ] Astrologer reputation dashboard in E12 workbench
- [ ] Documentation + API reference published

## 10. Rollout Plan

- **Feature flags:** `marketplace_referrals`, `marketplace_mentorship`, `marketplace_matcher_v2`, `reputation_graph_scoring`.
- **Phase 1 (3 weeks):** mentorship only to 100 senior astrologers; observe; no financial flows.
- **Phase 2 (4 weeks):** referrals to all astrologers Gold+ cert; Stripe split validated via a week of shadow accounting.
- **Phase 3 (4 weeks):** matching v2 A/B at 10% traffic; gate = +8% booking uplift, no NPS regression.
- **Phase 4 (2 weeks):** reputation graph + ranking boost turned on in matcher; A/B.
- **Phase 5:** GA at 100%.
- **Rollback:** flag off; matching reverts to v1; financial flows use fallback direct-payout path.

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Gaming destroys trust in graph scoring | Medium | Very High | Multi-layered anti-gaming; frequent audits; public abuse disclosures |
| Astrologers perceive mentorship as favoritism | Medium | Medium | Transparent eligibility rules; open application |
| Stripe split errors lead to financial disputes | Low | High | Shadow accounting; reconciliation job; escrow-like hold |
| Matching engine introduces bias (gender, language) | Medium | High | Fairness audits; bias metrics in eval; fallback to balanced ranking |
| Ranker overfits to historical bookings (feedback loop) | Medium | Medium | Exploration bonus; periodic retraining on fresh data |
| Referral abuse (fake clients) | Medium | High | Real consultation completion required for payout |
| Cross-border tax on revenue share | Medium | Medium | Stripe Connect handles reporting; legal review per jurisdiction |

## 12. References

- Master spec: `docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`
- Related PRDs: E12 (Workbench), D3 (localization for matching), D8 (certification), D9 (enterprise tier)
- Algorithms: Personalized PageRank (Jeh & Widom 2003); TrustRank (Gyongyi et al 2004)
- Stripe Connect: separate payouts + platform fee docs
