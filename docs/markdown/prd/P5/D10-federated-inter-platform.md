---
prd_id: D10
epic_id: D10
title: "Federated inter-platform agreement — cross-platform consensus on classical techniques"
phase: P5-dominance
tags: [#experimentation, #extensibility, #correctness]
priority: could
depends_on: [D7, F1, F4, F8, F13]
enables: [I2, I9]
classical_sources: [bphs, saravali, phaladeepika, jaimini_sutras]
estimated_effort: 10-14 weeks
status: draft
author: "@agent"
last_updated: 2026-04-19
---

# D10 — Federated Inter-Platform Agreement

## 1. Purpose & Rationale

Classical astrology has no authority. Every platform (AstroSage, Cafe Astrology, Drik Panchang, Kundli.com, Jagannatha Hora, Maitreya) implements the same techniques with silent divergences. A user who asks "is Gaja Kesari active on my chart?" can get "yes" on one and "no" on another, with no insight into why.

Josi's architecture (F1 source_authority, F8 aggregation, F13 provenance) already treats this as a first-class problem *within* Josi. D10 extends that lens **across** platforms via federated agreements.

Value:
1. **Empirical literature for the category** — "Platforms X and Y agree 93% on Gaja Kesari; disagree 22% on Parivartana Yoga. Disagreements cluster where birth-time accuracy is low." This has never been measured.
2. **Standards-body positioning** — Josi as the arbiter of cross-platform consensus. Reputation moat.
3. **Debugging partner value** — partnering platforms fix bugs once publicly measured.
4. **Research acceleration** — feeds D7 research API with multi-platform ground truth.

Partners: initially 2-3 friendly counterparts (targeted: JH, Maitreya, a commercial site). Not dependent on wide adoption.

## 2. Scope

### 2.1 In scope
- **Federation protocol spec** — standardized JSON request/response for classical techniques across platforms
- **Reference client** — Josi-published open-source client libraries in Python, JS
- **Agreement signing framework** — partner platforms sign a multi-platform agreement governing data use and publication
- **Comparison engine** — scheduled jobs that run the same chart through N platforms and diff outputs
- **Public agreement dashboard** — per-technique agreement statistics, public view
- **Private partner dashboard** — per-chart diff drill-downs for debugging (auth-gated)
- **Version-aware comparison** — each platform's output tagged with its rule version
- **Disagreement taxonomy** — systematic codes for "ayanamsa difference", "house system", "rule variant", "software bug", "ambiguous classical source"
- **Opt-in for users** — charts used in federation come only from research-opted-in user pool (D5/D6 style)

### 2.2 Out of scope
- Forcing partners to adopt Josi's schema (we normalize in our translation layer)
- Authoritative rulings on "correct" output (we report agreement, not truth)
- Commercial licensing of the protocol (open spec)
- Real-time query delegation (batch comparison only in P5)

### 2.3 Dependencies
- D7 research API as dataset companion
- F1 source_authority for partner-specific `source_id` rows
- F13 provenance for version-tagging
- F8 aggregation — agreement % = a special kind of aggregation signal

## 3. Technical Research

### 3.1 Federation protocol

Minimum viable envelope:

```json
{
  "protocol_version": "1.0",
  "platform_id": "astrosage_v7",
  "chart_input": {
    "birth_utc": "1984-06-15T13:30:00Z",
    "latitude": 13.0827,
    "longitude": 80.2707,
    "ayanamsa_hint": "lahiri",
    "house_system_hint": "whole_sign"
  },
  "requested_techniques": [
    {"family": "yoga", "rule_ids": ["gaja_kesari","ruchaka","bhadra"]},
    {"family": "dasa", "system": "vimshottari", "depth": 3}
  ],
  "caller_signature": "..."
}
```

Response normalized to Josi's output shapes (F7). Partners either natively support or run a shim translator.

### 3.2 Comparison engine

Batch job runs a rotating sample of charts through all partners, diffs outputs, classifies disagreements, updates agreement metrics. Runs on ClickHouse (via S4).

### 3.3 Disagreement taxonomy

Every diff classified into a code:
- `AYANAMSA` — different ayanamsa assumption
- `HOUSE_SYSTEM` — different house system
- `RULE_VARIANT` — legitimately different source authority
- `ROUNDING` — floating-point / minor numeric
- `SOFTWARE_BUG` — one platform is demonstrably wrong per its own docs
- `CLASSICAL_AMBIGUITY` — classical source doesn't resolve
- `VERSION_MISMATCH` — platforms on different versions

Taxonomy is expandable via YAML.

### 3.4 Participation incentives

- Partners get private debug dashboards for their own platform's diffs vs consensus
- Joint publications via I2 Research Press
- Marketing: "Certified by Federation v1.0" badge (nothing prevents non-partners from citing Josi findings, but partners get co-attribution)

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| Open spec vs proprietary | Open (Apache 2 / CC-BY for spec) | Adoption > control |
| Data-sharing direction | Bidirectional with research opt-in upstream data | Fairness + transparency |
| Who arbitrates disagreements | No arbitration; we publish disagreements, not rulings | Standards-body posture ≠ referee |
| What happens if a partner doesn't renew | Published data stays; future comparisons excluded | Partners can pull out cleanly |
| Publish without partner | Aggregate statistics yes; per-platform names require consent | Legal + ethics |
| Real-time vs batch | Batch in P5 | Cost + complexity |

## 5. Component Design

### 5.1 New modules

```
src/josi/federation/
├── protocol/
│   ├── schema.py                 # Pydantic / JSON Schema for protocol v1
│   └── translators/
│       ├── astrosage_shim.py     # bridge to external partners
│       ├── jh_shim.py
│       └── maitreya_shim.py
├── comparison/
│   ├── batch_runner.py
│   ├── normalizer.py             # unifies outputs to F7 shapes
│   ├── diff_engine.py
│   └── disagreement_classifier.py
├── dashboard/
│   ├── public_agreement.py
│   └── private_debug.py
├── agreements/
│   ├── partner_registry.py
│   └── signing_ceremony.py       # legal flow
└── api/
    └── controller.py

src/josi/content/federation_taxonomy.yaml
```

### 5.2 Data model additions

```sql
CREATE TABLE federation_partner (
    partner_id           TEXT PRIMARY KEY,
    display_name         TEXT NOT NULL,
    homepage             TEXT,
    agreement_uri        TEXT,
    protocol_version     TEXT,
    signed_at            TIMESTAMPTZ,
    revoked_at           TIMESTAMPTZ
);

CREATE TABLE federation_comparison_run (
    run_id               UUID PRIMARY KEY,
    chart_fingerprint    TEXT NOT NULL,             -- hashed chart input
    run_at               TIMESTAMPTZ NOT NULL,
    technique_family_id  TEXT NOT NULL
);

CREATE TABLE federation_platform_output (
    run_id               UUID REFERENCES federation_comparison_run(run_id),
    partner_id           TEXT REFERENCES federation_partner(partner_id),
    rule_id              TEXT NOT NULL,
    output_normalized    JSONB NOT NULL,
    output_raw           JSONB,
    platform_version     TEXT,
    PRIMARY KEY(run_id, partner_id, rule_id)
);

CREATE TABLE federation_disagreement (
    disagreement_id      UUID PRIMARY KEY,
    run_id               UUID REFERENCES federation_comparison_run(run_id),
    rule_id              TEXT NOT NULL,
    partners             TEXT[] NOT NULL,
    taxonomy_code        TEXT NOT NULL,
    details              JSONB
);

CREATE TABLE federation_agreement_stat (
    rule_id              TEXT NOT NULL,
    window_start         DATE NOT NULL,
    window_end           DATE NOT NULL,
    n_comparisons        INTEGER NOT NULL,
    agreement_pct        NUMERIC(5,4) NOT NULL,
    top_disagreement_codes JSONB,
    PRIMARY KEY(rule_id, window_start, window_end)
);
```

### 5.3 API contract

```
# Public
GET /api/v1/federation/agreement/{rule_id}?since=2026-01-01
Response: { agreement_pct, n_comparisons, top_disagreement_codes, partners_included }

GET /api/v1/federation/protocol-spec
Response: JSON Schema + markdown docs

# Partner (auth-gated)
GET /api/v1/federation/partner/me/diffs?since=...
POST /api/v1/federation/partner/me/submit-output  (partner pushes their output)
```

## 6. User Stories

### US-D10.1: As a classical scholar, I can see agreement % for Gaja Kesari across platforms over time
**Acceptance:** public dashboard per-rule agreement; N of comparisons; top disagreement codes; citation-ready.

### US-D10.2: As a partner platform engineer, I see where my output diverges from consensus
**Acceptance:** private dashboard lists diffs with taxonomy codes; I can drill into a specific chart.

### US-D10.3: As Josi, I run batch comparisons nightly on 10k research-opted charts
**Acceptance:** batch completes < 6h; all disagreements classified; stats updated.

### US-D10.4: As a new partner, I sign the agreement and get onboarded in 2 weeks
**Acceptance:** legal signing flow; shim translator; first comparison within 2 weeks.

### US-D10.5: As a researcher (D7), I can pull federation data via research API
**Acceptance:** `federation.*` research marts available; DP-wrapped.

### US-D10.6: As a disagreement reviewer, I classify ambiguous cases into taxonomy
**Acceptance:** reviewer queue; new taxonomy codes added via YAML PR.

## 7. Tasks

### T-D10.1: Protocol spec + schema
- **Definition:** JSON Schema + markdown docs; reference client libraries.
- **Acceptance:** public spec; sample implementations in Python + JS.
- **Effort:** 2 weeks

### T-D10.2: Partner translators (3 initial)
- **Definition:** Shims for JH, Maitreya, and 1 commercial partner.
- **Acceptance:** round-trip test: same chart → same normalized output via each shim.
- **Effort:** 4 weeks

### T-D10.3: Comparison engine + batch runner
- **Definition:** Scheduled jobs; chart sampling from research-opted pool; diff engine.
- **Acceptance:** nightly run of 10k charts; under 6h; observability dashboards.
- **Effort:** 3 weeks

### T-D10.4: Disagreement classifier + taxonomy
- **Definition:** Rule-based + LLM-assisted classifier; taxonomy YAML.
- **Acceptance:** classifier accuracy ≥ 85% on labeled sample.
- **Effort:** 2 weeks

### T-D10.5: Public + partner dashboards
- **Definition:** Agreement dashboard (public); partner debug dashboard (auth-gated).
- **Acceptance:** design review; published externally.
- **Effort:** 2 weeks

### T-D10.6: Partner agreement signing flow
- **Definition:** Legal-reviewed contract; signing flow; onboarding checklist.
- **Acceptance:** 3 partners signed pre-GA.
- **Effort:** 2 weeks (legal-heavy)

### T-D10.7: D7 research mart for federation
- **Definition:** `federation.*` rows exported into research ClickHouse with DP wrapping.
- **Acceptance:** sample queries return DP-wrapped stats.
- **Effort:** 1 week

## 8. Unit Tests

### 8.1 Protocol schema conformance
- Category: request/response validates against JSON Schema.
- Target: 100% valid examples pass; 100% invalid examples rejected.
- Representative: `test_request_schema_valid`, `test_missing_required_field_rejected`, `test_unknown_technique_family_rejected`.

### 8.2 Normalization across shims
- Category: same input across shims yields comparable normalized output.
- Target: zero spurious "RULE_VARIANT" codes due to normalization bugs.
- Representative: `test_yoga_normalized_across_shims`, `test_dasa_period_boundaries_aligned`.

### 8.3 Diff engine
- Category: produces correct diffs on known cases.
- Target: deterministic; idempotent.
- Representative: `test_diff_identical_no_disagreement`, `test_diff_boolean_mismatch`, `test_diff_temporal_range_overlap`.

### 8.4 Taxonomy classifier
- Category: accuracy vs. labeled set.
- Target: ≥ 85%.
- Representative: `test_classifier_ayanamsa`, `test_classifier_classical_ambiguity`, `test_classifier_escalates_unknown`.

### 8.5 Partner auth
- Category: partner-specific auth, rate limits.
- Target: zero cross-partner data leakage.
- Representative: `test_partner_cannot_see_other_partner_diffs`, `test_revoked_partner_access_denied`.

### 8.6 Opt-in enforcement
- Category: only research-opted charts enter federation pool.
- Target: 100% enforcement.
- Representative: `test_nonopted_chart_skipped`, `test_opt_out_removes_from_future_runs`.

### 8.7 Public dashboard correctness
- Category: agreement % matches underlying data.
- Target: exact match to underlying aggregates.
- Representative: `test_dashboard_numbers_match_store`.

## 9. EPIC-Level Acceptance Criteria

- [ ] Protocol v1.0 published + open spec
- [ ] 3 partners signed and running comparisons
- [ ] Batch runner producing nightly stats on ≥ 10k research-opted charts
- [ ] Disagreement classifier ≥ 85% accuracy
- [ ] Public agreement dashboard live for ≥ 50 rules
- [ ] Private partner debug dashboards live
- [ ] First co-authored publication draft with a partner

## 10. Rollout Plan

- **Feature flag:** `federation_enabled`.
- **Phase 1 (6 weeks):** protocol spec + 1 partner (e.g., Maitreya) internal shadow.
- **Phase 2 (4 weeks):** second + third partners; public dashboard preview.
- **Phase 3 (2 weeks):** public launch + press.
- **Phase 4:** ongoing partner acquisition; I2 Research Press ties in.
- **Rollback:** flag off; data archived; partner agreements preserved.

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Partners unwilling to sign | High | Medium | Start with open-source reference impls (JH, Maitreya); strong value prop |
| Public "disagreement" framing offends partners | Medium | Medium | Frame as transparency + collaboration; per-partner names optional |
| Classifier misclassifies bugs vs variants | Medium | Medium | Reviewer queue + escalation; conservative defaults |
| Spec becomes fragmented | Medium | Medium | Versioning discipline; backwards-compat commitments |
| Competitive partners weaponize our data | Medium | Medium | Co-publication terms; legal review of usage |
| Opt-in pool too small for significance | Medium | Medium | Expand research opt-in UX; incentives |
| Cost of running N-platform batches | Low | Medium | Sample strategy; cache; shared infra with D7 |

## 12. References

- Master spec: `docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`
- Related PRDs: D7 (research), F1 (sources), F13 (provenance), I2 (research press), I9 (regulatory)
- Precedents: FIDO alliance model; W3C cross-vendor interop; schema.org
