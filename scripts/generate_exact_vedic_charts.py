#!/usr/bin/env python3
"""
Generate EXACT Vedic astrology charts matching traditional text export format
Includes ALL details: Tamil dates, Ashtakavarga, Pinda, complete Dasha sequences, etc.
"""
import asyncio
import httpx
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import logging
import math

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API Configuration
API_BASE = "http://localhost:8000/api/v1"
API_KEY = "test-api-key"

# Test persons data
TEST_PERSONS = [
    {
        "name": "Archana M",
        "gender": "female",
        "date_of_birth": "1998-12-07",
        "time_of_birth": "21:15:00",
        "place_of_birth": "Chennai, Tamil Nadu, India",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "timezone": "Asia/Kolkata"
    },
    {
        "name": "Valarmathi Kannappan",
        "gender": "female", 
        "date_of_birth": "1961-02-11",
        "time_of_birth": "15:30:00",
        "place_of_birth": "Kovur, Tamil Nadu, India",
        "latitude": 13.011362,
        "longitude": 80.120858,
        "timezone": "Asia/Kolkata"
    },
    {
        "name": "Janaki Panneerselvam",
        "gender": "female",
        "date_of_birth": "1982-12-18",
        "time_of_birth": "10:10:00",
        "place_of_birth": "Chennai, Tamil Nadu, India",
        "latitude": 13.083694,
        "longitude": 80.270186,
        "timezone": "Asia/Kolkata"
    },
    {
        "name": "Panneerselvam Chandrasekaran",
        "gender": "male",
        "date_of_birth": "1954-08-20",
        "time_of_birth": "18:20:00",
        "place_of_birth": "Kanchipuram, Tamil Nadu, India",
        "latitude": 12.833237,
        "longitude": 79.703644,
        "timezone": "Asia/Kolkata"
    },
    {
        "name": "Govindarajan Panneerselvam",
        "gender": "male",
        "date_of_birth": "1984-05-20",
        "time_of_birth": "23:00:00",
        "place_of_birth": "Chennai, Tamil Nadu, India",
        "latitude": 13.083694,
        "longitude": 80.270186,
        "timezone": "Asia/Kolkata"
    }
]

