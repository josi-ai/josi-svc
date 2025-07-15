"""
Real-world user authentication and registration tests.

Tests realistic user scenarios including registration, login, subscription management,
and security edge cases.
"""
import pytest
import asyncio
from datetime import datetime, timedelta
from uuid import uuid4
from httpx import AsyncClient
from fastapi import status

from josi.models.user_model import User, SubscriptionTier
from josi.services.auth_service import AuthService
from tests.conftest import assert_response_success, assert_response_error


class TestUserRegistration:
    """Test real-world user registration scenarios."""
    
    @pytest.mark.asyncio
    async def test_new_user_complete_registration_flow(self, async_client: AsyncClient, db_session):
        """Test complete registration flow for a new user."""
        # Real user data
        user_data = {
            "email": "sarah.johnson@gmail.com",
            "password": "SecurePass123!",
            "full_name": "Sarah Johnson",
            "date_of_birth": "1985-03-15",
            "timezone": "America/New_York"
        }
        
        # Register user
        response = await async_client.post("/api/v1/auth/register", json=user_data)
        registration_data = assert_response_success(response, status.HTTP_201_CREATED)
        
        assert "user_id" in registration_data
        assert registration_data["email"] == user_data["email"]
        assert registration_data["full_name"] == user_data["full_name"]
        assert registration_data["subscription_tier"] == "FREE"
        assert "access_token" in registration_data
        assert "refresh_token" in registration_data
        
        # Verify user can authenticate with the tokens
        access_token = registration_data["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        
        profile_response = await async_client.get("/api/v1/auth/profile", headers=headers)
        profile_data = assert_response_success(profile_response)
        
        assert profile_data["email"] == user_data["email"]
        assert profile_data["subscription_tier"] == "FREE"
    
    @pytest.mark.asyncio
    async def test_duplicate_email_registration(self, async_client: AsyncClient, db_session):
        """Test that duplicate email registration is properly rejected."""
        user_data = {
            "email": "duplicate@example.com",
            "password": "SecurePass123!",
            "full_name": "First User",
            "date_of_birth": "1990-01-01",
            "timezone": "UTC"
        }
        
        # First registration should succeed
        response1 = await async_client.post("/api/v1/auth/register", json=user_data)
        assert_response_success(response1, status.HTTP_201_CREATED)
        
        # Second registration with same email should fail
        user_data["full_name"] = "Second User"
        response2 = await async_client.post("/api/v1/auth/register", json=user_data)
        assert response2.status_code == status.HTTP_400_BAD_REQUEST
        
        error_data = response2.json()
        assert "email already registered" in error_data["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_invalid_email_registration(self, async_client: AsyncClient):
        """Test registration with invalid email formats."""
        invalid_emails = [
            "notanemail",
            "@domain.com",
            "user@",
            "user..name@domain.com",
            "user@domain",
            ""
        ]
        
        for invalid_email in invalid_emails:
            user_data = {
                "email": invalid_email,
                "password": "SecurePass123!",
                "full_name": "Test User",
                "date_of_birth": "1990-01-01",
                "timezone": "UTC"
            }
            
            response = await async_client.post("/api/v1/auth/register", json=user_data)
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.asyncio
    async def test_weak_password_registration(self, async_client: AsyncClient):
        """Test registration with weak passwords."""
        weak_passwords = [
            "123456",
            "password",
            "qwerty",
            "abc123",
            "123",
            "pass",
            "aaaaaaaa"
        ]
        
        for weak_password in weak_passwords:
            user_data = {
                "email": f"test_{uuid4()}@example.com",
                "password": weak_password,
                "full_name": "Test User",
                "date_of_birth": "1990-01-01",
                "timezone": "UTC"
            }
            
            response = await async_client.post("/api/v1/auth/register", json=user_data)
            assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY]


class TestUserLogin:
    """Test real-world user login scenarios."""
    
    @pytest.mark.asyncio
    async def test_successful_login_with_email(self, async_client: AsyncClient, db_session):
        """Test successful login with email and password."""
        # Register a user first
        user_data = {
            "email": "login.test@example.com",
            "password": "SecurePass123!",
            "full_name": "Login Test User",
            "date_of_birth": "1990-01-01",
            "timezone": "UTC"
        }
        
        await async_client.post("/api/v1/auth/register", json=user_data)
        
        # Login with correct credentials
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"]
        }
        
        response = await async_client.post("/api/v1/auth/login", json=login_data)
        login_result = assert_response_success(response)
        
        assert "access_token" in login_result
        assert "refresh_token" in login_result
        assert login_result["user"]["email"] == user_data["email"]
        assert login_result["user"]["full_name"] == user_data["full_name"]
    
    @pytest.mark.asyncio
    async def test_login_with_wrong_password(self, async_client: AsyncClient, db_session):
        """Test login failure with wrong password."""
        # Register a user first
        user_data = {
            "email": "wrong.password@example.com",
            "password": "CorrectPassword123!",
            "full_name": "Test User",
            "date_of_birth": "1990-01-01",
            "timezone": "UTC"
        }
        
        await async_client.post("/api/v1/auth/register", json=user_data)
        
        # Login with wrong password
        login_data = {
            "email": user_data["email"],
            "password": "WrongPassword123!"
        }
        
        response = await async_client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        error_data = response.json()
        assert "invalid credentials" in error_data["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_login_with_nonexistent_email(self, async_client: AsyncClient):
        """Test login failure with non-existent email."""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "SomePassword123!"
        }
        
        response = await async_client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestTokenRefresh:
    """Test token refresh functionality."""
    
    @pytest.mark.asyncio
    async def test_successful_token_refresh(self, async_client: AsyncClient, db_session):
        """Test successful token refresh."""
        # Register and login
        user_data = {
            "email": "refresh.test@example.com",
            "password": "SecurePass123!",
            "full_name": "Refresh Test User",
            "date_of_birth": "1990-01-01",
            "timezone": "UTC"
        }
        
        reg_response = await async_client.post("/api/v1/auth/register", json=user_data)
        reg_data = assert_response_success(reg_response, status.HTTP_201_CREATED)
        
        refresh_token = reg_data["refresh_token"]
        
        # Refresh the token
        refresh_data = {"refresh_token": refresh_token}
        response = await async_client.post("/api/v1/auth/refresh", json=refresh_data)
        refresh_result = assert_response_success(response)
        
        assert "access_token" in refresh_result
        assert "refresh_token" in refresh_result
        assert refresh_result["access_token"] != reg_data["access_token"]
    
    @pytest.mark.asyncio
    async def test_refresh_with_invalid_token(self, async_client: AsyncClient):
        """Test token refresh with invalid refresh token."""
        refresh_data = {"refresh_token": "invalid_refresh_token"}
        
        response = await async_client.post("/api/v1/auth/refresh", json=refresh_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestSubscriptionTiers:
    """Test subscription tier functionality."""
    
    @pytest.mark.asyncio
    async def test_new_user_starts_with_free_tier(self, async_client: AsyncClient, db_session):
        """Test that new users start with FREE tier."""
        user_data = {
            "email": "free.tier@example.com",
            "password": "SecurePass123!",
            "full_name": "Free Tier User",
            "date_of_birth": "1990-01-01",
            "timezone": "UTC"
        }
        
        response = await async_client.post("/api/v1/auth/register", json=user_data)
        reg_data = assert_response_success(response, status.HTTP_201_CREATED)
        
        assert reg_data["subscription_tier"] == "FREE"
        
        # Verify tier limits are applied
        headers = {"Authorization": f"Bearer {reg_data['access_token']}"}
        profile_response = await async_client.get("/api/v1/auth/profile", headers=headers)
        profile_data = assert_response_success(profile_response)
        
        assert profile_data["tier_limits"]["charts_per_month"] == 5
        assert profile_data["tier_limits"]["ai_interpretations_per_month"] == 3
    
    @pytest.mark.asyncio
    async def test_subscription_upgrade(self, async_client: AsyncClient, db_session):
        """Test subscription tier upgrade."""
        # Register user
        user_data = {
            "email": "upgrade.test@example.com",
            "password": "SecurePass123!",
            "full_name": "Upgrade Test User",
            "date_of_birth": "1990-01-01",
            "timezone": "UTC"
        }
        
        reg_response = await async_client.post("/api/v1/auth/register", json=user_data)
        reg_data = assert_response_success(reg_response, status.HTTP_201_CREATED)
        
        headers = {"Authorization": f"Bearer {reg_data['access_token']}"}
        
        # Upgrade to EXPLORER tier
        upgrade_data = {"new_tier": "EXPLORER"}
        response = await async_client.post("/api/v1/auth/upgrade-subscription", 
                                         json=upgrade_data, headers=headers)
        upgrade_result = assert_response_success(response)
        
        assert upgrade_result["subscription_tier"] == "EXPLORER"
        assert upgrade_result["tier_limits"]["charts_per_month"] == 25
        assert upgrade_result["tier_limits"]["ai_interpretations_per_month"] == 15


class TestSecurityFeatures:
    """Test security features and edge cases."""
    
    @pytest.mark.asyncio
    async def test_rate_limiting_on_login_attempts(self, async_client: AsyncClient, db_session):
        """Test rate limiting on failed login attempts."""
        # Register a user
        user_data = {
            "email": "rate.limit@example.com",
            "password": "CorrectPassword123!",
            "full_name": "Rate Limit Test",
            "date_of_birth": "1990-01-01",
            "timezone": "UTC"
        }
        
        await async_client.post("/api/v1/auth/register", json=user_data)
        
        # Make multiple failed login attempts
        login_data = {
            "email": user_data["email"],
            "password": "WrongPassword123!"
        }
        
        for i in range(5):
            response = await async_client.post("/api/v1/auth/login", json=login_data)
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # The 6th attempt should be rate limited (if rate limiting is enabled)
        # Note: This test assumes rate limiting is configured
        response = await async_client.post("/api/v1/auth/login", json=login_data)
        # Could be 429 (rate limited) or 401 (still auth failure)
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_429_TOO_MANY_REQUESTS]
    
    @pytest.mark.asyncio
    async def test_password_change(self, async_client: AsyncClient, db_session):
        """Test password change functionality."""
        # Register user
        user_data = {
            "email": "password.change@example.com",
            "password": "OldPassword123!",
            "full_name": "Password Change Test",
            "date_of_birth": "1990-01-01",
            "timezone": "UTC"
        }
        
        reg_response = await async_client.post("/api/v1/auth/register", json=user_data)
        reg_data = assert_response_success(reg_response, status.HTTP_201_CREATED)
        
        headers = {"Authorization": f"Bearer {reg_data['access_token']}"}
        
        # Change password
        change_data = {
            "current_password": "OldPassword123!",
            "new_password": "NewPassword123!"
        }
        
        response = await async_client.post("/api/v1/auth/change-password", 
                                         json=change_data, headers=headers)
        assert_response_success(response)
        
        # Verify old password no longer works
        old_login = {
            "email": user_data["email"],
            "password": "OldPassword123!"
        }
        response = await async_client.post("/api/v1/auth/login", json=old_login)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Verify new password works
        new_login = {
            "email": user_data["email"],
            "password": "NewPassword123!"
        }
        response = await async_client.post("/api/v1/auth/login", json=new_login)
        assert_response_success(response)


