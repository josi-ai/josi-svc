# Josi - Product Vision

## What Is Josi

Josi is a **full-stack, multi-tradition astrology platform** that serves as both a direct-to-consumer product and a B2B API. It combines high-precision astronomical calculations, AI-powered interpretive guidance, and a marketplace connecting users with professional astrologers.

The name references "Jyotish" (the Sanskrit/Tamil term for astrology — the science of light).

## Three Pillars

### 1. Calculation Engine (Foundation)

The core of Josi is a trustworthy, high-precision astrology calculation engine built on Swiss Ephemeris (pyswisseph) and Skyfield. It supports six astrological traditions equally:

- **Vedic (Jyotish)**: Sidereal charts with multiple ayanamsa options (Lahiri, Krishnamurti, Raman, etc.), Panchang (Tithi, Nakshatra, Yoga, Karana with end times), Vimshottari/Yogini/Chara Dasha systems, divisional charts (D1-D60), Ashtakavarga, Shadbala/Bhava Bala strengths, Bhava charts, Tamil calendar integration, Muhurta (auspicious timing), and Pariharam (remedies).

- **Western (Tropical)**: Natal charts, secondary progressions, solar returns, synastry, composite charts, major aspects with applying/separating distinction.

- **Chinese**: BaZi Four Pillars (year/month/day/hour) with Heavenly Stems, Earthly Branches, and Day Master.

- **Hellenistic**: Sect determination (day/night), Lots (Fortune, Spirit), annual profections, zodiacal releasing.

- **Mayan**: Tzolkin calendar, day signs.

- **Celtic**: Tree astrology, lunar zodiac.

All six systems are treated as equally important — Josi aims to be the most comprehensive multi-tradition calculation engine available.

### 2. AI-Powered Guidance (Central Differentiator)

AI is not a supplementary feature — it is what makes Josi unique. The platform uses LLMs (GPT-4, Claude) to transform raw chart data into meaningful personal guidance:

- **Contextual Interpretations**: Chart-aware prompts generate interpretations across five styles — Balanced, Psychological, Spiritual, Practical, Predictive. The system builds rich context from planets, houses, aspects, and tradition-specific features (nakshatras, dashas, etc.).

- **Neural Pathway Questions**: A premium feature where AI generates psychological self-awareness questions derived from the user's chart. Moon placement informs emotional questions, Mercury shapes communication insights, Venus guides relationship reflections. Each response builds on previous answers — essentially an AI-guided self-reflection journal through the lens of your birth chart.

- **Vector Similarity**: Interpretations are stored in Qdrant and used for similarity matching — finding charts with similar patterns improves interpretation quality and enables "people like you" insights.

- **Confidence Scoring**: Each interpretation includes a confidence score based on interpretation quality and the number of similar past charts.

### 3. Astrologer Marketplace (Near-Term Priority)

Josi connects users with verified professional astrologers for deeper, paid consultations:

- **Astrologer Profiles**: Specialization areas, hourly rates (USD), sliding scale options, availability schedules, verification workflow (pending → verified → suspended).

- **Consultation Types**: Video (Twilio), chat, email, voice. Pre-consultation questions and focus areas. Post-consultation AI summary and key points.

- **Reviews & Ratings**: Multi-dimensional — accuracy, communication, empathy.

- **Payments**: Stripe integration with refund support, 2-hour cancellation policy.

This bridges the gap between automated AI guidance and human expertise.

## Business Model

### B2B: API-as-a-Service

Organizations authenticate with API keys and get isolated, multi-tenant access to the full calculation engine. This is the "Stripe for astrology" — other products can build on Josi's API without implementing their own astronomical calculations.

### B2C: Consumer Subscription

Four tiers:

| Tier | Charts/mo | AI Interpretations | Consultations | Price |
|------|-----------|-------------------|---------------|-------|
| Free | 3 | 5 | 0 | $0 |
| Explorer | 50 | 100 | 1/month | TBD |
| Mystic | 500 | 500 | 3/month | TBD |
| Master | Unlimited | Unlimited | 10/month | TBD |

Users authenticate via JWT/OAuth (Google, GitHub), save charts, track remedy progress, and book consultations.

## Core Domain

**Person** → The central entity. Birth data (name, date, time, place, coordinates, timezone) is the input to all calculations.

**AstrologyChart** → Calculated chart data stored as JSON. One person can have multiple charts (different systems, different times). Each chart can have multiple interpretations.

**Consultation** → Booking linking User + Astrologer + Chart, with full lifecycle (pending → scheduled → in_progress → completed).

**Remedy** → Multi-language astrological remedies (mantra, gemstone, yantra, ritual, charity, fasting, etc.) with user progress tracking.

## Target Audience

- Global users across all astrological traditions
- Indian diaspora and Tamil-speaking communities (strong Vedic/Tamil calendar emphasis)
- Professional astrologers seeking a marketplace to reach clients
- Developers and astrology businesses needing a reliable calculation API

## Current Development Focus

The team is actively improving Vedic calculation accuracy — validating against reference data (VedicAstro API) for five test persons, closing gaps in traditional export format (nakshatra end times, panchang timings, dasa tables, bhava charts, strengths, ashtakavarga, divisional charts), and ensuring output matches professional astrology software standards.

## Planned Client Applications

- React PWA (web)
- iOS/Android mobile apps (via Capacitor)
