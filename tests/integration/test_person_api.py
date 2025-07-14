"""Integration tests for Person API endpoints."""
import pytest
from uuid import uuid4
from datetime import datetime

from tests.conftest import assert_response_success, assert_response_error, generate_person_data


@pytest.mark.integration
class TestPersonAPI:
    """Integration tests for Person API endpoints."""
    
    @pytest.mark.asyncio
    async def test_create_person_full_flow(self, async_client, test_organization):
        """Test creating a person with full data flow."""
        # Create person data
        person_data = {
            "first_name": "John",
            "last_name": "Doe",
            "birth_date": "1990-01-01",
            "birth_time": "12:00:00",
            "birth_place": "New York, NY, USA",
            "email": "john.doe@example.com",
            "phone": "+1234567890"
        }
        
        # Send POST request
        response = await async_client.post("/api/v1/persons", json=person_data)
        
        # Verify response
        person = assert_response_success(response, status_code=201)
        assert person["first_name"] == "John"
        assert person["last_name"] == "Doe"
        assert person["email"] == "john.doe@example.com"
        assert person["organization_id"] == str(test_organization.organization_id)
        
        # Verify geocoding was performed
        assert person["latitude"] is not None
        assert person["longitude"] is not None
        assert person["timezone"] is not None
        
        # Verify person was created in database
        person_id = person["person_id"]
        get_response = await async_client.get(f"/api/v1/persons/{person_id}")
        retrieved_person = assert_response_success(get_response)
        assert retrieved_person["person_id"] == person_id
    
    @pytest.mark.asyncio
    async def test_create_person_minimal_data(self, async_client):
        """Test creating a person with minimal required data."""
        person_data = {
            "first_name": "Jane",
            "birth_date": "1995-05-15"
        }
        
        response = await async_client.post("/api/v1/persons", json=person_data)
        
        person = assert_response_success(response, status_code=201)
        assert person["first_name"] == "Jane"
        assert person["last_name"] is None
        assert person["birth_time"] is None
        assert person["latitude"] is None
        assert person["longitude"] is None
    
    @pytest.mark.asyncio
    async def test_create_person_invalid_data(self, async_client):
        """Test creating a person with invalid data."""
        # Missing required field
        response = await async_client.post("/api/v1/persons", json={
            "last_name": "Doe"
        })
        assert response.status_code == 422
        
        # Invalid email format
        response = await async_client.post("/api/v1/persons", json={
            "first_name": "Test",
            "birth_date": "2000-01-01",
            "email": "invalid-email"
        })
        assert response.status_code == 422
        
        # Invalid date format
        response = await async_client.post("/api/v1/persons", json={
            "first_name": "Test",
            "birth_date": "invalid-date"
        })
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_get_person(self, async_client, test_person):
        """Test getting a person by ID."""
        response = await async_client.get(f"/api/v1/persons/{test_person.person_id}")
        
        person = assert_response_success(response)
        assert person["person_id"] == str(test_person.person_id)
        assert person["first_name"] == test_person.first_name
        assert person["last_name"] == test_person.last_name
    
    @pytest.mark.asyncio
    async def test_get_person_not_found(self, async_client):
        """Test getting a non-existent person."""
        fake_id = uuid4()
        response = await async_client.get(f"/api/v1/persons/{fake_id}")
        
        assert response.status_code == 404
        errors = assert_response_error(response, status_code=404)
        assert "not found" in response.json()["message"].lower()
    
    @pytest.mark.asyncio
    async def test_update_person(self, async_client, test_person):
        """Test updating a person."""
        update_data = {
            "email": "updated.email@example.com",
            "phone": "+9876543210"
        }
        
        response = await async_client.put(
            f"/api/v1/persons/{test_person.person_id}",
            json=update_data
        )
        
        person = assert_response_success(response)
        assert person["person_id"] == str(test_person.person_id)
        assert person["email"] == "updated.email@example.com"
        assert person["phone"] == "+9876543210"
        # Original data should remain unchanged
        assert person["first_name"] == test_person.first_name
        assert person["last_name"] == test_person.last_name
    
    @pytest.mark.asyncio
    async def test_update_person_birth_place(self, async_client, test_person):
        """Test updating a person's birth place triggers geocoding."""
        update_data = {
            "birth_place": "Los Angeles, CA, USA"
        }
        
        response = await async_client.put(
            f"/api/v1/persons/{test_person.person_id}",
            json=update_data
        )
        
        person = assert_response_success(response)
        assert person["birth_place"] == "Los Angeles, CA, USA"
        # Verify coordinates were updated
        assert person["latitude"] != test_person.latitude
        assert person["longitude"] != test_person.longitude
        assert person["timezone"] != test_person.timezone
    
    @pytest.mark.asyncio
    async def test_delete_person(self, async_client, test_person):
        """Test deleting a person."""
        # Delete the person
        response = await async_client.delete(f"/api/v1/persons/{test_person.person_id}")
        assert_response_success(response)
        
        # Verify person is deleted (should return 404)
        get_response = await async_client.get(f"/api/v1/persons/{test_person.person_id}")
        assert get_response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_list_persons(self, async_client, db_session, test_organization):
        """Test listing persons with pagination."""
        # Create multiple persons
        for i in range(5):
            person_data = generate_person_data()
            person_data["first_name"] = f"Person{i}"
            await async_client.post("/api/v1/persons", json=person_data)
        
        # Test default listing
        response = await async_client.get("/api/v1/persons")
        persons = assert_response_success(response)
        assert isinstance(persons, list)
        assert len(persons) >= 5
        
        # Test with pagination
        response = await async_client.get("/api/v1/persons?skip=0&limit=3")
        persons = assert_response_success(response)
        assert len(persons) == 3
        
        # Test second page
        response = await async_client.get("/api/v1/persons?skip=3&limit=3")
        persons = assert_response_success(response)
        assert len(persons) >= 2
    
    @pytest.mark.asyncio
    async def test_list_persons_search(self, async_client, db_session, test_organization):
        """Test searching persons."""
        # Create persons with specific names
        await async_client.post("/api/v1/persons", json={
            "first_name": "Alice",
            "last_name": "Anderson",
            "birth_date": "1990-01-01",
            "email": "alice@example.com"
        })
        
        await async_client.post("/api/v1/persons", json={
            "first_name": "Bob",
            "last_name": "Brown",
            "birth_date": "1985-05-15",
            "email": "bob@example.com"
        })
        
        # Search by name
        response = await async_client.get("/api/v1/persons?search=Alice")
        persons = assert_response_success(response)
        assert len(persons) >= 1
        assert any(p["first_name"] == "Alice" for p in persons)
        
        # Search by email
        response = await async_client.get("/api/v1/persons?search=bob@example.com")
        persons = assert_response_success(response)
        assert len(persons) >= 1
        assert any(p["email"] == "bob@example.com" for p in persons)
    
    @pytest.mark.asyncio
    async def test_unauthorized_access(self, async_client):
        """Test accessing API without proper authorization."""
        # Remove API key header
        headers = async_client.headers.copy()
        del headers["X-API-Key"]
        
        # Try to create person without auth
        response = await async_client.post(
            "/api/v1/persons",
            json={"first_name": "Test", "birth_date": "2000-01-01"},
            headers=headers
        )
        assert response.status_code == 401
        
        # Try with invalid API key
        headers["X-API-Key"] = "invalid-api-key"
        response = await async_client.get("/api/v1/persons", headers=headers)
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_cross_organization_isolation(self, async_client, db_session, test_person):
        """Test that organizations cannot access each other's data."""
        # Create another organization
        from josi.models.organization_model import Organization
        other_org = Organization(
            organization_id=uuid4(),
            name="Other Organization",
            api_key=f"other-api-key-{uuid4()}",
            is_active=True
        )
        db_session.add(other_org)
        await db_session.commit()
        
        # Try to access test_person with other org's API key
        headers = {"X-API-Key": other_org.api_key}
        response = await async_client.get(
            f"/api/v1/persons/{test_person.person_id}",
            headers=headers
        )
        
        # Should return 404 (not found) rather than 403 (forbidden)
        # to avoid leaking information about existence
        assert response.status_code == 404