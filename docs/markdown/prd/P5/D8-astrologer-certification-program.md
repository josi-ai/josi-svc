---
prd_id: D8
epic_id: D8
title: "Astrologer certification program ('Josi Certified' — Bronze/Silver/Gold/Platinum)"
phase: P5-dominance
tags: [#astrologer-ux, #correctness]
priority: should
depends_on: [F16, D4, D6, E12]
enables: [D4, D9, I9]
classical_sources: [bphs, saravali, jaimini_sutras, kp_reader]
estimated_effort: 10-14 weeks
status: draft
author: "@agent"
last_updated: 2026-04-19
---

# D8 — Astrologer Certification Program ("Josi Certified")

## 1. Purpose & Rationale

Marketplace quality is the marketplace. Without a credible competence signal, bad astrologers crowd out good ones, client NPS degrades, and the flywheel stalls. Reviews alone are gameable and noisy. D8 creates an objective, rubric-based, annually-renewed competence signal: **Josi Certified Bronze / Silver / Gold / Platinum.**

Three axes of certification:
1. **Blind-reading accuracy** — astrologer is shown a chart-shaped problem from a curated golden set; reading is scored against known expected outputs (leveraging F16 golden chart infrastructure).
2. **Peer review scores** — other certified astrologers anonymously review the candidate's sample readings.
3. **Client rating aggregate** — per-client ratings over time.

Required for premium marketplace placement. Annual recertification keeps it current. Creates the only credible competence signal in consumer astrology.

## 2. Scope

### 2.1 In scope
- Rubric + scoring model across 3 axes
- Certification levels: Bronze (entry), Silver, Gold, Platinum (top tier)
- Blind-reading assessment: 10 golden charts per session; astrologer produces readings; structured scoring
- Peer-review workflow: Gold+ peers review junior candidates' sample readings (anonymized); minimum 3 reviewers per candidate
- Client-rating aggregate computation from completed consultations
- Annual recertification workflow (reminder, re-assessment of blind + peer)
- Public "Josi Certified" badge + profile surfacing
- Revocation workflow for verified misconduct
- Tradition-specific tracks: cert per tradition (Vedic, KP, Western, Tajaka, …) — an astrologer may be Gold in Vedic but uncertified in Western
- Language-specific tracks: cert per language (astrologer operates in Tamil, English, Hindi — each assessed separately)

### 2.2 Out of scope
- Government / regulatory accreditation — I9 addresses eventual regulatory posture
- Issuing verifiable credentials on-chain / blockchain — deferred
- Monetary reward paid *by* Josi for cert (astrologer pays assessment fee to recover review cost)
- Requiring cert for ANY marketplace presence — cert is for premium placement only; uncertified can still operate

### 2.3 Dependencies
- F16 golden chart suite provides blind-reading ground truth
- D4 marketplace network effects weighted by cert level
- D6 longitudinal for outcome-based accuracy component
- E12 workbench for assessment UI

## 3. Technical Research

### 3.1 Rubric design

A robust rubric needs:
- Objective components (accuracy against ground truth)
- Inter-rater-reliability-tested peer review (Cohen's kappa target ≥ 0.6)
- Normalized scoring across tradition / language

**Blind reading (40% weight):**
- Given chart → astrologer writes structured assessment on 5 prescribed questions (career valence, relationship timing, major transit identification, yoga identification, dasa period characterization)
- Each question scored 0-4 against expected output (classical advisor panel defined)
- Scoring: 0 = wrong, 1 = partial, 2 = directionally correct, 3 = specific + correct, 4 = specific + correct + well-cited

**Peer review (35% weight):**
- 3 anonymous Gold+ peers review 3 sample readings (candidate-provided)
- Dimensions: classical fidelity, coherence, client-appropriateness, citations
- Each 1-5 scale; averaged; inter-rater-reliability check

**Client rating aggregate (25% weight):**
- Rolling 12-month mean of post-consultation ratings
- Require n ≥ 30 for first cert; n ≥ 50 for Gold; n ≥ 100 for Platinum
- Bayesian-smoothed (prior prevents N=1 gaming)

### 3.2 Level thresholds

| Level | Blind (40%) | Peer (35%) | Client (25%) | Total | Requirements |
|---|---|---|---|---|---|
| Bronze | ≥ 50% | ≥ 3.0/5 | ≥ 4.0/5 | ≥ 55% | 10+ consultations |
| Silver | ≥ 65% | ≥ 3.5/5 | ≥ 4.3/5 | ≥ 70% | 50+ consultations |
| Gold | ≥ 80% | ≥ 4.0/5 | ≥ 4.5/5 | ≥ 82% | 200+ consultations |
| Platinum | ≥ 90% | ≥ 4.5/5 | ≥ 4.7/5 | ≥ 92% | 500+ consultations, 2+ years tenure |

Thresholds tunable post-launch based on calibration data.

### 3.3 Anti-gaming

- Blind charts drawn from a pool of 500+; rotated per candidate; never shown again to same astrologer
- Peer reviews double-blind (reviewer doesn't know candidate; candidate doesn't know reviewers)
- Client rating aggregated only from verified completed consultations (not self-reports)
- Suspicious rating patterns (D4 anti-gaming) invalidate the client-rating axis
- Revocation: substantiated misconduct or repeated annual-failure

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| Who sits on the classical advisor panel | Minimum 3 senior advisors per tradition; rotated every 2 years | Credibility + freshness |
| Pay for review | Yes — peers paid small honorarium; funded by assessment fee | Reviewer quality; ethical labor |
| Tradition tracks vs composite | Per-tradition; astrologers often specialize | Accuracy of signal |
| Cert revocation reversal | Appeal process with different reviewers | Fairness |
| Display badges publicly | Yes, with tooltip showing rubric | Transparency |
| Grandfather existing top astrologers | No — everyone assessed from scratch | Credibility of process |

## 5. Component Design

### 5.1 New modules

```
src/josi/certification/
├── rubric/
│   ├── scoring.py
│   └── tradition_variants.py
├── blind_reading/
│   ├── assessment_session.py
│   ├── chart_pool.py           # rotation logic
│   └── grader.py               # LLM-assisted + advisor-panel validation
├── peer_review/
│   ├── assignment.py           # matches reviewers to candidates
│   ├── form.py
│   └── irr.py                  # inter-rater reliability tracking
├── client_rating/
│   └── aggregator.py
├── cert_state_machine.py        # applied → assessed → conferred → renewed → revoked
├── badge_service.py             # public badge rendering + metadata
└── revocation.py

src/josi/api/v1/controllers/certification_controller.py
```

### 5.2 Data model additions

```sql
CREATE TABLE cert_application (
    application_id       UUID PRIMARY KEY,
    astrologer_id        UUID NOT NULL,
    tradition            TEXT NOT NULL,
    language             TEXT NOT NULL,
    target_level         TEXT CHECK (target_level IN ('bronze','silver','gold','platinum')),
    state                TEXT NOT NULL,
    submitted_at         TIMESTAMPTZ NOT NULL,
    completed_at         TIMESTAMPTZ
);

CREATE TABLE cert_blind_reading (
    blind_reading_id     UUID PRIMARY KEY,
    application_id       UUID NOT NULL REFERENCES cert_application(application_id),
    chart_id             UUID NOT NULL,
    question_id          TEXT NOT NULL,
    response             TEXT NOT NULL,
    score                INTEGER CHECK (score BETWEEN 0 AND 4),
    grader_notes         TEXT,
    graded_at            TIMESTAMPTZ
);

CREATE TABLE cert_peer_review (
    peer_review_id       UUID PRIMARY KEY,
    application_id       UUID NOT NULL,
    reviewer_id          UUID NOT NULL,
    sample_reading_id    UUID NOT NULL,
    classical_fidelity   INTEGER CHECK (classical_fidelity BETWEEN 1 AND 5),
    coherence            INTEGER CHECK (coherence BETWEEN 1 AND 5),
    client_appropriateness INTEGER CHECK (client_appropriateness BETWEEN 1 AND 5),
    citations_quality    INTEGER CHECK (citations_quality BETWEEN 1 AND 5),
    notes                TEXT,
    reviewed_at          TIMESTAMPTZ
);

CREATE TABLE cert_conferral (
    astrologer_id        UUID NOT NULL,
    tradition            TEXT NOT NULL,
    language             TEXT NOT NULL,
    level                TEXT NOT NULL,
    conferred_at         TIMESTAMPTZ NOT NULL,
    expires_at           TIMESTAMPTZ NOT NULL,
    revoked_at           TIMESTAMPTZ,
    revocation_reason    TEXT,
    PRIMARY KEY (astrologer_id, tradition, language)
);

CREATE INDEX idx_cert_badge_public
    ON cert_conferral(astrologer_id)
    WHERE revoked_at IS NULL AND expires_at > now();
```

### 5.3 API contract

```
POST /api/v1/certification/apply
Body: { tradition, language, target_level }
Response: { application_id, blind_reading_session_token, deadline }

POST /api/v1/certification/blind/{session_token}/submit
Body: { responses: [{question_id, response}] }

GET /api/v1/certification/astrologer/{id}/badges
Response: list of active conferrals with levels + expiry

POST /api/v1/certification/revoke   (admin)
```

## 6. User Stories

### US-D8.1: As an astrologer, I apply for Gold certification in Vedic tradition, Tamil language
**Acceptance:** application submitted; prerequisites checked (200+ consultations, 4.5+ client rating); blind session scheduled.

### US-D8.2: As an assessed astrologer, I complete a blind reading session
**Acceptance:** 10 charts × 5 questions; submitted; graded within SLA 2 weeks.

### US-D8.3: As a Gold peer reviewer, I'm assigned a Silver candidate's sample readings
**Acceptance:** 3 samples; anonymized; I rate within SLA 1 week; inter-rater reliability tracked.

### US-D8.4: As a certified astrologer, my public profile shows my badge(s)
**Acceptance:** per-tradition/per-language badges; tooltip shows rubric; expiry visible.

### US-D8.5: As a user searching the marketplace, I can filter by cert level
**Acceptance:** filter chip per level; results sort option "cert level"; D4 matching uses cert as ranking signal.

### US-D8.6: As a certified astrologer nearing expiry, I'm prompted to recertify
**Acceptance:** 60-day notification; recertification simpler (abbreviated blind session, confirmation of maintained client rating).

### US-D8.7: As admin, I revoke cert for confirmed misconduct with documented reason
**Acceptance:** revocation stored; badges removed immediately; audit log; appeal process accessible.

## 7. Tasks

### T-D8.1: Rubric + scoring model
- **Definition:** Codified rubric; scoring functions; threshold table.
- **Acceptance:** calibration run on historical data (synthetic + pilot); threshold table accepted by classical advisor panel.
- **Effort:** 2 weeks

### T-D8.2: Blind-reading session + chart pool
- **Definition:** Chart pool of 500+ (extension of F16 golden suite); rotation logic; session UI for astrologer.
- **Acceptance:** no repetition within astrologer history; session completable in 2 hours avg.
- **Effort:** 3 weeks

### T-D8.3: Grader (LLM-assisted + advisor-panel validation)
- **Definition:** LLM pre-scores; advisor sampling validates; final score = weighted combine.
- **Acceptance:** human-LLM agreement ≥ 90%; 100% of borderline cases advisor-reviewed.
- **Effort:** 2 weeks

### T-D8.4: Peer-review workflow + IRR tracking
- **Definition:** Assignment engine; review form; IRR computation; reviewer honorarium disbursement.
- **Acceptance:** Cohen's kappa ≥ 0.6 across reviewer pool; disbursement via Stripe Connect.
- **Effort:** 2 weeks

### T-D8.5: Client-rating aggregator + Bayesian smoothing
- **Definition:** Bayesian-smoothed aggregate; fraud-check against D4 anti-gaming.
- **Acceptance:** stable scores; gaming attempts caught.
- **Effort:** 1 week

### T-D8.6: State machine + conferral
- **Definition:** Application states; conferral on pass; expiry + recert scheduling.
- **Acceptance:** all state transitions tested; SLA observed.
- **Effort:** 1.5 weeks

### T-D8.7: Badge service + marketplace integration
- **Definition:** Badge rendering; E12 profile integration; D4 matcher feature.
- **Acceptance:** badges visible on marketplace; filter works.
- **Effort:** 1.5 weeks

### T-D8.8: Revocation + appeal
- **Definition:** Admin revocation flow; astrologer appeal; re-review by different panel.
- **Acceptance:** end-to-end; audit log complete.
- **Effort:** 1 week

## 8. Unit Tests

### 8.1 Rubric scoring correctness
- Category: given known responses → known scores.
- Target: deterministic; 100% match to spec.
- Representative: `test_blind_score_composition`, `test_threshold_for_gold`, `test_weighted_total_formula`.

### 8.2 Chart pool rotation
- Category: no astrologer sees same chart twice across all sessions.
- Target: 100% isolation.
- Representative: `test_no_chart_repetition_per_astrologer`, `test_pool_replenishes`.

### 8.3 Grader agreement
- Category: LLM grader vs human advisor agreement.
- Target: ≥ 90% agreement; borderline cases escalate.
- Representative: `test_llm_advisor_agreement`, `test_borderline_escalates_to_advisor`.

### 8.4 Peer-review IRR
- Category: Cohen's kappa across reviewers.
- Target: kappa ≥ 0.6.
- Representative: `test_kappa_computed_correctly`, `test_low_kappa_triggers_retraining`.

### 8.5 Client rating aggregation
- Category: Bayesian smoothing; fraud filter.
- Target: matches closed-form; fraud-flagged ratings excluded.
- Representative: `test_bayesian_smoothing_prior`, `test_fraud_flagged_excluded`.

### 8.6 State machine
- Category: valid and invalid transitions.
- Target: invalid transitions rejected; audit log complete.
- Representative: `test_apply_to_assessed_to_conferred`, `test_revoked_to_appealing_to_reconferred`.

### 8.7 Badge expiry & recert
- Category: expiry enforcement; recert workflow.
- Target: expired badges not shown; recert reminder sent at 60 days.
- Representative: `test_expired_badge_hidden`, `test_recert_reminder_at_60d`.

## 9. EPIC-Level Acceptance Criteria

- [ ] Rubric + thresholds ratified by advisor panel
- [ ] Blind-reading pool of 500+ with no overlap to open marketplace
- [ ] Grader agreement ≥ 90%
- [ ] Peer-review IRR ≥ 0.6
- [ ] 100+ astrologers certified across ≥ 3 traditions × ≥ 3 languages before GA
- [ ] Marketplace filter + sort working; D4 matcher uses cert as feature
- [ ] Revocation + appeal flow live
- [ ] Annual recertification reminders working

## 10. Rollout Plan

- **Feature flag:** `astrologer_certification`.
- **Phase 1 (4 weeks):** invitation-only beta with 50 senior astrologers; calibrate rubric; train first peer-reviewer cadre.
- **Phase 2 (6 weeks):** opt-in for all Gold-eligible astrologers (200+ consultations); scale reviewer pool; tune thresholds.
- **Phase 3 (4 weeks):** open to all levels; badge surfacing in marketplace.
- **Phase 4:** public GA announcement + marketing push.
- **Rollback:** flag off hides badges and pauses applications; data retained.

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Rubric bias across traditions | Medium | High | Per-tradition advisor panels; ongoing calibration |
| Peer reviewers game outcomes | Medium | High | Double-blind; IRR monitoring; reviewer rotation |
| Advisor panel bottleneck | High | Medium | LLM pre-grading + advisor sampling; panel recruitment ongoing |
| Astrologers refuse to apply | Medium | Medium | Marketing emphasizing marketplace uplift; early-adopter recognition |
| Revocation triggers litigation | Medium | Medium | Documented process; legal review of revocation language |
| Cost of honoraria not recovered | Medium | Medium | Assessment fee tuned to cover costs; revisited annually |
| Astrologers see cert as gatekeeping | Medium | Medium | Entry level Bronze accessible; uncertified still operate |

## 12. References

- Master spec: `docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`
- Related PRDs: F16 (golden suite), D4 (marketplace), D6 (longitudinal), E12 (workbench), I9 (regulatory)
- Methodology: Cohen's kappa for IRR; Bayesian rating smoothing (Evan Miller 2009 "How Not to Sort By Average Rating")
