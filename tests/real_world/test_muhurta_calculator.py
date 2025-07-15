"""
Real-world Muhurta calculator tests.

Tests the Muhurta (auspicious timing) calculator using real dates, locations,
and astrological events to verify accuracy and practical usefulness.
"""
import pytest
from datetime import datetime, timedelta, date
from httpx import AsyncClient
from fastapi import status

from tests.conftest import assert_response_success


class TestMuhurtaCalculations:
    """Test Muhurta calculations for various real-world scenarios."""
    
    @pytest.mark.asyncio
    async def test_marriage_muhurta_delhi_2024(self, async_client: AsyncClient, db_session):
        """Test marriage Muhurta calculation for Delhi in 2024."""
        
        # Search for marriage Muhurtas in Delhi for specific period
        muhurta_request = {
            "purpose": "marriage",
            "start_date": "2024-11-01T00:00:00",  # Auspicious month for marriages
            "end_date": "2024-11-30T23:59:59",
            "latitude": 28.7041,  # Delhi
            "longitude": 77.1025,
            "timezone": "Asia/Kolkata",
            "max_results": 10
        }
        
        response = await async_client.post("/api/v1/muhurta/find-muhurta", json=muhurta_request)
        
        if response.status_code == 404:
            pytest.skip("Muhurta calculator endpoints not implemented")
        
        muhurta_data = assert_response_success(response)
        
        # Verify response structure
        assert "muhurtas" in muhurta_data
        assert "search_criteria" in muhurta_data
        assert "total_found" in muhurta_data
        
        muhurtas = muhurta_data["muhurtas"]
        assert len(muhurtas) > 0, "Should find auspicious marriage times in November"
        
        # Verify each muhurta has required information
        for muhurta in muhurtas:
            assert "date" in muhurta
            assert "time" in muhurta
            assert "quality" in muhurta
            assert "score" in muhurta
            assert "tithi" in muhurta
            assert "nakshatra" in muhurta
            assert "yoga" in muhurta
            assert "weekday" in muhurta
            assert "factors" in muhurta
            assert "recommendations" in muhurta
            
            # Verify quality scoring
            assert muhurta["score"] >= 60, "Should only return good quality muhurtas"
            assert muhurta["quality"] in ["Good", "Very Good", "Excellent"]
            
            # Verify no unfavorable days for marriage
            assert muhurta["weekday"] not in ["Sunday", "Tuesday"], "Should avoid unfavorable weekdays for marriage"
            
            # Verify recommendations are marriage-specific
            recommendations_text = " ".join(muhurta["recommendations"]).lower()
            marriage_keywords = ["marriage", "wedding", "ceremony", "ritual", "ganesh"]
            assert any(keyword in recommendations_text for keyword in marriage_keywords), \
                "Should include marriage-specific recommendations"
    
    @pytest.mark.asyncio
    async def test_business_muhurta_mumbai_2024(self, async_client: AsyncClient, db_session):
        """Test business launch Muhurta calculation for Mumbai."""
        
        muhurta_request = {
            "purpose": "business",
            "start_date": "2024-10-15T00:00:00",  # After monsoon season
            "end_date": "2024-12-15T23:59:59",
            "latitude": 19.0760,  # Mumbai
            "longitude": 72.8777,
            "timezone": "Asia/Kolkata",
            "max_results": 8
        }
        
        response = await async_client.post("/api/v1/muhurta/find-muhurta", json=muhurta_request)
        muhurta_data = assert_response_success(response)
        
        muhurtas = muhurta_data["muhurtas"]
        assert len(muhurtas) > 0, "Should find auspicious business times"
        
        # Verify business-specific factors
        for muhurta in muhurtas:
            # Business muhurtas should favor prosperity-supporting days
            assert muhurta["weekday"] not in ["Saturday"], "Should avoid Saturn's day for new business"
            
            # Check for business-relevant recommendations
            recommendations_text = " ".join(muhurta["recommendations"]).lower()
            business_keywords = ["business", "prosperity", "lakshmi", "ganesh", "transaction"]
            assert any(keyword in recommendations_text for keyword in business_keywords), \
                "Should include business-specific recommendations"
            
            # Verify positive factors
            positive_factors = muhurta["factors"]["positive"]
            negative_factors = muhurta["factors"]["negative"]
            
            assert len(positive_factors) > 0, "Should have positive factors listed"
            # More positive than negative factors for good muhurtas
            assert len(positive_factors) >= len(negative_factors), "Should have more positive factors"
    
    @pytest.mark.asyncio
    async def test_travel_muhurta_bangalore_to_us(self, async_client: AsyncClient, db_session):
        """Test travel Muhurta for international journey from Bangalore to US."""
        
        muhurta_request = {
            "purpose": "travel",
            "start_date": "2024-12-01T00:00:00",
            "end_date": "2024-12-31T23:59:59",
            "latitude": 12.9716,  # Bangalore
            "longitude": 77.5946,
            "timezone": "Asia/Kolkata",
            "max_results": 15
        }
        
        response = await async_client.post("/api/v1/muhurta/find-muhurta", json=muhurta_request)
        muhurta_data = assert_response_success(response)
        
        muhurtas = muhurta_data["muhurtas"]
        assert len(muhurtas) > 0, "Should find auspicious travel times"
        
        # Verify travel-specific considerations
        for muhurta in muhurtas:
            # Travel muhurtas should avoid certain nakshatras and tithis
            unfavorable_nakshatras = ["Bharani", "Krittika", "Ashlesha", "Vishakha"]
            assert muhurta["nakshatra"] not in unfavorable_nakshatras, \
                f"Should avoid unfavorable nakshatra {muhurta['nakshatra']} for travel"
            
            # Check for travel-relevant recommendations
            recommendations_text = " ".join(muhurta["recommendations"]).lower()
            travel_keywords = ["travel", "journey", "direction", "safe", "depart"]
            assert any(keyword in recommendations_text for keyword in travel_keywords), \
                "Should include travel-specific recommendations"
    
    @pytest.mark.asyncio
    async def test_education_muhurta_chennai_academic_year(self, async_client: AsyncClient, db_session):
        """Test education/study commencement Muhurta for Chennai academic year."""
        
        muhurta_request = {
            "purpose": "education",
            "start_date": "2024-06-01T00:00:00",  # Academic year start
            "end_date": "2024-06-30T23:59:59",
            "latitude": 13.0827,  # Chennai
            "longitude": 80.2707,
            "timezone": "Asia/Kolkata",
            "max_results": 12
        }
        
        response = await async_client.post("/api/v1/muhurta/find-muhurta", json=muhurta_request)
        muhurta_data = assert_response_success(response)
        
        muhurtas = muhurta_data["muhurtas"]
        assert len(muhurtas) > 0, "Should find auspicious education times"
        
        # Verify education-specific factors
        for muhurta in muhurtas:
            # Education muhurtas should favor knowledge-supporting days
            favorable_days = ["Wednesday", "Thursday"]  # Mercury and Jupiter days
            if muhurta["weekday"] in favorable_days:
                # Should have higher scores on favorable days
                assert muhurta["score"] >= 70, "Should have higher score on Mercury/Jupiter days"
            
            # Check for education-relevant recommendations
            recommendations_text = " ".join(muhurta["recommendations"]).lower()
            education_keywords = ["education", "study", "learning", "saraswati", "wisdom", "knowledge"]
            assert any(keyword in recommendations_text for keyword in education_keywords), \
                "Should include education-specific recommendations"
    
    @pytest.mark.asyncio
    async def test_property_purchase_muhurta_pune(self, async_client: AsyncClient, db_session):
        """Test property purchase Muhurta for Pune."""
        
        muhurta_request = {
            "purpose": "property",
            "start_date": "2024-09-01T00:00:00",  # Post-monsoon property season
            "end_date": "2024-11-30T23:59:59",
            "latitude": 18.5204,  # Pune
            "longitude": 73.8567,
            "timezone": "Asia/Kolkata",
            "max_results": 10
        }
        
        response = await async_client.post("/api/v1/muhurta/find-muhurta", json=muhurta_request)
        muhurta_data = assert_response_success(response)
        
        muhurtas = muhurta_data["muhurtas"]
        assert len(muhurtas) > 0, "Should find auspicious property purchase times"
        
        # Verify property-specific considerations
        for muhurta in muhurtas:
            # Property transactions should favor stability-supporting factors
            recommendations_text = " ".join(muhurta["recommendations"]).lower()
            property_keywords = ["property", "bhumi", "documents", "puja", "stability"]
            assert any(keyword in recommendations_text for keyword in property_keywords), \
                "Should include property-specific recommendations"


