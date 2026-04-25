---
prd_id: F4
epic_id: F4
title: "Temporal rule versioning (effective_from/to, semver, content_hash)"
phase: P0-foundation
tags: [#correctness, #extensibility]
priority: must
depends_on: [F1, F2]
enables: [F6, F13, P3-E6-flag, S8]
classical_sources: []
estimated_effort: 2 days
status: approved
author: Govind
last_updated: 2026-04-25
---

# F4 — Temporal Rule Versioning

## 1. Purpose & Rationale

Classical astrology rules are not code constants. They are opinions — sometimes centuries-old, sometimes modern software interpretations — that we curate, version, and occasionally correct. A yoga condition derived from BPHS Ch.36 v.14-16 in our v1.0.0 rule may prove, after cross-source analysis, to have mis-interpreted a particular Sanskrit phrase. We fix it, ship v1.1.0, and the question arises: what happens to the 15 million chart computations already persisted with v1.0.0's result?

Three correctness-critical properties must hold for the answer:

1. **Rows are immutable provenance.** A `technique_compute` row computed against rule v1.0.0 must forever identify itself as v1.0.0. Downstream aggregations, AI explanations, and audit trails rely on this.
2. **Only one rule version is "active" at any moment in wall-clock time.** New computes invoked today use today's active version. There is no ambiguity about which rule will be applied to a new chart.
3. **Content cannot be silently mutated.** If someone edits a YAML rule file without bumping the version, the `content_hash` catches it at load time and refuses to apply.

This PRD establishes the schema, semantics, and enforcement mechanisms for temporal rule versioning. Changes are:
- Additive via `effective_from`, `effective_to`, `version` (semver), and `content_hash` columns on `classical_rule`
- A BEFORE INSERT/UPDATE trigger preventing overlapping active versions of the same `(rule_id, source_id)`
- A canonical JSON specification + sha256 hashing algorithm, uniform across the codebase
- A query pattern for "active rule at time T" and its index strategy

## 2. Scope

### 2.1 In scope
- Amendment to F2's `classical_rule` schema: confirm `effective_from`, `effective_to`, `version`, `content_hash` columns (already declared in F2 but not specified in detail)
- Canonical JSON algorithm specification (byte-exact, reproducible across languages)
- `sha256` content hashing algorithm applied to canonical JSON of `rule_body`
- Semver version format with explicit MAJOR/MINOR/PATCH semantics for rules
- BEFORE INSERT/UPDATE trigger preventing temporal overlap of active `(rule_id, source_id)` versions
- Query patterns for "active rule at time T" with supporting partial index
- Deprecation workflow: how to retire a rule version without losing historical computes
- Python helpers for canonicalization, hashing, and "active version resolution"
- Unit tests covering canonicalization edge cases, hash determinism, overlap prevention, and temporal queries

### 2.2 Out of scope
- Rule loader service that reads YAML → writes to DB (F6)
- Actual DSL grammar of `rule_body` (F6)
- Feature-flagged rollout of rule versions (shadow → 10% → 50% → 100%) — P3-E6-flag
- UI for rule authoring / promotion (P3-E2-console)
- Cross-source rule comparison (P3-E8-obs)
- Per-tenant rule overrides (P4-E4-tenant)
- Hash algorithms other than sha256 (sha256 is sufficient for non-adversarial integrity; if we ever require HMAC or signing, additive column)

### 2.3 Dependencies
- F1 (`source_authority` as FK target for rule source — referenced via `source_authority_code` per F1 Pass 2)
- F2 (`classical_rule` table exists with `effective_from`, `effective_to`, `content_hash`, `version` columns per F2 Pass 2 schema)
- Python 3.12 standard library: `hashlib` — for sha256
- `rfc8785` package (~50KB pure Python, MIT licensed) — for RFC 8785 / JCS canonical JSON per F4-Q1
- `packaging.version.Version` for semver parsing

## 2.5 Engineering Review (Pass 2 — Locked 2026-04-25)

**Reviewer:** cpselvam + Govind (pair) · **Rubric:** 3-layer · **Conforms to:** ARCHITECTURE_DECISIONS §0.9, §0.10, §0.12, §0.13, §0.14 · **Cascades from:** F1 + F2 Pass 2

### Summary

F4 establishes the temporal versioning + content-hash backbone for `classical_rule`. Pass 2 swaps the custom Josi Canonical JSON spec for RFC 8785 (JCS) — internet standard, byte-identical for our inputs, eliminates future migration if we ever ship multi-language SDKs or sign rules cryptographically. Trigger SQL + indexes updated for F1+F2 Pass 2 column renames. F2's non-unique partial index superseded by F4's UNIQUE partial index. Effort 3d → 2d. All three rubric layers pass.

### Layer 1 — Structural Completeness (12-point)

| # | Item | Status | Note |
|:-:|---|:-:|---|
| 1 | Frontmatter | ✅ | `status: approved`, `last_updated: 2026-04-25`, effort revised 3d→2d |
| 2 | Purpose clear | ✅ | §1 — 3 correctness invariants articulated |
| 3 | Scope precise | ✅ | clean in/out/deps; rfc8785 dependency declared |
| 4 | Research substantive | ✅ | §3.1–§3.8 with bitemporal reference, RFC 8785 rationale (revised), semver semantics, alternatives |
| 5 | Open questions resolved | ✅ | §4 + Pass 2 Decisions F4-Q1–F4-Q3 |
| 6 | Component design executable | ✅ | trigger + 3 Python modules; revised SQL below |
| 7 | User stories testable | ✅ | US-F4.1–F4.6 |
| 8 | Tasks decomposed | ✅ | T-F4.1–F4.8 + 6-task DAG below |
| 9 | Unit tests enumerated | ✅ | §8.1–§8.7 incl. Hypothesis property tests |
| 10 | Acceptance criteria binary | ✅ | revised below |
| 11 | Rollout plan credible | ✅ | empty-table swap |
| 12 | Risks identified | ✅ | revised below — JCJ-specific risks dropped |

**Layer 1 verdict:** 12 / 12 pass.

### Layer 2 — Design Quality (7-lens)

| # | Lens | Finding | Status |
|:-:|---|---|:-:|
| 1 | Futuristic | Valid-time only with explicit additive path to bitemporal; semver expressive | ✅ |
| 2 | Future-proof | RFC 8785 (internet standard) instead of custom JCJ → cross-language SDK / cryptographic signing / federation all unblocked. Resolved by F4-Q1. | ✅ |
| 3 | Extendible | New rule = INSERT row; new tradition handled by F1 dim layer | ✅ |
| 4 | Audit-ready | Immutable rows + content-hash + FK preservation forever; F4 IS the audit foundation | ✅ |
| 5 | Performant | Partial index + temporal index strategy; trigger O(log N); P99 < 5ms target at 100k rules | ✅ |
| 6 | User-friendly | Trigger error messages name both conflicting versions; semver semantics in author guide | ✅ |
| 7 | AI-first | N/A — `rule_body` consumed by F6 / engines, not directly LLM-facing | N/A |

**Layer 2 verdict:** 6 / 6 applicable lenses ✅; 1 N/A.

### Layer 3 — Cross-cutting Compliance

| Lock | Status | Evidence |
|---|:-:|---|
| §0.5 liability | N/A | No AI surface |
| §0.8 eval harness | N/A | No AI surface |
| §0.9 reconstructability | ✅ | F4 IS the reconstructability foundation (immutable rows + content_hash + temporal columns + FK preservation) |
| §0.10 task DAG + path overlap | ✅ | 6-task DAG below; path overlap declared |
| §0.12 naming | ✅ | F4-Q2: trigger SQL + indexes use F1+F2 Pass 2 column names (`rule_code`, `source_authority_code`); no bare `id` |
| §0.13 config-based versioning | ✅ | F4 IS the config-based versioning PRD; semver + temporal columns + content_hash |
| §0.14 PK conventions | ✅ | Compatible with F2-Q1 — `classical_rule_id UUID PK` + `UNIQUE(rule_code, source_authority_code, version)` |
| §1.5 multilingual | N/A | `classical_names` JSONB on classical_rule (F2-managed); F4 doesn't touch |
| F1+F2 cascade | ✅ | F4-Q2 + F4-Q3 applied (column renames + index dedup) |

**Layer 3 verdict:** 7 applicable locks ✅; 2 N/A.

### Pass 2 Decisions

| # | Gap | Decision |
|---|---|---|
| F4-Q1 | Custom JCJ vs RFC 8785 (JCS) canonical JSON | **RFC 8785 (JCS)** via `rfc8785` Python package. Internet standard; byte-identical to JCJ for all our inputs; reference implementations in JS / Go / Java / Swift / .NET keep multi-language SDKs and cryptographic-signing futures unblocked. Replaces §3.2 JCJ spec; replaces §5.3 `canonical_json` implementation. |
| F4-Q2 | F1+F2 cascade column renames in trigger SQL | **Apply rename.** `rule_id` → `rule_code`; `source_id` → `source_authority_code` throughout trigger function `check_rule_version_no_overlap()` and indexes. |
| F4-Q3 | Index redundancy with F2 | **F4 drops F2's `idx_classical_rule_active` and creates UNIQUE version.** F4's UNIQUE partial index (`idx_classical_rule_one_active`) is functionally a superset (also serves query lookup). Eliminates write-time penalty of duplicate index. |

### Revised SQL (applied — supersedes §5.2)

```sql
-- ============================================================
-- F4 migration: trigger + indexes + CHECKs on classical_rule
-- (table created in F2; this PRD adds enforcement)
-- ============================================================

-- Drop F2's non-unique partial index; F4-Q3 supersedes with UNIQUE version
DROP INDEX IF EXISTS idx_classical_rule_active;

-- Partial UNIQUE index: at most one active (effective_to NULL) version per (rule_code, source_authority_code)
CREATE UNIQUE INDEX idx_classical_rule_one_active
    ON classical_rule (rule_code, source_authority_code)
    WHERE effective_to IS NULL;

-- Temporal lookup index: supports "active at time T" queries
CREATE INDEX idx_classical_rule_temporal
    ON classical_rule (rule_code, source_authority_code, effective_from DESC, effective_to);

-- Overlap-prevention trigger function (handles closed-interval overlap cases)
CREATE OR REPLACE FUNCTION check_rule_version_no_overlap()
RETURNS trigger AS $$
DECLARE
    overlap_count INT;
BEGIN
    SELECT COUNT(*) INTO overlap_count
      FROM classical_rule
     WHERE rule_code = NEW.rule_code
       AND source_authority_code = NEW.source_authority_code
       AND version <> NEW.version
       AND tstzrange(
             NEW.effective_from,
             COALESCE(NEW.effective_to, 'infinity'::timestamptz),
             '[)'
           ) && tstzrange(
             effective_from,
             COALESCE(effective_to, 'infinity'::timestamptz),
             '[)'
           );
    IF overlap_count > 0 THEN
        RAISE EXCEPTION
          'classical_rule version overlap: (rule_code=%, source_authority_code=%) new [%..%) conflicts with existing version',
          NEW.rule_code, NEW.source_authority_code,
          NEW.effective_from,
          COALESCE(NEW.effective_to::text, 'open');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_rule_version_no_overlap
    BEFORE INSERT OR UPDATE ON classical_rule
    FOR EACH ROW EXECUTE FUNCTION check_rule_version_no_overlap();

-- Content-hash format check
ALTER TABLE classical_rule
    ADD CONSTRAINT ck_classical_rule_content_hash_format
    CHECK (content_hash ~ '^[0-9a-f]{64}$');

-- Semver format check (strict X.Y.Z; pre-release deferred)
ALTER TABLE classical_rule
    ADD CONSTRAINT ck_classical_rule_version_semver
    CHECK (version ~ '^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$');

-- Effective-window sanity
ALTER TABLE classical_rule
    ADD CONSTRAINT ck_classical_rule_effective_window
    CHECK (effective_to IS NULL OR effective_to > effective_from);
```

### Revised canonical_json module (RFC 8785 / JCS — supersedes §5.3)

```python
# src/josi/services/classical/canonical_json.py

import hashlib
import math
from typing import Any

import rfc8785


class CanonicalJSONError(ValueError):
    """Raised when a value cannot be canonicalized (NaN/Infinity, unsupported types)."""


def canonical_json(obj: Any) -> bytes:
    """Serialize obj to RFC 8785 (JSON Canonicalization Scheme) bytes.

    RFC 8785 spec (https://datatracker.ietf.org/doc/html/rfc8785):
      - UTF-8, no BOM
      - Object keys sorted by UTF-16 code unit ascending
      - Arrays preserved in source order
      - Numbers formatted per ECMAScript 2018 §7.1.12.1 (shortest round-trip)
      - Forbidden: NaN, Infinity (we pre-check + raise CanonicalJSONError)
      - No insignificant whitespace
      - No trailing newline

    Cross-language reference implementations exist for JavaScript, Go, Java,
    Swift, .NET — all guaranteed byte-identical for the same input.
    """
    _assert_finite(obj)
    return rfc8785.dumps(obj)


def content_hash(obj: Any) -> str:
    """Return sha256 hex digest of canonical_json(obj). 64 lowercase hex chars."""
    return hashlib.sha256(canonical_json(obj)).hexdigest()


def _assert_finite(obj: Any) -> None:
    """Pre-check NaN/Infinity to give a clear error before delegating to rfc8785."""
    if isinstance(obj, float) and not math.isfinite(obj):
        raise CanonicalJSONError(f"NaN/Infinity not allowed in canonical JSON: {obj}")
    if isinstance(obj, dict):
        for v in obj.values():
            _assert_finite(v)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            _assert_finite(v)
```

### Path overlap declaration

F4 reserves these paths (no other P0 PRD writes here):

```
src/josi/services/classical/canonical_json.py
src/josi/services/classical/rule_version.py
src/josi/services/classical/rule_temporal.py
src/josi/schemas/classical/rule_version_schema.py
src/alembic/versions/                  # one F4 migration file (sequenced after F3)
tests/unit/services/classical/test_canonical_json.py
tests/unit/services/classical/test_rule_version.py
tests/unit/services/classical/test_rule_temporal.py
tests/integration/classical/test_f4_overlap_trigger.py
tests/integration/classical/test_f4_temporal_lifecycle.py
docs/markdown/rule-authoring-semver.md
```

`pyproject.toml` gains `rfc8785 = "^0.1"` dependency (touches a file owned by project root, coordinated as a single-line addition).

### Task DAG entries (§0.10)

```json
[
  {
    "task_id": "F4-canonical-json-module",
    "prd_ref": "F4",
    "role": "coder",
    "depends_on": [],
    "acceptance_criteria": "rfc8785 added to pyproject.toml. canonical_json(obj) and content_hash(obj) wrappers implemented. Pre-checks NaN/Infinity → CanonicalJSONError. Hypothesis property tests verify determinism across 1000+ generated examples. Cross-version test (PY 3.12 + 3.13) yields identical hashes for known fixtures.",
    "affected_paths": ["src/josi/services/classical/canonical_json.py", "tests/unit/services/classical/test_canonical_json.py", "pyproject.toml"],
    "test_command": "poetry run pytest tests/unit/services/classical/test_canonical_json.py --cov=josi.services.classical.canonical_json --cov-fail-under=95",
    "max_turns": 25,
    "model_tier": "cheap",
    "retry_budget": 1
  },
  {
    "task_id": "F4-rule-version-module",
    "prd_ref": "F4",
    "role": "coder",
    "depends_on": [],
    "acceptance_criteria": "RuleVersion.parse() with strict X.Y.Z (rejects pre-release in P0). bump_kind() classifies MAJOR/MINOR/PATCH/NONE. Tests cover all bump cases + invalid input.",
    "affected_paths": ["src/josi/services/classical/rule_version.py", "tests/unit/services/classical/test_rule_version.py"],
    "test_command": "poetry run pytest tests/unit/services/classical/test_rule_version.py",
    "max_turns": 20,
    "model_tier": "cheap",
    "retry_budget": 1
  },
  {
    "task_id": "F4-trigger-and-indexes-migration",
    "prd_ref": "F4",
    "role": "coder + migration-writer",
    "depends_on": ["F2-schema-migration"],
    "acceptance_criteria": "Alembic migration: drop F2's idx_classical_rule_active; create idx_classical_rule_one_active (UNIQUE partial); create idx_classical_rule_temporal; create check_rule_version_no_overlap() function + trg_rule_version_no_overlap trigger; add 3 CHECK constraints (content_hash format, semver format, effective_window). Forward + downgrade roundtrip on empty DB.",
    "affected_paths": ["src/alembic/versions/"],
    "test_command": "poetry run alembic upgrade head && poetry run alembic downgrade -1 && poetry run alembic upgrade head",
    "max_turns": 35,
    "model_tier": "mid",
    "retry_budget": 1
  },
  {
    "task_id": "F4-temporal-resolver",
    "prd_ref": "F4",
    "role": "coder",
    "depends_on": ["F4-trigger-and-indexes-migration"],
    "acceptance_criteria": "resolve_active_rule(session, rule_code, source_authority_code, as_of) returns single ClassicalRule or raises RuleNotActiveError. list_versions() orders by effective_from DESC. EXPLAIN test confirms idx_classical_rule_temporal is used. P99 < 5ms at 100k seeded rule rows.",
    "affected_paths": ["src/josi/services/classical/rule_temporal.py", "tests/unit/services/classical/test_rule_temporal.py"],
    "test_command": "poetry run pytest tests/unit/services/classical/test_rule_temporal.py",
    "max_turns": 30,
    "model_tier": "mid",
    "retry_budget": 1
  },
  {
    "task_id": "F4-overlap-trigger-tests",
    "prd_ref": "F4",
    "role": "coder + qa",
    "depends_on": ["F4-trigger-and-indexes-migration"],
    "acceptance_criteria": "Integration tests cover all §8.3 cases: adjacent windows OK; two open-ended rejected; closed half-open overlap rejected; UPDATE creating overlap rejected; retroactive overlap caught; legitimate sequence accepted.",
    "affected_paths": ["tests/integration/classical/test_f4_overlap_trigger.py"],
    "test_command": "poetry run pytest tests/integration/classical/test_f4_overlap_trigger.py",
    "max_turns": 30,
    "model_tier": "mid",
    "retry_budget": 1
  },
  {
    "task_id": "F4-lifecycle-integration",
    "prd_ref": "F4",
    "role": "coder + qa",
    "depends_on": ["F4-temporal-resolver", "F4-overlap-trigger-tests"],
    "acceptance_criteria": "End-to-end test: seed v1.0.0 → insert technique_compute against v1.0.0 → deprecate v1 (effective_to=now) → insert v1.1.0 → insert technique_compute against v1.1.0 → both compute rows JOIN to their correct rule rows; resolve_active_rule(now-1d)=v1.0.0, resolve_active_rule(now+1d)=v1.1.0. Future-promotion test + rollback test included.",
    "affected_paths": ["tests/integration/classical/test_f4_temporal_lifecycle.py"],
    "test_command": "poetry run pytest tests/integration/classical/test_f4_temporal_lifecycle.py",
    "max_turns": 35,
    "model_tier": "mid",
    "retry_budget": 1
  }
]
```

**Total F4 implementation estimate:** 6 parallelizable tasks; F4-canonical-json-module + F4-rule-version-module run immediately (no blockers). Estimated cost ~$12-20. Wall-clock ~2 days.

### Acceptance criteria (revised — supersedes §9)

- [ ] `rfc8785` package added to `pyproject.toml`
- [ ] `canonical_json(obj)` wraps `rfc8785.dumps(obj)`; pre-checks NaN/Infinity → `CanonicalJSONError`
- [ ] `content_hash(obj)` returns sha256 hex of canonical_json(obj); 64 lowercase hex chars
- [ ] Hypothesis property tests verify determinism across 1000+ examples
- [ ] Cross-Python-version test (3.12, 3.13) produces identical hashes for fixed inputs
- [ ] `RuleVersion.parse` + `.bump_kind()` classify MAJOR/MINOR/PATCH correctly; rejects pre-release in P0
- [ ] `trg_rule_version_no_overlap` enforces non-overlap; uses `rule_code` + `source_authority_code` (F2 Pass 2 names)
- [ ] F2's `idx_classical_rule_active` dropped; replaced by UNIQUE `idx_classical_rule_one_active`
- [ ] `idx_classical_rule_temporal` exists and is used by EXPLAIN of resolve_active_rule
- [ ] 3 CHECK constraints: content_hash format, semver format, effective_window
- [ ] Integration test: deprecate v1 + insert v1.1 + retain historical compute rows all resolve correctly
- [ ] Unit test coverage ≥ 95% for canonical_json, rule_version, rule_temporal
- [ ] Documentation: `docs/markdown/rule-authoring-semver.md` exists; CLAUDE.md references it

### Risks (revised — supersedes §11)

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Author forgets to bump version when semantics change | Medium | High | F6 loader compares computed hash with DB; mismatch fails deploy |
| Trigger performance degrades at 100k+ rules | Low | Medium | O(log N) via temporal index; only on INSERT/UPDATE |
| `rfc8785` package unmaintained or behavior changes | Low | Medium | Pin minor version; CI runs property tests on every release; small enough (~50KB pure Python) that we could fork if abandoned |
| Semver parser rejects valid PEP 440 forms we want later | Medium | Medium | Strict in P0; non-breaking to relax CHECK constraint |
| Retro-active rule activation surprises astrologers | Medium | Medium | UI shows effective_from date; rule loader logs retroactive activations |
| content_hash drifts between YAML declaration and DB | Low | High | Loader computes from YAML and asserts match with DB on load; fail deploy on mismatch |
| Cross-language hash mismatch (if we ever ship a JS/Go SDK) | Low (P0) | High (later) | RFC 8785 chosen specifically to avoid this — JS/Go reference implementations are byte-identical |

### Eval cases

N/A — F4 is data-layer infrastructure; no AI surface.

### Cross-references

- `ARCHITECTURE_DECISIONS.md §0.9` — F4 IS the reconstructability foundation
- `ARCHITECTURE_DECISIONS.md §0.10` — task DAG + path overlap
- `ARCHITECTURE_DECISIONS.md §0.12` — naming compliance via F4-Q2 column rename
- `ARCHITECTURE_DECISIONS.md §0.13` — F4 IS the config-based versioning PRD
- `ARCHITECTURE_DECISIONS.md §0.14` — UUID PK + composite UNIQUE compatible with F2-Q1
- `F1-star-schema-dimensions.md §2.5` — `source_authority_code` rename (F4-Q2 cascade)
- `F2-fact-tables.md §2.5` — `classical_rule` schema F4 amends; `rule_code` rename; F2's `idx_classical_rule_active` superseded (F4-Q3)
- `F6` (next) — rule loader will consume `canonical_json`, `content_hash`, `RuleVersion.bump_kind`, `resolve_active_rule`
- `F13` — content-hash provenance chain extends F4's hashing approach to fact rows
- RFC 8785: https://datatracker.ietf.org/doc/html/rfc8785
- `rfc8785` Python: https://pypi.org/project/rfc8785/

---

## 3. Technical Research

### 3.1 Why temporal versioning over simple "latest version wins"

A naive approach: `classical_rule(rule_id, source_id)` is unique, with a single `version` column; updating a rule overwrites. This is insufficient because:

- **Historical reproducibility:** a chart read generated on 2025-01-15 citing "BPHS Raja Yoga 1.0.0" must still resolve to the exact rule body used then. If the rule is later overwritten to 1.1.0, the historical reading becomes unverifiable.
- **A/B experiments:** shadow-rolling out v1.1.0 on 10% of traffic while v1.0.0 runs on 90% requires two rows coexisting, with orthogonal activation logic handled by F4's feature flags. Both rows must be query-able.
- **Audit and regulatory stance:** when a user asks "what rule produced this?", we must answer with certainty. Immutable rows + PK including version = certainty.
- **Rollback:** a defective v1.1.0 can be retired by setting `effective_to = now()` and promoting v1.0.0 back to active (new row: v1.0.0 with fresh effective_from). Zero data is lost; zero recompute is forced (old computes stay valid against their version).

The temporal pattern is exactly bitemporal database theory (Snodgrass, *Developing Time-Oriented Database Applications in SQL*, Ch. 2–4), narrowed to valid-time only (we do not track transaction-time separately in P0; the `created_at` column is a reasonable proxy for transaction-time).

### 3.2 Canonical JSON specification

Content hashing requires a deterministic byte-sequence from an abstract document. Different JSON encoders produce different byte sequences for the same semantic content. We define Josi Canonical JSON (JCJ) as:

1. **Character encoding**: UTF-8, no BOM.
2. **Object key ordering**: keys sorted lexicographically by Unicode code point ascending.
3. **String escaping**: forward solidus `/` not escaped; `<`, `>`, `&` not escaped; control characters escaped as `\uXXXX`; the six JSON escapes (`\"`, `\\`, `\b`, `\f`, `\n`, `\r`, `\t`) used where applicable; other characters represented verbatim in UTF-8.
4. **Numbers**: integers as shortest decimal with no leading zeros, no `+` sign, no trailing `.0`; floats as shortest IEEE-754 round-trip form per EcmaScript 2018 §7.1.12.1; Infinity and NaN forbidden in `rule_body` (validated by JSON Schema in F5).
5. **Whitespace**: none outside strings.
6. **Null, true, false**: literal, no variation.
7. **Array ordering**: preserved as authored (arrays have semantic order; we do NOT sort arrays).
8. **Trailing newline**: none.

The Python implementation is `json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)` for the common case; we add a wrapper that raises on NaN/Infinity and asserts UTF-8 encoding. For cross-language determinism (if we ever expose this to JavaScript/Go), the spec above is sufficient to re-implement.

### 3.3 Why sha256 (not md5, sha1, blake2, sha3)

- **md5/sha1**: collision-vulnerable; not acceptable for integrity even in non-adversarial contexts
- **sha256**: well-supported, hardware-accelerated on modern x86/ARM, 64-char hex string fits nicely in `CHAR(64)`, ~1µs per rule (<10KB typical)
- **blake2/sha3**: faster or newer but less universally supported; no measurable benefit for our volumes (hundreds of rule loads per deploy, not gigabytes)

### 3.4 Semver semantics for rules

We apply `MAJOR.MINOR.PATCH` with the following semantics specific to classical rules:

- **MAJOR bump**: the rule's interpretation changes in a way that produces different results for the same chart. Examples: changing which planetary conjunction counts as a yoga, changing the house count for a Jaimini karaka. Historical computes against old MAJOR remain valid (they reflect the old interpretation, which was a valid reading of the classical text at the time).
- **MINOR bump**: rule gains additive information without changing output. Examples: adding a new citation, adding a `classical_names` entry in Tamil, refining the internal structure of `rule_body` while preserving output. Old computes remain valid AND can be re-associated with the new MINOR without semantic drift (re-association is optional; we prefer immutable provenance).
- **PATCH bump**: bug fix in the rule body that did not produce observably different outputs in practice. Examples: fixing typos in `rule_body.description`, correcting a citation page number. Re-computes are not required.

These semantics are documented in the rule author guide (F6) and enforced by code review, not by the DB.

### 3.5 Overlap prevention trigger

The invariant "at most one active (effective_to IS NULL) version of any `(rule_id, source_id)` pair" must be enforced at the DB level. A partial unique index:

```sql
CREATE UNIQUE INDEX idx_classical_rule_one_active
    ON classical_rule (rule_id, source_id)
    WHERE effective_to IS NULL;
```

…covers the simple case (no two rows with same `(rule_id, source_id)` and NULL `effective_to`). But it does NOT catch the case where v1.0.0 has `effective_to = 2026-06-01` and v1.1.0 has `effective_from = 2026-05-01` — an overlap during May 2026.

A BEFORE INSERT/UPDATE trigger catches this:

```sql
CREATE OR REPLACE FUNCTION check_rule_version_no_overlap()
RETURNS trigger AS $$
DECLARE
    overlap_count INT;
BEGIN
    SELECT COUNT(*) INTO overlap_count
      FROM classical_rule
     WHERE rule_id = NEW.rule_id
       AND source_id = NEW.source_id
       AND version <> NEW.version
       AND tstzrange(NEW.effective_from, COALESCE(NEW.effective_to, 'infinity'::timestamptz), '[)')
           && tstzrange(effective_from, COALESCE(effective_to, 'infinity'::timestamptz), '[)');
    IF overlap_count > 0 THEN
        RAISE EXCEPTION 'classical_rule version overlap for (rule_id=%, source_id=%): new [% .. %) conflicts with existing active version',
              NEW.rule_id, NEW.source_id, NEW.effective_from, COALESCE(NEW.effective_to::text, 'open');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_rule_version_no_overlap
    BEFORE INSERT OR UPDATE ON classical_rule
    FOR EACH ROW EXECUTE FUNCTION check_rule_version_no_overlap();
```

The trigger uses `tstzrange(...)` and the `&&` overlap operator to handle inclusive-exclusive half-open intervals cleanly. This catches:
- Two open-ended (NULL `effective_to`) versions → overlap at infinity
- An open-ended v1 + a future v2 with `effective_from < now()` (promotion scheduled in the past) → overlap
- Past-closed v1 + future v2 with effective_from before v1's effective_to → overlap

### 3.6 "Active at time T" query

Canonical query pattern:

```sql
SELECT *
  FROM classical_rule
 WHERE rule_id = :rule_id
   AND source_id = :source_id
   AND effective_from <= :as_of
   AND (effective_to IS NULL OR effective_to > :as_of);
```

With the partial index `idx_classical_rule_effective` from F2 plus the new `idx_classical_rule_temporal` below, this is O(log N) with at most one row returned (trigger enforces non-overlap).

### 3.7 Content-hash validation at load time

The rule loader (F6) performs:

1. Parse YAML → Python dict `body`.
2. Compute `hash = sha256(canonical_json(body))`.
3. Compare with the `content_hash` field declared in the YAML itself.
4. If mismatch: log the computed hash, refuse to load, fail the deploy.

This catches:
- Accidental edits to `rule_body` without bumping version (content_hash mismatch against DB's prior row for that version)
- Tampering between author's commit and deploy (content_hash mismatch against the hash the author committed)

The `content_hash` in the DB is stored for query convenience and tamper detection; the canonical source of truth is the YAML file + version.

### 3.8 Alternatives considered

| Alternative | Rejected because |
|---|---|
| Single-column `version` (no effective_from/to) | Loses temporal semantics; can't rollback without losing history |
| `valid_from`/`valid_to` + separate `transaction_from`/`transaction_to` (full bitemporal) | Overkill for P0; we don't yet need transaction-time; add later as additive columns |
| `is_active` boolean instead of effective_to | Encourages forgotten-to-set bugs; overlap prevention is harder to trigger |
| Soft delete (deleted_at) instead of effective_to | Confuses "retired" with "deleted"; a retired rule is not soft-deleted, its old computes remain valid |
| Use jsonb_canonical() from pg_jsonb_canonical extension | Not on Cloud SQL; Python-side canonicalization is portable |
| MD5 content hash | Collision-vulnerable; sha256 has no perceptible performance cost at rule volumes |
| Sequence-number version (1, 2, 3) instead of semver | Loses MAJOR/MINOR/PATCH semantic signaling; semver costs nothing |
| App-level overlap check (no trigger) | Race condition under concurrent rule edits; DB-level enforcement is free |

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| Valid-time only vs full bitemporal | Valid-time only in P0 | Add transaction-time as additive columns later if needed; YAGNI now |
| Semver vs sequence number | Semver | Conveys breaking vs additive vs fix; zero runtime cost |
| Canonical JSON spec source | Custom JCJ spec (documented here) | RFC 8785 (JCS) is aimed at JWS/JSON-LD and is stricter than needed; JCJ matches `json.dumps(sort_keys=True, separators=(",",":"), ensure_ascii=False)` |
| Hash algorithm | sha256 | Universal, hardware-accelerated, 64-char fixed width |
| Overlap prevention location | BEFORE INSERT/UPDATE trigger using tstzrange | Only DB-level enforcement is race-safe under concurrent edits |
| Active-rule index | Partial index on `(rule_id, source_id) WHERE effective_to IS NULL` + covering temporal index | Partial index handles the dominant query; temporal index handles "as-of" queries |
| Row deletion policy | Never delete; deprecate via effective_to | Historical computes' FK would fail; retention of provenance is non-negotiable |
| Canonical JSON includes rule_body only? Or whole row? | rule_body only | Other columns (citation, classical_names) can evolve without semantic change; hashing them would cause churn |
| What if author sets effective_from in the past (retro-activation)? | Allowed; trigger still checks for overlap with pre-existing rows | Retro-active rule activations are rare but legal; the trigger handles it |
| Test fixtures: shared or per-test? | Per-test with factory | Temporal tests need many time-shifted rows; shared fixtures accumulate state |

## 5. Component Design

### 5.1 New modules

```
src/josi/services/classical/
├── canonical_json.py           # JCJ canonicalization + sha256 hashing
├── rule_version.py             # semver parsing, comparison, bump validation
└── rule_temporal.py            # "active at time T" resolver + helpers

src/josi/schemas/classical/
└── rule_version_schema.py      # Pydantic wrappers for version strings
```

### 5.2 Data model amendment

F2's `classical_rule` table already declares `effective_from`, `effective_to`, `content_hash`, `version`. F4 adds trigger + additional partial indexes; no new columns.

```sql
-- ============================================================
-- F4 migration: trigger + indexes on classical_rule (table exists from F2)
-- ============================================================

-- Partial unique index: at most one active (effective_to NULL) version per (rule_id, source_id)
CREATE UNIQUE INDEX idx_classical_rule_one_active
    ON classical_rule (rule_id, source_id)
    WHERE effective_to IS NULL;

-- Temporal lookup index: supports "active at time T" with WHERE clause
CREATE INDEX idx_classical_rule_temporal
    ON classical_rule (rule_id, source_id, effective_from DESC, effective_to);

-- Overlap-prevention trigger (handles closed-interval overlap cases)
CREATE OR REPLACE FUNCTION check_rule_version_no_overlap()
RETURNS trigger AS $$
DECLARE
    overlap_count INT;
BEGIN
    -- Skip check if version AND PK match (trivial UPDATE path)
    IF (TG_OP = 'UPDATE' AND OLD.version = NEW.version) THEN
        -- still must check, because effective window may have changed
        NULL;
    END IF;

    SELECT COUNT(*) INTO overlap_count
      FROM classical_rule
     WHERE rule_id = NEW.rule_id
       AND source_id = NEW.source_id
       AND version <> NEW.version
       AND tstzrange(
             NEW.effective_from,
             COALESCE(NEW.effective_to, 'infinity'::timestamptz),
             '[)'
           ) && tstzrange(
             effective_from,
             COALESCE(effective_to, 'infinity'::timestamptz),
             '[)'
           );
    IF overlap_count > 0 THEN
        RAISE EXCEPTION
          'classical_rule version overlap: (rule_id=%, source_id=%) new [%..%) conflicts with existing version',
          NEW.rule_id, NEW.source_id,
          NEW.effective_from,
          COALESCE(NEW.effective_to::text, 'open');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_rule_version_no_overlap
    BEFORE INSERT OR UPDATE ON classical_rule
    FOR EACH ROW EXECUTE FUNCTION check_rule_version_no_overlap();

-- Content-hash sanity: enforce length and hex characters (not full crypto check, just format)
ALTER TABLE classical_rule
    ADD CONSTRAINT ck_classical_rule_content_hash_format
    CHECK (content_hash ~ '^[0-9a-f]{64}$');

-- Semver format constraint
ALTER TABLE classical_rule
    ADD CONSTRAINT ck_classical_rule_version_semver
    CHECK (version ~ '^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(-[0-9A-Za-z\.-]+)?(\+[0-9A-Za-z\.-]+)?$');

-- Effective-window sanity
ALTER TABLE classical_rule
    ADD CONSTRAINT ck_classical_rule_effective_window
    CHECK (effective_to IS NULL OR effective_to > effective_from);
```

### 5.3 Canonical JSON + hash

```python
# src/josi/services/classical/canonical_json.py

import hashlib
import json
import math
from typing import Any


class CanonicalJSONError(ValueError):
    """Raised when a value cannot be canonicalized (NaN/Infinity, unsupported types)."""


def canonical_json(obj: Any) -> bytes:
    """Serialize obj to Josi Canonical JSON (JCJ) bytes.

    Spec:
      - UTF-8, no BOM
      - Object keys lexicographically sorted by Unicode code point ascending
      - Arrays preserved in source order
      - Numbers in shortest decimal form (no trailing .0 for ints)
      - NaN / Infinity raise CanonicalJSONError
      - No whitespace outside strings
      - No trailing newline
    """
    _assert_finite(obj)
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def content_hash(obj: Any) -> str:
    """Return sha256 hex digest of canonical_json(obj). 64 lowercase hex chars."""
    return hashlib.sha256(canonical_json(obj)).hexdigest()


def _assert_finite(obj: Any) -> None:
    if isinstance(obj, float) and not math.isfinite(obj):
        raise CanonicalJSONError(f"NaN/Infinity not allowed in canonical JSON: {obj}")
    if isinstance(obj, dict):
        for v in obj.values():
            _assert_finite(v)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            _assert_finite(v)
```

### 5.4 Semver helpers

```python
# src/josi/services/classical/rule_version.py

from dataclasses import dataclass
from enum import Enum
from packaging.version import Version, InvalidVersion


class VersionBump(str, Enum):
    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"
    NONE = "none"


@dataclass(frozen=True)
class RuleVersion:
    major: int
    minor: int
    patch: int

    @classmethod
    def parse(cls, s: str) -> "RuleVersion":
        try:
            v = Version(s)
        except InvalidVersion as e:
            raise ValueError(f"invalid semver {s!r}") from e
        if len(v.release) != 3:
            raise ValueError(f"semver must be X.Y.Z; got {s!r}")
        return cls(major=v.release[0], minor=v.release[1], patch=v.release[2])

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def bump_kind(self, other: "RuleVersion") -> VersionBump:
        """Describes how `other` relates to `self`. Expects other > self."""
        if other == self:
            return VersionBump.NONE
        if other.major > self.major:
            return VersionBump.MAJOR
        if other.minor > self.minor:
            return VersionBump.MINOR
        return VersionBump.PATCH
```

### 5.5 Temporal resolver

```python
# src/josi/services/classical/rule_temporal.py

from datetime import datetime, timezone
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from josi.models.classical.classical_rule import ClassicalRule


class RuleNotActiveError(LookupError):
    """Raised when no rule version is active at the requested time."""


async def resolve_active_rule(
    session: AsyncSession,
    rule_id: str,
    source_id: str,
    as_of: datetime | None = None,
) -> ClassicalRule:
    """Return the single active rule row for (rule_id, source_id) at `as_of`.

    If as_of is None, uses current UTC time. Raises RuleNotActiveError if none.
    The overlap trigger guarantees at most one match.
    """
    as_of = as_of or datetime.now(timezone.utc)
    stmt = (
        select(ClassicalRule)
        .where(ClassicalRule.rule_id == rule_id)
        .where(ClassicalRule.source_id == source_id)
        .where(ClassicalRule.effective_from <= as_of)
        .where(
            (ClassicalRule.effective_to.is_(None))
            | (ClassicalRule.effective_to > as_of)
        )
    )
    row = (await session.execute(stmt)).scalar_one_or_none()
    if row is None:
        raise RuleNotActiveError(
            f"no active version of rule {rule_id!r} from source {source_id!r} at {as_of.isoformat()}"
        )
    return row


async def list_versions(
    session: AsyncSession, rule_id: str, source_id: str
) -> list[ClassicalRule]:
    """All versions, newest effective_from first."""
    stmt = (
        select(ClassicalRule)
        .where(ClassicalRule.rule_id == rule_id)
        .where(ClassicalRule.source_id == source_id)
        .order_by(ClassicalRule.effective_from.desc())
    )
    return list((await session.execute(stmt)).scalars())
```

### 5.6 Rule loader (F6) contract consumed here

The rule loader (detailed in F6) will call `content_hash(rule_body)` from this module, compare with the YAML-declared value, and use `resolve_active_rule` to check whether a new version is needed. F4 exposes:

- `canonical_json(obj) -> bytes`
- `content_hash(obj) -> str`
- `RuleVersion.parse(s).bump_kind(other)`
- `resolve_active_rule(session, rule_id, source_id, as_of)`
- `list_versions(session, rule_id, source_id)`

## 6. User Stories

### US-F4.1: As an engineer, I want content_hash to be deterministic across Python runs, processes, and machines
**Acceptance:** given identical `rule_body`, `content_hash(body)` returns the same 64-char hex string on any machine, any Python 3.12+ process, any run.

### US-F4.2: As a rule author, I want the system to reject a YAML that changes `rule_body` without bumping the version
**Acceptance:** editing a rule YAML's semantics while keeping the version unchanged: CI test computes hash, compares with the DB's current row for that version, fails with a clear message pointing at the mismatched hash.

### US-F4.3: As a rule author, I want to schedule a new version to activate at a future time
**Acceptance:** inserting v1.1.0 with `effective_from = 2026-07-01` and v1.0.0's `effective_to = 2026-07-01` succeeds (adjacent, non-overlapping). Between now and 2026-07-01, `resolve_active_rule(..., now())` returns v1.0.0; from 2026-07-01 onward, it returns v1.1.0.

### US-F4.4: As an engineer, I want the DB to refuse two active versions of the same rule from the same source
**Acceptance:** inserting v1.1.0 with `effective_to=NULL` while v1.0.0 exists with `effective_to=NULL` raises an exception from `trg_rule_version_no_overlap` with a message identifying both versions.

### US-F4.5: As an auditor, I want `technique_compute` rows computed in 2025 against rule v1.0.0 to remain resolvable forever
**Acceptance:** five years after v1.0.0 is deprecated (effective_to = 2025-12-31), a 2025 `technique_compute` row still JOINs successfully to its `classical_rule` row. The FK from compute → rule is never broken.

### US-F4.6: As an engineer, I want "what rule was active on date X?" to be a constant-time query
**Acceptance:** `resolve_active_rule(..., as_of=X)` generates a query whose EXPLAIN shows an Index Scan on `idx_classical_rule_temporal` with 1 row returned; runtime P99 < 5ms at 100k rules.

## 7. Tasks

### T-F4.1: Canonical JSON + hash module
- **Definition:** Implement `canonical_json(obj) -> bytes` and `content_hash(obj) -> str` per §5.3. Raise `CanonicalJSONError` on NaN/Infinity. No external deps beyond stdlib.
- **Acceptance:** All unit tests in §8.1 pass. Module is importable as `from josi.services.classical.canonical_json import content_hash`.
- **Effort:** 3 hours
- **Depends on:** none

### T-F4.2: RuleVersion parser + bump classifier
- **Definition:** Implement `RuleVersion.parse()` and `bump_kind()` per §5.4. Validate strict `MAJOR.MINOR.PATCH` format (reject pre-release / build identifiers in P0).
- **Acceptance:** Tests in §8.2 pass. `RuleVersion("1.0.0").bump_kind(RuleVersion("2.0.0")) == MAJOR`.
- **Effort:** 2 hours
- **Depends on:** none

### T-F4.3: Overlap prevention trigger + indexes migration
- **Definition:** Autogenerate Alembic migration; hand-add the plpgsql function, trigger, partial unique index, temporal index, content_hash format CHECK, semver CHECK, effective_window CHECK.
- **Acceptance:** Migration upgrades clean from F3 state; downgrades cleanly drop trigger + function + indexes + CHECKs.
- **Effort:** 4 hours
- **Depends on:** F2, F3 complete

### T-F4.4: Temporal resolver service
- **Definition:** Implement `resolve_active_rule()` and `list_versions()` per §5.5 using the project's async session pattern.
- **Acceptance:** Tests in §8.4 pass. Queries use the new temporal index (verified via EXPLAIN).
- **Effort:** 3 hours
- **Depends on:** T-F4.3

### T-F4.5: SQLModel updates
- **Definition:** Ensure `ClassicalRule` SQLModel exposes `effective_from`, `effective_to`, `version`, `content_hash` as typed fields. Add SQLAlchemy listeners that do NOT compute hash (hashing happens at loader / application layer, not at ORM write time, to keep writes explicit).
- **Acceptance:** Fields present, typed correctly (`datetime | None` for effective_to, `str` for content_hash). mypy passes.
- **Effort:** 2 hours
- **Depends on:** T-F4.3

### T-F4.6: Integration test — full temporal lifecycle
- **Definition:** Test that seeds rule v1.0.0, computes a row against it, deprecates v1.0.0 (sets effective_to=now), inserts v1.1.0 (effective_from=now), computes a row against v1.1.0, and verifies both compute rows remain retrievable and resolvable to their correct rule versions.
- **Acceptance:** Test passes; both compute rows JOIN correctly; `resolve_active_rule` returns v1.1.0 at "now + 1 hour" and would have returned v1.0.0 at "now - 1 day".
- **Effort:** 3 hours
- **Depends on:** T-F4.4, T-F4.5

### T-F4.7: Property-based tests for canonicalization determinism
- **Definition:** Using Hypothesis (F17), generate arbitrary JSON-compatible Python objects (dicts of str→int|str|list|nested-dict, lists of ints, strings) and verify `content_hash(obj) == content_hash(deepcopy(obj))` and that re-parsing `canonical_json(obj)` back into Python and re-canonicalizing yields the identical bytes.
- **Acceptance:** 1000+ generated examples all produce deterministic hashes. NaN/Infinity generators produce `CanonicalJSONError`.
- **Effort:** 3 hours
- **Depends on:** T-F4.1, F17

### T-F4.8: Documentation of semver policy
- **Definition:** Add `docs/markdown/rule-authoring-semver.md` with the §3.4 semantics + examples.
- **Acceptance:** Doc exists, referenced from CLAUDE.md under "Rule versioning".
- **Effort:** 1 hour
- **Depends on:** T-F4.2

## 8. Unit Tests

### 8.1 canonical_json module

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_keys_sorted_lex` | `{"b": 1, "a": 2}` | `b'{"a":2,"b":1}'` | ordering contract |
| `test_nested_keys_sorted_lex` | `{"z": {"b": 1, "a": 2}, "a": 3}` | `b'{"a":3,"z":{"a":2,"b":1}}'` | recursive sorting |
| `test_arrays_preserve_order` | `[3, 1, 2]` | `b'[3,1,2]'` | arrays are ordered |
| `test_unicode_not_ascii_escaped` | `{"name": "Śiva"}` | bytes include UTF-8 bytes of Ś | non-ASCII preserved |
| `test_bool_null` | `{"x": None, "y": True, "z": False}` | `b'{"x":null,"y":true,"z":false}'` | JSON literal mapping |
| `test_nan_raises` | `{"x": float("nan")}` | `CanonicalJSONError` | spec rejects NaN |
| `test_infinity_raises` | `{"x": float("inf")}` | `CanonicalJSONError` | spec rejects Infinity |
| `test_no_whitespace_between_tokens` | `{"a": 1}` | `b'{"a":1}'` (no spaces) | separators=(",",":") |
| `test_hash_is_64_hex_lowercase` | any valid input | return value matches `^[0-9a-f]{64}$` | format contract |
| `test_hash_determinism_across_dict_construction_order` | `{"a": 1, "b": 2}` vs `{"b": 2, "a": 1}` | identical hash | sort_keys contract |
| `test_hash_changes_on_value_change` | `{"a": 1}` vs `{"a": 2}` | different hash | detects tampering |
| `test_hash_stable_python_3_12_3_13` | known fixture → known hex | matches documented value | no silent algorithm drift |

### 8.2 RuleVersion

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_parse_valid` | `"1.2.3"` | `RuleVersion(1, 2, 3)` | happy path |
| `test_parse_rejects_two_parts` | `"1.2"` | `ValueError` | strict X.Y.Z |
| `test_parse_rejects_pre_release` | `"1.2.3-alpha"` | `ValueError` | P0 rejects pre-release suffixes |
| `test_str_roundtrip` | `RuleVersion.parse("1.0.0")` | `str(v) == "1.0.0"` | string fidelity |
| `test_bump_kind_major` | `v(1,0,0).bump_kind(v(2,0,0))` | `VersionBump.MAJOR` | semantic |
| `test_bump_kind_minor` | `v(1,0,0).bump_kind(v(1,1,0))` | `VersionBump.MINOR` | semantic |
| `test_bump_kind_patch` | `v(1,0,0).bump_kind(v(1,0,1))` | `VersionBump.PATCH` | semantic |
| `test_bump_kind_none` | `v(1,0,0).bump_kind(v(1,0,0))` | `VersionBump.NONE` | equal versions |

### 8.3 Overlap trigger

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_insert_v1_0_0_then_v1_1_0_adjacent` | v1.0.0 (effective_to = T); v1.1.0 (effective_from = T) | both inserts succeed | adjacent windows OK |
| `test_insert_two_open_ended_rejected` | v1.0.0 (to=NULL); v1.1.0 (to=NULL) | trigger raises | canonical bad case |
| `test_insert_overlapping_closed_rejected` | v1.0.0 [A..C); v1.1.0 [B..D) with A<B<C<D | trigger raises | half-open overlap |
| `test_update_effective_to_creating_overlap_rejected` | v1.0.0 [A..B); v1.1.0 [B..C); then UPDATE v1.0.0 effective_to = D > B | trigger raises | updates are checked too |
| `test_insert_future_v2_with_retroactive_v1_prevents_gap` | v1 [A..C); v2 [B..∞) with A<B<C | trigger raises | retroactive overlap caught |
| `test_insert_same_version_twice_rejected` | v1.0.0 inserted; v1.0.0 again | PK violation | PK covers |
| `test_trigger_allows_many_versions_with_proper_windows` | v1.0.0 [T1..T2); v1.1.0 [T2..T3); v1.2.0 [T3..∞) | all succeed | legitimate sequence |

### 8.4 resolve_active_rule

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_resolves_current_version_at_now` | v1.0.0 [T0..NULL); as_of=now | returns v1.0.0 | dominant query path |
| `test_resolves_historical_version_at_past_date` | v1.0.0 [T0..T1); v1.1.0 [T1..NULL); as_of=T0+1 day | returns v1.0.0 | historical replay |
| `test_resolves_new_version_after_promotion` | same fixture; as_of=T1+1 day | returns v1.1.0 | newer wins |
| `test_no_active_version_raises` | v1.0.0 [T0..T1); as_of=T1+1 day (no v1.1.0) | `RuleNotActiveError` | gap state visible |
| `test_multiple_sources_isolated` | bphs/v1 active; saravali/v1 active | each resolves to its own | FK correctness |
| `test_explain_uses_temporal_index` | EXPLAIN of resolve_active_rule query | plan contains `idx_classical_rule_temporal` | index effectiveness |

### 8.5 Content-hash validation workflow

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_hash_matches_yaml_declared` | load rule with matching declared hash | load succeeds | happy path |
| `test_hash_mismatch_rejects_load` | declared hash differs from computed | load aborts; error mentions computed hash | tamper detection |
| `test_hash_on_reload_matches_db_row` | insert rule, re-compute hash from in-memory body, compare with DB content_hash | equal | no drift through INSERT |
| `test_hash_format_constraint_enforced_at_db` | INSERT with `content_hash='nothex'` | DB CHECK violation | defensive |

### 8.6 Property-based (Hypothesis)

| Test name | Strategy | Expected invariant | Rationale |
|---|---|---|---|
| `test_hash_determinism_hypothesis` | JSON-serializable Python dicts with nested dicts/lists | `content_hash(obj)` == `content_hash(deepcopy(obj))` | bulletproof determinism |
| `test_canonicalize_roundtrip_stable` | arbitrary JSON objects | `canonical_json(json.loads(canonical_json(obj).decode()))` == `canonical_json(obj)` | idempotent |
| `test_key_reorder_does_not_change_hash` | dict + random key shuffle | identical hashes | sort_keys contract holds under any input |
| `test_nan_or_inf_always_raises` | floats filtered to NaN/Inf | `CanonicalJSONError` | edge case coverage |

### 8.7 Integration — full lifecycle

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_deprecate_and_replace_preserves_historical_computes` | seed v1; insert compute row; set v1.effective_to=now; insert v1.1.0; insert compute row against v1.1.0 | both compute rows JOIN; counts correct | end-to-end provenance |
| `test_future_promotion_window_respected` | v1 open; schedule v2 with effective_from = now+1h and v1.effective_to = now+1h | `resolve_active_rule(now)` == v1; `resolve_active_rule(now+2h)` == v2 | scheduled promotion |
| `test_rollback_via_reopening_v1` | deprecate v2 (effective_to=now); insert new v1 row with effective_from=now | resolves v1 from now forward | rollback path |

## 9. EPIC-Level Acceptance Criteria

- [ ] `classical_rule` has trigger `trg_rule_version_no_overlap` enforcing temporal non-overlap of distinct versions of same (rule_id, source_id)
- [ ] Partial unique index `idx_classical_rule_one_active` on `(rule_id, source_id) WHERE effective_to IS NULL` exists
- [ ] Temporal index `idx_classical_rule_temporal` supports "active at T" queries at P99 < 5ms at 100k rules
- [ ] CHECK constraint enforces `content_hash` format `^[0-9a-f]{64}$`
- [ ] CHECK constraint enforces semver format `MAJOR.MINOR.PATCH` (no pre-release)
- [ ] CHECK constraint enforces `effective_to IS NULL OR effective_to > effective_from`
- [ ] `canonical_json(obj)` and `content_hash(obj)` are deterministic (Hypothesis property tests pass with ≥1000 examples)
- [ ] `RuleVersion.parse` + `.bump_kind()` classify MAJOR/MINOR/PATCH correctly
- [ ] `resolve_active_rule(session, rule_id, source_id, as_of)` returns exactly one row or raises `RuleNotActiveError`
- [ ] Integration test: deprecate v1 + insert v1.1 + retain historical compute rows all resolve correctly
- [ ] Unit test coverage ≥ 95% for `canonical_json`, `rule_version`, `rule_temporal` modules
- [ ] Documentation: `docs/markdown/rule-authoring-semver.md` + CLAUDE.md reference
- [ ] Golden-chart suite gains a fixture covering version migration scenarios (invoked by F16)

## 10. Rollout Plan

- **Feature flag:** none — P0 foundation; schema change required unconditionally.
- **Shadow compute:** N/A (no computation yet at F4 time; rules haven't been authored yet).
- **Backfill strategy:** N/A (empty `classical_rule` table at F4 time). F6's rule loader will populate on first deploy.
- **Rollback plan:** `alembic downgrade -1` drops trigger, function, CHECKs, and partial indexes. Safe at P0. In a production-with-data scenario, rollback would leave the table functional but un-protected against overlap — acceptable as a recovery mode.

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Author forgets to bump version when semantics change | Medium | High | F6 loader compares computed hash with DB; mismatch fails deploy |
| Trigger performance degrades at 100k+ rules | Low | Medium | Trigger is O(log N) via index on (rule_id, source_id); only runs on INSERT/UPDATE, not read |
| Clock skew between dev machines produces different `effective_from` timestamps than expected | Low | Low | Use server `now()` in SQL where possible; author specifies explicit UTC in YAML |
| Python JSON encoder changes behavior between versions | Low | High | Hypothesis tests pin hash values for known fixtures; CI catches regression |
| Semver parser rejects valid PEP 440 forms we want to support later | Medium | Medium | Strict parser in P0; extend later if we need pre-release suffixes |
| Retro-active rule activation surprises astrologers | Medium | Medium | UI shows effective_from date; rule loader logs retroactive activations |
| Overlap trigger raises on rapid UPDATE of effective_to window | Low | Low | Documented: UPDATE window requires coordinated sequence |
| content_hash stored in DB diverges from YAML (race during deploy) | Low | High | Loader computes from YAML and asserts match with DB on load; fail deploy on mismatch |

## 12. References

- Master spec: [`docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`](../../../superpowers/specs/2026-04-19-classical-techniques-expansion-design.md) §2.4 (versioning everything), §2.5 (content-hash provenance)
- Related PRDs: [F1](./F1-star-schema-dimensions.md), [F2](./F2-fact-tables.md), F6 (rule loader), F13 (content-hash provenance chain), P3-E6-flag (shadow rollout), S8 (shadow-compute rule migrations)
- Snodgrass, R. T., *Developing Time-Oriented Database Applications in SQL* (1999), Ch. 2–4
- RFC 8259 (The JavaScript Object Notation Data Interchange Format)
- Josi Canonical JSON spec (this document, §3.2)
- Semver 2.0.0: https://semver.org
- PostgreSQL `tstzrange` operators: https://www.postgresql.org/docs/17/rangetypes.html
