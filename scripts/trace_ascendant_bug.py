#!/usr/bin/env python3
"""
Trace where the ascendant value gets corrupted from 318.05° to 176.51°
"""

import asyncio
from datetime import datetime
import pytz
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from uuid import uuid4

# Add the src directory to the path
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from josi.services.astrology_service import AstrologyCalculator
from josi.services.chart_service import ChartService
from josi.models.person_model import Person
from josi.models.chart_model import AstrologySystem, HouseSystem, Ayanamsa

# Barack Obama's birth data
OBAMA_DATA = {
    "name": "Barack Obama",
    "date": "1961-08-04",
    "time": "19:24:00",
    "lat": 21.3099,
    "lon": -157.8581,
    "timezone": "Pacific/Honolulu"
}

def create_test_person():
    """Create a test person object with Obama's data"""
    tz = pytz.timezone(OBAMA_DATA["timezone"])
    birth_dt = tz.localize(datetime.strptime(
        f"{OBAMA_DATA['date']} {OBAMA_DATA['time']}", 
        "%Y-%m-%d %H:%M:%S"
    ))
    
    return Person(
        person_id=uuid4(),
        organization_id=uuid4(),
        first_name="Barack",
        last_name="Obama",
        date_of_birth=birth_dt.date(),
        time_of_birth=birth_dt,
        latitude=OBAMA_DATA["lat"],
        longitude=OBAMA_DATA["lon"],
        timezone=OBAMA_DATA["timezone"],
        place_of_birth="Honolulu, Hawaii"
    )

async def test_astrology_calculator():
    """Test the raw astrology calculator"""
    print("=" * 80)
    print("TESTING ASTROLOGY CALCULATOR DIRECTLY")
    print("=" * 80)
    
    calculator = AstrologyCalculator()
    person = create_test_person()
    
    # Test Western calculation
    print("\nWestern Chart Calculation:")
    western_chart = calculator.calculate_western_chart(
        person.time_of_birth,
        person.latitude,
        person.longitude
    )
    
    asc_data = western_chart.get("ascendant", {})
    print(f"  Ascendant longitude: {asc_data.get('longitude', 'N/A')}°")
    print(f"  Ascendant sign: {asc_data.get('sign', 'N/A')}")
    print(f"  Houses: {western_chart.get('houses', [])[:3]}...")  # First 3 houses
    
    # Test Vedic calculation
    print("\nVedic Chart Calculation:")
    vedic_chart = calculator.calculate_vedic_chart(
        person.time_of_birth,
        person.latitude,
        person.longitude
    )
    
    asc_data = vedic_chart.get("ascendant", {})
    print(f"  Ascendant longitude: {asc_data.get('longitude', 'N/A')}°")
    print(f"  Ascendant sign: {asc_data.get('sign', 'N/A')}")
    print(f"  Ayanamsa: {vedic_chart.get('ayanamsa', 'N/A')}°")
    print(f"  Houses: {vedic_chart.get('houses', [])[:3]}...")  # First 3 houses
    
    return western_chart, vedic_chart

