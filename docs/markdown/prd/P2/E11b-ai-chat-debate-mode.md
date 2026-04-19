---
prd_id: E11b
epic_id: E11
title: "AI Chat v2 — Debate Mode, Ultra AI Ensemble, Semantic Similarity, Drill-Down, Voice Preview"
phase: P2-breadth
tags: [#ai-chat, #end-user-ux, #astrologer-ux, #experimentation, #performance]
priority: must
depends_on: [E11a, E14a, F8, F10, F11, F12]
enables: [E12, E13, AI5, D1]
classical_sources: [bphs, saravali, phaladeepika, jaimini_sutras, tajaka_neelakanthi, kp_reader]
estimated_effort: 4-5 weeks
status: draft
author: @agent
last_updated: 2026-04-19
---

# E11b — AI Chat v2 (Debate Mode, Ultra AI Ensemble, Semantic Similarity)

## 1. Purpose & Rationale

E11a shipped the foundational chat loop: tool-use, citations, prompt caching, per-turn feedback. It ships a single aggregated answer per technique (strategy D_hybrid from F8) and treats `find_similar_charts` as a stub. That's the right MVP — it proves the contract and generates signals — but it leaves three premium-tier product differentiators unbuilt:

1. **Debate mode** — the only feature in the category that *shows users the disagreement between classical sources* instead of hiding it behind a single aggregated answer. This is the product manifestation of Josi's core thesis: classical source authority is a first-class, visible axis. It's also the single most shareable moment ("look — the Saravali reading disagrees with BPHS on my Gaja Kesari"), driving word-of-mouth growth on a product that is otherwise hard to demo.
2. **Ultra AI ensemble** — power users and astrologers configure per-technique source weights in E12 and want the AI to reason over the *full* ensemble, not a pre-flattened aggregate. Ultra mode surfaces per-source confidences and the aggregated conclusion side-by-side. This is the Mystic/Master tier's core entitlement.
3. **Semantic chart similarity** — Qdrant is already in the stack; what's missing is the indexed embedding of technique-level chart patterns and the production-ready `find_similar_charts` handler. Once shipped, every AI response can ground claims in "users with charts like yours, during the same Mahadasa pattern, reported X." This creates a data-network-effects moat: more users → better similarity retrievals → better answers → more users.

Alongside those, E11b delivers two supporting surfaces that multiply the value of everything above: **explanation drill-down** (every AI claim is clickable to its exact citation + per-source values + which aggregation produced it), and **voice preview** (Mystic+ can hear responses read aloud via ElevenLabs/OpenAI TTS — the on-ramp to D1's voice-native astrologer in P5).

Commercial framing: E11b is the single PRD that turns the Free/Explorer-tier chat of E11a into a clearly-differentiated Mystic+ upgrade. The debate transcript alone is worth the subscription.

## 2. Scope

### 2.1 In scope

**Backend**

- `chat_session.mode` column: `ENUM('standard','debate','ultra')` with default `'standard'`.
- `chat_message.drill_down` JSONB column storing per-claim expansion payloads (verse citation, per-source values, aggregation applied).
- `POST /api/v1/ai/chat` extended to accept `mode` field; orchestrator branches on mode.
- `GET /api/v1/ai/chat/{message_id}/drill-down` — new endpoint returning drill-down payload for a given message's claim index.
- `DebateOrchestrator` — runs four parallel tool-use sub-loops (one per aggregation strategy A/B/C/D), captures per-strategy answers, composes a synthesized final answer that surfaces divergence.
- `UltraOrchestrator` — modifies tool handlers (via `ensemble=true` flag) to return per-source `CitedFact[T]` lists alongside the aggregated `CitedFact[T]`. LLM reasons over the ensemble.
- Qdrant vector index `chart_technique_embedding` populated by a new worker; `find_similar_charts` handler (stubbed in E11a) goes production.
- Multi-turn session state upgrade: `chat_session.session_state` JSONB captures {recent_tools_used, preferred_strategy, astrologer_preference_key, similarity_limits}. Injected into the cache-breakable prompt segment per F12.
- `POST /api/v1/ai/chat/{message_id}/tts` — Mystic+ endpoint returning an audio stream URL (S3 presigned or streamed MP3) for the assistant message.
- New tool `get_strategy_comparison(chart_id, technique_family)` — returns all four strategy outputs for a given family, used internally by debate mode but also available to the LLM in ultra mode.
- Tier gating upgrades in `usage_service.py`: `ai_debate_mode_used`, `ai_ultra_mode_used`, `ai_tts_seconds_used` (monthly quotas; Free 0, Explorer 0, Mystic 500/200/10min, Master unlimited).
- SSE stream extended with new events: `strategy_answer` (one per strategy in debate mode), `ensemble_fact` (one per source in ultra mode), `drill_down_ready`.

**Frontend** (consumer surface; astrologer workbench in E12 reuses components)

- `web/app/(dashboard)/ai/*` extended: mode picker (segmented control), debate timeline view, ultra-mode ensemble pane, drill-down modal.
- `web/components/chat/drill-down-panel.tsx` — collapsible expansion under any claim.
- `web/components/chat/debate-view.tsx` — collapsible "See where the strategies disagree" section.
- `web/components/chat/ensemble-chip.tsx` — per-source confidence chip with expand-on-click.
- `web/components/chat/voice-player.tsx` — lightweight audio player with speed control.
- `web/hooks/use-chat-mode.ts` — persists mode preference per chart in TanStack Query state + localStorage.
- `web/types/chat-v2.ts` — centralized types: `ChatMode`, `DebateStrategyAnswer`, `EnsembleFact`, `DrillDownPayload`, `TtsAudio`.
- Progressive disclosure: drill-down panels are collapsed by default; "Why?" affordance under every claim expands them.
- Mobile: voice-first mobile layout; debate view becomes a horizontally swipeable carousel of strategy cards.

### 2.2 Out of scope

- **Full voice-native astrologer** (two-way voice conversation, barge-in, prosody control) — D1 in P5.
- **Cross-user social features** (sharing debates publicly, commenting on similar charts) — deferred.
- **User-authored rule weights in Ultra mode** (astrologer-only in E12; end-users get Josi defaults).
- **Debate over non-classical techniques** (Chinese BaZi, Mayan, Celtic) — debate mode is limited to families with ≥ 2 classical sources. Others silently fall back to standard mode.
- **Inline TTS streaming in SSE** — audio is delivered via a separate streaming endpoint, not mixed into the text SSE.
- **Caching of TTS audio across users** — generated on-demand per user per message (privacy: a rendering is personal).
- **Whispering / multi-voice synthesis** (personas) — P5.
- **Debate with live astrologer override** (astrologer steps into a debate and adjudicates) — belongs in astrologer consultations, not this PRD.

### 2.3 Dependencies

- **E11a** — chat loop, `chat_session`, `chat_message`, SSE framing all reused.
- **E14a** — experiment framework must be live so debate-mode answers are tagged with active experiment arms and flow to signals.
- **F8** — all four aggregation strategies must emit computed events for every chart before debate mode is meaningful.
- **F10/F11** — tool contract and CitedFact envelope are the substrate; this PRD extends them with `ensemble=true` mode.
- **F12** — cache breakpoints must include `session_state` for multi-turn state.
- **Qdrant** — already deployed per CLAUDE.md; embedding dimensionality decided here.
- **ElevenLabs or OpenAI TTS** — provider choice resolved in §4.
- **E12** — astrologer source-preference model needed for ultra-mode weight selection; if E12 ships after E11b, fall back to Josi default weights.

## 3. Technical Research

### 3.1 Debate mode — parallel strategy execution

The naive approach (run the LLM loop four times, once per strategy) triples cost and latency. The right approach is to run tool calls with `mode=debate` once; each tool handler returns a *strategy-indexed* payload. The LLM sees all four answers in a single tool_result and can reason over the spread directly.

```
┌─────────────────────────────────────────────────────────────────┐
│  DebateOrchestrator.run(chart_id, user_question)                │
│    ↓                                                             │
│  Claude plans: "I'll call get_yoga_summary in debate mode"      │
│    ↓                                                             │
│  ToolExecutor.execute(get_yoga_summary, debate=True)            │
│    → reads all 4 strategy projections from chart_reading_view    │
│    → returns: {                                                  │
│        strategy_A: YogaSummary{yogas:[...], strategy:"A"},      │
│        strategy_B: YogaSummary{yogas:[...], strategy:"B"},      │
│        strategy_C: YogaSummary{yogas:[...], strategy:"C"},      │
│        strategy_D: YogaSummary{yogas:[...], strategy:"D"},      │
│        divergence_summary: {"contested": ["gaja_kesari"], ...}  │
│      }                                                           │
│    ↓                                                             │
│  Claude synthesizes: "Three strategies see Gaja Kesari active.  │
│    Source-weighted (favoring your BPHS preference) sees it as   │
│    strongly active; confidence-weighted sees it as moderate.    │
│    Simple majority disagrees because Saravali dissents."        │
└─────────────────────────────────────────────────────────────────┘
```

`chart_reading_view` (F9) is extended to store all four strategy projections (not just D). The total row bloat is ~4× but row count is unchanged; F3 partitioning handles this cleanly.

### 3.2 Ultra AI ensemble

Ultra mode is orthogonal to debate mode (user can be in one, both, or neither). Ultra adds a per-tool flag `ensemble=true`; the handler populates an additional `ensemble_facts: list[SourceFact]` field alongside the aggregated `CitedFact[T]`. Each `SourceFact` carries `{source_id, source_display_name, value, confidence, citation}`.

Claude is system-prompted in ultra mode to: (a) surface the aggregated answer first, (b) mention notable dissenters, (c) never average across sources without saying so, (d) weight its prose by the astrologer's configured `source_weights` if any (passed in from `get_astrologer_preferences`).

The JSON schema of tool outputs in ultra mode is *additive* — the aggregated field remains, and `ensemble_facts` is added. This means F10's snapshot-stability tests still pass; ultra is a forward-compatible extension.

### 3.3 Semantic chart similarity — Qdrant index

**What we embed.** Not the raw chart. The *technique-level feature vector* per chart per technique_family. For each `(chart_id, technique_family_id)` pair we build a dense vector:

- For `yoga`: one-hot-ish vector over the 250-yoga vocabulary with strength as magnitude, then dimensionally reduced via a learned projection to 512 dims.
- For `dasa`: current MD lord one-hot × remaining-duration fraction, concatenated with recent AD/PD history → 128 dims, projected to 512.
- For `ashtakavarga`: the 12-sign sarva + 7×12 bhinna, flattened and normalized → 96 dims → 512.
- For `jaimini`, `tajaka`, etc.: per-family feature extractors in `src/josi/services/ai/similarity/features/`.

Final index is 512-dim cosine-space over `chart_id × technique_family_id` pairs. Qdrant collection: `chart_technique_v1`, payload `{chart_id, technique_family_id, organization_id, feature_version}`.

**How it's used.** `find_similar_charts(chart_id, technique_family, limit)` does a vector query against `chart_technique_v1` filtered to the caller's `organization_id` and the requested family, returning the top-k neighbours with similarity scores and the *publicly shareable* outcome summary (if the matched chart owner has opted into outcome sharing) or an anonymized aggregate across neighbours.

**Privacy.** `aggregation_signal` data is aggregated across matched charts; individual user outcomes are never returned. The `SimilarChart.matched_features` list references the family-level pattern match, not the user.

**Why Qdrant.** Already in stack (per CLAUDE.md). Supports payload filtering, which lets us tenant-scope cheaply. Alternatives (pgvector, Pinecone, FAISS+Redis) were evaluated in the original stack decision; not re-litigated here.

### 3.4 Multi-turn conversational state

E11a binds one session to one chart but keeps only message history. E11b adds `chat_session.session_state`:

```jsonc
{
  "recent_tools_used": ["get_yoga_summary", "get_current_dasa"],
  "preferred_strategy": "D_hybrid",          // sticky within the session
  "astrologer_preference_key": "...",        // if astrologer user
  "similarity_scope": {"limit": 10, "min_score": 0.75},
  "drilled_down_claims": ["msg-42#claim-2"]  // so we don't re-push citations already expanded
}
```

This state is injected as a cached block (F12) between chart-context and history. It's updated after every turn in a single transaction with the `chat_message` insert. TTL is the session's — not shared across sessions.

### 3.5 Drill-down payloads

Every assistant message has a `claims` array embedded in `drill_down`. Each claim has:

```jsonc
{
  "claim_index": 0,
  "text_span": [120, 187],                   // char offsets in message content
  "technique_family_id": "yoga",
  "rule_id": "raja.gaja_kesari",
  "aggregated": {                            // the CitedFact user saw
    "value": true,
    "source_id": "bphs",
    "citation": "BPHS 36.14-16",
    "confidence": 0.9,
    "cross_source_agreement": "4/5 sources agree"
  },
  "per_source": [                            // the full ensemble (even if ultra not engaged)
    {"source_id": "bphs", "value": true, "confidence": 0.95, "citation": "BPHS 36.14-16"},
    {"source_id": "saravali", "value": false, "confidence": 0.6, "citation": "Saravali 34.12"},
    ...
  ],
  "aggregation_applied": {
    "strategy_id": "D_hybrid",
    "strategy_display_name": "Hybrid (default)"
  },
  "verse_citation": {                        // the classical verse itself
    "source_id": "bphs",
    "iast": "...",
    "devanagari": "...",
    "translation_en": "...",
    "translation_ta": "..."
  }
}
```

Payloads are computed at chat-turn completion time (not lazily) because they depend on tool results already in memory. Stored in `chat_message.drill_down` JSONB. The endpoint `GET /api/v1/ai/chat/{message_id}/drill-down` returns the appropriate slice for a given claim index. A follow-up on a new session can fetch a historical drill-down without re-running the tool.

### 3.6 Voice preview (TTS)

**Provider choice.** ElevenLabs (higher prosody, better Sanskrit pronunciation via custom voice training) vs OpenAI TTS (cheaper, fewer languages). Start with OpenAI `tts-1-hd` at launch (supports the 10 Indic languages plus English reliably for conversational output); introduce ElevenLabs as a premium voice unlock after the audio-product fit signals confirm.

**Flow.** Client calls `POST /api/v1/ai/chat/{message_id}/tts`. Backend loads the message content, strips markdown/citations to a TTS-safe script, calls the provider, streams MP3 chunks back via chunked transfer encoding. Client plays via `<audio>` tag with native controls. No intermediate S3 write for v1 (latency); we add caching when we measure repeat-listen rates.

**Language detection.** Use `message.detected_language` (auto-detected at turn completion; defaults to user's `ui_language` preference). TTS voice selected per language. Sanskrit terms are spelled phonetically inline.

**Usage metering.** Measured in audio seconds consumed, not characters generated. Meter on completion (full stream played) is too lossy; instead meter on generation and tolerate a small over-count.

### 3.7 Alternatives considered

| Alternative | Rejected because |
|---|---|
| Debate as separate endpoint (`/ai/debate`) | Forces UI duplication; mode is a property of a single chat session |
| Debate by re-running LLM 4× with different tool outputs | 4× cost, 4× latency, no synthesis |
| Ultra mode as separate model | Doubles infra; same data, different presentation is the right seam |
| Per-user Qdrant collection | Explodes collection count at scale; payload filter is sufficient |
| Embed the whole chart as one vector | Loses per-family retrieval; "similar on yogas" and "similar on dasa" are different queries |
| Compute drill-down lazily on first request | Tool results would need to be re-fetched; simpler to snapshot at turn time |
| TTS streaming multiplexed into SSE | SSE is text/event-stream; mixing binary is awkward. Separate endpoint is cleaner. |
| Use the same chat_session row for standard/debate/ultra interchangeably per-turn | Confuses cache keys and session_state semantics. Mode is per-session, switch creates new session. |

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| Mode switching mid-session | Not allowed; switch creates a new session | Cache keys, session_state, and signal attribution stay clean |
| Debate strategy count | All 4 (A/B/C/D) always | Debate is the single feature where *seeing* the strategies is the point |
| Debate cost vs standard | 1.6× (single LLM loop + 4× read from reading_view) | Reading view has all 4 projections; LLM cost barely budges |
| Ultra mode default | Off by default even on Mystic+ | User must opt in; signals "I want depth, not speed" |
| Similarity index dimensionality | 512 cosine | Balanced recall/storage; upgradable via feature_version column |
| Similarity tenant isolation | Payload filter on `organization_id` | Cheaper than per-tenant collection |
| TTS provider v1 | OpenAI `tts-1-hd` | Language breadth; revisit ElevenLabs when audio-product fit confirms |
| TTS caching | None in v1 | Audio is personal; cache heuristics unclear until we measure |
| Drill-down storage | Embedded JSONB on chat_message | Fast read, avoids JOIN; size bounded by tool results already loaded |
| Drill-down for historical (pre-E11b) messages | Backfill-on-request endpoint | Avoids heavy migration; old sessions just lack drill-down until accessed |
| Claim span detection | LLM emits `<claim id=N>...</claim>` markers in output (stripped before render) | Deterministic; cheaper than post-hoc NER |
| Voice language for mixed-language output | Primary language of message content; inline Sanskrit gets phonetic rendering | Acceptable first pass; per-language segmentation is P5 |
| Thumbs signal in debate mode | Thumbs attributed to the *synthesis*, with per-strategy sub-thumbs optional | Both are E14a inputs |
| Mobile voice player persistent across nav | Yes — mini player in bottom nav | Standard podcast UX pattern |
| Localization of mode labels | "Standard / Debate / Ultra AI" translated via existing i18n system (D3 scaffold) | Consistent with other UI strings |

## 5. Component Design

### 5.1 New and modified modules (backend)

```
src/josi/models/ai/
├── chat_session.py              # +mode, +session_state columns
└── chat_message.py              # +drill_down column

src/josi/schemas/ai/
├── chat_v2_schemas.py           # new: ChatModeEnum, DebateResponse, EnsembleFact
└── drill_down.py                # DrillDownPayload, ClaimSpan, VerseCitation

src/josi/services/ai/chat/
├── chat_orchestrator.py         # dispatches to ModeHandler
├── mode_handlers/
│   ├── __init__.py
│   ├── standard_handler.py      # unchanged from E11a
│   ├── debate_handler.py        # NEW: parallel strategy pathway
│   └── ultra_handler.py         # NEW: ensemble flag propagation
├── drill_down_builder.py        # builds per-claim drill-down from tool results
└── strategy_comparison_tool.py  # NEW F10 tool: get_strategy_comparison

src/josi/services/ai/similarity/
├── __init__.py
├── feature_extractors/
│   ├── yoga_features.py
│   ├── dasa_features.py
│   ├── ashtakavarga_features.py
│   ├── jaimini_features.py
│   └── tajaka_features.py
├── qdrant_client.py             # wraps Qdrant Python SDK
├── indexer.py                   # worker: extract + embed + upsert per chart_id
└── similarity_service.py        # find_similar_charts production handler

src/josi/services/ai/tts/
├── __init__.py
├── base.py                      # TtsProvider Protocol
├── openai_tts_provider.py
├── elevenlabs_tts_provider.py   # scaffold; not default
└── tts_service.py               # language detection, script sanitization, usage metering

src/josi/api/v1/controllers/
├── ai_chat_controller.py        # extended: mode field, drill_down, tts endpoints
└── ai_similarity_controller.py  # admin: reindex trigger, stats

src/josi/workers/
└── similarity_indexer_worker.py # subscribes to chart_reading_view updates
```

### 5.2 Data model additions

```sql
-- E11b: extend chat_session and chat_message
ALTER TABLE chat_session
    ADD COLUMN mode TEXT NOT NULL DEFAULT 'standard'
        CHECK (mode IN ('standard', 'debate', 'ultra')),
    ADD COLUMN session_state JSONB NOT NULL DEFAULT '{}'::jsonb;

CREATE INDEX idx_chat_session_mode
    ON chat_session(mode, last_active_at DESC)
    WHERE is_deleted = false;

ALTER TABLE chat_message
    ADD COLUMN drill_down JSONB NOT NULL DEFAULT '[]'::jsonb;

-- E11b: TTS usage metering (supplements user_usage)
ALTER TABLE user_usage
    ADD COLUMN ai_tts_seconds_used INTEGER NOT NULL DEFAULT 0,
    ADD COLUMN ai_debate_mode_used INTEGER NOT NULL DEFAULT 0,
    ADD COLUMN ai_ultra_mode_used  INTEGER NOT NULL DEFAULT 0;

-- E11b: chart_reading_view stores all 4 strategy projections
ALTER TABLE chart_reading_view
    ADD COLUMN yogas_by_strategy JSONB NOT NULL DEFAULT '{}'::jsonb,
    ADD COLUMN dasas_by_strategy JSONB NOT NULL DEFAULT '{}'::jsonb,
    ADD COLUMN ashtakavarga_by_strategy JSONB NOT NULL DEFAULT '{}'::jsonb,
    ADD COLUMN jaimini_by_strategy JSONB NOT NULL DEFAULT '{}'::jsonb,
    ADD COLUMN tajaka_by_strategy JSONB NOT NULL DEFAULT '{}'::jsonb;
```

Qdrant collection (declared, not SQL):

```
collection: chart_technique_v1
vector_size: 512
distance: Cosine
payload_schema:
  chart_id: keyword (indexed)
  technique_family_id: keyword (indexed)
  organization_id: keyword (indexed)
  feature_version: keyword
```

### 5.3 API contract additions

**Extended chat message endpoint:**

```
POST /api/v1/ai/chat
Body: {
  session_id?: UUID,
  chart_id: UUID,
  user_message: string,
  mode?: "standard" | "debate" | "ultra",   // default: session.mode or "standard"
  enable_similarity?: boolean                // default: true for Mystic+
}

SSE stream adds:
  event: strategy_answer       (debate mode only, one per strategy)
  data: {"strategy_id": "A_majority", "summary_text": "...", "divergent_facts": [...]}

  event: ensemble_fact         (ultra mode only, one per fact)
  data: {"fact_ref": "...", "per_source": [...], "aggregated": {...}}

  event: drill_down_ready
  data: {"claim_count": 7}     // tells client it can fetch drill-downs now

  (other events unchanged from E11a)
```

**Drill-down endpoint:**

```
GET /api/v1/ai/chat/{message_id}/drill-down?claim_index=0
Response: {
  success: true,
  data: DrillDownPayload       // see §3.5
}

GET /api/v1/ai/chat/{message_id}/drill-down        // all claims
Response: {
  success: true,
  data: { claims: DrillDownPayload[] }
}
```

**TTS endpoint:**

```
POST /api/v1/ai/chat/{message_id}/tts
Body: { voice?: string, speed?: number }   // voice catalog per-provider
Response: audio/mpeg stream
Headers:
  Content-Type: audio/mpeg
  X-Audio-Duration-Seconds: 42
  X-TTS-Provider: openai
  X-Remaining-TTS-Seconds: 418
```

**Similarity endpoint (exposed via F10 tool, not a public REST surface):**

```python
@ai_tool(
  name="find_similar_charts",
  description="Find charts with similar patterns in a given technique family.",
  input_model=FindSimilarChartsInput,
  output_model=FindSimilarChartsResponse,
)
async def find_similar_charts_handler(args, ...) -> BaseModel: ...
```

### 5.4 Internal interfaces (Python)

```python
# src/josi/services/ai/chat/mode_handlers/debate_handler.py

class DebateHandler(ModeHandler):
    async def run(self, ctx: ChatContext) -> AsyncIterator[StreamEvent]:
        """
        1. Build system prompt fragment that instructs Claude to:
             - call tools with debate=True
             - surface divergence explicitly
             - structure output as {synthesis, per_strategy_notes}
        2. Drive the tool-use loop (shares chat_orchestrator's loop).
        3. Emit strategy_answer events as they arrive.
        4. On end_turn, attribute signal writes to both synthesis message
           and per-strategy sub-events.
        """
```

```python
# src/josi/services/ai/similarity/similarity_service.py

class SimilarityService:
    def __init__(self, qdrant: QdrantClient, repo: ChartReadingViewRepository): ...

    async def find_similar(
        self,
        chart_id: UUID,
        technique_family: str,
        *,
        organization_id: UUID,
        limit: int = 10,
        min_score: float = 0.7,
    ) -> list[SimilarChart]:
        """Vector query filtered to tenant; returns payload-decorated neighbours."""

    async def index_chart(self, chart_id: UUID, technique_family: str) -> None:
        """Extract features → embed → upsert. Idempotent per (chart, family, feature_version)."""
```

```python
# src/josi/services/ai/tts/tts_service.py

class TtsService:
    async def stream_message_audio(
        self,
        message_id: UUID,
        *,
        user_id: UUID,
        voice: str | None = None,
        speed: float = 1.0,
    ) -> AsyncIterator[bytes]:
        """
        1. Load message, detect language, sanitize to TTS script.
        2. Check tier + usage quota; raise if exceeded.
        3. Stream chunks from provider; increment usage on generation.
        """
```

### 5.5 Frontend file structure (adheres to CLAUDE.md: ≤ 300 lines per file, one component per file, typed, CSS vars)

```
web/app/(dashboard)/ai/
├── page.tsx                              # main chat page (≤ 300 lines)
├── _components/
│   ├── mode-picker.tsx                   # segmented control: Standard / Debate / Ultra
│   ├── chat-composer.tsx                 # text input + send
│   ├── message-list.tsx                  # virtualized list of messages
│   └── (existing E11a components remain)

web/components/chat/
├── debate-view.tsx                       # collapsible strategies-divergence section
├── debate-strategy-card.tsx              # one card per A/B/C/D
├── ensemble-chip.tsx                     # per-source confidence chip
├── ensemble-pane.tsx                     # full ensemble breakdown panel
├── drill-down-panel.tsx                  # modal/drawer with citation + per-source + aggregation
├── drill-down-claim-marker.tsx           # inline "Why?" button attached to claim spans
├── voice-player.tsx                      # audio player with speed/lang controls
├── voice-player-mini.tsx                 # persistent bottom-nav mini player
├── similarity-callout.tsx                # "Users with charts like yours..." card
├── citation-pill.tsx                     # reused from E11a (small visual upgrade)
└── chat-mode-intro.tsx                   # one-time explainer modals per mode

web/hooks/
├── use-chat-mode.ts                      # mode state, persistence, tier-gate check
├── use-chat-message.ts                   # extends E11a hook with drill_down fetcher
├── use-drill-down.ts                     # TanStack Query hook for GET .../drill-down
├── use-voice-player.ts                   # plays audio, reports seconds consumed
└── use-similarity.ts                     # wraps find_similar_charts tool responses

web/types/
├── chat-v2.ts                            # ChatMode, DebateStrategyAnswer, EnsembleFact, DrillDownPayload
└── similarity.ts                         # SimilarChart type used by similarity components

web/lib/
└── chat-mode-tier-gate.ts                # client-side tier check; mirrors backend
```

**Type safety.** No `any`. Example:

```ts
// web/types/chat-v2.ts
export type ChatMode = "standard" | "debate" | "ultra";

export interface DebateStrategyAnswer {
  strategyId: "A_majority" | "B_confidence" | "C_weighted" | "D_hybrid";
  strategyDisplayName: string;
  summaryText: string;
  divergentFacts: DivergentFact[];
}

export interface EnsembleFact {
  factRef: string;
  aggregated: CitedFact<string | number | boolean>;
  perSource: SourceFact[];
}

export interface DrillDownPayload {
  claimIndex: number;
  textSpan: [number, number];
  techniqueFamilyId: string;
  ruleId: string;
  aggregated: CitedFact<unknown>;
  perSource: SourceFact[];
  aggregationApplied: { strategyId: string; strategyDisplayName: string };
  verseCitation: VerseCitation;
}
```

TanStack Query pattern:

```tsx
const { data: drillDown } = useQuery<DrillDownPayload>({
  queryKey: ['chat', 'drill-down', messageId, claimIndex],
  enabled: expanded,
  queryFn: async () => {
    const res = await apiClient.get<{ data: DrillDownPayload }>(
      `/api/v1/ai/chat/${messageId}/drill-down`,
      { params: { claim_index: claimIndex } },
    );
    return res.data.data;
  },
});
```

**Styling.** All colors use CSS variables from `globals.css` (`var(--blue)`, `var(--gold)`, `var(--citation-bg)` — new vars added in the PR). Tailwind for layout; inline styles only for calculated claim-span overlays.

### 5.6 Tier gating surface

| Feature | Free | Explorer | Mystic | Master |
|---|---|---|---|---|
| Standard chat | 5/day | 100/day | unlimited | unlimited |
| Debate mode | — | — | 500 turns/mo | unlimited |
| Ultra AI | — | — | 200 turns/mo | unlimited |
| Similarity retrieval in answers | — | — | enabled | enabled |
| Voice preview (TTS) | — | — | 10 min/mo | 60 min/mo |
| Drill-down | enabled for all | enabled | enabled | enabled |

Drill-down is intentionally free for all tiers — it's the transparency play. The premium value is debate/ultra/similarity/voice.

## 6. User Stories

### US-E11b.1: As a Mystic-tier user, I can switch to Debate mode and see the 4 strategies disagree on Gaja Kesari
**Acceptance:** mode picker offers "Debate" for Mystic+. After switching, asking "is Gaja Kesari active?" produces a synthesized answer *plus* a collapsible "See where the strategies disagree" panel showing A/B/C/D conclusions and the divergent fact list.

### US-E11b.2: As a user, I can click any claim in the AI response and expand it
**Acceptance:** every claim shows a subtle "Why?" button. Clicking it opens a panel showing: the classical verse (IAST + Devanagari + English), per-source computed values, which aggregation strategy was applied.

### US-E11b.3: As a Mystic-tier user, I can enable Ultra AI and see per-source confidences inline
**Acceptance:** toggling Ultra switches the response to show aggregated fact + expandable ensemble chips per technique. Claude's prose explicitly references "BPHS strongly supports this; Saravali is ambivalent."

### US-E11b.4: As a user, I can ask "are there people with charts like mine?" and get a relevant answer grounded in similarity retrieval
**Acceptance:** for Mystic+ users, Claude calls `find_similar_charts`; response includes a "Similarity callout" card: "Users with a similar Jupiter-in-5th Mahadasa pattern commonly reported…"

### US-E11b.5: As a user, I can tap a play button on any assistant message and hear it read aloud
**Acceptance:** Mystic+ users see a speaker icon on assistant messages. Tapping starts TTS playback via mini-player; speed and voice controls work; mobile mini-player persists across navigation.

### US-E11b.6: As a user continuing a session after a break, my preferred strategy and recent tools stay set
**Acceptance:** session_state persists across turns; returning to a debate-mode session an hour later resumes in debate mode with the same `preferred_strategy`.

### US-E11b.7: As an astrologer, my per-family source weights shape Ultra mode's reasoning
**Acceptance:** astrologers configured with BPHS weight 1.0, Saravali 0.2 for yogas see Ultra prose that cites BPHS first and flags Saravali dissent as "minor."

### US-E11b.8: As a free-tier user, Debate/Ultra/TTS are gracefully gated
**Acceptance:** attempting to select Debate mode shows an upgrade modal with a preview image, not a crash.

### US-E11b.9: As a developer, adding a new technique family to the similarity index doesn't require changing Qdrant schema
**Acceptance:** new `FeatureExtractor` plugged into `similarity/feature_extractors/` is enough; `feature_version` bump re-indexes.

### US-E11b.10: As a user, drill-down works for messages I sent last week
**Acceptance:** historical messages have drill-down available (drill_down JSONB populated at turn time); the endpoint returns them without re-running tools.

## 7. Tasks

### T-E11b.1: Data model migration (chat_session.mode/session_state, chat_message.drill_down, user_usage TTS)
- **Definition:** Autogenerate Alembic migration via `docker-compose exec web alembic revision --autogenerate -m "E11b: chat v2 columns"`. Review for correctness.
- **Acceptance:** Migration applies cleanly; existing rows default to mode='standard'.
- **Effort:** 2 hours
- **Depends on:** E11a merged

### T-E11b.2: Extend chart_reading_view with per-strategy projections
- **Definition:** Add `{family}_by_strategy` JSONB columns; update aggregation worker (F8) to populate all 4 strategies per chart per family.
- **Acceptance:** `SELECT yogas_by_strategy FROM chart_reading_view WHERE chart_id = :id` returns dict with keys A_majority, B_confidence, C_weighted, D_hybrid.
- **Effort:** 2 days
- **Depends on:** T-E11b.1, F8 aggregation worker

### T-E11b.3: DebateHandler implementation
- **Definition:** `mode_handlers/debate_handler.py`; tool-use loop branch; system-prompt fragment; `strategy_answer` SSE event.
- **Acceptance:** Unit tests for parallel-strategy path; integration test with mocked Anthropic showing all 4 strategy_answer events.
- **Effort:** 3 days
- **Depends on:** T-E11b.2

### T-E11b.4: UltraHandler implementation + tool ensemble flag
- **Definition:** `ensemble: bool = False` parameter on every F10 tool input model; handler branch; `ensemble_fact` SSE event.
- **Acceptance:** Tool snapshot tests pass (additive change); `get_yoga_summary(ensemble=true)` returns `ensemble_facts` list alongside aggregated.
- **Effort:** 3 days
- **Depends on:** T-E11b.2

### T-E11b.5: DrillDownBuilder
- **Definition:** `drill_down_builder.py`; extracts claim spans from Claude output (LLM emits `<claim id=N>...</claim>` markers, stripped server-side); constructs DrillDownPayload per claim; writes to `chat_message.drill_down`.
- **Acceptance:** Turn completes with populated drill_down; text content has markers stripped; claim_index maps correctly to text spans.
- **Effort:** 2 days
- **Depends on:** T-E11b.1

### T-E11b.6: Drill-down API endpoint
- **Definition:** `GET /api/v1/ai/chat/{message_id}/drill-down`.
- **Acceptance:** returns full claims list or slice by `claim_index`; auth enforced (caller must own session); 404 for missing; 403 for cross-tenant.
- **Effort:** 4 hours
- **Depends on:** T-E11b.5

### T-E11b.7: Qdrant feature extractors (yoga, dasa, ashtakavarga, jaimini, tajaka)
- **Definition:** One extractor per family producing a 512-dim vector from chart_reading_view projections.
- **Acceptance:** unit tests assert vector stability (same chart → same vector within tolerance); coverage of all families.
- **Effort:** 4 days
- **Depends on:** T-E11b.2

### T-E11b.8: Similarity indexer worker
- **Definition:** Subscribes to `chart_reading_view.last_computed_at` updates; extracts features per family; upserts to Qdrant.
- **Acceptance:** integration test with fake Qdrant confirming upserts; idempotent per `feature_version`.
- **Effort:** 2 days
- **Depends on:** T-E11b.7

### T-E11b.9: Promote `find_similar_charts` to production
- **Definition:** Replace E11a stub; call SimilarityService; return populated SimilarChart list.
- **Acceptance:** tool returns real neighbours for seeded data; tenant isolation tested; privacy test (no per-user outcome data leaked).
- **Effort:** 1 day
- **Depends on:** T-E11b.8

### T-E11b.10: TtsService with OpenAI provider
- **Definition:** `tts_service.py`, `openai_tts_provider.py`, script sanitizer, language detection; usage metering on generation.
- **Acceptance:** end-to-end test generates audio for a seeded assistant message; usage incremented correctly.
- **Effort:** 2 days
- **Depends on:** T-E11b.1

### T-E11b.11: TTS endpoint
- **Definition:** `POST /api/v1/ai/chat/{message_id}/tts`.
- **Acceptance:** streams MP3; tier-gates Mystic+; rejects over-quota; emits `X-Remaining-TTS-Seconds`.
- **Effort:** 4 hours
- **Depends on:** T-E11b.10

### T-E11b.12: Session state injection + F12 cache breakpoint
- **Definition:** Wire `session_state` into the cached prompt segment; update F12 cache-key logic to include `session_state` hash.
- **Acceptance:** cache-hit test confirms no regression; state changes invalidate correctly.
- **Effort:** 1 day
- **Depends on:** T-E11b.1

### T-E11b.13: Frontend — ModePicker + mode-aware chat surface
- **Definition:** `mode-picker.tsx`, `chat-mode-intro.tsx`, tier gating modal; `useChatMode` hook.
- **Acceptance:** Storybook stories for each mode state; Playwright e2e for mode switch.
- **Effort:** 3 days
- **Depends on:** T-E11b.3, T-E11b.4

### T-E11b.14: Frontend — DebateView components
- **Definition:** `debate-view.tsx` + `debate-strategy-card.tsx`; reads `strategy_answer` SSE events; collapsible.
- **Acceptance:** React Testing Library unit tests; Playwright e2e with mocked SSE stream.
- **Effort:** 2 days
- **Depends on:** T-E11b.13

### T-E11b.15: Frontend — EnsembleChip + EnsemblePane
- **Definition:** Per-source confidence chips; expandable pane.
- **Acceptance:** RTL tests; keyboard accessibility (tab to chip, enter to expand).
- **Effort:** 2 days
- **Depends on:** T-E11b.13

### T-E11b.16: Frontend — DrillDownPanel + claim markers
- **Definition:** Inline "Why?" button attached to claim spans; modal/drawer with citation + per-source + aggregation breakdown.
- **Acceptance:** RTL tests; accessibility (focus trap, ESC closes); mobile drawer on <768px.
- **Effort:** 3 days
- **Depends on:** T-E11b.6

### T-E11b.17: Frontend — VoicePlayer + mini-player
- **Definition:** `voice-player.tsx`, `voice-player-mini.tsx`; consumes `/tts` endpoint as audio stream.
- **Acceptance:** plays/pauses; speed control (0.75x-1.5x); mini persists across `(dashboard)` nav.
- **Effort:** 2 days
- **Depends on:** T-E11b.11

### T-E11b.18: Frontend — SimilarityCallout
- **Definition:** Card component rendered when response contains similarity references.
- **Acceptance:** RTL test with sample SimilarChart payload; privacy check (no chart_id leaked to DOM).
- **Effort:** 1 day
- **Depends on:** T-E11b.9

### T-E11b.19: Types + API client updates
- **Definition:** `web/types/chat-v2.ts`, `web/types/similarity.ts`; typed apiClient methods.
- **Acceptance:** no `any` in chat-v2 path; `tsc --noEmit` passes.
- **Effort:** 1 day
- **Depends on:** T-E11b.13

### T-E11b.20: Usage meter UI surfaces in settings
- **Definition:** Show monthly debate/ultra/TTS consumption in `/settings/usage` with progress bars.
- **Acceptance:** pulls from `GET /api/v1/me/usage`; CSS variable-driven progress.
- **Effort:** 1 day
- **Depends on:** T-E11b.1

### T-E11b.21: Documentation + rollout
- **Definition:** Update `CLAUDE.md` AI chat section; add `docs/markdown/ai-chat-v2.md`; feature-flag gating docs.
- **Acceptance:** docs merged; internal team runbook for diagnosing debate-mode failures.
- **Effort:** 4 hours
- **Depends on:** all

## 8. Unit Tests

### 8.1 Backend: DebateHandler

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_debate_handler_emits_four_strategy_answers` | reading_view with 4 strategy projections for yogas | 4 `strategy_answer` events, one per strategy id | core debate flow |
| `test_debate_handler_divergence_detection` | yogas where A/B say active, C/D say not | synthesis content mentions divergence; `divergent_facts` populated | correctness of divergence surface |
| `test_debate_handler_falls_back_when_single_source` | family with only 1 source computed | falls back to standard mode silently; user notified | graceful degradation |
| `test_debate_handler_tier_gate` | Free user, mode=debate | 403 with upgrade-required error | entitlement enforcement |
| `test_debate_handler_usage_increments_once_per_turn` | 1 successful turn in debate mode | `user_usage.ai_debate_mode_used += 1` | usage accounting |
| `test_debate_handler_cost_delta_vs_standard` | same question in both modes | debate uses ≤ 1.8× tokens (reading view is cheap; LLM barely differs) | performance budget |

### 8.2 Backend: UltraHandler

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_ultra_handler_ensemble_flag_propagates` | mode=ultra; tool call to get_yoga_summary | tool handler receives `ensemble=True` | plumbing |
| `test_ultra_response_has_per_source_facts` | seeded 3-source yoga | response's `ensemble_facts` list has 3 entries | shape correctness |
| `test_ultra_snapshot_stability` | run ultra response, compare to snapshot | passes | additive-schema guarantee |
| `test_ultra_astrologer_weights_applied` | astrologer with BPHS=1.0, Saravali=0.2 | ensemble_facts ordered by weight; aggregated source_id='bphs' | weight-aware aggregation |
| `test_ultra_falls_back_to_default_weights_when_no_preference` | non-astrologer user | Josi default weights used | safe default |

### 8.3 Backend: SimilarityService

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_feature_extractor_yoga_stability` | same chart twice | same vector within 1e-6 | determinism |
| `test_feature_extractor_dasa_dimensionality` | any chart | vector is length 512 | shape |
| `test_similarity_tenant_isolation` | query from org A for chart indexed from org B | 0 results | multi-tenant safety |
| `test_similarity_respects_min_score` | limit=10, min_score=0.9 | only neighbours ≥ 0.9 returned | filtering |
| `test_similarity_indexer_idempotent` | index same chart twice | Qdrant upsert called but no duplicate payloads | idempotency |
| `test_find_similar_charts_handler_privacy` | neighbour's user has `share_outcomes=false` | returned neighbour has no `user_outcomes` field | privacy |

### 8.4 Backend: DrillDownBuilder

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_drill_down_claim_extraction_from_markers` | LLM text with `<claim id=0>...</claim>` | drill_down has 1 claim with correct text_span | marker parsing |
| `test_drill_down_markers_stripped_from_visible_content` | same input | saved `content` has no marker tags | UX clean |
| `test_drill_down_payload_includes_all_sources` | yoga with 4-source ensemble | per_source has 4 entries | completeness |
| `test_drill_down_aggregation_applied_matches_session_strategy` | ultra mode user | `aggregation_applied.strategy_id = 'D_hybrid'` or the chosen strategy | correctness |

### 8.5 Backend: TtsService

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_tts_script_sanitizer_strips_markdown` | `**bold** text [cite](...)` | "bold text" | script quality |
| `test_tts_script_sanitizer_preserves_sanskrit_phonetics` | "Gaja Kesari (गज केसरी)" | phonetic rendering in audio script | Indic pronunciation |
| `test_tts_usage_increments_seconds` | generate 42-second audio | `user_usage.ai_tts_seconds_used += 42` | metering |
| `test_tts_over_quota_returns_402` | user at monthly cap | 402 Payment Required with upgrade URL | entitlement |
| `test_tts_provider_failure_fallback` | OpenAI returns 500 | handler logs + returns 502 with retryable flag | resilience |

### 8.6 Backend: Chat v2 API contract

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_chat_endpoint_accepts_mode_field` | POST /ai/chat mode=debate | session created with mode='debate' | API surface |
| `test_chat_mode_switch_creates_new_session` | existing session mode=standard, request mode=debate | 400 or new session created (design choice) | state integrity |
| `test_drill_down_endpoint_auth_cross_tenant` | caller org A requests message from org B | 403 | tenant isolation |
| `test_drill_down_endpoint_historical_message` | pre-E11b message without drill_down | returns `[]` with 200 (not 404) | backward compat |

### 8.7 Frontend: ModePicker (React Testing Library)

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_mode_picker_renders_three_options` | render with Mystic tier | 3 segmented options | UI shape |
| `test_mode_picker_free_tier_locks_debate_ultra` | Free user | Debate/Ultra options disabled with lock icon | tier gate |
| `test_mode_picker_persists_selection` | click Debate, reload | selection persists via localStorage | stickiness |
| `test_mode_picker_upgrade_modal_on_locked_click` | Free user clicks Debate | upgrade modal appears | conversion flow |

### 8.8 Frontend: DebateView

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_debate_view_collapsed_by_default` | render with 4 strategy answers | 4 cards hidden until "See disagreement" clicked | progressive disclosure |
| `test_debate_view_shows_divergent_facts_highlighted` | strategies with 1 divergent fact | divergent fact has `--accent-divergent` color | visual cue |
| `test_debate_strategy_card_keyboard_accessible` | tab through cards | focus ring visible; enter expands | a11y |

### 8.9 Frontend: DrillDownPanel

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_drill_down_panel_renders_verse_citation` | payload with IAST + Devanagari | both rendered in <code>-tagged blocks | classical fidelity |
| `test_drill_down_panel_per_source_list` | payload with 5 sources | 5 rows, each with source name + value + confidence bar | density |
| `test_drill_down_panel_esc_closes` | panel open, press ESC | panel closes, focus returns to "Why?" button | a11y |
| `test_drill_down_panel_mobile_becomes_drawer` | viewport < 768px | renders as bottom drawer, not centered modal | responsive |

### 8.10 Frontend: VoicePlayer

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_voice_player_fetches_audio_stream` | tap play on message | fetch called with correct URL | integration |
| `test_voice_player_speed_control` | set speed 1.5x | `audio.playbackRate === 1.5` | feature |
| `test_voice_player_mini_persists_across_nav` | start playback, navigate to /dashboard | mini-player still mounted, audio continues | UX continuity |
| `test_voice_player_quota_exhausted_hides_button` | user over monthly TTS cap | play button hidden with upgrade prompt | entitlement |

### 8.11 Frontend: Types (TypeScript compile-time)

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_no_any_in_chat_v2_path` | `tsc --noEmit` with strict lint | 0 occurrences of `any` in `web/app/(dashboard)/ai/**` or `web/components/chat/**` | CLAUDE.md rule |
| `test_apiclient_drilldown_returns_typed_payload` | `apiClient.get<DrillDownPayload>('...')` | compile succeeds | type discipline |

### 8.12 Playwright end-to-end

| Test name | Flow | Assertion | Rationale |
|---|---|---|---|
| `e2e_debate_mode_shows_divergence` | login Mystic → new session → pick Debate → ask "is Gaja Kesari active?" | "See disagreement" panel visible; 4 cards render | headline flow |
| `e2e_drill_down_cycle` | login → ask yoga question → click "Why?" on first claim | drawer opens with verse + per-source | drill-down works |
| `e2e_ultra_mode_ensemble_chips` | login Mystic → new session → Ultra → ask dasa question | ensemble chips render per source on fact | ultra renders |
| `e2e_tts_playback` | login Mystic → ask question → tap speaker icon | audio plays, mini-player appears | voice works |
| `e2e_similarity_callout` | login Mystic → ask "are there similar charts?" | SimilarityCallout card renders | similarity works |
| `e2e_free_tier_upgrade_modal` | login Free → try to select Debate | upgrade modal with preview image | conversion |
| `e2e_drill_down_preference_persistence` | expand "Why?" → close → refresh page → same message | drill-down state remembered via localStorage | state persistence |
| `e2e_tts_over_quota` | simulate user at cap | speaker icon hidden on new messages | entitlement |

## 9. EPIC-Level Acceptance Criteria

- [ ] `chat_session.mode` column deployed; rows default to 'standard'
- [ ] `chat_message.drill_down` populated at turn completion
- [ ] `chart_reading_view` stores all 4 strategy projections
- [ ] DebateHandler passes all unit + e2e tests; produces divergence surface reliably
- [ ] UltraHandler passes ensemble-flag snapshot stability (F10 tests still green)
- [ ] Qdrant `chart_technique_v1` collection live; indexer worker catches up on all existing charts
- [ ] `find_similar_charts` tool returns real neighbours with privacy guarantees
- [ ] TTS endpoint streams MP3; usage metered; tier gate enforced
- [ ] Drill-down endpoint serves per-claim and whole-message payloads
- [ ] Session state persists across turns and is included in F12 cache key
- [ ] Frontend: ModePicker + DebateView + EnsembleChip/Pane + DrillDownPanel + VoicePlayer + SimilarityCallout all shipped
- [ ] All new frontend files ≤ 300 lines; zero `any` in chat v2 path; all colors via CSS vars
- [ ] Playwright e2e suite green in CI
- [ ] Unit test coverage ≥ 90% for new backend modules
- [ ] Tier gating verified (Free/Explorer blocked from premium features with graceful upgrade path)
- [ ] Documentation: `docs/markdown/ai-chat-v2.md` + CLAUDE.md section
- [ ] Playwright screenshot gallery captured: Standard vs Debate vs Ultra on same question

## 10. Rollout Plan

- **Feature flags:**
  - `AI_CHAT_V2_DEBATE_ENABLED` (default OFF; ON for Mystic+ at launch)
  - `AI_CHAT_V2_ULTRA_ENABLED` (default OFF; ON for Mystic+ at launch)
  - `AI_CHAT_V2_SIMILARITY_ENABLED` (default OFF; ON after indexer backfill completes)
  - `AI_CHAT_V2_TTS_ENABLED` (default OFF; ON for Mystic+ at launch)
- **Shadow compute:** Indexer worker runs in shadow for 48 hours before flipping `similarity` on; validates no performance regression on `chart_reading_view` update throughput.
- **Backfill strategy:**
  - `chart_reading_view` backfill via worker to populate all 4 strategy projections for existing charts. Estimated ≈ 24h at 100k charts. Idle-hour batching.
  - Qdrant index backfill runs in parallel; incremental by `chart_id` cursor; tolerates restarts.
- **Rollback plan:** Flip feature flags OFF → chat degrades to E11a behaviour. Data columns remain (ignored). No destructive migrations. Qdrant collection remains populated (safe to leave).
- **Monitoring:**
  - New Prometheus metrics: `ai_chat_debate_turns_total`, `ai_chat_ultra_turns_total`, `ai_chat_tts_seconds_total`, `ai_similarity_queries_total`, `ai_drill_down_fetches_total`.
  - Alert on tool-call latency P99 > 500 ms (vs 200 ms baseline) when debate/ultra engaged.
  - Alert on Qdrant query error rate > 1%.
- **Staged rollout:** 10% of Mystic+ → 50% → 100% over 7 days. Gate on thumbs-up rate not regressing below 75%.

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Debate mode confuses end-users ("why are the strategies fighting?") | Medium | High | In-product explainer modal first-run; copy-test the synthesis prose; collapsed-by-default UI |
| Ultra mode generates overly-long prose | Medium | Medium | System-prompt caps per-fact prose; UI shows chips, not paragraphs, for ensemble |
| Qdrant index goes stale after rule-version change | High | High | `feature_version` in payload; reindex on bump; alert on stale-index ratio |
| TTS pronounces Sanskrit badly | High | Medium | Phonetic fallback rules in sanitizer; OpenAI `tts-1-hd` tested for Indic; ElevenLabs backup |
| TTS cost explodes (audio seconds ≫ text tokens) | Medium | High | Quota-metered by seconds; alerts on cost per DAU; cache presigned urls after launch if repeat-listen rate warrants |
| Debate mode doubles Anthropic spend | Low | Medium | Single LLM loop, 4× read from reading_view; cost analysis in §3.1 shows ≤ 1.8× |
| Drill-down payloads bloat chat_message rows | Medium | Low | JSONB compression; cap at 16 KB per row (enforced); archive old messages per 90-day policy |
| Similarity retrievals leak user data | Low | Very High | Strict payload filtering; opt-in outcomes; anonymized aggregates only; security review |
| Multi-turn session_state becomes stale/mis-cached | Medium | Medium | Hash-based cache key; tests for cache-invalidation on state change |
| Tier-gate UI allows call through to backend | Medium | High | Backend is the source of truth; always enforce server-side; client-gate is UX only |
| Claim-marker regex fails on edge cases (nested claims, unclosed tags) | Medium | Medium | Lenient parser; on parse failure, fall back to "no drill-down available" without crashing |
| E12 astrologer preferences ship late → Ultra mode degrades | Low | Low | Fall back to Josi default weights with a tooltip explaining |
| Users spam Debate mode to abuse LLM | Low | Medium | Per-session concurrent-debate limit; per-user monthly cap via usage_service |
| Accessibility regressions in new components | Medium | Medium | RTL a11y tests (focus, ARIA); manual screen-reader pass; axe-core in Playwright |
| Mobile bottom-nav mini-player clips content | Low | Low | Layout reserves space; tested at 320px viewport |

## 12. References

- Master spec: [`docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`](../../../superpowers/specs/2026-04-19-classical-techniques-expansion-design.md) §3.4 (Ultra AI mode)
- Predecessor: [`P1/E11a-ai-chat-orchestration-v1.md`](../P1/E11a-ai-chat-orchestration-v1.md)
- Tool contract: [`P0/F10-typed-ai-tool-use-contract.md`](../P0/F10-typed-ai-tool-use-contract.md)
- Citation envelope: [`P0/F11-citation-embedded-responses.md`](../P0/F11-citation-embedded-responses.md)
- Prompt caching: [`P0/F12-prompt-caching-claude.md`](../P0/F12-prompt-caching-claude.md)
- Aggregation strategies: [`P0/F8-technique-result-aggregation-protocol.md`](../P0/F8-technique-result-aggregation-protocol.md)
- Experimentation: [`P1/E14a-experimentation-framework-v1.md`](../P1/E14a-experimentation-framework-v1.md)
- Astrologer workbench (consumes Ultra mode): [`P2/E12-astrologer-workbench-ui.md`](./E12-astrologer-workbench-ui.md)
- End-user surface (consumes Standard + Debate): [`P2/E13-end-user-simplification-ui.md`](./E13-end-user-simplification-ui.md)
- Future voice: `P5/D1-voice-native-ai-astrologer.md`
- Frontend conventions: [`CLAUDE.md`](../../../../CLAUDE.md) → "Frontend Conventions (MUST FOLLOW)"
- Qdrant documentation: https://qdrant.tech/documentation/
- OpenAI TTS: https://platform.openai.com/docs/guides/text-to-speech
- ElevenLabs: https://elevenlabs.io/docs
