"""Integration tests for Person API endpoints."""
import pytest
from uuid import uuid4
from datetime import datetime, date
from decimal import Decimal

from tests.conftest import assert_response_success, assert_response_error


@pytest.mark.integration
class TestPersonAPIFixed:
    """Integration tests for Person API endpoints."""
    
    @pytest.mark.asyncio
    async def test_create_person_full_flow(self, async_client, test_organization):
        """Test creating a person with full data flow."""
        # Create person data matching PersonEntity model
        person_data = {
            "name": "John Doe",
            "date_of_birth": "1990-01-01",
            "time_of_birth": "1990-01-01T12:00:00",
            "place_of_birth": "New York, NY, USA",
            "latitude": "40.7128",
            "longitude": "-74.0060",
            "timezone": "America/New_York",
            "email": "john.doe@example.com",
            "phone": "+1234567890"
        }
        
        # Send POST request
        response = await async_client.post("/api/v1/persons/", json=person_data)
        
        # Verify response
        person = assert_response_success(response, status_code=201)
        assert person["name"] == "John Doe"
        assert person["email"] == "john.doe@example.com"
        assert person["organization_id"] == str(test_organization.organization_id)
        
        # Verify person was created in database
        person_id = person["person_id"]
        get_response = await async_client.get(f"/api/v1/persons/{person_id}")
        retrieved_person = assert_response_success(get_response)
        assert retrieved_person["person_id"] == person_id
    
    @pytest.mark.asyncio
    async def test_create_person_minimal_data(self, async_client):
        """Test creating a person with minimal required data."""
        person_data = {
            "name": "Jane Doe",
            "date_of_birth": "1995-05-15",
            "time_of_birth": "1995-05-15T09:00:00",
            "place_of_birth": "Los Angeles, CA, USA",
            "latitude": "34.0522",
            "longitude": "-118.2437",
            "timezone": "America/Los_Angeles"
        }
        
        response = await async_client.post("/api/v1/persons", json=person_data)
        person = assert_response_success(response, status_code=201)
        assert person["name"] == "Jane Doe"
        assert person["email"] is None
        assert person["phone"] is None
    
    @pytest.mark.asyncio
    async def test_create_person_invalid_data(self, async_client):
        """Test creating a person with invalid data."""
        # Missing required fields
        person_data = {
            "name": "Invalid Person"
            # Missing date_of_birth, time_of_birth, etc
        }
        
        response = await async_client.post("/api/v1/persons", json=person_data)
        errors = assert_response_error(response, status_code=422)
        assert len(errors) > 0
    
    @pytest.mark.asyncio
    async def test_get_person_by_id(self, async_client, test_person):
        """Test getting a person by ID."""
        person_id = test_person.person_id
        
        response = await async_client.get(f"/api/v1/persons/{person_id}")
        person = assert_response_success(response)
        
        assert person["person_id"] == str(person_id)
        assert person["name"] == test_person.name
    
    @pytest.mark.asyncio
    async def test_get_person_not_found(self, async_client):
        """Test getting a non-existent person."""
        fake_id = uuid4()
        
        response = await async_client.get(f"/api/v1/persons/{fake_id}")
        assert_response_error(response, status_code=404)
    
    @pytest.mark.asyncio
    async def test_update_person(self, async_client, test_person):
        """Test updating a person."""
        person_id = test_person.person_id
        update_data = {
            "email": "newemail@example.com",
            "phone": "+9876543210"
        }
        
        response = await async_client.patch(f"/api/v1/persons/{person_id}", json=update_data)
        updated_person = assert_response_success(response)
        
        assert updated_person["email"] == "newemail@example.com"
        assert updated_person["phone"] == "+9876543210"
        assert updated_person["name"] == test_person.name  # Unchanged
    
    @pytest.mark.asyncio
    async def test_delete_person(self, async_client, test_organization):
        """Test deleting a person."""
        # Create a person to delete
        person_data = {
            "name": "To Delete",
            "date_of_birth": "2000-01-01",
            "time_of_birth": "2000-01-01T00:00:00",
            "place_of_birth": "Test City",
            "latitude": "0.0",
            "longitude": "0.0",
            "timezone": "UTC"
        }
        
        create_response = await async_client.post("/api/v1/persons", json=person_data)
        person = assert_response_success(create_response, status_code=201)
        person_id = person["person_id"]
        
        # Delete the person
        delete_response = await async_client.delete(f"/api/v1/persons/{person_id}")
        assert_response_success(delete_response)
        
        # Verify person is soft deleted (should return 404)
        get_response = await async_client.get(f"/api/v1/persons/{person_id}")
        assert_response_error(get_response, status_code=404)
    
    @pytest.mark.asyncio
    async def test_list_persons(self, async_client, test_organization):
        """Test listing persons with pagination."""
        # Create multiple persons
        for i in range(3):
            person_data = {
                "name": f"Test Person {i}",
                "date_of_birth": "1990-01-01",
                "time_of_birth": "1990-01-01T12:00:00",
                "place_of_birth": "Test City",
                "latitude": "0.0",
                "longitude": "0.0",
                "timezone": "UTC"
            }
            await async_client.post("/api/v1/persons", json=person_data)
        
        # List persons
        response = await async_client.get("/api/v1/persons?limit=2&skip=0")
        persons = assert_response_success(response)
        
        assert len(persons) == 2
        assert all("person_id" in p for p in persons)
    
    @pytest.mark.asyncio
    async def test_search_persons(self, async_client, test_organization):
        """Test searching persons by name."""
        # Create persons with searchable names
        names = ["Alice Smith", "Bob Smith", "Charlie Jones"]
        for name in names:
            person_data = {
                "name": name,
                "date_of_birth": "1990-01-01",
                "time_of_birth": "1990-01-01T12:00:00",
                "place_of_birth": "Test City",
                "latitude": "0.0",
                "longitude": "0.0",
                "timezone": "UTC"
            }
            await async_client.post("/api/v1/persons", json=person_data)
        
        # Search for "Smith"
        response = await async_client.get("/api/v1/persons?search=Smith")
        persons = assert_response_success(response)
        
        assert len(persons) >= 2
        assert all("Smith" in p["name"] for p in persons)
    
    @pytest.mark.asyncio
    async def test_person_with_chart_creation(self, async_client, test_organization):
        """Test creating a person and then a chart for them."""
        # Create person
        person_data = {
            "name": "Chart Test Person",
            "date_of_birth": "1985-06-15",
            "time_of_birth": "1985-06-15T14:30:00",
            "place_of_birth": "London, UK",
            "latitude": "51.5074",
            "longitude": "-0.1278",
            "timezone": "Europe/London"
        }
        
        person_response = await async_client.post("/api/v1/persons", json=person_data)
        person = assert_response_success(person_response, status_code=201)
        person_id = person["person_id"]
        
        # Create chart for person
        chart_data = {
            "person_id": person_id,
            "chart_type": "vedic",
            "house_system": "placidus",
            "ayanamsa": "lahiri",
            "calculated_at": datetime.now().isoformat(),
            "calculation_version": "1.0"
        }
        
        chart_response = await async_client.post("/api/v1/charts", json=chart_data)
        chart = assert_response_success(chart_response, status_code=201)
        
        assert chart["person_id"] == person_id
        assert chart["chart_type"] == "vedic"