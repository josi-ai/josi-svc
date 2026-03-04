#!/usr/bin/env python3
"""
Generate traditional Vedic astrology chart export format from Josi API data.
This creates HTML files that replicate the exact traditional format.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
import pytz
from src.josi.services.astrology_service import AstrologyCalculator
from src.josi.services.tamil_calendar import TamilCalendar
from src.josi.services.nakshatra_utils import NakshatraUtils
from src.josi.services.dasa_results_calculator import DasaResultsCalculator
from src.josi.services.compressed_dasa_formatter import CompressedDasaFormatter
from src.josi.services.enhanced_strength_calculator import EnhancedStrengthCalculator
from src.josi.services.ashtakavarga_calculator import AshtakavargaCalculator
from src.josi.services.vargas_formatter import VargasFormatter
import math

# Test persons data
ALL_PERSONS = [
    {
        "name": "ARCHANA M",
        "gender": "female",
        "date_of_birth": "1998-12-07",
        "time_of_birth": "21:15:00",
        "place_of_birth": "MADRAS",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "timezone": "Asia/Kolkata"
    },
    {
        "name": "VALARMATHI KANNAPPAN",
        "gender": "female",
        "date_of_birth": "1961-02-11",
        "time_of_birth": "15:30:00",
        "place_of_birth": "KOVUR",
        "latitude": 13.1622,
        "longitude": 80.005,
        "timezone": "Asia/Kolkata"
    },
    {
        "name": "JANAKI PANNEERSELVAM",
        "gender": "female",
        "date_of_birth": "1982-12-18",
        "time_of_birth": "10:10:00",
        "place_of_birth": "CHENNAI",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "timezone": "Asia/Kolkata"
    },
    {
        "name": "GOVINDARAJAN PANNEERSELVAM",
        "gender": "male",
        "date_of_birth": "1989-12-29",
        "time_of_birth": "12:12:00",
        "place_of_birth": "CHENNAI",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "timezone": "Asia/Kolkata"
    },
    {
        "name": "PANNEERSELVAM CHANDRASEKARAN",
        "gender": "male",
        "date_of_birth": "1954-08-20",
        "time_of_birth": "18:20:00",
        "place_of_birth": "KANCHIPURAM",
        "latitude": 12.8185,
        "longitude": 79.6947,
        "timezone": "Asia/Kolkata"
    }
]

# Weekday names
WEEKDAYS = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY']

# Planet abbreviations
PLANET_SHORT = {
    "Sun": "SURY",
    "Moon": "CHAN",
    "Mars": "KUJA",
    "Mercury": "BUDH",
    "Jupiter": "GURU",
    "Venus": "SUKR",
    "Saturn": "SANI",
    "Rahu": "RAHU",
    "Ketu": "KETU"
}

# Nakshatra names mapping
NAKSHATRA_NAMES = {
    "Ashwini": "ASWINI",
    "Bharani": "BHARANI",
    "Krittika": "KRITHIKA",
    "Rohini": "ROHINI",
    "Mrigashira": "MRIGASIR",
    "Ardra": "ARIDRA",
    "Punarvasu": "PUNARVAS",
    "Pushya": "PUSHYAMI",
    "Ashlesha": "ASLESHA",
    "Magha": "MAKHA",
    "Purva Phalguni": "PURAPHAL",
    "Uttara Phalguni": "UTTRAPHAL",
    "Hasta": "HASTA",
    "Chitra": "CHITHRA",
    "Swati": "SWATHI",
    "Vishakha": "VISAKHA",
    "Anuradha": "ANURADHA",
    "Jyeshtha": "JYESHTA",
    "Mula": "MOOLA",
    "Purva Ashadha": "PURASHADA",
    "Uttara Ashadha": "UTTRASADA",
    "Shravana": "SRAVANA",
    "Dhanishta": "DHANISTA",
    "Shatabhisha": "SATABHISH",
    "Purva Bhadrapada": "PURVBDRA",
    "Uttara Bhadrapada": "UTTRBDRA",
    "Revati": "REVATHI"
}

# Nakshatra rulers
NAKSHATRA_RULERS = {
    "ASWINI": "KETU", "BHARANI": "SUKR", "KRITHIKA": "SURY",
    "ROHINI": "CHAN", "MRIGASIR": "KUJA", "ARIDRA": "RAHU",
    "PUNARVAS": "GURU", "PUSHYAMI": "SANI", "ASLESHA": "BUDH",
    "MAKHA": "KETU", "PURAPHAL": "SUKR", "UTTRAPHAL": "SURY",
    "HASTA": "CHAN", "CHITHRA": "KUJA", "SWATHI": "RAHU",
    "VISAKHA": "GURU", "ANURADHA": "SANI", "JYESHTA": "BUDH",
    "MOOLA": "KETU", "PURASHADA": "SUKR", "UTTRASADA": "SURY",
    "SRAVANA": "CHAN", "DHANISTA": "KUJA", "SATABHISH": "RAHU",
    "PURVBDRA": "GURU", "UTTRBDRA": "SANI", "REVATHI": "BUDH",
    # Alternative spellings
    "PURASHAD": "SUKR", "UTTRASAD": "SURY", "SATABHIS": "RAHU"
}

def calculate_chart(person: dict) -> dict:
    """Calculate chart using Josi AstrologyCalculator."""
    calc = AstrologyCalculator()
    
    # Parse datetime
    dob_parts = person['date_of_birth'].split('-')
    tob_parts = person['time_of_birth'].split(':')
    
    dt = datetime(
        int(dob_parts[0]), int(dob_parts[1]), int(dob_parts[2]),
        int(tob_parts[0]), int(tob_parts[1]), int(tob_parts[2])
    )
    
    # Calculate chart
    chart = calc.calculate_vedic_chart(
        dt=dt,
        latitude=person['latitude'],
        longitude=person['longitude'],
        timezone=person['timezone'],
        house_system='placidus'
    )
    
    return chart, dt

def format_degrees(longitude):
    """Format degrees as DEG:MIN."""
    deg = int(longitude)
    min = int((longitude - deg) * 60)
    return f"{deg:3d}:{min:2d}"

def format_lat_lon(value, is_lat=True):
    """Format latitude/longitude."""
    deg = int(abs(value))
    min = int((abs(value) - deg) * 60)
    if is_lat:
        dir = 'N' if value >= 0 else 'S'
    else:
        dir = 'E' if value >= 0 else 'W'
    return f"{deg:2d}°{min:2d}'{dir}"

def is_mercury_benefic(chart):
    """
    Determine if Mercury is benefic or malefic.
    
    Rules:
    1. Mercury alone or with benefics = Benefic
    2. Mercury with malefics = Malefic
    3. Check conjunctions within 10 degrees
    """
    if 'planets' not in chart or 'Mercury' not in chart['planets']:
        return True  # Default benefic
    
    mercury = chart['planets']['Mercury']
    mercury_long = mercury['longitude']
    mercury_sign = mercury.get('sign', '')
    
    benefics = ['Moon', 'Jupiter', 'Venus']
    malefics = ['Sun', 'Mars', 'Saturn', 'Rahu', 'Ketu']
    
    # Check conjunctions
    conjunct_benefics = 0
    conjunct_malefics = 0
    
    for planet, data in chart['planets'].items():
        if planet == 'Mercury':
            continue
        
        # Check if in same sign or within 10 degrees
        planet_long = data['longitude']
        distance = abs(mercury_long - planet_long)
        if distance > 180:
            distance = 360 - distance
        
        if distance <= 10 or data.get('sign') == mercury_sign:
            if planet in benefics:
                conjunct_benefics += 1
            elif planet in malefics:
                conjunct_malefics += 1
    
    # Mercury is malefic if conjunct more malefics than benefics
    return conjunct_malefics <= conjunct_benefics

def create_rasi_chart(planets, ascendant):
    """Create RASI chart in the exact format."""
    # Initialize houses
    houses = [[] for _ in range(12)]
    
    # Get ascendant sign
    asc_sign_num = int(ascendant['longitude'] / 30)
    
    # Place planets
    for planet, data in planets.items():
        sign_num = int(data['longitude'] / 30)
        planet_short = PLANET_SHORT.get(planet, planet[:3].upper())
        houses[sign_num].append(planet_short)
    
    # Add Lagn to ascendant house
    houses[asc_sign_num].append("LAG")
    
    # Format chart
    lines = []
    lines.append("+-------+-------+-------+-------+")
    lines.append("!       !       !       !       !")
    
    # House 12, 1, 2, 3 (top row)
    row1 = ["", "", "", ""]
    for i, house_idx in enumerate([11, 0, 1, 2]):
        if houses[house_idx]:
            row1[i] = houses[house_idx][0] if houses[house_idx] else ""
    
    lines.append(f"!{row1[0]:^7}!{row1[1]:^7}!{row1[2]:^7}!{row1[3]:^7}!")
    
    # Add additional planets if any
    max_planets = max(len(houses[i]) for i in [11, 0, 1, 2])
    for p_idx in range(1, max_planets):
        row = ["", "", "", ""]
        for i, house_idx in enumerate([11, 0, 1, 2]):
            if len(houses[house_idx]) > p_idx:
                row[i] = houses[house_idx][p_idx]
        if any(row):
            lines.append(f"!{row[0]:^7}!{row[1]:^7}!{row[2]:^7}!{row[3]:^7}!")
    
    lines.append("!       !       !       !       !")
    lines.append("!       !       !       !       !")
    lines.append("+-------+-------+-------+-------+")
    
    # Middle section
    lines.append("!       !               !       !")
    lines.append("!       !               !       !")
    
    # Houses 11 and 4
    h10_str = ' '.join(houses[10][:2]) if houses[10] else ''
    h3_str = ' '.join(houses[3][:2]) if houses[3] else ''
    lines.append(f"!{h10_str:^7}!               !{h3_str:^7}!")
    
    lines.append("!       !               !       !")
    lines.append("!       !               !       !")
    lines.append("+-------+    R A S I    +-------+")
    lines.append("!       !               !       !")
    lines.append("!       !               !       !")
    
    # Houses 10 and 5
    h9_str = ' '.join(houses[9][:2]) if houses[9] else ''
    h4_str = ' '.join(houses[4][:2]) if houses[4] else ''
    lines.append(f"!{h9_str:^7}!               !{h4_str:^7}!")
    
    lines.append("!       !               !       !")
    lines.append("!       !               !       !")
    lines.append("+-------+-------+-------+-------+")
    lines.append("!       !       !       !       !")
    lines.append("!       !       !       !       !")
    
    # Houses 9, 8, 7, 6 (bottom row)
    row3 = ["", "", "", ""]
    for i, house_idx in enumerate([8, 7, 6, 5]):
        if houses[house_idx]:
            row3[i] = ' '.join(houses[house_idx][:2])
    
    lines.append(f"!{row3[0]:^7}!{row3[1]:^7}!{row3[2]:^7}!{row3[3]:^7}!")
    lines.append("!       !       !       !       !")
    lines.append("!       !       !       !       !")
    lines.append("+-------+-------+-------+-------+")
    
    return '\n'.join(lines)

def generate_traditional_format(person, chart, dt):
    """Generate the complete traditional format."""
    lines = []
    
    # Header
    lines.append(f" (VER 6:1 9/91)          HOROSCOPE OF {person['name']:<30}")
    lines.append("")
    
    # Date and time info
    weekday = WEEKDAYS[dt.weekday()]
    date_str = f"{dt.day:2d}-{dt.month:2d}-{dt.year}"
    time_str = f"{dt.hour:2d}:{dt.minute:02d}HRS(IST)"
    
    lines.append(f" DATE OF BIRTH:{date_str:<16} {weekday:<12} TIME:{time_str} TIME ZONE: 5.50 HRS")
    
    # Tamil calendar info
    tamil_cal = TamilCalendar()
    sun_long = chart['planets']['Sun']['longitude']
    tamil_date = tamil_cal.get_tamil_date(dt, sun_long)
    
    # Get paksha and tithi info for Tamil display
    if chart.get('panchang') and chart['panchang'].get('tithi'):
        paksha_tithi = tamil_cal.get_paksha_tithi_tamil(
            chart['panchang']['tithi'],
            chart['planets']['Moon']['longitude'],
            dt
        )
        tamil_info = tamil_cal.format_tamil_calendar_info(tamil_date, paksha_tithi)
    else:
        tamil_info = f"TAMIL: {tamil_date['month'].upper()} {tamil_date['day']:2d}, {tamil_date['year']}"
    
    # Place info
    lat_str = format_lat_lon(person['latitude'], True)
    lon_str = format_lat_lon(person['longitude'], False)
    lines.append(f" {tamil_info:<40} PLACE:{lat_str} {lon_str} {person['place_of_birth']:<20}")
    
    # Astronomical data with placeholders
    ayanamsa_deg = int(chart['ayanamsa'])
    ayanamsa_min = int((chart['ayanamsa'] - ayanamsa_deg) * 60)
    ayanamsa_sec = int(((chart['ayanamsa'] - ayanamsa_deg) * 60 - ayanamsa_min) * 60)
    
    # Get sunrise/sunset and sidereal time from panchang if available
    if chart.get('panchang'):
        sidereal_time = chart['panchang'].get('sidereal_time', '[ERROR]')
        sunrise = chart['panchang'].get('sunrise', '[ERROR]')
        sunset = chart['panchang'].get('sunset', '[ERROR]')
        sunrise_sunset_str = f"{sunrise}/{sunset} (IST)"
    else:
        sidereal_time = "[PENDING]"
        sunrise_sunset_str = "[CALCULATION PENDING]"
    
    lines.append(f" SIDR.TIME: {sidereal_time} AYANAMSA:{ayanamsa_deg:2d}°{ayanamsa_min:2d}'{ayanamsa_sec:2d}\"   SUNRISE/SET: {sunrise_sunset_str}")
    
    # Panchang data
    moon_nakshatra = NAKSHATRA_NAMES.get(chart['planets']['Moon']['nakshatra'], chart['planets']['Moon']['nakshatra'])
    moon_pada = chart['planets']['Moon']['pada']
    
    # Check if panchang data is available
    if chart.get('panchang'):
        panchang = chart['panchang']
        
        # Format tithi with end time
        tithi_name = panchang['tithi']['name'].upper()
        paksha = panchang['tithi']['paksha'].upper()
        if 'end_time' in panchang['tithi']:
            # Convert to 12-hour format
            end_time = panchang['tithi']['end_time']
            hour, minute = map(int, end_time.split(':'))
            period = "AM" if hour < 12 else "PM"
            if hour == 0:
                hour = 12
            elif hour > 12:
                hour -= 12
            tithi_str = f"{paksha:<8} {tithi_name} UPTO {hour}:{minute:02d} {period}"
        else:
            tithi_str = f"{paksha:<8} {tithi_name}"
        
        # Format yoga with end time
        yoga_name = panchang['yoga']['name'].upper()
        if 'end_time' in panchang['yoga']:
            end_time = panchang['yoga']['end_time']
            hour, minute = map(int, end_time.split(':'))
            period = "AM" if hour < 12 else "PM"
            if hour == 0:
                hour = 12
            elif hour > 12:
                hour -= 12
            yoga_str = f"{yoga_name} UPTO {hour}:{minute:02d} {period}"
        else:
            yoga_str = yoga_name
        
        # Format karana with end time
        karana_name = panchang['karana']['name'].upper()
        if 'end_time' in panchang['karana']:
            end_time = panchang['karana']['end_time']
            hour, minute = map(int, end_time.split(':'))
            period = "AM" if hour < 12 else "PM"
            if hour == 0:
                hour = 12
            elif hour > 12:
                hour -= 12
            karana_str = f"{karana_name} UPTO {hour}:{minute:02d} {period}"
        else:
            karana_str = karana_name
        
        sunrise = panchang.get('sunrise', '[ERROR]')
        sunset = panchang.get('sunset', '[ERROR]')
        sidereal_time = panchang.get('sidereal_time', '[ERROR]')
    else:
        tithi_str = "[CALCULATION PENDING]"
        yoga_str = "[PENDING]"
        karana_str = "[CALCULATION PENDING]"
        sunrise = "[CALCULATION PENDING]"
        sunset = "[CALCULATION PENDING]"
        sidereal_time = "[PENDING]"
    
    # Get nakshatra end time if available
    nakshatra_end_str = ""
    if panchang and panchang.get('nakshatra_end_time'):
        from src.josi.services.nakshatra_end_time_calculator import NakshatraEndTimeCalculator
        calc = NakshatraEndTimeCalculator()
        nakshatra_end_str = calc.format_nakshatra_with_end_time(panchang['nakshatra_end_time'])
    else:
        nakshatra_end_str = "[TIME PENDING]"
    
    lines.append(f" STAR:{moon_nakshatra:<10} {nakshatra_end_str:<15} PADA {moon_pada}    THITHI:{tithi_str}")
    lines.append(f" YOGA:{yoga_str:<32}    KARANA:{karana_str:<20}")
    lines.append("")
    
    # Nirayana longitudes
    lines.append(" NIRAYANA LONGITUDES:")
    lines.append(" -------------------")
    lines.append(" PLANET DEG:MIN  STAR   PADA  RULER      PLANET DEG:MIN  STAR   PADA  RULER     ")
    lines.append("")
    
    # Planet positions in two columns
    planet_order = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']
    
    for i in range(0, len(planet_order), 2):
        left_planet = planet_order[i]
        right_planet = planet_order[i+1] if i+1 < len(planet_order) else None
        
        # Left column
        if left_planet in chart['planets']:
            p_data = chart['planets'][left_planet]
            p_short = PLANET_SHORT[left_planet]
            deg_str = format_degrees(p_data['longitude'])
            nak = NAKSHATRA_NAMES.get(p_data['nakshatra'], p_data['nakshatra'])[:8]
            pada = p_data['pada']
            ruler = NakshatraUtils.get_ruler_short_form(
                NakshatraUtils.get_nakshatra_ruler(p_data['nakshatra'])
            )
            left_str = f" {p_short:<6} {deg_str:<7} {nak:<10} {pada}    {ruler:<4}"
        else:
            left_str = " " * 40
        
        # Right column
        if right_planet and right_planet in chart['planets']:
            p_data = chart['planets'][right_planet]
            p_short = PLANET_SHORT[right_planet]
            deg_str = format_degrees(p_data['longitude'])
            nak = NAKSHATRA_NAMES.get(p_data['nakshatra'], p_data['nakshatra'])[:8]
            pada = p_data['pada']
            ruler = NakshatraUtils.get_ruler_short_form(
                NakshatraUtils.get_nakshatra_ruler(p_data['nakshatra'])
            )
            right_str = f" {p_short:<6} {deg_str:<7} {nak:<10} {pada}    {ruler:<4}"
        else:
            right_str = ""
        
        lines.append(left_str + "     " + right_str)
    
    # Add ascendant
    asc_deg_str = format_degrees(chart['ascendant']['longitude'])
    asc_nak = NAKSHATRA_NAMES.get(chart['ascendant']['nakshatra'], chart['ascendant']['nakshatra'])[:8]
    asc_pada = chart['ascendant']['pada']
    asc_ruler = NakshatraUtils.get_ruler_short_form(
        NakshatraUtils.get_nakshatra_ruler(chart['ascendant']['nakshatra'])
    )
    lines.append(f" LAGN   {asc_deg_str:<7} {asc_nak:<10} {asc_pada}    {asc_ruler:<4}")
    
    # Add Gulika if available
    if chart.get('panchang') and chart['panchang'].get('gulika'):
        gulika = chart['panchang']['gulika']
        guli_deg_str = format_degrees(gulika['longitude'])
        guli_nak = gulika.get('nakshatra', '[PENDING]')
        guli_pada = gulika.get('pada', 1)
        guli_ruler = gulika.get('ruler', '')
        
        if guli_nak != '[PENDING]':
            guli_nak_display = NAKSHATRA_NAMES.get(guli_nak, guli_nak)[:8]
            guli_ruler_short = NakshatraUtils.get_ruler_short_form(guli_ruler)
            lines.append(f" GULI   {guli_deg_str:<7} {guli_nak_display:<10} {guli_pada}    {guli_ruler_short:<4}")
        else:
            lines.append(f" GULI   {guli_deg_str:<7} [NAKSHATRA PENDING]")
    else:
        lines.append(" GULI   [CALCULATION PENDING]")
    lines.append("")
    
    # Retrograde planets
    retro_planets = []
    for planet, data in chart['planets'].items():
        if data.get('speed', 0) < 0 and planet not in ['Rahu', 'Ketu']:
            retro_planets.append(PLANET_SHORT.get(planet, planet[:4]))
    
    if retro_planets:
        lines.append(f" PLANETS UNDER RETROGRESSION : {';'.join(retro_planets)};")
    
    # Charts side by side
    rasi_chart = create_rasi_chart(chart['planets'], chart['ascendant'])
    rasi_lines = rasi_chart.split('\n')
    
    # Create placeholder navamsa chart
    navamsa_lines = []
    for line in rasi_lines:
        navamsa_lines.append(line.replace("R A S I", "NAVAMSA"))
    
    # Combine charts side by side
    for i in range(len(rasi_lines)):
        lines.append(f" {rasi_lines[i]}         {navamsa_lines[i]}")
    
    lines.append("")
    
    # Add Bhava Chart
    if chart.get('bhava_chart'):
        bhava_data = chart['bhava_chart']
        
        # Add blank line
        lines.append("")
        
        # Create bhava chart display
        from src.josi.services.bhava_calculator import BhavaCalculator
        bhava_calc = BhavaCalculator()
        
        # Generate bhava chart
        bhava_lines = bhava_calc.create_bhava_chart_display(
            bhava_data, chart['planets']
        )
        lines.extend(bhava_lines)
        
        # Add bhava details table
        lines.append("")
        table_lines = bhava_calc.create_bhava_details_table(bhava_data)
        lines.extend(table_lines)
    else:
        # Add placeholder
        lines.append("")
        lines.append(" BHAVA CHART: [CALCULATION PENDING]")
    
    lines.append("")
    
    # Dasa calculations
    if chart.get('dasa'):
        dasa = chart['dasa']
        lines.append(" BALANCE OF DASA AT BIRTH:")
        birth_balance = dasa['birth_balance']
        lines.append(f" {birth_balance['planet'].upper():<8} {birth_balance['years']} YEARS {birth_balance['months']} MONTHS {birth_balance['days']} DAYS")
        lines.append("")
        
        # Current dasa-bhukti
        current = dasa['current']
        lines.append(f" CURRENT DASA: {current['major'].upper()} FROM {current['major_start']} TO {current['major_end']}")
        if current.get('minor'):
            lines.append(f" CURRENT BHUKTI: {current['minor'].upper()} FROM {current['minor_start']} TO {current['minor_end']}")
        lines.append("")
        
        # Add cryptic dasa result lines
        dasa_calc = DasaResultsCalculator()
        birth_date_str = dt.strftime('%Y-%m-%d')
        current_dasa_lord = birth_balance['planet']  # Use birth balance planet for results
        
        result_lines = dasa_calc.calculate_full_dasa_results(
            current_dasa_lord, birth_date_str, chart
        )
        
        # Add the cryptic lines
        lines.extend(result_lines)
        lines.append("")
        
        # Add basic dasa table first (for comparison)
        lines.append("BALANCE OF DASA AT BIRTH:")
        lines.append(f"{birth_balance['planet'].upper():<8} {birth_balance['years']} YEARS {birth_balance['months']} MONTHS {birth_balance['days']} DAYS")
        lines.append("")
        
        # Add simple dasa periods
        lines.append("DASA BHUKTI PERIODS:")
        lines.append("-" * 70)
        lines.append("")
        
        # Show first few dasas in simple format
        if 'periods' in dasa:
            dasa_periods = dasa['periods']
            for i, period in enumerate(dasa_periods[:3]):  # Show first 3 dasas
                lines.append(f"{period['planet'].upper()} DASA: {period['start_date']} TO {period['end_date']}")
                
                # Show first 5 bhuktis
                if 'bhuktis' in period:
                    for j, bhukti in enumerate(period['bhuktis'][:5]):
                        lines.append(f"  {bhukti['planet']:<8} {bhukti['start_date']} TO {bhukti['end_date']}")
                lines.append("")
        
        # Add compressed dasa table
        lines.append("")
        try:
            compressed_formatter = CompressedDasaFormatter()
            
            # Calculate dasa periods manually if not in the data
            from josi.services.dasa_calculator import DasaCalculator
            dasa_calc = DasaCalculator()
            moon_long = chart['planets']['Moon']['longitude']
            
            # Get dasa periods
            dasa_periods = dasa_calc.calculate_dasa_periods(moon_long, dt)
            
            # Add bhukti periods to each dasa
            for i, dasa_period in enumerate(dasa_periods[:3]):  # Process first 3 dasas
                bhukti_periods = dasa_calc.calculate_bhukti_periods(dasa_period)
                dasa_period['bhuktis'] = bhukti_periods
            
            # Create compressed table
            compressed_lines = compressed_formatter.create_compressed_from_periods(
                dasa_periods, 
                dt,
                num_dasas=3  # Show 3 dasas in compressed format
            )
            lines.extend(compressed_lines)
        except Exception as e:
            lines.append("DASA ENDS ON   BHUKTHI FROM - TO    BHUKTHI FROM - TO    BHUKTHI FROM - TO    ")
            lines.append("")
            lines.append("[COMPRESSED DASA TABLE GENERATION ERROR]")
            print(f"Error generating compressed dasa table: {e}")
            import traceback
            traceback.print_exc()
    else:
        lines.append(" [DASA CALCULATIONS UNDER DEVELOPMENT]")
        lines.append("")
        lines.append(" [CURRENT DASA-BHUKTI CALCULATION PENDING]")
    
    # Additional sections
    lines.append("")
    lines.append(" ================== ADDITIONAL CALCULATIONS ==================")
    lines.append("")
    
    # Divisional Charts - Traditional Numeric Format
    if chart.get('vargas'):
        lines.append(" DIVISIONAL CHARTS (VARGAS):")
        lines.append(" " + "-" * 60)
        lines.append("")
        
        # First show the traditional numeric table format
        vargas_formatter = VargasFormatter()
        
        # Convert vargas data to proper format for formatter
        formatted_vargas = {}
        for varga_name, varga_data in chart['vargas'].items():
            formatted_vargas[varga_name] = {}
            # Convert from sign->planets to planet->sign format
            for sign, planets in varga_data.items():
                for planet in planets:
                    formatted_vargas[varga_name][planet] = {'sign': sign}
        
        # Add traditional numeric vargas table
        vargas_table_lines = vargas_formatter.format_vargas_table(formatted_vargas, format_type='numeric')
        for line in vargas_table_lines:
            lines.append(" " + line)
        
        lines.append("")
        
        # Then show the existing detailed format for important vargas
        important_vargas = ['D2', 'D3', 'D9', 'D10', 'D12', 'D30']
        varga_names = {
            'D2': 'HORA (Wealth)',
            'D3': 'DREKKANA (Siblings)',
            'D9': 'NAVAMSA (Marriage)',
            'D10': 'DASAMSA (Career)',
            'D12': 'DWADASAMSA (Parents)',
            'D30': 'TRIMSAMSA (Misfortunes)'
        }
        
        for varga in important_vargas:
            if varga in chart['vargas']:
                lines.append(f" {varga} - {varga_names[varga]}:")
                varga_chart = chart['vargas'][varga]
                
                # Display planets in each sign
                signs_with_planets = []
                for sign, planets in varga_chart.items():
                    if planets:
                        planet_str = ', '.join([PLANET_SHORT.get(p, p[:4]) for p in planets])
                        signs_with_planets.append(f"{sign[:3]}: {planet_str}")
                
                # Format in columns
                for i in range(0, len(signs_with_planets), 4):
                    row = signs_with_planets[i:i+4]
                    lines.append(" " + "  ".join(f"{s:<15}" for s in row))
                lines.append("")
    else:
        lines.append(" DIVISIONAL CHARTS (VARGAS): [CALCULATION PENDING]")
    
    lines.append("")
    
    # Enhanced Strength Calculations
    try:
        enhanced_calc = EnhancedStrengthCalculator()
        
        # Calculate all strength measures
        residential_decimal = enhanced_calc.calculate_residential_strength_decimal(
            chart['planets']
        )
        
        ishta_kashta = enhanced_calc.calculate_ishta_kashta_bala(
            chart['planets'], chart
        )
        
        # Determine if Mercury is benefic
        mercury_benefic = is_mercury_benefic(chart)
        
        bhava_bala_detailed = enhanced_calc.calculate_detailed_bhava_bala(
            chart['houses'], chart['planets'], mercury_benefic
        )
        
        # Format and add to output
        strength_lines = enhanced_calc.format_strength_tables(
            residential_decimal, ishta_kashta, bhava_bala_detailed
        )
        
        lines.extend(strength_lines)
        lines.append("")
        
        # Also add existing Shadbala if available
        if chart.get('strengths') and chart['strengths'].get('shadbala'):
            lines.append(" SHADBALA (PLANETARY STRENGTHS):")
            lines.append(" " + "-" * 70)
            lines.append(" PLANET  STHANA  DIG   KALA  CHEST NAISRG DRIK  TOTAL RUPAS")
            
            for planet in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']:
                if planet in chart['strengths']['shadbala']:
                    s = chart['strengths']['shadbala'][planet]
                    lines.append(f" {PLANET_SHORT[planet]:<7} {s['sthana_bala']:>6.1f} {s['dig_bala']:>5.1f} "
                               f"{s['kala_bala']:>5.1f} {s['chesta_bala']:>5.1f} {s['naisargika_bala']:>6.1f} "
                               f"{s['drik_bala']:>5.1f} {s['total']:>6.1f} {s['rupas']:>5.2f}")
            lines.append("")
    except Exception as e:
        print(f"Error calculating enhanced strengths: {e}")
        # Fallback to existing strength display
        lines.append(" STRENGTH CALCULATIONS: [ERROR]")
        if chart.get('strengths') and chart['strengths'].get('residential_strength'):
            lines.append(" RESIDENTIAL STRENGTH:")
            lines.append(" " + "-" * 60)
            lines.append(" PLANET   SIGN         TYPE              STRENGTH")
            
            for planet in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']:
                if planet in chart['strengths']['residential_strength']:
                    rs = chart['strengths']['residential_strength'][planet]
                    lines.append(f" {PLANET_SHORT[planet]:<8} {rs['sign']:<12} {rs['strength_type']:<16} {rs['strength_value']:>6.1f}%")
    
    lines.append("")
    
    # Ashtakavarga calculations
    try:
        ashtakavarga_calc = AshtakavargaCalculator()
        
        # Need to include Ascendant in the positions
        positions_with_asc = chart['planets'].copy()
        positions_with_asc['Ascendant'] = chart['ascendant']
        
        # Calculate Rasi-based Ashtakavarga
        rasi_ashtakavarga = ashtakavarga_calc.calculate_ashtakavarga(positions_with_asc)
        
        # Calculate Bhava-based if houses available
        bhava_ashtakavarga = None
        if chart.get('houses'):
            bhava_ashtakavarga = ashtakavarga_calc.calculate_bhava_ashtakavarga(
                rasi_ashtakavarga, chart['houses']
            )
        
        # Add section header
        lines.append("")
        lines.append("ASHTAKAVARGA")
        
        # Format both tables side by side
        rasi_lines = ashtakavarga_calc.format_ashtakavarga_table(rasi_ashtakavarga, 'rasi')
        
        if bhava_ashtakavarga:
            bhava_lines = ashtakavarga_calc.format_ashtakavarga_table(bhava_ashtakavarga, 'bhava')
            
            # Combine side by side
            for i in range(len(rasi_lines)):
                if i < len(bhava_lines):
                    # Pad rasi line to fixed width
                    combined = f"{rasi_lines[i]:<55} {bhava_lines[i]}"
                else:
                    combined = rasi_lines[i]
                lines.append(combined)
        else:
            lines.extend(rasi_lines)
            
    except Exception as e:
        print(f"Error calculating Ashtakavarga: {e}")
        import traceback
        traceback.print_exc()
        lines.append("")
        lines.append(" ASHTAKAVARGA: [CALCULATION ERROR]")
    
    lines.append("")
    
    # Footer
    lines.append(f"                                        PRINTED ON : {datetime.now().strftime('%d-%m-%Y')}")
    
    return '\n'.join(lines)

def generate_html(content, person_name):
    """Generate HTML with traditional format content."""
    html_template = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Josi Traditional Chart Export - {person_name}</title>
    <style>
        body {{
            font-family: 'Courier New', Courier, monospace;
            background-color: #f5f5f5;
            margin: 0;
            padding: 20px;
        }}
        .chart-container {{
            background-color: white;
            padding: 30px;
            max-width: 1200px;
            margin: 0 auto;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            white-space: pre;
            line-height: 1.2;
            font-size: 14px;
        }}
        @media print {{
            body {{
                background-color: white;
                margin: 0;
                padding: 0;
            }}
            .chart-container {{
                box-shadow: none;
                padding: 10px;
            }}
        }}
        .placeholder {{
            color: #888;
            font-style: italic;
        }}
        h1 {{
            font-family: Arial, sans-serif;
            text-align: center;
            color: #333;
            margin-bottom: 20px;
        }}
        .note {{
            font-family: Arial, sans-serif;
            background-color: #fffbcc;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 5px;
            border: 1px solid #ffe066;
        }}
    </style>
</head>
<body>
    <h1>Josi Traditional Vedic Astrology Chart Export</h1>
    <div class="note">
        <strong>Note:</strong> This is a preview of the traditional chart format. 
        Sections marked with [PENDING] or [CALCULATION PENDING] will be implemented in future updates.
        Currently showing all available data from Josi API.
    </div>
    <div class="chart-container">{content}</div>
</body>
</html>"""
    
    return html_template