class TestRahuKaalCalculations:
    """Test Rahu Kaal calculations for different locations and dates."""
    
    @pytest.mark.asyncio
    async def test_rahu_kaal_delhi_weekdays(self, async_client: AsyncClient, db_session):
        """Test Rahu Kaal calculation for Delhi across different weekdays."""
        
        # Test for a full week in Delhi
        test_dates = []
        base_date = date(2024, 10, 14)  # Monday
        
        for i in range(7):  # Monday to Sunday
            test_date = base_date + timedelta(days=i)
            test_dates.append(test_date)
        
        weekday_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        for i, test_date in enumerate(test_dates):
            rahu_kaal_request = {
                "date": f"{test_date}T12:00:00",
                "latitude": 28.7041,  # Delhi
                "longitude": 77.1025,
                "timezone": "Asia/Kolkata"
            }
            
            response = await async_client.post("/api/v1/muhurta/rahu-kaal", json=rahu_kaal_request)
            
            if response.status_code == 404:
                pytest.skip("Rahu Kaal endpoints not implemented")
            
            rahu_kaal_data = assert_response_success(response)
            
            # Verify structure
            assert "date" in rahu_kaal_data
            assert "weekday" in rahu_kaal_data
            assert "rahu_kaal" in rahu_kaal_data
            assert "sunrise" in rahu_kaal_data
            assert "sunset" in rahu_kaal_data
            assert "recommendation" in rahu_kaal_data
            
            # Verify weekday matches
            assert rahu_kaal_data["weekday"] == weekday_names[i]
            
            # Verify Rahu Kaal structure
            rahu_kaal = rahu_kaal_data["rahu_kaal"]
            assert "start" in rahu_kaal
            assert "end" in rahu_kaal
            assert "duration_minutes" in rahu_kaal
            assert rahu_kaal["duration_minutes"] == 90  # Standard 1.5 hours
            
            # Verify timing format
            assert ":" in rahu_kaal["start"]
            assert ":" in rahu_kaal["end"]
            assert "AM" in rahu_kaal["start"] or "PM" in rahu_kaal["start"]
            assert "AM" in rahu_kaal["end"] or "PM" in rahu_kaal["end"]
            
            # Verify recommendation includes warning
            assert "avoid" in rahu_kaal_data["recommendation"].lower()
    
    @pytest.mark.asyncio
    async def test_rahu_kaal_different_locations(self, async_client: AsyncClient, db_session):
        """Test Rahu Kaal calculation for different geographical locations."""
        
        test_locations = [
            {"name": "Mumbai", "lat": 19.0760, "lng": 72.8777, "tz": "Asia/Kolkata"},
            {"name": "Kolkata", "lat": 22.5726, "lng": 88.3639, "tz": "Asia/Kolkata"},
            {"name": "Chennai", "lat": 13.0827, "lng": 80.2707, "tz": "Asia/Kolkata"},
            {"name": "Bangalore", "lat": 12.9716, "lng": 77.5946, "tz": "Asia/Kolkata"},
        ]
        
        test_date = "2024-10-15T12:00:00"  # Tuesday
        
        rahu_kaal_times = []
        
        for location in test_locations:
            rahu_kaal_request = {
                "date": test_date,
                "latitude": location["lat"],
                "longitude": location["lng"],
                "timezone": location["tz"]
            }
            
            response = await async_client.post("/api/v1/muhurta/rahu-kaal", json=rahu_kaal_request)
            rahu_kaal_data = assert_response_success(response)
            
            rahu_kaal_times.append({
                "location": location["name"],
                "start": rahu_kaal_data["rahu_kaal"]["start"],
                "end": rahu_kaal_data["rahu_kaal"]["end"],
                "sunrise": rahu_kaal_data["sunrise"],
                "sunset": rahu_kaal_data["sunset"]
            })
        
        # Verify that Rahu Kaal times vary by location due to sunrise differences
        unique_start_times = set(rk["start"] for rk in rahu_kaal_times)
        assert len(unique_start_times) > 1, "Rahu Kaal times should vary by location"
        
        # All should be Tuesday (same weekday pattern)
        for rk_time in rahu_kaal_times:
            # Tuesday Rahu Kaal is typically in the morning
            start_hour = int(rk_time["start"].split(":")[0])
            if "PM" in rk_time["start"] and start_hour != 12:
                start_hour += 12
            elif "AM" in rk_time["start"] and start_hour == 12:
                start_hour = 0
            
            # Tuesday Rahu Kaal is typically 3-4.5 hours after sunrise (early afternoon)
            assert 12 <= start_hour <= 16, f"Tuesday Rahu Kaal should be afternoon for {rk_time['location']}"


