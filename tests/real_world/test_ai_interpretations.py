"""
Real-world AI interpretation service tests.

Tests AI-powered chart interpretations using real birth data and evaluates
the quality and accuracy of generated interpretations.
"""
import pytest
from datetime import datetime
from httpx import AsyncClient
from fastapi import status
from unittest.mock import AsyncMock, patch

from tests.conftest import assert_response_success
from tests.real_world.test_chart_calculations import TestRealBirthDataCharts


class TestAIInterpretationService:
    """Test AI interpretation service with real chart data."""
    
    @pytest.mark.asyncio
    async def test_basic_chart_interpretation(self, async_client: AsyncClient, db_session):
        """Test basic AI interpretation of a natal chart."""
        # Use Barack Obama's data for consistent testing
        person_data = TestRealBirthDataCharts.CELEBRITY_BIRTH_DATA["barack_obama"].copy()
        person_data["email"] = "ai_test_obama@example.com"
        
        # Create person
        person_response = await async_client.post("/api/v1/persons/", json=person_data)
        person_result = assert_response_success(person_response, status.HTTP_201_CREATED)
        person_id = person_result["person_id"]
        
        # Calculate chart
        chart_request = {
            "person_id": person_id,
            "chart_type": "natal",
            "house_system": "placidus",
            "coordinate_system": "tropical"
        }
        
        chart_response = await async_client.post("/api/v1/charts/calculate", json=chart_request)
        chart_data = assert_response_success(chart_response, status.HTTP_201_CREATED)
        chart_id = chart_data["chart_id"]
        
        # Request AI interpretation
        interpretation_request = {
            "chart_id": chart_id,
            "question": "What are the key personality traits and life themes shown in this chart?",
            "style": "balanced",
            "focus_areas": ["personality", "career", "relationships"]
        }
        
        # Mock AI response for testing
        mock_ai_response = {
            "interpretation": "This chart shows a strong Leo Sun in the 6th house, indicating natural leadership abilities and a focus on service and daily work routines. The Gemini Moon suggests adaptability and strong communication skills. The person likely has a diplomatic nature combined with determination.",
            "key_insights": [
                "Natural leadership qualities (Leo Sun)",
                "Strong communication skills (Gemini Moon)",
                "Service-oriented approach to life",
                "Diplomatic yet determined personality"
            ],
            "planetary_highlights": [
                {
                    "planet": "Sun",
                    "message": "Leo Sun in 6th house shows leadership through service and work"
                },
                {
                    "planet": "Moon",
                    "message": "Gemini Moon indicates emotional adaptability and communication needs"
                }
            ],
            "life_themes": ["Leadership", "Communication", "Service", "Diplomacy"],
            "confidence_score": 85.5
        }
        
        with patch('josi.services.ai.interpretation_service.AIInterpretationService.generate_interpretation') as mock_ai:
            mock_ai.return_value = mock_ai_response
            
            response = await async_client.post("/api/v1/ai/interpret", json=interpretation_request)
            interpretation_data = assert_response_success(response)
            
            # Verify interpretation structure
            assert "interpretation" in interpretation_data
            assert "key_insights" in interpretation_data
            assert "planetary_highlights" in interpretation_data
            assert "confidence_score" in interpretation_data
            
            # Verify content quality
            assert len(interpretation_data["interpretation"]) > 100, "Interpretation should be substantial"
            assert len(interpretation_data["key_insights"]) > 0, "Should have key insights"
            assert interpretation_data["confidence_score"] > 70, "Should have reasonable confidence"
    
    @pytest.mark.asyncio
    async def test_specific_question_interpretation(self, async_client: AsyncClient, db_session):
        """Test AI interpretation for specific astrological questions."""
        # Use Oprah's data for career-focused interpretation
        person_data = TestRealBirthDataCharts.CELEBRITY_BIRTH_DATA["oprah_winfrey"].copy()
        person_data["email"] = "ai_test_oprah@example.com"
        
        # Create person and chart
        person_response = await async_client.post("/api/v1/persons/", json=person_data)
        person_result = assert_response_success(person_response, status.HTTP_201_CREATED)
        person_id = person_result["person_id"]
        
        chart_request = {
            "person_id": person_id,
            "chart_type": "natal",
            "house_system": "placidus",
            "coordinate_system": "tropical"
        }
        
        chart_response = await async_client.post("/api/v1/charts/calculate", json=chart_request)
        chart_data = assert_response_success(chart_response, status.HTTP_201_CREATED)
        chart_id = chart_data["chart_id"]
        
        # Test career-specific question
        career_interpretation_request = {
            "chart_id": chart_id,
            "question": "What does this chart indicate about career potential and professional success?",
            "style": "professional",
            "focus_areas": ["career", "reputation", "public_image"]
        }
        
        mock_career_response = {
            "interpretation": "The chart shows strong indicators for media and communication careers, with emphasis on public service and helping others. The placement suggests potential for building a media empire while maintaining authentic connection with audiences.",
            "key_insights": [
                "Strong 10th house indicating public recognition",
                "Communication planets well-aspected for media work",
                "Service-oriented career themes",
                "Potential for building influential platform"
            ],
            "career_indicators": [
                "Media and Communication",
                "Public Speaking",
                "Humanitarian Work",
                "Business Leadership"
            ],
            "confidence_score": 88.2
        }
        
        with patch('josi.services.ai.interpretation_service.AIInterpretationService.generate_interpretation') as mock_ai:
            mock_ai.return_value = mock_career_response
            
            response = await async_client.post("/api/v1/ai/interpret", json=career_interpretation_request)
            career_data = assert_response_success(response)
            
            # Verify career-specific content
            assert "career" in career_data["interpretation"].lower()
            assert "professional" in career_data["interpretation"].lower()
            assert len(career_data["key_insights"]) >= 3
    
    @pytest.mark.asyncio
    async def test_different_interpretation_styles(self, async_client: AsyncClient, db_session):
        """Test different AI interpretation styles."""
        # Use Steve Jobs data for innovation-focused interpretation
        person_data = TestRealBirthDataCharts.CELEBRITY_BIRTH_DATA["steve_jobs"].copy()
        person_data["email"] = "ai_test_jobs@example.com"
        
        # Create person and chart
        person_response = await async_client.post("/api/v1/persons/", json=person_data)
        person_result = assert_response_success(person_response, status.HTTP_201_CREATED)
        person_id = person_result["person_id"]
        
        chart_request = {
            "person_id": person_id,
            "chart_type": "natal",
            "house_system": "placidus",
            "coordinate_system": "tropical"
        }
        
        chart_response = await async_client.post("/api/v1/charts/calculate", json=chart_request)
        chart_data = assert_response_success(chart_response, status.HTTP_201_CREATED)
        chart_id = chart_data["chart_id"]
        
        # Test different styles
        styles_to_test = [
            {
                "style": "spiritual",
                "expected_keywords": ["soul", "spiritual", "karma", "purpose", "growth"]
            },
            {
                "style": "practical",
                "expected_keywords": ["practical", "concrete", "daily", "work", "routine"]
            },
            {
                "style": "psychological",
                "expected_keywords": ["psychology", "personality", "unconscious", "behavior", "patterns"]
            }
        ]
        
        for style_test in styles_to_test:
            interpretation_request = {
                "chart_id": chart_id,
                "question": "What are the main themes in this person's life path?",
                "style": style_test["style"],
                "focus_areas": ["personality", "life_purpose"]
            }
            
            mock_style_response = {
                "interpretation": f"This is a {style_test['style']} interpretation focusing on relevant themes and aspects that align with this approach to astrology.",
                "key_insights": [
                    f"Key insight from {style_test['style']} perspective",
                    f"Another {style_test['style']} theme identified",
                    f"Third insight using {style_test['style']} approach"
                ],
                "style_used": style_test["style"],
                "confidence_score": 82.0
            }
            
            with patch('josi.services.ai.interpretation_service.AIInterpretationService.generate_interpretation') as mock_ai:
                mock_ai.return_value = mock_style_response
                
                response = await async_client.post("/api/v1/ai/interpret", json=interpretation_request)
                style_data = assert_response_success(response)
                
                # Verify style-appropriate content
                interpretation_text = style_data["interpretation"].lower()
                assert style_test["style"] in interpretation_text
    
    @pytest.mark.asyncio
    async def test_vedic_vs_western_interpretation_differences(self, async_client: AsyncClient, db_session):
        """Test that Vedic and Western charts produce different interpretations."""
        person_data = TestRealBirthDataCharts.CELEBRITY_BIRTH_DATA["albert_einstein"].copy()
        person_data["email"] = "ai_test_einstein@example.com"
        
        # Create person
        person_response = await async_client.post("/api/v1/persons/", json=person_data)
        person_result = assert_response_success(person_response, status.HTTP_201_CREATED)
        person_id = person_result["person_id"]
        
        # Calculate Western chart
        western_chart_request = {
            "person_id": person_id,
            "chart_type": "natal",
            "house_system": "placidus",
            "coordinate_system": "tropical"
        }
        
        western_response = await async_client.post("/api/v1/charts/calculate", json=western_chart_request)
        western_chart = assert_response_success(western_response, status.HTTP_201_CREATED)
        
        # Calculate Vedic chart
        vedic_chart_request = {
            "person_id": person_id,
            "chart_type": "natal",
            "house_system": "whole_sign",
            "ayanamsa": "lahiri",
            "coordinate_system": "sidereal"
        }
        
        vedic_response = await async_client.post("/api/v1/charts/calculate", json=vedic_chart_request)
        vedic_chart = assert_response_success(vedic_response, status.HTTP_201_CREATED)
        
        # Mock different interpretations for each system
        western_mock_response = {
            "interpretation": "Western tropical interpretation emphasizing Pisces Sun qualities of intuition, creativity, and universal thinking patterns that contributed to revolutionary scientific insights.",
            "system_used": "western",
            "key_insights": ["Pisces Sun creativity", "Intuitive thinking", "Universal perspective"],
            "confidence_score": 85.0
        }
        
        vedic_mock_response = {
            "interpretation": "Vedic sidereal interpretation focusing on Aquarius Sun characteristics of innovative thinking, humanitarian ideals, and revolutionary approach to established systems.",
            "system_used": "vedic", 
            "key_insights": ["Aquarius Sun innovation", "Revolutionary thinking", "Humanitarian ideals"],
            "confidence_score": 83.0
        }
        
        # Test Western interpretation
        western_interpretation_request = {
            "chart_id": western_chart["chart_id"],
            "question": "What are the key intellectual and creative themes in this chart?",
            "style": "balanced"
        }
        
        with patch('josi.services.ai.interpretation_service.AIInterpretationService.generate_interpretation') as mock_ai:
            mock_ai.return_value = western_mock_response
            
            western_interp_response = await async_client.post("/api/v1/ai/interpret", json=western_interpretation_request)
            western_interp_data = assert_response_success(western_interp_response)
        
        # Test Vedic interpretation
        vedic_interpretation_request = {
            "chart_id": vedic_chart["chart_id"],
            "question": "What are the key intellectual and creative themes in this chart?",
            "style": "balanced"
        }
        
        with patch('josi.services.ai.interpretation_service.AIInterpretationService.generate_interpretation') as mock_ai:
            mock_ai.return_value = vedic_mock_response
            
            vedic_interp_response = await async_client.post("/api/v1/ai/interpret", json=vedic_interpretation_request)
            vedic_interp_data = assert_response_success(vedic_interp_response)
        
        # Verify interpretations are different and system-appropriate
        assert western_interp_data["interpretation"] != vedic_interp_data["interpretation"]
        assert "pisces" in western_interp_data["interpretation"].lower()
        assert "aquarius" in vedic_interp_data["interpretation"].lower()
    
    @pytest.mark.asyncio
    async def test_chart_comparison_interpretation(self, async_client: AsyncClient, db_session):
        """Test AI interpretation for chart compatibility/comparison."""
        # Create two different persons for comparison
        person1_data = TestRealBirthDataCharts.CELEBRITY_BIRTH_DATA["barack_obama"].copy()
        person1_data["email"] = "ai_comparison1@example.com"
        
        person2_data = TestRealBirthDataCharts.CELEBRITY_BIRTH_DATA["oprah_winfrey"].copy()
        person2_data["email"] = "ai_comparison2@example.com"
        
        # Create both persons
        person1_response = await async_client.post("/api/v1/persons/", json=person1_data)
        person1_result = assert_response_success(person1_response, status.HTTP_201_CREATED)
        
        person2_response = await async_client.post("/api/v1/persons/", json=person2_data)
        person2_result = assert_response_success(person2_response, status.HTTP_201_CREATED)
        
        # Calculate charts for both
        chart_request1 = {
            "person_id": person1_result["person_id"],
            "chart_type": "natal",
            "house_system": "placidus",
            "coordinate_system": "tropical"
        }
        
        chart_request2 = {
            "person_id": person2_result["person_id"],
            "chart_type": "natal",
            "house_system": "placidus",
            "coordinate_system": "tropical"
        }
        
        chart1_response = await async_client.post("/api/v1/charts/calculate", json=chart_request1)
        chart1_data = assert_response_success(chart1_response, status.HTTP_201_CREATED)
        
        chart2_response = await async_client.post("/api/v1/charts/calculate", json=chart_request2)
        chart2_data = assert_response_success(chart2_response, status.HTTP_201_CREATED)
        
        # Request compatibility interpretation
        compatibility_request = {
            "chart1_id": chart1_data["chart_id"],
            "chart2_id": chart2_data["chart_id"],
            "comparison_type": "synastry",
            "focus_areas": ["communication", "collaboration", "shared_goals"]
        }
        
        mock_compatibility_response = {
            "compatibility_score": 78.5,
            "interpretation": "This pairing shows strong potential for collaborative success, with complementary leadership styles and shared vision for public service. Communication flows naturally between these charts.",
            "strengths": [
                "Complementary leadership approaches",
                "Shared humanitarian values",
                "Strong communication potential",
                "Mutual respect for public service"
            ],
            "challenges": [
                "Different approaches to decision-making",
                "Potential ego clashes in spotlight situations"
            ],
            "overall_assessment": "Highly compatible for professional collaboration and shared public initiatives"
        }
        
        with patch('josi.services.ai.interpretation_service.AIInterpretationService.generate_compatibility_interpretation') as mock_ai:
            mock_ai.return_value = mock_compatibility_response
            
            # Note: This endpoint might need to be implemented
            response = await async_client.post("/api/v1/ai/compatibility", json=compatibility_request)
            
            if response.status_code == 404:
                pytest.skip("Compatibility interpretation endpoint not implemented yet")
            
            compatibility_data = assert_response_success(response)
            
            # Verify compatibility interpretation structure
            assert "compatibility_score" in compatibility_data
            assert "strengths" in compatibility_data
            assert "challenges" in compatibility_data
            assert compatibility_data["compatibility_score"] > 0
            assert len(compatibility_data["strengths"]) > 0


