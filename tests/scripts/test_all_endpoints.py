#!/usr/bin/env python3
"""
Comprehensive API endpoint testing script.
Tests all endpoints systematically and reports coverage.
"""

import sys
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import time

BASE_URL = "http://localhost:8000"
API_KEY = "test-api-key-12345"
HEADERS = {"X-API-Key": API_KEY}

# Test person ID (Obama)
PERSON_ID = "f2303d9c-0bc9-4b18-b17e-9cf4b7bd5f9f"

class EndpointTester:
    def __init__(self):
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
    def test_endpoint(self, method: str, url: str, description: str, 
                     expected_status: int = 200, data: Dict = None, 
                     params: Dict = None) -> bool:
        """Test a single endpoint."""
        self.total_tests += 1
        
        try:
            full_url = f"{BASE_URL}{url}"
            
            if method.upper() == "GET":
                response = requests.get(full_url, headers=HEADERS, params=params, timeout=30)
            elif method.upper() == "POST":
                response = requests.post(full_url, headers=HEADERS, json=data, params=params, timeout=30)
            elif method.upper() == "PUT":
                response = requests.put(full_url, headers=HEADERS, json=data, params=params, timeout=30)
            elif method.upper() == "DELETE":
                response = requests.delete(full_url, headers=HEADERS, params=params, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            success = response.status_code == expected_status
            
            if success:
                self.passed_tests += 1
                status = "✅ PASS"
                try:
                    # Try to parse JSON response
                    json_data = response.json()
                    details = f"Response keys: {list(json_data.keys()) if isinstance(json_data, dict) else 'Non-dict response'}"
                except:
                    details = f"Non-JSON response, length: {len(response.text)}"
            else:
                self.failed_tests += 1
                status = "❌ FAIL"
                details = f"Expected {expected_status}, got {response.status_code}: {response.text[:200]}"
            
            self.results.append({
                "method": method.upper(),
                "url": url,
                "description": description,
                "status": status,
                "details": details,
                "response_code": response.status_code
            })
            
            print(f"{status} {method.upper()} {url} - {description}")
            if not success:
                print(f"      {details}")
            
            return success
            
        except requests.exceptions.Timeout:
            self.failed_tests += 1
            status = "❌ TIMEOUT"
            details = "Request timed out after 30 seconds"
            self.results.append({
                "method": method.upper(),
                "url": url,
                "description": description,
                "status": status,
                "details": details,
                "response_code": "TIMEOUT"
            })
            print(f"{status} {method.upper()} {url} - {description}")
            print(f"      {details}")
            return False
            
        except Exception as e:
            self.failed_tests += 1
            status = "❌ ERROR"
            details = str(e)
            self.results.append({
                "method": method.upper(),
                "url": url,
                "description": description,
                "status": status,
                "details": details,
                "response_code": "ERROR"
            })
            print(f"{status} {method.upper()} {url} - {description}")
            print(f"      {details}")
            return False

    def run_all_tests(self):
        """Run comprehensive tests for all endpoints."""
        print("🚀 Starting comprehensive API endpoint testing...")
        print(f"📍 Base URL: {BASE_URL}")
        print(f"🔑 Using API Key: {API_KEY}")
        print(f"👤 Test Person ID: {PERSON_ID}")
        print("=" * 80)
        
        # 1. CHART CONTROLLER ENDPOINTS
        print("\\n📊 TESTING CHART CONTROLLER ENDPOINTS")
        print("-" * 50)
        
        # Test chart calculation
        self.test_endpoint("POST", f"/api/v1/charts/calculate", 
                          "Calculate Western chart",
                          params={"person_id": PERSON_ID, "systems": "western", "house_system": "placidus"})
        
        self.test_endpoint("POST", f"/api/v1/charts/calculate", 
                          "Calculate Vedic chart",
                          params={"person_id": PERSON_ID, "systems": "vedic", "house_system": "whole_sign"})
        
        self.test_endpoint("POST", f"/api/v1/charts/calculate", 
                          "Calculate multiple systems",
                          params={"person_id": PERSON_ID, "systems": "western,vedic", "house_system": "placidus"})
        
        # Test chart retrieval
        self.test_endpoint("GET", f"/api/v1/charts/person/{PERSON_ID}", 
                          "Get person's charts")
        
        # 2. PERSON CONTROLLER ENDPOINTS  
        print("\\n👤 TESTING PERSON CONTROLLER ENDPOINTS")
        print("-" * 50)
        
        # Test person operations
        self.test_endpoint("GET", f"/api/v1/persons/{PERSON_ID}", 
                          "Get person by ID")
        
        self.test_endpoint("GET", "/api/v1/persons", 
                          "List all persons")
        
        # Create test person
        test_person_data = {
            "name": "Test Person", 
            "email": "test@example.com",
            "date_of_birth": "1990-01-01",
            "time_of_birth": "1990-01-01T12:00:00",  # Full datetime format
            "place_of_birth": "New York, NY, USA",
            "timezone": "America/New_York"
        }
        
        self.test_endpoint("POST", "/api/v1/persons", 
                          "Create new person",
                          data=test_person_data, expected_status=201)
        
        # 3. PANCHANG CONTROLLER ENDPOINTS
        print("\\n🌙 TESTING PANCHANG CONTROLLER ENDPOINTS")  
        print("-" * 50)
        
        self.test_endpoint("GET", "/api/v1/panchang",
                          "Get panchang for date",
                          params={
                              "date": "1961-08-04T19:24:00",
                              "latitude": 21.304547,
                              "longitude": -157.8581, 
                              "timezone": "Pacific/Honolulu"
                          })
        
        self.test_endpoint("GET", "/api/v1/panchang/today",
                          "Get today's panchang",
                          params={
                              "latitude": 21.304547,
                              "longitude": -157.8581,
                              "timezone": "Pacific/Honolulu"
                          })
        
        # 4. DASHA CONTROLLER ENDPOINTS
        print("\\n⏰ TESTING DASHA CONTROLLER ENDPOINTS")
        print("-" * 50)
        
        self.test_endpoint("GET", f"/api/v1/dasha/{PERSON_ID}",
                          "Get person's dasha periods")
        
        self.test_endpoint("GET", f"/api/v1/dasha/{PERSON_ID}/current",
                          "Get current dasha")
        
        # 5. TRANSIT CONTROLLER ENDPOINTS
        print("\\n🌍 TESTING TRANSIT CONTROLLER ENDPOINTS")
        print("-" * 50)
        
        self.test_endpoint("GET", f"/api/v1/transits/{PERSON_ID}",
                          "Get current transits")
        
        self.test_endpoint("GET", f"/api/v1/transits/{PERSON_ID}/upcoming",
                          "Get upcoming transits",
                          params={"days": 30})
        
        # 6. COMPATIBILITY CONTROLLER ENDPOINTS
        print("\\n💕 TESTING COMPATIBILITY CONTROLLER ENDPOINTS")
        print("-" * 50)
        
        # We need a second person for compatibility
        self.test_endpoint("GET", f"/api/v1/compatibility/{PERSON_ID}/{PERSON_ID}",
                          "Get compatibility (same person)",
                          expected_status=400)  # Should fail - can't compare person to themselves
        
        # 7. PREDICTION CONTROLLER ENDPOINTS
        print("\\n🔮 TESTING PREDICTION CONTROLLER ENDPOINTS")
        print("-" * 50)
        
        self.test_endpoint("GET", f"/api/v1/predictions/{PERSON_ID}",
                          "Get predictions for person")
        
        self.test_endpoint("GET", f"/api/v1/predictions/{PERSON_ID}/yearly",
                          "Get yearly predictions",
                          params={"year": 2025})
        
        # 8. REMEDIES CONTROLLER ENDPOINTS
        print("\\n💎 TESTING REMEDIES CONTROLLER ENDPOINTS")
        print("-" * 50)
        
        self.test_endpoint("GET", f"/api/v1/remedies/{PERSON_ID}",
                          "Get remedies for person")
        
        self.test_endpoint("GET", f"/api/v1/remedies/{PERSON_ID}/gemstones",
                          "Get gemstone recommendations")
        
        self.test_endpoint("GET", f"/api/v1/remedies/{PERSON_ID}/mantras",
                          "Get mantra recommendations")
        
        # 9. LOCATION CONTROLLER ENDPOINTS
        print("\\n📍 TESTING LOCATION CONTROLLER ENDPOINTS")
        print("-" * 50)
        
        self.test_endpoint("GET", "/api/v1/location/search",
                          "Search locations",
                          params={"query": "New York"})
        
        self.test_endpoint("GET", "/api/v1/location/geocode",
                          "Geocode location",
                          params={"address": "New York, NY, USA"})
        
        self.test_endpoint("GET", "/api/v1/location/timezone",
                          "Get timezone for coordinates",
                          params={"latitude": 40.7128, "longitude": -74.0060})
        
        # 10. ADDITIONAL CHART ENDPOINTS
        print("\\n📈 TESTING ADDITIONAL CHART ENDPOINTS")
        print("-" * 50)
        
        # Test divisional charts
        self.test_endpoint("GET", f"/api/v1/charts/divisional/{PERSON_ID}",
                          "Get divisional charts",
                          params={"division": "D9"})
        
        # Test progressions (need to check if this endpoint exists)
        self.test_endpoint("GET", f"/api/v1/charts/progressions/{PERSON_ID}",
                          "Get chart progressions")
        
        # Test solar return (need to check if this endpoint exists)
        self.test_endpoint("GET", f"/api/v1/charts/solar-return/{PERSON_ID}",
                          "Get solar return chart",
                          params={"year": 2025})
        
        # Additional endpoints discovered from implementation
        print("\\n🔍 TESTING ADDITIONAL DISCOVERED ENDPOINTS")
        print("-" * 50)
        
        # Test health endpoints if they exist
        self.test_endpoint("GET", "/health", "Health check", expected_status=200)
        self.test_endpoint("GET", "/", "Root endpoint", expected_status=200)
        
        # Print final results
        self.print_summary()
    
    def print_summary(self):
        """Print test summary and coverage report."""
        print("\\n" + "=" * 80)
        print("📊 TEST EXECUTION SUMMARY")
        print("=" * 80)
        
        print(f"📈 Total Tests: {self.total_tests}")
        print(f"✅ Passed: {self.passed_tests}")
        print(f"❌ Failed: {self.failed_tests}")
        
        if self.total_tests > 0:
            success_rate = (self.passed_tests / self.total_tests) * 100
            print(f"📊 Success Rate: {success_rate:.1f}%")
        
        print("\\n📋 DETAILED RESULTS:")
        print("-" * 80)
        
        for result in self.results:
            print(f"{result['status']} {result['method']} {result['url']}")
            print(f"      {result['description']}")
            if not result['status'].startswith('✅'):
                print(f"      {result['details']}")
        
        print("\\n🎯 ENDPOINT COVERAGE ANALYSIS:")
        print("-" * 80)
        
        # Group by controller
        controllers = {}
        for result in self.results:
            path_parts = result['url'].split('/')
            if len(path_parts) >= 4:
                controller = path_parts[3]  # /api/v1/CONTROLLER/...
                if controller not in controllers:
                    controllers[controller] = []
                controllers[controller].append(result)
        
        for controller, tests in controllers.items():
            passed = len([t for t in tests if t['status'].startswith('✅')])
            total = len(tests)
            print(f"📁 {controller.upper()}: {passed}/{total} tests passed")
        
        if self.failed_tests > 0:
            print(f"\\n⚠️  {self.failed_tests} endpoints need attention!")
        else:
            print(f"\\n🎉 All {self.total_tests} endpoints working perfectly!")

if __name__ == "__main__":
    tester = EndpointTester()
    tester.run_all_tests()