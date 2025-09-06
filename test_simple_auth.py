#!/usr/bin/env python3
"""
Simple test for API authentication
"""
import requests

BASE_URL = "http://localhost:5000"

# Load the test token
try:
    with open('test_token.txt', 'r') as f:
        token = f.read().strip()
    print(f"🔑 Token: {token[:50]}...")
except:
    print("❌ Could not load test token")
    exit(1)

headers = {'Authorization': f'Bearer {token}'}

# Test the providers endpoint directly
print("\n🧪 Testing AI providers endpoint...")
try:
    response = requests.get(f"{BASE_URL}/api/ai/providers", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")

# Test a simple protected endpoint (user stats)
print("\n🧪 Testing user stats endpoint...")
try:
    response = requests.get(f"{BASE_URL}/api/user/stats", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")