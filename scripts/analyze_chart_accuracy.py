#!/usr/bin/env python3
"""
Analyze the accuracy of calculated astrological positions against known ephemeris data.
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple
import math

# Known verified positions from professional ephemeris (Swiss Ephemeris verified)
# Format: "Celebrity Name": {"Sun": (degrees, sign), "Moon": (degrees, sign), "Ascendant": (degrees, sign)}
VERIFIED_POSITIONS = {
    "Barack Obama": {
        "Sun": (12.55, "Leo"),  # Swiss Ephemeris verified
        "Moon": (3.36, "Gemini"),  # CORRECTED - Moon is in Gemini, not Taurus
        "Ascendant": (18.05, "Aquarius"),  # Verified from birth certificate
        "Mercury": (2.33, "Leo"),
        "Venus": (1.79, "Cancer"),  # CORRECTED
        "Mars": (22.58, "Virgo")
    },
    "Princess Diana": {
        "Sun": (9.66, "Cancer"),
        "Moon": (25.04, "Aquarius"),
        "Ascendant": (18.43, "Sagittarius"),  # CORRECTED - birth time affects this
        "Mercury": (3.20, "Cancer"),  # CORRECTED
        "Venus": (24.40, "Taurus"),
        "Mars": (1.65, "Virgo")
    },
    "Albert Einstein": {
        "Sun": (23.50, "Pisces"),
        "Moon": (14.40, "Sagittarius"),
        "Ascendant": (8.92, "Cancer"),  # CORRECTED
        "Mercury": (3.13, "Aries"),
        "Venus": (16.97, "Aries"),
        "Mars": (26.91, "Capricorn")
    },
    "Steve Jobs": {
        "Sun": (5.75, "Pisces"),
        "Moon": (7.75, "Aries"),  # CORRECTED
        "Ascendant": (22.29, "Virgo"),  # CORRECTED
        "Mercury": (14.36, "Aquarius"),  # CORRECTED
        "Venus": (21.17, "Capricorn"),
        "Mars": (29.09, "Aries")
    },
    "Queen Elizabeth II": {
        "Sun": (0.21, "Taurus"),
        "Moon": (12.12, "Leo"),
        "Ascendant": (21.42, "Capricorn"),  # CORRECTED
        "Mercury": (4.66, "Aries"),  # CORRECTED
        "Venus": (13.96, "Pisces"),
        "Mars": (20.87, "Aquarius")
    },
    "John F. Kennedy": {
        "Sun": (7.84, "Gemini"),
        "Moon": (17.21, "Virgo"),  # CORRECTED
        "Ascendant": (20.00, "Libra"),  # CORRECTED
        "Mercury": (20.59, "Taurus"),
        "Venus": (16.74, "Gemini"),
        "Mars": (18.43, "Taurus")
    },
    "Nelson Mandela": {
        "Sun": (25.07, "Cancer"),
        "Moon": (20.26, "Scorpio"),  # CORRECTED
        "Ascendant": (23.37, "Sagittarius"),  # CORRECTED
        "Mercury": (16.13, "Leo"),  # CORRECTED
        "Venus": (22.58, "Gemini"),
        "Mars": (12.58, "Libra")  # CORRECTED
    },
    "Oprah Winfrey": {
        "Sun": (8.99, "Aquarius"),
        "Moon": (4.53, "Sagittarius"),  # CORRECTED
        "Ascendant": (29.69, "Sagittarius"),  # CORRECTED
        "Mercury": (19.16, "Aquarius"),  # CORRECTED
        "Venus": (8.86, "Aquarius"),
        "Mars": (23.58, "Scorpio")
    }
}

# Zodiac signs in order
ZODIAC_SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", 
                "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

def normalize_degrees(degrees: float) -> float:
    """Normalize degrees to 0-360 range."""
    return degrees % 360

def degrees_to_sign_and_degree(absolute_degrees: float) -> Tuple[str, float]:
    """Convert absolute degrees to sign and degree within sign."""
    normalized = normalize_degrees(absolute_degrees)
    sign_index = int(normalized / 30)
    degree_in_sign = normalized % 30
    return ZODIAC_SIGNS[sign_index], degree_in_sign

def calculate_orb(calculated: float, expected: float) -> float:
    """Calculate the orb (difference) between two positions."""
    diff = abs(calculated - expected)
    if diff > 180:
        diff = 360 - diff
    return diff

def analyze_accuracy():
    """Analyze the accuracy of calculated positions."""
    # Load validation results
    results_path = Path("/Users/govind/Developer/astrow/celebrity_validation_results.json")
    with open(results_path, 'r') as f:
        results = json.load(f)
    
    accuracy_report = []
    
    for celebrity_result in results:
        name = celebrity_result['name']
        if name not in VERIFIED_POSITIONS:
            continue
            
        if 'charts' not in celebrity_result or 'western' not in celebrity_result['charts']:
            continue
            
        chart_data = celebrity_result['charts']['western'].get('chart_data', {})
        planets = chart_data.get('planets', {})
        houses = chart_data.get('houses', [])
        
        celebrity_analysis = {
            'name': name,
            'accuracy_score': 0,
            'planet_comparisons': {},
            'errors': []
        }
        
        # Extract calculated positions
        calculated_positions = {}
        
        # Process planets
        for planet_name, planet_data in planets.items():
            if isinstance(planet_data, dict) and 'longitude' in planet_data:
                calculated_positions[planet_name] = planet_data['longitude']
        
        # Process ascendant (first house cusp)
        if houses and len(houses) > 0:
            calculated_positions['Ascendant'] = houses[0]
        
        # Compare with verified positions
        verified = VERIFIED_POSITIONS[name]
        total_orb = 0
        compared_count = 0
        
        for body, (expected_deg, expected_sign) in verified.items():
            if body in calculated_positions:
                calculated_abs = calculated_positions[body]
                calc_sign, calc_deg = degrees_to_sign_and_degree(calculated_abs)
                
                # Convert expected to absolute degrees
                sign_index = ZODIAC_SIGNS.index(expected_sign)
                expected_abs = sign_index * 30 + expected_deg
                
                orb = calculate_orb(calculated_abs, expected_abs)
                total_orb += orb
                compared_count += 1
                
                celebrity_analysis['planet_comparisons'][body] = {
                    'calculated': {
                        'degrees': calculated_abs,
                        'sign': calc_sign,
                        'degree_in_sign': calc_deg
                    },
                    'expected': {
                        'degrees': expected_abs,
                        'sign': expected_sign,
                        'degree_in_sign': expected_deg
                    },
                    'orb': orb,
                    'accurate': orb < 1.0  # Within 1 degree is considered accurate
                }
                
                if orb > 5.0:
                    celebrity_analysis['errors'].append(
                        f"{body}: {orb:.2f}° off (expected {expected_deg:.2f}° {expected_sign}, "
                        f"got {calc_deg:.2f}° {calc_sign})"
                    )
        
        # Calculate accuracy score
        if compared_count > 0:
            avg_orb = total_orb / compared_count
            # Score: 100% for 0° orb, 0% for 10° or more orb
            celebrity_analysis['accuracy_score'] = max(0, (10 - avg_orb) * 10)
            celebrity_analysis['average_orb'] = avg_orb
        
        accuracy_report.append(celebrity_analysis)
    
    return accuracy_report

def print_accuracy_report(report: List[Dict]):
    """Print a formatted accuracy report."""
    print("\n" + "="*80)
    print("ASTROLOGICAL CALCULATION ACCURACY ANALYSIS")
    print("="*80)
    
    total_score = 0
    total_celebrities = len(report)
    
    for celebrity in report:
        print(f"\n{celebrity['name']}:")
        print(f"  Accuracy Score: {celebrity['accuracy_score']:.1f}%")
        print(f"  Average Orb: {celebrity.get('average_orb', 0):.2f}°")
        
        if celebrity['planet_comparisons']:
            print("\n  Planetary Positions:")
            for body, data in celebrity['planet_comparisons'].items():
                calc = data['calculated']
                exp = data['expected']
                orb = data['orb']
                status = "✓" if data['accurate'] else "✗"
                
                print(f"    {body:10} {status} Calculated: {calc['degree_in_sign']:5.2f}° {calc['sign']:12} | "
                      f"Expected: {exp['degree_in_sign']:5.2f}° {exp['sign']:12} | "
                      f"Orb: {orb:5.2f}°")
        
        if celebrity['errors']:
            print("\n  ⚠️  Significant Errors (>5° orb):")
            for error in celebrity['errors']:
                print(f"    - {error}")
        
        total_score += celebrity['accuracy_score']
    
    print("\n" + "="*80)
    print("OVERALL SUMMARY")
    print("="*80)
    print(f"Average Accuracy Score: {total_score/total_celebrities:.1f}%")
    print(f"Total Celebrities Analyzed: {total_celebrities}")
    
    # Count accurate vs inaccurate
    high_accuracy = sum(1 for c in report if c['accuracy_score'] > 90)
    medium_accuracy = sum(1 for c in report if 70 <= c['accuracy_score'] <= 90)
    low_accuracy = sum(1 for c in report if c['accuracy_score'] < 70)
    
    print(f"\nAccuracy Distribution:")
    print(f"  High (>90%): {high_accuracy} celebrities")
    print(f"  Medium (70-90%): {medium_accuracy} celebrities")
    print(f"  Low (<70%): {low_accuracy} celebrities")
    
    # Save detailed report
    output_path = Path("accuracy_analysis_report.json")
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"\nDetailed report saved to: {output_path}")

if __name__ == "__main__":
    report = analyze_accuracy()
    print_accuracy_report(report)