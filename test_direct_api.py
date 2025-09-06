#!/usr/bin/env python3
"""
Test API directly by creating a user through the registration API
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_registration_and_switching():
    """Test registration and AI provider switching"""
    
    print("🧪 Testing AI Provider Switching via Registration API")
    print("=" * 60)
    
    # Step 1: Register a new user
    print("\n1. Registering new user...")
    register_data = {
        "name": "API Test User",
        "phone": "+234901234999",  # Use different number
        "location": "Abuja, Nigeria",
        "preferred_language": "en"
    }
    
    try:
        reg_response = requests.post(f"{BASE_URL}/api/register", json=register_data)
        print(f"Registration status: {reg_response.status_code}")
        
        if reg_response.status_code == 201:
            auth_data = reg_response.json()
            token = auth_data['access_token']
            user = auth_data['user']
            print("✅ Registration successful")
            print(f"   User: {user['name']}")
            print(f"   ID: {user['id']}")
        elif reg_response.status_code == 409:
            # User exists, try login
            print("User exists, trying login...")
            login_response = requests.post(f"{BASE_URL}/api/login", json={"phone": register_data["phone"]})
            if login_response.status_code == 200:
                auth_data = login_response.json()
                token = auth_data['access_token']
                user = auth_data['user']
                print("✅ Login successful")
            else:
                print(f"❌ Login failed: {login_response.text}")
                return
        else:
            print(f"❌ Registration failed: {reg_response.text}")
            return
            
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # Step 2: Test AI providers endpoint
    print("\n2. Getting AI providers...")
    try:
        providers_response = requests.get(f"{BASE_URL}/api/ai/providers", headers=headers)
        print(f"Providers status: {providers_response.status_code}")
        
        if providers_response.status_code == 200:
            providers_data = providers_response.json()
            print("✅ AI providers retrieved")
            print(f"   Available: {len(providers_data['providers'])}")
            
            for provider in providers_data['providers']:
                status = "✅" if provider['status'] == 'available' else "❌"
                print(f"   {status} {provider['name']} ({provider['id']})")
        else:
            print(f"❌ Providers failed: {providers_response.text}")
            return
            
    except Exception as e:
        print(f"❌ Providers error: {e}")
        return
    
    # Step 3: Test provider switching
    print("\n3. Testing provider switching...")
    available_providers = [p for p in providers_data['providers'] if p['status'] == 'available']
    
    if available_providers:
        test_provider = available_providers[0]
        print(f"   Switching to: {test_provider['name']}")
        
        try:
            switch_response = requests.put(
                f"{BASE_URL}/api/user/ai-provider",
                json={"provider": test_provider['id']},
                headers=headers
            )
            
            print(f"   Switch status: {switch_response.status_code}")
            if switch_response.status_code == 200:
                print("✅ Provider switch successful")
                print(f"   Response: {switch_response.json()}")
            else:
                print(f"❌ Switch failed: {switch_response.text}")
        except Exception as e:
            print(f"❌ Switch error: {e}")
    else:
        print("   ⚠️ No available providers to test")
    
    # Step 4: Test chat
    print("\n4. Testing chat with selected provider...")
    try:
        chat_response = requests.post(
            f"{BASE_URL}/api/chat",
            json={"message": "Hello, how do I grow tomatoes?"},
            headers=headers
        )
        
        print(f"   Chat status: {chat_response.status_code}")
        if chat_response.status_code == 200:
            chat_data = chat_response.json()
            print("✅ Chat successful")
            print(f"   AI Provider: {chat_data.get('ai_provider', 'unknown')}")
            print(f"   Response: {chat_data['response'][:100]}...")
        else:
            print(f"❌ Chat failed: {chat_response.text}")
    except Exception as e:
        print(f"❌ Chat error: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Test Complete!")

if __name__ == "__main__":
    test_registration_and_switching()