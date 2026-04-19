---
prd_id: I1
epic_id: I1
title: "Josi Academy — Structured Curriculum + AI Tutor"
phase: P6-institution
tags: [#extensibility, #end-user-ux, #astrologer-ux, #i18n, #ai-chat]
priority: must
depends_on: [D3, D8, E11b, P3-E2-console, I10]
enables: [I9, I2]
classical_sources: [bphs, saravali, phaladeepika, jataka_parijata, jaimini_sutras, tajaka_neelakanthi, kp_reader]
estimated_effort: 3-4 quarters (Year 3 Q1 through Year 4 Q1)
status: draft
author: "@claude"
last_updated: 2026-04-19
---

# I1 — Josi Academy (Structured Curriculum + AI Tutor)

## 1. Purpose & Rationale

Classical astrology knowledge is locked inside aging gurukulams, expensive in-person seminars, and unsearchable PDF scans of untranslated Sanskrit. New generations of practitioners cannot learn in a structured, verifiable, measurable way. Meanwhile, traditional schools face shrinking cohorts, no digital distribution, and no way to certify knowledge portably.

Josi Academy is the first structured, multi-tradition, AI-tutored astrology curriculum with paid certificates recognized by practicing astrologers and (eventually) an independent regulatory body (I9). It is the educational arm of Josi's category-creation strategy: if Josi defines the curriculum the next generation learns, Josi's conventions (source authority, aggregation, citation) become industry standard by default.

**Strategic value:**
- Revenue: subscription + per-course fees + certificate fees; diversifies away from B2C chart reading.
- Moat: students who learn on Josi become Josi astrologers; marketplace (D4) grows naturally.
- Research pipeline: Academy assessments (pass/fail per concept) feed I2 research on which classical techniques are learnable vs. internally inconsistent.
- Regulatory anchor: Academy graduates are the natural constituency for I9's certification body.

## 2. Scope

### 2.1 In scope
- Curriculum covering 6 traditions across 4 proficiency levels: Parashari (Foundations → Advanced → Pro → Master), Jaimini, KP, Tajaka/Varshaphala, Western (Hellenistic + Modern), Chinese/BaZi.
- Content formats: video lectures (recorded by partner gurus + Josi instructors), interactive text, chart-worked-examples tied to live engine, quizzes, capstone chart readings.
- AI tutor (built on Claude + RAG over classical corpus) that answers student questions in-context, references specific verses, and grades open-ended responses.
- Paid certificates at each level; verifiable via public certificate-ID URL.
- Assessment engine: MCQ, chart-interpretation rubric grading, practical exam (live chart reading reviewed by human TA).
- Partnerships with at least 3 traditional gurukulams (target: Krishnamurti Institute, Sagittarius Publications network, a Western/Hellenistic school).
- Learner dashboard, progress tracking, cohort-based live sessions for higher tiers.
- Multi-language delivery (English, Tamil, Hindi at launch; D3 unlocks further).

### 2.2 Out of scope
- Issuing regulatory licenses (deferred to I9).
- Generating novel content that blends classical + modern speculation (risks diluting authority; handled by opt-in "Josi Originals" track only after Year 5).
- University degree accreditation (too slow; Josi certs are portfolio credentials, not degrees).
- Free unlimited access (sustainability: freemium intro + paid advanced; scholarship program separate).

### 2.3 Dependencies
- **D3 (Localization)** — content rendered in 20+ languages; curriculum body must be i18n-ready.
- **D8 (Astrologer Certification)** — Academy graduation feeds into Josi Certified; tight coupling.
- **E11b (AI Chat Debate Mode)** — tutor reuses chat orchestration stack.
- **P3-E2-console** — non-engineer curriculum authors use authoring console.
- **I10 (10,000-yoga reference)** — Academy cross-links every yoga taught to the canonical entry.
- **Content licensing** with traditional schools; legal commitments.
- **Video production pipeline** (internal team + contracted post-production).

## 3. Classical / Technical Research

### 3.1 Curriculum design methodology

We adopt a **Bloom's Taxonomy × Classical Source authority** matrix. Each topic at each level targets a Bloom level (Remember → Understand → Apply → Analyze → Evaluate → Create). Classical content is sourced from dimension `source_authority` so every lesson cites verses in the same citation system as the engine.

Progression model per tradition:

| Level | Bloom target | Hours | Deliverable |
|---|---|---|---|
| Foundations | Remember + Understand | 40–60 | MCQ exam |
| Advanced | Apply + Analyze | 80–120 | 5 charts interpreted with rubric |
| Pro | Evaluate | 120–160 | Case study: longitudinal chart review |
| Master | Create | 160–200 | Capstone: original rule contribution to I10 registry |

### 3.2 AI tutor architecture

Built on Claude Opus with retrieval-augmented generation. Corpus:
- Classical texts (BPHS, Saravali, Phaladeepika, Jataka Parijata, Jaimini Sutras, Tajaka Neelakanthi, KP Reader, Hellenistic lots canon, BaZi classics) — chunked, embedded, stored in Qdrant collection `academy_corpus`.
- Curriculum lesson text (authoritative paraphrase by Josi + classical-advisor team).
- Live chart data via existing tool-use contracts (F10).

Grading flow:
1. Student submits open-ended response.
2. AI tutor generates rubric-based grade + justification.
3. If confidence < threshold (0.85) or grade is borderline, human TA reviews.

Guardrails: tutor cannot award certificates — only human-reviewed capstones can.

### 3.3 Partner gurukulam model

Each partner school:
- Contributes a designated "tradition authority" to curriculum committee.
- Records ~20 hours of video content (licensed to Josi, royalties per enrollment).
- Retains branding on their content module ("In partnership with Krishnamurti Institute").
- Can issue co-branded certificates.

Revenue share: 60% Josi / 40% partner on enrollment in their modules, with Academy overhead deducted first.

### 3.4 Alternatives considered

| Alternative | Rejected because |
|---|---|
| Free Khan-Academy-style open courseware | No revenue model; no credential value; dilutes partners. |
| Pure live cohort (bootcamp model) | Doesn't scale; pricing volatile; low margins. |
| License existing curricula as-is | No tradition is cross-mapped; no engine integration; no verification. |
| University accreditation path | 5–10 year timeline; not aligned with P6 window. |

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| Certificate authority in years 1–2 | Josi issues; independent recognition via I9 by Year 5 | Cannot wait for regulatory body; bootstrap with Josi reputation + partner co-brand. |
| Pricing model | Freemium intro + tiered subscription + per-certificate fee | Tests suggest learners pay for verifiable credentials; intro must be free for funnel. |
| Video vs text primary | Video for concepts, text for reference, interactive for practice | Established pedagogical pattern; matches watch-then-practice learning. |
| Do we build LMS or buy | Build on top of Josi auth + widgets + a thin LMS layer | Buying means data silo; building leverages chart engine natively. |
| Can AI tutor grade capstones | No — AI can pre-grade; humans finalize | Regulatory / ethics: automated certification unacceptable. |
| Multi-language content at launch | EN + TA + HI only; expand via D3 | Scope control for Year 3 launch. |

## 5. Component Design

### 5.1 New services / modules

```
src/josi/academy/
├── curriculum/
│   ├── models.py              # Course, Module, Lesson, Assessment, Enrollment
│   ├── repository.py
│   └── service.py
├── tutor/
│   ├── rag.py                 # Qdrant retrieval + Claude generation
│   ├── grading.py             # Rubric-based grading flows
│   └── guardrails.py          # Tutor ↔ chart engine tool-use
├── certification/
│   ├── issuance.py            # Certificate creation, signing
│   ├── verification.py        # Public /verify/{cert_id} endpoint
│   └── blockchain_anchor.py   # Optional: anchor cert hashes on-chain
└── progress/
    └── tracking.py            # Learner state machine

src/josi/api/v1/controllers/academy_controller.py
web/app/(academy)/                       # /academy/* routes in Next.js
```

### 5.2 Data model additions

```sql
CREATE TABLE academy_course (
  course_id UUID PRIMARY KEY,
  tradition TEXT NOT NULL,
  level TEXT NOT NULL CHECK (level IN ('foundations','advanced','pro','master')),
  title TEXT, description TEXT,
  partner_org_id UUID NULL,
  estimated_hours INT,
  price_usd NUMERIC(10,2),
  is_published BOOLEAN DEFAULT FALSE
);

CREATE TABLE academy_module (course_id FK, module_id UUID PK, seq INT, title TEXT, ...);
CREATE TABLE academy_lesson (module_id FK, lesson_id UUID PK, content_type TEXT, content_ref TEXT, ...);
CREATE TABLE academy_assessment (lesson_id FK, assessment_id UUID PK, rubric JSONB, ...);

CREATE TABLE academy_enrollment (
  user_id FK, course_id FK,
  enrolled_at TIMESTAMPTZ, completed_at TIMESTAMPTZ NULL,
  status TEXT,
  PRIMARY KEY (user_id, course_id)
);

CREATE TABLE academy_submission (
  submission_id UUID PK, user_id FK, assessment_id FK,
  response JSONB, ai_grade JSONB NULL, human_grade JSONB NULL,
  final_grade NUMERIC(5,2), graded_at TIMESTAMPTZ
);

CREATE TABLE academy_certificate (
  cert_id UUID PK, user_id FK, course_id FK,
  issued_at TIMESTAMPTZ, cert_hash TEXT UNIQUE,
  public_url TEXT, partner_cobrand BOOLEAN,
  revoked_at TIMESTAMPTZ NULL
);
```

### 5.3 API contract

```
GET  /api/v1/academy/courses                             # catalogue
POST /api/v1/academy/courses/{id}/enroll
GET  /api/v1/academy/enrollments/me
POST /api/v1/academy/submissions
GET  /api/v1/academy/tutor/ask                           # streamed SSE
GET  /verify/{cert_id}                                   # public cert verify
```

## 6. User Stories

### US-I1.1: As a learner in Chennai with no formal astrology education, I want a structured Parashari Foundations course so I can progress without needing a guru in person
**Acceptance:** enroll, complete 40 hours, pass MCQ, receive Level-1 cert; total time-to-cert < 90 days.

### US-I1.2: As a PhD student researching astrological accuracy, I want anonymized aggregate data on which yogas students find hardest to grasp
**Acceptance:** I2 research dashboard exposes per-yoga pass rates over cohort; anonymized; IRB-compliant.

### US-I1.3: As a traditional gurukulam owner, I want my teachings distributed globally while retaining attribution and royalties
**Acceptance:** partnership portal shows live enrollment, revenue share, content usage metrics; branded module module pages.

### US-I1.4: As a working astrologer seeking career advancement, I want a Pro certification that marketplace users recognize
**Acceptance:** Pro cert appears on astrologer profile (D4/D8); filter "Josi-certified Pro" returns only verified; verified by public URL.

### US-I1.5: As a stuck learner, I want a tutor available 24/7 that references specific verses when I'm confused
**Acceptance:** ask a question about Raja Yoga; response cites BPHS verses, shows a live chart example, answers in my preferred language.

### US-I1.6: As the head of a professional association, I want to negotiate curriculum equivalency with Josi Academy
**Acceptance:** API + formal review process for external bodies to map their syllabus to Josi levels.

## 7. Tasks

### T-I1.1: Curriculum spec (all 6 traditions, 4 levels = 24 course specs)
- **Definition:** Each course spec covers learning outcomes, module list, citation map to classical_rule registry, hour estimate, assessment blueprint.
- **Acceptance:** 24 course specs reviewed by classical advisors; signed off by partner leads.
- **Effort:** Q1 (12 weeks, cross-functional curriculum team).

### T-I1.2: Partner agreements (3 launch partners)
- **Definition:** Legal agreements signed; content delivery SLAs; royalty terms; branding rules.
- **Acceptance:** 3 signed MOUs; content calendar agreed.
- **Effort:** Q1–Q2 (parallel to T-I1.1).

### T-I1.3: Video production pipeline
- **Definition:** Record-edit-caption-QA-publish pipeline with i18n subtitles.
- **Acceptance:** 100 hours of content delivered for Foundations tier across all 6 traditions.
- **Effort:** Q1–Q2.

### T-I1.4: LMS backend + frontend
- **Definition:** Schema + APIs above; Next.js routes under `/academy`; progress tracking; video player with DRM.
- **Acceptance:** full learner journey end-to-end passes Playwright tests.
- **Effort:** Q1–Q2.

### T-I1.5: AI tutor RAG pipeline
- **Definition:** Corpus ingestion → chunking → embedding → Qdrant; tutor service with tool-use integration; guardrails.
- **Acceptance:** tutor answers 50 benchmark questions with citation; cite-accuracy ≥ 90% on held-out eval set.
- **Effort:** Q2.

### T-I1.6: Assessment + grading
- **Definition:** AI pre-grading + human TA review workflow; rubric editor; submission pipeline.
- **Acceptance:** median grading turnaround < 72 hours; inter-rater agreement (AI vs human) ≥ 0.8 Cohen's κ.
- **Effort:** Q2.

### T-I1.7: Certification issuance + verification
- **Definition:** Signed certificates (PDF + public verify URL); optional blockchain anchor; revocation flow.
- **Acceptance:** certificate verifiable by URL 1 year later; revoked cert shows revoked status.
- **Effort:** Q3.

### T-I1.8: Launch operations
- **Definition:** Pricing, billing, support, scholarship program, marketing launch.
- **Acceptance:** 1,000 enrollments in month 1 of public launch.
- **Effort:** Q3–Q4.

### T-I1.9: Cohort-based Pro live sessions
- **Definition:** Weekly live sessions for Pro cohorts with guest gurus; recording + transcript.
- **Acceptance:** cohort of 20 finishes Pro course with ≥ 70% completion rate.
- **Effort:** Q4 and ongoing.

## 8. Unit Tests

Per master spec guidance: test CATEGORIES and representative names + success targets (specific thresholds TBD at phase start).

### 8.1 Curriculum completion rate tests
| Test category | Representative names | Success target |
|---|---|---|
| Foundations completion | `test_foundations_parashari_cohort_completion_rate` | ≥ 60% of enrolled complete Module 1 within 30 days |
| Pass-through to Advanced | `test_advanced_conversion_from_foundations` | ≥ 30% of Foundations grads enroll in Advanced |
| Drop-off diagnostics | `test_dropoff_at_module_boundaries` | No single module shows > 40% drop in historical cohort |

### 8.2 AI tutor quality tests
| Test category | Representative names | Success target |
|---|---|---|
| Citation accuracy | `test_tutor_cites_verse_for_raja_yoga_question` | ≥ 90% of tutor responses citing classical content reference a real verse in corpus |
| Hallucination guardrail | `test_tutor_refuses_out_of_corpus_question` | ≥ 95% refusal rate for questions outside Academy scope |
| Language parity | `test_tutor_answer_quality_by_language` | Grading variance across EN/TA/HI ≤ 10% on held-out set |
| Tool-use chart integration | `test_tutor_invokes_chart_engine_for_live_example` | 100% of lesson-example questions surface live chart data |

### 8.3 Assessment grading tests
| Test category | Representative names | Success target |
|---|---|---|
| AI-human agreement | `test_ai_prescore_vs_human_final_agreement` | Cohen's κ ≥ 0.8 across 500 graded submissions |
| Rubric coverage | `test_rubric_all_criteria_evaluated` | 100% of final grades have evaluations per rubric dimension |
| Borderline routing | `test_borderline_submissions_route_to_human` | 100% of submissions with AI confidence < 0.85 reach human TA |

### 8.4 Certification integrity tests
| Test category | Representative names | Success target |
|---|---|---|
| Public verify | `test_cert_public_url_verifies` | 100% of issued certs verify via public URL after 1 year (archival retention test) |
| Revocation | `test_revoked_cert_shows_revoked_status` | Revoked status propagates within 1 minute |
| Anti-forgery | `test_cert_hash_validates_against_body` | 0% false-positive verification of mutated cert |

### 8.5 Knowledge retention tests (longitudinal)
| Test category | Representative names | Success target |
|---|---|---|
| 6-month retention | `test_foundations_6_month_retention_quiz` | ≥ 70% of graduates pass surprise retention quiz at 6 months |
| 12-month retention | `test_advanced_12_month_retention_quiz` | ≥ 60% of Advanced graduates pass at 12 months |

## 9. EPIC-Level Acceptance Criteria

- [ ] 24 course specs authored and peer-reviewed.
- [ ] 3 partner gurukulams live with at least one tradition each.
- [ ] Full learner journey (enroll → lesson → assessment → cert) works end-to-end in EN, TA, HI.
- [ ] AI tutor citation accuracy ≥ 90% on eval set.
- [ ] 1,000 enrolled learners in first month of public launch.
- [ ] Foundations-to-Advanced conversion ≥ 30%.
- [ ] Public cert verify URL operational and indexed by search engines.
- [ ] Revenue sharing to partners automated and audited.
- [ ] Accessibility: all video captioned; keyboard-navigable; WCAG 2.1 AA.
- [ ] IRB-reviewed research data export (opt-in) feeding I2.

## 10. Rollout Plan

Phased with learning gates. Specific dates TBD at phase start; gates are decision criteria, not dates.

**Gate 0 — Closed alpha (Year 3 Q2):**
- Feature flag: `academy_enabled` (off for all except alpha cohort).
- 50 invited learners; Parashari Foundations only.
- **Gate to proceed:** ≥ 70% cohort finishes Module 1; tutor quality ≥ 85% satisfaction.

**Gate 1 — Partner open beta (Year 3 Q3):**
- All 3 partners live; Foundations tier across all 6 traditions.
- 500 beta learners, priced at 50% off.
- **Gate to proceed:** no critical grading disputes; cert-verification infra stable; NPS ≥ 40.

**Gate 2 — Public launch (Year 3 Q4):**
- Full marketing launch; Foundations + Advanced tiers.
- **Gate to proceed to Pro tier:** first 500 Advanced-cert graduates employed in marketplace (D4) with measurable revenue impact.

**Gate 3 — Pro + Master tiers (Year 4):**
- Cohort-based, price-premium.
- **Gate to proceed to I9 alignment:** at least 2 recognized professional associations formally recognize Josi certs.

**Rollback plan:** feature flag disables Academy routes; existing enrolled learners get pro-rata refunds; content archive preserved.

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Partner gurukulams pull out due to content disputes | Medium | High | Robust MOUs with exit + content-use continuation rights; cultivate 5+ partners so 1–2 exits don't break curriculum. |
| AI tutor hallucinates verse citations, damaging credibility | Medium | Catastrophic | Hard RAG guardrails; every cite validated against corpus pre-emission; human review of tutor benchmarks each release. |
| Regulatory classification of Academy certs as "medical advice" or similar in certain jurisdictions | Low-Medium | High | Legal review per jurisdiction; strong disclaimers; I7 separate legal track. |
| Translation quality issues erode trust in non-English markets | Medium | Medium | Native-speaker classical-advisor review per language; community correction channels. |
| Certificate forgery / scraping | Low | Medium | Cryptographic signing; optional blockchain anchor; rate-limit verify API. |
| Scope creep: 24 courses × high quality = execution drag | High | High | Strict prioritization: Parashari Foundations must ship alone if needed; partner tiers phased. |
| Ethical concern: astrology as "education" misrepresenting scientific standing | Low | Medium | Explicit framing as "classical knowledge tradition", not science; disclaimers per lesson. |
| Revenue miss (under-monetization vs costs) | Medium | High | Staged pricing experiments; no all-or-nothing commitments; partner royalties capped on published schedule. |
| Cohort-based Pro live sessions scale poorly | Medium | Medium | Cap cohort size (20); waitlist; record for async replay. |
| Academy data breach (PII of learners) | Low | High | Encrypted PII at rest; audit logs; SOC 2 alignment per I11 readiness. |

## 12. References

- Master spec: `docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`
- Related PRDs: D3, D8, E11b, P3-E2-console, I9, I10, I2
- Bloom, B. S. (1956). *Taxonomy of Educational Objectives*.
- Krishnamurti Institute (KP) curriculum artifacts (licensed).
- Edu-tech teardown: Coursera, Masterclass, Outschool models.
