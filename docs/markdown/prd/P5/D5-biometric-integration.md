---
prd_id: D5
epic_id: D5
title: "Biometric integration (Apple Health, Oura, WHOOP) — transit-event ↔ body-signal correlation"
phase: P5-dominance
tags: [#end-user-ux, #experimentation, #correctness]
priority: should
depends_on: [F8, F9, F13, E6a, D6]
enables: [D7, Research]
classical_sources: [bphs, western_transits]
estimated_effort: 10-12 weeks
status: draft
author: "@agent"
last_updated: 2026-04-19
---

# D5 — Biometric Integration

## 1. Purpose & Rationale

Astrology's central skeptic claim — "it's unfalsifiable" — is **architecturally** answered by pairing transit events with objective body signals. Not as proof, but as a personal feedback loop: "When Saturn squared my Moon last week, my HRV dropped, my sleep quality fell, and my logged mood was 2/5. Correlation score: high. Make of that what you will."

Three value props:
1. **Personal validation** — a user learns, over months, whether transits correlate with their body. Agnostic framing; no efficacy claim.
2. **Longitudinal-dashboard anchor (D6)** — biometric deltas are objective signals feeding D6's "predictions vs outcomes" tracker, augmenting self-reports.
3. **Research substrate (D7)** — anonymized, opt-in, large-N biometric-transit dataset enables legitimate astrology research for the first time at scale.

Differentiator: no other astrology app integrates biometrics. Health/fitness apps do; spiritual apps don't.

## 2. Scope

### 2.1 In scope
- HealthKit (iOS) integration for: heart rate, HRV, sleep stages, active minutes, mindful minutes, menstrual cycle (opt-in)
- Oura API integration: readiness score, sleep score, activity score, HRV, body temp deviation
- WHOOP API integration: recovery, strain, sleep performance, HRV
- Manual mood/energy log: 1-5 scale, morning + evening prompts
- Transit-event generator (already exists via E6a) — produces timestamped events per user
- Correlation engine: for each transit event, compute delta in biometric signals in the 48h pre/post window vs the user's 30-day rolling baseline
- Per-user correlation dashboard: shows events + deltas + rolling correlation scores
- Privacy: on-device processing where possible; opt-in cloud correlation; no sale of data; HIPAA-adjacent handling
- Research opt-in: user can contribute anonymized data to D7

### 2.2 Out of scope
- Fitbit, Google Fit, Garmin — P6 expansion (API integrations are similar but numerous)
- Medical claims of any sort; no diagnosis, no advice beyond "your body shows X during transit Y"
- Continuous glucose monitors, blood labs, genomic — separate privacy tier
- Coaching or interventions based on biometrics
- Integration with wearable during active session (read-only cadence, daily batch)

### 2.3 Dependencies
- E6a Transit Intelligence already produces structured transit events with timestamps
- F9 chart_reading_view for active chart factors per user
- F13 content-hash provenance so correlations are tied to specific technique versions
- D6 longitudinal dashboard consumes correlation output
- Consent + privacy infrastructure (see §3.4)

## 3. Technical Research

### 3.1 Biometric signal prioritization

Tier-1 signals (highest SNR for transit correlation claims):
- HRV (RMSSD overnight) — stress/autonomic marker
- Deep sleep minutes
- Resting heart rate
- Self-reported mood 1-5
- Cycle-day (for menstruating users, opt-in)

Tier-2 signals:
- Step count / active minutes
- Body temperature deviation
- Mindful minutes

Correlation engine focuses on tier-1; tier-2 available for exploratory user viewing.

### 3.2 Correlation approach

Per-user, per-(signal, transit-family) correlation over a rolling window. Not traditional Pearson (auto-correlation in time series violates assumption). Approach:
- Establish 30-day rolling baseline for each signal (median + IQR)
- Event window: −24h pre / +48h post transit exact-hit
- Delta = (event window median − baseline median) / baseline IQR  → z-like score
- Aggregate deltas over multiple instances of same transit family → per-user "transit signature"
- Caveats shown explicitly: "N=3 observations; not statistically meaningful until N≥10"

### 3.3 Privacy architecture

- OAuth-based vendor token storage (encrypted-at-rest, envelope with KMS)
- Biometric data lands in a segregated schema `biometric.*` with stricter access controls
- On-device aggregation where possible (HealthKit encourages this; Oura/WHOOP require cloud pull)
- User can wipe data via DSR endpoint within 24h
- Never shared with third parties without explicit research opt-in (D7)
- Audit log on all reads

### 3.4 Consent flow

Two-stage consent:
1. **Integration consent** — "Connect Oura to see biometric deltas alongside transits. Data stored in your account only."
2. **Research consent** (separate opt-in) — "Contribute anonymized biometric-transit pairs to Josi research (D7). Aggregated statistics only; no individual identification."

Both revocable any time.

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| Medical framing | Strictly non-medical; "observation, not diagnosis" language | Regulatory + ethical |
| Mandatory research opt-in | No — separate opt-in | Research value must not gate personal feature |
| Real-time vs daily batch | Daily batch (cron 4am local) | Wearable APIs rate-limit; no latency need |
| Include menstrual cycle | Yes (opt-in, special-category data, extra consent) | Widely requested; ancient astrological link; treat with extra care |
| How to handle missing data | Explicit "N=X observations, insufficient" rather than interpolation | Honesty |
| Cross-user research aggregation | Opt-in only; differential privacy applied to released stats | Ethics |

## 5. Component Design

### 5.1 New modules

```
src/josi/biometric/
├── providers/
│   ├── base.py                  # BiometricProvider ABC
│   ├── healthkit.py             # iOS only, user-device-mediated
│   ├── oura.py
│   └── whoop.py
├── ingestion/
│   ├── oauth.py                 # token storage with envelope encryption
│   ├── batch_puller.py          # daily cron per-user
│   └── validator.py
├── correlation/
│   ├── baseline.py              # rolling baseline builder
│   ├── window_delta.py          # event-window delta computer
│   └── signature.py             # per-user transit signature
├── privacy/
│   ├── dsr.py                   # GDPR/DPDP wipe endpoint
│   └── audit.py
└── api/
    └── controller.py

src/josi/api/v1/controllers/biometric_controller.py
```

### 5.2 Data model additions

```sql
CREATE SCHEMA biometric;

CREATE TABLE biometric.connection (
    connection_id        UUID PRIMARY KEY,
    user_id              UUID NOT NULL,
    provider             TEXT NOT NULL CHECK (provider IN ('healthkit','oura','whoop')),
    oauth_token_enc      BYTEA NOT NULL,
    connected_at         TIMESTAMPTZ NOT NULL,
    revoked_at           TIMESTAMPTZ,
    research_opt_in      BOOLEAN NOT NULL DEFAULT false,
    special_category_opt_in BOOLEAN NOT NULL DEFAULT false   -- menstrual cycle
);

CREATE TABLE biometric.daily_metric (
    user_id              UUID NOT NULL,
    metric_date          DATE NOT NULL,
    metric_name          TEXT NOT NULL,                  -- 'hrv_rmssd','deep_sleep_min','rhr','mood',...
    value                NUMERIC(10,3) NOT NULL,
    source_provider      TEXT NOT NULL,
    ingested_at          TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (user_id, metric_date, metric_name)
);
-- Partitioned by RANGE(metric_date), monthly partitions.

CREATE TABLE biometric.mood_log (
    user_id              UUID NOT NULL,
    logged_at            TIMESTAMPTZ NOT NULL,
    mood_score           INTEGER NOT NULL CHECK (mood_score BETWEEN 1 AND 5),
    energy_score         INTEGER CHECK (energy_score BETWEEN 1 AND 5),
    notes                TEXT,
    PRIMARY KEY (user_id, logged_at)
);

CREATE TABLE biometric.transit_correlation (
    user_id              UUID NOT NULL,
    transit_event_id     UUID NOT NULL,                   -- FK to transit_event table
    metric_name          TEXT NOT NULL,
    pre_baseline_median  NUMERIC(10,3),
    window_median        NUMERIC(10,3),
    delta_zscore         NUMERIC(10,3),
    window_n             INTEGER,
    computed_at          TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (user_id, transit_event_id, metric_name)
);

CREATE INDEX idx_transit_correlation_user_time
    ON biometric.transit_correlation (user_id, computed_at DESC);
```

Strict RLS: only the user's own service role can read from `biometric.*`; research job has a read-only role with differential-privacy wrapper.

### 5.3 API contract

```
POST /api/v1/biometric/connect/{provider}  → OAuth start
GET  /api/v1/biometric/status               → connected providers + last sync
GET  /api/v1/biometric/transit-correlations?since=...
  Response: list of {transit_event, metric_name, delta_zscore, interpretation_caveat}
POST /api/v1/biometric/mood                 → { mood_score, energy_score, notes }
DELETE /api/v1/biometric/data               → DSR wipe
POST /api/v1/biometric/research/opt-in
```

## 6. User Stories

### US-D5.1: As a user, I connect my Oura and see transit-biometric deltas within 24h of first sync
**Acceptance:** OAuth succeeds; daily pull populates metrics; within 24h a first correlation card appears; UI shows explicit "N=1 observation; not meaningful yet" caveat.

### US-D5.2: As a skeptical user, I see the math
**Acceptance:** tap-through on correlation card shows baseline method, window definition, z-score formula, data points used, and honest confidence caveats.

### US-D5.3: As a privacy-conscious user, I can wipe biometric data and know it's gone
**Acceptance:** DSR endpoint clears biometric.* tables within 24h; audit log confirms; acknowledgment emailed.

### US-D5.4: As a menstruating user, I separately opt in for cycle correlation
**Acceptance:** cycle-day data requires `special_category_opt_in = true`; UI explains special-category handling; revocation removes cycle-specific correlations.

### US-D5.5: As a researcher-in-consent, I contribute aggregated data to D7
**Acceptance:** research opt-in stored; D7 only sees differential-privacy-wrapped aggregates; opt-out stops new contributions immediately.

### US-D5.6: As a user, when a major transit begins I get a "baseline-capture" nudge
**Acceptance:** 72h before a major transit, UX suggests logging mood nightly to improve signal; opt-in notification.

### US-D5.7: As a user on Android without Oura/WHOOP, I can still log mood
**Acceptance:** mood-only path works standalone; produces correlations when enough events accumulate.

## 7. Tasks

### T-D5.1: Provider abstractions + OAuth plumbing
- **Definition:** ABC + Oura + WHOOP; HealthKit via native iOS app wrapper; token encryption with KMS envelope.
- **Acceptance:** connect/disconnect flows; tokens never in plaintext logs; rotation tested.
- **Effort:** 3 weeks

### T-D5.2: Daily batch puller (cron + per-user scheduling)
- **Definition:** Procrastinate/Temporal job pulls each provider nightly in user's local 4am; rate-limit handling; backfill on reconnect.
- **Acceptance:** 99.5% success rate; retry-on-failure within 24h; observability dashboards.
- **Effort:** 2 weeks

### T-D5.3: Mood-log UI and API
- **Definition:** Morning/evening prompts; 1-5 scale; notes optional; notification opt-in.
- **Acceptance:** < 10s to log; streak incentive; response rate > 40% of engaged users.
- **Effort:** 1.5 weeks

### T-D5.4: Correlation engine (baseline + window + signature)
- **Definition:** Baseline builder; window-delta computer; per-transit-family signature aggregator.
- **Acceptance:** unit tests on synthetic data; deterministic; handles missing data gracefully.
- **Effort:** 3 weeks

### T-D5.5: Correlation dashboard (frontend)
- **Definition:** Per-user view of transit events × biometric deltas; timeline + table views; math tap-through.
- **Acceptance:** Playwright screenshots reviewed; caveats visible on every card.
- **Effort:** 2 weeks

### T-D5.6: Privacy controls (RLS, DSR, audit)
- **Definition:** Schema-level RLS; DSR endpoint; audit log.
- **Acceptance:** penetration test: only user's service role reads their data; DSR erases within 24h.
- **Effort:** 2 weeks

### T-D5.7: Research opt-in path + DP aggregates
- **Definition:** Opt-in flow; DP-wrapped aggregate view for D7; opt-out stops future contribution.
- **Acceptance:** DP epsilon ≤ 1 per released aggregate; aggregate count < 20 suppresses output.
- **Effort:** 2 weeks

### T-D5.8: HealthKit iOS integration
- **Definition:** iOS app wrapper reads HealthKit and pushes daily aggregates to API.
- **Acceptance:** permissions flow; background refresh; Apple review pass.
- **Effort:** 3 weeks (needs mobile team)

## 8. Unit Tests

### 8.1 OAuth + token handling
- Category: connect, disconnect, rotation, encryption.
- Target: zero plaintext tokens in logs; 100% encryption of stored tokens.
- Representative: `test_oauth_token_never_logged`, `test_token_rotation_succeeds`, `test_revoke_clears_token_and_data`.

### 8.2 Provider API adapters
- Category: ingestion correctness per provider.
- Target: unit fixtures for each vendor's documented responses.
- Representative: `test_oura_sleep_parsing`, `test_whoop_hrv_parsing`, `test_healthkit_aggregates_from_device`.

### 8.3 Correlation math
- Category: baseline, delta z-score, signature aggregation.
- Target: deterministic; correct on synthetic cases with known ground truth.
- Representative: `test_baseline_rolling_30d`, `test_delta_zscore_formula`, `test_signature_insufficient_observations_flagged`.

### 8.4 Privacy / RLS
- Category: enforcement of row-level security, DSR.
- Target: 100% isolation in pen tests; DSR removes all rows within 24h.
- Representative: `test_cross_user_read_blocked`, `test_dsr_wipes_all_schemas`, `test_audit_log_captures_every_read`.

### 8.5 Research DP
- Category: differential-privacy wrapping.
- Target: epsilon ≤ 1; small-cell suppression at n < 20.
- Representative: `test_dp_noise_added`, `test_small_aggregate_suppressed`, `test_optout_stops_contribution_immediately`.

### 8.6 End-to-end pipelines
- Category: provider → ingest → correlate → dashboard.
- Target: fixture user with 90 days of simulated data produces expected transit signatures.
- Representative: `test_e2e_oura_to_dashboard`, `test_e2e_mood_only_path`, `test_e2e_healthkit_background_refresh`.

## 9. EPIC-Level Acceptance Criteria

- [ ] 3 providers (HealthKit, Oura, WHOOP) connect end-to-end
- [ ] Mood log integrated
- [ ] Correlation engine produces per-user transit signatures with honest caveats
- [ ] Privacy pen-test passes
- [ ] DSR verified
- [ ] Research opt-in feeds D7 via DP-wrapped aggregates
- [ ] No medical claims surface anywhere in UX
- [ ] Launch disclaimers reviewed by counsel

## 10. Rollout Plan

- **Feature flag:** `biometric_integration`.
- **Phase 1 (3 weeks):** internal dogfood w/ Josi team; Oura + WHOOP only (web-only).
- **Phase 2 (4 weeks):** closed beta 1000 users with Oura/WHOOP; collect feedback; gate = NPS ≥ 40, zero privacy complaints, DSR tested live.
- **Phase 3 (4 weeks):** iOS HealthKit via native app; mood log everywhere; 10% rollout.
- **Phase 4:** GA.
- **Rollback:** flag off hides feature; data retained unless DSR; easy re-enable.

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Privacy breach via biometric schema | Low | Very High | RLS, KMS, audit logs, pen tests, isolated schema |
| Medical-claim drift in UX copy | Medium | High | Counsel review of all copy; automated copy-lint for banned phrases |
| Vendor API deprecation (Oura v3, WHOOP API) | Medium | Medium | Abstraction layer; version pinning; fallback to manual log |
| Overclaiming correlation with small N | High | Medium | Explicit N + caveats; suppress claims until N ≥ 10 |
| Research opt-in misunderstood | Medium | High | Two-stage consent; plain language; re-prompt annually |
| Menstrual cycle data mishandling | Low | Very High | Special-category opt-in; extra encryption; regional bans respected |
| iOS review rejection (HealthKit) | Medium | Medium | Follow Apple guidelines strictly; dry-run via TestFlight |

## 12. References

- Master spec: `docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`
- Related PRDs: E6a (transit events), F9 (chart_reading_view), D6 (longitudinal dashboard), D7 (research API)
- Vendor docs: Oura Cloud API v2+, WHOOP API v2, Apple HealthKit
- Regulatory: GDPR special-category data (Art 9); DPDP Act; US HIPAA-adjacent handling
