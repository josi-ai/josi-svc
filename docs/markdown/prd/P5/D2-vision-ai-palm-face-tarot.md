---
prd_id: D2
epic_id: D2
title: "Vision AI (palmistry, face reading, tarot via camera) cross-referenced with birth chart"
phase: P5-dominance
tags: [#ai-chat, #end-user-ux, #extensibility]
priority: should
depends_on: [F9, F10, F11, E11a, E11b]
enables: [I8]
classical_sources: [bphs, saravali, samudrika_shastra, hellenistic]
estimated_effort: 10-12 weeks
status: draft
author: "@agent"
last_updated: 2026-04-19
---

# D2 — Vision AI: Palmistry, Face Reading, Tarot via Camera

## 1. Purpose & Rationale

Astrology historically is multi-modal. *Samudrika Shastra* (classical Indian body-reading) is taught alongside jyotish in the same traditional curricula. Tarot, *I-Ching*, and facial physiognomy all belong to the same "divinatory toolkit" users expect from a comprehensive platform. Adding vision capabilities:

1. **Unique cross-reference** — no competitor cross-references palm *and* chart: "your life-line indicates X, your chart's 1st-house lord indicates Y — these confirm each other." This is the platform-level insight that's unreachable single-mode.
2. **Engagement** — camera interactions are fun, shareable, re-engaging. Palm-scan every 6 months tracks changes.
3. **Reduced dependence on birth data** — not every user has accurate birth time. Vision lets us still produce meaningful output.
4. **Tarot marketplace bridge** — users upload photos of physical spreads; AI reads. Lowers friction vs. digital-only draws.

## 2. Scope

### 2.1 In scope
- Palm image capture (left and right) with guided framing overlay
- Palm-line extraction (heart, head, life, fate) with classical Samudrika Shastra interpretation
- Face reading based on *Samudrika Lakshanas* + Western physiognomy — features only (never racial/biometric characterization)
- Tarot card recognition from a photo of a physical spread (single card, 3-card, Celtic Cross)
- Cross-referencing engine: vision findings fused with chart placements into a single reading (via E11b ensemble)
- Privacy-first: images processed ephemerally by default; user can opt in to store for "progress" view
- Multi-modal LLM adapter (Claude vision, GPT-4V, Gemini Vision — selected per benchmark)
- Frontend camera UX with alignment guides

### 2.2 Out of scope
- Medical diagnosis from face/palm (explicitly forbidden; safety guardrails required)
- Biometric identity (face-recognition-for-ID)
- Racial, ethnic, gender-based inference — explicitly banned
- Live video (still images only in P5)
- Automated cheiromancy for hiring/loans/insurance — banned use case
- Hand geometry for health predictions — banned

### 2.3 Dependencies
- F10 typed tool-use extended with vision tools
- F11 citations (Samudrika Shastra has classical verse references)
- E11b multi-strategy ensemble for fused readings
- Storage bucket in GCS with ephemeral lifecycle policy
- New `source_authority` rows for `samudrika_shastra`, `hast_samudrika`, `western_physiognomy`, `tarot_rws` — added to F1 seed via PR

## 3. Technical Research

### 3.1 Classical sources

- *Samudrika Shastra* — the Indian classical science of bodily marks; attributed fragments in various Puranas and later compendia. Contains palm-line names, lunar-mount correspondence, finger-length ratios.
- *Hasta Samudrika* — palmistry-specific subset.
- Western palmistry (Cheiro, early 20th century codification) — rejected for race-based claims; we cite only the line/mount taxonomy, not Cheiro's interpretations.
- Tarot — Rider-Waite-Smith (RWS) 78-card deck with standard iconography.

Each becomes its own `source_authority` row so aggregation strategies (A/B/C/D) work the same as for chart-based techniques.

### 3.2 Vision model selection (TBD at phase start)

| Candidate | Strengths |
|---|---|
| Claude vision (Opus/Sonnet) | Strong instruction following; citation-style responses |
| GPT-4V / GPT-5V | Broad object detection; detailed OCR |
| Gemini Vision | Strong multi-language labels; cost-competitive |
| Dedicated palm-line CV model + text LLM | Highest accuracy for line extraction; two-stage pipeline |

Criteria: palm-line extraction F1 ≥ 0.85 on 1k annotated palms; tarot card recognition accuracy ≥ 98% on 78 standard-deck cards across lighting conditions; face-feature extraction ≥ 90% on benchmark.

### 3.3 Cross-referencing architecture

Vision finding becomes a `technique_compute` row with `source_id = 'samudrika_shastra'` (or `hast_samudrika`, `tarot_rws`) and a structured output (e.g., `{"fate_line": {"strength": "clear", "length_score": 0.7, "breaks_at": ["middle"]}}`). The aggregation engine (F8) then fuses with chart-side `technique_compute` rows, so a fused reading is just a regular cross-source aggregation — reusing infrastructure.

### 3.4 Privacy model

- Image uploaded via signed URL → ephemeral processing bucket
- Vision provider called in-region with image bytes
- Extracted structured features stored in DB (no raw image unless opt-in)
- Raw image bucket lifecycle: delete after 15 min by default
- User can toggle "save palm progress" → moved to retained bucket with encryption-at-rest

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| Allow face as input | Yes, features only, no identity | Classical precedent (Samudrika); strong moderation guardrails |
| Store raw images | No by default; opt-in for "progress" view | Privacy + minimize liability |
| Accept third-party tarot decks beyond RWS | RWS only in P5; others as additive sources in P6 | Scope discipline; RWS = 95% of market |
| Combine with voice (D1) | Yes — user takes palm photo, then has voice session with visual context | Natural UX; no extra PRD work required |
| Price model | Free tier: 1 palm/month + 1 tarot/month; Premium: unlimited | Matches B2C tier structure |
| Safety on face reading | No claims about intelligence, morality, criminality, ancestry | Ethics + legal |

## 5. Component Design

### 5.1 New services / modules

```
src/josi/vision/
├── __init__.py
├── provider/
│   ├── base.py                 # VisionProvider ABC
│   ├── claude_vision.py
│   └── gpt_vision.py
├── palm/
│   ├── extractor.py            # calls vision model → structured palm features
│   ├── samudrika_rules.py      # maps features → rule activations
│   └── interpreter.py
├── face/
│   ├── extractor.py
│   ├── features.py              # feature taxonomy (forehead, jawline, ears, eye shape)
│   └── interpreter.py
├── tarot/
│   ├── recognizer.py            # card detection + recognition
│   └── spreads.py               # single / 3-card / Celtic Cross interpretations
├── fuse.py                      # cross-reference vision ↔ chart via F8 aggregation
└── image_store.py               # signed URL upload, ephemeral/retained lifecycle

src/josi/api/v1/controllers/vision_controller.py
  # POST /api/v1/vision/palm          { chart_id, image_id_left, image_id_right }
  # POST /api/v1/vision/face          { chart_id, image_id }
  # POST /api/v1/vision/tarot         { chart_id, image_id, spread_type, question }
  # POST /api/v1/vision/upload-url    → pre-signed ephemeral upload URL
```

### 5.2 Data model additions

```sql
CREATE TABLE vision_analysis (
    vision_analysis_id   UUID PRIMARY KEY,
    user_id              UUID NOT NULL,
    organization_id      UUID NOT NULL,
    chart_id             UUID REFERENCES chart(chart_id),
    modality             TEXT NOT NULL CHECK (modality IN ('palm','face','tarot')),
    image_uri_ephemeral  TEXT,                   -- cleared after 15 min by lifecycle
    image_uri_retained   TEXT,                   -- only if user opted in
    features             JSONB NOT NULL,         -- structured extractor output
    interpretation       JSONB NOT NULL,         -- fused interpretation
    created_at           TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_vision_user_modality_time
    ON vision_analysis(user_id, modality, created_at DESC);

-- Added rows in source_authority (via YAML PR, not a migration):
-- ('samudrika_shastra', 'Samudrika Shastra', 'parashari', ...)
-- ('hast_samudrika', 'Hasta Samudrika', 'parashari', ...)
-- ('tarot_rws', 'Rider-Waite-Smith Tarot', 'western', ...)
-- ('western_physiognomy', 'Western Physiognomy (feature-taxonomy only)', 'western', ...)
```

### 5.3 API contract

```
POST /api/v1/vision/palm
Body: { "chart_id": "...", "image_id_left": "...", "image_id_right": "..." }
Response: {
  "success": true,
  "data": {
    "vision_analysis_id": "...",
    "features": { "heart_line": {...}, "head_line": {...}, "life_line": {...}, "fate_line": {...} },
    "classical_interpretation": [
      { "source": "samudrika_shastra", "citation": "Hasta Samudrika v.28",
        "claim": "clear fate line from wrist to Saturn mount", "strength": 0.82 }
    ],
    "chart_cross_reference": [
      { "chart_factor": "10th lord Saturn in own sign",
        "palm_factor": "strong fate line",
        "agreement": "high",
        "commentary": "Career indications from chart and palm confirm each other." }
    ],
    "disclaimer": "For spiritual-guidance and entertainment purposes only."
  }
}
```

## 6. User Stories

### US-D2.1: As a user curious about career, I want palm + chart to jointly reveal insight
**Acceptance:** submitting both images returns interpretation that references specific chart placements AND specific palm features; citations present for both.

### US-D2.2: As a tarot practitioner, I want to photograph my physical 3-card spread and have AI read it within context of my chart
**Acceptance:** card recognition ≥ 98%; reading references the question posed; chart cross-reference optional but available.

### US-D2.3: As a privacy-sensitive user, I want my images auto-deleted
**Acceptance:** bucket lifecycle deletes ephemeral images at 15 min; retained images exist only when explicit opt-in; opt-out erases retained images within 24h.

### US-D2.4: As a user, I want clear refusal when I attempt medical or biometric-identity use
**Acceptance:** prompts like "diagnose my skin condition" or "identify this person" yield refusals with redirect messaging.

### US-D2.5: As a user without a known birth time, I want palm reading to stand alone
**Acceptance:** when `chart_id` is null or chart has `birth_time_unknown=true`, reading omits chart cross-reference cleanly, not with errors.

### US-D2.6: As an auditor, I want to inspect what rules fired on a given palm analysis
**Acceptance:** vision_analysis row contains `features` + `interpretation` with rule IDs + citations; audit API returns them.

## 7. Tasks

### T-D2.1: Classical content seeding (Samudrika / Hasta Samudrika / RWS / Physiognomy)
- **Definition:** YAML source_authority rows + F6-style rule registries for palm-line, face-feature, and tarot-card rules.
- **Acceptance:** classical advisor sign-off; citations verifiable.
- **Effort:** 3 weeks

### T-D2.2: Vision provider abstraction + benchmarking
- **Definition:** ABC + 2 adapters; eval harness on 1k annotated palms, 500 tarot photos, 500 face photos (ethically sourced, consenting dataset).
- **Acceptance:** scorecard archived; provider chosen meets F1 / accuracy targets.
- **Effort:** 3 weeks

### T-D2.3: Palm-line extractor + interpreter
- **Definition:** Vision call → structured features → Samudrika rule activations → interpretation text with citations.
- **Acceptance:** golden set of 100 annotated palms; ≥ 85% feature match.
- **Effort:** 2 weeks

### T-D2.4: Face-feature extractor + interpreter
- **Definition:** Feature taxonomy limited to neutral observables (forehead breadth, jawline, eye shape); interpreter maps to classical indications; banned claims list enforced.
- **Acceptance:** banned-claim regression test ≥ 100/100 blocked; feature extraction ≥ 90% on benchmark.
- **Effort:** 2 weeks

### T-D2.5: Tarot card recognizer + spread interpreter
- **Definition:** Recognize 78 RWS cards + orientation (upright/reversed); support single/3-card/Celtic Cross.
- **Acceptance:** 98% card accuracy across 500 test photos; spread positions labeled correctly.
- **Effort:** 2 weeks

### T-D2.6: Fusion with chart via F8 aggregation
- **Definition:** Vision findings enter as `technique_compute` rows; aggregation engine produces cross-referenced output.
- **Acceptance:** end-to-end: palm + chart → fused narrative; cross-source agreement score present.
- **Effort:** 1 week

### T-D2.7: Image lifecycle + privacy controls
- **Definition:** GCS bucket with 15-min TTL default; retained opt-in path; GDPR/DPDP delete endpoint.
- **Acceptance:** bucket policy verified; delete propagates in < 24h; logs audited.
- **Effort:** 1 week

### T-D2.8: Frontend camera UX
- **Definition:** Web + mobile camera flows with alignment guides, quality checks (blur, lighting), retake option.
- **Acceptance:** median capture-to-result < 30s; rejection rate for low-quality images < 20%.
- **Effort:** 2 weeks

### T-D2.9: Safety + moderation
- **Definition:** Banned-use detector (medical, biometric ID, ancestry inference); prompt-level + output-level filter.
- **Acceptance:** red-team suite; ≥ 99% correct refusal.
- **Effort:** 1.5 weeks

## 8. Unit Tests

### 8.1 Palm-line extraction
- Category: image → structured palm features.
- Target: ≥ 85% F1 on 1k-palm golden annotated set.
- Representative: `test_palm_heart_line_detection`, `test_palm_missing_fate_line`, `test_palm_low_light_fallback`.

### 8.2 Face-feature extraction (neutral taxonomy)
- Category: feature detection limited to non-identity observables.
- Target: ≥ 90% feature accuracy; 100% banned-claim block.
- Representative: `test_face_forehead_breadth_classification`, `test_face_rejects_ancestry_query`, `test_face_rejects_intelligence_inference`.

### 8.3 Tarot card recognition
- Category: 78-card RWS across lighting/orientations.
- Target: ≥ 98% card + orientation accuracy.
- Representative: `test_tarot_major_arcana_recognition`, `test_tarot_reversed_detection`, `test_tarot_three_card_spread_positions`.

### 8.4 Cross-reference fusion
- Category: vision finding + chart finding → fused reading via F8.
- Target: agreement score in [0,1]; narrative cites both.
- Representative: `test_fusion_palm_and_chart_agree_career`, `test_fusion_palm_and_chart_disagree_surfaces_both`.

### 8.5 Image lifecycle
- Category: upload, process, expire, opt-in retain, delete.
- Target: no image retained past TTL unless explicit flag; deletion audited.
- Representative: `test_ephemeral_bucket_ttl_enforced`, `test_retained_bucket_opt_in_required`, `test_delete_endpoint_removes_in_24h`.

### 8.6 Safety
- Category: medical, biometric-ID, ancestry, hiring/loan/insurance use cases.
- Target: ≥ 99% correct refusal.
- Representative: `test_refuses_medical_diagnosis`, `test_refuses_identity_lookup`, `test_refuses_hiring_assessment`.

## 9. EPIC-Level Acceptance Criteria

- [ ] Palm extractor F1 ≥ 0.85 on annotated suite
- [ ] Tarot recognition ≥ 98% on 500-photo benchmark
- [ ] Face extractor ≥ 90% on benchmark AND 100% banned-claim block
- [ ] Cross-reference fusion works end-to-end (palm + chart, face + chart, tarot + chart + question)
- [ ] Classical advisor sign-off on Samudrika/Hasta Samudrika/Physiognomy interpretation rules
- [ ] GCS lifecycle verified: ephemeral bucket auto-deletes in 15 min
- [ ] Red-team safety suite ≥ 99%
- [ ] Documentation in `CLAUDE.md` + public API docs

## 10. Rollout Plan

- **Feature flag:** `vision_ai_enabled` (per-org, per-user).
- **Phase 1 — Tarot first (2 weeks internal, 2 weeks 5% beta):** simplest modality; users most familiar; tests camera UX; gate = recognition ≥ 98% live, NPS ≥ 40.
- **Phase 2 — Palm (4 weeks internal, 2 weeks 5% beta):** more classical depth; gate = F1 ≥ 0.85, classical advisor review pass.
- **Phase 3 — Face (6 weeks internal, 2 weeks 5% beta):** highest safety risk; extended red-team; gate = 100% banned-claim block on 10k synthetic prompts.
- **Phase 4 — GA rollout:** 10% → 50% → 100% at 2-week cadences.
- **Rollback:** feature flag kill; images purge via lifecycle; structured feature data remains queryable.

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Face reading misused for discriminatory inference | Medium | Very High | Banned-claim filter; third-party ethics review; conservative feature taxonomy |
| Privacy leak via retained images | Low | Very High | Default-off retention; signed URLs only; bucket audit; encryption-at-rest |
| Low-light / blur causes bad reading | Medium | Medium | Quality gate in frontend; retake prompt; confidence scores surface |
| Vision provider hallucinates palm lines | Medium | Medium | Two-model ensemble for palm extraction; confidence threshold for interpretation |
| Tarot copyright concerns for non-RWS decks | Low | Medium | RWS-only in P5; additive licensing for premium decks in P6 |
| Classical source inauthenticity claim | Medium | Medium | Only cite verifiable verse/page references; neutral framing for disputed texts |
| Regulatory (EU AI Act biometric category) | Medium | High | Legal review; conservative taxonomy; no biometric ID use |

## 12. References

- Master spec: `docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`
- Related PRDs: F8 (aggregation), F10 (tool-use), F11 (citations), E11b (ensemble), D1 (voice — multi-modal fusion), I8 (cross-modal divination P6)
- Classical sources: Samudrika Shastra fragments; Hasta Samudrika; Rider-Waite-Smith Tarot iconography
- Regulatory: EU AI Act biometric categorization; US ADA / hiring-related restrictions
