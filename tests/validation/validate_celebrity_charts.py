#!/usr/bin/env python3
"""
Standalone script to validate celebrity chart calculations.

This script can be run independently to test the Josi API with celebrity data.
"""

import asyncio
import httpx
from datetime import datetime
from typing import Dict, Any, List
import json
from pathlib import Path
import sys

# Add parent directory to path to import from tests
sys.path.append(str(Path(__file__).parent.parent))

from tests.fixtures.celebrity_birth_data import get_celebrity_test_data, get_test_payload


class CelebrityChartValidator:
    """Validate celebrity charts against the Josi API."""
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: str = "test-api-key"):
        self.base_url = base_url
        self.headers = {"X-API-Key": api_key}
        self.results = []
    
    async def create_person(self, celebrity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a person via the API."""
        async with httpx.AsyncClient() as client:
            payload = get_test_payload(celebrity_data)
            response = await client.post(
                f"{self.base_url}/api/v1/persons/",
                json=payload,
                headers=self.headers,
                timeout=30.0,
                follow_redirects=True
            )
            
            if response.status_code not in [200, 201]:
                print(f"❌ Failed to create person {celebrity_data['name']}")
                print(f"   Status code: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
            
            data = response.json()
            return data["data"]
    
    async def calculate_chart(self, person_id: str, chart_type: str = "western") -> Dict[str, Any]:
        """Calculate a chart for a person."""
        async with httpx.AsyncClient() as client:
            # Use query parameters as expected by the API
            params = {
                "person_id": person_id,
                "systems": [chart_type],
                "house_system": "placidus",
                "ayanamsa": "lahiri"
            }
            
            response = await client.post(
                f"{self.base_url}/api/v1/charts/calculate",
                params=params,
                headers=self.headers,
                timeout=30.0,
                follow_redirects=True
            )
            
            if response.status_code not in [200, 201]:
                print(f"❌ Failed to calculate {chart_type} chart")
                print(f"   Status: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
            
            data = response.json()
            # Debug: print what we received
            if "data" in data:
                print(f"   ✓ Chart response received with keys: {list(data['data'].keys())}")
            return data.get("data", data)
    
    async def validate_celebrity(self, celebrity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a single celebrity's chart."""
        print(f"\n📊 Processing: {celebrity_data['name']}")
        print(f"   Born: {celebrity_data['birth_date']} at {celebrity_data['birth_time']}")
        print(f"   Location: {celebrity_data['birth_place']}")
        print(f"   Rating: {celebrity_data['rating']} - {celebrity_data['source']}")
        
        result = {
            "name": celebrity_data["name"],
            "success": False,
            "person_id": None,
            "charts": {},
            "errors": []
        }
        
        try:
            # Create person
            person = await self.create_person(celebrity_data)
            if not person:
                result["errors"].append("Failed to create person")
                return result
            
            result["person_id"] = person["person_id"]
            print(f"   ✓ Person created: {person['person_id']}")
            
            # Calculate Western chart
            western_response = await self.calculate_chart(person["person_id"], "western")
            if western_response:
                # The response contains 'charts' array
                if "charts" in western_response and len(western_response["charts"]) > 0:
                    western_chart = western_response["charts"][0]
                    result["charts"]["western"] = western_chart
                    
                    try:
                        positions = western_chart["chart_data"]["planets"]
                        sun = positions.get("Sun", {})
                        moon = positions.get("Moon", {})
                        houses = western_chart["chart_data"].get("houses", [])
                        ascendant_degree = houses[0] if houses else 0
                        
                        print(f"   ✓ Western chart calculated:")
                        print(f"     Sun: {sun.get('sign', 'Unknown')} {sun.get('longitude', 0):.2f}°")
                        print(f"     Moon: {moon.get('sign', 'Unknown')} {moon.get('longitude', 0):.2f}°")
                        print(f"     Ascendant: {ascendant_degree:.2f}°")
                    except (KeyError, IndexError) as e:
                        print(f"   ⚠️  Chart structure issue: {e}")
                        result["errors"].append(f"Chart structure: {e}")
                else:
                    print(f"   ⚠️  No charts in response")
                    result["errors"].append("No charts in response")
                
                    # Validate expected positions if provided
                    if "expected_sun_sign" in celebrity_data and "Sun" in positions:
                        sun_sign = positions["Sun"].get("sign", "").lower()
                        if sun_sign == celebrity_data["expected_sun_sign"].lower():
                            print(f"     ✅ Sun sign matches expected: {celebrity_data['expected_sun_sign']}")
                        else:
                            print(f"     ⚠️  Sun sign mismatch: expected {celebrity_data['expected_sun_sign']}, got {sun_sign}")
                            result["errors"].append(f"Sun sign mismatch")
            
            # Calculate Vedic chart
            vedic_response = await self.calculate_chart(person["person_id"], "vedic")
            if vedic_response:
                if "charts" in vedic_response and len(vedic_response["charts"]) > 0:
                    vedic_chart = vedic_response["charts"][0]
                    result["charts"]["vedic"] = vedic_chart
                    print(f"   ✓ Vedic chart calculated")
                    print(f"     Ayanamsa: {vedic_chart.get('ayanamsa', 'N/A')}")
                else:
                    print(f"   ⚠️  No Vedic charts in response")
                    result["errors"].append("No Vedic charts in response")
            
            result["success"] = len(result["errors"]) == 0
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            result["errors"].append(str(e))
        
        return result
    
    async def validate_all_celebrities(self):
        """Validate all celebrities in the test data."""
        celebrities = get_celebrity_test_data()
        print(f"\n🌟 Validating {len(celebrities)} Celebrity Charts 🌟")
        print("=" * 60)
        
        for celebrity in celebrities:
            result = await self.validate_celebrity(celebrity)
            self.results.append(result)
        
        self.print_summary()
    
    def print_summary(self):
        """Print validation summary."""
        print("\n" + "=" * 60)
        print("VALIDATION SUMMARY")
        print("=" * 60)
        
        total = len(self.results)
        successful = sum(1 for r in self.results if r["success"])
        
        print(f"\nTotal celebrities tested: {total}")
        print(f"Successful validations: {successful}")
        print(f"Failed validations: {total - successful}")
        
        if total > 0:
            print(f"Success rate: {(successful/total)*100:.1f}%")
        
        # Show failures
        failures = [r for r in self.results if not r["success"]]
        if failures:
            print("\n⚠️  Failed Validations:")
            for failure in failures:
                print(f"  - {failure['name']}: {', '.join(failure['errors'])}")
        
        # Save results to file
        output_path = Path("celebrity_validation_results.json")
        with open(output_path, "w") as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"\nDetailed results saved to: {output_path}")


async def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate celebrity charts against Josi API")
    parser.add_argument("--url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--api-key", default="test-api-key", help="API key")
    parser.add_argument("--celebrity", help="Test specific celebrity by name")
    
    args = parser.parse_args()
    
    validator = CelebrityChartValidator(base_url=args.url, api_key=args.api_key)
    
    if args.celebrity:
        # Test specific celebrity
        celebrities = get_celebrity_test_data()
        celebrity = next((c for c in celebrities if c["name"].lower() == args.celebrity.lower()), None)
        
        if not celebrity:
            print(f"Celebrity '{args.celebrity}' not found in test data")
            print("\nAvailable celebrities:")
            for c in celebrities:
                print(f"  - {c['name']}")
            return
        
        result = await validator.validate_celebrity(celebrity)
        print(f"\n{'✅ Validation passed' if result['success'] else '❌ Validation failed'}")
    else:
        # Test all celebrities
        await validator.validate_all_celebrities()


if __name__ == "__main__":
    asyncio.run(main())