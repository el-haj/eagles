#!/usr/bin/env python3

import requests
import json

def test_admin_endpoint():
    # Login and get token
    login_data = {'username': 'eventadmin', 'password': 'admin123'}
    response = requests.post('http://localhost:8000/api/auth/login/', json=login_data)
    
    if response.status_code == 200:
        token = response.json()['access']
        headers = {'Authorization': f'Bearer {token}'}
        
        print("=== Testing Admin Events Endpoint ===")
        
        # Test admin events endpoint
        admin_response = requests.get('http://localhost:8000/api/events/admin/', headers=headers)
        print(f'Admin events API: {admin_response.status_code}')
        
        if admin_response.status_code == 200:
            data = admin_response.json()
            print(f'SUCCESS: Admin can see {data["count"]} events')
            for event in data['results']:
                print(f'  - {event["title"]} (Status: {event["status"]})')
        else:
            print(f'ERROR: {admin_response.text}')
            
        # Also test regular endpoint for comparison
        print("\n=== Testing Regular Events Endpoint ===")
        regular_response = requests.get('http://localhost:8000/api/events/', headers=headers)
        print(f'Regular events API: {regular_response.status_code}')
        
        if regular_response.status_code == 200:
            data = regular_response.json()
            print(f'Regular endpoint shows {data["count"]} events')
        else:
            print(f'Regular endpoint error: {regular_response.text}')
            
    else:
        print(f'Login failed: {response.text}')

if __name__ == '__main__':
    test_admin_endpoint()
