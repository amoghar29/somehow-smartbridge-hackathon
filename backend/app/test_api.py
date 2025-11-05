"""
Quick API Test Script
Run this after starting the backend to verify everything works
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000/api/v1"

def print_response(response, title):
    """Pretty print response"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")
    print(f"Status: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)


def test_health():
    """Test health endpoint"""
    response = requests.get("http://localhost:8000/health")
    print_response(response, "HEALTH CHECK")
    return response.status_code == 200


def test_registration():
    """Test user registration"""
    data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "Test@123",
        "full_name": "Test User",
        "phone_number": "+919876543210"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=data)
    print_response(response, "USER REGISTRATION")
    return response.status_code in [200, 201, 400]  # 400 if already exists


def test_login():
    """Test user login"""
    data = {
        "username": "test@example.com",
        "password": "Test@123"
    }
    
    response = requests.post(
        f"{BASE_URL}/auth/token",
        data=data
    )
    print_response(response, "USER LOGIN")
    
    if response.status_code == 200:
        return response.json().get("access_token")
    return None


def test_create_transaction(token):
    """Test transaction creation"""
    headers = {"Authorization": f"Bearer {token}"}
    
    data = {
        "type": "expense",
        "category": "food",
        "amount": 1500,
        "description": "Restaurant dinner",
        "date": datetime.utcnow().isoformat(),
        "payment_method": "card",
        "tags": ["dining", "weekend"]
    }
    
    response = requests.post(
        f"{BASE_URL}/transactions/",
        json=data,
        headers=headers
    )
    print_response(response, "CREATE TRANSACTION")
    return response.status_code in [200, 201]


def test_get_transactions(token):
    """Test getting transactions"""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/transactions/?limit=10",
        headers=headers
    )
    print_response(response, "GET TRANSACTIONS")
    return response.status_code == 200


def test_analytics(token):
    """Test analytics endpoint"""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/transactions/analytics/summary?period=monthly",
        headers=headers
    )
    print_response(response, "GET ANALYTICS")
    return response.status_code == 200


def test_goal_planning(token):
    """Test goal planning"""
    headers = {"Authorization": f"Bearer {token}"}
    
    data = {
        "name": "Emergency Fund",
        "target_amount": 100000,
        "current_amount": 10000,
        "target_date": (datetime.utcnow() + timedelta(days=365)).isoformat(),
        "category": "emergency"
    }
    
    response = requests.post(
        f"{BASE_URL}/goals/plan",
        json=data,
        headers=headers
    )
    print_response(response, "GOAL PLANNING")
    return response.status_code == 200


def test_create_goal(token):
    """Test goal creation"""
    headers = {"Authorization": f"Bearer {token}"}
    
    data = {
        "name": "Vacation Fund",
        "target_amount": 50000,
        "current_amount": 5000,
        "target_date": (datetime.utcnow() + timedelta(days=180)).isoformat(),
        "category": "travel",
        "saving_strategy": "moderate",
        "monthly_contribution": 7500
    }
    
    response = requests.post(
        f"{BASE_URL}/goals/",
        json=data,
        headers=headers
    )
    print_response(response, "CREATE GOAL")
    return response.status_code in [200, 201]


def test_chat(token):
    """Test chat endpoint"""
    headers = {"Authorization": f"Bearer {token}"}
    
    data = {
        "content": "How can I save money on my monthly expenses?",
        "context": "general"
    }
    
    response = requests.post(
        f"{BASE_URL}/chat/message",
        json=data,
        headers=headers
    )
    print_response(response, "CHAT MESSAGE")
    return response.status_code == 200


def run_all_tests():
    """Run all API tests"""
    print("\n" + "="*60)
    print("  PERSONAL FINANCE BOT - API TESTS")
    print("="*60)
    
    results = {}
    
    # Test health
    results['health'] = test_health()
    
    # Test registration
    results['registration'] = test_registration()
    
    # Test login and get token
    token = test_login()
    if not token:
        print("\n❌ Login failed! Cannot continue with authenticated tests.")
        return
    
    results['login'] = True
    
    # Test authenticated endpoints
    results['create_transaction'] = test_create_transaction(token)
    results['get_transactions'] = test_get_transactions(token)
    results['analytics'] = test_analytics(token)
    results['goal_planning'] = test_goal_planning(token)
    results['create_goal'] = test_create_goal(token)
    results['chat'] = test_chat(token)
    
    # Print summary
    print("\n" + "="*60)
    print("  TEST SUMMARY")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:20s} : {status}")
    
    total = len(results)
    passed = sum(results.values())
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")


if __name__ == "__main__":
    run_all_tests()