def main():
    """Generate traditional format exports for all persons."""
    print("Generating Josi Traditional Format Exports")
    print("=" * 80)
    
    # Create output directory
    output_dir = "reports/josi_traditional_exports"
    os.makedirs(output_dir, exist_ok=True)
    
    # Create index HTML
    index_html = """<!DOCTYPE html>
<html>
<head>
    <title>Josi Traditional Chart Exports</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 40px;
            background-color: #f5f5f5;
        }
        h1 {
            text-align: center;
            color: #333;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        ul {
            list-style-type: none;
            padding: 0;
        }
        li {
            margin: 15px 0;
            padding: 15px;
            background-color: #f9f9f9;
            border-radius: 5px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        a {
            text-decoration: none;
            color: #4CAF50;
            font-size: 18px;
        }
        a:hover {
            text-decoration: underline;
        }
        .info {
            color: #666;
            font-size: 14px;
        }
        .timestamp {
            text-align: center;
            color: #666;
            font-style: italic;
        }
        .note {
            background-color: #fffbcc;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 5px;
            border: 1px solid #ffe066;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Josi Traditional Vedic Astrology Chart Exports</h1>
        <div class="note">
            <strong>New!</strong> Traditional format exports now available from Josi API. 
            These replicate the professional astrology software format with all available calculations.
        </div>
        <p class="timestamp">Generated on: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
        <h2>Available Charts:</h2>
        <ul>
"""
    
    for person in ALL_PERSONS:
        try:
            print(f"\\nProcessing: {person['name']}")
            
            # Calculate chart
            chart, dt = calculate_chart(person)
            
            # Generate traditional format
            traditional_text = generate_traditional_format(person, chart, dt)
            
            # Generate HTML
            html_content = generate_html(traditional_text, person['name'])
            
            # Save HTML file
            filename = person['name'].replace(' ', '_').lower()
            output_file = f"{output_dir}/{filename}_traditional.html"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"  Generated: {output_file}")
            
            # Add to index
            index_html += f"""            <li>
                <a href="{filename}_traditional.html">{person['name']}</a>
                <span class="info">DOB: {person['date_of_birth']}, {person['place_of_birth']}</span>
            </li>
"""
            
        except Exception as e:
            print(f"  Error: {e}")
            import traceback
            traceback.print_exc()
    
    # Complete index HTML
    index_html += """        </ul>
    </div>
</body>
</html>"""
    
    # Save index
    with open(f"{output_dir}/index.html", 'w', encoding='utf-8') as f:
        f.write(index_html)
    
    print(f"\\n{'='*80}")
    print(f"All traditional format exports generated in: {output_dir}/")
    print(f"Index page: {output_dir}/index.html")

if __name__ == "__main__":
    main()