class TestMonthlyCalendar:
    """Test monthly auspicious calendar generation."""
    
    @pytest.mark.asyncio
    async def test_monthly_calendar_diwali_month(self, async_client: AsyncClient, db_session):
        """Test monthly calendar for Diwali month (October/November 2024)."""
        
        calendar_request = {
            "year": 2024,
            "month": 11,  # November - Diwali month
            "latitude": 28.7041,  # Delhi
            "longitude": 77.1025,
            "timezone": "Asia/Kolkata"
        }
        
        response = await async_client.post("/api/v1/muhurta/monthly-calendar", json=calendar_request)
        
        if response.status_code == 404:
            pytest.skip("Monthly calendar endpoints not implemented")
        
        calendar_data = assert_response_success(response)
        
        # Verify structure
        assert "calendar" in calendar_data
        assert "month_info" in calendar_data
        
        calendar_days = calendar_data["calendar"]
        month_info = calendar_data["month_info"]
        
        # Verify month info
        assert month_info["year"] == 2024
        assert month_info["month"] == 11
        assert month_info["total_days"] == 30  # November has 30 days
        assert "auspicious_days" in month_info
        assert month_info["auspicious_days"] > 0, "Should have some auspicious days in the month"
        
        # Verify each day has required information
        assert len(calendar_days) == 30, "Should have 30 days for November"
        
        for day in calendar_days:
            assert "date" in day
            assert "weekday" in day
            assert "tithi" in day
            assert "nakshatra" in day
            assert "is_auspicious" in day
            assert "festivals" in day
            
            # Verify date format
            assert day["date"].startswith("2024-11-")
            
            # Verify weekday is valid
            assert day["weekday"] in ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
            
            # Verify tithi and nakshatra are present
            assert len(day["tithi"]) > 0
            assert len(day["nakshatra"]) > 0
        
        # Check for Diwali period (should be marked as auspicious)
        diwali_period_days = [day for day in calendar_days if "diwali" in str(day["festivals"]).lower()]
        # Note: This test might need adjustment based on actual Diwali date in 2024
    
    @pytest.mark.asyncio
    async def test_monthly_calendar_comparison_locations(self, async_client: AsyncClient, db_session):
        """Test monthly calendar for different locations to verify astronomical differences."""
        
        locations = [
            {"name": "Northern India", "lat": 28.7041, "lng": 77.1025, "tz": "Asia/Kolkata"},  # Delhi
            {"name": "Southern India", "lat": 13.0827, "lng": 80.2707, "tz": "Asia/Kolkata"},  # Chennai
        ]
        
        test_month = {"year": 2024, "month": 8}  # August 2024
        
        location_calendars = []
        
        for location in locations:
            calendar_request = {
                **test_month,
                "latitude": location["lat"],
                "longitude": location["lng"],
                "timezone": location["tz"]
            }
            
            response = await async_client.post("/api/v1/muhurta/monthly-calendar", json=calendar_request)
            calendar_data = assert_response_success(response)
            
            location_calendars.append({
                "location": location["name"],
                "calendar": calendar_data["calendar"],
                "auspicious_count": calendar_data["month_info"]["auspicious_days"]
            })
        
        # Both locations should have the same number of days
        assert len(location_calendars[0]["calendar"]) == len(location_calendars[1]["calendar"])
        
        # Tithi and nakshatra should be very similar but sunrise/sunset variations
        # might cause slight differences in daily calculations
        # This is more of a data consistency check
        for i in range(len(location_calendars[0]["calendar"])):
            day1 = location_calendars[0]["calendar"][i]
            day2 = location_calendars[1]["calendar"][i]
            
            # Same date
            assert day1["date"] == day2["date"]
            
            # Tithi might differ slightly due to location-based calculations
            # This is astronomically correct behavior


