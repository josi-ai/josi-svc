# Josi — Feature Summary (three lenses)

**Written:** 2026-04-23
**Source:** synthesis of 89 PRDs + DECISIONS.md (224 locked decisions) + PRODUCT_VISION.md
**Purpose:** three audience-specific summaries of the Josi feature set — for pitching, onboarding, and competitive positioning.

---

## Part 1 — Layman summary (non-astrologer, non-technical)

### What is Josi?

Josi is a **multi-tradition astrology platform** — one app that does everything from casting your birth chart to telling you when a good time for your business launch is to connecting you with a real astrologer for a video consultation.

### What does it actually do?

**1. Calculates your birth chart — accurately, in six traditions.**
Most astrology apps only do one tradition (Western *or* Vedic). Josi does six: **Vedic** (Indian), **Western**, **Chinese**, **Hellenistic** (ancient Greek), **Mayan**, **Celtic** — all treated with equal mathematical rigor using the same high-precision astronomy engine NASA-grade researchers use (Swiss Ephemeris). You pick your tradition; the chart is calculated correctly for that tradition.

**2. Explains your chart in plain language, personalized to you.**
Instead of generic "you are a Taurus, you like stability" readings, Josi uses AI (GPT-4 and Claude) to analyze your specific chart configuration and give you guidance that actually fits *your* placements — not a copy-paste horoscope. Five different interpretation styles (from mystical to psychological-scientific) so you can pick the tone that works for you.

**3. Tells you auspicious and inauspicious times — the daily panchangam.**
Want to know if today is a good day to sign a contract? Start a new job? Travel? Get married? Josi computes the traditional Indian panchangam (five-limbed calendar) every day — auspicious hours, inauspicious hours (Rahu Kalam, Kuligai, Emakandam), festival dates, planetary hours. For Tamil users specifically, this includes Tamil-tradition elements: Karthikai Deepam, Aadi Perukku, Pongal timings, regional muhurtas.

**4. Compatibility matching — for relationships, marriage, family.**
The classic 36-point Ashtakoota matching used across India, the Tamil 10-porutham (Thirumana Porutham) used in Tamil weddings, plus Manglik (Mangal Dosha) checks and Rajju/Vedha dosha screening. Tells you not just "compatible or not" but where the strengths and friction points are.

**5. Predicts life phases — dasa system.**
Vedic astrology divides your life into periods (dasas) ruled by different planets, each lasting years. Josi computes 10+ different dasa systems (Vimshottari is the standard — 120 years cycling through 9 planets) and tells you which period you're in, what it typically brings, when it changes, and what sub-periods (antardasha, pratyantardasha) overlap.

**6. Tells you what's happening *now* versus your birth chart — transits.**
Daily/weekly/monthly — where are the planets *today* relative to where they were at your birth? Josi tells you which transits are meaningful for you right now, when they peak, and what life area they affect.

**7. Chart rectification — fixing unknown birth times.**
If you don't know your exact birth time (common in families without hospital records), Josi uses life events you remember — marriage, first job, parent's death, childbirth — to reverse-calculate your most-likely birth time. Four different methods (Vimshottari-dasha matching, transit analysis, divisional charts, planetary progressions) combined with weighted scoring.

**8. Yoga detection — special chart combinations.**
Vedic astrology identifies 250+ special planetary configurations called "yogas" that indicate specific life outcomes (Raja Yoga = power/status; Gaja Kesari = wisdom; Neecha Bhanga = hardship turned to blessing). Josi detects all of them automatically.

**9. Remedies — what to do about negative placements.**
When the chart shows challenges, classical Vedic texts recommend remedies: specific mantras, gemstones, charitable acts, temple visits, yantras, planetary offerings. Josi maps detected doshas to classical remedies with region-appropriate temple/deity suggestions (Tamil users get Tamil temples; Telugu users get Tirumala; etc.).

