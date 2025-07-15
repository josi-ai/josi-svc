"""
Real-world astrologer marketplace and consultation booking tests.

Tests the complete astrologer marketplace flow including astrologer registration,
profile setup, consultation booking, video sessions, and payment processing.
"""
import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4
from httpx import AsyncClient
from fastapi import status
from unittest.mock import AsyncMock, patch

from tests.conftest import assert_response_success, assert_response_error


class TestAstrologerRegistration:
    """Test astrologer registration and profile setup."""
    
    @pytest.mark.asyncio
    async def test_complete_astrologer_registration_flow(self, async_client: AsyncClient, db_session):
        """Test complete flow of astrologer registration and profile setup."""
        
        # Step 1: Register as a regular user first
        user_data = {
            "email": "dr.astrologer@example.com",
            "password": "SecurePass123!",
            "full_name": "Dr. Sarah Cosmic",
            "date_of_birth": "1975-05-15",
            "timezone": "America/New_York"
        }
        
        user_response = await async_client.post("/api/v1/auth/register", json=user_data)
        
        if user_response.status_code == 404:
            pytest.skip("Authentication endpoints not implemented")
        
        user_data_result = assert_response_success(user_response, status.HTTP_201_CREATED)
        headers = {"Authorization": f"Bearer {user_data_result['access_token']}"}
        
        # Step 2: Apply to become an astrologer
        astrologer_application = {
            "professional_name": "Dr. Sarah Cosmic",
            "bio": "Professional Vedic astrologer with 15+ years of experience. Specializing in career guidance, relationship compatibility, and spiritual growth. PhD in Philosophy with focus on ancient wisdom traditions.",
            "specializations": ["vedic", "career_guidance", "relationships"],
            "experience_years": 15,
            "certifications": [
                "Certified Vedic Astrologer - American Institute of Vedic Studies",
                "PhD Philosophy - Harvard University",
                "Jyotish Acharya - Council of Vedic Astrology"
            ],
            "consultation_types": ["video", "chat", "email"],
            "languages": ["English", "Hindi", "Sanskrit"],
            "hourly_rate": "150.00",
            "availability": {
                "timezone": "America/New_York",
                "weekly_schedule": {
                    "monday": {"start": "09:00", "end": "17:00"},
                    "tuesday": {"start": "09:00", "end": "17:00"},
                    "wednesday": {"start": "09:00", "end": "17:00"},
                    "thursday": {"start": "09:00", "end": "17:00"},
                    "friday": {"start": "09:00", "end": "15:00"},
                    "saturday": {"start": "10:00", "end": "14:00"},
                    "sunday": {"available": False}
                }
            },
            "portfolio": {
                "website": "https://drsarahcosmic.com",
                "sample_readings": [
                    "https://example.com/sample1.pdf",
                    "https://example.com/sample2.pdf"
                ],
                "testimonials": [
                    {
                        "text": "Dr. Sarah's reading was incredibly accurate and insightful. She helped me understand my career path much better.",
                        "author": "Anonymous Client",
                        "rating": 5
                    }
                ]
            }
        }
        
        # Submit astrologer application
        astrologer_response = await async_client.post(
            "/api/v1/astrologers/apply", 
            json=astrologer_application, 
            headers=headers
        )
        
        if astrologer_response.status_code == 404:
            pytest.skip("Astrologer endpoints not implemented")
        
        astrologer_data = assert_response_success(astrologer_response, status.HTTP_201_CREATED)
        
        # Verify astrologer profile was created
        assert "astrologer_id" in astrologer_data
        assert astrologer_data["professional_name"] == "Dr. Sarah Cosmic"
        assert astrologer_data["status"] == "pending_verification"
        assert astrologer_data["hourly_rate"] == "150.00"
        assert len(astrologer_data["specializations"]) == 3
        
        return astrologer_data["astrologer_id"], headers
    
    @pytest.mark.asyncio
    async def test_astrologer_verification_process(self, async_client: AsyncClient, db_session):
        """Test astrologer verification and approval process."""
        
        # Register astrologer (using helper method)
        try:
            astrologer_id, headers = await self.test_complete_astrologer_registration_flow(async_client, db_session)
        except pytest.skip.Exception:
            pytest.skip("Prerequisites not available")
        
        # Admin verifies the astrologer (this would normally be done by admin)
        verification_data = {
            "astrologer_id": astrologer_id,
            "verification_status": "verified",
            "verification_notes": "All credentials verified. Excellent background and experience.",
            "documents_verified": True,
            "background_check_passed": True
        }
        
        # Mock admin verification call
        admin_headers = {"Authorization": "Bearer admin_token", "X-Admin-Access": "true"}
        
        verify_response = await async_client.post(
            f"/api/v1/admin/astrologers/{astrologer_id}/verify",
            json=verification_data,
            headers=admin_headers
        )
        
        if verify_response.status_code == 404:
            pytest.skip("Admin verification endpoints not implemented")
        
        # Check astrologer status after verification
        profile_response = await async_client.get(
            f"/api/v1/astrologers/{astrologer_id}",
            headers=headers
        )
        
        profile_data = assert_response_success(profile_response)
        assert profile_data["status"] == "verified"
        assert profile_data["is_available"] == True
    
    @pytest.mark.asyncio
    async def test_astrologer_profile_updates(self, async_client: AsyncClient, db_session):
        """Test astrologer profile updates and management."""
        
        try:
            astrologer_id, headers = await self.test_complete_astrologer_registration_flow(async_client, db_session)
        except pytest.skip.Exception:
            pytest.skip("Prerequisites not available")
        
        # Update astrologer profile
        profile_updates = {
            "bio": "Updated bio with additional 20 years of experience in Vedic astrology and spiritual counseling.",
            "hourly_rate": "175.00",
            "specializations": ["vedic", "career_guidance", "relationships", "spiritual_growth"],
            "certifications": [
                "Certified Vedic Astrologer - American Institute of Vedic Studies",
                "PhD Philosophy - Harvard University", 
                "Jyotish Acharya - Council of Vedic Astrology",
                "Advanced Certification in Spiritual Psychology"
            ]
        }
        
        update_response = await async_client.put(
            f"/api/v1/astrologers/profile",
            json=profile_updates,
            headers=headers
        )
        
        updated_data = assert_response_success(update_response)
        
        # Verify updates
        assert updated_data["hourly_rate"] == "175.00"
        assert len(updated_data["specializations"]) == 4
        assert "spiritual_growth" in updated_data["specializations"]
        assert len(updated_data["certifications"]) == 4


