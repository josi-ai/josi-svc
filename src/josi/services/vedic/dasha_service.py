"""
Vimshottari Dasha system calculator for Vedic astrology.
120-year cycle based on Moon's nakshatra position at birth.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import math


class VimshottariDashaCalculator:
    """Calculate Vimshottari Dasha periods."""
    
    # Dasha lords in order with their period in years
    DASHA_ORDER = [
        ("Ketu", 7),
        ("Venus", 20),
        ("Sun", 6),
        ("Moon", 10),
        ("Mars", 7),
        ("Rahu", 18),
        ("Jupiter", 16),
        ("Saturn", 19),
        ("Mercury", 17)
    ]
    
    # Total cycle duration
    TOTAL_YEARS = 120
    
    # Nakshatra rulers (repeating pattern)
    NAKSHATRA_RULERS = [
        "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu",
        "Jupiter", "Saturn", "Mercury", "Ketu", "Venus", "Sun",
        "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
        "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu",
        "Jupiter", "Saturn", "Mercury"
    ]
    
    def calculate_dasha_periods(
        self,
        birth_datetime: datetime,
        moon_longitude: float,
        include_antardashas: bool = True,
        include_pratyantardashas: bool = False,
        include_sookshma: bool = False,
        include_prana: bool = False
    ) -> Dict:
        """
        Calculate Vimshottari Dasha periods from birth.
        
        Args:
            birth_datetime: Date and time of birth
            moon_longitude: Sidereal longitude of Moon at birth
            include_antardashas: Include sub-periods (level 2)
            include_pratyantardashas: Include sub-sub-periods (level 3)
            include_sookshma: Include sookshma periods (level 4)
            include_prana: Include prana periods (level 5)

        Returns:
            Dictionary with dasha periods and current dasha
        """
        # Calculate birth nakshatra
        nakshatra_num = int(moon_longitude / 13.333333)
        nakshatra_progress = (moon_longitude % 13.333333) / 13.333333
        
        # Get dasha lord at birth
        birth_dasha_lord = self.NAKSHATRA_RULERS[nakshatra_num]
        
        # Calculate elapsed portion of birth dasha
        dasha_index = self._get_dasha_index(birth_dasha_lord)
        birth_dasha_years = self.DASHA_ORDER[dasha_index][1]
        elapsed_years = nakshatra_progress * birth_dasha_years
        remaining_years = birth_dasha_years - elapsed_years
        
        # Calculate all mahadasha periods
        mahadashas = self._calculate_mahadashas(
            birth_datetime, dasha_index, remaining_years
        )
        
        # Get current dasha
        if birth_datetime.tzinfo is not None:
            # Use UTC if birth_datetime is timezone-aware
            current_date = datetime.now(birth_datetime.tzinfo)
        else:
            current_date = datetime.now()
        current_dasha = self._get_current_dasha(mahadashas, current_date)
        
        # Calculate antardashas for current mahadasha if requested
        if include_antardashas and current_dasha:
            current_mahadasha = current_dasha["mahadasha"]
            for i, dasha in enumerate(mahadashas):
                if dasha["planet"] == current_mahadasha["planet"]:
                    antardashas = self._calculate_antardashas(
                        dasha["start_date"],
                        dasha["planet"],
                        dasha["duration_years"]
                    )
                    mahadashas[i]["antardashas"] = antardashas
                    
                    # Get current antardasha
                    current_antardasha = self._get_current_period(
                        antardashas, current_date
                    )
                    current_dasha["antardasha"] = current_antardasha
                    
                    # Calculate pratyantardashas if requested
                    if include_pratyantardashas and current_antardasha:
                        for j, antardasha in enumerate(antardashas):
                            if antardasha["planet"] == current_antardasha["planet"]:
                                pratyantardashas = self._calculate_pratyantardashas(
                                    antardasha["start_date"],
                                    current_mahadasha["planet"],
                                    antardasha["planet"],
                                    antardasha["duration_days"] / 365.25
                                )
                                antardashas[j]["pratyantardashas"] = pratyantardashas

                                # Get current pratyantardasha
                                current_pratyantardasha = self._get_current_period(
                                    pratyantardashas, current_date
                                )
                                current_dasha["pratyantardasha"] = current_pratyantardasha

                                # Calculate sookshma if requested
                                if include_sookshma and current_pratyantardasha:
                                    for k, pratyantar in enumerate(pratyantardashas):
                                        if pratyantar["planet"] == current_pratyantardasha["planet"]:
                                            sookshmas = self._calculate_sookshma(
                                                pratyantar["start_date"],
                                                pratyantar["planet"],
                                                pratyantar["duration_days"] / 365.25
                                            )
                                            pratyantardashas[k]["sookshmas"] = sookshmas

                                            # Get current sookshma
                                            current_sookshma = self._get_current_period(
                                                sookshmas, current_date
                                            )
                                            current_dasha["sookshma"] = current_sookshma

                                            # Calculate prana if requested
                                            if include_prana and current_sookshma:
                                                for m, sookshma in enumerate(sookshmas):
                                                    if sookshma["planet"] == current_sookshma["planet"]:
                                                        pranas = self._calculate_prana(
                                                            sookshma["start_date"],
                                                            sookshma["planet"],
                                                            sookshma["duration_days"] / 365.25
                                                        )
                                                        sookshmas[m]["pranas"] = pranas

                                                        # Get current prana
                                                        current_prana = self._get_current_period(
                                                            pranas, current_date
                                                        )
                                                        current_dasha["prana"] = current_prana
                                                        break
                                            break
                    break
        
        # Calculate future predictions based on upcoming dashas
        predictions = self._generate_dasha_predictions(current_dasha, mahadashas)
        
        # No need to clean up - custom JSON serializer handles datetime objects
        
        return {
            "birth_details": {
                "nakshatra_number": nakshatra_num + 1,
                "nakshatra_name": self._get_nakshatra_name(nakshatra_num),
                "nakshatra_progress": round(nakshatra_progress * 100, 2),
                "birth_dasha_lord": birth_dasha_lord,
                "elapsed_at_birth": round(elapsed_years, 2)
            },
            "current_dasha": current_dasha,
            "mahadashas": mahadashas,
            "life_events": self._predict_life_events(mahadashas),
            "predictions": predictions
        }
    
    def _get_dasha_index(self, planet: str) -> int:
        """Get index of planet in dasha order."""
        for i, (p, _) in enumerate(self.DASHA_ORDER):
            if p == planet:
                return i
        return 0
    
    def _calculate_mahadashas(
        self,
        birth_datetime: datetime,
        start_index: int,
        first_dasha_remaining: float
    ) -> List[Dict]:
        """Calculate all mahadasha periods from birth."""
        mahadashas = []
        current_date = birth_datetime
        
        # First, add the remaining portion of birth dasha
        first_planet, full_years = self.DASHA_ORDER[start_index]
        first_end_date = current_date + timedelta(days=first_dasha_remaining * 365.25)
        
        mahadashas.append({
            "planet": first_planet,
            "start_date": current_date,
            "end_date": first_end_date,
            "duration_years": first_dasha_remaining,
            "duration_days": int(first_dasha_remaining * 365.25),
            "is_partial": True
        })
        
        current_date = first_end_date
        
        # Add complete dashas for 120+ years
        cycles = 0
        while cycles < 2:  # Cover ~240 years
            for i in range(9):
                index = (start_index + 1 + i) % 9
                planet, years = self.DASHA_ORDER[index]
                
                end_date = current_date + timedelta(days=years * 365.25)
                
                mahadashas.append({
                    "planet": planet,
                    "start_date": current_date,
                    "end_date": end_date,
                    "duration_years": years,
                    "duration_days": int(years * 365.25),
                    "is_partial": False
                })
                
                current_date = end_date
                
                if index == 8:
                    cycles += 1
        
        return mahadashas
    
    def _calculate_antardashas(
        self,
        mahadasha_start: datetime,
        mahadasha_lord: str,
        mahadasha_years: float
    ) -> List[Dict]:
        """Calculate antardasha (sub-periods) within a mahadasha."""
        antardashas = []
        current_date = mahadasha_start
        
        # Find starting index
        start_index = self._get_dasha_index(mahadasha_lord)
        
        # Total days in mahadasha
        total_days = mahadasha_years * 365.25
        
        # Calculate each antardasha
        for i in range(9):
            index = (start_index + i) % 9
            planet, planet_years = self.DASHA_ORDER[index]
            
            # Antardasha duration = (Planet years * Mahadasha years) / 120
            antardasha_years = (planet_years * mahadasha_years) / 120
            antardasha_days = antardasha_years * 365.25
            
            end_date = current_date + timedelta(days=antardasha_days)
            
            antardashas.append({
                "planet": planet,
                "start_date": current_date,
                "end_date": end_date,
                "duration_years": antardasha_years,
                "duration_days": int(antardasha_days)
            })
            
            current_date = end_date
        
        return antardashas
    
    def _calculate_pratyantardashas(
        self,
        antardasha_start: datetime,
        mahadasha_lord: str,
        antardasha_lord: str,
        antardasha_years: float
    ) -> List[Dict]:
        """Calculate pratyantardasha (sub-sub-periods)."""
        pratyantardashas = []
        current_date = antardasha_start
        
        # Find starting index
        start_index = self._get_dasha_index(antardasha_lord)
        
        # Calculate each pratyantardasha
        for i in range(9):
            index = (start_index + i) % 9
            planet, planet_years = self.DASHA_ORDER[index]
            
            # Pratyantardasha duration
            pratyantardasha_years = (planet_years * antardasha_years) / 120
            pratyantardasha_days = pratyantardasha_years * 365.25
            
            end_date = current_date + timedelta(days=pratyantardasha_days)
            
            pratyantardashas.append({
                "planet": planet,
                "start_date": current_date,
                "end_date": end_date,
                "duration_years": pratyantardasha_years,
                "duration_days": int(pratyantardasha_days)
            })
            
            current_date = end_date
        
        return pratyantardashas
    
    def _calculate_sookshma(
        self,
        pratyantardasha_start: datetime,
        pratyantardasha_lord: str,
        pratyantardasha_years: float
    ) -> List[Dict]:
        """Calculate sookshma (level 4) sub-periods within a pratyantardasha."""
        sookshmas = []
        current_date = pratyantardasha_start

        # Find starting index
        start_index = self._get_dasha_index(pratyantardasha_lord)

        # Calculate each sookshma
        for i in range(9):
            index = (start_index + i) % 9
            planet, planet_years = self.DASHA_ORDER[index]

            # Sookshma duration = (planet_years * pratyantardasha_years) / 120
            sookshma_years = (planet_years * pratyantardasha_years) / 120
            sookshma_days = sookshma_years * 365.25

            end_date = current_date + timedelta(days=sookshma_days)

            sookshmas.append({
                "planet": planet,
                "start_date": current_date,
                "end_date": end_date,
                "duration_years": sookshma_years,
                "duration_days": int(sookshma_days)
            })

            current_date = end_date

        return sookshmas

    def _calculate_prana(
        self,
        sookshma_start: datetime,
        sookshma_lord: str,
        sookshma_years: float
    ) -> List[Dict]:
        """Calculate prana (level 5) sub-periods within a sookshma."""
        pranas = []
        current_date = sookshma_start

        # Find starting index
        start_index = self._get_dasha_index(sookshma_lord)

        # Calculate each prana
        for i in range(9):
            index = (start_index + i) % 9
            planet, planet_years = self.DASHA_ORDER[index]

            # Prana duration = (planet_years * sookshma_years) / 120
            prana_years = (planet_years * sookshma_years) / 120
            prana_days = prana_years * 365.25

            end_date = current_date + timedelta(days=prana_days)

            pranas.append({
                "planet": planet,
                "start_date": current_date,
                "end_date": end_date,
                "duration_years": prana_years,
                "duration_days": int(prana_days)
            })

            current_date = end_date

        return pranas

    def _get_current_dasha(self, mahadashas: List[Dict], current_date: datetime) -> Dict:
        """Get current dasha periods."""
        current_mahadasha = self._get_current_period(mahadashas, current_date)
        
        if not current_mahadasha:
            return None
        
        return {
            "mahadasha": current_mahadasha,
            "description": self._get_dasha_description(current_mahadasha["planet"])
        }
    
    def _get_current_period(self, periods: List[Dict], current_date: datetime) -> Optional[Dict]:
        """Get current period from a list of periods."""
        for period in periods:
            if period["start_date"] <= current_date <= period["end_date"]:
                # Calculate progress
                total_days = (period["end_date"] - period["start_date"]).days
                elapsed_days = (current_date - period["start_date"]).days
                progress = (elapsed_days / total_days) * 100 if total_days > 0 else 0
                
                period_copy = period.copy()
                period_copy["progress_percentage"] = round(progress, 2)
                period_copy["remaining_days"] = (period["end_date"] - current_date).days
                
                return period_copy
        
        return None
    
    def _get_nakshatra_name(self, nakshatra_num: int) -> str:
        """Get nakshatra name from number."""
        nakshatras = [
            "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
            "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
            "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
            "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
            "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
        ]
        return nakshatras[nakshatra_num]
    
    def _get_dasha_description(self, planet: str) -> str:
        """Get general description of dasha effects."""
        descriptions = {
            "Sun": "Period of authority, recognition, father figures, government, and self-realization",
            "Moon": "Period of emotions, mother, home, mental peace, and public dealings",
            "Mars": "Period of energy, conflicts, property, siblings, and bold actions",
            "Mercury": "Period of communication, learning, business, travel, and intellectual pursuits",
            "Jupiter": "Period of wisdom, spirituality, children, fortune, and expansion",
            "Venus": "Period of relationships, luxury, arts, material comforts, and pleasures",
            "Saturn": "Period of discipline, hard work, delays, lessons, and long-term rewards",
            "Rahu": "Period of material desires, foreign elements, sudden changes, and ambitions",
            "Ketu": "Period of spirituality, detachment, past karma, and liberation"
        }
        return descriptions.get(planet, "Period of transformation")
    
    def _predict_life_events(self, mahadashas: List[Dict]) -> List[Dict]:
        """Predict major life events based on dasha periods."""
        events = []
        
        for dasha in mahadashas:
            planet = dasha["planet"]
            start_age = (dasha["start_date"] - mahadashas[0]["start_date"]).days / 365.25
            
            # Major life events based on planetary periods
            if planet == "Jupiter" and 24 <= start_age <= 32:
                events.append({
                    "age": int(start_age),
                    "event": "Marriage or significant relationship",
                    "dasha": planet
                })
            
            if planet == "Mercury" and 16 <= start_age <= 25:
                events.append({
                    "age": int(start_age),
                    "event": "Higher education or career beginning",
                    "dasha": planet
                })
            
            if planet == "Sun" and 28 <= start_age <= 35:
                events.append({
                    "age": int(start_age),
                    "event": "Career advancement or recognition",
                    "dasha": planet
                })
            
            if planet == "Venus" and start_age >= 20:
                events.append({
                    "age": int(start_age),
                    "event": "Material prosperity and comfort",
                    "dasha": planet
                })
            
            if planet == "Saturn" and start_age >= 35:
                events.append({
                    "age": int(start_age),
                    "event": "Major responsibilities or karmic lessons",
                    "dasha": planet
                })
        
        return sorted(events, key=lambda x: x["age"])
    
    def _generate_dasha_predictions(
        self,
        current_dasha: Dict,
        mahadashas: List[Dict]
    ) -> Dict:
        """Generate predictions based on current and upcoming dashas."""
        if not current_dasha:
            return {}
        
        predictions = {
            "current_influences": self._get_current_influences(current_dasha),
            "upcoming_changes": self._get_upcoming_changes(current_dasha, mahadashas),
            "remedies": self._get_dasha_remedies(current_dasha)
        }
        
        return predictions
    
    def _get_current_influences(self, current_dasha: Dict) -> List[str]:
        """Get current planetary influences."""
        influences = []
        
        mahadasha = current_dasha["mahadasha"]["planet"]
        influences.append(f"Major influence of {mahadasha}")
        
        if "antardasha" in current_dasha:
            antardasha = current_dasha["antardasha"]["planet"]
            influences.append(f"Sub-influence of {antardasha}")
            
            # Combined effects
            if mahadasha == "Jupiter" and antardasha == "Venus":
                influences.append("Excellent period for relationships and prosperity")
            elif mahadasha == "Saturn" and antardasha == "Rahu":
                influences.append("Challenging period requiring patience and hard work")
        
        return influences
    
    def _get_upcoming_changes(
        self,
        current_dasha: Dict,
        mahadashas: List[Dict]
    ) -> List[Dict]:
        """Get upcoming dasha changes."""
        changes = []
        # Use timezone-aware datetime if birth_datetime was timezone-aware
        if mahadashas and mahadashas[0].get("start_date") and hasattr(mahadashas[0]["start_date"], 'tzinfo') and mahadashas[0]["start_date"].tzinfo:
            current_date = datetime.now(mahadashas[0]["start_date"].tzinfo)
        else:
            current_date = datetime.now()
        
        # Check next 3 years for significant changes
        for days in [30, 90, 180, 365, 730, 1095]:
            future_date = current_date + timedelta(days=days)
            future_dasha = self._get_current_dasha(mahadashas, future_date)
            
            if future_dasha and future_dasha["mahadasha"]["planet"] != current_dasha["mahadasha"]["planet"]:
                changes.append({
                    "date": future_date,
                    "days_until": days,
                    "new_dasha": future_dasha["mahadasha"]["planet"],
                    "significance": f"Major shift to {future_dasha['mahadasha']['planet']} period"
                })
                break
        
        return changes
    
    def _get_dasha_remedies(self, current_dasha: Dict) -> List[str]:
        """Get remedies for current dasha."""
        remedies = []
        
        planet = current_dasha["mahadasha"]["planet"]
        
        planet_remedies = {
            "Sun": ["Offer water to Sun at sunrise", "Wear ruby on Sunday"],
            "Moon": ["Wear pearl on Monday", "Donate white items"],
            "Mars": ["Recite Hanuman Chalisa", "Wear coral on Tuesday"],
            "Mercury": ["Donate green items on Wednesday", "Wear emerald"],
            "Jupiter": ["Wear yellow sapphire on Thursday", "Donate to teachers"],
            "Venus": ["Wear diamond or white sapphire", "Donate to women"],
            "Saturn": ["Donate black items on Saturday", "Serve the elderly"],
            "Rahu": ["Wear gomed (hessonite)", "Donate to outcasts"],
            "Ketu": ["Wear cat's eye", "Practice meditation"]
        }
        
        return planet_remedies.get(planet, ["Consult an astrologer for specific remedies"])


class YoginiDashaCalculator:
    """
    Calculate Yogini Dasha periods.
    
    Yogini Dasha is a 36-year cycle system with 8 yoginis.
    """
    
    def __init__(self):
        self.yogini_cycle = 36  # years
        self.yoginis = [
            {"name": "Mangala", "years": 1, "lord": "Moon"},
            {"name": "Pingala", "years": 2, "lord": "Sun"},
            {"name": "Dhanya", "years": 3, "lord": "Jupiter"},
            {"name": "Bhramari", "years": 4, "lord": "Mars"},
            {"name": "Bhadrika", "years": 5, "lord": "Mercury"},
            {"name": "Ulka", "years": 6, "lord": "Saturn"},
            {"name": "Siddha", "years": 7, "lord": "Venus"},
            {"name": "Sankata", "years": 8, "lord": "Rahu"}
        ]
    
    def calculate_yogini_dasha(
        self,
        birth_datetime: datetime,
        moon_longitude: float
    ) -> List[Dict]:
        """Calculate Yogini Dasha periods."""
        # Simplified implementation
        periods = []
        
        # Calculate starting yogini based on moon nakshatra
        nakshatra_index = int(moon_longitude / 13.333)
        starting_yogini_index = nakshatra_index % 8
        
        current_date = birth_datetime
        for i in range(16):  # Calculate 2 full cycles
            yogini = self.yoginis[(starting_yogini_index + i) % 8]
            period = {
                "yogini": yogini["name"],
                "lord": yogini["lord"],
                "start_date": current_date,
                "years": yogini["years"]
            }
            current_date = current_date.replace(year=current_date.year + yogini["years"])
            period["end_date"] = current_date
            periods.append(period)
        
        return periods


class CharaDashaCalculator:
    """
    Calculate Chara Dasha (Jaimini system).
    
    Based on movable, fixed, and dual signs.
    """
    
    def __init__(self):
        self.sign_types = {
            "movable": [0, 3, 6, 9],    # Aries, Cancer, Libra, Capricorn
            "fixed": [1, 4, 7, 10],      # Taurus, Leo, Scorpio, Aquarius
            "dual": [2, 5, 8, 11]        # Gemini, Virgo, Sagittarius, Pisces
        }
    
    def calculate_chara_dasha(
        self,
        birth_datetime: datetime,
        ascendant_sign: int,
        planet_positions: Dict[str, float]
    ) -> List[Dict]:
        """Calculate Chara Dasha periods."""
        # Simplified implementation
        periods = []
        
        # Calculate dasha order based on ascendant
        dasha_order = self._get_dasha_order(ascendant_sign)
        
        current_date = birth_datetime
        for sign in dasha_order:
            # Calculate period length (simplified - normally based on lord's position)
            years = self._calculate_sign_years(sign, planet_positions)
            
            period = {
                "sign": sign,
                "sign_name": self._get_sign_name(sign),
                "start_date": current_date,
                "years": years
            }
            current_date = current_date.replace(year=current_date.year + years)
            period["end_date"] = current_date
            periods.append(period)
        
        return periods
    
    def _get_dasha_order(self, ascendant_sign: int) -> List[int]:
        """Get dasha order based on ascendant."""
        # Simplified - normally considers odd/even and sign type
        order = list(range(12))
        # Rotate to start from ascendant
        return order[ascendant_sign:] + order[:ascendant_sign]
    
    def _calculate_sign_years(self, sign: int, planet_positions: Dict[str, float]) -> int:
        """Calculate years for a sign dasha."""
        # Simplified - normally based on lord's position from sign
        base_years = [7, 8, 9, 10, 11, 12, 7, 8, 9, 10, 11, 12]
        return base_years[sign]
    
    def _get_sign_name(self, sign: int) -> str:
        """Get sign name from index."""
        signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
        return signs[sign]