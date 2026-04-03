"""
Prediction engine — shared category-based scoring logic for all timeframes.

Analyzes natal chart, transit chart, and dasha data to produce scores and
summaries across 10 life categories.  Every prediction endpoint (daily through
yearly) funnels through `generate_predictions()`.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

BENEFICS = {"Jupiter", "Venus", "Moon", "Mercury"}
MALEFICS = {"Saturn", "Mars", "Rahu", "Ketu", "Sun"}

# Natural benefic/malefic weight used in scoring
PLANET_WEIGHT: Dict[str, float] = {
    "Jupiter": 1.5,
    "Venus": 1.3,
    "Moon": 0.8,
    "Mercury": 0.7,
    "Sun": -0.4,
    "Mars": -1.0,
    "Saturn": -1.2,
    "Rahu": -1.0,
    "Ketu": -0.8,
}

LIFE_CATEGORIES: List[Dict] = [
    {
        "name": "Career & Professional Growth",
        "slug": "career",
        "houses": [10, 6],
        "planets_key": ["Sun", "Saturn", "Jupiter"],
    },
    {
        "name": "Finance & Wealth",
        "slug": "finance",
        "houses": [2, 11],
        "planets_key": ["Jupiter", "Venus", "Mercury"],
    },
    {
        "name": "Love & Relationships",
        "slug": "love",
        "houses": [7, 5],
        "planets_key": ["Venus", "Moon", "Jupiter"],
    },
    {
        "name": "Family & Home",
        "slug": "family",
        "houses": [4],
        "planets_key": ["Moon", "Venus"],
    },
    {
        "name": "Health & Wellbeing",
        "slug": "health",
        "houses": [6, 1],
        "planets_key": ["Sun", "Mars", "Saturn"],
    },
    {
        "name": "Education & Learning",
        "slug": "education",
        "houses": [5, 4],
        "planets_key": ["Mercury", "Jupiter"],
    },
    {
        "name": "Spirituality & Inner Growth",
        "slug": "spirituality",
        "houses": [12, 9],
        "planets_key": ["Jupiter", "Ketu", "Moon"],
    },
    {
        "name": "Travel & Relocation",
        "slug": "travel",
        "houses": [3, 9, 12],
        "planets_key": ["Mercury", "Jupiter", "Rahu"],
    },
    {
        "name": "Social & Reputation",
        "slug": "social",
        "houses": [11, 1],
        "planets_key": ["Sun", "Jupiter", "Venus"],
    },
    {
        "name": "Legal & Challenges",
        "slug": "legal",
        "houses": [6, 8],
        "planets_key": ["Saturn", "Mars", "Rahu"],
    },
]

# Per-category advice templates keyed by score range (low/mid/high)
_ADVICE_TEMPLATES: Dict[str, Dict[str, str]] = {
    "career": {
        "high": "Excellent time to pursue promotions or launch new projects.",
        "mid": "Steady progress at work — stay focused on your priorities.",
        "low": "Expect obstacles in professional matters; patience is key.",
    },
    "finance": {
        "high": "Good period for investments and financial decisions.",
        "mid": "Maintain current financial plans; avoid speculative risks.",
        "low": "Exercise caution with money; delay large purchases if possible.",
    },
    "love": {
        "high": "Romance and deep connections are favored now.",
        "mid": "Relationships are stable; nurture existing bonds.",
        "low": "Misunderstandings possible — communicate openly.",
    },
    "family": {
        "high": "Harmonious family life; good for home improvements.",
        "mid": "Family matters proceed normally; stay involved.",
        "low": "Domestic tensions may arise; practice patience at home.",
    },
    "health": {
        "high": "Strong vitality — good time to start a fitness regimen.",
        "mid": "Health is stable; maintain your routines.",
        "low": "Pay extra attention to diet, sleep, and stress management.",
    },
    "education": {
        "high": "Learning and intellectual growth come easily.",
        "mid": "Steady academic progress; keep up the effort.",
        "low": "Concentration may waver — break tasks into smaller pieces.",
    },
    "spirituality": {
        "high": "Deep inner insights and meaningful spiritual experiences.",
        "mid": "Continue your practices; small gains accumulate.",
        "low": "Restless mind — grounding exercises and meditation help.",
    },
    "travel": {
        "high": "Favorable for travel and relocation decisions.",
        "mid": "Short trips are fine; postpone major moves if unsure.",
        "low": "Travel may face delays — plan with extra buffers.",
    },
    "social": {
        "high": "Public recognition and social popularity increase.",
        "mid": "Social life is balanced; attend key events.",
        "low": "Keep a low profile; avoid unnecessary conflicts.",
    },
    "legal": {
        "high": "Legal matters resolve favorably; agreements are supported.",
        "mid": "No major legal issues; stay compliant and documented.",
        "low": "Be cautious with contracts and legal disputes.",
    },
}

# Caution phrases tied to malefic transits in specific houses
_CAUTION_MAP: Dict[str, Dict[int, str]] = {
    "Saturn": {
        1: "Saturn transiting the 1st house may bring fatigue and self-doubt.",
        6: "Saturn in the 6th house demands attention to health and debts.",
        8: "Saturn in the 8th house warns of unexpected setbacks.",
    },
    "Mars": {
        1: "Mars energy in the 1st house can cause impulsiveness.",
        6: "Mars in the 6th may escalate conflicts — stay diplomatic.",
        8: "Mars in the 8th signals accident-prone energy — stay alert.",
    },
    "Rahu": {
        1: "Rahu in the 1st house may cloud judgment with illusions.",
        7: "Rahu transiting the 7th could create relationship confusion.",
        8: "Rahu in the 8th warns of hidden dangers or fraud.",
    },
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _sign_index(sign: str) -> int:
    """Return 0-based index of a zodiac sign."""
    try:
        return SIGNS.index(sign)
    except ValueError:
        return 0


def _house_from_signs(natal_sign: str, transit_sign: str) -> int:
    """Compute the house number (1-12) of a transit sign from a natal sign."""
    return ((_sign_index(transit_sign) - _sign_index(natal_sign)) % 12) + 1


def _planets_in_houses(
    natal_chart: Dict,
    transit_chart: Dict,
) -> Dict[int, List[str]]:
    """
    Map each house (1-12) to the list of transit planets occupying it,
    measured from the natal ascendant sign.
    """
    natal_asc_sign = natal_chart["ascendant"]["sign"]
    house_map: Dict[int, List[str]] = {h: [] for h in range(1, 13)}

    for planet_name, planet_data in transit_chart.get("planets", {}).items():
        transit_sign = planet_data.get("sign", "Aries")
        house = _house_from_signs(natal_asc_sign, transit_sign)
        house_map[house].append(planet_name)

    return house_map


def _dasha_lord_houses(
    natal_chart: Dict,
    dasha_lord: Optional[str],
) -> List[int]:
    """
    Return the natal house(s) ruled by the dasha lord.
    Uses a simplified sign-rulership mapping.
    """
    if not dasha_lord:
        return []

    # Standard Vedic sign rulers (traditional)
    sign_rulers: Dict[str, List[str]] = {
        "Sun": ["Leo"],
        "Moon": ["Cancer"],
        "Mars": ["Aries", "Scorpio"],
        "Mercury": ["Gemini", "Virgo"],
        "Jupiter": ["Sagittarius", "Pisces"],
        "Venus": ["Taurus", "Libra"],
        "Saturn": ["Capricorn", "Aquarius"],
        "Rahu": [],
        "Ketu": [],
    }

    ruled_signs = sign_rulers.get(dasha_lord, [])
    if not ruled_signs:
        return []

    natal_asc_sign = natal_chart["ascendant"]["sign"]
    houses = []
    for sign in ruled_signs:
        houses.append(_house_from_signs(natal_asc_sign, sign))
    return houses


def _score_category(
    category: Dict,
    house_planets: Dict[int, List[str]],
    dasha_lord: Optional[str],
    dasha_lord_natal_houses: List[int],
) -> Tuple[int, str, str, Optional[str]]:
    """
    Score a single life category (1-10) and produce summary, advice, caution.

    Scoring logic:
      - Start at 5 (neutral).
      - For each relevant house, add benefic weight / subtract malefic weight
        for planets transiting that house.
      - If the dasha lord rules one of the category's houses, boost +1.
      - Clamp to [1, 10].
    """
    cat_houses = category["houses"]
    slug = category["slug"]

    raw = 5.0  # neutral baseline

    caution_parts: List[str] = []

    for house in cat_houses:
        for planet in house_planets.get(house, []):
            weight = PLANET_WEIGHT.get(planet, 0.0)
            raw += weight

            # Collect caution text for malefic transits
            if planet in _CAUTION_MAP and house in _CAUTION_MAP[planet]:
                caution_parts.append(_CAUTION_MAP[planet][house])

    # Dasha lord bonus: if dasha lord rules a category house, +1
    if dasha_lord and dasha_lord_natal_houses:
        for house in cat_houses:
            if house in dasha_lord_natal_houses:
                raw += 1.0
                break

    # Dasha lord nature bonus/penalty
    if dasha_lord:
        if dasha_lord in BENEFICS:
            raw += 0.3
        elif dasha_lord in MALEFICS:
            raw -= 0.3

    score = max(1, min(10, round(raw)))

    # Pick advice tier
    if score >= 7:
        tier = "high"
    elif score >= 4:
        tier = "mid"
    else:
        tier = "low"

    advice = _ADVICE_TEMPLATES.get(slug, {}).get(tier, "")
    caution = "; ".join(caution_parts) if caution_parts else None

    # Build a short summary from transiting planets
    summary_parts: List[str] = []
    for house in cat_houses:
        planets = house_planets.get(house, [])
        if planets:
            plist = ", ".join(planets)
            summary_parts.append(f"{plist} transiting house {house}")
    summary = ". ".join(summary_parts) if summary_parts else "No major transiting influences."

    return score, summary, advice, caution


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def score_all_categories(
    natal_chart: Dict,
    transit_chart: Dict,
    dasha_lord: Optional[str] = None,
) -> List[Dict]:
    """
    Score all 10 life categories given a natal chart, a transit chart, and
    an optional current dasha lord.

    Returns a list of category dicts with keys:
        name, slug, houses, score, summary, details, advice, caution
    """
    house_planets = _planets_in_houses(natal_chart, transit_chart)
    dasha_natal_houses = _dasha_lord_houses(natal_chart, dasha_lord)

    results: List[Dict] = []
    for cat in LIFE_CATEGORIES:
        score, summary, advice, caution = _score_category(
            cat, house_planets, dasha_lord, dasha_natal_houses,
        )

        # Build a slightly longer "details" paragraph
        details_parts: List[str] = []
        for house in cat["houses"]:
            planets = house_planets.get(house, [])
            for p in planets:
                if p in BENEFICS:
                    details_parts.append(
                        f"{p} in house {house} supports {cat['name'].lower()}."
                    )
                elif p in MALEFICS:
                    details_parts.append(
                        f"{p} in house {house} creates challenges for {cat['name'].lower()}."
                    )
        details = " ".join(details_parts) if details_parts else (
            f"No strong planetary influences on {cat['name'].lower()} during this period."
        )

        results.append({
            "name": cat["name"],
            "slug": cat["slug"],
            "houses": cat["houses"],
            "score": score,
            "summary": summary,
            "details": details,
            "advice": advice,
            "caution": caution,
        })

    return results


def overall_score_and_summary(categories: List[Dict]) -> Tuple[int, str]:
    """Compute an overall score (1-10) and a one-line summary from category scores."""
    if not categories:
        return 5, "Insufficient data for predictions."

    avg = sum(c["score"] for c in categories) / len(categories)
    score = max(1, min(10, round(avg)))

    # Pick the top and bottom categories for the summary
    sorted_cats = sorted(categories, key=lambda c: c["score"], reverse=True)
    best = sorted_cats[0]["name"]
    weakest = sorted_cats[-1]["name"]

    if score >= 7:
        summary = f"A strongly positive period. {best} looks especially promising."
    elif score >= 4:
        summary = f"A balanced period with mixed influences. {best} is your strongest area while {weakest} needs attention."
    else:
        summary = f"A challenging period overall. Focus on mitigating difficulties in {weakest}."

    return score, summary


def get_current_dasha_lord(natal_chart: Dict) -> Optional[str]:
    """
    Extract the current Mahadasha lord from a natal chart dict.
    Returns None if dasha info is not available.
    """
    dasa = natal_chart.get("dasa")
    if not dasa:
        return None
    current = dasa.get("current")
    if not current:
        return None
    return current.get("major")


def identify_sign_changes(
    calculator,
    start_dt: datetime,
    end_dt: datetime,
    latitude: float,
    longitude: float,
    planets: Optional[List[str]] = None,
) -> List[Dict]:
    """
    Identify planets that change signs between start_dt and end_dt.
    Returns a list of dicts: {planet, from_sign, to_sign}.
    """
    start_chart = calculator.calculate_vedic_chart(start_dt, latitude, longitude)
    end_chart = calculator.calculate_vedic_chart(end_dt, latitude, longitude)

    check_planets = planets or list(start_chart.get("planets", {}).keys())
    changes: List[Dict] = []
    for p in check_planets:
        s_sign = start_chart["planets"].get(p, {}).get("sign")
        e_sign = end_chart["planets"].get(p, {}).get("sign")
        if s_sign and e_sign and s_sign != e_sign:
            changes.append({"planet": p, "from_sign": s_sign, "to_sign": e_sign})
    return changes


def aggregate_transit_charts(
    calculator,
    dates: List[datetime],
    latitude: float,
    longitude: float,
) -> Dict:
    """
    Compute transit charts for multiple dates and return a 'merged' transit
    chart that collects each planet's sign at each date.  The returned dict
    has the same shape as a single transit chart but each planet's 'sign' is
    set to the *most frequent* sign over the sample dates.
    """
    from collections import Counter

    if not dates:
        return {}

    charts = [calculator.calculate_vedic_chart(d, latitude, longitude) for d in dates]
    planet_names = list(charts[0].get("planets", {}).keys())

    merged_planets: Dict[str, Dict] = {}
    for pname in planet_names:
        signs = [c["planets"][pname]["sign"] for c in charts if pname in c.get("planets", {})]
        most_common_sign = Counter(signs).most_common(1)[0][0] if signs else "Aries"

        # Use the first chart's data as a base, override sign
        base = charts[0]["planets"].get(pname, {}).copy()
        base["sign"] = most_common_sign
        merged_planets[pname] = base

    # Return a chart-like dict
    return {
        "planets": merged_planets,
        "ascendant": charts[0].get("ascendant", {}),
    }
