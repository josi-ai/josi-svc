"""
Nakshatra Utilities
Common utilities for nakshatra calculations and ruler mappings
"""

from typing import Dict, Tuple


class NakshatraUtils:
    """Utilities for nakshatra calculations and information."""
    
    NAKSHATRA_RULERS = {
        # Complete mapping with all variations
        'Ashwini': 'Ketu', 'Aswini': 'Ketu', 'ASWINI': 'Ketu',
        'Bharani': 'Venus', 'BHARANI': 'Venus',
        'Krittika': 'Sun', 'Krithika': 'Sun', 'KRITHIKA': 'Sun',
        'Rohini': 'Moon', 'ROHINI': 'Moon',
        'Mrigashira': 'Mars', 'Mrigasira': 'Mars', 'MRIGASIRA': 'Mars', 'MRIGASIR': 'Mars',
        'Ardra': 'Rahu', 'Aridra': 'Rahu', 'ARIDRA': 'Rahu',
        'Punarvasu': 'Jupiter', 'Punarvas': 'Jupiter', 'PUNARVAS': 'Jupiter',
        'Pushya': 'Saturn', 'Pushyami': 'Saturn', 'PUSHYAMI': 'Saturn',
        'Ashlesha': 'Mercury', 'Aslesha': 'Mercury', 'ASLESHA': 'Mercury',
        'Magha': 'Ketu', 'Makha': 'Ketu', 'MAKHA': 'Ketu',
        'Purva Phalguni': 'Venus', 'Purvaphalguni': 'Venus', 'Purvapha': 'Venus', 'PURVAPHA': 'Venus', 'PURAPHAL': 'Venus',
        'Uttara Phalguni': 'Sun', 'Uttaraphalguni': 'Sun', 'Uttrapha': 'Sun', 'UTTRAPHA': 'Sun', 'UTTRAPHAL': 'Sun',
        'Hasta': 'Moon', 'HASTA': 'Moon',
        'Chitra': 'Mars', 'Chithra': 'Mars', 'CHITHRA': 'Mars',
        'Swati': 'Rahu', 'Swathi': 'Rahu', 'SWATHI': 'Rahu',
        'Vishakha': 'Jupiter', 'Visakha': 'Jupiter', 'VISAKHA': 'Jupiter',
        'Anuradha': 'Saturn', 'ANURADHA': 'Saturn',
        'Jyeshtha': 'Mercury', 'Jyeshta': 'Mercury', 'JYESHTA': 'Mercury',
        'Mula': 'Ketu', 'Moola': 'Ketu', 'MOOLA': 'Ketu',
        'Purva Ashadha': 'Venus', 'Purvashadha': 'Venus', 'Purashad': 'Venus', 'PURASHAD': 'Venus',
        'Uttara Ashadha': 'Sun', 'Uttarashadha': 'Sun', 'Uttrasad': 'Sun', 'UTTRASAD': 'Sun', 'UTTRASADA': 'Sun',
        'Shravana': 'Moon', 'Sravana': 'Moon', 'SRAVANA': 'Moon',
        'Dhanishta': 'Mars', 'Dhanista': 'Mars', 'DHANISTA': 'Mars',
        'Shatabhisha': 'Rahu', 'Satabhis': 'Rahu', 'SATABHIS': 'Rahu',
        'Purva Bhadrapada': 'Jupiter', 'Purvabhadra': 'Jupiter', 'Purvbdra': 'Jupiter', 'PURVBDRA': 'Jupiter',
        'Uttara Bhadrapada': 'Saturn', 'Uttarabhadra': 'Saturn', 'Uttrbdra': 'Saturn', 'UTTRBDRA': 'Saturn',
        'Revati': 'Mercury', 'Revathi': 'Mercury', 'REVATHI': 'Mercury'
    }
    
    # Ruler to short form mapping for display
    RULER_SHORT_FORMS = {
        'Ketu': 'KETU',
        'Venus': 'SUKR',
        'Sun': 'SURY',
        'Moon': 'CHAN',
        'Mars': 'KUJA',
        'Rahu': 'RAHU',
        'Jupiter': 'GURU',
        'Saturn': 'SANI',
        'Mercury': 'BUDH'
    }
    
    @classmethod
    def get_nakshatra_ruler(cls, nakshatra: str) -> str:
        """Get ruler of a nakshatra, handling variations."""
        # Try exact match first
        if nakshatra in cls.NAKSHATRA_RULERS:
            return cls.NAKSHATRA_RULERS[nakshatra]
        
        # Try case-insensitive match
        nakshatra_upper = nakshatra.upper()
        for key, ruler in cls.NAKSHATRA_RULERS.items():
            if key.upper() == nakshatra_upper:
                return ruler
        
        # Try partial match
        for key, ruler in cls.NAKSHATRA_RULERS.items():
            if nakshatra_upper in key.upper() or key.upper() in nakshatra_upper:
                return ruler
        
        return 'Unknown'
    
    @classmethod
    def get_ruler_short_form(cls, ruler: str) -> str:
        """Get short form of ruler name for display."""
        return cls.RULER_SHORT_FORMS.get(ruler, ruler[:4].upper())
    
    @classmethod
    def calculate_nakshatra_pada(cls, longitude: float) -> Tuple[str, int, str]:
        """
        Calculate nakshatra, pada, and ruler from longitude.
        
        Returns:
            Tuple of (nakshatra_name, pada, ruler)
        """
        # Each nakshatra is 13°20' = 13.333... degrees
        nakshatra_span = 360.0 / 27.0
        pada_span = nakshatra_span / 4.0
        
        # Standard nakshatra names
        nakshatras = [
            "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
            "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni",
            "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha",
            "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha",
            "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada",
            "Uttara Bhadrapada", "Revati"
        ]
        
        # Calculate nakshatra index
        nak_index = int(longitude / nakshatra_span)
        nakshatra_name = nakshatras[nak_index]
        
        # Calculate pada
        position_in_nak = longitude % nakshatra_span
        pada = int(position_in_nak / pada_span) + 1
        
        # Get ruler
        ruler = cls.get_nakshatra_ruler(nakshatra_name)
        
        return nakshatra_name, pada, ruler