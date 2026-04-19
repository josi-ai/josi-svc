---
prd_id: E17
epic_id: E17
title: "Chart Rectification — estimate accurate birth time from known life events"
phase: P2-breadth
tags: [#correctness, #ai-chat, #astrologer-ux, #end-user-ux]
priority: should
depends_on: [F1, F2, F6, F7, F8, F13, E1a, E6a]
enables: [E11a, E12, E13, S6]
classical_sources: [bphs, jh, cosmic_clock, rectification_modern]
estimated_effort: 4-5 weeks
status: draft
author: "@agent"
last_updated: 2026-04-19
---

# E17 — Chart Rectification

## 1. Purpose & Rationale

**Birth time is the single most error-prone input to any astrology calculation.** Across Josi's target audience segments this manifests as:

- **Diaspora users without birth certificates** (Indian-diaspora, Tamil-speaking, global South users born at home) — birth time unknown or approximate to ±2-4 hours.
- **Rounded-to-the-hour records** — hospital records often state "approximately 6:00 AM"; the true time may be 5:47 AM. A 13-minute error at equatorial latitudes shifts Lagna by ~3.25°, which in most cases is within a house but can cross a cusp.
- **Time-zone mis-stated records** — pre-daylight-saving or pre-partition records in regions where the zone changed.
- **Adopted users** — birth-time records legally sealed.

A 4-minute error shifts Lagna by 1°. A 2-hour error can move Lagna by a full house in some latitudes. **Without accurate birth time, everything downstream is wrong**: Lagna, all 12 houses, all house placements, Navamsa (D9) Lagna, all varga Lagnas, dasa starting lord, all dasa period boundaries, Muntha, and the entire annual-chart system.

Traditional rectification — by a senior astrologer in a multi-hour interview — triangulates likely birth time from **known life events**. The astrologer asks about major events, computes dasa periods and transits at those events under different candidate birth times, and selects the candidate whose technique-level signals align best with the reported events.

E17 delivers this as a computational pipeline. Given:
- Approximate birth date (known)
- Candidate time window (user-supplied; default ±4 hours)
- K known life events (`date`, `category`, optional `description`)

The engine searches the window at 1-minute resolution, scores each candidate using four independent techniques (Vimshottari dasa lord significations, slow-transit house-matter matches, secondary progressions, varga consistency), and returns the top 5 candidates with confidence scores and full reasoning.

**Three operating modes:**
1. **Pure AI mode** — fully automated; user chats with AI which gathers events, returns top 5 with reasoning, lets user choose.
2. **Expert-assisted mode** — engine shortlists candidates; professional astrologer (marketplace user) reviews and selects.
3. **Hybrid mode** — engine top 5 + astrologer final judgment with a scheduled video consultation.

E17 is not just a correctness fix — it is a **user-acquisition lever**. "We can estimate your birth time from your life events" is a differentiating promise against competitors who force users to enter a time they don't know.

## 2. Scope

### 2.1 In scope

- **Multi-technique triangulation engine** using four independent scoring methods:
  1. **Vimshottari Dasa-AD timing** — for each candidate birth time, compute which Mahadasa + Antardasa is active on each reported event date; score based on lord's house-lordship and classical significations matching event category.
  2. **Slow-transit natal-house matching** — for each event date, check transits of Jupiter, Saturn, Rahu, Ketu (and Chiron for Western mode) to the candidate's natal houses/lords; score based on matter-of-house alignment.
  3. **Secondary progressions** — compute progressed planets at event date; score based on angular contacts (progressed planet crossing natal angle or vice versa).
  4. **Varga consistency** — evaluate Lagna lord's position in Navamsa (D9) and Dasamsa (D10); score based on how well these align with reported life pattern (marriage quality, career shape).
- **Search algorithm:**
  - Candidate window divided at 1-minute resolution (default window ±4h = 480 candidates; astrologer can widen to ±8h = 960).
  - Each candidate scored by each of 4 methods independently; scores combined with configurable weights.
  - Top 5 returned with per-method score breakdown.
  - Coarse-to-fine optimization: first pass at 5-min resolution (48 or 96 candidates), then 1-min refinement around top-10 coarse winners.
- **Bayesian prior integration:**
  - User self-report ("I think I was born around sunrise" / "around 2 PM") → Gaussian prior centered on stated time with σ = user-supplied uncertainty (default 1h).
  - Mother's estimate (if given) → same formalism.
  - Priors combined with likelihood (score) into posterior via simple Bayesian update.
- **Event categorization:**
  - Supported categories (extensible via F1-style enum): `marriage`, `divorce`, `first_child`, `second_child`, `father_death`, `mother_death`, `sibling_death`, `major_illness`, `major_surgery`, `career_start`, `career_change`, `promotion`, `business_launch`, `financial_breakthrough`, `financial_loss`, `relocation_international`, `relocation_domestic`, `accident`, `spiritual_awakening`, `legal_victory`, `legal_defeat`.
  - Each category maps to a set of house/lord significations per BPHS (e.g., `marriage → 7th house + 7L + Venus; father_death → 9th house + Sun + 12 from 9th`).
  - Category map defined in `src/josi/data/rectification_event_categories.yaml`.
- **Confidence scoring:**
  - Each candidate's total score normalized against max possible (per-method weights × max-per-method).
  - Confidence tier: `high (> 0.75), medium (0.5-0.75), low (< 0.5)`.
  - Delta-to-second-place: if top candidate's score is >20% higher than second place, `clear_winner=true`; else `multiple_candidates=true`.
- **Output data model:**
  - New `rectification_session` table storing full session history (see §5.2).
  - Output shape reuses `structured_positions` with metadata describing rectification outcome, OR a new `rectification_result` shape (§5.3.5 proposes — we choose to propose a new shape).
- **API endpoints:**
  - `POST /api/v1/rectification/run` — initiate rectification; returns session_id immediately + triggers background compute.
  - `GET /api/v1/rectification/{session_id}` — retrieve status + results.
  - `POST /api/v1/rectification/{session_id}/select` — user/astrologer selects one candidate; optionally creates a chart with the selected time.
- **AI chat mode integration:**
  - `rectify_birth_time` tool exposed to AI chat.
  - Chat walks user through event collection.
  - Chat presents top 5 with reasoning and lets user choose.
- **Astrologer workbench integration (E12):**
  - Astrologer sees all candidates with per-method scoring breakdown and classical chart visualizations.
  - Manual override: astrologer can supply their own best-guess time and engine validates it against events with same scoring.
- **Unit tests:**
  - Synthetic charts with **known** birth times → blind rectification recovers to within ±15 minutes given 5+ events of varying categories.
  - Regression suite across 20 celebrity / published charts (Astro-Databank "AA"-rated timings as ground truth).

### 2.2 Out of scope

- **Prenatal epoch / conception-chart rectification** — Mardyks and Muhurta pre-birth techniques; deferred.
- **Trutti / Nadi rectification** — classical Nadi-reading style rectification requires access to palm-leaf classifications; not supported.
- **Event date error handling beyond ±day** — user must supply event date to ±1 day accuracy; a "sometime in 2019" event carries no signal.
- **Non-Gregorian calendar inputs for events** — events must be supplied in Gregorian ISO-8601; conversion from Tamil/Hindu calendars is a user-facing concern.
- **Retrieval of historical transit data pre-1800** — Swiss Ephemeris supports it, but classical rectification was not performed on pre-1800 events in practice; we decline for data-quality reasons.
- **Rectification of unknown date** (only time unknown) — date is an input; this PRD does not estimate date.
- **Live chat-driven rectification UI** — E11a / E13 deliver the UI; this PRD delivers the engine + API.
- **Payment integration for astrologer-assisted rectification** — consultations module (existing) handles payment; this PRD only exposes "assign to astrologer" action.

### 2.3 Dependencies

- F1 — `source_authority` has `rectification_modern`, `jh`, `cosmic_clock`; `technique_family` has `rectification` (new).
- F2 — `technique_compute` (not directly; rectification stores in its own session table, but scoring subroutines read `technique_compute` for natal candidate).
- F6 — DSL (event-category significations declared as DSL data, not executable rules).
- F7 — new or reused output shape (see §5.3).
- F8 — aggregation protocol (not used; rectification is single-source by definition).
- F13 — content-hash for session reproducibility.
- E1a — existing multi-dasa engine (Vimshottari computation for candidate).
- E6a — existing transit intelligence (transit-at-event lookups).
- S6 — "lazy compute on demand" — once a chart is rectified and birth_time updated, downstream re-computation triggered via S6.
- `pyswisseph` — for per-candidate chart recalculation.
- `AstrologyCalculator` — existing natal chart primitives.

## 3. Classical / Technical Research

### 3.1 Classical rectification techniques

**Primary sources:**
- *Brihat Parashara Hora Shastra* Ch. 1 v.33-42 — mentions timing-correction via event-matching (brief).
- *Jataka Parijata* Ch. 2 — clearer treatment of rectification from dasa-event correspondence.
- K.N. Rao, *The Modern Way of Rectification* (2001, Vani) — modern compendium of classical techniques, 12 methods.
- V.P. Jain, *Advanced Techniques of Rectification* (2006) — dasa-based + transit triangulation.
- Isaac Starkman, *Precise Times of Birth* (Israeli school, 1990s) — transit-event matching.
- James Eshelman, *Interpreting Solar Returns* (1985) — secondary progression events.
- Marc Edmund Jones, *Astrology: How and Why It Works* (1945) — early Western rectification essays.
- Jagannatha Hora (JH) 7.x documentation — "Rectification" panel using Tajaka events + varga Lagna method.

### 3.2 Why multi-technique triangulation (not a single method)

Any single classical technique has **known failure modes:**

| Method | Failure mode | Why |
|---|---|---|
| Dasa alone | Pratyantardasa boundaries shift with small time changes, but Mahadasa boundaries are years; low resolution | Most events within 1 MD ≈ 6-20 years |
| Transit alone | Slow planets (Jupiter/Saturn) transit a house for 2-3 years; low time resolution | Event within wide window |
| Progression alone | Only shows a few major events per decade | Sparse signal |
| Varga consistency | Does not directly tie to event date; tests long-term life-pattern match | Qualitative |

Combining all four methods creates **orthogonal signals** — a candidate time that scores high on dasa lord, slow-transit house, progressed aspect, and varga pattern is mathematically much less likely to be wrong than a candidate winning on only one.

Reference: K.N. Rao explicitly recommends "never trust a rectification from one method alone" (op. cit. Ch. 1).

### 3.3 Event-category → signification mapping

Based on BPHS Ch. 14-25 (house matters) + Ch. 35-40 (dasa significations). Each category maps to:
- **Primary house(s)** — whose activation is expected during the event.
- **Primary lord(s)** — dasa lords likely active.
- **Primary karakas** — natural significators (e.g., Venus for marriage, Sun for father).

```yaml
# src/josi/data/rectification_event_categories.yaml
marriage:
  primary_houses: [7, 2, 11]        # 7th marriage; 2nd family; 11th gain
  primary_lords: [7, 2, 11]
  karakas: [venus]                  # venus = marriage karaka (men); jupiter for women (dual)
  score_weight: 1.0
  citation: "BPHS Ch.17 v.2-8"
divorce:
  primary_houses: [6, 7, 12]        # 6th disputes; 7th spouse; 12th loss
  primary_lords: [6, 7, 12]
  karakas: [venus, mars]
  score_weight: 1.0
first_child:
  primary_houses: [5, 9]            # 5th progeny; 9th from 5th = 1st child
  primary_lords: [5, 9]
  karakas: [jupiter]
  score_weight: 1.0
father_death:
  primary_houses: [9, 3, 8]         # 9th father; 3rd = 12 from 4th; 8th from 9th
  primary_lords: [9, 8]
  karakas: [sun, saturn]
  score_weight: 1.0                 # death events carry high signal
  citation: "BPHS Ch.23 v.12-15"
career_start:
  primary_houses: [10, 6, 2]
  primary_lords: [10]
  karakas: [sun, saturn]
  score_weight: 0.8
major_illness:
  primary_houses: [6, 8, 12]
  primary_lords: [6, 8]
  karakas: [mars, saturn]
  score_weight: 0.9
# ... 15+ more categories in full file
```

### 3.4 Scoring Method 1: Dasa-AD timing

For each candidate birth time `t_c`:
1. Compute Vimshottari starting lord at `t_c` (requires natal Moon's nakshatra position — itself a function of `t_c`).
2. For each reported event date `e_date`:
   a. Determine active Mahadasa (MD) and Antardasa (AD) lords at `e_date`.
   b. Look up event category significations.
   c. Score `+N` for each match:
      - AD lord is house-significator of primary houses → `+5`
      - AD lord is karaka for category → `+5`
      - AD lord aspects/conjuncts primary lord → `+3`
      - MD lord matches significations → `+3` (lower weight because broader)
      - Either lord is placed in primary house → `+3`
      - Either lord is debilitated/combust in natal → `-2` (signal is distorted)
3. Sum across events: `dasa_score(t_c) = sum over events`.

Because MD/AD boundaries move as `t_c` moves, this method is **sensitive to birth time at AD-boundary resolution** (AD periods are weeks to months). Resolution: 1-60 minutes of birth time, typically.

### 3.5 Scoring Method 2: Slow-transit house matching

For each candidate `t_c` (which fixes natal houses and lord positions):
1. For each event date `e_date`:
   a. Compute transiting positions of Jupiter, Saturn, Rahu, Ketu (optionally Chiron) on `e_date`.
   b. For each slow planet, check which natal house it occupies AT `e_date`.
   c. Score `+N`:
      - Slow transit in primary house of event → `+5`
      - Slow transit aspects primary house (classical rashi-drishti) → `+3`
      - Slow transit conjunct/aspects primary house lord → `+3`
      - Multiple slow planets converging on primary house → `+5` (Saade Sati-like intensification)
2. Sum across events.

This method is sensitive to house-cusp position, which is sensitive to birth time at **Lagna-resolution** (about 4 min of birth time = 1° of Lagna).

### 3.6 Scoring Method 3: Secondary progressions

For each candidate `t_c`:
1. For each event date `e_date`:
   a. Compute "day-for-a-year" progressed positions: days_elapsed = (e_date - t_c).days / 365.25
   b. Progressed planet positions at `t_c + days_elapsed` (as real Julian days).
   c. Score `+N`:
      - Progressed Ascendant crosses natal planet within 1° → `+5`
      - Progressed MC crosses natal planet within 1° → `+4`
      - Progressed Moon aspects natal planet (0°, 60°, 90°, 120°, 180°) within 2° → `+3`
      - Progressed Sun aspects natal planet within 1° → `+3`
2. Sum across events.

Progressed Ascendant moves ~1° per year — this method has strong sensitivity to birth time (because MC/Asc are time-dependent) and strong sensitivity to event year.

### 3.7 Scoring Method 4: Varga consistency

Not event-specific; evaluates candidate's varga positions against reported long-term life pattern:

1. **Navamsa (D9) Lagna lord** — check if it's placed in a sign matching general "relationship success" pattern (if user reports happy marriage) or "relationship challenge" pattern (if difficult).
2. **Dasamsa (D10) Lagna lord** — similar for career satisfaction.
3. **Score `+N`**: match = +3; mismatch = -2; not reported = 0.

This method is weaker than the others but serves as a **tie-breaker** when dasa/transit/progression scores are close.

Only applied if user supplies general life-pattern self-report flags (e.g., `marriage_quality: happy | neutral | difficult | none`).

### 3.8 Coarse-to-fine search

**Pass 1 (coarse):** 5-minute resolution across full user window. For ±4h window: 96 candidates. Score each. Keep top 10.

**Pass 2 (fine):** 1-minute resolution across ±10 minutes of each top-10 coarse winner. That's 10 × 20 = 200 candidates. Score each. Keep top 5.

**Pass 3 (optional refinement):** 10-second resolution across ±1 minute of final top 5. For astrologer-pro mode; adds latency but improves precision to 10 seconds.

Total compute: ~300 candidate chart evaluations. Each chart ~50ms natal compute + ~100ms dasa/transit/progression scoring = ~150ms per candidate → 45 seconds total. Acceptable for async background job.

### 3.9 Bayesian prior formalism

Given user-supplied prior `mean = t_prior`, `sigma = sigma_prior` hours:

```
likelihood(t_c) = exp(score(t_c) / score_normalization)
prior(t_c) = exp(-0.5 * ((t_c - t_prior) / sigma_prior)^2)
posterior(t_c) ∝ likelihood(t_c) × prior(t_c)
```

`score_normalization` chosen so that a "perfect match" (all events align) maps to likelihood ~ 2; typical matches ~ 1.0-1.3.

If no prior supplied, uniform prior (likelihood alone drives ranking).

### 3.10 Test harness — ground truth charts

Astro-Databank tags birth-time records with `AA`, `A`, `B`, `C`, `X`, `XX` accuracy ratings. AA = official birth certificate to the minute. For test harness, we use 20 AA-rated celebrity charts as ground truth:
- Discard the true time.
- Provide engine with ±4h window centered on true time ± random offset (within window).
- Provide 6-10 well-documented life events from each celebrity's biography.
- Assert engine's top-1 candidate is within 15 min of true time in ≥ 70% of cases; top-5 contains truth in ≥ 90%.

Celebrities selected for event-density and public biographical record: Princess Diana, Barack Obama, Steve Jobs, Mahatma Gandhi, Nelson Mandela, Marilyn Monroe, Elvis Presley, John Lennon, Oprah Winfrey, Einstein, etc.

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| Single-method vs multi-method | Multi-method (4 techniques combined) | Single method fails on known edge cases; K.N. Rao explicit |
| Method weights | Configurable; defaults: dasa 0.35, transit 0.30, progression 0.20, varga 0.15 | Dasa + transit are highest-signal; varga is tie-breaker |
| Candidate window default | ±4h | Covers most "unknown to the hour" cases; configurable up to ±12h |
| Resolution | 1-minute (fine pass) | Matches astrologer manual precision; sub-minute rare need |
| Coarse-to-fine vs brute force | Coarse-to-fine | 300 evals vs 960; same outcome; 3× faster |
| Events required | Minimum 3, recommended 5+, optimal 7-10 | Fewer than 3 → insufficient signal; more than 10 diminishing returns |
| Event category extensibility | YAML-driven | Adding category is data change, not code |
| Bayesian prior optional | Yes, optional | Some users have no estimate; uniform prior fine |
| AI-mode auto-selection | No — always present top 5 with reasoning | Rectification is serious; user should pick explicitly |
| Astrologer override of engine top-5 | Yes, via workbench UI | Expert judgment can exceed algorithm |
| Store all 300 candidate scores | Only top 20 stored in DB | 300 × sessions × users = row explosion; 20 plenty for debug |
| Event date precision | ±1 day (user input); ±hour for progressions method (rare) | Day precision sufficient for dasa/transit |
| Re-rectification on same session | Allowed; creates new session; old session archived | Users revise event list |
| Rectified birth time updates chart in-place | No — creates NEW chart with flag `parent_chart_id` | Preserves audit; user may want to compare |
| Confidentiality of events | High — encrypted at rest; accessible only to session owner + assigned astrologer | Events may include sensitive health/family |
| Session expiry | 90 days | User reviews recommendations; then session archived |
| Retention of selected time | Indefinite (in chart record) | Chart is product of this session |
| Ayanamsa used during rectification | Match the target chart's ayanamsa | Consistent downstream |
| Native-timezone handling | Birth time input as local time + timezone; engine converts to UTC internally | Standard |
| Long-running async compute | Background job (arq / Celery) with status polling | 30-60s too long for sync HTTP |
| Astrologer-in-loop pricing | Handled by consultations module; not this PRD | Separation of concerns |

## 5. Component Design

### 5.1 New modules

```
src/josi/services/classical/rectification/
├── __init__.py
├── engine.py                       # RectificationEngine (orchestrator)
├── candidate_generator.py          # coarse-to-fine search
├── scoring/
│   ├── __init__.py
│   ├── dasa_scorer.py
│   ├── transit_scorer.py
│   ├── progression_scorer.py
│   └── varga_scorer.py
├── priors.py                       # Bayesian prior integration
├── event_categories.py             # loads YAML, exposes lookup
└── session_service.py              # CRUD over rectification_session

src/josi/data/
└── rectification_event_categories.yaml    # 20+ categories with significations

src/josi/api/v1/controllers/
└── rectification_controller.py

src/josi/workers/
└── rectification_worker.py         # background async job

src/josi/models/
└── rectification_session_model.py  # SQLModel for DB table
```

### 5.2 Data model additions

```sql
CREATE TABLE rectification_session (
    session_id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id        UUID NOT NULL REFERENCES organization(organization_id),
    user_id                UUID NOT NULL REFERENCES "user"(user_id),

    -- Input
    input_chart_id         UUID REFERENCES astrology_chart(chart_id),  -- optional; if refining existing
    approximate_birth_date DATE NOT NULL,
    birthplace_lat         NUMERIC(9,6) NOT NULL,
    birthplace_lon         NUMERIC(9,6) NOT NULL,
    birthplace_tz          TEXT NOT NULL,                              -- IANA
    candidate_window_start TIME NOT NULL,                              -- local time at birthplace
    candidate_window_end   TIME NOT NULL,
    input_events           JSONB NOT NULL,                             -- list of {date, category, description, confidence}
    user_prior             JSONB,                                      -- {mean_local_time, sigma_hours}
    life_pattern_flags     JSONB,                                      -- {marriage_quality, career_satisfaction, ...}

    -- Configuration
    method_weights         JSONB NOT NULL DEFAULT
                              '{"dasa": 0.35, "transit": 0.30, "progression": 0.20, "varga": 0.15}'::jsonb,
    ayanamsa               TEXT NOT NULL DEFAULT 'lahiri',
    mode                   TEXT NOT NULL CHECK (mode IN ('ai_auto', 'expert_assisted', 'hybrid'))
                              DEFAULT 'ai_auto',
    assigned_astrologer_id UUID REFERENCES "user"(user_id),            -- for expert_assisted

    -- Output
    candidate_times        JSONB,                                      -- top 20 with per-method scores
    selected_time_utc      TIMESTAMPTZ,                                -- final pick
    selected_candidate_idx INT,                                         -- 0-indexed into candidate_times
    confidence             NUMERIC(3,2),                               -- 0..1
    confidence_tier        TEXT CHECK (confidence_tier IN ('high','medium','low')),
    clear_winner           BOOLEAN,                                     -- top-1 beats top-2 by >20%
    method_used            TEXT,                                        -- 'multi' always in v1
    resulting_chart_id     UUID REFERENCES astrology_chart(chart_id),  -- chart created from selected time

    -- Lifecycle
    status                 TEXT NOT NULL CHECK (status IN
                              ('pending','computing','ready','selected','archived','failed'))
                              DEFAULT 'pending',
    status_message         TEXT,
    created_at             TIMESTAMPTZ NOT NULL DEFAULT now(),
    computed_at            TIMESTAMPTZ,
    completed_at           TIMESTAMPTZ,
    archived_at            TIMESTAMPTZ,
    expires_at             TIMESTAMPTZ NOT NULL DEFAULT (now() + INTERVAL '90 days'),

    -- Audit
    content_hash           CHAR(64),                                    -- input fingerprint
    engine_version         TEXT NOT NULL                                -- for reproducibility
);

CREATE INDEX idx_rectification_user ON rectification_session(user_id, created_at DESC);
CREATE INDEX idx_rectification_astrologer
  ON rectification_session(assigned_astrologer_id, status)
  WHERE assigned_astrologer_id IS NOT NULL;
CREATE INDEX idx_rectification_pending
  ON rectification_session(status, created_at)
  WHERE status IN ('pending', 'computing');
CREATE INDEX idx_rectification_expires
  ON rectification_session(expires_at)
  WHERE status != 'archived';
```

### 5.3 Output shape — propose new `rectification_result`

```python
# Proposed F7 shape addition (new output_shape_id = 'rectification_result')
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["session_id", "candidates", "best_candidate", "input_summary"],
  "properties": {
    "session_id": {"type": "string", "format": "uuid"},
    "input_summary": {
      "type": "object",
      "required": ["approximate_birth_date", "window", "event_count"],
      "properties": {
        "approximate_birth_date": {"type": "string", "format": "date"},
        "window": {
          "type": "object",
          "properties": {"start": {"type": "string"}, "end": {"type": "string"}}
        },
        "event_count": {"type": "integer", "minimum": 3},
        "categories_covered": {"type": "array", "items": {"type": "string"}}
      }
    },
    "candidates": {
      "type": "array",
      "minItems": 1,
      "maxItems": 20,
      "items": {
        "type": "object",
        "required": ["time_utc", "time_local", "total_score", "per_method", "rank"],
        "properties": {
          "rank": {"type": "integer", "minimum": 1},
          "time_utc": {"type": "string", "format": "date-time"},
          "time_local": {"type": "string"},
          "total_score": {"type": "number"},
          "confidence": {"type": "number", "minimum": 0, "maximum": 1},
          "per_method": {
            "type": "object",
            "properties": {
              "dasa": {"type": "number"},
              "transit": {"type": "number"},
              "progression": {"type": "number"},
              "varga": {"type": "number"}
            }
          },
          "reasoning": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "event_date": {"type": "string", "format": "date"},
                "event_category": {"type": "string"},
                "matches": {"type": "array", "items": {"type": "string"}}
              }
            }
          }
        }
      }
    },
    "best_candidate": {
      "type": "object",
      "required": ["time_utc", "confidence_tier"],
      "properties": {
        "time_utc": {"type": "string", "format": "date-time"},
        "confidence": {"type": "number"},
        "confidence_tier": {"type": "string", "enum": ["high","medium","low"]},
        "clear_winner": {"type": "boolean"}
      }
    }
  }
}
```

This shape is added to F1 `output_shapes.yaml` in E17's migration and F7 JSON Schema file.

### 5.4 API contract

```
POST /api/v1/rectification/run
Body:
{
  "approximate_birth_date": "1980-05-15",
  "birthplace": {"lat": 13.08, "lon": 80.27, "tz": "Asia/Kolkata"},
  "candidate_window": {"start_local": "00:00", "end_local": "08:00"},
  "events": [
    {"date": "2005-06-12", "category": "marriage"},
    {"date": "2008-03-05", "category": "father_death"},
    {"date": "2019-11-01", "category": "career_change",
     "description": "became a founder"},
    {"date": "2022-07-22", "category": "first_child"},
    {"date": "2015-09-14", "category": "major_illness"}
  ],
  "user_prior": {"mean_local_time": "05:30", "sigma_hours": 1.0},
  "life_pattern_flags": {"marriage_quality": "happy", "career_satisfaction": "high"},
  "method_weights": {"dasa": 0.40, "transit": 0.35, "progression": 0.15, "varga": 0.10},
  "mode": "ai_auto"
}
Response 202 (Accepted):
{
  "success": true, "message": "Rectification started",
  "data": {
    "session_id": "uuid",
    "status": "computing",
    "estimated_duration_sec": 45
  }
}

GET /api/v1/rectification/{session_id}
Response 200:
{
  "success": true, "message": "...",
  "data": {
    "session_id": "...",
    "status": "ready",
    "result": { ... rectification_result shape ... }
  }
}

POST /api/v1/rectification/{session_id}/select
Body: {"candidate_index": 0, "create_chart": true}
Response 200:
{
  "success": true,
  "data": {
    "selected_time_utc": "1980-05-15T00:17:00Z",
    "resulting_chart_id": "uuid",
    "session_status": "selected"
  }
}
```

### 5.5 Internal Python interface

```python
# src/josi/services/classical/rectification/engine.py

class RectificationEngine:
    def __init__(
        self,
        calc: AstrologyCalculator,
        dasa_scorer: DasaScorer,
        transit_scorer: TransitScorer,
        progression_scorer: ProgressionScorer,
        varga_scorer: VargaScorer,
        category_lookup: EventCategoryLookup,
    ):
        ...

    async def run(
        self,
        session: AsyncSession,
        input_data: RectificationInput,
    ) -> RectificationResult:
        """
        1. Validate input (≥3 events, window ≤12h, categories recognized).
        2. Generate coarse candidates (5-min resolution).
        3. Score each coarse candidate across 4 methods (parallel per candidate).
        4. Select top 10 coarse winners.
        5. Refine: generate 1-min candidates around each coarse winner (±10 min).
        6. Score fine candidates.
        7. Apply Bayesian prior if supplied.
        8. Rank; return top 5 for UI; top 20 stored in DB.
        9. Compute confidence tier + clear_winner flag.
        """

    async def score_candidate(
        self,
        candidate_time_utc: datetime,
        input_data: RectificationInput,
    ) -> CandidateScore:
        """
        Runs 4 scorers in parallel on one candidate; combines per method_weights.
        """


# src/josi/services/classical/rectification/scoring/dasa_scorer.py

class DasaScorer:
    def __init__(self, vimshottari_engine: VimshottariEngine,
                 category_lookup: EventCategoryLookup):
        ...

    def score(
        self,
        candidate_time_utc: datetime,
        events: list[Event],
        chart_context: ChartContext,   # lazy-computed natal at candidate time
    ) -> ScoreBreakdown:
        """
        For each event, find active MD+AD at event date via Vimshottari engine.
        Look up event category significations; accumulate matches.
        Return total score + per-event breakdown for reasoning.
        """
```

### 5.6 Worker architecture

Rectification is a 30-60s task — too long for sync HTTP. Use existing background task infrastructure (or add `arq` if not present):

- `POST /run` → create session row with `status=pending`; enqueue job; return 202.
- Worker picks up, transitions to `computing`, runs engine, writes top 20 candidates + best, transitions to `ready`.
- UI polls `GET /{session_id}` every 2s until `status=ready` or displays progress bar (progress = candidates_scored / total_candidates, exposed via heartbeat).

Worker retries on transient errors (3x); on permanent failure, `status=failed` + `status_message`.

### 5.7 AI chat tool integration

AI chat exposes:
```python
@tool
async def rectify_birth_time(
    user_id: UUID,
    approximate_date: str,       # ISO
    events: list[dict],
    birthplace: dict,
    window_hours: float = 4.0,
) -> dict:
    """Initiate rectification; returns session_id and ETA."""

@tool
async def get_rectification_result(session_id: UUID) -> dict:
    """Fetch rectification result; top 5 candidates with reasoning."""

@tool
async def select_rectification_candidate(session_id: UUID, rank: int) -> dict:
    """Select top-5 candidate; create chart from selected time."""
```

Chat flow:
1. User: "I don't know my exact birth time, can you figure it out?"
2. Chat: gathers approximate date + birthplace + window via dialog.
3. Chat: asks "Can you share 5-7 major life events with dates?"; categorizes from free text into known categories.
4. Chat: calls `rectify_birth_time`.
5. Chat: polls `get_rectification_result`.
6. Chat: presents top 5 with reasoning; asks user to pick.
7. User picks → chat calls `select_rectification_candidate` → chart created.

## 6. User Stories

### US-E17.1: As a diaspora user without birth certificate, I can rectify my time from life events
**Acceptance:** user provides approximate date (1988-03-15), window (00:00 - 08:00 IST), 6 life events; engine returns top 5 candidates within 60s; top candidate is within 15 min of user's self-report (if later corroborated).

### US-E17.2: As an AI chat user, rectification flows conversationally
**Acceptance:** I say "I don't know my birth time"; chat gathers events naturally; presents top 5 with human-readable reasoning ("Your Dasa of Saturn was active during your father's death in 2008, supporting birth time 02:34 AM").

### US-E17.3: As an astrologer in expert-assisted mode, I see full scoring breakdown
**Acceptance:** workbench shows per-candidate: dasa score + per-event match list, transit score + per-event, progression score, varga score, combined. I can override and pick a non-top-1 candidate with rationale.

### US-E17.4: As a developer, rectification recovers synthetic truth within ±15 min
**Acceptance:** test suite generates 20 synthetic charts with known times; blind-rectification recovers to within ±15 min in ≥ 70% of cases given 5+ events; top-5 includes truth in ≥ 90%.

### US-E17.5: As a user who selected a candidate, a new chart is created with that time
**Acceptance:** `POST /select` creates `AstrologyChart` row with `parent_chart_id` linking to any prior chart; downstream recomputes (via S6) use new birth time.

### US-E17.6: As a developer, rectification runs async and doesn't block HTTP
**Acceptance:** `POST /run` returns 202 within 500ms; worker processes in background; `GET /{session_id}` polling surfaces progress.

### US-E17.7: As a cost-sensitive operator, rectification stores only top 20 not 300 candidates
**Acceptance:** `rectification_session.candidate_times` JSONB size < 30KB per session; measured on real runs.

### US-E17.8: As a user, my event data is never exposed to other tenants
**Acceptance:** `rectification_session` has `organization_id` enforced; RBAC queries filter; audit log confirms.

### US-E17.9: As an astrologer, I can provide my own candidate time and have it scored
**Acceptance:** endpoint variant `POST /rectification/{session_id}/score-custom` accepts a candidate time, scores it with same 4-method pipeline, returns ScoreBreakdown.

### US-E17.10: As a user, the engine tells me when it's NOT confident
**Acceptance:** when top candidate's confidence < 0.5 OR `clear_winner=false`, UI displays "Low confidence — we recommend consulting a professional astrologer"; offers to assign to marketplace astrologer.

## 7. Tasks

### T-E17.1: Event category YAML + loader
- **Definition:** Author `rectification_event_categories.yaml` with 20 categories; build `EventCategoryLookup` loader.
- **Acceptance:** 20 categories load; lookup returns significations per category; unit tests cover lookups.
- **Effort:** 8 hours

### T-E17.2: Rectification session DB model + migration
- **Definition:** SQLModel `RectificationSession`; Alembic migration for table + indexes.
- **Acceptance:** Migration applies cleanly; rollback works; mypy passes.
- **Effort:** 4 hours

### T-E17.3: Candidate generator (coarse-to-fine)
- **Definition:** `CandidateGenerator` produces coarse grid (5-min) then fine grid (1-min around top 10).
- **Acceptance:** For ±4h window: 96 coarse candidates + 200 fine = 296 total; unit test asserts bounds.
- **Effort:** 6 hours

### T-E17.4: Dasa scorer
- **Definition:** `DasaScorer` uses Vimshottari engine (E1a) to find active MD+AD per event; scores matches per category significations.
- **Acceptance:** 5 synthetic fixtures produce scores matching hand-computed expectations.
- **Effort:** 14 hours
- **Depends on:** E1a, T-E17.1

### T-E17.5: Transit scorer
- **Definition:** `TransitScorer` uses transit engine (E6a) to locate slow planets at event dates; scores house-matter matches.
- **Acceptance:** 5 synthetic fixtures; scorer detects Saturn transit over 10H during career events.
- **Effort:** 12 hours
- **Depends on:** E6a

### T-E17.6: Progression scorer
- **Definition:** `ProgressionScorer` computes secondary progressions; scores angular contacts.
- **Acceptance:** Unit tests: progressed Ascendant advances ~1°/year from natal.
- **Effort:** 10 hours

### T-E17.7: Varga scorer
- **Definition:** `VargaScorer` evaluates D9 and D10 Lagna lord against life-pattern flags.
- **Acceptance:** When `marriage_quality=happy`, scorer returns positive for candidates with D9 Lagna lord in kendra; negative when in dusthana.
- **Effort:** 8 hours

### T-E17.8: Bayesian prior integration
- **Definition:** `priors.py` applies Gaussian prior to likelihood; uniform prior when absent.
- **Acceptance:** Unit test: given tight prior (σ=0.25h), top candidate pulled toward prior mean.
- **Effort:** 4 hours

### T-E17.9: Engine orchestrator
- **Definition:** `RectificationEngine.run` wires all scorers, generator, prior; parallelizes candidate scoring via asyncio.gather batches.
- **Acceptance:** End-to-end: given input, returns RectificationResult in < 60s on single request.
- **Effort:** 16 hours
- **Depends on:** T-E17.3 - T-E17.8

### T-E17.10: Background worker
- **Definition:** `rectification_worker.py` using existing async job infra (or arq). Picks up pending sessions; runs engine; writes results; marks complete.
- **Acceptance:** 10 concurrent sessions each finish < 90s; no deadlocks.
- **Effort:** 10 hours

### T-E17.11: API controllers
- **Definition:** `rectification_controller.py` with `POST /run`, `GET /{id}`, `POST /{id}/select`, `POST /{id}/score-custom`.
- **Acceptance:** All endpoints documented in OpenAPI; curl smoke tests succeed.
- **Effort:** 10 hours

### T-E17.12: AI chat tool registration
- **Definition:** Register `rectify_birth_time`, `get_rectification_result`, `select_rectification_candidate` as tools in AI orchestration (E11a). Write chat-flow prompts.
- **Acceptance:** AI completes a rectification flow in end-to-end demo.
- **Effort:** 8 hours
- **Depends on:** T-E17.11, E11a

### T-E17.13: Astrologer workbench integration
- **Definition:** E12 UI component: RectificationPanel showing candidates + scoring breakdown + override capability.
- **Acceptance:** Astrologer can view, select, or override candidate.
- **Effort:** 16 hours (frontend; deferred if E12 not ready — stub endpoint OK)
- **Depends on:** T-E17.11

### T-E17.14: Synthetic-ground-truth test harness
- **Definition:** Generate 20 synthetic charts with known times; run blind rectification; assert recovery metrics.
- **Acceptance:** 70%+ within ±15 min; 90%+ in top 5.
- **Effort:** 14 hours

### T-E17.15: Astro-Databank AA-rated regression
- **Definition:** 20 celebrity charts with documented AA-rated times + 6-10 biographical events each; regression suite.
- **Acceptance:** 60%+ within ±15 min; 85%+ in top 5. (Lower than synthetic because biographical event dates have ±week uncertainty.)
- **Effort:** 20 hours (data collection dominates)

### T-E17.16: F1 / F7 additions
- **Definition:** Add `rectification_modern`, `jh`, `cosmic_clock` source_authorities; `rectification` technique family; `rectification_result` output shape.
- **Acceptance:** DimensionLoader picks up additions; JSON Schema validates.
- **Effort:** 3 hours

### T-E17.17: Documentation
- **Definition:** CLAUDE.md: "rectification engine under `src/josi/services/classical/rectification/`". User-facing docs explain AI / expert / hybrid modes.
- **Acceptance:** Merged.
- **Effort:** 4 hours

### T-E17.18: Performance + cost budget
- **Definition:** Benchmark: 30-60s per session; memory < 500 MB during candidate scoring; DB writes batched.
- **Acceptance:** pytest-benchmark + load test with 10 concurrent sessions passes.
- **Effort:** 6 hours

## 8. Unit Tests

### 8.1 Event category lookup

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_all_20_categories_load` | startup | 20 loaded | completeness |
| `test_marriage_primary_houses_7_2_11` | lookup('marriage') | {7,2,11} | BPHS fidelity |
| `test_father_death_high_weight` | lookup('father_death') | weight=1.0 | high-signal event |
| `test_unknown_category_raises` | lookup('foo') | KeyError | safety |
| `test_category_yaml_schema_valid` | YAML | passes JSON Schema | data integrity |

### 8.2 Candidate generator

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_coarse_grid_96_for_8h_window` | ±4h, 5min | 96 candidates | resolution |
| `test_fine_grid_around_winners` | 10 coarse winners | 10×20=200 candidates | refinement |
| `test_no_duplicate_candidates` | overlapping fine windows | dedup via set | correctness |
| `test_window_clipped_to_birthday` | window straddling midnight | correctly handles date | edge case |

### 8.3 Dasa scorer

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_dasa_score_marriage_7L_active` | event marriage, AD lord = natal 7L | score += 5 | BPHS signification match |
| `test_dasa_score_father_death_venus_active` | event father_death, AD = Venus (not karaka) | score += 0 | karaka mismatch |
| `test_dasa_score_combust_lord_penalty` | AD lord combust | score -= 2 | signal distortion |
| `test_dasa_score_synthetic_truth_high` | synthetic chart where truth time's dasa fits all events | score > 20 | triangulation evidence |
| `test_dasa_score_wrong_time_low` | same events, wrong time by 2h | score < 8 | discrimination |

### 8.4 Transit scorer

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_transit_saturn_in_10H_career_event` | career_change event, Saturn transit in candidate's 10H | +5 | slow-transit match |
| `test_transit_jupiter_in_5H_child_birth` | first_child event, Jupiter in 5H | +5 | signification match |
| `test_transit_stacking_sadesati` | multiple slow planets hitting 1H/12H/2H | +5 for intensification | clustering bonus |
| `test_transit_no_match_returns_zero_per_event` | event with no relevant transits | 0 | neutral |

### 8.5 Progression scorer

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_progressed_asc_advance_1_deg_per_year` | natal → natal+10y | prog Asc ≈ natal Asc + 10° | secondary progression |
| `test_prog_asc_crosses_natal_venus_marriage` | fixture where progAsc crosses natal Venus at marriage event | +5 | angular contact |
| `test_prog_moon_aspect_within_orb` | prog Moon 88° from natal Sun | +3 (square within 2°) | soft aspect |

### 8.6 Varga scorer

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_d9_lagna_lord_kendra_marriage_happy` | happy marriage flag, D9 L1 in kendra | +3 | pattern match |
| `test_d9_lagna_lord_dusthana_marriage_happy_mismatch` | happy flag, D9 L1 in 6H | -2 | mismatch penalty |
| `test_no_flags_returns_zero` | no life_pattern_flags | 0 | graceful |

### 8.7 Bayesian prior

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_tight_prior_pulls_ranking` | uniform likelihoods + tight prior | top candidate near prior mean | prior integration |
| `test_flat_prior_no_effect` | no prior supplied | ranking = likelihood ranking | default |
| `test_wide_prior_weak_effect` | σ=4h, 8h window | ranking close to likelihood-only | weak prior |

### 8.8 Engine orchestrator

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_engine_end_to_end_synthetic` | 5 events, known truth | top-1 within ±15 min | core promise |
| `test_engine_returns_top_5` | valid input | result.candidates has 5 entries with rank 1..5 | API contract |
| `test_engine_confidence_tier_assignment` | high-agreement case | confidence_tier='high' | tier logic |
| `test_engine_clear_winner_flag` | top-1 score 22, top-2 score 17 | clear_winner=true (>20% margin) | margin rule |
| `test_engine_insufficient_events_raises` | 2 events | ValidationError "need ≥3 events" | guard |
| `test_engine_duration_budget` | 5 events, ±4h | completes < 60s | perf |

### 8.9 Synthetic-truth harness

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_synthetic_celebrity_fixture_01` | celebrity #1 with 8 events | top-1 within ±15 min | ground truth |
| ... | 20 fixtures | 70%+ within ±15 min; 90%+ top-5 | aggregate metric |

### 8.10 API + integration

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_post_run_returns_202` | valid POST | 202 + session_id | async semantics |
| `test_get_status_pending_then_ready` | poll | status transitions pending → computing → ready | lifecycle |
| `test_post_select_creates_chart` | valid select | new AstrologyChart row with parent_chart_id | chart creation |
| `test_tenant_isolation` | user A's session not visible to user B | 403/404 for user B | RBAC |
| `test_session_expiry_90d` | session age 91d | status='archived' | retention |
| `test_output_validates_rectification_result_schema` | any result | passes fastjsonschema | F7 parity |
| `test_idempotent_run_same_input` | same input 2x | 2 sessions (intentional; re-running allowed); same candidate_times | reproducibility |

## 9. EPIC-Level Acceptance Criteria

- [ ] `RectificationEngine` implements 4-method triangulation (dasa + transit + progression + varga)
- [ ] Coarse-to-fine search at 5-min then 1-min resolution
- [ ] Bayesian prior integration with Gaussian formalism
- [ ] Event categories loaded from YAML; 20+ categories covered
- [ ] `rectification_session` table with all indexes + tenant isolation
- [ ] 3 REST endpoints live: POST /run, GET /{id}, POST /{id}/select (+ optional score-custom)
- [ ] Async worker processes sessions with 30-60s target latency
- [ ] AI chat tools registered: rectify_birth_time, get_rectification_result, select_rectification_candidate
- [ ] 20 synthetic ground-truth fixtures; ≥70% within ±15 min; ≥90% in top 5
- [ ] 20 Astro-Databank AA-rated celebrity regressions; ≥60% within ±15 min
- [ ] New F1 rows: `rectification_modern` source_authority, `rectification` technique_family, `rectification_result` output_shape
- [ ] All outputs conform to proposed F7 `rectification_result` JSON Schema
- [ ] Unit test coverage ≥ 90% across `rectification/` package
- [ ] Performance: session completes < 60s for default window; memory < 500MB
- [ ] CLAUDE.md updated with rectification section
- [ ] Tenant isolation verified; events encrypted at rest
- [ ] Selected candidate creates chart via S6 downstream recompute

## 10. Rollout Plan

- **Feature flag:** `enable_rectification_engine` — default off in P1, on in P2 for astrologer-pro tier first, then for all users with explicit opt-in ("This is an experimental feature").
- **Shadow compute:** 2-week shadow: for users with known birth times who opt in, run rectification blind (hide true time); compare engine recovery to truth; log to `logs/rectification_shadow.log`; iterate on scoring weights based on error distribution.
- **Backfill strategy:** none — rectification is user-initiated per-session; no bulk backfill.
- **Rollback:** set flag off; API returns 503 Service Unavailable; existing sessions retained (no data loss); worker stops picking up new jobs.

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Scoring weights wrong for some categories → systematic bias | High | Medium | Configurable via method_weights; shadow-compute tunes weights; review every 2 weeks during P2 |
| Events mis-categorized by user/AI → bad scoring | High | Medium | Event categorization confidence threshold; AI reconfirms ambiguous events; "other" fallback excluded from scoring |
| Rectification accuracy insufficient for deep-probability claims | Medium | High | Clearly communicate confidence tier; recommend expert for low-confidence; never claim "your exact birth time is X" |
| Regulatory concerns around AI "divination" in some markets | Low | Medium | Frame as "calculation aid, not prophecy"; expert-assisted path always available |
| Event date precision ±week degrades progression scorer | Medium | Low | Dasa + transit methods less sensitive; progression weight reduced by default |
| Long compute blocks workers under load | Medium | Medium | Bounded worker pool; queue depth metric; autoscaling trigger |
| User provides 0 events → engine can't help | Low | Low | Validation: minimum 3 events; UI enforces; error message suggests event categories |
| Astrologer-provided events conflict with user events | Medium | Low | Expert mode allows astrologer to edit event list; audit trail preserves both |
| Event data sensitivity → privacy concerns | High | High | Encryption at rest; RBAC by organization_id; delete on session archive per GDPR; never log event descriptions in plaintext |
| Saved candidate times incorrect due to DST / timezone bugs | Medium | High | UTC storage everywhere; unit tests for DST-boundary births; explicit timezone in all user-facing display |
| High latency kills conversion in AI chat flow | Medium | Medium | Progress indicator; optimistic UI; allow user to skip and come back |
| Celebrity chart regression failures signal broader quality issue | Low | High | Pre-launch gate: must pass 85% top-5 metric before feature-flag on |
| Engine version change invalidates old sessions | Medium | Low | `engine_version` stored per session; old sessions marked with historical version; re-run button offered |
| 1-min resolution insufficient for equatorial latitudes (Lagna moves fast) | Low | Low | Astrologer-pro mode supports optional 10s resolution third pass |
| Varga scorer weak without life-pattern flags | Medium | Low | Documented as optional; reduced weight when flags absent |

## 12. References

- Master spec: [`docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`](../../../superpowers/specs/2026-04-19-classical-techniques-expansion-design.md)
- F1 dims: [`../P0/F1-star-schema-dimensions.md`](../P0/F1-star-schema-dimensions.md)
- F2 fact tables: [`../P0/F2-fact-tables.md`](../P0/F2-fact-tables.md)
- F6 Rule DSL: [`../P0/F6-rule-dsl-yaml-loader.md`](../P0/F6-rule-dsl-yaml-loader.md)
- F7 Output shapes: [`../P0/F7-output-shape-system.md`](../P0/F7-output-shape-system.md) — adds `rectification_result`
- E1a Multi-Dasa v1: [`../P1/E1a-multi-dasa-v1.md`](../P1/E1a-multi-dasa-v1.md)
- E6a Transit Intelligence v1: [`../P1/E6a-transit-intelligence-v1.md`](../P1/E6a-transit-intelligence-v1.md)
- E11a AI Chat Orchestration: [`../P1/E11a-ai-chat-orchestration-v1.md`](../P1/E11a-ai-chat-orchestration-v1.md)
- E12 Astrologer Workbench: [`./E12-astrologer-workbench-ui.md`](./E12-astrologer-workbench-ui.md)
- S6 Lazy Compute on Demand (compute infrastructure for downstream recomputation after rectification)
- **Classical & modern sources:**
  - *Brihat Parashara Hora Shastra* Ch. 1 v.33-42 (Santhanam trans., 2004) — rectification via events
  - *Jataka Parijata* Ch. 2 — dasa-event correspondence
  - K.N. Rao, *The Modern Way of Rectification*, Vani Publications, 2001 — 12 classical methods surveyed
  - V.P. Jain, *Advanced Techniques of Rectification*, 2006
  - Isaac Starkman, *Precise Times of Birth*, Israeli school, 1990s
  - James Eshelman, *Interpreting Solar Returns*, 1985 — progression events
  - Marc Edmund Jones, *Astrology: How and Why It Works*, 1945
  - Chris McRae, *Understanding Rectification*, 1999
- **Ground truth:**
  - Astro-Databank (https://www.astro.com/astro-databank) — AA-rated celebrity birth times
- Reference implementations:
  - Jagannatha Hora 7.x — "Rectification" panel
  - Solar Fire (commercial) — event-based rectification tool
  - Regulus (commercial) — primary-direction rectification
