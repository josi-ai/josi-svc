#!/usr/bin/env python3
"""
Test all persons including Archana M with local calculations.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from src.josi.services.astrology_service import AstrologyCalculator

# Complete test persons data including Archana
ALL_TEST_PERSONS = [
    {
        "name": "Archana M",
        "gender": "female",
        "date_of_birth": "1998-12-07",
        "time_of_birth": "21:15:00",
        "place_of_birth": "Chennai, Tamil Nadu, India",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "timezone": "Asia/Kolkata"
    },
    {
        "name": "Valarmathi Kannappan",
        "gender": "female",
        "date_of_birth": "1961-02-11",
        "time_of_birth": "15:30:00",
        "place_of_birth": "Kovur, Tamil Nadu, India",
        "latitude": 13.1622,
        "longitude": 80.005,
        "timezone": "Asia/Kolkata"
    },
    {
        "name": "Janaki Panneerselvam",
        "gender": "female",
        "date_of_birth": "1982-12-18",
        "time_of_birth": "10:10:00",
        "place_of_birth": "Chennai, Tamil Nadu, India",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "timezone": "Asia/Kolkata"
    },
    {
        "name": "Govindarajan Panneerselvam",
        "gender": "male",
        "date_of_birth": "1989-12-29",
        "time_of_birth": "12:12:00",
        "place_of_birth": "Chennai, Tamil Nadu, India",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "timezone": "Asia/Kolkata"
    },
    {
        "name": "Panneerselvam Chandrasekaran",
        "gender": "male",
        "date_of_birth": "1954-08-20",
        "time_of_birth": "18:20:00",
        "place_of_birth": "Kanchipuram, Tamil Nadu, India",
        "latitude": 12.8185,
        "longitude": 79.6947,
        "timezone": "Asia/Kolkata"
    }
]

def calculate_chart(person: dict) -> dict:
    """Calculate chart for a person."""
    calc = AstrologyCalculator()
    
    # Parse datetime
    dob_parts = person['date_of_birth'].split('-')
    tob_parts = person['time_of_birth'].split(':')
    
    dt = datetime(
        int(dob_parts[0]),  # year
        int(dob_parts[1]),  # month
        int(dob_parts[2]),  # day
        int(tob_parts[0]),  # hour
        int(tob_parts[1]),  # minute
        int(tob_parts[2])   # second
    )
    
    # Calculate chart
    chart = calc.calculate_vedic_chart(
        dt=dt,
        latitude=person['latitude'],
        longitude=person['longitude'],
        timezone=person['timezone'],
        house_system='placidus'
    )
    
    return chart

def display_chart_summary(person: dict, chart: dict):
    """Display chart summary for a person."""
    print(f"\n{'='*80}")
    print(f"Chart for: {person['name']} ({person['gender']})")
    print(f"{'='*80}")
    print(f"Date of Birth: {person['date_of_birth']}")
    print(f"Time of Birth: {person['time_of_birth']}")
    print(f"Place: {person['place_of_birth']}")
    print(f"Coordinates: {person['latitude']}, {person['longitude']}")
    
    print(f"\n{'Planet/Point':<15} {'Longitude':>12} {'Sign':<12} {'House':>6} {'Nakshatra':<15}")
    print(f"{'-'*15} {'-'*12} {'-'*12} {'-'*6} {'-'*15}")
    
    # Ascendant
    asc = chart['ascendant']
    print(f"{'Ascendant':<15} {asc['longitude']:>12.6f} {asc['sign']:<12} {1:>6} {asc['nakshatra']:<15}")
    
    # Planets
    planet_order = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']
    for planet_name in planet_order:
        if planet_name in chart['planets']:
            planet = chart['planets'][planet_name]
            print(f"{planet_name:<15} {planet['longitude']:>12.6f} {planet['sign']:<12} "
                  f"{planet['house']:>6} {planet['nakshatra']:<15}")
    
    # Check retrograde planets
    retrograde = []
    for planet_name, planet_data in chart['planets'].items():
        if planet_data.get('speed', 0) < 0 and planet_name not in ['Rahu', 'Ketu']:
            retrograde.append(planet_name)
    
    if retrograde:
        print(f"\nRetrograde Planets: {', '.join(retrograde)}")
    
    print(f"\nAyanamsa: {chart['ayanamsa_name']} = {chart['ayanamsa']:.6f}°")
    print(f"House System: {chart['house_system']}")

def main():
    """Run calculations for all persons."""
    print("Vedic Astrology Calculations for All Test Persons")
    print("=" * 80)
    
    for person in ALL_TEST_PERSONS:
        try:
            chart = calculate_chart(person)
            display_chart_summary(person, chart)
        except Exception as e:
            print(f"\nError calculating chart for {person['name']}: {e}")
    
    print(f"\n{'='*80}")
    print("All calculations completed")

if __name__ == "__main__":
    main()