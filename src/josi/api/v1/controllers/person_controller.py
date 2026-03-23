"""
Person management controller - Clean Architecture.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from uuid import UUID
import logging

from josi.api.v1.dependencies import PersonServiceDep
from josi.api.response import ResponseModel
from josi.models.person_model import PersonEntity
from josi.api.v1.dto.person_dto import CreatePersonRequest

log = logging.getLogger("uvicorn")

router = APIRouter(prefix="/persons", tags=["persons"])


@router.post("/", response_model=ResponseModel)
async def create_person(
    payload: CreatePersonRequest,
    person_service: PersonServiceDep
) -> ResponseModel:
    """
    Create a new person record.
    
    This endpoint creates a new person in the system with their birth information.
    The place of birth will be automatically geocoded to latitude/longitude coordinates
    and the timezone will be determined based on the location.
    
    Args:
        payload (CreatePersonRequest): Person creation data
            - name (str): Full name of the person
            - date_of_birth (date): Birth date in YYYY-MM-DD format
            - time_of_birth (str): Birth time in flexible formats:
                * 24-hour: "14:30" or "14:30:00"
                * 12-hour: "2:30 PM" or "02:30 PM"
            - place_of_birth (str): Birth location as "City, State, Country"
            - email (str, optional): Email address
            - phone (str, optional): Phone number
            - notes (str, optional): Additional notes about the person
        person_service (PersonServiceDep): Injected person service
    
    Returns:
        ResponseModel: Success response with created person data
            - success (bool): True if successful
            - message (str): Success message
            - data (Person): Created person object with:
                - person_id (UUID): Unique identifier
                - name (str): Full name
                - time_of_birth (datetime): Complete birth datetime
                - place_of_birth (str): Birth location
                - latitude (float): Geocoded latitude
                - longitude (float): Geocoded longitude
                - timezone (str): Determined timezone
                - created_at (datetime): Creation timestamp
    
    Raises:
        HTTPException(400): If payload is empty or geocoding fails
        HTTPException(422): If time format is invalid
        HTTPException(500): If person creation fails
    
    Example:
        POST /api/v1/persons
        {
            "name": "John Doe",
            "date_of_birth": "1990-01-01",
            "time_of_birth": "2:30 PM",
            "place_of_birth": "New York, NY, USA"
        }
    """
    if payload is None:
        raise HTTPException(400, "payload is empty")
    
    try:
        # Convert DTO to entity
        person_entity = payload.to_person_entity()
        person = await person_service.create_person(person_entity)
        return ResponseModel(
            success=True,
            message="Person created successfully",
            data=person
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        log.error(f"Failed to create person: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create person: {str(e)}")


@router.get("/{person_id}", response_model=ResponseModel)
# @cache(expire=7200)  # Cache for 2 hours - disabled for now
async def get_person(
    person_id: UUID,
    person_service: PersonServiceDep
) -> ResponseModel:
    """
    Get a person by ID.
    
    Retrieves complete person information including birth details and
    calculated astronomical positions if available.
    
    Args:
        person_id (UUID): Unique identifier of the person
        person_service (PersonServiceDep): Injected person service
    
    Returns:
        ResponseModel: Success response with person data
            - success (bool): True if successful
            - message (str): Success message
            - data (Person): Person object with all fields
    
    Raises:
        HTTPException(400): If person_id is empty
        HTTPException(404): If person not found
    
    Example:
        GET /api/v1/persons/123e4567-e89b-12d3-a456-426614174000
    """
    if person_id is None:
        raise HTTPException(400, "person_id is empty")
    
    person = await person_service.get_person(person_id)
    if not person:
        raise HTTPException(status_code=404, detail=f"Person with id: {person_id} not found")
    
    return ResponseModel(
        success=True,
        message="Person retrieved successfully",
        data=person
    )


@router.get("/", response_model=ResponseModel)
# @cache(expire=3600)  # Cache for 1 hour - disabled for now
async def list_persons(
    person_service: PersonServiceDep,
    search: Optional[str] = Query(None, description="Search by name"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
) -> ResponseModel:
    """
    List all persons with optional search and pagination.
    
    Retrieves a paginated list of persons, optionally filtered by name search.
    Results are ordered by creation date (newest first).
    
    Args:
        search (str, optional): Search term to filter by name
        skip (int): Number of records to skip (for pagination)
        limit (int): Maximum number of records to return (1-1000)
        person_service (PersonServiceDep): Injected person service
    
    Returns:
        ResponseModel: Success response with list of persons
            - success (bool): True if successful
            - message (str): Success message with count
            - data (List[Person]): List of person objects
    
    Example:
        GET /api/v1/persons?search=John&skip=0&limit=10
    """
    if search:
        persons = await person_service.search(search, skip, limit)
    else:
        persons = await person_service.list_persons(skip, limit)
    
    return ResponseModel(
        success=True,
        message=f"Found {len(persons)} persons",
        data=persons
    )


@router.put("/{person_id}", response_model=ResponseModel)
async def update_person(
    person_id: UUID,
    payload: PersonEntity,
    person_service: PersonServiceDep
) -> ResponseModel:
    """
    Update a person's information.
    
    Updates person details. If place_of_birth is changed, it will be
    re-geocoded to update latitude, longitude, and timezone.
    
    Args:
        person_id (UUID): Unique identifier of the person to update
        payload (PersonEntity): Updated person data
        person_service (PersonServiceDep): Injected person service
    
    Returns:
        ResponseModel: Success response with updated person data
            - success (bool): True if successful
            - message (str): Success message
            - data (Person): Updated person object
    
    Raises:
        HTTPException(400): If validation fails
        HTTPException(404): If person not found
        HTTPException(500): If update fails
    
    Example:
        PUT /api/v1/persons/123e4567-e89b-12d3-a456-426614174000
        {
            "name": "John Doe Updated",
            "place_of_birth": "Los Angeles, CA, USA"
        }
    """
    try:
        person = await person_service.update(person_id, payload)
        return ResponseModel(
            success=True,
            message="Person updated successfully",
            data=person
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        log.error(f"Failed to update person: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update person: {str(e)}")


@router.delete("/{person_id}", response_model=ResponseModel)
async def delete_person(
    person_id: UUID,
    person_service: PersonServiceDep
) -> ResponseModel:
    """
    Delete a person (soft delete).
    
    Performs a soft delete by marking the person as deleted.
    The record remains in the database but is excluded from normal queries.
    Associated charts and interpretations are also soft deleted.
    
    Args:
        person_id (UUID): Unique identifier of the person to delete
        person_service (PersonServiceDep): Injected person service
    
    Returns:
        ResponseModel: Success response
            - success (bool): True if successful
            - message (str): Success message
            - data (dict): Contains deleted person_id
    
    Raises:
        HTTPException(404): If person not found
        HTTPException(500): If deletion fails
    
    Example:
        DELETE /api/v1/persons/123e4567-e89b-12d3-a456-426614174000
    """
    success = await person_service.delete(person_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Person with id: {person_id} not found")
    
    return ResponseModel(
        success=True,
        message="Person deleted successfully",
        data={"person_id": str(person_id)}
    )


@router.post("/{person_id}/update-birth-location", response_model=ResponseModel)
async def update_birth_location(
    person_id: UUID,
    person_service: PersonServiceDep,
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    timezone: str = Query(...)
) -> ResponseModel:
    """
    Update person's birth location coordinates.
    
    Directly updates latitude, longitude, and timezone without geocoding.
    Useful when precise coordinates are known or when geocoding fails.
    
    Args:
        person_id (UUID): Unique identifier of the person
        latitude (float): Birth location latitude (-90 to 90)
        longitude (float): Birth location longitude (-180 to 180)
        timezone (str): Timezone name (e.g., "America/New_York")
        person_service (PersonServiceDep): Injected person service
    
    Returns:
        ResponseModel: Success response with updated person data
    
    Raises:
        HTTPException(400): If coordinates are invalid
        HTTPException(404): If person not found
    
    Example:
        POST /api/v1/persons/123e4567-e89b-12d3-a456-426614174000/update-birth-location
        ?latitude=40.7128&longitude=-74.0060&timezone=America/New_York
    """
    try:
        person = await person_service.update_birth_location(
            person_id, latitude, longitude, timezone
        )
        return ResponseModel(
            success=True,
            message="Birth location updated successfully",
            data=person
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        log.error(f"Failed to update birth location: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update birth location")


@router.get("/{person_id}/charts", response_model=ResponseModel)
async def get_person_charts(
    person_id: UUID,
    person_service: PersonServiceDep
) -> ResponseModel:
    """
    Get all charts for a person.
    
    Retrieves all astrological charts calculated for the person,
    including natal charts, divisional charts, and special charts.
    
    Args:
        person_id (UUID): Unique identifier of the person
        person_service (PersonServiceDep): Injected person service
    
    Returns:
        ResponseModel: Success response with list of charts
            - success (bool): True if successful
            - message (str): Success message with count
            - data (List[AstrologyChart]): List of chart objects
    
    Example:
        GET /api/v1/persons/123e4567-e89b-12d3-a456-426614174000/charts
    """
    charts = await person_service.get_person_charts(person_id)
    
    return ResponseModel(
        success=True,
        message=f"Found {len(charts)} charts",
        data=charts
    )