**10. Book a real astrologer.**
Josi includes a marketplace of verified professional astrologers. Video, chat, email, or voice consultations. Booking, payments (Stripe), multi-dimensional reviews (accuracy, empathy, depth, timeliness). After your consultation, Josi generates an AI-powered summary so you don't forget what was said.

### Who is it for?

- **Everyday users** who want to understand themselves better — Free tier available; paid tiers for more charts/AI interpretations/consultations.
- **Indian diaspora** — Tamil, Telugu, Hindi, Malayalam, Kannada, Bengali, Gujarati, Marathi speakers who want astrology in their native language.
- **Professional astrologers** — who need a powerful calculation engine to serve clients.
- **App developers** — who need an astrology calculation API to build their own products (B2B).

### Business model

- **Free tier** — limited charts, AI interpretations, consultations per month
- **Paid subscriptions** (Explorer / Mystic / Master) — more quotas, advanced features
- **Pay-per-consultation** — book astrologers directly
- **B2B API** — companies pay per API call to use Josi's calculation engine in their own apps

---

## Part 2 — Astrologer-user feature summary

### What an astrologer gets when using Josi

Josi treats astrologers as **power users** — every B2C feature is configurable, every classical technique is computable, every decision has an override. If you're a practicing astrologer with a specific lineage preference, you are not forced into one-size-fits-all defaults.

### The astrologer workbench

**Full classical computation transparency:**
- **Ashtakavargam** — 5-tab view showing Raw BAV → Trikona Shodhit → Ekadhipatya Shodhit → SAV → Sodhya Pinda, with contributor-trace per cell. D1 and D9 Ashtakavargam. Kaksha Vibhaga panel (96-kaksha sub-sign strength).
- **Shadbalam** — full 6-fold strength with sub-component decomposition (Sthana, Dik, Kala, Chesta, Naisargika, Drik Bala). Plus Budhan's dual-classification (friend of Guru vs. co-friend of Sooriyan/Sukkiran — displayed as two Shadbalam values so you can work from your preferred classification).
- **Bhava Bala** — house strength with Bhavadhipati, Digbala-Bhavasya, Bhava Drishti sub-components.
- **Vimshopaka Bala** — 20-point divisional strength across 16 vargas.
- **Avastha suite** — all 5 classical schemes: Baladi 5-fold, Jagrat-Swapna-Sushupti 3-fold, Lajjitadi 6-fold, 9-fold (Deepta/Swastha/etc.), Arohana-Avarohana.
- **Panchadha Maitri** — 5-fold composite planetary friendship.
- **Sudarshana Chakra** — triple-chakra reading (Lagna + Sooriyan + Chandran) with per-bhava triple-agreement scoring.

**16 divisional charts (Vargas):**
D1 · D2 (Hora) · D3 · D4 · D7 · D9 · D10 · D12 · D16 · D20 · D24 · D27 · D30 · D40 · D45 · D60.

**10 dasa systems:**
Vimshottari (primary, 4-level MD→AD→PD→SD), Ashtottari (paksha-based), Yogini, Chara Dasa (Jaimini), Kalachakra, Shoola Dasa, Sthira Dasa, Narayan Dasa, Brahma Dasa, Tri-Rashi Dasa — plus 5 minor kalpas (Chathurseethi-sama 84yr, Dwisaptati-sama 72yr, Panchottari, Shodashottari, Shatabdika) in E1c Extended Dasa Pack.

**10 Special Lagnas** (E26):
Bhava Lagna, Hora Lagna, Ghati Lagna, Vighati Lagna, Sri Lagna, Indu Lagna, Pranapada Lagna, Varnada Lagna, Nisheka Lagna, Vakra-Shoola points.

**250+ Yogas across 9 classes:**
Raja yogas, Dhana yogas, Arishta yogas, Nabhasa yogas, Pancha Mahapurusha, Gaja Kesari, Neecha Bhanga with 6 cancellation rules, Kaal Sarpa (12 variants), Sunapha/Anapha/Durudhura, Kemadruma, etc. Each yoga shows trigger evidence and classical source citation.