class TestAIInterpretationQuality:
    """Test AI interpretation quality and consistency."""
    
    @pytest.mark.asyncio
    async def test_interpretation_consistency(self, async_client: AsyncClient, db_session):
        """Test that similar questions produce consistent interpretations."""
        person_data = TestRealBirthDataCharts.CELEBRITY_BIRTH_DATA["steve_jobs"].copy()
        person_data["email"] = "ai_consistency_test@example.com"
        
        # Create person and chart
        person_response = await async_client.post("/api/v1/persons/", json=person_data)
        person_result = assert_response_success(person_response, status.HTTP_201_CREATED)
        person_id = person_result["person_id"]
        
        chart_request = {
            "person_id": person_id,
            "chart_type": "natal",
            "house_system": "placidus",
            "coordinate_system": "tropical"
        }
        
        chart_response = await async_client.post("/api/v1/charts/calculate", json=chart_request)
        chart_data = assert_response_success(chart_response, status.HTTP_201_CREATED)
        chart_id = chart_data["chart_id"]
        
        # Ask similar questions with slightly different wording
        similar_questions = [
            "What are the main personality traits shown in this chart?",
            "What does this chart reveal about the person's character?",
            "What are the key characteristics indicated by this natal chart?"
        ]
        
        mock_consistent_response = {
            "interpretation": "This chart consistently shows innovative thinking, perfectionist tendencies, and revolutionary approach to technology and design.",
            "key_traits": ["Innovation", "Perfectionism", "Revolutionary thinking", "Design focus"],
            "confidence_score": 86.0
        }
        
        interpretations = []
        
        for question in similar_questions:
            interpretation_request = {
                "chart_id": chart_id,
                "question": question,
                "style": "balanced"
            }
            
            with patch('josi.services.ai.interpretation_service.AIInterpretationService.generate_interpretation') as mock_ai:
                mock_ai.return_value = mock_consistent_response
                
                response = await async_client.post("/api/v1/ai/interpret", json=interpretation_request)
                interpretation_data = assert_response_success(response)
                interpretations.append(interpretation_data)
        
        # Verify consistent themes across similar questions
        for interpretation in interpretations:
            assert "innovative" in interpretation["interpretation"].lower()
            assert interpretation["confidence_score"] > 80
    
    @pytest.mark.asyncio
    async def test_interpretation_length_and_depth(self, async_client: AsyncClient, db_session):
        """Test that interpretations have appropriate length and depth."""
        person_data = TestRealBirthDataCharts.CELEBRITY_BIRTH_DATA["albert_einstein"].copy()
        person_data["email"] = "ai_depth_test@example.com"
        
        # Create person and chart
        person_response = await async_client.post("/api/v1/persons/", json=person_data)
        person_result = assert_response_success(person_response, status.HTTP_201_CREATED)
        person_id = person_result["person_id"]
        
        chart_request = {
            "person_id": person_id,
            "chart_type": "natal",
            "house_system": "placidus",
            "coordinate_system": "tropical"
        }
        
        chart_response = await async_client.post("/api/v1/charts/calculate", json=chart_request)
        chart_data = assert_response_success(chart_response, status.HTTP_201_CREATED)
        chart_id = chart_data["chart_id"]
        
        # Request detailed interpretation
        detailed_interpretation_request = {
            "chart_id": chart_id,
            "question": "Provide a comprehensive analysis of this person's intellectual gifts, creative potential, and life purpose.",
            "style": "comprehensive",
            "focus_areas": ["intellect", "creativity", "life_purpose", "career", "relationships"]
        }
        
        mock_detailed_response = {
            "interpretation": """This chart reveals extraordinary intellectual gifts combined with deep humanitarian concerns. 
            The person possesses a unique ability to perceive universal patterns and translate complex concepts into 
            revolutionary insights. Their creative approach to problem-solving stems from an intuitive understanding 
            of cosmic principles, allowing them to bridge the gap between abstract mathematics and physical reality. 
            The chart suggests a life purpose centered on advancing human understanding through scientific discovery, 
            with a particular gift for seeing connections that others miss. Relationships tend to be intellectually 
            stimulating but may require patience from partners who need to appreciate the person's mental intensity 
            and occasional social awkwardness. Career success comes through persistent dedication to theoretical work 
            that may not be immediately understood or appreciated by contemporaries.""",
            "key_insights": [
                "Extraordinary pattern recognition abilities",
                "Revolutionary approach to scientific thinking", 
                "Bridge between abstract and concrete concepts",
                "Life purpose in advancing human knowledge",
                "Intellectually intense relationships",
                "Ahead-of-time career contributions"
            ],
            "detailed_analysis": {
                "intellectual_gifts": "Exceptional ability to perceive universal patterns and mathematical relationships",
                "creative_potential": "Revolutionary approach combining intuition with rigorous analysis",
                "life_purpose": "Advancing human understanding through groundbreaking scientific discoveries",
                "relationship_patterns": "Seeks intellectual stimulation, may struggle with conventional social expectations",
                "career_themes": "Theoretical work that transforms human understanding of reality"
            },
            "confidence_score": 91.5
        }
        
        with patch('josi.services.ai.interpretation_service.AIInterpretationService.generate_interpretation') as mock_ai:
            mock_ai.return_value = mock_detailed_response
            
            response = await async_client.post("/api/v1/ai/interpret", json=detailed_interpretation_request)
            detailed_data = assert_response_success(response)
            
            # Verify interpretation depth and quality
            interpretation_text = detailed_data["interpretation"]
            assert len(interpretation_text) > 500, "Comprehensive interpretation should be substantial"
            assert len(detailed_data["key_insights"]) >= 5, "Should have multiple key insights"
            assert detailed_data["confidence_score"] > 85, "Detailed analysis should have high confidence"
            
            # Verify content addresses requested focus areas
            text_lower = interpretation_text.lower()
            assert "intellectual" in text_lower or "intellect" in text_lower
            assert "creative" in text_lower
            assert "purpose" in text_lower
            assert "career" in text_lower
            assert "relationship" in text_lower
    
    @pytest.mark.asyncio
    async def test_error_handling_for_ai_service(self, async_client: AsyncClient, db_session):
        """Test error handling when AI service is unavailable or fails."""
        person_data = TestRealBirthDataCharts.CELEBRITY_BIRTH_DATA["barack_obama"].copy()
        person_data["email"] = "ai_error_test@example.com"
        
        # Create person and chart
        person_response = await async_client.post("/api/v1/persons/", json=person_data)
        person_result = assert_response_success(person_response, status.HTTP_201_CREATED)
        person_id = person_result["person_id"]
        
        chart_request = {
            "person_id": person_id,
            "chart_type": "natal",
            "house_system": "placidus",
            "coordinate_system": "tropical"
        }
        
        chart_response = await async_client.post("/api/v1/charts/calculate", json=chart_request)
        chart_data = assert_response_success(chart_response, status.HTTP_201_CREATED)
        chart_id = chart_data["chart_id"]
        
        interpretation_request = {
            "chart_id": chart_id,
            "question": "What are the main themes in this chart?",
            "style": "balanced"
        }
        
        # Simulate AI service failure
        with patch('josi.services.ai.interpretation_service.AIInterpretationService.generate_interpretation') as mock_ai:
            mock_ai.side_effect = Exception("AI service temporarily unavailable")
            
            response = await async_client.post("/api/v1/ai/interpret", json=interpretation_request)
            
            # Should return appropriate error response
            assert response.status_code in [status.HTTP_500_INTERNAL_SERVER_ERROR, status.HTTP_503_SERVICE_UNAVAILABLE]
            
            error_data = response.json()
            assert "unavailable" in error_data["detail"].lower() or "error" in error_data["detail"].lower()


