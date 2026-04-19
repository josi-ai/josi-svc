---
prd_id: F12
epic_id: F12
title: "Prompt caching via Claude cache_control (chat-session context reuse)"
phase: P0-foundation
tags: [#ai-chat, #performance]
priority: must
depends_on: [F10]
enables: [E11a, E11b]
classical_sources: []
estimated_effort: 3-4 days
status: draft
author: @agent
last_updated: 2026-04-19
---

# F12 — Prompt Caching via Claude `cache_control`

## 1. Purpose & Rationale

Each AI chat turn for Josi includes substantial stable context: chart summary, active yogas, current dasas, relevant classical rule definitions, recent transits. Re-sending this ~3–8 KB of tokens on every turn is wasteful. Anthropic's API supports **prompt caching** via `cache_control: {type: "ephemeral"}` markers on message content blocks — cached blocks cost ~10% of input-token price and ~20% of the latency on cache hits, with a default TTL of 5 minutes (sliding on each hit).

For a typical 6-turn Josi chat session within 5 minutes:

- Without caching: ~8 KB × 6 turns = 48 KB of input tokens billed and processed.
- With caching: 8 KB (write) + 0.8 KB × 5 (hits, 10% cost) = ~12 KB billable.
- **~4x cost reduction, ~2x latency improvement.**

At projected P3 scale (100k DAU, 6 turns/day average), this is ~$300k/year in API cost savings and a materially better P50 latency on non-first turns.

This PRD specifies:

- The three-segment prompt partition (cached chart context / dynamic history / current turn).
- What goes into the chart-context block (and what doesn't).
- Size budget and compression rules.
- Session mechanics (`session_id` → cache key correspondence).
- Instrumentation (hit/miss metrics, per-turn cost reporting).
- Integration with the existing `AIInterpretationService` in `src/josi/services/ai/`.

## 2. Scope

### 2.1 In scope
- Prompt partitioning strategy: cached vs non-cached blocks
- `ChartContextBuilder` that produces the cached block from `chart_reading_view` (F9) and applicable classical rule definitions
- Size-budget enforcement (target 3–8 KB; hard cap 16 KB per cached block)
- Session registry in Redis mapping `session_id` → `cache_bucket_meta` (last-hit timestamp, TTL tracking)
- `MessageBuilder` that assembles Anthropic `messages.create(...)` call with `cache_control` applied
- Model selection per subscription tier (Sonnet 4.6 default; Opus 4.7 premium)
- Instrumentation: Prometheus metrics for cache writes/hits/misses, per-session cost, cache TTL expiries
- Dashboard JSON for cache hit rate
- Integration into `AIInterpretationService` + E11a orchestration loop
- Unit tests, cost estimation tests, integration with mocked Anthropic responses

### 2.2 Out of scope
- Long-lived (> 5 minute) caching (requires Anthropic's `ttl: "1h"` tier — revisit in P1 if cost-justified)
- Caching across sessions for the same chart (every session rebuilds; acceptable given chart context may differ per session mode)
- Caching of tool definitions themselves (they're small and stable enough that system-message caching covers it)
- Streaming partial cache writes (Anthropic doesn't expose partial cache granularity)
- Fallback to OpenAI provider's caching (P1)

### 2.3 Dependencies
- F9 (`chart_reading_view` supplies the cached context)
- F10 (tool definitions stable → reusable in cached portion)
- Existing `anthropic.AsyncAnthropic` client (pinned `anthropic = "^0.40.0"` in `pyproject.toml`)
- Redis for session registry
- `settings.anthropic_api_key` already wired in `src/josi/core/config.py`

## 3. Technical Research

### 3.1 Anthropic cache_control primer

Anthropic accepts `cache_control: {"type": "ephemeral"}` on individual content blocks within:
- `system` (as a list of text blocks)
- `messages[i].content` blocks
- `tools[i]` (full tool object via top-level content block)

A cached prefix is defined by the **last cache_control marker** before the non-cached suffix. Up to 4 cache breakpoints per request. The cache key is the exact token sequence of everything up to and including the marked block, across system + tools + messages.

Semantics:
- **Cache write**: first request at a given prefix; Anthropic bills at normal rate + ~25% write surcharge.
- **Cache hit**: subsequent request with identical prefix within TTL; Anthropic bills at ~10% of input token cost.
- **TTL**: 5 minutes by default (`ttl: "5m"`). Sliding on each hit (each hit resets the 5-min window).
- **Minimum cacheable size**: 1024 tokens (Sonnet 4.6) / 2048 tokens (Opus 4.7). Below minimum = silent no-op.

### 3.2 Prompt partition strategy

We split the request into three tiers:

```
┌─────────────────────────────────────────────────────────────┐
│  SYSTEM PROMPT                                              │
│    ┌─ assistant persona + instructions  (cached)            │
│    └─ citation/tone fragment (F11)       (cached)           │
├─────────────────────────────────────────────────────────────┤
│  TOOLS=[...]                              (cached)          │
├─────────────────────────────────────────────────────────────┤
│  MESSAGES                                                   │
│    user turn #1: [CHART_CONTEXT block, cache_control HERE]  │  ← cache breakpoint
│                  [plus user's initial question, non-cached] │
│    assistant:    tool_use + text                            │
│    user turn #2: [tool_result + user's follow-up]           │
│    ...                                                      │
│    user turn #N: current turn  (non-cached)                 │
└─────────────────────────────────────────────────────────────┘
```

The **cached prefix** terminates at the end of the CHART_CONTEXT block inside the first user message. Subsequent turns re-send the same prefix + append history + current turn. On each subsequent call within 5 minutes, Anthropic serves the prefix from cache.

We use exactly **two cache breakpoints per request**:
1. End of tools block (`cache_control` on the last tool entry).
2. End of CHART_CONTEXT block (`cache_control` on that content block).

Breakpoint #1 allows reuse across all sessions for all users (tools are global). Breakpoint #2 allows per-session, per-chart reuse.

### 3.3 CHART_CONTEXT block contents

Built from `chart_reading_view` (F9). Target 3–8 KB plain text. Contents, in order:

1. **Chart identity line**: "Chart for [first name] born [birth date] in [place], timezone [tz]."
2. **Chart summary**: ascendant sign + lord, sun sign, moon nakshatra, birth time precision.
3. **Active yogas (top 15 by strength)**: one line per yoga: `"{display_name} ({classical name}): active, strength=X, per {source}, {citation}. {cross_source_agreement}"`
4. **Current dasas**: one line per system (vimshottari, yogini, ashtottari): mahadasa/antardasa/pratyantardasa + current date.
5. **Transit highlights**: Sade Sati phase if active; upcoming major transits within 6 months.
6. **Tajaka summary** (if computed): Muntha sign, year lord.
7. **Jaimini summary** (if computed): chara karakas (atmakaraka, amatyakaraka), arudha lagna.
8. **Applicable classical rule citations used for active yogas above** (so Claude can quote verses without a tool-call round-trip). Stored as a deduplicated list.

Omitted: inactive yogas (too large and uninformative); full bhava/planet positions (Claude can tool-call if needed); full dasa tables past level 3.

### 3.4 Compression rules

- Use abbreviations where LLM-robust: "MD/AD/PD" for mahadasa/antardasa/pratyantardasa.
- Classical names use IAST transliteration only (not Devanagari) to save bytes; Devanagari retrievable via tool if asked.
- Citations in short form: "BPHS 36.14-16" not "Brihat Parashara Hora Shastra, Chapter 36, verses 14-16".
- Strip whitespace-heavy formatting; use newline-separated compact lines.

We enforce the 16 KB hard cap at build time. If over cap, prune: drop inactive yogas, drop dasa systems beyond vimshottari, drop Tajaka/Jaimini summaries. Log the pruning event.

### 3.5 Model selection and tier mapping

| Subscription tier | Model |
|---|---|
| Free | `claude-haiku-4-5` |
| Explorer | `claude-sonnet-4-6` |
| Mystic | `claude-sonnet-4-6` |
| Master (premium) | `claude-opus-4-7` |

All three models support `cache_control`. Minimum cacheable size differs:
- Haiku 4.5: 512 tokens
- Sonnet 4.6: 1024 tokens
- Opus 4.7: 2048 tokens

Our chart context target (3–8 KB ≈ 750–2000 tokens) sits at the Sonnet/Opus minimums. We enforce a **floor padding** to ensure the cached block always exceeds the model's minimum: if content is below 2048 tokens (worst case), pad with a verbatim "chart_context_v1" marker and harmless meta lines (table of what's known/not known) — cheap padding that also helps the LLM orient.

### 3.6 Session mechanics

```
Redis key: ai:chat:session:{session_id}
Value: JSON {
  "chart_id": "...",
  "user_id": "...",
  "audience": "end_user" | "astrologer",
  "model": "claude-sonnet-4-6",
  "chart_context_hash": "sha256(...)",
  "last_call_at": "2026-04-19T12:34:56Z",
  "cache_hit_count": 3,
  "cache_miss_count": 1,
  "last_ttl_expiry_at": "2026-04-19T12:40:01Z"
}
Redis TTL: 30 minutes (we track sessions beyond cache window for analytics)
```

On each turn:
1. Load session; if missing or `now - last_call_at > 300s`, treat as cache miss.
2. Re-build chart context; compare `chart_context_hash`. If different, cache miss (and re-write).
3. If same hash AND within 300s: expect cache hit; annotate metric accordingly.
4. Always re-send the prefix with `cache_control`; Anthropic decides hit vs write.
5. Update session state after response.

Note: we do not force `session_id` → cache key equivalence in Anthropic's API (Anthropic hashes the tokens). We just make `session_id` the bookkeeping handle so our code knows whether we *expect* a hit.

### 3.7 Cost model

Per turn within cache window:

```
Cost_turn_N = (prefix_tokens * 0.1) + (history_tokens * 1.0) + (current_turn_tokens * 1.0) + output_tokens * output_price
```

Per turn without caching:

```
Cost_turn_N = (prefix_tokens * 1.0) + (history_tokens * 1.0) + (current_turn_tokens * 1.0) + output_tokens * output_price
```

For 6-turn session with 2000-token prefix:

| Metric | No cache | With cache |
|---|---|---|
| Prefix tokens billed | 2000 × 6 = 12000 | 2000 × 1.25 (first write) + 2000 × 0.1 × 5 = 3500 |
| Savings | — | **~70%** on prefix tokens |

Prefix is the dominant input cost, so overall input cost drops ~50–70%.

### 3.8 Instrumentation

Prometheus metrics:
- `ai_chat_cache_writes_total{model}` (counter)
- `ai_chat_cache_hits_total{model}` (counter)
- `ai_chat_cache_misses_total{model}` (counter; subdivided by reason: `expired`, `context_changed`, `first_turn`)
- `ai_chat_cache_hit_rate{model}` (gauge, rolling 5-min)
- `ai_chat_prefix_tokens{model}` (histogram)
- `ai_chat_turn_cost_usd_estimate{model, hit}` (histogram)

Dashboard: Grafana JSON in `ops/dashboards/ai_chat_cache.json` with panels for hit rate, prefix size P95, cost per session.

The Anthropic API response carries `usage.cache_creation_input_tokens` and `usage.cache_read_input_tokens` — we use those directly as ground truth rather than self-inference.

### 3.9 Alternatives considered

| Alternative | Rejected because |
|---|---|
| Don't cache; keep prompts small | Chart context below minimum cache size = silent no-op; but we want rich context for quality. Caching unlocks richer context without cost penalty. |
| Cache in our own Redis and POST only deltas | Anthropic doesn't support incremental cache reconstitution; must be token-identical prefix |
| Cache ENTIRE conversation (including history) | History changes every turn by definition; can't be cached past turn N |
| One cache breakpoint only | Losing tools-prefix reuse (tools are global but tied to CHART_CONTEXT by positional prefix); 2 breakpoints cleanly separate global vs session |
| Re-cache on every turn (force write) | Pays 25% write surcharge every turn; defeats the purpose |
| Use `ttl: "1h"` extended tier | 2x write cost; unclear if needed at P0; revisit based on session-length data from E11a |

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| Number of cache breakpoints | 2 (tools end + chart context end) | Clean reuse boundaries |
| TTL choice | 5-min ephemeral (default) | Matches typical session; lower cost than 1h tier |
| Session ID source | `session_id` from E11a orchestrator (Clerk session + nonce) | Well-defined per chat session |
| What triggers cache miss by design | context hash change OR first turn OR > 300s gap | Predictable, instrumentable |
| Floor padding content | "chart_context_v1" marker + known/unknown meta lines | Safe, auditable, helps LLM orientation |
| Model per tier | Haiku free, Sonnet default, Opus premium | Existing cost/performance tiers |
| Cache behavior when Anthropic upgrades model version | Treat new model version as new cache key (Anthropic does this anyway) | Aligns with Anthropic's own semantics |
| Cache behavior across audience (end_user vs astrologer) | Different context → different hash → different cache entry | Audience change is rare, not worth optimization |
| Whether to cache tool definitions | Yes, via breakpoint #1 | Free win; tools are global |
| Metric ground truth | Anthropic `usage.cache_*_tokens` | No self-inference drift |

## 5. Component Design

### 5.1 New modules

```
src/josi/services/ai/
├── chart_context_builder.py       # builds cached chart context block
├── message_builder.py             # composes Anthropic messages.create(...) payload
├── cache_session_registry.py      # Redis-backed session state
├── cost_estimator.py              # per-turn cost projection + reporting
└── model_selector.py              # tier → model mapping

ops/dashboards/
└── ai_chat_cache.json             # Grafana dashboard
```

### 5.2 Data model

No database changes. Redis schema only:

```
Key: ai:chat:session:{session_id}
TTL: 1800s (30 min)
Value (JSON):
{
  "chart_id": UUID,
  "user_id": UUID,
  "organization_id": UUID,
  "audience": "end_user" | "astrologer",
  "model": str,
  "chart_context_hash": str (hex),
  "last_call_at": ISO timestamp,
  "cache_hit_count": int,
  "cache_miss_count": int,
  "cache_write_count": int,
  "total_input_tokens": int,
  "total_output_tokens": int,
  "total_cache_read_tokens": int,
  "total_cache_creation_tokens": int
}
```

### 5.3 ChartContextBuilder

```python
# src/josi/services/ai/chart_context_builder.py

from hashlib import sha256
from josi.repositories.chart_reading_view_repo import ChartReadingViewRepository


class ChartContextBuilder:
    """Builds the cacheable chart-context text block from chart_reading_view."""

    MIN_TOKEN_FLOOR = 2100   # above Opus 4.7 minimum; safe for all models
    HARD_CAP_TOKENS = 4000   # ~16KB; prune rather than exceed

    def __init__(self, reading_view_repo: ChartReadingViewRepository): ...

    async def build(
        self,
        chart_id: UUID,
        organization_id: UUID,
        audience: Literal["end_user", "astrologer"],
    ) -> ChartContextBlock:
        """Returns (text, token_count, hash). Prunes to stay within cap."""
        row = await self.reading_view_repo.get_by_chart_id(chart_id, organization_id)
        if row is None:
            # No reading view yet — return a minimal placeholder block with
            # "computing" marker; the LLM is instructed to tool-call instead.
            return self._empty_block(chart_id, audience)

        sections: list[str] = []
        sections.append(self._identity_line(row))
        sections.append(self._chart_summary(row))
        sections.append(self._active_yogas_section(row, limit=15))
        sections.append(self._current_dasas_section(row))
        sections.append(self._transit_highlights_section(row))
        if row.tajaka_summary:
            sections.append(self._tajaka_section(row))
        if row.jaimini_summary:
            sections.append(self._jaimini_section(row))
        sections.append(self._rule_citations_section(row, used_in_yogas=True))

        text = "\n\n".join(sections)
        text = self._prune_if_over_cap(text)
        text = self._pad_if_under_floor(text)

        return ChartContextBlock(
            text=text,
            token_count=self._count_tokens(text),
            hash=sha256(text.encode()).hexdigest(),
        )
```

### 5.4 MessageBuilder

```python
# src/josi/services/ai/message_builder.py

class MessageBuilder:
    """Assembles Anthropic messages.create(...) payload with cache_control markers."""

    def build_request(
        self,
        *,
        model: str,
        system_prompt: str,
        tools: list[dict],
        chart_context: ChartContextBlock,
        history: list[dict],            # prior turns (non-cached)
        current_turn: str,              # current user message
        max_tokens: int = 2048,
    ) -> dict:
        """Returns the dict ready to pass to `anthropic.AsyncAnthropic.messages.create(**kwargs)`."""

        # System: list of text blocks; cache_control on last to cache persona + tone fragment.
        system_blocks = [
            {"type": "text", "text": system_prompt,
             "cache_control": {"type": "ephemeral"}},
        ]

        # Tools: mark last tool with cache_control (becomes breakpoint #1).
        tools_with_cache = [*tools]
        if tools_with_cache:
            tools_with_cache[-1] = {
                **tools_with_cache[-1],
                "cache_control": {"type": "ephemeral"},
            }

        # First user message: chart context block + (this-turn OR stub).
        first_user_content = [
            {"type": "text",
             "text": f"<chart_context>\n{chart_context.text}\n</chart_context>",
             "cache_control": {"type": "ephemeral"}},   # breakpoint #2
        ]

        # Subsequent history turns flow in after. Current turn appended last.
        messages = [
            {"role": "user", "content": first_user_content},
            *history,
            {"role": "user", "content": current_turn},
        ]

        return {
            "model": model,
            "system": system_blocks,
            "tools": tools_with_cache,
            "messages": messages,
            "max_tokens": max_tokens,
        }
```

### 5.5 CacheSessionRegistry

```python
# src/josi/services/ai/cache_session_registry.py

class CacheSessionRegistry:
    """Redis-backed session state for cache-hit bookkeeping."""

    SESSION_TTL_SECONDS = 1800
    CACHE_EXPECTATION_WINDOW_SECONDS = 300  # matches Anthropic default ephemeral TTL

    def __init__(self, redis_client): ...

    async def load(self, session_id: str) -> SessionMeta | None: ...
    async def save(self, session_id: str, meta: SessionMeta) -> None: ...

    async def expect_cache_hit(
        self,
        session_id: str,
        chart_context_hash: str,
    ) -> bool:
        """True iff last_call_at < 300s ago AND chart_context_hash unchanged."""
        meta = await self.load(session_id)
        if not meta:
            return False
        if (now() - meta.last_call_at).total_seconds() > self.CACHE_EXPECTATION_WINDOW_SECONDS:
            return False
        return meta.chart_context_hash == chart_context_hash

    async def record_turn(
        self,
        session_id: str,
        *,
        anthropic_usage: dict,
        chart_context_hash: str,
    ) -> None:
        """Updates session meta from Anthropic's usage payload."""
        ...
```

### 5.6 CostEstimator

```python
# src/josi/services/ai/cost_estimator.py

class CostEstimator:
    """Projects + records per-turn cost using Anthropic usage payload as ground truth."""

    PRICES_USD_PER_MTOK = {
        # Placeholder; read from config to allow price updates without code change.
        "claude-haiku-4-5": {"input": 0.25, "output": 1.25,
                             "cache_write": 0.31, "cache_read": 0.025},
        "claude-sonnet-4-6": {"input": 3.0, "output": 15.0,
                              "cache_write": 3.75, "cache_read": 0.30},
        "claude-opus-4-7":   {"input": 15.0, "output": 75.0,
                              "cache_write": 18.75, "cache_read": 1.50},
    }

    def estimate_turn_cost(self, model: str, usage: dict) -> float: ...
    def record_metrics(self, model: str, usage: dict, hit: bool) -> None: ...
```

### 5.7 Model selector

```python
# src/josi/services/ai/model_selector.py

TIER_TO_MODEL = {
    "free":     "claude-haiku-4-5",
    "explorer": "claude-sonnet-4-6",
    "mystic":   "claude-sonnet-4-6",
    "master":   "claude-opus-4-7",
}

def model_for_user(user: User) -> str:
    return TIER_TO_MODEL.get(user.subscription_tier, "claude-sonnet-4-6")
```

### 5.8 Integration with AIInterpretationService

Existing `src/josi/services/ai/interpretation_service.py` wires prompt assembly directly to `self.anthropic_client.messages.create(...)`. We refactor so the orchestration layer (E11a) calls `MessageBuilder.build_request(...)` and passes the dict to `messages.create(**request)`. The existing `AIInterpretationService` retains a non-cached legacy path for the single-shot "chart interpretation" endpoint (not a conversation); new chat endpoint uses the cached path.

## 6. User Stories

### US-F12.1: As the system, consecutive turns in a chat session bill the prefix at ~10% of normal cost
**Acceptance:** Given 2 turns within 5 min on same chart: turn-2 Anthropic response `usage.cache_read_input_tokens > 0` and prefix cost estimate ~10% of turn-1.

### US-F12.2: As the system, a new session (different session_id, same chart) still benefits from the TOOLS cache
**Acceptance:** turn-1 of new session shows `usage.cache_read_input_tokens > 0` for the tools portion, even though chart context is fresh.

### US-F12.3: As the system, changing the chart (e.g., aggregation_event updates reading view) invalidates the cached context
**Acceptance:** chart_context_hash changes → `expect_cache_hit()` returns False → next turn writes new cache entry.

### US-F12.4: As ops, the cache hit rate dashboard is visible and updates live
**Acceptance:** Grafana dashboard shows hit rate gauge updating every 15s; panel for cost-per-session trend.

### US-F12.5: As a premium user, my chat uses Opus 4.7 with caching
**Acceptance:** `model_for_user` returns `claude-opus-4-7` for `subscription_tier='master'`; cache_control still applied; minimum-token floor ensures cacheability.

### US-F12.6: As a developer, chart context is always above the minimum cacheable size
**Acceptance:** `ChartContextBuilder.build()` output never returns fewer than `MIN_TOKEN_FLOOR` tokens; pad logic triggers for sparse charts.

### US-F12.7: As a security reviewer, cache does not cross tenants
**Acceptance:** two different `organization_id`s for the same `chart_id` (would be a data-isolation bug itself) would produce different chart contexts and thus different cache entries; assert via test.

### US-F12.8: As the chat backend, if Anthropic returns no cache metrics, we still function
**Acceptance:** missing `cache_read_input_tokens` in usage payload → treat as miss; no crash.

## 7. Tasks

### T-F12.1: `ChartContextBuilder`
- **Definition:** Build chart-context text block from `chart_reading_view`; produce hash + token count; enforce floor and cap.
- **Acceptance:** unit tests pass for rich, sparse, and missing-row cases; token count ≥ floor; hash deterministic.
- **Effort:** 1 day
- **Depends on:** F9 done

### T-F12.2: `MessageBuilder`
- **Definition:** Compose Anthropic messages payload with 2 cache_control markers.
- **Acceptance:** produced dict validates against Anthropic SDK types; cache_control present at exactly the right spots.
- **Effort:** 4 hours
- **Depends on:** T-F12.1, F10 tools spec

### T-F12.3: `CacheSessionRegistry`
- **Definition:** Redis-backed session tracker with `expect_cache_hit()` + `record_turn()`.
- **Acceptance:** unit tests with `fakeredis` cover TTL expiry, hash change, happy hit path.
- **Effort:** 4 hours
- **Depends on:** Redis client configured

### T-F12.4: `CostEstimator` + metrics
- **Definition:** Compute cost from `usage` payload; emit Prometheus metrics.
- **Acceptance:** metrics exposed on `/metrics`; cost numbers match hand-calculation on fixture.
- **Effort:** 4 hours
- **Depends on:** T-F12.2

### T-F12.5: `model_for_user` + tier mapping
- **Definition:** Simple function + fixture tests.
- **Acceptance:** each tier resolves to expected model.
- **Effort:** 1 hour
- **Depends on:** existing subscription tier enum

### T-F12.6: Integrate into AIInterpretationService + E11a
- **Definition:** New method `chat_turn(session_id, user_message, ...)` using MessageBuilder; legacy `generate_interpretation` left untouched.
- **Acceptance:** chat turn in integration test uses cache on second call; old endpoints unaffected.
- **Effort:** 1 day
- **Depends on:** T-F12.2, T-F12.3, T-F12.4

### T-F12.7: Grafana dashboard JSON
- **Definition:** `ops/dashboards/ai_chat_cache.json` with panels for hit rate, prefix size, cost trends.
- **Acceptance:** imports cleanly into Grafana dev instance.
- **Effort:** 2 hours
- **Depends on:** T-F12.4

### T-F12.8: Documentation
- **Definition:** `docs/markdown/ai-caching.md` section; `CLAUDE.md` paragraph under "AI layer".
- **Acceptance:** merged; links in INDEX.
- **Effort:** 2 hours
- **Depends on:** T-F12.6

## 8. Unit Tests

### 8.1 ChartContextBuilder

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_build_produces_floor_sized_output_for_sparse_chart` | reading view with 1 yoga and 1 dasa | token_count ≥ 2100 (floor) | floor padding works |
| `test_build_prunes_when_over_cap` | reading view with 150 active yogas | token_count ≤ 4000; pruning event logged | cap enforced |
| `test_build_hash_stable_across_runs` | same reading view | same hash on 2 calls | determinism |
| `test_build_hash_changes_on_yoga_change` | reading view A vs A with 1 yoga removed | different hashes | change detection |
| `test_build_for_missing_row_returns_placeholder` | no reading view | placeholder text + floor-sized output + marker "chart_context_v1_empty" | graceful path |
| `test_build_respects_audience_end_user` | reading view with reference source citations | no `jh`/`maitreya` raw ids appear | sanitization propagates via CitedFact from F11 |
| `test_build_short_form_citations` | citation "Brihat Parashara Hora Shastra Chapter 36..." | appears as "BPHS 36..." | compression applied |

### 8.2 MessageBuilder

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_cache_control_on_last_tool_only` | 5 tools | tool[4] has cache_control; tools[0..3] don't | breakpoint #1 correct |
| `test_cache_control_on_chart_context_block` | any input | first user message's chart_context text block has cache_control | breakpoint #2 correct |
| `test_system_prompt_cache_control_present` | any input | system block has cache_control | system block cached |
| `test_current_turn_has_no_cache_control` | any input | last user message has no cache_control | dynamic portion stays dynamic |
| `test_request_validates_against_sdk_types` | built request dict | passes `MessageCreateParams.model_validate(request)` | SDK compat |
| `test_history_preserved_between_first_and_current_turn` | history of 2 turns | resulting messages list has initial user + 2 history + current turn in order | order correctness |

### 8.3 CacheSessionRegistry

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_expect_hit_false_on_missing_session` | no session in Redis | False | first-turn miss |
| `test_expect_hit_true_within_window` | session saved 100s ago, same hash | True | happy hit |
| `test_expect_hit_false_after_expiry` | session saved 400s ago | False | TTL-expired miss |
| `test_expect_hit_false_on_hash_change` | session saved 100s ago, different hash | False | content-change miss |
| `test_record_turn_increments_counters` | record turn with `cache_read_input_tokens=1500` | `cache_hit_count += 1`; running totals updated | metrics aggregation |
| `test_session_ttl_set_to_30_min` | save session | `TTL` reports close to 1800s | bookkeeping TTL |

### 8.4 CostEstimator

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_estimate_turn_cost_cache_hit` | model=sonnet, usage with cache_read=1500, input=200, output=500 | matches hand-calc (cache_read @ $0.30/Mtok, etc.) | math correctness |
| `test_estimate_turn_cost_cache_write` | usage with cache_creation=2000 | write @ $3.75/Mtok for sonnet | write price applied |
| `test_estimate_turn_cost_unknown_model` | model='unknown' | fall back to sonnet defaults with WARN log | graceful |
| `test_metrics_emitted` | record a turn | `ai_chat_cache_hits_total` incremented | metric wiring |

### 8.5 Model selector

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_free_tier_maps_to_haiku` | user.tier=free | `claude-haiku-4-5` | tier map |
| `test_master_tier_maps_to_opus` | user.tier=master | `claude-opus-4-7` | premium mapping |
| `test_unknown_tier_defaults_to_sonnet` | user.tier=<unknown> | `claude-sonnet-4-6` | safe default |

### 8.6 Integration (mocked Anthropic)

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_two_consecutive_turns_second_is_hit` | mock Anthropic returning `cache_read_input_tokens=X` on turn 2 | session registry records `cache_hit_count=1`; cost estimate reflects ~10% prefix cost | end-to-end hit path |
| `test_chart_change_invalidates_cache` | reading view mutates between turns | second turn's `expect_cache_hit` returns False; next Anthropic response shows `cache_creation_input_tokens>0` | invalidation logic |
| `test_missing_usage_field_graceful` | mock response missing `cache_read_input_tokens` | no crash; recorded as miss | defensive |
| `test_tenant_isolation_cache_key` | two orgs with same chart_id | different chart contexts → different hashes → separate cache entries | isolation |

### 8.7 Cost projection vs actual

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_6turn_session_cost_reduction_estimate` | simulate 6-turn session with caching vs without | cached session costs ≤ 50% of non-cached | savings hypothesis validated |

## 9. EPIC-Level Acceptance Criteria

- [ ] `ChartContextBuilder` produces cacheable blocks (≥ floor, ≤ cap) for all reading view states (rich / sparse / empty)
- [ ] `MessageBuilder` places `cache_control` at exactly 2 breakpoints (tools end + chart context end) plus 1 on system block
- [ ] `CacheSessionRegistry` correctly predicts hit/miss from Redis state
- [ ] Anthropic `usage.cache_read_input_tokens` is used as ground truth for metric emission
- [ ] Grafana dashboard renders hit rate, prefix size, per-session cost
- [ ] Integration test shows turn-2 within 300s is served from cache (via mock verifying `cache_read_input_tokens > 0`)
- [ ] Integration test shows chart-context change invalidates cache
- [ ] Unit test coverage ≥ 90% on all new modules
- [ ] Cost projection test confirms ≥ 50% input cost reduction on 6-turn sessions
- [ ] Model selector routes by tier correctly
- [ ] Graceful handling when Anthropic usage payload lacks cache fields
- [ ] Tenant isolation verified (cache keys don't collide across orgs)
- [ ] `CLAUDE.md` updated with AI caching section; `docs/markdown/ai-caching.md` merged

## 10. Rollout Plan

- **Feature flag:** `AI_CHAT_PROMPT_CACHING_ENABLED` (default OFF until E11a orchestrator ready; flip ON in P1 behind 10% → 50% → 100% dial-up).
- **Shadow compute:** run cached and non-cached paths in parallel for 1% of sessions during first week of P1 enablement; compare response quality via user thumbs signals.
- **Backfill:** none (stateless; caches populate organically per session).
- **Rollback:** disable feature flag; all requests go to non-cached legacy path in `AIInterpretationService`. No data corruption possible. Anthropic's side caches evict naturally within 5 min.

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Chart context hovers just below minimum cacheable size → silent cache no-op | Medium | Medium | `MIN_TOKEN_FLOOR=2100` padding enforces cacheability; unit test asserts |
| Token counter drift vs Anthropic's counter | Medium | Low | Only an estimate for floor enforcement; Anthropic's `usage` is ground truth for cost |
| Hash collisions across charts | Very Low | Low | SHA-256 collision resistance more than sufficient |
| Cache TTL drift (Anthropic changes default) | Low | Medium | Track via `CACHE_EXPECTATION_WINDOW_SECONDS` constant; ops-tunable |
| Non-deterministic rendering of chart context (e.g., dict-order changes) | Medium | High | Explicit ordering in `ChartContextBuilder`; tests assert hash stability |
| Pruning removes information the LLM needs | Medium | Medium | Pruning order starts with least-relevant (inactive yogas, extra dasa systems); log pruning events; LLM can tool-call for missing info |
| 25% write surcharge negates savings for short sessions | Medium | Low | Monitor hit rate; if < 40% after 2 weeks, consider disabling for < 3-turn sessions |
| Anthropic deprecates ephemeral tier | Low | High | Abstract TTL tier via config; `ttl: "1h"` tier available as fallback |
| PII in chart context leaks via Anthropic cache | Low | Medium | Chart context contains birth data already shared with Anthropic for interpretation; no new exposure. Reviewed with privacy team. |
| Wrong model selected for Haiku 4.5 token floor | Low | Medium | Floor (2100) > Haiku minimum (512) → always safe |

## 12. References

- Master spec: [`docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`](../../../superpowers/specs/2026-04-19-classical-techniques-expansion-design.md) §3.3 (prompt caching)
- F9 reading view: [`F9-chart-reading-view-table.md`](./F9-chart-reading-view-table.md) — source of chart context
- F10 tool contracts: [`F10-typed-ai-tool-use-contract.md`](./F10-typed-ai-tool-use-contract.md) — stable tools list benefits from caching
- F11 citation envelope: [`F11-citation-embedded-responses.md`](./F11-citation-embedded-responses.md) — system-prompt fragment lives in cached block
- Anthropic prompt caching docs: https://docs.anthropic.com/claude/docs/prompt-caching
- Anthropic cache_control parameter reference: https://docs.anthropic.com/claude/reference/messages_post (see `cache_control`)
- Existing AI service: `src/josi/services/ai/interpretation_service.py`
- Anthropic SDK version: `anthropic = "^0.40.0"` pinned in `pyproject.toml`
- Grafana dashboard JSON format: https://grafana.com/docs/grafana/latest/dashboards/json-model/
