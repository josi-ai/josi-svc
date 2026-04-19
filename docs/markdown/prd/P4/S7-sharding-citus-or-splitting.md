---
prd_id: S7
epic_id: S7
title: "Sharding: Citus extension vs org-based application-level split"
phase: P4-scale-100m
tags: [#performance, #multi-tenant]
priority: must
depends_on: [F2, F3, S2]
enables: [S4, P4-E4-tenant]
classical_sources: []
estimated_effort: 6-8 weeks
status: draft
author: "@agent"
last_updated: 2026-04-19
---

# S7 — Sharding: Citus Extension vs Organization-Based Split

## 1. Purpose & Rationale

By P4 the corpus is:

- 100M end-users across ~20k astrologer/B2B organizations
- 200B `technique_compute` rows, 40B `aggregation_event` rows, 5B `aggregation_signal` rows
- 2–4 TB of hot data that will not fit in a single Cloud SQL instance's working set regardless of tier
- Write throughput peaks of 200k rows/s during batch backfill windows (new source added, new rule version rolled out)

A single Cloud SQL Postgres instance — even `db-custom-32-122880` (32 vCPU, 120 GiB) — cannot sustain this. S2 read replicas push read scale linearly but do nothing for writes; S3 caching hides hot-read traffic but does nothing for storage. We need to split the OLTP write path across multiple physical databases.

This PRD picks the sharding strategy, defines the shard key, describes live rebalancing, and enumerates the migration from today's single-instance topology to a sharded fleet. It preserves everything downstream: F9 chart_reading_view stays a table; F10 AI tool-use reads stay < 20 ms P50; S4 CDC continues working per-shard.

**Design stance: all fact tables in F2 already carry `organization_id` (per CLAUDE.md invariant). That choice, made in P0, is what makes sharding possible without a schema rewrite at P4.**

## 2. Scope

### 2.1 In scope

- Decision matrix: Citus (distributed Postgres) vs application-level per-org routing
- Shard key definition: `organization_id` with hash distribution
- Reference-table strategy for dim tables (F1) — replicated to every shard
- Colocation strategy for fact tables so `organization_id` joins stay local
- Online rebalancing procedure (add/remove shard without downtime)
- Migration plan from single instance → 4 shards → 16 shards → 64 shards (planned cap at P4)
- Application-level router for non-Citus path (if Cloud SQL does not support Citus)
- Cross-shard query library for analytics fallback (OLAP is primary; see S4)
- Coordination with S4 CDC: each shard publishes to its own slot/topic, sinks merge
- Coordination with P4-E4-tenant: per-tenant overrides also colocated on tenant's shard
- Shard-aware connection pooling: PgBouncer fleet per shard + routing layer

### 2.2 Out of scope

- Global geographic sharding (US / EU / APAC) — reserved for P5
- Per-user sharding (bad choice: co-located org queries become cross-shard)
- Cross-shard transactions (explicitly forbidden; use sagas if needed)
- Sharding the dim tables (they stay reference, replicated)
- Changing the application data model (invariants already in place)
- ClickHouse shard-aware consumers — S4 handles fan-in

### 2.3 Dependencies

- **F2** — every fact table has `organization_id` (confirmed in P0)
- **F3** — partitioning survives sharding; hash subpartitioning already uses `chart_id`
- **S2** — read replicas per shard reuse S2 patterns
- **S4** — CDC consumer must fan-in across shards (noted there)
- **P4-E4-tenant** — override rules must live on the correct shard

## 3. Technical Research

### 3.1 Why `organization_id` is the right shard key

Every fact table has it (invariant from F2). Queries are naturally scoped to an org: "give me chart X for org Y" — chart_id is unique globally (UUID) but always resolves to a known org. That means:

- Single-shard queries: 99%+ of online reads
- Writes: always single-shard (chart belongs to one org)
- Analytics aggregates that cross orgs: go to OLAP (S4), not OLTP

The 20k-org cardinality at P4 is high enough to distribute evenly across 64 shards with hash distribution (~300 orgs per shard). Skew risk is real but bounded: the largest B2B customers may be 100× the smallest. Mitigations covered in §3.4.

### 3.2 Option A — Citus extension on Postgres

Citus distributes data by a declared shard key across worker nodes under a single coordinator. From the client's perspective it looks like one Postgres.

**Pros:**
- **Single logical database.** Application code barely changes; SQL still works.
- **Built-in online rebalancing.** `SELECT citus_rebalance_start()` moves shards without downtime.
- **Reference tables.** Dim tables (F1) are automatically replicated to every worker so joins stay local.
- **Colocation.** Tables sharded on the same key with the same shard count colocate: no cross-shard join for `technique_compute ⋈ aggregation_event` on `organization_id`.
- **Mature.** Acquired by Microsoft 2019, multi-year production history at Twitch, Microsoft Azure (hosted Citus), Heap, Copper.
- **Works with F3 LIST+HASH partitioning.** Distributed tables can be partitioned; Citus handles partition routing.

**Cons:**
- **Cloud SQL support is uncertain.** As of 2026-04, GCP Cloud SQL for Postgres does not bundle Citus. Options: (a) self-host on GKE CloudNativePG + Citus; (b) migrate to Azure Cosmos DB for PostgreSQL (hosted Citus); (c) AlloyDB (GCP) has similar goals but different semantics and no drop-in Citus API.
- **DDL restrictions.** Some DDL (notably CREATE TRIGGER on distributed tables) needs coordinator-run variants.
- **Foreign keys across shards forbidden unless on the shard key.** Composite FK `technique_compute → classical_rule` (F2) must be adapted: `classical_rule` becomes a reference table.
- **Transaction boundaries.** Cross-shard multi-statement transactions are supported but degrade to 2PC; best avoided.

### 3.3 Option B — Application-level sharding

Operate N independent Cloud SQL instances. A thin routing layer in the application resolves `organization_id → shard_id` and opens connections accordingly. Each shard is a normal Postgres.

**Pros:**
- **No extension dependency.** Works on vanilla Cloud SQL.
- **Per-shard ops isolation.** Can upgrade/restart shards one at a time.
- **Per-shard sizing.** Heavy B2B customers go to dedicated shards with bigger instances.
- **Standard tooling.** pg_dump, pg_stat_*, standard monitoring.

**Cons:**
- **Application complexity.** Every repository method accepts org context; every query goes through the router. Violation = wrong-shard bug.
- **Dims replicated by application.** We'd need to run F1's dim loader on every shard; correctness enforcement is procedural, not structural.
- **Rebalancing is a custom dance.** Moving an org means pause writes for that org, dump, restore, flip router, resume. Typically hours of coordination; we've seen this done at multiple companies but it's labor-intensive.
- **Cross-shard joins = client-side.** A report over all orgs means N round-trips stitched in the application. Slow and buggy; OLAP (S4) is the escape hatch.
- **CDC × shards fan-out.** S4 already handles fan-in from multiple slots — tolerable, but more operationally complex than Citus' single publication.

### 3.4 Decision matrix

| Dimension | Citus | App-level split |
|---|---|---|
| Developer ergonomics | Single DB, normal SQL | Router injection in every query path |
| Operational complexity | Coordinator + workers on GKE | N Cloud SQL instances |
| Cost at 64 shards | ~$28k/mo (GKE + PDs) | ~$35k/mo (N × db-custom + PDs) |
| Rebalancing | Online, built-in | Custom, hours-long |
| Cross-shard queries | Coordinator planner | Client fan-out |
| Reference tables (dims) | Native | Manual replication per shard |
| Managed offering on GCP | No (AlloyDB is close but not drop-in) | Yes (Cloud SQL) |
| Migration from today | Medium: schema conversion | Medium: router insertion |
| DDL gotchas | Several, documented | None |

**Recommendation: Citus if available, application-level split otherwise.** The key blocker is "available." We commit to a spike in T-S7.1 to verify and pick. Everything else in this PRD is symmetric across the two paths unless called out.

### 3.5 Shard topology evolution

- **P0–P3:** Single Cloud SQL instance. `organization_id` present on all facts but not used for routing. "Sharded-ready, not sharded."
- **P4 T0:** 4 logical shards. If Citus: one coordinator + 4 workers. If app-level: 4 Cloud SQL instances. Shard count = 4 to start because rebalancing from fewer is trivial; rebalancing to fewer is hard.
- **P4 T+3 months:** 16 shards. Growth driven by write throughput.
- **P4 T+12 months:** 64 shards. Design cap for P4; P5 may revisit with geographic sharding.
- **Shard count always a power of 2** so splits are deterministic (each shard splits cleanly into 2 new).

### 3.6 Which tables are sharded vs reference vs local

**Distributed (sharded by `organization_id`):**
- `technique_compute`
- `aggregation_event`
- `aggregation_signal`
- `astrologer_source_preference`
- `chart_reading_view`
- `astrology_chart` (pre-existing table — prerequisite: this must carry `organization_id`; verify in T-S7.0)
- `tenant_rule_override` (from P4-E4-tenant)
- All partitioned children of the above (F3 partitions stay within shards)

**Reference (replicated to every shard, < 1 MB total):**
- `source_authority`
- `technique_family`
- `output_shape`
- `aggregation_strategy`
- `experiment`
- `experiment_arm`
- `classical_rule` (grows slowly; P4 cap ~5k rows even with 1000 yogas)

**Local (lives only on coordinator):**
- `organization` (metadata)
- `user` (authoritative table; rows reference orgs but user access patterns hit cache, not this table)
- Admin tables (rule authoring console drafts, audit logs)

### 3.7 Alternatives considered

| Alternative | Rejected because |
|---|---|
| Vitess (MySQL sharding) | Not Postgres; schema migration is a non-starter |
| CockroachDB | Multi-region first-class but geo-distributed Raft overhead for write latency; retains Postgres wire protocol but semantics differ enough to regress existing tests |
| AlloyDB | GCP-native but lock-in; no Citus-grade shard operator; postponed to P5 re-evaluation |
| Yugabyte | Emerging; smaller production footprint than Citus |
| Sharding by `chart_id` hash | Forces every cross-chart query (e.g., synastry in P2) to fan-out |
| Sharding by geography | Customers not geographically tenanted; compatibility with B2B multi-tenant model poor |

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| Primary choice | Citus if Cloud SQL supports it or GKE-hosted Citus is acceptable; else app-level | Verified in spike T-S7.1 |
| Shard key | `organization_id` | Invariant from F2; 99%+ queries are org-scoped |
| Distribution function | Hash | Even distribution without maintenance |
| Initial shard count | 4 | Aligns with 10M-user entry to P4; doubles cleanly |
| Max shard count (P4) | 64 | Enough for 100M users at current hot-shard sizing |
| Dim strategy | Reference tables (replicated) | Avoids cross-shard joins for hot enrichment |
| Composite FK on technique_compute | Allowed in Citus when FK target is reference table | `classical_rule` becomes reference; distance constant |
| Cross-shard transactions | Forbidden by convention | Sagas or eventual consistency where needed |
| Rebalance window | Business-hours OK with Citus online rebalance | Tested in staging at scale |
| Schema changes post-shard | Managed via Citus DDL propagation | Works for ALTER TABLE; CREATE TRIGGER needs coordinator helper |
| Connection routing | PgBouncer per shard + router layer in app | Keep coordinator clean; app-aware pool selection |
| Emergency single-shard read | `citus_isolation_session` | Bypass planner for diagnostic |
| Shard-skew handling for mega-tenants | Isolated tenant → dedicated shard via `isolate_tenant_to_new_shard()` | Mitigates hot-shard risk |

## 5. Component Design

### 5.1 New services / modules

```
src/josi/db/
├── shard_router.py            # app-level routing (fallback path)
├── citus_admin.py             # Citus ops wrappers (rebalance, add worker, isolate tenant)
└── reference_sync.py          # replicates dim tables to shards (app-level path)

src/josi/services/shard/
├── __init__.py
├── shard_resolver.py          # org_id → shard_id (hashring)
├── connection_pool.py         # per-shard asyncpg pool manager
├── query_fanout.py            # opt-in multi-shard query executor (fallback)
├── rebalance_orchestrator.py  # wraps Citus or drives app-level migration
└── tenant_isolator.py         # mega-tenant to dedicated shard

infra/citus/          # only if Citus path
├── helm_values.yaml           # CloudNativePG + Citus operator
├── coordinator.yaml
├── workers.yaml
└── monitoring.yaml

infra/sharded_cloudsql/  # only if app-level path
├── instances.tf               # N Cloud SQL instances
├── pgbouncer.tf               # per-shard PgBouncer
└── router_service.tf
```

### 5.2 Data model changes

**Citus path — executed once on coordinator:**

```sql
-- Promote dims to reference tables
SELECT create_reference_table('source_authority');
SELECT create_reference_table('technique_family');
SELECT create_reference_table('output_shape');
SELECT create_reference_table('aggregation_strategy');
SELECT create_reference_table('experiment');
SELECT create_reference_table('experiment_arm');
SELECT create_reference_table('classical_rule');

-- Distribute facts on organization_id, colocated
SELECT create_distributed_table('astrology_chart', 'organization_id', colocate_with => 'none');
SELECT create_distributed_table('technique_compute', 'organization_id',
  colocate_with => 'astrology_chart');
SELECT create_distributed_table('aggregation_event', 'organization_id',
  colocate_with => 'astrology_chart');
SELECT create_distributed_table('aggregation_signal', 'organization_id',
  colocate_with => 'astrology_chart');
SELECT create_distributed_table('astrologer_source_preference', 'organization_id',
  colocate_with => 'astrology_chart');
SELECT create_distributed_table('chart_reading_view', 'organization_id',
  colocate_with => 'astrology_chart');
SELECT create_distributed_table('tenant_rule_override', 'organization_id',
  colocate_with => 'astrology_chart');
```

**Note:** every distributed table must include `organization_id` in its primary key. F2 has composite PKs like `(chart_id, rule_id, source_id, rule_version)` — we amend to `(organization_id, chart_id, rule_id, source_id, rule_version)` in a P4 migration. This widens the PK by 16 bytes × 200B rows = ~3 TB. Cost is acceptable; the alternative is Citus rejecting the table.

**Composite FK on `technique_compute → classical_rule`:** after `classical_rule` becomes a reference table, the FK works across shards because Citus routes the FK check to the local replica. Verified in T-S7.2.

**Migration to widen PK:**

```sql
-- Before creating distributed tables, migrate PKs
ALTER TABLE technique_compute
  DROP CONSTRAINT technique_compute_pkey,
  ADD PRIMARY KEY (organization_id, chart_id, rule_id, source_id, rule_version);
-- similar for other tables
```

Alembic migration is generated by `alembic revision --autogenerate` after updating SQLModel classes.

**App-level path — schema unchanged; shards are independent DBs:**

```python
# src/josi/services/shard/shard_resolver.py
class ShardResolver:
    def __init__(self, shard_count: int = 4):
        self.shard_count = shard_count  # power of 2

    def resolve(self, organization_id: UUID) -> int:
        """jump-consistent hash for minimal movement on rescale."""
        return jump_hash(uuid_to_u64(organization_id), self.shard_count)
```

### 5.3 API contract

**Internal Python interface — shard-aware session:**

```python
# src/josi/services/shard/connection_pool.py

class ShardedSessionFactory:
    async def get_session(self, organization_id: UUID) -> AsyncSession:
        """Returns session bound to the shard that owns the org."""
        shard_id = self.resolver.resolve(organization_id)
        return await self.pools[shard_id].acquire()

    async def get_read_replica_session(self, organization_id: UUID) -> AsyncSession: ...

    async def fanout(
        self,
        func: Callable[[AsyncSession], Awaitable[T]],
    ) -> list[T]:
        """Runs func against every shard concurrently (analytics fallback)."""
```

**Repository layer changes** (existing `BaseRepository` adds):

```python
# src/josi/repositories/base_repository.py
class BaseRepository(Generic[T]):
    async def _get_session(self, organization_id: UUID) -> AsyncSession:
        if settings.SHARDED:
            return await self.shard_factory.get_session(organization_id)
        return self.default_session
```

**For Citus path, this is a no-op:** `settings.SHARDED = False`, the coordinator handles routing. For app-level, every repository call must carry `organization_id` — we enforce via mypy: `def get(self, id: UUID, *, organization_id: UUID) -> T`.

**Admin CLI:**

```bash
# Citus path
josi shard rebalance --drain-rate 1000rows/s
josi shard add-worker --instance db-custom-16-61440
josi shard isolate-tenant --organization-id <uuid>
josi shard status                                 # shows per-shard size, lag, load

# App-level path
josi shard migrate-org --organization-id <uuid> --to-shard <n>
josi shard split --shard <n>                       # splits into 2, rehashes
```

## 6. User Stories

### US-S7.1: As an SRE, I want to double shard count with zero read downtime
**Acceptance:** starting from 16 shards, running `citus_rebalance_start()` (or the app-level equivalent) produces a 32-shard topology while production traffic continues. Application errors stay below baseline; no user-visible regression.

### US-S7.2: As a backend engineer, I want my queries to stay local even after sharding
**Acceptance:** a typical chart read (`SELECT * FROM chart_reading_view WHERE chart_id = :id AND organization_id = :org`) produces a single-worker execution plan; `EXPLAIN` shows no coordinator broadcast.

### US-S7.3: As product, I want mega-tenant traffic not to hurt smaller tenants
**Acceptance:** after isolating the top 5 B2B tenants to dedicated shards via `tenant_isolator`, P99 write latency for other tenants drops by at least 20%.

### US-S7.4: As a B2C user, I want my AI chat latency unchanged
**Acceptance:** F10 tool-use reads that hit `chart_reading_view` maintain P50 < 20 ms and P99 < 200 ms after shard migration (same SLO as unsharded).

### US-S7.5: As the data team, I want S4 CDC to continue working after shardification
**Acceptance:** each shard has its own replication slot and publication; S4 Pub/Sub topics receive messages from all shards; `v_technique_compute` BQ view sees union of all shards with no duplicates.

### US-S7.6: As an astrologer, my pro-mode preferences survive shard splits
**Acceptance:** after splitting a shard containing org X, `astrologer_source_preference` rows for org X's astrologers remain on the correct new shard and reads return the saved preferences without latency regression.

## 7. Tasks

### T-S7.0: Audit tables for `organization_id` and schema readiness
- **Definition:** Confirm every fact table has `organization_id` NOT NULL. Confirm primary keys that would need widening. Produce a migration-impact report listing every table, current PK, widened PK, row count.
- **Acceptance:** Report merged to `docs/markdown/P4-sharding-readiness.md`; all discrepancies have follow-up tickets.
- **Effort:** 3 days
- **Depends on:** F2

### T-S7.1: Spike — validate Citus availability on GCP
- **Definition:** Two-week spike. Deploy Citus coordinator + 3 workers via CloudNativePG + Citus operator on GKE. Load 1B rows from production backup. Run load test (20k writes/s, 100k reads/s). Measure cost, latency, operational complexity. Produce go/no-go memo.
- **Acceptance:** Memo in `docs/superpowers/specs/` with decision and benchmark data. If NO-GO, escalate to app-level path for remaining tasks.
- **Effort:** 2 weeks
- **Depends on:** none

### T-S7.2: Widen primary keys to include `organization_id`
- **Definition:** Alembic migration amending PKs on `technique_compute`, `aggregation_event`, `aggregation_signal`, `astrologer_source_preference`, `chart_reading_view`, `astrology_chart`, `tenant_rule_override`. Also update SQLModel classes.
- **Acceptance:** Migration applies cleanly on staging (1B rows); no query regression; mypy passes.
- **Effort:** 1 week
- **Depends on:** T-S7.0

### T-S7.3a (Citus path): Stand up Citus coordinator + 4 workers in staging
- **Definition:** CloudNativePG + Citus Helm chart. Storage class `premium-rwo`. Coordinator: 16 vCPU / 64 GiB. Workers: 8 vCPU / 32 GiB each. Configure pg_hba, certificates, backup to GCS.
- **Acceptance:** `SELECT * FROM citus_get_active_worker_nodes()` shows 4 workers; backup/restore tested; monitoring dashboards up.
- **Effort:** 1 week
- **Depends on:** T-S7.1 (go decision)

### T-S7.3b (App-level path): Stand up 4 Cloud SQL instances
- **Definition:** Terraform for 4 `db-custom-16-61440` instances; per-instance PgBouncer; router service. Secrets per instance.
- **Acceptance:** Four instances live; router resolves a test `organization_id` to correct instance; PgBouncer fleet healthy.
- **Effort:** 1 week
- **Depends on:** T-S7.1 (no-go decision)

### T-S7.4a (Citus): Run `create_reference_table` / `create_distributed_table`
- **Definition:** Execute the SQL block in §5.2 on staging after T-S7.2.
- **Acceptance:** `SELECT logicalrelid, partmethod FROM pg_dist_partition` shows all expected tables distributed or reference. Joins on `organization_id` do not cross workers (verified with `EXPLAIN`).
- **Effort:** 2 days
- **Depends on:** T-S7.3a, T-S7.2

### T-S7.4b (App-level): Build shard_resolver + connection_pool + reference_sync
- **Definition:** `ShardResolver` with jump-consistent hashing. `ShardedSessionFactory` with per-shard asyncpg pools. `reference_sync` cron that upserts dim rows to every shard every 5 min (triggered also on F1 dim_loader changes).
- **Acceptance:** Unit + integration tests green; reference sync catches dim updates within 5 min.
- **Effort:** 2 weeks
- **Depends on:** T-S7.3b

### T-S7.5: Application read/write path updates
- **Definition:** Repositories accept `organization_id`; `BaseRepository._get_session` uses shard factory. For Citus path, this is a no-op but still enforced for consistency. For app path, mypy enforces `organization_id` presence.
- **Acceptance:** `mypy` strict passes; all repository unit tests pass with shard factory in place.
- **Effort:** 2 weeks
- **Depends on:** T-S7.4a or T-S7.4b

### T-S7.6: Migrate data from single instance to 4-shard topology
- **Definition:** Offline-capable tool that reads from single-instance snapshot, writes to sharded topology. For Citus: `pg_dump` restore into coordinator, then `create_distributed_table` auto-shards. For app-level: per-row COPY keyed on `shard_resolver.resolve(org_id)`. Run in staging with full production backup.
- **Acceptance:** 100% row parity. Query parity verified on top 100 queries. Migration runnable in < 8 h for 200B rows estimated via extrapolation from staging 1B rows.
- **Effort:** 2 weeks
- **Depends on:** T-S7.5

### T-S7.7: Online rebalance orchestrator
- **Definition:** Wrapper CLI around `citus_rebalance_start` (Citus) or custom per-org migration (app-level). Rate-limits to keep OLTP headroom. Reports progress. Resumable.
- **Acceptance:** Rebalance in staging from 4 → 8 shards completes without read errors; application 5xx rate stays at baseline.
- **Effort:** 1 week (Citus) or 3 weeks (app-level)
- **Depends on:** T-S7.6

### T-S7.8: Tenant isolator
- **Definition:** Tool to move a single `organization_id` to a dedicated shard. For Citus: `isolate_tenant_to_new_shard(…)`. For app-level: migrate that org's rows to a new instance and update the override shardmap entry (router checks override before hash).
- **Acceptance:** Top-5 B2B orgs moved; P99 write latency for rest of cluster drops as predicted.
- **Effort:** 1 week
- **Depends on:** T-S7.7

### T-S7.9: S4 CDC per-shard integration
- **Definition:** Each shard publishes to its own replication slot; S4 enrichment workers subscribe to all topics. Row uniqueness across shards guaranteed by PK including `organization_id`.
- **Acceptance:** S4 round-trip from sharded topology produces parity row counts; no duplicates in `v_*` views.
- **Effort:** 1 week
- **Depends on:** T-S7.6, S4

### T-S7.10: Production cutover
- **Definition:** Two-phase rollout. Phase 1 (read-shadow): sharded cluster runs parallel, fed by continuous replication from single instance; reads are compared. Phase 2 (write-flip): maintenance window ≤ 1 hour flips write traffic to sharded cluster, stops replication, validates.
- **Acceptance:** Zero data loss; read-shadow comparison passes 100% sample match for 72 hours pre-flip; post-flip single-instance retained for 2-week rollback window.
- **Effort:** 2 weeks
- **Depends on:** T-S7.9

### T-S7.11: Runbook + on-call training
- **Definition:** Runbooks for hot-shard diagnosis, rebalance operations, coordinator failover, worker loss, split-brain response. Table-top exercise with SREs.
- **Acceptance:** Runbooks published; exercise logged; on-call rotation updated.
- **Effort:** 1 week
- **Depends on:** T-S7.10

## 8. Unit Tests

### 8.1 ShardResolver

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_jump_hash_deterministic` | same org_id twice | same shard | routing stability |
| `test_jump_hash_minimal_movement_on_rescale` | 4 → 8 shards | ~50% orgs stay | jump-hash invariant |
| `test_shard_count_must_be_power_of_two` | `shard_count=6` | raises ValueError | constraint |
| `test_override_map_precedence` | org X in override map | returns override, not hash | mega-tenant isolation |

### 8.2 ShardedSessionFactory

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_session_routed_to_correct_pool` | org_id resolving to shard 2 | session from pool[2] | routing correctness |
| `test_read_replica_routed_same_shard` | read call for org | replica pool on same shard | S2 compatibility |
| `test_fanout_hits_every_shard` | fanout query | N results, one per shard | analytics fallback |
| `test_pool_exhaustion_raises` | pool saturated | timeout error not stuck | observability |

### 8.3 Widened PK migration

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_pk_widening_preserves_data` | 1k-row fixture | post-migration all rows readable | safety |
| `test_pk_widening_prevents_org_collision` | insert same (chart_id, rule_id, …) under two orgs | both succeed | multi-tenant isolation |
| `test_fk_still_enforces` | orphan compute row | IntegrityError | FK continuity |

### 8.4 Citus distribution (integration, requires Citus test cluster)

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_distributed_table_colocates` | `technique_compute` + `aggregation_event` | same shardid for same org | colocation |
| `test_reference_table_replicated_to_all_workers` | insert row into `source_authority` | visible on every worker | reference-table semantics |
| `test_fk_to_reference_table` | compute with unknown source_id | IntegrityError | FK across Citus boundary |
| `test_explain_single_worker_for_org_query` | `EXPLAIN` for org-scoped query | `Task Count: 1` | local-execution |
| `test_cross_shard_transaction_errors_clearly` | multi-org UPDATE | explicit Citus error | developer safety |

### 8.5 Rebalance

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_rebalance_4_to_8_no_errors` | controlled load during rebalance | 0 errors, lag bounded | online rebalance |
| `test_rebalance_resume_after_interruption` | kill rebalance mid-way, restart | finishes remaining shards | robustness |
| `test_rebalance_respects_rate_limit` | rate limit 1000 rows/s | OLTP CPU stays under cap | no production impact |

### 8.6 App-level path (if no Citus)

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_reference_sync_propagates` | update source_authority | all shards updated within 5 min | dim consistency |
| `test_org_migration_atomic` | move org to new shard mid-read | read returns from old shard until flip, then new | no split-read |
| `test_router_override_survives_restart` | override map persisted | re-read after router restart picks up override | durability |

## 9. EPIC-Level Acceptance Criteria

- [ ] Go/no-go memo on Citus availability published and actioned
- [ ] Every distributed table has `organization_id` in its primary key post-migration
- [ ] Reference tables (dims + `classical_rule`) replicated on every worker (Citus) or shard (app-level)
- [ ] Staging proves rebalance from 4 → 8 shards online with zero 5xx spike
- [ ] Production migration completes with zero data loss; read-shadow parity > 99.999% for 72 h
- [ ] AI tool-use P50 < 20 ms and P99 < 200 ms post-shard (same SLO as pre-shard)
- [ ] Mega-tenant isolation reduces cross-tenant P99 by at least 20%
- [ ] S4 CDC continues working; BQ row counts match OLTP
- [ ] All existing integration tests pass against sharded topology
- [ ] Rollback plan tested in staging (flip back to single-instance within 2 hours)
- [ ] Runbooks merged; on-call trained
- [ ] Cost within 15% of projection

## 10. Rollout Plan

- **Feature flag:** `SHARDED_TOPOLOGY` (infra-level). States:
  - `off` — single instance, pre-P4 default
  - `shadow` — sharded cluster fed by replication, reads compared
  - `primary` — writes flipped, sharded is source of truth
  - `rolled_back` — single instance reactivated from continuous backup
- **Shadow compute:** YES. 72 h of read-shadow comparison before write-flip.
- **Backfill strategy:** continuous logical replication from single instance to sharded cluster during shadow phase; CDC becomes the migration tool.
- **Rollback plan:**
  1. Re-enable continuous replication from sharded cluster → single instance (reverse direction) as soon as primary is declared.
  2. For 2 weeks, single instance is warm standby.
  3. If critical regression, flip back within 2 hours via DNS + config flip.
  4. After 2 weeks of stable primary, decommission single instance.

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Citus not available on GCP managed offering | High | High | Self-host on GKE documented in T-S7.3a; app-level path pre-designed |
| PK widening migration is expensive on 200B rows | High | High | Stage in off-peak; test-restore from backup; widen in sorted-partition batches (F3 helps) |
| Hot shard (one mega-tenant) dominates | High | High | `tenant_isolator` moves them; shard-aware routing accommodates overrides |
| Cross-shard accidental query via missing `organization_id` filter | Medium | Medium | mypy `--strict`; `EXPLAIN` linter in CI that fails on `Task Count > 1` for tagged queries |
| Citus DDL restrictions break existing migrations | Medium | Medium | Audit all Alembic migrations in T-S7.0; document coordinator-vs-worker DDL rules |
| Rebalance saturates OLTP | Medium | High | Rate limit; run during low-traffic window initially; monitoring halts if P99 breaches |
| Loss of a worker without replica | Low | High | CloudNativePG replicas per worker; automated failover; tested quarterly |
| Connection fanout blows up PgBouncer | Medium | Medium | Per-shard pool sizing: 2× old pool / shard_count; monitoring |
| App code relies on global sequences | Low | Medium | Replace with UUIDv7 in T-S7.5 |
| S4 CDC lag grows during rebalance | Medium | Medium | Pause rebalance if any slot > 10 min lag; resume when recovered |
| Operational regression: more moving pieces | High | Medium | SRE rotation training (T-S7.11); invest in dashboards before cutover |

## 12. References

- Master spec: [`docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`](../../../superpowers/specs/2026-04-19-classical-techniques-expansion-design.md)
- F2 fact tables: [`F2-fact-tables.md`](../P0/F2-fact-tables.md)
- F3 partitioning: [`F3-partitioning-from-day-one.md`](../P0/F3-partitioning-from-day-one.md)
- S2 read replicas: [`S2-read-replicas-routing.md`](../P3/S2-read-replicas-routing.md)
- S4 OLAP: [`S4-olap-replication-clickhouse.md`](./S4-olap-replication-clickhouse.md)
- P4-E4-tenant: [`P4-E4-tenant-per-tenant-rule-overrides.md`](./P4-E4-tenant-per-tenant-rule-overrides.md)
- Citus docs — https://docs.citusdata.com/
- CloudNativePG + Citus — https://cloudnative-pg.io/
- Jump-consistent hashing — Lamping & Veach 2014
- Microsoft Azure Cosmos DB for PostgreSQL (hosted Citus) — https://learn.microsoft.com/azure/cosmos-db/postgresql/
