# Josi — Cross-Cutting & Panchangam Decisions Log

**Purpose.** Durable record of every astrological/calculation decision locked during PRD review. Survives conversation compaction. Serves as authoritative input to PRD updates and source-of-truth for implementation.

**Review role.** Decisions are locked by the user (Parashari astrologer, calculation-side review). UX and user flows are owned by Govind and are out of scope here.

**Two-user-types framework.** Every decision addresses both:
- **End-user consumer (B2C)** — sensible default, one path, no options surfaced
- **Astrologer** — configurable, options surfaced at chart-calculation time or saved in profile

When a decision doesn't answer both sides, it's flagged.

**Legend:** 🔒 locked · 🟡 pending research · ⏳ deferred · 🚧 blocked

---

## 1. Cross-cutting chart calculation pipeline

### 1.1 Rahu/Ketu node computation 🔒

- **Compute both Mean Node AND True Node** for Rahu and Ketu on every chart. Store both.
- **End-user (B2C) default:** **Mean Node.** Matches Parashari Tamil lineage + every major Indian published panchang (Drik Panchang, Rashtriya Panchang, Kalnirnay) + JH default. Smoother motion, classical BPHS canonical. (Revised 2026-04-22 from prior True Node default after classical-soundness quality pass flagged mismatch with ecosystem norm.)
- **Astrologer:** prompted at chart calculation time to pick Mean or True (no default override at profile level — per-chart choice).
- Current code uses `swe.MEAN_NODE` — already matches B2C default. Extension needed: compute True Node in parallel and store alongside for astrologer toggle + audit.

### 1.2 Ayanamsa 🔒 (Option A — agent recommendation accepted)

- **End-user (B2C) default:** Lahiri (Chitrapaksha Official) = Government of India official ayanamsa adopted by Indian Calendar Reform Committee 1955 = `SIDM_LAHIRI`. Value ~23°51'11" at J2000.0. Places Chitra (Spica) at ~180° sidereal longitude. Matches Rashtriya Panchang, Drik Panchang, Kalnirnay, Indian Ephemeris.
- **Astrologer shortlist (9 total) — selectable per profile:**
  1. Lahiri (Chitrapaksha Official) — `SIDM_LAHIRI`
  2. Raman — `SIDM_RAMAN` (B.V. Raman South Indian lineage)
  3. Krishnamurti (KP) — `SIDM_KRISHNAMURTI` (required for KP engine E9)
  4. True Chithirai — `SIDM_TRUE_CITRA` (Spica exactly 180°; JH default)
  5. Yukteshwar — `SIDM_YUKTESHWAR` (Sri Yukteshwar, SRF/Kriya tradition)
  6. J.N. Bhasin — `SIDM_JN_BHASIN` (North Indian Parashari lineage)
  7. Suryasiddhantha — `SIDM_SURYASIDDHANTA` (classical text-derived)
  8. True Poosam — `SIDM_TRUE_PUSHYA` (true-star ayanamsa; JH researcher-favorite)
  9. Fagan-Bradley — `SIDM_FAGAN_BRADLEY` (Western sidereal; for cross-tradition + B2B API)
- **Advanced/research dropdown (opt-in for power users and B2B API):** remaining ~34 Swiss Ephemeris constants including Babylonian variants (Kugler 1/2/3, Huber, Britton, ETPSC), Galactic Center family (0°Sag, Wilhelm, Cochrane, Mardyks, IAU-1958), Hipparchos, Sassanian, Djwhal Khul, DeLuce, Aldebaran 15 Taurus, J2000/J1900/B1950 epochs, Ushashashi, Valens Moon, True Revathi, True Moolam, True Sheoran, SS Chithirai, SS Revathi, Lahiri refinements (1940/VP285/ICRC), Krishnamurti VP291, user-defined offset.
- **Current code:** `astrology_service.py:56` already defaults to `'lahiri'` via `swe.SIDM_LAHIRI`. ✅ No change needed for B2C.
- **Action:** extend enum/UI to expose the 9-shortlist to astrologer profile and the advanced dropdown to B2B API.

### 1.3 House system 🔒 (Option A — agent recommendation accepted + bug fix)

- **End-user (B2C) default:** Whole Sign (`W`) — classical Parashari canonical (BPHS default), polar-stable, maps cleanly to sign-lordship aspects/dasas/yogas.
- **Parallel secondary chart:** **Bhava Chalit / Sripati (`S`) auto-computed** alongside rasi chart for every chart. Surface as secondary "bhava chart" panel. Classical Parashari dual-chart method.
- **Astrologer shortlist (6 systems) — selectable per profile:**
  1. Whole Sign (`W`) — Parashari primary
  2. Bhava Chalit / Sripati (`S`) — Parashari bhava chart
  3. Equal House from Lagna (`E`) — Parashari alt + sidereal Western
  4. Placidus (`P`) — **required for KP engine E9**; also Western default
  5. Koch (`K`) — modern Western (German tradition)
  6. Porphyry (`O`) — Hellenistic + Jyotish bhava alt
- **Advanced dropdown (opt-in for power users and B2B API):** Regiomontanus (`R`), Campanus (`C`), Meridian / Axial Rotation (`X`), Alcabitius (`B`), Topocentric / Polich-Page (`T`), Morinus (`M`), Krusinski (`U`), APC (`Y`), Pullen SR (`L`), Pullen SD (`Q`), Vehlow Equal (`V`), Equal/MC (`D`), Equal from Aries (`N`), Carter Poli-Equatorial (`F`), Sunshine (`I`), Gauquelin Sectors (`G`, research-only).
- **Bug fix required (5-file change set) — current code defaults Placidus for Vedic, classically incorrect:**
  1. `src/josi/services/astrology_service.py:160` — change `calculate_vedic_chart` default from `'placidus'` → `'whole_sign'`
  2. `src/josi/services/astrology_service.py:180-190` — verify `house_systems` dict has Whole Sign (`b'W'`) + Bhava Chalit/Sripati (`b'S'`) entries; extend if missing
  3. `src/josi/enums/house_system_enum.py` — ensure WHOLE_SIGN + BHAVA_CHALIT entries present; add SE character-code second tuple field
  4. `src/josi/services/bhava_calculator.py` — verify Bhava Chalit logic uses Sripati midpoint semantics (`'S'`) not Placidus-derived cusps
  5. `src/josi/models/chart_model.py:20` — migrate DB default `"placidus"` → `"whole_sign"`; backfill existing chart records where house_system was Placidus (preserve records created with explicit Placidus, default-only records migrate)
- **KP engine binding:** when astrologer uses KP engine (E9), house system auto-forces to Placidus + KP ayanamsa (Krishnamurti) regardless of profile preference. Pair is classically mandatory.

### 1.4 Vimshottari dasa depth 🔒

- **Both user types see 5 levels:** Mahadasa → Antardasa → Pratyantardasa → Sookshma → Prana.
- Compute once, render the same for both. No user-type split.
- Applies to E1a PRD (Multi-Dasa v1) and existing Vimshottari in `dasa_calculator.py`.

### 1.5 Language display policy 🔒

- **App display format: English-transliteration (Sanskrit IAST) + user's regional language, side-by-side.** Language selector in the app UI drives the regional pair.
- **English side is ALWAYS transliteration (Sanskrit IAST)**, never translation. E.g., "Mṛgaśīrā" not "Orion" or "Deer-head"; "Sūrya" not "Sun"; "Meṣa" not "Aries"; "Bṛhaspati" / "Guru" not "Jupiter".
- **Regional side** defaults to user's selected language: Tamil (தமிழ்), Hindi/Sanskrit-Devanagari (देवनागरी), Telugu (తెలుగు), Kannada (ಕನ್ನಡ), Malayalam (മലയാളം), Bengali (বাংলা), Gujarati (ગુજરાતી), Marathi (मराठी).
- **Both user types** — B2C and Astrologer. No difference in display format policy; only regional-side language may differ by user profile.
- **Existing schema supports this.** E1a PRD `classical_names` YAML field has `en` (meaning "English gloss — to be deprecated/repurposed"), `sa_iast` (transliteration), `sa_devanagari` (Sanskrit script), `ta` (Tamil). Action items:
  - Schema update: add `hi`, `te`, `kn`, `ml`, `bn`, `gu`, `mr` fields to `classical_names`.
  - Audit/fill all canonical entities: 27 nakshatras · 12 rashis · 9 grahas · 16 vargas · 60 Samvatsaras · tithi names · karana names · yoga names · panchaka subtypes · muhurta labels · auspicious/inauspicious yoga names.
  - B2C UI + AI chat: render `sa_iast + regional` pair based on user language setting; never render `en` translation.
