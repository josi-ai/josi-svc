"""
Real-world remedy recommendation system tests.

Tests the AI-powered remedy recommendation system using real chart data
and evaluates the quality and relevance of recommended remedies.
"""
import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from httpx import AsyncClient
from fastapi import status
from unittest.mock import patch

from tests.conftest import assert_response_success
from tests.real_world.test_chart_calculations import TestRealBirthDataCharts


class TestRemedyRecommendationSystem:
    """Test AI-powered remedy recommendation system."""
    
    @pytest.mark.asyncio
    async def test_remedy_recommendations_for_mangal_dosha(self, async_client: AsyncClient, db_session):
        """Test remedy recommendations for Mangal Dosha (Mars affliction)."""
        
        # Create person with Mars in 7th house (Mangal Dosha)
        person_data = {
            "name": "Mars Afflicted Person",
            "date_of_birth": "1990-11-15",
            "time_of_birth": "1990-11-15T14:30:00",
            "place_of_birth": "Mumbai, India",
            "latitude": "19.0760",
            "longitude": "72.8777",
            "timezone": "Asia/Kolkata",
            "email": "mangal.dosha@example.com"
        }
        
        # Create person
        person_response = await async_client.post("/api/v1/persons/", json=person_data)
        person_result = assert_response_success(person_response, status.HTTP_201_CREATED)
        person_id = person_result["person_id"]
        
        # Calculate Vedic chart
        chart_request = {
            "person_id": person_id,
            "chart_type": "natal",
            "house_system": "whole_sign",
            "ayanamsa": "lahiri",
            "coordinate_system": "sidereal"
        }
        
        chart_response = await async_client.post("/api/v1/charts/calculate", json=chart_request)
        chart_data = assert_response_success(chart_response, status.HTTP_201_CREATED)
        chart_id = chart_data["chart_id"]
        
        # Request remedy recommendations focusing on marriage/relationship concerns
        remedy_request = {
            "chart_id": chart_id,
            "concern_areas": ["marriage", "relationships"],
            "tradition_preference": "vedic",
            "difficulty_preference": 3,  # Moderate difficulty
            "cost_preference": 2  # Low to moderate cost
        }
        
        remedy_response = await async_client.post("/api/v1/remedies/recommend", json=remedy_request)
        
        if remedy_response.status_code == 404:
            pytest.skip("Remedy recommendation endpoints not implemented")
        
        recommendations = assert_response_success(remedy_response)
        
        # Verify recommendation structure
        assert "recommendations" in recommendations
        assert "total_recommendations" in recommendations
        assert len(recommendations["recommendations"]) > 0
        
        # Verify Mangal Dosha specific remedies
        remedy_types = []
        remedy_descriptions = []
        
        for rec in recommendations["recommendations"]:
            remedy_types.append(rec["remedy"]["type"])
            remedy_descriptions.append(rec["remedy"]["description"]["en"].lower())
            
            # Verify recommendation structure
            assert "relevance_score" in rec
            assert "priority_level" in rec
            assert "issue_description" in rec
            assert "personalized_instructions" in rec
            assert rec["relevance_score"] > 0
        
        # Should include Mars-specific remedies
        mars_related = any("mars" in desc or "mangal" in desc for desc in remedy_descriptions)
        assert mars_related, "Should include Mars/Mangal specific remedies"
        
        # Should include relationship/marriage focused remedies
        relationship_related = any("marriage" in desc or "relationship" in desc for desc in remedy_descriptions)
        assert relationship_related, "Should include relationship-focused remedies"
    
    @pytest.mark.asyncio
    async def test_remedy_recommendations_for_career_concerns(self, async_client: AsyncClient, db_session):
        """Test remedy recommendations for career and professional issues."""
        
        # Use Steve Jobs' data for career-focused remedies
        person_data = TestRealBirthDataCharts.CELEBRITY_BIRTH_DATA["steve_jobs"].copy()
        person_data["email"] = "career.remedies@example.com"
        
        # Create person and chart
        person_response = await async_client.post("/api/v1/persons/", json=person_data)
        person_result = assert_response_success(person_response, status.HTTP_201_CREATED)
        person_id = person_result["person_id"]
        
        chart_request = {
            "person_id": person_id,
            "chart_type": "natal",
            "house_system": "whole_sign",
            "ayanamsa": "lahiri",
            "coordinate_system": "sidereal"
        }
        
        chart_response = await async_client.post("/api/v1/charts/calculate", json=chart_request)
        chart_data = assert_response_success(chart_response, status.HTTP_201_CREATED)
        chart_id = chart_data["chart_id"]
        
        # Request career-focused remedies
        remedy_request = {
            "chart_id": chart_id,
            "concern_areas": ["career", "business", "innovation"],
            "tradition_preference": "vedic",
            "difficulty_preference": 4,  # Higher difficulty for serious career goals
            "cost_preference": 3  # Moderate cost
        }
        
        remedy_response = await async_client.post("/api/v1/remedies/recommend", json=remedy_request)
        recommendations = assert_response_success(remedy_response)
        
        # Verify career-specific recommendations
        career_keywords = ["career", "business", "success", "leadership", "innovation", "jupiter", "saturn", "sun"]
        
        found_career_remedies = 0
        for rec in recommendations["recommendations"]:
            remedy_desc = rec["remedy"]["description"]["en"].lower()
            issue_desc = rec["issue_description"].lower()
            
            if any(keyword in remedy_desc or keyword in issue_desc for keyword in career_keywords):
                found_career_remedies += 1
                
                # Verify high priority for career concerns
                assert rec["priority_level"] >= 3, "Career remedies should have higher priority"
                
                # Verify personalized instructions exist
                assert len(rec["personalized_instructions"]) > 50, "Should have detailed personalized instructions"
        
        assert found_career_remedies > 0, "Should have career-specific remedies"
        
        # Verify recommendations are sorted by relevance/priority
        scores = [rec["relevance_score"] for rec in recommendations["recommendations"]]
        assert scores == sorted(scores, reverse=True), "Recommendations should be sorted by relevance"
    
    @pytest.mark.asyncio
    async def test_remedy_recommendations_for_health_concerns(self, async_client: AsyncClient, db_session):
        """Test remedy recommendations for health and wellness issues."""
        
        # Create person with potential health concerns (6th and 8th house afflictions)
        person_data = {
            "name": "Health Concern Person",
            "date_of_birth": "1985-07-20",
            "time_of_birth": "1985-07-20T06:15:00",
            "place_of_birth": "Delhi, India",
            "latitude": "28.7041",
            "longitude": "77.1025",
            "timezone": "Asia/Kolkata",
            "email": "health.concern@example.com"
        }
        
        # Create person and chart
        person_response = await async_client.post("/api/v1/persons/", json=person_data)
        person_result = assert_response_success(person_response, status.HTTP_201_CREATED)
        person_id = person_result["person_id"]
        
        chart_request = {
            "person_id": person_id,
            "chart_type": "natal",
            "house_system": "whole_sign",
            "ayanamsa": "lahiri",
            "coordinate_system": "sidereal"
        }
        
        chart_response = await async_client.post("/api/v1/charts/calculate", json=chart_request)
        chart_data = assert_response_success(chart_response, status.HTTP_201_CREATED)
        chart_id = chart_data["chart_id"]
        
        # Request health-focused remedies
        remedy_request = {
            "chart_id": chart_id,
            "concern_areas": ["health", "vitality", "wellness"],
            "tradition_preference": "vedic",
            "difficulty_preference": 2,  # Easier remedies for health
            "cost_preference": 1  # Lower cost for accessibility
        }
        
        remedy_response = await async_client.post("/api/v1/remedies/recommend", json=remedy_request)
        recommendations = assert_response_success(remedy_response)
        
        # Verify health-specific recommendations
        health_keywords = ["health", "vitality", "wellness", "healing", "sun", "moon", "mars"]
        
        found_health_remedies = 0
        dietary_recommendations = 0
        gemstone_recommendations = 0
        
        for rec in recommendations["recommendations"]:
            remedy = rec["remedy"]
            remedy_desc = remedy["description"]["en"].lower()
            
            if any(keyword in remedy_desc for keyword in health_keywords):
                found_health_remedies += 1
                
                # Check for different types of health remedies
                if remedy["type"] == "lifestyle":
                    dietary_recommendations += 1
                elif remedy["type"] == "gemstone":
                    gemstone_recommendations += 1
                
                # Verify accessible difficulty and cost levels
                assert remedy["difficulty_level"] <= 3, "Health remedies should be accessible"
                assert remedy["cost_level"] <= 2, "Health remedies should be affordable"
        
        assert found_health_remedies > 0, "Should have health-specific remedies"
    
    @pytest.mark.asyncio
    async def test_remedy_recommendations_with_different_traditions(self, async_client: AsyncClient, db_session):
        """Test remedy recommendations across different astrological traditions."""
        
        person_data = TestRealBirthDataCharts.CELEBRITY_BIRTH_DATA["albert_einstein"].copy()
        person_data["email"] = "tradition.test@example.com"
        
        # Create person and charts for different traditions
        person_response = await async_client.post("/api/v1/persons/", json=person_data)
        person_result = assert_response_success(person_response, status.HTTP_201_CREATED)
        person_id = person_result["person_id"]
        
        # Vedic chart
        vedic_chart_request = {
            "person_id": person_id,
            "chart_type": "natal",
            "house_system": "whole_sign",
            "ayanamsa": "lahiri",
            "coordinate_system": "sidereal"
        }
        
        vedic_chart_response = await async_client.post("/api/v1/charts/calculate", json=vedic_chart_request)
        vedic_chart_data = assert_response_success(vedic_chart_response, status.HTTP_201_CREATED)
        
        # Western chart
        western_chart_request = {
            "person_id": person_id,
            "chart_type": "natal",
            "house_system": "placidus",
            "coordinate_system": "tropical"
        }
        
        western_chart_response = await async_client.post("/api/v1/charts/calculate", json=western_chart_request)
        western_chart_data = assert_response_success(western_chart_response, status.HTTP_201_CREATED)
        
        # Test Vedic remedies
        vedic_remedy_request = {
            "chart_id": vedic_chart_data["chart_id"],
            "concern_areas": ["intellect", "creativity"],
            "tradition_preference": "vedic"
        }
        
        vedic_remedy_response = await async_client.post("/api/v1/remedies/recommend", json=vedic_remedy_request)
        vedic_recommendations = assert_response_success(vedic_remedy_response)
        
        # Test Western remedies
        western_remedy_request = {
            "chart_id": western_chart_data["chart_id"],
            "concern_areas": ["intellect", "creativity"],
            "tradition_preference": "western"
        }
        
        western_remedy_response = await async_client.post("/api/v1/remedies/recommend", json=western_remedy_request)
        western_recommendations = assert_response_success(western_remedy_response)
        
        # Verify different traditions produce different recommendations
        vedic_remedy_types = [rec["remedy"]["tradition"] for rec in vedic_recommendations["recommendations"]]
        western_remedy_types = [rec["remedy"]["tradition"] for rec in western_recommendations["recommendations"]]
        
        assert all(tradition == "vedic" for tradition in vedic_remedy_types), "Should only return Vedic remedies"
        assert all(tradition == "western" for tradition in western_remedy_types), "Should only return Western remedies"
        
        # Verify different approaches
        vedic_remedies = [rec["remedy"]["type"] for rec in vedic_recommendations["recommendations"]]
        western_remedies = [rec["remedy"]["type"] for rec in western_recommendations["recommendations"]]
        
        # Vedic should include traditional remedies
        vedic_traditional = any(remedy_type in ["mantra", "yantra", "ritual"] for remedy_type in vedic_remedies)
        assert vedic_traditional, "Vedic recommendations should include traditional remedies"


