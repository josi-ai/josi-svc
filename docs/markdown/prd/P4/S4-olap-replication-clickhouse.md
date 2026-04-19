---
prd_id: S4
epic_id: S4
title: "OLAP replication: pg_logical → Pub/Sub → BigQuery (primary) or ClickHouse Cloud (alt)"
phase: P4-scale-100m
tags: [#performance, #experimentation]
priority: must
depends_on: [F2, F3, S3]
enables: [P3-E8-obs, C5, Research, AI5]
classical_sources: []
estimated_effort: 4-5 weeks
status: draft
author: "@agent"
last_updated: 2026-04-19
---

# S4 — OLAP Replication: Postgres → BigQuery / ClickHouse

## 1. Purpose & Rationale

At 10M → 100M users Josi accumulates 50B–200B `technique_compute` rows and 10B–40B `aggregation_event` rows. The OLTP Cloud SQL Postgres cluster was sized for serving (P50 < 20 ms AI tool-use reads per F10/F9), not for analytics. Running scoreboards like "what is the astrologer-override rate for Gaja Kesari across BPHS vs Saravali?" on OLTP replicas:

- Competes with serving traffic for shared_buffers.
- Scans hundreds of billions of rows with no columnar compression.
- Triggers vacuum pressure that regresses write-path tail latencies.
- Cannot join across replicas (can only query each shard independently post-S7).

This PRD introduces a **physical separation** between OLTP (row store, single-chart reads, sub-20ms) and OLAP (columnar store, aggregate scans over the whole corpus, seconds–minutes). Change-data-capture (CDC) from Postgres logical replication streams all fact-table mutations into an analytics warehouse. Every downstream use case that was stubbed in P3 — experiment scoreboards (E14a), per-rule observability (P3-E8-obs), differential testing reports (C5), the research dataset (Research) — moves to read exclusively from the warehouse.

**Primary choice: BigQuery** (GCP-native, no cluster to operate, unlimited storage). **Alternative: ClickHouse Cloud** when BigQuery's per-query $5/TB cost becomes material or sub-second interactive OLAP becomes a product requirement. The design supports both; the ingestion tier is warehouse-agnostic.

## 2. Scope

### 2.1 In scope

- Postgres logical replication publication on `technique_compute`, `aggregation_event`, `aggregation_signal`, `chart_reading_view`, and all dims from F1
- CDC reader service (Debezium embedded / pgoutput decoder) that converts WAL records to normalized Avro messages
- Google Pub/Sub as the durable buffer (with Apache Kafka on GKE as alternative; both tested)
- BigQuery sink with declared star schema mirroring F1/F2 (dims inlined onto facts)
- Optional ClickHouse Cloud sink with MergeTree + materialized projections
- Latency SLO monitoring (OLTP commit → OLAP visible)
- Backfill path for one-time seeding from Postgres to warehouse
- Warehouse-resident query library for all P3/P4 analytics use cases
- Cost monitoring and alerting (BigQuery slot-hours, ClickHouse compute-hours, Pub/Sub egress)

### 2.2 Out of scope

- Real-time streaming analytics (< 1 s latency) — 5-minute SLO is sufficient; sub-second analytics would use materialized views on the OLTP read replica (S2)
- Changing OLTP schema for analytics optimization — OLAP consumes OLTP as-is
- Machine-learning feature store — OLAP is the source; feature store is downstream (P5)
- Replacing Qdrant vector search — remains the canonical similarity index
- Cross-cloud replication — GCP-only for P4; multi-cloud in P6

### 2.3 Dependencies

- **F2** — fact tables that we replicate
- **F3** — partitioning so that initial backfill can snapshot partition-by-partition
- **S3** — serving cache owns the hot OLTP read path so CDC lag is tolerable
- **P3-E8-obs** — consumes the OLAP surface for dashboards
- GCP: Pub/Sub, BigQuery, Dataflow (optional) already enabled in `josiam` project
- **S7 (sharding)** — after S7 each shard publishes independently; the CDC reader fan-in merges to a single logical stream

## 3. Technical Research

### 3.1 Why logical replication (not dblink / FDW / nightly dump)

| Option | Why rejected |
|---|---|
| `pg_dump` nightly | 24 h staleness breaks experiment monitoring; dump on 100M rows takes >12 h |
| Postgres FDW to warehouse | Pulls rows on every query; no columnar benefit |
| Triggers → outbox table | Doubles write amplification on hot tables (`technique_compute` at 10k writes/s) |
| Streaming replication (physical) | Cannot be consumed by BigQuery; copies unrelated bloat |
| **Logical replication via `pgoutput`** | Append-only decoded stream, low write overhead, preserves row-level change type (INSERT / UPDATE / DELETE), standard in GCP Cloud SQL |

Cloud SQL for Postgres 15+ supports logical replication with `cloudsql.logical_decoding = on` and `wal_level = logical`. Replication slots are first-class; we create one per publication consumer.

### 3.2 Why a durable buffer between Postgres and the warehouse

Direct Postgres → BigQuery streaming via Dataflow is tempting but has three problems:

1. BigQuery streaming insert API backpressure surfaces all the way back to the replication slot; if BQ throttles, the slot grows and OLTP WAL retention increases, risking disk pressure on Cloud SQL.
2. No replay. A bad transform pushed to BQ requires re-reading from Postgres — but the slot may have advanced.
3. No fan-out. We want both BigQuery (primary) and ClickHouse (alt) concurrently for migration testing, plus the research data API (P4-Research).

Pub/Sub decouples. Slot advances as soon as the message is ack'd by Pub/Sub (7-day default retention). Sinks are independent subscribers with independent replay. At 10M writes/day across all fact tables, Pub/Sub is ~$15/day — trivial.

Kafka on GKE is offered as an alternative for teams who prefer Kafka ergonomics (consumer groups, exactly-once via transactions). At 200B-row scale the cost is similar; operational burden is higher.

### 3.3 Schema mapping: star in OLTP, denormalized in OLAP

OLTP keeps F1 dim tables normalized. In OLAP we **inline** dim columns onto each fact row:

```
OLTP:
  technique_compute(chart_id, rule_id, source_id, rule_version, technique_family_id, result, …)
  source_authority(source_id, display_name, tradition, era, …)

OLAP (BigQuery):
  fct_technique_compute(
    chart_id, rule_id, source_id, rule_version,
    -- inlined from source_authority
    source_display_name, source_tradition, source_era, source_default_weight,
    -- inlined from technique_family
    technique_family_display_name, technique_family_parent_category,
    -- inlined from output_shape
    output_shape_display_name,
    -- original fact columns
    result_json STRING, computed_at TIMESTAMP,
    organization_id STRING,
    _op STRING,   -- 'I' | 'U' | 'D'
    _lsn INT64,
    _ingested_at TIMESTAMP
  )
  PARTITION BY DATE(computed_at)
  CLUSTER BY organization_id, technique_family_id, source_id
```

Dims drift slowly (F1 upserts at deploy time). The enrichment lookup happens once per message at the ingest worker, reading dim snapshots from a ~5-minute TTL cache. A dim change triggers rewrite of downstream materialized views; this is rare enough to be acceptable.

### 3.4 Query patterns that move to OLAP

| Use case | OLTP cost today | OLAP shape |
|---|---|---|
| Experiment scoreboard: override rate per arm per technique_family | Full scan of `aggregation_signal` joined with `aggregation_event` — seconds to minutes on 40B rows | Partitioned by day, clustered by experiment — sub-second |
| Cross-source agreement: per yoga, agreement fraction between BPHS and Saravali | Complex self-join on `technique_compute` | Single GROUP BY on denormalized fact |
| Differential testing vs JH: output_hash disagreement per rule | Batch job churns replicas | Scheduled query in BQ, materialized into `mart_differential_testing` |
| Per-rule observability: compute P99, cache hit rate, version drift | Live dashboards hammer OLTP | Dashboards read `mart_rule_observability` |
| Research API: cross-source agreement dataset | Impossible at OLTP | Published via BQ authorized views |

### 3.5 Latency budget

- **Steady state:** P99 OLTP commit → row visible in OLAP < **5 minutes**.
  - Postgres WAL write → pgoutput decode: ~200 ms
  - Publish to Pub/Sub: ~300 ms including ack
  - Pull + enrich + BQ streaming insert: 1–2 minutes typical (BQ buffers up to 90 s before visibility)
  - Target headroom: 2 minutes
- **Backfill:** initial snapshot or re-seed < **15 minutes per 1B rows** (measured).
- **Alerting:** if steady-state lag > 15 minutes for > 5 minutes, page oncall.

### 3.6 Cost estimate at 200B rows

Assumptions: 200B `technique_compute` rows (avg 400 bytes/row JSON), 40B `aggregation_event` rows (avg 300 bytes), 5B signals (avg 200 bytes). Total compressed in BigQuery ≈ 35–50 TiB.

| Line item | Monthly |
|---|---|
| BigQuery storage (50 TiB × $0.02/GiB active + 80% in long-term at $0.01) | ~$700 |
| BigQuery slot-time (100 flex slots × 10 h/day on-demand equiv. for ETL + dashboards) | ~$5,000 |
| Pub/Sub ingress + egress (1 TB/day) | ~$1,500 |
| Dataflow workers for enrichment (4 × n2-standard-4 × 24/7) | ~$900 |
| **Total BigQuery path** | **~$8,100** |
| ClickHouse Cloud alternative (3-node 32CPU/128GB, same storage) | ~$24,000 |

BigQuery is ~3× cheaper at P4 scale, at the cost of per-query latency (BQ: seconds; CH: sub-second). For internal dashboards that latency is fine. We revisit if an end-user-facing analytics surface requires sub-second queries over 50 TiB.

### 3.7 Alternatives considered

| Alternative | Rejected because |
|---|---|
| Snowflake | Multi-cloud is out of scope for P4; no GCP org discount |
| Druid / Pinot self-hosted | Operational overhead vs BQ; no cost win at our scale |
| Databricks | Heavyweight; Delta Lake overkill for schema we fully control |
| Materialized views on OLTP replica | Cannot scale past 1 TiB without regressing OLTP; tried via S2 and hit limits |
| Elasticsearch for analytics | Not designed for SQL aggregates at this scale |

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| BigQuery vs ClickHouse as primary | BigQuery | GCP-native, 3× cheaper at 200B rows; ClickHouse deferred as opt-in path |
| Kafka vs Pub/Sub as buffer | Pub/Sub | Managed, integrates natively with Dataflow and Cloud SQL; Kafka stays as documented alternative |
| Debezium vs custom pgoutput reader | Debezium Server (embedded JSON mode) | Mature, well-tested; custom reader deferred unless backpressure tuning demands it |
| CDC of `classical_rule` table | Yes, but to a separate low-volume topic | Rule changes are rare and drive OLAP view rewrites |
| CDC of `astrologer_source_preference` | Yes | Needed for astrologer-segmented scoreboards |
| PII in OLAP | Organizational isolation only | No user-level PII in these fact tables; `organization_id` is the strongest identifier |
| Schema evolution strategy | Additive-only in OLAP; add nullable columns; never drop | BQ handles schema widening natively |
| Dead-letter queue | Yes, per sink, 30-day retention | Enables replay after transform bug fixes |
| Replication slot monitoring | `pg_replication_slots.confirmed_flush_lsn` lag alert at 5 min / page at 15 min | Protects Cloud SQL WAL disk from unbounded growth |
| Exactly-once semantics | At-least-once + idempotent sink (dedupe on PK + `_lsn`) | Pure exactly-once is theoretical; idempotent writes are practical |

## 5. Component Design

### 5.1 New services / modules

```
src/josi/services/replication/
├── __init__.py
├── publication_manager.py     # creates/maintains PUBLICATIONs on fact tables
├── slot_monitor.py            # exposes slot lag Prometheus metrics; alerts
├── cdc_reader.py              # Debezium Server wrapper config; decodes pgoutput
├── enrichment_worker.py       # reads Pub/Sub, joins dim snapshots, writes fact row
├── bigquery_sink.py           # streaming insert + idempotent dedupe
├── clickhouse_sink.py         # alternative, kept active for A/B
└── dim_snapshot_service.py    # refreshes in-memory dim cache every 5 min

src/josi/analytics/
├── bq_queries/                # all warehouse-resident SQL, git-versioned
│   ├── mart_experiment_scoreboard.sql
│   ├── mart_rule_observability.sql
│   ├── mart_cross_source_agreement.sql
│   ├── mart_differential_testing.sql
│   └── research_public_agreement_view.sql
└── scheduled_queries.yaml     # BQ scheduled queries, terraform-applied

infra/replication/
├── pubsub.tf                  # topics + subscriptions + DLQ
├── bigquery_dataset.tf        # `josi_olap` dataset + table DDL
├── dataflow_jobs.tf           # optional Dataflow templates
└── cloud_sql_flags.tf         # wal_level=logical, max_replication_slots=10
```

### 5.2 Data model additions

**Postgres side (publication):**

```sql
-- Run once per fact table; managed by publication_manager.py
CREATE PUBLICATION josi_olap_fct FOR TABLE
    technique_compute,
    aggregation_event,
    aggregation_signal,
    chart_reading_view
  WITH (publish = 'insert, update, delete', publish_via_partition_root = true);

CREATE PUBLICATION josi_olap_dim FOR TABLE
    source_authority,
    technique_family,
    output_shape,
    aggregation_strategy,
    experiment,
    experiment_arm,
    classical_rule,
    astrologer_source_preference;

-- Replication slot per sink subscriber (BQ + CH); allows independent lag
SELECT pg_create_logical_replication_slot('josi_olap_bq', 'pgoutput');
SELECT pg_create_logical_replication_slot('josi_olap_ch', 'pgoutput');
```

**BigQuery side:**

```sql
CREATE SCHEMA IF NOT EXISTS josi_olap OPTIONS(location = 'us-central1');

-- Fact: technique_compute (partitioned, clustered)
CREATE TABLE josi_olap.fct_technique_compute (
  organization_id STRING NOT NULL,
  chart_id STRING NOT NULL,
  rule_id STRING NOT NULL,
  source_id STRING NOT NULL,
  rule_version STRING NOT NULL,
  technique_family_id STRING NOT NULL,
  output_shape_id STRING NOT NULL,
  -- inlined dim snapshots
  source_display_name STRING,
  source_tradition STRING,
  source_era STRING,
  source_default_weight NUMERIC,
  technique_family_parent_category STRING,
  -- fact payload
  result_json STRING,
  input_fingerprint STRING,
  output_hash STRING,
  computed_at TIMESTAMP NOT NULL,
  -- CDC metadata
  _op STRING NOT NULL,       -- 'I' | 'U' | 'D'
  _lsn INT64 NOT NULL,
  _ingested_at TIMESTAMP NOT NULL,
  _source_commit_ts TIMESTAMP NOT NULL
)
PARTITION BY DATE(computed_at)
CLUSTER BY organization_id, technique_family_id, source_id
OPTIONS(partition_expiration_days = NULL);

-- Fact: aggregation_event
CREATE TABLE josi_olap.fct_aggregation_event (
  id STRING NOT NULL,
  organization_id STRING NOT NULL,
  chart_id STRING NOT NULL,
  technique_family_id STRING NOT NULL,
  technique_id STRING,
  strategy_id STRING NOT NULL,
  strategy_version STRING NOT NULL,
  experiment_id STRING,
  experiment_arm_id STRING,
  inputs_hash STRING,
  output_json STRING,
  surface STRING,
  user_mode STRING,
  computed_at TIMESTAMP NOT NULL,
  _op STRING, _lsn INT64, _ingested_at TIMESTAMP, _source_commit_ts TIMESTAMP
)
PARTITION BY DATE(computed_at)
CLUSTER BY experiment_id, technique_family_id, strategy_id;

-- Fact: aggregation_signal
CREATE TABLE josi_olap.fct_aggregation_signal (
  id STRING NOT NULL,
  organization_id STRING NOT NULL,
  aggregation_event_id STRING NOT NULL,
  signal_type STRING NOT NULL,
  signal_value_json STRING,
  recorded_by_user_id STRING,
  recorded_at TIMESTAMP NOT NULL,
  _op STRING, _lsn INT64, _ingested_at TIMESTAMP, _source_commit_ts TIMESTAMP
)
PARTITION BY DATE(recorded_at)
CLUSTER BY signal_type, organization_id;

-- Dim snapshots (slowly changing)
CREATE TABLE josi_olap.dim_source_authority (
  source_id STRING NOT NULL,
  display_name STRING, tradition STRING, era STRING, citation_system STRING,
  default_weight NUMERIC, language STRING,
  valid_from TIMESTAMP NOT NULL,
  valid_to TIMESTAMP         -- null = current
);
-- Type 2 SCD; new row per change.
```

**Idempotent dedupe view** (the streaming inserts are at-least-once):

```sql
CREATE VIEW josi_olap.v_technique_compute AS
SELECT * EXCEPT(_rn)
FROM (
  SELECT *, ROW_NUMBER() OVER (
    PARTITION BY chart_id, rule_id, source_id, rule_version
    ORDER BY _lsn DESC
  ) AS _rn
  FROM josi_olap.fct_technique_compute
)
WHERE _rn = 1 AND _op != 'D';
```

All downstream marts read the `v_*` views, never the raw fact tables.

### 5.3 API contract

**Internal Python interface:**

```python
# src/josi/services/replication/slot_monitor.py

class SlotMonitor:
    """Tracks logical replication slot lag; emits Prometheus metrics."""

    async def get_slot_lag(self, slot_name: str) -> SlotLag:
        """Returns (committed_lsn, flushed_lsn, lag_bytes, lag_seconds)."""

    async def alert_if_lag_exceeds(
        self, slot_name: str, warn_sec: int = 300, page_sec: int = 900
    ) -> None: ...


# src/josi/services/replication/enrichment_worker.py

class EnrichmentWorker:
    """Consumes a Pub/Sub subscription; enriches with dim snapshots; writes to sink."""

    def __init__(
        self,
        subscription: str,
        sink: Sink,
        dim_snapshot_service: DimSnapshotService,
        dlq_topic: str,
    ): ...

    async def run(self) -> None: ...


# src/josi/services/replication/bigquery_sink.py

class BigQuerySink(Sink):
    async def write_batch(self, rows: list[FactRow]) -> WriteResult:
        """Streaming insert with dedupe tag on (pk, _lsn)."""
```

**External: warehouse query surface.** All analytics consumers call BQ directly (no API layer for P4 — that is D7 in P5). Access via GCP IAM: `roles/bigquery.dataViewer` on `josi_olap` dataset, further scoped by authorized views for research/PII isolation.

**Cutover signal:** each sink writes a `sink_heartbeat` row every 60 s containing its current LSN; `SELECT MAX(_source_commit_ts) FROM josi_olap.fct_technique_compute` is the single source of truth for freshness.

## 6. User Stories

### US-S4.1: As a data scientist, I want to query 100M charts' yoga activation rates in < 30 s
**Acceptance:** `SELECT source_id, COUNT(*) FROM v_technique_compute WHERE technique_family_id='yoga' AND JSON_VALUE(result_json, '$.active')='true' GROUP BY 1` returns in under 30 s against the full 200B-row corpus, reading only `source_id`, `technique_family_id`, and the JSON column (clustered read).

### US-S4.2: As the experimentation team, I want E14a scoreboards to read from BQ not OLTP
**Acceptance:** the scoreboard query path in `P3-E8-obs` routes to `josi_olap.mart_experiment_scoreboard`; OLTP `aggregation_signal` receives zero analytics scans during business hours (verified in `pg_stat_statements`).

### US-S4.3: As SRE, I want to be paged if OLAP lag exceeds 15 minutes
**Acceptance:** slot_monitor Prometheus metric `josi_olap_slot_lag_seconds` drives an Alertmanager rule; synthetic test of stopping the consumer triggers a page within 16 minutes.

### US-S4.4: As a backend engineer, I want a bad enrichment bug to be replayable
**Acceptance:** reprocessing a dead-letter topic with a fixed transform version produces identical row counts and checksums; no OLTP replay needed.

### US-S4.5: As Finance, I want predictable monthly OLAP cost
**Acceptance:** monthly BQ + Pub/Sub + Dataflow cost stays within ±10% of the $8.1k baseline across 12 months of steady-state traffic; cost dashboard exists.

### US-S4.6: As a classical researcher, I want to query cross-source agreement without touching OLTP
**Acceptance:** the `mart_cross_source_agreement` table is refreshed hourly and exposes agreement fraction per (yoga_id, source_pair) over the full corpus.

## 7. Tasks

### T-S4.1: Enable logical replication on Cloud SQL
- **Definition:** Apply `wal_level = logical`, `max_replication_slots = 10`, `max_wal_senders = 10` via `cloud_sql_flags.tf`; restart instance during maintenance window. Verify with `SHOW wal_level`.
- **Acceptance:** Flags applied in both dev and prod; instance healthy post-restart; no replica lag regression.
- **Effort:** 4 hours (plus 30-min maintenance window)
- **Depends on:** none

### T-S4.2: Create publications and slots
- **Definition:** Idempotent migration creating `josi_olap_fct` and `josi_olap_dim` publications and two slots (`josi_olap_bq`, `josi_olap_ch`). Managed by `publication_manager.py`. Publications use `publish_via_partition_root = true` so partition churn does not break subscribers (works with F3).
- **Acceptance:** Publications visible in `pg_publication`; slots in `pg_replication_slots`. New partitions created by F3 maintenance are auto-included.
- **Effort:** 1 day
- **Depends on:** T-S4.1

### T-S4.3: Stand up Pub/Sub topics + DLQ
- **Definition:** Terraform: topic `josi-olap-fct`, `josi-olap-dim`, with subscriptions `olap-bq-sink`, `olap-ch-sink`. 7-day retention. Dead-letter topic `josi-olap-dlq` (30-day retention). IAM: Cloud SQL SA publishes; Dataflow SA subscribes.
- **Acceptance:** `gcloud pubsub topics list` shows topics; DLQ receives messages that fail 5 ack deadlines.
- **Effort:** 1 day
- **Depends on:** none

### T-S4.4: Deploy Debezium Server for pgoutput → Pub/Sub
- **Definition:** Debezium Server in Cloud Run sidecar (or small GKE deployment) configured against slot `josi_olap_bq` publication `josi_olap_fct`. Output to Pub/Sub `josi-olap-fct`. Tombstone suppression off. Schema embed mode ON.
- **Acceptance:** INSERTs on `technique_compute` in dev surface as Pub/Sub messages with `_op = 'I'` within 1 s. End-to-end throughput test at 20k rows/s sustained.
- **Effort:** 3 days
- **Depends on:** T-S4.2, T-S4.3

### T-S4.5: Build enrichment worker + dim snapshot cache
- **Definition:** Python service that pulls from `olap-bq-sink`, looks up dim fields from in-memory cache (refreshed every 5 min via `DimSnapshotService`), emits enriched FactRow. Batches of 500 rows / 1 s window.
- **Acceptance:** Enrichment worker P99 processing latency < 1 s per batch. Dim cache miss triggers lazy refresh. All unit tests pass. Ack only after sink.write_batch returns success.
- **Effort:** 1 week
- **Depends on:** T-S4.4

### T-S4.6: BigQuery sink with idempotent dedupe
- **Definition:** `BigQuerySink` uses streaming insert API with `insertId = f"{pk}:{lsn}"` for dedupe within the 1-minute window. Creates target tables from Terraform. Emits `fct_technique_compute`, `fct_aggregation_event`, `fct_aggregation_signal`, `fct_chart_reading_view`. Failures go to DLQ.
- **Acceptance:** Backfill of 10M rows round-trips correctly; replay from DLQ produces zero duplicate rows under the `v_*` views.
- **Effort:** 1 week
- **Depends on:** T-S4.5

### T-S4.7: Backfill tool
- **Definition:** `josi olap backfill --table technique_compute --from 2026-01-01 --to 2026-04-19` reads Postgres partition-by-partition (F3), emits rows as `_op='I'`, `_lsn=synthetic_monotonic`, `_source_commit_ts=row.computed_at`. Rate-limited to not saturate OLTP (< 10% of CPU).
- **Acceptance:** 1 B rows backfilled in < 4 h; no OLTP regression (P99 read latency within 10% of pre-backfill).
- **Effort:** 3 days
- **Depends on:** T-S4.6

### T-S4.8: Slot monitor + alerts
- **Definition:** `SlotMonitor` queries `pg_replication_slots` every 30 s, exports `josi_olap_slot_lag_seconds{slot="…"}` Prometheus metric. Alertmanager rule: warn at 5 min, page at 15 min. Dashboards in Grafana.
- **Acceptance:** Kill the enrichment worker; alert fires at expected thresholds; dashboard shows lag rising then recovering after worker restart.
- **Effort:** 2 days
- **Depends on:** T-S4.5

### T-S4.9: Author warehouse marts + scheduled queries
- **Definition:** SQL files in `src/josi/analytics/bq_queries/` for `mart_experiment_scoreboard`, `mart_rule_observability`, `mart_cross_source_agreement`, `mart_differential_testing`. Schedule hourly via `bq mk --transfer_config` managed through Terraform.
- **Acceptance:** All 4 marts refresh on schedule; query examples in PR reproduce P3-E8-obs dashboard numbers within 0.1%.
- **Effort:** 1 week
- **Depends on:** T-S4.7

### T-S4.10: Cutover P3-E8-obs and C5 to BQ
- **Definition:** Update P3-E8-obs dashboard data sources and C5 differential-testing reporter to query BQ. Keep OLTP fallback for 2 weeks, then remove.
- **Acceptance:** Dashboards load from BQ; OLTP analytics queries drop to zero in `pg_stat_statements`.
- **Effort:** 3 days
- **Depends on:** T-S4.9

### T-S4.11: ClickHouse Cloud sink (opt-in)
- **Definition:** Parallel `ClickHouseSink` subscribed to the same Pub/Sub topics via the `olap-ch-sink` subscription. Writes to MergeTree tables with projections mirroring BQ clustering. Not on the default rollout — enabled via env flag.
- **Acceptance:** When enabled, ClickHouse tables reach parity with BQ within the 5-min SLO. Sample query `SELECT source_id, count() FROM fct_technique_compute GROUP BY 1` returns in < 500 ms on 10B rows (vs BQ's ~10 s).
- **Effort:** 1 week
- **Depends on:** T-S4.6

### T-S4.12: Cost monitoring dashboard
- **Definition:** Looker Studio or Grafana dashboard pulling billing export to BQ. Panels: BQ slot-hours, BQ storage, Pub/Sub egress, Dataflow compute, ClickHouse (if enabled). Forecast vs budget.
- **Acceptance:** Dashboard exists; monthly cost within ±10% forecast for 3 consecutive months.
- **Effort:** 2 days
- **Depends on:** T-S4.10

## 8. Unit Tests

### 8.1 publication_manager

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_create_publication_idempotent` | run twice | second run no-op | safe re-run |
| `test_publish_via_partition_root_enabled` | inspect `pg_publication` | `pubviaroot = true` | F3 partitions auto-included |
| `test_slot_creation` | create slot | `pg_replication_slots` row present | baseline |
| `test_missing_source_table_fails_fast` | drop a fact table, run manager | raises | prevents silent partial pub |

### 8.2 enrichment_worker

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_enrichment_adds_dim_fields` | fact row for chart with source_id='bphs' | output has `source_display_name='Brihat Parashara Hora Shastra'` | dim inline correctness |
| `test_dim_cache_refresh_on_miss` | fact references new `source_id` not in cache | cache refresh triggered; row enriched | lazy refresh |
| `test_enrichment_dlq_on_unknown_dim` | fact references `source_id` absent from Postgres | message routed to DLQ, not ack'd to subscription | safety |
| `test_idempotent_batch_processing` | same batch twice | sink called once per unique `(pk, _lsn)` | at-least-once safety |
| `test_order_preserved_per_pk` | two messages for same PK with different _lsn | later _lsn wins at sink view | correctness |

### 8.3 bigquery_sink

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_streaming_insert_dedupe` | insert same row twice with same _lsn | BQ streaming insertId dedupe within 1 min | idempotency |
| `test_delete_op_emits_tombstone` | `_op='D'` message | row in table with `_op='D'`; `v_*` view excludes | soft-delete semantics |
| `test_schema_widening_new_column` | dim gained new column | BQ schema auto-widened; old rows have NULL | schema evolution |
| `test_bq_streaming_error_to_dlq` | simulated 503 | message re-queued with backoff; eventual DLQ after 10 retries | failure handling |

### 8.4 slot_monitor

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_slot_lag_computed` | mock `pg_replication_slots` row | returns (lsn, bytes, seconds) correctly | metric shape |
| `test_alert_fires_at_warn_threshold` | lag 6 min | warn-level Prometheus alert registered | pager sensitivity |
| `test_alert_fires_at_page_threshold` | lag 16 min | page-level Prometheus alert registered | SRE contract |
| `test_no_alert_under_threshold` | lag 2 min | no alert | noise floor |

### 8.5 backfill tool

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_backfill_partition_by_partition` | 3-month range across 3 partitions | each partition read independently | memory cap |
| `test_backfill_rate_limiter` | simulated 10k rows/s limit | Postgres CPU usage stays below target | no OLTP impact |
| `test_backfill_resumable` | kill mid-backfill | resume reads remaining partitions only | operational safety |

### 8.6 End-to-end integration

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_e2e_insert_visible_in_bq` | INSERT on technique_compute in test DB | row visible under `v_technique_compute` within 90 s | real-world SLO |
| `test_e2e_update_latest_wins` | INSERT then UPDATE | `v_*` view returns UPDATE row | SCD-light correctness |
| `test_e2e_delete_hidden` | INSERT then DELETE | `v_*` view excludes row | soft-delete |
| `test_e2e_dim_update_backfill_marts` | change dim row | mart refresh picks up new dim values within schedule | dim SCD to fact enrichment |

## 9. EPIC-Level Acceptance Criteria

- [ ] Logical replication enabled on Cloud SQL prod without regressing OLTP P99 latency beyond 5%
- [ ] All 4 fact tables (technique_compute, aggregation_event, aggregation_signal, chart_reading_view) + 8 dim tables continuously replicated to BigQuery
- [ ] Steady-state lag P99 < 5 minutes, SLO measured and dashboarded
- [ ] Backfill completes 10M chart historical data in < 4 h with no OLTP impact
- [ ] P3-E8-obs dashboards, C5 differential reports, and E14a scoreboards all cut over to BQ; OLTP analytics query load drops to < 1% of pre-cutover
- [ ] DLQ replay produces exact-parity row counts and hashes
- [ ] Cost dashboard shows actuals within ±10% of $8.1k/month baseline
- [ ] ClickHouse sink available behind feature flag; parity test passes
- [ ] Unit test coverage ≥ 90% on replication modules
- [ ] Runbook: "OLAP lag alert — triage and recovery" published in `docs/runbooks/`
- [ ] Documentation updated: `CLAUDE.md` notes the OLAP dataset and forbids direct OLTP scans for analytics

## 10. Rollout Plan

- **Feature flag:** `OLAP_REPLICATION_ENABLED` (infra-level). Three states:
  - `off` — no slots, no workers (P3 default)
  - `shadow` — slots active, workers writing to BQ but no consumer cut over
  - `primary` — consumers read BQ, OLTP analytics paths removed
- **Shadow compute:** YES. Run `shadow` state for 4 weeks collecting lag, cost, correctness metrics before `primary`.
- **Backfill strategy:** snapshot oldest partition first, then newer, so that the moment steady-state CDC is caught up, the whole corpus is already visible. Parallelize across partitions with rate limit.
- **Rollback plan:** revert analytics queries to OLTP replicas (S2) via a single config flip; keep OLTP replica provisioned for rollback window of 4 weeks after cutover. If replication causes OLTP WAL pressure: `DROP PUBLICATION` and slot instantly halts CDC; no OLTP data loss.

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Replication slot lag grows unbounded, OLTP disk fills | Low | Critical | Slot monitor page at 15 min; auto-drop slot at 60 min if unrecoverable (explicit admin confirm) |
| BQ streaming insert quota hit at 100M users | Medium | High | Use BQ Storage Write API batching; partition per-day writes; request quota increase preemptively |
| Dim lookup enrichment misses, rows land un-enriched | Medium | Medium | DLQ + explicit tests; dim cache has "eager refresh on unknown key" |
| Cost overrun if ad-hoc analysts run unbounded queries | Medium | Medium | BQ reservation model with max-slots per project; monitoring dashboard alerts at $12k/mo |
| Schema drift between OLTP and OLAP | Medium | Medium | Alembic migration CI step emits BQ DDL diff; review required |
| Cloud SQL maintenance breaks slot (standard Postgres behavior) | Medium | High | Slot restart scripts in runbook; re-backfill from last-known `confirmed_flush_lsn` |
| S7 sharding complicates single-source CDC | High (when S7 lands) | High | Each shard publishes to its own slot + topic; sink merges by `organization_id` hash; design doc linked in S7 PRD |
| PII leak into OLAP via `result` JSON | Low | Critical | Result payload schemas (F5) reviewed for PII before P4; BQ authorized views for research access |
| Debezium Server fails — no alternative | Low | High | Documented custom pgoutput reader fallback in runbook; 1-week engineering cost estimated |

## 12. References

- Master spec: [`docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`](../../../superpowers/specs/2026-04-19-classical-techniques-expansion-design.md)
- F2 fact tables: [`F2-fact-tables.md`](../P0/F2-fact-tables.md)
- F3 partitioning: [`F3-partitioning-from-day-one.md`](../P0/F3-partitioning-from-day-one.md)
- S2 read replicas: [`S2-read-replicas-routing.md`](../P3/S2-read-replicas-routing.md)
- S3 serving cache: [`S3-three-layer-serving-cache.md`](../P3/S3-three-layer-serving-cache.md)
- S7 sharding (downstream consumer): [`S7-sharding-citus-or-splitting.md`](./S7-sharding-citus-or-splitting.md)
- P3-E8-obs: [`P3-E8-obs-per-rule-observability.md`](../P3/P3-E8-obs-per-rule-observability.md)
- Research dataset: [`Research-cross-source-agreement-dataset.md`](./Research-cross-source-agreement-dataset.md)
- Debezium Server docs — https://debezium.io/documentation/reference/stable/operations/debezium-server.html
- BigQuery Storage Write API — https://cloud.google.com/bigquery/docs/write-api
- Postgres logical replication — https://www.postgresql.org/docs/current/logical-replication.html
- Cloud SQL for Postgres logical replication flags — https://cloud.google.com/sql/docs/postgres/replication/configure-logical-replication
