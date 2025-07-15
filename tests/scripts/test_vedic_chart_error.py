#!/usr/bin/env python3
"""
Simple script to test and identify the Vedic chart calculation error.
"""

import httpx
import asyncio
import json

async def test_vedic_chart_error():
    """Test Vedic chart calculation to identify the exact error."""
    
    # API configuration
    base_url = "http://localhost:8000"
    headers = {"X-API-Key": "test-api-key"}
    
    async with httpx.AsyncClient() as client:
        # Step 1: Create a test person
        person_data = {
            "name": "Vedic Test Person",
            "date_of_birth": "1990-01-15", 
            "time_of_birth": "10:30:00",
            "place_of_birth": "New Delhi, India"
        }
        
        print("Creating test person...")
        response = await client.post(
            f"{base_url}/api/v1/persons/",
            json=person_data,
            headers=headers
        )
        
        if response.status_code != 200:
            print(f"Failed to create person: {response.status_code}")
            print(response.text)
            return
            
        person = response.json()["data"]
        person_id = person["person_id"]
        print(f"Created person: {person_id}")
        
        # Step 2: Try to calculate Vedic chart
        print("\nCalculating Vedic chart...")
        params = {
            "person_id": person_id,
            "systems": ["vedic"],
            "ayanamsa": "lahiri",
            "house_system": "whole_sign"
        }
        
        response = await client.post(
            f"{base_url}/api/v1/charts/calculate",
            params=params,
            headers=headers
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data["success"]:
                print("✅ Vedic chart calculated successfully!")
                print(json.dumps(data["data"]["charts"]["vedic"]["chart_data"], indent=2))
            else:
                print("❌ Calculation failed:")
                print(data.get("message", "Unknown error"))
        else:
            print("❌ API Error:")
            print(response.text)
            
            # Try to parse error details
            try:
                error_data = response.json()
                if "detail" in error_data:
                    print(f"\nError detail: {error_data['detail']}")
            except:
                pass
        
        # Step 3: For comparison, calculate Western chart
        print("\n\nFor comparison, calculating Western chart...")
        params["systems"] = ["western"]
        
        response = await client.post(
            f"{base_url}/api/v1/charts/calculate",
            params=params,
            headers=headers
        )
        
        if response.status_code == 200:
            print("✅ Western chart calculated successfully")
        else:
            print(f"❌ Western chart also failed: {response.status_code}")
            
        # Cleanup
        print(f"\nCleaning up: deleting person {person_id}")
        await client.delete(
            f"{base_url}/api/v1/persons/{person_id}",
            headers=headers
        )

if __name__ == "__main__":
    asyncio.run(test_vedic_chart_error())