class TestConsultationBooking:
    """Test consultation booking flow."""
    
    @pytest.mark.asyncio
    async def test_consultation_discovery_and_booking(self, async_client: AsyncClient, db_session):
        """Test complete consultation discovery and booking flow."""
        
        # Step 1: User searches for astrologers
        search_params = {
            "specialization": "vedic",
            "consultation_type": "video",
            "price_range_max": "200.00",
            "availability_date": (datetime.now() + timedelta(days=1)).date().isoformat(),
            "rating_min": 4.0
        }
        
        search_response = await async_client.get(
            "/api/v1/astrologers/search",
            params=search_params
        )
        
        if search_response.status_code == 404:
            pytest.skip("Astrologer search endpoints not implemented")
        
        search_results = assert_response_success(search_response)
        
        # Verify search results structure
        assert "astrologers" in search_results
        assert "total_count" in search_results
        assert "filters_applied" in search_results
        
        if len(search_results["astrologers"]) == 0:
            pytest.skip("No astrologers available for booking test")
        
        # Step 2: User selects an astrologer and views their profile
        selected_astrologer = search_results["astrologers"][0]
        astrologer_id = selected_astrologer["astrologer_id"]
        
        profile_response = await async_client.get(f"/api/v1/astrologers/{astrologer_id}")
        profile_data = assert_response_success(profile_response)
        
        # Verify astrologer profile has booking information
        assert "hourly_rate" in profile_data
        assert "availability" in profile_data
        assert "consultation_types" in profile_data
        assert "rating" in profile_data
        
        # Step 3: Check astrologer availability
        availability_params = {
            "astrologer_id": astrologer_id,
            "date": (datetime.now() + timedelta(days=1)).date().isoformat(),
            "consultation_type": "video"
        }
        
        availability_response = await async_client.get(
            "/api/v1/consultations/availability",
            params=availability_params
        )
        
        availability_data = assert_response_success(availability_response)
        
        # Verify availability data
        assert "available_slots" in availability_data
        assert "astrologer_timezone" in availability_data
        
        if len(availability_data["available_slots"]) == 0:
            pytest.skip("No available slots for booking test")
        
        # Step 4: User registers/logs in
        user_data = {
            "email": "consultation.seeker@example.com",
            "password": "SecurePass123!",
            "full_name": "Jane Seeker",
            "date_of_birth": "1985-08-20",
            "timezone": "America/New_York"
        }
        
        user_response = await async_client.post("/api/v1/auth/register", json=user_data)
        
        if user_response.status_code == 404:
            pytest.skip("Authentication required for booking")
        
        user_result = assert_response_success(user_response, status.HTTP_201_CREATED)
        headers = {"Authorization": f"Bearer {user_result['access_token']}"}
        
        # Step 5: Book the consultation
        booking_data = {
            "astrologer_id": astrologer_id,
            "consultation_type": "video",
            "scheduled_time": availability_data["available_slots"][0]["start_time"],
            "duration_minutes": 60,
            "topic": "Career guidance and life direction",
            "specific_questions": [
                "What career path would be most fulfilling for me?",
                "When is the best time to make a career change?",
                "What are my natural talents according to my chart?"
            ],
            "birth_data": {
                "date_of_birth": "1985-08-20",
                "time_of_birth": "14:30:00",
                "place_of_birth": "Boston, MA, USA",
                "timezone": "America/New_York"
            }
        }
        
        booking_response = await async_client.post(
            "/api/v1/consultations/book",
            json=booking_data,
            headers=headers
        )
        
        booking_result = assert_response_success(booking_response, status.HTTP_201_CREATED)
        
        # Verify booking was created
        assert "consultation_id" in booking_result
        assert "payment_required" in booking_result
        assert "total_amount" in booking_result
        assert booking_result["status"] == "pending_payment"
        
        return booking_result["consultation_id"], headers
    
    @pytest.mark.asyncio
    async def test_consultation_payment_flow(self, async_client: AsyncClient, db_session):
        """Test consultation payment processing."""
        
        try:
            consultation_id, headers = await self.test_consultation_discovery_and_booking(async_client, db_session)
        except pytest.skip.Exception:
            pytest.skip("Prerequisites not available")
        
        # Process payment for consultation
        payment_data = {
            "consultation_id": consultation_id,
            "payment_method": "stripe",
            "payment_token": "tok_test_visa_1234",  # Test Stripe token
            "billing_address": {
                "name": "Jane Seeker",
                "address_line1": "123 Main St",
                "city": "Boston",
                "state": "MA",
                "postal_code": "02101",
                "country": "US"
            }
        }
        
        payment_response = await async_client.post(
            "/api/v1/consultations/payment",
            json=payment_data,
            headers=headers
        )
        
        if payment_response.status_code == 404:
            pytest.skip("Payment endpoints not implemented")
        
        payment_result = assert_response_success(payment_response)
        
        # Verify payment was processed
        assert "payment_id" in payment_result
        assert payment_result["status"] == "confirmed"
        
        # Verify consultation status updated
        consultation_response = await async_client.get(
            f"/api/v1/consultations/{consultation_id}",
            headers=headers
        )
        
        consultation_data = assert_response_success(consultation_response)
        assert consultation_data["status"] == "confirmed"
        assert consultation_data["payment_status"] == "paid"
    
    @pytest.mark.asyncio
    async def test_consultation_rescheduling(self, async_client: AsyncClient, db_session):
        """Test consultation rescheduling flow."""
        
        try:
            consultation_id, headers = await self.test_consultation_discovery_and_booking(async_client, db_session)
        except pytest.skip.Exception:
            pytest.skip("Prerequisites not available")
        
        # Request to reschedule consultation
        reschedule_data = {
            "new_scheduled_time": (datetime.now() + timedelta(days=2, hours=2)).isoformat(),
            "reason": "Schedule conflict arose"
        }
        
        reschedule_response = await async_client.post(
            f"/api/v1/consultations/{consultation_id}/reschedule",
            json=reschedule_data,
            headers=headers
        )
        
        if reschedule_response.status_code == 404:
            pytest.skip("Reschedule endpoints not implemented")
        
        reschedule_result = assert_response_success(reschedule_response)
        
        # Verify reschedule request
        assert reschedule_result["status"] == "reschedule_requested"
        assert "new_scheduled_time" in reschedule_result