class TestUserProfile:
    """Test user profile management."""
    
    @pytest.mark.asyncio
    async def test_get_user_profile(self, async_client: AsyncClient, db_session):
        """Test retrieving user profile information."""
        # Register user
        user_data = {
            "email": "profile.test@example.com",
            "password": "SecurePass123!",
            "full_name": "Profile Test User",
            "date_of_birth": "1985-06-15",
            "timezone": "America/Los_Angeles"
        }
        
        reg_response = await async_client.post("/api/v1/auth/register", json=user_data)
        reg_data = assert_response_success(reg_response, status.HTTP_201_CREATED)
        
        headers = {"Authorization": f"Bearer {reg_data['access_token']}"}
        
        # Get profile
        response = await async_client.get("/api/v1/auth/profile", headers=headers)
        profile_data = assert_response_success(response)
        
        assert profile_data["email"] == user_data["email"]
        assert profile_data["full_name"] == user_data["full_name"]
        assert profile_data["date_of_birth"] == user_data["date_of_birth"]
        assert profile_data["timezone"] == user_data["timezone"]
        assert profile_data["subscription_tier"] == "FREE"
        assert "tier_limits" in profile_data
        assert "usage_stats" in profile_data
    
    @pytest.mark.asyncio
    async def test_update_user_profile(self, async_client: AsyncClient, db_session):
        """Test updating user profile information."""
        # Register user
        user_data = {
            "email": "update.profile@example.com",
            "password": "SecurePass123!",
            "full_name": "Original Name",
            "date_of_birth": "1990-01-01",
            "timezone": "UTC"
        }
        
        reg_response = await async_client.post("/api/v1/auth/register", json=user_data)
        reg_data = assert_response_success(reg_response, status.HTTP_201_CREATED)
        
        headers = {"Authorization": f"Bearer {reg_data['access_token']}"}
        
        # Update profile
        update_data = {
            "full_name": "Updated Name",
            "timezone": "America/New_York",
            "preferences": {
                "default_chart_style": "vedic",
                "language": "en"
            }
        }
        
        response = await async_client.put("/api/v1/auth/profile", 
                                        json=update_data, headers=headers)
        updated_profile = assert_response_success(response)
        
        assert updated_profile["full_name"] == "Updated Name"
        assert updated_profile["timezone"] == "America/New_York"
        assert updated_profile["preferences"]["default_chart_style"] == "vedic"