async def test_chart_service():
    """Test the chart service layer"""
    print("\n" + "=" * 80)
    print("TESTING CHART SERVICE")
    print("=" * 80)
    
    # Create a mock database session
    # For this test, we'll use a simplified approach
    org_id = uuid4()
    person = create_test_person()
    person.organization_id = org_id
    
    # Create chart service without actual database
    # We'll modify to test just the calculation methods
    from josi.services.chart_service import ChartService
    
    # Mock the chart service with minimal setup
    class MockSession:
        async def commit(self):
            pass
        def add(self, obj):
            pass
    
    mock_db = MockSession()
    chart_service = ChartService(mock_db, org_id)
    
    # Test Western chart calculation
    print("\nTesting _calculate_western_chart:")
    try:
        chart_data = await chart_service._calculate_western_chart(
            person, HouseSystem.PLACIDUS
        )
        
        asc_data = chart_data.get("ascendant", {})
        print(f"  Ascendant longitude: {asc_data.get('longitude', 'N/A')}°")
        print(f"  Ascendant sign: {asc_data.get('sign', 'N/A')}")
        
        # Check if progressions are affecting the natal chart
        if "current_progressions" in chart_data:
            prog_data = chart_data["current_progressions"]
            if prog_data and "progressed_angles" in prog_data:
                print(f"  Progressed ASC: {prog_data['progressed_angles'].get('ASC', 'N/A')}°")
        
    except Exception as e:
        print(f"  Error: {e}")
    
    # Test Vedic chart calculation
    print("\nTesting _calculate_vedic_chart:")
    try:
        chart_data = await chart_service._calculate_vedic_chart(
            person, HouseSystem.PLACIDUS, Ayanamsa.LAHIRI
        )
        
        asc_data = chart_data.get("ascendant", {})
        print(f"  Ascendant longitude: {asc_data.get('longitude', 'N/A')}°")
        print(f"  Ascendant sign: {asc_data.get('sign', 'N/A')}")
        print(f"  Ayanamsa: {chart_data.get('ayanamsa', 'N/A')}°")
        
    except Exception as e:
        print(f"  Error: {e}")

async def check_specific_calculation():
    """Check if 176.51 comes from a specific calculation"""
    print("\n" + "=" * 80)
    print("CHECKING SPECIFIC CALCULATIONS")
    print("=" * 80)
    
    import swisseph as swe
    person = create_test_person()
    
    # Get Julian day
    utc_dt = person.time_of_birth.astimezone(pytz.UTC)
    jd = swe.julday(
        utc_dt.year, utc_dt.month, utc_dt.day,
        utc_dt.hour + utc_dt.minute/60.0 + utc_dt.second/3600.0
    )
    
    # Get houses
    houses, ascmc = swe.houses(jd, person.latitude, person.longitude, b'P')
    raw_asc = houses[0]
    print(f"\nRaw ASC from pyswisseph: {raw_asc:.2f}°")
    
    # Check various calculations that might produce 176.51
    print("\nChecking calculations that produce 176.51:")
    
    # The difference is 141.54
    diff = raw_asc - 176.51
    print(f"  Difference: {diff:.2f}°")
    
    # Check if it's related to ARMC or other angles
    print(f"  ARMC: {ascmc[2]:.2f}°")
    print(f"  Vertex: {ascmc[3]:.2f}°")
    print(f"  Raw ASC - ARMC/2: {(raw_asc - ascmc[2]/2):.2f}°")
    print(f"  Raw ASC - Vertex: {(raw_asc - ascmc[3]):.2f}°")
    
    # Check if it's related to house 7 (descendant)
    desc = (raw_asc + 180) % 360
    print(f"  Descendant: {desc:.2f}°")
    print(f"  Raw ASC - Descendant: {(raw_asc - desc):.2f}°")
    
    # Check if progressions are involved
    print("\nChecking if progressions affect natal chart:")
    from josi.services.western.progressions_service import ProgressionCalculator
    prog_calc = ProgressionCalculator()
    
    try:
        prog_data = prog_calc.calculate_secondary_progressions(
            person.time_of_birth,
            datetime.now(),
            person.latitude,
            person.longitude
        )
        prog_asc = prog_data.get("progressed_angles", {}).get("ASC")
        print(f"  Progressed ASC: {prog_asc:.2f}°")
        print(f"  Raw ASC - Prog ASC: {(raw_asc - prog_asc):.2f}°")
    except Exception as e:
        print(f"  Error calculating progressions: {e}")

async def main():
    """Run all tests"""
    await test_astrology_calculator()
    await test_chart_service()
    await check_specific_calculation()
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("The ascendant value changes from 318.05° to 176.51° somewhere in the code.")
    print("The difference is exactly 141.54°")
    print("This needs to be traced through the actual API call stack.")

if __name__ == "__main__":
    asyncio.run(main())