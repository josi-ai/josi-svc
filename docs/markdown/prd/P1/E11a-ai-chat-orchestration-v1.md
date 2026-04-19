---
prd_id: E11a
epic_id: E11
title: "AI Chat Orchestration v1 (tool-use + citations)"
phase: P1-mvp
tags: [#ai-chat, #end-user-ux, #correctness, #performance]
priority: must
depends_on: [F1, F2, F8, F9, F10, F11, F12, E1a, E2a, E4a, E6a]
enables: [E11b, E13, E14a]
classical_sources: [bphs, saravali, phaladeepika]
estimated_effort: 3-4 weeks
status: draft
author: @agent
last_updated: 2026-04-19
---

# E11a — AI Chat Orchestration v1

## 1. Purpose & Rationale

Josi's central product differentiator is AI-powered classical astrology guidance. Until now, the AI surface has been prototype-level: `interpretation_engine_service.py` generates one-shot interpretations from precomputed chart data, with no conversational loop, no authoritative grounding, and no citations. The LLM cannot *query* the chart — it only sees a fixed blob of JSON. This produces hallucinated verse citations, inconsistent technique selection, and no feedback loop for improving source authority.

E11a makes AI chat real. It is the first shippable product surface built on the P0 foundation (F8 aggregation, F9 serving mart, F10 tool contract, F11 citations, F12 prompt caching) and the P1 engines (E1a dasa, E2a ashtakavarga, E4a yogas, E6a transits). The LLM is bound to a set of typed tools; every factual claim about a chart *must* come from a tool call; every tool return carries `CitedFact` envelopes with `source`, `citation`, `confidence`. The chat backend renders those envelopes into the response so the UI can surface provenance.

The commercial impact is immediate: B2C chat is the first monetizable flow (tier-gated), the first surface generating user thumbs signals for E14a's experimentation framework, and the first place Josi's classical accuracy becomes visible to paying customers.

## 2. Scope

### 2.1 In scope

- `chat_session` and `chat_message` SQLModel tables with migration
- `POST /api/v1/ai/chat` — SSE-streamed assistant response with citations
- `POST /api/v1/ai/chat/sessions` — create session (explicit) and auto-on-first-message
- `GET /api/v1/ai/chat/sessions/{id}` — fetch history
- `DELETE /api/v1/ai/chat/sessions/{id}` — soft-delete
- `POST /api/v1/ai/chat/sessions/{id}/messages/{mid}/signal` — thumbs feedback (feeds E14a)
- Anthropic SDK integration: `claude-sonnet-4-6` default, `claude-opus-4-7` for Mystic+
- Tool-use loop: register F10 tools; execute Claude's tool_use blocks; feed tool_result back; iterate until `stop_reason: end_turn`
- System prompt that mandates tool use before any factual claim about the chart
- Chart-context block (active yogas, current dasas, transit highlights) injected as a cache-breakpoint segment (F12)
- Citation aggregation from tool results; surfaced in response envelope
- Tier gating via `usage_service.py`: Free 5/day, Explorer 100/day, Mystic/Master unlimited
- SSE streaming of token-by-token output plus structured events (`tool_call`, `tool_result`, `citation`, `done`)
- Graceful tool-failure messaging ("technique not yet computed, queued")
- Rate-limit clean messages (429 body with retry-after)
- Unit + integration tests: tool roundtrip, citation propagation, rate limiting, tier gating, streaming
- Example conversations captured as fixtures for regression and demo

### 2.2 Out of scope

- **Debate mode / Ultra AI ensemble** — E11b (P2)
- **Semantic similarity via Qdrant** — E11b; `find_similar_charts` tool stubbed to return empty list in v1
- **Voice chat** — D1 (P5)
- **Multi-chart conversations** (compatibility, synastry) — treated as future work; v1 binds one session to one `chart_id`
- **Cross-session memory / digital-companion features** — I6 (P6)
- **Feedback-driven prompt auto-tuning** — later phase
- **Astrologer-authored chat overrides** — E12 (P2 astrologer workbench)
- **WebSocket transport** — SSE only in v1; WS infra from `realtime_service.py` reserved for future full-duplex needs
- **Chart creation flow within chat** — user must already have a `chart_id`

### 2.3 Dependencies

- F10 typed tool-use contract (Pydantic schemas, `@tool` registry)
- F11 citation-embedded response shape (`CitedFact` envelope)
- F12 Claude `cache_control` prompt caching
- F9 `chart_reading_view` populated by per-technique aggregation workers
- E1a / E2a / E4a / E6a engines implementing the tools' data sources
- `usage_service.py` for tier-gated quota checks
- `session_cache_service.py` for Redis auth/session (unchanged)
- Anthropic SDK ≥ 0.40 (per current `pyproject.toml`; bump if needed)

## 3. Technical Research

### 3.1 Why tool-use, not retrieval-augmented generation

Vanilla RAG embeds chart data + pre-computed interpretations and retrieves by semantic similarity. That fails for classical astrology because:

- Classical techniques are **procedural**, not textual — the right answer depends on exact planetary positions, not prose similarity.
- Numerical precision matters (dasa period boundaries to the minute; ashtakavarga bindu counts) and cannot be embedded reliably.
- Citations need to be *deterministic* — a specific verse for a specific rule, not a nearest-neighbor hit.
- The aggregation strategies (F8) produce answers that *change* with astrologer preference; static embedding pre-commits to one answer.

Tool-use gives the LLM a controlled surface: deterministic, typed, citation-carrying calls into Josi's computed star-schema. The LLM does reasoning; Josi does truth.

### 3.2 Why Anthropic Claude (not GPT-4)

- Superior tool-use reliability in multi-turn loops (measured in our internal bake-offs on the prototype `interpretation_engine_service.py`).
- `cache_control` primitives map cleanly onto F12.
- `claude-sonnet-4-6` hits the cost/quality sweet spot for the default tier; `claude-opus-4-7` is reserved for Mystic+ where depth > latency.
- Streaming SSE with interleaved `tool_use` blocks is first-class in the SDK.

We keep an adapter interface so GPT-4 / other providers can be swapped later without touching controllers (`src/josi/services/ai/llm_providers/`).

### 3.3 Tool-use loop shape

```
┌──────────────────────────────────────────────────────────────┐
│ 1. Build messages: [system, chart_context, history, user]    │
│ 2. Call Claude with tools=TOOL_REGISTRY                      │
│ 3. Stream response:                                          │
│    - text deltas → forward to SSE                            │
│    - tool_use block → execute tool → collect tool_result     │
│ 4. If stop_reason == "tool_use":                             │
│      append assistant + tool_result to messages              │
│      goto 2                                                  │
│    else (stop_reason == "end_turn"):                         │
│      emit final citations + done event                       │
└──────────────────────────────────────────────────────────────┘
```

Loop bounded at `MAX_TOOL_ITERATIONS = 8`. Beyond that, return best-effort response with `truncated: true` flag.

### 3.4 Prompt caching strategy (F12)

Three cache breakpoints per session:

1. **System + tool definitions** — stable per deploy; 1-hour TTL.
2. **Chart-context block** — stable per `chart_id`; invalidated by `chart_reading_view.last_computed_at`; 5-minute TTL.
3. **Message history** — grows during session; cached to the last assistant turn.

First message in a fresh session: full cache write (expensive). Subsequent messages within 5 min: cache hits on 1 + 2 + most of 3 → ~5× cost reduction, 2× latency improvement.

### 3.5 Alternatives considered

| Alternative | Rejected because |
|---|---|
| GPT-4 function calling | Tool loops less reliable in our bake-offs; cache primitives weaker |
| LangChain agent framework | Heavy abstraction; hides the Claude tool-use cycle we need to observe; harder to debug citations |
| Precompute all answers and serve from cache | Combinatorial explosion; cannot answer open-ended questions |
| WebSocket transport | SSE sufficient for one-way server-push; avoids full-duplex complexity of `realtime_service.py` for chat |
| One tool per technique family (coarse) | LLM picks wrong tool frequently; F10 opted for fine-grained typed tools |
| Store messages as JSONB array on `chat_session` | Per-message FKs, signals, and reads become awkward; we need per-message rows |

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| SSE vs WebSocket | SSE | Simpler; one-way suffices; avoids re-wiring `realtime_service.py` |
| Default model | `claude-sonnet-4-6` | Best quality/cost on free + Explorer tier |
| Upgrade model for Mystic+ | `claude-opus-4-7` | Premium users get deeper reasoning; cost absorbed by subscription |
| Streaming granularity | Token deltas + structured events | UI needs both: smooth text + pill-render citations/tool calls |
| Max tool iterations | 8 | Covers 99% of flows in prototype traces; hard ceiling prevents runaway loops |
| Session-to-chart binding | One chart per session | Simpler; synastry comes later |
| History retention | 90 days soft-delete; hard-delete on request | Default retention for feedback analysis; respects GDPR |
| Message-level signal grain | Per-message (user can thumb any assistant turn) | Finer attribution for E14a |
| Rate-limit enforcement layer | Service (not middleware) | Needs tier lookup + usage increment in same txn |
| Tool timeout | 3s per tool call | Computed reads should be <200ms P99 (F9); 3s is generous safety net |
| If tool fails | Return typed error to LLM; LLM decides (usually retries or apologises) | Better than hard-failing the turn |
| Where does chart-context block come from | `chart_reading_view` row (F9), serialized compact | Already aggregated per-strategy |
| How is usage incremented | Once per completed assistant turn (stop_reason=end_turn) | Partial/failed turns don't count against quota |

## 5. Component Design

### 5.1 New modules

```
src/josi/models/ai/
├── __init__.py
├── chat_session.py
└── chat_message.py

src/josi/schemas/ai/
├── chat_schemas.py              # request/response Pydantic models
└── streaming_events.py          # SSE event envelopes

src/josi/services/ai/
├── chat/
│   ├── __init__.py
│   ├── chat_orchestrator.py     # the tool-use loop
│   ├── prompt_builder.py        # system + context + history composition
│   ├── tool_executor.py         # dispatches F10 tools, collects CitedFacts
│   ├── citation_aggregator.py   # collects + dedupes CitedFacts across tool calls
│   ├── tier_gate.py             # quota checks against usage_service
│   └── streaming.py             # SSE event generator
├── llm_providers/
│   ├── __init__.py
│   ├── base.py                  # LLMProvider Protocol
│   └── anthropic_provider.py    # Claude SDK adapter
└── interpretation_service.py    # existing; unchanged in E11a

src/josi/repositories/
├── chat_session_repository.py
└── chat_message_repository.py

src/josi/api/v1/controllers/
└── ai_chat_controller.py        # new; separate from ai_controller.py (legacy)
```

### 5.2 Data model additions

```sql
-- ============================================================
-- chat_session: one conversation bound to one chart
-- ============================================================
CREATE TABLE chat_session (
    session_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id     UUID NOT NULL REFERENCES organization(organization_id),
    user_id             UUID NOT NULL REFERENCES "user"(user_id),
    chart_id            UUID NOT NULL REFERENCES astrology_chart(chart_id),
    title               TEXT,                            -- auto-derived from first user message
    cache_key           TEXT NOT NULL,                   -- opaque; used by F12 prompt caching
    model_used          TEXT NOT NULL,                   -- e.g., 'claude-sonnet-4-6'
    message_count       INTEGER NOT NULL DEFAULT 0,
    total_tokens_in     INTEGER NOT NULL DEFAULT 0,
    total_tokens_out    INTEGER NOT NULL DEFAULT 0,
    total_cache_reads   INTEGER NOT NULL DEFAULT 0,
    last_active_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    is_deleted          BOOLEAN NOT NULL DEFAULT false,
    deleted_at          TIMESTAMPTZ
);

CREATE INDEX idx_chat_session_user_recent
    ON chat_session(user_id, last_active_at DESC)
    WHERE is_deleted = false;

CREATE INDEX idx_chat_session_chart
    ON chat_session(chart_id, last_active_at DESC)
    WHERE is_deleted = false;

-- ============================================================
-- chat_message: every turn (user, assistant, tool_result)
-- ============================================================
CREATE TABLE chat_message (
    message_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id     UUID NOT NULL REFERENCES organization(organization_id),
    session_id          UUID NOT NULL REFERENCES chat_session(session_id) ON DELETE CASCADE,
    sequence            INTEGER NOT NULL,                -- monotonic per session, 1-based
    role                TEXT NOT NULL CHECK (role IN ('user','assistant','tool')),
    content             TEXT,                            -- text payload (user message or assistant text)
    tool_calls          JSONB NOT NULL DEFAULT '[]'::jsonb,
                        -- [{tool_use_id, name, input}, ...] on assistant rows
    tool_results        JSONB NOT NULL DEFAULT '[]'::jsonb,
                        -- [{tool_use_id, result, cited_facts}, ...] on tool rows
    citations           JSONB NOT NULL DEFAULT '[]'::jsonb,
                        -- aggregated CitedFact[] surfaced to user on assistant rows
    stop_reason         TEXT,                            -- 'end_turn' | 'tool_use' | 'max_tokens' | 'error'
    tokens_in           INTEGER,
    tokens_out          INTEGER,
    latency_ms          INTEGER,
    error               TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (session_id, sequence)
);

CREATE INDEX idx_chat_message_session
    ON chat_message(session_id, sequence);
```

Models use `TenantBaseModel` for `organization_id`, timestamps, soft-delete on session; message has its own lifecycle (no soft-delete — cascades via session).

### 5.3 API contract

**Create session (explicit or implicit on first message):**

```
POST /api/v1/ai/chat/sessions
Body: { chart_id: UUID, title?: string }
Response: {
  session_id: UUID,
  chart_id: UUID,
  title: string | null,
  model_used: string,
  created_at: ISO8601
}
```

**Send message (streamed SSE):**

```
POST /api/v1/ai/chat
Headers: Authorization, Accept: text/event-stream
Body: {
  session_id?: UUID,          // if absent, session auto-created
  chart_id: UUID,             // required if session_id absent
  user_message: string        // 1..4000 chars
}

SSE event stream:
  event: session
  data: {"session_id": "...", "message_id": "..."}

  event: tool_call
  data: {"tool_use_id": "toolu_01", "name": "get_yoga_summary", "input": {...}}

  event: tool_result
  data: {"tool_use_id": "toolu_01", "cited_facts_count": 4, "duration_ms": 18}

  event: text_delta
  data: {"delta": "Your current Vimshottari Mahadasa..."}

  event: citation
  data: {"index": 0, "source": "bphs", "citation": "BPHS 36.14-16", "confidence": 0.92, "fact_ref": "..."}

  event: done
  data: {
    "message_id": "...",
    "stop_reason": "end_turn",
    "citations": [...],
    "tool_calls": [...],
    "usage": {"tokens_in": 1234, "tokens_out": 567, "cache_reads": 1200}
  }

  event: error
  data: {"code": "rate_limit_exceeded", "retry_after_seconds": 3600, "message": "..."}
```

Non-streaming fallback: `Accept: application/json` returns the full envelope after the loop completes.

**Get session history:**

```
GET /api/v1/ai/chat/sessions/{session_id}
Response: {
  success: true,
  message: "ok",
  data: {
    session: {...},
    messages: [{message_id, role, content, tool_calls, tool_results, citations, created_at}, ...]
  }
}
```

**Signal feedback:**

```
POST /api/v1/ai/chat/sessions/{session_id}/messages/{message_id}/signal
Body: { kind: "thumbs_up" | "thumbs_down", note?: string }
Response: { success: true, message: "recorded" }
```

Signal handler writes one `aggregation_signal` row per unique `aggregation_event_id` referenced by the assistant message's citations (F2 table from P0).

### 5.4 Internal interfaces

```python
# src/josi/services/ai/chat/chat_orchestrator.py

class ChatOrchestrator:
    def __init__(
        self,
        session: AsyncSession,
        llm: LLMProvider,
        tool_executor: ToolExecutor,
        prompt_builder: PromptBuilder,
        tier_gate: TierGate,
        usage_service: UsageService,
    ): ...

    async def run(
        self,
        user_id: UUID,
        chart_id: UUID,
        user_message: str,
        session_id: UUID | None = None,
    ) -> AsyncIterator[StreamEvent]:
        """
        Drives the tool-use loop and yields StreamEvents.
        Persists chat_message rows as each turn completes.
        """
        await self.tier_gate.check_or_raise(user_id)
        session = await self._get_or_create_session(user_id, chart_id, session_id)
        messages = await self._load_history(session.session_id)
        messages.append(UserTurn(content=user_message))

        for iteration in range(MAX_TOOL_ITERATIONS):
            system_blocks = self.prompt_builder.build(session, messages)
            async for event in self.llm.stream(system_blocks, messages, TOOL_REGISTRY):
                yield event
                if event.type == "tool_use":
                    result = await self.tool_executor.execute(event)
                    messages.append(ToolTurn(result=result))
                    yield StreamEvent.tool_result(result)
            if messages[-1].stop_reason == "end_turn":
                await self.usage_service.increment(user_id, "ai_interpretations_used")
                break
        else:
            yield StreamEvent.done(truncated=True)
```

```python
# src/josi/services/ai/chat/tool_executor.py

class ToolExecutor:
    async def execute(self, tool_use: ToolUseBlock) -> ToolResult:
        """
        Dispatches to a registered F10 tool. Collects CitedFacts
        from the tool's return value. Wraps failures in ToolError
        so the LLM sees a structured result instead of crashing.
        Bounded by per-tool 3s timeout.
        """
```

```python
# src/josi/services/ai/llm_providers/anthropic_provider.py

class AnthropicProvider(LLMProvider):
    async def stream(
        self,
        system_blocks: list[SystemBlock],
        messages: list[Message],
        tools: list[ToolSpec],
    ) -> AsyncIterator[StreamEvent]:
        """
        Streams from Claude with cache_control markers on stable blocks.
        Emits text_delta, tool_use, stop_reason events.
        """
```

### 5.5 System prompt (stable; goes in cache block 1)

```
You are a classical Vedic astrology assistant grounded in primary sources
(BPHS, Saravali, Phaladeepika, Jaimini Sutras, Tajaka Neelakanthi).

RULES:
1. For any factual claim about the user's chart, you MUST call a tool
   first. Do not guess planetary positions, dasas, yogas, or transits.
2. When tool results include cited_facts, reference them naturally in
   your answer ("According to BPHS Ch. 36..."). Do not invent verses.
3. If a technique is not yet computed, the tool will say so. Acknowledge
   gracefully: "This technique isn't yet available for your chart — I've
   queued it; give me a few seconds."
4. Confidence scores from cross-source aggregation shape your tone:
   - >= 0.85: "strongly", "clearly"
   - 0.60-0.84: "likely", "tends to"
   - < 0.60: "some traditions hold", "there is disagreement"
5. Keep responses grounded, specific, and actionable. Classical guidance
   is not legal, medical, or financial advice — this is added as a
   standard disclaimer only when first asked about such topics.
```

### 5.6 Chart-context block (cache block 2, rebuilt per session open)

Built from `chart_reading_view`:

```json
{
  "chart_id": "...",
  "birth": "1991-03-14 06:20 IST, Chennai",
  "ascendant": "Pisces 14°22'",
  "active_yogas_top5": [...],
  "current_dasa": {"system": "vimshottari", "md": "Jupiter", "ad": "Saturn", ...},
  "transit_highlights": [{"event": "sade_sati_phase_2", "window": "..."}],
  "ashtakavarga_summary": {...},
  "astrologer_preference_key": "default"
}
```

Compact JSON; ~1-4 KB. Cache hit saves ~3k tokens per call.

### 5.7 Tier gating

```python
# src/josi/services/ai/chat/tier_gate.py

TIER_DAILY_LIMITS = {
    "free":     5,
    "explorer": 100,
    "mystic":   None,  # unlimited
    "master":   None,
}

class TierGate:
    async def check_or_raise(self, user_id: UUID) -> None:
        user = await self.user_repo.get_by_id(user_id)
        limit = TIER_DAILY_LIMITS[user.tier]
        if limit is None:
            return
        used_today = await self.usage_service.get_daily(user_id, "ai_interpretations_used")
        if used_today >= limit:
            raise TierQuotaExceeded(
                tier=user.tier, used=used_today, limit=limit,
                retry_after_seconds=_seconds_until_midnight_utc(),
            )
```

Model selection based on tier:

```python
MODEL_BY_TIER = {
    "free":     "claude-sonnet-4-6",
    "explorer": "claude-sonnet-4-6",
    "mystic":   "claude-opus-4-7",
    "master":   "claude-opus-4-7",
}
```

## 6. User Stories

### US-E11a.1: As a Free-tier user, I ask about my career next year and get a grounded, cited answer
**Acceptance:** The LLM calls `get_current_dasa`, `get_transit_events`, and `get_yoga_summary`. The streamed response references at least one classical citation. Response P95 latency (first-token) < 2s; full completion < 12s.

### US-E11a.2: As a Free-tier user, I cannot send a 6th message after hitting my daily limit
**Acceptance:** The 6th request returns HTTP 429 with a JSON body containing `retry_after_seconds` and a friendly message ("You've reached your 5-message daily limit. Resets in Xh."). No tokens are spent on Anthropic.

### US-E11a.3: As a Mystic-tier user, my chat uses Claude Opus and I get noticeably deeper analysis
**Acceptance:** `chat_session.model_used == "claude-opus-4-7"`. Test asserts model selection per tier.

### US-E11a.4: As any user, when a technique isn't computed yet, I get a helpful message, not a crash
**Acceptance:** Tool returns `ToolError(kind="not_computed", queued=true)`. LLM produces a graceful acknowledgment. The chart has a background compute job queued for that technique.

### US-E11a.5: As a user, I can thumbs-up an answer and the signal is recorded
**Acceptance:** `POST .../signal` with `kind="thumbs_up"` writes one `aggregation_signal` row per `aggregation_event_id` referenced in the assistant message's citations.

### US-E11a.6: As the product team, I can see citations in every assistant response that made a factual claim
**Acceptance:** 100% of assistant messages with `tool_calls != []` have `citations != []`. Regression test asserts this across the fixture suite.

### US-E11a.7: As a returning user, my second message in the same session is faster and cheaper
**Acceptance:** On second message within 5 min, `total_cache_reads > 0` on the session; logged latency is ≥ 25% lower than first message's first-token latency.

### US-E11a.8: As any user, SSE stream sends tokens smoothly and I can cancel mid-stream
**Acceptance:** Client disconnect stops Anthropic stream within 500ms. Partial assistant message is persisted with `stop_reason='client_cancel'`. Usage is NOT incremented.

## 7. Tasks

### T-E11a.1: Model + migration
- **Definition:** `chat_session` and `chat_message` SQLModel classes; autogenerate Alembic migration.
- **Acceptance:** `alembic upgrade head` applies; FKs, indexes, check constraints present; `downgrade -1` reverts cleanly.
- **Effort:** 1 day
- **Depends on:** none

### T-E11a.2: Repositories
- **Definition:** `ChatSessionRepository` and `ChatMessageRepository` with tenant-filtered CRUD. Soft-delete for session.
- **Acceptance:** Unit tests cover create/get/list-by-user/soft-delete; tenant isolation verified.
- **Effort:** 1 day
- **Depends on:** T-E11a.1

### T-E11a.3: LLMProvider adapter (Anthropic)
- **Definition:** Streaming adapter around Anthropic SDK; emits typed `StreamEvent`s; honors `cache_control`.
- **Acceptance:** Given fake Anthropic stream, adapter yields correct event sequence. Contract tests against recorded Anthropic cassettes.
- **Effort:** 3 days
- **Depends on:** F10, F11, F12 complete

### T-E11a.4: PromptBuilder
- **Definition:** Builds `[system, chart_context, history, user]` with cache markers; reads chart_context from `chart_reading_view`.
- **Acceptance:** Unit tests: cache markers in correct positions; chart context matches F9 row; token count < 4k for typical chart.
- **Effort:** 1 day
- **Depends on:** T-E11a.3, F9

### T-E11a.5: ToolExecutor
- **Definition:** Dispatches F10 `@tool` registry; 3s per-tool timeout; wraps failures in `ToolError`; collects `CitedFact`s.
- **Acceptance:** Unit tests: successful dispatch, timeout, typed error, citation collection. All 5 P1 tools (`get_yoga_summary`, `get_current_dasa`, `get_transit_events`, `get_tajaka_summary`, `find_similar_charts`-stub) wired.
- **Effort:** 2 days
- **Depends on:** F10 tool registry, E1a, E2a, E4a, E6a engines

### T-E11a.6: ChatOrchestrator + streaming
- **Definition:** Main tool-use loop; persists per-turn `chat_message` rows; generates SSE events; bounded at `MAX_TOOL_ITERATIONS=8`.
- **Acceptance:** Integration test with fake LLM: 2-iteration tool-use loop completes, persists 4 `chat_message` rows (user, tool_use_assistant, tool_result, final_assistant), emits correct SSE events.
- **Effort:** 3 days
- **Depends on:** T-E11a.4, T-E11a.5

### T-E11a.7: TierGate + model selection
- **Definition:** Daily-quota check via `usage_service`; tier → model map; raise `TierQuotaExceeded` → HTTP 429.
- **Acceptance:** Unit tests for all 4 tiers; quota-exceeded path increments no usage; retry-after math correct near midnight UTC.
- **Effort:** 1 day
- **Depends on:** T-E11a.6

### T-E11a.8: AI chat controller
- **Definition:** `POST /api/v1/ai/chat`, session CRUD endpoints, signal endpoint. SSE via `StreamingResponse`.
- **Acceptance:** E2E test hits real Anthropic (cassette-recorded) and streams a complete response with citations.
- **Effort:** 2 days
- **Depends on:** T-E11a.7

### T-E11a.9: Signal → aggregation_signal wiring
- **Definition:** Thumbs endpoint resolves assistant message's citations → aggregation_event IDs → writes one `aggregation_signal` per event with `signal_type` in `{'user_thumbs_up','user_thumbs_down'}`.
- **Acceptance:** Integration test: thumbs-up on a message with 3 citations inserts 3 distinct signal rows.
- **Effort:** 1 day
- **Depends on:** T-E11a.8, F2 signal table

### T-E11a.10: Citation aggregator + dedup
- **Definition:** Collects `CitedFact`s across tool calls within one turn; dedupes by (source, citation, aggregation_event_id); orders by confidence desc.
- **Acceptance:** Unit tests cover dedup, ordering, preservation of highest-confidence duplicate.
- **Effort:** 0.5 day
- **Depends on:** T-E11a.5, F11

### T-E11a.11: Fixture suite + replay harness
- **Definition:** 10 realistic conversation fixtures (recorded Anthropic streams + expected citations). Replay test asserts full output envelope.
- **Acceptance:** `pytest tests/integration/ai/test_chat_fixtures.py` green.
- **Effort:** 2 days
- **Depends on:** T-E11a.8

### T-E11a.12: Observability
- **Definition:** Structured log per turn (session_id, tokens_in, tokens_out, cache_reads, tool_count, latency_first_token_ms, latency_total_ms). Prometheus metrics: `ai_chat_turn_total`, `ai_chat_tool_call_total`, `ai_chat_first_token_latency_seconds`, `ai_chat_quota_exceeded_total`.
- **Acceptance:** Metrics scraped in dev; log schema documented in `docs/markdown/observability/ai_chat.md`.
- **Effort:** 1 day
- **Depends on:** T-E11a.8

### T-E11a.13: Docs
- **Definition:** `docs/markdown/api/ai-chat.md` with endpoint spec, SSE event format, tier limits, examples.
- **Acceptance:** Docs reviewed; `/docs` OpenAPI page shows the endpoints with full schemas.
- **Effort:** 0.5 day
- **Depends on:** T-E11a.8

## 8. Unit Tests

### 8.1 ChatOrchestrator

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_orchestrator_one_tool_one_turn` | user msg → 1 tool_use → tool_result → end_turn | 4 chat_message rows; citations surfaced; usage incremented once | happy path |
| `test_orchestrator_multi_tool_sequential` | user msg → 3 tool_uses interleaved with 2 text deltas → end_turn | 3 tool executions in order; all citations aggregated | sequential tool loop |
| `test_orchestrator_max_iterations_truncates` | LLM stuck in tool loop | returns with `truncated=true` after 8 iterations; logs warning | guard against runaway |
| `test_orchestrator_tool_failure_graceful` | tool raises | ToolError fed back to LLM; final message produced | resilience |
| `test_orchestrator_client_cancel` | client disconnects mid-stream | Anthropic stream closed ≤ 500ms; usage NOT incremented; message saved with stop_reason='client_cancel' | cancel semantics |
| `test_orchestrator_session_autocreate` | no session_id provided | new chat_session row created; session_id echoed in first event | implicit session |

### 8.2 TierGate

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_free_tier_allows_first_five` | Free user, used=4 | passes | under limit |
| `test_free_tier_blocks_sixth` | Free user, used=5 | `TierQuotaExceeded` raised | at limit |
| `test_explorer_tier_100_boundary` | Explorer, used=99, then used=100 | 99 passes, 100 raises | Explorer limit |
| `test_mystic_unlimited` | Mystic user, used=10000 | passes | unlimited tier |
| `test_retry_after_math` | current time = 23:30 UTC | retry_after_seconds ≈ 1800 | resets at midnight UTC |
| `test_model_selection_per_tier` | Mystic | returns `claude-opus-4-7` | premium model |

### 8.3 ToolExecutor

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_tool_dispatch_success` | valid tool_use for `get_yoga_summary` | ToolResult with CitedFacts | wiring works |
| `test_tool_timeout_3s` | tool that sleeps 4s | ToolError(kind='timeout') after 3s | timeout enforcement |
| `test_tool_unknown_name` | `tool_use.name = 'nonexistent'` | ToolError(kind='unknown_tool') | safety |
| `test_tool_input_schema_violation` | wrong arg types | ToolError(kind='invalid_input') before dispatch | F10 schema validation |
| `test_tool_result_collects_citations` | tool returns 3 CitedFacts | ToolResult.cited_facts has 3 items | citation path |

### 8.4 CitationAggregator

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_dedup_by_source_and_citation` | 2 identical cited facts | 1 in output | dedup |
| `test_order_by_confidence_desc` | 3 facts with conf 0.6, 0.9, 0.75 | ordered 0.9, 0.75, 0.6 | UX ranking |
| `test_preserves_higher_conf_duplicate` | 2 dupes with conf 0.7 and 0.9 | keeps the 0.9 one | correctness |

### 8.5 PromptBuilder

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_system_block_has_cache_marker` | build() | system block has `cache_control={'type':'ephemeral'}` | F12 caching |
| `test_chart_context_reads_from_view` | chart_id with populated view | chart_context block matches view row | F9 wiring |
| `test_history_excludes_tool_noise_for_context_budget` | 50-message session | only last N within token budget included | budget management |
| `test_chart_context_omitted_when_view_missing` | chart without view row | block replaced with minimal fallback; warning logged | safety on missing F9 |

### 8.6 SSE streaming

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_sse_event_sequence_happy_path` | one-tool turn | events in order: session, tool_call, tool_result, text_delta*, citation*, done | contract |
| `test_sse_error_event_on_anthropic_failure` | Anthropic 500 | emits `error` event with code; stream closes | error surface |
| `test_sse_keepalive_during_long_tool` | tool takes 2s | keepalive comments emitted to prevent proxy timeouts | infra resilience |

### 8.7 Signal endpoint

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_thumbs_up_writes_signal_per_citation` | assistant msg with 3 citations | 3 aggregation_signal rows | signal attribution |
| `test_thumbs_down_same_path` | assistant msg with 1 citation | 1 row, signal_type='user_thumbs_down' | symmetry |
| `test_signal_on_tool_free_message_noop` | message with 0 citations | 200 OK, 0 rows, warning logged | nothing to attribute |

### 8.8 Integration

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_full_chat_roundtrip` | POST with user_message against cassette | 200 OK, SSE stream complete, chat_session + 4 chat_message rows persisted | E2E sanity |
| `test_rate_limit_roundtrip` | Free user at limit | HTTP 429 with retry-after body | tier enforcement E2E |
| `test_fixture_suite_regression` | 10 recorded conversations | each replays to exact expected envelope | regression guard |

## 9. EPIC-Level Acceptance Criteria

PRD is "done" when ALL of these pass:

- [ ] `chat_session` and `chat_message` tables migrated and queryable
- [ ] `POST /api/v1/ai/chat` streams a valid SSE response that includes at least one citation for any factual chart question
- [ ] Tool-use loop honors `MAX_TOOL_ITERATIONS=8` with graceful truncation
- [ ] Tier gating enforced: Free 5/day, Explorer 100/day, Mystic/Master unlimited
- [ ] Model selection per tier verified (sonnet for free/explorer, opus for mystic/master)
- [ ] Prompt caching active: second message in session logs `cache_reads > 0`
- [ ] Signal endpoint writes one `aggregation_signal` per cited `aggregation_event_id`
- [ ] Client-cancel stops upstream Anthropic call within 500ms and does not charge quota
- [ ] Fixture suite (10 conversations) green and wired to CI
- [ ] Unit test coverage ≥ 90% across new modules
- [ ] Integration test hits full path: controller → orchestrator → Anthropic cassette → DB persistence → SSE
- [ ] Prometheus metrics exported and scraped in dev
- [ ] OpenAPI docs at `/docs` show all four endpoints with full schemas
- [ ] `docs/markdown/api/ai-chat.md` written with SSE event reference
- [ ] CLAUDE.md updated with AI chat entry point + tier gating convention
- [ ] Golden chart suite (E15a) adds assertions for chat responses on 5 canonical charts

## 10. Rollout Plan

- **Feature flag:** `AI_CHAT_V1_ENABLED` (default off; enabled for Josi staff first, then 10% canary, then 100%)
- **Shadow compute:** N/A (new surface)
- **Backfill:** N/A (empty on launch)
- **Rollback plan:** Disable flag → endpoint returns 503 `Service temporarily disabled`. No schema rollback needed — `chat_session`/`chat_message` inert. If models/schema change, `alembic downgrade -1`.

Rollout sequence:

1. Week 1: internal staff (flag on for `user.is_staff=true`)
2. Week 2: 10% Mystic+ users (hashed rollout by user_id)
3. Week 3: 100% of paid tiers
4. Week 4: 100% all tiers including Free

Abort triggers: first-token P95 > 5s for 30 min, error rate > 2% for 15 min, Anthropic quota > 80% sustained.

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| LLM skips tool use and hallucinates | Medium | High | System prompt mandates tool use; regression suite asserts citation presence on factual prompts; property test samples random chart questions |
| Tool loop runs forever | Low | High | `MAX_TOOL_ITERATIONS=8` hard cap; Prometheus alert on `truncated=true` rate |
| Anthropic API outage | Medium | High | Retry with exponential backoff once; then graceful 503 with friendly copy; status page integration |
| Runaway cost on Opus tier | Low | Medium | Per-user daily spend cap (computed from token usage); auto-escalate to eng on $X/day/user |
| SSE dropped by proxy/CDN | Medium | Medium | Emit keepalive `:` comment every 5s; document Cloud Run timeout (60 min) in runbook |
| Cache markers misplaced → no cache hits | Medium | Medium | Explicit test asserting `cache_read_input_tokens > 0` on second call; dashboard panel |
| Client-cancel leaks Anthropic streams | Medium | Medium | `async with` cancellation semantics; integration test explicitly cancels and asserts stream closed |
| Tool input schema drift between F10 and engines | Low | Medium | Contract tests from tool registry against each engine's actual output |
| Signal attribution wrong at citation dedup boundary | Low | Medium | Explicit dedup-by-aggregation_event_id test; analytics spot-checks in first week |
| Quota bypass via concurrent requests | Medium | Medium | Redis `INCR` is atomic; tier check + increment in same atomic op |

## 12. References

- Master spec: [`docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`](../../../superpowers/specs/2026-04-19-classical-techniques-expansion-design.md) §3 (AI chat integration)
- F10 Typed AI Tool-Use Contract: [`../P0/F10-typed-ai-tool-use-contract.md`](../P0/F10-typed-ai-tool-use-contract.md)
- F11 Citation-Embedded Response Shape: `../P0/F11-citation-embedded-responses.md`
- F12 Prompt Caching via Claude cache_control: `../P0/F12-prompt-caching-claude.md`
- F9 chart_reading_view: [`../P0/F9-chart-reading-view-table.md`](../P0/F9-chart-reading-view-table.md)
- Existing prototype: `src/josi/services/interpretation_engine_service.py` (to be superseded for chat flows)
- Existing WebSocket infra: `src/josi/services/realtime_service.py` (not used in v1; reserved for D1)
- Anthropic Claude API streaming + tool use docs (SDK ≥ 0.40)
- Usage service: `src/josi/services/usage_service.py`
