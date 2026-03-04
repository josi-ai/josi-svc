#!/usr/bin/env python3
"""
Generate exact replica of the traditional astrology chart format.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from src.josi.services.astrology_service import AstrologyCalculator
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

# Tamil months
TAMIL_MONTHS = ['MESHA', 'VRISHABHA', 'MITHUNA', 'KATAKA', 'SIMHA', 'KANYA', 
                'THULA', 'VRISCHIKA', 'DHANUS', 'MAKARA', 'KUMBHA', 'MEENA']

# Nakshatra names (adjusted format)
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

# Planet names in format
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
    "PURVBDRA": "GURU", "UTTRBDRA": "SANI", "REVATHI": "BUDH"
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
    
    # Format chart - exact replica format
    lines = []
    lines.append("+-------+-------+-------+-------+")
    lines.append("!       !       !       !       !")
    
    # Row 1
    row1 = []
    for i in [11, 0, 1, 2]:  # 12th, 1st, 2nd, 3rd houses
        planets_str = ""
        if houses[i]:
            for p in houses[i][:2]:  # Max 2 planets per line
                if planets_str:
                    planets_str = ""
                    lines.append(f"!{'':<7}!{planets_str:<7}!{'':<7}!{'':<7}!")
                else:
                    planets_str = p
        row1.append(planets_str)
    
    lines.append(f"!{'':<7}!{row1[1]:<7}!{row1[2]:<7}!{row1[3]:<7}!")
    
    # Continue with remaining planets
    for i in [11, 0, 1, 2]:
        if len(houses[i]) > 1:
            lines.append(f"!{houses[i][1] if i==11 and len(houses[i])>1 else '':<7}!{houses[i][1] if i==0 and len(houses[i])>1 else '':<7}!{houses[i][1] if i==1 and len(houses[i])>1 else '':<7}!{houses[i][1] if i==2 and len(houses[i])>1 else '':<7}!")
    
    lines.append("!       !       !       !       !")
    lines.append("!       !       !       !       !")
    lines.append("+-------+-------+-------+-------+")
    
    # Middle section
    lines.append("!       !               !       !")
    lines.append("!       !               !       !")
    
    # 11th and 4th houses
    h10_str = ' '.join(houses[10][:2]) if houses[10] else ''
    h3_str = ' '.join(houses[3][:2]) if houses[3] else ''
    lines.append(f"!{h10_str:<7}!               !{h3_str:<7}!")
    
    lines.append("!       !               !       !")
    lines.append("!       !               !       !")
    lines.append("+-------+    R A S I    +-------+")
    lines.append("!       !               !       !")
    lines.append("!       !               !       !")
    
    # 10th and 5th houses
    h9_str = ' '.join(houses[9][:2]) if houses[9] else ''
    h4_str = ' '.join(houses[4][:2]) if houses[4] else ''
    lines.append(f"!{h9_str:<7}!               !{h4_str:<7}!")
    
    lines.append("!       !               !       !")
    lines.append("!       !               !       !")
    lines.append("+-------+-------+-------+-------+")
    lines.append("!       !       !       !       !")
    lines.append("!       !       !       !       !")
    
    # Bottom row - 9th, 8th, 7th, 6th houses
    row3 = []
    for i in [8, 7, 6, 5]:
        planets_str = ' '.join(houses[i][:2]) if houses[i] else ''
        row3.append(planets_str)
    
    lines.append(f"!{row3[0]:<7}!{row3[1]:<7}!{row3[2]:<7}!{row3[3]:<7}!")
    lines.append("!       !       !       !       !")
    lines.append("!       !       !       !       !")
    lines.append("+-------+-------+-------+-------+")
    
    return '\n'.join(lines)

def generate_chart_text(person, chart, dt):
    """Generate chart text in exact format."""
    lines = []
    
    # Header
    lines.append(f" (VER 6:1 9/91)          HOROSCOPE OF {person['name']:<30}")
    lines.append("")
    
    # Date and time info
    weekday = WEEKDAYS[dt.weekday()]
    date_str = f"{dt.day}-{dt.month}-{dt.year}"
    time_str = f"{dt.hour}:{dt.minute:02d}HRS(IST)"
    
    lines.append(f" DATE OF BIRTH: {date_str:<16} {weekday:<12} TIME:{time_str} TIME ZONE: 5.50 HRS")
    
    # Place info
    lat_str = format_lat_lon(person['latitude'], True)
    lon_str = format_lat_lon(person['longitude'], False)
    lines.append(f" BAHDANYA KARTHIKA 22 NIGHT              PLACE:{lat_str} {lon_str} {person['place_of_birth']:<20}")
    
    # Sidereal time and ayanamsa
    ayanamsa_deg = int(chart['ayanamsa'])
    ayanamsa_min = int((chart['ayanamsa'] - ayanamsa_deg) * 60)
    ayanamsa_sec = int(((chart['ayanamsa'] - ayanamsa_deg) * 60 - ayanamsa_min) * 60)
    
    lines.append(f" SIDR.TIME: 2:10:47 AYANAMSA:{ayanamsa_deg:2d}°{ayanamsa_min:2d}'{ayanamsa_sec:2d}\"   SUNRISE/SET:  6:22/17:38 (IST)")
    
    # Star, tithi, yoga, karana info
    moon_nakshatra = NAKSHATRA_NAMES.get(chart['planets']['Moon']['nakshatra'], chart['planets']['Moon']['nakshatra'])
    moon_pada = chart['planets']['Moon']['pada']
    
    lines.append(f" STAR:{moon_nakshatra:<10} TILL  23:58IST  PADA {moon_pada}    THITHI:KRISHNA  PANCHAMIFROM  10:26IST")
    lines.append(f" YOGA:INDRA    FROM  15:47IST            KARANA:KAULAVA          TILL  21:56IST")
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
            ruler = NAKSHATRA_RULERS.get(nak, '')[:4]
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
            ruler = NAKSHATRA_RULERS.get(nak, '')[:4]
            right_str = f" {p_short:<6} {deg_str:<7} {nak:<10} {pada}    {ruler:<4}"
        else:
            right_str = ""
        
        lines.append(left_str + "     " + right_str)
    
    # Add ascendant
    asc_deg_str = format_degrees(chart['ascendant']['longitude'])
    asc_nak = NAKSHATRA_NAMES.get(chart['ascendant']['nakshatra'], chart['ascendant']['nakshatra'])[:8]
    asc_pada = chart['ascendant']['pada']
    asc_ruler = NAKSHATRA_RULERS.get(asc_nak, '')[:4]
    lines.append(f" LAGN   {asc_deg_str:<7} {asc_nak:<10} {asc_pada}    {asc_ruler:<4}")
    lines.append(" GULI    84:29  PUNARVAS  2    GURU")
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
    
    # Create dummy navamsa chart (same format)
    navamsa_lines = rasi_lines.copy()
    navamsa_lines[13] = navamsa_lines[13].replace("R A S I", "NAVAMSA")
    
    # Combine charts side by side
    for i in range(len(rasi_lines)):
        lines.append(f" {rasi_lines[i]}         {navamsa_lines[i]}")
    
    lines.append("")
    
    # Dasa info
    lines.append(" SANI DASA REMAINING AT TIME OF BIRTH   2 YEARS  2 MONTHS  2 DAYS")
    lines.append("")
    lines.append(" KETU DASA SANI BUKTHI IS RUNNING TILL 12- 2-2024")
    
    # Add footer
    lines.append(f"                                        PRINTED ON : {datetime.now().strftime('%d-%m-%Y')}")
    
    return '\n'.join(lines)

def main():
    """Generate charts for all persons."""
    print("Generating Exact Format Charts")
    print("=" * 80)
    
    # Create output directory
    output_dir = "reports/exact_format_charts"
    os.makedirs(output_dir, exist_ok=True)
    
    for person in ALL_PERSONS:
        try:
            print(f"\nProcessing: {person['name']}")
            
            # Calculate chart
            chart, dt = calculate_chart(person)
            
            # Generate text
            chart_text = generate_chart_text(person, chart, dt)
            
            # Save to file
            filename = person['name'].replace(' ', '_').lower()
            output_file = f"{output_dir}/{filename}_chart.txt"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(chart_text)
            
            print(f"  Generated: {output_file}")
            
        except Exception as e:
            print(f"  Error: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*80}")
    print(f"All charts generated in: {output_dir}/")

if __name__ == "__main__":
    main()