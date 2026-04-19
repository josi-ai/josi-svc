---
prd_id: D1
epic_id: D1
title: "Voice-native AI astrologer (real-time voice-in / voice-out consultations)"
phase: P5-dominance
tags: [#ai-chat, #end-user-ux, #i18n, #performance]
priority: must
depends_on: [F9, F10, F11, F12, E11a, E11b, D3]
enables: [D6, I6]
classical_sources: [bphs, saravali, phaladeepika, jaimini_sutras, kp_reader]
estimated_effort: 10-14 weeks
status: draft
author: "@agent"
last_updated: 2026-04-19
---

# D1 — Voice-Native AI Astrologer

## 1. Purpose & Rationale

Text chat is a compromise. Astrology is an oral tradition — transmitted verbally across millennia. A user asking "tell me about my Sade Sati" in their mother tongue, hearing a natural-voice response that correctly pronounces *Shani*, *dhaiya*, *dhrishti*, and cites verses in resonant Sanskrit, is a qualitatively different product from text.

Voice unlocks:
1. **New user segments** — elders, low-literacy users, commuters, drivers. A significant fraction of Josi's Indian diaspora target audience prefers voice for religious/spiritual content.
2. **Premium monetization** — $1/min pricing tier, no per-token economics confusion, aligns with existing astrologer-marketplace pricing anchors (D4).
3. **Trust & engagement** — prosody conveys confidence and gravitas; voice sessions show 3-5x the session length of text in adjacent categories (meditation apps, language tutors).
4. **Accessibility moat** — voice with correct classical-term pronunciation across Indic languages is hard to replicate quickly.

## 2. Scope

### 2.1 In scope
- Real-time bidirectional voice session (WebRTC or comparable) with sub-second latency
- Integration with a voice-in/voice-out LLM API (Claude voice API, GPT voice API, or equivalent; selected at phase start based on quality benchmarks)
- Custom voice synthesis for classical-term pronunciation (ElevenLabs or equivalent with pronunciation dictionaries)
- Multi-language at launch: Hindi, Tamil, English, Telugu, Bengali, Marathi
- Session continuity: the voice agent has full access to the user's `chart_reading_view`, prior sessions, and AI-tool-use contract (F10) — a voice session is a voice-rendered AI chat
- $1/min metered billing with pre-session balance hold
- Transcript capture (server-side) for safety, quality evaluation, and longitudinal-dashboard ingestion (D6)
- Voice-mode equivalent of citation disclosure: the agent can say "according to BPHS chapter 36" and on-screen an ambient citation card appears
- Barge-in: user can interrupt the agent mid-sentence

### 2.2 Out of scope
- On-device voice processing (all inference cloud-side in this phase)
- Voice cloning of specific astrologers (D8 / marketplace concern, separate PRD)
- Voice-based chart creation ("my birthday is …") — in this PRD we assume the chart is already created; entry point is chart-aware voice only
- Languages beyond the 6 launch set (covered by D3 for 20+)
- Offline mode

### 2.3 Dependencies
- Chart data and yoga/dasa/transit computes must already be available via F9 (`chart_reading_view`) and F10 (typed tool-use)
- Citation shape (F11) exposed to voice-mode UI
- Prompt caching (F12) used to keep per-minute cost economic
- E11b debate-mode for Ultra voice tier (optional upgrade path)

## 3. Technical Research

### 3.1 Voice API comparison (decision at phase start)

| Candidate | Pros | Cons |
|---|---|---|
| Claude voice API (if released by phase start) | Unified agent context with text tier; same tool-use contract | Availability unknown at PRD time; may lack Indic voice quality |
| OpenAI Realtime API (GPT voice) | Mature Indic TTS via voice variants; low-latency WebRTC | Separate vendor from text chat; dual tool-use plumbing |
| Gemini Live | Strong multilingual; Google pronunciation for Indic | Safety/content moderation differs from text tier |
| Split architecture: STT (Deepgram/Whisper) → text LLM → TTS (ElevenLabs) | Most control; best classical-term pronunciation | Higher end-to-end latency (~1.5–2.5s); more moving parts |

Decision criteria locked: latency P95 < 800ms round-trip; correct pronunciation of a 100-term classical glossary in each of 6 languages ≥ 95%; cost per minute < $0.25 at 10M MAU projected volume. Final vendor selection TBD at phase start.

### 3.2 Pronunciation strategy

Classical astrology has a ~500-term glossary (Sanskrit: *rashi*, *nakshatra*, *dasha*, *yoga* names; Tamil: *padham*, *navamsam*; Arabic/Tajaka loanwords). Generic TTS mispronounces these. Strategy:
- Maintain `src/josi/content/voice/pronunciation_dict/` — one YAML per language mapping term → IPA + phonetic hints
- TTS engine (ElevenLabs Pronunciation Dictionary or vendor equivalent) loads dict per session based on language
- Dict entries versioned; when a classical advisor corrects a pronunciation, it's a PR against YAML (same review pattern as F6 rule DSL)

### 3.3 Latency budget

P95 end-to-end target: 800ms from end-of-user-utterance to start-of-agent-speech.

| Segment | Budget |
|---|---|
| Voice activity detection + stop-of-speech | 150ms |
| STT (streaming) | 150ms |
| LLM first-token (with prompt cache hit via F12) | 250ms |
| Tool call round-trip (if triggered; <40% of turns) | 200ms (parallel with LLM streaming) |
| TTS first-audio | 150ms |
| Network jitter buffer | 100ms |

Barge-in: on speech-detect event, cancel TTS stream immediately; preserve partial transcript for context.

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| Voice API vendor | TBD at phase start against latency/quality/cost criteria above | Market will shift before P5 execution |
| Store audio vs transcript only | Transcript + audio (opt-in for audio) | Transcript always needed for safety/D6; audio opt-in respects privacy |
| Voice identity | Start with 2-3 vendor voices per language, neutral; premium voice personas in P6 | Keep scope focused; persona-voice is separate product |
| Pricing model | $1/min wall-clock; 60s free trial per new user | Matches industry anchor (marketplace astrologers); trial drives conversion |
| Interruption semantics | Barge-in always on; agent pauses on speech-detect | Natural conversation expectation |
| Offline/local | Not in P5 scope | Premium users are online; cost of on-device model quality not yet warranted |

## 5. Component Design

### 5.1 New services / modules

```
src/josi/voice/
├── __init__.py
├── session_manager.py          # lifecycle: create, heartbeat, teardown, billing
├── voice_provider/
│   ├── base.py                 # VoiceProvider ABC
│   ├── realtime_llm.py         # Claude/GPT/Gemini voice adapter
│   └── split_stack.py          # STT + text-LLM + TTS fallback adapter
├── pronunciation/
│   ├── loader.py               # loads YAML dict per language
│   └── injector.py             # patches TTS calls with dict overrides
├── billing.py                  # per-minute meter, pre-hold, post-debit
├── transcript_store.py         # writes to voice_session + voice_turn tables
└── tool_bridge.py              # bridges voice provider to F10 typed tool-use

src/josi/content/voice/pronunciation_dict/
├── hi.yaml
├── ta.yaml
├── en.yaml
├── te.yaml
├── bn.yaml
└── mr.yaml

src/josi/api/v1/controllers/voice_controller.py
  # POST /api/v1/voice/session/start   → returns WebRTC offer / session token
  # POST /api/v1/voice/session/end
  # GET  /api/v1/voice/session/{id}/transcript
```

### 5.2 Data model additions

```sql
CREATE TABLE voice_session (
    voice_session_id     UUID PRIMARY KEY,
    user_id              UUID NOT NULL REFERENCES user_account(user_id),
    organization_id      UUID NOT NULL,
    chart_id             UUID REFERENCES chart(chart_id),
    language             TEXT NOT NULL,
    provider             TEXT NOT NULL,          -- 'claude_voice' | 'gpt_voice' | 'split_stack' ...
    voice_persona        TEXT,
    started_at           TIMESTAMPTZ NOT NULL,
    ended_at             TIMESTAMPTZ,
    duration_seconds     INTEGER,
    billed_cents         INTEGER,
    audio_opt_in         BOOLEAN NOT NULL DEFAULT false,
    audio_blob_uri       TEXT,                    -- GCS URI if audio_opt_in
    ended_reason         TEXT,                    -- 'user' | 'balance' | 'timeout' | 'error'
    created_at           TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE voice_turn (
    voice_turn_id        UUID PRIMARY KEY,
    voice_session_id     UUID NOT NULL REFERENCES voice_session(voice_session_id),
    turn_index           INTEGER NOT NULL,
    speaker              TEXT NOT NULL CHECK (speaker IN ('user','agent')),
    transcript           TEXT NOT NULL,
    tool_calls           JSONB,                    -- list of {name, args, result_summary}
    citations            JSONB,                    -- list of {source_id, citation}
    latency_ms           INTEGER,
    started_at           TIMESTAMPTZ NOT NULL,
    ended_at             TIMESTAMPTZ
);

CREATE INDEX idx_voice_session_user_time ON voice_session (user_id, started_at DESC);
CREATE INDEX idx_voice_turn_session ON voice_turn (voice_session_id, turn_index);
```

### 5.3 API contract

```
POST /api/v1/voice/session/start
Body: { "chart_id": "...", "language": "hi", "voice_persona": "default" }
Response: {
  "success": true,
  "data": {
    "voice_session_id": "...",
    "webrtc_offer": "...",
    "token": "...",
    "price_per_minute_cents": 100,
    "balance_remaining_minutes": 12.3
  }
}
```

## 6. User Stories

### US-D1.1: As a Hindi-speaking elder, I want to ask my daughter's grandfather-name in voice and receive natural-sounding Hindi with correct Sanskrit pronunciation
**Acceptance:** audio output is judged natural by 3-of-3 native-speaker reviewers; Sanskrit terms (rashi names, dasa names, nakshatra names) pronounced correctly in ≥ 95% of sampled turns.

### US-D1.2: As a commuter, I want to interrupt the AI mid-sentence without weird pauses
**Acceptance:** barge-in latency < 250ms from speech-detect to TTS cancellation; context preserved so follow-up turn references prior topic.

### US-D1.3: As a premium user, I want the agent to cite classical sources when I ask a pointed question
**Acceptance:** when the user asks "what text says that?" the agent speaks the citation aloud AND the UI surfaces a citation card with source and verse reference (both drawn from F11 citations).

### US-D1.4: As a privacy-conscious user, I want my voice not stored unless I opt in
**Acceptance:** transcript stored always (for safety); audio blob only if `audio_opt_in = true`; toggle visible pre-session; audit log records opt-in status.

### US-D1.5: As a user, I want to know how much my voice session has cost so far
**Acceptance:** mid-session UI shows live meter; session auto-ends when balance hits zero with a 30s grace warning; final receipt emailed post-session.

### US-D1.6: As an engineering oncall, I want voice errors to fail gracefully to text fallback
**Acceptance:** if voice provider returns 5xx, session auto-degrades to a normal text AI chat with a banner; user is not charged for degraded minutes.

## 7. Tasks

### T-D1.1: Voice provider abstraction + evaluation harness
- **Definition:** Build `VoiceProvider` ABC, implement 2 adapters, build eval harness that runs 100 scripted multi-language exchanges against each and scores latency + pronunciation + coherence.
- **Acceptance:** harness runs in CI nightly; produces scorecard; chosen provider beats baseline on all 3 axes.
- **Effort:** 3 weeks

### T-D1.2: Pronunciation dictionary (6 languages × 500 terms)
- **Definition:** Author YAML dicts with classical-advisor review; wire TTS integration; golden-audio test suite.
- **Acceptance:** each term has IPA + at least 1 reference recording from a native speaker; regression test flags any change.
- **Effort:** 4 weeks (advisor time heavy)

### T-D1.3: Session manager + WebRTC signaling
- **Definition:** Implement session lifecycle, pre-hold billing, WebRTC offer/answer flow, heartbeat & teardown.
- **Acceptance:** load test: 1000 concurrent sessions sustained 5 min each; p95 setup < 1s.
- **Effort:** 2 weeks

### T-D1.4: Tool bridge to F10 typed tool-use
- **Definition:** Voice-mode LLM invokes same Pydantic tools as text tier; results summarized for voice (shorter than text surface).
- **Acceptance:** 100% parity on the tool-use catalog (get_yoga_summary, get_current_dasa, get_transit_events, get_tajaka_summary, find_similar_charts).
- **Effort:** 1 week

### T-D1.5: Transcript + citation ambient UI
- **Definition:** Frontend card surface that shows live transcript, citation chips, and mid-session meter.
- **Acceptance:** E2E test: user says "what does BPHS say?" → agent cites → card appears within 300ms of the word "BPHS" being spoken by the agent.
- **Effort:** 2 weeks

### T-D1.6: Billing + refund on degraded minutes
- **Definition:** Per-minute meter; on degradation event, automatic partial refund credited to user balance.
- **Acceptance:** unit + integration tests for all ended_reason branches; zero-balance sessions refunded correctly; audit log matches user statements.
- **Effort:** 1.5 weeks

### T-D1.7: Safety + moderation
- **Definition:** Real-time moderation on user transcript (self-harm, minors, medical/legal/financial advice seeking); moderation on agent output prior to TTS.
- **Acceptance:** red-team suite of 100 prompts across 6 languages; ≥ 98% correct refusal or redirection.
- **Effort:** 2 weeks

### T-D1.8: Beta → GA rollout
- **Definition:** 1% closed beta → 10% → 50% → 100%; quality & cost gates at each step.
- **Acceptance:** rollback playbook tested; gate criteria defined (see §10).
- **Effort:** 1-2 weeks + observation periods

## 8. Unit Tests

Representative categories (specific tests determined at phase start when voice provider and frameworks are locked):

### 8.1 Voice recognition accuracy
- Category: STT accuracy across 100 multi-language test clips (diverse accents, classical-term-heavy).
- Target: ≥ 95% word accuracy overall; ≥ 98% accuracy on classical-term glossary.
- Representative: `test_stt_accuracy_tamil_nakshatra_terms`, `test_stt_accuracy_hindi_dasa_system_names`, `test_stt_accuracy_english_with_mumbled_termination`.

### 8.2 Pronunciation correctness
- Category: TTS synthesizes classical terms; compared against reference audio + phonetic scoring.
- Target: ≥ 95% correct pronunciation across 6 languages × 500 terms.
- Representative: `test_tts_pronunciation_rahu_hindi`, `test_tts_pronunciation_nakshatra_names_tamil`, `test_tts_pronunciation_ashtakavarga_sanskrit_compound`.

### 8.3 Latency budgets
- Category: synthetic and recorded turns against latency budget.
- Target: P50 < 500ms end-to-end, P95 < 800ms, P99 < 1500ms.
- Representative: `test_latency_with_cache_hit`, `test_latency_with_tool_call`, `test_latency_with_cold_start`.

### 8.4 Barge-in
- Category: user interrupts agent mid-TTS.
- Target: < 250ms cancellation; context preserved.
- Representative: `test_bargein_cancels_tts_immediately`, `test_bargein_preserves_partial_context`, `test_bargein_rapid_toggle`.

### 8.5 Session lifecycle & billing
- Category: start, heartbeat, end, refund, balance-hit.
- Target: zero billing discrepancies in 10k synthetic sessions.
- Representative: `test_session_autoend_on_balance_zero`, `test_refund_on_provider_5xx`, `test_pre_hold_released_on_graceful_end`.

### 8.6 Tool-bridge parity
- Category: every F10 tool reachable from voice context.
- Target: 100% parity.
- Representative: `test_voice_invokes_get_yoga_summary`, `test_voice_citation_surfaced_from_get_transit_events`.

### 8.7 Safety / moderation
- Category: red-team prompts for self-harm, minors, legal/medical/financial overreach.
- Target: ≥ 98% correct refusal or redirection; zero false-positive refusals on benign classical queries.
- Representative: `test_refuses_medical_diagnosis_request`, `test_refuses_minor_birth_chart_without_consent`, `test_allows_general_life_guidance_query`.

## 9. EPIC-Level Acceptance Criteria

- [ ] Voice provider selected via documented evaluation; scorecard archived
- [ ] 6 languages live with pronunciation dict and advisor sign-off
- [ ] P95 latency < 800ms sustained over 24h production load
- [ ] Pronunciation correctness ≥ 95% on glossary regression suite
- [ ] Barge-in < 250ms cancellation
- [ ] Billing accuracy verified: 10k session audit shows zero discrepancies
- [ ] Red-team moderation ≥ 98% correct handling
- [ ] Session-to-D6 pipeline: every voice session becomes an ingestible row in the longitudinal dashboard
- [ ] Documentation: `CLAUDE.md` gains voice section; public API docs cover `/voice/session/*`
- [ ] Closed beta NPS ≥ 50 before GA

## 10. Rollout Plan

- **Feature flag:** `voice_ai_astrologer_enabled` (per-org, per-user).
- **Phase 1 — Internal dogfood (2 weeks):** staff + classical advisors; English + Hindi only.
- **Phase 2 — Closed beta (4 weeks):** invite 500 paying users across 6 languages; gate to proceed = NPS ≥ 50, pronunciation regression ≥ 95%, zero billing complaints.
- **Phase 3 — 10% rollout (2 weeks):** premium-tier users, 10% allocation; gate = cost-per-minute within budget (< $0.25), latency P95 < 800ms, moderation incident rate < 1/1000 sessions.
- **Phase 4 — 50% rollout (1 week):** gate = all metrics hold.
- **Phase 5 — 100% GA:** public announcement; D3 language expansion begins.
- **Rollback:** feature flag kill-switch; degrade to text AI chat with banner; no data migration required.

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Voice vendor changes pricing or availability | Medium | High | Abstraction layer; two validated adapters; quarterly re-eval |
| Classical-term pronunciation errors damage trust | Medium | High | Pronunciation dict with advisor review; golden-audio regression in CI |
| Latency spikes at scale | Medium | Medium | Regional edge termination; prompt-cache hits; P95 SLO with burn-rate alerts |
| Moderation bypass in under-resourced languages | Medium | High | Language-specific red-team; conservative fallback to refusal on uncertainty |
| Cost-per-minute exceeds $1 retail at scale | Low | High | Margin review per 10M MAU tier; fallback to split-stack architecture if unit economics break |
| Privacy backlash over voice capture | Low | High | Audio opt-in default-off; transcript retention policy documented; GDPR/DPDP compliant |
| Bias in voice identity (gender, accent) | Medium | Medium | Offer multiple voice personas per language including neutral; track user switching |

## 12. References

- Master spec: `docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`
- Related PRDs: F10 (typed tool-use), F11 (citation shape), F12 (prompt caching), E11a/E11b (text AI chat), D3 (language expansion), D6 (longitudinal dashboard)
- Industry references: OpenAI Realtime API docs; ElevenLabs Pronunciation Dictionary; WebRTC RFC 8825
- Classical-term glossary source files: to be authored in `src/josi/content/voice/pronunciation_dict/`
