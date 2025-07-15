#!/usr/bin/env python3
"""
Simple test runner to validate core Josi functionality without complex dependencies.
"""
import sys
import os
sys.path.append('src')

from datetime import datetime
import asyncio

def test_imports():
    """Test that core modules can be imported."""
    print("Testing imports...")
    
    try:
        from josi.models.person_model import Person
        print("✓ Person model imported")
    except Exception as e:
        print(f"✗ Person model import failed: {e}")
        return False
    
    try:
        from josi.models.chart_model import AstrologyChart
        print("✓ Chart model imported")
    except Exception as e:
        print(f"✗ Chart model import failed: {e}")
        return False
    
    try:
        from josi.models.user_model import User, SubscriptionTier
        print("✓ User model imported")
    except Exception as e:
        print(f"✗ User model import failed: {e}")
        return False
    
    try:
        from josi.models.astrologer_model import Astrologer
        print("✓ Astrologer model imported")
    except Exception as e:
        print(f"✗ Astrologer model import failed: {e}")
        return False
    
    try:
        from josi.models.remedy_model import Remedy, RecommendationRequest
        print("✓ Remedy model imported")
    except Exception as e:
        print(f"✗ Remedy model import failed: {e}")
        return False
    
    return True

def test_services():
    """Test that core services can be imported and instantiated."""
    print("\nTesting services...")
    
    try:
        from josi.services.astrology_service import AstrologyCalculator
        calc = AstrologyCalculator()
        print("✓ Astrology calculator created")
    except Exception as e:
        print(f"✗ Astrology calculator failed: {e}")
        return False
    
    try:
        from josi.services.vedic.muhurta_service import MuhurtaCalculator
        muhurta = MuhurtaCalculator()
        print("✓ Muhurta calculator created")
    except Exception as e:
        print(f"✗ Muhurta calculator failed: {e}")
        return False
    
    try:
        from josi.services.auth_service import AuthService
        auth = AuthService(db=None)  # Pass None for testing
        print("✓ Auth service created")
    except Exception as e:
        print(f"✗ Auth service failed: {e}")
        return False
    
    return True

async def test_chart_calculation():
    """Test basic chart calculation functionality."""
    print("\nTesting chart calculation...")
    
    try:
        from josi.services.astrology_service import AstrologyCalculator
        
        calc = AstrologyCalculator()
        
        # Test with Barack Obama's data
        birth_time = datetime(1961, 8, 4, 19, 24, 0)  # 7:24 PM HST
        latitude = 21.3099  # Honolulu
        longitude = -157.8581
        
        # Calculate Western chart
        western_chart = calc.calculate_western_chart(
            dt=birth_time,
            latitude=latitude,
            longitude=longitude
        )
        
        print("✓ Western chart calculated")
        print(f"  - Found {len(western_chart.get('planets', {}))} planets")
        print(f"  - Found {len(western_chart.get('houses', []))} houses")
        
        # Test Vedic chart
        calc.set_ayanamsa('lahiri')
        vedic_chart = calc.calculate_vedic_chart(
            dt=birth_time,
            latitude=latitude,
            longitude=longitude
        )
        
        print("✓ Vedic chart calculated")
        print(f"  - Found {len(vedic_chart.get('planets', {}))} planets")
        print(f"  - Found {len(vedic_chart.get('houses', []))} houses")
        
        # Verify key planets exist
        required_planets = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn']
        missing_planets = [p for p in required_planets if p not in western_chart.get('planets', {})]
        
        if missing_planets:
            print(f"✗ Missing planets: {missing_planets}")
            return False
        
        print("✓ All major planets calculated")
        return True
        
    except Exception as e:
        print(f"✗ Chart calculation failed: {e}")
        return False

