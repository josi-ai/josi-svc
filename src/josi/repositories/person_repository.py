from typing import Optional, List
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from uuid import UUID
from josi.repositories.base_repository import BaseRepository
from josi.models import Person, AstrologyChart


class PersonRepository(BaseRepository[Person]):
    """Repository for Person operations."""
    
    async def get_with_charts(self, person_id: UUID) -> Optional[Person]:
        """Get person with all their charts."""
        query = (
            select(Person)
            .where(
                and_(
                    Person.person_id == person_id,
                    Person.is_deleted == False
                )
            )
            .options(
                selectinload(Person.charts).selectinload(AstrologyChart.interpretations)
            )
        )
        
        # Apply tenant filter
        query = self._apply_tenant_filter(query)
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def find_by_email(self, email: str) -> Optional[Person]:
        """Find person by email within organization."""
        query = select(Person).where(
            and_(
                Person.email == email,
                Person.is_deleted == False
            )
        )
        
        # Apply tenant filter
        query = self._apply_tenant_filter(query)
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def search_by_name(self, name: str, limit: int = 10) -> List[Person]:
        """Search persons by name within organization."""
        query = (
            select(Person)
            .where(
                and_(
                    Person.name.ilike(f"%{name}%"),
                    Person.is_deleted == False
                )
            )
            .limit(limit)
        )
        
        # Apply tenant filter
        query = self._apply_tenant_filter(query)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())


class ChartRepository(BaseRepository[AstrologyChart]):
    """Repository for AstrologyChart operations."""
    
    async def get_person_charts(
        self,
        person_id: UUID,
        chart_type: Optional[str] = None
    ) -> List[AstrologyChart]:
        """Get all charts for a person."""
        query = select(AstrologyChart).where(
            and_(
                AstrologyChart.person_id == person_id,
                AstrologyChart.is_deleted == False
            )
        )
        
        if chart_type:
            query = query.where(AstrologyChart.chart_type == chart_type)
        
        # Apply tenant filter
        query = self._apply_tenant_filter(query)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_latest_chart(
        self,
        person_id: UUID,
        chart_type: str
    ) -> Optional[AstrologyChart]:
        """Get the most recent chart of a specific type for a person."""
        query = (
            select(AstrologyChart)
            .where(
                and_(
                    AstrologyChart.person_id == person_id,
                    AstrologyChart.chart_type == chart_type,
                    AstrologyChart.is_deleted == False
                )
            )
            .order_by(AstrologyChart.calculated_at.desc())
            .limit(1)
        )
        
        # Apply tenant filter
        query = self._apply_tenant_filter(query)
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()