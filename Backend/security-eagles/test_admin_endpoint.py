#!/usr/bin/env python3
"""
Quick test for admin endpoint
"""
import requests

BASE_URL = "http://localhost:8000/api"

def test_admin_endpoint():
    # Login
    login_data = {'username': 'eventadmin', 'password': 'admin123'}
    response = requests.post(f'{BASE_URL}/auth/login/', json=login_data)
    
    if response.status_code != 200:
        print(f"Login failed: {response.text}")
        return
    
    token = response.json()['access']
    headers = {'Authorization': f'Bearer {token}'}
    
    print("Testing admin endpoint...")
    
    # Test admin events endpoint
    admin_response = requests.get(f'{BASE_URL}/events/admin/', headers=headers)
    print(f'Admin Events API Status: {admin_response.status_code}')
    
    if admin_response.status_code == 200:
        data = admin_response.json()
        print(f'Admin can see {data["count"]} events')
        for event in data['results']:
            print(f'  - {event["title"]} (Status: {event["status"]})')
    else:
        print(f'Error: {admin_response.text}')
        print(f'Response headers: {admin_response.headers}')
    
    # Test creating an event
    print("\nTesting event creation...")
    new_event_data = {
        "title": "Admin Test Event",
        "description": "Event created via admin API",
        "category": 1,
        "event_type": "webinar",
        "start_time": "2025-09-01T14:00:00Z",
        "end_time": "2025-09-01T16:00:00Z",
        "organizer": "Admin Test",
        "status": "draft"
    }
    
    create_response = requests.post(f'{BASE_URL}/events/admin/', json=new_event_data, headers=headers)
    print(f"Create Status: {create_response.status_code}")
    if create_response.status_code == 201:
        created_event = create_response.json()
        print(f"Created event: {created_event['title']}")
    else:
        print(f"Create Error: {create_response.text}")

if __name__ == "__main__":
    test_admin_endpoint()
