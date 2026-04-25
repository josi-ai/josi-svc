# Parashari Gap Closure — Action Plan

**Purpose.** Durable record of the Parashari-classical-techniques gap survey conducted 2026-04-20 and the user's decision to close all critical + important gaps. This brings Josi to full Parashari + Jagannatha Hora parity.

**Decision:** Option A (full closure) locked by user. Scope expansion 76 → 89 PRDs (+13 new). Logged in `DECISIONS.md`.

**Survey methodology.** Gap-finding agent cross-referenced the 76-PRD scope against 12 categories of Parashari-classical techniques (dasas, strength/evaluation, transit, nakshatra, bhava, yogas, remedies, compatibility, prasna, time-cycle, special lagnas, analytical depth). Identified 48 gaps total across 4 priority tiers. This document captures the critical + important resolutions.

---

## Section 1 — New PRDs to create (13 total)

### Critical (11 PRDs) — Phase P2

| PRD ID | Title | Description | Classical source |
|---|---|---|---|
| **E19** | **Shadbalam Engine** | Formalize 6-component planetary strength (Sthana/Dik/Kala/Cheshta/Naisargika/Drik) with rule-versioning + Ishta-Kashta Phala. Currently only DECISIONS 1.7 locks display behavior; no engine PRD exists. | BPHS Ch.27–29 |
| **E20** | **Bhava Bala Engine** | House strength computation (Adhipati/Dig/Kala/Drik Bhava Bala components). Distinct from Ashtakavargam SAV house scoring. | BPHS Ch.31 |
| **E21** | **Vimshopaka Bala** | 20-point multi-varga weighted strength (Sapta/Dasa/Shodasa-varga schemes). Used for planet-strength via divisional dignity. | BPHS Ch.7 |
| **E22** | **Avastha Suite** | Baladi 5-fold (Bala/Kumara/Yuva/Vriddha/Mrita) + Jagrat-Swapna-Sushupti 3-fold + Lajjitadi 6-fold + 9-fold (Deepta/Swastha/Mudita/Shanta/Dinam/Duhkhita/Khala/Kopam/Sobhita) + 12-fold. Arohana-Avarohana + Naisargika Karaka enumeration. | BPHS Ch.45–46 |
| **E23** | **Panchadha Maitri** | 5-fold composite friendship (natural + temporal + composite maitri). Foundational input to Sthana Bala and dignity assessment. Can be bundled with E19 Shadbalam if desired. | BPHS Ch.3 |
| **E24** | **Janma-Tara 9-Cycle** | Tara cycle counted from natal natchathiram: Janma/Sampat/Vipat/Kshema/Pratyari/Sadhaka/Vadha-Naidhana/Mitra/Ati-Mitra. Heavily used in Tamil/South Indian muhurtham. Daily Tara checked against natal Tara for favorability. | Muhurta Chintamani Ch.3 |
| **E25** | **Ashtakoota Milan + Manglik Engine** | 8-kuta compatibility scoring: Varna/Vashya/Tara/Yoni/Graha-Maitri/Gana/Bhakoot/Nadi. Includes Manglik (Mangal Dosha) variants per placement + cancellations, Rajju Dosha, Nadi Dosha exception rules (same-rasi, same-Gotra), Papasamya. Promotes existing codebase Kuta Milan to rule-registry with source variants. | BPHS Ch.5 + Muhurta Chintamani Ch.5 |
| **E26** | **Special Lagnas Suite** | 10+ specialized ascendants: Bhava Lagna (1 rasi per 2h from sunrise), Hora Lagna (1 rasi per 1h), Ghati Lagna (1 rasi per 24min), Vighati Lagna (1 rasi per 24sec), Sri Lagna (Moon-based), Indu Lagna (wealth point), Pranapada Lagna (life-breath point), Varnada Lagna (varna-based life phase), Nisheka Lagna, Vakra-Shoola points. Surya/Chandra Lagnas (covered under E18 Sudarshana). | BPHS Ch.4, Ch.85 |
| **E27** | **Maraka-Badhaka Engine** | Longevity/misfortune timing via Maraka (death-dealer) and Badhaka (obstructor) house/lord analysis. Pairs with E5b Ayus. Currently zero explicit PRD coverage despite being central to longevity interpretation. | BPHS Ch.44, 74 |
| **E28** | **Upaya / Remedies Engine** | Rule-registry mapping detected doshas/weak grahas/afflicted bhavas → Upaya recommendations: Mantra · Yantra · Tantra · Daan · Vrata · Rudraksha · Gemstone · Temple-deity correlations. Biggest end-user-visible gap — users expect "why? + what to do" but current scope only computes doshas without remedies. | Ramayana / Purana references + classical Parashari commentaries |
| **E29** | **Thirumana Porutham (Tamil 10-Porutham)** | Tamil marriage-matching system distinct from pan-Indian Ashtakoota. 10 poruthams: Dina / Gana / Mahendra / Stree-Deerga / Yoni / Rasi / Rasyathipathi / Vashya / Rajju / Vedha. Critical for Tamil user base. | Tamil Vakya Panchangam + regional Tamil nūl sources |

