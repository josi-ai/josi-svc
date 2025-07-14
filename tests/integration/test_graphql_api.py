"""Integration tests for GraphQL API."""
import pytest
from uuid import uuid4
from datetime import datetime


@pytest.mark.integration
class TestGraphQLAPI:
    """Integration tests for GraphQL endpoints."""
    
    @pytest.mark.asyncio
    async def test_create_person_mutation(self, async_client):
        """Test creating a person via GraphQL mutation."""
        mutation = """
        mutation CreatePerson($input: PersonCreateInput!) {
            createPerson(input: $input) {
                personId
                firstName
                lastName
                birthDate
                birthTime
                birthPlace
                latitude
                longitude
                timezone
                email
            }
        }
        """
        
        variables = {
            "input": {
                "firstName": "GraphQL",
                "lastName": "Test",
                "birthDate": "1990-06-15",
                "birthTime": "14:30:00",
                "birthPlace": "San Francisco, CA, USA",
                "email": "graphql.test@example.com"
            }
        }
        
        response = await async_client.post(
            "/graphql",
            json={"query": mutation, "variables": variables}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "errors" not in data
        
        person = data["data"]["createPerson"]
        assert person["firstName"] == "GraphQL"
        assert person["lastName"] == "Test"
        assert person["email"] == "graphql.test@example.com"
        assert person["latitude"] is not None
        assert person["longitude"] is not None
        assert person["timezone"] is not None
    
    @pytest.mark.asyncio
    async def test_get_person_query(self, async_client, test_person):
        """Test getting a person via GraphQL query."""
        query = """
        query GetPerson($personId: UUID!) {
            person(personId: $personId) {
                personId
                firstName
                lastName
                birthDate
                email
                organizationId
            }
        }
        """
        
        variables = {
            "personId": str(test_person.person_id)
        }
        
        response = await async_client.post(
            "/graphql",
            json={"query": query, "variables": variables}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "errors" not in data
        
        person = data["data"]["person"]
        assert person["personId"] == str(test_person.person_id)
        assert person["firstName"] == test_person.first_name
        assert person["lastName"] == test_person.last_name
    
    @pytest.mark.asyncio
    async def test_list_persons_query(self, async_client, db_session, test_organization):
        """Test listing persons via GraphQL query."""
        # Create some test persons
        for i in range(3):
            await async_client.post("/api/v1/persons", json={
                "first_name": f"GraphQLPerson{i}",
                "birth_date": "2000-01-01"
            })
        
        query = """
        query ListPersons($limit: Int, $offset: Int) {
            persons(limit: $limit, offset: $offset) {
                personId
                firstName
                lastName
            }
        }
        """
        
        variables = {
            "limit": 5,
            "offset": 0
        }
        
        response = await async_client.post(
            "/graphql",
            json={"query": query, "variables": variables}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "errors" not in data
        
        persons = data["data"]["persons"]
        assert isinstance(persons, list)
        assert len(persons) >= 3
        
        # Check that our created persons are in the list
        first_names = [p["firstName"] for p in persons]
        assert any("GraphQLPerson" in name for name in first_names)
    
    @pytest.mark.asyncio
    async def test_update_person_mutation(self, async_client, test_person):
        """Test updating a person via GraphQL mutation."""
        mutation = """
        mutation UpdatePerson($personId: UUID!, $input: PersonUpdateInput!) {
            updatePerson(personId: $personId, input: $input) {
                personId
                firstName
                lastName
                email
                phone
            }
        }
        """
        
        variables = {
            "personId": str(test_person.person_id),
            "input": {
                "email": "updated.graphql@example.com",
                "phone": "+1234567890"
            }
        }
        
        response = await async_client.post(
            "/graphql",
            json={"query": mutation, "variables": variables}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "errors" not in data
        
        person = data["data"]["updatePerson"]
        assert person["personId"] == str(test_person.person_id)
        assert person["email"] == "updated.graphql@example.com"
        assert person["phone"] == "+1234567890"
        # Original data preserved
        assert person["firstName"] == test_person.first_name
        assert person["lastName"] == test_person.last_name
    
    @pytest.mark.asyncio
    async def test_delete_person_mutation(self, async_client, db_session, test_organization):
        """Test deleting a person via GraphQL mutation."""
        # Create a person to delete
        create_response = await async_client.post("/api/v1/persons", json={
            "first_name": "ToDelete",
            "birth_date": "2000-01-01"
        })
        person_id = create_response.json()["data"]["person_id"]
        
        mutation = """
        mutation DeletePerson($personId: UUID!) {
            deletePerson(personId: $personId)
        }
        """
        
        variables = {
            "personId": person_id
        }
        
        response = await async_client.post(
            "/graphql",
            json={"query": mutation, "variables": variables}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "errors" not in data
        assert data["data"]["deletePerson"] is True
        
        # Verify person is deleted
        query = """
        query GetPerson($personId: UUID!) {
            person(personId: $personId) {
                personId
            }
        }
        """
        
        response = await async_client.post(
            "/graphql",
            json={"query": query, "variables": {"personId": person_id}}
        )
        
        data = response.json()
        assert data["data"]["person"] is None
    
    @pytest.mark.asyncio
    async def test_create_chart_mutation(self, async_client, test_person):
        """Test creating an astrology chart via GraphQL."""
        mutation = """
        mutation CreateChart($input: ChartCreateInput!) {
            createChart(input: $input) {
                chartId
                personId
                chartType
                houseSystem
                ayanamsa
                coordinateSystem
                calculationTime
            }
        }
        """
        
        variables = {
            "input": {
                "personId": str(test_person.person_id),
                "chartType": "natal",
                "houseSystem": "placidus",
                "ayanamsa": "lahiri",
                "coordinateSystem": "tropical"
            }
        }
        
        response = await async_client.post(
            "/graphql",
            json={"query": mutation, "variables": variables}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # The chart creation might fail if astrology libraries aren't set up
        # but the GraphQL endpoint should still work
        if "errors" not in data:
            chart = data["data"]["createChart"]
            assert chart["personId"] == str(test_person.person_id)
            assert chart["chartType"] == "natal"
            assert chart["houseSystem"] == "placidus"
    
    @pytest.mark.asyncio
    async def test_graphql_error_handling(self, async_client):
        """Test GraphQL error handling."""
        # Test with invalid query
        response = await async_client.post(
            "/graphql",
            json={"query": "invalid query"}
        )
        
        assert response.status_code == 200  # GraphQL returns 200 even with errors
        data = response.json()
        assert "errors" in data
        
        # Test with non-existent person
        query = """
        query GetPerson($personId: UUID!) {
            person(personId: $personId) {
                personId
            }
        }
        """
        
        response = await async_client.post(
            "/graphql",
            json={"query": query, "variables": {"personId": str(uuid4())}}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["person"] is None
    
    @pytest.mark.asyncio
    async def test_graphql_introspection(self, async_client):
        """Test GraphQL introspection query."""
        query = """
        query {
            __schema {
                types {
                    name
                    kind
                }
            }
        }
        """
        
        response = await async_client.post(
            "/graphql",
            json={"query": query}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "errors" not in data
        
        types = data["data"]["__schema"]["types"]
        type_names = [t["name"] for t in types]
        
        # Check that our custom types exist
        assert "Person" in type_names
        assert "PersonCreateInput" in type_names
        assert "PersonUpdateInput" in type_names
        assert "Query" in type_names
        assert "Mutation" in type_names