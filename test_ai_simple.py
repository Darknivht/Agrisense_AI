#!/usr/bin/env python3
"""
Simple test for AI Provider functionality without authentication
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_basic_functionality():
    """Test basic functionality that doesn't require authentication"""
    
    print("🧪 Testing AgriSense AI Basic Functionality")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code == 200:
            health_data = response.json()
            print("✅ Health check passed")
            print(f"   Database: {health_data['services'].get('database', 'unknown')}")
            print(f"   RAG System: {health_data['services'].get('rag_system', False)}")
            print(f"   Weather Service: {health_data['services'].get('weather_service', False)}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    # Test 2: Check if settings page loads
    print("\n2. Testing settings page...")
    try:
        response = requests.get(f"{BASE_URL}/settings")
        if response.status_code == 200:
            print("✅ Settings page loads successfully")
            if "AI Assistant Provider" in response.text:
                print("✅ AI provider settings found in page")
            else:
                print("⚠️  AI provider settings not found in page")
        else:
            print(f"❌ Settings page failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Settings page error: {e}")
    
    # Test 3: Check AI engine functionality directly
    print("\n3. Testing AI engine import...")
    try:
        # This will test if the AI engine can be imported and initialized
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        from core.ai_engine import AgriSenseAI
        
        ai_engine = AgriSenseAI()
        providers = ai_engine.get_available_providers()
        
        print("✅ AI engine imported successfully")
        print(f"   Available providers: {len(providers)}")
        
        for provider in providers:
            status_icon = "✅" if provider['status'] == 'available' else "❌"
            print(f"   {status_icon} {provider['name']} - {provider['description']}")
            
    except Exception as e:
        print(f"❌ AI engine error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Basic functionality test complete!")

if __name__ == "__main__":
    test_basic_functionality()