- **Conversational convention (this review process):** Use **Tamil phonetic transliteration ONLY** — no Tamil script, no IAST diacritics. Examples: "Dasai" not "Daśā" or "தசை"; "Uthiradam" not "Uttara Āṣāḍhā"; "Nazhigai" not "ghati"; "Emakandam" not "Yamagaṇḍa"; "Kuligai" not "Gulika Kāla"; "Pradosham" not "Pradoṣa"; "Karthikai" not "Kṛttikā"; "Sooriyan" not "Sūrya"; "Mirugasirsham" not "Mṛgaśīrā". Where a Tamil-specific term exists (nazhigai, emakandam, kuligai, pongal), use that over the Sanskrit term. Durable docs (PRDs, DECISIONS.md itself) continue to use Sanskrit-IAST as canonical for cross-reference stability across multi-tradition use.
- **Hora exception 🔒 (revised 2026-04-22):** Use **"Hora"** (Sanskrit-IAST form without macron) instead of Tamil phonetic "Horai" throughout — because the same word refers to 3 distinct classical concepts that need disambiguating qualifiers: (a) **Hora Bala** — Kala Bala sub-component per BPHS Ch.27; (b) **Hora Lagna** — Special Lagna per BPHS Ch.4; (c) **Hora** (standalone) — Chaldean planetary hour per §3.11. The qualifier ("Bala" / "Lagna" / standalone) carries the disambiguation. Using "Horai" for all three creates ambiguity with no benefit. This is a targeted exception to the Tamil-phonetic rule; other Tamil-phonetic terms (Dasai, Uthiradam, Nazhigai, Kuligai, etc.) remain unchanged.

- **Foreign-language support scope 🔒 (locked 2026-04-23, Option A — Indian-only policy continued):** The 8 Indian regional languages listed above (Tamil, Hindi, Telugu, Kannada, Malayalam, Bengali, Gujarati, Marathi) + Sanskrit-IAST English transliteration remain the only supported display languages for **P1 / P2 / P3**. Foreign languages (Spanish, French, Portuguese, German, Chinese, Arabic, Russian, etc.) are **out of scope**. Rationale: (a) Vedic is the primary engine and Indian regional market is the primary audience for v1–v3; (b) non-Vedic traditions (Western, Chinese, Hellenistic, Mayan, Celtic) are not yet fully specced and premature foreign-language work would lock in compromises; (c) global B2B API consumers can consume `sa_iast` canonical and localize in their own UI layer; (d) AI interpretation language (GPT/Claude output) can already adapt naturally without schema changes. Revisit at **P4 or later** if global non-diaspora demand materializes; at that point likely adopt tradition-native rendering per tradition's classical canon (Western = English common names, Hellenistic = Greek, Chinese = Chinese, etc.) — deferred decision.

