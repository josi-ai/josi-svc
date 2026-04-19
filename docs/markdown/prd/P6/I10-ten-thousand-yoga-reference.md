---
prd_id: I10
epic_id: I10
title: "The 10,000-Yoga Reference Set"
phase: P6-institution
tags: [#correctness, #i18n, #extensibility]
priority: should
depends_on: [E4b, Reference-1000, P3-E2-console, I1, I3, S4]
enables: [I2, I5]
classical_sources: [bphs, saravali, phaladeepika, jataka_parijata, jaimini_sutras, tajaka_neelakanthi, nadi_texts, regional_tamil, regional_bengali, modern_commentary]
estimated_effort: 6+ quarters (Year 4 through Year 5+, ongoing)
status: draft
author: "@claude"
last_updated: 2026-04-19
---

# I10 — The 10,000-Yoga Reference Set

## 1. Purpose & Rationale

By P2 (E4b), Josi's Classical Yoga Engine covers ~250 core yogas. By P4 (Reference-1000), it expands to 1000. I10 completes the long tail: the **definitive global catalogue of every named yoga across every major classical astrology text**, with citations to verse, cross-source agreement analysis, and likely more yogas than have ever been assembled in one place.

The 10,000 target is ambitious but tractable:
- BPHS alone enumerates 300+ named yogas.
- Saravali, Phaladeepika, Jataka Parijata, Horasara, etc. each add hundreds more (many overlapping, many distinct).
- Regional Tamil, Bengali, Kannada, Telugu commentarial traditions contain thousands of additional yogas rarely cross-indexed.
- Nadi texts (Agastya, Bhrigu, etc.) reference hundreds of specialized yogas.
- Jaimini tradition yogas (karaka yogas, arudha yogas) add several hundred.
- Tajaka yogas add more.
- Modern commentarial (B.V. Raman, K.N. Rao, etc.) contribute codified extensions.

Cumulative plausible: 5000 well-cited + several thousand regional / obscure / synonymic = the 10,000 target.

**Strategic value:**
- Unmatched reference asset: nothing comparable exists in any language.
- Academic credibility: citation-indexed, cross-source-analyzed catalogue is a research artifact.
- Product depth: any yoga a user hears of, Josi recognizes and explains.
- Publishable research (I2): cross-source agreement analysis itself is a paper.
- I1 Academy use: master-level curriculum draws from this.
- Open-source asset (I3): makes `josi-classical-engine` the de facto standard.

## 2. Scope

### 2.1 In scope
- Aggregate cataloguing of named yogas from classical, regional, and credible modern sources.
- Each yoga entry includes:
  - Canonical name + aliases.
  - Source citations (verse-level where possible).
  - Formal rule (YAML in I3 registry) per source.
  - Cross-source agreement notes.
  - Classical-era attribution + tradition.
  - Practical application notes.
  - Localized names in original language + transliteration.
- Editorial standards: no unverified yogas; deprecation path for dubious entries.
- Community contribution via I3 (external scholars submit PRs).
- Rule authoring console (P3-E2-console) for non-engineer scholars.
- Public catalogue interface (browsable, searchable, filter by tradition / source / life-domain).
- Cross-source agreement analytics dashboard (S4 analytical replica).
- Integration into chart readings: "This chart activates 47 of 10,000 catalogued yogas per BPHS (28 active in consensus)."
- At least 3 I2 papers published on the catalogue (methodology, cross-source analysis, regional yoga statistics).
- Attribution and co-authorship for contributing scholars.

### 2.2 Out of scope
- Inventing novel yogas (that's I4; different provenance chain).
- Private / paywalled yogas (incompatible with I3 OSS commitment).
- Per-yoga UI widgets for every entry (most are reference-only; only high-relevance yogas get widgets).
- Completeness claim ("we have ALL yogas") — we claim "most comprehensive and systematically cross-indexed", never "all".
- Astrological-interpretation authority (we catalog; we don't adjudicate).

### 2.3 Dependencies
- **E4b (Full 250 yoga engine)** — baseline.
- **Reference-1000** — 1000-yoga expansion.
- **P3-E2-console** — authoring UI for non-engineers.
- **I1 (Academy)** — Master-level graduates contribute.
- **I3 (OSS engine)** — public repo for rule YAMLs.
- **S4 (OLAP / ClickHouse)** — cross-source analytics.
- **I2 (Research Press)** — publication venue.
- **Editorial team** — classical-content scholars as full-time + contract staff.
- **Text digitization partnerships** — libraries with rare manuscripts (need licensing).
- **Translation capacity** for regional texts.

## 3. Classical / Technical Research

### 3.1 Source prioritization (tiers)

| Tier | Sources | Estimated yogas |
|---|---|---|
| A — Core Parashari | BPHS, Saravali, Phaladeepika, Jataka Parijata, Horasara | ~1500 after dedup |
| B — Jaimini + Tajaka | Jaimini Sutras, Tajaka Neelakanthi, Varshatantra | ~800 |
| C — Regional commentarial | Tamil (Sukar Nadi, Olai-suvadi), Bengali (Siddhanta Siromani commentaries), Telugu, Kannada | ~2500 |
| D — Nadi texts | Agastya, Bhrigu, Chandra Kala nadi | ~1500 (highly redundant; careful dedup) |
| E — Modern commentarial | B.V. Raman, K.N. Rao, Sanjay Rath, P.V.R. Narasimha Rao, many | ~1500 |
| F — Regional obscure | Small-circulation texts, modern compilations | ~2000 |

Target: 10,000 unique yogas after dedup + alias consolidation. Likely reach 7000–9000; we stop at "comprehensive" rather than "10,000 at any cost."

### 3.2 Yoga entry schema

```yaml
yoga_id: bhadra_pancha_mahapurusha
canonical_name:
  sanskrit: "भद्र पञ्च महापुरुष योग"
  iast: "Bhadra Pañca Mahāpuruṣa Yoga"
  english: "Bhadra (Mercury) Mahapurusha Yoga"
aliases:
  - Bhadra Yoga
  - Mercury Pancha Mahapurusha
tradition: parashari
categories: [raja_yoga, pancha_mahapurusha]
life_domains: [intellect, communication, wealth, longevity]
sources:
  - source_id: bphs
    citation: "BPHS Ch.36 v.7"
    rule_yaml_path: "rules/yogas/bphs/bhadra.yml"
  - source_id: saravali
    citation: "Saravali Ch.35 v.12–14"
    rule_yaml_path: "rules/yogas/saravali/bhadra.yml"
cross_source_notes: "All core sources agree on Mercury in own/exaltation sign and in kendra; Saravali adds strength qualifier."
practical_notes: "Gives intellectual prowess, communication, wealth via business. Confers 'Bhadra'-type Mahapurusha constitution."
see_also: [ruchaka, hamsa, malavya, shasha]
first_catalogued_by: bphs
first_added_to_josi: 2026-03-01
contributors: [govind, scholar_a, scholar_b]
```

### 3.3 Dedup + alias consolidation

Many yogas exist under multiple names across texts. E.g., "Parijata Yoga" in Saravali ≈ "Kusuma Yoga" in regional Tamil. Dedup strategy:
1. Canonical rule matching: compute the rule's canonical form (hashed); duplicates cluster.
2. Manual curation: classical scholar resolves ambiguous clusters.
3. Alias table preserves all names; canonical yoga ID chosen deterministically.

### 3.4 Cross-source agreement analysis

For each yoga identified in multiple sources, compute:
- Boolean presence across sources.
- Definition equivalence (strict / partial / contested).
- Chart-level presence correlation across sources.

Publishable as an I2 paper (Josi's "Cross-Source Agreement" theme extended from the first P4 paper).

### 3.5 Digitization + translation pipeline

Many target sources are:
- Out of print.
- Untranslated from Tamil / Bengali / Kannada / Telugu / classical Sanskrit.
- In deteriorating condition (palm-leaf, rare manuscripts).

Approach:
- Partner with libraries (Adyar Library, Oriental Research Institute Mysore, Saraswati Mahal Thanjavur, etc.) for access.
- OCR + classical-Sanskrit NLP (where available).
- Human translator corps (contracted scholars fluent in source + English).
- Legal: public-domain for pre-20th-century texts; licensing for modern commentarial.

### 3.6 Alternatives considered

| Alternative | Rejected because |
|---|---|
| Stop at 1000 (Reference-1000) | Leaves the long-tail untouched; no comprehensive asset. |
| Crowdsource without editorial review | Quality catastrophe; unreliable catalogue. |
| Keep catalogue proprietary | Contradicts I3 OSS commitment; kills adoption. |
| Outsource entirely to one partner | Partner-bus-factor risk; editorial control lost. |

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| Numerical target | "Comprehensive" > 5000 at quality; stretch 10,000 | Quality over quantity branding. |
| Editorial rigor | Dual review per yoga: code (engineer) + classical (scholar) | Matches F6 rigor. |
| Language scope at launch | Sanskrit, Tamil, Bengali, Kannada, Telugu, English | Covers South Asian traditions; expand later. |
| Licensing strategy | CC BY-SA for catalogue text; Apache 2.0 for rule YAMLs (matches I3) | Open, with attribution. |
| Contributor recognition | Co-author on each entry + annual contributors list in I2 | Recognition matters; attracts scholars. |
| Nadi-text ethical concerns (some texts claim personal "scripted" content) | Catalog only the general-logic yogas from nadi, not claimed personal scripts | Respect + legitimacy. |
| Release cadence | Rolling; major milestones (3000, 5000, 7500, 10000) announced | Progress-visibility; momentum. |
| Redundancy handling | Aliases preserved; canonical yoga ID chosen | Serves search + respects sources. |

## 5. Component Design

### 5.1 New services / modules

```
src/josi/yoga_catalogue/
├── curation/
│   ├── dedup.py
│   ├── alias_consolidation.py
│   └── editorial_queue.py
├── analytics/
│   ├── agreement.py
│   └── coverage.py
├── ingestion/
│   ├── ocr_pipeline.py
│   └── translation_workflow.py
└── publication/
    └── catalogue_render.py

# Existing code extended:
src/josi/engine/yoga_engine.py   # Already from E4a/E4b; no change needed

# Content lives in I3 repo:
josi-classical-engine/rules/yogas/<tradition>/<source_id>/*.yml
josi-classical-engine/catalogue/yogas/*.yml  # metadata entries
```

### 5.2 Data model additions

Catalogue metadata goes in `classical_rule` (existing) plus:

```sql
CREATE TABLE yoga_catalogue_entry (
  yoga_id TEXT PK,
  canonical_name_json JSONB,
  aliases JSONB,
  tradition TEXT,
  categories TEXT[],
  life_domains TEXT[],
  first_catalogued_source_id TEXT,
  first_added_to_josi DATE,
  editorial_status TEXT, -- 'draft','reviewed','published','deprecated'
  deprecated_reason TEXT NULL
);

CREATE TABLE yoga_catalogue_source_link (
  yoga_id FK, source_id FK,
  citation TEXT, rule_id_ref TEXT, -- links to classical_rule
  notes TEXT,
  PRIMARY KEY (yoga_id, source_id)
);

CREATE TABLE yoga_catalogue_contributor (
  yoga_id FK, contributor_id FK, role TEXT,
  contributed_at TIMESTAMPTZ,
  PRIMARY KEY (yoga_id, contributor_id, role)
);
```

### 5.3 API contract

```
GET  /api/v1/catalogue/yogas                   # paginated, searchable
GET  /api/v1/catalogue/yogas/{yoga_id}
GET  /api/v1/catalogue/yogas/{yoga_id}/agreement   # cross-source
GET  /api/v1/catalogue/stats                    # counts, coverage
POST /api/v1/catalogue/yogas                    # via P3-E2-console (auth-gated)
```

## 6. User Stories

### US-I10.1: As a classical scholar, I want to look up any named yoga and find its primary source citations
**Acceptance:** search by name (any language) → entry with sources, aliases, rule, cross-source notes.

### US-I10.2: As an Academy Master-level student, I want to contribute a regional yoga from my lineage
**Acceptance:** authoring console flow; dual review; attribution preserved; merged within 30 days.

### US-I10.3: As a PhD researcher, I want to download the full catalogue with cross-source agreement data
**Acceptance:** CC BY-SA download; machine-readable JSON/YAML; reproducible analytics bundle.

### US-I10.4: As a Josi Ultra user reading my chart, I want to see which yogas apply beyond the common ones
**Acceptance:** chart reading includes "rare yogas activated" section with expandable entries; each links to catalogue page.

### US-I10.5: As a Tamil-language astrologer, I want Tamil-named yogas accessible in Tamil
**Acceptance:** full catalogue entries in Tamil with transliteration to English + Sanskrit.

### US-I10.6: As an I2 editor, I want the catalogue methodology as a paper
**Acceptance:** paper submitted and peer-reviewed; describes provenance, dedup, editorial standards.

### US-I10.7: As a competing astrology tool, I want to adopt Josi's yoga catalogue
**Acceptance:** free adoption via I3; CC BY-SA on catalogue text; Apache 2.0 on rules; attribution required.

## 7. Tasks

### T-I10.1: Scale editorial team
- **Definition:** Hire 3–5 full-time classical-content editors + contract 20+ translators/scholars.
- **Acceptance:** Team + contracts in place.
- **Effort:** Q1.

### T-I10.2: Library / text-source partnerships
- **Definition:** Access agreements with major libraries + text digitization.
- **Acceptance:** ≥ 3 library partnerships; first manuscripts digitized.
- **Effort:** Q1–Q2.

### T-I10.3: Ingestion pipeline (OCR + translation workflow)
- **Definition:** OCR for Devanagari + Tamil + Bengali; translation ticketing; quality control.
- **Acceptance:** 100 source-texts ingested and drafted through pipeline.
- **Effort:** Q2.

### T-I10.4: Dedup + alias consolidation logic
- **Definition:** Canonical-rule hashing + manual-resolution UI.
- **Acceptance:** 1000 candidate yogas processed with ≥ 95% correct dedup rate (vs expert label).
- **Effort:** Q2.

### T-I10.5: Public catalogue UI
- **Definition:** Browsable web catalogue; search; filters; localized names.
- **Acceptance:** Lighthouse accessibility ≥ 90; Playwright happy paths.
- **Effort:** Q2–Q3.

### T-I10.6: Authoring console for scholars
- **Definition:** P3-E2-console-based contribution flow with editorial queue.
- **Acceptance:** First 50 scholar-authored entries merged.
- **Effort:** Q3.

### T-I10.7: Analytics dashboard
- **Definition:** Cross-source agreement + coverage visualizations.
- **Acceptance:** Live dashboard; research-ready data export.
- **Effort:** Q3.

### T-I10.8: Milestone announcements (3000, 5000, 7500 entries)
- **Definition:** Coordinated releases with I3 major versions; press + I2 features.
- **Acceptance:** Milestones hit and announced.
- **Effort:** Q3–Year 5.

### T-I10.9: Cross-source agreement paper in I2
- **Definition:** Methodology + headline findings paper.
- **Acceptance:** Paper accepted.
- **Effort:** Year 5 Q1.

### T-I10.10: Ongoing curation operations
- **Definition:** Editorial SLAs, deprecation workflow, community moderation.
- **Acceptance:** Monthly release cadence; response-time SLAs met.
- **Effort:** Continuous.

## 8. Unit Tests

### 8.1 Catalogue-coverage tests
| Test category | Representative names | Success target |
|---|---|---|
| Milestone counts | `test_catalogue_size_at_release_N` | 3000 by Year 4 Q4; 5000 by Year 5 Q2; 7500 by Year 5 Q4; 10000 aspirational |
| Source-tier coverage | `test_bphs_coverage_complete` | ≥ 95% of BPHS-named yogas present |
| Language-specific coverage | `test_tamil_regional_yoga_presence` | ≥ 500 Tamil-regional yogas by Year 5 |

### 8.2 Dedup + alias tests
| Test category | Representative names | Success target |
|---|---|---|
| Dedup correctness | `test_known_aliases_cluster` | ≥ 95% correct on labeled set |
| Canonical ID stability | `test_canonical_id_stable_across_releases` | 100% stability after first publication |
| Alias retrieval | `test_search_by_alias_returns_canonical` | 100% |

### 8.3 Rule-integrity tests
| Test category | Representative names | Success target |
|---|---|---|
| Rule YAML validity | `test_every_catalogue_entry_has_valid_rule_yaml` | 100% |
| Citation integrity | `test_every_source_link_has_citation` | 100% |
| Compute on golden charts | `test_catalogue_rules_execute_on_golden_charts` | 100% of rules compute without error |

### 8.4 Editorial-workflow tests
| Test category | Representative names | Success target |
|---|---|---|
| Dual review | `test_new_entry_requires_engineer_and_scholar_approval` | 100% |
| Deprecation workflow | `test_deprecated_entry_excluded_from_default` | 100% |
| Contributor attribution | `test_every_entry_preserves_contributor` | 100% |

### 8.5 Cross-source agreement tests
| Test category | Representative names | Success target |
|---|---|---|
| Agreement computation | `test_agreement_stats_correct_on_synthetic_data` | 100% |
| Publication consistency | `test_published_stats_match_computed` | 100% |

### 8.6 Publication / API tests
| Test category | Representative names | Success target |
|---|---|---|
| Full-download integrity | `test_cc_bysa_download_round_trips` | 100% integrity |
| Search performance | `test_catalogue_search_p99_latency` | p99 ≤ 500ms at full scale |

## 9. EPIC-Level Acceptance Criteria

- [ ] Editorial team scaled and operational.
- [ ] Library + text partnerships signed.
- [ ] Ingestion + translation pipeline processing > 100 entries per month.
- [ ] ≥ 5000 yoga entries published by Year 5 Q4.
- [ ] ≥ 10,000 aspirational; minimum "comprehensive" >  5000 with quality gates preserved.
- [ ] Public catalogue UI live, localized into at least 4 languages.
- [ ] Authoring console used by external scholars; ≥ 50 external-scholar contributions merged.
- [ ] Cross-source agreement dashboard live; at least 2 I2 papers published.
- [ ] All rule YAMLs merged into I3 OSS repo.
- [ ] Deprecation workflow exercised and documented.

## 10. Rollout Plan

**Gate 0 — Team + partnerships (Year 4 Q1):**
- Staffing + library MOUs.
- **Gate to proceed:** staffing signed; at least 1 library partnership.

**Gate 1 — Pipeline operational (Year 4 Q2):**
- OCR + translation + editorial workflow.
- **Gate to proceed:** 100 entries through pipeline.

**Gate 2 — 3000-entry milestone (Year 4 Q4):**
- Public announcement; press + I2 feature.
- **Gate to proceed:** catalogue UI stable; search performant.

**Gate 3 — 5000-entry milestone (Year 5 Q2):**
- Includes first regional-source wave (Tamil).
- **Gate to proceed:** external scholar contributions ≥ 50.

**Gate 4 — 7500 and 10,000 milestones (Year 5 Q4 and beyond):**
- Rolling; continues past Year 5.

**Rollback plan:** catalogue is additive; rolling back a release is unusual. For individual entry errors, deprecation (soft) rather than deletion (hard). OSS repo releases follow SemVer.

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Low-quality contributions pollute catalogue | High | High | Dual editorial review; classical advisor veto; deprecation workflow. |
| Translation errors distort yoga definitions | High | High | Multi-translator review for ambiguous passages; back-translation spot checks. |
| Library / text access blocked | Medium | High | Multiple partnerships; focus on public-domain first; legal fund for access advocacy. |
| Dedup errors collapse distinct yogas | Medium | High | Human curation on all auto-dedup clusters; versioned canonical IDs. |
| Copyright claims on modern commentarial | Medium | Medium | Legal review; license or exclude; default to public-domain sources. |
| Nadi-text ethical disputes (personalized-script claims) | Medium | Medium | Catalog only general-logic; explicit scope statement. |
| Regional community objections to cataloguing their tradition | Medium | Medium | Community-representative editorial board; opt-in / respect preferences. |
| Cost overruns from translation + editorial | High | Medium | Phased funding; milestone-based contracts. |
| Search / infra performance at full scale | Medium | Medium | OLAP replica + indexing; progressive loading UI. |
| 10,000-entry target becomes vanity metric driving quality erosion | High | High | Quality gates enforced at every milestone; public willingness to say "comprehensive at 6500"; pivot from number-chasing. |
| Contributors feel under-recognized and stop contributing | Medium | Medium | Clear attribution; co-author on I2 papers; annual recognition. |
| Catalogue used by competitors without attribution | Low | Low | CC BY-SA enforces attribution; community norms. |
| Deep political disputes between tradition advocates (e.g., which Jaimini school is authoritative) | Medium | Medium | Inclusivity: catalog both; cross-source notes explain; scholar panel mediates. |

## 12. References

- Master spec: `docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md` — §1.5 (yoga coverage depth).
- Related PRDs: E4b, Reference-1000, P3-E2-console, I1, I3, I2, S4, I5
- Primary sources: BPHS, Saravali, Phaladeepika, Jataka Parijata, Horasara, Jaimini Sutras, Tajaka Neelakanthi, Nadi texts (Agastya, Bhrigu), regional commentaries.
- Modern commentarial: B.V. Raman's yoga compilations, K.N. Rao's tutorials, P.V.R. Narasimha Rao's lectures, Sanjay Rath's Jaimini materials.
- Library partners target: Adyar Library, Saraswati Mahal Thanjavur, Oriental Research Institute Mysore, Bhandarkar Oriental Research Institute.
