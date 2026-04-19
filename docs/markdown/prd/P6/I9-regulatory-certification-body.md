---
prd_id: I9
epic_id: I9
title: "Regulatory / Certification Body — Global Standards for Classical Astrology"
phase: P6-institution
tags: [#multi-tenant]
priority: could
depends_on: [I1, I2, I3, D8]
enables: [I11]
classical_sources: []
estimated_effort: 6+ quarters (Year 4 through Year 5, ongoing thereafter)
status: draft
author: "@claude"
last_updated: 2026-04-19
---

# I9 — Regulatory / Certification Body

## 1. Purpose & Rationale

Classical astrology has no globally-recognized practice standards. Credentials are fragmented: ISAR, NCGR, AFA, Council of Vedic Astrology, ICAS, Sagittarius Publications associations, Krishnamurti affiliates, and dozens of regional bodies each certify their own — often with no reciprocity, inconsistent rigor, and no measurable standards-of-practice. Consumers cannot easily distinguish an expert from a novice. Disputes have no forum. Ethics breaches have no consequence.

I9 proposes convening these fragmented bodies into a **Global Council on Classical Astrological Practice** (working name), with Josi acting as **technical secretariat / backbone**, not as the certifier. This is important: Josi does not own the body. Josi builds and maintains the infrastructure (rule registries, verification APIs, communications platform), while governance and certification decisions rest with the Council.

Think "CFA Institute for astrology": annual certifications, code of ethics, continuing education, disciplinary process, reciprocity agreements across traditions.

**Strategic value:**
- Category definition: whoever writes the standards shapes the industry.
- Legitimization: professional astrologers benefit from recognized credentials; unprofessional actors face accountability.
- Natural extension of I1 Academy (graduation → certification pathway) and D8 (Josi Certified).
- Protects consumers (public good; regulatory goodwill).
- Long-term: establishes precedent for I11 (acquisition / IPO legitimacy).

**Strategic risk it mitigates:** a government (especially in India, where astrology regulation periodically flares as a political issue) decides to regulate astrology top-down with no industry input. Early self-regulation via I9 gives the industry a voice before that happens.

## 2. Scope

### 2.1 In scope
- Governance: Council board of 11–15 members drawn from existing recognized associations + independent experts + at-large members.
- Bylaws and code of ethics (adopted, publicly published).
- Certification tiers: Associate, Practitioner, Fellow, Master. Each tier with clear criteria (exam + experience + continuing ed).
- Disciplinary process: complaint intake, investigation, sanctions, appeals.
- Continuing education (CE) requirements: ~20 hours/year via I1 Academy, partner schools, conferences.
- Public verify portal: "Is this astrologer certified?" → verification URL per certificate.
- Reciprocity agreements: recognized external credentials map to Council tiers.
- Code of conduct: consumer interactions, confidentiality, disclaimers, conflict of interest.
- Annual conference / convention.
- Josi as technical backbone:
  - Certification issuance infrastructure (public verify URLs, cryptographic signing).
  - Member / applicant registry.
  - CE tracking.
  - Complaint portal.
  - Examination delivery (proctored via partner).
- Multi-jurisdiction consideration (each major country may need local chapter).

### 2.2 Out of scope
- Josi as certifying authority (Josi is *technical* backbone only; Council owns certification decisions).
- Licensing astrologers as medical/psychological practitioners (separate legal regime).
- Consumer mediation / arbitration (Council handles ethics, not commercial disputes).
- Forcing Josi-only conventions on the industry (Council independence is the selling point).
- Replacing or delegitimizing existing associations (we aim to federate).

### 2.3 Dependencies
- **I1 (Academy)** — provides curriculum foundation; Academy certs can count toward Council tiers.
- **I2 (Research Press)** — source for evidence-based standard-setting.
- **I3 (Open-source engine)** — neutral technical substrate Council can endorse.
- **D8 (Astrologer certification)** — Josi Certified can map to Council tiers.
- **Convening work**: heavy external relationship-building; 12–18 months of pre-launch outreach.
- **Legal**: 501(c)(3)-equivalent nonprofit incorporation; international legal structure.
- **Independent executive director** hired by Council.

## 3. Governance Research

### 3.1 Council structure

Modeled on professional-body best practices (CFA Institute, IEEE, American Bar Association, Project Management Institute):

| Body | Composition | Role |
|---|---|---|
| **Board of Directors** | 11–15 members: 7 from federated associations (one each), 4 at-large elected, 3 independent expert (ethicist, statistician, legal) | Strategic governance |
| **Standards Committee** | 7 members drawn from board + external | Technical standards, examination content |
| **Ethics Committee** | 5 members | Code of ethics, disciplinary procedures |
| **Education Committee** | 5 members | Curriculum / CE standards |
| **Nominating Committee** | 5 members | Board elections |

Terms: 3-year, staggered. Chair elected by board.

Josi as technical backbone:
- Josi seats 1 non-voting observer on the Board (disclosed; for coordination).
- Josi staff run the secretariat (operations) with Council-defined scope.
- Josi's technical decisions (hosting, engine, UI) advised by Standards Committee.

### 3.2 Certification tiers

| Tier | Prerequisites | Exam | Experience | CE |
|---|---|---|---|---|
| **Associate** | I1 Foundations (or equivalent) | 100 MCQ | None | 10h/yr |
| **Practitioner** | I1 Advanced + 2 yrs consulting | 150 MCQ + case studies | 200 hrs consulting documented | 20h/yr |
| **Fellow** | Practitioner + 5 yrs | Advanced case studies + oral exam | 1000 hrs | 30h/yr |
| **Master** | Fellow + 10 yrs + published work / taught Academy | Teaching portfolio + peer review | 2000 hrs + teaching | 40h/yr |

Examinations administered by external proctor partner (e.g., Pearson VUE equivalent); no Josi-side content influence.

### 3.3 Code of ethics (headline items)

- Confidentiality of client information.
- Disclosure: astrology as classical framework, not medical/legal/financial advice.
- No financial/medical/legal advice; direct to licensed professionals.
- No exploitation of emotionally vulnerable clients.
- Transparent pricing.
- Competence: do not practice beyond training.
- Continuing education obligations.
- Disciplinary cooperation when investigated.

### 3.4 Relationship to existing associations

Two postures:
- **Federation**: existing associations maintain identity; grant mutual recognition; Council serves as federation umbrella. Members pay existing dues + Council dues (discounted if federated).
- **Reciprocity without absorption**: existing credentials recognized at specific tiers (e.g., ISAR CAP = Practitioner; NCGR Level IV = Fellow).

Josi's default stance: **federation with reciprocity**. Never absorption. Existing bodies must feel their heritage is respected.

### 3.5 Alternatives considered

| Alternative | Rejected because |
|---|---|
| Josi certifies directly under Josi brand | Kills industry-wide adoption; concentrates power inappropriately. |
| Wait for government regulation | Cedes agenda; likely worse outcomes. |
| Informal guild with no teeth | Ethics enforcement needs structure. |
| Multi-national federation with no central body | Fragmentation replicates existing problem. |

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| Legal form | Independent nonprofit incorporated (likely Delaware, US 501(c)(3) or analog) | Credibility; international operation; tax-exempt where possible. |
| Josi board seat | Observer only, non-voting | Preserves Council independence. |
| Fee model | Annual dues + certification fees + CE fees; Josi funds infrastructure at cost for first 3 years | Council must be self-sustaining long-term. |
| Relation to I1 | I1 is one path to certification but not exclusive | Avoids conflict of interest appearance. |
| Complaint jurisdiction | Members only; non-member actors referred to local consumer protection | Scope realism. |
| Discipline severity | Reprimand / suspension / revocation | Standard for professional bodies. |
| Multi-jurisdiction strategy | Start with US + India + UK; expand | Concentrated member density; established legal regimes. |
| Branding | Not "Josi Council"; neutral name (e.g., "Global Council on Classical Astrological Practice" or similar — TBD by Council) | Independence signal. |

## 5. Component Design

### 5.1 New services / modules

```
src/josi/council/
├── registry/
│   ├── member.py                  # Member + applicant records
│   └── credential.py              # Cert issuance + verification
├── ce_tracking/
│   └── accruals.py
├── ethics/
│   ├── complaint_intake.py
│   └── case_workflow.py
├── examination/
│   └── proctor_integration.py     # Pearson VUE-style external
└── reciprocity/
    └── external_credential_map.py

web/app/council/                   # Public-facing Council portal
web/app/(internal)/council-admin/  # Secretariat UI
```

### 5.2 Data model additions

```sql
CREATE TABLE council_member (
  member_id UUID PK, user_id FK NULL, -- nullable if non-Josi user
  full_name TEXT, email TEXT UNIQUE,
  country TEXT, home_association TEXT,
  tier TEXT, joined_at TIMESTAMPTZ,
  status TEXT -- 'active','suspended','revoked','lapsed'
);

CREATE TABLE council_credential (
  credential_id UUID PK, member_id FK,
  tier TEXT, issued_at TIMESTAMPTZ, expires_at TIMESTAMPTZ,
  credential_hash TEXT UNIQUE, public_verify_url TEXT,
  external_credential_ref TEXT NULL  -- if granted via reciprocity
);

CREATE TABLE council_ce_record (
  record_id UUID PK, member_id FK,
  activity_type TEXT, hours NUMERIC, provider TEXT,
  completed_at DATE, verified BOOLEAN
);

CREATE TABLE council_complaint (
  complaint_id UUID PK, complainant_email TEXT,
  respondent_member_id FK, filed_at TIMESTAMPTZ,
  summary TEXT, status TEXT,
  resolution JSONB NULL
);

CREATE TABLE council_reciprocity_mapping (
  external_body TEXT, external_credential TEXT,
  council_tier TEXT, effective_from DATE, effective_to DATE NULL,
  PRIMARY KEY (external_body, external_credential)
);
```

### 5.3 API contract

```
GET  /api/v1/council/members/search     # public: by name / country
GET  /verify/council/{credential_id}    # public verify
POST /api/v1/council/applications
POST /api/v1/council/ce/accrue
POST /api/v1/council/complaints
GET  /api/v1/council/reciprocity
```

## 6. User Stories

### US-I9.1: As the head of ICAS, I want my association to federate with the Council without losing identity
**Acceptance:** MOU template; ICAS certifications mapped to Council tiers; members pay both bodies if they choose.

### US-I9.2: As a working astrologer, I want a single credential that's recognized across countries
**Acceptance:** Council certificate verifiable in US, India, UK; reciprocity live.

### US-I9.3: As a consumer hiring an astrologer, I want to verify their credential
**Acceptance:** URL + QR code verify; name, tier, CE compliance status, disciplinary status all visible.

### US-I9.4: As a client who experienced misconduct, I want to file a complaint
**Acceptance:** complaint portal; confidential intake; acknowledgment within 72h; resolution SLA documented.

### US-I9.5: As the Council's executive director, I want operational dashboards without being a Josi employee
**Acceptance:** secretariat UI accessible under Council domain; Josi staff accountable to executive director for operational SLA.

### US-I9.6: As an examining body (Pearson VUE equivalent), I want a clean proctoring integration
**Acceptance:** standardized exam delivery via API; results flow to credential system; no grade tampering possible.

### US-I9.7: As a regulator in India exploring astrology-industry standards, I want a credible body to engage
**Acceptance:** Council public positioning + annual report engage regulators constructively.

## 7. Tasks

### T-I9.1: Convening + federation outreach
- **Definition:** Identify and engage major existing associations; workshop series to align on Council formation.
- **Acceptance:** MOUs signed by ≥ 5 associations to participate in founding.
- **Effort:** Year 4 Q1–Q3 (external relationship work).

### T-I9.2: Legal incorporation
- **Definition:** Nonprofit incorporation; bylaws; charter.
- **Acceptance:** Legal entity operational in at least US + India.
- **Effort:** Year 4 Q2–Q3.

### T-I9.3: Founding board election
- **Definition:** Initial nominations; election process.
- **Acceptance:** Board seated; chair elected; first meeting held.
- **Effort:** Year 4 Q4.

### T-I9.4: Code of ethics + bylaws adoption
- **Definition:** Drafting + Council adoption.
- **Acceptance:** Publicly published; ratified by board vote.
- **Effort:** Year 4 Q4.

### T-I9.5: Certification tiers + examination design
- **Definition:** Exam blueprint; question banks; proctor integration.
- **Acceptance:** First pilot exam administered to 50 candidates.
- **Effort:** Year 5 Q1.

### T-I9.6: Registry + verification portal
- **Definition:** Data model + public portal + cryptographic verify.
- **Acceptance:** Verify URL works end-to-end; revocation propagates < 24h.
- **Effort:** Year 5 Q1.

### T-I9.7: Reciprocity mappings
- **Definition:** Formal mappings for existing body credentials.
- **Acceptance:** ≥ 10 external credentials mapped; announced jointly.
- **Effort:** Year 5 Q1–Q2.

### T-I9.8: Complaints + disciplinary infrastructure
- **Definition:** Portal + workflow; Ethics Committee processes.
- **Acceptance:** First complaint processed end-to-end; confidentiality preserved.
- **Effort:** Year 5 Q2.

### T-I9.9: First annual conference
- **Definition:** Convening of member associations + practitioners.
- **Acceptance:** ≥ 300 attendees; signed reciprocity announcements.
- **Effort:** Year 5 Q3.

### T-I9.10: Independence plan (3-year Josi-funded horizon)
- **Definition:** Financial model toward self-sustainability by Year 7.
- **Acceptance:** Audited financials; transition plan.
- **Effort:** Ongoing; first milestone Year 5 Q4.

## 8. Unit Tests

### 8.1 Verification-portal tests
| Test category | Representative names | Success target |
|---|---|---|
| Public verify | `test_cert_public_verify_url_renders_status` | 100% uptime on verify endpoint |
| Revocation propagation | `test_revoked_cert_shows_within_24h` | ≥ 99% within 24h |
| Reciprocity resolve | `test_external_credential_maps_to_council_tier` | 100% per mapping table |

### 8.2 CE-tracking tests
| Test category | Representative names | Success target |
|---|---|---|
| CE accrual | `test_ce_hours_accrue_correctly` | 100% |
| Lapse detection | `test_member_lapses_when_ce_insufficient` | 100% within monthly sweep |

### 8.3 Complaint-workflow tests
| Test category | Representative names | Success target |
|---|---|---|
| Acknowledgement SLA | `test_complaint_acknowledged_within_72h` | ≥ 98% |
| Confidentiality | `test_complainant_identity_not_exposed_to_respondent_by_default` | 100% |
| Audit integrity | `test_workflow_steps_immutable` | 100% |

### 8.4 Governance-integrity tests
| Test category | Representative names | Success target |
|---|---|---|
| Josi observer non-voting | `test_josi_observer_cannot_record_vote` | 100% |
| Board quorum | `test_actions_require_quorum` | 100% |
| Term limits | `test_board_seats_expire_per_term` | 100% |

### 8.5 Exam-integrity tests
| Test category | Representative names | Success target |
|---|---|---|
| No Josi grade tampering | `test_proctor_results_immutable_after_receipt` | 100% |
| Question-bank integrity | `test_exam_questions_sampled_per_blueprint` | 100% |

### 8.6 Adoption metrics (longitudinal)
| Test category | Representative names | Success target |
|---|---|---|
| Federated associations | `test_federated_associations_count` | ≥ 5 by Year 5 end |
| Certified members | `test_active_certified_members` | ≥ 1000 by Year 5 end |
| Reciprocity coverage | `test_reciprocity_country_coverage` | ≥ 10 countries by Year 5 end |

## 9. EPIC-Level Acceptance Criteria

- [ ] Council legally incorporated as independent nonprofit.
- [ ] ≥ 5 founding associations federated.
- [ ] Bylaws and code of ethics publicly ratified.
- [ ] Initial board seated and chair elected.
- [ ] All 4 certification tiers live with examination infrastructure.
- [ ] Public verification portal operational.
- [ ] ≥ 10 external credentials reciprocated.
- [ ] Complaints + disciplinary workflow operational.
- [ ] First annual conference executed.
- [ ] Josi's role as technical backbone documented and audited; no conflict-of-interest incidents.
- [ ] Path to financial self-sustainability by Year 7 Q4 documented.

## 10. Rollout Plan

**Gate 0 — Convening (Year 4 Q1–Q3):**
- No technical launch; relationship-building only.
- **Gate to proceed:** ≥ 3 founding associations express intent in writing.

**Gate 1 — Incorporation + board (Year 4 Q4):**
- Legal entity; board seated.
- **Gate to proceed:** bylaws + code of ethics adopted.

**Gate 2 — Certification infrastructure live (Year 5 Q1):**
- Registry + verify portal + first pilot exam.
- **Gate to proceed:** 50 successful certifications issued.

**Gate 3 — Public launch (Year 5 Q3):**
- Annual conference; reciprocity announcements; full public portal.
- **Gate to self-sustainability:** financial plan on track.

**Gate 4 — Josi subsidy wind-down (Year 6–7):**
- Progressive reduction; Council funded by dues + fees.

**Rollback plan:** if Council fails to coalesce, retain domain + infrastructure as archive; D8 Josi Certified continues standalone; no participant-facing data loss.

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Existing associations refuse to federate | High | High | Heavy diplomatic work; reciprocity posture; low-friction on-ramp; avoid absorption. |
| Council perceived as Josi proxy | Medium | Catastrophic | Non-voting observer only; neutral branding; independent ED; transparent audit of technical backbone. |
| Internal Council politics / factions | High | Medium | Clear bylaws; term limits; disciplinary processes apply to board. |
| Government steps in with regulation before Council gels | Medium | High | Accelerate founding; engage regulators early; Council speaks for industry. |
| Legal liability for disciplinary actions | Medium | High | Robust due process; legal defense reserves; insurance. |
| Consumer protection gaps (complaints unresolved) | Medium | Medium | SLA + audit; external consumer-advocate on Ethics Committee. |
| Josi conflict of interest accusations | High | High | Full disclosure; independent oversight; Josi recuses from any decisions affecting its commercial interest. |
| Reciprocity disputes (which external cred = which tier) | Medium | Medium | Standards Committee + appeals process. |
| Low exam pass rate suggests standards too high / calibration issues | Medium | Medium | Pilot with psychometric review; adjust blueprints iteratively. |
| Financial dependence on Josi past Year 7 | Medium | Medium | Clear transition milestones; contingent grant-seeking. |
| Cultural fit: Western-style regulatory body imposed on diverse traditions | Medium | High | Strong representation from Asian traditions on board; translated bylaws; regional chapters. |
| Disciplinary process weaponized by bad actors | Medium | Medium | Complaint vetting; vexatious-complaint policies. |
| Member privacy breach in registry | Low | High | Public info minimized; sensitive data encrypted; audit. |

## 12. References

- Master spec: `docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`
- Related PRDs: I1, I2, I3, D8, I11
- CFA Institute bylaws + code of ethics (exemplar).
- IEEE code of ethics (exemplar).
- Project Management Institute certification model.
- ISAR, NCGR, AFA, ICAS, Council of Vedic Astrology (existing bodies to federate).
