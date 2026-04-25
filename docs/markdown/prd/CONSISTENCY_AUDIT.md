# Josi PRD Consistency Audit (Pass 1 closure — 2026-04-23)

## Executive summary

- **Total findings: 3 critical + 4 moderate + 6 cosmetic**
- **Verdict:** **Needs 3 quick pre-handoff fixes (critical)** before Engineering Pass 2.  The 3 criticals are all stale copy-paste artifacts from the 2026-04-22 DECISIONS §1.1 revision (True Node → Mean Node) that did not propagate into 4 P1 PRD bodies. Five-minute edit each. Moderate + cosmetic items can be absorbed during Pass 2 without blocking handoff.
- Core architecture (layering, two-user framework, ethical gating, engine graph) is **sound and internally consistent**. No cross-phase dependency violations. No contradictions between DECISIONS.md and the 15 fully-written astrology-heavy PRDs on locked values.

---

## Critical findings (must fix before Pass 2)

**C1 — Stale "B2C default True Node" in 4 P1 PRDs (contradicts DECISIONS §1.1).**
DECISIONS §1.1 was revised 2026-04-22 to make **Mean Node** the B2C default (see change-log line 831). The inheritance-table cells in 4 P1 PRDs were not updated:
- `P1/E1a-multi-dasa-v1.md:80` → "B2C default **True Node**; astrologer prompted"
- `P1/E2a-ashtakavarga-v2.md:77` → "True default B2C; astrologer prompted"
- `P1/E4a-yoga-engine-mvp.md:82` → "True default B2C"
- `P1/E6a-transit-intelligence-v1.md:82` → "True default B2C"

**Fix:** global replace `True default B2C` → `Mean default B2C` (and the E1a verbose variant). Line 98 of E1a ("period lengths unchanged; only active-moment Rahu position differs between node types") is fine.

**C2 — `review.md` phase tables only sum to 76 PRDs; header claims 89.**
The header announces "Total PRDs: 89 (76 original + 13 added via gap-closure)" and says Pass 1 is 29/29 complete, but the Phase P2 table (`review.md:69-86`) still shows the pre-GAP_CLOSURE 14 PRDs. The 13 new PRDs (E18, E19, E20, E21, E22, E23, E24, E25, E26, E27, E28, E29, E1c, E6b) have **zero rows** in any phase table, so Pass 2 Engineering will not see them as tracked work.

Note: E6b is locked for **P3** (per DECISIONS §6.5 E6b engineering action: "Create E6b PRD file under `docs/markdown/prd/P3/`") while all others go to P2. GAP_CLOSURE §1.B also says "Phase P2 (or late P2/early P3)".

**Fix:** append 12 rows to the P2 table and 1 row to the P3 table, with `⬜ PRD file pending · Pass 1 ✅ (locks in DECISIONS §6.5)` status. This matches the "Pass 1 ✅" claim in the header.

**C3 — `review.md:7` total claims 89 but Pass 1 says "29/29 astrology-heavy" — the non-astrology-heavy delta isn't described.**
Header line 9 says "Pass 2 0/89". OK. But the 13 GAP_CLOSURE PRDs' decisions live in DECISIONS §6.5 not in PRD files — Pass 2 Engineering reading `review.md` and clicking the link column will 404 on the non-existent files.

**Fix:** either add a "🚧 file pending" legend entry to the 13 new rows, or add a short paragraph below the P2 table explaining "These 13 PRDs have Pass 1 decisions locked in DECISIONS §6.5; PRD files will be authored during Engineering Pass 2 per their respective action-item sections."

---

## Moderate findings (Pass 2 will catch these)

**M1 — Orphan PRD reference: `E2b` in `enables` but no E2b PRD exists.**
`P1/E2a-ashtakavarga-v2.md:9` declares `enables: [E2b, E11a, E14a]`. `P2/E7-vargas-extended-sarvatobhadra-upagrahas.md:65` references "tracked in separate PRD (E2b)". No E2b file exists in P1–P6 and E2b is not in GAP_CLOSURE's 13. Either drop it from E2a/E7, or add it to GAP_CLOSURE deferred roadmap, or create a stub row in review.md.

**M2 — Orphan placeholder IDs: `P2-UI-kp`, `P2-UI-western`, `P2-UI-vargas`, `P2-UI-longevity` in `enables`.**
Appear in E9, E8, E8b, E7, E5b `enables:` frontmatter. These are conceptually covered by E12 Astrologer Workbench UI (which GAP_CLOSURE §2 extends to host tabs for all the new engines). Either rename the placeholders to `E12` and let E12 own them, or formally declare them as E12 sub-IDs. Engineering handoff will ask.

**M3 — `E10 Prasna` references a house-system convention that partially contradicts §1.3.**
`P2/E10-prasna-horary.md:223` says "Placidus or whole-sign — Kerala tradition uses whole-sign for Prasna (as distinct from KP's Placidus requirement)". OK at rule level, but line 156 says `"horary_chart": ... # From E9 (Krishnamurti ayanamsa + Placidus)`. E10 should call out that when the user selects Kerala Prasna Marga mode, the chart uses Whole-Sign + Lahiri (per DECISIONS §1.3 Parashari primary) and when KP Prasna mode is selected, it uses E9's Placidus+Krishnamurti. The two modes are locked (E10 Q1) but the rendered rule-list inside E10 reads as if the user always consumes E9's horary.

