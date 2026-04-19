---
prd_id: P3-E2-console
epic_id: E2
title: "Rule authoring console for non-engineer classical astrologers"
phase: P3-scale-10m
tags: [#extensibility, #i18n, #astrologer-ux]
priority: should
depends_on: [F6, F16, P3-E6-flag]
enables: [Reference-1000]
classical_sources: []
estimated_effort: 3 weeks
status: draft
author: Govind
last_updated: 2026-04-19
---

# P3-E2-console — Rule Authoring Console

## 1. Purpose & Rationale

Classical rules live in YAML (F6). Engineers can author them, but Sanskrit-literate classical astrologers cannot: git, YAML syntax, and the F6 DSL are all friction. This bottleneck hurts three ways:

1. We cannot realistically push past ~500 rules when every addition requires an engineer + a classical advisor round-trip.
2. Our real domain experts (classical scholars) cannot contribute directly; we mediate.
3. Rule-quality iteration is slow — spotting a BPHS chapter-verse discrepancy, updating a YAML, and cutting a PR takes days.

This PRD introduces a **web-based rule authoring console** — a Next.js surface inside the Josi frontend that lets a Sanskrit-literate (but non-engineer) classical astrologer:

- Pick predicates from the F6 DSL vocabulary with **multilingual labels** (English, IAST, Devanagari, Tamil).
- Compose rules via structured form (not raw YAML).
- **Test the rule against golden charts** in a sandbox — "given Tendulkar's chart, does my rule activate?"
- See a live YAML preview (for learning + debugging).
- Submit the rule → **GitHub PR auto-opened** with the YAML change + metadata.
- **Never write directly to the DB** — PR review by engineers + classical advisors is the gate (aligns with P3-E6-flag staged rollout).
- Autocomplete BPHS / Saravali / Phaladeepika citations with verse search.
- Auto-increment semver on submit (patch bump default; minor/major on opt-in).

Outputs: a tool that converts the rate-limiting step of "scaling classical rules" from engineer bandwidth to classical-expert bandwidth. P3 target: 250+ rules co-authored by non-engineers. P4 target (Reference-1000): 1000-rule reference set.

## 2. Scope

### 2.1 In scope
- Web surface: `/admin/rules/console` — gated by `role=classical-advisor` or `role=admin`.
- Predicate picker UI: dropdown / search over F6 DSL vocabulary.
- Localized predicate labels: en / sa_iast / sa_devanagari / ta.
- Structured rule-body form: activation conditions, strength formula, details fields.
- Live YAML preview panel.
- Golden-chart sandbox: pick from 50 golden charts, click "Run", see activation + strength + details.
- Citation autocomplete: BPHS / Saravali / Phaladeepika structured index (chapter-verse with English+Sanskrit text snippets).
- Submit flow: validates → opens GitHub PR → returns PR URL.
- Read-only view of existing rules (browse by technique_family, filter, diff across versions).
- Audit log: who edited what, when.
- No direct DB write path — safety by design.

### 2.2 Out of scope
- Full rule DSL from-scratch authoring by UI-only users (complex cases still need YAML + engineer help; UI covers "most common rule shapes").
- Real-time collaborative editing (Google-Docs-style) — single author at a time.
- Automatic rule generation from source text ("parse BPHS 43.5-7 → rule") — AI-assisted, P5+.
- Web-based code-review UI — PRs reviewed on GitHub (or Atlassian if later).
- Non-classical-rule authoring (the console is limited to `classical_rule` table; extensions later).
- Offline authoring / desktop app.

### 2.3 Dependencies
- F6 — rule DSL YAML loader (defines the vocabulary we expose).
- F16 — golden chart suite (provides sandbox test charts).
- P3-E6-flag — all new rule versions enter shadow stage.
- Existing Next.js frontend with `@clerk/nextjs` auth.

## 3. Technical Research

### 3.1 Why a console, not a direct editor

We could let advisors edit YAML files directly via VS Code + git. Problems:

- Git / CLI is a hard barrier for non-technical users.
- YAML whitespace errors are a major source of rule bugs.
- No golden-chart test loop without setting up the whole dev environment.
- Raw DSL predicate names (`graha_in_kendra_from_lord_of`) are opaque to someone thinking in `केन्द्रस्थ` (kendrastha).

A console solves all four: form-based, validated, multilingual, with a live test runner.

### 3.2 Why PR-as-submission (not direct DB write)

Direct DB write would:
- Bypass code review.
- Bypass staged rollout (P3-E6-flag) if not careful.
- Make it hard to audit / revert.
- Conflict with our "rules live in YAML" invariant (F6).

PR-based submission:
- Engineers + other advisors review before merge.
- CI runs tests, including golden-chart suite.
- Merge triggers F6 loader, which enters the rule at `stage=shadow` (P3-E6-flag).
- Everything flows through the normal deploy pipeline.

### 3.3 Why multilingual labels

Sanskrit terms describe astronomical relationships precisely; English labels are often lossy or unstable. The console shows:

- `graha_in_kendra_from_lagna` — English: "Planet in kendra (1/4/7/10) from Ascendant"
- IAST: "graha kendre lagnāt"
- Devanagari: "ग्रह केन्द्रे लग्नात्"
- Tamil: "கிரகம் லக்னத்திலிருந்து கேந்திரத்தில்"

Advisor may think/speak in any of the four; UI surfaces all. Autocomplete matches across all.

### 3.4 Sandbox test loop

Clicking "Run sandbox" invokes a backend endpoint that:

1. Serializes the draft rule body to canonical YAML + content_hash.
2. Temporarily loads the rule (not persisted).
3. Invokes the appropriate family engine against the chosen golden chart with `force_rule_body=draft`.
4. Returns `{active, strength, details}` for display.

Latency budget: < 2s per test run.

### 3.5 Citation autocomplete

We ship a structured **verse index** (`docs/classical/verse_index/`):

```json
[
  {
    "source_id": "bphs",
    "citation": "BPHS 36.14-16",
    "chapter": 36,
    "verse_start": 14, "verse_end": 16,
    "title_en": "Gaja Kesari Yoga",
    "title_sa_iast": "gajakesarī yoga",
    "text_snippet_en": "When Moon and Jupiter are in mutual kendra...",
    "text_snippet_sa_iast": "candrō yadā kendragataḥ guroḥ..."
  },
  ...
]
```

Autocomplete searches over `title_*` and `text_snippet_*`. Selecting one populates the citation field in the rule.

Initial index: BPHS (~95 chapters), Saravali (~50 chapters), Phaladeepika (~28 chapters). Human-curated by classical advisors as part of this PRD's delivery.

### 3.6 Authz

- `role=classical-advisor`: can edit rules in technique_families the advisor owns (defined per advisor in `advisor_scopes` table).
- `role=admin`: can edit all.
- `role=user`: no access.

Authz enforced both in UI and backend. Audit log records every edit attempt.

### 3.7 Form vs YAML mode

Power users can toggle to **raw YAML mode** (text editor with validation + linting). Pre-fills from form state; on save, parses YAML and writes back into form state. Bidirectional sync for advanced editing.

### 3.8 Alternatives considered

| Alternative | Rejected because |
|---|---|
| VS Code remote web + git GUI | Still technical; exposure of repo internals unsafe |
| Pure YAML text editor | No validation, no sandbox; worse than status quo |
| Notion / Airtable export → converter | Data model mismatch; fragile |
| Monaco editor with JSON Schema | Better than plain text; still not a form experience |
| Fully-automated LLM rule drafting from source text | Premature; need advisor validation first |

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| Direct DB write or PR? | PR only | Safety + review + staged rollout |
| Form vs YAML | Form primary; YAML toggle for power users | Low barrier + escape hatch |
| Languages | en, sa_iast, sa_devanagari, ta | Covers advisor audiences |
| Sandbox chart set | 50 golden charts | Known provenance + diverse |
| Citation index scope | BPHS, Saravali, Phaladeepika | Foundational Parashari triad |
| Auth | Clerk role (classical-advisor); per-family scoping | Least-privilege |
| Versioning | Auto patch-bump; opt-in minor/major | Safe default |
| Draft persistence | Stored in `rule_draft` table until submit | Don't lose work on browser refresh |
| Tech stack | Next.js (existing); React Hook Form + Zod; Monaco for YAML | Fit with current codebase |
| Who can submit? | advisor scope enforced | Accountability |

## 5. Component Design

### 5.1 New modules

```
web/app/(dashboard)/admin/rules/console/
├── page.tsx                         # NEW: console landing
├── new/page.tsx                     # NEW: new-rule form
├── [rule_id]/page.tsx               # NEW: view/edit existing
└── components/
    ├── predicate-picker.tsx
    ├── rule-form.tsx
    ├── yaml-preview.tsx
    ├── sandbox-runner.tsx
    ├── citation-autocomplete.tsx
    ├── version-controls.tsx
    └── multilingual-label.tsx

web/lib/rule-console/
├── api-client.ts                    # NEW: console backend calls
├── dsl-vocabulary.ts                # fetches + caches F6 vocabulary
├── yaml-serializer.ts               # canonical YAML output
└── validation.ts                    # Zod schemas mirroring F6 DSL

src/josi/api/v1/controllers/
└── rule_console_controller.py       # NEW: POST /admin/rules/console/*

src/josi/services/rule_console/
├── __init__.py
├── draft_store.py                   # NEW: rule_draft CRUD
├── sandbox.py                       # NEW: invokes engine with draft rule
├── pr_opener.py                     # NEW: GitHub API PR creation
└── vocab_localizer.py               # NEW: multilingual label service

docs/classical/verse_index/
├── bphs.json
├── saravali.json
└── phaladeepika.json
```

### 5.2 Data model additions

```sql
-- Drafts (unsaved rule edits)
CREATE TABLE rule_draft (
    id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    author_user_id     UUID NOT NULL REFERENCES "user"(user_id) ON DELETE CASCADE,
    rule_id            TEXT,                   -- null for new rules
    source_id          TEXT NOT NULL,
    technique_family_id TEXT NOT NULL,
    output_shape_id    TEXT NOT NULL,
    draft_body         JSONB NOT NULL,
    draft_citation     TEXT,
    classical_names    JSONB NOT NULL DEFAULT '{}'::jsonb,
    base_version       TEXT,                    -- what existing version this edits; null = new
    bumped_version     TEXT,                    -- patch/minor/major bump
    created_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    submitted_at       TIMESTAMPTZ,
    submitted_pr_url   TEXT
);

CREATE INDEX idx_draft_author ON rule_draft(author_user_id, updated_at DESC);

-- Per-advisor family scope
CREATE TABLE advisor_scope (
    user_id             UUID NOT NULL REFERENCES "user"(user_id),
    technique_family_id TEXT NOT NULL REFERENCES technique_family(family_id),
    granted_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    granted_by          UUID REFERENCES "user"(user_id),
    PRIMARY KEY (user_id, technique_family_id)
);

-- Audit log (append-only)
CREATE TABLE rule_console_audit (
    id            BIGSERIAL PRIMARY KEY,
    user_id       UUID NOT NULL,
    action        TEXT NOT NULL CHECK (action IN
                    ('view','draft_create','draft_update','draft_delete',
                     'sandbox_run','submit_pr','submit_failed')),
    target_rule_id TEXT,
    details       JSONB,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### 5.3 Console API

```
# Backend (Python, FastAPI)
GET  /api/v1/admin/rules/console/vocabulary
     Returns DSL predicate catalog with multilingual labels
     Response: {predicates: [ {id, labels: {en, sa_iast, ...}, args: [...]}, ... ]}

GET  /api/v1/admin/rules/console/citations?q=gaja&source=bphs
     Citation autocomplete

GET  /api/v1/admin/rules/console/drafts
     Lists current user's drafts

POST /api/v1/admin/rules/console/drafts
     Create draft
     Body: { rule_id?, source_id, family_id, shape_id, draft_body, ... }
     Response: { draft_id }

PUT  /api/v1/admin/rules/console/drafts/{draft_id}
     Update draft

POST /api/v1/admin/rules/console/drafts/{draft_id}/sandbox
     Body: { chart_id: "golden-chart-tendulkar" }
     Response: { active, strength, details, latency_ms }

POST /api/v1/admin/rules/console/drafts/{draft_id}/submit
     Body: { version_bump: "patch"|"minor"|"major", pr_title, pr_description }
     Response: { pr_url, branch_name }
```

### 5.4 PR opener

```python
# src/josi/services/rule_console/pr_opener.py

async def open_rule_pr(
    draft: RuleDraft, user: User, version_bump: str,
    pr_title: str, pr_description: str,
) -> PRResult:
    gh = GithubClient(token=settings.GITHUB_RULE_CONSOLE_TOKEN)

    branch_name = f"rule-console/{user.user_id}/{draft.draft_id}"
    await gh.create_branch(base="main", name=branch_name)

    # Serialize draft to canonical YAML
    yaml_path = _yaml_path_for(draft)       # e.g., src/josi/db/seeds/classical/rules/yoga/raja/gaja_kesari.yaml
    yaml_content = canonical_yaml(draft, version_bump=version_bump)

    await gh.commit_file(
        branch=branch_name,
        path=yaml_path,
        content=yaml_content,
        message=f"feat(rule): {draft.rule_id or 'new'} by {user.email}",
        author=GitActor(name=user.full_name, email=user.email),
        co_author=GitActor(name="Josi Rule Console", email="console@josi.com"),
    )

    pr = await gh.open_pr(
        base="main", head=branch_name,
        title=pr_title or f"Rule: {draft.rule_id}",
        body=_pr_body(draft, pr_description, user),
        labels=["rule-console", draft.technique_family_id, "needs-classical-review"],
        reviewers=_classical_reviewers(draft.technique_family_id),
    )

    # Update draft row
    await _mark_submitted(draft, pr.url)
    return PRResult(pr_url=pr.url, branch=branch_name)
```

### 5.5 Sandbox

```python
# src/josi/services/rule_console/sandbox.py

async def run_sandbox(
    draft: RuleDraft, chart_id: UUID,
) -> SandboxResult:
    # Load chart (must be golden)
    chart = await _load_golden_chart(chart_id)
    if chart is None:
        raise HTTPException(400, "Chart must be from the golden suite")

    # Build a transient ClassicalRule instance (not persisted)
    transient_rule = ClassicalRule(
        rule_id=draft.rule_id or "sandbox_draft",
        source_id=draft.source_id, version="0.0.0-sandbox",
        technique_family_id=draft.technique_family_id,
        output_shape_id=draft.output_shape_id,
        rule_body=draft.draft_body,
        content_hash=sha256_canonical(draft.draft_body),
        effective_from=datetime.utcnow(),
    )

    # Invoke engine
    engine = get_engine_for_family(draft.technique_family_id)
    started = time.perf_counter()
    result = await engine.compute_transient(chart, transient_rule)
    latency_ms = int((time.perf_counter() - started) * 1000)

    return SandboxResult(
        active=result.get("active"),
        strength=result.get("strength"),
        details=result.get("details", {}),
        latency_ms=latency_ms,
        rule_body_hash=transient_rule.content_hash,
    )
```

### 5.6 Multilingual vocab

```python
# src/josi/services/rule_console/vocab_localizer.py

VOCAB_LABELS: dict[str, dict[str, str]] = {
    # Loaded from docs/classical/dsl_labels.json
    "graha_in_kendra_from_lagna": {
        "en": "Planet in kendra (1/4/7/10) from Ascendant",
        "sa_iast": "graha kendre lagnāt",
        "sa_devanagari": "ग्रह केन्द्रे लग्नात्",
        "ta": "கிரகம் லக்னத்திலிருந்து கேந்திரத்தில்",
    },
    "mutual_aspect_moon_jupiter": {
        "en": "Moon and Jupiter in mutual aspect",
        "sa_iast": "candra-guru parasparadṛṣṭi",
        "sa_devanagari": "चन्द्र-गुरु परस्परदृष्टि",
        "ta": "சந்திர-குரு பரஸ்பர திருஷ்டி",
    },
    # ... ~100 entries for initial DSL vocabulary
}
```

### 5.7 Frontend: console landing

```tsx
// web/app/(dashboard)/admin/rules/console/page.tsx

export default function RuleConsolePage() {
  const { data: drafts } = useQuery<RuleDraft[]>({...});
  const { data: rules } = useQuery<RuleListItem[]>({...});

  return (
    <div className="flex flex-col gap-6 p-6">
      <h1>Rule Console</h1>
      <Section title="My drafts">
        {drafts?.map(d => <DraftCard key={d.id} draft={d} />)}
        <Button href="/admin/rules/console/new">+ New Rule</Button>
      </Section>
      <Section title="Browse rules">
        <RuleBrowser rules={rules} />
      </Section>
    </div>
  );
}
```

### 5.8 Frontend: rule form

```tsx
// web/app/(dashboard)/admin/rules/console/components/rule-form.tsx

export function RuleForm({ draft, onChange }: Props) {
  const { data: vocab } = useVocabulary();
  const [mode, setMode] = useState<"form"|"yaml">("form");

  return (
    <div className="grid grid-cols-2 gap-6">
      <div>
        <ModeToggle mode={mode} onChange={setMode} />
        {mode === "form" ? (
          <>
            <PredicatePicker vocabulary={vocab} selected={draft.body.conditions} onChange={...} />
            <StrengthFormulaBuilder ... />
            <CitationAutocomplete value={draft.citation} onChange={...} />
            <ClassicalNamesFields names={draft.classical_names} />
            <VersionBumpSelector ... />
          </>
        ) : (
          <MonacoEditor value={yamlize(draft)} onChange={setDraftFromYaml} lang="yaml" />
        )}
      </div>
      <div>
        <YamlPreview draft={draft} />
        <SandboxRunner draft={draft} />
      </div>
    </div>
  );
}
```

### 5.9 Sandbox runner UI

```tsx
export function SandboxRunner({ draft }: { draft: RuleDraft }) {
  const [chartId, setChartId] = useState(GOLDEN_CHARTS[0].id);
  const { mutate, data, isLoading } = useMutation<SandboxResult, Error, string>({
    mutationFn: (chartId) =>
      apiClient.post<SandboxResult>(
        `/admin/rules/console/drafts/${draft.id}/sandbox`,
        { chart_id: chartId }
      ),
  });

  return (
    <div>
      <Select value={chartId} onChange={setChartId}>
        {GOLDEN_CHARTS.map(c => <Option key={c.id} value={c.id}>{c.label}</Option>)}
      </Select>
      <Button onClick={() => mutate(chartId)} disabled={isLoading}>
        Run Sandbox
      </Button>
      {data && (
        <ResultCard active={data.active} strength={data.strength} details={data.details} />
      )}
    </div>
  );
}
```

## 6. User Stories

### US-P3-E2-console.1: As a classical advisor, I can log in and see all rules in my assigned technique families
**Acceptance:** advisor with `advisor_scope=[yoga]` sees only yoga rules in the browser.

### US-P3-E2-console.2: I can start a new rule with predicates, see live YAML, and test against a golden chart — all without leaving the browser
**Acceptance:** form → YAML preview updates on every change; sandbox test returns result within 2s.

### US-P3-E2-console.3: I can pick a BPHS citation by searching for "gaja kesari"
**Acceptance:** autocomplete returns BPHS 36.14-16 with verse snippet in English and IAST.

### US-P3-E2-console.4: I can see predicate labels in Sanskrit Devanagari if I prefer
**Acceptance:** language toggle switches all predicate labels; IAST / Devanagari / English / Tamil all render correctly.

### US-P3-E2-console.5: When I click Submit, a GitHub PR opens with my YAML change and I get the URL
**Acceptance:** after submit, PR visible in repo; branch name follows pattern; reviewers auto-assigned; draft status marked submitted.

### US-P3-E2-console.6: I cannot directly write to the production DB
**Acceptance:** no backend endpoint exposes write path to `classical_rule` table; all mutations go via PR.

### US-P3-E2-console.7: As an admin, I can see audit log of all rule-authoring activity
**Acceptance:** admin UI shows who viewed / edited / submitted / ran sandbox; timestamps correct.

### US-P3-E2-console.8: A non-engineer advisor onboarded in 10 minutes can submit their first rule
**Acceptance:** usability test: 3 new advisors (non-engineer) onboarded; each submits a valid PR within 10 min of first login.

## 7. Tasks

### T-P3-E2-console.1: Data model migration
- **Definition:** `rule_draft`, `advisor_scope`, `rule_console_audit` tables per 5.2.
- **Acceptance:** migration applies; FKs enforced.
- **Effort:** 1 day
- **Depends on:** F2 complete

### T-P3-E2-console.2: DSL vocabulary endpoint with multilingual labels
- **Definition:** `GET /admin/rules/console/vocabulary` returns predicate catalog with labels in 4 languages. Authored label file at `docs/classical/dsl_labels.json` (initial ~100 entries).
- **Acceptance:** endpoint returns valid shape; labels non-empty for all 4 languages.
- **Effort:** 3 days (most time on label authoring with classical advisors)
- **Depends on:** F6 complete

### T-P3-E2-console.3: Citation autocomplete + verse index
- **Definition:** Build `bphs.json`, `saravali.json`, `phaladeepika.json` verse index (human-curated by classical advisors). Endpoint `GET /admin/rules/console/citations?q=...&source=...`.
- **Acceptance:** search "gaja kesari" returns BPHS 36.14-16 with snippet.
- **Effort:** 5 days (bulk of effort is human curation)
- **Depends on:** nothing

### T-P3-E2-console.4: Draft CRUD endpoints
- **Definition:** POST/GET/PUT/DELETE for drafts. Authz enforced.
- **Acceptance:** CRUD works; user can only access own drafts; admin sees all.
- **Effort:** 2 days
- **Depends on:** T-P3-E2-console.1

### T-P3-E2-console.5: Sandbox endpoint + engine transient compute
- **Definition:** `POST /drafts/{id}/sandbox`. Engines expose `compute_transient(chart, rule)` for sandbox invocation (no DB write).
- **Acceptance:** sandbox returns result within 2s P95; never writes to DB.
- **Effort:** 3 days
- **Depends on:** T-P3-E2-console.4, F16 complete, engine updates

### T-P3-E2-console.6: GitHub PR opener
- **Definition:** `pr_opener.py` per 5.4. Bot token `GITHUB_RULE_CONSOLE_TOKEN` in Secret Manager. Canonical YAML serializer.
- **Acceptance:** submit flow opens PR; PR contains exact expected YAML; reviewers assigned.
- **Effort:** 3 days
- **Depends on:** T-P3-E2-console.4

### T-P3-E2-console.7: Frontend: console landing + rule browser
- **Definition:** Next.js pages per 5.7. Uses existing auth + dashboard shell.
- **Acceptance:** authorized user sees list of drafts + rules; unauthorized 403.
- **Effort:** 2 days
- **Depends on:** T-P3-E2-console.2

### T-P3-E2-console.8: Frontend: rule form + predicate picker
- **Definition:** Form with multilingual labels, live validation, YAML preview panel.
- **Acceptance:** form renders; validation errors clear; YAML preview matches server canonical output.
- **Effort:** 5 days
- **Depends on:** T-P3-E2-console.2

### T-P3-E2-console.9: Frontend: sandbox runner + citation autocomplete
- **Definition:** Components per 5.8, 5.9.
- **Acceptance:** run sandbox → result rendered; autocomplete works with 300ms debounce.
- **Effort:** 3 days
- **Depends on:** T-P3-E2-console.5, T-P3-E2-console.3

### T-P3-E2-console.10: Frontend: YAML mode (Monaco)
- **Definition:** Monaco editor with YAML syntax + custom linter for F6 DSL.
- **Acceptance:** toggle switches modes; bidirectional state sync; lint errors inline.
- **Effort:** 2 days
- **Depends on:** T-P3-E2-console.8

### T-P3-E2-console.11: Audit log + admin view
- **Definition:** Audit writes on each action. Admin page showing filtered audit log.
- **Acceptance:** every action logged; admin view renders; filter by user/action/date works.
- **Effort:** 2 days
- **Depends on:** T-P3-E2-console.4

### T-P3-E2-console.12: Advisor onboarding flow + documentation
- **Definition:** `docs/markdown/guides/rule-console-advisor-onboarding.md`. Video walkthrough. Advisor grant API for admins.
- **Acceptance:** 3 advisors successfully onboarded; feedback incorporated.
- **Effort:** 3 days
- **Depends on:** T-P3-E2-console.10

### T-P3-E2-console.13: End-to-end tests (Playwright)
- **Definition:** E2E test: login as advisor → new rule → form fill → sandbox → submit → PR URL. Verify PR exists in test repo.
- **Acceptance:** test passes against test Github repo; < 60s runtime.
- **Effort:** 2 days
- **Depends on:** T-P3-E2-console.10

## 8. Unit Tests

### 8.1 Vocabulary localizer

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_label_returns_all_four_languages` | predicate_id=graha_in_kendra | dict with en, sa_iast, sa_devanagari, ta | completeness |
| `test_fallback_to_en_when_missing` | language=ta on entry with no ta | returns en + logs warning | graceful |
| `test_unknown_predicate_404` | unknown predicate_id | raises | safety |

### 8.2 Draft store

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_draft_create_scoped_to_user` | user A creates draft | row has author_user_id=A | ownership |
| `test_draft_list_returns_only_own` | user A lists | user B's drafts absent | isolation |
| `test_draft_update_rejected_for_other_user` | user B updates A's draft | 403 | authz |
| `test_admin_sees_all_drafts` | admin lists | all drafts returned | admin override |
| `test_submitted_draft_becomes_readonly` | update after submit | 409 conflict | immutability post-submit |

### 8.3 Sandbox

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_sandbox_returns_active_strength_details` | valid draft + golden chart | structured result | happy path |
| `test_sandbox_rejects_non_golden_chart` | random chart_id | 400 | safety |
| `test_sandbox_does_not_persist_rule` | run sandbox | no new `classical_rule` or `technique_compute` rows | safety |
| `test_sandbox_latency_under_2s` | typical yoga rule | < 2s | SLO |
| `test_sandbox_invalid_draft_body_returns_validation_error` | malformed predicate | 422 with path to bad field | UX |

### 8.4 PR opener

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_pr_opens_with_correct_branch_name` | draft by user X | branch `rule-console/{user_id}/{draft_id}` | convention |
| `test_pr_body_includes_author_and_citation` | submit | body contains user email + citation | attribution |
| `test_pr_reviewers_assigned` | yoga rule | yoga classical reviewers tagged | routing |
| `test_pr_version_bump_patch_default` | no bump specified | version = prev patch+1 | safe default |
| `test_pr_version_bump_minor_opt_in` | bump=minor | minor bumped, patch reset | explicit |
| `test_pr_yaml_is_canonical` | submit | YAML matches canonical format (sorted keys, stable) | reviewability |

### 8.5 Authz

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_advisor_can_edit_scoped_family` | advisor with yoga scope edits yoga rule | 200 | scope respected |
| `test_advisor_cannot_edit_out_of_scope` | advisor with yoga scope edits dasa rule | 403 | scope enforced |
| `test_non_advisor_cannot_access_console` | user role | 403 | gate |
| `test_admin_bypass_scope` | admin edits any family | 200 | admin override |

### 8.6 Citation index

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_search_matches_english_title` | q=gaja kesari | returns BPHS 36.14-16 | search works |
| `test_search_matches_iast_title` | q=gajakesari | same result | IAST search |
| `test_search_empty_query` | q="" | 400 | guard |
| `test_search_limits_results` | broad query | ≤ 20 results | pagination |

### 8.7 Multilingual UI (frontend)

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_label_toggle_updates_all_predicates` | switch to Devanagari | all labels in Devanagari | UI correctness |
| `test_autocomplete_matches_across_languages` | type in Devanagari | matches English entries too | cross-lingual search |
| `test_yaml_preview_updates_on_form_change` | change predicate | YAML text changes in preview | live sync |

### 8.8 E2E (Playwright)

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_full_new_rule_submit_flow` | advisor login → new → form → sandbox → submit | PR URL returned | happy path |
| `test_draft_persistence_on_browser_refresh` | refresh mid-edit | draft restored | no data loss |
| `test_unauthorized_redirect` | non-advisor visits /console | redirect to 403 or dashboard | authz UX |

## 9. EPIC-Level Acceptance Criteria

- [ ] All three tables migrated (`rule_draft`, `advisor_scope`, `rule_console_audit`)
- [ ] Vocabulary endpoint returns ≥ 100 predicates with 4-language labels
- [ ] Citation index covers BPHS (95 chapters), Saravali (50), Phaladeepika (28)
- [ ] Draft CRUD + authz enforced
- [ ] Sandbox returns result < 2s P95; never writes to DB
- [ ] PR opener creates PR with canonical YAML, reviewers assigned
- [ ] Frontend: console landing, new-rule form, YAML preview, sandbox, citation autocomplete, YAML mode
- [ ] Multilingual UI: English, IAST, Devanagari, Tamil
- [ ] Audit log live; admin view operational
- [ ] 3+ classical advisors onboarded; each submits a rule successfully
- [ ] Playwright E2E test passes in CI
- [ ] Unit test coverage ≥ 85% for backend; ≥ 70% for frontend components
- [ ] Onboarding guide merged; video recorded
- [ ] CLAUDE.md updated with "classical rule authoring uses the console; direct YAML edits still allowed but flagged for engineering review"

## 10. Rollout Plan

- **Feature flag:** `FEATURE_RULE_CONSOLE` (default off in prod; on in dev).
- **Shadow compute:** N/A — console submits PRs; actual rule deployment gated by merge + P3-E6-flag staged rollout.
- **Backfill strategy:** existing rules viewable immediately (read from classical_rule). No migration of existing drafts.
- **Rollout phases:**
  1. Week 1: ship backend + frontend behind flag in dev. Internal dogfooding.
  2. Week 2: onboard 3 classical advisors in staging; collect feedback.
  3. Week 3: enable in prod for advisor-role users only; monitor audit log.
- **Rollback plan:**
  1. Flip `FEATURE_RULE_CONSOLE=false`. Console page renders "temporarily unavailable"; existing PRs unaffected.
  2. Backend endpoints respond 503.
  3. No data corruption; drafts persist for resume when re-enabled.

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Advisors struggle with abstract DSL predicates | High | Medium | Multilingual labels; video onboarding; sandbox loop shortens feedback |
| Citation index has errors | Medium | Medium | Peer-reviewed by 2+ classical advisors before merge; update process for corrections |
| PR spam from low-quality submissions | Medium | Low | Sandbox test + lint gate before submit; reviewers reject; audit log flags repeat offenders |
| GitHub API rate limits | Low | Medium | Bot token with appropriate scopes; retry-after handling; batching |
| Advisor scope confusion (wrong family) | Medium | Low | UI hides out-of-scope families; error message clear |
| YAML mode lets users bypass validation | Medium | Medium | Server-side re-validation on submit; reject invalid YAML even if frontend misses it |
| Sandbox compute spikes during heavy usage | Low | Medium | Rate-limited to 10/min per user; metric + alert |
| Draft table grows unbounded | Low | Low | Auto-purge drafts untouched > 90d |
| Advisor submits conflicting version | Medium | Medium | PR CI detects semver conflict; resolution via merge |
| Translation quality (Tamil, Devanagari) | Medium | Low | Native speakers review before ship; ongoing corrections via PR |

## 12. References

- Master spec: [`docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`](../../../superpowers/specs/2026-04-19-classical-techniques-expansion-design.md)
- Depends on: [F6](../P0/F6-rule-dsl-yaml-loader.md), [F16](../P0/F16-golden-chart-suite.md), [P3-E6-flag](./P3-E6-flag-feature-flagged-rule-rollouts.md)
- Enables: [Reference-1000](../P4/Reference-1000-expanded-yoga-set.md)
- Monaco Editor: https://microsoft.github.io/monaco-editor/
- React Hook Form: https://react-hook-form.com/
- Classical texts for verse index: BPHS, Saravali, Phaladeepika
