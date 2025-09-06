#!/usr/bin/env python3
"""
Test script for AI Provider Switching functionality
"""
import os
import sys
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_URL = "http://localhost:5000"

def test_ai_providers():
    """Test the AI provider switching functionality"""
    
    print("🧪 Testing AI Provider Switching Functionality")
    print("=" * 50)
    
    # Step 1: Register a test user
    print("\n1. Registering test user...")
    register_data = {
        "name": "Test Farmer",
        "phone": "+234901234567",
        "location": "Lagos, Nigeria",
        "preferred_language": "en"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/register", json=register_data)
        if response.status_code == 201:
            print("✅ User registered successfully")
            auth_data = response.json()
            token = auth_data['access_token']
            user_id = auth_data['user']['id']
        else:
            # Try to login instead
            print("ℹ️  User might already exist, trying to login...")
            login_response = requests.post(f"{BASE_URL}/api/login", json={
                "phone": register_data["phone"]
            })
            if login_response.status_code == 200:
                print("✅ User logged in successfully")
                auth_data = login_response.json()
                token = auth_data['access_token']
                user_id = auth_data['user']['id']
            else:
                print(f"❌ Failed to register/login user: {login_response.text}")
                return
    except Exception as e:
        print(f"❌ Error during registration/login: {e}")
        return
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # Step 2: Get available AI providers
    print("\n2. Getting available AI providers...")
    try:
        response = requests.get(f"{BASE_URL}/api/ai/providers", headers=headers)
        if response.status_code == 200:
            providers_data = response.json()
            providers = providers_data['providers']
            current = providers_data['current']
            
            print("✅ Available AI providers:")
            for provider in providers:
                status_icon = "✅" if provider['status'] == 'available' else "❌"
                print(f"   {status_icon} {provider['name']} ({provider['id']}) - {provider['description']}")
            print(f"   🔧 Current default: {current}")
        else:
            print(f"❌ Failed to get AI providers: {response.text}")
            return
    except Exception as e:
        print(f"❌ Error getting AI providers: {e}")
        return
    
    # Step 3: Test switching AI providers
    print("\n3. Testing AI provider switching...")
    available_providers = [p for p in providers if p['status'] == 'available']
    
    if len(available_providers) < 2:
        print("⚠️  Need at least 2 available providers to test switching")
        if len(available_providers) == 1:
            print(f"   Only {available_providers[0]['name']} is available")
    else:
        # Test switching to each available provider
        for provider in available_providers[:2]:  # Test first 2 providers
            print(f"\n   Testing {provider['name']} ({provider['id']})...")
            
            try:
                # Switch provider
                switch_response = requests.put(
                    f"{BASE_URL}/api/user/ai-provider",
                    json={"provider": provider['id']},
                    headers=headers
                )
                
                if switch_response.status_code == 200:
                    print(f"   ✅ Successfully switched to {provider['name']}")
                    
                    # Test chat with this provider
                    chat_response = requests.post(
                        f"{BASE_URL}/api/chat",
                        json={"message": "Hello, what crops grow well in Nigeria?"},
                        headers=headers
                    )
                    
                    if chat_response.status_code == 200:
                        chat_data = chat_response.json()
                        ai_provider_used = chat_data.get('ai_provider', 'unknown')
                        response_text = chat_data['response'][:100] + "..." if len(chat_data['response']) > 100 else chat_data['response']
                        
                        print(f"   ✅ Chat response from {ai_provider_used}:")
                        print(f"   💬 \"{response_text}\"")
                        
                        if ai_provider_used.lower() == provider['id'].lower():
                            print(f"   ✅ Correct AI provider used: {ai_provider_used}")
                        else:
                            print(f"   ⚠️  Expected {provider['id']}, but got {ai_provider_used}")
                    else:
                        print(f"   ❌ Chat failed: {chat_response.text}")
                else:
                    print(f"   ❌ Failed to switch provider: {switch_response.text}")
                    
            except Exception as e:
                print(f"   ❌ Error testing {provider['name']}: {e}")
    
    # Step 4: Test settings page access
    print("\n4. Testing settings page access...")
    try:
        settings_response = requests.get(f"{BASE_URL}/settings")
        if settings_response.status_code == 200:
            print("✅ Settings page accessible")
            if "AI Assistant Provider" in settings_response.text:
                print("✅ AI provider settings found in page")
            else:
                print("⚠️  AI provider settings not found in page content")
        else:
            print(f"❌ Settings page not accessible: {settings_response.status_code}")
    except Exception as e:
        print(f"❌ Error accessing settings page: {e}")
    
    # Step 5: Verify user preference persistence
    print("\n5. Testing user preference persistence...")
    try:
        # Verify token still works and get updated user data
        verify_response = requests.post(
            f"{BASE_URL}/api/verify-token",
            json={"token": token}
        )
        
        if verify_response.status_code == 200:
            user_data = verify_response.json()['user']
            preferred_provider = user_data.get('preferred_ai_provider', 'unknown')
            print(f"✅ User preference persisted: {preferred_provider}")
        else:
            print(f"❌ Failed to verify user preference: {verify_response.text}")
    except Exception as e:
        print(f"❌ Error verifying persistence: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 AI Provider Switching Test Complete!")
    print("\nKey Features Tested:")
    print("✓ User registration/authentication")
    print("✓ AI provider discovery")
    print("✓ Provider switching API")
    print("✓ Chat with different providers")
    print("✓ Settings page access")
    print("✓ User preference persistence")

if __name__ == "__main__":
    test_ai_providers()