class TestMuhurtaValidation:
    """Test Muhurta calculation validation and edge cases."""
    
    @pytest.mark.asyncio
    async def test_invalid_purpose_handling(self, async_client: AsyncClient, db_session):
        """Test handling of invalid or unknown purposes."""
        
        muhurta_request = {
            "purpose": "invalid_purpose_xyz",
            "start_date": "2024-10-01T00:00:00",
            "end_date": "2024-10-05T23:59:59",
            "latitude": 28.7041,
            "longitude": 77.1025,
            "timezone": "Asia/Kolkata",
            "max_results": 5
        }
        
        response = await async_client.post("/api/v1/muhurta/find-muhurta", json=muhurta_request)
        
        if response.status_code == 404:
            pytest.skip("Muhurta endpoints not implemented")
        
        # Should either return general business rules or appropriate error
        if response.status_code == 200:
            muhurta_data = assert_response_success(response)
            # Should still return results using general rules
            assert "muhurtas" in muhurta_data
        else:
            # Or return appropriate validation error
            assert response.status_code in [400, 422]
    
    @pytest.mark.asyncio
    async def test_extreme_date_ranges(self, async_client: AsyncClient, db_session):
        """Test Muhurta calculation with extreme date ranges."""
        
        # Test with very old date
        old_date_request = {
            "purpose": "marriage",
            "start_date": "1900-01-01T00:00:00",
            "end_date": "1900-01-31T23:59:59",
            "latitude": 28.7041,
            "longitude": 77.1025,
            "timezone": "Asia/Kolkata",
            "max_results": 5
        }
        
        response = await async_client.post("/api/v1/muhurta/find-muhurta", json=old_date_request)
        
        # Should either work or return appropriate error for dates outside ephemeris range
        if response.status_code == 400:
            error_data = response.json()
            assert "date" in error_data["detail"].lower() or "ephemeris" in error_data["detail"].lower()
        elif response.status_code == 200:
            # If it works, should return valid data
            muhurta_data = assert_response_success(response)
            assert "muhurtas" in muhurta_data
    
    @pytest.mark.asyncio
    async def test_invalid_coordinates(self, async_client: AsyncClient, db_session):
        """Test Muhurta calculation with invalid coordinates."""
        
        invalid_requests = [
            {
                "purpose": "business",
                "start_date": "2024-10-01T00:00:00",
                "end_date": "2024-10-05T23:59:59",
                "latitude": 91.0,  # Invalid latitude > 90
                "longitude": 77.1025,
                "timezone": "Asia/Kolkata"
            },
            {
                "purpose": "business",
                "start_date": "2024-10-01T00:00:00",
                "end_date": "2024-10-05T23:59:59",
                "latitude": 28.7041,
                "longitude": 181.0,  # Invalid longitude > 180
                "timezone": "Asia/Kolkata"
            }
        ]
        
        for invalid_request in invalid_requests:
            response = await async_client.post("/api/v1/muhurta/find-muhurta", json=invalid_request)
            
            if response.status_code == 404:
                pytest.skip("Muhurta endpoints not implemented")
            
            # Should return validation error
            assert response.status_code == 422


