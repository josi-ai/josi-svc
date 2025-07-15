"""
Improved person controller following clean architecture.
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from uuid import UUID
import logging

from josi.api.response import ResponseModel
from josi.models.person_model import PersonEntity
from josi.api.v1.dependencies_improved import PersonServiceDep

log = logging.getLogger("uvicorn")

router = APIRouter(prefix="/persons", tags=["persons"])


@router.post("/", response_model=ResponseModel)
async def create_person(
    payload: PersonEntity,
    person_service: PersonServiceDep  # ✅ Inject service, not database
) -> ResponseModel:
    """
    Create a new person record.
    
    Controller only handles:
    - HTTP request/response
    - Input validation
    - Error transformation
    - No database concerns!
    """
    if payload is None:
        raise HTTPException(400, "payload is empty")
    
    try:
        person = await person_service.create_person(payload)
        return ResponseModel(
            success=True,
            message="Person created successfully",
            data=person
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        log.error(f"Failed to create person: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{person_id}", response_model=ResponseModel)
async def get_person(
    person_id: UUID,
    person_service: PersonServiceDep  # ✅ Clean dependency injection
) -> ResponseModel:
    """Get a person by ID."""
    person = await person_service.get_by_id(person_id)
    
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    
    return ResponseModel(
        success=True,
        message="Person retrieved successfully",
        data=person
    )


@router.get("/", response_model=ResponseModel)
async def list_persons(
    person_service: PersonServiceDep,  # ✅ Service handles all business logic
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> ResponseModel:
    """List all persons with optional search."""
    persons = await person_service.list(
        search=search,
        skip=skip,
        limit=limit
    )
    
    return ResponseModel(
        success=True,
        message=f"Retrieved {len(persons)} persons",
        data=persons
    )