#!/usr/bin/env python3
import httpx
import json

# Create Archana M
person_data = {
    "name": "Archana M",
    "gender": "female",
    "date_of_birth": "1998-12-07",
    "time_of_birth": "21:15:00",
    "place_of_birth": "Chennai, Tamil Nadu, India",
    "latitude": 13.0827,
    "longitude": 80.2707,
    "timezone": "Asia/Kolkata"
}

# Create person
client = httpx.Client()
response = client.post(
    "http://localhost:8000/api/v1/persons/",
    json=person_data,
    headers={"X-API-Key": "test-api-key"}
)

print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    person_id = data['data']['person_id']
    print(f"Created person: {person_id}")
    
    # Calculate chart
    chart_response = client.post(
        "http://localhost:8000/api/v1/charts/calculate/",
        params={
            "person_id": person_id,
            "systems": "vedic",
            "house_system": "placidus",
            "ayanamsa": "lahiri"
        },
        headers={"X-API-Key": "test-api-key"}
    )
    
    print(f"Chart calculation status: {chart_response.status_code}")
    if chart_response.status_code == 200:
        chart_data = chart_response.json()
        print(json.dumps(chart_data['data'][0]['planet_positions'], indent=2))
else:
    print(f"Error: {response.text}")

client.close()