def test_muhurta_calculation():
    """Test Muhurta calculation functionality."""
    print("\nTesting Muhurta calculation...")
    
    try:
        from josi.services.vedic.muhurta_service import MuhurtaCalculator
        
        muhurta_calc = MuhurtaCalculator()
        
        # Test for marriage in Delhi
        start_date = datetime(2024, 11, 1)
        end_date = datetime(2024, 11, 7)
        
        muhurtas = muhurta_calc.find_muhurta(
            purpose="marriage",
            start_date=start_date,
            end_date=end_date,
            latitude=28.7041,  # Delhi
            longitude=77.1025,
            timezone="Asia/Kolkata",
            max_results=5
        )
        
        print(f"✓ Found {len(muhurtas)} marriage muhurtas")
        
        if muhurtas:
            first_muhurta = muhurtas[0]
            required_fields = ['date', 'time', 'quality', 'score', 'tithi', 'nakshatra']
            missing_fields = [f for f in required_fields if f not in first_muhurta]
            
            if missing_fields:
                print(f"✗ Missing muhurta fields: {missing_fields}")
                return False
            
            print(f"  - Best muhurta: {first_muhurta['date']} {first_muhurta['time']}")
            print(f"  - Quality: {first_muhurta['quality']} (Score: {first_muhurta['score']})")
        
        # Test Rahu Kaal calculation
        rahu_kaal = muhurta_calc.calculate_rahu_kaal(
            date=datetime(2024, 10, 15),  # Tuesday
            latitude=28.7041,
            longitude=77.1025,
            timezone="Asia/Kolkata"
        )
        
        print("✓ Rahu Kaal calculated")
        print(f"  - Tuesday Rahu Kaal: {rahu_kaal['rahu_kaal']['start']} - {rahu_kaal['rahu_kaal']['end']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Muhurta calculation failed: {e}")
        return False

def test_remedy_system():
    """Test remedy recommendation system components."""
    print("\nTesting remedy system...")
    
    try:
        from josi.models.remedy_model import Remedy, RemedyType, Tradition, DoshaType
        
        # Test creating a remedy instance
        remedy = Remedy(
            name="Test Mantra",
            type=RemedyType.MANTRA,
            tradition=Tradition.VEDIC,
            planet="Jupiter",
            description={"en": "Test mantra for Jupiter"},
            instructions={"en": "Chant 108 times daily"},
            difficulty_level=2,
            cost_level=1
        )
        
        print("✓ Remedy model created")
        print(f"  - Name: {remedy.name}")
        print(f"  - Type: {remedy.type}")
        print(f"  - Planet: {remedy.planet}")
        
        # Test localized content
        desc = remedy.get_localized_content("description", "en")
        print(f"  - Description: {desc}")
        
        return True
        
    except Exception as e:
        print(f"✗ Remedy system test failed: {e}")
        return False

def test_user_auth_models():
    """Test user authentication models."""
    print("\nTesting user authentication models...")
    
    try:
        from josi.models.user_model import User, SubscriptionTier
        from josi.services.auth_service import AuthService
        
        # Test user model
        user = User(
            email="test@example.com",
            full_name="Test User",
            subscription_tier=SubscriptionTier.FREE
        )
        
        print("✓ User model created")
        print(f"  - Email: {user.email}")
        print(f"  - Subscription: {user.subscription_tier}")
        print(f"  - Tier limits: {user.get_tier_limits()}")
        
        # Test auth service
        auth_service = AuthService(db=None)
        
        # Test password hashing
        password = "test_password_123"
        hashed = auth_service.get_password_hash(password)
        print("✓ Password hashing works")
        
        # Test password verification
        is_valid = auth_service.verify_password(password, hashed)
        assert is_valid, "Password verification failed"
        print("✓ Password verification works")
        
        return True
        
    except Exception as e:
        print(f"✗ User auth test failed: {e}")
        return False

async def main():
    """Run all core functionality tests."""
    print("=== Josi Core Functionality Tests ===\n")
    
    tests = [
        ("Imports", test_imports),
        ("Services", test_services),
        ("Chart Calculation", test_chart_calculation),
        ("Muhurta Calculation", test_muhurta_calculation),
        ("Remedy System", test_remedy_system),
        ("User Authentication", test_user_auth_models)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running {test_name} Tests")
        print('='*50)
        
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            if result:
                passed += 1
                print(f"\n✓ {test_name} tests PASSED")
            else:
                print(f"\n✗ {test_name} tests FAILED")
        except Exception as e:
            print(f"\n✗ {test_name} tests FAILED with exception: {e}")
    
    print(f"\n{'='*50}")
    print(f"TEST SUMMARY")
    print('='*50)
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Core functionality is working.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review the output above.")
    
    return passed == total

if __name__ == "__main__":
    asyncio.run(main())