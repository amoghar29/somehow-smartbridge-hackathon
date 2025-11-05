# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Personal Finance Assistant - A Smartbridge hackathon project. This is an AI-powered financial management application built with Streamlit for the frontend and Python backend.

**Repository Structure:**
- `/frontend` - Streamlit-based web application
- Root `main.py` - Backend entry point (Python)

## Frontend Architecture

The frontend is built with **Streamlit**, a Python framework for building data applications.

### Directory Structure

```
frontend/
├── app.py                      # Main application entry point
├── config/
│   └── settings.py             # Configuration and constants
├── utils/
│   ├── api_client.py          # Backend API communication
│   └── session_state.py       # Session state management
├── components/
│   ├── charts.py              # Plotly chart components
│   └── cards.py               # Custom UI card components
└── pages/                      # Streamlit multi-page app
    ├── 1_📊_Dashboard.py      # Financial overview dashboard
    ├── 2_🎯_Goals.py          # Goal planning with AI
    ├── 3_💰_Tax_Planner.py   # Tax calculation and planning
    └── 4_🤖_AI_Assistant.py  # AI chatbot and learning center
```

### Key Features

1. **Dashboard** - Financial overview with spending trends, recent transactions, and goal progress
2. **Goals Planning** - AI-powered goal recommendations (Easy/Moderate/Aggressive plans)
3. **Tax Planner** - Calculate taxes with deductions (80C, 80D, etc.) and get AI suggestions
4. **AI Assistant** - Chat interface for financial advice, learning center, and FAQs

### Technology Stack

- **Streamlit** - Web framework
- **Plotly** - Interactive charts and visualizations
- **Pandas** - Data manipulation
- **Requests** - HTTP client for backend API calls

## Development Commands

### Setup

```bash
# Install dependencies
pip install -r requirements.txt
```

### Running the Application

```bash
# From frontend directory
streamlit run app.py

# With custom port
streamlit run app.py --server.port 8501

# With hot reload enabled
streamlit run app.py --server.runOnSave true
```

### Backend Setup

```bash
# From repository root
python main.py
```

## Configuration

**Backend URL**: Set via `config/settings.py` or environment variable:
```bash
export BACKEND_URL="http://localhost:8000"
```

**Default settings** are in `config/settings.py`:
- Backend URL
- Currency options (INR, USD, EUR)
- Transaction categories
- Goal categories
- Chart color schemes

## Session State Management

Streamlit's session state is managed through `utils/session_state.py`:
- User authentication status
- Financial data (net worth, savings rate, etc.)
- Recent transactions
- Active goals
- Chat history

## API Integration

The `utils/api_client.py` handles all backend communication:
- Authentication (login/signup)
- Transactions (get/create)
- Analytics
- Goal planning
- AI chat messages

API endpoints expected:
- `POST /api/v1/auth/token` - Login
- `POST /api/v1/auth/register` - Signup
- `GET /api/v1/transactions` - Get transactions
- `POST /api/v1/transactions` - Create transaction
- `GET /api/v1/transactions/analytics` - Get analytics
- `POST /api/v1/goals/plan` - Create goal plan
- `POST /api/v1/chat/message` - Send chat message

## Streamlit Multi-Page Apps

Streamlit automatically discovers pages in the `pages/` directory. Files are displayed in alphabetical order, so prefix with numbers and emojis for proper ordering.

**Page naming convention**: `{number}_{emoji}_{PageName}.py`

## Custom Styling

Custom CSS is applied in `app.py` for:
- Gradient button styling
- Custom metric cards
- Tab styling
- Alert boxes (success/warning)
- Responsive layout

## Current State

The frontend is fully implemented with simulated data for demo purposes. To connect with a real backend:
1. Implement the backend API endpoints listed above
2. Update `BACKEND_URL` in `config/settings.py`
3. Remove simulated data and replace with actual API calls

## Hackathon Notes

This is a demo/prototype application. Current limitations:
- Authentication is simulated (no real validation)
- Data is hardcoded for demonstration
- AI responses are pre-scripted (not connected to LLM)
- No database persistence

For production deployment, implement:
- Real authentication with JWT tokens
- Backend API integration
- Actual AI/LLM integration for chat
- Data persistence
- Error handling and validation
- Security measures (input sanitization, rate limiting)