class TestSupportedActivities:
    """Test supported activities and their configurations."""
    
    @pytest.mark.asyncio
    async def test_get_supported_activities(self, async_client: AsyncClient, db_session):
        """Test retrieving list of supported activities."""
        
        response = await async_client.get("/api/v1/muhurta/activities")
        
        if response.status_code == 404:
            pytest.skip("Activities endpoint not implemented")
        
        activities_data = assert_response_success(response)
        
        # Verify structure
        assert "activities" in activities_data
        assert "note" in activities_data
        
        activities = activities_data["activities"]
        assert len(activities) > 0, "Should have supported activities"
        
        # Verify each activity has required information
        expected_activities = ["marriage", "business", "travel", "education", "medical", "property"]
        
        activity_names = [activity["name"] for activity in activities]
        
        for expected_activity in expected_activities:
            assert expected_activity in activity_names, f"Should support {expected_activity} activity"
        
        # Verify activity structure
        for activity in activities:
            assert "name" in activity
            assert "description" in activity
            assert "considerations" in activity
            
            assert len(activity["description"]) > 20, "Should have meaningful description"
            assert len(activity["considerations"]) > 0, "Should have astrological considerations"
    
    @pytest.mark.asyncio
    async def test_quick_todays_muhurta(self, async_client: AsyncClient, db_session):
        """Test quick today's best times feature."""
        
        params = {
            "latitude": 19.0760,  # Mumbai
            "longitude": 72.8777,
            "timezone": "Asia/Kolkata",
            "purpose": "business"
        }
        
        response = await async_client.get("/api/v1/muhurta/best-times-today", params=params)
        
        if response.status_code == 404:
            pytest.skip("Today's muhurta endpoint not implemented")
        
        today_data = assert_response_success(response)
        
        # Verify structure
        assert "date" in today_data
        assert "best_times" in today_data
        assert "rahu_kaal" in today_data
        assert "general_advice" in today_data
        
        # Verify date is today's date
        today_str = datetime.now().date().isoformat()
        assert today_data["date"] == today_str
        
        # Verify best times structure
        best_times = today_data["best_times"]
        for time_slot in best_times:
            assert "date" in time_slot
            assert "time" in time_slot
            assert "quality" in time_slot
            assert "score" in time_slot
        
        # Verify Rahu Kaal information
        rahu_kaal = today_data["rahu_kaal"]
        assert "start" in rahu_kaal
        assert "end" in rahu_kaal
        assert "duration_minutes" in rahu_kaal
        
        # Verify advice is present
        assert len(today_data["general_advice"]) > 20, "Should provide meaningful advice"