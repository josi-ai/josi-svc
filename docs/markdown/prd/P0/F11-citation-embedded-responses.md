---
prd_id: F11
epic_id: F11
title: "Citation-embedded response shape (CitedFact universal envelope)"
phase: P0-foundation
tags: [#ai-chat, #correctness, #extensibility]
priority: must
depends_on: [F10]
enables: [E11a, E11b, AI5]
classical_sources: []
estimated_effort: 3-4 days
status: draft
author: @agent
last_updated: 2026-04-19
---

# F11 — Citation-Embedded Response Shape

## 1. Purpose & Rationale

The LLM is only as epistemically honest as the data it receives. If we hand Claude `"gaja_kesari: active=true, strength=0.82"`, it will blithely declare that Gaja Kesari is active at 82% without telling the user *which classical source said so*, *how confident we are*, or *whether other sources disagree*. That is generic, culturally shallow, and indistinguishable from the many LLM-wrapper astrology apps.

Josi's differentiator is that **every fact the LLM sees carries its provenance**. Gaja Kesari is not just "active=true" — it's "active=true, per BPHS 36.14-16, confidence 0.90, 4 of 5 sources agree, Saravali dissents". When that shape reaches the LLM, the LLM naturally generates readings like "Gaja Kesari is strongly active in your chart (per the Brihat Parashara Hora Shastra, chapter 36) — though Saravali's framing is stricter".

This PRD establishes the **universal envelope** `CitedFact[T]` used by every `value` field in every AI-tool response. It specifies:

- Generic Pydantic model carrying value, source, citation, confidence, cross-source agreement, dissenters.
- How each aggregation strategy (A/B/C/D from F8) populates each field.
- Prompt patterns that teach Claude to modulate tone by confidence and surface citations on "why".
- Sanitization layer that never exposes internal source ids directly to the user (we don't want users seeing `source_id='jh'`).
- Round-trip and LLM-behavior tests.

## 2. Scope

### 2.1 In scope
- Generic `CitedFact[T]` Pydantic model (Pydantic v2 generics)
- Integration contract: every F10 tool response field that reports a classical conclusion wraps its value in `CitedFact[T]`
- Mapping: aggregation strategy → citation population rules
- `SourceSanitizer` that translates canonical `source_id` to user-safe display names
- System-prompt fragment (stored as a constant) that instructs Claude how to use citations and modulate tone
- Unit tests for roundtrip, sanitization, and strategy→citation mapping
- Golden LLM transcript test: given a `CitedFact`-heavy input, Claude's response contains the citation in natural prose

### 2.2 Out of scope
- Rendering citations in the UI (E12, E13)
- Per-language citation translation (D3)
- Footnote tracking / deduplication at render time (E13)
- Debate mode / Ultra AI (E11b)
- Inline streaming of citations as tokens arrive (future)

### 2.3 Dependencies
- F8 (aggregation strategies emit events with enough metadata to populate CitedFact)
- F9 (reading view stores already-aggregated CitedFact projections)
- F10 (tools consume CitedFact)

## 3. Technical Research

### 3.1 Why a universal envelope

Two alternatives:

- **Parallel fields** (`strength`, `strength_source`, `strength_citation`, `strength_confidence`): explodes field count; error-prone; LLM has to correlate fields by suffix.
- **Single envelope `CitedFact[T]`**: one structural type; consistent contract; LLM learns the pattern once.

The envelope wins. Pydantic v2 supports `BaseModel` generics cleanly with `TypeVar`:

```python
from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")

class CitedFact(BaseModel, Generic[T]):
    value: T
    ...
```

### 3.2 Strategy → citation population rules

From F8 we have four aggregation strategies. Each populates `CitedFact` differently:

| Strategy | `source_id` | `citation` | `confidence` | `cross_source_agreement` | `dissenting_sources` |
|---|---|---|---|---|---|
| **A — Simple majority** | `"consensus"` | `null` | `null` | e.g., `"4/5 sources agree"` | `null` |
| **B — Confidence-weighted** | top-agreeing source id | that source's citation | agreement fraction (0..1) | same fraction as text | sources voting the other way |
| **C — Source-weighted** | highest-weighted source in majority | that source's citation | weighted agreement score | text form | sources with non-zero weight voting other way |
| **D — Hybrid (default)** | = B for end-user surfaces; = C for astrologer surfaces | same | same | same | same |

`source_id="consensus"` is a sentinel — it is sanitized for user-facing rendering as "traditional consensus" or the localized equivalent.

### 3.3 Confidence → tone modulation (prompt pattern)

We instruct Claude (in the system prompt) to map confidence ranges to epistemic hedges:

| Confidence range | Example phrasing |
|---|---|
| ≥ 0.85 | "is strongly active", "definitively present", "clearly indicates" |
| 0.60 – 0.85 | "appears active", "likely indicates", "the tradition sees" |
| 0.40 – 0.60 | "some traditions see", "is weakly indicated", "partially present" |
| < 0.40 | "is contested", "rarely seen as active", "one source holds that" |

For `source_id == "consensus"` (strategy A), no single-source citation can be quoted. The prompt instructs Claude to say "across the classical tradition" or equivalent.

### 3.4 Sanitization layer

We never expose:
- Software-reference `source_id`s like `"jh"` or `"maitreya"` to end users (these are calibration references, not canonical sources to cite).
- Raw `source_id`s (e.g., `"tajaka_neelakanthi"`) verbatim to end users (use `display_name` from `source_authority`).

Sanitization happens at **tool response construction time**, not at prompt time. The LLM never sees the raw `source_id` in a way that could surface through a jailbreak.

Astrologer Pro mode (E12) *does* expose raw `source_id`s — different surface, same underlying data.

### 3.5 LLM-behavior evaluation

We add a golden transcript test: given a fixture `YogaSummary` with `CitedFact`s, we call Claude with a fixed question ("why is this yoga active?") and assert that:
- The response contains the citation string verbatim OR its `display_name`.
- The hedging phrase matches the confidence bucket.
- For `cross_source_agreement` = "4/5", Claude mentions that "most sources agree" or similar.

This test runs against the real Anthropic API (dev env) on nightly CI; daily PR runs use a cached/mocked response to avoid API cost.

### 3.6 Alternatives considered

| Alternative | Rejected because |
|---|---|
| Parallel fields (suffix pattern) | Exploding field count; LLM has to correlate |
| Citation as markdown footnotes in strings | Unreliable parsing; loses structural access |
| Citations only on "why" follow-up | Too late; loses tone calibration; not caching-friendly |
| Put citations in system prompt once, never in tool responses | LLM can't match citation to specific fact |
| Confidence as categorical (low/med/high) | Loses precision for aggregation strategies; categorical mapping still derived from numeric via Section 3.3 |
| Expose raw source_id to users | Breaks UX ("what is 'jh'?"); sanitization is the cleaner layer |

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| Generic T vs union of specific types | Generic `CitedFact[T]` | Type-safe, reusable, Pydantic v2 supports natively |
| Confidence numeric vs categorical | Numeric 0..1 | Finer precision; categorical derived at prompt time |
| Where sanitization happens | At tool response construction | LLM never sees raw source_id |
| Dissenting sources field | List of sanitized display names | Supports "Saravali disagrees" prose |
| Consensus sentinel | `source_id="consensus"` | Explicit; distinguishable from real sources |
| Fallback when aggregation has < 2 sources | `source_id` = single source; `confidence` = that source's default_weight; `cross_source_agreement` = null | Preserves determinism |
| User-visible vs astrologer-visible sanitization | Two modes on sanitizer | `sanitize(fact, audience='end_user' | 'astrologer')` |
| System-prompt fragment ownership | F11 owns it; E11a composes final prompt | Separation of concerns |
| Contract-stability guarantees | CitedFact is part of snapshot tests from F10 | Single snapshot mechanism |

## 5. Component Design

### 5.1 New modules

```
src/josi/schemas/ai/
├── cited_fact.py                  # CitedFact[T] generic
├── source_sanitizer.py            # id → display name + audience filter
└── prompt_fragments.py            # CITATION_TONE_SYSTEM_PROMPT constant

src/josi/services/ai/
└── aggregation_to_cited_fact.py   # strategy → CitedFact population mapper

tests/fixtures/ai/
└── cited_fact_corpus.json         # fixtures for snapshot + LLM tests

tests/integration/
└── test_llm_citation_behavior.py  # golden transcript test (Anthropic live, nightly)
```

### 5.2 CitedFact model

```python
# src/josi/schemas/ai/cited_fact.py

from typing import Generic, TypeVar, Literal
from pydantic import BaseModel, Field, ConfigDict

T = TypeVar("T")


class CitedFact(BaseModel, Generic[T]):
    """Universal envelope for any fact surfaced to the LLM.

    Every classical-technique conclusion that reaches the LLM MUST be wrapped
    in this envelope so that the LLM can naturally generate citation-bearing,
    tone-calibrated responses.
    """

    model_config = ConfigDict(frozen=True)

    value: T = Field(
        description="The actual fact value (boolean, number, string, etc.)."
    )

    source_id: str | Literal["consensus"] = Field(
        description=(
            "Sanitized source identifier. Either a human-readable source name "
            "(e.g., 'Brihat Parashara Hora Shastra') or the sentinel 'consensus' "
            "indicating classical tradition consensus rather than a single source."
        )
    )

    citation: str | None = Field(
        default=None,
        description=(
            "Specific verse/chapter citation, e.g., 'BPHS Ch.36 v.14-16'. "
            "Null when source is 'consensus' or citation unavailable."
        ),
    )

    confidence: float = Field(
        ge=0.0, le=1.0,
        description=(
            "Confidence score in [0,1]. Use to modulate tone: "
            ">=0.85 definitive, 0.6-0.85 likely, 0.4-0.6 partial, <0.4 contested."
        ),
    )

    cross_source_agreement: str | None = Field(
        default=None,
        description=(
            "Human-readable agreement summary, e.g., '4/5 sources agree', "
            "'unanimous', 'split opinion'. Null when only one source considered."
        ),
    )

    dissenting_sources: list[str] = Field(
        default_factory=list,
        description=(
            "Sanitized display names of sources disagreeing with this value. "
            "Empty when unanimous or only one source."
        ),
    )
```

### 5.3 Strategy → CitedFact mapper

```python
# src/josi/services/ai/aggregation_to_cited_fact.py

from josi.schemas.ai.cited_fact import CitedFact


@dataclass
class PerSourceResult:
    source_id: str
    value: Any
    source_weight: float
    citation: str | None


def build_cited_fact_strategy_a(
    per_source: list[PerSourceResult],
    consensus_value: Any,
    agreement_fraction: float,
) -> CitedFact:
    """Majority strategy: consensus sentinel, no citation."""
    return CitedFact(
        value=consensus_value,
        source_id="consensus",
        citation=None,
        confidence=agreement_fraction,  # inherited from B when applicable
        cross_source_agreement=_format_agreement(per_source, agreement_fraction),
        dissenting_sources=[],
    )


def build_cited_fact_strategy_b(
    per_source: list[PerSourceResult],
    majority_value: Any,
) -> CitedFact:
    agreeing = [s for s in per_source if s.value == majority_value]
    dissenting = [s for s in per_source if s.value != majority_value]
    top = max(agreeing, key=lambda s: s.source_weight)
    fraction = len(agreeing) / len(per_source)
    return CitedFact(
        value=majority_value,
        source_id=_display(top.source_id),
        citation=top.citation,
        confidence=fraction,
        cross_source_agreement=_format_agreement(per_source, fraction),
        dissenting_sources=[_display(s.source_id) for s in dissenting],
    )


def build_cited_fact_strategy_c(
    per_source: list[PerSourceResult],
    weighted_majority_value: Any,
) -> CitedFact:
    agreeing = [s for s in per_source if s.value == weighted_majority_value]
    dissenting = [s for s in per_source if s.value != weighted_majority_value]
    total_w = sum(s.source_weight for s in per_source)
    agree_w = sum(s.source_weight for s in agreeing)
    top = max(agreeing, key=lambda s: s.source_weight)
    return CitedFact(
        value=weighted_majority_value,
        source_id=_display(top.source_id),
        citation=top.citation,
        confidence=agree_w / total_w if total_w else 0.0,
        cross_source_agreement=_format_agreement_weighted(per_source, agree_w / total_w),
        dissenting_sources=[_display(s.source_id) for s in dissenting
                            if s.source_weight > 0],
    )


def build_cited_fact_strategy_d(
    per_source: list[PerSourceResult],
    value: Any,
    surface: Literal["end_user", "astrologer"],
) -> CitedFact:
    """Hybrid: B for end-user; C for astrologer."""
    if surface == "end_user":
        return build_cited_fact_strategy_b(per_source, value)
    return build_cited_fact_strategy_c(per_source, value)


def _format_agreement(per_source, fraction) -> str:
    agreeing_count = round(fraction * len(per_source))
    return f"{agreeing_count}/{len(per_source)} sources agree"


def _display(source_id: str) -> str:
    """Thin wrapper over SourceSanitizer.display_name(); imported here to avoid cycle."""
    from josi.schemas.ai.source_sanitizer import display_name
    return display_name(source_id, audience="end_user")
```

### 5.4 Source sanitizer

```python
# src/josi/schemas/ai/source_sanitizer.py

from typing import Literal
from functools import lru_cache

# Loaded once at startup from source_authority table; cached.
_DISPLAY_NAMES: dict[str, str] = {}

# Sources that are *reference implementations*, not canonical classical sources.
# Never surfaced to end users. Astrologers (Pro mode) can see them as
# calibration references.
REFERENCE_SOURCES: set[str] = {"jh", "maitreya"}


def refresh_from_db(session) -> None:
    """Called at app startup and on YAML reload. Populates _DISPLAY_NAMES."""
    # SELECT source_id, display_name FROM source_authority
    ...


def display_name(source_id: str, *, audience: Literal["end_user", "astrologer"]) -> str:
    if source_id == "consensus":
        return "traditional consensus" if audience == "end_user" else "consensus"
    if source_id in REFERENCE_SOURCES and audience == "end_user":
        # Don't leak reference-impl names to end users.
        return "reference implementation"
    return _DISPLAY_NAMES.get(source_id, source_id)


def sanitize_cited_fact(fact: CitedFact, audience: Literal["end_user", "astrologer"]) -> CitedFact:
    """Return a new CitedFact whose source_id and dissenting_sources are sanitized for audience."""
    return fact.model_copy(update={
        "source_id": display_name(fact.source_id, audience=audience),
        "dissenting_sources": [display_name(s, audience=audience) for s in fact.dissenting_sources],
    })
```

### 5.5 System-prompt fragment

```python
# src/josi/schemas/ai/prompt_fragments.py

CITATION_TONE_SYSTEM_PROMPT = """\
When the tool responses return facts wrapped in a CitedFact structure, you MUST:

1. Modulate your epistemic tone by the `confidence` score:
   - >= 0.85: use definitive language ("is strongly active", "clearly indicates").
   - 0.60-0.85: use likely language ("appears active", "the tradition sees").
   - 0.40-0.60: use partial language ("some traditions see", "is weakly indicated").
   - < 0.40: use contested language ("is contested", "one source holds that").

2. When the user asks "why?" or requests evidence, quote the `citation` field
   verbatim when present (e.g., "per Brihat Parashara Hora Shastra, Chapter 36,
   verses 14-16"). When `source_id` is "consensus" or "traditional consensus",
   phrase as "across the classical tradition" instead of naming a source.

3. When `cross_source_agreement` indicates disagreement (e.g., "3/5 sources
   agree") AND `dissenting_sources` is non-empty, briefly acknowledge the
   disagreement in measured language: "Saravali frames this more strictly,
   but the majority view holds..."

4. Do NOT invent citations. If `citation` is null, do not attribute a verse.

5. Do NOT expose raw internal identifiers (anything that looks like a lowercase
   snake_case code) — the source_id you receive is already user-facing.
"""
```

This constant is imported by E11a and inlined into the assistant system prompt.

### 5.6 Integration with F10 tool responses

Reference back to F10 §5.2 — every field that carries a classical conclusion uses `CitedFact[T]`:

```python
class YogaEntry(BaseModel):
    yoga_id: str
    display_name: str
    active: CitedFact[bool]
    strength: CitedFact[float]
    classical_names: dict[str, str]  # NOT a classical conclusion — raw data
```

The tool handler sanitizes for audience before returning:

```python
audience = "astrologer" if caller_is_astrologer else "end_user"
for yoga in yogas:
    yoga.active = sanitize_cited_fact(yoga.active, audience=audience)
    yoga.strength = sanitize_cited_fact(yoga.strength, audience=audience)
```

## 6. User Stories

### US-F11.1: As the LLM, every classical fact I see carries source + citation + confidence + agreement
**Acceptance:** inspecting a tool response JSON payload shows every non-raw field wrapped in `CitedFact`.

### US-F11.2: As the LLM, I naturally modulate tone by confidence
**Acceptance:** golden transcript test: for facts with confidence > 0.85, response uses definitive language; for 0.4-0.6, uses partial language. Manual check on 20 fixtures.

### US-F11.3: As a user, I do not see internal source ids like `jh` or snake_case
**Acceptance:** for every CitedFact sanitized as `end_user`, `source_id` is a human-readable string; `dissenting_sources` entries are human-readable; reference-implementation ids mapped to "reference implementation".

### US-F11.4: As an astrologer in Pro mode, I see the actual source ids (e.g., "Brihat Parashara Hora Shastra")
**Acceptance:** sanitize with `audience="astrologer"` preserves real display names and includes reference implementations.

### US-F11.5: As a backend engineer, changing confidence math in a strategy does not change the response shape
**Acceptance:** snapshot test passes; only `confidence` float value changes, not the envelope.

### US-F11.6: As a classical advisor, when strategy is "simple majority", no specific citation is attributed
**Acceptance:** for `source_id="consensus"`, `citation` is null; prompt fragment ensures LLM says "across the classical tradition" not a made-up citation.

### US-F11.7: As the chat orchestrator, when CitedFact agrees strongly and dissenting_sources is non-empty, the LLM acknowledges disagreement briefly
**Acceptance:** golden transcript test verifies "Saravali disagrees" or equivalent phrase appears when dissent present.

## 7. Tasks

### T-F11.1: `CitedFact[T]` generic Pydantic model
- **Definition:** Write `cited_fact.py` with generic model; ensure `model_json_schema()` works for parameterized types (`CitedFact[bool]`, `CitedFact[float]`, `CitedFact[str]`).
- **Acceptance:** unit tests round-trip all parameterizations; Pydantic generic instantiation works in F10 contracts.
- **Effort:** 4 hours
- **Depends on:** nothing

### T-F11.2: Source sanitizer
- **Definition:** `source_sanitizer.py` with `display_name()` + `sanitize_cited_fact()`; loader refreshes `_DISPLAY_NAMES` from DB on startup.
- **Acceptance:** reference sources masked for end user; preserved for astrologer; consensus mapped correctly.
- **Effort:** 4 hours
- **Depends on:** F1 (source_authority) seeded

### T-F11.3: Strategy → CitedFact mapper
- **Definition:** `build_cited_fact_strategy_{a,b,c,d}()` per F8 strategies.
- **Acceptance:** unit tests for each strategy produce correct shape from fixture per-source results.
- **Effort:** 1 day
- **Depends on:** T-F11.1, T-F11.2, F8 done

### T-F11.4: System-prompt fragment constant
- **Definition:** `CITATION_TONE_SYSTEM_PROMPT` in `prompt_fragments.py`; exported from package.
- **Acceptance:** fragment text reviewed; imported by E11a.
- **Effort:** 2 hours
- **Depends on:** nothing

### T-F11.5: Integrate CitedFact into F10 tool contracts
- **Definition:** Update F10 Pydantic models to use `CitedFact[T]` where appropriate; handlers apply `sanitize_cited_fact` for audience before return.
- **Acceptance:** F10 handlers pass their own tests with CitedFact; snapshot tests regenerated.
- **Effort:** 4 hours
- **Depends on:** T-F11.1, T-F11.2, F10 in progress

### T-F11.6: Golden LLM transcript test (mocked + live)
- **Definition:** `test_llm_citation_behavior.py` with fixtures + assertions on phrasing. Mocked variant runs in CI; live variant nightly.
- **Acceptance:** mocked test passes deterministically; live test passes in staging with real Anthropic key.
- **Effort:** 1 day
- **Depends on:** T-F11.4, T-F11.5

### T-F11.7: Documentation
- **Definition:** `docs/markdown/ai-citations.md` describing the CitedFact contract + prompt patterns; `CLAUDE.md` note under AI layer.
- **Acceptance:** merged, linked from INDEX.
- **Effort:** 2 hours
- **Depends on:** T-F11.6

## 8. Unit Tests

### 8.1 CitedFact model

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_cited_fact_bool_roundtrip` | `CitedFact[bool](value=True, source_id='bphs', confidence=0.9)` | `.model_dump_json()` → `.model_validate_json()` equal | generic T works |
| `test_cited_fact_float_roundtrip` | `CitedFact[float](value=0.82, source_id='consensus', confidence=0.7)` | round-trip equal | numeric T works |
| `test_cited_fact_str_roundtrip` | `CitedFact[str](value='jupiter', source_id='jaimini_sutras', confidence=1.0)` | round-trip equal | string T works |
| `test_confidence_range_enforced` | `CitedFact[bool](value=True, source_id='bphs', confidence=1.5)` | `ValidationError` | bound check |
| `test_dissenting_sources_defaults_empty` | construct without `dissenting_sources` | `== []` | default ergonomics |
| `test_frozen_immutability` | instance.confidence = 0.5 | raises | immutability |
| `test_json_schema_has_descriptions` | `CitedFact[bool].model_json_schema()` | every property has non-empty `description` | Claude readability |

### 8.2 Source sanitizer

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_sanitize_consensus_enduser` | `source_id='consensus'`, audience=end_user | returns `"traditional consensus"` | sentinel mapping |
| `test_sanitize_consensus_astrologer` | `source_id='consensus'`, audience=astrologer | returns `"consensus"` | less dressed up |
| `test_sanitize_reference_source_enduser` | `source_id='jh'`, end_user | returns `"reference implementation"` | don't leak JH |
| `test_sanitize_reference_source_astrologer` | `source_id='jh'`, astrologer | returns `"Jagannatha Hora 7.x (reference implementation)"` | astrologers see it |
| `test_sanitize_canonical_source` | `source_id='bphs'`, end_user | returns `"Brihat Parashara Hora Shastra"` | display name |
| `test_sanitize_unknown_source_passthrough` | `source_id='unseen'`, end_user | returns `"unseen"` | graceful fallback |
| `test_sanitize_cited_fact_maps_dissenting` | fact with `dissenting_sources=['jh','bphs']`, end_user | `['reference implementation', 'Brihat Parashara Hora Shastra']` | recursion works |

### 8.3 Strategy → CitedFact mappers

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_strategy_a_emits_consensus` | 4 agree True, 1 False | `source_id='consensus'`, `citation=None`, `cross_source_agreement='4/5 sources agree'` | majority rule |
| `test_strategy_b_top_source_is_highest_agreeing` | bphs(w=1.0)=True, saravali(w=0.85)=True, jh(w=0.95)=False | `source_id=bphs`, `confidence=0.67`, `dissenting_sources=['Jagannatha Hora...']` | B picks highest agreeing |
| `test_strategy_c_weighted_confidence` | bphs(w=1.0)=True, saravali(w=0.5)=True, jh(w=1.0)=False | `confidence = (1.0+0.5)/(1.0+0.5+1.0) = 0.6` | C weights |
| `test_strategy_d_end_user_behaves_as_b` | same inputs for end_user and astrologer | end_user matches B output; astrologer matches C | hybrid dispatch |
| `test_strategy_unanimous` | 5 agree | `confidence=1.0`, `dissenting_sources=[]`, agreement='unanimous' or '5/5' | edge case |
| `test_strategy_single_source` | 1 source only | `cross_source_agreement=None`; `confidence=source.weight or 1.0` | fallback |

### 8.4 Integration with F10

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_yoga_summary_serializes_with_cited_fact` | build a YogaSummary fixture | JSON payload has `active.value`, `active.source_id`, etc. | shape integration |
| `test_sanitization_applied_for_end_user_audience` | YogaEntry with `source_id='jh'` in `active`; sanitize end_user | returned entry has `source_id='reference implementation'` | audience gating |
| `test_sanitization_preserved_for_astrologer_audience` | same fixture, astrologer | `source_id` preserved | astrologer sees detail |
| `test_non_classical_fields_not_wrapped` | YogaEntry.classical_names | plain dict, not CitedFact | only conclusions are wrapped |

### 8.5 Golden LLM transcript (mocked + live)

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_llm_uses_definitive_tone_high_confidence` | YogaSummary with confidence=0.9 | LLM response contains "strongly" / "clearly" / "definitively" | tone calibration |
| `test_llm_uses_hedged_tone_low_confidence` | YogaSummary with confidence=0.35 | LLM response contains "some traditions" / "contested" / "rarely" | tone calibration |
| `test_llm_cites_bphs_on_why` | ask "why is Gaja Kesari active?" with citation='BPHS 36.14-16' | response contains that citation verbatim OR "Brihat Parashara" | citation surfaces on demand |
| `test_llm_says_consensus_for_strategy_a` | fixture with source_id='consensus' | response mentions "tradition" or "consensus"; no invented citation | no hallucination |
| `test_llm_acknowledges_dissent` | fixture with dissenting=['Saravali'] | response mentions "Saravali" or "different framing" | dissent surfaced |
| `test_llm_does_not_expose_raw_source_id` | fixture sanitized for end_user | response contains no occurrence of 'jh', 'bphs' (raw) | sanitization holds through LLM |

### 8.6 JSON Schema / contract

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_cited_fact_schema_stable` | `CitedFact[bool].model_json_schema()` | matches snapshot in `tests/snapshots/cited_fact_bool.json` | stability enforced |
| `test_adding_field_with_default_is_additive` | add new optional field | snapshot test marks additive OK | non-breaking change |
| `test_removing_field_fails_contract` | remove `dissenting_sources` | snapshot test fails | breaking change caught |

## 9. EPIC-Level Acceptance Criteria

- [ ] `CitedFact[T]` generic Pydantic model exists and is used by every classical-conclusion field in F10
- [ ] All 4 aggregation-strategy → CitedFact mappers implemented and unit-tested
- [ ] `SourceSanitizer` maps ids correctly for both audience modes
- [ ] Reference-implementation source ids (`jh`, `maitreya`) never surface to end users in a single test case by any path
- [ ] System-prompt fragment exists; imported by E11a
- [ ] Golden LLM transcript test (mocked variant) passes in CI
- [ ] Live LLM transcript test passes against Anthropic SDK nightly
- [ ] Snapshot tests enforce contract stability for `CitedFact`
- [ ] Unit test coverage ≥ 95% for `cited_fact.py`, `source_sanitizer.py`, `aggregation_to_cited_fact.py`
- [ ] Documentation: `docs/markdown/ai-citations.md` merged and linked
- [ ] Integration test: F10 tool response → serialized payload → CitedFact roundtrip → sanitized output

## 10. Rollout Plan

- **Feature flag:** `CITED_FACT_ENVELOPE_ENABLED` (default ON in P0; exists only to force-degrade to pre-CitedFact shape for emergency rollback — which should never be needed because this is greenfield).
- **Shadow compute:** N/A — formatting layer.
- **Backfill:** None (all future aggregation events carry CitedFact; past aggregation events before F11 ship get re-aggregated via F9 lazy paths).
- **Rollback:** Disable flag; degrades to raw values in tool responses. LLM output quality drops but nothing crashes. Sanitizer is idempotent on already-sanitized values.

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Pydantic generic schema generation produces inconsistent JSON for different T | Low | Medium | Pin Pydantic version; snapshot tests per parameterization |
| LLM ignores confidence hedging despite prompt | Medium | Medium | Golden transcript tests (mocked + live); prompt A/B iteration; fall back to post-processing regex guard at E11a |
| Sanitizer cache goes stale when a new source is added via YAML | Low | Low | `refresh_from_db()` called on dim-loader reload; manual invalidation endpoint for ops |
| Source id leaks via jailbreak ("what is the source_id for BPHS?") | Medium | Low | Sanitization happens before LLM sees data; LLM never has access to raw ids. If jailbroken to guess ids, it's guessing, not leaking. |
| Strategy C confidence > 1.0 due to weight math bug | Low | Medium | Clamp to [0,1] at construction; unit test for boundary cases |
| Cross-source disagreement feels noisy in UX for minor dissent | Medium | Low | Render-layer threshold (E13): only show dissent when > 20% weight dissents; CitedFact shape unchanged |
| Live LLM test burns API quota in CI | Medium | Low | Nightly only; budget cap in CI env; mocked variant on PR |

## 12. References

- Master spec: [`docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`](../../../superpowers/specs/2026-04-19-classical-techniques-expansion-design.md) §3.2 (citation + confidence)
- F8 aggregation protocol: [`F8-technique-result-aggregation-protocol.md`](./F8-technique-result-aggregation-protocol.md) — strategies producing per-source results
- F10 tool contracts: [`F10-typed-ai-tool-use-contract.md`](./F10-typed-ai-tool-use-contract.md) — consumes `CitedFact[T]`
- Pydantic v2 generics: https://docs.pydantic.dev/latest/concepts/models/#generic-models
- Existing source_authority: F1 seed YAML
- Anthropic guidance on tool descriptions: https://docs.anthropic.com/claude/docs/tool-use
