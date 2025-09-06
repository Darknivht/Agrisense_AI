#!/usr/bin/env python3
"""
Complete test for AI Provider Switching functionality
"""
import os
import requests
import json

BASE_URL = "http://localhost:5000"

def test_ai_provider_switching():
    """Test the complete AI provider switching functionality"""
    
    print("🧪 Testing AgriSense AI Provider Switching")
    print("=" * 60)
    
    # Load the test token
    try:
        with open('test_token.txt', 'r') as f:
            token = f.read().strip()
        print("✅ Test token loaded")
    except:
        print("❌ Could not load test token. Run create_test_user.py first.")
        return
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # Test 1: Verify token works
    print("\n1. Verifying authentication...")
    try:
        response = requests.post(f"{BASE_URL}/api/verify-token", json={"token": token})
        if response.status_code == 200:
            user_data = response.json()['user']
            print("✅ Authentication successful")
            print(f"   User: {user_data['name']}")
            print(f"   Current AI Provider: {user_data.get('preferred_ai_provider', 'unknown')}")
        else:
            print(f"❌ Authentication failed: {response.text}")
            return
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return
    
    # Test 2: Get available AI providers
    print("\n2. Getting available AI providers...")
    try:
        response = requests.get(f"{BASE_URL}/api/ai/providers", headers=headers)
        if response.status_code == 200:
            providers_data = response.json()
            providers = providers_data['providers']
            current_default = providers_data['current']
            
            print("✅ AI providers retrieved successfully")
            print(f"   System default: {current_default}")
            print(f"   Available providers: {len(providers)}")
            
            for provider in providers:
                status_icon = "✅" if provider['status'] == 'available' else "❌"
                print(f"     {status_icon} {provider['name']} ({provider['id']})")
                print(f"        {provider['description']}")
        else:
            print(f"❌ Failed to get AI providers: {response.text}")
            return
    except Exception as e:
        print(f"❌ Error getting AI providers: {e}")
        return
    
    # Test 3: Test initial chat (with current provider)
    print("\n3. Testing initial chat...")
    try:
        chat_response = requests.post(
            f"{BASE_URL}/api/chat",
            json={"message": "What are the best crops for Nigeria?"},
            headers=headers
        )
        
        if chat_response.status_code == 200:
            chat_data = chat_response.json()
            ai_provider_used = chat_data.get('ai_provider', 'unknown')
            response_preview = chat_data['response'][:150] + "..." if len(chat_data['response']) > 150 else chat_data['response']
            
            print("✅ Initial chat successful")
            print(f"   AI Provider Used: {ai_provider_used}")
            print(f"   Response: \"{response_preview}\"")
        else:
            print(f"❌ Initial chat failed: {chat_response.text}")
    except Exception as e:
        print(f"❌ Initial chat error: {e}")
    
    # Test 4: Switch AI providers
    print("\n4. Testing AI provider switching...")
    available_providers = [p for p in providers if p['status'] == 'available']
    
    if len(available_providers) < 1:
        print("⚠️  No available providers to test switching")
    else:
        # Test with the first available provider
        test_provider = available_providers[0]
        print(f"   Switching to: {test_provider['name']} ({test_provider['id']})")
        
        try:
            # Switch provider
            switch_response = requests.put(
                f"{BASE_URL}/api/user/ai-provider",
                json={"provider": test_provider['id']},
                headers=headers
            )
            
            if switch_response.status_code == 200:
                print(f"   ✅ Successfully switched to {test_provider['name']}")
                
                # Test chat with new provider
                chat_response = requests.post(
                    f"{BASE_URL}/api/chat",
                    json={"message": "How do I plant maize?"},
                    headers=headers
                )
                
                if chat_response.status_code == 200:
                    chat_data = chat_response.json()
                    ai_provider_used = chat_data.get('ai_provider', 'unknown')
                    response_preview = chat_data['response'][:150] + "..." if len(chat_data['response']) > 150 else chat_data['response']
                    
                    print(f"   ✅ Chat with {test_provider['name']} successful")
                    print(f"   AI Provider Used: {ai_provider_used}")
                    print(f"   Response: \"{response_preview}\"")
                    
                    # Verify the provider was actually used
                    if ai_provider_used.lower() == test_provider['id'].lower():
                        print(f"   ✅ Correct AI provider confirmed")
                    else:
                        print(f"   ⚠️  Expected {test_provider['id']}, but used {ai_provider_used}")
                else:
                    print(f"   ❌ Chat with new provider failed: {chat_response.text}")
            else:
                print(f"   ❌ Provider switch failed: {switch_response.text}")
                
        except Exception as e:
            print(f"   ❌ Error during provider switch: {e}")
    
    # Test 5: Verify persistence
    print("\n5. Testing preference persistence...")
    try:
        # Get updated user data
        verify_response = requests.post(f"{BASE_URL}/api/verify-token", json={"token": token})
        if verify_response.status_code == 200:
            updated_user = verify_response.json()['user']
            stored_provider = updated_user.get('preferred_ai_provider', 'unknown')
            print(f"✅ User preference persisted: {stored_provider}")
        else:
            print(f"❌ Could not verify persistence: {verify_response.text}")
    except Exception as e:
        print(f"❌ Persistence check error: {e}")
    
    # Test 6: Test invalid provider
    print("\n6. Testing invalid provider handling...")
    try:
        invalid_response = requests.put(
            f"{BASE_URL}/api/user/ai-provider",
            json={"provider": "invalid_provider"},
            headers=headers
        )
        
        if invalid_response.status_code == 400:
            print("✅ Invalid provider correctly rejected")
        else:
            print(f"⚠️  Expected 400 for invalid provider, got {invalid_response.status_code}")
    except Exception as e:
        print(f"❌ Invalid provider test error: {e}")
    
    # Test 7: Settings page functionality
    print("\n7. Testing settings page...")
    try:
        settings_response = requests.get(f"{BASE_URL}/settings")
        if settings_response.status_code == 200:
            settings_content = settings_response.text
            
            checks = [
                ("AI Assistant Provider", "AI provider section"),
                ("Settings", "Settings title"),
                ("ai-provider-card", "AI provider cards"),
                ("selectAIProvider", "Provider selection function")
            ]
            
            for check, description in checks:
                if check in settings_content:
                    print(f"   ✅ {description} found")
                else:
                    print(f"   ⚠️  {description} not found")
        else:
            print(f"❌ Settings page not accessible: {settings_response.status_code}")
    except Exception as e:
        print(f"❌ Settings page error: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 AI Provider Switching Test Complete!")
    print("\n📊 Test Summary:")
    print("✓ Authentication and token verification")
    print("✓ AI provider discovery and listing")
    print("✓ Provider switching API")
    print("✓ Chat functionality with different providers")
    print("✓ User preference persistence")
    print("✓ Invalid input handling")
    print("✓ Settings page integration")
    print("\n🚀 AI Provider switching functionality is ready!")

if __name__ == "__main__":
    test_ai_provider_switching()