---
prd_id: D9
epic_id: D9
title: "Enterprise tier (temples, corporate wellness, matchmaking) — white-label classical rule sets"
phase: P5-dominance
tags: [#multi-tenant, #extensibility, #astrologer-ux]
priority: should
depends_on: [P4-E4-tenant, F1, F6, E12, D8]
enables: [D11]
classical_sources: [bphs, saravali, muhurta_chintamani, ashtakoota]
estimated_effort: 12-16 weeks
status: draft
author: "@agent"
last_updated: 2026-04-19
---

# D9 — Enterprise Tier

## 1. Purpose & Rationale

Josi's architecture (multi-tenant by default, YAML-driven classical rules, per-tenant rule overrides via P4-E4) enables an enterprise product almost for free. Three initial vertical customers:

1. **Hindu temples** — ritual timing (muhurta), pooja scheduling, jyotish services as part of temple offerings. Tirumala, Rameshwaram, Vaishnodevi, ISKCON-scale audiences.
2. **Corporate wellness** — HR departments offering "astro-wellness" benefits (anonymized, opt-in for employees) alongside meditation apps.
3. **Matchmaking platforms** — existing sites (Shaadi, Jeevansathi, BharatMatrimony) want Ashtakoota compatibility + modern AI interpretation integrated; current homegrown jyotish is weak and unmaintained.

Value per customer:
- Guaranteed SLA (vs. consumer tier)
- Per-tenant classical rule overrides (some temples use lineage-specific variants)
- White-label (their brand)
- Dedicated support + solutions engineering
- API volume pricing

## 2. Scope

### 2.1 In scope
- Enterprise plan SKU (contract, not self-serve)
- Per-tenant rule override catalog (P4-E4 payoff) with audit
- White-label: custom logo, color scheme, domain, email templates, API banner
- Three initial verticals with ready-to-go configurations:
  - **Temple Pack**: muhurta activities catalog (prana pratishtha, vivaha, upanayana, etc.), panchang push API, Hindi/Sanskrit/Tamil outputs → companion to D11
  - **Corporate Wellness Pack**: anonymized employee access, benefits-portal SSO, aggregate dashboards (no individual PII), meditation-adjacent framing
  - **Matchmaking Pack**: Ashtakoota API + AI interpretation blend, integration templates for leading matchmaking sites, GDPR/DPDP data-residency options
- Dedicated SLA tiering: 99.9% uptime; 4-hour response for critical
- Audit log exported per tenant on request
- Per-tenant data residency (India region required for some temple / matchmaking customers)
- Contract + usage metering; invoicing
- Solutions-engineering onboarding playbook

### 2.2 Out of scope
- Full on-premises deployment (Josi remains SaaS; a P6 option)
- Dedicated tenant cluster (pooled with strong isolation in P5; dedicated in P6)
- Custom AI-interpretation fine-tuning per tenant (interpretation model is shared; only rules differ)
- Product UI customization beyond theme (no bespoke UX builds in P5)

### 2.3 Dependencies
- P4-E4-tenant per-tenant rule overrides
- F1 source_authority; F6 rule DSL
- E12 Astrologer Workbench (for temple priest-facing use)
- D8 Certification (matchmaking partners may demand certified astrologers behind the AI)
- Data-residency infra (Cloud SQL in `asia-south1` for Indian tenants)

## 3. Technical Research

### 3.1 Multi-tenancy isolation

Our existing `organization_id` partitioning gives row-level isolation. Enterprise requires stronger guarantees:
- **Strong isolation tier:** dedicated DB roles; rate-limit quotas; error-budget monitoring per tenant
- **Per-tenant encryption keys** (envelope): KMS keys per enterprise tenant; their data re-encrypted with their key; deletion verifiable
- **Per-tenant audit log stream** to their preferred destination (Splunk, Datadog, custom S3)

### 3.2 Rule override mechanics

Leveraging P4-E4-tenant: an enterprise customer registers a `tenant_rule_override_set` containing YAML rules that override the global set. Overrides are additive OR substitutive depending on customer need:
- **Additive** (more common): customer adds lineage-specific yogas on top of core set
- **Substitutive**: customer replaces specific rule versions (e.g., temple uses a particular commentary's muhurta criteria)

### 3.3 Data residency

Indian matchmaking customers + temple customers often require data-in-India. Cloud SQL `asia-south1` region; application in same region. Routing via tenant-region field in organization record.

### 3.4 Billing and usage metering

- Unit: API calls, consultations, AI interpretation tokens, voice minutes
- Per-tenant meter flushed hourly to billing DB
- Stripe invoicing or direct bank transfer for large enterprise
- Usage overage alerts configurable

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| Self-serve vs sales-led | Sales-led (minimum $20k/year commit) for Enterprise; Pro tier handles smaller orgs | Onboarding cost; white-label complexity |
| Dedicated vs pooled infra | Pooled with isolation controls in P5; dedicated option in P6 | Cost + velocity |
| Allow tenant to run custom AI | No — shared model; rule-set is the differentiator | Model-governance risk |
| Data-residency options | Start with `asia-south1` + `us-central1`; EU in P6 | Focus on launch markets |
| Tenant branding depth | Theme + logo + email; not full skin | Scope; avoid per-tenant UI drift |
| Tenant-level rule override governance | Advisor-reviewed at activation; tenant can author but Josi approves | Quality moat |

## 5. Component Design

### 5.1 New modules

```
src/josi/enterprise/
├── tenant_onboarding/
│   ├── wizard.py
│   ├── provisioner.py              # SSO, API keys, rule-set seeding
│   └── playbooks/                  # solutions engineering scripts per vertical
├── rule_overrides/                 # extends P4-E4
│   ├── tenant_override_set.py
│   └── activation.py
├── white_label/
│   ├── theme.py
│   ├── email_templates.py
│   └── domain_router.py
├── billing/
│   ├── metering.py
│   ├── invoicing.py
│   └── alerts.py
├── audit/
│   └── export.py                    # tenant-level audit stream export
├── packs/
│   ├── temple/                      # Temple Pack defaults
│   ├── corporate_wellness/
│   └── matchmaking/
└── sla/
    └── monitor.py                   # per-tenant SLO tracking
```

### 5.2 Data model additions

```sql
CREATE TABLE enterprise_tenant (
    tenant_id            UUID PRIMARY KEY REFERENCES organization(organization_id),
    plan                 TEXT CHECK (plan IN ('enterprise_core','enterprise_premium')),
    vertical             TEXT CHECK (vertical IN ('temple','corporate_wellness','matchmaking','other')),
    data_region          TEXT NOT NULL,
    sla_tier             TEXT,
    kms_key_id           TEXT,
    white_label_theme    JSONB,
    contract_uri         TEXT,
    activated_at         TIMESTAMPTZ,
    renewal_at           TIMESTAMPTZ
);

CREATE TABLE enterprise_audit_stream (
    tenant_id            UUID PRIMARY KEY REFERENCES enterprise_tenant(tenant_id),
    destination_type     TEXT,       -- 'splunk','datadog','s3','none'
    destination_config   JSONB,
    last_exported_at     TIMESTAMPTZ
);

CREATE TABLE enterprise_usage (
    tenant_id            UUID NOT NULL,
    meter                TEXT NOT NULL,      -- 'api_calls','voice_minutes','ai_tokens',...
    hour                 TIMESTAMPTZ NOT NULL,
    count                BIGINT NOT NULL,
    PRIMARY KEY(tenant_id, meter, hour)
);

CREATE TABLE enterprise_alert (
    alert_id             UUID PRIMARY KEY,
    tenant_id            UUID NOT NULL,
    kind                 TEXT NOT NULL,
    triggered_at         TIMESTAMPTZ NOT NULL,
    resolved_at          TIMESTAMPTZ,
    details              JSONB
);
```

### 5.3 API contract

```
# Admin APIs (Josi-internal)
POST /admin/enterprise/onboard  { org_id, vertical, plan, data_region, ... }
POST /admin/enterprise/{id}/activate-overrides  { override_set_id }
POST /admin/enterprise/{id}/audit-export       { destination }

# Enterprise-customer APIs
GET  /api/v1/enterprise/usage?since=...
GET  /api/v1/enterprise/alerts
GET  /api/v1/enterprise/audit?range=...
POST /api/v1/enterprise/theme  { logo_url, colors, fonts }
```

## 6. User Stories

### US-D9.1: As a temple IT admin, I onboard in under 5 business days
**Acceptance:** onboarding wizard + solutions engineer playbook guides from contract → activated tenant; 5-day SLA measurable.

### US-D9.2: As a matchmaking CTO, I integrate Ashtakoota API with 10 lines of code
**Acceptance:** SDK + docs + example; integration test green in sandbox.

### US-D9.3: As a temple head priest, my lineage's muhurta criteria override the default
**Acceptance:** tenant override set applied; advisor approval recorded; usage reflects overrides.

### US-D9.4: As a corporate HR, employee queries are anonymized in aggregate dashboards
**Acceptance:** dashboard shows aggregates with n ≥ 20; no individual identification possible.

### US-D9.5: As an enterprise tenant, I get audit log export to our Splunk
**Acceptance:** configured once; daily export; verified in Splunk; signed log integrity.

### US-D9.6: As an enterprise tenant, my data resides in India
**Acceptance:** tenant flagged `data_region=asia-south1`; infra isolated; DPDP compliance documented.

### US-D9.7: As a Josi ops engineer, per-tenant SLO monitoring lets me respond before breach
**Acceptance:** dashboard per tenant; burn-rate alerts; response playbook.

## 7. Tasks

### T-D9.1: Tenant onboarding wizard + provisioner
- **Definition:** Wizard that provisions API keys, SSO, KMS envelope, theme, rule overrides, data-region pinning.
- **Acceptance:** onboarding completes in < 5 business days avg for pilot customers.
- **Effort:** 3 weeks

### T-D9.2: Temple Pack (muhurta catalog + panchang push API + Tamil/Hindi/Sanskrit outputs)
- **Definition:** Pre-configured activities (prana pratishtha, vivaha, ...); push API for daily muhurta; multilingual templates.
- **Acceptance:** 1 temple pilot running; panchang accuracy vs. reference; priest-team sign-off.
- **Effort:** 4 weeks (shared with D11)

### T-D9.3: Matchmaking Pack (Ashtakoota API + AI interpretation + integration SDK)
- **Definition:** Ashtakoota scoring API (with mangal dosha variants); AI-interpretation endpoint; SDK in JS/Python.
- **Acceptance:** 1 matchmaking partner integrated in sandbox; < 200ms P95 latency.
- **Effort:** 3 weeks

### T-D9.4: Corporate Wellness Pack (SSO + aggregate dashboard)
- **Definition:** SAML/OIDC SSO; anonymized aggregate dashboard with k-anon enforcement.
- **Acceptance:** 1 corporate pilot; HR dashboard accurate; no individual identification possible.
- **Effort:** 3 weeks

### T-D9.5: Per-tenant rule override activation + advisor review
- **Definition:** Tenant authors YAML; Josi advisor reviews; activation with audit log.
- **Acceptance:** 10 lineage overrides reviewed + activated; advisor SLA 2 weeks.
- **Effort:** 2 weeks

### T-D9.6: White-label theming
- **Definition:** Theme config, logo upload, email template override, custom domain.
- **Acceptance:** pilot tenant's theme live; emails branded.
- **Effort:** 2 weeks

### T-D9.7: Billing + metering + invoicing
- **Definition:** Hourly meter flush; overage alerts; Stripe or direct invoicing.
- **Acceptance:** accounting reconciles; alerts fire at configured thresholds.
- **Effort:** 3 weeks

### T-D9.8: Per-tenant SLO monitoring + burn-rate alerts
- **Definition:** Per-tenant dashboards; burn-rate alerting; response runbook.
- **Acceptance:** dashboards populated; alerts triggered in synthetic load test.
- **Effort:** 2 weeks

### T-D9.9: Audit log export
- **Definition:** Stream to Splunk/Datadog/S3; signed integrity.
- **Acceptance:** export arrives hourly; signature verifies.
- **Effort:** 1.5 weeks

### T-D9.10: Data-residency infra
- **Definition:** `asia-south1` deployment; tenant-region routing.
- **Acceptance:** tenant traffic never leaves configured region; DPDP audit passes.
- **Effort:** 3 weeks (infra-heavy)

## 8. Unit Tests

### 8.1 Tenant isolation
- Category: cross-tenant reads blocked; rule overrides scoped.
- Target: 100% isolation; pen-test green.
- Representative: `test_cross_tenant_chart_read_blocked`, `test_tenant_override_not_visible_to_other`.

### 8.2 Rule override activation
- Category: overrides apply correctly; advisor approval gate.
- Target: activation without approval rejected.
- Representative: `test_override_requires_advisor_approval`, `test_additive_override_merged`, `test_substitutive_override_replaces`.

### 8.3 Metering accuracy
- Category: per-meter count correctness.
- Target: 100% count match to synthetic load.
- Representative: `test_api_call_metered`, `test_voice_minute_rounded_up`, `test_hourly_flush_atomic`.

### 8.4 Data residency
- Category: tenant data stays in configured region.
- Target: 100% compliance; any cross-region access blocked.
- Representative: `test_asia_south_tenant_no_us_reads`, `test_region_routing_correct`.

### 8.5 SSO (SAML/OIDC)
- Category: federation correctness.
- Target: valid tokens accepted; expired/tampered rejected.
- Representative: `test_saml_valid_assertion`, `test_oidc_tampered_token_rejected`.

### 8.6 Audit export
- Category: stream integrity and completeness.
- Target: no missing events; signature verifies.
- Representative: `test_audit_completeness_vs_oltp`, `test_signature_verification`.

### 8.7 Corporate-pack aggregate k-anon
- Category: n < 20 cells suppressed.
- Target: 100% enforcement.
- Representative: `test_small_cell_suppressed`.

### 8.8 White-label theming
- Category: theme applied to UI + emails; no cross-tenant leak.
- Target: pixel-diff vs template.
- Representative: `test_custom_logo_rendered`, `test_email_template_branded`.

## 9. EPIC-Level Acceptance Criteria

- [ ] 3 pilot customers (1 temple, 1 corporate, 1 matchmaking) live and contract-bound
- [ ] SLA tier (99.9%) met in pilot period
- [ ] Per-tenant rule overrides activated with advisor sign-off
- [ ] Billing + invoicing reconciles
- [ ] Data-residency `asia-south1` verified
- [ ] Audit export live per tenant
- [ ] Onboarding SLA ≤ 5 business days
- [ ] Documentation: enterprise handbook + per-pack guides

## 10. Rollout Plan

- **Feature flag:** `enterprise_tier`.
- **Phase 1 (4 weeks):** sales identifies 5 pilot candidates per vertical; 3 signed LOIs.
- **Phase 2 (8 weeks):** pilot onboarding; 1 customer per vertical live.
- **Phase 3 (4 weeks):** iterate on playbooks; second-wave customers.
- **Phase 4:** GA; press release; sales scaling.
- **Rollback:** flag off blocks new enterprise onboarding; pilots grandfathered on existing infra.

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Long sales cycles stall rollout | High | Medium | Pipeline of multiple verticals in parallel |
| Over-customization blows up scope | High | High | Packs define allowable customization; bespoke features denied |
| SLA breach in pilot | Medium | Very High | Per-tenant SLO alerting; response playbook rehearsed |
| Data-residency regulatory shifts (DPDP amendments) | Medium | Medium | Legal review quarterly; architecture pre-built for region adds |
| Tenant rule overrides degrade quality | Medium | High | Advisor-approval gate; regression tests per override |
| Cross-tenant data leak via override misconfig | Low | Very High | Mandatory override isolation tests; bi-annual pen test |
| Matchmaking partner demands SLA Josi can't meet | Medium | High | Scoped SLA in contract; premium tier offers dedicated option |
| Temple customer disputes interpretation outputs | Medium | Medium | Classical advisor escalation channel in contract |

## 12. References

- Master spec: `docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`
- Related PRDs: P4-E4-tenant (override infra), F1/F6 (rule engine), E12 (workbench), D8 (cert), D11 (temple muhurta API)
- Regulatory: DPDP Act (India); GDPR (EU for P6); HIPAA-adjacent concerns for corporate wellness
