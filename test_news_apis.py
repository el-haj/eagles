#!/usr/bin/env python3
"""
Test script for News APIs
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_login():
    """Test login endpoint"""
    print("🔐 Testing Login...")
    login_data = {
        'username': 'testuser',
        'password': 'testpass123'
    }
    
    response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        return response.json()['access']
    else:
        print("❌ Login failed!")
        return None

def test_news_endpoints(token):
    """Test news endpoints with authentication"""
    headers = {'Authorization': f'Bearer {token}'}

    print("\n📰 Testing News List...")
    response = requests.get(f"{BASE_URL}/api/news/", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}...")

    # Get first article slug for detailed testing
    first_article_slug = None
    if response.status_code == 200:
        data = response.json()
        if data['results']:
            first_article_slug = data['results'][0]['slug']

    print("\n🏷️ Testing Categories...")
    response = requests.get(f"{BASE_URL}/api/news/categories/", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")

    print("\n⭐ Testing Featured News...")
    response = requests.get(f"{BASE_URL}/api/news/featured/", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}...")

    print("\n🚨 Testing Breaking News...")
    response = requests.get(f"{BASE_URL}/api/news/breaking/", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}...")

    print("\n🕐 Testing Latest News...")
    response = requests.get(f"{BASE_URL}/api/news/latest/", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}...")

    # Test single article if we have one
    if first_article_slug:
        print(f"\n📖 Testing Single Article ({first_article_slug})...")
        response = requests.get(f"{BASE_URL}/api/news/{first_article_slug}/", headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:300]}...")

        print(f"\n💬 Testing Comments for {first_article_slug}...")
        response = requests.get(f"{BASE_URL}/api/news/{first_article_slug}/comments/", headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}...")

    print("\n🔍 Testing Search...")
    response = requests.get(f"{BASE_URL}/api/news/search/?q=test", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}...")

def test_without_auth():
    """Test endpoints without authentication"""
    print("\n🚫 Testing without authentication...")
    response = requests.get(f"{BASE_URL}/api/news/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")

if __name__ == "__main__":
    print("🧪 Starting News API Tests")
    print("=" * 50)
    
    # Test without auth first
    test_without_auth()
    
    # Test login
    token = test_login()
    
    if token:
        print(f"\n✅ Login successful! Token: {token[:20]}...")
        test_news_endpoints(token)
    else:
        print("\n❌ Cannot proceed without valid token")
        sys.exit(1)
    
    print("\n✅ Tests completed!")
