"""Integration tests for GraphQL API."""
import pytest
from uuid import uuid4

from tests.conftest import assert_response_success


@pytest.mark.integration
class TestGraphQLAPIFixed:
    """Integration tests for GraphQL API."""
    
    @pytest.mark.asyncio
    async def test_graphql_query_persons(self, async_client, test_person):
        """Test querying persons via GraphQL."""
        query = """
        query {
            persons(limit: 10) {
                personId
                name
                email
                dateOfBirth
                placeOfBirth
            }
        }
        """
        
        response = await async_client.post(
            "/graphql",
            json={"query": query}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "persons" in data["data"]
        assert len(data["data"]["persons"]) > 0
    
    @pytest.mark.asyncio
    async def test_graphql_query_person_by_id(self, async_client, test_person):
        """Test querying a specific person by ID."""
        query = """
        query GetPerson($personId: UUID!) {
            person(personId: $personId) {
                personId
                name
                email
                dateOfBirth
                timeOfBirth
                placeOfBirth
                latitude
                longitude
                timezone
            }
        }
        """
        
        variables = {"personId": str(test_person.person_id)}
        
        response = await async_client.post(
            "/graphql",
            json={"query": query, "variables": variables}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "person" in data["data"]
        person = data["data"]["person"]
        assert person["personId"] == str(test_person.person_id)
        assert person["name"] == test_person.name
    
    @pytest.mark.asyncio
    async def test_graphql_mutation_create_person(self, async_client, test_organization):
        """Test creating a person via GraphQL mutation."""
        mutation = """
        mutation CreatePerson($person: PersonCreateInput!) {
            createPerson(person: $person) {
                personId
                name
                email
                dateOfBirth
                placeOfBirth
            }
        }
        """
        
        variables = {
            "person": {
                "name": "GraphQL Test Person",
                "dateOfBirth": "1990-01-01",
                "timeOfBirth": "1990-01-01T12:00:00",
                "placeOfBirth": "New York, NY, USA",
                "latitude": 40.7128,
                "longitude": -74.0060,
                "timezone": "America/New_York",
                "email": "graphql@example.com"
            }
        }
        
        response = await async_client.post(
            "/graphql",
            json={"query": mutation, "variables": variables}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "createPerson" in data["data"]
        person = data["data"]["createPerson"]
        assert person["name"] == "GraphQL Test Person"
        assert person["email"] == "graphql@example.com"
    
    @pytest.mark.asyncio
    async def test_graphql_query_organization(self, async_client, test_organization):
        """Test querying current organization."""
        query = """
        query {
            currentOrganization {
                organizationId
                name
                slug
                isActive
                planType
                monthlyApiLimit
                currentMonthUsage
            }
        }
        """
        
        response = await async_client.post(
            "/graphql",
            json={"query": query}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "currentOrganization" in data["data"]
        org = data["data"]["currentOrganization"]
        assert org["organizationId"] == str(test_organization.organization_id)
        assert org["name"] == test_organization.name
        assert org["isActive"] is True
    
    @pytest.mark.asyncio
    async def test_graphql_query_charts(self, async_client, test_person):
        """Test querying charts for a person."""
        # First create a chart
        chart_mutation = """
        mutation CreateChart($chart: ChartCreateInput!) {
            createChart(chart: $chart) {
                chartId
                personId
                chartType
                houseSystem
                ayanamsa
            }
        }
        """
        
        chart_variables = {
            "chart": {
                "personId": str(test_person.person_id),
                "chartType": "vedic",
                "houseSystem": "placidus",
                "ayanamsa": "lahiri",
                "calculatedAt": "2024-01-01T12:00:00",
                "calculationVersion": "1.0"
            }
        }
        
        # Create chart
        await async_client.post(
            "/graphql",
            json={"query": chart_mutation, "variables": chart_variables}
        )
        
        # Query charts
        query = """
        query GetCharts($personId: UUID!) {
            chartsByPerson(personId: $personId) {
                chartId
                personId
                chartType
                houseSystem
                ayanamsa
                calculatedAt
            }
        }
        """
        
        variables = {"personId": str(test_person.person_id)}
        
        response = await async_client.post(
            "/graphql",
            json={"query": query, "variables": variables}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "chartsByPerson" in data["data"]
        charts = data["data"]["chartsByPerson"]
        assert len(charts) > 0
        assert all(c["personId"] == str(test_person.person_id) for c in charts)
    
    @pytest.mark.asyncio
    async def test_graphql_error_handling(self, async_client):
        """Test GraphQL error handling."""
        # Invalid query
        query = """
        query {
            invalidField {
                id
            }
        }
        """
        
        response = await async_client.post(
            "/graphql",
            json={"query": query}
        )
        
        assert response.status_code == 200  # GraphQL returns 200 even for errors
        data = response.json()
        assert "errors" in data
        assert len(data["errors"]) > 0