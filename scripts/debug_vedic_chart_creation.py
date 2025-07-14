#!/usr/bin/env python3
"""
Debug script to trace Vedic chart creation issue.
"""

import sys
sys.path.append('/Users/govind/Developer/astrow')

from datetime import datetime
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from josi.core.database import get_session
from josi.repositories.chart_repository import ChartRepository
from josi.models.chart_model import AstrologySystem, HouseSystem, Ayanamsa
from uuid import uuid4

async def test_chart_creation():
    """Test creating a chart directly in the database."""
    
    async for session in get_session():
        chart_repo = ChartRepository(session)
        
        # Create test chart data - minimal first
        chart_data = {
            "person_id": uuid4(),  # Random UUID for testing
            "chart_type": AstrologySystem.VEDIC.value,
            "house_system": HouseSystem.WHOLE_SIGN.value,
            "ayanamsa": Ayanamsa.LAHIRI.value,
            "calculated_at": datetime.utcnow(),
            "calculation_version": "2.0",
            "chart_data": {"test": "data"},
            "planet_positions": {},
            "house_cusps": [],
            "aspects": []
        }
        
        print("Creating chart with data:")
        for key, value in chart_data.items():
            print(f"  {key}: {value}")
        
        try:
            # Set organization_id for the repository
            chart_repo.organization_id = uuid4()  # Test organization
            
            chart = await chart_repo.create(chart_data)
            print(f"\n✅ Chart created successfully: {chart.chart_id}")
            
            # Commit the transaction
            await session.commit()
            
        except Exception as e:
            print(f"\n❌ Error creating chart: {e}")
            print(f"   Error type: {type(e).__name__}")
            
            # Check if it's a SQL error
            if hasattr(e, 'orig'):
                print(f"   Original error: {e.orig}")
            
            await session.rollback()
            
        finally:
            await session.close()

if __name__ == "__main__":
    asyncio.run(test_chart_creation())