"""
Script to populate MongoDB with dummy data for testing
Run this script to add sample transactions, chat history, and goals to the database
"""
import asyncio
from datetime import datetime, timedelta
import random
from motor.motor_asyncio import AsyncIOMotorClient
from config.settings import MONGODB_URL, MONGODB_DB_NAME
from core.logger import logger


# Sample data templates
EXPENSE_CATEGORIES = {
    "Food & Dining": [
        ("Breakfast at Starbucks", 250, 450),
        ("Lunch at office cafeteria", 150, 300),
        ("Dinner at restaurant", 500, 1500),
        ("Grocery shopping", 2000, 5000),
        ("Food delivery - Swiggy", 300, 600),
        ("Coffee with friends", 200, 400),
    ],
    "Transportation": [
        ("Uber to office", 150, 300),
        ("Petrol for car", 2000, 3000),
        ("Metro card recharge", 500, 1000),
        ("Car maintenance", 3000, 8000),
        ("Parking fees", 50, 200),
    ],
    "Shopping": [
        ("Clothes from Amazon", 1500, 5000),
        ("Electronics purchase", 5000, 25000),
        ("Books from bookstore", 500, 2000),
        ("Shoes", 2000, 6000),
        ("Accessories", 500, 2000),
    ],
    "Entertainment": [
        ("Movie tickets", 400, 800),
        ("Netflix subscription", 500, 800),
        ("Concert tickets", 1500, 3000),
        ("Gaming subscription", 500, 1500),
        ("Weekend outing", 1000, 3000),
    ],
    "Utilities": [
        ("Electricity bill", 1500, 3000),
        ("Internet bill", 800, 1500),
        ("Phone bill", 500, 1000),
        ("Water bill", 300, 600),
        ("Gas cylinder", 800, 1200),
    ],
    "Healthcare": [
        ("Doctor consultation", 500, 1500),
        ("Medicines", 300, 1000),
        ("Health insurance premium", 5000, 15000),
        ("Lab tests", 800, 2500),
        ("Gym membership", 1000, 3000),
    ],
    "Education": [
        ("Online course subscription", 1000, 5000),
        ("Books and study material", 500, 2000),
        ("Certification exam fee", 3000, 10000),
        ("Tuition fees", 10000, 50000),
    ],
    "Travel": [
        ("Flight tickets", 5000, 20000),
        ("Hotel booking", 3000, 15000),
        ("Vacation expenses", 10000, 50000),
        ("Weekend trip", 5000, 15000),
    ]
}

INCOME_SOURCES = [
    ("Monthly Salary", 45000, 80000),
    ("Freelance project payment", 10000, 30000),
    ("Stock dividend", 2000, 8000),
    ("Rental income", 8000, 20000),
    ("Interest income", 500, 3000),
    ("Bonus payment", 20000, 100000),
    ("Investment returns", 5000, 25000),
]

CHAT_QUESTIONS = [
    "How can I save more money each month?",
    "What is the best investment strategy for beginners?",
    "How do I create an emergency fund?",
    "What are the tax-saving options under Section 80C?",
    "Should I invest in mutual funds or stocks?",
    "How much should I save for retirement?",
    "What is SIP and how does it work?",
    "How can I reduce my monthly expenses?",
    "What is the 50-30-20 budgeting rule?",
    "How do I improve my credit score?",
    "What are ELSS funds?",
    "Should I pay off debt or invest?",
    "How much life insurance do I need?",
    "What is the difference between PPF and EPF?",
    "How can I invest with a small salary?",
    "What are the best tax-saving investments?",
    "How do I calculate my income tax?",
    "What is asset allocation?",
    "Should I invest in real estate?",
    "How can I track my expenses better?",
]

