#!/usr/bin/env python3
"""
Test script to verify our calculation method and compare with known values.
This will help identify if we're using geocentric vs topocentric calculations correctly.
"""
import sys
sys.path.insert(0, 'src')

import swisseph as swe
from datetime import datetime
import pytz
from josi.services.astrology_service import AstrologyCalculator

def test_calculation_flags():
    """Test different calculation flags to understand what we're using."""
    
    # Test case: 2000-01-01 12:00:00 UTC, New Delhi
    dt = datetime(2000, 1, 1, 12, 0, 0, tzinfo=pytz.UTC)
    lat = 28.6139  # New Delhi
    lon = 77.2090
    
    # Convert to Julian Day
    jd = swe.julday(dt.year, dt.month, dt.day, 
                    dt.hour + dt.minute/60.0 + dt.second/3600.0)
    
    # Set Lahiri ayanamsa
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    ayanamsa = swe.get_ayanamsa(jd)
    
    print(f"Test Date: {dt}")
    print(f"Location: New Delhi (lat: {lat}, lon: {lon})")
    print(f"Julian Day: {jd}")
    print(f"Lahiri Ayanamsa: {ayanamsa:.6f}°")
    print("\n" + "="*60 + "\n")
    
    # Test 1: Geocentric Tropical (Western)
    print("1. GEOCENTRIC TROPICAL (Western standard):")
    result_tropical = swe.calc(jd, swe.MOON)
    print(f"   Moon Longitude: {result_tropical[0][0]:.6f}°")
    print(f"   Moon Latitude: {result_tropical[0][1]:.6f}°")
    print(f"   Moon Speed: {result_tropical[0][3]:.6f}°/day")
    
    # Test 2: Geocentric Sidereal (Vedic standard)
    print("\n2. GEOCENTRIC SIDEREAL (Vedic standard):")
    result_sidereal = swe.calc(jd, swe.MOON, swe.FLG_SIDEREAL)
    print(f"   Moon Longitude: {result_sidereal[0][0]:.6f}°")
    print(f"   Moon Latitude: {result_sidereal[0][1]:.6f}°")
    print(f"   Moon Speed: {result_sidereal[0][3]:.6f}°/day")
    print(f"   Manual calculation: {result_tropical[0][0]:.6f}° - {ayanamsa:.6f}° = {(result_tropical[0][0] - ayanamsa) % 360:.6f}°")
    
    # Test 3: Topocentric Sidereal (NOT standard for Vedic)
    print("\n3. TOPOCENTRIC SIDEREAL (NOT traditional Vedic):")
    swe.set_topo(lon, lat, 0)  # Set observer location
    result_topo = swe.calc(jd, swe.MOON, swe.FLG_SIDEREAL | swe.FLG_TOPOCTR)
    print(f"   Moon Longitude: {result_topo[0][0]:.6f}°")
    print(f"   Moon Latitude: {result_topo[0][1]:.6f}°")
    print(f"   Moon Speed: {result_topo[0][3]:.6f}°/day")
    
    # Calculate differences
    print("\n" + "="*60)
    print("DIFFERENCES:")
    print(f"Geocentric vs Topocentric longitude difference: {abs(result_sidereal[0][0] - result_topo[0][0]):.6f}°")
    print(f"This is {abs(result_sidereal[0][0] - result_topo[0][0]) * 60:.2f} arc minutes")
    
    # Test our service
    print("\n" + "="*60)
    print("OUR ASTROLOGY SERVICE TEST:")
    service = AstrologyCalculator()
    chart = service.calculate_vedic_chart(dt, lat, lon)
    
    our_moon_long = chart['planets']['Moon']['longitude']
    print(f"Our Moon Longitude: {our_moon_long:.6f}°")
    print(f"Matches Geocentric Sidereal: {abs(our_moon_long - result_sidereal[0][0]) < 0.0001}")
    print(f"Matches Topocentric Sidereal: {abs(our_moon_long - result_topo[0][0]) < 0.0001}")
    
    # Additional test with a birth time that showed discrepancy
    print("\n" + "="*60)
    print("TEST WITH ACTUAL BIRTH DATA (Valarmathi_Kannappan):")
    
    # 11/02/1961, 15:30:00, Kovur, Tamil Nadu, India
    tz = pytz.timezone('Asia/Kolkata')
    dt2 = tz.localize(datetime(1961, 2, 11, 15, 30, 0))
    lat2 = 13.0113616
    lon2 = 80.1208582
    
    chart2 = service.calculate_vedic_chart(dt2, lat2, lon2)
    print(f"Date: {dt2}")
    print(f"Our Moon Longitude: {chart2['planets']['Moon']['longitude']:.6f}°")
    print(f"VedicAstroAPI Moon: 352.593° (from validation)")
    print(f"Difference: {abs(chart2['planets']['Moon']['longitude'] - 352.593):.6f}°")

if __name__ == "__main__":
    print("CALCULATION METHOD TEST")
    print("="*60)
    test_calculation_flags()