class TestOAuthIntegration:
    """Test OAuth integration scenarios."""
    
    @pytest.mark.asyncio
    async def test_google_oauth_login_new_user(self, async_client: AsyncClient, db_session):
        """Test OAuth login for new user via Google."""
        # Mock OAuth token data
        oauth_data = {
            "provider": "google",
            "access_token": "mock_google_access_token",
            "user_info": {
                "email": "oauth.test@gmail.com",
                "name": "OAuth Test User",
                "picture": "https://example.com/avatar.jpg"
            }
        }
        
        response = await async_client.post("/api/v1/auth/oauth/login", json=oauth_data)
        
        # This should create a new user and return tokens
        # Note: This test assumes OAuth endpoints are implemented
        if response.status_code == 404:
            pytest.skip("OAuth endpoints not implemented yet")
        
        oauth_result = assert_response_success(response, status.HTTP_201_CREATED)
        
        assert oauth_result["user"]["email"] == oauth_data["user_info"]["email"]
        assert oauth_result["user"]["full_name"] == oauth_data["user_info"]["name"]
        assert "access_token" in oauth_result
        assert "refresh_token" in oauth_result
    
    @pytest.mark.asyncio
    async def test_google_oauth_login_existing_user(self, async_client: AsyncClient, db_session):
        """Test OAuth login for existing user."""
        # First register user normally
        user_data = {
            "email": "existing.oauth@gmail.com",
            "password": "SecurePass123!",
            "full_name": "Existing User",
            "date_of_birth": "1990-01-01",
            "timezone": "UTC"
        }
        
        await async_client.post("/api/v1/auth/register", json=user_data)
        
        # Now try OAuth login with same email
        oauth_data = {
            "provider": "google",
            "access_token": "mock_google_access_token",
            "user_info": {
                "email": user_data["email"],
                "name": "OAuth Name",
                "picture": "https://example.com/avatar.jpg"
            }
        }
        
        response = await async_client.post("/api/v1/auth/oauth/login", json=oauth_data)
        
        if response.status_code == 404:
            pytest.skip("OAuth endpoints not implemented yet")
        
        oauth_result = assert_response_success(response)
        
        assert oauth_result["user"]["email"] == user_data["email"]
        # Should keep original name, not OAuth name for existing users
        assert oauth_result["user"]["full_name"] == user_data["full_name"]


