---
prd_id: F8
epic_id: F8
title: "TechniqueResult + AggregationStrategy Protocol"
phase: P0-foundation
tags: [#extensibility, #experimentation, #correctness]
priority: must
depends_on: [F1, F2, F7]
enables: [F9, F10, F13, E1a, E2a, E4a, E6a, E14a, E11a]
classical_sources: []
estimated_effort: 4-5 days
status: draft
author: @agent
last_updated: 2026-04-19
---

# F8 — TechniqueResult + AggregationStrategy Protocol

## 1. Purpose & Rationale

The master spec (§1.3) commits to four aggregation strategies (A/B/C/D) that unify how **per-source raw results** become **per-chart aggregated outputs** across every classical technique — yogas, dasas, tajaka, jaimini, ashtakavarga, transits, sahams.

Without a unifying contract:
- Every engine reinvents the aggregation wheel (different function signatures, different result envelopes, different handling of "some sources didn't compute this rule").
- Adding a fifth strategy (Strategy E) would require touching every engine.
- The experimentation framework (E14a) cannot swap strategies at runtime — they're not polymorphic.
- AI tool-use (F10) cannot publish a stable `TechniqueResult` shape that works across families.

This PRD defines the two core type contracts:

1. **`TechniqueResult[OutputShape]`** — the envelope every engine emits and every AI tool consumes. Generic over output shape (F7). Contains `per_source`, `aggregates`, and `metadata`.
2. **`AggregationStrategy` Protocol** — the plugin interface that each of strategies A/B/C/D implements, and that new experimental strategies add against. Pluggable via Python `entry_points`.

Together, they implement the **Open/Closed principle** over strategies: adding a new strategy requires *zero* engine changes; engines only emit per-source results, strategies do the rest.

## 2. Scope

### 2.1 In scope
- `TechniqueResult` generic dataclass/Pydantic model — the canonical envelope
- `ClassicalEngine` Protocol — refinement of the scaffold in F2 (§5.4) with clear contract
- `AggregationStrategy` Protocol — the full plugin contract
- `AggregationContext` dataclass — the runtime inputs each strategy receives (astrologer prefs, experiment arm, surface, user mode)
- Plugin registration via Python `entry_points` (`josi.aggregation_strategies`)
- Strategy lifecycle: versioning via `implementation_version`; how events snapshot version at compute time
- Determinism contract: same `per_source` → same `output` (seeded RNG where needed)
- Per-shape dispatch: each strategy declares which `output_shape_id`s it handles; engine falls back to default hybrid (D) or skips when strategy abstains
- Scaffolded test engine + test strategy demonstrating end-to-end round-trip
- Protocol compliance test harness — asserts any registered strategy meets the contract

### 2.2 Out of scope
- **Strategy A/B/C/D implementations** — this PRD provides the Protocol and stubs; full algorithmic implementations ship in P1 (E14a covers A/B/C/D impl + bake-off).
- **Event persistence** — `aggregation_event` table defined in F2; this PRD writes rows via the table but does not redefine it.
- **Feature-flagged rollout of new strategies** — owned by P3 (P3-E6-flag).
- **Experiment allocation logic** (user → arm assignment) — owned by E14a.
- **AI tool-use surfacing** — F10 consumes `TechniqueResult`; this PRD only defines it.
- **Serving-layer flattening** — F9 (`chart_reading_view`) consumes aggregation_event; this PRD only produces them.

### 2.3 Dependencies
- F1 — `aggregation_strategy`, `experiment`, `experiment_arm`, `output_shape`, `technique_family` dim tables
- F2 — `technique_compute`, `aggregation_event` fact tables; `ClassicalEngine` Protocol scaffold
- F7 — output-shape Pydantic models and JSON Schemas (for per-shape dispatch)
- Python 3.12+ (`typing.Protocol`, `ParamSpec`, `TypeVar` with `default=`)

## 3. Technical Research

### 3.1 Why two separate contracts (engine + strategy)

Engines and strategies change at different cadences:
- **Engines** evolve with classical knowledge — new yogas added, new dasas supported.
- **Strategies** evolve with product experimentation — new weighting schemes tested monthly.

Coupling them (e.g., "each engine has a `compute_and_aggregate` method") forces both to deploy together. Separating them lets strategies iterate independently, enables A/B testing, and makes plugin registration cleanly scoped.

### 3.2 Why `typing.Protocol` (not ABC)

| Approach | Rejected because |
|---|---|
| `abc.ABC` subclass hierarchy | Runtime `isinstance`; brittle across plugin packages; `ABC` forces inheritance which plugin authors often don't want. |
| `callable` / duck typing | No static checkability; mypy can't enforce signature. |
| **`typing.Protocol`** (chosen) | Structural typing; plugins declare conformance by signature alone; mypy/pyright verify; works across plugin package boundaries; supports generics. |

### 3.3 Why Python `entry_points` for plugin registration

| Approach | Rejected because |
|---|---|
| Hard-coded registry in `aggregation/__init__.py` | Adding a strategy requires editing core; blocks open-source rule authors (P6). |
| Environment variable pointing at a module list | String-based; no IDE support; fragile. |
| Import-side-effect registration (`@register` decorator) | Requires knowing all plugin modules; startup ordering fragile. |
| **`entry_points`** via `pyproject.toml` | Standard Python packaging; `importlib.metadata.entry_points(group='josi.aggregation_strategies')`; discovered at startup; IDE/mypy see the symbol. |

Configuration in `pyproject.toml`:
```toml
[project.entry-points."josi.aggregation_strategies"]
A_majority    = "josi.services.classical.aggregation.strategy_a:MajorityStrategy"
B_confidence  = "josi.services.classical.aggregation.strategy_b:ConfidenceStrategy"
C_weighted    = "josi.services.classical.aggregation.strategy_c:WeightedStrategy"
D_hybrid      = "josi.services.classical.aggregation.strategy_d:HybridStrategy"
```

### 3.4 Per-shape dispatch

Strategies operate over `per_source: dict[source_id, raw_result]`. The semantics of "aggregating two booleans" are very different from "aggregating two temporal hierarchies." So each strategy implements shape-specific methods, and declares which shapes it handles:

```python
class AggregationStrategy(Protocol):
    supported_shapes: frozenset[str]      # {"boolean_with_strength", "numeric", ...}

    def aggregate(
        self,
        per_source: Mapping[str, dict],
        output_shape_id: str,
        context: AggregationContext,
    ) -> dict: ...
```

If a strategy doesn't support a given shape:
- Strategy declares it in `supported_shapes`; engine filters BEFORE dispatch.
- If engine asks anyway (misconfiguration), strategy returns `None` → engine falls through to Strategy D (default hybrid).

### 3.5 Determinism contract

Requirement: given identical `per_source` and `context`, every strategy returns byte-identical `output` on every invocation.

Implications:
- No stateless RNGs in strategy bodies. Where randomness is needed (e.g., tie-breaking in Strategy A when votes are 50/50), use a seeded RNG derived from `inputs_hash` (F13).
- No time-dependent logic.
- Dict iteration order must be deterministic (Python 3.7+ insertion order).
- `per_source` input is sorted by `source_id` before processing in the reference helper.

Determinism is tested by Hypothesis property (F17): `aggregate(ps, shape, ctx) == aggregate(ps, shape, ctx)` for 1000 random inputs per strategy.

### 3.6 Strategy versioning

Strategies evolve. Strategy B v1 might use equal-weight agreement; v1.1 might add smoothing; v2 might rework the formula entirely.

Policy:
- Each strategy class exposes `implementation_version: str` (semver).
- Bump **PATCH** for refactors that do not change output (tested against bake-off fixtures).
- Bump **MINOR** for logic changes that do change output.
- Bump **MAJOR** when the output shape or meaning changes fundamentally.

Every `aggregation_event.strategy_version` column (F2) snapshots the version at compute time. Old events retain their version; recomputes write new rows rather than mutating old ones.

### 3.7 Alternatives considered

| Alternative | Rejected because |
|---|---|
| Single `aggregate()` function handling all shapes via giant if-elif | Untestable, unreadable, blocks plugin extensibility |
| Engine does aggregation itself | Couples engine to strategy; can't A/B test |
| JavaScript-style strategy "just a function" with no Protocol | No static typing; no per-shape dispatch discovery |
| Aggregation via SQL window functions only | Works for trivial cases (majority); breaks for temporal_hierarchy, cross_chart_relations |

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| Protocol vs ABC | Protocol | Structural typing, plugin-friendly |
| Plugin discovery mechanism | `entry_points` | Standard; IDE-discoverable |
| Per-shape dispatch | Strategy declares supported shapes; engine filters | Keeps strategies focused; graceful fallthrough |
| Determinism | Required; seeded RNG when needed | Experiment replay, provenance, reproducibility |
| Strategy returns `None` when shape unsupported | Allowed; engine substitutes default (Strategy D) | Forward compat |
| Strategy version on event | Snapshot at compute time in `aggregation_event.strategy_version` | Experiment replay |
| `TechniqueResult` representation | Pydantic model, generic over shape | Type-safe; serializable; matches F7 |
| Where aggregation runs | In-process, sync, within Celery/worker task (P3 switches to durable workflow) | Simple first; scale later |
| Failure handling | Strategy exception → engine logs, emits `aggregation_event` with `status='failed'` + empty output, continues | Isolation; one bad strategy doesn't break others |
| Context carries astrologer prefs | Yes | Strategy C (weighted) needs per-astrologer weights |
| Parallel strategies on same `per_source` | Yes — engine invokes all configured strategies | Enables Ultra AI mode (§1.3 D4) |

## 5. Component Design

### 5.1 New modules

```
src/josi/services/classical/
├── technique_result.py                  # TechniqueResult generic model
├── aggregation/
│   ├── __init__.py                       # plugin discovery
│   ├── protocol.py                       # AggregationStrategy Protocol + AggregationContext
│   ├── registry.py                       # loads plugins at startup
│   ├── runner.py                         # AggregationRunner — orchestrates strategy invocation
│   ├── strategy_a.py                     # stub (full impl in E14a)
│   ├── strategy_b.py                     # stub
│   ├── strategy_c.py                     # stub
│   └── strategy_d.py                     # stub (default — delegates to B/C blend)
└── engine_base.py                         # ClassicalEngine Protocol (refined from F2)

tests/classical/
└── test_aggregation_protocol.py          # compliance test for every registered strategy
```

### 5.2 TechniqueResult model

```python
# src/josi/services/classical/technique_result.py

from typing import Any, Generic, TypeVar
from pydantic import BaseModel, ConfigDict, Field

# Bound to a Pydantic output-shape model from F7
ShapeT = TypeVar("ShapeT", bound=BaseModel)

class PerSourceEntry(BaseModel, Generic[ShapeT]):
    model_config = ConfigDict(extra="forbid")
    source_id:       str
    rule_version:    str
    content_hash:    str                       # F13 linkage
    result:          ShapeT                    # typed per output shape
    computed_at:     datetime

class AggregateEntry(BaseModel, Generic[ShapeT]):
    model_config = ConfigDict(extra="forbid")
    strategy_id:        str
    strategy_version:   str
    experiment_id:      str | None = None
    experiment_arm_id:  str | None = None
    output:             ShapeT                 # same shape as per-source
    inputs_hash:        str                    # F13 — hash of per_source inputs
    computed_at:        datetime

class TechniqueResultMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")
    chart_id:            UUID
    technique_id:        str                   # e.g. 'yoga.raja.gaja_kesari' or family-level 'yoga'
    technique_family_id: str
    output_shape_id:     str
    surface:             str                   # 'b2c_chat' | 'astrologer_pro' | 'ultra_ai' | 'api'
    user_mode:           str                   # 'auto' | 'custom' | 'ultra'

class TechniqueResult(BaseModel, Generic[ShapeT]):
    """Canonical envelope emitted by every classical engine."""
    model_config = ConfigDict(extra="forbid")

    metadata:    TechniqueResultMetadata
    per_source:  dict[str, PerSourceEntry[ShapeT]]       # keyed by source_id
    aggregates:  dict[str, AggregateEntry[ShapeT]]       # keyed by strategy_id
```

### 5.3 ClassicalEngine Protocol (refined)

```python
# src/josi/services/classical/engine_base.py

from typing import Protocol, runtime_checkable
from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession

@runtime_checkable
class ClassicalEngine(Protocol):
    """Contract implemented by every per-family engine (yoga, dasa, tajaka, …)."""

    technique_family_id: str
    default_output_shape_id: str

    async def compute_for_source(
        self,
        session: AsyncSession,
        chart_id: UUID,
        source_id: str,
        rule_ids: list[str] | None = None,
    ) -> list[TechniqueComputeRow]: ...

    async def load_cached(
        self,
        session: AsyncSession,
        chart_id: UUID,
        source_id: str | None = None,
        rule_ids: list[str] | None = None,
    ) -> list[TechniqueComputeRow]: ...

    async def assemble_result(
        self,
        session: AsyncSession,
        chart_id: UUID,
        technique_id: str,
        context: "AggregationContext",
    ) -> TechniqueResult:
        """
        1. Fetch per-source rows from technique_compute.
        2. For each configured strategy (from context or default set):
             runner.run_single(per_source, shape_id, strategy, context).
        3. Persist aggregation_event rows.
        4. Return TechniqueResult.
        """
        ...
```

Implementors inherit from `ClassicalEngineBase` (concrete mixin providing `load_cached` and `assemble_result` boilerplate) or implement the Protocol directly.

### 5.4 AggregationStrategy Protocol

```python
# src/josi/services/classical/aggregation/protocol.py

from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol, runtime_checkable

@dataclass(frozen=True)
class AggregationContext:
    """Runtime inputs threaded through every strategy call."""
    surface:    str                              # 'b2c_chat' | 'astrologer_pro' | 'ultra_ai' | 'api'
    user_mode:  str                              # 'auto' | 'custom' | 'ultra'

    # Optional personalization
    astrologer_source_weights: Mapping[str, float] | None = None   # {'bphs': 1.0, 'saravali': 0.7}
    astrologer_preferred_strategy_id: str | None = None

    # Experiment context
    experiment_id:     str | None = None
    experiment_arm_id: str | None = None

    # Seed for deterministic tie-breaking / stochastic ops
    deterministic_seed: bytes | None = None       # derived from inputs_hash; F13

    # Passthrough for future extensions
    extras: Mapping[str, Any] = field(default_factory=dict)


@runtime_checkable
class AggregationStrategy(Protocol):
    """Pluggable aggregation algorithm."""

    strategy_id:            str
    implementation_version: str                    # semver
    supported_shapes:       frozenset[str]

    def aggregate(
        self,
        per_source: Mapping[str, dict],           # source_id → raw result dict (shape-conformant)
        output_shape_id: str,
        context: AggregationContext,
    ) -> dict | None:
        """
        Return the aggregated output payload (still shape-conformant), or None if this strategy
        does not handle output_shape_id (engine will fall through to Strategy D default).

        MUST be deterministic: same inputs → same output.
        MUST NOT mutate per_source.
        MAY raise AggregationError for genuinely invalid inputs (engine catches and logs).
        """
        ...
```

### 5.5 Strategy registry + runner

```python
# src/josi/services/classical/aggregation/registry.py

from importlib.metadata import entry_points

class AggregationStrategyRegistry:
    """Discovers all strategies registered via `josi.aggregation_strategies` entry point."""

    def __init__(self) -> None:
        self._by_id: dict[str, AggregationStrategy] = {}

    def load(self) -> None:
        for ep in entry_points(group="josi.aggregation_strategies"):
            cls = ep.load()
            strat = cls()
            if not isinstance(strat, AggregationStrategy):   # runtime_checkable
                raise StrategyContractError(f"{ep.name} does not implement AggregationStrategy")
            if strat.strategy_id != ep.name:
                raise StrategyContractError(f"entry_point name '{ep.name}' != strategy_id '{strat.strategy_id}'")
            self._by_id[strat.strategy_id] = strat

    def get(self, strategy_id: str) -> AggregationStrategy:
        try: return self._by_id[strategy_id]
        except KeyError: raise UnknownStrategyError(strategy_id)

    def all(self) -> list[AggregationStrategy]:
        return list(self._by_id.values())

    def supporting(self, output_shape_id: str) -> list[AggregationStrategy]:
        return [s for s in self._by_id.values() if output_shape_id in s.supported_shapes]
```

```python
# src/josi/services/classical/aggregation/runner.py

class AggregationRunner:
    def __init__(self, registry: AggregationStrategyRegistry,
                 default_strategy_id: str = "D_hybrid"):
        self._registry = registry
        self._default = default_strategy_id

    async def run_all(
        self,
        session: AsyncSession,
        per_source: Mapping[str, dict],
        metadata: TechniqueResultMetadata,
        context: AggregationContext,
        strategy_ids: list[str] | None = None,
    ) -> dict[str, AggregateEntry]:
        """
        For each strategy_id (or all that support this shape if None), invoke, persist
        aggregation_event, and collect AggregateEntry.
        """
        shape_id = metadata.output_shape_id
        chosen = (strategy_ids
                  or [s.strategy_id for s in self._registry.supporting(shape_id)])
        inputs_hash = hash_inputs(per_source)                   # F13
        context = replace(context, deterministic_seed=inputs_hash.encode())

        results: dict[str, AggregateEntry] = {}
        for sid in chosen:
            strat = self._registry.get(sid)
            if shape_id not in strat.supported_shapes:
                continue
            try:
                output = strat.aggregate(per_source, shape_id, context)
            except AggregationError as e:
                await self._persist_failed_event(session, metadata, sid, strat.implementation_version, str(e))
                continue
            if output is None:
                # strategy opted out; substitute default
                default = self._registry.get(self._default)
                output = default.aggregate(per_source, shape_id, context)
                sid_effective = f"{sid}→{self._default}"
            else:
                sid_effective = sid

            entry = AggregateEntry(
                strategy_id=sid_effective,
                strategy_version=strat.implementation_version,
                experiment_id=context.experiment_id,
                experiment_arm_id=context.experiment_arm_id,
                output=output,
                inputs_hash=inputs_hash,
                computed_at=datetime.now(tz=UTC),
            )
            await self._persist_event(session, metadata, entry)
            results[sid] = entry
        return results
```

### 5.6 Strategy stubs (full impl in E14a)

```python
# src/josi/services/classical/aggregation/strategy_a.py

class MajorityStrategy:
    strategy_id: str = "A_majority"
    implementation_version: str = "1.0.0"
    supported_shapes: frozenset[str] = frozenset({
        "boolean_with_strength", "numeric", "temporal_range", "temporal_event", "categorical",
    })

    def aggregate(self, per_source, output_shape_id, context):
        # Skeleton. Full implementation in E14a.
        if output_shape_id == "boolean_with_strength":
            return self._majority_bool(per_source)
        if output_shape_id == "numeric":
            return self._mean_numeric(per_source)
        if output_shape_id == "temporal_range":
            return self._union_range(per_source)
        return None
```

Strategies B/C/D follow the same pattern; full algorithms deferred to E14a per master spec phasing.

### 5.7 Plugin registration in `pyproject.toml`

```toml
[project.entry-points."josi.aggregation_strategies"]
A_majority   = "josi.services.classical.aggregation.strategy_a:MajorityStrategy"
B_confidence = "josi.services.classical.aggregation.strategy_b:ConfidenceStrategy"
C_weighted   = "josi.services.classical.aggregation.strategy_c:WeightedStrategy"
D_hybrid     = "josi.services.classical.aggregation.strategy_d:HybridStrategy"
```

Registry auto-discovers these on startup.

### 5.8 Contract-compliance test harness

```python
# tests/classical/test_aggregation_protocol.py

@pytest.mark.parametrize("strat", ALL_REGISTERED_STRATEGIES)
def test_strategy_declares_required_attrs(strat: AggregationStrategy):
    assert isinstance(strat.strategy_id, str)
    assert re.match(r"^\d+\.\d+\.\d+", strat.implementation_version)
    assert isinstance(strat.supported_shapes, frozenset)

@pytest.mark.parametrize("strat", ALL_REGISTERED_STRATEGIES)
@pytest.mark.parametrize("shape", ALL_SHAPES)
def test_strategy_is_deterministic(strat, shape):
    if shape not in strat.supported_shapes: pytest.skip()
    per_source = fixture_for(shape)
    ctx = AggregationContext(surface="api", user_mode="auto")
    out1 = strat.aggregate(per_source, shape, ctx)
    out2 = strat.aggregate(per_source, shape, ctx)
    assert out1 == out2

@pytest.mark.parametrize("strat", ALL_REGISTERED_STRATEGIES)
def test_strategy_does_not_mutate_input(strat):
    ...

@pytest.mark.parametrize("strat", ALL_REGISTERED_STRATEGIES)
def test_strategy_output_validates_against_shape_schema(strat):
    """For every shape in supported_shapes, aggregate output must validate against F7 JSON Schema."""
    ...
```

This harness runs for **every** registered strategy automatically — including third-party plugins in P6 open-source era.

## 6. User Stories

### US-F8.1: As an engine developer, I want a single envelope I emit that the AI and UI can consume
**Acceptance:** Import `TechniqueResult`; populate per_source + aggregates; serialize with `.model_dump()`; AI tool-use (F10) deserializes via the same model. No per-family bespoke wrappers.

### US-F8.2: As a product engineer, I want to add Strategy E without touching any engine
**Acceptance:** Create `strategy_e.py` implementing `AggregationStrategy`; add `entry_points` line in `pyproject.toml`; run migration to add row to `aggregation_strategy` dim; restart. Every engine instantly computes Strategy E alongside A/B/C/D. Contract-compliance tests pass automatically.

### US-F8.3: As an experimenter, I want to A/B test Strategy C-v1.0.0 vs Strategy C-v1.1.0
**Acceptance:** Bump Strategy C's `implementation_version` to 1.1.0 on a branch; deploy behind feature flag; events carry both versions during overlap; E14a metrics split by version.

### US-F8.4: As an astrologer in Pro mode, I want my per-source weights to flow into Strategy C
**Acceptance:** Pro-mode request sets `AggregationContext.astrologer_source_weights`; C's output differs from default weights; audit log `aggregation_event.output` reflects those weights (verifiable by replay).

### US-F8.5: As an engineer debugging a stale aggregation, I want byte-identical recompute
**Acceptance:** For any historical `aggregation_event`, given the same `per_source` inputs and `context` (reconstructed from the row), re-running the strategy at the same `implementation_version` produces identical `output`.

### US-F8.6: As an engineer, I want a misbehaving strategy to not break other strategies' outputs
**Acceptance:** Strategy X raises exception; engine logs, writes a failed-status event for X, continues to compute strategies Y and Z; aggregation_event rows for Y and Z are present and valid.

## 7. Tasks

### T-F8.1: Implement `TechniqueResult` + supporting models
- **Definition:** Generic Pydantic models in `technique_result.py` parameterized by `ShapeT` (F7 shape).
- **Acceptance:** `TechniqueResult[BooleanWithStrength]` type-checks under mypy; round-trips via JSON.
- **Effort:** 5 hours
- **Depends on:** F7 complete

### T-F8.2: Refine `ClassicalEngine` Protocol
- **Definition:** Promote F2's scaffold to full Protocol with `assemble_result` method. Provide `ClassicalEngineBase` mixin implementing `load_cached` + `assemble_result` boilerplate.
- **Acceptance:** A dummy engine subclassing the mixin passes `isinstance(engine, ClassicalEngine)`.
- **Effort:** 4 hours
- **Depends on:** T-F8.1, F2

### T-F8.3: Define `AggregationStrategy` Protocol + `AggregationContext`
- **Definition:** Protocol with `strategy_id`, `implementation_version`, `supported_shapes`, `aggregate()`. Frozen dataclass for context.
- **Acceptance:** mypy clean; `runtime_checkable` works; strategy stubs satisfy the Protocol.
- **Effort:** 3 hours
- **Depends on:** T-F8.1

### T-F8.4: Strategy registry via entry_points
- **Definition:** `AggregationStrategyRegistry` with `load`, `get`, `all`, `supporting` methods. Entry in `pyproject.toml`.
- **Acceptance:** After `poetry install`, `registry.load()` discovers all 4 built-in strategies.
- **Effort:** 3 hours
- **Depends on:** T-F8.3

### T-F8.5: `AggregationRunner` with event persistence
- **Definition:** Orchestrates strategy calls; persists `aggregation_event`; handles exceptions per strategy.
- **Acceptance:** Integration test: run 4 strategies on a sample `per_source`; 4 rows in `aggregation_event` with correct `strategy_version`, `inputs_hash`, `output` JSONB.
- **Effort:** 6 hours
- **Depends on:** T-F8.4, F2

### T-F8.6: Strategy stubs (A/B/C/D)
- **Definition:** 4 classes implementing `AggregationStrategy`. Stubs handle at least `boolean_with_strength` correctly (majority/agreement/weighted/hybrid per master spec §1.3). Other shapes return `None` (deferred to E14a).
- **Acceptance:** All 4 registered; each passes contract-compliance test harness; boolean_with_strength outputs match hand-computed fixtures.
- **Effort:** 8 hours
- **Depends on:** T-F8.4

### T-F8.7: Contract-compliance test harness
- **Definition:** Parametrized pytest module that runs invariants (determinism, no-mutation, shape-conformance) on every registered strategy × every shape.
- **Acceptance:** All 4 built-in strategies pass; adding a new strategy to `pyproject.toml` automatically includes it in test sweep.
- **Effort:** 4 hours
- **Depends on:** T-F8.6

### T-F8.8: Test engine demonstrating end-to-end round-trip
- **Definition:** Minimal `FakeYogaEngine` that computes `boolean_with_strength` for 3 fake sources; invoke its `assemble_result`; verify `TechniqueResult` has 3 per_source + 4 aggregate entries; verify 3 `technique_compute` + 4 `aggregation_event` rows persisted.
- **Acceptance:** Integration test green; round-trip serialization (dump → parse) preserves all fields.
- **Effort:** 5 hours
- **Depends on:** T-F8.5, T-F8.6

### T-F8.9: Register strategies in `aggregation_strategy` dim
- **Definition:** Ensure F1's seed YAML has 4 rows matching entry_points keys; lifespan startup verifies 1:1 correspondence between entry_points and dim rows; abort on mismatch.
- **Acceptance:** Fresh DB + install → 4 dim rows + 4 registered plugins; removing one entry_point without updating YAML → startup aborts.
- **Effort:** 2 hours
- **Depends on:** T-F8.4, F1

### T-F8.10: Developer docs
- **Definition:** Add section to `CLAUDE.md`: "Aggregation strategies are plugins. To add one, implement `AggregationStrategy`, add entry_points line, run DB migration to register dim row, deploy."
- **Acceptance:** Docs merged.
- **Effort:** 30 min
- **Depends on:** T-F8.9

## 8. Unit Tests

### 8.1 TechniqueResult model

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_technique_result_generic_type_preserved` | `TechniqueResult[BooleanWithStrength]` with valid payload | parses; `per_source['bphs'].result` is `BooleanWithStrength` instance | generics work |
| `test_technique_result_rejects_wrong_shape` | `TechniqueResult[BooleanWithStrength]` given numeric payload | ValidationError | shape type-safety |
| `test_technique_result_json_roundtrip` | dump → parse | equal object | serialization |
| `test_per_source_empty_allowed` | `per_source={}` | parses (no sources computed) | edge case |
| `test_aggregates_empty_allowed` | `aggregates={}` | parses (no strategies configured) | edge case |
| `test_metadata_required_fields` | missing `chart_id` | ValidationError | required |

### 8.2 AggregationStrategy Protocol conformance

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_stub_a_declares_contract` | MajorityStrategy() | has strategy_id, version, supported_shapes | attr presence |
| `test_stub_b_declares_contract` | ConfidenceStrategy() | same | attr presence |
| `test_stub_c_declares_contract` | WeightedStrategy() | same | attr presence |
| `test_stub_d_declares_contract` | HybridStrategy() | same | attr presence |
| `test_all_stubs_pass_isinstance_check` | each instance | `isinstance(s, AggregationStrategy)` True | structural typing |
| `test_strategy_id_semver` | each strategy | regex matches `^\d+\.\d+\.\d+` | versioning policy |
| `test_entry_point_name_matches_strategy_id` | each `ep.name` | equals `ep.load()().strategy_id` | registration invariant |

### 8.3 Determinism + no-mutation

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_determinism_per_strategy_per_shape` | random per_source × 1000 via Hypothesis | aggregate(x) == aggregate(x) | determinism |
| `test_strategy_does_not_mutate_per_source` | per_source dict with sentinel | unchanged after call | no-mutation |
| `test_dict_order_independence` | per_source in order ['a','b'] vs ['b','a'] | same output | sort_keys semantics |
| `test_seeded_tiebreak_deterministic` | 50/50 bool vote with same seed | same winner twice | seeded RNG |
| `test_seeded_tiebreak_varies_with_seed` | different seeds | possibly different winners (verify determinism per seed) | seed dependency |

### 8.4 AggregationRunner

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_runner_invokes_all_supporting_strategies` | shape supported by A/B/D, not C | 3 aggregation_event rows | shape dispatch |
| `test_runner_substitutes_default_on_none` | strategy returns None for a shape it claims not to support | default (D_hybrid) output used; strategy_id recorded as 'X→D_hybrid' | fallthrough |
| `test_runner_isolates_failing_strategy` | strategy X raises AggregationError | row for X has status='failed'; Y, Z succeed | isolation |
| `test_runner_persists_strategy_version` | strategy X @ v1.2.3 | `aggregation_event.strategy_version` = '1.2.3' | version snapshot |
| `test_runner_computes_inputs_hash` | same per_source twice | identical inputs_hash | F13 hook |
| `test_runner_threads_context_astrologer_weights` | context with weights `{bphs:1.0, saravali:0.5}` | Strategy C uses those weights (verify by output diff vs default weights) | personalization |

### 8.5 Registry + entry_points

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_registry_loads_all_entry_points` | installed package | registry has 4 strategies | discovery |
| `test_registry_rejects_non_protocol` | plugin not implementing Protocol | StrategyContractError | safety |
| `test_registry_rejects_name_mismatch` | entry_point name ≠ strategy_id | StrategyContractError | invariant |
| `test_registry_get_unknown_raises` | `get('X_nonexistent')` | UnknownStrategyError | error handling |
| `test_registry_supporting_filter` | `supporting('numeric_matrix')` | returns only strategies with shape in `supported_shapes` | dispatch |

### 8.6 End-to-end test engine

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_fake_yoga_engine_roundtrip` | FakeYogaEngine.compute_for_source × 3 sources + assemble_result | TechniqueResult with 3 per_source + 4 aggregate; 3 technique_compute + 4 aggregation_event rows in DB | end-to-end integration |
| `test_fake_engine_idempotent_recompute` | assemble_result called twice | second call returns identical TechniqueResult (ON CONFLICT DO NOTHING on technique_compute; new aggregation_event rows both match) | idempotency |
| `test_fake_engine_empty_sources_graceful` | 0 per_source rows | aggregates empty dict; no exception | edge case |

### 8.7 Shape-conformance of aggregate outputs

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_aggregate_output_validates_against_shape_schema` | each (strategy × supported_shape) | `output` validates against F7 JSON Schema for that shape | F7 ↔ F8 parity |
| `test_aggregate_output_parses_as_pydantic_shape` | same | Pydantic parse of output succeeds | Python type-safety |

## 9. EPIC-Level Acceptance Criteria

- [ ] `TechniqueResult[ShapeT]` generic model implemented and type-safe
- [ ] `ClassicalEngine` Protocol (runtime_checkable) refined; `ClassicalEngineBase` mixin provides `load_cached` + `assemble_result` boilerplate
- [ ] `AggregationStrategy` Protocol defined with `strategy_id`, `implementation_version`, `supported_shapes`, `aggregate()`
- [ ] `AggregationContext` dataclass threaded through every strategy call
- [ ] 4 strategy stubs (A/B/C/D) implemented; each handles at least `boolean_with_strength` correctly per master spec §1.3
- [ ] `AggregationStrategyRegistry` discovers plugins via `entry_points`; `pyproject.toml` registers 4 built-ins
- [ ] `AggregationRunner` persists `aggregation_event` rows with correct strategy_version + inputs_hash
- [ ] Contract-compliance test harness auto-runs for every registered strategy
- [ ] Determinism property test (Hypothesis) passes for all built-in strategies
- [ ] No-mutation invariant enforced
- [ ] End-to-end test engine + strategy round-trip succeeds
- [ ] Shape-conformance: every aggregate output validates against its F7 JSON Schema
- [ ] Startup verifies 1:1 correspondence between `entry_points` and `aggregation_strategy` dim rows
- [ ] Unit test coverage ≥ 90% across Protocols, registry, runner, stubs
- [ ] CLAUDE.md updated with "how to add an aggregation strategy"
- [ ] Integration test hits full path: engine → per_source persist → runner → aggregates persist → read via TechniqueResult

## 10. Rollout Plan

- **Feature flag:** none — P0 foundation. Built-in strategies are always loaded. Third-party strategies gated by their own `entry_points` (i.e., package presence).
- **Shadow compute:** N/A at P0.
- **Backfill:** N/A (no existing aggregation_event rows).
- **Rollback:** remove entry_points line from `pyproject.toml` + migration to mark dim row `deprecated_at` → strategy no longer invoked for new computes; existing rows preserved. Code rollback: revert Protocol + Runner; strategies continue to exist but no runner invokes them.

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Strategy non-determinism creeps in (e.g., via `time.time()` or unseeded RNG) | Medium | High (breaks replay + experiments) | Hypothesis property test runs 1000 iterations per strategy × shape; CI blocks merge on failure |
| Plugin conflicts (two packages register same `strategy_id`) | Low | High (ambiguous resolution) | Registry aborts startup on duplicate name |
| `entry_points` not discovered in Docker build | Medium | High (silent fallback to built-ins) | Startup logs list discovered strategies; canary env asserts all 4 present |
| Generic Pydantic model slow at scale | Low | Medium | Benchmark at 100k events/sec; fall back to TypedDict if needed |
| Strategy exceptions swallow bugs | Medium | Medium | Runner writes `aggregation_event` with `status='failed'` + stack trace in details; per-strategy failure alerting |
| Protocol doesn't capture all future strategy needs | Medium | Low | AggregationContext.extras escape hatch; Protocol can be extended additively |
| Dim row ↔ entry_points drift | Medium | Medium | Startup invariant check aborts on mismatch |
| Recompute doesn't produce identical output across strategy version bumps | Certain (design) | Low | By design — new rows written, old preserved; replay uses historical version |

## 12. References

- Master spec: [`docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`](../../../superpowers/specs/2026-04-19-classical-techniques-expansion-design.md) §1.3 (four strategies), §2.1 (compute/aggregation separation), §2.4 (strategy versioning)
- F1 dims: [`F1-star-schema-dimensions.md`](./F1-star-schema-dimensions.md) — `aggregation_strategy` dim rows
- F2 fact tables: [`F2-fact-tables.md`](./F2-fact-tables.md) — `technique_compute`, `aggregation_event` + `ClassicalEngine` Protocol scaffold
- F7 output shapes: [`F7-output-shape-system.md`](./F7-output-shape-system.md) — shape catalog + JSON Schemas
- F9 serving view: [`F9-chart-reading-view-table.md`](./F9-chart-reading-view-table.md) — consumer of `aggregation_event`
- F10 AI tool-use contract: [`F10-typed-ai-tool-use-contract.md`](./F10-typed-ai-tool-use-contract.md) — consumer of `TechniqueResult`
- F13 content-hash provenance: [`F13-content-hash-provenance.md`](./F13-content-hash-provenance.md) — `inputs_hash` derivation
- F17 property-based test harness: [`F17-property-based-test-harness.md`](./F17-property-based-test-harness.md) — Hypothesis integration
- E14a experimentation framework: [`../P1/E14a-experimentation-framework-v1.md`](../P1/E14a-experimentation-framework-v1.md) — full A/B/C/D algorithms + bake-off
- Python typing `Protocol`: https://peps.python.org/pep-0544/
- `importlib.metadata.entry_points`: https://docs.python.org/3/library/importlib.metadata.html
