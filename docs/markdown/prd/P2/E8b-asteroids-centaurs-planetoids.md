---
prd_id: E8b
epic_id: E8
title: "Asteroids, Centaurs & Planetoids — Chiron, Ceres, Pallas, Juno, Vesta, Eris, Centaurs, TNOs"
phase: P2-breadth
tags: [#correctness, #extensibility, #ai-chat, #astrologer-ux]
priority: should
depends_on: [F1, F2, F6, F7, F8, F13, E1a, E8]
enables: [E14a, E12]  # 2026-04-23: P2-UI-western resolved to E12 Astrologer Workbench UI (asteroid/centaur overlays within Western tab)
classical_sources: [modern_western, brady, reinhart, zane_stein, richard_brown]
estimated_effort: 2-3 weeks
status: draft
author: "@agent"
last_updated: 2026-04-22
---

# E8b — Asteroids, Centaurs & Planetoids

## 1. Purpose & Rationale

E8 covers classical and early-modern Western depth (Lots, fixed stars, harmonics, eclipses, Uranian midpoints). It stops short of the **minor bodies** that modern Western astrology has folded into mainstream practice over the last 50 years:

1. **The "Big Four" asteroids** — Ceres, Pallas, Juno, Vesta — discovered 1801-1807; reintroduced to astrology by Eleanor Bach (1973) and Demetra George (*Asteroid Goddesses*, 1986). Every serious modern Western natal reading cites at least Ceres and Juno; many psychoanalytic practitioners regard Pallas and Vesta as the missing feminine archetypes.
2. **Chiron** — the first-discovered centaur (1977, asteroid 2060). Barbara Hand Clow (*Chiron: Rainbow Bridge*, 1987) and Melanie Reinhart (*Chiron and the Healing Journey*, 1989) established Chiron as the "wounded healer" archetype. Universally accepted in modern Western astrology.
3. **Eris** — dwarf planet, discovery 2005, responsible for Pluto's 2006 reclassification. Catalyzed a generation of discord/outer-boundary interpretations (Richard Tarnas, Keiron Le Grice). 557-year orbit; generational.
4. **Other centaurs** — Pholus (1992), Nessus (1993), Chariklo (1997), Hylonome (1995). Small but growing literature (Reinhart, Zane Stein). Generational-to-personal depending on the body.
5. **Select TNOs / dwarf planets** — Sedna (2003), Haumea (2004), Makemake (2005), Orcus (2004). Very long orbits (250-12000 years); fringe but actively researched by Henry Seltzer, Mark Andrew Holmes, Richard Brown.

Josi's Western module currently ships the 10 classical planets (Sun through Pluto) + Nodes. It does **not** support any minor bodies — a credibility gap relative to free competitors (astro.com, Astrodienst) and paid software (Solar Fire, Kepler). Without minor bodies, Josi cannot serve modern Western practitioners, cannot answer "where's my Chiron?" (the single most-requested archetypal question in Western natal consultations), and cannot feed a Western-depth AI chat.

**Critical constraint — tradition isolation:** classical Vedic astrology (Parashari, Jaimini, Tajaka) does NOT use asteroids or centaurs. Ceres-in-the-4th has no BPHS interpretation. This PRD must keep minor bodies scrupulously separate from Vedic rule sets: they default to `tradition='western'`, `source_id='modern_western'` (with Chiron/Eris carrying their own named sources), and they are never surfaced in Parashari yoga computations or Vedic aggregations.

This PRD delivers 15-20 minor bodies, each as a first-class position source with F7-conformant `structured_positions` output, full integration with E8's aspect engine at minor-body orb conventions (2-3°), and modern-aspect transit support for multi-year minor-body cycles.

## 2. Scope

### 2.1 In scope

- **Major asteroids (5):**
  - Ceres (asteroid 1; Swiss Ephemeris `SE_CERES`)
  - Pallas (asteroid 2; `SE_PALLAS`)
  - Juno (asteroid 3; `SE_JUNO`)
  - Vesta (asteroid 4; `SE_VESTA`)
  - Astraea (asteroid 5; numbered `10005` in Swiss Ephemeris extended; optional — behind flag)
- **Chiron** (centaur; `SE_CHIRON`).
- **Eris** (dwarf planet; `SE_ERIS`).
- **Additional centaurs (4):**
  - Pholus (`SE_PHOLUS`)
  - Nessus (numbered asteroid 7066; requires extended ephemeris via `swe.calc_ut(jd, 10000 + mpc_number)`)
  - Chariklo (numbered 10199)
  - Hylonome (numbered 10370)
- **Select TNOs / dwarf planets (4, behind feature flag):**
  - Sedna (numbered 90377)
  - Haumea (numbered 136108)
  - Makemake (numbered 136472)
  - Orcus (numbered 90482)
- **Position computation:** Swiss Ephemeris `swe.calc_ut(jd_ut, body_constant_or_number, flag)` with flag `SEFLG_SWIEPH | SEFLG_SPEED`. For numbered-asteroid bodies beyond the built-in constants, use `swe.calc_ut(jd_ut, 10000 + mpc_number, flag)` after registering the asteroid ephemeris file via `swe.set_jpl_file()` or `swe.set_ephe_path()` pointing to Swiss Ephemeris `seas_*.se1` / extended `ast*.se1` files.
- **Output shape:** existing F7 `structured_positions`. Each minor body contributes one entry in `positions[]` with `name`, `longitude`, `latitude`, `distance_au`, `speed_deg_per_day`, `retrograde` boolean, and `details.body_type ∈ {major_asteroid, centaur, dwarf_planet, tno}`.
- **Aspect engine integration (modern orbs):**
  - Asteroids → 2° orb for aspects to classical planets, 1° for aspects between asteroids.
  - Centaurs (Chiron, Pholus, Nessus, Chariklo, Hylonome) → 3° for hard aspects, 2° for soft aspects.
  - Eris → 3° (slow body).
  - TNOs → 2° (even slower).
  - Orbs configurable via `?orb_asteroid=`, `?orb_centaur=`, `?orb_tno=` query params.
- **Transit engine integration:** minor-body transits to natal points supported through the existing transit calculator; long-cycle bodies (Chiron 50y, Eris 557y, Sedna 11400y) flagged as "generational transits" in output metadata.
- **Rule YAMLs (minor-body interpretations, optional classical-depth):**
  - Each body gets a `src/josi/rules/western/asteroids/{source}/{body}.yaml` with archetypal summary, named after its classical source (Demetra George for Big Four, Reinhart for Chiron, etc.). These are **informational summaries**, not compute rules — they carry `output_shape_id='categorical'` and emit a single archetype category.
- **Tradition isolation:**
  - All minor-body rules registered with `tradition='western'` on their source authority.
  - Minor-body positions NEVER surface in Vedic engines (yoga, dasa, ashtakavarga, varga, tajaka).
  - A test asserts: "no minor body appears in any `technique_compute` row with `technique_family_id ∈ {yoga, dasa, ashtakavarga, jaimini, tajaka, kp, prasna, varga_extended}`."
- **API surface:**
  - `GET /api/v1/charts/{chart_id}/western/asteroids` → positions + aspects for Big Four + Chiron
  - `GET /api/v1/charts/{chart_id}/western/centaurs` → Chiron + Pholus + Nessus + Chariklo + Hylonome
  - `GET /api/v1/charts/{chart_id}/western/eris` → Eris alone (common standalone query)
  - `GET /api/v1/charts/{chart_id}/western/tnos` → Sedna + Haumea + Makemake + Orcus (behind flag)
  - `GET /api/v1/charts/{chart_id}/western/minor-bodies` → aggregate: all enabled minor bodies
  - `GET /api/v1/transits/{chart_id}/minor-bodies?from=YYYY-MM-DD&to=YYYY-MM-DD` → transit events

### 2.2 Out of scope

- **All other minor-planet ephemerides** — the MPC catalogs 1M+ bodies; we ship 15-20. Astrologers requesting additional asteroids (Juno, Pallas-Athena variants, Psyche, Sappho, Eros-asteroid distinct from Hellenistic Lot Eros) are directed to use our extensible body-registry in E8c (future).
- **Named/personal-name asteroids** (e.g., asteroid named after a person matching the native's name) — a popular-practice technique; requires MPC name→number resolution; deferred.
- **Black Moon Lilith and True Lilith** — covered in E8 Uranian module (midpoints section) or a small follow-up; not bundled here. They are computed by `swe.calc_ut(jd, swe.MEAN_APOG)` / `swe.OSCU_APOG`, not minor-body registries.
- **Apophis, Bennu, other near-Earth object newsbodies** — no interpretive tradition; omitted.
- **Classical Vedic integration** — minor bodies are NOT used in BPHS, Jaimini, Tajaka. This PRD explicitly does not add them to any Vedic engine.
- **Orb schema reform** — E8 already established modern Western orbs for classical planets; this PRD only adds per-body-type defaults without revisiting classical aspect orbs.
- **Interpretation narrative generation** — AI chat interpretation of minor-body placements belongs to E11a/F10; this PRD emits structured positions + archetype categories only.

### 2.3 Dependencies

- F1 — add `source_id`: `modern_western`, `demetra_george`, `melanie_reinhart`, `barbara_hand_clow`, `henry_seltzer`. All with `tradition='western'`.
- F2 — `technique_compute`, `aggregation_event`.
- F6 — DSL loader (archetype rules as DSL documents with `output_shape_id='categorical'`).
- F7 — `structured_positions`, `categorical`.
- F8 — aggregation protocol (minor bodies aggregate only within `tradition='western'`).
- F13 — content-hash provenance.
- E1a — natal chart primitives (chart_id resolves to natal Julian day + location).
- E8 — Western depth; this PRD extends E8's aspect engine and minor-body output shapes.
- `pyswisseph` — `swe.calc_ut()` for all minor bodies. Extended asteroid ephemeris files (`ast*.se1`) shipped under `EPHEMERIS_PATH` (approximately 300 MB if all asteroids included; we ship only the 15-20 needed).
- Swiss Ephemeris asteroid ephemeris files at `/usr/share/swisseph/ast0/` (paths `seas_18.se1`, `seas_24.se1`, etc. — standard). Verified present on container.

## 2.4 Design Decisions (Pass 1 Astrologer Review — Locked 2026-04-22)

All open questions from E8b Pass 1 astrologer review are resolved. E8b inherits most from E8 (Western tradition isolation); E8b-specific scope decisions documented here.

### Cross-cutting + E8 inheritance (applied automatically)

| Decision | Value | Ref |
|---|---|---|
| Per-technique zodiac hybrid | Tropical for minor-body natal positions (Western convention) | E8 Q1 |
| House system default | Placidus + astrologer toggle (Whole Sign / Porphyry / Koch / Equal) | E8 Q2 |
| Tradition isolation | Strict — E8b bodies NEVER merged into Vedic rule sets; tagged `tradition=modern_western`; default `source_id='modern_western'` (with Chiron/Eris carrying own named sources) | E8 §2.4 guarantee |
| Rahu/Ketu node type | Both Mean + True (Western uses same Nodes) | DECISIONS 1.1 |
| Language display | Sanskrit-IAST + Tamil phonetic for UI; Western names for bodies | DECISIONS 1.5 |

### E8b-specific decisions (locked this review)

| Decision | Value | Source |
|---|---|---|
| **Body inclusion scope (tiered)** (Q1) | **Tiered feature flags.** Tier 1 (always on): Chiron + Ceres + Pallas + Juno + Vesta (Big Five + Chiron). Tier 2 (default on): Eris + Astraea. Tier 3 (astrologer toggle): 4 centaurs (Pholus, Nessus, Chariklo, Hylonome). Tier 4 (research flag, off by default): 4 TNOs (Sedna, Haumea, Makemake, Orcus). Preserves PRD 15-body scope with user-friendly defaults. Matches Solar Fire + Kepler base + Astro.com progressive disclosure pattern. | Q1 |
| **Orb conventions for minor bodies** (Q2) | **PRD orb convention.** Asteroid → major planet: 2°. Asteroid → asteroid: 1°. Centaur → major: 3°. TNO → major: 3°. Matches Solar Fire + Kepler modern Western standard. Same for both user types. | Q2 |
| **Interpretation layer scope** (Q3) | **Canonical interpretive strings per body with single primary-authority citation.** Per-body archetype + source: Chiron/Reinhart 1989, Ceres/George 1986, Pallas/Bach 1973, Juno/George, Vesta/George, Eris/Tarnas, Astraea/modern, Pholus/Reinhart, Nessus/Stein, Chariklo/Reinhart, Hylonome/Stein, Sedna/Seltzer, Haumea/Holmes, Makemake/Brown, Orcus/emerging. Matches Solar Fire + Kepler. Same for both user types. | Q3 |
| **Astrologer-profile practice-type defaults** (Q4) | **Preset practice-type profiles + per-body override.** At profile creation, astrologer selects practice type: Hellenistic purist (all E8b tiers off) / Modern Western (Tier 1+2 on; Tier 3+4 off) / Modern Western+centaurs (Tier 1+2+3 on; Tier 4 off) / Vedic-only (Western Depth tab hidden entirely) / Modern psychological (Tier 1+2 on) / Uranian (variable — may include asteroids) / Cross-tradition generalist (Tier 1 on). Preset sets initial E8b toggles; astrologer overrides individual bodies afterward. Matches Solar Fire + Astro.com + Ernst Wilhelm convention. | Q4 |

### Swiss Ephemeris implementation notes

- **Major asteroids (5):** `swe.calc_ut(jd_ut, swe.CERES/PALLAS/JUNO/VESTA/ASTRAEA, SEFLG_SWIEPH | SEFLG_SPEED)`
- **Chiron:** `swe.calc_ut(jd_ut, swe.CHIRON, flag)`
- **Eris:** `swe.calc_ut(jd_ut, swe.ERIS, flag)`
- **Centaurs (Pholus):** `swe.calc_ut(jd_ut, swe.PHOLUS, flag)`
- **Centaurs (Nessus, Chariklo, Hylonome) + TNOs:** `swe.calc_ut(jd_ut, 10000 + mpc_number, flag)` after registering Swiss Ephemeris asteroid files via `swe.set_jpl_file()` or `swe.set_ephe_path()` pointing to `seas_*.se1` or extended `ast*.se1`
- **Output shape:** `structured_positions` with per-body entry: `name`, `longitude`, `latitude`, `distance_au`, `speed_deg_per_day`, `retrograde: bool`, `details.body_type ∈ {major_asteroid, centaur, dwarf_planet, tno}`

### Engineering action items (not astrologer-review scope)

- [ ] Swiss Eph minor-body ephemeris file integration (`ast*.se1` extended files for non-built-in numbered asteroids)
- [ ] Tiered feature-flag infrastructure (Tier 1/2/3/4 per-body enable logic)
- [ ] Astrologer practice-type preset at profile creation (6 presets: Hellenistic/Modern Western/Modern Western+centaurs/Vedic-only/Modern psychological/Uranian/Cross-tradition)
- [ ] Per-body override API (user toggles individual bodies post-preset)
- [ ] Aspect engine integration at PRD orb conventions (2° asteroid-major, 1° asteroid-asteroid, 3° centaurs, 3° TNOs)
- [ ] Interpretation string database with primary-authority citations per 15 bodies
- [ ] Strict tradition isolation enforcement (never include E8b bodies in Vedic yoga rules / Parashari aggregations)
- [ ] Retrograde + speed display (modern convention — all minor bodies can retrograde visually from Earth)
- [ ] Golden chart fixtures: 5 AA-rated astrodatabank charts with known minor-body positions cross-verified

---

## 3. Classical / Technical Research

### 3.1 The Big Four asteroid goddesses

**Primary sources:**
- Eleanor Bach, *Ephemerides of the Asteroids: Ceres, Pallas, Juno, Vesta 1900–2000* (1973) — first published astrological ephemeris; founding modern use.
- Demetra George, *Asteroid Goddesses: The Mythology, Psychology and Astrology of the Re-Emerging Feminine* (1986; 2003 revised) — canonical interpretive text.
- Lee Lehman, *The Ultimate Asteroid Book* (1988) — additional asteroids; we consult only for 5.

**Archetypal assignments (per Demetra George):**

| Body | Archetype | Swiss Ephemeris constant | Typical significations |
|---|---|---|---|
| Ceres (1) | Great Mother / Nurturance | `swe.CERES` | Grain, nurturing, loss/grief, food, child-parent bond |
| Pallas (2) | Warrior Wisdom / Strategy | `swe.PALLAS` | Intellect, visual patterning, father-daughter, creative intelligence |
| Juno (3) | Sacred Partnership | `swe.JUNO` | Marriage, equality in union, betrayal/jealousy, committed relationship |
| Vesta (4) | Sacred Flame / Focus | `swe.VESTA` | Devotion, focus, sexuality-as-sacred, solitude, priestess work |
| Astraea (5) | Justice Maiden (optional) | 10005 via extended | Justice, ethical boundaries, discernment (fringe) |

**Interpretive orb convention (Demetra George Ch. 4):** 2° for natal aspects to the 10 classical planets; 1° for aspect between two asteroids. E8b uses these as defaults; configurable.

### 3.2 Chiron

**Primary sources:**
- Zane B. Stein, *Essence and Application: A View from Chiron* (1988) — first book-length study.
- Barbara Hand Clow, *Chiron: Rainbow Bridge Between the Inner and Outer Planets* (1987).
- Melanie Reinhart, *Chiron and the Healing Journey* (1989; 2009 revised) — canonical.

**Body type:** centaur. Orbit 50.3 years, between Saturn and Uranus (but crossing Saturn's orbit). Eccentric; discovered 1977 by Charles Kowal.

**Archetype:** the "wounded healer" — trauma that cannot be cured but can be metabolized into skill and mentorship. Chiron by house = area of core wound; by aspect = agents of healing/re-injury.

**Swiss Ephemeris:** `swe.CHIRON` constant; ephemeris file `seas_18.se1`, `seas_24.se1` etc. already bundled in standard distribution. Position to arc-second accuracy from 600 BCE to 4650 CE.

**Orb convention (Reinhart Ch. 3):** 3° for hard aspects (conjunction, square, opposition); 2° for soft (sextile, trine). Stricter than classical-planet orbs because Chiron is faint and slow relative to classical planets' prominence in chart narrative.

### 3.3 Eris

**Primary sources:**
- Henry Seltzer, *The Tenth Planet: Revelations from the Astrological Eris* (2015).
- Richard Tarnas, *Cosmos and Psyche* (2006; Eris section added 2009 edition).
- Keiron Le Grice, various essays on Eris & generational astrology (2008-2015).

**Body type:** dwarf planet. Orbit 557 years. Discovered 2005 (Mike Brown et al.); caused Pluto reclassification. Named after the Greek goddess of strife.

**Archetype:** outer-system disruption; strife that forces necessary restructuring; feminine shadow. Generational: spends ~46 years per sign. Personal via house/aspect to natal points.

**Swiss Ephemeris:** `swe.ERIS` constant available in pyswisseph ≥ 2.08. Position accuracy good from 1900 onward (our use window).

**Orb convention (Seltzer Ch. 4):** 3° for all aspects given slow motion. Natal conjunctions within 3° are interpreted as "Eris touches" — rare but potent.

### 3.4 Additional centaurs (Pholus, Nessus, Chariklo, Hylonome)

**Primary sources:**
- Melanie Reinhart, *Saturn, Chiron and the Centaurs* (1997) — covers Pholus, Nessus.
- Robert von Heeren & Dieter Koch, various papers (1990s-2000s).
- Zane B. Stein, *Centaurs, Planets and Kuiper Objects* (2002).

**Pholus:** centaur asteroid 5145 (`SE_PHOLUS` constant). Orbit 92 years. Mythological Pholus opened the wine jar that brought battle — Reinhart's interpretation: "the lid comes off" — long-suppressed matter erupting.

**Nessus:** centaur asteroid 7066. Orbit 122 years. Mythological Nessus attempted to abduct Deianira — interpretation: abuse-of-power dynamics, betrayal cycles, karmic justice.

**Chariklo:** centaur asteroid 10199. Orbit 62 years. Chariklo is Chiron's wife; small but has its own rings (discovered 2013). Interpretation: healing through containment, boundaries as sacred.

**Hylonome:** centaur asteroid 10370. Orbit 128 years. Mythological Hylonome killed herself at her beloved centaur Cyllarus's death — interpretation: grief, loss of partner, despair and its transcendence.

**Swiss Ephemeris:** only `SE_PHOLUS` is a named constant. Others accessed via `swe.calc_ut(jd, 10000 + mpc_number, flag)` after ensuring `ast0/seas_*.se1` or `ast1/seas_*.se1` ephemeris files are present. pyswisseph's numbered-body convention: pass `se.SE_AST_OFFSET + mpc_number`.

**Body coverage:** 1900-2100 accurate; earlier charts degrade gracefully (longitude to 0.1°) — acceptable for astrological use; test asserts 1800-2200 range.

### 3.5 TNOs / dwarf planets (Sedna, Haumea, Makemake, Orcus)

**Primary sources:**
- Mark Andrew Holmes, essays on Sedna (2004-2012).
- Henry Seltzer, *The Tenth Planet* (Eris focus; Sedna section).
- Jeremy Neal, various online essays on Haumea and Makemake (2010s).

**Sedna:** dwarf planet 90377. Orbit ~11,400 years (!). Discovered 2003. Extremely eccentric; distant. Interpretation: depth of isolation, the feminine frozen in grief, survival at the edge.

**Haumea:** dwarf planet 136108. Orbit 283 years. Interpretation: creativity from destruction, fertility in hostile environments.

**Makemake:** dwarf planet 136472. Orbit 306 years. Interpretation: creator archetype, fertility rites.

**Orcus:** dwarf planet 90482. Orbit 247 years; similar to Pluto. Interpretation: underworld oaths, broken vows, karmic justice.

**Swiss Ephemeris:** all accessible via `swe.calc_ut(jd, SE_AST_OFFSET + mpc_number, flag)` given extended asteroid ephemeris files. Because orbits are very long, interpretations are **generational** (entire generation shares placement); only house/aspect to natal angles/luminaries is personal.

**Ship behind `enable_tnos` flag** — fringe practice; default off.

### 3.6 Swiss Ephemeris integration details

```python
import swisseph as swe

# Path setup (once, at startup):
swe.set_ephe_path("/usr/share/swisseph")

# Named constants (built-in to pyswisseph):
SE_CHIRON = swe.CHIRON    # = 15
SE_CERES  = swe.CERES     # = 17
SE_PALLAS = swe.PALLAS    # = 18
SE_JUNO   = swe.JUNO      # = 19
SE_VESTA  = swe.VESTA     # = 20
SE_ERIS   = swe.ERIS      # = 146199 (pyswisseph ≥ 2.08)
SE_PHOLUS = swe.PHOLUS    # = 16

# Numbered minor bodies (require ast*.se1 ephemeris files):
SE_AST_OFFSET = swe.AST_OFFSET  # = 10000
def minor_body_id(mpc_number: int) -> int:
    return SE_AST_OFFSET + mpc_number

NESSUS_ID    = minor_body_id(7066)
CHARIKLO_ID  = minor_body_id(10199)
HYLONOME_ID  = minor_body_id(10370)
SEDNA_ID     = minor_body_id(90377)
HAUMEA_ID    = minor_body_id(136108)
MAKEMAKE_ID  = minor_body_id(136472)
ORCUS_ID     = minor_body_id(90482)

# Core call:
flag = swe.FLG_SWIEPH | swe.FLG_SPEED
position, ret_flag = swe.calc_ut(jd_ut, body_id, flag)
# position = [longitude, latitude, distance_au, lon_speed, lat_speed, dist_speed]
```

Error handling: `swe.calc_ut` returns `ret_flag < 0` on missing ephemeris file. E8b treats this as a **soft failure** per body (log + omit from positions list) rather than aborting the request, because an ephemeris gap for one minor body shouldn't break the response.

### 3.7 Body registry data structure

```python
# src/josi/services/classical/western/minor_bodies/registry.py

MINOR_BODY_REGISTRY: list[MinorBodyDef] = [
    MinorBodyDef(
        slug="ceres",
        display_name="Ceres",
        body_type="major_asteroid",
        swe_id=swe.CERES,
        orbital_period_years=4.6,
        default_orb_degrees=2.0,
        source_id="demetra_george",
        enabled_by_default=True,
    ),
    MinorBodyDef(slug="pallas", display_name="Pallas", body_type="major_asteroid",
                 swe_id=swe.PALLAS, orbital_period_years=4.62, default_orb_degrees=2.0,
                 source_id="demetra_george", enabled_by_default=True),
    MinorBodyDef(slug="juno",   swe_id=swe.JUNO,   orbital_period_years=4.36, ...),
    MinorBodyDef(slug="vesta",  swe_id=swe.VESTA,  orbital_period_years=3.63, ...),
    MinorBodyDef(slug="chiron", body_type="centaur", swe_id=swe.CHIRON,
                 orbital_period_years=50.3, default_orb_degrees=3.0,
                 source_id="melanie_reinhart", enabled_by_default=True),
    MinorBodyDef(slug="eris",   body_type="dwarf_planet", swe_id=swe.ERIS,
                 orbital_period_years=557.0, default_orb_degrees=3.0,
                 source_id="henry_seltzer", enabled_by_default=True),
    MinorBodyDef(slug="pholus", body_type="centaur", swe_id=swe.PHOLUS,
                 orbital_period_years=92.0, default_orb_degrees=3.0,
                 source_id="melanie_reinhart", enabled_by_default=True),
    MinorBodyDef(slug="nessus", body_type="centaur",
                 swe_id=swe.AST_OFFSET + 7066,
                 orbital_period_years=122.0, default_orb_degrees=3.0,
                 source_id="melanie_reinhart", enabled_by_default=True),
    MinorBodyDef(slug="chariklo", body_type="centaur",
                 swe_id=swe.AST_OFFSET + 10199, ...),
    MinorBodyDef(slug="hylonome", body_type="centaur",
                 swe_id=swe.AST_OFFSET + 10370, ...),
    MinorBodyDef(slug="sedna",    body_type="tno",
                 swe_id=swe.AST_OFFSET + 90377,
                 orbital_period_years=11400.0, default_orb_degrees=2.0,
                 source_id="modern_western", enabled_by_default=False),  # feature flag
    MinorBodyDef(slug="haumea",   body_type="tno", swe_id=swe.AST_OFFSET + 136108, ...),
    MinorBodyDef(slug="makemake", body_type="tno", swe_id=swe.AST_OFFSET + 136472, ...),
    MinorBodyDef(slug="orcus",    body_type="tno", swe_id=swe.AST_OFFSET + 90482, ...),
    MinorBodyDef(slug="astraea",  body_type="major_asteroid",
                 swe_id=swe.AST_OFFSET + 5, ...,  enabled_by_default=False),  # optional
]
```

Registry lives in code (not DB) — the list is small, stable, code-adjacent (each body has an `swe_id` that must match a runtime call).

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| Include all asteroids in default response | No — only Big Four + Chiron | Astrologers asking for "asteroids" typically mean these 5; others opt-in |
| Include TNOs by default | No — behind `enable_tnos` flag | Fringe usage; generational motion; avoid confusing mainstream users |
| Orb for asteroid aspects | 2° (Demetra George) | Modern convention; stricter than classical planets' 8-10° |
| Orb for centaur aspects | 3° hard / 2° soft | Reinhart convention; accommodates faintness |
| Orb for TNOs | 2° | Very slow motion; tight orb |
| Include asteroids in Vedic engines | **No — hard boundary** | Classical Vedic tradition does not use them; mixing pollutes rule set |
| Include Eris in "outer planets" grouping | Optional; separate endpoint preferred | Traditional outer = Uranus/Neptune/Pluto; Eris is a "fourth outer" per Seltzer |
| Accuracy window | 1800 - 2200 for all minor bodies | Swiss Ephemeris coverage; tested |
| Missing ephemeris file handling | Soft failure per body (omit from output + log) | Better than aborting entire request |
| Which centaurs to ship | Pholus + Nessus + Chariklo + Hylonome | Most-cited in Reinhart; others (Asbolus, Chariklo's moon) out |
| Retrograde flag | Yes, in each position entry | Standard astrological need |
| Synastry with minor bodies | Supported (minor body of person A vs planet of person B) | Inherits E8 aspect engine's cross-chart support |
| Transit events for Chiron | Full support (50-year cycle; return around age 50) | Chiron Return is the most-requested transit event after Saturn Return |
| Transit events for TNOs | Supported but flagged `generational=true` | Most won't complete return in a lifetime |
| House-system dependence | Uses chart's configured house system | No special handling needed |
| Archetype rule storage | YAML under `src/josi/rules/western/asteroids/` | F6 loader picks up; archetypal category emitted |
| Per-body source attribution | Chiron → Reinhart; Big Four → Demetra George; Eris → Seltzer | Honor actual interpretive authorities |

## 5. Component Design

### 5.1 New modules

```
src/josi/services/classical/western/minor_bodies/
├── __init__.py
├── registry.py              # MinorBodyDef list + runtime registry
├── position_calculator.py   # wraps swe.calc_ut per body
├── aspect_engine.py         # minor-body aspect detection (reuses E8 aspect math)
├── transit_engine.py        # long-cycle transit events
└── archetype_rules.py       # loads YAML archetype summaries

src/josi/rules/western/asteroids/
├── demetra_george/
│   ├── ceres.yaml
│   ├── pallas.yaml
│   ├── juno.yaml
│   └── vesta.yaml
├── melanie_reinhart/
│   ├── chiron.yaml
│   ├── pholus.yaml
│   ├── nessus.yaml
│   ├── chariklo.yaml
│   └── hylonome.yaml
├── henry_seltzer/
│   └── eris.yaml
└── modern_western/
    ├── sedna.yaml
    ├── haumea.yaml
    ├── makemake.yaml
    ├── orcus.yaml
    └── astraea.yaml

src/josi/api/v1/controllers/
└── western_minor_bodies_controller.py
```

### 5.2 Data model additions

No new tables. All positions land in `technique_compute` with:
- `technique_family_id = 'western_minor_bodies'` (new; seeded in F1 additive migration)
- `output_shape_id = 'structured_positions'`
- `source_id ∈ {'modern_western', 'demetra_george', 'melanie_reinhart', 'henry_seltzer'}` — seeded in F1.

Archetype categorical rules emit `output_shape_id = 'categorical'` with the archetype as the category.

F1 seed additions (additive):

```yaml
# source_authorities.yaml — new entries
- source_id: modern_western
  display_name: "Modern Western (consensus modern practice)"
  tradition: western
  era: "modern (20th-21st c)"
  citation_system: software_reference
  default_weight: 0.75
  language: english
  notes: "Catch-all for modern practices lacking a single canonical authority."

- source_id: demetra_george
  display_name: "Demetra George — Asteroid Goddesses"
  tradition: western
  era: "1986"
  citation_system: chapter_verse
  default_weight: 0.90
  language: english
  notes: "Canonical modern asteroid interpretation (Ceres/Pallas/Juno/Vesta)."

- source_id: melanie_reinhart
  display_name: "Melanie Reinhart — Chiron and the Centaurs"
  tradition: western
  era: "1989; 1997"
  citation_system: chapter_verse
  default_weight: 0.90
  language: english

- source_id: henry_seltzer
  display_name: "Henry Seltzer — The Tenth Planet (Eris)"
  tradition: western
  era: "2015"
  citation_system: chapter_verse
  default_weight: 0.85
  language: english

# technique_families.yaml — new entry
- family_id: western_minor_bodies
  display_name: "Western Minor Bodies (asteroids, centaurs, TNOs)"
  default_output_shape_id: structured_positions
  default_aggregation_hint: D
  parent_category: western
```

Index addition:

```sql
CREATE INDEX idx_minor_bodies_compute
  ON technique_compute (chart_id, technique_family_id, computed_at DESC)
  WHERE technique_family_id = 'western_minor_bodies';
```

### 5.3 API contract

```
GET /api/v1/charts/{chart_id}/western/asteroids?orb=2.0
Response: TechniqueResult[StructuredPositions]
  positions: [
    {name: "ceres", longitude: 142.33, latitude: -1.21, distance_au: 2.77,
     speed_deg_per_day: 0.22, retrograde: false,
     details: {body_type: "major_asteroid", swe_id: 17, orbital_period_years: 4.6}},
    ... Pallas, Juno, Vesta, Chiron ...
  ]
  aspects: [
    {body_a: "ceres", body_b: "sun", aspect: "conjunction", orb: 1.4, applying: true},
    ...
  ]

GET /api/v1/charts/{chart_id}/western/centaurs
  → Chiron + Pholus + Nessus + Chariklo + Hylonome

GET /api/v1/charts/{chart_id}/western/eris
  → Eris alone

GET /api/v1/charts/{chart_id}/western/tnos                # behind feature flag
  → Sedna + Haumea + Makemake + Orcus

GET /api/v1/charts/{chart_id}/western/minor-bodies?include=ceres,pallas,chiron,eris
  → aggregate with filter; default = all enabled bodies

GET /api/v1/transits/{chart_id}/minor-bodies?from=2024-01-01&to=2030-01-01&bodies=chiron,eris
  → transit events: each body crossing each natal aspect angle within window
  Response: TechniqueResult[TemporalEvent] list
```

### 5.4 Internal Python interface

```python
# src/josi/services/classical/western/minor_bodies/position_calculator.py

class MinorBodyCalculator(ClassicalEngineBase):
    technique_family_id: str = "western_minor_bodies"
    default_output_shape_id: str = "structured_positions"

    def __init__(self, registry: MinorBodyRegistry):
        self.registry = registry

    async def compute_positions(
        self,
        chart_id: UUID,
        body_slugs: list[str] | None = None,
    ) -> StructuredPositions:
        """
        For each body in body_slugs (or all enabled defaults if None):
          - Resolve natal Julian day (UT) from chart.
          - Call swe.calc_ut(jd, body.swe_id, FLG_SWIEPH|FLG_SPEED).
          - On failure, log + omit.
          - Populate Position with longitude, latitude, distance, speed, retrograde.
        """

# src/josi/services/classical/western/minor_bodies/aspect_engine.py

class MinorBodyAspectEngine:
    def __init__(self, natal_aspect_engine: WesternAspectEngine,
                 registry: MinorBodyRegistry):
        ...

    def detect_aspects(
        self,
        natal_positions: list[Position],        # classical planets + angles
        minor_body_positions: list[Position],
        config: AspectOrbConfig,
    ) -> list[Aspect]:
        """
        For each (classical, minor) pair AND each (minor, minor) pair:
          compute |Δλ|; match against aspect angles {0, 60, 90, 120, 180};
          apply body-type orb; emit Aspect with applying/separating flag.
        """

# src/josi/services/classical/western/minor_bodies/transit_engine.py

class MinorBodyTransitEngine:
    async def transits_in_window(
        self,
        chart_id: UUID,
        from_dt: datetime,
        to_dt: datetime,
        body_slugs: list[str],
    ) -> list[TransitEvent]:
        """
        For each body × each natal point × each aspect angle:
          bracket-search for times when transit body hits angle within orb.
          Mark generational=True for bodies with period > 100y.
        """
```

## 6. User Stories

### US-E8b.1: As a modern Western astrologer, I can fetch Ceres/Pallas/Juno/Vesta positions for any chart
**Acceptance:** `GET /api/v1/charts/{chart_id}/western/asteroids` returns 4 entries (Big Four) + Chiron; positions match astro.com's ephemeris report within 0.01°.

### US-E8b.2: As a Chiron-focused practitioner, I can fetch Chiron alone with its aspects to natal points
**Acceptance:** `GET /api/v1/charts/{chart_id}/western/asteroids?include=chiron` returns only Chiron + its aspects within 3° orb to classical planets and angles.

### US-E8b.3: As an Eris-aware astrologer, I can query Eris standalone
**Acceptance:** `GET /api/v1/charts/{chart_id}/western/eris` returns Eris position + its aspects to natal Sun/Moon/Asc. For a chart born 1980s, Eris is in Aries (position within classical Aries bounds).

### US-E8b.4: As a centaur-literate astrologer, I can query the 4 additional centaurs
**Acceptance:** `GET /api/v1/charts/{chart_id}/western/centaurs` returns Chiron + Pholus + Nessus + Chariklo + Hylonome. Each entry includes `body_type='centaur'`.

### US-E8b.5: As a Vedic astrologer, minor bodies NEVER contaminate my Parashari yoga results
**Acceptance:** running `GET /api/v1/charts/{chart_id}/yogas` returns only classical 9 grahas (no Chiron); inspection of `technique_compute` rows where `technique_family_id='yoga'` shows no rule references any minor body predicate.

### US-E8b.6: As an engineer, a missing asteroid ephemeris file produces graceful degradation
**Acceptance:** simulating missing `seas_*.se1` for Chariklo: request returns 4 centaurs not 5; response metadata lists `unavailable: ['chariklo']` with reason; no 500 error.

### US-E8b.7: As an astrologer tracking my Chiron Return, I can fetch Chiron transits
**Acceptance:** `GET /api/v1/transits/{chart_id}/minor-bodies?from=2026-01-01&to=2028-01-01&bodies=chiron` returns transit events including the Chiron-conjunct-natal-Chiron event (the "Chiron Return") for charts where the native is ~49-51 years old in the window.

### US-E8b.8: As an AI chat surface, every minor-body output validates against `structured_positions`
**Acceptance:** every engine output passes `fastjsonschema.compile(structured_positions_schema)(output)`.

### US-E8b.9: As a TNO researcher, I can opt into Sedna / Haumea / Makemake / Orcus
**Acceptance:** with `enable_tnos=true` feature flag set, `GET /api/v1/charts/{chart_id}/western/tnos` returns 4 positions; with flag off, endpoint returns 404.

### US-E8b.10: As an astrologer, I can override orbs per body type
**Acceptance:** `GET /api/v1/charts/{chart_id}/western/asteroids?orb_asteroid=3.0&orb_centaur=5.0` uses custom orbs; more aspects returned than default.

## 7. Tasks

### T-E8b.1: Body registry
- **Definition:** Implement `MinorBodyDef` dataclass + `MINOR_BODY_REGISTRY` list with 15 entries. Resolve Swiss Ephemeris IDs for Big Four, Chiron, Eris, Pholus from constants; resolve Nessus/Chariklo/Hylonome/TNOs via `AST_OFFSET + mpc_number`.
- **Acceptance:** Registry loads at startup; 15 bodies enumerable; unit test asserts each has non-zero swe_id.
- **Effort:** 4 hours
- **Depends on:** F1 seed additions

### T-E8b.2: Position calculator
- **Definition:** `MinorBodyCalculator` wrapping `swe.calc_ut` with FLG_SWIEPH|FLG_SPEED; soft-fail per body on missing ephemeris.
- **Acceptance:** For 5 golden charts, computed positions match astro.com reference within 0.01° for all 15 bodies.
- **Effort:** 8 hours
- **Depends on:** T-E8b.1, Swiss Ephemeris ast*.se1 files confirmed present

### T-E8b.3: Aspect engine extension
- **Definition:** `MinorBodyAspectEngine` leveraging E8 `WesternAspectEngine` aspect math. Applies per-body-type orb defaults; supports override via config.
- **Acceptance:** 10 aspect fixtures (asteroid-to-planet, centaur-to-asteroid, etc.) match hand-computed expectations.
- **Effort:** 10 hours
- **Depends on:** T-E8b.2, E8 complete

### T-E8b.4: Transit engine extension
- **Definition:** `MinorBodyTransitEngine` bracket-searches transits in user-supplied window. Tags `generational=true` for bodies with period > 100y.
- **Acceptance:** For a chart with native age 49-51 in target window, Chiron-conjunct-natal-Chiron event returned; event dated within 30 days of astro.com's ephemeris-computed date.
- **Effort:** 12 hours
- **Depends on:** T-E8b.2

### T-E8b.5: Archetype rule YAMLs
- **Definition:** Author 15 YAMLs under `src/josi/rules/western/asteroids/{source}/{body}.yaml`. Each has archetype category (e.g., `ceres → nurturance_and_grief`) + citation + `classical_names` with body slug translations.
- **Acceptance:** All 15 load via `poetry run validate-rules`; each content_hash stable.
- **Effort:** 8 hours
- **Depends on:** F6

### T-E8b.6: F1 dim seeding additions
- **Definition:** Add 4 new `source_authority` entries + 1 new `technique_family` entry via additive YAML edit; rerun `DimensionLoader`.
- **Acceptance:** `SELECT * FROM source_authority WHERE source_id IN ('modern_western','demetra_george','melanie_reinhart','henry_seltzer')` returns 4 rows.
- **Effort:** 2 hours
- **Depends on:** F1

### T-E8b.7: API controllers + routing
- **Definition:** `western_minor_bodies_controller.py` implementing 6 endpoints (asteroids, centaurs, eris, tnos, minor-bodies aggregate, transits/minor-bodies). Register under `/api/v1`.
- **Acceptance:** OpenAPI docs show all endpoints; curl smoke test returns valid shape.
- **Effort:** 8 hours
- **Depends on:** T-E8b.2, T-E8b.3, T-E8b.4

### T-E8b.8: Tradition isolation test
- **Definition:** Integration test: for a chart computed through E4a (yoga), E1a (dasa), E2a (ashtakavarga), E3 (jaimini), E5 (tajaka), E7 (vargas), E9 (KP), E10 (prasna) — assert NO `technique_compute` row references any minor body predicate and no result payload contains minor-body body slugs.
- **Acceptance:** Test passes on full engine suite.
- **Effort:** 4 hours
- **Depends on:** T-E8b.1, E4a complete

### T-E8b.9: Feature flag for TNOs
- **Definition:** `enable_tnos` env var / settings flag; gates both the registry entries and the `/tnos` endpoint. Default false.
- **Acceptance:** With flag off, `/western/tnos` returns 404; `/western/minor-bodies` excludes TNOs. With flag on, both succeed.
- **Effort:** 2 hours

### T-E8b.10: Golden fixtures
- **Definition:** 5 natal charts × 15 bodies × position + retrograde assertion = 150 values. 5 charts × 20 aspect assertions = 100 additional. Compare to astro.com reference and Solar Fire exports where available.
- **Acceptance:** All 250 assertions green within 0.01° / aspect match.
- **Effort:** 14 hours

### T-E8b.11: Performance
- **Definition:** Benchmark: positions for 15 bodies < 100ms; aspect detection < 50ms; transit bracket-search for 10-year window < 500ms per body.
- **Acceptance:** pytest-benchmark under thresholds.
- **Effort:** 4 hours

### T-E8b.12: Documentation
- **Definition:** Update CLAUDE.md with "Minor bodies live under `src/josi/services/classical/western/minor_bodies/`". Docs explain tradition isolation (Vedic ≠ minor bodies). API docs explain orb conventions per body type.
- **Acceptance:** Merged.
- **Effort:** 3 hours

## 8. Unit Tests

### 8.1 Registry

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_registry_has_15_bodies_by_default` | registry | 15 entries (Astraea + 4 TNOs behind flags = 10 default enabled) | scope check |
| `test_registry_all_swe_ids_positive_integers` | all entries | every `swe_id > 0` | data integrity |
| `test_registry_body_types_valid` | all entries | `body_type ∈ {major_asteroid, centaur, dwarf_planet, tno}` | enum contract |
| `test_tnos_disabled_by_default` | flag off | Sedna/Haumea/Makemake/Orcus filtered from default queries | feature-flag default |
| `test_astraea_optional_by_default` | default registry | Astraea `enabled_by_default=False` | optional body |

### 8.2 Position calculator

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_ceres_1980_position` | chart 1980-06-15 12:00 UTC | Ceres longitude matches astro.com (within 0.01°) | Swiss Ephemeris parity |
| `test_chiron_1977_position_near_discovery` | chart 1977-11-01 | Chiron ~3° Taurus (matches published discovery data) | historical fixture |
| `test_eris_2005_near_discovery` | chart 2005-01-05 | Eris ~20° Aries | historical fixture |
| `test_pholus_calc_via_constant` | any chart | uses swe.PHOLUS constant | integration |
| `test_nessus_calc_via_ast_offset` | any chart | uses swe.AST_OFFSET + 7066 | numbered-body path |
| `test_missing_ephemeris_soft_fails` | mock `swe.calc_ut` to return error for Chariklo | other 14 bodies returned; Chariklo absent with metadata.unavailable=['chariklo'] | graceful degradation |
| `test_retrograde_flag_correct` | chart where Juno is retrograde (speed < 0) | Position.retrograde = True | standard flag |
| `test_speed_populated` | any chart | speed_deg_per_day in position | FLG_SPEED wired |
| `test_pre_1800_chart_accuracy_degraded` | chart 1650 | positions returned but metadata.accuracy_warning='historical' | accuracy boundary |
| `test_post_2200_chart_accuracy_degraded` | chart 2250 | same warning | symmetry |

### 8.3 Aspect engine

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_ceres_conj_sun_within_2deg` | Ceres 142°, Sun 143° | conjunction active, orb 1° | asteroid orb |
| `test_chiron_square_saturn_within_3deg` | Chiron 10° Taurus, Saturn 8° Leo | square (Δλ=88°), orb 2° (within 3°) | centaur orb |
| `test_eris_opposition_moon_3deg` | Eris 15° Aries, Moon 12° Libra | opposition, orb 3° | slow-body orb |
| `test_asteroid_asteroid_orb_stricter` | Juno 10°, Vesta 11° | conjunction with 1° orb (strict inter-asteroid) | orb policy |
| `test_orb_override_captures_wider_pairs` | `?orb_asteroid=4.0` | pair at 3.5° captured | configurability |
| `test_applying_flag_present` | slow-planet aspect | applying/separating computed from speeds | daily motion |
| `test_minor_body_to_angle_aspect` | Chiron conj natal Asc within 3° | aspect emitted | angle support |

### 8.4 Transit engine

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_chiron_return_at_age_50` | chart born 1976, query 2025-2027 | Chiron-conj-natal-Chiron event found within 50th year | canonical life cycle |
| `test_eris_generational_flagged` | Eris transit | `metadata.generational=True` | long cycle |
| `test_sedna_transit_never_returns` | chart 2000-01-01, window 10y | no Sedna Return (orbital period 11400y) | sanity |
| `test_transit_respects_orb` | Chiron 3° from exact aspect | event emitted; 4° off → not emitted | orb bound |
| `test_transit_window_empty_ok` | Chiron in 1998, window 2030-2031 | empty list (no aspects hit) | boundary |

### 8.5 Tradition isolation

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_vedic_yoga_compute_has_no_minor_body_ref` | run full yoga engine on chart | no `technique_compute` row with `technique_family_id='yoga'` references any minor body slug | hard boundary |
| `test_vedic_dasa_compute_has_no_minor_body_ref` | run Vimshottari | same assertion for `technique_family_id='dasa'` | hard boundary |
| `test_ashtakavarga_unchanged_by_minor_bodies` | run ashtakavarga before/after computing minor bodies | identical outputs | no leakage |
| `test_tajaka_unchanged_by_minor_bodies` | run Varshaphala | same | no leakage |
| `test_jaimini_unchanged_by_minor_bodies` | run Jaimini engine | same | no leakage |

### 8.6 Rule YAMLs

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_all_15_archetype_yamls_load` | `validate-rules` | all pass | F6 integration |
| `test_archetype_rule_emits_categorical_shape` | Ceres archetype rule | output_shape_id='categorical' | F7 wiring |
| `test_archetype_rule_cites_source` | Chiron rule | citation='Reinhart Ch. 3' | provenance |
| `test_archetype_rule_tradition_western` | all rules | source_authority.tradition='western' | hard boundary reinforced |

### 8.7 API

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_asteroids_endpoint_returns_5_bodies` | GET /western/asteroids | 5 entries (Big Four + Chiron) | default scope |
| `test_centaurs_endpoint_returns_5_bodies` | GET /western/centaurs | 5 (Chiron + 4 others) | default scope |
| `test_eris_endpoint_returns_1_body` | GET /western/eris | 1 | standalone |
| `test_tnos_endpoint_404_when_flag_off` | flag off | 404 | feature flag |
| `test_tnos_endpoint_returns_4_when_flag_on` | flag on | 4 | feature flag |
| `test_minor_bodies_include_filter` | ?include=ceres,chiron | 2 entries | filter |
| `test_transits_endpoint_shape` | GET /transits/.../minor-bodies | TechniqueResult[TemporalEvent] | shape contract |

### 8.8 Integration

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_minor_bodies_full_path` | 5 charts × full endpoint sweep | 5 technique_compute rows per chart (one per subdomain); all outputs F7-valid | E2E |
| `test_minor_bodies_idempotent` | double-call | 1 compute row; 2 aggregation_event rows | F2 contract |
| `test_output_shape_strict_validation` | any response | passes fastjsonschema(structured_positions) | F7 parity |
| `test_cache_hit_on_repeat_request` | 2 sequential calls | second served from cache (< 50ms) | performance |

## 9. EPIC-Level Acceptance Criteria

- [ ] 15 minor bodies (Big Four + Chiron + Eris + 4 centaurs + 4 TNOs + Astraea) registered with correct Swiss Ephemeris IDs
- [ ] `MinorBodyCalculator.compute_positions` returns F7-conforming `structured_positions`
- [ ] Body-type-specific orb conventions applied (asteroid 2°, centaur 3° hard / 2° soft, Eris 3°, TNO 2°)
- [ ] Aspect engine detects minor-body aspects to classical planets and angles
- [ ] Transit engine detects minor-body transits including Chiron Return
- [ ] Tradition isolation verified: no minor body in any Vedic engine compute row
- [ ] 15 archetype rule YAMLs under `src/josi/rules/western/asteroids/` load via F6
- [ ] 4 new `source_authority` rows + 1 new `technique_family` row seeded
- [ ] 6 API endpoints live and documented in OpenAPI
- [ ] TNOs behind `enable_tnos` feature flag (default off)
- [ ] Missing ephemeris file soft-fails per body with metadata.unavailable list
- [ ] Golden chart suite: 5 charts × (15 positions + 20 aspects) = 175 assertions green
- [ ] Unit test coverage ≥ 90% across `minor_bodies/` package
- [ ] Performance budget met per §7 T-E8b.11
- [ ] CLAUDE.md updated with minor-body section

## 10. Rollout Plan

- **Feature flags:** `enable_western_minor_bodies` (master flag; default off in P1, on in P2); `enable_tnos` (sub-flag; default off). Sub-flags allow granular rollout per body class.
- **Shadow compute:** 2-week shadow for Big Four + Chiron + Eris on all Western-mode requests; compare to astro.com ephemeris exports on 50 random charts; log to `logs/minor_bodies_shadow.log`; manually review outliers > 0.1°.
- **Backfill:** lazy (compute on first request per chart); no bulk backfill needed since storage is in `technique_compute` with idempotent inserts.
- **Rollback:** set `enable_western_minor_bodies=false`; endpoints return 501; existing `technique_compute` rows retained (no data loss); redeploy old code harmless.

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Minor-body ephemeris file missing on some Docker builds | Medium | Medium | Soft-fail per body + metadata.unavailable; Docker build copies `/usr/share/swisseph/ast*` explicitly |
| Numbered-body ID convention changes in future pyswisseph | Low | Medium | Centralize ID lookups in `registry.py`; smoke test at startup |
| Orb convention disputed by individual practitioners | Medium | Low | Fully configurable via query param; document defaults |
| Accidental leak into Vedic engines | Medium | **High** (pollutes classical correctness) | Explicit tradition-isolation test in §8.5; CI blocks merge if it fails |
| Eris pre-1900 positions inaccurate | Low | Low | Accuracy warning in metadata; Eris discovered 2005 anyway |
| TNO interpretations fringe / reputation risk | Medium | Low | Behind feature flag; never default; clearly marked experimental |
| Chiron orb disputed (3° vs 5°) | Medium | Low | Configurable; default Reinhart 3° |
| Performance degradation with 15 bodies × 10 planets aspect matrix | Low | Medium | 150 pair comparisons ≪ 1ms; no concern |
| Asteroid name collisions (Juno asteroid vs Juno-as-archetype-in-another-tradition) | Low | Low | All minor-body slugs are namespaced under `western_minor_bodies` family |
| Long-period TNO positions degrade for historical charts | Medium | Low | Accuracy window 1800-2200 documented; metadata flag warns |
| Swiss Ephemeris `SE_ERIS` constant unavailable in older pyswisseph | Low | Medium | Pyproject pins pyswisseph ≥ 2.08; startup check asserts constant present |
| Generational body transits overwhelm transit endpoint | Low | Low | Metadata.generational flag filters in UI; default response excludes if window > 200y |

## 12. References

- Master spec: [`docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`](../../../superpowers/specs/2026-04-19-classical-techniques-expansion-design.md) §2.2 (Western families)
- F1 dims: [`../P0/F1-star-schema-dimensions.md`](../P0/F1-star-schema-dimensions.md)
- F2 fact tables: [`../P0/F2-fact-tables.md`](../P0/F2-fact-tables.md)
- F6 Rule DSL: [`../P0/F6-rule-dsl-yaml-loader.md`](../P0/F6-rule-dsl-yaml-loader.md)
- F7 Output shapes: [`../P0/F7-output-shape-system.md`](../P0/F7-output-shape-system.md)
- F8 Aggregation: [`../P0/F8-technique-result-aggregation-protocol.md`](../P0/F8-technique-result-aggregation-protocol.md)
- E8 Western depth: [`./E8-western-depth.md`](./E8-western-depth.md)
- E1a Multi-Dasa v1: (natal primitives)
- **Classical / modern sources:**
  - Eleanor Bach, *Ephemerides of the Asteroids: Ceres, Pallas, Juno, Vesta 1900–2000*, 1973
  - Demetra George, *Asteroid Goddesses: The Mythology, Psychology and Astrology of the Re-Emerging Feminine*, 1986 (rev. 2003)
  - Melanie Reinhart, *Chiron and the Healing Journey*, 1989 (rev. 2009)
  - Melanie Reinhart, *Saturn, Chiron and the Centaurs*, 1997
  - Zane B. Stein, *Essence and Application: A View from Chiron*, 1988
  - Zane B. Stein, *Centaurs, Planets and Kuiper Objects*, 2002
  - Barbara Hand Clow, *Chiron: Rainbow Bridge Between the Inner and Outer Planets*, 1987
  - Henry Seltzer, *The Tenth Planet: Revelations from the Astrological Eris*, 2015
  - Richard Tarnas, *Cosmos and Psyche*, 2006 (rev. 2009 includes Eris)
  - Lee Lehman, *The Ultimate Asteroid Book*, 1988
- **Astronomical references:**
  - Minor Planet Center (MPC) designations for numbered asteroids
  - Swiss Ephemeris documentation: https://www.astro.com/swisseph/swephprg.htm (asteroids & minor bodies section)
- Reference implementations:
  - astro.com (Swiss Ephemeris) — ephemeris parity target for all 15 bodies
  - Solar Fire (commercial) — asteroid selection + interpretation
  - Kepler (Cosmic Patterns) — centaur & TNO support
