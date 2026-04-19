---
prd_id: F10
epic_id: F10
title: "Typed AI tool-use contract (Pydantic + Anthropic tool-use spec)"
phase: P0-foundation
tags: [#ai-chat, #correctness, #extensibility]
priority: must
depends_on: [F8, F9]
enables: [F11, F12, E11a, E11b]
classical_sources: []
estimated_effort: 1 week
status: draft
author: @agent
last_updated: 2026-04-19
---

# F10 — Typed AI Tool-Use Contract (Pydantic + Claude)

## 1. Purpose & Rationale

Josi's differentiator is not that we call an LLM — it's that the LLM retrieves classical-technique results that carry **source authority**, **citations**, **confidence**, and **cross-source agreement**. Achieving this at runtime requires the LLM to be able to *fetch* those results on demand rather than have them all jammed into a monolithic prompt.

Anthropic's tool-use (function calling) is the right primitive, but naive tool definitions drift over time: response shapes change silently, new fields leak in, downstream parsers break. This PRD establishes a **contract layer** where:

1. Every tool has a Pydantic response model with stable additive shape.
2. Every tool is declared in the Anthropic tool-use `tools=[...]` spec with a JSON Schema derived from the Pydantic model.
3. Every tool implementation reads from `chart_reading_view` (F9) on the fast path, with a slow-path fallback to `aggregation_event`.
4. Tool authorization is enforced (chart ownership via `organization_id`, user context for astrologer preferences).
5. "Computing" is a first-class response — if a technique has not yet been aggregated, the tool returns `{status: "computing", estimated_ms: X}` and triggers compute if not already in progress.

The payoff: the chat orchestration layer (E11a) becomes thin; the classical-technique retrieval is provably typed; and we gain Anthropic prompt caching (F12) for free because tool definitions are stable.

## 2. Scope

### 2.1 In scope
- **Tool catalog (P0 initial set):**
  - `get_yoga_summary`
  - `get_current_dasa`
  - `get_transit_events`
  - `get_tajaka_summary`
  - `get_jaimini_summary`
  - `get_ashtakavarga_summary`
  - `find_similar_charts`
  - `get_astrologer_preferences`
- Pydantic response models with Anthropic-readable `Field(description=...)` annotations
- Anthropic tool-use spec generator (`tools=[...]` list at runtime)
- Tool dispatch layer (`ToolExecutor`) with per-tool authorization
- "Computing" status response + compute-trigger hook
- Per-session rate limiting
- Multi-tenant isolation (every tool resolves `organization_id` + user)
- Contract-stability tests (snapshot Pydantic schemas into `tests/snapshots/ai_tools/` and fail on breaking changes)
- Anthropic SDK integration in `src/josi/services/ai/`

### 2.2 Out of scope
- The Claude chat orchestration loop itself (E11a)
- Debate-mode / Ultra AI (E11b)
- Prompt caching (F12, consumes this layer's stable tool defs)
- Embedding-based similarity implementation (E11b; this PRD declares the `find_similar_charts` contract only)
- Streaming tool results (future)
- OpenAI tool-use compatibility (we ship Claude-first at P0; OpenAI fallback is P1)

### 2.3 Dependencies
- F8 (aggregation events are the source of truth)
- F9 (`chart_reading_view` is the fast read path)
- Existing `anthropic.AsyncAnthropic` client (already in `src/josi/services/ai/interpretation_service.py`)
- `Organization`, `User`, `AstrologyChart` models
- Redis (for rate limit + per-session compute dedup)

## 3. Technical Research

### 3.1 Anthropic tool-use format

Anthropic's tool spec is JSON Schema based (draft 2020-12 subset). Every tool declares:

```json
{
  "name": "get_yoga_summary",
  "description": "Returns the list of active yogas for a chart ...",
  "input_schema": {
    "type": "object",
    "properties": { ... },
    "required": [...]
  }
}
```

The assistant (Claude) returns a `tool_use` content block in its response; our code executes the tool, posts a `tool_result` back in a subsequent user message, and Claude continues. We follow this exact pattern — no custom wrapper, no third-party router.

### 3.2 Why Pydantic for response shapes

Input schemas are supplied to Claude (helps Claude fill params correctly). Output schemas are enforced on our side (ensures Claude never sees a shape that changes across rule versions). Pydantic gives us:

- `model_json_schema()` → derives Anthropic-compatible input_schema
- Validation on construction (tool implementation cannot return malformed data)
- `Field(description=...)` shows up in the Anthropic-facing schema, so Claude reads field meanings
- Additive-only evolution rules (new fields must have defaults) become code-enforceable

### 3.3 Contract stability contract

We commit to:
- **Never rename a field.** Renames break downstream parsers and caches.
- **Never remove a field.** Deprecation takes a full major version.
- **New fields always have defaults.** So old clients (cached Claude responses) still parse.
- **Enum values are append-only.**
- **Response shape is independent of rule-engine version.** If a rule changes meaning, the value changes, not the field name.

Enforcement: JSON schemas of each response model are snapshotted in `tests/snapshots/ai_tools/<tool_name>.json`. CI fails on any non-additive change.

### 3.4 Fast vs slow path

| Path | Source | Latency | Coverage |
|---|---|---|---|
| Fast | `chart_reading_view` (F9) | P99 < 10ms | All charts with at least 1 aggregation_event |
| Slow | `aggregation_event` direct query + on-the-fly projection | P99 < 200ms | Fallback for corner cases |
| Computing | No data yet | N/A | Triggers compute; returns placeholder |

Tool implementations try fast path first. If the reading view row is absent OR the relevant JSONB key is `null`, fall back to slow path. If the slow path also has no rows, return `status: "computing"`.

### 3.5 "Computing" response

Every Pydantic response model is wrapped in a discriminated union:

```python
class ComputingResponse(BaseModel):
    status: Literal["computing"] = "computing"
    estimated_ms: int = Field(description="Rough ETA in milliseconds before results are available.")
    compute_triggered: bool = Field(description="Whether this call enqueued a compute job.")

ToolResponse = Annotated[
    ResultResponse | ComputingResponse,
    Field(discriminator="status"),
]
```

Claude is prompted (in the system prompt) to handle `status=="computing"` gracefully ("The reading is still being computed. Here's what I can share so far…"). The UI layer reads the same shape and decides whether to poll or show a spinner.

### 3.6 Authorization model

Every tool resolves `chart_id` → `(organization_id, owner_user_id)` at dispatch time and checks:
1. The calling user belongs to `organization_id`.
2. Either the user owns the chart (`chart.owner_user_id == caller.user_id`) **or** the caller has astrologer access via `astrologer_chart_access` (existing model).
3. `get_astrologer_preferences` only returns preferences for the caller's own user_id.

Failures return `{"error": "unauthorized"}` without leaking chart existence.

### 3.7 Rate limiting

Per-session (Redis key `ai_tools:session:{session_id}`): 60 tool calls per minute, 600 per hour. Enforced via `slowapi` + existing Redis client. Exceeding limit returns `{"error": "rate_limited", "retry_after_seconds": N}`.

### 3.8 Alternatives considered

| Alternative | Rejected because |
|---|---|
| Dump full reading view in the system prompt, no tools | Bloats context, can't cache, loses type structure, defeats tool-use |
| Free-form JSON responses from tools | Loses compile-time safety and drift detection |
| LangChain / LlamaIndex abstraction | Adds a dependency; we only call one model family; direct Anthropic SDK is cleaner |
| Make tools return raw aggregation_event.output | Couples AI to internal storage shape; breaks on F9 schema evolution |
| One mega-tool `get_chart_context` returning everything | Defeats partial retrieval; blows cache budget; forces LLM to digest irrelevant fields |

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| Pydantic v1 vs v2 | v2 (already in use per CLAUDE.md) | Existing stack; better JSON Schema generator |
| Discriminated union for computing vs result | Yes | Type-safe handling of "not ready" state |
| Where to generate tool JSON schemas | At app startup, cached | No per-request cost; deterministic |
| Tool call auth granularity | Per-tool (declarative decorators) | Explicit, auditable |
| Rate-limit key | `session_id` if present, else `user_id` | Correct granularity for chat sessions |
| Compute-trigger mechanism on "computing" | Enqueue via existing Celery/workflow layer (S5 later; P0 uses direct coroutine) | P0 doesn't need durable workflow |
| Should tools stream | No at P0 | Complicates contract; Claude tool_result is atomic anyway |
| OpenAI compat at P0 | No | Focus; revisit P1 |
| Claude model | `claude-opus-4-7` for premium, `claude-sonnet-4-6` default | Matches subscription tier mapping (F12) |
| Tool-use system prompt owner | F10 publishes a fragment; E11a composes final | Separation of concerns |

## 5. Component Design

### 5.1 New modules

```
src/josi/services/ai/
├── tool_contracts.py              # Pydantic response models for every tool
├── tool_spec_generator.py         # Builds Anthropic tools=[...] list at startup
├── tool_executor.py               # ToolExecutor: dispatch, auth, fast/slow path
├── tool_rate_limit.py             # per-session rate limiter
├── tool_registry.py               # decorator + registry of (name, fn, schema)
└── compute_triggers.py            # hooks to enqueue compute when "computing" status

src/josi/schemas/ai/
└── cited_fact.py                  # re-export from F11 (imported here for typing)

tests/snapshots/ai_tools/
├── get_yoga_summary.json
├── get_current_dasa.json
├── get_transit_events.json
├── get_tajaka_summary.json
├── get_jaimini_summary.json
├── get_ashtakavarga_summary.json
├── find_similar_charts.json
└── get_astrologer_preferences.json
```

### 5.2 Pydantic response models

```python
# src/josi/services/ai/tool_contracts.py

from datetime import datetime, date
from typing import Annotated, Literal
from uuid import UUID
from pydantic import BaseModel, Field

from josi.schemas.ai.cited_fact import CitedFact  # from F11


# ---------- Generic wrappers ----------

class ComputingResponse(BaseModel):
    status: Literal["computing"] = "computing"
    estimated_ms: int = Field(description="Rough ETA in ms before results ready.")
    compute_triggered: bool = Field(description="True iff this call enqueued new compute.")


class ToolError(BaseModel):
    status: Literal["error"] = "error"
    code: Literal["unauthorized", "not_found", "rate_limited", "internal_error"]
    message: str
    retry_after_seconds: int | None = None


# ---------- get_yoga_summary ----------

class YogaEntry(BaseModel):
    yoga_id: str = Field(description="Stable internal id, e.g., 'raja.gaja_kesari'.")
    display_name: str = Field(description="Human-readable name.")
    active: CitedFact[bool] = Field(description="Whether the yoga is active, with citation.")
    strength: CitedFact[float] = Field(description="Strength 0..1, with citation.")
    classical_names: dict[str, str] = Field(
        description="Names keyed by language (en, sa_iast, sa_devanagari, ta)."
    )


class YogaSummary(BaseModel):
    status: Literal["ok"] = "ok"
    chart_id: UUID
    strategy_applied: str = Field(description="Aggregation strategy id, e.g., 'D_hybrid'.")
    yogas: list[YogaEntry]
    total_active: int
    generated_at: datetime


GetYogaSummaryResponse = Annotated[
    YogaSummary | ComputingResponse | ToolError,
    Field(discriminator="status"),
]


# ---------- get_current_dasa ----------

class DasaLevel(BaseModel):
    level: int = Field(ge=1, le=5, description="1=Mahadasa, 2=Antardasa, ...")
    lord: str = Field(description="Planet or nakshatra lord.")
    start: datetime
    end: datetime


class DasaPeriod(BaseModel):
    status: Literal["ok"] = "ok"
    chart_id: UUID
    system: str = Field(description="Dasa system: 'vimshottari', 'yogini', 'ashtottari', ...")
    level: int = Field(description="Deepest level returned.")
    levels: list[DasaLevel]
    source: CitedFact[str] = Field(description="Source authority for this system.")


GetCurrentDasaResponse = Annotated[
    DasaPeriod | ComputingResponse | ToolError,
    Field(discriminator="status"),
]


# ---------- get_transit_events ----------

class TransitEvent(BaseModel):
    event_type: str = Field(description="e.g., 'sade_sati_start', 'jupiter_sign_change'.")
    at: datetime
    planet: str | None
    details: dict = Field(default_factory=dict)
    importance: Literal["minor", "major", "watershed"]
    citation: str | None


class TransitEvents(BaseModel):
    status: Literal["ok"] = "ok"
    chart_id: UUID
    date_range_start: date
    date_range_end: date
    events: list[TransitEvent]


GetTransitEventsResponse = Annotated[
    TransitEvents | ComputingResponse | ToolError,
    Field(discriminator="status"),
]


# ---------- get_tajaka_summary ----------

class TajakaSummary(BaseModel):
    status: Literal["ok"] = "ok"
    chart_id: UUID
    year: int
    muntha_sign: CitedFact[str]
    year_lord: CitedFact[str]
    active_sahams: list[CitedFact[str]]
    varsha_phala_notes: list[CitedFact[str]]


GetTajakaSummaryResponse = Annotated[
    TajakaSummary | ComputingResponse | ToolError,
    Field(discriminator="status"),
]


# ---------- get_jaimini_summary ----------

class CharaKaraka(BaseModel):
    role: str = Field(description="Atmakaraka | Amatyakaraka | Bhratrikaraka | ... | Dara")
    planet: str
    longitude_deg: float


class JaiminiSummary(BaseModel):
    status: Literal["ok"] = "ok"
    chart_id: UUID
    chara_karakas: list[CharaKaraka]
    arudha_lagna: CitedFact[str]
    jaimini_yogas_active: list[CitedFact[str]]


GetJaiminiSummaryResponse = Annotated[
    JaiminiSummary | ComputingResponse | ToolError,
    Field(discriminator="status"),
]


# ---------- get_ashtakavarga_summary ----------

class AshtakavargaSummary(BaseModel):
    status: Literal["ok"] = "ok"
    chart_id: UUID
    sarvashtakavarga: list[int] = Field(description="12 sign totals; sum over 8 contributors.")
    bhinnashtakavarga: dict[str, list[int]] = Field(
        description="Per-planet 12-sign bindu arrays."
    )
    transit_bindu: dict[str, int] = Field(
        description="Current transit bindu per planet at now()."
    )
    notes: list[CitedFact[str]]


GetAshtakavargaSummaryResponse = Annotated[
    AshtakavargaSummary | ComputingResponse | ToolError,
    Field(discriminator="status"),
]


# ---------- find_similar_charts ----------

class SimilarChart(BaseModel):
    chart_id: UUID
    similarity_score: float = Field(ge=0, le=1)
    matched_technique_family: str
    matched_features: list[str]


class SimilarCharts(BaseModel):
    status: Literal["ok"] = "ok"
    query_chart_id: UUID
    technique_family: str
    results: list[SimilarChart]


FindSimilarChartsResponse = Annotated[
    SimilarCharts | ComputingResponse | ToolError,
    Field(discriminator="status"),
]


# ---------- get_astrologer_preferences ----------

class FamilyPreference(BaseModel):
    technique_family_id: str
    source_weights: dict[str, float]
    preferred_strategy_id: str | None
    preference_mode: Literal["auto", "custom", "ultra"]


class AstrologerPreferences(BaseModel):
    status: Literal["ok"] = "ok"
    user_id: UUID
    preferences: list[FamilyPreference]


GetAstrologerPreferencesResponse = Annotated[
    AstrologerPreferences | ToolError,
    Field(discriminator="status"),
]
```

### 5.3 Tool registry + decorator

```python
# src/josi/services/ai/tool_registry.py

from dataclasses import dataclass
from typing import Callable, Any, Awaitable
from pydantic import BaseModel

@dataclass(frozen=True)
class RegisteredTool:
    name: str
    description: str
    input_model: type[BaseModel]
    output_model: type[BaseModel]        # the Annotated union type
    handler: Callable[..., Awaitable[BaseModel]]
    requires_chart_access: bool
    requires_user_context: bool
    rate_limit_cost: int = 1             # some tools are heavier

_REGISTRY: dict[str, RegisteredTool] = {}


def ai_tool(
    name: str,
    description: str,
    input_model: type[BaseModel],
    output_model: type[BaseModel],
    *,
    requires_chart_access: bool = True,
    requires_user_context: bool = False,
    rate_limit_cost: int = 1,
):
    def decorator(fn):
        _REGISTRY[name] = RegisteredTool(
            name=name, description=description,
            input_model=input_model, output_model=output_model,
            handler=fn,
            requires_chart_access=requires_chart_access,
            requires_user_context=requires_user_context,
            rate_limit_cost=rate_limit_cost,
        )
        return fn
    return decorator


def all_tools() -> list[RegisteredTool]:
    return list(_REGISTRY.values())
```

### 5.4 Anthropic tool-spec generator

```python
# src/josi/services/ai/tool_spec_generator.py

def build_anthropic_tools() -> list[dict]:
    """Build the tools=[...] list for Anthropic API calls.

    Called once at app startup; result cached.
    """
    out = []
    for t in all_tools():
        out.append({
            "name": t.name,
            "description": t.description,
            "input_schema": t.input_model.model_json_schema(),
        })
    return out
```

### 5.5 Tool executor (dispatch + auth + rate limit)

```python
# src/josi/services/ai/tool_executor.py

class ToolExecutor:
    def __init__(
        self,
        session_factory: Callable[[], AsyncSession],
        reading_view_repo: ChartReadingViewRepository,
        rate_limiter: ToolRateLimiter,
    ): ...

    async def execute(
        self,
        tool_name: str,
        arguments: dict,
        *,
        caller_user_id: UUID,
        caller_organization_id: UUID,
        session_id: str | None = None,
    ) -> BaseModel:
        """Dispatch tool call: validate args, auth, rate limit, call handler.

        Returns a Pydantic model (one of the discriminated union members).
        Never raises — all errors are returned as ToolError.
        """
        tool = _REGISTRY.get(tool_name)
        if tool is None:
            return ToolError(code="not_found", message=f"Unknown tool: {tool_name}")

        # 1. Rate limit
        if not await self.rate_limiter.check(session_id or str(caller_user_id), tool.rate_limit_cost):
            return ToolError(code="rate_limited", message="Tool call budget exceeded",
                             retry_after_seconds=60)

        # 2. Validate input
        try:
            args = tool.input_model.model_validate(arguments)
        except ValidationError as e:
            return ToolError(code="internal_error", message=f"Invalid arguments: {e}")

        # 3. Auth (chart access / user context)
        if tool.requires_chart_access:
            chart_id = getattr(args, "chart_id", None)
            if not await self._has_chart_access(caller_user_id, caller_organization_id, chart_id):
                return ToolError(code="unauthorized", message="No access to this chart.")

        # 4. Dispatch
        try:
            return await tool.handler(args, caller_user_id=caller_user_id,
                                      caller_organization_id=caller_organization_id,
                                      session_factory=self.session_factory,
                                      reading_view_repo=self.reading_view_repo)
        except Exception as e:
            logger.exception("tool_handler_error", tool=tool_name)
            return ToolError(code="internal_error", message="Internal error.")
```

### 5.6 Example handler (get_yoga_summary)

```python
# src/josi/services/ai/handlers/yoga_handler.py

class GetYogaSummaryInput(BaseModel):
    chart_id: UUID
    strategy: str = "D_hybrid"
    min_confidence: float = Field(default=0.0, ge=0, le=1)
    limit: int = Field(default=50, ge=1, le=200)


@ai_tool(
    name="get_yoga_summary",
    description=(
        "Returns the list of active classical yogas for a chart with source citations "
        "and confidence scores. Use when the user asks about yogas, spiritual patterns, "
        "or combinations in their chart."
    ),
    input_model=GetYogaSummaryInput,
    output_model=GetYogaSummaryResponse,  # Annotated union
)
async def get_yoga_summary_handler(
    args: GetYogaSummaryInput,
    *,
    caller_user_id: UUID,
    caller_organization_id: UUID,
    session_factory,
    reading_view_repo: ChartReadingViewRepository,
) -> BaseModel:
    # Fast path: reading view
    row = await reading_view_repo.get_by_chart_id(args.chart_id, caller_organization_id)
    if row is None:
        triggered = await trigger_compute_if_absent(args.chart_id, family="yoga")
        return ComputingResponse(estimated_ms=5000, compute_triggered=triggered)

    yogas = [YogaEntry.model_validate(y) for y in (row.active_yogas or [])]
    yogas = [y for y in yogas if y.strength.value >= args.min_confidence][: args.limit]

    return YogaSummary(
        chart_id=args.chart_id,
        strategy_applied=row.strategy_applied,
        yogas=yogas,
        total_active=len([y for y in yogas if y.active.value]),
        generated_at=row.last_computed_at or row.created_at,
    )
```

### 5.7 Compute trigger hook

```python
# src/josi/services/ai/compute_triggers.py

async def trigger_compute_if_absent(chart_id: UUID, family: str) -> bool:
    """Enqueue compute for (chart, family) unless already in-flight.
    Returns True if newly triggered, False if already queued.
    """
    key = f"compute_in_flight:{chart_id}:{family}"
    if await redis.setnx(key, "1"):
        await redis.expire(key, 300)
        await enqueue_compute_task(chart_id, family)  # existing queue (or direct coroutine at P0)
        return True
    return False
```

## 6. User Stories

### US-F10.1: As the chat orchestration layer, I can pass the current `tools=[...]` list to Claude and expect it to be usable verbatim
**Acceptance:** `build_anthropic_tools()` returns a list that Anthropic's `messages.create(..., tools=...)` accepts without error.

### US-F10.2: As a user asking "what yogas do I have", Claude calls `get_yoga_summary` and receives a typed response
**Acceptance:** given a chart with computed yogas, the tool returns a `YogaSummary` with populated `yogas` list; Claude's response cites at least one yoga by name.

### US-F10.3: As a user asking about a chart that has not been computed yet, I get a graceful "computing" message
**Acceptance:** tool returns `ComputingResponse`; Claude's user-facing message reads like "Your chart is still being computed; here's what I can share so far."

### US-F10.4: As an attacker, I cannot retrieve data for a chart I do not own
**Acceptance:** tool returns `ToolError(code='unauthorized')` when `caller_user_id` does not have access to `chart_id`; no difference in response between "chart not found" and "chart not yours" (no enumeration leak).

### US-F10.5: As an astrologer, `get_astrologer_preferences` returns only my own preferences
**Acceptance:** passing a `user_id` that isn't mine returns `ToolError(code='unauthorized')`.

### US-F10.6: As an abuser, I cannot spam tool calls within a session
**Acceptance:** after 60 calls in 1 minute for a session, subsequent calls return `ToolError(code='rate_limited', retry_after_seconds=N)`.

### US-F10.7: As a backend engineer, a breaking change to a tool response shape fails CI
**Acceptance:** removing a field or changing a type in `YogaSummary` triggers a snapshot-mismatch test failure in `tests/snapshots/ai_tools/`.

### US-F10.8: As an engineer, I can add a new tool without touching the orchestration loop
**Acceptance:** `@ai_tool` decorator on a new async fn is sufficient to make it discoverable by `build_anthropic_tools()`.

## 7. Tasks

### T-F10.1: Pydantic response models for all 8 tools
- **Definition:** Write `tool_contracts.py` with every model above; each field has a `Field(description=...)`.
- **Acceptance:** `model_json_schema()` yields clean JSON Schema for each; discriminated unions validate correctly.
- **Effort:** 1 day
- **Depends on:** F11 contract decision (CitedFact shape — parallel)

### T-F10.2: Tool registry + decorator
- **Definition:** `@ai_tool` + `_REGISTRY` + `all_tools()`.
- **Acceptance:** decorating a fn registers it; double registration raises at import time.
- **Effort:** 3 hours
- **Depends on:** T-F10.1

### T-F10.3: Anthropic tool-spec generator
- **Definition:** `build_anthropic_tools()` returning Anthropic-accepted dicts.
- **Acceptance:** generated dicts pass Anthropic SDK type check (verified via `anthropic.types.ToolParam.model_validate`).
- **Effort:** 3 hours
- **Depends on:** T-F10.2

### T-F10.4: Handler implementations (all 8 tools)
- **Definition:** Fast-path (reading_view) + slow-path (aggregation_event fallback) + computing-status logic for each.
- **Acceptance:** unit tests pass for each; integration test with a seeded chart returns realistic data.
- **Effort:** 2 days
- **Depends on:** T-F10.1, F9 done

### T-F10.5: ToolExecutor with auth + rate limit
- **Definition:** `ToolExecutor.execute` dispatches, checks auth, rate-limits.
- **Acceptance:** all security tests pass; rate-limit surface works.
- **Effort:** 1 day
- **Depends on:** T-F10.2, T-F10.4

### T-F10.6: Compute-trigger hook
- **Definition:** `trigger_compute_if_absent` using Redis SETNX dedup.
- **Acceptance:** concurrent calls produce only 1 compute job.
- **Effort:** 4 hours
- **Depends on:** T-F10.4

### T-F10.7: Snapshot tests for contract stability
- **Definition:** Write snapshots of all 8 tool JSON schemas into `tests/snapshots/ai_tools/`; fail-on-diff test.
- **Acceptance:** CI fails when schema changes non-additively; explicit `--update-snapshots` regenerates.
- **Effort:** 4 hours
- **Depends on:** T-F10.3

### T-F10.8: Integration test end-to-end
- **Definition:** Seeded chart → Claude request with tools → mock Anthropic response triggering tool call → ToolExecutor → typed response.
- **Acceptance:** full loop works with Anthropic test fixtures.
- **Effort:** 1 day
- **Depends on:** T-F10.5

### T-F10.9: Documentation
- **Definition:** `docs/markdown/ai-tools.md` listing every tool, description, input/output shape. Plus `CLAUDE.md` section "AI Tool Contracts (F10)".
- **Acceptance:** docs merged and link from `CLAUDE.md`.
- **Effort:** 4 hours
- **Depends on:** T-F10.7

## 8. Unit Tests

### 8.1 Pydantic model shapes

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_yoga_summary_validates` | valid dict with yoga entries | `YogaSummary` instance, no errors | model correctness |
| `test_computing_response_discriminator` | `{"status":"computing","estimated_ms":5000}` | parses into `ComputingResponse` | discriminated union works |
| `test_cited_fact_roundtrip_in_yoga_entry` | YogaEntry with CitedFact | `.model_dump()` → `.model_validate(...)` equal | nested generic works |
| `test_all_fields_have_description` | walk every model's fields | every `FieldInfo.description` non-empty | Claude needs descriptions |
| `test_response_union_discriminator_rejects_missing_status` | `{}` (no status) | `ValidationError` | union needs discriminator |

### 8.2 Tool registry

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_decorator_registers_tool` | `@ai_tool(...)` on fn | `all_tools()` includes it | registration works |
| `test_duplicate_registration_raises` | register same name twice | `ValueError` at import | catches typos |
| `test_all_p0_tools_registered` | startup of app | 8 registered tools | coverage check |

### 8.3 Anthropic spec generator

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_spec_is_accepted_by_sdk` | `build_anthropic_tools()` | each dict validates against `anthropic.types.ToolParam` | SDK compatibility |
| `test_spec_input_schema_is_valid_json_schema` | each tool's input_schema | passes `jsonschema.Draft202012Validator.check_schema` | JSON Schema validity |
| `test_spec_descriptions_nonempty` | each tool | `description` > 20 chars | helps Claude pick tool |

### 8.4 Handler: get_yoga_summary

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_yoga_handler_fast_path` | reading_view row with 3 active yogas | `YogaSummary` with 3 entries | happy path |
| `test_yoga_handler_computing_when_no_row` | no reading_view row | `ComputingResponse` | lazy state |
| `test_yoga_handler_respects_min_confidence` | row with yogas of strengths [0.3, 0.7, 0.9], min_confidence=0.5 | returns 2 entries | filter works |
| `test_yoga_handler_limit` | 100 yogas, limit=10 | returns 10 | limit works |
| `test_yoga_handler_wrong_tenant_returns_unauthorized` | chart in org A, caller org B | `ToolError(unauthorized)` | tenant isolation |

### 8.5 Handler: get_current_dasa

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_dasa_handler_returns_vimshottari_default` | chart with computed dasas | `DasaPeriod(system='vimshottari')` | default system |
| `test_dasa_handler_level_cap` | level=10 requested | clamps to max supported (5) | input validation |
| `test_dasa_handler_unknown_system` | system='nonsense' | `ToolError(not_found)` | graceful failure |

### 8.6 Handler: get_transit_events

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_transit_handler_date_range_filter` | date_range: 2026-01-01 to 2026-06-30 | only events in range | filtering correct |
| `test_transit_handler_importance_filter` | importance='major' | no 'minor' events | filter correct |

### 8.7 Handler: get_astrologer_preferences

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_prefs_only_returns_own_prefs` | user_id matches caller | returns prefs | owner path |
| `test_prefs_other_user_unauthorized` | user_id different from caller | `ToolError(unauthorized)` | privacy |

### 8.8 ToolExecutor — auth + rate limit

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_executor_unknown_tool` | tool_name='made_up' | `ToolError(not_found)` | graceful |
| `test_executor_invalid_args` | missing chart_id | `ToolError(internal_error)` with details | input validation surfaces |
| `test_executor_rate_limit` | 61 calls in 1 min | 61st returns `rate_limited` | rate limiter works |
| `test_executor_handler_exception_wrapped` | handler raises | `ToolError(internal_error)` | never leak exceptions |
| `test_executor_auth_denied_charted` | caller has no access | `ToolError(unauthorized)` | auth enforced |
| `test_executor_auth_denied_response_indistinguishable_from_notfound` | chart exists but not mine vs chart doesn't exist | same error shape | no enumeration leak |

### 8.9 Compute triggers

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_trigger_compute_sets_redis_flag` | first call for (chart,family) | `compute_in_flight` key set | dedup works |
| `test_trigger_compute_dedupes` | second call before expiry | returns False, no extra enqueue | dedup correctness |
| `test_trigger_compute_reenqueues_after_ttl` | call → wait 301s (mocked) → call | second returns True | expiry works |

### 8.10 Snapshot / contract stability

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_snapshot_match_all_tools` | generated JSON schemas vs stored snapshots | all match | stability enforced |
| `test_additive_field_passes` | add field with default to a model | snapshot diff test passes in "additive" mode | non-breaking change |
| `test_removing_field_fails` | remove a field | snapshot test fails | breaking change caught |

## 9. EPIC-Level Acceptance Criteria

- [ ] All 8 Pydantic response models defined with Field descriptions
- [ ] `@ai_tool` decorator + registry work for all 8 tools
- [ ] `build_anthropic_tools()` returns SDK-accepted list
- [ ] Each tool has a handler that returns typed response (fast/slow/computing paths)
- [ ] `ToolExecutor.execute` dispatches, authorizes, rate-limits correctly
- [ ] Multi-tenant isolation: all tests for cross-tenant access return `unauthorized` with no enumeration leak
- [ ] JSON schema snapshots committed; CI fails on breaking changes
- [ ] Integration test: real Anthropic SDK call (against test endpoint or mock) with tools; full loop works
- [ ] Unit test coverage ≥ 90% for tool_executor, tool_contracts, handlers
- [ ] Rate limiter tested with Redis up and Redis down (graceful degradation: fail open but log)
- [ ] Documentation: `docs/markdown/ai-tools.md` generated or hand-written listing all tools
- [ ] `CLAUDE.md` updated with "AI Tool Contracts (F10)" section

## 10. Rollout Plan

- **Feature flag:** `AI_TOOL_USE_ENABLED` (default OFF until E11a wires the chat loop; ON in P1).
- **Shadow compute:** N/A — contract layer, no computation of its own.
- **Backfill:** None (stateless).
- **Rollback:** Disable flag; chat falls back to non-tool-use prompt (existing `AIInterpretationService` path). No data corruption possible.

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Pydantic schema drift silently breaks downstream | Medium | High | Snapshot tests (T-F10.7) enforced in CI |
| Claude calls a tool we didn't define | Low | Low | Executor returns `not_found`; Claude recovers |
| "Computing" status livelocks (tool keeps returning computing, Claude keeps polling) | Medium | Medium | Per-session cap on consecutive `computing` calls = 3; then fall through to "try again later" prose |
| Redis down → rate limiter fails | Low | Medium | Fail open (allow call) + log alert |
| New rule changes yoga output shape | Medium | High | Response-shape stability (F10) is independent of rule logic: values change, shape doesn't |
| Anthropic SDK version upgrade breaks tool spec | Low | Medium | Pin version; test matrix; schema validator against `anthropic.types.ToolParam` |
| Handler leaks PII in error messages | Medium | High | `ToolError.message` sanitization (no user input echoed); structured logs only carry ids |
| Adding OpenAI backend later requires schema translation | Medium | Low | JSON Schema is universal; OpenAI tool-use format is trivially derivable |
| Enumeration via error shape | Medium | High | Tests verify `unauthorized` and `not_found` produce identical response envelope |

## 12. References

- Master spec: [`docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`](../../../superpowers/specs/2026-04-19-classical-techniques-expansion-design.md) §3.1 (tool-use contract)
- F9 reading view: [`F9-chart-reading-view-table.md`](./F9-chart-reading-view-table.md) — primary data source for handlers
- F11 citation-embedded responses: [`F11-citation-embedded-responses.md`](./F11-citation-embedded-responses.md) — `CitedFact[T]` used throughout
- F12 prompt caching: [`F12-prompt-caching-claude.md`](./F12-prompt-caching-claude.md) — consumes stable tool specs from this PRD
- Anthropic tool-use docs: https://docs.anthropic.com/claude/docs/tool-use
- Anthropic SDK: `anthropic` package (already used in `src/josi/services/ai/interpretation_service.py`)
- Existing AI service: `src/josi/services/ai/interpretation_service.py`
