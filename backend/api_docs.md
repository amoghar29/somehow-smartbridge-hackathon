# API Reference Documentation

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication

All authenticated endpoints require a Bearer token in the Authorization header:
```
Authorization: Bearer <access_token>
```

## Endpoints

### Authentication

#### POST /auth/register
Register a new user.

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "SecurePass123!",
  "full_name": "John Doe",
  "phone": "+919876543210",
  "profile": {
    "age": 30,
    "occupation": "Software Engineer",
    "annual_income": 1200000,
    "risk_profile": "moderate",
    "financial_goals": ["retirement", "home", "education"]
  }
}
```

**Response:** `200 OK`
```json
{
  "message": "User registered successfully",
  "user_id": "507f1f77bcf86cd799439011"
}
```

#### POST /auth/token
Login and get access token.

**Request Body (Form Data):**
```
username: user@example.com
password: SecurePass123!
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

### User Management

#### GET /users/profile
Get current user profile.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "id": "507f1f77bcf86cd799439011",
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "profile": {
    "age": 30,
    "occupation": "Software Engineer",
    "annual_income": 1200000,
    "risk_profile": "moderate",
    "financial_goals": ["retirement", "home", "education"]
  },
  "financial_summary": {
    "total_income": 1200000,
    "total_expenses": 900000,
    "total_savings": 300000,
    "total_investments": 540000,
    "net_worth": 840000
  }
}
```

#### PUT /users/profile
Update user profile.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "profile": {
    "annual_income": 1500000,
    "risk_profile": "aggressive"
  }
}
```

### Transactions

#### POST /transactions
Create a new transaction.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "type": "expense",
  "category": "food",
  "amount": 1500,
  "description": "Restaurant dinner",
  "date": "2024-11-15T19:30:00Z",
  "payment_method": "card",
  "tags": ["dining", "weekend"],
  "recurring": false
}
```

**Response:** `201 Created`
```json
{
  "id": "507f1f77bcf86cd799439012",
  "message": "Transaction created",
  "ai_insights": {
    "category_average": 2000,
    "spending_trend": "increasing",
    "suggestion": "Consider reducing dining expenses"
  }
}
```

#### GET /transactions
Get user transactions with filters.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `limit` (int): Number of transactions (default: 10)
- `offset` (int): Pagination offset (default: 0)
- `start_date` (datetime): Filter start date
- `end_date` (datetime): Filter end date
- `category` (string): Filter by category
- `type` (string): Filter by type (income/expense)

**Response:** `200 OK`
```json
{
  "transactions": [
    {
      "id": "507f1f77bcf86cd799439012",
      "type": "expense",
      "category": "food",
      "amount": 1500,
      "description": "Restaurant dinner",
      "date": "2024-11-15T19:30:00Z",
      "payment_method": "card"
    }
  ],
  "total": 150,
  "limit": 10,
  "offset": 0
}
```

#### GET /transactions/analytics
Get spending analytics.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `period` (string): daily/weekly/monthly/yearly

**Response:** `200 OK`
```json
{
  "period": "monthly",
  "total_income": 60000,
  "total_expenses": 45000,
  "savings": 15000,
  "savings_rate": 25,
  "category_breakdown": {
    "food": {
      "amount": 12000,
      "percentage": 26.7,
      "trend": "increasing"
    },
    "transport": {
      "amount": 5000,
      "percentage": 11.1,
      "trend": "stable"
    }
  },
  "anomalies": [
    {
      "transaction_id": "507f1f77bcf86cd799439013",
      "reason": "Unusually high amount",
      "suggestion": "Review this transaction"
    }
  ],
  "ai_insights": "Your food expenses are 45% above average..."
}
```

#### POST /transactions/parse-email
Parse transactions from email content.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "email_content": "Your account has been debited with Rs. 1,500..."
}
```

**Response:** `200 OK`
```json
{
  "transactions": [
    {
      "type": "expense",
      "amount": 1500,
      "date": "2024-11-15",
      "description": "Debit transaction",
      "confidence": 0.95
    }
  ]
}
```

### Goals

#### POST /goals/plan
Create AI-powered goal plan.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "name": "Europe Vacation",
  "target_amount": 200000,
  "current_amount": 10000,
  "target_date": "2025-06-30",
  "category": "travel"
}
```

**Response:** `200 OK`
```json
{
  "goal_details": {
    "name": "Europe Vacation",
    "target_amount": 200000,
    "months_to_goal": 8
  },
  "ai_recommendations": {
    "feasibility_score": 85,
    "risk_assessment": "moderate",
    "recommended_monthly_saving": 23750
  },
  "saving_strategies": {
    "easy": {
      "monthly_saving": 15000,
      "time_to_goal": 13,
      "lifestyle_impact": "minimal",
      "breakdown": {
        "reduce_dining": 6000,
        "reduce_shopping": 4500,
        "optimize_subscriptions": 4500
      }
    },
    "moderate": {
      "monthly_saving": 23750,
      "time_to_goal": 8,
      "lifestyle_impact": "moderate",
      "breakdown": {
        "from_available_savings": 15000,
        "reduce_expenses": 8750
      }
    },
    "aggressive": {
      "monthly_saving": 38000,
      "time_to_goal": 5,
      "lifestyle_impact": "significant",
      "additional_income_needed": 8000
    }
  }
}
```

#### POST /goals/create
Create a new goal with selected strategy.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "name": "Europe Vacation",
  "target_amount": 200000,
  "current_amount": 10000,
  "target_date": "2025-06-30",
  "category": "travel",
  "saving_strategy": "moderate",
  "monthly_contribution": 23750
}
```