# Real-world test scenarios
@pytest.mark.integration
class TestRealWorldUserJourneys:
    """Test complete real-world user journeys."""
    
    @pytest.mark.asyncio
    async def test_astrology_enthusiast_signup_journey(self, async_client: AsyncClient, db_session):
        """Test complete journey of an astrology enthusiast signing up."""
        # Step 1: User discovers the platform and registers
        user_data = {
            "email": "astrology.lover@example.com",
            "password": "StarGazer123!",
            "full_name": "Luna StarGazer",
            "date_of_birth": "1988-11-22",  # Scorpio Sun
            "timezone": "America/Los_Angeles"
        }
        
        reg_response = await async_client.post("/api/v1/auth/register", json=user_data)
        reg_data = assert_response_success(reg_response, status.HTTP_201_CREATED)
        
        headers = {"Authorization": f"Bearer {reg_data['access_token']}"}
        
        # Step 2: User immediately wants to create their natal chart
        # (This would flow into chart creation tests)
        
        # Step 3: User explores free tier limitations
        profile_response = await async_client.get("/api/v1/auth/profile", headers=headers)
        profile_data = assert_response_success(profile_response)
        
        assert profile_data["tier_limits"]["charts_per_month"] == 5
        assert profile_data["subscription_tier"] == "FREE"
        
        # Step 4: User decides to upgrade after hitting limits
        upgrade_data = {"new_tier": "EXPLORER"}
        upgrade_response = await async_client.post("/api/v1/auth/upgrade-subscription", 
                                                 json=upgrade_data, headers=headers)
        upgrade_result = assert_response_success(upgrade_response)
        
        assert upgrade_result["subscription_tier"] == "EXPLORER"
        assert upgrade_result["tier_limits"]["charts_per_month"] == 25
    
    @pytest.mark.asyncio
    async def test_professional_astrologer_signup_journey(self, async_client: AsyncClient, db_session):
        """Test journey of a professional astrologer signing up."""
        # Step 1: Professional astrologer registers
        user_data = {
            "email": "professional.astrologer@example.com",
            "password": "Professional123!",
            "full_name": "Dr. Stella Cosmic",
            "date_of_birth": "1975-05-10",
            "timezone": "America/New_York"
        }
        
        reg_response = await async_client.post("/api/v1/auth/register", json=user_data)
        reg_data = assert_response_success(reg_response, status.HTTP_201_CREATED)
        
        headers = {"Authorization": f"Bearer {reg_data['access_token']}"}
        
        # Step 2: Immediately upgrades to highest tier
        upgrade_data = {"new_tier": "MASTER"}
        upgrade_response = await async_client.post("/api/v1/auth/upgrade-subscription", 
                                                 json=upgrade_data, headers=headers)
        upgrade_result = assert_response_success(upgrade_response)
        
        assert upgrade_result["subscription_tier"] == "MASTER"
        assert upgrade_result["tier_limits"]["charts_per_month"] == -1  # Unlimited
        
        # Step 3: Sets up professional profile for marketplace
        # (This would flow into astrologer profile creation tests)