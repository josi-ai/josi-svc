---
prd_id: P4-E4-tenant
epic_id: E4
title: "Per-tenant rule overrides (B2B white-label classical lineage)"
phase: P4-scale-100m
tags: [#multi-tenant, #extensibility, #correctness]
priority: must
depends_on: [F1, F2, F4, F5, F6, F13, P3-E2-console, S8]
enables: [Reference-1000]
classical_sources: []
estimated_effort: 4-5 weeks
status: draft
author: "@agent"
last_updated: 2026-04-19
---

# P4-E4-tenant — Per-Tenant Rule Overrides

## 1. Purpose & Rationale

Josi's classical-rule registry is curated globally: "BPHS v1.0 Gaja Kesari" means exactly one thing to every consumer of Josi's API. That is correct for neutral consumption but wrong for a growing class of B2B customers who have their own lineage tradition and want Josi to reflect *their* interpretation.

Concrete example: "Tamil Nadu Jyotish Mandali" (white-label brand) teaches that Gaja Kesari requires the Moon-Jupiter kendra to be within orb 3°, not 10°. Their astrologers and their consumers expect this interpretation. Today they cannot consume Josi's BPHS authority without a contradiction.

This PRD introduces **per-tenant rule overrides**: a B2B org can publish override rule bodies that supersede specific classical rules *only within that org's scope*. Every overridden compute row is labeled with the override metadata so audit, analytics, and the AI interpretation layer understand what happened and cite the override explicitly.

Business impact: unlocks temple federations, astrologer guild white-labels, classical-school SaaS deals, and the Reference-1000 long-tail yoga catalog (different lineages emphasize different yogas). This is directly tied to the enterprise tier (P5 D9) pricing model.

## 2. Scope

### 2.1 In scope

- New table `tenant_rule_override` keyed by `(organization_id, rule_id, source_id)` with JSONB override body
- Rule engine resolution: at compute time, check tenant override first; fall back to global `classical_rule`
- Override rule bodies conform to the same `output_shape` JSON Schema as the overridden rule (F5 / F7)
- Every `technique_compute` row carries provenance: `rule_source_kind ∈ {global, tenant_override}`, `override_id` nullable
- Audit fields: who created/updated the override, reason, version, effective dates
- Admin UI (extends P3-E2-console) with override authoring and diff preview against global rule
- Shadow / rollout controls per override, reusing S8 infrastructure
- AI interpretation layer aware of overrides: citation text reflects "per [tenant_display_name] lineage" when override active
- Migration safety: override body must pass output-shape JSON Schema validation (F5)
- Bulk-import tool for lineages with many overrides
- Billing instrumentation: count active overrides per org for enterprise-tier metering

### 2.2 Out of scope

- Cross-tenant override sharing / marketplace of lineage packs — reserved for P5
- Per-user overrides (within a tenant) — infeasible at scale; astrologers use `astrologer_source_preference` (F2) for personal weighting
- Overriding non-rule artifacts (interpretation templates, UI strings) — handled in E12/E13
- Custom output_shapes — an override cannot change the shape of a rule's output, only the rule body
- Override inheritance hierarchies (parent org → child org) — P5 if needed
- Automatic generation of overrides from natural-language lineage text — P5 AI authoring

### 2.3 Dependencies

- **F1** — dimension tables (`source_authority`, `technique_family`, `output_shape`)
- **F2** — fact tables; `technique_compute` needs to gain override provenance columns
- **F4** — temporal rule versioning (overrides are versioned)
- **F5** — JSON Schema validation (overrides validated at write time)
- **F6** — rule DSL and YAML loader (same DSL used for override bodies)
- **F13** — content-hash provenance (override bodies hashed; compute rows tie to override hash)
- **P3-E2-console** — UI substrate for override authoring
- **S8** — shadow-compute rule migrations (overrides reuse promotion machinery)

## 3. Technical Research

### 3.1 Where resolution happens

Two candidate locations:

- **At rule-load time** — merge tenant override into an in-memory "effective rule table" at worker startup per tenant. Fast compute path, but complicates cache invalidation when overrides change (every tenant's workers must reload), and explodes memory on worker pods that serve many tenants.
- **At compute time** — rule engine receives `organization_id` on every invocation; checks `tenant_rule_override` before falling back to `classical_rule`. Adds one cached lookup per compute.

We pick **compute-time** resolution with an aggressive L1 cache. The per-compute cost is one Redis GET (~0.5 ms) keyed by `(organization_id, rule_id, source_id)`. Cache invalidation is a single DEL on override CRUD. Memory cost scales with active overrides, not with tenant count.

### 3.2 Override body fidelity

An override body is structurally identical to a `classical_rule.rule_body` JSONB (F6 DSL). That invariant is load-bearing:

- Same parser in F6 DSL interpreter
- Same output_shape validation in F5
- Same golden-chart test harness in F16

Overrides that don't fit the shape are rejected at write time.

### 3.3 Audit fidelity

Every compute row produced under override must be distinguishable from a global-rule compute. Schema additions:

```sql
ALTER TABLE technique_compute
  ADD COLUMN rule_source_kind TEXT NOT NULL DEFAULT 'global'
    CHECK (rule_source_kind IN ('global','tenant_override')),
  ADD COLUMN tenant_rule_override_id UUID REFERENCES tenant_rule_override(id);
```

This is ~20 bytes per row × 200B rows = 4 TB additional storage (compared to the base fact-table size). Not material at P4 scale and essential for correctness.

### 3.4 Content hashing

`tenant_rule_override.content_hash` follows F13's canonical JSON serialization. When a compute row is produced under override, the `input_fingerprint` incorporates the override's content_hash, so recompute invalidation on override edit is automatic via F13's dependency graph.

### 3.5 Override-aware AI citation

F11 guarantees every AI tool-use response carries citations. Under override, citations become compound:

```json
{
  "rule": "gaja_kesari",
  "base_source": { "id": "bphs", "citation": "BPHS Ch.36 v.14-16" },
  "override_source": {
    "tenant": "tamil_nadu_jyotish_mandali",
    "citation": "TNJM Internal Commentary §4.2",
    "reason": "Orb constraint 3° per lineage tradition"
  }
}
```

The LLM prompt includes the override metadata so generated text says "per [tenant] lineage" where appropriate. Chat users not affiliated with the tenant never see the override (resolution is scoped by `organization_id`).

### 3.6 Alternatives considered

| Alternative | Rejected because |
|---|---|
| Fork the entire `classical_rule` table per tenant | Explodes storage; loses updates to global rules |
| Allow tenant overrides at runtime via config (no DB row) | No audit, no versioning, no JSON Schema validation |
| Store overrides as source_id = 'tenant_<uuid>' | Pollutes the source dimension; breaks "source_id → lineage tradition" invariant |
| Store override as YAML in Git per tenant | Not possible at scale (20k tenants); authoring UX unworkable for non-engineer tenant admins |
| Client-side override (tenant post-processes Josi's output) | Breaks consistency for AI chat, astrologer UI, audit |

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| Override primary key shape | `(organization_id, rule_id, source_id)` unique; surrogate UUID id for FK target | Enables FK from compute rows; uniqueness prevents duplicates |
| Can an override override another override? | No | Keep resolution linear; overrides target global rules only |
| Override versioning | Yes, full `version` + `effective_from`/`effective_to` per F4 | Safe rollouts, shadow compute via S8 |
| Rollout controls | Reuses S8 promotion machinery | Consistency with global rule migrations |
| Override-visible to non-tenant users? | Never | Strict tenant isolation |
| Can astrologers inside a tenant override further? | No (their `astrologer_source_preference` affects weighting, not rule body) | Separation of concerns |
| Limit on overrides per tenant | Soft cap 500, hard cap 2000 | Prevents abuse; metered for enterprise tier |
| Can an override modify output_shape? | No | Shape is a structural contract; changing it breaks downstream consumers |
| Cache policy | L1 Redis, TTL 1 hour, invalidated on CRUD | Trades 1-hour eventual consistency for 10× compute cost reduction |
| Override audit retention | Indefinite (like `classical_rule`) | Regulatory and trust |
| Who can author overrides | Users with `tenant_rule_author` role in that org | Role gated via org-admin |
| Classical advisor sign-off | Required at override activation (matches S8 gate) | Correctness gate |

## 5. Component Design

### 5.1 New services / modules

```
src/josi/services/overrides/
├── __init__.py
├── override_repository.py         # CRUD on tenant_rule_override
├── override_resolver.py           # compute-time resolution with L1 cache
├── override_validator.py          # JSON Schema + golden-chart validation
├── override_bulk_importer.py      # CSV / YAML batch import
└── override_cache.py              # Redis cache with namespace by org_id

src/josi/api/v1/controllers/
└── tenant_override_controller.py  # org-admin CRUD endpoints

web/app/(admin)/tenant/overrides/
├── page.tsx                       # list + filter
├── new/page.tsx                   # authoring with diff preview vs global
├── [override_id]/page.tsx         # detail, versions, shadow gate
└── components/
    ├── OverrideDiffViewer.tsx
    ├── OverrideAuthoringForm.tsx
    └── LineageCitationEditor.tsx
```

### 5.2 Data model additions

```sql
-- ============================================================
-- tenant_rule_override: per-tenant rule body replacement
-- ============================================================
CREATE TABLE tenant_rule_override (
    id                          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id             UUID NOT NULL REFERENCES organization(organization_id),
    rule_id                     TEXT NOT NULL,
    source_id                   TEXT NOT NULL REFERENCES source_authority(source_id),
    base_rule_version           TEXT NOT NULL,                -- which global version it overrides
    version                     TEXT NOT NULL,                -- semver of the override itself
    content_hash                CHAR(64) NOT NULL,
    override_rule_body          JSONB NOT NULL,
    override_citation           TEXT,                         -- e.g., "TNJM Commentary §4.2"
    tenant_display_name         TEXT,                         -- e.g., "Tamil Nadu Jyotish Mandali"
    override_reason             TEXT NOT NULL,                -- required free text
    active                      BOOLEAN NOT NULL DEFAULT false,
    effective_from              TIMESTAMPTZ,
    effective_to                TIMESTAMPTZ,
    created_at                  TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by                  UUID NOT NULL REFERENCES "user"(user_id),
    updated_at                  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_by                  UUID REFERENCES "user"(user_id),
    approved_at                 TIMESTAMPTZ,
    approved_by                 UUID REFERENCES "user"(user_id),
    UNIQUE (organization_id, rule_id, source_id, version),
    FOREIGN KEY (rule_id, source_id, base_rule_version)
        REFERENCES classical_rule(rule_id, source_id, version)
);

CREATE INDEX idx_override_active_lookup
    ON tenant_rule_override(organization_id, rule_id, source_id)
    WHERE active = true AND effective_to IS NULL;

CREATE INDEX idx_override_org_all
    ON tenant_rule_override(organization_id, created_at DESC);

-- ============================================================
-- technique_compute: add provenance columns
-- ============================================================
ALTER TABLE technique_compute
    ADD COLUMN rule_source_kind TEXT NOT NULL DEFAULT 'global'
        CHECK (rule_source_kind IN ('global','tenant_override')),
    ADD COLUMN tenant_rule_override_id UUID REFERENCES tenant_rule_override(id);

CREATE INDEX idx_compute_override
    ON technique_compute(tenant_rule_override_id, computed_at DESC)
    WHERE tenant_rule_override_id IS NOT NULL;

-- ============================================================
-- tenant_override_audit: immutable log of CRUD + approval events
-- ============================================================
CREATE TABLE tenant_override_audit (
    id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_rule_override_id UUID NOT NULL REFERENCES tenant_rule_override(id) ON DELETE CASCADE,
    event_type           TEXT NOT NULL CHECK (event_type IN
                           ('created','updated','activated','deactivated','deleted','approved','version_bumped')),
    actor_user_id        UUID REFERENCES "user"(user_id),
    payload              JSONB NOT NULL DEFAULT '{}'::jsonb,
    event_at             TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_override_audit ON tenant_override_audit(tenant_rule_override_id, event_at);
```

### 5.3 API contract

**REST (org-admin scope):**

```
POST /api/v1/tenant/overrides
Body:
  rule_id: string
  source_id: string
  base_rule_version: string
  override_rule_body: object        # F6 DSL JSON
  override_citation: string?
  tenant_display_name: string?
  override_reason: string            # required
Response:
  id, version, content_hash, status='draft'

GET /api/v1/tenant/overrides
Query: rule_id?, source_id?, active?
Response: list of overrides scoped to caller's org

GET /api/v1/tenant/overrides/{id}
Response: full override + history from tenant_override_audit

POST /api/v1/tenant/overrides/{id}/activate
Requires: caller has `tenant_rule_approver` role; override has passed shadow
Response: active=true, approved_at, approved_by

POST /api/v1/tenant/overrides/{id}/deactivate
Body: reason: string
Response: active=false; effective_to=now()

POST /api/v1/tenant/overrides/{id}/shadow-test
Body: chart_ids: list[UUID]?  (defaults to org's sampled 1%)
Response: diff summary vs global rule for each chart

POST /api/v1/tenant/overrides/bulk-import
Body: file with YAML list of overrides
Response: list of created override ids, list of errors

GET /api/v1/tenant/overrides/{id}/diff
Response: side-by-side diff of override body vs global rule body
```

**Internal Python interface:**

```python
# src/josi/services/overrides/override_resolver.py

class OverrideResolver:
    def __init__(self, cache: OverrideCache, repo: OverrideRepository): ...

    async def resolve(
        self,
        organization_id: UUID,
        rule_id: str,
        source_id: str,
    ) -> ResolvedRule:
        """Returns (rule_body, provenance) where provenance = global|tenant_override."""

# src/josi/services/overrides/override_validator.py

class OverrideValidator:
    async def validate(
        self,
        override: TenantRuleOverride,
        base_rule: ClassicalRule,
    ) -> ValidationResult:
        """Runs: (1) JSON Schema check against output_shape;
                 (2) F6 DSL parse check;
                 (3) golden-chart regression (org's curated chart set)."""
```

**Engine integration (existing `ClassicalEngine` from F2):**

```python
class ClassicalEngine(Protocol):
    async def compute_for_source(
        self,
        session: AsyncSession,
        chart_id: UUID,
        source_id: str,
        organization_id: UUID,                   # NEW: required for override resolution
        rule_ids: list[str] | None = None,
    ) -> list[TechniqueComputeRow]: ...
```

Every engine implementation calls `override_resolver.resolve(...)` before executing a rule. Output row carries `rule_source_kind` and `tenant_rule_override_id` when applicable.

### 5.4 AI citation layer hook

F11's citation shape (from P0) gains an optional `override` field. The chart_reading_view serving table (F9) gets a small denormalized column:

```sql
ALTER TABLE chart_reading_view
  ADD COLUMN active_override_count INTEGER NOT NULL DEFAULT 0,
  ADD COLUMN active_override_ids JSONB NOT NULL DEFAULT '[]'::jsonb;
```

This lets AI tool-use responses quickly identify which parts of a reading are under override, without re-joining at query time.

## 6. User Stories

### US-P4E4T.1: As a B2B org admin, I want to override Gaja Kesari to use my lineage's 3° orb
**Acceptance:** creating the override via `/api/v1/tenant/overrides`, running `shadow-test`, reviewing diff, and activating results in every new compute of Gaja Kesari for my org's charts producing the overridden result. Charts in other orgs remain unaffected.

### US-P4E4T.2: As the classical advisor for my org, I want to see what changed between my override and the global rule
**Acceptance:** `GET /api/v1/tenant/overrides/{id}/diff` returns side-by-side DSL diff; UI renders it with syntax highlighting.

### US-P4E4T.3: As a B2C end user, I never see another tenant's override
**Acceptance:** chart reading for an anonymous B2C user uses global rules; no override row from any tenant is resolvable in that query path.

### US-P4E4T.4: As a compliance officer, I want a full audit trail of who changed an override and when
**Acceptance:** `GET /api/v1/tenant/overrides/{id}` includes audit events; every state transition is logged with actor, timestamp, payload.

### US-P4E4T.5: As product, I want per-org metrics of active override count
**Acceptance:** billing pipeline reads `COUNT(*) FROM tenant_rule_override WHERE organization_id = ? AND active = true` daily; enterprise billing reflects usage.

### US-P4E4T.6: As AI chat, I want to cite the override explicitly in my response
**Acceptance:** when the LLM uses tool `get_yoga_summary` on a chart under an org with active overrides, the response metadata includes override_source fields; rendered text says "per [tenant] lineage …" when appropriate.

### US-P4E4T.7: As an org admin bulk-migrating from a legacy system, I want to upload 200 overrides at once
**Acceptance:** `POST /api/v1/tenant/overrides/bulk-import` with a YAML file creates 200 draft overrides; each flagged pass/fail on validation; bulk activation workflow covered by S8 shadow.

## 7. Tasks

### T-P4E4T.1: Alembic migration
- **Definition:** Generate migration for `tenant_rule_override`, `tenant_override_audit` tables, and `technique_compute` column additions + indexes. Respects per-CLAUDE.md autogenerate workflow.
- **Acceptance:** Applies cleanly on staging; downgrade reverts cleanly.
- **Effort:** 2 days
- **Depends on:** F2, F4

### T-P4E4T.2: OverrideRepository + CRUD endpoints
- **Definition:** BaseRepository subclass scoped by `organization_id`. REST controller with role gating (`tenant_rule_author` for create/update, `tenant_rule_approver` for activate). All writes emit `tenant_override_audit` rows.
- **Acceptance:** CRUD tests green; audit rows written on every state change; cross-tenant access blocked (attempt from org B to fetch org A's override returns 404).
- **Effort:** 1 week
- **Depends on:** T-P4E4T.1

### T-P4E4T.3: OverrideValidator
- **Definition:** Validates override_rule_body against F6 DSL parser; validates output against F5 JSON Schema for the base rule's output_shape; runs golden-chart regression if tenant has curated charts.
- **Acceptance:** Malformed DSL rejected with specific error messages; shape violations rejected; valid override passes.
- **Effort:** 1 week
- **Depends on:** F5, F6

### T-P4E4T.4: OverrideResolver with Redis cache
- **Definition:** Cache key `override:{org_id}:{rule_id}:{source_id}`; cache value the resolved rule body + content hash + override_id (if any) or sentinel for no-override. TTL 1 hour. Cache invalidation on CRUD.
- **Acceptance:** Cache hit rate > 95% in steady-state load test; invalidation correctness: edit override, next compute sees new body.
- **Effort:** 1 week
- **Depends on:** T-P4E4T.2

### T-P4E4T.5: Engine integration
- **Definition:** Update `ClassicalEngine` Protocol + all existing engines to call `override_resolver.resolve()`. Compute rows carry new provenance columns.
- **Acceptance:** Integration test: under org with active override, compute row has `rule_source_kind='tenant_override'` and correct `tenant_rule_override_id`; under org without override, `rule_source_kind='global'`.
- **Effort:** 1 week
- **Depends on:** T-P4E4T.4, F2

### T-P4E4T.6: Shadow-compute integration with S8
- **Definition:** `/api/v1/tenant/overrides/{id}/shadow-test` hooks into S8 promotion infrastructure scoped to the tenant. Uses a mini-promotion with `from_version=base_rule_version`, `to_version=<override_id synthetic>`.
- **Acceptance:** Shadow-test returns divergence summary within 10 minutes; auto-halt on unexpected divergence works exactly as for global rules.
- **Effort:** 1 week
- **Depends on:** T-P4E4T.3, S8

### T-P4E4T.7: Diff viewer endpoint + UI component
- **Definition:** `/diff` endpoint returns structured diff (field-level) between override body and global rule body. Web component renders side-by-side with syntax highlighting, respecting F6 DSL semantics (e.g., "change expression at $.conditions[2].value from X to Y").
- **Acceptance:** Manual review shows accurate diffs on 5 representative overrides.
- **Effort:** 1 week
- **Depends on:** T-P4E4T.2

### T-P4E4T.8: Admin UI for override authoring
- **Definition:** Next.js pages at `web/app/(admin)/tenant/overrides/`. List, create, edit (with DSL form + raw JSON tab), shadow-test, activate, deactivate, version history.
- **Acceptance:** Product walkthrough: org admin creates override, shadow-tests, activates; metrics reflect override live.
- **Effort:** 2 weeks
- **Depends on:** T-P4E4T.5, T-P4E4T.6, T-P4E4T.7

### T-P4E4T.9: Bulk importer
- **Definition:** `POST /bulk-import` accepts YAML file; creates draft overrides; validation summary returned. CLI `josi override import --org <id> --file <path>`.
- **Acceptance:** 200-row YAML with 10 invalid rows returns precise error map; 190 drafts created.
- **Effort:** 3 days
- **Depends on:** T-P4E4T.3

### T-P4E4T.10: AI citation layer integration
- **Definition:** Update F10 tool-use response models to include optional `override` citation field. Update chart_reading_view writer to populate `active_override_count` and `active_override_ids`. Update LLM prompt templates to surface override context.
- **Acceptance:** Chat integration test: for chart under active override, response shows override citation in tool response; rendered text mentions tenant lineage.
- **Effort:** 1 week
- **Depends on:** T-P4E4T.5, F10, F11

### T-P4E4T.11: Billing metering hook
- **Definition:** Daily job exports per-org active override count + audit event counts to billing pipeline.
- **Acceptance:** Enterprise tier usage dashboard reflects counts; metering verified against test orgs.
- **Effort:** 2 days
- **Depends on:** T-P4E4T.2

### T-P4E4T.12: Cross-tenant isolation test suite
- **Definition:** Explicit security tests attempting to access, modify, or activate other tenants' overrides via every endpoint.
- **Acceptance:** All attempts return 404 (not 403, to avoid enumeration); logged as potential intrusion attempts.
- **Effort:** 3 days
- **Depends on:** T-P4E4T.2

### T-P4E4T.13: Documentation + sample pack
- **Definition:** Docs page "How to build a lineage pack". Sample YAML bundle: TNJM-inspired overrides for 5 yogas as a reference.
- **Acceptance:** Docs merged; sample pack round-trips through bulk importer successfully.
- **Effort:** 3 days
- **Depends on:** T-P4E4T.9

## 8. Unit Tests

### 8.1 OverrideRepository

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_create_override_writes_audit` | create call | 1 override + 1 audit row (event_type='created') | audit guarantee |
| `test_unique_constraint_on_org_rule_source_version` | duplicate version | IntegrityError | version uniqueness |
| `test_base_rule_version_must_exist` | unknown base version | IntegrityError via composite FK | referential integrity |
| `test_list_scoped_to_org` | list from org A | rows only from org A | tenant isolation |
| `test_soft_deprecation_via_effective_to` | set effective_to=now | override no longer active | lifecycle |
| `test_deletion_cascades_audit` | delete override | audit rows cascade | cleanup |

### 8.2 OverrideValidator

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_malformed_dsl_rejected` | invalid F6 expression | ValidationError with line number | UX |
| `test_output_shape_violation_rejected` | override returns extra top-level key | ValidationError referencing JSON Schema | shape fidelity |
| `test_valid_override_passes` | well-formed override | passes all gates | happy path |
| `test_golden_chart_regression_failure` | override produces wrong result on golden chart | ValidationError with chart id | correctness gate |
| `test_content_hash_deterministic` | same body | same hash across invocations | F13 invariant |

### 8.3 OverrideResolver

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_resolve_returns_global_when_no_override` | org without override | global rule body | fallback path |
| `test_resolve_returns_override_when_active` | org with active override | override body | core path |
| `test_resolve_ignores_inactive_override` | override with active=false | global body | active gate |
| `test_resolve_ignores_expired_override` | effective_to in past | global body | temporal correctness |
| `test_cache_hit_second_call` | two resolves | second skips DB | perf |
| `test_cache_invalidated_on_activation` | activate override | next resolve returns new body | correctness over speed |
| `test_resolve_is_tenant_scoped` | org A's override, resolve for org B | B gets global | isolation |

### 8.4 Engine integration

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_compute_under_override_sets_provenance` | compute for org with override | `rule_source_kind='tenant_override'`, override_id set | provenance |
| `test_compute_without_override_sets_global` | org without override | `rule_source_kind='global'`, override_id null | baseline |
| `test_compute_idempotent_under_override` | run twice | one row | F2 invariant |
| `test_input_fingerprint_includes_override_hash` | two computes with different overrides | different fingerprints | F13 chain |

### 8.5 REST endpoints

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_create_requires_role` | caller without `tenant_rule_author` | 403 | authz |
| `test_activate_requires_approver_role` | author cannot self-activate | 403 | dual control |
| `test_activate_requires_shadow_pass` | no shadow run | 409 with 'shadow_required' | safety |
| `test_cross_tenant_fetch_returns_404` | org B reads org A's id | 404 | isolation |
| `test_bulk_import_partial_success` | 10 rows, 2 invalid | 8 created, 2 in error list | UX |
| `test_diff_endpoint_returns_structured_diff` | override differing in 2 fields | 2 field entries | diff correctness |

### 8.6 Security / isolation

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_override_never_leaks_to_b2c` | anon user compute | no override applied | B2C safety |
| `test_admin_of_parent_org_cannot_edit_child_org_override` | parent admin | 403 | scope |
| `test_api_key_without_org_context_fails` | missing org_id on request | 401 | auth path |

### 8.7 Shadow integration

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_shadow_test_creates_s8_promotion` | shadow-test call | mini-promotion created | S8 reuse |
| `test_activation_blocked_on_unresolved_shadow_diff` | shadow showed unexpected diffs | activate 409 | safety |

## 9. EPIC-Level Acceptance Criteria

- [ ] Alembic migration applies cleanly; technique_compute column additions work on 200B-row table via rolling deploy
- [ ] `tenant_rule_override` supports full lifecycle: draft → shadow-tested → approved → active → deactivated
- [ ] Override body validated against F5 output_shape and F6 DSL at write time; invalid rejected
- [ ] Resolution is compute-time with Redis cache; hit rate > 95% at steady state
- [ ] Every compute row under override carries `rule_source_kind='tenant_override'` and `tenant_rule_override_id`
- [ ] Tenant isolation verified: no cross-tenant access paths; security tests green
- [ ] AI tool-use responses include override citations when applicable
- [ ] Shadow-test via S8 works end-to-end
- [ ] Admin UI supports authoring, diff preview, shadow test, activation, bulk import
- [ ] Billing metering exports daily per-org override usage
- [ ] Sample lineage pack (TNJM-inspired) published
- [ ] Documentation merged; CLAUDE.md updated with "Tenant overrides — how rule resolution works at compute time"
- [ ] Unit test coverage ≥ 90% on new modules
- [ ] Golden-chart suite extended with per-tenant expected-result variants

## 10. Rollout Plan

- **Feature flag:** `TENANT_OVERRIDES_ENABLED` at infra level and `tenant_overrides` per-org capability flag.
  - `disabled` (global) — table exists but resolver returns global always
  - `enabled_shadow` (per-org) — resolver returns override but also shadow-computes global for diff analytics
  - `enabled_primary` (per-org) — resolver returns override
- **Shadow compute:** YES — every new override goes through S8 shadow before activation. A handful of pilot tenants enter `enabled_shadow` for 2 weeks before any tenant gets `enabled_primary`.
- **Backfill strategy:** historical compute rows retain `rule_source_kind='global'`; no retroactive relabeling. If a tenant wants historical recompute under new override, that is a tenant-initiated backfill via admin tool (separate from S8 rollback flow).
- **Rollback plan:**
  1. Disable resolver via flag — all resolution falls back to global; new computes revert to global rules within 1 cache TTL (1 h).
  2. Optionally recompute affected charts via F13 dependency graph (mass backfill).
  3. Table + audit preserved for forensics.
  4. Full Alembic downgrade is safe because `technique_compute` column additions are nullable/defaulted.

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Tenant writes override body that violates output_shape in a way validator missed | Medium | Medium | Defense in depth: runtime output validation; compute-time errors logged with override_id for fast diagnosis |
| Resolver cache hot-path becomes bottleneck | Low | High | L1 Redis cluster sized for P4; local process-level LRU as L0 cache |
| Org admin inadvertently publishes wrong override to production | Medium | High | Dual control: author + approver are different users; UI requires typing rule_id to confirm |
| Override body execution crashes rule engine | Low | High | Same DSL interpreter as global; golden-chart validation at activation time catches regressions |
| Explosion of overrides (20k tenants × 500 overrides) | Medium | Medium | Per-tenant soft cap 500; enterprise billing line aligns with count |
| AI chat leaks tenant A's override to tenant B's user | Low | Critical | Resolver tenant-scoped; integration tests verify; any cross-tenant ID surface audited |
| Shadow-compute via S8 slow for low-traffic tenant | Medium | Low | Tenant can supply explicit chart list for targeted shadow |
| Override references a rule_id that later gets deprecated globally | Low | Medium | Promotion tooling checks active overrides before deprecating a rule; auto-migration prompt |
| Storage growth from provenance columns exceeds forecasts | Low | Low | 20-byte addition × 200B rows = 4 TB; under 2% of total; monitored |
| Tenants with overrides experience divergent behavior from public docs | Medium | Medium | Override metadata surfaces in every AI response; public Josi docs note "if your org has overrides, your results may differ" |

## 12. References

- Master spec: [`docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`](../../../superpowers/specs/2026-04-19-classical-techniques-expansion-design.md)
- F1 dimensions: [`F1-star-schema-dimensions.md`](../P0/F1-star-schema-dimensions.md)
- F2 fact tables: [`F2-fact-tables.md`](../P0/F2-fact-tables.md)
- F4 temporal rule versioning: [`F4-temporal-rule-versioning.md`](../P0/F4-temporal-rule-versioning.md)
- F5 JSON Schema validation: [`F5-json-schema-validation.md`](../P0/F5-json-schema-validation.md)
- F6 rule DSL: [`F6-rule-dsl-yaml-loader.md`](../P0/F6-rule-dsl-yaml-loader.md)
- F13 content-hash provenance: [`F13-content-hash-provenance.md`](../P0/F13-content-hash-provenance.md)
- P3-E2-console: [`P3-E2-console-rule-authoring-console.md`](../P3/P3-E2-console-rule-authoring-console.md)
- S8 shadow-compute rule migrations: [`S8-shadow-compute-rule-migrations.md`](./S8-shadow-compute-rule-migrations.md)
- Enterprise tier product spec (P5 D9): [`D9-enterprise-tier.md`](../P5/D9-enterprise-tier.md)