CHAT_RESPONSES = {
    "How can I save more money each month?": """To save more money each month, consider these strategies:

1. **Follow the 50-30-20 Rule**: Allocate 50% for needs, 30% for wants, and 20% for savings
2. **Automate Savings**: Set up automatic transfers on payday
3. **Track Expenses**: Use apps to monitor where your money goes
4. **Cut Subscriptions**: Cancel unused services and subscriptions
5. **Cook at Home**: Reduce dining out expenses by 50%
6. **Use Cashback**: Leverage credit card rewards and cashback offers

Start small with 10% of your income and gradually increase to 20-30% for better financial security.""",

    "What is the best investment strategy for beginners?": """For beginners, here's a solid investment strategy:

1. **Build Emergency Fund First**: Save 3-6 months of expenses
2. **Start with SIP in Mutual Funds**: ₹1,000-5,000 monthly in index funds
3. **Diversify**: Split investments across equity (60%), debt (30%), and gold (10%)
4. **Long-term Approach**: Invest for at least 5 years
5. **Tax-saving Investments**: ELSS funds under Section 80C

Recommended allocation:
- Index Funds: 40%
- Large Cap Funds: 30%
- Debt Funds: 20%
- PPF/FD: 10%

Remember: Start early, invest regularly, and stay patient!""",

    "How do I create an emergency fund?": """Creating an emergency fund:

**Target Amount**: 3-6 months of monthly expenses
Example: If monthly expenses = ₹30,000, target = ₹90,000-₹1,80,000

**Where to Keep**:
- High-interest savings account (easy access)
- Liquid mutual funds (better returns)
- Fixed deposits with premature withdrawal option

**How to Build**:
1. Calculate monthly expenses
2. Set aside 10-15% of income monthly
3. Keep in separate account (don't touch!)
4. Build gradually over 1-2 years

**When to Use**: Only for genuine emergencies like job loss, medical issues, or urgent repairs."""
}


async def populate_transactions(db, num_transactions: int = 200):
    """Generate and insert dummy transactions"""
    transactions = []
    start_date = datetime.now() - timedelta(days=180)  # Last 6 months

    for i in range(num_transactions):
        # Random date within last 6 months
        days_ago = random.randint(0, 180)
        transaction_date = start_date + timedelta(days=days_ago)

        # 70% expenses, 30% income
        if random.random() < 0.7:
            # Generate expense
            category = random.choice(list(EXPENSE_CATEGORIES.keys()))
            templates = EXPENSE_CATEGORIES[category]
            template = random.choice(templates)
            description = template[0]
            amount = random.uniform(template[1], template[2])
            txn_type = "expense"
        else:
            # Generate income
            template = random.choice(INCOME_SOURCES)
            description = template[0]
            amount = random.uniform(template[1], template[2])
            category = "Income"
            txn_type = "income"

        transaction = {
            "description": description,
            "amount": round(amount, 2),
            "category": category,
            "type": txn_type,
            "date": transaction_date.isoformat(),
            "created_at": transaction_date,
            "updated_at": transaction_date
        }
        transactions.append(transaction)

    # Insert all transactions
    result = await db.transactions.insert_many(transactions)
    logger.info(f"✅ Inserted {len(result.inserted_ids)} transactions")
    return len(result.inserted_ids)


async def populate_chat_history(db, num_chats: int = 50):
    """Generate and insert dummy chat history"""
    chat_messages = []
    personas = ["professional", "conservative", "aggressive"]

    for i in range(num_chats):
        # Random date within last 90 days
        days_ago = random.randint(0, 90)
        chat_date = datetime.now() - timedelta(days=days_ago)

        question = random.choice(CHAT_QUESTIONS)
        response = CHAT_RESPONSES.get(
            question,
            f"This is a sample AI response about {question.lower()[:-1]}. It provides detailed financial advice based on your question."
        )

        chat = {
            "question": question,
            "response": response,
            "persona": random.choice(personas),
            "timestamp": chat_date,
            "metadata": {
                "model": "claude" if random.random() > 0.3 else "granite",
                "response_time_ms": random.randint(500, 2000)
            }
        }
        chat_messages.append(chat)

    # Insert all chat messages
    result = await db.chat_history.insert_many(chat_messages)
    logger.info(f"✅ Inserted {len(result.inserted_ids)} chat messages")
    return len(result.inserted_ids)


