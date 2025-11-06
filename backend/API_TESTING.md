# API Testing Guide

This guide helps you test the Personal Finance Assistant Backend API.

## Prerequisites

- Backend server running on http://127.0.0.1:8000
- curl installed (or use Postman/Insomnia)
- Alternatively, use the interactive docs at http://127.0.0.1:8000/docs

## 1. Health Check

Test if the server is running:

```bash
curl http://127.0.0.1:8000/
```

Expected response:
```json
{
  "status": "Backend running",
  "version": "1.0.0",
  "model_loaded": true
}
```

## 2. Budget Analysis

Analyze spending and get AI insights:

```bash
curl -X POST "http://127.0.0.1:8000/ai/budget-summary" \
  -H "Content-Type: application/json" \
  -d '{
    "income": 60000,
    "expenses": {
      "Housing": 15000,
      "Food": 10000,
      "Transportation": 5000,
      "Utilities": 3500,
      "Entertainment": 2500,
      "Shopping": 4000
    },
    "persona": "professional"
  }'
```

Expected response structure:
```json
{
  "summary": {
    "income": 60000,
    "total_expenses": 40000,
    "savings": 20000,
    "savings_rate": 33.33,
    "top_expenses": [
      {"category": "Housing", "amount": 15000},
      {"category": "Food", "amount": 10000},
      {"category": "Transportation", "amount": 5000}
    ]
  },
  "insights": [
    "Your savings rate is healthy at 33.33%...",
    "Consider reducing Housing expenses...",
    "..."
  ]
}
```

## 3. Goal Planning

Create a savings plan:

```bash
curl -X POST "http://127.0.0.1:8000/ai/goal-planner" \
  -H "Content-Type: application/json" \
  -d '{
    "goal_name": "Emergency Fund",
    "target_amount": 120000,
    "months": 12,
    "income": 60000,
    "persona": "professional",
    "current_savings": 20000
  }'
```

Expected response structure:
```json
{
  "plan": {
    "goal_name": "Emergency Fund",
    "target_amount": 120000,
    "current_savings": 20000,
    "remaining_amount": 100000,
    "months": 12,
    "monthly_savings_needed": 8333.33,
    "percentage_of_income": 13.89
  },
  "advice": "Your goal is achievable with discipline..."
}
```

## 4. Tax Advice

Get tax-saving suggestions:

```bash
curl -X POST "http://127.0.0.1:8000/ai/tax-advice" \
  -H "Content-Type: application/json" \
  -d '{
    "income": 800000,
    "persona": "professional"
  }'
```

Expected response structure:
```json
{
  "tax_advice": "For your income range, here are tax-saving strategies...",
  "estimated_tax": null,
  "suggestions": null
}
```

## 5. General AI Chat

Ask financial questions:

```bash
curl -X POST "http://127.0.0.1:8000/ai/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the 50-30-20 budgeting rule?",
    "persona": "general"
  }'
```

Expected response:
```json
{
  "response": "The 50-30-20 rule suggests allocating..."
}
```

## 6. Add Transaction

Add a new transaction:

```bash
curl -X POST "http://127.0.0.1:8000/transactions/add" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Grocery Shopping at Walmart",
    "amount": 3500,
    "category": "Food",
    "type": "expense"
  }'
```

Expected response:
```json
{
  "success": true,
  "message": "Transaction added successfully",
  "transaction_id": "txn_13"
}
```

## 7. Get Recent Transactions

Retrieve recent transactions:

```bash
curl http://127.0.0.1:8000/transactions/recent
```

Expected response:
```json
{
  "transactions": [
    {
      "id": "txn_1",
      "description": "Monthly Salary",
      "amount": 60000,
      "category": "Salary",
      "type": "income",
      "date": "2025-01-01T00:00:00"
    },
    ...
  ]
}
```

## 8. Analytics Summary

Get dashboard analytics:

```bash
curl http://127.0.0.1:8000/analytics/summary
```

Expected response:
```json
{
  "trend_data": [
    {"month": "Jan", "income": 54000, "expenses": 35700},
    {"month": "Feb", "income": 57000, "expenses": 37800},
    {"month": "Mar", "income": 60000, "expenses": 42000}
  ],
  "totals": {
    "income": 68000,
    "expenses": 42000,
    "savings": 26000,
    "savings_rate": 38.24
  }
}
```

## Using Interactive Documentation

The easiest way to test the API is using the built-in Swagger UI:

1. Navigate to http://127.0.0.1:8000/docs
2. Click on any endpoint to expand it
3. Click "Try it out"
4. Enter request data
5. Click "Execute"
6. View the response

## Common Issues

### 1. Connection Refused
- Ensure the backend is running
- Check the port number (default: 8000)

### 2. Model Not Loaded
- First request may take 30-60 seconds while model loads
- Check `logs/app.log` for loading status

### 3. Validation Errors
- Ensure all required fields are present
- Check data types match the schema
- Use the interactive docs to see exact requirements

## Testing with Python

```python
import requests

BASE_URL = "http://127.0.0.1:8000"

# Budget analysis
response = requests.post(
    f"{BASE_URL}/ai/budget-summary",
    json={
        "income": 60000,
        "expenses": {
            "Housing": 15000,
            "Food": 10000,
            "Transportation": 5000
        },
        "persona": "professional"
    }
)

print(response.json())
```

## Performance Notes

- First AI request: 30-60 seconds (model loading)
- Subsequent requests: 1-3 seconds
- Health check: < 100ms
- Transaction operations: < 100ms

## Troubleshooting

Check the logs:
```bash
# View last 50 lines
tail -n 50 logs/app.log

# On Windows
type logs\app.log | more
```

Monitor server console output for real-time debugging.
