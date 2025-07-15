#!/usr/bin/env python3
"""
Validate our astrology calculations against VedicAstroAPI test data.
This script compares our calculated values with the reference data.
"""
import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple
import logging
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from josi.services.astrology_service import AstrologyCalculator
from josi.services.vedic.panchang_service import PanchangService
from josi.services.vedic.dasha_service import DashaService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Paths
TEST_DATA_DIR = Path("test_data/vedicastro_api")
PROCESSED_DATA_DIR = TEST_DATA_DIR / "processed_data"
VALIDATION_RESULTS_DIR = TEST_DATA_DIR / "validation_results"

# Validation thresholds
THRESHOLDS = {
    "planetary_longitude": 0.01,  # degrees
    "planetary_latitude": 0.01,   # degrees
    "ascendant": 0.1,            # degrees
    "house_cusps": 0.5,          # degrees
    "dasha_dates": 1,            # days
}

class AstrologyValidator:
    """Validates our calculations against reference data"""
    
    def __init__(self):
        self.astro_calc = AstrologyCalculator()
        self.panchang_service = PanchangService()
        self.dasha_service = DashaService()
        self.results = {
            "passed": 0,
            "failed": 0,
            "discrepancies": []
        }
    
    async def validate_planetary_positions(self, reference_data: List[Dict]) -> Dict:
        """Validate planetary position calculations"""
        logger.info("Validating planetary positions...")
        
        results = []
        test_cases = {}
        
        # Group by test case
        for item in reference_data:
            test_name = item['test_case']
            if test_name not in test_cases:
                test_cases[test_name] = []
            test_cases[test_name].append(item)
        
        for test_name, planets in test_cases.items():
            logger.info(f"  Testing: {test_name}")
            
            # Get test case details from collected data
            test_data_file = TEST_DATA_DIR / f"collected_{test_name}.json"
            if not test_data_file.exists():
                logger.warning(f"  Test data file not found: {test_data_file}")
                continue
            
            with open(test_data_file, 'r') as f:
                test_data = json.load(f)
            
            test_case = test_data['test_case']
            
            # Parse date and time
            dob_parts = test_case['dob'].split('/')
            tob_parts = test_case['tob'].split(':')
            
            birth_datetime = datetime(
                int(dob_parts[2]),  # year
                int(dob_parts[1]),  # month
                int(dob_parts[0]),  # day
                int(tob_parts[0]),  # hour
                int(tob_parts[1])   # minute
            )
            
            # Calculate using our system
            try:
                our_positions = await self.astro_calc.calculate_chart(
                    birth_datetime,
                    test_case['lat'],
                    test_case['lon'],
                    test_case['tz']
                )
                
                # Compare each planet
                for ref_planet in planets:
                    planet_name = ref_planet['planet']
                    ref_longitude = ref_planet['longitude']
                    
                    # Find our calculated value
                    our_planet = None
                    for p in our_positions.get('planets', []):
                        if p['name'].lower() == planet_name.lower():
                            our_planet = p
                            break
                    
                    if our_planet:
                        our_longitude = our_planet['longitude']
                        difference = abs(our_longitude - ref_longitude)
                        
                        passed = difference <= THRESHOLDS['planetary_longitude']
                        
                        result = {
                            "test_case": test_name,
                            "planet": planet_name,
                            "reference": ref_longitude,
                            "calculated": our_longitude,
                            "difference": difference,
                            "threshold": THRESHOLDS['planetary_longitude'],
                            "passed": passed
                        }
                        
                        results.append(result)
                        
                        if passed:
                            self.results['passed'] += 1
                        else:
                            self.results['failed'] += 1
                            self.results['discrepancies'].append(result)
                            logger.warning(f"    {planet_name}: diff={difference:.4f}° (threshold={THRESHOLDS['planetary_longitude']}°)")
                    else:
                        logger.error(f"    Planet {planet_name} not found in our calculations")
                        
            except Exception as e:
                logger.error(f"  Error calculating for {test_name}: {e}")
        
        return {
            "category": "planetary_positions",
            "total_tests": len(results),
            "passed": sum(1 for r in results if r['passed']),
            "failed": sum(1 for r in results if not r['passed']),
            "details": results
        }
    
    async def validate_ascendants(self, reference_data: List[Dict]) -> Dict:
        """Validate ascendant calculations"""
        logger.info("Validating ascendants...")
        
        results = []
        
        for ref_data in reference_data:
            test_name = ref_data['test_case']
            ref_ascendant = ref_data['ascendant_degree']
            
            # Get test case details
            test_data_file = TEST_DATA_DIR / f"collected_{test_name}.json"
            if not test_data_file.exists():
                continue
            
            with open(test_data_file, 'r') as f:
                test_data = json.load(f)
            
            test_case = test_data['test_case']
            
            # Parse date and time
            dob_parts = test_case['dob'].split('/')
            tob_parts = test_case['tob'].split(':')
            
            birth_datetime = datetime(
                int(dob_parts[2]),
                int(dob_parts[1]),
                int(dob_parts[0]),
                int(tob_parts[0]),
                int(tob_parts[1])
            )
            
            try:
                our_chart = await self.astro_calc.calculate_chart(
                    birth_datetime,
                    test_case['lat'],
                    test_case['lon'],
                    test_case['tz']
                )
                
                our_ascendant = our_chart.get('ascendant', {}).get('degree', 0)
                difference = abs(our_ascendant - ref_ascendant)
                
                passed = difference <= THRESHOLDS['ascendant']
                
                result = {
                    "test_case": test_name,
                    "reference": ref_ascendant,
                    "calculated": our_ascendant,
                    "difference": difference,
                    "threshold": THRESHOLDS['ascendant'],
                    "passed": passed
                }
                
                results.append(result)
                
                if passed:
                    self.results['passed'] += 1
                else:
                    self.results['failed'] += 1
                    self.results['discrepancies'].append(result)
                    logger.warning(f"  {test_name}: diff={difference:.4f}° (threshold={THRESHOLDS['ascendant']}°)")
                    
            except Exception as e:
                logger.error(f"  Error calculating ascendant for {test_name}: {e}")
        
        return {
            "category": "ascendants",
            "total_tests": len(results),
            "passed": sum(1 for r in results if r['passed']),
            "failed": sum(1 for r in results if not r['passed']),
            "details": results
        }
    
    async def validate_panchang(self, reference_data: List[Dict]) -> Dict:
        """Validate panchang calculations"""
        logger.info("Validating panchang elements...")
        
        results = []
        
        for ref_data in reference_data:
            test_name = ref_data['test_case']
            
            # Get test case details
            test_data_file = TEST_DATA_DIR / f"collected_{test_name}.json"
            if not test_data_file.exists():
                continue
            
            with open(test_data_file, 'r') as f:
                test_data = json.load(f)
            
            test_case = test_data['test_case']
            
            # Parse date and time
            dob_parts = test_case['dob'].split('/')
            tob_parts = test_case['tob'].split(':')
            
            birth_datetime = datetime(
                int(dob_parts[2]),
                int(dob_parts[1]),
                int(dob_parts[0]),
                int(tob_parts[0]),
                int(tob_parts[1])
            )
            
            try:
                our_panchang = await self.panchang_service.calculate_panchang(
                    birth_datetime,
                    test_case['lat'],
                    test_case['lon'],
                    test_case['tz']
                )
                
                # Compare elements
                elements = ['tithi', 'nakshatra', 'yoga', 'karana']
                
                for element in elements:
                    ref_value = ref_data.get(element, '')
                    our_value = our_panchang.get(element, {}).get('name', '')
                    
                    # Normalize names for comparison
                    ref_normalized = ref_value.lower().strip()
                    our_normalized = our_value.lower().strip()
                    
                    passed = ref_normalized == our_normalized
                    
                    result = {
                        "test_case": test_name,
                        "element": element,
                        "reference": ref_value,
                        "calculated": our_value,
                        "passed": passed
                    }
                    
                    results.append(result)
                    
                    if passed:
                        self.results['passed'] += 1
                    else:
                        self.results['failed'] += 1
                        self.results['discrepancies'].append(result)
                        logger.warning(f"  {test_name} - {element}: '{ref_value}' != '{our_value}'")
                        
            except Exception as e:
                logger.error(f"  Error calculating panchang for {test_name}: {e}")
        
        return {
            "category": "panchang",
            "total_tests": len(results),
            "passed": sum(1 for r in results if r['passed']),
            "failed": sum(1 for r in results if not r['passed']),
            "details": results
        }
    
    def generate_report(self, validation_results: List[Dict]) -> None:
        """Generate validation report"""
        logger.info("\nGenerating validation report...")
        
        report = {
            "validation_date": datetime.utcnow().isoformat(),
            "summary": {
                "total_tests": self.results['passed'] + self.results['failed'],
                "passed": self.results['passed'],
                "failed": self.results['failed'],
                "accuracy_percentage": (self.results['passed'] / (self.results['passed'] + self.results['failed']) * 100) if (self.results['passed'] + self.results['failed']) > 0 else 0
            },
            "categories": validation_results,
            "discrepancies": self.results['discrepancies'],
            "thresholds_used": THRESHOLDS
        }
        
        # Save report
        report_file = VALIDATION_RESULTS_DIR / f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print("\n" + "="*60)
        print("VALIDATION SUMMARY")
        print("="*60)
        print(f"Total Tests: {report['summary']['total_tests']}")
        print(f"Passed: {report['summary']['passed']}")
        print(f"Failed: {report['summary']['failed']}")
        print(f"Accuracy: {report['summary']['accuracy_percentage']:.2f}%")
        print("="*60)
        
        if self.results['discrepancies']:
            print("\nTop discrepancies:")
            for disc in self.results['discrepancies'][:10]:
                if 'planet' in disc:
                    print(f"  - {disc['test_case']} / {disc['planet']}: diff={disc['difference']:.4f}°")
                elif 'element' in disc:
                    print(f"  - {disc['test_case']} / {disc['element']}: '{disc['reference']}' != '{disc['calculated']}'")
        
        print(f"\nFull report saved to: {report_file}")

