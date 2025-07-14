"""
Numerology calculator for various numerological calculations.
"""
from datetime import datetime
from typing import Dict, List


class NumerologyCalculator:
    """Calculate various numerology numbers and their meanings."""
    
    def __init__(self):
        self.number_meanings = self._load_number_meanings()
    
    def calculate_numerology(self, name: str, date_of_birth: datetime) -> Dict:
        """
        Calculate all major numerology numbers.
        
        Args:
            name: Full name of the person
            date_of_birth: Date of birth
        
        Returns:
            Dictionary with all numerology calculations
        """
        # Calculate various numbers
        life_path = self.calculate_life_path_number(date_of_birth)
        destiny = self.calculate_destiny_number(name)
        soul = self.calculate_soul_number(name)
        personality = self.calculate_personality_number(name)
        maturity = self.calculate_maturity_number(life_path, destiny)
        
        # Birthday number
        birthday = self._reduce_to_single_digit(date_of_birth.day)
        
        # Personal year
        personal_year = self.calculate_personal_year(date_of_birth, datetime.now().year)
        
        return {
            "name": name,
            "date_of_birth": date_of_birth.isoformat(),
            "life_path_number": life_path,
            "destiny_number": destiny,
            "soul_number": soul,
            "personality_number": personality,
            "maturity_number": maturity,
            "birthday_number": birthday,
            "personal_year": personal_year,
            "interpretations": {
                "life_path": self._get_life_path_interpretation(life_path),
                "destiny": self._get_destiny_interpretation(destiny),
                "soul": self._get_soul_interpretation(soul),
                "personality": self._get_personality_interpretation(personality),
                "maturity": self._get_maturity_interpretation(maturity),
                "personal_year": self._get_personal_year_interpretation(personal_year)
            },
            "compatibility": self._get_compatibility_numbers(life_path),
            "challenges": self._calculate_challenges(date_of_birth),
            "pinnacles": self._calculate_pinnacles(date_of_birth, life_path)
        }
    
    def calculate_life_path_number(self, date_of_birth: datetime) -> int:
        """Calculate life path number from date of birth."""
        # Add all digits of date
        date_str = date_of_birth.strftime("%d%m%Y")
        total = sum(int(digit) for digit in date_str)
        
        # Keep master numbers 11, 22, 33
        return self._reduce_to_single_digit(total, keep_master=True)
    
    def calculate_destiny_number(self, name: str) -> int:
        """Calculate destiny/expression number from full name."""
        # Letter to number mapping (Pythagorean system)
        letter_values = {
            'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 9,
            'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'O': 6, 'P': 7, 'Q': 8, 'R': 9,
            'S': 1, 'T': 2, 'U': 3, 'V': 4, 'W': 5, 'X': 6, 'Y': 7, 'Z': 8
        }
        
        # Calculate sum of all letters
        total = 0
        for char in name.upper():
            if char in letter_values:
                total += letter_values[char]
        
        return self._reduce_to_single_digit(total, keep_master=True)
    
    def calculate_soul_number(self, name: str) -> int:
        """Calculate soul/heart's desire number from vowels in name."""
        vowels = 'AEIOU'
        letter_values = {
            'A': 1, 'E': 5, 'I': 9, 'O': 6, 'U': 3,
            'Y': 7  # Y is sometimes a vowel
        }
        
        total = 0
        name_upper = name.upper()
        
        for i, char in enumerate(name_upper):
            if char in vowels:
                total += letter_values.get(char, 0)
            # Y is vowel when it's the only vowel sound in syllable
            elif char == 'Y':
                # Simple check: Y is vowel if no other vowel nearby
                if i > 0 and name_upper[i-1] not in vowels:
                    if i < len(name_upper)-1 and name_upper[i+1] not in vowels:
                        total += letter_values['Y']
        
        return self._reduce_to_single_digit(total, keep_master=True)
    
    def calculate_personality_number(self, name: str) -> int:
        """Calculate personality number from consonants in name."""
        consonants = 'BCDFGHJKLMNPQRSTVWXYZ'
        letter_values = {
            'B': 2, 'C': 3, 'D': 4, 'F': 6, 'G': 7, 'H': 8,
            'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'P': 7, 'Q': 8, 'R': 9,
            'S': 1, 'T': 2, 'V': 4, 'W': 5, 'X': 6, 'Y': 7, 'Z': 8
        }
        
        total = 0
        for char in name.upper():
            if char in consonants:
                total += letter_values.get(char, 0)
        
        return self._reduce_to_single_digit(total, keep_master=True)
    
    def calculate_maturity_number(self, life_path: int, destiny: int) -> int:
        """Calculate maturity number from life path and destiny numbers."""
        return self._reduce_to_single_digit(life_path + destiny, keep_master=True)
    
    def calculate_personal_year(self, date_of_birth: datetime, current_year: int) -> int:
        """Calculate personal year number."""
        # Add birth day + birth month + current year
        day = date_of_birth.day
        month = date_of_birth.month
        
        # Reduce current year to single digit
        year_sum = sum(int(digit) for digit in str(current_year))
        year_reduced = self._reduce_to_single_digit(year_sum)
        
        total = day + month + year_reduced
        return self._reduce_to_single_digit(total)
    
    def _reduce_to_single_digit(self, number: int, keep_master: bool = False) -> int:
        """Reduce number to single digit, optionally keeping master numbers."""
        while number > 9:
            if keep_master and number in [11, 22, 33]:
                return number
            number = sum(int(digit) for digit in str(number))
        return number
    
    def _calculate_challenges(self, date_of_birth: datetime) -> List[Dict]:
        """Calculate life challenges."""
        # Extract digits
        day = self._reduce_to_single_digit(date_of_birth.day)
        month = self._reduce_to_single_digit(date_of_birth.month)
        year = self._reduce_to_single_digit(sum(int(d) for d in str(date_of_birth.year)))
        
        # Calculate challenges
        first_challenge = abs(day - month)
        second_challenge = abs(day - year)
        third_challenge = abs(first_challenge - second_challenge)
        fourth_challenge = abs(month - year)
        
        return [
            {"period": "First", "number": first_challenge, "age_range": "0-early 30s"},
            {"period": "Second", "number": second_challenge, "age_range": "early 30s-late 50s"},
            {"period": "Third", "number": third_challenge, "age_range": "late 50s onwards"},
            {"period": "Fourth", "number": fourth_challenge, "age_range": "Lifetime"}
        ]
    
    def _calculate_pinnacles(self, date_of_birth: datetime, life_path: int) -> List[Dict]:
        """Calculate life pinnacles."""
        # Extract digits
        day = self._reduce_to_single_digit(date_of_birth.day)
        month = self._reduce_to_single_digit(date_of_birth.month)
        year = self._reduce_to_single_digit(sum(int(d) for d in str(date_of_birth.year)))
        
        # Calculate pinnacles
        first_pinnacle = self._reduce_to_single_digit(day + month)
        second_pinnacle = self._reduce_to_single_digit(day + year)
        third_pinnacle = self._reduce_to_single_digit(first_pinnacle + second_pinnacle)
        fourth_pinnacle = self._reduce_to_single_digit(month + year)
        
        # Calculate age ranges
        first_age = 36 - life_path
        second_age = first_age + 9
        third_age = second_age + 9
        
        return [
            {"period": "First", "number": first_pinnacle, "age_range": f"0-{first_age}"},
            {"period": "Second", "number": second_pinnacle, "age_range": f"{first_age+1}-{second_age}"},
            {"period": "Third", "number": third_pinnacle, "age_range": f"{second_age+1}-{third_age}"},
            {"period": "Fourth", "number": fourth_pinnacle, "age_range": f"{third_age+1} onwards"}
        ]
    
    def _get_life_path_interpretation(self, number: int) -> str:
        """Get interpretation for life path number."""
        interpretations = {
            1: "The Leader - Independent, pioneering, and innovative. Natural born leader with strong will.",
            2: "The Cooperator - Diplomatic, sensitive, and intuitive. Works well with others.",
            3: "The Communicator - Creative, expressive, and optimistic. Natural entertainer.",
            4: "The Builder - Practical, hardworking, and reliable. Strong sense of order.",
            5: "The Freedom Seeker - Adventurous, versatile, and progressive. Loves freedom and change.",
            6: "The Nurturer - Responsible, caring, and harmonious. Natural counselor and healer.",
            7: "The Seeker - Analytical, intuitive, and spiritual. Seeks truth and wisdom.",
            8: "The Achiever - Ambitious, organized, and efficient. Natural business person.",
            9: "The Humanitarian - Compassionate, generous, and idealistic. Serves humanity.",
            11: "The Intuitive - Highly intuitive, spiritual, and inspiring. Master number of illumination.",
            22: "The Master Builder - Visionary, practical, and powerful. Can turn dreams into reality.",
            33: "The Master Teacher - Selfless, devoted, and caring. Highest level of love and compassion."
        }
        return interpretations.get(number, "Unique path of self-discovery")
    
    def _get_destiny_interpretation(self, number: int) -> str:
        """Get interpretation for destiny number."""
        interpretations = {
            1: "Leadership and innovation. Destined to be original and independent.",
            2: "Partnership and cooperation. Destined to work with others harmoniously.",
            3: "Self-expression and creativity. Destined to inspire and entertain.",
            4: "Building and organizing. Destined to create lasting foundations.",
            5: "Freedom and adventure. Destined to experience and promote change.",
            6: "Service and responsibility. Destined to nurture and heal.",
            7: "Knowledge and wisdom. Destined to seek and share truth.",
            8: "Material mastery. Destined to achieve and manage resources.",
            9: "Universal love. Destined to serve humanity selflessly.",
            11: "Spiritual inspiration. Destined to uplift and enlighten others.",
            22: "Master manifestation. Destined to build dreams into reality.",
            33: "Master compassion. Destined to love and heal unconditionally."
        }
        return interpretations.get(number, "Unique destiny awaits")
    
    def _get_soul_interpretation(self, number: int) -> str:
        """Get interpretation for soul number."""
        interpretations = {
            1: "Desires independence and leadership. Wants to be first and unique.",
            2: "Desires harmony and partnership. Wants peace and cooperation.",
            3: "Desires joy and creativity. Wants to express and communicate.",
            4: "Desires stability and order. Wants security and tradition.",
            5: "Desires freedom and variety. Wants adventure and experience.",
            6: "Desires love and family. Wants to care for others.",
            7: "Desires knowledge and solitude. Wants to understand life's mysteries.",
            8: "Desires success and recognition. Wants material achievement.",
            9: "Desires to help humanity. Wants to make the world better.",
            11: "Desires spiritual growth. Wants to inspire and uplift.",
            22: "Desires to build something lasting. Wants to leave a legacy.",
            33: "Desires to heal and teach. Wants to spread love."
        }
        return interpretations.get(number, "Unique soul desires")
    
    def _get_personality_interpretation(self, number: int) -> str:
        """Get interpretation for personality number."""
        interpretations = {
            1: "Appears confident and independent. Projects leadership.",
            2: "Appears gentle and cooperative. Projects diplomacy.",
            3: "Appears friendly and outgoing. Projects enthusiasm.",
            4: "Appears practical and reliable. Projects stability.",
            5: "Appears dynamic and adventurous. Projects freedom.",
            6: "Appears caring and responsible. Projects warmth.",
            7: "Appears mysterious and wise. Projects depth.",
            8: "Appears successful and powerful. Projects authority.",
            9: "Appears compassionate and wise. Projects universality.",
            11: "Appears inspired and intuitive. Projects spirituality.",
            22: "Appears capable and visionary. Projects mastery.",
            33: "Appears loving and wise. Projects divine love."
        }
        return interpretations.get(number, "Unique personality traits")
    
    def _get_maturity_interpretation(self, number: int) -> str:
        """Get interpretation for maturity number."""
        return f"At maturity, you will embody the qualities of number {number}. This becomes more prominent after age 40."
    
    def _get_personal_year_interpretation(self, number: int) -> str:
        """Get interpretation for personal year."""
        interpretations = {
            1: "New beginnings. Start new projects and assert independence.",
            2: "Cooperation and patience. Focus on relationships and partnerships.",
            3: "Creative expression. Enjoy life and express yourself.",
            4: "Hard work and building. Lay foundations for the future.",
            5: "Change and freedom. Embrace new experiences and travel.",
            6: "Responsibility and family. Focus on home and relationships.",
            7: "Inner reflection. Spiritual growth and self-analysis.",
            8: "Material success. Focus on career and financial goals.",
            9: "Completion and release. Let go of what no longer serves."
        }
        return interpretations.get(number, "A year of growth and learning")
    
    def _get_compatibility_numbers(self, life_path: int) -> Dict[str, List[int]]:
        """Get compatible numbers for relationships."""
        compatibility = {
            1: {"natural_match": [1, 5, 7], "compatible": [3, 9], "challenging": [2, 4, 6, 8]},
            2: {"natural_match": [2, 4, 8], "compatible": [6, 9], "challenging": [1, 3, 5, 7]},
            3: {"natural_match": [3, 6, 9], "compatible": [1, 5], "challenging": [2, 4, 7, 8]},
            4: {"natural_match": [2, 4, 8], "compatible": [6, 7], "challenging": [1, 3, 5, 9]},
            5: {"natural_match": [1, 5, 7], "compatible": [3, 9], "challenging": [2, 4, 6, 8]},
            6: {"natural_match": [3, 6, 9], "compatible": [2, 4, 8], "challenging": [1, 5, 7]},
            7: {"natural_match": [1, 5, 7], "compatible": [4], "challenging": [2, 3, 6, 8, 9]},
            8: {"natural_match": [2, 4, 8], "compatible": [6], "challenging": [1, 3, 5, 7, 9]},
            9: {"natural_match": [3, 6, 9], "compatible": [1, 2, 5], "challenging": [4, 7, 8]},
            11: {"natural_match": [11, 22, 33], "compatible": [2, 4], "challenging": [1, 5, 7]},
            22: {"natural_match": [11, 22, 33], "compatible": [2, 4, 8], "challenging": [3, 5, 9]},
            33: {"natural_match": [11, 22, 33], "compatible": [3, 6, 9], "challenging": [1, 4, 7]}
        }
        return compatibility.get(life_path, {"natural_match": [], "compatible": [], "challenging": []})
    
    def _load_number_meanings(self) -> Dict:
        """Load detailed number meanings."""
        return {
            "master_numbers": [11, 22, 33],
            "karmic_debt_numbers": [13, 14, 16, 19],
            "angel_numbers": [111, 222, 333, 444, 555, 666, 777, 888, 999]
        }