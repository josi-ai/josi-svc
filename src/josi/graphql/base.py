"""
Base GraphQL utilities for pagination and common functionality.
"""
from typing import Generic, TypeVar, List, Optional
import strawberry
from strawberry.types import Info


T = TypeVar("T")


@strawberry.type
class PaginationWindow(Generic[T]):
    """Generic pagination window for any type."""
    data: List[T]
    total_count: int
    limit: int
    offset: int
    
    @property
    def has_next(self) -> bool:
        return self.offset + len(self.data) < self.total_count
    
    @property
    def has_previous(self) -> bool:
        return self.offset > 0


def get_pagination_window(
    data: List[T],
    total_count: int,
    limit: int = 100,
    offset: int = 0
) -> PaginationWindow[T]:
    """Create a pagination window from data."""
    return PaginationWindow(
        data=data,
        total_count=total_count,
        limit=limit,
        offset=offset
    )


def get_selected_fields(info: Info) -> List[str]:
    """Extract selected fields from GraphQL query info."""
    selected_fields = []
    
    # Get the field selection from the GraphQL query
    for field in info.selected_fields:
        if hasattr(field, 'name'):
            selected_fields.append(field.name)
    
    return selected_fields


def get_updated_fields(info: Info) -> List[str]:
    """Extract fields that were provided in a mutation."""
    # In mutations, we want to track which fields were actually provided
    # This is useful for partial updates
    updated_fields = []
    
    # This would need to be implemented based on your specific needs
    # For now, return empty list
    return updated_fields