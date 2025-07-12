#!/usr/bin/env python3
"""
Test script for Learning Management System API endpoints
"""

import requests
import json
import sys

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/learnings"

def test_tracks_endpoints():
    """Test track endpoints (no auth required)"""
    print("🧪 Testing Track Endpoints (No Auth Required)")
    
    # Test track list
    print("\n1. Testing GET /tracks/")
    response = requests.get(f"{API_BASE}/tracks/")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Found {data.get('count', 0)} tracks")
        if data.get('results'):
            print(f"First track: {data['results'][0].get('title', 'N/A')}")
    else:
        print(f"Error: {response.text}")
    
    # Test track categories
    print("\n2. Testing GET /tracks/category/cyber/")
    response = requests.get(f"{API_BASE}/tracks/category/cyber/")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Found {data.get('count', 0)} cyber tracks")
    
    # Test track search
    print("\n3. Testing track search")
    response = requests.get(f"{API_BASE}/tracks/?search=security")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Search results: {data.get('count', 0)} tracks")

def test_learning_paths_endpoints():
    """Test learning path endpoints (auth required)"""
    print("\n🧪 Testing Learning Path Endpoints (Auth Required)")
    
    # Test without authentication
    print("\n1. Testing GET /learning-paths/ (without auth)")
    response = requests.get(f"{API_BASE}/learning-paths/")
    print(f"Status: {response.status_code}")
    if response.status_code == 401:
        print("✅ Correctly requires authentication")
    else:
        print("❌ Should require authentication")

def test_api_structure():
    """Test API structure and endpoints availability"""
    print("\n🧪 Testing API Structure")
    
    endpoints_to_test = [
        "/tracks/",
        "/learning-paths/",
        "/my-progress/",
    ]
    
    for endpoint in endpoints_to_test:
        print(f"\nTesting {endpoint}")
        response = requests.get(f"{API_BASE}{endpoint}")
        print(f"Status: {response.status_code}")
        
        if response.status_code in [200, 401]:  # 401 is expected for auth-required endpoints
            print("✅ Endpoint accessible")
        else:
            print(f"❌ Unexpected status: {response.text}")

def main():
    """Run all tests"""
    print("🚀 Starting Learning Management System API Tests")
    print(f"Base URL: {API_BASE}")
    
    try:
        # Test if server is running
        response = requests.get(BASE_URL, timeout=5)
        print("✅ Server is running")
    except requests.exceptions.RequestException as e:
        print(f"❌ Server not accessible: {e}")
        print("Please make sure Django server is running on http://localhost:8000")
        sys.exit(1)
    
    # Run tests
    test_tracks_endpoints()
    test_learning_paths_endpoints()
    test_api_structure()
    
    print("\n🎉 API tests completed!")
    print("\n📋 Summary:")
    print("- Track endpoints should work without authentication")
    print("- Learning path endpoints should require authentication")
    print("- Use JWT tokens for authenticated requests")
    print("- Check the API_ENDPOINTS.md file for complete documentation")

if __name__ == "__main__":
    main()
