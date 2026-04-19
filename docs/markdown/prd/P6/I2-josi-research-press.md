---
prd_id: I2
epic_id: I2
title: "Josi Research Press — Peer-Reviewed Computational Astrology"
phase: P6-institution
tags: [#correctness, #experimentation]
priority: must
depends_on: [S4, Research, D7, I1]
enables: [I9, I11]
classical_sources: [bphs, saravali, phaladeepika, jaimini_sutras, tajaka_neelakanthi, kp_reader]
estimated_effort: 4 quarters (Year 3 Q2 through Year 4 Q2)
status: draft
author: "@claude"
last_updated: 2026-04-19
---

# I2 — Josi Research Press (Peer-Reviewed Publications)

## 1. Purpose & Rationale

Astrology has never had a credible, peer-reviewed research venue. Academic journals won't touch it; astrology associations publish house journals with no blinded review. The result: no reproducible claims, no cumulative knowledge, no bridge to adjacent research communities (statistics, anthropology, religious studies, cognitive science).

Josi — operating at 100M+ chart scale with cross-source agreement data, experimentation framework, and classical-rule registry — is uniquely positioned to found this venue. Josi Research Press publishes rigorous, reproducible, data-driven papers on computational astrology. First paper: *"Cross-Source Agreement on Raja Yogas Across 10M Charts."*

**Strategic value:**
- Category authority: peer-reviewed publishing cements Josi as the reference. Competitors become cite-ers.
- Data gravity: researchers join because Josi has the only dataset at this scale. Their findings compound back into the product.
- Regulatory precedent (I9): empirical findings create the basis for standard-of-practice debates.
- Acquisition signal (I11): published-research output is a defensible moat that appears in due-diligence data rooms.

## 2. Scope

### 2.1 In scope
- Editorial board of 7–11 members: mix of classical scholars, working astrologers, quantitative researchers (statistician, cognitive scientist).
- Double-blind peer review process, managed via open-source editorial software (Open Journal Systems or equivalent).
- Quarterly publication cadence: 4 papers per year minimum.
- Open-access (Creative Commons BY-NC-SA) for all accepted papers.
- IRB (institutional review board) process for all human-subjects data (via independent contracted IRB).
- Data / code availability requirements: reproducibility mandated for empirical papers.
- DOI registration via CrossRef or DataCite.
- Submission portal, reviewer management, production pipeline (LaTeX → PDF + HTML).
- Targeted Google Scholar indexing; application for indexing in DOAJ (Directory of Open Access Journals).
- Yearly conference (virtual at first; physical by Year 5): "Josi Research Symposium".

### 2.2 Out of scope
- Publishing Josi's own engine/product announcements (separate blog; don't muddy research authority).
- Paywalling research (open-access is strategic).
- Impact-factor pursuit via traditional indexes (slow, political; Google Scholar + DOAJ is sufficient initially).
- Predatory-journal behavior: no author fees in Years 1–2; no fast-track review for paying authors ever.

### 2.3 Dependencies
- **S4 (OLAP replication / ClickHouse)** — research queries run on analytical replica, not OLTP.
- **Research (Cross-source agreement dataset)** — first paper's dataset.
- **D7 (Research Data API)** — external researchers access anonymized data.
- **I1 (Academy)** — academic constituency + author pool.
- **IRB contract** with third party (no in-house IRB; conflict-of-interest).
- **Legal** — defamation, libel, research-ethics risk review per paper.

## 3. Classical / Technical Research

### 3.1 First paper — canonical structure

*"Cross-Source Agreement on Raja Yogas Across 10M Charts"*

- **Hypothesis**: Sources disagree on Raja Yoga identification in predictable ways; disagreement correlates with definition specificity in source text.
- **Method**: For 10M anonymized natal charts (opt-in users only, per D7 terms), compute Raja Yoga presence per source (BPHS, Saravali, Phaladeepika, Jataka Parijata). Agreement metric: Fleiss' κ per chart; aggregate by yoga, by source pair.
- **Results**: Report agreement distribution, source-pair agreement matrix, yoga-level disagreement ranking.
- **Discussion**: Link high-disagreement yogas to textual ambiguity; propose disambiguation framework.
- **Data availability**: Aggregated anonymized statistics (not per-chart) published; reproducibility code on GitHub under `josi/research`.

This paper establishes the publication model: quantitative, reproducible, data-grounded, with classical textual engagement.

### 3.2 Ethical / statistical constraints

