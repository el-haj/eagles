#!/usr/bin/env python
"""
Test script for Events API endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

def get_jwt_token():
    """Get JWT token for authentication"""
    login_data = {
        'username': 'eventadmin',
        'password': 'admin123'
    }
    
    response = requests.post(f'{BASE_URL}/auth/login/', json=login_data)
    if response.status_code == 200:
        return response.json()['access']
    else:
        print(f"Login failed: {response.status_code} - {response.text}")
        return None

def test_events_endpoints():
    """Test various events endpoints"""
    token = get_jwt_token()
    if not token:
        return
    
    headers = {'Authorization': f'Bearer {token}'}
    
    print("=" * 60)
    print("TESTING EVENTS API ENDPOINTS")
    print("=" * 60)
    
    # Test 1: List all events
    print("\n1. Testing GET /api/events/ (List Events)")
    response = requests.get(f'{BASE_URL}/events/', headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total events: {data['count']}")
        print(f"Events in response: {len(data['results'])}")
        for event in data['results']:
            print(f"  - {event['title']} ({event['event_type']})")
            print(f"    Status: Upcoming={event['is_upcoming']}, Ongoing={event['is_ongoing']}, Passed={event['is_passed']}")
    else:
        print(f"Error: {response.text}")
    
    # Test 2: Get categories
    print("\n2. Testing GET /api/events/categories/ (Event Categories)")
    response = requests.get(f'{BASE_URL}/events/categories/', headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        categories = response.json()
        print(f"Categories found: {len(categories)}")
        for cat in categories:
            print(f"  - {cat['name']} ({cat['slug']}) - Color: {cat['color']}")
    else:
        print(f"Error: {response.text}")
    
    # Test 3: Get featured events
    print("\n3. Testing GET /api/events/featured/ (Featured Events)")
    response = requests.get(f'{BASE_URL}/events/featured/', headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        featured = response.json()
        print(f"Featured events: {len(featured)}")
        for event in featured:
            print(f"  - {event['title']} (Featured: {event['is_featured']})")
    else:
        print(f"Error: {response.text}")
    
    # Test 4: Get upcoming events
    print("\n4. Testing GET /api/events/upcoming/ (Upcoming Events)")
    response = requests.get(f'{BASE_URL}/events/upcoming/', headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Upcoming events: {data['count']}")
        for event in data['results']:
            print(f"  - {event['title']} (Start: {event['start_time']})")
    else:
        print(f"Error: {response.text}")
    
    # Test 5: Get ongoing events
    print("\n5. Testing GET /api/events/ongoing/ (Ongoing Events)")
    response = requests.get(f'{BASE_URL}/events/ongoing/', headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        ongoing = response.json()
        print(f"Ongoing events: {len(ongoing)}")
        for event in ongoing:
            print(f"  - {event['title']} (Ongoing: {event['is_ongoing']})")
    else:
        print(f"Error: {response.text}")
    
    # Test 6: Get past events
    print("\n6. Testing GET /api/events/past/ (Past Events)")
    response = requests.get(f'{BASE_URL}/events/past/', headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Past events: {data['count']}")
        for event in data['results']:
            print(f"  - {event['title']} (Passed: {event['is_passed']})")
    else:
        print(f"Error: {response.text}")
    
    # Test 7: Get event details (using first event slug)
    print("\n7. Testing GET /api/events/{slug}/ (Event Details)")
    # Get first event slug
    response = requests.get(f'{BASE_URL}/events/', headers=headers)
    if response.status_code == 200:
        first_event = response.json()['results'][0]
        slug = first_event['slug']
        
        detail_response = requests.get(f'{BASE_URL}/events/{slug}/', headers=headers)
        print(f"Status: {detail_response.status_code}")
        if detail_response.status_code == 200:
            event_detail = detail_response.json()
            print(f"Event: {event_detail['title']}")
            print(f"Description: {event_detail['description'][:100]}...")
            print(f"Organizer: {event_detail['organizer']}")
            print(f"Platforms: {event_detail['platforms']}")
            print(f"Tags: {event_detail['tags']}")
            print(f"Views: {event_detail['views']}")
        else:
            print(f"Error: {detail_response.text}")
    
    # Test 8: Test filtering
    print("\n8. Testing Filtering (GET /api/events/?event_type=workshop)")
    response = requests.get(f'{BASE_URL}/events/?event_type=workshop', headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Workshop events: {data['count']}")
        for event in data['results']:
            print(f"  - {event['title']} (Type: {event['event_type']})")
    else:
        print(f"Error: {response.text}")
    
    # Test 9: Test search
    print("\n9. Testing Search (GET /api/events/?search=django)")
    response = requests.get(f'{BASE_URL}/events/?search=django', headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Django search results: {data['count']}")
        for event in data['results']:
            print(f"  - {event['title']}")
    else:
        print(f"Error: {response.text}")
    
    # Test 10: Admin endpoints
    print("\n10. Testing GET /api/events/admin/ (Admin Events List)")
    response = requests.get(f'{BASE_URL}/events/admin/', headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Admin events view: {data['count']} events")
        for event in data['results']:
            print(f"  - {event['title']} (Status: {event['status']})")
    else:
        print(f"Error: {response.text}")

    # Test 11: Create a new event via API
    print("\n11. Testing POST /api/events/admin/ (Create Event)")
    new_event_data = {
        "title": "API Test Event",
        "description": "Event created via API for testing",
        "long_description": "This is a test event created through the API to verify the create functionality works correctly.",
        "category": 1,  # Technology category
        "event_type": "webinar",
        "start_time": "2025-09-01T14:00:00Z",
        "end_time": "2025-09-01T16:00:00Z",
        "location": "Online",
        "organizer": "API Test Team",
        "tags": ["api", "test", "webinar"],
        "status": "draft"
    }

    create_response = requests.post(f'{BASE_URL}/events/admin/', json=new_event_data, headers=headers)
    print(f"Create Status: {create_response.status_code}")
    if create_response.status_code == 201:
        created_event = create_response.json()
        print(f"Created event: {created_event['title']} (Slug: {created_event['slug']})")
    else:
        print(f"Create Error: {create_response.text}")
    
    print("\n" + "=" * 60)
    print("EVENTS API TESTING COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    test_events_endpoints()
