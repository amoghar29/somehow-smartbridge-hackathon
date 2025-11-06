import random
from datetime import datetime, timedelta
from core.database import db
from core.auth import get_password_hash

# Dummy users
users = [
    {"email": f"user{i}@test.com", "password": get_password_hash(f"password{i}"), "name": f"User{i}"}
    for i in range(1, 6)
]

user_ids = []
for user in users:
    result = db.users.insert_one(user)
    user_ids.append(result.inserted_id)

# Dummy transactions
categories = ["Food", "Transport", "Shopping", "Bills", "Entertainment", "Salary", "Other"]
types = ["income", "expense"]

for user_id in user_ids:
    for _ in range(20):
        txn_type = random.choice(types)
        amount = random.randint(100, 5000) if txn_type == "expense" else random.randint(5000, 20000)
        txn = {
            "user_id": str(user_id),
            "description": f"{'Salary' if txn_type == 'income' else 'Purchase'} {_}",
            "amount": amount,
            "category": random.choice(categories),
            "type": txn_type,
            "date": datetime.utcnow() - timedelta(days=random.randint(0, 180))
        }
        db.transactions.insert_one(txn)

# Dummy conversations
questions = [
    "How can I save more money?",
    "What is a good budget for groceries?",
    "How do I plan for retirement?",
    "Tips for reducing tax liability?",
    "Should I invest in stocks or mutual funds?"
]
responses = [
    "You can save more by tracking expenses and setting goals.",
    "A good grocery budget is 10-15% of your income.",
    "Start retirement planning early and invest regularly.",
    "Use available deductions and invest in tax-saving instruments.",
    "Diversify your investments for balanced growth."
]

for user_id in user_ids:
    for i in range(10):
        convo = {
            "user_id": str(user_id),
            "question": random.choice(questions),
            "response": random.choice(responses),
            "timestamp": datetime.utcnow() - timedelta(days=random.randint(0, 180))
        }
        db.conversations.insert_one(convo)

print("Dummy data loaded successfully.")
