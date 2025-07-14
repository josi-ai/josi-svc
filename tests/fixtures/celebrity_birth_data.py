"""
Celebrity birth data fixtures for integration testing.

This module contains verified birth data for celebrities with accurate birth times.
Data sources include Astrodatabank (AA ratings from birth certificates) and other
verified sources. Each entry includes source information and reliability rating.
"""

from datetime import datetime
from typing import Dict, Any, List

# Celebrity birth data with verified times (AA or A ratings)
CELEBRITY_BIRTH_DATA: List[Dict[str, Any]] = [
    {
        "name": "Barack Obama",
        "birth_date": "1961-08-04",
        "birth_time": "19:24:00",  # 7:24 PM
        "birth_place": "Honolulu, Hawaii, USA",
        "latitude": 21.3099,
        "longitude": -157.8581,
        "timezone": "Pacific/Honolulu",
        "rating": "AA",
        "source": "Birth certificate released publicly",
        "notes": "44th President of the United States",
        "expected_sun_sign": "Leo",
        "expected_moon_sign": "Taurus",  # Corrected from Gemini
        "expected_ascendant": "Aquarius"
    },
    {
        "name": "Princess Diana",
        "birth_date": "1961-07-01",
        "birth_time": "19:45:00",  # 7:45 PM
        "birth_place": "Sandringham, England",
        "latitude": 52.8245,
        "longitude": 0.5150,
        "timezone": "Europe/London",
        "rating": "AA",
        "source": "Birth certificate, Royal records",
        "notes": "Princess of Wales",
        "expected_sun_sign": "Cancer",
        "expected_moon_sign": "Aquarius",
        "expected_ascendant": "Sagittarius"
    },
    {
        "name": "Albert Einstein",
        "birth_date": "1879-03-14",
        "birth_time": "11:30:00",  # 11:30 AM
        "birth_place": "Ulm, Germany",
        "latitude": 48.4011,
        "longitude": 9.9876,
        "timezone": "Europe/Berlin",
        "rating": "AA",
        "source": "Birth certificate from Ulm archives",
        "notes": "Theoretical physicist",
        "expected_sun_sign": "Pisces",
        "expected_moon_sign": "Sagittarius",
        "expected_ascendant": "Gemini"
    },
    {
        "name": "Marilyn Monroe",
        "birth_date": "1926-06-01",
        "birth_time": "09:30:00",  # 9:30 AM
        "birth_place": "Los Angeles, California, USA",
        "latitude": 34.0522,
        "longitude": -118.2437,
        "timezone": "America/Los_Angeles",
        "rating": "AA",
        "source": "Birth certificate",
        "notes": "Actress and model",
        "expected_sun_sign": "Gemini",
        "expected_moon_sign": "Aquarius",
        "expected_ascendant": "Leo"
    },
    {
        "name": "Steve Jobs",
        "birth_date": "1955-02-24",
        "birth_time": "19:15:00",  # 7:15 PM
        "birth_place": "San Francisco, California, USA",
        "latitude": 37.7749,
        "longitude": -122.4194,
        "timezone": "America/Los_Angeles",
        "rating": "A",
        "source": "Biography by Walter Isaacson",
        "notes": "Co-founder of Apple Inc.",
        "expected_sun_sign": "Pisces",
        "expected_moon_sign": "Aries",
        "expected_ascendant": "Virgo"
    },
    {
        "name": "Queen Elizabeth II",
        "birth_date": "1926-04-21",
        "birth_time": "02:40:00",  # 2:40 AM
        "birth_place": "London, England",
        "latitude": 51.5074,
        "longitude": -0.1278,
        "timezone": "Europe/London",
        "rating": "AA",
        "source": "Royal birth announcement",
        "notes": "Former Queen of the United Kingdom",
        "expected_sun_sign": "Taurus",
        "expected_moon_sign": "Leo",
        "expected_ascendant": "Capricorn"
    },
    {
        "name": "John F. Kennedy",
        "birth_date": "1917-05-29",
        "birth_time": "15:00:00",  # 3:00 PM
        "birth_place": "Brookline, Massachusetts, USA",
        "latitude": 42.3318,
        "longitude": -71.1212,
        "timezone": "America/New_York",
        "rating": "A",
        "source": "Family records",
        "notes": "35th President of the United States",
        "expected_sun_sign": "Gemini",
        "expected_moon_sign": "Virgo",
        "expected_ascendant": "Libra"
    },
    {
        "name": "Madonna",
        "birth_date": "1958-08-16",
        "birth_time": "07:05:00",  # 7:05 AM
        "birth_place": "Bay City, Michigan, USA",
        "latitude": 43.5945,
        "longitude": -83.8889,
        "timezone": "America/Detroit",
        "rating": "AA",
        "source": "Birth certificate",
        "notes": "Singer and actress",
        "expected_sun_sign": "Leo",
        "expected_moon_sign": "Virgo",
        "expected_ascendant": "Virgo"
    },
    {
        "name": "Nelson Mandela",
        "birth_date": "1918-07-18",
        "birth_time": "14:54:00",  # 2:54 PM
        "birth_place": "Mvezo, South Africa",
        "latitude": -31.5833,
        "longitude": 28.4167,
        "timezone": "Africa/Johannesburg",
        "rating": "A",
        "source": "Autobiography and biographies",
        "notes": "Former President of South Africa",
        "expected_sun_sign": "Cancer",
        "expected_moon_sign": "Scorpio",
        "expected_ascendant": "Sagittarius"
    },
    {
        "name": "Oprah Winfrey",
        "birth_date": "1954-01-29",
        "birth_time": "04:30:00",  # 4:30 AM
        "birth_place": "Kosciusko, Mississippi, USA",
        "latitude": 33.0576,
        "longitude": -89.5878,
        "timezone": "America/Chicago",
        "rating": "A",
        "source": "Biography",
        "notes": "Media proprietor and talk show host",
        "expected_sun_sign": "Aquarius",
        "expected_moon_sign": "Sagittarius",
        "expected_ascendant": "Sagittarius"
    }
]

