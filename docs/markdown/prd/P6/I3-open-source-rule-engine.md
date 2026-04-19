---
prd_id: I3
epic_id: I3
title: "Open-Source the Rule Engine (Apache 2.0)"
phase: P6-institution
tags: [#extensibility, #correctness]
priority: must
depends_on: [F6, F8, F13, P3-E2-console, Reference-1000]
enables: [I9, I10, I11, D10]
classical_sources: []
estimated_effort: 3 quarters (Year 3 Q2 through Year 3 Q4) plus ongoing stewardship
status: draft
author: "@claude"
last_updated: 2026-04-19
---

# I3 — Open-Source the Rule Engine (Apache 2.0)

## 1. Purpose & Rationale

By Year 3, Josi's classical rule engine will be the most comprehensive codification of classical astrology logic ever built. The engine consists of: the rule DSL (F6), YAML rule files (E4a/E4b + Reference-1000), the aggregation protocol (F8), the aggregation strategies A/B/C/D, the content-hash provenance chain (F13), the correctness harness (E15a), and output-shape validation (F7).

The master spec explicitly states: **"Closed-source classical rules… we never publish, we publish it commercially. Commercial moat is the AI layer + data, not the rule definitions."** I3 operationalizes that commitment.

**Strategic rationale (non-obvious):**
- A proprietary rule registry invites reimplementation; an open-source registry becomes the *standard*. Competitors either conform (ratifying Josi's conventions) or build incompatible systems (paying a fragmentation tax).
- Community contributions accelerate rule coverage beyond what any one team can author (aligns with I10).
- Regulatory body (I9) needs a neutral, non-proprietary rule corpus to reference.
- Research credibility (I2) requires reproducibility, which requires open algorithms.
- Enterprise / government procurement (D9, I7) routinely blocks closed-source in sensitive domains.
- Josi's commercial moat shifts to **AI layer + data at scale + hosting** — defensible, and stronger than rule secrecy.

## 2. Scope

### 2.1 In scope
- Extract rule engine from monorepo into a standalone repository `github.com/josi/josi-classical-engine`.
- Apache 2.0 license with contributor license agreement (CLA) for contributions.
- All rule YAMLs (Reference-1000 minimum) + DSL loader + engine + 4 aggregation strategies + content-hash + output-shape schemas.
- Golden test suite (subset sharable, redacted of any PII) published.
- Python package published on PyPI: `pip install josi-classical-engine`.
- Governance model: Technical Steering Committee (TSC) of 5 (3 Josi + 2 external initially; inverted by Year 5).
- Apache Software Foundation (ASF) incubation proposal filed by Year 4.
- Documentation site: `docs.josi-classical-engine.org`.
- Contribution guide, code of conduct, security policy (SECURITY.md), roadmap.
- Release cadence: SemVer, monthly minor; rule-file updates (data) on their own lifecycle.
- Josi-hosted service continues to use the same engine; fork-ahead is avoided by vendoring from the OSS repo.

### 2.2 Out of scope
- Open-sourcing the AI orchestration layer (LLM prompts, chat UX, Claude integration) — commercial moat.
- Open-sourcing user-level serving infrastructure (chart_reading_view materialization, caching, experiment allocation) — operational, not algorithmic.
- Open-sourcing marketplace, billing, auth, or any PII-touching service.
- Liberal open licensing (MIT/BSD) — Apache 2.0 explicitly chosen for patent grant.
- Dual licensing / copyleft (AGPL) — friction for enterprise adoption.

### 2.3 Dependencies
- **F6 (Rule DSL / YAML loader)** — already structured for portability.
- **F8 (TechniqueResult + Aggregation Protocol)** — the public interface the engine exposes.
- **F13 (Content-hash provenance)** — required for reproducibility claim.
- **P3-E2-console (Rule authoring console)** — community contribution UI.
- **Reference-1000 (expanded yoga set)** — critical mass of rules at launch.
- **Legal**: patent review across all engine code; redaction of any proprietary hooks; CLA process.
- **Community team**: at minimum 1 FTE developer advocate.

## 3. Classical / Technical Research

### 3.1 Why Apache 2.0 specifically

| License | Rejected because |
|---|---|
| MIT | No patent grant (material risk if patents asserted). |
| BSD-3 | Same patent issue; marginally different from MIT. |
| AGPL / GPL | Enterprise poison pill; forces downstream opens; blocks marketplace adoption. |
| MPL-2.0 | File-level copyleft confuses contributors; uncommon in Python ecosystem. |
| Apache 2.0 | **Selected.** Patent grant, permissive, ASF-compatible, enterprise-friendly, Python-ecosystem-standard. |

### 3.2 What's separable vs. what's not

Not every internal module is a clean OSS candidate. The boundary must be drawn precisely:

**Open-sourced:**
- DSL grammar + YAML loader
- RuleEngine (Layer 2: per-source compute)
- AggregationStrategy Protocol + A/B/C/D implementations (Layer 3)
- Output-shape schemas + validator
- Content-hash provenance functions
- YAML rule files (all of Reference-1000 + E4b full 250)
- Golden chart suite (subset, with birth data redacted or synthesized)
- Differential test harness against JH/Maitreya (as a reusable CLI)

**Closed-source:**
- Chart-engine integration specifics (how Josi calls the engine from `chart_service.py`)
- Caching layer (Layer 1 Redis)
- Serving mart materialization worker
- Experiment allocation wiring
- Any user/tenant-aware code
- Any AI-prompt code

### 3.3 Governance model (ASF incubation target)

- **Benevolent Dictator for Life** not viable — category-creation requires neutrality.
- **Steering Committee (TSC)** — 5 voting members at launch (3 Josi employees, 2 external). Seats rotate on 2-year terms. By Year 5, majority external.
- **Committer** tier — review/merge privilege, earned by sustained contribution.
- **Rule Authoring Advisory Board** — classical-content reviewers (distinct from code committers) required for rule YAML changes; enforces citation quality.
- Voting by lazy consensus (ASF-style), with formal votes for releases and governance changes.
- Conflict of interest: Josi employees on TSC recuse from votes affecting Josi-specific interests; external TSC members do not.

Target: Apache Software Foundation incubation application filed by Year 4 Q1; graduation to top-level ASF project by Year 5 or 6.

### 3.4 Sustainability

- Josi funds 1 FTE developer advocate + 0.5 FTE release manager ongoing (commitment, budgeted).
- Seek additional sponsors (potential: universities with computational-humanities programs, open-source-supportive tech companies).
- Optional: foundational grant (e.g., Sloan Foundation, Mozilla Open Source Support Fund).

### 3.5 Alternatives considered

| Alternative | Rejected because |
|---|---|
| Publish under source-available (BSL) | Defeats standardization goal; enterprise still blocks. |
| Dual-license (AGPL + commercial) | Marketing nightmare; defeats community signal. |
| Keep closed; publish "reference" Markdown | Half-measure; no reproducibility; no contribution. |
| Open-source everything including AI layer | Destroys moat without added community value. |

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| License | Apache 2.0 | Patent grant + enterprise + ASF path. |
| CLA required | Yes, individual CLA (similar to Apache ICLA) | Future relicense flexibility; patent clarity. |
| Corporate contributions | CCLA required | Standard OSS hygiene. |
| Who owns copyright on merged code | Contributor retains; Josi has broad license via CLA | Respects contributor rights; enables project continuity. |
| TSC seat distribution at launch | 3 Josi / 2 external; flipping by Year 5 | Bootstrap credibility; long-term neutrality. |
| Rule YAML contribution process | Via P3-E2-console or PR; dual review (code + classical) | Enforce citation quality. |
| Can OSS engine version diverge from Josi-hosted? | No — Josi vendors from OSS release; bugs/patches upstream first | Prevents fork-ahead drift. |
| Security disclosure process | Standard coordinated disclosure; `security@josi-classical-engine.org` | Basic OSS hygiene. |

## 5. Component Design

### 5.1 Repository layout

```
josi-classical-engine/                    # new public GitHub repo
├── LICENSE                                # Apache 2.0
├── NOTICE
├── README.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md                     # Contributor Covenant
├── SECURITY.md
├── GOVERNANCE.md                          # TSC model
├── pyproject.toml                         # PyPI package config
├── src/josi_classical/
│   ├── __init__.py
│   ├── dsl/                               # extracted from F6
│   ├── engine/                            # extracted from F8
│   ├── aggregation/                       # A/B/C/D strategies
│   ├── shapes/                            # output shapes
│   ├── provenance/                        # content-hash
│   └── rules/                             # YAML registry
├── tests/
│   ├── golden/                            # sharable golden charts
│   ├── property/                          # Hypothesis tests
│   └── differential/                      # JH/Maitreya harness
├── docs/                                  # Sphinx docs
└── tools/
    └── differential_cli.py
```

### 5.2 Public Python API

```python
# Public, stable, SemVer'd
from josi_classical import (
    RuleEngine,
    AggregationStrategy,
    load_rules,
    TechniqueResult,
)

engine = RuleEngine(rules_dir="./rules")
results = engine.compute(chart_data, source="bphs", technique_family="yoga")
aggregated = AggregationStrategy.D_hybrid.apply(results)
```

Internal APIs are explicitly marked `_private`.

### 5.3 Upstreaming flow (Josi-hosted ↔ OSS)

```
 Josi engineer edits rule YAML
      ↓
 PR to josi-classical-engine (OSS)
      ↓
 Classical advisor + code review
      ↓
 Merge + release minor version
      ↓
 Josi monorepo pins new version in pyproject.toml
      ↓
 Josi staging deploy; regression tests
      ↓
 Josi production
```

No hotfixes bypass OSS; exception: security issues follow coordinated disclosure with temporary vendored patch, then upstream.

### 5.4 Versioning

- Engine code: strict SemVer. Breaking API changes bump major.
- Rule YAMLs: content-addressable (content_hash) so consumers can pin exact rule versions independent of engine version.
- Rule "schema" (YAML shape) versioned separately; deprecations gated per F4.

## 6. User Stories

### US-I3.1: As a university researcher, I want to pip-install a battle-tested classical astrology engine
**Acceptance:** `pip install josi-classical-engine`; import; run Raja Yoga compute on a sample chart; matches Josi hosted output.

### US-I3.2: As a competing astrology platform, I want to adopt Josi's rule conventions without paying for Josi
**Acceptance:** free adoption of engine + rules; only commercial friction is at the AI / hosted-service layer if they want Josi's AI.

### US-I3.3: As an enterprise procurement officer for a temple network, I want to verify no closed-source dependencies on a security-audited rule engine
**Acceptance:** source available, Apache 2.0; third-party security audit (commissioned annually by Josi + sponsors) passes.

### US-I3.4: As a classical scholar in a non-English community, I want to contribute a rule set from my regional tradition
**Acceptance:** documented contribution flow via PR; classical advisory board reviews; merged rules ship in next release.

### US-I3.5: As a Josi engineer, I want rule changes to flow cleanly between OSS and hosted production
**Acceptance:** upstream-first policy enforced by CI; Josi monorepo pin auto-bumped via Dependabot.

### US-I3.6: As a member of the TSC, I want a clear vote-of-record mechanism
**Acceptance:** formal votes recorded in public `GOVERNANCE_LOG.md`; consensus process documented.

## 7. Tasks

### T-I3.1: Legal + patent review
- **Definition:** Counsel reviews every engine module for patent exposure; review CLA drafts.
- **Acceptance:** Clean bill from counsel; CLA (individual + corporate) templates ratified.
- **Effort:** Q1.

### T-I3.2: Monorepo → OSS repo extraction
- **Definition:** Extract listed modules into new repo; ensure tests pass standalone; no Josi-internal imports leak.
- **Acceptance:** Fresh clone + `pip install -e .` + `pytest` green on clean environment.
- **Effort:** Q1–Q2.

### T-I3.3: Documentation site
- **Definition:** Sphinx docs; tutorials; API reference; governance; contribution guide.
- **Acceptance:** Published at docs.josi-classical-engine.org; all examples tested.
- **Effort:** Q2.

### T-I3.4: Governance ratification
- **Definition:** Draft GOVERNANCE.md; seat initial TSC (5 members); code of conduct; security policy.
- **Acceptance:** All members signed; first public TSC meeting held with minutes.
- **Effort:** Q2.

### T-I3.5: PyPI release v1.0.0
- **Definition:** Release pipeline (GitHub Actions → PyPI via trusted publisher); signing; SBOM.
- **Acceptance:** `pip install josi-classical-engine==1.0.0` works on Python 3.12+.
- **Effort:** Q2.

### T-I3.6: Josi hosted service switches to OSS package
- **Definition:** Josi monorepo depends on `josi-classical-engine` via PyPI pin; internal modules deleted.
- **Acceptance:** Production regression tests all pass on OSS engine; cutover executed.
- **Effort:** Q2–Q3.

### T-I3.7: Community launch
- **Definition:** Blog post, HN launch, conference talk, outreach to adjacent communities (Python data-science, computational humanities, astrology forums).
- **Acceptance:** 500 GitHub stars in 60 days; 10 external PRs merged by Q4.
- **Effort:** Q3 (sustained).

### T-I3.8: ASF incubation application prep
- **Definition:** Drafts; sponsor mentor identification; meet ASF incubation bar.
- **Acceptance:** Application filed in Year 4 Q1.
- **Effort:** Q3–Q4 + Year 4.

### T-I3.9: Security + vulnerability disclosure process
- **Definition:** security@ address; PGP key; coordinated disclosure SLA.
- **Acceptance:** First third-party CVE-style report triaged within 72 hours.
- **Effort:** Q3.

### T-I3.10: Sponsor / grant outreach
- **Definition:** Pursue open-source grants (Sloan, Mozilla MOSS, Chan Zuckerberg).
- **Acceptance:** At least 1 grant or matching sponsor secured.
- **Effort:** Q3–Q4.

## 8. Unit Tests

Inherited tests (F6/F7/F8/F13/E15a) migrate with the code. New tests specific to OSS release:

### 8.1 Standalone-install tests
| Test category | Representative names | Success target |
|---|---|---|
| Fresh-env install | `test_pip_install_clean_env` | 100% success on Python 3.12, 3.13 / Linux, macOS, Windows |
| No hidden Josi deps | `test_no_josi_internal_imports` | grep-style lint passes on every release |
| SBOM generation | `test_sbom_generated_on_release` | SBOM present in every GH release artifact |

### 8.2 API stability tests (SemVer contract)
| Test category | Representative names | Success target |
|---|---|---|
| Public API surface snapshot | `test_public_api_unchanged_within_minor` | Any change to public API fails CI on non-major bump |
| Deprecation window | `test_deprecated_apis_warn_before_removal` | ≥ 2 minor versions between deprecation and removal |

### 8.3 Determinism / reproducibility tests
| Test category | Representative names | Success target |
|---|---|---|
| Bit-for-bit determinism | `test_same_input_same_output_across_runs` | 100% across 10k sample charts |
| Version pin parity | `test_engine_version_X_matches_josi_hosted_version_X` | Josi hosted vs OSS package: 0 differences on golden set |

### 8.4 Governance-process tests (non-code, but tracked)
| Test category | Representative names | Success target |
|---|---|---|
| CLA enforcement | `test_pr_without_cla_blocked_by_bot` | 100% block rate |
| TSC vote recording | `test_tsc_votes_in_public_log` | 100% of formal votes logged within 7 days |
| Rule YAML dual review | `test_rule_yaml_pr_requires_classical_reviewer` | 100% |

### 8.5 Community health tests (longitudinal)
| Test category | Representative names | Success target |
|---|---|---|
| External contributor growth | `test_external_pr_merge_rate` | ≥ 25% of merged PRs from non-Josi by Year 5 |
| Downstream adopters | `test_downstream_dependents_count` | ≥ 50 public repos depend on us by Year 5 (via deps.dev) |
| Release cadence | `test_release_cadence_sustained` | ≤ 5 weeks between minor releases on average |

## 9. EPIC-Level Acceptance Criteria

- [ ] Public GitHub repo with Apache 2.0 license, CLA bot, code of conduct, security policy.
- [ ] PyPI package `josi-classical-engine v1.0.0` published.
- [ ] Josi hosted service runs on exactly the same PyPI package version as OSS users.
- [ ] TSC seated with 5 members, at least 2 external.
- [ ] Documentation site live and accurate.
- [ ] 500+ GitHub stars within 60 days of launch.
- [ ] 10+ external-contributor PRs merged in first year.
- [ ] Third-party security audit commissioned and passed.
- [ ] ASF incubation application filed by Year 4.
- [ ] At least 1 sustainability grant or sponsor secured.

## 10. Rollout Plan

**Gate 0 — Private extraction (Year 3 Q2):**
- Feature flag: none (internal refactor).
- Extract engine to a private prerelease repo; Josi monorepo imports from it.
- **Gate to proceed:** all regression tests green on extracted package.

**Gate 1 — Friends-and-family release (Year 3 Q3):**
- Repo made public; v0.x releases on PyPI.
- Private outreach to ~20 researchers, partner schools, adjacent projects.
- **Gate to proceed:** 3 external users successfully install + run end-to-end without support tickets.

**Gate 2 — Public v1.0 launch (Year 3 Q4):**
- HN/Reddit/blog launch; press release.
- **Gate to proceed to ASF incubation:** 500 stars; 10 PRs; 50 issues triaged.

**Gate 3 — ASF incubation (Year 4):**
- File application; work through incubation mentorship.
- **Gate to graduation:** meet ASF criteria (3+ successful Apache-way releases, diverse committer base).

**Rollback plan:** the open-source release is irreversible (that's the point). If technical issues arise, respond with patch releases. If governance issues arise, follow TSC process. Josi hosted service's dependency can be rolled back to a prior PyPI version while OSS community stays on latest.

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Competitor forks engine + out-competes Josi on AI/hosting | Low-Medium | Medium | Commercial moat is AI + data + scale; engine is commodity by design. Embrace forks (they ratify Josi's conventions). |
| Community adopts but doesn't contribute (bus factor stays at Josi) | High | Medium | Actively mentor external committers; dev-advocate FTE; grants to external maintainers. |
| Classical-content contributors push low-quality or unverified rules | Medium | High | Dual review (code + classical); classical advisory board has veto. |
| Legal action by a source-text translator claiming copyright on rule paraphrase | Low | High | All rule bodies paraphrased from primary sources with citation; legal review pre-release. |
| Governance disputes fork the community | Low | High | Clear GOVERNANCE.md; ASF-style lazy consensus + formal vote procedure; COPE-style conflict resolution. |
| Security vulnerability discovered post-launch | Medium | Medium | SECURITY.md with disclosure SLA; CI security scanning (CodeQL, Dependabot). |
| Josi hosted diverges from OSS (secret fork-ahead) | Medium | Catastrophic (credibility) | Technical enforcement: Josi monorepo can only depend on PyPI-published versions; no path-dependency overrides allowed. |
| Patent troll asserts against OSS version | Low | High | Apache 2.0 patent grant + retaliation clause; Josi carries OSS indemnification insurance. |
| Low adoption (< 100 stars) | Low | Medium (optics) | Aggressive outreach; classical-content appeal to non-engineers via I1 Academy. |
| Maintenance burden overwhelms Josi FTE allocation | Medium | Medium | Committer tier grown over time; grant-funded maintainer positions; hard cap on Josi issue-response SLA. |
| Open-sourcing leaks architectural insight to acquirers (I11) | Low | Low | Engine is commodity; deal math centers on AI + data + user base. |

## 12. References

- Master spec: `docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md` — §7 non-goals explicitly permit/mandate open rule definitions.
- Related PRDs: F6, F7, F8, F13, E15a, P3-E2-console, Reference-1000, I9, I10, I11
- Apache License 2.0: `apache.org/licenses/LICENSE-2.0`
- Apache Software Foundation incubation: `incubator.apache.org`
- Contributor Covenant: `contributor-covenant.org`
- Python packaging guide: `packaging.python.org`
- "Open Source Strategy" (Simon Wardley): ecosystem-playbook framing.
