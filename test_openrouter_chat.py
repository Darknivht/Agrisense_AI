#!/usr/bin/env python3
"""
Test chat functionality with OpenRouter
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_openrouter_chat():
    """Test chat with OpenRouter provider"""
    
    print("🧪 Testing OpenRouter Chat Functionality")
    print("=" * 50)
    
    # Register/login user
    register_data = {
        "name": "OpenRouter Test User",
        "phone": "+234901234777",
        "location": "Lagos, Nigeria",
        "preferred_language": "en"
    }
    
    try:
        # Try registration
        reg_response = requests.post(f"{BASE_URL}/api/register", json=register_data)
        if reg_response.status_code == 201:
            auth_data = reg_response.json()
            token = auth_data['access_token']
            print("✅ User registered")
        elif reg_response.status_code == 409:
            # Login existing user
            login_response = requests.post(f"{BASE_URL}/api/login", json={"phone": register_data["phone"]})
            auth_data = login_response.json()
            token = auth_data['access_token']
            print("✅ User logged in")
        else:
            print(f"❌ Auth failed: {reg_response.text}")
            return
            
        headers = {'Authorization': f'Bearer {token}'}
        
        # Switch to OpenRouter
        print("\n1. Switching to OpenRouter...")
        switch_response = requests.put(
            f"{BASE_URL}/api/user/ai-provider",
            json={"provider": "openrouter"},
            headers=headers
        )
        
        if switch_response.status_code == 200:
            print("✅ Switched to OpenRouter")
        else:
            print(f"❌ Switch failed: {switch_response.text}")
            return
        
        # Test simple chat
        print("\n2. Testing simple chat...")
        chat_response = requests.post(
            f"{BASE_URL}/api/chat",
            json={"message": "What is farming?"},
            headers=headers,
            timeout=30  # 30 second timeout
        )
        
        if chat_response.status_code == 200:
            chat_data = chat_response.json()
            print("✅ Chat successful")
            print(f"   AI Provider: {chat_data.get('ai_provider', 'unknown')}")
            print(f"   Response length: {len(chat_data['response'])} characters")
            print(f"   First 200 chars: {chat_data['response'][:200]}...")
        else:
            print(f"❌ Chat failed: {chat_response.status_code} - {chat_response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_openrouter_chat()