### Important (2 PRDs) — Phase P2 (or late P2/early P3)

| PRD ID | Title | Description | Classical source |
|---|---|---|---|
| **E1c** | **Extended Dasa Pack** | Bundle for less-common Parashari + Jaimini dasas: Sthira Dasa (Jaimini), Shoola Dasa (Jaimini maraka-timing), Drig Dasa (Jaimini 9th-house spiritual), **Tara Dasa (Tamil Parashari — critical for TN users)**, Kendra Dasa, Trikona Dasa, Brahma Dasa, Niryana Shoola Dasa, minor kalpas (Dwadashottari, Panchottari, Shatabdika, Chathurseethi-sama, Dwisaptati-sama — all behind feature-flag for niche use). Builds on E1a (Multi-Dasai v1) + E1b (Multi-Dasai v2). | BPHS Ch.46–53 + Jaimini Upadesha Sutras |
| **E6b** | **Transit Intelligence v2** | Transit Ashtakavargam Engine (transit-time SAV + Kaksha Vibhaga-in-transit), Vedha (natchathiram-based transit obstruction rules per Parashara gochara-phala), Tara Bala + Chandra Bala engine PRDs (locked in DECISIONS 2.2 but no engine spec), Lattha (retrograde-impact transit rules), Graha-Karaka transit interaction, Kal Sarpa transit activations, Ashtakavargam Transit Phala per house. Builds on E6a (Transit v1). | BPHS Ch.40 + Phaladeepika Ch.26 + Muhurta Chintamani |

### Total new PRDs: 13 (11 critical + 2 important)

---

## Section 2 — Existing PRDs to extend (11 extensions)

| PRD | Extension required |
|---|---|
| **P1/E2a Ashtakavarga v2** | Promote Kaksha Vibhaga from "Optional Stage 7" to in-scope (per DECISIONS 1.8 astrologer lock-in). Add transit-Ashtakavargam hook for E6b. |
| **P1/E4a Yoga Engine MVP** | Explicitly enumerate Yoga Karaka per-ascendant table; add Naisargika Karaka dimension; verify Spasta Drishti (degree-based aspect intensity) handling. |
| **P1/E6a Transit v1** | Add Vedha (natchathiram obstruction) + Tara Bala / Chandra Bala natal-dependent transit computations per DECISIONS 2.4 phase 5. Nakshatra Sandhi / Gandanta handling. |
| **P2/E1b Multi-Dasai v2** | Explicit note that Sthira/Shoola/Drig/Tara-Dasai are deferred to new E1c (scope clarity). |
| **P2/E3 Jaimini System** | Generalize Argala / Virodha Argala to any reference bhava (not only Arudha Lagna). |
| **P2/E4b Yoga Engine Full 250** | Complete Kaal Sarpa to all 12 variants (currently 8 — add Shankhachur, Ghatak, Vishdhar, Sheshnag). Verify Mangal Dosha variants + cancellations explicit. Add Daridra/Vishnu/Daina/Maha/Jaya yogas if absent. Dashamsha (D10) specific yogas. |
| **P2/E5b Ayus (Longevity) Suite** | Explicit callout to Maraka/Badhaka bhava computation as dependency on E27. Amsha Bala (divisional strength) — fold into E21 Vimshopaka. |
| **P2/E7 Extended Vargas + SBC + Upagrahas** | **Add 5 Sphuta sensitive points to scope: Beeja Sphuta, Kshetra Sphuta, Deha Sphuta, Mrityu Sphuta, Pranapada Sphuta** (MaitreyaGapAnalysis flagged, verified absent from E7 body). |
| **P2/E10 Prasna / Horary** | Explicit Tajaka Prasna mode callout + Arudha-based Prasna mode. |
| **P2/E12 Astrologer Workbench UI** | Add workbench tabs/panels for: Shadbalam (E19), Bhava Bala (E20), Vimshopaka Bala (E21), Avastha Suite (E22), Panchadha Maitri (E23), Special Lagnas (E26), Ashtakoota Milan (E25), Thirumana Porutham (E29), Upaya Engine (E28), Maraka-Badhaka (E27). All currently absent from workbench design. |
| **P4/Reference-1000 Yogas** | Explicit slot for Pancha Mahapurusha timing-qualities + regional Tamil/Bengali yoga variants. |

---

## Section 3 — Deferred to future roadmap

