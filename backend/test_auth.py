#!/usr/bin/env python3
"""
Quick test script to verify authentication is working
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test basic health endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health Check: {response.status_code} - {response.json()}")
    return response.status_code == 200

def test_auth_without_token():
    """Test auth endpoint without token (should fail)"""
    response = requests.get(f"{BASE_URL}/auth/me")
    print(f"Auth without token: {response.status_code} - {response.json()}")
    return response.status_code in [401, 403]  # Either is acceptable

def test_auth_with_test_token():
    """Test auth endpoint with test token (should work)"""
    headers = {
        "Authorization": "Bearer test_token"
    }
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print(f"Auth with test token: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")
        return True
    else:
        print(f"Error: {response.json()}")
        return False

def test_auth_with_wrong_token():
    """Test auth endpoint with wrong token (should fail)"""
    headers = {
        "Authorization": "Bearer wrong_token"
    }
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print(f"Auth with wrong token: {response.status_code} - {response.json()}")
    return response.status_code == 401

if __name__ == "__main__":
    print("🧪 Testing Authentication Setup...")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health),
        ("Auth without token", test_auth_without_token),
        ("Auth with test token", test_auth_with_test_token),
        ("Auth with wrong token", test_auth_with_wrong_token),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}:")
        try:
            result = test_func()
            results.append((test_name, result))
            print(f"✅ PASS" if result else "❌ FAIL")
        except Exception as e:
            print(f"❌ ERROR: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"\n🎯 Summary: {passed}/{total} tests passed")