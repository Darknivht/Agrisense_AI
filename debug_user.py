#!/usr/bin/env python3
"""
Debug user creation and login
"""
import requests
import json

BASE_URL = "http://localhost:5000"

# Try registration first
print("Trying registration...")
register_data = {
    "name": "Test Farmer Debug",
    "phone": "+234901234000",
    "location": "Lagos, Nigeria",
    "preferred_language": "en"
}

reg_response = requests.post(f"{BASE_URL}/api/register", json=register_data)
print(f"Registration response: {reg_response.status_code}")
print(f"Registration body: {reg_response.text}")

if reg_response.status_code != 201:
    # Try login
    print("\nTrying login...")
    login_data = {"phone": "+234901234000"}
    login_response = requests.post(f"{BASE_URL}/api/login", json=login_data)
    print(f"Login response: {login_response.status_code}")
    print(f"Login body: {login_response.text}")