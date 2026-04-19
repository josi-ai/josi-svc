---
prd_id: D7
epic_id: D7
title: "Research data API (anonymized, opt-in, differential-privacy-wrapped)"
phase: P5-dominance
tags: [#experimentation, #multi-tenant]
priority: should
depends_on: [D5, D6, S4, F13]
enables: [I2, D10]
classical_sources: []
estimated_effort: 8-12 weeks
status: draft
author: "@agent"
last_updated: 2026-04-19
---

# D7 — Research Data API

## 1. Purpose & Rationale

Astrology research is stuck in the 1970s (Gauquelin Mars effect, dismissed skeptical follow-ups). It's stuck because no one has large-N, high-resolution, longitudinally-tracked data. Josi does. At 100M+ users, millions opted into research, and longitudinal outcomes captured via D6, Josi can become the **empirical backbone** of astrology research.

Academic value: PhD students, cognitive-science researchers, statisticians, anthropologists get first-time access to aggregated astrology data.

Strategic value:
1. **Category-creator positioning** — "Josi is where astrology becomes measurable" — legitimacy among serious thinkers
2. **Feeds I2 (Research Press)** — peer-reviewed publications
3. **Feeds D10 (federated inter-platform)** — we become the standards body by owning the largest dataset
4. **Countermoat vs skeptics** — we own the data that would vindicate or falsify specific claims

Never individual charts. Always aggregates. Differential privacy end-to-end.

## 2. Scope

### 2.1 In scope
- Research API with query DSL for aggregated statistics
- Four query classes:
  1. **Prevalence** — "% of charts with Gaja Kesari yoga activation" (stratify by decade, geography, gender — all opt-in stratifications)
  2. **Co-occurrence** — "co-activation rate of Gaja Kesari + Ruchaka yoga"
  3. **Outcome-correlation** (uses D6 data) — "Saturn transit to Moon → user-reported life-event rate"
  4. **Longitudinal-event** — "average mood delta during Saturn ingress transitions"
- Differential-privacy wrapping with budget accounting per researcher
- Minimum cell size enforcement (no cell < 20; otherwise suppress)
- IRB-compliant consent flow; reaffirmed annually
- Application / vetting process for API access; academic affiliation required; agreement on non-reidentification
- Query auditability and rate limiting
- Aggregate downloads (CSV) for approved researchers

### 2.2 Out of scope
- Raw chart data or individual-level anything
- Re-identification support of any kind
- Named-user queries
- Writable API (researchers cannot modify data)
- Real-time streaming
- Commercial use of derived research without separate license

### 2.3 Dependencies
- D5 biometric (for body-signal research questions)
- D6 longitudinal (for outcome-correlation research)
- S4 OLAP replication (ClickHouse-backed analytics; raw OLTP never touched by this API)
- F13 provenance so researchers can filter by rule version

## 3. Technical Research

### 3.1 Differential privacy approach

Event-level DP at query time:
- Each query has a DP budget (epsilon per query; user lifetime budget)
- Laplace noise added proportional to sensitivity of the aggregate function
- For counts: sensitivity = 1 (one user's contribution)
- For means/proportions: sensitivity based on bounded value range
- Composition theorem tracks total budget usage per researcher

Target: epsilon ≤ 1 per released aggregate; total budget 10 per researcher per project.

### 3.2 Minimum cell size and k-anonymity

- Aggregates with n < 20 suppressed
- Intersections (stratifications) check k-anonymity: each stratum must have ≥ 20 contributors
- Nested queries don't bypass: sibling queries that together reconstruct a small cell are rate-limited

### 3.3 Analytics substrate

Query engine sits on ClickHouse (via S4 replication). OLTP stays untouched. Researcher credentials never touch OLTP.

Schema:
- `research.chart_facts` — derived, anonymized, opt-in-only rows (user_id hashed with rotating salt; no way back)
- `research.activation_facts` — yoga / dasa / transit activations
- `research.outcome_facts` — D6 outcomes (de-identified)
- `research.biometric_aggregates` — D5 daily rollups (de-identified)

### 3.4 Researcher application gate

Manual review by a small Josi Research Ethics committee (Josi Research Press, I2, will eventually take this over):
- Academic affiliation verified
- Research proposal reviewed
- Non-reidentification agreement signed
- Conflict-of-interest disclosure
- Annual renewal

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| Allow commercial researchers | Case-by-case, separate license | Commercial use has different incentive alignment |
| Allow journalists | Aggregate-view in a dedicated press tier; no API | Prevents misuse narratives |
| Publish DP budget usage publicly | Per-project yes (transparency); per-researcher no | Privacy of researchers |
| Allow downloading aggregates to local | Yes for approved researchers; watermarked | Accountability |
| Real-time vs daily refresh | Daily refresh of research marts | Cost + DP budget simplicity |
| Support for custom stratification | Yes with k-anonymity check | Research value; safety preserved |

## 5. Component Design

### 5.1 New modules

```
src/josi/research/
├── schema/
│   ├── chart_facts.sql
│   ├── activation_facts.sql
│   ├── outcome_facts.sql
│   └── biometric_aggregates.sql
├── ingest/
│   └── research_etl.py           # from OLTP (via S4) → ClickHouse mart
├── dp/
│   ├── budget_tracker.py
│   ├── laplace.py
│   └── composition.py
├── query/
│   ├── dsl.py                     # query language parser
│   ├── planner.py
│   ├── safety_check.py            # k-anon + cell size + budget
│   └── executor.py                # ClickHouse dispatch
├── auth/
│   ├── researcher_account.py
│   ├── application.py
│   └── agreement_signing.py
└── audit/
    └── logger.py

src/josi/api/v1/research_controller.py
```

### 5.2 Data model additions

```sql
CREATE TABLE research.researcher (
    researcher_id        UUID PRIMARY KEY,
    email                TEXT NOT NULL,
    affiliation          TEXT NOT NULL,
    agreement_uri        TEXT NOT NULL,
    dp_budget_total      NUMERIC(8,4) NOT NULL DEFAULT 10.0,
    dp_budget_used       NUMERIC(8,4) NOT NULL DEFAULT 0.0,
    approved_at          TIMESTAMPTZ,
    approved_by          UUID,
    renewal_due          DATE,
    revoked_at           TIMESTAMPTZ
);

CREATE TABLE research.query_log (
    query_id             UUID PRIMARY KEY,
    researcher_id        UUID NOT NULL REFERENCES research.researcher(researcher_id),
    query_text           TEXT NOT NULL,
    epsilon_spent        NUMERIC(8,4) NOT NULL,
    result_cells_returned INTEGER,
    result_cells_suppressed INTEGER,
    executed_at          TIMESTAMPTZ NOT NULL,
    latency_ms           INTEGER,
    status               TEXT CHECK (status IN ('ok','denied_budget','denied_k_anon','error'))
);

-- ClickHouse marts (research.* schema) populated by ETL
```

### 5.3 API contract

```
POST /api/v1/research/query
Auth: researcher token (separate auth domain from B2C/B2B)
Body:
{
  "query_class": "prevalence",
  "expression": "activation_rate(yoga='gaja_kesari')",
  "stratify": ["birth_decade","tradition_preference"],
  "filters": { "source_id": "bphs", "rule_version": "*" },
  "epsilon": 0.5
}
Response:
{
  "query_id": "...",
  "rows": [
    { "birth_decade": "1980s", "tradition_preference": "parashari",
      "value_noised": 0.182, "n_contributors_approx": 45678 }
  ],
  "suppressed_cells": 3,
  "epsilon_spent": 0.5,
  "budget_remaining": 7.2,
  "caveats": ["Laplace noise added; expect ±0.01 at this epsilon"]
}
```

## 6. User Stories

### US-D7.1: As a PhD student, I apply for API access and receive approval within 2 weeks
**Acceptance:** application portal; committee dashboard; standard SLA; rejection comes with reasons.

### US-D7.2: As an approved researcher, I run a prevalence query and get DP-wrapped results
**Acceptance:** query returns rows with noised values; cells < 20 suppressed; budget debited.

### US-D7.3: As a researcher, I run a co-occurrence matrix of 60 yogas
**Acceptance:** handles 60×60 query; DP budget proportional to distinct outputs; suppression honored.

### US-D7.4: As an ethics reviewer, I audit a researcher's queries
**Acceptance:** query log searchable; pattern-detection alerts on small-cell-reconstruction attempts.

### US-D7.5: As a user, I see my research opt-in status and can revoke
**Acceptance:** settings panel; revoke removes from future research aggregates within 24h.

### US-D7.6: As Josi Research Press (I2), I can export an approved-for-publication dataset
**Acceptance:** export endpoint gated on reviewer approval; watermarked CSV; matches published paper.

## 7. Tasks

### T-D7.1: ClickHouse research marts + ETL
- **Definition:** Pipeline from OLTP → ClickHouse research.* tables; salted hashing; opt-in filter.
- **Acceptance:** nightly refresh; reconciliation matches OLTP counts modulo opt-in.
- **Effort:** 3 weeks

### T-D7.2: DP library + composition
- **Definition:** Laplace noise addition; budget accounting; advanced composition theorem.
- **Acceptance:** matches published DP references; unit tests vs closed-form.
- **Effort:** 2 weeks

### T-D7.3: Query DSL + planner + safety check
- **Definition:** Parser; plan → ClickHouse SQL; k-anon + cell-size enforcement.
- **Acceptance:** 50 synthetic query tests; invalid queries rejected with clear errors.
- **Effort:** 3 weeks

### T-D7.4: Researcher application + ethics committee tooling
- **Definition:** Application form; reviewer queue; agreement signing; renewal flow.
- **Acceptance:** end-to-end flow; 2-week SLA tracked.
- **Effort:** 2 weeks

### T-D7.5: Researcher auth + separate API
- **Definition:** Separate auth domain; distinct rate limits; mTLS optional.
- **Acceptance:** no overlap with B2C/B2B auth; isolated logs.
- **Effort:** 1.5 weeks

### T-D7.6: Audit + anomaly detection
- **Definition:** Query log; pattern detection for small-cell reconstruction; reviewer alerts.
- **Acceptance:** red-team attacks detected within 24h.
- **Effort:** 1.5 weeks

### T-D7.7: Export + watermarking
- **Definition:** CSV export with researcher-id watermark; approval gate for export.
- **Acceptance:** watermark verifiable; unapproved queries can't export.
- **Effort:** 1 week

## 8. Unit Tests

### 8.1 DP correctness
- Category: noise distribution, composition, budget accounting.
- Target: matches textbook formulas; budget never exceeded.
- Representative: `test_laplace_noise_matches_epsilon`, `test_advanced_composition_bound`, `test_budget_exceeded_denies_query`.

### 8.2 k-anonymity + cell-size
- Category: cells < 20 suppressed; nested-query collapse blocked.
- Target: 100% enforcement.
- Representative: `test_cell_below_20_suppressed`, `test_stratification_with_small_stratum_suppressed`, `test_sibling_queries_cant_reconstruct`.

### 8.3 Query DSL
- Category: parsing, planning, error messages.
- Target: valid queries run; invalid give clear errors.
- Representative: `test_parse_prevalence_query`, `test_parse_cooccurrence_query`, `test_invalid_filter_rejected`.

### 8.4 Opt-in compliance
- Category: only opted-in rows ever reach research marts.
- Target: 100% compliance; revocation propagates within 24h.
- Representative: `test_opt_out_user_removed_from_mart`, `test_opt_in_new_user_included_next_refresh`.

### 8.5 Authentication + rate limiting
- Category: researcher-only endpoints; rate limits enforced.
- Target: zero leaks; 100% enforcement.
- Representative: `test_b2c_token_rejected`, `test_rate_limit_triggered`.

### 8.6 Audit
- Category: query log captures everything; anomaly detection flags attacks.
- Target: zero untracked queries; ≥ 90% detection of synthetic reconstruction attacks.
- Representative: `test_every_query_logged`, `test_detect_reconstruction_pattern`.

### 8.7 Export watermarking
- Category: watermark embedded and verifiable.
- Target: embedded in CSV; verifiable offline.
- Representative: `test_watermark_embedded`, `test_watermark_verification_tool`.

## 9. EPIC-Level Acceptance Criteria

- [ ] Research marts refreshed daily with opt-in filter
- [ ] DP budget tracking verified against published composition theorems
- [ ] k-anonymity enforced; red-team reconstruction blocked
- [ ] Researcher application + approval flow live
- [ ] At least 3 pilot researchers approved and running queries pre-GA
- [ ] Audit log + anomaly detection functional
- [ ] Documentation: query DSL reference + ethics policy public

## 10. Rollout Plan

- **Feature flag:** `research_api_enabled`.
- **Phase 1 (4 weeks):** internal — Josi researchers only; test DP math + marts.
- **Phase 2 (6 weeks):** closed pilot: 5-10 invited academics; gate = no reconstruction incidents, ethics committee sign-off, query SLA < 5s p95.
- **Phase 3:** GA via application portal; launch with I2 (Research Press) announcement.
- **Rollback:** flag off denies all queries; marts remain but unreachable.

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Re-identification attack | Low | Catastrophic | DP + k-anon + audit + legal agreement + anomaly detection |
| Researcher misuses data commercially | Medium | High | Agreement + periodic audits + revocation mechanism |
| Over-claimed statistical findings based on biased opt-in | High | Medium | Publish opt-in composition; ask researchers to disclose |
| DP budget exhaustion frustrates researchers | Medium | Medium | Transparent budget UI; renewal process |
| Cost of ClickHouse at scale | Medium | Medium | Aggregated marts; cold storage for archives |
| IRB/ethics body demands exceed internal committee | Medium | Medium | Partner with academic IRB for external validation |
| Negative findings used to attack Josi | Medium | Medium | Principle: we publish negative findings equally; credibility > optics |

## 12. References

- Master spec: `docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`
- Related PRDs: D5 (biometric), D6 (longitudinal), S4 (ClickHouse), I2 (Research Press), D10 (federated)
- Privacy: Dwork & Roth *Algorithmic Foundations of Differential Privacy*; composition theorem; k-anonymity literature
- Precedents: OpenSAFELY (NHS), LinkedIn Economic Graph, US Census DP
