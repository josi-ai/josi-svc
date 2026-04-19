---
prd_id: F14
epic_id: F14
title: "Deterministic seeding for stochastic operations"
phase: P0-foundation
tags: [#correctness]
priority: should
depends_on: []
enables: [E1a, E11a, E11b, E14a, AI5]
classical_sources: []
estimated_effort: 1 day
status: draft
author: Govind
last_updated: 2026-04-19
---

# F14 — Deterministic Seeding for Stochastic Operations

## 1. Purpose & Rationale

Astrology is deterministic by nature: a birth chart has one correct planetary configuration. However, several parts of Josi's engine layer introduce *optional* randomness:

- **Monte Carlo uncertainty bands** on dasa timing (planned for E1b refinement; scaffolded in E1a).
- **Similar-chart top-k sampling** when Qdrant returns many high-similarity candidates and we choose which to surface.
- **Prediction confidence bootstrap** when aggregating per-source computes via strategy B (F8) uses bootstrap resampling.
- **AI-chat exemplar selection** when we show "users with similar charts experienced X."

If any of these operations use an un-seeded RNG, the same chart produces different results on repeat invocation — violating user trust, breaking cache invalidation, and making bug reports irreproducible.

F14 delivers a single, tiny utility — `get_deterministic_seed(chart_id, context_key)` — plus a governance policy: **no engine code may call `random.random`, `np.random.rand`, etc. without first obtaining a seeded generator via this utility**.

The PRD is small by design. Scope is a one-file module, a handful of tests, and a lint/CI rule.

## 2. Scope

### 2.1 In scope
- `get_deterministic_seed(chart_id: UUID, context_key: str) -> int` utility
- `get_seeded_rng(chart_id: UUID, context_key: str) -> random.Random` convenience
- `get_seeded_numpy_rng(chart_id: UUID, context_key: str) -> numpy.random.Generator` convenience
- A registry/catalog of sanctioned `context_key` values (prevents typos that silently share seed state)
- Linting rule (ruff / custom AST check) that flags unsanctioned `random` / `numpy.random` calls inside `src/josi/services/classical/**` and `src/josi/services/ai/**`

### 2.2 Out of scope
- Replacing non-deterministic sources *outside* chart compute (e.g., test fixtures, request IDs, CSRF tokens — those should remain non-deterministic).
- Changing any existing engine (those are not yet implemented at P0).
- Cryptographic-quality random — we use sha256-derived seeds for reproducibility, NOT for security. Any security-sensitive randomness must continue to use `secrets.token_bytes`.

### 2.3 Dependencies
- None. This is a leaf utility.

## 3. Technical Research

### 3.1 Why seed from `chart_id` and not from chart content

`chart_id` is a UUID assigned at chart creation, immutable thereafter. Using it as the seed basis means:
- Same chart → same seed, always.
- Two charts with identical birth data (twins, shared chart imports) get **different** seeds — this is correct because the random operation may legitimately differ for them (e.g., sampling similar-chart peers based on chart_id identity).
- We do NOT mix chart content into the seed because recompute-after-geocode-refinement (F13 staleness) should NOT change stochastic sampling (otherwise the user sees "different similar-chart peers" after a harmless geocoding update).

Tradeoff accepted: if a chart is migrated between systems with a new UUID, its stochastic outputs change. This is rare (import/export flow) and the user expects novelty in that case.

### 3.2 Why a `context_key` argument

Distinct stochastic processes within the same chart must NOT share seed state, or correlations appear. Example:

```
# bad:
rng = seeded(chart_id)
mc_result = monte_carlo(rng)        # consumes ~100 values
peers    = sample_peers(rng, k=5)   # now peers depends on mc_result length
```

By requiring a `context_key`, each process gets its own independent sub-stream:

```
mc_rng    = get_seeded_rng(chart_id, "vimshottari_monte_carlo")
peer_rng  = get_seeded_rng(chart_id, "similar_chart_sampling")
mc_result = monte_carlo(mc_rng)
peers     = sample_peers(peer_rng, k=5)  # independent of mc_result
```

### 3.3 Seed derivation

```python
def get_deterministic_seed(chart_id: UUID, context_key: str) -> int:
    digest = hashlib.sha256(chart_id.bytes + context_key.encode("utf-8")).digest()
    # Take first 8 bytes → unsigned 64-bit int; numpy/python accept this.
    return int.from_bytes(digest[:8], "big", signed=False)
```

Why first 8 bytes: Python's `random.Random(seed)` and `numpy.random.default_rng(seed)` both accept a Python int up to arbitrary size, but many library functions down the line have historically preferred 64-bit. Using the top 8 bytes of sha256 gives 2^64 distinct seeds — vastly more than 2^40 chart-context combinations we'll ever see.

### 3.4 Sanctioned context_key registry

Free-form strings invite typos (`"monte_carlo_dasa"` vs `"monte_carlo_dasas"`) that silently share seed space and cause bugs with no error. The solution: an enum/frozen-set of sanctioned values, checked at runtime.

```python
# src/josi/services/randomness/context_keys.py
class SeedContext(StrEnum):
    VIMSHOTTARI_MONTE_CARLO         = "vimshottari_monte_carlo"
    YOGINI_MONTE_CARLO              = "yogini_monte_carlo"
    SIMILAR_CHART_SAMPLING          = "similar_chart_sampling"
    CONFIDENCE_BOOTSTRAP            = "confidence_bootstrap"
    EXEMPLAR_SELECTION_AI_CHAT      = "exemplar_selection_ai_chat"
    AI_CHAT_EXAMPLE_JITTER          = "ai_chat_example_jitter"
```

New stochastic uses add an entry here as part of their PRD; code review enforces.

The utility accepts both `SeedContext` enum and raw string for pragmatic testing but emits a warning (or raises in strict mode) if a non-enum string is passed from production code paths.

### 3.5 Alternatives considered

| Alternative | Rejected because |
|---|---|
| Hash entire chart content into seed | Recompute-after-geocoding would change peer sampling silently |
| Single global RNG seeded once per process | Shared state across charts and concurrent requests → unreproducible |
| Mersenne Twister via `random.seed(int(chart_id))` | UUID ints exceed 2^64 and lead to undefined seed-state coercion in older numpy; sha256 trim is explicit |
| Free-form context strings | Typo-prone; no registry → bugs silently share state |
| Skip seeding (accept non-determinism) | Breaks cache invalidation, breaks tests, breaks bug reports |

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| Use 8 bytes or 16 bytes of digest | 8 bytes | Fits 64-bit int, plenty for our cardinality |
| Accept raw strings or force enum | Accept string, warn-on-non-enum | Pragmatic for tests; governance for prod |
| Cryptographic quality? | No — sha256 used for reproducibility not security | security-critical code uses `secrets` module |
| Seed type | Python int | Works with both stdlib `random` and `numpy.random.default_rng` |
| Expose a `get_seeded_numpy_rng` helper | Yes | Most Monte Carlo code paths use numpy |
| Global monkey-patch `random` | No | Explicit is better; monkey-patching breaks thread safety |

## 5. Component Design

### 5.1 New modules

```
src/josi/services/randomness/
├── __init__.py
├── context_keys.py            # SeedContext StrEnum
└── seeding.py                 # get_deterministic_seed, get_seeded_rng, get_seeded_numpy_rng

tests/unit/services/randomness/
├── test_seeding.py
└── test_context_keys.py

tools/lint/
└── forbid_unseeded_random.py  # AST-based check (runs in CI)
```

### 5.2 Data model

No database changes.

### 5.3 API contract

```python
# src/josi/services/randomness/seeding.py

import hashlib
import random
from typing import Union
from uuid import UUID

import numpy as np

from josi.services.randomness.context_keys import SeedContext


def get_deterministic_seed(
    chart_id: UUID,
    context_key: Union[SeedContext, str],
    *,
    strict: bool = False,
) -> int:
    """
    Derive a deterministic 64-bit int seed from (chart_id, context_key).

    Args:
        chart_id: The chart's UUID. Immutable across chart edits.
        context_key: Either a SeedContext enum value or a raw string. If a raw
                     string is passed and `strict=True` or
                     `JOSI_SEED_STRICT=true` env var is set, ValueError is
                     raised. Otherwise, a logger.warning is emitted.
        strict: If True, reject non-enum context_keys.

    Returns:
        Unsigned 64-bit int suitable for random.Random or np.random.default_rng.

    Raises:
        ValueError: if strict and context_key is not a SeedContext.
    """
    key_str = context_key.value if isinstance(context_key, SeedContext) else context_key
    if not isinstance(context_key, SeedContext):
        _warn_or_raise_nonenum(key_str, strict)
    digest = hashlib.sha256(chart_id.bytes + key_str.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big", signed=False)


def get_seeded_rng(
    chart_id: UUID,
    context_key: Union[SeedContext, str],
    *,
    strict: bool = False,
) -> random.Random:
    """Return a stdlib Random() seeded deterministically."""
    return random.Random(get_deterministic_seed(chart_id, context_key, strict=strict))


def get_seeded_numpy_rng(
    chart_id: UUID,
    context_key: Union[SeedContext, str],
    *,
    strict: bool = False,
) -> np.random.Generator:
    """Return a numpy Generator seeded deterministically."""
    return np.random.default_rng(get_deterministic_seed(chart_id, context_key, strict=strict))
```

### 5.4 Use-case catalog (for reviewers)

These are the known / planned randomness call sites. Each new PRD using RNG must add its entry here *and* a `SeedContext` enum value.

| Use case | PRD | Context key | Notes |
|---|---|---|---|
| Vimshottari Monte Carlo uncertainty | E1b | `VIMSHOTTARI_MONTE_CARLO` | simulates dasa-start jitter from birth-time uncertainty |
| Yogini Monte Carlo uncertainty | E1b | `YOGINI_MONTE_CARLO` | same, different system |
| Similar-chart top-k sampling | E11a | `SIMILAR_CHART_SAMPLING` | Qdrant returns 50; we sample 5 to surface |
| Confidence bootstrap (strategy B/C) | F8, E14a | `CONFIDENCE_BOOTSTRAP` | resamples per-source results for CI bands |
| AI-chat exemplar selection | E11a | `EXEMPLAR_SELECTION_AI_CHAT` | picks which past-chart example to cite |
| AI-chat prompt-jitter (example rotation) | E11b | `AI_CHAT_EXAMPLE_JITTER` | rotates example order in prompt for cache diversity |

### 5.5 Lint rule

```python
# tools/lint/forbid_unseeded_random.py

"""
AST check: flag direct imports from 'random' or 'numpy.random' in
src/josi/services/classical/** and src/josi/services/ai/** unless
the file imports get_seeded_rng/get_seeded_numpy_rng and the random
calls are known-safe helpers.

Approved exception: 'secrets' module calls are always allowed.
"""
```

Wired into `poetry run flake8` via a small plugin OR invoked as a standalone pytest step. Specifics at implementation time; either approach acceptable.

## 6. User Stories

### US-F14.1: As an engineer, I want Monte Carlo to produce the same dasa uncertainty band on repeat calls for the same chart
**Acceptance:** calling the Monte Carlo helper twice with the same `chart_id` yields byte-identical result dicts, and `output_hash` (F13) matches.

### US-F14.2: As an engineer, I want two different stochastic operations on the same chart to be independent
**Acceptance:** different `context_key` values produce statistically-independent sequences (no correlation within a realistic sample size).

### US-F14.3: As a reviewer, I want to catch typos in context_keys at code-review time
**Acceptance:** introducing `"monte_carlo_dasaz"` as a raw string in a production PR triggers the lint rule and fails CI until the author either adds a `SeedContext` enum value or corrects the typo.

### US-F14.4: As a bug-report triager, I want to reproduce any stochastic result from logs
**Acceptance:** given a `chart_id` and context_key from a log line, running `get_seeded_rng(...)` locally reproduces the exact RNG sequence the production process saw.

## 7. Tasks

### T-F14.1: Implement seeding module
- **Definition:** `seeding.py` + `context_keys.py` per §5.3. Initial `SeedContext` has the 6 known values from §5.4.
- **Acceptance:** mypy clean; functions documented; unit tests pass.
- **Effort:** 2 hours
- **Depends on:** nothing

### T-F14.2: Unit tests
- **Definition:** Tests per §8.1 and §8.2.
- **Acceptance:** Coverage ≥ 100% on `seeding.py` and `context_keys.py`.
- **Effort:** 2 hours
- **Depends on:** T-F14.1

### T-F14.3: Lint rule
- **Definition:** AST-based check flagging unsanctioned random calls inside target dirs.
- **Acceptance:** A deliberate violation in a temp file fails CI; removing the violation passes CI.
- **Effort:** 2 hours
- **Depends on:** T-F14.1

### T-F14.4: Documentation
- **Definition:** Add a `docs/markdown/stochastic-operations.md` (or a section in `CLAUDE.md`) explaining: "All randomness inside engines MUST use `get_seeded_rng(chart_id, SeedContext.X)`. Add a new `SeedContext` value in the same PR that introduces a new stochastic operation."
- **Acceptance:** doc committed; `CLAUDE.md` cross-links it.
- **Effort:** 1 hour
- **Depends on:** T-F14.1

### T-F14.5: Use-case catalog table in this PRD
- **Definition:** Already captured in §5.4; maintained as living doc updated by downstream PRDs.
- **Acceptance:** Each P1/P2 PRD that introduces randomness links back to F14 and adds a catalog entry.
- **Effort:** 0 (governance only)

## 8. Unit Tests

### 8.1 `get_deterministic_seed`

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_same_chart_same_context_same_seed` | `(uuid_A, SeedContext.VIMSHOTTARI_MONTE_CARLO)` × 2 | identical int | determinism |
| `test_same_chart_different_context_different_seed` | `(uuid_A, ctx1)` vs `(uuid_A, ctx2)` | different ints | stream independence |
| `test_different_chart_same_context_different_seed` | `(uuid_A, ctx)` vs `(uuid_B, ctx)` | different ints | chart isolation |
| `test_returns_unsigned_64bit_range` | arbitrary input | `0 <= seed < 2**64` | format contract |
| `test_accepts_enum_and_string` | enum member and enum.value string | same seed | API flexibility |
| `test_warns_on_nonenum_string_in_non_strict` | `"adhoc_key"` | `logger.warning` emitted, returns seed | default behavior |
| `test_raises_on_nonenum_string_in_strict` | `"adhoc_key"`, `strict=True` | `ValueError` | strict mode |
| `test_env_var_strict_mode` | `JOSI_SEED_STRICT=true` + non-enum string | `ValueError` | env-driven strict |
| `test_known_golden_value` | fixed uuid + `VIMSHOTTARI_MONTE_CARLO` | known golden int | regression guard |

### 8.2 `get_seeded_rng` and `get_seeded_numpy_rng`

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_rng_reproducible_sequence` | call `.random()` 5 times from freshly-seeded RNG twice | identical 5-tuples | reproducibility |
| `test_numpy_rng_reproducible_sequence` | `.standard_normal(100)` twice | identical arrays | numpy reproducibility |
| `test_rng_different_contexts_statistically_independent` | sample 10k values from two contexts | Pearson correlation coefficient \|r\| < 0.05 | independence (sanity-level, not cryptographic) |
| `test_numpy_rng_default_rng_type` | returned object | is `np.random.Generator` | API contract |

### 8.3 `SeedContext` enum

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_context_values_unique` | all enum values | no duplicates | correctness |
| `test_context_values_snake_case` | each `.value` | regex `^[a-z][a-z0-9_]*$` | convention |
| `test_context_catalog_matches_prd_table` | comparing enum to the §5.4 table | same set | doc-code sync |

### 8.4 Lint rule

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_lint_flags_unsanctioned_random_call` | file with `import random; random.random()` in `services/classical/` | lint failure | enforcement |
| `test_lint_allows_secrets_module` | file with `from secrets import token_bytes` | pass | crypto exception |
| `test_lint_allows_seeded_helpers` | file using `get_seeded_rng` | pass | happy path |
| `test_lint_scope_bounded` | file in `tests/` with `random.random()` | pass | only engines enforced |

## 9. EPIC-Level Acceptance Criteria

- [ ] `get_deterministic_seed`, `get_seeded_rng`, `get_seeded_numpy_rng` implemented and tested
- [ ] `SeedContext` enum contains the 6 initial values; new additions follow the §5.4 catalog pattern
- [ ] Lint rule active in CI and green on the existing codebase (no current engine uses raw random)
- [ ] Unit test coverage = 100% on `services/randomness/*`
- [ ] Cross-Python-version test: same golden seed value on 3.12 and 3.13
- [ ] `CLAUDE.md` updated with the "All randomness uses F14" rule
- [ ] Catalog in §5.4 documented as the authoritative registry

## 10. Rollout Plan

- **Feature flag:** none — leaf utility.
- **Shadow compute:** N/A.
- **Backfill strategy:** N/A — no existing stochastic code paths at P0.
- **Rollback plan:** `git revert`. Pure-function module with no DB or state side effects.

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Engineers forget to use F14 and reach for `random` directly | Medium | Medium | Lint rule enforces in CI |
| Two PRDs add the same logical context with different enum names | Low | Medium | Catalog table in §5.4 reviewed as part of PRD review |
| sha256 truncation to 64 bits reduces independence | Very low | Low | 2^64 space is ample; Pearson correlation test in §8.2 validates |
| numpy API change across versions | Low | Low | Pinned numpy version in poetry; test on upgrade |
| Non-chart-scoped randomness (batch jobs without a chart_id) | Medium | Low | Out of scope; those use `secrets` or normal `random` freely |

## 12. References

- Master spec: [`docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`](../../../superpowers/specs/2026-04-19-classical-techniques-expansion-design.md)
- Python `hashlib` stdlib
- NumPy `Generator` docs: https://numpy.org/doc/stable/reference/random/generator.html
- F13 content-hash provenance: seeded RNG yields stable `output_hash`
- Related downstream PRDs: E1a (dasa MC), E11a (similar-chart sampling), E14a (bootstrap)