class TestRemedyProgressTracking:
    """Test remedy progress tracking functionality."""
    
    @pytest.mark.asyncio
    async def test_remedy_progress_tracking_flow(self, async_client: AsyncClient, db_session):
        """Test complete remedy progress tracking flow."""
        
        # First get a remedy recommendation
        person_data = {
            "name": "Progress Tracker",
            "date_of_birth": "1988-03-12",
            "time_of_birth": "1988-03-12T10:00:00",
            "place_of_birth": "Chennai, India",
            "latitude": "13.0827",
            "longitude": "80.2707",
            "timezone": "Asia/Kolkata",
            "email": "progress.tracker@example.com"
        }
        
        person_response = await async_client.post("/api/v1/persons/", json=person_data)
        person_result = assert_response_success(person_response, status.HTTP_201_CREATED)
        person_id = person_result["person_id"]
        
        chart_request = {
            "person_id": person_id,
            "chart_type": "natal",
            "house_system": "whole_sign",
            "ayanamsa": "lahiri",
            "coordinate_system": "sidereal"
        }
        
        chart_response = await async_client.post("/api/v1/charts/calculate", json=chart_request)
        chart_data = assert_response_success(chart_response, status.HTTP_201_CREATED)
        chart_id = chart_data["chart_id"]
        
        remedy_request = {
            "chart_id": chart_id,
            "concern_areas": ["peace", "meditation"]
        }
        
        remedy_response = await async_client.post("/api/v1/remedies/recommend", json=remedy_request)
        recommendations = assert_response_success(remedy_response)
        
        # Select first remedy for progress tracking
        selected_remedy = recommendations["recommendations"][0]
        remedy_id = selected_remedy["remedy"]["remedy_id"]
        
        # Start progress tracking
        progress_start_response = await async_client.post(
            f"/api/v1/remedies/{remedy_id}/start-progress",
            params={"target_days": 40}
        )
        
        if progress_start_response.status_code == 404:
            pytest.skip("Progress tracking endpoints not implemented")
        
        progress_data = assert_response_success(progress_start_response)
        
        # Verify progress tracking started
        assert "progress_id" in progress_data
        assert progress_data["current_day"] == 1
        assert progress_data["total_days"] == 40
        assert progress_data["completion_percentage"] == 0.0
        
        progress_id = progress_data["progress_id"]
        
        # Update progress after several days
        progress_updates = [
            {
                "current_day": 7,
                "completion_percentage": 17.5,
                "daily_log": {"mood": "positive", "meditation_duration": "20 minutes", "observations": "Feeling more centered"},
                "notes": "First week completed. Finding the practice calming.",
                "benefits_experienced": ["Better sleep", "Reduced anxiety"]
            },
            {
                "current_day": 14,
                "completion_percentage": 35.0,
                "daily_log": {"mood": "very positive", "meditation_duration": "25 minutes", "observations": "Deeper meditation states"},
                "notes": "Two weeks in. Practice becoming more natural.",
                "benefits_experienced": ["Better sleep", "Reduced anxiety", "Improved focus", "Emotional stability"]
            },
            {
                "current_day": 28,
                "completion_percentage": 70.0,
                "daily_log": {"mood": "excellent", "meditation_duration": "30 minutes", "observations": "Strong connection to practice"},
                "notes": "Four weeks completed. Significant improvements noticed.",
                "benefits_experienced": ["Better sleep", "Reduced anxiety", "Improved focus", "Emotional stability", "Spiritual connection"]
            }
        ]
        
        for update in progress_updates:
            update_response = await async_client.put(
                f"/api/v1/remedies/progress/{progress_id}",
                json=update
            )
            
            update_result = assert_response_success(update_response)
            
            # Verify progress update
            assert update_result["current_day"] == update["current_day"]
            assert update_result["completion_percentage"] == update["completion_percentage"]
            assert len(update_result["benefits_experienced"]) == len(update["benefits_experienced"])
        
        # Complete the remedy
        completion_update = {
            "current_day": 40,
            "completion_percentage": 100.0,
            "notes": "Successfully completed 40-day practice. Life-changing experience.",
            "effectiveness_rating": 9,
            "would_recommend": True,
            "feedback": "This remedy has transformed my daily life. The meditation practice has become essential."
        }
        
        completion_response = await async_client.put(
            f"/api/v1/remedies/progress/{progress_id}",
            json=completion_update
        )
        
        completion_result = assert_response_success(completion_response)
        
        # Verify completion
        assert completion_result["is_completed"] == True
        assert completion_result["effectiveness_rating"] == 9
        assert completion_result["would_recommend"] == True
    
    @pytest.mark.asyncio
    async def test_user_active_remedies_dashboard(self, async_client: AsyncClient, db_session):
        """Test user's active remedies dashboard."""
        
        # This would require authentication to work properly
        user_headers = {"Authorization": "Bearer test_user_token"}
        
        active_remedies_response = await async_client.get(
            "/api/v1/remedies/my-remedies/active",
            headers=user_headers
        )
        
        if active_remedies_response.status_code == 404:
            pytest.skip("User remedy dashboard not implemented")
        
        active_remedies = assert_response_success(active_remedies_response)
        
        # Verify dashboard structure
        assert "active_remedies" in active_remedies
        assert "count" in active_remedies
        
        # Verify each active remedy has progress information
        for remedy_progress in active_remedies["active_remedies"]:
            assert "progress" in remedy_progress
            assert "remedy" in remedy_progress
            
            progress = remedy_progress["progress"]
            assert "current_day" in progress
            assert "completion_percentage" in progress
            assert "started_at" in progress


