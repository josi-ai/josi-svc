---
prd_id: D6
epic_id: D6
title: "Longitudinal personal dashboard — predictions made vs outcomes reported"
phase: P5-dominance
tags: [#experimentation, #end-user-ux, #correctness]
priority: must
depends_on: [E14a, F8, F13, D5]
enables: [D7, D10, I2]
classical_sources: []
estimated_effort: 8-10 weeks
status: draft
author: "@agent"
last_updated: 2026-04-19
---

# D6 — Longitudinal Personal Dashboard

## 1. Purpose & Rationale

Astrology has never been measured **at the individual user level**. Across classical literature and modern apps alike, predictions are made, and whether they came true is anecdotal at best. Josi can change this. Every AI response, every astrologer reading, every classical technique activation carries provenance via F13. Every prediction is time-stamped. If we also capture outcomes, we have per-user ground truth.

The longitudinal dashboard is that capture-and-display layer. Over months:
- User sees "Saturn transit to Moon prediction last June — outcome reported: matched moderately"
- Per-astrologer accuracy: "Astrologer X was 78% accurate on your last 10 predictions"
- Per-strategy accuracy: "Strategy C (source-weighted, your weights) was 82% on your major transits; Strategy D was 71%"
- Per-technique-family accuracy: "Dasha-based predictions ran higher than yoga-activation predictions"

Downstream:
1. Drives subscription retention (unique longitudinal value)
2. Feeds back into E14a experimentation (per-user measurement signal)
3. Provides raw material for D7 research API
4. Creates the empirical layer the category has never had

## 2. Scope

### 2.1 In scope
- Prediction capture: any AI response or astrologer reading that makes a time-bounded claim is tagged as a `prediction` with time window, topic tag, and provenance
- Outcome capture: user marks "matched / partial / no match / not sure" on individual predictions; optionally with note
- Passive outcome signals: biometric deltas (D5), calendar events (opt-in), mood logs
- Dashboard views:
  - Timeline of predictions (past + upcoming)
  - Per-astrologer accuracy over time
  - Per-strategy (A/B/C/D) accuracy over time
  - Per-technique-family accuracy
  - Per-topic accuracy (career/relationships/health/finance)
- Accuracy computation: Bayesian with uninformative prior (never claim accuracy until sufficient N)
- Export to PDF for user records
- Feedback loop into E14a (signal: `predicted_vs_actual`)

### 2.2 Out of scope
- Cross-user leaderboards ("most accurate astrologer platform-wide") — privacy-heavy; deferred to D8 certification's own accuracy component
- Public sharing of user accuracy data
- ML-based outcome inference from biometrics/calendar (we prompt the user; no inference)
- Monetary reward for feedback (tempts gaming)

### 2.3 Dependencies
- E14a experimentation framework provides the signal pipe
- F13 content-hash provenance ties predictions to specific rule versions / strategy versions
- F8 aggregation for per-strategy accuracy attribution
- D5 biometric for passive signals (optional)

## 3. Technical Research

### 3.1 What counts as a "prediction"

A claim is a prediction iff:
- It has a time window (future or currently-active)
- It has a topic (career/relationships/health/finance/general)
- It has an assertion (positive, neutral, challenging)
- It cites provenance (source_id(s), strategy_id, rule_ids)

Claims that are general ("your Moon is in Cancer") are not predictions. Only claims like "the next 3 months will be favorable for career" are.

Detection: LLM-based classifier (tool-use) tags AI output at generation time. Astrologer readings prompted to tag predictions explicitly during workbench (E12) input.

### 3.2 Accuracy computation

For each prediction, outcomes have 4 states: `matched`, `partial`, `no_match`, `unknown`. Bayesian treatment:
- Prior: Beta(1, 1) uninformative
- Update: `matched` → +1 success; `partial` → +0.5 success; `no_match` → +1 failure; `unknown` → no update
- Report mean + 80% credible interval
- Never report an accuracy number until 80%-CI width < 0.3 (prevents "100% accuracy, N=1")

### 3.3 Attribution

A prediction carries multiple provenance dimensions. Attribution is done per dimension:
- Per-astrologer: predictions made by astrologer A
- Per-strategy: aggregations via strategy S
- Per-technique-family: predictions primarily driven by dasa/yoga/transit
- Per-topic: career/relationships/etc.

Same prediction can attribute to multiple dimensions (e.g., "astrologer A used strategy C on dasa technique for career topic").

### 3.4 Anti-gaming

Users might over-report "matched" if the app rewards it. Mitigations:
- No reward for reporting
- Passive signal cross-checks (D5): if user reported "positive career" but calendar shows a termination event opt-in-captured nearby, flag for review
- Confidence interval dampens exaggerated small-N claims
- Audit: predictions > 6 months old are sampled for sanity checks

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| Auto-infer outcomes from biometrics | No — prompt user; biometrics are supplementary | Respects agency; avoids overclaim |
| Public ranking of astrologers by accuracy | No in D6; D8 cert handles this with moderation | Privacy + fairness |
| How to handle predictions astrologer didn't explicitly tag | Workbench (E12) prompts tagging; untagged readings don't become predictions | Quality > quantity |
| When to show accuracy number | Only after credible interval width < 0.3 | Honest epistemics |
| Include AI-only accuracy separately | Yes — own attribution dimension | Comparison across modalities |
| How long to keep prediction records | Forever (per retention policy) unless user deletes | Longitudinal = long |

## 5. Component Design

### 5.1 New modules

```
src/josi/longitudinal/
├── prediction_detector.py       # LLM classifier; assigns prediction metadata
├── prediction_store.py
├── outcome_capture.py           # user-driven feedback API
├── accuracy_engine.py           # Bayesian aggregator; per-dimension
├── dashboard_service.py         # serves assembled views
├── export_pdf.py
└── feedback_bridge.py           # forwards signal to E14a

src/josi/api/v1/controllers/longitudinal_controller.py
```

### 5.2 Data model additions

```sql
CREATE TABLE prediction (
    prediction_id        UUID PRIMARY KEY,
    user_id              UUID NOT NULL,
    organization_id      UUID NOT NULL,
    chart_id             UUID REFERENCES chart(chart_id),
    source_kind          TEXT NOT NULL CHECK (source_kind IN
                           ('ai_chat','ai_voice','astrologer_consultation','astrologer_async')),
    source_id_ref        UUID,                    -- FK to specific session / consultation
    astrologer_id        UUID,
    topic                TEXT NOT NULL,           -- 'career','relationships',...
    valence              TEXT CHECK (valence IN ('favorable','neutral','challenging')),
    window_start         DATE NOT NULL,
    window_end           DATE NOT NULL,
    claim_text           TEXT NOT NULL,
    strategy_id          TEXT,                    -- attribution to aggregation strategy
    technique_family_id  TEXT,                    -- primary technique
    rule_ids             TEXT[],                  -- specific rules that drove claim
    created_at           TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE prediction_outcome (
    prediction_id        UUID PRIMARY KEY REFERENCES prediction(prediction_id),
    outcome              TEXT NOT NULL CHECK (outcome IN ('matched','partial','no_match','unknown')),
    reported_at          TIMESTAMPTZ NOT NULL,
    reported_by_user_id  UUID NOT NULL,
    note                 TEXT,
    passive_signals      JSONB                    -- captured signals snapshot
);

CREATE TABLE accuracy_aggregate (
    user_id              UUID NOT NULL,
    dimension            TEXT NOT NULL,            -- 'astrologer' | 'strategy' | 'technique_family' | 'topic'
    dimension_value      TEXT NOT NULL,            -- astrologer_id / 'C_weighted' / 'yoga' / 'career'
    alpha                NUMERIC(10,4) NOT NULL,   -- Beta posterior alpha
    beta                 NUMERIC(10,4) NOT NULL,   -- Beta posterior beta
    mean                 NUMERIC(5,4) NOT NULL,
    ci_low               NUMERIC(5,4) NOT NULL,
    ci_high              NUMERIC(5,4) NOT NULL,
    n_observations       INTEGER NOT NULL,
    computed_at          TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (user_id, dimension, dimension_value)
);

CREATE INDEX idx_prediction_user_window ON prediction(user_id, window_start, window_end);
```

### 5.3 API contract

```
GET /api/v1/me/longitudinal/predictions?state=open|past&limit=50
Response: list with attribution + outcome (if any)

POST /api/v1/me/longitudinal/predictions/{id}/outcome
Body: { "outcome": "partial", "note": "career move happened but later than expected" }

GET /api/v1/me/longitudinal/accuracy
Response: {
  by_astrologer: [...],
  by_strategy: [...],
  by_technique_family: [...],
  by_topic: [...]
}

GET /api/v1/me/longitudinal/export.pdf
```

## 6. User Stories

### US-D6.1: As a user, I see predictions made for me with clear time windows
**Acceptance:** timeline view of past + upcoming predictions; each shows source (AI / astrologer name), topic, window, and current status.

### US-D6.2: As a user, I can report an outcome on a prediction in under 10 seconds
**Acceptance:** one-tap outcome; optional note; persists immediately; dashboard updates.

### US-D6.3: As a user, I see per-astrologer accuracy only after enough data
**Acceptance:** if credible-interval width ≥ 0.3 → shows "needs more data" instead of number; once width < 0.3 → shows mean + CI.

### US-D6.4: As a user, I can export my longitudinal record as PDF
**Acceptance:** PDF generated in < 10s; includes timeline + accuracy summaries + disclaimer.

### US-D6.5: As a user, I can delete any prediction or outcome
**Acceptance:** delete removes from aggregates within 1h; audit log captures.

### US-D6.6: As an experimentation engine (E14a), I receive outcome signals per prediction
**Acceptance:** outcome events published to E14a with full attribution; E14a can compute per-strategy accuracy across users.

### US-D6.7: As a product owner, I can measure retention impact of the dashboard
**Acceptance:** A/B: users with dashboard engagement (≥ 1 outcome logged per month) show retention delta vs controls; metric tracked.

## 7. Tasks

### T-D6.1: Prediction detector (LLM classifier + workbench prompts)
- **Definition:** Tool-use classifier in AI chat; workbench (E12) prompts astrologer to tag predictions.
- **Acceptance:** ≥ 90% precision on gold-labeled 500-claim set; minimal recall loss.
- **Effort:** 2 weeks

### T-D6.2: Prediction storage + linkage
- **Definition:** `prediction` table populated on AI/astrologer output; linkage to provenance.
- **Acceptance:** every prediction has source/rule/strategy attribution; zero orphans.
- **Effort:** 1.5 weeks

### T-D6.3: Outcome capture UX + API
- **Definition:** One-tap outcome UI on timeline; API endpoint; passive-signal snapshot.
- **Acceptance:** Playwright: <10s flow; API 200 median latency < 100ms.
- **Effort:** 2 weeks

### T-D6.4: Bayesian accuracy engine
- **Definition:** Beta posterior per (user, dimension, value); credible-interval reporting.
- **Acceptance:** determinstic; property-based test; correct mathematics.
- **Effort:** 1.5 weeks

### T-D6.5: Dashboard views + charts
- **Definition:** Timeline + per-dimension accuracy views; "insufficient data" handling.
- **Acceptance:** design review pass; copy reviewed for overclaim.
- **Effort:** 2 weeks

### T-D6.6: PDF export
- **Definition:** Server-side PDF generation from dashboard data.
- **Acceptance:** < 10s; all sections rendered; disclaimer present.
- **Effort:** 1 week

### T-D6.7: E14a feedback bridge
- **Definition:** Outcome events publish to E14a signal log with full attribution.
- **Acceptance:** E14a experiment can read per-strategy accuracy; integration test passes.
- **Effort:** 1 week

### T-D6.8: Retention A/B instrumentation
- **Definition:** Cohort instrumentation; retention delta metric.
- **Acceptance:** dashboard in metrics tool; baseline measured pre-launch.
- **Effort:** 0.5 weeks

## 8. Unit Tests

### 8.1 Prediction detection
- Category: classifier precision/recall on labeled sample.
- Target: precision ≥ 90%; recall ≥ 70%.
- Representative: `test_detects_time_bounded_claim`, `test_ignores_generic_placements`, `test_detects_astrologer_tagged_prediction`.

### 8.2 Provenance linkage
- Category: every prediction row ties to source/rule/strategy.
- Target: 100% linkage; zero orphans.
- Representative: `test_ai_prediction_attributes_strategy`, `test_astrologer_prediction_attributes_astrologer_id`.

### 8.3 Bayesian accuracy
- Category: correctness of posterior + CI.
- Target: matches textbook closed-form for Beta(1,1) + Bernoulli.
- Representative: `test_beta_posterior_update`, `test_ci_width_shrinks_with_n`, `test_partial_counts_half_success`.

### 8.4 Outcome capture
- Category: API correctness, idempotency, audit.
- Target: correctly debouncing double-tap; delete removes from aggregates.
- Representative: `test_duplicate_outcome_submission`, `test_delete_outcome_recomputes_aggregates`.

### 8.5 "Insufficient data" gate
- Category: enforcement of CI-width < 0.3 before showing number.
- Target: 100% enforcement.
- Representative: `test_small_n_shows_insufficient`, `test_wide_ci_shows_insufficient`.

### 8.6 E14a integration
- Category: signal emission.
- Target: every outcome produces exactly one E14a signal with correct tags.
- Representative: `test_emit_signal_on_outcome`, `test_no_duplicate_emit_on_update`.

### 8.7 Anti-gaming
- Category: detection of implausible reporting patterns.
- Target: flag for review when passive signal contradicts self-report at > 3σ.
- Representative: `test_passive_signal_contradiction_flagged`.

## 9. EPIC-Level Acceptance Criteria

- [ ] Predictions captured from AI chat, AI voice, astrologer consultations
- [ ] Outcome capture UX < 10s flow
- [ ] Bayesian engine + CI gating verified
- [ ] 4 attribution dimensions live (astrologer, strategy, technique_family, topic)
- [ ] E14a receives signals end-to-end
- [ ] Retention A/B instrumentation ready
- [ ] Privacy: delete works across all tables
- [ ] Export PDF works

## 10. Rollout Plan

- **Feature flag:** `longitudinal_dashboard`.
- **Phase 1 (2 weeks):** internal dogfood + beta 500 users; AI-only predictions tagged.
- **Phase 2 (3 weeks):** astrologer-tagged predictions enabled via E12; 10% rollout.
- **Phase 3:** GA; E14a starts using signals for per-strategy analysis.
- **Rollback:** flag off hides UI; data retained; can re-enable.

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Astrologers avoid tagging to avoid accuracy scrutiny | High | Medium | Make tagging easy + positive framing; untagged readings don't accrue accuracy credit (positive or negative) |
| Over-claiming with small N | Medium | High | CI-width gate; explicit "insufficient" state |
| Confirmation bias in user self-reports | High | Medium | Passive cross-checks; periodic reminder of honest reporting |
| Negative aggregate damages B2C NPS | Medium | Medium | Pitch as "personal science"; frame non-match as neutral, not failure |
| Retention A/B confound | Medium | Low | Multiple cohorts; longer observation window |
| Aggregates become gaming targets for astrologers | Medium | Medium | D8 cert handles public reputation; D6 is private per-user |
| Classifier bias across topics/languages | Medium | Medium | Multilingual eval set; ongoing bias audits |

## 12. References

- Master spec: `docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`
- Related PRDs: E14a (experimentation), F13 (provenance), D5 (passive signals), D7 (research), I2 (research press)
- Bayesian method: Beta-Bernoulli conjugacy (textbook)
