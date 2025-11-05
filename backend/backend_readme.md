🧠 Backend Generation Specification

Project: Personal Finance Assistant
Frontend: Streamlit (provided)
Goal: Local AI-powered backend with modular finance logic and IBM Granite model integration.

⚙️ 1. General Architecture

The backend must be implemented using FastAPI.

It must expose RESTful endpoints compatible with the Streamlit frontend buttons and actions:

“Add Transaction”

“Analyze Spending”

“Get AI Advice”

The AI engine will use IBM Granite-3.3-2B Instruct from Hugging Face, loaded locally via Transformers pipeline.

All computations must run on CPU only (no GPU dependency).

The backend must be modular: configuration, agents, routes, models, and utilities must live in separate directories.

Responses must be in structured JSON format, suitable for Streamlit visualization (e.g., metrics, charts, text).

CORS middleware must allow all origins to enable local integration with Streamlit running at port 8501.

📁 2. Directory Layout
personal_finance_backend/
│
├── main.py                   → FastAPI entry point
├── config/                   → Application configuration
│   └── settings.py
│
├── core/                     → Shared backend logic
│   ├── granite_api.py        → Granite model loader + inference handler
│   ├── utils.py              → Helper math, formatting, validators
│   └── logger.py             → Logging configuration
│
├── models/                   → Request/response data schemas
│   ├── request_models.py
│   └── response_models.py
│
├── agents/                   → Modular AI logic
│   ├── budget_agent.py
│   ├── goal_agent.py
│   ├── tax_agent.py
│   └── intent_router.py
│
├── routes/                   → API routes
│   ├── base_routes.py
│   └── finance_routes.py
│
├── data/                     → Local mock user data (optional)
│   └── sample_transactions.json
│
└── requirements.txt

🔧 3. Component Responsibilities
3.1 main.py

Initializes FastAPI application.

Registers middleware for CORS.

Includes all routers from routes/finance_routes.py and routes/base_routes.py.

Defines a root health check endpoint (GET /) that returns service status.

Should run locally via:

uvicorn main:app --reload --port 8000

3.2 config/settings.py

Defines project constants like:

MODEL_ID → "ibm-granite/granite-3.3-2b-instruct"

DEVICE → "cpu"

Base paths (BASE_DIR, CACHE_DIR)

Stores metadata: name, description, version.

Optionally include environment variables via dotenv.

3.3 core/logger.py

Configures Python’s logging module to log both to console and a logs/app.log file.

Log levels: INFO, WARNING, ERROR.

Used globally by all components.

3.4 core/granite_api.py

Loads Granite-3.3-2B model and tokenizer using Hugging Face Transformers.

Creates a text-generation pipeline stored in a singleton-like instance for reuse.

Provides a single public function generate(prompt: str, max_new_tokens: int = 300, temperature: float = 0.7) returning the generated text.

Must automatically download and cache the model in /model_cache if not present.

Should gracefully handle model load errors and generation failures with meaningful log messages.

3.5 core/utils.py

Contains helper utilities, such as:

calc_savings_rate(income, expenses) → computes savings percentage.

get_top_expenses(expenses_dict, n=3) → returns top categories by amount.

format_currency(value) → returns string like "₹60,000".

Must ensure no circular imports and be reusable by all agents.

📦 4. Data Models
4.1 models/request_models.py

Defines Pydantic classes for validating input JSON payloads.

Class	Fields	Description
ChatRequest	question: str, persona: str	For general AI Q&A
BudgetRequest	income: float, expenses: dict[str, float], persona: str	For budget analysis
GoalRequest	goal_name: str, target_amount: float, months: int, income: float, persona: str	For goal planning
TransactionRequest	description: str, amount: float, category: str, type: str	For adding new transactions
4.2 models/response_models.py

Defines JSON response structures.

Class	Fields	Description
BudgetResponse	summary: dict, insights: list[str]	Budget summaries
GoalResponse	plan: dict, advice: str	Goal planning results
ChatResponse	response: str	General AI response
AnalyticsResponse	trend_data: list[dict], totals: dict	For dashboard analytics
🧩 5. Agents (AI Logic Modules)

Each agent file contains one main function that accepts structured data, builds a tailored prompt, calls the Granite model through core/granite_api.generate(), and returns structured results.

5.1 budget_agent.py

Inputs: income, expenses, persona.

Process:

Calculate total expenses and savings rate.

Determine top 3 expense categories.

Create a contextual prompt describing the user’s situation.