class TestVideoConsultationFlow:
    """Test video consultation session flow."""
    
    @pytest.mark.asyncio
    async def test_video_session_creation_and_access(self, async_client: AsyncClient, db_session):
        """Test video session creation and participant access."""
        
        # Mock a confirmed consultation
        consultation_data = {
            "consultation_id": str(uuid4()),
            "astrologer_id": str(uuid4()),
            "user_id": str(uuid4()),
            "consultation_type": "video",
            "status": "confirmed",
            "scheduled_time": (datetime.now() + timedelta(minutes=5)).isoformat()
        }
        
        # Test video room creation (would be called near consultation time)
        video_room_request = {
            "consultation_id": consultation_data["consultation_id"],
            "duration_minutes": 60,
            "enable_recording": True
        }
        
        room_response = await async_client.post(
            "/api/v1/consultations/video/create-room",
            json=video_room_request
        )
        
        if room_response.status_code == 404:
            pytest.skip("Video consultation endpoints not implemented")
        
        room_data = assert_response_success(room_response)
        
        # Verify video room was created
        assert "room_name" in room_data
        assert "room_sid" in room_data
        assert "participant_tokens" in room_data
        assert "astrologer_token" in room_data["participant_tokens"]
        assert "client_token" in room_data["participant_tokens"]
        
        # Test participant access tokens
        for participant_type, token in room_data["participant_tokens"].items():
            assert len(token) > 20, f"{participant_type} token should be substantial"
    
    @pytest.mark.asyncio
    async def test_consultation_recording_and_notes(self, async_client: AsyncClient, db_session):
        """Test consultation recording and note-taking functionality."""
        
        consultation_id = str(uuid4())
        headers = {"Authorization": "Bearer test_astrologer_token"}
        
        # Test adding consultation notes during session
        notes_data = {
            "consultation_id": consultation_id,
            "notes": "Client has strong Sagittarius influence. Jupiter in 10th house indicates career success in teaching or publishing. Recommended focusing on writing and education.",
            "key_insights": [
                "Strong Jupiter influence in career sector",
                "Natural teaching abilities",
                "Publishing potential",
                "Travel opportunities in career"
            ],
            "recommendations": [
                "Pursue advanced education or certifications",
                "Consider writing or publishing projects", 
                "Look for teaching opportunities",
                "Plan travel around favorable Jupiter transits"
            ]
        }
        
        notes_response = await async_client.post(
            f"/api/v1/consultations/{consultation_id}/notes",
            json=notes_data,
            headers=headers
        )
        
        if notes_response.status_code == 404:
            pytest.skip("Consultation notes endpoints not implemented")
        
        notes_result = assert_response_success(notes_response)
        
        # Verify notes were saved
        assert "notes_id" in notes_result
        assert notes_result["consultation_id"] == consultation_id
        
        # Test retrieving consultation summary
        summary_response = await async_client.get(
            f"/api/v1/consultations/{consultation_id}/summary",
            headers=headers
        )
        
        summary_data = assert_response_success(summary_response)
        
        # Verify summary includes notes and insights
        assert "consultation_notes" in summary_data
        assert "key_insights" in summary_data
        assert "recommendations" in summary_data
        assert "session_duration" in summary_data