**Response:** `201 Created`
```json
{
  "id": "507f1f77bcf86cd799439014",
  "message": "Goal created successfully"
}
```

#### GET /goals
Get all user goals.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `status` (string): active/completed/paused

**Response:** `200 OK`
```json
{
  "goals": [
    {
      "id": "507f1f77bcf86cd799439014",
      "name": "Europe Vacation",
      "target_amount": 200000,
      "current_amount": 50000,
      "progress_percentage": 25,
      "status": "active",
      "monthly_contribution": 23750,
      "target_date": "2025-06-30"
    }
  ]
}
```

#### GET /goals/{goal_id}/progress
Get detailed goal progress.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "goal": {
    "id": "507f1f77bcf86cd799439014",
    "name": "Europe Vacation",
    "target_amount": 200000,
    "current_amount": 50000
  },
  "progress": {
    "percentage": 25,
    "months_elapsed": 2,
    "months_remaining": 6,
    "on_track": true,
    "projected_completion": "2025-05-15"
  },
  "milestones": [
    {
      "date": "2024-10-01",
      "amount": 25000,
      "percentage": 12.5
    },
    {
      "date": "2024-11-01",
      "amount": 50000,
      "percentage": 25
    }
  ],
  "visualization": {
    "chart_data": [...]
  }
}
```

#### PUT /goals/{goal_id}/contribute
Add contribution to goal.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "amount": 25000
}
```

### Investments

#### POST /investments
Add new investment.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "type": "mutual_funds",
  "name": "Axis Bluechip Fund",
  "amount_invested": 100000,
  "purchase_date": "2024-01-15",
  "units": 2500,
  "nav": 40
}
```

#### GET /investments
Get all investments.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "investments": [
    {
      "id": "507f1f77bcf86cd799439015",
      "type": "mutual_funds",
      "name": "Axis Bluechip Fund",
      "amount_invested": 100000,
      "current_value": 115000,
      "returns_percentage": 15,
      "risk_level": "moderate"
    }
  ],
  "total_invested": 540000,
  "total_current_value": 621000,
  "overall_returns": 15
}
```

#### GET /investments/recommendations
Get AI investment recommendations.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "risk_profile": "moderate",
  "recommended_allocation": {
    "equity": 50,
    "debt": 30,
    "gold": 10,
    "liquid": 10
  },
  "specific_recommendations": [
    {
      "type": "mutual_funds",
      "name": "HDFC Mid-Cap Fund",
      "suggested_amount": 10000,
      "expected_returns": "12-15%",
      "risk": "moderate-high",
      "reasoning": "Diversification into mid-cap segment"
    }
  ],
  "rebalancing_needed": true,
  "rebalancing_suggestions": [...]
}
```

### Tax Planning

#### GET /tax/calculate
Calculate tax liability.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "annual_income": 1200000,
  "deductions": {
    "section_80c": 150000,
    "section_80d": 35000,
    "section_24": 0,
    "section_80e": 0,
    "section_80ccd": 50000
  },
  "regime": "new"
}
```

**Response:** `200 OK`
```json
{
  "gross_income": 1200000,
  "total_deductions": 285000,
  "taxable_income": 915000,
  "tax_liability": 142000,
  "tax_with_cess": 147680,
  "effective_rate": 12.3,
  "regime_comparison": {
    "old_regime_tax": 195000,
    "new_regime_tax": 147680,
    "savings_with_new": 47320
  }
}
```

#### GET /tax/suggestions
Get tax-saving suggestions.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "current_tax_liability": 147680,
  "suggestions_by_section": {
    "section_80c": {
      "current": 100000,
      "limit": 150000,
      "remaining": 50000,
      "suggestions": [
        {
          "instrument": "ELSS",
          "amount": 30000,
          "benefit": "Tax saving + High returns"
        }
      ]
    }
  },
  "potential_savings": 25000,
  "documents_required": [
    "Form 16",
    "Investment proofs",
    "Insurance receipts"
  ]
}
```

### Chat & AI Assistant

#### POST /chat/message
Send message to AI assistant.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "content": "How can I save more money?",
  "context": "general",
  "session_id": "optional-session-id"
}
```

