"""Lookup endpoints — serves enum values for frontend dropdowns."""
from fastapi import APIRouter

from josi.enums import ALL_ENUMS

router = APIRouter(prefix="/lookups", tags=["lookups"])


@router.get("")
async def get_all_lookups():
    """Return all enum values grouped by type. Used by frontend for dropdowns."""
    return {
        key: enum_cls.to_lookup_list()
        for key, enum_cls in ALL_ENUMS.items()
    }


@router.get("/{lookup_type}")
async def get_lookup(lookup_type: str):
    """Return values for a specific lookup type."""
    enum_cls = ALL_ENUMS.get(lookup_type)
    if not enum_cls:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unknown lookup type: {lookup_type}. Available: {list(ALL_ENUMS.keys())}",
        )
    return enum_cls.to_lookup_list()
