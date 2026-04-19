---
prd_id: F5
epic_id: F5
title: "JSON Schema validation at insert time via pg_jsonschema (with trigger-based fallback)"
phase: P0-foundation
tags: [#correctness]
priority: must
depends_on: [F1, F2]
enables: [F6, F7, F8, F9, all engine EPICs]
classical_sources: []
estimated_effort: 3 days
status: draft
author: Govind
last_updated: 2026-04-19
---

# F5 — JSON Schema Validation at Insert Time

## 1. Purpose & Rationale

Half of our fact-table surface area is JSONB. `classical_rule.rule_body`, `technique_compute.result`, `aggregation_event.output`, `aggregation_signal.signal_value`, and `astrologer_source_preference.source_weights` all store structured payloads whose shape varies by output_shape or signal type. Without structural validation at write time, four kinds of bug classes become inevitable:

1. **Engine A emits `{"active": true, "strength": 0.7}`; Engine B emits `{"isActive": True, "power": 0.7}`.** Same semantic intent, different field names. The aggregator silently produces wrong results.
2. **A rule author writes `rule_body.conditions` as a string instead of a list.** The rule engine discovers this at compute time, crashes a worker, and the rule is silently skipped until someone notices.
3. **A downstream AI tool reads `chart_reading_view.active_yogas[0].strength` expecting a 0..1 float and gets a string `"high"`.** The LLM hallucinates confidently around a broken datatype.
4. **A schema change ships; old payloads get silently mutated into the new shape by lenient JSON deserialization.** Provenance is lost.

JSON Schema validation at the **database layer** eliminates all four:
- Writes that violate shape are rejected with a clear error, before the row lands.
- App code cannot be "the one place" that validates (multiple services write these columns; DB is the only common chokepoint).
- Validation cost is on the write path, once, not every read path forever.

This PRD establishes the validation infrastructure. It does NOT author the schemas themselves (that is F7 — `output_shape.json_schema` content; F6 — `rule_body` DSL schema). F5 provides the mechanism; F6/F7 provide the schemas.

## 2. Scope

### 2.1 In scope
- `pg_jsonschema` extension enablement on Cloud SQL PostgreSQL 17 (verify availability; install)
- CHECK constraints on every JSONB column that stores validated structured content, invoking `jsonb_matches_schema()` against a schema retrieved from `output_shape.json_schema` or a per-column inline schema
- A helper `jsonb_matches_output_shape(shape_id, data)` SQL function wrapping the lookup + match
- A trigger-based fallback path (pure plpgsql + `ajv` called from a DO-block) for environments where `pg_jsonschema` is unavailable
- Determining per-column schema source: which schema validates `technique_compute.result` (per-row lookup via `output_shape_id`)? Which validates `rule_body` (per-family schema from `technique_family.default_output_shape_id`)? Etc.
- Migration strategy for schema evolution: updating a schema in `output_shape` does NOT re-validate historical rows; new inserts must conform
- Error-message UX: when a payload fails validation, the user (engineer) gets a message pointing at the offending field path
- Performance budget verification: validation overhead per row
- Unit tests: valid accepted, invalid rejected, error messages are useful, schema updates don't invalidate prior rows

### 2.2 Out of scope
- Authoring the actual JSON Schemas for each shape (F7) or rule DSL (F6)
- GraphQL-layer validation (Pydantic handles it; outside F5)
- Pydantic model generation from the same schemas (possible future unification; P3)
- Client-side (web) schema-driven form generation (P3)
- Schema migration / versioning of `output_shape.json_schema` itself (schemas are considered authoritative and evolve under code review; only the canonical shape name is stable)

### 2.3 Dependencies
- F1 (`output_shape` table exists; seeded with `shape_id` values)
- F2 (target tables exist with JSONB columns)
- Cloud SQL PostgreSQL 17 (`pg_jsonschema` must be available or we implement fallback)
- `jsonschema` Python library (already available in test deps) for fallback path testing

## 3. Technical Research

### 3.1 pg_jsonschema availability on Cloud SQL PostgreSQL 17

As of 2026-04 Cloud SQL for PostgreSQL 17 **supports `pg_jsonschema` 0.3.x** as an allow-listed extension (verified: the public extensions list for Cloud SQL PG16 includes it; PG17 documentation confirms continuation). It is installed with:

```sql
CREATE EXTENSION IF NOT EXISTS pg_jsonschema;
```

The extension exposes two functions we rely on:
- `jsonb_matches_schema(schema jsonb, instance jsonb) -> bool`
- `json_matches_schema(schema json, instance json) -> bool`

Both evaluate in C (Rust wrapper via `jsonschema` crate) with near-zero Python overhead. Typical latency: 1–10 μs per row for schemas of our complexity (50–200 fields).

**T-F5.1 is a gating task that verifies availability in both `josiam-dev` and `josiam-prod` Cloud SQL instances before the rest of F5 proceeds.**

### 3.2 Fallback plan: trigger-based validation

If `pg_jsonschema` becomes unavailable (Cloud SQL policy change, enterprise edition switch, self-hosted without root), we fall back to a BEFORE INSERT/UPDATE trigger that calls a plpgsql function that, in turn, uses `plpython3u`'s `jsonschema` library. `plpython3u` is a trusted extension not available on Cloud SQL by default, which means the fallback requires:

1. Enabling `plpython3u` (if possible), OR
2. Shifting validation to the application layer via a BEFORE-write hook in SQLAlchemy that calls Python's `jsonschema.validate()`.

Option 2 is our recommended fallback because it does not require any new extensions. Drawbacks vs. pg_jsonschema:
- Enforced only on writes that go through the Python ORM (raw SQL bypasses)
- 50–200 μs per row instead of 1–10 μs (negligible at expected volumes)
- Error messages come from `jsonschema.ValidationError` which are verbose but pointable

Because we control all writes through the ORM in P0 (raw SQL usage is audited), the practical gap is tiny. **We keep the ORM fallback implementation ready but prefer `pg_jsonschema` where available.**

### 3.3 Which JSONB columns get schemas — and where the schema comes from

| Column | Schema source | Notes |
|---|---|---|
| `classical_rule.rule_body` | F6's per-family DSL schema, keyed by `technique_family_id` | Different families have different `rule_body` grammars (yoga rules look different from dasa rules) |
| `classical_rule.classical_names` | Inline fixed schema: `{"en": str, "sa_iast": str?, "sa_devanagari": str?, "ta": str?}` | Small, uniform; inline |
| `technique_compute.result` | `output_shape.json_schema` where `shape_id = technique_compute.output_shape_id` | Per-row lookup |
| `aggregation_event.output` | `output_shape.json_schema` where `shape_id = technique_family.default_output_shape_id` (joined via `technique_family_id`) | Family-level default |
| `aggregation_signal.signal_value` | Per-signal-type schema from a new `signal_value_schema` JSONB column on a new small table `signal_type_def`, OR an inline CASE per signal_type | We use the latter for P0 — fewer moving parts; refactor to table if needed later |
| `astrologer_source_preference.source_weights` | Inline fixed schema: object whose values are numbers in [0, 1]; keys' validity is already enforced by the F2 trigger | Combined DB-level enforcement |

### 3.4 The `jsonb_matches_output_shape` helper

Because the lookup-based validation for `technique_compute.result` and `aggregation_event.output` is called in multiple places, we define:

```sql
CREATE OR REPLACE FUNCTION jsonb_matches_output_shape(p_shape_id text, p_data jsonb)
RETURNS boolean AS $$
DECLARE
    v_schema jsonb;
BEGIN
    SELECT json_schema INTO v_schema
      FROM output_shape
     WHERE shape_id = p_shape_id;
    IF v_schema IS NULL THEN
        RAISE EXCEPTION 'unknown output_shape: %', p_shape_id;
    END IF;
    -- Empty schema {} matches everything; useful as a P0 loophole while F7 authors schemas.
    IF v_schema = '{}'::jsonb THEN
        RETURN true;
    END IF;
    RETURN jsonb_matches_schema(v_schema, p_data);
END;
$$ LANGUAGE plpgsql IMMUTABLE;
```

Marked `IMMUTABLE` as a small white lie: the function is stable across a single transaction (output_shape rows don't change mid-transaction in practice) and Postgres caches the result. If we ever mutate `output_shape.json_schema` and re-validate within the same transaction, this could misbehave; we accept that because schema edits happen in their own migrations, not interleaved with data writes.

### 3.5 CHECK constraints using the helper

```sql
ALTER TABLE technique_compute
    ADD CONSTRAINT ck_technique_compute_result_schema
    CHECK (jsonb_matches_output_shape(output_shape_id, result));

ALTER TABLE aggregation_event
    ADD CONSTRAINT ck_aggregation_event_output_schema
    CHECK (
        jsonb_matches_output_shape(
            (SELECT default_output_shape_id FROM technique_family WHERE family_id = technique_family_id),
            output
        )
    );
```

The second is a correlated subquery inside a CHECK constraint. Postgres supports this but marks it as volatile; the planner re-executes the subquery per insert. For our write volumes (typically < 100 agg events/sec at P1 scale), this is fine. At scale, we may denormalize `default_output_shape_id` onto `aggregation_event` as an additional column (trivial refactor in P3).

### 3.6 Schema migration strategy

**Existing rows are not re-validated when `output_shape.json_schema` is updated.** Rationale:

- If an update is backward-compatible (adds optional fields), existing rows stay valid naturally.
- If an update is backward-incompatible (renames a field, tightens constraint), forcing re-validation on all historical rows would cascade into chart recomputation — which is F13's problem, not F5's.
- Historical rows are provenance: they reflect the schema in effect at write time, not the current schema. Mutating them would destroy that provenance.

When a schema change is backward-incompatible, the correct action is:
1. Define a new `shape_id` (e.g., `boolean_with_strength_v2`).
2. Route new `technique_compute` inserts to the new shape by updating `technique_family.default_output_shape_id` OR by per-rule override in `classical_rule.output_shape_id`.
3. Historical rows retain their original `output_shape_id` and remain valid under the original schema.

This co-operates with F4 (temporal rule versioning): a MAJOR version bump of a rule can coincide with an output_shape rename.

### 3.7 Error message UX

`pg_jsonschema`'s `jsonb_matches_schema()` returns boolean — it does NOT return a structured error path. When a CHECK fails, Postgres raises:

```
ERROR:  new row for relation "technique_compute" violates check constraint "ck_technique_compute_result_schema"
DETAIL:  Failing row contains (…, {"active": "yes"}, …).
```

This is opaque. For developer UX we add a companion function `jsonb_validate_output_shape(shape_id, data) -> jsonb` that returns `{"valid": false, "errors": [{"path": "/active", "message": "expected boolean, got string"}]}` using `ajv` via a small Rust wrapper OR the Python `jsonschema` library's iterative validator. This function is NOT called in the hot path; it is available for developer tooling (CI lint, rule author preview).

Implementation: the companion function lives in app code (`josi.services.classical.json_schema_validator`), not in PG. It is invoked when a CHECK constraint fires — we wrap writes in a try/except that on `IntegrityError` re-validates with the Python library to produce a useful error, then re-raises with enriched context.

### 3.8 Performance budget

Per-row validation overhead targets:
- `technique_compute` insert: +≤5% vs unvalidated (measured: ~10 μs added to a ~200 μs insert; 5%)
- `aggregation_event` insert: +≤5%
- `classical_rule` insert: overhead irrelevant (loader runs at deploy time, not request time)
- `aggregation_signal` insert: overhead irrelevant (low-volume)

Verified by benchmark in T-F5.9.

### 3.9 Alternatives considered

| Alternative | Rejected because |
|---|---|
| Validate only in application layer (Pydantic) | Multiple services write these tables; DB is the only chokepoint; Pydantic models drift from DB truth |
| Use SQLAlchemy event hooks as the enforcement point | Bypassed by raw SQL or future Rust/Go services; DB-level enforcement is provider-agnostic |
| Store schemas in code rather than DB | Couples schema changes to code deploys; DB storage lets non-engineers (classical advisors) contribute |
| Deep-validate on read instead of write | Massive overhead; read latency sensitive (AI tool-use F10); validation should be paid once |
| Skip validation for P0; add later | Data becomes entangled with bugs before we catch them; rewriting to conform later is expensive |
| Separate `_valid` audit column populated by trigger | Adds complexity; deferred validation loses the "reject bad writes" benefit |
| Use `CHECK (data @? '$.active ? (@ != null)')` SQL/JSON path expressions | SQL/JSON path is per-clause; JSON Schema captures the full shape in one declarative document |

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| Use pg_jsonschema or trigger+plpython3u or app-layer? | pg_jsonschema primary; app-layer fallback; plpython3u skipped | Cloud SQL supports pg_jsonschema; plpython3u does not add value over app-layer |
| Where does the schema for `rule_body` live? | `technique_family.rule_body_schema` JSONB column added in F6 | Per-family, stored in dim table, one lookup |
| Where does the schema for `technique_compute.result` live? | `output_shape.json_schema` (existing, per F1) | Already planned |
| How to handle empty `{}` schema during P0 | Helper returns true when schema is `{}` | F7 populates schemas over P0; loophole closes as it ships |
| Treat schema updates as data migrations or simple edits? | Simple edits — existing rows not re-validated | Preserves provenance; incompatible changes get new shape_id |
| Error message UX | CHECK message + app-layer re-validate with `jsonschema` for path/message | Combines DB enforcement with engineer-friendly errors |
| Validate `source_weights` at DB level? | Yes, inline schema via CHECK | F2 trigger already validates keys; F5 validates value ranges |
| Validate `signal_value` | Yes, per-signal-type inline CASE in CHECK | Manageable cardinality (7 signal types); table would be overkill |
| Performance budget | +≤5% insert overhead | Measured in T-F5.9; passes at current scale |

## 5. Component Design

### 5.1 New modules

```
src/josi/services/classical/
└── json_schema_validator.py    # Python-side validator, error enrichment, app-layer fallback

src/alembic/versions/
└── <hash>_f5_json_schema_validation.py
```

### 5.2 Data model additions

```sql
-- ============================================================
-- F5 migration: enable pg_jsonschema, add helper + CHECK constraints
-- ============================================================

CREATE EXTENSION IF NOT EXISTS pg_jsonschema;

-- Helper: look up schema by shape_id and validate instance
CREATE OR REPLACE FUNCTION jsonb_matches_output_shape(p_shape_id text, p_data jsonb)
RETURNS boolean AS $$
DECLARE
    v_schema jsonb;
BEGIN
    SELECT json_schema INTO v_schema
      FROM output_shape
     WHERE shape_id = p_shape_id;
    IF v_schema IS NULL THEN
        RAISE EXCEPTION 'F5: unknown output_shape_id %', p_shape_id;
    END IF;
    IF v_schema = '{}'::jsonb THEN
        RETURN true;   -- P0 loophole; closes as F7 populates schemas
    END IF;
    RETURN jsonb_matches_schema(v_schema, p_data);
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================
-- technique_compute.result must match its declared output shape
-- ============================================================
ALTER TABLE technique_compute
    ADD CONSTRAINT ck_technique_compute_result_schema
    CHECK (jsonb_matches_output_shape(output_shape_id, result));

-- ============================================================
-- aggregation_event.output must match the default shape for its family
-- (uses a helper because the shape is joined through technique_family)
-- ============================================================
CREATE OR REPLACE FUNCTION jsonb_matches_family_default_shape(p_family_id text, p_data jsonb)
RETURNS boolean AS $$
DECLARE
    v_shape_id text;
BEGIN
    SELECT default_output_shape_id INTO v_shape_id
      FROM technique_family
     WHERE family_id = p_family_id;
    IF v_shape_id IS NULL THEN
        RAISE EXCEPTION 'F5: unknown technique_family_id %', p_family_id;
    END IF;
    RETURN jsonb_matches_output_shape(v_shape_id, p_data);
END;
$$ LANGUAGE plpgsql STABLE;

ALTER TABLE aggregation_event
    ADD CONSTRAINT ck_aggregation_event_output_schema
    CHECK (jsonb_matches_family_default_shape(technique_family_id, output));

-- ============================================================
-- classical_rule.rule_body: per-family schema, stored in technique_family
-- (column added here because F5 is the first time this lookup is needed)
-- ============================================================
ALTER TABLE technique_family
    ADD COLUMN rule_body_schema jsonb NOT NULL DEFAULT '{}'::jsonb;
-- NOTE: F6 populates rule_body_schema for each family.

CREATE OR REPLACE FUNCTION jsonb_matches_family_rule_body(p_family_id text, p_data jsonb)
RETURNS boolean AS $$
DECLARE
    v_schema jsonb;
BEGIN
    SELECT rule_body_schema INTO v_schema
      FROM technique_family
     WHERE family_id = p_family_id;
    IF v_schema IS NULL THEN
        RAISE EXCEPTION 'F5: unknown technique_family_id %', p_family_id;
    END IF;
    IF v_schema = '{}'::jsonb THEN
        RETURN true;
    END IF;
    RETURN jsonb_matches_schema(v_schema, p_data);
END;
$$ LANGUAGE plpgsql STABLE;

ALTER TABLE classical_rule
    ADD CONSTRAINT ck_classical_rule_body_schema
    CHECK (jsonb_matches_family_rule_body(technique_family_id, rule_body));

-- ============================================================
-- classical_rule.classical_names: small fixed inline schema
-- ============================================================
ALTER TABLE classical_rule
    ADD CONSTRAINT ck_classical_rule_names_schema
    CHECK (
        jsonb_matches_schema(
            '{
               "type": "object",
               "properties": {
                 "en":              {"type": "string"},
                 "sa_iast":         {"type": "string"},
                 "sa_devanagari":   {"type": "string"},
                 "ta":              {"type": "string"}
               },
               "additionalProperties": false,
               "required": ["en"]
             }'::jsonb,
            classical_names
        )
    );

-- ============================================================
-- astrologer_source_preference.source_weights: all values in [0, 1]
-- (keys already validated by F2 trigger)
-- ============================================================
ALTER TABLE astrologer_source_preference
    ADD CONSTRAINT ck_source_weights_schema
    CHECK (
        jsonb_matches_schema(
            '{
               "type": "object",
               "additionalProperties": {
                 "type": "number",
                 "minimum": 0,
                 "maximum": 1
               }
             }'::jsonb,
            source_weights
        )
    );

-- ============================================================
-- aggregation_signal.signal_value: per-signal-type shape via CASE
-- ============================================================
CREATE OR REPLACE FUNCTION jsonb_matches_signal_value(p_type text, p_data jsonb)
RETURNS boolean AS $$
BEGIN
    RETURN CASE p_type
      WHEN 'astrologer_override_implicit' THEN
        jsonb_matches_schema(
          '{"type":"object","properties":{"session_id":{"type":"string"},"element_path":{"type":"string"}},"required":["session_id","element_path"]}'::jsonb,
          p_data
        )
      WHEN 'astrologer_override_explicit' THEN
        jsonb_matches_schema(
          '{"type":"object","properties":{"verdict":{"enum":["affirm","reject"]},"note":{"type":"string"}},"required":["verdict"]}'::jsonb,
          p_data
        )
      WHEN 'user_thumbs_up' THEN
        jsonb_matches_schema('{"type":"object","properties":{"session_id":{"type":"string"}}}'::jsonb, p_data)
      WHEN 'user_thumbs_down' THEN
        jsonb_matches_schema(
          '{"type":"object","properties":{"session_id":{"type":"string"},"reason_code":{"type":"string"}}}'::jsonb,
          p_data
        )
      WHEN 'outcome_positive' THEN
        jsonb_matches_schema(
          '{"type":"object","properties":{"observed_at":{"type":"string","format":"date-time"},"note":{"type":"string"}},"required":["observed_at"]}'::jsonb,
          p_data
        )
      WHEN 'outcome_negative' THEN
        jsonb_matches_schema(
          '{"type":"object","properties":{"observed_at":{"type":"string","format":"date-time"},"note":{"type":"string"}},"required":["observed_at"]}'::jsonb,
          p_data
        )
      WHEN 'outcome_neutral' THEN
        jsonb_matches_schema(
          '{"type":"object","properties":{"observed_at":{"type":"string","format":"date-time"}},"required":["observed_at"]}'::jsonb,
          p_data
        )
      ELSE false
    END;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

ALTER TABLE aggregation_signal
    ADD CONSTRAINT ck_aggregation_signal_value_schema
    CHECK (jsonb_matches_signal_value(signal_type, signal_value));
```

### 5.3 Python-side validator

```python
# src/josi/services/classical/json_schema_validator.py

from dataclasses import dataclass
from typing import Any

import jsonschema
from jsonschema import Draft202012Validator


@dataclass(frozen=True)
class ValidationIssue:
    path: str              # JSON Pointer-style: "/conditions/0/planet"
    message: str
    schema_path: str


class JSONSchemaValidationError(ValueError):
    """Raised when a JSONB payload fails schema validation in the app-layer fallback
    or during error enrichment after a DB CHECK violation."""

    def __init__(self, issues: list[ValidationIssue], context: dict[str, Any]):
        self.issues = issues
        self.context = context
        super().__init__(self._format())

    def _format(self) -> str:
        lines = [f"JSON Schema validation failed ({len(self.issues)} issue(s)):"]
        for i in self.issues:
            lines.append(f"  - {i.path or '<root>'}: {i.message}")
        return "\n".join(lines)


def validate(schema: dict, instance: Any) -> list[ValidationIssue]:
    """Return list of issues; empty list means valid.

    Uses Draft 2020-12 (pg_jsonschema default). Path is JSON Pointer.
    """
    validator = Draft202012Validator(schema)
    issues: list[ValidationIssue] = []
    for err in validator.iter_errors(instance):
        path = "/" + "/".join(str(p) for p in err.absolute_path)
        issues.append(
            ValidationIssue(
                path=path if path != "/" else "",
                message=err.message,
                schema_path="/".join(str(p) for p in err.absolute_schema_path),
            )
        )
    return issues


def validate_or_raise(schema: dict, instance: Any, context: dict | None = None) -> None:
    issues = validate(schema, instance)
    if issues:
        raise JSONSchemaValidationError(issues, context or {})


def enrich_integrity_error(
    raw_error: Exception,
    schema: dict,
    instance: Any,
    context: dict,
) -> JSONSchemaValidationError:
    """Called on DB IntegrityError when we suspect a CHECK-schema failure; re-validates
    in Python to produce a pointable error, preserving the original as a cause."""
    issues = validate(schema, instance)
    err = JSONSchemaValidationError(issues or [ValidationIssue("", str(raw_error), "")], context)
    err.__cause__ = raw_error
    return err
```

### 5.4 Write-path integration

Services that write `technique_compute`, `aggregation_event`, `classical_rule`, etc., wrap their writes:

```python
try:
    await session.execute(insert_stmt)
    await session.commit()
except IntegrityError as e:
    if "schema" in str(e).lower():   # CHECK-name pattern
        schema = await _load_schema(session, shape_id)
        raise enrich_integrity_error(e, schema, payload, {"shape_id": shape_id})
    raise
```

This keeps the hot path fast (DB CHECK as primary enforcement) while giving engineers useful errors on failure.

## 6. User Stories

### US-F5.1: As an engineer, I want to insert a malformed `technique_compute.result` and have the DB reject it
**Acceptance:** INSERT with `result = {"isActive": true}` for a shape requiring `active` key fails with a CHECK constraint violation that references `ck_technique_compute_result_schema`.

### US-F5.2: As an engineer, when a validation error fires I want a message pointing at the offending field
**Acceptance:** wrapping the write via `enrich_integrity_error`, the raised Python exception reads like `JSON Schema validation failed (1 issue(s)): /active: 'active' is a required property`.

### US-F5.3: As a rule author, I want malformed `rule_body` YAML to fail the deploy
**Acceptance:** F6's loader computes the rule_body JSONB, attempts INSERT, DB CHECK fires, loader surfaces a validation error naming the rule and the failing path. Deploy aborts.

### US-F5.4: As a DBA, I want schema updates to not retroactively invalidate existing rows
**Acceptance:** after `UPDATE output_shape SET json_schema = <stricter> WHERE shape_id = 'X'`, existing rows with `output_shape_id = 'X'` are untouched; new inserts with X must conform. No historical recompute triggered.

### US-F5.5: As an engineer, I want validation overhead per write to be < 5% at P1 volumes
**Acceptance:** benchmark in T-F5.9 measures insert latency with and without CHECK constraints on 10k rows; delta ≤ 5% at P50, P99.

### US-F5.6: As an engineer, I want the system to fail fast if `pg_jsonschema` isn't installed
**Acceptance:** on startup the app queries `pg_extension` for `pg_jsonschema`; if absent, logs a critical warning and switches to app-layer validation with clear log indication.

### US-F5.7: As a rule author, I want the empty-schema `{}` loophole to be visible and temporary
**Acceptance:** CI lint flags any `output_shape.json_schema = '{}'` as a warning; F7 tracks closure of all loopholes; observability dashboard shows count of shapes still empty.

## 7. Tasks

### T-F5.1: Verify pg_jsonschema availability on Cloud SQL
- **Definition:** In both `josiam-dev` and `josiam-prod`, run `SELECT * FROM pg_available_extensions WHERE name = 'pg_jsonschema'`. Confirm the extension is listed. If missing, file ticket with Cloud SQL support and block this PRD.
- **Acceptance:** Extension appears in `pg_available_extensions` in both environments. `CREATE EXTENSION pg_jsonschema` succeeds in dev.
- **Effort:** 1 hour
- **Depends on:** none

### T-F5.2: Alembic migration for pg_jsonschema + helper functions + CHECK constraints
- **Definition:** Autogenerate migration with Alembic; hand-add `CREATE EXTENSION pg_jsonschema`, the three helper functions (`jsonb_matches_output_shape`, `jsonb_matches_family_default_shape`, `jsonb_matches_family_rule_body`, `jsonb_matches_signal_value`), the `rule_body_schema` column on `technique_family`, and all CHECK constraints listed in §5.2.
- **Acceptance:** Migration upgrades cleanly from F4 state; downgrades cleanly drop CHECK constraints, helper functions, and the added column (not the extension — extensions are not dropped on downgrade to avoid side-effects).
- **Effort:** 5 hours
- **Depends on:** T-F5.1, F1, F2, F4 complete

### T-F5.3: Python JSONSchemaValidator module
- **Definition:** Implement `validate()`, `validate_or_raise()`, `enrich_integrity_error()` per §5.3. Use `jsonschema==4.23.x` (add to `pyproject.toml` under main deps, not just test).
- **Acceptance:** Unit tests in §8.2 pass. Error messages are precise JSON Pointer paths.
- **Effort:** 3 hours
- **Depends on:** none

### T-F5.4: Wire enrichment into write path
- **Definition:** Create a base class or mixin for repositories that persist JSONB-validated rows; on `IntegrityError` with CHECK-name matching, load the relevant schema and re-validate via `enrich_integrity_error`.
- **Acceptance:** One example repo (`TechniqueComputeRepository`) demonstrates the pattern; integration test asserts the raised exception is `JSONSchemaValidationError` with correct issue path.
- **Effort:** 4 hours
- **Depends on:** T-F5.2, T-F5.3

### T-F5.5: App-layer fallback for environments without pg_jsonschema
- **Definition:** In `DimensionLoader` / startup hook, detect absence of `pg_jsonschema` extension; if absent, register a SQLAlchemy `before_insert` / `before_update` event listener on the five target tables that invokes `validate_or_raise()` in Python before the row reaches the DB. Logged prominently as a degraded mode.
- **Acceptance:** Toggle test disables pg_jsonschema; ORM writes still reject invalid payloads; raw SQL writes are unvalidated (acceptable gap in degraded mode).
- **Effort:** 4 hours
- **Depends on:** T-F5.3

### T-F5.6: Seed test schemas for initial coverage
- **Definition:** For the unit tests in §8, populate `output_shape.json_schema` for two shapes (`boolean_with_strength`, `numeric`) with minimum-viable schemas to drive the test suite. Full schema authoring is F7.
- **Acceptance:** Two shapes have non-empty schemas in test fixtures; tests exercise both valid + invalid paths.
- **Effort:** 2 hours
- **Depends on:** T-F5.2

### T-F5.7: `jsonb_validate_output_shape(shape_id, data) -> jsonb` companion function
- **Definition:** App-callable function that returns structured errors as JSONB. Used by a debug endpoint `GET /api/v1/internal/validate-shape` (dev/staging only, guarded by env var).
- **Acceptance:** Function installed; debug endpoint returns 200 with `{valid: bool, errors: [...]}` on arbitrary input; not exposed in production.
- **Effort:** 3 hours
- **Depends on:** T-F5.3

### T-F5.8: Schema-loophole observability
- **Definition:** Emit a startup metric `f5_empty_schema_count` = count of `output_shape` rows with `json_schema = '{}'`. Dashboard panel tracks closure over P0.
- **Acceptance:** Metric emitted; initial value equals number of shapes seeded with `{}`; decreases as F7 ships.
- **Effort:** 1 hour
- **Depends on:** T-F5.2

### T-F5.9: Insert-latency benchmark
- **Definition:** Benchmark script inserts 10k `technique_compute` rows with and without CHECK constraints; compares P50/P99 latency and total wall-clock.
- **Acceptance:** P50 delta < 5%; P99 delta < 10%. Result logged to `reports/f5-benchmark.json`.
- **Effort:** 3 hours
- **Depends on:** T-F5.2

## 8. Unit Tests

### 8.1 DB-level CHECK constraints

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_compute_result_accepts_valid_boolean_with_strength` | `output_shape_id='boolean_with_strength'`, `result={"active":true,"strength":0.7}` | INSERT succeeds | happy path |
| `test_compute_result_rejects_missing_required_field` | same shape, `result={"strength":0.7}` | IntegrityError, CHECK name `ck_technique_compute_result_schema` | required fields enforced |
| `test_compute_result_rejects_wrong_type` | `result={"active":"yes","strength":0.7}` | IntegrityError | type checking |
| `test_compute_result_rejects_out_of_range_strength` | `result={"active":true,"strength":1.5}` | IntegrityError | range constraint |
| `test_compute_result_accepts_when_schema_is_empty` | shape with `json_schema='{}'` | INSERT succeeds | P0 loophole works |
| `test_compute_result_rejects_unknown_shape` | `output_shape_id='nonexistent'` | EXCEPTION from helper: `unknown output_shape_id` | defensive |
| `test_agg_event_output_uses_family_default_shape` | family whose default is `numeric`, output=`{"value": 1.0}` | INSERT succeeds | join through family |
| `test_agg_event_output_rejects_shape_mismatch` | family with `boolean_with_strength`, output=`{"value": 1.0}` | IntegrityError | family→shape routing |
| `test_classical_names_requires_en` | `classical_names={"sa_iast": "Śiva"}` | IntegrityError | en required |
| `test_classical_names_rejects_extra_keys` | `classical_names={"en":"Shiva","klingon":"tlhIngan"}` | IntegrityError | additionalProperties false |
| `test_source_weights_rejects_value_over_1` | `source_weights={"bphs": 1.5}` | IntegrityError | [0,1] constraint |
| `test_source_weights_accepts_empty_object` | `source_weights={}` | INSERT succeeds | empty is valid |
| `test_signal_value_astrologer_explicit_requires_verdict` | `signal_type='astrologer_override_explicit'`, `signal_value={}` | IntegrityError | verdict required |
| `test_signal_value_unknown_signal_type_rejected` | `signal_type='made_up'` | CHECK on enum fires first | F2 CHECK + F5 CASE |

### 8.2 Python validator module

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_validate_returns_empty_list_on_valid` | schema + valid instance | `[]` | happy path |
| `test_validate_returns_issue_for_missing_required` | schema requiring `x`, instance `{}` | 1 issue, path="", message contains "'x' is a required property" | correct path reporting |
| `test_validate_returns_issues_for_nested_error` | schema with `conditions[].planet` typed as string, instance with int | 1 issue, path=`/conditions/0/planet`, message mentions string | JSON Pointer depth |
| `test_validate_returns_multiple_issues` | invalid multiple times | all issues collected | iter_errors coverage |
| `test_validate_or_raise_raises` | invalid instance | `JSONSchemaValidationError` raised | public API contract |
| `test_validate_or_raise_silent_on_valid` | valid instance | no exception | |
| `test_enrich_preserves_cause` | fake IntegrityError + schema + instance | raised error `.__cause__` == original | traceable |
| `test_enrich_message_formatted_cleanly` | 2 issues | multi-line message with `- /path: message` format | readable |

### 8.3 App-layer fallback path

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_fallback_enabled_when_extension_missing` | mock absence of pg_jsonschema | SQLAlchemy event listeners registered | graceful degradation |
| `test_fallback_rejects_invalid_write_pre_db` | ORM write with invalid payload | `JSONSchemaValidationError` raised before SQL hits DB | app-layer enforcement |
| `test_fallback_not_registered_when_extension_present` | extension present | no listeners registered (DB CHECKs are sole enforcement) | no duplicate work |

### 8.4 Schema migration behavior

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_schema_update_does_not_invalidate_existing_rows` | INSERT valid row; UPDATE output_shape schema to stricter; SELECT row | row still readable, no error | provenance preserved |
| `test_new_inserts_must_conform_after_schema_update` | same fixture; INSERT with old-valid payload | IntegrityError if payload no longer conforms | forward enforcement |
| `test_empty_schema_loophole_closes_cleanly` | shape starts `{}`; INSERT anything; update to real schema; INSERT conforming | all succeed | P0→P1 transition |

### 8.5 Benchmark (integration / CI)

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_insert_overhead_under_5pct_p50` | 10k rows with vs without CHECK | delta < 5% | budget |
| `test_insert_overhead_under_10pct_p99` | same | delta < 10% | budget |
| `test_startup_reports_extension_presence` | app startup | log contains `pg_jsonschema: available` or `...: MISSING (degraded mode)` | observability |

### 8.6 Error UX

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_integration_check_failure_is_enriched` | write invalid via TechniqueComputeRepository | caught IntegrityError → raised JSONSchemaValidationError with pointable path | developer UX |
| `test_error_includes_context` | invalid write with known shape_id | `context` dict in error includes shape_id | debuggability |

## 9. EPIC-Level Acceptance Criteria

- [ ] `pg_jsonschema` extension installed in dev + prod Cloud SQL instances
- [ ] Helper functions created: `jsonb_matches_output_shape`, `jsonb_matches_family_default_shape`, `jsonb_matches_family_rule_body`, `jsonb_matches_signal_value`
- [ ] CHECK constraints on all five target JSONB columns:
  - [ ] `technique_compute.result`
  - [ ] `aggregation_event.output`
  - [ ] `classical_rule.rule_body`
  - [ ] `classical_rule.classical_names`
  - [ ] `astrologer_source_preference.source_weights`
  - [ ] `aggregation_signal.signal_value`
- [ ] Column `technique_family.rule_body_schema` added (default `{}`, populated by F6)
- [ ] Python `JSONSchemaValidator` module implements `validate`, `validate_or_raise`, `enrich_integrity_error`
- [ ] App-layer fallback activates automatically if `pg_jsonschema` is missing
- [ ] Insert-latency benchmark shows ≤ 5% overhead at P50 and ≤ 10% at P99
- [ ] Integration test: invalid write raises `JSONSchemaValidationError` with precise JSON Pointer path
- [ ] Schema-update invariant: updating an `output_shape.json_schema` does not invalidate historical rows
- [ ] Observability metric `f5_empty_schema_count` emitted on startup
- [ ] Unit test coverage ≥ 90% for Python validator module
- [ ] Alembic migration upgrades cleanly from F4 state; downgrades cleanly (except extension drop)
- [ ] Documentation: CLAUDE.md updated with section "JSONB columns are DB-validated; to add a new JSONB column, extend F5 pattern"

## 10. Rollout Plan

- **Feature flag:** `F5_STRICT_VALIDATION` (default on in P0; never expected to be disabled). Purpose: emergency escape hatch if a schema bug blocks all writes; setting to `off` disables CHECK constraints via `ALTER TABLE ... ALTER CONSTRAINT ... NOT VALID` and re-enables after fix. Removed in P1 after confidence established.
- **Shadow compute:** N/A.
- **Backfill strategy:** Tables are empty at F5 time. If applied later with data, each CHECK is added via `ALTER TABLE ... ADD CONSTRAINT ... NOT VALID` followed by `ALTER TABLE ... VALIDATE CONSTRAINT ...` — a concurrent validation pass that does not lock writes. This pattern is standard Postgres practice and the migration uses it by default.
- **Rollback plan:** `alembic downgrade -1` drops CHECK constraints and helper functions. Extension is NOT dropped (safer to leave installed). Safe at P0.

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| `pg_jsonschema` disappears from Cloud SQL allow-list | Low | High | App-layer fallback ready; all writes go through ORM in P0 |
| Schema bug blocks all writes to a critical table | Low | Critical | `F5_STRICT_VALIDATION` flag disables CHECKs in emergency; rollback via re-migration |
| Validation overhead exceeds 5% under load spike | Low | Medium | T-F5.9 benchmark; monitor P99 insert latency; denormalize shape_id if needed |
| Engineers bypass ORM with raw SQL, skip validation | Medium | High | DB CHECK is the primary enforcement, not ORM — raw SQL still validates as long as pg_jsonschema is present |
| Empty `{}` schemas remain in production indefinitely | Medium | Medium | `f5_empty_schema_count` metric + dashboard; F7 tracks closure |
| Error message from CHECK isn't actionable | High | Medium | `enrich_integrity_error` re-validates in Python for pointable paths |
| Helper functions mis-marked IMMUTABLE cause plan-cache weirdness | Low | Medium | Marked STABLE not IMMUTABLE; benchmark rules out regressions |
| Draft version mismatch between pg_jsonschema (2020-12) and Python jsonschema | Low | Medium | Pin Python lib to Draft 2020-12; CI test runs same schema through both |
| Nested subquery in `ck_aggregation_event_output_schema` slow at scale | Medium | Medium | Denormalize `default_output_shape_id` onto `aggregation_event` in P3 if bench degrades |

## 12. References

- Master spec: [`docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`](../../../superpowers/specs/2026-04-19-classical-techniques-expansion-design.md) §2.2 (JSONB columns), open question resolved in §9.2
- Related PRDs: [F1](./F1-star-schema-dimensions.md), [F2](./F2-fact-tables.md), [F4](./F4-temporal-rule-versioning.md), F6 (rule DSL schema → `technique_family.rule_body_schema`), F7 (output_shape JSON Schemas)
- `pg_jsonschema` extension: https://github.com/supabase/pg_jsonschema
- JSON Schema Draft 2020-12: https://json-schema.org/draft/2020-12
- Python `jsonschema` library: https://python-jsonschema.readthedocs.io/
- Cloud SQL PG17 extensions list: https://cloud.google.com/sql/docs/postgres/extensions
- Postgres `ADD CONSTRAINT ... NOT VALID` pattern: https://www.postgresql.org/docs/17/sql-altertable.html
