"""
Interpretation engine for generating astrological interpretations.
Uses rule-based system with potential for ML enhancement.
"""
from typing import Dict, List, Any, Optional
import json


class InterpretationEngine:
    """Generate interpretations for astrological charts."""
    
    def __init__(self):
        # Initialize interpretation rules
        self.planet_meanings = self._load_planet_meanings()
        self.sign_meanings = self._load_sign_meanings()
        self.house_meanings = self._load_house_meanings()
        self.aspect_meanings = self._load_aspect_meanings()
    
    def generate_interpretations(
        self,
        chart_data: Dict[str, Any],
        chart_type: str
    ) -> Dict[str, Dict]:
        """Generate multiple interpretation types for a chart."""
        interpretations = {}
        
        # General overview
        interpretations["general"] = self._generate_general_interpretation(
            chart_data, chart_type
        )
        
        # Personality analysis
        interpretations["personality"] = self._generate_personality_interpretation(
            chart_data, chart_type
        )
        
        # Career insights
        interpretations["career"] = self._generate_career_interpretation(
            chart_data, chart_type
        )
        
        # Relationship patterns
        interpretations["relationships"] = self._generate_relationship_interpretation(
            chart_data, chart_type
        )
        
        # Life purpose
        interpretations["life_purpose"] = self._generate_life_purpose_interpretation(
            chart_data, chart_type
        )
        
        return interpretations
    
    def generate_interpretation(
        self,
        chart_data: Dict[str, Any],
        chart_type: str,
        interpretation_type: str,
        language: str = "en"
    ) -> Dict[str, Any]:
        """Generate specific type of interpretation."""
        
        generators = {
            "general": self._generate_general_interpretation,
            "personality": self._generate_personality_interpretation,
            "career": self._generate_career_interpretation,
            "relationships": self._generate_relationship_interpretation,
            "health": self._generate_health_interpretation,
            "spiritual": self._generate_spiritual_interpretation,
            "life_purpose": self._generate_life_purpose_interpretation,
            "current_transits": self._generate_transit_interpretation
        }
        
        generator = generators.get(
            interpretation_type,
            self._generate_general_interpretation
        )
        
        return generator(chart_data, chart_type)
    
    def _generate_general_interpretation(
        self,
        chart_data: Dict[str, Any],
        chart_type: str
    ) -> Dict[str, Any]:
        """Generate general chart overview."""
        planets = chart_data.get("planets", {})
        ascendant = chart_data.get("ascendant", {})
        
        # Build interpretation
        key_points = []
        
        # Sun sign interpretation
        if "Sun" in planets:
            sun_sign = planets["Sun"].get("sign", "Unknown")
            key_points.append(
                f"Sun in {sun_sign}: {self.sign_meanings.get(sun_sign, {}).get('core', '')}"
            )
        
        # Moon sign interpretation
        if "Moon" in planets:
            moon_sign = planets["Moon"].get("sign", "Unknown")
            key_points.append(
                f"Moon in {moon_sign}: {self.sign_meanings.get(moon_sign, {}).get('emotional', '')}"
            )
        
        # Ascendant interpretation
        if ascendant:
            asc_sign = ascendant.get("sign", "Unknown")
            key_points.append(
                f"Ascendant in {asc_sign}: {self.sign_meanings.get(asc_sign, {}).get('appearance', '')}"
            )
        
        # Dominant elements
        element_analysis = self._analyze_elements(planets)
        if element_analysis:
            dominant = element_analysis.get("dominant", "balanced")
            key_points.append(f"Dominant element: {dominant}")
        
        summary = f"This {chart_type} chart shows a complex personality with " + \
                 f"multiple dimensions. " + " ".join(key_points[:3])
        
        return {
            "title": "General Chart Overview",
            "summary": summary,
            "details": {
                "key_points": key_points,
                "element_balance": element_analysis,
                "chart_pattern": self._identify_chart_pattern(planets),
                "prominent_features": self._find_prominent_features(chart_data)
            },
            "confidence": 0.85
        }
    
    def _generate_personality_interpretation(
        self,
        chart_data: Dict[str, Any],
        chart_type: str
    ) -> Dict[str, Any]:
        """Generate personality analysis."""
        planets = chart_data.get("planets", {})
        aspects = chart_data.get("aspects", [])
        
        traits = []
        
        # Sun-based traits
        if "Sun" in planets:
            sun_data = planets["Sun"]
            sun_sign = sun_data.get("sign", "")
            sun_house = sun_data.get("house", 1)
            
            traits.append({
                "category": "Core Identity",
                "description": f"Sun in {sun_sign} in house {sun_house}",
                "traits": self._get_sun_traits(sun_sign, sun_house)
            })
        
        # Moon-based traits
        if "Moon" in planets:
            moon_data = planets["Moon"]
            moon_sign = moon_data.get("sign", "")
            moon_house = moon_data.get("house", 1)
            
            traits.append({
                "category": "Emotional Nature",
                "description": f"Moon in {moon_sign} in house {moon_house}",
                "traits": self._get_moon_traits(moon_sign, moon_house)
            })
        
        # Mercury-based traits
        if "Mercury" in planets:
            mercury_data = planets["Mercury"]
            mercury_sign = mercury_data.get("sign", "")
            
            traits.append({
                "category": "Communication Style",
                "description": f"Mercury in {mercury_sign}",
                "traits": self._get_mercury_traits(mercury_sign)
            })
        
        # Aspect-based modifications
        personality_aspects = self._get_personality_aspects(aspects)
        
        summary = "Your personality is characterized by " + \
                 f"{', '.join([t['category'].lower() for t in traits[:2]])}. "
        
        return {
            "title": "Personality Analysis",
            "summary": summary,
            "details": {
                "core_traits": traits,
                "aspect_influences": personality_aspects,
                "strengths": self._identify_strengths(planets, aspects),
                "challenges": self._identify_challenges(planets, aspects),
                "growth_areas": self._suggest_growth_areas(planets, aspects)
            },
            "confidence": 0.82
        }
    
    def _generate_career_interpretation(
        self,
        chart_data: Dict[str, Any],
        chart_type: str
    ) -> Dict[str, Any]:
        """Generate career and vocation interpretation."""
        planets = chart_data.get("planets", {})
        houses = chart_data.get("houses", [])
        
        career_indicators = []
        
        # 10th house analysis (career)
        tenth_house_planets = [p for p, data in planets.items() if data.get("house") == 10]
        if tenth_house_planets:
            career_indicators.append({
                "factor": "10th House Planets",
                "planets": tenth_house_planets,
                "interpretation": f"Strong career focus with {', '.join(tenth_house_planets)}"
            })
        
        # MC (Midheaven) ruler
        if len(houses) >= 10:
            mc_sign = self._get_sign_from_degree(houses[9])
            mc_ruler = self._get_sign_ruler(mc_sign)
            if mc_ruler in planets:
                ruler_house = planets[mc_ruler].get("house", 1)
                career_indicators.append({
                    "factor": "MC Ruler",
                    "interpretation": f"{mc_ruler} rules career, placed in house {ruler_house}"
                })
        
        # 6th house analysis (work environment)
        sixth_house_planets = [p for p, data in planets.items() if data.get("house") == 6]
        
        # 2nd house analysis (income)
        second_house_planets = [p for p, data in planets.items() if data.get("house") == 2]
        
        # Saturn placement (career lessons)
        if "Saturn" in planets:
            saturn_sign = planets["Saturn"].get("sign", "")
            saturn_house = planets["Saturn"].get("house", 1)
            career_indicators.append({
                "factor": "Saturn Placement",
                "interpretation": f"Career mastery through {saturn_sign} in house {saturn_house}"
            })
        
        suitable_careers = self._suggest_careers(planets, career_indicators)
        
        summary = "Your career path is influenced by " + \
                 f"{career_indicators[0]['factor'] if career_indicators else 'multiple factors'}. "
        
        return {
            "title": "Career & Vocation",
            "summary": summary,
            "details": {
                "career_indicators": career_indicators,
                "suitable_careers": suitable_careers,
                "work_style": self._analyze_work_style(planets),
                "success_timing": self._predict_career_timing(chart_data),
                "financial_potential": self._analyze_financial_potential(planets, houses)
            },
            "confidence": 0.78
        }
    
    def _generate_relationship_interpretation(
        self,
        chart_data: Dict[str, Any],
        chart_type: str
    ) -> Dict[str, Any]:
        """Generate relationship pattern interpretation."""
        planets = chart_data.get("planets", {})
        aspects = chart_data.get("aspects", [])
        
        relationship_factors = []
        
        # Venus analysis (love nature)
        if "Venus" in planets:
            venus_sign = planets["Venus"].get("sign", "")
            venus_house = planets["Venus"].get("house", 1)
            relationship_factors.append({
                "planet": "Venus",
                "interpretation": f"Love nature: {self._get_venus_love_style(venus_sign)}"
            })
        
        # Mars analysis (passion/desire)
        if "Mars" in planets:
            mars_sign = planets["Mars"].get("sign", "")
            relationship_factors.append({
                "planet": "Mars",
                "interpretation": f"Passion style: {self._get_mars_passion_style(mars_sign)}"
            })
        
        # 7th house analysis (partnerships)
        seventh_house_planets = [p for p, data in planets.items() if data.get("house") == 7]
        if seventh_house_planets:
            relationship_factors.append({
                "factor": "7th House",
                "interpretation": f"Partnership focus: {', '.join(seventh_house_planets)}"
            })
        
        # 5th house analysis (romance)
        fifth_house_planets = [p for p, data in planets.items() if data.get("house") == 5]
        
        # Venus-Mars aspects
        venus_mars_aspects = [
            a for a in aspects 
            if ("Venus" in [a.get("planet1"), a.get("planet2")] and 
                "Mars" in [a.get("planet1"), a.get("planet2")])
        ]
        
        relationship_patterns = self._analyze_relationship_patterns(
            planets, aspects, relationship_factors
        )
        
        summary = "Your relationship style is characterized by " + \
                 f"{relationship_factors[0]['interpretation'] if relationship_factors else 'complexity'}. "
        
        return {
            "title": "Relationship Patterns",
            "summary": summary,
            "details": {
                "love_nature": relationship_factors,
                "relationship_patterns": relationship_patterns,
                "ideal_partner": self._describe_ideal_partner(planets, aspects),
                "relationship_lessons": self._identify_relationship_lessons(planets, aspects),
                "compatibility_factors": self._list_compatibility_factors(planets)
            },
            "confidence": 0.80
        }
    
    def _generate_health_interpretation(
        self,
        chart_data: Dict[str, Any],
        chart_type: str
    ) -> Dict[str, Any]:
        """Generate health and vitality interpretation."""
        planets = chart_data.get("planets", {})
        
        health_indicators = []
        
        # 6th house (health)
        sixth_house = [p for p, data in planets.items() if data.get("house") == 6]
        
        # Sun vitality
        if "Sun" in planets:
            sun_sign = planets["Sun"].get("sign", "")
            health_indicators.append({
                "factor": "Sun Sign",
                "area": self._get_sign_body_rulership(sun_sign),
                "advice": f"Focus on {sun_sign} health themes"
            })
        
        # Moon emotional health
        if "Moon" in planets:
            moon_sign = planets["Moon"].get("sign", "")
            health_indicators.append({
                "factor": "Moon Sign",
                "area": "Emotional well-being",
                "advice": f"Nurture through {moon_sign} activities"
            })
        
        return {
            "title": "Health & Vitality",
            "summary": "Your health constitution shows...",
            "details": {
                "health_indicators": health_indicators,
                "vulnerable_areas": self._identify_health_vulnerabilities(planets),
                "wellness_advice": self._generate_wellness_advice(planets)
            },
            "confidence": 0.75
        }
    
    def _generate_spiritual_interpretation(
        self,
        chart_data: Dict[str, Any],
        chart_type: str
    ) -> Dict[str, Any]:
        """Generate spiritual and growth interpretation."""
        planets = chart_data.get("planets", {})
        
        spiritual_indicators = []
        
        # 9th house (higher wisdom)
        ninth_house = [p for p, data in planets.items() if data.get("house") == 9]
        
        # 12th house (transcendence)
        twelfth_house = [p for p, data in planets.items() if data.get("house") == 12]
        
        # Neptune placement
        if "Neptune" in planets:
            neptune_sign = planets["Neptune"].get("sign", "")
            neptune_house = planets["Neptune"].get("house", 1)
            spiritual_indicators.append({
                "planet": "Neptune",
                "interpretation": f"Spiritual connection through {neptune_sign}"
            })
        
        # Jupiter wisdom
        if "Jupiter" in planets:
            jupiter_sign = planets["Jupiter"].get("sign", "")
            spiritual_indicators.append({
                "planet": "Jupiter",
                "interpretation": f"Wisdom seeking through {jupiter_sign}"
            })
        
        return {
            "title": "Spiritual Path",
            "summary": "Your spiritual journey involves...",
            "details": {
                "spiritual_indicators": spiritual_indicators,
                "growth_path": self._identify_spiritual_path(planets),
                "karmic_lessons": self._identify_karmic_patterns(planets)
            },
            "confidence": 0.77
        }
    
    def _generate_life_purpose_interpretation(
        self,
        chart_data: Dict[str, Any],
        chart_type: str
    ) -> Dict[str, Any]:
        """Generate life purpose and destiny interpretation."""
        planets = chart_data.get("planets", {})
        
        # North Node (life purpose)
        purpose_indicators = []
        
        if "NorthNode" in planets:
            nn_sign = planets["NorthNode"].get("sign", "")
            nn_house = planets["NorthNode"].get("house", 1)
            purpose_indicators.append({
                "factor": "North Node",
                "interpretation": f"Life purpose through {nn_sign} in house {nn_house}"
            })
        
        # Sun's purpose
        if "Sun" in planets:
            sun_sign = planets["Sun"].get("sign", "")
            sun_house = planets["Sun"].get("house", 1)
            purpose_indicators.append({
                "factor": "Sun",
                "interpretation": f"Self-realization through {sun_sign} themes"
            })
        
        return {
            "title": "Life Purpose",
            "summary": "Your life purpose centers on...",
            "details": {
                "purpose_indicators": purpose_indicators,
                "soul_mission": self._describe_soul_mission(planets),
                "life_themes": self._identify_life_themes(planets),
                "evolutionary_path": self._describe_evolutionary_path(planets)
            },
            "confidence": 0.76
        }
    
    def _generate_transit_interpretation(
        self,
        chart_data: Dict[str, Any],
        chart_type: str
    ) -> Dict[str, Any]:
        """Generate current transit interpretation."""
        # This would compare current positions to natal
        return {
            "title": "Current Transits",
            "summary": "Current planetary influences suggest...",
            "details": {
                "major_transits": [],
                "opportunities": [],
                "challenges": []
            },
            "confidence": 0.73
        }
    
    # Helper methods
    
    def _load_planet_meanings(self) -> Dict:
        """Load planet meaning database."""
        return {
            "Sun": {
                "keywords": ["identity", "ego", "vitality", "purpose"],
                "positive": ["confident", "creative", "generous"],
                "negative": ["arrogant", "domineering", "self-centered"]
            },
            "Moon": {
                "keywords": ["emotions", "instincts", "habits", "mother"],
                "positive": ["nurturing", "intuitive", "responsive"],
                "negative": ["moody", "clingy", "oversensitive"]
            },
            "Mercury": {
                "keywords": ["communication", "thinking", "learning"],
                "positive": ["intelligent", "adaptable", "witty"],
                "negative": ["nervous", "superficial", "gossipy"]
            },
            "Venus": {
                "keywords": ["love", "beauty", "values", "pleasure"],
                "positive": ["harmonious", "artistic", "affectionate"],
                "negative": ["indulgent", "vain", "lazy"]
            },
            "Mars": {
                "keywords": ["action", "desire", "energy", "conflict"],
                "positive": ["courageous", "assertive", "passionate"],
                "negative": ["aggressive", "impulsive", "angry"]
            },
            "Jupiter": {
                "keywords": ["expansion", "wisdom", "luck", "growth"],
                "positive": ["optimistic", "generous", "philosophical"],
                "negative": ["excessive", "overconfident", "wasteful"]
            },
            "Saturn": {
                "keywords": ["discipline", "responsibility", "limits"],
                "positive": ["disciplined", "patient", "wise"],
                "negative": ["pessimistic", "rigid", "fearful"]
            }
        }
    
    def _load_sign_meanings(self) -> Dict:
        """Load zodiac sign meanings."""
        return {
            "Aries": {
                "element": "Fire",
                "quality": "Cardinal",
                "ruler": "Mars",
                "keywords": ["pioneering", "independent", "courageous"],
                "core": "Natural leader with pioneering spirit",
                "emotional": "Direct and spontaneous emotional expression",
                "appearance": "Dynamic and assertive presence"
            },
            "Taurus": {
                "element": "Earth",
                "quality": "Fixed",
                "ruler": "Venus",
                "keywords": ["stable", "sensual", "persistent"],
                "core": "Grounded and values material security",
                "emotional": "Steady and loyal emotional nature",
                "appearance": "Calm and graceful demeanor"
            },
            "Gemini": {
                "element": "Air",
                "quality": "Mutable",
                "ruler": "Mercury",
                "keywords": ["communicative", "versatile", "curious"],
                "core": "Intellectual and adaptable communicator",
                "emotional": "Changeable and mentally oriented emotions",
                "appearance": "Youthful and animated expression"
            },
            "Cancer": {
                "element": "Water",
                "quality": "Cardinal",
                "ruler": "Moon",
                "keywords": ["nurturing", "sensitive", "protective"],
                "core": "Emotionally attuned caregiver",
                "emotional": "Deep and nurturing emotional nature",
                "appearance": "Soft and approachable presence"
            },
            "Leo": {
                "element": "Fire",
                "quality": "Fixed",
                "ruler": "Sun",
                "keywords": ["creative", "confident", "generous"],
                "core": "Natural performer seeking recognition",
                "emotional": "Warm and dramatic emotional expression",
                "appearance": "Regal and commanding presence"
            },
            "Virgo": {
                "element": "Earth",
                "quality": "Mutable",
                "ruler": "Mercury",
                "keywords": ["analytical", "helpful", "perfectionist"],
                "core": "Practical analyzer seeking perfection",
                "emotional": "Reserved but deeply caring",
                "appearance": "Neat and understated elegance"
            },
            "Libra": {
                "element": "Air",
                "quality": "Cardinal",
                "ruler": "Venus",
                "keywords": ["diplomatic", "harmonious", "social"],
                "core": "Natural mediator seeking balance",
                "emotional": "Harmonious and partnership-oriented",
                "appearance": "Graceful and aesthetically pleasing"
            },
            "Scorpio": {
                "element": "Water",
                "quality": "Fixed",
                "ruler": "Pluto/Mars",
                "keywords": ["intense", "transformative", "mysterious"],
                "core": "Deep transformer seeking truth",
                "emotional": "Intense and transformative emotions",
                "appearance": "Magnetic and mysterious presence"
            },
            "Sagittarius": {
                "element": "Fire",
                "quality": "Mutable",
                "ruler": "Jupiter",
                "keywords": ["adventurous", "philosophical", "optimistic"],
                "core": "Truth-seeking adventurer",
                "emotional": "Optimistic and freedom-loving",
                "appearance": "Open and enthusiastic demeanor"
            },
            "Capricorn": {
                "element": "Earth",
                "quality": "Cardinal",
                "ruler": "Saturn",
                "keywords": ["ambitious", "disciplined", "traditional"],
                "core": "Ambitious achiever building legacy",
                "emotional": "Controlled and responsible emotions",
                "appearance": "Professional and authoritative"
            },
            "Aquarius": {
                "element": "Air",
                "quality": "Fixed",
                "ruler": "Uranus/Saturn",
                "keywords": ["innovative", "humanitarian", "independent"],
                "core": "Progressive thinker and humanitarian",
                "emotional": "Detached but friendly emotional style",
                "appearance": "Unique and unconventional presence"
            },
            "Pisces": {
                "element": "Water",
                "quality": "Mutable",
                "ruler": "Neptune/Jupiter",
                "keywords": ["compassionate", "imaginative", "spiritual"],
                "core": "Mystical dreamer and healer",
                "emotional": "Empathetic and boundless emotions",
                "appearance": "Gentle and ethereal quality"
            }
        }
    
    def _load_house_meanings(self) -> Dict:
        """Load house meanings."""
        return {
            1: {"area": "Self, identity, appearance", "keywords": ["personality", "first impressions"]},
            2: {"area": "Resources, values, possessions", "keywords": ["money", "self-worth"]},
            3: {"area": "Communication, siblings, short trips", "keywords": ["learning", "neighbors"]},
            4: {"area": "Home, family, roots", "keywords": ["foundation", "private life"]},
            5: {"area": "Creativity, romance, children", "keywords": ["fun", "self-expression"]},
            6: {"area": "Health, work, service", "keywords": ["routine", "wellness"]},
            7: {"area": "Partnerships, relationships", "keywords": ["marriage", "contracts"]},
            8: {"area": "Transformation, shared resources", "keywords": ["death/rebirth", "intimacy"]},
            9: {"area": "Philosophy, travel, higher learning", "keywords": ["wisdom", "expansion"]},
            10: {"area": "Career, reputation, public life", "keywords": ["achievement", "status"]},
            11: {"area": "Friends, groups, hopes", "keywords": ["community", "ideals"]},
            12: {"area": "Spirituality, hidden things", "keywords": ["transcendence", "sacrifice"]}
        }
    
    def _load_aspect_meanings(self) -> Dict:
        """Load aspect interpretations."""
        return {
            "conjunction": {
                "nature": "fusion",
                "keywords": ["blend", "intensify", "unite"],
                "interpretation": "Energies merge and amplify each other"
            },
            "sextile": {
                "nature": "opportunity",
                "keywords": ["harmony", "talent", "ease"],
                "interpretation": "Natural talents that can be developed"
            },
            "square": {
                "nature": "challenge",
                "keywords": ["tension", "growth", "conflict"],
                "interpretation": "Dynamic tension requiring integration"
            },
            "trine": {
                "nature": "flow",
                "keywords": ["harmony", "gift", "ease"],
                "interpretation": "Natural flow and harmony between energies"
            },
            "opposition": {
                "nature": "awareness",
                "keywords": ["balance", "projection", "relationship"],
                "interpretation": "Need for balance and integration of opposites"
            }
        }
    
    def _analyze_elements(self, planets: Dict) -> Dict:
        """Analyze elemental balance in chart."""
        elements = {"Fire": 0, "Earth": 0, "Air": 0, "Water": 0}
        
        for planet, data in planets.items():
            sign = data.get("sign", "")
            sign_data = self.sign_meanings.get(sign, {})
            element = sign_data.get("element", "")
            if element:
                elements[element] += 1
        
        total = sum(elements.values())
        if total > 0:
            percentages = {e: (c/total)*100 for e, c in elements.items()}
            dominant = max(elements.items(), key=lambda x: x[1])[0]
            
            return {
                "counts": elements,
                "percentages": percentages,
                "dominant": dominant,
                "lacking": [e for e, c in elements.items() if c == 0]
            }
        
        return {}
    
    def _identify_chart_pattern(self, planets: Dict) -> str:
        """Identify major chart pattern if present."""
        # Simplified pattern recognition
        # In practice, would check for:
        # - Grand Trine, T-Square, Grand Cross
        # - Yod, Mystic Rectangle, Kite
        # - Bundle, Bowl, Bucket patterns
        
        planet_count = len(planets)
        if planet_count >= 7:
            # Check distribution across signs/houses
            signs = [p.get("sign") for p in planets.values()]
            unique_signs = len(set(signs))
            
            if unique_signs <= 4:
                return "Bundle pattern - focused energy"
            elif unique_signs <= 6:
                return "Bowl pattern - seeking fulfillment"
            else:
                return "Splash pattern - diverse interests"
        
        return "Mixed pattern"
    
    def _find_prominent_features(self, chart_data: Dict) -> List[str]:
        """Find prominent features in chart."""
        features = []
        
        planets = chart_data.get("planets", {})
        aspects = chart_data.get("aspects", [])
        
        # Angular planets
        angular_planets = [
            p for p, data in planets.items() 
            if data.get("house") in [1, 4, 7, 10]
        ]
        if angular_planets:
            features.append(f"Angular planets: {', '.join(angular_planets)}")
        
        # Retrograde planets
        retrograde = [
            p for p, data in planets.items() 
            if data.get("is_retrograde", False)
        ]
        if retrograde:
            features.append(f"Retrograde planets: {', '.join(retrograde)}")
        
        # Major aspect patterns
        if len(aspects) > 10:
            features.append("Highly aspected chart")
        
        return features
    
    def _get_sun_traits(self, sign: str, house: int) -> List[str]:
        """Get personality traits based on Sun placement."""
        sign_traits = self.sign_meanings.get(sign, {}).get("keywords", [])
        house_traits = self.house_meanings.get(house, {}).get("keywords", [])
        
        combined = []
        if sign_traits:
            combined.extend(sign_traits[:2])
        if house_traits:
            combined.append(f"expressed through {house_traits[0]}")
        
        return combined
    
    def _get_moon_traits(self, sign: str, house: int) -> List[str]:
        """Get emotional traits based on Moon placement."""
        sign_data = self.sign_meanings.get(sign, {})
        emotional = sign_data.get("emotional", "")
        
        traits = []
        if emotional:
            traits.append(emotional)
        
        house_area = self.house_meanings.get(house, {}).get("area", "")
        if house_area:
            traits.append(f"Emotional focus on {house_area.lower()}")
        
        return traits
    
    def _get_mercury_traits(self, sign: str) -> List[str]:
        """Get communication traits based on Mercury placement."""
        sign_data = self.sign_meanings.get(sign, {})
        element = sign_data.get("element", "")
        quality = sign_data.get("quality", "")
        
        traits = []
        
        if element == "Fire":
            traits.append("Direct and enthusiastic communication")
        elif element == "Earth":
            traits.append("Practical and methodical thinking")
        elif element == "Air":
            traits.append("Intellectual and versatile communication")
        elif element == "Water":
            traits.append("Intuitive and empathetic communication")
        
        if quality == "Cardinal":
            traits.append("Initiating conversations")
        elif quality == "Fixed":
            traits.append("Persistent in viewpoints")
        elif quality == "Mutable":
            traits.append("Adaptable communication style")
        
        return traits
    
    def _get_personality_aspects(self, aspects: List[Dict]) -> List[Dict]:
        """Extract personality-relevant aspects."""
        personality_aspects = []
        
        # Focus on aspects involving personal planets
        personal_planets = ["Sun", "Moon", "Mercury", "Venus", "Mars"]
        
        for aspect in aspects:
            planet1 = aspect.get("planet1", "")
            planet2 = aspect.get("planet2", "")
            
            if planet1 in personal_planets or planet2 in personal_planets:
                aspect_type = aspect.get("aspect", "")
                aspect_meaning = self.aspect_meanings.get(aspect_type, {})
                
                personality_aspects.append({
                    "aspect": f"{planet1} {aspect_type} {planet2}",
                    "interpretation": aspect_meaning.get("interpretation", ""),
                    "keywords": aspect_meaning.get("keywords", [])
                })
        
        return personality_aspects[:5]  # Top 5 aspects
    
    def _identify_strengths(self, planets: Dict, aspects: List[Dict]) -> List[str]:
        """Identify personality strengths."""
        strengths = []
        
        # Trines and sextiles indicate natural talents
        harmonious_aspects = [
            a for a in aspects 
            if a.get("aspect") in ["trine", "sextile"]
        ]
        
        if harmonious_aspects:
            strengths.append("Natural flow between different life areas")
        
        # Well-placed planets
        for planet, data in planets.items():
            sign = data.get("sign", "")
            # Check if planet is in domicile or exaltation
            planet_meaning = self.planet_meanings.get(planet, {})
            if planet_meaning:
                strengths.extend(planet_meaning.get("positive", [])[:1])
        
        return strengths[:5]
    
    def _identify_challenges(self, planets: Dict, aspects: List[Dict]) -> List[str]:
        """Identify personality challenges."""
        challenges = []
        
        # Squares and oppositions indicate challenges
        challenging_aspects = [
            a for a in aspects 
            if a.get("aspect") in ["square", "opposition"]
        ]
        
        if challenging_aspects:
            challenges.append("Integration needed between conflicting energies")
        
        # Retrograde planets
        for planet, data in planets.items():
            if data.get("is_retrograde", False):
                challenges.append(f"{planet} retrograde: internalized {planet} themes")
        
        return challenges[:5]
    
    def _suggest_growth_areas(self, planets: Dict, aspects: List[Dict]) -> List[str]:
        """Suggest areas for personal growth."""
        growth_areas = []
        
        # Based on challenging aspects
        for aspect in aspects:
            if aspect.get("aspect") in ["square", "opposition"]:
                planet1 = aspect.get("planet1", "")
                planet2 = aspect.get("planet2", "")
                growth_areas.append(
                    f"Integrate {planet1} and {planet2} energies"
                )
        
        # Based on lacking elements
        element_analysis = self._analyze_elements(planets)
        lacking = element_analysis.get("lacking", [])
        for element in lacking:
            growth_areas.append(f"Develop {element} qualities")
        
        return growth_areas[:3]
    
    def _get_sign_from_degree(self, degree: float) -> str:
        """Convert degree to zodiac sign."""
        signs = [
            "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
            "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
        ]
        return signs[int(degree / 30) % 12]
    
    def _get_sign_ruler(self, sign: str) -> str:
        """Get traditional ruler of a sign."""
        rulers = {
            "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury",
            "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury",
            "Libra": "Venus", "Scorpio": "Mars", "Sagittarius": "Jupiter",
            "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter"
        }
        return rulers.get(sign, "")
    
    def _suggest_careers(
        self,
        planets: Dict,
        career_indicators: List[Dict]
    ) -> List[str]:
        """Suggest suitable career paths."""
        careers = []
        
        # Based on 10th house planets
        tenth_house = [p for p, data in planets.items() if data.get("house") == 10]
        
        for planet in tenth_house:
            if planet == "Sun":
                careers.extend(["Leadership", "Management", "Entertainment"])
            elif planet == "Moon":
                careers.extend(["Caregiving", "Hospitality", "Public service"])
            elif planet == "Mercury":
                careers.extend(["Writing", "Teaching", "Communications"])
            elif planet == "Venus":
                careers.extend(["Arts", "Design", "Diplomacy"])
            elif planet == "Mars":
                careers.extend(["Sports", "Military", "Surgery"])
            elif planet == "Jupiter":
                careers.extend(["Education", "Law", "Publishing"])
            elif planet == "Saturn":
                careers.extend(["Administration", "Engineering", "Architecture"])
        
        # Based on MC sign
        if career_indicators:
            for indicator in career_indicators:
                if indicator.get("factor") == "MC Ruler":
                    # Add careers based on MC ruler
                    pass
        
        return list(set(careers))[:6]  # Unique careers, max 6
    
    def _analyze_work_style(self, planets: Dict) -> Dict:
        """Analyze working style preferences."""
        work_style = {
            "environment": [],
            "approach": [],
            "motivations": []
        }
        
        # 6th house analysis
        sixth_house = [p for p, data in planets.items() if data.get("house") == 6]
        
        if "Mercury" in sixth_house:
            work_style["environment"].append("Intellectual stimulation needed")
        if "Venus" in sixth_house:
            work_style["environment"].append("Harmonious workplace important")
        
        # Mars placement for work approach
        if "Mars" in planets:
            mars_sign = planets["Mars"].get("sign", "")
            mars_element = self.sign_meanings.get(mars_sign, {}).get("element", "")
            
            if mars_element == "Fire":
                work_style["approach"].append("Direct and energetic")
            elif mars_element == "Earth":
                work_style["approach"].append("Methodical and persistent")
        
        return work_style
    
    def _predict_career_timing(self, chart_data: Dict) -> List[str]:
        """Predict favorable career timing."""
        # Simplified - would use progressions/transits
        timing = []
        
        # Saturn returns
        timing.append("Major career shifts around ages 29-30, 58-60 (Saturn returns)")
        
        # Jupiter cycles
        timing.append("Opportunities every 12 years (Jupiter returns)")
        
        return timing
    
    def _analyze_financial_potential(
        self,
        planets: Dict,
        houses: List[float]
    ) -> Dict:
        """Analyze financial potential."""
        financial = {
            "potential": "moderate",
            "sources": [],
            "advice": []
        }
        
        # 2nd house (personal resources)
        second_house = [p for p, data in planets.items() if data.get("house") == 2]
        
        if "Jupiter" in second_house:
            financial["potential"] = "high"
            financial["sources"].append("Natural abundance")
        elif "Saturn" in second_house:
            financial["potential"] = "steady growth"
            financial["advice"].append("Build wealth slowly and steadily")
        
        # 8th house (shared resources)
        eighth_house = [p for p, data in planets.items() if data.get("house") == 8]
        
        if eighth_house:
            financial["sources"].append("Shared resources, investments")
        
        return financial
    
    def _get_venus_love_style(self, sign: str) -> str:
        """Get love style based on Venus sign."""
        love_styles = {
            "Aries": "Passionate and direct",
            "Taurus": "Sensual and loyal",
            "Gemini": "Playful and communicative",
            "Cancer": "Nurturing and protective",
            "Leo": "Romantic and generous",
            "Virgo": "Devoted and practical",
            "Libra": "Harmonious and partnership-oriented",
            "Scorpio": "Intense and transformative",
            "Sagittarius": "Adventurous and freedom-loving",
            "Capricorn": "Committed and traditional",
            "Aquarius": "Independent and unconventional",
            "Pisces": "Romantic and idealistic"
        }
        return love_styles.get(sign, "Unique")
    
    def _get_mars_passion_style(self, sign: str) -> str:
        """Get passion style based on Mars sign."""
        passion_styles = {
            "Aries": "Direct and fiery",
            "Taurus": "Slow-burning and sensual",
            "Gemini": "Varied and mental",
            "Cancer": "Emotional and protective",
            "Leo": "Dramatic and playful",
            "Virgo": "Refined and attentive",
            "Libra": "Balanced and aesthetic",
            "Scorpio": "Intense and profound",
            "Sagittarius": "Adventurous and spontaneous",
            "Capricorn": "Controlled and enduring",
            "Aquarius": "Experimental and detached",
            "Pisces": "Romantic and imaginative"
        }
        return passion_styles.get(sign, "Complex")
    
    def _analyze_relationship_patterns(
        self,
        planets: Dict,
        aspects: List[Dict],
        factors: List[Dict]
    ) -> List[str]:
        """Analyze relationship patterns."""
        patterns = []
        
        # Venus aspects
        venus_aspects = [
            a for a in aspects 
            if "Venus" in [a.get("planet1"), a.get("planet2")]
        ]
        
        for aspect in venus_aspects:
            if aspect.get("aspect") == "square":
                patterns.append("Challenges in relationships lead to growth")
            elif aspect.get("aspect") == "trine":
                patterns.append("Natural ease in relationships")
        
        # 7th house ruler
        # Simplified - would need to calculate actual ruler
        patterns.append("Partnerships are significant life theme")
        
        return patterns
    
    def _describe_ideal_partner(self, planets: Dict, aspects: List[Dict]) -> Dict:
        """Describe ideal partner characteristics."""
        ideal_partner = {
            "qualities": [],
            "signs": [],
            "elements": []
        }
        
        # Based on 7th house
        seventh_house = [p for p, data in planets.items() if data.get("house") == 7]
        
        if seventh_house:
            for planet in seventh_house:
                if planet == "Venus":
                    ideal_partner["qualities"].append("Attractive and harmonious")
                elif planet == "Mars":
                    ideal_partner["qualities"].append("Dynamic and assertive")
                elif planet == "Jupiter":
                    ideal_partner["qualities"].append("Wise and expansive")
        
        # Based on Venus sign
        if "Venus" in planets:
            venus_sign = planets["Venus"].get("sign", "")
            venus_element = self.sign_meanings.get(venus_sign, {}).get("element", "")
            
            # Compatible elements
            if venus_element == "Fire":
                ideal_partner["elements"].extend(["Fire", "Air"])
            elif venus_element == "Earth":
                ideal_partner["elements"].extend(["Earth", "Water"])
            elif venus_element == "Air":
                ideal_partner["elements"].extend(["Air", "Fire"])
            elif venus_element == "Water":
                ideal_partner["elements"].extend(["Water", "Earth"])
        
        return ideal_partner
    
    def _identify_relationship_lessons(
        self,
        planets: Dict,
        aspects: List[Dict]
    ) -> List[str]:
        """Identify relationship lessons."""
        lessons = []
        
        # Saturn in 7th
        if any(p for p, d in planets.items() if d.get("house") == 7 and p == "Saturn"):
            lessons.append("Learning commitment and responsibility in partnerships")
        
        # Challenging Venus aspects
        venus_squares = [
            a for a in aspects 
            if "Venus" in [a.get("planet1"), a.get("planet2")] 
            and a.get("aspect") == "square"
        ]
        
        if venus_squares:
            lessons.append("Integrating different relationship needs")
        
        # North Node in 7th
        if any(p for p, d in planets.items() if d.get("house") == 7 and p == "NorthNode"):
            lessons.append("Soul growth through partnerships")
        
        return lessons
    
    def _list_compatibility_factors(self, planets: Dict) -> List[str]:
        """List key compatibility factors."""
        factors = []
        
        # Sun sign element
        if "Sun" in planets:
            sun_sign = planets["Sun"].get("sign", "")
            sun_element = self.sign_meanings.get(sun_sign, {}).get("element", "")
            factors.append(f"Sun in {sun_element}: Compatible with {sun_element} and complementary elements")
        
        # Moon sign
        if "Moon" in planets:
            moon_sign = planets["Moon"].get("sign", "")
            factors.append(f"Moon in {moon_sign}: Emotional compatibility important")
        
        # Venus sign
        if "Venus" in planets:
            venus_sign = planets["Venus"].get("sign", "")
            factors.append(f"Venus in {venus_sign}: Love language compatibility")
        
        return factors
    
    def _get_sign_body_rulership(self, sign: str) -> str:
        """Get body parts ruled by sign."""
        rulerships = {
            "Aries": "Head and face",
            "Taurus": "Throat and neck",
            "Gemini": "Arms and lungs",
            "Cancer": "Chest and stomach",
            "Leo": "Heart and spine",
            "Virgo": "Digestive system",
            "Libra": "Kidneys and lower back",
            "Scorpio": "Reproductive system",
            "Sagittarius": "Hips and thighs",
            "Capricorn": "Knees and bones",
            "Aquarius": "Ankles and circulation",
            "Pisces": "Feet and immune system"
        }
        return rulerships.get(sign, "General vitality")
    
    def _identify_health_vulnerabilities(self, planets: Dict) -> List[str]:
        """Identify potential health vulnerabilities."""
        vulnerabilities = []
        
        # 6th house planets
        sixth_house = [p for p, data in planets.items() if data.get("house") == 6]
        
        if "Saturn" in sixth_house:
            vulnerabilities.append("Chronic conditions requiring discipline")
        elif "Mars" in sixth_house:
            vulnerabilities.append("Tendency toward inflammation or accidents")
        elif "Neptune" in sixth_house:
            vulnerabilities.append("Sensitivity to substances and environment")
        
        # Afflicted luminaries
        # Simplified - would check actual aspects
        
        return vulnerabilities
    
    def _generate_wellness_advice(self, planets: Dict) -> List[str]:
        """Generate wellness advice based on chart."""
        advice = []
        
        # Sun sign vitality
        if "Sun" in planets:
            sun_sign = planets["Sun"].get("sign", "")
            sun_element = self.sign_meanings.get(sun_sign, {}).get("element", "")
            
            if sun_element == "Fire":
                advice.append("Regular physical activity essential")
            elif sun_element == "Earth":
                advice.append("Grounding practices and routine important")
            elif sun_element == "Air":
                advice.append("Mental stimulation and fresh air needed")
            elif sun_element == "Water":
                advice.append("Emotional expression and water activities helpful")
        
        # Moon sign self-care
        if "Moon" in planets:
            moon_sign = planets["Moon"].get("sign", "")
            advice.append(f"Nurture yourself through {moon_sign} activities")
        
        return advice
    
    def _identify_spiritual_path(self, planets: Dict) -> List[str]:
        """Identify spiritual path indicators."""
        paths = []
        
        # 9th house
        ninth_house = [p for p, data in planets.items() if data.get("house") == 9]
        
        if "Jupiter" in ninth_house:
            paths.append("Traditional wisdom and philosophy")
        elif "Neptune" in ninth_house:
            paths.append("Mystical and transcendent practices")
        elif "Uranus" in ninth_house:
            paths.append("Revolutionary and unique spiritual path")
        
        # 12th house
        twelfth_house = [p for p, data in planets.items() if data.get("house") == 12]
        
        if twelfth_house:
            paths.append("Meditation and solitary practices")
        
        # Neptune placement
        if "Neptune" in planets:
            neptune_sign = planets["Neptune"].get("sign", "")
            paths.append(f"Spiritual connection through {neptune_sign} themes")
        
        return paths
    
    def _identify_karmic_patterns(self, planets: Dict) -> List[str]:
        """Identify karmic patterns and lessons."""
        patterns = []
        
        # Saturn placement
        if "Saturn" in planets:
            saturn_house = planets["Saturn"].get("house", 1)
            patterns.append(f"Karmic lessons in house {saturn_house} areas")
        
        # South Node
        if "SouthNode" in planets:
            sn_sign = planets["SouthNode"].get("sign", "")
            patterns.append(f"Past life talents in {sn_sign}")
        
        # 12th house planets
        twelfth_house = [p for p, data in planets.items() if data.get("house") == 12]
        
        if twelfth_house:
            patterns.append("Hidden karmic debts to resolve")
        
        return patterns
    
    def _describe_soul_mission(self, planets: Dict) -> str:
        """Describe soul mission based on chart."""
        # North Node primary indicator
        if "NorthNode" in planets:
            nn_sign = planets["NorthNode"].get("sign", "")
            nn_house = planets["NorthNode"].get("house", 1)
            
            return f"Soul mission involves developing {nn_sign} qualities " + \
                   f"through {self.house_meanings.get(nn_house, {}).get('area', 'life experiences')}"
        
        # Sun as backup
        if "Sun" in planets:
            sun_sign = planets["Sun"].get("sign", "")
            return f"Soul mission of authentic self-expression through {sun_sign}"
        
        return "Soul mission of self-discovery and growth"
    
    def _identify_life_themes(self, planets: Dict) -> List[str]:
        """Identify major life themes."""
        themes = []
        
        # Stelliums (3+ planets in a sign/house)
        house_counts = {}
        sign_counts = {}
        
        for planet, data in planets.items():
            house = data.get("house", 0)
            sign = data.get("sign", "")
            
            house_counts[house] = house_counts.get(house, 0) + 1
            sign_counts[sign] = sign_counts.get(sign, 0) + 1
        
        # House stelliums
        for house, count in house_counts.items():
            if count >= 3:
                area = self.house_meanings.get(house, {}).get("area", "")
                themes.append(f"Major focus on {area}")
        
        # Sign stelliums
        for sign, count in sign_counts.items():
            if count >= 3:
                themes.append(f"Strong {sign} themes throughout life")
        
        # Angular planets
        angular = [p for p, d in planets.items() if d.get("house") in [1, 4, 7, 10]]
        if angular:
            themes.append("Public visibility and impact")
        
        return themes
    
    def _describe_evolutionary_path(self, planets: Dict) -> str:
        """Describe evolutionary/growth path."""
        # Pluto placement
        if "Pluto" in planets:
            pluto_sign = planets["Pluto"].get("sign", "")
            pluto_house = planets["Pluto"].get("house", 1)
            
            return f"Evolutionary path of transformation through {pluto_sign} " + \
                   f"in {self.house_meanings.get(pluto_house, {}).get('area', 'life')}"
        
        return "Evolutionary path of conscious growth and transformation"