#!/usr/bin/env python3
"""
Trace the Vedic chart error by examining the chart data structure.
"""

import sys
sys.path.append('/Users/govind/Developer/astrow/src')

from datetime import datetime
from josi.models.chart_model import AstrologySystem, HouseSystem, Ayanamsa

# Simulate what the chart service is trying to create
def trace_chart_dict():
    """Trace the chart dictionary that causes the error."""
    
    # This is what the chart service creates (from line 75-90)
    chart_dict = {
        "person_id": "e7132b4f-bf01-4ac6-bb84-6e56fa442e48",  # Example UUID
        "chart_type": AstrologySystem.VEDIC.value,
        "house_system": HouseSystem.WHOLE_SIGN.value,
        "ayanamsa": Ayanamsa.LAHIRI.value,
        "calculated_at": datetime.utcnow(),
        "calculation_version": "2.0",
        "chart_data": {
            "chart_type": "vedic",
            "ayanamsa": 24.1234,
            "ascendant": {"longitude": 123.45},
            "planets": {"Sun": {"longitude": 100}},
            "houses": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        },
        "planet_positions": {"Sun": {"longitude": 100}},
        "house_cusps": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        "aspects": []
    }
    
    print("Chart dictionary being created:")
    for key, value in chart_dict.items():
        print(f"  {key}: {type(value).__name__} = {value if not isinstance(value, (dict, list)) else '...'}")
    
    # Count the fields
    print(f"\nTotal fields: {len(chart_dict)}")
    
    # Check AstrologyChart model fields
    print("\nExpected AstrologyChart fields from model:")
    print("  - chart_id (auto-generated)")
    print("  - person_id")
    print("  - chart_type") 
    print("  - house_system")
    print("  - ayanamsa")
    print("  - calculated_at")
    print("  - calculation_version")
    print("  - chart_data (JSON)")
    print("  - planet_positions (JSON)")
    print("  - house_cusps (JSON)")
    print("  - aspects (JSON)")
    print("  - divisional_chart_type (nullable)")
    print("  - progression_type (nullable)")
    print("  - organization_id (added by TenantRepository)")
    print("  - created_at (auto)")
    print("  - updated_at (auto)")
    print("  - is_deleted (default)")
    print("  - deleted_at (nullable)")
    
    # The error says "function takes at most 7 arguments (8 given)"
    # This might be a PostgreSQL trigger or stored procedure
    print("\nPossible issues:")
    print("1. Database trigger expecting different number of columns")
    print("2. Stored procedure for INSERT has wrong signature")
    print("3. Model definition mismatch with database schema")

if __name__ == "__main__":
    trace_chart_dict()