# Integration Guide - Frontend & Backend

## Overview

The Personal Finance Assistant is now **fully integrated** with a dynamic connection between the Streamlit frontend and FastAPI backend powered by IBM Granite AI.

## What Has Been Integrated

### ✅ Backend (FastAPI)
- **AI Model**: IBM Granite 3.0 2B for intelligent financial advice
- **API Endpoints**: RESTful APIs for all features
- **Data Management**: Transaction storage and analytics
- **Health Checks**: Real-time server status monitoring

### ✅ Frontend (Streamlit)
- **Dynamic Dashboard**: Real-time data from backend analytics API
- **Budget Analyzer**: AI-powered budget insights
- **Goal Planner**: AI-generated personalized savings plans
- **Tax Planner**: Intelligent tax-saving recommendations
- **AI Chat**: Real-time conversational financial advisor
- **Transaction Management**: Add and view transactions dynamically

### ✅ Integration Points

1. **Health Check Integration** (`app.py:216`)
   - Frontend checks backend availability before loading
   - Displays error if backend is down
   - Shows connection status

2. **Analytics Integration** (`app.py:226`)
   - Fetches real-time financial metrics
   - Displays income, expenses, savings, and savings rate
   - Shows trend data with visualizations

3. **Transaction Management** (`app.py:294`)
   - Fetches recent transactions from backend
   - Adds new transactions via API
   - Real-time updates after adding transactions

4. **AI Chat Integration** (`app.py:352`, `pages/3_🤖_AI_Chat.py`)
   - Real-time AI responses from Granite model
   - Context-aware conversations
   - Persona-based advice

5. **Budget Analysis** (`pages/2_💰_Budget.py`)
   - Sends budget data to AI backend
   - Receives personalized insights
   - Visual expense breakdown

6. **Goal Planning** (`pages/1_🎯_Goals.py`)
   - AI-powered savings plan generation
   - Monthly savings calculations
   - Progress visualizations

7. **Tax Advisory** (`pages/4_💳_Tax_Planner.py`)
   - AI tax-saving recommendations
   - Deduction optimization
   - Tax calculation with real-time advice

## Architecture Flow

```
User Browser
    ↓
Streamlit Frontend (Port 8501)
    ↓
API Client (utils/api_client.py)
    ↓ HTTP/REST
FastAPI Backend (Port 8000)
    ↓
AI Agents (budget, goal, tax)
    ↓
IBM Granite 3.0 2B Model
```

## How to Run

### Method 1: One-Click Startup (Recommended)

**Windows:**
```cmd
start-all.bat
```

**Linux/Mac:**
```bash
./start-all.sh
```

This will:
1. Start the backend server on port 8000
2. Wait 5 seconds for initialization
3. Start the frontend server on port 8501
4. Open both in separate terminal windows

### Method 2: Manual Startup

**Terminal 1 - Backend:**
```bash
cd backend
python main.py
```
Wait for: `Starting Personal Finance Assistant Backend v1.0.0`

**Terminal 2 - Frontend:**
```bash
cd frontend
streamlit run app.py
```
Wait for: `You can now view your Streamlit app in your browser`

### Method 3: Development Mode

**Backend with Auto-reload:**
```bash
cd backend
uvicorn main:app --reload --port 8000
```

**Frontend with Auto-reload:**
```bash
cd frontend
streamlit run app.py --server.runOnSave true
```

## Testing the Integration

### 1. Health Check Test
- Open http://localhost:8501
- You should see: ✅ Connected to backend server
- If you see an error, backend isn't running

### 2. Dashboard Test
- Login (any email/password for demo)
- Dashboard should show:
  - Real metrics from backend
  - Spending trend chart
  - Recent transactions list
- Add a transaction and verify it appears

### 3. AI Chat Test
- Go to "🤖 AI Chat" page
- Ask: "How can I save more money?"
- Wait 10-30 seconds for first response (model loading)
- Subsequent responses should be faster (1-3 seconds)

### 4. Budget Analysis Test
- Go to "💰 Budget" page
- Enter income and expenses
- Click "Get AI Budget Analysis"
- Should receive personalized insights

### 5. Goal Planning Test
- Go to "🎯 Goals" page
- Create a goal with target amount
- Click "Get AI-Powered Plan"
- Should see savings plan and projections

### 6. Tax Advisory Test
- Go to "💳 Tax Planner" page
- Enter annual income
- Click "Get AI Tax-Saving Advice"
- Should receive tax optimization tips

## API Endpoints

### Health & Status
```bash
curl http://localhost:8000/
curl http://localhost:8000/health
```

### Analytics
```bash
curl http://localhost:8000/analytics/summary
```

### Transactions
```bash
# Add transaction
curl -X POST http://localhost:8000/transactions/add \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Test Transaction",
    "amount": 1000,
    "category": "Food",
    "type": "expense"
  }'

# Get transactions
curl http://localhost:8000/transactions/recent
```

