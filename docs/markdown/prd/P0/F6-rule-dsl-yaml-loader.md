---
prd_id: F6
epic_id: F6
title: "Rule DSL: YAML format, loader, content-hash"
phase: P0-foundation
tags: [#extensibility, #correctness, #i18n]
priority: must
depends_on: [F1, F2, F4]
enables: [F7, F8, F13, E1a, E2a, E4a, E6a, E14a, P3-E2-console]
classical_sources: [bphs, saravali, phaladeepika, jataka_parijata, jaimini_sutras, tajaka_neelakanthi]
estimated_effort: 4-5 days
status: draft
author: @agent
last_updated: 2026-04-19
---

# F6 — Rule DSL: YAML Format, Loader, Content-Hash

## 1. Purpose & Rationale

Classical rules — yogas, dasa rules, tajaka yogas, sahams, jaimini definitions, aspect schemes — are the crown jewels of Josi's calculation engine. We must be able to:

1. **Author rules without writing code.** A classical advisor who knows Sanskrit but not Python must be able to propose `Gaja Kesari Yoga` via a PR-reviewable YAML file.
2. **Version rules independently from engine code.** A rule's logic may change (new citation discovered, disagreement in a commentary) without a code deploy.
3. **Content-address rules.** Every rule gets a `content_hash` so `technique_compute` rows can point at the *exact* rule revision that produced them (F13 provenance).
4. **Validate rule bodies before they reach production.** A rule referring to an undefined predicate must fail CI — not at compute time for an end-user.
5. **Support the 1000-yoga reference set long term.** The DSL must scale to thousands of rules across six traditions without engineering bottleneck.

The alternative — expressing rules as Python functions — fails all five requirements. It forces a deploy for every rule change, collapses advisor/engineer roles, prevents content-hashing, cannot be validated statically as declarative predicates can, and does not scale to non-engineer authorship.

This PRD defines the YAML format, the **predicate vocabulary** (the shared library of atoms rules compose from), the loader that ingests YAMLs into the `classical_rule` table (F2), and the content-hash algorithm that pins each row to a canonical byte-level identity.

## 2. Scope

### 2.1 In scope
- Complete YAML grammar for rule documents (structure, required fields, semantics)
- Complete YAML grammar for **predicate-library documents** — the shared vocabulary of atoms (e.g., `moon_in_kendra_from`, `planet_not_debilitated`) that rule bodies reference
- Boolean combinators: `all_of`, `any_of`, `none_of`, `not`
- Strength-formula combinators: `weighted_average`, `max`, `min`, `product`, `piecewise`, `constant`
- `RuleRegistryLoader` service — discovers YAMLs, validates, computes `content_hash`, upserts `classical_rule` rows with `effective_from` handling
- Canonical-JSON + SHA-256 content-hash algorithm (deterministic, platform-independent)
- Conflict handling: duplicate `(rule_id, source_id, version)` with differing `content_hash` → abort with clear error
- Dev-mode watch: auto-reload on YAML file change (uvicorn reload hook)
- Unit + integration tests covering grammar, validation, content-hash stability, reload

### 2.2 Out of scope
- **JSON Schema for rule_body payloads** — owned by F5 (insert-time validation); this PRD produces the rule body, F5 enforces shape.
- **Output-shape JSON Schemas** — owned by F7 (validates the `result` a rule produces at compute time).
- **Aggregation strategy plugins** — owned by F8.
- **Rule-authoring GUI console** — deferred to P3 (P3-E2-console).
- **Executing rules against a chart** — engines (E1a/E2a/E4a/etc.) consume the registry; this PRD only loads it.
- **Predicate implementation functions** — each engine owns the Python functions for predicates its family uses; this PRD defines the *declarations* only.

### 2.3 Dependencies
- F1 — `source_authority`, `technique_family`, `output_shape` dim tables (FK targets)
- F2 — `classical_rule` fact table (target of upsert)
- F4 — temporal versioning (`effective_from`/`effective_to` semantics)
- PyYAML (already in `pyproject.toml`), `pydantic` (already present), `jsonschema` library (needs add)

## 3. Technical Research

### 3.1 Why a declarative YAML DSL (not Python, not JSON)

| Candidate | Rejected because |
|---|---|
| **Python functions** as rules | Non-engineers cannot author; requires deploy per change; cannot content-hash a function body meaningfully (whitespace, imports, Python version); cannot statically validate. |
| **JSON** rule files | Humans don't read/write JSON comfortably for multi-line citations and Devanagari text; no comments; quote-heavy. |
| **Pure Python dict with DSL functions (`all_of(moon_in_kendra_from("jupiter"), …)`)** | Tempting but re-introduces Python dependency for authoring; no PR-reviewability for non-engineers. |
| **Custom binary DSL (protobuf, capnp)** | Overkill; no human-authoring story. |
| **YAML (selected)** | Human-readable, PR-reviewable, supports multi-line strings (`|` block literal), supports comments, native Unicode (Devanagari/Tamil), Pydantic-parseable, diff-friendly. |

### 3.2 Why predicates are declared separately from rules

A rule like *Gaja Kesari Yoga* references the predicate `moon_in_kendra_from(of=jupiter)`. That predicate is itself a small classical concept ("Moon is in 1/4/7/10 from Jupiter") with a Sanskrit name, a citation, and a typed signature.

If we inlined predicate logic in every rule YAML, we would:
- Duplicate the predicate definition across 40+ rules that use it
- Lose the ability to audit "every rule that uses predicate X" when we realize X has a bug
- Lose the invariant "predicate X is implemented once in Python"

So we split the DSL into **two document types**:
- **predicate documents** — declare the vocabulary: name, Sanskrit translations, citation, typed parameters, reference to the Python implementation symbol
- **rule documents** — compose those predicates via combinators

This is the same pattern as SQL functions vs SQL queries.

### 3.3 Content-hash algorithm

Requirements:
- **Deterministic** — same rule YAML → same hash on any machine, any OS, any Python version.
- **Insensitive to cosmetic YAML diffs** — key ordering, whitespace, comments, trailing newlines must NOT change the hash. A reformatting PR must not invalidate every compute row.
- **Sensitive to semantic diffs** — any change to a predicate name, parameter value, combinator structure, `source_id`, or `version` MUST change the hash.

Approach:
1. Parse YAML → Python dict.
2. **Drop documentation-only keys** from the hash input: `classical_names`, `citation`, `notes`, `examples`. These are human-facing metadata; changing "BPHS Ch.36 v.14-16" to "BPHS 36.14-16" should not invalidate compute. *(Note: the `rule_id`, `source_id`, `version` themselves ARE hashed — they are semantic identity.)*
3. Recursively canonicalize: sort all dict keys; convert floats to `repr()` with up to 17 significant digits (shortest round-trippable form); represent booleans as `true`/`false` (lowercase), nulls as `null`.
4. Serialize via `json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False)`.
5. Encode UTF-8 → `hashlib.sha256(...).hexdigest()` → 64 lowercase hex chars.

This matches the RFC 8785 JCS approach in spirit (the Python ecosystem's closest equivalent).

### 3.4 Loader placement

```
src/josi/rules/                            # YAML content lives here (checked into git)
├── predicates/
│   ├── vedic_core.yaml
│   ├── jaimini_core.yaml
│   └── tajaka_core.yaml
├── yogas/
│   ├── bphs/
│   │   └── raja/
│   │       └── gaja_kesari.yaml
│   ├── saravali/
│   └── phaladeepika/
├── dasas/
│   └── ...
└── sahams/
    └── ...

src/josi/services/classical/
├── rule_registry_loader.py                # main service
├── rule_canonicalizer.py                  # content_hash computation
└── predicate_registry.py                  # in-memory predicate lookup
```

Directory layout is authoritative — a YAML's location hints its technique family but the YAML body is the source of truth.

### 3.5 Alternatives considered for loader trigger

| Trigger | Chosen? | Rationale |
|---|---|---|
| On FastAPI startup (lifespan event) | **Yes** | Same pattern as F1 `DimensionLoader`; consistent with dim seeding; fail-fast. |
| Alembic migration step | No | Rule count grows to thousands; don't want to run on every `alembic upgrade head`. |
| Manual CLI only | No | Risk of drift between YAML and DB across environments. |
| On every API request | No | Latency, lock contention. |

Dev-mode watch (uvicorn `--reload`) additionally calls the loader when a YAML file changes — incremental upsert only.

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| YAML vs TOML vs JSON | YAML | Only one with native multi-line + Devanagari + comments + PR-reviewability. |
| Predicate definitions inline vs separate | Separate (`predicates/*.yaml`) | Single source of truth per predicate; auditability. |
| Content-hash includes documentation | **No** — excludes `classical_names`, `citation`, `notes`, `examples` | Cosmetic edits must not invalidate compute. Semantic fields (rule_id, source_id, version, rule_body, output_shape_id, technique_family_id) are hashed. |
| Floats in canonical JSON | `repr()` (shortest round-trippable) | Language-independent; Python, JS, Go agree on the spelling. |
| Duplicate `(rule_id, source_id, version)` with different content | **Abort load with error** | Silent overwrite destroys provenance. Authors must bump `version`. |
| Missing predicate reference | Abort load (fail-fast) | A rule that cannot evaluate cannot ship. |
| Watch mode in prod | **No** — dev only | Prod loads once at startup; rule changes ship via deploy. |
| Effective_from in the past | Allowed | Backfill of historical rule revisions is a real use case. |
| Effective_from in the future | Allowed | Supports timed rollouts (ship Tuesday; activates Monday). |
| Rule without predicate (pure strength formula) | Allowed — `activation` is optional | Some "rules" are pure numeric computations (e.g., bhava bala). |
| Semver validation on `version` field | Yes, `^\d+\.\d+\.\d+(-\w+)?$` regex | Consistency across rules. |

## 5. Component Design

### 5.1 New modules

```
src/josi/rules/                                    # (content root, not code)
src/josi/services/classical/
├── rule_registry_loader.py
├── rule_canonicalizer.py
├── predicate_registry.py
└── dsl_schemas.py                                 # Pydantic models for DSL validation
src/josi/cli/
└── validate_rules.py                              # CI command: poetry run validate-rules
```

### 5.2 Rule document grammar (complete)

```yaml
# src/josi/rules/yogas/bphs/raja/gaja_kesari.yaml
rule_id: yoga.raja.gaja_kesari                     # globally unique; dot.separated.namespace
source_id: bphs                                    # FK → source_authority(source_id)
version: 1.0.0                                     # semver; bump for any semantic change
technique_family_id: yoga                          # FK → technique_family(family_id)
output_shape_id: boolean_with_strength             # FK → output_shape(shape_id)

citation: "BPHS Ch.36 v.14-16"                     # free text, not hashed
classical_names:                                    # free text per language, not hashed
  en: "Gaja Kesari Yoga"
  sa_iast: "gajakesarī-yoga"
  sa_devanagari: "गजकेसरी-योग"
  ta: "கஜகேசரி யோகம்"

notes: |                                           # optional free text, not hashed
  Classical Raja Yoga formed when Moon is in a kendra (1/4/7/10) from Jupiter,
  provided Jupiter is not debilitated or combust.
examples:                                          # optional: canonical chart IDs that activate this rule
  - chart_id: golden.bphs.gaja_kesari_01
    expected_active: true

effective_from: "2026-04-19T00:00:00Z"             # UTC ISO-8601; defaults to now() if omitted
effective_to: null                                 # null = still active

rule_body:                                         # the hashed core
  activation:                                      # optional; omitted for pure-numeric rules
    all_of:
      - predicate: moon_in_kendra_from
        of: jupiter
      - predicate: planet_not_debilitated
        planet: jupiter
      - predicate: planet_not_combust
        planet: jupiter
  strength_formula:                                # required for boolean_with_strength shape
    type: weighted_average
    inputs:
      - value:
          call: planet_dignity_score
          args: { planet: jupiter }
        weight: 0.5
      - value:
          call: planet_dignity_score
          args: { planet: moon }
        weight: 0.5
    clamp: [0, 1]
```

#### 5.2.1 Required fields (top-level)

| Field | Type | Required | Hashed? |
|---|---|---|---|
| `rule_id` | dotted-string | yes | yes |
| `source_id` | FK to `source_authority` | yes | yes |
| `version` | semver string | yes | yes |
| `technique_family_id` | FK to `technique_family` | yes | yes |
| `output_shape_id` | FK to `output_shape` | yes | yes |
| `rule_body` | object | yes | yes |
| `citation` | string | no | no |
| `classical_names` | object of lang→string | no | no |
| `notes` | string (block) | no | no |
| `examples` | list of objects | no | no |
| `effective_from` | ISO-8601 UTC | no (default `now()`) | yes |
| `effective_to` | ISO-8601 UTC or null | no (default null) | yes |

#### 5.2.2 Rule-body grammar

A `rule_body` is an object with two optional-but-one-required subkeys:

- `activation` — a boolean expression over predicates. Evaluates to `true`/`false`.
- `strength_formula` — a numeric expression. Evaluates to a float (usually clamped `[0,1]`).

At least one of `activation` or `strength_formula` must be present. Shape-specific rules:

| `output_shape_id` | Must have `activation`? | Must have `strength_formula`? |
|---|---|---|
| `boolean_with_strength` | yes | yes |
| `numeric` | no | yes |
| `numeric_matrix` | no | yes (returns matrix) |
| `temporal_range`, `temporal_event`, `temporal_hierarchy` | no | yes (returns temporal) |
| `structured_positions` | no | yes (returns positions) |
| `annual_chart_summary` | no | yes |
| `cross_chart_relations` | no | yes |
| `categorical` | no | yes |

(F7 enforces the per-shape output constraints; F5 enforces the insert-time validation.)

#### 5.2.3 Boolean combinators

```yaml
activation:
  # Exactly one of the following keys at each node:
  all_of: [ <clause>, <clause>, ... ]     # ∧
  any_of: [ <clause>, <clause>, ... ]     # ∨
  none_of: [ <clause>, <clause>, ... ]    # ¬(∨)
  not:    <clause>                         # ¬
  predicate: <predicate_name>              # leaf; remaining keys are named args
```

Each `<clause>` is itself either a combinator or a predicate leaf. Nesting is unbounded.

#### 5.2.4 Strength-formula combinators

```yaml
strength_formula:
  type: weighted_average | max | min | product | piecewise | constant | call
  # type: constant
  value: 0.5
  # type: call — direct engine function
  call: function_name                      # e.g., planet_dignity_score
  args: { planet: moon, ... }
  # type: weighted_average | max | min | product
  inputs:
    - value: <number | call | nested formula>
      weight: <number>                     # only for weighted_average
  clamp: [min, max]                        # optional; applied after combine
  # type: piecewise
  input: <number | call>
  pieces:
    - { when: "<= 0.3", then: 0.0 }
    - { when: "<= 0.6", then: 0.5 }
    - { when: ">  0.6", then: 1.0 }
```

The grammar is captured completely by Pydantic discriminated unions in `dsl_schemas.py`.

### 5.3 Predicate document grammar

```yaml
# src/josi/rules/predicates/vedic_core.yaml
predicates:
  - name: moon_in_kendra_from
    signature:
      of: { type: planet }                 # typed param; type ∈ {planet, house, sign, number, string}
    returns: boolean
    impl: "josi.services.classical.predicates.vedic_core:moon_in_kendra_from"
    classical_names:
      en: "Moon in kendra from {of}"
      sa_iast: "kendrasthita-candra"
    citation: "BPHS Ch.3 v.22"
    notes: |
      Kendras from a planet are houses 1, 4, 7, 10 counting from that planet's house.

  - name: planet_not_debilitated
    signature:
      planet: { type: planet }
    returns: boolean
    impl: "josi.services.classical.predicates.vedic_core:planet_not_debilitated"
    citation: "BPHS Ch.3 v.44 (debilitation table)"

  - name: planet_not_combust
    signature:
      planet: { type: planet }
    returns: boolean
    impl: "josi.services.classical.predicates.vedic_core:planet_not_combust"

  - name: in_exaltation
    signature:
      planet: { type: planet }
    returns: boolean
    impl: "josi.services.classical.predicates.vedic_core:in_exaltation"

  - name: in_own_sign
    signature:
      planet: { type: planet }
    returns: boolean
    impl: "josi.services.classical.predicates.vedic_core:in_own_sign"

  - name: aspects_to
    signature:
      from_planet: { type: planet }
      to_planet:   { type: planet }
      scheme:      { type: string, enum: [drishti, tajaka, western], default: drishti }
    returns: boolean
    impl: "josi.services.classical.predicates.vedic_core:aspects_to"

  - name: conjoined_with
    signature:
      planet_a: { type: planet }
      planet_b: { type: planet }
      orb_deg:  { type: number, default: 8.0 }
    returns: boolean
    impl: "josi.services.classical.predicates.vedic_core:conjoined_with"

functions:                                   # numeric-returning callables for strength_formula
  - name: planet_dignity_score
    signature:
      planet: { type: planet }
    returns: number                          # 0..1
    impl: "josi.services.classical.functions.vedic_core:planet_dignity_score"

  - name: house_lord_strength
    signature:
      house: { type: house }
    returns: number
    impl: "josi.services.classical.functions.vedic_core:house_lord_strength"
```

**Typed parameter system:** `type: planet` resolves to the enum `{sun, moon, mercury, venus, mars, jupiter, saturn, rahu, ketu, uranus, neptune, pluto}`. `type: house` → 1..12. `type: sign` → 0..11 (or 1..12 with convention flagged). `type: number`, `type: string` straightforward. Validation in the loader.

### 5.4 Data model — no new tables

All rule content lands in existing `classical_rule` (F2). Predicates are declared in YAML but **not stored in DB**; they form an in-memory `PredicateRegistry` built at startup. This is deliberate: predicates are code-adjacent (every predicate has a Python `impl`), so co-locating their metadata with the registry-in-Python is simpler than syncing a `predicate` table.

### 5.5 Loader service interface

```python
# src/josi/services/classical/rule_registry_loader.py

class RuleRegistryLoader:
    """Walks src/josi/rules/**/*.yaml, validates, hashes, upserts classical_rule rows."""

    RULES_ROOT: Path = Path("src/josi/rules")
    PREDICATES_SUBDIR: str = "predicates"

    def __init__(self, predicate_registry: PredicateRegistry, canonicalizer: RuleCanonicalizer):
        ...

    async def load_all(self, session: AsyncSession) -> LoadReport:
        """
        Returns counts of inserted/updated/unchanged/deprecated rules.
        Phases:
          1. Load all predicate YAMLs → PredicateRegistry.
          2. Discover rule YAMLs.
          3. Parse + Pydantic-validate each.
          4. Resolve all predicate refs in rule_body against PredicateRegistry.
          5. Compute content_hash per rule.
          6. Upsert classical_rule rows.
          7. For rules present in DB but absent from YAML with no effective_to → set effective_to=now().
        Fail-fast on any validation error.
        """

    async def reload_file(self, session: AsyncSession, yaml_path: Path) -> LoadReport:
        """Dev-mode incremental reload of a single file."""

    def _parse_rule_yaml(self, path: Path) -> RuleDocument: ...
    def _validate_rule(self, rule: RuleDocument) -> None: ...
    def _compute_content_hash(self, rule: RuleDocument) -> str: ...
    async def _upsert_rule(self, session: AsyncSession, rule: RuleDocument, content_hash: str) -> UpsertOutcome: ...
```

Fail modes:
- Predicate YAML missing → startup aborts.
- Rule references undefined predicate → startup aborts; error names the rule + predicate.
- Rule duplicates existing (`rule_id`, `source_id`, `version`) with different content_hash → startup aborts with diff-style error ("rule X@bphs@1.0.0 has changed; bump version to 1.0.1").
- Invalid YAML → startup aborts with filename + line number.
- Missing FK target (`technique_family_id`, `output_shape_id`, `source_id`) → startup aborts (F1 should be loaded first).

### 5.6 Canonicalizer contract

```python
# src/josi/services/classical/rule_canonicalizer.py

class RuleCanonicalizer:
    """Computes content_hash over the semantic subset of a rule document."""

    HASHED_TOP_KEYS: frozenset[str] = frozenset({
        "rule_id", "source_id", "version",
        "technique_family_id", "output_shape_id",
        "rule_body", "effective_from", "effective_to",
    })

    def canonical_json(self, rule: RuleDocument) -> bytes:
        """Sort keys recursively, normalize floats via repr, UTF-8 encode, no whitespace."""

    def content_hash(self, rule: RuleDocument) -> str:
        """SHA-256 hex of canonical_json output."""
```

### 5.7 CLI validation command

```bash
poetry run validate-rules                 # exits non-zero if any rule fails
poetry run validate-rules --paths src/josi/rules/yogas/bphs/**/*.yaml
poetry run validate-rules --show-hashes   # prints rule_id → content_hash for all loaded rules
```

Wired into CI: a PR that adds/changes a rule runs `validate-rules` and fails if broken. This catches classical-content errors before they reach `main`.

### 5.8 Predicate implementation discovery

Each predicate YAML entry specifies `impl: "package.module:function_name"`. At startup, the `PredicateRegistry` imports each symbol and stores callable references. Type signature from the YAML is compared against the Python signature via `inspect` — mismatches abort startup.

### 5.9 Dev-mode watch

In `ENV=development` only, register a `watchfiles`-based observer on `src/josi/rules/`. On change:
- Predicate YAML changed → full reload (predicate edits can affect many rules).
- Rule YAML changed → incremental `reload_file`.

Logs go to `logs/rule_reload.log`.

## 6. User Stories

### US-F6.1: As a classical advisor, I want to author Gaja Kesari Yoga via a YAML PR
**Acceptance:** I can create `src/josi/rules/yogas/bphs/raja/gaja_kesari.yaml` with the schema above, open a PR, and after merge + deploy, `SELECT * FROM classical_rule WHERE rule_id='yoga.raja.gaja_kesari'` returns the row with non-null `content_hash`, `rule_body`, and `classical_names`.

### US-F6.2: As a classical advisor, I want a typo in my YAML to fail CI, not production
**Acceptance:** introducing `mon_in_kendra_from` (typo) in a rule fails `poetry run validate-rules` with message `rule 'yoga.raja.gaja_kesari': unknown predicate 'mon_in_kendra_from'`. CI job fails the PR.

### US-F6.3: As an engineer, I want cosmetic YAML edits to not invalidate compute rows
**Acceptance:** reformatting `notes` text, adding a `classical_names.ta` translation, or fixing a typo in `citation` does NOT change `content_hash`. `technique_compute` rows remain valid.

### US-F6.4: As an engineer, I want semantic edits to require a version bump
**Acceptance:** changing `orb_deg: 8.0` → `orb_deg: 10.0` in a rule without bumping `version` from `1.0.0` fails startup with error "rule X@bphs@1.0.0 has changed; bump version". Bumping to `1.0.1` succeeds and inserts a new row; the old `1.0.0` row remains with its old `content_hash`.

### US-F6.5: As an engineer, I want rules deprecated by setting `effective_to`
**Acceptance:** removing a rule YAML file sets its DB row's `effective_to = now()`. Compute rows tied to that version remain queryable.

### US-F6.6: As a developer in dev mode, I want YAML edits to reload without server restart
**Acceptance:** editing `gaja_kesari.yaml` while the server runs under `uvicorn --reload` triggers `reload_file`; within 2 seconds the updated rule is queryable via `/api/v1/classical/rules/yoga.raja.gaja_kesari`.

## 7. Tasks

### T-F6.1: Pydantic DSL schemas
- **Definition:** Define `RuleDocument`, `PredicateDocument`, `FunctionDocument`, `BooleanCombinator` (discriminated union), `StrengthFormula` (discriminated union) in `dsl_schemas.py`. Use Pydantic v2 `TypeAdapter` + `Discriminator`.
- **Acceptance:** A well-formed rule YAML parses; malformed YAMLs raise `ValidationError` with clear paths (`rule_body.strength_formula.inputs[1].weight`).
- **Effort:** 8 hours
- **Depends on:** F1, F2 complete

### T-F6.2: Predicate registry
- **Definition:** `PredicateRegistry` class; loads predicate YAMLs, imports each `impl` symbol, verifies Python signature matches YAML signature.
- **Acceptance:** Missing symbol aborts startup; signature mismatch aborts startup; registry exposes `get(name) -> PredicateSpec`.
- **Effort:** 6 hours
- **Depends on:** T-F6.1

### T-F6.3: Canonicalizer + content_hash
- **Definition:** `RuleCanonicalizer` with `canonical_json` and `content_hash`. Drop non-hashed top-level keys. Deterministic float rendering.
- **Acceptance:** Given two YAMLs differing only in `citation`, `classical_names`, `notes`, `examples`, they produce identical hashes. Changing any hashed field changes the hash. Running the same YAML through the canonicalizer on macOS and Linux produces the same hash.
- **Effort:** 5 hours
- **Depends on:** T-F6.1

### T-F6.4: RuleRegistryLoader
- **Definition:** Service walks `src/josi/rules/**/*.yaml`, parses, validates, hashes, upserts. Implements all fail-modes.
- **Acceptance:** Integration test: create two rules, run loader, verify DB rows and content_hashes. Run again, verify no changes. Edit one rule's `notes`, run again, verify no hash change (row untouched). Edit semantic field without bumping version, verify abort.
- **Effort:** 10 hours
- **Depends on:** T-F6.2, T-F6.3

### T-F6.5: FastAPI lifespan integration
- **Definition:** Register loader in app lifespan after `DimensionLoader` (F1). Fail-fast on startup error.
- **Acceptance:** Fresh DB + rule YAMLs → app boots, DB populated. Broken rule YAML → app fails to boot with clear error.
- **Effort:** 2 hours
- **Depends on:** T-F6.4

### T-F6.6: CLI `validate-rules` command
- **Definition:** Poetry script entry point; runs loader in "dry-run" mode (no DB writes); prints report. Wired into `.github/workflows/ci.yml` or Cloud Build equivalent.
- **Acceptance:** `poetry run validate-rules` exits 0 on clean tree, non-zero on any error.
- **Effort:** 3 hours
- **Depends on:** T-F6.4

### T-F6.7: Dev-mode watch
- **Definition:** `watchfiles` observer; on change, trigger `reload_file` or full reload.
- **Acceptance:** In `ENV=development`, editing a rule YAML while server runs updates the DB within 2s; errors log but don't crash the server.
- **Effort:** 4 hours
- **Depends on:** T-F6.4

### T-F6.8: Seed starter rule + predicates
- **Definition:** Author `predicates/vedic_core.yaml` with the 7 predicates + 2 functions shown above, their Python `impl`s as stubs (stub bodies ok — F-series is scaffolding; actual impls come in engine EPICs), and one real rule (Gaja Kesari) as proof-of-life.
- **Acceptance:** On fresh DB + this seed, loader produces 1 `classical_rule` row; content_hash is stable across three runs.
- **Effort:** 4 hours
- **Depends on:** T-F6.4

## 8. Unit Tests

### 8.1 dsl_schemas (Pydantic DSL parsing)

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_minimal_valid_rule` | YAML with only required top-level fields + `rule_body.activation.predicate` | parses to `RuleDocument` | happy path |
| `test_missing_rule_id` | YAML without `rule_id` | `ValidationError` naming `rule_id` | required-field enforcement |
| `test_invalid_semver` | `version: "1.0"` | `ValidationError` | regex enforcement |
| `test_unknown_top_level_key` | extra `foo: bar` key | `ValidationError` (strict mode) | catch typos at author time |
| `test_nested_all_of_any_of` | 3-level nested boolean tree | parses | combinators compose |
| `test_combinator_missing_leaf` | `all_of: []` | `ValidationError` | empty combinator rejected |
| `test_strength_weighted_average_missing_weights` | inputs without `weight` in `weighted_average` | `ValidationError` | weighted_average requires weights |
| `test_strength_constant_happy` | `type: constant, value: 0.5` | parses | constant formula |
| `test_strength_piecewise_happy` | piecewise with 3 pieces | parses | piecewise combinator |
| `test_output_shape_requires_activation` | `output_shape_id: boolean_with_strength` without `activation` | `ValidationError` | shape-specific rule |

### 8.2 PredicateRegistry

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_predicate_registry_happy` | valid predicates YAML + valid impl symbols | registry has 7 predicates + 2 functions | basic load |
| `test_missing_impl_symbol` | `impl: 'josi.missing:fn'` | startup aborts with ImportError | fail-fast |
| `test_impl_signature_mismatch` | YAML says `planet: planet`; Python fn takes `(foo, bar)` | startup aborts | type-safety contract |
| `test_duplicate_predicate_name_across_files` | `vedic_core.yaml` + `jaimini_core.yaml` both declare `aspects_to` | abort with "duplicate predicate" | namespace integrity |
| `test_predicate_lookup_returns_spec` | registry.get("moon_in_kendra_from") | returns PredicateSpec with typed signature | runtime use |

### 8.3 RuleCanonicalizer (content_hash)

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_hash_stable_across_runs` | same YAML hashed 100× | identical 64-char hex | determinism |
| `test_hash_invariant_to_key_order` | YAML A, YAML B identical but keys shuffled | identical hash | cosmetic reformat |
| `test_hash_invariant_to_whitespace` | YAML A, YAML B identical but extra blank lines | identical hash | cosmetic reformat |
| `test_hash_invariant_to_citation_change` | A: `citation: "BPHS 36.14"`, B: `citation: "BPHS Ch.36"` | identical hash | docs not hashed |
| `test_hash_invariant_to_classical_names_change` | A no `ta`, B adds `ta: "..."` | identical hash | i18n additions free |
| `test_hash_invariant_to_notes_change` | A no notes, B with long notes | identical hash | docs not hashed |
| `test_hash_changes_on_predicate_arg` | `orb_deg: 8.0` → `orb_deg: 10.0` | different hash | semantic change |
| `test_hash_changes_on_version` | `version: 1.0.0` → `1.0.1` | different hash | version is identity |
| `test_hash_changes_on_effective_from` | `effective_from: 2026-04-19` → `2026-04-20` | different hash | activation window is semantic |
| `test_float_repr_stable` | `weight: 0.1 + 0.2` (Python) written as `0.30000000000000004` vs `0.3` | different hashes (by design — authors must be precise) | determinism |

### 8.4 RuleRegistryLoader (integration with DB)

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_loader_inserts_on_empty_db` | 1 rule YAML, fresh DB | 1 row in classical_rule with matching content_hash | base case |
| `test_loader_idempotent_second_run` | same YAML, same DB | 0 inserts, 0 updates | idempotency |
| `test_loader_cosmetic_edit_no_db_change` | edit `notes`, rerun | 0 updates (hash unchanged) | provenance stable |
| `test_loader_semantic_edit_without_version_bump_aborts` | change `orb_deg` without bumping version | raises `RuleVersionCollisionError` | safety |
| `test_loader_semantic_edit_with_version_bump_inserts_new_row` | bump to 1.0.1 + change arg | 1 existing + 1 new row, both active | versioning |
| `test_loader_deleted_yaml_soft_deprecates` | remove YAML, rerun | row's `effective_to` set to `now()` | retention |
| `test_loader_unknown_predicate_aborts` | rule refers to undefined predicate | raises `UnknownPredicateError` | fail-fast |
| `test_loader_unknown_source_id_aborts` | rule has `source_id: made_up` | FK violation at upsert | referential integrity |
| `test_loader_future_effective_from_loaded` | `effective_from: 2099-01-01` | row inserted; engines filter it out until then | timed rollout |
| `test_loader_concurrent_run_safe` | 2 loader.load_all() in parallel | both succeed, no duplicate rows (ON CONFLICT DO NOTHING or DO UPDATE with identical hash) | concurrency |

### 8.5 CLI validate-rules

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_cli_clean_tree_exit_zero` | all rules valid | exit 0 | CI signal |
| `test_cli_broken_rule_exit_nonzero` | one rule references unknown predicate | exit != 0; stderr names file + error | CI signal |
| `test_cli_show_hashes_prints_all` | `--show-hashes` | stdout has `rule_id <sha256>` per rule | debuggability |

### 8.6 Dev-mode watch

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_watch_reloads_on_file_change` | edit a rule YAML at runtime | within 2s, DB reflects change | DX |
| `test_watch_broken_file_logs_not_crashes` | break syntax in a file at runtime | error in `logs/rule_reload.log`; server stays up | resilience |

## 9. EPIC-Level Acceptance Criteria

- [ ] `src/josi/rules/` tree exists with at least one seeded rule (Gaja Kesari) and `predicates/vedic_core.yaml`
- [ ] Pydantic DSL schemas cover both rule documents and predicate documents; all combinators supported
- [ ] `PredicateRegistry` loads at startup with signature validation
- [ ] `RuleCanonicalizer.content_hash` is deterministic and hashes only the semantic subset
- [ ] `RuleRegistryLoader.load_all` runs on FastAPI lifespan; fail-fast on error
- [ ] `poetry run validate-rules` CLI exits 0/non-zero correctly; wired into CI
- [ ] Cosmetic edits (citation, classical_names, notes, examples) do NOT change content_hash — verified by test
- [ ] Semantic edits without version bump abort startup — verified by test
- [ ] Deleted YAMLs soft-deprecate their DB rows via `effective_to = now()`
- [ ] Dev-mode watch reloads single files without full restart
- [ ] Unit test coverage ≥ 90% across loader + canonicalizer + registry + schemas
- [ ] Integration test covers rule → DB → read-back path
- [ ] CLAUDE.md updated: "To add a classical rule, create a YAML under `src/josi/rules/{family}/{source}/...`; run `poetry run validate-rules` before committing"

## 10. Rollout Plan

- **Feature flag:** none — P0 foundation.
- **Shadow compute:** N/A.
- **Backfill:** At P0 the rule set is small (Gaja Kesari + handful of proof-of-life rules). Engine EPICs (E4a etc.) will backfill the ~250 rule target.
- **Rollback:** remove rule YAMLs from repo; next deploy soft-deprecates rows. Hard rollback: `alembic downgrade` reverts F2 (dropping `classical_rule`).

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Canonicalizer disagrees across Python versions (float repr, dict ordering) | Low | High (invalidates provenance) | Pin minimum Python 3.12; repr-based float; sort_keys=True; CI asserts hash of a fixture rule is constant |
| Predicate library grows too fat; one file unwieldy | High over time | Medium | Shard by tradition (`vedic_core`, `jaimini_core`, `tajaka_core`, …); no single-file growth mandate |
| Author forgets to bump version on semantic edit | High | High (would overwrite provenance) | Loader aborts startup with diff-style error; CI catches pre-merge |
| Watch-mode masks real errors in prod | Low | Medium | `ENV != development` disables watcher |
| YAML parse errors blocking startup in prod | Medium | High | CI step runs full `validate-rules` against merge target pre-deploy |
| Predicate Python signature vs YAML signature drift | Medium | Medium | Loader verifies on startup; unit test with deliberate mismatch |
| Rule count grows beyond 10k and loader gets slow | Low near-term, rises P4+ | Medium | Loader is O(N) at startup; at 10k rules × 200µs each = 2s; acceptable; revisit at P4 if needed |
| Non-ASCII characters in `rule_id` or `source_id` | Low | Medium | Regex-restrict `rule_id` to `[a-z0-9._-]+`; `classical_names` are free Unicode |

## 12. References

- Master spec: [`docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`](../../../superpowers/specs/2026-04-19-classical-techniques-expansion-design.md) §2.2, §2.4, §2.5
- F1 dims: [`F1-star-schema-dimensions.md`](./F1-star-schema-dimensions.md)
- F2 fact tables: [`F2-fact-tables.md`](./F2-fact-tables.md)
- F4 temporal versioning: [`F4-temporal-rule-versioning.md`](./F4-temporal-rule-versioning.md)
- F5 JSON Schema validation at insert time: [`F5-json-schema-validation.md`](./F5-json-schema-validation.md)
- F7 output-shape system: [`F7-output-shape-system.md`](./F7-output-shape-system.md)
- F13 content-hash provenance: [`F13-content-hash-provenance.md`](./F13-content-hash-provenance.md)
- Classical source verses: BPHS Ch.36 v.14-16 (Gaja Kesari); Saravali Ch.34 (parallel yoga definitions); Jaimini Sutras Bk.1 Ch.2 (karaka definitions)
- Canonical-JSON reference: RFC 8785 (JCS) — spiritual guide, not exact implementation
- Reference implementations: Jagannatha Hora 7.x (proprietary), Maitreya9 (open-source)
