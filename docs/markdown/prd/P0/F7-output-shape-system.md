---
prd_id: F7
epic_id: F7
title: "Output-shape system with JSON schemas"
phase: P0-foundation
tags: [#extensibility, #correctness]
priority: must
depends_on: [F1, F5]
enables: [F6, F8, F9, E1a, E2a, E4a, E6a, E14a]
classical_sources: []
estimated_effort: 3-4 days
status: draft
author: @agent
last_updated: 2026-04-19
---

# F7 — Output-Shape System with JSON Schemas

## 1. Purpose & Rationale

Every classical technique family emits a result. A yoga rule says "active with strength 0.82." A dasa computation says "Jupiter Mahadasha from 2024-03-14 to 2040-03-14." Ashtakavarga returns a 12×8 grid of bindus. Varshaphala returns an annual summary containing muntha, year lord, and sahams.

Without a **typed, schema-validated output shape system**:
- Engine-to-aggregation-strategy contracts are ad-hoc — Strategy A for yogas and Strategy A for dasa can't share code.
- AI tool-use responses (F10, F11) carry unpredictable payloads; prompt engineering is fragile.
- JSONB columns (`technique_compute.result`, `aggregation_event.output`) accept anything; bugs surface at read time for end-users.
- UI dev must defensively handle "maybe this field exists" — slow product velocity.

This PRD defines the **closed catalog of 10 output shapes** that every classical technique must conform to, the **JSON Schemas** that validate them (Draft 2020-12), the **Pydantic models** that provide Python-native type-safety, and the **seeding** of `output_shape.json_schema` (the dim column F1 left empty).

The catalog is deliberately small. New shapes are *breaking changes* — adding `boolean_with_strength_v2` is an additive non-breaking change; modifying `boolean_with_strength` in place is forbidden.

## 2. Scope

### 2.1 In scope
- Complete catalog of 10 output shapes with precise semantics
- JSON Schema (Draft 2020-12) for each shape
- Pydantic v2 model for each shape (paired 1:1 with the JSON Schema)
- Shape registry: a single Python source-of-truth that YAMLs + DB rows are derived from
- Shape seeder: on startup, writes `output_shape.json_schema` JSONB for each shape
- Versioning policy: shapes are immutable once shipped; breaking changes get new `shape_id`
- Valid + invalid payload fixtures per shape (used as canonical examples in docs and tests)
- Unit tests: valid-payload acceptance, invalid-payload rejection, schema ↔ Pydantic parity
- Developer documentation: "how to add a new shape"

### 2.2 Out of scope
- **Insert-time validation plumbing** — owned by F5 (hooks up the schemas this PRD defines to the `pg_jsonschema` CHECK or app-layer validator).
- **Rule DSL** — owned by F6 (produces rules whose `output_shape_id` points here).
- **Engine-specific result composition** — owned by each engine EPIC (E1a, E2a, E4a, …). Engines emit shapes; this PRD defines them.
- **Aggregation-output shapes** — strategy outputs re-use the same shape catalog (enforced by F8). This PRD does not enumerate separate aggregate shapes.
- **GraphQL types derived from shapes** — deferred; engines expose typed GraphQL per family, not per shape.

### 2.3 Dependencies
- F1 — `output_shape` dim table exists; this PRD fills `json_schema` column
- F5 — consumes schemas from this PRD for DB-level validation
- `pydantic` v2 (present); `jsonschema` or `fastjsonschema` library (needs add for runtime validation in tests)

## 3. Technical Research

### 3.1 Why a closed catalog (not free-form shapes per rule)

Options considered:

| Option | Rejected because |
|---|---|
| **Per-rule unique shape** (every rule declares its own JSON Schema) | Explodes the number of schemas to thousands; aggregation strategies can't be written generically; AI tool-use can't publish a stable contract. |
| **Polymorphic envelope** (one big union schema per technique family) | Collapses type-safety; defeats the point of per-shape aggregation logic. |
| **Two shapes total** (boolean, numeric) with everything else wedged in | Insufficient expressivity — dasa periods are genuinely a temporal hierarchy, not a numeric. |
| **Closed 10-shape catalog** (selected) | Small enough that aggregation strategies (F8) can implement each case explicitly; large enough to cover all classical technique families per master spec §2.2. |

### 3.2 Draft 2020-12 JSON Schema choice

Options:
- Draft 7 — widely supported but missing `unevaluatedProperties`, `prefixItems`, composition improvements.
- Draft 2019-09 — transitional; fewer validators.
- **Draft 2020-12** — latest stable; `prefixItems` (ordered tuples, useful for `[start, end]`), `unevaluatedProperties: false` (strict object closure), unified `$ref` resolution. Pydantic v2's `.model_json_schema()` targets 2020-12.

Validators:
- `pg_jsonschema` extension (Postgres) — supports Draft 2020-12 as of pgx 0.8. F5 picks this path if available.
- `fastjsonschema` (Python) — compiles to Python code, 10× faster than `jsonschema` for hot-path validation. Used in unit tests and fallback app-layer validation.

### 3.3 Pydantic ↔ JSON Schema parity

Pydantic v2 emits Draft 2020-12 JSON Schema via `TypeAdapter(Model).json_schema(mode='serialization')`. We use this as the **single source of truth** for each shape — the Pydantic model is authored by engineers; the JSON Schema is derived mechanically. This prevents drift.

Caveats:
- Pydantic emits `anyOf` for optional fields; equivalent semantics to `null` allowance.
- `Literal` types become `enum` in JSON Schema.
- `confloat(ge=0, le=1)` becomes `{"type": "number", "minimum": 0, "maximum": 1}`.
- `dict[str, Any]` becomes `{"type": "object", "additionalProperties": true}`.
- Pydantic's default `additionalProperties: true` is too permissive; we set `model_config = ConfigDict(extra='forbid')` per model to force closed objects where appropriate.

### 3.4 Versioning policy

Shapes are **immutable once seeded in production**. The rationale is storage-wide: there are millions of `technique_compute.result` rows in each shape's format. Changing the schema breaks retroactive validation and invalidates cached aggregations.

Rules:
- Additive changes (new optional field) — **forbidden in place**. Must be `shape_id + "_v2"`.
- Field removal — forbidden in place. Must be new shape.
- Tightening constraints — forbidden in place. Must be new shape.
- Relaxing constraints — also forbidden in place (breaks the invariant that all historical data validates against the current schema).

When we truly need a change, we introduce `boolean_with_strength_v2` with its own `shape_id`, migrate engines rule-by-rule (bumping each rule's `output_shape_id`), and leave the old shape live for historical compute rows.

### 3.5 Alternatives considered

| Alternative | Rejected because |
|---|---|
| Keep JSON Schemas in YAML files | YAML ↔ Pydantic drift is unavoidable; Pydantic-derived is single-source-of-truth |
| Store schemas only in DB (no Python models) | Loses Python type-safety; tools/aggregators write dicts |
| Use TypedDict instead of Pydantic | No runtime validation; can't derive JSON Schema as cleanly |
| One shape per technique family | Aggregation strategies can't be written generically over shape |

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| Catalog closed or open | Closed (10 shapes) | Aggregation strategies require finite shape enumeration |
| Pydantic or YAML as source-of-truth | Pydantic | Mechanical schema derivation; no drift |
| JSON Schema draft | 2020-12 | Pydantic v2 native; best validator support |
| `additionalProperties` default | `false` (extra='forbid') for top-level objects | Catch typos at validation |
| Immutable shapes | Yes | Storage-layer invariant |
| Mutable `details` escape hatch | Yes, but typed as `dict[str, Any]` | Every shape has `details` for engine-specific enrichment without schema changes |
| Unit of time | All timestamps are `datetime` ISO-8601 UTC | Tzinfo always present; engines must convert local → UTC |
| Numeric precision | `float` (IEEE 754 double) | Postgres JSONB uses double; consistent |
| Null vs missing | Missing means "engine didn't compute this"; null means "engine computed but no value" | Semantic distinction for AI tool-use |

## 5. Component Design

### 5.1 New modules

```
src/josi/schemas/classical/
├── output_shapes/
│   ├── __init__.py                       # registry: SHAPE_REGISTRY dict
│   ├── boolean_with_strength.py
│   ├── numeric.py
│   ├── numeric_matrix.py
│   ├── temporal_range.py
│   ├── temporal_event.py
│   ├── temporal_hierarchy.py
│   ├── structured_positions.py
│   ├── annual_chart_summary.py
│   ├── cross_chart_relations.py
│   └── categorical.py
├── fixtures/
│   └── output_shape_examples.py          # valid + invalid fixtures per shape

src/josi/services/classical/
└── shape_seeder.py                       # upserts output_shape.json_schema at startup
```

### 5.2 Shape registry (single source of truth)

```python
# src/josi/schemas/classical/output_shapes/__init__.py

from typing import Any
from pydantic import BaseModel

SHAPE_REGISTRY: dict[str, type[BaseModel]] = {
    "boolean_with_strength":   BooleanWithStrength,
    "numeric":                 Numeric,
    "numeric_matrix":          NumericMatrix,
    "temporal_range":          TemporalRange,
    "temporal_event":          TemporalEvent,
    "temporal_hierarchy":      TemporalHierarchy,
    "structured_positions":    StructuredPositions,
    "annual_chart_summary":    AnnualChartSummary,
    "cross_chart_relations":   CrossChartRelations,
    "categorical":             Categorical,
}

def json_schema_for(shape_id: str) -> dict[str, Any]:
    model = SHAPE_REGISTRY[shape_id]
    return model.model_json_schema(mode="serialization")
```

### 5.3 Shape catalog — complete definitions

#### 5.3.1 `boolean_with_strength`

Used for: yoga activation, tajaka yoga activation, cross-chart match/no-match.

**Pydantic:**
```python
from pydantic import BaseModel, ConfigDict, Field

class BooleanWithStrength(BaseModel):
    model_config = ConfigDict(extra="forbid")

    active:   bool
    strength: float = Field(..., ge=0.0, le=1.0)
    details:  dict[str, Any] = Field(default_factory=dict)
    reason:   str | None = None          # "Moon debilitated" or "Jupiter in 1st from Moon"
```

**JSON Schema (derived):**
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "BooleanWithStrength",
  "type": "object",
  "additionalProperties": false,
  "required": ["active", "strength"],
  "properties": {
    "active":   {"type": "boolean"},
    "strength": {"type": "number", "minimum": 0.0, "maximum": 1.0},
    "details":  {"type": "object", "additionalProperties": true, "default": {}},
    "reason":   {"anyOf": [{"type": "string"}, {"type": "null"}], "default": null}
  }
}
```

**Valid payloads:**
```json
{"active": true, "strength": 0.82, "details": {"jupiter_sign": 5}, "reason": "Moon in kendra from Jupiter"}
{"active": false, "strength": 0.0}
```

**Invalid payloads:**
```json
{"active": "yes", "strength": 0.5}                          // active must be bool
{"active": true, "strength": 1.5}                           // strength > 1
{"active": true, "strength": 0.5, "typo_key": "oops"}       // additionalProperties: false
{"active": true}                                             // strength required
```

#### 5.3.2 `numeric`

Used for: bhava bala, shadbala totals, any single-value numeric output.

```python
class Numeric(BaseModel):
    model_config = ConfigDict(extra="forbid")

    value:   float
    unit:    str | None = None           # "rupas", "degrees", "years", None
    details: dict[str, Any] = Field(default_factory=dict)
```

**Valid:** `{"value": 487.3, "unit": "rupas"}`, `{"value": 0.0}`

**Invalid:** `{"value": "high"}`, `{}`

#### 5.3.3 `numeric_matrix`

Used for: ashtakavarga bindu grids (12 signs × 8 contributors), sarvashtakavarga, prastarashtaka.

```python
class NumericMatrix(BaseModel):
    model_config = ConfigDict(extra="forbid")

    matrix:     list[list[float]]
    row_labels: list[str]
    col_labels: list[str]
    details:    dict[str, Any] = Field(default_factory=dict)

    @field_validator("matrix")
    @classmethod
    def _rectangular(cls, v: list[list[float]]) -> list[list[float]]:
        if not v: return v
        n = len(v[0])
        if not all(len(row) == n for row in v):
            raise ValueError("matrix must be rectangular")
        return v
```

**Valid:** Ashtakavarga 12×8 grid with row_labels = zodiac signs, col_labels = 7 planets + ascendant.

**Invalid:** non-rectangular matrix; row_labels length != matrix row count (enforced in addition to shape schema, via custom validator; JSON Schema alone cannot express rectangularity, so app-layer validation supplements).

JSON Schema additions:
```json
{
  "properties": {
    "matrix":     {"type": "array", "items": {"type": "array", "items": {"type": "number"}}},
    "row_labels": {"type": "array", "items": {"type": "string"}},
    "col_labels": {"type": "array", "items": {"type": "string"}}
  }
}
```

#### 5.3.4 `temporal_range`

Used for: a single dasa period, a transit window, a muhurta window.

```python
from datetime import datetime

class TemporalRange(BaseModel):
    model_config = ConfigDict(extra="forbid")

    start:   datetime                       # tz-aware required
    end:     datetime                       # tz-aware required
    lord:    str | None = None              # "jupiter", "saturn", etc.
    level:   int | None = Field(default=None, ge=1, le=5)   # 1=MD, 2=AD, 3=PD, 4=SD, 5=PA
    details: dict[str, Any] = Field(default_factory=dict)
```

**Valid:** `{"start": "2024-03-14T00:00:00Z", "end": "2040-03-14T00:00:00Z", "lord": "jupiter", "level": 1}`

**Invalid:** end before start (app-layer validator); naive datetime (timezone required).

#### 5.3.5 `temporal_event`

Used for: eclipse events, Sade Sati entry/exit, planetary ingress, retrograde station.

```python
class TemporalEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    at:         datetime
    event_type: str                         # "sade_sati_entry", "solar_eclipse", ...
    details:    dict[str, Any] = Field(default_factory=dict)
```

**Valid:** `{"at": "2025-09-07T18:11:00Z", "event_type": "lunar_eclipse", "details": {"saros_cycle": 128}}`

#### 5.3.6 `temporal_hierarchy`

Used for: a full dasa tree (MD → AD → PD → SD → PA), Varshaphala sub-period tree.

```python
class TemporalHierarchy(BaseModel):
    model_config = ConfigDict(extra="forbid")

    root_system: str                        # "vimshottari", "yogini", "ashtottari", "chara"
    periods:     list[TemporalRange]        # flat, with `level` distinguishing hierarchy
    details:     dict[str, Any] = Field(default_factory=dict)
```

**Valid:** `{"root_system": "vimshottari", "periods": [{...MD...}, {...AD1...}, {...AD2...}, ...]}`

Design note: flat list with `level` field (rather than nested structure) makes querying and AI tool-use simpler — "give me all level-2 periods active today" becomes a single filter.

#### 5.3.7 `structured_positions`

Used for: Arudhas (A1–A12), Chara Karakas (AK, AmK, BK, …), Upagrahas (Gulika, Mandi, …), Arabic Parts, fixed stars on a chart.

```python
class Position(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name:   str                             # "arudha_lagna", "atmakaraka", "gulika", "part_of_fortune"
    sign:   int | None = Field(default=None, ge=0, le=11)   # 0=Aries
    house:  int | None = Field(default=None, ge=1, le=12)
    degree: float | None = Field(default=None, ge=0.0, lt=30.0)
    lord:   str | None = None
    details: dict[str, Any] = Field(default_factory=dict)

class StructuredPositions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    positions: list[Position]
    details:   dict[str, Any] = Field(default_factory=dict)
```

**Valid:** list of 7 Chara Karakas with name, sign, degree.

#### 5.3.8 `annual_chart_summary`

Used for: Varshaphala (annual solar return) summary emitted by E5.

```python
class Saham(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name:   str                             # "punya", "vidya", "mangala", etc.
    sign:   int = Field(..., ge=0, le=11)
    house:  int = Field(..., ge=1, le=12)
    degree: float = Field(..., ge=0.0, lt=30.0)

class AnnualChartSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    year:               int
    muntha_sign:        int = Field(..., ge=0, le=11)
    muntha_house:       int = Field(..., ge=1, le=12)
    year_lord:          str                 # "sun", "moon", ...
    year_lord_strength: float = Field(..., ge=0.0, le=1.0)
    active_sahams:      list[Saham] = Field(default_factory=list)
    active_yogas:       list[str] = Field(default_factory=list)  # rule_ids
    details:            dict[str, Any] = Field(default_factory=dict)
```

#### 5.3.9 `cross_chart_relations`

Used for: synastry (chart A × chart B); composite chart summary.

```python
class Relation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    from_planet:  str                       # "a.moon"
    to_planet:    str                       # "b.sun"
    relation:     str                       # "conjunction", "trine", "kuta_type_X"
    orb_deg:      float | None = Field(default=None, ge=0.0, le=30.0)
    strength:     float = Field(..., ge=0.0, le=1.0)
    details:      dict[str, Any] = Field(default_factory=dict)

class CrossChartRelations(BaseModel):
    model_config = ConfigDict(extra="forbid")

    chart_a_id: str
    chart_b_id: str
    relations:  list[Relation]
    summary:    dict[str, Any] = Field(default_factory=dict)
```

#### 5.3.10 `categorical`

Used for: "auspicious / inauspicious / neutral"; nakshatra category; temperament type.

```python
class Categorical(BaseModel):
    model_config = ConfigDict(extra="forbid")

    category:   str
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    alternatives: list[str] = Field(default_factory=list)
    details:    dict[str, Any] = Field(default_factory=dict)
```

### 5.4 Shape seeder

```python
# src/josi/services/classical/shape_seeder.py

from josi.schemas.classical.output_shapes import SHAPE_REGISTRY, json_schema_for
from josi.models.classical.output_shape import OutputShape

class ShapeSeeder:
    """On startup, upsert each registered shape's JSON Schema into output_shape.json_schema."""

    async def seed_all(self, session: AsyncSession) -> SeedReport:
        for shape_id in SHAPE_REGISTRY:
            schema = json_schema_for(shape_id)
            await self._upsert(session, shape_id, schema)

    async def _upsert(self, session: AsyncSession, shape_id: str, schema: dict) -> None:
        """Upsert. If the row exists with a different schema, log WARNING and refuse update
        (immutability invariant). Require a new shape_id for changes."""
```

Runs in FastAPI lifespan **after** F1's `DimensionLoader` (which ensures `output_shape` rows exist with empty schemas) and **before** F6's `RuleRegistryLoader` (which needs populated schemas to validate rule output_shape_id references).

### 5.5 Immutability enforcement

```python
async def _upsert(self, session: AsyncSession, shape_id: str, new_schema: dict) -> None:
    existing = await session.get(OutputShape, shape_id)
    if existing is None:
        # first-ever seed
        ...
    else:
        if existing.json_schema and existing.json_schema != {}:
            if _canonical(existing.json_schema) != _canonical(new_schema):
                raise ShapeImmutabilityError(
                    f"output_shape '{shape_id}' already exists with a different schema. "
                    f"Shapes are immutable; introduce a new shape_id (e.g. '{shape_id}_v2') instead."
                )
        else:
            # empty placeholder from F1 seed; fill it
            existing.json_schema = new_schema
```

`_canonical` sorts keys to compare schemas order-independently.

### 5.6 Test fixture library

```python
# src/josi/schemas/classical/fixtures/output_shape_examples.py

VALID_EXAMPLES: dict[str, list[dict]] = {
    "boolean_with_strength": [
        {"active": True,  "strength": 0.82, "reason": "Moon in kendra from Jupiter"},
        {"active": False, "strength": 0.0},
    ],
    "numeric": [
        {"value": 487.3, "unit": "rupas"},
        {"value": 0.0},
    ],
    ...
}

INVALID_EXAMPLES: dict[str, list[tuple[dict, str]]] = {
    "boolean_with_strength": [
        ({"active": "yes", "strength": 0.5}, "active must be bool"),
        ({"active": True,  "strength": 1.5}, "strength out of range"),
        ({"active": True,  "strength": 0.5, "typo_key": "oops"}, "additionalProperties"),
        ({"active": True}, "strength required"),
    ],
    ...
}
```

These fixtures are consumed by:
- Unit tests (validate every sample)
- API documentation (embedded as examples in OpenAPI spec)
- AI tool-use response templates (F10 / F11)

## 6. User Stories

### US-F7.1: As an engine developer, I want a typed Pydantic model for each output shape
**Acceptance:** `from josi.schemas.classical.output_shapes import BooleanWithStrength` works; `BooleanWithStrength(active=True, strength=0.82).model_dump()` produces a valid payload.

### US-F7.2: As a DB engineer, I want the `output_shape.json_schema` column populated after startup
**Acceptance:** After app startup, `SELECT shape_id, json_schema FROM output_shape` returns 10 rows, each with a non-empty Draft 2020-12 JSON Schema.

### US-F7.3: As an engineer, I want invalid payloads to fail validation at the shape boundary
**Acceptance:** Every `INVALID_EXAMPLES` fixture raises `ValidationError` via Pydantic and fails `jsonschema.validate` against the DB-stored schema.

### US-F7.4: As an architect, I want to prevent accidental schema changes
**Acceptance:** Modifying `BooleanWithStrength` in Python without renaming causes `ShapeImmutabilityError` at startup. The PR author must either revert or introduce `boolean_with_strength_v2`.

### US-F7.5: As an AI engineer, I want every shape's JSON Schema available for prompt engineering
**Acceptance:** `GET /api/v1/classical/output-shapes/boolean_with_strength` returns the Draft 2020-12 JSON Schema, consumable by Claude as tool-use schema.

### US-F7.6: As an analytics user, I want to query every `technique_compute.result` in a given shape
**Acceptance:** `SELECT * FROM technique_compute tc JOIN output_shape os ON tc.output_shape_id = os.shape_id WHERE os.shape_id = 'numeric_matrix'` returns all ashtakavarga-style results.

## 7. Tasks

### T-F7.1: Implement 10 Pydantic models
- **Definition:** One module per shape with exact fields above; `model_config = ConfigDict(extra="forbid")`; custom validators for rectangularity (matrix) and temporal order.
- **Acceptance:** All 10 models importable; `model_json_schema(mode='serialization')` produces Draft 2020-12; mypy clean.
- **Effort:** 8 hours
- **Depends on:** F1 complete

### T-F7.2: Build `SHAPE_REGISTRY` and `json_schema_for()`
- **Definition:** Single-source-of-truth dict; helper to extract schema.
- **Acceptance:** `list(SHAPE_REGISTRY.keys())` matches the 10 `shape_id`s seeded in F1.
- **Effort:** 1 hour
- **Depends on:** T-F7.1

### T-F7.3: ShapeSeeder service + immutability guard
- **Definition:** On startup, upsert each shape's schema. Raise `ShapeImmutabilityError` if existing non-empty schema differs.
- **Acceptance:** First run populates 10 rows; second run is no-op; manually corrupting a schema in code then restarting raises immutability error.
- **Effort:** 4 hours
- **Depends on:** T-F7.2

### T-F7.4: Wire ShapeSeeder into FastAPI lifespan
- **Definition:** Lifespan ordering: F1 DimensionLoader → F7 ShapeSeeder → F6 RuleRegistryLoader.
- **Acceptance:** Fresh DB starts up with all three steps; ordering verified by log order.
- **Effort:** 1 hour
- **Depends on:** T-F7.3

### T-F7.5: Fixture library
- **Definition:** `VALID_EXAMPLES` and `INVALID_EXAMPLES` for all 10 shapes; at least 2 valid + 3 invalid per shape.
- **Acceptance:** Exports are importable; each example runs through validation tests.
- **Effort:** 4 hours
- **Depends on:** T-F7.1

### T-F7.6: Unit tests — Pydantic + jsonschema parity
- **Definition:** Test matrix: for each shape × each valid sample, Pydantic parse succeeds AND `fastjsonschema.compile(schema)(sample)` succeeds. For each invalid sample, both fail with matching reason (string match on schema path).
- **Acceptance:** All tests green; parity invariant holds for all 10 shapes.
- **Effort:** 4 hours
- **Depends on:** T-F7.5

### T-F7.7: Public API endpoint
- **Definition:** `GET /api/v1/classical/output-shapes` (list), `GET /api/v1/classical/output-shapes/{shape_id}` (fetch schema). Read-only. No auth required for P0 (public taxonomy).
- **Acceptance:** Endpoints return expected payloads; OpenAPI spec documents them.
- **Effort:** 2 hours
- **Depends on:** T-F7.3

### T-F7.8: Developer docs
- **Definition:** Short addition to `CLAUDE.md`: "Output shapes are closed; new shape = new `shape_id`. To propose a new shape, add Pydantic model in `src/josi/schemas/classical/output_shapes/` and register in `SHAPE_REGISTRY`."
- **Acceptance:** CLAUDE.md updated; PR reviewed.
- **Effort:** 30 min
- **Depends on:** T-F7.3

## 8. Unit Tests

### 8.1 Pydantic models — valid payloads

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_bool_with_strength_valid_minimal` | `{"active": True, "strength": 0.0}` | parses | minimal valid |
| `test_bool_with_strength_valid_full` | `{"active": True, "strength": 0.82, "details": {"k": "v"}, "reason": "…"}` | parses | full valid |
| `test_numeric_valid_no_unit` | `{"value": 12.5}` | parses | unit optional |
| `test_numeric_matrix_rectangular` | 12×8 matrix | parses | shape invariant |
| `test_temporal_range_valid` | tz-aware start < end | parses | basic |
| `test_temporal_event_valid` | tz-aware `at` | parses | basic |
| `test_temporal_hierarchy_valid_vimshottari` | 1 MD + 9 ADs + 81 PDs | parses | hierarchy depth |
| `test_structured_positions_valid_arudhas` | 12 Arudhas | parses | typical arudha output |
| `test_annual_chart_summary_valid` | full Varshaphala summary | parses | E5 contract |
| `test_cross_chart_relations_valid_synastry` | 10 inter-chart aspects | parses | synastry shape |
| `test_categorical_valid_with_confidence` | `{"category": "auspicious", "confidence": 0.7}` | parses | basic |

### 8.2 Pydantic models — invalid payloads

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_bool_active_must_be_bool` | `active: "yes"` | ValidationError | type-safety |
| `test_bool_strength_range` | `strength: 1.5` | ValidationError | range constraint |
| `test_bool_extra_key_forbidden` | extra `typo_key` | ValidationError | additionalProperties: false |
| `test_bool_strength_required` | `{"active": true}` | ValidationError | required |
| `test_numeric_matrix_non_rectangular` | rows of unequal length | ValidationError | custom validator |
| `test_temporal_range_naive_datetime` | naive datetime | ValidationError | tz required |
| `test_temporal_range_end_before_start` | end < start | ValidationError | semantic validator |
| `test_temporal_hierarchy_empty_periods` | `periods: []` | parses (acceptable "no periods found") | sanity — not a failure mode |
| `test_position_degree_30_excluded` | `degree: 30.0` | ValidationError | must be < 30 |
| `test_position_house_out_of_range` | `house: 13` | ValidationError | range |
| `test_saham_invalid_sign` | `sign: 12` | ValidationError | range 0..11 |
| `test_cross_chart_relation_strength_range` | `strength: -0.1` | ValidationError | range |

### 8.3 JSON Schema derivation — parity with Pydantic

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_every_shape_emits_draft_2020_12` | `json_schema_for(shape_id)` for all 10 | `$schema` points at 2020-12 URI | draft version |
| `test_every_shape_has_required_fields` | schema per shape | `required` array non-empty where applicable | schema completeness |
| `test_every_schema_validates_every_valid_fixture` | `fastjsonschema.compile(schema)(fixture)` | passes for all VALID_EXAMPLES | parity |
| `test_every_schema_rejects_every_invalid_fixture` | same, with INVALID_EXAMPLES | fails for all | parity |
| `test_pydantic_and_jsonschema_agree_on_extras` | extra-key fixture | both reject | closed-object enforcement |

### 8.4 ShapeSeeder

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_seeder_populates_empty_rows` | F1-seeded rows with `json_schema={}` | all 10 rows updated with real schemas | startup happy path |
| `test_seeder_idempotent` | second run | 0 changes | idempotency |
| `test_seeder_rejects_schema_drift` | existing row has schema A; registry emits schema B | raises `ShapeImmutabilityError` | immutability |
| `test_seeder_fills_missing_shape` | F1 seed missing one shape_id (rare, e.g. added to registry not yet to YAML) | creates new `output_shape` row | forward-compat |
| `test_seeder_preserves_display_name` | existing display_name from F1 | not overwritten | concern separation |

### 8.5 API endpoint

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_list_output_shapes` | `GET /api/v1/classical/output-shapes` | 10 shape_ids + display_names | catalog read |
| `test_get_output_shape_schema` | `GET /.../boolean_with_strength` | Draft 2020-12 schema | AI tool-use contract |
| `test_get_output_shape_unknown_404` | `GET /.../made_up` | 404 | error handling |

## 9. EPIC-Level Acceptance Criteria

- [ ] All 10 Pydantic models implemented with `extra="forbid"` and appropriate validators
- [ ] `SHAPE_REGISTRY` is the single source of truth; no divergent schemas elsewhere
- [ ] `ShapeSeeder` populates `output_shape.json_schema` JSONB for all 10 shapes on startup
- [ ] Immutability guard: attempting to mutate an existing shape's schema raises `ShapeImmutabilityError`
- [ ] Every shape has ≥ 2 valid + ≥ 3 invalid fixture examples
- [ ] Every valid fixture passes both Pydantic parse and DB-stored JSON Schema validation
- [ ] Every invalid fixture fails both
- [ ] `GET /api/v1/classical/output-shapes` and `/{shape_id}` endpoints live and documented in OpenAPI
- [ ] Unit test coverage ≥ 95% across all shapes
- [ ] Integration test: compute a `BooleanWithStrength` via a dummy engine → insert into `technique_compute` → read back → re-validate against schema → pass
- [ ] CLAUDE.md updated with "how to add a new shape" guidance
- [ ] Golden chart suite passes (no shape-related regressions)

## 10. Rollout Plan

- **Feature flag:** none — P0 foundation.
- **Shadow compute:** N/A.
- **Backfill:** N/A (F1 seeded placeholder rows; this PRD fills them in).
- **Rollback:** `alembic downgrade` would drop `output_shape`; since F7 only writes to an existing column, a code-only rollback reverts to the F1 state (empty schemas) — no data destruction. Safe at P0.

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Pydantic emits schema in slightly different Draft version than expected | Low | Medium | CI test asserts `$schema` URI equals `https://json-schema.org/draft/2020-12/schema` |
| `extra="forbid"` breaks forward compatibility when adding optional fields | High (happens naturally) | Medium | Per immutability policy, every addition is a new shape_id; no in-place adds |
| Matrix-shape rectangularity cannot be expressed in pure JSON Schema | Certain | Low | Custom Pydantic validator + app-layer check; JSON Schema handles the common "array of arrays of numbers" case |
| `details` escape hatch becomes dumping ground | Medium | Low | Keep field explicitly untyped; code review enforces "use details only for engine-internal enrichment, not for fields AI tools will query" |
| `fastjsonschema` and Postgres `pg_jsonschema` disagree on edge cases | Low | Medium | Canonical test suite runs both validators on every fixture in CI |
| Shape catalog too small; rules want a custom shape | Medium | Low | Review process at F6 load-time rejects rules referencing unknown shapes; shape additions require PRD amendment + new shape_id |
| Developers mutate shape in place | High (easy mistake) | High (breaks historical rows) | Immutability guard in ShapeSeeder aborts startup on schema drift |

## 12. References

- Master spec: [`docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`](../../../superpowers/specs/2026-04-19-classical-techniques-expansion-design.md) §2.2 (output shapes per technique family), §3 (AI tool-use contract)
- F1 dim tables: [`F1-star-schema-dimensions.md`](./F1-star-schema-dimensions.md)
- F2 fact tables: [`F2-fact-tables.md`](./F2-fact-tables.md)
- F5 JSON Schema validation at insert: [`F5-json-schema-validation.md`](./F5-json-schema-validation.md)
- F6 Rule DSL: [`F6-rule-dsl-yaml-loader.md`](./F6-rule-dsl-yaml-loader.md)
- F8 TechniqueResult + AggregationStrategy: [`F8-technique-result-aggregation-protocol.md`](./F8-technique-result-aggregation-protocol.md)
- JSON Schema Draft 2020-12: https://json-schema.org/draft/2020-12/schema
- Pydantic v2 schema generation: https://docs.pydantic.dev/latest/concepts/json_schema/
- `fastjsonschema` library: https://horejsek.github.io/python-fastjsonschema/