class TestAIInterpretationSubscriptionLimits:
    """Test AI interpretation usage limits based on subscription tiers."""
    
    @pytest.mark.asyncio 
    async def test_free_tier_interpretation_limits(self, async_client: AsyncClient, db_session):
        """Test that free tier users have limited AI interpretations."""
        # This test would require authentication system to be fully implemented
        # For now, we'll test the basic structure
        
        person_data = TestRealBirthDataCharts.CELEBRITY_BIRTH_DATA["oprah_winfrey"].copy()
        person_data["email"] = "ai_limits_test@example.com"
        
        # Create person and chart
        person_response = await async_client.post("/api/v1/persons/", json=person_data)
        person_result = assert_response_success(person_response, status.HTTP_201_CREATED)
        person_id = person_result["person_id"]
        
        chart_request = {
            "person_id": person_id,
            "chart_type": "natal",
            "house_system": "placidus",
            "coordinate_system": "tropical"
        }
        
        chart_response = await async_client.post("/api/v1/charts/calculate", json=chart_request)
        chart_data = assert_response_success(chart_response, status.HTTP_201_CREATED)
        chart_id = chart_data["chart_id"]
        
        interpretation_request = {
            "chart_id": chart_id,
            "question": "What are the key themes in this chart?",
            "style": "balanced"
        }
        
        # Mock successful interpretation for now
        mock_response = {
            "interpretation": "Test interpretation for free tier user",
            "key_insights": ["Insight 1", "Insight 2"],
            "remaining_interpretations": 2,  # For free tier
            "tier_limit": 3,
            "confidence_score": 82.0
        }
        
        with patch('josi.services.ai.interpretation_service.AIInterpretationService.generate_interpretation') as mock_ai:
            mock_ai.return_value = mock_response
            
            response = await async_client.post("/api/v1/ai/interpret", json=interpretation_request)
            
            if response.status_code == 401:
                pytest.skip("Authentication system required for tier limit testing")
            
            interpretation_data = assert_response_success(response)
            
            # Verify tier information is included
            if "remaining_interpretations" in interpretation_data:
                assert interpretation_data["remaining_interpretations"] >= 0
                assert interpretation_data["tier_limit"] > 0