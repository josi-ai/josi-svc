#!/usr/bin/env python3
"""
Test direct database insert to isolate the 7 arguments error.
"""

import asyncio
import asyncpg
import json
from datetime import datetime
from uuid import uuid4

async def test_direct_insert():
    """Test inserting chart data directly into database."""
    
    # Connect to database
    conn = await asyncpg.connect(
        host='localhost',
        port=5432,
        user='astrow',
        password='astrow',
        database='astrow'
    )
    
    try:
        # Get a test person with their organization
        person = await conn.fetchrow(
            "SELECT person_id, organization_id FROM person LIMIT 1"
        )
        
        if not person:
            print("No person found in database")
            return
            
        person_id = person['person_id']
        org_id = person['organization_id']
        
        print(f"Using person_id: {person_id}")
        
        # Test 1: Insert Western chart (should work)
        print("\n1. Testing Western chart insert...")
        try:
            western_id = await conn.fetchval("""
                INSERT INTO astrology_chart (
                    person_id, organization_id, chart_type, house_system,
                    ayanamsa, calculated_at, calculation_version,
                    chart_data, planet_positions, house_cusps, aspects,
                    is_deleted
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12
                ) RETURNING chart_id
            """, 
                person_id, org_id, 'western', 'placidus',
                None, datetime.utcnow(), '2.0',
                json.dumps({"test": "western"}), json.dumps({}), json.dumps([]), json.dumps([]),
                False
            )
            print(f"✅ Western chart created: {western_id}")
        except Exception as e:
            print(f"❌ Western chart failed: {e}")
        
        # Test 2: Insert Vedic chart (might fail)
        print("\n2. Testing Vedic chart insert...")
        try:
            vedic_id = await conn.fetchval("""
                INSERT INTO astrology_chart (
                    person_id, organization_id, chart_type, house_system,
                    ayanamsa, calculated_at, calculation_version,
                    chart_data, planet_positions, house_cusps, aspects,
                    is_deleted
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12
                ) RETURNING chart_id
            """, 
                person_id, org_id, 'vedic', 'whole_sign',
                'lahiri', datetime.utcnow(), '2.0',
                json.dumps({"test": "vedic"}), json.dumps({}), json.dumps([]), json.dumps([]),
                False
            )
            print(f"✅ Vedic chart created: {vedic_id}")
        except Exception as e:
            print(f"❌ Vedic chart failed: {e}")
            print(f"   Error type: {type(e).__name__}")
            
        # Test 3: Check if it's the planet_position insert
        print("\n3. Testing planet_position insert for Vedic chart...")
        if 'vedic_id' in locals():
            try:
                # Simulate Vedic planet data
                planet_id = await conn.fetchval("""
                    INSERT INTO planet_position (
                        chart_id, organization_id, planet_name,
                        longitude, latitude, speed,
                        sign, sign_degree, house,
                        nakshatra, nakshatra_pada,
                        is_retrograde, is_combust, is_deleted
                    ) VALUES (
                        $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14
                    ) RETURNING planet_position_id
                """,
                    vedic_id, org_id, 'Sun',
                    120.5, 0.0, 1.0,
                    'Leo', 0.5, 1,
                    'Magha', 1,  # Vedic-specific fields
                    False, False, False
                )
                print(f"✅ Planet position created: {planet_id}")
            except Exception as e:
                print(f"❌ Planet position failed: {e}")
                
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(test_direct_insert())