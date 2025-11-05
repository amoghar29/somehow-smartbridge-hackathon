# Personal Finance RAG Chatbot - Complete Implementation Guide

## 🚀 Project Overview

An intelligent personal finance management system powered by IBM Granite models, featuring RAG-based conversational AI, spending analysis, goal tracking, tax planning, and investment management.

## 📋 Table of Contents
- [System Architecture](#system-architecture)
- [Technology Stack](#technology-stack)
- [Prerequisites](#prerequisites)
- [Project Structure](#project-structure)
- [Installation Guide](#installation-guide)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Features Documentation](#features-documentation)
- [Deployment Guide](#deployment-guide)

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Frontend (Streamlit)                   │
│  ┌────────┐ ┌──────────┐ ┌─────────┐ ┌──────────────┐ │
│  │Dashboard│ │  Goals   │ │   Tax   │ │Learning Chat │ │
│  └────────┘ └──────────┘ └─────────┘ └──────────────┘ │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                   Backend (FastAPI)                      │
│  ┌─────────────┐ ┌──────────────┐ ┌────────────────┐   │
│  │ Auth & User │ │Finance Logic │ │  RAG Pipeline  │   │
│  │ Management  │ │   Services   │ │   (LangChain)  │   │
│  └─────────────┘ └──────────────┘ └────────────────┘   │
└─────────────────────────────────────────────────────────┘
                            │
                ┌───────────┴────────────┐
                ▼                        ▼
    ┌──────────────────┐      ┌───────────────────┐
    │     MongoDB      │      │   Vector Store    │
    │  Collections:    │      │   (Chroma/FAISS)  │
    │  - users         │      │                   │
    │  - transactions  │      │  Embeddings for:  │
    │  - goals         │      │  - Documents      │
    │  - chat_history  │      │  - Finance guides │
    │  - investments   │      │  - Tax laws       │
    └──────────────────┘      └───────────────────┘
                            │
                            ▼
                ┌───────────────────────┐
                │   IBM Granite Models  │
                │  (via HuggingFace)    │
                └───────────────────────┘
```

## 💻 Technology Stack

### Core Technologies
- **Backend Framework**: FastAPI (Python 3.10+)
- **Frontend Framework**: Streamlit
- **Database**: MongoDB (v6.0+)
- **Vector Store**: ChromaDB/FAISS
- **LLM Framework**: LangChain/LangGraph
- **LLM Models**: IBM Granite (via HuggingFace)
- **Data Visualization**: Plotly

### Key Dependencies
```python
# Backend
fastapi==0.104.1
uvicorn==0.24.0
pymongo==4.5.0
motor==3.3.2
pydantic==2.4.2
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0

# AI/ML
langchain==0.1.0
langgraph==0.0.20
chromadb==0.4.18
transformers==4.35.2
sentence-transformers==2.2.2
huggingface-hub==0.19.4

# Frontend
streamlit==1.29.0
plotly==5.18.0
pandas==2.1.3
```

## 📁 Project Structure

```
personal-finance-bot/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config/
│   │   │   ├── __init__.py
│   │   │   ├── settings.py
│   │   │   └── database.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── transaction.py
│   │   │   ├── goal.py
│   │   │   ├── investment.py
│   │   │   └── chat.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── user_schema.py
│   │   │   ├── transaction_schema.py
│   │   │   ├── goal_schema.py
│   │   │   └── chat_schema.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py
│   │   │   │   ├── users.py
│   │   │   │   ├── transactions.py
│   │   │   │   ├── goals.py
│   │   │   │   ├── investments.py
│   │   │   │   ├── chat.py
│   │   │   │   ├── documents.py
│   │   │   │   └── analytics.py
│   │   │   └── dependencies.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── finance_analyzer.py
│   │   │   ├── goal_planner.py
│   │   │   ├── tax_advisor.py
│   │   │   └── investment_tracker.py
│   │   ├── ai/
│   │   │   ├── __init__.py
│   │   │   ├── rag_pipeline.py
│   │   │   ├── embeddings.py
│   │   │   ├── vector_store.py
│   │   │   ├── prompts/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── finance_prompts.py
│   │   │   │   ├── goal_prompts.py
│   │   │   │   └── tax_prompts.py
│   │   │   └── chains.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── email_parser.py
│   │       └── helpers.py
│   ├── tests/
│   │   └── ...
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── app.py
│   ├── pages/
│   │   ├── 1_📊_Dashboard.py
│   │   ├── 2_🎯_Goals.py
│   │   ├── 3_💰_Tax_Planner.py
│   │   └── 4_📚_Learning_Bot.py
│   ├── components/
│   │   ├── __init__.py
│   │   ├── charts.py
│   │   ├── cards.py
│   │   └── forms.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── api_client.py
│   │   └── session_state.py
│   ├── config/
│   │   └── settings.py
│   └── requirements.txt
├── data/
│   ├── documents/
│   ├── embeddings/
│   └── uploads/
├── scripts/
│   ├── setup_db.py
│   ├── populate_vectors.py
│   └── migrate.py
├── docker-compose.yml
├── .gitignore
└── README.md
```

## 🔧 Prerequisites

### Required API Keys
```bash
# Create .env file in backend/ directory
HUGGINGFACE_API_KEY=your_hf_api_key_here
MONGODB_URI=mongodb://localhost:27017/finance_bot
JWT_SECRET_KEY=your_secret_key_here
JWT_ALGORITHM=HS256
REDIS_URL=redis://localhost:6379
```

### System Requirements
- Python 3.10+
- MongoDB 6.0+
- Redis (optional, for caching)
- 8GB+ RAM recommended
- 10GB+ storage for vector embeddings

## 📦 Installation Guide

### Step 1: Clone Repository
```bash
git clone https://github.com/yourrepo/personal-finance-bot.git
cd personal-finance-bot
```

### Step 2: Setup Python Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Step 4: Install Frontend Dependencies
```bash
cd ../frontend
pip install -r requirements.txt
```

### Step 5: Setup MongoDB
```bash
# Install MongoDB (Ubuntu/Debian)
sudo apt-get install mongodb

# Start MongoDB
sudo systemctl start mongodb

# Create database and collections
python ../scripts/setup_db.py
```

### Step 6: Initialize Vector Store
```bash
python ../scripts/populate_vectors.py
```

### Step 7: Run Backend Server
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### Step 8: Run Frontend Application
```bash
cd frontend
streamlit run app.py
```

## 🔑 Configuration Details

### IBM Granite Model Configuration
```python
# backend/app/config/settings.py
GRANITE_MODEL_NAME = "ibm-granite/granite-7b-base"
EMBEDDING_MODEL = "ibm-granite/granite-embedding-125m-english"
MAX_TOKENS = 2048
TEMPERATURE = 0.7
```

### MongoDB Schema Configuration
See `BACKEND_DOCUMENTATION.md` for detailed schema definitions.

## 📚 API Documentation

The API documentation is automatically generated and available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🎯 Features

### 1. Smart Dashboard
- Real-time spending analysis
- Investment portfolio overview
- Monthly/weekly comparisons
- Category-wise expense breakdown

### 2. Goal Tracker
- AI-powered savings recommendations
- Multiple saving strategies (Easy/Medium/Aggressive)
- Progress visualization
- Milestone notifications

### 3. Tax Planner
- Personalized tax-saving suggestions
- Section-wise deduction recommendations
- Tax liability estimation
- Document checklist

### 4. Learning Chatbot
- Context-aware financial guidance
- Document-based Q&A
- Personalized learning paths
- Investment education

## 🚀 Deployment

### Docker Deployment
```bash
docker-compose up -d
```

### Production Deployment (AWS/GCP)
See `DEPLOYMENT.md` for detailed production deployment instructions.

## 📖 Additional Documentation

- [Backend Development Guide](./BACKEND_DOCUMENTATION.md)
- [Frontend Development Guide](./FRONTEND_DOCUMENTATION.md)
- [API Reference](./API_REFERENCE.md)
- [Database Schemas](./DATABASE_SCHEMAS.md)

## 🤝 Contributing

Please read our contributing guidelines before submitting PRs.

## 📝 License

This project is licensed under the MIT License.

## 🆘 Support

For support, email support@financebot.com or open an issue in the repository.