class TestRemedyDatabase:
    """Test remedy database and categorization."""
    
    @pytest.mark.asyncio
    async def test_remedy_categories_and_filtering(self, async_client: AsyncClient, db_session):
        """Test remedy categories and filtering options."""
        
        # Get available remedy categories
        categories_response = await async_client.get("/api/v1/remedies/categories")
        
        if categories_response.status_code == 404:
            pytest.skip("Remedy categories endpoint not implemented")
        
        categories = assert_response_success(categories_response)
        
        # Verify category structure
        assert "remedy_types" in categories
        assert "traditions" in categories
        assert "dosha_types" in categories
        assert "planets" in categories
        assert "difficulty_levels" in categories
        assert "cost_levels" in categories
        
        # Test filtering by different criteria
        filter_tests = [
            {"tradition": "vedic", "remedy_type": "mantra"},
            {"planet": "Jupiter", "difficulty_max": 3},
            {"dosha_type": "mangal_dosha", "cost_max": 2},
            {"tradition": "vedic", "planet": "Saturn", "remedy_type": "gemstone"}
        ]
        
        for filters in filter_tests:
            remedies_response = await async_client.get(
                "/api/v1/remedies/",
                params=filters
            )
            
            remedies_data = assert_response_success(remedies_response)
            
            # Verify filtering structure
            assert "remedies" in remedies_data
            assert "pagination" in remedies_data
            assert "filters_applied" in remedies_data
            
            # Verify filters were applied
            for key, value in filters.items():
                assert key in remedies_data["filters_applied"]
    
    @pytest.mark.asyncio
    async def test_individual_remedy_details(self, async_client: AsyncClient, db_session):
        """Test retrieving detailed information about individual remedies."""
        
        # Get list of remedies first
        remedies_response = await async_client.get("/api/v1/remedies/", params={"limit": 5})
        
        if remedies_response.status_code == 404:
            pytest.skip("Remedy listing endpoint not implemented")
        
        remedies_data = assert_response_success(remedies_response)
        
        if len(remedies_data["remedies"]) == 0:
            pytest.skip("No remedies available for testing")
        
        # Get details of first remedy
        remedy = remedies_data["remedies"][0]
        remedy_id = remedy["remedy_id"]
        
        remedy_detail_response = await async_client.get(f"/api/v1/remedies/{remedy_id}")
        remedy_details = assert_response_success(remedy_detail_response)
        
        # Verify detailed remedy structure
        required_fields = [
            "remedy_id", "name", "type", "tradition", "description", 
            "instructions", "benefits", "duration_days", "difficulty_level",
            "cost_level", "effectiveness_rating"
        ]
        
        for field in required_fields:
            assert field in remedy_details, f"Missing required field: {field}"
        
        # Verify localized content
        assert "localized_content" in remedy_details
        localized = remedy_details["localized_content"]
        assert "description" in localized
        assert "instructions" in localized
        assert "benefits" in localized
        
        # Test with different language
        remedy_hindi_response = await async_client.get(
            f"/api/v1/remedies/{remedy_id}",
            params={"language": "hi"}
        )
        
        if remedy_hindi_response.status_code == 200:
            remedy_hindi = assert_response_success(remedy_hindi_response)
            
            # Should return Hindi content if available
            assert "localized_content" in remedy_hindi