**Per-chart configuration toggles:**
- Ayanamsa (9-shortlist: Lahiri default + Raman, Krishnamurti, True Chithirai, Yukteshwar, Bhasin, Suryasiddhantha, True Poosam, Fagan-Bradley; plus 34-ayanamsa advanced dropdown for research)
- House system (6-shortlist: Whole Sign default + Bhava Chalit, Equal, Placidus for KP, Koch, Porphyry; plus 18-system advanced dropdown)
- Rahu/Ketu node: Mean or True per-chart choice (B2C defaults to Mean; astrologer picks)
- Vimshottari depth L1–L5
- Trikona Shodhanai variant (Phaladeepika 3-case, default)

**Dual-system support:**
- **Parashari primary** with BPHS canonical rules; commentary variants (Phaladeepika, Saravali, Uttara Kalamrita, Jataka Parijata, Sarvartha Chintamani) available as astrologer toggles.
- **Jaimini** full suite: Chara Dasa, Karakamsa, Arudha Lagna (with generalized Argala), Atmakaraka analysis, Upapada.
- **Tajaka (Varshaphala)** — annual chart + 16 Tajaka yogas + Sahams + Muntha.
- **KP (Krishnamurti Paddhati)** — 5-level significators, cuspal sub-lord analysis, Ruling Planets, KP horary — single-source Krishnamurti canon (no variant dilution).
- **Kerala Prasna** — via E10 with traditional Prasna Marga rules.

**Rectification engine (E17):**
4-method weighted: Vimshottari 35% + Transit 30% + Varga 25% + Progressions 10%. 3 operating modes: event-based (user enters life events), personality-based (questionnaire), Prashna-assisted (your Prasna chart at consultation time cross-references birth time). ±4h default window, ±12h max. ≥70% absolute confidence threshold; top-3 candidates shown.

**Longevity / Maraka / Badhaka (E5b + E27):**
Full Pindayu computation, Maraka identification (2nd+7th lords + occupants + conjuncts), Badhaka engine per Lagna-type triad (movable=11th, fixed=9th, dual=7th) with classical BPHS triggers + Shadbalam-weighted severity.

**Compatibility (E25 + E29):**
- **Ashtakoota 36-point** (8-koota pan-Indian)
- **Manglik (Mangal Dosha)** — Lagna-only 5-house rule (2/4/7/8/12); astrologer can enable Chandran-reference + 1st-house-inclusion
- **5 classical Manglik cancellations**
- **Rajju / Vedha / Papasamya** doshas
- **Thirumana Porutham** — Tamil 10-porutham (Dina/Gana/Mahendra/Stree-Deerga/Yoni/Rasi/Rasyathipathi/Vashya/Rajju/Vedha) for Tamil matchmaking

**Prasna/Horary (E10):**
Dual-method always — Parashari Prasna + KP horary simultaneously. Arudha-of-Prasna-Lagna, Prasna Marga omen rules (15 core + 65 extended), Navamsa yes/no method.

**Transit intelligence v2 (E6b):**
Full Ashtakavargam-transit, Gochara-Vedha rules, Tara Bala / Chandra Bala for daily transits, Kal Sarpa transit detection, Graha-Karaka transits.

**Muhurtam engine:**
Full Muhurta Chintamani canonical rules — daily muhurtams (30-muhurta subdivision), Abhijit Muhurta, Sarvatobhadra Chakra (28-nakshatra version), Brahma/Agneya/Raja/Chara muhurtas, region-adapted suggestions.

**Consultation and practice management:**
- Client management with session notes
- Video/chat/email/voice consultation tools
- Booking and Stripe payments
- Multi-dimensional reviews (accuracy, empathy, depth, timeliness, value)
- AI-generated post-consultation summaries
- Quota tracking
- Revenue dashboard

