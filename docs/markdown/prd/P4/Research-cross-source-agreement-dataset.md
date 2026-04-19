---
prd_id: Research
epic_id: Research
title: "Cross-source agreement research dataset + first-of-its-kind academic paper"
phase: P4-scale-100m
tags: [#experimentation, #correctness]
priority: could
depends_on: [S4, Reference-1000, F2, F8]
enables: [D7, I2]
classical_sources: [bphs, saravali, phaladeepika, jataka_parijata, jataka_bharanam, jaimini_sutras, tajaka_neelakanthi]
estimated_effort: 8-10 weeks engineering + 3-6 months academic cycle
status: draft
author: "@agent"
last_updated: 2026-04-19
---

# Research — Cross-Source Agreement Research Dataset

## 1. Purpose & Rationale

Josi is uniquely positioned: hundreds of millions of natal charts, every classical technique computed against every configured source authority, stored in a queryable OLAP warehouse (S4). No prior platform has had this data at this scale. The product vision's differentiator — "empirically measure classical-technique agreement for the first time" — resolves into a concrete academic deliverable:

> **"Computational Agreement Analysis of Classical Yogas Across 100 Million Horoscopes"**

This PRD scopes the publication of an anonymized dataset and a peer-reviewed paper. Goals:

1. **Scientific.** For each classical yoga, report activation rate per source (BPHS, Saravali, Phaladeepika, Jataka Parijata, Jataka Bharanam). Report pairwise source agreement. Surface yogas with highest disagreement as research-interesting (where classical tradition itself contains competing formulations). Nothing like this has been measured at this scale — ever.
2. **Strategic.** Land a first-of-its-kind open dataset in an academic venue, giving Josi category-defining scholarly credibility. Enables partnerships with Banaras Hindu University (BHU), IIT-B cognition lab, Stanford astronomy. Establishes moat against competitors who lack the compute + corpus.
3. **Ethical.** Zero individual-chart disclosure. All datapoints aggregate; k-anonymity ≥ 1000 on every row. IRB-reviewed.
4. **Product.** Seeds D7 (P5) research API, I2 (P6) Josi Research Press, and Reference-1000's long-tail validation.

This is `could` priority at P4 — opportunistic if resources allow, foundational if activated.

## 2. Scope

### 2.1 In scope

- Cross-source agreement statistics per yoga (activation rate, pairwise agreement, Krippendorff's alpha)
- Dataset schema + anonymization pipeline
- Public data release at `research.josi.ai/datasets/cross-source-agreement-v1`
- Academic paper draft and submission (Sociology of Religion / Journal of Indian Philosophy / Journal of Astronomical History & Heritage — venue TBD)
- Data API endpoint `GET /api/v1/research/cross-source-agreement` returning aggregated statistics only
- Partnership outreach package: talking points for BHU, IIT-B, Stanford
- IRB-equivalent ethics review (we are not an academic institution but we adopt an internal board)
- Opt-in flag on user/org level for inclusion in research corpus (default opt-out for B2C; default opt-in for academic partner orgs)
- Reproducibility: dataset version hash; methodology doc; R/Python analysis notebooks published
- Preregistration of methodology before running analyses (to avoid p-hacking — even though this is descriptive, discipline matters)
- Publication plan: preprint on arXiv + journal submission
- Open review mechanism: public comment period on methodology + dataset before paper submission

### 2.2 Out of scope

- Claiming predictive validity of astrology (not what this paper is about)
- Per-individual analysis (violates ethical baseline)
- Astrologer-preference data (not the research question here — possible follow-up paper)
- Commercial licensing of the dataset (explicitly open under CC BY 4.0)
- Real-time API for researchers — batch dataset release for v1 (interactive API is D7, P5)
- Cross-tradition agreement (Vedic vs Western) — different taxonomic bases; reserved for v2 paper
- Longitudinal validation against real-world outcomes — entirely separate research (requires consenting cohorts; I2+)

### 2.3 Dependencies

- **S4** — OLAP warehouse is the compute substrate for the statistics
- **Reference-1000** — subject corpus: the yogas we analyze
- **F2** — `technique_compute` is the raw data
- **F8** — aggregation machinery (though this paper reports per-source, not aggregated)
- Ethics board: retained external ethicist specializing in AI research ethics + one academic advisor from religion/philosophy
- Academic partnerships: provisional MoUs with BHU, IIT-B (optional but high value)
- Legal review: GDPR for EU users; CCPA for California; India's DPDP Act (2023)

## 3. Research Methodology

### 3.1 Research question

> For each classical yoga in Josi's curated catalog (≥ 1000 yogas at Reference-1000 completion), what is the per-source activation rate across 100M natal charts, and what is the pairwise agreement between source pairs?

### 3.2 Operationalization

**Unit of analysis:** a yoga (identified by `rule_id`, independent of source).
**Source identifiers:** `source_id ∈ {bphs, saravali, phaladeepika, jataka_parijata, jataka_bharanam}` (we include Jaimini and Tajaka yogas if applicable; we exclude AI-generated/modern yogas from v1).
**Per-chart observation:** the output_hash comparison of `(yoga_id, source_pair)` — either both sources say active, both say inactive, or they disagree.

Let Y = set of yogas; S = set of sources; C = corpus of charts (sampled or whole).

- **Activation rate**: `p_a(y, s) = |{c ∈ C : active(y, s, c)}| / |C|` for each `(y, s)`.
- **Pairwise agreement**: for sources `s₁, s₂` and yoga `y`, proportion of `c` where both agree (both active, or both inactive).
- **Krippendorff's alpha (α)** on binary nominal data: across all sources that formulate a given yoga, reliability coefficient. Higher α = stronger inter-source agreement.
- **Disagreement index** `d(y) = 1 - min_pairwise_agreement(y)` highlights research-interesting yogas.

### 3.3 Sampling

- **Whole-corpus pass** for activation rates (200B rows of `technique_compute` aggregated to per-yoga counts). BQ handles this in minutes.
- **100M stratified chart sample** for agreement statistics, stratified to ensure representation across birth decades, hemispheres, ascendant signs.
- **10k-chart bootstrap sample** for confidence intervals on activation rates (sample size sufficient for 0.5% resolution).

### 3.4 Anonymization guarantees

- **k-anonymity ≥ 1000**: every published row is aggregated over ≥ 1000 charts. Rows with fewer charts are suppressed.
- **Removed fields**: birth date, location (lat/long), name, user_id, organization_id. Only `sun_sign`, `ascendant_sign`, birth decade retained as stratification dimensions at suppression threshold.
- **Differential privacy (stretch)**: add Laplace noise with ε=1.0 to published counts. Reduces re-identification risk to below standard open-data thresholds.
- **Release bundle hash**: SHA-256 committed for reproducibility; dataset immutable post-release.

### 3.5 Preregistration

Methodology frozen in `docs/markdown/research/2026-preregistration.md` before any statistics are computed. Preregistration covers:

- Hypotheses (or descriptive claims)
- Sample size and stratification
- Exclusion criteria (e.g., charts with birth time precision > 1 h excluded)
- Statistical tests and thresholds
- Multiple-comparison correction (Benjamini-Hochberg across yogas)

Any deviation must be documented as a "post-hoc exploration" in the paper, not rolled into primary claims.

### 3.6 Ethics and IRB-equivalent review

Josi has no IRB but adopts one:

- External ethics board: 1 bioethicist, 1 academic astronomy/religion scholar, 1 ML-ethics researcher
- Reviews protocol before data pipeline runs
- Reviews dataset schema before public release
- Annual re-review for follow-on releases

Key ethical concerns:

- **Do no identification.** k-anonymity + removed PII.
- **Do no harm.** Paper is explicit that astrology is not asserted to be predictive; this is a descriptive study of classical traditions' computational implications.
- **Consent.** B2C users opt-in only; default is opt-out (reversing Josi's default stance for commercial data). B2B organizations opt-in on their user cohort with proper notification.
- **Cultural sensitivity.** Classical Vedic astrology is a living tradition within Hindu religious practice; we partner with tradition-bearers (advisors, BHU) and invite their commentary as a section of the paper.

### 3.7 Methodological precedents

This paper sits at the intersection of:

- Computational religious studies (e.g., Roes 2014 on cross-tradition agreement analysis)
- Scholarly astrology / astronomical history (e.g., Pingree's work on Indian astronomy)
- Large-scale observational corpus analysis (astronomy survey papers)
- Computational social science open-data releases (Twitter/X research datasets)

Venue shortlist:

- *Journal of Astronomical History and Heritage* — neutral astronomy-history framing
- *Journal of Indian Philosophy* — scholarly tradition-focus
- *Religions* (MDPI, open-access) — multi-disciplinary, fast turnaround
- *Sociology of Religion* — if framed around tradition-variance
- arXiv `cs.CY` — preprint always, first

Paper is framed as **descriptive analysis of computational implications of classical variance**, not a claim about truth-value of astrology.

### 3.8 Alternatives considered

| Alternative | Rejected because |
|---|---|
| Ship dataset without paper | Loses scholarly credibility play |
| Paper without dataset | Blocks reproducibility and partnership value |
| Include astrologer override rates in v1 | Mixes research questions; delays release |
| Full corpus release (non-aggregated) | Unacceptable PII risk even with removal |
| Commercial closed dataset | Contradicts master spec §7 "closed-source classical rules" non-goal |
| Wait for I2 Research Press at P6 | P4 timing lets Josi claim first-mover in academic space |

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| Primary venue | arXiv preprint first; target *Journal of Astronomical History and Heritage* for journal publication; *Religions* as backup | Balance rigor and reach |
| License | CC BY 4.0 on dataset; CC BY 4.0 on paper if venue permits | Aligns with master spec's open-content stance |
| Opt-in default for B2C | Opt-out (users must check "include in research") | Conservative; consent-forward |
| Opt-in default for B2B | Opt-in at contract negotiation; per-org toggle | Contractual clarity |
| k-anonymity threshold | 1000 | Strong by open-data norms; precedent in health data releases |
| Differential privacy | Stretch goal v1; mandatory v2 | Engineering cost non-trivial; monitor re-identification attempts post-v1 |
| Researcher access | Batch dataset only v1; API is D7 P5 | Release-first, interactive-later |
| Authorship attribution | Lead author: Josi senior engineer + classical-advisor co-author; external academic advisors as co-authors where materially involved | Classic multi-disciplinary |
| Conflict-of-interest disclosure | Full: Josi authors disclose employment; dataset is from commercial product | Transparency |
| Post-publication update cadence | Yearly v2, v3, with change log | Corpus grows, results refresh |
| Response to critical review | Peer-reviewed + public comment period before submission | Invites criticism pre-publication |
| Handling retraction request | If ethics breach surfaces, paper retracted and dataset withdrawn; documented in governance doc | Integrity |

## 5. Component Design

### 5.1 New services / modules

```
src/josi/services/research/
├── __init__.py
├── consent_manager.py              # opt-in / opt-out tracking per user + org
├── dataset_builder.py              # BQ query pipeline for aggregate stats
├── anonymizer.py                   # k-anonymity + DP noise application
├── stratified_sampler.py           # stratified sampling helper
├── methodology_validator.py        # checks adherence to preregistration
├── release_packager.py             # bundles CSV / Parquet / JSON + methodology doc + checksums
└── research_api_controller.py      # public API for aggregate stats

src/josi/db/bq_queries/research/
├── agreement_activation_rate.sql
├── agreement_pairwise.sql
├── agreement_krippendorff.sql
├── stratified_sample.sql
└── suppression_gate.sql

docs/markdown/research/
├── 2026-preregistration.md
├── methodology-v1.md
├── ethics-board-minutes.md
├── paper-draft-latex/              # latex source
└── dataset-release-v1/             # signed release assets
```

### 5.2 Data model additions

```sql
-- ============================================================
-- research_consent: user / org inclusion in research corpus
-- ============================================================
CREATE TABLE research_consent (
    id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scope_type           TEXT NOT NULL CHECK (scope_type IN ('user','organization')),
    scope_id             UUID NOT NULL,
    consent_state        TEXT NOT NULL CHECK (consent_state IN ('opted_in','opted_out')),
    consent_text_version TEXT NOT NULL,
    consented_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    consent_source       TEXT NOT NULL,            -- 'signup_wizard' | 'settings_page' | 'b2b_contract'
    revoked_at           TIMESTAMPTZ,
    UNIQUE (scope_type, scope_id)
);

CREATE INDEX idx_consent_included ON research_consent(scope_type) WHERE consent_state = 'opted_in' AND revoked_at IS NULL;

-- ============================================================
-- research_release: version + signature of every public dataset release
-- ============================================================
CREATE TABLE research_release (
    id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    version              TEXT NOT NULL,          -- 'v1.0', 'v1.1', ...
    released_at          TIMESTAMPTZ NOT NULL,
    charts_included      BIGINT NOT NULL,
    orgs_included        INTEGER NOT NULL,
    users_included       BIGINT NOT NULL,
    dataset_sha256       CHAR(64) NOT NULL,
    methodology_sha256   CHAR(64) NOT NULL,
    preregistration_sha256 CHAR(64) NOT NULL,
    dp_epsilon           NUMERIC(5,4),            -- null if no DP applied
    k_anonymity_threshold INTEGER NOT NULL,
    irb_approval_id      TEXT,                    -- internal ethics board record id
    release_notes        TEXT,
    paper_doi            TEXT,
    paper_arxiv_id       TEXT
);

-- ============================================================
-- research_query_log: every query run against research API
-- ============================================================
CREATE TABLE research_query_log (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    release_version     TEXT NOT NULL,
    api_key_id          UUID REFERENCES api_key(api_key_id),   -- research access via dedicated key
    query_params        JSONB NOT NULL,
    rows_returned       INTEGER NOT NULL,
    query_latency_ms    INTEGER NOT NULL,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### 5.3 BigQuery aggregation views

```sql
-- research mart: per-yoga per-source activation rates with suppression
CREATE OR REPLACE TABLE `josi_olap.research_activation_rate_v1`
PARTITION BY DATE(computed_at_day)
CLUSTER BY rule_id, source_id
AS
WITH base AS (
  SELECT
    rule_id,
    source_id,
    COUNT(DISTINCT chart_id) AS charts_with_rule,
    COUNTIF(JSON_VALUE(result_json, '$.active') = 'true') AS active_count,
    DATE_TRUNC(computed_at, DAY) AS computed_at_day
  FROM `josi_olap.v_technique_compute` tc
  JOIN `josi_olap.consent_view` cv USING (organization_id)
  WHERE cv.consent_state = 'opted_in'
    AND tc.technique_family_id = 'yoga'
  GROUP BY rule_id, source_id, computed_at_day
)
SELECT *,
       SAFE_DIVIDE(active_count, charts_with_rule) AS activation_rate
FROM base
WHERE charts_with_rule >= 1000;       -- k-anonymity gate
```

```sql
-- pairwise agreement
CREATE OR REPLACE TABLE `josi_olap.research_pairwise_agreement_v1` AS
WITH pairs AS (
  SELECT
    a.rule_id,
    a.source_id AS source_a,
    b.source_id AS source_b,
    a.chart_id,
    JSON_VALUE(a.result_json,'$.active') AS a_active,
    JSON_VALUE(b.result_json,'$.active') AS b_active
  FROM `josi_olap.v_technique_compute` a
  JOIN `josi_olap.v_technique_compute` b
    USING (chart_id, rule_id, technique_family_id)
  WHERE a.source_id < b.source_id
    AND technique_family_id = 'yoga'
)
SELECT
  rule_id, source_a, source_b,
  COUNT(*) AS pair_count,
  COUNTIF(a_active = b_active) AS agreement_count,
  SAFE_DIVIDE(COUNTIF(a_active = b_active), COUNT(*)) AS agreement_rate
FROM pairs
GROUP BY rule_id, source_a, source_b
HAVING pair_count >= 1000;
```

### 5.4 API contract

```
GET /api/v1/research/cross-source-agreement
Query: rule_id?, source?, limit?=100, offset?
Auth: api-key with `research_access` scope (public key issued on request)

Response:
{
  "dataset_version": "v1.0",
  "methodology_sha256": "...",
  "results": [
    {
      "rule_id": "gaja_kesari",
      "source_id": "bphs",
      "charts_with_rule": 87210988,
      "activation_rate": 0.142,
      "activation_rate_ci_95": [0.139, 0.145]
    },
    ...
  ]
}

GET /api/v1/research/cross-source-agreement/pairwise
Query: rule_id?, source_pair?
Response: list of {rule_id, source_a, source_b, agreement_rate, pair_count}

GET /api/v1/research/releases
Response: list of published releases with version, DOI, arxiv_id

GET /api/v1/research/releases/{version}/manifest
Response: full manifest with file URLs, checksums, license
```

**Internal:**

```python
# src/josi/services/research/dataset_builder.py

class DatasetBuilder:
    async def build(self, release_version: str, prereg_sha: str) -> ReleaseBundle:
        """Runs BQ pipeline, applies suppression, serializes CSV/Parquet/JSON,
        writes manifest + checksums, returns local bundle."""

# src/josi/services/research/consent_manager.py

class ConsentManager:
    async def set_user_consent(self, user_id: UUID, opted_in: bool, source: str) -> None: ...
    async def get_consent(self, scope_type: str, scope_id: UUID) -> ConsentState: ...
    async def included_orgs(self) -> list[UUID]:
        """Returns orgs currently opted in for research corpus."""

# src/josi/services/research/anonymizer.py

class Anonymizer:
    def apply_k_anonymity(self, df: DataFrame, k: int = 1000) -> DataFrame: ...
    def apply_dp_noise(self, df: DataFrame, epsilon: float = 1.0) -> DataFrame: ...
```

### 5.5 Consent UX touchpoints

- **Signup wizard** adds a final step: "Contribute anonymously to astrology research?" — default off; 2-sentence explanation + link to policy.
- **Settings page** under `/settings/privacy` lets users toggle consent post-signup; changes respected within 24 h across all research pipelines.
- **B2B org admin page** mirrors same toggle, scoped per-org; cascades to all org users unless individually overridden.

## 6. User Stories

### US-R.1: As a researcher at IIT-B, I want to download the cross-source agreement dataset in CSV
**Acceptance:** `research.josi.ai/datasets/cross-source-agreement-v1.csv` downloads with CC BY 4.0 license file, methodology PDF, and SHA-256 manifest.

### US-R.2: As a classical advisor, I want to see which yogas have the highest disagreement
**Acceptance:** `/api/v1/research/cross-source-agreement/pairwise?sort=agreement_rate_asc` returns yogas sorted by least agreement; top 20 become interesting research items.

### US-R.3: As a B2C user, I want opt-in consent respected with granular control
**Acceptance:** toggling research consent off removes my chart from the next dataset build; all prior releases are immutable (cannot remove from released bundle, documented in consent text).

### US-R.4: As a journal reviewer, I want to reproduce Table 3 of the paper from the dataset
**Acceptance:** R/Python notebook at `docs/markdown/research/paper-draft-latex/reproducibility/table3.ipynb` runs against released CSV and produces identical table.

### US-R.5: As an ethics board member, I want to review methodology before dataset runs
**Acceptance:** preregistration doc + methodology doc circulated 30 days before first dataset build; board sign-off gate enforced in `release_packager.py`.

### US-R.6: As Josi leadership, I want this paper on arXiv by Q4 of P4
**Acceptance:** arXiv ID issued; paper publicly downloadable; press release drafted.

### US-R.7: As a hostile reviewer, I want to check for p-hacking
**Acceptance:** preregistration timestamp predates analysis code commits; any post-hoc analyses clearly labeled in paper; dataset published before paper submission.

## 7. Tasks

### T-R.1: Draft ethics board charter + recruit members
- **Definition:** Written charter describing board composition, authority, review cadence, conflict handling. Recruit 3 external members.
- **Acceptance:** Charter signed; members onboarded; first meeting minutes logged.
- **Effort:** 3 weeks (external-dependency bound)

### T-R.2: Consent UX + data model
- **Definition:** `research_consent` table + Alembic migration. Settings UI + signup wizard step. Consent API endpoints. B2B org-admin toggle.
- **Acceptance:** User can opt in/out; toggle respected in dataset builder within 24 h; analytics event fired on change.
- **Effort:** 2 weeks

### T-R.3: Preregistration document
- **Definition:** Written in `docs/markdown/research/2026-preregistration.md`. Covers hypotheses (descriptive), sample size, exclusion criteria, statistical methods, suppression rules. Reviewed by ethics board.
- **Acceptance:** Document sha256 hash committed; locked via git tag; ethics board approval logged.
- **Effort:** 2 weeks

### T-R.4: BigQuery analytics marts
- **Definition:** SQL files for activation rate, pairwise agreement, Krippendorff's alpha. Scheduled queries for weekly refresh. Suppression gate enforced at view level.
- **Acceptance:** Marts populate from OLAP; suppression drops rows with <1000 charts; spot-check on 5 known yogas matches expected counts.
- **Effort:** 2 weeks
- **Depends on:** S4

### T-R.5: Anonymizer + DP noise layer
- **Definition:** `Anonymizer.apply_k_anonymity` and `Anonymizer.apply_dp_noise`. Unit tests on synthetic data.
- **Acceptance:** k-anonymity passes on realistic data; DP epsilon=1.0 shows expected noise magnitude; no row leaks through gate.
- **Effort:** 1 week
- **Depends on:** T-R.3

### T-R.6: ReleasePackager
- **Definition:** Produces downloadable bundle: CSV + Parquet + JSON + methodology PDF + preregistration PDF + manifest (SHA-256 per file) + license. Signs with GPG.
- **Acceptance:** Bundle downloads, checksums verify, license present; GPG signature verifies against publicly-pinned key.
- **Effort:** 1 week
- **Depends on:** T-R.5

### T-R.7: Research API + rate limiting
- **Definition:** `/api/v1/research/...` endpoints; dedicated API-key scope `research_access` with rate limit 100 req/min; query logging to `research_query_log`.
- **Acceptance:** End-to-end: request key, query endpoint, see row in query_log, rate limit enforced.
- **Effort:** 1 week
- **Depends on:** T-R.4

### T-R.8: v1 dataset build end-to-end
- **Definition:** Run the full pipeline: pull consented corpus (expected ~50M charts at P4), compute marts, apply anonymization, package. Validate row counts against expectations.
- **Acceptance:** v1 bundle produced; ethics board reviews and approves release; bundle uploaded to `research.josi.ai`.
- **Effort:** 2 weeks (pipeline runtime + review)
- **Depends on:** T-R.6

### T-R.9: Write paper draft
- **Definition:** Lead author + classical-advisor co-author + external academic advisor draft paper. Sections: introduction, methodology, results, discussion, limitations, tradition-bearer commentary. Reproducibility notebooks embedded.
- **Acceptance:** Draft complete; internal review round 1 complete; external advisor sign-off.
- **Effort:** 6 weeks (editorial-bound)
- **Depends on:** T-R.8

### T-R.10: arXiv submission
- **Definition:** Submit to arXiv cs.CY / physics.hist-ph. Coordinate release announcement.
- **Acceptance:** arXiv ID issued; public URL live; press release drafted.
- **Effort:** 1 week
- **Depends on:** T-R.9

### T-R.11: Journal submission
- **Definition:** Primary target venue submission with formatting, cover letter, suggested reviewers.
- **Acceptance:** Submitted; confirmation email saved; tracking ticket open for journal response.
- **Effort:** 1 week
- **Depends on:** T-R.10

### T-R.12: Public comment + partnership outreach
- **Definition:** 30-day public comment period on preprint; outreach package to BHU, IIT-B, Stanford contacts. Collect feedback and integrate before journal revision.
- **Acceptance:** Comment submissions archived; revision plan in place.
- **Effort:** 4 weeks
- **Depends on:** T-R.10

### T-R.13: v1.1 update for post-comment revisions
- **Definition:** Revise dataset if material issues surfaced; update paper.
- **Acceptance:** v1.1 released; change log explicit.
- **Effort:** 2 weeks
- **Depends on:** T-R.12

## 8. Unit Tests

### 8.1 consent_manager

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_default_user_consent_is_opted_out` | new user | returns 'opted_out' | default-off contract |
| `test_toggle_consent_persists` | opt-in then read | returns 'opted_in' | persistence |
| `test_revoke_consent_recorded` | revoke | revoked_at set | audit |
| `test_included_orgs_filter` | 3 orgs, 2 opted in | returns the 2 | corpus scoping |
| `test_consent_text_version_required` | opt-in missing version | ValueError | regulatory |

### 8.2 anonymizer

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_k_anonymity_drops_small_groups` | groups of sizes 500, 1500, 2000 | 1500 and 2000 retained | suppression |
| `test_k_anonymity_preserves_total_counts` | dataset | sum(kept) ≤ sum(input) | integrity |
| `test_dp_noise_distribution` | 10k runs | Laplace-distributed deviations | correctness |
| `test_dp_noise_sign_random` | 10k runs | ≈50/50 positive/negative | unbiased |
| `test_no_leak_through_gate` | synthetic PII columns | not present in output | defense in depth |

### 8.3 dataset_builder

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_build_respects_consent` | non-consented org in OLAP | not in output | consent fidelity |
| `test_build_applies_suppression` | rule with 500 charts | row suppressed | k-anon integration |
| `test_build_writes_manifest` | any build | manifest.json with per-file sha256 | reproducibility |
| `test_build_fails_without_prereg` | missing preregistration hash | raises | methodology gate |
| `test_build_is_idempotent_for_same_inputs` | two builds same day | identical sha256 | determinism |

### 8.4 research_api

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_research_api_requires_scope` | api key without research_access | 403 | authz |
| `test_agreement_endpoint_returns_rows` | valid query | rows with required fields | API contract |
| `test_query_logged` | any call | row in research_query_log | audit |
| `test_rate_limit_enforced` | 101 requests/min | 101st returns 429 | rate limit |
| `test_suppressed_rows_not_leaked` | rule with < 1000 charts | no row returned | suppression |

### 8.5 Reproducibility

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_notebook_reproduces_table3` | dataset v1 + notebook | table3 output matches paper | reproducibility guarantee |
| `test_dataset_sha256_stable_across_runs` | same preregistration, same input | same bundle sha256 | determinism |

## 9. EPIC-Level Acceptance Criteria

- [ ] Ethics board in place; charter published; members recruited
- [ ] Consent UX live; opt-in rates tracked in product analytics
- [ ] Preregistration document locked with public sha256 hash
- [ ] BigQuery analytics marts refresh on schedule with k-anonymity ≥ 1000
- [ ] v1 dataset bundle published with GPG signature and CC BY 4.0 license
- [ ] Public dataset download available at `research.josi.ai/datasets/cross-source-agreement-v1`
- [ ] `/api/v1/research` endpoints live; rate-limited; logged
- [ ] Academic paper posted on arXiv
- [ ] Paper submitted to primary target journal
- [ ] Reproducibility notebook for each major table in paper
- [ ] Public comment period conducted; feedback incorporated
- [ ] Press release drafted; partnership outreach initiated (BHU, IIT-B, Stanford)
- [ ] Ethics board approval on each release logged
- [ ] Documentation merged: methodology, ethics policy, consent text, API guide
- [ ] Unit test coverage ≥ 90% on anonymizer + dataset_builder (correctness-critical)

## 10. Rollout Plan

- **Feature flag:** `RESEARCH_DATASET_ENABLED` for backend pipeline (off by default until ethics approval). Consent UX ships independently behind `RESEARCH_CONSENT_UX` flag.
- **Shadow compute:** N/A — dataset construction is one-shot per release, reviewed before publish.
- **Backfill strategy:** consent is forward-only; no retroactive inclusion. First dataset uses whatever corpus has opted in at build time.
- **Rollback plan:**
  1. If dataset release contains ethics breach, dataset withdrawn from `research.josi.ai`; arXiv version-update issued.
  2. `research_release.released_at` retained for history; download links 404 with clear notice.
  3. Retraction documented in governance doc and ethics board minutes.

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Opt-in rates too low for statistical power | Medium | High | Nudge via in-app message; academic-partner orgs opt in at contract; B2B enterprise customers opt in by default |
| Re-identification attack on published dataset | Low | Critical | k-anon ≥ 1000; DP noise v2; ethics board sign-off gate; monitor for published attack |
| Paper rejected by target journal | Medium | Medium | Multiple target venues; arXiv preprint secures priority regardless |
| Hostile public response to astrology research | Medium | Medium | Paper framed as descriptive classical-tradition analysis; press prep with leadership + external advisors |
| Data scientists at Josi run exploratory analyses that become p-hacking | Medium | High | Preregistration; separate exploratory dataset for internal use; disciplined reviewer |
| Advisor or advisor-affiliated individual disputes finding | Medium | Medium | Tradition-bearer commentary section in paper; public comment period |
| Legal challenge (DPDP Act / GDPR) | Low | High | Legal review of consent flow; dataset schema does not include PII; counsel's sign-off logged |
| Dataset build pipeline fails at 50M charts | Medium | Medium | BQ sized for scale; batch mode with retry; ethics gate does not advance to release until successful build |
| arXiv moderators reject | Low | Low | Endorsement from academic co-author; choose correct category |
| Partnership orgs slow to engage | Medium | Low | v1 ships independently; partnerships are upside |
| Paper language offends religious communities | Medium | High | Tradition-bearer commentary; advisor review; avoid truth-claims |

## 12. References

- Master spec: [`docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`](../../../superpowers/specs/2026-04-19-classical-techniques-expansion-design.md)
- S4 OLAP replication: [`S4-olap-replication-clickhouse.md`](./S4-olap-replication-clickhouse.md)
- F2 fact tables: [`F2-fact-tables.md`](../P0/F2-fact-tables.md)
- Reference-1000: [`Reference-1000-expanded-yoga-set.md`](./Reference-1000-expanded-yoga-set.md)
- D7 Research Data API (P5): [`D7-research-data-api.md`](../P5/D7-research-data-api.md)
- I2 Josi Research Press (P6): [`I2-josi-research-press.md`](../P6/I2-josi-research-press.md)
- Krippendorff, K. (2011). *Computing Krippendorff's Alpha-Reliability*. Annenberg School
- Dwork & Roth (2014). *The Algorithmic Foundations of Differential Privacy*
- Sweeney, L. (2002). *k-anonymity: a model for protecting privacy*. IJUFKS
- Preregistration: Open Science Framework — https://osf.io/prereg
- arXiv submission guidelines — https://arxiv.org/help/submit
- DPDP Act 2023 (India) — https://www.meity.gov.in/content/digital-personal-data-protection-act-2023
- CC BY 4.0 — https://creativecommons.org/licenses/by/4.0/
