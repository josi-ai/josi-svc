#!/usr/bin/env python3
"""
Trace the exact location of the Vedic chart API error.
"""

import asyncio
import sys
sys.path.append('/Users/govind/Developer/astrow/src')

from datetime import datetime
import pytz
from uuid import UUID
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Import services and models
from josi.services.chart_service import ChartService
from josi.models.chart_model import AstrologySystem, HouseSystem, Ayanamsa
from josi.models.person_model import Person

async def trace_api_flow():
    """Trace the API flow to find where the error occurs."""
    
    # Setup database connection
    DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/josi_prod"
    engine = create_async_engine(DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as db:
        # Use test person ID
        person_id = UUID('f2303d9c-0bc9-4b18-b17e-9cf4b7bd5f9f')
        org_id = UUID('00000000-0000-0000-0000-000000000000')
        
        print("\n1. Creating ChartService...")
        chart_service = ChartService(db, org_id)
        
        print("\n2. Calling calculate_charts_for_person with vedic...")
        try:
            # Add some debug prints to trace the flow
            original_calculate_charts = chart_service.calculate_charts
            
            async def debug_calculate_charts(*args, **kwargs):
                print(f"\n   DEBUG: calculate_charts called with:")
                print(f"   - args: {len(args)}")
                print(f"   - kwargs: {kwargs.keys()}")
                return await original_calculate_charts(*args, **kwargs)
            
            chart_service.calculate_charts = debug_calculate_charts
            
            # Call the method
            charts = await chart_service.calculate_charts_for_person(
                person_id=person_id,
                chart_types=['vedic'],
                house_system='whole_sign',
                ayanamsa='lahiri',
                include_interpretations=False
            )
            
            print("\n✅ Success! Charts calculated:")
            for chart in charts:
                print(f"   - {chart.chart_type}: {chart.chart_id}")
                
        except Exception as e:
            print(f"\n❌ Error occurred: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(trace_api_flow())