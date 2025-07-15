#!/usr/bin/env python3
"""
Final accuracy test using the fixed calculations directly.
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime
import pytz
from src.josi.services.astrology_service import AstrologyCalculator
from scripts.analyze_chart_accuracy import VERIFIED_POSITIONS, ZODIAC_SIGNS

def test_accuracy():
    """Test accuracy of all celebrity calculations."""
    calc = AstrologyCalculator()
    
    # Celebrity birth data
    celebrities = {
        "Barack Obama": {
            "datetime": datetime(1961, 8, 4, 19, 24, 0),
            "timezone": "Pacific/Honolulu",
            "latitude": 21.3099,
            "longitude": -157.8581
        },
        "Princess Diana": {
            "datetime": datetime(1961, 7, 1, 19, 45, 0),
            "timezone": "Europe/London",
            "latitude": 52.8245,
            "longitude": 0.5150
        },
        "Albert Einstein": {
            "datetime": datetime(1879, 3, 14, 11, 30, 0),
            "timezone": "Europe/Berlin",
            "latitude": 48.4011,
            "longitude": 9.9876
        },
        "Steve Jobs": {
            "datetime": datetime(1955, 2, 24, 19, 15, 0),
            "timezone": "America/Los_Angeles",
            "latitude": 37.7749,
            "longitude": -122.4194
        },
        "Queen Elizabeth II": {
            "datetime": datetime(1926, 4, 21, 2, 40, 0),
            "timezone": "Europe/London",
            "latitude": 51.5074,
            "longitude": -0.1278
        },
        "John F. Kennedy": {
            "datetime": datetime(1917, 5, 29, 15, 0, 0),
            "timezone": "America/New_York",
            "latitude": 42.3467,
            "longitude": -71.0972
        },
        "Nelson Mandela": {
            "datetime": datetime(1918, 7, 18, 14, 54, 0),
            "timezone": "Africa/Johannesburg",
            "latitude": -31.8955,
            "longitude": 28.7820
        },
        "Oprah Winfrey": {
            "datetime": datetime(1954, 1, 29, 4, 30, 0),
            "timezone": "America/Chicago",
            "latitude": 33.4504,
            "longitude": -88.8184
        }
    }
    
    total_errors = 0
    total_comparisons = 0
    
    print("🌟 FINAL ACCURACY TEST WITH FIXED CALCULATIONS 🌟")
    print("=" * 80)
    
    for name, data in celebrities.items():
        if name not in VERIFIED_POSITIONS:
            continue
            
        # Localize datetime
        tz = pytz.timezone(data["timezone"])
        dt = tz.localize(data["datetime"])
        
        # Calculate chart
        chart = calc.calculate_western_chart(dt, data["latitude"], data["longitude"])
        
        print(f"\n📊 {name}")
        print(f"   Birth: {dt.strftime('%Y-%m-%d %H:%M %Z')}")
        
        errors = []
        celebrity_total_orb = 0
        celebrity_comparisons = 0
        
        # Compare each planet
        verified = VERIFIED_POSITIONS[name]
        
        # Process planets
        for body in ["Sun", "Moon", "Mercury", "Venus", "Mars"]:
            if body in verified and body in chart["planets"]:
                calc_long = chart["planets"][body]["longitude"]
                calc_sign = chart["planets"][body]["sign"]
                calc_deg = calc_long % 30
                
                exp_deg, exp_sign = verified[body]
                exp_sign_idx = ZODIAC_SIGNS.index(exp_sign)
                exp_long = exp_sign_idx * 30 + exp_deg
                
                # Calculate orb
                orb = abs(calc_long - exp_long)
                if orb > 180:
                    orb = 360 - orb
                
                celebrity_total_orb += orb
                celebrity_comparisons += 1
                total_comparisons += 1
                
                status = "✓" if orb < 1.0 else "✗"
                
                if orb > 1.0:
                    errors.append(f"{body}: {orb:.2f}° off")
                    total_errors += 1
                    
                print(f"   {body:8} {status} {calc_deg:5.2f}° {calc_sign:12} (expected {exp_deg:.2f}° {exp_sign})")
        
        # Process Ascendant
        if "Ascendant" in verified:
            calc_long = chart["ascendant"]["longitude"]
            calc_sign = chart["ascendant"]["sign"]
            calc_deg = calc_long % 30
            
            exp_deg, exp_sign = verified["Ascendant"]
            exp_sign_idx = ZODIAC_SIGNS.index(exp_sign)
            exp_long = exp_sign_idx * 30 + exp_deg
            
            # Calculate orb
            orb = abs(calc_long - exp_long)
            if orb > 180:
                orb = 360 - orb
            
            celebrity_total_orb += orb
            celebrity_comparisons += 1
            total_comparisons += 1
            
            status = "✓" if orb < 1.0 else "✗"
            
            if orb > 1.0:
                errors.append(f"Ascendant: {orb:.2f}° off")
                total_errors += 1
                
            print(f"   {'ASC':8} {status} {calc_deg:5.2f}° {calc_sign:12} (expected {exp_deg:.2f}° {exp_sign})")
        
        # Calculate accuracy
        if celebrity_comparisons > 0:
            avg_orb = celebrity_total_orb / celebrity_comparisons
            accuracy = max(0, (10 - avg_orb) * 10)
            print(f"\n   Accuracy: {accuracy:.1f}% (avg orb: {avg_orb:.2f}°)")
            
            if errors:
                print("   ⚠️  Errors:")
                for error in errors:
                    print(f"      - {error}")
    
    print("\n" + "=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)
    
    if total_comparisons > 0:
        error_rate = (total_errors / total_comparisons) * 100
        accuracy_rate = 100 - error_rate
        
        print(f"Total Comparisons: {total_comparisons}")
        print(f"Total Errors (>1° orb): {total_errors}")
        print(f"Overall Accuracy: {accuracy_rate:.1f}%")
        
        if accuracy_rate >= 95:
            print("\n✅ EXCELLENT! Astrological calculations are highly accurate!")
        elif accuracy_rate >= 80:
            print("\n⚠️  GOOD! Most calculations are accurate, minor issues remain.")
        else:
            print("\n❌ NEEDS WORK! Significant accuracy issues detected.")

if __name__ == "__main__":
    test_accuracy()