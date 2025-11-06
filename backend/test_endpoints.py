"""
Test script to verify all MongoDB endpoints
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:8000"

def test_transaction_add():
    """Test adding a transaction"""
    print("\n=== Testing POST /transactions/add ===")

    data = {
        "description": "Test Transaction from API",
        "amount": 1250.50,
        "category": "Food & Dining",
        "type": "expense"
    }

    response = requests.post(f"{BASE_URL}/transactions/add", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200 and response.json().get("success")


def test_transactions_recent():
    """Test getting recent transactions"""
    print("\n=== Testing GET /transactions/recent ===")

    response = requests.get(f"{BASE_URL}/transactions/recent")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Found {len(data.get('transactions', []))} transactions")
    if data.get('transactions'):
        print(f"First transaction: {data['transactions'][0].get('description', 'N/A')}")
    return response.status_code == 200


def test_goal_add():
    """Test adding a goal"""
    print("\n=== Testing POST /goals/add ===")

    deadline = (datetime.now() + timedelta(days=365)).isoformat()

    data = {
        "name": "Test Goal - New Car",
        "target_amount": 500000.0,
        "current_amount": 50000.0,
        "category": "Car",
        "deadline": deadline,
        "monthly_required": 37500.0
    }

    response = requests.post(f"{BASE_URL}/goals/add", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    if response.status_code == 200 and response.json().get("success"):
        return response.json().get("goal_id")
    return None


def test_goals_list():
    """Test getting all goals"""
    print("\n=== Testing GET /goals/list ===")

    response = requests.get(f"{BASE_URL}/goals/list?status=active")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Found {data.get('total', 0)} active goals")
    if data.get('goals'):
        print(f"First goal: {data['goals'][0].get('name', 'N/A')}")
    return response.status_code == 200


def test_goal_update(goal_id):
    """Test updating a goal"""
    print(f"\n=== Testing PUT /goals/update/{goal_id} ===")

    data = {
        "current_amount": 75000.0,
        "status": "active"
    }

    response = requests.put(f"{BASE_URL}/goals/update/{goal_id}", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200 and response.json().get("success")


def test_chat_generate():
    """Test AI chat endpoint (saves to MongoDB)"""
    print("\n=== Testing POST /ai/generate ===")

    data = {
        "question": "What is a mutual fund?",
        "persona": "professional"
    }

    response = requests.post(f"{BASE_URL}/ai/generate", json=data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        resp_data = response.json()
        print(f"Response length: {len(resp_data.get('response', ''))} characters")
        print(f"Response preview: {resp_data.get('response', '')[:100]}...")
    return response.status_code == 200


def main():
    """Run all tests"""
    print("=" * 60)
    print("MongoDB Endpoint Testing")
    print("=" * 60)

    results = {}

    # Test transactions
    results["Transaction Add"] = test_transaction_add()
    results["Transactions Recent"] = test_transactions_recent()

    # Test goals
    goal_id = test_goal_add()
    results["Goal Add"] = goal_id is not None
    results["Goals List"] = test_goals_list()

    if goal_id:
        results["Goal Update"] = test_goal_update(goal_id)
    else:
        print("\n⚠️ Skipping goal update test (no goal_id)")
        results["Goal Update"] = False

    # Test chat (saves to MongoDB)
    results["AI Chat"] = test_chat_generate()

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")

    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)

    print("\n" + "=" * 60)
    print(f"Results: {passed_tests}/{total_tests} tests passed")
    print("=" * 60)

    return passed_tests == total_tests


if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error running tests: {str(e)}")
        exit(1)
