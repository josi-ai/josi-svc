---
prd_id: F15
epic_id: F15
title: "Chart canonical fingerprinting for cross-user cache"
phase: P0-foundation
tags: [#performance]
priority: should
depends_on: [F13]
enables: [S3, S6, E1a, E2a, E4a, E6a, E11a]
classical_sources: []
estimated_effort: 3 days
status: draft
author: Govind
last_updated: 2026-04-19
---

# F15 — Chart Canonical Fingerprinting for Cross-User Cache

## 1. Purpose & Rationale

Two users born at the same moment in the same city should share every classical-technique computation. Their yogas are identical. Their vimshottari dasa periods are identical. Their ashtakavarga matrix is identical. At user scale, this is not a small fraction:

- Twins (identical birth data, two user accounts) share 100% of computes.
- Shared-chart imports (astrologer uploads a client's chart; client later signs up) share 100%.
- Re-rolled charts (same person, geocoding refined from city-centroid to precise address within 10m) frequently share 100%.
- Distinct people born minutes/km apart in a dense city may share substantial classical state — not via fingerprint identity, but aligned fingerprints are the foundation for future "near-neighbor" cache.

F15 defines a **chart canonical fingerprint** — a sha256 over normalized birth data — and a storage + lookup layer that lets the compute layer share rows by fingerprint rather than by `chart_id`.

Expected savings at 100M charts is real but bounded (§3.6 analysis). The bigger reasons to build F15 now:
- Twins is a visible correctness concern from day one.
- Import/sync flows demand it.
- It closes the loop between F13 (input_fingerprint) and cross-user sharing.

## 2. Scope

### 2.1 In scope
- `chart_canonical_fingerprint(chart) -> str` (sha256 hex).
- `canonical_fingerprint` column on `astrology_chart`, indexed.
- Backfill migration: compute fingerprint for all existing charts.
- `compute_cache_by_fingerprint` table keyed by `(fingerprint, rule_id, source_id, rule_version)` — **Option A** from the task brief.
- Read path: engines look up by fingerprint first, fall back to compute + insert.
- Write path: populate both `technique_compute` (chart-keyed) and `compute_cache_by_fingerprint` (fingerprint-keyed) in the same transaction.
- Lat/lon rounding to 4 decimals (~10m precision).
- Timezone normalization: all birth times converted to UTC before fingerprinting.
- Ayanamsa inclusion so that a chart viewed under Lahiri vs KP-Ayanamsa gets different fingerprints.

### 2.2 Out of scope
- **Option B** (copy-on-create) is described in §3.5 as a fallback but not implemented at P0.
- Near-neighbor fingerprint matching (same minute, adjacent cities) — interesting but out of scope; the fingerprint here is exact-match only.
- Chart-to-chart similarity (that's E11a's Qdrant semantic similarity; this is exact cache sharing).
- Cross-organization sharing: fingerprints are global, but `compute_cache_by_fingerprint` rows include `organization_id` so tenants cannot see each other's data. Sharing happens within a tenant only.
- Fuzzy birth-time handling ("I was born in the morning"). Out of scope; handled by E1b uncertainty bands.

### 2.3 Dependencies
- F13: the cache-lookup protocol piggybacks on F13's `load_or_recompute` and its canonical-JSON utility.
- Existing `astrology_chart` table with birth fields (`birth_datetime_utc`, `birth_latitude`, `birth_longitude`, `ayanamsa_id`).

## 3. Technical Research

### 3.1 Fingerprint composition

```python
def chart_canonical_fingerprint(chart: AstrologyChart) -> str:
    payload = {
        "birth_utc":     chart.birth_datetime_utc.astimezone(UTC).isoformat(),
        "lat_rounded":   round(chart.birth_latitude, 4),
        "lon_rounded":   round(chart.birth_longitude, 4),
        "ayanamsa_id":   chart.ayanamsa_id,
    }
    return hashlib.sha256(canonical_json(payload)).hexdigest()
```

The four fields are exactly the inputs that, together, determine every classical computation:
- `birth_utc` — moment in time.
- `lat_rounded`, `lon_rounded` — location (for houses, local-time conversions).
- `ayanamsa_id` — which sidereal frame.

No name. No chart owner. No organization. Fingerprint is chart-intrinsic.

### 3.2 Why 4 decimal places for lat/lon

4 decimal places = 0.0001° ≈ 11.1 m at the equator, less at higher latitudes.

Reasons for this granularity:
- City-centroid geocoding jitter typically 1–100 m; 11m rounding absorbs that.
- Classical house cusps at ~29° or ~1° sensitivities are utterly insensitive to 11m east-west shifts.
- More precision (5 decimals = 1.1m) splits fingerprints unnecessarily.
- Less precision (3 decimals = 110m) falsely merges distinct charts in dense cities (Brooklyn vs Manhattan at 3 decimals can collide).

4 is the empirically-chosen sweet spot used by OpenStreetMap and most geocoding services.

### 3.3 Timezone normalization

All birth times are stored internally as UTC. The fingerprint uses `astimezone(UTC)` explicitly — defense in depth in case some chart row is stored naive (which shouldn't happen, but F13's canonical-JSON raises on naive so we'd catch it).

### 3.4 Ayanamsa inclusion

Without ayanamsa, a chart computed under Lahiri (default Indian) vs Krishnamurti Paddhati would get the same fingerprint, yet their sidereal planet positions differ by ~0.01°. Fingerprinting would over-share. Including `ayanamsa_id` fixes this.

If a chart's ayanamsa is changed (via user pref) post-creation, its fingerprint changes and the previous fingerprint's cached computes become unreachable for this chart — correct behavior, since they were computed under the wrong ayanamsa.

### 3.5 Option A vs Option B (core design choice)

**Option A (chosen):** `compute_cache_by_fingerprint` is the canonical cache. `technique_compute` becomes a chart-scoped view/materialization over it.

```
┌───────────────────────────────────────────┐
│ compute_cache_by_fingerprint              │
│   PK: (fingerprint, rule_id,              │
│        source_id, rule_version)           │
│   organization_id, result, hashes         │
└──────────────┬────────────────────────────┘
               │
               ▼  (copied / joined on read)
┌───────────────────────────────────────────┐
│ technique_compute                          │
│   PK: (chart_id, rule_id, source_id,       │
│        rule_version)                       │
│   result, hashes                           │
└───────────────────────────────────────────┘
```

On compute:
1. Calculate fingerprint.
2. Check `compute_cache_by_fingerprint`. If hit → copy row to `technique_compute` for this chart (or read via join). Done.
3. If miss → run compute, insert into `compute_cache_by_fingerprint`, then insert into `technique_compute`.

Both tables keep `organization_id` so tenants are isolated.

**Option B (fallback, NOT implemented at P0):** keep `technique_compute` as-is; on new chart creation, compute its fingerprint, find all existing charts with same fingerprint in same org, copy their technique_compute rows. Simpler but incurs copy storms during bulk imports.

**Rationale for Option A:** cleaner, monotonically adds rows, doesn't require the chart creation path to know about every computed technique. Extra table is cheap. Migration cost is moderate but one-time.

### 3.6 Savings analysis

Back-of-envelope at 100M charts:
- Assume 0.1% of charts share fingerprint with ≥1 other chart (twins, imports, re-rolls). = 100,000 chart pairs.
- Average techniques per chart at full platform: ~10,000 (all dasa systems, all yogas, all vargas — heavy).
- Per-technique result row: ~500 bytes.
- Savings per duplicate chart: 10,000 × 500 = 5 MB.
- Total savings at 100M charts with 0.1% sharing: 100,000 × 5 MB = **500 GB**.

Relative to total `technique_compute` storage (~500 TB at 100M charts × 10k techniques × 500 bytes = 500 TB), that's 0.1%.

So: not a storage-optimization win primarily. The **correctness** win (twins see same computes) and the **future-optionality** win (near-neighbor cache, shared-reading flows, import-time deduplication) justify the build.

### 3.7 Edge cases

| Case | Fingerprint behavior | Correct? |
|---|---|---|
| Twin brothers A, B — same birth data | Same fingerprint | Yes (classical computes truly identical) |
| Chart imported from CSV, then user signs up and re-creates same chart | Same fingerprint | Yes (Ops can dedupe) |
| Same birth data, one user configured Lahiri, another configured KP | Different fingerprints | Yes (ayanamsa_id differs) |
| User edits birth time by 1 second | Different fingerprint | Yes (real chart difference) |
| Same chart stored as two rows with 37.7749 and 37.77494 lat (geocoder jitter) | Same fingerprint (both round to 37.7749) | Yes (correctly merged) |
| Chart near antimeridian: lon=-179.9999 vs 180.0001 (same place) | Different fingerprints | Acceptable edge case; ~0 users affected |
| Chart at exact pole: lat=90.0 | Works normally | Classical astrology is undefined at poles; we don't serve |
| Naive datetime snuck into DB | Fingerprint raises `CanonicalizationError` | Fail-fast catches data bug |

### 3.8 Alternatives considered

| Alternative | Rejected because |
|---|---|
| No fingerprinting; use `chart_id` only | Twins and imports silently re-compute everything |
| Round lat/lon to 5 decimals | Falsely splits charts due to geocoder jitter |
| Round to 3 decimals | Falsely merges distinct city neighborhoods |
| Include chart owner (user_id) in fingerprint | Defeats sharing entirely |
| Use H3 / S2 geospatial indexing for lat/lon | Over-engineered for exact-match cache |
| Fingerprint per ayanamsa implicit, not explicit | Easy to get wrong; explicit beats implicit |
| Cross-organization fingerprint sharing | Privacy/tenancy violation |

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| Option A vs Option B | Option A | Cleaner model, avoids copy storms |
| Rounding precision | 4 decimals (~11m) | Absorbs geocoder jitter, preserves classical precision |
| Include ayanamsa? | Yes | Different ayanamsas → different sidereal state |
| Cross-tenant sharing | No | Privacy / multi-tenancy invariant |
| Backfill existing charts | Yes, via one-shot migration | Otherwise Option A read path misses existing compute rows |
| Fingerprint column nullable | No — `NOT NULL` with trigger populating on INSERT/UPDATE | Invariant |
| Regenerate fingerprint on chart edit | Yes, in a `BEFORE UPDATE` trigger | Fingerprint must reflect current birth data |

## 5. Component Design

### 5.1 New modules

```
src/josi/services/chart_fingerprint/
├── __init__.py
└── fingerprint.py              # chart_canonical_fingerprint()

src/josi/models/classical/
└── compute_cache_by_fingerprint.py   # new SQLModel

src/josi/services/classical/
└── fingerprint_cache.py        # Option-A cache lookup helper

src/josi/scripts/
└── backfill_chart_fingerprints.py   # one-shot migration helper

tests/unit/services/chart_fingerprint/
└── test_fingerprint.py

tests/integration/chart_fingerprint/
└── test_cross_chart_cache.py
```

### 5.2 Data model

#### 5.2.1 Add fingerprint column to existing `astrology_chart`

```sql
ALTER TABLE astrology_chart
    ADD COLUMN canonical_fingerprint CHAR(64);

-- Backfill (executed as part of migration via a data migration step)
UPDATE astrology_chart
SET canonical_fingerprint = encode(
    digest(
        convert_to(
            '{"ayanamsa_id":' || to_jsonb(ayanamsa_id)::text ||
            ',"birth_utc":' || to_jsonb(birth_datetime_utc at time zone 'UTC')::text ||
            ',"lat_rounded":"' || round(birth_latitude::numeric, 4) ||
            '","lon_rounded":"' || round(birth_longitude::numeric, 4) || '"}',
            'UTF8'
        ),
        'sha256'
    ),
    'hex'
);

-- NOTE: Python-side backfill is preferred for byte-identical semantics vs
-- the app's canonical_json. The SQL above is shown for illustration; actual
-- backfill runs via backfill_chart_fingerprints.py to guarantee parity.

ALTER TABLE astrology_chart
    ALTER COLUMN canonical_fingerprint SET NOT NULL;

CREATE INDEX idx_chart_canonical_fingerprint
    ON astrology_chart(canonical_fingerprint);
```

Trigger to keep it fresh:

```sql
CREATE OR REPLACE FUNCTION refresh_chart_fingerprint()
RETURNS trigger AS $$
BEGIN
    -- Defer actual computation to the app layer on INSERT/UPDATE via ORM hook.
    -- The trigger's job here is to REJECT any INSERT/UPDATE lacking fingerprint,
    -- not to compute it (guarantees consistency with Python canonical_json).
    IF NEW.canonical_fingerprint IS NULL OR LENGTH(NEW.canonical_fingerprint) <> 64 THEN
        RAISE EXCEPTION 'canonical_fingerprint must be set by application layer';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_check_chart_fingerprint
    BEFORE INSERT OR UPDATE ON astrology_chart
    FOR EACH ROW EXECUTE FUNCTION refresh_chart_fingerprint();
```

The ORM layer (ChartService / chart repository) computes and sets the fingerprint before every insert/update of chart birth fields.

#### 5.2.2 New `compute_cache_by_fingerprint` table

```sql
CREATE TABLE compute_cache_by_fingerprint (
    organization_id          UUID NOT NULL REFERENCES organization(organization_id),
    canonical_fingerprint    CHAR(64) NOT NULL,
    rule_id                  TEXT NOT NULL,
    source_id                TEXT NOT NULL REFERENCES source_authority(source_id),
    rule_version             TEXT NOT NULL,
    technique_family_id      TEXT NOT NULL REFERENCES technique_family(family_id),
    output_shape_id          TEXT NOT NULL REFERENCES output_shape(shape_id),
    result                   JSONB NOT NULL,
    input_fingerprint        CHAR(64) NOT NULL,
    output_hash              CHAR(64) NOT NULL,
    computed_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (organization_id, canonical_fingerprint, rule_id, source_id, rule_version),
    FOREIGN KEY (rule_id, source_id, rule_version)
        REFERENCES classical_rule(rule_id, source_id, version)
);

CREATE INDEX idx_ccf_family
    ON compute_cache_by_fingerprint(canonical_fingerprint, technique_family_id);
```

Notes:
- PK includes `organization_id` for tenant isolation.
- Structure mirrors `technique_compute` but keyed by fingerprint instead of chart_id.
- `technique_compute` remains the chart-scoped view (engines still read/write it; F15 just adds the fingerprint-scoped backing cache).

### 5.3 Read / write path

```python
# src/josi/services/classical/fingerprint_cache.py

async def load_or_recompute_with_fingerprint(
    session: AsyncSession,
    chart: AstrologyChart,
    rule: ClassicalRule,
    extra_params: dict[str, Any],
    compute_fn: Callable[[], Awaitable[BaseModel]],
) -> tuple[BaseModel, CacheStatus]:
    """
    1. Compute desired input_fingerprint (F13).
    2. Look up compute_cache_by_fingerprint by (org_id, chart.canonical_fingerprint, rule_id, source_id, rule_version).
       a. If HIT and input_fingerprint matches → copy row to technique_compute (if missing), return result.
       b. If HIT but input_fingerprint differs (stale rule_body content) → treat as MISS.
    3. If MISS → invoke compute_fn(), insert into both tables in a single transaction.
    """
```

The chart-scoped `technique_compute` row is still maintained because:
- Downstream queries often join on chart_id directly.
- The aggregation layer (F8) reads from chart_id.
- Row-level audit and provenance (F13) use chart_id.

On cache HIT via fingerprint, we still materialize the chart-scoped row — it's a cheap insert and enables everything downstream.

### 5.4 API contract

No new public API. The `/api/v1/charts` endpoint response gains a debug field:

```json
{
  "success": true,
  "data": {
    "chart_id": "…",
    "birth_datetime_utc": "1879-12-30T19:30:00+00:00",
    …,
    "canonical_fingerprint": "a3f7…"   // new: exposed for debugging; stable
  }
}
```

### 5.5 Chart service integration

```python
# src/josi/services/chart_service.py  (existing, extended)

class ChartService:
    async def create_chart(self, data: ChartCreate) -> AstrologyChart:
        chart = AstrologyChart(**data.model_dump())
        chart.canonical_fingerprint = chart_canonical_fingerprint(chart)  # new
        chart = await self.repo.create(chart)
        return chart

    async def update_chart(self, chart_id: UUID, data: ChartUpdate) -> AstrologyChart:
        chart = await self.repo.get(chart_id)
        for k, v in data.model_dump(exclude_unset=True).items():
            setattr(chart, k, v)
        if _birth_fields_changed(data):
            chart.canonical_fingerprint = chart_canonical_fingerprint(chart)  # new
        return await self.repo.update(chart)
```

## 6. User Stories

### US-F15.1: As a pair of twins signing up separately, we see identical yoga activations without redundant compute
**Acceptance:** Twin A signs up → computes all yogas. Twin B signs up with identical birth data → `compute_cache_by_fingerprint` HIT → technique_compute rows for twin B materialized by copy, no engine invocation. Timing < 200ms vs ~5s for cold compute.

### US-F15.2: As an astrologer, I import a CSV of 100 clients with precise birth data. Many have Clerk-registered accounts. Imports should not re-compute for charts whose fingerprints already exist.
**Acceptance:** Bulk import of 100 charts, 30 of which collide with existing fingerprints → only 70 engine invocations, all 100 charts have full compute rows within 2 minutes.

### US-F15.3: As a user, if I correct my birth time by 1 second, I expect my computes to refresh
**Acceptance:** Edit birth time by 1 second → fingerprint changes → next compute invocation is a MISS, re-runs engine, inserts new rows.

### US-F15.4: As an ops engineer, I want to see fingerprint in the chart record for debugging
**Acceptance:** `GET /api/v1/charts/{id}` returns `canonical_fingerprint`. `psql` lookup by fingerprint works with the idx index.

### US-F15.5: As a multi-tenant architect, I want fingerprints never to cross-pollinate between organizations
**Acceptance:** Two orgs each create a chart with identical birth data. Org A computes yogas. Org B's subsequent compute is a MISS (not HIT), because `compute_cache_by_fingerprint` PK includes `organization_id`.

## 7. Tasks

### T-F15.1: `chart_canonical_fingerprint` utility
- **Definition:** Implement per §3.1. Uses F13's `canonical_json`. Pure function.
- **Acceptance:** Unit tests pass; golden hex value for a known chart matches.
- **Effort:** 2 hours
- **Depends on:** F13 complete

### T-F15.2: Alembic migration — add column + trigger
- **Definition:** `alembic revision --autogenerate -m "F15: chart canonical fingerprint"` + manual trigger; column initially nullable for backfill, then ALTER NOT NULL.
- **Acceptance:** Migration applies cleanly; can be rolled back.
- **Effort:** 3 hours
- **Depends on:** T-F15.1

### T-F15.3: Backfill script
- **Definition:** `backfill_chart_fingerprints.py` iterates `astrology_chart` in batches of 10,000, computes fingerprint via Python (identical to runtime), writes in transaction.
- **Acceptance:** After run, 100% of chart rows have non-null fingerprint; spot-check 10 random rows match Python recomputation.
- **Effort:** 3 hours
- **Depends on:** T-F15.2

### T-F15.4: Alembic migration — ALTER NOT NULL
- **Definition:** Follow-up migration after backfill complete.
- **Acceptance:** Column NOT NULL; trigger active.
- **Effort:** 1 hour
- **Depends on:** T-F15.3

### T-F15.5: `compute_cache_by_fingerprint` table
- **Definition:** Migration for the new table per §5.2.2.
- **Acceptance:** Table exists with correct PK, FK, indexes.
- **Effort:** 2 hours
- **Depends on:** F2 complete

### T-F15.6: `load_or_recompute_with_fingerprint` helper
- **Definition:** Per §5.3. Replaces F13's `load_or_recompute` as the standard engine helper (F13's version becomes a simpler internal primitive).
- **Acceptance:** Integration test demonstrates HIT / MISS / STALE across two charts with same fingerprint.
- **Effort:** 5 hours
- **Depends on:** T-F15.5, F13 complete

### T-F15.7: ChartService integration
- **Definition:** Populate fingerprint on create/update per §5.5.
- **Acceptance:** Creating a chart via API yields non-null fingerprint in DB and in response.
- **Effort:** 2 hours
- **Depends on:** T-F15.1, T-F15.2

### T-F15.8: Expose fingerprint in chart API response
- **Definition:** Add field to Chart Pydantic response schema.
- **Acceptance:** `GET /api/v1/charts/{id}` response includes `canonical_fingerprint`.
- **Effort:** 1 hour
- **Depends on:** T-F15.7

### T-F15.9: Tests
- **Definition:** Full test suite per §8.
- **Acceptance:** All tests pass; coverage ≥ 95% on new modules.
- **Effort:** 4 hours
- **Depends on:** T-F15.6, T-F15.7

### T-F15.10: Documentation
- **Definition:** Update `CLAUDE.md`; add section to `docs/markdown/provenance.md` (created in F13) describing fingerprint semantics.
- **Acceptance:** Doc committed.
- **Effort:** 1 hour
- **Depends on:** T-F15.6

## 8. Unit Tests

### 8.1 `chart_canonical_fingerprint`

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_stable_across_runs` | fixed chart | same hex twice | determinism |
| `test_golden_value` | hand-crafted Ramana-era chart | documented golden hex | regression guard |
| `test_twins_same_fingerprint` | two charts with identical birth fields | identical hex | twin semantics |
| `test_lat_rounding_absorbs_jitter` | lat=37.77490 vs 37.77495 | same hex (both → 37.7749) | 4-dp rounding |
| `test_lat_5th_decimal_boundary` | lat=37.77495 vs 37.77496 (rounds differently) | different hex | boundary correctness |
| `test_lon_sign_matters` | lon=-122.4 vs 122.4 | different hex | signed comparison |
| `test_tz_normalization` | naive datetime | raises `CanonicalizationError` | strict UTC only |
| `test_non_utc_timezone_normalized` | Asia/Kolkata datetime | same hex as equivalent UTC datetime | normalization |
| `test_ayanamsa_included` | same chart, ayanamsa=lahiri vs kp | different hex | ayanamsa sensitivity |
| `test_returns_64char_lowercase_hex` | any chart | matches `^[0-9a-f]{64}$` | format contract |

### 8.2 `compute_cache_by_fingerprint` table behavior

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_pk_includes_org_id` | insert same (fingerprint, rule, source, version) across 2 orgs | both succeed, isolated | multi-tenancy |
| `test_fk_to_classical_rule` | insert with unknown rule | IntegrityError | referential integrity |
| `test_index_used_for_lookup` | EXPLAIN on `(org_id, fingerprint, rule_id, source_id, rule_version)` lookup | uses PK index | perf |

### 8.3 `load_or_recompute_with_fingerprint`

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_miss_then_hit_same_org_different_charts` | chart A compute (MISS) → chart B same fingerprint compute | chart B is HIT, engine not invoked | cross-chart sharing |
| `test_miss_then_miss_different_org` | org 1 chart compute (MISS) → org 2 chart same fingerprint | MISS (multi-tenancy) | tenant isolation |
| `test_stale_recompute_updates_fingerprint_cache` | rule content_hash changes | MISS path triggered, both tables updated | staleness coherence |
| `test_chart_edit_changes_fingerprint` | edit birth time 1 sec | new fingerprint, cache lookup misses | chart identity update |
| `test_concurrent_compute_same_fingerprint_idempotent` | two workers compute concurrently | exactly one row in each table, no errors | UPSERT safety |

### 8.4 Chart API integration

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_chart_create_populates_fingerprint` | POST /api/v1/charts | response has fingerprint | service integration |
| `test_chart_update_changes_fingerprint` | PUT birth time | new fingerprint | update flow |
| `test_chart_update_nonbirth_preserves_fingerprint` | PUT chart name only | same fingerprint | no false invalidation |

### 8.5 Backfill

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_backfill_populates_all_rows` | 10k rows pre-seeded | all 10k have non-null fingerprint post-run | completeness |
| `test_backfill_idempotent` | run twice | second run is no-op | safety |
| `test_backfill_matches_runtime_util` | 100 random rows | backfilled fingerprint matches Python recomputation | parity |

## 9. EPIC-Level Acceptance Criteria

- [ ] `chart_canonical_fingerprint` utility deterministic and unit-tested
- [ ] `astrology_chart.canonical_fingerprint` column NOT NULL, indexed, trigger-enforced
- [ ] `compute_cache_by_fingerprint` table created and FK-integrated
- [ ] `load_or_recompute_with_fingerprint` helper used by all downstream engines (F8, E1a+)
- [ ] Backfill script executed; 100% of existing charts have fingerprint
- [ ] Twins integration test: two charts same birth data → one compute, two chart-scoped row sets
- [ ] Tenant-isolation integration test: two orgs same birth data → no cross-tenant cache hit
- [ ] Unit test coverage ≥ 95% on new modules
- [ ] Chart API response includes fingerprint
- [ ] `CLAUDE.md` updated
- [ ] No engine bypasses the fingerprint-aware cache helper

## 10. Rollout Plan

- **Feature flag:** `ENABLE_FINGERPRINT_CACHE` — default ON after successful backfill in staging; controls whether engines use `load_or_recompute_with_fingerprint` (the cross-chart path) vs F13's `load_or_recompute` (chart-only path). P0 leaves flag ON; P1+ removes the flag.
- **Shadow compute:** Yes — for 48 hours in staging, both paths run on every compute; results compared byte-for-byte; discrepancies alert. Staging-only.
- **Backfill strategy:**
  1. Ship migration (column nullable).
  2. Run `backfill_chart_fingerprints.py` in maintenance window (~30 min at 10M charts with batched updates).
  3. Ship follow-up migration (NOT NULL).
  4. Enable `ENABLE_FINGERPRINT_CACHE`.
- **Rollback plan:** Flip flag OFF → engines use F13 path only; no data loss. Migrations are reversible. `compute_cache_by_fingerprint` can be dropped without affecting `technique_compute`.

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Backfill takes longer than expected at 100M scale | Medium | Medium | Batched updates, off-peak window, progress metrics; can resume from checkpoint |
| Python backfill computes differ from runtime util (drift) | Low | High | Same code path used for both; parity test in §8.5 |
| Trigger blocks legitimate inserts if fingerprint missed | Low | High | ORM layer always sets fingerprint; trigger is defense-in-depth |
| Cross-tenant leak if org_id forgotten in query | Low | High | PK on `compute_cache_by_fingerprint` includes org_id; repository base class auto-filters (existing convention) |
| Fingerprint collisions (sha256) | Effectively zero | — | 2^256 space |
| Chart edits storm invalidates cache unnecessarily | Low | Medium | Edit-detection skips non-birth-field updates; fingerprint recomputed only when birth fields change |
| Storage cost of duplicating rows in two tables | Medium | Low | 2× disk; analysis in §3.6 shows total is bounded; could denormalize away later |
| Engines written before F15 bypass the helper | Medium | Medium | Lint rule: direct `technique_compute` INSERTs flagged; must go via helper |
| Existing `technique_compute` rows have no fingerprint counterpart | Medium | Medium | Lazy population — on next read, populate fingerprint cache; or one-shot script to backfill if desired |

## 12. References

- Master spec: [`docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`](../../../superpowers/specs/2026-04-19-classical-techniques-expansion-design.md)
- F2 fact tables: [`F2-fact-tables.md`](./F2-fact-tables.md)
- F13 content-hash provenance: [`F13-content-hash-provenance.md`](./F13-content-hash-provenance.md)
- Geocoding precision: [OpenStreetMap Nominatim Precision](https://nominatim.org/release-docs/latest/api/Search/)
- Ayanamsa background: Swiss Ephemeris documentation
- Related downstream: S3 (3-layer cache builds on this), S6 (lazy compute uses fingerprint for cache identity)