Call Granite’s generate() to produce short insights.

Output:

A dict containing:

summary → income, total_expenses, savings_rate, top_expenses

insights → list of advice lines

5.2 goal_agent.py

Inputs: goal_name, target_amount, months, income, persona.

Calculates required monthly saving.

Builds a motivational prompt and gets an actionable plan.

Output dict includes:

plan → goal details + required monthly saving

advice → model’s textual output

5.3 tax_agent.py

Inputs: income, persona

Generates general, educational tax-saving advice.

Outputs one string under key "tax_advice".

5.4 intent_router.py

Determines which agent to call based on the query or endpoint.

Simple keyword mapping:

Contains “goal” → goal_agent

Contains “tax” → tax_agent

Contains “spend” / “budget” → budget_agent

Returns fallback message for unrecognized intents.

🌐 6. Routes (API Endpoints)
6.1 routes/base_routes.py

GET / → Health check endpoint returning { "status": "Backend running" }.

6.2 routes/finance_routes.py

Defines all REST endpoints required by the frontend.

Endpoint	Method	Input Model	Functionality
/ai/generate	POST	ChatRequest	General AI response using Granite
/ai/budget-summary	POST	BudgetRequest	Analyzes spending and gives advice
/ai/goal-planner	POST	GoalRequest	Creates savings plan for target goal
/analytics/summary	GET	None	Returns summary for dashboard metrics
/transactions/add	POST	TransactionRequest	Simulates transaction creation
/transactions/recent	GET	None	Returns recent mock transactions

Each endpoint:

Parses and validates incoming JSON with Pydantic models.

Calls the appropriate agent or function.

Returns a JSON response ready to be rendered by Streamlit (with metrics, lists, or text).

🧮 7. Integration Rules with Frontend

Frontend API client (in utils/api_client.py) must call these endpoints using requests with BACKEND_URL defined as http://127.0.0.1:8000.

Expected response format for AI endpoints:

{
  "response": "AI generated advice text..."
}


Budget summary endpoint must return keys matching dashboard labels:

"income", "expenses", "savings", "savings_rate".

All endpoints must return HTTP 200 on success and include error details in JSON for 400/500 failures.

No authentication required — the frontend handles simulated login.

The /ai/generate endpoint powers the “💡 Get AI Advice” button.
The /ai/budget-summary endpoint supports “📊 Analyze Spending.”

🧠 8. Business Logic & Data Flow

Frontend sends JSON → backend route.

FastAPI validates payload → calls relevant agent.

Agent formats prompt and invokes Granite model.

Granite generates human-readable insights.

Agent structures response → returns to route.

Route sends JSON back to frontend.

Streamlit updates dashboard metrics or displays AI text.

🧩 9. Non-Functional Requirements
Attribute	Description
Performance	Model inference must stay below ~3 s on CPU.
Portability	Must run on Windows 10+ without CUDA.
Maintainability	Each agent independent; adding new one shouldn’t break others.
Security	Local only, no user data persisted externally.
Logging	Every model call logged to logs/app.log.
Error Handling	All exceptions return JSON { "error": "message" }.
🧱 10. Development Setup Guide

Create and activate a Python 3.10+ virtual environment.

Install dependencies listed in requirements.txt:

fastapi, uvicorn, transformers, torch (CPU build), python-dotenv.

Run backend:

uvicorn main:app --reload


Run frontend:

streamlit run app.py


Access UI at http://localhost:8501, backend at http://127.0.0.1:8000/docs.

🧩 11. Future Extensions
Extension	Description
LangChain Integration	Add multi-step reasoning (summarize → advise → plan).
SQLite Storage	Persist transactions and goals.
User Profiles	Separate student/professional insights.
Visualization API	Return pre-aggregated data for charts.
Deployment	Package into Docker for IBM Cloud or Render.
✅ 12. Output Requirements for AI Generation

When a code-generation AI reads this document, it must:

Create all files and directories listed in Section 2.

Implement each module’s functionality exactly as described in Sections 3–6.

Ensure function names and class names match those specified.

Make sure all endpoints, models, and responses comply with schema definitions.

Integrate cleanly with Streamlit frontend without further modification.

💡 Summary

This backend architecture enables the Personal Finance Assistant to:

Deliver AI-driven financial insights via local Granite 3.3 2B model.

Support budget analysis, goal planning, and tax suggestions.

Provide a clean API layer for the Streamlit dashboard.

Run completely offline and CPU-friendly on Windows laptops.