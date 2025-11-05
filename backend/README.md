# Personal Finance Assistant Backend

AI-powered personal finance backend using FastAPI and IBM Granite 3.0 2B model.

## Features

- **Budget Analysis**: Analyze spending patterns and get AI-powered insights
- **Goal Planning**: Create savings plans for financial goals
- **Tax Advisory**: Get tax-saving advice (Indian tax context)
- **Transaction Management**: Track income and expenses
- **Analytics Dashboard**: View financial trends and summaries

## Architecture

```
backend/
├── main.py                 # FastAPI application entry point
├── config/                 # Configuration settings
│   └── settings.py
├── core/                   # Core functionality
│   ├── granite_api.py     # IBM Granite model integration
│   ├── utils.py           # Helper functions
│   └── logger.py          # Logging configuration
├── models/                 # Pydantic models
│   ├── request_models.py
│   └── response_models.py
├── agents/                 # AI agents
│   ├── budget_agent.py
│   ├── goal_agent.py
│   ├── tax_agent.py
│   └── intent_router.py
├── routes/                 # API routes
│   ├── base_routes.py
│   └── finance_routes.py
├── data/                   # Sample data
│   └── sample_transactions.json
└── logs/                   # Application logs
```

## Setup Instructions

### Prerequisites

- Python 3.10 or higher
- 8GB+ RAM (for model loading)
- Windows/Linux/macOS

### Installation

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   ```

2. **Activate virtual environment:**
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create .env file:**
   ```bash
   copy .env.example .env  # Windows
   # or
   cp .env.example .env    # Linux/Mac
   ```

### Running the Backend

```bash
# Method 1: Using Python directly
python main.py

# Method 2: Using uvicorn
uvicorn main:app --reload --port 8000
```

The API will be available at:
- **API Base URL**: http://127.0.0.1:8000
- **Interactive Docs**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

### First Run

On the first run, the IBM Granite model will be downloaded automatically (approximately 2-3 GB). This may take several minutes depending on your internet connection. The model is cached in the `model_cache/` directory for subsequent runs.

## API Endpoints

### Health Check
- `GET /` - Basic health check
- `GET /health` - Detailed health check with model status

### AI Endpoints
- `POST /ai/generate` - General AI chat
- `POST /ai/budget-summary` - Budget analysis
- `POST /ai/goal-planner` - Goal planning
- `POST /ai/tax-advice` - Tax advisory

### Analytics
- `GET /analytics/summary` - Dashboard analytics

### Transactions
- `POST /transactions/add` - Add transaction
- `GET /transactions/recent` - Get recent transactions

## Example API Usage

### Budget Analysis

```bash
curl -X POST "http://127.0.0.1:8000/ai/budget-summary" \
  -H "Content-Type: application/json" \
  -d '{
    "income": 60000,
    "expenses": {
      "Housing": 15000,
      "Food": 10000,
      "Transportation": 5000,
      "Entertainment": 3000
    },
    "persona": "professional"
  }'
```

### Goal Planning

```bash
curl -X POST "http://127.0.0.1:8000/ai/goal-planner" \
  -H "Content-Type: application/json" \
  -d '{
    "goal_name": "Emergency Fund",
    "target_amount": 100000,
    "months": 12,
    "income": 60000,
    "persona": "professional",
    "current_savings": 10000
  }'
```

### Add Transaction

```bash
curl -X POST "http://127.0.0.1:8000/transactions/add" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Grocery Shopping",
    "amount": 2500,
    "category": "Food",
    "type": "expense"
  }'
```

## Configuration

Edit `config/settings.py` to customize:
- Model ID and configuration
- API host and port
- CORS settings
- Directory paths

## Logging

Application logs are stored in `logs/app.log` with the following levels:
- INFO: General information and request logs
- WARNING: Warning messages
- ERROR: Error messages with stack traces

## Performance Notes

- First request will take longer as the model loads
- Subsequent requests are much faster (1-3 seconds)
- Model runs on CPU only (no GPU required)
- Recommended minimum: 8GB RAM

## Troubleshooting

### Model Loading Issues

If the model fails to load:
1. Check internet connection
2. Ensure sufficient disk space (5GB+)
3. Delete `model_cache/` and retry
4. Check logs in `logs/app.log`

### Port Already in Use

If port 8000 is already in use:
```bash
# Windows
netstat -ano | findstr :8000

# Linux/Mac
lsof -i :8000
```

Change the port in `config/settings.py` or pass it as a parameter:
```bash
uvicorn main:app --port 8001
```

### Memory Issues

If you encounter memory errors:
- Close other applications
- Reduce `MAX_NEW_TOKENS` in `config/settings.py`
- Consider using a smaller model

## Integration with Frontend

The backend is designed to work with the Streamlit frontend. Ensure:
1. Backend is running on port 8000
2. Frontend API client points to http://127.0.0.1:8000
3. CORS is configured to allow frontend origin

## Development

### Adding New Endpoints

1. Create request/response models in `models/`
2. Add business logic in `agents/`
3. Create route handler in `routes/finance_routes.py`
4. Register router in `main.py`

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests (when available)
pytest tests/
```

## License

This project is for educational and demonstration purposes.

## Support

For issues and questions:
- Check logs in `logs/app.log`
- Review API documentation at `/docs`
- Open an issue in the GitHub repository
