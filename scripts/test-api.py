#!/usr/bin/env python3
"""
Bridge Platform API Testing Script
Tests all API endpoints with sample data
"""

import requests
import json
import time
import sys
from typing import Dict, Any

API_BASE_URL = "http://localhost:8000"
API_V1_URL = f"{API_BASE_URL}/api/v1"

class BridgeAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.results = []
        
    def test_endpoint(self, method: str, endpoint: str, data: Dict = None, expected_status: int = 200) -> Dict[str, Any]:
        """Test a single API endpoint"""
        url = f"{API_V1_URL}{endpoint}"
        start_time = time.time()
        
        try:
            if method == "GET":
                response = self.session.get(url)
            elif method == "POST":
                response = self.session.post(url, json=data)
            elif method == "PUT":
                response = self.session.put(url, json=data)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response_time = time.time() - start_time
            
            result = {
                "endpoint": endpoint,
                "method": method,
                "status_code": response.status_code,
                "response_time": response_time,
                "success": response.status_code == expected_status,
                "data_length": len(response.content) if response.content else 0
            }
            
            if not result["success"]:
                result["error"] = response.text[:200]
            
            self.results.append(result)
            return result
            
        except Exception as e:
            result = {
                "endpoint": endpoint,
                "method": method,
                "success": False,
                "error": str(e),
                "response_time": time.time() - start_time
            }
            self.results.append(result)
            return result
    
    def test_health_endpoints(self):
        """Test basic health and info endpoints"""
        print("🏥 Testing health endpoints...")
        
        # Root endpoint
        result = self.test_endpoint("GET", "", expected_status=404)  # This will hit the v1 prefix
        
        # Test actual root
        try:
            response = self.session.get(API_BASE_URL)
            print(f"   Root endpoint: {response.status_code} - {response.json().get('message', 'OK')}")
        except Exception as e:
            print(f"   Root endpoint error: {e}")
        
        # Health check
        try:
            response = self.session.get(f"{API_BASE_URL}/health")
            if response.status_code == 200:
                health_data = response.json()
                print(f"   Health check: ✅ {health_data.get('status', 'unknown')}")
            else:
                print(f"   Health check: ❌ Status {response.status_code}")
        except Exception as e:
            print(f"   Health check error: {e}")
    
    def test_players_endpoints(self):
        """Test player-related endpoints"""
        print("👥 Testing player endpoints...")
        
        # Get all players
        result = self.test_endpoint("GET", "/players")
        if result["success"]:
            print(f"   GET /players: ✅ ({result['response_time']:.3f}s)")
        else:
            print(f"   GET /players: ❌ {result.get('error', 'Unknown error')}")
        
        # Get players with filtering
        self.test_endpoint("GET", "/players?status=active&limit=5")
        
        # Test specific player (assuming player ID 1 exists)
        result = self.test_endpoint("GET", "/players/1")
        if result["success"]:
            print(f"   GET /players/1: ✅")
        else:
            print(f"   GET /players/1: ❌ {result.get('error', 'Unknown error')}")
        
        # Test player masterpoints
        result = self.test_endpoint("GET", "/players/1/masterpoints")
        if result["success"]:
            print(f"   GET /players/1/masterpoints: ✅")
        
        # Test player ratings
        result = self.test_endpoint("GET", "/players/1/ratings")
        if result["success"]:
            print(f"   GET /players/1/ratings: ✅")
    
    def test_events_endpoints(self):
        """Test event-related endpoints"""
        print("🏆 Testing event endpoints...")
        
        # Get all events
        result = self.test_endpoint("GET", "/events")
        if result["success"]:
            print(f"   GET /events: ✅ ({result['response_time']:.3f}s)")
        
        # Get recent events
        result = self.test_endpoint("GET", "/events/recent")
        if result["success"]:
            print(f"   GET /events/recent: ✅")
        
        # Test specific event (assuming event ID 1 exists)
        result = self.test_endpoint("GET", "/events/1")
        if result["success"]:
            print(f"   GET /events/1: ✅")
        
        # Test event results
        result = self.test_endpoint("GET", "/events/1/results")
        if result["success"]:
            print(f"   GET /events/1/results: ✅")
    
    def test_results_endpoints(self):
        """Test result-related endpoints"""
        print("📊 Testing result endpoints...")
        
        # Test event results
        result = self.test_endpoint("GET", "/results/event/1")
        if result["success"]:
            print(f"   GET /results/event/1: ✅")
        
        # Test player results
        result = self.test_endpoint("GET", "/results/player/1")
        if result["success"]:
            print(f"   GET /results/player/1: ✅")
        
        # Test leaderboard
        result = self.test_endpoint("GET", "/results/leaderboard")
        if result["success"]:
            print(f"   GET /results/leaderboard: ✅")
        
        # Test leaderboard with different periods
        for period in ["week", "month", "year"]:
            result = self.test_endpoint("GET", f"/results/leaderboard?period={period}")
            if result["success"]:
                print(f"   GET /results/leaderboard?period={period}: ✅")
    
    def test_organizations_endpoints(self):
        """Test organization-related endpoints"""
        print("🏢 Testing organization endpoints...")
        
        # Get all organizations
        result = self.test_endpoint("GET", "/organizations")
        if result["success"]:
            print(f"   GET /organizations: ✅")
        
        # Test specific organization
        result = self.test_endpoint("GET", "/organizations/1")
        if result["success"]:
            print(f"   GET /organizations/1: ✅")
    
    def test_create_operations(self):
        """Test creation endpoints (optional, requires valid data)"""
        print("➕ Testing create operations...")
        
        # Test creating a new player (will likely fail due to duplicate number)
        new_player = {
            "number": 9999,
            "firstname": "Test",
            "lastname": "Player",
            "email": "test.player@example.com",
            "organization_id": 1
        }
        
        result = self.test_endpoint("POST", "/players", data=new_player, expected_status=200)
        if result["success"]:
            print(f"   POST /players: ✅ Created test player")
        else:
            print(f"   POST /players: ⚠️  {result.get('error', 'Expected - likely duplicate')}")
    
    def run_all_tests(self):
        """Run all API tests"""
        print("🧪 Starting Bridge Platform API Tests...")
        print(f"📡 Testing API at: {API_BASE_URL}")
        
        # Check if API is running
        try:
            response = self.session.get(f"{API_BASE_URL}/health", timeout=5)
            if response.status_code != 200:
                print("❌ API is not responding correctly. Make sure it's running.")
                return False
        except Exception as e:
            print(f"❌ Cannot connect to API: {e}")
            print("   Make sure the API is running: cd apps/api && uvicorn app.main:app --reload")
            return False
        
        print("✅ API is responding\n")
        
        # Run all test suites
        self.test_health_endpoints()
        self.test_players_endpoints()
        self.test_events_endpoints()
        self.test_results_endpoints()
        self.test_organizations_endpoints()
        self.test_create_operations()
        
        # Print summary
        print(f"\n📋 Test Summary:")
        total_tests = len(self.results)
        successful_tests = len([r for r in self.results if r["success"]])
        failed_tests = total_tests - successful_tests
        
        print(f"   Total tests: {total_tests}")
        print(f"   Successful: {successful_tests} ✅")
        print(f"   Failed: {failed_tests} ❌")
        
        if failed_tests > 0:
            print(f"\n❌ Failed tests:")
            for result in self.results:
                if not result["success"]:
                    print(f"   {result['method']} {result['endpoint']}: {result.get('error', 'Unknown error')}")
        
        # Performance summary
        avg_response_time = sum(r.get("response_time", 0) for r in self.results) / len(self.results)
        print(f"\n⚡ Performance:")
        print(f"   Average response time: {avg_response_time:.3f}s")
        
        slow_endpoints = [r for r in self.results if r.get("response_time", 0) > 1.0]
        if slow_endpoints:
            print(f"   Slow endpoints (>1s): {len(slow_endpoints)}")
            for endpoint in slow_endpoints:
                print(f"     {endpoint['method']} {endpoint['endpoint']}: {endpoint['response_time']:.3f}s")
        
        return failed_tests == 0

if __name__ == "__main__":
    tester = BridgeAPITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)