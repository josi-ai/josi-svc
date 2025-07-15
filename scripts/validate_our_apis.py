#!/usr/bin/env python3
"""
Validate our API endpoints against VedicAstroAPI test data.
This script calls our APIs and compares results with stored VedicAstroAPI data.
"""
import asyncio
import json
import httpx
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
from uuid import UUID

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
OUR_API_BASE = "http://localhost:8000/api/v1"
API_KEY = "your-api-key-here"  # Replace with actual API key
TEST_DATA_DIR = Path("test_data/vedicastro_api")

class APIValidator:
    """Validates our API endpoints against VedicAstroAPI reference data"""
    
    def __init__(self, base_url: str = OUR_API_BASE, api_key: str = API_KEY):
        self.base_url = base_url
        self.headers = {"X-API-Key": api_key}
        self.client = httpx.AsyncClient(timeout=30.0)
        self.results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "endpoint_results": {}
        }
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
    
    async def create_test_person(self, test_case: Dict) -> Optional[UUID]:
        """Create a person for testing"""
        # Parse date
        dob_parts = test_case['dob'].split('/')
        tob_parts = test_case['tob'].split(':')
        
        person_data = {
            "name": test_case.get('name', 'Test Person'),
            "birth_date": f"{dob_parts[2]}-{dob_parts[1]}-{dob_parts[0]}",
            "birth_time": f"{tob_parts[0]}:{tob_parts[1]}:00",
            "birth_place": test_case.get('name', 'Test Location'),
            "latitude": test_case['lat'],
            "longitude": test_case['lon'],
            "timezone": test_case['tz'],
            "gender": "male"
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/persons",
                json=person_data,
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                return UUID(data['data']['person_id'])
            else:
                logger.error(f"Failed to create person: {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error creating person: {e}")
            return None
    
    async def validate_chart_calculation(self, person_id: UUID, reference_data: Dict) -> Dict:
        """Validate chart calculation endpoint"""
        logger.info("Validating /charts/calculate endpoint...")
        
        results = {
            "endpoint": "/charts/calculate",
            "tests": []
        }
        
        try:
            # Call our API
            response = await self.client.post(
                f"{self.base_url}/charts/calculate",
                params={
                    "person_id": str(person_id),
                    "systems": "vedic",
                    "house_system": "PLACIDUS",
                    "ayanamsa": "LAHIRI"
                },
                headers=self.headers
            )
            
            if response.status_code != 200:
                logger.error(f"Chart calculation failed: {response.text}")
                return results
            
            our_data = response.json()['data'][0]  # First chart (Vedic)
            
            # Compare planetary positions
            if 'planet_details' in reference_data:
                ref_planets = reference_data['planet_details']['response']
                our_planets = our_data['planets']
                
                for ref_planet in ref_planets:
                    planet_name = ref_planet['name']
                    
                    # Find matching planet in our data
                    our_planet = next(
                        (p for p in our_planets if p['name'].lower() == planet_name.lower()),
                        None
                    )
                    
                    if our_planet:
                        diff = abs(our_planet['longitude'] - ref_planet['longitude'])
                        passed = diff < 0.01  # 0.01° tolerance
                        
                        test_result = {
                            "test": f"Planet {planet_name} longitude",
                            "reference": ref_planet['longitude'],
                            "calculated": our_planet['longitude'],
                            "difference": diff,
                            "passed": passed
                        }
                        
                        results['tests'].append(test_result)
                        self.results['total_tests'] += 1
                        
                        if passed:
                            self.results['passed'] += 1
                        else:
                            self.results['failed'] += 1
                            logger.warning(f"  {planet_name}: diff={diff:.4f}°")
            
            # Compare ascendant
            if 'extended_kundli' in reference_data:
                ref_asc = reference_data['extended_kundli']['response'].get('ascendant_degree', 0)
                our_asc = our_data['ascendant']['degree']
                
                diff = abs(our_asc - ref_asc)
                passed = diff < 0.1  # 0.1° tolerance for ascendant
                
                test_result = {
                    "test": "Ascendant degree",
                    "reference": ref_asc,
                    "calculated": our_asc,
                    "difference": diff,
                    "passed": passed
                }
                
                results['tests'].append(test_result)
                self.results['total_tests'] += 1
                
                if passed:
                    self.results['passed'] += 1
                else:
                    self.results['failed'] += 1
                    logger.warning(f"  Ascendant: diff={diff:.4f}°")
                    
        except Exception as e:
            logger.error(f"Error validating chart calculation: {e}")
        
        return results
    
    async def validate_panchang(self, person_id: UUID, reference_data: Dict) -> Dict:
        """Validate panchang calculation endpoint"""
        logger.info("Validating /panchang/calculate endpoint...")
        
        results = {
            "endpoint": "/panchang/calculate",
            "tests": []
        }
        
        try:
            # Get person details first
            person_response = await self.client.get(
                f"{self.base_url}/persons/{person_id}",
                headers=self.headers
            )
            
            if person_response.status_code != 200:
                logger.error(f"Failed to get person: {person_response.text}")
                return results
            
            person = person_response.json()['data']
            
            # Call our panchang API
            response = await self.client.get(
                f"{self.base_url}/panchang/calculate",
                params={
                    "date": person['birth_date'],
                    "time": person['birth_time'],
                    "latitude": person['latitude'],
                    "longitude": person['longitude'],
                    "timezone": person['timezone']
                },
                headers=self.headers
            )
            
            if response.status_code != 200:
                logger.error(f"Panchang calculation failed: {response.text}")
                return results
            
            our_data = response.json()['data']
            
            # Compare panchang elements
            if 'panchang' in reference_data:
                ref_panchang = reference_data['panchang']['response']
                
                elements = ['tithi', 'nakshatra', 'yoga', 'karana']
                for element in elements:
                    ref_value = ref_panchang.get(element, '')
                    our_value = our_data.get(element, {}).get('name', '')
                    
                    # Normalize for comparison
                    ref_normalized = ref_value.lower().replace(' ', '').replace('-', '')
                    our_normalized = our_value.lower().replace(' ', '').replace('-', '')
                    
                    passed = ref_normalized == our_normalized
                    
                    test_result = {
                        "test": f"Panchang {element}",
                        "reference": ref_value,
                        "calculated": our_value,
                        "passed": passed
                    }
                    
                    results['tests'].append(test_result)
                    self.results['total_tests'] += 1
                    
                    if passed:
                        self.results['passed'] += 1
                    else:
                        self.results['failed'] += 1
                        logger.warning(f"  {element}: '{ref_value}' != '{our_value}'")
                        
        except Exception as e:
            logger.error(f"Error validating panchang: {e}")
        
        return results
    
    async def validate_dasha(self, person_id: UUID, reference_data: Dict) -> Dict:
        """Validate dasha calculation endpoint"""
        logger.info("Validating /dashas/vimshottari endpoint...")
        
        results = {
            "endpoint": "/dashas/vimshottari",
            "tests": []
        }
        
        try:
            # Call our dasha API
            response = await self.client.get(
                f"{self.base_url}/dashas/vimshottari/{person_id}",
                headers=self.headers
            )
            
            if response.status_code != 200:
                logger.error(f"Dasha calculation failed: {response.text}")
                return results
            
            our_data = response.json()['data']
            
            # Compare dasha order
            if 'mahadasha' in reference_data:
                ref_dasha = reference_data['mahadasha']['response']
                ref_order = ref_dasha.get('mahadasha', [])
                
                our_order = [d['planet'] for d in our_data['maha_dashas']]
                
                # Compare first few dashas (order should match)
                for i in range(min(5, len(ref_order), len(our_order))):
                    ref_planet = ref_order[i]
                    our_planet = our_order[i]
                    
                    passed = ref_planet.lower() == our_planet.lower()
                    
                    test_result = {
                        "test": f"Dasha order position {i+1}",
                        "reference": ref_planet,
                        "calculated": our_planet,
                        "passed": passed
                    }
                    
                    results['tests'].append(test_result)
                    self.results['total_tests'] += 1
                    
                    if passed:
                        self.results['passed'] += 1
                    else:
                        self.results['failed'] += 1
                        logger.warning(f"  Dasha position {i+1}: '{ref_planet}' != '{our_planet}'")
                        
        except Exception as e:
            logger.error(f"Error validating dasha: {e}")
        
        return results
    
    async def run_validation(self):
        """Run validation for all test cases"""
        logger.info("Starting API validation...")
        
        # Load test cases
        test_cases = []
        for test_file in TEST_DATA_DIR.glob("collected_*.json"):
            with open(test_file, 'r') as f:
                test_cases.append(json.load(f))
        
        logger.info(f"Found {len(test_cases)} test cases")
        
        # Validate each test case
        for test_data in test_cases[:3]:  # Limit to 3 for demo
            test_case = test_data['test_case']
            logger.info(f"\nValidating test case: {test_case['name']}")
            
            # Create person
            person_id = await self.create_test_person(test_case)
            if not person_id:
                logger.error(f"Failed to create person for {test_case['name']}")
                continue
            
            # Run validations
            chart_results = await self.validate_chart_calculation(person_id, test_data['data'])
            self.results['endpoint_results'][f"{test_case['name']}_charts"] = chart_results
            
            panchang_results = await self.validate_panchang(person_id, test_data['data'])
            self.results['endpoint_results'][f"{test_case['name']}_panchang"] = panchang_results
            
            dasha_results = await self.validate_dasha(person_id, test_data['data'])
            self.results['endpoint_results'][f"{test_case['name']}_dasha"] = dasha_results
            
            # Clean up - delete test person
            try:
                await self.client.delete(
                    f"{self.base_url}/persons/{person_id}",
                    headers=self.headers
                )
            except:
                pass
        
        # Generate report
        self.generate_report()
    
    def generate_report(self):
        """Generate validation report"""
        accuracy = (self.results['passed'] / self.results['total_tests'] * 100) if self.results['total_tests'] > 0 else 0
        
        report = {
            "validation_date": datetime.utcnow().isoformat(),
            "api_base_url": self.base_url,
            "summary": {
                "total_tests": self.results['total_tests'],
                "passed": self.results['passed'],
                "failed": self.results['failed'],
                "accuracy_percentage": accuracy
            },
            "endpoint_results": self.results['endpoint_results']
        }
        
        # Save report
        report_file = TEST_DATA_DIR / "validation_results" / f"api_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_file.parent.mkdir(exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print("\n" + "="*60)
        print("API VALIDATION SUMMARY")
        print("="*60)
        print(f"Total Tests: {self.results['total_tests']}")
        print(f"Passed: {self.results['passed']}")
        print(f"Failed: {self.results['failed']}")
        print(f"Accuracy: {accuracy:.2f}%")
        print("="*60)
        
        # Show failures
        if self.results['failed'] > 0:
            print("\nFailed Tests:")
            for endpoint_key, endpoint_data in self.results['endpoint_results'].items():
                for test in endpoint_data.get('tests', []):
                    if not test['passed']:
                        print(f"  - {endpoint_key} / {test['test']}")
                        if 'difference' in test:
                            print(f"    Difference: {test['difference']:.4f}")
                        else:
                            print(f"    Expected: '{test['reference']}', Got: '{test['calculated']}'")
        
        print(f"\nFull report saved to: {report_file}")

async def main():
    """Main execution function"""
    validator = APIValidator()
    
    try:
        # Check if test data exists
        if not TEST_DATA_DIR.exists():
            logger.error("Test data not found! Please run collect_vedicastro_test_data.py first.")
            return
        
        # Check if API is running
        try:
            response = await validator.client.get(f"{OUR_API_BASE}/health")
            if response.status_code != 200:
                logger.error("API is not responding. Please start the API server first.")
                return
        except:
            logger.error("Cannot connect to API. Please ensure the server is running on http://localhost:8000")
            return
        
        # Run validation
        await validator.run_validation()
        
    finally:
        await validator.close()

if __name__ == "__main__":
    print("=== Astrow API Validation ===")
    print("This script validates our API endpoints against VedicAstroAPI reference data")
    print("\nPrerequisites:")
    print("1. Run collect_vedicastro_test_data.py to fetch reference data")
    print("2. Start the API server: uvicorn josi.main:app --reload")
    print("3. Update API_KEY in this script")
    print("\nStarting validation...\n")
    
    asyncio.run(main())