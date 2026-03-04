# Josi — Master Strategy Document

*Consolidated from all brainstorming sessions, market research, and technical discussions. March 2026.*

---

## The Elevator Pitch

**Josi is the Shopify of astrology.** One app for consumers and professional astrologers (role-based), powered by an in-house multi-tradition calculation engine, AI-guided self-discovery with gamified psyche profiling, and a two-sided marketplace — all available as a standalone B2B API. Six astrology traditions. NASA-grade accuracy. Global launch.

---

## Core Decisions (Locked In)

| Decision | Choice |
|---|---|
| **Brand name** | Josi (final) |
| **Mobile framework** | React Native (Expo) |
| **Web framework** | Next.js (latest) |
| **Backend** | Python / FastAPI (microservices) |
| **Frontend repo structure** | Monorepo with Turborepo: Next.js + React Native + shared packages |
| **Repo split** | `josi-svc` (backend microservices) + `josi-app` (frontend monorepo) |
| **Deployment** | Docker Compose (local) + Kubernetes (production) |
| **App structure** | One app, role-based (consumer + astrologer views) + web dashboard for astrologers |
| **Astrology systems** | All 6 equally: Vedic, Western, Chinese, Hellenistic, Mayan, Celtic |
| **AI** | Central differentiator (GPT-4 / Claude) |
| **Psyche profiling** | Critical for AI quality — builds the data layer that powers personalization |
| **Monetization** | Hybrid: subscription + credit/token system |
| **Swiss Ephemeris** | Purchase CHF 700 commercial license (action item) |
| **Priority order** | Calculations → AI Guidance → Marketplace |

---

## Product Architecture

### One App, Three Experiences

**1. Consumer Experience (default)**
- Birth chart across all 6 traditions
- Daily/weekly/monthly predictions (AI-generated, chart-personalized)
- Consumer Muhurta ("When should I do this?" calendar)
- Life Decision Calendar (12-24 month forward view)
- AI Guide (empowering, never fatalistic, learns from feedback)
- Gamified Psyche Profiling (daily games that build personality model)
- Community (chart-similarity-based, not just sun signs)
- Spiritual content feed (personalized)
- Book astrologer consultations
- Parigaram / remedies
- Cultural festival notifications based on heritage + astrological timing

**2. Astrologer Experience (role-based switch in-app)**
- All chart generation tools (all 6 systems)
- Client management CRM (linked to charts)
- Scheduling and calendar
- Payment processing
- Report generation (PDF, branded)
- Booking management and availability
- Practice analytics and revenue tracking
- Marketplace profile management

**3. Web Dashboard (Next.js — astrologers only)**
- Full practice management suite
- Client CRM with chart history
- Revenue analytics
- Report builder
- Calendar management
- Same data as mobile, optimized for desktop workflows

### B2B API (Standalone Product)
- All calculation endpoints exposed for third-party developers
- AI interpretation API
- Muhurta / electional timing API
- Webhook-based transit notifications
- White-label PDF report generation
- Multi-tenant with organization isolation
- Tiered pricing: Starter ($29), Professional ($149), Business ($599), Enterprise (custom), White-label ($500-2,000/mo + usage)

---

## Technical Stack

### Backend Microservices (`josi-svc`)

```
Services:
  calculation-engine    → Core astronomical calculations (pyswisseph, Skyfield)
  interpretation-service → AI text generation (GPT-4 / Claude)
  chart-renderer        → SVG/PNG chart generation
  marketplace-service   → Astrologer profiles, bookings, payments
  user-service          → Auth, profiles, psyche data
  notification-service  → Push notifications, transit alerts, webhooks
  content-service       → Daily horoscopes, spiritual content, community
  api-gateway           → Request routing, rate limiting, API key management

Infrastructure:
  PostgreSQL            → Primary database
  Redis                 → Caching, session management, rate limiting
  RabbitMQ / Redis Streams → Inter-service communication
  S3-compatible storage → Charts, reports, media files
```

