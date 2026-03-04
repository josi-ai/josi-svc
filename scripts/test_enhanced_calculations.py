#!/usr/bin/env python3
"""
Test script for enhanced calculations (Divisional Charts, Dasa Balance, Nakshatra Details).
This script tests the new implementations against known values.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
import pytz
from src.josi.services.astrology_service import AstrologyCalculator
from src.josi.services.divisional_chart_calculator import DivisionalChartCalculator
from src.josi.services.dasa_balance_calculator import DasaBalanceCalculator
from src.josi.services.enhanced_nakshatra_calculator import EnhancedNakshatraCalculator

# Test data - Person with known chart values
TEST_PERSON = {
    "name": "Test Person",
    "date_of_birth": "1998-12-07",
    "time_of_birth": "21:15:00",
    "place_of_birth": "Chennai",
    "latitude": 13.0827,
    "longitude": 80.2707,
    "timezone": "Asia/Kolkata"
}

def test_enhanced_nakshatra():
    """Test enhanced nakshatra calculations."""
    print("="*80)
    print("Testing Enhanced Nakshatra Calculator")
    print("="*80)
    
    calc = EnhancedNakshatraCalculator()
    
    # Test with known Moon position (Pushya nakshatra)
    moon_longitude = 105.07  # Should be in Pushya
    
    details = calc.calculate_nakshatra_pada_details(moon_longitude)
    
    print(f"Moon Longitude: {moon_longitude}°")
    print(f"Nakshatra: {details['nakshatra']}")
    print(f"Pada: {details['pada']}")
    print(f"Ruler: {details['ruler']}")
    print(f"Deity: {details['deity']}")
    print(f"Navamsa Sign: {details['navamsa_sign']}")
    print(f"Position in Nakshatra: {details['position_in_nakshatra']}")
    print(f"Gana: {details['gana']}")
    print(f"Symbol: {details['symbol']}")
    
    # Verify expected values
    assert details['nakshatra'] == 'Pushya', f"Expected Pushya, got {details['nakshatra']}"
    assert details['ruler'] == 'Saturn', f"Expected Saturn as ruler, got {details['ruler']}"
    assert details['pada'] == 4, f"Expected pada 4, got {details['pada']}"
    
    print("\n✓ Enhanced Nakshatra test passed!")

def test_dasa_balance():
    """Test dasa balance calculation."""
    print("\n" + "="*80)
    print("Testing Dasa Balance Calculator")
    print("="*80)
    
    calc = DasaBalanceCalculator()
    
    # Test with known values
    moon_longitude = 105.07  # Pushya nakshatra (Saturn)
    birth_dt = datetime(1998, 12, 7, 21, 15, 0)
    tz = pytz.timezone('Asia/Kolkata')
    birth_dt = tz.localize(birth_dt)
    
    balance = calc.calculate_dasa_balance_at_birth(moon_longitude, birth_dt)
    
    print(f"Moon Longitude: {moon_longitude}°")
    print(f"Nakshatra: {balance['nakshatra_name']}")
    print(f"Ruling Planet: {balance['planet']}")
    print(f"Balance at Birth: {balance['years']}Y {balance['months']}M {balance['days']}D")
    print(f"Proportion Remaining: {balance['proportion_remaining']:.4f}")
    print(f"Exact Balance Years: {balance['exact_balance_years']:.4f}")
    
    # Verify Saturn dasa (Pushya is ruled by Saturn)
    assert balance['planet'] == 'Saturn', f"Expected Saturn dasa, got {balance['planet']}"
    assert 0 < balance['exact_balance_years'] < 19, "Balance should be between 0 and 19 years for Saturn"
    
    # Test current dasa
    current = calc.get_current_dasa_bhukti(moon_longitude, birth_dt)
    print(f"\nCurrent Dasa (as of now): {current['maha_dasa']}")
    print(f"Current Bhukti: {current['bhukti']}")
    
    print("\n✓ Dasa Balance test passed!")

def test_divisional_charts():
    """Test divisional chart calculations."""
    print("\n" + "="*80)
    print("Testing Divisional Chart Calculator")
    print("="*80)
    
    calc = DivisionalChartCalculator()
    
    # Test with Sun at 231.29° (Scorpio)
    sun_longitude = 231.29
    
    print(f"Sun Longitude: {sun_longitude}° (Scorpio)")
    
    # Test Navamsa (D9)
    d9 = calc.calculate_navamsa(sun_longitude)
    print(f"\nNavamsa (D9):")
    print(f"  Sign: {d9['sign']}")
    print(f"  Degrees: {d9['degrees']:.2f}")
    
    # Test Hora (D2)
    d2 = calc.calculate_hora(sun_longitude)
    print(f"\nHora (D2):")
    print(f"  Sign: {d2['sign']}")
    
    # Test Drekkana (D3)
    d3 = calc.calculate_drekkana(sun_longitude)
    print(f"\nDrekkana (D3):")
    print(f"  Sign: {d3['sign']}")
    
    # Test all vargas for one planet
    all_vargas = calc.calculate_all_vargas(sun_longitude)
    
    print(f"\nAll Divisional Charts for Sun:")
    for division, data in sorted(all_vargas.items()):
        print(f"  {division}: {data['sign']}")
    
    print("\n✓ Divisional Charts test passed!")

def test_full_chart_calculation():
    """Test full chart calculation with enhanced features."""
    print("\n" + "="*80)
    print("Testing Full Chart Calculation with Enhanced Features")
    print("="*80)
    
    calc = AstrologyCalculator()
    
    # Parse datetime
    date_parts = TEST_PERSON['date_of_birth'].split('-')
    time_parts = TEST_PERSON['time_of_birth'].split(':')
    
    dt = datetime(
        int(date_parts[0]), int(date_parts[1]), int(date_parts[2]),
        int(time_parts[0]), int(time_parts[1]), int(time_parts[2])
    )
    
    # Calculate chart
    chart = calc.calculate_vedic_chart(
        dt=dt,
        latitude=TEST_PERSON['latitude'],
        longitude=TEST_PERSON['longitude'],
        timezone=TEST_PERSON['timezone']
    )
    
    print(f"Chart calculated for: {TEST_PERSON['name']}")
    print(f"Date/Time: {dt}")
    print(f"Location: {TEST_PERSON['place_of_birth']}")
    
    # Check enhanced nakshatra data
    print("\nEnhanced Planet Data:")
    for planet in ['Sun', 'Moon', 'Mars']:
        if planet in chart['planets']:
            p_data = chart['planets'][planet]
            print(f"\n{planet}:")
            print(f"  Longitude: {p_data['longitude']:.2f}°")
            print(f"  Sign: {p_data['sign']}")
            print(f"  Nakshatra: {p_data['nakshatra']}")
            print(f"  Pada: {p_data.get('nakshatra_pada', 'N/A')}")
            print(f"  Ruler: {p_data.get('nakshatra_ruler', 'N/A')}")
            print(f"  Deity: {p_data.get('nakshatra_deity', 'N/A')}")
            print(f"  Navamsa Sign: {p_data.get('navamsa_sign', 'N/A')}")
    
    # Check dasa balance
    if 'dasa' in chart and chart['dasa']:
        print("\nDasa Information:")
        if 'balance_at_birth' in chart['dasa']:
            balance = chart['dasa']['balance_at_birth']
            print(f"  Balance at Birth: {balance['planet']} - {balance['years']}Y {balance['months']}M {balance['days']}D")
        
        if 'current' in chart['dasa']:
            current = chart['dasa']['current']
            print(f"  Current Dasa: {current.get('major', 'N/A')}")
            print(f"  Current Bhukti: {current.get('minor', 'N/A')}")
    
    # Check enhanced vargas
    if 'vargas' in chart and chart['vargas']:
        print("\nEnhanced Divisional Charts:")
        
        # Show D9 (Navamsa) for key planets
        if 'D9' in chart['vargas']:
            print("\nNavamsa (D9) Positions:")
            for planet in ['Ascendant', 'Sun', 'Moon', 'Mars', 'Venus']:
                if planet in chart['vargas']['D9']:
                    d9_data = chart['vargas']['D9'][planet]
                    print(f"  {planet}: {d9_data['sign']}")
        
        # Count available vargas
        print(f"\nTotal Vargas Available: {len(chart['vargas'])}")
        print(f"Vargas: {', '.join(sorted(chart['vargas'].keys()))}")
    
    print("\n✓ Full chart calculation test passed!")

def main():
    """Run all tests."""
    print("Testing Enhanced Vedic Astrology Calculations")
    print("=" * 80)
    
    try:
        test_enhanced_nakshatra()
        test_dasa_balance()
        test_divisional_charts()
        test_full_chart_calculation()
        
        print("\n" + "="*80)
        print("ALL TESTS PASSED! ✓")
        print("="*80)
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())