---
prd_id: E10
epic_id: E10
title: "Prasna / Horary — Vedic (Kerala) + KP Unified"
phase: P2-breadth
tags: [#correctness, #ai-chat, #astrologer-ux, #extensibility]
priority: must
depends_on: [F1, F2, F6, F7, F8, F13, E1a, E5, E7, E9]
enables: [E12, E14a, P5-horary-marketplace]  # 2026-04-23: P2-UI-prasna resolved to E12 Astrologer Workbench UI (dedicated Prasna tab)
classical_sources: [prasna_marga, kp_reader, hora_deepika, jataka_parijata]
estimated_effort: 4-5 weeks
status: draft
author: "@agent"
last_updated: 2026-04-22
---

# E10 — Prasna / Horary — Vedic (Kerala) + KP Unified

## 1. Purpose & Rationale

Prasna (Sanskrit *praśna* = "question") is the classical discipline of answering a specific question based on the chart of the moment the question is asked. Unlike natal astrology, Prasna does not require the querent's birth details — only the time, place, and nature of the question. This makes it the most **immediately applicable** astrology in everyday life: "will my train arrive on time?", "should I take this job?", "is the lost necklace findable?"

Two classical systems dominate Indian practice:

1. **Kerala Prasna tradition** — codified in *Prasna Marga* (17th c, Kerala; Sanskrit verse) — the single most-cited Prasna text in Kerala, Tamil Nadu, and Sri Lanka. Deeply integrated with Sarvatobhadra Chakra (E7), omen analysis, and Tajaka aspects (E5).
2. **KP Horary** — K.S. Krishnamurti's 249-number method (E9) — the dominant horary in modern South Indian practice, offering a more mechanical/predictable outcome method.

These two traditions **are not in conflict** — they answer different question types better. Kerala Prasna excels at omens, lost articles, elemental questions (health, travel). KP excels at yes/no binary outcomes with confidence (marriage, career, litigation).

E10 delivers a **unified Prasna engine** that:
- Accepts a question (text + moment + location + optional category).
- Routes to both Vedic Kerala Prasna and KP Horary methods.
- Returns structured results from both, with **confidence-scored verdicts** and an AI-aided narrative synthesis.
- Lets the astrologer choose primary method via source preference; end-users get both by default (Ultra AI mode surfaces both separately).

Critically, E10 does **NOT** reimplement the KP horary mechanics (owned by E9) or the Tajaka aspects / Sahams (owned by E5). It **orchestrates** these engines via a new `PrasnaEngine` that invokes them with horary-appropriate inputs, plus adds Kerala-specific primitives:
- **Arudha of Prasna lagna** — derived position capturing the "apparent" reality of the question
- **Dasa of the moment** — current Vimshottari (MD→PD) at t_q applied to query-house analysis
- **Omen analysis** — ambient events at query time as auxiliary signals (rule-based; extensible)
- **Planetary hour (hora) of question**
- **Navamsa of Prasna chart** — yes/no refinement per Prasna Marga Ch. 8

The output is a `horary_analysis` shape (proposed new F7 shape; fallback to `structured_positions` with typed details if rejected) carrying both method results, per-method confidence, overall synthesis, and full reasoning trace.

## 2. Scope

### 2.1 In scope

- **Unified query model**:
  - `PrasnaQuery(user_id, question_text, moment_utc, location, intent_category: str | None = None, preferred_method: str = "both")`
  - Intent categorization (AI-assisted if `intent_category` not provided; standard 20 categories map to houses per E9 query map, extended for Prasna-specific intents)
- **Vedic Kerala Prasna analysis**:
  - Prasna lagna = Ascendant at t_q, location L
  - **Arudha of Prasna lagna** — per Prasna Marga Ch. 2: count from Lagna's sign to its lord's sign; same count from the lord yields the Arudha sign
  - **Dasa of moment** — Vimshottari MD/AD/PD at t_q (reuses E1a Vimshottari)
  - **Navamsa yes/no** — navamsa position of query-house lord indicates outcome per Prasna Marga Ch. 8
  - **Omen analysis** — rule-based scoring of ambient events (e.g., sound of bell = benefic; crow crosses path = malefic); extensible via YAML
  - **Planetary hour (hora) fitness** — hora lord at t_q vs question-category lord
- **KP Horary delegation**:
  - For KP analysis, E10 delegates to E9's `compute_horary()` method
  - Either: querent supplied a 249-number (call E9 directly); OR: no number supplied, E10 uses moment-based horary (horary Ascendant = astronomical Ascendant at t_q; otherwise KP analysis runs as normal)
- **Intent classification**:
  - Static table of 20 common intents (marriage, job, health, travel, lost_item, litigation, property, children, education, business, disease, journey_safety, proposal_acceptance, investment, election, contract_completion, reunion, pregnancy, relationship_longevity, exam_result)
  - AI-assisted classification for novel questions (uses Claude with few-shot prompt)
  - Each intent maps to house sets (primary/supporting/contra) — shared with E9 query map
- **Yes/No verdict extraction**:
  - Per-method verdict: `"yes" | "no" | "mixed" | "undetermined"` + confidence ∈ [0, 1]
  - Overall synthesis: weighted combination of both methods using configurable weights (default: 0.5 / 0.5)
- **Output shape: propose `horary_analysis`** (new 12th F7 shape; fallback to `structured_positions` with typed details)
- **Rule YAMLs** under `src/josi/rules/prasna/` for Prasna Marga-sourced rules; KP rules reused from E9
- **API surface**:
  - `POST /api/v1/prasna` — unified query endpoint
  - `GET /api/v1/prasna/{prasna_id}` — retrieve previous Prasna by id
  - `GET /api/v1/prasna/categories` — list of supported intent categories

### 2.2 Out of scope

- **Long-range retrospective validation** — validating historical Prasna questions against real outcomes (continuous learning) is an experimentation-framework concern (E14a).
- **Voice question intake** — UI concern (P5-voice-ai).
- **Lost-article directional analysis** — Prasna Marga Ch. 13 gives complex directional rules for lost items; deferred to E10b.
- **Death-time Prasna** — specialized and sensitive; explicitly out of scope for ethical reasons.
- **Prasna Jatakam** (natal prasna — using Prasna chart as a proxy natal when birth data unknown) — deferred to E10b.
- **Real-time omen capture** (e.g., user reports what they see/hear at t_q) — UI concern; engine supports structured omen inputs but UI collection is P3+.
- **Multi-person consultation scheduling** — marketplace feature (P5).
- **Tajaka Prasna (Annual-chart-based Prasna)** — a secondary Prasna method; deferred.
- **Querent authentication / fraud prevention** — platform concern.

### 2.3 Dependencies

- F1 — add `source_id='prasna_marga'`; add `source_id='hora_deepika'`; add `technique_family_id='prasna'`
- F2 — fact tables
- F6 — DSL loader (Prasna Marga rule YAMLs)
- F7 — propose new `horary_analysis` shape (fallback to `structured_positions`)
- F8 — aggregation protocol
- F13 — provenance on each Prasna (caching by (user_id, question_hash, moment))
- E1a — Vimshottari dasa computation
- E5 — Tajaka aspects (used in Prasna Marga's aspect analysis where references align)
- E7 — Sarvatobhadra Chakra (used for auxiliary omen-grid analysis); Upagrahas (for advanced Kerala Prasna)
- E9 — KP engine (delegated for KP horary)
- Existing `AstrologyCalculator` — Ascendant at arbitrary moment

## 2.4 Design Decisions (Pass 1 Astrologer Review — Locked 2026-04-22)

All open questions from E10 Pass 1 astrologer review are resolved. E10 orchestrates E5 (Tajaka) + E7 (SBC) + E9 (KP) + E1a (Vimshottari) + E4a (yogas). E10-specific decisions documented here.

### Cross-cutting + orchestration inheritance

| Decision | Value | Ref |
|---|---|---|
| Ayanamsa | Lahiri for Kerala branch; Krishnamurti for KP branch | DECISIONS 1.2 + E9 Q1 |
| Natchathiram count | 27 | DECISIONS 3.7 |
| Hora computation | Chaldean + variable-length | DECISIONS 3.11 |
| Sunrise/sunset | Center of disc + refraction | DECISIONS 2.3 |
| 5-level significators | KP Reader Vol.2 Ch.4 canonical | E9 Q2 |
| 5-element Ruling Planets | Day + Asc sign/natchathiram + Moon sign/natchathiram lords | E9 Q3 |
| 249-number horary | KP Reader Vol.3 canonical | E9 inheritance |
| Sarvathobhadra Chakra | BPHS Ch.86 9×9 grid | E7 Q2 |
| Tajaka aspects + Sahams | Tajaka Neelakanthi + 30 Sahams | E5 inheritance |
| Practice-type preset | Determines KP vs Kerala vs Both visibility | E9 Q5 |
| Arudha computation | JUS 1.2.39-45 canonical (E3 Q2 inheritance) | E3 Q2 |
| Language display | Sanskrit-IAST + Tamil phonetic | DECISIONS 1.5 |

### E10-specific decisions (locked this review)

| Decision | Value | Source |
|---|---|---|
| **Method routing** (Q1) | **Always run BOTH Kerala Prasna + KP Horary methods** for every query. Classical rigor; dual results with per-method reasoning trace. Matches JH Prasna module + PRD intent ("Ultra AI mode surfaces both"). Same for both user types. | Q1 |
| **Arudha of Prasna Lagna formula** (Q2) | **Same JUS 1.2.39-45 rule as natal Arudha (E3 Q2 inheritance).** 2 exception rules: (a) Arudha = Prasna Lagna itself → project to 10th from L, (b) Arudha = 7th from Prasna Lagna → project to 10th from L. Consistent with natal Arudha computation; Prasna Marga (17th c Kerala) follows JUS foundation. Matches JH + PL + Kerala tools + Sanjay Rath. | Q2 |
| **Omen rule scope** (Q3) | **Tiered:** 15 core always-available (temple bell, crow, cow, dog, sudden wind/rain, sweet/harsh sounds, directional signs, etc.) + 65 extended astrologer-toggle for comprehensive Nimitta Shastra coverage. Total 80 omens per Prasna Marga full canon. Progressive disclosure matches tiered decisions convention (E8b Q1, E7 scope). | Q3 |
| **Navamsa yes/no rule** (Q4) | **Prasna Marga Ch.8 canonical.** Lord of query-house in Navamsa dignity evaluation → yes / no / maybe verdict (own sign/exaltation/friend/benefic aspect = yes; enemy/debilitation/malefic = no; neutral = maybe). Strict single-source. Matches JH + PL + Kerala tools + Rath. | Q4 |
| **AI synthesis strictness (dual-method presentation)** (Q5) | **Dual display for astrologer + narrative synthesis for B2C.** Split by user type. **Astrologer workbench:** raw dual-method results with per-method reasoning trace (classical rigor). **B2C AI chat:** unified narrative synthesis weaving both Kerala + KP methods with agreement flag (AGREE / PARTIAL / DIVERGE). Matches Josi's two-user-type pattern. | Q5 |
| **Cross-source aggregation** (Q6) | **Strict single-source per branch.** Kerala Prasna = Prasna Marga canonical (17th c Kerala). KP = KP Reader Vols 1-6 (inherited from E9 Q6). No commentary variant toggles for MVP. Matches E9 Q6 single-source approach. Same for both user types. | Q6 |

### E10 engine output shape

```python
horary_analysis = {
    "query_id": str,
    "question_text": str,
    "moment_utc": datetime,
    "location": {lat: float, lon: float},
    "intent_category": str,  # marriage/career/lost_article/health/etc.
    "query_house": int,      # Mapped per E9 query map
    "kerala_prasna": {
        # Kerala branch uses Lahiri ayanamsa + Whole-Sign houses per DECISIONS §1.2 + §1.3 (Parashari primary)
        "prasna_lagna": rasi,
        "arudha_of_prasna_lagna": rasi,  # JUS rule
        "vimshottari_at_moment": {md: graha, ad: graha, pd: graha},
        "navamsa_yes_no": Literal["yes", "no", "maybe"],
        "planetary_hour_lord": graha,
        "omens_active": list[OmenResult],  # From user-reported + 15 core + astrologer-enabled extended
        "verdict": str,
        "confidence": float,
        "reasoning_trace": str
    },
    "kp_horary": {
        # KP branch uses Krishnamurti ayanamsa + Placidus houses per E9 Q1 (exclusive to KP chart; natal chart remains Lahiri+Whole-Sign)
        "horary_chart": ... ,  # From E9 (Krishnamurti ayanamsa + Placidus)
        "cuspal_sub_lord_analysis": {house: str},
        "ruling_planets": ... ,  # From E9
        "verdict": str,
        "confidence": float,
        "reasoning_trace": str
    },
    "synthesis": {
        "agreement_level": Literal["AGREE", "PARTIAL", "DIVERGE"],
        "astrologer_view": "dual_raw",  # Q5 astrologer UX
        "b2c_narrative": str,           # Q5 B2C AI-generated synthesis
        "combined_verdict": str,
        "combined_confidence": float
    },
    "source_attribution": {
        "kerala_source": "prasna_marga",
        "kp_source": "kp_reader_vols_1_6"
    }
}
```

### Engineering action items (not astrologer-review scope)

- [ ] Prasna Lagna computation at query moment (both Lahiri + Krishnamurti depending on branch)
- [ ] Arudha of Prasna Lagna using JUS 1.2.39-45 rule (reuse E3 logic)
- [ ] Navamsa yes/no computation per Prasna Marga Ch.8
- [ ] Planetary hour (Hora) lookup per DECISIONS 3.11
- [ ] Omen rule engine: 15 core + 65 extended with astrologer-profile enable toggle
- [ ] KP horary delegation to E9 engine
- [ ] Kerala Prasna + KP both-methods orchestrator
- [ ] Synthesis engine: agreement flag computation (AGREE/PARTIAL/DIVERGE) + B2C narrative AI
- [ ] Intent categorization AI layer (maps question text → house number)
- [ ] `horary_analysis` output shape per F7 (propose as new shape)
- [ ] REST endpoint: `POST /api/v1/prasna` with `PrasnaQuery` body
- [ ] Golden-test-fixture horary cases: 10 classical Prasna Marga examples + 10 KP Reader Vol.5/6 example horaries, cross-verified

---

## 3. Classical Research

### 3.1 Kerala Prasna Tradition — *Prasna Marga*

**Primary source:** *Prasna Marga* (Sanskrit: प्रश्नमार्ग), attributed to an anonymous Namputiri Brahmin of Kerala, ~1649 CE. Standard English edition: *Prasna Marga* trans. by B.V. Raman (2 volumes, 1984-1991, Motilal Banarsidas). 32 chapters (*adhyayas*) in ~1500 verses.

Additional Kerala sources:
- *Hora Deepika* (17th c; Tamil-Sanskrit) — Kerala-Tamil compendium
- *Jataka Desha Marga* (Kerala) — parallel treatment
- *Krishneeyam* (17th c) — mentioned in Raman's commentary

Key chapters of Prasna Marga:

| Ch. | Topic | Relevance |
|---|---|---|
| 1 | Preliminaries, invocations | context |
| 2 | Prasna Lagna and Arudha | **core** |
| 3 | Omens (Nimitta) | **core** |
| 4 | Aspects and benefic/malefic calculations | classical |
| 5-7 | House interpretations | shared |
| 8 | Navamsa in Prasna | **core yes/no** |
| 9 | Dasa in Prasna | **core** |
| 10 | Planetary hour (hora) | **core** |
| 11-14 | Specific question types (disease, litigation, travel, lost articles) | per-intent rules |
| 15-20 | Mundane and national Prasna | out of scope |
| 21-32 | Advanced topics | out of scope for E10 MVP |

### 3.2 Prasna Lagna and Arudha (Prasna Marga Ch. 2)

**Prasna Lagna (PL):** simply the Ascendant at the moment of question t_q computed at location L. Placidus or whole-sign — Kerala tradition uses whole-sign for Prasna (as distinct from KP's Placidus requirement).

**Arudha of Prasna Lagna (APL):** per PM 2.v3-7, a doubly-derived sign.

```
Let S_L = sign of Prasna Lagna (0..11)
Let L_L = lord of that sign
Let S_LL = sign occupied by L_L at t_q
Let count = (S_LL − S_L + 12) mod 12 + 1    # inclusive count from PL sign to lord's sign
Let APL_sign = (S_LL + count − 1) mod 12     # same count from lord's sign
```

PM 2.v5 commentary: Arudha is the "sign in which the questioner's reality appears to the querent" — a psychological or perceived-reality layer. It's used in combination with PL to triangulate the true situation.

**Classical rule:** if PL and APL are in mutual kendras (1/4/7/10 from each other), the question is "genuinely held" — confidence bonus. If PL is in 6/8/12 from APL, the querent is "deceived or mistaken" — confidence penalty.

E10 computes PL and APL, and scores the PL-APL relationship as a **confidence modifier** on the overall Prasna verdict.

### 3.3 Omens (Nimitta) — Prasna Marga Ch. 3

Kerala Prasna heavily integrates **nimitta** — omens surrounding the querent at t_q. PM Ch. 3 lists dozens of omens with benefic/malefic flags:

| Omen | Polarity | Verse |
|---|---|---|
| Sound of conch | strongly benefic | PM 3.12 |
| Sound of bell or cymbal | benefic | PM 3.13 |
| Chanting of Vedas nearby | benefic | PM 3.14 |
| Crow crossing path left-to-right | benefic | PM 3.24 |
| Crow crossing path right-to-left | malefic | PM 3.24 |
| Black cat crossing | malefic | PM 3.31 |
| Dog barking aggressively | malefic | PM 3.32 |
| Child crying | malefic | PM 3.40 |
| Flower falling on querent's head | benefic | PM 3.50 |
| Person greeting with folded hands | benefic | PM 3.52 |
| ... (~80 more) | | |

E10 ships an **omen rule registry** under `src/josi/rules/prasna/prasna_marga/omens/` with one YAML per omen. The Prasna API accepts an optional `observed_omens` array; each omen contributes a +/- score to a net `omen_score ∈ [-1, +1]`.

```json
"observed_omens": [
  {"code": "sound_conch", "at": "2026-04-20T10:12:33Z"},
  {"code": "child_crying", "at": "2026-04-20T10:13:01Z"}
]
```

If no omens supplied, omen_score = 0 (neutral).

### 3.4 Navamsa in Prasna (PM Ch. 8)

PM 8.v10-14 — the **navamsa of the query-house cusp** provides a yes/no refinement:

**For each intent category, there's a primary query house:**
- Marriage: 7
- Children: 5
- Career: 10
- Health recovery: 1 (or 8 for disease)
- Travel: 9 (long), 3 (short)
- Lost items: 2
- etc. (same map shared with E9)

**Algorithm:**
1. Identify query house H.
2. Compute navamsa of the cusp of H (or sign of H for whole-sign).
3. Find the lord of that navamsa sign.
4. Check that lord's relationship to query house in Prasna chart:
   - If navamsa lord is a benefic for H and in kendra/trikona of PL: **yes**.
   - If navamsa lord is afflicted (in 6/8/12, combust, debilitated, aspected by malefics): **no**.
   - Mixed signs: **mixed**.

E10 computes navamsa-based yes/no as one signal.

### 3.5 Dasa of the Moment (PM Ch. 9)

PM 9.v3-12 applies **Vimshottari Dasa at the moment of question** as a critical signal. The active MD, AD, and PD lords at t_q indicate whether the question is "ripe" for fruition:

- If active MD lord is a significator of query house H: **yes** (event time favors H).
- If active PD lord is a significator of H: **yes, soon** (near-term activation).
- If active MD lord is contra-significator: **no**.

E10 computes active MD/AD/PD at t_q (delegating to E1a's Vimshottari engine), then checks significator membership using the KP-style 5-level significators (reused from E9).

### 3.6 Planetary Hour (Hora) — PM Ch. 10

The 24-hour day is divided into 24 unequal *horas* (daylight horas for day, night horas for night). The first hora is ruled by the weekday lord, rotating through Sun → Venus → Mercury → Moon → Saturn → Jupiter → Mars → (back to Sun).

PM 10.v7: the hora at t_q adds "tone" to the Prasna — if hora lord is friendly to the question (e.g., Venus hora for marriage question): benefic shift; if hostile: malefic shift.

E10 maps intent → relevant-planet (marriage=Venus, children=Jupiter, career=Sun/Mars, health=Jupiter/Moon, travel=Mercury/Jupiter, etc.), then scores the hora lord's friendliness to the relevant planet via standard classical friendship tables.

### 3.7 Integration with KP

E10 **delegates to E9** for KP horary:
- If user supplied a 249-number: call `E9.compute_horary(number, t_q, location)`.
- If no number: call `E9.compute_horary_moment_based(t_q, location)` — a thin E9 helper that uses astronomical Ascendant at t_q as proxy for KP analysis.

The KP verdict (via cuspal sub-lord analysis §3.7 of E9) is a **binary signal** with confidence.

### 3.8 Yes/No Synthesis

E10 collects signals:

| Signal | Source | Weight (default) | Notes |
|---|---|---|---|
| KP CSL verdict | E9 | 0.30 | Binary +confidence |
| Navamsa analysis | Prasna Marga Ch. 8 | 0.20 | Ternary (yes/no/mixed) |
| Dasa at moment | Prasna Marga Ch. 9 | 0.20 | Binary |
| Omens | Prasna Marga Ch. 3 | 0.10 | −1..+1 |
| Hora lord tone | Prasna Marga Ch. 10 | 0.05 | −1..+1 |
| PL-APL relationship | Prasna Marga Ch. 2 | 0.05 | Confidence modifier |
| SBC fitness (from E7) | auxiliary | 0.10 | 0..1, centered to −1..+1 |

**Formula:**
```
score = sum(signal_value_i × weight_i)        # ∈ [-1, +1]
verdict = "yes" if score > 0.3
        = "no" if score < -0.3
        = "mixed" if |score| <= 0.3 and |score| > 0.1
        = "undetermined" if |score| <= 0.1
confidence = min(1.0, abs(score) + 0.3)       # heuristic; refined via E14a
```

Weights are configurable via `astrologer_source_preference.source_weights` for E10; default weights ship.

### 3.9 Alternatives considered

| Alternative | Rejected because |
|---|---|
| One Prasna method only (KP or Kerala) | Loses breadth; both traditions have complementary strengths |
| Reimplement KP in E10 | Duplicates E9; violates DRY |
| Include mundane/national Prasna (PM Ch. 15-20) | Out of scope; different use case |
| Fixed weights (no configuration) | Astrologer preferences vary; must expose |
| ML-based question classification | Over-engineered for 20 categories + AI fallback |
| Store Prasnas in dedicated table | Use `technique_compute` with family='prasna'; adds no schema complexity |
| Voice-capture omens | UI problem; structured omen input suffices for engine |

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| New output shape `horary_analysis` vs reuse | Propose new shape; fallback to `structured_positions` | Rich structure: two method results + synthesis + signal trace |
| House system for Kerala Prasna | Whole-sign | Kerala tradition; PM is pre-Placidus |
| House system for KP Prasna | Placidus (KP-required) | E9 policy |
| Question categorization | 20 static categories + AI fallback | Covers 95% + handles novel |
| AI classification model | Claude Haiku (cheap, fast, good enough for 20-way classification) | Latency budget for Prasna is < 5s end-to-end |
| Synthesis weights | Ship defaults; astrologer-overridable | Classical literature doesn't specify exact weights; let data decide (E14a) |
| Omen collection | Structured input array; no UI collection in E10 | Engine-only; UI is P3+ |
| Cache Prasna results | Yes, by (user_id, question_hash, moment_bucketed_to_minute) | Prasna is moment-specific; minute-bucketing catches re-renders |
| Retroactive outcome logging | Yes — `aggregation_signal` with `signal_type='outcome_positive/negative/neutral'` wired in E10 | Feeds E14a experimentation |
| Prasna for birth-data-unknown users | Yes, no natal chart required | Key differentiator vs other engines |
| Multi-language question text | Accept UTF-8 any language; classification uses Claude (multilingual) | Global accessibility |
| Questions about others (3rd person) | Supported; house map shifts to 7H-centered for spouse-matters, 5H for child-matters, etc. | PM Ch. 11 explicitly covers third-party Prasna |
| Sensitive questions (suicide, death-time) | Refuse at intent classification; return 403 with helpful message | Ethical |
| PrasnaQuery moment in the past | Allowed (retrospective analysis for learning) | Validator doesn't reject; flagged in response |

## 5. Component Design

### 5.1 New modules

```
src/josi/services/classical/
└── prasna/
    ├── __init__.py
    ├── engine.py                         # PrasnaEngine : ClassicalEngine (orchestrator)
    ├── query_model.py                    # PrasnaQuery Pydantic model
    ├── intent_classifier.py              # static table + AI fallback
    ├── kerala/
    │   ├── __init__.py
    │   ├── prasna_lagna.py               # PL computation
    │   ├── arudha.py                     # APL computation (PM Ch. 2)
    │   ├── omen_analyzer.py              # omen rule registry + scoring
    │   ├── navamsa_yesno.py              # PM Ch. 8
    │   ├── dasa_moment.py                # PM Ch. 9 — delegates to E1a
    │   └── hora_analyzer.py              # PM Ch. 10 planetary hour
    └── synthesis/
        ├── __init__.py
        └── verdict_synthesizer.py        # combines signals per §3.8

src/josi/schemas/classical/output_shapes/
└── horary_analysis.py                    # NEW SHAPE (proposal; fallback via details)

src/josi/rules/prasna/
├── prasna_marga/
│   ├── omens/                            # ~80 omen YAMLs
│   │   ├── sound_conch.yaml
│   │   ├── child_crying.yaml
│   │   └── ...
│   ├── arudha_rules.yaml
│   ├── navamsa_yesno.yaml
│   ├── dasa_of_moment.yaml
│   ├── hora_analyzer.yaml
│   └── pl_apl_relationship.yaml
└── hora_deepika/
    └── auxiliary_rules.yaml

src/josi/data/
└── prasna_intent_map.json                # 20 intents → house sets + relevant planets

src/josi/api/v1/controllers/
└── prasna_controller.py
```

### 5.2 Proposed new output shape: `horary_analysis`

```python
class PrasnaMethodResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    method:            str                                    # "kerala_vedic" | "kp"
    verdict:           str                                    # "yes" | "no" | "mixed" | "undetermined"
    confidence:        float = Field(..., ge=0.0, le=1.0)
    signal_values:     dict[str, float]                       # per-signal score in [-1, +1]
    rationale:         str                                    # narrative
    details:           dict[str, Any] = Field(default_factory=dict)

class HoraryAnalysis(BaseModel):
    model_config = ConfigDict(extra="forbid")

    prasna_id:         UUID
    question_text:     str
    intent_category:   str
    intent_confidence: float                                  # AI classifier confidence
    moment_utc:        datetime
    location:          dict[str, float]                       # {lat, lon}

    prasna_lagna_sign: int = Field(..., ge=0, le=11)
    arudha_sign:       int = Field(..., ge=0, le=11)
    pl_apl_relation:   str                                    # "kendra" | "trikona" | "dusthana" | "neutral"

    method_results:    list[PrasnaMethodResult]               # usually 2 (Kerala + KP)
    overall_verdict:   str                                    # "yes" | "no" | "mixed" | "undetermined"
    overall_confidence: float = Field(..., ge=0.0, le=1.0)
    synthesis_weights: dict[str, float]                       # weights used

    details:           dict[str, Any] = Field(default_factory=dict)
```

**Fallback:** if F7 rejects the shape, emit `structured_positions` with positions = [PL, APL, KP cusps subset] and put `HoraryAnalysis` typed as Pydantic model in `details.analysis`.

### 5.3 Data model additions

No new tables. Compute rows in `technique_compute` with `technique_family_id='prasna'`.

```sql
CREATE INDEX idx_prasna_compute_user_moment
  ON technique_compute (organization_id, chart_id, computed_at DESC)
  WHERE technique_family_id = 'prasna';

-- Prasna doesn't require a natal chart; for birth-unknown users, chart_id = a "null" sentinel
-- created per-user lazily for Prasna-only accounts.
```

**Note:** `technique_compute.chart_id` is NOT NULL per F2. For Prasna-only users (no natal chart), we create a minimal "Prasna-only chart" row (natal data = user-provided locality fallback, not time-specific). This keeps F2 FK integrity clean.

### 5.4 API contract

```
POST /api/v1/prasna
Body: {
  "question_text": "Will I get the marketing manager job I applied for?",
  "moment_utc": "2026-04-20T14:32:00Z",        // optional; default: server now
  "location": { "lat": 13.08, "lon": 80.27 },  // required
  "intent_category": "career",                  // optional; AI classifies if absent
  "preferred_method": "both",                   // "both" | "kerala_vedic" | "kp"
  "kp_number": 147,                             // optional; enables KP number-method horary
  "observed_omens": [                           // optional
    { "code": "sound_conch", "at": "..." }
  ],
  "natal_chart_id": "uuid"                      // optional; enriches analysis if natal known
}

Response 200: TechniqueResult[HoraryAnalysis]

GET /api/v1/prasna/{prasna_id}
Response: TechniqueResult[HoraryAnalysis] (cached retrieval)

GET /api/v1/prasna/categories
Response: list of 20 intent categories with house maps + relevant planets
```

### 5.5 Internal Python interface

```python
# src/josi/services/classical/prasna/engine.py

class PrasnaEngine(ClassicalEngineBase):
    technique_family_id: str = "prasna"
    default_output_shape_id: str = "horary_analysis"

    def __init__(
        self, kp_engine: KPEngine, kerala_engine: KeralaPrasnaEngine,
        intent_classifier: IntentClassifier, synthesizer: VerdictSynthesizer,
        calc: AstrologyCalculator,
    ): ...

    async def answer(
        self, session: AsyncSession, query: PrasnaQuery,
    ) -> TechniqueResult[HoraryAnalysis]:
        """
        1. Classify intent (static → AI fallback).
        2. Compute Prasna Lagna + Arudha (Kerala primitive).
        3. Kerala analysis:
             - Navamsa yes/no
             - Dasa of moment
             - Omens scoring
             - Hora analyzer
             - PL-APL modifier
        4. KP analysis: delegate to KPEngine.compute_horary(...)
        5. Synthesis: VerdictSynthesizer.combine(signals)
        6. Persist HoraryAnalysis to technique_compute.
        7. Return TechniqueResult[HoraryAnalysis].
        """

# src/josi/services/classical/prasna/intent_classifier.py

class IntentClassifier:
    STATIC_MAP: dict[str, IntentCategory]   # loaded from prasna_intent_map.json

    async def classify(self, question_text: str) -> tuple[str, float]:
        """Returns (category, confidence)."""
        # 1. Keyword heuristic match; if > 0.8 confidence, return.
        # 2. Else: Claude Haiku call with few-shot prompt.
        ...
```

## 6. User Stories

### US-E10.1: As a querent, I can ask a question without a natal chart and get a Prasna answer
**Acceptance:** `POST /api/v1/prasna` with `question_text`, `moment_utc`, `location`, no `natal_chart_id` returns HoraryAnalysis with both Kerala and KP results.

### US-E10.2: As a querent, I receive both Vedic and KP methods' results with clear verdict
**Acceptance:** response has 2 `method_results` entries, each with verdict + confidence + rationale; `overall_verdict` synthesized.

### US-E10.3: As a querent who knows KP, I can supply a 249-number for precise KP horary
**Acceptance:** `kp_number: 147` is used as KP Ascendant proxy; KP verdict reflects number-chart analysis.

### US-E10.4: As an omens-trained astrologer, I can supply observed omens and see their effect
**Acceptance:** adding `observed_omens: [{"code":"sound_conch"}]` vs omitting produces different `signal_values.omens` and potentially different overall verdict.

### US-E10.5: As a classical advisor, a known published Prasna example reproduces the classical verdict
**Acceptance:** Prasna Marga Ch. 8 Appendix Example 2 (question about journey) input reproduces verdict within confidence 0.6+.

### US-E10.6: As a Tamil-speaking user, I can ask in Tamil
**Acceptance:** `question_text` in Tamil classifies to correct intent via Claude (multilingual); response categories available in Tamil via `lang=ta` param (UI-layer; engine supports i18n in classical_names).

### US-E10.7: As the E14a experimentation framework, Prasna outcomes are trackable over time
**Acceptance:** `POST /api/v1/prasna/{id}/outcome` with `outcome="positive"|"negative"` inserts `aggregation_signal` with `signal_type='outcome_positive'`; E14a can aggregate.

### US-E10.8: As an AI chat surface, HoraryAnalysis validates against its shape
**Acceptance:** output passes `fastjsonschema.compile(horary_analysis_schema)(output)`.

### US-E10.9: As an ethical system, sensitive questions are refused with helpful redirect
**Acceptance:** question text classified as suicide/death/harm returns 403 with message redirecting to professional resources; no Prasna computation performed.

### US-E10.10: As an engineer, adding a new omen requires only YAML
**Acceptance:** creating `src/josi/rules/prasna/prasna_marga/omens/rainbow.yaml` + reloading yields support for `omen code: rainbow` without engine changes.

## 7. Tasks

### T-E10.1: PrasnaQuery Pydantic model + API surface scaffold
- **Definition:** `query_model.py` with PrasnaQuery; `prasna_controller.py` scaffold.
- **Acceptance:** POST /api/v1/prasna accepts minimal payload and returns 501 placeholder.
- **Effort:** 4 hours

### T-E10.2: Intent classification (static + AI)
- **Definition:** `intent_classifier.py` with 20-category map + Claude fallback.
- **Acceptance:** 20 clear questions classify via static map; 5 ambiguous questions correctly via Claude (unit test with vcrpy-recorded Claude responses).
- **Effort:** 10 hours

### T-E10.3: Prasna Lagna computation
- **Definition:** `prasna_lagna.py` — Ascendant at (t_q, location).
- **Acceptance:** 5 fixtures: PL sign matches Swiss Ephemeris output.
- **Effort:** 2 hours

### T-E10.4: Arudha of Prasna Lagna
- **Definition:** `arudha.py` per §3.2.
- **Acceptance:** 5 fixtures match hand-computed APL per PM Ch. 2 worked examples.
- **Effort:** 4 hours

### T-E10.5: Omen analyzer + ~80 omen YAMLs
- **Definition:** `omen_analyzer.py` loads omen registry; computes net omen_score.
- **Acceptance:** 10 omens with known polarity produce expected score; unit test scores sum correctly.
- **Effort:** 14 hours (YAML authoring dominates)

### T-E10.6: Navamsa yes/no analysis
- **Definition:** `navamsa_yesno.py` per §3.4 + PM Ch. 8 rules.
- **Acceptance:** PM Ch. 8 worked example reproduces; 3 additional fixtures.
- **Effort:** 8 hours

### T-E10.7: Dasa of moment
- **Definition:** `dasa_moment.py` uses E1a Vimshottari; checks significator membership with E9-style 5-level logic.
- **Acceptance:** 5 fixtures match hand-computed.
- **Effort:** 6 hours

### T-E10.8: Hora analyzer
- **Definition:** `hora_analyzer.py` — hora lord at t_q vs intent's relevant planet; friendship table.
- **Acceptance:** 10 moment fixtures return correct hora lord and tone.
- **Effort:** 6 hours

### T-E10.9: PL-APL relationship scorer
- **Definition:** Function to score PL-APL sign distance; return kendra/trikona/dusthana/neutral + confidence modifier.
- **Acceptance:** 8 PL-APL pair fixtures classify correctly.
- **Effort:** 4 hours

### T-E10.10: KP integration (delegate)
- **Definition:** Call E9.compute_horary() with number (if supplied) or moment-based; extract verdict + signal values.
- **Acceptance:** Both paths exercised; E9 integration test passes.
- **Effort:** 4 hours
- **Depends on:** E9 complete

### T-E10.11: VerdictSynthesizer
- **Definition:** `verdict_synthesizer.py` applies weighted formula §3.8; returns overall verdict + confidence.
- **Acceptance:** unit tests with constructed signal vectors produce expected verdicts at boundaries.
- **Effort:** 6 hours

### T-E10.12: HoraryAnalysis output shape
- **Definition:** Add `HoraryAnalysis` to F7 `SHAPE_REGISTRY`; update F7 PRD as AMENDMENT; JSON Schema derivation.
- **Acceptance:** Shape registered; `GET /api/v1/classical/output-shapes/horary_analysis` returns schema.
- **Effort:** 4 hours
- **Depends on:** F7 owner acceptance (same dependency as E9 kp_analysis)

### T-E10.13: PrasnaEngine orchestrator
- **Definition:** `engine.py` wires all modules; implements `answer()` per §5.5.
- **Acceptance:** Full integration test: 5 Prasna queries → 5 HoraryAnalysis outputs.
- **Effort:** 12 hours

### T-E10.14: API controller implementation
- **Definition:** `prasna_controller.py` with all endpoints; ethical filter for sensitive questions.
- **Acceptance:** All endpoints live; OpenAPI complete; 10 integration tests pass.
- **Effort:** 10 hours

### T-E10.15: Outcome logging endpoint
- **Definition:** `POST /api/v1/prasna/{id}/outcome` writes `aggregation_signal`.
- **Acceptance:** signal_row created; E14a reads it successfully.
- **Effort:** 4 hours

### T-E10.16: Golden fixtures
- **Definition:** 10 Prasna scenarios covering all 20 intent categories; each with expected verdict ± 1 (allowing mixed→yes/no as acceptable).
- **Acceptance:** 10 assertions with reasonable tolerance; fixtures include 3 known Prasna Marga worked examples.
- **Effort:** 20 hours

### T-E10.17: Ethical filter
- **Definition:** Intent classifier flags sensitive categories (suicide, self-harm, death-time, violence-against-others); controller returns 403 with resource redirect.
- **Acceptance:** 5 sensitive questions correctly refused; 20 non-sensitive accepted.
- **Effort:** 6 hours

### T-E10.18: Performance + caching
- **Definition:** Cache by (user_id, question_hash, moment_bucketed_to_minute, location_bucketed). P95 < 2.5 s end-to-end including AI classification.
- **Acceptance:** Locust test passes.
- **Effort:** 6 hours

### T-E10.19: Documentation
- **Definition:** CLAUDE.md Prasna section; API docs; educational content on Kerala vs KP distinctions.
- **Acceptance:** Merged.
- **Effort:** 4 hours

## 8. Unit Tests

### 8.1 Intent classification

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_static_marriage_keyword` | "Will I get married this year?" | category="marriage", confidence > 0.9 | static match |
| `test_static_career_keyword` | "Will I get the job?" | category="career" | static match |
| `test_ai_fallback_ambiguous` | "Is this move wise?" | AI returns category with confidence | fallback |
| `test_tamil_question_classifies` | Tamil marriage question | category="marriage" | multilingual |
| `test_20_categories_all_mapped` | full intent map | 20 entries | completeness |
| `test_sensitive_question_flagged` | suicide-ideation query | sensitive=True flag | ethical |

### 8.2 Prasna Lagna + Arudha

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_pl_computed_at_moment` | known moment+loc | matches Swiss Ephemeris Asc | astronomy |
| `test_apl_pm_ch2_example_1` | PM Ch.2 published example | APL_sign matches | classical |
| `test_apl_lord_same_sign_as_lagna` | lord of PL in PL sign | count=1; APL=PL | edge case |
| `test_apl_full_cycle_wraps` | long count | APL correctly modulo 12 | wrap |
| `test_pl_apl_kendra_relationship` | PL=Aries, APL=Cancer | relation="kendra" | §3.2 |
| `test_pl_apl_dusthana_relationship` | PL=Aries, APL=Virgo (6th) | relation="dusthana" | §3.2 |

### 8.3 Omen analyzer

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_single_benefic_omen` | sound_conch | omen_score = +0.6 (registry value) | basic |
| `test_single_malefic_omen` | child_crying | omen_score = −0.4 | basic |
| `test_multiple_omens_sum` | 2 benefic + 1 malefic | weighted sum in [-1, +1] | composition |
| `test_no_omens_neutral` | empty list | omen_score = 0 | default |
| `test_unknown_omen_code_ignored` | "rainbow_unicorn" | ignored; no error; logged | resilience |
| `test_80_omens_load_cleanly` | boot | 80 YAMLs parse | data integrity |

### 8.4 Navamsa yes/no

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_navamsa_marriage_benefic_lord` | 7H navamsa lord benefic in kendra of PL | verdict="yes" | PM Ch.8 |
| `test_navamsa_marriage_afflicted_lord` | lord in 8H, combust | verdict="no" | affliction |
| `test_navamsa_mixed` | partial support | verdict="mixed" | ternary |
| `test_navamsa_pm_ch8_appendix_ex2` | PM Ch.8 App Ex 2 | matches published | canonical |

### 8.5 Dasa of moment + Hora

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_dasa_md_significator_of_query_house` | MD=Jupiter, 7H significator | signal=+0.7 | PM Ch.9 |
| `test_dasa_md_contra_significator` | MD=Ketu, 7H contra | signal=−0.5 | PM Ch.9 |
| `test_dasa_pd_ripens_signal` | PD is primary significator | signal_boost | near-term |
| `test_hora_venus_for_marriage` | Venus hora, marriage query | tone=+1 | PM Ch.10 |
| `test_hora_saturn_for_marriage` | Saturn hora | tone=−0.5 | hostile |
| `test_hora_weekday_rotation` | Sunday 1st hora | Sun hora | rotation |

### 8.6 Synthesis

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_all_signals_strongly_positive` | score=+0.8 | verdict="yes", conf ≥ 0.9 | clear yes |
| `test_all_signals_strongly_negative` | score=−0.8 | verdict="no", conf ≥ 0.9 | clear no |
| `test_mixed_signals_small_positive` | score=+0.15 | verdict="mixed" | boundary |
| `test_mixed_signals_near_zero` | score=0.05 | verdict="undetermined" | low signal |
| `test_kp_and_kerala_disagree` | KP=+1, Kerala=−1 | verdict based on weighted sum; rationale notes disagreement | conflict handling |
| `test_custom_weights_shift_verdict` | high KP weight vs high Kerala weight on same signals | different overall verdicts | configurability |

### 8.7 KP integration

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_kp_with_249_number` | kp_number=147 | E9 compute_horary called with 147 | number path |
| `test_kp_without_number_moment_based` | no kp_number | E9 called with moment Ascendant | moment path |
| `test_kp_verdict_extracted_into_method_result` | E9 returns KPAnalysis | PrasnaMethodResult has verdict+conf | extraction |

### 8.8 Ethical filter

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_suicide_question_403` | "should I end my life" | 403; redirect message | ethics |
| `test_death_time_prediction_403` | "when will X die" | 403 | ethics |
| `test_harm_to_others_403` | "how to harm Y" | 403 | ethics |
| `test_normal_questions_pass` | 20 standard queries | all 200 | no false positives |

### 8.9 Integration

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_horary_analysis_output_validates_schema` | output | passes horary_analysis JSON Schema | F7 parity |
| `test_prasna_engine_full_path` | POST /prasna | HoraryAnalysis returned; 1 technique_compute + 1 aggregation_event | E2E |
| `test_prasna_cache_hit` | same query twice within 60s | second response faster; same result | caching |
| `test_prasna_outcome_logging` | POST .../{id}/outcome | aggregation_signal row created | E14a hook |
| `test_prasna_works_without_natal_chart` | no natal_chart_id | valid HoraryAnalysis returned | no-natal support |
| `test_prasna_pm_ch8_appendix_ex2_end_to_end` | canonical question | verdict matches within confidence 0.6 | canonical verification |

## 9. EPIC-Level Acceptance Criteria

- [ ] `PrasnaQuery` model + API endpoints live
- [ ] Intent classifier: 20 static categories + Claude fallback; ≥ 95% accuracy on internal fixture set
- [ ] Prasna Lagna + Arudha computed per PM Ch. 2
- [ ] ~80 omens loaded as rule YAMLs; composable omen_score
- [ ] Navamsa yes/no analysis per PM Ch. 8
- [ ] Dasa-of-moment signal extraction per PM Ch. 9 using E1a Vimshottari
- [ ] Hora analyzer per PM Ch. 10
- [ ] PL-APL relationship scorer per §3.2
- [ ] KP horary delegation to E9 (both number-based and moment-based paths)
- [ ] VerdictSynthesizer combines signals with configurable weights; produces yes/no/mixed/undetermined + confidence
- [ ] New output shape `horary_analysis` proposed to F7 (or fallback to `structured_positions` + typed details)
- [ ] All outputs validate against chosen F7 shape schema
- [ ] API endpoints live: POST /prasna, GET /prasna/{id}, GET /prasna/categories, POST /prasna/{id}/outcome
- [ ] Ethical filter blocks sensitive questions
- [ ] Golden fixtures: 10 Prasna scenarios including 3 PM canonical examples; all assertions green
- [ ] Outcome logging wires to `aggregation_signal` for E14a consumption
- [ ] Unit test coverage ≥ 90% across `prasna/` package
- [ ] Integration tests cover full path (compute → persist → aggregate → API) for both Kerala and KP methods
- [ ] Performance: P95 < 2.5 s end-to-end (including AI classification)
- [ ] CLAUDE.md updated with Prasna section
- [ ] Multilingual question support tested (English, Tamil, Hindi at minimum)

## 10. Rollout Plan

- **Feature flag:** `enable_prasna_engine` — off at merge; on in P2 for astrologer Pro users first, then B2C after 2-week soak.
- **Shadow compute:** 1 week shadow on internal test queries; verify classifier accuracy and verdict sanity.
- **Backfill:** N/A (Prasna is query-time-only, no historical backfill).
- **Rollback:** disable feature flag; endpoints return 501; no data destruction.

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| AI classifier misroutes questions | Medium | High | 20-category static map covers majority; AI is fallback; unit tests on internal fixture set; log all AI classifications for audit |
| KP moment-based horary (no number) is non-classical | Certain | Medium | Document clearly; recommend number-based in UI; engine computes both if available |
| Omen YAML drift (classical variants) | Medium | Low | Single-source from PM Ch. 3; variants go into source_id='hora_deepika' |
| Synthesis weights disagree with astrologers | High | Medium | Defaults + per-astrologer override; E14a experiments refine |
| Ethical filter false positives/negatives | Medium | High | Conservative-yet-not-restrictive keyword + AI; human review of flagged queries |
| Multilingual classification varies in quality | Medium | Medium | Claude Haiku is strong multilingual; fallback to English translation for truly obscure languages |
| Dasa-of-moment requires full natal chart (but Prasna doesn't) | Medium | Medium | Use moment-based "synthetic" Vimshottari (starting lord from moment Moon's nakshatra); documented |
| Caching by minute-bucket loses precision for rapid re-queries | Low | Low | Acceptable trade-off; re-query within same minute = same answer is desired |
| Outcome logging exposes private questions | Medium | High | Outcome endpoint is user-authenticated; privacy review; no cross-user leakage |
| PM Ch.8-style navamsa rules incomplete for modern question types | Medium | Low | Graceful fall-back to "undetermined"; no false confidence |
| Claude Haiku latency spikes degrade P95 | Medium | Medium | Timeout at 2s; fall back to "other" category; retry once |
| 80-omen registry becomes unwieldy | Low | Low | One YAML per omen; F6 loader is O(N); 80 × 1ms = 80 ms at startup |
| F7 rejects new shape | Medium | Medium | Fallback plan: structured_positions with typed details; no functionality loss |

## 12. References

- Master spec: [`docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`](../../../superpowers/specs/2026-04-19-classical-techniques-expansion-design.md) §2.2 (prasna technique_family)
- F1 dims: [`../P0/F1-star-schema-dimensions.md`](../P0/F1-star-schema-dimensions.md) — `source_id='prasna_marga'`, `source_id='hora_deepika'`, `technique_family_id='prasna'`
- F2 fact tables: [`../P0/F2-fact-tables.md`](../P0/F2-fact-tables.md)
- F6 Rule DSL: [`../P0/F6-rule-dsl-yaml-loader.md`](../P0/F6-rule-dsl-yaml-loader.md)
- F7 Output shapes: [`../P0/F7-output-shape-system.md`](../P0/F7-output-shape-system.md) — proposal to add `horary_analysis` as 12th shape
- F8 Aggregation: [`../P0/F8-technique-result-aggregation-protocol.md`](../P0/F8-technique-result-aggregation-protocol.md)
- E1a Multi-Dasa v1 — Vimshottari reused for dasa-of-moment
- E5 Varshaphala/Tajaka — Tajaka aspects referenced in advanced Kerala Prasna analysis
- E7 Vargas/SBC/Upagrahas — SBC used for auxiliary omen-grid scoring
- E9 KP System — delegated for KP horary
- E14a Experimentation framework — consumes Prasna outcome signals
- **Classical sources:**
  - *Prasna Marga* (Kerala, ~1649 CE), trans. B.V. Raman, 2 vols, 1984-1991, Motilal Banarsidas — Ch. 2 (Prasna Lagna + Arudha), Ch. 3 (Omens), Ch. 8 (Navamsa), Ch. 9 (Dasa), Ch. 10 (Hora), Ch. 11-14 (intent-specific rules)
  - *Hora Deepika* (17th c Kerala-Tamil compendium) — Raman commentary
  - *Jataka Desha Marga* (Kerala parallel)
  - *Krishneeyam* (17th c; cited in Raman's Prasna Marga introduction)
  - K.S. Krishnamurti, *KP Reader Vol IV*, 1977 — KP horary (via E9 delegation)
- **Reference implementations:**
  - Jagannatha Hora 7.41 — Prasna module (Kerala-oriented)
  - KP Astro — KP Horary module (delegation target via E9)
  - Parashara's Light 9.0 — Prasna module (commercial)
- **AI classification prompt template:** internal; few-shot with 20-category examples; uses Claude Haiku at temperature 0.0 for deterministic routing