class TestConsultationReviewsAndRatings:
    """Test consultation review and rating system."""
    
    @pytest.mark.asyncio
    async def test_post_consultation_review_flow(self, async_client: AsyncClient, db_session):
        """Test post-consultation review and rating flow."""
        
        consultation_id = str(uuid4())
        astrologer_id = str(uuid4())
        client_headers = {"Authorization": "Bearer test_client_token"}
        
        # Simulate completed consultation
        completion_data = {
            "consultation_id": consultation_id,
            "status": "completed",
            "actual_duration": 65,  # 65 minutes
            "session_quality": "excellent"
        }
        
        # Client submits review after consultation
        review_data = {
            "consultation_id": consultation_id,
            "astrologer_id": astrologer_id,
            "overall_rating": 5,
            "accuracy_rating": 5,
            "communication_rating": 4,
            "professionalism_rating": 5,
            "value_rating": 4,
            "review_text": "Dr. Sarah provided incredibly insightful reading. Her predictions about my career were spot-on and her guidance was very practical. The session went over time but she didn't charge extra. Highly recommended!",
            "would_recommend": True,
            "favorite_aspects": [
                "Accurate predictions",
                "Practical guidance", 
                "Professional demeanor",
                "Generous with time"
            ]
        }
        
        review_response = await async_client.post(
            "/api/v1/consultations/review",
            json=review_data,
            headers=client_headers
        )
        
        if review_response.status_code == 404:
            pytest.skip("Review endpoints not implemented")
        
        review_result = assert_response_success(review_response, status.HTTP_201_CREATED)
        
        # Verify review was created
        assert "review_id" in review_result
        assert review_result["overall_rating"] == 5
        assert review_result["would_recommend"] == True
        
        # Test astrologer rating update
        astrologer_stats_response = await async_client.get(
            f"/api/v1/astrologers/{astrologer_id}/stats"
        )
        
        if astrologer_stats_response.status_code != 404:
            stats_data = assert_response_success(astrologer_stats_response)
            
            # Verify updated statistics
            assert "average_rating" in stats_data
            assert "total_reviews" in stats_data
            assert "total_consultations" in stats_data
            assert stats_data["average_rating"] > 0