### Nice-to-have (15 — defer)
- Additional minor dasas: Saptarishi (Shodasottari 116-yr), Dwadashottari (112-yr), Panchottari (105-yr), Shataabdika (100-yr), Chathurseethi-sama (84-yr), Dwisaptati-sama (72-yr) — all lineage-specific
- Graha-Karaka transit integration (fold into E6b later if demand)
- Kal Sarpa transit activations (fold into E6b later)
- Natchathiram-Pada yoga rules beyond basic
- Janma Natchathiram Phala interpretation layer (fold into E11b)
- Pada Lagna / Dwara Pada (argala extensions — fold into E3 or E26 later)
- Arohana-Avarohana (fold into E22 if explicit treatment wanted)
- Bhava Karaka enumeration (fold into E20/E22)
- Upachaya/Apachaya classification reusable predicate
- Vakra-Shoola points (fold into E26)
- Shodhasha Sanjna (16-fold time categorization)
- Kala-Varna classification
- Pancha Maha Purusha timing-qualities
- Bhavaya Varna (timing varna for muhurtham)
- Anga-lipta (partial-day categorization)

### Optional / Regional / Market-dependent
- Kerala Pothunana compatibility method
- Bengali Kundli-Milan regional variant
- Ashtamangala Deva Prasna (Kerala ritual)
- Kala Chakra transit triggers
- Varnada Lagna as standalone (fold into E26)
- Vakya Siddhanta engine (DECISIONS 3.4 already notes as P2/P3 roadmap)
- Parahita Siddhanta (Kerala hybrid — DECISIONS 3.4 already defers)

---

## Section 4 — Scope expansion summary

| Measure | Before | After | Delta |
|---|:-:|:-:|:-:|
| Total PRDs | 76 | **89** | +13 |
| P2 phase PRDs | 14 | **~25** | +11 |
| P2 phase themes | Breadth & UIs | Breadth & UIs + **Strength/Remedies/Matching/Special-Lagnas** | — |
| Parashari-JH parity | ~70% | ~98% | +28% |

### P2 phase re-composition (14 → ~25)

| Existing P2 PRDs (14) | New P2 additions (11) |
|---|---|
| E1b Multi-Dasai v2 | E19 Shadbalam Engine |
| E3 Jaimini System | E20 Bhava Bala Engine |
| E4b Yoga Engine Full (250) | E21 Vimshopaka Bala |
| E5 Varshaphala (Tajaka) | E22 Avastha Suite |
| E5b Full Ayus | E23 Panchadha Maitri |
| E7 Extended Vargas + SBC + Upagrahas | E24 Janma-Tara 9-Cycle |
| E8 Western Depth | E25 Ashtakoota Milan + Manglik |
| E8b Asteroids | E26 Special Lagnas Suite |
| E9 KP System | E27 Maraka-Badhaka Engine |
| E10 Prasna / Horary | E28 Upaya / Remedies Engine |
| E11b AI Chat Debate Mode | E29 Thirumana Porutham |
| E12 Astrologer Workbench UI | E18 Sudarshana Chakra (locked in DECISIONS 1.9) |
| E13 End-User Simplification UI | E1c Extended Dasa Pack |
| E17 Chart Rectification | E6b Transit Intelligence v2 |

---

## Section 5 — Action items for implementation

### For PRD-writing phase (separate from decision-review phase):

1. **Create 13 new PRD files** under `docs/markdown/prd/P2/` (or P3 as appropriate) using the `_TEMPLATE.md` format. Each must include frontmatter, purpose, classical research, component design, user stories, tasks, tests, acceptance criteria, risks, and cross-references to `DECISIONS.md` for any already-locked decisions.
2. **Update 11 existing PRD files** with the specified extensions. Bump `last_updated` frontmatter. Log changes in `review.md` notes section.
3. **Update `INDEX.md`** to include the 13 new PRDs with their phase assignments, tags, priorities, dependencies, and enables.
4. **Update `review.md` tracker** — the 89-row review table with ⬜ status for the new PRDs.

### For the cross-cutting updates:

5. **Reference this file from DECISIONS.md** to preserve the audit trail.
6. **Reference the full gap-finding agent report** (saved in task output file) as a provenance record.

---

## Section 6 — Provenance

- **Gap survey conducted:** 2026-04-20
- **Methodology:** Background research agent spawned with 12-category Parashari classical technique checklist; cross-referenced against all 76 PRDs + DECISIONS.md + MaitreyaGapAnalysis.md + HighLevelYogasVargas.md.
- **User decision:** Option A (full closure) locked 2026-04-20 during PRD review Pass 1.
- **Source files referenced:**
  - `docs/markdown/prd/INDEX.md`
  - `docs/markdown/prd/DECISIONS.md`
  - `docs/markdown/prd/MaitreyaGapAnalysis.md`
  - `docs/markdown/prd/HighLevelYogasVargas.md`
  - `docs/markdown/prd/TAMIL_NAMING_AUDIT.md`
  - `docs/markdown/prd/PRODUCT_STORIES.md`
  - All 76 PRD files across P0–P6 phase directories

---

**Maintenance.** As each new PRD is written, append a row to section 5's action item list with its created-date and PR reference. When an extension is applied to an existing PRD, log the specific change in that PRD's file + bump `last_updated`.