- **Ambiguity editorial locks 🔒 (Option A — agent recommendations accepted).** Primary Tamil phonetic spellings locked for all 14 ambiguous entries from `TAMIL_NAMING_AUDIT.md`:

  | # | Entity (IAST) | Primary Tamil phonetic | Alternates (notes-only) |
  |:-:|---|---|---|
  | 1 | Mṛgaśīrā | **Mirugasirsham** | Mrigasheersham, Mirugasirisham |
  | 2 | Punarvasu | **Punarpoosam** | Punarvasu |
  | 3 | Hasta | **Hastham** | Astham |
  | 4 | Viśākhā | **Visakam** | Vishakam |
  | 5 | Śatabhiṣā | **Sathayam** | Sadayam |
  | 6 | Pramoda (Samvatsara #4) | **Pramodhootha** | Pramoda |
  | 7 | Śrīmukha (Samvatsara #7) | **Srimukha** | Sreemukha (Tamil Brahmin publications) |
  | 8 | Vṛṣa (Samvatsara #15) | **Visu** | Vrisha |
  | 9 | Subhānu (Samvatsara #17) | **Subanu** | Swabanu, Svabhanu |
  | 10 | Paridhāvī (Samvatsara #46) | **Paridhabi** | Paridhavi |
  | 11 | Raudra (Samvatsara #54) | **Roudhri** | Raudra |
  | 12 | Dyumad-gadyuti (Muhurta #28) | **Dyumadgadyuthi** | (rare in Tamil; fallback IAST-phonetic) |
  | 13 | Bṛhaspati/Guru (Graha) | **Guru** (planet context) | Viyalan (Thursday weekday context only) |
  | 14 | Maṅgala (Graha) | **Sevvai** (planet + weekday) | Angarakan, Mangal |

  Alternates retained in seed-data migration as searchable aliases (for cross-verification with other Tamil panchangam sources) but NEVER rendered in UI.

### 1.6 Ashtottari Dasai eligibility predicate 🔒

- **Permissive default for both user types** — Ashtottari Dasai always computed and shown on every chart (no BPHS Ch.47 gating applied).
- Aligns with Jagannatha Hora 7.x behavior and Jataka Parijata permissive tradition.
- **Astrologer override:** individual astrologers can set their per-profile preference to filter to BPHS strict activation (Krishna Paksham + Lagnam-benefic + night birth + Rahu-not-in-Lagnam — all 4 conditions) via F2 `astrologer_source_preference` table.
- Rule YAML encodes both variants (strict + permissive) as sibling rules; permissive chosen as Josi default via `effective_from` on the permissive variant.
- Vimshottari (120yr) and Yogini (36yr) have no eligibility predicate — always applied to all charts.

### 1.7 Shadbalam — Budhan classification + display 🔒

**Budhan benefic/malefic classification policy** (Option C — compute both):
- Josi computes **BOTH Shadbalam values always** for every chart: (i) Budhan-classified-as-benefic, (ii) Budhan-classified-as-malefic.
- Stores both in `technique_compute` with a discriminator `classification: benefic | malefic | classical_auto`.
- **B2C:** renders the classical context-dependent value (applies BPHS Ch.27 v.11 — evaluates Budhan's associates via conjunction, aspect, to auto-classify). Single number.
- **Astrologer:** sees both values + classical classification label ("classical rule: malefic due to Sooriyan conjunction") + a flip toggle + delta annotation ("flipping to benefic changes Shadbalam by +44 rupas"). Can override per chart.
- Same policy extends to **Chandran classification** (unambiguous — Shukla Paksham = benefic, Krishna Paksham = malefic; no ambiguity so no dual computation needed).
- Rationale: Budhan's classification is the ONE genuine classical ambiguity in Shadbalam. Computing both lets AI chat and astrologer surface the uncertainty rather than hide it behind an auto-classification.

**Display format** (Option E — full transparency):
- **Both user types see:** rupas (classical) + percentage of threshold + pass/fail badge + 6-component breakdown (Sthana/Dik/Kala/Chesta/Naisargika/Drik individually in rupas).
- Example output:
  ```
  Budhan Shadbalam: 7.52 rupas (451 virupas) · 107% of threshold · PASSES ✓
    Sthana 2.10 · Dik 0.85 · Kala 2.30 · Chesta 0.95 · Naisargika 0.67 · Drik 0.65
    Threshold: 7.0 rupas (BPHS Ch.27)
    Classification: malefic (classical — Sooriyan conjunction)  [Astrologer toggle]
  ```
- Minimum thresholds per graha (BPHS Ch.27):
  - Sooriyan 6.5 · Chandran 6.0 · Sevvai 5.0 · Budhan 7.0 · Guru 6.5 · **Sukkiran 5.5** · Sani 5.0 rupas
  - Sukkiran threshold 5.5 ratified 2026-04-22 by reviewer (vs Raman's *Graha and Bhava Balas* variant of 5.25). BPHS Ch.27 canonical value is 5.5 rupas; Raman's 5.25 is a lineage-specific refinement not adopted.
- Astrologer-only additional data: virupa-level precision, component formula trace, Ishta-Kashta Phala derivation.

### 1.8 Ashtakavargam scope and display 🔒

**Computation pipeline (6 stages per BPHS Ch.66–67):**
1. Bhinnashtakavargam (BAV) — per-graha 12-rasi × 8-contributor matrices
2. Raw Sarvashtakavargam (Raw SAV) — column sum across 7 grahas
3. Trikona Shodhanai (Trinal Purification) applied per BAV (BPHS 66.1–5)
4. Ekadhipatya Shodhanai (Dual-Lordship Purification) applied per BAV (BPHS 66.6–15)
5. Shodhit SAV — column sum of doubly-shodhit BAVs (the interpretively meaningful SAV)
6. Sodhya Pinda per graha — feeds Ayurdaya (E5b) and transit phalita
- Optional Stage 7: Kaksha Vibhaga (96 kaksha subdivisions, 3°45' each)

**Chart scope (Option Y — modern Parashari extension):**
- **D1 (rasi chart)** — full Ashtakavargam computation (BAV + SAV + Shodhanai + Sodhya Pinda + Kaksha). Classical Parashari primary.
- **D9 (Navamsa)** — full Ashtakavargam computation (modern extension; Sanjay Rath, Rath lineage advocates use D9 Ashtakavargam for dharma-bhava refinement).
- **D10 / D12 / other vargas** — not computed in this scope (deferred).

**B2C display (Option A):**
- Single view: **3-tier bhava-strength summary from post-shodhanai SAV** (strong ≥30 bindus · moderate 25–29 · needs effort <25 — thresholds illustrative; calibrate per BPHS conventions).
- Each bhava labeled with purpose string from BPHS Ch.6 (locked in 1.8 Divisional chart purpose metadata).
- Heatmap visualization (colored bars per bhava).
- Raw BAV matrices hidden by default; "expand" toggle reveals astrologer view on demand.
- No Sodhya Pinda exposure (astrologer-only, feeds Ayurdaya which has ethical gating).
- No Kaksha Vibhaga exposure.

**Astrologer display (full transparency, 5 tabs + panel):**
1. Tab 1: Raw BAV — 7 graha matrices × 12 rasis × 8 contributors with contributor-trace per cell
2. Tab 2: Trikona-Shodhit BAV per graha with trine-group reduction trace
3. Tab 3: Ekadhipatya-Shodhit BAV per graha with dual-lordship reduction trace
4. Tab 4: Sarvashtakavargam — Raw SAV + Shodhit SAV side-by-side, bhava mapping per BPHS Ch.6
5. Tab 5: Sodhya Pinda — per-graha Pinda values with Graha Pinda + Rashi Pinda factors exposed; feeds E5b Ayurdaya
- Panel: Kaksha Vibhaga toggle — per-graha 96-kaksha strength view
- Transit Ashtakavargam (current transit-chart strength per graha per rasi)
- D9 Ashtakavargam toggle — full 5-tab view applied to Navamsa chart
- Contributor-trace drill-down per cell

**Trikona Shodhanai variant 🔒 (Option A — Phaladeepika 3-case rule; revised 2026-04-22):**

For each trine (1-5-9, 2-6-10, 3-7-11, 4-8-12), apply the following 3-case rule to `(s1, s2, s3)`:

1. **If `min(s1, s2, s3) == 0`** → zero all three: `(0, 0, 0)`. Rationale: any zero-bindu member pollutes the trine; classical Phaladeepika treats the trine as a unit that collapses when any member is void.
2. **Else if the minimum value appears in 2 or more members (tie at the bottom)** → zero all three: `(0, 0, 0)`. Rationale: no single sign stands out as the unique weak member; excess at the top is considered redundant and stripped.
3. **Else (unique minimum > 0)** → subtract minimum from all three members.

**Worked examples:**
- `(5, 3, 4)` → min=3, unique, >0 → `(2, 0, 1)` *(normal subtract)*
- `(0, 2, 3)` → min=0 → `(0, 0, 0)` *(edge case 1)*
- `(3, 3, 5)` → min=3, appears twice → `(0, 0, 0)` *(edge case 2)*
- `(4, 2, 2)` → min=2, appears twice → `(0, 0, 0)` *(edge case 2)*
- `(6, 4, 5)` → min=4, unique, >0 → `(2, 0, 1)` *(normal subtract)*

Same for both user types.

**Classical sources:** Phaladeepika Ch.26 v.12-18 (Mantreswara — spells out the edge cases that BPHS Ch.40 v.39-42 leaves terse); implemented identically in Jagannatha Hora and Parashara's Light.

**Revision note:** Prior version (pre-2026-04-22) locked a simple "subtract-minimum" rule without edge cases 1 and 2. Classical-soundness quality pass on 2026-04-22 flagged that this would systematically over-report Shodhit SAV for any chart where a trine contains (a) any zero-bindu sign or (b) a tie at the minimum — both common conditions. Revised to the full 3-case rule.

### 1.9 Sudarshana Chakra 🔒 (new dedicated PRD E18)

**Technique.** Triple-chakra composite reading — three concentric rasi charts anchored at Lagna, Sooriyan, and Chandran rasis. A bhava-matter is classical-certain when affirmed across all three chakras.

**PRD scope (create E18 Sudarshana Chakra + Triple-Affirmation Analysis):**
- Rendering engine: three concentric overlays with rasi/bhava labels per chakra
- Analysis engine: per-bhava triple-agreement evaluator (output: 3/3 certain · 2/3 probable · 1/3 partial · 0/3 disagreement)
- AI tool-use extension: `get_sudarshana_reading(chart_id, bhava)` returns triple-chakra agreement level + classical interpretation
- Classical source: Jataka Parijata Ch.11, Sarvartha Chintamani, BPHS references

**Computation:** zero new ephemeris calls — pure view/analysis layer over existing chart data. Cost trivial (36 lookups per chart).

**Rendering style — regional auto-adapt (Option A):**
- **North Indian (diamond / house-fixed):** three concentric diamond frames. Outer=Lagna chakra, middle=Surya chakra, inner=Chandra chakra. Houses fixed in position; rasis shift per chakra.
- **South Indian (square / rasi-fixed):** three concentric square frames. Rasis fixed in position; bhava numbers shift per chakra.
- **East Indian (circular):** three concentric circles, rasis in fixed clock-face positions.
- **B2C auto-detect by user region:** Tamil/Malayalam/Telugu/Kannada → South · Hindi/Gujarati/Marathi/Punjabi → North · Bengali/Oriya → East.
- **Astrologer:** all three styles available via toggle; user's region as default.

**Scope note:** was a flagged GAP in the 76-PRD original scope. Added as E18 to close the gap. Will appear in P2 (Breadth & UIs) phase per dependency on completed chart engine.

### 1.10 Divisional chart purpose metadata 🔒

- Store canonical purpose/usage string per varga alongside chart data. Available to UI + AI chat.
- **Source:** BPHS Ch.6 canonical mapping.
- **Same for both user types.**

| Varga | Name | Purpose |
|---|---|---|
| D1 | Rashi | Body, overall life |
| D2 | Hora | Wealth |
| D3 | Drekkana | Siblings |
| D4 | Chaturthamsa | Property, fortune |
| D7 | Saptamsa | Children, progeny |
| D9 | Navamsa | Spouse, dharma |
| D10 | Dasamsa | Career, profession |
| D12 | Dwadashamsa | Parents |
| D16 | Shodasamsa | Vehicles, luxuries |
| D20 | Vimsamsa | Spiritual pursuits |
| D24 | Chaturvimsamsa | Education, learning |
| D27 | Bhamsa | Strengths, weaknesses |
| D30 | Trimsamsa | Misfortunes, afflictions |
| D40 | Khavedamsa | Auspicious/inauspicious effects |
| D45 | Akshavedamsa | General life effects |
| D60 | Shashtiamsa | All matters, past karma |

---

## 2. Panchangam decisions — macro

### 2.1 B2C Daily Panchangam — scope 🔒 (Option D)

8-section B2C default with **regional overlay auto-adaptation**:

1. **Date header:** Gregorian · Vikram Samvat · Shaka Samvat · Samvatsara · Ayana · Ritu · Masa (Amanta+Purnimanta) · Paksha · Regional solar month (auto-detect by user region)
2. **Panch-anga:** Tithi · Vaara · Nakshatra+Pada · Yoga · Karana — each with end-time
3. **Sun/Moon:** Sunrise · Sunset · Moonrise · Moonset · Day-length
4. **Auspicious windows:** Abhijit · Brahma · Amrit Kala · Guru/Ravi Pushya flag · Amrita-Siddhi/Sarvartha-Siddhi flags
5. **Inauspicious windows:** Rahu Kala · Yamagandam · Gulika · Dur Muhurta · Varjyam · Bhadra/Vishti
6. **Choghadiya** (day 8 + night 8) — auto-adapts per region (Choghadiya for North; Tamil Nalla Neram for Tamil users; Bengali Dinmaan/Ratrimaan for Bengali; Malayalam Kolla Varsham/Uchhaaram for Malayalam; Telugu Panchanga Shravanam for Telugu; Gujarati Labh Panchami marker for Gujarati)
7. **Festival/observance tag** (Ekadashi/Pradosha/Sankashti/Purnima/Amavasya/named festivals)
8. **Dishashoola** badge (direction to avoid today)

**Region detection source:** UX — Govind's call (birth location / current location / profile preference).

**Calculation implication:** Josi computes ALL regional variants for every chart, stores all, UI picks which to surface based on user region.

### 2.2 Astrologer Full Panchangam — scope 🔒 (Option A)

B2C defaults + 12 additional sections:

1. **Time grids:** Ghati/Vighati toggle · 30 muhurtas of day · 8 prahara · 5 Kala divisions (Pratah–Sangava–Madhyahna–Aparahna–Sayankala)
2. **24 Hora table:** day+night, planetary lords, Chaldean sequence
3. **Tara Bala + Chandra Bala:** relative to user's natal Moon-nakshatra and Moon-sign
4. **Auspicious yoga detector:** Siddha / Amrita-Siddhi / Sarvartha-Siddhi / Dwipushkar / Tripushkar / Ravi-yoga / Guru Pushya / Ravi Pushya
5. **Panchaka + Ganda Moola flags**
6. **Kulika, Ardha-prahara, Night-Rahu/Yama/Gulika**
7. **Sankranti clock:** countdown to next Sun-ingress
8. **Adhika/Kshaya Masa alerts**
9. **Eclipse contacts:** P1/P2/U1/U2/Max/U3/U4 for nearest solar + lunar
10. **Planetary events for today:** ingresses · retrograde flips · combustion · graha yuddha
11. **Regional overlay toggle:** astrologer can view any region's variants
12. **Ayanamsha selector + degree display:** picker from 9 ayanamsa options with real-time comparison

### 2.3 Sunrise/sunset convention 🔒 (Option A)

- **Center of Sun's disc at apparent horizon, with atmospheric refraction.**
- Matches Drik Panchang, mypanchang.com, Kalnirnay, Indian published almanacs.
- Swiss Eph flag: `SE_BIT_DISC_CENTER`.
- **Same convention for both user types.**
- Applies to ALL sunrise/sunset-anchored computations (muhurtas, Choghadiya, Hora, Rahu/Yama/Gulika, Abhijit, Brahma, 5 Kala, Prahara, day/night boundary).
- For Chennai 19 Apr 2026: Sunrise 05:55:28 IST · Sunset 18:23:10 IST (illustrative).

### 2.4 Build priority order 🔒 (Option B — Parashari-lens ordering)

Foundational dependencies resolved first; natal-chart-dependent items later.

| Phase | Items |
|:-:|---|
| 1. Foundational | Sankranti instant solver · Calendar layer (Shaka/Vikram/Kali/Samvatsara/Masa Amanta+Purnimanta/Paksha/Ayana/Ritu/Saura-masa + regional month names) |
| 2. Depends on foundational | Festival rule engine (Ekadashi/Pradosha/Sankashti/Purnima/Amavasya + named festivals) |
| 3. Quick-wins batch | Choghadiya · Dishashoola · Hora (day+night) · Night Rahu/Yama/Gulika · Panchaka + Ganda Moola · Muhurta/Ghati/Prahara grid · Moonrise/Moonset |
| 4. Shared-table batch | Nakshatra-percentile + vaara-nakshatra lookup tables → Dur Muhurta + Varjyam · Amrit Kala · Auspicious yoga detector |
| 5. Natal-chart-dependent | Tara Bala + Chandra Bala |
| 6. Astronomical events | Eclipses · Planetary events (ingresses, retrograde flips, combustion, graha yuddha) |
| 7. Regional overlays | Tamil Nalla Neram/Kari Naal/Lagna Nilai · Malayalam Kolla Varsham/Uchhaaram · Telugu Panchanga-Shravanam · Bengali Dinmaan/Ratrimaan · Gujarati Labh Panchami |

---

## 3. Panchangam decisions — nuances

### 3.1 Samvatsara numbering 🔒 (Option A)

- **South-Indian Prabhava-start cycle** is default for both user types.
- **Astrologer toggle:** North-Indian Barhaspatya cycle (~22-year offset).
- 2026 Chaitra = Vishwavasu (South) / Siddharthi (North).

### 3.2 Nakshatra-percentile table source 🔒 (Option B)

- **Muhurta Chintamani** is the single default source for Varjyam, Amrit Kala, Dur Muhurta for both user types.
- **Astrologer source-selector:** Muhurta Chintamani / Kalaprakashika / Narada Samhita (optics only — research found values near-identical across sources).
- Research finding: tables are textually identical across MC/Narada/Kalaprakashika for Varjyam and Dur Muhurta; only ~1-ghati (~24 min) boundary convention offset between sources.

### 3.3 Amrit Kala placement offset 🔒 (Option X)

- **Muhurta Chintamani offset:** Amrit Kala starts 8 ghatis after Varjya start (immediately after Varjya ends, same 4-ghati duration).
- **Same for both user types.**
- Matches Drik Panchang, mypanchang, Kalnirnay, JH.

### 3.4 Siddhanta school 🔒 (Option B)

- **Drik Siddhanta (astronomical / Swiss Ephemeris)** is default for both user types.
- **Astrologer profile option:** Vakya Siddhanta (fixed-formula Surya-Siddhanta-based) — build engine as P2/P3 roadmap item.
- When astrologer toggles Vakya, ALL panchang + chart calculations rebase to Vakya. B2C always stays Drik.
- Parahita Siddhanta (Kerala hybrid) deferred; can add in future roadmap if Kerala market demand warrants.
- Research finding: Vakya vs Drik is the single biggest divergence source for Kerala/traditional Tamil users (15–40 min sunrise delta, 1–5 arc-min planet-longitude delta).

### 3.5 Panchaka subtype computation 🔒 (Option D)

- **Both user types** see: Panchaka-active flag + subtype name + classical warning string + severity indicator.
- Panchaka active when Moon transits {Dhanishta 2nd-half, Shatabhisha, P.Bhadrapada, U.Bhadrapada, Revati} — ~5 days every ~27 days.

| Weekday | Subtype | Severity | Classical warning |
|---|---|:-:|---|
| Sunday | Agni Panchaka | Low | Avoid fire-work (new flame, welding, fire rituals) |
| Monday | Raja Panchaka | Low | Avoid authority/legal matters |
| Tuesday | Mrityu Panchaka | **High** | Avoid risk exposure (surgery start, dangerous journey, quarrels) |
| Wednesday | (neutral — no subtype) | — | Displayed as "Panchaka active (neutral, no weekday subtype)" |
| Thursday | (neutral — no subtype) | — | Same as Wed |
| Friday | Chora Panchaka | Medium | Avoid valuables exposure (financial transactions, unlocked house) |
| Saturday | Roga Panchaka | Medium | Avoid health-risk activities (surgery, new treatment, long fasting) |

### 3.6 Masa convention primary for B2C 🔒 (Option A)

- **B2C auto-adapts by user region:**
  - South (Tamil, Telugu, Kannada, Malayalam) / Gujarat / Maharashtra → **Amanta** primary (new-moon to new-moon)
  - North (Hindi belt, Bihar, UP, MP, Rajasthan, Punjab, Nepal) → **Purnimanta** primary (full-moon to full-moon)
- Both computed always; B2C UI surfaces one.
- **Astrologer always sees both** side-by-side regardless of region.

### 3.7 Nakshatra count (27 vs 28) 🔒 (Option A, with Y exception for SBC)

- **27-count for everything nakshatra-based:** daily panchang, Moon's nakshatra, Vimshottari dasa, percentile tables (Varjyam/Amrit Kala), Panchaka, Ganda Moola, Ravi Yoga, natal chart, divisional charts.
- Abhijit **not** recognized as nakshatra.
- "Abhijit Muhurta" (~48-min window around solar noon) is still computed independently — it's time-based, not nakshatra-based.
- **Sub-flag exception (Option Y): Sarvatobhadra Chakra retains classical 28-nakshatra grid** — scoped exception in E7 PRD. Abhijit appears only in SBC by structural necessity.

### 3.8 Ghati definition 🔒 (Option C)

- **Classical contextual** — for both user types:
  - Day-ghati = `day_length / 30` for sunrise-anchored windows (muhurta/hora/Choghadiya/Rahu Kala/Varjyam clock-time)
  - Night-ghati = `night_length / 30` for night-windows
  - Nakshatra-ghati = `nakshatra_duration / 60` for percentile-in-nakshatra tables (Varjyam, Amrit Kala)
- **Astrologer-only diagnostic panel:** "ghati precision" showing nakshatra-duration variability for the current chart.

### 3.9 Ravi Yoga nakshatra-count positions 🔒 (Option B)

- **Muhurta Chintamani standard** (Moon in 4/6/9/10/13/20 from Sun-nakshatra) is default for both user types.
- **Astrologer variant toggle:** 7-position variant (adds 12) and inverse-direction variant.

### 3.10 Dwipushkar & Tripushkar activation 🔒 (Option A, post-research correction)

**Corrected canonical rule (pada-structure-based, no source-selector):**

```
Dwipushkar = tithi ∈ {2, 7, 12}
           ∧ vaara ∈ {Sunday, Tuesday, Saturday}
           ∧ nakshatra ∈ {Mrigashira, Chitra, Dhanishta}    ← Dvipada (2-footed)

Tripushkar = tithi ∈ {2, 7, 12}
           ∧ vaara ∈ {Sunday, Tuesday, Saturday}
           ∧ nakshatra ∈ {Krittika, Punarvasu, U.Phalguni,
                          Vishakha, U.Ashadha, P.Bhadrapada}  ← Tripada (3-footed)
```

- Disjoint sets by construction (pada-count structural rule).
- Same for both user types.
- Rule is arithmetic (pada counts), not convention-based — no classical source meaningfully disagrees.
- Kalaprakashika verification flagged as future-work if Malayalam user base scales.

### 3.11 Hora computation 🔒 (Option A)

- **Chaldean + variable-length** for both user types.
- Day-hora = `day_length / 12`, Night-hora = `night_length / 12`.
- **First hora of day = day-lord (vaara lord).** Sunday → Sun-hora first. Monday → Moon-hora first.
- Subsequent horas: Chaldean order Sa → Ju → Ma → Su → Ve → Me → Mo → Sa …
- 25th hora correctly rolls to next day's day-lord.

---

### 3.12 Festival calendar source + scope 🔒 (Option B)

- **Unified core + regional additive layers.**
- **Core (~40 all-India festivals):** Deepavali, Navarathri, Krishna Jayanthi, Rama Navami, Vinayaka Chathurthi, Shivarathri, Akshaya Thrithiyai, Guru Pournami, Raksha Bandhan, Vasantha Panchami, Dhana Thrayodasi, etc. Plus tithi-recurring: Ekadasi, Pradosham, Sankatahara Chathurthi, Pournami, Amavasai.
- **Regional additive layers** surface only for users in that region:
  - **Tamil:** Pongal (Makara Sankaranthi morning), Tamil Puthandu (Chithirai 1), Aadi Perukku, Karthigai Deepam
  - **Malayalam:** Vishu (Mesha Sankaranthi), Onam (Chingam Thiruvonam)
  - **Telugu/Kannada:** Ugadi (Chithirai Shukla Prathami)
  - **Punjabi:** Baisakhi (Mesha Sankaranthi)
  - **Bengali:** Poila Boishakh (solar Boishakh 1), Durga Puja
  - **Gujarati:** Bestu Varsh (Karthika Shukla 1), Labh Panchami
  - **Marathi:** Gudi Padwa (Chithirai Shukla 1)
- **B2C:** sees core + their region's additions (auto-detect by region).
- **Astrologer:** sees everything + region-toggle.
- **Tithi-to-festival mapping** (item 3.13 proposed earlier) subsumed under this — covered by core + regional additives above; no separate decision needed.
- Calendar uses Drik Siddhantha (locked 3.4), Masam auto-adapt (locked 3.6) already handles Amanta/Purnimanta name differences for same-day festivals.

---

## 5. Cross-cutting decisions not yet made (in review queue)

1. Ayanamsa final lock (research complete; see 1.2)
2. House system final lock + fix bug (research complete; see 1.3)
3. ~~Ashtottari eligibility predicate~~ — 🔒 locked (see 1.6)
4. ~~Shadbalam / Budhan benefic-malefic split~~ — 🔒 locked (see 1.7)
5. ~~Ashtakavargam SAV + BAV scope for end-user vs astrologer~~ — 🔒 locked (see 1.8)
5a. ~~Trikona Shodhanai variant~~ — 🔒 locked (see 1.8)
6. Language display policy (locked — see 1.5) — ✅ Tamil audit complete (see `TAMIL_NAMING_AUDIT.md`); ✅ 14 ambiguity flags locked (Option A, see 1.5)
7. Region-detection mechanism for auto-adapt (UX — Govind's call)
8. E18 Sudarshana Chakra PRD creation — action item (locked scope in 1.9)
9. **Parashari gap closure (Option A) — 13 new PRDs + 11 extensions** locked 2026-04-20. See `GAP_CLOSURE.md` for the full action plan. Summary:
   - **New PRDs:** E19 Shadbalam · E20 Bhava Bala · E21 Vimshopaka · E22 Avastha Suite · E23 Panchadha Maitri · E24 Janma-Tara 9-Cycle · E25 Ashtakoota Milan + Manglik · E26 Special Lagnas Suite · E27 Maraka-Badhaka · E28 Upaya Engine · E29 Thirumana Porutham · E1c Extended Dasa Pack · E6b Transit v2
   - **Extensions:** E2a (Kaksha promote) · E3 (generalized Argala) · E4a (Yoga Karaka table) · E4b (Kaal Sarpa 12 variants) · E5b (Maraka-Badhaka dep) · E6a (Vedha + Tara/Chandra Bala) · E7 (5 Sphutas) · E10 (Tajaka + Arudha Prasna modes) · E12 (workbench tabs for new engines) · E1b (deferral callout) · P4 (timing-quality yogas)
   - **Total scope:** 76 → 89 PRDs (+13). P2 phase grows 14 → ~25. Parashari-JH parity ~70% → ~98%.

---

## 6. Approved research outputs (for reference)

- **Ayanamsa** — 43 systems catalogued, 9-total recommended shortlist. Full findings in Task 1 (ayanamsa research agent).
- **House systems** — 20+ systems catalogued, Whole Sign + 6-system shortlist recommended. Full findings in Task 2 (house-system research agent).
- **Panchangam** — 80+ elements across 10 categories, B2C + astrologer splits proposed. Full findings in Task 3 (panchangam deep research).
- **Nakshatra-percentile variance** — MC/Narada/Kalaprakashika tables textually identical; only ~1-ghati boundary offset; Dur Muhurta is vaara-based not nakshatra-based. Amrit Kala placement varies by ~95 min across traditions. Full findings in Task 4.
- **Dwipushkar/Tripushkar verification** — caught critical error in original nakshatra sets; corrected to pada-structure-based canonical rule. Full findings in Task 5.

---

## 6.5 GAP_CLOSURE PRDs — Pass 1 Decisions (PRD files pending)

These decisions are captured for new GAP_CLOSURE PRDs before their PRD files are written. Engineering creates the PRD files applying these locks.

### E19 Shadbalam Engine — Pass 1 locked 2026-04-22

**Cross-cutting inheritance:** All DECISIONS.md + Shadbalam-related locks apply (1.1 Rahu/Ketu node, 1.2 Ayanamsa Lahiri, 1.5 Language display, 1.7 Shadbalam display format + Budhan dual-classification + Chandran classification + minimum thresholds per graha, 3.7 Natchathiram 27, 3.11 Hora Chaldean variable-length).

**E19-specific decisions:**

| Decision | Value | Source |
|---|---|---|
| Sthana Bala sub-components (Q1) | **5 classical BPHS Ch.27 canonical** — Uccha + Saptavargaja + Oja-Yugma + Kendra + Drekkana. Same for both user types. |
| Saptavargaja Bala varga set (Q2) | **BPHS Ch.27 canonical 7** — D1 Rashi + D2 Hora + D3 Drekkana + D7 Saptamsa + D9 Navamsa + D12 Dwadashamsa + D30 Trimsamsa. |
| Kala Bala sub-components (Q3) | **BPHS 9 canonical** — Nata-Unnata + Paksha + Tribhaga + Varsha + Masa + Dina + **Hora Bala** + Ayana + Yuddha. |
| Yuddha Bala winner rule (Q4) | **Declination-based (BPHS Ch.27 v.48-52 canonical)** — winner = graha with greater northern declination. |
| Chesta Bala variant (Q5) | **BPHS Ch.27 v.23-30 canonical** — standard 9-step formula. Synodic position for inner planets (Budhan, Sukkiran); retrograde + speed for outer planets (Sevvai, Guru, Sani); Sooriyan uses Ayana Bala; Chandran uses Paksha Bala. |
| Ishta-Kashta Phala formula (Q6) | **BPHS Ch.29 canonical** — `Ishta Phala = sqrt(Uccha Bala × Chesta Bala)` [0-60 range] + `Kashta Phala = 60 − Ishta Phala`. Astrologer-only data per DECISIONS 1.7. |
| Cross-source aggregation (Q7) | **BPHS canonical only, no variants** — matches E9 Q6 single-source pattern + JH + PL + Astrosage + Raman + K.N. Rao convergent practice. |

**Dependencies:**
- E19 depends on E23 Panchadha Maitri (Sthana Bala Saptavargaja requires composite friendship matrix)
- E4a yoga strength formula (Source D synthesis per E4a Q2) consumes E19 Shadbalam
- E20 Bhava Bala + E21 Vimshopaka Bala + E5b Ayurdaya all build on E19

**Engineering action items:**
- Create E19 PRD file under `docs/markdown/prd/P2/` applying above Pass 1 decisions
- Implement 6-component Shadbalam calculator per BPHS Ch.27-29
- Golden chart fixtures: 10 BPHS/Raman-published Shadbala tables cross-verified at ±0 exact rupa match

### E23 Panchadha Maitri — Pass 1 locked 2026-04-22

**Cross-cutting inheritance:** All DECISIONS.md locks apply (1.1, 1.2, 1.5, 3.7).

**E23-specific decisions:**

| Decision | Value | Source |
|---|---|---|
| Natural friendship table source (Q1) | **BPHS Ch.3 v.47-62 canonical** — 7×7 matrix. Same for both user types. |
| Composite 5-fold categorization (Q2) | **BPHS Ch.3 canonical 5-fold** — Adhimitra / Mitra / Sama / Shatru / Adhishatru. Computed by combining natural + temporal friendship per BPHS Ch.3 v.63-65. |
| Rahu/Ketu friendship treatment (Q3) | **BPHS literal default** (Variant A — no natural friendships for Rahu/Ketu, Tatkalika-only) + astrologer-profile toggle: (B) Uttarakalamrita (Sani-like Rahu, Sevvai-like Ketu) OR (C) Sanjay Rath nodal-lord-inheritance. Parallels E4a Q5 4-option node treatment. |
| Cross-source aggregation (Q4) | **BPHS canonical only, no additional variants** (Q3 Rahu/Ketu toggle stands alone). Matches E19 Q7 single-source pattern + JH + PL + Astrosage. |

**Dependencies:**
- E19 Shadbalam Sthana Bala Saptavargaja consumes E23 Panchadha Maitri matrix
- E4a yoga predicates using "planet in friend-sign" / "planet in enemy-sign" consume E23
- E20/E21/E22/E27 downstream strength engines use E23

**Engineering action items:**
- Create E23 PRD file under `docs/markdown/prd/P2/` applying above Pass 1 decisions
- Implement 3-layer friendship computation (Naisargika table + Tatkalika position-based + Panchadha composite)
- Astrologer profile toggle for Rahu/Ketu treatment (3 options: A/B/C)
- Golden test fixtures: 5 sample charts with hand-verified Panchadha matrices

### E20 Bhava Bala Engine — Pass 1 locked 2026-04-22

**Cross-cutting inheritance:** All DECISIONS.md + E19 Shadbalam + E23 Panchadha Maitri + E4a Drishti locks apply.

**E20-specific decisions:**

| Decision | Value | Source |
|---|---|---|
| Bhava Bala components (Q1) | **BPHS Ch.31 canonical 4 components** — Bhavadhipathi + Dig + Drishti + Karaka. Same for both user types. |
| Bhava chart source (Q2) | **Bhava Chalit/Sripati** — all Bhava Bala computations use Sripati midpoints. Matches post-11th c Parashari consensus + JH + PL + Astrosage. |
| Bhava Karaka table (Q3) | **BPHS Ch.12 canonical** — 1st=Sooriyan · 2nd=Guru · 3rd=Sevvai · 4th=Chandran+Sukkiran · 5th=Guru · 6th=Sevvai+Sani · 7th=Sukkiran · 8th=Sani · 9th=Guru · 10th=Sooriyan+Budhan+Guru+Sani · 11th=Guru · 12th=Sani. |
| Cross-source aggregation (Q4) | **BPHS canonical only, no variants** — matches E19 Q7 single-source pattern. |

**Dependencies:**
- E20 depends on E19 (Shadbalam for Bhavadhipathi + Karaka components)
- E20 uses E4a Q5 Drishti (Bhava Drishti Bala — V2 graded + Rahu/Ketu default 7th only)
- Downstream: feeds dasa phalita interpretation, chart-strength narratives

**Engineering action items:**
- Create E20 PRD file under `docs/markdown/prd/P2/` applying above Pass 1 decisions
- 4-component Bhava Bala calculator per BPHS Ch.31 using Sripati bhava midpoints
- 10-chart golden fixture set with hand-verified 12-bhava strength totals

### E21 Vimshopaka Bala — Pass 1 locked 2026-04-22

**Cross-cutting inheritance:** All DECISIONS.md + E19 Shadbalam + E23 Panchadha Maitri (dignity source) locks apply.

**E21-specific decisions:**

| Decision | Value | Source |
|---|---|---|
| Primary Vimshopaka scheme (Q1) | **Dasa-Vargi (10-varga) default + astrologer-profile toggle to Sapta-Vargi (7) or Shodasa-Vargi (16).** B2C sees Dasa-Vargi. Matches JH + Raman + K.N. Rao + Narasimha Rao standard. |
| Weight values per varga (Q2) | **BPHS Ch.7 canonical weights for all 3 schemes.** Sapta-Vargi: D1=5, D2=2, D3=3, D7=2.5, D9=4.5, D12=2, D30=1. Dasa-Vargi: D1=3, D2=1.5, D3=1.5, D7=1.5, D9=3, D10=1.5, D12=1.5, D16=1.5, D30=1.5, D60=3. Shodasa-Vargi per BPHS. |
| Dignity-fraction formula (Q3) | **BPHS Ch.7 canonical 9 dignity levels.** Exaltation 1.0 / Mooltrikona 0.75 / Own sign 0.75 / Great Friend 0.5 / Friend 0.375 / Neutral 0.25 / Enemy 0.125 / Great Enemy 0.0625 / Debilitation 0.0. |
| Cross-source aggregation (Q4) | **BPHS canonical only, no variants** — matches E19/E20 single-source pattern. |

**Dependencies:**
- E21 depends on E23 Panchadha Maitri (dignity evaluation)
- E21 depends on existing divisional chart engines (D1-D60)
- E21 can run standalone from E19 (doesn't require Shadbalam)

**Engineering action items:**
- Create E21 PRD file under `docs/markdown/prd/P2/` applying above Pass 1 decisions
- Dasa-Vargi default Vimshopaka calculator + Sapta/Shodasa toggles
- 10-chart golden fixture cross-verified against Raman Dasa-Vargi published tables

### E22 Avastha Suite — Pass 1 locked 2026-04-22

**Cross-cutting inheritance:** All DECISIONS.md + E23 Panchadha Maitri locks apply.

**E22-specific decisions:**

| Decision | Value | Source |
|---|---|---|
| Scheme inclusion scope (Q1) | **All 5 schemes shipped** — Baladi 5-fold + Jagrat-Swapna-Sushupti 3-fold + 9-fold (Deepta/Swastha/Mudita/Shanta/Dinam/Duhkhita/Khala/Kopam/Sobhita) + Lajjitadi 6-fold (Lajjita/Garvita/Kshudhita/Trishita/Muditha/Kshobhita) + Arohana-Avarohana. Matches JH + GAP_CLOSURE scope. Same for both user types. |
| Baladi gender assignments (Q2) | **BPHS Ch.45 fixed** — Sooriyan/Sevvai/Guru/Budhan male order; Chandran/Sukkiran/Sani female order. Fixed regardless of sign placement. |
| 9-fold composite formula (Q3) | **BPHS Ch.46 v.15-25 canonical.** |
| Lajjitadi configurations (Q4) | **BPHS Ch.46 v.30-40 canonical** 6-fold. |
| Cross-source aggregation (Q5) | **BPHS canonical only, no variants** — matches E19/E20/E21 single-source pattern. |

**Dependencies:**
- E22 depends on E23 Panchadha Maitri (dignity for 9-fold + Lajjitadi composite)
- E22 output feeds dasa phalita interpretation, strength narratives

**Engineering action items:**
- Create E22 PRD file under `docs/markdown/prd/P2/` applying above Pass 1 decisions
- 5 avastha calculators (Baladi/3-fold/9-fold/Lajjitadi/Arohana)
- Multi-avastha state vector output per graha

### E27 Maraka-Badhaka Engine — Pass 1 locked 2026-04-22

**Cross-cutting inheritance:** All DECISIONS.md + E19 Shadbalam + E5b Ayus locks apply.

**E27-specific decisions:**

| Decision | Value | Source |
|---|---|---|
| Maraka identification (Q1) | **Strict 2nd + 7th BPHS Ch.44 canonical.** Primary Marakas = 2nd + 7th house lords. Secondary = planets in 2nd/7th + planets conjunct 2nd/7th lords. Same for both user types. |
| Badhaka house rule (Q2) | **BPHS Ch.44 canonical triad.** Movable Lagna → 11th Badhaka; Fixed Lagna → 9th Badhaka; Dual Lagna → 7th Badhaka. |
| Badhaka lord activation criteria (Q3) | **Classical strict (BPHS Ch.44 v.20-25) + Shadbalam-strength weighting** (hybrid). Self-placement / dusthana / malefic affliction / dasha-period triggers + Shadbalam modulates severity. |
| E5b Ayus integration (Q4) | **E27 feeds E5b dasha-window prediction.** Flags "critical Maraka dasha periods" within E5b Ayus window. Astrologer workbench integrated view. Ethical gating inherited from E5b Q5 (B2C hard refusal for direct longevity-timing queries). |
| Cross-source aggregation (Q5) | **BPHS canonical only, no variants.** |
| KP Maraka scope (Q6, locked 2026-04-23) | **Out of scope for E27 v1 — deferred to P3 or later.** E27 ships Parashari-only (BPHS Ch.44 canonical). KP Maraka analysis (sub-lord of 2/7/12 cusps + contrary-significator rejection per KPR Vol.4 Ch.18–22) is a specialized application of E9 primitives (5-level significators + cuspal sub-lords + RP matching); when added, will compose on top of E9 rather than extending E27. No engineering work in P2. |

**Dependencies:**
- E27 depends on E5b Ayus (feeds critical-period prediction)
- E27 uses E19 Shadbalam (lord-strength weighting)
- E27 inherits E5b ethical gating (hard refusal B2C)
- **KP Maraka analysis — NOT a dependency for v1.** Future P3 work will build on E9 (not E27).

**Engineering action items:**
- Create E27 PRD file under `docs/markdown/prd/P2/` applying above Pass 1 decisions
- Maraka identification engine (2nd+7th houses + lords + conjuncts)
- Badhaka identification per Lagna type triad
- Shadbalam-weighted activation logic
- E5b integration API for dasha-window critical-period flagging

### E24 Janma-Tara 9-Cycle — Pass 1 locked 2026-04-22

**Cross-cutting inheritance:** All DECISIONS.md locks apply.

**E24-specific decisions:**

| Decision | Value | Source |
|---|---|---|
| Classical source (Q1) | **Muhurta Chintamani Ch.3 canonical** 9-Tara order (Janma/Sampat/Vipat/Kshema/Pratyari/Sadhaka/Vadha/Mitra/Ati-Mitra). Matches JH + PL + Drik + Tamil Vakya + DECISIONS 3.2 convention. |
| Cross-cycle severity (Q2) | **All 3 cycles equal severity.** 1st/2nd/3rd cycle Taras treated equally in severity. Matches Tamil Vakya daily practice + JH + Drik + Astrosage. |
| Interpretation strings per Tara (Q3) | **Canonical meaning + activity-suitability strings with Muhurta Chintamani citation.** Per Tara: classical meaning (e.g., "Vipat Tara: Obstacles, danger-prone") + activity-suitability (e.g., "Avoid travel, surgery, risky ventures"). Same for both user types. |
| Cross-source aggregation (Q4) | **Muhurta Chintamani canonical only, no variants.** Matches single-source strength-engine chain pattern. |

**Dependencies:**
- E24 uses existing natal chart + Chandran natchathiram (no new ephemeris)
- E24 used by AI chat daily-practice queries ("is today good for X?")

**Engineering action items:**
- Create E24 PRD file under `docs/markdown/prd/P2/` applying above Pass 1 decisions
- Tara calculator: natchathiram count from natal position 1-27 → 9-category mod logic
- Interpretation strings bundle (9 Taras × meaning + activity-suitability)
- Daily Tara calendar API for astrologer workbench date-range query

### E25 Ashtakoota Milan + Manglik — Pass 1 locked 2026-04-22

**Cross-cutting inheritance:** All DECISIONS.md + E23 Panchadha Maitri + E24 Janma-Tara locks apply.

**E25-specific decisions:**

| Decision | Value | Source |
|---|---|---|
| 8-Koota classical source + points (Q1) | **Muhurta Chintamani Ch.5 + BPHS canonical 36-point** — Varna 1, Vashya 2, Tara 3, Yoni 4, Graha Maitri 5, Gana 6, Bhakoot 7, Nadi 8. Matches all matrimony tools. |
| Manglik placement rules (Q2) | **Single-reference (Lagna only), 5 houses (2/4/7/8/12).** Revised 2026-04-22. Sevvai in houses 2, 4, 7, 8, or 12 from Lagna triggers Manglik. 1st house dropped (user: not in current Tamil Parashari practice). Chandran-reference and Sukran-reference counting dropped (user: not in current use). Astrologer toggle exposes Chandran-reference + 1st-house-inclusion for lineages that require them; B2C sees Lagna-only 5-house result. |
| Manglik cancellations (Q3) | **Core 5 classical cancellations** — (1) mutual Manglik, (2) Sevvai in own sign, (3) Sevvai in exaltation, (4) benefic aspect on Sevvai, (5) Sevvai conjunct benefic. |
| Dashakoota extension scope (Q4) | **Ashtakoota 36 + Rajju Dosha + Vedha Dosha + Papasamya** checks. Middle ground; matches JH + PL + Astrosage + matrimony tools. |
| Cross-source aggregation (Q5) | **Muhurta Chintamani + BPHS canonical only, no variants.** |

**Dependencies:**
- E25 uses E23 Panchadha Maitri (Graha Maitri koota)
- E25 uses E24 Janma-Tara (Tara koota)
- Dual-chart input (user + partner)

**Engineering action items:**
- Create E25 PRD file under `docs/markdown/prd/P2/` applying above Pass 1 decisions
- 8-Koota scorer per MC+BPHS
- Manglik single-reference checker (Lagna-only, 5 houses: 2/4/7/8/12). Astrologer toggle to add Chandran-reference + 1st-house-inclusion.
- Core 5 cancellation rule engine
- Rajju/Vedha/Papasamya dosha checks
- Dual-chart API (user + partner) for compatibility query

### E26 Special Lagnas Suite — Pass 1 locked 2026-04-22

**Cross-cutting inheritance:** All DECISIONS.md + E7 Sphuta (Pranapada) + E3 Arudha Lagna inheritance.

**E26-specific decisions:**

| Decision | Value | Source |
|---|---|---|
| Lagnas-to-ship scope (Q1) | **All 10 Special Lagnas** — Bhava, **Hora Lagna**, Ghati, Vighati, Sri, Indu, Pranapada (from E7), Varnada, Nisheka, Vakra-Shoola. AL referenced from E3. Same for both user types. |
| Classical formulas source (Q2) | **BPHS + JUS + UK per canonical primary source per Lagna.** Bhava/Hora Lagna/Ghati/Vighati from BPHS Ch.4; Sri/Indu from BPHS Ch.85; Pranapada from BPHS Ch.79-80 (E7 inheritance); Varnada from JUS + BPHS; Nisheka from BPHS Ch.4 + Phaladeepika; Vakra-Shoola from UK. |
| Display tiering (Q3) | **Tiered:** Primary (Bhava, Hora Lagna, Ghati, Sri) always visible. Secondary (Vighati, Indu, Pranapada, Varnada) expandable panel. Research (Nisheka, Vakra-Shoola) opt-in flag. Matches JH + PL + SJVC + uniform tiered convention. |
| Cross-source aggregation (Q4) | **BPHS + JUS + UK canonical only, no variants.** |

**Dependencies:**
- E26 Pranapada reuses E7 Sphutas computation
- E26 AL referenced from E3 (already locked)

**Engineering action items:**
- Create E26 PRD file under `docs/markdown/prd/P2/` applying above Pass 1 decisions
- 10-Lagna computation engine per Q2 sources
- Tiered UI rendering (primary/secondary/research)

### E28 Upaya / Remedies Engine — Pass 1 locked 2026-04-22

**Cross-cutting inheritance:** All DECISIONS.md + E4a/E4b dosha detection + E19/E20 strength detection + E5b ethical gating patterns apply.

**E28-specific decisions:**

| Decision | Value | Source |
|---|---|---|
| Remedy categories scope (Q1) | **All 9 classical Upaya categories** — Mantra, Yantra, Tantra, Daan, Vrata, Rudraksha, Gemstone, Temple deity, Yagna. Same for both user types. |
| Remedy mapping source (Q2) | **Purana + Mantra Shastra + Graha Shanti classical synthesis.** Classical depth; matches JH. |
| Ethical framing (Q3) | **Classical "traditional practice" framing + universal disclaimer.** Remedies as classical tradition, not outcome-guaranteed advice. |
| Regional variants (Q4) | **Region auto-adapt per DECISIONS 2.1 pattern.** Tamil → Tamil temples (Murugan, Navagraha Vaitheeswaran). Hindi → North Indian (Hanuman, Mangal Nath). Malayalam → Kerala. Telugu → Tirumala. Bengali → Tarapith. Astrologer override per chart. |
| Cross-source aggregation (Q5) | **Classical synthesis + regional auto-adapt.** Single-source canonical with regional variance. |

**Dependencies:**
- E28 consumes E4a/E4b dosha detection
- E28 consumes E19 Shadbalam weakness detection
- E28 consumes E20 Bhava Bala weakness detection
- E28 inherits E5b-style ethical disclaimer framing

**Engineering action items:**
- Create E28 PRD file under `docs/markdown/prd/P2/` applying above Pass 1 decisions
- 9-category Upaya catalog database
- Dosha/weakness-to-remedy mapping table
- Regional auto-adapt temple-correlation engine
- Universal disclaimer framing across all remedy outputs

### E29 Thirumana Porutham — Pass 1 locked 2026-04-22

**Cross-cutting inheritance:** All DECISIONS.md + E23 Panchadha Maitri (Rasyathipathi) + E24 Janma-Tara (Dina) + E25 Ashtakoota (parallel system) locks apply.

**E29-specific decisions:**

| Decision | Value | Source |
|---|---|---|
| Classical source (Q1) | **Tamil Vakya Panchangam canonical.** Universal Tamil tradition; matches Tamil Nadu Rashtriya Panchang + all Tamil matchmaking software. Same for both user types. |
| Scoring system (Q2) | **Binary pass/fail per porutham + critical-flag for Rajju and Vedha** (deal-breakers if failed). Strict Tamil tradition. Matches Bharat Matrimony Tamil + Tamil Vakya printed editions. |
| Integration with E25 Ashtakoota (Q3) | **Both for astrologer; region-adapt for B2C.** Astrologer workbench always shows both side-by-side. B2C: Tamil users see Thirumana primary; other regions see Ashtakoota primary. Matches DECISIONS 2.1 pattern. |
| Cross-source aggregation (Q4) | **Tamil Vakya canonical only, no variants.** |

**Dependencies:**
- E29 uses E23 Panchadha Maitri (Rasyathipathi Porutham)
- E29 uses E24 Janma-Tara (Dina Porutham)
- E29 parallels E25 Ashtakoota (both surface together for astrologer; region-adapt for B2C)

**Engineering action items:**
- Create E29 PRD file under `docs/markdown/prd/P2/` applying above Pass 1 decisions
- 10-Porutham binary scorer + critical-flag logic (Rajju/Vedha)
- E25/E29 integration view (parallel for astrologer; region-adapt for B2C)
- Tamil naming + classical citation per porutham

### E18 Sudarshana Chakra — Pass 1 locked 2026-04-22

**Cross-cutting inheritance:** All DECISIONS.md + DECISIONS 1.9 (Sudarshana Chakra technique scope locked previously) + E4a/E4b yoga detection + E19 Shadbalam.

**E18-specific decisions:**

| Decision | Value | Source |
|---|---|---|
| Classical source primary (Q1) | **Jataka Parijata Ch.11 canonical primary** — most-detailed source. Matches all modern software + Raman + Rao + Rath. Same for both user types. |
| Triple-agreement evaluation method (Q2) | **Combined synthesis (Variant A bhava lord strength + Variant B per-chakra yoga detection + Variant C aspect favorability)** for triple-agreement evaluation per bhava. Most nuanced; matches JH + Sanjay Rath. |
| AI tool-use scope (Q3) | **All API patterns supported** — single bhava, all-12-summary, batched multi-bhava, matter-specific. Comprehensive AI tool-use richness. |

**Inherited from DECISIONS 1.9:**
- Triple-chakra composite (Lagna + Sooriyan + Chandran anchors)
- Zero new ephemeris (pure view/analysis layer)
- Region auto-adapt rendering style (Tamil/Malayalam/Telugu/Kannada → South · Hindi/Gujarati/Marathi/Punjabi → North · Bengali/Oriya → East)
- Astrologer toggle for all 3 styles

**Dependencies:**
- E18 uses E4a/E4b yoga detection (per-chakra yoga signals)
- E18 uses E19 Shadbalam (lord strength per chakra)
- E18 uses E20 Bhava Bala (aspect favorability per chakra)
- E11a AI chat consumes Sudarshana via 4-pattern API

**Engineering action items:**
- Create E18 PRD file under `docs/markdown/prd/P2/` applying above Pass 1 decisions
- Triple-chakra rendering engine (3 styles: South/North/East auto-adapt)
- Combined-synthesis triple-agreement evaluator
- 4-pattern AI tool-use API surface

### E1c Extended Dasa Pack — Pass 1 locked 2026-04-22

**Cross-cutting inheritance:** All DECISIONS.md + E1a/E1b dasa locks apply.

**E1c-specific decisions:**

| Decision | Value | Source |
|---|---|---|
| Dasa-pack scope (Q1) | **Tiered feature flags.** T1 always-on (Tara + Shoola Dasa). T2 default-on (Sthira + Drig Dasa). T3 astrologer-toggle (Kendra/Trikona/Brahma/Niryana Shoola). T4 research-flag (5 minor kalpas: Dwadashottari/Panchottari/Shataabdika/Chathurseethi-sama/Dwisaptati-sama). |
| Tara Dasa Tamil source (Q2) | **Tamil Vakya Panchangam canonical.** Universal Tamil tradition. |
| Sthira/Shoola/Drig source (Q3) | **JUS canonical default + Rangacharya commentary variant astrologer-profile toggle.** More accurate for Jaimini dasa lineage; consistent with E1b Q7. |
| Display tiering / primary dasa (Q4) | **Vimshottari always primary for B2C.** Universal Parashari standard. Tara visible in T1 panel but not primary. Astrologer sees all enabled per profile. |
| Cross-source aggregation (Q5) | **Per-dasa canonical** — Tamil Vakya for Tara; JUS canonical (+ Rangacharya toggle) for Sthira/Shoola/Drig + Jaimini variants. |

**Dependencies:**
- E1c uses E1a (Vimshottari) + E24 (9-Tara cycle for Tara Dasa)
- E1c follows E1a/E1b ClassicalEngine Protocol pattern

**Engineering action items:**
- Create E1c PRD file under `docs/markdown/prd/P2/P3/` applying above Pass 1 decisions
- Tara Dasa engine using E24 9-Tara cycle + Tamil Vakya allocations
- Sthira/Shoola/Drig Jaimini dasa engines per JUS
- Tier-based dasa visibility (T1-T4 feature flags)
- Astrologer-profile JUS-vs-Rangacharya toggle for Jaimini dasas

### E17 Chart Rectification — Pass 1 locked 2026-04-22 🔒

| Decision | Lock |
|---|---|
| 4-method scoring weights (Q1) | **Option B — Parashari-weighted**: Vimshottari 35% + Transit 30% + Varga 25% + Progressions 10%. Matches Parashari classical emphasis; Josi is Parashari-primary. Astrologer can tune weights; B2C locked to default. |
| Search window default (Q2) | **Option B — ±4 hours**. Matches traditional Tamil astrologer practice for family-recollected ("pulgalkaalam"/"maalai") birth times; covers ~80% of Indian diaspora cases. Astrologer override up to ±12h. |
| Operating modes scope (Q3) | **Option B — Modes 1+2 for B2C; all 3 for astrologers**. Event-based (Mode 1) + Personality-based (Mode 2) exposed to B2C. Prashna-assisted (Mode 3) gated to `astrologer_role_verified == True`. |
| Confidence threshold (Q4) | **Option B — absolute ≥70% match score**. Below threshold → "insufficient data, add more events" for B2C. Astrologer UI shows top 3 candidates with scores (Option D variant). |
| Cross-source aggregation (Q5) | **Option B — BPHS canonical default + Jaimini/KP as astrologer toggles**. B2C: pure Parashari (Vimshottari + Varga + transits). Astrologer toggle: `bphs_only` (default) \| `bphs_plus_jaimini` \| `bphs_plus_kp` \| `bphs_plus_both`. Matches cross-cutting Pattern 1.x. |

**Engineering action items:**
- Implement weighted scoring pipeline; expose weights as astrologer-tunable (B2C locked).
- Default `search_window_hours = 4`; astrologer override up to ±12h.
- Gate Mode 3 (Prashna) behind `astrologer_role_verified` feature flag.
- Surface `score < 0.70` as inconclusive response with CTA; astrologer UI shows top 3.
- Add `tradition_toggle` astrologer option.

### E6b Transit Intelligence v2 — Pass 1 locked 2026-04-22

**Cross-cutting inheritance:** All DECISIONS.md + E6a v1 + E2a Ashtakavargam + E24 9-Tara + E4a/E4b yoga locks apply.

**E6b-specific decisions:**

| Decision | Value | Source |
|---|---|---|
| E6b scope (Q1) | **All 7 features ship MVP** — Transit Ashtakavargam + Vedha + Tara Bala + Chandra Bala + Lattha + Graha-Karaka transit + Kal Sarpa transit activations. Same for both user types. |
| Vedha source (Q2) | **BPHS Ch.40 canonical.** |
| Lattha source (Q3) | **BPHS Ch.40 canonical.** |
| Tara/Chandra Bala formulas (Q4) | **Muhurta Chintamani Ch.3 canonical** (paired with E24 + DECISIONS 3.2/3.11). |
| Cross-source aggregation (Q5) | **Per-feature canonical sources, no variants.** BPHS for Vedha/Lattha/Graha-Karaka/Kal-Sarpa; Muhurta Chintamani for Tara/Chandra Bala; E2a inheritance for Transit Ashtakavargam. |

**Dependencies:**
- E6b extends E6a v1
- E6b uses E2a Transit Ashtakavargam infrastructure
- E6b uses E24 9-Tara cycle for Tara Bala
- E6b feeds AI chat synthesis ("what's blocking your career right now")

**Engineering action items:**
- Create E6b PRD file under `docs/markdown/prd/P3/` applying above Pass 1 decisions
- Transit Ashtakavargam engine (extends E2a to transit moments)
- Vedha + Lattha rule engines per BPHS Ch.40
- Tara Bala + Chandra Bala calculators per Muhurta Chintamani Ch.3
- Graha-Karaka transit + Kal Sarpa transit detectors

---

## 7. Change log

| Date | Change | Who |
|---|---|---|
| 2026-04-19 | Initial decision log created after Panchangam review session | cpselvam |
| 2026-04-22 | E17 Chart Rectification Pass 1 locked (Q1–Q5 all Option B). Pass 1 complete across all astrology-heavy PRDs. | cpselvam |
| 2026-04-22 | §1.1 B2C node default revised True Node → Mean Node after classical-soundness quality pass flagged mismatch with Parashari Tamil lineage + Indian panchang ecosystem norm. | cpselvam |
| 2026-04-22 | §1.8 Trikona Shodhanai revised simple-subtract → Phaladeepika 3-case rule (zero-if-min-is-zero, zero-if-tie-at-min, else subtract). Prior rule would over-report Shodhit SAV for common trine patterns. | cpselvam |
| 2026-04-22 | §1.5 Hora exception added: "Horai" → "Hora" with qualifiers (Hora Bala / Hora Lagna / Hora standalone). Other Tamil-phonetic terms unchanged. Disambiguates 3 collided Kala-Bala/Special-Lagna/Chaldean-clock senses. | cpselvam |
| 2026-04-22 | §1.7 Sukkiran Kala Bala threshold 5.5 rupas ratified (BPHS Ch.27 canonical); Raman's 5.25 variant not adopted. | cpselvam |
| 2026-04-22 | §6.5 E25 Q2 Manglik revised — dual-reference (Lagna+Chandran, 6 houses 1/2/4/7/8/12) → single-reference (Lagna only, 5 houses 2/4/7/8/12). 1st house dropped; Chandran + Sukran counting dropped. Matches current Tamil Parashari practice. Astrologer toggle retains Chandran-reference + 1st-house-inclusion for lineages that require them. | cpselvam |
| 2026-04-22 | §6.5 E27 Q3 Badhaka "Classical strict + Shadbalam-weighted activation" — ratified as-is. Reviewer comfortable with hybrid BPHS triggers + severity modulation by Shadbalam total. Attribution note: Shadbalam weighting is Rath-school modern commentary, not BPHS literal; labeled "Classical strict" per reviewer preference. | cpselvam |
| 2026-04-23 | §6.5 E27 Q6 KP Maraka scope locked — **out of scope for v1**, deferred to P3+. E27 ships Parashari-only. When added, KP Maraka will build on E9 primitives (significators + cuspal sub-lords + RPs) per KPR Vol.4 Ch.18–22, not extend E27. | cpselvam |
| 2026-04-23 | §1.5 Foreign-language support locked as Option A (Indian-only continued) for P1/P2/P3. 8 Indian regional languages + Sanskrit-IAST remain sole supported display set. Foreign languages (Spanish/French/Chinese/etc.) deferred to P4+ with tradition-native rendering if demand materializes. | cpselvam |
| 2026-04-23 | Consistency audit fixes (per `CONSISTENCY_AUDIT.md`): (1) stale True Node B2C default cleaned from E1a/E2a/E4a/E6a inheritance tables → Mean; (2) `review.md` tracker updated: 13 GAP_CLOSURE PRDs added as 🚧 rows (12 to P2, 1 to P3), P2 header count 14→27, P3 header count 9→10, first-sentence count 76→89; (3) orphan `E2b` reference removed from E2a `enables` + E7 prose; (4) `P2-UI-*` placeholders resolved to E12 in E5/E5b/E7/E8/E8b/E9/E10; (5) E10 Prasna branches annotated with house-system/ayanamsa source per branch; (6) E4a Tamil yoga #57 + Kuja Dosha catalog entry aligned to revised §6.5 E25 Q2 5-house Lagna-only default. | cpselvam |

---

**Maintenance notes.**
- When a new decision is locked, add it under the relevant section with a 🔒 marker.
- When a decision is revised, update in place and add a row to section 7 (change log) with date + what changed.
- Never delete a decision — if superseded, mark old decision as **SUPERSEDED** and link to new.
- This file is the source-of-truth. When PRDs are updated to reflect these decisions, cite back to this file.
