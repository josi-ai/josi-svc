#!/usr/bin/env python3
"""
Debugging script for house calculation - Barack Obama birth data
Expected: Ascendant at 236.51° (26.51° Scorpio)
Current: Ascendant at 176.51° (26.51° Virgo)
Difference: Exactly 60 degrees
"""

import swisseph as swe
from datetime import datetime
import pytz
import math

# Barack Obama's birth data
BIRTH_DATA = {
    "name": "Barack Obama",
    "date": "1961-08-04",
    "time": "19:24:00",
    "lat": 21.3099,
    "lon": -157.8581,
    "timezone": "Pacific/Honolulu"
}

def degrees_to_dms(degrees):
    """Convert decimal degrees to degrees, minutes, seconds format"""
    d = int(degrees)
    m = int((degrees - d) * 60)
    s = ((degrees - d) * 60 - m) * 60
    return f"{d}°{m}'{s:.2f}\""

def get_zodiac_position(degrees):
    """Convert absolute degrees to zodiac sign and degree"""
    signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
             "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    
    # Normalize to 0-360
    degrees = degrees % 360
    sign_num = int(degrees / 30)
    sign_deg = degrees % 30
    
    return f"{sign_deg:.2f}° {signs[sign_num]}"

def calculate_houses_debug():
    """Debug house calculation with detailed output"""
    
    print("=" * 80)
    print("HOUSE CALCULATION DEBUG - BARACK OBAMA")
    print("=" * 80)
    print()
    
    # Parse birth data
    date_str = BIRTH_DATA["date"]
    time_str = BIRTH_DATA["time"]
    lat = BIRTH_DATA["lat"]
    lon = BIRTH_DATA["lon"]
    tz_name = BIRTH_DATA["timezone"]
    
    print(f"Birth Data:")
    print(f"  Date: {date_str}")
    print(f"  Time: {time_str}")
    print(f"  Location: {lat}°N, {lon}°E")
    print(f"  Timezone: {tz_name}")
    print()
    
    # Create datetime object
    dt_str = f"{date_str} {time_str}"
    tz = pytz.timezone(tz_name)
    birth_dt = tz.localize(datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S"))
    
    print(f"Local DateTime: {birth_dt}")
    print(f"UTC DateTime: {birth_dt.astimezone(pytz.UTC)}")
    print()
    
    # Calculate Julian Day
    utc_dt = birth_dt.astimezone(pytz.UTC)
    year = utc_dt.year
    month = utc_dt.month
    day = utc_dt.day
    hour = utc_dt.hour + utc_dt.minute/60.0 + utc_dt.second/3600.0
    
    jd = swe.julday(year, month, day, hour)
    print(f"Julian Day: {jd:.6f}")
    print()
    
    # Test different longitude formats
    print("Testing Different Longitude Formats:")
    print("-" * 40)
    
    # Original longitude (negative for West)
    lon1 = lon  # -157.8581
    print(f"\n1. Original Longitude: {lon1}° (negative for West)")
    cusps1, ascmc1 = swe.houses(jd, lat, lon1, b'P')
    print(f"   Ascendant: {ascmc1[0]:.2f}° = {get_zodiac_position(ascmc1[0])}")
    print(f"   MC: {ascmc1[1]:.2f}° = {get_zodiac_position(ascmc1[1])}")
    print(f"   ARMC: {ascmc1[2]:.2f}°")
    print(f"   Vertex: {ascmc1[3]:.2f}°")
    
    # Positive longitude (360 - abs(lon))
    lon2 = 360 + lon  # 202.1419
    print(f"\n2. Positive Longitude (360 + lon): {lon2}°")
    cusps2, ascmc2 = swe.houses(jd, lat, lon2, b'P')
    print(f"   Ascendant: {ascmc2[0]:.2f}° = {get_zodiac_position(ascmc2[0])}")
    print(f"   MC: {ascmc2[1]:.2f}° = {get_zodiac_position(ascmc2[1])}")
    print(f"   ARMC: {ascmc2[2]:.2f}°")
    print(f"   Vertex: {ascmc2[3]:.2f}°")
    
    # Absolute value of longitude
    lon3 = abs(lon)  # 157.8581
    print(f"\n3. Absolute Longitude: {lon3}°")
    cusps3, ascmc3 = swe.houses(jd, lat, lon3, b'P')
    print(f"   Ascendant: {ascmc3[0]:.2f}° = {get_zodiac_position(ascmc3[0])}")
    print(f"   MC: {ascmc3[1]:.2f}° = {get_zodiac_position(ascmc3[1])}")
    print(f"   ARMC: {ascmc3[2]:.2f}°")
    print(f"   Vertex: {ascmc3[3]:.2f}°")
    
    # Negative of absolute value
    lon4 = -abs(lon)  # -157.8581 (same as original)
    print(f"\n4. Negative Absolute: {lon4}°")
    cusps4, ascmc4 = swe.houses(jd, lat, lon4, b'P')
    print(f"   Ascendant: {ascmc4[0]:.2f}° = {get_zodiac_position(ascmc4[0])}")
    print(f"   MC: {ascmc4[1]:.2f}° = {get_zodiac_position(ascmc4[1])}")
    
    print("\n" + "=" * 80)
    print("DETAILED CALCULATION WITH ORIGINAL LONGITUDE")
    print("=" * 80)
    print()
    
    # Calculate Local Sidereal Time manually
    # GMST at 0h UT
    jd_0h = swe.julday(year, month, day, 0)
    _, ascmc_0h = swe.houses(jd_0h, 0, 0, b'P')
    gmst_0h = ascmc_0h[2]  # ARMC at Greenwich
    
    # Hours since 0h UT
    ut_hours = hour
    
    # GMST at birth time
    gmst = gmst_0h + ut_hours * 15.04107  # Earth rotation rate
    gmst = gmst % 360
    
    # Local Sidereal Time
    lst = gmst + lon
    lst = lst % 360
    
    print(f"Sidereal Time Calculation:")
    print(f"  GMST at 0h UT: {gmst_0h:.4f}°")
    print(f"  UT hours: {ut_hours:.4f}")
    print(f"  GMST at birth: {gmst:.4f}°")
    print(f"  Longitude: {lon}°")
    print(f"  LST: {lst:.4f}° = {degrees_to_dms(lst/15)} (in hours)")
    print()
    
    # Get all house cusps
    print("House Cusps (Placidus):")
    print("-" * 40)
    for i in range(12):
        house_num = i + 1
        cusp_deg = cusps1[i]
        print(f"  House {house_num:2d}: {cusp_deg:6.2f}° = {get_zodiac_position(cusp_deg)}")
    
    print("\n" + "=" * 80)
    print("ANALYSIS")
    print("=" * 80)
    print()
    
    expected_asc = 236.51  # 26.51° Scorpio
    current_asc = ascmc1[0]
    difference = expected_asc - current_asc
    
    print(f"Expected Ascendant: {expected_asc:.2f}° = {get_zodiac_position(expected_asc)}")
    print(f"Current Ascendant:  {current_asc:.2f}° = {get_zodiac_position(current_asc)}")
    print(f"Difference: {difference:.2f}°")
    print()
    
    # Check if difference is exactly 60 degrees
    if abs(abs(difference) - 60) < 0.1:
        print("FINDING: The difference is almost exactly 60 degrees!")
        print("This suggests a systematic offset, possibly related to:")
        print("  1. Sidereal vs Tropical zodiac (but ayanamsa is ~24°, not 60°)")
        print("  2. House system differences")
        print("  3. Time zone or DST handling")
        print("  4. Longitude sign convention")
    
    # Additional checks
    print("\nAdditional Checks:")
    print("-" * 40)
    
    # Check if adding 60° gives expected result
    adjusted_asc = (current_asc + 60) % 360
    print(f"Current + 60°: {adjusted_asc:.2f}° = {get_zodiac_position(adjusted_asc)}")
    
    # Check MC relationship
    mc_to_asc = (ascmc1[0] - ascmc1[1]) % 360
    print(f"MC to ASC angle: {mc_to_asc:.2f}°")
    
    # Test with different house systems
    print("\nTesting Other House Systems:")
    print("-" * 40)
    
    house_systems = {
        'P': 'Placidus',
        'K': 'Koch',
        'R': 'Regiomontanus',
        'C': 'Campanus',
        'E': 'Equal',
        'W': 'Whole Sign'
    }
    
    for code, name in house_systems.items():
        try:
            _, ascmc_test = swe.houses(jd, lat, lon, code.encode())
            asc_test = ascmc_test[0]
            print(f"  {name:15s}: {asc_test:6.2f}° = {get_zodiac_position(asc_test)}")
        except:
            print(f"  {name:15s}: Not available")
    
    # Test with tropical vs sidereal
    print("\nTropical vs Sidereal:")
    print("-" * 40)
    
    # Set sidereal mode (Lahiri ayanamsa)
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    ayanamsa = swe.get_ayanamsa(jd)
    print(f"Ayanamsa (Lahiri): {ayanamsa:.4f}°")
    
    # Sidereal ascendant
    sidereal_asc = (current_asc - ayanamsa) % 360
    print(f"Sidereal Ascendant: {sidereal_asc:.2f}° = {get_zodiac_position(sidereal_asc)}")
    
    # Reset to tropical
    swe.set_sid_mode(swe.SIDM_FAGAN_BRADLEY)
    
    print("\n" + "=" * 80)
    print("CONCLUSION")
    print("=" * 80)
    
    if abs(adjusted_asc - expected_asc) < 0.1:
        print("\nThe 60-degree offset is confirmed!")
        print("Current calculation gives Ascendant 60° less than expected.")
        print("\nPossible causes to investigate:")
        print("1. Check the source of the expected value (236.51°)")
        print("2. Verify time zone handling (Hawaii doesn't use DST)")
        print("3. Check if reference uses a different house system")
        print("4. Verify the birth time accuracy")

if __name__ == "__main__":
    # Set up Swiss Ephemeris
    swe.set_ephe_path('/usr/share/ephe')  # Adjust path as needed
    
    try:
        calculate_houses_debug()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()