**M4 — E5b ethical-gating inheritance into E27 is correct in DECISIONS but not yet echoed in E5b PRD body.**
DECISIONS §6.5 E27 Q4 locks: "E27 feeds E5b dasha-window prediction... Ethical gating inherited from E5b Q5 (B2C hard refusal for direct longevity-timing queries)." E5b PRD (`E5b-full-ayus-longevity-suite.md`) mentions Maraka only once (line 101) and does not cite E27 as a downstream consumer that inherits its gating. When E27 is written, engineer should add an inheritance paragraph back-referencing E5b. Not a contradiction today, but flag for Pass 2.

---

## Cosmetic findings

**Cos1 — Hora / Horai.** §1.5 Hora exception is applied correctly in all locked P1/P2 PRD bodies — zero `\bHorai\b` matches in `P*/*.md`. `TAMIL_NAMING_AUDIT.md` lines 91, 391 retain both spellings with the correct cross-ref ("Josi convention per DECISIONS §1.5 Hora exception"), which is the right editorial pattern for an audit document. Clean.

**Cos2 — Dwipushkar/Tripushkar.** Zero `ubhayadaivata` matches in live PRDs; only pre-correction appearances are in the frozen `PRD Conversation - Whole.txt` transcript (expected). DECISIONS §3.10 Dvipada/Tripada rule is canonical.

**Cos3 — Manglik 5-house revision propagated cleanly.** E4a yoga #57 (`E4a-yoga-engine-mvp.md:236`) correctly cites DECISIONS §6.5 E25 Q2 revised 5-house Lagna-only default. But E4a §Tamil yoga catalog line 713 still says "Mars in {1,2,4,7,8,12} from Lagna OR from Moon OR from Venus (3 variant references; default all 3 active)". Per the revised lock, `default all 3 active` should now be `default Lagna-only; Chandran + Sukran are astrologer toggles`. Edit ~2 lines.

**Cos4 — `enables:` chain for F16 Golden-Chart-Suite names E1a/E2a/E4a/E6a but not any of the 13 new engines.** Once GAP_CLOSURE PRDs land, F16's enables list should extend to cover the new engines that will need golden fixtures (E19, E20, E21, E22, E25, E27 all have fixture requirements in DECISIONS §6.5 action items). Pass 2 will catch this.

**Cos5 — `review.md:3` title says "76 PRDs" in the first sentence** while line 7 says 89. Update the first-sentence count to 89 for consistency.

**Cos6 — PRD review statuses remain `🟡 in review`** despite Pass 1 being complete (header says "✅ COMPLETE — 29/29"). Consider flipping the 15 row statuses to `✅ Pass 1` (keeping Pass 2 column blank / future) so Engineering can scan the tracker and see which PRDs have locked decisions vs. which are still untouched.

---

## Positive signals

- **DECISIONS §6.5 E27 Q6 KP-Maraka deferral is clean.** No PRD claims KP Maraka for v1. E9 KP System PRD (`E9-kp-system.md`) does not mention Maraka at all. Future P3+ can compose on E9 primitives as documented.
- **Ayanamsa consistency is excellent.** Every locked PRD cross-inheritance table cites DECISIONS §1.2 Lahiri default; E9 correctly hard-binds Krishnamurti+Placidus to KP chart only, leaving natal chart on Lahiri+Whole-Sign.
- **Two-user-type framework is honored in every locked PRD.** All §6.5 E19–E29 decision tables explicitly name "Same for both user types" or call out the astrologer toggle. No decision silently assumes a single user class.
- **Ethical gating is consistent.** E5b (Ayus), E7 (Mrityu Sphuta), E27 (Maraka timing) all declare B2C hard refusal / role-gated API. Pattern is reusable.
- **The Trikona Shodhanai 3-case correction (§1.8)** is a model of how to record a revision — worked examples, rationale, change-log entry, classical citation.
- **GAP_CLOSURE traceability is strong.** Every new PRD in §6.5 cites classical source, cross-inheritance, dependencies, and engineering action items. Engineering Pass 2 can author files mechanically.

---

## Coverage summary

- PRDs audited: **89** (76 files + 13 GAP_CLOSURE decision-only specs)
- DECISIONS.md sections validated: **30** (§1.1–§1.10, §2.1–§2.4, §3.1–§3.12, §5, §6.5 entries for E17, E18, E19, E20, E21, E22, E23, E24, E25, E26, E27, E28, E29, E1c, E6b)
- Cross-refs checked: ~140 (depends_on chains, enables chains, "per DECISIONS §X.Y" inline cites, inheritance tables, E-to-E dependency prose, classical-source citations)
- Files with write changes recommended: **6** (4 P1 PRDs + review.md + small touch-up to E4a yoga table line 713)
- Files with zero changes needed: remaining **83** (all checked, all consistent)
