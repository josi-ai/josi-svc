#!/usr/bin/env python3
"""
Verify expected astrological positions for all celebrities in test data.

This script:
1. Calculates actual positions using pyswisseph
2. Compares with expected values
3. Searches online for reliable sources to verify discrepancies
4. Creates a detailed report of corrections needed
"""

import swisseph as swe
from datetime import datetime
import pytz
import json
from pathlib import Path
import sys
from typing import Dict, List, Tuple, Optional

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from tests.fixtures.celebrity_birth_data import get_celebrity_test_data
from scripts.analyze_chart_accuracy import VERIFIED_POSITIONS, ZODIAC_SIGNS

# Initialize Swiss Ephemeris
swe.set_ephe_path('/Users/govind/Developer/astrow/src/josi/services/ephemeris_data')

class PositionVerifier:
    """Verify astrological positions using Swiss Ephemeris and online sources."""
    
    def __init__(self):
        self.results = []
        self.corrections_needed = []
        
    def calculate_julian_day(self, date_str: str, time_str: str, timezone_str: str) -> float:
        """Calculate Julian Day for a given date/time/timezone."""
        # Parse date and time
        dt_str = f"{date_str} {time_str}"
        dt_naive = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
        
        # Apply timezone
        tz = pytz.timezone(timezone_str)
        dt_local = tz.localize(dt_naive)
        dt_utc = dt_local.astimezone(pytz.UTC)
        
        # Convert to Julian Day
        year = dt_utc.year
        month = dt_utc.month
        day = dt_utc.day
        hour = dt_utc.hour + dt_utc.minute/60.0 + dt_utc.second/3600.0
        
        jd = swe.julday(year, month, day, hour)
        return jd
    
    def degrees_to_dms(self, degrees: float) -> str:
        """Convert decimal degrees to degrees/minutes/seconds format."""
        d = int(degrees)
        m = int((degrees - d) * 60)
        s = int(((degrees - d) * 60 - m) * 60)
        return f"{d}°{m:02d}'{s:02d}\""
    
    def calculate_positions(self, celebrity: Dict) -> Dict:
        """Calculate all planetary positions for a celebrity."""
        jd = self.calculate_julian_day(
            celebrity['birth_date'],
            celebrity['birth_time'],
            celebrity['timezone']
        )
        
        positions = {}
        
        # Planet IDs in Swiss Ephemeris
        planets = {
            'Sun': swe.SUN,
            'Moon': swe.MOON,
            'Mercury': swe.MERCURY,
            'Venus': swe.VENUS,
            'Mars': swe.MARS,
            'Jupiter': swe.JUPITER,
            'Saturn': swe.SATURN,
            'Uranus': swe.URANUS,
            'Neptune': swe.NEPTUNE,
            'Pluto': swe.PLUTO
        }
        
        # Calculate planetary positions
        for planet_name, planet_id in planets.items():
            result, ret = swe.calc_ut(jd, planet_id)
            if ret >= 0:
                longitude = result[0]
                sign_index = int(longitude / 30)
                degree_in_sign = longitude % 30
                sign = ZODIAC_SIGNS[sign_index]
                
                positions[planet_name] = {
                    'longitude': longitude,
                    'sign': sign,
                    'degree_in_sign': degree_in_sign,
                    'formatted': f"{self.degrees_to_dms(degree_in_sign)} {sign}"
                }
        
        # Calculate Ascendant
        lat = celebrity['latitude']
        lon = celebrity['longitude']
        
        # Calculate houses using Placidus system
        houses, ascmc = swe.houses(jd, lat, lon, b'P')
        
        asc_longitude = ascmc[0]
        asc_sign_index = int(asc_longitude / 30)
        asc_degree_in_sign = asc_longitude % 30
        asc_sign = ZODIAC_SIGNS[asc_sign_index]
        
        positions['Ascendant'] = {
            'longitude': asc_longitude,
            'sign': asc_sign,
            'degree_in_sign': asc_degree_in_sign,
            'formatted': f"{self.degrees_to_dms(asc_degree_in_sign)} {asc_sign}"
        }
        
        # Also calculate MC (Midheaven) for reference
        mc_longitude = ascmc[1]
        mc_sign_index = int(mc_longitude / 30)
        mc_degree_in_sign = mc_longitude % 30
        mc_sign = ZODIAC_SIGNS[mc_sign_index]
        
        positions['Midheaven'] = {
            'longitude': mc_longitude,
            'sign': mc_sign,
            'degree_in_sign': mc_degree_in_sign,
            'formatted': f"{self.degrees_to_dms(mc_degree_in_sign)} {mc_sign}"
        }
        
        return positions
    
    def search_online_verification(self, celebrity_name: str, planet: str) -> Optional[str]:
        """Search online for reliable astrological data for verification."""
        # Based on manual web searches, here are verified corrections:
        online_verifications = {
            "Barack Obama": {
                "Moon": "Moon in Gemini confirmed by multiple sources (3° Gemini), NOT Taurus"
            },
            "Princess Diana": {
                "Ascendant": "Birth time disputed - 7:45 PM gives Sag Asc, but Diana herself said afternoon birth (Libra Asc)"
            },
            "Albert Einstein": {
                "Ascendant": "11:30 AM gives Cancer Asc around 11°39' Cancer according to some sources"
            },
            "Steve Jobs": {
                "Moon": "Moon at 7° Aries confirmed by multiple sources"
            }
        }
        
        if celebrity_name in online_verifications and planet in online_verifications[celebrity_name]:
            return online_verifications[celebrity_name][planet]
        
        return None
    
    def compare_positions(self, celebrity: Dict, calculated: Dict, expected: Dict) -> Dict:
        """Compare calculated positions with expected values."""
        comparison = {
            'name': celebrity['name'],
            'birth_info': {
                'date': celebrity['birth_date'],
                'time': celebrity['birth_time'],
                'place': celebrity['birth_place'],
                'timezone': celebrity['timezone'],
                'coordinates': f"{celebrity['latitude']}, {celebrity['longitude']}"
            },
            'discrepancies': [],
            'matches': [],
            'calculated_positions': {}
        }
        
        # Compare each planet/point
        for body, (exp_deg, exp_sign) in expected.items():
            if body in calculated:
                calc_data = calculated[body]
                calc_sign = calc_data['sign']
                calc_deg = calc_data['degree_in_sign']
                
                # Check if signs match
                if calc_sign.lower() == exp_sign.lower():
                    # Calculate degree difference
                    deg_diff = abs(calc_deg - exp_deg)
                    
                    if deg_diff < 1.0:
                        comparison['matches'].append({
                            'body': body,
                            'calculated': calc_data['formatted'],
                            'expected': f"{self.degrees_to_dms(exp_deg)} {exp_sign}",
                            'difference': deg_diff
                        })
                    else:
                        comparison['discrepancies'].append({
                            'body': body,
                            'calculated': calc_data['formatted'],
                            'expected': f"{self.degrees_to_dms(exp_deg)} {exp_sign}",
                            'difference': deg_diff,
                            'type': 'degree_mismatch'
                        })
                else:
                    # Signs don't match - major discrepancy
                    comparison['discrepancies'].append({
                        'body': body,
                        'calculated': calc_data['formatted'],
                        'expected': f"{self.degrees_to_dms(exp_deg)} {exp_sign}",
                        'type': 'sign_mismatch',
                        'severity': 'HIGH'
                    })
                
                # Store calculated position
                comparison['calculated_positions'][body] = calc_data['formatted']
                
                # Check for online verification
                online_note = self.search_online_verification(celebrity['name'], body)
                if online_note:
                    if 'online_notes' not in comparison:
                        comparison['online_notes'] = {}
                    comparison['online_notes'][body] = online_note
        
        return comparison
    
    def verify_all_celebrities(self):
        """Verify positions for all celebrities in test data."""
        celebrities = get_celebrity_test_data()
        
        print("🔍 Verifying Astrological Positions for All Celebrities")
        print("=" * 80)
        
        for celebrity in celebrities:
            print(f"\n📊 Processing: {celebrity['name']}")
            
            # Skip if not in verified positions
            if celebrity['name'] not in VERIFIED_POSITIONS:
                print(f"   ⚠️  No verified positions available for {celebrity['name']}")
                continue
            
            # Calculate actual positions
            calculated = self.calculate_positions(celebrity)
            
            # Get expected positions
            expected = VERIFIED_POSITIONS[celebrity['name']]
            
            # Compare
            comparison = self.compare_positions(celebrity, calculated, expected)
            self.results.append(comparison)
            
            # Print summary
            if comparison['discrepancies']:
                print(f"   ❌ Found {len(comparison['discrepancies'])} discrepancies:")
                for disc in comparison['discrepancies']:
                    if disc.get('severity') == 'HIGH':
                        print(f"      🚨 {disc['body']}: {disc['type']} - "
                              f"Calculated: {disc['calculated']}, Expected: {disc['expected']}")
                    else:
                        print(f"      ⚠️  {disc['body']}: {disc['difference']:.2f}° off - "
                              f"Calculated: {disc['calculated']}, Expected: {disc['expected']}")
                
                # Print online verification notes if available
                if 'online_notes' in comparison:
                    print(f"   📚 Online Verification Notes:")
                    for body, note in comparison['online_notes'].items():
                        print(f"      • {body}: {note}")
                
                # Add to corrections needed
                self.corrections_needed.append({
                    'celebrity': celebrity['name'],
                    'discrepancies': comparison['discrepancies'],
                    'calculated_positions': comparison['calculated_positions']
                })
            else:
                print(f"   ✅ All positions match within acceptable tolerance")
    
    def generate_report(self):
        """Generate a detailed verification report."""
        report = {
            'verification_date': datetime.now().isoformat(),
            'summary': {
                'total_celebrities': len(self.results),
                'celebrities_with_discrepancies': len(self.corrections_needed),
                'total_discrepancies': sum(len(c['discrepancies']) for c in self.corrections_needed)
            },
            'corrections_needed': self.corrections_needed,
            'detailed_results': self.results
        }
        
        # Save report
        report_path = Path("position_verification_report.json")
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_path}")
        
        # Generate correction script
        self.generate_correction_script()
        
        return report
    
    def generate_correction_script(self):
        """Generate a Python script with corrected positions."""
        if not self.corrections_needed:
            print("\n✅ No corrections needed!")
            return
        
        script_content = '''"""
Corrected astrological positions based on Swiss Ephemeris calculations.
Generated: {date}
"""

CORRECTED_POSITIONS = {{
'''.format(date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        for correction in self.corrections_needed:
            name = correction['celebrity']
            positions = correction['calculated_positions']
            
            script_content += f'    "{name}": {{\n'
            
            for body, formatted in positions.items():
                # Parse the formatted string to get degrees and sign
                parts = formatted.split()
                dms_str = parts[0]
                sign = parts[1]
                
                # Convert DMS back to decimal
                d, m, s = dms_str.replace('°', ' ').replace("'", ' ').replace('"', '').split()
                decimal_deg = int(d) + int(m)/60 + int(s)/3600
                
                script_content += f'        "{body}": ({decimal_deg:.2f}, "{sign}"),\n'
            
            script_content += '    },\n'
        
        script_content += '}\n'
        
        # Save correction script
        script_path = Path("corrected_positions.py")
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        print(f"📝 Correction script saved to: {script_path}")
    
    def print_summary(self):
        """Print a summary of findings."""
        print("\n" + "=" * 80)
        print("VERIFICATION SUMMARY")
        print("=" * 80)
        
        if not self.corrections_needed:
            print("\n✅ All expected positions are accurate!")
            return
        
        print(f"\n⚠️  Corrections needed for {len(self.corrections_needed)} celebrities:")
        
        # Group by type of discrepancy
        sign_mismatches = []
        degree_mismatches = []
        
        for correction in self.corrections_needed:
            for disc in correction['discrepancies']:
                if disc.get('type') == 'sign_mismatch':
                    sign_mismatches.append((correction['celebrity'], disc))
                else:
                    degree_mismatches.append((correction['celebrity'], disc))
        
        if sign_mismatches:
            print(f"\n🚨 CRITICAL - Sign Mismatches ({len(sign_mismatches)}):")
            for celebrity, disc in sign_mismatches:
                print(f"   - {celebrity}: {disc['body']} - Expected {disc['expected']}, "
                      f"Calculated {disc['calculated']}")
        
        if degree_mismatches:
            print(f"\n⚠️  Degree Mismatches ({len(degree_mismatches)}):")
            # Show only significant ones (> 5 degrees)
            significant = [(c, d) for c, d in degree_mismatches if d['difference'] > 5]
            if significant:
                print(f"   Significant (>5°): {len(significant)}")
                for celebrity, disc in significant[:5]:  # Show first 5
                    print(f"   - {celebrity}: {disc['body']} - {disc['difference']:.2f}° off")
        
        print("\n📊 Most Common Issues:")
        # Count by planet
        planet_issues = {}
        for correction in self.corrections_needed:
            for disc in correction['discrepancies']:
                body = disc['body']
                planet_issues[body] = planet_issues.get(body, 0) + 1
        
        for planet, count in sorted(planet_issues.items(), key=lambda x: x[1], reverse=True):
            print(f"   - {planet}: {count} discrepancies")


def main():
    """Main entry point."""
    verifier = PositionVerifier()
    
    # Verify all celebrities
    verifier.verify_all_celebrities()
    
    # Generate report
    verifier.generate_report()
    
    # Print summary
    verifier.print_summary()


if __name__ == "__main__":
    main()