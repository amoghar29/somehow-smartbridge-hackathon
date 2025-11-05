# Personal Finance Assistant - AI-Powered Finance Management

A full-stack AI-powered personal finance application built for the Smartbridge Hackathon. Features include budget analysis, goal planning, tax advisory, and real-time AI chat powered by IBM Granite 3.0 2B model.

## Features

### Backend (FastAPI)
- **IBM Granite 3.0 2B AI Model** - Local AI inference for privacy
- **Budget Analysis** - AI-powered spending insights
- **Goal Planning** - Personalized savings strategies
- **Tax Advisory** - Indian tax law guidance
- **Transaction Management** - Track income and expenses
- **RESTful API** - Well-documented endpoints

### Frontend (Streamlit)
- **Interactive Dashboard** - Real-time financial overview
- **Budget Analyzer** - Visual expense breakdown
- **Goal Planner** - AI-generated savings plans with projections
- **Tax Calculator** - Comprehensive tax planning tool
- **AI Chat Assistant** - Conversational financial advice
- **Beautiful UI** - Modern, responsive design

## Architecture

```
├── backend/               # FastAPI backend
│   ├── main.py           # Application entry point
│   ├── agents/           # AI agents (budget, goal, tax)
│   ├── routes/           # API endpoints
│   ├── models/           # Request/response models
│   ├── core/             # Granite AI integration
│   └── config/           # Settings
│
├── frontend/             # Streamlit frontend
│   ├── app.py           # Main application
│   ├── pages/           # Multi-page app
│   │   ├── 1_🎯_Goals.py
│   │   ├── 2_💰_Budget.py
│   │   ├── 3_🤖_AI_Chat.py
│   │   └── 4_💳_Tax_Planner.py
│   ├── utils/           # API client & utilities
│   └── config/          # Frontend settings
│
├── start-all.bat        # Windows startup script
└── start-all.sh         # Linux/Mac startup script
```

## Quick Start

### Prerequisites

- Python 3.10 or higher
- 8GB+ RAM (for AI model)
- Windows/Linux/macOS

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/amoghar29/somehow-smartbridge-hackathon.git
   cd somehow-smartbridge-hackathon
   ```

2. **Setup Backend:**
   ```bash
   cd backend
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # Linux/Mac
   source venv/bin/activate

   pip install -r requirements.txt
   cd ..
   ```

3. **Setup Frontend:**
   ```bash
   cd frontend
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # Linux/Mac
   source venv/bin/activate

   pip install -r requirements.txt
   cd ..
   ```

### Running the Application

#### Option 1: Use Startup Scripts (Recommended)

**Windows:**
```bash
start-all.bat
```

**Linux/Mac:**
```bash
chmod +x start-all.sh
./start-all.sh
```

#### Option 2: Manual Start

**Terminal 1 - Backend:**
```bash
cd backend
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
streamlit run app.py
```

### Access the Application

- **Frontend UI:** http://localhost:8501
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Usage Guide

### 1. Dashboard
- View financial overview with real-time metrics
- See spending trends and recent transactions
- Add new transactions
- Quick access to AI advice

### 2. Budget Analysis
- Input monthly income and expenses by category
- Get AI-powered budget insights
- Visualize expense distribution
- Receive personalized recommendations

### 3. Goal Planning
- Set financial goals with target amounts
- Get AI-generated savings plans
- View progress visualization
- See projected savings timeline

### 4. Tax Planning
- Calculate income tax with deductions
- Get AI tax-saving advice
- Learn about tax-saving instruments
- View tax planning calendar

### 5. AI Chat Assistant
- Ask any personal finance questions
- Get contextual AI responses
- View example questions
- Export chat history

## API Endpoints

### Health & Status
- `GET /` - Health check
- `GET /health` - Detailed status with model info

### AI-Powered Features
- `POST /ai/generate` - General AI chat
- `POST /ai/budget-summary` - Budget analysis
- `POST /ai/goal-planner` - Goal planning
- `POST /ai/tax-advice` - Tax advisory

### Transactions & Analytics
- `POST /transactions/add` - Add transaction
- `GET /transactions/recent` - Get recent transactions
- `GET /analytics/summary` - Dashboard analytics

## Configuration

### Backend Configuration
Edit `backend/config/settings.py`:
```python
API_HOST = "127.0.0.1"
API_PORT = 8000
MODEL_ID = "ibm-granite/granite-3.0-2b-instruct"
```

### Frontend Configuration
Edit `frontend/config/settings.py`:
```python
BACKEND_URL = "http://localhost:8000"
```

## First Run Notes

- **Model Download:** On first run, the IBM Granite model (~2-3 GB) will be downloaded automatically. This may take several minutes.
- **Model Loading:** First AI request will take 10-30 seconds as the model loads into memory.
- **Subsequent Requests:** Will be much faster (1-3 seconds).

## Development

### Backend Development
```bash
cd backend
uvicorn main:app --reload --port 8000
```

### Frontend Development
```bash
cd frontend
streamlit run app.py --server.runOnSave true
```

## Troubleshooting

### Backend Not Starting
- Check if port 8000 is available
- Ensure Python 3.10+ is installed
- Check logs in `backend/logs/app.log`

### Frontend Connection Error
- Ensure backend is running at http://localhost:8000
- Check BACKEND_URL in `frontend/config/settings.py`
- Verify CORS settings in backend

### AI Model Issues
- Ensure sufficient disk space (5GB+)
- Check internet connection for initial download
- Verify RAM availability (8GB+ recommended)
- Delete `backend/model_cache/` and retry

### Memory Issues
- Close other applications
- Reduce MAX_NEW_TOKENS in backend settings
- Consider using a smaller model

## Tech Stack

### Backend
- **FastAPI** - Modern web framework
- **IBM Granite 3.0 2B** - AI model
- **Transformers** - Model inference
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server

### Frontend
- **Streamlit** - Web framework
- **Plotly** - Interactive visualizations
- **Pandas** - Data manipulation
- **Requests** - HTTP client

## Project Structure Features

- ✅ Fully integrated backend and frontend
- ✅ Real-time AI responses
- ✅ Dynamic data from backend
- ✅ Transaction management
- ✅ Analytics and visualizations
- ✅ Multi-page Streamlit app
- ✅ RESTful API design
- ✅ Error handling
- ✅ Health checks
- ✅ Logging system

## Future Enhancements

- [ ] User authentication and authorization
- [ ] Database integration (PostgreSQL)
- [ ] Multi-user support
- [ ] Data persistence
- [ ] Email notifications
- [ ] Export reports (PDF)
- [ ] Mobile app
- [ ] Real-time stock prices
- [ ] Investment tracking
- [ ] Bill reminders

## Contributing

This is a hackathon project. Contributions are welcome!

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is for educational and demonstration purposes.

## Team

Smartbridge Hackathon Team

## Acknowledgments

- IBM Granite AI Model
- Hugging Face Transformers
- Streamlit Community
- FastAPI Community

## Support

For issues and questions:
- Check logs in `backend/logs/app.log`
- Review API documentation at `/docs`
- Open an issue on GitHub

---

**Made with ❤️ for Smartbridge Hackathon**