class TestAstrologerDashboard:
    """Test astrologer dashboard and management features."""
    
    @pytest.mark.asyncio
    async def test_astrologer_consultation_management(self, async_client: AsyncClient, db_session):
        """Test astrologer consultation management dashboard."""
        
        astrologer_headers = {"Authorization": "Bearer test_astrologer_token"}
        
        # Get astrologer's upcoming consultations
        upcoming_response = await async_client.get(
            "/api/v1/astrologers/consultations/upcoming",
            headers=astrologer_headers
        )
        
        if upcoming_response.status_code == 404:
            pytest.skip("Astrologer dashboard endpoints not implemented")
        
        upcoming_data = assert_response_success(upcoming_response)
        
        # Verify consultation data structure
        assert "consultations" in upcoming_data
        assert "total_count" in upcoming_data
        
        # Get consultation history
        history_response = await async_client.get(
            "/api/v1/astrologers/consultations/history",
            params={"limit": 10, "offset": 0},
            headers=astrologer_headers
        )
        
        history_data = assert_response_success(history_response)
        
        assert "consultations" in history_data
        assert "pagination" in history_data
        
        # Get earnings summary
        earnings_response = await async_client.get(
            "/api/v1/astrologers/earnings",
            params={"period": "monthly"},
            headers=astrologer_headers
        )
        
        if earnings_response.status_code != 404:
            earnings_data = assert_response_success(earnings_response)
            
            assert "total_earnings" in earnings_data
            assert "consultation_count" in earnings_data
            assert "average_rating" in earnings_data
    
    @pytest.mark.asyncio
    async def test_astrologer_availability_management(self, async_client: AsyncClient, db_session):
        """Test astrologer availability and schedule management."""
        
        astrologer_headers = {"Authorization": "Bearer test_astrologer_token"}
        
        # Update availability schedule
        availability_update = {
            "weekly_schedule": {
                "monday": {"start": "10:00", "end": "18:00"},
                "tuesday": {"start": "10:00", "end": "18:00"},
                "wednesday": {"start": "10:00", "end": "18:00"},
                "thursday": {"start": "10:00", "end": "18:00"},
                "friday": {"start": "10:00", "end": "16:00"},
                "saturday": {"available": False},
                "sunday": {"available": False}
            },
            "time_off": [
                {
                    "start_date": (datetime.now() + timedelta(days=30)).date().isoformat(),
                    "end_date": (datetime.now() + timedelta(days=37)).date().isoformat(),
                    "reason": "Vacation"
                }
            ],
            "special_hours": [
                {
                    "date": (datetime.now() + timedelta(days=7)).date().isoformat(),
                    "start": "14:00",
                    "end": "20:00",
                    "reason": "Extended evening hours"
                }
            ]
        }
        
        availability_response = await async_client.put(
            "/api/v1/astrologers/availability",
            json=availability_update,
            headers=astrologer_headers
        )
        
        if availability_response.status_code == 404:
            pytest.skip("Availability management endpoints not implemented")
        
        availability_result = assert_response_success(availability_response)
        
        # Verify availability was updated
        assert "weekly_schedule" in availability_result
        assert "time_off" in availability_result
        assert availability_result["weekly_schedule"]["friday"]["end"] == "16:00"