**Tech choices:**
- Python 3.12+ / FastAPI for all services
- SQLModel + asyncpg (PostgreSQL)
- Redis for caching
- Docker Compose for local dev
- Kubernetes (GKE) for production
- Swiss Ephemeris (commercial license) + Skyfield
- OpenAI GPT-4 + Anthropic Claude for AI
- Qdrant for vector similarity (interpretation matching)
- Stripe for payments
- Firebase for push notifications
- ElevenLabs / similar for voice synthesis (future)

### Frontend Monorepo (`josi-app`)

```
josi-app/
├── apps/
│   ├── mobile/          → React Native (Expo)
│   └── web/             → Next.js (latest)
├── packages/
│   ├── api-client/      → Shared API client (TypeScript)
│   ├── types/           → Shared TypeScript types
│   ├── ui/              → Shared component library
│   └── utils/           → Shared utilities
├── turbo.json           → Turborepo config
└── package.json         → Root package.json
```

**Tech choices:**
- React Native with Expo (iOS + Android)
- Next.js (latest) for web app + astrologer dashboard
- TypeScript throughout
- Turborepo for monorepo orchestration
- Shared component library between web and mobile
- State management: Zustand or Jotai (lightweight, works in both RN and Next.js)
- React Query / TanStack Query for API data fetching
- Tailwind CSS (web) + NativeWind (mobile) for consistent styling

