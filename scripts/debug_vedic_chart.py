#!/usr/bin/env python3
"""Debug script to reproduce Vedic chart creation error with SQL logging."""

import asyncio
import logging
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlmodel import Session
from datetime import datetime
import pytz

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Enable SQL logging
@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    logger.info("SQL Statement: %s", statement)
    logger.info("Parameters: %s", parameters)

# Import after logging is configured
import sys
sys.path.insert(0, '/Users/govind/Developer/josi/src')

from josi.core.config import settings
from josi.models.organization_model import Organization
from josi.models.person_model import Person
from josi.services.chart_service import ChartService
from josi.repositories.chart_repository import ChartRepository
from josi.repositories.person_repository import PersonRepository

async def main():
    """Test Vedic chart creation with SQL logging."""
    # Create engine with echo=True for SQL logging
    engine = create_engine(settings.database_url, echo=True)
    
    with Session(engine) as session:
        # Get or create test organization
        org = session.query(Organization).filter_by(slug="test-org").first()
        if not org:
            org = Organization(
                name="Test Organization",
                slug="test-org",
                api_key="test-api-key",
                is_active=True,
                plan_type="premium",
                monthly_api_limit=10000,
                current_month_usage=0,
                is_deleted=False
            )
            session.add(org)
            session.commit()
            session.refresh(org)
        
        # Get or create test person
        person = session.query(Person).filter_by(
            organization_id=org.organization_id,
            name="Test User"
        ).first()
        
        if not person:
            person = Person(
                organization_id=org.organization_id,
                name="Test User",
                email="test@example.com",
                date_of_birth=datetime(1990, 1, 1).date(),
                time_of_birth=datetime(1990, 1, 1, 12, 0, 0),
                place_of_birth="New York, USA",
                latitude=40.7128,
                longitude=-74.0060,
                timezone="America/New_York",
                is_deleted=False
            )
            session.add(person)
            session.commit()
            session.refresh(person)
        
        # Create services
        chart_repo = ChartRepository(session)
        person_repo = PersonRepository(session)
        chart_service = ChartService(chart_repo, person_repo, session, org.organization_id)
        
        try:
            logger.info("Creating Vedic chart for person_id: %s", person.person_id)
            
            # This should trigger the error
            vedic_chart = await chart_service.create_chart(
                person_id=person.person_id,
                chart_type="vedic",
                house_system="whole_sign",
                ayanamsa="lahiri"
            )
            
            logger.info("Vedic chart created successfully: %s", vedic_chart.chart_id)
            
        except Exception as e:
            logger.error("Error creating Vedic chart: %s", str(e))
            logger.exception("Full traceback:")
            
        # Also try Western chart for comparison
        try:
            logger.info("Creating Western chart for comparison...")
            
            western_chart = await chart_service.create_chart(
                person_id=person.person_id,
                chart_type="western",
                house_system="placidus"
            )
            
            logger.info("Western chart created successfully: %s", western_chart.chart_id)
            
        except Exception as e:
            logger.error("Error creating Western chart: %s", str(e))

if __name__ == "__main__":
    asyncio.run(main())