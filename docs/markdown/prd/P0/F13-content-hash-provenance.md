---
prd_id: F13
epic_id: F13
title: "Content-hash provenance chain (input_fingerprint + output_hash)"
phase: P0-foundation
tags: [#correctness]
priority: must
depends_on: [F2, F4, F6]
enables: [F15, E1a, E2a, E4a, E6a, E14a, P3-E6-flag, P3-E8-obs, S8]
classical_sources: []
estimated_effort: 3 days
status: draft
author: Govind
last_updated: 2026-04-19
---

# F13 — Content-Hash Provenance Chain

## 1. Purpose & Rationale

Every `technique_compute` row is a truth claim: "given this chart, this rule, this version — the result is X." Without cryptographic linkage between inputs and outputs we cannot answer three operational questions:

1. **"Is this cached row still correct?"** — rule changed, chart geocoding refined, ayanamsa override flipped: we need automatic staleness detection.
2. **"How did this chart arrive at `Gaja Kesari = active, strength=0.82`?"** — astrologers and the AI both require auditable provenance down to the verse.
3. **"Has anything been tampered with?"** — periodic integrity sweeps must detect silent corruption in JSONB `result` payloads.

F13 defines the two content hashes stored on every `technique_compute` row, the canonical-JSON serialization that makes them reproducible across Python versions and hosts, the recompute trigger protocol, the audit-trace query, and the tamper-detection background job.

This PRD does not implement the engines that populate compute rows (E1a, E2a, E4a, E6a). It delivers the provenance primitives that every engine depends on.

## 2. Scope

### 2.1 In scope
- `input_fingerprint` (sha256) semantics and composition
- `output_hash` (sha256) semantics
- `canonical_json` utility: deterministic UTF-8 bytes from a Python value
- `compute_input_fingerprint(chart_state, rule, extra_params) -> str` utility
- `compute_output_hash(result_payload) -> str` utility
- Recompute-trigger protocol: short-circuit cache if stored `input_fingerprint` ≠ desired `input_fingerprint`
- Audit-trace query: API + internal helper that walks `output_hash → input_fingerprint → classical_rule.content_hash → rule_body.citation`
- Tamper-detection job: nightly cron that recomputes `output_hash` from stored `result` JSONB and flags mismatches
- Integration tests across Python 3.12 vs 3.13 to prove cross-version stability
- Hypothesis property tests for canonical-JSON reproducibility

### 2.2 Out of scope
- Signing hashes with a private key — we store plain sha256; HMAC is a future S8 concern.
- Recompute orchestration (when/where to run the engine on staleness) — handled by S5 and S6.
- Storing historical fingerprints per row — we overwrite on recompute; historical lineage lives in the aggregation_event log, not in technique_compute.
- Hashing the aggregation-layer outputs — `aggregation_event.inputs_hash` already exists (F2) and uses the same `canonical_json` utility but is aggregation-side.
- Storing a Merkle tree or chained hash across rows. Per-row independence is sufficient; tamper-detection still works row-by-row.

### 2.3 Dependencies
- F2: `technique_compute.input_fingerprint` and `technique_compute.output_hash` columns already declared as `CHAR(64) NOT NULL`.
- F4: `classical_rule.content_hash` exists and is populated by the rule loader.
- F6: Rule DSL YAML loader produces deterministic `rule_body` content for hashing.

## 3. Technical Research

### 3.1 What "canonical JSON" means here

We define **canonical JSON** as:
- Keys sorted lexicographically at every object level (recursively).
- No insignificant whitespace (`separators=(",", ":")`).
- UTF-8 encoded bytes.
- Floats and integers represented as their decimal string form (`repr`) with one subtlety: **all numeric values are passed through `decimal.Decimal` and serialized as strings** to defeat IEEE-754 rounding differences between Python versions or platforms.
- Booleans as `true` / `false`, null as `null`.
- Datetimes serialized as ISO-8601 with `+00:00` UTC offset (never `Z`, never naive).
- Enum values serialized as their `.value` string.

Rationale: Python's stdlib `json` is almost but not quite canonical. `sort_keys=True` plus `separators` handles ordering and whitespace. The numeric-string wrap handles float non-determinism. A thin wrapper over `json.dumps` gets us there.

### 3.2 What goes into `input_fingerprint`

```
input_fingerprint = sha256(canonical_json({
  "chart": {
    "birth_utc":          chart.birth_utc.isoformat(),
    "lat":                round(chart.lat, 4),      # match F15 rounding
    "lon":                round(chart.lon, 4),
    "ayanamsa_id":        chart.ayanamsa_id,
    "planet_positions":   chart.planet_positions_canonical(),
    "house_cusps":        chart.house_cusps_canonical(),
  },
  "rule": {
    "rule_id":            rule.rule_id,
    "source_id":          rule.source_id,
    "version":            rule.version,
    "content_hash":       rule.content_hash,        # from F4
  },
  "extra_params":         extra_params,             # technique-specific
}))
```

Notes:
- `planet_positions_canonical()` returns a sorted list of tuples `[(planet_id, longitude_decimal_str, latitude_decimal_str, speed_decimal_str), …]`.
- `house_cusps_canonical()` returns a 12-element list of decimal strings.
- `extra_params` is a technique-specific dict. Examples:
  - tajaka: `{"year": 2026}`
  - transit: `{"date_range": ["2026-01-01", "2026-12-31"]}`
  - vimshottari antardasha lookup: `{"parent_period_lord": "jupiter", "parent_period_start": "2024-04-11T03:22:00+00:00"}`
  - yoga (no params): `{}`

The rule's `content_hash` is included in the input_fingerprint so that a rule body change (same `rule_id`, same `version` — which should never happen, but if it does via a bug) still yields a new fingerprint and forces a recompute.

### 3.3 What goes into `output_hash`

```
output_hash = sha256(canonical_json(result_payload))
```

Where `result_payload` is the exact JSONB stored in `technique_compute.result`. The Pydantic model is serialized via `.model_dump(mode="json")` before canonicalization — which already normalizes datetimes, UUIDs, enums, etc. The canonicalizer then does the ordering and whitespace.

This gives us: the same result dict always produces the same `output_hash`, regardless of order in which keys were inserted or which Python version produced it.

### 3.4 Recompute trigger protocol

When an engine is asked to compute for `(chart_id, rule_id, source_id, rule_version)`:

1. Build the *desired* `input_fingerprint` from current chart state, current rule, current extra_params.
2. `SELECT input_fingerprint, result FROM technique_compute WHERE pk = ...`
3. If row exists and stored `input_fingerprint` matches desired → **cache hit**, return stored result.
4. If row exists and stored `input_fingerprint` differs → **stale**, recompute, `INSERT ... ON CONFLICT (pk) DO UPDATE` with new fingerprint and new result.
5. If row absent → **miss**, compute, insert.

This is the entire cache-validation rule. No TTL. Staleness is content-driven.

### 3.5 Audit-trace query

Given an `output_hash` (copy-pasted from a UI or log), return a full provenance tree:

```
output_hash
  → technique_compute row (chart_id, rule_id, source_id, rule_version, input_fingerprint, computed_at)
    → classical_rule (rule_body, citation, content_hash, classical_names)
      → source_authority (display_name, era, citation_system)
    → chart astronomical state at computed_at
```

Implemented as `audit_trace(output_hash: str) -> AuditTrace` that renders cleanly as JSON for an internal operator endpoint.

### 3.6 Tamper detection

Nightly Celery/procrastinate/Temporal job (mechanism chosen in S5, scaffold here):

```python
async def detect_tampered_rows(batch_size=10_000) -> list[TamperReport]:
    """
    For each batch: recompute output_hash from stored result, compare to stored output_hash.
    Mismatch → emit TamperReport; mismatch count is a SLO.
    """
```

At P0 the job is a one-shot script runnable via `poetry run python -m josi.scripts.detect_tampered_rows`. S5 will schedule it.

Expected tamper count at steady state: **0**. Non-zero count is a P1 incident.

### 3.7 Alternatives considered

| Alternative | Rejected because |
|---|---|
| `json.dumps(..., sort_keys=True)` without decimal-wrap | Float rounding drift between Python patch versions would yield unstable hashes |
| CBOR / MessagePack canonical form | Human-unreadable; dev tooling (grep, inspect in psql) becomes painful |
| Blake3 instead of sha256 | sha256 is hardware-accelerated on all modern CPUs; blake3 adds a dependency for no win at our row scale |
| Storing input_fingerprint as bytea | Hex `CHAR(64)` is greppable in logs and copy-pasteable into audit UIs |
| Storing result + input together and hashing once | Conflates "what went in" vs "what came out"; staleness detection becomes impossible |
| HMAC with secret key | Useful for anti-tamper but not needed at P0; would force secret rotation pipeline; defer to S8 |

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| sha256 vs sha512 vs blake3 | sha256 | Hardware-accelerated; 64-char hex fits our column; ample security margin for non-adversarial use |
| Hex vs base64 storage | Hex | Greppable; copy-paste friendly; already chose `CHAR(64)` in F2 |
| Wrap numerics in Decimal strings? | Yes | Only way to guarantee stability across Python versions and hardware |
| Include `computed_at` in input_fingerprint? | No | Would defeat caching — same inputs at two times would differ |
| Include chart's geocoded lat/lon or user-entered lat/lon? | Rounded to 4 decimals (matches F15) | Prevents geocode-jitter churn; still precise to ~10m |
| Hash stored result or hash re-serialized Pydantic model? | Hash stored `result` column JSONB via canonical_json | JSONB storage may reorder keys in Postgres; we always re-canonicalize before hashing so order-in-DB is irrelevant |
| Should tamper-detection auto-repair? | No, flag only | Auto-repair could mask a real attack; operator decides |
| Expose `input_fingerprint` in public API? | No | Internal audit only; leaking it reveals rule structure to reverse-engineers |

## 5. Component Design

### 5.1 New modules

```
src/josi/services/provenance/
├── __init__.py
├── canonical_json.py         # canonical_json() utility
├── fingerprint.py            # compute_input_fingerprint(), compute_output_hash()
├── audit.py                  # audit_trace() service
└── tamper_detection.py       # detect_tampered_rows() job

src/josi/schemas/provenance/
├── audit_trace.py            # Pydantic response shape for audit API
└── tamper_report.py          # Pydantic shape for tamper reports

src/josi/api/v1/controllers/
└── provenance_controller.py  # GET /api/v1/provenance/audit/{output_hash}  (admin-only)

src/josi/scripts/
└── detect_tampered_rows.py   # CLI entrypoint; S5 will schedule it

tests/unit/services/provenance/
├── test_canonical_json.py
├── test_fingerprint.py
├── test_audit.py
└── test_tamper_detection.py

tests/integration/provenance/
└── test_cache_staleness_roundtrip.py
```

### 5.2 Data model

No new tables. Columns already declared in F2:

```sql
technique_compute.input_fingerprint  CHAR(64) NOT NULL
technique_compute.output_hash        CHAR(64) NOT NULL
```

Helpful indexes (added in this PRD):

```sql
-- Support audit lookups by output_hash (rare but must be fast when invoked)
CREATE INDEX idx_compute_output_hash ON technique_compute(output_hash);

-- Support staleness sweeps by (chart_id, rule_id, source_id) without version
CREATE INDEX idx_compute_chart_rule_source
  ON technique_compute(chart_id, rule_id, source_id);
```

### 5.3 API contract

#### 5.3.1 Internal (Python)

```python
# src/josi/services/provenance/canonical_json.py

def canonical_json(value: Any) -> bytes:
    """
    Deterministic UTF-8 serialization.

    - Sorts keys lexicographically at every level.
    - No whitespace.
    - All numeric values wrapped via Decimal then emitted as quoted strings.
    - Datetimes → ISO-8601 with explicit +00:00 offset.
    - UUIDs → canonical hex string.
    - Enums → .value.
    - Custom objects must define .__canonical_json__() -> dict|list|primitive.

    Raises:
        CanonicalizationError: if value contains unserializable types.
    """


# src/josi/services/provenance/fingerprint.py

def compute_input_fingerprint(
    chart_state: ChartAstronomicalState,
    rule: ClassicalRule,
    extra_params: Mapping[str, Any] | None = None,
) -> str:
    """Returns 64-char lowercase hex sha256."""


def compute_output_hash(result_payload: Mapping[str, Any] | BaseModel) -> str:
    """
    Returns 64-char lowercase hex sha256.
    If a Pydantic BaseModel is passed, .model_dump(mode="json") is called first.
    """


# src/josi/services/provenance/audit.py

class AuditService:
    async def trace(
        self, session: AsyncSession, output_hash: str
    ) -> AuditTrace | None:
        """Returns full provenance chain; None if output_hash unknown."""
```

#### 5.3.2 External (REST, admin-only)

```
GET /api/v1/provenance/audit/{output_hash}

Headers: X-API-Key (must belong to an organization with role=admin)

200 Response:
{
  "success": true,
  "message": "ok",
  "data": {
    "output_hash": "a3f…",
    "compute": {
      "chart_id": "…",
      "rule_id": "yoga.raja.gaja_kesari",
      "source_id": "bphs",
      "rule_version": "1.0.0",
      "input_fingerprint": "b4e…",
      "computed_at": "2026-04-15T12:34:56+00:00",
      "result": {…}
    },
    "rule": {
      "citation": "BPHS Ch.36 v.14-16",
      "classical_names": {"en": "Gaja Kesari", "sa_iast": "Gaja Keśarī"},
      "content_hash": "c5f…",
      "rule_body_excerpt": "…"
    },
    "source": {
      "display_name": "Brihat Parashara Hora Shastra",
      "tradition": "parashari",
      "era": "~100 BCE (traditional)"
    }
  },
  "errors": null
}

404 Response: output_hash not found
403 Response: non-admin caller
```

### 5.4 Staleness-aware cache helper

A thin helper that engines call from their `compute_for_source`:

```python
# src/josi/services/classical/cache.py

async def load_or_recompute(
    session: AsyncSession,
    chart_state: ChartAstronomicalState,
    rule: ClassicalRule,
    extra_params: dict[str, Any],
    compute_fn: Callable[[], Awaitable[BaseModel]],
) -> tuple[BaseModel, CacheStatus]:
    """
    Returns (result, CacheStatus.HIT | CacheStatus.MISS | CacheStatus.STALE).
    Handles input_fingerprint check, invokes compute_fn on miss/stale,
    and upserts technique_compute with new fingerprints.
    """
```

## 6. User Stories

### US-F13.1: As an engineer, I want the same chart + rule to produce byte-identical fingerprints across environments
**Acceptance:** running `compute_input_fingerprint(chart, rule)` on Mac + Linux, Python 3.12 + 3.13, returns the same 64-char hex. Enforced by a CI matrix test.

### US-F13.2: As an astrologer, I want to click an "explain" button on a computed yoga and see the exact verse + chart state that produced it
**Acceptance:** UI passes `output_hash` to `/api/v1/provenance/audit/{hash}`; response renders the full chain including the BPHS citation. 100% of `technique_compute` rows must be traceable.

### US-F13.3: As an engineer, when a rule's content changes (same rule_id, new version), I want cached rows to recompute automatically on next access
**Acceptance:** publishing a new rule version with different `content_hash` → next read for any chart rebuilds `input_fingerprint` → fingerprint mismatch → row recomputed and updated.

### US-F13.4: As a security operator, I want nightly tamper-detection to flag any silently-modified `result` JSONB
**Acceptance:** manually `UPDATE technique_compute SET result = ... WHERE ...` without updating `output_hash` → next nightly sweep emits a `TamperReport` with the row's PK.

### US-F13.5: As an engineer debugging a flaky test, I want canonical-JSON to never depend on dict-insertion order or float representation
**Acceptance:** Hypothesis test with randomized dict insertion orders + randomized float inputs shows `canonical_json(a) == canonical_json(b)` for semantically-equal `a` and `b`.

## 7. Tasks

### T-F13.1: canonical_json utility
- **Definition:** Implement `canonical_json(value: Any) -> bytes` with the rules in §3.1. Support dict, list, tuple (→ list), str, int, float, Decimal, bool, None, datetime (UTC-normalized), UUID, Enum, and a `__canonical_json__()` protocol for custom types.
- **Acceptance:** 100% unit test coverage; Hypothesis test proves idempotency under key reorderings and semantically-equal float inputs.
- **Effort:** 6 hours
- **Depends on:** nothing

### T-F13.2: fingerprint functions
- **Definition:** `compute_input_fingerprint` and `compute_output_hash` per §3.2 and §3.3. Take `ChartAstronomicalState` as an existing Pydantic type (or introduce one in this PRD if missing).
- **Acceptance:** Unit tests for: stability across runs, sensitivity to any input change (chart, rule, extra_params), stability across Python 3.12 / 3.13.
- **Effort:** 5 hours
- **Depends on:** T-F13.1

### T-F13.3: load_or_recompute cache helper
- **Definition:** Shared helper used by every engine. Honors the §3.4 protocol. Uses `ON CONFLICT (pk) DO UPDATE SET result=..., input_fingerprint=..., output_hash=..., computed_at=now()`.
- **Acceptance:** Integration test with a fake engine shows HIT / MISS / STALE transitions; stored row reflects new fingerprint after STALE.
- **Effort:** 4 hours
- **Depends on:** T-F13.2, F2, F4

### T-F13.4: audit_trace service + API controller
- **Definition:** `AuditService.trace(output_hash)`; REST controller behind admin auth; returns shape in §5.3.2.
- **Acceptance:** Given a seeded compute row, the API returns the full chain including rule citation and source metadata. 404 on unknown hash.
- **Effort:** 4 hours
- **Depends on:** T-F13.2, F2 populated

### T-F13.5: tamper-detection job
- **Definition:** Script + function that iterates compute rows in batches, recomputes `output_hash` from stored `result`, compares to stored `output_hash`, returns `TamperReport` list.
- **Acceptance:** Test seeds one healthy row + one tampered row → job reports exactly the tampered row's PK.
- **Effort:** 3 hours
- **Depends on:** T-F13.2, F2

### T-F13.6: Migration for audit indexes
- **Definition:** `alembic revision --autogenerate -m "F13: provenance indexes"` + manual addition of the two indexes in §5.2.
- **Acceptance:** `EXPLAIN` on audit lookup uses `idx_compute_output_hash`.
- **Effort:** 1 hour
- **Depends on:** T-F13.4

### T-F13.7: Cross-version CI matrix
- **Definition:** GitHub-Actions-style matrix (using existing CI) running `test_canonical_json_stability_across_python_versions` on 3.12 and 3.13.
- **Acceptance:** Both matrix cells pass; hash values documented in the test as explicit expected-value assertions.
- **Effort:** 2 hours
- **Depends on:** T-F13.1

### T-F13.8: Documentation
- **Definition:** Update `CLAUDE.md` and add developer note at `docs/markdown/provenance.md` with: when to call `load_or_recompute`, how to add a new extra_param, how to interpret a tamper report.
- **Acceptance:** Engineer unfamiliar with F13 can read the doc and correctly integrate a new engine.
- **Effort:** 2 hours
- **Depends on:** T-F13.3

## 8. Unit Tests

### 8.1 canonical_json

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_sorts_keys_recursively` | `{"b": 1, "a": {"z": 2, "y": 3}}` | `{"a":{"y":"3","z":"2"},"b":"1"}` bytes | ordering applied at all depths |
| `test_no_whitespace` | `{"a": 1}` | no spaces, no newlines | deterministic size |
| `test_float_via_decimal` | `{"x": 0.1 + 0.2}` | `{"x":"0.30000000000000004"}` | stable float repr |
| `test_datetime_utc_normalized` | naive `datetime(2026,1,1)` | raises `CanonicalizationError` | reject ambiguous |
| `test_datetime_utc_explicit_offset` | `datetime(2026,1,1,tzinfo=UTC)` | `"2026-01-01T00:00:00+00:00"` | ISO-8601 strict |
| `test_enum_serialized_as_value` | `MyEnum.FOO` (value='foo') | `"foo"` | unambiguous |
| `test_tuple_becomes_list` | `("a", "b")` | `["a","b"]` bytes | JSON has no tuple |
| `test_uuid_canonical_hex` | `UUID('…')` | lowercase hex string | stable |
| `test_custom_object_protocol` | object with `__canonical_json__` returning `{"k": 1}` | serialized correctly | extensibility |
| `test_unserializable_raises` | `object()` without protocol | raises `CanonicalizationError` | fail-fast |
| `test_hypothesis_idempotent_reorder` | Hypothesis: random dict | same output regardless of insertion order | property |

### 8.2 fingerprint

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_input_fingerprint_stable` | fixed chart + rule | known golden hex value | regression guard |
| `test_input_fingerprint_sensitive_to_chart` | two charts differing in 1 planet deg | different hashes | correctness |
| `test_input_fingerprint_sensitive_to_rule_version` | same chart, v1 vs v2 rule | different hashes | version-lock |
| `test_input_fingerprint_sensitive_to_rule_content_hash` | same version, different content_hash | different hashes | content-lock |
| `test_input_fingerprint_sensitive_to_extra_params` | same chart + rule, `year=2026` vs `year=2027` | different hashes | param-lock |
| `test_input_fingerprint_insensitive_to_lat_jitter` | lat = 37.77490 vs 37.77495 (same after round) | same hash | F15 alignment |
| `test_output_hash_pydantic_model_vs_dict` | same data via BaseModel or dict | same hash | serialization equivalence |
| `test_output_hash_stable` | golden result payload | known golden hex value | regression guard |
| `test_hashes_are_64_char_lowercase_hex` | any input | matches `^[0-9a-f]{64}$` | format contract |

### 8.3 load_or_recompute (integration with DB)

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_miss_on_empty_row` | no row in DB | compute_fn invoked, row inserted, status=MISS | first compute |
| `test_hit_on_matching_fingerprint` | row exists, fingerprint matches | compute_fn NOT invoked, status=HIT | cache correctness |
| `test_stale_on_fingerprint_mismatch` | row exists, fingerprint differs | compute_fn invoked, row UPDATED, status=STALE | staleness detection |
| `test_stale_rebuild_updates_both_hashes` | STALE path | stored `output_hash` matches newly-computed | self-consistency |
| `test_concurrent_stale_recompute_idempotent` | two concurrent workers on same STALE row | exactly one final row, no errors (UPSERT safe) | race-safety |

### 8.4 audit_trace

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_trace_walks_full_chain` | seed rule+source+compute | returns all three layers | end-to-end |
| `test_trace_unknown_hash_returns_none` | random hex not in DB | None | 404 source |
| `test_trace_includes_citation` | rule with citation="BPHS 36.14" | citation present in response | UX requirement |
| `test_trace_rule_body_excerpt_length_bounded` | rule_body with 10MB blob | excerpt truncated to 2KB | safety |

### 8.5 tamper_detection

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_detects_mutated_result` | row with result changed but output_hash untouched | report emitted for that row | detection |
| `test_no_false_positive_on_healthy_rows` | 1000 healthy rows | empty report | precision |
| `test_batching_covers_all_rows` | 5000 rows, batch_size=1000 | 5 batches, all rows scanned | completeness |
| `test_report_includes_pk_fields` | tampered row | report has chart_id, rule_id, source_id, rule_version, stored_hash, recomputed_hash | operator usability |

### 8.6 Cross-version reproducibility (CI matrix)

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_canonical_json_identical_on_3_12_and_3_13` | fixed golden value | same bytes across Python versions | portability |
| `test_fingerprint_matches_golden_on_3_12_and_3_13` | fixed chart + rule | same hex on both | portability |

## 9. EPIC-Level Acceptance Criteria

- [ ] `canonical_json` handles every supported type with unit tests proving determinism
- [ ] `compute_input_fingerprint` and `compute_output_hash` return 64-char lowercase hex
- [ ] `load_or_recompute` helper correctly implements HIT / MISS / STALE protocol
- [ ] `GET /api/v1/provenance/audit/{hash}` returns full chain for any seeded output_hash
- [ ] `detect_tampered_rows` job correctly identifies tampered rows and never false-positives on healthy rows
- [ ] Cross-version CI matrix (3.12 + 3.13) green
- [ ] Hypothesis property tests pass at `max_examples=1000`
- [ ] Unit test coverage ≥ 95% on `services/provenance/*`
- [ ] Integration test hits the full HIT/MISS/STALE path against a real Postgres
- [ ] `CLAUDE.md` updated; `docs/markdown/provenance.md` authored
- [ ] Every existing engine scaffold (F8) uses `load_or_recompute` — no direct compute_fn invocations in engines

## 10. Rollout Plan

- **Feature flag:** none — P0 foundation.
- **Shadow compute:** N/A.
- **Backfill strategy:** at P0 no production compute rows exist. For subsequent rule-version promotions in P1+, the staleness-detection logic automatically triggers recompute on first access (lazy). A one-shot script `backfill_fingerprints.py` is provided for operators who want to pre-warm: it re-runs `compute_output_hash` over stored `result` and updates `output_hash` in place without rebuilding `result`.
- **Rollback plan:** The two new indexes are safe to drop (`alembic downgrade -1`). The canonical_json/fingerprint code is pure-function with no side effects; reverting is a normal git revert. Existing stored `input_fingerprint` / `output_hash` columns are already mandatory (F2), so disabling F13 is not meaningful — the system would fail to insert new rows.

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Python version upgrade changes `json.dumps` behavior | Low | High (all hashes break) | CI matrix pins expected hex values; upgrade is gated by that test |
| Floats silently re-serialized by JSONB round-trip changing bytes | High | Medium | We always re-canonicalize from the stored dict, never rely on JSONB byte-equality |
| Chart state not deterministically reducible (e.g., ephemeris lookup returns slightly different value) | Medium | High | `planet_positions_canonical()` rounds to 6 decimal degrees; ephemeris call inputs are fully specified |
| Audit API leaks sensitive chart data | Medium | Medium | Admin-only auth; `rule_body_excerpt` capped at 2KB; chart fields filtered to astronomical only, no PII |
| Tamper-detection job floods alerting on legitimate schema migrations | Medium | Medium | Rule-version changes use the normal staleness path (write new row, new hash); tamper-detection specifically detects `result` changes without `output_hash` change — which should be impossible through normal code paths |
| `CHAR(64)` column waste on frequently-NULL cases | None | — | F2 already forbids NULL; not a concern |
| Hypothesis test flakiness on floats at extreme magnitudes | Low | Low | Restrict hypothesis `floats()` strategy to `[-1e12, 1e12]`, non-NaN, non-inf |
| Audit endpoint becomes abuse vector at scale | Low | Medium | Rate-limit to 10 req/sec per admin key; index on `output_hash` keeps lookups cheap |

## 12. References

- Master spec: [`docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`](../../../superpowers/specs/2026-04-19-classical-techniques-expansion-design.md) §2.5
- F2 fact tables: [`F2-fact-tables.md`](./F2-fact-tables.md)
- F4 temporal rule versioning: [`F4-temporal-rule-versioning.md`](./F4-temporal-rule-versioning.md)
- F6 rule DSL YAML loader: [`F6-rule-dsl-yaml-loader.md`](./F6-rule-dsl-yaml-loader.md)
- F15 chart canonical fingerprint: [`F15-chart-canonical-fingerprint.md`](./F15-chart-canonical-fingerprint.md)
- RFC 8785 — JSON Canonicalization Scheme (our format is inspired by, not identical to, JCS)
- Python `hashlib` stdlib docs — sha256
- `hypothesis` docs — property-based testing