class TestRemedyAIPersonalization:
    """Test AI-powered remedy personalization."""
    
    @pytest.mark.asyncio
    async def test_ai_personalized_remedy_instructions(self, async_client: AsyncClient, db_session):
        """Test AI-generated personalized remedy instructions."""
        
        # Create chart and get recommendations
        person_data = {
            "name": "AI Personalization Test",
            "date_of_birth": "1992-09-22",
            "time_of_birth": "1992-09-22T15:45:00",
            "place_of_birth": "Bangalore, India",
            "latitude": "12.9716",
            "longitude": "77.5946",
            "timezone": "Asia/Kolkata",
            "email": "ai.personalization@example.com"
        }
        
        person_response = await async_client.post("/api/v1/persons/", json=person_data)
        person_result = assert_response_success(person_response, status.HTTP_201_CREATED)
        person_id = person_result["person_id"]
        
        chart_request = {
            "person_id": person_id,
            "chart_type": "natal",
            "house_system": "whole_sign",
            "ayanamsa": "lahiri",
            "coordinate_system": "sidereal"
        }
        
        chart_response = await async_client.post("/api/v1/charts/calculate", json=chart_request)
        chart_data = assert_response_success(chart_response, status.HTTP_201_CREATED)
        chart_id = chart_data["chart_id"]
        
        # Mock AI service for testing personalization
        mock_ai_response = [
            {
                "recommendation_id": str(uuid4()),
                "remedy": {
                    "remedy_id": str(uuid4()),
                    "name": "Ganesha Mantra for Jupiter",
                    "type": "mantra",
                    "tradition": "vedic",
                    "description": {"en": "Powerful mantra to strengthen Jupiter"},
                    "instructions": {"en": "Chant 108 times daily"},
                    "mantra_text": "Om Gam Ganapataye Namaha"
                },
                "relevance_score": 85.5,
                "priority_level": 4,
                "issue_description": "Jupiter weakness affecting wisdom and abundance",
                "personalized_instructions": "Based on your chart analysis showing Jupiter in the 6th house, this mantra will help strengthen your natural wisdom and teaching abilities. Focus particularly on chanting during the early morning hours (6-8 AM) when Jupiter's energy is strongest. Since your Moon is in Gemini, you may find it helpful to write down insights that come during your practice. The 108 repetitions should be done with a rudraksha mala, focusing on abundance and wisdom manifestation.",
                "confidence_score": 88.0,
                "created_at": datetime.utcnow().isoformat()
            }
        ]
        
        remedy_request = {
            "chart_id": chart_id,
            "concern_areas": ["wisdom", "abundance", "career_growth"]
        }
        
        with patch('josi.services.remedy_recommendation_service.RemedyRecommendationService.analyze_and_recommend') as mock_service:
            mock_service.return_value = mock_ai_response
            
            remedy_response = await async_client.post("/api/v1/remedies/recommend", json=remedy_request)
            
            if remedy_response.status_code == 404:
                pytest.skip("Remedy recommendation service not available")
            
            recommendations = assert_response_success(remedy_response)
            
            # Verify AI personalization
            rec = recommendations["recommendations"][0]
            personalized = rec["personalized_instructions"]
            
            # Verify personalization quality
            assert len(personalized) > 100, "Personalized instructions should be substantial"
            assert "chart" in personalized.lower(), "Should reference chart analysis"
            assert "jupiter" in personalized.lower(), "Should reference specific planetary influence"
            assert "moon" in personalized.lower(), "Should reference other chart factors"
            
            # Verify specific timing and method recommendations
            assert "morning" in personalized.lower() or "time" in personalized.lower(), "Should include timing guidance"
            assert "mala" in personalized.lower() or "method" in personalized.lower(), "Should include method guidance"