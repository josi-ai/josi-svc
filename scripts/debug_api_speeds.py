#!/usr/bin/env python3
"""
Debug script to test API speed calculation directly
"""
import requests
import json

# Test person data
person_data = {
    "name": "Test Person",
    "date_of_birth": "1998-12-07",
    "time_of_birth": "21:15",
    "place_of_birth": "Chennai",
    "timezone": "Asia/Kolkata",
    "latitude": 13.0827,
    "longitude": 80.2707,
    "gender": "female"
}

# Create person
print("Creating person...")
headers = {"X-API-Key": "test-api-key"}
person_response = requests.post("http://localhost:8000/api/v1/persons/", json=person_data, headers=headers)
print(f"Person response status: {person_response.status_code}")

if person_response.status_code == 200:
    person_id = person_response.json()["data"]["person_id"]
    print(f"Person ID: {person_id}")
    
    # Calculate chart
    print("\nCalculating chart...")
    chart_response = requests.post(
        f"http://localhost:8000/api/v1/charts/calculate",
        params={
            "person_id": person_id,
            "systems": "vedic", 
            "house_system": "placidus",
            "ayanamsa": "lahiri"
        },
        headers=headers
    )
    
    print(f"Chart response status: {chart_response.status_code}")
    
    if chart_response.status_code == 200:
        chart_data = chart_response.json()["data"][0]
        planets = chart_data["chart_data"]["planets"]
        
        print("\n=== PLANET SPEEDS FROM API ===")
        for planet_name, planet_data in planets.items():
            speed = planet_data.get("speed", "NOT_FOUND")
            print(f"{planet_name}: speed = {speed}")
        
        # Pretty print the full chart data
        print("\n=== FULL CHART DATA ===")
        print(json.dumps(chart_data, indent=2, default=str))
    else:
        print(f"Chart calculation failed: {chart_response.text}")
else:
    print(f"Person creation failed: {person_response.text}")