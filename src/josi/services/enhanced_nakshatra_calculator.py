# src/josi/services/enhanced_nakshatra_calculator.py

from typing import Dict, List, Optional, Tuple

class EnhancedNakshatraCalculator:
    """
    Enhanced nakshatra calculations with complete pada details.
    
    This implementation provides detailed nakshatra information including
    pada (quarter) calculations, rulers, deities, and navamsa mappings.
    """
    
    def __init__(self):
        # Complete nakshatra data with all attributes
        self.nakshatra_data = [
            {
                'name': 'Ashwini',
                'ruler': 'Ketu',
                'deity': 'Ashwini Kumaras',
                'symbol': 'Horse Head',
                'padas': ['Aries', 'Taurus', 'Gemini', 'Cancer'],
                'qualities': ['Swift', 'Healing', 'Pioneer'],
                'gana': 'Deva'
            },
            {
                'name': 'Bharani',
                'ruler': 'Venus',
                'deity': 'Yama',
                'symbol': 'Yoni',
                'padas': ['Leo', 'Virgo', 'Libra', 'Scorpio'],
                'qualities': ['Restraint', 'Discipline', 'Transformation'],
                'gana': 'Manushya'
            },
            {
                'name': 'Krittika',
                'ruler': 'Sun',
                'deity': 'Agni',
                'symbol': 'Razor',
                'padas': ['Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'],
                'qualities': ['Cutting', 'Purification', 'Leadership'],
                'gana': 'Rakshasa'
            },
            {
                'name': 'Rohini',
                'ruler': 'Moon',
                'deity': 'Brahma',
                'symbol': 'Cart',
                'padas': ['Aries', 'Taurus', 'Gemini', 'Cancer'],
                'qualities': ['Growth', 'Beauty', 'Fertility'],
                'gana': 'Manushya'
            },
            {
                'name': 'Mrigashira',
                'ruler': 'Mars',
                'deity': 'Soma',
                'symbol': 'Deer Head',
                'padas': ['Leo', 'Virgo', 'Libra', 'Scorpio'],
                'qualities': ['Searching', 'Gentle', 'Curious'],
                'gana': 'Deva'
            },
            {
                'name': 'Ardra',
                'ruler': 'Rahu',
                'deity': 'Rudra',
                'symbol': 'Teardrop',
                'padas': ['Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'],
                'qualities': ['Storm', 'Transformation', 'Renewal'],
                'gana': 'Manushya'
            },
            {
                'name': 'Punarvasu',
                'ruler': 'Jupiter',
                'deity': 'Aditi',
                'symbol': 'Bow and Quiver',
                'padas': ['Aries', 'Taurus', 'Gemini', 'Cancer'],
                'qualities': ['Return', 'Renewal', 'Safety'],
                'gana': 'Deva'
            },
            {
                'name': 'Pushya',
                'ruler': 'Saturn',
                'deity': 'Brihaspati',
                'symbol': 'Cow Udder',
                'padas': ['Leo', 'Virgo', 'Libra', 'Scorpio'],
                'qualities': ['Nourishment', 'Protection', 'Teaching'],
                'gana': 'Deva'
            },
            {
                'name': 'Ashlesha',
                'ruler': 'Mercury',
                'deity': 'Nagas',
                'symbol': 'Coiled Snake',
                'padas': ['Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'],
                'qualities': ['Embracing', 'Mystical', 'Cunning'],
                'gana': 'Rakshasa'
            },
            {
                'name': 'Magha',
                'ruler': 'Ketu',
                'deity': 'Pitris',
                'symbol': 'Throne',
                'padas': ['Aries', 'Taurus', 'Gemini', 'Cancer'],
                'qualities': ['Authority', 'Ancestry', 'Power'],
                'gana': 'Rakshasa'
            },
            {
                'name': 'Purva Phalguni',
                'ruler': 'Venus',
                'deity': 'Bhaga',
                'symbol': 'Hammock',
                'padas': ['Leo', 'Virgo', 'Libra', 'Scorpio'],
                'qualities': ['Relaxation', 'Pleasure', 'Creativity'],
                'gana': 'Manushya'
            },
            {
                'name': 'Uttara Phalguni',
                'ruler': 'Sun',
                'deity': 'Aryaman',
                'symbol': 'Bed',
                'padas': ['Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'],
                'qualities': ['Patronage', 'Agreements', 'Prosperity'],
                'gana': 'Manushya'
            },
            {
                'name': 'Hasta',
                'ruler': 'Moon',
                'deity': 'Savitar',
                'symbol': 'Hand',
                'padas': ['Aries', 'Taurus', 'Gemini', 'Cancer'],
                'qualities': ['Skill', 'Craft', 'Dexterity'],
                'gana': 'Deva'
            },
            {
                'name': 'Chitra',
                'ruler': 'Mars',
                'deity': 'Tvashtar',
                'symbol': 'Pearl',
                'padas': ['Leo', 'Virgo', 'Libra', 'Scorpio'],
                'qualities': ['Beauty', 'Creation', 'Brilliance'],
                'gana': 'Rakshasa'
            },
            {
                'name': 'Swati',
                'ruler': 'Rahu',
                'deity': 'Vayu',
                'symbol': 'Coral',
                'padas': ['Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'],
                'qualities': ['Independence', 'Movement', 'Trade'],
                'gana': 'Deva'
            },
            {
                'name': 'Vishakha',
                'ruler': 'Jupiter',
                'deity': 'Indra-Agni',
                'symbol': 'Archway',
                'padas': ['Aries', 'Taurus', 'Gemini', 'Cancer'],
                'qualities': ['Goal-oriented', 'Determination', 'Achievement'],
                'gana': 'Rakshasa'
            },
            {
                'name': 'Anuradha',
                'ruler': 'Saturn',
                'deity': 'Mitra',
                'symbol': 'Lotus',
                'padas': ['Leo', 'Virgo', 'Libra', 'Scorpio'],
                'qualities': ['Friendship', 'Devotion', 'Success'],
                'gana': 'Deva'
            },
            {
                'name': 'Jyeshtha',
                'ruler': 'Mercury',
                'deity': 'Indra',
                'symbol': 'Umbrella',
                'padas': ['Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'],
                'qualities': ['Seniority', 'Protection', 'Courage'],
                'gana': 'Rakshasa'
            },
            {
                'name': 'Mula',
                'ruler': 'Ketu',
                'deity': 'Nirriti',
                'symbol': 'Roots',
                'padas': ['Aries', 'Taurus', 'Gemini', 'Cancer'],
                'qualities': ['Foundation', 'Investigation', 'Destruction'],
                'gana': 'Rakshasa'
            },
            {
                'name': 'Purva Ashadha',
                'ruler': 'Venus',
                'deity': 'Apas',
                'symbol': 'Fan',
                'padas': ['Leo', 'Virgo', 'Libra', 'Scorpio'],
                'qualities': ['Invincibility', 'Purification', 'Victory'],
                'gana': 'Manushya'
            },
            {
                'name': 'Uttara Ashadha',
                'ruler': 'Sun',
                'deity': 'Vishwadevas',
                'symbol': 'Elephant Tusk',
                'padas': ['Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'],
                'qualities': ['Victory', 'Leadership', 'Universal'],
                'gana': 'Manushya'
            },
            {
                'name': 'Shravana',
                'ruler': 'Moon',
                'deity': 'Vishnu',
                'symbol': 'Ear',
                'padas': ['Aries', 'Taurus', 'Gemini', 'Cancer'],
                'qualities': ['Listening', 'Learning', 'Connection'],
                'gana': 'Deva'
            },
            {
                'name': 'Dhanishtha',
                'ruler': 'Mars',
                'deity': 'Eight Vasus',
                'symbol': 'Drum',
                'padas': ['Leo', 'Virgo', 'Libra', 'Scorpio'],
                'qualities': ['Wealth', 'Music', 'Abundance'],
                'gana': 'Rakshasa'
            },
            {
                'name': 'Shatabhisha',
                'ruler': 'Rahu',
                'deity': 'Varuna',
                'symbol': 'Circle',
                'padas': ['Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'],
                'qualities': ['Healing', 'Secrecy', 'Hundred Healers'],
                'gana': 'Rakshasa'
            },
            {
                'name': 'Purva Bhadrapada',
                'ruler': 'Jupiter',
                'deity': 'Aja Ekapada',
                'symbol': 'Sword',
                'padas': ['Aries', 'Taurus', 'Gemini', 'Cancer'],
                'qualities': ['Fire', 'Transformation', 'Penance'],
                'gana': 'Manushya'
            },
            {
                'name': 'Uttara Bhadrapada',
                'ruler': 'Saturn',
                'deity': 'Ahir Budhnya',
                'symbol': 'Twins',
                'padas': ['Leo', 'Virgo', 'Libra', 'Scorpio'],
                'qualities': ['Depth', 'Wisdom', 'Serpent of Deep'],
                'gana': 'Manushya'
            },
            {
                'name': 'Revati',
                'ruler': 'Mercury',
                'deity': 'Pushan',
                'symbol': 'Fish',
                'padas': ['Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'],
                'qualities': ['Journey', 'Nourishment', 'Completion'],
                'gana': 'Deva'
            }
        ]
        
        # Quick lookup dictionaries
        self._build_lookup_tables()
    
    def _build_lookup_tables(self):
        """Build lookup tables for efficient access."""
        self.nakshatra_by_name = {n['name']: n for n in self.nakshatra_data}
        self.nakshatra_by_index = {i: n for i, n in enumerate(self.nakshatra_data)}
    
    def calculate_nakshatra_pada_details(self, longitude: float) -> Dict:
        """
        Calculate complete nakshatra pada information.
        
        Args:
            longitude: Sidereal longitude in degrees (0-360)
            
        Returns:
            Detailed nakshatra and pada information
        """
        # Each nakshatra is 13°20' (800 minutes or 13.3333... degrees)
        nakshatra_span = 360.0 / 27
        
        # Find nakshatra index
        nakshatra_index = int(longitude / nakshatra_span)
        
        # Degrees within the nakshatra
        degrees_in_nakshatra = longitude % nakshatra_span
        
        # Each pada is 3°20' (200 minutes or 3.3333... degrees)
        pada_span = nakshatra_span / 4
        pada = int(degrees_in_nakshatra / pada_span) + 1
        
        # Ensure pada is between 1 and 4
        pada = min(4, max(1, pada))
        
        # Get nakshatra data
        nakshatra_info = self.nakshatra_data[nakshatra_index]
        
        # Calculate exact position in pada
        degrees_in_pada = degrees_in_nakshatra % pada_span
        pada_percentage = (degrees_in_pada / pada_span) * 100
        
        # Minutes and seconds
        total_minutes = degrees_in_nakshatra * 60
        minutes = int(total_minutes)
        seconds = int((total_minutes - minutes) * 60)
        
        return {
            'nakshatra': nakshatra_info['name'],
            'nakshatra_index': nakshatra_index,
            'pada': pada,
            'ruler': nakshatra_info['ruler'],
            'deity': nakshatra_info['deity'],
            'symbol': nakshatra_info['symbol'],
            'gana': nakshatra_info['gana'],
            'qualities': nakshatra_info['qualities'],
            'navamsa_sign': nakshatra_info['padas'][pada - 1],
            'pada_percentage': pada_percentage,
            'degrees_in_nakshatra': degrees_in_nakshatra,
            'degrees_in_pada': degrees_in_pada,
            'position_in_nakshatra': f"{int(degrees_in_nakshatra)}°{minutes % 60}'{seconds}\"",
            'nakshatra_lord': nakshatra_info['ruler'],  # Alternative name
            'nakshatra_number': nakshatra_index + 1  # 1-based numbering
        }
    
    def get_nakshatra_compatibility(self, nakshatra1: str, nakshatra2: str) -> Dict:
        """
        Calculate compatibility between two nakshatras.
        
        Args:
            nakshatra1: Name of first nakshatra
            nakshatra2: Name of second nakshatra
            
        Returns:
            Compatibility information
        """
        n1 = self.nakshatra_by_name.get(nakshatra1)
        n2 = self.nakshatra_by_name.get(nakshatra2)
        
        if not n1 or not n2:
            return {'error': 'Invalid nakshatra name'}
        
        # Gana compatibility
        gana_compatibility = {
            ('Deva', 'Deva'): 6,
            ('Deva', 'Manushya'): 5,
            ('Deva', 'Rakshasa'): 1,
            ('Manushya', 'Deva'): 5,
            ('Manushya', 'Manushya'): 6,
            ('Manushya', 'Rakshasa'): 0,
            ('Rakshasa', 'Deva'): 1,
            ('Rakshasa', 'Manushya'): 0,
            ('Rakshasa', 'Rakshasa'): 6
        }
        
        gana_score = gana_compatibility.get((n1['gana'], n2['gana']), 0)
        
        return {
            'nakshatra1': nakshatra1,
            'nakshatra2': nakshatra2,
            'gana_compatibility': gana_score,
            'gana1': n1['gana'],
            'gana2': n2['gana'],
            'max_gana_score': 6
        }
    
    def get_nakshatra_by_degree(self, longitude: float) -> Dict:
        """
        Get nakshatra information for a given longitude.
        
        Args:
            longitude: Sidereal longitude in degrees
            
        Returns:
            Basic nakshatra information
        """
        nakshatra_span = 360.0 / 27
        nakshatra_index = int(longitude / nakshatra_span)
        
        return self.nakshatra_data[nakshatra_index]
    
    def calculate_nakshatra_lord_sequence(self, start_nakshatra: str, count: int = 9) -> List[str]:
        """
        Calculate the sequence of nakshatra lords from a starting nakshatra.
        
        Args:
            start_nakshatra: Starting nakshatra name
            count: Number of lords to return
            
        Returns:
            List of nakshatra lords in sequence
        """
        # Find starting index
        start_index = None
        for i, n in enumerate(self.nakshatra_data):
            if n['name'] == start_nakshatra:
                start_index = i
                break
        
        if start_index is None:
            return []
        
        lords = []
        for i in range(count):
            nakshatra_index = (start_index + i) % 27
            lords.append(self.nakshatra_data[nakshatra_index]['ruler'])
        
        return lords
    
    def get_all_nakshatras_by_ruler(self, ruler: str) -> List[Dict]:
        """
        Get all nakshatras ruled by a specific planet.
        
        Args:
            ruler: Planet name (e.g., 'Mars', 'Venus')
            
        Returns:
            List of nakshatras ruled by the planet
        """
        return [n for n in self.nakshatra_data if n['ruler'] == ruler]