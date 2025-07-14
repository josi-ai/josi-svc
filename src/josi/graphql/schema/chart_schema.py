"""
Chart GraphQL schema.
"""
import strawberry
from strawberry.types import Info
from typing import List, Optional
from uuid import UUID

from josi.graphql.base import PaginationWindow, get_pagination_window, get_selected_fields
from josi.models import (
    ChartSchema,
    ChartCreateInput,
    ChartInterpretationSchema
)


@strawberry.type
class ChartQuery:
    @strawberry.field
    async def charts(
        self,
        info: Info,
        limit: Optional[int] = 100,
        offset: Optional[int] = 0,
        chart_type: Optional[str] = None
    ) -> List[ChartSchema]:
        """Get all charts with optional filtering."""
        charts = await info.context.chart_service.get_all_charts(
            limit=limit,
            offset=offset,
            chart_type=chart_type,
            selected_fields=get_selected_fields(info)
        )
        return [ChartSchema.from_orm(chart) for chart in charts]
    
    @strawberry.field
    async def chart(self, info: Info, chart_id: UUID) -> Optional[ChartSchema]:
        """Get a chart by ID."""
        chart = await info.context.chart_service.get_chart(
            chart_id=chart_id,
            selected_fields=get_selected_fields(info)
        )
        return ChartSchema.from_orm(chart) if chart else None
    
    @strawberry.field
    async def person_charts(
        self,
        info: Info,
        person_id: UUID,
        chart_type: Optional[str] = None,
        limit: Optional[int] = 100,
        offset: Optional[int] = 0
    ) -> PaginationWindow[ChartSchema]:
        """Get all charts for a person."""
        charts = await info.context.chart_service.get_person_charts(
            person_id=person_id,
            chart_type=chart_type,
            limit=limit,
            offset=offset,
            selected_fields=get_selected_fields(info)
        )
        
        total_count = await info.context.chart_service.get_person_charts_count(
            person_id=person_id,
            chart_type=chart_type
        )
        
        schemas = [ChartSchema.from_orm(chart) for chart in charts]
        
        return get_pagination_window(
            data=schemas,
            total_count=total_count,
            limit=limit,
            offset=offset
        )
    
    @strawberry.field
    async def chart_interpretations(
        self,
        info: Info,
        chart_id: UUID
    ) -> List[ChartInterpretationSchema]:
        """Get all interpretations for a chart."""
        interpretations = await info.context.chart_service.get_chart_interpretations(
            chart_id=chart_id,
            selected_fields=get_selected_fields(info)
        )
        return [ChartInterpretationSchema.from_orm(interp) for interp in interpretations]


@strawberry.type
class ChartMutation:
    @strawberry.field
    async def calculate_chart(
        self,
        info: Info,
        person_id: UUID,
        chart_types: List[str],
        house_system: str = "placidus",
        ayanamsa: Optional[str] = None,
        include_interpretations: bool = False
    ) -> List[ChartSchema]:
        """Calculate astrological charts for a person."""
        charts = await info.context.chart_service.calculate_charts_for_person(
            person_id=person_id,
            chart_types=chart_types,
            house_system=house_system,
            ayanamsa=ayanamsa,
            include_interpretations=include_interpretations
        )
        return [ChartSchema.from_orm(chart) for chart in charts]
    
    @strawberry.field
    async def generate_interpretation(
        self,
        info: Info,
        chart_id: UUID,
        interpretation_types: List[str],
        language: str = "en"
    ) -> List[ChartInterpretationSchema]:
        """Generate interpretations for a chart."""
        interpretations = await info.context.chart_service.generate_interpretations(
            chart_id=chart_id,
            interpretation_types=interpretation_types,
            language=language
        )
        return [ChartInterpretationSchema.from_orm(interp) for interp in interpretations]
    
    @strawberry.field
    async def delete_chart(self, info: Info, chart_id: UUID) -> bool:
        """Delete a chart."""
        return await info.context.chart_service.delete_chart(chart_id)
    
    @strawberry.field
    async def restore_chart(self, info: Info, chart_id: UUID) -> ChartSchema:
        """Restore a deleted chart."""
        restored_chart = await info.context.chart_service.restore_chart(chart_id)
        return ChartSchema.from_orm(restored_chart)