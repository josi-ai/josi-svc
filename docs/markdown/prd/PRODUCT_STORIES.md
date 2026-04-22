# Josi Classical Techniques Expansion — Product Stories

**Purpose of this document.** The 76 PRDs under `docs/markdown/prd/` are technically dense — they describe classical formulas, rule schemas, data models, and citations. This document is the **product-story companion**: plain-English narratives that explain *what each astrology feature is*, *how an end-user will experience it*, *how a professional astrologer will use it*, and *what the system does behind the scenes* to make it work.

If you're reviewing the PRDs and can't picture how a human being would actually use the thing being specified, read the story here first, then go back to the PRD.

**Audience.** Product reviewers, new engineers joining the team, astrologers on our advisory panel, marketing, and anyone trying to answer the question "so what is this *for*?"

**Scope.** 15 astrology-heavy PRDs across P1 (MVP Engines) and P2 (Breadth & UIs). Engineering-focused PRDs (P0 foundation, P3/P4 scale, P5/P6 vision) are not narrated here — they don't produce user-visible features directly; they enable the ones below.

**How to read.** Each section follows the same shape: what the feature is → why it matters → regular-user flow → astrologer flow → what the system does in the background → a concrete worked example. Classical citations are minimal here; they live in the PRDs themselves.

---

## Background: Two user types

Before the feature stories make sense, know the two user types Josi serves:

- **Regular user (B2C).** A curious person on their phone. Not an astrologer. Wants an honest, accessible answer to questions like "what's my chart say about my career?" or "why does this year feel so hard?" Pays $5–$30/mo for a subscription tier. Never sees raw chart tables. Converses with AI chat in plain language. If a reading needs a human, gets routed to the marketplace of professional astrologers.
- **Professional astrologer (B2B / marketplace).** A practicing astrologer using Josi's **Astrologer Workbench** to produce readings for their own clients. Needs raw charts, every technique, side-by-side comparisons, citations. Makes money on Josi by taking consultation bookings from B2C users. Configures their "source preferences" — e.g., "for Ashtakavarga, I use BPHS shodhana; for sub-lord I use KP." Those preferences are saved to their profile and applied to every chart they work.

Many features have two UI surfaces: a **simplified end-user surface** (AI chat answers, visual summaries) and a **depth astrologer surface** (tables, toggles, alternate-tradition overlays). Every story below distinguishes the two.

---

## P1 — MVP Engines (the first 4 PRDs, shippable in Month 1–3)

### E1a — Multi-Dasa Engine v1 (Yogini + Ashtottari)

**What it is.** A **dasa** is a timing cycle in Vedic astrology — it divides a person's life into named periods ruled by planets, and each period colors what that stretch of life is "about." Josi currently computes only **Vimshottari Dasa** (the 120-year cycle almost every Indian astrologer uses). This PRD adds two more classical dasa systems so a reading can cross-reference multiple timing frames: **Yogini Dasa** (36 years, used for short-term transitional windows) and **Ashtottari Dasa** (108 years, used when specific classical conditions are met, like the Moon being in the dark half of the lunar month).

**Why it matters.** Classical astrologers rarely use Vimshottari alone — they cross-check at least two systems before calling a period "good" or "bad." A reading that names your current dasa as just Vimshottari is literally incomplete by the tradition's own rules.

**Regular-user flow.** User opens the app and asks the AI chat: *"What's happening in my life right now, astrologically?"* Before E1a, the AI answers using one dasa. After E1a, the AI says something like: *"You're in Venus Mahadasa / Jupiter Antardasa under Vimshottari — a ~2-year window emphasizing career partnerships and growth. But under Yogini dasa, you're in a shorter Rahu period lasting through June 2027, which classically indicates sudden shifts. The two signals together suggest: growth is real, but don't mistake turbulence for failure."* Two timing lenses, honest synthesis, surfaced conversationally.

**Astrologer flow.** Astrologer opens the Workbench and pulls up a client's chart. The dasa panel shows **three columns side by side** — Vimshottari, Yogini, Ashtottari — with the currently-active Mahadasa → Antardasa → Pratyantardasa highlighted in each. They can toggle which systems display, can jump the date slider to any past or future date to see what was/will-be-active, and when they write their reading, the three-system cross-confirmation appears as citations in the rendered document.

**Behind the scenes.** When a chart is created, the system takes the Moon's nakshatra position (one of 27 lunar mansions) and runs each dasa's starting-rule to produce a complete lifetime timeline. For Ashtottari specifically, it checks whether the Moon is in krishna paksha (the dark half of the lunar month) — if so, Ashtottari is applicable by the classical BPHS rule. The astrologer can override this to "always applicable" or "never" per their school's preference. Each system's timeline gets stored as a 3-level nested structure (Mahadasa → Antardasa → Pratyantardasa) so queries like "who is the active lord on 2028-06-15?" return in milliseconds.

**Worked example.** Shweta, born 14 March 1987, asks AI chat: *"Why does this year feel so scattered?"* AI pulls her current dasa state: Vimshottari = Saturn-Venus (steady, methodical), Yogini = just-entered Rahu (short-term, sudden-shift). AI replies: *"Your primary chapter is methodical — Saturn-Venus in Vimshottari. But a shorter Rahu window opened in December and runs through June 2027, which classically brings externally-triggered changes. The 'scattered' feeling tracks — it's the Rahu overlay on an otherwise steady period."*

---

### E2a — Ashtakavarga v2 (Trikona + Ekadhipatya Shodhana, Sodhya Pinda)

**What it is.** **Ashtakavarga** is a classical numerical-strength system — it scores each sign of the zodiac from each planet's perspective and produces a matrix of "points" (bindus) that tell you where a chart is strong and where it's weak. Josi currently computes only the *raw* Ashtakavarga (the surface-level matrix). Classical astrologers universally reject raw Ashtakavarga as incomplete — the tradition prescribes **two mandatory "purification" passes** (*shodhana*) before any interpretation: one that removes redundancies across trinal sign groups (*trikona shodhana*), and one that resolves duplication from planets owning two signs (*ekadhipatya shodhana*). Only the doubly-purified matrix should drive any prediction. This PRD adds both purification passes plus a deeper computation called **Sodhya Pinda** used for longevity and strength assessments.

**Why it matters.** B.V. Raman, the 20th-century Parashari authority, wrote: "never judge a house by raw bindu counts; always judge by shodhit values." A platform that displays raw bindus is misleading its users. This PRD fixes that.

**Regular-user flow.** Largely invisible — this is a correctness fix under the hood. The AI chat's strength assessments ("your 10th house is strong" → "your 10th house is strong after shodhana, meaning the strength survives classical scrutiny") become quietly more trustworthy. The end-user rarely sees "shodhit" terminology; they just get more-accurate readings.

