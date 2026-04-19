⏺ Three-part answer. Let me take them in order.

  ★ Insight ─────────────────────────────────────
  - The value of YAML authoring becomes obvious only when you picture the alternative: 1,000+ yogas as hardcoded Python would be unshippable. Each rule would need an engineer, each fix would be a code deploy, and a Sanskrit-literate classical advisor couldn't contribute without learning Python. Separating content (YAML) from engine (Python) is exactly the
  pattern that makes dbt transform 10,000 SQL models and makes Kubernetes run on 10,000 CRDs. This is the architectural choice that makes the 1,000-yoga target actually achievable.
  - On the gap analysis: there are 3 honest gaps against Maitreya I didn't explicitly spec (asteroids/planetoids, chart rectification, full Ayus longevity suite). I'll flag them below and propose where they land. Everything else from our original Maitreya comparison is covered.
  ─────────────────────────────────────────────────

  ---
  Part 1 — What "YAML authoring" actually means

  Instead of writing Python code to detect a yoga, we write a data file describing it. Here's Gaja Kesari Yoga as a YAML rule (simplified from F6 DSL):

  # src/josi/rules/yoga/raja/gaja_kesari.yaml
  rule_id: yoga.raja.gaja_kesari
  source_id: bphs
  version: 1.0.0
  technique_family_id: yoga
  output_shape_id: boolean_with_strength
  citation: "BPHS Ch.36 v.14-16"

  classical_names:
    en: "Gaja Kesari Yoga"
    sa_iast: "gajakesarī-yoga"
    sa_devanagari: "गजकेसरी-योग"
    ta: "கஜகேசரி யோகம்"

  rule_body:
    activation:
      all_of:
        - predicate: moon_in_kendra_from
          of: jupiter
        - predicate: planet_not_debilitated
          planet: jupiter
        - predicate: planet_not_combust
          planet: jupiter
    strength_formula:
      type: weighted_average
      inputs:
        - value: planet_dignity_score(jupiter)
          weight: 0.5
        - value: planet_dignity_score(moon)
          weight: 0.5
      clamp: [0, 1]

  The engine reads this file, validates it, computes a sha256 content hash, and inserts one row into classical_rule. On every new chart, the engine walks every rule and evaluates the predicates. No code change needed to add a rule — just the YAML file + test fixture + PR review.

  This is how one person can ship 50 new yogas in a week without touching the engine. That's the point.

  ---
  Part 2 — Honest gap analysis vs Maitreya (and other leading software)

  Re-running the original comparison against the 73 PRDs we now have:

  Fully covered (was in initial gap list)

  ┌─────────────────────────────────────────────────────────────────────────┬─────────────────────────────────────┐
  │                            Maitreya feature                             │               Our PRD               │
  ├─────────────────────────────────────────────────────────────────────────┼─────────────────────────────────────┤
  │ D1–D144 vargas                                                          │ P2/E7                               │
  ├─────────────────────────────────────────────────────────────────────────┼─────────────────────────────────────┤
  │ Multiple dasa systems (Yogini, Ashtottari, Chara, Narayana, Kalachakra) │ P1/E1a + P2/E1b                     │
  ├─────────────────────────────────────────────────────────────────────────┼─────────────────────────────────────┤
  │ Ashtakavarga Trikona + Ekadhipatya shodhana                             │ P1/E2a                              │
  ├─────────────────────────────────────────────────────────────────────────┼─────────────────────────────────────┤
  │ Jaimini (Chara Karakas, Arudhas, Rashi Drishti)                         │ P2/E3                               │
  ├─────────────────────────────────────────────────────────────────────────┼─────────────────────────────────────┤
  │ Classic Yoga detection (250 → 1000+)                                    │ P1/E4a + P2/E4b + P4/Reference-1000 │
  ├─────────────────────────────────────────────────────────────────────────┼─────────────────────────────────────┤
  │ Tajaka / Varshaphala (annual, Muntha, Sahams, Tajaka yogas)             │ P2/E5                               │
  ├─────────────────────────────────────────────────────────────────────────┼─────────────────────────────────────┤
  │ Sarvatobhadra Chakra                                                    │ P2/E7                               │
  ├─────────────────────────────────────────────────────────────────────────┼─────────────────────────────────────┤
  │ Full Upagrahas (Dhuma, Vyatipata, etc.)                                 │ P2/E7                               │
  ├─────────────────────────────────────────────────────────────────────────┼─────────────────────────────────────┤
  │ KP sub-lord system                                                      │ P2/E9                               │
  ├─────────────────────────────────────────────────────────────────────────┼─────────────────────────────────────┤
  │ Prasna / Horary                                                         │ P2/E10                              │
  ├─────────────────────────────────────────────────────────────────────────┼─────────────────────────────────────┤
  │ Sade Sati + Dhaiya                                                      │ P1/E6a                              │
  ├─────────────────────────────────────────────────────────────────────────┼─────────────────────────────────────┤
  │ Arabic Parts / Lots (50+)                                               │ P2/E8                               │
  ├─────────────────────────────────────────────────────────────────────────┼─────────────────────────────────────┤
  │ Fixed Stars + parans (60+)                                              │ P2/E8                               │
  ├─────────────────────────────────────────────────────────────────────────┼─────────────────────────────────────┤
  │ Harmonic Charts (7)                                                     │ P2/E8                               │
  ├─────────────────────────────────────────────────────────────────────────┼─────────────────────────────────────┤
  │ Eclipses                                                                │ P2/E8                               │
  ├─────────────────────────────────────────────────────────────────────────┼─────────────────────────────────────┤
  │ Uranian sensitive points (midpoints, reflection, TNPs)                  │ P2/E8                               │
  ├─────────────────────────────────────────────────────────────────────────┼─────────────────────────────────────┤
  │ Multiple chart styles (N/S/E Indian, Bengali, Western wheel)            │ P2/E12                              │
  ├─────────────────────────────────────────────────────────────────────────┼─────────────────────────────────────┤
  │ Dasa tree + bar diagrams                                                │ P2/E12                              │
  ├─────────────────────────────────────────────────────────────────────────┼─────────────────────────────────────┤
  │ Partner / synastry charts                                               │ P2/E12 + existing                   │
  ├─────────────────────────────────────────────────────────────────────────┼─────────────────────────────────────┤
  │ Hora (planetary hours)                                                  │ existing + P2/E5 for Tajaka Hora    │
  └─────────────────────────────────────────────────────────────────────────┴─────────────────────────────────────┘

  Honest gaps — NOT in current PRDs (I should flag these)

  Three real gaps I didn't explicitly spec:

  Gap 1: Asteroids / Planetoids / Centaurs

  Maitreya supports minor bodies: Chiron, Ceres, Pallas, Juno, Vesta, Eris (plus centaurs Nessus, Pholus, Chariklo). Swiss Ephemeris already calculates these — it's purely a question of enabling them.

  Recommendation: add to P2/E8 scope as an amendment, OR create a small new PRD E8b — Asteroids & Centaurs. Low effort (~3-5 days); adds ~10 points per chart.

  Gap 2: Chart Rectification

  When the birth time is unknown or approximate, astrologers use known life events (marriage date, children, career shifts, deaths) to work backwards and estimate the accurate birth time. Maitreya has a basic rectification wizard.

  Recommendation: this is a substantive feature — belongs as a new PRD E14 — Chart Rectification in P2 or P3 (moderate effort, ~3-4 weeks). Deferred today; flag explicitly.

  Gap 3: Full Ayus (Longevity) suite

  We have Sodhya Pinda (part of it). Maitreya has:
  - Pindayu (longevity via weighted planet strengths)
  - Amshayu (via divisional chart strength)
  - Nisargayu (natural lifespan per planet)
  - Jaimini Ayur-dasha (longevity via Jaimini scheme)
  - Ayur-harana (subtractions for afflictions)

  Recommendation: new PRD E5b — Full Ayus Suite in P2 (~2-3 weeks). Important for classical Vedic readings.

  Minor items — probably worth adding but not gaps per se

  ┌───────────────────────────────────────────────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────────────────┐
  │                                             Item                                              │                              Status                               │                            Recommendation                             │
  ├───────────────────────────────────────────────────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────────────┤
  │ Ephemeris table export (printable daily/monthly)                                              │ Swiss Ephemeris computes; we'd just need a PDF/CSV export surface │ Small P2 amendment (~1 week)                                          │
  ├───────────────────────────────────────────────────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────────────┤
  │ Sphuta sensitive points (Beeja Sphuta, Kshetra Sphuta, Pranapada, Mrityu Sphuta, Deha Sphuta) │ Not specced                                                       │ Add to P2/E7 as sub-items (~1 week)                                   │
  ├───────────────────────────────────────────────────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────────────┤
  │ Tamil classical muhurtas (Chandrashtama avoidance, Horai, Yamaganda, Durmuhurtam precise)     │ Existing partial; deeper covered as extensions                    │ Already in scope via existing panchang_calculator.py + Tamil calendar │
  ├───────────────────────────────────────────────────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────────────┤
  │ Transit-triggered yogas                                                                       │ Yogas defined for natal; transits checked separately              │ Edge case; can be added via E6a post-P1                               │
  └───────────────────────────────────────────────────────────────────────────────────────────────┴───────────────────────────────────────────────────────────────────┴───────────────────────────────────────────────────────────────────────┘

  ---
  Part 3 — Every item we're adding, with short description + PRD reference

  Organized by category. Everything shippable has a PRD; the 3 gaps above are flagged as "not yet".

  Dasa systems (how planetary/sign periods are assigned to life phases)

  ┌─────────────────────────────┬─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┬───────────────────┐
  │            Item             │                                              What it is, in plain language                                              │        PRD        │
  ├─────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼───────────────────┤
  │ Vimshottari Dasa (existing) │ The most-used Vedic dasa. 120-year cycle across 9 planetary periods, ordered from Moon's birth nakshatra lord.          │ Existing codebase │
  ├─────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼───────────────────┤
  │ Yogini Dasa                 │ 36-year cycle, 8 sub-divinity periods (Mangala, Pingala, Dhanya…). Used alongside Vimshottari for cross-check.          │ P1 / E1a          │
  ├─────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼───────────────────┤
  │ Ashtottari Dasa             │ 108-year cycle, 8 planetary periods. Applies especially when Moon in krishna paksha.                                    │ P1 / E1a          │
  ├─────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼───────────────────┤
  │ Chara Dasa (Jaimini)        │ Sign-based. Each mahadasha is a rasi, not a planet. Direction depends on Atmakaraka's placement.                        │ P2 / E1b          │
  ├─────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼───────────────────┤
  │ Narayana Dasa (Jaimini)     │ Also sign-based but starts from 7th or Karakamsa rather than Lagna.                                                     │ P2 / E1b          │
  ├─────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼───────────────────┤
  │ Kalachakra Dasa             │ The most complex. Based on Moon's nakshatra pada. 9 periods per pada in Savya (forward) or Apasavya (reverse) sequence. │ P2 / E1b          │
  ├─────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼───────────────────┤
  │ Mudda Dasa (Tajaka)         │ Year-scale dasa running inside the Varshaphala annual chart. Compresses Vimshottari into 1 year.                        │ P2 / E5           │
  └─────────────────────────────┴─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┴───────────────────┘

  Divisional charts (vargas — same chart viewed at different "resolutions")

  Each varga re-maps the 30° of each sign onto a new set of 30° blocks, revealing different life areas.

  ┌─────────────────────────────┬────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┬──────────┐
  │            Item             │                                                                                                                                                      What it reveals                                                                                                                                                       │   PRD    │
  ├─────────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼──────────┤
  │ D1–D60 (20 charts,          │ Main life (D1), wealth (D2), siblings (D3), property (D4), progeny (D5), health (D6), children (D7), longevity (D8), marriage/dharma (D9), career (D10), death (D11), parents (D12), vehicles (D16), spiritual (D20), education (D24), strengths/weaknesses (D27), misfortunes (D30), auspicious/inauspicious (D40),       │ Existing │
  │ existing)                   │ paternal legacy (D45), past karma (D60)                                                                                                                                                                                                                                                                                    │          │
  ├─────────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼──────────┤
  │ D72 Ashtottariamsa          │ 72-fold division; used for deep karmic analysis                                                                                                                                                                                                                                                                            │ P2 / E7  │
  ├─────────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼──────────┤
  │ D81 Navanavamsa             │ Division of Navamsa itself — fine-grained partner analysis                                                                                                                                                                                                                                                                 │ P2 / E7  │
  ├─────────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼──────────┤
  │ D84 Chaturashitiamsa        │ 84-fold — very subtle life-phase patterns                                                                                                                                                                                                                                                                                  │ P2 / E7  │
  ├─────────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼──────────┤
  │ D100 Shatamsa               │ 100-fold — reputation & legacy                                                                                                                                                                                                                                                                                             │ P2 / E7  │
  ├─────────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼──────────┤
  │ D108 Ashtottaramsa          │ Sacred 108; overall life quality. Two variant formulas (composite vs direct).                                                                                                                                                                                                                                              │ P2 / E7  │
  ├─────────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼──────────┤
  │ D120 Ashtottari Varga       │ 120 divisions; extended life analysis                                                                                                                                                                                                                                                                                      │ P2 / E7  │
  ├─────────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼──────────┤
  │ D144 Dvadashadvadashamsa    │ D12 × D12; deepest parental/ancestral karma                                                                                                                                                                                                                                                                                │ P2 / E7  │
  ├─────────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼──────────┤
  │ D150 Nadiamsa               │ 150 unequal divisions with 1,800-name Nadi lookup table. Associated with Nadi astrology.                                                                                                                                                                                                                                   │ P2 / E7  │
  └─────────────────────────────┴────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┴──────────┘

  Yogas (specific planetary combinations producing named life effects)

  ┌────────────────────┬───────┬─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┬─────────────────────┐
  │       Batch        │ Count │                                                                                               What it is                                                                                                │         PRD         │
  ├────────────────────┼───────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼─────────────────────┤
  │ P1 core 60         │ 60    │ Pancha Mahapurusha (5 great-person yogas), Raja (kingly/authority), Dhana (wealth), Chandra (Moon-based), Surya (Sun-based), Dushta (afflictive). Curated most-cited.                                   │ P1 / E4a            │
  ├────────────────────┼───────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼─────────────────────┤
  │ P2 full 250        │ +190  │ Adds Nabhasa (32 — shape-of-chart yogas like Rajju/Musala), Parivartana (30 — mutual-exchange yogas), more Raja/Dhana/Chandra/Surya/Dushta variants, Tajaka yogas (16 applying/separating aspect pairs) │ P2 / E4b            │
  ├────────────────────┼───────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼─────────────────────┤
  │ P4 reference 1000+ │ +750  │ Full long-tail from every major classical text. Bulk content done via rule authoring console + classical advisors, no engineering.                                                                      │ P4 / Reference-1000 │
  └────────────────────┴───────┴─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┴─────────────────────┘

  Ashtakavarga (numerical system scoring strength of each sign for each planet)

  ┌──────────────────────────────┬────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┬──────────┐
  │             Item             │                                                       What it is                                                       │   PRD    │
  ├──────────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼──────────┤
  │ Bhinnashtakavarga (existing) │ Each planet's individual bindu score per sign.                                                                         │ Existing │
  ├──────────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼──────────┤
  │ Sarvashtakavarga (existing)  │ Total bindus across all planets per sign.                                                                              │ Existing │
  ├──────────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼──────────┤
  │ Trikona Shodhana             │ "Trine purification" — subtracts shared bindus from each trine group (1-5-9, 2-6-10, etc.). Removes noise.             │ P1 / E2a │
  ├──────────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼──────────┤
  │ Ekadhipatya Shodhana         │ "Co-lordship purification" — for signs owned by same planet, applies classical rules to concentrate strength into one. │ P1 / E2a │
  ├──────────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼──────────┤
  │ Sodhya Pinda                 │ Final weighted bindu product used in longevity (ayus) calculations.                                                    │ P1 / E2a │
  └──────────────────────────────┴────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┴──────────┘

  Jaimini system (alternative Vedic framework — sign-centric not planet-centric)

  ┌──────────────────────────────┬────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┬───────────────────┐
  │             Item             │                                                                                     What it is                                                                                     │        PRD        │
  ├──────────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼───────────────────┤
  │ Chara Karakas (8)            │ "Movable significators." Planets ranked by degree within sign. Highest = Atmakaraka (soul), next = Amatyakaraka (career), etc. Changes per chart (unlike fixed Parashari karakas). │ P2 / E3           │
  ├──────────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼───────────────────┤
  │ Arudha Padas (13)            │ "Reflection points" — how each house appears to the world. AL = Arudha Lagna (public image), UL = Upapada (marriage image). A2–A12 for other houses.                               │ P2 / E3           │
  ├──────────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼───────────────────┤
  │ Rashi Drishti                │ Sign-to-sign aspects (movable signs aspect fixed, fixed aspect movable, dual aspect dual) — entirely different from planet-aspects.                                                │ P2 / E3           │
  ├──────────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼───────────────────┤
  │ Jaimini-specific yogas (~25) │ Raja yogas and Dhana yogas based on Karakamsa + Arudha positions.                                                                                                                  │ Counted in P2/E4b │
  └──────────────────────────────┴────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┴───────────────────┘

  Varshaphala / Tajaka (annual Vedic chart — the "yearly reading" tradition)

  ┌─────────────────────────┬────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┬─────────┐
  │          Item           │                                                                                                       What it is                                                                                                       │   PRD   │
  ├─────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼─────────┤
  │ Solar-return chart      │ Chart cast for the exact moment Sun returns to its natal longitude each birthday.                                                                                                                                      │ P2 / E5 │
  ├─────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼─────────┤
  │ Muntha                  │ Year-point — progresses 1 sign per year from birth Lagna. Its house + lord shape the year.                                                                                                                             │ P2 / E5 │
  ├─────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼─────────┤
  │ Varsheswara (Year Lord) │ 1 of 5 candidates wins via 11-criterion strength contest. Rules the year.                                                                                                                                              │ P2 / E5 │
  ├─────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼─────────┤
  │ Tajaka aspects          │ Different from Parashari — uses orbs (deeptamsha) per planet. Aspects are applying or separating.                                                                                                                      │ P2 / E5 │
  ├─────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼─────────┤
  │ Tajaka Yogas (16)       │ Ithasala (applying = event fulfilled), Isharaaph (separating = event missed), Nakta, Yamya, Mama, etc.                                                                                                                 │ P2 / E5 │
  ├─────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼─────────┤
  │ Sahams (50+)            │ Arabic-part-like sensitive points specific to Tajaka. Punya (virtue), Vidya (learning), Vivaha (marriage), Santana (children), Karma (work), Roga (disease), etc. Each has a formula like lon(A) − lon(B) + lagna_lon. │ P2 / E5 │
  ├─────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼─────────┤
  │ Mudda Dasa              │ Year-scale dasa within the annual chart.                                                                                                                                                                               │ P2 / E5 │
  ├─────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼─────────┤
  │ Tripathaka Chakra       │ Hourly Tajaka — daily timing.                                                                                                                                                                                          │ P2 / E5 │
  └─────────────────────────┴────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┴─────────┘

  Sarvatobhadra Chakra (omen-analysis grid)

  ┌──────────┬────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┬─────────┐
  │   Item   │                                                                                             What it is                                                                                             │   PRD   │
  ├──────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼─────────┤
  │ 9×9 grid │ Arranges 28 nakshatras (Abhijit included) + 12 rashis + letter-syllables + tithis in a specific grid. Used to check if a name/letter/event falls in a favorable row/column relative to natal Moon. │ P2 / E7 │
  └──────────┴────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┴─────────┘

  Upagrahas (sub-planets — mathematical sensitive points)

  Existing: Gulika, Mandi. Adding 9:

  ┌─────────────────────────────────────────┬──────────────────────────────────────────────────────────────────────────┬─────────┐
  │                  Item                   │                                What it is                                │   PRD   │
  ├─────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────┼─────────┤
  │ Dhuma                                   │ "Smoke" — from Sun's longitude via classical formula. Affliction marker. │ P2 / E7 │
  ├─────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────┼─────────┤
  │ Vyatipata / Pata                        │ "Descent" — Rahu's position from Dhuma. Major obstacle marker.           │ P2 / E7 │
  ├─────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────┼─────────┤
  │ Parivesha                               │ "Halo" — opposite Vyatipata. Protective/illuminating.                    │ P2 / E7 │
  ├─────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────┼─────────┤
  │ Chapa (Indra-chapa)                     │ "Rainbow" — 360° minus Parivesha. Auspicious for creativity.             │ P2 / E7 │
  ├─────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────┼─────────┤
  │ Upaketu                                 │ "Auxiliary dragon" — Sun longitude + 30° extra. Sudden-event marker.     │ P2 / E7 │
  ├─────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────┼─────────┤
  │ Kala, Mrityu, Ardhaprahara, Yamakantaka │ Planetary-hour sub-points; Mrityu is death-timing marker.                │ P2 / E7 │
  └─────────────────────────────────────────┴──────────────────────────────────────────────────────────────────────────┴─────────┘

  Both Kerala and North Indian calculation schools included (sibling rules).

  Transit intelligence

  ┌──────────────────────┬──────────────────────────────────────────────────────────────────────────────────────────────────────────────┬────────────────────┐
  │         Item         │                                                  What it is                                                  │        PRD         │
  ├──────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────┼────────────────────┤
  │ Sade Sati            │ "7.5 years of Saturn." Saturn transits 12th, 1st, 2nd from natal Moon. 3 phases. Universally feared/studied. │ P1 / E6a           │
  ├──────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────┼────────────────────┤
  │ Kantaka Shani        │ Saturn in 4th from Moon (2.5 yr affliction).                                                                 │ P1 / E6a           │
  ├──────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────┼────────────────────┤
  │ Ashtama Shani        │ Saturn in 8th from Moon (2.5 yr affliction).                                                                 │ P1 / E6a           │
  ├──────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────┼────────────────────┤
  │ Major ingress map    │ Jupiter/Saturn/Rahu/Ketu ingresses for 30 years forward, annotated with house + sign effects.                │ P1 / E6a           │
  ├──────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────┼────────────────────┤
  │ Eclipse conjunctions │ Solar + lunar eclipses + conjunction with natal points.                                                      │ P1 / E6a + P2 / E8 │
  └──────────────────────┴──────────────────────────────────────────────────────────────────────────────────────────────────────────────┴────────────────────┘

  Western depth

  ┌──────────────────────────────────────┬───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┬─────────┐
  │                 Item                 │                                                                                      What it is                                                                                       │   PRD   │
  ├──────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼─────────┤
  │ Arabic Parts / Lots (50+)            │ Sensitive points computed from planetary longitudes. Fortune (Lagna + Moon − Sun) most famous. Sect-aware: day vs night charts reverse the formula. Dorotheus/Paulus/Valens variants. │ P2 / E8 │
  ├──────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼─────────┤
  │ Fixed Stars (60+)                    │ Actual stars (Regulus, Spica, Algol, Antares…) with conjunctions to natal points within 1° orb.                                                                                       │ P2 / E8 │
  ├──────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼─────────┤
  │ Parans                               │ When a fixed star rises/culminates/sets at the same moment a planet rises/culminates/sets (Brady method).                                                                             │ P2 / E8 │
  ├──────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼─────────┤
  │ Harmonic charts (7)                  │ Multiply each longitude by N, mod 360. H5 (talents), H7 (spiritual), H9 (marriage — mirrors Navamsa), H12 (karmic), etc.                                                              │ P2 / E8 │
  ├──────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼─────────┤
  │ Eclipses (250-yr catalog)            │ Full NASA eclipse catalog, 200 yr past + 50 yr forward, Saros cycle membership.                                                                                                       │ P2 / E8 │
  ├──────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼─────────┤
  │ Uranian midpoints                    │ Halfway points between every planet pair. Used in Hamburg School for event prediction.                                                                                                │ P2 / E8 │
  ├──────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼─────────┤
  │ Reflection points, sums, differences │ Additional Uranian sensitive calculations.                                                                                                                                            │ P2 / E8 │
  ├──────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼─────────┤
  │ Hamburg School TNPs (8)              │ Hypothetical planets: Cupido, Hades, Zeus, Kronos, Apollon, Admetos, Vulkanus, Poseidon.                                                                                              │ P2 / E8 │
  ├──────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼─────────┤
  │ Planetary pictures (~200)            │ Named midpoint equations like "Sun/Moon = Venus = love."                                                                                                                              │ P2 / E8 │
  └──────────────────────────────────────┴───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┴─────────┘

  KP (Krishnamurti Paddhati) system

  ┌──────────────────────────┬──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┬─────────┐
  │           Item           │                                                    What it is                                                    │   PRD   │
  ├──────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼─────────┤
  │ 243-sub zodiac           │ Each nakshatra divided into 9 unequal subs proportional to Vimshottari periods. 27 × 9 = 243 subs around zodiac. │ P2 / E9 │
  ├──────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼─────────┤
  │ Sub-sub-sub (5 levels)   │ Recursive division. Ultra-precise event timing.                                                                  │ P2 / E9 │
  ├──────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼─────────┤
  │ Cuspal sub-lord          │ Sub-lord of each house cusp determines outcomes for that house's matters.                                        │ P2 / E9 │
  ├──────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼─────────┤
  │ Significators (5 levels) │ Hierarchical planets signifying each house.                                                                      │ P2 / E9 │
  ├──────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼─────────┤
  │ Ruling Planets           │ At any moment: day lord, ascendant lord, ascendant nakshatra lord, Moon sign lord, Moon nakshatra lord.          │ P2 / E9 │
  ├──────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼─────────┤
  │ 249-number horary        │ Client picks number 1–249 → maps to specific zodiac degree → casts horary chart.                                 │ P2 / E9 │
  └──────────────────────────┴──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┴─────────┘

  Prasna / Horary (answering a question using moment-of-asking)

  ┌────────────────────────────────────┬─────────────────────────────────────────────────────────────────────────────┬──────────┐
  │                Item                │                                 What it is                                  │   PRD    │
  ├────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────┼──────────┤
  │ Vedic Prasna (Kerala Prasna Marga) │ Arudha of Prasna lagna, Navamsa yes/no, planetary hour analysis, ~80 omens. │ P2 / E10 │
  ├────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────┼──────────┤
  │ KP Horary                          │ Cuspal sub-lord analysis of horary chart per KP rules.                      │ P2 / E10 │
  ├────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────┼──────────┤
  │ Unified yes/no engine              │ Combines 7 weighted signals across both methods → confidence-rated answer.  │ P2 / E10 │
  └────────────────────────────────────┴─────────────────────────────────────────────────────────────────────────────┴──────────┘

  Experience layer

  ┌─────────────────────────────┬──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┬───────────┐
  │            Item             │                                                    What it is                                                    │    PRD    │
  ├─────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼───────────┤
  │ AI Chat v1                  │ First LLM-powered chat using typed tools to consume all computed techniques.                                     │ P1 / E11a │
  ├─────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼───────────┤
  │ AI Chat v2 (debate / Ultra) │ Consults all 4 aggregation strategies, shows disagreement, Ultra AI ensemble mode.                               │ P2 / E11b │
  ├─────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼───────────┤
  │ Astrologer Workbench UI     │ Pro surface with all chart tabs, per-technique source selector, 5 chart styles, citation drawer, reading editor. │ P2 / E12  │
  ├─────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼───────────┤
  │ End-User UI                 │ Chat-first consumer, one-paragraph answers, progressive disclosure, 10 languages.                                │ P2 / E13  │
  └─────────────────────────────┴──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┴───────────┘

  The 3 honest gaps — no PRD yet

  ┌────────────────────────┬──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┬───────────────────────────────────┐
  │          Item          │                                                              What it is                                                              │           Where to add            │
  ├────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼───────────────────────────────────┤
  │ Asteroids / Planetoids │ Chiron, Ceres, Pallas, Juno, Vesta, Eris + major centaurs. Used in modern Western astrology for psychological themes.                │ Amend P2/E8 OR new P2/E8b         │
  ├────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼───────────────────────────────────┤
  │ Chart Rectification    │ When birth time is unknown, use known life events (marriage, death of parent, career change) to calculate back to likely birth time. │ New P2 or P3 PRD: E-rectification │
  ├────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼───────────────────────────────────┤
  │ Full Ayus Suite        │ Pindayu, Amshayu, Nisargayu, Jaimini Ayur-dasha, Ayur-harana — full classical longevity calculation system.                          │ New P2 PRD: E5b — Full Ayus       │
  └────────────────────────┴──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┴───────────────────────────────────┘

  ---
  Do we have a calculation PRD for each item?

  Yes, with three exceptions. Every item above that's assigned a PRD has a fully-specified calculation in the corresponding PRD file, including:
  - Classical source citation (BPHS chapter/verse, etc.)
  - Activation/computation algorithm
  - Edge cases
  - Test fixtures
  - Unit tests

  The three gaps (asteroids, rectification, ayus) don't have PRDs yet. If you want them, say the word and I'll write the three additional PRDs — that's 2–3 hours of additional agent work. That would bring us to 76 PRDs total and true feature-parity-plus vs Maitreya.

  Want me to:
  1. Commit the 73 PRDs as-is and tackle the 3 gaps as follow-up?
  2. Write the 3 gap PRDs first, then commit 76 PRDs as one unified set?
  3. Ignore the gaps (they're genuinely minor for now) and ship 73?