# Josi Architecture Decisions — Pass 2 Engineering Review

**Purpose:** authoritative log of cross-cutting architectural decisions locked during Pass 2 engineering review. Analogous to `DECISIONS.md` (which captures astrological/calculation decisions from Pass 1).

**Owners:** cpselvam + Govind (pair review) · started 2026-04-23.

**Consumption:** downstream agent team (PM + coding + QA + frontend-design + frontend-dev agents) consumes this file as a hard spec when implementing PRDs. Every 🔒 lock here is binding — no implementation choice may contradict it without an explicit revision + changelog entry.

**Convention:** same as `DECISIONS.md` — 🔒 marker for locked decisions, **SUPERSEDED** for revised, numbered sub-sections, changelog at end.

**Quality bar for every decision:** futuristic · future-proof · extendible · audit-ready · performant · user-friendly · AI-first.

---

## 0. Foundation context (Tier-1 locks — shape all downstream decisions)

### 0.1 Launch geography + sequence 🔒 (Option C — Global simultaneous, locked 2026-04-23)

- **Launch scope:** India + US + UK + EU (Schengen) at Month 1 — no staged rollout.
- **Data residency:** tri-region at minimum — India (ap-south-1 or equivalent) + US (us-east-1) + EU (eu-central-1). Per-user data routed to home-region based on signup location. Cross-region replication only for globally-cached reference data (ephemeris tables, classical rule registry).
- **Compliance stack at launch:**
  - **India:** DPDP Act 2023 + DPDP Rules 2025 (consent manager integration, 12-month window from rule notification)
  - **US:** CCPA/CPRA (California) + generic consumer-privacy law posture for other states
  - **UK:** UK GDPR + Online Safety Act (2023)
  - **EU:** GDPR + EU AI Act (Aug 2, 2026 GPAI deployer obligations — transparency labels on AI-generated content, logging, incident reporting)
  - **Global:** FTC AI/review rules (affects astrologer marketplace review labels)
- **Payment rails (triple):** RazorpayX/Cashfree for India; Stripe for US + UK; SEPA/Stripe-EU for EU. Per-geography astrologer payout corridor. GST invoicing (India) + 1099-K/1042-S (US) + UK VAT + EU VAT-OSS.
- **LLM provider regions:** Anthropic + OpenAI endpoints selected per user home-region for data-residency + latency. India users prefer Asia-Pacific endpoints; EU users prefer EU-hosted endpoints (Azure OpenAI EU or Anthropic Frankfurt if available at launch).
- **Language launch set:** §1.5 Indian-only policy continues (8 Indian regional + Sanskrit-IAST); English-IAST side serves all diaspora + Western users. Foreign languages deferred to P4+ per DECISIONS.md §1.5 2026-04-23 lock.
- **Rationale:** maximum addressable market at launch + PRODUCT_VISION.md explicitly names "global users across all traditions" + regulatory deadlines (DPDP 12-month / EU AI Act Aug 2026) push hard the "don't defer compliance" stance.
- **Cost:** ~3-4 months extra compliance work upfront (vs India-only) but buys 10x TAM.