### AI Features
```bash
# AI Chat
curl -X POST http://localhost:8000/ai/generate \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How to save money?",
    "persona": "professional"
  }'

# Budget Analysis
curl -X POST http://localhost:8000/ai/budget-summary \
  -H "Content-Type: application/json" \
  -d '{
    "income": 60000,
    "expenses": {"Housing": 15000, "Food": 10000},
    "persona": "professional"
  }'

# Goal Planning
curl -X POST http://localhost:8000/ai/goal-planner \
  -H "Content-Type: application/json" \
  -d '{
    "goal_name": "Emergency Fund",
    "target_amount": 100000,
    "months": 12,
    "income": 60000,
    "persona": "professional"
  }'

# Tax Advice
curl -X POST http://localhost:8000/ai/tax-advice \
  -H "Content-Type: application/json" \
  -d '{
    "income": 1200000,
    "persona": "professional"
  }'
```

## Configuration

### Backend Configuration
File: `backend/config/settings.py`

```python
# Server settings
API_HOST = "127.0.0.1"
API_PORT = 8000

# CORS settings (allows frontend to connect)
CORS_ORIGINS = [
    "http://localhost:8501",
    "http://127.0.0.1:8501",
]

# AI Model settings
MODEL_ID = "ibm-granite/granite-3.0-2b-instruct"
MAX_NEW_TOKENS = 300
TEMPERATURE = 0.7
```

### Frontend Configuration
File: `frontend/config/settings.py`

```python
# Backend API URL
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
```

## Troubleshooting

### Frontend shows "Backend not running"
**Solution:**
1. Check if backend is running: `curl http://localhost:8000/`
2. Start backend: `cd backend && python main.py`
3. Check backend logs: `backend/logs/app.log`

### AI responses are slow
**Cause:** First request loads the model into memory
**Solution:**
- Wait 10-30 seconds for first request
- Subsequent requests will be much faster (1-3 seconds)
- Ensure 8GB+ RAM available

### Model download fails
**Solution:**
1. Check internet connection
2. Ensure 5GB+ disk space
3. Delete `backend/model_cache/` and retry
4. Check logs for specific errors

### Port conflicts
**Backend port 8000 in use:**
```python
# Edit backend/config/settings.py
API_PORT = 8001
```

**Frontend port 8501 in use:**
```bash
streamlit run app.py --server.port 8502
```

### Import errors
**Backend:**
```bash
cd backend
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
pip install -r requirements.txt
```

## Data Flow Examples

### Adding a Transaction
```
User enters transaction in frontend
    ↓
Frontend: create_transaction() API call
    ↓
Backend: POST /transactions/add
    ↓
Saves to backend/data/sample_transactions.json
    ↓
Returns success with transaction_id
    ↓
Frontend: Shows success message
    ↓
Frontend: Refreshes to show new transaction
```

### Getting AI Advice
```
User asks question in chat
    ↓
Frontend: get_ai_advice() API call
    ↓
Backend: POST /ai/generate
    ↓
Intent router analyzes question
    ↓
Routes to appropriate agent
    ↓
Granite AI model generates response
    ↓
Returns AI response
    ↓
Frontend: Displays in chat
```

## Features Summary

| Feature | Frontend | Backend | Status |
|---------|----------|---------|--------|
| Dashboard | ✅ | ✅ | Integrated |
| Transactions | ✅ | ✅ | Integrated |
| Analytics | ✅ | ✅ | Integrated |
| Budget Analysis | ✅ | ✅ | Integrated |
| Goal Planning | ✅ | ✅ | Integrated |
| Tax Advisory | ✅ | ✅ | Integrated |
| AI Chat | ✅ | ✅ | Integrated |
| Authentication | ✅ | ⚠️ | Demo Only |
| Database | ❌ | ❌ | File-based |

## Next Steps

### For Development
1. Add user authentication
2. Integrate database (PostgreSQL)
3. Add data persistence
4. Implement caching
5. Add unit tests

### For Production
1. Setup environment variables
2. Configure production CORS
3. Add SSL/HTTPS
4. Setup monitoring
5. Add logging aggregation
6. Containerize with Docker

## Performance Metrics

- **Backend startup**: ~5 seconds
- **Model loading**: ~10-30 seconds (first request)
- **API response**: ~50-200ms (after model loaded)
- **AI inference**: ~1-3 seconds
- **Frontend load**: ~2-3 seconds

## Security Notes

- Authentication is currently demo-only (no real validation)
- No user data encryption
- Local file-based storage (not production-ready)
- CORS configured for localhost only

For production deployment, implement proper:
- Authentication (JWT, OAuth)
- Authorization
- Data encryption
- Secure storage
- Rate limiting
- Input validation

## Support

- **Backend logs**: `backend/logs/app.log`
- **API docs**: http://localhost:8000/docs
- **GitHub issues**: Open an issue on the repository

---

**Integration completed successfully! The frontend and backend are now fully connected and working dynamically.** 🚀