- Every paper with user-chart data requires prior IRB review and opt-in consent per D7.
- No re-identification permissible; minimum aggregation threshold (k ≥ 100 per published statistic).
- Multiple-comparisons correction required for any claims of significant effect (Benjamini-Hochberg or Bonferroni).
- Pre-registration encouraged; required for confirmatory (non-exploratory) studies from Year 2.

### 3.3 Peer review model

Double-blind. 3 reviewers per paper (2 quantitative/technical; 1 classical-content). Target time-to-first-decision: 60 days. Acceptance rate target: 30–40% (selective enough to matter; not so selective as to stall).

### 3.4 Alternatives considered

| Alternative | Rejected because |
|---|---|
| Partner with existing journal for astrology section | No existing venue; partnership negotiations slow. |
| White papers / blog posts under Josi brand | No credibility boost; doesn't build research community. |
| Closed-access subscription journal | Contradicts strategic openness; kills adoption. |
| Crypto / web3 "decentralized peer review" | Vaporware ecosystem; no reviewer pool. |

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| Publication cadence | 4/year → expandable to 8/year by Year 5 | Sustainable editorial bandwidth; quarterly rhythm. |
| Author fees | None Years 1–2; modest APC Year 3+ if costs demand | Access first; sustainability second. |
| Indexing priority | Google Scholar → DOAJ → Scopus (Year 5) | Progressive credentialing. |
| Editor-in-chief role | External academic hire (not Govind) | Independence of editorial voice. |
| Josi employees authoring | Permitted, with declared COI; cannot be sole author without external co-author for empirical papers using Josi data | Standard COI pattern for industry-affiliated venues. |
| Retraction policy | COPE (Committee on Publication Ethics) guidelines | Established standard. |

## 5. Component Design

### 5.1 New services / modules

```
src/josi/research/
├── editorial/
│   ├── submission.py          # Submission intake, metadata
│   ├── review_matching.py     # Assign reviewers (conflict detection)
│   ├── anonymization.py       # Strip author identifiers for blind review
│   └── production.py          # LaTeX compile, DOI mint
├── data_access/
│   ├── reproducibility.py     # Paper ↔ dataset ↔ code provenance
│   └── aggregation_guard.py   # Enforce k-anonymity floor
└── indexing/
    └── crossref.py            # DOI registration
```

Editorial management may lean on **Open Journal Systems** (OJS, open-source from PKP) integrated via API; we do not build a full editorial CMS from scratch.

### 5.2 Data model additions

```sql
CREATE TABLE research_submission (
  submission_id UUID PK, title TEXT, abstract TEXT,
  corresponding_author_id UUID, status TEXT,
  submitted_at TIMESTAMPTZ, decided_at TIMESTAMPTZ NULL
);

CREATE TABLE research_reviewer_assignment (
  submission_id FK, reviewer_user_id FK,
  invited_at, accepted_at NULL, completed_at NULL,
  recommendation TEXT, review_body TEXT,
  PRIMARY KEY (submission_id, reviewer_user_id)
);

CREATE TABLE research_paper (
  paper_id UUID PK, submission_id FK UNIQUE,
  doi TEXT UNIQUE, published_at TIMESTAMPTZ,
  license TEXT, pdf_url TEXT, html_url TEXT,
  data_availability_statement TEXT,
  code_repo_url TEXT NULL,
  retracted_at TIMESTAMPTZ NULL, retraction_notice TEXT NULL
);

CREATE TABLE research_dataset_provenance (
  paper_id FK, dataset_fingerprint TEXT,
  query_hash TEXT, k_anonymity_floor INT,
  generated_at TIMESTAMPTZ
);
```

### 5.3 API / interface

```
POST /api/v1/research/submissions
GET  /api/v1/research/papers                # public catalog
GET  /api/v1/research/papers/{doi}
GET  /api/v1/research/data/{paper_id}       # bundled tables, csv/json
```

Authoring portal at `https://research.josi.com/`; public reading at `https://research.josi.com/papers/{doi-slug}`.

## 6. User Stories

### US-I2.1: As a PhD student researching astrological accuracy, I want anonymized aggregate data on cross-source yoga agreement
**Acceptance:** via D7 + Josi Research Press reproducibility bundle, I download aggregate CSV; documentation explains k-anonymity floor and aggregation method.

### US-I2.2: As an editor-in-chief, I want to manage submission/review lifecycle without manual email tracking
**Acceptance:** OJS-backed dashboard shows all open submissions; automated reviewer reminders; anonymized file distribution.

