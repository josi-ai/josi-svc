"""
Ashtakoota compatibility calculator for Vedic astrology.

The Ashtakoota (8-fold) matching system evaluates marriage compatibility
based on 8 different factors from the Moon's nakshatra positions.
"""
from typing import Dict, List, Tuple
import math


class AshtakootaCalculator:
    """Calculate Vedic Ashtakoota compatibility for marriage matching."""
    
    def __init__(self):
        # Gana (temperament) classifications
        self.DEVA_GANA = [0, 4, 6, 9, 12, 14, 16, 20, 24]  # Divine nature
        self.MANUSHYA_GANA = [1, 2, 7, 10, 13, 17, 21, 25, 26]  # Human nature  
        self.RAKSHASA_GANA = [3, 5, 8, 11, 15, 18, 19, 22, 23]  # Demonic nature
        
        # Yoni (animal symbol) for each nakshatra
        self.YONI_ANIMALS = [
            "Horse", "Elephant", "Sheep", "Snake", "Dog", "Cat",
            "Rat", "Cow", "Buffalo", "Tiger", "Hare", "Monkey", 
            "Mongoose", "Lion", "Horse", "Elephant", "Sheep", "Snake",
            "Dog", "Cat", "Rat", "Cow", "Buffalo", "Tiger", "Lion", "Mongoose", "Hare"
        ]
        
        # Nakshatra lords for Graha Maitri
        self.NAKSHATRA_LORDS = [
            "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
            "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
            "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"
        ]
        
        # Planetary friendships for Graha Maitri calculation
        self.PLANETARY_FRIENDS = {
            "Sun": ["Moon", "Mars", "Jupiter"],
            "Moon": ["Sun", "Mercury"],
            "Mars": ["Sun", "Moon", "Jupiter"],
            "Mercury": ["Sun", "Venus"],
            "Jupiter": ["Sun", "Moon", "Mars"],
            "Venus": ["Mercury", "Saturn"],
            "Saturn": ["Mercury", "Venus"],
            "Rahu": ["Mercury", "Venus", "Saturn"],
            "Ketu": ["Mars", "Jupiter"]
        }
        
        # Nadi (pulse/health) classifications
        self.ADI_NADI = [0, 3, 6, 9, 12, 15, 18, 21, 24]
        self.MADHYA_NADI = [1, 4, 7, 10, 13, 16, 19, 22, 25]
        self.ANTYA_NADI = [2, 5, 8, 11, 14, 17, 20, 23, 26]
        
        # Varna (caste) classifications  
        self.BRAHMIN_VARNA = [2, 5, 8, 11, 14, 17, 20, 23, 26]
        self.KSHATRIYA_VARNA = [0, 4, 9, 12, 16, 21, 24]
        self.VAISHYA_VARNA = [1, 6, 10, 13, 18, 22, 25]
        self.SHUDRA_VARNA = [3, 7, 15, 19]
    
    def calculate_compatibility(self, person1_moon_longitude: float, person2_moon_longitude: float) -> Dict:
        """
        Calculate complete Ashtakoota compatibility between two people.
        
        Args:
            person1_moon_longitude: Moon longitude for person 1 (0-360°)
            person2_moon_longitude: Moon longitude for person 2 (0-360°)
            
        Returns:
            Dictionary with detailed compatibility analysis
        """
        # Convert longitudes to nakshatra numbers (0-26)
        nak1 = self._longitude_to_nakshatra(person1_moon_longitude)
        nak2 = self._longitude_to_nakshatra(person2_moon_longitude)
        
        # Calculate all 8 gunas
        guna_results = self._calculate_all_gunas(nak1, nak2)
        
        # Calculate total score
        total_points = sum(result["points"] for result in guna_results.values())
        max_total = sum(result["max_points"] for result in guna_results.values())
        
        # Determine compatibility level
        compatibility_level = self._get_compatibility_level(total_points)
        
        # Check for dosha (negative factors)
        doshas = self._check_doshas(nak1, nak2, guna_results)
        
        return {
            "person1_nakshatra": {
                "number": nak1 + 1,
                "name": self._get_nakshatra_name(nak1),
                "longitude": person1_moon_longitude
            },
            "person2_nakshatra": {
                "number": nak2 + 1,
                "name": self._get_nakshatra_name(nak2),
                "longitude": person2_moon_longitude
            },
            "ashtakoota_points": {
                "total_points": total_points,
                "max_points": max_total,
                "percentage": round((total_points / max_total) * 100, 1)
            },
            "guna_analysis": guna_results,
            "compatibility_level": compatibility_level,
            "doshas": doshas,
            "recommendations": self._get_recommendations(total_points, doshas),
            "overall_assessment": self._get_overall_assessment(total_points, compatibility_level, doshas)
        }
    
    def check_manglik_dosha(self, planets: Dict, houses: List[float]) -> Dict:
        """
        Check for Manglik dosha (Mars affliction).
        
        Args:
            planets: Dictionary of planetary positions
            houses: List of house cusps
            
        Returns:
            Dictionary with Manglik analysis
        """
        mars_data = planets.get("Mars", {})
        mars_house = mars_data.get("house", 0)
        
        # Manglik houses: 1, 2, 4, 7, 8, 12
        manglik_houses = [1, 2, 4, 7, 8, 12]
        is_manglik = mars_house in manglik_houses
        
        severity = "None"
        if is_manglik:
            if mars_house in [1, 7, 8]:
                severity = "High"
            elif mars_house in [2, 12]:
                severity = "Medium"
            else:
                severity = "Low"
        
        return {
            "is_manglik": is_manglik,
            "mars_house": mars_house,
            "severity": severity,
            "description": self._get_manglik_description(mars_house, severity),
            "remedies": self._get_manglik_remedies(severity) if is_manglik else []
        }
    
    def _longitude_to_nakshatra(self, longitude: float) -> int:
        """Convert longitude to nakshatra number (0-26)."""
        # Each nakshatra is 13°20' = 13.333...°
        nakshatra_size = 360 / 27
        return int(longitude / nakshatra_size) % 27
    
    def _calculate_all_gunas(self, nak1: int, nak2: int) -> Dict:
        """Calculate all 8 gunas of Ashtakoota matching."""
        return {
            "varna": self._calculate_varna(nak1, nak2),
            "vashya": self._calculate_vashya(nak1, nak2),
            "tara": self._calculate_tara(nak1, nak2),
            "yoni": self._calculate_yoni(nak1, nak2),
            "graha_maitri": self._calculate_graha_maitri(nak1, nak2),
            "gana": self._calculate_gana(nak1, nak2),
            "bhakoot": self._calculate_bhakoot(nak1, nak2),
            "nadi": self._calculate_nadi(nak1, nak2)
        }
    
    def _calculate_varna(self, nak1: int, nak2: int) -> Dict:
        """Calculate Varna guna (1 point)."""
        varna1 = self._get_varna(nak1)
        varna2 = self._get_varna(nak2)
        
        varna_order = ["Brahmin", "Kshatriya", "Vaishya", "Shudra"]
        score1 = varna_order.index(varna1)
        score2 = varna_order.index(varna2)
        
        # Girl's varna should be equal or lower than boy's
        points = 1 if score1 >= score2 else 0
        
        return {
            "points": points,
            "max_points": 1,
            "person1_varna": varna1,
            "person2_varna": varna2,
            "description": f"Varna compatibility: {varna1} - {varna2}"
        }
    
    def _calculate_vashya(self, nak1: int, nak2: int) -> Dict:
        """Calculate Vashya guna (2 points)."""
        sign1 = nak1 // 2.25  # Approximate sign from nakshatra
        sign2 = nak2 // 2.25
        
        # Simplified Vashya calculation
        if abs(sign1 - sign2) <= 1 or abs(sign1 - sign2) >= 11:
            points = 2
        elif abs(sign1 - sign2) in [2, 10]:
            points = 1
        else:
            points = 0
            
        return {
            "points": points,
            "max_points": 2,
            "description": "Vashya (mutual control) compatibility"
        }
    
    def _calculate_tara(self, nak1: int, nak2: int) -> Dict:
        """Calculate Tara guna (3 points)."""
        # Count from person1's nakshatra to person2's
        count = (nak2 - nak1) % 27 + 1
        
        # Favorable tara numbers: 1, 3, 5, 7, 9 (janma, sampat, kshema, sadhana, mitra)
        favorable = [1, 3, 5, 7, 9]
        unfavorable = [2, 4, 6, 8]  # vadha, pratyak, naidhana, ati-mitra
        
        if count in favorable:
            points = 3
        elif count in unfavorable:
            points = 0
        else:
            points = 1.5
            
        return {
            "points": points,
            "max_points": 3,
            "tara_count": count,
            "description": f"Tara count: {count}"
        }
    
    def _calculate_yoni(self, nak1: int, nak2: int) -> Dict:
        """Calculate Yoni guna (4 points)."""
        animal1 = self.YONI_ANIMALS[nak1]
        animal2 = self.YONI_ANIMALS[nak2]
        
        if animal1 == animal2:
            points = 4  # Same animal
        elif self._are_friendly_animals(animal1, animal2):
            points = 3  # Friendly animals
        elif self._are_neutral_animals(animal1, animal2):
            points = 2  # Neutral animals
        elif self._are_enemy_animals(animal1, animal2):
            points = 1  # Enemy animals
        else:
            points = 0  # Hostile animals
            
        return {
            "points": points,
            "max_points": 4,
            "person1_animal": animal1,
            "person2_animal": animal2,
            "description": f"Yoni compatibility: {animal1} - {animal2}"
        }
    
    def _calculate_graha_maitri(self, nak1: int, nak2: int) -> Dict:
        """Calculate Graha Maitri guna (5 points)."""
        lord1 = self.NAKSHATRA_LORDS[nak1]
        lord2 = self.NAKSHATRA_LORDS[nak2]
        
        if lord1 == lord2:
            points = 5  # Same lord
        elif lord2 in self.PLANETARY_FRIENDS.get(lord1, []):
            points = 4  # Friends
        elif lord1 in self.PLANETARY_FRIENDS.get(lord2, []):
            points = 4  # Friends (reverse)
        else:
            points = 1  # Neutral or enemies
            
        return {
            "points": points,
            "max_points": 5,
            "person1_lord": lord1,
            "person2_lord": lord2,
            "description": f"Graha Maitri: {lord1} - {lord2}"
        }
    
    def _calculate_gana(self, nak1: int, nak2: int) -> Dict:
        """Calculate Gana guna (6 points)."""
        gana1 = self._get_gana(nak1)
        gana2 = self._get_gana(nak2)
        
        if gana1 == gana2:
            points = 6  # Same gana
        elif (gana1 == "Deva" and gana2 == "Manushya") or (gana1 == "Manushya" and gana2 == "Deva"):
            points = 5  # Compatible
        elif (gana1 == "Manushya" and gana2 == "Rakshasa") or (gana1 == "Rakshasa" and gana2 == "Manushya"):
            points = 1  # Somewhat compatible
        else:
            points = 0  # Deva-Rakshasa incompatible
            
        return {
            "points": points,
            "max_points": 6,
            "person1_gana": gana1,
            "person2_gana": gana2,
            "description": f"Gana compatibility: {gana1} - {gana2}"
        }
    
    def _calculate_bhakoot(self, nak1: int, nak2: int) -> Dict:
        """Calculate Bhakoot guna (7 points)."""
        # Convert to approximate moon signs
        sign1 = int(nak1 * 13.333 / 30) % 12
        sign2 = int(nak2 * 13.333 / 30) % 12
        
        diff = abs(sign1 - sign2)
        
        # Same sign or friendly positions
        if diff == 0 or diff in [3, 4, 5, 7, 9, 10, 11]:
            points = 7
        elif diff in [2, 6]:  # 6/8 positions
            points = 0  # Asta-dosha
        else:
            points = 0
            
        return {
            "points": points,
            "max_points": 7,
            "description": f"Bhakoot (moon sign) compatibility"
        }
    
    def _calculate_nadi(self, nak1: int, nak2: int) -> Dict:
        """Calculate Nadi guna (8 points)."""
        nadi1 = self._get_nadi(nak1)
        nadi2 = self._get_nadi(nak2)
        
        # Same nadi is problematic for health
        points = 0 if nadi1 == nadi2 else 8
        
        return {
            "points": points,
            "max_points": 8,
            "person1_nadi": nadi1,
            "person2_nadi": nadi2,
            "description": f"Nadi compatibility: {nadi1} - {nadi2}"
        }
    
    def _get_varna(self, nak: int) -> str:
        """Get varna for nakshatra."""
        if nak in self.BRAHMIN_VARNA:
            return "Brahmin"
        elif nak in self.KSHATRIYA_VARNA:
            return "Kshatriya"
        elif nak in self.VAISHYA_VARNA:
            return "Vaishya"
        else:
            return "Shudra"
    
    def _get_gana(self, nak: int) -> str:
        """Get gana for nakshatra."""
        if nak in self.DEVA_GANA:
            return "Deva"
        elif nak in self.MANUSHYA_GANA:
            return "Manushya"
        else:
            return "Rakshasa"
    
    def _get_nadi(self, nak: int) -> str:
        """Get nadi for nakshatra."""
        if nak in self.ADI_NADI:
            return "Adi"
        elif nak in self.MADHYA_NADI:
            return "Madhya"
        else:
            return "Antya"
    
    def _are_friendly_animals(self, animal1: str, animal2: str) -> bool:
        """Check if animals are friendly."""
        friendly_pairs = [
            ("Horse", "Cow"), ("Elephant", "Sheep"), ("Cat", "Rat"),
            ("Dog", "Hare"), ("Snake", "Mongoose"), ("Tiger", "Monkey"),
            ("Buffalo", "Lion")
        ]
        return (animal1, animal2) in friendly_pairs or (animal2, animal1) in friendly_pairs
    
    def _are_neutral_animals(self, animal1: str, animal2: str) -> bool:
        """Check if animals are neutral."""
        # Most other combinations are neutral
        return not (self._are_friendly_animals(animal1, animal2) or 
                   self._are_enemy_animals(animal1, animal2))
    
    def _are_enemy_animals(self, animal1: str, animal2: str) -> bool:
        """Check if animals are enemies."""
        enemy_pairs = [
            ("Cat", "Dog"), ("Tiger", "Cow"), ("Lion", "Elephant"),
            ("Snake", "Mongoose"), ("Horse", "Buffalo")
        ]
        return (animal1, animal2) in enemy_pairs or (animal2, animal1) in enemy_pairs
    
    def _get_compatibility_level(self, points: float) -> str:
        """Determine compatibility level from total points."""
        if points >= 28:
            return "Excellent"
        elif points >= 24:
            return "Very Good"
        elif points >= 18:
            return "Good"
        elif points >= 13:
            return "Average"
        else:
            return "Poor"
    
    def _check_doshas(self, nak1: int, nak2: int, guna_results: Dict) -> List[Dict]:
        """Check for specific doshas (negative factors)."""
        doshas = []
        
        # Nadi dosha
        if guna_results["nadi"]["points"] == 0:
            doshas.append({
                "name": "Nadi Dosha",
                "severity": "High",
                "description": "Same Nadi can cause health issues in offspring",
                "remedies": ["Ganga snan", "Mahamrityunjaya mantra", "Medical consultation"]
            })
        
        # Bhakoot dosha
        if guna_results["bhakoot"]["points"] == 0:
            doshas.append({
                "name": "Bhakoot Dosha", 
                "severity": "Medium",
                "description": "6/8 position can cause financial and health problems",
                "remedies": ["Vishnu puja", "Charity", "Gemstone therapy"]
            })
        
        # Gana dosha
        if guna_results["gana"]["points"] == 0:
            doshas.append({
                "name": "Gana Dosha",
                "severity": "Medium", 
                "description": "Temperament mismatch can cause marital discord",
                "remedies": ["Jupiter strengthening", "Compatibility counseling"]
            })
        
        return doshas
    
    def _get_recommendations(self, points: float, doshas: List[Dict]) -> List[str]:
        """Get compatibility recommendations."""
        recommendations = []
        
        if points >= 24:
            recommendations.append("Highly compatible match - proceed with confidence")
        elif points >= 18:
            recommendations.append("Good compatibility - minor adjustments may help")
        elif points >= 13:
            recommendations.append("Average match - consider remedies for improvement")
        else:
            recommendations.append("Low compatibility - serious consideration needed")
        
        if doshas:
            recommendations.append("Perform recommended remedies to mitigate doshas")
            
        return recommendations
    
    def _get_overall_assessment(self, points: float, level: str, doshas: List[Dict]) -> str:
        """Get overall compatibility assessment."""
        if points >= 24 and not doshas:
            return "Excellent match with no major concerns"
        elif points >= 18 and len(doshas) <= 1:
            return "Good match with minor considerations"
        elif points >= 13:
            return "Average match requiring attention to specific areas"
        else:
            return "Challenging match requiring significant remedial measures"
    
    def _get_manglik_description(self, mars_house: int, severity: str) -> str:
        """Get description of Manglik condition."""
        if severity == "None":
            return "No Manglik dosha present"
        
        descriptions = {
            1: "Mars in 1st house can cause aggression and dominance issues",
            2: "Mars in 2nd house may affect speech and family relations", 
            4: "Mars in 4th house can cause property and vehicle problems",
            7: "Mars in 7th house may cause delays and conflicts in marriage",
            8: "Mars in 8th house can cause health and longevity concerns",
            12: "Mars in 12th house may cause financial losses and expenses"
        }
        
        return descriptions.get(mars_house, f"Mars in {mars_house}th house causes Manglik dosha")
    
    def _get_manglik_remedies(self, severity: str) -> List[str]:
        """Get remedies for Manglik dosha."""
        if severity == "High":
            return [
                "Marry another Manglik person",
                "Kumbh Vivah (marriage to banana tree/peepal tree)",
                "Hanuman worship on Tuesdays", 
                "Red coral gemstone",
                "Mangal Chandika Stotra recitation"
            ]
        elif severity == "Medium":
            return [
                "Regular Hanuman worship",
                "Tuesday fasting",
                "Red coral or red thread",
                "Mars pacification mantras"
            ]
        else:
            return [
                "Simple Mars remedies",
                "Tuesday prayers",
                "Avoid red color excess"
            ]
    
    def _get_nakshatra_name(self, nak_num: int) -> str:
        """Get nakshatra name from number."""
        names = [
            "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
            "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", 
            "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
            "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
            "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
        ]
        return names[nak_num]