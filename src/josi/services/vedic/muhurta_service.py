"""
Muhurta (Auspicious Time) calculator for Vedic astrology.
"""
import swisseph as swe
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import pytz
from lunarcalendar import Converter, Solar

from .panchang_service import PanchangCalculator


class MuhurtaCalculator:
    """Calculate auspicious times (Muhurta) for various activities."""
    
    def __init__(self):
        swe.set_ephe_path('')
        self.panchang_calc = PanchangCalculator()
        
        # Activity-specific favorable factors
        self.activity_rules = {
            "marriage": {
                "favorable_tithis": [2, 3, 5, 7, 10, 11, 13],
                "unfavorable_tithis": [4, 6, 8, 9, 12, 14, 30],  # 30 = Amavasya
                "favorable_nakshatras": ["Rohini", "Mrigashira", "Magha", "Uttara Phalguni", 
                                       "Hasta", "Swati", "Anuradha", "Uttara Ashadha", 
                                       "Uttara Bhadrapada", "Revati"],
                "unfavorable_nakshatras": ["Bharani", "Krittika", "Ashlesha", "Vishakha"],
                "favorable_days": [1, 3, 5],  # Monday, Wednesday, Friday
                "unfavorable_days": [0, 2],    # Sunday, Tuesday
                "favorable_yogas": ["Siddha", "Amrita", "Sarvartha Siddhi"],
                "avoid_months": [7, 8, 9, 11]  # Ashada, Shravana, Bhadrapada, Pausha
            },
            "business": {
                "favorable_tithis": [1, 2, 3, 5, 7, 10, 11, 13, 15],
                "unfavorable_tithis": [4, 6, 8, 9, 12, 14, 30],
                "favorable_nakshatras": ["Ashwini", "Rohini", "Pushya", "Hasta", 
                                       "Chitra", "Swati", "Anuradha", "Revati"],
                "unfavorable_nakshatras": ["Krittika", "Ashlesha", "Magha", "Moola"],
                "favorable_days": [1, 3, 4, 5],  # Monday, Wednesday, Thursday, Friday
                "unfavorable_days": [6],  # Saturday
                "favorable_yogas": ["Siddha", "Amrita", "Sarvartha Siddhi"],
                "avoid_months": []
            },
            "travel": {
                "favorable_tithis": [2, 3, 5, 7, 11, 13],
                "unfavorable_tithis": [4, 6, 8, 9, 12, 14, 30],
                "favorable_nakshatras": ["Ashwini", "Mrigashira", "Punarvasu", "Pushya",
                                       "Hasta", "Anuradha", "Shravana", "Ghanishtha"],
                "unfavorable_nakshatras": ["Bharani", "Krittika", "Ashlesha", "Vishakha"],
                "favorable_days": [1, 3, 5],  # Monday, Wednesday, Friday
                "unfavorable_days": [2],  # Tuesday
                "favorable_yogas": ["Siddha", "Amrita"],
                "avoid_months": []
            },
            "education": {
                "favorable_tithis": [2, 3, 5, 7, 10, 11, 12, 13],
                "unfavorable_tithis": [1, 4, 6, 8, 9, 14, 30],
                "favorable_nakshatras": ["Ashwini", "Punarvasu", "Pushya", "Hasta",
                                       "Chitra", "Swati", "Anuradha", "Revati"],
                "unfavorable_nakshatras": ["Krittika", "Ashlesha", "Magha"],
                "favorable_days": [3, 4],  # Wednesday, Thursday
                "unfavorable_days": [],
                "favorable_yogas": ["Siddha", "Amrita", "Sarvartha Siddhi"],
                "avoid_months": []
            },
            "medical": {
                "favorable_tithis": [1, 2, 3, 5, 7, 10, 11, 13],
                "unfavorable_tithis": [4, 6, 8, 9, 12, 14, 30],
                "favorable_nakshatras": ["Ashwini", "Rohini", "Punarvasu", "Pushya",
                                       "Hasta", "Chitra", "Anuradha"],
                "unfavorable_nakshatras": ["Bharani", "Krittika", "Ashlesha", "Moola"],
                "favorable_days": [0, 1, 3, 4],  # Sunday, Monday, Wednesday, Thursday
                "unfavorable_days": [2, 6],  # Tuesday, Saturday
                "favorable_yogas": ["Siddha", "Amrita"],
                "avoid_months": []
            },
            "property": {
                "favorable_tithis": [1, 2, 3, 5, 7, 10, 11, 13, 15],
                "unfavorable_tithis": [4, 6, 8, 9, 12, 14, 30],
                "favorable_nakshatras": ["Rohini", "Mrigashira", "Uttara Phalguni",
                                       "Hasta", "Chitra", "Swati", "Uttara Ashadha"],
                "unfavorable_nakshatras": ["Bharani", "Krittika", "Ashlesha", "Vishakha"],
                "favorable_days": [1, 3, 4, 5],  # Monday, Wednesday, Thursday, Friday
                "unfavorable_days": [2, 6],  # Tuesday, Saturday
                "favorable_yogas": ["Siddha", "Amrita", "Sarvartha Siddhi"],
                "avoid_months": []
            }
        }
        
        # Rahu Kaal timings (minutes from sunrise)
        self.rahu_kaal_timings = {
            0: (240, 330),  # Sunday: 4-5.5 hours after sunrise
            1: (450, 540),  # Monday: 7.5-9 hours after sunrise
            2: (180, 270),  # Tuesday: 3-4.5 hours after sunrise
            3: (720, 810),  # Wednesday: 12-13.5 hours after sunrise
            4: (360, 450),  # Thursday: 6-7.5 hours after sunrise
            5: (600, 690),  # Friday: 10-11.5 hours after sunrise
            6: (540, 630)   # Saturday: 9-10.5 hours after sunrise
        }
    
    def find_muhurta(
        self,
        purpose: str,
        start_date: datetime,
        end_date: datetime,
        latitude: float,
        longitude: float,
        timezone: str,
        max_results: int = 10
    ) -> List[Dict]:
        """
        Find auspicious times for a specific purpose.
        
        Args:
            purpose: Type of activity (marriage, business, travel, etc.)
            start_date: Start of search period
            end_date: End of search period
            latitude: Location latitude
            longitude: Location longitude
            timezone: Location timezone
            max_results: Maximum number of results to return
        
        Returns:
            List of muhurta recommendations
        """
        # Get rules for the activity
        rules = self.activity_rules.get(purpose.lower(), self.activity_rules["business"])
        
        muhurtas = []
        tz = pytz.timezone(timezone)
        
        # Check each day in the range
        current_date = start_date.date()
        while current_date <= end_date.date() and len(muhurtas) < max_results:
            # Skip unfavorable months
            if current_date.month in rules.get("avoid_months", []):
                current_date += timedelta(days=1)
                continue
            
            # Check if day of week is favorable
            weekday = current_date.weekday()
            if weekday in rules.get("unfavorable_days", []):
                current_date += timedelta(days=1)
                continue
            
            # Calculate panchang for the day
            day_start = tz.localize(datetime.combine(current_date, datetime.min.time()))
            panchang = self.panchang_calc.calculate_panchang(
                day_start, latitude, longitude, timezone
            )
            
            # Check tithi
            tithi_num = panchang["tithi"]["number"]
            if tithi_num not in rules.get("favorable_tithis", []):
                current_date += timedelta(days=1)
                continue
            
            # Check nakshatra
            nakshatra_name = panchang["nakshatra"]["name"]
            if nakshatra_name in rules.get("unfavorable_nakshatras", []):
                current_date += timedelta(days=1)
                continue
            
            # Check yoga
            yoga_name = panchang["yoga"]["name"]
            
            # Calculate quality score
            quality_score = self._calculate_quality_score(
                tithi_num, nakshatra_name, yoga_name, weekday, rules
            )
            
            if quality_score >= 60:  # Minimum acceptable score
                # Find best time slots in the day
                time_slots = self._find_best_time_slots(
                    current_date, latitude, longitude, timezone, rules
                )
                
                for slot in time_slots[:2]:  # Max 2 slots per day
                    muhurta = {
                        "date": current_date.isoformat(),
                        "time": f"{slot['start'].strftime('%I:%M %p')} - {slot['end'].strftime('%I:%M %p')}",
                        "quality": self._get_quality_label(quality_score),
                        "score": quality_score,
                        "tithi": panchang["tithi"]["name"],
                        "nakshatra": nakshatra_name,
                        "yoga": yoga_name,
                        "weekday": ["Sunday", "Monday", "Tuesday", "Wednesday", 
                                  "Thursday", "Friday", "Saturday"][weekday],
                        "factors": {
                            "positive": slot.get("positive_factors", []),
                            "negative": slot.get("negative_factors", [])
                        },
                        "recommendations": self._get_recommendations(
                            purpose, quality_score, panchang
                        )
                    }
                    
                    muhurtas.append(muhurta)
                    
                    if len(muhurtas) >= max_results:
                        break
            
            current_date += timedelta(days=1)
        
        # Sort by quality score
        muhurtas.sort(key=lambda x: x["score"], reverse=True)
        
        return muhurtas
    
    def _calculate_quality_score(
        self,
        tithi: int,
        nakshatra: str,
        yoga: str,
        weekday: int,
        rules: Dict
    ) -> float:
        """Calculate quality score for a muhurta."""
        score = 50  # Base score
        
        # Tithi score
        if tithi in rules.get("favorable_tithis", []):
            score += 15
        if tithi in [2, 3, 5, 7, 11]:  # Especially good tithis
            score += 5
        
        # Nakshatra score
        if nakshatra in rules.get("favorable_nakshatras", []):
            score += 20
        if nakshatra in ["Pushya", "Rohini", "Uttara Phalguni"]:  # Best nakshatras
            score += 5
        
        # Yoga score
        if yoga in rules.get("favorable_yogas", []):
            score += 15
        elif yoga in ["Vyatipata", "Vaidhriti", "Vishkumbha"]:  # Inauspicious yogas
            score -= 10
        
        # Weekday score
        if weekday in rules.get("favorable_days", []):
            score += 10
        if weekday == 4:  # Thursday (Jupiter's day) is generally good
            score += 5
        
        # Cap score at 100
        return min(score, 100)
    
    def _get_quality_label(self, score: float) -> str:
        """Get quality label based on score."""
        if score >= 90:
            return "Excellent"
        elif score >= 75:
            return "Very Good"
        elif score >= 60:
            return "Good"
        elif score >= 45:
            return "Fair"
        else:
            return "Poor"
    
    def _find_best_time_slots(
        self,
        date: datetime.date,
        latitude: float,
        longitude: float,
        timezone: str,
        rules: Dict
    ) -> List[Dict]:
        """Find best time slots within a day."""
        tz = pytz.timezone(timezone)
        slots = []
        
        # Get sunrise and sunset
        sunrise, sunset = self._get_sun_times(date, latitude, longitude, timezone)
        
        # Calculate Rahu Kaal for the day
        weekday = date.weekday()
        rahu_start_min, rahu_end_min = self.rahu_kaal_timings.get(weekday, (0, 0))
        rahu_start = sunrise + timedelta(minutes=rahu_start_min)
        rahu_end = sunrise + timedelta(minutes=rahu_end_min)
        
        # Define time periods
        periods = [
            ("Early Morning", sunrise, sunrise + timedelta(hours=2)),
            ("Morning", sunrise + timedelta(hours=2), sunrise + timedelta(hours=4)),
            ("Late Morning", sunrise + timedelta(hours=4), sunrise + timedelta(hours=6)),
            ("Noon", sunrise + timedelta(hours=6), sunrise + timedelta(hours=8)),
            ("Afternoon", sunrise + timedelta(hours=8), sunset - timedelta(hours=2)),
            ("Evening", sunset - timedelta(hours=2), sunset)
        ]
        
        # Abhijit Muhurta (most auspicious time around noon)
        abhijit_start = sunrise + timedelta(hours=6) - timedelta(minutes=24)
        abhijit_end = sunrise + timedelta(hours=6) + timedelta(minutes=24)
        
        for period_name, start, end in periods:
            # Skip if period overlaps with Rahu Kaal
            if not (end <= rahu_start or start >= rahu_end):
                continue
            
            positive_factors = []
            negative_factors = []
            
            # Check if it's Abhijit Muhurta
            if start <= abhijit_start <= end or start <= abhijit_end <= end:
                positive_factors.append("Abhijit Muhurta")
            
            # Morning is generally good for most activities
            if period_name in ["Early Morning", "Morning"]:
                positive_factors.append("Brahma Muhurta influence")
            
            # Avoid twilight for important activities
            if period_name == "Evening":
                negative_factors.append("Twilight period")
            
            slot = {
                "start": start,
                "end": end,
                "period": period_name,
                "positive_factors": positive_factors,
                "negative_factors": negative_factors
            }
            
            slots.append(slot)
        
        return slots
    
    def _get_sun_times(
        self,
        date: datetime.date,
        latitude: float,
        longitude: float,
        timezone: str
    ) -> Tuple[datetime, datetime]:
        """Calculate sunrise and sunset times."""
        tz = pytz.timezone(timezone)
        
        # Create datetime at midnight
        dt = tz.localize(datetime.combine(date, datetime.min.time()))
        jd = self.panchang_calc._datetime_to_julian(dt)
        
        # Calculate sunrise and sunset
        # Geographic position as sequence [longitude, latitude, altitude]
        geopos = [float(-longitude), float(latitude), 0.0]  # Swiss Ephemeris uses negative longitude
        
        res_rise, times_rise = swe.rise_trans(
            jd - 1,  # Start search from previous day
            swe.SUN,
            swe.CALC_RISE,
            geopos,
            0.0,  # Atmospheric pressure
            0.0,  # Temperature
            swe.FLG_SWIEPH
        )
        
        rise_set = times_rise[0] if res_rise == 0 else jd + 0.25
        
        sunrise_jd = rise_set
        
        # Geographic position as sequence [longitude, latitude, altitude]
        geopos = [float(-longitude), float(latitude), 0.0]  # Swiss Ephemeris uses negative longitude
        
        res_set, times_set = swe.rise_trans(
            jd - 1,
            swe.SUN,
            swe.CALC_SET,
            geopos,
            0.0,  # Atmospheric pressure
            0.0,  # Temperature
            swe.FLG_SWIEPH
        )
        
        rise_set = times_set[0] if res_set == 0 else jd + 0.75
        
        sunset_jd = rise_set
        
        # Convert to datetime
        sunrise = self._julian_to_datetime(sunrise_jd)
        sunset = self._julian_to_datetime(sunset_jd)
        
        # Localize to timezone
        sunrise = tz.localize(sunrise.replace(tzinfo=None))
        sunset = tz.localize(sunset.replace(tzinfo=None))
        
        return sunrise, sunset
    
    def _julian_to_datetime(self, jd: float) -> datetime:
        """Convert Julian day to datetime."""
        year, month, day, hour = swe.revjul(jd)
        hour_int = int(hour)
        minute = int((hour - hour_int) * 60)
        second = int(((hour - hour_int) * 60 - minute) * 60)
        
        return datetime(year, month, day, hour_int, minute, second)
    
    def _get_recommendations(
        self,
        purpose: str,
        quality_score: float,
        panchang: Dict
    ) -> List[str]:
        """Get specific recommendations for the muhurta."""
        recommendations = []
        
        # General recommendations based on purpose
        purpose_recommendations = {
            "marriage": [
                "Perform Ganesh puja before the ceremony",
                "Exchange garlands during the auspicious time",
                "Complete main rituals within the muhurta period"
            ],
            "business": [
                "Sign important documents during this time",
                "Make the first transaction auspicious",
                "Invoke Lakshmi and Ganesh for prosperity"
            ],
            "travel": [
                "Start journey facing the favorable direction",
                "Carry something sweet for good luck",
                "Pray for safe travels before departing"
            ],
            "education": [
                "Begin with Saraswati vandana",
                "Keep study materials ready beforehand",
                "Face east or north while studying"
            ],
            "medical": [
                "Maintain positive mindset",
                "Follow all medical advice",
                "Consider charitable acts for well-being"
            ],
            "property": [
                "Perform bhumi puja if buying land",
                "Check all documents thoroughly",
                "Enter property with right foot first"
            ]
        }
        
        recommendations.extend(purpose_recommendations.get(purpose, []))
        
        # Quality-based recommendations
        if quality_score >= 90:
            recommendations.append("This is an exceptionally auspicious time")
        elif quality_score >= 75:
            recommendations.append("Very favorable time for important activities")
        
        # Nakshatra-specific recommendations
        nakshatra = panchang["nakshatra"]["name"]
        if nakshatra == "Pushya":
            recommendations.append("Pushya nakshatra is excellent for all auspicious activities")
        elif nakshatra == "Rohini":
            recommendations.append("Rohini favors growth and prosperity")
        
        return recommendations
    
    def calculate_rahu_kaal(
        self,
        date: datetime,
        latitude: float,
        longitude: float,
        timezone: str
    ) -> Dict:
        """Calculate Rahu Kaal for a specific date and location."""
        # Get sunrise and sunset
        sunrise, sunset = self._get_sun_times(date.date(), latitude, longitude, timezone)
        
        # Get weekday
        weekday = date.weekday()
        
        # Calculate Rahu Kaal timing
        rahu_start_min, rahu_end_min = self.rahu_kaal_timings.get(weekday, (0, 0))
        
        rahu_start = sunrise + timedelta(minutes=rahu_start_min)
        rahu_end = sunrise + timedelta(minutes=rahu_end_min)
        
        return {
            "date": date.date().isoformat(),
            "weekday": ["Sunday", "Monday", "Tuesday", "Wednesday", 
                       "Thursday", "Friday", "Saturday"][weekday],
            "rahu_kaal": {
                "start": rahu_start.strftime("%I:%M %p"),
                "end": rahu_end.strftime("%I:%M %p"),
                "duration_minutes": 90
            },
            "sunrise": sunrise.strftime("%I:%M %p"),
            "sunset": sunset.strftime("%I:%M %p"),
            "recommendation": "Avoid starting new ventures during Rahu Kaal"
        }
    
    def get_monthly_calendar(
        self,
        year: int,
        month: int,
        latitude: float,
        longitude: float,
        timezone: str
    ) -> List[Dict]:
        """Get auspicious dates for an entire month."""
        import calendar
        
        dates = []
        _, last_day = calendar.monthrange(year, month)
        
        for day in range(1, last_day + 1):
            date = datetime(year, month, day)
            
            # Calculate panchang
            panchang = self.panchang_calc.calculate_panchang(
                date, latitude, longitude, timezone
            )
            
            # Calculate basic quality
            weekday = date.weekday()
            tithi = panchang["tithi"]["number"]
            nakshatra = panchang["nakshatra"]["name"]
            
            # Simple classification
            is_auspicious = (
                tithi in [2, 3, 5, 7, 10, 11, 13] and
                nakshatra not in ["Bharani", "Krittika", "Ashlesha", "Vishakha"]
            )
            
            dates.append({
                "date": date.date().isoformat(),
                "weekday": ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"][weekday],
                "tithi": panchang["tithi"]["name"],
                "nakshatra": nakshatra,
                "is_auspicious": is_auspicious,
                "festivals": panchang.get("festivals", [])
            })
        
        return dates