**Multi-language display:**
Sanskrit-IAST + 8 Indian regional scripts (Tamil, Hindi, Telugu, Kannada, Malayalam, Bengali, Gujarati, Marathi) side-by-side. Tamil phonetic conventions locked (Dasai, Uthiradam, Sevvai, Kuligai, etc.).

**Upaya (Remedies) engine (E28):**
Rule-registry mapping detected doshas/weak grahas/afflicted bhavas to classical Upayas: Mantra · Yantra · Tantra · Daan · Vrata · Rudraksha · Gemstone · Temple-deity correlations. Regional auto-adapt for temple suggestions.

---

## Part 3 — Competitive positioning (what Josi has that others don't)

### Competitive landscape

| Category | Competitors | What they do | What they miss |
|---|---|---|---|
| Consumer Vedic apps | AstroSage, AstroTalk, AstroYogi, Ganeshaspeaks | Basic chart + daily horoscope + astrologer marketplace | Shallow classical depth; no Shadbalam transparency; no Tamil-specific rules; generic AI |
| Consumer Western apps | Co-Star, The Pattern, CHANI, Astro.com | Chart + psychological interpretation | Vedic-only as afterthought; no dasa systems; no muhurtam |
| Panchangam apps | Drik Panchang, Kalnirnay, Rashtriya Panchang | Daily panchangam reference | No AI; no chart; no astrologer marketplace; static content |
| Professional software | Jagannatha Hora (JH), Parashara's Light, Kala, Solar Fire | Deep computation for astrologers | Desktop-only; no consumer UX; no AI; no mobile; no API |
| Calculation APIs | Swiss Ephemeris wrappers, Astrology API | Raw astronomical data | No classical rule engine; no interpretation; no multi-tradition |

### What Josi provides that nobody else does — 8 unique angles

#### 1. True six-tradition parity
Every other consumer app is "Vedic with a Western afterthought" or vice versa. Josi treats **Vedic + Western + Chinese + Hellenistic + Mayan + Celtic** as equal first-class traditions, each with its own full calculation engine and tradition-native rendering. No competitor does this. This alone is a defensible moat — building 6 tradition engines at parity is 3–4 years of classical research work.

#### 2. AI interpretation with classical grounding
Competitors either (a) have AI that generates generic horoscope text, or (b) show raw classical computation with no interpretation. Josi's AI is **grounded in the specific chart's classical machinery** — it sees your Shadbalam, your yogas, your dasa-phase, your transits, and synthesizes all of it into personalized guidance. Five interpretation styles (mystical, psychological, practical, devotional, research-academic). Not a horoscope generator — a chart analyst.

#### 3. Neural Pathway Questions (NPQ) — unique to Josi
Psychology-meets-chart feature: Josi generates **self-reflection questions** based on your chart placements that build on your previous responses. Over sessions, you build a psychological map of yourself informed by your chart but expressed in your own words. Nothing else does this.

#### 4. Vector similarity search across charts (Qdrant-powered)
"Show me charts similar to mine where the person had a Saturn return peak in 2023" — queryable across the full user base (opt-in, anonymized). For astrologers this is a research tool nobody has. For users it's "find my chart twins."

#### 5. Tamil classical canon — depth no Western or North-Indian app has
- **Thirumana Porutham (10-porutham)** — Tamil wedding matching distinct from Ashtakoota
- **Tamil panchangam nuances** — Saura Masa conventions, Pongal / Karthikai Deepam / Aadi Perukku, Vakya-Nirayana-Drik reconciliation
- **Corrected Dwipushkar/Tripushkar pada-rule** (Dvipada 3-nakshatra / Tripada 6-nakshatra) — most apps use the wrong nakshatra set
- **27 vs 28 nakshatra handling** — 27 default, 28 for Sarvatobhadra Chakra muhurta only
- **Tamil phonetic canonical table** — 300+ entities across nakshatras, rasis, grahas, vargas, Samvatsaras, tithis, karanas, yogas, muhurtas, shadbalams, koottas