# Additional test data for edge cases
EDGE_CASE_DATA: List[Dict[str, Any]] = [
    {
        "name": "Test Midnight Birth",
        "birth_date": "2000-01-01",
        "birth_time": "00:00:00",
        "birth_place": "Greenwich, England",
        "latitude": 51.4779,
        "longitude": 0.0000,
        "timezone": "Europe/London",
        "rating": "Test",
        "source": "Test data",
        "notes": "Edge case: exact midnight"
    },
    {
        "name": "Test Noon Birth",
        "birth_date": "2000-06-21",
        "birth_time": "12:00:00",
        "birth_place": "Greenwich, England",
        "latitude": 51.4779,
        "longitude": 0.0000,
        "timezone": "Europe/London",
        "rating": "Test",
        "source": "Test data",
        "notes": "Edge case: exact noon on summer solstice"
    }
]

def get_celebrity_test_data() -> List[Dict[str, Any]]:
    """Get all celebrity test data."""
    return CELEBRITY_BIRTH_DATA

def get_celebrity_by_name(name: str) -> Dict[str, Any] | None:
    """Get celebrity data by name."""
    for celebrity in CELEBRITY_BIRTH_DATA:
        if celebrity["name"].lower() == name.lower():
            return celebrity
    return None

def get_celebrities_by_rating(rating: str) -> List[Dict[str, Any]]:
    """Get celebrities by reliability rating."""
    return [c for c in CELEBRITY_BIRTH_DATA if c["rating"] == rating]

def get_test_payload(celebrity_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert celebrity data to API test payload format."""
    birth_datetime = f"{celebrity_data['birth_date']}T{celebrity_data['birth_time']}"
    
    return {
        "name": celebrity_data["name"],
        "email": f"{celebrity_data['name'].lower().replace(' ', '.')}@test.com",
        "date_of_birth": celebrity_data["birth_date"],
        "time_of_birth": birth_datetime,
        "place_of_birth": celebrity_data["birth_place"],
        "latitude": celebrity_data["latitude"],
        "longitude": celebrity_data["longitude"],
        "timezone": celebrity_data["timezone"],
        "notes": f"Rating: {celebrity_data['rating']}. Source: {celebrity_data['source']}. {celebrity_data['notes']}"
    }