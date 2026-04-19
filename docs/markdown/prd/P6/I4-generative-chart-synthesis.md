---
prd_id: I4
epic_id: I4
title: "Generative Chart Synthesis — AI-Composed Divisional Charts"
phase: P6-institution
tags: [#ai-chat, #extensibility, #correctness, #experimentation]
priority: should
depends_on: [E7, I2, I3, Reference-1000, I10]
enables: [I5]
classical_sources: [bphs, jaimini_sutras]
estimated_effort: 3-4 quarters (Year 4)
status: draft
author: "@claude"
last_updated: 2026-04-19
---

# I4 — Generative Chart Synthesis

## 1. Purpose & Rationale

All existing divisional charts (vargas D1–D144, Sarvatobhadra, etc.) are classical: composed centuries ago with specific life-domain mappings (D10 for career, D7 for children, D9 for spouse, etc.). The classical set covers many — but not all — plausible life-domain decompositions a modern user might want: "startup founding readiness", "climate-adaptation resilience", "cross-cultural relocation viability", etc.

I4 proposes an AI system that *composes novel divisional charts from stated principles*. A user or researcher states: "compose a varga that highlights indicators relevant to software engineering careers." The system reasons from:
- Classical precedent (D10 for career; its harmonic logic)
- Stated target domain
- Planet/house/sign affinities in that domain (trained from classical corpus)
- Validation against outcome data (where available, opt-in)

It proposes a harmonic number, aspect weighting, and chart-construction rule. Novel vargas go through a **rigorous editorial review** before being published to the registry. This is part research tool (for I2), part product feature (for Ultra AI users and Pro astrologers).

**Strategic value:**
- Distinctive capability no competitor can replicate (requires the data + rule engine + LLM stack).
- Generates research output: every accepted novel varga is a potential publication.
- Positions Josi as pushing the frontier of classical astrology rather than merely digitizing it.
- Advances I10 (growing the comprehensive catalogue beyond classically-enumerated set).

## 2. Scope

### 2.1 In scope
- A generative model (LLM-based, likely Claude Opus with retrieval over I3 OSS rule corpus) that proposes:
  - Varga harmonic (divisor n)
  - Planet-weighting scheme
  - House-role reassignment
  - Justification paragraph citing classical precedents
- Editorial review workflow for submitted novel charts (analogous to I2 peer review but faster).
- A sandbox where Josi internal team + select Pro astrologers can experiment with novel vargas.
- Validation harness: for any proposed varga, auto-run it against a labeled outcome dataset (where available, opt-in from user research consent per D7) and report predictive performance.
- Publication pathway: accepted novel vargas merge into the rule registry (I3) as "generated" source authority, distinct from classical sources.
- Rollback / deprecation of novel vargas that fail ongoing validation.
- Community submission: external researchers can propose novel vargas via I3 repo; same editorial review.

### 2.2 Out of scope
- Fully automatic publication without human review (ethical + correctness risk).
- Mixing novel-generated rules with classical rules under the same `source_id` (would violate master spec §7).
- Generating novel yogas (that's I10's rule-registry growth, not I4).
- Generating novel dasas (extension; not initial scope; can follow once varga synthesis is validated).
- Real-time generation visible to end-users in Auto mode (only Pro astrologers + Ultra AI mode).

### 2.3 Dependencies
- **E7 (Extended Vargas + Sarvatobhadra + Upagrahas)** — the existing classical varga baseline.
- **I2 (Research Press)** — publication venue for accepted novel vargas.
- **I3 (Open-source engine)** — rule registry into which novel vargas are merged.
- **Reference-1000 + I10** — the rule corpus the LLM reasons over.
- **D7 (Research Data API)** — outcome data for validation.
- **Editorial board** (separate from I2 — domain experts in divisional-chart theory).

## 3. Classical / Technical Research

### 3.1 How classical vargas are constructed (priors for generation)

The classical vargas follow a small set of construction patterns:

| Pattern | Examples | Harmonic |
|---|---|---|
| Simple harmonic division | D9, D10, D12, D16, D30 | sign/n → new sign |
| Composite from multiple divisions | D60 (sign × nakshatra pada) | compound |
| Body-part mapping | D6 (Shashthamsa for health) | mapped by text rule |
| Role-reassignment | D20 (spiritual practice) | planet-role shifts |

The LLM is prompted with these patterns as few-shot examples.

### 3.2 Generative architecture

```
User/Researcher:
  "Compose a varga for software engineering career indicators"
      ↓
1. Prompt constructs:
   - Pattern library (5 classical vargas as exemplars)
   - Domain keywords (software, technical, analytical, focus, abstraction)
   - Planet/sign affinities from classical corpus (retrieved via Qdrant)
2. LLM output:
   - Proposed harmonic (e.g., D-24 based on precedent for intellectual work)
   - Proposed planet weighting (Mercury 1.5×, Saturn 1.2×, ...)
   - House-role reassignments
   - Justification prose with classical citations
3. Validation pass (automatic):
   - Run proposed varga on labeled outcome dataset
   - Compute: correlation with observed outcome, effect size, confidence intervals
4. Editorial review (human):
   - Classical-content scholar reviews plausibility
   - Quantitative reviewer reviews validation stats
   - Accept / reject / revise
5. Registry merge (if accepted):
   - New source_id = "josi_generated_{slug}"
   - Rule YAML checked into I3
   - Version tag: "experimental" (promotable to "accepted" after sustained validation)
```

### 3.3 Source-authority distinction (non-negotiable)

Per master spec §7: **"we never blend Josi-originated rules with classical rules in the same TechniqueResult; if we ever originate rules, they get their own source_id = 'josi_original'."**

I4 respects this. Novel vargas get distinctive source_ids:
- `source_id: josi_generated_{slug}` (e.g., `josi_generated_d24_tech_career`)
- `tradition: josi_original`
- `default_weight: 0.5` at publication (below classical sources); adjustable per validation performance.

UIs surface this clearly: "Experimental / Josi-generated" badge.

### 3.4 Validation data

Outcome data comes from:
- Opt-in user self-reports (via D6 longitudinal dashboard): "my career outcome", "my relationship status", etc.
- Career/demographic data licensed from third parties (anonymized).
- Historical/biographical datasets (public figures, anonymized).

Critical: no PII ever flows to the generative LLM; only aggregated statistics.

### 3.5 Alternatives considered

| Alternative | Rejected because |
|---|---|
| Human-only novel chart design | Slow; limited by human imagination; no systematic search. |
| Fully automatic publication (no human review) | Correctness risk; classical ethics violated. |
| Generate novel yogas instead of vargas | Yogas already enumerate 1000+ (I10); vargas are more undersampled. |
| Generate vargas only from classical pattern library (no LLM) | Too restrictive; loses the research-generation upside. |

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| Who can propose novel vargas | Internal team + select Pro astrologers + I3 community PRs | Breadth of input; reviewed before publication. |
| Novel vargas visible to end-users | Only in Ultra AI mode + Astrologer Workbench with experimental toggle | Protect Auto mode from noise. |
| How to weight novel vargas in aggregation | Start at weight 0.5; adjust per validation; never exceed weight of classical source | Epistemic humility. |
| Validation threshold for promotion | Effect size ≥ 0.2 (Cohen's d equivalent), confidence interval excluding 0, n ≥ 1000 chart-outcome pairs | Standard effect-size + power thresholds. |
| Deprecation criterion | Sustained validation failure over 6 months → move to deprecated state | Avoid accumulating bad novel vargas. |
| Attribution / royalty to novel-varga proposer | Name on accepted rule; no royalty (OSS ethos) | Aligns with I3 contribution model. |

## 5. Component Design

### 5.1 New services / modules

```
src/josi/generative/
├── chart_synthesis/
│   ├── proposer.py              # Claude-powered proposal generation
│   ├── validator.py             # Run proposed varga on labeled data
│   ├── editorial_queue.py       # Workflow state machine
│   └── promotion.py             # experimental → accepted → deprecated
├── corpus/
│   └── pattern_library.py       # Few-shot examples from classical vargas
└── eval/
    └── outcome_correlation.py   # Stats: effect size, CI, power

src/josi/api/v1/controllers/generative_chart_controller.py
```

### 5.2 Data model additions

```sql
CREATE TABLE generative_chart_proposal (
  proposal_id UUID PK,
  proposer_user_id FK,
  proposed_at TIMESTAMPTZ,
  domain_prompt TEXT,
  proposed_spec JSONB,        -- {harmonic, weights, house_roles, justification}
  llm_model_version TEXT,
  validation_result JSONB NULL,  -- {effect_size, ci_low, ci_high, n}
  status TEXT CHECK (status IN ('draft','under_validation','under_review','accepted','rejected','deprecated')),
  reviewer_notes JSONB NULL,
  merged_source_id TEXT NULL  -- points to classical_rule source_authority once merged
);

CREATE TABLE generative_chart_validation_run (
  run_id UUID PK, proposal_id FK,
  dataset_fingerprint TEXT,
  metric JSONB,
  run_at TIMESTAMPTZ
);
```

New rows in `source_authority` dim (lazy-created on merge): tradition = `josi_original`.

### 5.3 API contract

```
POST /api/v1/generative/proposals            # body: {domain_prompt, constraints}
GET  /api/v1/generative/proposals/{id}
POST /api/v1/generative/proposals/{id}/validate
POST /api/v1/generative/proposals/{id}/submit-for-review
GET  /api/v1/generative/editorial-queue      # reviewer-only
POST /api/v1/generative/proposals/{id}/review  # reviewer-only
```

## 6. User Stories

### US-I4.1: As a researcher at Josi Press, I want to propose a novel varga for evaluation
**Acceptance:** submit domain prompt; receive LLM proposal + validation run; submit for review; receive decision within 30 days.

### US-I4.2: As a Pro astrologer in Ultra AI mode, I want to experiment with a novel varga on my client's chart
**Acceptance:** select experimental varga from catalogue; compute on chart; result clearly labeled "experimental"; export blocked from final report template without explicit acknowledgment.

### US-I4.3: As a classical-content editorial reviewer, I want a structured queue of proposals to review
**Acceptance:** queue shows pending proposals with: LLM justification, classical citations, validation stats, proposer identity; approve/reject/revise options.

### US-I4.4: As a PhD student, I want to analyze novel vargas generated by Josi and their predictive performance
**Acceptance:** D7 research data API exposes aggregated validation stats for all proposals; anonymized at k ≥ 100.

### US-I4.5: As a Josi engineer, I want to deprecate a novel varga that fails ongoing validation
**Acceptance:** quarterly re-validation job; vargas failing threshold auto-flag for deprecation review; deprecated state propagates to all surfaces.

### US-I4.6: As an external I3 contributor, I want to submit a novel varga via GitHub PR
**Acceptance:** same editorial review applies to PR-submitted proposals as internal submissions; no privileged path.

## 7. Tasks

### T-I4.1: Pattern library + prompt engineering
- **Definition:** Codify classical varga construction patterns as few-shot exemplars; design proposal prompt.
- **Acceptance:** 10 classical vargas encoded; LLM produces syntactically valid YAML on 95% of test prompts.
- **Effort:** Q1.

### T-I4.2: Proposer service
- **Definition:** Claude-integrated proposer with retrieval + guardrails; returns proposal in structured form.
- **Acceptance:** Integration tests; output validates against varga JSON Schema.
- **Effort:** Q1.

### T-I4.3: Validator service
- **Definition:** Runs proposed varga over labeled outcome dataset; computes statistics; stores run.
- **Acceptance:** Validator reproduces known classical effects on D10 career varga within error margin (sanity check).
- **Effort:** Q2.

### T-I4.4: Editorial queue + review UI
- **Definition:** Workflow state machine; reviewer dashboard (internal Next.js admin app).
- **Acceptance:** Full workflow tested end-to-end with 5 synthetic proposals.
- **Effort:** Q2.

### T-I4.5: Registry merge automation
- **Definition:** On acceptance, auto-generate rule YAML + PR to I3 OSS repo; source_id convention.
- **Acceptance:** Accepted proposal lands as PR in I3 repo with classical_reviewer assigned.
- **Effort:** Q2.

### T-I4.6: Experimental-varga UI surfacing
- **Definition:** Workbench (E12) toggle; Ultra AI mode exposure; prominent "experimental" badging.
- **Acceptance:** Badge visible in Playwright test; exports require acknowledgment checkbox.
- **Effort:** Q3.

### T-I4.7: Quarterly re-validation job
- **Definition:** Scheduled cron re-runs validation on all accepted novel vargas; flags deprecations.
- **Acceptance:** First quarterly run completes without error; deprecation candidates flagged.
- **Effort:** Q3.

### T-I4.8: External submission flow (I3)
- **Definition:** Document submission process in I3 repo; GitHub PR template; CI that triggers validation run.
- **Acceptance:** Test PR from external contributor completes full workflow.
- **Effort:** Q3–Q4.

### T-I4.9: First peer-reviewed paper on generated vargas
- **Definition:** Paper submitted to I2 describing methodology + results on first 10 accepted novel vargas.
- **Acceptance:** Paper accepted or revise-resubmit with reasonable revisions.
- **Effort:** Q4.

## 8. Unit Tests

### 8.1 Proposer-service tests
| Test category | Representative names | Success target |
|---|---|---|
| Output validity | `test_proposer_output_is_valid_varga_yaml` | ≥ 95% of proposals validate against schema |
| Citation accuracy | `test_proposer_citations_exist_in_corpus` | ≥ 90% of citations reference real corpus entries |
| Diversity | `test_proposer_generates_distinct_proposals_for_distinct_prompts` | Levenshtein distance ≥ threshold across 100 paired prompts |
| Hallucination guard | `test_proposer_rejects_out_of_scope_prompt` | ≥ 98% rejection on adversarial prompts |

### 8.2 Validator-service tests
| Test category | Representative names | Success target |
|---|---|---|
| Statistical correctness | `test_validator_reproduces_known_effect_on_d10_career` | Effect size within ±10% of precomputed baseline |
| Multiple-comparisons correction | `test_validator_applies_bh_correction` | 100% of reported p-values adjusted |
| k-anonymity | `test_validator_aggregates_k_100_minimum` | 100% of per-chart stats roll up to k ≥ 100 |

### 8.3 Editorial workflow tests
| Test category | Representative names | Success target |
|---|---|---|
| State transitions | `test_proposal_lifecycle_states` | Only valid transitions accepted |
| Review SLA | `test_editorial_median_time_to_decision` | Median ≤ 30 days, p90 ≤ 45 days |
| Rejection irreversibility | `test_rejected_proposal_cannot_be_auto_merged` | 100% enforcement |

### 8.4 Registry merge tests
| Test category | Representative names | Success target |
|---|---|---|
| source_id convention | `test_merged_rule_has_josi_generated_source_id` | 100% |
| No classical blending | `test_merged_rule_never_has_classical_tradition` | 100% |
| Weight cap | `test_default_weight_lte_0_5_at_publication` | 100% |

### 8.5 Deprecation tests
| Test category | Representative names | Success target |
|---|---|---|
| Re-validation cadence | `test_quarterly_revalidation_all_accepted` | 100% covered per quarter |
| Deprecation propagation | `test_deprecated_rule_hidden_from_default_ui` | Propagates within 24 hours |

## 9. EPIC-Level Acceptance Criteria

- [ ] Proposer generates valid varga proposals with classical-citation justifications.
- [ ] Validator runs proposals against outcome data with k ≥ 100 aggregation.
- [ ] Editorial queue active; median review time ≤ 30 days.
- [ ] At least 10 novel vargas accepted and merged into I3 registry in Year 4.
- [ ] Zero classical-tradition blending incidents (source_id hygiene preserved).
- [ ] Ultra AI mode exposes accepted novel vargas with experimental badging.
- [ ] First I2 paper on generative methodology accepted.
- [ ] External contributor submits + wins acceptance on at least 1 proposal.
- [ ] Quarterly re-validation job operational for at least 2 quarters.
- [ ] Deprecation of at least 1 novel varga executed cleanly (demonstrates lifecycle).

## 10. Rollout Plan

**Gate 0 — Internal research (Year 4 Q1):**
- Feature flag: `generative_charts_internal_only` (on for Josi employees only).
- Produce first 5 proposals; internal editorial review; no public surfacing.
- **Gate to proceed:** at least 3 proposals pass validation + editorial review.

**Gate 1 — Pro astrologer alpha (Year 4 Q2):**
- Opt-in for 20–50 Pro astrologers via Ultra AI mode.
- **Gate to proceed:** no more than 2% of Pro astrologer sessions accidentally leak experimental vargas into non-experimental exports.

**Gate 2 — Ultra AI public (Year 4 Q3):**
- Accepted novel vargas visible in Ultra AI mode for all Ultra subscribers.
- **Gate to proceed:** first paper accepted at I2.

**Gate 3 — External contributor flow (Year 4 Q4):**
- Open submission via I3 repo.
- **Gate to Year 5 expansion (generative dasas?):** external contributions meaningfully diverse from internal proposals.

**Rollback plan:** feature flag disables generative charts; deprecated novel vargas remain readable in historical records but are not applied to new computations.

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| LLM hallucinates plausible-sounding but unjustified varga | High | Medium | Citation check against corpus; editorial review; classical-content reviewer has veto. |
| Novel vargas perceived as "AI slop" by classical community | Medium | High | Source-id distinction; conservative publication cadence; conspicuous experimental badging; peer-reviewed papers for methodology. |
| Validation dataset has systematic bias (e.g., demographic) | High | High | Disclose dataset provenance per proposal; multiple datasets; bias audit before acceptance. |
| User confusion: classical vs generated | Medium | Medium | Only visible in Ultra/Pro modes; badging; acknowledgment on export. |
| Regulatory: generated vargas used for consequential decisions | Low | Medium | Disclaimer layer; no medical/legal/financial use endorsements. |
| Erosion of trust in classical rules by implication | Low | Medium | Messaging emphasizes complementarity; classical remains default. |
| Gaming: user submits many low-quality proposals to game the system | Medium | Low | Rate limits per user; reputation-weighted queue priority. |
| Validation overhead becomes cost center | Medium | Medium | Cap compute budget per proposal; batch validation runs. |
| Deprecation backlash (user relied on a novel varga that's now deprecated) | Low | Medium | Deprecation grace period; UX shows historical results with disclaimer. |
| Research ethics: generative modeling treated as "novel medical hypothesis" in some jurisdictions | Low | High | Legal review; framing as computational research; IRB sign-off via I2. |

## 12. References

- Master spec: `docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md` — §7 enforces source_id hygiene.
- Related PRDs: E7, I2, I3, Reference-1000, I10, D7, E12, D6
- BPHS Ch.4–7 on varga construction
- Jaimini Sutras on chart-section logic
- Generative AI + scientific discovery: analogous patterns in AlphaFold, generative chemistry.
