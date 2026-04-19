---
prd_id: I7
epic_id: I7
title: "Astrology for Institutions (B2G / B2NGO)"
phase: P6-institution
tags: [#multi-tenant, #correctness]
priority: could
depends_on: [I5, I1, I6, D9, I2]
enables: [I9, I11]
classical_sources: []
estimated_effort: 4-6 quarters (Year 4 through Year 5), with long-horizon studies extending beyond
status: draft
author: "@claude"
last_updated: 2026-04-19
---

# I7 — Astrology for Institutions (B2G / B2NGO)

## 1. Purpose & Rationale

Wellness, self-knowledge, and reflection programs already run in schools, prisons, veterans' services, corporate EAPs, and NGO social-work contexts. They use frameworks like CBT, positive psychology, expressive arts, and journaling. Classical astrology — stripped of fatalism and used as a structured framework for self-reflection and cognitive pattern recognition — is a plausible (if novel) addition to this toolkit, *where legally and ethically appropriate*.

I7 pursues institutional pilots only in jurisdictions and contexts where:
- Astrology is culturally familiar and non-stigmatized (significant parts of India, Nepal, Sri Lanka, diaspora communities globally).
- Participation is strictly voluntary and separated from coerced-engagement contexts (we avoid compulsory-participation in carceral or minor-student settings).
- Academic outcome studies can be run (with IRB approval) to evaluate efficacy.
- Disclaimers are legally clear: this is not medical, legal, or financial advice.

**Strategic value:**
- Diversified revenue: institutional contracts are sticky, predictable, non-correlated with B2C.
- Research pipeline: IRB-approved studies feed I2.
- Regulatory legitimization: institutional adoption strengthens I9 (standards body).
- Mission alignment: if astrology-as-reflection has measurable efficacy, making it accessible in institutions is a compounding public good.
- High scrutiny environments also sharpen Josi's ethical rigor — helpful across the whole product.

## 2. Scope

### 2.1 In scope
- Pilot program design for 3 institutional verticals:
  - **Schools** (higher-ed or late-secondary in culturally-appropriate regions): self-reflection / career-exploration module.
  - **Veterans' wellness NGOs**: supplementary reflection tool alongside CBT / peer-support.
  - **Corporate EAPs / wellness programs**: voluntary employee offering.
- Outcome-measurement framework (pre/post surveys, validated wellness scales such as WHO-5, DASS-21).
- Independent ethics board (3 external members: ethicist + clinical psychologist + domain astrologer) for IRB-complementary oversight.
- Institutional admin portal: enroll cohorts, manage consent, view aggregated wellness dashboards (never individual).
- Volunteer-only participation in every context; opt-out at any time without consequences.
- Curriculum content from I1 Academy (Foundations), re-framed for institutional participants.
- Legal disclaimers per jurisdiction + legal review as a gating requirement.
- Outcome studies: partner with academic researchers to run and publish through I2.

### 2.2 Out of scope (non-negotiable)
- **Carceral / incarcerated populations** in Year 4 launch — ethical complexity too high; revisit with dedicated ethics framework in Year 5+.
- **Minors without parental consent** — defer to Year 5+ with school + parental + student tri-consent.
- **Clinical replacement for therapy or medication** — explicitly complementary; all materials state this.
- **Decision-making tools for institutional assessments** (e.g., "use astrology to decide parole"). Never.
- **Jurisdictions where astrology-adjacent services are restricted** (check per launch country).
- **Astrology as spiritual / religious counseling** — program framed as reflective framework, not religious practice.

### 2.3 Dependencies
- **I5 (Cross-tradition unified reasoning)** — the voice of the companion in institutional contexts.
- **I1 (Academy)** — curriculum source material.
- **I6 (Digital lifetime companion)** — journaling substrate (with institutional consent overlay).
- **D9 (Enterprise tier)** — multi-tenant admin + billing.
- **I2 (Research Press)** — publication venue for outcome studies.
- **Legal**: per-jurisdiction counsel engagement.
- **Ethics board**: external recruitment.
- **Partner IRB**: independent; reviews pilot protocols.

## 3. Research / Programmatic Design

### 3.1 Pilot model

Each pilot follows a standard shape:

| Phase | Duration | Activity |
|---|---|---|
| Pre-study | 4 weeks | IRB approval; consent infrastructure; baseline surveys. |
| Intervention | 12 weeks | Participants engage with Josi companion; weekly reflection prompts. |
| Mid-point | 1 week | Interim survey + check-in interview. |
| Post-study | 4 weeks | Final survey; focus groups; data analysis. |
| Follow-up | 6 / 12 months | Retention surveys. |

Instruments:
- **WHO-5 Well-being Index** (5-item, validated).
- **DASS-21** (depression/anxiety/stress; validated).
- **UCLA Loneliness Scale** (for veterans pilot).
- **Custom qualitative interview protocol**.

### 3.2 Efficacy hypothesis

**Null:** participants report no significant change in wellness scores compared to waitlist control.
**H1:** participants show small-to-moderate positive change (Cohen's d ≥ 0.3) on composite wellness score vs waitlist control.

Analysis pre-registered on OSF (Open Science Framework). Power analysis pre-computes required n.

### 3.3 Ethics framework

The ethics board (separate from IRB) reviews:
- Voluntariness: are there coercion or perceived-coercion risks?
- Harm framework: what's the plausible harm pathway from astrology-reflection?
- Cultural fit: is astrology culturally appropriate in this context?
- Exit pathway: what happens to data if user withdraws mid-pilot?
- Disclaimer efficacy: do participants actually understand the scope?

No pilot proceeds without green light from both IRB (scientific-ethical) and Josi ethics board (program-design ethical).

### 3.4 Legal review checklist (per jurisdiction)

- Fortune-telling / divination laws (some US states, some EU countries restrict).
- Mental-health practice regulations (can this be construed as unlicensed counseling?).
- Education ministry rules (for school pilots).
- Consumer protection: what claims can be made vs not.
- Data protection (GDPR, CCPA, PDPA, DPDP Act).

### 3.5 Alternatives considered

| Alternative | Rejected because |
|---|---|
| B2C-only expansion with institutional marketing | Misses sticky institutional revenue; misses research pipeline. |
| Sell to institutions as unreviewed "wellness" product | Ethically unacceptable; reputationally catastrophic on first bad outcome. |
| Partner with existing EAP provider as white-label | Revisit later; Year 4 focuses on direct institutional relationships for ethics control. |
| Carceral pilots | Ethical complexity; explicitly out of scope Year 4. |

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| Which verticals in Year 4 | Schools (higher-ed, voluntary) + Veterans NGO + Corporate EAP | Balanced risk profile; diverse outcome data. |
| Outcome instruments | WHO-5 + DASS-21 + UCLA-L + qualitative | Validated, widely-used, interpretable. |
| Control arm | Waitlist control (not placebo — hard in reflection contexts) | Standard for behavioral intervention studies. |
| Ethics board composition | External ethicist + clinical psychologist + practicing classical astrologer | Balances perspectives. |
| Publication path | I2 Research Press primary; open to co-submission with academic journals | Builds I2; retains IP neutrality. |
| Program framing | "Structured reflection framework based on classical astrology" — not "spiritual counseling" | Legally safer; accurate. |
| Data ownership | Institutional tenant holds participant data; Josi processes; individuals retain rights | Standard B2G/B2NGO pattern; respects participant dignity. |
| Can institutions see individual participant data | No — aggregated only, k ≥ 20 per cohort stat | Prevents institutional misuse. |

## 5. Component Design

### 5.1 New services / modules

```
src/josi/institutions/
├── tenant_overlay/
│   ├── program.py                 # Program = institution cohort
│   ├── consent_institutional.py   # Multi-party consent (institution + individual)
│   └── data_boundary.py           # Institution can see aggregated only
├── measurement/
│   ├── instruments.py             # WHO-5, DASS-21, etc.
│   ├── survey_engine.py
│   └── analysis.py                # Pre/post comparisons
├── ethics/
│   ├── review_workflow.py         # Ethics board + IRB submission tracking
│   └── incident_logging.py        # Adverse-event log
└── admin/
    └── portal_api.py              # Institution admin endpoints
```

### 5.2 Data model additions

```sql
CREATE TABLE institution (
  institution_id UUID PK, display_name TEXT, vertical TEXT,
  jurisdiction_code TEXT, contact_email TEXT,
  contract_start TIMESTAMPTZ, contract_end TIMESTAMPTZ,
  status TEXT
);

CREATE TABLE program (
  program_id UUID PK, institution_id FK,
  name TEXT, start_date DATE, end_date DATE,
  irb_ref TEXT, ethics_board_ref TEXT,
  protocol_hash TEXT,
  status TEXT
);

CREATE TABLE program_enrollment (
  program_id FK, user_id FK,
  enrolled_at TIMESTAMPTZ, consent_doc_hash TEXT,
  withdrew_at TIMESTAMPTZ NULL,
  PRIMARY KEY (program_id, user_id)
);

CREATE TABLE program_survey_response (
  response_id UUID PK, program_id FK, user_id FK,
  instrument TEXT, administration TEXT, -- 'baseline'|'mid'|'post'|'6m'|'12m'
  responses JSONB, completed_at TIMESTAMPTZ
);

CREATE TABLE institutional_adverse_event (
  event_id UUID PK, program_id FK,
  reported_at TIMESTAMPTZ, severity TEXT,
  description TEXT, resolution JSONB NULL
);
```

### 5.3 API contract

```
# Institution admin
POST /api/v1/institutions
POST /api/v1/institutions/{id}/programs
GET  /api/v1/programs/{id}/aggregate-dashboard   # never individual
GET  /api/v1/programs/{id}/adverse-events

# Participant (uses regular companion APIs + this enrollment wrapper)
GET  /api/v1/programs/me
POST /api/v1/programs/{id}/withdraw
```

## 6. User Stories

### US-I7.1: As a veterans' wellness NGO director, I want to run a 12-week reflection program with Josi and measure outcomes
**Acceptance:** enroll cohort; deliver program; see aggregated pre/post scores; never see individual data.

### US-I7.2: As a participant in a school program, I want to engage voluntarily without my institution seeing my reflections
**Acceptance:** institution sees only aggregated metrics; participant owns journal; opt-out honored within 24 hours.

### US-I7.3: As an academic co-investigator, I want to run pre-registered analyses on pilot data
**Acceptance:** OSF pre-registration; de-identified dataset access (opt-in); analysis pipeline reproducible.

### US-I7.4: As the Josi ethics board, I want to review each proposed pilot before launch
**Acceptance:** structured review workflow with sign-off from 3 of 3 members; launch blocked without.

### US-I7.5: As legal counsel per jurisdiction, I want a checklist of regulatory items signed off before each country launch
**Acceptance:** checklist documented; sign-off immutable in audit log; no launch without.

### US-I7.6: As a participant withdrawing mid-pilot, I want clear data handling
**Acceptance:** withdrawal form; choice to delete or retain-but-anonymize; receipt within 7 days.

### US-I7.7: As an I2 editor, I want institutional study results published in the journal
**Acceptance:** pilot paper submission → peer review → publication cycle.

## 7. Tasks

### T-I7.1: Legal framework per initial jurisdictions
- **Definition:** Legal review for India, Nepal, US (state-by-state), UK pilot jurisdictions.
- **Acceptance:** Go/no-go per jurisdiction; checklist published.
- **Effort:** Q1–Q2.

### T-I7.2: Ethics board recruitment + charter
- **Definition:** Recruit 3 external members; write ethics charter; operational procedures.
- **Acceptance:** Charter ratified; first case (mock) reviewed end-to-end.
- **Effort:** Q1.

### T-I7.3: IRB partnership
- **Definition:** Contract external IRB for institutional-study protocols.
- **Acceptance:** First protocol submitted + approved.
- **Effort:** Q1.

### T-I7.4: Multi-party consent infrastructure
- **Definition:** Institution + individual consent flows; data-boundary enforcement in backend.
- **Acceptance:** Institution admin cannot query any individual record; audit log proves.
- **Effort:** Q2.

### T-I7.5: Measurement instruments
- **Definition:** WHO-5 + DASS-21 + UCLA-L + custom instruments implemented as structured surveys.
- **Acceptance:** Instrument validity preserved; scoring algorithms match published references.
- **Effort:** Q2.

### T-I7.6: Institution admin portal
- **Definition:** Next.js portal for enrolling cohorts; aggregated dashboards; adverse-event reporting.
- **Acceptance:** Full admin journey tested; data boundary enforced in E2E test.
- **Effort:** Q2–Q3.

### T-I7.7: Pilot #1 — schools (voluntary higher-ed in India)
- **Definition:** Partner with 1 university; recruit 100 volunteer participants; run 12-week pilot + follow-ups.
- **Acceptance:** Pilot completes per protocol; pre-registered analysis executed.
- **Effort:** Q3–Q4 + follow-ups in Year 5.

### T-I7.8: Pilot #2 — veterans NGO (US or UK)
- **Definition:** Similar structure; 50–80 participants.
- **Acceptance:** Pilot completes; adverse events handled per SOP.
- **Effort:** Q3–Q4.

### T-I7.9: Pilot #3 — corporate EAP
- **Definition:** Partner with 1 mid-size employer; voluntary opt-in employees.
- **Acceptance:** Pilot completes; ROI + wellness metrics reported.
- **Effort:** Q4.

### T-I7.10: First publication (I2)
- **Definition:** Pilot #1 results written up and submitted to I2.
- **Acceptance:** Paper accepted or revise-resubmit.
- **Effort:** Year 5 Q1–Q2.

## 8. Unit Tests

### 8.1 Data-boundary tests
| Test category | Representative names | Success target |
|---|---|---|
| Institution admin cannot access individual data | `test_admin_blocked_from_participant_journal` | 100% enforcement across API surface |
| Aggregation floor | `test_aggregate_stat_k_ge_20` | 100% of dashboard stats |
| Participant export not gated by institution | `test_participant_can_export_regardless_of_institution` | 100% |

### 8.2 Consent / withdrawal tests
| Test category | Representative names | Success target |
|---|---|---|
| Multi-party consent capture | `test_both_institution_and_individual_consent_required` | 100% |
| Withdrawal SLA | `test_withdrawal_processed_within_7_days` | ≥ 98% |
| Adverse-event logging | `test_adverse_event_immutable_audit` | 100% |

### 8.3 Measurement-instrument tests
| Test category | Representative names | Success target |
|---|---|---|
| Scoring accuracy | `test_who5_scoring_matches_reference` | 100% on known test cases |
| Missing-value handling | `test_dass21_handles_missing_items_per_spec` | 100% |

### 8.4 Ethics / IRB workflow tests
| Test category | Representative names | Success target |
|---|---|---|
| No pilot launch without dual sign-off | `test_launch_blocked_without_irb_and_ethics` | 100% |
| Protocol hash integrity | `test_protocol_hash_frozen_at_launch` | 100% immutability |

### 8.5 Outcome-study tests (programmatic)
| Test category | Representative names | Success target |
|---|---|---|
| Pre-registration lock | `test_analysis_plan_locked_prior_to_data_collection` | 100% of pilots pre-registered on OSF |
| Statistical power | `test_enrollment_meets_power_plan` | ≥ 90% of pilots hit n target |
| Efficacy detection | `test_pilot_1_detects_cohen_d_gte_0.3_if_present` | Target effect detection at 80% power |

### 8.6 Longitudinal retention tests
| Test category | Representative names | Success target |
|---|---|---|
| 12-week completion | `test_pilot_completion_rate` | ≥ 60% across pilots |
| 6-month follow-up response | `test_6m_followup_response_rate` | ≥ 40% |

## 9. EPIC-Level Acceptance Criteria

- [ ] Ethics board charter ratified; board seated.
- [ ] External IRB partnership signed.
- [ ] Legal framework documented for each launch jurisdiction.
- [ ] 3 pilots (schools + veterans NGO + corporate EAP) launched.
- [ ] Pilots complete per protocol with ≥ 60% completion.
- [ ] Aggregated dashboards operational; individual-data boundary enforced.
- [ ] Zero unhandled adverse events.
- [ ] At least 1 pilot paper submitted to I2.
- [ ] Institutional billing + multi-tenant overlay (from D9) in place.
- [ ] Public ethics statement + FAQ published on josi.com/institutions.

## 10. Rollout Plan

**Gate 0 — Legal + ethics readiness (Year 4 Q1):**
- No flag; preparatory only.
- **Gate to proceed:** legal green light per initial jurisdiction; ethics board operational.

**Gate 1 — Pilot #1 launch (Year 4 Q3):**
- School partner signed; IRB approval; 100 volunteers.
- **Gate to subsequent pilots:** first 4 weeks show no unmitigated adverse events.

**Gate 2 — Pilots #2 and #3 (Year 4 Q4):**
- Veterans NGO + corporate EAP.
- **Gate to scale expansion:** all 3 pilots complete and retained to 6-month follow-up.

**Gate 3 — Expansion to additional institutions (Year 5):**
- Based on published pilot results and regulatory readiness.
- **Gate to carceral pilots (if ever):** dedicated ethics framework + minimum 2 years of non-carceral track record.

**Rollback plan:** terminate a pilot mid-flight if adverse-event threshold tripped; participant data handled per consent preferences; institutional contract has pause clause.

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Adverse mental-health incident in pilot | Medium | Catastrophic | Clinical co-PI on each pilot; crisis-response pathway from I6; ethics review. |
| Institutional coercion (participant feels pressured) | Medium | High | Voluntariness audits; exit surveys; anonymized grievance channel. |
| Regulatory ruling classifies program as "counseling" | Low-Medium | High | Per-jurisdiction legal review; framing explicit and consistent. |
| Null or negative efficacy results | High | Medium (reputational) | Publish honestly; null results strengthen I2 credibility over long run. |
| Institutional misuse of aggregate data (e.g., cohort profiling) | Medium | High | k-floor enforcement; contractual use limitations; audit. |
| Cultural appropriation accusations | Medium | Medium | Co-design with tradition-authority partners; clear attribution. |
| Adverse press if a pilot underperforms or fails | Medium | Medium | Pre-commitment to publish regardless; transparency is the strategy. |
| Scaling institution tenant model overwhelms support | Medium | Medium | Caps on concurrent pilots; tiered SLA. |
| Academic partners lose interest after null results | Medium | Medium | Multi-year research relationships; co-authorship; research stipends. |
| Data breach of institutional PII | Low | Catastrophic | Tenant-isolated encryption; SOC 2 controls; bug bounty. |
| Conflicts between institution and individual data rights | Medium | Medium | Contract-codified: individual rights supersede institutional access. |
| Drift into "astrology as HR tool" (e.g., hiring) | Low | Catastrophic | Explicit contractual prohibition; refuse engagements that propose this. |

## 12. References

- Master spec: `docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md` — §7 non-goals on predictions + disclaimers.
- Related PRDs: I5, I1, I6, D9, I2, I9
- WHO-5 Well-being Index (Topp et al., 2015).
- DASS-21 (Lovibond & Lovibond, 1995).
- OSF pre-registration standards.
- Belmont Report principles.
- Applicable laws: GDPR, CCPA, PDPA, DPDP Act, per-state fortune-telling statutes (US).
