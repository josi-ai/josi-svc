#!/usr/bin/env python3
"""
Generate new format chart exports for all persons.
This creates text files in the new-chart-export-format-{person}.txt format.
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
        "longitude": 79.1029,
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

# Planet short forms
PLANET_SHORT = {
    'Sun': 'SURY', 'Moon': 'CHAN', 'Mars': 'KUJA',
    'Mercury': 'BUDH', 'Jupiter': 'GURU', 'Venus': 'SUKR',
    'Saturn': 'SANI', 'Rahu': 'RAHU', 'Ketu': 'KETU',
    'Ascendant': 'LAGN'
}

# Sign short forms (3 letters)
SIGN_SHORT = {
    'Aries': 'ARI', 'Taurus': 'TAU', 'Gemini': 'GEM',
    'Cancer': 'CAN', 'Leo': 'LEO', 'Virgo': 'VIR',
    'Libra': 'LIB', 'Scorpio': 'SCO', 'Sagittarius': 'SAG',
    'Capricorn': 'CAP', 'Aquarius': 'AQU', 'Pisces': 'PIS'
}

# Tamil months
TAMIL_MONTHS = {
    4: 'CHITHIRAI', 5: 'VAIKASI', 6: 'AANI', 7: 'AADI',
    8: 'AAVANI', 9: 'PURATTASI', 10: 'AIPPASI', 11: 'KAARTHIKAI',
    12: 'MARGAZHI', 1: 'THAI', 2: 'MAASI', 3: 'PANGUNI'
}

# Weekdays
WEEKDAYS = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY']

def format_longitude(deg):
    """Format longitude as DEG:MIN."""
    d = int(deg)
    m = int((deg - d) * 60)
    return f"{d:3d}:{m:02d}"

def format_lat_lon(lat, lon):
    """Format latitude and longitude for display."""
    lat_deg = int(abs(lat))
    lat_min = int((abs(lat) - lat_deg) * 60)
    lat_dir = 'N' if lat >= 0 else 'S'
    
    lon_deg = int(abs(lon))
    lon_min = int((abs(lon) - lon_deg) * 60)
    lon_dir = 'E' if lon >= 0 else 'W'
    
    return f"{lat_deg}°{lat_min:2d}'{lat_dir} {lon_deg}°{lon_min:2d}'{lon_dir}"

def format_time(time_str):
    """Format time as HH:MMHRS."""
    h, m, s = map(int, time_str.split(':'))
    return f"{h}:{m:02d}HRS"

def calculate_chart(person):
    """Calculate chart using AstrologyCalculator."""
    calc = AstrologyCalculator()
    
    # Parse datetime
    date_parts = person['date_of_birth'].split('-')
    time_parts = person['time_of_birth'].split(':')
    
    dt = datetime(
        int(date_parts[0]), int(date_parts[1]), int(date_parts[2]),
        int(time_parts[0]), int(time_parts[1]), int(time_parts[2])
    )
    
    # Calculate the chart
    chart = calc.calculate_vedic_chart(
        dt=dt,
        latitude=person['latitude'],
        longitude=person['longitude'],
        timezone=person['timezone']
    )
    
    return chart, dt

def get_tamil_date(dt, sun_longitude):
    """Get Tamil calendar date."""
    tamil_calc = TamilCalendar()
    tamil_date = tamil_calc.get_tamil_date(dt, sun_longitude)
    
    # Format as "TAMIL_MONTH TAMIL_DAY"
    month_name = tamil_date['month']
    return f"{month_name} {tamil_date['day']}"

def format_chart_positions(chart):
    """Format planet positions for Rasi and Navamsa charts."""
    rasi_positions = {}
    navamsa_positions = {}
    
    # Initialize all houses
    for i in range(1, 13):
        rasi_positions[i] = []
        navamsa_positions[i] = []
    
    # Process planets
    for planet_name, planet_data in chart['planets'].items():
        if planet_name == 'Pluto':
            continue
            
        # Rasi position
        house = planet_data.get('house', 1)
        rasi_positions[house].append(PLANET_SHORT.get(planet_name, planet_name[:3]))
        
        # Navamsa position - use navamsa_sign from enhanced nakshatra data
        nav_sign = planet_data.get('navamsa_sign', '')
        if nav_sign:
            nav_house = get_sign_number(nav_sign)
            if nav_house:
                navamsa_positions[nav_house].append(PLANET_SHORT.get(planet_name, planet_name[:3]))
        elif chart.get('vargas', {}).get('D9', {}).get(planet_name):
            # Fallback to vargas data
            nav_sign = chart['vargas']['D9'][planet_name].get('sign', '')
            nav_house = get_sign_number(nav_sign)
            if nav_house:
                navamsa_positions[nav_house].append(PLANET_SHORT.get(planet_name, planet_name[:3]))
    
    # Add Ascendant
    asc_house = 1  # Ascendant is always in 1st house
    rasi_positions[asc_house].append('LAG')
    
    # Add Ascendant to Navamsa if available
    if chart.get('vargas', {}).get('D9', {}).get('Ascendant'):
        asc_nav_sign = chart['vargas']['D9']['Ascendant'].get('sign', '')
        asc_nav_house = get_sign_number(asc_nav_sign)
        if asc_nav_house:
            navamsa_positions[asc_nav_house].append('LAG')
    
    # Add Gulika if available
    if 'Gulika' in chart.get('special_points', {}):
        gulika_data = chart['special_points']['Gulika']
        gulika_house = gulika_data.get('house', 1)
        rasi_positions[gulika_house].append('GUL')
    
    return rasi_positions, navamsa_positions

def get_sign_number(sign_name):
    """Get sign number from name."""
    signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
             'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
    try:
        return signs.index(sign_name) + 1
    except ValueError:
        return None

def format_chart_box(positions, box_number):
    """Format a single box of the chart."""
    planets = positions.get(box_number, [])
    lines = [''] * 5
    
    if planets:
        # Distribute planets across lines
        for i, planet in enumerate(planets):
            line_num = min(i // 2, 4)  # Max 2 planets per line
            if lines[line_num]:
                lines[line_num] += ' '
            lines[line_num] += planet[:3]
    
    return lines

def draw_chart(positions):
    """Draw the chart in traditional format."""
    lines = []
    
    # Top row
    lines.append("+-------+-------+-------+-------+")
    for i in range(5):
        line = "!"
        for box in [12, 1, 2, 3]:
            box_lines = format_chart_box(positions, box)
            line += f" {box_lines[i]:<6}!"
        lines.append(line)
    
    # Middle section
    lines.append("+-------+-------+-------+-------+")
    for i in range(5):
        line = "!"
        # Box 11
        box_lines_11 = format_chart_box(positions, 11)
        line += f" {box_lines_11[i]:<6}!"
        
        # Center space
        if i == 2:
            line += "               !"
        else:
            line += "               !"
        
        # Box 4
        box_lines_4 = format_chart_box(positions, 4)
        line += f" {box_lines_4[i]:<6}!"
        lines.append(line)
    
    # Chart label in center
    lines[9] = lines[9][:17] + "    R A S I    " + lines[9][32:]
    
    # Continue middle section
    for i in range(5):
        line = "!"
        # Box 10
        box_lines_10 = format_chart_box(positions, 10)
        line += f" {box_lines_10[i]:<6}!"
        
        # Center space
        line += "               !"
        
        # Box 5
        box_lines_5 = format_chart_box(positions, 5)
        line += f" {box_lines_5[i]:<6}!"
        lines.append(line)
    
    # Bottom row
    lines.append("+-------+-------+-------+-------+")
    for i in range(5):
        line = "!"
        for box in [9, 8, 7, 6]:
            box_lines = format_chart_box(positions, box)
            line += f" {box_lines[i]:<6}!"
        lines.append(line)
    lines.append("+-------+-------+-------+-------+")
    
    return lines

def generate_new_format_export(person, chart, dt):
    """Generate chart export in new format."""
    lines = []
    
    # Header
    lines.append(f"  (VER 6:1 9/91)          HOROSCOPE OF {person['name']:<30}")
    lines.append("")
    
    # Date and time info
    weekday = WEEKDAYS[dt.weekday()]
    date_str = f"{dt.day:2d}-{dt.month:2d}-{dt.year}"
    time_str = format_time(person['time_of_birth'])
    
    lines.append(f" DATE OF BIRTH:{date_str} {weekday:<12} TIME:{time_str}(IST) TIME ZONE: 5.50 HRS")
    
    # Tamil date and place
    sun_longitude = chart['planets']['Sun']['longitude']
    tamil_date = get_tamil_date(dt, sun_longitude)
    day_night = "NIGHT" if int(person['time_of_birth'].split(':')[0]) >= 18 else "DAY"
    place_str = format_lat_lon(person['latitude'], person['longitude'])
    
    lines.append(f" {tamil_date} {day_night:<20} PLACE:{place_str} {person['place_of_birth']:<20}")
    
    # Sidereal time and ayanamsa
    sidr_time = chart.get('sidereal_time', '00:00:00')
    ayanamsa = chart.get('ayanamsa', 23.0)
    ayanamsa_deg = int(ayanamsa)
    ayanamsa_min = int((ayanamsa - ayanamsa_deg) * 60)
    ayanamsa_sec = int(((ayanamsa - ayanamsa_deg) * 60 - ayanamsa_min) * 60)
    
    # Get sunrise/sunset
    sunrise = "6:00"  # Default values
    sunset = "18:00"
    if 'sunrise' in chart:
        sunrise = chart['sunrise'].strftime('%H:%M')
    if 'sunset' in chart:
        sunset = chart['sunset'].strftime('%H:%M')
    
    lines.append(f" SIDR.TIME: {sidr_time} AYANAMSA:{ayanamsa_deg}°{ayanamsa_min}'{ayanamsa_sec}\"   SUNRISE/SET: {sunrise}/{sunset} (IST)")
    
    # Current nakshatra, tithi, yoga, karana
    moon_data = chart['planets']['Moon']
    nakshatra = moon_data.get('nakshatra', '')
    pada = moon_data.get('nakshatra_pada', moon_data.get('pada', ''))
    
    # Get panchang details
    panchang = chart.get('panchang', {})
    tithi = panchang.get('tithi', {}).get('name', '')
    yoga = panchang.get('yoga', {}).get('name', '')
    karana = panchang.get('karana', {}).get('name', '')
    
    lines.append(f" STAR:{nakshatra:<8} PADA {pada}    THITHI:{tithi:<20} ")
    lines.append(f" YOGA:{yoga:<20}       KARANA:{karana:<20}")
    lines.append("")
    
    # Nirayana longitudes
    lines.append(" NIRAYANA LONGITUDES:")
    lines.append(" -------------------")
    lines.append(" PLANET DEG:MIN  STAR   PADA  RULER      PLANET DEG:MIN  STAR   PADA  RULER     ")
    lines.append("")
    
    # Planet positions in two columns
    planet_order = ['Sun', 'Mars', 'Jupiter', 'Saturn', 'Ketu']
    planet_order2 = ['Moon', 'Mercury', 'Venus', 'Rahu', 'Ascendant']
    
    for i in range(5):
        line = " "
        
        # First column
        if i < len(planet_order):
            planet = planet_order[i]
            if planet in chart['planets']:
                p_data = chart['planets'][planet]
                long_str = format_longitude(p_data['longitude'])
                nak = p_data.get('nakshatra', '')[:8] if p_data.get('nakshatra') else ''
                pada = str(p_data.get('nakshatra_pada', p_data.get('pada', ''))) if p_data.get('nakshatra_pada') or p_data.get('pada') else ''
                ruler = p_data.get('nakshatra_ruler', '')[:4] if p_data.get('nakshatra_ruler') else ''
                line += f"{PLANET_SHORT[planet]:<5} {long_str}  {nak:<8} {pada:>2}    {ruler:<4}      "
        else:
            line += " " * 40
        
        # Second column
        if i < len(planet_order2):
            planet = planet_order2[i]
            if planet in chart['planets'] or planet == 'Ascendant':
                if planet == 'Ascendant':
                    # Use ascendant data
                    asc_long = chart.get('ascendant', {}).get('longitude', 0)
                    long_str = format_longitude(asc_long)
                    # Calculate nakshatra for ascendant
                    nak, pada, ruler = NakshatraUtils.calculate_nakshatra_pada(asc_long)
                    nak = nak[:8]
                    ruler = ruler[:4]
                    line += f"LAGN  {long_str}  {nak:<8} {pada:>2}    {ruler:<4}"
                else:
                    p_data = chart['planets'][planet]
                    long_str = format_longitude(p_data['longitude'])
                    nak = p_data.get('nakshatra', '')[:8] if p_data.get('nakshatra') else ''
                    pada = str(p_data.get('nakshatra_pada', p_data.get('pada', ''))) if p_data.get('nakshatra_pada') or p_data.get('pada') else ''
                    ruler = p_data.get('nakshatra_ruler', '')[:4] if p_data.get('nakshatra_ruler') else ''
                    line += f"{PLANET_SHORT[planet]:<5} {long_str}  {nak:<8} {pada:>2}    {ruler:<4}"
        
        lines.append(line)
    
    # Add Gulika if present
    if 'Gulika' in chart.get('special_points', {}):
        gulika = chart['special_points']['Gulika']
        long_str = format_longitude(gulika['longitude'])
        nak, pada, ruler = NakshatraUtils.calculate_nakshatra_pada(gulika['longitude'])
        nak = nak[:8]
        ruler = ruler[:4]
        lines.append(f" GULI  {long_str}  {nak:<8} {pada:>2}    {ruler:<4}")
    
    lines.append("")
    
    # Check for retrograde planets
    retro_planets = []
    for planet, data in chart['planets'].items():
        if data.get('is_retrograde', False):
            retro_planets.append(PLANET_SHORT.get(planet, planet[:4]))
    
    if retro_planets:
        lines.append(f" PLANETS UNDER RETROGRESSION : {';'.join(retro_planets)};")
    
    # Draw Rasi and Navamsa charts
    rasi_positions, navamsa_positions = format_chart_positions(chart)
    
    # Draw charts side by side
    rasi_lines = draw_chart(rasi_positions)
    navamsa_lines = draw_chart(navamsa_positions)
    
    # Replace RASI with NAVAMSA in navamsa chart
    for i, line in enumerate(navamsa_lines):
        if 'R A S I' in line:
            navamsa_lines[i] = line.replace('R A S I', 'NAVAMSA')
    
    # Combine side by side
    for i in range(len(rasi_lines)):
        combined = f" {rasi_lines[i]}         {navamsa_lines[i]}"
        lines.append(combined)
    
    lines.append("")
    
    # Dasa balance at birth
    if 'dasa' in chart and chart['dasa']:
        dasa_balance = chart['dasa'].get('balance_at_birth', {})
        current_info = chart['dasa'].get('current', {})
        
        if dasa_balance:
            planet = dasa_balance.get('planet', '')
            years = dasa_balance.get('years', 0)
            months = dasa_balance.get('months', 0)
            days = dasa_balance.get('days', 0)
            
            lines.append(f" {planet.upper()} DASA REMAINING AT TIME OF BIRTH   {years} YEARS  {months} MONTHS  {days} DAYS")
            lines.append("")
        else:
            lines.append(" DASA BALANCE: [DATA NOT AVAILABLE]")
            lines.append("")
        
        # Current dasa/bhukti
        if current_info:
            maha_dasa = current_info.get('major', '')
            bhukti = current_info.get('minor', '')
            end_date = current_info.get('end_date', '')
            
            if end_date:
                try:
                    end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                    end_str = end_dt.strftime('%d-%m-%Y')
                    lines.append(f" {maha_dasa.upper()} DASA {bhukti.upper()} BUKTHI IS RUNNING TILL {end_str}")
                except:
                    pass
            
            # Add dasa results if available
            try:
                dasa_calc = DasaResultsCalculator()
                results = dasa_calc.calculate_dasa_results(maha_dasa.lower(), chart)
                if results and results['result_houses']:
                    house_str = ','.join(str(h) for h in results['result_houses'])
                    lines.append(f" {maha_dasa.lower()} dasa------{house_str}")
            except:
                pass
    
    lines.append("")
    
    return '\n'.join(lines)

def main():
    """Generate new format exports for all persons."""
    print("Generating New Format Chart Exports")
    print("=" * 80)
    
    for person in ALL_PERSONS:
        try:
            print(f"\nProcessing: {person['name']}")
            
            # Calculate chart
            chart, dt = calculate_chart(person)
            
            # Generate new format export
            export_text = generate_new_format_export(person, chart, dt)
            
            # Save to file
            filename = person['name'].split()[0].lower()
            output_file = f"new-chart-export-format-{filename}.txt"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(export_text)
            
            print(f"  Generated: {output_file}")
            
        except Exception as e:
            print(f"  Error: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*80}")
    print("All new format exports generated!")

if __name__ == "__main__":
    main()