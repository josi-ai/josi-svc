"""
Vedic Panchang calculations using Swiss Ephemeris.
Implements authentic calculations for Tithi, Nakshatra, Yoga, and Karana.
"""
import swisseph as swe
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional
import math
import pytz


class PanchangCalculator:
    """Calculate Vedic Panchang elements."""
    
    # Nakshatra names
    NAKSHATRAS = [
        "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
        "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
        "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
        "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
        "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
    ]
    
    # Tithi names
    TITHIS = [
        "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
        "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
        "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima/Amavasya"
    ]
    
    # Yoga names
    YOGAS = [
        "Vishkumbha", "Priti", "Ayushman", "Saubhagya", "Shobhana",
        "Atiganda", "Sukarman", "Dhriti", "Shula", "Ganda",
        "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra",
        "Siddhi", "Vyatipata", "Viriyana", "Parigha", "Shiva",
        "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma",
        "Indra", "Vaidhriti"
    ]
    
    # Karana names (half-tithis)
    KARANAS = [
        "Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti",
        "Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti",
        "Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti",
        "Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti",
        "Bava", "Balava", "Kaulava", "Taitila", "Shakuni", "Chatushpada", "Naga", "Kimstughna"
    ]
    
    def __init__(self):
        swe.set_ephe_path('')
    
    def calculate_panchang(
        self,
        dt: datetime,
        latitude: float,
        longitude: float,
        timezone: str
    ) -> Dict:
        """Calculate all panchang elements for given date and location."""
        
        # Convert to UTC for calculations
        tz = pytz.timezone(timezone)
        local_dt = tz.localize(dt) if dt.tzinfo is None else dt
        utc_dt = local_dt.astimezone(pytz.UTC)
        
        # Calculate Julian Day
        jd = self._datetime_to_julian(utc_dt)
        
        # Get Sun and Moon positions
        sun_long = self._get_planet_longitude(jd, swe.SUN)
        moon_long = self._get_planet_longitude(jd, swe.MOON)
        
        # Calculate panchang elements
        tithi = self._calculate_tithi(sun_long, moon_long)
        nakshatra = self._calculate_nakshatra(moon_long)
        yoga = self._calculate_yoga(sun_long, moon_long)
        karana = self._calculate_karana(sun_long, moon_long)
        
        # Calculate sunrise and sunset
        sunrise, sunset = self._calculate_sun_times(jd, latitude, longitude)
        
        # Calculate auspicious/inauspicious times
        rahu_kaal = self._calculate_rahu_kaal(sunrise, sunset, local_dt.weekday())
        gulika_kaal = self._calculate_gulika_kaal(sunrise, sunset, local_dt.weekday())
        yamaganda = self._calculate_yamaganda(sunrise, sunset, local_dt.weekday())
        
        # Set ayanamsa mode and get ayanamsa
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        ayanamsa = swe.get_ayanamsa(jd)
        
        return {
            "date": local_dt.isoformat(),
            "location": {
                "latitude": latitude,
                "longitude": longitude,
                "timezone": timezone
            },
            "sunrise": self._julian_to_time(sunrise, timezone),
            "sunset": self._julian_to_time(sunset, timezone),
            "ayanamsa": round(ayanamsa, 6),
            "tithi": {
                "number": tithi["number"],
                "name": tithi["name"],
                "percent": round(tithi["percent"], 2),
                "end_time": tithi["end_time"],
                "paksha": tithi["paksha"],
                "deity": self._get_tithi_deity(tithi["number"])
            },
            "nakshatra": {
                "number": nakshatra["number"],
                "name": nakshatra["name"],
                "pada": nakshatra["pada"],
                "percent": round(nakshatra["percent"], 2),
                "end_time": nakshatra["end_time"],
                "ruler": self._get_nakshatra_ruler(nakshatra["number"]),
                "deity": self._get_nakshatra_deity(nakshatra["number"])
            },
            "yoga": {
                "number": yoga["number"],
                "name": yoga["name"],
                "percent": round(yoga["percent"], 2),
                "end_time": yoga["end_time"],
                "quality": self._get_yoga_quality(yoga["number"])
            },
            "karana": {
                "number": karana["number"],
                "name": karana["name"],
                "percent": round(karana["percent"], 2),
                "end_time": karana["end_time"],
                "quality": self._get_karana_quality(karana["name"])
            },
            "vara": {
                "day": self._get_vara_name(local_dt.weekday()),
                "ruler": self._get_vara_ruler(local_dt.weekday())
            },
            "auspicious_times": {
                "abhijit_muhurta": self._calculate_abhijit_muhurta(sunrise, sunset),
                "brahma_muhurta": self._calculate_brahma_muhurta(sunrise)
            },
            "inauspicious_times": {
                "rahu_kaal": rahu_kaal,
                "gulika_kaal": gulika_kaal,
                "yamaganda": yamaganda
            }
        }
    
    def _datetime_to_julian(self, dt: datetime) -> float:
        """Convert datetime to Julian day number."""
        return swe.julday(
            dt.year, dt.month, dt.day,
            dt.hour + dt.minute/60.0 + dt.second/3600.0
        )
    
    def _julian_to_time(self, jd: float, timezone: str) -> str:
        """Convert Julian day to time string in given timezone."""
        year, month, day, hour = swe.revjul(jd)
        hours = int(hour)
        minutes = int((hour - hours) * 60)
        
        utc_dt = datetime(year, month, day, hours, minutes, tzinfo=pytz.UTC)
        local_dt = utc_dt.astimezone(pytz.timezone(timezone))
        
        return local_dt.strftime("%H:%M")
    
    def _get_planet_longitude(self, jd: float, planet: int) -> float:
        """Get sidereal longitude of planet."""
        # Set Lahiri ayanamsa
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        
        # Calculate position
        xx, ret = swe.calc_ut(jd, planet, swe.FLG_SIDEREAL)
        
        return xx[0]  # Sidereal longitude
    
    def _calculate_tithi(self, sun_long: float, moon_long: float) -> Dict:
        """Calculate lunar tithi (phase)."""
        # Tithi = (Moon - Sun) / 12
        diff = (moon_long - sun_long) % 360
        tithi_num = diff / 12.0
        tithi_index = int(tithi_num)
        
        # Determine paksha (fortnight)
        if tithi_index < 15:
            paksha = "Shukla" # Waxing
        else:
            paksha = "Krishna"  # Waning
            tithi_index = tithi_index - 15
        
        # Calculate percentage and end time
        percent = (tithi_num % 1) * 100
        
        # Special handling for Purnima/Amavasya
        if tithi_index == 14:
            if paksha == "Shukla":
                name = "Purnima"
            else:
                name = "Amavasya"
        else:
            name = self.TITHIS[tithi_index]
        
        return {
            "number": tithi_index + 1,
            "name": name,
            "paksha": paksha,
            "percent": percent,
            "end_time": self._calculate_end_time(diff % 12, 12, "tithi")
        }
    
    def _calculate_nakshatra(self, moon_long: float) -> Dict:
        """Calculate lunar nakshatra (constellation)."""
        # Each nakshatra = 13°20' = 13.333...°
        nakshatra_size = 360 / 27
        nakshatra_num = moon_long / nakshatra_size
        nakshatra_index = int(nakshatra_num)
        
        # Calculate pada (quarter)
        pada_num = (nakshatra_num % 1) * 4
        pada = int(pada_num) + 1
        
        # Calculate percentage
        percent = (nakshatra_num % 1) * 100
        
        return {
            "number": nakshatra_index + 1,
            "name": self.NAKSHATRAS[nakshatra_index],
            "pada": pada,
            "percent": percent,
            "end_time": self._calculate_end_time(moon_long % nakshatra_size, nakshatra_size, "nakshatra")
        }
    
    def _calculate_yoga(self, sun_long: float, moon_long: float) -> Dict:
        """Calculate yoga (Sun + Moon combination)."""
        # Yoga = (Sun + Moon) / 13°20'
        yoga_size = 360 / 27
        sum_long = (sun_long + moon_long) % 360
        yoga_num = sum_long / yoga_size
        yoga_index = int(yoga_num)
        
        # Calculate percentage
        percent = (yoga_num % 1) * 100
        
        return {
            "number": yoga_index + 1,
            "name": self.YOGAS[yoga_index],
            "percent": percent,
            "end_time": self._calculate_end_time(sum_long % yoga_size, yoga_size, "yoga")
        }
    
    def _calculate_karana(self, sun_long: float, moon_long: float) -> Dict:
        """Calculate karana (half-tithi)."""
        # Karana = (Moon - Sun) / 6
        diff = (moon_long - sun_long) % 360
        karana_num = diff / 6.0
        karana_index = int(karana_num)
        
        # Fixed karanas for special positions
        if karana_index == 0:
            name = "Kimstughna"
        elif karana_index >= 57:
            fixed_karanas = ["Shakuni", "Chatushpada", "Naga", "Kimstughna"]
            name = fixed_karanas[karana_index - 57]
        else:
            # Rotating karanas
            name = self.KARANAS[(karana_index - 1) % 7]
        
        # Calculate percentage
        percent = (karana_num % 1) * 100
        
        return {
            "number": karana_index + 1,
            "name": name,
            "percent": percent,
            "end_time": self._calculate_end_time(diff % 6, 6, "karana")
        }
    
    def _calculate_sun_times(self, jd: float, latitude: float, longitude: float) -> Tuple[float, float]:
        """Calculate sunrise and sunset times."""
        # Geographic position as sequence [longitude, latitude, altitude]
        geopos = [longitude, latitude, 0]  # altitude = 0 (sea level)
        
        # Calculate sunrise
        res_rise, times_rise = swe.rise_trans(
            jd - 1,  # Start search from previous day
            swe.SUN,
            swe.CALC_RISE,
            geopos,
            0.0,  # Atmospheric pressure
            0.0,  # Temperature
            swe.FLG_SWIEPH
        )
        
        # Calculate sunset
        res_set, times_set = swe.rise_trans(
            jd - 1,
            swe.SUN,
            swe.CALC_SET,
            geopos,
            0.0,  # Atmospheric pressure
            0.0,  # Temperature
            swe.FLG_SWIEPH
        )
        
        # Extract the rise and set times (first element of the returned tuple)
        rise_jd = times_rise[0] if res_rise == 0 else jd + 0.25  # Default to 6am if not found
        set_jd = times_set[0] if res_set == 0 else jd + 0.75    # Default to 6pm if not found
        
        return rise_jd, set_jd
    
    def _calculate_rahu_kaal(self, sunrise: float, sunset: float, weekday: int) -> str:
        """Calculate Rahu Kaal timing."""
        day_duration = sunset - sunrise
        part_duration = day_duration / 8
        
        # Rahu Kaal order for weekdays (Sun=0, Mon=1, ..., Sat=6)
        rahu_parts = [7, 1, 6, 4, 5, 3, 2]  # 8th, 2nd, 7th, 5th, 6th, 4th, 3rd part
        
        part = rahu_parts[weekday]
        start = sunrise + (part - 1) * part_duration
        end = start + part_duration
        
        return f"{self._julian_to_time(start, 'UTC')}-{self._julian_to_time(end, 'UTC')}"
    
    def _calculate_gulika_kaal(self, sunrise: float, sunset: float, weekday: int) -> str:
        """Calculate Gulika Kaal timing."""
        day_duration = sunset - sunrise
        part_duration = day_duration / 8
        
        # Gulika Kaal order for weekdays
        gulika_parts = [6, 5, 4, 3, 2, 1, 7]  # Different part for each day
        
        part = gulika_parts[weekday]
        start = sunrise + (part - 1) * part_duration
        end = start + part_duration
        
        return f"{self._julian_to_time(start, 'UTC')}-{self._julian_to_time(end, 'UTC')}"
    
    def _calculate_yamaganda(self, sunrise: float, sunset: float, weekday: int) -> str:
        """Calculate Yamaganda timing."""
        day_duration = sunset - sunrise
        part_duration = day_duration / 8
        
        # Yamaganda order for weekdays
        yama_parts = [4, 3, 2, 1, 7, 6, 5]
        
        part = yama_parts[weekday]
        start = sunrise + (part - 1) * part_duration
        end = start + part_duration
        
        return f"{self._julian_to_time(start, 'UTC')}-{self._julian_to_time(end, 'UTC')}"
    
    def _calculate_abhijit_muhurta(self, sunrise: float, sunset: float) -> str:
        """Calculate Abhijit Muhurta (most auspicious time)."""
        day_duration = sunset - sunrise
        muhurta_duration = day_duration / 15  # Day divided into 15 muhurtas
        
        # Abhijit is the 8th muhurta of the day
        start = sunrise + 7 * muhurta_duration
        end = start + muhurta_duration
        
        return f"{self._julian_to_time(start, 'UTC')}-{self._julian_to_time(end, 'UTC')}"
    
    def _calculate_brahma_muhurta(self, sunrise: float) -> str:
        """Calculate Brahma Muhurta (pre-dawn spiritual time)."""
        # 1.5 hours before sunrise
        muhurta_duration = 48 / 1440  # 48 minutes in Julian days
        start = sunrise - (2 * muhurta_duration)
        end = sunrise - muhurta_duration
        
        return f"{self._julian_to_time(start, 'UTC')}-{self._julian_to_time(end, 'UTC')}"
    
    def _calculate_end_time(self, current: float, size: float, element: str) -> Optional[str]:
        """Calculate when current panchang element ends."""
        # This is a simplified calculation
        # In practice, you'd need to iterate to find exact transition time
        remaining = size - current
        # Convert to approximate hours
        if element == "tithi":
            hours = remaining * 2  # Rough approximation
        elif element == "nakshatra":
            hours = remaining * 1.8
        else:
            hours = remaining * 1.5
        
        return f"~{int(hours)}h {int((hours % 1) * 60)}m"
    
    def _get_vara_name(self, weekday: int) -> str:
        """Get Vedic day name."""
        vara_names = [
            "Ravivara (Sunday)",
            "Somavara (Monday)",
            "Mangalavara (Tuesday)",
            "Budhavara (Wednesday)",
            "Guruvara (Thursday)",
            "Shukravara (Friday)",
            "Shanivara (Saturday)"
        ]
        return vara_names[weekday]
    
    def _get_vara_ruler(self, weekday: int) -> str:
        """Get planetary ruler of the day."""
        rulers = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
        return rulers[weekday]
    
    def _get_tithi_deity(self, tithi_num: int) -> str:
        """Get deity associated with tithi."""
        deities = [
            "Agni", "Brahma", "Gauri", "Ganesha", "Naga",
            "Kartikeya", "Surya", "Shiva", "Durga", "Yama",
            "Vishvadeva", "Vishnu", "Kamadeva", "Shiva", "Chandra/Shiva"
        ]
        return deities[tithi_num - 1] if tithi_num <= 15 else deities[(tithi_num - 16) % 15]
    
    def _get_nakshatra_ruler(self, nakshatra_num: int) -> str:
        """Get planetary ruler of nakshatra."""
        rulers = ["Ketu", "Venus", "Sun", "Moon", "Mars",
                  "Rahu", "Jupiter", "Saturn", "Mercury"]
        return rulers[(nakshatra_num - 1) % 9]
    
    def _get_nakshatra_deity(self, nakshatra_num: int) -> str:
        """Get deity of nakshatra."""
        deities = [
            "Ashwini Kumaras", "Yama", "Agni", "Brahma", "Soma", "Rudra",
            "Aditi", "Brihaspati", "Naga", "Pitris", "Bhaga", "Aryama",
            "Savitar", "Tvashtar", "Vayu", "Indragni", "Mitra", "Indra",
            "Nirriti", "Apas", "Vishvadevas", "Vishnu", "Vasu", "Varuna",
            "Aja Ekapada", "Ahir Budhyana", "Pushan"
        ]
        return deities[nakshatra_num - 1]
    
    def _get_yoga_quality(self, yoga_num: int) -> str:
        """Get quality/nature of yoga."""
        # Simplified - some yogas are good, some bad, some mixed
        good_yogas = [2, 3, 4, 5, 7, 8, 11, 12, 14, 16, 20, 21, 22, 23, 24, 25, 26]
        bad_yogas = [1, 6, 9, 10, 13, 15, 17, 19, 27]
        
        if yoga_num in good_yogas:
            return "Auspicious"
        elif yoga_num in bad_yogas:
            return "Inauspicious"
        else:
            return "Mixed"
    
    def _get_karana_quality(self, karana_name: str) -> str:
        """Get quality of karana."""
        good_karanas = ["Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija"]
        bad_karanas = ["Vishti", "Shakuni", "Chatushpada", "Naga", "Kimstughna"]
        
        if karana_name in good_karanas:
            return "Auspicious"
        elif karana_name in bad_karanas:
            return "Inauspicious"
        else:
            return "Neutral"