**Response:** `200 OK`
```json
{
  "response": "Based on your spending patterns, here are my suggestions...",
  "session_id": "507f1f77bcf86cd799439016",
  "sources": [
    {
      "type": "document",
      "title": "Personal Finance Guide",
      "relevance": 0.92
    }
  ],
  "suggested_actions": [
    {
      "action": "create_goal",
      "description": "Create an emergency fund goal"
    }
  ]
}
```

#### GET /chat/history/{session_id}
Get chat history for a session.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "session_id": "507f1f77bcf86cd799439016",
  "messages": [
    {
      "role": "user",
      "content": "How can I save more money?",
      "timestamp": "2024-11-15T10:30:00Z"
    },
    {
      "role": "assistant",
      "content": "Based on your spending patterns...",
      "timestamp": "2024-11-15T10:30:05Z"
    }
  ]
}
```

### Documents

#### POST /documents/upload
Upload document for RAG processing.

**Headers:** 
- `Authorization: Bearer <token>`
- `Content-Type: multipart/form-data`

**Request Body:**
```
file: <binary file data>
document_type: "tax" | "investment" | "guide" | "general"
```

**Response:** `200 OK`
```json
{
  "document_id": "507f1f77bcf86cd799439017",
  "filename": "tax_guide.pdf",
  "chunks_created": 42,
  "processing_status": "completed"
}
```

#### GET /documents/search
Search through uploaded documents.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `query` (string): Search query
- `document_type` (string): Filter by type
- `limit` (int): Number of results

**Response:** `200 OK`
```json
{
  "results": [
    {
      "document_id": "507f1f77bcf86cd799439017",
      "content": "Tax deduction under Section 80C...",
      "relevance_score": 0.95,
      "metadata": {
        "filename": "tax_guide.pdf",
        "page": 5
      }
    }
  ]
}
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request data",
  "errors": [
    {
      "field": "email",
      "message": "Invalid email format"
    }
  ]
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid or expired token"
}
```

### 403 Forbidden
```json
{
  "detail": "You don't have permission to access this resource"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 429 Too Many Requests
```json
{
  "detail": "Rate limit exceeded",
  "retry_after": 60
}
```

### 500 Internal Server Error
```json
{
  "detail": "An internal error occurred",
  "error_id": "507f1f77bcf86cd799439018"
}
```

## Rate Limiting

- **Authentication endpoints**: 5 requests per minute
- **Transaction endpoints**: 30 requests per minute
- **Chat endpoints**: 10 requests per minute
- **Document upload**: 5 requests per hour

## Pagination

All list endpoints support pagination using:
- `limit`: Number of items per page (default: 10, max: 100)
- `offset`: Number of items to skip

## Filtering

Most list endpoints support filtering via query parameters:
- Date ranges: `start_date` and `end_date`
- Categories: `category` parameter
- Status: `status` parameter

## Webhooks

The API supports webhooks for real-time notifications:

### Available Events
- `transaction.created`
- `goal.completed`
- `goal.milestone_reached`
- `investment.matured`
- `anomaly.detected`

### Webhook Payload
```json
{
  "event": "goal.completed",
  "timestamp": "2024-11-15T10:30:00Z",
  "data": {
    "goal_id": "507f1f77bcf86cd799439014",
    "name": "Emergency Fund",
    "completed_at": "2024-11-15T10:30:00Z"
  }
}
```

## SDK Examples

### Python
```python
import requests

class FinanceAPIClient:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {token}"}
    
    def get_transactions(self, limit=10):
        response = requests.get(
            f"{self.base_url}/transactions",
            headers=self.headers,
            params={"limit": limit}
        )
        return response.json()

# Usage
client = FinanceAPIClient("http://localhost:8000/api/v1", "your-token")
transactions = client.get_transactions()
```

### JavaScript
```javascript
class FinanceAPIClient {
    constructor(baseUrl, token) {
        this.baseUrl = baseUrl;
        this.headers = {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        };
    }
    
    async getTransactions(limit = 10) {
        const response = await fetch(
            `${this.baseUrl}/transactions?limit=${limit}`,
            { headers: this.headers }
        );
        return response.json();
    }
}

// Usage
const client = new FinanceAPIClient('http://localhost:8000/api/v1', 'your-token');
const transactions = await client.getTransactions();
```

## Testing

### Using cURL
```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/token \
  -F "username=user@example.com" \
  -F "password=password123"

# Get transactions
curl -X GET http://localhost:8000/api/v1/transactions \
  -H "Authorization: Bearer <token>"

# Create transaction
curl -X POST http://localhost:8000/api/v1/transactions \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"type":"expense","amount":1500,"category":"food"}'
```

### Using Postman
Import the OpenAPI specification from `http://localhost:8000/openapi.json` to automatically generate a Postman collection.
