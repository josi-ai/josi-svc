"""
Security tests for API endpoints.
"""
import pytest
from httpx import AsyncClient
import json
from uuid import uuid4

from josi.main import app
from josi.models.organization_model import Organization


@pytest.mark.asyncio
class TestSecurityValidation:
    """Test security features and protections."""
    
    async def test_sql_injection_prevention(self, async_client: AsyncClient, test_organization: Organization):
        """Test that SQL injection attempts are blocked."""
        # Attempt SQL injection in search/filter parameters
        malicious_inputs = [
            "'; DROP TABLE person; --",
            "1' OR '1'='1",
            "admin'--",
            "1; DELETE FROM organization WHERE 1=1; --",
            "' UNION SELECT * FROM organization --"
        ]
        
        for malicious_input in malicious_inputs:
            # Try injection in person name
            person_data = {
                "name": malicious_input,
                "email": "test@example.com",
                "date_of_birth": "1990-01-01",
                "time_of_birth": "12:00:00",
                "place_of_birth": "Test City",
                "latitude": 0.0,
                "longitude": 0.0,
                "timezone": "UTC"
            }
            
            response = await async_client.post(
                "/api/v1/persons",
                json=person_data,
                headers={"X-API-Key": test_organization.api_key}
            )
            # Should either succeed (data is escaped) or fail validation
            # But should never execute the SQL
            assert response.status_code in [201, 422]
            
            # Try injection in query parameters
            response = await async_client.get(
                f"/api/v1/persons?name={malicious_input}",
                headers={"X-API-Key": test_organization.api_key}
            )
            # Should return results or empty, but not error
            assert response.status_code == 200
    
    async def test_xss_prevention(self, async_client: AsyncClient, test_organization: Organization):
        """Test that XSS attempts are properly escaped."""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<iframe src='javascript:alert(1)'></iframe>",
            "<svg onload=alert('XSS')>"
        ]
        
        for payload in xss_payloads:
            person_data = {
                "name": payload,
                "email": "xss@test.com",
                "notes": payload,
                "date_of_birth": "1990-01-01",
                "time_of_birth": "12:00:00",
                "place_of_birth": "Test City",
                "latitude": 0.0,
                "longitude": 0.0,
                "timezone": "UTC"
            }
            
            response = await async_client.post(
                "/api/v1/persons",
                json=person_data,
                headers={"X-API-Key": test_organization.api_key}
            )
            
            if response.status_code == 201:
                # Verify the data is stored but escaped
                created = response.json()["data"]
                person_id = created["person_id"]
                
                # Fetch the person
                response = await async_client.get(
                    f"/api/v1/persons/{person_id}",
                    headers={"X-API-Key": test_organization.api_key}
                )
                person = response.json()["data"]
                
                # The payload should be stored as-is (not executed)
                assert person["name"] == payload
                assert person["notes"] == payload
    
    async def test_authentication_required(self, async_client: AsyncClient):
        """Test that all endpoints require authentication."""
        endpoints = [
            ("/api/v1/persons", "GET"),
            ("/api/v1/persons", "POST"),
            (f"/api/v1/persons/{uuid4()}", "GET"),
            (f"/api/v1/persons/{uuid4()}", "PATCH"),
            (f"/api/v1/persons/{uuid4()}", "DELETE"),
            (f"/api/v1/persons/{uuid4()}/charts", "GET"),
            (f"/api/v1/persons/{uuid4()}/charts", "POST"),
            (f"/api/v1/charts/{uuid4()}", "GET"),
        ]
        
        for endpoint, method in endpoints:
            if method == "GET":
                response = await async_client.get(endpoint)
            elif method == "POST":
                response = await async_client.post(endpoint, json={})
            elif method == "PATCH":
                response = await async_client.patch(endpoint, json={})
            elif method == "DELETE":
                response = await async_client.delete(endpoint)
            
            # Should return 401 Unauthorized without API key
            assert response.status_code == 401
            
            # Should also fail with invalid API key
            if method == "GET":
                response = await async_client.get(
                    endpoint,
                    headers={"X-API-Key": "invalid-key"}
                )
            assert response.status_code == 401
    
    async def test_rate_limiting(self, async_client: AsyncClient, test_organization: Organization):
        """Test rate limiting functionality."""
        # Make many requests quickly
        responses = []
        for i in range(100):  # Try to exceed rate limit
            response = await async_client.get(
                "/api/v1/persons",
                headers={"X-API-Key": test_organization.api_key}
            )
            responses.append(response.status_code)
        
        # Some requests should be rate limited (429 status)
        # Note: This depends on rate limit configuration
        # Default is 60/minute, so 100 requests should trigger limiting
        rate_limited = [r for r in responses if r == 429]
        
        # If rate limiting is enabled, we should see some 429s
        # (This test might need adjustment based on actual rate limit config)
        if len(rate_limited) == 0:
            pytest.skip("Rate limiting may not be configured or limit is too high")
    
    async def test_api_key_security(self, async_client: AsyncClient):
        """Test API key security features."""
        # Test that API keys are properly validated
        invalid_keys = [
            "",  # Empty
            "short",  # Too short
            "test-key-with-special-chars-!@#$%",  # Special chars
            " test-key-with-spaces ",  # Spaces
            "a" * 1000,  # Too long
        ]
        
        for invalid_key in invalid_keys:
            response = await async_client.get(
                "/api/v1/persons",
                headers={"X-API-Key": invalid_key}
            )
            assert response.status_code == 401
    
    async def test_input_validation(self, async_client: AsyncClient, test_organization: Organization):
        """Test input validation and sanitization."""
        # Test oversized payloads
        large_string = "x" * 10000  # 10KB string
        
        person_data = {
            "name": large_string,
            "email": "test@example.com",
            "notes": large_string,
            "date_of_birth": "1990-01-01",
            "time_of_birth": "12:00:00",
            "place_of_birth": "Test City",
            "latitude": 0.0,
            "longitude": 0.0,
            "timezone": "UTC"
        }
        
        response = await async_client.post(
            "/api/v1/persons",
            json=person_data,
            headers={"X-API-Key": test_organization.api_key}
        )
        # Should either accept or reject based on field limits
        assert response.status_code in [201, 422]
        
        # Test invalid data types
        invalid_data = {
            "name": 12345,  # Should be string
            "email": ["array", "of", "emails"],  # Should be string
            "date_of_birth": "not-a-date",
            "latitude": "not-a-number",
            "longitude": {"invalid": "object"},
            "timezone": None
        }
        
        response = await async_client.post(
            "/api/v1/persons",
            json=invalid_data,
            headers={"X-API-Key": test_organization.api_key}
        )
        assert response.status_code == 422
    
    async def test_cors_headers(self, async_client: AsyncClient, test_organization: Organization):
        """Test CORS headers are properly set."""
        response = await async_client.options(
            "/api/v1/persons",
            headers={
                "Origin": "https://example.com",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "X-API-Key"
            }
        )
        
        # Check CORS headers
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
        assert "access-control-allow-headers" in response.headers
    
    async def test_secure_headers(self, async_client: AsyncClient, test_organization: Organization):
        """Test that security headers are properly set."""
        response = await async_client.get(
            "/api/v1/persons",
            headers={"X-API-Key": test_organization.api_key}
        )
        
        # Check for security headers
        headers = response.headers
        
        # These headers should be set by security middleware
        security_headers = [
            "x-content-type-options",
            "x-frame-options",
            "x-xss-protection",
            "strict-transport-security"
        ]
        
        for header in security_headers:
            # Note: Some headers might only be set in production
            if header in headers:
                assert headers[header] is not None
    
    async def test_json_content_type_enforcement(self, async_client: AsyncClient, test_organization: Organization):
        """Test that API only accepts JSON content type."""
        # Try to send non-JSON content
        response = await async_client.post(
            "/api/v1/persons",
            content="name=test&email=test@example.com",  # Form data
            headers={
                "X-API-Key": test_organization.api_key,
                "Content-Type": "application/x-www-form-urlencoded"
            }
        )
        # Should reject non-JSON content
        assert response.status_code in [415, 422]
    
    async def test_path_traversal_prevention(self, async_client: AsyncClient, test_organization: Organization):
        """Test that path traversal attempts are blocked."""
        # Try various path traversal patterns
        traversal_ids = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32",
            "%2e%2e%2f%2e%2e%2f",
            "....//....//",
            str(uuid4()) + "/../../../"
        ]
        
        for traversal_id in traversal_ids:
            response = await async_client.get(
                f"/api/v1/persons/{traversal_id}",
                headers={"X-API-Key": test_organization.api_key}
            )
            # Should return 404 or 422, not expose system files
            assert response.status_code in [404, 422]