**Astrologer flow.** In the Workbench, the Ashtakavarga view now shows **four matrices in tabs**: Raw BAV, Trikona-Shodhit, Ekadhipatya-Shodhit (doubly purified), and Sodhya Pinda. The astrologer can see the purification step-by-step — critical for teaching, for client explanations, and for sanity-checking that Josi matches their desktop software (Jagannatha Hora, Parashara's Light). When they reference bindu counts in their reading, the shodhit values flow into the document with the correct classical meaning.

**Behind the scenes.** The system takes the raw BAV (already computed) and applies two deterministic algorithms from BPHS Chapter 66. Each produces a new matrix. Then BPHS Chapter 67's Sodhya Pinda computation multiplies in two strength factors — a planet-factor (*graha pinda*) and a sign-factor (*rashi pinda*) — to produce a final strength number per planet. Golden test fixtures verify the output matches Jagannatha Hora 7.x exactly.

**Worked example.** An astrologer reviews Arjun's chart. Raw BAV shows the 10th house (career) has 31 bindus — looks strong. She clicks "Trikona-Shodhit" and the number drops to 19 — many of those bindus were redundant across the trinal houses. She clicks "Ekadhipatya-Shodhit" and it drops to 14 — still above threshold but meaningfully weaker than raw suggested. In her reading she writes: *"Career strength is present but not dominant (shodhit 14) — don't over-promise on this axis."*

---

### E4a — Classical Yoga Engine MVP (60 core yogas)

**What it is.** A **yoga** in Vedic astrology is a specific planetary configuration that produces a definite, named effect. "Gaja Kesari Yoga" (Jupiter in a cardinal position from the Moon) means intelligence and respect. "Neecha Bhanga Raja Yoga" (a debilitated planet whose debility gets cancelled) means rising from hardship to power. Classical texts catalogue thousands of these; the most-cited ~250 are what a working astrologer uses day-to-day; of those, ~60 are the ones you'd mention *first* in any reading. Today Josi has zero yoga detection — it only reports planet positions and aspects. This PRD adds an engine that detects **60 core yogas** automatically on every chart, with both a boolean ("is the yoga present?") and a strength score ("at what intensity?").

**Why it matters.** Ask any astrology user "what's special about my chart?" and the answer is named yogas. A platform that can't say "you have Raja Yoga at 0.82 strength" cannot answer the single most-asked question in astrology.

**Regular-user flow.** User asks AI chat: *"What's special about my chart?"* AI responds: *"You have four notable yogas active in your chart: **Gaja Kesari Yoga** (strength 0.91) — associated with intelligence, learning, and respect — that's the strongest. **Dhana Yoga** (0.67) for wealth potential through self-effort. **Chandra-Mangal Yoga** (0.54) for entrepreneurial drive. And a mild **Kemadruma Yoga** (0.32) — technically a difficult configuration, but at low strength it manifests as occasional emotional isolation rather than a core pattern."* The strength scores turn "you have X" into a nuanced, honest answer.

**Astrologer flow.** Workbench opens to a **Yogas panel** showing all 60 yogas evaluated, with filters: Active Only | By Category (Pancha Mahapurusha, Raja, Dhana, Chandra, Surya, Dushta) | By Strength. Each yoga row expands to show *which planets are participating, which rule activated it, and the citation* (e.g., "BPHS Ch.36 v.14–16"). If two classical sources disagree on a yoga's definition (BPHS says one thing, Saravali another), both rules show; the astrologer picks which to use in their reading via their source preferences.

**Behind the scenes.** Each of the 60 yogas lives as a **YAML rule file**, not as Python code. The rule file declares the activation predicate (e.g., "Jupiter in kendra from Moon"), the strength formula (e.g., "0.5 + 0.3 × planet_dignity + 0.2 × aspect_support"), and the classical citation. A generic engine loads all rules at startup and evaluates them against any chart. Adding yoga #61 is a pure-content change — author a YAML file, submit a PR, deploy. No engineer needed.

**Worked example.** Ravi's chart is loaded. Engine evaluates all 60 rules and finds 7 activations: Ruchaka (Mars in own sign in kendra, strength 0.88), Hamsa (Jupiter in exaltation in kendra, 0.82), Gaja Kesari (Moon-Jupiter kendra, 0.91), Dhana Yoga (2nd and 11th lords combined, 0.71), Vipareeta Raja Yoga (6th lord in 8th, 0.58), and two mild Dushta yogas. The reading opens with: *"Ravi's chart is dominated by strength configurations — two Pancha Mahapurusha yogas (Mars and Jupiter) plus Gaja Kesari — indicating a chart wired for visible achievement."*

---

### E6a — Transit Intelligence v1 (Sade Sati, Dhaiya, Major Transits, Eclipses)

**What it is.** *Transits* (*gochara*, "moving sky") are what planets are doing *right now* and how that interacts with where they were at your birth. Transits are what end-users actually ask about: *"When does my Sade Sati end?"*, *"Is this a good year for marriage?"*, *"What's happening with my Saturn?"* Josi today can report where planets are at any given date, but it doesn't recognize classical **transit patterns** — the named, interpretively-loaded configurations that astrologers actually talk about. This PRD adds four: **Sade Sati** (Saturn's 7.5-year passage through the three signs around your natal Moon — the single most-feared transit in Indian popular astrology), **Kantaka Shani & Ashtama Shani** (Saturn's 2.5-year passages through the 4th and 8th from Moon — "mini Sade-Satis"), **major outer-planet ingresses** (when Jupiter, Saturn, Rahu, or Ketu change signs — each a cultural event in Indian astrology, especially in Tamil tradition where *guru peyarchi* and *shani peyarchi* are widely discussed), and **eclipses** (conjunctions with natal points).

**Why it matters.** This PRD powers the #1 most-asked-about class of questions in consumer astrology. Without it, AI chat cannot credibly answer "what's coming up?"

**Regular-user flow.** User asks: *"When does my Sade Sati end?"* AI checks the user's natal Moon sign, looks up Saturn's current position, and replies: *"You're in the peak phase of Sade Sati, which started in January 2023 when Saturn entered Aquarius (your natal Moon sign). The peak phase ends March 2025, the setting phase runs through January 2028, and Sade Sati fully exits in January 2028. If you want, I can show you the timeline visually."* Or user asks: *"Is this a good year?"* AI pulls all active transit patterns — Sade Sati phase, Jupiter's current sign vs their chart, any eclipse conjunctions to their natal points — and synthesizes an honest take.

**Astrologer flow.** Workbench has a **Transit Timeline** view — a horizontal scrollable timeline showing Sade Sati phases as color bands, Jupiter/Saturn/Rahu/Ketu ingresses as vertical markers, eclipses as stars. Astrologer can scrub the date slider and see which patterns were active. They can click any event to see the exact date, duration, retrograde re-entries, and the classical citation. When writing a reading, they click "insert transit context" and the timeline becomes a rendered visual in the document.

**Behind the scenes.** The system uses Swiss Ephemeris to compute when each named transit pattern starts and ends over a 30-year window per chart (not a day-by-day scan — that would be too slow). For Sade Sati: find when Saturn enters the 12th from Moon (rising dhaiya begins), when Saturn enters the Moon's sign itself (peak begins), when Saturn enters the 2nd from Moon (setting dhaiya), when Saturn exits the 2nd (Sade Sati ends). Retrograde motion can cause Saturn to re-enter a sign; the system tracks all boundary crossings. Output is a stream of typed events the AI chat and UI both consume.

**Worked example.** Priya, natal Moon in Leo. Currently (April 2026), Saturn is in Pisces. Priya asks: *"What's my Saturn doing?"* AI checks: her Moon is in Leo; 4th from Leo is Scorpio; 8th from Leo is Pisces. Saturn is in the 8th — Ashtama Shani active. AI replies: *"You're not in Sade Sati (that ended in late 2022), but you are in Ashtama Shani — Saturn's 2.5-year passage through the 8th from your natal Moon. It started February 2025 and runs through September 2027. Classical interpretation: a period of inward restructuring, often around hidden fears, inheritance, or long-buried patterns. Not catastrophic — but a time for honest self-work rather than external expansion."*

---

## P2 — Breadth & UIs (the next 11 PRDs, shippable in Month 3–6)

### E1b — Multi-Dasa Engine v2 (Chara + Narayana + Kalachakra)

**What it is.** E1a gave us three Parashari dasa systems (Vimshottari + Yogini + Ashtottari). E1b adds three **structurally different** dasa systems: **Chara Dasha** and **Narayana Dasha** (both from the Jaimini tradition — they're *sign-based*, not *planet-based*, so instead of "Venus Mahadasa" you get "Libra Mahadasa"; the "lord" of the period is a zodiac sign, not a planet) and **Kalachakra Dasha** (the most computationally intricate classical dasa — its period lengths depend on which nakshatra-pada the Moon occupies; different padas produce completely different timelines).

**Why it matters.** Jaimini astrologers use Chara and Narayana as their *primary* timing tools, not as supplements. Kalachakra is famously cited in BPHS as "the most accurate dasa" by some traditions. A platform that claims "comprehensive dasa coverage" without these three isn't being honest.

**Regular-user flow.** Largely transparent unless the user's astrologer uses Jaimini. AI chat can now answer *"What do Jaimini-school astrologers say about my current period?"* with the Chara/Narayana context. For Tamil/Kerala diaspora users — where Jaimini practice is strong — this materially improves relevance.

**Astrologer flow.** Workbench dasa panel expands from 3 columns to up to 6 (any combination the astrologer enables in their preferences). A Jaimini-school astrologer configures their profile as "Chara + Narayana primary, Vimshottari for cross-check" — now every chart they open leads with Chara/Narayana. A Parashari astrologer leaves it as Vimshottari primary and only pulls Chara/Narayana if they want a specific second opinion.

**Behind the scenes.** Unlike nakshatra-lord dasas, these use sign-order sequences. Chara Dasha starts from the sign containing the *Atmakaraka* (the planet with the highest longitude-within-sign), direction-flips based on whether that sign is odd/even, and walks the zodiac. Narayana has different starting rules (based on 7th-from-Lagna or Karakamsa). Kalachakra uses *paryaya* (sequence) tables: given the Moon's nakshatra-pada, lookup the paryaya, then walk one of four rasi sequences with per-sign year allotments (Aries=7yr, Taurus=16yr, etc.). Each engine ships with 5+ golden-chart test fixtures cross-verified against Jagannatha Hora 7.x.

**Worked example.** Meenakshi's astrologer is trained in Irangati Rangacharya's Jaimini school. She opens Meenakshi's chart and sees Chara Dasha leading: *"Libra Mahadasa, Pisces Antardasa, active now until 2028."* She interprets: Libra = partnership axis, Pisces = spiritual/dissolutive overlay. Her reading for Meenakshi focuses on "a partnership transformation driven by a spiritual or artistic turning point." She cross-checks with Vimshottari (which shows Mercury-Saturn — a communication/structure period), confirming the partnership-restructuring theme.

---

### E3 — Jaimini System (Chara Karakas, Arudhas, Rashi Drishti, Jaimini Yogas)

**What it is.** Jaimini astrology is a **parallel classical system** to Parashari — attributed to the sage Jaimini (around 300 BCE), elaborated over millennia. It has its own aspects, its own significators, its own yogas. Four pillars: **Chara Karakas** (*movable* significators — instead of Parashari's fixed "Sun = father, Moon = mother," Jaimini ranks the 7 planets by their longitude-within-sign and assigns chart-specific roles: the planet with the highest longitude is the Atmakaraka "soul significator," second-highest is Amatyakaraka "career/counsel significator," and so on); **Arudha Padas** (*reflection points* — each house projects into another sign via a geometric formula; the Arudha Lagna is "your public image" vs. the Lagna which is "your actual self"); **Rashi Drishti** (*sign-to-sign aspects*, not planet-to-planet — a completely different geometry than Parashari aspects); and **Jaimini Yogas** (~25 yogas that combine the above three pillars).

**Why it matters.** Jaimini is not a minor variant — for many South Indian and Kerala astrologers, it is the *primary* system. Arudha Lagna in particular is increasingly popular in modern Western-influenced Vedic practice (Ernst Wilhelm, Pranav Sanjay Rath) as "the chart of how others see you."

**Regular-user flow.** User asks: *"How do people perceive me?"* AI pulls the Arudha Lagna's sign and its lord's placement: *"Your Arudha Lagna is in Cancer, and Cancer's lord (Moon) is in your 10th house. Publicly, you come across as emotionally steady and career-focused — more nurturing than your actual Ascendant (Aries) suggests."* This is a distinctly Jaimini answer — Parashari has no equivalent.

**Astrologer flow.** Workbench opens a **Jaimini panel** with four tabs: Chara Karakas (a ranked list showing each planet's role), Arudhas (a 12-position table showing each house's projected sign), Rashi Drishti (a sign-aspect matrix), Jaimini Yogas (15+ yogas with activation status). A Jaimini-practicing astrologer uses this panel as their *primary* chart view. A Parashari astrologer uses it for specific questions — e.g., marriage analysis via Upapada — while keeping the Parashari panels as primary.

**Behind the scenes.** Chara Karaka computation is just a sort — rank 7 planets by their longitude mod 30° (longitude-within-sign), then assign AK/AmK/BK/MK/PK/GK/DK. Arudha calculation per house H: count from H to its lord's sign, then count the same number forward from the lord's sign; the landed sign is the Arudha — with exception rules (if landed on H itself or on the 7th from H, project to the 10th from the lord instead) to prevent degenerate cases. Rashi Drishti is a fixed sign-aspect matrix (movable signs aspect fixed signs except adjacent; etc.) — load it once at startup. Jaimini yogas use the same rule-engine infrastructure as Parashari yogas (E4a) but with a Jaimini-specific predicate vocabulary.

**Worked example.** Karthik asks his Jaimini-school astrologer: *"Why does my career feel blocked?"* The astrologer checks the Amatyakaraka (career significator in Jaimini). In Karthik's chart, Sun has the second-highest longitude, making it his AmK. Sun is placed in the 12th house (loss, dissolution). The astrologer: *"Your career significator (Sun as AmK) is in the 12th — Jaimini reads this as career fulfillment requiring withdrawal, overseas work, or behind-the-scenes roles rather than public leadership. The block you feel is a mismatch between the public-leadership mold and what your chart actually wants."*

---

### E4b — Classical Yoga Engine Full (250 yogas)

**What it is.** E4a shipped 60 core yogas. E4b adds 190 more, bringing Josi's total to ~250 — matching the working catalogue of Jagannatha Hora or Maitreya9, the two reference implementations professional astrologers compare against. The 190 include **Nabhasa Yogas** (based on planetary count-patterns — e.g., "all 7 planets in 7 signs"), **Parivartana Yogas** (mutual-exchange between two house-lords — a powerful wealth/partnership signal), **Kaal-Sarp Yoga** variants (all planets between Rahu and Ketu — a widely-discussed affliction with many classical subtypes), and **Tajaka Yogas** (annual-chart yogas, 16 of them, gated by E5 Varshaphala).

**Why it matters.** 60 yogas is enough to be useful; 250 is enough to be *professionally complete*. An astrologer opening a Josi chart expects to see every yoga they'd see in JH. Anything less produces "why doesn't Josi catch this?" complaints.

**Regular-user flow.** AI chat becomes noticeably richer. Before E4b: "you have Raja Yoga and Dhana Yoga." After E4b: "you have Raja Yoga (0.82), Dhana Yoga (0.71), Saraswati Yoga (0.69, indicates intelligence and scholarship), Vasumati Yoga (0.55, wealth from inheritance/passive income), and Amala Yoga (0.43, clean reputation)." The end-user gets 3–5× more specific context about what makes their chart distinctive.

**Astrologer flow.** Workbench Yogas panel now shows all 250 with filters — by category, by strength threshold, by classical source (show only BPHS yogas, or only Saravali, or the cross-source union). Click any yoga for its YAML source, its activation predicate, its verse citation, and the participating planets.

**Behind the scenes.** The engine from E4a is **unchanged** — E4b is purely additive content. 190 new YAML rule files + about 10 new predicate definitions (for Nabhasa counts, Parivartana checks, Tajaka-specific applying/separating-aspect logic). Released in 4 waves of ~50 yogas each; each wave passes its golden-chart fixtures before promoting to production.

**Worked example.** Anjali's chart, previously showed 4 yogas under E4a, now shows 11 under E4b. Her astrologer notes a previously-hidden **Sunapha Yoga** (planets in the 2nd from Moon) and **Anapha Yoga** (planets in the 12th from Moon) — both benefic indicators. The fuller picture shifts the reading from "promising but average" to "distinctly supported for independent work."

---

### E5 — Varshaphala (Tajaka Annual Chart System)

**What it is.** **Varshaphala** (literally "fruits of the year") is the Vedic *annual* predictive system — you cast a new chart each year at the exact moment the Sun returns to its natal longitude (roughly your birthday), and you read that chart for the year ahead. The technique originated in the Persian/Arabic **Tajaka tradition** and was synthesized into Sanskrit classical literature by Neelakantha in the 16th century. Crucially, **Tajaka uses entirely different machinery** from the natal Parashari system: its own aspect scheme (sextile/square/trine/opposition with specific orb rules), its own 16 yogas (Ithasala, Isharaaph, Kamboola, etc.), its own year-lord selection algorithm (a 5-candidate strength contest called *Varsheswara*), its own "year point" (*Muntha*, which progresses 1 sign per year from the natal Lagna), its own Arabic-Parts system (*Sahams*, 50+ of them), and its own intra-year timing system (*Mudda Dasha*, a compressed-proportional Vimshottari running the full cycle in one year).

**Why it matters.** "What does this year hold?" is, in Indian popular practice, the most-asked astrology question at birthdays. Varshaphala is the classical answer. Without it, Josi can only offer transit-based "this year" answers, which are incomplete.

**Regular-user flow.** On or near the user's birthday, AI chat proactively offers: *"Your new year chart (Varshaphala) just started. Want a read?"* User accepts. AI synthesizes: *"Your Muntha moved into your 7th house this year — classically a partnership-heavy year. Your Varsheswara (year lord) is Jupiter, strong in your 10th — career expansion is the dominant theme. Notable activations: Vivaha Saham (marriage point) is active, and a Kamboola yoga (wealth transfer) is forming in your 2nd. Mudda Dasha: you're in Saturn-Jupiter for the next 3 months — reliable progress in professional matters."* A complete year-ahead reading.

**Astrologer flow.** Workbench has a **Varshaphala page** — the full annual chart rendered next to the natal chart, with Muntha position marked, Varsheswara highlighted, active Tajaka yogas listed, all 30 Sahams with their positions, and a Mudda Dasha timeline. Astrologer can change the "year" dropdown to see past years or preview upcoming ones. When writing an annual reading, they insert Varshaphala context as a dedicated section.

**Behind the scenes.** System computes the exact solar-return moment (Sun returning to natal longitude) to the second. Casts a full chart at that moment, default location = birthplace (astrologer can override to "current location" — a tradition-dependent choice). Muntha = count years elapsed, start from natal Lagna sign, move one sign per year. Varsheswara runs a 5-candidate strength contest per Tajaka Neelakanthi Chapter 2 with explicit tie-breaking. Mudda Dasha takes the standard 120-year Vimshottari proportions and compresses them into one solar year, starting from the lord determined by solar-return Moon's nakshatra modulo 9.

**Worked example.** Varun, birthday 12 April. On 12 April 2026 his new Varshaphala year starts. AI checks: Muntha = natal Lagna (Virgo) + 39 years = Sagittarius in his 4th house. Varsheswara = Mars (wins the 5-candidate contest). Mars is in the 10th of the annual chart. AI tells Varun: *"This year, your Muntha is in your 4th — home, foundations, emotional base. Year lord is Mars in the 10th — action-driven career energy. Pattern: this is a year to build a home-base while pushing career. Don't scatter focus. Mudda dasha: you start the year in Rahu-Mercury (14 days) — sharp communication, unexpected opportunities. Then Rahu-Ketu (19 days) — watch for sudden reversals."*

---

### E5b — Full Ayus (Longevity) Suite

**What it is.** *Ayus* (longevity) is one of the oldest and most elaborate subsystems in Parashari astrology — BPHS devotes three full chapters to it (72, 73, 74). It produces a **numerical estimate of the native's lifespan**. Four methods are classical: **Pindayu** (BPHS Ch.72, weighted by planet strength with multiple subtraction factors called *haranas*), **Amshayu** (Ch.73, based on Navamsa divisional positions), **Nisargayu** (Ch.74, based on fixed per-planet natural allotments with haranas), and **Jaimini Ayur-dasha** (from Jaimini Upadesha Sutras, categorizing into *Alpa* short / *Madhya* medium / *Deergha* long life-spans).

**Why it matters and why it's carefully handled.** Classical astrologers consider ayus foundational — they traditionally run it *first*, because every other prediction is mute beyond the ayus window. *But* the same tradition (Phaladeepika Ch.7 v.2) explicitly says: "do not state the year of death to the native." Modern astrology consensus agrees — this is ethically and legally fraught territory. This PRD implements ayus for **professional astrologer use** but **gates it from direct B2C chat**. End-users who ask "how long will I live?" get a polite deflection and a referral to the marketplace.

**Regular-user flow.** User asks AI chat: *"How long will I live?"* AI replies (scripted response, not computed): *"This is a question I'm not set up to answer directly — classical astrology has strong ethical traditions against stating specific lifespan to the native, and I follow that tradition. If longevity context is important for a life-planning decision you're facing, I can connect you with a professional astrologer from our network who handles these questions in context."* Behind the scenes, the ayus is computed but never surfaced.

**Astrologer flow.** In the Workbench (for verified professional astrologer accounts only), a **Longevity panel** appears. All four methods compute and display side by side — Pindayu: 68 years. Amshayu: 73 years. Nisargayu: 71 years. Jaimini: Madhya (medium). The astrologer sees the agreement pattern (classical practice: don't trust a single method; look at the ensemble — this is called *ayur-nirnaya*). Used in professional consultation for framing — never for prediction.

**Behind the scenes.** Pindayu: starts with each planet's base contribution (strength in sign), applies up to 5 subtraction factors (haranas) for debility, combustion, enemy-sign placement, rising/non-rising sign on Lagna, and malefic affliction; sums across planets. Amshayu: similar but uses Navamsa positions, not rashi positions. Nisargayu: fixed 120-year natural total divided per-planet, then reduced by the same haranas. Jaimini: a classical scoring based on lord-of-8th placement and Chara Karaka configurations. All four produce a years-number; system stores all four but gates surfacing by user-role.

**Worked example.** Astrologer runs ayus on a new client, Sreeja. Pindayu = 71, Amshayu = 76, Nisargayu = 74, Jaimini = Madhya. Agreement is high, all in mid-70s, Jaimini confirms medium range. The astrologer never mentions the specific numbers to Sreeja. Instead, when Sreeja asks about a big life decision (buying a house, long-term investment), the astrologer privately notes "ayus window supports a 20-year horizon" and advises accordingly.

---

### E7 — Extended Vargas, Sarvatobhadra Chakra, Upagrahas

**What it is.** Three distinct additions bundled into one PRD because all three concern "classical instruments not in most software":

**Extended Vargas** — divisional charts beyond the standard Shodashavarga set. Josi already has D1 through D60; this adds D72, D84, D100, D108, D144 (each a different "zoom level" into specific life themes — e.g., D108 for very fine karmic patterns).

**Sarvatobhadra Chakra (SBC)** — a **9×9 grid** that maps the 28 nakshatras (including Abhijit), 12 rashis, 8 directions, weekdays, tithis, and vowels together. Used for muhurta (auspicious-timing selection), prasna (horary), and evaluating names/letters (which is why it's central to naming a child or a business).

**Upagrahas** — "sub-planets" computed from the Sun and day/night duration. Josi has Gulika and Mandi; this adds 8 more: Dhuma, Vyatipata, Parivesha, Chapa, Upaketu, Kala, Yamakantaka, Ardhaprahara. Two different classical schools (Kerala vs North Indian) compute these differently — both are shipped as separate sources.

**Why it matters.** These are what separates a "full classical platform" from a "basic platform." Professional astrologers notice their absence immediately.

**Regular-user flow.** User comes in for a **name-selection consultation** (naming a newborn, renaming a business). AI chat: *"I can check a name against your Sarvatobhadra Chakra — each letter has a classical compatibility score with your chart. Give me 3–5 candidate names and I'll rank them."* User enters names; AI scores them using SBC grid logic and returns a ranked list with explanations.

**Astrologer flow.** Workbench has a **Vargas page** that lets the astrologer select any varga (D1-D144) and see the chart rendered in that division. Also an **SBC grid view** — clickable 9×9 grid where hovering a cell shows which of the user's natal points fall on it. An **Upagrahas table** with school toggle (Kerala | North Indian). Used extensively for muhurta consultations (picking wedding dates, surgery dates, business-launch dates).

**Behind the scenes.** Each extended varga is a deterministic division algorithm (e.g., D108 = "divide each rashi into 108/12 = 9 equal parts, assign to rashis by a specific formula from Uttara Kalamrita"). SBC is a static grid loaded once, with runtime lookup logic for "does this letter/nakshatra/weekday hit an auspicious cell given the chart's key points?" Upagrahas are computed from Sun's position and the day's duration (sunrise to sunset) divided into classical fractions; each upagraha has a per-school formula.

**Worked example.** Lakshmi is naming her newborn. Her astrologer uses Josi's SBC tool, enters the baby's birth time, and tests 4 candidate names: Aarav, Aryan, Advait, Abhiram. The SBC grid highlights: Aarav's first syllable maps to a nakshatra cell adjacent to the baby's natal Moon nakshatra (harmonious); Aryan's maps to an aspected-malefic cell (avoid); Advait's maps to a supporting-friend cell (strong); Abhiram's to a neutral cell. The astrologer recommends Advait or Aarav.

---

### E8 — Western Depth (Arabic Parts, Fixed Stars, Harmonics, Eclipses, Uranian)

**What it is.** Five additions to Josi's Western module, bringing it to professional Western-astrology parity:

**Arabic Parts / Hellenistic Lots** — computed points derived by adding/subtracting longitudes (e.g., Part of Fortune = Ascendant + Moon − Sun for day births). 50 classical Lots with sect-aware formulas (daytime births use one formula, nighttime another).

**Fixed Stars** — 60 bright stars (Regulus, Spica, Antares, Aldebaran — the "Royal Stars" — plus Algol, Sirius, Vega, etc.), with classical interpretations when they conjunct natal planets within 1°.

**Harmonic Charts** — mathematical transforms of the natal chart revealing hidden patterns (H5 for talent, H7 for spirituality, H9 for marriage — philosophically parallel to Vedic Navamsa, H12 for karmic themes).

**Eclipses** — 250-year NASA eclipse catalogue, with Saros cycle identification and natal-point conjunctions.

**Uranian midpoints** — the "planetary pictures" methodology from the Hamburg School: midpoints between planet pairs, plus 8 hypothetical planets (Cupido, Hades, Zeus, Kronos, Apollon, Admetos, Vulkanus, Poseidon).

**Why it matters.** Without these, Josi cannot credibly serve Western professional astrologers. With them, we match Solar Fire (the industry-standard Western software).

**Regular-user flow.** For Western-leaning users: AI chat becomes much more specific about Western content. *"Your Part of Fortune is in Pisces in your 7th house — a classical indicator of good fortune through partnerships, especially creative or spiritual ones."* Or: *"Your natal Sun is conjunct the fixed star Regulus at 0°18' — classical tradition associates this with honor and prominence, with the caveat 'unless fallen through arrogance' (Ptolemaic warning)."*

**Astrologer flow.** Workbench has a dedicated **Western Depth tab** with sub-panels for each of the five. The Fixed Stars panel lists every conjunction within 1° ordered by star-magnitude. The Harmonics panel lets you toggle any of H5/H7/H9/H10/H11/H12/H16. The Uranian panel lists every midpoint configuration where a natal planet sits within 2° of a midpoint of two other planets.

**Behind the scenes.** Arabic Parts: formula lookup table (50 Lots) with sect-check branching. Fixed Stars: Swiss Ephemeris `swe.fixstar()` with precession-adjusted positions. Harmonics: multiply every natal longitude by H, take modulo 360. Eclipses: local NASA Canon JSON file, linear scan over 250-year window. Uranian midpoints: pairwise half-sums of 10 planets + 3 angles = 78 midpoints, then compare against natal positions within 2°.

**Worked example.** Rebecca, a Western-trained user, asks: *"Anything unusual in my chart?"* AI responds: *"Your natal Sun at 29°08' Leo sits within 52' of Regulus — that's the kind of contact Western tradition flagged as 'kingly'. But Ptolemy's qualifier applies: Regulus gives prominence *until* undone by personal arrogance. Also: your Part of Fortune (6°14' Sagittarius) is conjunct your Ascendant ruler — a classical fortune-enhancer. Finally, your H9 chart (the 'marriage harmonic') puts Venus exactly on its Ascendant — a strong partnership signature if you're approaching marriage."*

---

### E8b — Asteroids, Centaurs & Planetoids

**What it is.** Modern Western astrology has folded in celestial bodies discovered after the classical canon: the **Big Four asteroids** (Ceres, Pallas, Juno, Vesta — archetypally interpreted by Eleanor Bach and Demetra George as the missing feminine principles), **Chiron** (the "wounded healer" — Melanie Reinhart's formulation), **Eris** (discord; the dwarf planet whose discovery demoted Pluto), **other centaurs** (Pholus, Nessus, Chariklo, Hylonome), and **select TNOs** (Sedna, Haumea, Makemake, Orcus). 15-20 minor bodies in total.

**Why it matters.** Modern Western practitioners universally use at least Chiron; most use Ceres and Juno. Without asteroid support, Josi looks dated to Western users. **Critical constraint:** these bodies are *strictly isolated from Vedic*. Classical Parashari has no interpretation for Ceres-in-the-4th. The engine ensures asteroids never leak into Vedic yoga rules or Vedic aggregations.

**Regular-user flow.** Western-leaning users get Chiron and the Big Four integrated into AI chat answers. *"Your Chiron is in the 7th house — classically a pattern of healing through relationships (the wound *and* the medicine both show up there)."*

**Astrologer flow.** Workbench's Western Depth tab gets an **Asteroids sub-panel** with toggles per body. Modern Western astrologers enable Ceres/Juno/Vesta/Chiron by default. Classical Hellenistic astrologers disable them. A Vedic astrologer sees them only if they explicitly turn on "Western depth" for a chart — otherwise invisible.

**Behind the scenes.** Swiss Ephemeris supports all major asteroids via its `swe.calc_ut()` API with asteroid numbers. For numbered-but-not-built-in bodies (Nessus = asteroid 7066, Chariklo = 10199), system registers external asteroid ephemeris files. Position computation is identical to planets; only the interpretation/integration is different.

**Worked example.** Jenny, a modern Western practitioner, pulls her new client Mark's chart. Chiron is in Aries in the 1st house. Jenny: *"Your core wound-and-gift pattern is self-identity (Chiron in the 1st) — the thing that's hardest for you to own will also be your teaching to others once owned."* Classical Western or Vedic astrologers would not have this interpretive layer.

---

### E9 — KP System (Sub-Lord, Significators, Ruling Planets, KP Horary)

**What it is.** **Krishnamurti Paddhati (KP)** is a 20th-century Indian astrological system developed by K.S. Krishnamurti (1908–1972). It's notable because it's the **single classical system with single-source authority** — no centuries of commentary disagreement; Krishnamurti himself specified every rule, and his sons and students preserved it. KP's key innovations: **Sub-lord** (each of the 27 nakshatras is subdivided into 9 parts proportional to Vimshottari dasa lord periods, producing 243 "subs"; planets and house-cusps each have a unique sub-lord, which is KP's primary predictor); **5-level significator hierarchy** (every house has 5 levels of planets that signify it — a specific ordering that enables clean yes/no outcome prediction); **Ruling Planets** (a dynamic set of 4-5 planets computed for any moment from the day-lord, Lagna, and Moon positions); **249-number horary method** (KP's famous horary — the querent picks a number from 1 to 249 and the system casts the horary chart with that number mapped to a specific zodiacal longitude).

**Why it matters.** KP is the **dominant horary methodology in South India and Sri Lanka**, with millions of practicing astrologers. For marriage, career, litigation, and yes/no questions, KP is preferred over BPHS Parashari by many practitioners.

**Regular-user flow.** User asks: *"Should I take this job offer?"* AI: *"This is a yes/no question — let me route it through KP, which is designed exactly for this. Pick a number between 1 and 249 that feels right to you, without thinking too hard."* User picks 137. AI casts a KP horary at current moment with 137 as Ascendant-proxy. AI analyzes the cuspal sub-lord of the 10th house (career) and its significators. Returns: *"The 10th cusp's sub-lord signifies the 6th and 10th houses — classically favorable for a new career role, but with some service/competition component. KP reading: yes, take it, but expect the role to involve more hands-on work than positioned as."*

**Astrologer flow.** KP practitioners get their full toolkit in a dedicated **KP panel**: sub-lord table for all planets and cusps, 5-level significator map for all 12 houses, real-time Ruling Planets display, horary-number-method form (enter moment + number, get full analysis). Parashari astrologers typically ignore this panel; dedicated KP astrologers use it as their primary workspace.

**Behind the scenes.** Sub-lord: the zodiac (360°) is split into 27 nakshatras of 13°20' each; each nakshatra subdivided into 9 parts proportional to Vimshottari dasa years (Ketu 7yr → 7/120 of 13°20' = 46'40", etc.). 27 × 9 = 243 sub-divisions total. Each planet's longitude maps to exactly one sub. 5-level significators: (1) planets in the house, (2) planets in nakshatras of planets-in-house, (3) lord of the house, (4) planets in nakshatras of the house-lord, (5) planets conjunct the house-lord. 249-number method: a static lookup table maps each number to a specific zodiacal longitude (from Aries 0°00' at number 1 to Pisces 29°41' at number 249). System uses Placidus houses by default (KP-standard).

**Worked example.** Lokesh asks his KP astrologer: *"Will I get married this year?"* Astrologer: "Pick a number 1–249." Lokesh: "88." KP casts horary. Cuspal sub-lord of the 7th (marriage) is Jupiter. Jupiter's significators: the 7th (marriage), 2nd (family), 11th (gains). All marriage-favorable. Astrologer checks Ruling Planets at the query moment — Jupiter and Venus among them. Confirmed. *"Yes — within this calendar year. Watch May through August as the peak window."*

---

### E10 — Prasna / Horary (Vedic Kerala + KP Unified)

**What it is.** **Prasna** (Sanskrit "question") is classical horary — answering a specific question by casting a chart for the moment the question is asked, without needing the querent's birth details. Two traditions dominate: **Kerala Prasna** (codified in Prasna Marga, 17th century — deeply integrated with Sarvatobhadra Chakra, omen analysis, and Tajaka aspects) and **KP Horary** (from E9). E10 is a **unified engine** that takes a question and runs it through both methods in parallel, then synthesizes. Kerala excels at omens, lost articles, elemental questions (health, travel). KP excels at binary yes/no outcomes with confidence.

**Why it matters.** Prasna is the most *immediately applicable* astrology — it doesn't require the user's birth chart, just the moment. Every astrology platform with a chat surface should support it. And unifying Kerala + KP gives richer answers than either alone.

**Regular-user flow.** User asks AI chat: *"I lost my wallet — will I find it?"* AI: *"This is a classic Prasna question. Let me cast a chart for this moment."* Casts chart. Runs both Kerala Prasna (Arudha of Prasna Lagna, Navamsa yes/no, planetary hour, omen rules) and KP Horary (automatic-number variant or ask user for a number). Returns: *"Both methods agree on 'yes, findable.' Kerala says: the Arudha of your Prasna Lagna is in a stable sign, and Mercury (signifier of lost objects) is well-placed. KP says: the 2nd-house cuspal sub-lord is a significator of the 11th (gains) — recovery likely. Time frame: within the next 3–5 days. Most likely location: somewhere connected to recent travel or a public place you frequent."*

**Astrologer flow.** Professional Prasna-practicing astrologers (especially in Kerala) get a **Prasna console** — a single form: question text, moment, location, optional category. The engine runs both methods, displays Kerala and KP results side by side with per-method reasoning trace. Astrologer selects primary method per their preference, synthesizes the reading.

**Behind the scenes.** The engine **orchestrates** existing engines rather than reimplementing: E1a for Vimshottari dasa at the query moment, E5 for Tajaka aspects and Sahams, E7 for Sarvatobhadra Chakra omen rules, E9 for KP horary mechanics. New primitives added: Arudha of Prasna Lagna (count from Prasna Lagna's sign to its lord's sign; project same count from lord), Navamsa yes/no (position of query-house lord in Navamsa indicates outcome), planetary-hour lord computation, rule-based omen scorer.

**Worked example.** Deepak asks: *"Should I go on this trip next week — will it be safe?"* AI routes to Prasna. Casts chart for now. Kerala: Prasna Lagna in Sagittarius (travel sign, auspicious), 9th lord (long journeys) strong, no malefics on 4th (home) or 8th (obstacles), hora-lord Mercury favorable. KP: cuspal sub-lord of 9th is Jupiter, significator of 9th and 11th — favorable. Omen rule: the time of asking falls in a benefic hora. AI: *"Both methods converge on safe travel. Kerala flags: your arrival is likely smoother than the departure — expect a minor delay or logistical hiccup at the start, then a good trip."*

---

### E17 — Chart Rectification (estimating accurate birth time from life events)

**What it is.** **Birth time is the single most error-prone input to any astrology calculation.** A 4-minute error shifts the Ascendant by 1°. A 2-hour error can move it by an entire house. Without accurate birth time, *everything downstream is wrong* — Ascendant, all 12 houses, the Navamsa Ascendant, every divisional chart's Ascendant, the dasa starting lord, all dasa period boundaries. **Rectification** is the classical practice of estimating the correct birth time by triangulating it against known life events. Traditionally done by a senior astrologer in a multi-hour interview. E17 automates it.

The engine takes: approximate birth date (known), a candidate time window (e.g., ±4 hours), and a list of K known life events (marriage, career change, child's birth, parental death, etc.). It searches the window at 1-minute resolution, scores each candidate birth time using **four independent techniques** (Vimshottari dasa-lord significations vs event category, slow-transit house-matter matching, Western secondary progressions, divisional-chart consistency), and returns the top 5 candidate times with confidence scores and full per-method reasoning.

**Why it matters.** Besides correctness, this is a **user-acquisition lever**. "We can estimate your birth time from your life events" is a differentiating promise against every competitor who forces users to enter a time they don't know. Particularly resonant for diaspora users without birth certificates, people with rounded-to-the-hour hospital records, and adopted users with sealed records.

**Regular-user flow.** User onboarding detects "unknown or approximate birth time." AI chat: *"I can estimate your birth time if you can tell me 4–6 major life events (with dates). Marriage, career changes, big moves, child births, parent passings — any memorable turning points. The more events, the tighter the estimate."* User enters 5 events. AI runs rectification. Returns: *"Your most likely birth time is 6:47 AM (confidence 0.82). Two other candidates: 6:34 AM (0.71) and 7:12 AM (0.64). Your marriage date aligns best with 6:47; your career change aligns best with 6:47; your first child's birth is slightly better at 6:34. Want me to proceed with 6:47 as the working time, or schedule a video call with a professional astrologer to finalize?"*

**Astrologer flow.** Rectification is a premium service astrologers charge for. Workbench has a **Rectification console**: enter candidate window, enter events with categories, run. Engine returns top 5 candidates with per-event per-method score breakdowns. Astrologer reviews the reasoning (e.g., "candidate 6:47 scores highly on marriage because Venus-Moon antardasa aligns and transiting Jupiter hit the 7th lord on the marriage date"), may adjust weights or add events, and finalizes the birth time with a certification.

**Behind the scenes.** 1-minute resolution over ±4 hours = 480 candidates. Coarse-to-fine: first pass at 5-min resolution (96 candidates) to find promising neighborhoods, then 1-min refinement around top 10 coarse winners. Each candidate gets 4 method scores: (1) for each event, check which Vimshottari MD+AD is active; score based on lord's house-lordship and classical significations matching event category. (2) For each event date, check slow-transit (Jupiter, Saturn, Rahu, Ketu) aspects to candidate's natal houses; score by matter-of-house match. (3) Western secondary progressions: compute progressed planets at event date, score angular contacts. (4) Varga consistency: check Lagna lord's position in D9 and D10 against reported marriage quality and career shape. Scores combined with configurable weights.

**Worked example.** Anita's hospital record says "around 2 PM." She reports: marriage Jun 2015, first child Oct 2017, career change Mar 2020, father's death Aug 2022. Engine searches 12:00–16:00 at 1-min resolution. Best candidate: **2:23 PM, confidence 0.86**. Dasa alignment: marriage happened in Venus-Saturn (Venus = 7th lord, classical marriage signal — fits); career change happened in Venus-Mercury with transiting Saturn hitting 10th lord (fits strongly); father's death in Venus-Ketu with transiting Saturn over natal Sun (fits — Sun signifies father). Second candidate (2:08 PM, 0.74) fits marriage better but career change slightly worse. Astrologer finalizes 2:23 PM.

---

## How it all fits together — a complete user story

Let's walk a single user through the full system to see how these 15 features compose.

**Character: Priya.** 34 years old, Indian-diaspora in London, never been to an astrologer before, curious about astrology. Birth time approximate.

**Day 1 — Onboarding.** Priya downloads Josi. Enters birth date (known), birthplace, *approximate* birth time ("sometime before sunrise, maybe 5-6 AM — mom isn't sure"). Josi flags the approximate time and offers rectification. Priya lists 4 events: graduated college Jun 2014, moved to London Mar 2017, got married Oct 2019, started her current job Feb 2023. System runs **E17 rectification**, returns top candidate 5:34 AM with 0.79 confidence. Priya accepts; her chart is finalized.

**Day 1 continued — First conversation.** Priya asks AI chat: *"What's special about my chart?"* AI runs **E4a (60 yogas) and E4b (250 yogas)** across her chart. Returns 6 active yogas with strengths. Dominant: Gaja Kesari (0.88, Jupiter-Moon kendra — intelligence/respect). Priya asks follow-ups; AI uses citations like "per BPHS Ch.36."

**Day 3 — "What's happening right now?"** Priya asks. AI runs **E1a (dasas)**: Saturn-Mercury under Vimshottari, Mars under Yogini. Runs **E6a (transits)**: Priya is in Ashtama Shani (Saturn in 8th from Moon). Synthesizes: *"A restructuring period — Saturn-Mercury asks for systematic work, Ashtama Shani pushes inward psychological work. Not external expansion right now; this is the season for consolidation."*

**Day 14 — Birthday approaches.** On April 3 (her birthday), AI proactively messages: *"Your new annual chart just started. Want a read?"* Priya accepts. **E5 (Varshaphala)** runs: Muntha in 7th (partnerships), Varsheswara Jupiter in 10th (career growth), 3 Tajaka yogas active. AI gives a year-ahead reading focused on career-through-partnerships.

**Day 30 — A specific question.** Priya is considering a new job offer. Asks AI: *"Should I take this job?"* AI: *"This is a classic yes/no question — best handled via KP horary. Pick a number 1–249."* Priya: 67. **E9 (KP horary)** runs. Cuspal sub-lord of 10th is Jupiter, favorable significators. Answer: *"Yes, take it — but expect more collaborative/partnership work than described."*

**Day 45 — Complexity, routed to astrologer.** Priya asks about marriage and health concerns in her family. AI recognizes complexity, offers: *"This is a multi-dimensional question best handled by a human astrologer. Can I connect you with someone from our network?"* Priya books a 1-hour video consultation with astrologer Lakshmi.

**Day 50 — The consultation.** Lakshmi opens Priya's chart in the **Workbench**. She sees:
- **E1a + E1b (all 6 dasa systems)** side by side — Vimshottari + Yogini + Ashtottari + Chara + Narayana + Kalachakra.
- **E2a (full Ashtakavarga with shodhana)** — Lakshmi notes the shodhit values diverge from raw in the 7th house.
- **E3 (Jaimini panel)** — Priya's Atmakaraka is Venus; Lakshmi reads this as "soul theme: beauty, harmony, relational refinement."
- **E4a + E4b (all 250 yogas)** — 8 active yogas with strengths and citations.
- **E5 (Varshaphala page)** — current year's annual chart.
- **E5b (Ayus)** — Lakshmi sees the 4-method ensemble (all in mid-70s, all agree). Never mentions numbers to Priya.
- **E6a (transit timeline)** — Ashtama Shani overlay visible.
- **E7 (Sarvatobhadra Chakra)** — Lakshmi uses this to choose an auspicious date for Priya to sign her new employment contract.
- **E8 (Western depth)** — Lakshmi checks Priya's Part of Fortune and Chiron position for Western-context reading since Priya grew up abroad.
- **E8b (Asteroids)** — Chiron in 7th: "healing through relationships."
- **E9 (KP)** — Lakshmi checks the cuspal sub-lord of the 7th for marriage timing.
- **E10 (Prasna)** — for Priya's health question about her father, Lakshmi casts a Kerala Prasna at the current moment.
- **E17 (Rectification)** — Lakshmi reviews the original rectification; re-runs with the new event data Priya provided during consultation, confirms 5:34 AM holds.

Lakshmi writes a structured reading. The document generated includes citations to every classical source used, every technique activated, and every decision point. Priya downloads the PDF; the reading becomes a durable artifact of her consultation.

**Day 90 — Back to AI chat.** Priya returns to the AI. Because Josi stored Lakshmi's reading, AI chat now has Lakshmi's context and frames its own answers in ways that reinforce — not contradict — Lakshmi's reading. Priya's journey has a continuous narrative thread across AI and human interactions.

---

## How to use this document

**For product reviewers:** If a PRD feels abstract, find its section here. The user stories and worked examples should make the purpose clear within 2 minutes.

**For engineers implementing a PRD:** Read the corresponding story before reading the PRD. The story tells you *what experience you're building*; the PRD tells you *how to build it*. Both together prevent shipping a technically-correct feature that solves the wrong problem.

**For astrologers on the advisory panel:** Read the "Behind the scenes" and "Worked example" sections critically. The goal of this document is to surface the *user experience* of the classical tradition — if an example feels wrong by your practice, flag it. These stories shape how end-users and professionals will interact with the tradition through Josi.

**For marketing:** The worked examples double as case studies. The full-system narrative ("Priya's journey") is the kind of story that turns a feature list into a compelling product narrative.

**Living document.** As PRDs are revised or new ones added, update the corresponding section. Every story should match what ships.
