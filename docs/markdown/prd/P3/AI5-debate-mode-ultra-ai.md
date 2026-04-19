---
prd_id: AI5
epic_id: AI5
title: "Debate-mode Ultra AI (shows strategy disagreement with confidence-aware synthesis)"
phase: P3-scale-10m
tags: [#ai-chat, #end-user-ux, #experimentation]
priority: could
depends_on: [E11b, S3, S6, F8]
enables: []
classical_sources: []
estimated_effort: 3 weeks
status: draft
author: Govind
last_updated: 2026-04-19
---

# AI5 — Debate-Mode Ultra AI

## 1. Purpose & Rationale

Josi's aggregation strategies (F8) produce four possible answers per technique: A (simple majority), B (confidence-weighted), C (source-weighted with astrologer preferences), D (hybrid default). In the default AI chat flow (E11a/E11b), we surface only one — typically D, flattened to a single best-guess with confidence. That's correct for ~95% of user questions.

For **depth users** — spiritual practitioners, advanced astrology enthusiasts, paying Mystic+ tier subscribers — the flattened answer hides something interesting: **when strategies disagree, why do they disagree?** Different sources, different weights, different epistemologies. Seeing the disagreement is often *more* valuable than the consensus — it surfaces genuine classical ambiguity rather than false precision.

**Debate Mode** (premium feature on Mystic and Master tiers) makes the LLM:

1. Consult all 4 aggregation strategy outputs separately (not flattened).
2. Internally "debate" — produce a structured breakdown: "Strategy B says X with 0.7 confidence. Strategy C with your source weights says Y. Strategy A says X by majority."
3. Synthesize a **confidence-aware answer** that acknowledges disagreement explicitly.
4. Surface UI affordance: expandable "Why does this answer vary?" section showing the per-strategy breakdown.

This requires: new AI tool-use shapes that return multi-strategy data, a Claude prompt scaffold that elicits internal debate, a UI component that renders the expansion, and a pricing-tier gate.

Ultra AI mode as defined in master spec §3.4 is premium. AI5 operationalizes it.

## 2. Scope

### 2.1 In scope
- New tool-use shape: `get_multi_strategy_summary(chart_id, technique_family)` — returns all 4 strategies' outputs + metadata.
- Tool handlers wrap existing `get_yoga_summary`, `get_current_dasa`, `get_transit_events`, `get_tajaka_summary`, `get_ashtakavarga_summary`.
- LLM prompt template: "debate scaffolding" — system prompt that tells Claude to consult all 4 and produce both synthesized answer + per-strategy reasoning.
- Response shape: `DebatedAnswer` — synthesis text + per-strategy views + agreement score.
- Frontend component: `DebateExpansion` — renders "Why does this answer vary?" expandable panel.
- Tier gate: enabled for `subscription_tier in {mystic, master}` only.
- Usage metering: debate-mode calls count against premium usage quota.
- Fallback: if strategies agree (all 4 outputs ≈ identical), render as normal single answer (no debate UI). Saves tokens and UI clutter.
- Analytics: user engagement with the debate UI (expand rate, dwell time).
- Cost controls: debate mode costs ~2× regular AI call (more tokens); budget + alert.

### 2.2 Out of scope
- User choosing strategy weights in-chat — config lives in astrologer preferences (E12); Ultra AI respects them.
- Astrologer-facing debate mode — separate feature in Astrologer Workbench (E12).
- Real-time voting / user picking winner strategy — no UX affordance; informational only.
- Debate across non-strategy axes (e.g., different rule versions) — out of scope.
- Debate on compatibility / synastry — initial release covers yoga + dasa + transit + tajaka + ashtakavarga.
- Tier migration / billing — assumes existing subscription tier system.

### 2.3 Dependencies
- F8 — 4 aggregation strategies computed for every chart-family.
- E11a/E11b — AI chat orchestration v1/v2 (tool-use infrastructure).
- S3 — serving cache (cached per-strategy).
- S6 — lazy compute (ensures 4 strategies ready on demand).

## 3. Technical Research

### 3.1 When do strategies actually disagree?

From E11b instrumentation (collected P2):

- **Yoga activation**: ~15% of activations show disagreement between strategies (typically C disagrees due to astrologer weights; A/B/D agree).
- **Dasa periods**: rare disagreement (~1%) because dasa math is deterministic; disagreement only arises when sources define different dasa systems.
- **Transit events**: ~10% disagreement on threshold-based events (e.g., "Sade Sati starts when Saturn enters 12th from natal Moon" — some sources use whole-sign ingress, others degree-based).
- **Tajaka Muntha**: deterministic; near-zero disagreement.
- **Ashtakavarga**: deterministic; near-zero disagreement.

So debate mode is most useful for **yoga and transit events**. Other families often show no disagreement, rendering as normal.

### 3.2 Debate scaffold: prompt engineering

System prompt fragment:

```
You are Josi's Ultra AI astrologer in DEBATE MODE.

When answering a classical astrology question, you have access to four aggregation strategies:
- Strategy A (Simple Majority): boolean votes, arithmetic means.
- Strategy B (Confidence-Weighted): same shapes, with agreement-fraction confidence.
- Strategy C (Source-Weighted): weighted by this astrologer's preferred source weights.
- Strategy D (Hybrid): Josi's default blend.

For each question:

1. Call get_multi_strategy_summary for the relevant technique.
2. Examine the four outputs.
3. If strategies agree (all 4 say the same within tolerance): answer naturally, citing consensus.
4. If strategies disagree: synthesize with explicit acknowledgment. Structure your response:
   - "Strategy [X] says [result] because [reason/source]."
   - "Strategy [Y] says [different result] because [reason]."
   - "Most likely [best synthesis given user context]. Confidence: [0.0-1.0]."

Be concise but respect the classical ambiguity — some disagreements reflect genuine scholarly debate, not ranking among them.
```

Claude's tool-use + extended thinking naturally handles this structure. Token budget: ~1000 tokens extra for debate responses (vs ~500 for single-strategy).

### 3.3 Agreement detection

Per-output-shape agreement function (reuse P3-E6-flag's `agrees`):

```python
def strategies_agree(outputs: dict[str, Any], shape_id: str) -> bool:
    """True if all 4 strategies produced equivalent outputs within tolerance."""
    if len(outputs) < 2:
        return True
    ref = next(iter(outputs.values()))
    return all(agrees(ref, o, shape_id) for o in outputs.values())
```

If agreement, tool response has `debate_needed=False`; LLM emits single answer, UI renders normally.

If disagreement, tool response has `debate_needed=True`; LLM emits `DebatedAnswer` shape.

### 3.4 Response shape

```python
class StrategyView(BaseModel):
    strategy_id: str                  # "A_majority" | "B_confidence" | "C_weighted" | "D_hybrid"
    strategy_label: str               # human-readable
    output_summary: str               # 1–2 sentence summary of this strategy's answer
    confidence: float | None
    sources_consulted: list[str]

class DebatedAnswer(BaseModel):
    synthesis: str                    # the LLM's synthesized answer
    synthesis_confidence: float       # 0.0–1.0
    debate_needed: bool               # false if all 4 agreed
    strategy_views: list[StrategyView]  # 4 entries when debate_needed
    agreement_summary: str | None     # "3 of 4 agree", etc.
    citations: list[Citation]         # from E11a
```

### 3.5 UI component

```
┌─────────────────────────────────────────────────────────────────┐
│ [Chat bubble: synthesized answer with confidence badge]         │
│                                                                 │
│ ► Why does this answer vary?                (expandable)        │
└─────────────────────────────────────────────────────────────────┘
              ↓ on expand
┌─────────────────────────────────────────────────────────────────┐
│ Synthesized answer (as above)                                   │
│                                                                 │
│ ▼ Strategy breakdown                                            │
│                                                                 │
│ ┌─ A (Simple Majority) ────────────────────────────────────┐    │
│ │ 4 of 5 sources say Gaja Kesari is active.               │    │
│ │ Confidence: 0.80                                         │    │
│ └──────────────────────────────────────────────────────────┘    │
│                                                                 │
│ ┌─ B (Confidence-Weighted) ────────────────────────────────┐    │
│ │ Active with confidence 0.72.                             │    │
│ │ Primary source: BPHS.                                    │    │
│ └──────────────────────────────────────────────────────────┘    │
│                                                                 │
│ ┌─ C (Your source weights: BPHS 1.0, Phaladeepika 0.9) ────┐   │
│ │ Active. Your weights emphasize BPHS which activates.     │    │
│ └──────────────────────────────────────────────────────────┘    │
│                                                                 │
│ ┌─ D (Hybrid — Josi default) ──────────────────────────────┐   │
│ │ Active. Consensus + confidence flattening.               │    │
│ └──────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

### 3.6 Tier gate

Checked on tool-use call path:

```python
async def get_multi_strategy_summary(chart_id, family, *, user):
    if user.subscription_tier not in {"mystic", "master"}:
        raise HTTPException(403, "Debate Mode is available on Mystic and Master tiers.")
    ...
```

Frontend also hides the debate toggle / expansion UI for non-tier users; backend guard is defense in depth.

### 3.7 Cost model

Per debate-mode AI turn:
- 4 strategy reads via cache (4 × ~2ms) = ~10ms
- LLM call: ~2000 input tokens + ~800 output tokens (vs ~1500 in + ~500 out for normal) = ~1.5–2× more tokens.
- Prompt cache (F12) offsets chart-context repetition across turns.

Budget: keep debate-mode average cost per turn ≤ 3× normal turn. Hard cap per user per month = 2× normal quota.

### 3.8 Alternatives considered

| Alternative | Rejected because |
|---|---|
| Always show debate (for all users) | UI clutter for 95% of users; cost increase |
| Pick one strategy per question algorithmically | Loses transparency; users can't tell why answers vary |
| Let user pick strategy | Decision fatigue; most users don't know the strategy semantics |
| Astrologer-only feature | Misses premium consumer segment; Mystic/Master want depth |
| Show debate as a table, not narrative | Less natural in chat UX; table feels bureaucratic |

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| Tier gate | Mystic + Master only | Premium depth feature |
| Auto-enable or user toggle? | User toggle in chat (persistent per session) | Agency |
| Fallback when strategies agree | Render as normal (no debate UI) | Avoid noise |
| Cost cap | 2× normal quota per month | Prevent runaway |
| Families supported | Yoga, dasa, transit_event, tajaka, ashtakavarga | Initial set |
| Response format | Narrative synthesis + expandable strategy cards | Balance depth + scannability |
| Prompt caching | Use F12 caching on chart context | Reduce cost |
| Analytics | Track expand rate + dwell time | Validate feature value |
| Astrologer-weight visibility in C | Show which weights | Transparency |
| What if user has no custom weights? | C strategy uses Josi defaults | Consistent fallback |

## 5. Component Design

### 5.1 New modules

```
src/josi/services/ai/ultra/
├── __init__.py
├── debate_tools.py              # NEW: get_multi_strategy_summary
├── agreement.py                 # NEW: strategies_agree helper
├── debate_orchestrator.py       # NEW: wraps Claude call
└── prompts/
    └── debate_system.md         # NEW: system prompt scaffold

src/josi/schemas/ai/
└── debate_shapes.py             # NEW: DebatedAnswer, StrategyView

src/josi/api/v1/controllers/
└── ai_chat_controller.py        # modified: route Ultra+debate turns

web/components/ai-chat/
├── DebateExpansion.tsx          # NEW: expandable strategy breakdown
├── StrategyCard.tsx             # NEW: per-strategy view
└── DebateToggle.tsx             # NEW: chat-level toggle

web/types/
└── ai-debate.ts                 # NEW: DebatedAnswer types
```

### 5.2 Data model additions

```sql
-- Usage tracking: debate mode calls
ALTER TABLE user_usage
    ADD COLUMN debate_mode_calls_month INT NOT NULL DEFAULT 0,
    ADD COLUMN debate_mode_quota_month INT NOT NULL DEFAULT 0;

-- Analytics: debate engagement
CREATE TABLE debate_engagement (
    id               BIGSERIAL PRIMARY KEY,
    user_id          UUID NOT NULL REFERENCES "user"(user_id),
    chart_id         UUID NOT NULL,
    chat_turn_id     UUID NOT NULL,
    technique_family TEXT NOT NULL,
    debate_surfaced  BOOLEAN NOT NULL,    -- did we actually render debate UI?
    user_expanded    BOOLEAN NOT NULL DEFAULT false,
    dwell_seconds    INT,
    strategies_agreed BOOLEAN NOT NULL,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_debate_engagement_user
    ON debate_engagement(user_id, created_at DESC);
```

### 5.3 Tool: get_multi_strategy_summary

```python
# src/josi/services/ai/ultra/debate_tools.py

class MultiStrategySummary(BaseModel):
    family_id: str
    strategies: dict[str, StrategyOutput]   # strategy_id → per-strategy output
    agreement: bool
    agreement_detail: dict
    astrologer_weights: dict[str, float] | None   # current user's weights if C used

@tool
async def get_multi_strategy_summary(
    chart_id: str,
    technique_family: str,
    *,
    user: CurrentUser,
) -> MultiStrategySummary:
    """Return all 4 strategies' outputs for a given chart and family.
    Available only in Ultra AI mode (Mystic+ tier)."""
    if user.subscription_tier not in {"mystic", "master"}:
        raise HTTPException(403, "Debate Mode requires Mystic or Master tier")

    cache = get_serving_cache()
    session = await get_read_db_session()
    outputs: dict[str, StrategyOutput] = {}
    for strat in ("A_majority", "B_confidence", "C_weighted", "D_hybrid"):
        value = await cache.get(
            UUID(chart_id), technique_family, strat, session,
        )
        if value is None:
            # Lazy compute trigger (S6)
            await trigger_lazy_compute(
                session, UUID(chart_id), technique_family, user_id=user.user_id,
            )
            # wait up to 2s
            for _ in range(2):
                await asyncio.sleep(1.0)
                value = await cache.get(UUID(chart_id), technique_family, strat, session)
                if value is not None:
                    break
        outputs[strat] = value

    shape_id = await _shape_for(technique_family, session)
    agreement = strategies_agree(
        {k: v.result for k, v in outputs.items() if v is not None},
        shape_id,
    )

    return MultiStrategySummary(
        family_id=technique_family,
        strategies=outputs,
        agreement=agreement,
        agreement_detail=_detail(outputs, shape_id),
        astrologer_weights=(await _load_user_weights(session, user.user_id, technique_family)),
    )
```

### 5.4 Agreement helper

```python
# src/josi/services/ai/ultra/agreement.py

def strategies_agree(outputs: dict[str, Any], shape_id: str) -> bool:
    vals = [v for v in outputs.values() if v is not None]
    if len(vals) < 2:
        return True
    ref = vals[0]
    return all(agrees(ref, v, shape_id) for v in vals[1:])
```

### 5.5 Debate orchestrator

```python
# src/josi/services/ai/ultra/debate_orchestrator.py

async def handle_debate_turn(
    chat_session: ChatSession,
    user_message: str,
    user: CurrentUser,
) -> DebatedAnswer:
    # Tools available include both regular (get_yoga_summary) and debate-mode (get_multi_strategy_summary)
    system_prompt = _load_debate_system_prompt()
    response = await claude_client.messages.create(
        model="claude-opus-4-7",
        max_tokens=2500,
        system=system_prompt,
        messages=chat_session.history,
        tools=[*ULTRA_TOOLS, *REGULAR_TOOLS],
        cache_control={"type": "ephemeral"},   # F12
    )

    # Parse tool-use results; build DebatedAnswer
    ...
```

### 5.6 System prompt

Stored as markdown at `src/josi/services/ai/ultra/prompts/debate_system.md`:

```markdown
You are Josi's Ultra AI astrologer, operating in DEBATE MODE.

You have access to four aggregation strategies for every classical technique:
- **Strategy A (Simple Majority)**: boolean votes across sources, arithmetic mean for numbers.
- **Strategy B (Confidence-Weighted)**: same shapes as A, with explicit confidence = agreement fraction.
- **Strategy C (Source-Weighted)**: weighted by the current user's source weights (or Josi defaults).
- **Strategy D (Hybrid)**: Josi's default — internal B semantics surfaced as single best-guess.

When the user asks a classical astrology question:

1. Call `get_multi_strategy_summary(chart_id, technique_family)` for the relevant technique.
2. Examine `agreement`:
   - If `agreement: true`: answer naturally, citing consensus. Skip debate scaffold.
   - If `agreement: false`: produce a DebatedAnswer.
3. For DebatedAnswer, follow this structure:
   - **Synthesis** (2–4 sentences): the most likely answer given the classical weight of evidence and the user's context. Explicitly acknowledge disagreement.
   - **Per-strategy breakdown** (1 sentence each): what each strategy said and why.
   - **Confidence**: 0.0–1.0 indicating how sure you are. Lower when strategies diverge widely.

Principles:
- Never flatten disagreement into false certainty.
- Honor the user's source weights (Strategy C) as one signal, not gospel.
- Some classical disagreements are scholarly debates lasting centuries. It's fine to say "two traditions answer this differently."
- Cite sources (F11 citation shape) within the synthesis.
- Brevity matters: total response ≤ 400 words.
```

### 5.7 Frontend: DebateExpansion

```tsx
// web/components/ai-chat/DebateExpansion.tsx

export function DebateExpansion({ answer }: { answer: DebatedAnswer }) {
  const [expanded, setExpanded] = useState(false);
  const [startedAt, setStartedAt] = useState<number | null>(null);

  useEffect(() => {
    if (expanded) {
      setStartedAt(Date.now());
      trackEvent("debate_expanded", { turn_id: answer.chat_turn_id });
    } else if (startedAt) {
      const dwell = Math.round((Date.now() - startedAt) / 1000);
      trackEvent("debate_collapsed", { turn_id: answer.chat_turn_id, dwell_seconds: dwell });
    }
  }, [expanded]);

  if (!answer.debate_needed) {
    return <ChatBubble text={answer.synthesis} citations={answer.citations} />;
  }

  return (
    <div>
      <ChatBubble text={answer.synthesis} citations={answer.citations} />
      <button onClick={() => setExpanded(!expanded)}
              className="text-sm text-[var(--gold)] mt-2">
        {expanded ? "Hide" : "Why does this answer vary?"}
      </button>
      {expanded && (
        <div className="mt-3 space-y-3">
          {answer.strategy_views.map(v => (
            <StrategyCard key={v.strategy_id} view={v} />
          ))}
        </div>
      )}
    </div>
  );
}
```

### 5.8 StrategyCard

```tsx
// web/components/ai-chat/StrategyCard.tsx
export function StrategyCard({ view }: { view: StrategyView }) {
  return (
    <div className="border border-[var(--border-subtle)] rounded-md p-3">
      <div className="flex items-center justify-between">
        <div className="font-semibold">{view.strategy_label}</div>
        {view.confidence !== null && (
          <ConfidenceBadge value={view.confidence} />
        )}
      </div>
      <p className="mt-1 text-sm text-[var(--text-muted)]">
        {view.output_summary}
      </p>
      {view.sources_consulted.length > 0 && (
        <p className="mt-2 text-xs text-[var(--text-dim)]">
          Sources: {view.sources_consulted.join(", ")}
        </p>
      )}
    </div>
  );
}
```

### 5.9 DebateToggle

```tsx
// web/components/ai-chat/DebateToggle.tsx
export function DebateToggle() {
  const { subscriptionTier } = useUser();
  const [enabled, setEnabled] = useSessionStorage("debate_mode", false);

  if (!["mystic", "master"].includes(subscriptionTier)) return null;

  return (
    <label className="flex items-center gap-2 text-sm">
      <Switch checked={enabled} onCheckedChange={setEnabled} />
      <span>Debate Mode</span>
      <InfoTooltip>
        Show disagreement between classical aggregation strategies.
      </InfoTooltip>
    </label>
  );
}
```

## 6. User Stories

### US-AI5.1: As a Mystic-tier user, I can toggle Debate Mode on in chat and see strategy disagreements
**Acceptance:** Mystic user: toggle visible + functional; chat turn with disagreement shows expandable panel.

### US-AI5.2: As a Free-tier user, Debate Mode is not available
**Acceptance:** toggle hidden; backend call returns 403 if manually invoked.

### US-AI5.3: When all 4 strategies agree, the answer renders normally with no debate UI
**Acceptance:** on agreement, no "Why does this answer vary?" link appears; UI identical to non-debate mode.

### US-AI5.4: When strategies disagree, I see a clear synthesis + per-strategy breakdown
**Acceptance:** disagreement shows 4 StrategyCards; synthesis explicitly mentions disagreement.

### US-AI5.5: The debate view respects my custom source weights (Strategy C)
**Acceptance:** Strategy C card shows my weights (e.g., "BPHS 1.0, Phaladeepika 0.9"); output reflects weighting.

### US-AI5.6: Expand rate and dwell time are tracked for product analytics
**Acceptance:** `debate_engagement` rows logged; Grafana panel shows expand rate by family.

### US-AI5.7: Debate mode usage counts against my monthly premium quota
**Acceptance:** quota decrements on each debate call; hard-cap exceeded returns tier-upgrade prompt.

### US-AI5.8: Cost per debate turn stays within 3× normal turn cost
**Acceptance:** measured mean cost per debate turn ≤ 3× baseline; alert fires if exceeded for > 1 day.

## 7. Tasks

### T-AI5.1: Debate shapes + tool schema
- **Definition:** `DebatedAnswer`, `StrategyView`, `MultiStrategySummary` Pydantic models. Registered in tool catalog.
- **Acceptance:** schemas validate; Claude tool-use contract accepts.
- **Effort:** 2 days
- **Depends on:** E11a, E11b complete

### T-AI5.2: `get_multi_strategy_summary` tool
- **Definition:** Backend tool per 5.3. Reads all 4 strategies via cache, triggers lazy compute if needed.
- **Acceptance:** returns all 4 outputs for a test chart; tier gate enforced (403 for free users).
- **Effort:** 3 days
- **Depends on:** T-AI5.1, S3 + S6 complete

### T-AI5.3: Agreement helper + agreement_detail
- **Definition:** `strategies_agree` + detail extractor per 5.4. Per-shape tolerances (reuse P3-E6-flag `agrees`).
- **Acceptance:** unit tests per shape: agreement detection correct.
- **Effort:** 1 day
- **Depends on:** P3-E6-flag agreement fn

### T-AI5.4: Debate system prompt
- **Definition:** `debate_system.md` per 5.6. Reviewed by classical advisor + product.
- **Acceptance:** merged; Claude responses follow structure in manual testing.
- **Effort:** 2 days
- **Depends on:** T-AI5.2

### T-AI5.5: Debate orchestrator
- **Definition:** `handle_debate_turn` per 5.5. Integrates with F12 prompt caching. Returns DebatedAnswer.
- **Acceptance:** test chat turn produces valid DebatedAnswer; latency ≤ 5s P95.
- **Effort:** 3 days
- **Depends on:** T-AI5.4

### T-AI5.6: Chat controller routing
- **Definition:** `ai_chat_controller.py` detects Ultra mode + debate flag; routes to orchestrator.
- **Acceptance:** flag on → debate path; flag off → regular path.
- **Effort:** 1 day
- **Depends on:** T-AI5.5

### T-AI5.7: Frontend: DebateToggle
- **Definition:** Toggle component per 5.9. Hidden for non-tier users. Persistent via sessionStorage.
- **Acceptance:** tier detection works; state persists across refresh within session.
- **Effort:** 1 day
- **Depends on:** T-AI5.6

### T-AI5.8: Frontend: DebateExpansion + StrategyCard
- **Definition:** Components per 5.7, 5.8. Animation on expand. Analytics events.
- **Acceptance:** renders correctly for 4 strategies; analytics events fire.
- **Effort:** 3 days
- **Depends on:** T-AI5.1

### T-AI5.9: Quota + usage tracking
- **Definition:** Migration for `user_usage.debate_mode_*`. Integration with existing usage service.
- **Acceptance:** quota enforces; over-quota returns friendly upgrade prompt.
- **Effort:** 2 days
- **Depends on:** T-AI5.2

### T-AI5.10: Analytics: `debate_engagement` + Grafana
- **Definition:** Migration + event-ingestion endpoint + Grafana dashboard.
- **Acceptance:** rows logged; panels show expand rate + dwell.
- **Effort:** 2 days
- **Depends on:** T-AI5.8

### T-AI5.11: Cost alerting
- **Definition:** Per-turn cost tracking via existing LLM cost service; alert when mean debate-turn cost > 3× baseline.
- **Acceptance:** alert fires under synthetic cost inflation.
- **Effort:** 1 day
- **Depends on:** T-AI5.5

### T-AI5.12: Documentation + product copy
- **Definition:** User-facing help text ("What is Debate Mode?"). Internal runbook.
- **Acceptance:** copy reviewed; doc merged.
- **Effort:** 1 day
- **Depends on:** T-AI5.8

## 8. Unit Tests

### 8.1 `get_multi_strategy_summary`

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_tier_gate_mystic_allowed` | user.tier=mystic | 200 | gate |
| `test_tier_gate_free_denied` | user.tier=free | 403 | gate |
| `test_returns_all_4_strategies` | cached chart | dict with 4 keys | completeness |
| `test_triggers_lazy_compute_on_miss` | uncached chart | lazy_compute trigger observed | integration |
| `test_agreement_true_when_all_equal` | 4 identical outputs | agreement=True | happy |
| `test_agreement_false_on_divergence` | different outputs | agreement=False | disagreement |
| `test_astrologer_weights_included` | user with prefs | astrologer_weights populated | transparency |

### 8.2 Agreement helper

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_agree_boolean_all_true` | 4x active=True, strength≈0.7 | True | yoga shape |
| `test_disagree_boolean_3_true_1_false` | 3 true, 1 false | False | yoga shape |
| `test_agree_when_single_strategy_present` | only 1 non-null | True (degenerate) | edge |
| `test_disagree_temporal_outside_1hr` | starts differ 2hr | False | temporal shape |
| `test_agree_numeric_within_5pct` | 100, 103, 97, 102 | True | numeric shape |
| `test_disagree_numeric_outside_5pct` | 100, 110 | False | numeric shape |

### 8.3 Orchestrator

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_orchestrator_returns_debated_answer` | disagreeing outputs | DebatedAnswer with debate_needed=True | path |
| `test_orchestrator_returns_flat_when_agreement` | agreeing outputs | debate_needed=False | skip debate UI |
| `test_orchestrator_includes_citations` | response | citations array populated | F11 integration |
| `test_orchestrator_synthesis_nonempty` | any input | synthesis has > 20 chars | quality |
| `test_orchestrator_strategy_views_count_4` | disagreement | 4 StrategyView entries | contract |
| `test_orchestrator_cost_tracked` | turn complete | cost recorded to metric | observability |

### 8.4 Tier + quota

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_quota_decrement_on_call` | 1 debate call | debate_mode_calls_month += 1 | usage |
| `test_quota_exceeded_returns_upgrade` | quota full | 402 with upgrade message | metering |
| `test_quota_resets_monthly` | month boundary | counter reset to 0 | accounting |
| `test_master_has_higher_quota` | master tier | quota > mystic | tier diff |

### 8.5 Frontend (Testing Library / Playwright)

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_toggle_hidden_for_free_tier` | user.tier=free | toggle not rendered | UX |
| `test_toggle_visible_for_mystic` | user.tier=mystic | toggle rendered | UX |
| `test_expand_shows_4_strategy_cards` | DebatedAnswer with 4 views | 4 cards rendered | UI |
| `test_no_expand_link_on_agreement` | agreement=True | no "Why does this answer vary?" | UX |
| `test_expand_fires_analytics_event` | expand click | trackEvent called | analytics |
| `test_dwell_time_measured_on_collapse` | expand + wait 3s + collapse | dwell_seconds=3 | analytics |

### 8.6 Analytics

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_engagement_row_per_turn` | debate turn | 1 debate_engagement row | logging |
| `test_strategies_agreed_flag` | agreement path | row.strategies_agreed=True | accuracy |
| `test_debate_surfaced_flag` | debate_needed=True | row.debate_surfaced=True | accuracy |

### 8.7 Cost

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_cost_alert_under_threshold` | mean cost 2× baseline | no alert | silent |
| `test_cost_alert_over_threshold` | mean cost 4× baseline for 1 day | alert fires | guard |

## 9. EPIC-Level Acceptance Criteria

- [ ] `get_multi_strategy_summary` tool implemented with tier gate
- [ ] `strategies_agree` helper covers all 10 output shapes
- [ ] Debate system prompt merged; Claude produces structured output in manual testing
- [ ] Debate orchestrator returns DebatedAnswer within 5s P95
- [ ] Chat controller routes Ultra+debate turns to orchestrator
- [ ] Frontend: DebateToggle hidden for non-tier users; DebateExpansion renders strategy cards
- [ ] Debate UI respects agreement: no expansion when strategies agree
- [ ] Astrologer source weights surfaced in Strategy C card
- [ ] `user_usage.debate_mode_*` columns populated per call; quota enforced
- [ ] `debate_engagement` analytics live; Grafana panel for expand rate + dwell
- [ ] Mean debate-turn cost ≤ 3× normal turn cost; alert configured
- [ ] Unit test coverage ≥ 90% for backend modules; ≥ 75% for frontend
- [ ] Documentation + user-facing help copy merged
- [ ] Feature flag cleanly removable; default off; enabled for Mystic/Master tier users opt-in
- [ ] CLAUDE.md updated with "Debate Mode: Ultra AI feature for Mystic+ tiers"

## 10. Rollout Plan

- **Feature flag:** `FEATURE_DEBATE_MODE` (default off).
- **Shadow compute:** N — Debate Mode is an additional surface; it doesn't shadow any existing surface.
- **Rollout phases:**
  1. Week 1: ship backend + frontend in dev; internal dogfooding.
  2. Week 2: enable for Master-tier users only (smallest audience; highest engagement); collect 7 days of feedback + analytics.
  3. Week 3: enable for Mystic tier; monitor cost + satisfaction.
  4. Week 4: publish help article; consider marketing surfaces.
- **Backfill strategy:** N/A — no data backfill required.
- **Rollback plan:**
  1. Flip `FEATURE_DEBATE_MODE=false`. Toggle hidden; backend 404s for route.
  2. Existing `debate_engagement` rows retained.
  3. No user-visible breakage for non-debate chat flows.

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| LLM produces verbose debate when brevity wanted | Medium | Medium | Strict max_tokens; prompt instructs ≤ 400 words; tested with 20+ example turns |
| Users confused by debate UI | Medium | Medium | Help tooltip; clear "Why does this answer vary?" label; user testing |
| Cost spike from debate mode | Medium | Medium | Quota + alert; hard cap 2× monthly quota |
| Tier gate bypass via API | Low | High | Enforced in backend tool call (defense in depth); logged |
| Agreement detection false positives (treat disagreement as agreement) | Low | Medium | Property-based tests per shape; conservative tolerances |
| Latency regression (4 cache calls vs 1) | Low | Low | Cache ensures < 10ms total; parallel reads |
| Astrologer weights leaked cross-user (C strategy) | Low | High | Strict user-scoping in query; audit test |
| Analytics loss if event endpoint errors | Medium | Low | Fire-and-forget; no user blocking |
| Frustration when agreement happens often (debate rarely appears) | Low | Low | Acceptable: agreement is correct outcome; analytics show on which families disagreement occurs |
| Gaming via repeated debate calls to fish for desired answer | Low | Low | Quota caps; answers deterministic per chart state |

## 12. References

- Master spec: [`docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`](../../../superpowers/specs/2026-04-19-classical-techniques-expansion-design.md), §3.4 Ultra AI mode.
- Depends on: [E11b](../P2/E11b-ai-chat-debate-mode.md), [S3](./S3-three-layer-serving-cache.md), [S6](./S6-lazy-compute-strategy.md), [F8](../P0/F8-technique-result-aggregation-protocol.md)
- Related: [F11](../P0/F11-citation-embedded-responses.md), [F12](../P0/F12-prompt-caching-claude.md)
- Tool use: Anthropic tool-use docs
- Premium tier UX patterns: ChatGPT Pro, Perplexity Pro