#### 6. Full Parashari gap closure — 13 engines competitors skip
Most consumer Vedic apps skip the hard classical work and just show dasa + basic yoga + compatibility. Josi ships:
- **Shadbalam Engine (E19)** — full 6-balas + Budhan dual-classification
- **Bhava Bala Engine (E20)** — house strength decomposition
- **Vimshopaka Bala (E21)** — 20-point divisional synthesis
- **Avastha Suite (E22)** — all 5 classical schemes
- **Panchadha Maitri (E23)** — 5-fold friendship
- **Janma-Tara 9-Cycle (E24)** — Tamil muhurtam essential
- **Maraka-Badhaka Engine (E27)** — longevity/obstruction timing
- **Upaya / Remedies Engine (E28)** — classical remedies with regional adaptation
- **Special Lagnas (E26)** — 10 lagnas most apps don't even compute

This takes Parashari implementation coverage from the typical consumer-app **~70%** to **~98%** (gap closure locked 2026-04-20; formal audit in GAP_CLOSURE.md). Professional astrologers can use Josi as their primary computation tool — something no other consumer platform offers.

#### 7. Two-user-type framework applied across every decision
Every calculation decision has two modes:
- **B2C default** — the classically-canonical, ecosystem-standard pick (Mean Node, Lahiri, Whole-sign, BPHS Ch.44 Badhaka)
- **Astrologer toggle** — commentary variants, lineage-specific options (True Node, Raman ayanamsa, Sripati houses, Rath-school Badhaka weighting)

224 decisions locked this way. A Parashari Tamil astrologer, a Bengali Jyotish-shastra astrologer, and a Rath-school commentator can all use Josi with their own preferences honored — without forking the codebase.

#### 8. Astrologer marketplace integrated with the calculation engine
AstroTalk/AstroYogi have marketplaces but no serious calculation engine — astrologers there hand-calculate or use JH separately. Professional software (JH, Parashara's Light) has no marketplace.

Josi is the **only platform** where:
- Astrologer logs in to Josi, uses the full classical workbench
- Client books a consultation through the same platform
- Video/chat consultation happens in-app with chart data shared
- Post-consultation AI summary generated from the actual chart + session notes
- Reviews + ratings persist on astrologer's profile

### Sales pitch — one paragraph

> **Josi is the only astrology platform where six traditions, 250+ classical yogas, 10+ dasa systems, and AI-powered guidance come together in one app — with the Parashari classical depth that professional astrologers need and the personalized AI interpretation that everyday users want. It's what you'd get if Jagannatha Hora, Drik Panchang, AstroTalk, and Co-Star were rebuilt as one product by a practicing Parashari Tamil astrologer. For users: accurate charts, honest guidance, real astrologers. For astrologers: a classical workbench, a marketplace, and clients. For developers: a B2B API with multi-tenant isolation.**

### Defensibility — why a competitor can't just clone this

- **Classical depth takes years of domain review.** 224 decisions locked with explicit classical source citations is 2+ years of astrologer-time. Nobody else has done this publicly.
- **Multi-tradition parity is a 3-4 year build** — not a weekend project.
- **Two-user-type framework baked into every lock** — retrofitting this into an existing app is architecturally hard.
- **Tamil canonical corpus (TAMIL_NAMING_AUDIT.md)** — no other app has it. Building it requires a native speaker + Parashari astrologer + Tamil nūl literature expertise.
- **AI interpretation grounded in classical rule engine** — most AI astrology is LLM-wrappers. Josi's AI has structured tool-use against the calculation engine; the interpretations cite specific chart placements.

---

## Part 4 — deep consistency audit

See `CONSISTENCY_AUDIT.md` (generated separately by background agent) for feature-level logical-consistency findings across all 89 PRDs.

---

**Document version:** 1.0 (2026-04-23, Pass 1 closure snapshot)
**Maintained by:** cpselvam (Parashari Tamil astrologer, calculation-side review) + Govind (engineering, UX/user flows)