### US-I2.3: As a classical-content scholar on the editorial board, I want to review papers where my expertise applies
**Acceptance:** review-matching assigns by declared expertise + conflict-of-interest check; reviewer workload ≤ 4 papers/year default.

### US-I2.4: As a working astrologer, I want to cite empirical findings in consultations with clients
**Acceptance:** every paper has a layperson summary + citeable DOI; marketplace UI (D4) can link a reading to supporting research.

### US-I2.5: As a privacy-conscious Josi user, I want assurance that my chart data cannot be linked back to me in any published paper
**Acceptance:** k ≥ 100 floor enforced at query time; research ethics statement in every paper; external audit attestation annually.

### US-I2.6: As an acquirer (I11) performing due diligence, I want evidence of Josi's research moat
**Acceptance:** paginated index of published papers with citation counts (via Google Scholar API); retraction-free record.

## 7. Tasks

### T-I2.1: Editorial board recruitment
- **Definition:** Recruit editor-in-chief + 7–10 board members across classical + quantitative specialties.
- **Acceptance:** Signed engagement letters; conflict-of-interest policies executed.
- **Effort:** Q1–Q2.

### T-I2.2: Editorial infrastructure (OJS + Josi integration)
- **Definition:** Deploy OJS; integrate SSO with Josi auth; wire submission portal.
- **Acceptance:** End-to-end submission → review → decision workflow passes with test paper.
- **Effort:** Q1–Q2.

