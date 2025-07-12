#!/usr/bin/env python3
"""
Create a test user for API testing
"""
import os
import sys
import django

# Setup Django
sys.path.append('Backend/security-eagles')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from core.models import User

def create_test_user():
    """Create a test user for API testing"""
    username = 'testuser'
    password = 'testpass123'
    email = 'test@example.com'
    
    # Check if user already exists
    if User.objects.filter(username=username).exists():
        print(f"User '{username}' already exists!")
        user = User.objects.get(username=username)
    else:
        # Create new user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name='Test',
            last_name='User'
        )
        print(f"Created user '{username}' with password '{password}'")
    
    # Make sure user is active
    user.is_active = True
    user.save()
    
    print(f"User details:")
    print(f"- Username: {user.username}")
    print(f"- Email: {user.email}")
    print(f"- Is active: {user.is_active}")
    print(f"- Is staff: {user.is_staff}")
    
    return user

if __name__ == "__main__":
    create_test_user()
