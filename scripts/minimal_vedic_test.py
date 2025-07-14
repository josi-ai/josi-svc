#!/usr/bin/env python3
"""
Minimal test to reproduce the Vedic chart error.
"""

import httpx
import asyncio
import json

async def minimal_vedic_test():
    """Minimal test to reproduce the error."""
    
    base_url = "http://localhost:8000"
    headers = {"X-API-Key": "test-api-key"}
    
    async with httpx.AsyncClient() as client:
        # Use the first person from celebrity data
        person_id = "f2303d9c-0bc9-4b18-b17e-9cf4b7bd5f9f"  # From previous test run
        
        print("Testing chart calculations for existing person...")
        
        # Test 1: Western chart (should work)
        print("\n1. Western Chart:")
        params = {
            "person_id": person_id,
            "systems": ["western"],
            "house_system": "placidus"
        }
        
        response = await client.post(
            f"{base_url}/api/v1/charts/calculate",
            params=params,
            headers=headers
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   Error: {response.text}")
        else:
            print("   ✅ Success")
        
        # Test 2: Vedic chart WITHOUT ayanamsa parameter
        print("\n2. Vedic Chart (no ayanamsa param):")
        params = {
            "person_id": person_id,
            "systems": ["vedic"],
            "house_system": "whole_sign"
            # NO ayanamsa parameter
        }
        
        response = await client.post(
            f"{base_url}/api/v1/charts/calculate",
            params=params,
            headers=headers
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   Error: {response.text}")
        else:
            print("   ✅ Success")
        
        # Test 3: Vedic chart WITH ayanamsa parameter
        print("\n3. Vedic Chart (with ayanamsa):")
        params = {
            "person_id": person_id,
            "systems": ["vedic"],
            "house_system": "whole_sign",
            "ayanamsa": "lahiri"  # This might be the issue
        }
        
        response = await client.post(
            f"{base_url}/api/v1/charts/calculate",
            params=params,
            headers=headers
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code != 200:
            error_text = response.text
            print(f"   Error: {error_text}")
            
            # Parse error to see SQL
            try:
                error_data = json.loads(error_text)
                if "detail" in error_data:
                    detail = error_data["detail"]
                    if "SQL:" in detail:
                        sql_start = detail.find("SQL:") + 5
                        sql_end = detail.find("]", sql_start)
                        sql = detail[sql_start:sql_end]
                        print(f"\n   SQL: {sql}")
            except:
                pass
        else:
            print("   ✅ Success")
        
        # Test 4: Try different ayanamsa values
        print("\n4. Testing different ayanamsa values:")
        for ayanamsa in ["lahiri", "krishnamurti", "raman"]:
            params = {
                "person_id": person_id,
                "systems": ["vedic"],
                "house_system": "whole_sign",
                "ayanamsa": ayanamsa
            }
            
            response = await client.post(
                f"{base_url}/api/v1/charts/calculate",
                params=params,
                headers=headers
            )
            
            print(f"   {ayanamsa}: {response.status_code}")

if __name__ == "__main__":
    asyncio.run(minimal_vedic_test())