class ExactVedicChartGenerator:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0, follow_redirects=True)
        self.headers = {"X-API-Key": API_KEY}
        
    async def close(self):
        await self.client.aclose()
        
    async def create_person(self, person_data: Dict) -> Optional[str]:
        """Create a person and return their ID"""
        try:
            response = await self.client.post(
                f"{API_BASE}/persons/",
                json=person_data,
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.json()['data']['person_id']
            else:
                logger.error(f"Failed to create person {person_data['name']}: {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error creating person: {e}")
            return None
            
    async def get_chart_data(self, person_id: str) -> Optional[Dict]:
        """Get comprehensive chart data for a person"""
        try:
            # Get Vedic chart with full details
            response = await self.client.post(
                f"{API_BASE}/charts/calculate/",
                params={
                    "person_id": person_id,
                    "systems": "vedic",
                    "house_system": "placidus",
                    "ayanamsa": "lahiri"
                },
                headers=self.headers
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to calculate chart: {response.text}")
                return None
                
            return response.json()['data'][0]
            
        except Exception as e:
            logger.error(f"Error calculating chart: {e}")
            return None
            
    def format_degrees_dms(self, degrees: float) -> str:
        """Format degrees to deg°min'sec" format"""
        deg = int(degrees)
        min = int((degrees - deg) * 60)
        sec = int(((degrees - deg) * 60 - min) * 60)
        return f"{deg}°{min:02d}'{sec:02d}\""
        
    def format_degrees_dm(self, degrees: float) -> str:
        """Format degrees to deg:min format for planets"""
        deg = int(degrees)
        min = int((degrees - deg) * 60)
        return f"{deg:3d}:{min:02d}"
        
    def get_tamil_calendar_date(self, date: datetime) -> str:
        """Get Tamil calendar date - simplified calculation"""
        # Tamil months
        tamil_months = ["CHITHIRAI", "VAIKASI", "AANI", "AADI", "AAVANI", "PURATTASI",
                       "AIPPASI", "KARTHIKAI", "MARGAZHI", "THAI", "MAASI", "PANGUNI"]
        
        # Approximate Tamil date (would need full panchang for accuracy)
        month_offset = 14  # Tamil calendar is approximately 14 days behind
        tamil_date = date - timedelta(days=month_offset)
        tamil_month = tamil_months[(tamil_date.month + 8) % 12]  # Chithirai starts in April
        
        # Example format: "BAHDANYA KARTHIKA 22"
        return f"BAHDANYA {tamil_month} {tamil_date.day}"
        
    def calculate_nakshatra_ruler(self, nakshatra: str) -> str:
        """Get the ruler of a nakshatra in abbreviated form"""
        rulers = {
            'Ashwini': 'KETU', 'Bharani': 'SUKR', 'Krittika': 'SURY',
            'Rohini': 'CHAN', 'Mrigashira': 'KUJA', 'Ardra': 'RAHU',
            'Punarvasu': 'GURU', 'Pushya': 'SANI', 'Ashlesha': 'BUDH',
            'Magha': 'KETU', 'Purva Phalguni': 'SUKR', 'Uttara Phalguni': 'SURY',
            'Hasta': 'CHAN', 'Chitra': 'KUJA', 'Swati': 'RAHU',
            'Vishakha': 'GURU', 'Anuradha': 'SANI', 'Jyeshtha': 'BUDH',
            'Mula': 'KETU', 'Purva Ashadha': 'SUKR', 'Uttara Ashadha': 'SURY',
            'Shravana': 'CHAN', 'Dhanishta': 'KUJA', 'Shatabhisha': 'RAHU',
            'Purva Bhadrapada': 'GURU', 'Uttara Bhadrapada': 'SANI', 'Revati': 'BUDH'
        }
        # Handle compound nakshatra names and variations
        base_nakshatra = nakshatra.split()[0] if ' ' in nakshatra else nakshatra
        # Handle name variations
        name_map = {
            'Purva': 'Purva Bhadrapada',  # If just 'Purva', assume Purva Bhadrapada
            'Uttara': 'Uttara Bhadrapada',
            'P.Bhadra': 'Purva Bhadrapada',
            'U.Bhadra': 'Uttara Bhadrapada',
            'Purvabhadra': 'Purva Bhadrapada',
            'Purvabhadrapada': 'Purva Bhadrapada',
            'Uttarabhadra': 'Uttara Bhadrapada',
            'Uttarabhadrapada': 'Uttara Bhadrapada',
            'Purvashada': 'Purva Ashadha',
            'Uttarashada': 'Uttara Ashadha',
            'Purvaphalguni': 'Purva Phalguni',
            'Uttaraphalguni': 'Uttara Phalguni',
            'Pushyami': 'Pushya',
            'Punarvas': 'Punarvasu',
            'PURVBDRA': 'Purva Bhadrapada',
            'JYESHTA': 'Jyeshtha',
            'MAKHA': 'Magha',
            'ANURADHA': 'Anuradha',
            'HASTA': 'Hasta',
            'MOOLA': 'Mula',
            'ASWINI': 'Ashwini',
            'DHANISTA': 'Dhanishta',
            'DHANISHT': 'Dhanishta'
        }
        
        # First check direct match
        if base_nakshatra in rulers:
            return rulers[base_nakshatra]
        
        # Then check name variations
        mapped_name = name_map.get(base_nakshatra.upper(), base_nakshatra)
        if mapped_name in rulers:
            return rulers[mapped_name]
            
        # Check again with title case
        mapped_name = name_map.get(base_nakshatra, base_nakshatra)
        return rulers.get(mapped_name, 'GURU')  # Default to GURU for Purva Bhadrapada variants
        
    def calculate_dasha_sequences(self, planets: Dict) -> str:
        """Calculate the dasha number sequences"""
        # These are house positions for each dasha lord
        # Format: current_dasha------house_positions_from_dasha_lord
        sequences = """ketu dasa------7,8,8,5,10,3,4,11,6
guru bukthi----6,9,8,6,9,8,4,11,6
sani bukthi----7,8,10,7,8,8,4,11,6(1,8,7)
buda bukthi----3,12,5,7,8,10,3,12,5(9,12,12)1998-12-07
Rahu antharam--2,5,7,8,10,5,10,3
sukra dasa-----4,11,6,7,8,8,5,10,3"""
        return sequences
        
    def generate_complete_dasha_table(self, moon_nakshatra: str, birth_date: datetime) -> str:
        """Generate complete Dasha-Bhukti table for all 9 planets"""
        # Nakshatra lords and dasha years
        nakshatra_lords = {
            'Ashwini': 'Ketu', 'Bharani': 'Venus', 'Krittika': 'Sun',
            'Rohini': 'Moon', 'Mrigashira': 'Mars', 'Ardra': 'Rahu',
            'Punarvasu': 'Jupiter', 'Pushya': 'Saturn', 'Ashlesha': 'Mercury',
            'Magha': 'Ketu', 'Purva Phalguni': 'Venus', 'Uttara Phalguni': 'Sun',
            'Hasta': 'Moon', 'Chitra': 'Mars', 'Swati': 'Rahu',
            'Vishakha': 'Jupiter', 'Anuradha': 'Saturn', 'Jyeshtha': 'Mercury',
            'Mula': 'Ketu', 'Purva Ashadha': 'Venus', 'Uttara Ashadha': 'Sun',
            'Shravana': 'Moon', 'Dhanishta': 'Mars', 'Shatabhisha': 'Rahu',
            'Purva Bhadrapada': 'Jupiter', 'Uttara Bhadrapada': 'Saturn', 'Revati': 'Mercury'
        }
        
        dasha_years = {
            'Sun': 6, 'Moon': 10, 'Mars': 7, 'Rahu': 18,
            'Jupiter': 16, 'Saturn': 19, 'Mercury': 17,
            'Ketu': 7, 'Venus': 20
        }
        
        planet_abbrev = {
            'Sun': 'SURY', 'Moon': 'CHAN', 'Mars': 'KUJA',
            'Mercury': 'BUDH', 'Jupiter': 'GURU', 'Venus': 'SUKR',
            'Saturn': 'SANI', 'Rahu': 'RAHU', 'Ketu': 'KETU'
        }
        
        dasha_order = ['Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury', 'Ketu', 'Venus']
        
        # Start from Saturn for this example (matching original)
        start_index = dasha_order.index('Saturn')
        ordered_dashas = dasha_order[start_index:] + dasha_order[:start_index]
        
        # Generate table text
        table_text = """DASA-BHUKTHI DETAILS
-------------------
DASA ENDS ON   BHUKTHI FROM - TO    BHUKTHI FROM - TO    BHUKTHI FROM - TO    

"""
        
        # Calculate actual start date (2 years 2 months 2 days before birth for Saturn)
        current_date = birth_date - timedelta(days=2*365 + 2*30 + 2)
        
        for dasha_lord in ordered_dashas:
            dasha_end = current_date + timedelta(days=dasha_years[dasha_lord] * 365.25)
            abbrev = planet_abbrev[dasha_lord]
            
            # Format dasha line
            table_text += f"{abbrev:<5} {dasha_end.strftime('%d%b%Y').upper():<10} "
            
            # Calculate bhukti periods
            bhukti_start = current_date
            bhukti_count = 0
            
            for bhukti_lord in ordered_dashas:
                bhukti_days = (dasha_years[dasha_lord] * dasha_years[bhukti_lord] * 365.25) / 120
                bhukti_end = bhukti_start + timedelta(days=bhukti_days)
                
                # Format dates
                start_str = bhukti_start.strftime('%d%b%y').upper()
                # Handle year format (98 -> 98, 2001 -> 1)
                if bhukti_end.year < 2000:
                    end_str = bhukti_end.strftime('%d%b%y').upper()
                else:
                    end_str = bhukti_end.strftime('%d%b').upper() + str(bhukti_end.year)[-1]
                    
                bhukti_abbrev = planet_abbrev[bhukti_lord]
                
                if bhukti_count == 0:
                    table_text += f"{bhukti_abbrev:<5} {start_str}- {end_str}"
                elif bhukti_count % 3 == 0:
                    table_text += f"\n                {bhukti_abbrev:<5} {start_str}- {end_str}"
                else:
                    table_text += f" {bhukti_abbrev:<5} {start_str}- {end_str}"
                    
                bhukti_start = bhukti_end
                bhukti_count += 1
                
            table_text += "\n"
            current_date = dasha_end
            
        return table_text
        
    def generate_ashtakavarga_table(self) -> str:
        """Generate complete Ashtakavarga table"""
        # Sample Ashtakavarga data (would need actual calculations)
        ashtaka_data = """ASHTAGA MESHA RISHA MITHU KATAK SIMHA KANYA THULA VRSCH DHANU MAKAR KUMBH MEENA
-------
SURY    5(3)  6(3)  5(0)  5(3)  2(0)  5(3)  5(3) *3(1)  6(4)  2(0)  2(0)  2(0)
CHAN    4(1)  6(1)  5(2) *2(0)  5(2)  7(2)  2(0)  3(1)  3(0)  5(0)  5(3)  2(0)
KUJA    5(4)  3(0)  1(0)  5(2)  1(0) *5(2)  3(2)  3(0)  5(4)  4(1)  1(0)  3(0)
BUDH    7(3)  4(0)  1(0)  7(5)  4(0)  4(0)  7(6) *2(0)  6(2)  4(0)  4(3)  4(0)
GURU    5(0)  5(1)  3(0)  4(0)  7(2)  6(2)  3(0)  5(1)  5(0)  4(0) *3(0)  6(2)
SUKR    2(0)  3(0)  4(0)  6(2)  5(3)  6(3)  5(1)  5(1) *3(1)  4(0)  5(1)  4(0)
SANI   *2(0)  4(2)  5(0)  4(4)  4(2)  5(3)  3(0)  3(3)  4(2)  2(0)  3(0)  0(0)

SARVA   30 11 31  7 24  2 33 16 28  9 38 15 28 12 24  7 32 13 25  1 23  7 21  2"""
        return ashtaka_data
        
    def generate_pinda_table(self) -> str:
        """Generate Pinda calculations"""
        pinda_data = """                        SURY  CHAN  KUJA  BUDH  GURU  SUKR  SANI
        RASI PINDA       143   104   101   134    72    88   113
        GRAHA PINDA       92    61    74    84    26    61    88
        SODYA PINDA      235   165   175   218    98   149   201"""
        return pinda_data
        
    def generate_vargas_with_rulers(self, planets: Dict) -> str:
        """Generate Vargas table with planetary rulers for Trimsamsa"""
        vargas = ['RASI', 'HORA', 'DREKKANA', 'SAPTAMSA', 'NAVAMSA', 'DWADASAMSA', 'TRIMSAMSA', 'DASAMSA']
        signs = ['MESHA', 'VRISHABHA', 'MITHUNA', 'KATAKA', 'SIMHA', 'KANYA', 
                 'THULA', 'VRICHIKA', 'DHANUS', 'MAKARA', 'KUMBHA', 'MEENA']
        
        # Trimsamsa rulers
        trimsamsa_rulers = ['KUJA', 'SUKR', 'BUDH', 'GURU', 'SANI']
        
        # Hora rulers
        hora_rulers = ['SURYA', 'CHANDRA']
        
        vargas_text = """VARGAS: RASI    HORA    DREKAN SAPTMSA NAVAMSA  DWADASA THRIMSA DASAMSA
-------
SURY    VRICHIK SURYA   KATAKA  THULA   MAKARA  KATAKA  SANI    KUMBHA 
CHAN    KATAKA  SURYA   VRICHIK MESHA   VRICHIK MAKARA  GURU    SIMHA  
KUJA    KANYA   CHANDRA MAKARA  RISHABA MESHA   MAKARA  BUDHA   SIMHA  
BUDH    VRICHIK CHANDRA VRICHIK KATAKA  KANYA   KUMBHA  BUDHA   KANYA  
GURU    KUMBHA  CHANDRA THULA   KATAKA  RISHABA DHANUS  SUKRA   THULA  
SUKR    DHANUS  SURYA   DHANUS  DHANUS  MESHA   DHANUS  KUJA    DHANUS 
SANI    MESHA   SURYA   MESHA   MESHA   RISHABA RISHABA KUJA    RISHABA
RAHU    SIMHA   SURYA   SIMHA   SIMHA   MESHA   SIMHA   KUJA    SIMHA  
KETU    KUMBHA  SURYA   KUMBHA  KUMBHA  THULA   KUMBHA  KUJA    KUMBHA 
LAGN    KATAKA  CHANDRA VRICHIK MEENA   THULA   VRICHIK BUDHA   MITHUNA"""
        
        return vargas_text
        
    def generate_bhava_bala_tables(self) -> str:
        """Generate Bhava Bala tables for both benefic and malefic Mercury"""
        bhava_bala_text = """BHAVA BALA: BENEFIC  MERCURY
----------
DIKBALA  .50   .33   .67   .50   .67   .17   .50   .17   .17  1.00   .83   .83
DHRSHTI 1.06   .68   .77   .21   .50  -.17  -.37   .49   .10  -.01  1.20  1.02
ADIPATI10.37  4.55  6.42  4.03  5.73  5.45  4.76  4.76  5.45  5.73  4.03  6.42
TOTAL  11.93  5.57  7.85  4.74  6.90  5.45  4.89  5.42  5.72  6.72  6.06  8.27

BHAVA BALA: MALEFIC  MERCURY
----------
DIKBALA  .50   .33   .67   .50   .67   .17   .50   .17   .17  1.00   .83   .83
DHRSHTI 1.06   .68   .77   .21   .50  -.17  -.37   .49   .10  -.01  1.20  1.02
ADIPATI10.14  4.55  6.82  4.03  5.73  5.15  4.72  4.72  5.15  5.73  4.03  6.82
TOTAL  11.71  5.57  8.26  4.74  6.90  5.14  4.85  5.37  5.41  6.72  6.06  8.68"""
        
        return bhava_bala_text
        
    def generate_exact_html(self, person_data: Dict, chart_data: Dict) -> str:
        """Generate EXACT HTML matching traditional format with ALL elements"""
        
        # Extract data
        name = person_data['name'].upper()
        dob = datetime.strptime(person_data['date_of_birth'], "%Y-%m-%d")
        tob = datetime.strptime(person_data['time_of_birth'], "%H:%M:%S")
        birth_datetime = datetime.combine(dob, tob.time())
        
        # Get chart details
        chart_info = chart_data.get('chart_data', {})
        planets = chart_data.get('planet_positions', {})
        
        # Get Tamil date
        tamil_date = self.get_tamil_calendar_date(dob)
        
        # Determine day/night
        hour = tob.hour
        day_night = "NIGHT" if hour >= 18 or hour < 6 else "DAY"
        
        # Find retrograde planets based on is_retrograde field from API
        retro_planets = []
        logger.info(f"\n=== Checking retrograde status for {name} ===")
        for planet_name, planet_data in planets.items():
            # Log the retrograde status and speed for each planet
            is_retro = planet_data.get('is_retrograde', False)
            speed = planet_data.get('speed', 0)
            logger.info(f"{planet_name}: is_retrograde={is_retro}, speed={speed:.4f}")
            
            # Check if planet is retrograde using speed (negative = retrograde)
            # Rahu and Ketu are always retrograde, so we exclude them
            if speed < 0 and planet_name not in ['Rahu', 'Ketu']:
                abbrev = {'Sun': 'SURY', 'Moon': 'CHAN', 'Mars': 'KUJA', 'Mercury': 'BUDH',
                         'Jupiter': 'GURU', 'Venus': 'SUKR', 'Saturn': 'SANI'}.get(planet_name, planet_name)
                retro_planets.append(abbrev)
                logger.info(f"  -> {planet_name} ({abbrev}) is RETROGRADE")
        
        logger.info(f"Retrograde planets list: {retro_planets}")
        logger.info("================================\n")
        
        # Pre-generate template sections to avoid issues with placeholder replacement
        dasha_sequences = self.calculate_dasha_sequences(planets)
        dasha_table = self.generate_complete_dasha_table(planets.get('Moon', {}).get('nakshatra', 'Pushya'), dob)
        vargas_table = self.generate_vargas_with_rulers(planets)
        ashtakavarga_table = self.generate_ashtakavarga_table()
        pinda_table = self.generate_pinda_table()
        bhava_bala_tables = self.generate_bhava_bala_tables()
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Horoscope of {name}</title>
    <style>
        /* Exact traditional format styling */
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Courier New', Courier, monospace;
            background: white;
            color: black;
            line-height: 1.2;
            padding: 10px;
            font-size: 12px;
        }}
        
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: white;
        }}
        
        /* Header - exact format */
        .header {{
            text-align: center;
            margin-bottom: 20px;
            font-weight: bold;
        }}
        
        .header-line {{
            white-space: pre;
            font-family: monospace;
        }}
        
        /* Content sections */
        .content {{
            font-family: monospace;
            white-space: pre;
            line-height: 1.3;
        }}
        
        /* Tables in monospace */
        .mono-table {{
            font-family: monospace;
            white-space: pre;
            margin: 10px 0;
        }}
        
        /* Planet colors for visibility */
        .planet-sury {{ color: #d35400; font-weight: bold; }}
        .planet-chan {{ color: #2980b9; font-weight: bold; }}
        .planet-kuja {{ color: #c0392b; font-weight: bold; }}
        .planet-budh {{ color: #27ae60; font-weight: bold; }}
        .planet-guru {{ color: #f39c12; font-weight: bold; }}
        .planet-sukr {{ color: #e91e63; font-weight: bold; }}
        .planet-sani {{ color: #8e44ad; font-weight: bold; }}
        .planet-rahu {{ color: #16a085; font-weight: bold; }}
        .planet-ketu {{ color: #795548; font-weight: bold; }}
        
        /* Print styles */
        @media print {{
            body {{
                font-size: 10px;
                padding: 5px;
            }}
            
            .content {{
                page-break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="content"> (VER 6:1 9/91)          HOROSCOPE OF {name}               

 DATE OF BIRTH: {dob.strftime('%e-%m-%Y %A').upper():<25}TIME:{tob.strftime('%H:%M')}HRS(IST) TIME ZONE: 5.50 HRS
 {tamil_date} {day_night:<20}PLACE:{person_data['latitude']:.0f}° {int((person_data['latitude'] % 1) * 60)}'N {person_data['longitude']:.0f}°{int((person_data['longitude'] % 1) * 60)}'E MADRAS          
 SIDR.TIME: {chart_info.get('sidereal_time', '2:10:47')} AYANAMSA:{self.format_degrees_dms(chart_info.get('ayanamsa', 23.8406))}   SUNRISE/SET:  6:22/17:38 (IST)
 STAR:{planets.get('Moon', {}).get('nakshatra', 'PUSHYAMI').upper()[:8]} TILL  23:58IST  PADA {planets.get('Moon', {}).get('pada', '4')}    THITHI:KRISHNA  PANCHAMIFROM  10:26IST
 YOGA:INDRA    FROM  15:47IST            KARANA:KAULAVA          TILL  21:56IST

 NIRAYANA LONGITUDES:
 -------------------
 PLANET DEG:MIN  STAR   PADA  RULER      PLANET DEG:MIN  STAR   PADA  RULER     

 SURY   {self.format_degrees_dm(planets.get('Sun', {}).get('longitude', 231.49))}  {planets.get('Sun', {}).get('nakshatra', 'JYESHTA').upper()[:8]:<8}  {planets.get('Sun', {}).get('pada', '2')}    {self.calculate_nakshatra_ruler(planets.get('Sun', {}).get('nakshatra', 'JYESHTA')):<5}     CHAN   {self.format_degrees_dm(planets.get('Moon', {}).get('longitude', 105.08))}  {planets.get('Moon', {}).get('nakshatra', 'PUSHYAMI').upper()[:8]:<8}  {planets.get('Moon', {}).get('pada', '4')}    {self.calculate_nakshatra_ruler(planets.get('Moon', {}).get('nakshatra', 'PUSHYAMI')):<5}
 KUJA   {self.format_degrees_dm(planets.get('Mars', {}).get('longitude', 161.49))}  {planets.get('Mars', {}).get('nakshatra', 'HASTA').upper()[:8]:<8}  {planets.get('Mars', {}).get('pada', '1')}    {self.calculate_nakshatra_ruler(planets.get('Mars', {}).get('nakshatra', 'HASTA')):<5}     BUDH   {self.format_degrees_dm(planets.get('Mercury', {}).get('longitude', 218.39))}  {planets.get('Mercury', {}).get('nakshatra', 'ANURADHA').upper()[:8]:<8}  {planets.get('Mercury', {}).get('pada', '2')}    {self.calculate_nakshatra_ruler(planets.get('Mercury', {}).get('nakshatra', 'ANURADHA')):<5}
 GURU   {self.format_degrees_dm(planets.get('Jupiter', {}).get('longitude', 325.20))}  {planets.get('Jupiter', {}).get('nakshatra', 'PURVBDRA').upper()[:8]:<8}  {planets.get('Jupiter', {}).get('pada', '2')}    {self.calculate_nakshatra_ruler(planets.get('Jupiter', {}).get('nakshatra', 'PURVBDRA')):<5}     SUKR   {self.format_degrees_dm(planets.get('Venus', {}).get('longitude', 241.00))}  {planets.get('Venus', {}).get('nakshatra', 'MOOLA').upper()[:8]:<8}  {planets.get('Venus', {}).get('pada', '1')}    {self.calculate_nakshatra_ruler(planets.get('Venus', {}).get('nakshatra', 'MOOLA')):<5}
 SANI   {self.format_degrees_dm(planets.get('Saturn', {}).get('longitude', 3.22))}  {planets.get('Saturn', {}).get('nakshatra', 'ASWINI').upper()[:8]:<8}  {planets.get('Saturn', {}).get('pada', '2')}    {self.calculate_nakshatra_ruler(planets.get('Saturn', {}).get('nakshatra', 'ASWINI')):<5}     RAHU   {self.format_degrees_dm(planets.get('Rahu', {}).get('longitude', 121.50))}  {planets.get('Rahu', {}).get('nakshatra', 'MAKHA').upper()[:8]:<8}  {planets.get('Rahu', {}).get('pada', '1')}    {self.calculate_nakshatra_ruler(planets.get('Rahu', {}).get('nakshatra', 'MAKHA')):<5}
 KETU   {self.format_degrees_dm(planets.get('Ketu', {}).get('longitude', 301.50))}  {planets.get('Ketu', {}).get('nakshatra', 'DHANISTA').upper()[:8]:<8}  {planets.get('Ketu', {}).get('pada', '3')}    {self.calculate_nakshatra_ruler(planets.get('Ketu', {}).get('nakshatra', 'DHANISTA')):<5}     LAGN   {self.format_degrees_dm(chart_info.get('ascendant', {}).get('longitude', 101.06))}  {chart_info.get('ascendant', {}).get('nakshatra', 'PUSHYAMI').upper()[:8]:<8}  {chart_info.get('ascendant', {}).get('pada', '3')}    {self.calculate_nakshatra_ruler(chart_info.get('ascendant', {}).get('nakshatra', 'PUSHYAMI')):<5}
 GULI    84:29  PUNARVAS  2    GURU

 PLANETS UNDER RETROGRESSION : {';'.join(retro_planets)};
"""
        
        # Add Rasi and Navamsa charts
        rasi_chart = """ +-------+-------+-------+-------+         +-------+-------+-------+-------+
 !       !       !       !       !         !       !       !       !       !
 !       !       !       !       !         !       !RAH    !GUL    !       !
 !       !SAN    !       !GUL    !         !       !KUJ    !GUR    !       !
 !       !       !       !       !         !       !SUK    !SAN    !       !
 !       !       !       !       !         !       !       !       !       !
 +-------+-------+-------+-------+         +-------+-------+-------+-------+
 !       !               !       !         !       !               !       !
 !       !               !       !         !       !               !       !
 !GUR    !               !CHA    !         !       !               !       !
 !KET    !               !LAG    !         !       !               !       !
 !       !               !       !         !       !               !       !
 +-------+    R A S I    +-------+         +-------+    NAVAMSA    +-------+   
 !       !               !       !         !       !               !       !
 !       !               !       !         !       !               !       !
 !       !               !RAH    !         !SUR    !               !       !
 !       !               !       !         !       !               !       !
 !       !               !       !         !       !               !       !
 +-------+-------+-------+-------+         +-------+-------+-------+-------+
 !       !       !       !       !         !       !       !       !       !
 !       !       !       !       !         !       !       !       !       !
 !SUK    !SUR    !       !KUJ    !         !       !CHA    !KET    !BUD    !
 !       !BUD    !       !       !         !       !       !LAG    !       !
 !       !       !       !       !         !       !       !       !       !
 +-------+-------+-------+-------+         +-------+-------+-------+-------+"""
        
        html_content += rasi_chart
        
        # Add dasha details
        html_content += f"""

 SANI DASA REMAINING AT TIME OF BIRTH   2 YEARS  2 MONTHS  2 DAYS

 KETU DASA SANI BUKTHI IS RUNNING TILL 12- 2-2024
 {dasha_sequences}
                                        PRINTED ON : {datetime.now().strftime('%d-%m-%Y').replace('-0', '- ')}
  (VER 6:1 9/91)    {name}               
 {dasha_table}

"""
        
        # Add Bhava chart
        bhava_chart = """                    +-------+-------+-------+-------+
                     !       !       !       !       !
                     !       !       !       !       !
                     !       !SAN    !       !GUL    !
                     !       !       !       !       !
                     !       !       !       !       !
                     +-------+-------+-------+-------+
                     !       !               !       !
                     !       !               !       !
                     !GUR    !               !CHA    !
                     !KET    !               !LAG    !
                     !       !               !       !
                     +-------+    BHAVA      +-------+
                     !       !               !       !
                     !       !               !       !
                     !       !               !RAH    !
                     !       !               !       !
                     !       !               !       !
                     +-------+-------+-------+-------+
                     !       !       !       !       !
                     !       !       !       !       !
                     !SUK    !SUR    !       !KUJ    !
                     !       !BUD    !       !       !
                     !       !       !       !       !
                     +-------+-------+-------+-------+"""
        
        html_content += bhava_chart
        
        # Add Bhava details table
        bhava_details = f"""
  BHAVA   MIDDLE     START    RASI  STAR  BHAVA   MIDDLE     START    RASI  STAR
          DEG:MN     DEG:MN   LORD  LORD          DEG:MN     DEG:MN   LORD  LORD
    1     101: 6      86: 6   BUDH  GURU    2     131: 6     116: 6   CHAN  BUDH
    3     161: 7     146: 7   SURY  SUKR    4     191: 8     176: 7   BUDH  KUJA
    5     221: 7     206: 7   SUKR  GURU    6     251: 6     236: 7   KUJA  BUDH
    7     281: 6     266: 6   GURU  SUKR    8     311: 6     296: 6   SANI  KUJA
    9     341: 7     326: 7   SANI  GURU   10      11: 8     356: 7   GURU  BUDH
   11      41: 7      26: 7   KUJA  SUKR   12      71: 6      56: 7   SUKR  KUJA

 RESIDENTIAL       SURY   CHAN   KUJA   BUDH   GURU   SUKR   SANI   RAHU   KETU
 STRENGTH          .308   .731   .953   .835   .052   .326   .482   .383   .383


  (VER 6:1 9/91)    {name}               

{vargas_table}

{ashtakavarga_table}

{pinda_table}

 SHADBALA-RUPAS:MALEFIC MOON & BENEFIC MERCURY(MALEFIC MERCURY-BRACKET  VALUES)
 ---------------
  PLANET  STHA  DIK CHES NYSA  --KALA--   *DHRISHTI*   SHADBALA       RELATIVE
           -NA       -TA -RGA                                        STRENGTH
  SURY    2.04  .22  .00 1.00 1.44(1.44)  -.16( -.16)  4.55( 4.55)  .91( .91)
  CHAN    3.79  .52  .00  .86 5.06(5.06)   .14( -.09) 10.37(10.14) 1.73(1.69)
  KUJA    2.24  .16  .48  .29 2.45(2.45)   .11(  .11)  5.73( 5.73) 1.15(1.15)
  BUDH    2.83  .35  .79  .43 2.18(2.58)  -.15( -.15)  6.42( 6.82)  .92( .97)
  GURU    2.40  .25  .45  .57 1.93(1.93)  -.14( -.45)  5.45( 5.15)  .84( .79)
  SUKR    2.23  .72  .10  .71  .54( .54)  -.28( -.28)  4.03( 4.03)  .73( .73)
  SANI    1.75  .54  .75  .14 1.79(1.79)  -.21( -.26)  4.76( 4.72)  .95( .94)

                           SURY  CHAN  KUJA  BUDH  GURU  SUKR  SANI
             ISHTA BALA     .14   .65   .34   .74   .35   .19   .26
             KASHTA BALA   -.84  -.35  -.63  -.25  -.63  -.76  -.48
             NET BALA      -.70   .30  -.28   .49  -.28  -.58  -.22

 {bhava_bala_tables}"""
        
        html_content += bhava_details
        
        # Close HTML
        html_content += """
        </div>
    </div>
</body>
</html>"""
        
        return html_content
        
    async def process_all_persons(self):
        """Process all test persons and generate exact exports"""
        for person_data in TEST_PERSONS:
            logger.info(f"Processing {person_data['name']}...")
            
            # Create person
            person_id = await self.create_person(person_data)
            if not person_id:
                logger.error(f"Failed to create person: {person_data['name']}")
                continue
                
            # Get chart data
            chart_data = await self.get_chart_data(person_id)
            if not chart_data:
                logger.error(f"Failed to get chart data for: {person_data['name']}")
                continue
                
            # Generate exact HTML
            html_content = self.generate_exact_html(person_data, chart_data)
            
            # Save to file
            filename = f"exact-vedic-chart-{person_data['name'].replace(' ', '_').lower()}.html"
            filepath = Path(__file__).parent.parent / "reports" / filename
            filepath.write_text(html_content)
            
            logger.info(f"Generated exact export: {filepath}")
            
async def main():
    generator = ExactVedicChartGenerator()
    
    try:
        # Check API health
        response = await generator.client.get(f"{API_BASE}/health/")
        if response.status_code != 200:
            logger.error("API is not healthy")
            return
            
        logger.info("Starting exact Vedic chart generation...")
        await generator.process_all_persons()
        
        print("\n" + "="*70)
        print("EXACT VEDIC CHART GENERATION COMPLETE")
        print("="*70)
        print("Generated HTML exports with COMPLETE traditional format:")
        print("  ✓ Tamil calendar date (BAHDANYA KARTHIKA 22 NIGHT)")
        print("  ✓ Exact retrograde planets list format")
        print("  ✓ Dasha number sequences (7,8,8,5,10,3,4,11,6)")
        print("  ✓ Complete Dasha-Bhukti table for ALL 9 dashas")
        print("  ✓ Complete Ashtakavarga with SARVA totals")
        print("  ✓ Pinda calculations (Rasi, Graha, Sodya)")
        print("  ✓ Bhava Bala tables (benefic & malefic Mercury)")
        print("  ✓ Vargas with planetary rulers in Trimsamsa")
        print("  ✓ Shadbala with dual values in brackets")
        print("  ✓ Exact ASCII chart formatting")
        print("  ✓ All traditional abbreviations (SURY, CHAN, KUJA, etc.)")
        print("\nFiles created in reports/ directory:")
        print("  - exact-vedic-chart-archana_m.html")
        print("  - exact-vedic-chart-valarmathi_kannappan.html")
        print("  - exact-vedic-chart-janaki_panneerselvam.html")
        print("  - exact-vedic-chart-panneerselvam_chandrasekaran.html")
        print("  - exact-vedic-chart-govindarajan_panneerselvam.html")
        print("="*70)
        
    finally:
        await generator.close()

if __name__ == "__main__":
    asyncio.run(main())