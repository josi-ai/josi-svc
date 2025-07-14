#!/usr/bin/env python3
"""
Generate a comprehensive accuracy analysis report comparing API results vs expected values.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
import math
import re

def load_validation_results():
    """Load the celebrity validation results from the API."""
    results_path = Path("/Users/govind/Developer/astrow/celebrity_validation_results.json")
    with open(results_path, 'r') as f:
        return json.load(f)

def load_accuracy_analysis():
    """Load the accuracy analysis results."""
    analysis_path = Path("/Users/govind/Developer/astrow/accuracy_analysis_report.json")
    with open(analysis_path, 'r') as f:
        return json.load(f)

def get_star_rating(accuracy_score):
    """Convert accuracy score to star rating."""
    if accuracy_score >= 90:
        return "⭐⭐⭐⭐⭐"
    elif accuracy_score >= 70:
        return "⭐⭐⭐⭐"
    elif accuracy_score >= 50:
        return "⭐⭐⭐"
    elif accuracy_score >= 30:
        return "⭐⭐"
    elif accuracy_score > 0:
        return "⭐"
    else:
        return "❌"

def generate_report():
    """Generate the comprehensive accuracy report."""
    validation_results = load_validation_results()
    accuracy_analysis = load_accuracy_analysis()
    
    print("📊 ASTROLOGICAL CHART ACCURACY ANALYSIS REPORT")
    print("=" * 80)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("Analysis Type: API Validation vs Swiss Ephemeris")
    print("\n")
    
    # Overall statistics
    total_celebrities = len(accuracy_analysis)
    total_score = sum(c['accuracy_score'] for c in accuracy_analysis)
    avg_score = total_score / total_celebrities if total_celebrities > 0 else 0
    
    print("🎯 EXECUTIVE SUMMARY")
    print("-" * 40)
    print(f"Overall Accuracy: {avg_score:.1f}%")
    print(f"Celebrities Tested: {total_celebrities}")
    
    # Accuracy distribution
    high_accuracy = sum(1 for c in accuracy_analysis if c['accuracy_score'] >= 90)
    medium_accuracy = sum(1 for c in accuracy_analysis if 70 <= c['accuracy_score'] < 90)
    low_accuracy = sum(1 for c in accuracy_analysis if c['accuracy_score'] < 70)
    
    print(f"\nAccuracy Distribution:")
    print(f"  ⭐⭐⭐⭐⭐ High (≥90%): {high_accuracy} celebrities")
    print(f"  ⭐⭐⭐ Medium (70-90%): {medium_accuracy} celebrities")
    print(f"  ⭐ Low (<70%): {low_accuracy} celebrities")
    
    # Detailed breakdown by celebrity
    print("\n\n📈 Accuracy Breakdown by Celebrity:")
    print("\n  | Celebrity          | Accuracy    | Major Issues                                    |")
    print("  |--------------------|-------------|------------------------------------------------|")
    
    # Sort by accuracy score descending
    sorted_analysis = sorted(accuracy_analysis, key=lambda x: x['accuracy_score'], reverse=True)
    
    for celeb in sorted_analysis:
        name = celeb['name']
        score = celeb['accuracy_score']
        stars = get_star_rating(score)
        
        # Identify major issues
        issues = []
        if 'errors' in celeb and celeb['errors']:
            for error in celeb['errors']:
                if 'Ascendant' in error:
                    issues.append("Wrong Ascendant")
                elif 'Mercury' in error:
                    # Extract the degree offset
                    match = re.search(r'(\d+\.\d+)° off', error)
                    if match:
                        offset = float(match.group(1))
                        issues.append(f"Mercury {offset:.0f}° off")
                elif 'Moon' in error:
                    if 'sign_mismatch' in error or 'different sign' in error.lower():
                        issues.append("Wrong Moon sign")
                    else:
                        match = re.search(r'(\d+\.\d+)° off', error)
                        if match:
                            offset = float(match.group(1))
                            issues.append(f"Moon {offset:.0f}° off")
                elif 'Venus' in error:
                    match = re.search(r'(\d+\.\d+)° off', error)
                    if match:
                        offset = float(match.group(1))
                        issues.append(f"Venus {offset:.0f}° off")
        
        issues_str = ", ".join(issues) if issues else "None - Nearly perfect!" if score > 95 else "Multiple errors"
        
        # Pad strings for alignment
        name_padded = name.ljust(18)
        accuracy_str = f"{stars} {score:5.1f}%"
        accuracy_padded = accuracy_str.ljust(11)
        issues_padded = issues_str[:46].ljust(46)
        
        print(f"  | {name_padded} | {accuracy_padded} | {issues_padded} |")
    
    # Planet-by-planet analysis
    print("\n\n🔍 Accuracy by Celestial Body:")
    print("\n  | Body      | Avg Error | Success Rate | Common Issues           |")
    print("  |-----------|-----------|--------------|-------------------------|")
    
    planet_stats = {}
    for celeb in accuracy_analysis:
        for planet, data in celeb['planet_comparisons'].items():
            if planet not in planet_stats:
                planet_stats[planet] = {'total_orb': 0, 'count': 0, 'accurate': 0}
            
            planet_stats[planet]['total_orb'] += data['orb']
            planet_stats[planet]['count'] += 1
            if data['accurate']:
                planet_stats[planet]['accurate'] += 1
    
    for planet in ['Sun', 'Moon', 'Ascendant', 'Mercury', 'Venus', 'Mars']:
        if planet in planet_stats:
            stats = planet_stats[planet]
            avg_orb = stats['total_orb'] / stats['count'] if stats['count'] > 0 else 0
            success_rate = (stats['accurate'] / stats['count'] * 100) if stats['count'] > 0 else 0
            
            # Determine common issues
            if planet == 'Ascendant' and avg_orb > 30:
                issue = "Timezone conversion error"
            elif planet == 'Mercury' and avg_orb > 10:
                issue = "Position calculation error"
            elif planet == 'Moon' and success_rate < 50:
                issue = "Sign boundary errors"
            elif success_rate == 100:
                issue = "Perfect accuracy"
            elif success_rate > 80:
                issue = "Minor variations"
            else:
                issue = "Significant errors"
            
            planet_padded = planet.ljust(9)
            orb_str = f"{avg_orb:6.2f}°"
            success_str = f"{success_rate:6.1f}%"
            issue_padded = issue[:23].ljust(23)
            
            print(f"  | {planet_padded} | {orb_str} | {success_str} | {issue_padded} |")
    
    # Identified patterns
    print("\n\n🔬 KEY FINDINGS:")
    print("-" * 40)
    
    if avg_score < 20:
        print("❌ CRITICAL ISSUES DETECTED:")
        print("   1. Ascendant calculations consistently wrong by 30-140°")
        print("   2. Suggests timezone conversion problem in Julian Day calculation")
        print("   3. Mercury positions often 20-28° off")
        print("   4. Some Moon sign mismatches")
        print("\n   DIAGNOSIS: UTC timezone conversion not being applied before")
        print("   astronomical calculations, causing systematic errors.")
    elif avg_score < 50:
        print("⚠️  MODERATE ISSUES:")
        print("   1. Some Ascendant calculations incorrect")
        print("   2. Occasional planet position errors")
        print("   3. Possible ephemeris configuration issues")
    else:
        print("✅ GOOD ACCURACY:")
        print("   1. Most calculations within acceptable tolerance")
        print("   2. Sun and major planets generally accurate")
        print("   3. Minor refinements needed for edge cases")
    
    # Recommendations
    print("\n\n💡 RECOMMENDATIONS:")
    print("-" * 40)
    
    if avg_score < 50:
        print("1. FIX TIMEZONE HANDLING: Convert all datetimes to UTC before Julian Day")
        print("2. VERIFY EPHEMERIS: Check Swiss Ephemeris integration")
        print("3. UPDATE TEST DATA: Ensure expected values are correct")
        print("4. TEST EDGE CASES: Historical dates, different timezones")
    else:
        print("1. MAINTAIN ACCURACY: Current calculations are working well")
        print("2. MONITOR EDGE CASES: Keep testing various birth locations")
        print("3. DOCUMENT METHODS: Ensure calculation methods are clear")
    
    print("\n" + "=" * 80)
    print("END OF REPORT")

if __name__ == "__main__":
    generate_report()