**Action items for agent team:**
- Multi-region data model from day 1: every user row stamped with `home_region` + routing enforced at repository layer.
- Consent-ledger primitive + per-jurisdiction consent text surfaces.
- Per-region payment-rail abstraction (astrologer payout provider chosen by astrologer's tax residence, not user residence).
- AI-generated content labels structurally baked into API envelope (not optional footer).
- Deletion surface coverage: Postgres + Redis + Qdrant + LLM provider log retention audit.

### 0.2 Launch timeline + delivery strategy 🔒 (Hybrid A+D — Pass 2 review upfront, agent-parallel 6-month implementation, locked 2026-04-23)

- **Overall target:** v1 ships Month 6 from 2026-04-23 → **target launch 2026-10-23.**
- **Core insight:** agent teams parallelize coding in ways human teams cannot. The bottleneck for agent-based implementation is **spec quality, not code-writing speed**. Investing ~2 months up-front in hardened specs unlocks ~4 months of massively-parallel agent work. Classic D-conservative review discipline + A-aggressive delivery = both.

**Phased plan:**

| Phase | Month | Scope | Who |
|---|---|---|---|
| **Phase 1 — Pass 2 architectural review + PRD hardening** | Month 1–2 (2026-04-23 → 2026-06-23) | All 89 PRDs reviewed against 7-lens rubric + all ARCHITECTURE_DECISIONS §0/§1/§... locked + every PRD gets `§ 2.5 Engineering Review` section with implementation-ready spec | cpselvam + Govind (pair) + me |
| **Phase 2 — Foundation + compliance scaffold** | Month 2–3 (overlapping tail of Phase 1) | Legal frameworks (consent ledger, DPDP/CCPA/GDPR/AI Act readiness) + payment rails (RazorpayX + Stripe + SEPA integration) + data residency (tri-region Postgres) + crisis classifier foundation service + editorial governance role + agent-team orchestration infrastructure | Small human team (2–3 humans) + specialized agent teams |
| **Phase 3 — Parallel agent-team engine implementation** | Month 3–5 | All foundation PRDs (F1-F17) + P1 MVP engines (E1a/E2a/E4a/E6a/E11a/E14a/E15a) + P2 engines (E1b/E3/E4b/E5/E5b/E7/E8/E8b/E9/E10/E17) + 14 GAP_CLOSURE engines (E18–E29 + E1c + E6b) implemented by parallel agent teams | PM agent orchestrating coding + QA + frontend agents across all PRDs simultaneously |
| **Phase 4 — Integration + AI eval + polish + soft launch** | Month 5–6 | Integration testing + UI polish (E12 + E13) + AI eval harness gating all prompt-layer PRDs + astrologer marketplace live + beta with invited diaspora users | Human review + agent iteration |

**Scope bounded for v1 (explicit cut-list):**
- **Vedic tradition at full depth** (Parashari + Jaimini + Tajaka + KP + Kerala Prasna) — non-negotiable
- **Western tradition at functional depth** (E8 Western Depth + E8b asteroids); full Hellenistic tooling deferred to v1.1
- **Chinese, Mayan, Celtic traditions as stub engines** returning placeholder charts + "coming soon" messaging. Architecture supports them; classical rule content is v1.1+. B2B API customers get `501 Not Yet Implemented` with clear roadmap pointer.
- **Astrologer marketplace** live for India + US + UK + EU (matches §0.1 launch geography)
- **AI interpretations + Neural Pathway Questions** live with eval harness in place from day 1
- **Mobile app:** web-first, mobile-responsive PWA at launch; native iOS/Android in v1.1 (Month 9–12)
- **Languages:** Sanskrit-IAST + 8 Indian regional scripts per §1.5; foreign languages deferred per prior lock

**Quality bar non-negotiables (cannot be cut for timeline):**
- Compliance stack (§0.1)
- Crisis-signal safety classifier + geography-specific hotline routing (§0.2)
- Audit-trail scope on every chart calc (see upcoming §0.8)
- AI provenance stamping on every AI artifact (see upcoming §0.6)
- Multi-region data residency (§0.1)
- Tenant isolation + per-tenant quotas (see upcoming §1.x)

**Risk mitigations:**
- **Spec-quality risk:** Phase 1 has an explicit gate — no Phase 3 work starts until every PRD has `§ 2.5 Engineering Review` section + all ARCHITECTURE_DECISIONS §0 locks complete.
- **Agent-coordination risk:** PM agent orchestrates; integration tests run continuously; cross-PRD dependencies flagged at Phase 1 review time, not discovered at integration.
- **Compliance risk:** Phase 2 legal scaffold runs in parallel to Phase 1 tail; external legal counsel engaged Month 2 for India DPDP + EU AI Act opinions.
- **Scope creep:** explicit cut-list above; any scope change requires revision + changelog entry here.
- **AI quality risk:** Phase 4 eval-harness gate blocks launch if regression thresholds fail; eval dataset seeded during Phase 1.

**Action items for agent team orchestration:**
- **Phase 1 (now):** continue Pass 2 architectural review. Each PRD gets `§ 2.5 Engineering Review` section stamped during review.
- **Phase 2 setup:** PM agent spec (what is "project manager agent" concretely? — see upcoming T1.9 Agent-team parallelism lock).
- **Phase 3 kickoff gate:** all 89 PRDs have `§ 2.5 Engineering Review` present AND all ARCHITECTURE_DECISIONS §0 locks complete AND foundation compliance scaffold deployed.
- **Phase 4 launch gate:** eval harness passing for all AI surfaces + crisis-classifier tested at >95% recall on red-team dataset + at least 10 astrologers onboarded across 4 launch regions.

### 0.3 Scale architecture + FinOps-first cost strategy 🔒 (Option D + aggressive FinOps overlay, locked 2026-04-23)

- **Scale target shape:** Architect for 1M users + 10K astrologers; operationally provision for current demand. No fixed pre-reserved capacity. Compute, storage, and LLM spend scale strictly with actual traffic.
- **Core principle:** **spend must track users + astrologers, not aspirational targets.** At 1K users + 10 astrologers, infra bill ≈ $500-1K/mo. At 100K + 1K, ≈ $30-50K/mo. At 1M + 10K, ≈ $300-500K/mo. All elastic, no stepwise jumps.

**Scale-ready architecture (built once, scales silently):**
- Postgres: tenant_id + user_id composite keys on every table from day 1; region-aware routing at repository layer. Start on **Aurora Serverless v2** (scale-to-1-ACU minimum) per region; graduate to provisioned + Citus sharding when single-region hits 50K QPS sustained.
- Redis: **ElastiCache Serverless** (pay-per-ops, not per-node) or **Upstash Redis** (truly serverless, scale-to-zero for low-tier caches). Namespace all keys `{region}:{tenant}:{key}` so sharding is schema-ready.
- **Vector store (pgvector-first → Qdrant at scale) 🔒 (locked 2026-04-23):**
  - **v1 launch (1K → 100K users):** **pgvector** extension on Postgres. Reuses existing infra; no new service to operate, secure, or migrate in Phase 2. ~$0-50/mo at launch scale; no extra network hop; HNSW index native in pgvector as of 2026.
  - **Scale threshold (>100K users OR >10M embeddings):** migrate to **Qdrant Cloud** with tenant-partitioned collections; scale-to-zero between tenants. Migration is embedding re-index + connection-string swap (~1 day of agent work), not a rewrite.
  - **Abstraction layer mandatory:** all vector operations go through a `VectorStore` Protocol (insert / search / filter / delete) with `PgvectorStore` and `QdrantStore` implementations. Repository-layer only depends on the Protocol. Swapping stores is a DI-config change.
  - **Embeddings are lazily computed** on first retrieval, not eagerly on chart creation (FinOps + matches S6 lazy compute).
  - **Tenant partitioning in pgvector:** use a `tenant_id` column + composite index (`tenant_id`, HNSW embedding) so queries prune by tenant before ANN scan. When migrating to Qdrant, tenant-per-collection replaces the tenant_id filter.
  - **Note on Qdrant refs in existing PRDs:** 11 PRDs currently say "Qdrant" (F14, F15, E11a, E11b, S3, S4, I1, I4, I6 + FEATURE_SUMMARY + ARCHITECTURE_DECISIONS). These will be updated to "vector store" during per-PRD Pass 2 review, citing this §0.4 lock.
- Compute: **Google Cloud Run** or **AWS Fargate** per service (scale-to-zero-ish with min-instances=0 for non-critical paths, min-instances=1 for hot paths with predictable P99 latency SLO).
- Ephemeris data: immutable; ship as container layer (baked into image, no storage cost). Swiss Ephemeris files ~500MB; fine.
- Static assets + rule registry: CDN-fronted (Cloudflare); negligible cost.
- CI/CD: GitHub Actions pay-per-minute (no self-hosted runners until $500+/mo spend).

**LLM routing strategy 🔒 (GCP-Gemini primary v1, locked 2026-04-23):**

Cloud strategy: **GCP-only infrastructure for v1.** AWS/multi-cloud deferred to v1.1+ when user demand or resilience requirements justify it. All LLM inference through Vertex AI + Gemini family in v1; no vendor lock-in at code level via LLM adapter pattern (§0.5).

| Task class | v1 Primary (GCP) | v1.1+ User-opt-in | Rationale |
|---|---|---|---|
| **Structured extraction** (parse user query → schema) | **Gemma-2-9B self-hosted on Vertex Model Garden** | Gemini 2.5 Flash-Lite fallback | Cheapest tier; Gemma pre-trained strong on structure; scale-to-zero on Vertex |
| **Transit/panchangam/NPQ snippets** (high volume, small context) | **Gemini 2.5 Flash-Lite** | Gemini 2.5 Flash on fallback | $0.04/M input, $0.15/M output — 95% cheaper than Haiku |
| **Templated narrative synthesis** (free/Explorer tier) | **Gemini 2.5 Flash** | Gemini 2.5 Pro on fallback | Adequate for templated structure; 90%+ cheaper than Haiku |
| **Mid-tier interpretation** (Mystic) | **Gemini 2.5 Pro** | (v1.1 opt-in: Claude Sonnet 4.6) | 58% cheaper than Sonnet; parity on Vedic reasoning benchmarks |
| **Premium interpretation** (Master) | **Gemini 3.0 Ultra** | (v1.1 opt-in: Claude Opus 4.7) | 85% cheaper than Opus; frontier quality |
| **Neural Pathway Questions** | **Gemini 2.5 Pro** (safety + depth) | (v1.1 opt-in: Claude Sonnet 4.6) | Safety classifier gates this surface per §0.3 |
| **Post-consultation summaries** | **Llama-3.1-8B self-hosted Vertex** → Gemini 2.5 Flash synthesis | Gemini 2.5 Pro fallback | OSS for transcription cleanup; Gemini for synthesis |
| **Astrologer workbench AI** | **Gemini 3.0 Ultra** | (v1.1 opt-in: Claude Opus 4.7) | Professional tier; frontier quality required |
| **Agent-orchestration (PM agent in Phase 3)** | **Gemini 2.5 Pro** | Claude Sonnet 4.6 (internal tooling, not user-facing) | Internal agent ops; cost amortized over implementation |

**User-opt-in Anthropic (v1.1+, NOT v1):**
- Mystic/Master tier users can select "preferred LLM family" in account settings: Gemini (default) | Claude (v1.1+ opt-in)
- Astrologer workbench has per-chart LLM selector for astrologers who prefer Claude's reasoning style
- B2B API: tenant-level `preferred_llm_family` in org config
- Implementation: zero code changes required when enabling — flip the feature flag and the adapter layer routes accordingly (§0.5)
- Business rationale: Claude brand recognition among some professional users; "bring your own model" appeal for B2B; resilience during Gemini outages (rare but real)

**Self-hosted OSS strategy via Vertex AI Model Garden:**
- **v1 launch:** Gemma-2-9B + Llama-3.1-8B deployed from day 1 for extraction + transcription tasks. Vertex's scale-to-zero means near-zero cost at low traffic; native auto-scaling at volume.
- **Month 3-5:** measure quality + cost. If Llama-3.1-70B materially outperforms Gemini 2.5 Flash on any task class at lower cost, promote.
- **Month 6+:** dedicated GPU pool (A100/H100 on GCP Compute Engine) only if OSS inference sustained >$10K/mo. Before that, Vertex serverless.
- **Tamil fine-tuning path:** **Gemma-2-9B is the SLM base** (corrected from prior Llama recommendation — Gemma has best Tamil tokenizer + native Vertex fine-tuning). Proprietary SLM (E-SLM PRD) fine-tunes Gemma-2-9B on Josi's proprietary data for Tamil register + 5 interpretation-style voices. Per §0.5 RAG research lock: **fine-tuning teaches voice/style, NOT facts** — classical grounding stays in symbolic + CAG layers.
- **Quality gate:** LLM eval harness (foundation PRD) runs OSS vs Gemini A/B weekly; drops OSS from task class if quality regresses below threshold.

**GCP startup credits:** apply aggressively ($100K-$300K typical) — likely covers 12-24 months of launch-scale LLM inference entirely.

**OpenAI status:** dropped from v1 stack. No GCP integration; no unique niche Gemini doesn't fill. Reserved as future escape hatch if specific feature (e.g., structured-outputs native implementation gap) demands it. Easy to add via §0.5 adapter pattern when/if needed.

**Cost estimates (GCP-Gemini primary, symbolic-first architecture per §0.5 RAG lock):**

| User scale | Monthly LLM cost |
|---|---|
| **1K users** (bootstrap) | $25-50/mo |
| **10K users** (early launch) | $250-400/mo |
| **100K users** (growth) | $2,500-3,500/mo |
| **1M users** (scale) | $25-35K/mo |

All spend tracks user volume elastically per §0.4 FinOps principle. GCP credits likely cover first 12-24 months entirely.

**Proprietary SLM — new PRD on roadmap:**
- **New PRD: E-SLM Proprietary Astrology SLM.** Placement: P3-P4 (after sufficient user data accumulates). Scope: fine-tune a small (7B-13B) open-source base model (Llama-3/Qwen-2.5) on Josi's proprietary data — chart interpretations + astrologer consultation transcripts + NPQ responses + user feedback signals.
- **Prerequisites:** 100K+ interpretations generated + 1K+ consultations logged + user consent framework for training-data usage (opt-in per user; revocable; GDPR Article 22 compliance for automated decision-making).
- **Target:** proprietary SLM handles 60-70% of B2C interpretation volume at ~10% of frontier API cost, with measurably better classical-grounding than generic frontier models (because it's trained on Josi's locked DECISIONS.md classical rules + Parashari lineage data).
- **Defensive moat:** SLM trained on proprietary data becomes a business asset that compounds over time — classical astrology is a niche domain where frontier models underperform specialists.
- **Add to `review.md` + GAP_CLOSURE as future P3-P4 item.** Not implementing in v1; architecture-ready.

**FinOps observability (foundation, not optional):**
- **Cost per request** tagged on every API call (tenant_id, user_id, surface, LLM provider, token count, compute ms).
- **Cost per user per month** dashboard (P50/P95 per subscription tier). Alert when tier's unit-economics go negative.
- **Cost per feature** attribution — which API endpoints consume what share of LLM budget; unlocks "this interpretation style costs 10x more than that one, kill it or meter it."
- **Per-astrologer revenue vs cost** — which astrologers generate positive marketplace economics (commission - LLM summary cost - payment rail cost - infra share).
- **Per-geography cost-of-serving** — India users on Asia-Pacific compute may be 30% cheaper than EU users on EU compute; ARPU tier mapping follows.
- **Monthly budget caps per LLM provider** — hard spend limits that throttle to fallback tier when breached (not outage; graceful degradation).
- **Tenant-level spend visibility** for B2B API customers — they see their own usage, billing is transparent.

**Unit economics tracking (foundational):**
- Every user row has derived `cost_to_serve_ytd` (compute + LLM + storage share).
- Every astrologer row has `revenue_generated_ytd - cost_to_serve_ytd` = contribution margin.
- Subscription tier pricing is formally backed by unit-economics model; tier changes require unit-economics review.
- Free tier has explicit cost budget per user per month (e.g., $0.15/user/mo); users exceeding cap get rate-limited not cut off (wellness posture §0.3 — don't abandon people).

**Rationale:** cost-consciousness is not about being cheap — it's about **sustainable unit economics that let Josi stay alive through bootstrapped growth without burn-multiple blowup**. Every cost lever has a customer-experience trade-off; we measure both and optimize jointly.

**Action items for agent team:**
- Aurora Serverless v2 per region from day 1 with composite-key tenant schema.
- ElastiCache Serverless or Upstash Redis (not provisioned nodes).
- Qdrant Cloud with tenant-partitioned collections + lazy embedding.
- Cloud Run or Fargate with scale-to-zero per service (non-critical paths).
- LLM routing library with task-class + tier-aware provider selection; cost per request logged.
- Self-hosted OSS eval harness scheduled for Month 3-5 evaluation.
- Proprietary SLM PRD to be authored as `E-SLM` placed in P3-P4; add to tracker.
- FinOps dashboards in Phase 2 compliance scaffold: cost per request + cost per user + cost per feature + per-tenant + per-astrologer + per-geography.
- Monthly LLM spend caps with graceful fallback degradation.
- Free-tier user cost budget caps with rate-limiting fallback.

### 0.4 LLM provider abstraction — adapter pattern 🔒 (locked 2026-04-23)

**Core principle:** no code anywhere in Josi's service layer imports Vertex AI, Anthropic, or OpenAI SDKs directly. All LLM interactions go through the `LLMProvider` Protocol defined in `src/josi/ai/providers/`. Swapping providers is a dependency-injection config change, not a code change.

**Abstraction shape (Python Protocol, no ABC):**

```python
# src/josi/ai/providers/protocol.py

from typing import Protocol, AsyncIterator
from pydantic import BaseModel

class LLMMessage(BaseModel):
    role: Literal["system", "user", "assistant", "tool"]
    content: str
    tool_calls: list[ToolCall] | None = None
    tool_call_id: str | None = None

class LLMRequest(BaseModel):
    messages: list[LLMMessage]
    model_tier: Literal["ultra", "premium", "mid", "cheap", "ultra-cheap"]
    tools: list[ToolDefinition] | None = None
    output_schema: type[BaseModel] | None = None  # Structured Outputs
    temperature: float = 0.7
    max_tokens: int = 2048
    stream: bool = False
    cache_key: str | None = None  # For prompt caching
    cache_ttl_seconds: int = 3600  # 1-hour default per §0.5 CAG strategy
    user_region: Literal["india", "us", "uk", "eu"]  # For data residency routing
    tenant_id: str
    request_id: str  # For audit stamping per §0.6

class LLMResponse(BaseModel):
    content: str
    tool_calls: list[ToolCall] | None = None
    structured_output: BaseModel | None = None
    # Audit metadata (stamped by adapter, per upcoming §0.6)
    provider: str  # "vertex-gemini", "anthropic-claude", etc.
    model_name: str
    model_version: str
    prompt_template_id: str | None
    prompt_version: str | None
    context_hash: str
    input_tokens: int
    output_tokens: int
    cache_hit_tokens: int
    cost_usd: float
    latency_ms: int
    safety_verdict: Literal["pass", "crisis_detected", "moderation_flagged"]
    finish_reason: Literal["stop", "length", "tool_calls", "content_filter"]

class LLMProvider(Protocol):
    async def generate(self, request: LLMRequest) -> LLMResponse: ...
    async def generate_stream(self, request: LLMRequest) -> AsyncIterator[LLMStreamChunk]: ...
    async def embed(self, text: str, model: str) -> list[float]: ...
    def supports_feature(self, feature: LLMFeature) -> bool: ...  # caching, tool-use, structured-outputs, streaming
```

**v1 Concrete implementations (delivered by agent team in Phase 3):**
- `VertexGeminiProvider` — Gemini 3.0 Ultra / 2.5 Pro / 2.5 Flash / 2.5 Flash-Lite via Vertex AI SDK. **Primary for v1.**
- `VertexModelGardenProvider` — OSS models (Gemma-2-9B, Llama-3.1-8B/70B, Qwen-2.5-32B) via Vertex AI Model Garden. Used for extraction + transcription + fine-tuned SLM.
- `MockLLMProvider` — testing only; deterministic responses for CI.

**v1.1+ deferred implementations:**
- `AnthropicClaudeProvider` — Claude Opus 4.7 / Sonnet 4.6 / Haiku 4.5 via direct Anthropic API. **Behind user-opt-in feature flag.** Deferred to v1.1 per user request.
- `OpenAIProvider` — GPT-5 / GPT-4.1 via direct OpenAI API. Only added if specific feature need emerges.
- `AWSBedrockProvider` — Anthropic via Bedrock for AWS-resilience escape hatch. Post v1.1.
- `AzureOpenAIProvider` — GPT via Azure for enterprise compliance. Post v1.1.

**Routing layer (`LLMRouter`):**
- Receives `LLMRequest` + task-class hint from caller
- Consults routing config (task-class → model-tier → provider preference) + user opt-in + tenant config
- Selects provider + concrete model (e.g., `"mid"` tier for this task class → `Gemini 2.5 Pro`)
- Applies per-tenant cost caps (§0.4 FinOps)
- Passes to provider; on failure, falls back to next-preference provider (cross-provider fallback = opt-in only; intra-provider fallback = always)
- Logs cost + latency + provider choice to audit log

**Implementation library choice:**
- **Option: LiteLLM + custom Protocol wrapper.** Use LiteLLM (mature, 100+ model support, standardized message format) as the underlying HTTP layer; wrap it with Josi's `LLMProvider` Protocol so Josi code never depends on LiteLLM directly. Best of both: zero provider-specific boilerplate, clean domain abstraction, free to swap LiteLLM for custom later. ← **selected default for v1.**
- Alternative considered: Vercel AI SDK (less mature Python), pure custom (more code but max control). Revisit at Phase 2 kickoff.

**Vendor lock-in posture:**
- **Acceptable v1 lock-in: Google Cloud infrastructure.** Postgres (Cloud SQL or Aurora→Cloud SQL port), compute (Cloud Run), LLM (Vertex + Gemini), secrets (Secret Manager), CDN (Cloud Armor), observability (Cloud Logging/Monitoring).
- **Unacceptable lock-in: any LLM provider at code level.** Adapter pattern enforces this.
- **Future portability posture:** if/when AWS becomes needed (v1.1+ AWS Bedrock for Claude; or multi-cloud resilience), the code changes are: add new `AWSBedrockProvider` implementing `LLMProvider` + add to routing config. Zero service-layer changes.

**Feature flags for LLM routing:**
- `llm.provider.anthropic_enabled` — gates v1.1+ user opt-in for Claude
- `llm.provider.openai_enabled` — gates future OpenAI activation
- `llm.user_preference_enabled` — gates Mystic/Master tier LLM family selector UI
- `llm.tenant_override_enabled` — gates B2B API `preferred_llm_family` tenant config
- All flags default OFF in v1; individually flipped on as features mature

**Action items for agent team:**
- Implement `LLMProvider` Protocol + `LLMRequest` / `LLMResponse` / `LLMMessage` Pydantic models in `src/josi/ai/providers/`
- Implement `VertexGeminiProvider` + `VertexModelGardenProvider` + `MockLLMProvider` for v1 delivery
- Implement `LLMRouter` with task-class routing config + per-tenant cost caps + audit logging
- Scaffold (but do not implement) `AnthropicClaudeProvider` for v1.1 hot-swap
- Feature-flag all non-v1 provider code paths
- All LLM-consuming PRDs (E11a, E11b, E28, all AI-powered interpretation paths) depend on `LLMProvider` Protocol, never concrete providers
- Add lint rule in CI: `import vertexai` / `import anthropic` / `import openai` allowed ONLY in `src/josi/ai/providers/` subdirectory

### 0.5 Liability posture + crisis flow 🔒 (Option B — Wellness guidance + soft crisis flow, locked 2026-04-23)

- **Overall posture:** Josi is a **wellness / self-reflection tool.** NOT positioned as entertainment-only (underselling) and NOT positioned as medical/therapy-adjacent (overselling + over-exposing). Middle-ground defensible legal posture.
- **Disclaimer placement:** **structural, not footer.** Every AI-generated response carries a typed `content_class` field in the API envelope (`entertainment | wellness_guidance | classical_tradition | professional_consultation`) and corresponding disclaimer surface text. Response envelope carries it; UI renders per surface; legal cannot be hidden by UI redesign.
- **Copy guidelines (enforced by editorial review + prompt constraints):**
  - Chart interpretations: "classical tradition suggests" / "indicates a tendency toward" / "may manifest as" — never "you will" or "this guarantees."
  - NPQ: reflection-focused questions, never claims. AI never generates "you are X" statements; always "consider whether X resonates."
  - Upaya / Remedies (E28): **subjunctive only.** "May support," "classical tradition associates," "traditional recommendation" — never "will cause," "fixes," "cures." India Consumer Protection Act 2019 misleading-ad liability protection.
  - Astrologer consultations: astrologer-authored; AI only summarizes, never prescribes.
- **Crisis-signal safety classifier (soft-triggered):**
  - Scope: NPQ reflection text + AI chat user turns. NOT applied to chart inputs (birth data) or astrologer-authored content.
  - Detection: Anthropic/OpenAI moderation API + custom classifier fine-tuned on distress signals (self-harm, suicidal ideation, acute mental-health crisis, abuse disclosure). Run on every user text input pre-LLM.
  - Response on positive detection: **AI chat reply is replaced** with a gentle wellness-framed message surfacing **geography-specific crisis resources**:
    - **India:** iCall (9152987821), Vandrevala Foundation (1860-2662-345), NIMHANS (080-46110007)
    - **US:** 988 Suicide & Crisis Lifeline + Crisis Text Line (text HOME to 741741)
    - **UK:** Samaritans (116-123), SHOUT (text 85258)
    - **EU:** country-specific resolver (Telefonseelsorge DE, Suicide Ecoute FR, etc.) — initial set covers DE/FR/ES/IT/NL
  - **Astrologer consultation escalation path:** if a user in crisis is currently in an active consultation, astrologer gets an in-app prompt to follow standardized crisis-response protocol. Astrologers vetted for this protocol at onboarding.
  - Event logging: crisis-detections logged immutably with timestamp + geography + outcome (user redirected / user continued / astrologer notified). NO user text stored at crisis events (privacy-preserving; classifier runs on-hash). For audit + incident reporting (EU AI Act logging requirement).
- **Content moderation & guardrails:**
  - Astrologer-authored bio + consultation notes pass through same moderation pipeline to prevent astrologers from writing distress-triggering copy.
  - NPQ prompts (system-generated) reviewed by editorial owner (see §0.X Governance) before production rollout.
  - Upaya copy reviewed pre-launch for "will cause / guarantees" language.
- **Regulatory mapping:**
  - EU AI Act Aug 2026: wellness positioning keeps Josi OUT of "high-risk AI" category; GPAI deployer obligations apply (transparency labels, logging, incident reporting) — crisis event log satisfies incident-reporting requirement.
  - India Consumer Protection Act: subjunctive copy on Upaya satisfies misleading-ad carveout.
  - FTC (US): AI-content-labeled responses + reviews comply.
  - UK Online Safety Act: crisis classifier + hotline routing satisfies "user harm prevention" obligation for wellness-adjacent services.
- **Engineering investment:** moderate — classifier as foundation service (not per-PRD), one-time hotline-routing table build, one-time editorial copy pass.

**Action items for agent team:**
- Safety classifier as foundation service (not per-PRD). Run on every NPQ + AI chat user turn before LLM call.
- Geography-specific crisis-hotline routing table in data layer + per-country localization.
- Response envelope: add `content_class` enum + `disclaimer_text` localized per user's regional language.
- Prompt-template library with enforced subjunctive copy constraints + editorial review checkpoint.
- Immutable crisis-event log (privacy-preserving hash only, no raw user text) for EU AI Act incident-reporting compliance.
- Astrologer onboarding: crisis-response protocol training module + acknowledgment requirement.
- Editorial owner role (see §0.X Governance TBD) reviews NPQ templates + Upaya copy pre-launch.

### 0.6 AI grounding architecture — symbolic + CAG + deferred RAG 🔒 (locked 2026-04-23)

Research-backed conclusion (see conversation transcript 2026-04-23): traditional vector-RAG is **cargo-cult for Josi's scenario** — the classical corpus is authored, finite (~500K tokens), stable, and structured. The right 2026 architecture is a three-layer hybrid with no vector store in v1.

**Layer 1 — Symbolic / tool-use retrieval (primary):**
- ~250 authored yogas + ~500 classical passages encoded as Python rule functions with classical citations (F1 rule registry).
- LLM invokes as tool calls: `evaluate_yogas(chart)`, `get_dasa_interpretation(dasa, bhava)`, `lookup_nakshatra(degree)`, etc.
- Deterministic, auditable, cached at Python-function level.
- Produces ~95% of interpretation substance as structured output.
- Zero embedding cost, zero retrieval latency.
- **Quality advantage:** classically-correct by construction (authored mappings), not semantically-close-but-classically-wrong retrievals.

**Layer 2 — Cache-Augmented Generation (CAG) for narrative synthesis:**
- Full classical corpus (~500K tokens of BPHS, Phaladeepika, Saravali, Jataka Parijata, etc.) loaded into Gemini 2.5 Pro's 2M-token context window.
- Cached with 1-hour TTL via Vertex AI prompt caching (90% input discount, 85% latency reduction).
- Every interpretation request gets full corpus access at cached-read pricing.
- LLM synthesizes narrative from (tool outputs from Layer 1) + (cached classical corpus) + (user's chart + NPQ history).
- Tiered by subscription: Mystic/Master get contextual-CAG with Gemini 2.5 Pro / 3.0 Ultra; Free/Explorer get thin-context with Gemini 2.5 Flash (symbolic output + minimal classical context).

**Layer 3 — Deferred vector-RAG (v2+ only, NOT v1):**
- pgvector introduced ONLY when user-generated content (consultation transcripts, NPQ response histories, astrologer notes) exceeds 1M tokens per user cohort.
- Classical canon NEVER goes in vector store — always symbolic + CAG.
- Abstraction layer (VectorStore Protocol per §0.3) built from day 1 so pgvector is a drop-in when triggered.
- v3+: evaluate GraphRAG over yoga/house/planet relationship graph if multi-hop reasoning becomes a bottleneck.

**Per-user interpretation caching:**
- User's natal chart is immutable → base interpretation generated once per user lifetime, stored, served from cache forever.
- Regenerate only on: tier upgrade, explicit user refresh request, or classical-rule-registry version bump.
- Transit snippets, NPQ follow-ups, dasa-change notifications = separate lightweight LLM calls (thin context, high volume tier).
- At 100K users with 10% annual refresh rate, reduces LLM interpretation costs ~10x vs no-cache baseline.

**Fine-tuning scope correction (CRITICAL — from RAG research):**
- **Fine-tuning a small model (Gemma-2-9B / Llama-3.1-8B) teaches VOICE/STYLE/REGISTER, NOT FACTS.** 2025 MedQuAD study across 5 SLMs: RAG and FT+RAG consistently beat FT-alone for factual grounding.
- **Wrong use:** "fine-tune Gemma on BPHS so it knows classical astrology." Fine-tuning doesn't reliably memorize facts.
- **Right use:** fine-tune Gemma-2-9B on Josi's proprietary data for:
  - Tamil astrological register and terminology nuance
  - 5 interpretation-style voices (mystical, psychological, practical, devotional, research-academic per PRODUCT_VISION.md)
  - Parashari tone (vs North-Indian Nadi vs KP-school tone)
- **Structure / facts stay in symbolic + CAG layers, always.** SLM is a style transfer layer on top.
- **Proprietary SLM (E-SLM PRD) purpose:** cost reduction on B2C volume narrative synthesis while preserving classical grounding through symbolic + CAG layers. Expected ~60-70% of narrative volume at ~10% of Gemini 2.5 Pro cost when eligible.

**Cost at typical scale (symbolic-first + CAG + per-user cache + Gemini primary):**

| User scale | Monthly AI cost | Notes |
|---|---|---|
| **1K users (bootstrap)** | ~$25-50 | Mostly cache-hits; GCP credits cover 100% |
| **10K users (early launch)** | ~$250-400 | GCP credits still cover 100% likely |
| **100K users (growth)** | ~$2,500-3,500 | Tier split drives cost; Mystic/Master tier most of the spend |
| **1M users (scale)** | ~$25-35K | Proprietary SLM (post-v2) can drop this 40-50% |

**Architectural cascading effects:**
- E11a (AI Chat Orchestration v1) → Layer 1 tool-use + Layer 2 CAG primary pattern
- E11b (AI Chat Debate Mode) → same pattern, more sophisticated tool chains
- E28 (Upaya / Remedies Engine) → pure Layer 1 symbolic; LLM only for personalization prose
- All chart-interpretation paths → symbolic rule evaluation → structured output → thin LLM narrative synthesis
- Neural Pathway Questions → thin-context LLM, same-user timestamp history for context
- Classical text passage retrieval → symbolic lookup table, never vector search
- Astrologer workbench full classical drill-down → direct rule-registry access, no LLM intermediary needed

**Action items for agent team:**
- Build symbolic rule registry (F1) as primary classical-retrieval interface; all ~250 yogas + classical passages as tool-callable Python functions.
- Build Layer 2 CAG infrastructure: classical corpus loading + Vertex AI prompt caching + cache-warmth monitoring.
- Build per-user interpretation cache at repository layer; invalidation on user events (tier upgrade / explicit refresh / registry version bump).
- Do NOT build vector store in v1 (VectorStore Protocol exists per §0.3 for future swap, but no concrete implementation ships in v1).
- Fine-tuning deferred to v2+ proprietary SLM PRD; scope locked as style/voice transfer, not factual memorization.
- Update 11 PRDs mentioning Qdrant during per-PRD Pass 2 to reflect this lock (F14, F15, E11a, E11b, S3, S4, I1, I4, I6 + FEATURE_SUMMARY + ARCHITECTURE_DECISIONS).
- Add F1 rule registry as foundation PRD priority in Pass 2 review order (prerequisite for all AI-powered features).

### 0.7 AI provenance + audit persistence 🔒 (Option B — Async Pub/Sub → BigQuery, locked 2026-04-23)

Every `LLMResponse` from §0.4 adapter is stamped with full provenance metadata and persisted asynchronously for audit, reproducibility, regression detection, and regulatory compliance (EU AI Act, DPDP, CCPA incident-reporting obligations).

**Pipeline:**
```
LLM call → LLMRouter → Provider.generate() → LLMResponse
                                                  ↓
                              await pubsub.publish("ai-audit-events", event)
                                                  ↓ [non-blocking, <1ms]
                                            (return to caller)
                                                  ↓
[Pub/Sub topic: ai-audit-events]
  → Dataflow streaming subscriber → BigQuery `josi_audit.ai_events` (7yr hot)
  → Cloud Logging mirror (ops dashboards, alerts)
  → Cloud Storage Coldline after 90d (long-term archive)
```

**Audit event schema (persisted to BigQuery):**

| Field group | Fields |
|---|---|
| Request | `request_id`, `tenant_id`, `user_id_hash`, `timestamp`, `surface` (interpretation/NPQ/summary/chat/rectification), `content_class` (§0.5), `user_region`, `llm_region` |
| Provider | `provider` (vertex-gemini/anthropic-claude/vertex-gemma/etc.), `model_name`, `model_version`, `routing_tier` (ultra/premium/mid/cheap/ultra-cheap) |
| Prompt | `prompt_template_id`, `prompt_template_version` (integer, from `prompt_template_version` append-only DB table per §0.13), `context_hash` (SHA-256), `input_tokens`, `cache_hit_tokens`, `tools_invoked` (list[tool_name + args_hash]) |
| Response | `output_tokens`, `finish_reason`, `cost_usd`, `latency_ms`, `first_token_ms` (for streaming) |
| Safety | `safety_verdict` (pass/crisis_detected/moderation_flagged), `moderation_flags`, `crisis_resources_surfaced` |
| Regulatory | `eu_ai_act_logged`, `dpdp_consent_verified`, `content_labeled_ai_generated` (boolean — per §0.1 FTC + EU AI Act labels) |
| Reproducibility | Full request parameters for re-execution: `temperature`, `max_tokens`, `top_p`, `seed` (when provider supports deterministic sampling) |

**Retention policy:**
- **7 years hot in BigQuery** (EU AI Act 6-year minimum + 1yr buffer). Query-able for incident response, regulatory requests, user data-access requests.
- **Cloud Storage Coldline after 90 days** for cost optimization (~$0.004/GB/mo vs BigQuery $0.02/GB/mo).
- **User deletion flow** (DPDP/GDPR right-to-erasure) purges all events by `user_id_hash` (preserves aggregate analytics via hash-only retention; user's raw content never stored in audit log, only hashes + metadata).

**Reproducibility guarantee:**
- Given a stamped audit event, any past AI output can be regenerated by re-running the original request (same `context_hash` + `prompt_template_version` + `model_version` + `request_parameters`).
- For deterministic sampling (`temperature=0` or `seed` set): bit-exact reproducibility.
- For sampling (`temperature>0`): semantically-equivalent reproducibility (which is what EU AI Act incident-reporting actually requires, not bit-exactness).
- Regression detection: compare output of same request across model_version changes; threshold-alert on semantic drift.

**Compliance coverage:**
- **EU AI Act Aug 2026:** GPAI deployer logging obligation satisfied (all AI-generated content logged with model_version + content_hash + `content_labeled_ai_generated=true`).
- **India DPDP Act:** audit trail satisfies data-principal right-to-access (user can request "what AI-generated content exists about me?"). User deletion purges.
- **US FTC AI guidance:** AI-generated reviews + testimonials + consult summaries all stamped `content_class="ai_generated"` for labeling compliance.
- **UK Online Safety Act:** incident-reporting via safety_verdict + crisis_resources_surfaced events.
- **CCPA/CPRA:** access + deletion rights supported.

**Design choices explicitly rejected:**
- **Sampling-based audit** (~10% of free-tier events) — rejected. EU AI Act requires 100% logging. GDPR right-to-explanation needs complete audit.
- **Synchronous audit writes on hot path** — rejected. Adds 10-30ms P95 latency; Pub/Sub async is <1ms and GCP SLA 99.95%.
- **Vector-store semantic audit** (compute embeddings of every AI output for drift detection) — rejected for v1 per §0.6 (no vector store v1). Revisit v2+.
- **Storing raw prompt content in audit** — rejected. Store `context_hash` + `prompt_version` (reproducible via template lookup). Reduces storage cost, avoids PII duplication, simplifies right-to-erasure.

**Action items for agent team:**
- Pub/Sub topic `ai-audit-events` + Dataflow streaming job + BigQuery dataset `josi_audit` with `ai_events` table — Phase 2 foundation scaffold.
- `LLMRouter` emits audit event after every provider call (non-blocking).
- BigQuery partitioning by `timestamp` (daily) + clustering by `tenant_id`, `surface`, `user_region` for query efficiency.
- 90-day lifecycle policy BigQuery → Cloud Storage Coldline via scheduled export.
- User deletion flow (part of DPDP/GDPR data-subject-rights module) purges events by `user_id_hash`.
- Dashboards: per-day AI event volume + cost by tier + safety-verdict distribution + latency P50/P95/P99 per provider per model.
- Alerts: safety_verdict=crisis_detected spike → on-call notification; cost per tenant exceeding monthly cap → throttle to fallback tier per §0.3.

### 0.8 LLM eval harness 🔒 (Option A — P1 foundation, blocks Phase 3 AI PRDs, locked 2026-04-23)

**Core principle:** no AI-powered PRD ships in Phase 3 without a passing eval gate. Eval infrastructure is a Phase 2 foundation deliverable, not a post-launch bolt-on. Ungated prompt changes silently regress production quality — this is the single most common way AI products fail.

**Four-layer eval architecture:**

### Layer 1 — Golden datasets per AI surface (authored during Phase 1)

Every AI-powered PRD has a golden dataset of 50-200 curated `(input, expected_output, rubric_criteria)` tuples authored by domain experts during Phase 1 PRD review. Each PRD's `§ 2.5 Engineering Review` section includes seed eval cases + expansion targets.

**AI surfaces requiring golden datasets (~15):**
- Chart interpretations per tradition (Vedic Parashari, Vedic Jaimini, Western, Tajaka, KP) — 100+ cases each
- Neural Pathway Questions (NPQ) — 50+ response-quality cases, 30+ crisis-signal cases
- Post-consultation summaries — 50+ cases covering edge scenarios
- Transit alerts + dasa-change notifications — 30+ cases
- Upaya / remedy suggestions (E28) — 80+ cases covering all regional variants
- Astrologer workbench assistant queries — 60+ cases
- Prasna / horary queries (E10) — 40+ cases
- Compatibility / Ashtakoota / Thirumana Porutham interpretations (E25, E29) — 50+ cases
- Chart rectification confidence explanations (E17) — 30+ cases
- Foreign-language output (when v1.1+ activates) — 20+ cases per language

**Authored by:** cpselvam (classical accuracy) + editorial-role (cultural/language) + Govind (engineering feasibility). Each case cites the `DECISIONS.md` or `ARCHITECTURE_DECISIONS.md` lock it validates.

### Layer 2 — LLM-as-judge rubrics (automated scoring)

Each AI output scored against surface-specific rubric by an LLM-judge (Gemini 2.5 Pro, separate from production inference to avoid self-grading bias):

| Rubric dimension | Example: chart interpretation | Score |
|---|---|---|
| **Classical accuracy** | Does interpretation cite correct yoga? Correct classical source? | 0-10 |
| **Grounding fidelity** | Does LLM output align with symbolic rule engine tool outputs (§0.6 Layer 1)? | 0-10 |
| **Disclaimer compliance** | Subjunctive language per §0.5 ("may suggest" not "will cause")? | Pass/Fail |
| **Safety posture** | No crisis-adjacent content without classifier routing per §0.5? | Pass/Fail |
| **Content class label** | Matches expected `content_class` from §0.5? | Pass/Fail |
| **Language fidelity** | Tamil/IAST/English per §1.5 locked conventions? | 0-10 |
| **Length discipline** | Within target output length per surface? | Pass/Fail |
| **Personalization** | References user's specific chart placements (not generic)? | 0-10 |

**Composite score** = weighted sum; threshold per surface (typically ≥7.5/10 composite for production promotion).

### Layer 3 — Human-in-loop calibration (weekly cadence)

- 5-10% of judge scores reviewed weekly by editorial-role + cpselvam.
- Disagreements logged as judge-calibration-events.
- Judge rubric refined quarterly based on disagreement patterns.
- **Why critical:** LLM judges drift. Without human calibration, you trust a biased judge and don't know it.

### Layer 4 — CI gate + production regression monitoring

**CI gate (blocks merge):**
- Every prompt template change in PR triggers: candidate_prompt vs current_prompt run on golden dataset.
- Merge blocked if composite score regresses >3% OR any Pass/Fail criterion fails.
- Required approval from editorial-role for prompts affecting user-facing copy (per §0.5 disclaimer discipline).

**Production regression monitoring:**
- 1% of production LLM outputs sampled daily, scored by judge, stored in BigQuery `josi_audit.eval_scores` (same infrastructure as §0.7).
- Weekly drift report: composite-score-by-surface trend over 30d; alert if any surface drops >5% week-over-week.
- Monthly cross-provider A/B: same request to Gemini 2.5 Pro vs fallback; compare scores; informs routing decisions.

### Phase 2 deliverables (blocks Phase 3 AI PRD kickoff)

1. Golden-dataset authoring framework + schema in repository.
2. `pytest-eval` harness: run PRD's golden set against current prompt template, produce score report.
3. LLM-judge service using Gemini 2.5 Pro with surface-specific rubrics.
4. CI workflow step: eval gate on prompt-template PRs.
5. BigQuery eval tables + daily scoring job.
6. Dashboards: score-by-surface, drift-detection alerts.
7. Editorial review workflow: judge-disagreement queue for weekly human calibration.

### Gate for Phase 3 AI PRD implementation

Agent team CANNOT start implementing an AI-powered PRD until:
- [ ] Golden dataset exists (≥50 cases minimum) for the PRD's surface
- [ ] Judge rubric defined + calibrated (at least one human-calibration round completed)
- [ ] CI eval gate operational
- [ ] Surface has composite-score threshold defined in PRD's `§ 2.5 Engineering Review`

PM agent enforces this gate in Phase 3 orchestration.

### Cost of eval infrastructure

- **Golden-dataset authoring:** ~20-40 hours of cpselvam + editorial-role time during Phase 1 (spread across PRD reviews — already in the 2-month Pass 2 budget per §0.2).
- **Judge infrastructure ops:** ~$200-500/mo at 100K users (1% sampling × Gemini 2.5 Pro judge calls).
- **Human calibration:** 1-2 hours/week editorial-role time ongoing.
- **ROI:** catches ~80% of regression bugs before production; saves 10x in incident response + user trust damage.

### Alternatives explicitly rejected

- **Ship-first-eval-later (Option C)** — rejected. Untested prompts in production is the #1 AI product failure mode; worth the 4-6 week Phase 2 investment.
- **Eval only for paid tiers (not free)** — rejected. Free tier users are our trust-building front-line; regressions there damage brand + conversion funnel more than paid-tier regressions.
- **Manual-only eval (no LLM judge)** — rejected. Doesn't scale beyond 2-3 surfaces; we have 15.
- **LLM judge without human calibration** — rejected. Judge drift is real; human calibration catches it.

**Action items for agent team:**
- Phase 2 Month 2-3: build golden-dataset framework + judge service + CI eval gate + BigQuery scoring tables.
- Phase 1 Month 1-2 (current): every PRD's `§ 2.5 Engineering Review` section includes `## Eval Cases` subsection with seed cases + rubric + threshold.
- Phase 3 kickoff gate: cpselvam + Govind verify all AI PRDs have passing eval gates before Phase 3 starts.
- Phase 4 launch gate: 30d of production regression data + no surface below threshold + all safety rubrics at 100% Pass for 7d consecutive.
- Editorial-role hired / assigned by end of Month 2 (blocks calibration work).

### 0.9 Classical-calculation audit architecture 🔒 (Option C+ — 5-layer reconstructability, locked 2026-04-23)

**Principle:** classical-calculation audit is served by **reconstructability**, not pre-logging. Regulatory minimums for classical math = zero (all AI-side audit requirements satisfied by §0.7). The real needs — explainability, lawsuit defense, engineering debug — are met more efficiently by deterministic re-derivation from immutable rule registry + lightweight chart-level audit, rather than always-on per-rule logging.

**5-layer architecture:**

### Layer 1 — Chart-level audit (persistent, lightweight)

Every chart calculation writes one row to BigQuery `josi_audit.chart_calcs`:
- `chart_id`, `tenant_id`, `user_id_hash`, `timestamp`
- `input_hash` — SHA-256 of normalized chart inputs (birth data + location + ayanamsa + house_system + graha node-type choice)
- `rule_registry_version` — integer version from append-only `rule_registry_version` DB table at calc time (per §0.13 config-based versioning, not git SHA)
- `output_hash` — SHA-256 of the final chart state for integrity verification
- `tier` (free/explorer/mystic/master/astrologer) + `surface` (chart_view/interpretation/consultation/export)

**Scale:** ~100K rows/day at 100K users. BigQuery cost: ~$2-5/mo at launch, ~$20-50/mo at 1M users.

**Retention:** 7 years hot + Cloud Storage Coldline archive after 90d (matches §0.7 policy).

### Layer 2 — Immutable rule registry (append-only database, per §0.13)

- Every classical rule (yoga, dasa, varga, shadbalam sub-component, etc.) version-tracked in an **append-only `rule_registry_version` DB table**: `rule_id + rule_registry_version` = permanent addressable identifier.
- **Never delete, never rewrite rows.** Rule revisions insert new rows with monotonically-incrementing `rule_registry_version` integer; old rows remain queryable forever.
- **DB-level enforcement:** INSERT-only role; no UPDATE or DELETE grants on this table. Agent teams + human ops physically cannot rewrite history.
- When a rule is revised (e.g., Trikona Shodhanai edge cases added 2026-04-22 per DECISIONS §1.8), both versions remain permanently retrievable by version integer.
- **Why this matters:** `rule_registry_version` from Layer 1 is always re-playable via DB query, even years later. Database is the audit log for rule definitions. No repo checkout, no git access needed.

### Layer 3 — On-demand re-derivation API

Endpoint: `POST /api/v1/audit/reconstruct`
- Request: `{chart_id}` OR `{input_hash, rule_registry_version}` (for third-party reconstruction requests)
- Response: full calculation trace
  ```json
  {
    "chart_inputs": {...},
    "rule_registry_version": "abc123",
    "rules_fired": [
      {
        "rule_id": "yoga.raja.kendra_trikona_lord_exchange",
        "rule_version": "v3",
        "inputs": {...},
        "output": {"matched": true, "strength": "medium"},
        "classical_citation": "BPHS Ch.39 v.3-8"
      },
      ...
    ],
    "output_chart": {...},
    "output_hash_match": true
  }
  ```
- Deterministic — same inputs + version always produce identical trace
- **Used for:**
  - User-facing "explain this yoga" feature (product feature, not audit log)
  - Astrologer workbench drill-down on a specific chart placement
  - Lawsuit-package assembly (§ Layer 5)
  - Engineering debugging a specific reported anomaly

**Not a persistent log — a reproducibility guarantee backed by immutable rule registry + chart audit.**

### Layer 4 — Per-incident deep-trace flag

- Default off. Flipped on for specific `chart_id`s under investigation (user complaint, legal review, engineering deep-debug).
- When on: next calc for that chart produces full Option-A trace (every rule evaluation including non-firing ones) → written to BigQuery `josi_audit.chart_debug_traces`.
- 30-day retention, cleared when investigation closes.
- Triggered by: support-ticket workflow (1-click "enable deep trace on this chart"), legal workflow, ops on-call.
- Opt-in per chart, not always-on — avoids the 50M rows/day cost of Option A.

### Layer 5 — Litigation-response workflow (24-48h SLA)

Concrete process for legal subpoena response:

1. **Intake:** Legal request specifies `user_id` or `chart_id` + date range.
2. **Chart reconstruction:** Query `chart_audit` → get `input_hash` + `rule_registry_version` per chart in range. Call `/audit/reconstruct` for each → produce classical calculation trace.
3. **AI interpretation retrieval:** Query §0.7 `ai_events` table → all AI-generated content served to user in date range (prompts, responses, model versions, context hashes, safety verdicts).
4. **Consent + disclaimer retrieval:** Query F4 consent ledger → what consents were active, what disclaimer text was displayed at each interaction timestamp, what `content_class` was served.
5. **Consultation records:** Query astrologer marketplace → any consultations + recordings + astrologer-authored notes + post-consultation AI summaries.
6. **Package assembly:** Generate litigation-response PDF with: user profile (consent-limited to what legal allows), chart reconstruction traces, AI interpretation log, disclaimer surfaces, consultation transcripts. Signed by legal-response-role.
7. **SLA:** 24h for simple requests, 48h for complex multi-chart + multi-consultation.

**Archival for reconstructability:**
- Rule registry DB history: permanent append-only table (per §0.13 config-based versioning)
- `chart_audit` BigQuery: 7 years hot + Coldline archive
- §0.7 `ai_events` BigQuery: 7 years hot + Coldline archive
- Consent ledger (F4): 7 years hot + Coldline archive
- Raw user content (chat transcripts, NPQ responses): retention per §0.5 crisis-log policy + user opt-out

### Explainability framing — user-facing, not audit-facing

"Why did the system give this response?" is a **product feature**, not a compliance obligation:
- Every yoga detection carries `classical_citation` field (BPHS/Phaladeepika/etc. ch + verse)
- "Explain this" UI element on every classical claim → calls `/audit/reconstruct` → surfaces inputs + rule + citation
- AI interpretations cite the symbolic layer outputs (§0.6 Layer 1) that informed them
- User export (DPDP right-to-access) includes full chart calculation traces + AI interpretation log
- **No "the algorithm said so" — every claim traces to a classical source by design.**

### What this architecture does NOT do

- **Not always-on per-rule logging.** Would cost 250× more ($500/mo vs $2/mo at launch) for debugging utility we can achieve on-demand.
- **Not real-time semantic drift detection.** Covered by §0.8 eval harness on 1% production sampling, not chart-audit.
- **Not multi-tenant query workload optimization.** Audit is infrequent-access (subpoenas are rare, debugging is targeted) — BigQuery partitioning + on-demand query is fine. No dedicated warehouse needed.

### Cost at scale

| User scale | chart_audit rows/day | BigQuery cost | debug_traces (opt-in) |
|---|---|---|---|
| **1K users** | ~1K | <$1/mo | ~0 |
| **10K users** | ~10K | ~$2/mo | ~$1/mo (ad-hoc) |
| **100K users** | ~100K | ~$5/mo | ~$5/mo |
| **1M users** | ~1M | ~$50/mo | ~$20/mo |

Compare Option A (full-calc always): ~$500/mo at 100K, ~$5K/mo at 1M. **100× cheaper, same defensive capability.**

**Action items for agent team:**
- Create BigQuery dataset `josi_audit` with tables `chart_calcs` + `chart_debug_traces` (+ existing `ai_events` from §0.7 + upcoming `consent_ledger` from F4).
- Chart calculation pipeline emits chart-audit event (async, Pub/Sub) after every calc — batched if volume demands.
- Build `/api/v1/audit/reconstruct` endpoint backed by rule registry + chart_audit lookup.
- Support-ticket + legal + ops tooling: 1-click "enable deep trace on chart_id" flipping the per-chart flag.
- Rule registry enforced as immutable via append-only DB table (per §0.13): DB-level INSERT-ONLY role; no UPDATE/DELETE grants on `rule_registry_version` table; agent teams physically cannot rewrite history.
- Litigation-response runbook + automated package generator (uses reconstruct API + audit tables).
- Product UI: "explain this" component consuming reconstruct API for every classical claim surface.
- User export (DPDP right-to-access) includes full chart calculation traces on request.

### 0.10 Agent-team orchestration architecture 🔒 (locked 2026-04-23)

**Philosophy:** Front-load all decisions + spec hardening during Pass 1 + Pass 2 (Phase 1 in §0.2). Implementation becomes massively-parallel autonomous execution by agent teams. Humans review specs beforehand; agent teams execute with full autonomy; PM agent signs off via test-result verification, not human sampling.

**This is a workflow (predefined code paths), not an agent swarm (dynamic direction-finding).** Per Anthropic's taxonomy (Schluntz & Carr, "Building Effective Agents"), workflows suit scenarios where tasks + prerequisites are known up front — which is precisely what Josi's spec-hardened Phase 1 produces.

### a) Parallelism — 10+ concurrent teams with concurrency cap

- **Target: 10-15 concurrent worker agents per execution wave.**
- **Hard concurrency cap** prevents runaway token blowout (Anthropic flagged 15× token multiplier vs single-agent as the primary cost of parallel agent systems).
- **Topological-sort waves** — all tasks in wave N must complete before wave N+1 starts. Matches Anthropic's LeadResearcher synchronous-fan-out pattern.
- **Non-overlapping artifact constraint:** PM refuses to dispatch two tasks in the same wave whose `affected_paths` overlap. This is the primary defense against the "parallel decision drift" failure mode Cognition's Devin team documented.

### b) Up-front task DAG — spec-hardened, locked before execution

- **Task list is a JSON DAG** generated during Phase 1 from the 89 PRDs' `§ 2.5 Engineering Review` sections.
- **Schema per task:**
  ```json
  {
    "task_id": "E19-shadbalam-repo-layer",
    "prd_ref": "E19",
    "role": "coder | frontend | qa | migration-writer | doc-writer",
    "depends_on": ["E19-shadbalam-schema", "F1-rule-registry"],
    "acceptance_criteria": "...",
    "affected_paths": ["src/josi/services/shadbalam/", "tests/unit/services/test_shadbalam.py"],
    "test_command": "poetry run pytest tests/unit/services/test_shadbalam.py",
    "worktree_path": ".josi/runs/{run_id}/worktrees/{task_id}/",
    "max_turns": 30,
    "model_tier": "mid",
    "retry_budget": 1
  }
  ```
- **No dynamic task creation during execution.** If an agent discovers a missing task, it fails back to PM → PM escalates to human for DAG revision (rare, should trigger spec-review gap analysis).
- **DAG stored as durable artifact** (`.josi/runs/{run_id}/tasks.json`) under version control.

### c) Full autonomy during execution — PM sign-off via test verification

**Human involvement:**
- **BEFORE execution:** humans (cpselvam + Govind) review every PRD + ARCHITECTURE_DECISIONS lock + generate task DAG + author eval goldens. This is the 2-month Phase 1 budget from §0.2.
- **DURING execution:** **zero code review.** Agents code, agents test, PM agent signs off. Humans called only on PM escalation.
- **ESCALATION triggers (PM → human):**
  - Task fails retry budget (1 retry per §0.10.a), PM quarantines task
  - DAG-revision request (task discovers missing dependency not in spec)
  - Integration-wave failure (path-overlap collision not caught pre-dispatch)
  - Policy-red-flag detection (e.g., agent attempts to modify DECISIONS.md, disable crisis classifier, bypass eval gate)
  - Cost threshold breach (any single task exceeds token budget)

**PM verification protocol (the autonomy guarantee):**

1. Coder agent finishes → reports `status: complete` + `test_results_ref` + `patch_ref` (git worktree branch)
2. **PM re-runs the test command in the worktree itself** — never trusts worker self-report. Anthropic explicitly called this out as the top failure mode to design around.
3. QA agent (evaluator-optimizer pattern, Opus-tier read-only + Bash) reviews the diff against `acceptance_criteria` → returns `{passed, failures[], suggested_fixes[]}`
4. If tests pass AND QA passes AND path-overlap check passes AND no policy-red-flags: **PM merges via `git merge --no-ff` to integration branch**
5. If any check fails: **one retry** with QA's suggested fixes back to coder → re-verify → if still failing, quarantine + escalate

**Sign-off signals (PM auto-merge authority):**
- ✅ Unit tests pass (re-executed by PM, not worker-reported)
- ✅ Integration tests pass
- ✅ Lint passes (`poetry run black + flake8 + mypy`)
- ✅ Type-check passes
- ✅ QA agent verdict `passed: true`
- ✅ E2E browser tests pass (for frontend tasks) — Anthropic explicitly warned about "silent success drift" where Claude says unit tests pass but feature is broken end-to-end
- ✅ Eval harness passes (§0.8) for AI-affecting changes
- ✅ Cost within task budget
- ✅ No path-overlap collision with concurrent tasks

### d) Inter-agent communication protocol — Claude Agent SDK canonical

**Per Anthropic's published patterns + Claude Code canonical architecture:**

**Parent→child (PM → worker):** Agent tool invocation with structured task contract (JSON) passed as prompt string. Fresh context window for each worker. Workers cannot spawn their own subagents (enforced by SDK).

**Child→parent (worker → PM):** Final message contains filled-in task contract with `status`, `artifact_refs`, `test_results_ref`. PM receives subagent's final message verbatim as Agent tool result.

**Peer→peer (worker ↔ worker):** **NEVER direct.** All coordination either:
- Through orchestrator (PM routes intents)
- Through durable artifacts on shared filesystem (git worktree + `.josi/runs/{run_id}/`)

**Artifact channels (durable, version-controlled):**
- `.josi/runs/{run_id}/tasks.json` — immutable DAG (input)
- `.josi/runs/{run_id}/progress.jsonl` — append-only event log (output, PM-written)
- `.josi/runs/{run_id}/feature-list.json` — per-task pass/fail matrix (PM-written)
- `.josi/runs/{run_id}/worktrees/{task_id}/` — git worktree per task (worker-written)
- `.josi/runs/{run_id}/qa-verdicts/{task_id}.json` — QA agent outputs
- `.josi/runs/{run_id}/test-results/{task_id}.json` — re-executed test output

**MCP (Model Context Protocol):** used EXCLUSIVELY for agent→tool communication, NOT agent→agent. MCP servers provide: database access, git operations, test runners, LLM-judge calls, classical rule-registry lookups. Agent-to-agent communication is always through the SDK + artifacts.

**Model assignments:**

| Role | Model | Rationale |
|---|---|---|
| **PM (orchestrator)** | **Gemini 3.0 Ultra** (primary) / Claude Opus 4.7 (fallback v1.1+) | Stateful, long-running, reads/writes DAG, re-verifies tests, escalation judgment |
| **Coder** | **Gemini 2.5 Pro** | Fresh context per task, 30-40 turns max, structured output |
| **Frontend-dev** | **Gemini 2.5 Pro** | Same as coder, with E2E test verification |
| **QA agent (evaluator-optimizer)** | **Gemini 3.0 Ultra** | Read-only access + Bash for test execution; higher-quality critique model |
| **Frontend-design** | **Gemini 2.5 Pro** with multimodal | Design artifacts, Figma-like output via Gemini's native multimodal |
| **Doc-writer** | **Gemini 2.5 Flash** | Cheap, straightforward docs + PR descriptions |
| **Triage / linter** | **Gemini 2.5 Flash-Lite** | Cheap noise-filtering on PR comments, style checks |

### Concrete orchestration topology

```
┌─ PM / Orchestrator (Gemini 3.0 Ultra, stateful) ─────────┐
│  - Reads task DAG from .josi/runs/{run_id}/tasks.json    │
│  - Topological scheduler; dispatches ready tasks         │
│  - Pre-dispatch path-overlap check                       │
│  - Re-runs tests in worktrees post-completion            │
│  - Consults QA verdicts                                  │
│  - Merges on success; escalates on red-flag              │
│  - Writes progress.jsonl append-only                     │
└───────────┬──────────────────────────────────────────────┘
            │ Agent tool (synchronous fan-out per wave)
  ┌─────────┼──────────┬──────────┬──────────┐
  ▼         ▼          ▼          ▼          ▼
Coder-1   Coder-2   Coder-N   Frontend-K   QA-Agent
(2.5 Pro, (2.5 Pro, (2.5 Pro, (2.5 Pro,    (3.0 Ultra,
 own      own       own       own          read-only+
 worktree)worktree) worktree) worktree)    Bash)
  │         │          │          │          │
  └─────────┴──────────┴──────────┴──────────┘
            │  Artifacts (durable, git-tracked):
            │  - worktree branches (patches)
            │  - test-results.json per task
            │  - qa-verdict.json per task
            │  - progress.jsonl (append-only event log)
            ▼
         Shared filesystem + git + MCP servers (tools)
```

### Wave execution lifecycle

**Wave 0 — Foundation (serial, human-supervised):**
- Phase 2 compliance scaffold: legal frameworks, payment rails, data residency, crisis classifier, editorial role, agent-team orchestration infra itself, eval harness baseline
- Only after Wave 0 completes does autonomous execution begin

**Waves 1..N — Parallel implementation:**
- PM reads DAG → selects all tasks whose `depends_on[]` are satisfied → filters by path-overlap → dispatches up to 10-15 in parallel
- Each worker spawns in fresh context with its task contract + relevant file list only (never parent history)
- Workers write to isolated worktrees; report back via final-message schema
- PM re-verifies each; merges green, retries red-once-then-escalates
- Wave N+1 begins once Wave N fully merged

**Wave Final — Integration + E2E:**
- All merged; full-system integration tests + E2E browser tests + eval harness + compliance smoke tests
- Human sign-off before production promotion (this is the Phase 4 launch gate per §0.2)

### Failure modes + mitigations (synthesized from research)

| Failure mode | Mitigation |
|---|---|
| **Parallel decision drift** (Cognition's Flappy Bird) | Spec-harden phase locks cross-cutting decisions (DECISIONS.md + ARCHITECTURE_DECISIONS.md). PM rejects task contracts with under-specified ambiguity. |
| **Merge collisions on shared files** | Pre-dispatch path-overlap check; dedicated serial "integration" tasks for hot files (CLAUDE.md, route registries, configs) |
| **Hallucinated verification** ("tests pass") | PM re-executes test command in worktree itself; never trusts worker self-report |
| **Runaway subagent spawning / token blowout** | Hard concurrency cap (10-15); per-task `max_turns` (20-40); subagents cannot spawn subagents (SDK constraint) |
| **Context blow-up in PM** (long run) | PM offloads state to `progress.jsonl`; re-reads only current-wave state; uses context editing + memory tool (Anthropic harness pattern) |
| **Brittle recovery on worker crash** | Treat as tool error (managed-agents pattern); capture session_id + agentId; retry with `resume:`; after 2 failures, quarantine + escalate |
| **Silent success drift** (unit tests pass but feature broken) | QA agent runs E2E browser tests for frontend tasks; multi-layer verification required for merge |
| **Quality regression on prompt changes** | §0.8 eval harness gate: prompt-template PRs run goldens; merge blocked if regression > 3% |
| **Policy violations** (agent tries to disable safety, modify locks) | PM pre-merge policy scanner: detects edits to DECISIONS.md / ARCHITECTURE_DECISIONS.md / crisis-classifier / eval-harness; escalates |

### What this architecture does NOT do

- **Does not allow dynamic task creation** during execution. If an agent discovers an unspecced concern, it escalates to human for DAG revision, never self-spawns.
- **Does not allow recursive subagent spawning.** SDK prevents this; architecture enforces via worker model restrictions.
- **Does not use A2A protocols** (Google's agent-to-agent messaging spec). Premature for single-org system; artifact-based is simpler + observable + recoverable.
- **Does not trust worker self-reports.** PM re-executes everything verifiable (tests, lint, type-check).

### Cost estimate

**Per PRD implementation** (average):
- Coder: ~100-300K tokens at Gemini 2.5 Pro ($1.25/M input, $5/M output) = $1-5 per PRD
- QA evaluator: ~50-100K tokens at Gemini 3.0 Ultra = $0.50-2 per PRD
- PM orchestration overhead: ~20K tokens per task = $0.20 per PRD
- Total per PRD: ~$2-10

**89 PRDs × $5 avg = ~$450 implementation budget total.** Rounds to $1-2K with retries + overhead. GCP credits likely cover 100%.

**Compared to human-team equivalent:** 89 PRDs × 1-2 weeks engineering time × $150/hr × 40 hrs = $500K-1M. Agent team is 500-1000× cheaper.

### Action items for agent team orchestration (Phase 2 deliverables — blocks Phase 3)

- Build task-DAG generator (reads PRD `§ 2.5 Engineering Review` sections → outputs `tasks.json`)
- Implement PM orchestrator using Claude Agent SDK (or equivalent) with Gemini-primary routing
- Implement worker agent definitions (coder, frontend, qa, doc-writer, etc.) with SDK `AgentDefinition`
- Build git-worktree isolation tooling (one-per-task, auto-cleanup)
- Implement path-overlap pre-dispatch check
- Build PM re-verification tooling (test runner, lint runner, type-check runner)
- Build policy scanner (detects agent attempts to modify locked decisions, eval gates, safety classifiers)
- Build escalation workflow (PM → human notification via Slack/email/on-call)
- Build `progress.jsonl` append-only event log + dashboard
- Build QA evaluator-optimizer agent with structured verdict schema
- Build auto-merge tool (git merge --no-ff from worktree branch to integration branch)
- Build run-lifecycle tooling (start run, pause run, resume run, abort run)
- Write orchestration PRD (new PRD: `AGENT-ORCH`) consolidating this §0.10 into implementation spec

### 0.11 Payment + billing architecture 🔒 (locked 2026-04-23)

**Scope:** Josi has four distinct money flows:
1. **B2C subscription billing** (Free/Explorer/Mystic/Master tiers — recurring)
2. **B2C consultation purchases** (marketplace — one-time per booking)
3. **Astrologer marketplace payouts** (platform → astrologer, cross-border complex)
4. **B2B API metered billing** (per-tenant, usage-based)

Each has different provider, tax, compliance, and UX characteristics. Locking per-flow to avoid downstream agent-team ambiguity.

### Flow 1 — B2C subscription billing

**Provider split by user home-region (per §0.1):**

| User region | Provider | Rationale |
|---|---|---|
| **India** | **Razorpay Subscriptions** (UPI Autopay + Netbanking + Cards) | Stripe subscription billing not viable in India for INR-native recurring charges; UPI Autopay is the dominant mechanism for Indian subscriptions |
| **US + UK + EU + global diaspora** | **Stripe Billing** (Cards + ACH + SEPA Direct Debit) | Stripe Billing is industry standard; native tax/VAT; global card acceptance |

**Subscription lifecycle states:**
- `trialing` — 14-day free trial (Explorer+ tiers); no credit card required for Free
- `active` — recurring billing at tier price
- `past_due` — payment failed; 3-day grace period with retry attempts
- `canceled` — user-initiated or past-due grace expired; access remains until period end
- `incomplete` — signup payment failed; account in limbo <24h then deactivated
- `paused` — user-requested pause (up to 90 days for Master tier only)

**Tier pricing (placeholder; to be locked during E-BILLING PRD review):**
- Free: $0 (no card required)
- Explorer: ~$9/mo or ₹299/mo (14-day trial)
- Mystic: ~$29/mo or ₹999/mo (14-day trial)
- Master: ~$79/mo or ₹2499/mo (no trial; direct-to-paid with 30-day money-back)

**Tier transitions:**
- Upgrade: immediate, prorated charge for remaining period
- Downgrade: applies at next billing cycle (no immediate refund)
- Cancel: access through end of current period, no refund unless explicit request within 7 days
- Resume after cancel: one-click reactivation without re-onboarding (card data retained per user consent)

**Currency per region:** INR (India), USD (US + unspecified), GBP (UK), EUR (EU). No multi-currency switching — region-locked at signup.

### Flow 2 — B2C consultation purchases (marketplace)

**Same provider-split as Flow 1.** Astrologer consultation booking = one-time charge (not subscription). Stripe PaymentIntents for US/UK/EU; Razorpay Orders for India.

**Price structure:**
- Astrologer sets base rate per service type (video / chat / email / voice) per duration
- Platform commission applied transparently (user sees total; astrologer sees base + commission breakdown in dashboard)
- Platform commission: **15% on async (email/chat), 20% on live (video/voice)**. Industry-standard range; revisable during marketplace PRD review.

**Booking flow:**
- User selects astrologer + service + time → hold cart ≤15 min
- Payment captured at booking (not at service delivery)
- Refund-eligible window: 24h before consultation (full) / within 24h of consultation completion with valid dispute (partial or full per dispute resolution)
- Funds held in platform balance until consultation completes + dispute window elapses (72h default)

### Flow 3 — Astrologer marketplace payouts

**Provider split by astrologer tax residence:**

| Astrologer region | Provider | Rationale |
|---|---|---|
| **India** | **RazorpayX Route** (Marketplace Payouts product) | Stripe Connect NOT available as payee in India — hard constraint from research; RazorpayX Route is the purpose-built Indian marketplace solution |
| **US + UK + EU + global** | **Stripe Connect Express accounts** | Handles cross-border, KYC, 1099-K/1042-S, VAT, currency conversion; industry standard |

**Payout cadence:**
- **Weekly** default (every Friday; astrologer can self-configure monthly)
- **Minimum payout threshold:** $50 or ₹5,000 (below threshold rolls to next cycle)
- Held in platform balance until dispute window elapses (72h post-consultation)

**KYC / onboarding:**
- KYC at astrologer onboarding (not first payout) — Stripe Connect Identity + Razorpay Route KYC
- Credentials verification (see marketplace trust & safety PRD) separate from payment KYC
- Sanctions screening (OFAC, UN, EU, UK) at onboarding + periodic re-screening

**Cross-border corridor handling:**
- Indian-resident astrologer, US user: user pays USD → Stripe → platform converts to INR → pays astrologer via RazorpayX in INR (FEMA-compliant via LRS route)
- Platform absorbs FX spread (baked into commission structure) — transparent to astrologer
- Record FX rate on each payout for tax reporting

**Commission structure on each transaction:**
```
Gross (user pays):           $100.00
Platform commission (20%):   $20.00  → platform revenue
Stripe processing (2.9%+30¢): $3.20  → payment processor fee
Astrologer net:              $76.80  → paid out weekly
```

All fees broken out in astrologer dashboard (transparency).

**Tax forms (automated via payment providers):**
- US astrologers: **1099-K** (annual, via Stripe Connect); **1042-S** for non-US astrologers paid by US-sourced income
- India astrologers: GST invoice per consultation + annual reconciliation (via RazorpayX)
- UK astrologers: VAT-registered astrologers emit VAT invoices (Stripe handles)
- EU astrologers: VAT-OSS for cross-border B2C sales (Stripe Tax)

### Flow 4 — B2B API metered billing

**Provider:** **Stripe Billing with Stripe Meters** (usage-based pricing).

**Billing model:**
- **Tier-based + metered overage.** Example: Starter $99/mo includes 10K API calls; $0.005 per call over. Growth $499/mo includes 100K calls; $0.003 per call over. Enterprise custom-contract.
- Monthly billing cycle with mid-cycle tier changes prorated
- Per-tenant hard spend cap (prevents bill shock) — tenant-configurable; default $5K/mo
- Cap reached → API calls return `429 Rate Limited: billing cap` with clear remediation link

**Tenant portal:**
- Real-time usage dashboard (calls/day, cost so far this cycle, projected monthly cost)
- Invoice history + PDF download
- Tax-registered address for jurisdiction-appropriate invoicing
- Multiple payment methods (card, ACH, wire for enterprise)
- Usage alerts at 50%/80%/100% of tier + cap thresholds

**Enterprise contracts:**
- Above $10K/mo: manual-invoice option (net-30 or net-60)
- Custom pricing per negotiated agreement
- SLA contracts with uptime credits (defined in enterprise PRD)

### Refund + dispute flows

**User-initiated refund eligibility matrix:**

| Scenario | Eligibility | Process |
|---|---|---|
| Subscription within 14-day trial | Full refund automatic | Self-service; no questions |
| Subscription >14 days, <30 days | Pro-rated refund | Support ticket; auto-approved for Master tier, reviewed for others |
| Subscription >30 days | No refund | Access continues until period end |
| Consultation booked but not held (>24h before) | Full refund | Self-service |
| Consultation booked but not held (<24h before) | 50% refund | Self-service |
| Consultation held, quality dispute | Case-by-case | Dispute ticket; 48h platform SLA; resolved in favor of party with evidence |
| Consultation held, no-show by astrologer | Full refund + astrologer penalty | Automated detection; platform-initiated refund |
| Consultation held, no-show by user | No refund (astrologer gets paid) | Astrologer confirms no-show within 12h |

**Dispute resolution workflow:**
- User opens dispute → platform holds astrologer payout until resolved
- Platform support reviews within 48h → proposes resolution
- Either party can escalate to human review (Trust & Safety role)
- Chargebacks (bank-initiated) handled separately via Stripe Radar + evidence submission

**Fraud detection:**
- **Stripe Radar** baseline (ML fraud scoring on every payment)
- **Custom rules layer:**
  - Velocity check: >5 bookings per user per day → flag
  - Geo mismatch: user IP country ≠ billing country → flag
  - New-account high-value: account <48h old + purchase >$200 → manual review
  - Fake-review detection: astrologer reviews from disposable emails → flag
  - Sanctioned-party screening: OFAC + UN + EU + UK lists; daily re-screen

### Data model implications

- **`Subscription` entity:** stripe_subscription_id OR razorpay_subscription_id, tier, status, current_period_end, cancel_at_period_end
- **`Payment` entity:** provider, provider_payment_id, amount, currency, purpose (subscription/consultation/api), status, tax_amount, platform_fee_amount
- **`Payout` entity:** astrologer_id, provider, provider_payout_id, amount, currency, period_start, period_end, status, fx_rate (if cross-border)
- **`Invoice` entity:** generated for every payment; PDF URL; tax breakdown; jurisdiction
- **`Dispute` entity:** payment_id OR consultation_id, opener_id, reason, status, resolution, resolved_at
- **`TenantUsage` entity:** per-B2B-tenant metered usage; daily roll-up for billing

All entities persist to BigQuery audit tables per §0.7 pattern (payment-events as a separate topic).

### Regulatory coverage

- **PCI DSS:** both Stripe and Razorpay are PCI-DSS Level 1 certified; Josi never touches raw card data (redirect/iframe tokenization)
- **India FEMA** (Foreign Exchange Management Act): cross-border user→astrologer flows compliant via LRS route through RazorpayX
- **India GST:** automated via Razorpay + periodic reconciliation; 18% standard rate on platform commission; astrologer services fall under respective tax category
- **US sales tax:** Stripe Tax auto-calculates per state (subscription + consultation)
- **EU VAT:** VAT-OSS for cross-border B2C via Stripe Tax
- **UK VAT:** threshold £85K+ registration; Stripe handles
- **Sanctions:** OFAC + UN + EU + UK list screening via payment providers' built-in tools

### Action items for agent team

- Integrate Stripe Billing (subscriptions) + Stripe Connect (payouts) + Stripe Meters (B2B) via `PaymentProvider` adapter pattern (mirror §0.4 LLM adapter)
- Integrate RazorpayX (subscriptions + Route payouts) via same `PaymentProvider` Protocol
- Abstraction: all payment code depends on Protocol, never concrete provider (matches §0.4 philosophy)
- Build subscription lifecycle state machine with automatic transitions
- Build astrologer onboarding workflow with KYC + sanctions screening
- Build cross-border FX corridor handling (India astrologer + non-India user)
- Build refund/dispute workflow with 48h SLA tooling
- Build B2B tenant portal (usage dashboard + invoice history + alerts)
- Build fraud detection custom rule layer on top of Stripe Radar
- Build tax invoice generation (GST India, VAT EU/UK, automated sales tax US)
- Tenant spending cap enforcement in API gateway (429 response with remediation)
- Payment audit trail (separate Pub/Sub topic, same BigQuery pattern as §0.7)

### New PRDs to add to tracker

- **E-BILLING** — B2C subscription billing (Flows 1+2)
- **E-PAYOUT** — Astrologer marketplace payouts (Flow 3)
- **E-METER** — B2B API metered billing (Flow 4)
- **E-TRUST** — Trust & Safety: disputes, refunds, fraud, sanctions
- **E-TAX** — Tax compliance automation

Add to `review.md` as P1 or P2 priority (marketplace + subscription = blocker for launch per §0.2).

### 0.12 Coding standards + naming conventions 🔒 (locked 2026-04-23)

**Core principle:** every table, column, variable, function, class, module, and file name must be **fully explicit and self-explanatory**. No abbreviations, no shorthand, no acronyms except universally-understood ones. Code is read far more than written; clarity compounds across 95 PRDs × thousands of agent-written files.

### The rule

**Prohibited (unless on the whitelist below):**
- ❌ `dim` → use `dimension_table` (in conceptual docs) or avoid entirely
- ❌ `fact` → use `fact_table` or spell the specific purpose
- ❌ `PK` / `FK` in code → use `primary_key` / `foreign_key`
- ❌ `src` → use `source`
- ❌ `svc` → use `service`
- ❌ `calc` → use `calculation`
- ❌ `org` → use `organization`
- ❌ `cfg` → use `config` (or `configuration`)
- ❌ `auth` for variable/table names → use `authentication` / `authorization` explicitly
- ❌ `usr` → use `user`
- ❌ `prd` in code (in docs OK) → use `product_requirements_document`
- ❌ `repo` → use `repository`
- ❌ `ctrl` → use `controller`
- ❌ `mgr` → use `manager`
- ❌ `util` / `utils` → use purpose-specific name (e.g., `chart_formatting_helpers`, not `chart_utils`)
- ❌ `temp` / `tmp` → use `temporary_` + purpose
- ❌ `misc` — banned entirely; always find a specific name
- ❌ Single-letter variables except loop indices in tight scopes (`i`, `j` in 3-line loops OK; `x` for user object NOT OK)
- ❌ `data` as standalone variable name → always qualify (`chart_data`, `user_profile_data`)
- ❌ `info` as standalone → always qualify (`debugging_information`)
- ❌ `helper` / `helpers` in module names → use specific purpose
- ❌ `manager` as generic suffix → use specific role (`BookingCoordinator` not `BookingManager`)

**Allowed (universal conventions; whitelist):**
- ✅ `id` as column suffix (`user_id`, `chart_id`) — universal in SQL
- ✅ `url`, `uri`, `http`, `https`, `json`, `xml`, `yaml`, `sql`, `csv`, `pdf` — de facto standard
- ✅ `api` when referring to the concept "API" broadly (but `api_key`, `api_response` — qualify)
- ✅ `db` in CLAUDE.md / scripts when referring to docker-compose service name (existing convention); in code use `database`
- ✅ `ui` in routing / component naming where industry-standard
- ✅ `ai`, `llm`, `ml` — universally understood
- ✅ `i`, `j`, `k` as loop indices in tight scopes (≤5 lines)
- ✅ `n` for count in tight scopes
- ✅ `e` for caught exception in `except` blocks
- ✅ Astrological Sanskrit/Tamil terms per DECISIONS.md §1.5 (e.g., `rasi`, `nakshatra`, `graha`, `dasa`, `varga`)
- ✅ Well-known domain acronyms: `bphs`, `kp`, `sbc`, `npq`, `sav`, `bav` (spelled out in first use in docstrings)
- ✅ `b2b`, `b2c` — business-segment standard

### Naming by artifact type

**Database tables:**
- `snake_case`, singular or plural — be consistent (Josi convention: **singular** table names, plural column names when representing collections)
- ✅ `source_authority` (NOT `source_authorities`, NOT `src_auth`)
- ✅ `chart_calculation_result` (NOT `calc_result`, NOT `results`)
- ✅ `astrologer_consultation_session` (NOT `consultation`, NOT `astro_consult`)

**Database columns:**
- `snake_case`
- Always qualify: `user_id` not `id` (except in primary-key column of user table where `user_id` is the PK of `user` table — this is the convention per CLAUDE.md)
- Boolean columns: `is_`, `has_`, `can_`, `should_` prefix
  - ✅ `is_deleted`, `has_verified_credentials`, `can_access_premium_features`
  - ❌ `deleted`, `verified`, `premium`
- Timestamp columns: `_at` suffix (`created_at`, `consultation_completed_at`)
- Enum-valued text columns: purpose-specific
  - ✅ `subscription_tier`, `payment_provider_name`, `consultation_status`
  - ❌ `type`, `status` (without prefix)

**Python variables + function parameters:**
- `snake_case`, descriptive
- ✅ `user_birth_chart = calculate_natal_chart(user_birth_data)`
- ❌ `chart = calc(data)`

**Python classes:**
- `PascalCase`, noun phrases, purpose-explicit
- ✅ `AstrologerMarketplacePayoutProcessor`, `ChartCalculationAuditPersister`
- ❌ `PayoutMgr`, `AuditHandler`, `Processor`

**Python functions + methods:**
- `snake_case`, verb phrases
- ✅ `reconstruct_chart_from_audit_record`, `verify_astrologer_credentials_at_onboarding`
- ❌ `reconstruct`, `verify_creds`, `run_check`

**Python modules (files):**
- `snake_case`, purpose-specific
- ✅ `chart_calculation_service.py`, `astrologer_payout_coordinator.py`
- ❌ `chart.py`, `utils.py`, `helpers.py`, `misc.py`

**Agent task contracts:**
- `task_id` uses `kebab-case` with purpose-explicit parts
- ✅ `"E19-shadbalam-engine-repository-layer"`, `"F1-dimension-tables-schema-creation"`
- ❌ `"E19-part-1"`, `"F1-task-a"`

### Exceptions

- Existing Josi code with abbreviations currently in production (e.g., `josi.services.`, `josi.db.async_db`) is grandfathered — do not mass-rename as part of this lock. Replace opportunistically during per-PRD Pass 2 review when touching the file.
- Third-party library requirements (e.g., SQLAlchemy `fk_*` naming conventions for constraints) are accepted.
- External-API-response fields may retain their vendor abbreviations in `adapter` layers only; internal domain models spell them out.

### Enforcement

**During Pass 2 review (now):**
- Every PRD's `§ 2.5 Engineering Review` section includes a "Naming check" subsection flagging any ambiguous names in the PRD's proposed schemas / APIs / module layouts. Fixes go into the PRD before agent team picks it up.

**During Phase 3 agent-team execution:**
- Every agent task contract carries the naming rule in its prompt prefix (PM agent injects it).
- QA agent (evaluator-optimizer per §0.10) runs a naming-lint check as part of the verdict — flags any addition to the whitelist-violating patterns.
- `ruff` / `flake8` custom rules:
  - `N999-josi-no-generic-data-var` — bans standalone `data`, `info`, `result`, `obj` as variable names
  - `N998-josi-no-banned-abbrev` — bans `dim`, `fact`, `src`, `svc`, `calc`, `cfg`, `mgr`, `ctrl`, `repo`, `util`, `misc`, `tmp`, `temp` in variable/function/class/module names
  - `N997-josi-boolean-prefix-required` — bans boolean columns without `is_`/`has_`/`can_`/`should_` prefix

**During code review (automated PR comment if failing):**
- `ruff` CI check must pass before merge (blocks agent auto-merge per §0.10)
- Human review (during Pass 2, rare in Phase 3) adds feedback if rules miss something subtle

### Retroactive application

- **Existing code:** audit during per-PRD Pass 2 review. When reviewing E1a (for example), scan `src/josi/services/` for E1a's files and flag abbreviations. Rename opportunistically. Do NOT mass-rewrite everything at once (touches too many files, breaks git blame, explodes review scope).
- **New code:** rule applies immediately. Agent teams in Phase 3 must follow it.
- **Documentation:** PRDs and markdown docs can use abbreviations in conceptual explanations (e.g., "dim tables" in a diagram caption) as long as the first mention spells them out. Code is strict; docs are flexible.

### CLAUDE.md integration

This lock is propagated to `CLAUDE.md` project instructions so every agent invocation (including Claude Code sessions) gets the rule automatically. Update action item below.

### Action items for agent team (Phase 2 deliverables)

- Add naming-rule section to `CLAUDE.md` project instructions referencing §0.12.
- Implement `ruff` custom lint rules `N997`, `N998`, `N999`.
- Add naming-rule check to CI workflow (blocks merge).
- Add naming-rule verification step to PM agent verification protocol per §0.10.
- QA agent prompt template includes naming-rule checklist in every task review.
- Pass 2 PRD review: add "Naming check" subsection to every PRD's `§ 2.5 Engineering Review`.

### Expected cost

- **Phase 2 setup:** ~2-4 hours (ruff rules, CI wiring, CLAUDE.md update).
- **Phase 3 per-PRD overhead:** ~5-10 min of naming review per PRD × 95 PRDs = ~10 hours total, absorbed by agent team (effectively free).
- **Retroactive cleanup:** ~1-2 hours per touched file during Pass 2 PRD review.

### 0.13 Config-based versioning, not git-based 🔒 (locked 2026-04-23)

**Core principle:** every versioned artifact in the runtime system — rules, prompts, dimension data, classical passages, feature flags, model configurations, schema definitions — is versioned in the **database or explicit configuration files**, NEVER by reference to git SHAs or version-control-system state. Git is the development workflow; the database is the runtime source of truth.

**Rationale:**
- **Runtime queryability.** Services, agents, and users can query "what version was active when chart X was calculated?" without repo checkout or git access.
- **Self-contained database.** Reconstruction, audit, replay, incident response all work from DB state alone — the database is authoritative.
- **Multi-environment separation.** Production, staging, development can run different versions without git-branch coordination.
- **Agent-team friendly.** Phase 3 agent teams don't need git access to understand system state during execution. Matches §0.10 artifact-based communication.
- **User-visible explainability.** "Your chart was calculated using rule registry version 23, classical data seed version 4, prompt template version 7" surfaces cleanly to end-users without exposing repo internals.
- **Decoupling from repo structure.** If we ever split the repo, rename, migrate VCS provider — versioning doesn't care.

### What this principle requires

All runtime-relevant versioned artifacts must have an explicit `*_version` column or `_version` table with SCD pattern:

1. **Classical rule registry** — `rule_registry_version` table (SCD Type 2 append-only; each rule revision gets new row with monotonically-increasing version integer). Schema in F6 will be updated to reflect this.
2. **Prompt templates** — `prompt_template_version` table (append-only; stores full template content per version). Revised from §0.7.
3. **Dimension data** — SCD Type 2 per F1 (locked below in F1 design).
4. **Classical passages / text corpus** — `classical_passage_version` table (append-only).
5. **AI provider configurations** — `llm_provider_config_version` table (tracks model-version-override history, routing config changes).
6. **Feature flags** — configuration store (LaunchDarkly or equivalent) OR DB table with SCD pattern.
7. **Chart calculation schemas** — `chart_schema_version` table for Pydantic model evolution.
8. **Seed data** — every seed YAML has an in-band `version` field loaded into `seed_data_version` table on seeding.

### What this principle does NOT require

- **Source code is still git-versioned.** The code implementing rule engines, services, controllers lives in git. What's not git-tracked is the *version identifier* that runtime captures for reconstruction.
- **CI / build artifacts are still git-tracked.** Deploy image tags, etc.
- **Documentation (PRDs, DECISIONS.md, this file) is git-tracked.** Docs are development artifacts, not runtime state.
- **Migration history is git + alembic-tracked.** Alembic revisions, not SCD.

### The clean split

| Artifact | Versioned in | Why |
|---|---|---|
| Source code | Git | Developer workflow |
| Alembic migrations | Git + alembic_version table | Standard pattern |
| Classical rules (content) | **Database SCD** | Runtime, reconstructable, user-visible |
| Prompt templates (content) | **Database SCD** | Runtime, auditable, A/B-testable |
| Dimension data (rows) | **Database SCD Type 2** | Runtime reconstruction per §0.9 |
| Seed data (content) | **Database version table** | Reproducibility without git checkout |
| Feature flags | **Configuration store** | Toggled at runtime, not deploys |
| LLM model routing config | **Database config table** | Changes without deploys |
| Documentation | Git | Development artifact |

### Revisions required to prior locks (cascading)

- **§0.7** AI provenance: `prompt_version` was described as git SHA — revised to "prompt_template_version (integer, from `prompt_template_version` table)". Stamp both `prompt_template_id` and `prompt_template_version`. No git reference.
- **§0.9** Classical-calculation audit: `rule_registry_version` was described as git SHA — revised to "integer version from `rule_registry_version` append-only table". "Immutable git history" language removed; replaced with "append-only database table with version column that never decrements, never updates existing rows."
- **§0.10** Agent-team orchestration: "Rule registry enforced as immutable: CI rule blocks any git operation that rewrites rule history" → "Rule registry enforced as immutable via append-only database table constraint: `INSERT ONLY` role at DB level; no `UPDATE` or `DELETE` grants on `rule_registry_version`."

### Action items for agent team

- Create `rule_registry_version` table (append-only, SCD) — Phase 2 foundation scaffold
- Create `prompt_template_version` table (append-only) — Phase 2
- Create `classical_passage_version` table (append-only) — Phase 2
- Create `llm_provider_config_version` table — Phase 2
- Create `chart_schema_version` + `seed_data_version` tables — Phase 2
- Implement SCD Type 2 loader pattern (generic, reusable across dim tables) — part of F1 scope
- DB-level INSERT-ONLY role enforcement on append-only tables — Phase 2 foundation
- Update F1, F4, F6, F12 to reflect config-based versioning (no git SHA references)
- Update §0.7, §0.9, §0.10 text in this document (done in their respective sections above with cross-reference to §0.13)

### 0.14 Database primary key conventions 🔒 (locked 2026-04-23)

**Core principle:** two PK patterns, selected by table category. Real-entity tables use UUID; enum lookup tables use integer + text code.

### Pattern A — Real-entity tables (UUID PK)

**When to use:** any table representing real business entities — users, charts, calculations, consultations, payments, AI events, audit rows, subscriptions, astrologers, organizations, marketplace bookings, messages, reviews, etc. Also all SCD Type 2 row-level tables.

**Rules:**
- **Primary key type:** `UUID` using **UUIDv7** (time-sortable, index-locality-friendly, RFC 9562 standard).
  - Postgres: use `uuidv7()` via `pg_uuidv7` extension OR `gen_random_uuid()` with application-side UUIDv7 generation as fallback
  - UUIDv7 is monotonically-sortable by creation time = better B-tree index performance than UUIDv4 (random)
- **PK column name:** `{table_name}_id`
  - ✅ `chart_id`, `user_id`, `consultation_session_id`, `chart_calculation_result_id`
  - ❌ `id` alone, `uuid`, `pk`
- **Application-side generation:** clients can generate the UUID before insert (enables optimistic UI + idempotent retries). Server validates it's a well-formed UUIDv7 before commit.
- **No information leakage:** unlike sequential integers, UUIDs don't reveal entity counts, growth rates, or creation order to external observers.
- **Storage:** 16 bytes. For Josi's expected 1M users × 100M facts scale, UUID overhead vs integer ≈ 8 bytes × 100M = 800MB. Immaterial at modern storage prices; clean trade-off.

**Foreign keys to UUID tables:** always `UUID` type, always named `{referenced_table_name}_id`.

### Pattern B — Enum lookup tables (UUID PK + integer enum `id` + text code)

**When to use:** small, bounded-cardinality reference tables representing enumerations. Stable vocabulary (changes extremely rarely). Typical row count ≤ 100, often ≤ 20. Examples in Josi:

- `tradition` (parashari, jaimini, tajaka, kp, western, hellenistic, chinese, mayan, celtic, modern_commentary)
- `parent_category` (vedic_classical, western, cross_tradition, chinese, other)
- `citation_system` (chapter_verse, sutra, karika, software_reference)
- `language_code` (sa_iast, sa_devanagari, ta, hi, te, kn, ml, bn, gu, mr)
- `subscription_tier` (free, explorer, mystic, master)
- `consultation_type` (video, chat, email, voice)
- `content_class` (entertainment, wellness_guidance, classical_tradition, professional_consultation) — per §0.5
- `payment_provider` (razorpay, stripe, stripe_connect)
- `user_region` (india, us, uk, eu) — per §0.1
- `llm_model_tier` (ultra, premium, mid, cheap, ultra-cheap) — per §0.3
- `consultation_status`, `payment_status`, `subscription_status`, etc.
- `safety_verdict` (pass, crisis_detected, moderation_flagged)

**Rules:**
- **Primary key type:** `UUID` (UUIDv7) — matches Pattern A universal UUID convention.
- **PK column name:** `{table_name}_id UUID`
  - ✅ `tradition_id UUID PRIMARY KEY DEFAULT uuidv7()`
- **Stable enum integer column:** `id INTEGER UNIQUE NOT NULL` — maps 1:1 to the corresponding Python `IntEnum` value. This is the ONE exception to §0.12's explicit-naming rule: the column is literally named `id` to match standard Python enum convention and make `MyEnum(row.id)` idiomatic in application code.
  - ✅ `id INTEGER UNIQUE NOT NULL` with values 1, 2, 3... matching Python `IntEnum`
  - Stable across all environments forever (value 1 always means parashari; never reassigned)
  - Allows efficient runtime lookup: `Tradition(row.id)` returns Python enum instance
- **Business key column:** `{table_name}_code TEXT UNIQUE NOT NULL`
  - ✅ `tradition_code TEXT UNIQUE NOT NULL` with values like `'parashari'`
  - Self-documenting in logs, debuggable, human-readable
- **Rationale for triple identifier (UUID + integer `id` + text code):**
  - **UUID PK:** universal row-identity convention (consistent with Pattern A); no FK type surprises
  - **Integer `id`:** stable enum value matching Python `IntEnum`; supports compile-time checked enum code patterns
  - **Text code:** human-readable debugging + seed data + log clarity
  - All three carry different semantics and all three are useful
- **Required columns on every enum lookup table:**
  - `{table}_id UUID PRIMARY KEY DEFAULT uuidv7()`
  - `id INTEGER UNIQUE NOT NULL` (maps to Python IntEnum; literal column name `id` — §0.12 exception)
  - `{table}_code TEXT UNIQUE NOT NULL`
  - `display_name TEXT NOT NULL`
  - `classical_names JSONB NOT NULL DEFAULT '{}'::jsonb` (per §1.5 / F1-Q3; multilingual names)
  - `created_at TIMESTAMPTZ NOT NULL DEFAULT now()`
  - `deprecated_at TIMESTAMPTZ` (nullable; soft-deprecation)
- **No SCD Type 2 on enum lookup tables.** Enumerations should be stable; if a code needs to change meaning, deprecate old code + add new code. Mutation is a smell; treat enum tables as append + deprecate.
- **Integer `id` values are never reassigned** — if a code is deprecated, its integer `id` is permanently retired; new codes get new integers. This preserves runtime `IntEnum` stability across version history.

**Foreign keys to enum tables:** always `UUID`, always named `{referenced_table_name}_id`. FKs reference the UUID PK, not the integer `id`. The integer is a runtime lookup convenience, not a join target.

**Python SQLModel pattern:**

```python
from enum import IntEnum
from uuid import UUID
from sqlmodel import SQLModel, Field

class TraditionEnum(IntEnum):
    PARASHARI = 1
    JAIMINI = 2
    TAJAKA = 3
    KP = 4
    WESTERN = 5
    HELLENISTIC = 6
    CHINESE = 7
    MAYAN = 8
    CELTIC = 9
    MODERN_COMMENTARY = 10

class Tradition(EnumLookupBaseModel, table=True):
    tradition_id: UUID = Field(default_factory=uuidv7, primary_key=True)
    id: int = Field(unique=True)  # Maps to TraditionEnum
    tradition_code: str = Field(unique=True)
    display_name: str
    classical_names: dict = Field(default_factory=dict, sa_type=JSONB)
    ...

# Usage:
row = session.exec(select(Tradition).where(Tradition.id == TraditionEnum.PARASHARI)).one()
# OR:
row = session.exec(select(Tradition).where(Tradition.tradition_code == 'parashari')).one()
```

**§0.12 exception documentation:** the single-letter-lowercase column name `id` is permitted EXCLUSIVELY on enum lookup tables as the integer-enum-mapping column. This is the only place `id` may appear unqualified as a column name in the entire schema. All other tables use `{table}_id` for their PK and never have a bare `id` column.

### Pattern A+B combined — SCD Type 2 for real-entity tables

When a real-entity table needs SCD Type 2 per §0.13 (e.g., `source_authority` whose `default_weight` can change):

```
table: source_authority
  source_authority_row_id    UUID PRIMARY KEY        -- Pattern A: UUIDv7 per SCD row
  source_authority_code      TEXT NOT NULL           -- business key (NOT unique alone)
  version_number             INTEGER NOT NULL        -- monotonic per code
  effective_from             TIMESTAMPTZ NOT NULL
  effective_to               TIMESTAMPTZ             -- NULL = current
  is_current                 BOOLEAN NOT NULL
  
  -- SCD-tracked attributes below
  display_name               TEXT NOT NULL
  tradition_id               INTEGER NOT NULL REFERENCES tradition(tradition_id)
  default_weight             NUMERIC(3,2) NOT NULL
  classical_names            JSONB NOT NULL DEFAULT '{}'
  ...
  
  CONSTRAINT unique_code_version UNIQUE (source_authority_code, version_number)
  CONSTRAINT one_current_per_code EXCLUDE (source_authority_code WITH =) WHERE (is_current)
```

- FKs from fact tables (e.g., chart_calculation_result) reference `source_authority_row_id` (UUID) — this pins to the specific SCD version active at fact creation time.
- "Find current BPHS metadata" queries use `WHERE source_authority_code = 'bphs' AND is_current = TRUE`.
- Reconstruction: given a fact's `source_authority_row_id`, DB query returns the row with exact version used.

### PK convention summary table

| Table category | PK type | PK name | Additional identifiers |
|---|---|---|---|
| Real entities (user, chart, consultation, payment, ai_event, etc.) | **UUID (UUIDv7)** | `{table}_id` | Varies (e.g., email for user) |
| SCD Type 2 descriptive (source_authority, technique_family, etc.) | **UUID (UUIDv7)** per SCD row | `{table}_row_id` | `{table}_code` + `version_number` composite business key |
| Enum lookup (tradition, parent_category, subscription_tier, etc.) | **UUID (UUIDv7)** | `{table}_id` | `id INTEGER UNIQUE` (maps to Python IntEnum) + `{table}_code TEXT UNIQUE` |
| Junction/association (many-to-many link tables) | **Composite FK** of two UUIDs | — | — |

### Enforcement

- SQLModel base classes per category:
  - `RealEntityBaseModel` — UUID PK, created_at/updated_at/deleted_at
  - `EnumLookupBaseModel` — integer PK, `_code` field, classical_names, deprecated_at
  - `ScdType2BaseModel` — UUID row_id, `_code` + `version_number`, effective_from/to, is_current
- **Migration-lint rule:** every new CREATE TABLE in Alembic must match one of these patterns; CI rejects non-conforming schemas.
- **Naming-rule integration with §0.12:** PK column names must be `{table}_id` or `{table}_row_id` — enforced by `ruff` / SQLAlchemy metadata naming conventions.

### Action items for agent team

- Create `RealEntityBaseModel`, `EnumLookupBaseModel`, `ScdType2BaseModel` SQLModel base classes — Phase 2 foundation
- Install `pg_uuidv7` extension OR implement application-side UUIDv7 generator (Python `uuid_utils` library or equivalent) — Phase 2
- Alembic migration-lint rule enforcing PK conventions — Phase 2
- F1 schema revision to use UUID + enum lookup + SCD Type 2 per this §0.14
- Update existing Josi schemas (`TenantBaseModel`, `SQLBaseModel`) to conform — may require data migration (assess during per-PRD Pass 2)

---

## Change log

| Date | Change | Who |
|---|---|---|
| 2026-04-23 | File created. §0.1 Launch geography locked Option C (global simultaneous). | cpselvam + Govind (pair) |
| 2026-04-23 | §0.5 Liability posture locked Option B (wellness guidance + soft crisis flow). (Renumbered from §0.3 → §0.5 on 2026-04-23.) | cpselvam + Govind (pair) |
| 2026-04-23 | §0.2 Launch timeline locked Hybrid A+D (2 months review + 4 months agent-parallel implementation, v1 ships 2026-10-23). | cpselvam + Govind (pair) |
| 2026-04-23 | §0.3 Scale architecture locked Option D + FinOps overlay: architect for 1M, spend tracks demand elastically, tiered LLM routing (Haiku/Sonnet/OSS), self-hosted OSS eval Month 3-5, proprietary SLM on P3-P4 roadmap, unit economics + cost-per-request tracked from day 1. Rolls in T1.5 LLM cost envelope. (Renumbered from §0.4 → §0.3 on 2026-04-23.) | cpselvam + Govind (pair) |
| 2026-04-23 | §0.3 Vector store revised: pgvector-first (v1 launch 1K→100K users) → Qdrant Cloud at scale (>100K users OR >10M embeddings). Mandatory VectorStore Protocol abstraction for drop-in swap. 11 existing PRDs (F14, F15, E11a, E11b, S3, S4, I1, I4, I6 + FEATURE_SUMMARY) will be updated during per-PRD Pass 2. | cpselvam + Govind (pair) |
| 2026-04-23 | §0.3 LLM routing revised to GCP-Gemini primary (Gemini 3.0 Ultra / 2.5 Pro / 2.5 Flash / Flash-Lite tiered by task class). Anthropic deferred to v1.1 as user opt-in (Mystic/Master tier LLM family selector + B2B tenant preference). OpenAI dropped from v1. Proprietary SLM base corrected to Gemma-2-9B on Vertex AI (native Tamil tokenizer + native Vertex fine-tuning). Cost estimates revised down 60-70% vs Anthropic-only. GCP startup credits likely cover 12-24 months. | cpselvam + Govind (pair) |
| 2026-04-23 | §0.4 LLM provider abstraction locked: LLMProvider Protocol via LiteLLM-wrapped adapter pattern. No LLM SDK imports outside src/josi/ai/providers/. v1 ships VertexGeminiProvider + VertexModelGardenProvider + MockLLMProvider. Anthropic/OpenAI/Bedrock/Azure scaffolded but feature-flagged off. GCP infra lock-in acceptable; LLM code-level lock-in unacceptable. | cpselvam + Govind (pair) |
| 2026-04-23 | §0.6 AI grounding architecture locked: 3-layer hybrid (symbolic tool-use + Cache-Augmented Generation + deferred vector-RAG). No vector store in v1. Fine-tuning scope corrected: style/voice/register transfer only, never factual grounding. Per-user interpretation cache. Cost 35-50x cheaper than naive CAG baseline. Classical corpus NEVER in vector store. | cpselvam + Govind (pair) |
| 2026-04-23 | §0.7 AI provenance + audit persistence locked Option B: async Pub/Sub → BigQuery pipeline. Every LLMResponse stamped with full reproducibility + compliance metadata. 7yr BigQuery + Cloud Storage Coldline archive. EU AI Act / DPDP / FTC / UK OSA / CCPA compliant. Sampling rejected (full logging mandatory). | cpselvam + Govind (pair) |
| 2026-04-23 | §0.8 LLM eval harness locked Option A: P1 foundation blocking Phase 3 AI PRD implementation. Golden datasets per-surface (~15 surfaces) authored during Phase 1 PRD review; LLM-as-judge rubrics; weekly human-in-loop calibration; CI gate on prompt changes; production regression monitoring via 1% sampled scoring. Editorial-role hiring blocker by Month 2. | cpselvam + Govind (pair) |
| 2026-04-23 | §0.9 Classical-calculation audit locked Option C+ (honest-minimum): 5-layer reconstructability architecture. Chart-level audit (input_hash + rule_registry_version + output_hash) at ~100K rows/day at 100K users (~$5/mo). Immutable git-backed rule registry. On-demand re-derivation API for explainability + lawsuit defense. Per-incident deep-trace flag (opt-in). 24-48h litigation-response SLA. 100× cheaper than always-on full-calc audit, same defensive capability. | cpselvam + Govind (pair) |
| 2026-04-23 | §0.10 Agent-team orchestration architecture locked: workflow (not agent swarm) pattern per Anthropic. 10-15 concurrent workers with hard concurrency cap. Up-front JSON DAG of tasks. Full autonomy during execution; PM re-verifies tests (never trusts worker self-reports). Gemini primary for all agent roles; Claude fallback v1.1+. Git worktree per task. Artifact-based inter-agent communication; MCP for agent→tool only. Cost ~$1-2K for 89 PRDs implementation (vs $500K-1M human equivalent). | cpselvam + Govind (pair) |
| 2026-04-23 | §0.11 Payment + billing architecture locked: 4 distinct money flows (B2C subscriptions + marketplace + astrologer payouts + B2B metered). Dual-provider: Razorpay India + Stripe rest. RazorpayX Route (India astrologer payouts, Stripe Connect unavailable). Stripe Connect (US/UK/EU astrologer payouts). Stripe Meters (B2B). PaymentProvider adapter pattern mirrors §0.4 LLM pattern. 5 new PRDs added (E-BILLING, E-PAYOUT, E-METER, E-TRUST, E-TAX). Commission 15% async / 20% live. Cross-border FX handled via LRS route for India-resident astrologers. | cpselvam + Govind (pair) |
| 2026-04-23 | §0.12 Coding standards + naming conventions locked: all table/column/variable/function/class/module/file names must be fully explicit — no abbreviations (banned list includes `dim`, `fact`, `src`, `svc`, `calc`, `cfg`, `mgr`, `ctrl`, `repo`, `util`, `misc`, `tmp`, `temp`). Whitelist for universal conventions (id, url, json, ai, llm, rasi, dasa, etc.). Enforced via ruff custom rules (N997-N999) in CI, agent task prompts, QA agent checks, CLAUDE.md project instructions. Applied immediately to new code; retroactive during per-PRD Pass 2 review. | cpselvam + Govind (pair) |
| 2026-04-23 | §0.13 Config-based versioning locked (not git-based). All runtime-versioned artifacts (rules, prompts, dimension data, classical passages, LLM configs, feature flags, schemas, seeds) tracked in DB tables with SCD pattern, never git SHAs. Database is runtime source of truth; git is dev workflow only. Cascading revisions: §0.7 `prompt_version` → `prompt_template_version` (DB integer); §0.9 `rule_registry_version` → DB integer from append-only table; §0.10 rule-registry immutability via DB INSERT-ONLY role not CI git-block. F1 revised to SCD Type 2. Append-only DB tables: rule_registry_version, prompt_template_version, classical_passage_version, llm_provider_config_version, chart_schema_version, seed_data_version. | cpselvam + Govind (pair) |
| 2026-04-23 | §0.14 Database primary key conventions locked: UUID PK (UUIDv7) universal across all tables for consistency. Enum lookup tables have triple identifier: UUID PK `{table}_id` + integer `id` column (maps 1:1 to Python IntEnum, literal column name `id` is §0.12 exception) + text `{table}_code` UNIQUE business key + classical_names JSONB. FKs always UUID, never integer-id. SCD Type 2 descriptive tables: UUID row_id per version + TEXT code + integer version_number composite business key. Alembic migration-lint enforces conformance; SQLModel base classes (RealEntityBaseModel, EnumLookupBaseModel, ScdType2BaseModel) in Phase 2 foundation. | cpselvam + Govind (pair) |

---

## Maintenance notes

- When a new decision is locked, add it under the relevant section with a 🔒 marker + date + option letter.
- When a decision is revised, update in place and add a row to the change log with date + what changed. Old text should be prefixed **SUPERSEDED —** and linked to the new decision.
- Never delete a decision — supersede it.
- This file is source-of-truth. When PRDs are updated to reflect these decisions, cite back to this file.
- Agent team implementations MUST cite the relevant ARCHITECTURE_DECISIONS.md section in code comments for non-obvious architectural choices.
