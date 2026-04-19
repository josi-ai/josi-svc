---
prd_id: D11
epic_id: D11
title: "Hindu temple muhurta-as-a-service API"
phase: P5-dominance
tags: [#multi-tenant, #i18n, #performance]
priority: could
depends_on: [D9, E5, E10, F9, P4-E4-tenant]
enables: []
classical_sources: [muhurta_chintamani, bphs, shulba_sutras, dharmasindhu]
estimated_effort: 8-10 weeks
status: draft
author: "@agent"
last_updated: 2026-04-19
---

# D11 — Hindu Temple Muhurta-as-a-Service API

## 1. Purpose & Rationale

Temples consume astrological data at industrial volumes: daily panchang for priests, muhurta computation for rituals (prana pratishtha, kalyanam, abhishekam, homam, brahmotsavam schedules), festival calendars, grahan (eclipse) protocols. Today, most temples rely on printed panchang booklets from a handful of traditional publishers (e.g., Brahmasri Chilakamarthi Prabhakara Chakravarthy's Drik panchang, Telugu Gantala Panchangam). These are authoritative but:
- Published annually → updates delayed
- Not queryable by ritual type
- Not integrated with temple operations software

D11 productizes muhurta as a JSON API for temple IT teams and their operations vendors. Volume-priced (per-lookup or flat annual). Hindi/Sanskrit/Tamil/Telugu/Kannada/Malayalam outputs. Ritual-specific muhurta criteria per temple's lineage.

Companion to D9 Temple Pack; D11 is the API-centric specialization.

## 2. Scope

### 2.1 In scope
- Daily panchang API for any location (tithi, nakshatra, yoga, karana, vara, sunrise, sunset, rahukalam, yamaganda, gulika, abhijit muhurta, choghadiya)
- Ritual-specific muhurta API: user supplies {activity, date-range, location}; response is ranked list of shubh (auspicious) windows with reasoning
- Activity catalog: prana pratishtha, vivaha (kalyanam), griha pravesh, upanayana, aksharabhyasa, karnavedha, simanta, srimantham, bhoomi puja, satyanarayan vrat, homam, abhishekam, annaprasana — 40+ activities seeded
- Festival calendar API: annual calendar of major festivals per region/tradition (Vaishnava/Shaiva/Shakta variants)
- Eclipse (grahan) protocol API: pre/during/post eclipse ritual guidance per classical prescriptions
- Multi-language outputs: Hindi, Sanskrit (Devanagari), Tamil, Telugu, Kannada, Malayalam
- Per-temple lineage overrides (P4-E4 payoff): specific temple can register "our muhurta criteria per Sri Vaishnava tradition" and API respects
- High-volume pricing + SLA; sub-100ms P95 for panchang lookup
- API-key or OAuth; no B2C surface
- Push endpoint: subscribe to "daily panchang for location L at 4am IST"

### 2.2 Out of scope
- Muhurta for non-Hindu rituals (Jain/Sikh/Buddhist variants deferred to P6)
- Direct-to-priest UX (handled by E12 workbench + D9 temple pack)
- Ritual procedure instructions (we provide timing; not the priestly process)
- Physical booklet publishing

### 2.3 Dependencies
- D9 Temple Pack (UX side)
- E5 Varshaphala / Tajaka for year-level festival calc
- E10 Prasna / Horary (some temple decisions are prasna-based)
- P4-E4-tenant for lineage-specific overrides
- F9 chart_reading_view (unused for non-natal API but pattern reused)

## 3. Classical / Technical Research

### 3.1 Classical sources

- *Muhurta Chintamani* (Rama Daivajna) — authoritative compendium of muhurta criteria
- *Dharmasindhu* (Kashinath Upadhyaya) — ritual timing and festival calendar
- *Brihat Samhita* (Varahamihira) — general principles
- *Shulba Sutras* — ritual geometry and timing for fire altar construction
- Regional sources: *Vakhyam Panchangam* (Tamil Nadu), *Drik Panchang* computations (pan-India)

### 3.2 Computational bases

- Drik (true-position) vs Vakhyam (algorithmic-approximation) — Josi defaults to Drik using Swiss Ephemeris (existing); Vakhyam supported as alternate per tenant preference
- Location-sensitive: local sunrise/sunset, ayanamsa, latitude corrections
- Precision: 1-minute granularity for muhurta windows; sub-second for sunrise

### 3.3 Lineage overrides

Major Hindu traditions differ on muhurta details:
- Sri Vaishnava — specific nakshatra combinations preferred for Vaishnava rituals
- Madhva — some muhurta rules differ
- Shaiva (various) — Shiva-specific rituals have unique criteria
- Shakta — Devi festivals use different timings
- Regional (Kashmiri, Bengali, Odia, Kerala) — local variations

These become per-tenant rule override sets via P4-E4.

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| Drik vs Vakhyam default | Drik (modern astronomical positions) | Higher precision; classical acceptance evolving |
| Granularity of muhurta | 1-minute | Finer than any ritual needs; coarser causes errors |
| Festival calendar scope | Major festivals only in P5 (~50); regional in P6 | Scope |
| Output format | Structured JSON + optional rendered text per language | API consumers need structured; priests appreciate text |
| Allow non-temple B2B customers | Yes (developers, matrimony sites, media) | Broader addressable market |
| Eclipse ritual content | Timing only; ritual text via content partners | Stay in timing lane |
| Tenant authoring of muhurta rules | Yes, with Josi advisor review | Quality gate |

## 5. Component Design

### 5.1 New modules

```
src/josi/muhurta/
├── panchang/
│   ├── daily.py
│   └── elements.py              # tithi, nakshatra, yoga, karana, vara
├── ritual/
│   ├── activity_catalog.py      # 40+ ritual types
│   ├── criteria.py              # YAML-driven criteria per activity
│   └── window_finder.py
├── festival/
│   ├── calendar.py
│   └── regional_variants.py
├── eclipse/
│   └── protocol.py
├── localization/
│   └── sanskrit_hindi_tamil_etc.py
└── api/
    └── controller.py

src/josi/content/muhurta/
├── activities/
│   ├── prana_pratishtha.yaml
│   ├── vivaha.yaml
│   ├── ... (40+)
├── festivals/
│   ├── major.yaml
│   └── regional/
└── lineage_variants/
    ├── sri_vaishnava.yaml
    ├── madhva.yaml
    └── shaiva_smarta.yaml
```

### 5.2 Data model additions

```sql
-- Reuses F1 source_authority rows for muhurta_chintamani, dharmasindhu, brihat_samhita
-- Reuses F6 rule DSL for activity criteria YAML

CREATE TABLE muhurta_activity (
    activity_id          TEXT PRIMARY KEY,
    display_name_map     JSONB NOT NULL,           -- language → label
    category             TEXT,                     -- 'temple_ritual','life_cycle','festival','commercial'
    default_criteria_yaml TEXT NOT NULL,
    notes                TEXT
);

CREATE TABLE muhurta_festival (
    festival_id          TEXT PRIMARY KEY,
    display_name_map     JSONB NOT NULL,
    tradition            TEXT[],                    -- ['vaishnava','shaiva','shakta'] applicable
    rule_yaml            TEXT NOT NULL,
    regional_variants    JSONB
);

CREATE TABLE muhurta_push_subscription (
    subscription_id      UUID PRIMARY KEY,
    tenant_id            UUID NOT NULL,
    location_lat         NUMERIC(9,6) NOT NULL,
    location_lng         NUMERIC(9,6) NOT NULL,
    timezone             TEXT NOT NULL,
    push_url             TEXT NOT NULL,
    schedule_cron        TEXT NOT NULL,           -- e.g., "0 4 * * *" 4am local
    language             TEXT NOT NULL,
    last_pushed_at       TIMESTAMPTZ
);
```

### 5.3 API contract

```
GET /api/v1/muhurta/panchang?date=2026-05-15&lat=13.0827&lng=80.2707&tz=Asia/Kolkata&lang=ta
Response: {
  "tithi": {"name":"navami","krishna":false,"end_time":"2026-05-15T08:42:00+05:30"},
  "nakshatra": {"name":"pushya","pada":3,"end_time":"..."},
  "yoga": {...}, "karana": {...}, "vara": {...},
  "sunrise": "...", "sunset": "...",
  "rahukalam": ["2026-05-15T10:30:00+05:30","..."],
  "yamaganda": [...], "gulika": [...], "abhijit": [...],
  "choghadiya": [{"name":"shubh","start":"...","end":"..."}, ...],
  "localized_text": { "ta": "..." }
}

POST /api/v1/muhurta/ritual
Body: {
  "activity_id": "vivaha",
  "date_range": {"from":"2026-06-01","to":"2026-06-30"},
  "location": {"lat":13.08, "lng":80.27, "tz":"Asia/Kolkata"},
  "lineage": "sri_vaishnava",   // optional per-tenant override key
  "options": {"min_window_minutes": 90}
}
Response: {
  "windows": [
    {"start":"2026-06-05T09:12:00+05:30","end":"2026-06-05T10:48:00+05:30",
     "score":0.92, "reasons":["pushya nakshatra","abhijit overlap","..."]},
    ...
  ],
  "citations": [{"source":"muhurta_chintamani","ref":"Ch 7 v 24"}]
}

GET /api/v1/muhurta/festivals?year=2026&region=tamil_nadu&tradition=vaishnava&lang=ta

GET /api/v1/muhurta/eclipse?year=2026&lat=...&lng=...

POST /api/v1/muhurta/subscribe  (push)
```

## 6. User Stories

### US-D11.1: As a temple IT admin, I fetch tomorrow's panchang in Tamil at 4am for our operations portal
**Acceptance:** push subscription delivers; accuracy vs Drik reference within 1-minute tolerance.

### US-D11.2: As a priest team scheduling a kalyanam, I request muhurta windows across a month
**Acceptance:** windows returned with reasons + citations; filter by duration; lineage respected.

### US-D11.3: As a temple board, our lineage's Sri Vaishnava muhurta criteria are honored
**Acceptance:** lineage override activates; advisor-reviewed; verified against 10 historical temple muhurta decisions.

### US-D11.4: As a festival calendar consumer, I get 50 major festivals with dates for 2026 in my region
**Acceptance:** calendar matches Drik panchang reference within expected tolerance.

### US-D11.5: As an eclipse pujari, I get pre/during/post grahan ritual timing
**Acceptance:** timings match classical prescriptions; displayed with clear sutra references.

### US-D11.6: As a high-volume consumer, my API sustains 500 RPS with < 100ms P95
**Acceptance:** load test; cache warming; observability dashboards.

## 7. Tasks

### T-D11.1: Panchang API (extends existing panchang endpoints)
- **Definition:** Extend existing /panchang controller; add all elements; multi-lang outputs.
- **Acceptance:** parity with reference panchang ≥ 99.9% on 1000 sample dates × 10 locations.
- **Effort:** 2 weeks

### T-D11.2: Activity catalog (40+ rituals)
- **Definition:** YAML per activity with criteria; advisor-reviewed.
- **Acceptance:** sign-off by Sri Vaishnava, Madhva, Shaiva, Shakta advisors; 40 activities live.
- **Effort:** 3 weeks

### T-D11.3: Window-finder algorithm
- **Definition:** Given criteria + date range, find ranked windows.
- **Acceptance:** deterministic; golden test cases per activity; citations attached.
- **Effort:** 2 weeks

### T-D11.4: Festival calendar seed (50 major)
- **Definition:** YAML + regional variants.
- **Acceptance:** 2026 calendar matches 3 reference panchangs.
- **Effort:** 2 weeks

### T-D11.5: Eclipse protocol
- **Definition:** Solar/lunar eclipse computation + protocol text.
- **Acceptance:** next 5 years of eclipses validated vs NASA ephemeris.
- **Effort:** 1 week

### T-D11.6: Localization (6 languages)
- **Definition:** Localized strings; transliteration; numeric format.
- **Acceptance:** 6 languages complete; native-speaker spot-check.
- **Effort:** 2 weeks

### T-D11.7: Lineage override mechanism
- **Definition:** P4-E4 override sets for Sri Vaishnava, Madhva, Shaiva Smarta; advisor signoff.
- **Acceptance:** overrides activate per tenant; verified.
- **Effort:** 2 weeks

### T-D11.8: Push subscription engine
- **Definition:** Per-subscription cron; retry on delivery failure; observability.
- **Acceptance:** 99.5% on-time delivery; daily reconciliation.
- **Effort:** 1.5 weeks

### T-D11.9: Caching + performance tuning
- **Definition:** Redis cache for hot locations; cache warming before peak hours.
- **Acceptance:** P95 < 100ms at 500 RPS.
- **Effort:** 1 week

## 8. Unit Tests

### 8.1 Panchang accuracy
- Category: vs. reference panchang on 1000 date × location samples.
- Target: ≥ 99.9% exact match for tithi/nakshatra/yoga/karana boundaries (±1 min).
- Representative: `test_tithi_boundary_accuracy`, `test_sunrise_within_1s_of_reference`, `test_rahukalam_for_each_day_of_week`.

### 8.2 Activity criteria
- Category: YAML-driven criteria produce expected windows.
- Target: golden cases per activity pass.
- Representative: `test_vivaha_pushya_nakshatra_acceptance`, `test_griha_pravesh_avoids_shunya_masa`.

### 8.3 Lineage overrides
- Category: override set changes expected output vs default.
- Target: deterministic; advisor-validated.
- Representative: `test_sri_vaishnava_vivaha_differs_from_default`, `test_madhva_prana_pratishtha_override`.

### 8.4 Festival calendar
- Category: reference-panchang comparison.
- Target: ≥ 98% agreement on 50 festivals × 2026.
- Representative: `test_deepavali_2026_correct`, `test_regional_pongal_variant`.

### 8.5 Eclipse accuracy
- Category: timing vs NASA ephemeris.
- Target: within 1 min.
- Representative: `test_2027_total_solar_eclipse_timing`, `test_lunar_eclipse_visibility_per_location`.

### 8.6 Localization fidelity
- Category: translations round-trip; script preserved.
- Target: 100%; native-speaker spot-check ≥ 95%.
- Representative: `test_tamil_nakshatra_names_script_preserved`, `test_sanskrit_devanagari_encoding`.

### 8.7 Performance
- Category: latency and throughput.
- Target: P95 < 100ms at 500 RPS; cache hit rate > 95% for panchang.
- Representative: `test_panchang_p95_latency_under_load`, `test_cache_hit_rate`.

### 8.8 Push delivery
- Category: on-time + retry on failure.
- Target: 99.5% on-time; retry within 5 min.
- Representative: `test_push_at_scheduled_time`, `test_push_retry_on_5xx`.

## 9. EPIC-Level Acceptance Criteria

- [ ] Panchang API ≥ 99.9% accuracy vs reference on broad sample
- [ ] 40+ activities with advisor sign-off
- [ ] 50+ festivals with regional variants
- [ ] 6 languages localized
- [ ] 3 lineage override sets (Sri Vaishnava, Madhva, Shaiva) advisor-signed
- [ ] Load: 500 RPS P95 < 100ms
- [ ] Push delivery 99.5% on-time
- [ ] 1 pilot temple customer live

## 10. Rollout Plan

- **Feature flag:** `muhurta_api`.
- **Phase 1 (4 weeks):** internal + 1 pilot temple; panchang + 10 activities.
- **Phase 2 (4 weeks):** expand to 40 activities + festivals + eclipses; second pilot.
- **Phase 3 (2 weeks):** GA; marketing to temple IT.
- **Rollback:** flag off; keep pilots running.

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Muhurta calculation errors cause ritual-timing disputes | Medium | Very High | Advisor review + golden tests + citations |
| Lineage-specific variants accumulate scope | High | Medium | P4-E4 supports additive; we don't maintain, tenants do |
| Reference panchang publishers see us as threat | Medium | Low | Co-citation of classical sources; partnership overtures |
| Regional festival variants cause disagreement | High | Medium | Publish variants side-by-side; tenant chooses |
| High traffic on festival days causes latency spikes | High | Medium | Pre-compute + cache; auto-scale; CDN panchang |
| Sanskrit rendering font/encoding issues | Medium | Low | Strict UTF-8; font sheet in docs; tested across clients |
| Drik vs Vakhyam user expectation mismatch | Medium | Medium | Per-tenant setting; documentation explicit |

## 12. References

- Master spec: `docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`
- Related PRDs: D9 (Enterprise/Temple Pack), E5 (Tajaka), E10 (Prasna), P4-E4-tenant
- Classical sources: *Muhurta Chintamani*, *Dharmasindhu*, *Brihat Samhita*, *Shulba Sutras*
- Reference panchangs: Drik Panchang, Vakhyam Panchangam, Kalnirnay