### Design System
- **Primary colors:** Deep purple (#6B4ECE), Cosmic blue (#1B1B3A), Mystical black
- **Accent:** Gold
- **Style:** Futuristic yet traditional, clean and minimal
- **Brand voice:** Approachable mysticism, empowering self-discovery, modern interpreter of ancient wisdom

---

## Feature Priority (Within Phase 1)

Since all features ship in Phase 1, here's the build order within the phase:

### Wave 1: Foundation (Calculations + Core)
1. Authentication (Apple, Google, Email)
2. User profile (birth data collection with timezone detection)
3. Multi-tradition chart calculations (all 6 systems)
4. Chart visualization (South Indian, North Indian, Western wheel)
5. Basic predictions (daily/weekly/monthly — AI-generated)
6. Swiss Ephemeris commercial license purchase

### Wave 2: AI Guidance
7. AI-powered readings (GPT-4/Claude, chart-aware, 5 interpretation styles)
8. Gamified Psyche Profiling (daily games, OCEAN → planetary archetype mapping)
9. Neural Pathway Questions (chart-derived self-reflection prompts)
10. Consumer Muhurta ("When should I do this?" calendar)
11. Life Decision Calendar (12-24 month forward view)
12. Event-triggered notifications (transit alerts personalized to chart)

### Wave 3: Marketplace + Community
13. Astrologer profile/listing creation
14. Booking system (chat, voice, video)
15. Payment processing (Stripe, tokens/credits)
16. Client management CRM (astrologer view)
17. Professional report generation (PDF)
18. Rating and review system
19. Community features (chart-similarity groups)
20. Parigaram / remedies (connect with practitioners)

### Wave 4: Advanced Features
21. Celebrity astrologer AI voice clones (with consenting partners)
22. Ancestral pattern analysis (family tree + chart overlay)
23. Spiritual content personalization
24. Cultural festival notifications
25. Practice analytics for astrologers
26. B2B API public launch
27. Webhook transit notifications for developers

---

## Monetization Model

### Consumer

| Stream | Model |
|---|---|
| **Subscription** | Free / Explorer / Mystic / Master tiers |
| **Tokens** | For AI consultations, voice sessions, detailed reports |
| **Marketplace** | Commission on astrologer bookings (per-minute or per-session) |
| **Reports** | One-time purchase for detailed PDF charts/reports |
| **Remedies** | Commission on remedy product sales and puja bookings |

**Token/credit system (not pure subscription):**
- Subscription gives a base allocation of tokens monthly
- Additional tokens purchasable à la carte
- Tokens spent on: premium AI readings, voice consultations, human astrologer bookings, detailed reports
- Avoids subscription fatigue while capturing high-intent spending

### B2B API

| Tier | Calls/Month | Price |
|---|---|---|
| Starter | 1,000 | $29/mo |
| Professional | 10,000 | $149/mo |
| Business | 100,000 | $599/mo |
| Enterprise | Custom | Custom |
| White-label | Licensing | $500–2,000/mo + usage |

---

## Market Position

### What Makes Josi Unique (No Competitor Has All of These)

1. **Six-tradition calculation engine** — Vedic, Western, Chinese, Hellenistic, Mayan, Celtic under one roof
2. **Gamified psyche profiling** — Daily games build a personality model that makes AI readings genuinely personal (not generic sun-sign content)
3. **Digital psyche twin** — Over time, the AI knows you better than a generic chart reading ever could
4. **Consumer muhurta** — "When should I do this?" in a clean calendar UX (massive unserved demand)
5. **One app, two roles** — Consumers and professional astrologers in one ecosystem
6. **Empowering AI, never fatalistic** — Frames challenges as growth, not doom
7. **B2B API** — The infrastructure layer for the entire astrology app ecosystem

### Target Markets (Priority Order)
1. **India** — 49% CAGR, deep Vedic cultural demand, AstroTalk proves the model
2. **US/Global diaspora** — Largest premium subscription market, Vedic + Western demand
3. **UK/Europe** — Growing interest, GDPR compliance as trust advantage

### Key Competitors to Watch
- **AstroTalk** ($145M rev, IPO-bound) — marketplace juggernaut, but India-only, Vedic-only, no pro tools
- **Co-Star** ($21M raised) — strong Gen Z brand, but Western-only, no marketplace
- **AstroSage** (70M downloads) — deep Vedic, AI astrologers at 90% margin, but dated UX
- **Vedika API** (2025 launch) — closest B2B competitor with AI, but Vedic-only

---

## Immediate Action Items

1. **Purchase Swiss Ephemeris commercial license** — CHF 700 one-time. Email signed contract to webmaster@astro.ch
2. **Set up `josi-app` repo** — Turborepo monorepo with Next.js + React Native (Expo) + shared packages
3. **Restructure `josi-svc` into microservices** — Start with calculation-engine and api-gateway as separate services
4. **Finalize API contract** — OpenAPI spec that both frontend and B2B consumers will use
5. **Begin React Native consumer app** — Auth + onboarding + chart display
6. **Begin Next.js astrologer dashboard** — Chart tools + client CRM

---

## Key Metrics to Track

| Category | Metric | Target |
|---|---|---|
| **Supply** | Active professional astrologers | 50 at launch |
| **Demand** | DAU/MAU ratio | >30% |
| **Engagement** | Session duration | >7 min |
| **Marketplace** | Booking conversion rate | >5% |
| **AI** | Reading satisfaction (thumbs up/down) | >80% positive |
| **Psyche** | Daily game completion rate | >40% of DAU |
| **Revenue** | LTV:CAC ratio | >3:1 |
| **API** | Third-party API customers | 10 in first 6 months |
| **Retention** | 30-day retention | >40% |

---

## Risk Mitigation

| Risk | Mitigation |
|---|---|
| Scope creep (massive feature set) | Strict wave-based build order. Ship Wave 1 before starting Wave 2. |
| Swiss Ephemeris AGPL violation | Purchase CHF 700 commercial license immediately |
| Calculation inaccuracy | Validate against NASA JPL, Solar Fire, and VedicAstro reference data |
| AI generating harmful/fatalistic content | Content safety filters, empowering-only framing, human review of edge cases |
| Supply-side chicken-and-egg | Onboard 50 astrologers manually before consumer launch. Free pro tools as incentive. |
| Cultural sensitivity | Partner with practitioners from each tradition before launching that system |
| Subscription fatigue | Token/credit hybrid model, not pure subscription |
| Data privacy (birth data is sensitive) | GDPR-compliant from day one, minimal data collection, explicit consent |

---

## References

All research documents are in `docs/markdown/`:
- `PRODUCT_VISION.md` — Product vision and three pillars
- `COMPETITIVE_LANDSCAPE.md` — Detailed competitor profiles
- `MARKET_RESEARCH_AND_STRATEGY.md` — User needs, market gaps, 10 opportunities
- `RESEARCH_PRODUCT_CONCEPTS.md` — Feasibility research on novel features

Source strategy documents (in project root):
- `astrology-app-complete-discussion.md` — Original vision and feature planning
- `astrology-platform-market-analysis-2026.md` — Market analysis and business plan
