"""
Test to isolate and fix the Vedic chart database error.
"""

import pytest
import asyncio
from datetime import datetime
from uuid import uuid4
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os

# Import models
import sys
sys.path.append('/Users/govind/Developer/astrow/src')
from josi.models.chart_model import AstrologyChart, AstrologySystem, HouseSystem, Ayanamsa
from josi.models.base import SQLBaseModel
from sqlalchemy import text

@pytest.mark.asyncio
async def test_minimal_chart_creation():
    """Test creating a minimal chart record to isolate the error."""
    
    # Database connection
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost/astrow")
    
    engine = create_async_engine(DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            # First, let's check the database schema
            result = await session.execute(
                text("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'astrology_chart'
                ORDER BY ordinal_position
                """)
            )
            
            print("\nDatabase schema for astrology_chart:")
            for row in result:
                print(f"  {row[0]}: {row[1]} (nullable: {row[2]})")
            
            # Try creating a Western chart (this works)
            western_chart = AstrologyChart(
                person_id=uuid4(),
                chart_type=AstrologySystem.WESTERN.value,
                house_system=HouseSystem.PLACIDUS.value,
                ayanamsa=None,  # NULL for Western
                calculated_at=datetime.utcnow(),
                calculation_version="2.0",
                chart_data={"test": "western"},
                planet_positions={},
                house_cusps=[],
                aspects=[],
                organization_id=uuid4()
            )
            
            session.add(western_chart)
            await session.flush()
            print(f"\n✅ Western chart created: {western_chart.chart_id}")
            
            # Try creating a Vedic chart (this fails)
            vedic_chart = AstrologyChart(
                person_id=uuid4(),
                chart_type=AstrologySystem.VEDIC.value,
                house_system=HouseSystem.WHOLE_SIGN.value,
                ayanamsa=Ayanamsa.LAHIRI.value,  # Has value for Vedic
                calculated_at=datetime.utcnow(),
                calculation_version="2.0",
                chart_data={"test": "vedic"},
                planet_positions={},
                house_cusps=[],
                aspects=[],
                organization_id=uuid4()
            )
            
            session.add(vedic_chart)
            await session.flush()
            print(f"\n✅ Vedic chart created: {vedic_chart.chart_id}")
            
            await session.rollback()  # Don't actually save
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print(f"   Type: {type(e).__name__}")
            if hasattr(e, 'orig'):
                print(f"   Original: {e.orig}")
            await session.rollback()

async def test_check_functions():
    """Check for any database functions that might be causing the error."""
    
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost/astrow")
    engine = create_async_engine(DATABASE_URL)
    
    async with engine.begin() as conn:
        # Check for functions
        result = await conn.execute(
            text("""
            SELECT routine_name, routine_type, data_type
            FROM information_schema.routines
            WHERE routine_schema = 'public'
            AND routine_name LIKE '%chart%'
            """)
        )
        
        print("\nDatabase functions related to 'chart':")
        for row in result:
            print(f"  {row[0]} ({row[1]}): {row[2]}")
        
        # Check for triggers
        result = await conn.execute(
            text("""
            SELECT trigger_name, event_manipulation, event_object_table
            FROM information_schema.triggers
            WHERE trigger_schema = 'public'
            """)
        )
        
        print("\nDatabase triggers:")
        for row in result:
            print(f"  {row[0]} on {row[2]} ({row[1]})")

if __name__ == "__main__":
    print("Testing minimal chart creation...")
    asyncio.run(test_minimal_chart_creation())
    
    print("\n\nChecking for database functions/triggers...")
    asyncio.run(test_check_functions())