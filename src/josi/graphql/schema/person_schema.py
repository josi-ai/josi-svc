"""
Person GraphQL schema.
"""
import strawberry
from strawberry.types import Info
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from josi.graphql.base import PaginationWindow, get_pagination_window, get_selected_fields, get_updated_fields
from josi.models import (
    PersonSchema,
    PersonInput,
    PersonCreateInput,
    PersonUpdateInput
)


@strawberry.type
class PersonQuery:
    @strawberry.field
    async def persons(
        self,
        info: Info,
        limit: Optional[int] = 100,
        offset: Optional[int] = 0,
        order_by: Optional[str] = None
    ) -> List[PersonSchema]:
        """Get all persons with optional pagination."""
        persons = await info.context.person_service.list_persons(
            limit=limit,
            offset=offset,
            selected_fields=get_selected_fields(info)
        )
        return [PersonSchema.from_orm(person) for person in persons]
    
    @strawberry.field
    async def search_persons(
        self,
        info: Info,
        limit: Optional[int] = 100,
        offset: Optional[int] = 0,
        search: Optional[str] = None,
        order_by: Optional[str] = None
    ) -> PaginationWindow[PersonSchema]:
        """Search persons with pagination."""
        persons = await info.context.person_service.list_persons(
            limit=limit,
            offset=offset,
            search=search,
            selected_fields=get_selected_fields(info)
        )
        
        total_count = await info.context.person_service.get_total_persons_count(search=search)
        
        schemas = [PersonSchema.from_orm(person) for person in persons]
        
        return get_pagination_window(
            data=schemas,
            total_count=total_count,
            limit=limit,
            offset=offset
        )
    
    @strawberry.field
    async def person(self, info: Info, person_id: UUID) -> Optional[PersonSchema]:
        """Get a person by ID."""
        person = await info.context.person_service.get_person(
            person_id=person_id,
            selected_fields=get_selected_fields(info)
        )
        return PersonSchema.from_orm(person) if person else None
    
    @strawberry.field
    async def persons_by_ids(
        self,
        info: Info,
        person_ids: List[UUID],
        limit: Optional[int] = 100,
        offset: Optional[int] = 0
    ) -> PaginationWindow[PersonSchema]:
        """Get persons by multiple IDs."""
        persons = await info.context.person_service.get_persons_by_ids(
            person_ids=person_ids,
            limit=limit,
            offset=offset,
            selected_fields=get_selected_fields(info)
        )
        
        total_count = len(person_ids)  # Or get actual count from service
        
        schemas = [PersonSchema.from_orm(person) for person in persons]
        
        return get_pagination_window(
            data=schemas,
            total_count=total_count,
            limit=limit,
            offset=offset
        )


@strawberry.type
class PersonMutation:
    @strawberry.field
    async def add_person(self, info: Info, person: PersonCreateInput) -> PersonSchema:
        """Create a new person."""
        person_data = person.to_pydantic()
        new_person = await info.context.person_service.create_person(person_data)
        return PersonSchema.from_orm(new_person)
    
    @strawberry.field
    async def add_persons(self, info: Info, persons: List[PersonCreateInput]) -> List[PersonSchema]:
        """Create multiple persons."""
        persons_data = [person.to_pydantic() for person in persons]
        new_persons = await info.context.person_service.create_persons(persons_data)
        return [PersonSchema.from_orm(person) for person in new_persons]
    
    @strawberry.field
    async def update_person(
        self,
        info: Info,
        person_id: UUID,
        person: PersonUpdateInput
    ) -> PersonSchema:
        """Update a person."""
        person_data = person.to_pydantic()
        updated_person = await info.context.person_service.update_person(
            person_id=person_id,
            person_data=person_data,
            updated_fields=get_updated_fields(info)
        )
        return PersonSchema.from_orm(updated_person)
    
    @strawberry.field
    async def update_persons(
        self,
        info: Info,
        persons: List[PersonUpdateInput]
    ) -> List[PersonSchema]:
        """Update multiple persons."""
        persons_data = [person.to_pydantic() for person in persons]
        updated_persons = await info.context.person_service.update_persons(
            persons_data=persons_data,
            updated_fields=get_updated_fields(info)
        )
        return [PersonSchema.from_orm(person) for person in updated_persons]
    
    @strawberry.field
    async def delete_person(self, info: Info, person_id: UUID) -> bool:
        """Delete a person."""
        return await info.context.person_service.delete_person(person_id)
    
    @strawberry.field
    async def restore_person(self, info: Info, person_id: UUID) -> PersonSchema:
        """Restore a deleted person."""
        restored_person = await info.context.person_service.restore_person(person_id)
        return PersonSchema.from_orm(restored_person)