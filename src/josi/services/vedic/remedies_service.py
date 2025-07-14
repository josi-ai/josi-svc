"""
Vedic remedies and gemstone recommendation calculator.
"""
from typing import Dict, List, Optional
from datetime import datetime


class RemediesCalculator:
    """Calculate personalized remedies based on planetary positions."""
    
    def __init__(self):
        # Gemstone recommendations for planets
        self.gemstones = {
            "Sun": {
                "primary": "Ruby",
                "alternative": ["Red Spinel", "Red Garnet", "Red Tourmaline"],
                "metal": "Gold",
                "weight": "3-6 carats",
                "finger": "Ring finger",
                "day": "Sunday",
                "mantra": "Om Suryaya Namah"
            },
            "Moon": {
                "primary": "Pearl",
                "alternative": ["Moonstone", "White Coral"],
                "metal": "Silver",
                "weight": "2-4 carats",
                "finger": "Ring finger or little finger",
                "day": "Monday",
                "mantra": "Om Chandraya Namah"
            },
            "Mars": {
                "primary": "Red Coral",
                "alternative": ["Carnelian", "Red Jasper"],
                "metal": "Gold or Copper",
                "weight": "5-9 carats",
                "finger": "Ring finger",
                "day": "Tuesday",
                "mantra": "Om Mangalaya Namah"
            },
            "Mercury": {
                "primary": "Emerald",
                "alternative": ["Green Tourmaline", "Peridot", "Green Jade"],
                "metal": "Gold or Silver",
                "weight": "3-6 carats",
                "finger": "Little finger",
                "day": "Wednesday",
                "mantra": "Om Budhaya Namah"
            },
            "Jupiter": {
                "primary": "Yellow Sapphire",
                "alternative": ["Yellow Topaz", "Citrine", "Yellow Beryl"],
                "metal": "Gold",
                "weight": "3-5 carats",
                "finger": "Index finger",
                "day": "Thursday",
                "mantra": "Om Brihaspataye Namah"
            },
            "Venus": {
                "primary": "Diamond",
                "alternative": ["White Sapphire", "White Topaz", "White Zircon"],
                "metal": "Silver or Platinum",
                "weight": "0.5-1 carat",
                "finger": "Ring finger or middle finger",
                "day": "Friday",
                "mantra": "Om Shukraya Namah"
            },
            "Saturn": {
                "primary": "Blue Sapphire",
                "alternative": ["Amethyst", "Blue Spinel", "Lapis Lazuli"],
                "metal": "Silver or Iron",
                "weight": "3-6 carats",
                "finger": "Middle finger",
                "day": "Saturday",
                "mantra": "Om Shanaishcharaya Namah"
            },
            "Rahu": {
                "primary": "Hessonite Garnet",
                "alternative": ["Orange Zircon", "Spessartite Garnet"],
                "metal": "Silver",
                "weight": "4-6 carats",
                "finger": "Middle finger",
                "day": "Saturday",
                "mantra": "Om Rahave Namah"
            },
            "Ketu": {
                "primary": "Cat's Eye Chrysoberyl",
                "alternative": ["Tiger's Eye", "Turquoise"],
                "metal": "Silver",
                "weight": "3-6 carats",
                "finger": "Ring finger",
                "day": "Tuesday",
                "mantra": "Om Ketave Namah"
            }
        }
        
        # Donation recommendations
        self.donations = {
            "Sun": {
                "items": ["Wheat", "Jaggery", "Copper", "Red clothes"],
                "beneficiary": "Father figures, government servants",
                "day": "Sunday",
                "color": "Red or Orange"
            },
            "Moon": {
                "items": ["Rice", "Milk", "White clothes", "Silver"],
                "beneficiary": "Women, especially mothers",
                "day": "Monday",
                "color": "White"
            },
            "Mars": {
                "items": ["Red lentils", "Red clothes", "Copper utensils"],
                "beneficiary": "Soldiers, athletes, young men",
                "day": "Tuesday",
                "color": "Red"
            },
            "Mercury": {
                "items": ["Green moong dal", "Green clothes", "Books"],
                "beneficiary": "Students, teachers, intellectuals",
                "day": "Wednesday",
                "color": "Green"
            },
            "Jupiter": {
                "items": ["Yellow items", "Turmeric", "Gold", "Books"],
                "beneficiary": "Priests, teachers, gurus",
                "day": "Thursday",
                "color": "Yellow"
            },
            "Venus": {
                "items": ["White items", "Perfumes", "Clothes", "Sweets"],
                "beneficiary": "Women, artists, musicians",
                "day": "Friday",
                "color": "White or Pink"
            },
            "Saturn": {
                "items": ["Black sesame", "Iron", "Black clothes", "Oil"],
                "beneficiary": "Poor people, laborers, elderly",
                "day": "Saturday",
                "color": "Black or Dark Blue"
            },
            "Rahu": {
                "items": ["Blue clothes", "Sesame seeds", "Electronics"],
                "beneficiary": "Outcasts, foreigners",
                "day": "Saturday",
                "color": "Blue or Black"
            },
            "Ketu": {
                "items": ["Multicolored clothes", "Sesame seeds", "Blankets"],
                "beneficiary": "Dogs, spiritual people",
                "day": "Tuesday",
                "color": "Grey or Checkered"
            }
        }
    
    def analyze_chart_for_remedies(self, chart_data: Dict) -> Dict:
        """
        Analyze chart to recommend remedies.
        
        Args:
            chart_data: Complete chart data with planetary positions
        
        Returns:
            Dictionary with remedy recommendations
        """
        remedies = {
            "gemstones": [],
            "mantras": [],
            "donations": [],
            "yantras": [],
            "fasting": [],
            "general_remedies": []
        }
        
        # Analyze planetary strengths and afflictions
        planets = chart_data.get("planets", {})
        houses = chart_data.get("houses", [])
        
        # Check for weak or afflicted planets
        weak_planets = self._identify_weak_planets(planets, chart_data)
        afflicted_planets = self._identify_afflicted_planets(planets, chart_data)
        
        # Recommend gemstones for weak benefic planets
        for planet in weak_planets:
            if planet in ["Jupiter", "Venus", "Mercury", "Moon"]:
                gemstone_info = self._get_gemstone_recommendation(planet, planets[planet])
                if gemstone_info:
                    remedies["gemstones"].append(gemstone_info)
        
        # Recommend mantras for afflicted planets
        for planet in afflicted_planets:
            mantra_info = self._get_mantra_recommendation(planet)
            remedies["mantras"].append(mantra_info)
        
        # Recommend donations for malefic planets
        malefic_planets = self._identify_prominent_malefics(planets, chart_data)
        for planet in malefic_planets:
            donation_info = self._get_donation_recommendation(planet)
            remedies["donations"].append(donation_info)
        
        # Add general remedies based on chart analysis
        general = self._get_general_remedies(chart_data)
        remedies["general_remedies"] = general
        
        # Add yantras for specific doshas
        yantras = self._recommend_yantras(chart_data)
        remedies["yantras"] = yantras
        
        # Add fasting recommendations
        fasting = self._recommend_fasting(weak_planets + afflicted_planets)
        remedies["fasting"] = fasting
        
        return remedies
    
    def _identify_weak_planets(self, planets: Dict, chart_data: Dict) -> List[str]:
        """Identify weak planets in the chart."""
        weak_planets = []
        
        for planet, data in planets.items():
            # Check if planet is debilitated
            if data.get("dignity") == "debilitated":
                weak_planets.append(planet)
            
            # Check if planet is combust (too close to Sun)
            elif planet != "Sun" and data.get("is_combust"):
                weak_planets.append(planet)
            
            # Check if planet is in enemy sign
            elif self._is_in_enemy_sign(planet, data.get("sign")):
                weak_planets.append(planet)
        
        return weak_planets
    
    def _identify_afflicted_planets(self, planets: Dict, chart_data: Dict) -> List[str]:
        """Identify afflicted planets (aspected by malefics)."""
        afflicted = []
        aspects = chart_data.get("aspects", [])
        
        malefics = ["Mars", "Saturn", "Rahu", "Ketu"]
        
        for aspect in aspects:
            if aspect["aspect"] in ["conjunction", "square", "opposition"]:
                if aspect["planet1"] in malefics:
                    if aspect["planet2"] not in afflicted:
                        afflicted.append(aspect["planet2"])
                elif aspect["planet2"] in malefics:
                    if aspect["planet1"] not in afflicted:
                        afflicted.append(aspect["planet1"])
        
        return afflicted
    
    def _identify_prominent_malefics(self, planets: Dict, chart_data: Dict) -> List[str]:
        """Identify prominent malefic planets that need pacification."""
        prominent_malefics = []
        
        # Natural malefics
        malefics = ["Mars", "Saturn", "Rahu", "Ketu"]
        
        # Add Sun if afflicting important houses
        ascendant = chart_data.get("ascendant", {})
        
        for planet in malefics:
            if planet in planets:
                # Check if in angular houses (1, 4, 7, 10)
                house = planets[planet].get("house")
                if house in [1, 4, 7, 10]:
                    prominent_malefics.append(planet)
                
                # Check if ruling important houses
                elif self._rules_important_house(planet, chart_data):
                    prominent_malefics.append(planet)
        
        return list(set(prominent_malefics))
    
    def _get_gemstone_recommendation(self, planet: str, planet_data: Dict) -> Optional[Dict]:
        """Get gemstone recommendation for a planet."""
        if planet not in self.gemstones:
            return None
        
        gem_info = self.gemstones[planet].copy()
        
        # Add specific recommendations based on planet condition
        recommendation = {
            "planet": planet,
            "condition": self._get_planet_condition(planet_data),
            "primary_stone": gem_info["primary"],
            "alternative_stones": gem_info["alternative"],
            "weight": gem_info["weight"],
            "metal": gem_info["metal"],
            "finger": gem_info["finger"],
            "day_to_wear": gem_info["day"],
            "activation_mantra": gem_info["mantra"],
            "wearing_instructions": self._get_wearing_instructions(planet)
        }
        
        return recommendation
    
    def _get_mantra_recommendation(self, planet: str) -> Dict:
        """Get mantra recommendation for a planet."""
        mantras = {
            "Sun": {
                "vedic": "Om Suryaya Namah",
                "tantric": "Om Hram Hreem Hroum Sah Suryaya Namah",
                "gayatri": "Om Bhaskaraya Vidmahe Divakaraya Dhimahi Tanno Suryah Prachodayat"
            },
            "Moon": {
                "vedic": "Om Chandraya Namah",
                "tantric": "Om Shram Shreem Shroum Sah Chandraya Namah",
                "gayatri": "Om Kshirputraya Vidmahe Amrittatvaya Dhimahi Tanno Chandrah Prachodayat"
            },
            "Mars": {
                "vedic": "Om Mangalaya Namah",
                "tantric": "Om Kram Kreem Kroum Sah Bhaumaya Namah",
                "gayatri": "Om Angarakaya Vidmahe Sakti Hastaya Dhimahi Tanno Bhauma Prachodayat"
            },
            "Mercury": {
                "vedic": "Om Budhaya Namah",
                "tantric": "Om Bram Breem Broum Sah Budhaya Namah",
                "gayatri": "Om Gajadhwajaaya Vidmahe Sukha Hastaya Dhimahi Tanno Budha Prachodayat"
            },
            "Jupiter": {
                "vedic": "Om Brihaspataye Namah",
                "tantric": "Om Gram Greem Groum Sah Guruve Namah",
                "gayatri": "Om Vrishabadhwajaaya Vidmahe Kruni Hastaya Dhimahi Tanno Guru Prachodayat"
            },
            "Venus": {
                "vedic": "Om Shukraya Namah",
                "tantric": "Om Dram Dreem Droum Sah Shukraya Namah",
                "gayatri": "Om Ashwadhwajaaya Vidmahe Dhanur Hastaya Dhimahi Tanno Shukra Prachodayat"
            },
            "Saturn": {
                "vedic": "Om Shanaishcharaya Namah",
                "tantric": "Om Pram Preem Proum Sah Shanaischaraya Namah",
                "gayatri": "Om Kaakadhwajaaya Vidmahe Khadga Hastaya Dhimahi Tanno Mandah Prachodayat"
            },
            "Rahu": {
                "vedic": "Om Rahave Namah",
                "tantric": "Om Bhram Bhreem Bhroum Sah Rahave Namah",
                "gayatri": "Om Naakadhwajaaya Vidmahe Padma Hastaya Dhimahi Tanno Rahu Prachodayat"
            },
            "Ketu": {
                "vedic": "Om Ketave Namah",
                "tantric": "Om Sram Sreem Sroum Sah Ketave Namah",
                "gayatri": "Om Ashwadhwajaaya Vidmahe Soola Hastaya Dhimahi Tanno Ketu Prachodayat"
            }
        }
        
        planet_mantras = mantras.get(planet, {})
        
        return {
            "planet": planet,
            "mantras": planet_mantras,
            "count": "108 times daily" if planet in ["Saturn", "Rahu", "Ketu"] else "108 times daily",
            "best_time": "During planetary hora" if planet != "Rahu" else "During Rahu Kaal",
            "minimum_days": 40
        }
    
    def _get_donation_recommendation(self, planet: str) -> Dict:
        """Get donation recommendation for a planet."""
        if planet not in self.donations:
            return {}
        
        donation_info = self.donations[planet].copy()
        
        return {
            "planet": planet,
            "items": donation_info["items"],
            "beneficiary": donation_info["beneficiary"],
            "day": donation_info["day"],
            "color": donation_info["color"],
            "quantity": "As per capacity",
            "frequency": "Every week on the planet's day"
        }
    
    def _get_general_remedies(self, chart_data: Dict) -> List[Dict]:
        """Get general remedies based on overall chart analysis."""
        remedies = []
        
        # Check for specific doshas
        if self._has_kaal_sarp_dosha(chart_data):
            remedies.append({
                "dosha": "Kaal Sarp Dosha",
                "remedies": [
                    "Perform Kaal Sarp Dosha Puja",
                    "Worship Lord Shiva regularly",
                    "Chant Om Namah Shivaya 108 times daily",
                    "Keep peacock feathers at home"
                ]
            })
        
        if self._has_pitra_dosha(chart_data):
            remedies.append({
                "dosha": "Pitra Dosha",
                "remedies": [
                    "Perform Pitra Tarpan",
                    "Feed crows and dogs regularly",
                    "Donate to old age homes",
                    "Perform Shradh ceremonies"
                ]
            })
        
        # General remedies for well-being
        remedies.append({
            "type": "General Well-being",
            "remedies": [
                "Worship your Ishta Devata (personal deity)",
                "Practice meditation daily",
                "Maintain good karma through service",
                "Respect elders and teachers"
            ]
        })
        
        return remedies
    
    def _recommend_yantras(self, chart_data: Dict) -> List[Dict]:
        """Recommend yantras based on chart analysis."""
        yantras = []
        
        # Check which planets need strengthening
        weak_planets = self._identify_weak_planets(chart_data.get("planets", {}), chart_data)
        
        yantra_map = {
            "Sun": "Surya Yantra",
            "Moon": "Chandra Yantra",
            "Mars": "Mangal Yantra",
            "Mercury": "Budh Yantra",
            "Jupiter": "Guru Yantra",
            "Venus": "Shukra Yantra",
            "Saturn": "Shani Yantra",
            "Rahu": "Rahu Yantra",
            "Ketu": "Ketu Yantra"
        }
        
        for planet in weak_planets[:3]:  # Recommend max 3 yantras
            if planet in yantra_map:
                yantras.append({
                    "yantra": yantra_map[planet],
                    "planet": planet,
                    "placement": "Puja room or altar",
                    "activation": f"Energize on {self.gemstones[planet]['day']}",
                    "maintenance": "Clean regularly and offer flowers"
                })
        
        # Add Sri Yantra for overall prosperity
        if len(yantras) < 3:
            yantras.append({
                "yantra": "Sri Yantra",
                "purpose": "Overall prosperity and spiritual growth",
                "placement": "Northeast corner of home",
                "activation": "Friday during Venus hora",
                "maintenance": "Offer lotus flowers on Fridays"
            })
        
        return yantras
    
    def _recommend_fasting(self, planets: List[str]) -> List[Dict]:
        """Recommend fasting based on afflicted planets."""
        fasting = []
        
        fasting_map = {
            "Sun": {"day": "Sunday", "type": "Sunrise to sunset", "food": "Avoid salt"},
            "Moon": {"day": "Monday", "type": "Moonrise to moonrise", "food": "Milk and fruits only"},
            "Mars": {"day": "Tuesday", "type": "Sunrise to sunset", "food": "Avoid red items"},
            "Mercury": {"day": "Wednesday", "type": "Half day", "food": "Green vegetables only"},
            "Jupiter": {"day": "Thursday", "type": "Sunrise to sunset", "food": "Yellow items allowed"},
            "Venus": {"day": "Friday", "type": "Sunrise to sunset", "food": "White items only"},
            "Saturn": {"day": "Saturday", "type": "24 hours", "food": "Black sesame allowed"},
            "Rahu": {"day": "Saturday", "type": "Sunset to sunset", "food": "Simple vegetarian"},
            "Ketu": {"day": "Tuesday", "type": "Sunrise to sunset", "food": "Avoid grains"}
        }
        
        # Prioritize Saturn, Rahu, Ketu fasts
        priority_planets = ["Saturn", "Rahu", "Ketu"]
        
        for planet in priority_planets:
            if planet in planets and planet in fasting_map:
                fast_info = fasting_map[planet].copy()
                fast_info["planet"] = planet
                fasting.append(fast_info)
        
        # Add other planets if needed
        for planet in planets:
            if planet not in priority_planets and planet in fasting_map and len(fasting) < 3:
                fast_info = fasting_map[planet].copy()
                fast_info["planet"] = planet
                fasting.append(fast_info)
        
        return fasting
    
    def _get_planet_condition(self, planet_data: Dict) -> str:
        """Determine planet's condition."""
        dignity = planet_data.get("dignity", "neutral")
        is_combust = planet_data.get("is_combust", False)
        is_retrograde = planet_data.get("is_retrograde", False)
        
        if dignity == "exalted":
            return "Exalted - Very Strong"
        elif dignity == "own_sign":
            return "Own Sign - Strong"
        elif dignity == "debilitated":
            return "Debilitated - Weak"
        elif is_combust:
            return "Combust - Weakened"
        elif is_retrograde:
            return "Retrograde - Internalized"
        else:
            return "Neutral"
    
    def _get_wearing_instructions(self, planet: str) -> List[str]:
        """Get specific instructions for wearing gemstone."""
        general_instructions = [
            "Purify the gemstone in raw milk and honey",
            "Wear during the planetary hora on its day",
            "Chant the planet's mantra while wearing",
            "Face east while wearing the ring"
        ]
        
        specific = {
            "Sun": ["Wear at sunrise", "Avoid during eclipses"],
            "Moon": ["Wear on full moon day preferably", "Remove during eclipses"],
            "Saturn": ["Test for 3 days before permanent wear", "Donate black items before wearing"],
            "Rahu": ["Wear during Rahu Kaal", "Keep silver with the stone"],
            "Ketu": ["Wear on Tuesday during Mars hora", "Maintain spiritual practices"]
        }
        
        instructions = general_instructions.copy()
        if planet in specific:
            instructions.extend(specific[planet])
        
        return instructions
    
    def _is_in_enemy_sign(self, planet: str, sign: str) -> bool:
        """Check if planet is in enemy sign."""
        # Simplified enemy relationships
        enemies = {
            "Sun": ["Saturn", "Venus"],
            "Moon": ["None"],
            "Mars": ["Mercury"],
            "Mercury": ["Moon"],
            "Jupiter": ["Mercury", "Venus"],
            "Venus": ["Sun", "Moon"],
            "Saturn": ["Sun", "Moon", "Mars"]
        }
        
        # This is simplified - would need full sign lordship logic
        return False
    
    def _rules_important_house(self, planet: str, chart_data: Dict) -> bool:
        """Check if planet rules important houses."""
        # Simplified - would need to calculate house lordships
        return False
    
    def _has_kaal_sarp_dosha(self, chart_data: Dict) -> bool:
        """Check for Kaal Sarp Dosha (all planets between Rahu-Ketu)."""
        planets = chart_data.get("planets", {})
        
        if "Rahu" not in planets or "Ketu" not in planets:
            return False
        
        rahu_long = planets["Rahu"]["longitude"]
        ketu_long = planets["Ketu"]["longitude"]
        
        # Check if all planets are on one side of Rahu-Ketu axis
        # Simplified check - would need more complex logic
        return False
    
    def _has_pitra_dosha(self, chart_data: Dict) -> bool:
        """Check for Pitra Dosha (ancestral afflictions)."""
        # Check for Sun afflictions and 9th house issues
        # Simplified - would need full analysis
        return False