### T-I2.3: IRB contracting + policies
- **Definition:** Contract external IRB; document review scope; create IRB-submission templates for Josi-data papers.
- **Acceptance:** IRB approves first study (paper #1); policies published.
- **Effort:** Q1.

### T-I2.4: First paper — dataset, code, draft
- **Definition:** Internal team authors *"Cross-Source Agreement on Raja Yogas"* with reproducible code on GitHub.
- **Acceptance:** Accepted for peer review (submit to own venue with independent reviewers outside Josi payroll).
- **Effort:** Q2.

### T-I2.5: DOI registration + CrossRef membership
- **Definition:** CrossRef member agreement; DOI minting automation.
- **Acceptance:** Paper #1 receives real DOI; resolves correctly.
- **Effort:** Q2.

### T-I2.6: Public reading site
- **Definition:** Next.js site at research.josi.com; paper pages with PDF + HTML versions; schema.org markup.
- **Acceptance:** Google Scholar indexes papers within 60 days of publication.
- **Effort:** Q2–Q3.

### T-I2.7: Reproducibility enforcement
- **Definition:** Pipeline that validates dataset fingerprint + code repo on every accepted paper; blocks publication without.
- **Acceptance:** Third-party re-runs reproducibility bundle for paper #1 and reproduces results within 5%.
- **Effort:** Q3.

### T-I2.8: Annual symposium
- **Definition:** Plan + execute first virtual symposium; 8–12 talks.
- **Acceptance:** ≥ 300 live attendees; recordings published.
- **Effort:** Q3–Q4.

### T-I2.9: DOAJ indexing application
- **Definition:** Submit for Directory of Open Access Journals inclusion.
- **Acceptance:** Acceptance or documented reason for rejection with remediation plan.
- **Effort:** Q4.

### T-I2.10: Ongoing editorial operations
- **Definition:** Sustainable editorial cadence; 4 papers/year.
- **Acceptance:** Year 4 Q2: 8 total published papers; time-to-decision median ≤ 75 days.
- **Effort:** Continuous.

## 8. Unit Tests

### 8.1 Submission workflow tests
| Test category | Representative names | Success target |
|---|---|---|
| Anonymization | `test_reviewer_never_sees_author_identity` | 0 leaks in 100 anonymization passes; red-team manual check quarterly |
| COI detection | `test_coi_reviewer_excluded_from_assignment` | 100% of reviewer-author shared-org/shared-paper relations blocked |
| Decision latency | `test_time_to_first_decision_distribution` | p50 ≤ 60 days; p90 ≤ 90 days |

### 8.2 Data availability / reproducibility tests
| Test category | Representative names | Success target |
|---|---|---|
| k-anonymity floor | `test_published_stat_enforces_k_100` | 100% of published aggregates have k ≥ 100 |
| Dataset fingerprint | `test_paper_dataset_fingerprint_matches_published` | 100% of papers link to immutable dataset artifact |
| Code reproducibility | `test_paper_code_runs_to_published_result` | ≥ 95% of quantitative papers reproduce within 5% on fresh env |

### 8.3 DOI / citation indexing tests
| Test category | Representative names | Success target |
|---|---|---|
| DOI resolves | `test_doi_resolves_to_paper_page` | 100% uptime on DOI resolution |
| Scholar indexing | `test_paper_indexed_in_google_scholar_within_60d` | ≥ 90% of papers indexed |
| Citation tracking | `test_citation_count_sync_from_scholar` | Daily sync success ≥ 99% |

### 8.4 Editorial integrity tests
| Test category | Representative names | Success target |
|---|---|---|
| Retraction workflow | `test_retracted_paper_shows_prominent_retraction` | 100% of retracted papers show notice above fold |
| Version control | `test_paper_versions_immutable_after_publication` | 0 silent edits detected in audit log |
| COPE compliance | `test_policies_map_to_cope_guidelines` | Annual external audit passes |

### 8.5 Scholarly impact tests (longitudinal)
| Test category | Representative names | Success target |
|---|---|---|
| Citations by Year 5 | `test_journal_cumulative_citations` | ≥ 100 citations across all papers by Year 5 |
| External author share | `test_non_josi_first_author_share` | ≥ 50% of Year 4+ papers have non-Josi first authors |

## 9. EPIC-Level Acceptance Criteria

- [ ] Editorial board seated and operational.
- [ ] First paper published with real DOI.
- [ ] 4 papers published in Year 3 launch year.
- [ ] 100% of published papers reproducibility-bundled + IRB-cleared (where applicable).
- [ ] Google Scholar indexes all published papers within 60 days.
- [ ] Annual symposium executed with ≥ 300 attendees.
- [ ] DOAJ acceptance (or remediation plan).
- [ ] Zero retractions in Year 1 (aspirational; anti-metric if forced).
- [ ] At least 50% of Year 4 papers have non-Josi-employed first authors.
- [ ] Citations across papers cumulatively ≥ 100 by Year 5.

## 10. Rollout Plan

**Gate 0 — Editorial setup (Year 3 Q2):**
- Feature flag: internal only; editorial dashboard accessible to board.
- **Gate to proceed:** all board members engaged; IRB contracted.

**Gate 1 — First paper submission (Year 3 Q3):**
- Internal paper enters external review.
- **Gate to proceed:** 3 reviewer decisions returned within 75 days.

**Gate 2 — Public launch (Year 3 Q4):**
- research.josi.com live; first paper published.
- **Gate to proceed to full quarterly cadence:** second paper (external first-author) completes review.

**Gate 3 — External author predominance (Year 4–5):**
- Open submissions; active editorial outreach.
- **Success indicator:** Year 4 has ≥ 50% external first-authors.

**Rollback:** research.josi.com remains accessible even if new paper pipeline pauses; published DOIs must never be de-resolved. If operation becomes untenable, transfer archive to institutional partner (Internet Archive Scholar as safety net).

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Perception as "pay-to-publish" venue | Medium | Catastrophic | No APCs Years 1–2; conspicuously rigorous review; external editor-in-chief. |
| Reviewer pool too small | High | High | Expand via I1 Academy alumni + academic outreach; pay reviewers modest honoraria. |
| Privacy breach via re-identifiable stats | Low | Catastrophic | Automated k-floor enforcement; pre-publication privacy review; external audit. |
| Retraction of first paper (methodological error) | Medium | High | Rigorous internal review before submission; transparent retraction if needed. |
| Editorial board conflict / public resignation | Medium | High | Clear editorial charter; term limits; escalation path. |
| IRB rejects a paper after publication | Low | Catastrophic | No publication without prior IRB clearance. |
| Indexing (DOAJ/Scholar) rejects journal | Medium | Medium | Pre-apply checklist; fallback to Scholar-only indexing Year 1. |
| Astrology stigma keeps credible academics out | High | Medium | Position as "computational study of classical knowledge traditions"; emphasize quantitative methods. |
| Conference (symposium) fails to attract audience | Medium | Low | Virtual-first, recorded; low fixed costs; tie to I1 Academy launch calendar. |
| Legal risk: defamation / negligence claims on predictive papers | Low | High | Editorial scope excludes medical/legal/financial prediction claims; disclaimers per paper. |

## 12. References

- Master spec: `docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`
- Related PRDs: D7, Research, S4, I1, I9, I11
- COPE (Committee on Publication Ethics): `publicationethics.org`
- Open Journal Systems: `pkp.sfu.ca/ojs/`
- CrossRef membership: `crossref.org`
- DOAJ: `doaj.org`
- Benjamini, Y., & Hochberg, Y. (1995). *Controlling the false discovery rate.*
