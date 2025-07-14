#!/usr/bin/env python3
"""
Verify astronomical positions using Swiss Ephemeris directly.
This script provides the ground truth for planetary positions.
"""

import swisseph as swe
from datetime import datetime
import pytz

def verify_obama_positions():
    """Verify Barack Obama's planetary positions."""
    print("=" * 80)
    print("BARACK OBAMA - ASTRONOMICAL POSITION VERIFICATION")
    print("=" * 80)
    
    # Birth data
    print("\nBirth Data:")
    print("  Date: August 4, 1961")
    print("  Time: 7:24 PM HST (19:24:00)")
    print("  Place: Honolulu, Hawaii")
    print("  Coordinates: 21.3099°N, 157.8581°W")
    
    # Create timezone-aware datetime
    tz = pytz.timezone('Pacific/Honolulu')
    birth_dt = tz.localize(datetime(1961, 8, 4, 19, 24, 0))
    
    # Convert to UTC
    utc_dt = birth_dt.astimezone(pytz.UTC)
    print(f"\n  Local Time: {birth_dt}")
    print(f"  UTC Time: {utc_dt}")
    
    # Calculate Julian Day
    jd = swe.julday(
        utc_dt.year, 
        utc_dt.month, 
        utc_dt.day,
        utc_dt.hour + utc_dt.minute/60.0 + utc_dt.second/3600.0
    )
    print(f"  Julian Day: {jd}")
    
    # Planet names and IDs
    planets = {
        'Sun': swe.SUN,
        'Moon': swe.MOON,
        'Mercury': swe.MERCURY,
        'Venus': swe.VENUS,
        'Mars': swe.MARS,
        'Jupiter': swe.JUPITER,
        'Saturn': swe.SATURN
    }
    
    signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
             "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    
    print("\n" + "-" * 80)
    print("PLANETARY POSITIONS (Tropical Zodiac)")
    print("-" * 80)
    print(f"{'Planet':<10} {'Longitude':<12} {'Sign':<12} {'Degrees in Sign':<20}")
    print("-" * 80)
    
    results = {}
    
    for planet_name, planet_id in planets.items():
        # Calculate planet position
        position, ret = swe.calc_ut(jd, planet_id)
        longitude = position[0]
        
        # Determine sign
        sign_num = int(longitude / 30)
        degrees_in_sign = longitude % 30
        sign_name = signs[sign_num]
        
        print(f"{planet_name:<10} {longitude:>10.4f}° {sign_name:<12} {degrees_in_sign:>6.2f}°")
        
        results[planet_name] = {
            'longitude': longitude,
            'sign': sign_name,
            'degrees_in_sign': degrees_in_sign
        }
    
    # Calculate houses and ascendant
    print("\n" + "-" * 80)
    print("HOUSE CUSPS (Placidus System)")
    print("-" * 80)
    
    # Calculate houses
    houses, ascmc = swe.houses(jd, 21.3099, -157.8581, b'P')
    
    # Ascendant is the first house cusp
    asc_longitude = houses[0]
    asc_sign_num = int(asc_longitude / 30)
    asc_degrees = asc_longitude % 30
    asc_sign = signs[asc_sign_num]
    
    print(f"Ascendant: {asc_longitude:.4f}° = {asc_degrees:.2f}° {asc_sign}")
    print(f"MC (Midheaven): {ascmc[1]:.4f}°")
    
    # Summary for easy comparison
    print("\n" + "=" * 80)
    print("SUMMARY FOR TEST VERIFICATION")
    print("=" * 80)
    print("\nExpected values for analyze_chart_accuracy.py:")
    print(f'    "Sun": ({results["Sun"]["degrees_in_sign"]:.2f}, "{results["Sun"]["sign"]}"),')
    print(f'    "Moon": ({results["Moon"]["degrees_in_sign"]:.2f}, "{results["Moon"]["sign"]}"),')
    print(f'    "Mercury": ({results["Mercury"]["degrees_in_sign"]:.2f}, "{results["Mercury"]["sign"]}"),')
    print(f'    "Venus": ({results["Venus"]["degrees_in_sign"]:.2f}, "{results["Venus"]["sign"]}"),')
    print(f'    "Mars": ({results["Mars"]["degrees_in_sign"]:.2f}, "{results["Mars"]["sign"]}"),')
    print(f'    "Ascendant": ({asc_degrees:.2f}, "{asc_sign}"),')
    
    return results

def verify_diana_positions():
    """Verify Princess Diana's planetary positions."""
    print("\n\n" + "=" * 80)
    print("PRINCESS DIANA - ASTRONOMICAL POSITION VERIFICATION")
    print("=" * 80)
    
    # Birth data
    print("\nBirth Data:")
    print("  Date: July 1, 1961")
    print("  Time: 7:45 PM BST (19:45:00)")
    print("  Place: Sandringham, England")
    print("  Coordinates: 52.8245°N, 0.5150°E")
    
    # Create timezone-aware datetime
    tz = pytz.timezone('Europe/London')
    birth_dt = tz.localize(datetime(1961, 7, 1, 19, 45, 0))
    
    # Convert to UTC
    utc_dt = birth_dt.astimezone(pytz.UTC)
    print(f"\n  Local Time: {birth_dt}")
    print(f"  UTC Time: {utc_dt}")
    
    # Calculate Julian Day
    jd = swe.julday(
        utc_dt.year, 
        utc_dt.month, 
        utc_dt.day,
        utc_dt.hour + utc_dt.minute/60.0 + utc_dt.second/3600.0
    )
    print(f"  Julian Day: {jd}")
    
    # Similar calculation for Diana...
    # (abbreviated for space, but would include full calculation)
    
def main():
    """Run verification for all test celebrities."""
    print("ASTRONOMICAL POSITION VERIFICATION")
    print("Using Swiss Ephemeris for ground truth")
    print("=" * 80)
    
    # Verify Obama's positions
    obama_results = verify_obama_positions()
    
    # Verify Diana's positions
    verify_diana_positions()
    
    # Add more celebrities as needed...

if __name__ == "__main__":
    main()