async def populate_goals(db, num_goals: int = 10):
    """Generate and insert dummy goals"""
    goal_templates = [
        ("Emergency Fund", 300000, 180000, "Emergency Fund", 12, 10000),
        ("Dream Vacation to Europe", 150000, 45000, "Travel", 10, 10500),
        ("New Laptop", 80000, 64000, "Other", 2, 8000),
        ("Car Down Payment", 200000, 80000, "Car", 15, 8000),
        ("Home Renovation", 500000, 150000, "Home", 24, 14583),
        ("Child Education Fund", 1000000, 300000, "Education", 60, 11667),
        ("Retirement Corpus", 5000000, 800000, "Retirement", 240, 17500),
        ("Wedding Fund", 800000, 200000, "Other", 18, 33333),
        ("Debt Clearance", 250000, 150000, "Other", 12, 8333),
        ("Investment Portfolio", 600000, 250000, "Other", 24, 14583),
    ]

    goals = []
    for i in range(min(num_goals, len(goal_templates))):
        template = goal_templates[i]
        # Random creation date within last 60 days
        days_ago = random.randint(0, 60)
        created_date = datetime.now() - timedelta(days=days_ago)

        # Random deadline in future
        deadline_days = random.randint(180, 720)
        deadline = datetime.now() + timedelta(days=deadline_days)

        goal = {
            "name": template[0],
            "target_amount": template[1],
            "current_amount": template[2],
            "category": template[3],
            "deadline": deadline.isoformat(),
            "monthly_required": template[5],
            "created_at": created_date,
            "updated_at": created_date,
            "status": random.choice(["active", "active", "active", "paused"])  # 75% active
        }
        goals.append(goal)

    # Insert all goals
    if goals:
        result = await db.goals.insert_many(goals)
        logger.info(f"✅ Inserted {len(result.inserted_ids)} goals")
        return len(result.inserted_ids)
    return 0


async def main():
    """Main function to populate all dummy data"""
    logger.info("🚀 Starting dummy data population...")
    logger.info(f"Connecting to MongoDB at {MONGODB_URL}")

    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[MONGODB_DB_NAME]

    try:
        # Test connection
        await client.admin.command('ping')
        logger.info("✅ Connected to MongoDB successfully")

        # Ask for confirmation
        print("\n" + "="*60)
        print("DUMMY DATA POPULATION")
        print("="*60)
        print(f"Database: {MONGODB_DB_NAME}")
        print(f"This will add:")
        print("  - 200 transactions (mix of income and expenses)")
        print("  - 50 chat history messages")
        print("  - 10 financial goals")
        print("="*60)

        proceed = input("\nProceed with data population? (yes/no): ").strip().lower()

        if proceed not in ['yes', 'y']:
            logger.info("❌ Cancelled by user")
            return

        print("\n🔄 Populating data...\n")

        # Populate transactions
        txn_count = await populate_transactions(db, 200)

        # Populate chat history
        chat_count = await populate_chat_history(db, 50)

        # Populate goals
        goal_count = await populate_goals(db, 10)

        # Summary
        print("\n" + "="*60)
        print("✅ DUMMY DATA POPULATION COMPLETE!")
        print("="*60)
        print(f"Transactions added: {txn_count}")
        print(f"Chat messages added: {chat_count}")
        print(f"Goals added: {goal_count}")
        print(f"\nTotal documents: {txn_count + chat_count + goal_count}")
        print("="*60)

        # Show some stats
        total_expense = 0
        total_income = 0
        async for txn in db.transactions.find({"type": "expense"}):
            total_expense += txn["amount"]
        async for txn in db.transactions.find({"type": "income"}):
            total_income += txn["amount"]

        print(f"\n📊 Financial Summary:")
        print(f"Total Income: ₹{total_income:,.2f}")
        print(f"Total Expenses: ₹{total_expense:,.2f}")
        print(f"Net Savings: ₹{total_income - total_expense:,.2f}")
        print(f"Savings Rate: {((total_income - total_expense) / total_income * 100):.1f}%")
        print("="*60)

        logger.info("✅ All dummy data populated successfully!")

    except Exception as e:
        logger.error(f"❌ Error populating data: {str(e)}")
        print(f"\n❌ Error: {str(e)}")
        print("\nMake sure MongoDB is running and accessible!")

    finally:
        client.close()
        logger.info("Closed MongoDB connection")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