async def main():
    """Main validation function"""
    logger.info("Starting validation against VedicAstroAPI data...")
    
    # Check if test data exists
    if not PROCESSED_DATA_DIR.exists():
        logger.error(f"Test data not found! Please run collect_vedicastro_test_data.py first.")
        return
    
    validator = AstrologyValidator()
    validation_results = []
    
    # Validate planetary positions
    planet_data_file = PROCESSED_DATA_DIR / "planetary_positions.json"
    if planet_data_file.exists():
        with open(planet_data_file, 'r') as f:
            planet_data = json.load(f)
        result = await validator.validate_planetary_positions(planet_data)
        validation_results.append(result)
    
    # Validate ascendants
    ascendant_data_file = PROCESSED_DATA_DIR / "ascendants.json"
    if ascendant_data_file.exists():
        with open(ascendant_data_file, 'r') as f:
            ascendant_data = json.load(f)
        result = await validator.validate_ascendants(ascendant_data)
        validation_results.append(result)
    
    # Validate panchang
    panchang_data_file = PROCESSED_DATA_DIR / "panchang_elements.json"
    if panchang_data_file.exists():
        with open(panchang_data_file, 'r') as f:
            panchang_data = json.load(f)
        result = await validator.validate_panchang(panchang_data)
        validation_results.append(result)
    
    # Generate report
    validator.generate_report(validation_results)

if __name__ == "__main__":
    asyncio.run(main())