class TestMarketplaceSearchAndFiltering:
    """Test marketplace search and filtering functionality."""
    
    @pytest.mark.asyncio
    async def test_advanced_astrologer_search(self, async_client: AsyncClient, db_session):
        """Test advanced search and filtering for astrologers."""
        
        # Test various search scenarios
        search_scenarios = [
            {
                "name": "Vedic specialists under $100/hour",
                "params": {
                    "specialization": "vedic",
                    "price_range_max": "100.00",
                    "rating_min": "4.0"
                }
            },
            {
                "name": "Career guidance experts",
                "params": {
                    "specialization": "career_guidance",
                    "consultation_type": "video",
                    "experience_min": "5"
                }
            },
            {
                "name": "Available today for urgent consultation",
                "params": {
                    "availability_date": datetime.now().date().isoformat(),
                    "consultation_type": "chat",
                    "rating_min": "3.5"
                }
            },
            {
                "name": "Relationship specialists with video consultations",
                "params": {
                    "specialization": "relationships",
                    "consultation_type": "video",
                    "language": "English"
                }
            }
        ]
        
        for scenario in search_scenarios:
            search_response = await async_client.get(
                "/api/v1/astrologers/search",
                params=scenario["params"]
            )
            
            if search_response.status_code == 404:
                pytest.skip("Search endpoints not implemented")
            
            search_results = assert_response_success(search_response)
            
            # Verify search results structure
            assert "astrologers" in search_results
            assert "total_count" in search_results
            assert "filters_applied" in search_results
            
            # Verify filters were applied correctly
            filters = search_results["filters_applied"]
            for key, value in scenario["params"].items():
                assert key in filters
                assert str(filters[key]) == str(value)
    
    @pytest.mark.asyncio
    async def test_astrologer_sorting_options(self, async_client: AsyncClient, db_session):
        """Test different sorting options for astrologer listings."""
        
        sorting_options = [
            "rating_desc",
            "price_asc", 
            "price_desc",
            "experience_desc",
            "popularity_desc",
            "availability_asc"
        ]
        
        for sort_option in sorting_options:
            search_response = await async_client.get(
                "/api/v1/astrologers/search",
                params={"sort_by": sort_option, "limit": 5}
            )
            
            if search_response.status_code == 404:
                pytest.skip("Search endpoints not implemented")
            
            search_results = assert_response_success(search_response)
            
            # Verify sorting was applied
            assert "sort_applied" in search_results
            assert search_results["sort_applied"] == sort_option
            
            # Verify results are actually sorted (if we have multiple results)
            astrologers = search_results["astrologers"]
            if len(astrologers) > 1:
                if sort_option == "rating_desc":
                    for i in range(len(astrologers) - 1):
                        assert astrologers[i]["rating"] >= astrologers[i + 1]["rating"]
                elif sort_option == "price_asc":
                    for i in range(len(astrologers) - 1):
                        price1 = float(astrologers[i]["hourly_rate"])
                        price2 = float(astrologers[i + 1]["hourly_rate"])
                        assert price1 <= price2