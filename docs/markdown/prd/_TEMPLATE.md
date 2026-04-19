---
prd_id: <ID, e.g., F1, E4a>
epic_id: <parent EPIC if applicable>
title: "<descriptive title>"
phase: <P0-foundation | P1-mvp | P2-breadth | P3-scale-10m | P4-scale-100m | P5-dominance | P6-institution>
tags: [<#correctness>, <#extensibility>, <#performance>, <#ai-chat>, <#astrologer-ux>, <#end-user-ux>, <#multi-tenant>, <#experimentation>, <#i18n>]
priority: must | should | could
depends_on: [<list of other PRD IDs this requires>]
enables: [<list of PRD IDs this unlocks>]
classical_sources: [<list of source_ids used, if classical>]
estimated_effort: <hours | days | weeks>
status: draft
author: <name or @agent>
last_updated: 2026-04-19
---

# <PRD ID> — <Title>

## 1. Purpose & Rationale

<Why does this exist? What problem does it solve? What's the business or engineering impact?>

## 2. Scope

### 2.1 In scope
- <specific bullet points>

### 2.2 Out of scope
- <things explicitly deferred, with rationale>

### 2.3 Dependencies
- <Other PRDs / infrastructure / team decisions this relies on>

## 3. Classical / Technical Research

For classical-content PRDs: the authoritative rules with verse citations.
For infrastructure PRDs: the technical approach with alternatives considered.

### 3.1 <section as appropriate>

## 4. Open Questions Resolved

Every decision made in drafting this PRD, with rationale. If a question surfaces during implementation that wasn't resolved here, flag back to brainstorming.

| Question | Decision | Rationale |
|---|---|---|
| | | |

## 5. Component Design

### 5.1 New services / modules

```
src/josi/...
```

### 5.2 Data model additions

```sql
-- new tables, columns, indexes
```

### 5.3 API contract

For external API:

```
GET /api/v1/...
Response: { ... }
```

For internal interfaces (Python):

```python
class FooService:
    async def compute_foo(self, chart_id: UUID) -> FooResult: ...
```

## 6. User Stories

### US-<ID>.1: <As a [role], I want [capability], so that [benefit]>
**Acceptance:** <conditions that must be true for this story to be done>

### US-<ID>.2: ...

## 7. Tasks

### T-<ID>.1: <Task name>
- **Definition:** <what needs to be built>
- **Acceptance:** <specific, testable conditions>
- **Effort:** <hours or days>
- **Depends on:** <prior tasks>

### T-<ID>.2: ...

## 8. Unit Tests

Per module / per rule. Each test specifies name, input, expected output, and rationale.

### 8.1 <Module/rule name>

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| | | | |

## 9. EPIC-Level Acceptance Criteria

PRD is "done" when ALL of these pass:

- [ ] <criterion 1>
- [ ] <criterion 2>
- [ ] Golden chart suite green for this technique
- [ ] Unit test coverage ≥ 90% for new code
- [ ] Integration test hits the full path (DB → aggregation → serving view → API response)
- [ ] Documentation updated (CLAUDE.md, API docs)

## 10. Rollout Plan

- **Feature flag:** `<flag name>` (default off in P0; on in P1; removed in P2)
- **Shadow compute:** Y/N — if Y, describe shadow window
- **Backfill strategy:** <how existing charts get computed>
- **Rollback plan:** <if we need to revert>

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| | | | |

## 12. References

- Master spec: `docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`
- Related PRDs: `<list>`
- Classical source verses: `<citations>`
- Reference implementation: `<JH version / Maitreya9>`
